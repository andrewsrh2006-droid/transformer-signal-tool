#!/usr/bin/env python3
"""Streamlit dashboard for the transformer leading-signal results.

Reads the artifacts produced by `run_pipeline.py` (leaderboard, correlation matrix,
per-pair details) plus the cached FRED CSVs, and presents them interactively:

  • Leaderboard  — ranked, verdict-coloured table + headline metrics
  • Correlation  — interactive heatmap of the leading signals + flagged clusters
  • Signal detail — per-pair mechanism, screen/gate/significance readouts, and three
                    interactive charts (levels, YoY overlay, lag-correlation curve)

Run:  streamlit run app.py
The dashboard never re-runs the heavy permutation/bootstrap; it consumes the saved
outputs committed in the repo. To regenerate them offline (developer step, needs the
raw FRED CSVs), run `python3 run_pipeline.py` locally.
"""

import json
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Belt-and-suspenders: the deployed dashboard is fully offline. Every series it needs is a
# committed CSV under data/raw/, so it never fetches from FRED. This flag makes the data
# loader raise a clear error instead of hitting the network if a cache were ever missing.
os.environ.setdefault("SIGNAL_TOOL_NO_NETWORK", "1")

from signal_tool import config as CFG
from signal_tool import fred, process as P
from signal_tool import matrix as MTX
from signal_tool import control as CTRL
from signal_tool import correlate as C
from signal_tool import screen as SCR
from signal_tool import leaderboard as LB

# One-line reminder shown atop every analytical tab: the two layers are the SAME checks at
# different aggregation, and the force count is not a count of independent bets.
LAYER_REMINDER = (
    "🔹 **Signal** and 🔸 **Force** below run the *same checks at different aggregation* "
    "(a force = a tight ≥0.70 cluster collapsed into one equal-weighted composite = one "
    "witness). The force **count is not a count of independent bets** — cousins remain; the "
    "partial-r market control and the inter-force matrix (Correlation tab) are the real "
    "independence check.")

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "outputs")

VERDICT_COLORS = {
    "CONFIRMED": "#1a7f37",
    "STRONG BUT CYCLE-DRIVEN": "#9a4d00",
    "STRONG / NOT ROBUST": "#bf8700",
    "SHORT-SAMPLE (unverified)": "#953800",
    "PARTIAL / INCONCLUSIVE": "#9a6700",
    "CO-MOVER (not a lead)": "#0969da",
    "CO-MOVER (cycle-driven)": "#0e7490",
    "REVERSED": "#8250df",
    "REJECTED": "#cf222e",
}
VERDICT_BG = {
    "CONFIRMED": "#dafbe1",
    "STRONG BUT CYCLE-DRIVEN": "#ffede0",
    "STRONG / NOT ROBUST": "#fff8c5",
    "SHORT-SAMPLE (unverified)": "#ffe7d1",
    "PARTIAL / INCONCLUSIVE": "#fff1e5",
    "CO-MOVER (not a lead)": "#ddf4ff",
    "CO-MOVER (cycle-driven)": "#d0f0f5",
    "REVERSED": "#fbefff",
    "REJECTED": "#ffebe9",
}

# One tile per verdict. Relationship type leads (confirmed → co-mover → reversed), then the
# weaker forward grades, then short-sample and rejected. The header tiles and the Compare-tab
# tally strip both render from this list, so their counts always agree.
VERDICT_TILES = [
    ("✅ Confirmed", "CONFIRMED"),
    ("↔️ Co-mover (pure)", "CO-MOVER (not a lead)"),
    ("🌀 Co-mover · cycle-driven", "CO-MOVER (cycle-driven)"),
    ("❌ Reversed", "REVERSED"),
    ("🌀 Strong but cycle-driven", "STRONG BUT CYCLE-DRIVEN"),
    ("⚠️ Strong / not robust", "STRONG / NOT ROBUST"),
    ("⚠️ Partial", "PARTIAL / INCONCLUSIVE"),
    ("⏳ Short-sample", "SHORT-SAMPLE (unverified)"),
    ("❌ Rejected", "REJECTED"),
]


def header_tiles_html(board) -> str:
    """Verdict tally as wrapping tiles (never clipped): a big count over a full, two-line-capable
    label, tinted per verdict. Signals-tested leads; the eight verdict tiles sum to it."""
    vc = board["verdict"].value_counts()
    tiles = [("📊 Signals tested", None, len(board))]
    tiles += [(lbl, key, int(vc.get(key, 0))) for lbl, key in VERDICT_TILES]
    cells = []
    for lbl, key, count in tiles:
        fg = "#24292f" if key is None else VERDICT_COLORS.get(key, "#24292f")
        bg = "#f6f8fa" if key is None else VERDICT_BG.get(key, "#f6f8fa")
        cells.append(
            f"<div style='flex:1 1 130px;min-width:130px;background:{bg};border:1px solid #d0d7de;"
            f"border-radius:9px;padding:8px 10px'>"
            f"<div style='font-size:1.5rem;font-weight:700;color:{fg};line-height:1'>{count}</div>"
            f"<div style='font-size:0.8rem;color:{fg};margin-top:3px;white-space:normal;"
            f"line-height:1.15'>{lbl}</div></div>")
    return "<div style='display:flex;flex-wrap:wrap;gap:8px;margin:2px 0 6px'>" + "".join(cells) + "</div>"

# Cell shout-palette for the Compare transparency table (fg, bg). Failures use red, passes green,
# soft-fails amber — so a verdict is legible from the row alone, no drill-down needed.
_SHOUT = {
    "pass":  ("#1a7f37", "#dafbe1"),
    "fail":  ("#cf222e", "#ffebe9"),
    "warn":  ("#9a6700", "#fff8c5"),
    "muted": ("#57606a", "transparent"),
}


def verdict_strip_html(board) -> str:
    """A compact one-line verdict tally (same counts as the header tiles), colored per verdict."""
    vc = board["verdict"].value_counts()
    chips = [f"<span style='background:#eaeef2;color:#24292f;padding:2px 9px;border-radius:5px;"
             f"font-weight:600'>{len(board)} tested</span>"]
    for label, key in VERDICT_TILES:
        chips.append(
            f"<span style='background:{VERDICT_BG.get(key, '#fff')};color:{VERDICT_COLORS.get(key, '#000')};"
            f"padding:2px 9px;border-radius:5px;font-weight:600'>{label} {int(vc.get(key, 0))}</span>")
    return "<div style='display:flex;flex-wrap:wrap;gap:6px;font-size:0.86rem'>" + "".join(chips) + "</div>"

st.set_page_config(page_title="Transformer leading-signal dashboard",
                   page_icon="⚡", layout="wide")


# --------------------------------------------------------------------------- data
@st.cache_data(show_spinner=False)
def load_outputs():
    board = pd.read_csv(os.path.join(OUT, "leaderboard.csv"))
    inter = pd.read_csv(os.path.join(OUT, "leading_signal_corr_matrix.csv"), index_col=0)
    with open(os.path.join(OUT, "pair_details.json")) as fh:
        details = json.load(fh)
    return board, inter, details


@st.cache_data(show_spinner=False)
def load_analysis():
    """Clustering assignments + cycle-control table (both optional)."""
    clusters = None
    cpath = os.path.join(OUT, "clusters.json")
    if os.path.exists(cpath):
        with open(cpath) as fh:
            clusters = json.load(fh)
    ctrl = None
    ctlpath = os.path.join(OUT, "cycle_control.csv")
    if os.path.exists(ctlpath):
        ctrl = pd.read_csv(ctlpath)
    force = None
    fpath = os.path.join(OUT, "force_cycle_control.csv")
    if os.path.exists(fpath):
        force = pd.read_csv(fpath)
    return clusters, ctrl, force


@st.cache_data(show_spinner=False)
def load_level(fred_id: str) -> pd.Series:
    """Level series from the cached CSV (offline; no network)."""
    return P.to_monthly(fred.load_series(fred_id))


def outputs_exist() -> bool:
    return all(os.path.exists(os.path.join(OUT, f)) for f in
               ("leaderboard.csv", "leading_signal_corr_matrix.csv", "pair_details.json"))


LABEL = {c.fred_id: c.label for c in CFG.CANDIDATES}
MECH = {c.fred_id: c.mechanism for c in CFG.CANDIDATES}
NOTE = {c.fred_id: c.note for c in CFG.CANDIDATES}
STARTER = {c.fred_id: c.starter for c in CFG.CANDIDATES}
OUT_ID = CFG.OUTCOME.fred_id


# ------------------------------------------------------------------------- charts
def levels_fig(cid: str) -> go.Figure:
    lc = load_level(cid)
    lo = load_level(OUT_ID)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=lo.index, y=lo.values, name="Transformer PPI",
                             line=dict(color="#24292f", width=1.6)), secondary_y=False)
    fig.add_trace(go.Scatter(x=lc.index, y=lc.values, name=LABEL[cid],
                             line=dict(color="#cf222e", width=1.6)), secondary_y=True)
    fig.update_yaxes(title_text="Transformer PPI", secondary_y=False,
                     title_font_color="#24292f")
    fig.update_yaxes(title_text=LABEL[cid], secondary_y=True, title_font_color="#cf222e")
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=30, b=10),
                      legend=dict(orientation="h", y=1.12),
                      title="Level (0th derivative) — original data, dual axis")
    return fig


