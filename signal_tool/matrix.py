"""Correlation-of-correlations: how alike are the leading signals themselves?

Two candidates whose CONTEMPORANEOUS (lag 0) YoY series correlate >= 0.70 are largely
the same underlying force and must not be counted as two independent confirmations.
We build the full pairwise matrix on the candidates' YoY series (common overlap per
pair) and flag clusters of mutually-high-correlation signals.
"""

import numpy as np
import pandas as pd

from . import process as P


def contemporaneous_yoy_matrix(levels: dict, cand_ids: list) -> pd.DataFrame:
    """Pairwise Pearson r of candidate YoY series (each pair on its own overlap)."""
    yoys = {cid: P.yoy(levels[cid]) for cid in cand_ids}
    m = pd.DataFrame(index=cand_ids, columns=cand_ids, dtype=float)
    for i in cand_ids:
        for j in cand_ids:
            df = pd.concat([yoys[i].rename("a"), yoys[j].rename("b")], axis=1).dropna()
            m.loc[i, j] = df["a"].corr(df["b"]) if len(df) >= 4 else np.nan
    return m


def find_clusters(matrix: pd.DataFrame, threshold: float = 0.70) -> list:
    """Connected components where |r| >= threshold (single-linkage clustering)."""
    ids = list(matrix.index)
    parent = {i: i for i in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    for i in ids:
        for j in ids:
            if i < j and not np.isnan(matrix.loc[i, j]) and abs(matrix.loc[i, j]) >= threshold:
                union(i, j)

    comps = {}
    for i in ids:
        comps.setdefault(find(i), []).append(i)
    # Only report groups with >1 member (true clusters).
    return [sorted(members) for members in comps.values() if len(members) > 1]
