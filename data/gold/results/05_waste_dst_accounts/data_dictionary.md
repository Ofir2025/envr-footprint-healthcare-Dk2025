# 05_waste_dst_accounts - data dictionary

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

### `waste_extension_validation.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `source` | dimension | str |  | EXIOBASE hybrid 2011 waste extension (as |
| `quantity` | dimension | str |  | direct waste of the Danish health sector |
| `value_kt` | measure | float64 |  | 240.4465651885147 |
| `basis` | dimension | str |  | absolute 2011 tonnes / analysis-year mon |
| `analysis_year` | measure | int64 |  | 2022 |

### `waste_footprint_domestic_dst.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `analysis_year` | measure | int64 |  | 2022 |
| `industry_code` | measure | int64 |  | 860010 |
| `industry` | dimension | str |  | Hospital activities |
| `expenditure_m_dkk` | measure | float64 |  | 153438.002 |
| `direct_intensity_t_per_mdkk` | measure | float64 |  | 0.211 |
| `multiplier_t_per_mdkk` | measure | float64 |  | 0.795 |
| `hazardous_multiplier_t_per_mdkk` | measure | float64 |  | 0.069 |
| `direct_waste_t` | measure | float64 |  | 32375.418422 |
| `total_waste_t` | measure | float64 |  | 121983.21159 |
| `hazardous_waste_t` | measure | float64 |  | 10587.222138 |
| `source` | dimension | str |  | Statistics Denmark AFF1MU1N / AFF3MU1N ( |
| `boundary` | measure | str |  | domestic (Danish waste generation); impo |
