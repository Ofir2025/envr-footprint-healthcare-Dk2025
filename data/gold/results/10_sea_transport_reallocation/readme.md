# 10_sea_transport_reallocation

**Sea transport reallocation**

The submitted manuscript's most quotable finding was that transport accounts for roughly 40 % of the Danish health-care footprint. Is that a finding or an artefact?

Method, equations, and verification: [`docs/methods/replications.md`, section 10](../../../../docs/methods/replications.md#r10).

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

### `phantom_shipping_input_removed_by_industry.csv`

- **Rows:** 275
- **Format:** csv
- **Units:** M.EUR
- **Dimensions:** `country_producing`, `sector_producing`, `country_consuming`, `sector_consuming`, `unit`
- **Measures:** `background_year`, `analysis_year`, `value`

### `shipping_reallocation_diagnostics.csv`

- **Rows:** 14
- **Format:** csv
- **Units:** %, M.EUR
- **Dimensions:** `country_producing`, `sector_producing`, `quantity`, `unit`, `source`
- **Measures:** `background_year`, `analysis_year`, `value`
