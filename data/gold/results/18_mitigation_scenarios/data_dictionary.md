# 18_mitigation_scenarios - data dictionary

One row per column of every table in this folder. Units are the
table's own; `varies by row` means the table carries a `unit`
column and the value is read from there.

## Common columns

Every gold table shares this vocabulary; columns particular to one table
are described below, per table.

| Column | Meaning |
|:---|:---|
| `analysis_year` | year of the Danish expenditure data and of the MRIO background |
| `model` | MRIO release actually used (e.g. `EXIOBASE v3.8.2 IOT_2022_ixi with Danish sea-transport reallocation (Rørmose Jensen & Iliev 2022)`) - **not** v3.10.2, which this study rejects (see `docs/methods/exiobase_version_vintage_and_classification.md`) |
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

### `burden_shifting.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `scenario_id` | dimension | str |  | B1 |
| `scenario` | dimension | str |  | B1 grid and district heat, Danish, 2030 |
| `ambition` | dimension | str |  | KF22 to 2030 |
| `blue_water_consumption` | measure | float64 |  | -1.4879704410679468e-14 |
| `climate_change` | measure | float64 |  | -3.0476807431981245 |
| `land_use` | measure | float64 |  | 0.0 |
| `material_extraction` | measure | float64 |  | 0.0 |
| `waste_generation` | measure | float64 |  | -1.2821856898918456 |
| `shifts_burden` | dimension | bool |  | False |
| `backfires_on_climate` | dimension | bool |  | False |
| `non_climate_resolved` | dimension | bool |  | True |

### `mitigation_scenarios.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `analysis_year` | measure | int64 |  | 2022 |
| `scenario_id` | dimension | str |  | B1 |
| `scenario` | dimension | str |  | B1 grid and district heat, Danish, 2030 |
| `scenario_type` | dimension | str |  | background pathway |
| `ambition` | dimension | str |  | KF22 to 2030 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `baseline` | measure | float64 | varies by row | 4712.417605953846 |
| `scenario_value` | measure | float64 | varies by row | 4568.798162038112 |
| `change` | measure | float64 | varies by row | -143.61944391573343 |
| `change_pct` | measure | float64 | % | -3.0476807431981245 |
| `per_capita_change` | measure | float64 | varies by row | -24.45243893944813 |
| `per_capita_unit` | dimension | str |  | kg CO2eq per capita |
| `k_t` | dimension | str |  | 0.862266 |
| `k_p` | dimension | str |  | 1 |
| `k_a` | dimension | str |  | 0.862266 |
| `edited_objects` | dimension | str |  | B |
| `rebound` | dimension | bool |  | False |
| `unbalanced_pct_of_output` | measure | float64 | varies by row | 0.0 |
| `ambition_basis` | dimension | str |  | the Danish grid, which is what the proje |
| `source` | dimension | str |  | Danish Energy Agency KF22: 122.7 -> 16.9 |
| `note` | dimension | str |  | scales the intensity matrix at transmiss |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |

### `scenario_selection.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `scenario_id` | dimension | str |  | P1 |
| `scenario` | dimension | str |  | P1 hospital energy and transport |
| `ambition` | dimension | str |  | -75 % by 2030, 100% of the target met |
| `in_combined` | dimension | str |  | C1 |

### `scenarios_by_producing_node.csv.gz`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `analysis_year` | measure | int64 |  | 2022 |
| `scenario_id` | dimension | str |  | B1 |
| `scenario` | dimension | str |  | B1 grid and district heat, Danish, 2030 |
| `ambition` | dimension | str |  | KF22 to 2030 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `producing_country_iso3` | dimension | str |  | AUT |
| `producing_country_name` | dimension | str |  | Austria |
| `producing_sector_code` | dimension | str |  | WHEA |
| `producing_sector_name` | dimension | str |  | Cultivation of wheat |
| `producing_sector_group` | dimension | str |  | Food and catering |
| `value_type` | dimension | str |  | supply chain |
| `value` | measure | float64 | kt CO2eq | 0.068653306187386 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |

### `target_consistency.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `quantity` | dimension | str |  | baseline climate footprint |
| `value` | measure | float64 | varies by row | 4712.417605953846 |
| `unit` | dimension | str |  | kt CO2eq |
| `target` | dimension | str |  | Danske Regioner, January 2024 |
| `basis` | dimension | str |  | consumption-based CO2 of hospitals, agai |
| `caveat` | dimension | str |  | the regional target covers hospitals whi |
