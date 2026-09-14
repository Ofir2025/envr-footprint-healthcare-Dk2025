# The environmental footprint of the Danish health care system

Environmentally extended multi-regional input-output (EE-MRIO) analysis of Danish
health care, replicating and extending Steenmeijer et al. (2022), *The
environmental impact of the Dutch health-care sector beyond climate change*,
Lancet Planetary Health 6: e949-57.

**Primary analysis year 2022**, on EXIOBASE v3.8.2 `IOT_2022_ixi` (49 regions ×
163 industries). 2019 is retained as a pre-COVID baseline and as the link to the
submitted manuscript. v3.10.2 is rejected on evidence set out in
[`docs/methods/exiobase_release_and_classification.md`](docs/methods/exiobase_release_and_classification.md).

## Headline result, Denmark 2022

| Indicator | Health care footprint | Share of the national consumption footprint |
|:---|:---|:---|
| Climate change | 4,162.1 kt CO₂-eq (≈ 0.71 t per capita) | 5.4 % |
| Material extraction | 3,494.0 kt | 6.5 % |
| Blue water | 74.8 Mm³ | 5.9 % |
| Land use | 4,117.4 km² | 4.1 % |
| Waste generation | 221.1 kt | 2.1 % |

Every cell above is read from
[`19_tables_of_record/`](data/gold/results/19_tables_of_record/) table 1, which
also carries the national total and the per-person figure in full. Eight further
pressure accounts — PM2.5, PM10, NOx, SOx, NH₃, NMVOC, and nitrogen and
phosphorus to water — are reported in
[`00_core_footprint/extended_indicators_summary.csv`](data/gold/results/00_core_footprint/extended_indicators_summary.csv),
and 99 characterised impact categories across 29 characterisation methods in
[`12_impact_categories_full/`](data/gold/results/12_impact_categories_full/),
because the studies this one is benchmarked against each report a different set.

## Model variants

A **variant** fixes the four axes that change the numbers — EXIOBASE release,
Danish sea-transport correction, care boundary, capital treatment — and is named
`<year><letter>`. `2022c` is the headline of the resubmission; `2019a` is the
configuration the manuscript was submitted on.

| Variant | EXIOBASE background | Shipping correction | Care boundary | Capital | Climate footprint, kt CO₂-eq | Share of national | Arising in transport |
|:---|:---|:---|:---|:---|---:|---:|---:|
| `2016a` | v3.7, `IOT_2016_ixi` | no | health care | excluded | 7,625 | 9.6 % | 37.3 % |
| `2016b` | v3.7, `IOT_2016_ixi` | yes | health care | excluded | 5,665 | 8.6 % | 17.8 % |
| `2016c` | v3.8.2, `IOT_2016_ixi` | yes | health care | excluded | 3,687 | 5.0 % | 21.9 % |
| `2016d` | v3.8.2, `IOT_2016_ixi` | yes | + child and elder care | endogenised | 5,449 | 6.0 % | 20.3 % |
| `2019a` | v3.7, `IOT_2016_ixi` | no | health care | excluded | 8,047 | 10.2 % | 37.3 % |
| `2019b` | v3.7, `IOT_2016_ixi` | yes | health care | excluded | 5,983 | 9.0 % | 17.8 % |
| `2019c` | v3.8.2, `IOT_2016_ixi` | yes | health care | excluded | 3,890 | 5.2 % | 21.9 % |
| `2019d` | v3.8.2, `IOT_2016_ixi` | yes | + child and elder care | endogenised | 5,739 | 6.3 % | 20.3 % |
| `2022c` | v3.8.2, `IOT_2022_ixi` | yes | health care | excluded | 4,162 | 5.4 % | 16.0 % |
| `2022d` | v3.8.2, `IOT_2022_ixi` | yes | + child and elder care | endogenised | 5,949 | 6.3 % | 15.3 % |
| `2016_uncorrected` | v3.8.2, `IOT_2016_ixi` | no | health care | excluded | 5,883 | 6.8 % | 48.3 % |
| `2019_uncorrected` | v3.8.2, `IOT_2016_ixi` | no | health care | excluded | 6,204 | 7.2 % | 48.2 % |
| `2022_uncorrected` | v3.8.2, `IOT_2022_ixi` | no | health care | excluded | 5,583 | 6.5 % | 34.7 % |

The same thirteen configurations for **all five indicators**, with the national
footprint and the expenditure behind each, are published as
[`01_eriksen_replication/variant_comparison.csv`](data/gold/results/01_eriksen_replication/variant_comparison.csv).
Every cell is read from the variant's own tables, so the summary and the folders
cannot disagree.

Three properties of that table matter for reading the manuscript:

- **There is no `2022a` or `2022b`, and there cannot be.** EXIOBASE v3.7 publishes
  `IOT_*_ixi` for 1995-2016 only, so the release axis collapses for 2022.
