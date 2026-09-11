# Silver: Danish healthcare expenditure

Mirrors `data/bronze/dst_supply_use/`. Four files: the frame the background model
consumes, the column-by-column record of how its expenditure totals were
assembled, and the two-year table that lets a downstream module read either
year's frame without rerunning the pipeline.

| item | value |
|:---|:---|
| Bronze sources | `data/bronze/dst_supply_use/dk_umat_2019.xlsx` (the detailed supply-use table, dominant source); `data/bronze/dst_input_output/input_output_en_2022.xlsx` for the 2022 expenditure route; `data/bronze/dst_emission_accounts/dk_direct_emissions_drivhus.csv` for the direct-emission row |
| Produced by | `analysis.main_2025` (the first two files), `analysis.build_shipping_inputs` (the frame table) |
| In version control | the frame and both breakdowns are **tracked**; `dk_health_expenditure_frame.csv` is not |

These files derive from three bronze folders and sit under `dst_supply_use/`
because that is the dominant one: the expenditure boundary is defined on the
detailed supply-use table's purpose-by-transaction grid, and the 2022 route and
the DRIVHUS row are the same boundary evaluated on two other Statistics Denmark
publications.

## Files

| file | derives from | transformation | rows × cols | rebuild |
|:---|:---|:---|:---|:---|
| `dk_data_2016.csv` | `input_output_en_2016.xlsx`, sheets `CP` and `IO`, plus `dk_direct_emissions_drivhus.csv` | the same as 2022: the published 117-industry workbook rather than the detailed supply-use table, so the 2016 vector needs no confidential extract | 3 × 6 | the same, with `HC_ANALYSIS_YEAR=2016` |
| `dk_expenditure_breakdown_2016.csv` | `input_output_en_2016.xlsx`, sheets `CP` and `IO` | every (purpose × transaction) cell that entered the 2016 totals | 15 × 6 | the same, with `HC_ANALYSIS_YEAR=2016` |
| `dk_data_2019.csv` | `dk_umat_2019.xlsx`, sheet `Ubas`, plus `dk_direct_emissions_drivhus.csv` | healthcare totals summed over the boundary's purpose × transaction cells, converted 1000 DKK → M.EUR at the year's Nationalbank average, `Conversion` set to 1.0, `DirectEm` built from DRIVHUS less hospital N2O | 3 × 6 | `HC_ANALYSIS_YEAR=2019 HC_BACKGROUND_TAG=_snacship PYTHONPATH=src .venv/bin/python -m analysis.main_2025` |
| `dk_data_2022.csv` | `input_output_en_2022.xlsx`, sheets `CP` and `IO`, plus `dk_direct_emissions_drivhus.csv` | the same | 3 × 6 | the same, with `HC_ANALYSIS_YEAR=2022` |
| `dk_expenditure_breakdown_2019.csv` | `dk_umat_2019.xlsx`, sheet `Ubas` | every (purpose × transaction) cell that entered the 2019 totals, kept unaggregated as a provenance record | 14 × 5 | the same, with `HC_ANALYSIS_YEAR=2019` |
| `dk_expenditure_breakdown_2022.csv` | `input_output_en_2022.xlsx`, sheets `CP` and `IO` | the same for 2022, with the sheet each cell came from | 15 × 6 | the same, with `HC_ANALYSIS_YEAR=2022` |
| `dk_health_expenditure_frame.csv` | all three bronze sources above, both years | the `dk_data_<year>.csv` frame rebuilt for **both** analysis years in one pass, so a consumer can select a year from one file instead of choosing which file to open | 6 × 6 | `PYTHONPATH=src .venv/bin/python -m analysis.build_shipping_inputs` |

## Columns

### `dk_data_2019.csv`, `dk_data_2022.csv`

The shape `functions_2025.createBackground` consumes, read positionally, so the
row order matters: `Expenditure`, `Conversion`, `DirectEm`.

| column | unit | meaning |
|:---|:---|:---|
| `Index` | — | row name: `Expenditure`, `Conversion` or `DirectEm` |
| `Unit` | — | `MEUR`, `na`, `kt CO2e` respectively |
| `HC service` | see `Unit` | healthcare services, the boundary's service component |
| `Pharm` | see `Unit` | pharmaceuticals, HC.5.1 |
| `MedAppl` | see `Unit` | medical appliances, HC.5.2 |
| `ISO2` | — | country of the row; `DK` throughout |

`Conversion` is 1.0 for all three columns because both Danish expenditure routes
are already at **basic** prices, matching EXIOBASE's valuation: the 2019 route
reads sheet `Ubas` of the detailed use table, and the 2022 route sums only the
industry-coded basic-price rows of the public workbook, excluding its separate
product-tax and VAT rows. The Dutch reference frame in
`data/bronze/netherlands_reference/nl_cbs_data_2016.csv` carries real
purchaser-to-basic conversions instead; that difference is the reason the row
exists at all.

