# Documentation index

Denmark health-care environmental footprint, 2022. This page is the entry point:
it says where everything lives, what each piece does, and — as importantly —
what it does **not** do.

## Start here

| If you want to… | Read |
|---|---|
| Understand the headline results and how they were produced | [`revision/analysis_2022.md`](revision/analysis_2022.md) |
| Know what is broken, uncertain or still undecided | [`revision/anomalies_bugs_and_open_questions.md`](revision/anomalies_bugs_and_open_questions.md) |
| Understand why the background model is v3.8.2 and not v3.10.2 | [`revision/exiobase_vintage_defects.md`](revision/exiobase_vintage_defects.md) |
| Trace any published number back to its data and method | `data/gold/results/MANIFEST_lineage.csv` |
| See which of the author's requests are answered | [`revision/REQUEST_CHECKLIST.md`](revision/REQUEST_CHECKLIST.md) |
| Understand the modelling approaches implemented | [`methods_approaches.md`](methods_approaches.md) |
| Understand the data layout | [`data_architecture.md`](data_architecture.md) |

## The pipeline

Medallion layout: **bronze** (raw, never modified) → **silver** (prepared
intermediates) → **gold** (published results).

```
data/bronze/          raw inputs, exactly as obtained
  exiobase_v3_7/        symlinks to the EXIOBASE store (v3.8.2 tables)
  input_output/         Statistics Denmark 117-industry IO tables
  medstat/              Danish Medicines Agency ATC sales register
  tu_travel/            Danish national travel survey reports
  dst_capital/          Statistics Denmark capital accounts (NABK69)

data/silver/          prepared model objects
  background/pickled_mrio/    A, L, Z, Y, x, V, Q per vintage and variant
  inputs/                     the Danish expenditure and bottom-up vectors

data/gold/results/    published tables, one folder per approach
```

Build order:

```bash
HC_BACKGROUND_YEAR=2022 python -m pipelines.prep_background_2025.load
HC_BACKGROUND_YEAR=2022 python -m pipelines.prep_background_2025.leontief
HC_BACKGROUND_YEAR=2022 python -m pipelines.prep_background_2025.process
python -m pipelines.prep_background.waste
python -m analysis.dk_shipping_correction
HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship python -m analysis.main_2025
```

then any analysis module, then `python -m analysis.build_manifest`.

## Environment switches

| Variable | Default | Effect |
|---|---|---|
| `HC_ANALYSIS_YEAR` | `2022` | Which year's Danish expenditure and bottom-up data to use |
| `HC_BACKGROUND_YEAR` | `2016` | Which EXIOBASE year to build a background from |
| `HC_BACKGROUND_TAG` | *(empty)* | Model variant; `_snacship` selects the Danish sea-transport reallocation |
| `HC_SCOPE` | `health_eldercare` | `health_only`, `health_eldercare` or `zorg_en_welzijn` (adds childcare) |
| `HC_WASTE_FRACTIONS` | `statistical` | `all` restores the unfiltered 19-fraction waste sum |
| `HC_GWP_VINTAGE` | `AR6` | `AR4` reproduces the workbook's supplied climate factors |

Background year and model provenance are defined **once**, in
`analysis.constants`, so no module can pair one vintage's data with another's
label.

## Gold folders

| Folder | What it holds | Implements |
|---|---|---|
| `00_core_footprint` | Footprint by producing node, by purchased product, bilateral, national totals | Steenmeijer et al. 2022; Miller & Blair |
| `01_eriksen_replication` | The Steenmeijer-style replication outputs, corrected | Steenmeijer et al. 2022 |
| `02_scopes_wood_hertwich` | GHG-Protocol scope partition and the double-counting ledger | Wood & Hertwich 2018 |
| `03_cabernard_target_scope3` | Target-sector scope 3 without double counting | Cabernard et al. 2019 |
| `04_uncertainty_lenzen_ieooc` | Monte Carlo, Sobol shares, ranking probabilities, figures | Lenzen et al. 2020 SI |
| `05_waste_dst_accounts` | Danish domestic waste from Statistics Denmark | DST AFFALD01 |
| `06_benchmarks_validation` | Recipe validation, demand-vector consistency, FIGARO benchmarks | Rørmose Jensen & Iliev 2022; Eurostat |
| `07_malik_replication` | Domestic-only footprint and production layers | Malik et al. 2018, 2021 |
| `08_lenzen_replication` | The Lenzen KPI set for Denmark | Lenzen et al. 2020 |
| `09_vintage_diagnostics` | EXIOBASE vintages against Danish national accounts | this study |
| `10_snac_shipping_correction` | The Danish sea-transport reallocation and its diagnostics | Rørmose Jensen & Iliev 2022 |
| `11_capital_gfcf` | Capital excluded / exogenous / endogenised | Södersten et al. 2018 |
| `12_impact_categories_full` | All 99 usable DESIRE categories, with a quality screen | DESIRE FP7; ILCD |
| `13_steenmeijer_replication` | The Dutch template table, side by side | Steenmeijer et al. 2022 |
| `14_eckelman_replication` | Nine-category frame and DALYs | Eckelman & Sherman 2016 |
| `15_gwp_vintage` | Climate vintage sensitivity, SAR to AR6 | IPCC AR6 table 7.15 |
| `16_impact_world_plus` | 38 current categories incl. water scarcity and DALYs | IMPACT World+ v2.2.1 |

