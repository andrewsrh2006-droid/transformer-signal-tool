#!/usr/bin/env python3
"""FRED API helper for the 200-signal acquisition phase.

Uses the FRED API (free key) only for DISCOVERY + METADATA — searching, enumerating a
category/release, and pulling reliable frequency/units/seasonal-adjustment info so we can
weight toward genuinely monthly, forward-looking series. Observations themselves are still
fetched by the keyless CSV endpoint in signal_tool.fred, so the key never enters the
reproducible pipeline or any committed file.

Key is read from the FRED_API_KEY environment variable — never hard-coded.

Usage:
  FRED_API_KEY=... python3 tools/fred_harvest.py meta ID1 ID2 ...
  FRED_API_KEY=... python3 tools/fred_harvest.py search "electrical equipment new orders" 20
  FRED_API_KEY=... python3 tools/fred_harvest.py release 46 500      # series in a release
  FRED_API_KEY=... python3 tools/fred_harvest.py category 31 200     # series in a category
"""

import json
import os
import subprocess
import sys
import time

BASE = "https://api.stlouisfed.org/fred"


def _key():
    k = os.environ.get("FRED_API_KEY")
    if not k:
        sys.exit("FRED_API_KEY not set. Run with FRED_API_KEY=... (paste via `!`).")
    return k


def _get(path, params):
    params = {**params, "api_key": _key(), "file_type": "json"}
    q = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE}/{path}?{q}"
    for attempt in range(4):
        res = subprocess.run(["curl", "-sSL", "--http1.1", "--max-time", "40", url],
                             capture_output=True)
        if res.returncode == 0 and res.stdout:
            try:
                return json.loads(res.stdout)
            except json.JSONDecodeError:
                pass
        time.sleep(1)
    raise RuntimeError(f"FRED API failed: {path} {params.get('series_id', params)}")


def meta(ids):
    """Print id | freq | sa | units | start..end | title for each series id."""
    out = []
    for sid in ids:
        try:
            j = _get("series", {"series_id": sid})
            s = j["seriess"][0]
            out.append({"id": sid, "freq": s["frequency_short"], "sa": s["seasonal_adjustment_short"],
                        "units": s["units_short"], "start": s["observation_start"],
                        "end": s["observation_end"], "title": s["title"]})
        except Exception as e:
            out.append({"id": sid, "error": str(e)[:80]})
    return out


def search(text, limit=20, extra=None):
    params = {"search_text": text.replace(" ", "+"), "limit": limit,
              "order_by": "popularity", "sort_order": "desc"}
    if extra:
        params.update(extra)
    j = _get("series/search", params)
    return [{"id": s["id"], "freq": s["frequency_short"], "title": s["title"],
             "start": s["observation_start"], "end": s["observation_end"]}
            for s in j.get("seriess", [])]


def release(rid, limit=1000):
    j = _get("release/series", {"release_id": rid, "limit": limit})
    return [{"id": s["id"], "freq": s["frequency_short"], "title": s["title"]}
            for s in j.get("seriess", [])]


def category(cid, limit=1000):
    j = _get("category/series", {"category_id": cid, "limit": limit})
    return [{"id": s["id"], "freq": s["frequency_short"], "title": s["title"]}
            for s in j.get("seriess", [])]


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "meta"
    if cmd == "meta":
        print(json.dumps(meta(sys.argv[2:]), indent=2))
    elif cmd == "search":
        print(json.dumps(search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 20), indent=2))
    elif cmd == "release":
        print(json.dumps(release(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 1000), indent=2))
    elif cmd == "category":
        print(json.dumps(category(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 1000), indent=2))
    else:
        sys.exit(f"unknown command {cmd}")
