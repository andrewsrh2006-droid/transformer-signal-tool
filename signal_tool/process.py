"""Transparent processing: three views of each series, and alignment.

- level:      the raw series.
- yoy:        year-over-year % change, (x_t / x_{t-12} - 1) * 100  (cancels seasonality).
- yoy2:       second derivative = 12-month difference of the YoY series.

All series here are monthly and month-start dated on FRED, so a 12-period shift is a
true 12-month shift. Alignment is an inner join on the common monthly index, keeping
only months where BOTH the candidate and outcome YoY exist (no interpolation).
"""

import numpy as np
import pandas as pd


def yoy(level: pd.Series) -> pd.Series:
    """Year-over-year change (seasonality-cancelling 12-month transform).

    For strictly-positive series (prices, indices, yields) this is the protocol's
    **% change** `(x_t / x_{t-12} - 1) * 100`.

    For series that cross zero or go negative — yield-curve spreads (e.g. 10y-2y),
    regional-Fed diffusion indices, etc. — a percent change is meaningless (division by
    ~0, sign flips), so we use the **12-month level difference** `x_t - x_{t-12}` instead.
    Pearson r is scale-invariant, so mixing the two transforms across signals is fine; the
    choice is per-series and documented. Strictly-positive anchors are unaffected.
    """
    vals = level.dropna()
    if len(vals) and (vals <= 0).any():
        out = level - level.shift(12)                      # level Δ for zero-crossing series
    else:
        out = (level / level.shift(12) - 1.0) * 100.0      # % change for positive series
    out.name = level.name
    return out


def yoy2(level_or_yoy: pd.Series, is_yoy: bool = False) -> pd.Series:
    """Second derivative: 12-month difference of the YoY series."""
    y = level_or_yoy if is_yoy else yoy(level_or_yoy)
    out = y - y.shift(12)
    out.name = y.name
    return out


def three_views(level: pd.Series) -> dict:
    y = yoy(level)
    return {"level": level, "yoy": y, "yoy2": yoy2(y, is_yoy=True)}


def align(cand: pd.Series, outcome: pd.Series) -> pd.DataFrame:
    """Inner-join two series on a monthly index, dropping months missing in either.

    Returns a DataFrame with columns ['cand', 'outcome'] on a sorted monthly index.
    """
    df = pd.concat([cand.rename("cand"), outcome.rename("outcome")], axis=1)
    df = df.dropna(how="any").sort_index()
    return df


def to_monthly(s: pd.Series) -> pd.Series:
    """Normalise a series onto a month-start monthly grid (defensive; FRED already is).

    Reindexes to a continuous month-start range so that a 12-row shift is exactly a
    12-month shift even if the source had a gap. Missing months stay NaN (not filled).
    """
    idx = pd.period_range(s.index.min(), s.index.max(), freq="M").to_timestamp()
    return s.reindex(idx)
