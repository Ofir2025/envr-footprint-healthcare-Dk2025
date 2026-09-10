# Methods

The methodology behind this study: the research blueprint, the equations and
data-source decisions behind each approach, the published star schema, and
Ofir Eriksen's own methodology write-ups. Reading notes on the wider hybrid
LCA and replication literature live in the two subfolders below rather than
here, so that this level stays about this study's own method.

| File | Purpose |
|:---|:---|
| `00_index_and_research_architecture.md` | Entry point into the four-part method blueprint below. |
| `01_danish_sut_and_health_disaggregation.md` | How the Danish supply-use tables are disaggregated to health-sector detail. |
| `02_snac_exiobase_and_footprint_accounting.md` | Simplified-SNAC, the EXIOBASE coupling, and footprint accounting. |
| `03_validation_uncertainty_software_and_scaling.md` | Validation, uncertainty, software implementation and scaling. |
| `04_sources_and_references.md` | Sources and references behind the blueprint. |
| `denmark_healthcare_footprint_replication_blueprint.md` | The replication blueprint for the Danish study. |
| `exiobase_version_vintage_and_classification.md` | Why EXIOBASE v3.8.2, not v3.10.2, and what the classification can and cannot say. |
| `hybrid_lca_palm_hagenaars_denmark_replication_checkpoint.md` | Reading notes and replication checkpoint for the hybrid-LCA/coupled-MRIO literature. |
| `malik_et_al_2018_2021_australian_healthcare_reading_notes.md` | Reading notes on the Malik et al. Australian healthcare studies. |
| `star_schema.sql` | The canonical star schema DDL; the contract the published CSV/Parquet tables satisfy. |
| `eriksen_methodology_eldercare_excluded.md` (+ `.docx`) | Ofir Eriksen's methodology, eldercare excluded (COFOG 10). |
| `eriksen_methodology_eldercare_included.md` (+ `.docx`) | Ofir Eriksen's methodology, eldercare included. |

Subfolders, each with its own readme:

| Folder | Purpose |
|:---|:---|
| `danish_data_acquisition/` | The Danish data-access inventory and acquisition plan. |
| `hybrid_lca_reading_notes_and_denmark_health_synthesis/` | Reading notes on hybrid LCA studies and their synthesis for Denmark. |
| `replications/` | The per-study replication write-ups. |
