# Netherlands reference inputs

The Dutch side of the study. Steenmeijer et al. (2022) measured the
environmental footprint of Dutch healthcare; this study replicates their method
for Denmark, so their inputs are kept as the reference the Danish run is
compared against and, for the bottom-up items Denmark has no measurement for, as
the base that is scaled.

| item | value |
|:---|:---|
| Provider | Statistics Netherlands (CBS); Steenmeijer et al. |
| Dataset | CBS national supply-use tables 2015-2018; CBS health-expenditure statistics (StatLine, Zorgrekeningen); the bottom-up inventory published with Steenmeijer et al. |
| Citation | Steenmeijer, Rodrigues, Zijp & Waaijers-van der Loop (2022), *Lancet Planet Health* 6:e949-e959, doi `10.1016/S2542-5196(22)00244-3` |
| Licence | CBS open data, free reuse with attribution; the bottom-up inventory under the article's own terms |
| Retrieved | inherited with the upstream Netherlands repository, 2022-08-24 (`ee3f015`); the `nl_` prefixes and `ISO2` columns were added 2026-09 |

## Files

| file | size | shape | unit |
|:---|:---|:---|:---|
| `nl_supply_tables_2015_2018.xlsx` | 255 kB | 8 sheets, 103 × 91 each | M.EUR |
| `nl_cbs_data_2016.csv` | 190 B | 3 rows × 6 columns | see `Unit` column |
| `nl_bottomup_data.txt` | 466 B | 8 rows × 7 columns, tab-separated | see column names |

## Column dictionaries

### `nl_supply_tables_2015_2018.xlsx`

CBS supply tables at current and previous-year prices, one sheet per year and
price basis: `Supply 2015 current prices`, `Supply 2016 current prices`,
`Supply 2016 PY prices`, and the same for 2017 and 2018, plus `Explanation`.
`analysis.functions_2025.get_cbsdata` reads **`Supply 2016 current prices`**
only, with `skiprows=1`, `header=[0]`, `index_col=[1]`, `nrows=98`, and takes two
columns — `Supply at basic prices (columns 82-85)` and `Total` — whose quotient
is the purchaser-to-basic price conversion for four product groups: basic
pharmaceutical products, computer and electronic products, human health
services, and residential care and social work services.

This is the file whose absence the `analysis.main` guard used to report. It was
present all along under the name `supply_tables_2015_2018.xlsx`, one directory
up, without the `nl_` prefix its reader builds. The rename fixed that.

### `nl_cbs_data_2016.csv`

The Dutch expenditure and direct-emission frame, the exact shape
`functions_2025.createBackground` consumes.

| column | meaning |
|:---|:---|
| `Index` | row name: `Expenditure`, `Conversion` or `DirectEm` |
| `Unit` | `MEUR`, `na`, `kt CO2e` respectively |
| `HC service` | healthcare services |
| `Pharm` | pharmaceuticals |
| `MedAppl` | medical appliances |
| `ISO2` | country of the row; `NL` throughout |

Values: expenditure 86,096 / 5,639 / 3,107 M.EUR; conversions 0.9961 / 0.6726 /
0.8494; direct emissions 1,699 / 0 / 0 kt CO2-eq.

### `nl_bottomup_data.txt`

The Dutch bottom-up inventory: the impact items that sit outside the
input-output model. Tab-separated, eight rows.

| column | unit |
|:---|:---|
| `Source` | row name: `Anaesthetic`, `pMDI`, `Commute (total/direct/indirect)`, `Visitor travel (total/direct/indirect)` |
| `Global warming (ktCO2eq)` | kt CO2-eq |
| `Material extraction (kt)` | kt |
| `Blue water consumption (Mm3)` | Mm³ |
| `Land use (km2)` | km² |
| `Waste generation (kt)` | kt |
| `ISO2` | country of the row; `NL` throughout |

The `(total)` rows are the sum of their `(direct)` and `(indirect)` rows;
`analysis.main_2025` recomputes them after scaling rather than scaling them
directly.

**Caveat: this file is a base, not a result.** `analysis.main_2025` reads it,
applies the Danish scaling factors and the Danish primary values, and writes
`data/silver/netherlands_reference/dk_bottomup_data_<year>.txt`. Nothing downstream reads the
Dutch file. Two pre-`ISO2` copies of it and of `nl_cbs_data_2016.csv` used to sit
beside them in the bronze root; they were removed, and the reasons are in
`../readme.md`.

**Caveat: the Dutch anaesthetic and pMDI values are superseded for Denmark.**
The 14.2 kt and 76.9 kt of this file are Dutch measurements. Denmark's are
11.6 kt from the medicines register and 11.6 kt from the Danish EPA F-gas
inventory; the Dutch rows survive only to carry the (all-zero) non-climate
columns.
