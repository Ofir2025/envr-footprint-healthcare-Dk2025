# 03_cabernard_target_scope3

**03 — Target-sector scope 3 without double counting**

A different question from the headline, and the distinction is the point of the folder.

Method, equations and verification: [`docs/methods/replications/03_cabernard_target_scope3.md`](../../../docs/methods/replications/03_cabernard_target_scope3.md).

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

### `cabernard_domestic_vs_imported.csv`

- **Rows:** 6
- **Units:** kt CO2eq
- **Dimensions:** `target_set`, `indicator`, `unit`, `origin`
- **Measures:** `value`, `share_of_total_pct`

### `cabernard_target_scope3.csv`

- **Rows:** 3
- **Dimensions:** `target`, `note`
- **Measures:** `analysis_year`, `n_target_nodes`, `e_T_naive_MtCO2e`, `e_T_wdc_MtCO2e`, `double_counting_factor_f_T`, `overestimate_vs_correct_pct`, `complement_identity_rel_dev`

### `cabernard_target_scope3_by_producing_node.csv.gz`

- **Rows:** 20,610
- **Resolution:** 44+ regions x 89+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `target_set`, `indicator`, `unit`, `model`, `quantity`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`
- **Measures:** `n_target_nodes`, `value`
