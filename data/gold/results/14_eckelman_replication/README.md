# 14_eckelman_replication

**14 - Eckelman & Sherman replication**

Denmark placed on the nine-category frame of the most-cited health-sector footprint study, including its health-damage estimate in DALYs.

Method, equations, and verification: [`docs/methods/replications/14_eckelman_replication.md`](../../../docs/methods/replications/14_eckelman_replication.md).

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

### `damage_daly_dk_vs_us.csv`

- **Rows:** 4
- **Dimensions:** `damage_category`, `us_method`, `dk_method`
- **Measures:** `us_daly`, `us_daly_per_1000`, `dk_daly`, `dk_daly_per_1000`

### `nine_categories_dk_vs_us.csv`

- **Rows:** 9
- **Dimensions:** `us_unit`, `dk_method`, `dk_indicator`, `dk_unit`, `source_us`, `source_dk`
- **Measures:** `analysis_year_denmark`, `reference_year_us`, `eckelman_code`, `effect_category`, `us_health_care`, `us_national`, `us_share_of_national_pct`, `dk_health_care`, `dk_national`, `dk_share_of_national_pct`, `share_difference_pp`, `comparability`
