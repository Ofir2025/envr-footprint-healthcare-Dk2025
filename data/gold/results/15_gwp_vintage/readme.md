# 15_gwp_vintage

**15 - Climate characterisation vintage**

This study reports climate change on **IPCC AR6**. The characterisation workbook shipped with the background instead carries **AR4** factors (CH₄ = 25, N₂O = 298) under a sheet labelled "CML 1999". What does the restatement change, and what can it not reach?

Method, equations, and verification: [`docs/methods/replications/15_gwp_vintage.md`](../../../../docs/methods/replications/15_gwp_vintage.md).

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

### `gwp_by_species.csv`

- **Rows:** 6
- **Format:** csv
- **Units:** kg, kg CO2eq
- **Dimensions:** `country_consuming`, `sector_consuming`, `species`, `unit`
- **Measures:** `mass_kg`, `ar6_gwp100`, `contribution_kt_co2eq`

### `gwp_vintage_sensitivity.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `country_consuming`, `gwp_vintage`, `is_study_default`, `model`, `note`
- **Measures:** `analysis_year`, `healthcare_kt_co2eq`, `national_kt_co2eq`, `healthcare_share_pct`, `healthcare_t_per_capita`, `not_restatable_kt_co2eq`, `not_restatable_share_pct`
