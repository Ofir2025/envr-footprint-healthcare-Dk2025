# 04_uncertainty_lenzen_ieooc - data dictionary

One row per column of every table in this folder. Units are the
table's own; `varies by row` means the table carries a `unit`
column and the value is read from there.

## Common columns

Every gold table shares this vocabulary; columns particular to one table
are described below, per table.

| Column | Meaning |
|:---|:---|
| `analysis_year` | year of the Danish expenditure data and of the MRIO background |
| `model` | MRIO release actually used (e.g. `EXIOBASE v3.8.2 IOT_2022_ixi with Danish sea-transport reallocation (Rørmose Jensen & Iliev 2022)`) - **not** v3.10.2, which this study rejects (see `docs/methods/exiobase_release_and_classification.md`) |
| `scenario` | model scenario (`baseline`, scope variants, pharma-mapping variants) |
| `consuming_country_iso3` | always `DNK` - Denmark is the final consumer in this study |
| `demand_component` | `healthcare_services`, `pharmaceuticals`, `medical_appliances` |
| `indicator` | `climate_change`, `material_extraction`, `blue_water_consumption`, `land_use`, `waste_generation` |
| `unit` | `kt CO2eq`, `kt`, `Mm3`, `km2`, or `M.EUR` for monetary rows |
| `value` | numeric value in `unit` |

## Country and region coding

`*_country_iso3` uses **ISO 3166-1 alpha-3** for the 44 EXIOBASE countries.
The five rest-of-world regions are **not countries** and keep their own
codes and names: `WA` RoW Asia and Pacific, `WL` RoW America, `WE` RoW
Europe, `WF` RoW Africa, `WM` RoW Middle East. `*_world_region` gives the
continental grouping (Europe, Asia and Pacific, America, Middle East,
Africa, Denmark).

## The two perspectives (and why they reconcile)

Every impact cell is $E_{ij} = s_i\,L_{ij}\,y_{H,j}$: pressure arising
in node *i* caused by Danish healthcare final demand for node *j*. Summing
over *i* gives the **consumption / contribution** perspective (by
purchased product); summing over *j* gives the **production / hotspot**
perspective (by producing node). Both are marginals of the same array, so
they sum to the identical total - verified to machine precision by
`analysis.validate_io_identities` (tests T5/T6). Allocating production
emissions to final demand is additive and does not double count (Wood et
al. 2018); embodied-flow tables ($\mathbf{E}_Z$) would.

## Units

Monetary values are **million euro (M.EUR)** - EXIOBASE's native unit
(`unit.txt` of the release). No US-dollar values are used anywhere in this
model; dollar figures appearing in the comparative literature (Karliner et
al. 2019, Lenzen et al. 2020, Pichler et al. 2019) are those studies' own
units and are labelled as such wherever they are quoted.

## Tables

### `uncertainty_audit.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `check` | dimension | str |  | median-1 multipliers, MRIO factor includ |
| `status` | dimension | str |  | PASS |
| `detail` | dimension | str |  | largest deviation 7.50e-04 (mrio) over 6 |
| `tolerance` | dimension | str |  | < 5e-3 |

### `uncertainty_by_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `pharma_scenario` | dimension | str |  | A |
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `unit` | dimension | str |  | ktCO2eq |
| `group` | dimension | str |  | Food and food services |
| `deterministic` | measure | float64 | varies by row | 433.74297726496013 |
| `median` | measure | float64 | varies by row | 433.41757290022554 |
| `mean` | measure | float64 | varies by row | 435.11041303383314 |
| `sd` | measure | float64 | varies by row | 36.47906149741982 |
| `cv_pct` | measure | float64 | % | 8.383863130984938 |
| `p2_5` | measure | float64 | varies by row | 368.1241102574662 |
| `p16` | measure | float64 | varies by row | 399.0758524033876 |
| `p84` | measure | float64 | varies by row | 471.16399809704774 |
| `p97_5` | measure | float64 | varies by row | 511.1307684313873 |
| `share_pct` | measure | float64 | % | 10.411541292877477 |
| `share_p2_5` | measure | float64 | % | 9.41517242901782 |
| `share_p97_5` | measure | float64 | % | 11.09866899049132 |
| `draws` | measure | int64 |  | 100000 |
| `seed` | measure | int64 | varies by row | 42 |

### `uncertainty_convergence.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `criterion` | dimension | str |  | IPCC (2000) 6.4 step 5: 95 % range deter |
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `pharma_scenario` | dimension | str |  | A |
| `draws` | measure | int64 |  | 100000 |
| `seed` | measure | int64 |  | 42 |
| `max_relative_difference_between_halves_pct` | measure | float64 | % | 0.2426106814389829 |
| `passes` | dimension | bool |  | True |

### `uncertainty_group_covariance_gwp.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `group` | dimension | str |  | Food and food services |
| `Food and food services` | measure | float64 |  | 1330.721927732554 |
| `Heat and electricity` | measure | float64 |  | 227.56302030131312 |
| `Individual travel` | measure | float64 |  | 9.409280125067482 |
| `Medical, electrical equipment and machinery` | measure | float64 |  | 351.5370790895976 |
| `Operational impacts` | measure | float64 |  | -0.6626030681830762 |
| `Other` | measure | float64 |  | 898.7815417233388 |
| `Pharmaceuticals and chemical products` | measure | float64 |  | 3502.894373093366 |
| `Services` | measure | float64 |  | 2428.7285351920427 |
| `Transport` | measure | float64 |  | 1738.1170963086447 |

