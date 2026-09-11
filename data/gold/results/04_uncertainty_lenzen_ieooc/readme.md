# 04_uncertainty_lenzen_ieooc

**Monte Carlo parameter uncertainty**

Reviewer 1's central request: how precise is the estimate, what drives its imprecision, and do the reported rankings hold across draws?

Method, equations, and verification: [`docs/methods/replications.md`, section 04](../../../../docs/methods/replications.md#r04).

## Ranges on the reported estimates, not only on the total

`uncertainty_by_group.csv` carries the mean, standard deviation,
coefficient of variation and 95 % interval of every contribution group
in every indicator - 90 rows - beside the interval on that group's
SHARE of the footprint. The two answer different questions and the
second cannot be derived from the first.

Reviewer 1 asked for "the resulting ranges for the main impact
estimates". A range on the total alone does not answer that: the
groups do not vary independently, so a reader cannot infer a group's
range from the total's. They share the MRIO multiplier, which is why
seven of the nine climate groups carry a coefficient of variation of
8.4 % - the MRIO block's own - and why their shares are far tighter
than their levels: the shared factor cancels in the ratio.

Two groups are not like the others, and that is the finding. Individual
travel carries a CV of **26.3 %** against the 8.4 % of the MRIO-driven
groups, because commuting and patient and visitor travel are bottom-up
terms with uncertainties of their own rather than a share of the MRIO
block; operational impacts carries 9.1 % for the same reason, smaller
because the direct-emissions account is tighter. In share terms
pharmaceuticals run 33.9 % to 39.4 % while individual travel runs
8.4 % to 20.9 %, so the statement that pharmaceuticals lead is robust
and the position of travel in the ranking is not - which is what
`uncertainty_ranking_probabilities.csv` quantifies.

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

### `uncertainty_audit.csv`

- **Rows:** 19
- **Format:** csv
- **Dimensions:** `check`, `status`, `detail`, `tolerance`
- **Measures:** none

### `uncertainty_by_group.csv`

- **Rows:** 90
- **Format:** csv
- **Units:** Mm3, km2, kt, ktCO2eq
- **Dimensions:** `pharma_scenario`, `indicator`, `unit`, `group`
- **Measures:** `deterministic`, `median`, `mean`, `sd`, `cv_pct`, `p2_5`, `p16`, `p84`, `p97_5`, `share_pct`, `share_p2_5`, `share_p97_5`, `draws`, `seed`

### `uncertainty_convergence.csv`

- **Rows:** 10
- **Format:** csv
- **Dimensions:** `criterion`, `indicator`, `pharma_scenario`, `passes`
- **Measures:** `draws`, `seed`, `max_relative_difference_between_halves_pct`

### `uncertainty_group_covariance_gwp.csv`

- **Rows:** 9
- **Format:** csv
- **Dimensions:** `group`
- **Measures:** `Food and food services`, `Heat and electricity`, `Individual travel`, `Medical, electrical equipment and machinery`, `Operational impacts`, `Other`, `Pharmaceuticals and chemical products`, `Services`, `Transport`

### `uncertainty_mrio_correlation.csv`

- **Rows:** 3
- **Format:** csv
- **Dimensions:** `interpretation`
- **Measures:** `rho_mrio`, `median`, `p2_5`, `p97_5`, `cv_pct`, `sigma_used`, `mrio_block_cv_if_not_recalibrated_pct`, `median_group_cv_pct`, `max_group_cv_pct`, `draws`, `seed`, `mean_over_deterministic_closed_form`

### `uncertainty_noncarbon_bound.csv`

- **Rows:** 9
- **Format:** csv
- **Dimensions:** `indicator`, `basis`
- **Measures:** `mrio_spread_multiplier`, `median`, `p2_5`, `p97_5`, `cv_pct`, `draws`, `seed`

### `uncertainty_parameters.csv`

- **Rows:** 6
- **Format:** csv
- **Dimensions:** `parameter`, `distribution`, `source`
- **Measures:** `gsd`, `cv`, `factor_2_5pct`, `factor_97_5pct`

### `uncertainty_ranking_probabilities.csv`

- **Rows:** 90
- **Format:** csv
- **Dimensions:** `pharma_scenario`, `indicator`, `group`
- **Measures:** `P_rank_1`, `P_rank_2`, `P_rank_3`

### `uncertainty_structural_scenarios.csv`

- **Rows:** 30
- **Format:** csv
- **Dimensions:** `price_base_year`, `reference_year`, `indicator`
- **Measures:** `median`, `draws`, `seed`

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
- **Measures:** `deterministic`, `median`, `mean`, `sd`, `cv_pct`, `p2_5`, `p16`, `p84`, `p97_5`, `rel_low_pct`, `rel_high_pct`, `mcse_median_pct`, `draws`, `seed`

### `uncertainty_travel_correlation.csv`

- **Rows:** 3
- **Format:** csv
- **Dimensions:** none
- **Measures:** `rho`, `median`, `p2_5`, `p97_5`, `cv_pct`, `draws`, `seed`

### `uncertainty_variance_shares.csv`

- **Rows:** 35
- **Format:** csv
- **Dimensions:** `indicator`, `parameter`
- **Measures:** `variance_share_pct`

### `uncertainty_variance_shares_by_correlation.csv`

- **Rows:** 3
- **Format:** csv
- **Dimensions:** `note`
- **Measures:** `rho_mrio`, `mrio_variance_share_pct`, `draws`, `seed`
