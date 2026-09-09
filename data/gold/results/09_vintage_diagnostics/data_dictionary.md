# 09_vintage_diagnostics - data dictionary

One row per column of every table in this folder. Units are the
table's own; `varies by row` means the table carries a `unit`
column and the value is read from there.

## Common columns

Every gold table shares this vocabulary; columns particular to one table
are described below, per table.

| Column | Meaning |
|:---|:---|
| `analysis_year` | year of the Danish expenditure data and of the MRIO background |
| `model` | MRIO release actually used (e.g. `EXIOBASE v3.10.2 IOT_2022_ixi (screened)`) |
| `scenario` | model scenario (`baseline`, scope variants, pharma-mapping variants) |
| `consuming_country_iso3` | always `DNK` - Denmark is the final consumer in this study |
| `demand_component` | `healthcare_services`, `pharmaceuticals`, `medical_appliances` |
| `indicator` | `climate_change`, `material_extraction`, `blue_water_consumption`, `land_use`, `waste_generation` |
| `unit` | `kt CO2eq`, `kt`, `Mm3`, `km2`, or `M.EUR` for monetary rows |
| `value` | numeric value in `unit` |

## Country and region coding

`*_country_iso3` uses **ISO 3166-1 alpha-3** for the 44 EXIOBASE countries.
The five rest-of-world regions are **not countries** and keep their own
codes and names: `WA` RoW Asia and Pacific, `WL` RoW America, `WE` RoW
Europe, `WF` RoW Africa, `WM` RoW Middle East. `*_world_region` gives the
continental grouping (Europe, Asia and Pacific, America, Middle East,
Africa, Denmark).

## The two perspectives (and why they reconcile)

Every impact cell is `E[i,j] = s_k(i) . L(i,j) . y_H(j)`: pressure arising
in node *i* caused by Danish healthcare final demand for node *j*. Summing
over *i* gives the **consumption / contribution** perspective (by
purchased product); summing over *j* gives the **production / hotspot**
perspective (by producing node). Both are marginals of the same array, so
they sum to the identical total - verified to machine precision by
`analysis.validate_io_identities` (tests T5/T6). Allocating production
emissions to final demand is additive and does not double count (Wood et
al. 2018); embodied-flow tables (E_Z) would.

## Units

Monetary values are **million euro (M.EUR)** - EXIOBASE's native unit
(`unit.txt` of the release). No US-dollar values are used anywhere in this
model; dollar figures appearing in the comparative literature (Karliner et
al. 2019, Lenzen et al. 2020, Pichler et al. 2019) are those studies' own
units and are labelled as such wherever they are quoted.

## Tables

### `dk_block_vs_national_accounts.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `mrio_vintage` | dimension | str |  | v3.10.2 |
| `mrio_year` | measure | int64 | M.EUR | 2022 |
| `country_producing` | dimension | str |  | DNK |
| `sector_producing` | dimension | str |  | Health and social work |
| `exiobase_industry_index` | dimension | str |  | 137 |
| `dst_nace_prefixes` | measure | str | M.EUR | 86;87;88 |
| `exiobase_output_meur` | measure | float64 | M.EUR | 16326.113359 |
| `national_accounts_output_meur` | measure | float64 | M.EUR | 45320.98661218329 |
| `ratio_exiobase_over_dst` | measure | float64 | M.EUR | 0.3602329644476711 |
| `unit` | dimension | str |  | M.EUR |
| `source_national_accounts` | dimension | str |  | Statistics Denmark, published 117-indust |

### `industry33_output_by_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `mrio_vintage` | dimension | str |  | v3.10.2 |
| `mrio_year` | measure | int64 | M.EUR | 2022 |
| `country_producing` | dimension | str |  | AUT |
| `sector_producing` | dimension | str |  | Manufacture of medical, precision and op |
| `exiobase_industry_index` | measure | int64 | M.EUR | 89 |
| `value` | measure | float64 | M.EUR | 0.0 |
| `unit` | dimension | str |  | M.EUR |
| `variable` | measure | str | M.EUR | total_industry_output |

### `vintage_defect_verdicts.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `defect` | dimension | str |  | D1 industry 33 emptied in Europe |
| `mrio_vintage` | dimension | str |  | v3.10.2 |
| `mrio_year` | measure | int64 |  | 2016 |
| `metric` | dimension | str |  | European regions with i33 output < 1 M.E |
| `value` | measure | int64 |  | 26 |
| `of` | measure | int64 |  | 30 |
| `world_total_meur` | measure | float64 |  | 160110.8 |
| `verdict` | dimension | str |  | DEFECT |
