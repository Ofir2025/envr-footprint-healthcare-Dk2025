# scenarios/health_only - data dictionary

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
| `Global warming (ktCO2eq)` | measure | float64 |  | 324.04821578431256 |
| `Material extraction (kt)` | measure | float64 |  | 104.54898649813676 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 14.989565794430574 |
| `Land use (km2)` | measure | float64 |  | 1180.5148238090903 |
| `Waste generation (kt)` | measure | float64 |  | 25.312709611331943 |

### `full_results_tables_fig1_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 7.868889746695564 |
| `Material extraction (kt)` | measure | float64 |  | 2.8387197500577734 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 17.758265274067867 |
| `Land use (km2)` | measure | float64 |  | 28.811967886813942 |
| `Waste generation (kt)` | measure | float64 |  | 11.056808884317157 |

### `full_results_tables_fig2_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 506.00585713762337 |
| `Material extraction (kt)` | measure | float64 |  | 40.75597665441908 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 72.12182911225848 |
| `Land use (km2)` | measure | float64 |  | 4052.534475515813 |
| `Waste generation (kt)` | measure | float64 |  | 38.5683318595245 |

### `full_results_tables_fig2_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 12.287382269212609 |
| `Material extraction (kt)` | measure | float64 |  | 1.1066084879154223 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 85.44334045368728 |
| `Land use (km2)` | measure | float64 |  | 98.90726555387204 |
| `Waste generation (kt)` | measure | float64 |  | 16.846978490472374 |

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
| `Global warming (ktCO2eq)` | measure | float64 |  | 6.1977472649959 |
| `Material extraction (kt)` | measure | float64 |  | 0.6960456251386327 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.2104042209045364 |
| `Land use (km2)` | measure | float64 |  | 0.0407389520459315 |
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
| `Climate change (kt CO2eq)` | dimension | str |  | 4,118 (100·0%) |
| `Material extraction (kt)` | dimension | str |  | 3,683 (100·0%) |
| `Blue water consumption (Mm3)` | dimension | str |  | 84 (100·0%) |
| `Land use (km2)` | dimension | str |  | 4,097 (100·0%) |
| `Waste generation (kt)` | dimension | str |  | 229 (100·0%) |
| `Basic price expenditure (million euros)` | dimension | str |  | 31,079 (100·0%) |

### `table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Global warming (ktCO2eq)` | measure | float64 |  | 4118.093228087125 |
| `Material extraction (kt)` | measure | float64 |  | 3682.962592415446 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 84.40895303168854 |
| `Land use (km2)` | measure | float64 |  | 4097.307162241296 |
| `Waste generation (kt)` | measure | float64 |  | 228.93322907331077 |
| `Expenditure (MEUR)` | measure | float64 |  | 31079.141889348888 |

### `table_s05_dk.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Global warming (ktCO2eq) |
| `Healthcare footprint` | measure | float64 |  | 4118.093228087125 |
| `National consumption footprint` | measure | float64 |  | 77477.50333386465 |
| `Healthcare share of national consumption footprint (%)` | measure | float64 | % | 5.315211578697254 |
