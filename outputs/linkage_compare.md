# Linkage comparison — average vs complete (chain-effect diagnostic)

Same lag-0 YoY correlation matrix (192 signals), same cut **r ≥ 0.70**. Read-only; the production clustering is unchanged.

| Method | Multi-signal clusters | Singletons | **Total forces** |
|--------|-----------------------|-----------|------------------|
| Average (UPGMA, production) | 31 | 39 | **70** |
| Complete (max-linkage) | 45 | 39 | **84** |

*Tightness* = the weakest internal link (minimum pairwise r between any two members). A tightness well below the 0.70 cut means members were joined transitively, not because they are all mutually ≥0.70 correlated — the chain effect.

## Average linkage — 31 multi-signal clusters

| Size | Tightness (min pairwise r) | Members (peak r @ lead) |
|------|----------------------------|-------------------------|
| 24 ⚠️ | +0.52 | Machinery and Equipment: Agricultural Machin (+0.86@-3), Metals and Metal Products: Heating Equipment (+0.82@-1), Machinery and Equipment: Miscellaneous Const (+0.81@-2), Metals and Metal Products: Hardware, Not Els (+0.79@+0), Chemicals and Allied Products: Prepared Pain (+0.79@-1), Machinery and Equipment: Agricultural Machin (+0.76@-2), Metals and Metal Products: Hardware (+0.76@-1), Machinery and Equipment: General Purpose Mac (+0.76@-1), Chemicals and Allied Products: Paints and Al (+0.75@+0), Metals and Metal Products: Foundry and Forge (+0.74@-1), Metals and Metal Products: Miscellaneous Met (+0.73@+0), Fuels and Related Products and Power: Reside (+0.73@-6), Metals and Metal Products: Metal Containers (+0.73@+0), Machinery and Equipment: Special Industry Ma (+0.70@-1), Metals and Metal Products: Metal Cans and Ca (+0.69@-1), Chemicals and Allied Products: Other Chemica (+0.69@+0), Machinery and Equipment (+0.67@-2), Machinery and Equipment: Construction Machin (+0.67@-2), Machinery and Equipment: Miscellaneous Machi (+0.66@-3), Machinery and Equipment: Metalworking Machin (+0.63@-1), Rubber and Plastic Products: Laminated Plast (+0.61@+0), Electric power PPI (+0.60@-1), Electrical machinery & equip. PPI (+0.59@-1), Metals and Metal Products: Hand and Edge Too (+0.58@-2) |
| 19 ⚠️ | +0.52 | New Orders: Total Manufacturing (+0.55@+3), New Orders: Primary Metals (+0.55@+5), New Orders: Fabricated Metal Products (+0.47@+3), New Orders: Nondefense Capital Goods Excludi (+0.42@+3), New Orders: Machinery (+0.41@+3), New Orders: Durable Goods (+0.38@+6), Manufacturing: Durable Goods: Primary Metal (-0.31@-10), Industrial production: manufacturing (-0.31@-8), Manufacturing (-0.31@-8), Capacity utilization: manufacturing (-0.31@-8), Durable Goods Materials: Durable Goods Mater (-0.30@-9), Manufacturing: Durable Goods: Electrical Equ (-0.30@-7), Manufacturing: Durable Goods: Machinery (-0.29@-14), Manufacturing: Durable Goods: Primary Metal (-0.27@-10), Materials (-0.27@-8), Manufacturing: Durable Goods: Machinery (-0.26@-13), Manufacturing: Durable Goods: Iron and Steel (-0.26@-10), Manufacturing: Durable Goods: Electrical Equ (-0.25@-6), Manufacturing: Durable Goods: Fabricated Met (-0.25@-12) |
| 11 ⚠️ | +0.45 | Import: Copper (+0.86@+10), Nonferrous wire & cable PPI (+0.68@+6), Metals and Metal Products: Nonferrous Mill S (+0.65@+6), Metals and Metal Products: Nonferrous Metals (+0.60@+7), Global aluminum price (+0.56@+5), Metals and Metal Products: Primary Nonferrou (+0.54@+7), Metals and Metal Products: Secondary Nonferr (+0.54@+8), Global copper price (+0.53@+7), Copper PPI (+0.53@+8), Metals and Metal Products: Nonferrous Scrap (+0.48@+11), Metals and Metal Products: Nonferrous Metal (+0.40@+6) |
| 10 ⚠️ | +0.55 | Metals and Metal Products (+0.78@+5), Chemicals and Allied Products (+0.72@+2), Cold-rolled steel sheet (+0.71@+6), Chemicals and Allied Products: Industrial Ch (+0.71@+2), Import: Ind. Supplies & Materials (+0.68@+3), Iron & steel PPI (+0.67@+4), Steel mill products PPI (+0.66@+4), Import: Ind. Supplies & Materials (+0.64@+5), Chemicals and Allied Products: Basic Organic (+0.62@+2), Chemicals and Allied Products: Plastic Resin (+0.60@+4) |
| 10 ⚠️ | +0.52 | Transportation Services: Truck Transportatio (+0.81@+2), Truck Transportation (+0.80@+1), Total Manufacturing Industries (+0.80@+1), Metals and Metal Products: Fabricated Struct (+0.80@+2), Rubber and Plastic Products (+0.80@+2), Plastic products PPI (+0.78@+2), Rubber and Plastic Products: Unsupported Pla (+0.74@+2), Coal, Australia (+0.74@+2), Rubber and Plastic Products: Plastic Constru (+0.70@+3), Metals and Metal Products: Barrels, Drums, P (+0.69@+2) |
| 7 | +0.80 | Refined petroleum products PPI (+0.62@+3), Import: Industrial Supplies & Materials (+0.60@+2), WTI crude oil (+0.59@+5), WTI Crude (+0.55@+3), Fuels and Related Products and Power: Natura (+0.54@+5), Brent Crude (+0.53@+3), Fuels and Related Products and Power: Crude (+0.52@+3) |
| 7 ⚠️ | +0.68 | 5-Year Breakeven Inflation Rate (+0.47@+6), Current Prices Paid (-0.45@-11), Current Prices Received (-0.42@-8), Future Prices Paid (-0.42@-10), Current Prices Paid (-0.41@-8), Future Prices Received (-0.33@-7), Future Prices Paid (-0.27@-8) |
| 5 | +0.86 | Machinery Manufacturing (+0.37@-3), Primary Metal Manufacturing (+0.36@-2), Employment: electrical-equip mfg (+0.32@-2), Fabricated Metal Product Manufacturing (+0.29@-1), Manufacturing employment (-0.12@-12) |
| 5 | +0.71 | Residential (-0.49@-14), Authorized in Permit-Issuing Places: Single- (-0.34@-3), Started: Single-Family Units (-0.33@-4), Authorized in Permit-Issuing Places: Total U (-0.31@-2), Started: Total Units (-0.31@-2) |
| 5 ⚠️ | +0.64 | 30-Year Fixed Rate Mortgage Average (+0.56@-3), Baa Corporate Bond Yield (+0.53@-5), 10-Year Constant Maturity, Quoted on an Inve (+0.52@-7), 10-Year Treasury yield (+0.48@+2), Aaa Corporate Bond Yield (+0.46@-1) |
| 4 | +0.75 | Fuels and Related Products and Power: Gas Fu (+0.45@+3), Fuels and Related Products and Power: Utilit (+0.40@+1), Natural gas PPI (+0.38@+3), Natural Gas, US Henry Hub Gas (+0.33@+2) |
| 4 ⚠️ | +0.69 | Machinery and Equipment: Mixers, Pavers, and (+0.70@-4), Machinery and Equipment: Tractors and Attach (+0.68@-7), Machinery and Equipment: Power Cranes, Dragl (+0.61@-9), Machinery and Equipment: Off-Highway, Equipm (+0.59@-10) |
| 3 | +1.00 | Fuels and Related Products and Power: Coal (+0.57@-1), Fuels and Related Products and Power: Coal (+0.57@-1), Fuels and Related Products and Power: Bitumi (+0.55@-1) |
| 3 | +0.81 | Rubber and Plastic Products: Miscellaneous R (+0.71@-2), Rubber and Plastic Products: Rubber and Rubb (+0.69@+0), Rubber and Plastic Products: Tires, Tubes, T (+0.64@-1) |
| 3 | +0.79 | 2-Year Constant Maturity, Quoted on an Inves (+0.70@-2), 1-Year Constant Maturity, Quoted on an Inves (+0.55@-3), 3-Month Treasury Bill Secondary Market Rate, (+0.51@-5) |
| 3 | +0.79 | Current Unfilled Orders (-0.29@-3), Current New Orders (-0.22@-3), Current General Activity (-0.21@-1) |
| 2 | +0.96 | Nominal Broad U.S. Dollar Index (-0.37@+6), Nominal Advanced Foreign Economies U.S. Doll (-0.33@+7) |
| 2 | +0.96 | Global zinc price (+0.47@+5), Import: Zinc (-0.46@-17) |
| 2 | +0.94 | Future New Orders (+0.21@-22), Future General Activity (+0.20@-24) |
| 2 | +0.94 | Current General Business Conditions (-0.37@-8), Current New Orders (-0.37@-8) |
| 2 | +0.89 | 5-Year, 5-Year Forward Inflation Expectation (+0.33@+7), 10-Year Breakeven Inflation Rate (+0.24@+7) |
| 2 | +0.88 | Baa Corporate Bond Yield Relative to Yield o (-0.25@+9), Aaa Corporate Bond Yield Relative to Yield o (-0.24@+9) |
| 2 | +0.87 | Total Business: Inventories to Sales Ratio (+0.39@-9), Manufacturers: Inventories to Sales Ratio (+0.34@-10) |
| 2 | +0.86 | Energy, Total (-0.29@+20), Mining: Mining (-0.26@+19) |
| 2 | +0.84 | 10-Year Treasury Constant Maturity Minus 2-Y (+0.29@-24), 10-Year Treasury Constant Maturity Minus 3-M (-0.22@-8) |
| 2 | +0.81 | Metals and Metal Products: Plumbing Fixtures (+0.62@+1), Metals and Metal Products: Vitreous China Pl (+0.39@+0) |
| 2 | +0.80 | Construction (-0.28@-10), Total Construction (-0.25@-24) |
| 2 | +0.79 | Chemicals and Allied Products: Agricultural (+0.69@-1), Chemicals and Allied Products: Basic Inorgan (+0.69@-3) |
| 2 | +0.77 | Manufacturing (+0.65@-10), Nonresidential (+0.60@-10) |
| 2 | +0.75 | Fuels and Related Products and Power: Anthra (+0.66@-3), Machinery and Equipment: Parts for Construct (+0.32@-3) |
| 2 | +0.72 | Future Capital Expenditures (-0.38@-11), Current Employment (-0.26@-8) |

