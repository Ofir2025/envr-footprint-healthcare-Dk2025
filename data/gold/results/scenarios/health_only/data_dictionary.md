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
| `model` | MRIO release actually used (e.g. `EXIOBASE v3.8.2 IOT_2022_ixi with Danish sea-transport reallocation (Rørmose Jensen & Iliev 2022)`) - **not** v3.10.2, which this study rejects (see `docs/methods/exiobase_release_and_classification.md`) |
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

Every impact cell is $E_{ij} = s_i\,L_{ij}\,y_{H,j}$: pressure arising
in node *i* caused by Danish healthcare final demand for node *j*. Summing
over *i* gives the **consumption / contribution** perspective (by
purchased product); summing over *j* gives the **production / hotspot**
perspective (by producing node). Both are marginals of the same array, so
they sum to the identical total - verified to machine precision by
`analysis.validate_io_identities` (tests T5/T6). Allocating production
emissions to final demand is additive and does not double count (Wood et
al. 2018); embodied-flow tables ($\mathbf{E}_Z$) would.

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
| `Global warming (ktCO2eq)` | measure | float64 |  | 323.80840386945425 |
| `Material extraction (kt)` | measure | float64 |  | 104.53460425087178 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 14.98920172004991 |
| `Land use (km2)` | measure | float64 |  | 1180.491233433167 |
| `Waste generation (kt)` | measure | float64 |  | 25.31178133919173 |

### `full_results_tables_fig1_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 9.353356981968664 |
| `Material extraction (kt)` | measure | float64 |  | 3.586217054000202 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 23.55010481885589 |
| `Land use (km2)` | measure | float64 |  | 35.13430990992944 |
| `Waste generation (kt)` | measure | float64 |  | 14.206115988226731 |

### `full_results_tables_fig2_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 426.2808013022775 |
| `Material extraction (kt)` | measure | float64 |  | 33.069292825529246 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 54.20579520199274 |
| `Land use (km2)` | measure | float64 |  | 3322.5915076197175 |
| `Waste generation (kt)` | measure | float64 |  | 34.49729033645657 |

### `full_results_tables_fig2_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 12.313320042018756 |
| `Material extraction (kt)` | measure | float64 |  | 1.134491900978813 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 85.16478613326144 |
| `Land use (km2)` | measure | float64 |  | 98.888459673953 |
| `Waste generation (kt)` | measure | float64 |  | 19.361438898037083 |

### `full_results_tables_fig3_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 213.94798586629048 |
| `Material extraction (kt)` | measure | float64 |  | 24.433791658440025 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.1704968294729508 |
| `Land use (km2)` | measure | float64 |  | 1.5902403979778554 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `full_results_tables_fig3_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 6.179987497135411 |
| `Material extraction (kt)` | measure | float64 |  | 0.8382380262242656 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.2678740522919069 |
| `Land use (km2)` | measure | float64 |  | 0.0473294484460961 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `scopes_summary.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Component` | dimension | str |  | Scope 1 direct (DRIVHUS, excl. medical N |
| `kt_CO2eq` | measure | float64 |  | 81.93 |

### `steenmeijer_table.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Category group` | dimension | str |  | Total |
| `Climate change (kt CO2eq)` | dimension | str |  | 3,462 (100·0%) |
| `Material extraction (kt)` | dimension | str |  | 2,915 (100·0%) |
| `Blue water consumption (Mm3)` | dimension | str |  | 64 (100·0%) |
| `Land use (km2)` | dimension | str |  | 3,360 (100·0%) |
| `Waste generation (kt)` | dimension | str |  | 178 (100·0%) |
| `Basic price expenditure (million euros)` | dimension | str |  | 31,079 (100·0%) |

### `table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Global warming (ktCO2eq)` | measure | float64 |  | 3461.9485227997866 |
| `Material extraction (kt)` | measure | float64 |  | 2914.8989778594314 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 63.648131655229285 |
| `Land use (km2)` | measure | float64 |  | 3359.938579865337 |
| `Waste generation (kt)` | measure | float64 |  | 178.17524058066715 |
| `Expenditure (MEUR)` | measure | float64 |  | 31079.141889348888 |

### `table_s05_dk.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Global warming (ktCO2eq) |
| `Healthcare footprint` | measure | float64 |  | 3461.9485227997866 |
| `National consumption footprint` | measure | float64 |  | 77240.6211863052 |
| `Healthcare share of national consumption footprint (%)` | measure | float64 | % | 4.482030917966766 |
