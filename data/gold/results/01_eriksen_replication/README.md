# 01_eriksen_replication

**01 — Eriksen replication (the manuscript layer)**

Everything the manuscript reports, in the manuscript's own table and figure structure, for reference year 2022 on a 2022 background model.

Method, equations and verification: [`docs/methods/replications/01_eriksen_replication.md`](../../../docs/methods/replications/01_eriksen_replication.md).

## Conventions

| Item | Convention |
|---|---|
| Schema | star schema: dimension columns, then measure and unit |
| Industry / product codes | EXIOBASE codes **without** the `A_` / `C_` prefix |
| Countries | ISO3 (`DNK`, `DEU`, `ROU`) |
| Regions without an ISO3 code | region name (`RoW Europe`, `RoW Africa`, ...) |
| Monetary unit | M.EUR, EXIOBASE basic prices, unless a column says otherwise |
| Provenance | one row per file in `../MANIFEST_lineage.csv` |

## Tables

### `contribution_by_purchased_product.csv`

- **Rows:** 30,499
- **Resolution:** 3+ regions x 152+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `sector_consuming`, `analysis`, `purchased_country_iso3`, `purchased_country_name`, `purchased_world_region`, `purchased_sector_code`, `purchased_sector_name`, `purchased_sector_group`, `ghg_protocol_scope`, `indicator`, `unit`, `component_type`, `model`
- **Measures:** `value`, `analysis_year`

### `contribution_by_sector_group.csv`

- **Rows:** 101
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `purchased_sector_group`
- **Measures:** `value`

### `contribution_by_world_region.csv`

- **Rows:** 30
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `purchased_world_region`
- **Measures:** `value`

### `contribution_domestic_vs_imported.csv`

- **Rows:** 10
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `origin`
- **Measures:** `value`, `share_of_total_pct`

### `hotspot_by_producing_node.csv`

- **Rows:** 22,229
- **Resolution:** 3+ regions x 158+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `sector_consuming`, `analysis`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `ghg_protocol_scope`, `indicator`, `unit`, `component_type`, `model`
- **Measures:** `value`, `analysis_year`

### `hotspot_by_sector_group.csv`

- **Rows:** 101
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `producing_sector_group`
- **Measures:** `value`

### `hotspot_by_world_region.csv`

- **Rows:** 34
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `producing_world_region`
- **Measures:** `value`

### `hotspot_domestic_vs_imported.csv`

- **Rows:** 10
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `origin`
- **Measures:** `value`, `share_of_total_pct`

### `intensity_by_purchased_product.csv`

- **Rows:** 30,487
- **Resolution:** 3+ regions x 152+ industries (sampled)
- **Units:** kt CO2eq per MEUR
- **Dimensions:** `country_consuming`, `sector_consuming`, `analysis`, `purchased_country_iso3`, `purchased_country_name`, `purchased_world_region`, `purchased_sector_code`, `purchased_sector_name`, `purchased_sector_group`, `indicator`, `unit`, `component_type`, `model`
- **Measures:** `Total (MEUR)`, `value`, `analysis_year`

### `intensity_by_sector_group.csv`

- **Rows:** 95
- **Units:** Mm3 per MEUR, km2 per MEUR, kt CO2eq per MEUR, kt per MEUR
- **Dimensions:** `indicator`, `unit`, `purchased_sector_group`
- **Measures:** `value`

### `intensity_by_world_region.csv`

- **Rows:** 30
- **Units:** Mm3 per MEUR, km2 per MEUR, kt CO2eq per MEUR, kt per MEUR
- **Dimensions:** `indicator`, `unit`, `purchased_world_region`
- **Measures:** `value`

### `scopes_summary.csv`

- **Rows:** 10
- **Dimensions:** `Component`
- **Measures:** `kt_CO2eq`
