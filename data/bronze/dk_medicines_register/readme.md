# Danish Medicines Agency ATC sales register

National sales of medicines by ATC code, for 2019 and 2022. The study reads one
ATC group from it — **N01AB**, the volatile anaesthetic agents — and that single
extraction replaced a population-scaled Dutch proxy with a Danish measurement.

| item | value |
|:---|:---|
| Provider | Danish Medicines Agency (Lægemiddelstyrelsen) |
| Dataset | medstat.dk, the national medicine statistics register — mandatory reporting, covering all sales in Denmark |
| URL | <https://medstat.dk/> — the "Download data" page serves one `<year>_atc_code_data.txt` per year |
| Licence | Danish public-sector open data; free reuse with attribution |
| Retrieved | 2026-09-07 (`6fff025`) |

## Download step

From <https://medstat.dk/>, download the yearly ATC data file for each year
wanted and keep its published name, `<year>_atc_code_data.txt`. The files are
served exactly as stored here: **no transformation has been applied**, which is
the bronze contract. A version with named columns is a silver product —
`data/silver/inputs/dk_atc_sales_<year>.csv`, written by
`analysis.build_atc_sales`.

| file | size | rows | encoding |
|:---|:---|:---|:---|
| `2019_atc_code_data.txt` | 76.9 MB | 1,833,789 | latin-1 |
| `2022_atc_code_data.txt` | 76.1 MB | 1,814,588 | latin-1 |

## Raw layout

Semicolon-separated, **no header row**, exactly 14 fields on every line, a
trailing empty field, no quoting. Fields are positional and are numbered
one-based below.

| position | name | verified content |
|:---|:---|:---|
| 1 | `atc` | ATC code at any level: `A`, `A01`, `A01A`, `A01AA`, `A01AA01` |
| 2 | `year` | reference year; constant within a file |
| 3 | `sector` | `0` primary care, `1` hospital, `2` all sectors |
| 4 | `region` | `0` whole country, `1`-`5` the five Danish regions |
| 5 | `sex` | `A` all, `1`, `2`, `0` |
| 6 | `age_group` | `A` all, or a band such as `00-17`, `18-24`, `25-44`, `45-64`, `65-79` |
| 7 | `field_07` | integer; populated only on sex- or age-specific rows. **Meaning not established here** |
| 8 | `field_08` | one-decimal number. **Meaning not established here** |
| 9 | `field_09` | integer, population-scale. **Meaning not established here** |
| 10 | `field_10` | integer, smaller than field 9. **Meaning not established here** |
| 11 | `volume_thousand_units` | **the field this study reads.** Volume, in thousands of the product's own unit |
| 12 | `field_12` | one-decimal rate accompanying field 11. **Meaning not established here** |
| 13 | `field_13` | integer or `>99`. **Meaning not established here** |
| 14 | — | always empty; an artefact of the trailing separator |

Positions 7 to 10, 12 and 13 are named positionally on purpose. Their meaning
could not be established from the file itself or from anything in this
repository, and inventing a name for a column in a published schema is worse
than admitting the gap. medstat.dk's own file description is the place to
resolve them; nothing in this study depends on them.

## The unit trap

Field 11 is documented by the register as **"volume in 1.000 units"**, and what
"unit" means depends on the product. For **N01AB** every marketed product is an
inhalation liquid, so the unit is millilitres and **the field is litres**. Read
it as anything else and the anaesthetic term is wrong by three orders of
magnitude.

The rows the study reads are `sector = 2` (all sectors) and `region = 0` (whole
country), `sex = A`, `age_group = A`:

| ATC | agent | 2019, litres | 2022, litres |
|:---|:---|:---|:---|
| `N01AB06` | isoflurane | 17 | 15 |
| `N01AB07` | desflurane | 400 | 181 |
| `N01AB08` | sevoflurane | 2,714 | 2,400 |

Those six numbers are the integrity check for this folder: they are the values
`analysis.main_2025` carries in `DK_ANAESTHETIC_LITRES`, and a re-download that
does not reproduce them means the register has been revised or the field has
moved.

## Caveats

**Sales, not consumption.** The register records what was sold, not what was
administered or exhaled. The study applies a 5 % downward correction to
sevoflurane for the fraction metabolised rather than exhaled; the other two
agents are taken as fully exhaled.

**Sector totals are not additive with the parts you might expect.** `sector = 2`
is the total, and for the volatile agents primary-care sales are nil, so the
total equals the hospital figure. Do not add sectors 0, 1 and 2.

**ATC levels are nested.** `A`, `A01`, `A01A`, `A01AA` and `A01AA01` all appear
as rows in the same file. Summing the `atc` column double-counts.
