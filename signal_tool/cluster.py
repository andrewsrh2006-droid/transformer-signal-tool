"""Hierarchical clustering of the leading signals from their YoY correlation matrix.

We turn the contemporaneous correlation matrix into a distance (`d = 1 - r`, so r=1 -> 0,
r=0 -> 1, r=-1 -> 2) and run agglomerative clustering with **average linkage** (UPGMA).
Average linkage is preferred over single linkage here: single linkage *chains* (two loosely
related signals get merged through a bridging third), which is exactly the artefact we want
to avoid when deciding what is "the same underlying force". Cutting the dendrogram at
`d = 1 - 0.70 = 0.30` yields the clusters at the 0.70 correlation cut.

Requires scipy (installed for this analysis).
"""

import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram, leaves_list
from scipy.spatial.distance import squareform


def correlation_distance(corr):
    """Symmetric distance matrix d = 1 - r (NaNs -> max distance 2)."""
    r = corr.to_numpy(dtype=float)
    r = np.where(np.isnan(r), -1.0, r)          # missing pair => maximally distant
    r = np.clip(r, -1.0, 1.0)
    d = 1.0 - r
    np.fill_diagonal(d, 0.0)
    d = (d + d.T) / 2.0                          # enforce exact symmetry
    return d


def linkage_matrix(corr, method="average"):
    d = correlation_distance(corr)
    condensed = squareform(d, checks=False)
    return linkage(condensed, method=method)


def clusters_at(Z, labels, cut_r=0.70):
    """Flat clusters at the given correlation cut. Returns {cluster_id: [labels]}."""
    t = 1.0 - cut_r
    assign = fcluster(Z, t=t, criterion="distance")
    out = {}
    for lab, cid in zip(labels, assign):
        out.setdefault(int(cid), []).append(lab)
    # Renumber so the biggest clusters come first, deterministically.
    ordered = sorted(out.values(), key=lambda m: (-len(m), m))
    return {i + 1: members for i, members in enumerate(ordered)}


def leaf_order(Z, labels):
    """Signal order along the dendrogram leaves (for a clustered heatmap)."""
    return [labels[i] for i in leaves_list(Z)]


def dendrogram_data(Z, labels, cut_r=0.70):
    """scipy dendrogram dict (no plotting) using the cut as the colour threshold."""
    return dendrogram(Z, labels=labels, color_threshold=1.0 - cut_r, no_plot=True)
