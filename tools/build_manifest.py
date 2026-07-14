#!/usr/bin/env python3
"""Generate signal_tool/signals_extra.csv — the expanded (~200) candidate manifest.

Forward-weighted per the brief: construction pipeline, order backlog / supply tightness,
rates & credit, inflation expectations, import prices, freight, and regional-Fed FUTURE
sub-indices; plus a curated PPI input-cost tree sample and global commodities for force
structure. Mechanisms are category-level templates + a strength tier (the chosen approach).

Run: FRED_API_KEY=... python3 tools/build_manifest.py <keyfile> <ppi_tree.json>
Titles come from the FRED API (labels only); observations stay on the keyless CSV endpoint.
"""
import csv, json, os, subprocess, sys, time

KEYFILE, PPITREE = sys.argv[1], sys.argv[2]
KEY = open(KEYFILE).read().strip()
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "signal_tool", "signals_extra.csv")

# Existing 30 (seed in config.py) — do not duplicate.
EXISTING = {"WPUSI019011","WPU102501","WPU101","WPU1012","PCOPPUSDM","PALUMUSDM","PNICKUSDM",
    "WTISPLC","WPU117","IPUTIL","MANEMP","WPU101707","WPU1026","WPU1011","WPU0576","PZINCUSDM",
    "PLEADUSDM","PTINUSDM","WPU1017","WPU101705","WPU057","WPU072","WPU0531","WPU054","IPMAN",
    "MCUMFN","A35SNO","TLPWRCONS","CES3133500001","GS10","PCU335311335311","PPIACO"}

# (category, tier, mechanism_template, [ids])
FAM = [
 ("construction","demand-forward","Construction/permit activity in the building pipeline; the build cycle leads electrical-equipment demand ahead of transformer orders and prices.",
   ["PERMIT","PERMIT1","HOUST","HOUST1F","PBPWRCONS","TLMFGCONS","TLNRESCONS","TTLCONS","TLRESCONS"]),
 ("orders","demand-forward","Manufacturers' new/unfilled orders — forward demand and backlog for equipment; orders lead shipments and prices.",
   ["AMTMUO","A35SUO","A34SNO","A33SNO","A32SNO","A31SNO","ANDENO","DGORDER","AMTMNO","NEWORDER"]),
 ("inventories","demand-forward","Inventories-to-sales ratio; a supply/demand-imbalance gauge that leads price pressure (low I/S = tightening).",
   ["ISRATIO","MNFCTRIRSA","RETAILIRSA"]),
 ("rates","financial-forward","Interest-rate / yield-curve signal; financing cost for capital-intensive grid investment, which leads the capex/build cycle.",
   ["T10Y2Y","T10Y3M","DFII10","GS2","GS1","FEDFUNDS","MORTGAGE30US","TB3MS"]),
 ("credit","financial-forward","Corporate credit spread / bond yield; risk appetite and financing cost that lead industrial investment.",
   ["BAA10Y","AAA10Y","BAA","AAA"]),
 ("expectations","financial-forward","Market / survey inflation expectations; a forward read on input-cost inflation.",
   ["T5YIE","T10YIE","T5YIFR","EXPINF1YR","MICH"]),
 ("dollar","financial-forward","Trade-weighted US dollar; FX moves imported input costs and global commodity prices with a lead.",
   ["DTWEXBGS","DTWEXAFEGS"]),
 ("sentiment","financial-forward","Consumer sentiment; a forward demand proxy.",
   ["UMCSENT"]),
 ("import","input-upstream","Import price index; imported input costs tend to lead domestic PPI.",
   ["IR1","IR1EXFUEL","IR1DUR","IR14260","IR14220"]),
 ("freight","input-upstream","Freight / transport cost; a fast-moving trade-cost signal that can lead delivered input prices.",
   ["PCU484484","WPU3012"]),
 ("regionalfed_future","demand-forward","Regional-Fed survey FUTURE (6-month-ahead) expectation; a purpose-built forward indicator of orders / prices / capex.",
   ["GAFDFSA066MSFRBPHI","NOFDFSA066MSFRBPHI","PPFDFSA066MSFRBPHI","PRFDFSA066MSFRBPHI",
    "CEFDFSA066MSFRBPHI","NOFDISA066MSFRBNY","PPFDISA066MSFRBNY","CEFDISA066MSFRBNY"]),
 ("regionalfed_current","demand-activity","Regional-Fed survey CURRENT diffusion; near-real-time activity/price reading (largely coincident).",
   ["GACDFSA066MSFRBPHI","NOCDFSA066MSFRBPHI","PPCDFSA066MSFRBPHI","PRCDFSA066MSFRBPHI",
    "DTCDFSA066MSFRBPHI","UOCDFSA066MSFRBPHI","NECDFSA066MSFRBPHI","GACDISA066MSFRBNY",
    "NOCDISA066MSFRBNY","PPCDISA066MSFRBNY","DTCDISA066MSFRBNY"]),
 ("commodity","triangulation","Global commodity benchmark; triangulates the traded-input price cycle (may duplicate a domestic force).",
   ["POILBREUSDM","PIORECRUSDM","PNGASUSUSDM","POILWTIUSDM","PCOALAUUSDM","PURANUSDM","PRUBBUSDM"]),
 ("ip","demand-activity","Industrial production for a related industry; the output cycle (largely coincident with prices).",
   ["IPMINE","IPG331S","IPG332S","IPG333S","IPG335S","IPG3311A2S","IPGMFN","IPDMAT","IPB50089S","IPMAT"]),
 ("capacity","demand-activity","Capacity utilization for a related industry; supply tightness that can precede price pressure.",
   ["CAPUTLG331S","CAPUTLG333S","CAPUTLG335S"]),
 ("employment","demand-activity","Sector employment; an activity proxy (coincident/lagging).",
   ["CES3133100001","CES3133200001","CES3133300001","CES1021100001","USCONS"]),
 ("mfg_price","price-broad","Broad manufacturing producer price; expected to co-move with transformer prices rather than lead.",
   ["PCUOMFGOMFG"]),
]

