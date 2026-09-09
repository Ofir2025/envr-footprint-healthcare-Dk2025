# 13_steenmeijer_replication - data dictionary

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

### `national_shares_dk_vs_nl.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `netherlands_national` | measure | int64 | varies by row | 241358 |
| `netherlands_health_share_pct` | measure | float64 | varies by row | 7.3 |
| `denmark_national` | measure | float64 | varies by row | 77477.50333386465 |
| `denmark_health_share_pct` | measure | float64 | varies by row | 5.089731660302548 |
| `share_difference_pp` | measure | float64 | varies by row | -2.2102683396974516 |
| `comparability_note` | dimension | str |  | NOT on the same boundary: the Dutch figu |
| `source_netherlands` | dimension | str |  | Steenmeijer et al. 2022 table S7 (= RIVM |
| `source_denmark` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |

### `template_table_dk_vs_nl.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `analysis_year_denmark` | measure | int64 | varies by row | 2022 |
| `reference_year_netherlands` | measure | int64 | varies by row | 2016 |
| `table_row` | measure | str | varies by row | Total |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `netherlands_2016` | measure | float64 | varies by row | 17575.0 |
| `denmark_2022` | measure | float64 | varies by row | 4712.417605953846 |
| `netherlands_per_capita` | measure | float64 | varies by row | 1031.9833210356544 |
| `denmark_per_capita` | measure | float64 | varies by row | 802.3294104548705 |
| `per_capita_unit` | dimension | str |  | kt CO2eq per million population |
| `dk_as_pct_of_nl_per_capita` | measure | float64 | varies by row | 77.7463544323262 |
| `source_netherlands` | dimension | str |  | Steenmeijer et al. 2022, Lancet Planet H |
| `source_denmark` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
