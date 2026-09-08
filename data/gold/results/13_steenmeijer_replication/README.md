# 13_steenmeijer_replication

**13 - Steenmeijer replication**

Denmark placed beside every number the Dutch study published, in their own table structure, for every impact category - not only climate. That is what FAIR replication means here.

Method, equations, and verification: [`docs/methods/replications/13_steenmeijer_replication.md`](../../../docs/methods/replications/13_steenmeijer_replication.md).

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

### `national_shares_dk_vs_nl.csv`

- **Rows:** 5
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `comparability_note`, `source_netherlands`, `source_denmark`
- **Measures:** `netherlands_national`, `netherlands_health_share_pct`, `denmark_national`, `denmark_health_share_pct`, `share_difference_pp`

### `template_table_dk_vs_nl.csv`

- **Rows:** 35
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `per_capita_unit`, `source_netherlands`, `source_denmark`
- **Measures:** `analysis_year_denmark`, `reference_year_netherlands`, `table_row`, `netherlands_2016`, `denmark_2022`, `netherlands_per_capita`, `denmark_per_capita`, `dk_as_pct_of_nl_per_capita`
