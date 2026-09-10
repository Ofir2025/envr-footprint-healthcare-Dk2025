# 06_benchmarks_validation - data dictionary

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

### `consistency_audit.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `check` | dimension | str |  | C1 scope partition vs grand total |
| `status` | dimension | str |  | PASS |
| `detail` | dimension | str |  | partition total 4,710.58 + self-supply l |
| `known_conventions` | dimension | str |  | the capital baseline excludes the bottom |

### `danish_healthcare_benchmark_boundary_matched.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `basis` | dimension | str |  | Schmidt & Merciai 2023 (published compar |
| `sector_boundary` | dimension | str |  | Health and social work services (NACE Q, |
| `capital` | dimension | str |  | endogenised |
| `model_type` | dimension | str |  | consequential |
| `year` | measure | int64 |  | 2016 |
| `value_kt` | measure | float64 |  | 6100.0 |
| `t_per_capita` | measure | float64 |  | 1.07 |
| `share_of_national_pct` | measure | float64 | % | 8.3 |
| `comparable_with_published` | dimension | bool |  | True |
| `ratio_to_published` | measure | float64 |  | 1.0 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `residual_caveat` | dimension | str |  | their model is consequential (marginal), |

### `demand_vector_consistency.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `component` | dimension | str |  | pharmaceuticals |
| `mapped_sector` | dimension | str |  | mapped to Chemicals nec |
| `y_H_meur` | measure | float64 |  | 1950.3076778321415 |
| `exiobase_dk_final_demand_meur` | measure | float64 |  | 50.863367248858005 |
| `ratio` | measure | float64 |  | 38.34405355606751 |
| `analysis_year` | measure | int64 |  | 2022 |
| `interpretation` | dimension | str |  | y_H is superimposed on the model rather  |

### `dst_concordance_validation.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `reference_year` | measure | int64 |  | 2016 |
| `source_national_accounts` | dimension | str |  | Statistics Denmark, published 117-indust |
| `source_concordance` | dimension | str |  | EXIOBASE developers' NACE rev.2 concorda |
| `check` | dimension | str |  | completeness |
| `subject` | dimension | str |  | every EXIOBASE industry appears exactly  |
| `exiobase_industries` | dimension | str |  | 163 |
| `dst_industries` | dimension | str |  | 86;87;88 |
| `exiobase_output_meur` | measure | float64 |  | 37163.1 |
| `dst_output_meur` | measure | float64 |  | 36639.5 |
| `output_difference_meur` | measure | float64 |  | -954.2 |
| `ratio_exiobase_over_dst` | measure | float64 |  | 1.014 |
| `ratio_relative_to_national_aggregate` | measure | float64 |  | 0.975 |
| `share_of_exiobase_output_pct` | measure | float64 | % | 96.17 |
| `share_of_dst_output_pct` | measure | float64 | % | 98.74 |
| `flag` | dimension | str |  | pass |
| `detail` | dimension | str |  | 163 rows, 163 expected; duplicated []; a |

### `figaro_dk_footprint_by_final_demand.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `final_demand_category` | dimension | str |  | P31_S14 |
| `final_demand_label` | dimension | str |  | Final consumption expenditure of househo |
| `value` | measure | float64 | kt CO2eq | 30172.219 |
| `unit` | dimension | str |  | kt CO2eq |
| `source` | dimension | str |  | Eurostat env_ac_ghgfp (FIGARO), 2022 |

### `figaro_dk_footprint_by_origin.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `country_producing` | dimension | str |  | WORLD |
| `is_aggregate` | dimension | bool |  | True |
| `value` | measure | float64 | kt CO2eq | 57401.691 |
| `unit` | dimension | str |  | kt CO2eq |
| `source` | dimension | str |  | Eurostat env_ac_ghgfp (FIGARO), 2022 |

### `figaro_eu27_material_footprint_health.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | EU27_2020 |
| `sector_consuming` | dimension | str |  | Human health services |
| `cpa_code` | dimension | str |  | CPA_Q86 |
| `value` | measure | float64 | kt | 128627.907 |
| `unit` | dimension | str |  | kt |
| `per_capita_t` | measure | float64 | kt | 0.2879286897439226 |
| `source` | dimension | str |  | Eurostat env_ac_rmefd (FIGARO), 2022 |
| `note` | dimension | str |  | EU27 aggregate only; Eurostat publishes  |

### `figaro_vs_this_study_climate.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `analysis_year` | measure | int64 |  | 2022 |
| `quantity` | dimension | str |  | Danish national consumption-based GHG fo |
| `source` | dimension | str |  | Eurostat FIGARO (env_ac_ghgfp) |
| `value` | measure | float64 | kt CO2eq | 57401.691 |
| `unit` | dimension | str |  | kt CO2eq |
| `per_capita_t` | measure | float64 | kt CO2eq | 9.773128943613772 |
| `ratio_to_figaro_national` | measure | float64 | kt CO2eq | 1.0 |

### `published_danish_footprint_benchmarks.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `source` | dimension | str |  | Eurostat FIGARO (env_ac_ghgfp) |
| `year` | measure | int64 |  | 2022 |
| `model_family` | dimension | str |  | national accounts (FIGARO) |
| `total_mt` | measure | float64 |  | 57.4 |
| `per_capita_t` | measure | float64 |  | 9.77 |
| `capital` | dimension | str |  | exogenous |
| `note` | dimension | str |  | official EU statistical product |

### `recipe_validation_2022.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | water transport |
| `EXIOBASE 2022 DK health column (%)` | measure | float64 |  | 3.9 |
| `DST IOT 2022 health industries (%)` | measure | float64 |  | 0.4 |

### `recipe_validation_three_way.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `input_group_share_pct` | dimension | str |  | Water transport |
| `EXIOBASE v3.10.2 (modelled)` | measure | float64 |  | 3.9 |
| `Eurostat FIGARO Q86 (official EU)` | measure | float64 |  | 0.1 |
| `Statistics Denmark IO 86 (national)` | measure | float64 |  | 0.1 |

### `snac_split_weight_sensitivity.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `reference_year` | measure | int64 |  | 2019 |
| `exiobase_code` | dimension | str |  | COIL |
| `exiobase_name` | dimension | str |  | Extraction of crude petroleum and servic |
| `dst_industries` | dimension | str |  | 060000;090000 |
| `n_dst` | measure | int64 |  | 2 |
| `dst_output_share` | dimension | str |  | 0.860997;0.139003 |
| `dst_import_share` | dimension | str |  | 0.994294;0.005706 |
| `member_intensity_kt_per_bndkk` | dimension | str |  | 74.609;0.985 |
| `q_import_weighted` | measure | float64 |  | 72.65677170822848 |
| `q_output_weighted` | measure | float64 |  | 59.55176938460458 |
| `q_equal_weighted` | measure | float64 |  | 37.79709882872971 |
| `q_min` | measure | float64 |  | 0.9850561078108444 |
| `q_max` | measure | float64 |  | 74.60914154964858 |
| `spread_within_group` | measure | float64 |  | 75.7410069924417 |
| `ratio_import_over_output` | measure | float64 |  | 1.2200606708927078 |
| `ratio_equal_over_import` | measure | float64 |  | 0.5202143990172514 |
| `q_import_relative_to_national` | measure | float64 |  | 3.4859961179447994 |
| `group_imports_bndkk` | measure | float64 |  | 19.241176167487257 |
| `group_output_bndkk` | measure | float64 |  | 24.818742000000004 |
| `import_penetration` | measure | float64 |  | 0.4367047640520977 |

### `year_comparison_2019_2022.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `per_capita_2019` | measure | float64 | varies by row | 9.885627152008569 |
| `per_capita_2022` | measure | float64 | varies by row | 16.260535271709426 |
| `value_2019` | measure | float64 | varies by row | 57.47920799643595 |
| `value_2022` | measure | float64 | varies by row | 95.50495307556358 |
| `ratio_2022_over_2019` | measure | float64 | varies by row | 1.6615565246042612 |
| `change_pct` | measure | float64 | % | 66.15565246042611 |
| `per_capita_unit` | dimension | str |  | m3 per person |
| `comparable_as_a_trend` | dimension | bool |  | False |
| `why_not` | dimension | str |  | the background model and the sea-transpo |

### `year_comparison_climate_bridge.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `contribution_group` | dimension | str |  | Transport |
| `value_2019` | measure | float64 |  | 2605.151771420495 |
| `share_pct_2019` | measure | float64 | % | 40.952900791806286 |
| `value_2022` | measure | float64 |  | 595.84969141357 |
| `share_pct_2022` | measure | float64 | % | 12.644246355856732 |
| `delta_kt` | measure | float64 |  | -2009.3020800069253 |
| `share_of_total_change_pct` | measure | float64 | % | 121.85573525178977 |
| `driver` | dimension | str |  | sea-transport reallocation, applied in 2 |

### `year_comparison_run_differences.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `dimension` | dimension | str |  | reference year |
| `y2019` | dimension | str |  | 2019 |
| `y2022` | dimension | str |  | 2022 |
| `kind` | dimension | str |  | change in the world |
| `effect` | dimension | str |  | health-care expenditure rises 15 %, from |
