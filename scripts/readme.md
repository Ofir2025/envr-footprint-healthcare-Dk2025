# Pipeline entry points

- `notebooks/`: exploratory notebooks and rendered notebook assets.

Python implementation and pipeline entry points live under `src/` and are run
as modules with `PYTHONPATH=src python3 -m ...`. For example:

```bash
PYTHONPATH=src python3 -m analysis.main_2025
```

`analysis.main` is the superseded Netherlands entry point (Steenmeijer et al.
2022 replication), kept for provenance only. It refuses to run: its source
workbook is not in this repository, and the unmodified script wrote
intermediates and results directly into the published `data/gold` layer.
`analysis.main_2025` is the Danish study's entry point and replaces it.

The background stages are available under
`pipelines.prep_background` and
`pipelines.prep_background_2025`. They require the
source data and prepared Exiobase objects.