## Complete linkage — 45 multi-signal clusters

| Size | Tightness (min pairwise r) | Members (peak r @ lead) |
|------|----------------------------|-------------------------|
| 10 | +0.74 | Industrial production: manufacturing (-0.31@-8), Manufacturing (-0.31@-8), Capacity utilization: manufacturing (-0.31@-8), Durable Goods Materials: Durable Goods Mater (-0.30@-9), Manufacturing: Durable Goods: Electrical Equ (-0.30@-7), Manufacturing: Durable Goods: Machinery (-0.29@-14), Materials (-0.27@-8), Manufacturing: Durable Goods: Machinery (-0.26@-13), Manufacturing: Durable Goods: Electrical Equ (-0.25@-6), Manufacturing: Durable Goods: Fabricated Met (-0.25@-12) |
| 8 | +0.80 | Machinery and Equipment: General Purpose Mac (+0.76@-1), Machinery and Equipment: Special Industry Ma (+0.70@-1), Machinery and Equipment (+0.67@-2), Machinery and Equipment: Construction Machin (+0.67@-2), Machinery and Equipment: Miscellaneous Machi (+0.66@-3), Machinery and Equipment: Metalworking Machin (+0.63@-1), Electrical machinery & equip. PPI (+0.59@-1), Metals and Metal Products: Hand and Edge Too (+0.58@-2) |
| 7 | +0.80 | Refined petroleum products PPI (+0.62@+3), Import: Industrial Supplies & Materials (+0.60@+2), WTI crude oil (+0.59@+5), WTI Crude (+0.55@+3), Fuels and Related Products and Power: Natura (+0.54@+5), Brent Crude (+0.53@+3), Fuels and Related Products and Power: Crude (+0.52@+3) |
| 6 | +0.75 | Machinery and Equipment: Agricultural Machin (+0.86@-3), Metals and Metal Products: Heating Equipment (+0.82@-1), Machinery and Equipment: Miscellaneous Const (+0.81@-2), Metals and Metal Products: Hardware, Not Els (+0.79@+0), Machinery and Equipment: Agricultural Machin (+0.76@-2), Metals and Metal Products: Hardware (+0.76@-1) |
| 6 | +0.71 | New Orders: Total Manufacturing (+0.55@+3), New orders: electrical equipment (+0.50@+1), New Orders: Fabricated Metal Products (+0.47@+3), New Orders: Nondefense Capital Goods Excludi (+0.42@+3), New Orders: Machinery (+0.41@+3), New Orders: Durable Goods (+0.38@+6) |
| 5 | +0.86 | Machinery Manufacturing (+0.37@-3), Primary Metal Manufacturing (+0.36@-2), Employment: electrical-equip mfg (+0.32@-2), Fabricated Metal Product Manufacturing (+0.29@-1), Manufacturing employment (-0.12@-12) |
| 5 | +0.83 | Import: Copper (+0.86@+10), Global aluminum price (+0.56@+5), Global copper price (+0.53@+7), Copper PPI (+0.53@+8), Metals and Metal Products: Nonferrous Scrap (+0.48@+11) |
| 5 | +0.76 | Metals and Metal Products (+0.78@+5), Import: Ind. Supplies & Materials (+0.68@+3), Nonferrous wire & cable PPI (+0.68@+6), Metals and Metal Products: Nonferrous Mill S (+0.65@+6), Import: Ind. Supplies & Materials (+0.64@+5) |
| 5 | +0.71 | Residential (-0.49@-14), Authorized in Permit-Issuing Places: Single- (-0.34@-3), Started: Single-Family Units (-0.33@-4), Authorized in Permit-Issuing Places: Total U (-0.31@-2), Started: Total Units (-0.31@-2) |
| 4 | +0.88 | Chemicals and Allied Products (+0.72@+2), Chemicals and Allied Products: Industrial Ch (+0.71@+2), Chemicals and Allied Products: Basic Organic (+0.62@+2), Chemicals and Allied Products: Plastic Resin (+0.60@+4) |
| 4 | +0.84 | Current Prices Paid (-0.45@-11), Current Prices Received (-0.42@-8), Future Prices Paid (-0.42@-10), Current Prices Paid (-0.41@-8) |
| 4 | +0.83 | New Orders: Primary Metals (+0.55@+5), Manufacturing: Durable Goods: Primary Metal (-0.31@-10), Manufacturing: Durable Goods: Primary Metal (-0.27@-10), Manufacturing: Durable Goods: Iron and Steel (-0.26@-10) |
| 4 | +0.83 | Metals and Metal Products: Nonferrous Metals (+0.60@+7), Metals and Metal Products: Primary Nonferrou (+0.54@+7), Metals and Metal Products: Secondary Nonferr (+0.54@+8), Metals and Metal Products: Nonferrous Metal (+0.40@+6) |
| 4 | +0.81 | Rubber and Plastic Products (+0.80@+2), Plastic products PPI (+0.78@+2), Rubber and Plastic Products: Unsupported Pla (+0.74@+2), Rubber and Plastic Products: Plastic Constru (+0.70@+3) |
| 4 | +0.80 | 30-Year Fixed Rate Mortgage Average (+0.56@-3), Baa Corporate Bond Yield (+0.53@-5), 10-Year Constant Maturity, Quoted on an Inve (+0.52@-7), Aaa Corporate Bond Yield (+0.46@-1) |
| 4 | +0.79 | Transportation Services: Truck Transportatio (+0.81@+2), Truck Transportation (+0.80@+1), Total Manufacturing Industries (+0.80@+1), Coal, Australia (+0.74@+2) |
| 4 | +0.75 | Fuels and Related Products and Power: Gas Fu (+0.45@+3), Fuels and Related Products and Power: Utilit (+0.40@+1), Natural gas PPI (+0.38@+3), Natural Gas, US Henry Hub Gas (+0.33@+2) |
| 4 | +0.73 | Metals and Metal Products: Foundry and Forge (+0.74@-1), Metals and Metal Products: Miscellaneous Met (+0.73@+0), Metals and Metal Products: Metal Containers (+0.73@+0), Metals and Metal Products: Metal Cans and Ca (+0.69@-1) |
| 4 | +0.72 | Chemicals and Allied Products: Prepared Pain (+0.79@-1), Chemicals and Allied Products: Paints and Al (+0.75@+0), Chemicals and Allied Products: Other Chemica (+0.69@+0), Rubber and Plastic Products: Laminated Plast (+0.61@+0) |
| 3 | +1.00 | Fuels and Related Products and Power: Coal (+0.57@-1), Fuels and Related Products and Power: Coal (+0.57@-1), Fuels and Related Products and Power: Bitumi (+0.55@-1) |
| 3 | +0.89 | Cold-rolled steel sheet (+0.71@+6), Iron & steel PPI (+0.67@+4), Steel mill products PPI (+0.66@+4) |
| 3 | +0.81 | Rubber and Plastic Products: Miscellaneous R (+0.71@-2), Rubber and Plastic Products: Rubber and Rubb (+0.69@+0), Rubber and Plastic Products: Tires, Tubes, T (+0.64@-1) |
| 3 | +0.79 | Current Unfilled Orders (-0.29@-3), Current New Orders (-0.22@-3), Current General Activity (-0.21@-1) |
| 2 | +0.96 | Fuels and Related Products and Power: Reside (+0.73@-6), Electric power PPI (+0.60@-1) |
| 2 | +0.96 | Nominal Broad U.S. Dollar Index (-0.37@+6), Nominal Advanced Foreign Economies U.S. Doll (-0.33@+7) |
| 2 | +0.96 | Global zinc price (+0.47@+5), Import: Zinc (-0.46@-17) |
| 2 | +0.94 | 2-Year Constant Maturity, Quoted on an Inves (+0.70@-2), 1-Year Constant Maturity, Quoted on an Inves (+0.55@-3) |
| 2 | +0.94 | Future New Orders (+0.21@-22), Future General Activity (+0.20@-24) |
| 2 | +0.94 | Current General Business Conditions (-0.37@-8), Current New Orders (-0.37@-8) |
| 2 | +0.89 | 5-Year, 5-Year Forward Inflation Expectation (+0.33@+7), 10-Year Breakeven Inflation Rate (+0.24@+7) |
| 2 | +0.88 | Baa Corporate Bond Yield Relative to Yield o (-0.25@+9), Aaa Corporate Bond Yield Relative to Yield o (-0.24@+9) |
| 2 | +0.87 | Total Business: Inventories to Sales Ratio (+0.39@-9), Manufacturers: Inventories to Sales Ratio (+0.34@-10) |
| 2 | +0.87 | Metals and Metal Products: Fabricated Struct (+0.80@+2), Metals and Metal Products: Barrels, Drums, P (+0.69@+2) |
| 2 | +0.86 | Energy, Total (-0.29@+20), Mining: Mining (-0.26@+19) |
| 2 | +0.86 | Machinery and Equipment: Tractors and Attach (+0.68@-7), Machinery and Equipment: Off-Highway, Equipm (+0.59@-10) |
| 2 | +0.84 | 10-Year Treasury Constant Maturity Minus 2-Y (+0.29@-24), 10-Year Treasury Constant Maturity Minus 3-M (-0.22@-8) |
| 2 | +0.81 | Future Prices Received (-0.33@-7), Future Prices Paid (-0.27@-8) |
| 2 | +0.81 | Metals and Metal Products: Plumbing Fixtures (+0.62@+1), Metals and Metal Products: Vitreous China Pl (+0.39@+0) |
| 2 | +0.80 | Federal Funds Effective Rate (+0.53@-7), 3-Month Treasury Bill Secondary Market Rate, (+0.51@-5) |
| 2 | +0.80 | Construction (-0.28@-10), Total Construction (-0.25@-24) |
| 2 | +0.79 | Chemicals and Allied Products: Agricultural (+0.69@-1), Chemicals and Allied Products: Basic Inorgan (+0.69@-3) |
| 2 | +0.77 | Manufacturing (+0.65@-10), Nonresidential (+0.60@-10) |
| 2 | +0.75 | Fuels and Related Products and Power: Anthra (+0.66@-3), Machinery and Equipment: Parts for Construct (+0.32@-3) |
| 2 | +0.74 | Machinery and Equipment: Mixers, Pavers, and (+0.70@-4), Machinery and Equipment: Power Cranes, Dragl (+0.61@-9) |
| 2 | +0.72 | Future Capital Expenditures (-0.38@-11), Current Employment (-0.26@-8) |

