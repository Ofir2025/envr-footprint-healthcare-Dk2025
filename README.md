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
|---|---|---|
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
        |        pipelines.prep_background_2022.build_background_2022
data/silver/     prepared model objects (git-ignored, regenerable)
                 mrio2022.pkl, leontief2022.pkl, waste.pkl
                 + derived Danish inputs with provenance breakdowns
        |        analysis.main_2025 and the approach modules
data/gold/       published results, one folder per METHOD, indexed by
                 manifest_lineage.csv (approach, script, equations,
                 reference, inputs, checksum)
```

Gold folders: `00_core_footprint`, `01_eriksen_replication`,
`02_scopes_wood_hertwich`, `03_cabernard_target_scope3`,
`04_uncertainty_lenzen_ieooc`, `05_waste_dst_accounts`,
`06_benchmarks_validation`, `scenarios`.

Every table is exported at the most detailed level available - producing
country × producing sector × purchased product × demand component, ISO3 codes
for countries and the EXIOBASE rest-of-world labels (WA/WL/WE/WF/WM) kept as
they are - so all aggregates are derivable and no lineage is lost.

## Running it

```bash
python -m venv .venv && ./.venv/bin/pip install -r requirements.txt

PYTHONPATH=src python -m pipelines.prep_background_2022.build_background_2022
HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship PYTHONPATH=src python -m analysis.main_2025
for m in export_tables extended_indicators national_totals scopes_detail \
         double_counting_audit cabernard_target_scope3 waste_validation \
         waste_domestic_dst demand_vector_consistency figaro_recipe_validation \
         uncertainty_2025 uncertainty_figures build_manifest; do
  HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship PYTHONPATH=src python -m analysis.$m
done
```

Scope variants: `HC_SCOPE=health_only | health_eldercare | zorg_en_welzijn`.
Accounting checks: `PYTHONPATH=src python -m analysis.validate_io_identities`.

## Documentation

| document | content |
|---|---|
| `docs/methods_approaches.md` | every methodological layer, its equations and references |
| `docs/revision/REQUEST_CHECKLIST.md` | status of all outstanding work |
| `docs/revision/bug_and_method_fixes.md` | defects found and fixed, with effects |
| `docs/revision/analysis_2022.md` | the 2022 analysis: inputs, method, results |
| `docs/revision/data_sources_and_models.md` | which external models are used, and why not the others |
| `docs/revision/dk_snac_feasibility.md` | the planned Danish-SNAC hybrid |
| `docs/methods/` | the research blueprint and data-access assessments |

## Provenance and reproducibility

The Danish 2022 expenditure vector is built entirely from **public** Statistics
Denmark tables, so the analysis needs no confidential extract. Direct emissions
come from DRIVHUS, direct waste from AFFALD01, and every StatBank query is in
the code. EXIOBASE archives are MD5-verified against Zenodo.
