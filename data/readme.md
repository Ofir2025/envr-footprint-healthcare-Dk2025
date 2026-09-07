# Data layout

The repository uses a medallion-style data boundary:

- **Bronze**: source workbooks, downloaded Exiobase files, and unmodified
  country inputs. These are retained for provenance and are never edited by
  modelling scripts.
- **Silver**: cleaned inputs under `data/silver/inputs/` and generated
  background MRIO objects under `data/silver/background/`.
- **Gold**: published model outputs under `data/gold/results/`.

New files should use lowercase `snake_case` names and include the source and
analysis year where relevant. Temporary files, editor lock files, and pipeline
outputs must not be committed.