Every file in every folder has a row in `MANIFEST_lineage.csv` giving its
approach, script, equations, inputs, published reference and a content hash.

## Detail and aggregate are stored separately

Every substantive result is written **twice**: once at full node detail and once
aggregated. The detailed file is the record; the aggregate is a convenience.
Storing only the aggregate would destroy the ability to ask where an impact
originates, which is the question an EE-MRIO exists to answer.

A *node* is one (region, industry) pair — 49 x 163 = 7,987. Detailed files carry
`producing_country_iso3`, `producing_country_name`, `producing_world_region`,
`producing_sector_code`, `producing_sector_name` and `producing_sector_group`,
so impacts embodied in **imports** separate from those arising **domestically**,
and the responsible industry is identifiable in both. Files named
`*_domestic_vs_imported.csv` carry that split directly.

Where a table also mixes MRIO results with bottom-up additions, a
`component_type` column distinguishes `MRIO supply-chain node` from
`bottom-up item`, so aggregating cannot silently mix the two.

Detail is asserted to reconcile with its aggregate: the impact-category tables
agree to 4x10^-14 and the production layers to 1x10^-13.

Shared builders live in `analysis.detail_tables`.

## Run the consistency audit after any rebuild

```bash
PYTHONPATH=src .venv/bin/python -m analysis.audit_consistency
```

Seven checks, non-zero exit on failure, so it can gate a release: headline
agreement across independently computing modules; detail reconciling to its
aggregate; no background-derived file older than the background; no file
carrying a superseded model label; and full manifest coverage. It exists because
two real defects — a superseded direct-waste value reaching the capital
sensitivity, and a boundary-scenario run overwriting the headline — were both
found by hand, which is not a reliable way to find them.

## Table schema convention

Tables are written **most detailed first**, so aggregation is always possible
and lineage is never lost. The canonical columns are:

```
country_producing, country_consuming, sector_producing, sector_consuming,
value, unit
```

Countries use ISO3 codes; EXIOBASE's five rest-of-world aggregates keep their
own names (`WA`, `WE`, `WF`, `WL`, `WM`) because they are not countries. Every
table also carries `model`, `analysis_year` and `indicator` so a row is
self-describing once separated from its file.

## Code conventions

- NumPy-style docstrings and type hints on all modules written for this revision.
- Model indices, background selection and provenance live only in
  `analysis.constants`.
- Verification is asserted in code, not assumed: `analysis.validate_io_identities`
  tests six accounting identities, and modules that build a new inverse verify it
  and record the residual in their own diagnostics table.

## What this study does **not** do

Stated plainly so nobody has to infer it:

- **No capital in the headline.** Capital is excluded for comparability with
  Steenmeijer, Eckelman, Lenzen and Pichler, and reported as a sensitivity.
- **No Danish SNAC tier yet.** Only the single documented sea-transport
  reallocation is applied. A full national-accounts coupling is future work.
- **No clinical-waste resolution outside Denmark.** The imported waste tier rests
  on a 2011 hybrid extension; roughly a third of it sits in rest-of-world
  aggregates where no national statistic can apply.
- **No stratospheric ozone depletion.** EXIOBASE carries no CFC, halon or HCFC
  stressor, so the category cannot be computed at all. The shipped DESIRE
  workbook appears to supply one only because its ozone-depletion row
  characterises NMVOC, which is the wrong pollutant class.
- **No physical energy accounting.** Scope 2 is inferred from monetary spend,
  which understates physical consumption in a price-spike year such as 2022.
- **No claim that the national total matches the official one.** It is 22 % above
  Statistics Denmark's AFTRYK and 33 % above Eurostat FIGARO; this is reported,
  not adjusted away.
