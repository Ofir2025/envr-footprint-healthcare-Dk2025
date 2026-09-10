# Source material locations

This is a hand-written map of where the project's source material - literature
PDFs and the data stores read alongside them - actually lives on disk. It is
not the bibliography: for the APA-formatted, generated citation list, see
[`references.md`](references.md) (and edit
[`references.csv`](references.csv), never that file, to change it). This file
holds the opposite kind of information - not what to cite, but which directory
to open to find the source behind a citation - and it is maintained by hand
because that mapping cannot be generated from the CSV.

**`docs/references/`, the directory this file leads with below, is withheld
from the co-author's published branch by
`scripts/release/publish_ofir_branch.sh`.** A reader working from that branch
will not have those PDFs; the citations they support are still in
`references.md`, but the source files themselves are only in the full working
copy.

Every literature source this project draws on, with its location, so that a
claim can be checked and so the same libraries can be reused by later work.
This file is the project's single record of where each source lives; other
documents cite it rather than restating bibliographic detail, and where a
document draws on an online source instead of the local library, it states why
the local library was insufficient.

Paths are absolute because the libraries live outside this repository.

---

## 1. Project library - health-sector footprints

`envrfootprint_healthcare/docs/references/` - **42 items**

The studies this project replicates or benchmarks against, and the method papers
its equations come from.

| Cluster | Key items |
|:---|:---|
| **Replication targets** | Steenmeijer et al. 2022 (the template, + the Lancet appendix and the fuller RIVM report 2022-0159); Eckelman & Sherman 2016 (+ S1-S5 tables); Malik et al. 2018 (+SI) and 2021 (+SI); Lenzen et al. 2020 (+SI directory) |
| **Danish EXIOBASE remedies** | **Rørmose Jensen & Iliev 2022** - the coupled model; Palm et al. 2019 (+SI) - simplified SNAC; Tukker et al. 2018 - the method taxonomy |
| **Scope and double counting** | Wood & Hertwich 2018; Cabernard et al. 2019 (+SI, at the AFRIMAT path below) |
| **Danish context** | Arup 2025 Denmark health fact sheet; Healthcare Denmark 2024; Fagerberg et al. 2017 |
| **Bottom-up items** | Tennison et al. 2021 (+2 appendices); Kouwenberg et al. 2024; Belkhir & Elmeligi 2018; Jeswani & Azapagic 2019 |
| **Comparators** | Pichler et al. 2019 (+SI); Karliner et al. 2019; Chung & Meltzer 2009; Doucet et al. 2025 (ICIO) |

## 2. Kommune-project library - the largest resource

`dk_kommune_footprints/docs/references/` - **896 items**

Assembled for the municipal footprint project; most of its method material
applies directly here.

| Subtree | Items | Why it matters here |
|:---|:---|:---|
| `methods/emission_inventories/` | 104 | Danish National Inventory Document (Nielsen et al. 2026); Gravgaard et al. 2009 on GHG emissions of the Danish economy; **`danish_energy_agency_global_report_pointer.md`** |
| `methods/mrio_exiobase_io_theory/` | 78 | IO theory; `input_output_theory/` holds Melo 2019 on bottom-up versus top-down environmental extensions, and the Statistics Denmark ADAM model |
| `methods/denmark_data_statistics/` | 68 | **Statistics Denmark 2019 environmental-economic accounting**; regional accounts; household budget survey; municipal energy and GHG; `energy_economy_reports/` |
| `methods/denmark_studies_comparators/` | 38 | **Schmidt & Merciai 2023, GHG emissions of Danish consumption 2016** - a directly comparable Danish consumption footprint; Ghosh et al. 2014 |
| `methods/classifications_standards/` | 10 | **GHG Protocol/IPCC AR6 GWP values**; WRI/WBCSD scope 3 technical guidance; COICOP 2018; NACE Rev. 2 |
| `methods/uncertainty/` | 9 | **The primary uncertainty literature**: Lenzen et al. 2010; Rodrigues et al. 2018 (+SI); Schulte et al. 2021, 2024, 2026; Badr et al. 2026 review |
| `introduction/denmark_climate_policy/` | 203 | Danish Climate Act; DEA Climate Status and Outlook; **DEA 2025 Denmark global climate impact**; Climate Council 2025 |
| `discussion/food_diet_agriculture/` | 124 | Relevant to the food and catering contribution group |
| `introduction/subnational_urban_footprints/` | 48 | Downscaling and subnational attribution |

## 3. MRIO master library - **712 PDFs**

`~/Library/CloudStorage/OneDrive-Personal/Career/professor/teaching/MRIO_literature/`

