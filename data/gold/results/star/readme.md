# star

## Conventions

| Item | Convention |
|:---|:---|
| Schema | star schema: dimension columns, then measure and unit |
| Industry / product codes | EXIOBASE codes **without** the `A_` / `C_` prefix |
| Countries | ISO3 (`DNK`, `DEU`, `ROU`) |
| Regions without an ISO3 code | region name (`RoW Europe`, `RoW Africa`, ...) |
| Monetary unit | M.EUR, EXIOBASE basic prices, unless a column says otherwise |
| Provenance | one row per file in `../manifest_lineage.csv` |

## Tables

### `dim_capital_treatment.csv`

- **Rows:** 4
- **Format:** csv
- **Dimensions:** `capital_treatment_id`, `treatment_code`, `treatment_name`, `capital_included`, `produced_by`
- **Measures:** none

### `dim_demand_component.csv`

- **Rows:** 3
- **Format:** csv
- **Dimensions:** `demand_component_id`, `demand_component_name`
- **Measures:** none

### `dim_draw_group.csv`

- **Rows:** 9
- **Format:** csv
- **Dimensions:** `draw_group_id`, `draw_group_name`
- **Measures:** none

### `dim_gwp_vintage.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `gwp_vintage_id`, `vintage_code`, `is_study_default`
- **Measures:** none

### `dim_impact_category.csv`

- **Rows:** 97
- **Format:** csv
- **Units:** 1000 p., Accumulated Exceedance (AE), CTUe = PAF.m3.year, CTUh = cases, CTUh/kg = cases, DALY
- **Dimensions:** `impact_category_id`, `method`, `category_code`, `unit`, `quality_flag`
- **Measures:** none

### `dim_indicator.csv`

- **Rows:** 13
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator_id`, `indicator_code`, `unit`
- **Measures:** none

### `dim_industry.csv`

- **Rows:** 171
- **Format:** csv
- **Dimensions:** `industry_id`, `industry_code`, `industry_name`, `industry_group_id`, `industry_type`, `isic_rev3_description`, `technology_group`
- **Measures:** `isic_rev3_division`

### `dim_industry_group.csv`

- **Rows:** 22
- **Format:** csv
- **Dimensions:** `industry_group_id`, `industry_group_name`
- **Measures:** none

### `dim_model.csv`

- **Rows:** 4
- **Format:** csv
- **Dimensions:** `model_id`, `model_label`, `background_year`, `mrio`, `danish_block_correction`, `gwp_vintage`, `scope_boundary`, `capital`, `is_headline`, `source_folder`, `note`
- **Measures:** `analysis_year`

### `dim_production_layer.csv`

- **Rows:** 22
- **Format:** csv
- **Dimensions:** `production_layer_id`, `layer_code`, `layer_name`, `is_residual`, `has_node_detail`
- **Measures:** `layer_number`

### `dim_region.csv`

- **Rows:** 50
- **Format:** csv
- **Dimensions:** `region_id`, `region_code`, `region_name`, `world_region`, `region_type`, `is_row_region`, `is_domestic`
- **Measures:** none

### `dim_scenario.csv`

- **Rows:** 33
- **Format:** csv
- **Dimensions:** `scenario_id`, `scenario_code`, `scenario_label`, `ambition`, `scenario_kind`, `k_t`, `k_p`, `k_a`, `edited_objects`, `rebound`, `ambition_basis`, `source`, `note`, `in_combined`
- **Measures:** `unbalanced_pct_of_output`

### `dim_scope.csv`

- **Rows:** 4
- **Format:** csv
- **Dimensions:** `scope_id`, `scope_name`
- **Measures:** none

### `dim_scope_component.csv`

- **Rows:** 10
- **Format:** csv
- **Dimensions:** `scope_component_id`, `component_code`, `component_name`, `component_role`, `parent_component_code`
- **Measures:** none

### `dim_substance.csv`

- **Rows:** 6
- **Format:** csv
- **Dimensions:** `substance_id`, `substance_code`, `base_unit`, `gwp_vintage`, `is_restatable`
- **Measures:** `gwp100`

### `fact_capital_node.csv`

- **Rows:** 6,870
- **Format:** csv
- **Dimensions:** `model_id`, `capital_treatment_id`, `indicator_id`, `producing_region_id`, `producing_industry_id`
- **Measures:** `value`

### `fact_capital_scenario.csv`

- **Rows:** 15
- **Format:** csv
- **Dimensions:** `model_id`, `capital_treatment_id`, `indicator_id`
- **Measures:** `value`, `delta_vs_baseline`, `pct_vs_baseline`, `per_capita`

### `fact_footprint_bilateral.parquet`

- **Rows:** 2,351,620
- **Format:** parquet (pyarrow, snappy)
- **Dimensions:** `model_id`, `indicator_id`, `demand_component_id`, `producing_region_id`, `producing_industry_id`, `purchased_region_id`, `purchased_industry_id`
- **Measures:** `value`

### `fact_footprint_node.parquet`

- **Rows:** 193,047
- **Format:** parquet (pyarrow, snappy)
- **Dimensions:** `model_id`, `indicator_id`, `demand_component_id`, `producing_region_id`, `producing_industry_id`
- **Measures:** `value`

### `fact_footprint_product.csv`

- **Rows:** 30,930
- **Format:** csv
- **Dimensions:** `model_id`, `indicator_id`, `demand_component_id`, `purchased_region_id`, `purchased_industry_id`
- **Measures:** `value`

### `fact_ghg_species.csv`

- **Rows:** 6
- **Format:** csv
- **Dimensions:** `model_id`, `substance_id`
- **Measures:** `mass_kg`, `gwp100`, `co2eq_kt`

### `fact_gwp_vintage.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `model_id`, `gwp_vintage_id`, `indicator_id`
- **Measures:** `healthcare_kt_co2eq`, `national_kt_co2eq`, `healthcare_share_pct`, `healthcare_t_per_capita`, `not_restatable_kt_co2eq`

