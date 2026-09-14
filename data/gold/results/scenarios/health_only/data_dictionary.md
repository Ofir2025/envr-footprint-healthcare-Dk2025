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
| `Global warming (ktCO2eq)` | measure | float64 |  | 9.052912759629526 |
| `Material extraction (kt)` | measure | float64 |  | 3.582254920261895 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 23.542012279092496 |
| `Land use (km2)` | measure | float64 |  | 35.132111915858054 |
| `Waste generation (kt)` | measure | float64 |  | 13.27703786640586 |

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
| `Global warming (ktCO2eq)` | measure | float64 |  | 11.917797250408317 |
| `Material extraction (kt)` | measure | float64 |  | 1.1332384886590845 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 85.13552089544082 |
| `Land use (km2)` | measure | float64 |  | 98.88227323543607 |
| `Waste generation (kt)` | measure | float64 |  | 18.095203334280907 |

### `full_results_tables_fig3_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 245.7291104137513 |
| `Material extraction (kt)` | measure | float64 |  | 27.657799955171782 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.1923758018470864 |
| `Land use (km2)` | measure | float64 |  | 1.8004505070789103 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `full_results_tables_fig3_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 6.87000143447145 |
| `Material extraction (kt)` | measure | float64 |  | 0.9477941843569668 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.3021450757598646 |
| `Land use (km2)` | measure | float64 |  | 0.053582463742405 |
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
| `Climate change (kt CO2eq)` | dimension | str |  | 3,577 (100·0%) |
| `Material extraction (kt)` | dimension | str |  | 2,918 (100·0%) |
| `Blue water consumption (Mm3)` | dimension | str |  | 64 (100·0%) |
| `Land use (km2)` | dimension | str |  | 3,360 (100·0%) |
| `Waste generation (kt)` | dimension | str |  | 191 (100·0%) |
| `Basic price expenditure (million euros)` | dimension | str |  | 31,079 (100·0%) |

### `table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Global warming (ktCO2eq)` | measure | float64 |  | 3576.8421994901246 |
| `Material extraction (kt)` | measure | float64 |  | 2918.1229861561633 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 63.67001062760342 |
| `Land use (km2)` | measure | float64 |  | 3360.1487899744384 |
| `Waste generation (kt)` | measure | float64 |  | 190.6432865062213 |
| `Expenditure (MEUR)` | measure | float64 |  | 31079.141889348888 |

### `table_s05_dk.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Global warming (ktCO2eq) |
| `Healthcare footprint` | measure | float64 |  | 3576.8421994901246 |
| `National consumption footprint` | measure | float64 |  | 77240.6211863052 |
| `Healthcare share of national consumption footprint (%)` | measure | float64 | % | 4.630778655783649 |