## Stability: which forces are robust vs artifacts

**22 robust force(s)** — the exact same member set is a cluster under BOTH average and complete linkage. Keep these.

- **(7, tightness +0.80)** Refined petroleum products PPI (+0.62@+3), Import: Industrial Supplies & Materials (+0.60@+2), WTI crude oil (+0.59@+5), WTI Crude (+0.55@+3), Fuels and Related Products and Power: Natura (+0.54@+5), Brent Crude (+0.53@+3), Fuels and Related Products and Power: Crude (+0.52@+3)
- **(5, tightness +0.71)** Residential (-0.49@-14), Authorized in Permit-Issuing Places: Single- (-0.34@-3), Started: Single-Family Units (-0.33@-4), Authorized in Permit-Issuing Places: Total U (-0.31@-2), Started: Total Units (-0.31@-2)
- **(5, tightness +0.86)** Machinery Manufacturing (+0.37@-3), Primary Metal Manufacturing (+0.36@-2), Employment: electrical-equip mfg (+0.32@-2), Fabricated Metal Product Manufacturing (+0.29@-1), Manufacturing employment (-0.12@-12)
- **(4, tightness +0.75)** Fuels and Related Products and Power: Gas Fu (+0.45@+3), Fuels and Related Products and Power: Utilit (+0.40@+1), Natural gas PPI (+0.38@+3), Natural Gas, US Henry Hub Gas (+0.33@+2)
- **(3, tightness +0.81)** Rubber and Plastic Products: Miscellaneous R (+0.71@-2), Rubber and Plastic Products: Rubber and Rubb (+0.69@+0), Rubber and Plastic Products: Tires, Tubes, T (+0.64@-1)
- **(3, tightness +0.79)** Current Unfilled Orders (-0.29@-3), Current New Orders (-0.22@-3), Current General Activity (-0.21@-1)
- **(3, tightness +1.00)** Fuels and Related Products and Power: Coal (+0.57@-1), Fuels and Related Products and Power: Coal (+0.57@-1), Fuels and Related Products and Power: Bitumi (+0.55@-1)
- **(2, tightness +0.88)** Baa Corporate Bond Yield Relative to Yield o (-0.25@+9), Aaa Corporate Bond Yield Relative to Yield o (-0.24@+9)
- **(2, tightness +0.79)** Chemicals and Allied Products: Agricultural (+0.69@-1), Chemicals and Allied Products: Basic Inorgan (+0.69@-3)
- **(2, tightness +0.94)** Future New Orders (+0.21@-22), Future General Activity (+0.20@-24)
- **(2, tightness +0.77)** Manufacturing (+0.65@-10), Nonresidential (+0.60@-10)
- **(2, tightness +0.96)** Nominal Broad U.S. Dollar Index (-0.37@+6), Nominal Advanced Foreign Economies U.S. Doll (-0.33@+7)
- **(2, tightness +0.87)** Total Business: Inventories to Sales Ratio (+0.39@-9), Manufacturers: Inventories to Sales Ratio (+0.34@-10)
- **(2, tightness +0.86)** Energy, Total (-0.29@+20), Mining: Mining (-0.26@+19)
- **(2, tightness +0.75)** Fuels and Related Products and Power: Anthra (+0.66@-3), Machinery and Equipment: Parts for Construct (+0.32@-3)
- **(2, tightness +0.89)** 5-Year, 5-Year Forward Inflation Expectation (+0.33@+7), 10-Year Breakeven Inflation Rate (+0.24@+7)
- **(2, tightness +0.80)** Construction (-0.28@-10), Total Construction (-0.25@-24)
- **(2, tightness +0.94)** Current General Business Conditions (-0.37@-8), Current New Orders (-0.37@-8)
- **(2, tightness +0.84)** 10-Year Treasury Constant Maturity Minus 2-Y (+0.29@-24), 10-Year Treasury Constant Maturity Minus 3-M (-0.22@-8)
- **(2, tightness +0.96)** Global zinc price (+0.47@+5), Import: Zinc (-0.46@-17)
- **(2, tightness +0.81)** Metals and Metal Products: Plumbing Fixtures (+0.62@+1), Metals and Metal Products: Vitreous China Pl (+0.39@+0)
- **(2, tightness +0.72)** Future Capital Expenditures (-0.38@-11), Current Employment (-0.26@-8)

