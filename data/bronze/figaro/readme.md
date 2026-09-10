# Eurostat FIGARO extracts

Reproducible downloads from the Eurostat dissemination API. Used for the
independent national denominator, the NACE-Q cross-check and the three-way
validation of the Danish health input recipe.

| file | dataset | content |
|:---|:---|:---|
| `env_ac_ghgfp_DKdest_2021-2023.csv` | `env_ac_ghgfp` | FIGARO-based GHG footprint, Denmark as destination, by origin country and NACE |
| `env_ac_co2fp_DKdest_2021-2023.csv` | `env_ac_co2fp` | as above, CO2 only |
| `env_ac_ghgfp_WORLDdest_by_origin_2022-2023.csv` | `env_ac_ghgfp` | world destination, by origin |
| `figaro2026_use_DKdest_2022.csv`, `..._2024.csv` | FIGARO 2026 edition | use table, Denmark as destination, by product and using industry |
| `figaro2026_supply_DK_2022-2024.csv` | FIGARO 2026 edition | Danish supply table |

`estat_naio_10_fcp_ii4_*.tsv.gz` (71 MB, the full EU industry-by-industry IOT)
is git-ignored: it is not used by the current analysis and is reproducible from
the same API.

Note on units: FIGARO monetary values are **MIO_EUR**; the GHG footprint
datasets are in **THS_T** (thousand tonnes CO2e).
