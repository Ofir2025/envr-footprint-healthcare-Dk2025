# 02_scopes_wood_hertwich

**02 — GHG-Protocol scope decomposition**

Of the total health-care footprint, how much is emitted by the providers themselves, how much by the generation of the energy they buy, and how much everywhere else in the supply chain — using the partition a health system would recognise from its own reporting.

Method, equations and verification: [`docs/methods/replications/02_scopes_wood_hertwich.md`](../../../docs/methods/replications/02_scopes_wood_hertwich.md).

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

### `double_counting_ledger.csv`

- **Rows:** 10
- **Units:** % overestimate, broadest target set (T3), -, M.EUR (in services column), kt CO2eq, kt CO2eq (deviation)
- **Dimensions:** `item`, `risk`, `test`, `unit`, `verdict`
- **Measures:** `analysis_year`, `value`

### `scope_by_continent.csv`

- **Rows:** 14
- **Units:** kt CO2eq
- **Dimensions:** `producing_world_region`, `scope`, `indicator`, `unit`
- **Measures:** `value`, `share_of_scope_pct`

### `scope_by_continent_and_industry_group.csv`

- **Rows:** 130
- **Units:** kt CO2eq
- **Dimensions:** `producing_world_region`, `producing_sector_group`, `scope`, `indicator`, `unit`
- **Measures:** `value`, `share_of_scope_pct`

### `scope_by_country.csv`

- **Rows:** 96
- **Units:** kt CO2eq
- **Dimensions:** `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `scope`, `indicator`, `unit`
- **Measures:** `value`, `share_of_scope_pct`

### `scope_by_industry_group.csv`

- **Rows:** 25
- **Units:** kt CO2eq
- **Dimensions:** `producing_sector_group`, `scope`, `indicator`, `unit`
- **Measures:** `value`, `share_of_scope_pct`

### `scope_by_origin_and_industry.csv`

- **Rows:** 7,346
- **Resolution:** 1+ regions x 15+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `consuming_country_iso3`, `model`, `indicator`, `unit`, `scope`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `component_type`
- **Measures:** `analysis_year`, `value`

### `scope_by_origin_industry_top25.csv`

- **Rows:** 32
- **Resolution:** 11+ regions x 13+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `scope`, `indicator`, `unit`
- **Measures:** `value`, `rank`, `is_remainder`

### `scopes_by_producing_node.csv`

- **Rows:** 23,726
- **Resolution:** 1+ regions x 15+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `consuming_country_iso3`, `model`, `indicator`, `unit`, `scope`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`
- **Measures:** `analysis_year`, `value`

### `scopes_summary_detailed.csv`

- **Rows:** 40
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `consuming_country_iso3`, `model`, `indicator`, `unit`, `scope`, `basis`
- **Measures:** `analysis_year`, `value`
