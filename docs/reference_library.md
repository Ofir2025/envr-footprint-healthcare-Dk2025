# Reference library — pinned locations

Every literature source this project draws on, with its location, so that a
claim can be checked and so the same libraries can be reused by later work.
**These are the source of truth. Consult them before searching online**, and
when an online source is used instead, say so and say why the local library was
insufficient.

Paths are absolute because the libraries live outside this repository.

---

## 1. Project library — health-sector footprints

`envrfootprint_healthcare/docs/references/` — **42 items**

The studies this project replicates or benchmarks against, and the method papers
its equations come from.

| Cluster | Key items |
|---|---|
| **Replication targets** | Steenmeijer et al. 2022 (the template, + the Lancet appendix and the fuller RIVM report 2022-0159 in `reports/source/`); Eckelman & Sherman 2016 (+ S1–S5 tables); Malik et al. 2018 (+SI) and 2021 (+SI); Lenzen et al. 2020 (+SI directory) |
| **Danish EXIOBASE remedies** | **Rørmose Jensen & Iliev 2022** — the coupled model; Palm et al. 2019 (+SI) — simplified SNAC; Tukker et al. 2018 — the method taxonomy |
| **Scope and double counting** | Wood & Hertwich 2018; Cabernard et al. 2019 (+SI, at the AFRIMAT path below) |
| **Danish context** | Arup 2025 Denmark health fact sheet; Healthcare Denmark 2024; Fagerberg et al. 2017 |
| **Bottom-up items** | Tennison et al. 2021 (+2 appendices); Kouwenberg et al. 2024; Belkhir & Elmeligi 2018; Jeswani & Azapagic 2019 |
| **Comparators** | Pichler et al. 2019 (+SI); Karliner et al. 2019; Chung & Meltzer 2009; Doucet et al. 2025 (ICIO) |

## 2. Kommune-project library — the largest resource

`dk_kommune_footprints/docs/references/` — **896 items**

Assembled for the municipal footprint project; most of its method material
applies directly here.

| Subtree | Items | Why it matters here |
|---|---|---|
| `methods/emission_inventories/` | 104 | Danish National Inventory Document (Nielsen et al. 2026); Gravgaard et al. 2009 on GHG emissions of the Danish economy; **`danish_energy_agency_global_report_pointer.md`** |
| `methods/mrio_exiobase_io_theory/` | 78 | IO theory; `input_output_theory/` holds Melo 2019 on bottom-up versus top-down environmental extensions, and the Statistics Denmark ADAM model |
| `methods/denmark_data_statistics/` | 68 | **Statistics Denmark 2019 environmental-economic accounting**; regional accounts; household budget survey; municipal energy and GHG; `energy_economy_reports/` |
| `methods/denmark_studies_comparators/` | 38 | **Schmidt & Merciai 2023, GHG emissions of Danish consumption 2016** — a directly comparable Danish consumption footprint; Ghosh et al. 2014 |
| `methods/classifications_standards/` | 10 | **GHG Protocol/IPCC AR6 GWP values**; WRI/WBCSD scope 3 technical guidance; COICOP 2018; NACE Rev. 2 |
| `methods/uncertainty/` | 9 | **The primary uncertainty literature**: Lenzen et al. 2010; Rodrigues et al. 2018 (+SI); Schulte et al. 2021, 2024, 2026; Badr et al. 2026 review |
| `introduction/denmark_climate_policy/` | 203 | Danish Climate Act; DEA Climate Status and Outlook; **DEA 2025 Denmark global climate impact**; Climate Council 2025 |
| `discussion/food_diet_agriculture/` | 124 | Relevant to the food and catering contribution group |
| `introduction/subnational_urban_footprints/` | 48 | Downscaling and subnational attribution |

## 3. MRIO teaching library

`~/Library/CloudStorage/OneDrive-Personal/Career/professor/teaching/MRIO_literature/`

| Subfolder | Items | Contents |
|---|---|---|
| `methods/` | 209 PDFs | `approaches/` (16, incl. Owen 2023 LACA); `data_methods/` (6, incl. Eurostat 2022 RME); `hybrid_io_lca/` (48, incl. Merciai 2022 EXIOBASE-hybrid v4, Nakamura 2023 textbook, Jakobs 2023 thesis); `modelling/` (23); `theory_tools/` (core theory, environmental models, integrated assessment, reviews, software) |
| `uncertainty/` | 23 items | Includes a curated, DOI'd reading list (`_reading_list_mrio_uncertainty.md`); Lenzen 2010; Rodrigues 2018; Schulte 2021/2024/2026; Wood 2019; Stadler 2018; downscaling literature |

## 4. Cross-project single sources

| Source | Path |
|---|---|
| Cabernard et al. 2019 (+SI) — target-sector scope 3 | `~/Library/CloudStorage/OneDrive-Personal/_Projects/2026_project/AFRIMAT/docs/references/articles/methods/footprint_methodologies/` |

## 5. Data stores (not literature, but pinned for the same reason)

| Store | Path |
|---|---|
| EXIOBASE releases (v3.6, v3.7, v3.8.2, v3.10.2, hybrid v3.3.18) | `~/Library/CloudStorage/OneDrive-Personal/Data/lca/input_output/mrio/exiobase/versions/` |
| Characterisation factors (IMPACT World+ v2.2.1, IPCC AR6 chapter 7 + SM) | `data/bronze/characterisation/` — provenance and licence in `SOURCES.txt` |
| Danish registers cached in-repo | `data/bronze/medstat/` (medicine sales), `data/bronze/tu_travel/` (national travel survey), `data/bronze/dst_capital/` (NABK69), `data/bronze/input_output/` (117-industry IO tables) |

---

## Sources located but deliberately not mirrored

| Source | Why not |
|---|---|
| ReCiPe 2016 v1.1 characterisation factors (RIVM) | Freely downloadable but **not openly licensed**; no AR6 update exists; its perspective is a fourth GWP vintage. IMPACT World+ was chosen instead |
| Dawkins et al. 2018 (*JCLP* 209:1578–1592) | The citation for the SNAC-versus-raw effect size; absent from all local folders |
| AR6 WG3 Annex II | Referenced for the inventory methane split; the WG1 chapter carries what we need |

## Known defect in a local copy

`methods/uncertainty/schulte_et_al_2024_uncertainty_greenhouse_gas_emission_accounts_gmrio.pdf`
is a **truncated or corrupt download** — standard extractors fail and pages
beyond the third are unrecoverable. The published version is at
doi:10.5194/essd-16-2669-2024 with data at Zenodo 10.5281/zenodo.10041196.
Worth re-downloading, because it is the best available per-account uncertainty
and correlation dataset at EXIOBASE resolution.
