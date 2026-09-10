# 12_impact_categories_full - data dictionary

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

### `impact_categories_all_methods.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `analysis_year` | measure | int64 |  | 2022 |
| `method` | dimension | str |  | Value Added |
| `indicator` | dimension | str |  | Value Added |
| `unit` | dimension | str |  | M.EUR |
| `sheet` | dimension | str |  | Q_factorinputs |
| `n_nonzero_factors` | measure | int64 |  | 8 |
| `healthcare_supply_chain` | measure | float64 | varies by row | 11977.476858927186 |
| `national_supply_chain` | measure | float64 | varies by row | 286028.6902930252 |
| `healthcare_share_of_national_pct` | measure | float64 | % | 4.187508898725064 |
| `healthcare_per_capita` | measure | float64 | varies by row | 0.0020392678982479 |
| `component` | dimension | str |  | supply chain (MRIO) only; the Danish dir |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `quality_flag` | dimension | str |  | ok |
| `quality_note` | dimension | str |  | WRONG STRESSOR CLASS: the row characteri |

### `impact_categories_by_producing_node.csv.gz`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `analysis_year` | measure | int64 |  | 2022 |
| `method` | dimension | str |  | Value Added |
| `indicator` | dimension | str |  | Value Added |
| `unit` | dimension | str |  | M.EUR |
| `quality_flag` | dimension | str |  | ok |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `producing_country_iso3` | dimension | str |  | DNK |
| `producing_country_name` | dimension | str |  | Denmark |
| `producing_world_region` | dimension | str |  | Denmark |
| `producing_sector_code` | dimension | str |  | OBUS |
| `producing_sector_name` | dimension | str |  | Other business activities (74) |
| `producing_sector_group` | dimension | str |  | Services |
| `value` | measure | float64 | M.EUR | 799.9756103392839 |

### `impact_categories_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `method` | dimension | str |  | Damage Approach |
| `indicator` | dimension | str |  | EPS (Steen, 1999)) |
| `unit` | dimension | str |  | elu |
| `producing_sector_group` | dimension | str |  | Chemical |
| `value` | measure | float64 | varies by row | 175687614.1292201 |

### `impact_categories_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `method` | dimension | str |  | Damage Approach |
| `indicator` | dimension | str |  | EPS (Steen, 1999)) |
| `unit` | dimension | str |  | elu |
| `quality_flag` | dimension | str |  | ok |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 336581947.66712177 |
| `share_of_total_pct` | measure | float64 | % | 12.55580440413941 |

### `stressor_totals_uncharacterised.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `analysis_year` | measure | int64 |  | 2022 |
| `stressor` | dimension | str |  | Taxes less subsidies on products purchas |
| `healthcare_supply_chain` | measure | float64 |  | 829.2950355096353 |
| `national_supply_chain` | measure | float64 |  | 16395.595223811626 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
