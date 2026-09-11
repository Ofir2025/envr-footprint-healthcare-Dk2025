# Eurostat FIGARO extracts

Reproducible downloads from the Eurostat dissemination API. They give the study
an independent national denominator, the NACE-Q cross-check, and the three-way
validation of the Danish health input recipe — official EU national accounts,
international trade balancing and Eurostat's own environmental accounts, built
by someone other than this study.

| item | value |
|:---|:---|
| Provider | Eurostat |
| Datasets | `env_ac_ghgfp`, `env_ac_co2fp` (FIGARO-based footprints); FIGARO 2026 edition supply and use tables; nine SDMX codelists |
| URL | dissemination API <https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}>; FIGARO database at <https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/database> |
| Metadata | <https://ec.europa.eu/eurostat/cache/metadata/en/env_ac_ghgfp_esms.htm> |
| Licence | Eurostat open data; free reuse with attribution |
| Retrieved | 2026-09-07 (`55fd8ef`) |

## Download step

Each file is one dissemination-API query, flattened to long CSV. The filename
encodes the query: dataset, the destination or geography filter, and the years.

| file | dataset | filter | years | rows × cols | size |
|:---|:---|:---|:---|:---|:---|
| `env_ac_ghgfp_DKdest_2021-2023.csv` | `env_ac_ghgfp` | `c_dest=DK`, all origins | 2021-2023 | 69,696 × 7 | 2.3 MB |
| `env_ac_co2fp_DKdest_2021-2023.csv` | `env_ac_co2fp` | `c_dest=DK`, all origins | 2021-2023 | 69,696 × 7 | 2.3 MB |
| `env_ac_ghgfp_WORLDdest_by_origin_2022-2023.csv` | `env_ac_ghgfp` | `c_dest=WORLD`, all origins | 2022-2023 | 46,648 × 7 | 1.8 MB |
| `figaro2026_use_DKdest_2022.csv` | FIGARO 2026 use table | `c_dest=DK` | 2022 | 221,214 × 7 | 7.8 MB |
| `figaro2026_use_DKdest_2024.csv` | FIGARO 2026 use table | `c_dest=DK` | 2024 | 221,214 × 7 | 7.8 MB |
| `figaro2026_supply_DK_2022-2024.csv` | FIGARO 2026 supply table | `geo=DK` | 2022-2024 | 12,288 × 6 | 390 kB |

`estat_naio_10_fcp_ii4_*.tsv.gz` — the full EU industry-by-industry inter-country
IOT, 71 MB — is git-ignored. It is not used by the current analysis and is
reproducible from the same API.

### The codelists

The fact tables above are keys and a `value`. Nothing in them says that `Q86` is
human health activities or that `CPA_C21` is pharmaceutical products, so the
codelists are retrieved as well, one per code column, from the SDMX 2.1 endpoint:

```
https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/{codelist}?format=TSV&compressed=false
```

| file | codelist | codes in the register | codes used here |
|:---|:---|---:|---:|
| `codelist_c_dest.tsv` | `C_DEST` | 4,292 | 2 |
| `codelist_c_orig.tsv` | `C_ORIG` | 4,093 | 54 |
| `codelist_cpa2_1.tsv` | `CPA2_1` | 5,580 | 64 |
| `codelist_geo.tsv` | `GEO` | 4,292 | 1 |
| `codelist_ind_use.tsv` | `IND_USE` | 168 | 69 |
| `codelist_na_item.tsv` | `NA_ITEM` | 643 | 6 |
| `codelist_nace_r2.tsv` | `NACE_R2` | 1,342 | 83 |
| `codelist_prd_ava.tsv` | `PRD_AVA` | 166 | 70 |
| `codelist_unit.tsv` | `UNIT` | 759 | 2 |

Two columns, tab-separated, no header: code, then Eurostat's English label. They
are kept as retrieved — whole registers, not filtered to the codes used — because
that is what bronze is for. The filtered join is the silver product,
`data/silver/eurostat_figaro/figaro_dimensions.csv`, built by
`analysis.build_figaro_dimensions`, and that readme records which levels of each
classification add up to what.

**Each column must be resolved against the codelist of its own name.** Eurostat
publishes one codelist per dimension, not per classification, and the spellings
differ between dimensions of the same classification: `nace_r2` writes food
manufacturing `C10-C12`, `ind_use` writes it `C10-12`. Sixteen of the 69
`ind_use` codes are absent from `NACE_R2` for that reason, and `P3_S14`,
`P3_S15` and `P5M` are absent from every Eurostat codelist except `IND_USE`.

## Column dictionaries

### The two footprint extracts, and the world-destination extract

| column | meaning |
|:---|:---|
| `time` | reference year |
| `c_dest` | destination country of the footprint; `DK` or `WORLD` |
| `c_orig` | country where the emission occurs, ISO 2 or a FIGARO aggregate |
| `nace_r2` | NACE rev.2 activity of the emitting industry, A64 level |
| `na_item` | final-demand item; `TOTAL` for the whole footprint |
| `unit` | `THS_T` — **thousand tonnes CO2-equivalent** |
| `value` | the quantity, in `unit` |

### `figaro2026_use_DKdest_*.csv`

| column | meaning |
|:---|:---|
| `time` | reference year |
| `c_dest` | using country; `DK` |
| `c_orig` | country of origin of the product, or `DOM` for domestic |
| `prd_ava` | product available, FIGARO product code, e.g. `B2A3G` |
| `ind_use` | using industry, NACE rev.2 A64, e.g. `A01` |
| `unit` | `MIO_EUR` — **million euro** |
| `value` | the quantity, in `unit` |

### `figaro2026_supply_DK_2022-2024.csv`

| column | meaning |
|:---|:---|
| `time` | reference year |
| `geo` | country; `DK` |
| `nace_r2` | supplying industry, NACE rev.2 A64 |
| `cpa2_1` | product supplied, CPA 2.1 |
| `unit` | `MIO_EUR` |
| `value` | the quantity, in `unit` |

## Caveats

**Two unit systems in one folder.** The monetary tables are `MIO_EUR`; the
footprint datasets are `THS_T`. Mixing them by reading the `value` column
without the `unit` column is the obvious way to be wrong by a factor of a
thousand.

**A64 resolution.** FIGARO separates `Q86` human health activities from
`Q87_Q88` residential care and social work, and carries `C21` pharmaceutical
manufacturing separately, which is better than one broad health-and-social
sector. It is still coarser than the Danish 117-industry SUT: medical and dental
instruments fall inside broader manufacturing groups, electromedical equipment
shares `C26`, and individual clinical services are not resolved. FIGARO is a
benchmark here, not a replacement for the Danish table.

**Years.** The 2026 FIGARO edition covers 2010-2024. 2023 and 2024 are the
newest and least settled releases; the study's published numbers rest on 2022.
**There is no 2025 FIGARO table and cannot be**: the edition released in year
$n$ ends at $n-2$, so 2025 first appears in the 2027 edition. 2016 and 2019 are
published and are not held here yet; they are one query each on the same API,
and they are what a 2016/2019/2022 FIGARO benchmark of the time series would
need.