This is the project's master MRIO library. An earlier note recorded it as ~230
items; the true size is **712**, and the three folders below are the ones this
project depends on most.

| Subfolder | Items | Status |
|:---|:---|:---|
| `applications/` | 374 | **largely unsurveyed** - includes `footprints/carbon/scope_3/` (Hertwich & Wood 2018, Kanemoto 2011, Davis 2025) and `subnational_regionalisation/` |
| `methods/` | 209 | surveyed |
| `databases/` | 77 | **pinned below** |
| `book_chapters/` | 31 | unsurveyed |
| `uncertainty/` | 21 | **pinned below**, fully used |

### 3a. `databases/exiobase/` - the EXIOBASE documentation of record

The primary methodology sources for the model this study runs on. **Cite these
for anything about how EXIOBASE is built.**

| File | Why it matters |
|:---|:---|
| `stadler_et_al_2018_exiobase3_detailed_ee_mrio_tables.pdf` (+ 2 SIs) | The EXIOBASE 3 paper of record, with the detailed-tables SI and the material-accounts SI |
| `merciai_&_schmidt_2017_exiobase_v3_mr_hsut_methodology.pdf` | The hybrid supply-use construction underlying the hybrid releases and the waste extension |
| `wood_et_al_2015_exiobase_global_sustainability_mrio_footprint.pdf` | The footprint application paper |
| `tukker_et_al_2018_jie_special_issue_exiobase.pdf` | The special-issue framing |
| `rasul_et_al_2024_exiobase_energy_accounts_precision_mrio.pdf` | Energy-account precision - relevant to the Scope 2 question |
| `de_koning_et_al_2011_exiopol_exiobase_database_management.pdf`, `reyes_et_al_2017_virtual_ielab_exiobase_v2_production_pipeline.pdf` | Construction history and pipeline |

### 3b. `methods/hybrid_io_lca/` - hybrid LCA and the EXIOBASE-hybrid model

| Item | Why it matters |
|:---|:---|
| `merciai_2022_exiobase_hybrid_v4/` (7 parts) | **The EXIOBASE-hybrid v4 documentation** - the model behind Schmidt & Merciai's Danish footprint, and the source for their capital endogenisation |
| `agez_et_al_2020_lifting_veil_double_counting_hybrid_lca.pdf`, `agez_et_al_2022_correcting_truncations_hybrid_lca.pdf` | Double counting in hybrid LCA - directly relevant to R1-2 |
| `lee_&_ma_2013_improving_integrated_hybrid_lca_upstream_scope3_emissions.pdf` | An explicit process/IO truncation criterion |
| `perkins_&_suh_2019_hybrid_lca_precision_vs_accuracy.pdf`, `yang_et_al_2017_hybrid_lca_not_necessarily_more_accurate_process_lca.pdf` | The counter-case: hybrid is not automatically better. Worth citing when justifying our additive approach |
| `suh_et_al_2010_generalized_make_use_framework_allocation_lca.pdf`, `majeau_bettez_et_al_2011_process_io_lci_truncation_aggregation.pdf` | Construct and allocation choice |
| `nakamura_2023_eeio_hybrid_lca/`, `jakobs_2023_modelling_uncertainty_hlca/` | Textbook and thesis treatments |
| `palm_et_al_2019_..._hybrid_multiregional_input_output.pdf` | The SNAC implementation (duplicate of the copy in the project library) |

### 3c. `uncertainty/` - the uncertainty literature of record

Every claim in [`docs/revision/uncertainty.md`](revision/uncertainty.md), section
2 ("The Monte Carlo, explained from first principles"), traces to this folder.

| File | Use |
|:---|:---|
| `_reading_list_mrio_uncertainty.md` | A curated, DOI'd tier list - start here |
| `lenzen_et_al_2010_uncertainty_analysis_mrio_uk_carbon.pdf` | The method template; the lognormality argument |
| `rodrigues_et_al_2018_uncertainty_consumption_based_carbon.pdf` | Correlation between country accounts; independence understates by half |
| `schulte_et_al_2024_uncertainty_ghg_accounts_mrio.pdf` | Per-account uncertainties at EXIOBASE resolution; emission accounts, country CV 4 % against sector 94 %; footprints 3 % against 18 % |
| `schulte_et_al_2026_correlation_uncertainty_data_disaggregation.pdf` | Disaggregation induces negative correlations |
| `schulte_et_al_2021_relaxing_import_proportionality_mrio.pdf` | Structural uncertainty from the import-proportionality assumption |
| `wood_et_al_2019_variation_trends_consumption_based_carbon.pdf` | Cross-database spread; **Denmark CBCA RSD 8.8 %**, named as a shipping-driven outlier |
| `stadler_et_al_2018_exiobase3_construction.pdf` | Construction uncertainty |
| `jakobs_et_al_2021_price_variance_hybrid_lca_carbon_footprint.pdf` | Price variance - relevant to monetary-model limits |
| `moran_et_al_2018_carbon_footprints_13000_cities.pdf` | Feedback-effect magnitude used to justify simplified SNAC |

