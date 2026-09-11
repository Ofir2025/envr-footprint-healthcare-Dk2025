# 01_eriksen_replication/2016a - data dictionary

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

### `contribution_by_purchased_product.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `analysis` | dimension | str |  | B L diag(y): impacts attributed along th |
| `purchased_country_iso3` | dimension | str |  | AUT |
| `purchased_country_name` | dimension | str |  | Austria |
| `purchased_world_region` | dimension | str |  | Europe |
| `purchased_sector_code` | dimension | str |  | OCER |
| `purchased_sector_name` | dimension | str |  | Cultivation of cereal grains nec |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `ghg_protocol_scope` | dimension | str |  | Scope 3 |
| `value` | measure | float64 | kt CO2eq | 0.0002650169669765 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2016 |
| `model` | dimension | str |  | EXIOBASE v3.7 IOT_2016_ixi |

### `contribution_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt |
| `purchased_sector_group` | dimension | str |  | Chemical |
| `value` | measure | float64 | varies by row | 4906.351461409792 |

### `contribution_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `purchased_world_region` | dimension | str |  | Denmark |
| `value` | measure | float64 | varies by row | 5886.753629620406 |

### `contribution_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 23.231763059540324 |
| `share_of_total_pct` | measure | float64 | % | 27.714620942171283 |

### `figure1_activity_contributions.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `contribution_group` | dimension | str |  | Pharmaceuticals and chemical products |
| `value` | measure | float64 | varies by row | 39.310976196267745 |
| `share_pct` | measure | float64 | % | 46.89651841550064 |

### `figure2_sector_contributions.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `hotspot_group` | dimension | str |  | Agricultural sector |
| `value` | measure | float64 | varies by row | 70.23418710663205 |
| `share_pct` | measure | float64 | % | 83.78674781819845 |

### `figure2b_top_origin_industry_pairs.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_country_iso3` | dimension | str |  | BRA |
| `producing_world_region` | dimension | str |  | America |
| `producing_sector_code` | dimension | str |  | SUGB |
| `producing_sector_name` | dimension | str |  | Cultivation of sugar cane, sugar beet |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `value` | measure | float64 | varies by row | 10.33786469198625 |
| `rank` | measure | int64 |  | 1 |
| `share_pct` | measure | float64 | % | 12.35681574758263 |
| `mrio_coverage_pct` | measure | float64 | % | 99.80471204718272 |

### `figure3_geographical_origin.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `producing_world_region` | dimension | str |  | Asia and Pacific |
| `value` | measure | float64 | varies by row | 36.098603534744235 |
| `share_pct` | measure | float64 | % | 43.06427845975792 |

### `full_results_tables_fig1_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 415.982511365617 |
| `Material extraction (kt)` | measure | float64 |  | 181.62188945745797 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 19.32841664627366 |
| `Land use (km2)` | measure | float64 |  | 1399.7565045770975 |
| `Waste generation (kt)` | measure | float64 |  | 36.93823118982242 |

### `full_results_tables_fig1_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 5.047734810328067 |
| `Material extraction (kt)` | measure | float64 |  | 2.373756011475334 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 23.058075247709045 |
| `Land use (km2)` | measure | float64 |  | 26.522031349918713 |
| `Waste generation (kt)` | measure | float64 |  | 10.026356119116144 |

### `full_results_tables_fig2_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 537.9949912019588 |
| `Material extraction (kt)` | measure | float64 |  | 20.945951425072103 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 70.23418710663213 |
| `Land use (km2)` | measure | float64 |  | 5167.533151791351 |
| `Waste generation (kt)` | measure | float64 |  | 57.232528257476375 |

### `full_results_tables_fig2_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 6.528293867235466 |
| `Material extraction (kt)` | measure | float64 |  | 0.2737587317247983 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 83.78674781819839 |
| `Land use (km2)` | measure | float64 |  | 97.91236961957304 |
| `Waste generation (kt)` | measure | float64 |  | 15.534953662452152 |

