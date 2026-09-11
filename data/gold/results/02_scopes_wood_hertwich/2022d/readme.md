# 02_scopes_wood_hertwich/2022d — EXIOBASE v3.8.2, Danish shipping correction, health care plus child and elder care, capital endogenised

**GHG-Protocol scope decomposition**

Of the total health-care footprint, this layer asks how much is emitted by the providers themselves, how much by the generation of the energy they buy, and how much everywhere else in the supply chain, using the partition a health system would recognise from its own reporting.

Method, equations, and verification: [`docs/methods/replications.md`, section 02](../../../../../docs/methods/replications.md#r02).

## Which model run this folder is

Variant d on the headline year: child care added to the demand vector
and consumption of fixed capital endogenised inside the Leontief
inverse. Its partition closes on `01_eriksen_replication/2022d`.

This is the variant built to be comparable with Schmidt & Merciai
(2023), whose 6,100 kt covers NACE Q including child care with capital
endogenised. At 6,495.66 kt it is 6.5 % above them, on a full pipeline
run rather than the 1.2111 post-hoc uplift that
`06_benchmarks_validation` applies to the headline; the residual
difference their model being consequential and ours attributional
cannot be removed by any boundary adjustment and remains.

## Conventions

| Item | Convention |
|:---|:---|
| Schema | star schema: dimension columns, then measure and unit |
| Industry / product codes | EXIOBASE codes **without** the `A_` / `C_` prefix |
| Countries | ISO3 (`DNK`, `DEU`, `ROU`) |
| Regions without an ISO3 code | region name (`RoW Europe`, `RoW Africa`, ...) |
| Monetary unit | M.EUR, EXIOBASE basic prices, unless a column says otherwise |
| Provenance | one row per file in `../../manifest_lineage.csv` |

## Tables

### `double_counting_ledger.csv`

- **Rows:** 10
- **Format:** csv
- **Units:** % overestimate, broadest target set (T3), -, M.EUR (in services column), kt CO2eq, kt CO2eq (deviation)
- **Dimensions:** `item`, `risk`, `test`, `unit`, `verdict`
- **Measures:** `analysis_year`, `value`

### `scope_by_continent.csv`

- **Rows:** 64
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `producing_world_region`, `scope`, `indicator`, `unit`
- **Measures:** `value`, `share_of_scope_pct`

### `scope_by_continent_and_industry_group.csv`

- **Rows:** 596
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `producing_world_region`, `producing_sector_group`, `scope`, `indicator`, `unit`
- **Measures:** `value`, `share_of_scope_pct`

### `scope_by_country.csv`

- **Rows:** 407
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `scope`, `indicator`, `unit`
- **Measures:** `value`, `share_of_scope_pct`

### `scope_by_industry_group.csv`

- **Rows:** 116
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `producing_sector_group`, `scope`, `indicator`, `unit`
- **Measures:** `value`, `share_of_scope_pct`

### `scope_by_origin_and_industry.csv`

- **Rows:** 23,740
- **Format:** csv
- **Resolution:** 1+ regions x 15+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `consuming_country_iso3`, `model`, `indicator`, `unit`, `scope`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `component_type`
- **Measures:** `analysis_year`, `value`

### `scope_by_origin_industry_top25.csv`

- **Rows:** 113
- **Format:** csv
- **Resolution:** 12+ regions x 15+ industries (sampled)
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `scope`, `indicator`, `unit`, `is_remainder`
- **Measures:** `value`, `rank`

### `scopes_by_producing_node.csv`

- **Rows:** 23,728
- **Format:** csv
- **Resolution:** 1+ regions x 15+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `consuming_country_iso3`, `model`, `indicator`, `unit`, `scope`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`
- **Measures:** `analysis_year`, `value`

### `scopes_summary_detailed.csv`

- **Rows:** 65
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `consuming_country_iso3`, `model`, `indicator`, `unit`, `scope`, `basis`
- **Measures:** `analysis_year`, `value`
