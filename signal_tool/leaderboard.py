"""Scoring and verdicts, and assembly of the ranked leaderboard.

Verdicts are assigned by RELATIONSHIP TYPE first, so the label agrees with the Lead-type and
Why columns on the dashboard. Every verdict belongs to one of four relationship groups — LEAD,
CO-MOVER, REVERSED, REJECTED — and within a group is graded by strength, robustness and
significance. Significance = FDR q < 0.05 AND the bootstrap 95% CI excludes zero (both must hold).

  REJECTED            — |r| < 0.30: no relationship in any direction.

  LEAD group (peak lag >= 0, forward lead):
  CONFIRMED           — |r| >= 0.50, passes the screen, significant, AND retains market-controlled
                        partial |r| >= 0.20 (survives the commodity cycle).
  STRONG BUT CYCLE-DRIVEN — a CONFIRMED forward lead whose partial |r| collapses below 0.20 once
                        the broad commodity cycle is removed.
  STRONG / NOT ROBUST — |r| >= 0.50, significant but FRAGILE: it fails a robustness gate
                        (smoothing / holds-over-time / episode).
  STRONG / NOT SIGNIFICANT — |r| >= 0.50, clears the gates but fails significance (q >= 0.05 or the
                        bootstrap CI spans zero): the correlation could be chance.
  PARTIAL / INCONCLUSIVE — moderate forward lead (0.30 <= |r| < 0.50).

  CO-MOVER group (peak at/near lag 0, moves WITH the outcome, at any |r| >= 0.30):
  CO-MOVER (not a lead) — co-movement that survives the commodity cycle.
  CO-MOVER (cycle-driven) — a co-mover whose partial |r| collapses below 0.20 once the cycle is
                        removed: the co-movement is just the cycle. (Cycle-first: this label wins
                        over "not significant".)
  CO-MOVER (not significant) — a co-mover that is NOT cycle-driven but could be chance
                        (q >= 0.05 or CI spans zero).

  REVERSED group (OUTCOME leads the candidate, peak lag < 0, at any |r| >= 0.30):
  REVERSED            — a reversal that survives the commodity cycle.
  REVERSED (cycle-driven) — a reversal whose partial |r| collapses once the cycle is removed: the
                        lag is just the cycle. (Cycle-first: wins over "not significant".)
  REVERSED (not significant) — a reversal that is NOT cycle-driven but could be chance.
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
    has_q = q_value is not None
    # Significant = FDR q < 0.05 AND the bootstrap 95% CI excludes zero. Both must hold, so a
    # relationship that could be chance on either test is "not significant".
    significant = has_q and (q_value < CFG.SIG_ALPHA) and ci_excludes_zero

    # 1. No relationship in any direction.
    if ar < CFG.R_MIN_SCREEN:
        return "REJECTED"

    # 2. Relationship type first — co-mover (near lag 0), then reversal (outcome leads). Each
    #    carries a significance sub-split: a co-mover / reversal whose FDR q >= 0.05 (or whose
    #    bootstrap CI spans zero) could be chance, and is named "(not significant)". Composites
    #    carry no q (has_q False) and keep the plain relationship label. apply_cycle_control later
    #    splits only the SIGNIFICANT ones into their (cycle-driven) variant; a (not significant)
    #    label is terminal (significance is the deeper doubt).
    if is_comover:
        return "CO-MOVER (not a lead)" if (not has_q or significant) else COMOVER_NOTSIG_VERDICT
    if peak_lag < 0:
        return "REVERSED" if (not has_q or significant) else REVERSED_NOTSIG_VERDICT

    # 3. Forward lead (lag >= 0, |r| >= 0.30): grade by strength / gates / significance.
    #    A strong forward lead that isn't CONFIRMED fails EITHER a robustness gate (structural:
    #    it's real & significant but fragile → STRONG / NOT ROBUST) OR statistical significance
    #    (it could be chance → STRONG / NOT SIGNIFICANT). Significance is checked after the gates
    #    because a gate failure is the more concrete defect. apply_cycle_control may later downgrade
    #    CONFIRMED to STRONG BUT CYCLE-DRIVEN.
    if ar >= CFG.R_STRONG:
        if not screen_pass:                       # a robustness gate (smoothing/holds/episode) failed
            return "STRONG / NOT ROBUST"
        if significant:
            return "CONFIRMED"
        return "STRONG / NOT SIGNIFICANT"         # gates pass, but q >= 0.05 or the CI spans zero
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
COMOVER_NOTSIG_VERDICT = "CO-MOVER (not significant)"
REVERSED_VERDICT = "REVERSED"
REVERSED_CYCLE_VERDICT = "REVERSED (cycle-driven)"
REVERSED_NOTSIG_VERDICT = "REVERSED (not significant)"


def apply_cycle_control(verdict_label: str, partial_r, raw_r=None) -> str:
    """Fold the market-cycle control into the verdict, only when the item is genuinely
    CYCLE-DRIVEN — the partial is weak AND the correlation actually dropped from raw to partial
    (see control.is_cycle_driven). An item that is weak on its own with a small drop is NOT
    downgraded (the cycle removed nothing).

    Precedence differs by relationship group:
      * LEAD group — significance-first. Only a CONFIRMED (already significant) forward lead is
        downgraded to STRONG BUT CYCLE-DRIVEN; a STRONG / NOT SIGNIFICANT lead is left alone
        (a relationship that could be chance isn't interpreted through the cycle).
      * CO-MOVER / REVERSED groups — cycle-first. For a non-lead, "is this just the commodity
        cycle?" is the more informative distinction, so the (cycle-driven) label wins over
        (not significant): a cycle-driven co-mover/reversal is tagged (cycle-driven) whether or
        not it is significant. (not significant) is thus reserved for co-movers/reversals that are
        NOT cycle-driven."""
    from . import control as CTRL
    if not CTRL.is_cycle_driven(raw_r, partial_r):
        return verdict_label
    if verdict_label == "CONFIRMED":
        return CYCLE_DRIVEN_VERDICT
    if verdict_label in (COMOVER_VERDICT, COMOVER_NOTSIG_VERDICT):
        return COMOVER_CYCLE_VERDICT
    if verdict_label in (REVERSED_VERDICT, REVERSED_NOTSIG_VERDICT):
        return REVERSED_CYCLE_VERDICT
    return verdict_label


# Rank order for sorting the leaderboard (best first).
VERDICT_RANK = {
    # Lead group
    "CONFIRMED": 0,
    "STRONG BUT CYCLE-DRIVEN": 1,
    "STRONG / NOT ROBUST": 2,
    "STRONG / NOT SIGNIFICANT": 3,
    "SHORT-SAMPLE (unverified)": 4,
    "PARTIAL / INCONCLUSIVE": 5,
    # Co-mover group
    "CO-MOVER (not a lead)": 6,
    "CO-MOVER (cycle-driven)": 7,
    "CO-MOVER (not significant)": 8,
    # Reversed group
    "REVERSED": 9,
    "REVERSED (cycle-driven)": 10,
    "REVERSED (not significant)": 11,
    # Rejected
    "REJECTED": 12,
}


def build_table(rows: list) -> pd.DataFrame:
    """rows: list of dicts (one per pair). Returns a sorted leaderboard DataFrame."""
    df = pd.DataFrame(rows)
    df["_vrank"] = df["verdict"].map(VERDICT_RANK).fillna(9)
    df["_absr"] = df["peak_r"].abs()
    df = df.sort_values(["_vrank", "_absr"], ascending=[True, False]).reset_index(drop=True)
    df.insert(0, "rank", df.index + 1)
    return df.drop(columns=["_vrank", "_absr"])
