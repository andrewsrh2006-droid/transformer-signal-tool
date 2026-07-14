"""Series catalogue: the outcome and every candidate leading signal.

Each candidate carries a *written mechanism* (required by the brief). The `group`
tag is an a-priori guess at which underlying force a signal represents; it is only
used for commentary — the actual independence check is the data-driven
correlation-of-correlations matrix, not these tags.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Series:
    fred_id: str
    label: str          # short human label used in tables/charts
    mechanism: str      # why it might lead transformer prices
    group: str          # a-priori family / category (commentary only)
    starter: bool       # True = from the brief's starter set; False = self-added
    note: str = ""      # any caveat (e.g. proxy)
    tier: str = ""      # mechanism tier: input-direct/upstream, demand-forward,
                        # demand-activity, financial-forward, triangulation, price-broad


# ---- Outcome (the thing being predicted) --------------------------------------
OUTCOME = Series(
    fred_id="PCU335311335311",
    label="Transformer PPI (outcome)",
    mechanism="PPI for Electric Power & Specialty Transformer Manufacturing — the outcome.",
    group="outcome",
    starter=True,
)

# ---- Candidate leading signals ------------------------------------------------
CANDIDATES = [
    # --- Starter set (Section 8 of the brief) ---
    Series("WPUSI019011", "Copper PPI", "Copper is the primary conductor for transformer "
           "windings; its input price feeds directly into finished transformer cost.",
           "copper", True),
    Series("WPU102501", "Aluminum mill shapes PPI", "Aluminum is the main alternative "
           "winding conductor and is used in housings and radiators.", "aluminum", True),
    Series("WPU101", "Iron & steel PPI", "Electrical (silicon) steel forms the transformer "
           "core; broad iron & steel prices proxy that core-metal cost.", "steel", True),
    Series("WPU1012", "Iron & steel scrap PPI", "Scrap is the feedstock for electric-arc "
           "steelmaking; it sits upstream of finished steel and may lead it.", "steel", True),
    Series("PCOPPUSDM", "Global copper price", "Independent global (LME-based) copper "
           "benchmark; triangulates the domestic copper PPI.", "copper", True),
    Series("PALUMUSDM", "Global aluminum price", "Independent global aluminum benchmark; "
           "triangulates the domestic aluminum PPI.", "aluminum", True),
    Series("PNICKUSDM", "Global nickel price", "Nickel alloys electrical steels and "
           "stainless components; a global proxy for alloying-input cost.", "nickel", True),
    Series("WTISPLC", "WTI crude oil", "Energy is a major cost in smelting, rolling and "
           "transformer fabrication; crude oil proxies broad energy cost.", "energy", True),
    Series("WPU117", "Electrical machinery & equip. PPI", "Broad electrical-goods price "
           "level; a sibling output market that may co-move with transformers.",
           "downstream", True),
    Series("IPUTIL", "Industrial production: utilities", "Utility output proxies grid-side "
           "demand; stronger grid activity can pull transformer demand and price.",
           "demand", True),
    Series("MANEMP", "Manufacturing employment", "General manufacturing labour demand; "
           "included as a negative-control anchor (weak expected link, per the brief).",
           "macro", True, note="Anchor / negative control."),

    # --- Self-added signals (each with a mechanism, per user instruction) ---
    Series("WPU101707", "Cold-rolled steel sheet (GOES proxy)",
           "Grain-oriented electrical steel — the transformer CORE material — is a "
           "specialised cold-rolled silicon-steel sheet. FRED has no GOES-specific series, "
           "so cold-rolled steel sheet & strip is the closest public PPI to the core input. "
           "Mechanistically the strongest single candidate.",
           "steel", False, note="Proxy for grain-oriented electrical steel (GOES); no exact "
           "GOES PPI exists on FRED."),
    Series("WPU1026", "Nonferrous wire & cable PPI",
           "The literal wound-conductor product (copper/aluminum wire & cable) that goes "
           "into windings — one step downstream of raw metal, one step upstream of the "
           "finished transformer.", "wire", False),
    Series("WPU1011", "Iron ores PPI",
           "Deepest upstream input to the steel core (ore -> steel -> electrical steel); "
           "may lead finished steel, and thus transformers, at the longest horizon.",
           "steel", False),
    Series("WPU0576", "Finished lubricants PPI",
           "Proxy for transformer insulating/mineral oil, a genuine dielectric-coolant "
           "input to oil-filled transformers; refined-oil cost distinct from crude.",
           "energy", False),

    # ===== Expansion to 30: more categories, each with a mechanism =====
    # --- Base metals (triangulate the metals cycle; some direct uses) ---
    Series("PZINCUSDM", "Global zinc price",
           "Zinc galvanises steel transformer tanks, enclosures and structural steel; also a "
           "core member of the base-metals price cycle that feeds equipment cost.",
           "basemetal", False),
    Series("PLEADUSDM", "Global lead price",
           "Lead is used in cable sheathing, some electrical components and counterweights, "
           "and triangulates the broad non-ferrous base-metals cycle.", "basemetal", False),
    Series("PTINUSDM", "Global tin price",
           "Tin is the solder that joins electrical connections in transformers, switchgear "
           "and assemblies; its price tracks connection/joint material cost.", "basemetal", False),
    # --- Steel mill products ---
    Series("WPU1017", "Steel mill products PPI",
           "Broad finished steel (sheet, plate, structural) fabricated into transformer "
           "tanks, cores and mountings — one step downstream of raw iron & steel.",
           "steel", False),
    Series("WPU101705", "Steel wire PPI",
           "Steel wire is used for core banding, tie/support wire and structural bracing "
           "inside coils and assemblies.", "steel", False),
    # --- Transformer / insulating materials ---
    Series("WPU057", "Refined petroleum products PPI",
           "Transformer insulating/mineral oil is a refined-petroleum product; this also "
           "proxies broad energy and fabrication cost feeding equipment prices.",
           "energy", False),
    Series("WPU072", "Plastic products PPI",
           "Plastics form insulation, bushings, coil formers and enclosures in transformers "
           "and switchgear; a genuine non-metal input.", "materials", False),
    # --- Energy ---
    Series("WPU0531", "Natural gas PPI",
           "Natural gas is a major energy input to metal smelting, rolling and component "
           "fabrication (and to grid gas generation); an upstream cost driver.",
           "energy", False),
    Series("WPU054", "Electric power PPI",
           "Electricity is a dominant cost in aluminium and steel production and in "
           "fabrication; grid electricity price proxies that energy input.", "energy", False),
    # --- Grid-demand & macro ---
    Series("IPMAN", "Industrial production: manufacturing",
           "Broad manufacturing output cycle; rising activity pulls electrical-equipment "
           "orders and tightens input-material demand ahead of price moves.", "demand", False),
    Series("MCUMFN", "Capacity utilization: manufacturing",
           "High utilisation signals supply tightness across manufacturing, which precedes "
           "upward pressure on equipment and input prices.", "demand", False),
    Series("A35SNO", "New orders: electrical equipment",
           "Manufacturers' new orders for electrical equipment, appliances & components — a "
           "direct forward-demand signal for the very goods transformers belong to; orders "
           "lead shipments and prices.", "demand", False),
    Series("TLPWRCONS", "Construction spending: power",
           "Spending on power/grid construction directly pulls demand for transformers and "
           "grid equipment; the build cycle should lead equipment prices.", "demand", False),
    Series("CES3133500001", "Employment: electrical-equip mfg",
           "Payrolls in electrical-equipment, appliance & component manufacturing proxy "
           "sector activity; hiring tracks the production/pricing cycle for this industry.",
           "macro", False),
    # --- Forward / financial ---
    Series("GS10", "10-Year Treasury yield",
           "Financing cost for capital-intensive grid and utility investment; rate moves lead "
           "the capex/build cycle that drives transformer demand. (Caveat: YoY of a yield is "
           "an unusual transform — interpret with care.)", "financial", False),
]

# Broad commodity-market control (NOT a candidate) — used to strip the general
# commodity cycle out of each confirmed signal (partial correlation + relative series).
MARKET = Series(
    fred_id="PPIACO",
    label="All-commodities PPI (market control)",
    mechanism="Broad Producer Price Index for all commodities; proxy for the general "
              "commodity/industrial-price cycle common to every metal input.",
    group="market",
    starter=False,
    note="Control variable, not scored as a candidate.",
)

# Lag search window (months). Positive lag = candidate leads outcome.
MAX_LAG = 24

# Thresholds from the brief.
R_MIN_SCREEN = 0.30        # minimum |r| to pass the robustness screen
R_STRONG = 0.50           # |r| threshold for CONFIRMED / strong
CLUSTER_R = 0.70          # >= this contemporaneous |r| => same underlying force
# When True, a force must be a TIGHT cluster (every member >=0.70 with every other, i.e. it
# would survive complete linkage). ANY loose force — same-sign OR opposite-sign — is split
# with complete linkage into its tight pieces and each piece is re-tested from scratch, so no
# loose force ever reaches the leaderboard. When False, only opposite-sign loose forces split.
FORCES_MUST_BE_TIGHT = True

# Production clustering linkage. "complete" makes every cluster tight by construction (every
# pair >=0.70), so no loose grab-bag ever forms and the split machinery is a no-op fallback.
# Set to "average" to revert to the older average-linkage-then-split behaviour. (The
# average-vs-complete comparison lives on as a diagnostic in tools/linkage_compare.py.)
CLUSTER_LINKAGE = "complete"

# A signal whose aligned overlap with the outcome is shorter than this (months) is EXCLUDED
# from force formation entirely — it is already quarantined individually (short-sample), and
# because a composite/force is only as long as its shortest member, one short member would
# truncate an otherwise decades-long force's window. It still appears in the per-signal
# leaderboard; it just never joins a cluster or a composite.
FORCE_MIN_MONTHS = 150
SIG_ALPHA = 0.05          # permutation significance level
N_SURROGATES = 1000       # circular-shift permutation surrogates (brief min 500)
N_BOOTSTRAP = 2000        # moving-block bootstrap resamples (brief min 1000)
BLOCK_LEN = 12            # bootstrap block length (months)
SMOOTH_WIN = 6           # centered rolling-mean window for the smoothing gate

# ---- Load harvested/expanded candidates from a manifest (keeps the 30 above as seed).
# The manifest is machine-generated (tools/build_manifest.py) so 200+ signals don't have
# to be hand-written here. Each row: fred_id,label,category,tier,starter,mechanism.
import csv as _csv
import os as _os

_MANIFEST = _os.path.join(_os.path.dirname(__file__), "signals_extra.csv")


def _load_manifest(path):
    extra = []
    if not _os.path.exists(path):
        return extra
    seen = {c.fred_id for c in CANDIDATES}
    with open(path, newline="") as fh:
        for row in _csv.DictReader(fh):
            fid = row["fred_id"].strip()
            if not fid or fid in seen:
                continue
            seen.add(fid)
            extra.append(Series(fid, row["label"].strip(), row["mechanism"].strip(),
                                row["category"].strip(), False,
                                note=row.get("note", "").strip(), tier=row.get("tier", "").strip()))
    return extra


CANDIDATES = CANDIDATES + _load_manifest(_MANIFEST)

ALL_SERIES = [OUTCOME] + CANDIDATES + [MARKET]
