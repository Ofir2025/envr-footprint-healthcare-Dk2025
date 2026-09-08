# 06 - Benchmarks and the standing consistency audit

**Gold folder** `data/gold/results/06_benchmarks_validation/`
**Modules** `analysis.danish_healthcare_benchmark`, `analysis.figaro_benchmarks`,
`analysis.figaro_recipe_validation`, `analysis.demand_vector_consistency`,
`analysis.audit_consistency`
**Sources** Schmidt & Merciai (2023), *GHG emissions from Danish consumption 2016*;
Eurostat `env_ac_ghgfp` (FIGARO); Statistics Denmark AFTRYK

## Question this layer answers

Is the result right? Two independent tests answer it: agreement with published Danish
footprints, and internal consistency across the study's own outputs.

## Method

### Boundary-matched benchmark against the only comparable published study

Schmidt & Merciai report Danish *Health and social work services* at 6.1 Mt CO₂e,
1.07 t per capita, 8.3 % of the national total, on the EXIOBASE v4 hybrid model. It is the
only published Danish health-sector footprint on an EXIOBASE-family model.

Comparing headline to headline would mislead, so three boundary differences are removed
one at a time and each step is reported:

| Basis | Mt | t/capita | % national | ratio |
|---|---|---|---|---|
| Schmidt & Merciai 2023 (published) | 6.10 | 1.070 | 8.3 | 1.000 |
| This study, headline | 4.71 | 0.802 | 6.1 | 0.750 |
| + their sector boundary (NACE Q incl. childcare) | 5.28 | 0.899 | 6.8 | 0.841 |
| **+ their capital treatment (endogenised)** | **6.39** | **1.088** | **8.2** | **1.017** |

Boundary-matched agreement is **1.7 % on per capita and 0.1 percentage points on the
national share**. The apparent 25 % gap was entirely boundary, not model, data, or
implementation.

What remains and cannot be adjusted away: their model is **consequential (marginal)**,
ours is attributional. This difference is stated, not corrected.

### Model-family benchmark

Published Danish consumption-based footprints separate by **model family**, not by year:

| Source | Year | Family | t/capita |
|---|---|---|---|
| Eurostat FIGARO | 2022 | national accounts | 9.77 |
| Statistics Denmark AFTRYK | 2022 | NA coupled to EXIOBASE | 10.71 |
| Rørmose Jensen & Iliev | 2020 | NA coupled to EXIOBASE | 11.00 |
| Schmidt & Merciai | 2016 | EXIOBASE v4 hybrid | 12.90 |
| **This study** | 2022 | EXIOBASE v3.8.2 | **13.19** |

The two EXIOBASE-family results agree to 2.3 %; the three national-accounts-family results
cluster 20 % below. Our gap against Statistics Denmark is a property of the model family,
with a named cause (the Danish domestic block, see [09](09_vintage_diagnostics.md)), not
an implementation error.

### Recipe validation

The Danish health column's input structure is compared three ways (EXIOBASE, Eurostat
FIGARO Q86, and Statistics Denmark IO 86), so the model's *composition*, not only its
total, is tested (`recipe_validation_three_way.csv`).

### Standing consistency audit

`analysis.audit_consistency` runs these families of check, several of which cover
more than one table, and exits non-zero on failure:

| Check | What it enforces |
|---|---|
| C1 | the climate total agrees across independently written modules |
| C2 | every node-detail file sums to its own aggregate |
| C3 | no gold file is older than the background it claims |
| C4 | no file retains a withdrawn model label |
| C5 | every gold file has a manifest lineage row |
| C6 | headline numbers quoted in the revision docs still reproduce |

C6 was added on 8 September 2026 after six quoted figures were found to have drifted from
the outputs, two of them mutually inconsistent between documents.

## Deviations from the source, stated

- FIGARO's `nace_r2` is the industry where emissions occur, not the purpose the final
  demand serves, so FIGARO supports a **national** benchmark and a bilateral-origin
  comparison but **not** a health-sector benchmark. The closest proxy is general-government
  final consumption, and it is labelled as a proxy.
- Schmidt & Merciai's reference year is 2016 and ours is 2022; the comparison is of
  per-capita level and national share, not of a time series.

## Outputs

This layer writes `danish_healthcare_benchmark_boundary_matched.csv`,
`published_danish_footprint_benchmarks.csv`, `figaro_vs_this_study_climate.csv`,
`figaro_dk_footprint_by_origin.csv`, `figaro_dk_footprint_by_final_demand.csv`,
`figaro_eu27_material_footprint_health.csv`, `recipe_validation_2022.csv`,
`recipe_validation_three_way.csv`, `demand_vector_consistency.csv`,
`consistency_audit.csv`.

## Verification

The audit is the verification, and it is a gate. Every check passes at the current
build; the count grows as families are added, so the report itself is the record
rather than a number quoted here.
