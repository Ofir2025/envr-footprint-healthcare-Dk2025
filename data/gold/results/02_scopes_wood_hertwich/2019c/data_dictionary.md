# 02_scopes_wood_hertwich/2019c - data dictionary

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

### `double_counting_ledger.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `analysis_year` | measure | int64 |  | 2019 |
| `item` | dimension | str |  | MRIO footprint decomposition by producin |
| `risk` | dimension | str |  | none |
| `test` | dimension | str |  | partition of one scalar (sum of cells == |
| `value` | measure | float64 | varies by row | 3257.1574428588515 |
| `unit` | dimension | str |  | kt CO2eq |
| `verdict` | dimension | str |  | OK - additive by construction (Wood & He |

### `scope_by_continent.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_world_region` | dimension | str |  | Denmark |
| `scope` | dimension | str |  | Outside protocol |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `value` | measure | float64 | varies by row | 0.0709 |
| `share_of_scope_pct` | measure | float64 | % | 100.0 |

### `scope_by_continent_and_industry_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_world_region` | dimension | str |  | Denmark |
| `producing_sector_group` | dimension | str |  | Private travel |
| `scope` | dimension | str |  | Outside protocol |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `value` | measure | float64 | varies by row | 0.0709 |
| `share_of_scope_pct` | measure | float64 | % | 100.0 |

### `scope_by_country.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_country_iso3` | dimension | str |  | DNK |
| `producing_country_name` | dimension | str |  | Denmark |
| `producing_world_region` | dimension | str |  | Denmark |
| `scope` | dimension | str |  | Outside protocol |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `value` | measure | float64 | varies by row | 0.0709 |
| `share_of_scope_pct` | measure | float64 | % | 100.0 |

### `scope_by_industry_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_sector_group` | dimension | str |  | Private travel |
| `scope` | dimension | str |  | Outside protocol |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `value` | measure | float64 | varies by row | 0.0709 |
| `share_of_scope_pct` | measure | float64 | % | 100.0 |

### `scope_by_origin_and_industry.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi with Danish |
| `analysis_year` | measure | int64 |  | 2019 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `scope` | dimension | str |  | Scope 2 |
| `producing_country_iso3` | dimension | str |  | AUT |
| `producing_country_name` | dimension | str |  | Austria |
| `producing_world_region` | dimension | str |  | Europe |
| `producing_sector_code` | dimension | str |  | POWC |
| `producing_sector_name` | dimension | str |  | Production of electricity by coal |
| `producing_sector_group` | dimension | str |  | Electricity |
| `value` | measure | float64 | kt CO2eq | 0.0069994014960735 |
| `component_type` | dimension | str |  | MRIO supply-chain node |

### `scope_by_origin_industry_top25.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_country_iso3` | dimension | str |  | DNK |
| `producing_country_name` | dimension | str |  | Denmark |
| `producing_world_region` | dimension | str |  | Denmark |
| `producing_sector_code` | dimension | str |  | BU_TRAVEL |
| `producing_sector_name` | dimension | str |  | Bottom-up: patient and visitor travel |
| `producing_sector_group` | dimension | str |  | Private travel |
| `scope` | dimension | str |  | Outside protocol |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `value` | measure | float64 | varies by row | 0.0709 |
| `rank` | measure | int64 |  | 2 |
| `is_remainder` | dimension | bool |  | False |

### `scopes_by_producing_node.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi with Danish |
| `analysis_year` | measure | int64 |  | 2019 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `scope` | dimension | str |  | Scope 2 |
| `producing_country_iso3` | dimension | str |  | AUT |
| `producing_country_name` | dimension | str |  | Austria |
| `producing_world_region` | dimension | str |  | Europe |
| `producing_sector_code` | dimension | str |  | POWC |
| `producing_sector_name` | dimension | str |  | Production of electricity by coal |
| `producing_sector_group` | dimension | str |  | Electricity |
| `value` | measure | float64 | kt CO2eq | 0.0069994014960735 |

### `scopes_summary_detailed.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi with Danish |
| `analysis_year` | measure | int64 |  | 2019 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `scope` | dimension | str |  | Scope 1 |
| `value` | measure | float64 | varies by row | 163.39469914555332 |
| `basis` | dimension | str |  | national accounts (DRIVHUS/AFFALD) + med |
