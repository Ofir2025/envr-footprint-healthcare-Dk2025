# Request checklist — status of everything asked for

| # | Request | Status | Where |
|---|---|---|---|
| 1 | **National totals** for all 163 sectors, so healthcare's share of total impacts of all goods and services is computable | **Done** | `00_core_footprint/national_footprint_by_purchased_product.csv` (26,390 rows), `..._by_producing_node.csv` (16,401), `national_vs_healthcare_by_product_group.csv` (163 sectors × 5 indicators), `national_totals_summary.csv` |
| 2 | **Capital / GFCF** — do we need it, how do others handle it, endogenising | **In progress** — literature review running against your assembled PDFs (Wood endogenises, Steenmeijer excludes, Malik includes, Eckelman includes) | will land in `docs/revision/capital_gfcf_treatment.md` + a sensitivity |
| 3 | **Malik replication folder** for all of Denmark | **Done** — domestic-only variant (the only like-for-like basis: 872.8 kt = **5.71 %** vs their 7.2 % AUS / 6.6 % NSW), component intensities, published-reference table, and the production-layer decomposition (climate L0–L2 **67.9 %** vs their **67 %**) | `07_malik_replication/` |
| 4 | **Lenzen replication folder**, his equations and full KPI set for Denmark | **Done** — totals, direct/supplier/higher-order split, truncation errors, per capita, share of national, intensity, import share, for 5 core + PM10/NOx/SO2/reactive-N; his Danish 2015 values carried alongside; malaria and scarce water documented as not reproducible | `08_lenzen_replication/` |
| 5 | **FIGARO — did we make enough of it?** | **Done** — independent denominator (57.40 Mt), NACE-Q cross-check, and a **three-way recipe validation** in which FIGARO and Statistics Denmark agree with each other while EXIOBASE overstates transport and understates chemicals/pharma 2–3× | `06_benchmarks_validation/recipe_validation_three_way.csv` |
| 6 | **Is the eldercare α change defensible?** | **Done — and it needed the challenge.** Ran both constructions for both years: IO method 0.3060 (2019) / 0.3092 (2022), SUT method 0.4914 (2019). The gap is a *method* artefact, not a year effect; the IO method is the correct object (the industry's own deliveries). Lever size 0.2 % of the footprint | `06_benchmarks_validation/eldercare_alpha_method_test.csv` |
| 7a | **Patient/visitor travel** — research options, pick most feasible yet robust | **In progress** — mining Tennison appendix 1, the RIVM report and Danish TU/patient-transport sources | will land in `docs/revision/bottom_up_travel.md` |
| 7b | **Volatile anaesthetics** — same | **In progress** — testing whether medstat ATC N01AB is retrievable in mass units | `docs/revision/bottom_up_anaesthetics.md` (updated) |
| 8 | **Imported waste** — where needed; FIGARO/Eurostat, or the newest hybrid EXIOBASE on Zenodo | **In progress** — hunting the newest attributional hybrid release with waste accounts | `05_waste_dst_accounts/` |
| 9 | **No Claude traces in GitHub; no stray AI/dev notes** | **Done** — all 26 commit trailers stripped by history rewrite (0 remaining), backup ref deleted, authorship is yours alone, `claude_project_prompt_*.md` renamed to `project_brief_*.md`, emoji/dev chatter removed from console output | verified with `git log --format=%B \| grep -ci claude` = 0 |
| 10 | **Repo organised; ELT/ETL obvious; commit what matters** | **Done** for the gold layer (approach folders + `MANIFEST_lineage.csv`); pipeline documented in `docs/methods_approaches.md` | see below |
| 11 | **Enumerate and check off every request** | This file | — |
| 12 | **Use the assembled literature as source of truth before online sources** | **Standing instruction now in every research brief**; the current round mines your PDFs first and goes online only for genuine gaps | — |

## The pipeline, end to end

```
bronze (raw, never modified)
  EXIOBASE v3.10.2 IOT_2022_ixi ....... external store (Zenodo, MD5-verified)
  DST IO tables 2006-2022 ............. data/bronze/input_output/
  DST detailed SUT 2019 ............... data/bronze/dk_umat_2019.xlsx
  DRIVHUS / AFFALD / SHA / NABB69 ..... StatBank API (queried in code)
  FIGARO + Eurostat footprints ........ data/bronze/figaro/
        |
        v  pipelines.prep_background_2022.build_background_2022
silver (prepared model objects)
  mrio2022.pkl, leontief2022.pkl, waste.pkl ....... data/silver/background/
  dk_data_2025.csv, dk_bottomup_data_2025.txt,
  dk_expenditure_breakdown_2022.csv ............... data/silver/inputs/
        |
        v  analysis.main_2025  (+ the approach modules)
gold (published results, one folder per approach, all indexed by MANIFEST_lineage.csv)
  00_core_footprint  01_eriksen_replication  02_scopes_wood_hertwich
  03_cabernard_target_scope3  04_uncertainty_lenzen_ieooc
  05_waste_dst_accounts  06_benchmarks_validation  scenarios
  07_malik_replication  08_lenzen_replication              (in progress)
```

Run order:

```bash
PYTHONPATH=src python -m pipelines.prep_background_2022.build_background_2022
HC_ANALYSIS_YEAR=2022 PYTHONPATH=src python -m analysis.main_2025
for m in export_tables extended_indicators national_totals scopes_detail \
         double_counting_audit cabernard_target_scope3 waste_validation \
         waste_domestic_dst demand_vector_consistency uncertainty_2025 \
         uncertainty_figures build_manifest; do
  HC_ANALYSIS_YEAR=2022 PYTHONPATH=src python -m analysis.$m
done
```

Scope variants: `HC_SCOPE=health_only|health_eldercare|zorg_en_welzijn`.
Validation: `python -m analysis.validate_io_identities` (Leontief identities).
