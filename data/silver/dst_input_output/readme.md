# Silver: Danish water-transport domestic share

Mirrors `data/bronze/dst_input_output/`. One table, holding the sea-transport
reallocation's target share $\phi$ per Statistics Denmark table year, together
with the two quantities it is the quotient of — so a reader can check the
division rather than trust it.

| item | value |
|:---|:---|
| Bronze source | `data/bronze/dst_input_output/input_output_en_{2016,2019,2022}.xlsx`, sheet `DIO` (Statistics Denmark) |
| Produced by | `analysis.build_shipping_inputs` |
| Read by | `analysis.dk_shipping_correction` |
| Rebuild | `PYTHONPATH=src .venv/bin/python -m analysis.build_shipping_inputs` |
| In version control | **no** — regenerable from the tracked bronze workbooks |

## Files

| file | derives from | transformation | rows × cols | size |
|:---|:---|:---|:---|:---|
| `dst_water_transport_domestic_share.csv` | the three `input_output_en_<year>.xlsx` workbooks | the `DIO` sheet's row 500000 located between the `Danish production` and `Imports` block headers, its 117 industry deliveries summed, divided by its `Total` | 3 × 7 | 355 B |

## The transformation

$$\phi(t) = \frac{\sum_{j=1}^{117} d_{\mathrm{wt},j}(t)}{x_{\mathrm{wt}}(t)}$$

where $d_{\mathrm{wt},j}$ is the delivery of row 500000 (Water transport) of the
`DIO` sheet to Danish industry $j$, and $x_{\mathrm{wt}}$ is that row's `Total`.
Both are in 1000 DKK, so $\phi$ is dimensionless and the crowns cancel.

The `DIO` sheet is the **domestic** input-output table. The `IO` sheet is the
total table, domestic plus imported; only the domestic one measures what share of
a Danish industry's output Danish industries actually buy. The 117 product codes
repeat in both the Danish-production and the Imports block of `DIO`, which is why
the row has to be located between the two block headers rather than by code
alone.

## Columns

| column | unit | meaning |
|:---|:---|:---|
| `background_year` | year | which background year consumes this row; empty for the cross-check year, which serves none |
| `dst_table_year` | year | year of the Statistics Denmark workbook read |
| `domestic_intermediate_dkk` | 1000 DKK | numerator: row 500000's deliveries to the 117 Danish industries |
| `row_total_dkk` | 1000 DKK | denominator: row 500000's `Total` |
| `phi` | dimensionless | the quotient, $\phi$ |
| `source_workbook` | — | file name the row was read from |
| `retrieved` | date | ISO-8601 date the workbook was last read |

## The 2019 row is a validation, not an input

Rørmose Jensen & Iliev (2022, pp. 11-12) publish the national-accounts share for
2019 only. That year is **not** a background year of this study — the 2019
analysis runs on the 2016 background — so its row serves no run. It is here
because reproducing their 9 % to within 0.3 percentage points is what licenses
reading the other two years off the same table, and writing it to silver lets the
consumer re-assert the cross-check on every run without reopening bronze.
`dk_shipping_correction.domestic_share_rows` asserts it.

| `dst_table_year` | $\phi$ | role |
|:---|:---|:---|
| 2016 | 0.0774 | applied, background 2016 (analysis year 2019) |
| 2019 | 0.0931 | cross-check against the published 0.09 |
| 2022 | 0.0651 | applied, background 2022 (analysis year 2022) |

## Caveat

**Read this file with `float_precision="round_trip"`.** pandas' default CSV
parser is not correctly rounded and drops the last bit of a float. $\phi$
multiplies a row block of $\mathbf{A}$ before a Leontief inversion, so that bit
is a published number.
