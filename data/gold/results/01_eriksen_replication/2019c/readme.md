# 01_eriksen_replication/2019c — EXIOBASE v3.8.2, Danish shipping correction, health-care boundary, capital excluded - the headline configuration

**Eriksen replication, the manuscript layer**

This layer reproduces everything the manuscript reports, in the manuscript's own table and figure structure, once per reference year AND per Danish sea-transport correction state ([section 10](#r10)), in four self-describing subfolders rather than two:

Method, equations, and verification: [`docs/methods/replications.md`, section 01](../../../../../docs/methods/replications.md#r01).

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

### `contribution_by_purchased_product.csv`

- **Rows:** 30,794
- **Format:** csv
- **Resolution:** 3+ regions x 152+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `sector_consuming`, `analysis`, `purchased_country_iso3`, `purchased_country_name`, `purchased_world_region`, `purchased_sector_code`, `purchased_sector_name`, `purchased_sector_group`, `ghg_protocol_scope`, `indicator`, `unit`, `component_type`, `model`
- **Measures:** `value`, `analysis_year`

### `contribution_by_sector_group.csv`

- **Rows:** 101
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `purchased_sector_group`
- **Measures:** `value`

### `contribution_by_world_region.csv`

- **Rows:** 30
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `purchased_world_region`
- **Measures:** `value`

### `contribution_domestic_vs_imported.csv`

- **Rows:** 10
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `origin`
- **Measures:** `value`, `share_of_total_pct`

### `figure1_activity_contributions.csv`

- **Rows:** 41
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `contribution_group`
- **Measures:** `value`, `share_pct`

### `figure2_sector_contributions.csv`

- **Rows:** 37
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `hotspot_group`
- **Measures:** `value`, `share_pct`

### `figure2b_top_origin_industry_pairs.csv`

- **Rows:** 105
- **Format:** csv
- **Resolution:** 20+ regions x 42+ industries (sampled)
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `producing_country_iso3`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `indicator`, `unit`
- **Measures:** `value`, `rank`, `share_pct`, `mrio_coverage_pct`

### `figure3_geographical_origin.csv`

- **Rows:** 34
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `producing_world_region`
- **Measures:** `value`, `share_pct`

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

### `hotspot_by_producing_country_and_sector_group.csv`

- **Rows:** 3,392
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_group`, `indicator`, `unit`, `model`
- **Measures:** `value`, `analysis_year`

### `hotspot_by_producing_node.csv`

- **Rows:** 22,228
- **Format:** csv
- **Resolution:** 3+ regions x 158+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `sector_consuming`, `analysis`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `ghg_protocol_scope`, `indicator`, `unit`, `component_type`, `model`
- **Measures:** `value`, `analysis_year`

### `hotspot_by_sector_group.csv`

- **Rows:** 101
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `producing_sector_group`
- **Measures:** `value`

### `hotspot_by_world_region.csv`

- **Rows:** 34
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `producing_world_region`
- **Measures:** `value`

### `hotspot_domestic_vs_imported.csv`

- **Rows:** 10
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `origin`
- **Measures:** `value`, `share_of_total_pct`

### `intensity_by_purchased_product.csv`

- **Rows:** 30,782
- **Format:** csv
- **Resolution:** 3+ regions x 152+ industries (sampled)
- **Units:** kt CO2eq per MEUR
- **Dimensions:** `country_consuming`, `sector_consuming`, `analysis`, `purchased_country_iso3`, `purchased_country_name`, `purchased_world_region`, `purchased_sector_code`, `purchased_sector_name`, `purchased_sector_group`, `indicator`, `unit`, `component_type`, `model`
- **Measures:** `Total (MEUR)`, `value`, `analysis_year`

### `intensity_by_sector_group.csv`

- **Rows:** 95
- **Format:** csv
- **Units:** Mm3 per MEUR, km2 per MEUR, kt CO2eq per MEUR, kt per MEUR
- **Dimensions:** `indicator`, `unit`, `purchased_sector_group`
- **Measures:** `value`

### `intensity_by_world_region.csv`

- **Rows:** 30
- **Format:** csv
- **Units:** Mm3 per MEUR, km2 per MEUR, kt CO2eq per MEUR, kt per MEUR
- **Dimensions:** `indicator`, `unit`, `purchased_world_region`
- **Measures:** `value`

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
