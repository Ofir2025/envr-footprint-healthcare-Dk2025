# Silver: Eurostat FIGARO dimensions and series

Mirrors `data/bronze/eurostat_figaro/`. Three tables: one that decodes every code
in every code column of the FIGARO extracts, and two that turn those extracts
into series with a `year` column.

The dissemination API serves the extracts as keys and a `value` and nothing else,
so a reader holding `figaro2026_use_DKdest_2022.csv` sees `CPA_C21,Q86` and
cannot tell without leaving the repository that the row is pharmaceutical
products bought by human health activities. And bronze holds one file per API
query, because that is what bronze is — while a query can only ask for the years
inside one of Eurostat's four-year dataset blocks, so 2016, 2019 and 2022 arrive
as three files from three datasets. Reading a series out of that means globbing a
folder and trusting filenames. These three tables are the alternative.

| item | value |
|:---|:---|
| Bronze source | `data/bronze/eurostat_figaro/codelist_*.tsv` — nine Eurostat SDMX codelists, one per code column, cached as retrieved; and the fact tables themselves, which say which codes are used |
| Provider | Eurostat, SDMX 2.1 codelist endpoint `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/{codelist}?format=TSV` |
| Licence | Eurostat open data; free reuse with attribution |
| Retrieved | 2026-09-11 |
| Produced by | `analysis.build_figaro_dimensions` (the dimension table), `analysis.build_figaro_series` (the two series) |
| Read by | `analysis.figaro_benchmarks` |
| Rebuild | `PYTHONPATH=src .venv/bin/python -m analysis.build_figaro_dimensions` then `… -m analysis.build_figaro_series`. Both are offline from bronze; `build_figaro_dimensions --refresh` re-fetches the codelists, and `analysis.fetch_figaro --years … ` re-fetches the extracts |
| In version control | **yes**, all three — 1.2 MB together. The dimension table is the only thing in the repository that says what a FIGARO code means; the two series are the whole benchmark a reviewer would ask to see, and rebuilding them takes eight API queries and the 31 MB of extracts those return. |

## Files

| file | derives from | transformation | rows × cols | size |
|:---|:---|:---|:---|:---|
| `figaro_dimensions.csv` | the nine cached codelists and the ten bronze extracts | one row per code actually used, labelled from the codelist paired with its own column | 351 × 7 | 30 kB |
| `figaro_dk_health_inputs.csv` | `figaro2026_use_DKdest_{2016,2019,2022,2024}.csv` | the `Q86` and `Q87_88` columns, product rows only, concatenated with a `year` column | 25,600 × 6 | 902 kB |
| `figaro_dk_footprint_series.csv` | `env_ac_ghgfp_DKdest_2016-2023.csv`, `env_ac_co2fp_DKdest_2016-2023.csv` | the `nace_r2 = TOTAL` slice of both indicators, concatenated with a `year` column | 4,704 × 7 | 234 kB |

## Columns of `figaro_dimensions.csv`

| column | meaning |
|:---|:---|
| `fact_column` | the column of the bronze fact tables this row decodes; the join key |
| `code` | the code, exactly as the fact tables spell it |
| `label` | Eurostat's own label for that code in that codelist |
| `entry_type` | `industry`, `product`, `final_demand`, `value_added`, `adjustment`, `country`, `country_aggregate`, `country_residual`, `no_origin`, `household`, `total` or `unit`. Only `country_aggregate` and `total` have to come out of a sum; `country_residual` has to stay in |
| `nace_level` | for `nace_r2` only: `section`, `division`, `cross_section`, `household`, `all_activities`, `all_activities_and_households`; empty in every other column |
| `codelist` | the Eurostat codelist the label was read from |
| `fact_tables` | which FIGARO tables use the code: `use`, `supply`, `footprint`, `;`-separated. Recorded as the family rather than the file name because the family is stable — adding 2016 to the series adds a bronze file, and a column keyed on file names would churn on every fetch while saying nothing new |

## Columns of the two series

Both carry codes and no labels, and join to `figaro_dimensions.csv` on
`fact_column` and `code`. Denormalising Eurostat's wording onto 25,600 fact rows
would put it in two places and let them drift.

### `figaro_dk_health_inputs.csv`