### `full_results_tables_fig3_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 230.1477330605942 |
| `Material extraction (kt)` | measure | float64 |  | 23.6533 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.1637 |
| `Land use (km2)` | measure | float64 |  | 1.5402 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `full_results_tables_fig3_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 2.792724948871518 |
| `Material extraction (kt)` | measure | float64 |  | 0.3091431502774949 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.1952879528172671 |
| `Land use (km2)` | measure | float64 |  | 0.0291830990258455 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `hotspot_by_producing_country_and_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_country_iso3` | dimension | str |  | CHN |
| `producing_country_name` | dimension | str |  | China |
| `producing_world_region` | dimension | str |  | Asia and Pacific |
| `producing_sector_group` | dimension | str |  | Minerals and Metals |
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt |
| `value` | measure | float64 | varies by row | 1830.977869842679 |
| `analysis_year` | measure | int64 |  | 2016 |
| `model` | dimension | str |  | EXIOBASE v3.7 IOT_2016_ixi |

### `hotspot_by_producing_node.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `analysis` | dimension | str |  | B diag(L y): where impacts physically oc |
| `producing_country_iso3` | dimension | str |  | AUT |
| `producing_country_name` | dimension | str |  | Austria |
| `producing_world_region` | dimension | str |  | Europe |
| `producing_sector_code` | dimension | str |  | WHEA |
| `producing_sector_name` | dimension | str |  | Cultivation of wheat |
| `producing_sector_group` | dimension | str |  | Food and catering |
| `ghg_protocol_scope` | dimension | str |  | Indirect |
| `value` | measure | float64 | kt CO2eq | 0.0343294707231926 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2016 |
| `model` | dimension | str |  | EXIOBASE v3.7 IOT_2016_ixi |

### `hotspot_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt |
| `producing_sector_group` | dimension | str |  | Minerals and Metals |
| `value` | measure | float64 | varies by row | 7516.381700855577 |

### `hotspot_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt |
| `producing_world_region` | dimension | str |  | Asia and Pacific |
| `value` | measure | float64 | varies by row | 4087.8937197926407 |

### `hotspot_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 7.212704314585596 |
| `share_of_total_pct` | measure | float64 | % | 8.604485399338369 |

### `intensity_by_purchased_product.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `analysis` | dimension | str |  | impact per unit of node output, indexed  |
| `purchased_country_iso3` | dimension | str |  | AUT |
| `purchased_country_name` | dimension | str |  | Austria |
| `purchased_world_region` | dimension | str |  | Europe |
| `purchased_sector_code` | dimension | str |  | OCER |
| `purchased_sector_name` | dimension | str |  | Cultivation of cereal grains nec |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `Total (MEUR)` | measure | float64 | kt CO2eq per MEUR | 0.0003333246190005 |
| `value` | measure | float64 | kt CO2eq per MEUR | 0.7950716864875012 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per MEUR |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2016 |
| `model` | dimension | str |  | EXIOBASE v3.7 IOT_2016_ixi |

### `intensity_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per MEUR |
| `purchased_sector_group` | dimension | str |  | Steam, hot water supply and water distri |
| `value` | measure | float64 | varies by row | 22127090.985921074 |

### `intensity_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per MEUR |
| `purchased_world_region` | dimension | str |  | America |
| `value` | measure | float64 | varies by row | 22172749.88585013 |

### `scopes_summary.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Component` | dimension | str |  | Scope 1 direct (DRIVHUS, excl. medical N |
| `kt_CO2eq` | measure | float64 |  | 182.8387699118744 |

### `steenmeijer_table.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Category group` | dimension | str |  | Total |
| `Climate change (kt CO2eq)` | dimension | str |  | 8,241 (100·0%) |
| `Material extraction (kt)` | dimension | str |  | 7,651 (100·0%) |
| `Blue water consumption (Mm3)` | dimension | str |  | 84 (100·0%) |
| `Land use (km2)` | dimension | str |  | 5,278 (100·0%) |
| `Waste generation (kt)` | dimension | str |  | 368 (100·0%) |
| `Basic price expenditure (million euros)` | dimension | str |  | 33,430 (100·0%) |

### `table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Global warming (ktCO2eq)` | measure | float64 |  | 8240.973961518019 |
| `Material extraction (kt)` | measure | float64 |  | 7651.24505549232 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 83.82493524993615 |
| `Land use (km2)` | measure | float64 |  | 5277.712276670657 |
| `Waste generation (kt)` | measure | float64 |  | 368.4113226279323 |
| `Expenditure (MEUR)` | measure | float64 |  | 33429.843657658625 |

### `table_s05_dk.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Global warming (ktCO2eq) |
| `Healthcare footprint` | measure | float64 |  | 8240.973961518019 |
| `National consumption footprint` | measure | float64 |  | 79040.33438684596 |
| `Healthcare share of national consumption footprint (%)` | measure | float64 | % | 10.426289343848598 |
