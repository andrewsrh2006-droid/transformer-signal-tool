"""FRED data loader: fetch, cache, and verify each series.

Design choices:
- Use the plain CSV endpoint `fredgraph.csv?id=ID`. In this environment it returns
  clean, uncompressed CSV, so no special decoding is needed.
- An invalid ID returns an HTML error page instead of CSV; we detect that and fail
  loudly rather than silently ingesting garbage.
- Raw CSVs are cached under data/raw/ so runs are reproducible; re-fetch only when
  the cache is missing (or force=True).
- Metadata (units, frequency, date range, fetch date, spot-checks) is written next
  to each series so the provenance is auditable.
"""

import io
import os
import subprocess
import time
from datetime import date

import numpy as np
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={id}"
SERIES_PAGE = "https://fred.stlouisfed.org/series/{id}"


def _http_get(url: str, timeout: int = 60) -> bytes:
    """Fetch a URL via curl.

    The macOS python.org interpreter here lacks a usable CA bundle, so urllib's TLS
    verification fails; the system curl has working roots. We keep verification ON
    (no -k) and just rely on curl's trust store.
    """
    last = ""
    for attempt in range(5):                      # resilient to transient SSL/network hiccups
        res = subprocess.run(
            ["curl", "-sSL", "--http1.1", "--retry", "4", "--retry-delay", "1",
             "--retry-all-errors", "--retry-connrefused", "--max-time", str(timeout), url],
            capture_output=True, timeout=timeout + 15)
        if res.returncode == 0 and res.stdout:
            return res.stdout
        last = res.stderr.decode(errors="replace")[:200]
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"curl failed for {url} after retries: {last}")


def _looks_like_html(text: str) -> bool:
    head = text.lstrip()[:200].lower()
    return head.startswith("<!doctype html") or head.startswith("<html")


def fetch_raw(fred_id: str, force: bool = False) -> str:
    """Download the raw CSV for a series and cache it. Returns the local path."""
    os.makedirs(RAW_DIR, exist_ok=True)
    path = os.path.join(RAW_DIR, f"{fred_id}.csv")
    if os.path.exists(path) and not force:
        return path
    # Offline mode (set by the deployed dashboard): never touch the network. Every series the
    # app uses is a committed cache under data/raw/, so a miss here is a packaging error, not a
    # reason to fetch. Fail loudly instead of making a runtime FRED request.
    if os.environ.get("SIGNAL_TOOL_NO_NETWORK"):
        raise RuntimeError(
            f"Offline mode: no cached CSV for {fred_id!r} at {path} and network is disabled "
            "(SIGNAL_TOOL_NO_NETWORK). Commit data/raw/{fred_id}.csv or run the pipeline "
            "locally without this flag to fetch it.")
    raw = _http_get(CSV_URL.format(id=fred_id)).decode("utf-8", errors="replace")
    if _looks_like_html(raw):
        raise ValueError(f"FRED returned HTML (not CSV) for id={fred_id!r} — "
                         "series likely does not exist.")
    if "observation_date" not in raw.splitlines()[0]:
        raise ValueError(f"Unexpected CSV header for id={fred_id!r}: "
                         f"{raw.splitlines()[0]!r}")
    with open(path, "w") as fh:
        fh.write(raw)
    return path


def fetch_title(fred_id: str) -> str:
    """Best-effort human title from the FRED series page (for metadata)."""
    try:
        html = _http_get(SERIES_PAGE.format(id=fred_id)).decode("utf-8", errors="replace")
        start = html.find("<title>")
        end = html.find("</title>", start)
        if start != -1 and end != -1:
            return html[start + 7:end].split(" | ")[0].strip()
    except Exception:
        pass
    return ""


def infer_frequency(idx: pd.DatetimeIndex) -> str:
    """Rough native frequency from median spacing: daily / weekly / monthly / quarterly."""
    if len(idx) < 3:
        return "unknown"
    gap = np.median(np.diff(idx.values).astype("timedelta64[D]").astype(int))
    if gap <= 3:
        return "daily"
    if gap <= 10:
        return "weekly"
    if gap <= 45:
        return "monthly"
    if gap <= 100:
        return "quarterly"
    return "annual"


def load_series(fred_id: str, force: bool = False, monthly: bool = True) -> pd.Series:
    """Return a monthly pandas Series (float, DatetimeIndex) for a FRED id.

    Higher-than-monthly series (daily/weekly, e.g. Treasury spreads, breakevens) are
    **month-averaged** to a month-start grid so a 12-period shift is a true 12-month YoY.
    Monthly series pass through unchanged. Quarterly/annual series stay at native spacing
    (they are flagged and excluded upstream — the protocol is monthly, no interpolation).
    """
    path = fetch_raw(fred_id, force=force)
    with open(path) as fh:
        df = pd.read_csv(io.StringIO(fh.read()))
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    # FRED encodes missing observations as "."; coerce to NaN and drop them.
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    s = df.dropna(subset=["value"]).set_index("date")["value"].astype(float).sort_index()
    if monthly and infer_frequency(s.index) in ("daily", "weekly"):
        # Average within each calendar month (standard for rates); label at month start.
        s = s.groupby(s.index.to_period("M")).mean()
        s.index = s.index.to_timestamp()
    s.name = fred_id
    return s


def spot_check(s: pd.Series, n_mid: int = 3) -> dict:
    """Return first / last / evenly-spaced mid observations for manual verification."""
    checks = {"first": _fmt(s.index[0], s.iloc[0]),
              "last": _fmt(s.index[-1], s.iloc[-1])}
    if len(s) > n_mid + 2:
        step = len(s) // (n_mid + 1)
        for i in range(1, n_mid + 1):
            idx = i * step
            checks[f"mid_{i}"] = _fmt(s.index[idx], s.iloc[idx])
    return checks


def _fmt(ts, val) -> str:
    return f"{pd.Timestamp(ts).date().isoformat()} = {val:g}"


def build_metadata(fred_id: str, s: pd.Series, title: str = "") -> dict:
    native = load_series(fred_id, monthly=False)      # un-resampled, for provenance
    native_freq = infer_frequency(native.index)
    return {
        "fred_id": fred_id,
        "title": title,                               # from manifest label (no slow HTML fetch)
        "n_obs": int(len(s)),
        "date_start": s.index[0].date().isoformat(),
        "date_end": s.index[-1].date().isoformat(),
        "native_frequency": native_freq,
        "used_frequency": "monthly",
        "resampled": native_freq in ("daily", "weekly"),
        "fetch_date": date.today().isoformat(),
        "source": CSV_URL.format(id=fred_id),
        "spot_checks": spot_check(native),
    }


def load_all(series_list, force: bool = False) -> tuple[dict, list]:
    """Load every series; return {id: pd.Series} and a list of metadata dicts."""
    data, meta = {}, []
    for spec in series_list:
        s = load_series(spec.fred_id, force=force)
        data[spec.fred_id] = s
        m = build_metadata(spec.fred_id, s, title=spec.label)
        m["label"] = spec.label
        meta.append(m)
    return data, meta
