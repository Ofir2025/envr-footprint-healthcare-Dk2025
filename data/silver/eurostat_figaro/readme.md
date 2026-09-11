# Silver: Eurostat FIGARO dimension tables

Mirrors `data/bronze/eurostat_figaro/`. One table, decoding every code in every
code column of the FIGARO fact tables held in bronze. The dissemination API
serves those tables as keys and a `value` and nothing else, so a reader holding
`figaro2026_use_DKdest_2022.csv` sees `CPA_C21,Q86` and cannot tell without
leaving the repository that the row is pharmaceutical products bought by human
health activities. That is what this table is for.

| item | value |
|:---|:---|
| Bronze source | `data/bronze/eurostat_figaro/codelist_*.tsv` — nine Eurostat SDMX codelists, one per code column, cached as retrieved; and the fact tables themselves, which say which codes are used |
| Provider | Eurostat, SDMX 2.1 codelist endpoint `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/{codelist}?format=TSV` |
| Licence | Eurostat open data; free reuse with attribution |
| Retrieved | 2026-09-11 |
| Produced by | `analysis.build_figaro_dimensions` |
| Read by | `analysis.figaro_benchmarks` |
| Rebuild | `PYTHONPATH=src .venv/bin/python -m analysis.build_figaro_dimensions` (offline from the cached codelists; `--refresh` re-fetches them) |
| In version control | **yes** — 58 kB, and it is the only thing in the repository that says what a FIGARO code means. The codelists it is built from are 920 kB of mostly unused register and stay in bronze, untracked like the rest of the layer. |

## Files

| file | derives from | transformation | rows × cols | size |
|:---|:---|:---|:---|:---|
| `figaro_dimensions.csv` | the nine cached codelists and the seven bronze fact tables | one row per code actually used, labelled from the codelist paired with its own column | 351 × 7 | 58 kB |

## Columns

| column | meaning |
|:---|:---|
| `fact_column` | the column of the bronze fact tables this row decodes; the join key |
| `code` | the code, exactly as the fact tables spell it |
| `label` | Eurostat's own label for that code in that codelist |
| `entry_type` | `industry`, `product`, `final_demand`, `value_added`, `adjustment`, `country`, `country_aggregate`, `country_residual`, `no_origin`, `household`, `total` or `unit`. Only `country_aggregate` and `total` have to come out of a sum; `country_residual` has to stay in |
| `nace_level` | for `nace_r2` only: `section`, `division`, `cross_section`, `household`, `all_activities`, `all_activities_and_households`; empty in every other column |
| `codelist` | the Eurostat codelist the label was read from |
| `bronze_files` | the bronze fact tables the code appears in, `;`-separated |

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