| column | unit | meaning |
|:---|:---|:---|
| `year` | year | reference year: 2016, 2019, 2022, 2024 |
| `using_industry` | — | `Q86` human health activities, or `Q87_88` residential care and social work without accommodation. Join on `fact_column = ind_use` |
| `product` | — | CPA product bought. Join on `fact_column = prd_ava` |
| `origin` | — | country the product comes from. Join on `fact_column = c_orig` |
| `unit` | — | `MIO_EUR` |
| `value` | million euro | intermediate use at basic prices |

**Intermediate inputs only.** The use table's rows are products *and* the
primary inputs — `D1` compensation of employees, `B2A3G` gross operating surplus,
`D21X31` and `D29X39` net taxes — plus the two residents adjustments. An input
recipe that included value added would not be an input recipe, so only rows typed
`product` in the dimension table are kept. That is also why `DOM` never appears
in `origin` here: it is the origin code the primary-input rows carry, and those
rows are gone.

| `year` | `Q86` | `Q87_88` |
|:---|---:|---:|
| 2016 | 5,415.0 | 3,978.6 |
| 2019 | 5,662.9 | 4,233.3 |
| 2022 | 6,933.2 | 5,189.8 |
| 2024 | 7,001.4 | 5,693.2 |

### `figaro_dk_footprint_series.csv`

| column | unit | meaning |
|:---|:---|:---|
| `year` | year | reference year, 2016 to 2023 with no gaps |
| `indicator` | — | `greenhouse_gas` (`env_ac_ghgfp`) or `carbon_dioxide` (`env_ac_co2fp`) |
| `origin` | — | country or aggregate where the emission occurs. Join on `fact_column = c_orig` |
| `origin_is_aggregate` | — | `True` for `WORLD`, `EU27_2020` and `EXT_EU27_2020` only; exclude these before summing over origins. `WRL_REST` is `False` and belongs in the sum |
| `final_demand` | — | final-demand category, `TOTAL` for the whole footprint. Join on `fact_column = na_item` |
| `unit` | — | `THS_T`, thousand tonnes |
| `value` | kt | the footprint |

Taken at `nace_r2 = TOTAL`, so the emitting industry is not resolved and the
level mixing described below does not arise. Denmark's whole consumption-based
footprint, at `origin = WORLD` and `final_demand = TOTAL`:

| `year` | greenhouse gas, kt CO₂-eq | carbon dioxide, kt CO₂ |
|:---|---:|---:|
| 2016 | 58,288.5 | 46,886.0 |
| 2017 | 58,163.6 | 46,344.9 |
| 2018 | 60,427.6 | 47,089.0 |
| 2019 | 54,576.4 | 43,283.7 |
| 2020 | 53,458.2 | 40,270.5 |
| 2021 | 57,274.6 | 43,670.0 |
| 2022 | 57,401.7 | 44,037.4 |
| 2023 | 50,245.3 | 38,430.1 |

The study's three benchmark years are 2016, 2019 and 2022, and this is the
independent national denominator for each.

## Each code column is resolved against the codelist of its own name

Eurostat publishes one codelist per *dimension*, not per classification, and the
spellings differ between dimensions of the same classification. The footprint
extracts write food manufacturing as `C10-C12` in `nace_r2`; the use table writes
the same activity as `C10-12` in `ind_use`. Sixteen of the 69 `ind_use` codes are
absent from `NACE_R2` for that reason, and three of them — `P3_S14`, `P3_S15`,
`P5M` — are absent from every other Eurostat codelist as well. Pairing each
column with the codelist of the same name resolves all 351 codes exactly, with no
spelling repair and no inference from ESA 2010 semantics. The builder raises
rather than emit a row whose label it had to invent.

| `fact_column` | codelist | codes used |
|:---|:---|---:|
| `c_dest` | `C_DEST` | 2 |
| `c_orig` | `C_ORIG` | 54 |
| `cpa2_1` | `CPA2_1` | 64 |
| `geo` | `GEO` | 1 |
| `ind_use` | `IND_USE` | 69 |
| `na_item` | `NA_ITEM` | 6 |
| `nace_r2` | `NACE_R2` | 83 |
| `prd_ava` | `PRD_AVA` | 70 |
| `unit` | `UNIT` | 2 |

## Three code columns do not hold one classification each

**`ind_use` is industries and final demand in one column.** The FIGARO use
table's columns are 64 NACE rev.2 activities followed by `P3_S13`, `P3_S14`,
`P3_S15`, `P51G` and `P5M`. Summing the column without separating them adds final
demand to intermediate use. `P85` is *not* one of them: it is NACE P85,
education, so a rule keyed on the letter `P` gets education wrong.

