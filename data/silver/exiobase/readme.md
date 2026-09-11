# Silver: EXIOBASE industry reporting groups

Mirrors `data/bronze/exiobase/`. One table: the aggregate reporting group of every
EXIOBASE industry, lifted out of the classification workbook so the group labels
the published contribution tables carry and the group labels the sensitivity band
carries are the same labels, read from the same place.

| item | value |
|:---|:---|
| Bronze source | `data/bronze/exiobase/classifications.xlsx`, sheet `disagg_ind` (EXIOBASE consortium) |
| Produced by | `analysis.build_shipping_inputs` |
| Read by | `analysis.dk_shipping_correction` |
| Rebuild | `PYTHONPATH=src .venv/bin/python -m analysis.build_shipping_inputs` |
| In version control | **no** — `classifications.xlsx` is tracked, so one command rebuilds this table in any clone, and no document quotes a number from it: the group labels it assigns travel into gold in the published tables' own `sector_group` columns, where a reader reads them |

`classifications.xlsx` is one copy for every EXIOBASE release, so it sits in the
bronze `exiobase/` root rather than under a release subfolder, and this product is
release-independent too.

## Files

| file | derives from | transformation | rows × cols | size |
|:---|:---|:---|:---|:---|
| `exiobase_industry_sector_group.csv` | `classifications.xlsx`, sheet `disagg_ind`, `skiprows=5` | the `Code`, `Description` and `AggDescription` columns taken, whitespace stripped, rows with no code dropped | 169 × 3 | 11 kB |

## Columns

| column | unit | meaning |
|:---|:---|:---|
| `exiobase_industry_code` | — | the `A_`-prefixed industry code as the background's own labels carry it, e.g. `A_PARI` |
| `exiobase_industry_name` | — | the industry's published description, e.g. `Cultivation of paddy rice` |
| `sector_group` | — | the aggregate reporting group, e.g. `Food and catering`, `Transport` |

## Caveat

**169 rows, not 163.** The `disagg_ind` sheet carries the disaggregated industry
list, which is longer than the 163-industry vector the model's matrices are
indexed on. Join on `exiobase_industry_code`; do not assume positional alignment
with a 163-row array.
