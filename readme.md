# envr-footprint-healthcare - The environmental footprint of the Dutch healthcare sector

## Repository organization

This project follows a medallion-style ELT boundary: source inputs are kept in
`data/bronze`, prepared MRIO objects in `data/silver`, and published results in
`data/gold`. Python implementation lives under `src/`; `scripts/` is reserved
for notebooks and lightweight operational helpers.

Use the `2019-update` branch for the current organization work. See
[`docs/data_architecture.md`](docs/data_architecture.md) for the data-flow
contract and [`data/readme.md`](data/readme.md) for naming guidance.
This root `readme.md` is the authoritative project guide; folder-level
`readme.md` files are scoped orientation notes only.
This project contains the model and some of the input data for the paper: 
*The environmental footprint of the Dutch healthcare sector: beyond environmental impact*
*Steenmeijer MA, Rodrigues JFD, Zijp MC, Waaijers-van der Loop SL. The Lancet Planetary Health (in press)*

The work is part of a research project at the RIVM - the national institute for public health and the environment, on building a knowledge base to support the healthcare sector in becoming more sustainable.

## Getting started (steps for the first run)
### Step 1: Additional input data
After cloning the project from this repository, it is necessary to download the **Exiobase 3.7 IOT_2016_ixi zip folder** from Zenodo: https://zenodo.org/record/3583071#.Y0MV7NhBw2w .
The unzipped file should be placed in `data/bronze/exiobase_v3_7`. Do not
change the internal Exiobase archive structure.
It is both possible to use newer versions (3.8 and up) and other years, but at this point it will  require manual adjustments in the model's scripts (e.g. F_hh should be changed into F_Y when using v3.8).

### Step 2: First run, preparing pickled EE-IO files
Before running the main script the first time, the Exiobase data will be processed into several pickled files. These files will later on be used to create the so-called **background** that contains all the elements needed for the main script.
Four pipeline modules are used under
`src/pipelines/prep_background/`.
These scripts need to be executed in the following order:
1. `load`, which filters the desired impact category and builds the MRIO dictionary
2. `leontief`, which calculates the Leontief inverse
3. `process`, which calculates total input (**x**) and the transaction matrix (**Z**)
4. `waste`, which processes the waste-production extension from the hybrid SUT

The prepared objects are written to `data/silver/background/pickled_mrio/`.

## Running the main script (main.py)
Run the Netherlands analysis as a module:

```bash
PYTHONPATH=src python3 -m analysis.main
```

The 2025 variant is available as
`analysis.main_2025`. Prepared MRIO objects are
written to `data/silver/background`; curated outputs are written to
`data/gold/results`.
The output from the model is stored in `data/gold/results/`.

### Output
For some of the output files, we use the following abbreviations
- **aggsec** = results aggregated on aggregated sector groups (19 groups)
- **aggsec_aggreg** = results aggregated on aggregated sector groups and global regions (19 sector groups for 6 global regions)
- **allsec** = = results aggregated on sector (163 sectors)
- **full** = unaggregated results, complete list (163 sectors for 49 countries/regions)