def yoy_fig(cid: str) -> go.Figure:
    df = P.align(P.yoy(load_level(cid)), P.yoy(load_level(OUT_ID)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["outcome"], name="Transformer YoY",
                             line=dict(color="#24292f", width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=df["cand"], name="Candidate YoY",
                             line=dict(color="#cf222e", width=1.5)))
    fig.add_hline(y=0, line=dict(color="#8c959f", width=0.8))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=30, b=10),
                      legend=dict(orientation="h", y=1.12),
                      title="1st derivative — YoY % change  (x_t / x_{t-12} − 1)×100",
                      yaxis_title="% YoY")
    return fig


def yoy2_fig(cid: str) -> go.Figure:
    """Second derivative: 12-month change in the YoY series (candidate vs outcome)."""
    cand2 = P.yoy2(load_level(cid))
    out2 = P.yoy2(load_level(OUT_ID))
    df = pd.concat([cand2.rename("cand"), out2.rename("outcome")], axis=1).dropna(how="all")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["outcome"], name="Transformer Δ-YoY",
                             line=dict(color="#24292f", width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=df["cand"], name="Candidate Δ-YoY",
                             line=dict(color="#cf222e", width=1.5)))
    fig.add_hline(y=0, line=dict(color="#8c959f", width=0.8))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=30, b=10),
                      legend=dict(orientation="h", y=1.12),
                      title="2nd derivative — 12-month change in YoY (Δ of the 1st derivative)",
                      yaxis_title="Δ %-pts YoY")
    return fig


@st.cache_data(show_spinner=False)
def build_data_table(cid: str) -> pd.DataFrame:
    """Original observations + all three views for candidate and outcome (outer join)."""
    cv = P.three_views(load_level(cid))
    ov = P.three_views(load_level(OUT_ID))
    df = pd.DataFrame({
        f"{cid} level": cv["level"], f"{cid} YoY%": cv["yoy"], f"{cid} Δ-YoY": cv["yoy2"],
        f"{OUT_ID} level": ov["level"], f"{OUT_ID} YoY%": ov["yoy"],
        f"{OUT_ID} Δ-YoY": ov["yoy2"],
    })
    df.index.name = "date"
    return df.round(3)


def lag_fig(cid: str, details: dict) -> go.Figure:
    d = details[cid]
    curve = {int(k): v for k, v in d["lag_curve"].items()}
    ks = sorted(curve)
    rs = [curve[k] for k in ks]
    peak_lag, peak_r = d["peak"]["lag"], d["peak"]["r"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ks, y=rs, mode="lines", name="r(lag)",
                             line=dict(color="#0969da", width=2.2),
                             hovertemplate="lag %{x} mo<br>r=%{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[peak_lag], y=[peak_r], mode="markers+text",
                             marker=dict(color="#cf222e", size=11),
                             text=[f"  r={peak_r:.2f} @ {peak_lag:+d}m"],
                             textposition="top center", showlegend=False))
    fig.add_hline(y=0, line=dict(color="#8c959f", width=0.8))
    fig.add_vline(x=0, line=dict(color="#8c959f", width=0.8, dash="dot"))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=30, b=10),
                      title="Lag correlation  (+k = candidate leads)",
                      xaxis_title="lag k (months)", yaxis_title="Pearson r")
    return fig


SURVIVAL_COLORS = {"survives": "#1a7f37", "partly survives": "#bf8700",
                   "cycle-driven": "#cf222e", "n/a": "#57606a"}


def cycle_bar_fig(ctrl: pd.DataFrame) -> go.Figure:
    """Raw vs partial (|market) lead-r for each confirmed signal.

    Only these two are shown: the partial r is the measure that decides survival. The
    relative-series r is kept in the CSV as a diagnostic (it misleads for volatile signals).
    """
    df = ctrl.sort_values("partial_r_ctrl_market", ascending=True)
    labels = [s.split(" (")[0] for s in df["signal"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=labels, x=df["raw_r"], name="Raw lead r",
                         orientation="h", marker_color="#8c959f"))
    fig.add_trace(go.Bar(y=labels, x=df["partial_r_ctrl_market"],
                         name="Partial r (∣ market) — decides survival",
                         orientation="h", marker_color="#0969da"))
    fig.add_vline(x=0.30, line=dict(color="#1a7f37", width=1, dash="dot"),
                  annotation_text="survives ≥0.30", annotation_font_size=10)
    fig.add_vline(x=0.20, line=dict(color="#cf222e", width=1, dash="dot"),
                  annotation_text="cycle-driven <0.20", annotation_font_size=10)
    fig.add_vline(x=0.0, line=dict(color="#8c959f", width=0.8))
    fig.update_layout(barmode="group", height=460, margin=dict(l=10, r=10, t=30, b=10),
                      legend=dict(orientation="h", y=1.08),
                      xaxis_title="correlation with transformer PPI",
                      title="Predictive power before vs after removing the commodity cycle")
    return fig


@st.cache_data(show_spinner=False)
def spread_data_signal(cid: str, lead_k: int):
    mkt_yoy = P.yoy(load_level(CFG.MARKET.fred_id))
    df, meta = CTRL.spread_series(load_level(cid), load_level(OUT_ID), mkt_yoy, lead_k)
    return df, meta, lead_k


@st.cache_data(show_spinner=False)
def spread_data_force(member_ids: tuple):
    mkt_yoy = P.yoy(load_level(CFG.MARKET.fred_id))
    return CTRL.force_spread([load_level(m) for m in member_ids], load_level(OUT_ID),
                             mkt_yoy, CFG.MAX_LAG)


def spread_fig(df, meta, series_label: str, lead_k: int, standardize: bool = True) -> go.Figure:
    """Render an observable de-cycled spread: signal/force − β·market vs transformer − β·market.

    standardize=True z-scores each spread (mean 0, sd 1) so the two lines share a scale and
    the co-movement (= the partial correlation) is visually obvious. The correlation is
    scale-invariant, so it is identical in either view.
    """
    sig, out = df["signal_spread"], df["outcome_spread"]
    if standardize:
        sig = (sig - sig.mean()) / sig.std(ddof=0)
        out = (out - out.mean()) / out.std(ddof=0)
        ytitle = "de-cycled spread (z-score, σ units)"
        scale_note = "standardized (z-scored)"
    else:
        ytitle = "de-cycled YoY (%-pts)"
        scale_note = "raw %-pts"
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=out, name="Transformer spread",
                             line=dict(color="#24292f", width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=sig, name=f"{series_label} spread",
                             line=dict(color="#cf222e", width=1.5)))
    fig.add_hline(y=0, line=dict(color="#8c959f", width=0.8))
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=48, b=10),
                      legend=dict(orientation="h", y=1.14),
                      yaxis_title=ytitle,
                      title=(f"De-cycled spreads (lead +{lead_k}m) — both sides minus β·market · "
                             f"{scale_note} (β_signal={meta['beta_signal']:.1f}, "
                             f"β_transf={meta['beta_outcome']:.1f}); "
                             f"corr = {meta['spread_r']:+.2f} = partial r (same either view)"))
    return fig


def heatmap_fig(inter: pd.DataFrame) -> go.Figure:
    ids = list(inter.index)
    labels = [LABEL[i].split(" (")[0] for i in ids]
    z = inter.values.astype(float)
    text = [[f"{v:.2f}" if v == v else "" for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=labels, y=labels, text=text, texttemplate="%{text}",
        textfont=dict(size=9), zmin=-1, zmax=1, colorscale="RdBu", reversescale=True,
        colorbar=dict(title="r"),
        hovertemplate="%{y}<br>%{x}<br>r=%{z:.2f}<extra></extra>"))
    fig.update_layout(height=680, margin=dict(l=10, r=10, t=30, b=10),
                      xaxis=dict(tickangle=-45), yaxis=dict(autorange="reversed"),
                      title="Contemporaneous YoY correlation of the leading signals")
    return fig


# ---------------------------------------------------------- shared signal/force layer logic
# The SAME functions drive both layers, so the analysis can never diverge: a signal provides
# its own YoY series; a force provides the equal-weighted composite YoY of its members.
@st.cache_data(show_spinner=False)
def force_composite_yoy(member_ids: tuple) -> pd.Series:
    return CTRL.composite_yoy([load_level(m) for m in member_ids])


def _cand_yoy(kind: str, ident):
    """YoY series for a signal (ident=fred_id) or a force (ident=tuple of member ids)."""
    if kind == "force":
        return force_composite_yoy(tuple(ident))
    return P.yoy(load_level(ident))


def analyze(cand_yoy: pd.Series) -> dict:
    """Run the identical battery (peak-lead, gates, lead-sharpness, market-control partial r)
    on any YoY series — one signal or one force composite. Used by BOTH layers."""
    out_yoy = P.yoy(load_level(OUT_ID))
    mkt_yoy = P.yoy(load_level(CFG.MARKET.fred_id))
    dfa = P.align(cand_yoy, out_yoy)
    a, b = dfa["cand"].to_numpy(), dfa["outcome"].to_numpy()
    curve, peak = C.peak_lag_corr(a, b, CFG.MAX_LAG)
    gates = SCR.run_gates(a, b, peak, CFG.MAX_LAG, index=dfa.index, smooth_win=CFG.SMOOTH_WIN,
                          r_min_screen=CFG.R_MIN_SCREEN) if peak else None
    sharp = C.lead_sharpness(curve, peak)
    lead = int(peak[0]) if peak else 0
    cc = CTRL.cycle_control_yoy(cand_yoy, out_yoy, mkt_yoy, lead)
    return {"curve": curve, "peak": peak, "gates": gates, "sharp": sharp, "cc": cc,
            "n": int(len(dfa)), "lead": lead}


