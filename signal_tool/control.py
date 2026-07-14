"""Does a confirmed signal survive the broad commodity cycle?

Metal prices all rise and fall with a general commodity super-cycle. A signal that only
correlates with transformers *because* the whole complex is moving carries little unique,
actionable information. We test each confirmed signal three ways, all at its measured lead
lag k (signal_t vs transformer_{t+k}):

  1. RAW lead correlation           r(signal_t, transformer_{t+k})            — the headline.
  2. PARTIAL correlation | market   the same, statistically holding the broad commodity
                                    index (market_t) constant — the signal's unique co-
                                    movement with transformers after removing the cycle.
  3. RELATIVE-series correlation    r(signal_t - market_t, transformer_{t+k}) — how well the
                                    signal's EXCESS over the cycle predicts transformers.

The market control is a broad "all commodities" YoY series (FRED PPIACO by default).
Partial correlation:  r(X,Y|Z) = (r_XY - r_XZ r_YZ) / sqrt((1-r_XZ^2)(1-r_YZ^2)).
"""

import numpy as np
import pandas as pd

from . import process as P
from . import correlate as C


def partial_corr(x, y, z):
    r_xy = C.pearson(x, y)
    r_xz = C.pearson(x, z)
    r_yz = C.pearson(y, z)
    denom = np.sqrt((1 - r_xz ** 2) * (1 - r_yz ** 2))
    if denom == 0 or np.isnan(denom):
        return np.nan, (r_xy, r_xz, r_yz)
    return (r_xy - r_xz * r_yz) / denom, (r_xy, r_xz, r_yz)


def market_index(level_series_by_id, market_id):
    """YoY of the broad commodity market index."""
    return P.yoy(level_series_by_id[market_id])


def cycle_control(signal_level, outcome_level, market_yoy, lead_k):
    """Run the tests at lead lag k for a LEVEL signal. Returns a dict of results."""
    return cycle_control_yoy(P.yoy(signal_level), P.yoy(outcome_level), market_yoy, lead_k)


def cycle_control_yoy(signal_yoy, outcome_yoy, market_yoy, lead_k):
    """Same as cycle_control but takes YoY series directly (used for composites too).

    Everything is aligned so that at index t we observe (signal_t, market_t,
    transformer_{t+k}); the common sample is used for all measures so they compare.
    """
    sig = signal_yoy.rename("sig")
    tr_lead = outcome_yoy.shift(-lead_k).rename("tr")            # transformer_{t+k} at t
    mkt = market_yoy.rename("mkt")

    df = pd.concat([sig, mkt, tr_lead], axis=1).dropna()
    x = df["sig"].to_numpy()
    z = df["mkt"].to_numpy()
    y = df["tr"].to_numpy()
    n = len(df)

    raw_r = C.pearson(x, y)
    pcorr, (r_xy, r_xz, r_yz) = partial_corr(x, y, z)
    rel = x - z                                                  # naive signal minus cycle
    rel_r = C.pearson(rel, y)

    # Beta-adjusted, BOTH-SIDES de-cycled spread. beta = how many %pts the variable moves
    # per 1 %pt of the market. Removing beta*market from a variable strips its cycle
    # exposure correctly (regardless of its volatility). Correlating the two de-cycled
    # spreads reproduces the partial correlation exactly (it IS the partial correlation).
    beta_sig = _beta(x, z)
    beta_out = _beta(y, z)
    sig_spread = x - beta_sig * z
    out_spread = y - beta_out * z
    spread_r = C.pearson(sig_spread, out_spread)

    retained = (pcorr / raw_r) if (raw_r not in (0, None) and not np.isnan(raw_r)) else np.nan

    return {
        "lead_k": lead_k, "n": int(n),
        "raw_r": _r(raw_r),
        "partial_r": _r(pcorr),
        "spread_r": _r(spread_r),          # both-sides de-cycled == partial_r
        "beta_signal": _r(beta_sig),
        "beta_outcome": _r(beta_out),
        "relative_r": _r(rel_r),           # naive 1-for-1, diagnostic only
        "r_signal_market": _r(r_xz),
        "r_transformer_market": _r(r_yz),
        "fraction_retained": _r(retained),
        "survival": _survival(raw_r, pcorr),
    }


def _beta(v, z):
    """OLS slope of v on the market z (cov / var)."""
    var = np.var(z)
    return np.cov(v, z)[0, 1] / var if var > 0 else np.nan


def spread_series(signal_level, outcome_level, market_yoy, lead_k):
    """Return the observable de-cycled spread series for plotting.

    DataFrame indexed by month t with columns:
      signal_spread   = signal_t       − beta_signal  * market_t
      outcome_spread  = transformer_{t+k} − beta_outcome * market_t
    plus the raw YoY series for reference. The two spread columns are what a person could
    literally chart/monitor; their correlation equals the partial r.
    """
    return spread_series_yoy(P.yoy(signal_level), P.yoy(outcome_level), market_yoy, lead_k)


