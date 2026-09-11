# 12_impact_categories_full

**Full impact-category profile**

The study's headline uses five indicators, the five rows of `00_core_footprint/national_totals_summary.csv`. The studies it is benchmarked against use different and wider sets: Eckelman & Sherman report nine TRACI categories plus DALYs, Malik et al. several environmental impacts, Lenzen et al. a long KPI list. Comparing one stressor at a time is not a replication.

Method, equations, and verification: [`docs/methods/replications.md`, section 12](../../../../docs/methods/replications.md#r12).

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

### `impact_categories_all_methods.csv`

- **Rows:** 99
- **Format:** csv
- **Units:** 1000 p., Accumulated Exceedance (AE), CTUe = PAF.m3.year, CTUh = cases, CTUh/kg = cases, DALY
- **Dimensions:** `country_consuming`, `method`, `indicator`, `unit`, `sheet`, `component`, `model`, `sector_consuming`, `quality_flag`, `quality_note`
- **Measures:** `analysis_year`, `n_nonzero_factors`, `healthcare_supply_chain`, `national_supply_chain`, `healthcare_share_of_national_pct`, `healthcare_per_capita`

### `impact_categories_by_producing_node.csv.gz`

- **Rows:** 600,866
- **Format:** csv
- **Resolution:** 41+ regions x 79+ industries (sampled)
- **Units:** M.EUR
- **Dimensions:** `country_consuming`, `sector_consuming`, `method`, `indicator`, `unit`, `quality_flag`, `model`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`
- **Measures:** `analysis_year`, `value`

### `impact_categories_by_sector_group.csv`

- **Rows:** 1,826
- **Format:** csv
- **Units:** 1000 p., DALY, M.hr, PDF*m2*yr, elu, kt
- **Dimensions:** `method`, `indicator`, `unit`, `producing_sector_group`
- **Measures:** `value`

### `impact_categories_domestic_vs_imported.csv`

- **Rows:** 194
- **Format:** csv
- **Units:** 1000 p., Accumulated Exceedance (AE), CTUe = PAF.m3.year, CTUh = cases, CTUh/kg = cases, DALY
- **Dimensions:** `method`, `indicator`, `unit`, `quality_flag`, `origin`
- **Measures:** `value`, `share_of_total_pct`

### `stressor_totals_uncharacterised.csv`

- **Rows:** 1,027
- **Format:** csv
- **Dimensions:** `country_consuming`, `sector_consuming`, `stressor`, `model`
- **Measures:** `analysis_year`, `healthcare_supply_chain`, `national_supply_chain`
