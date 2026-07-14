"""Robustness screen: three disqualifying GATES and two CONFIRMATORY supports.

A pair passes the screen only if it actually leads (peak lag >= 0), |peak r| >= 0.30,
and NONE of the gates fail. The supports add confidence but never fail a pair on their own.

Gates:
  - Survives smoothing: smooth both YoY series with a centered 6-month rolling mean,
    recompute the peak. Pass if sign unchanged, lag within 6 months of the raw peak,
    and |r| >= 0.30.
  - Holds over time: split the aligned history at the peak lag into early/late halves.
    Pass if both halves share the full-sample sign and each |r| >= 0.20. This is a
    DIRECTIONAL check — it punishes a relationship that was strong early and decayed.
  - Episode-robust (block jackknife): at the peak lag, drop each ~3-year block of history
    in turn and recompute the YoY correlation on what remains. Pass only if the relationship
    survives every deletion. This complements "holds over time": the early/late split can be
    fooled by a single mid-sample episode that straddles both halves, whereas leaving out one
    block at a time isolates any single episode the whole correlation depends on. The Retailers
    Inventories-to-Sales signal (peak -0.55) is the archetype it catches: drop 2020-2022 and it
    collapses to about -0.16 — the entire relationship lived in the COVID inventory whipsaw.

Supports:
  - Second opinion: another candidate that is NOT itself highly correlated (>=0.70)
    with this one peaks with the same sign at a lag within 6 months, |r| >= 0.30.
  - Has a reason: a written mechanism exists (checked by the caller / config).
"""

import numpy as np
import pandas as pd

from . import correlate as C


def _smooth(arr: np.ndarray, win: int) -> np.ndarray:
    """Centered rolling mean; returns array with NaNs where the window is incomplete."""
    return pd.Series(arr).rolling(win, center=True, min_periods=win).mean().to_numpy()


def gate_smoothing(cand: np.ndarray, out: np.ndarray, raw_peak, max_lag: int,
                   win: int = 6, r_min: float = 0.30) -> dict:
    cs = _smooth(cand, win)
    os_ = _smooth(out, win)
    mask = ~(np.isnan(cs) | np.isnan(os_))
    cs, os_ = cs[mask], os_[mask]
    curve, peak = C.peak_lag_corr(cs, os_, max_lag)
    raw_lag, raw_r = raw_peak[0], raw_peak[1]
    passed = False
    if peak is not None:
        s_lag, s_r, _ = peak
        passed = (np.sign(s_r) == np.sign(raw_r)
                  and abs(s_lag - raw_lag) <= 6
                  and abs(s_r) >= r_min)
    return {"pass": bool(passed),
            "smoothed_lag": None if peak is None else peak[0],
            "smoothed_r": None if peak is None else round(peak[1], 4)}


# Stability thresholds for the "holds over time" gate. A genuine leading relationship
# should be roughly as strong in the recent half as in the early half. A signal whose
# correlation is carried by one episode (e.g. IR14220 copper-import: early r≈0.93, late
# r≈0.22 — all 2020-22 supercycle) must FAIL, not squeak through on same-sign + |r|≥0.20.
COLLAPSE_RATIO = 0.5      # late |r| must be at least this fraction of early |r|
MAX_HALF_DIFF = 0.30     # late |r| must not drop more than this below early |r| (directional)


