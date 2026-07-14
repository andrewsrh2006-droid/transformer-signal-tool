#!/usr/bin/env python3
"""Average- vs complete-linkage comparison — a chain-effect diagnostic.

Read-only. Reuses the SAME contemporaneous (lag-0) YoY correlation matrix and the SAME
r>=0.70 cut the production clustering uses (outputs/leading_signal_corr_matrix.csv), and
the peak correlations from outputs/leaderboard.csv. Changes nothing in the pipeline.

Average linkage (UPGMA) merges on the *mean* inter-group distance, so a loose pair can be
pulled into a group through a bridging third signal — the classic **chain effect** that
produces grab-bag clusters. Complete linkage merges only when *every* pair is within the
threshold, so its clusters are tight refinements. Comparing the two tells us which of our
"forces" are genuine (identical under both) and which are average-linkage artifacts.

Output: outputs/linkage_compare.md + a short console summary.
Run:  python3 tools/linkage_compare.py
"""
import csv
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from signal_tool import cluster as CL
OUT = os.path.join(ROOT, "outputs")
CUT_R = 0.70


def load():
    M = pd.read_csv(os.path.join(OUT, "leading_signal_corr_matrix.csv"), index_col=0)
    M.columns = list(M.index)                       # ensure ids match exactly
    label, peak_r, lead = {}, {}, {}
    with open(os.path.join(OUT, "leaderboard.csv")) as fh:
        for r in csv.DictReader(fh):
            label[r["fred_id"]] = r["signal"]
            peak_r[r["fred_id"]] = float(r["peak_r"])
            lead[r["fred_id"]] = int(r["measured_lead_months"])
    return M, label, peak_r, lead


def tightness(members, M):
    """Weakest internal link = min pairwise correlation between any two members."""
    if len(members) < 2:
        return None
    vals = [M.loc[a, b] for i, a in enumerate(members) for b in members[i + 1:]]
    return float(np.nanmin(vals))


def cluster_sets(M, method):
    Z = CL.linkage_matrix(M, method=method)
    clusters = CL.clusters_at(Z, list(M.index), CUT_R)      # {cid: [members]}
    return list(clusters.values())


def summarize(clusters, M):
    multi = [c for c in clusters if len(c) > 1]
    singles = [c for c in clusters if len(c) == 1]
    return {
        "multi": multi, "n_multi": len(multi), "n_single": len(singles),
        "n_forces": len(multi) + len(singles),
        "tight": {frozenset(c): tightness(c, M) for c in multi},
    }


def sign_split(members, peak_r):
    """Does the cluster mix positive-lead and negative-relationship members?"""
    pos = [m for m in members if peak_r.get(m, 0) > 0]
    neg = [m for m in members if peak_r.get(m, 0) < 0]
    return pos, neg


