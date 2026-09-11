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
| `dk_data_2025.csv` | `dk_umat_2019.xlsx` (2019) or `input_output_en_2022.xlsx` (2022), plus `dk_direct_emissions_drivhus.csv` | healthcare totals summed over the boundary's purpose × transaction cells, converted 1000 DKK → M.EUR at the year's Nationalbank average, `Conversion` set to 1.0, `DirectEm` built from DRIVHUS less hospital N2O | 3 × 6 | `HC_ANALYSIS_YEAR=<year> HC_BACKGROUND_TAG=_snacship PYTHONPATH=src .venv/bin/python -m analysis.main_2025` |
| `dk_expenditure_breakdown_2019.csv` | `dk_umat_2019.xlsx`, sheet `Ubas` | every (purpose × transaction) cell that entered the 2019 totals, kept unaggregated as a provenance record | 14 × 5 | the same, with `HC_ANALYSIS_YEAR=2019` |
| `dk_expenditure_breakdown_2022.csv` | `input_output_en_2022.xlsx`, sheets `CP` and `IO` | the same for 2022, with the sheet each cell came from | 15 × 6 | the same, with `HC_ANALYSIS_YEAR=2022` |
| `dk_health_expenditure_frame.csv` | all three bronze sources above, both years | the `dk_data_2025.csv` frame rebuilt for **both** analysis years in one pass, so a consumer can select a year instead of inheriting whichever ran last | 6 × 6 | `PYTHONPATH=src .venv/bin/python -m analysis.build_shipping_inputs` |

## Columns

### `dk_data_2025.csv`

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

The same three-row frame as `dk_data_2025.csv`, once per analysis year.

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

## Known defect

`dk_data_2025.csv` is **one file for every analysis year**, overwritten on every
run, and the `2025` in its name is an edition marker rather than a year of data.
A 2019 run leaves 2019 values in the file a 2022 run then reads. The two
breakdowns beside it are year-scoped and `dk_health_expenditure_frame.csv` carries
both years, so no value is lost — what is missing is the file itself saying which
year it holds. `analysis.dk_shipping_correction` already reads the frame table
rather than this file for exactly that reason.
