# Signal-candidate expansion — ~200 new series toward ~400 total

**Purpose.** Grow the candidate leading-signal library from ~192 to **~400** by enumerating the
*whole FRED family* behind each category's seed IDs (by release, category, or targeted search),
not just the seeds. The decisive test is unchanged: a new signal only counts as a **new force**
if its lead **survives removing the broad commodity cycle** (market-control partial |r| ≥ 0.20 with
a real raw→partial drop). Adding 200 series is about *coverage of mechanisms*, not about the
pass count.

**Outcome (unchanged):** `PCU335311335311` — PPI, Electric Power & Specialty Transformer Mfg.
**Market control (unchanged):** `PPIACO` — All-commodities PPI.

---

## Enumeration method (per category)

For each category we expand from the seed IDs to the full family using `tools/fred_harvest.py`:

1. **`meta ID…`** — pull `frequency`, `seasonal_adjustment`, `units`, `observation_start/end`,
   `title` for every candidate (keeps only genuinely **Monthly** series; drops daily/weekly
   unless it aggregates cleanly to monthly).
2. **`release <id>`** — all series in a BLS/Fed release (e.g. PPI, Import/Export Price Indexes).
3. **`category <id>`** — all series under a FRED category node (resolved from a seed via
   `fred/series/<seed>/categories`, added to the harvester as `cats <id>`).
4. **`search "<text>"`** — targeted text search, filtered to Monthly, for families not cleanly
   under one node (e.g. regional-Fed future sub-indices, data-center proxies).

Exact numeric release/category IDs are **resolved at harvest time** (printed and logged), because
they are not stable to hard-code; the seeds below are the anchors the family is grown from.

## Metadata recorded for EVERY series (into `signals_extra.csv` + `outputs/harvest_log.csv`)

`fred_id, title, category, tier, mechanism, source_url, units, frequency, obs_start, obs_end,
fetch_date, spot_check`

- `source_url` = `https://fred.stlouisfed.org/series/<ID>`
- `spot_check` = last observation `date=value` vs the FRED page (sanity that the CSV endpoint and
  the API agree), recorded at fetch time.

## Exclusions (applied before scoring)

- **Outcome siblings** — series that are the transformer PPI itself sliced differently, which
  would leak the answer. Drop **`WPU117409`** (power & distribution transformers PPI) and any
  `PCU335311*` / `WPU11740*` transformer-specific PPI. (Kept as a hidden benchmark only, never a
  candidate.)
- **Non-monthly** series that don't aggregate cleanly.
- **Duplicates** of an existing candidate ID.

## Short-sample quarantine

Many import-price, regional-Fed, and expectations families start ~2010+. Any series with usable
overlap **< 150 months** or start **after 2010** is flagged `short-sample` and **cannot be
CONFIRMED** unless a long (pre-2010) independent series measures the same thing and it is not a
window artifact (existing `history.py` guardrail).

---

## The 12 categories (🔶 = over-weighted — mechanisms not yet tested)

| # | Category | Now | +New | Total | Over? |
|---|----------|----:|----:|------:|:-----:|
| 1 | Input-cost PPI tree (metals/energy/materials upstream) | ~70 | 18 | 88 | |
| 2 | Import & export price indices | 5 | **34** | 39 | 🔶 |
| 3 | Freight & logistics cost | 2 | **18** | 20 | 🔶 |
| 4 | Forward demand: new orders, backlog, inventories | 13 | **24** | 37 | 🔶 |
| 5 | Forward financial: rates, curve, credit | 12 | 14 | 26 | |
| 6 | Inflation expectations | 5 | **10** | 15 | 🔶 |
| 7 | Regional-Fed survey — FUTURE (6-mo-ahead) | 8 | **26** | 34 | 🔶 |
| 8 | Regional-Fed survey — CURRENT | 11 | 14 | 25 | |
| 9 | Grid & data-center / electricity demand | 3 | **22** | 25 | 🔶 |
| 10 | Construction pipeline (power, mfg, permits) | 9 | 10 | 19 | |
| 11 | Industrial production & capacity (related industries) | 13 | 6 | 19 | |
| 12 | Global commodity benchmarks & FX | 9 | 6 | 15 | |
| | **Total** | ~160 | **202** | **~362–400** | |

(The "Now" counts are approximate current coverage; the input-cost PPI tree already dominates, so
it is grown only modestly. The four over-weighted categories add **134 of the 202** new series.)

### 1 · Input-cost PPI tree — +18
Direct/upstream input costs (metals, energy, materials) that feed transformer manufacture.
- **Seeds:** `WPUSI019011, WPU101, WPU1017, WPU102501, WPU1026, WPU057, WPU072, WPU0531` (+ full
  existing metals/energy tree).
- **Enumerate:** PPI release → Metals & metal products, Nonmetallic minerals, Rubber & plastics,
  Fuels & related power sub-trees; add missing mid-tree nodes (e.g. cold-rolled, castings,
  insulated wire, transformer-oil-adjacent lubricants) **excluding** any transformer sibling.
