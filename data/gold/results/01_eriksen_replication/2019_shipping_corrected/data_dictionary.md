# 01_eriksen_replication/2019_shipping_corrected - data dictionary

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
| `value` | measure | float64 | kt CO2eq | 0.0006394984976105 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2019 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi with Danish |

### `contribution_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | land_use |
| `unit` | dimension | str |  | km2 |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | varies by row | 1336.721901592973 |

### `contribution_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `purchased_world_region` | dimension | str |  | Denmark |
| `value` | measure | float64 | varies by row | 3225.893707742161 |

### `contribution_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 24.015188957550347 |
| `share_of_total_pct` | measure | float64 | % | 43.74560781310852 |

### `figure1_activity_contributions.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `contribution_group` | dimension | str |  | Pharmaceuticals and chemical products |
| `value` | measure | float64 | varies by row | 18.30306161769645 |
| `share_pct` | measure | float64 | % | 33.34050615725752 |

### `figure2_sector_contributions.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `hotspot_group` | dimension | str |  | Agricultural sector |
| `value` | measure | float64 | varies by row | 46.576904479384766 |
| `share_pct` | measure | float64 | % | 84.84359628006125 |

### `figure2b_top_origin_industry_pairs.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_country_iso3` | dimension | str |  | RoW Middle East |
| `producing_world_region` | dimension | str |  | Middle East |
| `producing_sector_code` | dimension | str |  | WHEA |
| `producing_sector_name` | dimension | str |  | Cultivation of wheat |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `value` | measure | float64 | varies by row | 3.509656603170472 |
| `rank` | measure | int64 |  | 1 |
| `share_pct` | measure | float64 | % | 6.412091738036203 |
| `mrio_coverage_pct` | measure | float64 | % | 99.7041752733486 |

### `figure3_geographical_origin.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `producing_world_region` | dimension | str |  | Asia and Pacific |
| `value` | measure | float64 | varies by row | 25.9725254597163 |
| `share_pct` | measure | float64 | % | 47.311054461618646 |

### `full_results_tables_fig1_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 389.6491233215574 |
| `Material extraction (kt)` | measure | float64 |  | 112.13991348115322 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 17.515657573473547 |
| `Land use (km2)` | measure | float64 |  | 1336.7219015929725 |
| `Waste generation (kt)` | measure | float64 |  | 30.029339780231233 |

### `full_results_tables_fig1_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 9.609643094427158 |
| `Material extraction (kt)` | measure | float64 |  | 3.683317476569776 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 31.906186045518293 |
| `Land use (km2)` | measure | float64 |  | 40.09641281171175 |
| `Waste generation (kt)` | measure | float64 |  | 11.32023451083016 |

### `full_results_tables_fig2_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 439.06283772219297 |
| `Material extraction (kt)` | measure | float64 |  | 34.668922192009006 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 46.57690447938482 |
| `Land use (km2)` | measure | float64 |  | 3291.3343890550173 |
| `Waste generation (kt)` | measure | float64 |  | 42.59494502873047 |

### `full_results_tables_fig2_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 10.828298882260658 |
| `Material extraction (kt)` | measure | float64 |  | 1.1387261059830036 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 84.84359628006119 |
| `Land use (km2)` | measure | float64 |  | 98.72711908712164 |
| `Waste generation (kt)` | measure | float64 |  | 16.057121809204006 |

### `full_results_tables_fig3_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 252.90240567336656 |
| `Material extraction (kt)` | measure | float64 |  | 23.4337 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.1624 |
| `Land use (km2)` | measure | float64 |  | 1.5258 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `full_results_tables_fig3_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 6.2371546881101985 |
| `Material extraction (kt)` | measure | float64 |  | 0.7696970157302598 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.2958247266513905 |
| `Land use (km2)` | measure | float64 |  | 0.0457680139714944 |
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
| `value` | measure | float64 | varies by row | 1719.7423123700771 |
| `analysis_year` | measure | int64 |  | 2019 |
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
| `value` | measure | float64 | kt CO2eq | 0.0528417562632345 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2019 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi with Danish |

### `hotspot_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | land_use |
| `unit` | dimension | str |  | km2 |
| `producing_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | varies by row | 3291.3343890550173 |

### `hotspot_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt |
| `producing_world_region` | dimension | str |  | Denmark |
| `value` | measure | float64 | varies by row | 1832.063024073563 |

### `hotspot_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 4.799982058129505 |
| `share_of_total_pct` | measure | float64 | % | 8.743555297276721 |

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
| `Total (MEUR)` | measure | float64 | kt CO2eq per MEUR | 0.0003098412806462 |
| `value` | measure | float64 | kt CO2eq per MEUR | 2.063955120108059 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per MEUR |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2019 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi with Danish |

### `intensity_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt per MEUR |
| `purchased_sector_group` | dimension | str |  | Minerals and Metals |
| `value` | measure | float64 | varies by row | 63140.64411145227 |

### `intensity_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt per MEUR |
| `purchased_world_region` | dimension | str |  | Europe |
| `value` | measure | float64 | varies by row | 61584.96227058688 |

### `scopes_summary.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Component` | dimension | str |  | Scope 1 direct (DRIVHUS, excl. medical N |
| `kt_CO2eq` | measure | float64 |  | 150.92464394929328 |

### `steenmeijer_table.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Category group` | dimension | str |  | Total |
| `Climate change (kt CO2eq)` | dimension | str |  | 4,055 (100·0%) |
| `Material extraction (kt)` | dimension | str |  | 3,045 (100·0%) |
| `Blue water consumption (Mm3)` | dimension | str |  | 55 (100·0%) |
| `Land use (km2)` | dimension | str |  | 3,334 (100·0%) |
| `Waste generation (kt)` | dimension | str |  | 265 (100·0%) |
| `Basic price expenditure (million euros)` | dimension | str |  | 35,271 (100·0%) |

### `table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Global warming (ktCO2eq)` | measure | float64 |  | 4054.7720606556422 |
| `Material extraction (kt)` | measure | float64 |  | 3044.5356446870273 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 54.89737177763963 |
| `Land use (km2)` | measure | float64 |  | 3333.7693021818964 |
| `Waste generation (kt)` | measure | float64 |  | 265.2713576869985 |
| `Expenditure (MEUR)` | measure | float64 |  | 35271.231705222825 |

### `table_s05_dk.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Global warming (ktCO2eq) |
| `Healthcare footprint` | measure | float64 |  | 4054.7720606556422 |
| `National consumption footprint` | measure | float64 |  | 73591.42856519141 |
| `Healthcare share of national consumption footprint (%)` | measure | float64 | % | 5.50984284408027 |
