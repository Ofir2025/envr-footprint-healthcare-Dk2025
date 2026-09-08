# Request checklist - status of everything asked for

| # | Request | Status | Where |
|---|---|---|---|
| 1 | **National totals** for all 163 sectors, so healthcare's share of total impacts of all goods and services is computable | **Done** | `00_core_footprint/national_footprint_by_purchased_product.csv` (26,390 rows), `..._by_producing_node.csv` (16,401), `national_vs_healthcare_by_product_group.csv` (163 sectors × 5 indicators), `national_totals_summary.csv` |
| 2 | **Capital / GFCF** - do we need it, how do others handle it, endogenising | **In progress** - literature review running against your assembled PDFs (Wood endogenises, Steenmeijer excludes, Malik includes, Eckelman includes) | will land in `docs/revision/capital_gfcf_treatment.md` + a sensitivity |
| 3 | **Malik replication folder** for all of Denmark | **Done** - domestic-only variant, the only like-for-like basis: 839.5 kt, **3.98 %** of the domestic national total and 6.00 % of the full one, against their 7.2 % AUS and 6.6 % NSW; component intensities; published-reference table; and the production-layer decomposition, where the first three layers carry **63.0 %** of the Danish climate footprint against Malik's **67 %** for NSW. *(Corrected 2026-09-08: this row previously read 872.8 kt, 5.71 % and 67.9 %, none of which reproduce; `production_layers_vs_malik.csv` and `malik_domestic_vs_full.csv` are the source.)* | `07_malik_replication/` |
| 4 | **Lenzen replication folder**, his equations and full KPI set for Denmark | **Done** - totals, direct/supplier/higher-order split, truncation errors, per capita, share of national, intensity, import share, for 5 core + PM10/NOx/SO2/reactive-N; his Danish 2015 values carried alongside; malaria and scarce water documented as not reproducible | `08_lenzen_replication/` |
| 5 | **FIGARO - did we make enough of it?** | **Done** - independent denominator (57.40 Mt), NACE-Q cross-check, and a **three-way recipe validation** in which FIGARO and Statistics Denmark agree with each other while EXIOBASE overstates transport and understates chemicals/pharma 2-3× | `06_benchmarks_validation/recipe_validation_three_way.csv` |
| 6 | **Is the eldercare α change defensible?** | **Done - and it needed the challenge.** Ran both constructions for both years: IO method 0.3060 (2019) / 0.3092 (2022), SUT method 0.4914 (2019). The gap is a *method* artefact, not a year effect; the IO method is the correct object (the industry's own deliveries). Lever size 0.2 % of the footprint | `06_benchmarks_validation/eldercare_alpha_method_test.csv` |
| 7a | **Patient/visitor travel** - research options, pick most feasible yet robust | **In progress** - mining Tennison appendix 1, the RIVM report and Danish TU/patient-transport sources | will land in `docs/revision/bottom_up_travel.md` |
| 7b | **Volatile anaesthetics** - same | **In progress** - testing whether medstat ATC N01AB is retrievable in mass units | `docs/revision/bottom_up_anaesthetics.md` (updated) |
| 8 | **Imported waste** - where needed; FIGARO/Eurostat, or the newest hybrid EXIOBASE on Zenodo | **In progress** - hunting the newest attributional hybrid release with waste accounts | `05_waste_dst_accounts/` |
| 9 | **Repository hygiene: no assistant traces, no stray development notes** | **Done** - all 26 commit trailers stripped by history rewrite, backup ref deleted, authorship is yours alone, the project brief renamed to `project_brief_*.md`, emoji and development chatter removed from console output | verified by scanning commit messages, source and docs |
| 10 | **Repo organised; ELT/ETL obvious; commit what matters** | **Done** for the gold layer (approach folders + `MANIFEST_lineage.csv`); pipeline documented in `docs/methods_approaches.md` | see below |
| 11 | **Enumerate and check off every request** | This file | - |
| 12 | **Use the assembled literature as source of truth before online sources** | **Standing instruction now in every research brief**; the current round mines your PDFs first and goes online only for genuine gaps | - |

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

## Round of 2026-09-07 (continued)

| # | Request | Status | Evidence |
|---|---|---|---|
| 10 | **Capital / GFCF: do we need it, how do others handle it, endogenisation** | **Done** | `docs/revision/capital_gfcf_treatment.md`; `analysis.capital_gfcf` → `11_capital_gfcf/`. Cross-study table; three treatments; +13.2 % (exogenous capital service flow, DST NABK69) and +19.4 % (endogenised on the published Södersten et al. 2018 matrices). *(Corrected 2026-09-08: this row previously gave +21.0 % for the endogenised case, which is the simplified construction the published method later replaced; `capital_endogenised_sodersten.csv` is the source.)* Corrected the earlier wrong claim that zero medical-instrument purchases were a capital artefact |
| 11 | **Volatile anaesthetics - how far can the proxy go** | **Done** | Replaced by Danish primary data: medstat.dk ATC N01AB sales, both years verified against the register. 11.6 kt for 2022, and the item now shows the desflurane phase-out |
| 12 | **Patient / visitor travel - find a Danish source** | **Done** | A Danish source exists after all: TU (DTU) Tabel 15, purpose code 33, verified in the primary PDFs (0.9 km/person/day 2019, 0.8 in 2022). Also fixed a unit error - a whole-population quantity was being scaled by employment × working hours |
| 13 | **Imported waste - hybrid EXIOBASE waste data** | **Done** | v3.3.18 confirmed as the newest hybrid with waste accounts (nothing newer exists; the 2024 "October" release is consequential and has none). Fixed a real bug: all 19 fractions were being summed, including manure, sewage, mining and unused waste, none of which are in the Eurostat/DST boundary. World industry waste 13.17 → 2.01 Gt; healthcare waste 829 → 257 kt |
| 14 | **Figure formatting compliant with house rules** | **Done** | Variance-share figure had three legend keys for series never drawn; sub-visible parameters are now pooled into one labelled residual. Aspect ratios 1.50-1.75, legends at the bottom, no baked-in titles |
| 15 | **EXIOBASE vintage integrity (not requested - found)** | **Done** | v3.10.2's 2022 Danish block fails against national accounts; background moved to v3.8.2. `docs/revision/exiobase_vintage_defects.md`, `analysis.vintage_defect_audit` → `09_vintage_diagnostics/` |
| 16 | **"Transport ≈ 40 %" (not requested - found)** | **Done** | Reproduced Statistics Denmark's published 74 % shipping misallocation at 73.6 % on our own model; correcting it moves transport from 37.5 % to **18.5 %** of the 3,943 kt supply-chain component, which is 15.5 % of the 4,712 kt total. *(Corrected 2026-09-08 from 18.9 %, and the basis is now stated, which is the rule this study adopted after three unreproducible shares were found in earlier drafts.)* `analysis.dk_shipping_correction` → `10_snac_shipping_correction/` |

## Round of 2026-09-08

Every item below was asked for across the three most recent rounds of comments.
The evidence column names the file or the check that shows the work is done, so
each row can be verified without taking this table's word for it.

### Scenario analysis

| # | Request | Status | Evidence |
|---|---|---|---|
| 17 | The sea-transport correction must be explained explicitly somewhere | **Done** | `docs/revision/shipping_reallocation_method.md`, six sections plus every alternative considered, the official Statistics Denmark method in full, and an independent validation against the hybrid EXIOBASE; replication note `10_snac_shipping_correction.md`; a flowchart of what moves and what is preserved |
| 18 | Scenarios in the paper explicitly and properly | **Done** | `docs/methods/replications/18_mitigation_scenarios.md`. The formalism is Aguilar-Hernandez et al. (2018) equations 1 to 4 and Donati et al. (2020) equations 1, 5 and 6, with Takase et al.'s (2005) rebound; the counterfactual is solved, not approximated from the stored inverse |
| 19 | Why is there no figure for the scenario results | **Done** | `fig8_mitigation_waterfall_2022` and `fig9_burden_shifting_2022`. The choice of a waterfall is argued in the header of `R/plot_scenarios.R` against the four alternatives that were rejected |
| 20 | Why are the scenarios climate only; burden shifting matters | **Done** | Every lever is solved for all five impact categories. The finding that waste diversion and inhaler substitution move blue water, land use and waste in the opposite direction to climate is now a headline result rather than a caveat |
| 21 | Schmidt and Merciai's consequential approach, and the circular-economy MRIO literature, as the yardstick | **Done** | Section 6 of the scenario note sets out what an attributional model can and cannot answer, and names each lever that would need a consequential model |
| 22 | Model real Danish green-transition interventions | **Done** | Fourteen lever families drawn from stated Danish policy: Danish Energy Agency KF22 and KF25 grid factors, the Danske Regioner 2024 regional target, measured Danish outcomes where they exist |
| 23 | Write the results into data tables with correct schemas | **Done** | `data/gold/results/18_mitigation_scenarios/`, keyed into the star schema; foreign keys resolve and the grain holds (audit checks C7) |
| 24 | Make clear that we do not rebalance | **Done** | Section 2.4 of the scenario note, with the imbalance measured by equation (7), reported per scenario, and the Lenzen et al. (2010, section 2.3) precedent for declining to rebalance |

### Uncertainty

| # | Request | Status | Evidence |
|---|---|---|---|
| 25 | Re-audit the Monte Carlo end to end; make it justifiable and statistically sound | **Done, and it found a substantive error** | The correlation sensitivity had been holding the spread fixed while varying the correlation, which abandoned the calibration and let the supply-chain coefficient of variation collapse to 4.27 % against the 8.35 % asserted. `analysis.uncertainty_2025.sigma_for_rho` now re-solves the spread at every correlation. `analysis.uncertainty_audit` runs nineteen numerical checks, all passing |
| 26 | Identify all sources of uncertainty; quantify those that can be quantified | **Done** | `docs/revision/uncertainty_sources.md`: a four-branch taxonomy after Huijbregts (1998) as adapted by Schulte et al., a flowchart, eight tagged equations, and a closing ledger that names every source left unquantified and the direction of the bias each leaves |
| 27 | New literature: Schulte et al. (2026) on correlation and disaggregation | **Done** | Read and integrated. Its central result, that allocation of an inventory category across industries can move a sector standard deviation by anywhere from −34 % to +130 %, is the largest single unquantified source in the ledger |
| 28 | Report both IPCC tiers | **Done** | Tier 1 error propagation 7.84 % against Tier 2 simulation 7.87 %, as IPCC (2000) 6.3.1 requires; convergence measured against the 6.4 step 5 criterion at 0.21 % |

### Documentation, figures and presentation

| # | Request | Status | Evidence |
|---|---|---|---|
| 29 | A comprehensive foundation of documentation for the co-author to build on | **Done** | Twenty-three revision documents and nineteen replication notes, each stating its question, its method, its equations, its data requirements and its limitations |
| 30 | Correct Markdown equation syntax | **Done** | Display equations in `$$ ... $$` with `\tag{}` numbering, symbols defined in prose or in a symbol table at first use |
| 31 | Flowcharts where they aid understanding, in Mermaid or draw.io, embedded in the Markdown | **Done** | Four diagrams, all Mermaid so they render in place on GitHub: the uncertainty taxonomy; the two marginals of the bilateral table and the trap of quoting a share without its basis; the counterfactual scenario workflow; the sea-transport reallocation |
| 32 | Formal academic tone throughout, per the publishing guidelines | **Done** | A full pass against the house copy-editing guideline: no em or en dash anywhere, connector dashes replaced by the punctuation the rule names, serial commas, no bare demonstratives, no filler, three significant figures in prose |
| 33 | Document every limitation of using EXIOBASE | **Done** | `docs/revision/exiobase_limitations_and_interpretation.md`, twelve sections, each in the required three parts: name the limitation, say what it changes about the conclusion, say what design would reduce it |
| 34 | The citation lesson: never assert a number from an abstract, and never withdraw one without reading the table | **Done** | Recorded as a dated self-correction in `monte_carlo_explained.md`. It earned its keep this round: it caught a second conflation, where a *Scientific Data* reference had been given the authors and title of a different Wood et al. (2019) paper |
| 35 | Figure-type choice reasoned and argued, formatting compliant | **Done** | Each plotting script carries a header stating the question the figure answers, the form chosen, and the forms rejected with reasons; `figures/manuscript/README.md` records the shared conventions |
| 36 | Keep the presentation up to date | **Done** | Twenty-six slides, checked by `scripts/release/check_deck_layout.py` for geometry and by a LibreOffice render for what the geometry check cannot see |
| 37 | A Word document of every table circulated so far, verified, with notes | **Done** | `data/gold/results/19_tables_of_record/`: fifteen tables regenerated from the gold facts, each with a note, a source line, and where an earlier figure is in circulation, the value it supersedes |
| 38 | Put the relevant tables into the slide deck | **Done** | The 2019-against-2022 comparison and its climate decomposition are now slide 20, which is the slide that answers whether the two runs form a series |
| 39 | Differentiate the private results folder from the branch published to the co-author | **Done** | `analysis.gold_scope` classifies all twenty-two gold folders with a reason each; the publish script reads that classification rather than a hand-maintained list, and audit check C9 fails on any unclassified folder |
| 40 | Replace the corrupt reference PDF | **Done** | The Schulte et al. (2024) file had no trailer dictionary. Replaced from an intact copy, verified to open and extract, and the damaged original kept alongside it |

### What this round's audits found

Nothing in the list above was accepted on assertion. Five substantive errors were
found and corrected while checking it, and they are worth stating plainly because
four of them had reached documents intended for the editor.

| Finding | Where it had reached | Correction |
|---|---|---|
| The correlation sensitivity table carried the superseded, pre-calibration values, and the argument built on them no longer held | `uncertainty_methods_for_manuscript.md`, which is the manuscript text, and `response_to_reviewers.md` | Both replaced with the re-solved values, and the argument restated: the correlation assumption governs how variance is distributed, not how much of it there is |
| The 95 % interval existed in four different forms across five documents | five revision documents | One form everywhere, 4,064 to 5,531 kt, taken from `uncertainty_totals.csv` |
| The first-order variance share of the input-output model was quoted as 86.8 % | `response_to_reviewers.md`, `analysis_2022.md` | 78.8 %, with the covariance between commuting and visitor travel named separately at 9.3 % rather than folded in |
| Schulte et al.'s sector-level coefficient of variation of 94 % was quoted where the argument concerns a footprint | four documents | The paper's table 2 gives 94 % for emission *accounts* and 18 % for the *footprints* derived from them. The footprint pair is the one that applies, and using the accounts figure would have overstated the caveat roughly fivefold |
| A *Scientific Data* reference carried the authors and title of a different Wood et al. (2019) paper | two documents | Corrected to Wood, Moran, Rodrigues and Stadler (2019), which is the paper the 8.8 % Danish figure actually comes from |
| The Cabernard note printed its overestimation column under the label of equation (12) | `03_cabernard_target_scope3.md` | They are different statistics. Equation (12) divides by the naive total and gives 35.4 % for the broadest target set; the overestimate divides by the corrected total and gives 54.7 %. Both are now shown and named, and the comparison with Cabernard's own G20 figures is on the second, which is the one she reports |
| The capital table attributed this study's own construction to Södersten et al. | `response_to_reviewers.md`, `analysis_2022.md`, `capital_gfcf_treatment.md` | The published matrices give 4,849 kt and +19.4 %; our simplified construction gave 4,914 kt and +21.0 %. Both are shown, correctly attributed, with the agreement between them stated as the evidence it is |
| The capital table's waste row was still on the pre-correction waste accounts | `capital_gfcf_treatment.md` | 259.4 kt baseline, not 377 |
| The greenhouse-gas vintage table named AR4 as the vintage in use and carried superseded AR5 and AR6 rows | `anomalies_bugs_and_open_questions.md` | Rebuilt from `gwp_vintage_sensitivity.csv`, with AR6 marked as the study default and the 155.3 kt of pre-aggregated HFC and PFC reported as not restatable |
| One bottom-up item still characterises N₂O at AR4's 298 while the model runs on AR6's 273 | `main_2025.py`, and now stated in the anomalies note | Left as it stands and reported. The mismatch is 0.95 kt, 0.02 % of the headline, against an interval spanning 1,467 kt; restating it would move every gold file for a difference two orders of magnitude below the interval. It is now a stated decision rather than an unexamined inheritance |

Two stale figures in the earlier rounds of this checklist were corrected at the
same time, and are marked in place: the Malik production-layer share, which had
been recorded as agreeing with Malik when it is four points below, and the
post-correction transport share, which is 18.5 % of the supply-chain component
and 15.5 % of the total.

### Standing audits, and their current state

| Audit | Scope | State |
|---|---|---|
| `analysis.audit_consistency` | partition totals, detail reconciliation, file currency, model labels, lineage coverage, documented numbers, star-schema keys and grain, citations, gold-folder classification | **12 of 12 pass** |
| `analysis.uncertainty_audit` | median-1 construction, realised geometric standard deviations, correlations, closed-form moments, variance shares, convergence, seed independence, calibration held across correlations, both IPCC tiers | **19 of 19 pass** |
| `analysis.bibliography` | in-text citations resolve, DOIs verified against Crossref | 62 sources, 47 DOIs, 8 documents |
| `scripts/release/check_deck_layout.py` | slide geometry, text overflow against font metrics | 3 known decorative bleeds, no text faults |
| `scripts/release/publish_ofir_branch.sh` | withheld paths, referee wording, attribution trailers | run before every publish |
