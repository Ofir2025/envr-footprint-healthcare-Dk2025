# 09_exiobase_release_diagnostics

**EXIOBASE release defects**

Which EXIOBASE release can carry this study? Rørmose Jensen & Iliev argue EXIOBASE's Danish block misallocates output between industries. This module turns that argument into a reproducible test rather than accepting or dismissing it.

Method, equations, and verification: [`docs/methods/replications.md`, section 09](../../../../docs/methods/replications.md#r09).

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

### `dk_block_vs_national_accounts.csv`

- **Rows:** 65
- **Format:** csv
- **Units:** M.EUR
- **Dimensions:** `mrio_release`, `country_producing`, `sector_producing`, `exiobase_industry_index`, `dst_nace_prefixes`, `unit`, `exiobase_source`, `source_national_accounts`
- **Measures:** `mrio_year`, `exiobase_output_meur`, `national_accounts_output_meur`, `ratio_exiobase_over_dst`

### `dk_health_output_by_release.csv`

- **Rows:** 30
- **Format:** csv
- **Units:** M.EUR
- **Dimensions:** `release`, `assessment`, `unit`, `exiobase_industry`, `dst_industries`
- **Measures:** `table_year`, `exiobase_output_meur`, `national_accounts_output_meur`, `ratio_exiobase_over_dst`

### `industry33_output_by_region.csv`

- **Rows:** 245
- **Format:** csv
- **Units:** M.EUR
- **Dimensions:** `mrio_release`, `country_producing`, `sector_producing`, `unit`, `variable`
- **Measures:** `mrio_year`, `exiobase_industry_index`, `value`

### `release_defect_verdicts.csv`

- **Rows:** 10
- **Format:** csv
- **Dimensions:** `defect`, `mrio_release`, `metric`, `verdict`
- **Measures:** `mrio_year`, `value`, `of`, `world_total_meur`