def yoy_overlay_fig(cand_yoy: pd.Series, label: str, color="#cf222e") -> go.Figure:
    """1st-derivative overlay: any candidate/composite YoY vs the transformer YoY."""
    df = P.align(cand_yoy, P.yoy(load_level(OUT_ID)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["outcome"], name="Transformer YoY",
                             line=dict(color="#24292f", width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=df["cand"], name=f"{label} YoY",
                             line=dict(color=color, width=1.5)))
    fig.add_hline(y=0, line=dict(color="#8c959f", width=0.8))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=30, b=10),
                      legend=dict(orientation="h", y=1.12), yaxis_title="% YoY",
                      title="1st derivative — YoY % change")
    return fig


def lag_curve_fig(curve: dict, peak, title="Lag correlation  (+k = candidate leads)") -> go.Figure:
    """Lag-correlation curve from a live curve dict (k -> (r, n)) or (k -> r)."""
    ks = sorted(curve)
    rs = [(curve[k][0] if isinstance(curve[k], (tuple, list)) else curve[k]) for k in ks]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ks, y=rs, mode="lines", line=dict(color="#0969da", width=2.2),
                             hovertemplate="lag %{x} mo<br>r=%{y:.2f}<extra></extra>", name="r(lag)"))
    if peak:
        fig.add_trace(go.Scatter(x=[peak[0]], y=[peak[1]], mode="markers+text",
                                 marker=dict(color="#cf222e", size=11),
                                 text=[f"  r={peak[1]:.2f} @ {peak[0]:+d}m"],
                                 textposition="top center", showlegend=False))
    fig.add_hline(y=0, line=dict(color="#8c959f", width=0.8))
    fig.add_vline(x=0, line=dict(color="#8c959f", width=0.8, dash="dot"))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=30, b=10), title=title,
                      xaxis_title="lag k (months)", yaxis_title="Pearson r")
    return fig


def raw_partial_bar_fig(a: dict, label: str) -> go.Figure:
    """Raw lead-r vs market-controlled partial-r for ONE item (signal or force).

    The same function drives both layers, so a cycle-driven item (raw high, partial near
    zero) is visually obvious identically at signal and force level: the left bar stays tall
    while the right bar collapses toward — or through — the ±0.20 survival band."""
    peak, cc = a["peak"], a["cc"]
    raw = peak[1] if peak else float("nan")
    part = cc.get("partial_r")
    part = float("nan") if part is None else float(part)
    surv = cc.get("survival", "")
    survives = (part == part) and abs(part) >= 0.20
    part_col = "#1a7f37" if survives else "#cf222e"
    fig = go.Figure(go.Bar(
        x=["Raw lead r", "Partial r ( ∣ cycle )"], y=[raw, part],
        marker_color=["#0969da", part_col],
        text=[f"{raw:+.2f}", "n/a" if part != part else f"{part:+.2f}"],
        textposition="outside", cliponaxis=False, width=0.55))
    fig.add_hline(y=0, line=dict(color="#24292f", width=1))
    fig.add_hline(y=0.20, line=dict(color="#1a7f37", width=1, dash="dot"),
                  annotation_text="survives +0.20", annotation_position="top left",
                  annotation_font_size=10)
    fig.add_hline(y=-0.20, line=dict(color="#1a7f37", width=1, dash="dot"))
    fig.add_hline(y=0.50, line=dict(color="#8c959f", width=1, dash="dash"),
                  annotation_text="strong +0.50", annotation_position="top left",
                  annotation_font_size=10)
    lo = min(-0.30, part - 0.10) if part == part else -0.30
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=44, b=10), showlegend=False,
                      yaxis=dict(range=[lo, max(1.0, raw + 0.15 if raw == raw else 1.0)],
                                 title="Pearson r", zeroline=False),
                      title=f"Cycle control — raw {raw:+.2f} → partial "
                            + ("n/a" if part != part else f"{part:+.2f}") + f"  ({surv})")
    return fig