### `fact_health_expenditure.csv`

- **Rows:** 6,186
- **Format:** csv
- **Dimensions:** `model_id`, `demand_component_id`, `purchased_region_id`, `purchased_industry_id`
- **Measures:** `expenditure_meur`

### `fact_impact_node.parquet`

- **Rows:** 600,866
- **Format:** parquet (pyarrow, snappy)
- **Dimensions:** `model_id`, `impact_category_id`, `producing_region_id`, `producing_industry_id`
- **Measures:** `value`

### `fact_national_total.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `model_id`, `indicator_id`
- **Measures:** `national_footprint`, `national_supply_chain`, `national_direct_households`, `healthcare_footprint_mrio`, `healthcare_share_pct`

### `fact_production_layer.parquet`

- **Rows:** 444,389
- **Format:** parquet (pyarrow, snappy)
- **Dimensions:** `model_id`, `indicator_id`, `production_layer_id`, `producing_region_id`, `producing_industry_id`
- **Measures:** `value`

### `fact_scenario_node.parquet`

- **Rows:** 733,920
- **Format:** parquet (pyarrow, snappy)
- **Dimensions:** `model_id`, `scenario_id`, `indicator_id`, `producing_region_id`, `producing_industry_id`
- **Measures:** `value`

### `fact_scope_component.csv`

- **Rows:** 40
- **Format:** csv
- **Dimensions:** `model_id`, `indicator_id`, `scope_component_id`
- **Measures:** `value`

### `fact_scope_node.csv`

- **Rows:** 23,737
- **Format:** csv
- **Dimensions:** `model_id`, `indicator_id`, `scope_id`, `producing_region_id`, `producing_industry_id`
- **Measures:** `value`

### `fact_uncertainty_draw.parquet`

- **Rows:** 900,000
- **Format:** parquet (pyarrow, snappy)
- **Dimensions:** `model_id`, `indicator_id`, `draw_id`, `draw_group_id`
- **Measures:** `value`
