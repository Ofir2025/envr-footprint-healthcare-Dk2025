# 03_cabernard_target_scope3 - data dictionary

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

### `cabernard_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `target_set` | dimension | str |  | T1 Danish health and social work |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | kt CO2eq | 1692.585287632406 |
| `share_of_total_pct` | measure | float64 | % | 39.124088474656496 |

### `cabernard_target_scope3.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `analysis_year` | measure | int64 |  | 2022 |
| `target` | dimension | str |  | T1 Danish health and social work |
| `n_target_nodes` | measure | int64 |  | 1 |
| `e_T_naive_MtCO2e` | measure | float64 |  | 4.391361962425819 |
| `e_T_wdc_MtCO2e` | measure | float64 |  | 4.326197372569628 |
| `double_counting_factor_f_T` | measure | float64 |  | 0.0148392663628651 |
| `overestimate_vs_correct_pct` | measure | float64 | % | 1.5062787072399624 |
| `complement_identity_rel_dev` | measure | float64 |  | 7.702710422487045e-16 |
| `note` | dimension | str |  | target-perspective scope 3 (Cabernard et |

### `cabernard_target_scope3_by_producing_node.csv.gz`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `target_set` | dimension | str |  | T1 Danish health and social work |
| `n_target_nodes` | measure | int64 |  | 1 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `quantity` | dimension | str |  | corrected target scope 3 (Cabernard eq.  |
| `producing_country_iso3` | dimension | str |  | DNK |
| `producing_country_name` | dimension | str |  | Denmark |
| `producing_world_region` | dimension | str |  | Denmark |
| `producing_sector_code` | dimension | str |  | TWAS |
| `producing_sector_name` | dimension | str |  | Sea and coastal water transport |
| `producing_sector_group` | dimension | str |  | Transport |
| `value` | measure | float64 | kt CO2eq | 948.5154083597616 |
