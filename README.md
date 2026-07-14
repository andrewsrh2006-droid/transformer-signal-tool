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

- **Screen** — per-signal peak lead/lag, the disqualifying robustness gates (smoothing, holds-over-time, 3-year-block episode jackknife), permutation *p* / bootstrap CI, and market-cycle control, with a verdict per signal.
- **Correlation** — correlation-of-correlations heatmap that collapses redundant signals into independent "forces."
- **Lead–lag**, **Compare**, and **Groups** tabs for the network of leads and the clustering ladder.

Verdicts and the full ranking live in `outputs/leaderboard.csv` / `outputs/leaderboard.md`.

## Regenerating the results (optional, developer step)

The committed files in `outputs/` are produced offline from the cached CSVs in `data/raw/`:

```bash
python3 run_pipeline.py
```

This runs the heavy permutation/bootstrap and clustering (~15 min) and is **not** invoked by the dashboard. Fetching new series from FRED requires a `FRED_API_KEY` environment variable; it is never stored in the repo.
