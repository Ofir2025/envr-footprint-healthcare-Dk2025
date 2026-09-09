# scenarios/health_only

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

### `full_results_tables_fig1_absolute.csv`

- **Rows:** 9
- **Format:** csv
- **Dimensions:** `Contribution`
- **Measures:** `Global warming (ktCO2eq)`, `Material extraction (kt)`, `Blue water consumption (Mm3)`, `Land use (km2)`, `Waste generation (kt)`

### `full_results_tables_fig1_relative_pct.csv`

- **Rows:** 9
- **Format:** csv
- **Dimensions:** `Contribution`
- **Measures:** `Global warming (ktCO2eq)`, `Material extraction (kt)`, `Blue water consumption (Mm3)`, `Land use (km2)`, `Waste generation (kt)`

### `full_results_tables_fig2_absolute.csv`

- **Rows:** 8
- **Format:** csv
- **Dimensions:** `Hotspot`
- **Measures:** `Global warming (ktCO2eq)`, `Material extraction (kt)`, `Blue water consumption (Mm3)`, `Land use (km2)`, `Waste generation (kt)`

### `full_results_tables_fig2_relative_pct.csv`

- **Rows:** 8
- **Format:** csv
- **Dimensions:** `Hotspot`
- **Measures:** `Global warming (ktCO2eq)`, `Material extraction (kt)`, `Blue water consumption (Mm3)`, `Land use (km2)`, `Waste generation (kt)`

### `full_results_tables_fig3_absolute.csv`

- **Rows:** 7
- **Format:** csv
- **Dimensions:** `Region`
- **Measures:** `Global warming (ktCO2eq)`, `Material extraction (kt)`, `Blue water consumption (Mm3)`, `Land use (km2)`, `Waste generation (kt)`

### `full_results_tables_fig3_relative_pct.csv`

- **Rows:** 7
- **Format:** csv
- **Dimensions:** `Region`
- **Measures:** `Global warming (ktCO2eq)`, `Material extraction (kt)`, `Blue water consumption (Mm3)`, `Land use (km2)`, `Waste generation (kt)`

### `scopes_summary.csv`

- **Rows:** 10
- **Format:** csv
- **Dimensions:** `Component`
- **Measures:** `kt_CO2eq`

### `steenmeijer_table.csv`

- **Rows:** 7
- **Format:** csv
- **Dimensions:** `Unnamed: 0`, `Category group`, `Climate change (kt CO2eq)`, `Material extraction (kt)`, `Blue water consumption (Mm3)`, `Land use (km2)`, `Waste generation (kt)`, `Basic price expenditure (million euros)`
- **Measures:** none

### `table_01.csv`

- **Rows:** 7
- **Format:** csv
- **Dimensions:** `Unnamed: 0`
- **Measures:** `Global warming (ktCO2eq)`, `Material extraction (kt)`, `Blue water consumption (Mm3)`, `Land use (km2)`, `Waste generation (kt)`, `Expenditure (MEUR)`

### `table_s05_dk.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Unnamed: 0`
- **Measures:** `Healthcare footprint`, `National consumption footprint`, `Healthcare share of national consumption footprint (%)`
