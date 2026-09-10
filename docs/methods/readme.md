# Methods

The methodology behind this study: the EXIOBASE coupling this revision's
pipeline actually runs, the equations and data-source decisions behind each
approach, the published star schema, and Ofir Eriksen's own methodology
write-ups.

| File | Purpose |
|:---|:---|
| `02_snac_exiobase_and_footprint_accounting.md` | Simplified-SNAC, the EXIOBASE coupling, and footprint accounting. `analysis.build_dst_concordance`, which runs in the published pipeline, is specified against this document's import-bridge section. |
| `exiobase_version_vintage_and_classification.md` | Why EXIOBASE v3.8.2, not v3.10.2, and what the classification can and cannot say. |
| `star_schema.sql` | The canonical star schema DDL; the contract the published CSV/Parquet tables satisfy. |
| `eriksen_methodology_eldercare_excluded.md` (+ `.docx`) | Ofir Eriksen's methodology, eldercare excluded (COFOG 10). |
| `eriksen_methodology_eldercare_included.md` (+ `.docx`) | Ofir Eriksen's methodology, eldercare included. |

Subfolders, each with its own readme:

| Folder | Purpose |
|:---|:---|
| `danish_data_acquisition/` | The Danish data-access inventory and acquisition plan. |
| `replications/` | The per-study replication write-ups. |
