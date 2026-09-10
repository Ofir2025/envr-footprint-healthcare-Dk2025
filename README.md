# The environmental footprint of the Danish health care system

Environmentally extended multi-regional input-output (EE-MRIO) analysis of
Danish health care, replicating and extending Steenmeijer et al. (2022),
*The environmental impact of the Dutch health-care sector beyond climate
change*, Lancet Planetary Health 6: e949-57.

**Primary analysis year: 2022** (EXIOBASE version 3.8.2, industry-by-industry
monetary tables, `IOT_2022_ixi`, 49 regions x 163 industries). This study
rejects v3.10.2: it disagrees with v3.8.2 by a factor of three on the size of
the Danish health industry. See
[`docs/methods/exiobase_version_vintage_and_classification.md`](docs/methods/exiobase_version_vintage_and_classification.md).
2019 is retained as a pre-COVID validation baseline.

## Headline result, Denmark 2022

| Indicator | Health care footprint | Share of the national consumption footprint |
|:---|:---|:---|
| Climate change | 4,864 kt CO₂e (~0.83 t/capita) | 7.5 % own model · 7.7 % vs DST AFTRYK · 8.5 % vs Eurostat FIGARO |
| Material extraction | 5,568 kt | 6.8 % |
| Blue water | 42.8 Mm³ | 4.9 % |
| Land use | 3,831 km² | 4.4 % |
| Waste (domestic, DST accounts) | 216 kt (17 kt hazardous) | - |

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
# actually uses - see docs/methods/exiobase_version_vintage_and_classification.md
# for why v3.10.2 is rejected.
#
# `pipelines.prep_background_2022.build_background_2022` builds the REJECTED
# v3.10.2 and exists only to supply layer 09, which has to hold both vintages
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

`python scripts/run_pipeline.py --check` reports stage coverage against the
modules on disk without running anything. It defaults to
`HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship` - the published background.

Scope variants: `HC_SCOPE=health_only | health_eldercare | zorg_en_welzijn`.
Accounting checks: `PYTHONPATH=src python -m analysis.validate_io_identities`.

## Documentation

| document | content |
|:---|:---|
| `docs/revision_guide.md` | branch notes for the revision: how to cite the background, the three things that change the paper, and where everything else lives |
| `docs/methods_approaches.md` | every methodological layer, its equations and references |
| `docs/revision/request_checklist.md` | status of all outstanding work |
| `docs/revision/bug_and_method_fixes.md` | defects found and fixed, with effects |
| `docs/revision/analysis_2022.md` | the 2022 analysis: inputs, method, results |
| `docs/revision/data_sources_and_models.md` | which external models are used, and why not the others |
| `docs/revision/dk_snac_feasibility.md` | what Statistics Denmark does about EXIOBASE, our patch, and the planned Danish-SNAC hybrid |
| `docs/methods/` | the EXIOBASE coupling method, the star schema, and data-access assessments |

## Provenance and reproducibility

The Danish 2022 expenditure vector is built entirely from **public** Statistics
Denmark tables, so the analysis needs no confidential extract. Direct emissions
come from DRIVHUS, direct waste from AFFALD01, and every StatBank query is in
the code. EXIOBASE archives are MD5-verified against Zenodo.
