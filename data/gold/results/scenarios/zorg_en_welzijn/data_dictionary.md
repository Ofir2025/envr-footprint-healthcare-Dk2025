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
| `Global warming (ktCO2eq)` | measure | float64 |  | 538.9906423792066 |
| `Material extraction (kt)` | measure | float64 |  | 174.00157878159516 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 24.950061108044412 |
| `Land use (km2)` | measure | float64 |  | 1964.9697803633392 |
| `Waste generation (kt)` | measure | float64 |  | 42.132363214616085 |

### `full_results_tables_fig1_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 11.41337721764726 |
| `Material extraction (kt)` | measure | float64 |  | 4.301295664937434 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 29.22851089045275 |
| `Land use (km2)` | measure | float64 |  | 40.578510127830505 |
| `Waste generation (kt)` | measure | float64 |  | 16.83645941959149 |

### `full_results_tables_fig2_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 626.635031756535 |
| `Material extraction (kt)` | measure | float64 |  | 47.19582659820925 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 72.47369561512272 |
| `Land use (km2)` | measure | float64 |  | 4788.619134637775 |
| `Waste generation (kt)` | measure | float64 |  | 53.27329947428006 |

### `full_results_tables_fig2_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 13.269287874200066 |
| `Material extraction (kt)` | measure | float64 |  | 1.1666744966999625 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 84.90152358284163 |
| `Land use (km2)` | measure | float64 |  | 98.8895768245818 |
| `Waste generation (kt)` | measure | float64 |  | 21.288474614576263 |

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
| `Global warming (ktCO2eq)` | measure | float64 |  | 5.20342805605865 |
| `Material extraction (kt)` | measure | float64 |  | 0.6836971013821084 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.2253645069243626 |
| `Land use (km2)` | measure | float64 |  | 0.0371810293808436 |
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
| `Climate change (kt CO2eq)` | dimension | str |  | 4,722 (100·0%) |
| `Material extraction (kt)` | dimension | str |  | 4,045 (100·0%) |
| `Blue water consumption (Mm3)` | dimension | str |  | 85 (100·0%) |
| `Land use (km2)` | dimension | str |  | 4,842 (100·0%) |
| `Waste generation (kt)` | dimension | str |  | 250 (100·0%) |
| `Basic price expenditure (million euros)` | dimension | str |  | 49,709 (100·0%) |

### `table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Global warming (ktCO2eq)` | measure | float64 |  | 4722.446582645355 |
| `Material extraction (kt)` | measure | float64 |  | 4045.329415505929 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 85.36206720060494 |
| `Land use (km2)` | measure | float64 |  | 4842.390157187368 |
| `Waste generation (kt)` | measure | float64 |  | 250.24479413759184 |
| `Expenditure (MEUR)` | measure | float64 |  | 49709.03368460669 |

### `table_s05_dk.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Global warming (ktCO2eq) |
| `Healthcare footprint` | measure | float64 |  | 4722.446582645355 |
| `National consumption footprint` | measure | float64 |  | 77240.6211863052 |
| `Healthcare share of national consumption footprint (%)` | measure | float64 | % | 6.1139417447909485 |
