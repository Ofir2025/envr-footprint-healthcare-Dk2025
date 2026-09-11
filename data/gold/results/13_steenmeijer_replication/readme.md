# 13_steenmeijer_replication

**Steenmeijer replication**

This layer places Denmark beside every number the Dutch study published, in their own table structure, for every impact category, not only climate. That completeness is what FAIR replication means here.

Method, equations, and verification: [`docs/methods/replications.md`, section 13](../../../../docs/methods/replications.md#r13).

## Where the Dutch numbers come from

Every `nl_*.csv` here is a conversion of the authors' own published
output, not a re-run of their model. The source of record is the RIVM
repository <https://github.com/rivm-syso/envr-footprint-healthcare>,
kept verbatim at `archive/rivm_steenmeijer_2022/`; each row carries
the workbook, the sheet and that URL in its own `source` column.
`analysis.steenmeijer_replication.convert_rivm_outputs` regenerates
them and asserts every column total back against the workbook it came
from.

The archive does not reproduce the article's own tables exactly: their
script reads Statistics Netherlands at run time, so the direct
emissions and the expenditure move with the vintage of the query. The
differences, and two inconsistencies internal to the archive, are
tabulated in the methods section linked above.

## Figures

Figures live in `figures/`, never in the data layer. These six render
the article's figures 1, 2 and 3 for both countries in one style, so
the two can be set side by side:

| Figure | Caption |
|:---|:---|
| [`steenmeijer_fig1_contribution_nl.tiff`](../../../../figures/steenmeijer_replication/steenmeijer_fig1_contribution_nl.tiff) | Contribution analysis of the Dutch health-care impact footprints by product group, 2016. Scopes follow the Greenhouse Gas Protocol. Rendered from the archived RIVM outputs in the groups, legend order and palette of Steenmeijer et al. (2022) figure 1. |
| [`steenmeijer_fig1_contribution_dk.tiff`](../../../../figures/steenmeijer_replication/steenmeijer_fig1_contribution_dk.tiff) | The same figure for Denmark, 2022, shipping-corrected. This study's own `Transport` and `Unallocated` groups are folded into the Dutch *other* so the two legends are identical. |
| [`steenmeijer_fig2_hotspot_sector_nl.tiff`](../../../../figures/steenmeijer_replication/steenmeijer_fig2_hotspot_sector_nl.tiff) | Sector hotspot analysis of the Dutch health-care impact footprints, 2016: where the pressure physically arises. The indirect impact of private travel is distributed proportionally among all groups, as in the original. |
| [`steenmeijer_fig2_hotspot_sector_dk.tiff`](../../../../figures/steenmeijer_replication/steenmeijer_fig2_hotspot_sector_dk.tiff) | The same figure for Denmark, 2022, shipping-corrected. |
| [`steenmeijer_fig3_hotspot_region_nl.tiff`](../../../../figures/steenmeijer_replication/steenmeijer_fig3_hotspot_region_nl.tiff) | Geographical hotspot analysis of the Dutch health-care impact footprints, 2016, in the six world regions of the DESIRE concordance. The indirect impact of private travel is distributed proportionally among all regions, as in the original. |
| [`steenmeijer_fig3_hotspot_region_dk.tiff`](../../../../figures/steenmeijer_replication/steenmeijer_fig3_hotspot_region_dk.tiff) | The same figure for Denmark, 2022, shipping-corrected, with Denmark in the home-country slot the Netherlands occupies above. |

All six are produced by `r/plot_steenmeijer_replication.r` from the
tables in this folder and in `01_eriksen_replication/`. None carries a
title or a caption on the image: the captions are the table above.

## Conventions

| Item | Convention |
|:---|:---|
| Schema | star schema: dimension columns, then measure and unit |
| Industry / product codes | EXIOBASE codes **without** the `A_` / `C_` prefix |
| Countries | ISO3 (`DNK`, `DEU`, `ROU`) |
| Regions without an ISO3 code | region name (`RoW Europe`, `RoW Africa`, ...) |
| Monetary unit | M.EUR, EXIOBASE basic prices, unless a column says otherwise |
| Provenance | one row per file in `../manifest_lineage.csv` |

## Tables

### `national_shares_dk_vs_nl.csv`

- **Rows:** 5
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `indicator`, `unit`, `comparability_note`, `source_netherlands`, `source_denmark`
- **Measures:** `netherlands_national`, `netherlands_health_share_pct`, `denmark_national`, `denmark_health_share_pct`, `share_difference_pp`

### `nl_contribution_by_purchased_node.csv`

- **Rows:** 39,960
- **Format:** csv
- **Resolution:** 1+ regions x 163+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `purchased_country_iso3`, `purchased_country_name`, `purchased_world_region`, `purchased_sector_code`, `purchased_sector_name`, `purchased_sector_group`, `component_type`, `ghg_protocol_scope`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_contribution_by_purchased_product.csv`

- **Rows:** 840
- **Format:** csv
- **Resolution:** 1+ regions x 168+ industries (sampled)
- **Units:** Mm3, kt, kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `purchased_sector_code`, `component_type`, `purchased_sector_name`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_contribution_by_sector_group.csv`

- **Rows:** 105
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `purchased_sector_group`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_expenditure_by_purchased_node.csv`

- **Rows:** 31,948
- **Format:** csv
- **Resolution:** 1+ regions x 163+ industries (sampled)
- **Units:** M.EUR
- **Dimensions:** `study`, `consuming_country_iso3`, `purchased_country_iso3`, `purchased_country_name`, `purchased_world_region`, `purchased_sector_code`, `purchased_sector_name`, `purchased_sector_group`, `component_type`, `demand_component`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_expenditure_by_purchased_product.csv`

- **Rows:** 652
- **Format:** csv
- **Resolution:** 1+ regions x 163+ industries (sampled)
- **Units:** M.EUR
- **Dimensions:** `study`, `consuming_country_iso3`, `purchased_sector_code`, `component_type`, `purchased_sector_name`, `demand_component`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_expenditure_by_sector_group.csv`

- **Rows:** 76
- **Format:** csv
- **Units:** M.EUR
- **Dimensions:** `study`, `consuming_country_iso3`, `purchased_sector_group`, `demand_component`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_expenditure_by_sector_group_and_country.csv`

- **Rows:** 3,724
- **Format:** csv
- **Units:** M.EUR
- **Dimensions:** `study`, `consuming_country_iso3`, `purchased_country_name`, `purchased_sector_group`, `demand_component`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_figure1_contribution_groups.csv`

- **Rows:** 40
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `indicator`, `unit`, `figure_group`, `source`
- **Measures:** `reference_year`, `figure`, `legend_position`, `value`, `share_pct`

### `nl_figure2_hotspot_sector_groups.csv`

- **Rows:** 35
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `indicator`, `unit`, `figure_group`, `source`
- **Measures:** `reference_year`, `figure`, `legend_position`, `value`, `share_pct`

### `nl_figure3_hotspot_world_regions.csv`

- **Rows:** 30
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `indicator`, `unit`, `figure_group`, `source`
- **Measures:** `reference_year`, `figure`, `legend_position`, `value`, `share_pct`

### `nl_hotspot_by_producing_country.csv`

- **Rows:** 255
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `ghg_protocol_scope`, `producing_country_name`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_hotspot_by_producing_node.csv`

- **Rows:** 39,970
- **Format:** csv
- **Resolution:** 1+ regions x 163+ industries (sampled)
- **Units:** kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `producing_country_iso3`, `producing_country_name`, `producing_world_region`, `producing_sector_code`, `producing_sector_name`, `producing_sector_group`, `component_type`, `ghg_protocol_scope`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_hotspot_by_producing_sector.csv`

- **Rows:** 845
- **Format:** csv
- **Resolution:** 1+ regions x 169+ industries (sampled)
- **Units:** Mm3, kt, kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `ghg_protocol_scope`, `producing_sector_code`, `component_type`, `producing_sector_name`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_hotspot_by_sector_group.csv`

- **Rows:** 105
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `ghg_protocol_scope`, `producing_sector_group`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_hotspot_by_sector_group_and_country.csv`

- **Rows:** 4,670
- **Format:** csv
- **Units:** kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `ghg_protocol_scope`, `producing_country_name`, `producing_sector_group`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_hotspot_by_world_region.csv`

- **Rows:** 255
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `ghg_protocol_scope`, `producing_world_region`, `producing_country_name`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_intensity_by_purchased_node.csv`

- **Rows:** 30,830
- **Format:** csv
- **Resolution:** 1+ regions x 152+ industries (sampled)
- **Units:** kt CO2eq per M.EUR
- **Dimensions:** `study`, `consuming_country_iso3`, `purchased_country_iso3`, `purchased_country_name`, `purchased_world_region`, `purchased_sector_code`, `purchased_sector_name`, `purchased_sector_group`, `component_type`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `Total (MEUR)`, `value`

### `nl_intensity_by_purchased_product.csv`

- **Rows:** 800
- **Format:** csv
- **Units:** Mm3 per M.EUR, kt CO2eq per M.EUR, kt per M.EUR
- **Dimensions:** `study`, `consuming_country_iso3`, `purchased_sector_name`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `Total (MEUR)`, `value`

### `nl_intensity_by_sector_group.csv`

- **Rows:** 95
- **Format:** csv
- **Units:** Mm3 per M.EUR, km2 per M.EUR, kt CO2eq per M.EUR, kt per M.EUR
- **Dimensions:** `study`, `consuming_country_iso3`, `purchased_sector_group`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `Total (MEUR)`, `value`

### `nl_intensity_by_sector_group_and_country.csv`

- **Rows:** 4,435
- **Format:** csv
- **Units:** kt CO2eq per M.EUR
- **Dimensions:** `study`, `consuming_country_iso3`, `purchased_country_name`, `purchased_sector_group`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `Total (MEUR)`, `value`

### `nl_published_figure_shares.csv`

- **Rows:** 98
- **Format:** csv
- **Dimensions:** `study`, `consuming_country_iso3`, `article_page`, `indicator`, `figure_group`, `note`, `source`
- **Measures:** `reference_year`, `figure`, `published_share_pct`, `archive_share_pct`, `difference_pp`

### `nl_table_01.csv`

- **Rows:** 42
- **Format:** csv
- **Units:** M.EUR, Mm3, km2, kt, kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `table_row`, `indicator`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `nl_table_s05.csv`

- **Rows:** 15
- **Format:** csv
- **Units:** %, Mm3, km2, kt, kt CO2eq
- **Dimensions:** `study`, `consuming_country_iso3`, `indicator`, `quantity`, `unit`, `source`
- **Measures:** `reference_year`, `value`

### `template_table_dk_vs_nl.csv`

- **Rows:** 35
- **Format:** csv
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `table_row`, `indicator`, `unit`, `per_capita_unit`, `source_netherlands`, `source_denmark`
- **Measures:** `analysis_year_denmark`, `reference_year_netherlands`, `netherlands_2016`, `denmark_2022`, `netherlands_per_capita`, `denmark_per_capita`, `dk_as_pct_of_nl_per_capita`
