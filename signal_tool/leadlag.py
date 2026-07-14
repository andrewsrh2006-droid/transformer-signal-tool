"""Lead-lag propagation map: directed 'A leads B' edges among a set of series.

Read-only diagnostic — it changes no scoring. Everything else in the tool measures
item -> transformer; this measures item -> other item, to expose the propagation chain
(e.g. steel scrap -> steel -> transformer) that the item->transformer tests alone cannot show.

For every ordered pair (A, B) we find the positive lag k in 1..max_lag at which A best leads B
on their YoY series, and keep a directed edge A -> B only if it is a GENUINE lead:
  - k >= 1                     (A actually precedes B, not contemporaneous),
  - |r| >= r_min               (the lead correlation is strong), and
  - lead-sharpness gain >= min_gain over lag 0  (the same co-mover check used elsewhere —
    the peak must beat lag-0 |r|, so a pure co-mover is not counted as a lead).
"""
import numpy as np
import pandas as pd

from . import correlate as C


def best_positive_lead(a: np.ndarray, b: np.ndarray, max_lag: int,
                       r_min: float, min_gain: float):
    """a, b: aligned YoY arrays. Return (lag, r, n, gain) for the best positive lag at which a
    leads b and the lead is genuine, else None. Positive lag k means a(t) tracks b(t+k)."""
    if a.size < max_lag + 8:
        return None
    curve, _ = C.peak_lag_corr(a, b, max_lag)
    r0 = curve.get(0, (np.nan,))[0]
    best = None
    for k in range(1, max_lag + 1):
        rk = curve.get(k)
        if rk is None or np.isnan(rk[0]):
            continue
        if best is None or abs(rk[0]) > abs(best[1]):
            best = (k, rk[0], rk[1])
    if best is None:
        return None
    k, r, n = best
    gain = abs(r) - (0.0 if np.isnan(r0) else abs(r0))
    if abs(r) < r_min or gain < min_gain:
        return None
    return k, float(r), int(n), float(gain)


def edges(yoy_by_id: dict, ids: list, labels: dict, max_lag: int = 24,
          r_min: float = 0.50, min_gain: float = 0.05) -> pd.DataFrame:
    """Directed genuine-lead edges over every ordered pair of the given nodes.

    yoy_by_id: {id -> YoY pandas Series (DatetimeIndex)}. Returns a DataFrame with one row per
    kept edge: source_id, target_id, source, target, lag, r, gain, n."""
    frame = pd.DataFrame({i: yoy_by_id[i] for i in ids})
    out = []
    for a_id in ids:
        sa = frame[a_id]
        for b_id in ids:
            if a_id == b_id:
                continue
            sub = pd.concat([sa, frame[b_id]], axis=1).dropna()
            if len(sub) < max_lag + 8:
                continue
            res = best_positive_lead(sub.iloc[:, 0].to_numpy(), sub.iloc[:, 1].to_numpy(),
                                     max_lag, r_min, min_gain)
            if res is None:
                continue
            k, r, n, gain = res
            out.append({"source_id": a_id, "target_id": b_id,
                        "source": labels.get(a_id, a_id), "target": labels.get(b_id, b_id),
                        "lag": k, "r": round(r, 4), "gain": round(gain, 4), "n": n})
    return pd.DataFrame(out, columns=["source_id", "target_id", "source", "target",
                                      "lag", "r", "gain", "n"])