**9 average-linkage-only cluster(s)** — the exact member set is a cluster under average but NOT under complete linkage. These come in two kinds; the tightness tells them apart:

- **8 genuinely loose (tightness < 0.70) → chain-effect grab-bags.** Members are held together transitively, not by mutual ≥0.70 correlation. These fragment under complete linkage.
- **1 tight (tightness ≥ 0.70) but partition-boundary differs.** All members are mutually ≥0.70, but complete linkage reassigned a member to an even tighter neighbouring group, so the exact set isn't a complete cluster. Not a grab-bag.

### Chain-effect grab-bags (loose average-only clusters)

#### (24, tightness +0.52) — sign-consistent
- Members: Machinery and Equipment: Agricultural Machin (+0.86@-3), Metals and Metal Products: Heating Equipment (+0.82@-1), Machinery and Equipment: Miscellaneous Const (+0.81@-2), Metals and Metal Products: Hardware, Not Els (+0.79@+0), Chemicals and Allied Products: Prepared Pain (+0.79@-1), Machinery and Equipment: Agricultural Machin (+0.76@-2), Metals and Metal Products: Hardware (+0.76@-1), Machinery and Equipment: General Purpose Mac (+0.76@-1), Chemicals and Allied Products: Paints and Al (+0.75@+0), Metals and Metal Products: Foundry and Forge (+0.74@-1), Metals and Metal Products: Miscellaneous Met (+0.73@+0), Fuels and Related Products and Power: Reside (+0.73@-6), Metals and Metal Products: Metal Containers (+0.73@+0), Machinery and Equipment: Special Industry Ma (+0.70@-1), Metals and Metal Products: Metal Cans and Ca (+0.69@-1), Chemicals and Allied Products: Other Chemica (+0.69@+0), Machinery and Equipment (+0.67@-2), Machinery and Equipment: Construction Machin (+0.67@-2), Machinery and Equipment: Miscellaneous Machi (+0.66@-3), Machinery and Equipment: Metalworking Machin (+0.63@-1), Rubber and Plastic Products: Laminated Plast (+0.61@+0), Electric power PPI (+0.60@-1), Electrical machinery & equip. PPI (+0.59@-1), Metals and Metal Products: Hand and Edge Too (+0.58@-2)
- Weakest internal link: **+0.52** (cut is 0.70) — joined transitively.
- Under complete linkage it fragments into pieces of sizes [8, 6, 4, 4, 2].
- Sign check: all 24 members share the **positive** peak sign — over-merged but directionally consistent, so treating it as one force merely *under*-counts witnesses (conservative), it does not average opposite signs together.

