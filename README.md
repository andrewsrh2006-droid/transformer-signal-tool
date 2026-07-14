# Transformer Leading-Signal Dashboard

Interactive Streamlit dashboard that tests which industrial input prices (copper, grain-oriented electrical steel, aluminum, wire, …) **lead** the U.S. Producer Price Index for power & specialty transformer manufacturing (FRED `PCU335311335311`) — by how many months, and how trustworthy each lead is.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Entry point: **`app.py`**.

The dashboard is **fully offline**: it reads precomputed results from `outputs/` and cached FRED CSVs from `data/raw/`, both committed in this repo. No API key and no network calls at runtime, so it starts in seconds and stays within Streamlit Community Cloud's memory limits.

## What it shows

Three tabs, all rendered from the committed `outputs/`:

- **🔬 Screen** — everything about one signal / force / bloc: peak lead/lag, the disqualifying robustness gates (smoothing, holds-over-time, 3-year-block episode jackknife), FDR *q* / bootstrap CI, and the market-cycle control, with a verdict.
- **🔗 Correlation** — at each level (signal / tight-force / loose-bloc), the **lead-lag propagation map** (which signals lead which others) above the **co-movement matrix** that collapses redundant signals into independent "forces," plus the clustering dendrograms.
- **🏆 Compare** — every verdict side by side in one colour-coded transparency table.

Verdicts and the full ranking live in `outputs/leaderboard.csv` / `outputs/leaderboard.md`.

**📘 For the complete methodology — every gate, the correlation math, the verdict taxonomy, all thresholds, and how to reproduce or re-point the whole site — see [`BUILD_GUIDE.md`](BUILD_GUIDE.md).**

## Regenerating the results (optional, developer step)

The committed files in `outputs/` are produced offline from the cached CSVs in `data/raw/`:

```bash
python3 run_pipeline.py
```

This runs the heavy permutation/bootstrap and clustering (~15 min) and is **not** invoked by the dashboard. Fetching new series from FRED requires a `FRED_API_KEY` environment variable; it is never stored in the repo.
