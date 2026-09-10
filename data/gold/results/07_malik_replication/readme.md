# 07_malik_replication

**Malik replication**

How does Denmark compare with the Australian health system, on Australia's own methodological choices rather than ours; and how far upstream does the pressure occur?

Method, equations, and verification: [`docs/methods/replications.md`, section 07](../../../../docs/methods/replications.md#r07).

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

### `malik_component_intensities.csv`

- **Rows:** 15
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `model`, `consuming_country_iso3`, `indicator`, `unit`, `component`
- **Measures:** `analysis_year`, `footprint`, `expenditure_meur`, `total_intensity_per_meur`, `direct_intensity_per_meur`

### `malik_domestic_vs_full.csv`

- **Rows:** 5
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `model`, `consuming_country_iso3`, `indicator`, `unit`
- **Measures:** `analysis_year`, `full_mrio`, `domestic_only`, `domestic_share_of_full_pct`, `share_of_national_full_pct`, `share_of_national_domestic_pct`

### `malik_published_reference.csv`

- **Rows:** 4
- **Format:** csv
- **Dimensions:** `model`, `consuming_country_iso3`, `study`, `indicator`, `boundary`
- **Measures:** `analysis_year`, `total_kt`, `share_national_pct`, `direct_pct`

### `production_layers_vs_malik.csv`

- **Rows:** 3
- **Format:** csv
- **Dimensions:** `indicator`, `malik_unit`, `layer_definition`, `comparability`, `source_malik`, `source_denmark`
- **Measures:** `denmark_first_three_layers_pct`, `malik_nsw_first_three_layers_pct`, `denmark_first_layer_pct`, `malik_nsw_first_layer_pct`, `malik_total`
