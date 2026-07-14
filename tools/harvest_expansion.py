#!/usr/bin/env python3
"""Enumerate the ~200-series expansion per SIGNAL_CANDIDATES_200_EXPANSION.md.

For each of the 12 categories, grow the FRED FAMILY behind the seed IDs (via the categories a
seed belongs to, and via targeted search) — not just the seeds — filter to Monthly, dedupe
against the existing library, DROP outcome siblings, cap near the per-category target, and record
full metadata + a spot-check. Appends new rows to signal_tool/signals_extra.csv and writes
outputs/harvest_log.csv.

Run: FRED_API_KEY=... python3 tools/harvest_expansion.py
Discovery/metadata via the FRED API; observations via the keyless CSV endpoint (signal_tool.fred).
"""
import csv
import os
import re
import sys
import time
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import fred_harvest as FH          # _get, meta, search, release, category
from signal_tool import config as CFG
from signal_tool import fred as FRED

MANIFEST = os.path.join(ROOT, "signal_tool", "signals_extra.csv")
LOG = os.path.join(ROOT, "outputs", "harvest_log.csv")
SERIES_URL = "https://fred.stlouisfed.org/series/{}"
FETCH_DATE = date.today().isoformat()

# Outcome siblings — transformer PPI sliced differently; would leak the answer. Never candidates.
SIBLING_RX = re.compile(r"^(WPU11740|PCU335311|WPU117409)")

