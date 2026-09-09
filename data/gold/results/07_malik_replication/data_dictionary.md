# 07_malik_replication - data dictionary

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

### `malik_component_intensities.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `consuming_country_iso3` | dimension | str |  | DNK |
| `analysis_year` | measure | int64 | varies by row | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `component` | dimension | str |  | healthcare_services |
| `footprint` | measure | float64 | varies by row | 2344.885845780632 |
| `expenditure_meur` | measure | float64 | varies by row | 37552.28493467391 |
| `total_intensity_per_meur` | measure | float64 | varies by row | 0.0624432268198807 |
| `direct_intensity_per_meur` | measure | float64 | varies by row | 0.0117217097512177 |

### `malik_domestic_vs_full.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `consuming_country_iso3` | dimension | str |  | DNK |
| `analysis_year` | measure | int64 | varies by row | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `full_mrio` | measure | float64 | varies by row | 4061.9511864328815 |
| `domestic_only` | measure | float64 | varies by row | 839.4965252767034 |
| `domestic_share_of_full_pct` | measure | float64 | varies by row | 20.66732185459696 |
| `share_of_national_full_pct` | measure | float64 | varies by row | 5.995012471472214 |
| `share_of_national_domestic_pct` | measure | float64 | varies by row | 3.983162174492114 |

### `malik_published_reference.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `consuming_country_iso3` | dimension | str |  | DNK |
| `analysis_year` | measure | int64 |  | 2022 |
| `study` | measure | str |  | Malik et al. 2018 (Australia, 2014-15) |
| `indicator` | dimension | str |  | climate_change |
| `total_kt` | measure | float64 |  | 35772.0 |
| `share_national_pct` | measure | float64 |  | 7.2 |
| `direct_pct` | measure | float64 |  | 13.4 |
| `boundary` | measure | str |  | domestic-only; capital INCLUDED; aged ca |

### `production_layers.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `method` | dimension | str |  | production layer decomposition, Malik et |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `consuming_country_iso3` | dimension | str |  | DNK |
| `analysis_year` | measure | int64 | varies by row | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `layer` | dimension | str |  | 0 |
| `value` | measure | float64 | varies by row | 353.33928659046666 |
| `share_pct` | measure | float64 | varies by row | 8.6988278774147 |
| `cumulative_share_pct` | measure | float64 | varies by row | 8.6988278774147 |
| `truncation_error_pct` | measure | float64 | varies by row | 91.3011721225853 |

### `production_layers_by_producing_node.csv.gz`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `analysis_year` | measure | int64 | kt CO2eq | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `layer` | measure | int64 | kt CO2eq | 0 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `producing_country_iso3` | dimension | str |  | DNK |
| `producing_country_name` | dimension | str |  | Denmark |
| `producing_world_region` | dimension | str |  | Denmark |
| `producing_sector_code` | dimension | str |  | HEAL |
| `producing_sector_name` | dimension | str |  | Health and social work (85) |
| `producing_sector_group` | dimension | str |  | Services |
| `value` | measure | float64 | kt CO2eq | 118.5541696372094 |

### `production_layers_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `method` | dimension | str |  | production layer decomposition, Malik et |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `consuming_country_iso3` | dimension | str |  | DNK |
| `analysis_year` | measure | int64 | varies by row | 2022 |
| `sector_group` | dimension | str |  | Chemical |
| `value` | measure | float64 | varies by row | 228.7552377324756 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `layer` | measure | int64 | varies by row | 0 |

### `production_layers_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `layer` | measure | int64 | varies by row | 0 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 0.1484568765427218 |
| `share_of_total_pct` | measure | float64 | varies by row | 4.19807516788021 |

### `production_layers_vs_malik.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `denmark_first_three_layers_pct` | measure | float64 |  | 62.99012726771795 |
| `malik_nsw_first_three_layers_pct` | measure | float64 |  | 67.0 |
| `denmark_first_layer_pct` | measure | float64 |  | 8.6988278774147 |
| `malik_nsw_first_layer_pct` | measure | float64 |  | 11.0 |
| `malik_total` | measure | float64 |  | 7908.0 |
| `malik_unit` | dimension | str |  | kt CO2e |
| `layer_definition` | dimension | str |  | Malik's 'first three production layers'  |
| `comparability` | measure | str |  | shares are comparable; levels are not -  |
| `source_malik` | dimension | str |  | Malik et al. 2021, Lancet Planet Health  |
| `source_denmark` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