#### (19, tightness +0.52) — 🚨 SIGN CONFLICT
- Members: New Orders: Total Manufacturing (+0.55@+3), New Orders: Primary Metals (+0.55@+5), New Orders: Fabricated Metal Products (+0.47@+3), New Orders: Nondefense Capital Goods Excludi (+0.42@+3), New Orders: Machinery (+0.41@+3), New Orders: Durable Goods (+0.38@+6), Manufacturing: Durable Goods: Primary Metal (-0.31@-10), Industrial production: manufacturing (-0.31@-8), Manufacturing (-0.31@-8), Capacity utilization: manufacturing (-0.31@-8), Durable Goods Materials: Durable Goods Mater (-0.30@-9), Manufacturing: Durable Goods: Electrical Equ (-0.30@-7), Manufacturing: Durable Goods: Machinery (-0.29@-14), Manufacturing: Durable Goods: Primary Metal (-0.27@-10), Materials (-0.27@-8), Manufacturing: Durable Goods: Machinery (-0.26@-13), Manufacturing: Durable Goods: Iron and Steel (-0.26@-10), Manufacturing: Durable Goods: Electrical Equ (-0.25@-6), Manufacturing: Durable Goods: Fabricated Met (-0.25@-12)
- Weakest internal link: **+0.52** (cut is 0.70) — joined transitively.
- Under complete linkage it fragments into pieces of sizes [10, 4].
- 🚨 **Sign conflict:** 6 positive-lead vs 13 negative member(s) averaged into one 'force' — a positive lead and a negative relationship in the same bag is exactly the dangerous chain effect.
    - positive: New Orders: Total Manufacturing (+0.55), New Orders: Primary Metals (+0.55), New Orders: Fabricated Metal Products (+0.47), New Orders: Nondefense Capital Goods Excludi (+0.42), New Orders: Machinery (+0.41), New Orders: Durable Goods (+0.38)
    - negative: Manufacturing: Durable Goods: Primary Metal (-0.31), Industrial production: manufacturing (-0.31), Manufacturing (-0.31), Capacity utilization: manufacturing (-0.31), Durable Goods Materials: Durable Goods Mater (-0.30), Manufacturing: Durable Goods: Electrical Equ (-0.30), Manufacturing: Durable Goods: Machinery (-0.29), Manufacturing: Durable Goods: Primary Metal (-0.27), Materials (-0.27), Manufacturing: Durable Goods: Machinery (-0.26), Manufacturing: Durable Goods: Iron and Steel (-0.26), Manufacturing: Durable Goods: Electrical Equ (-0.25), Manufacturing: Durable Goods: Fabricated Met (-0.25)

