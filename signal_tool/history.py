"""Minimum-history guardrail: catch correlations inflated by a short window.

A signal whose usable overlap with the outcome is short (few months, or a start date
after the 2010s) can post a spectacular lead-correlation that is really just the one big
2020-22 commodity supercycle filling its entire sample. Pearson r has no idea the sample
is short; it will happily report +0.86 off ~80 months that are all one boom-and-bust.

Two defences, per the brief:

1. **Short-sample flag + CONFIRMED gate.** Flag any signal with usable `n < MIN_MONTHS`
   OR a sample starting after `LATE_START`. A short signal is *excluded from CONFIRMED*
   unless a long, independent series measuring the same thing (a pre-2010 co-member of its
   ≥0.70 cluster that is itself confirmed) corroborates it — AND it is not a window artifact.

2. **Window-artifact check.** For a short signal, re-measure a long benchmark (copper PPI,
   1967-start) *restricted to the short signal's own window*. If a generic long metal
   already scores about the same correlation over that window, the signal's "edge" is the
   window, not the signal. We report the benchmark's correlation over the short window
   next to its correlation over full history; the gap (`window_inflation`) shows how much
   that particular window puffs up any metal.
"""

import pandas as pd

from . import process as P
from . import correlate as C

# Thresholds (the brief's "~150 months / after ~2010").
MIN_MONTHS = 150
LATE_START = pd.Timestamp("2010-01-01")

# Long, generic metal benchmark used for the window-artifact check: domestic copper PPI,
# monthly back to 1967 — same span as the transformer outcome, spans many cycles.
BENCHMARK_ID = "WPUSI019011"
BENCHMARK_LABEL = "Copper PPI (1967-start benchmark)"

# A short signal is a "window artifact" when a generic long metal already reaches roughly
# the same correlation over the *same* window: the benchmark clears this bar AND the signal
# fails to beat it by more than BEATS_MARGIN.
ARTIFACT_BENCH_R = 0.60
BEATS_MARGIN = 0.10


def sample_window(aligned_df) -> dict:
    """Usable overlap (post-YoY, contemporaneous) of a candidate with the outcome."""
    idx = aligned_df.index
    return {"start": idx[0], "end": idx[-1], "n": int(len(aligned_df))}


def is_short(start, n: int) -> tuple:
    """Return (short?, reason). Short if too few usable months or a post-2010 start."""
    reasons = []
    if n < MIN_MONTHS:
        reasons.append(f"only {n} usable months (<{MIN_MONTHS})")
    if pd.Timestamp(start) > LATE_START:
        reasons.append(f"sample starts {pd.Timestamp(start).date()} (after {LATE_START.date()})")
    return (len(reasons) > 0, "; ".join(reasons))


def _peak_lead_r(cand_level, out_level, max_lag, restrict=None):
    """Peak lead-|r| (positive lag only) of cand YoY vs outcome YoY, optionally restricted
    to a [start, end] window. Returns (lag, r, n) or None."""
    cy, oy = P.yoy(cand_level), P.yoy(out_level)
    if restrict is not None:
        s, e = restrict
        cy = cy[(cy.index >= s) & (cy.index <= e)]
        oy = oy[(oy.index >= s) & (oy.index <= e)]
    df = P.align(cy, oy)
    if len(df) < 8:
        return None
    a, b = df["cand"].to_numpy(), df["outcome"].to_numpy()
    curve, _ = C.peak_lag_corr(a, b, max_lag)
    # Restrict to leads (k >= 0), matching the protocol's "candidate leads" convention.
    lead = {k: v for k, v in curve.items() if k >= 0}
    return C.peak_from_curve(lead)


def window_artifact_check(signal_level, out_level, bench_level, window, signal_r,
                          max_lag) -> dict:
    """Compare a short signal's correlation with the same-window correlation of the long
    benchmark, and with the benchmark's full-history correlation.

    Returns the numbers plus a boolean `window_artifact`.
    """
    s, e = window["start"], window["end"]
    bench_win = _peak_lead_r(bench_level, out_level, max_lag, restrict=(s, e))
    bench_full = _peak_lead_r(bench_level, out_level, max_lag, restrict=None)
    bwin_r = abs(bench_win[1]) if bench_win else float("nan")
    bfull_r = abs(bench_full[1]) if bench_full else float("nan")
    beats = abs(signal_r) - bwin_r
    artifact = (bwin_r == bwin_r) and (bwin_r >= ARTIFACT_BENCH_R) and (beats <= BEATS_MARGIN)
    return {
        "signal_r": round(abs(signal_r), 4),
        "bench_r_same_window": round(bwin_r, 4) if bwin_r == bwin_r else None,
        "bench_lead_same_window": bench_win[0] if bench_win else None,
        "bench_r_full_history": round(bfull_r, 4) if bfull_r == bfull_r else None,
        "window_inflation": round(bwin_r - bfull_r, 4) if (bwin_r == bwin_r and bfull_r == bfull_r) else None,
        "signal_beats_benchmark": round(beats, 4) if bwin_r == bwin_r else None,
        "window_artifact": bool(artifact),
    }


def long_corroborators(short_id, clusters, is_long_by_id, confirmed_ids) -> list:
    """Long (pre-2010, n≥MIN) co-members of the short signal's ≥0.70 cluster that are
    themselves confirmed — i.e. an independent long series measuring the same force."""
    for cl in clusters:
        if short_id in cl:
            return [c for c in cl if c != short_id and is_long_by_id.get(c, False)
                    and c in confirmed_ids]
    return []
