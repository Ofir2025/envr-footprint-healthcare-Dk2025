# 01_eriksen_replication/2019_uncorrected - data dictionary

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
| `value` | measure | float64 | kt CO2eq | 0.0006161715498301 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2019 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi |

### `contribution_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `purchased_sector_group` | dimension | str |  | Transport |
| `value` | measure | float64 | varies by row | 2617.155232125088 |

### `contribution_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `purchased_world_region` | dimension | str |  | Denmark |
| `value` | measure | float64 | varies by row | 5576.658661409865 |

### `contribution_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 26.59756864354587 |
| `share_of_total_pct` | measure | float64 | % | 46.27256854254077 |

### `figure1_activity_contributions.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `contribution_group` | dimension | str |  | Pharmaceuticals and chemical products |
| `value` | measure | float64 | varies by row | 18.397371608682313 |
| `share_pct` | measure | float64 | % | 32.00644578360439 |

### `figure2_sector_contributions.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `hotspot_group` | dimension | str |  | Agricultural sector |
| `value` | measure | float64 | varies by row | 48.66995588756262 |
| `share_pct` | measure | float64 | % | 84.67254657564978 |

### `figure2b_top_origin_industry_pairs.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `producing_country_iso3` | dimension | str |  | DNK |
| `producing_world_region` | dimension | str |  | Denmark |
| `producing_sector_code` | dimension | str |  | POWB |
| `producing_sector_name` | dimension | str |  | Production of electricity by biomass and |
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `value` | measure | float64 | varies by row | 3.641371745948947 |
| `rank` | measure | int64 |  | 1 |
| `share_pct` | measure | float64 | % | 6.353060948850069 |
| `mrio_coverage_pct` | measure | float64 | % | 99.71572823812654 |

### `figure3_geographical_origin.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `producing_world_region` | dimension | str |  | Asia and Pacific |
| `value` | measure | float64 | varies by row | 27.654337826041075 |
| `share_pct` | measure | float64 | % | 48.11106081549977 |

### `full_results_tables_fig1_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 409.51635187052887 |
| `Material extraction (kt)` | measure | float64 |  | 112.6500772207951 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 17.531500999572476 |
| `Land use (km2)` | measure | float64 |  | 1337.8357982740483 |
| `Waste generation (kt)` | measure | float64 |  | 30.090593047992723 |

### `full_results_tables_fig1_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Contribution` | dimension | str |  | Food and food services |
| `Global warming (ktCO2eq)` | measure | float64 |  | 6.376247906743854 |
| `Material extraction (kt)` | measure | float64 |  | 3.6015492589816933 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 30.500065345378506 |
| `Land use (km2)` | measure | float64 |  | 38.05752282162843 |
| `Waste generation (kt)` | measure | float64 |  | 10.931970168177228 |

### `full_results_tables_fig2_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 462.3067147054534 |
| `Material extraction (kt)` | measure | float64 |  | 35.53841050932789 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 48.669955887562665 |
| `Land use (km2)` | measure | float64 |  | 3470.5865295134163 |
| `Waste generation (kt)` | measure | float64 |  | 44.048728035961986 |

### `full_results_tables_fig2_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Hotspot` | dimension | str |  | Agricultural sector |
| `Global warming (ktCO2eq)` | measure | float64 |  | 7.198203950708734 |
| `Material extraction (kt)` | measure | float64 |  | 1.1362028255372525 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 84.67254657564972 |
| `Land use (km2)` | measure | float64 |  | 98.72805483437712 |
| `Waste generation (kt)` | measure | float64 |  | 16.00298738104833 |

### `full_results_tables_fig3_absolute.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 254.39260567336655 |
| `Material extraction (kt)` | measure | float64 |  | 23.5848 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.1634 |
| `Land use (km2)` | measure | float64 |  | 1.5356999999999998 |
| `Waste generation (kt)` | measure | float64 |  | 0.0 |

### `full_results_tables_fig3_relative_pct.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Region` | dimension | str |  | Unallocated |
| `Global warming (ktCO2eq)` | measure | float64 |  | 3.9609415155386607 |
| `Material extraction (kt)` | measure | float64 |  | 0.7540324965489786 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 0.2842717618734632 |
| `Land use (km2)` | measure | float64 |  | 0.0436861817216844 |
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
| `value` | measure | float64 | varies by row | 1731.3161811606444 |
| `analysis_year` | measure | int64 |  | 2019 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi |

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
| `value` | measure | float64 | kt CO2eq | 0.051374742844364 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2019 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi |

### `hotspot_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | land_use |
| `unit` | dimension | str |  | km2 |
| `producing_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | varies by row | 3470.586529513414 |

### `hotspot_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `producing_world_region` | dimension | str |  | Denmark |
| `value` | measure | float64 | varies by row | 2980.6436993360853 |

### `hotspot_domestic_vs_imported.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | blue_water_consumption |
| `unit` | dimension | str |  | Mm3 |
| `origin` | dimension | str |  | domestic |
| `value` | measure | float64 | varies by row | 4.986885138000327 |
| `share_of_total_pct` | measure | float64 | % | 8.675830014932322 |

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
| `value` | measure | float64 | kt CO2eq per MEUR | 1.988668354794579 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq per MEUR |
| `component_type` | dimension | str |  | MRIO supply-chain node |
| `analysis_year` | measure | int64 |  | 2019 |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2016_ixi |

### `intensity_by_sector_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt per MEUR |
| `purchased_sector_group` | dimension | str |  | Minerals and Metals |
| `value` | measure | float64 | varies by row | 63140.65143823977 |

### `intensity_by_world_region.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `indicator` | dimension | str |  | material_extraction |
| `unit` | dimension | str |  | kt per MEUR |
| `purchased_world_region` | dimension | str |  | Europe |
| `value` | measure | float64 | varies by row | 61585.0075097025 |

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
| `Climate change (kt CO2eq)` | dimension | str |  | 6,423 (100·0%) |
| `Material extraction (kt)` | dimension | str |  | 3,128 (100·0%) |
| `Blue water consumption (Mm3)` | dimension | str |  | 57 (100·0%) |
| `Land use (km2)` | dimension | str |  | 3,515 (100·0%) |
| `Waste generation (kt)` | dimension | str |  | 275 (100·0%) |
| `Basic price expenditure (million euros)` | dimension | str |  | 35,271 (100·0%) |

### `table_01.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Total |
| `Global warming (ktCO2eq)` | measure | float64 |  | 6422.528701203737 |
| `Material extraction (kt)` | measure | float64 |  | 3127.822754051277 |
| `Blue water consumption (Mm3)` | measure | float64 |  | 57.48020799643617 |
| `Land use (km2)` | measure | float64 |  | 3515.29920784478 |
| `Waste generation (kt)` | measure | float64 |  | 275.253157345653 |
| `Expenditure (MEUR)` | measure | float64 |  | 35271.231705222825 |

### `table_s05_dk.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `Unnamed: 0` | dimension | str |  | Global warming (ktCO2eq) |
| `Healthcare footprint` | measure | float64 |  | 6422.528701203737 |
| `National consumption footprint` | measure | float64 |  | 86614.13373867093 |
| `Healthcare share of national consumption footprint (%)` | measure | float64 | % | 7.415104699403403 |
