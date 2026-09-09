# 20_production_layers

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
