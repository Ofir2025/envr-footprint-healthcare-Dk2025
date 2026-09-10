# 18_mitigation_scenarios

**Counterfactual scenarios**

Method, equations, and verification: [`docs/methods/replications.md`, section 18](../../../../docs/methods/replications.md#r18).

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

### `burden_shifting.csv`

- **Rows:** 33
- **Format:** csv
- **Dimensions:** `scenario_id`, `scenario`, `ambition`, `shifts_burden`, `backfires_on_climate`, `non_climate_resolved`
- **Measures:** `blue_water_consumption`, `climate_change`, `land_use`, `material_extraction`, `waste_generation`

### `mitigation_scenarios.csv`

- **Rows:** 165
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `country_consuming`, `scenario_id`, `scenario`, `scenario_type`, `ambition`, `indicator`, `unit`, `per_capita_unit`, `k_t`, `k_p`, `k_a`, `edited_objects`, `rebound`, `ambition_basis`, `source`, `note`, `model`
- **Measures:** `analysis_year`, `baseline`, `scenario_value`, `change`, `change_pct`, `per_capita_change`, `unbalanced_pct_of_output`

### `scenario_selection.csv`

- **Rows:** 8
- **Format:** csv
- **Dimensions:** `scenario_id`, `scenario`, `ambition`, `in_combined`
- **Measures:** none

### `scenarios_by_producing_node.csv.gz`

- **Rows:** 733,920
- **Format:** csv
- **Resolution:** 3+ regions x 158+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `scenario_id`, `scenario`, `ambition`, `indicator`, `unit`, `producing_country_iso3`, `producing_country_name`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `value_type`, `model`
- **Measures:** `analysis_year`, `value`

### `target_consistency.csv`

- **Rows:** 12
- **Format:** csv
- **Units:** %, kt CO2eq
- **Dimensions:** `quantity`, `unit`, `target`, `basis`, `caveat`
- **Measures:** `value`
