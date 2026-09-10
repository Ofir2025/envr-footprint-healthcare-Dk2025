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
| `check` | dimension | str |  | median-1 multipliers |
| `status` | dimension | str |  | PASS |
| `detail` | dimension | str |  | largest deviation 5.58e-04 (B_COMM) |
| `tolerance` | dimension | str |  | < 5e-3 |

### `uncertainty_convergence.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `criterion` | dimension | str |  | IPCC (2000) 6.4 step 5: 95 % range deter |
| `draws` | measure | int64 |  | 100000 |
| `max_relative_difference_between_halves_pct` | measure | float64 | % | 0.2069875486125891 |
| `passes` | dimension | bool |  | True |

### `uncertainty_group_covariance_gwp.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Food and food services |
| `Food and food services` | measure | float64 |  | 1332.6937180922905 |
| `Heat and electricity` | measure | float64 |  | 227.78876329117747 |
| `Individual travel` | measure | float64 |  | 9.746502409477351 |
| `Medical, electrical equipment and machinery` | measure | float64 |  | 615.6010151893076 |
| `Operational impacts` | measure | float64 |  | -0.660469311221808 |
| `Pharmaceuticals and chemical products` | measure | float64 |  | 5301.357216660349 |
| `Services` | measure | float64 |  | 1899.6213068982809 |
| `Transport` | measure | float64 |  | 1829.4186176545625 |
| `Unallocated` | measure | float64 |  | 900.8156798368024 |

### `uncertainty_mrio_correlation.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `rho_mrio` | measure | float64 |  | 1.0 |
| `interpretation` | dimension | str |  | perfect correlation (study default). Rod |
| `median` | measure | float64 |  | 4734.20181449759 |
| `p2_5` | measure | float64 |  | 4067.039734534131 |
| `p97_5` | measure | float64 |  | 5526.229517058415 |
| `cv_pct` | measure | float64 | % | 7.852589550926811 |
| `sigma_used` | measure | float64 |  | 0.0833550013881799 |
| `mrio_block_cv_if_not_recalibrated_pct` | measure | float64 | % | 8.379058580808772 |
| `median_group_cv_pct` | measure | float64 | % | 8.370461611866572 |
| `max_group_cv_pct` | measure | float64 | % | 26.217627095402428 |
| `median_1_lognormal_mean_inflation` | measure | float64 |  | 1.003480069557936 |

### `uncertainty_noncarbon_bound.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `mrio_spread_multiplier` | measure | float64 |  | 1.0 |
| `basis` | dimension | str |  | carbon calibration applied unchanged (de |
| `median` | measure | float64 |  | 4734.8998653164945 |
| `p2_5` | measure | float64 |  | 4062.288374613191 |
| `p97_5` | measure | float64 |  | 5518.490994729384 |
| `cv_pct` | measure | float64 | % | 7.823868741006974 |

### `uncertainty_parameters.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `parameter` | dimension | str |  | mrio |
| `distribution` | dimension | str |  | lognormal, median 1 |
| `gsd` | measure | float64 |  | 1.1 |
| `cv` | measure | float64 |  | 0.0835 |
| `factor_2_5pct` | measure | float64 |  | 0.8492719697197726 |
| `factor_97_5pct` | measure | float64 |  | 1.1774791064044678 |
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
| `median` | measure | float64 |  | 4736.9016013661985 |

### `uncertainty_tier1_error_propagation.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `deterministic` | measure | float64 |  | 4712.417605953842 |
| `tier1_uncertainty_pct` | measure | float64 | % | 7.840701455400814 |

### `uncertainty_totals.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `pharma_scenario` | dimension | str |  | A |
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `unit` | dimension | str |  | ktCO2eq |
| `deterministic` | measure | float64 | varies by row | 4712.417605953854 |
| `median` | measure | float64 | varies by row | 4733.659773313824 |
| `mean` | measure | float64 | varies by row | 4749.952065897599 |
| `sd` | measure | float64 | varies by row | 373.7860346835424 |
| `cv_pct` | measure | float64 | % | 7.869259089310578 |
| `p2_5` | measure | float64 | varies by row | 4063.64336676984 |
| `p16` | measure | float64 | varies by row | 4381.8272825066215 |
| `p84` | measure | float64 | varies by row | 5118.405571889963 |
| `p97_5` | measure | float64 | varies by row | 5531.252639583388 |
| `rel_low_pct` | measure | float64 | % | -14.154300026402945 |
| `rel_high_pct` | measure | float64 | % | 16.849391474351894 |
| `mcse_median_pct` | measure | float64 | % | 0.0359398247900488 |

### `uncertainty_travel_correlation.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `rho` | measure | float64 |  | 0.0 |
| `median` | measure | float64 |  | 4740.432219635996 |
| `p2_5` | measure | float64 |  | 4095.684785594957 |
| `p97_5` | measure | float64 |  | 5492.347473800488 |
| `cv_pct` | measure | float64 | % | 7.486835308286129 |

### `uncertainty_variance_shares.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | Global warming (ktCO2eq) |
| `parameter` | dimension | str |  | mrio |
| `variance_share_pct` | measure | float64 | % | 78.75929022214825 |

### `uncertainty_variance_shares_by_correlation.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `rho_mrio` | measure | float64 |  | 1.0 |
| `mrio_variance_share_pct` | measure | float64 | % | 78.91819521274822 |
| `note` | dimension | str |  | frozen-input estimate: the share of outp |