# (key, tier, target, mechanism, seed_ids, search_terms, title_whitelist_regex)
# The title whitelist is decisive: category-node enumeration pulls in mechanism-IRRELEVANT
# siblings (e.g. the data-processing PPI category also holds newspaper/book-publishing PPIs), so
# only titles matching the category's mechanism keywords are kept.
CATS = [
 ("input_ppi", "input-upstream", 18,
  "Upstream input material/energy cost (metals, energy, materials) that feeds finished transformer cost.",
  ["WPUSI019011","WPU101","WPU1017","WPU102501","WPU1026","WPU057","WPU072","WPU0531"],
  [],
  r"metal|steel|iron|copper|aluminum|alumin|nonferrous|non-ferrous|zinc|nickel|lead|tin|scrap|"
  r"\bore\b|wire|cable|fabricated|foundry|cast|rubber|plastic|chemical|fuel|petroleum|\bgas\b|"
  r"energy|mineral|cement|glass|insulat|lumber|paint|coat"),
 ("import", "input-upstream", 34,
  "Imported input cost (metals, capital goods, industrial supplies); delivered import prices lead domestic transformer input PPI.",
  ["IR1","IR1EXFUEL","IR1DUR","IR14260","IR14220"],
  ["import price index end use industrial supplies","import price index metals",
   "import price index capital goods","import price index electrical"],
  r"import"),
 ("freight", "input-upstream", 18,
  "Freight / transport cost and capacity tightness; a fast-moving trade-cost signal that leads delivered input and equipment cost.",
  ["PCU484484","WPU3012","PCU493","FRGSHPUSM649NCIS","FRGEXPUSM649NCIS"],
  ["truck transportation PPI","rail transportation PPI","freight index","warehousing PPI"],
  r"freight|truck|transport|\brail\b|water transport|air transport|courier|warehous|shipp|cargo|"
  r"logistic|deep sea|inland water"),
 ("orders", "demand-forward", 24,
  "Manufacturers' new/unfilled orders, shipments, inventories; forward demand and backlog for equipment lead shipments and prices.",
  ["A35SNO","A35SUO","AMTMNO","AMTMUO","ANDENO","NEWORDER","DGORDER","ISRATIO","MNFCTRIRSA","RETAILIRSA"],
  ["manufacturers unfilled orders","manufacturers new orders electrical","inventories to sales ratio"],
  r"order|shipment|inventor|unfilled|backlog"),
 ("rates", "financial-forward", 14,
  "Interest-rate / yield-curve / credit signal; financing cost for capital-intensive grid investment that leads the capex/build cycle.",
  ["T10Y2Y","T10Y3M","DFII10","GS2","GS1","FEDFUNDS","MORTGAGE30US","BAA10Y","AAA10Y","BAA","AAA"],
  ["treasury constant maturity","corporate bond spread option adjusted"],
  r"yield|treasury|\brate\b|bond|spread|maturity|federal funds|mortgage|libor|sofr"),
 ("expectations", "financial-forward", 10,
  "Market / survey inflation expectations; a forward read on input-cost inflation.",
  ["T5YIE","T10YIE","T5YIFR","EXPINF1YR","MICH"],
  ["breakeven inflation rate","expected inflation cleveland","5-year forward inflation"],
  r"inflation|expected|breakeven|expectation|sentiment"),
 ("regionalfed_future", "demand-forward", 26,
  "Regional-Fed survey FUTURE (6-month-ahead) diffusion (orders/prices/capex); a purpose-built forward indicator of the pricing cycle for electrical equipment.",
  ["GAFDFSA066MSFRBPHI","NOFDFSA066MSFRBPHI","PPFDFSA066MSFRBPHI","PRFDFSA066MSFRBPHI",
   "CEFDFSA066MSFRBPHI","NOFDISA066MSFRBNY","PPFDISA066MSFRBNY","CEFDISA066MSFRBNY"],
  ["future federal reserve bank of manufacturing","future prices paid federal reserve bank",
   "future new orders federal reserve bank","future capital expenditures federal reserve"],
  r"future.*federal reserve|future.*fed\b"),
 ("regionalfed_current", "demand-activity", 14,
  "Regional-Fed survey CURRENT diffusion; near-real-time activity/prices (largely coincident).",
  ["GACDFSA066MSFRBPHI","NOCDFSA066MSFRBPHI","PPCDFSA066MSFRBPHI","PRCDFSA066MSFRBPHI"],
  ["current prices paid federal reserve bank of","current new orders federal reserve bank of",
   "current general activity federal reserve bank of"],
  r"current.*federal reserve|current.*fed\b"),
 ("grid_datacenter", "demand-forward", 22,
  "Grid build-out and the data-center electricity boom pull grid-transformer demand ahead of transformer prices.",
  ["IPUTIL","WPU054","TLPWRCONS","IPG2211S","PCU518210518210","IPG334S","IPG3344S","TLCOMCONS"],
  ["electric power generation industrial production","electricity price producer",
   "data processing hosting PPI","semiconductor industrial production","utilities capacity utilization"],
  r"electric|electricity|power generation|\butilit|kilowatt|\bgrid\b|data processing|hosting|"
  r"data center|semiconductor|computer|server|transmission and distribution"),
 ("construction", "demand-forward", 10,
  "Construction/permit activity in the building pipeline; power & manufacturing construction leads grid-equipment orders.",
  ["PERMIT","PERMIT1","HOUST","HOUST1F","PBPWRCONS","TLMFGCONS","TLNRESCONS","TTLCONS","TLRESCONS"],
  ["total construction spending","new private construction manufacturing"],
  r"construction|permit|housing|\bstarts\b|building|nonresidential|manufacturing construction"),
 ("ip_capacity", "demand-activity", 6,
  "Industrial production / capacity utilization of adjacent industries; largely coincident, used for force structure.",
  ["IPG331S","IPG332S","IPG333S","IPG335S","IPG3311A2S","CAPUTLG331S","CAPUTLG333S","CAPUTLG335S"],
  ["capacity utilization primary metal","industrial production fabricated metal"],
  r"industrial production|capacity utilization"),
 ("commodity_fx", "triangulation", 6,
  "Global commodity benchmark / trade-weighted dollar; traded-input triangulation and FX pass-through.",
  ["POILBREUSDM","PIORECRUSDM","PNGASUSUSDM","PCOALAUUSDM","PURANUSDM","PRUBBUSDM","DTWEXBGS","DTWEXAFEGS"],
  ["global price index of commodity","trade weighted dollar index"],
  r"global price|price index of|dollar index|trade weighted|crude|metal|commodity"),
]

MIN_OBS_END = "2025-01-01"      # drop discontinued series (must still be updating recently)


