# Danish national travel survey, and the travel workbooks built from it

The Danish evidence for the two private-travel items of the bottom-up
inventory: employee commuting, and patient and visitor travel. Until the
2026-09 revision both were the Dutch values scaled by a ratio; they are now
read from Denmark's own measurement.

| item | value |
|:---|:---|
| Provider | DTU Center for Transport Analytics (Transportvaneundersøgelsen, TU); the derived workbooks are this study's own |
| Dataset | TU årsrapport Danmark, annual report, one per year |
| URL | <https://www.cta.man.dtu.dk/transportvaneundersoegelsen> |
| Licence | DTU publication; free use with attribution |
| Retrieved | 2026-09-07 (`6fff025`) |

## Files

| file | size | shape | tracked | content |
|:---|:---|:---|:---|:---|
| `tu_danmark_2019.pdf` | 279 kB | — | no | TU annual report 2019, the published tables the parameters are read from |
| `tu_danmark_2022.pdf` | 279 kB | — | no | TU annual report 2022 |
| `commuting_private_travel_calculations_2026.xlsx` | 19.4 kB | 5 sheets | yes | the commute and visitor scaling workbook, 2026-09 revision |
| `danish_travel_data_2019.xlsx` | 8.6 kB | 1 sheet, 1 data row × 5 | yes | the five raw quantities the 2019 commute ratio is built from |

The two PDFs are **not in version control** — the author's global excludes file
drops `*.pdf` and they are third-party publications, freely re-downloadable from
the URL above. Everything the study takes from them is quoted below, so the
numbers are checkable without the files.

## What is read from the reports

| quantity | table | 2019 | 2022 |
|:---|:---|:---|:---|
| All-purpose travel | Tabel 15 | 40.4 km/person/day | 37.5 km/person/day |
| Purpose 33, "Social/sundhed" (doctor, hospital, jobcentre visits) | Tabel 15 | 0.9 km/person/day | 0.8 km/person/day |
| Commuting distance | Table 20 | 9.0 km/person/day | 9.3 km/person/day |

The TU universe is **residents aged 6 and over**, which is why
`analysis.main_2025` multiplies by a 6-plus population (5,442,766 for 2019,
5,499,115 for 2022) and not by the whole population.

## Column dictionaries

### `danish_travel_data_2019.xlsx`, sheet `Ark1`

One header row and one data row, five columns.

| column | value | unit |
|:---|:---|:---|
| `Dk Emplyoees in 2019` | 524000 | persons |
| `NL empoyees in 2019` | 1220750 | persons |
| `DK average work hours` | 34.4 | hours/week |
| `NL average work hours` | 29.2 | hours/week |
| `Commuting days in NL 2019` | 138 | days/year |

The column heading `Dk Emplyoees in 2019` carries a typo in the source workbook.
It is left as it is: this is bronze, and a silently corrected heading is a
silently edited source.

### `commuting_private_travel_calculations_2026.xlsx`

| sheet | shape | content |
|:---|:---|:---|
| `Private travel calculations` | 34 × 24 | the commute and visitor-travel ratios, one row per component |
| `Modal commuting  NL` | 10 × 2 | Dutch modal split |
| `Modal commuting DK` | 8 × 2 | Danish modal split |
| `Errand travel construction (NL` | 6 × 3 | how the Dutch errand-travel term was built |
| `Distance comparison` | 4 × 4 | DK against NL travel distances |

`Private travel calculations` carries `Category`, `Component`, `Denmark`,
`Netherlands`, `Ratio`, where `Ratio` is a live Excel formula `=C<n>/D<n>`. A
reader that does not evaluate formulas sees the formula text, not the number.

## The correction this folder records

The commute factor is the product of three ratios — employment, weekly hours and
commuting distance:

$$
f_{\text{commute}} = \frac{518{,}889}{1{,}220{,}750} \times \frac{34.4}{29.2}
  \times \frac{9.0}{7.88} = 0.5719 \quad (2019)
$$

The **hours ratio applies to commuting only**. Hours worked scale how often
staff travel to work; they do not scale how far patients and visitors travel,
which is driven by system size and travel behaviour. Steenmeijer et al.'s
appendix is explicit — eq. A10 (commuting) carries the hours term, eqs. A12-A15
(patient and visitor) do not. Until 2026-09 this study applied the hours ratio to
visitor travel as well, overstating it by 17.8 %.

**Caveat.** Visitor travel has no Danish source: TU folds hospital visits into
"Besøge familie/venner". It is carried as one clearly labelled imported
parameter, the NHS England visitor-to-patient ratio 0.29/1.23 = 0.236 (Tennison
et al. 2021, appendix 1 table S12).

**Caveat.** `danish_travel_data_2019.xlsx` records Danish health employment as
524,000. `analysis.main_2025` uses 518,889, from DST NABB69 national-accounts
employment 2019, industries 86000 + 87880. The workbook is the earlier working
figure; the module's value is the one every published number is built on.