PPI_TEMPL = {"metals":"Producer price for a metals/metal-products group — a material-input signal; included to map the force structure and triangulate (expected co-mover).",
    "chemicals":"Producer price for a chemicals group (resins, coatings, treatment chemicals) — a non-metal input signal (expected co-mover).",
    "plastics_rubber":"Producer price for a plastics/rubber-products group — insulation/enclosure input (expected co-mover).",
    "fuels_power":"Producer price for a fuels-and-power group — energy input to metal production and fabrication (expected co-mover).",
    "machinery":"Producer price for a machinery/equipment group — sibling capital-goods price (expected co-mover)."}


def api_titles(ids):
    out = {}
    for i in range(0, len(ids), 1):
        sid = ids[i]
        url = f"https://api.stlouisfed.org/fred/series?series_id={sid}&api_key={KEY}&file_type=json"
        for _ in range(3):
            r = subprocess.run(["curl","-sSL","--http1.1","--max-time","30",url], capture_output=True)
            if r.returncode == 0 and r.stdout:
                try:
                    out[sid] = json.loads(r.stdout)["seriess"][0]["title"]; break
                except Exception: pass
            time.sleep(0.5)
    return out


def clean_label(title, cat):
    for pre in ["Producer Price Index by Commodity: ","Producer Price Index by Industry: ",
                "Global price of ","Industrial Production: ","Capacity Utilization: ",
                "All Employees, ","Import Price Index (End Use): ","Import Price Index: ",
                "Manufacturers' ","Total Construction Spending: ","New Privately-Owned Housing Units ",
                "Market Yield on U.S. Treasury Securities at ","Moody's Seasoned ",
                "University of Michigan: "]:
        if title.startswith(pre): title = title[len(pre):]
    title = title.split(" for Federal Reserve")[0].split(" for New York")[0].split(" in the United States")[0]
    title = title.replace("; Diffusion Index","").replace("Diffusion Index","").strip(" ,;")
    return (title[:44]).strip()


# --- curate PPI sample: group-level codes (short WPU), diverse, capped per category ---
ppi = json.load(open(PPITREE))
CAPS = {"metals":22,"chemicals":12,"plastics_rubber":8,"fuels_power":10,"machinery":16}
ppi_pick = []  # (id, cat, title)
for cat, series in ppi.items():
    items = [(sid,t) for sid,t in series.items()
             if sid.startswith("WPU") and sid not in EXISTING and 5 <= len(sid) <= 7]
    items.sort(key=lambda x:(len(x[0]), x[0]))     # prefer higher-level groups
    for sid,t in items[:CAPS.get(cat,10)]:
        ppi_pick.append((sid, "ppi_"+cat, t)); EXISTING.add(sid)

# --- assemble rows ---
rows = []
allids = []
for cat, tier, mech, ids in FAM:
    for sid in ids:
        if sid in EXISTING: continue
        EXISTING.add(sid); allids.append(sid)
        rows.append(dict(fred_id=sid, category=cat, tier=tier, mechanism=mech, label=""))
for sid, cat, t in ppi_pick:
    allids.append(sid)
    base = cat.replace("ppi_","")
    rows.append(dict(fred_id=sid, category=cat, tier="price-broad",
                     mechanism=PPI_TEMPL.get(base,"Producer-price input signal (expected co-mover)."),
                     label="", _title=t))

# titles for label
titles = api_titles([r["fred_id"] for r in rows if not r.get("_title")])
for r in rows:
    t = r.get("_title") or titles.get(r["fred_id"], r["fred_id"])
    r["label"] = clean_label(t, r["category"])
    r.pop("_title", None)
    r["note"] = ""

with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["fred_id","label","category","tier","mechanism","note"])
    w.writeheader()
    for r in rows: w.writerow(r)
print(f"wrote {len(rows)} new candidates to {OUT}")
print("by category:", {c: sum(1 for r in rows if r['category']==c) for c in sorted({r['category'] for r in rows})})
