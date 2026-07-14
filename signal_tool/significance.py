"""Resampling significance: circular-shift permutation p-value and block-bootstrap CI.

Ordinary p-values are invalid here (autocorrelation + a 49-lag search), so we use:

- Permutation p-value: generate surrogates by CIRCULARLY SHIFTING the outcome array by
  a random offset (>= max_lag, wrapping). This keeps each series' own autocorrelation
  but destroys the cross relationship. For each surrogate we recompute the PEAK |r| over
  ALL lags, so the multi-lag search is baked into the null.
      p = (#surrogates with peak|r| >= observed peak|r|, + 1) / (n_surrogates + 1)

- Confidence interval: moving-block bootstrap at the peak lag (block length ~12 months),
  reporting the 2.5/97.5 percentiles of r. It should exclude 0.

A seeded numpy Generator makes results reproducible (the harness also forbids
Math.random-style nondeterminism).
"""

import numpy as np

from . import correlate as C


def permutation_pvalue(cand: np.ndarray, out: np.ndarray, observed_peak_abs_r: float,
                       max_lag: int, n_surrogates: int = 1000, seed: int = 12345) -> dict:
    rng = np.random.default_rng(seed)
    n = out.size
    lo, hi = max_lag, n - max_lag  # shift offsets that are non-trivial and leave overlap
    if hi <= lo:
        return {"p_value": np.nan, "n_surrogates": 0, "n_ge": None}
    ge = 0
    for _ in range(n_surrogates):
        shift = int(rng.integers(lo, hi))
        surrogate = np.roll(out, shift)
        if C.peak_abs_r(cand, surrogate, max_lag) >= observed_peak_abs_r:
            ge += 1
    p = (ge + 1) / (n_surrogates + 1)
    return {"p_value": p, "n_surrogates": n_surrogates, "n_ge": ge}


def benjamini_hochberg(pvalues) -> list:
    """Benjamini-Hochberg FDR q-values for a list of p-values.

    Controls the expected proportion of false positives among the signals declared
    significant — essential when testing many candidates, where p<0.05 alone yields
    ~5% of all signals as lucky false positives. Returns q-values aligned to the input
    order; declare significant where q < target FDR (e.g. 0.05).
    """
    p = np.asarray(pvalues, float)
    n = p.size
    order = np.argsort(p)
    ranked = p[order]
    # q_i = min over k>=i of ( p_(k) * n / k )
    q_sorted = ranked * n / (np.arange(1, n + 1))
    q_sorted = np.minimum.accumulate(q_sorted[::-1])[::-1]
    q_sorted = np.clip(q_sorted, 0, 1)
    q = np.empty(n)
    q[order] = q_sorted
    return q.tolist()


def block_bootstrap_ci(cand: np.ndarray, out: np.ndarray, peak_lag: int,
                       n_boot: int = 2000, block_len: int = 12, seed: int = 12345) -> dict:
    """Moving-block bootstrap of r at the peak lag; 95% percentile interval."""
    rng = np.random.default_rng(seed + 1)
    a, b = C._pair_at_lag(cand, out, peak_lag)
    n = a.size
    if n < block_len + 2:
        return {"ci_low": np.nan, "ci_high": np.nan, "excludes_zero": False, "n": int(n)}
    n_blocks = int(np.ceil(n / block_len))
    max_start = n - block_len
    rs = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, max_start + 1, size=n_blocks)
        idx = (starts[:, None] + np.arange(block_len)[None, :]).ravel()[:n]
        rs[i] = C.pearson(a[idx], b[idx])
    rs = rs[~np.isnan(rs)]
    lo, hi = np.percentile(rs, [2.5, 97.5])
    return {"ci_low": round(float(lo), 4), "ci_high": round(float(hi), 4),
            "excludes_zero": bool(lo > 0 or hi < 0), "n": int(n)}
