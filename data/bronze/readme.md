# Bronze: source data, exactly as obtained

Bronze is immutable. No modelling script writes here, and a generated file in
this tree is a defect regardless of its content: prepared inputs belong in
`data/silver/`, published tables in `data/gold/results/`.

Folders are grouped by **who published the data**, because provenance is what
this layer exists to carry. Each folder's `readme.md` gives the provider, the
dataset, a DOI or URL, the retrieval date, the licence, the exact query or
download step, a file table with sizes and shapes, and a column dictionary for
every tabular file. A clone with an empty `data/bronze/` should be able to
rebuild each folder from its readme alone.

## Index

| folder | provider | holds |
|:---|:---|:---|
| `classification_concordances/` | this study, from EXIOBASE and DST classifications | EXIOBASE industry and region bridges to ISIC, NACE, DST DB07 and the reporting groups |
| `dk_medicines_register/` | Danish Medicines Agency (medstat.dk) | national medicine sales by ATC code, 2019 and 2022 |
| `dk_travel_survey/` | DTU Center for Transport Analytics; this study | the Danish national travel survey reports and the commuting and private-travel workbooks derived from them |
| `dst_capital_stock/` | Statistics Denmark | NABK69 gross fixed capital formation for the health industries |
| `dst_emission_accounts/` | Statistics Denmark | DRIVHUS, MRU1 and ENE2HA environmental-economic accounts by industry |
| `dst_input_output/` | Statistics Denmark | the published 117-industry input-output workbooks, 2006-2022 |
| `dst_supply_use/` | Statistics Denmark | the detailed supply-use tables and the household expenditure vector |
| `eurostat_figaro/` | Eurostat | FIGARO supply, use and footprint extracts |
| `exiobase/` | EXIOBASE consortium; CML Leiden | the background MRIO tables and the classification and characterisation workbooks |
| `exiobase_capital/` | Södersten, Wood & Hertwich | the EXIOBASE capital-formation matrix |
| `exiobase_characterisation/` | CIRAIG; IPCC | IMPACT World+ characterisation factors and the AR6 GWP source chapters |
| `netherlands_reference/` | CBS Netherlands; Steenmeijer et al. | the Dutch inputs of the replication this study extends |

## What is and is not in version control

Small public registers are tracked, including every `.csv` in every subfolder:
the repository `.gitignore` un-ignores `data/bronze/**/*.csv`, because the
author's global excludes file drops `*.csv` and that is exactly how
`dst_capital_stock/nabk69_health_assets_2022.csv` came to sit on one machine's
disk, read by `analysis.capital_gfcf`, and be absent from every clone.

Large or licensed third-party files are **not** tracked and must be fetched
from the URLs their folder readme gives: the EXIOBASE tables (symlinked, ~1.5 GB
per year), the IMPACT World+ workbooks and IPCC chapters, the FIGARO full-EU
IOT, and the two DTU travel-survey PDFs.

## Removed

Six files were deleted from the bronze root in this reorganisation. Each is
recorded with the evidence that established it as dead.

| file | why it went |
|:---|:---|
| `bottomup_data.txt` | pre-`ISO2` copy of `netherlands_reference/nl_bottomup_data.txt`; identical to it in every value, differing only by the absent `ISO2` column, and read by nothing (`analysis.main` and `analysis.main_2025` both read the `nl_` file) |
| `cbs_data_2016.csv` | pre-`ISO2` copy of `netherlands_reference/nl_cbs_data_2016.csv`, same evidence: identical values, no `ISO2` column, no reader |
| `bottomup_data_2025.txt` | a pipeline product, not a source. Its values are `nl_bottomup_data.txt` multiplied by a superseded scaling set (Commute 0.544, Visitor 0.636); `analysis.main_2025` now writes the live file to `data/silver/netherlands_reference/dk_bottomup_data_<year>.txt` on the 2026-09 factors, and every reader points there |
| `dk_data_2025.csv` | a pipeline product. `analysis.main_2025` writes the live copy to `data/silver/dst_supply_use/dk_data_<year>.csv`, which has five readers; the bronze copy had none |
| `dk_data_2025_raw.csv` | referenced by no module, no script, no document; an intermediate of the expenditure conversion that predates the silver layer |
| `commuting_private_travel_calculations_2025.xlsx` | superseded by `dk_travel_survey/commuting_private_travel_calculations_2026.xlsx`, which is the workbook `analysis.main_2025` cites for the 2026-09 commute and visitor factors. The 2025 workbook has a single undocumented sheet and no reader |

There is no `dk_bottom_up_inventories/` folder. The two bronze-root files that
would have filled it turned out, on reading them and their history, to be a
pre-`ISO2` copy of a Dutch source and a stale pipeline output; the Danish
bottom-up inventory itself is computed in `analysis.main_2025` from register and
survey quantities and written to silver. Bronze has no bottom-up source to hold.

`supply_tables_2015_2018.xlsx` was not removed but renamed: it is the Dutch CBS
supply table, and it now carries the `nl_` prefix its readers expect, at
`netherlands_reference/nl_supply_tables_2015_2018.xlsx`.

## Fixed defect

`analysis.build_dst_concordance` used to write
`classification_concordances/exiobase_industry_to_dst_db07.csv` into this layer.
A generated file in bronze breaks medallion rule 1, and it is now written to
`data/silver/classification_concordances/` instead, beside the bronze
concordance it is built from and under the silver folder mirroring it. Its column
dictionary moved with it. `analysis.build_star_schema` still reads the
hand-maintained concordances in this folder, which are sources.

## Moving an existing working copy

A working copy checked out before this reorganisation keeps its untracked
caches under the old directory names — `characterisation/`, `tu_travel/`,
`dst_capital/`, `exiobase_v3_7/`. Git moves only what it tracks, so those
directories survive the checkout with their untracked contents. Move the
contents into the new folder and delete the old directory; nothing reads the
old names any more.
