# Gold result tables - schema and lineage

All tables are long-format CSV, one observation per row, with explicit units.
They are exported at the **most detailed level available**; every published
figure and aggregate is derived from these by grouping (never the reverse).

## Common columns

| column | meaning |
|---|---|
| `analysis_year` | year of the Danish expenditure data and of the MRIO background |
| `model` | MRIO release actually used (e.g. `EXIOBASE v3.10.2 IOT_2022_ixi (screened)`) |
| `scenario` | model scenario (`baseline`, scope variants, pharma-mapping variants) |
| `consuming_country_iso3` | always `DNK` - Denmark is the final consumer in this study |
| `demand_component` | `healthcare_services`, `pharmaceuticals`, `medical_appliances` |
| `indicator` | `climate_change`, `material_extraction`, `blue_water_consumption`, `land_use`, `waste_generation` |
| `unit` | `kt CO2eq`, `kt`, `Mm3`, `km2`, `kt`, or `M.EUR` for monetary rows |
| `value` | numeric value in `unit` |

## Country and region coding

`*_country_iso3` uses **ISO 3166-1 alpha-3** for the 44 EXIOBASE countries.
The five rest-of-world regions are **not countries** and keep their own codes
and names: `WA` RoW Asia and Pacific, `WL` RoW America, `WE` RoW Europe,
`WF` RoW Africa, `WM` RoW Middle East. `*_world_region` gives the continental
grouping (Europe, Asia and Pacific, America, Middle East, Africa, Denmark).

## The two perspectives (and why they reconcile)

Every impact cell is `E[i,j] = s_k(i) · L(i,j) · y_H(j)`:
pressure arising in node *i* caused by Danish healthcare final demand for
node *j*. Summing over *i* gives the **consumption / contribution**
perspective (`footprint_by_purchased_product.csv`); summing over *j* gives
the **production / hotspot** perspective (`footprint_by_producing_node.csv`).
Both are marginals of the same array, so they sum to the identical total -
verified to machine precision by `analysis.validate_io_identities` (tests
T5/T6). Allocating production emissions to final demand is additive and does
not double count (Wood et al. 2018); embodied-flow tables (E_Z) would.

## Tables

| file | grain | rows |
|---|---|---|
| `expenditure_summary.csv` | demand component | basic-price expenditure vs the y_H vector actually run through the model |
| `expenditure_vector_detail.csv` | demand component × supplying region × product | the final-demand vector y_H, M.EUR |
| `footprint_by_producing_node.csv` | indicator × demand component × **producing** region × producing sector | complete, unthresholded |
| `footprint_by_purchased_product.csv` | indicator × demand component × **purchased** product region × product | complete, unthresholded |
| `footprint_bilateral_producer_x_purchase.csv.gz` | indicator × demand component × producing node × purchased node | largest cells covering ≥99.5 % of each total, **plus an explicit `BELOW_THRESHOLD_REMAINDER` row** so every total reconciles exactly |
| `_bilateral_coverage.csv` | indicator × demand component | achieved coverage of the named cells |

## Important note on `healthcare_services`

Following Steenmeijer et al. (2022), the healthcare-services component enters
the model as the **scaled intermediate-input column** of the Danish
"Health and social work" industry: value added (wages, surplus) carries no
environmental pressure and is therefore not part of `y_H`. Consequently
`sum(y_H)` is smaller than total health expenditure; `expenditure_summary.csv`
reports both so the relationship is explicit. Pharmaceuticals and appliances
enter at their full basic-price value, distributed over supplying regions.

## Units

Monetary values are **million euro (M.EUR)** - EXIOBASE's native unit
(`unit.txt` of the release). No US-dollar values are used anywhere in this
model; dollar figures appearing in the comparative literature (Karliner et al.
2019, Lenzen et al. 2020, Pichler et al. 2019) are those studies' own units
and are labelled as such wherever they are quoted.
