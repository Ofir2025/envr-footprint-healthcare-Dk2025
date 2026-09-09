# star - data dictionary

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

### `dim_capital_treatment.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `capital_treatment_id` | dimension | int64 |  | 1 |
| `treatment_code` | dimension | str |  | baseline_capital_excluded |
| `treatment_name` | dimension | str |  | Capital excluded (Steenmeijer-comparable |
| `capital_included` | dimension | bool |  | False |
| `produced_by` | dimension | str |  | analysis.capital_gfcf |

### `dim_demand_component.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `demand_component_id` | dimension | int64 |  | 1 |
| `demand_component_name` | dimension | str |  | healthcare_services |

### `dim_draw_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `draw_group_id` | dimension | int64 |  | 1 |
| `draw_group_name` | dimension | str |  | Food and food services |

### `dim_gwp_vintage.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `gwp_vintage_id` | dimension | int64 |  | 1 |
| `vintage_code` | dimension | str |  | IPCC SAR (1995) |
| `is_study_default` | dimension | bool |  | False |

### `dim_impact_category.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `impact_category_id` | dimension | int64 |  | 1 |
| `method` | dimension | str |  | Damage Approach |
| `category_code` | dimension | str |  | EPS (Steen, 1999)) |
| `unit` | dimension | str |  | elu |
| `quality_flag` | dimension | str |  | ok |

### `dim_indicator.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator_id` | dimension | int64 |  | 1 |
| `indicator_code` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |

### `dim_industry.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `industry_id` | dimension | int64 |  | 1 |
| `industry_code` | dimension | str |  | PARI |
| `industry_name` | dimension | str |  | Cultivation of paddy rice |
| `industry_group_id` | dimension | int64 |  | 6 |
| `industry_type` | dimension | str |  | MRIO industry |
| `isic_rev3_division` | measure | float64 |  | 1.0 |
| `isic_rev3_description` | dimension | str |  | Agriculture, hunting and related service |
| `technology_group` | dimension | str |  | Low tech |

### `dim_industry_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `industry_group_id` | dimension | int64 |  | 1 |
| `industry_group_name` | dimension | str |  | Chemical |

