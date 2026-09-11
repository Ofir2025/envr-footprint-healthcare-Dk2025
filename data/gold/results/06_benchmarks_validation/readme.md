# 06_benchmarks_validation

**Benchmarks and the standing consistency audit**

Is the result right? Two independent tests answer it: agreement with published Danish footprints, and internal consistency across the study's own outputs.

Method, equations, and verification: [`docs/methods/replications.md`, section 06](../../../../docs/methods/replications.md#r06).

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

### `consistency_audit.csv`

- **Rows:** 18
- **Format:** csv
- **Dimensions:** `check`, `status`, `detail`, `known_conventions`
- **Measures:** none

### `danish_healthcare_benchmark_boundary_matched.csv`

- **Rows:** 4
- **Format:** csv
- **Dimensions:** `basis`, `sector_boundary`, `capital`, `model_type`, `comparable_with_published`, `model`, `residual_caveat`
- **Measures:** `year`, `value_kt`, `t_per_capita`, `share_of_national_pct`, `ratio_to_published`

### `demand_vector_consistency.csv`

- **Rows:** 3
- **Format:** csv
- **Dimensions:** `component`, `mapped_sector`, `interpretation`
- **Measures:** `y_H_meur`, `exiobase_dk_final_demand_meur`, `ratio`, `analysis_year`

### `dst_concordance_validation.csv`

- **Rows:** 278
- **Format:** csv
- **Dimensions:** `source_national_accounts`, `source_concordance`, `check`, `subject`, `exiobase_industries`, `dst_industries`, `flag`, `detail`
- **Measures:** `reference_year`, `exiobase_output_meur`, `dst_output_meur`, `output_difference_meur`, `ratio_exiobase_over_dst`, `ratio_relative_to_national_aggregate`, `share_of_exiobase_output_pct`, `share_of_dst_output_pct`

### `figaro_dk_footprint_by_final_demand.csv`

- **Rows:** 6
- **Format:** csv
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `final_demand_category`, `final_demand_label`, `unit`, `source`
- **Measures:** `value`

### `figaro_dk_footprint_by_origin.csv`

- **Rows:** 49
- **Format:** csv
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `country_producing`, `is_aggregate`, `unit`, `source`
- **Measures:** `value`

### `figaro_eu27_material_footprint_health.csv`

- **Rows:** 2
- **Format:** csv
- **Units:** kt
- **Dimensions:** `country_consuming`, `sector_consuming`, `cpa_code`, `unit`, `source`, `note`
- **Measures:** `value`, `per_capita_t`

### `figaro_vs_this_study_climate.csv`

- **Rows:** 5
- **Format:** csv
- **Units:** kt CO2eq
- **Dimensions:** `quantity`, `source`, `unit`
- **Measures:** `analysis_year`, `value`, `per_capita_t`, `ratio_to_figaro_national`

### `published_danish_footprint_benchmarks.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `source`, `model_family`, `capital`, `note`
- **Measures:** `year`, `total_mt`, `per_capita_t`

### `recipe_validation_2022.csv`

- **Rows:** 11
- **Format:** csv
- **Dimensions:** `Unnamed: 0`
- **Measures:** `EXIOBASE 2022 DK health column (%)`, `DST IOT 2022 health industries (%)`

### `recipe_validation_three_way.csv`

- **Rows:** 11
- **Format:** csv
- **Dimensions:** `input_group_share_pct`
- **Measures:** `EXIOBASE v3.10.2 (modelled)`, `Eurostat FIGARO Q86 (official EU)`, `Statistics Denmark IO 86 (national)`

### `snac_split_weight_sensitivity.csv`

- **Rows:** 58
- **Format:** csv
- **Dimensions:** `exiobase_code`, `exiobase_name`, `dst_industries`, `dst_output_share`, `dst_import_share`, `member_intensity_kt_per_bndkk`
- **Measures:** `reference_year`, `n_dst`, `q_import_weighted`, `q_output_weighted`, `q_equal_weighted`, `q_min`, `q_max`, `spread_within_group`, `ratio_import_over_output`, `ratio_equal_over_import`, `q_import_relative_to_national`, `group_imports_bndkk`, `group_output_bndkk`, `import_penetration`

### `year_comparison_2019_2022.csv`

- **Rows:** 5
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `per_capita_unit`, `comparable_as_a_trend`, `why_not`
- **Measures:** `per_capita_2019`, `per_capita_2022`, `value_2019`, `value_2022`, `ratio_2022_over_2019`, `change_pct`

### `year_comparison_climate_bridge.csv`

- **Rows:** 9
- **Format:** csv
- **Dimensions:** `contribution_group`, `driver`
- **Measures:** `value_2019`, `share_pct_2019`, `value_2022`, `share_pct_2022`, `delta_kt`, `share_of_total_change_pct`

### `year_comparison_run_differences.csv`

- **Rows:** 4
- **Format:** csv
- **Dimensions:** `dimension`, `y2019`, `y2022`, `kind`, `effect`
- **Measures:** none

### `year_comparison_two_step_bridge.csv`

- **Rows:** 9
- **Format:** csv
- **Dimensions:** `contribution_group`, `driver`
- **Measures:** `value_2019_uncorrected`, `value_2019_shipping_corrected`, `value_2022_shipping_corrected`, `delta_correction_kt`, `delta_year_kt`, `share_of_correction_change_pct`, `share_of_year_change_pct`