#### (11, tightness +0.45) — sign-consistent
- Members: Import: Copper (+0.86@+10), Nonferrous wire & cable PPI (+0.68@+6), Metals and Metal Products: Nonferrous Mill S (+0.65@+6), Metals and Metal Products: Nonferrous Metals (+0.60@+7), Global aluminum price (+0.56@+5), Metals and Metal Products: Primary Nonferrou (+0.54@+7), Metals and Metal Products: Secondary Nonferr (+0.54@+8), Global copper price (+0.53@+7), Copper PPI (+0.53@+8), Metals and Metal Products: Nonferrous Scrap (+0.48@+11), Metals and Metal Products: Nonferrous Metal (+0.40@+6)
- Weakest internal link: **+0.45** (cut is 0.70) — joined transitively.
- Under complete linkage it fragments into pieces of sizes [5, 4].
- Sign check: all 11 members share the **positive** peak sign — over-merged but directionally consistent, so treating it as one force merely *under*-counts witnesses (conservative), it does not average opposite signs together.

#### (10, tightness +0.52) — sign-consistent
- Members: Transportation Services: Truck Transportatio (+0.81@+2), Truck Transportation (+0.80@+1), Total Manufacturing Industries (+0.80@+1), Metals and Metal Products: Fabricated Struct (+0.80@+2), Rubber and Plastic Products (+0.80@+2), Plastic products PPI (+0.78@+2), Rubber and Plastic Products: Unsupported Pla (+0.74@+2), Coal, Australia (+0.74@+2), Rubber and Plastic Products: Plastic Constru (+0.70@+3), Metals and Metal Products: Barrels, Drums, P (+0.69@+2)
- Weakest internal link: **+0.52** (cut is 0.70) — joined transitively.
- Under complete linkage it fragments into pieces of sizes [4, 4, 2].
- Sign check: all 10 members share the **positive** peak sign — over-merged but directionally consistent, so treating it as one force merely *under*-counts witnesses (conservative), it does not average opposite signs together.

