# The environmental footprint of the Danish health care system

Environmentally extended multi-regional input-output (EE-MRIO) analysis of
Danish health care, replicating and extending Steenmeijer et al. (2022),
*The environmental impact of the Dutch health-care sector beyond climate
change*, Lancet Planetary Health 6: e949-57.

**Primary analysis year: 2022** (EXIOBASE version 3.8.2, industry-by-industry
monetary tables, `IOT_2022_ixi`, 49 regions x 163 industries). This study
rejects v3.10.2: it disagrees with v3.8.2 by a factor of three on the size of
the Danish health industry. See
[`docs/methods/exiobase_release_and_classification.md`](docs/methods/exiobase_release_and_classification.md).
2019 is retained as a pre-COVID validation baseline.

## Headline result, Denmark 2022

| Indicator | Health care footprint | Share of the national consumption footprint |
|:---|:---|:---|
| Climate change | 4,675.5 kt CO₂-eq (~0.80 t/capita) | 6.1 % |
| Material extraction | 4,257.2 kt | 7.9 % |
| Blue water | 95.4 Mm³ | 7.5 % |
| Land use | 4,851.8 km² | 4.9 % |
| Waste generation | 259.3 kt | 2.4 % |

Every cell is read from gold: the footprints from
[`data/gold/results/01_eriksen_replication/2022_shipping_corrected/figure1_activity_contributions.csv`](data/gold/results/01_eriksen_replication/2022_shipping_corrected/figure1_activity_contributions.csv)
summed over activity groups, the denominators from `national_footprint` in
[`data/gold/results/00_core_footprint/national_totals_summary.csv`](data/gold/results/00_core_footprint/national_totals_summary.csv),
and the per-capita value on the 2022 Danish population of 5,873,420 that
`analysis.constants.DK_POPULATION` carries. The same values, with the national
total and the per-person figure in full, are published as table 1 of
[`data/gold/results/19_tables_of_record/`](data/gold/results/19_tables_of_record/).
The health-care share against the Statistics Denmark AFTRYK and Eurostat FIGARO
national totals used to be quoted here and is gone: no current gold table
publishes it, and
[`data/gold/results/06_benchmarks_validation/figaro_vs_this_study_climate.csv`](data/gold/results/06_benchmarks_validation/figaro_vs_this_study_climate.csv)
carries only the three national totals themselves.

Ten further pressure accounts (PM2.5, PM10, NOx, SOx, NH₃, NMVOC, energy,
N and P to water) are reported alongside. All monetary values are **million
euro** (EXIOBASE's native unit); Danish source data are in 1000 DKK.

## Repository layout - a medallion ELT boundary

```
data/bronze/     raw inputs, never modified
                 EXIOBASE (external store), Danish IO tables and SUT,
                 Eurostat FIGARO extracts, bottom-up source workbooks
        |        pipelines.prep_background_2025 (EXIOBASE v3.8.2)
data/silver/     prepared model objects (git-ignored, regenerable)
                 mrio2022.pkl, leontief2022.pkl, waste.pkl
                 + derived Danish inputs with provenance breakdowns
        |        analysis.main_2025 and the approach modules
data/gold/       published results, one folder per METHOD, indexed by
                 manifest_lineage.csv (approach, script, equations,
                 reference, inputs, checksum)
```

One folder per method, each with a `readme.md` and a `data_dictionary.md`
describing every column. The list is not repeated here: it is generated from
`analysis.gold_scope` into
[`data/gold/results/readme.md`](data/gold/results/readme.md), which says what
each folder holds and why it ships. A hand-typed list is exactly what drifts —
this one had named eight folders while twenty-one existed.

Every table is exported at the most detailed level available - producing
country × producing sector × purchased product × demand component, ISO3 codes
for countries and the EXIOBASE rest-of-world labels (WA/WL/WE/WF/WM) kept as
they are - so all aggregates are derivable and no lineage is lost.

## Running it

```bash
python -m venv .venv && ./.venv/bin/pip install -r requirements.txt

# Build the background once. This uses EXIOBASE v3.8.2, the version this study
# actually uses - see docs/methods/exiobase_release_and_classification.md
# for why v3.10.2 is rejected.
#
# `pipelines.prep_background_2022.build_background_2022` builds the REJECTED
# v3.10.2 and exists only to supply layer 09, which has to hold both releases
# side by side to demonstrate the defects. It writes version-tagged filenames
# (mrio2022_v3_10_2.pkl, leontief2022_v3_10_2.pkl), so it cannot overwrite what
# the commands below produce. It used to write the unsuffixed names and did
# overwrite them; if you are reading an older clone, check before running it.
HC_BACKGROUND_YEAR=2022 PYTHONPATH=src python -m pipelines.prep_background_2025.load
HC_BACKGROUND_YEAR=2022 PYTHONPATH=src python -m pipelines.prep_background_2025.leontief
HC_BACKGROUND_YEAR=2022 PYTHONPATH=src python -m pipelines.prep_background_2025.process
PYTHONPATH=src python -m pipelines.prep_background.waste
PYTHONPATH=src python -m analysis.dk_shipping_correction

# Then run the full pipeline - the supported, executable run order for every
# analysis stage, in dependency order (replaces a hand-written module list,
# which drifts as the pipeline grows):
python scripts/run_pipeline.py
```

Figures are drawn in R, after the pipeline: every figure command is listed in
[`figures/manuscript/readme.md`](figures/manuscript/readme.md), and every one of
them needs `LANG=en_US.UTF-8`, because the locale guard in `r/_dk_common.r`
stops the script rather than draw CO₂, Mm³ and km² as `..`.

`python scripts/run_pipeline.py --check` reports stage coverage against the
modules on disk without running anything. It defaults to
`HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship` - the published background.

Scope variants: `HC_SCOPE=health_only | health_eldercare | zorg_en_welzijn`.
Accounting checks: `PYTHONPATH=src python -m analysis.validate_io_identities`.

## Documentation

| document | content |
|:---|:---|
| `docs/revision_guide.md` | branch notes for the revision: how to cite the background, the three things that change the paper, and where everything else lives |
| `docs/methods/methods.md` | every methodological layer, its equations and references, and which external models are used and why not the others |
| `docs/revision/request_checklist.md` | status of all outstanding work |
| `docs/revision/defects_and_fixes.md` | defects found and fixed, with effects |
| `docs/revision/results_2022.md` | the 2022 analysis: inputs, method, results, and the withdrawn transport finding |
| `docs/methods/methods.md#danish-snac-what-statistics-denmark-does-what-we-patch-and-the-feasibility-of-a-full-build` | what Statistics Denmark does about EXIOBASE, our patch, and the planned Danish-SNAC hybrid |
| `docs/methods/` | the EXIOBASE coupling method, the star schema, and data-access assessments |

## Provenance and reproducibility

The Danish 2022 expenditure vector is built entirely from **public** Statistics
Denmark tables, so the analysis needs no confidential extract. Direct emissions
come from DRIVHUS, direct waste from AFFALD01, and every StatBank query is in
the code. EXIOBASE archives are MD5-verified against Zenodo.
