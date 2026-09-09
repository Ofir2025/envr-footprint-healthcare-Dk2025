# 07_malik_replication

**07 - Malik replication and production layers**

How does Denmark compare with the Australian health system, on Australia's own methodological choices rather than ours; and how far upstream does the pressure occur?

Method, equations, and verification: [`docs/methods/replications/07_malik_replication.md`](../../../../docs/methods/replications/07_malik_replication.md).

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
- **Dimensions:** `model`, `consuming_country_iso3`, `indicator`
- **Measures:** `analysis_year`, `study`, `total_kt`, `share_national_pct`, `direct_pct`, `boundary`

### `production_layers.csv`

- **Rows:** 110
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `method`, `model`, `consuming_country_iso3`, `indicator`, `unit`, `layer`
- **Measures:** `analysis_year`, `value`, `share_pct`, `cumulative_share_pct`, `truncation_error_pct`

### `production_layers_by_producing_node.csv.gz`

- **Rows:** 444,389
- **Format:** csv
- **Resolution:** 49+ regions x 89+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `sector_consuming`, `indicator`, `unit`, `model`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`
- **Measures:** `analysis_year`, `layer`, `value`

### `production_layers_by_sector_group.csv`

- **Rows:** 1,995
- **Format:** csv
- **Units:** kt, kt CO2eq
- **Dimensions:** `method`, `model`, `consuming_country_iso3`, `sector_group`, `indicator`, `unit`
- **Measures:** `analysis_year`, `value`, `layer`

### `production_layers_domestic_vs_imported.csv`

- **Rows:** 210
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `origin`
- **Measures:** `layer`, `value`, `share_of_total_pct`

### `production_layers_vs_malik.csv`

- **Rows:** 3
- **Format:** csv
- **Dimensions:** `indicator`, `malik_unit`, `layer_definition`, `source_malik`, `source_denmark`
- **Measures:** `denmark_first_three_layers_pct`, `malik_nsw_first_three_layers_pct`, `denmark_first_layer_pct`, `malik_nsw_first_layer_pct`, `malik_total`, `comparability`
