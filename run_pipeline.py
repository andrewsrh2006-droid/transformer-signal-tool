#!/usr/bin/env python3
"""End-to-end runner for the transformer leading-signal protocol.

Steps (Section 3 of the brief):
  1. Gather each series from FRED (cached + spot-checked).
  2. Process: level / YoY / 2nd-derivative; align each candidate with the outcome.
  3. Visualize before correlating (overview + per-pair charts).
  4. Correlate across lags [-24, +24].
  5. Robustness screen (2 gates + 2 supports).
  6. Significance (circular-shift permutation p; moving-block bootstrap CI).
  7. Conclude: verdicts, leaderboard, correlation-of-correlations matrix.

Outputs land in outputs/.
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.cluster.hierarchy import dendrogram

from signal_tool import config as CFG
from signal_tool import fred, process as P, correlate as C
from signal_tool import screen as SCR, significance as SIG
from signal_tool import matrix as MTX, leaderboard as LB
from signal_tool import cluster as CL, control as CTRL
from signal_tool import history as HIST
from signal_tool import leadlag as LL

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "outputs")
CHARTS = os.path.join(OUT, "charts")
DATA = os.path.join(ROOT, "data")


def ensure_dirs():
    for d in (OUT, CHARTS, DATA):
        os.makedirs(d, exist_ok=True)


def gather():
    print("[1] Gathering FRED series ...")
    data, meta = fred.load_all(CFG.ALL_SERIES, force=False)
    with open(os.path.join(DATA, "metadata.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    for m in meta:
        print(f"    {m['fred_id']:16s} {m['n_obs']:4d} obs  "
              f"{m['date_start']}..{m['date_end']}  | {m['label']}")
    return data, meta


def overview_chart(levels, cand_ids):
    """Visualize candidate YoY against the outcome YoY before correlating.

    With a large library the full grid is impractical; cap at 36 panels (the per-signal
    charts cover the rest)."""
    out_yoy = P.yoy(levels[CFG.OUTCOME.fred_id])
    cand_ids = cand_ids[:36]
    n = len(cand_ids)
    ncol, nrow = 3, int(np.ceil(n / 3))
    fig, axes = plt.subplots(nrow, ncol, figsize=(15, 3 * nrow), sharex=True)
    axes = axes.ravel()
    label_by_id = {c.fred_id: c.label for c in CFG.CANDIDATES}
    for ax, cid in zip(axes, cand_ids):
        cy = P.yoy(levels[cid])
        ax.plot(out_yoy.index, out_yoy.values, color="black", lw=1.0, label="Transformer YoY")
        ax.plot(cy.index, cy.values, color="tab:red", lw=0.9, alpha=0.8,
                label=label_by_id[cid])
        ax.axhline(0, color="gray", lw=0.5)
        ax.set_title(label_by_id[cid], fontsize=9)
        ax.tick_params(labelsize=7)
    for ax in axes[n:]:
        ax.set_visible(False)
    fig.suptitle("Candidate YoY (red) vs Transformer PPI YoY (black) — inspect before correlating",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(os.path.join(CHARTS, "_overview_yoy.png"), dpi=110)
    plt.close(fig)


def pair_chart(cid, label, levels, aligned_df, curve, peak):
    fig, axes = plt.subplots(1, 3, figsize=(15, 3.4))
    # Panel 1: levels (dual axis)
    ax = axes[0]
    lc = levels[cid]
    lo = levels[CFG.OUTCOME.fred_id]
    ax.plot(lo.index, lo.values, color="black", lw=1.0)
    ax.set_ylabel("Transformer PPI", color="black", fontsize=8)
    ax2 = ax.twinx()
    ax2.plot(lc.index, lc.values, color="tab:red", lw=1.0)
    ax2.set_ylabel(label, color="tab:red", fontsize=8)
    ax.set_title("Levels", fontsize=9)
    # Panel 2: YoY overlay
    ax = axes[1]
    ax.plot(aligned_df.index, aligned_df["outcome"], color="black", lw=1.0, label="Transformer YoY")
    ax.plot(aligned_df.index, aligned_df["cand"], color="tab:red", lw=1.0, label="Candidate YoY")
    ax.axhline(0, color="gray", lw=0.5)
    ax.legend(fontsize=7)
    ax.set_title("Year-over-year % change", fontsize=9)
    # Panel 3: lag-correlation curve
    ax = axes[2]
    ks = sorted(curve)
    rs = [curve[k][0] for k in ks]
    ax.plot(ks, rs, color="tab:blue", lw=1.2)
    ax.axhline(0, color="gray", lw=0.5)
    ax.axvline(0, color="gray", lw=0.5, ls=":")
    if peak:
        ax.plot([peak[0]], [peak[1]], "o", color="crimson")
        ax.annotate(f"peak r={peak[1]:.2f}\n@ +{peak[0]}m" if peak[0] >= 0
                    else f"peak r={peak[1]:.2f}\n@ {peak[0]}m",
                    (peak[0], peak[1]), fontsize=8,
                    textcoords="offset points", xytext=(6, -2))
    ax.set_xlabel("lag k (months); +k = candidate leads", fontsize=8)
    ax.set_ylabel("Pearson r", fontsize=8)
    ax.set_title("Lag correlation", fontsize=9)
    fig.suptitle(f"{label}  →  Transformer PPI", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(CHARTS, f"{cid}.png"), dpi=110)
    plt.close(fig)


def run_clustering(inter, cand_ids, label_by_id, method=None, suffix=""):
    """Hierarchical clustering: dendrogram PNG, clustered-heatmap PNG, clusters.json.

    method: "complete" (tight forces) or "average" (looser blocs that merge same-sign cousins);
    defaults to CFG.CLUSTER_LINKAGE. suffix distinguishes the loose-bloc outputs from the tight
    ones (e.g. clusters_loose.json, _dendrogram_loose.png)."""
    method = method or getattr(CFG, "CLUSTER_LINKAGE", "average")
    short = {i: label_by_id[i].split(" (")[0] for i in cand_ids}
    Z = CL.linkage_matrix(inter, method=method)
    clusters = CL.clusters_at(Z, cand_ids, CFG.CLUSTER_R)
    order = CL.leaf_order(Z, cand_ids)

    N = len(cand_ids)
    big = N > 40
    # Dendrogram — horizontal for many leaves so labels are readable.
    fig, ax = plt.subplots(figsize=(12, max(5, N * 0.16)) if big else (12, 5))
    dendrogram(Z, labels=[short[i] for i in cand_ids],
               color_threshold=1.0 - CFG.CLUSTER_R, above_threshold_color="#8c959f",
               orientation="left" if big else "top", ax=ax,
               leaf_font_size=5 if big else 8)
    line = ax.axvline if big else ax.axhline
    line(1.0 - CFG.CLUSTER_R, color="crimson", ls="--", lw=1.0,
         label=f"cut at r = {CFG.CLUSTER_R:.2f}")
    ax.set_title(f"Hierarchical clustering ({method} linkage, 1−r distance)", fontsize=10)
    ax.legend(loc="lower right", fontsize=8)
    if not big:
        plt.xticks(rotation=40, ha="right", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, f"_dendrogram{suffix}.png"), dpi=130)
    plt.close(fig)

    # Clustered heatmap (rows/cols reordered by dendrogram leaves) — no cell text if large.
    m = inter.loc[order, order]
    sz = 8 if not big else min(24, 0.11 * N)
    fig, ax = plt.subplots(figsize=(sz, sz))
    im = ax.imshow(m.values.astype(float), vmin=-1, vmax=1, cmap="RdBu_r")
    if not big:
        ax.set_xticks(range(len(order))); ax.set_yticks(range(len(order)))
        ax.set_xticklabels([short[i] for i in order], rotation=45, ha="right", fontsize=7)
        ax.set_yticklabels([short[i] for i in order], fontsize=7)
        for a in range(len(order)):
            for b in range(len(order)):
                v = m.values[a, b]
                ax.text(b, a, f"{v:.2f}", ha="center", va="center", fontsize=6,
                        color="white" if abs(v) > 0.6 else "black")
    else:
        ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(im, ax=ax, shrink=0.8, label="r")
    ax.set_title(f"Clustered correlation heatmap ({N} signals, leaf order)", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, f"_clustered_heatmap{suffix}.png"), dpi=130)
    plt.close(fig)

    payload = {"method": f"{method} linkage", "distance": "1 - r", "cut_r": CFG.CLUSTER_R,
               "leaf_order": order,
               "clusters": {str(k): [{"fred_id": c, "label": label_by_id[c]} for c in v]
                            for k, v in clusters.items()}}
    with open(os.path.join(OUT, f"clusters{suffix}.json"), "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"    dendrogram + clustered heatmap saved; {len(clusters)} clusters at r>={CFG.CLUSTER_R}")
    for k, v in clusters.items():
        print(f"      cluster {k}: " + ", ".join(short[c] for c in v))
    return clusters, order


def run_cycle_control(levels, board, label_by_id, mech_by_id):
    """Partial-correlation / relative-series test vs the broad commodity cycle."""
    market_id = CFG.MARKET.fred_id
    mkt_yoy = CTRL.market_index(levels, market_id)
    out_level = levels[CFG.OUTCOME.fred_id]
    rows = []
    confirmed = board[board["verdict"] == "CONFIRMED"]
    for _, r in confirmed.iterrows():
        cid = r["fred_id"]
        res = CTRL.cycle_control(levels[cid], out_level, mkt_yoy, int(r["measured_lead_months"]))
        rows.append({
            "signal": label_by_id[cid], "fred_id": cid,
            "lead_months": res["lead_k"], "raw_r": res["raw_r"],
            "partial_r_ctrl_market": res["partial_r"],
            "spread_r_both_decycled": res["spread_r"],
            "beta_signal": res["beta_signal"], "beta_outcome": res["beta_outcome"],
            "relative_series_r": res["relative_r"],
            "fraction_retained": res["fraction_retained"],
            "r_signal_market": res["r_signal_market"],
            "r_outcome_market": res["r_transformer_market"],
            "survival": res["survival"], "n": res["n"],
            "mechanism": mech_by_id[cid],
        })
    df = pd.DataFrame(rows).sort_values("partial_r_ctrl_market", ascending=False,
                                        key=lambda s: s.abs()).reset_index(drop=True)
    df.to_csv(os.path.join(OUT, "cycle_control.csv"), index=False)
    print(f"    cycle control on {len(df)} confirmed signals (market = {market_id})")
    for _, x in df.iterrows():
        print(f"      {x['signal']:30s} raw={x['raw_r']:+.2f} -> partial={x['partial_r_ctrl_market']:+.2f}"
              f"  rel={x['relative_series_r']:+.2f}  [{x['survival']}]")
    return df


_GROUP_THEME = {
    "copper": "non-ferrous metals", "aluminum": "non-ferrous metals", "wire": "non-ferrous metals",
    "nickel": "non-ferrous metals", "basemetal": "non-ferrous metals", "ppi_metals": "metals",
    "import": "import prices", "steel": "steel",
    "materials": "plastics & materials", "ppi_plastics_rubber": "plastics & materials",
    "ppi_chemicals": "chemicals", "energy": "energy", "ppi_fuels_power": "energy",
    "commodity": "energy/commodity", "freight": "freight", "mfg_price": "broad price",
    "downstream": "machinery", "ppi_machinery": "machinery",
    "ip": "industrial activity", "capacity": "industrial activity", "employment": "industrial activity",
    "orders": "orders/demand", "demand": "orders/demand", "inventories": "orders/demand",
    "construction": "construction", "rates": "rates", "credit": "credit",
    "expectations": "inflation expectations", "dollar": "dollar", "sentiment": "sentiment",
    "macro": "macro", "financial": "financial",
    "regionalfed_future": "regional-Fed survey", "regionalfed_current": "regional-Fed survey",
}


def _force_name(members, group_by_id, label_by_id):
    """Clean, descriptive name for a multi-signal force by dominant member theme."""
    from collections import Counter
    themes = Counter(_GROUP_THEME.get(group_by_id.get(m, "?"), "other") for m in members)
    top = themes.most_common(2)
    name = top[0][0]
    # If a metals cluster is really the non-ferrous complex plus generic metals, prefer that.
    keys = {t for t, _ in top}
    if keys <= {"metals", "non-ferrous metals", "import prices"} and "non-ferrous metals" in themes:
        name = "non-ferrous metals"
    elif len(top) > 1 and top[1][1] >= 0.4 * top[0][1] and top[1][0] != "other":
        name = f"{top[0][0]} & {top[1][0]}"
    return name[:1].upper() + name[1:] + " complex"


TIER_RANK = {"TIGHT": 0, "LOOSE/SAME-SIGN": 1, "LOOSE/OPPOSITE-SIGN": 2}
OPPOSITE_LABEL = "opposite-sign grab-bag → split"
LOOSE_LABEL = "loose same-sign → split"


def _split_tiers(must_be_tight=None):
    """Tiers that are split into tight sub-forces rather than scored as merged.

    must_be_tight=True (tight forces): split BOTH loose tiers (a force must be a tight cluster).
    must_be_tight=False (loose blocs): split only the incoherent opposite-sign grab-bags, so
    same-sign cousins stay MERGED into bigger, more independent blocs.
    None → fall back to the CFG.FORCES_MUST_BE_TIGHT global."""
    if must_be_tight is None:
        must_be_tight = getattr(CFG, "FORCES_MUST_BE_TIGHT", False)
    if must_be_tight:
        return {"LOOSE/OPPOSITE-SIGN", "LOOSE/SAME-SIGN"}
    return {"LOOSE/OPPOSITE-SIGN"}


def classify_force(members, inter, sign_by_id):
    """3-tier classification of a force from two metrics.

    METRIC 1 tightness   = the weakest pairwise correlation between any two members (a
                           singleton is trivially tight).
    METRIC 2 sign purity = the share of members whose peak correlation with transformer PPI
                           shares the MAJORITY sign (1.0 = unanimous).

    Tier rule:
      TIGHT               if tightness >= 0.70;
      else LOOSE/SAME-SIGN if sign purity == 1.0 (over-merged but directionally coherent);
      else LOOSE/OPPOSITE-SIGN (loose AND mixes positive-lead with negative members).
    """
    signs = [sign_by_id.get(m, 0.0) for m in members]
    n_pos = sum(1 for s in signs if s > 0)
    n_neg = sum(1 for s in signs if s < 0)
    size = len(members)
    purity = (max(n_pos, n_neg) / size) if size else 1.0
    if size < 2:
        tightness, tier = None, "TIGHT"
    else:
        vals = [inter.loc[a, b] for i, a in enumerate(members) for b in members[i + 1:]]
        tightness = float(np.nanmin(vals))
        if tightness >= CFG.CLUSTER_R:
            tier = "TIGHT"
        elif purity >= 1.0:
            tier = "LOOSE/SAME-SIGN"
        else:
            tier = "LOOSE/OPPOSITE-SIGN"
    return {"tier": tier, "size": size, "tightness": tightness, "sign_purity": round(purity, 4),
            "n_pos": n_pos, "n_neg": n_neg, "usable": tier != "LOOSE/OPPOSITE-SIGN"}


def run_force_tiers(hclusters, inter, sign_by_id, label_by_id, group_by_id, out_name="force_tiers.csv"):
    """Classify EVERY force (multi-cluster + singleton) into the 3 tiers; write
    force_tiers.csv and a console summary. Returns {cluster_key: tier_info}."""
    from collections import Counter
    rows, tier_by_key, counts = [], {}, Counter()
    for k, members in hclusters.items():
        info = classify_force(members, inter, sign_by_id)
        name = (_force_name(members, group_by_id, label_by_id) if len(members) > 1
                else label_by_id[members[0]])
        info["force"] = name
        tier_by_key[k] = info
        counts[info["tier"]] += 1
        rows.append({
            "force": name, "tier": info["tier"], "size": info["size"],
            "tightness_min_pairwise_r": "" if info["tightness"] is None else round(info["tightness"], 4),
            "sign_purity": info["sign_purity"],
            "n_pos": info["n_pos"], "n_neg": info["n_neg"],
            "usable": "yes" if info["usable"] else "no",
            "status": "usable" if info["usable"] else OPPOSITE_LABEL,
            "members": "; ".join(label_by_id[m].split(" (")[0] for m in members),
        })
    df = pd.DataFrame(rows)
    df["_r"] = df["tier"].map(TIER_RANK)
    df = df.sort_values(["_r", "size"], ascending=[True, False]).drop(columns="_r")
    df.to_csv(os.path.join(OUT, out_name), index=False)
    print("    force tiers: " + ", ".join(f"{t}={counts[t]}" for t in TIER_RANK))
    for r in rows:
        if r["tier"] == "LOOSE/OPPOSITE-SIGN":
            print(f"      EXCLUDED (opposite-sign grab-bag): {r['force']} "
                  f"(size {r['size']}, tightness {r['tightness_min_pairwise_r']}, "
                  f"+{r['n_pos']}/-{r['n_neg']})")
    return tier_by_key


def run_force_cycle_control(levels, hclusters, board, control_df, label_by_id, mech_by_id,
                            tier_by_key, must_be_tight=None, out_name="force_cycle_control.csv"):
    """Full test battery PER FORCE (cluster composite), not per signal.

    Each tight multi-member cluster is collapsed into an equal-weighted composite and given
    its OWN peak-lead search, both robustness gates, permutation p, bootstrap CI, market-
    control partial r and a verdict — with Benjamini-Hochberg FDR across the force family
    (more, smaller forces = more tests). Confirmed singletons pass through with their per-
    signal verdict. Loose forces (only when CLUSTER_LINKAGE='average') are routed to split.
    """
    group_by_id = {c.fred_id: c.group for c in CFG.CANDIDATES}
    # A force is worth testing if it contains a member that is a STRONG lead on the raw data —
    # i.e. CONFIRMED or STRONG-BUT-CYCLE-DRIVEN. Gating on CONFIRMED alone would couple force
    # *composition* to the cycle-fold (a force whose members are all cycle-driven would silently
    # vanish); the composite still gets its own cycle test and verdict below.
    confirmed_ids = set(board[board["verdict"].isin(
        ["CONFIRMED", LB.CYCLE_DRIVEN_VERDICT])]["fred_id"])
    verdict_by_id = dict(zip(board["fred_id"], board["verdict"]))
    mkt_yoy = CTRL.market_index(levels, CFG.MARKET.fred_id)
    out_level = levels[CFG.OUTCOME.fred_id]
    out_yoy = P.yoy(out_level)
    per_signal = {r["fred_id"]: r for _, r in control_df.iterrows()}
    board_by_id = {r["fred_id"]: r for _, r in board.iterrows()}

    split_tiers = _split_tiers(must_be_tight)
    excluded, scored_members = [], {}
    multi_pending, single_rows = [], []          # multi-forces tested; singletons pass-through
    for k, members in hclusters.items():
        info = tier_by_key[k]
        tier = info["tier"]
        name = (_force_name(members, group_by_id, label_by_id) if len(members) > 1
                else label_by_id[members[0]])

        # ---- SINGLETON force: a force of size 1 = one independent witness. List and score it
        # exactly like any other force, from its own per-signal measures — no confirmed gate,
        # so the leaderboard reflects EVERY independent witness, not just clustered ones.
        if len(members) == 1:
            mid = members[0]
            br = board_by_id.get(mid)
            if br is None:
                continue
            ps = per_signal.get(mid)
            lead = int(br["measured_lead_months"])
            single_rows.append({
                "force": name, "tier": tier, "origin": "primary", "type": "single signal",
                "n_signals": 1, "members": label_by_id[mid].split(" (")[0], "member_ids": mid,
                "lead_months": lead, "raw_r": round(float(br["peak_r"]), 4),
                "partial_r_ctrl_market": br["partial_r_ctrl_market"],
                "beta_signal": (ps["beta_signal"] if ps is not None else np.nan),
                "survival": br["survival_vs_cycle"],
                "leads": "yes" if lead >= 1 else "no",
                "smoothing_pass": br.get("smoothing_pass", ""),
                "holds_pass": br.get("holds_pass", ""),
                "is_comover": br.get("is_comover", ""),
                "lead_class": br.get("lead_class", ""),
                "verdict": br["verdict"], "status": "scored", "n": int(br["n"])})
            if mid in confirmed_ids:              # lead-bearing singleton is also a matrix/lead-lag node
                nm, _i = name, 2
                while nm in scored_members:
                    nm, _i = f"{name} ({_i})", _i + 1
                scored_members[nm] = [mid]
            continue

        # ---- MULTI-member cluster ----
        if tier in split_tiers:                  # loose (only under average linkage) → split
            excluded.append({
                "force": name, "tier": tier, "origin": "primary", "type": "cluster composite",
                "n_signals": len(members),
                "members": ", ".join(label_by_id[m].split(" (")[0] for m in members),
                "member_ids": ";".join(members),
                "lead_months": np.nan, "raw_r": np.nan, "partial_r_ctrl_market": np.nan,
                "beta_signal": np.nan, "verdict": "—",
                "survival": OPPOSITE_LABEL if tier == "LOOSE/OPPOSITE-SIGN" else LOOSE_LABEL,
                "status": "split → sub-forces", "n": np.nan})
            continue
        if not any(m in confirmed_ids for m in members):
            continue                             # a tight cluster of rejects is not a lead
        uname, _i = name, 2
        while uname in scored_members:
            uname, _i = f"{name} ({_i})", _i + 1
        scored_members[uname] = list(members)
        test = _test_composite(CTRL.composite_yoy([levels[m] for m in members]), out_yoy, mkt_yoy)
        multi_pending.append({"name": name, "tier": tier, "members": members, "test": test})

    # BH-FDR across the multi-force composite family (the tests forces add).
    tested = [m for m in multi_pending if m["test"] is not None]
    qmap = {}
    if tested:
        qs = SIG.benjamini_hochberg([m["test"]["perm"]["p_value"] for m in tested])
        qmap = {id(tested[i]): qs[i] for i in range(len(tested))}
    scored = list(single_rows)
    for m in multi_pending:
        t = m["test"]
        if t is None:
            continue
        q = qmap.get(id(m))
        v = LB.verdict(t["r"], t["lag"], t["gates"]["screen_pass"], q,
                       t["boot"]["excludes_zero"], is_comover=t["sharp"]["is_comover"],
                       lead_gain=t["sharp"]["lead_gain"])
        v = LB.apply_cycle_control(v, t["cc"]["partial_r"], t["r"])   # fold market control into the verdict
        scored.append({
            "force": m["name"], "tier": m["tier"], "origin": "primary", "type": "cluster composite",
            "n_signals": len(m["members"]),
            "members": ", ".join(label_by_id[x].split(" (")[0] for x in m["members"]),
            "member_ids": ";".join(m["members"]),
            "lead_months": t["lag"], "raw_r": round(t["r"], 4),
            "partial_r_ctrl_market": t["cc"]["partial_r"], "beta_signal": t["cc"]["beta_signal"],
            "survival": t["cc"]["survival"],
            "leads": "yes" if t["lag"] >= 1 else "no",
            "smoothing_pass": "yes" if t["gates"]["smoothing_gate"]["pass"] else "no",
            "holds_pass": "yes" if t["gates"]["holds_gate"]["pass"] else "no",
            "episode_pass": "yes" if t["gates"]["episode_gate"]["pass"] else "no",
            "is_comover": "yes" if t["sharp"]["is_comover"] else "no",
            "lead_class": t["sharp"].get("lead_class", ""),
            "verdict": v, "status": "scored", "n": t["n"]})

    sdf = pd.DataFrame(scored).sort_values("partial_r_ctrl_market", ascending=False,
                                           key=lambda s: s.abs()).reset_index(drop=True)
    df = pd.concat([sdf, pd.DataFrame(excluded)], ignore_index=True)
    df.to_csv(os.path.join(OUT, out_name), index=False)
    print(f"    per-force cycle control: {len(sdf)} tight force(s) scored as-is, "
          f"{len(excluded)} loose force(s) routed to split")
    for _, x in sdf.iterrows():
        print(f"      {x['force']:34s} ({x['n_signals']}x)  raw={x['raw_r']:+.2f}@{int(x['lead_months']):+d} -> "
              f"partial={x['partial_r_ctrl_market']:+.2f} [{x['survival']}]  => {x.get('verdict','')}")
    for x in excluded:
        print(f"      {x['force']:34s} ({x['n_signals']}x, {x['tier']})  -> split")
    return df, scored_members


def _test_composite(comp_yoy, out_yoy, mkt_yoy):
    """Run the FULL per-signal battery on a composite YoY index: peak-lead, both gates,
    permutation p, block-bootstrap CI, lead-sharpness, and the market-control partial r."""
    df = P.align(comp_yoy, out_yoy)
    if len(df) < 12:
        return None
    a, b = df["cand"].to_numpy(), df["outcome"].to_numpy()
    curve, peak = C.peak_lag_corr(a, b, CFG.MAX_LAG)
    if peak is None:
        return None
    lag, r, n = peak
    gates = SCR.run_gates(a, b, peak, CFG.MAX_LAG, index=df.index, smooth_win=CFG.SMOOTH_WIN,
                          r_min_screen=CFG.R_MIN_SCREEN)
    perm = SIG.permutation_pvalue(a, b, abs(r), CFG.MAX_LAG, n_surrogates=CFG.N_SURROGATES)
    boot = SIG.block_bootstrap_ci(a, b, lag, n_boot=CFG.N_BOOTSTRAP, block_len=CFG.BLOCK_LEN)
    sharp = C.lead_sharpness(curve, peak)
    cc = CTRL.cycle_control_yoy(comp_yoy, out_yoy, mkt_yoy, lag)
    return {"lag": lag, "r": r, "n": n, "gates": gates, "perm": perm, "boot": boot,
            "sharp": sharp, "cc": cc}


def run_force_splits(levels, hclusters, tier_by_key, inter, sign_by_id, label_by_id, group_by_id,
                     must_be_tight=None, out_name="force_splits.csv"):
    """Split rule: never discard a LOOSE/OPPOSITE-SIGN force. Re-cluster its members with
    COMPLETE linkage at 0.70 into tight sub-forces, then re-classify and re-test EACH sub-
    force independently (its own composite, gates, market control, significance).

    Multiple-comparisons discipline: splitting adds tests, so the sub-force permutation
    p-values are Benjamini-Hochberg-corrected as their own family; a sub-force is only
    credited as a genuine lead if it clears q < alpha (on top of the gates + CI).
    """
    out_level = levels[CFG.OUTCOME.fred_id]
    out_yoy = P.yoy(out_level)
    mkt_yoy = CTRL.market_index(levels, CFG.MARKET.fred_id)
    split_tiers = _split_tiers(must_be_tight)
    loose = [(k, hclusters[k]) for k in hclusters
             if tier_by_key[k]["tier"] in split_tiers and len(hclusters[k]) > 1]

    subs = []
    for k, members in loose:
        parent = tier_by_key[k]["force"]
        origin = ("split-from-opposite" if tier_by_key[k]["tier"] == "LOOSE/OPPOSITE-SIGN"
                  else "split-from-loose")
        subM = inter.loc[members, members]
        subZ = CL.linkage_matrix(subM, method="complete")          # tight sub-forces
        subclusters = CL.clusters_at(subZ, members, CFG.CLUSTER_R)
        for smembers in subclusters.values():
            info = classify_force(smembers, inter, sign_by_id)
            test = _test_composite(CTRL.composite_yoy([levels[m] for m in smembers]),
                                   out_yoy, mkt_yoy)
            subs.append({"parent": parent, "origin": origin, "members": smembers,
                         "info": info, "test": test})

    # BH-FDR across the split family (the tests splitting added).
    tested = [s for s in subs if s["test"] is not None]
    qmap = {}
    if tested:
        qs = SIG.benjamini_hochberg([s["test"]["perm"]["p_value"] for s in tested])
        qmap = {id(tested[i]): qs[i] for i in range(len(tested))}

    detail_rows, board_rows, confirm, sub_members = [], [], [], {}
    for s in subs:
        members, info, test = s["members"], s["info"], s["test"]
        name = (_force_name(members, group_by_id, label_by_id) if len(members) > 1
                else label_by_id[members[0]])
        if test is None:
            continue
        q = qmap.get(id(s))
        v = LB.verdict(test["r"], test["lag"], test["gates"]["screen_pass"], q,
                       test["boot"]["excludes_zero"], is_comover=test["sharp"]["is_comover"],
                       lead_gain=test["sharp"]["lead_gain"])
        v = LB.apply_cycle_control(v, test["cc"]["partial_r"], test["r"])   # fold market control into the verdict
        board_name = f"{name} ↳ (split of {s['parent'].split(' complex')[0]})"
        _bn, _i = board_name, 2
        while _bn in sub_members:
            _bn, _i = f"{board_name} [{_i}]", _i + 1
        board_name = _bn
        detail_rows.append({
            "parent_force": s["parent"], "sub_force": name, "origin": s["origin"],
            "n_signals": len(members), "tier": info["tier"],
            "tightness_min_pairwise_r": "" if info["tightness"] is None else round(info["tightness"], 4),
            "sign_purity": info["sign_purity"], "majority_sign": "+" if info["n_pos"] >= info["n_neg"] else "-",
            "lead_months": test["lag"], "peak_r": round(test["r"], 4),
            "r_lag0": test["sharp"]["r_lag0"], "lead_gain": test["sharp"]["lead_gain"],
            "is_comover": "yes" if test["sharp"]["is_comover"] else "no",
            "lead_class": test["sharp"].get("lead_class", ""),
            "partial_r_ctrl_market": test["cc"]["partial_r"], "survival": test["cc"]["survival"],
            "perm_p": round(test["perm"]["p_value"], 4), "perm_q_splitfamily": round(q, 4) if q is not None else None,
            "ci95_low": test["boot"]["ci_low"], "ci95_high": test["boot"]["ci_high"],
            "robust": "yes" if (test["gates"]["smoothing_gate"]["pass"] and test["gates"]["holds_gate"]["pass"]) else "no",
            "verdict": v, "members": "; ".join(label_by_id[m].split(" (")[0] for m in members),
        })
        # Rows to append to the force-level leaderboard (same schema).
        board_rows.append({
            "force": board_name,
            "tier": info["tier"], "origin": s["origin"], "type": "split sub-force",
            "n_signals": len(members),
            "members": "; ".join(label_by_id[m].split(" (")[0] for m in members),
            "lead_months": test["lag"], "raw_r": round(test["r"], 4),
            "partial_r_ctrl_market": test["cc"]["partial_r"], "beta_signal": test["cc"]["beta_signal"],
            "survival": test["cc"]["survival"], "status": v, "n": test["n"]})
        sub_members[board_name] = list(members)

    df = pd.DataFrame(detail_rows)
    if not df.empty:
        df = df.sort_values(["parent_force", "n_signals"], ascending=[True, False])
    df.to_csv(os.path.join(OUT, out_name), index=False)

    print(f"    split {len(loose)} loose force(s) into {len(detail_rows)} tight sub-force(s) "
          "(complete linkage @0.70), re-tested with BH-FDR across the split family:")
    for r in detail_rows:
        gl = "GENUINE LEAD" if r["verdict"] == "CONFIRMED" else r["verdict"]
        print(f"      [{r['parent_force'][:26]:26}] {r['sub_force'][:26]:26} "
              f"({r['n_signals']}x, {r['majority_sign']}) r={r['peak_r']:+.2f}@{r['lead_months']:+d} "
              f"q={r['perm_q_splitfamily']} partial={r['partial_r_ctrl_market']} -> {gl}")

    # Headline confirmation: the New-Orders sub-force of the industrial/orders bag.
    for r in detail_rows:
        if "orders" in r["sub_force"].lower() and r["majority_sign"] == "+":
            genuine = (r["verdict"] == "CONFIRMED")
            confirm.append(
                f"New-Orders sub-force ({r['n_signals']} signals) split from the industrial/orders "
                f"bag: r={r['peak_r']:+.2f} @ {r['lead_months']:+d}m, q={r['perm_q_splitfamily']}, "
                f"partial r={r['partial_r_ctrl_market']} ({r['survival']}) → "
                + ("GENUINE LEAD (survives as an independent CONFIRMED force)."
                   if genuine else f"verdict {r['verdict']} (does not clear as a genuine lead)."))
    for c in confirm:
        print("    >>> " + c)
    return board_rows, detail_rows, confirm, sub_members


SHORT_VERDICT = "SHORT-SAMPLE (unverified)"


def reconcile_short_sample(rows, clusters, levels, out_id):
    """Downgrade short-sample CONFIRMED signals that lack long corroboration or are a
    window artifact, and write the window-artifact diagnostic table.

    `rows` is mutated in place (verdict + short_note). Returns the check rows.
    """
    out_level = levels[out_id]
    bench_level = levels.get(HIST.BENCHMARK_ID)
    by_id = {r["fred_id"]: r for r in rows}
    is_long_by_id = {r["fred_id"]: (r["short_sample"] == "no") for r in rows}
    base_confirmed = {r["fred_id"] for r in rows if r["verdict"] == "CONFIRMED"}

    checks = []
    for r in rows:
        if r["short_sample"] != "yes":
            continue
        cid = r["fred_id"]
        window = {"start": pd.Timestamp(r["sample_start"]),
                  "end": P.yoy(levels[cid]).dropna().index[-1], "n": int(r["n"])}
        art = HIST.window_artifact_check(levels[cid], out_level, bench_level, window,
                                         r["peak_r"], CFG.MAX_LAG) if bench_level is not None else {}
        corrob = HIST.long_corroborators(cid, clusters, is_long_by_id, base_confirmed)
        corrob_labels = [by_id[c]["signal"] for c in corrob]

        # A short signal that is strong & correctly-directed (would-be CONFIRMED, or STRONG
        # but failing the screen) can't be trusted on a short sample. It is quarantined as
        # SHORT-SAMPLE unless a long series confirms the same force AND it isn't a window
        # artifact. (Weak/rejected/co-mover short signals are only flagged, not relabelled.)
        decision, base_v = "kept", r["verdict"]
        if base_v in ("CONFIRMED", "STRONG / NOT ROBUST"):
            if art.get("window_artifact"):
                r["verdict"] = SHORT_VERDICT
                decision = "downgraded: window artifact"
                r["short_note"] += " | window artifact: long benchmark matches over this window"
            elif not corrob:
                r["verdict"] = SHORT_VERDICT
                decision = "downgraded: no long corroboration"
                r["short_note"] += " | no long confirmed series measures the same force"
            else:
                decision = f"kept ({base_v}): corroborated by long series"
                r["short_note"] += " | corroborated by long: " + "; ".join(corrob_labels)
        checks.append({
            "signal": r["signal"], "fred_id": cid, "usable_n": r["n"],
            "sample_start": r["sample_start"], "lead_months": r["measured_lead_months"],
            "signal_r": art.get("signal_r"),
            "bench_r_same_window": art.get("bench_r_same_window"),
            "bench_r_full_history": art.get("bench_r_full_history"),
            "window_inflation": art.get("window_inflation"),
            "signal_beats_benchmark": art.get("signal_beats_benchmark"),
            "window_artifact": "yes" if art.get("window_artifact") else "no",
            "long_corroborators": "; ".join(corrob_labels) if corrob_labels else "(none)",
            "base_verdict": base_v, "final_verdict": r["verdict"], "decision": decision,
        })

    df = pd.DataFrame(checks)
    df.to_csv(os.path.join(OUT, "short_sample_check.csv"), index=False)
    print(f"    {len(checks)} short-sample signal(s); benchmark = {HIST.BENCHMARK_LABEL}")
    for c in checks:
        print(f"      {c['signal'][:30]:30} n={c['usable_n']} from {c['sample_start']}  "
              f"r={c['signal_r']} vs bench@window={c['bench_r_same_window']} "
              f"(full={c['bench_r_full_history']})  -> {c['decision']}")
    return checks


def run_force_correlation(force_members, levels, out_name="force_correlation_matrix.csv",
                          kind="force"):
    """Inter-GROUP correlation matrix: correlation between the YoY composites of every group
    on the leaderboard (tight forces, or loose blocs). Tighter grouping makes more, smaller
    groups that can still be 'cousins' (0.5-0.7 correlated); merging same-sign cousins into
    looser blocs lowers cross-correlation and yields fewer, more independent groups. Either way
    this matrix (plus the partial-r market control) is the real independence check."""
    if len(force_members) < 2:
        return None
    comps = {name: CTRL.composite_yoy([levels[m] for m in ids])
             for name, ids in force_members.items()}
    dfc = pd.DataFrame(comps)
    cm = dfc.corr(min_periods=24)
    cm.to_csv(os.path.join(OUT, out_name))
    names = list(cm.index)
    cousins, offdiag = [], []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            r = cm.loc[a, b]
            if pd.notna(r):
                offdiag.append(abs(float(r)))
                if 0.50 <= abs(r) < CFG.CLUSTER_R:
                    cousins.append((a, b, round(float(r), 3)))
    cousins.sort(key=lambda x: -abs(x[2]))
    mean_abs = round(float(np.mean(offdiag)), 4) if offdiag else None
    print(f"    inter-{kind} correlation matrix: {len(names)} {kind}s; mean |r|={mean_abs}; "
          f"{len(cousins)} 'cousin' pair(s) at 0.50<=|r|<0.70 (not independent bets)")
    for a, b, r in cousins[:6]:
        print(f"      cousins r={r:+.2f}: {a.split(' ↳')[0][:30]}  ~  {b.split(' ↳')[0][:30]}")
    return {"matrix": cm, "cousins": cousins, "n_forces": len(names), "mean_abs_r": mean_abs}


def main():
    ensure_dirs()
    data, meta = gather()
    levels = {cid: P.to_monthly(s) for cid, s in data.items()}
    out_id = CFG.OUTCOME.fred_id
    cand_ids = [c.fred_id for c in CFG.CANDIDATES]
    label_by_id = {c.fred_id: c.label for c in CFG.CANDIDATES}
    mech_by_id = {c.fred_id: c.mechanism for c in CFG.CANDIDATES}

    print("[2/3] Processing + overview visualization ...")
    overview_chart(levels, cand_ids)

    print("[3] Correlation-of-correlations matrix ...")
    inter = MTX.contemporaneous_yoy_matrix(levels, cand_ids)
    clusters = MTX.find_clusters(inter, CFG.CLUSTER_R)
    # Clusters over ALL signals (production linkage) — used for short-sample corroboration,
    # where a short signal must be able to find its long same-force cluster-mates.
    _method = getattr(CFG, "CLUSTER_LINKAGE", "average")
    _Z = CL.linkage_matrix(inter, method=_method)
    hcluster_lists = list(CL.clusters_at(_Z, cand_ids, CFG.CLUSTER_R).values())
    inter.to_csv(os.path.join(OUT, "leading_signal_corr_matrix.csv"))

    print("[4-6] Per-pair correlation, screen, significance ...")
    out_yoy = P.yoy(levels[out_id])
    peaks, aligned_cache, curve_cache = {}, {}, {}
    for cid in cand_ids:
        df = P.align(P.yoy(levels[cid]), out_yoy)
        aligned_cache[cid] = df
        cand_arr = df["cand"].to_numpy()
        out_arr = df["outcome"].to_numpy()
        curve, peak = C.peak_lag_corr(cand_arr, out_arr, CFG.MAX_LAG)
        curve_cache[cid] = curve
        peaks[cid] = peak

    # ---- Fix 1: force-eligible signals = aligned overlap with the outcome >= FORCE_MIN_MONTHS.
    # Short-sample signals (already individually quarantined) are excluded from force
    # formation entirely, so one short member cannot truncate a whole composite's window.
    force_min = getattr(CFG, "FORCE_MIN_MONTHS", 150)
    eligible_ids = [cid for cid in cand_ids if len(aligned_cache[cid]) >= force_min]
    dropped_short = [cid for cid in cand_ids if cid not in eligible_ids]
    print(f"    force-eligible: {len(eligible_ids)}/{len(cand_ids)} signals "
          f"(overlap >= {force_min} mo); excluded from forces: "
          + (", ".join(label_by_id[c].split(' (')[0] for c in dropped_short) or "none"))
    inter_force = inter.loc[eligible_ids, eligible_ids]

    # ---- Pass 1: per-signal measures (no verdict yet — FDR needs all p-values first).
    stats = []
    for cid in cand_ids:
        peak = peaks[cid]
        if peak is None:
            continue
        df = aligned_cache[cid]
        cand_arr = df["cand"].to_numpy()
        out_arr = df["outcome"].to_numpy()
        curve = curve_cache[cid]
        peak_lag, peak_r, peak_n = peak

        gates = SCR.run_gates(cand_arr, out_arr, peak, CFG.MAX_LAG, index=df.index,
                              smooth_win=CFG.SMOOTH_WIN, r_min_screen=CFG.R_MIN_SCREEN)
        perm = SIG.permutation_pvalue(cand_arr, out_arr, abs(peak_r), CFG.MAX_LAG,
                                      n_surrogates=CFG.N_SURROGATES)
        boot = SIG.block_bootstrap_ci(cand_arr, out_arr, peak_lag,
                                      n_boot=CFG.N_BOOTSTRAP, block_len=CFG.BLOCK_LEN)
        support = SCR.second_opinion(cid, peaks, inter, CFG.CLUSTER_R, CFG.R_MIN_SCREEN)
        sharp = C.lead_sharpness(curve, peak)     # guardrail 2: lead vs co-mover
        pair_chart(cid, label_by_id[cid], levels, df, curve, peak)
        stats.append(dict(cid=cid, peak_lag=peak_lag, peak_r=peak_r, peak_n=peak_n,
                          gates=gates, perm=perm, boot=boot, support=support,
                          sharp=sharp, curve=curve, df=df))

    # ---- Guardrail 1: Benjamini-Hochberg FDR across ALL signals.
    pvals = [s["perm"]["p_value"] for s in stats]
    qvals = SIG.benjamini_hochberg(pvals)
    for s, q in zip(stats, qvals):
        s["q"] = q

    # ---- Pass 2: verdicts (FDR-controlled) + rows/details.
    mkt_yoy = CTRL.market_index(levels, CFG.MARKET.fred_id)   # broad-cycle control, once
    out_level = levels[out_id]
    rows, details = [], {}
    for s in stats:
        cid = s["cid"]; peak_lag = s["peak_lag"]; peak_r = s["peak_r"]
        gates = s["gates"]; perm = s["perm"]; boot = s["boot"]; sharp = s["sharp"]
        v = LB.verdict(peak_r, peak_lag, gates["screen_pass"], s["q"],
                       boot["excludes_zero"], is_comover=sharp["is_comover"],
                       lead_gain=sharp["lead_gain"])
        cc = CTRL.cycle_control(levels[cid], out_level, mkt_yoy, peak_lag)  # partial r vs cycle
        # Fold the cycle control into the verdict: a CONFIRMED signal is downgraded to STRONG
        # BUT CYCLE-DRIVEN only if it is genuinely cycle-driven (weak partial AND a real
        # raw→partial drop), not merely weak on its own. Applied before short-sample reconcile.
        v = LB.apply_cycle_control(v, cc["partial_r"], peak_r)
        win = HIST.sample_window(s["df"])                     # usable overlap w/ outcome
        short, short_reason = HIST.is_short(win["start"], win["n"])
        rows.append({
            "signal": label_by_id[cid], "fred_id": cid, "verdict": v,
            "measured_lead_months": peak_lag, "peak_r": round(peak_r, 4),
            "r_lag0": sharp["r_lag0"], "lead_gain": sharp["lead_gain"],
            "is_comover": "yes" if sharp["is_comover"] else "no",
            "lead_class": sharp.get("lead_class", ""),
            "ci95_low": boot["ci_low"], "ci95_high": boot["ci_high"],
            "perm_p": round(perm["p_value"], 4) if perm["p_value"] == perm["p_value"] else None,
            "perm_q": round(s["q"], 4),
            "robust": "yes" if (gates["smoothing_gate"]["pass"] and gates["holds_gate"]["pass"]
                                and gates["episode_gate"]["pass"]) else "no",
            "smoothing_pass": "yes" if gates["smoothing_gate"]["pass"] else "no",
            "holds_pass": "yes" if gates["holds_gate"]["pass"] else "no",
            "episode_pass": "yes" if gates["episode_gate"]["pass"] else "no",
            "episode_worst_r": gates["episode_gate"]["worst_r"],
            "episode_worst_block": gates["episode_gate"]["worst_block"],
            "n": s["peak_n"], "corroborators": s["support"]["n_corroborators"],
            "category": next((c.group for c in CFG.CANDIDATES if c.fred_id == cid), ""),
            "starter": "starter" if any(c.fred_id == cid and c.starter for c in CFG.CANDIDATES) else "added",
            "sample_start": win["start"].date().isoformat(),
            "short_sample": "yes" if short else "no", "short_note": short_reason,
            "partial_r_ctrl_market": cc["partial_r"], "survival_vs_cycle": cc["survival"],
        })
        details[cid] = {
            "label": label_by_id[cid], "mechanism": mech_by_id[cid],
            "peak": {"lag": peak_lag, "r": round(peak_r, 4), "n": s["peak_n"]},
            "lead_sharpness": sharp, "gates": gates,
            "permutation": {k: (round(v_, 4) if isinstance(v_, float) else v_)
                            for k, v_ in perm.items()},
            "perm_q": round(s["q"], 4), "bootstrap_ci": boot,
            "support": s["support"], "verdict": v,
            "partial_r_ctrl_market": cc["partial_r"], "survival_vs_cycle": cc["survival"],
            "r_signal_market": cc["r_signal_market"], "r_outcome_market": cc["r_transformer_market"],
            "sample_start": win["start"].date().isoformat(),
            "short_sample": "yes" if short else "no", "short_note": short_reason,
            "lag_curve": {str(k): round(s["curve"][k][0], 4) for k in sorted(s["curve"])},
        }
        print(f"    {label_by_id[cid]:34s} r={peak_r:+.2f} @ {peak_lag:+d}m  "
              f"q={s['q']:.3f}  {'CO-MOVER' if sharp['is_comover'] else 'lead'}  -> {v}")

    # ---- Guardrail 4: minimum-history. Short-sample signals cannot be CONFIRMED unless a
    # long (pre-2010) co-member of their cluster confirms the same force AND they are not a
    # pure window artifact (a generic long metal already scores the same over their window).
    print("[6b] Minimum-history guardrail (short-sample + window-artifact) ...")
    short_checks = reconcile_short_sample(rows, hcluster_lists, levels, out_id)
    # Propagate any downgraded verdicts into the per-signal details (pair_details.json /
    # the dashboard's Signal-detail tab) so every view agrees with the leaderboard.
    for r in rows:
        if r["fred_id"] in details:
            details[r["fred_id"]]["verdict"] = r["verdict"]
            details[r["fred_id"]]["short_sample"] = r["short_sample"]
            details[r["fred_id"]]["short_note"] = r["short_note"]

    print("[7] Leaderboard + writing outputs ...")
    board = LB.build_table(rows)
    board.to_csv(os.path.join(OUT, "leaderboard.csv"), index=False)
    with open(os.path.join(OUT, "pair_details.json"), "w") as fh:
        json.dump(details, fh, indent=2, default=str)

    write_markdown(board, inter, clusters, label_by_id)

    print(f"[8] Hierarchical clustering ({_method} linkage, force-eligible signals) ...")
    hclusters, order = run_clustering(inter_force, eligible_ids, label_by_id)

    print("[9] Broad-commodity-cycle control ...")
    control_df = run_cycle_control(levels, board, label_by_id, mech_by_id)

    print("[10] Force tier classification (TIGHT / LOOSE-SAME / LOOSE-OPPOSITE) ...")
    sign_by_id = {cid: float(np.sign(pk[1])) for cid, pk in peaks.items() if pk is not None}
    group_by_id = {c.fred_id: c.group for c in CFG.CANDIDATES}
    tier_by_key = run_force_tiers(hclusters, inter, sign_by_id, label_by_id, group_by_id)

    print("[11] Per-force cycle control — tight forces scored as-is ...")
    force_df, scored_members = run_force_cycle_control(levels, hclusters, board, control_df,
                                                       label_by_id, mech_by_id, tier_by_key)

    print("[12] Split loose forces (complete linkage) → re-test tight sub-forces ...")
    split_board, split_detail, split_confirm, sub_members = run_force_splits(
        levels, hclusters, tier_by_key, inter, sign_by_id, label_by_id, group_by_id)
    if split_board:
        force_df = pd.concat([force_df, pd.DataFrame(split_board)], ignore_index=True)
        force_df.to_csv(os.path.join(OUT, "force_cycle_control.csv"), index=False)

    print("[13] Inter-force correlation matrix (cousin check) ...")
    force_corr = run_force_correlation({**scored_members, **sub_members}, levels, kind="force")

    # ---- Third grouping rung: LOOSE BLOCS. Same machinery, tight=False — average linkage
    # merges same-sign cousins into bigger blocs (opposite-sign grab-bags still split). Fewer,
    # coarser, MORE INDEPENDENT groups; lower cross-correlation than the tight forces.
    print("[13b] Loose independent blocs (average linkage, merge same-sign cousins) ...")
    bloc_clusters, bloc_order = run_clustering(inter_force, eligible_ids, label_by_id,
                                               method="average", suffix="_loose")
    bloc_tiers = run_force_tiers(bloc_clusters, inter, sign_by_id, label_by_id, group_by_id,
                                 out_name="bloc_tiers.csv")
    # Same-sign cousins merge into bigger blocs; opposite-sign grab-bags are NOT merged (they're
    # excluded as incoherent, not averaged). The coarse coherent blocs (bloc_members) ARE the
    # loose grouping — we don't re-fragment the grab-bags back into the bloc set, which is what
    # would otherwise inflate the count above the tight level.
    bloc_df, bloc_members = run_force_cycle_control(
        levels, bloc_clusters, board, control_df, label_by_id, mech_by_id, bloc_tiers,
        must_be_tight=False, out_name="loose_bloc_cycle_control.csv")
    bloc_corr = run_force_correlation(bloc_members, levels,
                                      out_name="bloc_correlation_matrix.csv", kind="bloc")

    # Grouping ladder stats: signals → tight forces → loose blocs.
    ladder = {
        "signal": {"n_groups": len(eligible_ids), "mean_abs_r": None, "n_cousins": None},
        "tight": {"n_groups": (force_corr or {}).get("n_forces"),
                  "mean_abs_r": (force_corr or {}).get("mean_abs_r"),
                  "n_cousins": len((force_corr or {}).get("cousins", []))},
        "loose": {"n_groups": (bloc_corr or {}).get("n_forces"),
                  "mean_abs_r": (bloc_corr or {}).get("mean_abs_r"),
                  "n_cousins": len((bloc_corr or {}).get("cousins", []))},
    }
    with open(os.path.join(OUT, "grouping_ladder.json"), "w") as fh:
        json.dump(ladder, fh, indent=2)
    print(f"    ladder — tight: {ladder['tight']['n_groups']} forces, mean|r|="
          f"{ladder['tight']['mean_abs_r']}, {ladder['tight']['n_cousins']} cousins  |  "
          f"loose: {ladder['loose']['n_groups']} blocs, mean|r|={ladder['loose']['mean_abs_r']}, "
          f"{ladder['loose']['n_cousins']} cousins")

    print("[14] Lead-lag propagation map (item→item, read-only diagnostic) ...")
    run_lead_lag_map(levels, board, {**scored_members, **sub_members}, label_by_id, out_id,
                     bloc_members=bloc_members)

    write_analysis_markdown(inter, hclusters, order, control_df, label_by_id, force_df,
                            short_checks, split_detail, split_confirm, force_corr)
    print("Done. See outputs/leaderboard.md and outputs/analysis.md")
    return board, inter, clusters


def run_lead_lag_map(levels, board, force_members, label_by_id, out_id, bloc_members=None):
    """Directed item→item genuine-lead edges at signal, tight-force AND loose-bloc level
    (read-only diagnostic).

    Signal level: every candidate signal + the transformer PPI as nodes.
    Force level:  each scored tight-force composite + the transformer PPI.
    Bloc level:   each loose-bloc composite + the transformer PPI.
    Writes lead_lag_edges.csv, lead_lag_edges_force.csv, lead_lag_edges_bloc.csv."""
    tname = "Transformer PPI"
    # -- signal level: candidates + transformer
    node_ids = [c for c in board["fred_id"] if c in levels] + [out_id]
    yoy_by_id = {cid: P.yoy(levels[cid]) for cid in node_ids}
    labels = {cid: label_by_id.get(cid, cid) for cid in node_ids}
    labels[out_id] = tname
    sig = LL.edges(yoy_by_id, node_ids, labels, max_lag=CFG.MAX_LAG,
                   r_min=CFG.R_STRONG, min_gain=0.05)
    sig.to_csv(os.path.join(OUT, "lead_lag_edges.csv"), index=False)

    def _group_edges(members_by_name, out_name):
        nodes, glabels = {}, {}
        for name, members in members_by_name.items():
            nodes[name] = CTRL.composite_yoy([levels[m] for m in members])
            glabels[name] = name
        nodes[out_id] = P.yoy(levels[out_id])
        glabels[out_id] = tname
        e = LL.edges(nodes, list(nodes.keys()), glabels, max_lag=CFG.MAX_LAG,
                     r_min=CFG.R_STRONG, min_gain=0.05)
        e.to_csv(os.path.join(OUT, out_name), index=False)
        return e

    frc = _group_edges(force_members, "lead_lag_edges_force.csv")
    if bloc_members:
        _group_edges(bloc_members, "lead_lag_edges_bloc.csv")

    into = sig[sig["target_id"] == out_id]
    outof = sig[sig["source_id"] == out_id]
    sink = " (pure SINK ✓)" if (len(outof) == 0 and len(into) > 0) else ""
    print(f"      signal edges: {len(sig)} | transformer led-by {len(into)}, leads {len(outof)}{sink}")
    for _, e in into.sort_values("r", key=lambda s: s.abs(), ascending=False).head(6).iterrows():
        print(f"        {e['source'][:34]:34} → transformer  r={e['r']:+.2f} @ +{int(e['lag'])}m")
    return sig, frc


def write_analysis_markdown(inter, hclusters, order, control_df, label_by_id, force_df=None,
                            short_checks=None, split_detail=None, split_confirm=None,
                            force_corr=None):
    short = {i: label_by_id[i].split(" (")[0] for i in inter.index}
    L = ["# Analysis — signal groupings & commodity-cycle control", "",
         "## 1. Hierarchical clustering of the leading signals", "",
         "Average linkage on `d = 1 − r` (contemporaneous YoY). Cutting the tree at "
         f"**r = {CFG.CLUSTER_R:.2f}** (distance {1 - CFG.CLUSTER_R:.2f}) gives these groups:", "",
         "![dendrogram](charts/_dendrogram.png)", "",
         "![clustered heatmap](charts/_clustered_heatmap.png)", ""]
    multi = {k: v for k, v in hclusters.items() if len(v) > 1}
    n_single = sum(1 for v in hclusters.values() if len(v) == 1)
    n_forces = len(multi) + n_single
    L.append(f"**{len(hclusters)} signals → {n_forces} independent forces** "
             f"({len(multi)} multi-signal clusters + {n_single} singletons).")
    L.append("")
    L.append("Multi-signal clusters (each = ONE witness):")
    for k, members in multi.items():
        L.append(f"- **Cluster {k}** ({len(members)} signals): "
                 + ", ".join(label_by_id[m] for m in members))
    if n_single:
        L.append(f"- …plus {n_single} singletons (each its own independent force).")
    L += ["",
          "*How to read it:* signals that merge **below** the red line are ≥0.70 correlated — "
          "the same underlying price force. Count each such cluster as ONE independent witness, "
          "not as many. Average linkage (not single linkage) is used so a loose pair can't be "
          "chained together through a bridging third signal.", "",
          "## 2. Does each confirmed signal survive the broad commodity cycle?", "",
          f"Market control = **{CFG.MARKET.label}** (`{CFG.MARKET.fred_id}`). For each confirmed "
          "signal, at its measured lead: **raw** lead-r and the **partial** r holding the market "
          "constant. Survival is decided on the **partial r alone** — the correct measure of "
          "predictive power beyond the cycle. `retained` = partial / raw.", "",
          "| Signal | Lead | β (signal) | Raw r | Partial r (∣mkt) | Retained | Survival | Mechanism |",
          "|--------|------|-----------|-------|------------------|----------|----------|-----------|"]
    for _, r in control_df.iterrows():
        L.append(f"| {r['signal']} | {r['lead_months']:+d} | {r['beta_signal']:.1f} | "
                 f"{r['raw_r']:+.2f} | {r['partial_r_ctrl_market']:+.2f} | "
                 f"{r['fraction_retained']:.0%} | **{r['survival']}** | {r['mechanism'][:70]}… |")
    L += ["",
          "*How to read it:* **raw r** is the headline lead correlation. **Partial r** removes "
          "the part of the co-movement that is really just the whole commodity complex rising "
          "and falling together; what's left is the signal's own, transformer-specific "
          "information — and that is what the **survival** verdict is based on. If the partial r "
          "stays strong (**survives**), the signal is genuinely informative beyond the cycle; if "
          "it collapses toward zero (**cycle-driven**), the signal was mostly riding the general "
          "boom/bust and adds little unique lead.", "",
          "> The naive **relative** (signal − market) series is reported in `cycle_control.csv` "
          "as a diagnostic only, **not** used for the verdict. It assumes the signal moves "
          "1-for-1 with the market, so for a high-volatility signal like WTI crude (≈7× the "
          "index's volatility) subtracting the index barely changes it — the relative series is "
          "~0.99 correlated with raw crude, so its ‘0.54’ just re-measures crude and overstates "
          "survival. The partial correlation weights the market correctly and is the measure to "
          "trust (crude: raw 0.59 → partial 0.15 → cycle-driven).", "",
          "### 2b. The observable de-cycled spread (and why we de-cycle transformers too)", "",
          "`beta` = how many %-points a series moves per 1 %-point of the market. Subtracting "
          "`beta × market` removes a series' cycle exposure *correctly*, whatever its "
          "volatility (unlike the naive 1-for-1 relative series). We build two observable, "
          "plottable spreads:", "",
          "- **signal spread** = signal_YoY − β_signal × market_YoY", "",
          "- **transformer spread** = transformer_YoY − β_transformer × market_YoY", "",
          "**Should we de-cycle the transformer too? Yes** — transformer prices themselves ride "
          "the commodity cycle (they correlate ~0.71 with the broad index), so a fair test "
          "removes the cycle from *both* sides. And here is the key identity: **the correlation "
          "of the two de-cycled spreads equals the partial correlation exactly.** That is what a "
          "partial correlation *is* — the correlation of both variables after the common factor "
          "is regressed out of each. So `spread_r_both_decycled` == `partial_r` in the CSV (a "
          "numeric check, not a coincidence). De-cycling only the signal (leaving the "
          "transformer raw) gives the smaller *semi-partial* correlation and understates the "
          "true relationship.", "",
          "*Why it matters:* the partial r is one number you can't watch month to month; the "
          "de-cycled **spread is a real series** you can chart, alert on, or trade — e.g. a live "
          "‘steel-cost excess over the commodity complex’ indicator — while carrying the same, "
          "correct, cycle-stripped information as the partial correlation.", ""]

    if force_df is not None:
        prim = force_df[force_df.get("origin") == "primary"] if "origin" in force_df else force_df
        n_scored = int((prim.get("status") == "scored").sum()) if "status" in prim else len(prim)
        n_excl = int(prim["partial_r_ctrl_market"].isna().sum())
        method = getattr(CFG, "CLUSTER_LINKAGE", "average")
        L += ["### 2c. Per-force test (full battery per cluster, not per signal)", "",
              "A cluster of ≥0.70-correlated signals is **one witness**, so testing every member "
              "separately over-counts the evidence (pseudo-replication). Each multi-signal force is "
              "collapsed into an **equal-weighted composite YoY index** and given its OWN peak-lead "
              "search, both robustness gates, market-control partial r, permutation p, bootstrap CI "
              "and a **verdict** — with Benjamini-Hochberg FDR across the force family. Singletons "
              "carry their per-signal verdict.", "",
              f"**Production clustering: `{method}` linkage** — every cluster is **tight by "
              "construction** (every pair ≥0.70), so no loose grab-bag forms and the split machinery "
              "(§2d) is a no-op fallback. **Short-sample signals (overlap < "
              f"{getattr(CFG, 'FORCE_MIN_MONTHS', 150)} months) are excluded from force formation** "
              "so one short member cannot truncate a whole composite's decades-long window.", "",
              f"**{n_scored} tight force(s) scored" + (f" · {n_excl} routed to split." if n_excl else "."), "",
              "| Force | Tier | # | Lead | Raw r | Partial r (∣mkt) | Survival | Verdict |",
              "|-------|------|---|------|-------|------------------|----------|---------|"]
        for _, r in force_df.iterrows():
            if pd.isna(r["partial_r_ctrl_market"]):
                L.append(f"| ~~{r['force']}~~ | **{r['tier']}** | {int(r['n_signals'])} | "
                         f"— | — | — | ↳ split → §2d | — |")
            else:
                L.append(f"| **{r['force']}** | {r['tier']} | {int(r['n_signals'])} | "
                         f"{int(r['lead_months']):+d} | {r['raw_r']:+.2f} | "
                         f"{r['partial_r_ctrl_market']:+.2f} | {r['survival']} | **{r.get('verdict','')}** |")
        L += ["",
              "*How to read it:* every row is a **tight** force or a singleton. The **Verdict** is "
              "the composite's own CONFIRMED / co-mover / partial / reversed / rejected call; "
              "**Survival** is whether its partial r beats the broad commodity cycle. A force that "
              "is CONFIRMED *and* survives is a genuine, transformer-specific, independent lead. "
              "§2e then checks whether the (now more numerous, smaller) forces are really "
              "independent or merely cousins.", ""]

    if split_detail:
        L += ["### 2d. Auto-split of opposite-sign forces (never discard — re-cluster & re-test)", "",
              "A LOOSE/OPPOSITE-SIGN force is not thrown away. Its members are re-clustered with "
              "**complete linkage at r ≥ 0.70** into tight sub-forces, and **each sub-force is re-"
              "tested independently** — its own composite, peak-lead search, both robustness gates, "
              "market-control partial r, permutation p and bootstrap CI. Because splitting adds "
              "tests, the sub-force permutation p-values are **Benjamini-Hochberg-corrected as their "
              "own family** (`perm_q_splitfamily`); a sub-force is credited as a genuine lead only if "
              "it clears q < 0.05 *and* the gates *and* a non-zero CI. `origin = split-from-opposite`.", "",
              "| Parent grab-bag | Sub-force | Maj. sign | # | Tier | Lead | Peak r | Partial r | q (split) | Verdict |",
              "|-----------------|-----------|-----------|---|------|------|--------|-----------|-----------|---------|"]
        for r in split_detail:
            pr = "—" if r["partial_r_ctrl_market"] is None else f"{r['partial_r_ctrl_market']:+.2f}"
            L.append(f"| {r['parent_force']} | {r['sub_force']} | {r['majority_sign']} | "
                     f"{r['n_signals']} | {r['tier']} | {r['lead_months']:+d} | {r['peak_r']:+.2f} | "
                     f"{pr} | {r['perm_q_splitfamily']} | **{r['verdict']}** |")
        if split_confirm:
            L += [""] + [f"> **Confirmation.** {c}" for c in split_confirm]
        L += ["",
              "*How to read it:* the grab-bag is resolved into the sub-forces it was hiding. The "
              "positive **New-Orders** sub-force and the negative **IP/capacity** sub-groups are now "
              "separate, sign-coherent forces, each judged on its own merits — so a real forward "
              "lead buried in the bag is recovered, and the reversed relationships are kept distinct "
              "instead of being averaged into (and cancelling) it.", ""]

    if force_corr is not None:
        cous = force_corr["cousins"]
        L += ["### 2e. Force count is NOT a count of independent bets — the cousin check", "",
              "With `FORCES_MUST_BE_TIGHT`, every leaderboard force is a **tight cluster** (all "
              "members ≥0.70 with each other) or a singleton. But tighter clustering makes **more, "
              "smaller** forces that can still be **cousins** — correlate 0.5-0.7 with each other "
              "(just under the cut). So the force *count* overstates independence. The real "
              "independence checks are (a) this **inter-force correlation matrix** "
              "(`force_correlation_matrix.csv`), and (b) the **partial-r market control**, which "
              "strips the shared commodity cycle — the main reason cousins co-move.", "",
              f"**{force_corr['n_forces']} leaderboard forces; {len(cous)} cousin pair(s) at "
              f"0.50 ≤ |r| < 0.70.**"]
        if cous:
            L.append("")
            L.append("| Force A | Force B | r |")
            L.append("|---------|---------|---|")
            for a, b, r in cous[:12]:
                L.append(f"| {a.split(' ↳')[0]} | {b.split(' ↳')[0]} | {r:+.2f} |")
        L += ["",
              "*How to read it:* treat clusters of cousins as **one bet, not several**. E.g. a "
              "copper core and a steel core may each be a tight force yet still be cousins through "
              "the metals cycle; the partial-r control is what tells you whether each adds "
              "transformer-specific information beyond that shared cycle.", ""]

    if short_checks:
        n_down = sum(1 for c in short_checks if c["final_verdict"] == SHORT_VERDICT)
        L += ["## 3. Minimum-history guardrail (short-sample / window-artifact)", "",
              f"Signals whose usable overlap with the outcome is short (**n < {HIST.MIN_MONTHS} "
              f"months** or a sample starting after **{HIST.LATE_START.date()}**) can post a huge "
              "lead-correlation that is really just the 2020-22 commodity supercycle filling their "
              "whole sample. Such a signal is **excluded from CONFIRMED** unless a long, "
              "independent series measuring the same force (a pre-2010 confirmed co-member of its "
              "≥0.70 cluster) corroborates it — **and** it is not a window artifact.", "",
              f"**Window-artifact check.** For each short signal we re-measure a long benchmark "
              f"(**{HIST.BENCHMARK_LABEL}**) *restricted to the short signal's own window*. If that "
              "generic long metal already scores about the same correlation over the window, the "
              "signal's edge is the window, not the signal. `bench full` is the same benchmark over "
              "its entire 1967-start history; `inflation` = window − full shows how much that "
              "particular window puffs up any metal.", "",
              f"**{len(short_checks)} short-sample signal(s); {n_down} downgraded out of CONFIRMED.**", "",
              "| Signal | n | Start | Lead | Signal r | Bench r (same window) | Bench r (full) | Inflation | Artifact? | Long corroborator | Verdict |",
              "|--------|---|-------|------|----------|-----------------------|----------------|-----------|-----------|-------------------|---------|"]
        for c in short_checks:
            L.append(f"| {c['signal']} | {c['usable_n']} | {c['sample_start']} | "
                     f"{c['lead_months']:+d} | {c['signal_r']} | {c['bench_r_same_window']} | "
                     f"{c['bench_r_full_history']} | {c['window_inflation']} | "
                     f"**{c['window_artifact']}** | {c['long_corroborators']} | "
                     f"**{c['final_verdict']}** |")
        L += ["",
              "*How to read it:* if **Signal r ≈ Bench r (same window)** and the benchmark's "
              "window value is far above its full-history value (**Inflation** large and positive), "
              "the short signal has demonstrated nothing a generic long metal doesn't already show "
              "over the same months — its lead is a **window artifact**. The underlying force may "
              "still be real (that is what the long corroborator establishes), but *this particular "
              "short series* is not independent evidence of it and is not counted as a CONFIRMED "
              "lead.", ""]

    with open(os.path.join(OUT, "analysis.md"), "w") as fh:
        fh.write("\n".join(L))


def _fmt_ci(lo, hi):
    if lo is None or hi is None or (isinstance(lo, float) and np.isnan(lo)):
        return "n/a"
    return f"[{lo:+.2f}, {hi:+.2f}]"


def write_markdown(board, inter, clusters, label_by_id):
    n_lead = int((board["verdict"] == "CONFIRMED").sum())
    n_como = int((board["verdict"].isin(["CO-MOVER (not a lead)", "CO-MOVER (cycle-driven)"])).sum())
    n_short = int((board["verdict"] == "SHORT-SAMPLE (unverified)").sum())
    lines = ["# Leaderboard — do metal inputs lead transformer prices?", "",
             f"**{n_lead} true leads · {n_como} co-movers** (strong & FDR-significant but peak ≈ lag 0)"
             f" · **{n_short} short-sample (unverified)**.",
             "Four guardrails run together: **q** = Benjamini-Hochberg FDR across all signals "
             "(CONFIRMED needs q<0.05); **r@0** and **gain** = lead-sharpness (peak |r| minus "
             "lag-0 |r|; a small gain = co-mover, not a lead); **min-history** = a short sample "
             f"(n<{HIST.MIN_MONTHS} or start after {HIST.LATE_START.date()}) can't be CONFIRMED "
             "unless a long series corroborates the same force and it isn't a window artifact "
             "(see `analysis.md` §3 / `short_sample_check.csv`); per-force compositing in "
             "`analysis.md`.", "",
             "Positive lead = candidate leads the transformer PPI (months). "
             "`robust` = passes both disqualifying gates. **short** marks a short usable sample.", "",
             "| # | Signal | Verdict | Lead | Peak r | r@0 | gain | 95% CI | Perm q | Robust | n | short | Cat |",
             "|---|--------|---------|------|--------|-----|------|--------|--------|--------|---|-------|-----|"]
    for _, r in board.iterrows():
        g = "" if r.get("lead_gain") is None or pd.isna(r.get("lead_gain")) else f"{r['lead_gain']:+.2f}"
        r0 = "" if r.get("r_lag0") is None or pd.isna(r.get("r_lag0")) else f"{r['r_lag0']:+.2f}"
        sh = "⚠︎" if r.get("short_sample") == "yes" else ""
        lines.append(
            f"| {r['rank']} | {r['signal']} | **{r['verdict']}** | "
            f"{r['measured_lead_months']:+d} | {r['peak_r']:+.2f} | {r0} | {g} | "
            f"{_fmt_ci(r['ci95_low'], r['ci95_high'])} | {r['perm_q']} | {r['robust']} | "
            f"{r['n']} | {sh} | {r.get('category','')} |")
    lines += ["", "## Leading-signal correlation matrix (contemporaneous YoY)", "",
              "Values are Pearson r. Pairs with |r| >= 0.70 are the *same underlying force* "
              "and must not count as independent confirmations.", ""]

    ids = list(inter.index)
    if len(ids) <= 40:
        header = "| | " + " | ".join(label_by_id[i].split(" (")[0][:14] for i in ids) + " |"
        lines.append(header)
        lines.append("|" + "---|" * (len(ids) + 1))
        for i in ids:
            cells = []
            for j in ids:
                v = inter.loc[i, j]
                if np.isnan(v):
                    cells.append("·")
                elif i != j and abs(v) >= CFG.CLUSTER_R:
                    cells.append(f"**{v:.2f}**")
                else:
                    cells.append(f"{v:.2f}")
            lines.append(f"| {label_by_id[i].split(' (')[0][:18]} | " + " | ".join(cells) + " |")
    else:
        lines.append(f"*{len(ids)}×{len(ids)} matrix — too large to render inline; see "
                     "`leading_signal_corr_matrix.csv` and the clustered heatmap "
                     "`charts/_clustered_heatmap.png`. Clusters at |r|≥0.70 listed below.*")

    lines += ["", "## Flagged clusters (|r| >= 0.70 — count as ONE witness each)", ""]
    if clusters:
        for k, cl in enumerate(clusters, 1):
            names = ", ".join(label_by_id[c] for c in cl)
            lines.append(f"- **Cluster {k}:** {names}")
    else:
        lines.append("- No clusters at |r| >= 0.70; all signals are at least partly independent.")
    lines.append("")

    with open(os.path.join(OUT, "leaderboard.md"), "w") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    main()
