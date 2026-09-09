# 01 - Eriksen replication (the manuscript layer)

**Gold folder** `data/gold/results/01_eriksen_replication/`
**Modules** `analysis.main_2025`, `analysis.eriksen_tables`
**Source** Eriksen et al., *The environmental impacts of the Danish health care system:
supply-chain origins and geographical displacement of impacts*, NXSUST-D-26-01589,
itself following Steenmeijer et al. (2022)

## Question this layer answers

This layer reproduces everything the manuscript reports, in the manuscript's own
table and figure structure, once per reference year and its matching background
model: 2019 expenditure on the 2016 background (as submitted) in `2019/`, and
2022 expenditure on the 2022 background (the resubmission) in `2022/`.

This folder is the deliverable for the resubmission. It is deliberately kept in the
submitted paper's shape (the same tables, the same figure numbering) so that the
revision can be described as a change of inputs and corrections, not a change of study.

## Method

Three quantities are reported, and they are three different things that the submitted
manuscript did not fully separate.

> **Naming warning, inherited from the original code.** The two analyses are named
> the opposite way round from how most readers will guess, and the names cannot be
> changed without breaking continuity with the submitted manuscript. In this study:
>
> * `hotspot` $= B\,\mathrm{diag}(L y)$, indexed by the **producing node**, i.e.
>   *where the pressure physically occurs*.
> * `contribution` $= B\,L\,\mathrm{diag}(y)$, indexed by the **purchased
>   product**, i.e. *which purchase drives it*.
>
> Reading them the intuitive way inverts the domestic/imported split: 26.3 % of the
> climate footprint is domestic on the producing-node basis, and 61.7 % on the
> purchased-product basis. Since September 2026 the output columns carry the correct
> `producing_*` / `purchased_*` prefixes, so the file schema now disambiguates them
> even though the file stems retain the legacy words.

### Contribution

Pressure allocated to the node where it arises, driven by health final demand:

$$c_i = s_i \,[L\,y_H]_i$$

This allocation is what "where does the impact occur" means. It sums to $f$ across
all nodes.

### Hotspot

The same quantity aggregated to the **purchased product**, i.e. the second marginal of
$E$ from [00](00_core_footprint.md):

$$h_j = y_{H,j}\,[s\,L]_j$$

This marginal is what "which purchase drives it" means. It also sums to $f$.
Contribution and hotspot are marginals of the same table and must not be added
together; doing so double counts the whole footprint. The tables are written
separately for exactly this reason.

### Intensity

Pressure per unit of expenditure on a product, independent of how much is bought:

$$m_j = [s\,L]_j \quad \text{(kt CO}_2\text{e per M€)}$$

Intensity ranks products by how damaging a euro spent on them is; hotspot ranks them by
how much damage our actual spending causes. A product can be top of one and unremarkable
on the other, and the manuscript's discussion depends on the distinction.

### Scope split

The scope split is reported here from [02](02_scopes_wood_hertwich.md) and
summarised in `scopes_summary.csv`, so the manuscript's scope figure is reproducible
from this folder alone.

## Data requirements

This layer needs the same inputs as [00](00_core_footprint.md), plus the bottom-up
items added outside the MRIO: direct provider emissions (DST DRIVHUS), medical
anaesthetic gases, patient and visitor travel, employee commuting, and the domestic
waste account ([05](05_waste_dst_accounts.md)).

## Deviations from the submitted manuscript, stated

These deviations are the ones a reviewer will need to see declared.

| Submitted | Revision | Reason |
|:---|:---|:---|
| 2019 expenditure on the 2016 model | 2022 on 2022 | reviewer R2-4; removes the deflation question entirely |
| EXIOBASE v3.7 | v3.8.2 | v3.10.2 tested and rejected, see [09](09_vintage_diagnostics.md) |
| AR4 climate factors (implicit in the DESIRE sheet) | IPCC AR6 | [15](15_gwp_vintage.md) |
| transport 37.5 % of the supply-chain footprint | 18.5 %, or 15.5 % of the total | EXIOBASE artefact, see [10](10_sea_transport_reallocation.md) |
| aggregate results only | aggregate **and** full node detail | reviewer R1-11 |
| no uncertainty | Monte Carlo, 10⁵ draws | reviewer R1-1, see [04](04_uncertainty_lenzen_ieooc.md) |

## Outputs

Gold publishes tabular data only, so every manuscript table below is a CSV; no
workbook, document or image is published in this folder.

| File | Content |
|:---|:---|
| `hotspot_by_producing_node.csv` (22,229 rows) | $c_i$, indexed by **producing node** |
| `contribution_by_purchased_product.csv` (30,499) | $h_j$, indexed by **purchased product** |
| `intensity_by_purchased_product.csv` (30,487) | $m_j$, indexed by purchased product |
| `*_by_sector_group.csv`, `*_by_world_region.csv`, `*_domestic_vs_imported.csv` | the aggregations the manuscript prints |
| `table_01.csv`, `table_s05_dk.csv`, `steenmeijer_table.csv` | manuscript tables |
| `scopes_summary.csv` | the GHG-Protocol scope split for this boundary |
| `full_results_tables_fig1_absolute.csv`, `full_results_tables_fig1_relative_pct.csv`, `full_results_tables_fig2_absolute.csv`, `full_results_tables_fig2_relative_pct.csv`, `full_results_tables_fig3_absolute.csv`, `full_results_tables_fig3_relative_pct.csv` | the tables behind figures 1-3, absolute and as a percentage share |
| `figure1_activity_contributions.csv`, `figure2_sector_contributions.csv`, `figure2b_top_origin_industry_pairs.csv`, `figure3_geographical_origin.csv` | the plotted data behind figures 1, 2, 2b and 3 |

`contribution_full_detail.xlsx` and `hotspot_full_detail.xlsx`, the wide
raw-detail copies of $h_j$ and $c_i$, are written to silver (`eriksen_interim/`)
rather than gold: they are a redundant wide copy of the same two frames already
published above in long format, so nothing is lost by not publishing them here.
Manuscript figures are not published from this folder either; they are produced
separately under `figures/manuscript/`.

## Verification

- Contribution, hotspot, and the domestic/imported split each sum to the same $f$;
  asserted, not assumed.
- `analysis.audit_consistency` runs C2 (every detail table reconciles to its own
  aggregate) and C1 (this folder's headline equals the one every other module
  computes) against it.
- The headline is scope-guarded: only `HC_SCOPE=health_eldercare` writes here, so a
  sensitivity run cannot silently overwrite the manuscript numbers.
