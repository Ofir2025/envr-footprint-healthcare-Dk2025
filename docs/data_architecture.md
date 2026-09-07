# Data architecture

The repository follows a local medallion-style ELT layout:

```text
data/bronze/              immutable source downloads and raw country inputs
data/silver/inputs/       validated, model-ready country inputs
data/silver/background/   generated MRIO/background objects
data/gold/results/        published analysis outputs
```

Country-specific CSV/TSV inputs carry an `ISO2` column and use the same code
in their filenames (`nl_` for Netherlands, `dk_` for Denmark). The Denmark
pipeline reads its immutable source from Bronze, writes its transformed
inputs to Silver, and never overwrites the Bronze source.

Run modules with `PYTHONPATH=src`; source code is under `src/`, while
`scripts/` is reserved for notebooks and lightweight operational helpers.
