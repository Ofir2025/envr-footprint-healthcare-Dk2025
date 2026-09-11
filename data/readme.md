# Data layout

The repository uses a medallion-style data boundary:

- **Bronze**: source workbooks, downloaded Exiobase files, and unmodified
  country inputs. These are retained for provenance and are never edited by
  modelling scripts.
- **Silver**: transformed bronze products, one folder per bronze provider
  folder (`data/silver/dst_supply_use/`, `data/silver/exiobase/`, and so on);
  the script-to-script handoff workbooks under `data/silver/handoff/`; and
  generated background MRIO objects under `data/silver/background/`.
  `data/silver/readme.md` states the layer's contract.
- **Gold**: published model outputs under `data/gold/results/`.

New files should use lowercase `snake_case` names and include the source and
analysis year where relevant. Temporary files, editor lock files, and pipeline
outputs must not be committed.
