# Statistics Denmark capital accounts for the health industries

Gross fixed capital formation by asset type for the two Danish health
industries, used by `analysis.capital_gfcf` to scale the endogenised capital
term to the Danish healthcare boundary.

| item | value |
|:---|:---|
| Provider | Statistics Denmark |
| Dataset | StatBank table **NABK69**, "Capital stock by industry (69-grouping), type of asset, price unit and time" |
| URL | <https://www.statbank.dk/NABK69> — API endpoint <https://api.statbank.dk/v1/data>, no key required |
| Licence | Statistics Denmark open data; free reuse with attribution |
| Retrieved | 2026-09-07 |

## Query

StatBank table `NABK69`, delimiter-separated download with variable labels, for:

| variable | selection |
|:---|:---|
| `BEHOLD` | `P.51g` Gross fixed capital formation |
| `AKTIV` | all asset types |
| `BRANCHE` | `86000` Human health activities, `87880` Residential care |
| `PRISENHED` | Current prices |
| `TID` | `2022` |

The download is semicolon-separated, UTF-8 with a byte-order mark, and English
labels. Keep the published column names; `analysis.capital_gfcf` reads them as
they come.

| file | size | shape | unit |
|:---|:---|:---|:---|
| `nabk69_health_assets_2022.csv` | 3.4 kB | 28 rows × 6 columns | million DKK, current prices |

## Column dictionary

| column | meaning |
|:---|:---|
| `BEHOLD` | account item; `P.51g Gross fixed capital formation` throughout |
| `AKTIV` | asset type: dwellings, buildings other than dwellings, other structures and land improvements, transport equipment, ICT equipment and other machinery, cultivated biological resources, intellectual property products, and the total |
| `BRANCHE` | DB07 industry, `86000 Human health activities` or `87880 Residential care` |
| `PRISENHED` | price unit; `Current prices` throughout |
| `TID` | reference year; `2022` throughout |
| `INDHOLD` | the value, million DKK |

**Caveat.** The 69-grouping is coarser than the 117-grouping used everywhere
else in this study: `86000` and `87880` here correspond to the 117-grouping's
`860010`, `860020` and `870000`/`880000` split, so the eldercare share has to be
applied outside this table.

**How it nearly went missing.** This file was untracked for its whole life. The
author's global excludes file drops `*.csv`, and the repository `.gitignore`
un-ignored only `data/bronze/*.csv` — the root, not the subfolders. It sat on
one machine's disk, read by `analysis.capital_gfcf`, invisible to every clone
and every audit. The un-ignore rule now reads `data/bronze/**/*.csv`.
