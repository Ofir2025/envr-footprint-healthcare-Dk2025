# 14_eckelman_replication - data dictionary

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

### `damage_daly_dk_vs_us.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `damage_category` | dimension | str |  | Particulate matter |
| `us_daly` | measure | float64 |  | 435000.0 |
| `us_daly_per_1000` | measure | float64 |  | 1.3760212493615618 |
| `dk_daly` | measure | float64 |  | 8480.57431533371 |
| `dk_daly_per_1000` | measure | float64 |  | 1.4438903254549664 |
| `us_method` | dimension | str |  | IMPACT 2002+ endpoint factors |
| `dk_method` | dimension | str |  | ILCD recommended endpoint factors |

### `nine_categories_dk_vs_us.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `analysis_year_denmark` | measure | int64 |  | 2022 |
| `reference_year_us` | measure | int64 |  | 2013 |
| `eckelman_code` | measure | str |  | GW |
| `effect_category` | measure | str |  | Global warming |
| `us_unit` | dimension | str |  | kg CO2-e |
| `us_health_care` | measure | float64 |  | 660000000000.0 |
| `us_national` | measure | float64 |  | 6500000000000.0 |
| `us_share_of_national_pct` | measure | float64 |  | 9.8 |
| `dk_method` | dimension | str |  | Problem oriented approach: baseline (CML |
| `dk_indicator` | dimension | str |  | global warming GWP100 |
| `dk_unit` | dimension | str |  | kg CO2 eq. |
| `dk_health_care` | measure | float64 |  | 3859168427.4281926 |
| `dk_national` | measure | float64 |  | 66744817262.27816 |
| `dk_share_of_national_pct` | measure | float64 |  | 5.7819746696786 |
| `share_difference_pp` | measure | float64 |  | -4.018025330321401 |
| `comparability` | measure | str |  | shares only; reference substances differ |
| `source_us` | dimension | str |  | Eckelman & Sherman 2016, PLoS ONE 11(6): |
| `source_dk` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
