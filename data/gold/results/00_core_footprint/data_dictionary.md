# 00_core_footprint - data dictionary

One row per column of every table in this folder. Units are the
table's own; `varies by row` means the table carries a `unit`
column and the value is read from there.

## Common columns

Every gold table shares this vocabulary; columns particular to one table
are described below, per table.

| Column | Meaning |
|:---|:---|
| `analysis_year` | year of the Danish expenditure data and of the MRIO background |
| `model` | MRIO release actually used (e.g. `EXIOBASE v3.10.2 IOT_2022_ixi (screened)`) |
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

Every impact cell is `E[i,j] = s_k(i) . L(i,j) . y_H(j)`: pressure arising
in node *i* caused by Danish healthcare final demand for node *j*. Summing
over *i* gives the **consumption / contribution** perspective (by
purchased product); summing over *j* gives the **production / hotspot**
perspective (by producing node). Both are marginals of the same array, so
they sum to the identical total - verified to machine precision by
`analysis.validate_io_identities` (tests T5/T6). Allocating production
emissions to final demand is additive and does not double count (Wood et
al. 2018); embodied-flow tables (E_Z) would.

## Units

Monetary values are **million euro (M.EUR)** - EXIOBASE's native unit
(`unit.txt` of the release). No US-dollar values are used anywhere in this
model; dollar figures appearing in the comparative literature (Karliner et
al. 2019, Lenzen et al. 2020, Pichler et al. 2019) are those studies' own
units and are labelled as such wherever they are quoted.

## Important note on `healthcare_services`

Following Steenmeijer et al. (2022), the healthcare-services component enters
the model as the **scaled intermediate-input column** of the Danish
"Health and social work" industry: value added (wages, surplus) carries no
environmental pressure and is therefore not part of `y_H`. Consequently
`sum(y_H)` is smaller than total health expenditure; `expenditure_summary.csv`
reports both so the relationship is explicit. Pharmaceuticals and appliances
enter at their full basic-price value, distributed over supplying regions.

## Tables

### `expenditure_summary.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `scenario` | dimension | str |  | baseline |
| `analysis_year` | measure | int64 |  | 2022 |
| `demand_component` | dimension | str |  | healthcare_services |
| `basic_price_expenditure_meur` | measure | float64 | M.EUR | 37552.28493467391 |
| `y_H_meur` | measure | float64 | M.EUR | 10022.046976724128 |
| `unit` | dimension | str |  | M.EUR |

### `expenditure_vector_detail.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `scenario` | dimension | str |  | baseline |
| `analysis_year` | measure | int64 |  | 2022 |
| `demand_component` | dimension | str |  | healthcare_services |
| `purchased_country_iso3` | dimension | str |  | AUT |
| `purchased_country_name` | dimension | str |  | Austria |
| `purchased_world_region` | dimension | str |  | Europe |
| `purchased_sector_code` | dimension | str |  | WHEA |
| `purchased_sector_name` | dimension | str |  | Cultivation of wheat |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | M.EUR | 0.000491428770022 |
| `unit` | dimension | str |  | M.EUR |
| `note` | dimension | str |  | healthcare_services enters as the scaled |

### `extended_indicators_by_producing_node.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `scenario` | dimension | str |  | baseline |
| `analysis_year` | measure | int64 |  | 2022 |
| `indicator` | dimension | str |  | pm2_5 |
| `unit` | dimension | str |  | kt |
| `demand_component` | dimension | str |  | healthcare_services |
| `producing_country_iso3` | dimension | str |  | AUT |
| `producing_country_name` | dimension | str |  | Austria |
| `producing_world_region` | dimension | str |  | Europe |
| `producing_sector_code` | dimension | str |  | WHEA |
| `producing_sector_name` | dimension | str |  | Cultivation of wheat |
| `producing_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | kt | 1.1451961815713651e-05 |

### `extended_indicators_summary.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `scenario` | dimension | str |  | baseline |
| `analysis_year` | measure | int64 |  | 2022 |
| `indicator` | dimension | str |  | pm2_5 |
| `unit` | dimension | str |  | kt |
| `demand_component` | dimension | str |  | healthcare_services |
| `n_stressor_rows` | measure | int64 |  | 48 |
| `value` | measure | float64 | kt | 1.2820478567488611 |