### `uncertainty_mrio_correlation.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `rho_mrio` | measure | float64 |  | 1.0 |
| `interpretation` | dimension | str |  | perfect correlation (study default). Rod |
| `median` | measure | float64 |  | 4182.898095754231 |
| `p2_5` | measure | float64 |  | 3592.5654666496803 |
| `p97_5` | measure | float64 |  | 4887.488292587324 |
| `cv_pct` | measure | float64 | % | 7.9014768426454625 |
| `sigma_used` | measure | float64 |  | 0.0833550013881799 |
| `mrio_block_cv_if_not_recalibrated_pct` | measure | float64 | % | 8.379058580808774 |
| `median_group_cv_pct` | measure | float64 | % | 8.370461611866626 |
| `max_group_cv_pct` | measure | float64 | % | 26.41178559705765 |
| `draws` | measure | int64 |  | 40000 |
| `seed` | measure | int64 |  | 13 |
| `mean_over_deterministic_closed_form` | measure | float64 |  | 1.0088631501890977 |

### `uncertainty_noncarbon_bound.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `mrio_spread_multiplier` | measure | float64 |  | 1.0 |
| `basis` | dimension | str |  | carbon calibration applied unchanged (de |
| `median` | measure | float64 |  | 4183.455029529441 |
| `p2_5` | measure | float64 |  | 3588.0468545553667 |
| `p97_5` | measure | float64 |  | 4885.958471111916 |
| `cv_pct` | measure | float64 | % | 7.874316089650438 |
| `draws` | measure | int64 |  | 40000 |
| `seed` | measure | int64 |  | 23 |

### `uncertainty_parameters.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `parameter` | dimension | str |  | mrio |
| `distribution` | dimension | str |  | lognormal, median 1 |
| `gsd` | measure | float64 |  | 1.1 |
| `cv` | measure | float64 |  | 0.0835 |
| `factor_2_5pct` | measure | float64 |  | 0.8492745192964093 |
| `factor_97_5pct` | measure | float64 |  | 1.1774755715365872 |
| `source` | dimension | str |  | Lenzen et al. 2020 SI Tab. SI 7.1: relat |

### `uncertainty_ranking_probabilities.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `pharma_scenario` | dimension | str |  | A |
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `group` | dimension | str |  | Food and food services |
| `P_rank_1` | measure | float64 |  | 0.0 |
| `P_rank_2` | measure | float64 |  | 0.0 |
| `P_rank_3` | measure | float64 |  | 0.0 |

### `uncertainty_structural_scenarios.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `price_base_year` | dimension | str |  | none |
| `reference_year` | dimension | str |  | central |
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `median` | measure | float64 |  | 4184.445026956534 |
| `draws` | measure | int64 |  | 20000 |
| `seed` | measure | int64 |  | 42 |

### `uncertainty_tier1_error_propagation.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `deterministic` | measure | float64 |  | 4162.12065934072 |
| `tier1_uncertainty_pct` | measure | float64 | % | 7.955151419759845 |

### `uncertainty_totals.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `pharma_scenario` | dimension | str |  | A |
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `unit` | dimension | str |  | ktCO2eq |
| `deterministic` | measure | float64 | varies by row | 4162.1206593407205 |
| `median` | measure | float64 | varies by row | 4182.350911930765 |
| `mean` | measure | float64 | varies by row | 4197.439267800459 |
| `sd` | measure | float64 | varies by row | 332.4010476836163 |
| `cv_pct` | measure | float64 | % | 7.919138943439699 |
| `p2_5` | measure | float64 | varies by row | 3587.2530026437394 |
| `p16` | measure | float64 | varies by row | 3869.93549783091 |
| `p84` | measure | float64 | varies by row | 4524.730089433584 |
| `p97_5` | measure | float64 | varies by row | 4892.859674818636 |
| `rel_low_pct` | measure | float64 | % | -14.228789544880648 |
| `rel_high_pct` | measure | float64 | % | 16.988262770133478 |
| `mcse_median_pct` | measure | float64 | % | 0.0339896734482667 |
| `draws` | measure | int64 |  | 100000 |
| `seed` | measure | int64 | varies by row | 42 |

### `uncertainty_travel_correlation.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `rho` | measure | float64 |  | 0.0 |
| `median` | measure | float64 |  | 4188.58895234348 |
| `p2_5` | measure | float64 |  | 3620.315679190001 |
| `p97_5` | measure | float64 |  | 4850.467053355594 |
| `cv_pct` | measure | float64 | % | 7.462530663540402 |
| `draws` | measure | int64 |  | 20000 |
| `seed` | measure | int64 |  | 42 |

### `uncertainty_variance_shares.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `parameter` | dimension | str |  | mrio |
| `variance_share_pct` | measure | float64 | % | 74.70317223320149 |

### `uncertainty_variance_shares_by_correlation.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `rho_mrio` | measure | float64 |  | 1.0 |
| `mrio_variance_share_pct` | measure | float64 | % | 74.87766597855314 |
| `note` | dimension | str |  | frozen-input estimate: the share of outp |
| `draws` | measure | int64 |  | 40000 |
| `seed` | measure | int64 |  | 17 |
