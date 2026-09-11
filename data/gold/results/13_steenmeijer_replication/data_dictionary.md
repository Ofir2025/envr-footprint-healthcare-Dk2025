# 13_steenmeijer_replication - data dictionary

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

### `national_shares_dk_vs_nl.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `netherlands_national` | measure | int64 | varies by row | 241358 |
| `netherlands_health_share_pct` | measure | float64 | % | 7.3 |
| `denmark_national` | measure | float64 | varies by row | 77240.62118630517 |
| `denmark_health_share_pct` | measure | float64 | % | 5.05750214089784 |
| `share_difference_pp` | measure | float64 | % | -2.2424978591021603 |
| `comparability_note` | dimension | str |  | NOT on the same boundary: the Dutch figu |
| `source_netherlands` | dimension | str |  | Steenmeijer et al. 2022 table S7 (= RIVM |
| `source_denmark` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |

### `nl_contribution_by_purchased_node.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `purchased_country_iso3` | dimension | str |  | AUT |
| `purchased_country_name` | dimension | str |  | Austria |
| `purchased_world_region` | dimension | str |  | Europe |
| `purchased_sector_code` | dimension | str |  | PARI |
| `purchased_sector_name` | dimension | str |  | Cultivation of paddy rice |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `ghg_protocol_scope` | dimension | str |  | Scope 3 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `value` | measure | float64 | kt CO2eq | 0.0 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Con |

### `nl_contribution_by_purchased_product.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `purchased_sector_code` | dimension | str |  | ALUM |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `purchased_sector_name` | dimension | str |  | Aluminium production |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `value` | measure | float64 | varies by row | 3.42443379349901 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Con |

### `nl_contribution_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `purchased_sector_group` | dimension | str |  | Chemical |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `value` | measure | float64 | varies by row | 7334.786301615341 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Con |

### `nl_expenditure_by_purchased_node.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `purchased_country_iso3` | dimension | str |  | AUT |
| `purchased_country_name` | dimension | str |  | Austria |
| `purchased_world_region` | dimension | str |  | Europe |
| `purchased_sector_code` | dimension | str |  | PARI |
| `purchased_sector_name` | dimension | str |  | Cultivation of paddy rice |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `demand_component` | dimension | str |  | total |
| `indicator` | dimension | str |  | expenditure |
| `unit` | dimension | str |  | M.EUR |
| `value` | measure | float64 | M.EUR | 0.0 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Exp |

### `nl_expenditure_by_purchased_product.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `purchased_sector_code` | dimension | str |  | ALUM |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `purchased_sector_name` | dimension | str |  | Aluminium production |
| `demand_component` | dimension | str |  | total |
| `indicator` | dimension | str |  | expenditure |
| `unit` | dimension | str |  | M.EUR |
| `value` | measure | float64 | M.EUR | 2.269081537485643 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Exp |

### `nl_expenditure_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `purchased_sector_group` | dimension | str |  | Chemical |
| `demand_component` | dimension | str |  | total |
| `indicator` | dimension | str |  | expenditure |
| `unit` | dimension | str |  | M.EUR |
| `value` | measure | float64 | M.EUR | 5861.267663643347 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Exp |

### `nl_expenditure_by_sector_group_and_country.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `purchased_country_name` | dimension | str |  | Australia |
| `purchased_sector_group` | dimension | str |  | Chemical |
| `demand_component` | dimension | str |  | total |
| `indicator` | dimension | str |  | expenditure |
| `unit` | dimension | str |  | M.EUR |
| `value` | measure | float64 | M.EUR | 31.68051465715346 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Exp |

### `nl_figure1_contribution_groups.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `figure` | measure | int64 | varies by row | 1 |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `figure_group` | dimension | str |  | Other (scope 3) |
| `legend_position` | measure | int64 | varies by row | 1 |
| `value` | measure | float64 | varies by row | 15.130738511971137 |
| `share_pct` | measure | float64 | % | 3.8320811451697967 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Con |

### `nl_figure2_hotspot_sector_groups.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `figure` | measure | int64 | varies by row | 2 |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `figure_group` | dimension | str |  | Other |
| `legend_position` | measure | int64 | varies by row | 1 |
| `value` | measure | float64 | varies by row | 19.378422414583973 |
| `share_pct` | measure | float64 | % | 4.911507748994972 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Hot |

### `nl_figure3_hotspot_world_regions.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `figure` | measure | int64 | varies by row | 3 |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `figure_group` | dimension | str |  | Africa |
| `legend_position` | measure | int64 | varies by row | 1 |
| `value` | measure | float64 | varies by row | 28.50293501421166 |
| `share_pct` | measure | float64 | % | 7.224137403777721 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Hot |

### `nl_hotspot_by_producing_country.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `ghg_protocol_scope` | dimension | str |  | Direct |
| `producing_country_name` | dimension | str |  | Netherlands |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `value` | measure | float64 | varies by row | 1713.2 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Hot |

### `nl_hotspot_by_producing_node.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `producing_country_iso3` | dimension | str |  | AUT |
| `producing_country_name` | dimension | str |  | Austria |
| `producing_world_region` | dimension | str |  | Europe |
| `producing_sector_code` | dimension | str |  | PARI |
| `producing_sector_name` | dimension | str |  | Cultivation of paddy rice |
| `producing_sector_group` | dimension | str |  | Food and catering |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `ghg_protocol_scope` | dimension | str |  | Indirect |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `value` | measure | float64 | kt CO2eq | 0.0 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Hot |

### `nl_hotspot_by_producing_sector.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `ghg_protocol_scope` | dimension | str |  | Direct |
| `producing_sector_code` | dimension | str |  | B_ANAE |
| `component_type` | dimension | str |  | bottom-up item |
| `producing_sector_name` | dimension | str |  | Emission from anesthetic gases |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `value` | measure | float64 | varies by row | 14.2 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Hot |

### `nl_hotspot_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `ghg_protocol_scope` | dimension | str |  | Direct |
| `producing_sector_group` | dimension | str |  | Operational impact |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `value` | measure | float64 | varies by row | 1713.2 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Hot |

### `nl_hotspot_by_sector_group_and_country.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `ghg_protocol_scope` | dimension | str |  | Direct |
| `producing_country_name` | dimension | str |  | Netherlands |
| `producing_sector_group` | dimension | str |  | Operational impact |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `value` | measure | float64 | kt CO2eq | 1713.2 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Hot |

### `nl_hotspot_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `ghg_protocol_scope` | dimension | str |  | Direct |
| `producing_world_region` | dimension | str |  | Netherlands |
| `producing_country_name` | dimension | str |  | Netherlands |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `value` | measure | float64 | varies by row | 1713.2 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Hot |

### `nl_intensity_by_purchased_node.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `purchased_country_iso3` | dimension | str |  | AUT |
| `purchased_country_name` | dimension | str |  | Austria |
| `purchased_world_region` | dimension | str |  | Europe |
| `purchased_sector_code` | dimension | str |  | WHEA |
| `purchased_sector_name` | dimension | str |  | Cultivation of wheat |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `Total (MEUR)` | measure | float64 | kt CO2eq per M.EUR | 0.0040941750473664 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per M.EUR |
| `value` | measure | float64 | kt CO2eq per M.EUR | 1.324706513490257 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Int |

### `nl_intensity_by_purchased_product.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `purchased_sector_name` | dimension | str |  | Activities auxiliary to financial interm |
| `Total (MEUR)` | measure | float64 | varies by row | 110.8931361423936 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per M.EUR |
| `value` | measure | float64 | varies by row | 0.0813831062701448 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Int |

### `nl_intensity_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `purchased_sector_group` | dimension | str |  | Chemical |
| `Total (MEUR)` | measure | float64 | varies by row | 5861.267663643347 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per M.EUR |
| `value` | measure | float64 | varies by row | 1.238279279862107 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Int |

### `nl_intensity_by_sector_group_and_country.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `purchased_country_name` | dimension | str |  | Australia |
| `purchased_sector_group` | dimension | str |  | Chemical |
| `Total (MEUR)` | measure | float64 | kt CO2eq per M.EUR | 31.68051465715346 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per M.EUR |
| `value` | measure | float64 | kt CO2eq per M.EUR | 0.7016201389319593 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Int |

### `nl_published_figure_shares.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `figure` | measure | int64 |  | 1 |
| `article_page` | dimension | str |  | e954 |
| `indicator` | dimension | str |  | climate_change |
| `figure_group` | dimension | str |  | Other (scope 3) |
| `published_share_pct` | measure | float64 | % | 12.213 |
| `archive_share_pct` | measure | float64 | % | 11.877707372557786 |
| `difference_pp` | measure | float64 |  | -0.3352926274422128 |
| `note` | dimension | str |  | drawn at the composing spreadsheet's hai |
| `source` | dimension | str |  | Steenmeijer et al. (2022) figure 1, p e9 |

### `nl_table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `table_row` | dimension | str |  | Total |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `value` | measure | float64 | varies by row | 17718.55838682618 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Tab |

### `nl_table_s05.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `study` | dimension | str |  | steenmeijer_2022 |
| `consuming_country_iso3` | dimension | str |  | NLD |
| `reference_year` | measure | int64 |  | 2016 |
| `indicator` | dimension | str |  | climate_change |
| `quantity` | dimension | str |  | Healthcare footprint |
| `unit` | dimension | str |  | kt CO2eq |
| `value` | measure | float64 | varies by row | 17718.55838682618 |
| `source` | dimension | str |  | archive/rivm_steenmeijer_2022/output/Tab |

### `template_table_dk_vs_nl.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `analysis_year_denmark` | measure | int64 | varies by row | 2022 |
| `reference_year_netherlands` | measure | int64 | varies by row | 2016 |
| `table_row` | dimension | str |  | Total |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `netherlands_2016` | measure | float64 | varies by row | 17575.0 |
| `denmark_2022` | measure | float64 | varies by row | 4652.070759298349 |
| `netherlands_per_capita` | measure | float64 | varies by row | 1031.9833210356544 |
| `denmark_per_capita` | measure | float64 | varies by row | 792.0548435661589 |
| `per_capita_unit` | dimension | str |  | kt CO2eq per million population |
| `dk_as_pct_of_nl_per_capita` | measure | float64 | varies by row | 76.75074077469455 |
| `source_netherlands` | dimension | str |  | Steenmeijer et al. 2022, Lancet Planet H |
| `source_denmark` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
