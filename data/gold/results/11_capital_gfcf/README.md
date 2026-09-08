# 11_capital_gfcf

**11 - Capital endogenisation**

Steenmeijer, Eckelman and the NHS reports all **exclude** capital: the Leontief matrix carries current inputs only, so hospital buildings, scanners and IT systems never enter the supply chain. Wood & Hertwich and Södersten et al. both show this is the largest single boundary omission for service sectors. How large is it here?

Method, equations and verification: [`docs/methods/replications/11_capital_gfcf.md`](../../../docs/methods/replications/11_capital_gfcf.md).

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

### `capital_asset_mix.csv`

- **Rows:** 7
- **Units:** M.EUR
- **Dimensions:** `country_consuming`, `sector_consuming`, `asset`, `exiobase_products`, `unit`, `source`
- **Measures:** `consumption_of_fixed_capital_meur`, `share_pct`

### `capital_diagnostics.csv`

- **Rows:** 10
- **Units:** -, M.EUR
- **Dimensions:** `quantity`, `unit`, `source`
- **Measures:** `value`

### `capital_endogenised_by_producing_node.csv.gz`

- **Rows:** 6,870
- **Resolution:** 41+ regions x 86+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `country_consuming`, `indicator`, `unit`, `model`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`
- **Measures:** `treatment`, `value`

### `capital_endogenised_domestic_vs_imported.csv`

- **Rows:** 2
- **Units:** kt CO2eq
- **Dimensions:** `indicator`, `unit`, `origin`
- **Measures:** `value`, `share_of_total_pct`

### `capital_endogenised_sodersten.csv`

- **Rows:** 5
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `country_consuming`, `sector_consuming`, `indicator`, `unit`, `method`, `model`
- **Measures:** `analysis_year`, `baseline_capital_excluded`, `endogenised_sodersten`, `change`, `change_pct`, `per_capita_endogenised`, `kbar_year`, `structure_assumption`

### `capital_scenarios_by_indicator.csv`

- **Rows:** 15
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `country_consuming`, `sector_consuming`, `scenario`, `indicator`, `unit`, `per_capita_unit`, `model`, `note`
- **Measures:** `value`, `delta_vs_baseline`, `pct_vs_baseline`, `per_capita`, `analysis_year`