def gate_holds_over_time(cand: np.ndarray, out: np.ndarray, raw_peak,
                         r_min: float = 0.20, collapse_ratio: float = COLLAPSE_RATIO,
                         max_half_diff: float = MAX_HALF_DIFF) -> dict:
    """r at the raw peak lag in the early vs late half of the aligned-at-lag pairs.

    Fails if the relationship is not *stable* across the sample: a sign flip, a weak half,
    a **collapse** (late |r| < collapse_ratio × early |r|), or the two halves differing by
    more than max_half_diff. The collapse/divergence tests are what catch a correlation that
    lives in a single window."""
    k, full_r = raw_peak[0], raw_peak[1]
    a, b = C._pair_at_lag(cand, out, k)
    n = a.size
    if n < 8:
        return {"pass": False, "early_r": None, "late_r": None, "reason": "too few points"}
    half = n // 2
    er = C.pearson(a[:half], b[:half])
    lr = C.pearson(a[half:], b[half:])
    if np.isnan(er) or np.isnan(lr):
        return {"pass": False, "early_r": None if np.isnan(er) else round(er, 4),
                "late_r": None if np.isnan(lr) else round(lr, 4), "reason": "degenerate half"}
    aer, alr = abs(er), abs(lr)
    reasons = []
    # The test is DIRECTIONAL: a collapse (early-strong -> late-weak) is the pathology we
    # punish; a relationship that *strengthened* recently is allowed to stay. So the
    # magnitude checks look only at the late half falling below the early half — never the
    # reverse. (A hard sign REVERSAL is still failed either way.)
    if alr < r_min:                                              # relationship gone recently
        reasons.append(f"late half weak (|r|={alr:.2f} < {r_min:g})")
    elif np.sign(lr) != np.sign(full_r):
        reasons.append("late half sign-flips vs full sample")
    if aer > 0 and alr < collapse_ratio * aer:                  # collapse (ratio)
        reasons.append(f"late |r| {alr:.2f} < {collapse_ratio:g}× early |r| {aer:.2f} (collapse)")
    if (aer - alr) > max_half_diff:                             # collapse (level, directional)
        reasons.append(f"late |r| drops {aer - alr:.2f} below early (>{max_half_diff:g})")
    if aer >= r_min and np.sign(er) != np.sign(full_r):         # early half opposes = reversal
        reasons.append("early half strongly opposes full sample (reversal)")
    return {"pass": not reasons,
            "early_r": round(er, 4), "late_r": round(lr, 4),
            "half_ratio": round(alr / aer, 4) if aer > 0 else None,
            "half_diff": round(aer - alr, 4),        # signed: positive = late weaker
            "reason": "; ".join(reasons) if reasons else "stable"}


# Episode-robustness (block-jackknife) parameters.
JACK_BLOCK_YEARS = 3       # width of each leave-one-out block (~3 years of monthly history)
JACK_ANCHOR_YEAR = 2020    # calendar grid anchor: blocks are ...,2017-19,2020-22,2023-25 so the
                           # COVID demand shock (2020-2022) falls in a single block, not split
JACK_R_FLOOR = 0.30        # a block fails if leaving it out drops |r| below this
JACK_COLLAPSE_RATIO = 0.5  # ...or below this fraction of the full-sample |r| (see note below)


def _index_at_lag(index, cand_n: int, k: int):
    """Candidate-side timestamps for the aligned-at-lag pairs (mirrors C._pair_at_lag)."""
    if k >= 0:
        return index[: cand_n - k]
    return index[-k:]


def _block_ids(index, n: int, block_years: int, anchor_year: int) -> tuple:
    """Assign each aligned-at-lag pair to a ~`block_years`-long block.

    With a real DatetimeIndex, blocks are a fixed calendar grid anchored so `anchor_year` starts
    a block (so 2020-2022 is one block). Without dates, fall back to equal contiguous chunks."""
    if index is not None:
        years = pd.DatetimeIndex(index).year.to_numpy()
        ids = np.floor((years - anchor_year) / block_years).astype(int)
        labels = {b: f"{years[ids == b].min()}-{years[ids == b].max()}" for b in np.unique(ids)}
        return ids, labels
    nblocks = max(2, round(n / (12 * block_years)))
    ids = np.empty(n, dtype=int)
    for i, chunk in enumerate(np.array_split(np.arange(n), nblocks)):
        ids[chunk] = i
    labels = {i: f"block {i + 1}/{nblocks}" for i in range(nblocks)}
    return ids, labels


