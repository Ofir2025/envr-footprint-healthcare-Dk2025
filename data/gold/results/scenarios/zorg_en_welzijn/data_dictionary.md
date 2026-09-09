# scenarios/zorg_en_welzijn - data dictionary

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

### `full_results_tables_fig1_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 539.3898178684632 |
| `Material extraction (kt)` | measure | float64 |  | 174.0255185453556 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 24.950667122841935 |
| `Land use (km2)` | measure | float64 |  | 1965.0090473858104 |
| `Waste generation (kt)` | measure | float64 |  | 42.13390835671613 |

### `full_results_tables_fig1_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 10.213000929547192 |
| `Material extraction (kt)` | measure | float64 |  | 3.6170685138073218 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 23.5100000568968 |
| `Land use (km2)` | measure | float64 |  | 35.20707479237855 |
| `Waste generation (kt)` | measure | float64 |  | 14.59924820606745 |

### `full_results_tables_fig2_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 706.5277153933312 |
| `Material extraction (kt)` | measure | float64 |  | 54.88861254250904 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 90.4110443436922 |
| `Land use (km2)` | measure | float64 |  | 5520.277479487429 |
| `Waste generation (kt)` | measure | float64 |  | 57.35197527105783 |

### `full_results_tables_fig2_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 13.377650031618863 |
| `Material extraction (kt)` | measure | float64 |  | 1.1408434455682162 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 85.19065430993561 |
| `Land use (km2)` | measure | float64 |  | 98.9068332044364 |
| `Waste generation (kt)` | measure | float64 |  | 19.872253838919033 |

### `full_results_tables_fig3_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 255.22901041375133 |
| `Material extraction (kt)` | measure | float64 |  | 25.6351 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.1776 |
| `Land use (km2)` | measure | float64 |  | 1.6692 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `full_results_tables_fig3_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 4.832597936134411 |
| `Material extraction (kt)` | measure | float64 |  | 0.5328179098867949 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.1673452653409167 |
| `Land use (km2)` | measure | float64 |  | 0.0299070629326725 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `scopes_summary.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Component` | dimension | str |  | Scope 1 direct (DRIVHUS, excl. medical N |
| `kt_CO2eq` | measure | float64 |  | 118.5541696372094 |

### `steenmeijer_table.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Category group` | dimension | str |  | Total |
| `Climate change (kt CO2eq)` | dimension | str |  | 5,281 (100·0%) |
| `Material extraction (kt)` | dimension | str |  | 4,811 (100·0%) |
| `Blue water consumption (Mm3)` | dimension | str |  | 106 (100·0%) |
| `Land use (km2)` | dimension | str |  | 5,581 (100·0%) |
| `Waste generation (kt)` | dimension | str |  | 289 (100·0%) |
| `Basic price expenditure (million euros)` | dimension | str |  | 49,709 (100·0%) |

### `table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Global warming (ktCO2eq)` | measure | float64 |  | 5281.4037870882485 |
| `Material extraction (kt)` | measure | float64 |  | 4811.230914787854 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 106.1278905251322 |
| `Land use (km2)` | measure | float64 |  | 5581.290291720555 |
| `Waste generation (kt)` | measure | float64 |  | 288.60327437412263 |
| `Expenditure (MEUR)` | measure | float64 |  | 49709.03368460669 |

### `table_s05_dk.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Global warming (ktCO2eq) |
| `Healthcare footprint` | measure | float64 |  | 5281.4037870882485 |
| `National consumption footprint` | measure | float64 |  | 77477.50333386465 |
| `Healthcare share of national consumption footprint (%)` | measure | float64 | % | 6.816693310740435 |