- **`2019_uncorrected` is not variant `a`.** It is v3.8.2's 2016 table without the
  correction, and it is the configuration that reproduced the submitted
  transport share (47.0 % against the submitted 46 %) while pharmaceutical and
  appliance spending was still mapped whole to the good, as the submission did.
  With the distribution margins moved to the Danish trade industries
  (13 September 2026) it returns 48.2 %; variant `a`, the release the
  submission cites, returns 37.3 % (35.0 % before).
- **All thirteen run on IPCC AR6 GWP100.** The 2016 backgrounds were republished on
  AR6 on 11 September 2026; before that the study reported a 2019 answer on AR4
  beside a 2022 answer on AR6. See
  [`docs/revision/defects_and_fixes.md`](docs/revision/defects_and_fixes.md).

Axis definitions and the environment variables that select a variant are in
[`docs/methods/replications.md`, section 01](docs/methods/replications.md#r01).

## Repository layout — a medallion ELT boundary

```
data/bronze/   raw inputs, never modified: EXIOBASE, Danish IO and supply-use
               tables, Eurostat FIGARO extracts, bottom-up source workbooks
data/silver/   prepared model objects and conformed inputs, mirroring bronze by
               provenance; regenerable, mostly git-ignored
data/gold/     published results, one folder per METHOD, each with a readme.md
               and a data_dictionary.md, indexed by manifest_lineage.csv
```

The folder list is generated into
[`data/gold/results/readme.md`](data/gold/results/readme.md) rather than typed
here — a hand-written list is exactly what drifts.

## Running it

```bash
python -m venv .venv && ./.venv/bin/pip install -r requirements.txt

HC_BACKGROUND_YEAR=2022 PYTHONPATH=src python -m pipelines.prep_background_2025.load
HC_BACKGROUND_YEAR=2022 PYTHONPATH=src python -m pipelines.prep_background_2025.leontief
HC_BACKGROUND_YEAR=2022 PYTHONPATH=src python -m pipelines.prep_background_2025.process
PYTHONPATH=src python -m pipelines.prep_background.waste
PYTHONPATH=src python -m analysis.dk_shipping_correction

python scripts/run_pipeline.py
```

`run_pipeline.py` is the supported run order for every analysis stage, in
dependency order; `--check` reports stage coverage without running anything. It
defaults to `HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship`, the published
background. Accounting identities:
`PYTHONPATH=src python -m analysis.validate_io_identities`.

Figures are drawn in R after the pipeline; every command is listed in
[`figures/manuscript/readme.md`](figures/manuscript/readme.md) and each needs
`LANG=en_US.UTF-8`, because the locale guard in `r/_dk_common.r` halts rather than
draw CO₂, Mm³ and km² as `..`.

## Documentation

| document | content |
|:---|:---|
| [`docs/revision_guide.md`](docs/revision_guide.md) | how to cite the background, the three things that change the paper, and where everything else lives |
| [`docs/methods/methods.md`](docs/methods/methods.md) | every methodological layer, its equations and references, and which external models are used and why not the others |
| [`docs/methods/replications.md`](docs/methods/replications.md) | what each gold layer replicates, per method, with its verification |
| [`docs/methods/exiobase_release_and_classification.md`](docs/methods/exiobase_release_and_classification.md) | which EXIOBASE release, why v3.10.2 is rejected, and how the classification is handled |
| [`docs/methods/danish_data_acquisition.md`](docs/methods/danish_data_acquisition.md) | every Danish source, its StatBank query and its licence |
| [`docs/revision/results_2022.md`](docs/revision/results_2022.md) | the 2022 analysis: inputs, method, results, and the withdrawn transport finding |
| [`docs/revision/defects_and_fixes.md`](docs/revision/defects_and_fixes.md) | defects found and fixed, with their effect on every number that moved |
| [`docs/revision/uncertainty.md`](docs/revision/uncertainty.md) | the Monte Carlo, the Sobol decomposition and what they do and do not establish |
| [`docs/revision/response_to_reviewers.md`](docs/revision/response_to_reviewers.md) | the reviewer replies, each tied to the table that answers it |
| [`docs/revision/request_checklist.md`](docs/revision/request_checklist.md) | status of all outstanding work |

## Provenance and reproducibility

The Danish 2022 expenditure vector is built entirely from **public** Statistics
Denmark tables, so the analysis needs no confidential extract; every StatBank
query is in the code and documented in
[`docs/methods/danish_data_acquisition.md`](docs/methods/danish_data_acquisition.md).
EXIOBASE archives are MD5-verified against Zenodo. All monetary values are
**million euro**, EXIOBASE's native unit; Danish source data are in 1000 DKK.
`analysis.audit_consistency` runs 21 cross-layer checks over the published
tables, and its result is published as
[`06_benchmarks_validation/consistency_audit.csv`](data/gold/results/06_benchmarks_validation/consistency_audit.csv).