def gate_episode_jackknife(cand: np.ndarray, out: np.ndarray, raw_peak, index=None,
                           block_years: int = JACK_BLOCK_YEARS, anchor_year: int = JACK_ANCHOR_YEAR,
                           r_floor: float = JACK_R_FLOOR,
                           collapse_ratio: float = JACK_COLLAPSE_RATIO) -> dict:
    """Leave-one-block-out jackknife at the peak lead lag.

    Drop each ~`block_years`-year block of aligned history in turn and recompute r on the rest.
    The signal is "episode-driven" — and fails — if removing any single block drops |r| below
    `r_floor` OR below `collapse_ratio` x the full-sample |r|. The relative (half-the-full)
    clause is CAPPED at the floor: min(collapse_ratio*|full|, r_floor) <= r_floor, so it never
    demands more than the floor of a very strong signal (e.g. the GOES-proxy core-steel lead,
    full r ~0.71, is held to 0.30 not 0.36). The operative per-block test is therefore |r|>=0.30.
    """
    k, full_r = raw_peak[0], raw_peak[1]
    a, b = C._pair_at_lag(cand, out, k)
    n = a.size
    idx = None if index is None else _index_at_lag(index, cand.size, k)
    if n < 24:
        return {"pass": True, "n_blocks": 0, "worst_r": None, "worst_block": None,
                "blocks": [], "floor": r_floor, "reason": "history too short to jackknife"}
    ids, labels = _block_ids(idx, n, block_years, anchor_year)
    uniq = np.unique(ids)
    if uniq.size < 2:
        return {"pass": True, "n_blocks": int(uniq.size), "worst_r": None, "worst_block": None,
                "blocks": [], "floor": r_floor, "reason": "fewer than 2 blocks"}
    # min(0.5*|full|, floor) <= floor, so failing the relative clause implies failing the floor.
    thr = min(collapse_ratio * abs(full_r), r_floor)
    blocks, worst = [], None
    for b_id in uniq:
        mask = ids != b_id
        r = C.pearson(a[mask], b[mask])
        blocks.append({"block": labels[b_id], "r": None if np.isnan(r) else round(float(r), 4),
                       "n_dropped": int((~mask).sum())})
        if not np.isnan(r) and (worst is None or abs(r) < abs(worst[1])):
            worst = (labels[b_id], float(r))
    failures = [blk for blk in blocks if blk["r"] is not None and abs(blk["r"]) < r_floor]
    passed = not failures
    if failures:
        wl, wr = worst
        reason = f"drops to {wr:+.2f} when {wl} removed (< {r_floor:g}) — episode-driven"
    else:
        reason = "stable across all blocks"
    return {"pass": bool(passed),
            "n_blocks": int(uniq.size),
            "worst_r": None if worst is None else round(worst[1], 4),
            "worst_block": None if worst is None else worst[0],
            "floor": r_floor, "rel_threshold": round(thr, 4), "full_r": round(float(full_r), 4),
            "blocks": blocks, "reason": reason}


def run_gates(cand: np.ndarray, out: np.ndarray, raw_peak, max_lag: int, index=None,
              smooth_win: int = 6, r_min_screen: float = 0.30) -> dict:
    g1 = gate_smoothing(cand, out, raw_peak, max_lag, win=smooth_win, r_min=r_min_screen)
    g2 = gate_holds_over_time(cand, out, raw_peak)
    g3 = gate_episode_jackknife(cand, out, raw_peak, index=index, r_floor=r_min_screen)
    leads = raw_peak[0] >= 0
    strong_enough = abs(raw_peak[1]) >= r_min_screen
    passed = leads and strong_enough and g1["pass"] and g2["pass"] and g3["pass"]
    return {"screen_pass": bool(passed), "leads": bool(leads),
            "strong_enough": bool(strong_enough),
            "smoothing_gate": g1, "holds_gate": g2, "episode_gate": g3}


def second_opinion(target_id: str, peaks: dict, inter_corr: pd.DataFrame,
                   cluster_r: float = 0.70, r_min: float = 0.30) -> dict:
    """Count independent corroborators for target_id.

    A corroborator is another candidate that (a) leads (lag>=0), (b) has the same peak
    sign, (c) peaks within 6 months of the target's lag, (d) |r| >= r_min, and
    (e) is NOT highly correlated (contemporaneous YoY |r| >= cluster_r) with the target
    — otherwise it is the same underlying force, not an independent witness.
    """
    tp = peaks[target_id]
    if tp is None:
        return {"n_corroborators": 0, "corroborators": []}
    t_lag, t_r = tp[0], tp[1]
    hits = []
    for other, op in peaks.items():
        if other == target_id or op is None:
            continue
        o_lag, o_r = op[0], op[1]
        if o_lag < 0:
            continue
        if np.sign(o_r) != np.sign(t_r):
            continue
        if abs(o_lag - t_lag) > 6:
            continue
        if abs(o_r) < r_min:
            continue
        try:
            ic = abs(inter_corr.loc[target_id, other])
        except KeyError:
            ic = np.nan
        if not np.isnan(ic) and ic >= cluster_r:
            continue  # same force — does not count as independent
        hits.append(other)
    return {"n_corroborators": len(hits), "corroborators": hits}
