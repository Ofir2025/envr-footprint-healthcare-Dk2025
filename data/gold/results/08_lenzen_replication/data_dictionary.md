# 08_lenzen_replication - data dictionary

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

### `lenzen_expenditure_base_check.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `quantity` | dimension | str |  | Danish health expenditure, this study |
| `value` | measure | float64 | varies by row | 302.025275 |
| `unit` | dimension | str |  | bn DKK current prices |
| `source` | dimension | str |  | Statistics Denmark IO tables, health + e |

### `lenzen_kpi_by_producing_node.csv.gz`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `quantity` | dimension | str |  | Lenzen KPI, supply-chain component by pr |
| `producing_country_iso3` | dimension | str |  | RUS |
| `producing_country_name` | dimension | str |  | Russia |
| `producing_world_region` | dimension | str |  | Europe |
| `producing_sector_code` | dimension | str |  | COIL |
| `producing_sector_name` | dimension | str |  | Extraction of crude petroleum and servic |
| `producing_sector_group` | dimension | str |  | Coal and Petroleum |
| `value` | measure | float64 | kt CO2eq | 100.6514597829438 |

### `lenzen_kpi_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 4.432603751212643 |
| `share_of_total_pct` | measure | float64 | % | 4.652613984138589 |

### `lenzen_kpi_set.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `consuming_country_iso3` | dimension | str |  | DNK |
| `analysis_year` | measure | int64 |  | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `total` | measure | float64 | varies by row | 4025.0002397773846 |
| `direct` | measure | float64 | varies by row | 353.33928659046666 |
| `supplier_first_order` | measure | float64 | varies by row | 1114.9707785732494 |
| `higher_order` | measure | float64 | varies by row | 2556.6901746136687 |
| `direct_pct` | measure | float64 | % | 8.77861529295236 |
| `supplier_pct` | measure | float64 | % | 27.70113570564449 |
| `higher_order_pct` | measure | float64 | % | 63.52024900140315 |
| `truncation_error_TE0_pct` | measure | float64 | % | 91.22138470704763 |
| `truncation_error_TE1_pct` | measure | float64 | % | 63.52024900140315 |
| `per_capita` | measure | float64 | varies by row | 685.2907232544896 |
| `national_total` | measure | float64 | varies by row | 67518.62638160589 |
| `share_of_national_pct` | measure | float64 | % | 5.96131831389555 |
| `intensity_per_meur` | measure | float64 | varies by row | 0.0991453175031388 |
| `domestic_pct` | measure | float64 | % | 17.511612231334944 |
| `import_pct` | measure | float64 | % | 82.48838776866506 |
| `lenzen_dk_2015` | measure | float64 | varies by row | 3370.0 |
| `lenzen_unit` | dimension | str |  | kt CO2eq |
| `lenzen_note` | dimension | str |  | SI Tab. 10.1/10.2/10.3/10.4; SI Tab. 7.1 |
| `population` | measure | int64 | varies by row | 5873420 |
| `health_expenditure_meur` | measure | float64 | varies by row | 40596.97766008925 |
