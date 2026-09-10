# 19_tables_of_record - data dictionary

One row per column of every table in this folder. Units are the
table's own; `varies by row` means the table carries a `unit`
column and the value is read from there.

## Common columns

Every gold table shares this vocabulary; columns particular to one table
are described below, per table.

| Column | Meaning |
|:---|:---|
| `analysis_year` | year of the Danish expenditure data and of the MRIO background |
| `model` | MRIO release actually used (e.g. `EXIOBASE v3.8.2 IOT_2022_ixi with Danish sea-transport reallocation (Rørmose Jensen & Iliev 2022)`) - **not** v3.10.2, which this study rejects (see `docs/methods/exiobase_version_vintage_and_classification.md`) |
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

### `table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Impact category` | dimension | str |  | Blue water consumption |
| `Unit` | dimension | str |  | Mm³ |
| `Health care` | measure | float64 |  | 95.5 |
| `Per person` | measure | float64 |  | 16.3 |
| `Danish total` | measure | float64 |  | 1276.4 |
| `Share of national (%)` | measure | float64 | % | 7.5 |

### `table_02.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Impact category` | dimension | str |  | Blue water consumption |
| `Unit` | dimension | str |  | Mm³ |
| `2019` | measure | float64 |  | 57.5 |
| `2022` | measure | float64 |  | 95.5 |
| `Change (%)` | measure | float64 |  | 66.2 |

### `table_03.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Activity group` | dimension | str |  | Transport |
| `2019 (kt CO₂-eq)` | measure | float64 |  | 2605.2 |
| `2022 (kt CO₂-eq)` | measure | float64 |  | 595.8 |
| `Change (kt)` | measure | float64 |  | -2009.3 |
| `Driver` | dimension | str |  | sea-transport reallocation, applied in 2 |

### `table_04.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Impact category` | dimension | str |  | Blue water consumption |
| `Unit` | dimension | str |  | Mm³ |
| `Scope 1` | measure | float64 |  | 0.0 |
| `Scope 2` | measure | float64 |  | 0.07 |
| `Scope 3` | measure | float64 |  | 95.36 |
| `Outside protocol` | measure | float64 |  | 0.08 |
| `TOTAL` | measure | float64 |  | 95.5 |

### `table_05.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Source` | dimension | str |  | Eurostat FIGARO (env_ac_ghgfp) |
| `Year` | measure | int64 |  | 2022 |
| `Model family` | dimension | str |  | national accounts (FIGARO) |
| `Mt CO₂-eq` | measure | float64 |  | 57.4 |
| `t per person` | measure | float64 |  | 9.77 |
| `Capital` | dimension | str |  | exogenous |

### `table_06.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Basis` | dimension | str |  | Schmidt & Merciai 2023 (published compar |
| `Mt CO₂-eq` | measure | float64 |  | 6.1 |
| `t per person` | measure | float64 |  | 1.07 |
| `Share of national (%)` | measure | float64 | % | 8.3 |
| `Comparable` | dimension | str |  | yes |

### `table_07.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Vintage` | dimension | str |  | DNK |
| `Health care (kt CO₂-eq)` | measure | int64 |  | 2022 |

### `table_08.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Impact category` | dimension | str |  | Blue water consumption |
| `Unit` | dimension | str |  | Mm³ |
| `Capital excluded (headline)` | measure | float64 |  | 95.3 |
| `Capital as a service flow` | measure | float64 |  | 102.4 |
| `Capital endogenised` | measure | float64 |  | 105.4 |
| `Endogenised change (%)` | measure | float64 |  | 10.6 |

### `table_10.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Impact category` | dimension | str |  | Global warming (ktCO2eq) |
| `Deterministic` | measure | float64 |  | 4712.4 |
| `Median` | measure | float64 |  | 4733.7 |
| `2.5th percentile` | measure | float64 |  | 4063.6 |
| `97.5th percentile` | measure | float64 |  | 5531.3 |
| `CV, Tier 2 (%)` | measure | float64 |  | 7.87 |
| `CV, Tier 1 (%)` | measure | float64 |  | 7.84 |

### `table_11.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contributor` | dimension | str |  | Input-output model |
| `Share of variance (%)` | measure | float64 | % | 78.8 |

### `table_12.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Quantity` | dimension | str |  | baseline climate footprint |
| `Value` | measure | float64 |  | 4712.4 |
| `Unit` | dimension | str |  | kt CO₂-eq |

### `table_13.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Scenario` | dimension | str |  | C3  maximum modelled, KF22 to 2035 |
| `Climate (%)` | measure | float64 |  | -9.77 |
| `Material (%)` | dimension | str |  | -4.56 |
| `Blue water (%)` | dimension | str |  | -1.37 |
| `Land (%)` | dimension | str |  | -1.42 |
| `Waste (%)` | dimension | str |  | -2.58 |

### `table_14.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Danish industry` | dimension | str |  | TOTAL (all 163 industries) |
| `National accounts (M.EUR)` | measure | int64 |  | 706281 |
| `EXIOBASE v3.8.2` | dimension | str |  | 592,645  (0.84x) |
| `EXIOBASE v3.10.2` | dimension | str |  | 681,918  (0.97x) |

### `table_15.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Parameter` | dimension | str |  | Input-output model |
| `GSD` | dimension | str |  | CV 8.35 % |
| `95 % factor range` | dimension | str |  | 0.85 to 1.18 |
| `Basis` | dimension | str |  | Lenzen et al. 2020 SI Tab. SI 7.1: relat |

### `tables_of_record_index.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `number` | measure | int64 |  | 1 |
| `title` | dimension | str |  | The Danish health-care footprint in 2022 |
| `source` | dimension | str |  | 01_eriksen_replication/2022/figure1_acti |
| `rows` | measure | int64 |  | 5 |
| `columns` | measure | int64 |  | 6 |
| `supersedes` | dimension | bool |  | True |
