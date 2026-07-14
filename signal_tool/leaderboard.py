"""Scoring and verdicts, and assembly of the ranked leaderboard.

Verdicts (from the brief, Section 5):
  CONFIRMED           — leads, |r| >= 0.50, passes the screen, p < 0.05, AND retains
                        market-controlled partial |r| >= 0.20 (survives the commodity cycle).
  STRONG BUT CYCLE-DRIVEN — strong, leading, robust and significant, but the partial |r|
                        collapses below 0.20 once the broad commodity cycle is removed: it
                        does not carry transformer-specific information beyond the cycle.
  STRONG / NOT ROBUST — strong (|r| >= 0.50) and correctly directed but fails the
                        screen or significance (a likely false correlation).
  REVERSED            — strong but the OUTCOME leads the candidate (peak lag < 0).
  REJECTED            — |r| < 0.30, or not significant.
  PARTIAL / INCONCLUSIVE — moderate (0.30 <= |r| < 0.50) or mixed.
"""

import pandas as pd

from . import config as CFG


# A peak only this many months on the negative side, whose |r| barely beats lag 0 (co-mover
# gain below COMOVER_MIN_GAIN), is contemporaneous noise — NOT a genuine reversal. REVERSED is
# reserved for the outcome leading by a meaningful margin (|lag| > COMOVER_MAX_LAG, or a real gain).
COMOVER_MAX_LAG = 2
COMOVER_MIN_GAIN = 0.05


def verdict(peak_r: float, peak_lag: int, screen_pass: bool, q_value: float,
            ci_excludes_zero: bool, is_comover: bool = False, lead_gain: float = None) -> str:
    """Assign a verdict. Significance uses the FDR q-value (not raw p) so that testing
    many signals doesn't manufacture false positives. A strong, significant, correctly
    directed pair that merely CO-MOVES (peak barely beats lag 0) is separated out as a
    CO-MOVER rather than credited as a lead — and a peak only 1-2 months on the negative side
    with the same co-mover signature is a CO-MOVER too, not a REVERSED."""
    ar = abs(peak_r)
    sig = (q_value is not None) and (q_value < CFG.SIG_ALPHA)   # FDR-controlled

    if ar < CFG.R_MIN_SCREEN:
        return "REJECTED"

    if peak_lag < 0:
        # Near-contemporaneous co-mover (|lag| <= 2 AND gain < 0.05): the −1/−2 is within noise,
        # so call it a CO-MOVER (if the co-movement is real), not a reversal. Only a peak that
        # meaningfully leads from the outcome side (bigger negative lag, or a real gain) is REVERSED.
        near_zero = abs(peak_lag) <= COMOVER_MAX_LAG
        weak_gain = (lead_gain is not None) and (abs(lead_gain) < COMOVER_MIN_GAIN)
        if near_zero and weak_gain:
            return "CO-MOVER (not a lead)" if sig else "REJECTED"
        return "REVERSED" if ar >= CFG.R_STRONG else "REJECTED"

    # peak_lag >= 0  (candidate leads)
    if ar >= CFG.R_STRONG:
        if screen_pass and sig and ci_excludes_zero:
            return "CO-MOVER (not a lead)" if is_comover else "CONFIRMED"
        return "STRONG / NOT ROBUST"

    # moderate: 0.30 <= |r| < 0.50, leading
    if screen_pass and sig:
        return "CO-MOVER (not a lead)" if is_comover else "PARTIAL / INCONCLUSIVE"
    return "REJECTED"


# A CONFIRMED item must ALSO carry transformer-specific information beyond the broad
# commodity cycle: its market-controlled partial |r| (at the measured lead) must be at least
# this. Otherwise it is strong, leading, robust and significant but merely riding the cycle,
# and is downgraded to STRONG BUT CYCLE-DRIVEN. This is applied identically to signals and to
# force composites.
CYCLE_PARTIAL_MIN = 0.20
CYCLE_DRIVEN_VERDICT = "STRONG BUT CYCLE-DRIVEN"


def apply_cycle_control(verdict_label: str, partial_r, raw_r=None) -> str:
    """Fold the market-cycle control into the verdict. Only CONFIRMED is affected, and only
    when the item is genuinely CYCLE-DRIVEN — the partial is weak AND the correlation actually
    dropped from raw to partial (see control.is_cycle_driven). An item that is weak on its own
    with a small drop is NOT downgraded. (A CONFIRMED item has raw |r| ≥ 0.50, so a collapse to
    partial < 0.20 always clears the drop threshold; the raw_r guard just makes this explicit.)"""
    if verdict_label != "CONFIRMED":
        return verdict_label
    from . import control as CTRL
    if CTRL.is_cycle_driven(raw_r, partial_r):
        return CYCLE_DRIVEN_VERDICT
    return verdict_label


# Rank order for sorting the leaderboard (best first).
VERDICT_RANK = {
    "CONFIRMED": 0,
    "STRONG BUT CYCLE-DRIVEN": 1,
    "STRONG / NOT ROBUST": 2,
    "SHORT-SAMPLE (unverified)": 3,
    "PARTIAL / INCONCLUSIVE": 4,
    "CO-MOVER (not a lead)": 5,
    "REVERSED": 6,
    "REJECTED": 7,
}


def build_table(rows: list) -> pd.DataFrame:
    """rows: list of dicts (one per pair). Returns a sorted leaderboard DataFrame."""
    df = pd.DataFrame(rows)
    df["_vrank"] = df["verdict"].map(VERDICT_RANK).fillna(9)
    df["_absr"] = df["peak_r"].abs()
    df = df.sort_values(["_vrank", "_absr"], ascending=[True, False]).reset_index(drop=True)
    df.insert(0, "rank", df.index + 1)
    return df.drop(columns=["_vrank", "_absr"])
