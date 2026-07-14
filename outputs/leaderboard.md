# Leaderboard — do metal inputs lead transformer prices?

**26 true leads · 78 co-movers** (strong & FDR-significant but peak ≈ lag 0) · **2 short-sample (unverified)**.
Four guardrails run together: **q** = Benjamini-Hochberg FDR across all signals (CONFIRMED needs q<0.05); **r@0** and **gain** = lead-sharpness (peak |r| minus lag-0 |r|; a small gain = co-mover, not a lead); **min-history** = a short sample (n<150 or start after 2010-01-01) can't be CONFIRMED unless a long series corroborates the same force and it isn't a window artifact (see `analysis.md` §3 / `short_sample_check.csv`); per-force compositing in `analysis.md`.

Positive lead = candidate leads the transformer PPI (months). `robust` = passes both disqualifying gates. **short** marks a short usable sample.

| # | Signal | Verdict | Lead | Peak r | r@0 | gain | 95% CI | Perm q | Robust | n | short | Cat |
|---|--------|---------|------|--------|-----|------|--------|--------|--------|---|-------|-----|
| 1 | Producer Price Index by Commodity: Metals an | **CONFIRMED** | +6 | +0.78 | +0.54 | +0.24 | [+0.44, +0.89] | 0.0284 | yes | 419 |  | input_ppi |
| 2 | Metals and Metal Products | **CONFIRMED** | +5 | +0.78 | +0.64 | +0.14 | [+0.57, +0.88] | 0.0158 | yes | 696 |  | ppi_metals |
| 3 | Import Price Index (End Use): Finished Metal | **CONFIRMED** | +3 | +0.72 | +0.66 | +0.06 | [+0.53, +0.86] | 0.0158 | yes | 419 |  | import |
| 4 | Cold-rolled steel sheet (GOES proxy) | **CONFIRMED** | +6 | +0.71 | +0.49 | +0.23 | [+0.19, +0.85] | 0.0245 | yes | 510 |  | steel |
| 5 | Rubber and Plastic Products: Plastic Constru | **CONFIRMED** | +3 | +0.70 | +0.64 | +0.06 | [+0.33, +0.83] | 0.0043 | yes | 662 |  | ppi_plastics_rubber |
| 6 | Nonferrous wire & cable PPI | **CONFIRMED** | +6 | +0.68 | +0.49 | +0.19 | [+0.51, +0.79] | 0.0132 | yes | 695 |  | wire |
| 7 | Iron & steel PPI | **CONFIRMED** | +4 | +0.67 | +0.55 | +0.12 | [+0.41, +0.80] | 0.0158 | yes | 697 |  | steel |
| 8 | Steel mill products PPI | **CONFIRMED** | +4 | +0.66 | +0.55 | +0.11 | [+0.37, +0.80] | 0.0158 | yes | 697 |  | steel |
| 9 | Producer Price Index by Commodity: Metals an | **CONFIRMED** | +9 | +0.66 | +0.19 | +0.47 | [+0.21, +0.77] | 0.0043 | yes | 332 |  | input_ppi |
| 10 | Metals and Metal Products: Nonferrous Mill S | **CONFIRMED** | +6 | +0.65 | +0.46 | +0.19 | [+0.48, +0.78] | 0.0043 | yes | 695 |  | ppi_metals |
| 11 | Import Price Index (End Use): Iron and Steel | **CONFIRMED** | +4 | +0.64 | +0.55 | +0.09 | [+0.26, +0.84] | 0.0043 | yes | 402 |  | import |
| 12 | Import: Ind. Supplies & Materials (durable) | **CONFIRMED** | +5 | +0.64 | +0.53 | +0.11 | [+0.46, +0.76] | 0.0043 | yes | 401 |  | import |
| 13 | Aluminum mill shapes PPI | **CONFIRMED** | +4 | +0.61 | +0.52 | +0.09 | [+0.39, +0.76] | 0.0043 | yes | 697 |  | aluminum |
| 14 | Producer Price Index by Commodity: Metals an | **CONFIRMED** | +7 | +0.61 | +0.34 | +0.27 | [+0.43, +0.74] | 0.0043 | yes | 514 |  | input_ppi |
| 15 | Metals and Metal Products: Nonferrous Metals | **CONFIRMED** | +7 | +0.60 | +0.36 | +0.25 | [+0.45, +0.73] | 0.0043 | yes | 694 |  | ppi_metals |
| 16 | Chemicals and Allied Products: Plastic Resin | **CONFIRMED** | +4 | +0.60 | +0.52 | +0.08 | [+0.35, +0.74] | 0.0043 | yes | 697 |  | ppi_chemicals |
| 17 | Global tin price | **CONFIRMED** | +6 | +0.59 | +0.40 | +0.20 | [+0.29, +0.77] | 0.0043 | yes | 395 |  | basemetal |
| 18 | Global aluminum price | **CONFIRMED** | +5 | +0.56 | +0.41 | +0.15 | [+0.34, +0.73] | 0.0185 | yes | 396 |  | aluminum |
| 19 | Metals and Metal Products: Primary Nonferrou | **CONFIRMED** | +7 | +0.54 | +0.30 | +0.24 | [+0.41, +0.67] | 0.0043 | yes | 694 |  | ppi_metals |
| 20 | Producer Price Index by Commodity: Metals an | **CONFIRMED** | +7 | +0.54 | +0.31 | +0.23 | [+0.40, +0.67] | 0.0043 | yes | 694 |  | input_ppi |
| 21 | Metals and Metal Products: Secondary Nonferr | **CONFIRMED** | +8 | +0.54 | +0.29 | +0.25 | [+0.34, +0.71] | 0.0043 | yes | 693 |  | ppi_metals |
| 22 | Import Price Index (End Use): Major Nonferro | **CONFIRMED** | +6 | +0.54 | +0.37 | +0.17 | [+0.37, +0.71] | 0.0043 | yes | 420 |  | import |
| 23 | Global price of Industrial Materials index | **CONFIRMED** | +7 | +0.53 | +0.34 | +0.19 | [+0.33, +0.71] | 0.0043 | yes | 394 |  | commodity_fx |
| 24 | Global copper price | **CONFIRMED** | +7 | +0.53 | +0.31 | +0.21 | [+0.35, +0.69] | 0.0043 | yes | 394 |  | copper |
| 25 | Copper PPI | **CONFIRMED** | +8 | +0.53 | +0.26 | +0.26 | [+0.39, +0.63] | 0.0185 | yes | 693 |  | copper |
| 26 | Global price of Metal index | **CONFIRMED** | +7 | +0.52 | +0.33 | +0.19 | [+0.32, +0.71] | 0.0043 | yes | 394 |  | commodity_fx |
| 27 | Global Price Index of All Commodities | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.69 | +0.61 | +0.08 | [+0.52, +0.80] | 0.0043 | yes | 398 |  | commodity_fx |
| 28 | Import: Ind. Supplies & Materials (ex-fuel) | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.68 | +0.61 | +0.06 | [+0.52, +0.79] | 0.0284 | yes | 278 |  | import |
| 29 | Global price of Energy index | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.67 | +0.60 | +0.08 | [+0.39, +0.82] | 0.0043 | yes | 398 |  | commodity_fx |
| 30 | Import Price Index (End Use): Industrial Sup | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.65 | +0.59 | +0.06 | [+0.48, +0.77] | 0.0043 | yes | 429 |  | import |
| 31 | Refined petroleum products PPI | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.62 | +0.54 | +0.08 | [+0.46, +0.73] | 0.0043 | yes | 698 |  | energy |
| 32 | Import: Industrial Supplies & Materials | **STRONG BUT CYCLE-DRIVEN** | +2 | +0.60 | +0.54 | +0.06 | [+0.46, +0.73] | 0.0158 | yes | 451 |  | import |
| 33 | Import Price Index (End Use): Unfinished Met | **STRONG BUT CYCLE-DRIVEN** | +5 | +0.60 | +0.48 | +0.12 | [+0.44, +0.74] | 0.0043 | yes | 431 |  | import |
| 34 | Manufacturers' Unfilled Orders: Primary Meta | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.59 | +0.54 | +0.05 | [+0.42, +0.76] | 0.0196 | yes | 398 |  | orders |
| 35 | WTI crude oil | **STRONG BUT CYCLE-DRIVEN** | +5 | +0.59 | +0.43 | +0.16 | [+0.41, +0.72] | 0.0158 | yes | 696 |  | energy |
| 36 | Global price of Food index | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.57 | +0.48 | +0.09 | [+0.36, +0.71] | 0.0043 | yes | 398 |  | commodity_fx |
| 37 | New Orders: Total Manufacturing | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.55 | +0.48 | +0.06 | [+0.41, +0.68] | 0.0272 | yes | 397 |  | orders |
| 38 | New Orders: Primary Metals | **STRONG BUT CYCLE-DRIVEN** | +5 | +0.55 | +0.42 | +0.13 | [+0.37, +0.73] | 0.0272 | yes | 395 |  | orders |
| 39 | Manufacturers' Unfilled Orders: Iron and Ste | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.55 | +0.48 | +0.06 | [+0.36, +0.73] | 0.0284 | yes | 398 |  | orders |
| 40 | WTI Crude | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.55 | +0.44 | +0.11 | [+0.37, +0.69] | 0.0043 | yes | 398 |  | commodity |
| 41 | Fuels and Related Products and Power: Natura | **STRONG BUT CYCLE-DRIVEN** | +5 | +0.54 | +0.40 | +0.13 | [+0.31, +0.69] | 0.0043 | yes | 648 |  | ppi_fuels_power |
| 42 | Brent Crude | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.53 | +0.45 | +0.09 | [+0.36, +0.69] | 0.0043 | yes | 398 |  | commodity |
| 43 | Import Price Index (End Use): Petroleum Prod | **STRONG BUT CYCLE-DRIVEN** | +2 | +0.52 | +0.47 | +0.06 | [+0.34, +0.68] | 0.0158 | yes | 462 |  | import |
| 44 | Fuels and Related Products and Power: Crude | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.52 | +0.42 | +0.10 | [+0.33, +0.68] | 0.0043 | yes | 404 |  | ppi_fuels_power |
| 45 | Import Price Index (End Use): Crude Oil | **STRONG BUT CYCLE-DRIVEN** | +3 | +0.51 | +0.44 | +0.08 | [+0.33, +0.67] | 0.0043 | yes | 437 |  | import |
| 46 | Manufacturers' Unfilled Orders: Photographic | **STRONG / NOT ROBUST** | +22 | +0.64 | +0.07 | +0.57 | [+0.46, +0.78] | 0.1232 | yes | 379 |  | orders |
| 47 | Producer Price Index by Commodity: Fuels and | **STRONG / NOT ROBUST** | +0 | +0.58 | +0.58 | +0.00 | [+0.37, +0.77] | 0.0106 | no | 701 |  | grid_datacenter |
| 48 | Producer Price Index by Industry: Electric P | **STRONG / NOT ROBUST** | +0 | +0.58 | +0.58 | +0.00 | [+0.38, +0.77] | 0.0106 | no | 701 |  | grid_datacenter |
| 49 | Market Yield on U.S. Treasury Securities at | **STRONG / NOT ROBUST** | +1 | +0.56 | +0.56 | +0.00 | [+0.14, +0.77] | 0.0132 | no | 700 |  | rates |
| 50 | Retailers: Inventories to Sales Ratio | **STRONG / NOT ROBUST** | +12 | -0.55 | +0.06 | +0.48 | [-0.74, -0.10] | 0.0043 | no | 388 |  | inventories |
| 51 | Chemicals and Allied Products: Paint Materia | **STRONG / NOT ROBUST** | +0 | +0.54 | +0.54 | +0.00 | [+0.34, +0.71] | 0.0106 | no | 701 |  | ppi_chemicals |
| 52 | Market Yield on U.S. Treasury Securities at | **STRONG / NOT ROBUST** | +2 | +0.54 | +0.53 | +0.01 | [+0.22, +0.72] | 0.0106 | no | 669 |  | rates |
| 53 | Manufacturers' Unfilled Orders: Construction | **STRONG / NOT ROBUST** | +2 | +0.53 | +0.52 | +0.02 | [+0.35, +0.70] | 0.242 | yes | 399 |  | orders |
| 54 | Import: Copper | **SHORT-SAMPLE (unverified)** | +10 | +0.86 | +0.09 | +0.77 | [+0.28, +0.93] | 0.0043 | no | 80 | ⚠︎ | import |
| 55 | Transportation Services: Truck Transportatio | **SHORT-SAMPLE (unverified)** | +2 | +0.81 | +0.78 | +0.03 | [+0.26, +0.94] | 0.0272 | no | 190 | ⚠︎ | freight |
| 56 | Iron & steel scrap PPI | **PARTIAL / INCONCLUSIVE** | +8 | +0.49 | +0.21 | +0.27 | [+0.25, +0.65] | 0.0151 | yes | 693 |  | steel |
| 57 | Metals and Metal Products: Nonferrous Scrap | **PARTIAL / INCONCLUSIVE** | +11 | +0.48 | +0.11 | +0.37 | [+0.30, +0.64] | 0.0196 | yes | 688 |  | ppi_metals |
| 58 | New Orders: Fabricated Metal Products | **PARTIAL / INCONCLUSIVE** | +3 | +0.47 | +0.39 | +0.08 | [+0.33, +0.61] | 0.0272 | yes | 397 |  | orders |
| 59 | Producer Price Index by Commodity: Metals an | **PARTIAL / INCONCLUSIVE** | +10 | +0.45 | +0.11 | +0.34 | [+0.22, +0.56] | 0.0043 | yes | 509 |  | input_ppi |
| 60 | Metals and Metal Products: Nonferrous Metal | **PARTIAL / INCONCLUSIVE** | +6 | +0.40 | +0.28 | +0.12 | [+0.26, +0.60] | 0.0043 | yes | 482 |  | ppi_metals |
| 61 | Metals and Metal Products: Heating Equipment | **CO-MOVER (not a lead)** | -1 | +0.82 | +0.82 | +0.00 | [+0.61, +0.90] | 0.0106 | yes | 700 |  | ppi_metals |
| 62 | Producer Price Index by Commodity: Metals an | **CO-MOVER (not a lead)** | +2 | +0.81 | +0.77 | +0.04 | [+0.47, +0.92] | 0.0043 | yes | 339 |  | input_ppi |
| 63 | Machinery and Equipment: Miscellaneous Const | **CO-MOVER (not a lead)** | -2 | +0.81 | +0.79 | +0.02 | [+0.24, +0.91] | 0.0331 | yes | 232 |  | ppi_machinery |
| 64 | Truck Transportation | **CO-MOVER (not a lead)** | +1 | +0.80 | +0.78 | +0.02 | [+0.45, +0.92] | 0.0228 | yes | 257 |  | freight |
| 65 | Producer Price Index by Commodity: Metals an | **CO-MOVER (not a lead)** | +1 | +0.80 | +0.79 | +0.01 | [+0.52, +0.90] | 0.0151 | yes | 520 |  | input_ppi |
| 66 | Total Manufacturing Industries | **CO-MOVER (not a lead)** | +1 | +0.80 | +0.78 | +0.02 | [+0.59, +0.90] | 0.0043 | yes | 472 |  | mfg_price |
| 67 | Metals and Metal Products: Fabricated Struct | **CO-MOVER (not a lead)** | +2 | +0.80 | +0.78 | +0.02 | [+0.54, +0.90] | 0.0151 | yes | 699 |  | ppi_metals |
| 68 | Rubber and Plastic Products | **CO-MOVER (not a lead)** | +2 | +0.80 | +0.78 | +0.01 | [+0.60, +0.88] | 0.0132 | yes | 699 |  | ppi_plastics_rubber |
| 69 | Metals and Metal Products: Hardware, Not Els | **CO-MOVER (not a lead)** | +0 | +0.79 | +0.79 | +0.00 | [+0.59, +0.88] | 0.0106 | yes | 701 |  | ppi_metals |
| 70 | Chemicals and Allied Products: Prepared Pain | **CO-MOVER (not a lead)** | -1 | +0.79 | +0.78 | +0.01 | [+0.54, +0.89] | 0.0106 | yes | 700 |  | ppi_chemicals |
| 71 | Plastic products PPI | **CO-MOVER (not a lead)** | +2 | +0.78 | +0.76 | +0.02 | [+0.57, +0.87] | 0.0043 | yes | 651 |  | materials |
| 72 | Machinery and Equipment: Agricultural Machin | **CO-MOVER (not a lead)** | -2 | +0.76 | +0.74 | +0.02 | [+0.52, +0.86] | 0.0151 | yes | 699 |  | ppi_machinery |
| 73 | Metals and Metal Products: Hardware | **CO-MOVER (not a lead)** | -1 | +0.76 | +0.76 | +0.00 | [+0.56, +0.86] | 0.0106 | yes | 700 |  | ppi_metals |
| 74 | Machinery and Equipment: General Purpose Mac | **CO-MOVER (not a lead)** | -1 | +0.76 | +0.75 | +0.01 | [+0.60, +0.85] | 0.0151 | yes | 700 |  | ppi_machinery |
| 75 | Chemicals and Allied Products: Paints and Al | **CO-MOVER (not a lead)** | +0 | +0.75 | +0.75 | +0.00 | [+0.54, +0.85] | 0.0151 | yes | 645 |  | ppi_chemicals |
| 76 | Rubber and Plastic Products: Unsupported Pla | **CO-MOVER (not a lead)** | +2 | +0.74 | +0.72 | +0.03 | [+0.53, +0.84] | 0.0043 | yes | 651 |  | ppi_plastics_rubber |
| 77 | Metals and Metal Products: Foundry and Forge | **CO-MOVER (not a lead)** | -1 | +0.74 | +0.74 | +0.00 | [+0.57, +0.84] | 0.0106 | yes | 700 |  | ppi_metals |
| 78 | Coal, Australia | **CO-MOVER (not a lead)** | +2 | +0.74 | +0.70 | +0.03 | [+0.35, +0.86] | 0.0043 | yes | 399 |  | commodity |
| 79 | Metals and Metal Products: Miscellaneous Met | **CO-MOVER (not a lead)** | +0 | +0.73 | +0.73 | +0.00 | [+0.53, +0.83] | 0.0151 | yes | 701 |  | ppi_metals |
| 80 | Metals and Metal Products: Metal Containers | **CO-MOVER (not a lead)** | +0 | +0.73 | +0.73 | +0.00 | [+0.44, +0.85] | 0.0151 | yes | 701 |  | ppi_metals |
| 81 | Chemicals and Allied Products | **CO-MOVER (not a lead)** | +2 | +0.72 | +0.70 | +0.03 | [+0.58, +0.84] | 0.0132 | yes | 699 |  | ppi_chemicals |
| 82 | Rubber and Plastic Products: Miscellaneous R | **CO-MOVER (not a lead)** | -2 | +0.71 | +0.70 | +0.01 | [+0.51, +0.82] | 0.0151 | yes | 699 |  | ppi_plastics_rubber |
| 83 | Chemicals and Allied Products: Industrial Ch | **CO-MOVER (not a lead)** | +2 | +0.71 | +0.67 | +0.04 | [+0.55, +0.82] | 0.0132 | yes | 699 |  | ppi_chemicals |
| 84 | Import Price Index (End Use): Agricultural P | **CO-MOVER (not a lead)** | +1 | +0.70 | +0.69 | +0.01 | [+0.45, +0.84] | 0.0151 | yes | 425 |  | import |
| 85 | 2-Year Constant Maturity, Quoted on an Inves | **CO-MOVER (not a lead)** | -2 | +0.70 | +0.67 | +0.03 | [+0.04, +0.85] | 0.0158 | no | 586 |  | rates |
| 86 | Machinery and Equipment: Special Industry Ma | **CO-MOVER (not a lead)** | -1 | +0.70 | +0.69 | +0.01 | [+0.45, +0.82] | 0.0043 | yes | 700 |  | ppi_machinery |
| 87 | Metals and Metal Products: Metal Cans and Ca | **CO-MOVER (not a lead)** | -1 | +0.69 | +0.69 | +0.01 | [+0.38, +0.83] | 0.0106 | yes | 700 |  | ppi_metals |
| 88 | Chemicals and Allied Products: Agricultural | **CO-MOVER (not a lead)** | -1 | +0.69 | +0.69 | +0.00 | [+0.49, +0.81] | 0.0106 | yes | 700 |  | ppi_chemicals |
| 89 | Chemicals and Allied Products: Other Chemica | **CO-MOVER (not a lead)** | +0 | +0.69 | +0.69 | +0.00 | [+0.53, +0.82] | 0.0151 | yes | 701 |  | ppi_chemicals |
| 90 | Metals and Metal Products: Barrels, Drums, P | **CO-MOVER (not a lead)** | +2 | +0.69 | +0.67 | +0.02 | [+0.36, +0.84] | 0.0132 | yes | 699 |  | ppi_metals |
| 91 | Rubber and Plastic Products: Rubber and Rubb | **CO-MOVER (not a lead)** | +0 | +0.69 | +0.69 | +0.00 | [+0.54, +0.81] | 0.0106 | yes | 701 |  | ppi_plastics_rubber |
| 92 | Producer Price Index by Commodity: Metals an | **CO-MOVER (not a lead)** | -1 | +0.68 | +0.68 | +0.01 | [+0.54, +0.82] | 0.0151 | yes | 533 |  | input_ppi |
| 93 | Machinery and Equipment | **CO-MOVER (not a lead)** | -2 | +0.67 | +0.66 | +0.01 | [+0.46, +0.80] | 0.0151 | yes | 699 |  | ppi_machinery |
| 94 | Machinery and Equipment: Construction Machin | **CO-MOVER (not a lead)** | -2 | +0.67 | +0.64 | +0.02 | [+0.47, +0.81] | 0.0151 | yes | 699 |  | ppi_machinery |
| 95 | Unfilled Orders: Electrical Equipment, Appli | **CO-MOVER (not a lead)** | +1 | +0.65 | +0.65 | +0.00 | [+0.39, +0.79] | 0.0043 | yes | 400 |  | orders |
| 96 | Rubber and Plastic Products: Tires, Tubes, T | **CO-MOVER (not a lead)** | -1 | +0.64 | +0.64 | +0.00 | [+0.49, +0.75] | 0.0106 | yes | 700 |  | ppi_plastics_rubber |
| 97 | Import Price Index (End Use): Iron and Steel | **CO-MOVER (not a lead)** | +2 | +0.63 | +0.61 | +0.02 | [+0.31, +0.81] | 0.0151 | yes | 428 |  | import |
| 98 | Metals and Metal Products: Nonferrous Foundr | **CO-MOVER (not a lead)** | +1 | +0.63 | +0.63 | +0.00 | [+0.45, +0.78] | 0.0185 | yes | 575 |  | ppi_metals |
| 99 | Machinery and Equipment: Metalworking Machin | **CO-MOVER (not a lead)** | -1 | +0.63 | +0.62 | +0.01 | [+0.43, +0.79] | 0.0106 | yes | 700 |  | ppi_machinery |
| 100 | Producer Price Index by Commodity: Metals an | **CO-MOVER (not a lead)** | +0 | +0.63 | +0.63 | +0.00 | [+0.43, +0.78] | 0.0151 | yes | 677 |  | input_ppi |
| 101 | Chemicals and Allied Products: Basic Organic | **CO-MOVER (not a lead)** | +2 | +0.62 | +0.58 | +0.05 | [+0.42, +0.73] | 0.0043 | yes | 616 |  | ppi_chemicals |
| 102 | Metals and Metal Products: Plumbing Fixtures | **CO-MOVER (not a lead)** | +1 | +0.62 | +0.62 | +0.00 | [+0.43, +0.79] | 0.0151 | yes | 700 |  | ppi_metals |
| 103 | Producer Price Index by Industry: Couriers a | **CO-MOVER (not a lead)** | +0 | +0.62 | +0.62 | +0.00 | [+0.48, +0.76] | 0.0167 | yes | 450 |  | freight |
| 104 | Rubber and Plastic Products: Laminated Plast | **CO-MOVER (not a lead)** | +0 | +0.61 | +0.61 | +0.00 | [+0.34, +0.75] | 0.0043 | yes | 647 |  | ppi_plastics_rubber |
| 105 | Market Yield on U.S. Treasury Securities at | **CO-MOVER (not a lead)** | -1 | +0.61 | +0.60 | +0.01 | [+0.07, +0.82] | 0.0106 | no | 700 |  | rates |
| 106 | Producer Price Index by Industry: Electric P | **CO-MOVER (not a lead)** | -1 | +0.61 | +0.60 | +0.00 | [+0.42, +0.75] | 0.0043 | yes | 700 |  | grid_datacenter |
| 107 | Producer Price Index by Commodity: Fuels and | **CO-MOVER (not a lead)** | -1 | +0.61 | +0.61 | +0.00 | [+0.42, +0.75] | 0.0043 | yes | 700 |  | grid_datacenter |
| 108 | Electric power PPI | **CO-MOVER (not a lead)** | -1 | +0.60 | +0.60 | +0.00 | [+0.42, +0.77] | 0.0043 | yes | 700 |  | energy |
| 109 | Manufacturers' Unfilled Orders: Fabricated M | **CO-MOVER (not a lead)** | +4 | +0.60 | +0.55 | +0.05 | [+0.31, +0.78] | 0.0043 | yes | 397 |  | orders |
| 110 | Import Price Index (End Use): All Commoditie | **CO-MOVER (not a lead)** | +2 | +0.60 | +0.55 | +0.04 | [+0.49, +0.72] | 0.0151 | yes | 460 |  | import |
| 111 | Electrical machinery & equip. PPI | **CO-MOVER (not a lead)** | -1 | +0.59 | +0.59 | +0.00 | [+0.38, +0.77] | 0.0158 | yes | 700 |  | downstream |
| 112 | Iron ores PPI | **CO-MOVER (not a lead)** | +0 | +0.59 | +0.59 | +0.00 | [+0.41, +0.73] | 0.0106 | yes | 701 |  | steel |
| 113 | Metals and Metal Products: Hand and Edge Too | **CO-MOVER (not a lead)** | -2 | +0.58 | +0.56 | +0.02 | [+0.34, +0.78] | 0.0158 | yes | 699 |  | ppi_metals |
| 114 | Fuels and Related Products and Power: Coal | **CO-MOVER (not a lead)** | -1 | +0.57 | +0.56 | +0.01 | [+0.21, +0.74] | 0.0106 | yes | 700 |  | ppi_fuels_power |
| 115 | Fuels and Related Products and Power: Coal | **CO-MOVER (not a lead)** | -1 | +0.57 | +0.56 | +0.01 | [+0.21, +0.74] | 0.0106 | yes | 700 |  | ppi_fuels_power |
| 116 | Fuels and Related Products and Power: Bitumi | **CO-MOVER (not a lead)** | -1 | +0.55 | +0.55 | +0.01 | [+0.13, +0.69] | 0.0043 | yes | 659 |  | ppi_fuels_power |
| 117 | Manufacturers' Unfilled Orders: Ventilation, | **CO-MOVER (not a lead)** | +3 | +0.55 | +0.54 | +0.01 | [+0.32, +0.70] | 0.0331 | yes | 398 |  | orders |
| 118 | Producer Price Index by Commodity for Metals | **CO-MOVER (not a lead)** | +0 | +0.54 | +0.54 | +0.00 | [+0.19, +0.76] | 0.0043 | yes | 585 |  | ppi_metals |
| 119 | Producer Price Index by Industry: Scheduled | **CO-MOVER (not a lead)** | -2 | +0.54 | +0.50 | +0.04 | [+0.19, +0.74] | 0.0043 | yes | 424 |  | freight |
| 120 | Metals and Metal Products: Nonferrous Forge | **CO-MOVER (not a lead)** | -2 | +0.52 | +0.51 | +0.01 | [+0.27, +0.72] | 0.0228 | yes | 496 |  | ppi_metals |
| 121 | Fuels and Related Products and Power: Asphal | **CO-MOVER (not a lead)** | +0 | +0.51 | +0.51 | +0.00 | [+0.38, +0.66] | 0.0151 | yes | 486 |  | ppi_fuels_power |
| 122 | Producer Price Index by Industry: Deep Sea F | **CO-MOVER (not a lead)** | -1 | +0.51 | +0.50 | +0.01 | [+0.09, +0.73] | 0.0167 | no | 443 |  | freight |
| 123 | Producer Price Index by Industry: Deep Sea F | **CO-MOVER (not a lead)** | -1 | +0.50 | +0.49 | +0.01 | [+0.08, +0.72] | 0.0167 | no | 443 |  | freight |
| 124 | Producer Price Index by Industry: Deep Sea F | **CO-MOVER (not a lead)** | -1 | +0.50 | +0.49 | +0.01 | [+0.08, +0.72] | 0.0167 | no | 443 |  | freight |
| 125 | New orders: electrical equipment | **CO-MOVER (not a lead)** | +1 | +0.50 | +0.48 | +0.02 | [+0.34, +0.63] | 0.0158 | yes | 399 |  | demand |
| 126 | Producer Price Index by Commodity: Metals an | **CO-MOVER (not a lead)** | +0 | +0.49 | +0.49 | +0.00 | [+0.15, +0.72] | 0.0132 | yes | 365 |  | input_ppi |
| 127 | Producer Price Index by Commodity: Metals an | **CO-MOVER (not a lead)** | -1 | +0.49 | +0.48 | +0.01 | [+0.37, +0.65] | 0.0196 | yes | 508 |  | input_ppi |
| 128 | Unfilled Orders: Total Manufacturing | **CO-MOVER (not a lead)** | -1 | +0.49 | +0.48 | +0.00 | [+0.31, +0.69] | 0.0158 | no | 400 |  | orders |
| 129 | Steel wire PPI | **CO-MOVER (not a lead)** | +2 | +0.48 | +0.47 | +0.02 | [+0.29, +0.86] | 0.0043 | yes | 502 |  | steel |
| 130 | Rubber and Plastic Products: Synthetic Rubbe | **CO-MOVER (not a lead)** | +2 | +0.48 | +0.47 | +0.01 | [+0.34, +0.61] | 0.0151 | yes | 699 |  | ppi_plastics_rubber |
| 131 | Import Price Index (End Use): Durables, Manu | **CO-MOVER (not a lead)** | +2 | +0.47 | +0.47 | +0.01 | [+0.24, +0.76] | 0.0158 | yes | 442 |  | import |
| 132 | Producer Price Index by Industry: Scheduled | **CO-MOVER (not a lead)** | -2 | +0.47 | +0.45 | +0.03 | [+0.13, +0.69] | 0.0043 | no | 424 |  | freight |
| 133 | Aaa Corporate Bond Yield | **CO-MOVER (not a lead)** | -1 | +0.46 | +0.45 | +0.01 | [+0.19, +0.63] | 0.0151 | no | 700 |  | credit |
| 134 | Import Price Index (End Use): Foods, Feeds, | **CO-MOVER (not a lead)** | +3 | +0.46 | +0.42 | +0.03 | [+0.30, +0.63] | 0.0158 | yes | 480 |  | import |
| 135 | New Orders: Nondefense Capital Goods Excludi | **CO-MOVER (not a lead)** | +3 | +0.42 | +0.38 | +0.04 | [+0.29, +0.56] | 0.0318 | yes | 397 |  | orders |
| 136 | Machinery and Equipment: Electronic Computer | **CO-MOVER (not a lead)** | -1 | +0.42 | +0.42 | +0.00 | [+0.06, +0.65] | 0.0284 | no | 413 |  | ppi_machinery |
| 137 | Global nickel price | **CO-MOVER (not a lead)** | +2 | +0.41 | +0.39 | +0.02 | [+0.21, +0.60] | 0.0043 | yes | 399 |  | nickel |
| 138 | Current Unfilled Orders; Percent Reporting D | **CO-MOVER (not a lead)** | -2 | +0.31 | +0.30 | +0.01 | [+0.12, +0.49] | 0.0151 | no | 683 |  | orders |
| 139 | Machinery and Equipment: Agricultural Machin | **REVERSED** | -3 | +0.86 | +0.82 | +0.04 | [+0.51, +0.95] | 0.0284 | yes | 267 |  | ppi_machinery |
| 140 | Fuels and Related Products and Power: Reside | **REVERSED** | -6 | +0.73 | +0.59 | +0.14 | [+0.42, +0.87] | 0.0331 | yes | 408 |  | ppi_fuels_power |
| 141 | Producer Price Index by Industry: Refined Pe | **REVERSED** | -18 | +0.72 | +0.04 | +0.67 | [+0.46, +0.84] | 0.0043 | yes | 353 |  | freight |
| 142 | Producer Price Index by Industry: Refined Pe | **REVERSED** | -18 | +0.72 | +0.04 | +0.67 | [+0.46, +0.84] | 0.0043 | yes | 353 |  | freight |
| 143 | Machinery and Equipment: Mixers, Pavers, and | **REVERSED** | -4 | +0.70 | +0.67 | +0.03 | [+0.45, +0.82] | 0.0167 | yes | 697 |  | ppi_machinery |
| 144 | Chemicals and Allied Products: Basic Inorgan | **REVERSED** | -3 | +0.69 | +0.64 | +0.05 | [+0.55, +0.77] | 0.0043 | yes | 615 |  | ppi_chemicals |
| 145 | Machinery and Equipment: Tractors and Attach | **REVERSED** | -7 | +0.68 | +0.52 | +0.16 | [+0.30, +0.81] | 0.0439 | yes | 299 |  | ppi_machinery |
| 146 | Fuels and Related Products and Power: Anthra | **REVERSED** | -3 | +0.66 | +0.62 | +0.04 | [+0.39, +0.81] | 0.0167 | yes | 657 |  | ppi_fuels_power |
| 147 | Machinery and Equipment: Miscellaneous Machi | **REVERSED** | -3 | +0.66 | +0.61 | +0.04 | [+0.50, +0.82] | 0.0158 | yes | 698 |  | ppi_machinery |
| 148 | Producer Price Index by Industry: Refined Pe | **REVERSED** | -18 | +0.66 | +0.07 | +0.58 | [+0.36, +0.80] | 0.0043 | yes | 450 |  | freight |
| 149 | Manufacturing | **REVERSED** | -10 | +0.65 | +0.30 | +0.35 | [+0.25, +0.84] | 0.0345 | yes | 271 |  | construction |
| 150 | Producer Price Index by Industry: Scheduled | **REVERSED** | -3 | +0.63 | +0.56 | +0.07 | [+0.38, +0.79] | 0.0043 | yes | 302 |  | freight |
| 151 | Producer Price Index by Commodity: Metals an | **REVERSED** | -3 | +0.62 | +0.58 | +0.04 | [+0.26, +0.81] | 0.0043 | yes | 521 |  | input_ppi |
| 152 | Machinery and Equipment: Power Cranes, Dragl | **REVERSED** | -9 | +0.61 | +0.44 | +0.17 | [+0.08, +0.83] | 0.0043 | yes | 297 |  | ppi_machinery |
| 153 | Nonresidential | **REVERSED** | -10 | +0.60 | +0.26 | +0.34 | [+0.22, +0.78] | 0.0043 | yes | 271 |  | construction |
| 154 | Machinery and Equipment: Miscellaneous Instr | **REVERSED** | -10 | +0.60 | +0.41 | +0.19 | [+0.19, +0.80] | 0.0345 | yes | 530 |  | ppi_machinery |
| 155 | Machinery and Equipment: Off-Highway, Equipm | **REVERSED** | -10 | +0.59 | +0.33 | +0.25 | [+0.16, +0.80] | 0.0043 | yes | 296 |  | ppi_machinery |
| 156 | Producer Price Index by Commodity: Metals an | **REVERSED** | -3 | +0.58 | +0.55 | +0.03 | [+0.37, +0.74] | 0.0043 | yes | 531 |  | input_ppi |
| 157 | 30-Year Fixed Rate Mortgage Average | **REVERSED** | -3 | +0.56 | +0.52 | +0.04 | [+0.22, +0.76] | 0.0167 | yes | 647 |  | rates |
| 158 | Current Delivery Time | **REVERSED** | -10 | -0.55 | -0.03 | +0.52 | [-0.73, -0.18] | 0.0705 | yes | 277 |  | regionalfed_current |
| 159 | 1-Year Constant Maturity, Quoted on an Inves | **REVERSED** | -3 | +0.55 | +0.49 | +0.06 | [-0.13, +0.75] | 0.0043 | no | 698 |  | rates |
| 160 | Producer Price Index by Commodity: Metals an | **REVERSED** | -3 | +0.54 | +0.38 | +0.16 | [+0.34, +0.69] | 0.0043 | yes | 482 |  | input_ppi |
| 161 | Producer Price Index by Commodity: Metals an | **REVERSED** | -3 | +0.54 | +0.38 | +0.16 | [+0.34, +0.69] | 0.0043 | yes | 482 |  | input_ppi |
| 162 | Baa Corporate Bond Yield | **REVERSED** | -5 | +0.53 | +0.44 | +0.09 | [+0.21, +0.72] | 0.0167 | yes | 696 |  | credit |
| 163 | Finished lubricants PPI | **REVERSED** | -3 | +0.53 | +0.51 | +0.03 | [+0.44, +0.67] | 0.0167 | yes | 611 |  | energy |
| 164 | Federal Funds Effective Rate | **REVERSED** | -7 | +0.53 | +0.30 | +0.23 | [-0.19, +0.73] | 0.0043 | yes | 694 |  | rates |
| 165 | Total Public Construction Spending: Power | **REVERSED** | -13 | +0.52 | +0.08 | +0.44 | [+0.19, +0.70] | 0.0043 | yes | 268 |  | construction |
| 166 | 10-Year Constant Maturity, Quoted on an Inve | **REVERSED** | -7 | +0.52 | +0.29 | +0.24 | [-0.01, +0.78] | 0.0553 | yes | 262 |  | rates |
| 167 | Producer Price Index by Commodity: Metals an | **REVERSED** | -3 | +0.52 | +0.49 | +0.03 | [+0.40, +0.67] | 0.0132 | no | 494 |  | input_ppi |
| 168 | 3-Month Treasury Bill Secondary Market Rate, | **REVERSED** | -5 | +0.51 | +0.39 | +0.12 | [-0.22, +0.73] | 0.0043 | no | 696 |  | rates |
| 169 | Import Price Index (End Use): Lumber and Oth | **REJECTED** | +14 | +0.49 | +0.05 | +0.44 | [-0.02, +0.69] | 0.0681 | no | 416 |  | import |
| 170 | Residential | **REJECTED** | -14 | -0.49 | +0.02 | +0.47 | [-0.72, -0.34] | 0.1065 | yes | 267 |  | construction |
| 171 | 10-Year Treasury yield | **REJECTED** | +2 | +0.48 | +0.47 | +0.01 | [+0.22, +0.63] | 0.0151 | no | 699 |  | financial |
| 172 | Oil and Gas Extraction | **REJECTED** | -7 | +0.47 | +0.36 | +0.11 | [+0.36, +0.61] | 0.0043 | yes | 634 |  | employment |
| 173 | Global zinc price | **REJECTED** | +5 | +0.47 | +0.34 | +0.12 | [+0.28, +0.71] | 0.2418 | yes | 396 |  | basemetal |
| 174 | 5-Year Breakeven Inflation Rate | **REJECTED** | +6 | +0.47 | +0.22 | +0.25 | [+0.19, +0.68] | 0.3604 | no | 263 |  | expectations |
| 175 | 10-Year Expected Inflation | **REJECTED** | +2 | +0.46 | +0.44 | +0.02 | [+0.17, +0.64] | 0.0151 | no | 519 |  | expectations |
| 176 | Import: Zinc | **REJECTED** | -17 | -0.46 | +0.36 | +0.10 | [-0.66, -0.24] | 0.4437 | yes | 181 |  | import |
| 177 | 11-Year Expected Inflation | **REJECTED** | +2 | +0.45 | +0.44 | +0.02 | [+0.16, +0.64] | 0.0151 | no | 519 |  | expectations |
| 178 | Current Prices Paid | **REJECTED** | -11 | -0.45 | +0.20 | +0.25 | [-0.63, -0.18] | 0.0043 | yes | 276 |  | regionalfed_current |
| 179 | Market Yield on U.S. Treasury Securities at | **REJECTED** | +2 | +0.45 | +0.44 | +0.01 | [+0.24, +0.58] | 0.0158 | no | 606 |  | rates |
| 180 | Import Price Index (End Use): Fish and Shell | **REJECTED** | +4 | +0.45 | +0.38 | +0.07 | [+0.16, +0.66] | 0.0245 | no | 426 |  | import |
| 181 | Fuels and Related Products and Power: Gas Fu | **REJECTED** | +3 | +0.45 | +0.40 | +0.05 | [+0.19, +0.65] | 0.0043 | no | 698 |  | ppi_fuels_power |
| 182 | 12-Year Expected Inflation | **REJECTED** | +2 | +0.45 | +0.43 | +0.02 | [+0.16, +0.63] | 0.0151 | no | 519 |  | expectations |
| 183 | 1-Year Expected Inflation | **REJECTED** | +2 | +0.44 | +0.40 | +0.04 | [+0.25, +0.59] | 0.0151 | no | 519 |  | expectations |
| 184 | 13-Year Expected Inflation | **REJECTED** | +2 | +0.44 | +0.42 | +0.01 | [+0.15, +0.62] | 0.0151 | no | 519 |  | expectations |
| 185 | Import Price Index (End Use): Fuels, N.e.s. | **REJECTED** | +2 | +0.44 | +0.42 | +0.02 | [+0.06, +0.67] | 0.0106 | no | 424 |  | import |
| 186 | 14-Year Expected Inflation | **REJECTED** | +2 | +0.43 | +0.42 | +0.01 | [+0.15, +0.62] | 0.0151 | no | 519 |  | expectations |
| 187 | Future New Orders | **REJECTED** | -6 | -0.43 | -0.25 | +0.18 | [-0.65, -0.12] | 0.0424 | no | 281 |  | regionalfed_future |
| 188 | 15-Year Expected Inflation | **REJECTED** | +2 | +0.43 | +0.41 | +0.01 | [+0.15, +0.61] | 0.0151 | no | 519 |  | expectations |
| 189 | Chemicals and Allied Products: Fats and Oils | **REJECTED** | +10 | +0.42 | +0.18 | +0.25 | [+0.07, +0.62] | 0.0043 | no | 691 |  | ppi_chemicals |
| 190 | Import Price Index (End Use): Furniture, Hou | **REJECTED** | +0 | +0.42 | +0.42 | +0.00 | [+0.18, +0.62] | 0.2936 | no | 432 |  | import |
| 191 | 16-Year Expected Inflation | **REJECTED** | +2 | +0.42 | +0.41 | +0.01 | [+0.15, +0.61] | 0.0151 | no | 519 |  | expectations |
| 192 | Current Prices Received | **REJECTED** | -8 | -0.42 | +0.00 | +0.42 | [-0.58, -0.23] | 0.0259 | yes | 677 |  | regionalfed_current |
| 193 | Future Prices Paid | **REJECTED** | -10 | -0.42 | +0.16 | +0.26 | [-0.59, -0.16] | 0.0043 | yes | 277 |  | regionalfed_future |
| 194 | Import Price Index (End Use): Natural Gas | **REJECTED** | +2 | +0.42 | +0.40 | +0.02 | [+0.04, +0.65] | 0.0043 | no | 416 |  | import |
| 195 | 17-Year Expected Inflation | **REJECTED** | +2 | +0.42 | +0.40 | +0.01 | [+0.14, +0.60] | 0.0151 | no | 519 |  | expectations |
| 196 | 18-Year Expected Inflation | **REJECTED** | +2 | +0.41 | +0.40 | +0.01 | [+0.14, +0.60] | 0.0151 | no | 519 |  | expectations |
| 197 | Current Prices Paid | **REJECTED** | -8 | -0.41 | -0.00 | +0.41 | [-0.55, -0.23] | 0.0259 | yes | 677 |  | regionalfed_current |
| 198 | New Orders: Machinery | **REJECTED** | +3 | +0.41 | +0.37 | +0.04 | [+0.29, +0.57] | 0.2458 | yes | 397 |  | orders |
| 199 | Import Price Index (End Use): Paper and Pape | **REJECTED** | -1 | +0.41 | +0.41 | +0.00 | [+0.25, +0.62] | 0.1931 | yes | 439 |  | import |
| 200 | 19-Year Expected Inflation | **REJECTED** | +2 | +0.41 | +0.40 | +0.01 | [+0.14, +0.59] | 0.0151 | no | 519 |  | expectations |
| 201 | Construction spending: power | **REJECTED** | -12 | +0.41 | +0.04 | +0.36 | [+0.17, +0.65] | 0.2936 | yes | 269 |  | demand |
| 202 | Iron Ore | **REJECTED** | +14 | +0.40 | +0.16 | +0.24 | [+0.10, +0.63] | 0.1792 | yes | 387 |  | commodity |
| 203 | Import Price Index (End Use): Automotive Par | **REJECTED** | +0 | +0.40 | +0.40 | +0.00 | [+0.18, +0.63] | 0.3184 | no | 421 |  | import |
| 204 | Fuels and Related Products and Power: Utilit | **REJECTED** | +1 | +0.40 | +0.39 | +0.01 | [+0.04, +0.68] | 0.0151 | no | 413 |  | ppi_fuels_power |
| 205 | Total Business: Inventories to Sales Ratio | **REJECTED** | -9 | +0.39 | -0.01 | +0.38 | [+0.09, +0.58] | 0.0043 | yes | 391 |  | inventories |
| 206 | Metals and Metal Products: Vitreous China Pl | **REJECTED** | +0 | +0.39 | +0.39 | +0.00 | [-0.05, +0.66] | 0.0151 | no | 549 |  | ppi_metals |
| 207 | New Orders: Durable Goods | **REJECTED** | +6 | +0.38 | +0.31 | +0.07 | [+0.21, +0.55] | 0.242 | no | 394 |  | orders |
| 208 | Future Capital Expenditures | **REJECTED** | -11 | -0.38 | +0.10 | +0.28 | [-0.53, -0.17] | 0.0826 | yes | 276 |  | regionalfed_future |
| 209 | Natural gas PPI | **REJECTED** | +3 | +0.38 | +0.35 | +0.03 | [+0.11, +0.60] | 0.0043 | no | 698 |  | energy |
| 210 | Current Unfilled Orders; Percent Reporting D | **REJECTED** | -3 | +0.38 | +0.35 | +0.02 | [+0.12, +0.53] | 0.0167 | yes | 682 |  | orders |
| 211 | Current Delivery Time | **REJECTED** | -6 | -0.37 | -0.23 | +0.14 | [-0.57, -0.11] | 0.0228 | yes | 679 |  | regionalfed_current |
| 212 | Machinery Manufacturing | **REJECTED** | -3 | +0.37 | +0.35 | +0.02 | [+0.23, +0.51] | 0.2819 | yes | 422 |  | employment |
| 213 | Nominal Broad U.S. Dollar Index | **REJECTED** | +6 | -0.37 | -0.16 | +0.21 | [-0.70, -0.11] | 0.4008 | no | 227 |  | dollar |
| 214 | Current General Business Conditions | **REJECTED** | -8 | -0.37 | -0.14 | +0.22 | [-0.55, -0.13] | 0.0043 | yes | 279 |  | regionalfed_current |
| 215 | Current New Orders | **REJECTED** | -8 | -0.37 | -0.13 | +0.24 | [-0.54, -0.16] | 0.0043 | yes | 279 |  | regionalfed_current |
| 216 | New Orders: Nondefense Capital Goods | **REJECTED** | +7 | +0.37 | +0.26 | +0.10 | [+0.18, +0.53] | 0.0043 | no | 393 |  | orders |
| 217 | Manufacturers' Unfilled Orders: Industrial M | **REJECTED** | -4 | +0.36 | +0.32 | +0.04 | [+0.18, +0.55] | 0.2755 | yes | 397 |  | orders |
| 218 | Producer Price Index by Industry: Carbon and | **REJECTED** | -6 | +0.36 | +0.29 | +0.07 | [+0.16, +0.58] | 0.1243 | no | 695 |  | grid_datacenter |
| 219 | Import Price Index (End Use): Toys, Games, a | **REJECTED** | -5 | +0.36 | +0.30 | +0.06 | [+0.15, +0.60] | 0.5581 | no | 423 |  | import |
| 220 | Primary Metal Manufacturing | **REJECTED** | -2 | +0.36 | +0.34 | +0.01 | [+0.20, +0.49] | 0.2606 | yes | 423 |  | employment |
| 221 | Global price of Agr. Raw Material Index | **REJECTED** | +4 | +0.35 | +0.28 | +0.08 | [+0.24, +0.55] | 0.4705 | yes | 397 |  | commodity_fx |
| 222 | Global lead price | **REJECTED** | +6 | +0.35 | +0.20 | +0.15 | [+0.23, +0.56] | 0.2611 | yes | 395 |  | basemetal |
| 223 | Producer Price Index by Commodity: Metals an | **REJECTED** | +9 | +0.35 | +0.12 | +0.23 | [+0.12, +0.56] | 0.0361 | no | 608 |  | input_ppi |
| 224 | Authorized in Permit-Issuing Places: Single- | **REJECTED** | -3 | -0.34 | -0.32 | +0.02 | [-0.48, -0.20] | 0.1338 | yes | 698 |  | construction |
| 225 | Uranium | **REJECTED** | -3 | +0.34 | +0.32 | +0.02 | [+0.09, +0.62] | 0.4971 | no | 398 |  | commodity |
| 226 | Manufacturers: Inventories to Sales Ratio | **REJECTED** | -10 | +0.34 | -0.03 | +0.31 | [+0.16, +0.52] | 0.0705 | no | 390 |  | inventories |
| 227 | New Privately-Owned Housing Units Authorized | **REJECTED** | -3 | -0.34 | -0.32 | +0.02 | [-0.47, -0.19] | 0.1322 | yes | 698 |  | construction |
| 228 | Import Price Index (End Use): Other Precious | **REJECTED** | +11 | +0.34 | +0.16 | +0.17 | [+0.02, +0.58] | 0.2294 | no | 407 |  | import |
| 229 | Import Price Index (End Use): Nonelectrical | **REJECTED** | +2 | +0.33 | +0.33 | +0.01 | [+0.12, +0.54] | 0.4019 | no | 443 |  | import |
| 230 | Import Price Index (End Use): Green Coffee, | **REJECTED** | +2 | +0.33 | +0.31 | +0.02 | [+0.18, +0.52] | 0.237 | no | 423 |  | import |
| 231 | Nominal Advanced Foreign Economies U.S. Doll | **REJECTED** | +7 | -0.33 | -0.04 | +0.29 | [-0.69, -0.06] | 0.4264 | no | 226 |  | dollar |
| 232 | New Privately-Owned Housing Units Started: S | **REJECTED** | -4 | -0.33 | -0.30 | +0.03 | [-0.47, -0.19] | 0.1338 | no | 697 |  | construction |
| 233 | Started: Single-Family Units | **REJECTED** | -4 | -0.33 | -0.29 | +0.04 | [-0.46, -0.19] | 0.1338 | no | 697 |  | construction |
| 234 | Natural Gas, US Henry Hub Gas | **REJECTED** | +2 | +0.33 | +0.32 | +0.01 | [+0.03, +0.59] | 0.0158 | no | 399 |  | commodity |
| 235 | Future Prices Received | **REJECTED** | -7 | -0.33 | -0.04 | +0.29 | [-0.49, -0.11] | 0.0259 | no | 678 |  | regionalfed_future |
| 236 | 5-Year, 5-Year Forward Inflation Expectation | **REJECTED** | +7 | +0.33 | +0.19 | +0.13 | [+0.13, +0.63] | 0.2062 | no | 262 |  | expectations |
| 237 | Capacity Utilization: Manufacturing: Durable | **REJECTED** | +11 | +0.32 | +0.12 | +0.21 | [+0.18, +0.45] | 0.2734 | no | 690 |  | grid_datacenter |
| 238 | Machinery and Equipment: Parts for Construct | **REJECTED** | -3 | +0.32 | +0.30 | +0.02 | [+0.14, +0.86] | 0.2633 | no | 303 |  | ppi_machinery |
| 239 | Employment: electrical-equip mfg | **REJECTED** | -2 | +0.32 | +0.32 | +0.01 | [+0.10, +0.47] | 0.3692 | no | 423 |  | macro |
| 240 | Industrial Capacity: Utilities: Natural Gas | **REJECTED** | -23 | -0.32 | -0.28 | +0.04 | [-0.55, -0.17] | 0.2615 | no | 678 |  | grid_datacenter |
| 241 | Industrial Production: Durable Goods Materia | **REJECTED** | -6 | -0.32 | -0.22 | +0.10 | [-0.49, -0.13] | 0.2533 | no | 695 |  | grid_datacenter |
| 242 | Industrial Production: Durable Goods Materia | **REJECTED** | -6 | -0.32 | -0.22 | +0.10 | [-0.49, -0.13] | 0.2533 | no | 695 |  | grid_datacenter |
| 243 | Import Price Index (End Use): Capital Goods, | **REJECTED** | -3 | +0.32 | +0.32 | +0.00 | [+0.13, +0.54] | 0.454 | no | 470 |  | import |
| 244 | Future Unfilled Orders; Percent Reporting De | **REJECTED** | -21 | -0.32 | +0.11 | +0.20 | [-0.44, -0.16] | 0.0043 | no | 664 |  | orders |
| 245 | Manufacturers' Unfilled Orders: Mining, Oil, | **REJECTED** | +2 | +0.31 | +0.31 | +0.01 | [+0.13, +0.57] | 0.6818 | no | 399 |  | orders |
| 246 | Industrial Production: Consumer Goods | **REJECTED** | -5 | -0.31 | -0.25 | +0.06 | [-0.48, -0.15] | 0.1363 | no | 696 |  | ip_capacity |
| 247 | Future Unfilled Orders; Percent Reporting De | **REJECTED** | -21 | -0.31 | +0.11 | +0.20 | [-0.44, -0.16] | 0.0043 | no | 664 |  | orders |
| 248 | Authorized in Permit-Issuing Places: Total U | **REJECTED** | -2 | -0.31 | -0.31 | +0.00 | [-0.50, -0.15] | 0.2062 | no | 699 |  | construction |
| 249 | Manufacturing: Durable Goods: Primary Metal | **REJECTED** | -10 | -0.31 | +0.03 | +0.28 | [-0.48, -0.13] | 0.0043 | no | 691 |  | capacity |
| 250 | Industrial production: manufacturing | **REJECTED** | -8 | -0.31 | -0.12 | +0.19 | [-0.49, -0.11] | 0.0043 | no | 633 |  | demand |
| 251 | Manufacturing (NAICS) | **REJECTED** | -8 | -0.31 | -0.12 | +0.19 | [-0.49, -0.11] | 0.0043 | no | 633 |  | ip |
| 252 | New Privately-Owned Housing Units Authorized | **REJECTED** | -2 | -0.31 | -0.31 | +0.00 | [-0.49, -0.15] | 0.1939 | no | 699 |  | construction |
| 253 | Capacity utilization: manufacturing | **REJECTED** | -8 | -0.31 | -0.10 | +0.20 | [-0.51, -0.12] | 0.0043 | no | 633 |  | demand |
| 254 | Import Price Index (End Use): Vegetables | **REJECTED** | -9 | +0.31 | +0.09 | +0.22 | [+0.20, +0.43] | 0.0043 | no | 421 |  | import |
| 255 | Started: Total Units | **REJECTED** | -2 | -0.31 | -0.29 | +0.01 | [-0.48, -0.14] | 0.1457 | no | 699 |  | construction |
| 256 | New Privately-Owned Housing Units Started: T | **REJECTED** | -3 | -0.30 | -0.30 | +0.01 | [-0.47, -0.15] | 0.1457 | no | 698 |  | construction |
| 257 | Import Price Index (End Use): Meat Products | **REJECTED** | +2 | +0.30 | +0.27 | +0.03 | [+0.06, +0.53] | 0.2763 | no | 428 |  | import |
| 258 | Import Price Index (End Use): Fruits and Fro | **REJECTED** | +2 | +0.30 | +0.28 | +0.02 | [+0.12, +0.48] | 0.0043 | no | 428 |  | import |
| 259 | Import Price Index (End Use): Metal Working | **REJECTED** | -5 | +0.30 | +0.27 | +0.03 | [+0.11, +0.53] | 0.6937 | no | 420 |  | import |
| 260 | Durable Goods Materials: Durable Goods Mater | **REJECTED** | -9 | -0.30 | -0.13 | +0.17 | [-0.48, -0.10] | 0.1296 | no | 692 |  | ip |
| 261 | Import Price Index (End Use): Apparel, House | **REJECTED** | -7 | +0.30 | +0.25 | +0.05 | [+0.05, +0.59] | 0.3179 | no | 423 |  | import |
| 262 | Manufacturing: Durable Goods: Electrical Equ | **REJECTED** | -7 | -0.30 | -0.15 | +0.14 | [-0.53, -0.04] | 0.1453 | no | 634 |  | ip |
| 263 | Capacity Utilization: Manufacturing Excludin | **REJECTED** | -7 | -0.29 | -0.12 | +0.18 | [-0.50, -0.07] | 0.1286 | no | 694 |  | grid_datacenter |
| 264 | 10-Year Treasury Constant Maturity Minus 2-Y | **REJECTED** | -24 | +0.29 | -0.18 | +0.11 | [+0.16, +0.47] | 0.3541 | no | 564 |  | rates |
| 265 | 10-Year Treasury Constant Maturity Minus 2-Y | **REJECTED** | -24 | +0.29 | -0.18 | +0.11 | [+0.16, +0.47] | 0.3541 | no | 564 |  | rates |
| 266 | Current Unfilled Orders | **REJECTED** | -3 | -0.29 | -0.26 | +0.03 | [-0.46, -0.10] | 0.0167 | no | 682 |  | regionalfed_current |
| 267 | Fabricated Metal Product Manufacturing | **REJECTED** | -1 | +0.29 | +0.28 | +0.01 | [+0.13, +0.43] | 0.5587 | no | 424 |  | employment |
| 268 | Energy, Total | **REJECTED** | +20 | -0.29 | +0.16 | +0.13 | [-0.55, +0.06] | 0.065 | no | 681 |  | ip |
| 269 | Current Unfilled Orders; Diffusion Index for | **REJECTED** | -3 | -0.29 | -0.26 | +0.03 | [-0.46, -0.10] | 0.0167 | no | 682 |  | orders |
| 270 | Inflation Expectation | **REJECTED** | +5 | +0.29 | +0.19 | +0.10 | [+0.05, +0.60] | 0.0151 | no | 564 |  | expectations |
| 271 | Future Unfilled Orders; Diffusion Index for | **REJECTED** | -20 | +0.29 | -0.06 | +0.23 | [+0.16, +0.41] | 0.0043 | no | 665 |  | orders |
| 272 | Future Unfilled Orders; Diffusion Index for | **REJECTED** | -20 | +0.29 | -0.06 | +0.23 | [+0.16, +0.41] | 0.0043 | no | 665 |  | orders |
| 273 | Manufacturing: Durable Goods: Machinery (NAI | **REJECTED** | -14 | -0.29 | +0.08 | +0.20 | [-0.45, -0.13] | 0.1307 | no | 627 |  | ip |
| 274 | Manufacturers' Unfilled Orders: Ferrous Meta | **REJECTED** | +2 | +0.29 | +0.28 | +0.01 | [+0.01, +0.50] | 0.5524 | no | 399 |  | orders |
| 275 | Chemicals and Allied Products: Drugs and Pha | **REJECTED** | -3 | +0.28 | +0.26 | +0.02 | [-0.02, +0.61] | 0.3111 | no | 698 |  | ppi_chemicals |
| 276 | Producer Price Index by Industry: Pipeline T | **REJECTED** | -24 | +0.28 | +0.15 | +0.13 | [+0.14, +0.51] | 0.4737 | no | 347 |  | freight |
| 277 | Consumer Sentiment | **REJECTED** | +1 | -0.28 | -0.28 | +0.00 | [-0.45, -0.07] | 0.0158 | no | 612 |  | sentiment |
| 278 | Industrial Production: Total Index | **REJECTED** | -8 | -0.28 | -0.11 | +0.17 | [-0.47, -0.07] | 0.1322 | no | 693 |  | ip_capacity |
| 279 | Industrial Production: Total Index | **REJECTED** | -8 | -0.28 | -0.10 | +0.17 | [-0.47, -0.07] | 0.1322 | no | 693 |  | ip_capacity |
| 280 | Industrial Production: Durable Consumer Good | **REJECTED** | -5 | -0.28 | -0.21 | +0.07 | [-0.44, -0.14] | 0.0538 | no | 696 |  | ip_capacity |
| 281 | Construction | **REJECTED** | -10 | -0.28 | -0.18 | +0.09 | [-0.52, -0.06] | 0.3126 | no | 691 |  | employment |
| 282 | Manufacturing: Durable Goods: Primary Metal | **REJECTED** | -10 | -0.27 | +0.05 | +0.23 | [-0.48, -0.05] | 0.0043 | no | 631 |  | ip |
| 283 | Future Prices Paid | **REJECTED** | -8 | -0.27 | -0.02 | +0.25 | [-0.43, -0.07] | 0.0043 | no | 677 |  | regionalfed_future |
| 284 | Producer Price Index by Industry: Scheduled | **REJECTED** | -13 | -0.27 | +0.20 | +0.08 | [-0.61, +0.29] | 0.3996 | no | 437 |  | freight |
| 285 | Producer Price Index by Industry: Pipeline T | **REJECTED** | -24 | +0.27 | +0.12 | +0.15 | [+0.10, +0.49] | 0.3839 | no | 444 |  | freight |
| 286 | Future Capital Expenditures | **REJECTED** | -6 | -0.27 | -0.19 | +0.07 | [-0.44, -0.10] | 0.0228 | no | 679 |  | regionalfed_future |
| 287 | Materials | **REJECTED** | -8 | -0.27 | -0.10 | +0.16 | [-0.48, -0.05] | 0.2069 | no | 693 |  | ip |
| 288 | Future Capital Expenditures; Diffusion Index | **REJECTED** | -6 | -0.27 | -0.19 | +0.07 | [-0.44, -0.10] | 0.0228 | no | 679 |  | regionalfed_future |
| 289 | Current Work Hours; Percent Reporting Increa | **REJECTED** | -5 | -0.27 | -0.18 | +0.08 | [-0.45, -0.05] | 0.0196 | no | 680 |  | regionalfed_current |
| 290 | Import Price Index (End Use): Consumer Goods | **REJECTED** | +0 | +0.27 | +0.27 | +0.00 | [+0.09, +0.54] | 0.78 | no | 463 |  | import |
| 291 | Current Work Hours; Percent Reporting Increa | **REJECTED** | -5 | -0.27 | -0.18 | +0.08 | [-0.45, -0.05] | 0.0196 | no | 680 |  | regionalfed_current |
| 292 | Current Work Hours; Diffusion Index for Fede | **REJECTED** | -5 | -0.26 | -0.18 | +0.08 | [-0.41, -0.09] | 0.0196 | no | 680 |  | regionalfed_current |
| 293 | Current Work Hours; Diffusion Index for Fede | **REJECTED** | -5 | -0.26 | -0.18 | +0.08 | [-0.41, -0.09] | 0.0196 | no | 680 |  | regionalfed_current |
| 294 | Mining: Mining (NAICS = 21) | **REJECTED** | +19 | -0.26 | +0.21 | +0.05 | [-0.50, +0.03] | 0.242 | no | 682 |  | ip |
| 295 | Producer Price Index by Industry: Scheduled | **REJECTED** | -13 | -0.26 | +0.20 | +0.06 | [-0.60, +0.29] | 0.4207 | no | 437 |  | freight |
| 296 | Moody's Seasoned Aaa Corporate Bond Minus Fe | **REJECTED** | +13 | -0.26 | +0.05 | +0.21 | [-0.49, -0.05] | 0.174 | no | 688 |  | rates |
| 297 | Manufacturing: Durable Goods: Machinery (NAI | **REJECTED** | -13 | -0.26 | +0.06 | +0.20 | [-0.44, -0.08] | 0.423 | no | 688 |  | capacity |
| 298 | 3-Month Treasury Bill Minus Federal Funds Ra | **REJECTED** | +11 | -0.26 | +0.09 | +0.17 | [-0.47, -0.08] | 0.2463 | no | 690 |  | rates |
| 299 | Current Employment | **REJECTED** | -8 | -0.26 | -0.11 | +0.15 | [-0.44, -0.06] | 0.0259 | no | 677 |  | regionalfed_current |
| 300 | Manufacturing: Durable Goods: Iron and Steel | **REJECTED** | -10 | -0.26 | +0.08 | +0.18 | [-0.46, -0.04] | 0.0043 | no | 631 |  | ip |
| 301 | Moody's Seasoned Baa Corporate Bond Minus Fe | **REJECTED** | +12 | -0.25 | +0.09 | +0.17 | [-0.46, -0.07] | 0.4066 | no | 689 |  | rates |
| 302 | Baa Corporate Bond Yield Relative to Yield o | **REJECTED** | +9 | -0.25 | -0.04 | +0.22 | [-0.39, -0.09] | 0.2453 | no | 464 |  | credit |
| 303 | 6-Month Treasury Bill Minus Federal Funds Ra | **REJECTED** | +11 | -0.25 | +0.12 | +0.13 | [-0.47, -0.07] | 0.2755 | no | 690 |  | rates |
| 304 | Total Construction | **REJECTED** | -24 | -0.25 | +0.12 | +0.13 | [-0.68, +0.06] | 0.7075 | no | 365 |  | construction |
| 305 | Manufacturing: Durable Goods: Electrical Equ | **REJECTED** | -6 | -0.25 | -0.14 | +0.11 | [-0.53, +0.03] | 0.3182 | no | 635 |  | capacity |
| 306 | New Privately-Owned Housing Units Authorized | **REJECTED** | +3 | -0.25 | -0.23 | +0.02 | [-0.45, -0.05] | 0.2082 | no | 698 |  | construction |
| 307 | Manufacturing: Durable Goods: Fabricated Met | **REJECTED** | -12 | -0.25 | +0.01 | +0.24 | [-0.42, -0.07] | 0.2981 | no | 629 |  | ip |
| 308 | 1-Year Treasury Constant Maturity Minus Fede | **REJECTED** | -5 | +0.24 | +0.16 | +0.09 | [-0.07, +0.47] | 0.2734 | no | 696 |  | rates |
| 309 | Import Price Index (End Use): Passenger Cars | **REJECTED** | -19 | +0.24 | +0.06 | +0.18 | [+0.12, +0.45] | 0.5088 | no | 408 |  | import |
| 310 | New Privately-Owned Housing Units Authorized | **REJECTED** | +3 | -0.24 | -0.23 | +0.02 | [-0.45, -0.04] | 0.2174 | no | 698 |  | construction |
| 311 | Capacity Utilization: Total Excluding Comput | **REJECTED** | -9 | -0.24 | -0.03 | +0.21 | [-0.44, -0.04] | 0.3427 | no | 692 |  | grid_datacenter |
| 312 | Aaa Corporate Bond Yield Relative to Yield o | **REJECTED** | +9 | -0.24 | -0.11 | +0.13 | [-0.37, -0.10] | 0.455 | no | 500 |  | credit |
| 313 | 10-Year Breakeven Inflation Rate | **REJECTED** | +7 | +0.24 | +0.10 | +0.13 | [+0.09, +0.69] | 0.4321 | no | 262 |  | expectations |
| 314 | Moody's Seasoned Baa Corporate Bond Yield Re | **REJECTED** | -6 | +0.24 | +0.13 | +0.10 | [+0.07, +0.41] | 0.4125 | no | 695 |  | rates |
| 315 | Rubber | **REJECTED** | +10 | +0.24 | +0.11 | +0.12 | [+0.03, +0.44] | 0.8467 | no | 391 |  | commodity |
| 316 | New Orders: Computers and Electronic Product | **REJECTED** | +3 | +0.23 | +0.22 | +0.02 | [+0.07, +0.41] | 0.49 | no | 397 |  | orders |
| 317 | Producer Price Index by Industry: Pipeline T | **REJECTED** | -24 | +0.23 | +0.15 | +0.08 | [+0.05, +0.41] | 0.4954 | no | 444 |  | freight |
| 318 | 10-Year Treasury Constant Maturity Minus Fed | **REJECTED** | +13 | -0.23 | +0.07 | +0.16 | [-0.47, -0.01] | 0.3692 | no | 688 |  | rates |
| 319 | Import Price Index (End Use): Apparel, Texti | **REJECTED** | +23 | -0.23 | +0.09 | +0.14 | [-0.35, -0.11] | 0.8535 | no | 399 |  | import |
| 320 | Industrial Capacity: Manufacturing: Durable | **REJECTED** | +20 | -0.23 | -0.12 | +0.11 | [-0.39, -0.05] | 0.6439 | no | 681 |  | grid_datacenter |
| 321 | 5-Year Treasury Constant Maturity Minus Fede | **REJECTED** | +14 | -0.23 | +0.11 | +0.12 | [-0.46, -0.02] | 0.2861 | no | 687 |  | rates |
| 322 | New Privately-Owned Housing Units Started: U | **REJECTED** | +3 | -0.23 | -0.21 | +0.02 | [-0.43, -0.02] | 0.2533 | no | 698 |  | construction |
| 323 | Industrial Production: Final Products | **REJECTED** | -10 | -0.22 | -0.07 | +0.15 | [-0.38, -0.04] | 0.478 | no | 691 |  | ip_capacity |
| 324 | Import Price Index (End Use): Automotive Veh | **REJECTED** | +0 | +0.22 | +0.22 | +0.00 | [+0.02, +0.46] | 0.6737 | no | 467 |  | import |
| 325 | Current New Orders | **REJECTED** | -3 | -0.22 | -0.20 | +0.02 | [-0.39, -0.04] | 0.0167 | no | 682 |  | regionalfed_current |
| 326 | Current Unfilled Orders; Percent Reporting I | **REJECTED** | -3 | -0.22 | -0.18 | +0.04 | [-0.37, -0.07] | 0.0167 | no | 682 |  | orders |
| 327 | Current Unfilled Orders; Percent Reporting I | **REJECTED** | -3 | -0.22 | -0.19 | +0.03 | [-0.37, -0.06] | 0.0167 | no | 682 |  | orders |
| 328 | 10-Year Treasury Constant Maturity Minus 3-M | **REJECTED** | -8 | -0.22 | -0.10 | +0.12 | [-0.47, +0.13] | 0.6638 | no | 513 |  | rates |
| 329 | Future Unfilled Orders; Percent Reporting In | **REJECTED** | -19 | +0.22 | +0.00 | +0.22 | [+0.12, +0.33] | 0.0797 | no | 666 |  | orders |
| 330 | Future Unfilled Orders; Percent Reporting In | **REJECTED** | -19 | +0.22 | +0.00 | +0.22 | [+0.12, +0.32] | 0.0797 | no | 666 |  | orders |
| 331 | Industrial Capacity: Total Excluding Compute | **REJECTED** | +6 | -0.21 | -0.17 | +0.04 | [-0.48, +0.13] | 0.625 | no | 695 |  | grid_datacenter |
| 332 | Future Capital Expenditures; Percent Reporti | **REJECTED** | -5 | +0.21 | +0.16 | +0.05 | [+0.07, +0.38] | 0.0196 | no | 680 |  | regionalfed_future |
| 333 | Future General Activity; Percent Reporting D | **REJECTED** | -24 | -0.21 | +0.02 | +0.19 | [-0.34, -0.07] | 0.3948 | no | 661 |  | regionalfed_future |
| 334 | Future Capital Expenditures; Percent Reporti | **REJECTED** | -5 | +0.21 | +0.16 | +0.05 | [+0.07, +0.38] | 0.0196 | no | 680 |  | regionalfed_future |
| 335 | Current General Activity | **REJECTED** | -1 | -0.21 | -0.20 | +0.01 | [-0.36, -0.04] | 0.0228 | no | 684 |  | regionalfed_current |
| 336 | Future General Activity; Percent Reporting D | **REJECTED** | -24 | -0.21 | +0.02 | +0.19 | [-0.34, -0.08] | 0.3948 | no | 661 |  | regionalfed_future |
| 337 | Current General Activity; Percent Reporting | **REJECTED** | -17 | +0.21 | -0.08 | +0.13 | [-0.06, +0.46] | 0.1476 | no | 668 |  | regionalfed_current |
| 338 | Future Capital Expenditures; Percent Reporti | **REJECTED** | -7 | -0.21 | -0.13 | +0.08 | [-0.35, -0.06] | 0.1649 | no | 678 |  | regionalfed_future |
| 339 | Future New Orders | **REJECTED** | -22 | +0.21 | -0.03 | +0.18 | [+0.07, +0.34] | 0.3617 | no | 663 |  | regionalfed_future |
| 340 | Current General Activity; Diffusion Index fo | **REJECTED** | -1 | -0.21 | -0.20 | +0.01 | [-0.36, -0.04] | 0.0695 | no | 684 |  | regionalfed_current |
| 341 | Moody's Seasoned Aaa Corporate Bond Yield Re | **REJECTED** | +12 | -0.20 | -0.04 | +0.16 | [-0.35, -0.05] | 0.5488 | no | 689 |  | rates |
| 342 | Current General Activity; Percent Reporting | **REJECTED** | +7 | +0.20 | +0.08 | +0.13 | [+0.04, +0.34] | 0.0043 | no | 678 |  | regionalfed_current |
| 343 | Industrial production: utilities | **REJECTED** | -13 | -0.20 | -0.04 | +0.16 | [-0.33, -0.07] | 0.3286 | no | 688 |  | demand |
| 344 | Future Capital Expenditures; Percent Reporti | **REJECTED** | -7 | -0.20 | -0.13 | +0.07 | [-0.35, -0.05] | 0.1657 | no | 678 |  | regionalfed_future |
| 345 | Producer Price Index by Industry: Pipeline T | **REJECTED** | -24 | +0.20 | +0.15 | +0.05 | [+0.01, +0.39] | 0.6137 | no | 444 |  | freight |
| 346 | Current Work Hours; Percent Reporting Decrea | **REJECTED** | -5 | +0.20 | +0.14 | +0.06 | [+0.06, +0.35] | 0.0375 | no | 680 |  | regionalfed_current |
| 347 | Current Work Hours; Percent Reporting Decrea | **REJECTED** | -5 | +0.20 | +0.14 | +0.06 | [+0.06, +0.35] | 0.0375 | no | 680 |  | regionalfed_current |
| 348 | Future General Activity | **REJECTED** | -24 | +0.20 | -0.02 | +0.18 | [+0.06, +0.35] | 0.4661 | no | 661 |  | regionalfed_future |
| 349 | Current General Activity; Percent Reporting | **REJECTED** | -16 | +0.20 | -0.01 | +0.19 | [-0.07, +0.36] | 0.1476 | no | 669 |  | regionalfed_current |
| 350 | Future General Activity; Diffusion Index for | **REJECTED** | -24 | +0.20 | -0.02 | +0.18 | [+0.06, +0.35] | 0.4661 | no | 661 |  | regionalfed_future |
| 351 | Industrial Production: Utilities: Electric a | **REJECTED** | -13 | -0.19 | -0.04 | +0.15 | [-0.31, -0.07] | 0.3363 | no | 688 |  | grid_datacenter |
| 352 | New Privately-Owned Housing Units Authorized | **REJECTED** | +6 | -0.19 | -0.16 | +0.02 | [-0.44, +0.04] | 0.677 | no | 695 |  | construction |
| 353 | Producer Price Index by Industry: Scheduled | **REJECTED** | +9 | -0.18 | -0.05 | +0.13 | [-0.34, -0.05] | 0.641 | no | 438 |  | freight |
| 354 | Import Price Index (End Use): Nondurables, M | **REJECTED** | -24 | +0.18 | +0.02 | +0.17 | [-0.06, +0.38] | 0.8526 | no | 415 |  | import |
| 355 | New Privately-Owned Housing Units Authorized | **REJECTED** | +6 | -0.18 | -0.16 | +0.02 | [-0.43, +0.04] | 0.6794 | no | 695 |  | construction |
| 356 | Future General Activity; Percent Reporting N | **REJECTED** | +9 | +0.18 | +0.06 | +0.12 | [+0.02, +0.33] | 0.1157 | no | 676 |  | regionalfed_future |
| 357 | Current General Activity; Percent Reporting | **REJECTED** | -3 | +0.18 | +0.17 | +0.01 | [+0.01, +0.35] | 0.2673 | no | 682 |  | regionalfed_current |
| 358 | Current General Activity; Percent Reporting | **REJECTED** | -3 | +0.18 | +0.16 | +0.02 | [+0.01, +0.35] | 0.2673 | no | 682 |  | regionalfed_current |
| 359 | Future Work Hours; Percent Reporting Increas | **REJECTED** | -24 | +0.17 | +0.01 | +0.16 | [+0.07, +0.29] | 0.3912 | no | 661 |  | regionalfed_future |
| 360 | Future Work Hours; Percent Reporting Increas | **REJECTED** | -24 | +0.17 | +0.01 | +0.16 | [+0.07, +0.29] | 0.3912 | no | 661 |  | regionalfed_future |
| 361 | Future Work Hours; Diffusion Index for Feder | **REJECTED** | -24 | +0.17 | -0.01 | +0.16 | [+0.08, +0.28] | 0.499 | no | 661 |  | regionalfed_future |
| 362 | Future Work Hours; Diffusion Index for Feder | **REJECTED** | -24 | +0.17 | -0.01 | +0.16 | [+0.07, +0.28] | 0.4962 | no | 661 |  | regionalfed_future |
| 363 | Future General Activity; Percent Reporting N | **REJECTED** | +9 | +0.17 | +0.06 | +0.12 | [+0.01, +0.32] | 0.2981 | no | 676 |  | regionalfed_future |
| 364 | Capacity Utilization: Utilities: Electric an | **REJECTED** | -13 | -0.17 | -0.01 | +0.16 | [-0.28, -0.05] | 0.2673 | no | 688 |  | grid_datacenter |
| 365 | Producer Price Index by Commodity: Metals an | **REJECTED** | +0 | +0.17 | +0.17 | +0.00 | [-0.05, +0.43] | 0.8947 | no | 394 |  | input_ppi |
| 366 | Industrial Capacity: Utilities: Electric Pow | **REJECTED** | +18 | +0.17 | -0.02 | +0.15 | [-0.12, +0.51] | 0.6761 | no | 683 |  | grid_datacenter |
| 367 | Industrial Production: Durable Consumer Good | **REJECTED** | -4 | -0.17 | -0.13 | +0.04 | [-0.31, -0.06] | 0.5281 | no | 697 |  | ip_capacity |
| 368 | New Privately-Owned Housing Units Started: U | **REJECTED** | +4 | -0.16 | -0.14 | +0.02 | [-0.38, +0.03] | 0.7821 | no | 697 |  | construction |
| 369 | Future General Activity; Percent Reporting I | **REJECTED** | -24 | +0.16 | +0.08 | +0.08 | [+0.04, +0.30] | 0.5506 | no | 661 |  | regionalfed_future |
| 370 | Future General Activity; Percent Reporting I | **REJECTED** | -24 | +0.16 | +0.08 | +0.08 | [+0.05, +0.30] | 0.5604 | no | 661 |  | regionalfed_future |
| 371 | Future Unfilled Orders; Percent Reporting No | **REJECTED** | -21 | +0.16 | -0.13 | +0.03 | [-0.01, +0.29] | 0.2759 | no | 664 |  | orders |
| 372 | Future Unfilled Orders; Percent Reporting No | **REJECTED** | -21 | +0.15 | -0.13 | +0.02 | [-0.02, +0.29] | 0.2936 | no | 664 |  | orders |
| 373 | Future Capital Expenditures; Percent Reporti | **REJECTED** | -7 | +0.15 | +0.09 | +0.07 | [-0.00, +0.28] | 0.1388 | no | 678 |  | regionalfed_future |
| 374 | Capacity Utilization: Utilities: Electric Po | **REJECTED** | -13 | -0.15 | -0.02 | +0.13 | [-0.26, -0.03] | 0.5893 | no | 688 |  | grid_datacenter |
| 375 | Industrial Capacity: Utilities: Electric and | **REJECTED** | +19 | +0.15 | -0.05 | +0.10 | [-0.11, +0.47] | 0.7872 | no | 682 |  | grid_datacenter |
| 376 | Current Unfilled Orders; Percent Reporting N | **REJECTED** | -15 | +0.15 | -0.10 | +0.05 | [-0.01, +0.28] | 0.2048 | no | 670 |  | orders |
| 377 | Current Unfilled Orders; Percent Reporting N | **REJECTED** | -15 | +0.15 | -0.09 | +0.05 | [-0.00, +0.29] | 0.2082 | no | 670 |  | orders |
| 378 | Future Capital Expenditures; Percent Reporti | **REJECTED** | -7 | +0.15 | +0.08 | +0.07 | [-0.00, +0.27] | 0.1413 | no | 678 |  | regionalfed_future |
| 379 | Industrial Production: Durable Consumer Good | **REJECTED** | -6 | -0.15 | -0.13 | +0.01 | [-0.30, +0.04] | 0.641 | no | 695 |  | grid_datacenter |
| 380 | Industrial Production: Durable Consumer Good | **REJECTED** | -6 | -0.14 | -0.13 | +0.01 | [-0.29, +0.04] | 0.6937 | no | 695 |  | grid_datacenter |
| 381 | Future Work Hours; Percent Reporting Decreas | **REJECTED** | +24 | +0.13 | +0.04 | +0.10 | [+0.00, +0.27] | 0.6517 | no | 661 |  | regionalfed_future |
| 382 | Future Work Hours; Percent Reporting Decreas | **REJECTED** | +24 | +0.13 | +0.03 | +0.10 | [+0.00, +0.27] | 0.6414 | no | 661 |  | regionalfed_future |
| 383 | Capacity Utilization: Utilities: Natural Gas | **REJECTED** | +22 | -0.13 | +0.01 | +0.11 | [-0.22, -0.01] | 0.4892 | no | 679 |  | grid_datacenter |
| 384 | Manufacturing employment | **REJECTED** | -12 | -0.12 | +0.04 | +0.08 | [-0.36, +0.10] | 0.8849 | no | 689 |  | macro |
| 385 | Producer Price Index by Industry: Pipeline T | **REJECTED** | +21 | +0.12 | -0.06 | +0.06 | [-0.27, +0.35] | 0.9875 | no | 447 |  | freight |
| 386 | Future Employment; Percent Reporting Decreas | **REJECTED** | -6 | +0.11 | +0.05 | +0.07 | [-0.05, +0.27] | 0.677 | no | 679 |  | regionalfed_future |
| 387 | Future Employment; Percent Reporting Decreas | **REJECTED** | -6 | +0.11 | +0.05 | +0.07 | [-0.05, +0.27] | 0.677 | no | 679 |  | regionalfed_future |
| 388 | Future Work Hours; Percent Reporting No Chan | **REJECTED** | +8 | +0.11 | +0.00 | +0.11 | [-0.04, +0.24] | 0.5263 | no | 677 |  | regionalfed_future |
| 389 | Future Work Hours; Percent Reporting No Chan | **REJECTED** | +8 | +0.11 | -0.00 | +0.10 | [-0.04, +0.23] | 0.5574 | no | 677 |  | regionalfed_future |
| 390 | Future Employment; Diffusion Index for Feder | **REJECTED** | -7 | -0.09 | -0.01 | +0.08 | [-0.35, +0.21] | 0.9875 | no | 678 |  | regionalfed_future |
| 391 | Future Employment; Diffusion Index for Feder | **REJECTED** | -7 | -0.09 | -0.01 | +0.08 | [-0.35, +0.22] | 0.99 | no | 678 |  | regionalfed_future |
| 392 | Industrial Capacity: Manufacturing Excluding | **REJECTED** | +20 | -0.09 | -0.03 | +0.06 | [-0.30, +0.19] | 0.9875 | no | 681 |  | grid_datacenter |
| 393 | Current Work Hours; Percent Reporting No Cha | **REJECTED** | -1 | +0.05 | +0.04 | +0.01 | [-0.18, +0.27] | 0.978 | no | 684 |  | regionalfed_current |
| 394 | Current Work Hours; Percent Reporting No Cha | **REJECTED** | -1 | +0.04 | +0.03 | +0.01 | [-0.18, +0.26] | 0.978 | no | 684 |  | regionalfed_current |

## Leading-signal correlation matrix (contemporaneous YoY)

Values are Pearson r. Pairs with |r| >= 0.70 are the *same underlying force* and must not count as independent confirmations.

*394×394 matrix — too large to render inline; see `leading_signal_corr_matrix.csv` and the clustered heatmap `charts/_clustered_heatmap.png`. Clusters at |r|≥0.70 listed below.*

## Flagged clusters (|r| >= 0.70 — count as ONE witness each)

- **Cluster 1:** Manufacturers' Unfilled Orders: Iron and Ste, New Orders: Primary Metals, Manufacturers' Unfilled Orders: Primary Meta, New Orders: Fabricated Metal Products, Manufacturers' Unfilled Orders: Fabricated M, Manufacturers' Unfilled Orders: Construction, New Orders: Machinery, New Orders: Computers and Electronic Product, New orders: electrical equipment, Unfilled Orders: Electrical Equipment, Appli, Aaa Corporate Bond Yield, New Orders: Total Manufacturing, New Orders: Nondefense Capital Goods, Current Work Hours; Diffusion Index for Fede, Current Work Hours; Diffusion Index for Fede, Current Work Hours; Percent Reporting Decrea, Current Work Hours; Percent Reporting Decrea, Current Work Hours; Percent Reporting Increa, Current Work Hours; Percent Reporting Increa, Baa Corporate Bond Yield, Manufacturing: Durable Goods: Primary Metal, Manufacturing: Durable Goods: Machinery (NAI, Manufacturing: Durable Goods: Electrical Equ, Capacity Utilization: Manufacturing Excludin, Capacity Utilization: Total Excluding Comput, Future Capital Expenditures, Primary Metal Manufacturing, Fabricated Metal Product Manufacturing, Machinery Manufacturing, Employment: electrical-equip mfg, 10-Year Constant Maturity, Quoted on an Inve, New Orders: Durable Goods, Current Delivery Time, Current Delivery Time, Nominal Advanced Foreign Economies U.S. Doll, Nominal Broad U.S. Dollar Index, 10-Year Expected Inflation, 11-Year Expected Inflation, 12-Year Expected Inflation, 13-Year Expected Inflation, 14-Year Expected Inflation, 15-Year Expected Inflation, 16-Year Expected Inflation, 17-Year Expected Inflation, 18-Year Expected Inflation, 19-Year Expected Inflation, 1-Year Expected Inflation, Federal Funds Effective Rate, Current General Activity; Diffusion Index fo, Current General Activity, Current General Business Conditions, Current General Activity; Percent Reporting, Current General Activity; Percent Reporting, Current General Activity; Percent Reporting, 1-Year Constant Maturity, Quoted on an Inves, 10-Year Treasury yield, 2-Year Constant Maturity, Quoted on an Inves, Market Yield on U.S. Treasury Securities at, Market Yield on U.S. Treasury Securities at, Market Yield on U.S. Treasury Securities at, Market Yield on U.S. Treasury Securities at, Started: Total Units, Started: Single-Family Units, New Privately-Owned Housing Units Started: S, New Privately-Owned Housing Units Started: U, New Privately-Owned Housing Units Started: T, Industrial Production: Total Index, Industrial Production: Total Index, Industrial Production: Final Products, Industrial Production: Consumer Goods, Industrial Production: Durable Consumer Good, Industrial Production: Durable Consumer Good, Durable Goods Materials: Durable Goods Mater, Manufacturing: Durable Goods: Iron and Steel, Manufacturing: Durable Goods: Primary Metal, Manufacturing: Durable Goods: Fabricated Met, Manufacturing: Durable Goods: Machinery (NAI, Manufacturing: Durable Goods: Electrical Equ, Manufacturing (NAICS), Industrial production: manufacturing, Materials, Import Price Index (End Use): All Commoditie, Import Price Index (End Use): Foods, Feeds,, Import Price Index (End Use): Green Coffee,, Import: Industrial Supplies & Materials, Import Price Index (End Use): Petroleum Prod, Import Price Index (End Use): Crude Oil, Import Price Index (End Use): Fuels, N.e.s., Import Price Index (End Use): Natural Gas, Import Price Index (End Use): Agricultural P, Import Price Index (End Use): Unfinished Met, Import Price Index (End Use): Major Nonferro, Import: Copper, Import: Zinc, Import Price Index (End Use): Other Precious, Import Price Index (End Use): Finished Metal, Import Price Index (End Use): Iron and Steel, Import Price Index (End Use): Iron and Steel, Import: Ind. Supplies & Materials (durable), Import: Ind. Supplies & Materials (ex-fuel), Import Price Index (End Use): Industrial Sup, Import Price Index (End Use): Capital Goods,, Import Price Index (End Use): Nonelectrical, Import Price Index (End Use): Metal Working, Import Price Index (End Use): Automotive Veh, Import Price Index (End Use): Passenger Cars, Import Price Index (End Use): Automotive Par, Import Price Index (End Use): Consumer Goods, Import Price Index (End Use): Nondurables, M, Import Price Index (End Use): Apparel, House, Import Price Index (End Use): Apparel, Texti, Import Price Index (End Use): Durables, Manu, Import Price Index (End Use): Furniture, Hou, Total Business: Inventories to Sales Ratio, Manufacturing employment, Capacity utilization: manufacturing, Manufacturers: Inventories to Sales Ratio, 30-Year Fixed Rate Mortgage Average, Current Employment, New Orders: Nondefense Capital Goods Excludi, Current New Orders, Current New Orders, Global Price Index of All Commodities, Global aluminum price, Coal, Australia, Global copper price, Producer Price Index by Industry: Electric P, Producer Price Index by Industry: Electric P, Producer Price Index by Industry: Deep Sea F, Producer Price Index by Industry: Deep Sea F, Producer Price Index by Industry: Deep Sea F, Truck Transportation, Producer Price Index by Industry: Couriers a, Total Manufacturing Industries, Authorized in Permit-Issuing Places: Total U, Authorized in Permit-Issuing Places: Single-, New Privately-Owned Housing Units Authorized, New Privately-Owned Housing Units Authorized, New Privately-Owned Housing Units Authorized, New Privately-Owned Housing Units Authorized, New Privately-Owned Housing Units Authorized, New Privately-Owned Housing Units Authorized, Global price of Food index, Global price of Industrial Materials index, Global lead price, Global price of Metal index, Natural Gas, US Henry Hub Gas, Global nickel price, Global price of Energy index, Brent Crude, WTI Crude, Current Prices Paid, Current Prices Paid, Future Prices Paid, Future Prices Paid, Producer Price Index by Commodity: Metals an, Global price of Agr. Raw Material Index, Current Prices Received, Future Prices Received, Rubber, Global tin price, Global zinc price, Retailers: Inventories to Sales Ratio, 10-Year Breakeven Inflation Rate, 5-Year Breakeven Inflation Rate, 5-Year, 5-Year Forward Inflation Expectation, 3-Month Treasury Bill Secondary Market Rate,, Residential, Total Construction, Current Unfilled Orders; Diffusion Index for, Current Unfilled Orders, Current Unfilled Orders; Percent Reporting D, Current Unfilled Orders; Percent Reporting D, Current Unfilled Orders; Percent Reporting I, Current Unfilled Orders; Percent Reporting I, Construction, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Fuels and Related Products and Power: Coal, Fuels and Related Products and Power: Anthra, Fuels and Related Products and Power: Bitumi, Fuels and Related Products and Power: Coal, Fuels and Related Products and Power: Gas Fu, Natural gas PPI, Fuels and Related Products and Power: Natura, Electric power PPI, Fuels and Related Products and Power: Reside, Producer Price Index by Commodity: Fuels and, Producer Price Index by Commodity: Fuels and, Fuels and Related Products and Power: Utilit, Fuels and Related Products and Power: Crude, Refined petroleum products PPI, Finished lubricants PPI, Chemicals and Allied Products, Chemicals and Allied Products: Industrial Ch, Chemicals and Allied Products: Basic Inorgan, Chemicals and Allied Products: Basic Organic, Chemicals and Allied Products: Paints and Al, Chemicals and Allied Products: Prepared Pain, Chemicals and Allied Products: Paint Materia, Chemicals and Allied Products: Fats and Oils, Chemicals and Allied Products: Agricultural, Chemicals and Allied Products: Plastic Resin, Chemicals and Allied Products: Other Chemica, Rubber and Plastic Products, Rubber and Plastic Products: Rubber and Rubb, Rubber and Plastic Products: Synthetic Rubbe, Rubber and Plastic Products: Tires, Tubes, T, Rubber and Plastic Products: Miscellaneous R, Plastic products PPI, Rubber and Plastic Products: Plastic Constru, Rubber and Plastic Products: Unsupported Pla, Rubber and Plastic Products: Laminated Plast, Metals and Metal Products, Iron & steel PPI, Iron ores PPI, Iron & steel scrap PPI, Metals and Metal Products: Foundry and Forge, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity: Metals an, Producer Price Index by Commodity for Metals, Steel mill products PPI, Steel wire PPI, Cold-rolled steel sheet (GOES proxy), Metals and Metal Products: Nonferrous Metals, Metals and Metal Products: Nonferrous Metal, Metals and Metal Products: Primary Nonferrou, Metals and Metal Products: Nonferrous Scrap, Metals and Metal Products: Secondary Nonferr, Metals and Metal Products: Nonferrous Mill S, Aluminum mill shapes PPI, Nonferrous wire & cable PPI, Metals and Metal Products: Nonferrous Foundr, Metals and Metal Products: Metal Containers, Metals and Metal Products: Metal Cans and Ca, Metals and Metal Products: Barrels, Drums, P, Metals and Metal Products: Hardware, Metals and Metal Products: Hardware, Not Els, Metals and Metal Products: Hand and Edge Too, Metals and Metal Products: Plumbing Fixtures, Metals and Metal Products: Vitreous China Pl, Metals and Metal Products: Heating Equipment, Metals and Metal Products: Fabricated Struct, Metals and Metal Products: Miscellaneous Met, Machinery and Equipment, Machinery and Equipment: Agricultural Machin, Machinery and Equipment: Agricultural Machin, Machinery and Equipment: Construction Machin, Machinery and Equipment: Tractors and Attach, Machinery and Equipment: Power Cranes, Dragl, Machinery and Equipment: Mixers, Pavers, and, Machinery and Equipment: Off-Highway, Equipm, Machinery and Equipment: Miscellaneous Const, Machinery and Equipment: Parts for Construct, Machinery and Equipment: Metalworking Machin, Machinery and Equipment: General Purpose Mac, Machinery and Equipment: Electronic Computer, Machinery and Equipment: Special Industry Ma, Electrical machinery & equip. PPI, Machinery and Equipment: Miscellaneous Instr, Machinery and Equipment: Miscellaneous Machi, Transportation Services: Truck Transportatio, Copper PPI, WTI crude oil
- **Cluster 2:** Capacity Utilization: Utilities: Electric an, Capacity Utilization: Utilities: Electric Po, Industrial Production: Utilities: Electric a, Industrial production: utilities
- **Cluster 3:** Manufacturing, Nonresidential
- **Cluster 4:** Moody's Seasoned Aaa Corporate Bond Minus Fe, Moody's Seasoned Baa Corporate Bond Minus Fe, 10-Year Treasury Constant Maturity Minus 2-Y, 10-Year Treasury Constant Maturity Minus 2-Y, 10-Year Treasury Constant Maturity Minus 3-M, 10-Year Treasury Constant Maturity Minus Fed, 1-Year Treasury Constant Maturity Minus Fede, 5-Year Treasury Constant Maturity Minus Fede, 3-Month Treasury Bill Minus Federal Funds Ra, 6-Month Treasury Bill Minus Federal Funds Ra
- **Cluster 5:** Aaa Corporate Bond Yield Relative to Yield o, Moody's Seasoned Aaa Corporate Bond Yield Re, Baa Corporate Bond Yield Relative to Yield o, Moody's Seasoned Baa Corporate Bond Yield Re
- **Cluster 6:** Future Work Hours; Diffusion Index for Feder, Future Work Hours; Diffusion Index for Feder, Future Work Hours; Percent Reporting Decreas, Future Work Hours; Percent Reporting Decreas, Future Work Hours; Percent Reporting Increas, Future Work Hours; Percent Reporting Increas, Future General Activity; Diffusion Index for, Future General Activity, Future General Activity; Percent Reporting D, Future General Activity; Percent Reporting D, Future General Activity; Percent Reporting I, Future General Activity; Percent Reporting I, Future New Orders, Future Unfilled Orders; Diffusion Index for, Future Unfilled Orders; Diffusion Index for, Future Unfilled Orders; Percent Reporting De, Future Unfilled Orders; Percent Reporting De, Future Unfilled Orders; Percent Reporting In, Future Unfilled Orders; Percent Reporting In
- **Cluster 7:** Future Capital Expenditures; Diffusion Index, Future Capital Expenditures, Future Capital Expenditures; Percent Reporti, Future Capital Expenditures; Percent Reporti, Future Capital Expenditures; Percent Reporti, Future Capital Expenditures; Percent Reporti
- **Cluster 8:** Energy, Total, Mining: Mining (NAICS = 21)
- **Cluster 9:** Producer Price Index by Industry: Pipeline T, Producer Price Index by Industry: Pipeline T, Producer Price Index by Industry: Pipeline T, Producer Price Index by Industry: Pipeline T
- **Cluster 10:** Producer Price Index by Industry: Refined Pe, Producer Price Index by Industry: Refined Pe, Producer Price Index by Industry: Refined Pe
- **Cluster 11:** Producer Price Index by Industry: Scheduled, Producer Price Index by Industry: Scheduled
- **Cluster 12:** Producer Price Index by Industry: Scheduled, Producer Price Index by Industry: Scheduled, Producer Price Index by Industry: Scheduled
- **Cluster 13:** Current Unfilled Orders; Percent Reporting N, Current Unfilled Orders; Percent Reporting N
- **Cluster 14:** Future Unfilled Orders; Percent Reporting No, Future Unfilled Orders; Percent Reporting No
- **Cluster 15:** Future Work Hours; Percent Reporting No Chan, Future Work Hours; Percent Reporting No Chan
- **Cluster 16:** Future Capital Expenditures; Percent Reporti, Future Capital Expenditures; Percent Reporti
- **Cluster 17:** Future General Activity; Percent Reporting N, Future General Activity; Percent Reporting N
- **Cluster 18:** Future Employment; Diffusion Index for Feder, Future Employment; Diffusion Index for Feder, Future Employment; Percent Reporting Decreas, Future Employment; Percent Reporting Decreas
- **Cluster 19:** Current Work Hours; Percent Reporting No Cha, Current Work Hours; Percent Reporting No Cha
- **Cluster 20:** Industrial Production: Durable Goods Materia, Industrial Production: Durable Goods Materia
- **Cluster 21:** Industrial Capacity: Utilities: Electric and, Industrial Capacity: Utilities: Electric Pow
- **Cluster 22:** Industrial Capacity: Manufacturing Excluding, Industrial Capacity: Total Excluding Compute
- **Cluster 23:** Industrial Production: Durable Consumer Good, Industrial Production: Durable Consumer Good
