# Pipeline entry points

- `notebooks/`: exploratory notebooks and rendered notebook assets.

Python implementation and pipeline entry points live under `src/` and are run
as modules with `PYTHONPATH=src python3 -m ...`. For example:

```bash
PYTHONPATH=src python3 -m analysis.main
PYTHONPATH=src python3 -m analysis.main_2025
```

The background stages are available under
`pipelines.prep_background` and
`pipelines.prep_background_2025`. They require the
source data and prepared Exiobase objects.