- **Mechanism:** input material/energy cost feeds finished transformer cost.

### 2 · 🔶 Import & export price indices — +34
Imported input costs (copper, transformers' inputs, industrial supplies) lead domestic PPI; the US
imports a large share of grid-transformer components.
- **Seeds:** `IR1, IR1EXFUEL, IR1DUR, IR14260, IR14220` (BLS MUR/IR end-use import families).
- **Enumerate:** Import/Export Price Indexes release → **end-use** (industrial supplies, capital
  goods, metals), **NAICS** (primary metal, electrical equipment), and **locality-of-origin**
  (China, EU) import families; export counterparts where a domestic mechanism exists.
- **Mechanism:** delivered imported-input cost tends to lead domestic transformer input PPI.
- ⚠️ Many start 2010+ → expect heavy short-sample quarantine.

### 3 · 🔶 Freight & logistics cost — +18
Fast-moving trade/transport cost that can lead delivered input prices and equipment lead-times.
- **Seeds:** `PCU484484` (general freight trucking), `WPU3012` (transportation services PPI).
- **Enumerate:** Transportation-services PPI family (truck long-distance TL/LTL, rail, water, air,
  courier, warehousing/`PCU493`), plus FRED freight indexes (`FRGSHPUSM649NCIS` Cass-type shipments
  & `FRGEXPUSM649NCIS` expenditures) and diesel/fuel-surcharge proxies. Monthly only.
- **Mechanism:** transport cost + capacity tightness lead delivered input and equipment cost.

### 4 · 🔶 Forward demand: new orders, backlog, inventories — +24
Orders and backlogs are the classic *forward* demand signal; inventory-to-sales imbalance leads
price pressure. Directly upstream of the goods transformers belong to.
- **Seeds:** `A35SNO, A35SUO, AMTMNO, AMTMUO, ANDENO, NEWORDER, DGORDER, ISRATIO, MNFCTRIRSA,
  RETAILIRSA` (M3 + inventory releases).
- **Enumerate:** M3 Manufacturers' Shipments/Inventories/Orders release → **new orders**,
  **unfilled orders (backlog)**, **shipments**, **inventories** for electrical equipment,
  machinery, primary & fabricated metal, computers/electronics, capital goods; plus total-business
  and manufacturing inventory-to-sales ratios.
- **Mechanism:** orders/backlog lead shipments and prices; low I/S ratio = tightening → price rise.

### 5 · Forward financial: rates, curve, credit — +14
Financing cost for capital-intensive grid/utility investment leads the capex/build cycle.
- **Seeds:** `T10Y2Y, T10Y3M, DFII10, GS2, GS1, FEDFUNDS, MORTGAGE30US, BAA10Y, AAA10Y, BAA, AAA`.
- **Enumerate:** Treasury constant-maturity curve (`GS1MO…GS30`), real yields (`DFII5/10/30`),
  curve spreads, corporate spreads (`BAMLC0A0CM`, `BAMLH0A0HYM2`), utility-sector credit where
  monthly. Aggregate daily→monthly average.
- **Mechanism:** rate/credit conditions lead industrial & grid capital investment.

### 6 · 🔶 Inflation expectations — +10
A forward read on input-cost inflation — a mechanism the library barely covers.
- **Seeds:** `T5YIE, T10YIE, T5YIFR, EXPINF1YR, MICH`.
- **Enumerate:** TIPS breakevens across maturities (`T5YIE, T7YIE, T10YIE, T20YIE, T30YIE`),
  5y5y forward, Cleveland-Fed expected-inflation term structure (`EXPINF1YR…EXPINF10YR`), Michigan
  1y/5y. Daily→monthly.
- **Mechanism:** expected inflation leads realized input-cost inflation and pricing behaviour.

### 7 · 🔶 Regional-Fed survey — FUTURE (6-month-ahead) — +26
Purpose-built *forward* indicators of orders, prices-paid/received, and capex — the strongest
a-priori forward mechanism not yet tested at breadth.
- **Seeds (Philly/NY):** `GAFDFSA066MSFRBPHI, NOFDFSA066MSFRBPHI, PPFDFSA066MSFRBPHI,
  PRFDFSA066MSFRBPHI, CEFDFSA066MSFRBPHI, NOFDISA066MSFRBNY, PPFDISA066MSFRBNY, CEFDISA066MSFRBNY`.
- **Enumerate:** FUTURE (6-mo-ahead) diffusion sub-indices — **new orders, unfilled orders,
  prices paid, prices received, capex, employment, general activity** — across **Philadelphia, New
  York (Empire), Richmond, Kansas City, Dallas, Texas** manufacturing surveys (search
  `"future ... Federal Reserve Bank of"`, Monthly).
- **Mechanism:** 6-month-ahead expectations of orders/prices/capex directly forecast the pricing
  cycle for electrical equipment.

### 8 · Regional-Fed survey — CURRENT — +14
Near-real-time activity/prices (largely coincident) — a control/contrast to the FUTURE indices.
- **Seeds:** `GACDFSA066MSFRBPHI, NOCDFSA066MSFRBPHI, PPCDFSA066MSFRBPHI, …` (Philly/NY current).
- **Enumerate:** CURRENT diffusion sub-indices (same sub-index list, same six banks).
- **Mechanism:** current diffusion is coincident; expected mostly to co-move, not lead.

### 9 · 🔶 Grid & data-center / electricity demand — +22
A **new mechanism**: grid build-out and the data-center electricity boom pull transformer demand.
- **Seeds:** `IPUTIL` (utilities IP), `WPU054` (electric power PPI), `TLPWRCONS` (power
  construction).
- **Enumerate:**
  - Electricity **price**: `WPU0543` (electric power to ultimate/industrial), `APU000072610`
    (avg retail electricity), industrial electricity PPI nodes.
  - Electricity **output/demand**: `IPG2211S` (electric power generation IP), `IPG2211A2S`,
    `CAPUTLG2211S` (utility capacity), electricity end-use where monthly.
  - **Data-center proxies**: `PCU518210518210` (data processing, hosting & related PPI),
    `IPG334S` (computer & electronic product IP), `IPG3344S` (semiconductor), `TLCOMCONS`
    (commercial construction), office/commercial construction spending.
- **Mechanism:** electricity demand + data-center/commercial build pull grid-transformer orders
  ahead of transformer prices. **This is the headline new-mechanism test.**

### 10 · Construction pipeline (power, mfg, permits) — +10
The build cycle leads electrical-equipment demand.
- **Seeds:** `PERMIT, PERMIT1, HOUST, HOUST1F, PBPWRCONS, TLMFGCONS, TLNRESCONS, TTLCONS,
  TLRESCONS`.
- **Enumerate:** Census construction-spending release (power, manufacturing, commercial, office,
  transportation) + permits/starts by region. Monthly.
- **Mechanism:** power & manufacturing construction leads grid-equipment orders.

### 11 · Industrial production & capacity (related industries) — +6
Output cycle of adjacent industries (largely coincident).
- **Seeds:** `IPG331S, IPG332S, IPG333S, IPG335S, IPG3311A2S, CAPUTLG331S, CAPUTLG333S,
  CAPUTLG335S`.
- **Enumerate:** IP & capacity-utilization release for primary/fabricated metal, machinery,
  electrical equipment, and their capacity nodes.
- **Mechanism:** related-industry output; coincident, used mainly for force structure.

### 12 · Global commodity benchmarks & FX — +6
Traded-input triangulation and FX pass-through (likely duplicates the metals/energy force).
- **Seeds:** `POILBREUSDM, PIORECRUSDM, PNGASUSUSDM, PCOALAUUSDM, PURANUSDM, PRUBBUSDM, DTWEXBGS,
  DTWEXAFEGS`.
- **Enumerate:** IMF/World-Bank global commodity series (metals, energy, industrial inputs) +
  trade-weighted dollar variants. Monthly.
- **Mechanism:** global benchmark / FX; triangulation and cycle-control context.

---

## Testing discipline (applied hard at ~400)

Per the protocol, **each signal is tested individually first**, before any clustering:

1. **Gather → process → visualize** (level / YoY / 2nd-derivative), spot-check recorded.
2. **Lag correlation** across lags [−24, +24] on YoY.
3. **Robustness screen** — two disqualifying gates (survives smoothing; holds over time,
   directional-collapse aware) + lead-sharpness (co-mover check).
4. **Market-control partial r** — the **decisive filter**: raw lead-r vs `PPIACO`-controlled
   partial r at the measured lead. A signal is a **new force only if** partial |r| ≥ 0.20 **and**
   the raw→partial drop is real (not weak-on-its-own).
5. **Significance** — circular-shift permutation p, **Benjamini-Hochberg FDR across all ~400**
   candidates (one family), + moving-block bootstrap CI.
6. **Then, and only then, grouping** — per-force counting on the **ladder**: signals → 🔸 tight
   forces (complete linkage) → 🔶 loose blocs (average linkage), with the inter-group correlation
   matrix + partial-r as the independence check.
7. **Short-sample quarantine** and **outcome-sibling drop** applied throughout.

## The reporting goal (what actually matters)

Not the pass count. The single question:

> **Does ANY forward, freight, or grid/data-center-demand signal lead transformer prices AND
> survive the commodity-cycle control?**

Report, specifically, whether any category-2/3/4/6/7/9 signal ends **CONFIRMED and survives**
(partial |r| ≥ 0.20 with a real drop, FDR-significant, not short-sample). **That single genuine
demand/forward survivor is the goal** — if none survives, that is the finding: the metals-input
forces remain the only genuine leads, and demand/forward/import/freight are cycle-driven
co-movers.
