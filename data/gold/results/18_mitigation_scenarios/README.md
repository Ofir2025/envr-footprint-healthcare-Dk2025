# 18_mitigation_scenarios

**18 · Counterfactual scenarios**

Method, equations, and verification: [`docs/methods/replications/18_mitigation_scenarios.md`](../../../docs/methods/replications/18_mitigation_scenarios.md).

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

### `burden_shifting.csv`

- **Rows:** 29
- **Dimensions:** `scenario_id`, `scenario`
- **Measures:** `ambition`, `blue_water_consumption`, `climate_change`, `land_use`, `material_extraction`, `waste_generation`, `shifts_burden`, `backfires_on_climate`, `non_climate_resolved`

### `mitigation_scenarios.csv`

- **Rows:** 145
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `country_consuming`, `scenario_id`, `scenario`, `scenario_type`, `indicator`, `unit`, `ambition_basis`, `source`, `note`, `model`
- **Measures:** `analysis_year`, `ambition`, `baseline`, `scenario_value`, `change`, `change_pct`, `per_capita_change`, `k_t`, `k_p`, `k_a`, `edited_objects`, `rebound`, `unbalanced_pct_of_output`

### `target_consistency.csv`

- **Rows:** 12
- **Units:** %, kt CO2eq
- **Dimensions:** `quantity`, `unit`, `target`, `basis`
- **Measures:** `value`, `caveat`
