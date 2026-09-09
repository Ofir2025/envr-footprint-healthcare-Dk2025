# 11_capital_gfcf - data dictionary

One row per column of every table in this folder. Units are the
table's own; `varies by row` means the table carries a `unit`
column and the value is read from there.

## Common columns

Every gold table shares this vocabulary; columns particular to one table
are described below, per table.

| Column | Meaning |
|:---|:---|
| `analysis_year` | year of the Danish expenditure data and of the MRIO background |
| `model` | MRIO release actually used (e.g. `EXIOBASE v3.10.2 IOT_2022_ixi (screened)`) |
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

Every impact cell is `E[i,j] = s_k(i) . L(i,j) . y_H(j)`: pressure arising
in node *i* caused by Danish healthcare final demand for node *j*. Summing
over *i* gives the **consumption / contribution** perspective (by
purchased product); summing over *j* gives the **production / hotspot**
perspective (by producing node). Both are marginals of the same array, so
they sum to the identical total - verified to machine precision by
`analysis.validate_io_identities` (tests T5/T6). Allocating production
emissions to final demand is additive and does not double count (Wood et
al. 2018); embodied-flow tables (E_Z) would.

## Units

Monetary values are **million euro (M.EUR)** - EXIOBASE's native unit
(`unit.txt` of the release). No US-dollar values are used anywhere in this
model; dollar figures appearing in the comparative literature (Karliner et
al. 2019, Lenzen et al. 2020, Pichler et al. 2019) are those studies' own
units and are labelled as such wherever they are quoted.

## Tables

### `capital_asset_mix.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `asset` | dimension | str |  | ICT equipment, other machinery and equip |
| `consumption_of_fixed_capital_meur` | measure | float64 | M.EUR | 1016.5869132749071 |
| `share_pct` | measure | float64 | M.EUR | 44.714437743880815 |
| `exiobase_products` | dimension | str |  | Manufacture of office machinery and comp |
| `unit` | dimension | str |  | M.EUR |
| `source` | dimension | str |  | DST NABK69 P.51c 2022 |

### `capital_diagnostics.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `quantity` | dimension | str |  | DK health + residential care, consumptio |
| `value` | measure | float64 | varies by row | 2273.509328458519 |
| `unit` | dimension | str |  | M.EUR |
| `source` | dimension | str |  | Statistics Denmark NABK69, P.51c, V86000 |

### `capital_endogenised_by_producing_node.csv.gz`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `treatment` | measure | str | kt CO2eq | capital endogenised (Sodersten et al. 20 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `producing_country_iso3` | dimension | str |  | DNK |
| `producing_country_name` | dimension | str |  | Denmark |
| `producing_world_region` | dimension | str |  | Denmark |
| `producing_sector_code` | dimension | str |  | HWAT |
| `producing_sector_name` | dimension | str |  | Steam and hot water supply |
| `producing_sector_group` | dimension | str |  | Steam, hot water supply and water distri |
| `value` | measure | float64 | kt CO2eq | 106.90340755354045 |

### `capital_endogenised_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | kt CO2eq | 816.9225806529726 |
| `share_of_total_pct` | measure | float64 | kt CO2eq | 17.26914805775572 |

### `capital_endogenised_sodersten.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `analysis_year` | measure | int64 | varies by row | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `baseline_capital_excluded` | measure | float64 | varies by row | 4061.9511864328815 |
| `endogenised_sodersten` | measure | float64 | varies by row | 4849.0862023745485 |
| `change` | measure | float64 | varies by row | 787.135015941667 |
| `change_pct` | measure | float64 | varies by row | 19.37824901911025 |
| `per_capita_endogenised` | measure | float64 | varies by row | 0.8255984081462843 |
| `method` | dimension | str |  | Södersten, Wood & Hertwich (2018) Enviro |
| `kbar_year` | measure | int64 | varies by row | 2020 |
| `structure_assumption` | measure | str | varies by row | 2020 capital structure applied to 2022 l |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |

### `capital_scenarios_by_indicator.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `scenario` | dimension | str |  | baseline_capital_excluded |
| `indicator` | dimension | str |  | climate_change |
| `value` | measure | float64 | varies by row | 4061.9511864328815 |
| `unit` | dimension | str |  | kt CO2eq |
| `delta_vs_baseline` | measure | float64 | varies by row | 0.0 |
| `pct_vs_baseline` | measure | float64 | varies by row | 0.0 |
| `per_capita` | measure | float64 | varies by row | 691.5819380246741 |
| `per_capita_unit` | dimension | str |  | kg per capita |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `analysis_year` | measure | int64 | varies by row | 2022 |
| `note` | dimension | str |  | Steenmeijer-comparable; capital outside  |
