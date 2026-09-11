# 01_eriksen_replication/2022d - data dictionary

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
| `value` | measure | float64 | kt CO2eq | 0.0011801085523185 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2022 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |

### `contribution_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt |
| `purchased_sector_group` | dimension | str |  | Chemical |
| `value` | measure | float64 | varies by row | 2564.1699648125737 |

### `contribution_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt |
| `purchased_world_region` | dimension | str |  | Denmark |
| `value` | measure | float64 | varies by row | 4755.1708446096445 |

### `contribution_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 37.21573968435915 |
| `share_of_total_pct` | measure | float64 | % | 30.651081968131308 |

### `figure1_activity_contributions.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `contribution_group` | dimension | str |  | Pharmaceuticals and chemical products |
| `value` | measure | float64 | varies by row | 60.6745061002787 |
| `share_pct` | measure | float64 | % | 49.97184727829363 |

### `figure2_sector_contributions.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `hotspot_group` | dimension | str |  | Agricultural sector |
| `value` | measure | float64 | varies by row | 100.60876480839632 |
| `share_pct` | measure | float64 | % | 82.86191603362468 |

### `figure2b_top_origin_industry_pairs.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_country_iso3` | dimension | str |  | RoW Middle East |
| `producing_world_region` | dimension | str |  | Middle East |
| `producing_sector_code` | dimension | str |  | WHEA |
| `producing_sector_name` | dimension | str |  | Cultivation of wheat |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `value` | measure | float64 | varies by row | 10.37514285494007 |
| `rank` | measure | int64 |  | 1 |
| `share_pct` | measure | float64 | % | 8.557081610562188 |
| `mrio_coverage_pct` | measure | float64 | % | 99.85908112617868 |

### `figure3_geographical_origin.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `producing_world_region` | dimension | str |  | Asia and Pacific |
| `value` | measure | float64 | varies by row | 52.34270097614444 |
| `share_pct` | measure | float64 | % | 43.10972807904349 |

### `full_results_tables_fig1_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 636.1444033167465 |
| `Material extraction (kt)` | measure | float64 |  | 348.41001672986425 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 26.338009328964755 |
| `Land use (km2)` | measure | float64 |  | 2108.0886835003016 |
| `Waste generation (kt)` | measure | float64 |  | 47.81430980923125 |

### `full_results_tables_fig1_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 9.828771534331898 |
| `Material extraction (kt)` | measure | float64 |  | 4.902334307535595 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 21.692125150982537 |
| `Land use (km2)` | measure | float64 |  | 29.421300525256537 |
| `Waste generation (kt)` | measure | float64 |  | 13.44391880169576 |

### `full_results_tables_fig2_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 785.4494373212056 |
| `Material extraction (kt)` | measure | float64 |  | 62.13690939078576 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 100.60876480839632 |
| `Land use (km2)` | measure | float64 |  | 7050.261449720517 |
| `Waste generation (kt)` | measure | float64 |  | 61.96729000445083 |

### `full_results_tables_fig2_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 12.135614226815353 |
| `Material extraction (kt)` | measure | float64 |  | 0.8743029420616794 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 82.86191603362462 |
| `Land use (km2)` | measure | float64 |  | 98.39617399275733 |
| `Waste generation (kt)` | measure | float64 |  | 17.423303159760977 |

### `full_results_tables_fig3_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 245.7291104137513 |
| `Material extraction (kt)` | measure | float64 |  | 24.6714 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.1711 |
| `Land use (km2)` | measure | float64 |  | 1.6064 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `full_results_tables_fig3_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 3.796646285024074 |
| `Material extraction (kt)` | measure | float64 |  | 0.3471411406885835 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.140918873821319 |
| `Land use (km2)` | measure | float64 |  | 0.0224195393361236 |
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
| `value` | measure | float64 | varies by row | 2351.092658226701 |
| `analysis_year` | measure | int64 |  | 2022 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |

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
| `value` | measure | float64 | kt CO2eq | 0.0915889157011375 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2022 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |

### `hotspot_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | land_use |
| `unit` | dimension | str |  | km2 |
| `producing_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | varies by row | 7050.261449720518 |

### `hotspot_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt |
| `producing_world_region` | dimension | str |  | Denmark |
| `value` | measure | float64 | varies by row | 2919.604680489351 |

### `hotspot_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 6.268902809256876 |
| `share_of_total_pct` | measure | float64 | % | 5.163101835042563 |

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
| `Total (MEUR)` | measure | float64 | kt CO2eq per MEUR | 0.0006106738836626 |
| `value` | measure | float64 | kt CO2eq per MEUR | 1.932469332470099 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per MEUR |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2022 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |

### `intensity_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt per MEUR |
| `purchased_sector_group` | dimension | str |  | Minerals and Metals |
| `value` | measure | float64 | varies by row | 16414.051511438844 |

### `intensity_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per MEUR |
| `purchased_world_region` | dimension | str |  | Europe |
| `value` | measure | float64 | varies by row | 22775.302675866067 |

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
| `Climate change (kt CO2eq)` | dimension | str |  | 6,472 (100·0%) |
| `Material extraction (kt)` | dimension | str |  | 7,107 (100·0%) |
| `Blue water consumption (Mm3)` | dimension | str |  | 121 (100·0%) |
| `Land use (km2)` | dimension | str |  | 7,165 (100·0%) |
| `Waste generation (kt)` | dimension | str |  | 356 (100·0%) |
| `Basic price expenditure (million euros)` | dimension | str |  | 49,709 (100·0%) |

### `table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Global warming (ktCO2eq)` | measure | float64 |  | 6472.267679584303 |
| `Material extraction (kt)` | measure | float64 |  | 7107.022795126533 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 121.41737679294113 |
| `Land use (km2)` | measure | float64 |  | 7165.178445088191 |
| `Waste generation (kt)` | measure | float64 |  | 355.6575319630764 |
| `Expenditure (MEUR)` | measure | float64 |  | 49709.03368460669 |

### `table_s05_dk.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Global warming (ktCO2eq) |
| `Healthcare footprint` | measure | float64 |  | 6472.267679584303 |
| `National consumption footprint` | measure | float64 |  | 95112.19776732936 |
| `Healthcare share of national consumption footprint (%)` | measure | float64 | % | 6.804876589454121 |
