# 02_scopes_wood_hertwich/2019_shipping_corrected

**GHG-Protocol scope decomposition**

Of the total health-care footprint, this layer asks how much is emitted by the providers themselves, how much by the generation of the energy they buy, and how much everywhere else in the supply chain, using the partition a health system would recognise from its own reporting.

Method, equations, and verification: [`docs/methods/replications.md`, section 02](../../../../../docs/methods/replications.md#r02).

## Which model run this folder is

The folder name carries both axes, as `01_eriksen_replication` does:
reference year 2019 on EXIOBASE v3.8.2 `IOT_2016_ixi`, with the Danish
sea-transport reallocation applied. Its partition closes on
`01_eriksen_replication/2019_shipping_corrected` exactly: the climate
`TOTAL` of 4,052.850438 kt CO2-eq plus the self-supply loop of
1.921622 kt is the grand total of 4,054.772061 kt that
`scopes_summary.csv` publishes there.

The bottom-up items are 2019's own: anaesthetic gases 12.470055 kt,
commuting 327.944600 kt, patient and visitor travel 293.475319 kt.

## Why there is no 2019_uncorrected companion

The other three runs of the 2x2 are published; this year's uncorrected
one is not, and it is withheld rather than missing by accident. The
2016 background it needs cannot currently be paired with
`01_eriksen_replication/2019_uncorrected`: the uncorrected and
shipping-corrected 2016 model objects on disk descend from two
different extractions of `IOT_2016_ixi`, whose climate intensity rows
disagree on 6,779 of 7,987 nodes by up to 0.4 % each. Rebuilding the
uncorrected background moves that run's grand total from 6,360.386367
to 6,418.858701 kt, so a scope partition built on it would miss this
layer's own reconciliation identity by 58.47 kt. See
`docs/revision/defects_and_fixes.md`.

The shipping-corrected 2019 run is unaffected: it reproduces from the
objects on disk byte for byte, its background included.

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

- **Rows:** 90
- **Format:** csv
- **Resolution:** 11+ regions x 17+ industries (sampled)
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
