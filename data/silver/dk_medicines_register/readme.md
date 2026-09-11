# Silver: the Danish medicines register, with named columns

Mirrors `data/bronze/dk_medicines_register/`. The register arrives as 1.8 million
semicolon-separated lines with **no header row**; bronze keeps it exactly that
way, because a source with columns silently renamed is a source nobody can check
against the provider. This is where it becomes readable.

| item | value |
|:---|:---|
| Bronze source | `data/bronze/dk_medicines_register/<year>_atc_code_data.txt` (Danish Medicines Agency, medstat.dk) |
| Produced by | `analysis.build_atc_sales` |
| Rebuild | `PYTHONPATH=src .venv/bin/python -m analysis.build_atc_sales` |
| In version control | **no** — 78 MB per year; `.gitignore` drops `dk_atc_sales_*.csv` explicitly rather than relying on a personal excludes file |

## Files

| file | derives from | transformation | rows × cols | size |
|:---|:---|:---|:---|:---|
| `dk_atc_sales_2019.csv` | `2019_atc_code_data.txt` | latin-1 decoded to UTF-8; 14 positional fields given names; the always-empty trailing field dropped; every field read as text | 1,833,789 × 13 | 78.8 MB |
| `dk_atc_sales_2022.csv` | `2022_atc_code_data.txt` | the same | 1,814,588 × 13 | 78.0 MB |

Row counts are the bronze line counts exactly: the transformation renames and
re-encodes, and drops no row.

## Columns

Six of the fourteen bronze fields have a meaning this repository can
demonstrate. The rest keep positional names on purpose — inventing a plausible
name for a column whose content has not been established is worse than leaving
the gap visible, because the invented name is what the next reader trusts.

| column | unit | meaning |
|:---|:---|:---|
| `atc` | — | ATC code at any level: `A`, `A01`, `A01A`, `A01AA`, `A01AA01` |
| `year` | year | reference year; constant within a file |
| `sector` | code | `0` primary care, `1` hospital, `2` all sectors |
| `region` | code | `0` whole country, `1`-`5` the five Danish regions |
| `sex` | code | `A` all, or `0`, `1`, `2` |
| `age_group` | — | `A` all, or a band such as `00-17`, `45-64`, `65-79` |
| `field_07` | — | integer, populated only on sex- or age-specific rows. **Meaning not established** |
| `field_08` | — | one-decimal number. **Meaning not established** |
| `field_09` | — | integer, population scale. **Meaning not established** |
| `field_10` | — | integer, smaller than `field_09`. **Meaning not established** |
| `volume_thousand_units` | thousands of the product's own unit | **the field this study reads** |
| `field_12` | — | one-decimal rate accompanying `volume_thousand_units`. **Meaning not established** |
| `field_13` | — | integer, or the string `>99`. **Meaning not established** |

## The unit trap, and the build-time check

`volume_thousand_units` is the register's "volume in 1.000 units", and *unit*
means the product's own unit. For ATC **N01AB**, the volatile anaesthetics, every
marketed product is an inhalation liquid, so the unit is millilitres and the
field is **litres**. Read as anything else, the study's anaesthetic term is wrong
by three orders of magnitude.

`build_atc_sales.verify_anaesthetic_volumes` fails the build unless the register
reproduces the six litre values `analysis.main_2025` carries in
`DK_ANAESTHETIC_LITRES`, at `sector = 2`, `region = 0`, `sex = A`,
`age_group = A`:

| ATC | agent | 2019, litres | 2022, litres |
|:---|:---|:---|:---|
| `N01AB06` | isoflurane | 17 | 15 |
| `N01AB07` | desflurane | 400 | 181 |
| `N01AB08` | sevoflurane | 2,714 | 2,400 |

## Caveats

**ATC levels are nested.** `A`, `A01`, `A01A`, `A01AA` and `A01AA01` are all rows
in the same file. Summing the `atc` column double-counts.

**Do not add sectors.** `sector = 2` is the total, not a third category.

**Sales, not consumption.** The register records what was sold. The study applies
a 5 % downward correction to sevoflurane for the fraction metabolised rather than
exhaled; the other two agents are taken as fully exhaled.