## 3d. Danish Energy Agency Global Report - the official Danish method

`~/workzone/projects/codebase/github/ce_mriot/docs/references/danish_energy_agency/` - **95 PDFs**

**This is where Denmark's official consumption-based method is documented**, and
it is the single most important source for positioning this study against
national practice. It is *not* in the folders where one would first look: the 64
policy PDFs under `dk_kommune_footprints/.../national_climate_policy/` contain
**zero** occurrences of EXIOBASE, MRIO or input-output. The method lives only in
the Global Report's background memoranda, reachable via
`methods/emission_inventories/danish_energy_agency_global_report_pointer.md`.

| Sub-collection | Why it matters |
|:---|:---|
| `danish_energy_agency_2024_climate_footprint_consumption/` | **`..._method_assumptions.pdf` §3.1.1 names the model.** |
| `danish_energy_agency_2024_denmarks_global_climate_impact/` | The headline Global Report |
| `danish_energy_agency_2024_international_transport/` | Shipping and aviation treatment - directly relevant to our reallocation |
| `danish_energy_agency_2024_projection_climate_footprint_consumption/` | Forward projections - relevant to mitigation scenarios |
| `danish_energy_agency_2024_key_indicators_consumption/` | Indicator definitions |

**What DEA actually uses**, verbatim from the method annexe: a **coupled IO
model** whose five subcomponents are Danish IO tables from Statistics Denmark;
Statistics Denmark emission accounts on DCE coefficients; *"EE-MRIO database in
the form of **EXIOBASE, version 3.9.2**"*; Danish foreign-trade statistics; and
DCE land-use data. EXIOBASE 3.9.2's country data are themselves *"updated to
2020 with accounting data (supply-use tables) from the **FIGARO** database"*.

So the official Danish chain is **FIGARO supply-use → EXIOBASE 3.9.2 → coupled
to Danish national accounts and emission accounts**. Two consequences for this
study: the official method is EXIOBASE-based, so our model family is the same
one Denmark uses; and it runs a **newer EXIOBASE release (3.9.2) than ours
(3.8.2)**, which bears on decision D8.

They also state the coupled model's weakness themselves: *"the global balance
between imports and exports, which the EE-MRIO database contains, is broken when
data for individual countries changes."*

## 4. Cross-project single sources

| Source | Path |
|:---|:---|
| Cabernard et al. 2019 (+SI) - target-sector scope 3 | `~/Library/CloudStorage/OneDrive-Personal/_Projects/2026_project/AFRIMAT/docs/references/articles/methods/footprint_methodologies/` |

## 5. Data stores (not literature, but pinned for the same reason)

| Store | Path |
|:---|:---|
| EXIOBASE releases (v3.6, v3.7, v3.8.2, v3.10.2, hybrid v3.3.18) | `~/Library/CloudStorage/OneDrive-Personal/Data/lca/input_output/mrio/exiobase/versions/` |
| Characterisation factors (IMPACT World+ v2.2.1, IPCC AR6 chapter 7 + SM) | `data/bronze/characterisation/` - provenance and licence in `SOURCES.txt` |
| Danish registers cached in-repo | `data/bronze/medstat/` (medicine sales), `data/bronze/tu_travel/` (national travel survey), `data/bronze/dst_capital/` (NABK69), `data/bronze/input_output/` (117-industry IO tables) |

---

## Sources located but deliberately not mirrored

| Source | Why not |
|:---|:---|
| ReCiPe 2016 v1.1 characterisation factors (RIVM) | Freely downloadable but **not openly licensed**; no AR6 update exists; its perspective is a fourth GWP revision. IMPACT World+ was chosen instead |
| Dawkins et al. 2018 (*JCLP* 209:1578-1592) | The citation for the SNAC-versus-raw effect size; absent from all local folders |
| AR6 WG3 Annex II | Referenced for the inventory methane split; the WG1 chapter carries what we need |

## Known defect in a local copy

`methods/uncertainty/schulte_et_al_2024_uncertainty_greenhouse_gas_emission_accounts_gmrio.pdf`
is a **truncated or corrupt download** - standard extractors fail and pages
beyond the third are unrecoverable. The published version is at
doi:10.5194/essd-16-2669-2024 with data at Zenodo 10.5281/zenodo.10041196.
Worth re-downloading, because it is the best available per-account uncertainty
and correlation dataset at EXIOBASE resolution.

