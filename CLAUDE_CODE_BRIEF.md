# Signal Tool — Independent Build Brief (for Claude Code)

You are being asked to build and run a leading-indicator signal test **independently**,
following the protocol below. Another assistant is doing the same task in parallel;
the point is to compare both the approach and the results, so implement this yourself
rather than copying an existing solution. Where the protocol pins down an exact
definition, follow it (so results are comparable). Where it leaves a choice, use your
judgment and note what you chose.

---

## 0. How to use this brief

1. Read the whole document first.
2. Build a small, modular Python package that implements the protocol in Section 3–5.
3. Gather the data in Section 7–8 from FRED.
4. Produce the deliverables in Section 9.
5. Check your numbers against the known-good anchors in Section 10.
6. Write a short README explaining your design choices.

Keep it simple and legible. No machine learning. The value is in careful data handling,
honest statistics, and clear reasoning, not model complexity.

---

## 1. Background & objective

The larger project builds an "external signal discernment" tool for the energy
transition: gather many candidate signals, turn them into time series, and find where
a **fast-moving signal reliably leads a slower one**. The investable idea lives in the
gap between them.

This brief covers one narrow, fully public slice of that: **do the prices of raw metal
inputs lead the price of electrical transformers, and by how much?** The transformer
shortage makes this a real economic question, and all the data is free on FRED.

**Objective:** for each candidate leading signal, determine whether it genuinely leads
transformer prices, measure the lead time, and rank the candidates by how trustworthy
the relationship is.

---

## 2. Scope for this run

- **Outcome variable (the thing being predicted):** Producer Price Index for Electric
  Power and Specialty Transformer Manufacturing. FRED series `PCU335311335311`. Monthly.
- **Candidate leading signals:** metal input prices and related industrial series (see
  Section 8).
- **Frequency:** monthly, 1967–present where available.

---

## 3. The protocol (do these in order, never skip)

1. **Gather** each series from a primary source (FRED). Record series ID, units,
   frequency, date range, and fetch date. Save raw data locally so runs are reproducible.
   Never fabricate or interpolate; if a value is estimated, label it.
2. **Process** transparently. Compute three views of each series: level, year-over-year
   % change (1st derivative), and change in that YoY (2nd derivative). Use year-over-year
   to cancel seasonality. Align each candidate with the outcome on a common monthly index;
   keep only months where both exist.
3. **Visualize** the prepared series **before** computing any correlation, and describe
   what you see. The chart drives the question; statistics confirm or surprise.
4. **Correlate across lags.** For lags k = −24…+24 months, correlate the candidate's YoY
   with the outcome's YoY shifted by k. Positive k = candidate leads. Record the peak
   (largest |r|), the lag at the peak, and n.
5. **Robustness screen** (Section 4).
6. **Significance test** (Section 4).
7. **Conclude** and report the lead time as a *measured output*, not a pre-guessed target.

---

## 4. Exact method definitions (follow these so results compare)

**Year-over-year % change:** `(x_t / x_{t-12} − 1) × 100`.
**Second derivative:** the 12-month difference of the YoY series.
**Lag correlation:** Pearson r between candidate YoY and outcome YoY at each integer lag
in [−24, +24]. Peak = lag with the largest absolute r (require n ≥ 4 at that lag).

**Robustness screen — two disqualifying GATES and two CONFIRMATORY checks.**
A pair passes only if it actually leads (peak lag ≥ 0), |peak r| ≥ 0.30, and **neither
gate fails**. The confirmatory checks add confidence but never fail a pair on their own
(a "no" means "not shown yet", important while the signal library is small).

- *Gate — Survives smoothing:* smooth both YoY series with a centered 6-month rolling
  mean, recompute the peak. Pass if the sign is unchanged, the lag stays within 6 months
  of the raw peak, and |r| ≥ 0.30.
- *Gate — Holds over time:* split the aligned history into an early half and a late half.
  Measure r at the raw peak lag in each half. Pass if both halves have the same sign as
  the full-sample r and each |r| ≥ 0.20.
- *Support — Second opinion:* does another, **independent** candidate (same outcome) peak
  with the same sign at a lag within 6 months, with |r| ≥ 0.30? If none, mark "not yet
  corroborated" (not a failure).
- *Support — Has a reason:* is a plausible written mechanism supplied? (Human judges
  quality; the tool only checks one exists.)

**Significance (this is required, not optional).** Ordinary p-values assume independent
observations and no lag search; both are false here, so use resampling methods:

- *Permutation p-value:* generate surrogates by **circularly shifting** the outcome series
  by a random offset (≥ max_lag, wrapping). This preserves each series' own
  autocorrelation but destroys the cross relationship. For each surrogate recompute the
  **peak |r| over all lags** (so the multi-lag search is built into the null). p = (number
  of surrogates with peak |r| ≥ observed peak |r|, plus 1) / (n_surrogates + 1). Use
  ≥ 500 surrogates. Significant if p < 0.05.
- *Confidence interval:* moving-block bootstrap at the peak lag (block length ≈ 12 months,
  ≥ 1000 resamples). Report the 95% interval; it should exclude 0.