#### (10, tightness +0.55) — sign-consistent
- Members: Metals and Metal Products (+0.78@+5), Chemicals and Allied Products (+0.72@+2), Cold-rolled steel sheet (+0.71@+6), Chemicals and Allied Products: Industrial Ch (+0.71@+2), Import: Ind. Supplies & Materials (+0.68@+3), Iron & steel PPI (+0.67@+4), Steel mill products PPI (+0.66@+4), Import: Ind. Supplies & Materials (+0.64@+5), Chemicals and Allied Products: Basic Organic (+0.62@+2), Chemicals and Allied Products: Plastic Resin (+0.60@+4)
- Weakest internal link: **+0.55** (cut is 0.70) — joined transitively.
- Under complete linkage it fragments into pieces of sizes [4, 3].
- Sign check: all 10 members share the **positive** peak sign — over-merged but directionally consistent, so treating it as one force merely *under*-counts witnesses (conservative), it does not average opposite signs together.

#### (7, tightness +0.68) — 🚨 SIGN CONFLICT
- Members: 5-Year Breakeven Inflation Rate (+0.47@+6), Current Prices Paid (-0.45@-11), Current Prices Received (-0.42@-8), Future Prices Paid (-0.42@-10), Current Prices Paid (-0.41@-8), Future Prices Received (-0.33@-7), Future Prices Paid (-0.27@-8)
- Weakest internal link: **+0.68** (cut is 0.70) — joined transitively.
- Under complete linkage it fragments into pieces of sizes [4, 2, 1].
- 🚨 **Sign conflict:** 1 positive-lead vs 6 negative member(s) averaged into one 'force' — a positive lead and a negative relationship in the same bag is exactly the dangerous chain effect.
    - positive: 5-Year Breakeven Inflation Rate (+0.47)
    - negative: Current Prices Paid (-0.45), Current Prices Received (-0.42), Future Prices Paid (-0.42), Current Prices Paid (-0.41), Future Prices Received (-0.33), Future Prices Paid (-0.27)

