# 12 - Full impact-category profile

**Gold folder** `data/gold/results/12_impact_categories_full/`
**Module** `analysis.impact_categories_full`
**Source** DESIRE FP7 characterisation workbook
(`characterisation_desire_version3_4_adapted.xlsx`), carrying CML 1999, USEtox,
EcoIndicator 99 and the ILCD recommended factors

## Question this layer answers

The study's headline uses six indicators. The studies it is benchmarked against use
different and wider sets - Eckelman & Sherman report nine TRACI categories plus DALYs,
Malik et al. several environmental impacts, Lenzen et al. a long KPI list. Comparing one
stressor at a time is not a replication.

## Method

$$f_c = C_c\,S\,L\,y_H \quad \text{for every characterisation row } c$$

The workbook contains **121 emission categories** across four methods, plus resource and
material categories. The pipeline previously used six. This module computes them all once,
so every replication layer selects the subset it needs from a single consistent
calculation rather than each rebuilding its own characterisation.

The ILCD block includes **endpoint factors in DALYs** for climate change, ozone depletion,
human toxicity (cancer and non-cancer), particulate matter and photochemical ozone
formation, which is what makes the Eckelman comparison ([14](14_eckelman_replication.md))
possible at all.

### Quality flagging, not silent use

Three workbook rows were tested and found unusable, and are flagged rather than dropped
silently:

| Row | Defect |
|---|---|
| an ILCD endpoint | numerically identical to its own midpoint |
| photochemical ozone endpoint | two orders of magnitude from its published damage factor |
| SF₆ factor | matches no IPCC assessment |

Each carries a `quality_flag` in the output. **Ozone depletion was retracted** from the
study's reported set on this basis.

`stressor_totals_uncharacterised.csv` reports the stressor mass that **no** method
characterises, so the coverage of the characterisation is visible rather than assumed
complete.

## Data requirements

$S$, $L$, $y_H$ from [00](00_core_footprint.md); the DESIRE workbook; the EXIOBASE
stressor list, whose order the workbook columns must match.

## Deviations from the source, stated

- The climate row is **not** taken from the workbook, which carries AR4 factors
  (CH₄ = 25, N₂O = 298) under a sheet labelled "CML 1999". It is rebuilt on IPCC AR6 from
  the stressor names - see [15](15_gwp_vintage.md).
- DESIRE is a 2014-vintage file with no water-scarcity, land-biodiversity or
  mineral-resource categories. That gap is the reason for
  [16](16_impact_world_plus.md), which is current and openly licensed.

## Outputs

`impact_categories_all_methods.csv` (97 usable categories, health-care and national, with
the health share of each), `impact_categories_by_producing_node.csv.gz`,
`impact_categories_by_sector_group.csv`, `impact_categories_domestic_vs_imported.csv`
(carrying `quality_flag`), `stressor_totals_uncharacterised.csv`.

## Verification

`analysis.audit_consistency` C2: 97 categories, maximum relative deviation between detail
and aggregate 4.41 × 10⁻¹⁴.
