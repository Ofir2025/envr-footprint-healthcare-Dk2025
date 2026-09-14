# 01_eriksen_replication/2016c - data dictionary

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
| `purchased_sector_code` | dimension | str |  | WHEA |
| `purchased_sector_name` | dimension | str |  | Cultivation of wheat |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `ghg_protocol_scope` | dimension | str |  | Scope 3 |
| `value` | measure | float64 | kt CO2eq | 0.0005849431175352 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2016 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi with Danish |

### `contribution_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | land_use |
| `unit` | dimension | str |  | km2 |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | varies by row | 1269.0531695061943 |

### `contribution_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `purchased_world_region` | dimension | str |  | Denmark |
| `value` | measure | float64 | varies by row | 3110.8826095850363 |

### `contribution_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 20.253891717614152 |
| `share_of_total_pct` | measure | float64 | % | 44.9208040784777 |

### `figure1_activity_contributions.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `contribution_group` | dimension | str |  | Food and food services |
| `value` | measure | float64 | varies by row | 16.628964284278005 |
| `share_pct` | measure | float64 | % | 36.88113163913221 |

### `figure2_sector_contributions.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `hotspot_group` | dimension | str |  | Agricultural sector |
| `value` | measure | float64 | varies by row | 38.11681088277874 |
| `share_pct` | measure | float64 | % | 84.53870582672344 |

### `figure2b_top_origin_industry_pairs.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_country_iso3` | dimension | str |  | DNK |
| `producing_world_region` | dimension | str |  | Denmark |
| `producing_sector_code` | dimension | str |  | POWB |
| `producing_sector_name` | dimension | str |  | Production of electricity by biomass and |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `value` | measure | float64 | varies by row | 3.091477544695438 |
| `rank` | measure | int64 |  | 1 |
| `share_pct` | measure | float64 | % | 6.888357750948541 |
| `mrio_coverage_pct` | measure | float64 | % | 99.53812131838195 |

### `figure3_geographical_origin.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `producing_world_region` | dimension | str |  | Asia and Pacific |
| `value` | measure | float64 | varies by row | 21.967931159754908 |
| `share_pct` | measure | float64 | % | 48.72234656901193 |

### `full_results_tables_fig1_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 375.3300907654283 |
| `Material extraction (kt)` | measure | float64 |  | 106.46306644771464 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 16.628964284278045 |
| `Land use (km2)` | measure | float64 |  | 1269.0531695061943 |
| `Waste generation (kt)` | measure | float64 |  | 28.509167674193563 |

### `full_results_tables_fig1_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 9.853299852772771 |
| `Material extraction (kt)` | measure | float64 |  | 4.379988878186352 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 36.881131639132185 |
| `Land use (km2)` | measure | float64 |  | 44.38925844802454 |
| `Waste generation (kt)` | measure | float64 |  | 12.561853038445408 |

### `full_results_tables_fig2_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 392.2069390800654 |
| `Material extraction (kt)` | measure | float64 |  | 30.69024512000503 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 38.11681088277877 |
| `Land use (km2)` | measure | float64 |  | 2821.983065022806 |
| `Waste generation (kt)` | measure | float64 |  | 37.665988063302024 |

### `full_results_tables_fig2_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 10.296356914024528 |
| `Material extraction (kt)` | measure | float64 |  | 1.2626250283749962 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 84.53870582672334 |
| `Land use (km2)` | measure | float64 |  | 98.70802785827196 |
| `Waste generation (kt)` | measure | float64 |  | 16.59657735386422 |

