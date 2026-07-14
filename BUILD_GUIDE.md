# Build Guide — Transformer Leading-Signal Dashboard

A complete, self-contained reference for **what this site is, how it is built, how every
statistical gate and correlation works, and how to reproduce or re-deploy it from scratch.**
If you have this repository and this document, you can copy the site, regenerate its results,
re-point it at a different outcome, or hand it to another agent and have them do the same.

---

## Table of contents

1. [The question this answers](#1-the-question-this-answers)
2. [How the site is put together (architecture)](#2-how-the-site-is-put-together-architecture)
3. [Quick start — run and deploy](#3-quick-start--run-and-deploy)
4. [Repository layout](#4-repository-layout)
5. [The data](#5-the-data)
6. [Methodology, step by step](#6-methodology-step-by-step)
   - 6.1 [Transform: year-over-year](#61-transform-year-over-year)
   - 6.2 [Lead-lag correlation](#62-lead-lag-correlation)
   - 6.3 [Lead classification (true lead / co-mover / reversed)](#63-lead-classification-true-lead--co-mover--reversed)
   - 6.4 [The three robustness gates](#64-the-three-robustness-gates)
   - 6.5 [Statistical significance (permutation q + bootstrap CI)](#65-statistical-significance-permutation-q--bootstrap-ci)
   - 6.6 [Short-sample guardrail](#66-short-sample-guardrail)
   - 6.7 [Market-cycle control (partial correlation)](#67-market-cycle-control-partial-correlation)
   - 6.8 [Grouping correlated signals into forces and blocs](#68-grouping-correlated-signals-into-forces-and-blocs)
   - 6.9 [The lead-lag propagation map](#69-the-lead-lag-propagation-map)
7. [The verdict taxonomy (the heart of the tool)](#7-the-verdict-taxonomy-the-heart-of-the-tool)
8. [Every threshold in one table](#8-every-threshold-in-one-table)
9. [The dashboard (app.py)](#9-the-dashboard-apppy)
10. [Regenerating the results](#10-regenerating-the-results)
11. [Output-file reference](#11-output-file-reference)
12. [Adapting the tool to a different outcome](#12-adapting-the-tool-to-a-different-outcome)

---

## 1. The question this answers

**Which economic signals genuinely _lead_ U.S. transformer prices, by how many months, and
how trustworthy is each lead?**

- **Outcome (the thing predicted):** FRED series `PCU335311335311` — Producer Price Index for
  Electric Power & Specialty Transformer Manufacturing.
- **Candidates:** ~400 monthly economic series — metal prices (copper, aluminium, steel,
  nickel, zinc…), energy (crude, gas, electricity), freight, grid-demand and construction,
  labour, macro activity, and financial/forward series.
- **The job:** for each candidate, find the lag at which it best correlates with the outcome,
  then subject that correlation to a battery of robustness and significance tests, and assign a
  single **verdict** describing the _kind_ of relationship (leads / co-moves / reverses /
  nothing) and its _quality_ (confirmed / cycle-driven / fragile / not significant).

The core intellectual point: **a high correlation is not a lead.** A signal can correlate
strongly yet be (a) contemporaneous rather than leading, (b) merely riding the broad commodity
cycle, (c) an artefact of one short window, or (d) statistically indistinguishable from chance.
The tool's value is separating a real, tradeable lead from each of those look-alikes.

---

## 2. How the site is put together (architecture)

There are two completely separate halves, connected only by a folder of committed result files:

```
   ┌─────────────────────────────┐        ┌──────────────────┐        ┌────────────────────────┐
   │  OFFLINE PIPELINE           │        │  COMMITTED       │        │  DASHBOARD             │
   │  run_pipeline.py            │  ───▶  │  outputs/*.csv   │  ───▶  │  app.py (Streamlit)    │
   │  + signal_tool/*.py         │ writes │  outputs/*.json  │ reads  │  reads only, no stats  │
   │  heavy: permutation,        │        │  outputs/charts  │        │  renders tables/plots  │
   │  bootstrap, clustering      │        │  (399 PNGs)      │        │  starts in seconds     │
   │  ~15 min run                │        └──────────────────┘        └────────────────────────┘
   └─────────────────────────────┘
            ▲
            │ reads cached CSVs
   ┌────────┴─────────┐
   │  data/raw/*.csv  │  ~517 FRED series, committed (no network at runtime)
   └──────────────────┘
```

**Why this split matters:**

- The **dashboard is fully offline and stateless.** It performs no statistics, makes no FRED
  calls, and needs no API key. It reads the precomputed `outputs/` files and renders them. This
  is what lets it deploy to Streamlit Community Cloud, start in seconds, and stay inside the
  memory limit.
- The **pipeline is a developer step**, run rarely (when data or methodology changes). It does
  all the expensive work — the permutation null, the bootstrap, the clustering — and writes the
  result files that get committed to git.
- Because results are committed, **the repo is the source of truth**: what you see on the site is
  exactly what is in `outputs/`, reproducible from `data/raw/` by re-running the pipeline.

**Tech stack:** Python 3.11+, Streamlit (UI), pandas/numpy (data), plotly (interactive charts),
scipy (hierarchical clustering), matplotlib (the offline PNGs). No database, no server-side
state, no external services at runtime.

---

## 3. Quick start — run and deploy

### Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. Reads the committed `outputs/` and `data/raw/` — nothing else
required.

### Deploy to Streamlit Community Cloud

1. Push the repo to GitHub (public or private).
2. Go to **[share.streamlit.io](https://share.streamlit.io)** → sign in with GitHub → **Create
   app** → **Deploy a public app from GitHub**.
3. Set **Repository** = your repo, **Branch** = `main`, **Main file path** = `app.py`.
4. (Optional) Advanced settings → pin **Python 3.12**.
5. **Deploy.** It installs from `requirements.txt` automatically. **No secrets/API keys needed**
   (the app is offline). Every future `git push` to `main` auto-redeploys.

First build takes a few minutes (it clones the ~56 MB repo including the 399 committed chart
PNGs). After that the workflow is simply *edit → commit → push*.

---

## 4. Repository layout

```
app.py                     # THE DASHBOARD — the only file needed at runtime. ~1600 lines.
run_pipeline.py            # THE PIPELINE — regenerates everything in outputs/. Developer-only.
requirements.txt           # runtime + pipeline deps
README.md                  # short readme
BUILD_GUIDE.md             # this document

signal_tool/               # the analysis library (imported by run_pipeline.py; app.py uses a few helpers)
├── config.py              # series catalogue (outcome, ~400 candidates, market control) + ALL thresholds
├── process.py             # YoY transform, alignment
├── correlate.py           # lag correlation, peak finding, lead-sharpness classification
├── screen.py              # the 3 robustness GATES (smoothing / holds / episode) + second-opinion support
├── significance.py        # permutation p-value, Benjamini-Hochberg FDR q, block-bootstrap CI
├── history.py             # short-sample flag + window-artifact check
├── control.py             # market-cycle control: partial correlation, is_cycle_driven, survival
├── cluster.py             # hierarchical clustering of the correlation matrix into forces/blocs
├── leadlag.py             # directed "A leads B" propagation edges
├── matrix.py              # correlation-of-correlations helpers
├── leaderboard.py         # verdict() logic + verdict ranking + leaderboard assembly  ← the taxonomy
├── fred.py                # FRED fetch (only used when harvesting NEW series; needs FRED_API_KEY)
└── signals_extra.csv      # machine-generated manifest of the 364 expansion candidates

data/
├── raw/                   # ~517 cached FRED series CSVs (committed; read by the pipeline)
└── metadata.json          # per-series metadata

outputs/                   # COMMITTED RESULTS — what the dashboard reads (see §11)
├── leaderboard.csv/.md    # the ranked per-signal verdicts
├── pair_details.json      # full per-signal detail (gates, permutation, bootstrap, control)
├── *_cycle_control.csv    # force / bloc composite results
├── *_correlation_matrix.csv, clusters*.json, *_tiers.csv, *_splits.csv
├── lead_lag_edges*.csv    # propagation edges (signal / force / bloc)
└── charts/                # 399 precomputed PNGs (per-pair charts, dendrograms, heatmaps)

tools/                     # data-harvesting utilities (build_manifest, fred_harvest, …) — dev-only
```

---

## 5. The data

- **Source:** FRED (Federal Reserve Economic Data), monthly series. All series used are cached as
  CSVs under `data/raw/` and committed, so the pipeline and dashboard both run with **no network
  access**.
- **Outcome:** `PCU335311335311` (transformer PPI). Defined in `signal_tool/config.py` as
  `OUTCOME`.
- **Candidates:** defined in two places — a hand-written seed set of ~30 in `config.py::CANDIDATES`
  (each with a written _mechanism_ explaining why it might lead transformers), plus 364 more loaded
  from `signal_tool/signals_extra.csv` (machine-generated by `tools/build_manifest.py`). Total ≈ 400.
- **Market control:** `PPIACO` (All-commodities PPI), defined as `MARKET`. This is **not** a
  candidate — it is the broad commodity-cycle proxy that the cycle control strips out (see §6.7).
- **Fetching new series** (developer-only) uses `signal_tool/fred.py` and requires a
  `FRED_API_KEY` environment variable. It is never stored in the repo (`.gitignore` blocks
  `.env`, `*.key`, `.streamlit/secrets.toml`).

Each candidate carries a mechanism string and an a-priori `group` tag (copper, steel, energy,
demand, financial…). **The group tag is commentary only** — the actual independence check is the
data-driven clustering (§6.8), never the hand tags.

---

## 6. Methodology, step by step

Everything below is implemented in `signal_tool/`. The pipeline runs these in order for every
candidate against the outcome. All correlations are **Pearson r** on aligned monthly series
(`signal_tool/correlate.py::pearson`), computed on the inner-join of the two series' common
months (no interpolation, no fill).

### 6.1 Transform: year-over-year

`signal_tool/process.py::yoy`

Every level series is converted to a **year-over-year change** before any correlation:

- **Strictly-positive series** (prices, indices, yields): percent change
  `(x_t / x_{t-12} − 1) × 100`.
- **Zero-crossing series** (yield-curve spreads like 10y−2y, regional-Fed diffusion indices):
  a percent change is meaningless near zero, so a **12-month level difference** `x_t − x_{t−12}`
  is used instead. Pearson r is scale-invariant, so mixing the two transforms across series is
  fine; the choice is per-series and automatic (triggered when any value ≤ 0).

The 12-month transform cancels seasonality. Series are month-start dated, so a 12-row shift is
exactly 12 months.

### 6.2 Lead-lag correlation

`signal_tool/correlate.py`

**Convention:** positive lag `k` means the **candidate leads** the outcome. We correlate
`candidate_t` with `outcome_{t+k}`.

- We sweep `k` from **−24 to +24 months** (`MAX_LAG = 24`, 49 lags) and compute r at each lag
  with enough overlap (`min_n = 4`). This is the **lag curve**.
- The **peak** is the lag with the largest **|r|** (`peak_from_curve`). The peak's `(lag, r, n)`
  is the headline: peak lag = the lead in months, peak r = the strength.

Because the peak is chosen over 49 lags, the multi-lag search is a source of selection bias — the
significance test (§6.5) is specifically built to correct for it.

### 6.3 Lead classification (true lead / co-mover / reversed)

`signal_tool/correlate.py::lead_sharpness`

The peak's _position_ decides the **kind** of relationship. Let `gain = |peak r| − |r at lag 0|`
and `COMOVER_MAX_LAG = 2`, `min_gain = 0.05`:

| Class | Condition | Meaning |
|---|---|---|
| **true lead** | peak lag ≥ +1 **and** gain ≥ 0.05 | leads forward and clearly beats lag 0 |
| **co-mover** | peak within ±2 of lag 0 **and** gain < 0.05 | moves _with_ the outcome, not ahead |
| **lags / reversed** | peak lag ≤ −1 **and** (beyond ±2 **or** real gain) | the **outcome** moves first; the candidate trails |

The `is_comover` flag is set **only** for the co-mover case. This is important: a co-mover can be
wildly significant (a strong contemporaneous correlation), so significance alone never catches it
— the lead-position check does. A negative-lag peak that barely beats lag 0 within ±2 months is
treated as contemporaneous noise (co-mover), **not** a reversal; a reversal is reserved for the
outcome genuinely leading.

### 6.4 The three robustness gates

`signal_tool/screen.py`

A forward-lead correlation must survive all three gates to be trusted. Each gate targets a
different way a correlation can be spurious. (A pair only enters the gates if it leads —
peak lag ≥ 0 — and |peak r| ≥ 0.30.)

**Gate 1 — Smoothing** (`gate_smoothing`): is the correlation signal, or noise? Smooth **both**
YoY series with a **centered 6-month rolling mean** and recompute the peak. **Pass** if the
smoothed peak keeps the same **sign**, its lag is within **6 months** of the raw peak, and
|smoothed r| ≥ **0.30**. A correlation that only exists in the month-to-month jitter fails.

**Gate 2 — Holds over time** (`gate_holds_over_time`): did it work in every era, or just one?
Split the aligned-at-peak-lag pairs into an **early half and a late half**. The check is
**directional** — it punishes a relationship that was strong early and decayed. It **fails** if:

- late |r| < 0.20 (relationship gone recently), or
- late half sign-flips vs the full sample, or
- late |r| < 0.5 × early |r| (**collapse ratio**), or
- early |r| − late |r| > 0.30 (**max half-diff**, level collapse), or
- the early half strongly opposes the full sample (early |r| ≥ 0.20 with opposite sign = a
  reversal).

A relationship that _strengthened_ recently is allowed (only late-half weakness is punished).

**Gate 3 — Episode jackknife** (`gate_episode_jackknife`): does the whole correlation live in one
window? Partition history into **~3-year calendar blocks anchored so that 2020–2022 (the COVID
supercycle) is a single block**. Drop each block in turn and recompute r on the rest. **Fail** if
removing _any_ single block drops |r| below **0.30** (the floor). Needs ≥ 24 months and ≥ 2 blocks,
else it auto-passes with "history too short to jackknife". This complements Gate 2: the early/late
split can be fooled by a mid-sample episode straddling both halves, whereas leave-one-block-out
isolates any single episode the correlation depends on. (Archetype it catches: Retailers'
Inventories-to-Sales, peak −0.55 — drop 2020–2022 and it collapses to ≈ −0.16.)

`run_gates` returns `screen_pass = leads AND |r|≥0.30 AND smoothing AND holds AND episode`.

**Support (not a gate) — Second opinion** (`second_opinion`): counts _independent_ corroborators
— other candidates that lead with the same sign within 6 months at |r| ≥ 0.30 **and are not ≥0.70
correlated** with the target (a ≥0.70 partner is the same force, not an independent witness). This
adds confidence but never fails a signal.

### 6.5 Statistical significance (permutation q + bootstrap CI)

`signal_tool/significance.py`

Ordinary p-values are invalid here (heavy autocorrelation + a 49-lag search inflates them), so two
resampling procedures are used, and significance requires **both**.

**Permutation p-value** (`permutation_pvalue`): build surrogates by **circularly shifting the
outcome array** by a random offset (≥ `max_lag`, wrapping). This preserves each series' own
autocorrelation but destroys the cross-relationship. For each of **1000 surrogates** recompute the
**peak |r| over all lags** — so the multi-lag search is baked into the null. Then
`p = (# surrogates with peak|r| ≥ observed + 1) / (1000 + 1)`.

**Benjamini-Hochberg FDR q-value** (`benjamini_hochberg`): with ~400 candidates, p < 0.05 alone
yields ~5% of _all_ signals as lucky false positives. BH converts the vector of p-values into
**q-values** that control the expected false-discovery rate. A signal is **significant when
q < 0.05** (`SIG_ALPHA`). The dashboard's `q` column is this FDR q, not the raw p.

**Block-bootstrap CI** (`block_bootstrap_ci`): a **moving-block bootstrap** (block length 12
months, 2000 resamples) of r at the peak lag, reporting the **2.5 / 97.5 percentile** interval.
The CI **excludes zero** if the whole interval is on one side of 0.

> **The significance rule used everywhere:** an item is *significant* only if
> **FDR q < 0.05 AND the bootstrap CI excludes zero.** Failing either makes it "not significant"
> (could be chance). This is the exact rule in `leaderboard.py::verdict`.

### 6.6 Short-sample guardrail

`signal_tool/history.py`

A series with a short overlap can post a spectacular correlation that is really one big
2020–2022 supercycle filling its whole sample. Two defences:

- **Short-sample flag:** flag any signal with usable `n < 150 months` (`MIN_MONTHS`) **or** a
  sample starting after 2010 (`LATE_START`). A short signal is **excluded from CONFIRMED** unless a
  long, independent co-member of its ≥0.70 cluster (itself confirmed, pre-2010) corroborates it —
  and it is not a window artefact. Such signals get the `SHORT-SAMPLE (unverified)` verdict.
- **Window-artefact check** (`window_artifact_check`): re-measure a long generic benchmark (copper
  PPI, 1967-start) _restricted to the short signal's own window_. If the benchmark already scores
  ≈ the same correlation over that window (bench |r| ≥ 0.60 and the signal beats it by ≤ 0.10),
  the "edge" is the window, not the signal.

### 6.7 Market-cycle control (partial correlation)

`signal_tool/control.py`

Every metal rises and falls with a broad commodity super-cycle. A signal that correlates with
transformers only _because the whole complex is moving_ carries little unique information. At the
signal's measured lead lag `k` (aligning `signal_t`, `market_t`, `transformer_{t+k}`) we compute:

- **Raw r** — the headline lead correlation.
- **Partial r | market** — the same, statistically holding the broad commodity index constant:
  `r(X,Y|Z) = (r_XY − r_XZ·r_YZ) / √((1−r_XZ²)(1−r_YZ²))`, with X = signal, Y = transformer,
  Z = market (`PPIACO` YoY). This is the signal's **unique** co-movement with transformers after
  removing the cycle. (An equivalent beta-adjusted both-sides de-cycled spread is also computed and
  reproduces the partial r exactly; it's what a person could literally chart.)

**Is it cycle-driven?** (`is_cycle_driven`) — **True only when the cycle removed a _real_ edge**:
the partial is weak (|partial| < **0.20** = `PARTIAL_MIN`, or it flipped sign) **AND** the
correlation actually dropped by at least **0.15** (`CYCLE_DROP_MIN`) from raw to partial. An item
that was already weak on its own (raw ≈ partial, small drop) is **not** cycle-driven — the cycle
removed nothing.

**Survival label** (`_survival`), shown as the dashboard `Cycle` column:

| Label | Condition |
|---|---|
| `survives` | \|partial\| ≥ 0.30 |
| `partly survives` | 0.20 ≤ \|partial\| < 0.30 |
| `cycle-driven` | `is_cycle_driven` is true (weak partial **and** ≥ 0.15 drop) |
| `not cycle-driven (weak on its own)` → shown as **"raw weak"** | weak partial but small drop (the raw was weak to begin with) |

### 6.8 Grouping correlated signals into forces and blocs

`signal_tool/cluster.py`, `signal_tool/control.py::composite_yoy`

Many candidates measure the same underlying thing (five copper series). Counting them as five
independent leads would be double-counting. So signals are **clustered** from their
contemporaneous YoY correlation matrix:

- Distance `d = 1 − r` (r = 1 → 0, r = 0 → 1, r = −1 → 2). Cutting the dendrogram at
  `d = 1 − 0.70 = 0.30` gives clusters at the **0.70 correlation cut** (`CLUSTER_R`).
- **Two linkages, two levels:**
  - **Tight "forces" — complete linkage** (`CLUSTER_LINKAGE = "complete"`, production). Every pair
    in a cluster is ≥ 0.70, so clusters are tight by construction and no loose grab-bag forms
    (copper core stays separate from steel/GOES). More, smaller groups; some remain **cousins**
    (0.50 ≤ |r| < 0.70).
  - **Loose "blocs" — average linkage** (UPGMA). Merges same-sign cousins into bigger, coarser,
    more-independent blocs (opposite-sign grab-bags are still split as incoherent). Fewer groups,
    lower cross-correlation.
- A **force/bloc composite** is the **equal-weighted average of its members' YoY series**
  (inner-joined). Because members are ≥ 0.70 correlated, the average is a clean, lower-noise proxy
  for the shared force. The composite is then run through the _same_ lead-lag + cycle-control
  battery at its own peak lead (`force_cycle_control`). A member shorter than `FORCE_MIN_MONTHS`
  (150) is excluded from composite formation (one short member would truncate a decades-long
  force's window); it still appears individually.

The dashboard's Correlation tab shows the inter-force and inter-bloc matrices with the remaining
**cousin pairs** flagged — the reminder that the group _count_ is not a count of independent bets.

### 6.9 The lead-lag propagation map

`signal_tool/leadlag.py`

Everything above measures **item → transformer**. This measures **item → item** to expose the
propagation chain (e.g. steel scrap → steel → transformer). For every ordered pair (A, B) it finds
the positive lag `k ∈ 1..24` at which A best leads B, and keeps a directed edge **A → B** only if
it is a **genuine lead**: `k ≥ 1`, `|r| ≥ 0.50`, and lead-sharpness `gain ≥ 0.05` over lag 0 (the
same co-mover check — a pure co-mover is not an edge). Nodes are then coloured by role:
🟢 **source** (leads, not led) · 🔵 **relay** · 🔴 **sink** (led, leads nothing). It is a read-only
diagnostic and changes no scoring. Transformer PPI should be a **pure sink** — the terminal end of
the chain.

---

## 7. The verdict taxonomy (the heart of the tool)

`signal_tool/leaderboard.py::verdict` + `apply_cycle_control`

Every screened signal gets **exactly one verdict**, assigned by **relationship type first, then
quality**. Verdicts belong to **four relationship groups**. Define
`significant = (FDR q < 0.05) AND (bootstrap CI excludes zero)`.

### Decision procedure

```
if |peak r| < 0.30:                     →  REJECTED            (no relationship in any direction)

elif is_comover (peak near lag 0):      # CO-MOVER group
     if significant (or no q, e.g. a composite):  CO-MOVER (not a lead)
     else:                                        CO-MOVER (not significant)
     # then, if is_cycle_driven and it was CO-MOVER (not a lead):  CO-MOVER (cycle-driven)

elif peak lag < 0 (outcome leads):      # REVERSED group
     if significant (or no q):   REVERSED
     else:                       REVERSED (not significant)
     # then, if is_cycle_driven and it was REVERSED:  REVERSED (cycle-driven)

else:                                   # LEAD group (forward lead, lag ≥ 0, |r| ≥ 0.30)
     if |peak r| ≥ 0.50 (strong):
         if a robustness gate failed:          STRONG / NOT ROBUST
         elif significant:                     CONFIRMED
              # then, if is_cycle_driven:       STRONG BUT CYCLE-DRIVEN
         else:                                 STRONG / NOT SIGNIFICANT
     else (0.30 ≤ |r| < 0.50, moderate):       PARTIAL / INCONCLUSIVE

# Overlay (history.py): a strong forward lead on a short/late sample without a long
# corroborator, or a window artefact, is downgraded to  SHORT-SAMPLE (unverified).
```

### Key precedence rules

- **Relationship type is assigned first.** A co-mover or a reversal is named as such at _any_
  strength ≥ 0.30 — only a near-zero |r| is rejected. Strength grading (CONFIRMED / PARTIAL) applies
  only to genuine forward leads.
- **Significance outranks cycle-dependence.** `apply_cycle_control` splits a relationship into its
  `(cycle-driven)` variant _only_ when it is otherwise good (CONFIRMED, a significant CO-MOVER, or a
  significant REVERSED). Any `(not significant)` verdict is **terminal** — we don't interpret the
  cycle for a relationship that could be chance.
- **Cycle-driven requires a real drop**, not just a weak partial (§6.7). A signal that was weak on
  its own is not called cycle-driven.

### The full verdict set (ranked best → worst)

| # | Verdict | Group | Meaning |
|---|---|---|---|
| 0 | **CONFIRMED** | Lead | Strong forward lead, passes all gates, significant, survives the cycle. |
| 1 | **STRONG BUT CYCLE-DRIVEN** | Lead | Was CONFIRMED, but its partial |r| collapses once the commodity cycle is removed. |
| 2 | **STRONG / NOT ROBUST** | Lead | Strong & significant but fragile — fails a robustness gate (smoothing/holds/episode). |
| 3 | **STRONG / NOT SIGNIFICANT** | Lead | Strong, clears the gates, but q ≥ 0.05 or the CI spans zero — could be chance. |
| 4 | **SHORT-SAMPLE (unverified)** | Lead | Would be strong, but the sample is too short/late and no long series corroborates it. |
| 5 | **PARTIAL / INCONCLUSIVE** | Lead | Moderate forward lead (0.30 ≤ |r| < 0.50). |
| 6 | **CO-MOVER (not a lead)** | Co-mover | Significant co-movement (peak at lag 0) that survives the cycle — moves with, not ahead. |
| 7 | **CO-MOVER (cycle-driven)** | Co-mover | A significant co-mover whose partial collapses — the co-movement is just the cycle. |
| 8 | **CO-MOVER (not significant)** | Co-mover | The co-movement could be chance. |
| 9 | **REVERSED** | Reversed | A significant reversal — the outcome leads the candidate. |
| 10 | **REVERSED (cycle-driven)** | Reversed | A significant reversal whose partial collapses — the lag is just the cycle. |
| 11 | **REVERSED (not significant)** | Reversed | The reversal could be chance. |
| 12 | **REJECTED** | Rejected | |peak r| < 0.30 — no relationship in any direction. |

`VERDICT_RANK` (this order) sorts every leaderboard and table.

---

## 8. Every threshold in one table

All defined in `signal_tool/config.py` unless noted.

| Constant | Value | Role |
|---|---|---|
| `MAX_LAG` | 24 | ± lag search window (months); 49 lags total |
| `R_MIN_SCREEN` | 0.30 | minimum |r| to be more than REJECTED; gate floor |
| `R_STRONG` | 0.50 | |r| for a "strong" forward lead (CONFIRMED-eligible) |
| `CLUSTER_R` | 0.70 | contemporaneous |r| ⇒ same underlying force |
| `CLUSTER_LINKAGE` | `"complete"` | tight forces (complete linkage); `"average"` for loose blocs |
| `FORCES_MUST_BE_TIGHT` | True | every force member ≥ 0.70 with every other |
| `FORCE_MIN_MONTHS` | 150 | shorter members excluded from composites |
| `SIG_ALPHA` | 0.05 | FDR q significance level |
| `N_SURROGATES` | 1000 | circular-shift permutation surrogates |
| `N_BOOTSTRAP` | 2000 | moving-block bootstrap resamples |
| `BLOCK_LEN` | 12 | bootstrap block length (months) |
| `SMOOTH_WIN` | 6 | centered rolling-mean window for the smoothing gate |
| `COMOVER_MAX_LAG` | 2 | ± band around lag 0 counted as contemporaneous (correlate.py / leaderboard.py) |
| `min_gain` (lead-sharpness) | 0.05 | peak must beat lag-0 |r| by this to be a "true lead" (correlate.py) |
| smoothing: lag tolerance | 6 mo | smoothed peak lag must be within this of raw (screen.py) |
| holds: `r_min` | 0.20 | late-half |r| floor (screen.py) |
| holds: `COLLAPSE_RATIO` | 0.5 | late |r| ≥ this × early |r| (screen.py) |
| holds: `MAX_HALF_DIFF` | 0.30 | early |r| − late |r| must not exceed this (screen.py) |
| episode: `JACK_BLOCK_YEARS` | 3 | jackknife block width (screen.py) |
| episode: `JACK_ANCHOR_YEAR` | 2020 | calendar anchor so 2020–2022 is one block (screen.py) |
| episode: `JACK_R_FLOOR` | 0.30 | block-out |r| floor to pass (screen.py) |
| `PARTIAL_MIN` | 0.20 | partial |r| at/above = a real edge remains (control.py) |
| `CYCLE_DROP_MIN` | 0.15 | |raw| − |partial| drop needed to call it cycle-driven (control.py) |
| short-sample `MIN_MONTHS` | 150 | usable-months floor (history.py) |
| short-sample `LATE_START` | 2010-01-01 | samples starting after this are flagged (history.py) |
| artefact `ARTIFACT_BENCH_R` | 0.60 | benchmark |r| over the window that signals an artefact (history.py) |
| artefact `BEATS_MARGIN` | 0.10 | signal must beat the benchmark by more than this (history.py) |

---

## 9. The dashboard (app.py)

Three tabs, all rendered from `outputs/`:

**🔬 Screen** — everything about one item in one place: pick a signal / force / bloc, see its
lag curve, the pass/fail of each gate, the permutation q and bootstrap CI, the market-cycle
control (raw vs partial), and its verdict.

**🔗 Correlation** — at each of the three levels (signal / tight-force / loose-bloc), the
**🗺️ lead-lag propagation map** (directed "A leads B") sits **above** the **🔗 co-movement matrix**
(undirected inter-item |r|), plus the clustering dendrograms. Cousin pairs (0.50–0.70) are flagged.

**🏆 Compare** — every verdict side by side in one table, with a colour-coded transparency row so
no verdict needs a drill-down. Columns:

| Column | What it shows |
|---|---|
| Verdict | the final label (§7), tinted per verdict |
| Why | one plain-language binding reason (significance-first, then cycle, etc.) |
| Lead | peak lag in months (+ = leads) |
| Raw r | peak correlation — green ≥ 0.50, amber 0.30–0.50, grey < 0.30 |
| Partial r | market-controlled r — coloured by the Cycle survival state |
| Cycle | survives / partly survives / cycle-driven / raw weak (grey) |
| Leads? | yes / NO from the peak-lag sign |
| Smoothing / Holds / Episode | the three gates: ✅ / ❌ NO / n·a |
| History | short-sample flag |
| Lead type | true lead / co-mover / lags |
| q | FDR q — green if < 0.05, red otherwise |
| CI | bootstrap 95% CI excludes zero? ✅ / ❌ NO |
| N | sample months — green ≥ 360, amber 150–359, red < 150 |

The header shows the **four relationship-group cards** (Leads / Co-movers / Reversed / Rejected),
each with its total and the screening-gate breakdown inside; the four totals sum to the number of
signals tested.

The verdict colours/backgrounds, group structure, and the flat verdict list all derive from
`VERDICT_COLORS`, `VERDICT_BG`, and `VERDICT_GROUPS` at the top of `app.py`, so the header, legend,
caption, and table always agree.

---

## 10. Regenerating the results

The committed `outputs/` are produced offline from the cached CSVs in `data/raw/`:

```bash
python3 run_pipeline.py
```

This runs the full battery — lag correlations, the 1000-surrogate permutation null, the
2000-resample bootstrap, the gates, the cycle control, and the clustering — for ~400 signals, and
writes every file in `outputs/`. It takes **~15 minutes** and is **never invoked by the dashboard**.

Pipeline stages (in `run_pipeline.py::main`, roughly):

1. Load levels for all series from `data/raw/`; YoY-transform.
2. Build the inter-signal contemporaneous correlation matrix → `leading_signal_corr_matrix.csv`.
3. For each candidate: lag curve, peak, lead classification, the 3 gates, permutation p +
   bootstrap CI, per-pair chart PNG.
4. Benjamini-Hochberg across all p-values → q. Assign `verdict()`.
5. Cycle control per signal → `cycle_control.csv`; fold into verdicts (`apply_cycle_control`).
6. Cluster into tight forces (complete) and loose blocs (average); build composites and run the
   same battery on each → `force_cycle_control.csv`, `loose_bloc_cycle_control.csv`, `*_tiers.csv`,
   `*_splits.csv`, `clusters*.json`, force/bloc correlation matrices.
7. Short-sample reconciliation → `short_sample_check.csv`.
8. Lead-lag propagation edges at all three levels → `lead_lag_edges*.csv`.
9. Assemble and sort the leaderboard → `leaderboard.csv` / `.md`; write `pair_details.json`,
   `analysis.md`, `grouping_ladder.json`.

**Fetching new series** from FRED requires `FRED_API_KEY` (see `tools/fred_harvest.py`,
`signal_tool/fred.py`). Not needed to re-run the pipeline on the already-cached data.

> **Reproducibility:** all resampling uses a seeded numpy `Generator` (seed 12345), so a re-run on
> the same data reproduces the same q-values and CIs exactly.

---

## 11. Output-file reference

Everything the dashboard reads lives in `outputs/`:

| File | Contents |
|---|---|
| `leaderboard.csv` | one row per signal: peak lag/r, gates, q, CI, partial r, survival, verdict, rank. The primary table. |
| `leaderboard.md` | human-readable version of the above. |
| `pair_details.json` | full per-signal detail: gate sub-results, permutation, bootstrap_ci, survival_vs_cycle, verdict. Drives the Screen tab. |
| `cycle_control.csv` | per-signal raw vs partial r, betas, survival. |
| `force_cycle_control.csv` | tight-force composites run through the battery. |
| `loose_bloc_cycle_control.csv` | loose-bloc composites. |
| `bloc_splits.csv`, `force_splits.csv` | how loose groups split into tight pieces. |
| `force_tiers.csv`, `bloc_tiers.csv` | force/bloc classification tiers. |
| `clusters.json`, `clusters_loose.json` | cluster memberships (tight / loose). |
| `leading_signal_corr_matrix.csv` | full inter-signal correlation matrix. |
| `force_correlation_matrix.csv`, `bloc_correlation_matrix.csv` | inter-composite matrices. |
| `lead_lag_edges.csv` / `_force.csv` / `_bloc.csv` | directed genuine-lead edges per level. |
| `grouping_ladder.json` | the signal→force→bloc grouping ladder. |
| `short_sample_check.csv` | short-sample flags and window-artefact numbers. |
| `signals.csv` | the catalogue actually used in the run. |
| `analysis.md` | narrative write-up. |
| `charts/*.png` | 399 precomputed charts: per-pair lag/overlay charts, dendrograms, clustered heatmaps. |

When the dashboard is reclassified without re-running stats (e.g. a verdict-taxonomy change), only
the verdict columns of the CSVs and `pair_details.json` are rewritten deterministically from the
already-stored gate/q/CI/survival columns — the 399 chart PNGs are untouched.

---

## 12. Adapting the tool to a different outcome

To point this at a different target (say, a different PPI or a company's input cost):

1. **Swap the outcome** in `signal_tool/config.py::OUTCOME` (new `fred_id`).
2. **Cache its data** and any new candidates under `data/raw/` (use `tools/fred_harvest.py` with a
   `FRED_API_KEY`, or drop in CSVs in the same 2-column `date,value` shape).
3. **Curate candidates**: edit `config.py::CANDIDATES` (seed set, each with a mechanism) and/or
   regenerate `signal_tool/signals_extra.csv` via `tools/build_manifest.py`.
4. **Re-run** `python3 run_pipeline.py` to regenerate all of `outputs/`.
5. **Adjust the copy** in `app.py` (title, the intro paragraph, the outcome id in a couple of
   captions) — the methodology, gates, taxonomy, and dashboard structure need no changes.
6. **Commit + push** — Streamlit Cloud redeploys automatically.

The thresholds in §8 are the tuning surface. They encode the brief's standards (a real lead needs
|r| ≥ 0.50, must survive smoothing/eras/episodes, must beat the commodity cycle, and must be FDR-
significant). Change them in one place (`config.py`, plus the gate constants in `screen.py` /
`control.py` / `history.py`) and re-run; every verdict and colour follows.

---

*This document describes the repository as committed. The single runtime entry point is
`app.py`; the single regeneration entry point is `run_pipeline.py`; every threshold and rule lives
in `signal_tool/`.*
