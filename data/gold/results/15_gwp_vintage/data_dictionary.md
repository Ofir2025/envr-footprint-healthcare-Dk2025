# 15_gwp_vintage - data dictionary

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

### `gwp_by_species.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `species` | dimension | str |  | CO2 |
| `mass_kg` | measure | float64 | varies by row | 2670662773.160374 |
| `unit` | dimension | str |  | kg |
| `ar6_gwp100` | measure | float64 | varies by row | 1.0 |
| `contribution_kt_co2eq` | measure | float64 | varies by row | 2670.662773160375 |

### `gwp_vintage_sensitivity.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `analysis_year` | measure | int64 |  | 2022 |
| `gwp_vintage` | dimension | str |  | IPCC SAR (1995) |
| `is_study_default` | dimension | bool |  | False |
| `healthcare_kt_co2eq` | measure | float64 |  | 3740.212749906714 |
| `national_kt_co2eq` | measure | float64 |  | 64766.870324631665 |
| `healthcare_share_pct` | measure | float64 | % | 5.774885726544461 |
| `healthcare_t_per_capita` | measure | float64 |  | 0.6368032168492488 |
| `not_restatable_kt_co2eq` | measure | float64 |  | 155.29988960547564 |
| `not_restatable_share_pct` | measure | float64 | % | 4.152167269344478 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `note` | dimension | str |  | HFC and PFC are supplied by EXIOBASE alr |