**`prd_ava` is products, primary inputs and two adjustments.** 64 CPA products,
then `D1` compensation of employees, `B2A3G` gross operating surplus and mixed
income, `D21X31` and `D29X39` net taxes, then `OP_RES` and `OP_NRES`, the
residents and non-residents adjustments. Summing products and value added double
counts output.

**`c_orig` carries 49 countries and five codes that are not one**, and they do
not behave alike, which was checked against the tables rather than read off the
labels.

| code | Eurostat label | `entry_type` | what it does |
|:---|:---|:---|:---|
| `WORLD` | All countries of the world | `country_aggregate` | overlaps every member; exclude from a sum |
| `EU27_2020` | European Union - 27 countries (from 2020) | `country_aggregate` | overlaps its members; exclude from a sum |
| `EXT_EU27_2020` | Extra-EU27 (from 2020) | `country_aggregate` | overlaps the non-EU members; exclude from a sum |
| `WRL_REST` | Rest of the world | `country_residual` | the countries FIGARO does not resolve individually; **keep** it in a sum |
| `DOM` | Domestic country | `no_origin` | not a duplicate of `DK`: in the use table it appears on 414 rows, every one a primary input or an adjustment, and on no product row |

Measured on `env_ac_ghgfp_DKdest_2021-2023.csv` at `nace_r2 = TOTAL`,
`na_item = TOTAL`, in kt CO₂-eq:

| year | 49 countries + `WRL_REST` | `WORLD` | `EU27_2020` + `EXT_EU27_2020` | every row summed |
|:---|---:|---:|---:|---:|
| 2021 | 57,274.6 | 57,274.6 | 57,274.6 | 171,823.8 |
| 2022 | 57,401.7 | 57,401.7 | 57,401.7 | 172,205.1 |
| 2023 | 50,245.3 | 50,245.3 | 50,245.3 | 150,735.9 |

Three readings of the same footprint agree to every published digit, and summing
the column naively returns exactly three times it. A reader who dropped
everything without an ISO code would lose the rest of the world instead; the
residual has to stay in.

## What adds up to what in `nace_r2`, measured

`nace_r2` mixes NACE levels: 21 section letters, 58 divisions, households' direct
emissions, one `G-U_X_H` aggregate spanning sections, and two different totals.
`nace_level` records the level, which for NACE follows from the shape of the code.
Additivity does not follow from the shape of the code, so it was measured on
`env_ac_ghgfp_DKdest_2021-2023.csv` at `c_orig = WORLD`, `na_item = TOTAL`, in
kt CO₂-eq:

| year | $\sum$ sections | `TOTAL` | `TOTAL` + `HH` | `TOTAL_HH` | $\sum$ divisions | divisions as % of `TOTAL` |
|:---|---:|---:|---:|---:|---:|---:|
| 2021 | 57,274.6 | 57,274.6 | 64,108.4 | 64,108.4 | 36,293.0 | 63 |
| 2022 | 57,401.7 | 57,401.7 | 63,760.4 | 63,760.4 | 36,385.3 | 63 |
| 2023 | 50,245.3 | 50,245.3 | 56,460.1 | 56,460.1 | 32,990.6 | 66 |

So: **the 21 sections reproduce the `TOTAL` row exactly**, to every digit
published, in all three years; `TOTAL_HH` is `TOTAL` plus the single `HH` row of
households' direct emissions, again exactly; and **the divisions are not a
partition** — they recover 63 % of the total, because nine of the 21 sections are
published with no division detail at all. A reader who summed the division rows
as though they covered the economy would be 37 % low. Sum sections, or read the
`TOTAL` row; never sum the column, and never sum the divisions.

The supply table's `nace_r2` is a different set in the same column name: 64
divisions, flat, no sections and no totals. `bronze_files` is how a reader tells
which codes belong to which table.

## Caveat

**The labels are as Eurostat writes them, including where Eurostat is
inconsistent.** `ind_use` gives `P3_S14` as "Final consumption expenditure by
households" while `NA_ITEM` gives the near-equivalent `P31_S14` as "Final
consumption expenditure of household". Neither was edited. The codelist a label
came from is in the `codelist` column so a reader can see which register is
being quoted.