`DirectEm` is Statistics Denmark's DRIVHUS greenhouse-gas account for the
boundary's industries — human health (QA) plus residential care (870000) plus the
eldercare share of social work without accommodation (880000) — **less** hospital
N2O, which is removed because anaesthetic gases enter separately as the bottom-up
item `B_ANAE`.

### `dk_expenditure_breakdown_<year>.csv`

| column | unit | meaning |
|:---|:---|:---|
| `category` | — | which component the cell feeds: `HC.5.1 Pharmaceuticals`, `HC.5.2 Appliances`, `Healthcare services` |
| `purpose_code` | code | five-digit Danish consumption-purpose code, e.g. `06112`, `12401` |
| `purpose` | — | its published name |
| `transaction` | — | national-accounts transaction, e.g. `Household consumption (Transaction code 3110)`, `Non-market individual government consumption (Transaction code 3142)` |
| `source_sheet` | — | **2022 only**: `CP` or `IO`, the workbook sheet the cell was read from |
| `value_kdkk` | 1000 DKK | the cell value, before currency conversion |

The two years do not share a purpose vocabulary and are not meant to: Denmark
renumbered its consumption purposes between them, so 2019's `06130` therapeutic
appliances is 2022's `06134`, and 2019's `12401` retirement homes is 2022's
`13302`. The breakdown is what makes that visible instead of leaving the
difference inside one aggregate.

### `dk_health_expenditure_frame.csv`

The same three-row frame as `dk_data_<year>.csv`, both years in one file.

| column | unit | meaning |
|:---|:---|:---|
| `analysis_year` | year | `2019` or `2022`; selects the block |
| `Index` | — | `Expenditure`, `Conversion`, `DirectEm` |
| `Unit` | — | `MEUR`, `na`, `kt CO2e` respectively |
| `HC service` | see `Unit` | healthcare services |
| `Pharm` | see `Unit` | pharmaceuticals |
| `MedAppl` | see `Unit` | medical appliances |

Read it with `float_precision="round_trip"`: these values enter a Leontief
inversion, so the last bit of the float is a published number.

## Fixed defect: the year scope

There used to be one `dk_data_2025.csv` for every analysis year, overwritten on
every run, with `2025` an edition marker rather than a year of data: a 2019 run
left 2019 values in the file a 2022 run then read. The file is now year-scoped,
and `paths.silver_dk_data_csv` is a function of the year rather than a constant,
so a reader cannot resolve the path without saying which year it wants.

The 2019 file was seeded from the 2019 block of
`dk_health_expenditure_frame.csv`, which had carried both years all along, and a
2019 run then reproduced it byte for byte — so the split recovered the values
rather than inventing them.

## Why the year is in the name and the care boundary is not

The year is in the name because a file can hold either year's values: a 2019 run
and a 2022 run both write, so a shared name is overwritten and read for the
wrong year. That happened, and it is the fixed defect above.

The care boundary is **not** in the name, and this is a decision rather than an
omission. `analysis.main_2025` writes `dk_data_<year>.csv` and
`dk_expenditure_breakdown_<year>.csv` **only** for `HC_SCOPE=health_eldercare`
and skips the write on every other boundary, so these files have exactly one
possible boundary. A suffix would distinguish nothing: there is no second file
for it to be distinguished from, and a `_health_eldercare` on every name would
state a constant.

What a suffix could not have prevented either is the one thing that could go
wrong here — a module running on another boundary opening the file anyway and
publishing the manuscript boundary's expenditure as that boundary's own. A
suffix does not stop a reader from typing it. So that is enforced at the read
instead, by `analysis.constants.require_manuscript_boundary`, which every
reader of these two files calls first: `analysis.export_tables`,
`analysis.lenzen_replication`, `analysis.malik_replication`,
`analysis.waste_validation` and `analysis.waste_domestic_dst`. On any boundary
but the manuscript's they stop, and say which boundary they are on and which
file they refused to read.

`dk_bottomup_data_<year>.txt` is a third case and needs neither the suffix nor
the guard: it is written on every boundary, and it is boundary-INVARIANT.
Anaesthetic gases, pMDI propellants, commuting and patient travel are Danish
primary totals scaled from the Dutch baseline, and none of the four scaling
inputs is a function of the care boundary. Measured rather than assumed: a
`zorg_en_welzijn` run on 11 September 2026 rewrote the file and left it
byte-identical, and the three bottom-up rows of `table_01.csv` are equal to the
last digit in `01_eriksen_replication/2019c` and `01_eriksen_replication/2019d`.
