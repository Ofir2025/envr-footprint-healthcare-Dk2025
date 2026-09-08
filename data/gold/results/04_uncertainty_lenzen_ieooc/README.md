# 04_uncertainty_lenzen_ieooc

**04 — Monte Carlo parameter uncertainty**

Reviewer 1's central request: how precise is the estimate, what drives its imprecision, and are the reported rankings robust?

Method, equations and verification: [`docs/methods/replications/04_uncertainty_lenzen_ieooc.md`](../../../docs/methods/replications/04_uncertainty_lenzen_ieooc.md).

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

### `uncertainty_mrio_correlation.csv`

- **Rows:** 3
- **Dimensions:** none
- **Measures:** `rho_mrio`, `interpretation`, `median`, `p2_5`, `p97_5`, `cv_pct`, `median_1_lognormal_mean_inflation`

### `uncertainty_parameters.csv`

- **Rows:** 6
- **Dimensions:** `parameter`, `source`
- **Measures:** `distribution`, `gsd`, `cv`, `factor_2_5pct`, `factor_97_5pct`

### `uncertainty_ranking_probabilities.csv`

- **Rows:** 90
- **Dimensions:** `pharma_scenario`, `indicator`, `group`
- **Measures:** `P_rank_1`, `P_rank_2`, `P_rank_3`

### `uncertainty_structural_scenarios.csv`

- **Rows:** 30
- **Dimensions:** `price_vintage`, `waste_vintage`, `indicator`
- **Measures:** `median`

### `uncertainty_totals.csv`

- **Rows:** 10
- **Units:** Mm3, km2, kt, ktCO2eq
- **Dimensions:** `pharma_scenario`, `indicator`, `unit`
- **Measures:** `deterministic`, `median`, `mean`, `sd`, `cv_pct`, `p2_5`, `p16`, `p84`, `p97_5`, `rel_low_pct`, `rel_high_pct`, `mcse_median_pct`

### `uncertainty_variance_shares.csv`

- **Rows:** 35
- **Dimensions:** `indicator`, `parameter`
- **Measures:** `variance_share_pct`
