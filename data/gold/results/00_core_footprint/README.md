# 00_core_footprint

**00 - Core footprint**

What environmental pressure, anywhere in the world, is caused by Danish health-care final expenditure, and where does it physically arise?

Method, equations, and verification: [`docs/methods/replications/00_core_footprint.md`](../../../docs/methods/replications/00_core_footprint.md).

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

### `expenditure_summary.csv`

- **Rows:** 3
- **Units:** M.EUR
- **Dimensions:** `consuming_country_iso3`, `model`, `scenario`, `demand_component`, `unit`
- **Measures:** `analysis_year`, `basic_price_expenditure_meur`, `y_H_meur`

### `expenditure_vector_detail.csv`

- **Rows:** 6,186
- **Resolution:** 1+ regions x 152+ industries (sampled)
- **Units:** M.EUR
- **Dimensions:** `consuming_country_iso3`, `model`, `scenario`, `demand_component`, `purchased_country_iso3`, `purchased_country_name`, `purchased_world_region`, `purchased_sector_code`, `purchased_sector_name`, `purchased_sector_group`, `unit`, `note`
- **Measures:** `analysis_year`, `value`

### `extended_indicators_by_producing_node.csv`

- **Rows:** 126,402
- **Resolution:** 1+ regions x 158+ industries (sampled)
- **Units:** kt
- **Dimensions:** `consuming_country_iso3`, `model`, `scenario`, `indicator`, `unit`, `demand_component`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`
- **Measures:** `analysis_year`, `value`

### `extended_indicators_summary.csv`

- **Rows:** 24
- **Units:** kt
- **Dimensions:** `consuming_country_iso3`, `model`, `scenario`, `indicator`, `unit`, `demand_component`
- **Measures:** `analysis_year`, `n_stressor_rows`, `value`

### `footprint_bilateral_producer_x_purchase.csv.gz`

- **Rows:** 2,351,620
- **Resolution:** 1+ regions x 63+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `consuming_country_iso3`, `model`, `scenario`, `indicator`, `unit`, `demand_component`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `purchased_country_iso3`, `purchased_country_name`, `purchased_world_region`, `purchased_sector_code`, `purchased_sector_name`, `purchased_sector_group`
- **Measures:** `analysis_year`, `value`

### `footprint_by_producing_node.csv`

- **Rows:** 66,645
- **Resolution:** 1+ regions x 158+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `consuming_country_iso3`, `model`, `scenario`, `indicator`, `unit`, `demand_component`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`
- **Measures:** `analysis_year`, `value`

### `footprint_by_purchased_product.csv`

- **Rows:** 30,930
- **Resolution:** 1+ regions x 152+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `consuming_country_iso3`, `model`, `scenario`, `indicator`, `unit`, `demand_component`, `purchased_country_iso3`, `purchased_country_name`, `purchased_world_region`, `purchased_sector_code`, `purchased_sector_name`, `purchased_sector_group`
- **Measures:** `analysis_year`, `value`

### `national_footprint_by_producing_node.csv`

- **Rows:** 22,215
- **Resolution:** 1+ regions x 158+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `scope`, `consuming_country_iso3`, `model`, `indicator`, `unit`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`
- **Measures:** `analysis_year`, `value`

### `national_footprint_by_purchased_product.csv`

- **Rows:** 30,562
- **Resolution:** 1+ regions x 152+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `scope`, `consuming_country_iso3`, `model`, `indicator`, `unit`, `purchased_country_iso3`, `purchased_country_name`, `purchased_world_region`, `purchased_sector_code`, `purchased_sector_name`, `purchased_sector_group`
- **Measures:** `analysis_year`, `value`

### `national_totals_summary.csv`

- **Rows:** 5
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `scope`, `consuming_country_iso3`, `model`, `indicator`, `unit`
- **Measures:** `analysis_year`, `national_footprint`, `national_supply_chain`, `national_direct_households`, `healthcare_footprint_mrio`, `healthcare_share_pct`

### `national_vs_healthcare_by_product_group.csv`

- **Rows:** 815
- **Resolution:** 1+ regions x 163+ industries (sampled)
- **Units:** Mm3, kt, kt CO2eq
- **Dimensions:** `scope`, `consuming_country_iso3`, `model`, `indicator`, `unit`, `sector_code`, `sector_name`, `sector_group`
- **Measures:** `analysis_year`, `national`, `healthcare`, `healthcare_vs_sector_ratio_pct`, `sector_share_of_national_pct`
