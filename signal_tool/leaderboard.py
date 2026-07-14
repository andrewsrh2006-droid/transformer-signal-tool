"""Scoring and verdicts, and assembly of the ranked leaderboard.

Verdicts are assigned by RELATIONSHIP TYPE first, so the label agrees with the Lead-type and
Why columns on the dashboard. Only a near-zero correlation is rejected outright; a co-mover or a
reversal is named as such at any strength, and a forward lead is then graded:
  REJECTED            — |r| < 0.30: no relationship in any direction.
  CO-MOVER (not a lead) — the peak sits at/near lag 0 (moves WITH the outcome, not ahead),
                        at any |r| >= 0.30, and its co-movement survives the commodity cycle.
  CO-MOVER (cycle-driven) — a co-mover whose partial |r| collapses below 0.20 once the broad
                        commodity cycle is removed: the co-movement is just the cycle.
  REVERSED            — the OUTCOME leads the candidate (peak lag < 0), at any |r| >= 0.30.
  CONFIRMED           — forward lead, |r| >= 0.50, passes the screen, q < 0.05, AND retains
                        market-controlled partial |r| >= 0.20 (survives the commodity cycle).
  STRONG BUT CYCLE-DRIVEN — a CONFIRMED forward lead whose partial |r| collapses below 0.20
                        once the broad commodity cycle is removed.
  STRONG / NOT ROBUST — forward lead, |r| >= 0.50, real & significant but FRAGILE: it fails a
                        robustness gate (smoothing / holds-over-time / episode).
  NOT SIGNIFICANT     — forward lead, |r| >= 0.50, clears the gates but fails the FDR
                        significance test (q >= 0.05) or its bootstrap CI spans zero: the
                        correlation could be chance. Worse than fragile, better than rejected.
  REVERSED (cycle-driven) — a reversal whose partial |r| collapses once the commodity cycle is
                        removed: the lag is just the cycle.
  PARTIAL / INCONCLUSIVE — moderate forward lead (0.30 <= |r| < 0.50).
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
    """Assign a verdict by RELATIONSHIP TYPE first, so it matches the Lead-type / Why columns.

    Order: |r| < 0.30 → REJECTED (no relationship in any direction); else a co-mover (peak near
    lag 0) → CO-MOVER; else the outcome leads (peak lag < 0) → REVERSED; else a forward lead
    (|r| >= 0.30, lag >= 0) is graded by strength, gates and significance. So REVERSED and
    CO-MOVER apply at ANY strength >= 0.30 — only a near-zero |r| is rejected. `is_comover` is
    the same near-lag-0 flag used by the Lead-type column (it already folds in the ±2 / small-gain
    contemporaneous band, so a −1/−2 near-zero peak is a co-mover, not a reversal). Significance
    uses the FDR q-value, not the raw p."""
    ar = abs(peak_r)
    sig = (q_value is not None) and (q_value < CFG.SIG_ALPHA)   # FDR-controlled

    # 1. No relationship in any direction.
    if ar < CFG.R_MIN_SCREEN:
        return "REJECTED"

    # 2. Relationship type first — co-mover (near lag 0), then reversal (outcome leads).
    if is_comover:
        return "CO-MOVER (not a lead)"
    if peak_lag < 0:
        return "REVERSED"

    # 3. Forward lead (lag >= 0, |r| >= 0.30): grade by strength / gates / significance.
    #    A strong forward lead that isn't CONFIRMED fails EITHER a robustness gate (structural:
    #    it's real & significant but fragile → STRONG / NOT ROBUST) OR statistical significance
    #    (it could be chance → NOT SIGNIFICANT). Significance is checked after the gates because
    #    a gate failure is the more concrete defect. apply_cycle_control may later downgrade
    #    CONFIRMED to STRONG BUT CYCLE-DRIVEN.
    if ar >= CFG.R_STRONG:
        if not screen_pass:                       # a robustness gate (smoothing/holds/episode) failed
            return "STRONG / NOT ROBUST"
        if sig and ci_excludes_zero:
            return "CONFIRMED"
        return "NOT SIGNIFICANT"                  # gates pass, but q >= 0.05 or the CI spans zero
    return "PARTIAL / INCONCLUSIVE"   # moderate forward lead (0.30 <= |r| < 0.50)


# A CONFIRMED item must ALSO carry transformer-specific information beyond the broad
# commodity cycle: its market-controlled partial |r| (at the measured lead) must be at least
# this. Otherwise it is strong, leading, robust and significant but merely riding the cycle,
# and is downgraded to STRONG BUT CYCLE-DRIVEN. This is applied identically to signals and to
# force composites.
CYCLE_PARTIAL_MIN = 0.20
CYCLE_DRIVEN_VERDICT = "STRONG BUT CYCLE-DRIVEN"
COMOVER_VERDICT = "CO-MOVER (not a lead)"
COMOVER_CYCLE_VERDICT = "CO-MOVER (cycle-driven)"
REVERSED_VERDICT = "REVERSED"
REVERSED_CYCLE_VERDICT = "REVERSED (cycle-driven)"


def apply_cycle_control(verdict_label: str, partial_r, raw_r=None) -> str:
    """Fold the market-cycle control into the verdict, only when the item is genuinely
    CYCLE-DRIVEN — the partial is weak AND the correlation actually dropped from raw to partial
    (see control.is_cycle_driven). A CONFIRMED forward lead is downgraded to STRONG BUT
    CYCLE-DRIVEN; a pure CO-MOVER or REVERSED is split off to its (cycle-driven) variant,
    separating a relationship that is transformer-specific from one that is merely the commodity
    cycle. NOT SIGNIFICANT is left alone (significance is the more fundamental doubt — we don't
    interpret the cycle for a relationship that could be chance). An item that is weak on its own
    with a small drop is NOT downgraded (the cycle removed nothing)."""
    from . import control as CTRL
    if not CTRL.is_cycle_driven(raw_r, partial_r):
        return verdict_label
    if verdict_label == "CONFIRMED":
        return CYCLE_DRIVEN_VERDICT
    if verdict_label == COMOVER_VERDICT:
        return COMOVER_CYCLE_VERDICT
    if verdict_label == REVERSED_VERDICT:
        return REVERSED_CYCLE_VERDICT
    return verdict_label


# Rank order for sorting the leaderboard (best first).
VERDICT_RANK = {
    "CONFIRMED": 0,
    "STRONG BUT CYCLE-DRIVEN": 1,
    "STRONG / NOT ROBUST": 2,
    "NOT SIGNIFICANT": 3,
    "SHORT-SAMPLE (unverified)": 4,
    "PARTIAL / INCONCLUSIVE": 5,
    "CO-MOVER (not a lead)": 6,
    "CO-MOVER (cycle-driven)": 7,
    "REVERSED": 8,
    "REVERSED (cycle-driven)": 9,
    "REJECTED": 10,
}


def build_table(rows: list) -> pd.DataFrame:
    """rows: list of dicts (one per pair). Returns a sorted leaderboard DataFrame."""
    df = pd.DataFrame(rows)
    df["_vrank"] = df["verdict"].map(VERDICT_RANK).fillna(9)
    df["_absr"] = df["peak_r"].abs()
    df = df.sort_values(["_vrank", "_absr"], ascending=[True, False]).reset_index(drop=True)
    df.insert(0, "rank", df.index + 1)
    return df.drop(columns=["_vrank", "_absr"])
