# Statistics Denmark supply-use tables and household expenditure vector

The detailed Danish supply-use tables and the household expenditure detail
behind the 2019 healthcare expenditure boundary. `analysis.extra_functions`
reads them to build the healthcare totals and the eldercare share of social
work, which are the two quantities the whole Danish scope rests on.

| item | value |
|:---|:---|
| Provider | Statistics Denmark, national accounts |
| Dataset | Detailed supply-use tables (UMAT), 2019; household consumption by COICOP purpose, 2019 |
| URL | <https://www.dst.dk/en/Statistik/dokumentation/Times/national-accounts/supply-and-use-tables> |
| Licence | Statistics Denmark open data; free reuse with attribution |
| Retrieved | in the repository from 2026-09-07 (`55fd8ef`). Neither workbook is published under these filenames: both are manual exports, and the Danish default sheet names (`Ark1`) are the trace of that |

## Files

| file | size | sheets | unit |
|:---|:---|:---|:---|
| `dk_umat_2019.xlsx` | 17.9 MB | 8 | 1000 DKK |
| `expenditure_vector_dk_2019.xlsx` | 275 kB | 2 | 1000 DKK |

### `dk_umat_2019.xlsx`

The detailed supply-use matrices, ~2400 products × ~244 industries and final
demand columns.

| sheet | shape | content |
|:---|:---|:---|
| `Ubas` | 2422 × 248 | use at basic prices |
| `Umargins` | 2422 × 244 | trade and transport margins |
| `Utaxes` | 2422 × 244 | taxes less subsidies on products |
| `Upurch` | 2422 × 244 | use at purchasers' prices |
| `Ubas_dk` | 2422 × 244 | use at basic prices, domestic origin |
| `Ubas_imp` | 2422 × 244 | use at basic prices, imported |
| `Vbas` | 2470 × 244 | supply at basic prices |
| `Imports` | 2470 × 4 | imports by product |

`Upurch = Ubas + Umargins + Utaxes` and `Ubas = Ubas_dk + Ubas_imp` are the two
identities the readers rely on.

### `expenditure_vector_dk_2019.xlsx`

Household and government consumption of health products at the COICOP detail the
healthcare boundary is drawn on.

| sheet | shape | content |
|:---|:---|:---|
| `Ark1` | 2366 × 20 | household consumption, transaction code 3110, by COICOP code |
| `Sheet1` | 2375 × 16 | the same plus marketed (3141) and non-market (3142) individual government consumption, with the HC.51 and HC.52 sums |

The COICOP codes that carry the boundary are `06112` pharmaceutical and other
medical products, `06130` therapeutic appliances and equipment, `06200`
out-patient services and `06300` hospital services. `Sheet1` states its own unit
in cell A1: **all prices are in 1000 DKK**.

**Caveat.** `Sheet1` carries live Excel formulas (`=SUM(D5:D2366)`) rather than
values in its summary rows, so a reader that does not evaluate formulas sees the
formula string. The pipeline does not read this workbook: it is the documentary
source for the 2019 expenditure split, which `analysis.extra_functions` derives
from `dk_umat_2019.xlsx` instead.

**Rebuilding this folder.** There is no URL that returns these two files.
Statistics Denmark's own published supply-use tables are coarser than
`dk_umat_2019.xlsx`, and for 2021-22 only a preliminary commodity system is
available (`docs/methods/methods.md`, source table). Obtaining the detailed UMAT
for a year means requesting it from Statistics Denmark's national-accounts
division. Until then this folder cannot be reconstructed from a public source,
and that is stated here rather than left for a reader to discover.

**What actually reads this folder.** `analysis.extra_functions` opens
`dk_umat_2019.xlsx`, sheet `Ubas` only — the use table at **basic** prices, which
is why no purchaser-to-basic conversion is applied downstream and why
`Conversion` is 1.0 in the silver expenditure frame. Reading `Upurch` instead
would change the price basis and break that assumption silently. The boundary is
COICOP purposes 06112, 06130, 06200, 06300 and 12401, summed over every
individual-consumption transaction column present.
