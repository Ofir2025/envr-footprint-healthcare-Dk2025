# Statistics Denmark input-output tables, 117 industries

The published Danish national input-output workbooks, one per year, 2006 to
2022. They are the Danish-side evidence throughout the study: the expenditure
boundary, the domestic sea-transport share, the FIGARO cross-check and the
EXIOBASE-to-DST concordance all read from them.

| item | value |
|:---|:---|
| Provider | Statistics Denmark, national accounts |
| Dataset | Input-output tables, 117 industries, basic prices, current and previous-year prices, English edition |
| URL | <https://www.dst.dk/en/Statistik/dokumentation/Times/input-output-tables> |
| Licence | Statistics Denmark open data; free reuse with attribution |
| Retrieved | in the repository from 2026-09-07 (`55fd8ef`); the 2006-2015 workbooks arrived with the project scaffolding (`c898c90`) |

## Download step

One English workbook per year from the page above, saved under its published
name pattern `input_output_en_<year>.xlsx`. The two year-range subfolders the
files used to sit in (`2006_2015/`, `2016_2022/`) are gone: they were a filing
convention, not a property of the data, and every reader had to know which of
the two a year fell in. The folder is now flat and a reader needs only the year.

| file | years | size each | sheets |
|:---|:---|:---|:---|
| `input_output_en_2006.xlsx` … `input_output_en_2022.xlsx` | 2006-2022, one per year, 17 files | 1.7-2.2 MB | 9 |

## Sheet dictionary

Each workbook carries the same nine sheets. They are **not** header-first: the
banner occupies row 0, the six-digit industry codes row 2, and the row labels
column A. Readers pass `header=None` and locate the blocks by label.

| sheet | shape (2022) | content |
|:---|:---|:---|
| `IO` | 460 × 281 | total input-output table, industry by industry, 1000 DKK |
| `CP` | 473 × 173 | the same on the product classification |
| `DIO` | 460 × 281 | **domestic** input-output table — domestic production only, the sheet the sea-transport share is read from |
| `DCP` | 473 × 173 | domestic, product classification |
| `IO Customs`, `CP Customs`, `DIO Customs`, `DCP Customs` | 329-343 × 173-281 | the same four on the customs import definition |
| `Employment` | 246 × 13 | employment by industry |

Within a sheet: 117 six-digit industry columns matched by
`re.fullmatch(r"\d{6}", code)` on row 2, a `Total` column named in the row-0
banner, and the row labels split into a Danish-production block and an import
block by the two block labels the readers locate by name.

**Units.** Every monetary cell is **1000 DKK**, current prices, basic prices
unless the sheet says otherwise. Nothing in the model consumes DKK directly: the
expenditure conversion divides by the year's DKK-per-EUR average, and the
sea-transport share is a ratio inside the table, so its crowns cancel.

**Caveat.** 2016-2022 and 2006-2015 are published on the same 117-industry
grouping but the earlier range was revised less recently. Only 2016 onward is
used for anything that enters a published number; the earlier years serve the
concordance's time-series diagnostics.
