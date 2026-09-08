# 08 - Lenzen KPI set

**Gold folder** `data/gold/results/08_lenzen_replication/`
**Module** `analysis.lenzen_replication`
**Source** Lenzen, Malik, Li et al. (2020), *The environmental footprint of health care:
a global assessment*, Lancet Planet Health 4:e271-79, and its SI §§2, 5

## Question this layer answers

This layer reproduces for Denmark every indicator Lenzen et al. publish per country,
so our result can be placed directly beside their published Danish row.

## Method

Their equations, as implemented:

$$F = q\,L\,y^{*} \qquad \text{footprint}$$
$$q = Q\,\hat{x}^{-1} \qquad \text{direct intensities}$$
$$S_m = \frac{\sum_{n \le m} q A^n y^{*}}{F} \qquad \text{cumulative layer share (SI §5)}$$
$$TE_m = 1 - S_m \qquad \text{truncation error}$$
$$\text{import share} = 1 - \frac{\mathrm{tr}(\hat{q}\,L\,\hat{y^{*}})}{F}$$

The trace form of the import share is theirs: $\mathrm{tr}(\hat{q} L \hat{y^*})$ picks out
the diagonal, i.e. pressure arising in the same node that is being supplied, which for a
single-country demand vector is the domestic part.

Each KPI is split into **direct**, **first-order supplier**, and **higher-order**
contributions, which is the decomposition their table reports.

### Indicator correspondence

Their seven indicator families are matched to EXIOBASE stressor rows explicitly, and the
mapping is carried in the output's `notes` column rather than left in the code:

| Lenzen family | EXIOBASE rows used |
|---|---|
| climate change | CO₂, CH₄, N₂O, SF₆, HFC, PFC on AR6 |
| PM | PM10 rows (matching their "PM10 or less") |
| NOₓ | NOx rows |
| SO₂ | SO2 combustion + SOx non-combustion |
| reactive nitrogen | NH₃ + NOx + N to water |
| water | blue water consumption |
| land | land use |

Where a family cannot be supported on EXIOBASE it is reported as unsupported rather than
approximated.

## Data requirements

This layer needs $Q$, $x$, $A$, $L$, and $y^{*}$ from [00](00_core_footprint.md), plus
their published Danish row for comparison. `lenzen_expenditure_base_check.csv` documents
that our expenditure base and theirs are the same concept before any comparison is
drawn.

## Deviations from the source, stated

- Their model is **Eora**, ours is EXIOBASE. Differences in the Danish result therefore
  carry a model-family component that cannot be removed; see the family analysis in
  [06](06_benchmarks_validation.md).
- Their per-country health expenditure comes from WHO GHED; ours from Statistics Denmark.
  The base is checked rather than assumed equivalent.
- Their SI reports uncertainty by propagating Eora's own parameter distributions. EXIOBASE
  publishes none, so we use their Danish result as the calibration target for our own
  Monte Carlo instead ([04](04_uncertainty_lenzen_ieooc.md)).

## Outputs

| File | Content |
|---|---|
| `lenzen_kpi_set.csv` | every KPI with total, direct, first-order, higher-order, and truncation |
| `lenzen_kpi_by_producing_node.csv.gz` | each KPI at full node detail |
| `lenzen_kpi_domestic_vs_imported.csv` | origin split per KPI |
| `lenzen_expenditure_base_check.csv` | the base comparison, before any KPI is compared |

## Verification

Direct + first-order + higher-order sums to the total for every KPI; the truncation error
is reported rather than assumed negligible.
