"""Lag correlation between a candidate's YoY and the outcome's YoY.

Convention (from the brief): positive lag k = candidate LEADS the outcome.
We correlate candidate_t with outcome_{t+k}. Peak = lag with the largest |r|.

Everything operates on two equal-length numpy arrays that are already aligned on a
common monthly index (see process.align). Working on arrays keeps the permutation
null (which circularly shifts one array) fast and unambiguous.
"""

import numpy as np


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson r with no external deps; NaN if degenerate."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    if a.size < 2:
        return np.nan
    a = a - a.mean()
    b = b - b.mean()
    denom = np.sqrt((a * a).sum() * (b * b).sum())
    if denom == 0:
        return np.nan
    return float((a * b).sum() / denom)


def _pair_at_lag(cand: np.ndarray, out: np.ndarray, k: int):
    """Return (cand_slice, out_slice) for lag k: cand_t vs out_{t+k}."""
    n = cand.size
    if k >= 0:
        if n - k < 1:
            return cand[:0], out[:0]
        return cand[: n - k], out[k:]
    m = -k
    if n - m < 1:
        return cand[:0], out[:0]
    return cand[m:], out[: n - m]


def lag_curve(cand: np.ndarray, out: np.ndarray, max_lag: int, min_n: int = 4):
    """Return dict k -> (r, n) for k in [-max_lag, max_lag] where n >= min_n."""
    curve = {}
    for k in range(-max_lag, max_lag + 1):
        a, b = _pair_at_lag(cand, out, k)
        if a.size >= min_n:
            curve[k] = (pearson(a, b), a.size)
    return curve


def peak_from_curve(curve: dict):
    """Return (lag, r, n) at the largest |r|. None if the curve is empty."""
    best = None
    for k, (r, n) in curve.items():
        if r is None or np.isnan(r):
            continue
        if best is None or abs(r) > abs(best[1]):
            best = (k, r, n)
    return best


def peak_lag_corr(cand: np.ndarray, out: np.ndarray, max_lag: int, min_n: int = 4):
    """Convenience: full curve + its peak."""
    curve = lag_curve(cand, out, max_lag, min_n=min_n)
    return curve, peak_from_curve(curve)


def peak_abs_r(cand: np.ndarray, out: np.ndarray, max_lag: int, min_n: int = 4) -> float:
    """Just the peak |r| over all lags (used inside the permutation null)."""
    peak = peak_from_curve(lag_curve(cand, out, max_lag, min_n=min_n))
    return abs(peak[1]) if peak else 0.0


def r_at_lag(cand: np.ndarray, out: np.ndarray, k: int) -> tuple:
    a, b = _pair_at_lag(cand, out, k)
    return pearson(a, b), a.size


# A negative peak this close to lag 0, whose |r| barely beats lag 0 (gain below `min_gain`),
# is contemporaneous noise, not a genuine reversal — the SAME band leaderboard.verdict uses to
# call such a peak a CO-MOVER rather than REVERSED. Keeping the label on this band aligned with
# the verdict avoids a row reading verdict "CO-MOVER" but label "lags" at the same time.
COMOVER_MAX_LAG = 2


def lead_sharpness(curve: dict, peak, min_lead: int = 1, min_gain: float = 0.05,
                   comover_max_lag: int = COMOVER_MAX_LAG) -> dict:
    """Classify a peak by WHERE it sits relative to lag 0. Three mutually exclusive cases:

      * ``true lead`` — the peak leads (lag >= +1) AND its |r| beats lag-0 |r| by >= min_gain.
      * ``co-mover``  — the peak sits within +-`comover_max_lag` of lag 0 with a negligible
                        gain (< min_gain): it moves *with* the outcome, not ahead of it. FDR
                        does not catch these — a co-mover can be wildly significant.
      * ``lags``      — the peak is a genuine NEGATIVE lead (lag <= -1 and either beyond the
                        +-`comover_max_lag` band or with a real gain): the OUTCOME moves first
                        and the candidate trails it. A reversed laggard, never a co-mover; its
                        verdict (REVERSED) is decided in leaderboard.verdict on the same band.

    `is_comover` is True for the ``co-mover`` case ONLY. Previously it also tripped on any
    peak below the min lead, which lumped negative-lag laggards in with contemporaneous
    co-movers; that is fixed here so only genuine near-lag-0 signals carry the flag.
    """
    if peak is None:
        return {"r_lag0": None, "lead_gain": None, "is_comover": False,
                "lead_class": "undetermined"}
    peak_lag, peak_r = peak[0], peak[1]
    r0 = curve.get(0, (float("nan"),))[0]
    if r0 is None or np.isnan(r0):
        return {"r_lag0": None, "lead_gain": None, "is_comover": False,
                "lead_class": "undetermined"}
    gain = abs(peak_r) - abs(r0)
    if peak_lag <= -1:
        # contemporaneous (near lag 0 AND barely beats it) -> co-mover; otherwise a real reversal
        if abs(peak_lag) <= comover_max_lag and gain < min_gain:
            lead_class = "co-mover"
        else:
            lead_class = "lags"                  # outcome leads the candidate: negative lead
    elif peak_lag >= min_lead and gain >= min_gain:
        lead_class = "true lead"                 # leads forward and clearly beats lag 0
    else:
        lead_class = "co-mover"                  # at/near lag 0, barely beats it
    return {"r_lag0": round(float(r0), 4), "lead_gain": round(float(gain), 4),
            "is_comover": lead_class == "co-mover", "lead_class": lead_class}