def render_screen_panel(a: dict, verdict=None, perm_q=None, extra_short=None):
    """The gates / lead-sharpness / market-control panel — identical for signal & force."""
    peak, g, sh, cc = a["peak"], a["gates"], a["sharp"], a["cc"]
    if peak is None or g is None:
        st.info("Not enough overlapping history to run the screen.")
        return
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Peak r", f"{peak[1]:+.2f}")
    m2.metric("Measured lead", f"{peak[0]:+d} mo")
    m3.metric("Partial r (∣mkt)", f"{cc['partial_r']:+.2f}" if cc['partial_r'] is not None else "n/a")
    m4.metric("n", a["n"])

    sg, hg = g["smoothing_gate"], g["holds_gate"]
    eg = g.get("episode_gate")
    ca, cb, cc2 = st.columns(3)
    ca.markdown(f"**Screen:** {'✅ passes' if g['screen_pass'] else '❌ fails'}  \n"
                f"leads: {'yes' if g['leads'] else 'no'} · |r|≥0.30: "
                f"{'yes' if g['strong_enough'] else 'no'}")
    cb.markdown(f"**Gate · smoothing:** {'✅' if sg['pass'] else '❌'}  \n"
                f"smoothed r={sg['smoothed_r']} @ {sg['smoothed_lag']}m")
    hgr = hg.get("reason", "")
    cc2.markdown(f"**Gate · holds over time:** {'✅' if hg['pass'] else '❌'}  \n"
                 f"early r={hg['early_r']} · late r={hg['late_r']}"
                 + (f"  \n<span style='color:#cf222e;font-size:0.85em'>{hgr}</span>"
                    if not hg["pass"] and hgr else ""), unsafe_allow_html=True)
    if eg is not None:
        egr = eg.get("reason", "")
        wr, wb = eg.get("worst_r"), eg.get("worst_block")
        detail = (f"worst leave-one-out r={wr:+.2f} (drop {wb})"
                  if wr is not None else "history too short to jackknife")
        st.markdown(f"**Gate · episode-robust (3-yr block jackknife):** "
                    f"{'✅' if eg['pass'] else '❌'} — {detail}"
                    + (f"  \n<span style='color:#cf222e;font-size:0.85em'>{egr}</span>"
                       if not eg["pass"] and egr else ""), unsafe_allow_html=True)

    surv = cc["survival"]
    surv_icon = {"survives": "✅", "partly survives": "◐", "cycle-driven": "⚠️",
                 "not cycle-driven (weak on its own)": "○"}.get(surv, "")
    d1, d2, d3 = st.columns(3)
    _lc = sh.get("lead_class") or ("co-mover" if sh.get("is_comover") else "true lead")
    _lc_disp = {"true lead": "✅ true lead",
                "co-mover": "⚠️ co-mover",
                "lags": "↩️ lags / negative lead (outcome moves first)",
                "undetermined": "—"}.get(_lc, "—")
    d1.markdown(f"**Lead-sharpness:** {_lc_disp}  \n"
                f"r@0={sh.get('r_lag0')} · gain={sh.get('lead_gain')}")
    d2.markdown(f"**Market-control survival:** {surv_icon}  \nvs commodity cycle: **{surv}**")
    if verdict is not None:
        badge = (f"<span style='background:{VERDICT_BG.get(verdict,'#eee')};"
                 f"color:{VERDICT_COLORS.get(verdict,'#000')};padding:2px 10px;border-radius:6px;"
                 f"font-weight:700'>{verdict}</span>")
        d3.markdown(f"**Verdict:** {badge}"
                    + (f"  \nFDR q={perm_q}" if perm_q is not None else ""),
                    unsafe_allow_html=True)

    # Binding reason (same logic as the Compare 'Why' column): for a co-mover / reversal that is
    # also cycle-driven, this appends ", and cycle-driven (partial X)" so the cycle read is explicit.
    _why = compose_reason(peak[1], peak[0], _lc, cc.get("survival"), cc.get("partial_r"),
                          a.get("n"), extra_short is not None,
                          sg.get("pass"), hg.get("pass"), eg.get("pass") if eg else None,
                          q=perm_q, verdict=verdict)
    _wc = ("#1a7f37" if _why == "confirmed lead"
           else "#9a6700" if (_why.startswith("co-mover") or _why.startswith("moderate"))
           else "#cf222e")
    st.markdown(f"**Why:** <span style='color:{_wc};font-weight:600'>{_why}</span>",
                unsafe_allow_html=True)
    if extra_short:
        st.markdown(f"<span style='color:#953800'>⚠️ **Short-sample:** {extra_short}</span>",
                    unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_force_matrix():
    fp = os.path.join(OUT, "force_correlation_matrix.csv")
    if os.path.exists(fp):
        return pd.read_csv(fp, index_col=0)
    return None


@st.cache_data(show_spinner=False)
def load_bloc_leaderboard():
    fp = os.path.join(OUT, "loose_bloc_cycle_control.csv")
    return pd.read_csv(fp) if os.path.exists(fp) else None


@st.cache_data(show_spinner=False)
def load_bloc_matrix():
    fp = os.path.join(OUT, "bloc_correlation_matrix.csv")
    return pd.read_csv(fp, index_col=0) if os.path.exists(fp) else None


def render_clustering(cj, dpath, hpath, one_witness_word):
    """How a group level is defined: the dendrogram, the cluster listing (multi-signal clusters
    vs independent singletons), and the clustered correlation heatmap. Shared by both levels."""
    if os.path.exists(dpath):
        st.image(dpath, use_container_width=True)
    if cj:
        st.markdown(f"**Clusters at the r = {cj['cut_r']:.2f} cut** "
                    f"(method: {cj['method']}, distance: {cj['distance']}):")
        multi, singles = [], []
        for k, members in cj["clusters"].items():
            names = [m["label"] for m in members]
            (multi if len(names) > 1 else singles).append((k, names))
        for k, names in multi:
            st.markdown(f"- 🔴 **Cluster {k} — one {one_witness_word} ({len(names)}):** "
                        + ", ".join(names))
        if singles:
            st.markdown(f"- ⚪ **{len(singles)} independent singletons** (each its own group).")
    if os.path.exists(hpath):
        with st.expander("Clustered correlation heatmap (leaf order)", expanded=False):
            st.image(hpath, use_container_width=True)


@st.cache_data(show_spinner=False)
def load_ladder():
    fp = os.path.join(OUT, "grouping_ladder.json")
    if os.path.exists(fp):
        with open(fp) as fh:
            return json.load(fh)
    return None


def group_matrix_fig(fm, title):
    """Inter-group correlation heatmap (tight forces OR loose blocs), same style for both."""
    labels = [str(c).split(" ↳")[0][:26] for c in fm.index]
    z = fm.values.astype(float)
    txt = [[f"{v:.2f}" if v == v else "" for v in row] for row in z]
    hf = go.Figure(go.Heatmap(z=z, x=labels, y=labels, text=txt, texttemplate="%{text}",
                   textfont=dict(size=9), zmin=-1, zmax=1, colorscale="RdBu",
                   reversescale=True, colorbar=dict(title="r")))
    hf.update_layout(height=560, margin=dict(l=10, r=10, t=34, b=10),
                     xaxis=dict(tickangle=-45), yaxis=dict(autorange="reversed"), title=title)
    return hf


def cousin_pairs(fm):
    import itertools
    return [(a, b, float(fm.loc[a, b])) for a, b in itertools.combinations(list(fm.index), 2)
            if pd.notna(fm.loc[a, b]) and 0.5 <= abs(fm.loc[a, b]) < CFG.CLUSTER_R]


def render_ladder_note():
    """The three-rung grouping ladder + its independence stats (shared by Compare/Correlation)."""
    st.markdown("**The grouping ladder** — 🔹 **signals** → 🔸 **tight forces** (cohesive, cousins "
                "remain) → 🔶 **loose blocs** (most independent, coarser). Each rung trades "
                "resolution for independence: merging same-sign cousins lowers cross-correlation "
                "and yields fewer, more independent groupings.")
    lad = load_ladder()
    if not lad:
        return
    def fmt(v):
        return "—" if v is None else (f"{v:.3f}" if isinstance(v, (int, float)) else str(v))
    def s(v):
        return "—" if v is None else str(v)
    tbl = pd.DataFrame([
        {"Rung": "🔹 Signals", "Groups": s(lad["signal"]["n_groups"]),
         "Mean inter-group |r|": "—", "Cousin pairs (0.5–0.7)": "—"},
        {"Rung": "🔸 Tight forces", "Groups": s(lad["tight"]["n_groups"]),
         "Mean inter-group |r|": fmt(lad["tight"]["mean_abs_r"]),
         "Cousin pairs (0.5–0.7)": s(lad["tight"]["n_cousins"])},
        {"Rung": "🔶 Loose blocs", "Groups": s(lad["loose"]["n_groups"]),
         "Mean inter-group |r|": fmt(lad["loose"]["mean_abs_r"]),
         "Cousin pairs (0.5–0.7)": s(lad["loose"]["n_cousins"])},
    ])
    st.dataframe(tbl, use_container_width=True, hide_index=True)
    t, l = lad["tight"], lad["loose"]
    if t["mean_abs_r"] is not None and l["mean_abs_r"] is not None:
        st.caption(f"Loose blocs are **fewer** ({l['n_groups']} vs {t['n_groups']}) with **lower** "
                   f"mean inter-group |r| ({l['mean_abs_r']:.3f} vs {t['mean_abs_r']:.3f}) and "
                   f"**fewer cousins** ({l['n_cousins']} vs {t['n_cousins']}) — merging cousins "
                   "buys independence at the cost of resolution. *Groups* here counts the "
                   "lead-bearing groups in the independence matrix; the leaderboards list every "
                   "witness (each singleton included).")


def build_force_catalog(clusters_json, force_df):
    """List of the SCORED multi-signal forces for the force-layer selectors.

    A "force" here is a tight cluster that was actually collapsed into a composite and run
    through the full battery (force_cycle_control.csv). clusters.json contains many more
    multi-clusters (bond yields, inflation breakevens, …) that are part of the independence
    partition but were never tested as leads — those are NOT offered here. Member fred_ids
    are recovered from clusters.json by matching the row's member label-set."""
    if force_df is None or not clusters_json:
        return []
    ids_by_labels = {}
    for _, members in clusters_json["clusters"].items():
        ids = [m["fred_id"] for m in members]
        if len(ids) < 2:
            continue
        ids_by_labels[frozenset(LABEL.get(i, i).split(" (")[0] for i in ids)] = ids
    cat = []
    for _, r in force_df.iterrows():
        n = r.get("n_signals")
        if pd.isna(n) or int(n) < 2:
            continue
        if "status" in r and str(r.get("status")) != "scored":
            continue            # skip opposite-sign grab-bags (excluded); their composite is meaningless
        # Prefer the explicit member_ids column (robust — some labels contain commas); fall back
        # to matching the member label-set against the clusters json.
        ids = None
        if "member_ids" in r and pd.notna(r.get("member_ids")):
            ids = [x for x in str(r["member_ids"]).split(";") if x]
        if not ids:
            labelset = frozenset(s.strip() for s in str(r["members"]).replace(";", ",").split(","))
            ids = ids_by_labels.get(labelset)
        if not ids:                # name/label drift — skip rather than mislabel
            continue
        cat.append({"name": str(r["force"]), "ids": ids, "row": r})
    cat.sort(key=lambda c: -len(c["ids"]))
    # Unique keys by position — two distinct forces can share a display name (e.g. two
    # non-ferrous cores of different size); the "· N signals" suffix keeps them readable.
    for i, c in enumerate(cat):
        c["key"] = f"force::{i}"
    return cat


def force_data_table(member_ids) -> pd.DataFrame:
    comp = force_composite_yoy(tuple(member_ids))
    ov = P.three_views(load_level(OUT_ID))
    df = pd.DataFrame({"force composite YoY%": comp,
                       f"{OUT_ID} level": ov["level"], f"{OUT_ID} YoY%": ov["yoy"]})
    df.index.name = "date"
    return df.round(3)


# --------------------------------------------------------------------------- table
def style_board(board: pd.DataFrame):
    def fnum(x, s="{:+.2f}"):
        return "" if x is None or pd.isna(x) else s.format(x)
    disp = pd.DataFrame({
        "#": board["rank"],
        "Signal": board["signal"],
        "Category": board["category"] if "category" in board else "",
        "Verdict": board["verdict"],
        "Lead": board["measured_lead_months"].map(lambda x: f"{x:+d}"),
        "Peak r": board["peak_r"].map(lambda x: fnum(x)),
        "r@0": board["r_lag0"].map(fnum) if "r_lag0" in board else "",
        "gain": board["lead_gain"].map(fnum) if "lead_gain" in board else "",
        "Perm q": board["perm_q"].map(lambda x: fnum(x, "{:.3f}")) if "perm_q" in board else "",
        "Robust": board["robust"],
        "n": board["n"],
        "short": (board["short_sample"].map({"yes": "⚠︎", "no": ""})
                  if "short_sample" in board else ""),
    })

    def color_gain(val):
        try:
            v = float(val)
        except (ValueError, TypeError):
            return ""
        return "color:#1a7f37;font-weight:600" if v >= 0.05 else "color:#cf222e"

    def color_verdict(val):
        c = VERDICT_COLORS.get(val, "#24292f")
        bg = VERDICT_BG.get(val, "#ffffff")
        return f"color:{c}; background-color:{bg}; font-weight:600"

    sty = disp.style.map(color_verdict, subset=["Verdict"])
    if "gain" in disp:
        sty = sty.map(color_gain, subset=["gain"])
    return sty.hide(axis="index")


# ---------------------------------------------------------- Compare (full transparency)
# ONE column layout shared by the signal and force tables so rows line up 1:1. Every column
# that drives a verdict is visible and failures shout in color — no drill-down needed.
COMPARE_COLS = ["Signal", "Verdict", "Why", "Lead", "Raw r", "Partial r", "Cycle", "Leads?",
                "Smoothing", "Holds", "Episode", "History", "Lead type", "q", "N"]


def _g(row, *names, default=None):
    for n in names:
        if n in row and pd.notna(row[n]):
            return row[n]
    return default


def _as_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _as_int(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def _gate_cell(row, col):
    """A robustness gate: ✅ when it passes, a shouting ❌ NO when it fails, — when not run."""
    v = _g(row, col, default=None)
    if v is None:
        return "—"
    return "✅" if str(v).strip().lower() in ("yes", "true", "1") else "❌ NO"


def _cycle_cell(row):
    s = str(_g(row, "survival_vs_cycle", "survival", default="")).strip().lower()
    if s == "survives":
        return "survives"
    if s.startswith("partly"):
        return "partly"
    if s == "cycle-driven":
        return "cycle-driven"
    if s.startswith("not cycle"):
        return "weak"
    return "—"


def _lead_type_cell(row):
    """true lead / co-mover / lags for EVERY signal with a computable peak — classified from its
    lag and gain (same rule as correlate.lead_sharpness), even weak ones. Only a dash when the
    correlation itself is undefined (NaN lag or r)."""
    lc = str(_g(row, "lead_class", default="")).strip().lower()
    if lc in ("true lead", "co-mover", "lags"):
        return lc
    r = _as_float(_g(row, "peak_r", "raw_r"))
    lead = _as_int(_g(row, "measured_lead_months", "lead_months"))
    if r is None or lead is None:
        return "—"                                   # correlation truly undefined
    gain = _as_float(_g(row, "lead_gain"))
    if lead <= -1:
        if abs(lead) <= 2 and (gain is None or gain < 0.05):
            return "co-mover"                        # contemporaneous, near lag 0
        return "lags"                                # genuine negative lead
    if lead >= 1 and gain is not None and gain >= 0.05:
        return "true lead"
    return "co-mover"                                # at/near lag 0, barely beats it


def _episode_cell(row):
    """The 3-year block jackknife applies only to genuine forward-lead candidates with enough
    history. For a non-forward-lead signal (co-mover / lags), or a series too short to run the
    jackknife, show a grey 'n/a' (not applicable) rather than a bare dash or a misleading pass."""
    if _lead_type_cell(row) != "true lead":
        return "n/a"                                 # not a forward lead → gate doesn't apply
    ep = _g(row, "episode_pass", default=None)
    if ep is None:
        return "n/a"                                 # gate result unavailable (e.g. too short)
    if "episode_worst_r" in row and pd.isna(row.get("episode_worst_r")):
        return "n/a"                                 # too little history to jackknife 3-yr blocks
    return "✅" if str(ep).strip().lower() in ("yes", "true", "1") else "❌ NO"


def compose_reason(raw, lead, lead_class, survival, partial, n=None, short=False,
                   smoothing_ok=None, holds_ok=None, episode_ok=None,
                   q=None, ci_lo=None, ci_hi=None, verdict=None):
    """One plain-language binding reason, first match wins (weak → co-mover → reversed → gate
    fails → short-sample → cycle-driven → moderate → not-significant → else confirmed lead). A
    CO-MOVER or REVERSED row that is ALSO cycle-driven (partial |r| < 0.20 with a real drop from
    raw, i.e. its survival reads 'cycle-driven') gets ', and cycle-driven (partial X)' appended —
    parallel to how a forward lead reads 'strong but cycle-driven'. A strong forward lead that
    cleared the gates and cycle but is not CONFIRMED failed the FDR significance test (q ≥ 0.05)
    or its bootstrap CI spans zero — so it reads 'strong but not significant', not 'confirmed
    lead'."""
    lc = str(lead_class or "").strip().lower()
    surv = str(survival or "").strip().lower()
    cyc = ""
    if surv == "cycle-driven":
        cyc = (f", and cycle-driven (partial {partial:+.2f})" if partial is not None
               else ", and cycle-driven")

    if raw is not None and abs(raw) < 0.30:
        return f"too weak (raw {raw:+.2f})"
    if lc == "co-mover":
        return "co-mover" + cyc
    if lc == "lags":
        base = (f"reversed (outcome leads by {abs(lead)} mo)" if lead is not None
                else "reversed (outcome leads first)")
        return base + cyc
    if smoothing_ok is False:
        return "fails smoothing"
    if holds_ok is False:
        return "one-era only"
    if episode_ok is False:
        return "episode-driven"
    if short:
        return f"short-sample (only {n} months)" if n is not None else "short-sample"
    if surv == "cycle-driven":
        return f"cycle-driven (partial {partial:+.2f})" if partial is not None else "cycle-driven"
    if raw is not None and abs(raw) < 0.50:
        return f"moderate (raw {raw:+.2f})"
    # strong forward lead (|r| >= 0.50) that cleared the gates and cycle but isn't CONFIRMED:
    # the remaining CONFIRMED conditions are FDR significance and a CI that excludes zero.
    if q is not None and q >= CFG.SIG_ALPHA:
        return f"strong but not significant (q={q:.2f})"
    if ci_lo is not None and ci_hi is not None and ci_lo <= 0 <= ci_hi:
        return "strong but CI spans zero"
    if verdict is not None and str(verdict).strip().upper() != "CONFIRMED":
        return "strong but not robust"          # forces/blocs carry no q in the row
    return "confirmed lead"


def _okv(row, col):
    v = _g(row, col, default=None)
    if v is None:
        return None
    return str(v).strip().lower() in ("yes", "true", "1")


def _why_reason(row):
    """The Compare 'Why' cell — compose_reason from a leaderboard/force row."""
    return compose_reason(
        _as_float(_g(row, "peak_r", "raw_r")),
        _as_int(_g(row, "measured_lead_months", "lead_months")),
        _lead_type_cell(row),
        _g(row, "survival_vs_cycle", "survival", default=""),
        _as_float(_g(row, "partial_r_ctrl_market")),
        _as_int(_g(row, "n")),
        str(_g(row, "short_sample", default="")).lower() in ("yes", "true", "1"),
        _okv(row, "smoothing_pass"), _okv(row, "holds_pass"), _okv(row, "episode_pass"),
        q=_as_float(_g(row, "perm_q")),
        ci_lo=_as_float(_g(row, "ci95_low")), ci_hi=_as_float(_g(row, "ci95_high")),
        verdict=_g(row, "verdict"))


def sort_by_verdict(df: pd.DataFrame, r_col: str = "peak_r") -> pd.DataFrame:
    """Order rows best-to-worst by verdict (the same rank the signal leaderboard uses), then by
    |r| within a verdict — so all three Compare tables sort consistently."""
    if "verdict" not in df.columns:
        return df
    d = df.copy()
    d["_vr"] = d["verdict"].map(LB.VERDICT_RANK).fillna(9)
    d["_ar"] = d[r_col].abs() if r_col in d.columns else 0
    return d.sort_values(["_vr", "_ar"], ascending=[True, False]).drop(columns=["_vr", "_ar"])


def compare_frame(df: pd.DataFrame, name_col: str) -> pd.DataFrame:
    """Map a signal-board OR force-board frame onto the identical transparency layout."""
    rows = []
    for _, r in df.iterrows():
        lead = _as_int(_g(r, "measured_lead_months", "lead_months"))
        raw = _as_float(_g(r, "peak_r", "raw_r"))
        partial = _as_float(_g(r, "partial_r_ctrl_market"))
        q = _as_float(_g(r, "perm_q"))
        n = _as_int(_g(r, "n"))
        short = str(_g(r, "short_sample", default="")).lower() in ("yes", "true", "1")
        has_short_col = _g(r, "short_sample", default=None) is not None
        rows.append({
            "Signal": r[name_col],
            "Verdict": _g(r, "verdict", default="—"),
            "Why": _why_reason(r),
            "Lead": (f"{lead:+d}" if lead is not None else "—"),
            "Raw r": (f"{raw:+.2f}" if raw is not None else "—"),
            "Partial r": (f"{partial:+.2f}" if partial is not None else "—"),
            "Cycle": _cycle_cell(r),
            "Leads?": ("yes" if (lead is not None and lead >= 0) else "NO"),
            "Smoothing": _gate_cell(r, "smoothing_pass"),
            "Holds": _gate_cell(r, "holds_pass"),
            "Episode": _episode_cell(r),
            "History": ("❌ NO" if short else ("✅" if has_short_col or n is not None else "—")),
            "Lead type": _lead_type_cell(r),
            "q": (f"{q:.3f}" if q is not None else "—"),
            "N": (n if n is not None else "—"),
        })
    return pd.DataFrame(rows, columns=COMPARE_COLS)


def _shout_css(kind, bold=False):
    fg, bg = _SHOUT[kind]
    weight = ";font-weight:700" if bold else ""
    return f"color:{fg}{weight}" if bg == "transparent" else f"color:{fg};background-color:{bg}{weight}"


def style_compare(cf: pd.DataFrame):
    def sty_verdict(v):
        return f"color:{VERDICT_COLORS.get(v, '#57606a')};background-color:{VERDICT_BG.get(v, '#fff')};font-weight:600"

    def sty_why(v):
        s = str(v)
        if s == "confirmed lead":
            return _shout_css("pass", bold=True)
        if s.startswith("co-mover") or s.startswith("moderate"):
            return _shout_css("warn")          # co-mover stays amber even with a cycle-driven tail
        return _shout_css("fail", bold=True)   # every disqualifying reason shouts red

    def sty_cycle(v):
        return {"survives": _shout_css("pass"), "partly": _shout_css("warn"),
                "cycle-driven": _shout_css("fail", bold=True), "weak": _shout_css("muted")}.get(v, "")

    def sty_gate(v):
        s = str(v)
        if s == "n/a":
            return _shout_css("muted")            # grey: gate not applicable
        if "NO" in s:
            return _shout_css("fail", bold=True)
        return _shout_css("pass") if s == "✅" else ""

    def sty_leads(v):
        if v == "yes":
            return _shout_css("pass")
        if v == "NO":
            return _shout_css("fail", bold=True)
        return ""

    def sty_leadtype(v):
        if v == "true lead":
            return _shout_css("pass")
        if v in ("co-mover", "lags"):
            return _shout_css("warn")
        return ""

    def sty_partial(v):
        x = _as_float(v)
        if x is None:
            return ""
        return _shout_css("pass") if abs(x) >= 0.20 else _shout_css("fail", bold=True)

    sty = cf.style
    sty = sty.map(sty_verdict, subset=["Verdict"])
    sty = sty.map(sty_why, subset=["Why"])
    sty = sty.map(sty_cycle, subset=["Cycle"])
    sty = sty.map(sty_gate, subset=["Smoothing", "Holds", "Episode", "History"])
    sty = sty.map(sty_leads, subset=["Leads?"])
    sty = sty.map(sty_leadtype, subset=["Lead type"])
    sty = sty.map(sty_partial, subset=["Partial r"])
    return sty.hide(axis="index")


# ---------------------------------------------------------------- Lead-lag map helpers
ROLE_COLORS = {"source": "#1a7f37", "relay": "#0969da", "sink": "#cf222e"}


@st.cache_data(show_spinner=False)
def load_leadlag(kind: str):
    fn = {"signal": "lead_lag_edges.csv", "force": "lead_lag_edges_force.csv",
          "bloc": "lead_lag_edges_bloc.csv"}.get(kind, "lead_lag_edges.csv")
    fp = os.path.join(OUT, fn)
    return pd.read_csv(fp) if os.path.exists(fp) else None


@st.cache_data(show_spinner=False)
def load_clusters_loose():
    fp = os.path.join(OUT, "clusters_loose.json")
    if os.path.exists(fp):
        with open(fp) as fh:
            return json.load(fh)
    return None


def leadlag_roles(edges: pd.DataFrame):
    """Global node roles over the full edge set: source (leads, not led), sink (led, leads
    nothing), relay (both). Returns (role_by_node, indeg, outdeg, labels)."""
    from collections import Counter
    outd, ind = Counter(edges["source_id"]), Counter(edges["target_id"])
    nodes = set(edges["source_id"]) | set(edges["target_id"])
    labels = {}
    for _, e in edges.iterrows():
        labels[e["source_id"]] = e["source"]
        labels[e["target_id"]] = e["target"]
    role = {}
    for n in nodes:
        i, o = ind.get(n, 0), outd.get(n, 0)
        role[n] = "source" if (i == 0 and o > 0) else "sink" if (o == 0 and i > 0) else "relay"
    return role, ind, outd, labels


def leadlag_ranks(edge_pairs, nodes):
    """Longest-path layer index (x-position); relaxation with a cap so cycles can't loop."""
    rank = {n: 0 for n in nodes}
    for _ in range(len(nodes) + 1):
        changed = False
        for s, t in edge_pairs:
            if s in rank and t in rank and rank[t] < rank[s] + 1:
                rank[t] = rank[s] + 1
                changed = True
        if not changed:
            break
    return rank


def leadlag_ancestors(edges: pd.DataFrame, target_id):
    from collections import defaultdict
    preds = defaultdict(set)
    for s, t in zip(edges["source_id"], edges["target_id"]):
        preds[t].add(s)
    seen, stack = set(), [target_id]
    while stack:
        for p in preds.get(stack.pop(), ()):
            if p not in seen:
                seen.add(p)
                stack.append(p)
    return seen


def leadlag_fig(edges: pd.DataFrame, nodes: set, labels: dict, roles: dict, title: str,
                detail_max: int = 26) -> go.Figure:
    """Left→right propagation graph: sources left, relays middle, sinks right."""
    from collections import defaultdict
    E = [(s, t) for s, t in zip(edges["source_id"], edges["target_id"]) if s in nodes and t in nodes]
    rank = leadlag_ranks(E, nodes)
    byr = defaultdict(list)
    for n in nodes:
        byr[rank.get(n, 0)].append(n)
    pos = {}
    for rk, col in byr.items():
        col = sorted(col, key=lambda n: labels.get(n, n))
        m = len(col)
        for idx, n in enumerate(col):
            pos[n] = (rk, idx - (m - 1) / 2)
    detail = len(nodes) <= detail_max
    fig = go.Figure()
    ex, ey = [], []
    for s, t in E:
        ex += [pos[s][0], pos[t][0], None]
        ey += [pos[s][1], pos[t][1], None]
    fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines", hoverinfo="skip", showlegend=False,
                             line=dict(color="rgba(140,150,160,0.4)", width=1)))
    if detail:
        for s, t in E:
            fig.add_annotation(x=pos[t][0], y=pos[t][1], ax=pos[s][0], ay=pos[s][1],
                               xref="x", yref="y", axref="x", ayref="y", showarrow=True,
                               arrowhead=3, arrowsize=1, arrowwidth=1,
                               arrowcolor="rgba(120,130,140,0.6)", text="")
    for role, color in ROLE_COLORS.items():
        ns = [n for n in nodes if roles.get(n) == role]
        if not ns:
            continue
        fig.add_trace(go.Scatter(
            x=[pos[n][0] for n in ns], y=[pos[n][1] for n in ns],
            mode="markers+text" if detail else "markers",
            marker=dict(color=color, size=14, line=dict(color="white", width=1)),
            text=[labels.get(n, n)[:24] for n in ns], textposition="middle right",
            textfont=dict(size=10), name=role,
            hovertext=[labels.get(n, n) for n in ns], hoverinfo="text"))
    rows_max = max((len(v) for v in byr.values()), default=1)
    fig.update_layout(height=max(360, 30 * rows_max + 130), title=title,
                      margin=dict(l=10, r=10, t=44, b=30), plot_bgcolor="white",
                      legend=dict(orientation="h", y=1.08),
                      xaxis=dict(title="◀ leads · · · · · · propagation · · · · · · led by ▶",
                                 showgrid=False, zeroline=False, tickvals=sorted(byr),
                                 range=[-0.5, max(byr) + 1.2] if byr else [-1, 1]),
                      yaxis=dict(visible=False))
    return fig