**Correlation-of-correlations (do not skip).** Build a correlation matrix of the *leading
signals themselves* (contemporaneous YoY). Two signals correlated ≥ 0.70 are largely the
same underlying force and must **not** be counted as two independent confirmations. Report
this matrix and flag such clusters.

---

## 5. Success metrics, scorecard, and verdicts

Grade each pair on: leads (lag ≥ 0), strength (|r|), significance (permutation p),
confidence (CI excludes 0), robustness (passes both gates), independent support (≥ 1
uncorrelated corroborator), and measured lead.

Verdicts:
- **CONFIRMED** — leads, |r| ≥ 0.50, passes the screen, and p < 0.05.
- **STRONG / NOT ROBUST** — strong and correctly directed but fails the screen or
  significance (a likely false correlation).
- **REVERSED** — strong but the outcome leads the candidate (test the flipped pair).
- **REJECTED** — |r| < 0.30 or not significant.
- **PARTIAL / INCONCLUSIVE** — moderate or mixed.

---

## 6. Guardrails (how to avoid fooling yourself)

1. Testing many pairs manufactures false positives; the screen and significance test are
   mandatory at scale.
2. Direction is the prediction to confirm; lead time is a quantity to measure. Never move
   a predicted lead to the observed peak and call it "confirmed."
3. Corroborators only count if they are not themselves highly correlated.
4. A good story is necessary but not sufficient — it must clear the gates and significance.

---

## 7. Data source: FRED

FRED (Federal Reserve Economic Data, St. Louis Fed) is free and needs no key for browsing.
Two ways to get a series:
- CSV endpoint `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SERIESID` — may return
  as binary/compressed depending on your fetcher.
- Data-table page `https://fred.stlouisfed.org/data/SERIESID` — returns the observations as
  readable text (DATE, VALUE). Robust fallback if the CSV endpoint gives you trouble.
- The official **FRED API** (free key) is the cleanest for automation:
  `https://api.stlouisfed.org/fred/series/observations?series_id=ID&api_key=KEY&file_type=json`.

**Verification rule:** after saving each series, spot-check several values (e.g. first,
last, and a few mid-history dates) against the live FRED page. Record the checks. Do not
proceed with a series that fails a spot-check.

---

## 8. Candidate signals (starter set — expand with your own)

Outcome: `PCU335311335311` (transformer PPI, monthly).

Confirm each ID on FRED before use; some are best-guesses.

| Concept | Likely FRED ID | Why it might lead transformers |
|---|---|---|
| Copper PPI | `WPUSI019011` | Copper is the primary winding metal |
| Aluminum mill shapes PPI | `WPU102501` | Alternative winding/housing metal |
| Iron & steel PPI | `WPU101` | Core steel is the transformer core |
| Iron & steel scrap PPI | `WPU1012` | Upstream of finished steel |
| Global copper price | `PCOPPUSDM` | Independent copper measure (triangulation) |
| Global aluminum price | `PALUMUSDM` | Independent aluminum measure |
| Global nickel price | `PNICKUSDM` | Alloying input to electrical steels |
| WTI crude oil (monthly) | `WTISPLC` | Energy cost feeding manufacturing |
| Electrical machinery & equipment PPI | `WPU117` | Broader electrical-goods price |
| Industrial production: utilities | `IPUTIL` | Grid-side demand proxy |

Add any others you can justify with a mechanism. More independent signals make the
correlation-of-correlations check more meaningful.

---

## 9. Deliverables

1. A small Python package implementing the protocol (data loaders, processing,
   correlation, screen, significance, leaderboard).
2. A **leaderboard**: one ranked table over all pairs with columns — verdict, measured
   lead, peak r, 95% CI, permutation p-value, robust (yes/no), n.
3. The **leading-signal correlation matrix** with clusters flagged.
4. A short **README / methods note** describing your design choices and any judgment calls.
5. (Optional) simple charts per pair: level, YoY, and the lag-correlation curve.

---

## 10. Known-good anchor results (for comparison / validation)

If your pipeline is correct, these three pairs should reproduce closely (small differences
in significance from randomness are fine):

| Pair | Expected peak r | Expected lead | Expected verdict |
|---|---|---|---|
| Copper → transformer | ≈ +0.53 | +8 months | CONFIRMED, significant |
| Aluminum → transformer | ≈ +0.62 | +4 months | CONFIRMED, significant |
| Iron & steel → transformer | ≈ +0.67 | +4 months | CONFIRMED, significant |
| Manufacturing employment (`MANEMP`) → transformer | ≈ −0.12 | −12 months (lags) | REJECTED, p ≈ 0.8 |
| Hyperscaler capex (annual, self-compiled) → transformer | ≈ +0.75 but at −3 yr | reversed | REVERSED / flip candidate |

The three metals correlate only ~0.48–0.69 with each other (moderately, none ≥ 0.70), so
they count as partly-independent witnesses. If you find any of these materially different,
something in your pipeline differs — worth investigating, and exactly the kind of
divergence this comparison is meant to surface.

---

## 11. Reference implementation (optional)

A separate reference implementation of this protocol exists. You do **not** need to look at
it, and for a clean comparison it may be better not to. Build your own and let the results be
compared.

---

*End of brief. Build it, run it, and report your leaderboard plus a note on where your
choices differed from the protocol's defaults.*
