# 02_scopes_wood_hertwich/2022_uncorrected — EXIOBASE v3.8.2 IOT_2022_ixi, no Danish shipping correction, health-care boundary, capital excluded

**GHG-Protocol scope decomposition**

Of the total health-care footprint, this layer asks how much is emitted by the providers themselves, how much by the generation of the energy they buy, and how much everywhere else in the supply chain, using the partition a health system would recognise from its own reporting.

Method, equations, and verification: [`docs/methods/replications.md`, section 02](../../../../../docs/methods/replications.md#r02).

## Which model run this folder is

Reference year 2022 on EXIOBASE v3.8.2 `IOT_2022_ixi` with the Danish
sea-transport reallocation **not** applied - the comparison run, not
the headline, and not a lettered variant. Its partition closes on
`01_eriksen_replication/2022_uncorrected` exactly: the climate `TOTAL`
of 6,085.494934 kt CO2-eq plus the self-supply loop of 1.833390 kt is
the grand total of 6,063.932424 kt published there.

What the correction is worth, read across this folder and `2022c`: the
climate footprint falls from 6,062.10 to 4,650.24 kt, and the
transport industry group falls from 32.31 % of it to 14.94 %. The
ledger's MRIO decomposition row moves from 5,318.307735 to
3,906.446070 kt on the same comparison. Nothing in this folder is on
the headline basis, and no manuscript number is taken from it.

Its purpose is figures 3 to 6 of the `2022_uncorrected` figure
variant. Until this layer carried the configuration in its folder
name, those four figures were drawn from the shipping-corrected
tables and were byte-identical to the corrected variant's.

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

- **Rows:** 23,738
- **Format:** csv
- **Resolution:** 1+ regions x 15+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `consuming_country_iso3`, `model`, `indicator`, `unit`, `scope`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `component_type`
- **Measures:** `analysis_year`, `value`

### `scope_by_origin_industry_top25.csv`

- **Rows:** 116
- **Format:** csv
- **Resolution:** 12+ regions x 13+ industries (sampled)
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `scope`, `indicator`, `unit`, `is_remainder`
- **Measures:** `value`, `rank`

### `scopes_by_producing_node.csv`

- **Rows:** 23,726
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