### `dim_model.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `model_label` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `background_year` | dimension | str |  | 2022_snacship |
| `analysis_year` | measure | int64 |  | 2022 |
| `mrio` | dimension | str |  | EXIOBASE v3.8.2 IOT ixi |
| `danish_block_correction` | dimension | str |  | sea-transport reallocation (Rormose Jens |
| `gwp_vintage` | dimension | str |  | IPCC AR6 |
| `scope_boundary` | dimension | str |  | health and eldercare |
| `capital` | dimension | str |  | excluded from the headline |
| `is_headline` | dimension | bool |  | True |
| `source_folder` | dimension | str |  | 01_eriksen_replication/2022 |
| `note` | dimension | str |  | the configured run; every fact this buil |

### `dim_production_layer.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `production_layer_id` | dimension | int64 |  | 1 |
| `layer_code` | dimension | str |  | 0 |
| `layer_number` | measure | float64 |  | 0.0 |
| `layer_name` | dimension | str |  | direct (on-site, layer 0) |
| `is_residual` | dimension | bool |  | False |
| `has_node_detail` | dimension | bool |  | True |

### `dim_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `region_id` | dimension | int64 |  | 1 |
| `region_code` | dimension | str |  | AUT |
| `region_name` | dimension | str |  | Austria |
| `world_region` | dimension | str |  | Europe |
| `region_type` | dimension | str |  | MRIO region |
| `is_row_region` | dimension | bool |  | False |
| `is_domestic` | dimension | bool |  | False |

### `dim_scenario.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `scenario_id` | dimension | int64 |  | 1 |
| `scenario_code` | dimension | str |  | B1 |
| `scenario_label` | dimension | str |  | B1 grid and district heat, Danish, 2030 |
| `ambition` | dimension | str |  | KF22 to 2030 |
| `scenario_kind` | dimension | str |  | background pathway |
| `k_t` | dimension | str |  | 0.862266 |
| `k_p` | dimension | str |  | 1 |
| `k_a` | dimension | str |  | 0.862266 |
| `edited_objects` | dimension | str |  | B |
| `rebound` | dimension | bool |  | False |
| `unbalanced_pct_of_output` | measure | float64 |  | 0.0 |
| `ambition_basis` | dimension | str |  | the Danish grid, which is what the proje |
| `source` | dimension | str |  | Danish Energy Agency KF22: 122.7 -> 16.9 |
| `note` | dimension | str |  | scales the intensity matrix at transmiss |
| `in_combined` | dimension | bool |  | False |

### `dim_scope.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `scope_id` | dimension | int64 |  | 1 |
| `scope_name` | dimension | str |  | Outside protocol |

### `dim_scope_component.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `scope_component_id` | dimension | int64 |  | 1 |
| `component_code` | dimension | str |  | scope1_direct |
| `component_name` | dimension | str |  | Scope 1 direct (DRIVHUS, excl. medical N |
| `component_role` | dimension | str |  | addend |
| `parent_component_code` | dimension | str |  | scope1_total |

### `dim_substance.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `substance_id` | dimension | int64 |  | 1 |
| `substance_code` | dimension | str |  | CH4_biogenic |
| `base_unit` | dimension | str |  | kg |
| `gwp100` | measure | float64 |  | 27.0 |
| `gwp_vintage` | dimension | str |  | IPCC AR6 (2021) |
| `is_restatable` | dimension | bool |  | True |

### `fact_capital_node.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `capital_treatment_id` | dimension | int64 |  | 4 |
| `indicator_id` | dimension | int64 |  | 2 |
| `producing_region_id` | dimension | int64 |  | 1 |
| `producing_industry_id` | dimension | int64 |  | 2 |
| `value` | measure | float64 |  | 0.0739461137925476 |

### `fact_capital_scenario.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `capital_treatment_id` | dimension | int64 |  | 1 |
| `indicator_id` | dimension | int64 |  | 2 |
| `value` | measure | float64 |  | 4061.9511864328815 |
| `delta_vs_baseline` | measure | float64 |  | 0.0 |
| `pct_vs_baseline` | measure | float64 |  | 0.0 |
| `per_capita` | measure | float64 |  | 691.5819380246741 |

### `fact_footprint_bilateral.parquet`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `indicator_id` | dimension | int64 |  | 1 |
| `demand_component_id` | dimension | int64 |  | 1 |
| `producing_region_id` | dimension | int64 |  | 1 |
| `producing_industry_id` | dimension | int64 |  | 2 |
| `purchased_region_id` | dimension | int64 |  | 1 |
| `purchased_industry_id` | dimension | int64 |  | 2 |
| `value` | measure | float64 |  | 1.1479717331398931e-06 |

### `fact_footprint_node.parquet`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `indicator_id` | dimension | int64 |  | 1 |
| `demand_component_id` | dimension | int64 |  | 1 |
| `producing_region_id` | dimension | int64 |  | 1 |
| `producing_industry_id` | dimension | int64 |  | 2 |
| `value` | measure | float64 |  | 8.437715255581849e-05 |

### `fact_footprint_product.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `indicator_id` | dimension | int64 |  | 1 |
| `demand_component_id` | dimension | int64 |  | 1 |
| `purchased_region_id` | dimension | int64 |  | 1 |
| `purchased_industry_id` | dimension | int64 |  | 2 |
| `value` | measure | float64 |  | 5.434729087357228e-06 |

### `fact_ghg_species.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `substance_id` | dimension | int64 |  | 3 |
| `mass_kg` | measure | float64 |  | 2670662773.160374 |
| `gwp100` | measure | float64 |  | 1.0 |
| `co2eq_kt` | measure | float64 |  | 2670.662773160375 |

### `fact_gwp_vintage.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `gwp_vintage_id` | dimension | int64 |  | 1 |
| `indicator_id` | dimension | int64 |  | 2 |
| `healthcare_kt_co2eq` | measure | float64 |  | 3740.212749906714 |
| `national_kt_co2eq` | measure | float64 |  | 64766.870324631665 |
| `healthcare_share_pct` | measure | float64 | % | 5.774885726544461 |
| `healthcare_t_per_capita` | measure | float64 |  | 0.6368032168492488 |
| `not_restatable_kt_co2eq` | measure | float64 |  | 155.29988960547564 |

### `fact_health_expenditure.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `demand_component_id` | dimension | int64 |  | 1 |
| `purchased_region_id` | dimension | int64 |  | 1 |
| `purchased_industry_id` | dimension | int64 |  | 2 |
| `expenditure_meur` | measure | float64 |  | 0.000491428770022 |

### `fact_impact_node.parquet`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `impact_category_id` | dimension | int64 |  | 1 |
| `producing_region_id` | dimension | int64 |  | 1 |
| `producing_industry_id` | dimension | int64 |  | 2 |
| `value` | measure | float64 |  | 9827.429242261784 |

### `fact_national_total.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `national_footprint` | measure | float64 |  | 77477.50333386465 |
| `national_supply_chain` | measure | float64 |  | 67755.50852916535 |
| `national_direct_households` | measure | float64 |  | 9721.994804699298 |
| `healthcare_footprint_mrio` | measure | float64 |  | 3943.3970167956713 |
| `healthcare_share_pct` | measure | float64 | % | 5.089731660302548 |
| `indicator_id` | dimension | int64 |  | 2 |

### `fact_production_layer.parquet`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `indicator_id` | dimension | int64 |  | 1 |
| `production_layer_id` | dimension | int64 |  | 1 |
| `producing_region_id` | dimension | int64 |  | 1 |
| `producing_industry_id` | dimension | int64 |  | 63 |
| `value` | measure | float64 |  | 0.0004137612339798 |

### `fact_scenario_node.parquet`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `scenario_id` | dimension | int64 |  | 1 |
| `indicator_id` | dimension | int64 |  | 1 |
| `producing_region_id` | dimension | int64 |  | 1 |
| `producing_industry_id` | dimension | int64 |  | 2 |
| `value` | measure | float64 |  | 9.793619712318792e-05 |

### `fact_scope_component.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `indicator_id` | dimension | int64 |  | 2 |
| `scope_component_id` | dimension | int64 |  | 1 |
| `value` | measure | float64 |  | 118.5541696372094 |

### `fact_scope_node.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `indicator_id` | dimension | int64 |  | 1 |
| `scope_id` | dimension | int64 |  | 1 |
| `producing_region_id` | dimension | int64 |  | 7 |
| `producing_industry_id` | dimension | int64 |  | 165 |
| `value` | measure | float64 |  | 0.0761 |

### `fact_uncertainty_draw.parquet`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `model_id` | dimension | int64 |  | 1 |
| `indicator_id` | dimension | int64 |  | 2 |
| `draw_id` | dimension | int64 |  | 1 |
| `draw_group_id` | dimension | int64 |  | 1 |
| `value` | measure | float32 |  | 445.2305 |
