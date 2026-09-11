# 02_scopes_wood_hertwich/2019_uncorrected — EXIOBASE v3.8.2 IOT_2016_ixi, no Danish shipping correction, health-care boundary, capital excluded - not variant a, which is on v3.7

**GHG-Protocol scope decomposition**

Of the total health-care footprint, this layer asks how much is emitted by the providers themselves, how much by the generation of the energy they buy, and how much everywhere else in the supply chain, using the partition a health system would recognise from its own reporting.

Method, equations, and verification: [`docs/methods/replications.md`, section 02](../../../../../docs/methods/replications.md#r02).

## Which model run this folder is

Reference year 2019 on EXIOBASE v3.8.2 `IOT_2016_ixi` with the Danish
sea-transport reallocation **not** applied - and therefore **not**
variant a, which is on v3.7. Its partition closes on
`01_eriksen_replication/2019_uncorrected` exactly: the climate `TOTAL`
of 6,416.930810 kt CO2-eq plus the self-supply loop of 1.927891 kt is
the grand total of 6,418.858701 kt published there.

This folder was withheld until 11 September 2026 on the grounds that
the uncorrected and corrected 2016 model objects descended from two
different extractions of `IOT_2016_ixi`. That diagnosis was wrong. One
extraction ever existed - the two objects' `A`, `Y`, `R`, `H` and `x`
are byte-identical - and what differed was the climate row of the
characterisation matrix, AR4 in one and AR6 in the other. With both
backgrounds on IPCC AR6 the reconciliation identity closes to the last
digit, so there is nothing left to withhold.

What the correction is worth, read across this folder and `2019c`: the
climate footprint falls from 6,416.93 to 4,107.33 kt and the transport
industry group from 46.85 % of it to 21.17 %.

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

- **Rows:** 597
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `producing_world_region`, `producing_sector_group`, `scope`, `indicator`, `unit`
- **Measures:** `value`, `share_of_scope_pct`

### `scope_by_country.csv`

- **Rows:** 410
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

- **Rows:** 23,747
- **Format:** csv
- **Resolution:** 1+ regions x 15+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `consuming_country_iso3`, `model`, `indicator`, `unit`, `scope`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `component_type`
- **Measures:** `analysis_year`, `value`

### `scope_by_origin_industry_top25.csv`

- **Rows:** 91
- **Format:** csv
- **Resolution:** 12+ regions x 16+ industries (sampled)
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `scope`, `indicator`, `unit`, `is_remainder`
- **Measures:** `value`, `rank`

### `scopes_by_producing_node.csv`

- **Rows:** 23,735
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
