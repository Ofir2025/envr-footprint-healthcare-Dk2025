# Statistics Denmark environmental-economic accounts by industry

The Danish direct-emission accounts. These are the study's Scope 1 evidence and
the domestic satellite of the SNAC coupling: they follow national-accounts
residence principles and the same DB07 industry classification as the Danish
input-output tables, which is what makes them substitutable into an
input-output model at all.

| item | value |
|:---|:---|
| Provider | Statistics Denmark |
| Dataset | StatBank tables **DRIVHUS** (greenhouse gas accounts, CO2 equivalents), **MRU1** (air emission accounts), **ENE2HA** (energy account, GJ) |
| URL | <https://api.statbank.dk/v1/data> (POST, no key); table pages at <https://www.statbank.dk/DRIVHUS>, `/MRU1`, `/ENE2HA` |
| Licence | Statistics Denmark open data; free reuse with attribution |
| Retrieved | `dk_direct_emissions_drivhus.csv` 2026-09-07; `dst_emission_accounts_by_industry.csv` 2026-09-09 (`3c78cd1`). DRIVHUS last updated at source 2025-09-15 |

## Download step

`dst_emission_accounts_by_industry.csv` is written by
`analysis.fetch_dst_accounts`, which is a **retrieval** step, not a modelling
stage — the file it writes is the source as obtained, which is why it lives in
bronze:

```bash
PYTHONPATH=src .venv/bin/python -m analysis.fetch_dst_accounts
```

It POSTs to the StatBank REST API for all three tables, keeps only the
**six-digit** DB07 industry codes (the 117-grouping; five-digit codes are the
69-grouping and bare letters the sections, both aggregates of these), and
validates the download against `dk_direct_emissions_drivhus.csv` before
replacing it. Re-run it rather than editing the file by hand.

`dk_direct_emissions_drivhus.csv` is the older five-code health extract, kept
because it is the validation reference and because it carries a header comment
block recording the scope decisions.

## Files

| file | size | shape | unit |
|:---|:---|:---|:---|
| `dst_emission_accounts_by_industry.csv` | 1.6 MB | 7254 rows × 9 columns | per-row, see `unit` |
| `dk_direct_emissions_drivhus.csv` | 2.1 kB | 20 rows × 5 columns | kt CO2-eq |

Both carry `#`-prefixed header comments before the CSV header; readers pass
`comment="#"`.

## Column dictionaries

### `dst_emission_accounts_by_industry.csv`

Long format: one row per (year, industry, account, substance).

| column | meaning |
|:---|:---|
| `year` | reference year, `2019` or `2022` |
| `industry_code` | DB07 six-digit code, `V`-prefixed, e.g. `V860010`; 117 distinct values |
| `industry_name` | the industry's published English name |
| `account` | `greenhouse_gas` (DRIVHUS), `air_emission` (MRU1) or `energy_use` (ENE2HA) |
| `substance` | substance or carrier mnemonic, e.g. `GHGEXBIO`, `N2O`, `ETOT` |
| `substance_name` | its published description |
| `unit` | the published unit of this row: 1000 t CO2-eq for DRIVHUS, 1000 t for CO2 and t for the other substances in MRU1, t CO2-eq for the fluorinated gases, GJ for ENE2HA |
| `value` | the quantity, in `unit` |
| `source` | the StatBank table the row came from |

### `dk_direct_emissions_drivhus.csv`

| column | meaning |
|:---|:---|
| `industry_code` | `VQ`, `VQA`, `V860010`, `V870000`, `V880000` — the health-sector aggregates and members |
| `industry` | the industry's English name |
| `emtype` | emission type; `GHGEXBIO` for the totals, `N2O` for the medical-gas subtraction |
| `year` | 2016, 2019, 2022 or 2023 |
| `value_kt_co2e` | the quantity, **kt CO2-eq** |

## Caveats

**Do not sum the substance column.** `GHGEXBIO = CO2UBIO + N2O + CH4 + FGAS` and
`GHGBIO = GHGEXBIO + CO2BIO`: the totals sit in the same column as their
components. The same holds for `ENE2HA`, where `ETOT` is the total of the eight
carrier groups.

**Direct only.** These are the territorial, Scope 1 accounts. The sibling
`FORDEL` and `BRUTTO` principles redistribute electricity and district-heat
emissions onto the consuming industry; they must **not** be used here, because
the input-output model derives that redistribution through the Leontief inverse
and would otherwise count it twice.

**Rounding.** DRIVHUS is published rounded to whole 1000 tonnes, so a small
industry can carry a several-per-cent rounding error and an industry below
500 t CO2-eq reports as zero. MRU1 publishes the non-CO2 substances in tonnes
and is the more precise source for them.

**Medical N2O.** The N2O of industry `860010` (hospital activities), roughly
11 kt CO2-eq a year, is dominated by anaesthetic N2O. It is subtracted before
the remainder is used as the operational-direct row, because anaesthetic gases
enter separately as a bottom-up item; the header comment of
`dk_direct_emissions_drivhus.csv` records this.

**Not a full satellite.** There are no water, land or material-extraction rows
here, and the waste rows live in the `AFF*` StatBank family instead.
