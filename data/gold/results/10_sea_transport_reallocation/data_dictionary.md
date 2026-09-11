# 10_sea_transport_reallocation - data dictionary

One row per column of every table in this folder. Units are the
table's own; `varies by row` means the table carries a `unit`
column and the value is read from there.

## Common columns

Every gold table shares this vocabulary; columns particular to one table
are described below, per table.

| Column | Meaning |
|:---|:---|
| `analysis_year` | year of the Danish expenditure data and of the MRIO background |
| `model` | MRIO release actually used (e.g. `EXIOBASE v3.8.2 IOT_2022_ixi with Danish sea-transport reallocation (Rørmose Jensen & Iliev 2022)`) - **not** v3.10.2, which this study rejects (see `docs/methods/exiobase_release_and_classification.md`) |
| `scenario` | model scenario (`baseline`, scope variants, pharma-mapping variants) |
| `consuming_country_iso3` | always `DNK` - Denmark is the final consumer in this study |
| `demand_component` | `healthcare_services`, `pharmaceuticals`, `medical_appliances` |
| `indicator` | `climate_change`, `material_extraction`, `blue_water_consumption`, `land_use`, `waste_generation` |
| `unit` | `kt CO2eq`, `kt`, `Mm3`, `km2`, or `M.EUR` for monetary rows |
| `value` | numeric value in `unit` |

## Country and region coding

`*_country_iso3` uses **ISO 3166-1 alpha-3** for the 44 EXIOBASE countries.
The five rest-of-world regions are **not countries** and keep their own
codes and names: `WA` RoW Asia and Pacific, `WL` RoW America, `WE` RoW
Europe, `WF` RoW Africa, `WM` RoW Middle East. `*_world_region` gives the
continental grouping (Europe, Asia and Pacific, America, Middle East,
Africa, Denmark).

## The two perspectives (and why they reconcile)

Every impact cell is $E_{ij} = s_i\,L_{ij}\,y_{H,j}$: pressure arising
in node *i* caused by Danish healthcare final demand for node *j*. Summing
over *i* gives the **consumption / contribution** perspective (by
purchased product); summing over *j* gives the **production / hotspot**
perspective (by producing node). Both are marginals of the same array, so
they sum to the identical total - verified to machine precision by
`analysis.validate_io_identities` (tests T5/T6). Allocating production
emissions to final demand is additive and does not double count (Wood et
al. 2018); embodied-flow tables ($\mathbf{E}_Z$) would.

## Units

Monetary values are **million euro (M.EUR)** - EXIOBASE's native unit
(`unit.txt` of the release). No US-dollar values are used anywhere in this
model; dollar figures appearing in the comparative literature (Karliner et
al. 2019, Lenzen et al. 2020, Pichler et al. 2019) are those studies' own
units and are labelled as such wherever they are quoted.

## Tables

### `phantom_shipping_input_removed_by_industry.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_producing` | dimension | str |  | DNK |
| `sector_producing` | dimension | str |  | Sea and coastal water transport |
| `background_year` | dimension | str |  | 2016 |
| `analysis_year` | measure | int64 |  | 2019 |
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | Sea and coastal water transport |
| `value` | measure | float64 | M.EUR | 4596.613524817225 |
| `unit` | dimension | str |  | M.EUR |

### `phi_sensitivity_2016.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `phi` | measure | float64 |  | 0.05 |
| `phi_source` | dimension | str |  | sensitivity grid |
| `released_meur` | measure | float64 |  | 10573.158181268676 |
| `footprint_climate_kt` | measure | float64 |  | 3989.812886834499 |
| `transport_share_pct` | measure | float64 | % | 18.490275073503412 |
| `background_year` | measure | int64 |  | 2016 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi |

### `phi_sensitivity_2022.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `phi` | measure | float64 |  | 0.05 |
| `phi_source` | dimension | str |  | sensitivity grid |
| `released_meur` | measure | float64 |  | 12221.956251977515 |
| `footprint_climate_kt` | measure | float64 |  | 4653.5712732386055 |
| `transport_share_pct` | measure | float64 | % | 11.800811132913516 |
| `background_year` | measure | int64 |  | 2022 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi |

### `shipping_reallocation_diagnostics.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_producing` | dimension | str |  | DNK |
| `sector_producing` | dimension | str |  | Sea and coastal water transport |
| `background_year` | dimension | str |  | 2016 |
| `analysis_year` | measure | int64 |  | 2019 |
| `quantity` | dimension | str |  | DK sea transport total output |
| `value` | measure | float64 | varies by row | 15432.100020195892 |
| `unit` | dimension | str |  | M.EUR |
| `source` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi |
| `phi_applied` | measure | float64 |  | 0.0773547579047825 |
| `phi_source` | dimension | str |  | DST DIO 2016 |
| `rormose_2019_cross_check` | measure | float64 |  | 0.0931189507920632 |