def existing_ids():
    ids = {c.fred_id for c in CFG.ALL_SERIES}
    if os.path.exists(MANIFEST):
        with open(MANIFEST) as fh:
            for row in csv.DictReader(fh):
                ids.add(row["fred_id"].strip())
    return ids


def series_categories(sid):
    try:
        j = FH._get("series/categories", {"series_id": sid})
        return [c["id"] for c in j.get("categories", [])]
    except Exception:
        return []


def enumerate_category(cid, limit=500):
    try:
        return FH.category(cid, limit=limit)     # [{id, freq, title}]
    except Exception:
        return []


def search_monthly(text, limit=60):
    try:
        return FH.search(text, limit=limit,
                         extra={"filter_variable": "frequency", "filter_value": "Monthly"})
    except Exception:
        return []


def spot_check(sid):
    """Return 'YYYY-MM-DD=value' for the last observation via the keyless CSV endpoint, or ''."""
    try:
        path = FRED.fetch_raw(sid)
        with open(path) as fh:
            rows = [r for r in fh.read().splitlines() if r.strip()]
        for line in reversed(rows[1:]):
            d, _, v = line.partition(",")
            if v not in ("", ".", "NaN"):
                return f"{d}={v}"
    except Exception as e:
        return f"ERR:{str(e)[:30]}"
    return ""


def main():
    have = existing_ids()
    selected_all, log_rows = [], []
    print(f"Existing library: {len(have)} ids. Target ~200 new across {len(CATS)} categories.\n")

    for key, tier, target, mech, seeds, terms, wl in CATS:
        white = re.compile(wl, re.I)
        # candidate ids from (a) categories each seed belongs to, (b) targeted searches
        cand = {}                                # id -> title
        cat_ids = set()
        for s in seeds[:8]:
            for cid in series_categories(s):
                cat_ids.add(cid)
            time.sleep(0.05)
        for cid in list(cat_ids)[:12]:
            for row in enumerate_category(cid):
                if row.get("freq") == "M":
                    cand[row["id"]] = row["title"]
            time.sleep(0.05)
        for t in terms:
            for row in search_monthly(t):
                cand[row["id"]] = row["title"]
            time.sleep(0.05)

        # filter: new, not a sibling, TITLE matches the category mechanism whitelist
        fresh = [(i, ttl) for i, ttl in cand.items()
                 if i not in have and not SIBLING_RX.match(i) and white.search(ttl or "")]
        # metadata (capped); keep monthly, still-updating (not discontinued); longest history first
        metas = {m["id"]: m for m in FH.meta([i for i, _ in fresh][:200]) if "error" not in m}
        keep = [i for i, _ in fresh
                if metas.get(i, {}).get("freq") == "M" and metas[i]["end"] >= MIN_OBS_END]
        keep.sort(key=lambda i: metas[i]["start"])       # longest history first (most testable)
        chosen = keep[:target]

        for i in chosen:
            m = metas[i]
            have.add(i)
            label = m["title"][:44]
            selected_all.append({"fred_id": i, "label": label, "category": key, "tier": tier,
                                 "mechanism": mech, "note": ""})
            log_rows.append({"fred_id": i, "title": m["title"], "category": key,
                             "source_url": SERIES_URL.format(i), "units": m["units"],
                             "frequency": m["freq"], "obs_start": m["start"], "obs_end": m["end"],
                             "fetch_date": FETCH_DATE, "spot_check": spot_check(i)})
        print(f"{key:22} seeds={len(seeds):2} cats={len(cat_ids):2} pool={len(cand):3} "
              f"fresh={len(fresh):3} -> chose {len(chosen)}/{target}")

    # append to manifest
    with open(MANIFEST, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["fred_id","label","category","tier","mechanism","note"])
        for r in selected_all:
            w.writerow(r)
    # harvest log
    with open(LOG, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["fred_id","title","category","source_url","units",
                                           "frequency","obs_start","obs_end","fetch_date","spot_check"])
        w.writeheader()
        for r in log_rows:
            w.writerow(r)
    print(f"\nAppended {len(selected_all)} new series to {os.path.relpath(MANIFEST, ROOT)}")
    print(f"Wrote metadata + spot-checks to {os.path.relpath(LOG, ROOT)}")


if __name__ == "__main__":
    main()
