# 08_lenzen_replication

**Lenzen KPI set**

This layer reproduces for Denmark every indicator Lenzen et al. publish per country, so our result can be placed directly beside their published Danish row.

Method, equations, and verification: [`docs/methods/replications.md`, section 08](../../../../docs/methods/replications.md#r08).

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

### `lenzen_expenditure_base_check.csv`

- **Rows:** 5
- **Format:** csv
- **Units:** %, -, EUR per capita, bn DKK current prices
- **Dimensions:** `quantity`, `unit`, `source`
- **Measures:** `value`

### `lenzen_kpi_by_producing_node.csv.gz`

- **Rows:** 43,355
- **Format:** csv
- **Resolution:** 43+ regions x 86+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `sector_consuming`, `indicator`, `unit`, `model`, `quantity`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`
- **Measures:** `value`

### `lenzen_kpi_domestic_vs_imported.csv`

- **Rows:** 18
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `origin`
- **Measures:** `value`, `share_of_total_pct`

### `lenzen_kpi_set.csv`

- **Rows:** 11
- **Format:** csv
- **Units:** GL, Mm3, km2, kt, kt CO2eq, million people
- **Dimensions:** `consuming_country_iso3`, `indicator`, `unit`, `lenzen_unit`, `lenzen_note`
- **Measures:** `analysis_year`, `total`, `direct`, `supplier_first_order`, `higher_order`, `direct_pct`, `supplier_pct`, `higher_order_pct`, `truncation_error_TE0_pct`, `truncation_error_TE1_pct`, `per_capita`, `national_total`, `share_of_national_pct`, `intensity_per_meur`, `domestic_pct`, `import_pct`, `lenzen_dk_2015`, `population`, `health_expenditure_meur`