# ---------------------------------------------------------------------------- app
def sidebar():
    st.sidebar.title("⚡ Signal Tool")
    st.sidebar.caption("Do metal inputs lead transformer prices?")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**What it does** · Finds which economic signals genuinely lead US transformer prices, "
        "and rejects the false ones. Full guide and the tab map are at the top of the page.")
    st.sidebar.caption("Source: FRED (monthly), precomputed. Outcome: PCU335311335311.")


def main():
    sidebar()
    # Make the tab labels read as prominent, obviously-clickable buttons.
    st.markdown(
        "<style>"
        ".stTabs [data-baseweb='tab-list'] { gap: 6px; }"
        ".stTabs [data-baseweb='tab'] { padding: 10px 18px; }"
        ".stTabs [data-baseweb='tab'] [data-testid='stMarkdownContainer'] p,"
        ".stTabs [data-baseweb='tab'] p { font-size: 1.18rem; font-weight: 700; }"
        "</style>", unsafe_allow_html=True)
    st.title("Transformer leading-signal dashboard")

    if not outputs_exist():
        st.warning("No precomputed results found in `outputs/`. This deployment expects the "
                   "committed result files; regenerate them locally with `python3 run_pipeline.py`.")
        st.stop()

    board, inter, details = load_outputs()

    clusters_json, ctrl_df, force_df = load_analysis()

    # Plain-language guide (what the tool does + how to read the tabs), then the verdict tally.
    st.markdown(
        "This tool screens roughly 400 economic signals to find which genuinely **lead US "
        "transformer prices** (FRED PPI `PCU335311335311`), and rejects the false ones. Each "
        "signal is tested on year-over-year changes across a two-year lead/lag window, then must "
        "clear four hurdles to count as a real lead: **survive smoothing** (not noise), **hold "
        "across eras** and not depend on one episode, **keep its edge after the broad commodity "
        "cycle is removed** (not just riding commodity prices), and be **statistically "
        "significant**. Correlated signals are grouped into \"forces,\" so five copper series "
        "count as one witness, not five. Use the tabs below: **Screen** (each item's checks), "
        "**Correlation** (how signals and forces relate, plus the groupings), **Lead-lag map** "
        "(which signals lead which others), **Compare** (every verdict side by side).")

    st.markdown(header_tiles_html(board), unsafe_allow_html=True)
    _summed = int(sum(int((board["verdict"] == k).sum()) for _, k in VERDICT_TILES))
    st.caption(f"Every screened signal lands in exactly one verdict — the nine verdict tiles "
               f"sum to **{_summed}** = the {len(board)} signals tested.")

    tab_screen, tab_corr, tab_leadlag, tab_compare = st.tabs(
        ["🔬 Screen", "🔗 Correlation", "🗺️ Lead-lag map", "🏆 Compare"])

    catalog = build_force_catalog(clusters_json, force_df)
    bloc_catalog = build_force_catalog(load_clusters_loose(), load_bloc_leaderboard())

    def pick_signal(key):
        order = list(board["fred_id"])
        return st.selectbox("🔹 Signal", order, key=key,
                            format_func=lambda c: f"{LABEL.get(c, c)}  ·  {details[c]['verdict']}")

    def _pick_group(cat, key, label, empty):
        if not cat:
            st.info(empty)
            return None
        keys = [c["key"] for c in cat]
        by = {c["key"]: c for c in cat}

        def _fmt(k):
            row = by[k].get("row")
            v = row["verdict"] if (row is not None and "verdict" in row) else None
            base = f"{by[k]['name']} · {len(by[k]['ids'])} signals"
            return f"{base}  ·  {v}" if v else base
        sel = st.selectbox(label, keys, key=key, format_func=_fmt)
        return by[sel]

    def pick_force(key):
        return _pick_group(catalog, key, "🔸 Force (tight ≥0.70 cluster → composite)",
                           "No multi-signal forces defined — run the pipeline.")

    def pick_bloc(key):
        return _pick_group(bloc_catalog, key, "🔶 Loose bloc (average-linkage → composite)",
                           "No multi-signal loose blocs defined — run the pipeline.")

    def _std_radio(key):
        return st.radio("Spread scale", ["Standardized (z-score)", "Raw %-pts"],
                        horizontal=True, key=key).startswith("Standardized")

    # ============================ CORRELATION ============================
    with tab_corr:
        st.caption(LAYER_REMINDER)
        st.subheader("🔹 Signal level — inter-signal correlation")
        if len(inter) <= 40:
            st.plotly_chart(heatmap_fig(inter), use_container_width=True, key="corr_heatmap")
        else:
            st.caption(f"{len(inter)}×{len(inter)} matrix — clustered heatmap (leaf order); full "
                       "values in `leading_signal_corr_matrix.csv`.")
            hp = os.path.join(OUT, "charts", "_clustered_heatmap.png")
            if os.path.exists(hp):
                st.image(hp, use_container_width=True)
        render_ladder_note()

        st.divider()
        st.subheader("🔸 Tight-force level — inter-force correlation (the cousin check)")
        if force_df is not None and "n_signals" in force_df:
            _sf = force_df[force_df.get("status", "scored") == "scored"] if "status" in force_df else force_df
            _tm = int((_sf["n_signals"] > 1).sum())
            _ts = int((_sf["n_signals"] == 1).sum())
            st.markdown(f"**{len(_sf)} tight forces** — {_tm} multi-signal clusters + {_ts} singletons "
                        "(each singleton is a force of size 1 = one independent witness).")
        fm = load_force_matrix()
        if fm is None or len(fm) < 2:
            st.info("Run the pipeline to generate `force_correlation_matrix.csv`.")
        else:
            st.plotly_chart(group_matrix_fig(fm, "Correlation between the TIGHT-FORCE composites"),
                            use_container_width=True, key="force_matrix")
            cous = cousin_pairs(fm)
            st.warning(f"**{len(cous)} cousin pair(s) at 0.50 ≤ |r| < 0.70** — distinct tight forces "
                       "that still co-move (just under the 0.70 cut). Cohesive, but **cousins remain**, "
                       "so the force **count is not a count of independent bets**.")

        with st.expander("How the tight forces are defined — complete-linkage clustering", expanded=False):
            st.markdown("**Complete linkage** makes every cluster *tight* — every pair ≥ 0.70 — so no "
                        "loose grab-bag forms (the copper/non-ferrous core stays separate from "
                        "steel/GOES, aluminium mill stands alone). Cohesive, but more/smaller groups "
                        "can still be **cousins** (0.5–0.7).")
            render_clustering(clusters_json,
                              os.path.join(OUT, "charts", "_dendrogram.png"),
                              os.path.join(OUT, "charts", "_clustered_heatmap.png"), "witness")

        st.divider()
        st.subheader("🔶 Loose-bloc level — inter-bloc correlation (most independent, coarser)")
        _blb = load_bloc_leaderboard()
        if _blb is not None and "n_signals" in _blb:
            _bs = _blb[_blb.get("status", "scored") == "scored"] if "status" in _blb else _blb
            _lm = int((_bs["n_signals"] > 1).sum())
            _lk = int((_bs["n_signals"] == 1).sum())
            st.markdown(f"**{len(_bs)} loose blocs** — {_lm} clusters + {_lk} singletons.")
        bm = load_bloc_matrix()
        if bm is None or len(bm) < 2:
            st.info("Run the pipeline to generate `bloc_correlation_matrix.csv`.")
        else:
            st.caption("Average linkage merges **same-sign cousins** into bigger blocs (opposite-sign "
                       "grab-bags still split). Fewer, coarser groups — and lower cross-correlation.")
            st.plotly_chart(group_matrix_fig(bm, "Correlation between the LOOSE-BLOC composites"),
                            use_container_width=True, key="bloc_matrix")
            bcous = cousin_pairs(bm)
            st.warning(f"**{len(bcous)} cousin pair(s)** among loose blocs — fewer than at the tight "
                       "level, because merging cousins removed the near-0.70 pairs.")

        with st.expander("How the loose blocs are defined — average-linkage clustering", expanded=False):
            st.markdown("**Average linkage** merges same-sign cousins into bigger blocs (opposite-sign "
                        "grab-bags are still split out as incoherent, not averaged). Fewer, coarser, "
                        "more independent groups — lower cross-correlation than the tight forces.")
            render_clustering(load_clusters_loose(),
                              os.path.join(OUT, "charts", "_dendrogram_loose.png"),
                              os.path.join(OUT, "charts", "_clustered_heatmap_loose.png"), "bloc")

        st.divider()
        st.caption("Either way, the **partial-r market control** (Screen tab) is the real "
                   "independence check — the inter-group matrix shows co-movement, the partial r "
                   "shows whether a group adds transformer-specific information beyond the cycle.")

    # =================== SCREEN — everything about one item, in one place ===================
    with tab_screen:
        st.caption(LAYER_REMINDER)
        st.markdown("Each item reads top-to-bottom: **gates → cycle graph → chart → data.** "
                    "The 🔹 signal, 🔸 tight-force and 🔶 loose-bloc layers run the identical checks "
                    "at coarser and coarser aggregation.")

        # ------------------------------- 🔹 SIGNAL -------------------------------
        st.subheader("🔹 Signal level")
        cid = pick_signal("screen_sig")
        d = details[cid]
        st.info(f"**Mechanism.** {MECH.get(cid, '')}")
        a = analyze(P.yoy(load_level(cid)))

        st.markdown("**① Gates · sharpness · market control**")
        render_screen_panel(a, verdict=d.get("verdict"), perm_q=d.get("perm_q"),
                            extra_short=(d.get("short_note") if d.get("short_sample") == "yes" else None))

        st.markdown("**② Cycle graph — raw r vs cycle-controlled partial r**")
        gL, gR = st.columns(2)
        gL.plotly_chart(raw_partial_bar_fig(a, LABEL.get(cid, cid)), use_container_width=True,
                        key=f"sig_rawpartial_{cid}")
        df_s, meta, lead_k = spread_data_signal(cid, a["lead"])
        gR.plotly_chart(spread_fig(df_s, meta, LABEL.get(cid, cid), lead_k,
                        standardize=_std_radio("screen_sig_scale")), use_container_width=True,
                        key=f"sig_spread_{cid}")
        if ctrl_df is not None:
            with st.expander("Aggregate cycle-control — all confirmed signals (raw vs partial r)"):
                st.plotly_chart(cycle_bar_fig(ctrl_df), use_container_width=True, key="sig_cyclebar")

        st.markdown("**③ Chart — level / YoY / 2nd-derivative / lag**")
        st.plotly_chart(levels_fig(cid), use_container_width=True, key=f"sig_levels_{cid}")
        cL, cR = st.columns(2)
        cL.plotly_chart(yoy_fig(cid), use_container_width=True, key=f"sig_yoy_{cid}")
        cR.plotly_chart(yoy2_fig(cid), use_container_width=True, key=f"sig_yoy2_{cid}")
        st.plotly_chart(lag_fig(cid, details), use_container_width=True, key=f"sig_lag_{cid}")

        st.markdown("**④ Data — raw observations & three views**")
        tbl = build_data_table(cid)
        st.caption(f"{tbl.notna().any(axis=1).sum()} monthly rows · "
                   f"{tbl.index.min().date()} → {tbl.index.max().date()} · outer join.")
        nf = st.checkbox("Newest first", True, key="screen_sig_newest")
        st.dataframe(tbl.sort_index(ascending=not nf), use_container_width=True, height=320)
        st.download_button("⬇ Download signal table (CSV)", tbl.to_csv().encode("utf-8"),
                           file_name=f"{cid}_views.csv", mime="text/csv", key="dl_sig")

        # Shared renderer for a GROUP (tight force OR loose bloc) — identical battery.
        def render_group_screen(g, prefix, one_word, icon):
            gv = g["row"]["verdict"] if (g["row"] is not None and "verdict" in g["row"]) else None
            if gv:
                badge = (f"<span style='background:{VERDICT_BG.get(gv, '#eee')};"
                         f"color:{VERDICT_COLORS.get(gv, '#000')};padding:1px 9px;border-radius:5px;"
                         f"font-weight:700;font-size:0.8em'>{gv}</span>")
                st.markdown(f"#### {icon} {one_word} — {g['name']}  ·  {badge}", unsafe_allow_html=True)
            else:
                st.markdown(f"#### {icon} {one_word} — {g['name']}")
            st.caption(f"Composite of {len(g['ids'])} members: "
                       + ", ".join(LABEL.get(m, m).split(" (")[0] for m in g["ids"]))
            comp = force_composite_yoy(tuple(g["ids"]))
            ga = analyze(comp)
            st.markdown("**① Gates · sharpness · market control**")
            render_screen_panel(ga, verdict=gv)
            st.markdown("**② Cycle graph — raw r vs cycle-controlled partial r**")
            c1, c2 = st.columns(2)
            c1.plotly_chart(raw_partial_bar_fig(ga, g["name"]), use_container_width=True,
                            key=f"{prefix}_rawpartial")
            df_g, meta_g, lead_g = spread_data_force(tuple(g["ids"]))
            c2.plotly_chart(spread_fig(df_g, meta_g, g["name"], lead_g,
                            standardize=_std_radio(f"{prefix}_scale")), use_container_width=True,
                            key=f"{prefix}_spread")
            st.markdown("**③ Chart — composite YoY & lag**")
            st.plotly_chart(yoy_overlay_fig(comp, g["name"]), use_container_width=True,
                            key=f"{prefix}_yoyoverlay")
            st.plotly_chart(lag_curve_fig(ga["curve"], ga["peak"],
                            title=f"{one_word} composite lag correlation  (+k = {one_word.lower()} leads)"),
                            use_container_width=True, key=f"{prefix}_lag")
            st.markdown("**④ Data — equal-weighted composite views**")
            gtbl = force_data_table(g["ids"])
            nfg = st.checkbox("Newest first", True, key=f"{prefix}_newest")
            st.dataframe(gtbl.sort_index(ascending=not nfg), use_container_width=True, height=320)
            st.download_button("⬇ Download composite table (CSV)", gtbl.to_csv().encode("utf-8"),
                               file_name=f"{prefix}_composite_views.csv", mime="text/csv",
                               key=f"dl_{prefix}")

        st.divider()
        # ------------------------------- 🔸 TIGHT FORCE -------------------------------
        st.subheader("🔸 Tight-force level — identical battery on the composite")
        f = pick_force("screen_force")
        if f:
            render_group_screen(f, "screen_force", "Force", "🔸")

        st.divider()
        # ------------------------------- 🔶 LOOSE BLOC -------------------------------
        st.subheader("🔶 Loose-bloc level — identical battery on the composite")
        bl = pick_bloc("screen_bloc")
        if bl:
            render_group_screen(bl, "screen_bloc", "Bloc", "🔶")

        st.caption("The **cycle graph** (left) is the raw lead-r beside the market-controlled "
                   "partial r — a tall raw bar collapsing to a near-zero partial = cycle-driven, "
                   "identically for a signal and a force. The **spread** (right) = series − β·market "
                   "on both sides; its correlation *equals* that partial r.")
        st.info("**‘Cycle-driven’ means the cycle removed a *real* edge** — the correlation was "
                "strong on its own (raw) and fell by ≥0.15 to a weak partial. An item that was "
                "already weak (raw ≈ partial, small drop) is labelled *‘not cycle-driven (weak on "
                "its own)’*, and is **not** downgraded to STRONG BUT CYCLE-DRIVEN — the cycle "
                "explained nothing there.")

    # =============================== LEAD-LAG MAP ===============================
    with tab_leadlag:
        st.caption(LAYER_REMINDER)
        st.markdown("Everything else measures **item → transformer**; this maps **item → item** "
                    "to expose the *propagation chain*. A directed edge **A → B** is kept only if "
                    "A is a **genuine lead** of B: lag ≥ 1, |r| ≥ 0.50, and a real lead-sharpness "
                    "gain over lag 0 (co-mover check). Flow is left→right: "
                    "🟢 **sources** (lead, not led) · 🔵 **relays** · 🔴 **sinks** (led, lead nothing). "
                    "Read-only — it changes no scoring.")

        def render_leadlag(edges, layer, tname="Transformer PPI"):
            if edges is None or len(edges) == 0:
                st.info("Run the pipeline to generate the lead-lag edges.")
                return
            role, ind, outd, labels = leadlag_roles(edges)
            # transformer node id: the one whose label is the transformer
            tid = next((n for n, lb in labels.items() if lb == tname), None)
            # summary line
            if tid is not None:
                led_by = int(ind.get(tid, 0))
                leads = int(outd.get(tid, 0))
                pure = (leads == 0 and led_by > 0)
                st.markdown(f"**What leads transformer.** Transformer PPI is led by **{led_by}** "
                            f"{layer}(s) and leads **{leads}** → "
                            + ("**pure sink ✓** (led by many, leads nothing) — the terminal end of "
                               "the propagation chain." if pure
                               else f"the {leads} it appears to lead are **later-stage output / "
                               "macro / financial series that lag it** (see the full edge table), "
                               "not its material inputs. Within the input→transformer chain shown "
                               "below it is still the **terminal sink** (rightmost node)."))
                direct = (edges[edges["target_id"] == tid]
                          .sort_values("r", key=lambda s: s.abs(), ascending=False).head(8))
                if len(direct):
                    st.markdown("Direct leaders (strongest first): "
                                + " · ".join(f"**{d['source']}** ({d['r']:+.2f} @ +{int(d['lag'])}m)"
                                             for _, d in direct.iterrows()))
            # graph: default to transformer's propagation chain (its ancestors) for readability
            full_nodes = set(edges["source_id"]) | set(edges["target_id"])
            show_full = st.checkbox(f"Show the full {layer} graph ({len(full_nodes)} nodes) "
                                    "instead of just the transformer chain",
                                    value=(len(full_nodes) <= 14), key=f"ll_full_{layer}")
            if show_full or tid is None:
                nodes = full_nodes
            else:
                nodes = leadlag_ancestors(edges, tid) | {tid}
            st.plotly_chart(leadlag_fig(edges, nodes, labels, role,
                            title=f"{layer.capitalize()} propagation → transformer"),
                            use_container_width=True, key=f"leadlag_{layer}")
            # full edge table
            with st.expander(f"Full edge table — {len(edges)} genuine-lead edges"):
                et = edges.rename(columns={"source": "Leads (A)", "target": "→ B",
                                           "lag": "Lag (mo)", "r": "r", "gain": "Gain vs lag0",
                                           "n": "n"})[["Leads (A)", "→ B", "Lag (mo)", "r",
                                                       "Gain vs lag0", "n"]]
                st.dataframe(et.sort_values("r", key=lambda s: s.abs(), ascending=False),
                             use_container_width=True, hide_index=True, height=340)

        st.subheader("🔹 Signal level — individual signals")
        render_leadlag(load_leadlag("signal"), "signal")
        st.divider()
        st.subheader("🔸 Tight-force level — force composites")
        render_leadlag(load_leadlag("force"), "force")
        st.divider()
        st.subheader("🔶 Loose-bloc level — bloc composites")
        render_leadlag(load_leadlag("bloc"), "bloc")

    # ==================== COMPARE — identical columns, signal ↔ force ====================
    with tab_compare:
        st.caption(LAYER_REMINDER)
        st.markdown(verdict_strip_html(board), unsafe_allow_html=True)
        st.markdown("Every column that drives a verdict is on the table and **failures shout in "
                    "color** — a plain-language **Why** gives the one binding reason, gates show "
                    "✅ or a red **❌ NO**, and Cycle flags cycle-driven rows. No verdict needs the "
                    "row opened. All three tables share the identical layout so rows line up 1:1.")
        render_ladder_note()

        st.divider()
        st.subheader("🔹 Signal level — signal leaderboard")
        fcol1, fcol2 = st.columns([2, 3])
        verd_opts = list(board["verdict"].unique())
        pick = fcol1.multiselect("Filter verdict", verd_opts, default=verd_opts, key="cmp_verd")
        qq = fcol2.text_input("Search signal / category", "", key="cmp_q")
        view = board[board["verdict"].isin(pick)]
        if qq:
            mm = view["signal"].str.contains(qq, case=False, na=False)
            if "category" in view:
                mm = mm | view["category"].astype(str).str.contains(qq, case=False, na=False)
            view = view[mm]
        st.caption(f"{len(view)} of {len(board)} signals shown")
        st.dataframe(style_compare(compare_frame(view, "signal")),
                     use_container_width=True, hide_index=True)
        legend = "  ".join(
            f"<span style='background:{VERDICT_BG.get(v,'#fff')};color:{VERDICT_COLORS.get(v,'#000')};"
            f"padding:2px 8px;border-radius:4px;font-weight:600'>{v}</span>"
            for v in ["CONFIRMED", "STRONG BUT CYCLE-DRIVEN", "CO-MOVER (not a lead)",
                      "CO-MOVER (cycle-driven)", "SHORT-SAMPLE (unverified)",
                      "PARTIAL / INCONCLUSIVE", "STRONG / NOT ROBUST", "REVERSED", "REJECTED"])
        st.markdown(legend, unsafe_allow_html=True)

        st.divider()
        st.subheader("🔸 Tight-force level — force leaderboard (one row per witness)")
        if force_df is None:
            st.warning("Run the pipeline to generate the force leaderboard.")
        else:
            scored = force_df[force_df.get("status", "scored") == "scored"] if "status" in force_df else force_df
            fv_opts = list(pd.unique(scored["verdict"].dropna())) if "verdict" in scored else []
            fpick = st.multiselect("Filter verdict", fv_opts, default=fv_opts, key="cmp_fverd")
            fview = scored[scored["verdict"].isin(fpick)] if fv_opts else scored
            fview = sort_by_verdict(fview, "raw_r")
            singles = int((fview["n_signals"] == 1).sum()) if "n_signals" in fview else 0
            multis = int((fview["n_signals"] > 1).sum()) if "n_signals" in fview else 0
            st.caption(f"{len(fview)} tight forces shown — {multis} clusters + {singles} singletons "
                       "(each singleton is a force of size 1 = one independent witness).")
            st.dataframe(style_compare(compare_frame(fview, "force")),
                         use_container_width=True, hide_index=True)
            st.caption("Cohesive (every pair ≥0.70) but **cousins remain** — see the inter-force "
                       "matrix on the Correlation tab.")

        st.divider()
        st.subheader("🔶 Loose-bloc level — bloc leaderboard (most independent, coarser)")
        bloc_df = load_bloc_leaderboard()
        if bloc_df is None:
            st.warning("Run the pipeline to generate `loose_bloc_cycle_control.csv`.")
        else:
            bscored = bloc_df[bloc_df.get("status", "scored") == "scored"] if "status" in bloc_df else bloc_df
            bscored = sort_by_verdict(bscored, "raw_r")
            bmul = int((bscored["n_signals"] > 1).sum()) if "n_signals" in bscored else 0
            bsin = int((bscored["n_signals"] == 1).sum()) if "n_signals" in bscored else 0
            st.caption(f"{len(bscored)} loose blocs — {bmul} merged blocs + {bsin} singletons. "
                       "Average linkage merges same-sign cousins into bigger blocs (opposite-sign "
                       "grab-bags still split), so there are **fewer, more independent** groups.")
            st.dataframe(style_compare(compare_frame(bscored, "force")),
                         use_container_width=True, hide_index=True)
            st.caption("Same identical columns. The ladder is **signals → tight forces → loose "
                       "blocs**; partial-r (Screen) and the inter-group matrix (Correlation) stay "
                       "the real independence check at every rung.")


if __name__ == "__main__":
    main()