### `full_results_tables_fig3_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 273.9895816124288 |
| `Material extraction (kt)` | measure | float64 |  | 30.11717534552141 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.2082518555950769 |
| `Land use (km2)` | measure | float64 |  | 1.961211745817756 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `full_results_tables_fig3_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 7.192872542293086 |
| `Material extraction (kt)` | measure | float64 |  | 1.2390484085911235 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.4618786816180258 |
| `Land use (km2)` | measure | float64 |  | 0.0685997538545061 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `hotspot_by_producing_country_and_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_country_iso3` | dimension | str |  | DNK |
| `producing_country_name` | dimension | str |  | Denmark |
| `producing_world_region` | dimension | str |  | Denmark |
| `producing_sector_group` | dimension | str |  | Minerals and Metals |
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt |
| `value` | measure | float64 | varies by row | 1351.6056612350735 |
| `analysis_year` | measure | int64 |  | 2016 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi with Danish |

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
| `value` | measure | float64 | kt CO2eq | 0.0448138889894308 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2016 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi with Danish |

### `hotspot_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | land_use |
| `unit` | dimension | str |  | km2 |
| `producing_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | varies by row | 2821.983065022806 |

### `hotspot_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `producing_world_region` | dimension | str |  | Denmark |
| `value` | measure | float64 | varies by row | 1575.9911869194596 |

### `hotspot_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 4.2852243858170045 |
| `share_of_total_pct` | measure | float64 | % | 9.504135192951257 |

### `intensity_by_purchased_product.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `country_consuming` | dimension | str |  | DNK |
| `sector_consuming` | dimension | str |  | health_and_eldercare |
| `analysis` | dimension | str |  | impact per unit of node output, indexed  |
| `purchased_country_iso3` | dimension | str |  | AUT |
| `purchased_country_name` | dimension | str |  | Austria |
| `purchased_world_region` | dimension | str |  | Europe |
| `purchased_sector_code` | dimension | str |  | WHEA |
| `purchased_sector_name` | dimension | str |  | Cultivation of wheat |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `Total (MEUR)` | measure | float64 | kt CO2eq per MEUR | 0.0002941562181178 |
| `value` | measure | float64 | kt CO2eq per MEUR | 1.98854581853791 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per MEUR |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2016 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi with Danish |

### `intensity_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt per MEUR |
| `purchased_sector_group` | dimension | str |  | Minerals and Metals |
| `value` | measure | float64 | varies by row | 93.60358364120675 |
| `expenditure_meur` | measure | float64 | varies by row | 7.4228878381629 |
| `footprint` | measure | float64 | varies by row | 694.8089026187774 |

### `intensity_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | land_use |
| `unit` | dimension | str |  | km2 per MEUR |
| `purchased_world_region` | dimension | str |  | Africa |
| `value` | measure | float64 | varies by row | 4.359753157620143 |
| `expenditure_meur` | measure | float64 | varies by row | 51.45095822293768 |
| `footprint` | measure | float64 | varies by row | 224.3134775750346 |

### `scopes_summary.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Component` | dimension | str |  | Scope 1 direct (DRIVHUS, excl. medical N |
| `kt_CO2eq` | measure | float64 |  | 172.53211635709056 |

### `steenmeijer_table.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Category group` | dimension | str |  | Total |
| `Climate change (kt CO2eq)` | dimension | str |  | 3,809 (100·0%) |
| `Material extraction (kt)` | dimension | str |  | 2,431 (100·0%) |
| `Blue water consumption (Mm3)` | dimension | str |  | 45 (100·0%) |
| `Land use (km2)` | dimension | str |  | 2,859 (100·0%) |
| `Waste generation (kt)` | dimension | str |  | 227 (100·0%) |
| `Basic price expenditure (million euros)` | dimension | str |  | 33,430 (100·0%) |

### `table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Global warming (ktCO2eq)` | measure | float64 |  | 3809.1816586684663 |
| `Material extraction (kt)` | measure | float64 |  | 2430.66978954976 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 45.08799905324501 |
| `Land use (km2)` | measure | float64 |  | 2858.919508628714 |
| `Waste generation (kt)` | measure | float64 |  | 226.9503359650974 |
| `Expenditure (MEUR)` | measure | float64 |  | 33429.843657658625 |

### `table_s05_dk.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Global warming (ktCO2eq) |
| `Healthcare footprint` | measure | float64 |  | 3809.1816586684663 |
| `National consumption footprint` | measure | float64 |  | 74432.54477363416 |
| `Healthcare share of national consumption footprint (%)` | measure | float64 | % | 5.117629217505637 |
