# star

## Conventions

| Item | Convention |
|---|---|
| Schema | star schema: dimension columns, then measure and unit |
| Industry / product codes | EXIOBASE codes **without** the `A_` / `C_` prefix |
| Countries | ISO3 (`DNK`, `DEU`, `ROU`) |
| Regions without an ISO3 code | region name (`RoW Europe`, `RoW Africa`, ...) |
| Monetary unit | M.EUR, EXIOBASE basic prices, unless a column says otherwise |
| Provenance | one row per file in `../MANIFEST_lineage.csv` |

## Tables

### `dim_demand_component.csv`

- **Rows:** 3
- **Dimensions:** `demand_component_name`
- **Measures:** `demand_component_id`

### `dim_health_function.csv`

- **Rows:** 5
- **Dimensions:** `health_function_name`
- **Measures:** `health_function_id`

### `dim_indicator.csv`

- **Rows:** 13
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator_code`, `unit`
- **Measures:** `indicator_id`

### `dim_industry.csv`

- **Rows:** 165
- **Dimensions:** `industry_code`, `industry_name`, `industry_type`, `technology_group`
- **Measures:** `industry_id`, `industry_group_id`, `isic_rev3_division`, `isic_rev3_description`

### `dim_industry_group.csv`

- **Rows:** 19
- **Dimensions:** `industry_group_name`
- **Measures:** `industry_group_id`

### `dim_model.csv`

- **Rows:** 1
- **Dimensions:** `model_label`, `background_year`, `gwp_vintage`, `scope_boundary`
- **Measures:** `model_id`, `analysis_year`, `mrio`, `danish_block_correction`, `capital`

### `dim_region.csv`

- **Rows:** 49
- **Dimensions:** `region_code`, `region_name`, `world_region`
- **Measures:** `region_id`, `is_row_region`, `is_domestic`

### `dim_scope.csv`

- **Rows:** 4
- **Dimensions:** `scope_name`
- **Measures:** `scope_id`

### `fact_footprint_node.csv`

- **Rows:** 193,047
- **Dimensions:** none
- **Measures:** `model_id`, `indicator_id`, `demand_component_id`, `producing_region_id`, `producing_industry_id`, `value`

### `fact_footprint_product.csv`

- **Rows:** 30,930
- **Dimensions:** none
- **Measures:** `model_id`, `indicator_id`, `demand_component_id`, `purchased_region_id`, `purchased_industry_id`, `value`

### `fact_health_function.csv`

- **Rows:** 25
- **Dimensions:** none
- **Measures:** `model_id`, `value`, `expenditure_meur`, `intensity_per_meur`, `indicator_id`, `health_function_id`

### `fact_national_total.csv`

- **Rows:** 5
- **Dimensions:** none
- **Measures:** `model_id`, `national_footprint`, `national_supply_chain`, `national_direct_households`, `healthcare_footprint_mrio`, `healthcare_share_pct`, `indicator_id`

### `fact_scope_node.csv`

- **Rows:** 7,345
- **Dimensions:** none
- **Measures:** `model_id`, `indicator_id`, `scope_id`, `producing_region_id`, `producing_industry_id`, `value`