def spread_series_yoy(signal_yoy, outcome_yoy, market_yoy, lead_k):
    """Same as spread_series but takes YoY series directly (works for composites too)."""
    sig = signal_yoy.rename("signal_yoy")
    tr_lead = outcome_yoy.shift(-lead_k).rename("outcome_yoy")
    mkt = market_yoy.rename("market_yoy")
    df = pd.concat([sig, mkt, tr_lead], axis=1).dropna()
    x, z, y = df["signal_yoy"].to_numpy(), df["market_yoy"].to_numpy(), df["outcome_yoy"].to_numpy()
    bs, bo = _beta(x, z), _beta(y, z)
    df["signal_spread"] = x - bs * z
    df["outcome_spread"] = y - bo * z
    return df, {"beta_signal": _r(bs), "beta_outcome": _r(bo),
                "spread_r": _r(C.pearson(df["signal_spread"], df["outcome_spread"]))}


def force_spread(member_levels, outcome_level, market_yoy, max_lag):
    """Observable de-cycled spread for a whole FORCE (cluster composite).

    Builds the composite YoY, finds its own peak lead, then returns the two de-cycled
    spread series (composite spread vs transformer spread). Their correlation equals the
    force's partial r. Returns (df, meta, lead_k).
    """
    comp = composite_yoy(member_levels)
    out_yoy = P.yoy(outcome_level)
    a = pd.concat([comp.rename("c"), out_yoy.rename("o")], axis=1).dropna()
    _, peak = C.peak_lag_corr(a["c"].to_numpy(), a["o"].to_numpy(), max_lag)
    lead_k = int(peak[0]) if peak else 0
    df, meta = spread_series_yoy(comp, out_yoy, market_yoy, lead_k)
    return df, meta, lead_k


def composite_yoy(member_levels):
    """Average the YoY series of several signals into one 'force' index.

    Members are inner-joined (composite defined only where every member exists) and equally
    weighted. Because cluster members are ≥0.70 correlated, the average is a clean proxy for
    the shared underlying force with less idiosyncratic noise than any single member.
    """
    yoys = [P.yoy(lv).rename(f"m{i}") for i, lv in enumerate(member_levels)]
    df = pd.concat(yoys, axis=1).dropna()
    return df.mean(axis=1)


def force_cycle_control(member_levels, outcome_level, market_yoy, max_lag):
    """Cycle-control for a whole cluster: composite the members, find the composite's OWN
    peak lead, then run the partial-correlation test there. Returns (result_dict, lead_k).
    """
    comp = composite_yoy(member_levels)
    out_yoy = P.yoy(outcome_level)
    a = pd.concat([comp.rename("c"), out_yoy.rename("o")], axis=1).dropna()
    curve, peak = C.peak_lag_corr(a["c"].to_numpy(), a["o"].to_numpy(), max_lag)
    lead_k = int(peak[0]) if peak else 0
    res = cycle_control_yoy(comp, out_yoy, market_yoy, lead_k)
    res["n_members"] = len(member_levels)
    return res, lead_k


# Cycle-control thresholds.
PARTIAL_MIN = 0.20      # partial |r| at/above this = a real edge remains after the cycle control
CYCLE_DROP_MIN = 0.15   # AND the correlation must have fallen at least this much (|raw|−|partial|)
                        # for the loss to count as the cycle removing a real edge.


def is_cycle_driven(raw_r, pcorr):
    """True only when the broad cycle removed a REAL edge: the post-control partial is weak
    (|partial| < PARTIAL_MIN, or it flipped sign) AND the correlation actually dropped by at
    least CYCLE_DROP_MIN from raw to partial. An item that was already weak on its own
    (raw ≈ partial, small drop) is NOT cycle-driven — the cycle removed nothing."""
    if pcorr is None or (isinstance(pcorr, float) and np.isnan(pcorr)):
        return False
    weak_after = (abs(pcorr) < PARTIAL_MIN) or (np.sign(pcorr) != np.sign(raw_r))
    if not weak_after:
        return False
    if raw_r is None or (isinstance(raw_r, float) and np.isnan(raw_r)):
        return False                                   # can't establish a drop → don't assert it
    return (abs(raw_r) - abs(pcorr)) >= CYCLE_DROP_MIN


def _survival(raw_r, pcorr):
    """Plain-language read of whether signal-specific predictive power survives.

    Decided on the PARTIAL correlation — the statistically correct measure of "predicts
    transformers beyond the broad commodity cycle". The naive relative (signal − market)
    series is NOT used here: it assumes the signal moves 1-for-1 with the market, so for
    high-volatility signals (e.g. crude) it barely removes the cycle and overstates survival.

    "cycle-driven" is reserved for the case where the cycle actually REMOVED a real edge
    (see is_cycle_driven). An item that is weak after the control only because it was already
    weak to begin with (small raw→partial drop) is labelled "not cycle-driven (weak on its
    own)" so the tag never implies the cycle explained away an edge that wasn't there.
    """
    if pcorr is None or np.isnan(pcorr):
        return "n/a"
    if is_cycle_driven(raw_r, pcorr):
        return "cycle-driven"
    weak_after = (abs(pcorr) < PARTIAL_MIN) or (np.sign(pcorr) != np.sign(raw_r))
    if weak_after:
        return "not cycle-driven (weak on its own)"
    if abs(pcorr) >= 0.30:
        return "survives"
    return "partly survives"


def _r(v):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), 4)