def main():
    M, label, peak_r, lead = load()
    ids = list(M.index)
    avg = summarize(cluster_sets(M, "average"), M)
    com = summarize(cluster_sets(M, "complete"), M)

    avg_sets = {frozenset(c) for c in avg["multi"]}
    com_sets = {frozenset(c) for c in com["multi"]}
    com_all = {frozenset(c) for c in cluster_sets(M, "complete")}

    robust = avg_sets & com_sets                    # identical multi-cluster in both
    avg_only = avg_sets - com_sets                   # average-linkage-only (grab-bags)
    com_only = com_sets - avg_sets                   # complete-only (tight sub-clusters)

    avg_singletons = {next(iter(c)) for c in cluster_sets(M, "average") if len(c) == 1}
    com_singletons = {next(iter(c)) for c in cluster_sets(M, "complete") if len(c) == 1}

    def nm(m):
        return label.get(m, m).split(" (")[0]

    def fmt_members(members):
        members = sorted(members, key=lambda m: -abs(peak_r.get(m, 0)))
        return ", ".join(f"{nm(m)} ({peak_r.get(m, 0):+.2f}@{lead.get(m, 0):+d})" for m in members)

    L = ["# Linkage comparison — average vs complete (chain-effect diagnostic)", "",
         f"Same lag-0 YoY correlation matrix ({len(ids)} signals), same cut **r ≥ {CUT_R:.2f}**. "
         "Read-only; the production clustering is unchanged.", "",
         "| Method | Multi-signal clusters | Singletons | **Total forces** |",
         "|--------|-----------------------|-----------|------------------|",
         f"| Average (UPGMA, production) | {avg['n_multi']} | {avg['n_single']} | **{avg['n_forces']}** |",
         f"| Complete (max-linkage) | {com['n_multi']} | {com['n_single']} | **{com['n_forces']}** |",
         "",
         "*Tightness* = the weakest internal link (minimum pairwise r between any two members). "
         "A tightness well below the 0.70 cut means members were joined transitively, not "
         "because they are all mutually ≥0.70 correlated — the chain effect.", ""]

    def cluster_table(summary, title):
        rows = ["## " + title, "",
                "| Size | Tightness (min pairwise r) | Members (peak r @ lead) |",
                "|------|----------------------------|-------------------------|"]
        for c in sorted(summary["multi"], key=lambda c: (-len(c), -(summary["tight"][frozenset(c)] or 0))):
            t = summary["tight"][frozenset(c)]
            flag = " ⚠️" if (t is not None and t < CUT_R) else ""
            rows.append(f"| {len(c)}{flag} | {t:+.2f} | {fmt_members(c)} |")
        rows.append("")
        return rows

    L += cluster_table(avg, f"Average linkage — {avg['n_multi']} multi-signal clusters")
    L += cluster_table(com, f"Complete linkage — {com['n_multi']} multi-signal clusters")

    # ---- Stability section
    L += ["## Stability: which forces are robust vs artifacts", "",
          f"**{len(robust)} robust force(s)** — the exact same member set is a cluster under "
          "BOTH average and complete linkage. Keep these.", ""]
    for c in sorted(robust, key=lambda c: -len(c)):
        t = avg["tight"][c]
        L.append(f"- **({len(c)}, tightness {t:+.2f})** {fmt_members(c)}")

    # Split average-only into genuinely-loose (chain effect) vs tight-but-reassigned.
    loose = sorted([c for c in avg_only if (avg["tight"][c] or 0) < CUT_R], key=lambda c: -len(c))
    reassigned = sorted([c for c in avg_only if (avg["tight"][c] or 0) >= CUT_R], key=lambda c: -len(c))
    dangerous = [c for c in avg_only if all(sign_split(list(c), peak_r))]

    L += ["",
          f"**{len(avg_only)} average-linkage-only cluster(s)** — the exact member set is a cluster "
          "under average but NOT under complete linkage. These come in two kinds; the tightness "
          "tells them apart:", "",
          f"- **{len(loose)} genuinely loose (tightness < {CUT_R:.2f}) → chain-effect grab-bags.** "
          "Members are held together transitively, not by mutual ≥0.70 correlation. These fragment "
          "under complete linkage.",
          f"- **{len(reassigned)} tight (tightness ≥ {CUT_R:.2f}) but partition-boundary differs.** "
          "All members are mutually ≥0.70, but complete linkage reassigned a member to an even "
          "tighter neighbouring group, so the exact set isn't a complete cluster. Not a grab-bag.", "",
          "### Chain-effect grab-bags (loose average-only clusters)", ""]
    for c in loose:
        members = list(c)
        t = avg["tight"][c]
        pos, neg = sign_split(members, peak_r)
        mixed = bool(pos) and bool(neg)
        pieces = [cc for cc in com_all if cc <= c]
        piece_sizes = sorted((len(p) for p in pieces), reverse=True)
        L += [f"#### ({len(members)}, tightness {t:+.2f}) — "
              + ("🚨 SIGN CONFLICT" if mixed else "sign-consistent"),
              f"- Members: {fmt_members(members)}",
              f"- Weakest internal link: **{t:+.2f}** (cut is {CUT_R:.2f}) — joined transitively.",
              f"- Under complete linkage it fragments into pieces of sizes {piece_sizes}."]
        if mixed:
            L += [f"- 🚨 **Sign conflict:** {len(pos)} positive-lead vs {len(neg)} negative member(s) "
                  "averaged into one 'force' — a positive lead and a negative relationship in the "
                  "same bag is exactly the dangerous chain effect.",
                  f"    - positive: {', '.join(nm(m) + f' ({peak_r[m]:+.2f})' for m in sorted(pos, key=lambda m:-peak_r[m]))}",
                  f"    - negative: {', '.join(nm(m) + f' ({peak_r[m]:+.2f})' for m in sorted(neg, key=lambda m:peak_r[m]))}"]
        else:
            s = "positive" if (pos and not neg) else "negative"
            L.append(f"- Sign check: all {len(members)} members share the **{s}** peak sign — over-merged "
                     "but directionally consistent, so treating it as one force merely *under*-counts "
                     "witnesses (conservative), it does not average opposite signs together.")
        L.append("")
    if reassigned:
        L += ["### Tight-but-reassigned (average-only, tightness ≥ cut — not grab-bags)", ""]
        for c in reassigned:
            L.append(f"- **({len(c)}, tightness {avg['tight'][c]:+.2f})** {fmt_members(c)}")
        L.append("")

    # ---- Verdict on current forces
    danger_loose = [c for c in loose if all(sign_split(list(c), peak_r))]
    L += ["## Verdict — do our current (average-linkage) forces survive complete linkage?", "",
          f"- **{len(robust)} of {avg['n_multi']}** multi-signal forces are identical under complete "
          f"linkage → **robust, genuine forces — keep.**",
          f"- **{len(reassigned)} of {avg['n_multi']}** differ only by a partition boundary (all members "
          "still mutually ≥0.70) → effectively fine, just drawn differently.",
          f"- **{len(loose)} of {avg['n_multi']}** are genuinely loose (weakest link < {CUT_R:.2f}) → "
          "**chain-effect grab-bags / average-linkage artifacts** that fragment under complete linkage.",
          f"- Of those grab-bags, **{len(danger_loose)}** mix positive-lead and negative members "
          "(🚨 **sign conflict**) — the dangerous case: averaging a lead with a negative relationship. "
          "The rest are sign-consistent (over-merged but directionally coherent, so conservative).", "",
          "Empirical stability notes (this dataset — complete linkage is *not* a strict refinement "
          "of average, so these are observed, not guaranteed):",
          f"- Singletons: {'identical set under both methods' if avg_singletons == com_singletons else f'differ — {len(avg_singletons - com_singletons)} average-only and {len(com_singletons - avg_singletons)} complete-only singletons'}.",
          f"- Complete linkage also forms {len(com_only)} multi-cluster(s) that are not average "
          "clusters (the two partitions cross-cut; complete is not a pure sub-division of average).", ""]

    with open(os.path.join(OUT, "linkage_compare.md"), "w") as fh:
        fh.write("\n".join(L))

    # ---- Console summary
    print(f"Linkage comparison ({len(ids)} signals, cut r>={CUT_R}):")
    print(f"  average : {avg['n_multi']} multi + {avg['n_single']} singletons = {avg['n_forces']} forces")
    print(f"  complete: {com['n_multi']} multi + {com['n_single']} singletons = {com['n_forces']} forces")
    print(f"  robust (identical member set both methods): {len(robust)} multi-clusters")
    print(f"  average-only: {len(avg_only)}  ({len(loose)} genuinely loose grab-bags, "
          f"{len(reassigned)} tight-but-reassigned)")
    print(f"  loose grab-bags with SIGN CONFLICT (pos lead + neg member): {len(danger_loose)}")
    for c in loose:
        pos, neg = sign_split(list(c), peak_r)
        tag = "🚨 SIGN CONFLICT" if (pos and neg) else "sign-consistent"
        print(f"    - size {len(c):>2}, tightness {avg['tight'][c]:+.2f}  [{tag}]  "
              + ", ".join(nm(m) for m in list(c)[:5]) + ("…" if len(c) > 5 else ""))
    print("  wrote outputs/linkage_compare.md")


if __name__ == "__main__":
    main()
