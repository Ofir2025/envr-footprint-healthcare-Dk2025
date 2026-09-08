# 09_vintage_diagnostics

**09 - EXIOBASE vintage defects**

Which EXIOBASE vintage can carry this study? Rørmose Jensen & Iliev argue EXIOBASE's Danish block misallocates output between industries. This module turns that argument into a reproducible test rather than accepting or dismissing it.

Method, equations and verification: [`docs/methods/replications/09_vintage_diagnostics.md`](../../../docs/methods/replications/09_vintage_diagnostics.md).

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

### `dk_block_vs_national_accounts.csv`

- **Rows:** 65
- **Units:** M.EUR
- **Dimensions:** `mrio_vintage`, `country_producing`, `sector_producing`, `exiobase_industry_index`, `unit`, `source_national_accounts`
- **Measures:** `mrio_year`, `dst_nace_prefixes`, `exiobase_output_meur`, `national_accounts_output_meur`, `ratio_exiobase_over_dst`

### `industry33_output_by_region.csv`

- **Rows:** 245
- **Units:** M.EUR
- **Dimensions:** `mrio_vintage`, `country_producing`, `sector_producing`, `unit`
- **Measures:** `mrio_year`, `exiobase_industry_index`, `value`, `variable`

### `vintage_defect_verdicts.csv`

- **Rows:** 10
- **Dimensions:** `defect`, `mrio_vintage`, `metric`, `verdict`
- **Measures:** `mrio_year`, `value`, `of`, `world_total_meur`