## Pinned reference folders (September 2026)

Pinned for this study and for future figure and schema work. Paths are on Albert's
OneDrive; nothing from them is redistributed in this repository.

| Folder | What it is for | Status |
|:---|:---|:---|
| `Career/data_engineer/library/data_visualization/` | Figure design authority: Wickham *ggplot2: Elegant Graphics for Data Analysis*; **The Economist (2017) visual style guide**; Lupton *Sankey view* documentation; **Katsnelson (2021) fixing figures for colour blindness** | pinned; consult before designing any new figure |
| `Career/data_engineer/library/r_programming/` | R and presentation craft: Duarte *HBR Guide to Persuasive Presentations*; Kampakis *Decision-Maker's Handbook to Data Science*; AWS data-potential report | pinned |
| `Data/lca/input_output/mrio/classifications/concordances/` | MRIO classifications and concordances (see the note below) | pinned; source of record for aggregations |

### What the concordance folder actually contains, and what we use

Inspected 8 September 2026.

* **`Industry grouping.xlsx`** - an **ISIC Rev. 3, manufacturing-only** grouping (divisions
  15-37) with a *technology-intensity* classification (Low / Mid / High tech), cross-walked
  to CEPII BACI, UNIDO INDSTAT and OECD TiVA. It is a genuinely useful **secondary**
  aggregation - a technology-intensity view of the manufactured inputs to health care - but
  it is **not a replacement** for the study's whole-economy grouping: it covers no
  agriculture, mining, energy or services, and EXIOBASE's 163 industries span all of those.
  **Now wired.** The missing link is the EXIOBASE developers' own
  `ISIC REV. 3 - EXIOBASE2.0.xlsx`, which is already on disk at
  `concordances/exiobase/developers_concordances/Other_Ind_Prod/` (byte-identical to the
  copy mirrored by the BONSAI project at
  `github.com/BONSAMURAIS/correspondence_tables`, and originally from the EXIOBASE
  developer set linked from exiobase.eu; EXIOBASE terms, CC BY-SA 4.0).
  `data/bronze/concordances/exiobase_industry_to_isic_rev3.csv` derives from it:
  **138 of 163 EXIOBASE industries** carry an ISIC Rev. 3 division, of which 44 fall in
  manufacturing divisions 15-37 and so carry your Low / Mid / High technology group.
  `HEAL` maps one-to-one to division 85, *Health and social work*.
  Two limits, stated rather than smoothed over: 25 industries have no row in the ISIC
  table because the hybrid release renumbers them (`i24.x`, `i26.w.1`, `i40.2`, `i90.x`),
  and 5 span several divisions (quarrying 14/15, private households 95/96/97,
  extra-territorial 93/99) - for those the lowest division is taken as primary and the
  full set is kept in `isic_multi_division`, so the assignment is visibly a choice.
  No direct EXIOBASE → ISIC Rev. 4 table exists; the NACE Rev. 2 route is available but
  weaker (161 industries, only 143 one-to-one).
* **`exio_Classifications_v_3_3_18.xlsx`** - EXIOBASE activity, product, country, resource,
  land, emission and waste classifications. Sheets: `Activities`, `Products_HSUTs`,
  `Products_HIOT`, `Correspondence_products`, `Country`, `Priority industry`, and others.
* **`CountryMappingEXIOBASE.xlsx`**, **`concordance_exio_eora_icio.xlsx`**,
  **`concordances_literature.xlsx`** - country and cross-MRIO correspondences.
* **`DK-IOT_health_subsectors.xls`** - Danish health sub-sector IO detail. Directly relevant
  to the sub-sector limitation in
  [`docs/revision/uncertainty.md`, section 7.3](revision/uncertainty.md#73-one-health-industry-so-no-genuine-sub-sector-detail);
  the route to genuine per-function recipes runs through this file.
* **Giljum et al. (2019)** on data deviations between EXIOBASE, Eora and ICIO - supports the
  model-family argument in `06_benchmarks_validation`.

### The aggregations this study uses, now explicit

Both are exported as editable concordances rather than left implicit in a workbook:

| File | Rows | Content |
|:---|:---|:---|
| `data/bronze/concordances/exiobase_industry_to_group.csv` | 163 | EXIOBASE industry code and name → one of 19 industry groups |
| `data/bronze/concordances/exiobase_region_to_world_region.csv` | 49 | region code and name → one of 6 world regions |

They are the source of `dim_industry_group` and `dim_region.world_region` in the star
schema, so correcting a grouping is a one-file edit followed by a rebuild.