#### (5, tightness +0.64) — sign-consistent
- Members: 30-Year Fixed Rate Mortgage Average (+0.56@-3), Baa Corporate Bond Yield (+0.53@-5), 10-Year Constant Maturity, Quoted on an Inve (+0.52@-7), 10-Year Treasury yield (+0.48@+2), Aaa Corporate Bond Yield (+0.46@-1)
- Weakest internal link: **+0.64** (cut is 0.70) — joined transitively.
- Under complete linkage it fragments into pieces of sizes [4, 1].
- Sign check: all 5 members share the **positive** peak sign — over-merged but directionally consistent, so treating it as one force merely *under*-counts witnesses (conservative), it does not average opposite signs together.

#### (4, tightness +0.69) — sign-consistent
- Members: Machinery and Equipment: Mixers, Pavers, and (+0.70@-4), Machinery and Equipment: Tractors and Attach (+0.68@-7), Machinery and Equipment: Power Cranes, Dragl (+0.61@-9), Machinery and Equipment: Off-Highway, Equipm (+0.59@-10)
- Weakest internal link: **+0.69** (cut is 0.70) — joined transitively.
- Under complete linkage it fragments into pieces of sizes [2, 2].
- Sign check: all 4 members share the **positive** peak sign — over-merged but directionally consistent, so treating it as one force merely *under*-counts witnesses (conservative), it does not average opposite signs together.

### Tight-but-reassigned (average-only, tightness ≥ cut — not grab-bags)

- **(3, tightness +0.79)** 2-Year Constant Maturity, Quoted on an Inves (+0.70@-2), 1-Year Constant Maturity, Quoted on an Inves (+0.55@-3), 3-Month Treasury Bill Secondary Market Rate, (+0.51@-5)

## Verdict — do our current (average-linkage) forces survive complete linkage?

- **22 of 31** multi-signal forces are identical under complete linkage → **robust, genuine forces — keep.**
- **1 of 31** differ only by a partition boundary (all members still mutually ≥0.70) → effectively fine, just drawn differently.
- **8 of 31** are genuinely loose (weakest link < 0.70) → **chain-effect grab-bags / average-linkage artifacts** that fragment under complete linkage.
- Of those grab-bags, **2** mix positive-lead and negative members (🚨 **sign conflict**) — the dangerous case: averaging a lead with a negative relationship. The rest are sign-consistent (over-merged but directionally coherent, so conservative).

Empirical stability notes (this dataset — complete linkage is *not* a strict refinement of average, so these are observed, not guaranteed):
- Singletons: differ — 2 average-only and 2 complete-only singletons.
- Complete linkage also forms 23 multi-cluster(s) that are not average clusters (the two partitions cross-cut; complete is not a pure sub-division of average).
