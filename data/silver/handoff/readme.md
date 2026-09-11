# Silver: script-to-script handoff

**Not part of the bronze mirror.** Everything else in `data/silver/` is a
transformed bronze source, named for the bronze folder it derives from. These are
not that. They are workbooks one module writes for another module to read back —
one script's private message to another, with no bronze folder to be named for
and no consumer outside the pair that owns them.

They are kept separate because the distinction is the one the medallion contract
turns on. A transformed source table is an **input**: it has a provider, a unit
dictionary, and a reason any consumer may read it. An interim workbook is a
**mechanism**: it exists because two scripts were written at different times and
communicate through a file rather than through a function call, and reading one
from outside the pair means depending on an implementation detail. Filing the two
kinds together is how six Excel workbooks came to sit in the published gold tree,
where the gold format check (C14, tabular data only) now refuses them.

| item | value |
|:---|:---|
| Written by | `analysis.main_2025` |
| Read by | `analysis.eriksen_tables`, `analysis.scopes_detail`, `analysis.uncertainty_2025` |
| Path constant | `paths.ERIKSEN_INTERIM_DIR` |
| Rebuild | `HC_ANALYSIS_YEAR=<year> HC_BACKGROUND_TAG=_snacship PYTHONPATH=src .venv/bin/python -m analysis.main_2025` |
| In version control | **no** — `.gitignore` drops `data/silver/handoff/*`, and un-ignores this readme only |

## Layout

```
handoff/eriksen_tables/01_eriksen_replication/<variant>/   one folder per lettered variant
handoff/eriksen_tables/scenarios/<scope>/                  one per unlettered boundary scenario
```

The subfolder is the same name `analysis.constants.eriksen_folder` gives the
variant's gold folder, resolved from all four configuration axes at once —
EXIOBASE release, sea-transport correction, sector boundary, capital treatment —
so a workbook and the published table built from it cannot come from two different
backgrounds without saying so. A boundary change that is not one of the author's
four lettered variants goes to `scenarios/<scope>/` instead, matching where its
results go.

## Files, per variant folder

Six workbooks. `<n>` is the number of region-industry nodes carried, 6,099 to
7,994 depending on the analysis; the shapes below are the 2022 headline variant.

| file | sheets | shape (2022) | size | what it is | read by |
|:---|:---|:---|:---|:---|:---|
| `expenditure_vector.xlsx` | `full`, `allsec`, `aggsec_aggreg`, `aggsec` | 7,987 × 11 | 474 kB | the healthcare final-demand vector $y_H$ in M.EUR, at four aggregations | `eriksen_tables` |
| `intensities.xlsx` | `full`, `allsec`, `aggsec_aggreg`, `aggsec` | 6,099 × 13 | 811 kB | the multipliers $c_i$ per node, one column per indicator | `eriksen_tables` |
| `contribution_analysis.xlsx` | `full`, `allsec`, `aggsec` | 7,992 × 13 | 783 kB | impact attributed to the **purchasing** node | `eriksen_tables`, `scopes_detail`, `uncertainty_2025` |
| `hotspot_analysis.xlsx` | `full`, `aggsec`, `aggsec_aggreg`, `aggreg`, `allreg`, `allsec` | 7,994 × 13 | 763 kB | impact attributed to the **producing** node | `eriksen_tables` |
| `contribution_full_detail.xlsx` | `Sheet1` | 7,992 × 13 | 766 kB | the raw-detail copy of the contribution analysis, unaggregated | — |
| `hotspot_full_detail.xlsx` | `Sheet1` | 7,994 × 13 | 678 kB | the raw-detail copy of the hotspot analysis | — |

Indicator columns carry their units in the column name, as the published tables
do: `Global warming (ktCO2eq)`, `Material extraction (kt)`, `Blue water
consumption (Mm3)`, `Land use (km2)`, `Waste generation (kt)`. The `full` sheet is
the one every reader takes; the aggregated sheets are written for inspection.

## Caveats

**A missing workbook is not an error to fall back from.** `eriksen_tables` skips
an analysis whose workbook is absent and says to run `analysis.main_2025`. That is
the right behaviour for a handoff: the producer has not run.

**These are not results.** Nothing here may be quoted, and nothing here is
checked by the gold audit. The published forms are the CSVs `eriksen_tables`
writes into `data/gold/results/01_eriksen_replication/<variant>/`.
