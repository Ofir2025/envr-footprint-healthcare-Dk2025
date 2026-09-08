# 06_benchmarks_validation

**06 — Benchmarks and the standing consistency audit**

Is the result right? Two independent tests: agreement with published Danish footprints, and internal consistency across the study's own outputs.

Method, equations and verification: [`docs/methods/replications/06_benchmarks_validation.md`](../../../docs/methods/replications/06_benchmarks_validation.md).

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

### `consistency_audit.csv`

- **Rows:** 10
- **Dimensions:** `check`
- **Measures:** `status`, `detail`, `known_conventions`

### `danish_healthcare_benchmark_boundary_matched.csv`

- **Rows:** 4
- **Dimensions:** `basis`, `sector_boundary`, `model_type`, `model`
- **Measures:** `capital`, `year`, `value_kt`, `t_per_capita`, `share_of_national_pct`, `comparable_with_published`, `ratio_to_published`, `residual_caveat`

### `demand_vector_consistency.csv`

- **Rows:** 3
- **Dimensions:** `component`, `mapped_sector`
- **Measures:** `y_H_meur`, `exiobase_dk_final_demand_meur`, `ratio`, `analysis_year`, `interpretation`

### `figaro_dk_footprint_by_final_demand.csv`

- **Rows:** 6
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `unit`, `source`
- **Measures:** `final_demand_category`, `final_demand_label`, `value`

### `figaro_dk_footprint_by_origin.csv`

- **Rows:** 49
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `country_producing`, `unit`, `source`
- **Measures:** `is_aggregate`, `value`

### `figaro_eu27_material_footprint_health.csv`

- **Rows:** 2
- **Units:** kt
- **Dimensions:** `country_consuming`, `sector_consuming`, `unit`, `source`, `note`
- **Measures:** `cpa_code`, `value`, `per_capita_t`

### `figaro_vs_this_study_climate.csv`

- **Rows:** 5
- **Units:** kt CO2eq
- **Dimensions:** `quantity`, `source`, `unit`
- **Measures:** `analysis_year`, `value`, `per_capita_t`, `ratio_to_figaro_national`

### `published_danish_footprint_benchmarks.csv`

- **Rows:** 5
- **Dimensions:** `source`, `model_family`, `note`
- **Measures:** `year`, `total_mt`, `per_capita_t`, `capital`

### `recipe_validation_2022.csv`

- **Rows:** 11
- **Dimensions:** none
- **Measures:** `Unnamed: 0`, `EXIOBASE 2022 DK health column (%)`, `DST IOT 2022 health industries (%)`

### `recipe_validation_three_way.csv`

- **Rows:** 11
- **Dimensions:** `input_group_share_pct`
- **Measures:** `EXIOBASE v3.10.2 (modelled)`, `Eurostat FIGARO Q86 (official EU)`, `Statistics Denmark IO 86 (national)`
