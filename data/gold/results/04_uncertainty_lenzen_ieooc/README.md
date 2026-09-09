# 04_uncertainty_lenzen_ieooc

**04: Monte Carlo parameter uncertainty**

Reviewer 1's central request: how precise is the estimate, what drives its imprecision, and do the reported rankings hold across draws?

Method, equations, and verification: [`docs/methods/replications/04_uncertainty_lenzen_ieooc.md`](../../../docs/methods/replications/04_uncertainty_lenzen_ieooc.md).

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

### `uncertainty_audit.csv`

- **Rows:** 19
- **Format:** csv
- **Dimensions:** `check`
- **Measures:** `status`, `detail`, `tolerance`

### `uncertainty_convergence.csv`

- **Rows:** 1
- **Format:** csv
- **Dimensions:** none
- **Measures:** `criterion`, `draws`, `max_relative_difference_between_halves_pct`, `passes`

### `uncertainty_group_covariance_gwp.csv`

- **Rows:** 9
- **Format:** csv
- **Dimensions:** none
- **Measures:** `Unnamed: 0`, `Food and food services`, `Heat and electricity`, `Individual travel`, `Medical, electrical equipment and machinery`, `Operational impacts`, `Pharmaceuticals and chemical products`, `Services`, `Transport`, `Unallocated`

### `uncertainty_mrio_correlation.csv`

- **Rows:** 3
- **Format:** csv
- **Dimensions:** none
- **Measures:** `rho_mrio`, `interpretation`, `median`, `p2_5`, `p97_5`, `cv_pct`, `sigma_used`, `mrio_block_cv_if_not_recalibrated_pct`, `median_group_cv_pct`, `max_group_cv_pct`, `median_1_lognormal_mean_inflation`

### `uncertainty_noncarbon_bound.csv`

- **Rows:** 9
- **Format:** csv
- **Dimensions:** `indicator`, `basis`
- **Measures:** `mrio_spread_multiplier`, `median`, `p2_5`, `p97_5`, `cv_pct`

### `uncertainty_parameters.csv`

- **Rows:** 6
- **Format:** csv
- **Dimensions:** `parameter`, `source`
- **Measures:** `distribution`, `gsd`, `cv`, `factor_2_5pct`, `factor_97_5pct`

### `uncertainty_ranking_probabilities.csv`

- **Rows:** 90
- **Format:** csv
- **Dimensions:** `pharma_scenario`, `indicator`, `group`
- **Measures:** `P_rank_1`, `P_rank_2`, `P_rank_3`

### `uncertainty_structural_scenarios.csv`

- **Rows:** 30
- **Format:** csv
- **Dimensions:** `price_vintage`, `waste_vintage`, `indicator`
- **Measures:** `median`

### `uncertainty_tier1_error_propagation.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `indicator`
- **Measures:** `deterministic`, `tier1_uncertainty_pct`

### `uncertainty_totals.csv`

- **Rows:** 10
- **Format:** csv
- **Units:** Mm3, km2, kt, ktCO2eq
- **Dimensions:** `pharma_scenario`, `indicator`, `unit`
- **Measures:** `deterministic`, `median`, `mean`, `sd`, `cv_pct`, `p2_5`, `p16`, `p84`, `p97_5`, `rel_low_pct`, `rel_high_pct`, `mcse_median_pct`

### `uncertainty_variance_shares.csv`

- **Rows:** 35
- **Format:** csv
- **Dimensions:** `indicator`, `parameter`
- **Measures:** `variance_share_pct`

### `uncertainty_variance_shares_by_correlation.csv`

- **Rows:** 3
- **Format:** csv
- **Dimensions:** `note`
- **Measures:** `rho_mrio`, `mrio_variance_share_pct`