### `footprint_bilateral_producer_x_purchase.csv.gz`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `scenario` | dimension | str |  | baseline |
| `analysis_year` | measure | int64 |  | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `demand_component` | dimension | str |  | healthcare_services |
| `producing_country_iso3` | dimension | str |  | DNK |
| `producing_country_name` | dimension | str |  | Denmark |
| `producing_world_region` | dimension | str |  | Denmark |
| `producing_sector_code` | dimension | str |  | POWT |
| `producing_sector_name` | dimension | str |  | Transmission of electricity |
| `producing_sector_group` | dimension | str |  | Electricity |
| `purchased_country_iso3` | dimension | str |  | DNK |
| `purchased_country_name` | dimension | str |  | Denmark |
| `purchased_world_region` | dimension | str |  | Denmark |
| `purchased_sector_code` | dimension | str |  | POWT |
| `purchased_sector_name` | dimension | str |  | Transmission of electricity |
| `purchased_sector_group` | dimension | str |  | Electricity |
| `value` | measure | float64 | kt CO2eq | 54.31864188434562 |

### `footprint_by_producing_node.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `scenario` | dimension | str |  | baseline |
| `analysis_year` | measure | int64 |  | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `demand_component` | dimension | str |  | healthcare_services |
| `producing_country_iso3` | dimension | str |  | AUT |
| `producing_country_name` | dimension | str |  | Austria |
| `producing_world_region` | dimension | str |  | Europe |
| `producing_sector_code` | dimension | str |  | WHEA |
| `producing_sector_name` | dimension | str |  | Cultivation of wheat |
| `producing_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | kt CO2eq | 0.0591484115147743 |

### `footprint_by_purchased_product.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `scenario` | dimension | str |  | baseline |
| `analysis_year` | measure | int64 |  | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `demand_component` | dimension | str |  | healthcare_services |
| `purchased_country_iso3` | dimension | str |  | AUT |
| `purchased_country_name` | dimension | str |  | Austria |
| `purchased_world_region` | dimension | str |  | Europe |
| `purchased_sector_code` | dimension | str |  | WHEA |
| `purchased_sector_name` | dimension | str |  | Cultivation of wheat |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | kt CO2eq | 0.00089628418447 |

### `national_footprint_by_producing_node.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `scope` | dimension | str |  | ALL Danish final demand (163 products x  |
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `analysis_year` | measure | int64 |  | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `producing_country_iso3` | dimension | str |  | AUT |
| `producing_country_name` | dimension | str |  | Austria |
| `producing_world_region` | dimension | str |  | Europe |
| `producing_sector_code` | dimension | str |  | WHEA |
| `producing_sector_name` | dimension | str |  | Cultivation of wheat |
| `producing_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | kt CO2eq | 1.4657021219399546 |

### `national_footprint_by_purchased_product.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `scope` | dimension | str |  | ALL Danish final demand (163 products x  |
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `analysis_year` | measure | int64 |  | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `purchased_country_iso3` | dimension | str |  | AUT |
| `purchased_country_name` | dimension | str |  | Austria |
| `purchased_world_region` | dimension | str |  | Europe |
| `purchased_sector_code` | dimension | str |  | WHEA |
| `purchased_sector_name` | dimension | str |  | Cultivation of wheat |
| `purchased_sector_group` | dimension | str |  | Food and catering |
| `value` | measure | float64 | kt CO2eq | 0.1269444699860208 |

### `national_totals_summary.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `scope` | dimension | str |  | ALL Danish final demand (163 products x  |
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `analysis_year` | measure | int64 |  | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `national_footprint` | measure | float64 | varies by row | 77477.50333386465 |
| `national_supply_chain` | measure | float64 | varies by row | 67755.50852916535 |
| `national_direct_households` | measure | float64 | varies by row | 9721.994804699298 |
| `healthcare_footprint_mrio` | measure | float64 | varies by row | 3943.3970167956713 |
| `healthcare_share_pct` | measure | float64 | % | 5.089731660302548 |

### `national_vs_healthcare_by_product_group.csv`

| Column | Role | Type | Unit | Example |
|:---|:---|:---|:---|:---|
| `scope` | dimension | str |  | ALL Danish final demand (163 products x  |
| `consuming_country_iso3` | dimension | str |  | DNK |
| `model` | dimension | str |  | EXIOBASE v3.8.2 IOT_2022_ixi with Danish |
| `analysis_year` | measure | int64 |  | 2022 |
| `indicator` | dimension | str |  | climate_change |
| `unit` | dimension | str |  | kt CO2eq |
| `sector_code` | dimension | str |  | ALUM |
| `sector_name` | dimension | str |  | Aluminium production |
| `sector_group` | dimension | str |  | Metal Products |
| `national` | measure | float64 | varies by row | 7.953724723473594 |
| `healthcare` | measure | float64 | varies by row | 0.7812067574513278 |
| `healthcare_vs_sector_ratio_pct` | measure | float64 | % | 9.821898350916964 |
| `sector_share_of_national_pct` | measure | float64 | % | 0.0117388606419357 |
