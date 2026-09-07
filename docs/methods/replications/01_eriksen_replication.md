# 01 — Eriksen replication (the manuscript layer)

**Gold folder** `data/gold/results/01_eriksen_replication/`
**Modules** `analysis.main_2025`, `analysis.eriksen_tables`
**Source** Eriksen et al., *The environmental impacts of the Danish health care system:
supply-chain origins and geographical displacement of impacts*, NXSUST-D-26-01589 —
itself following Steenmeijer et al. (2022)

## Question this layer answers

Everything the manuscript reports, in the manuscript's own table and figure structure,
for reference year 2022 on a 2022 background model.

This folder is the deliverable for the resubmission. It is deliberately kept in the
submitted paper's shape — the same tables, the same figure numbering — so that the
revision can be described as a change of inputs and corrections, not a change of study.

## Method

Three quantities are reported, and they are three different things that the submitted
manuscript did not fully separate.

> **Naming warning, inherited from the original code.** The two analyses are named
> the opposite way round from how most readers will guess, and the names cannot be
> changed without breaking continuity with the submitted manuscript. In this study:
>
> * `hotspot` $= B\,\mathrm{diag}(L y)$ — indexed by the **producing node**, i.e.
>   *where the pressure physically occurs*.
> * `contribution` $= B\,L\,\mathrm{diag}(y)$ — indexed by the **purchased
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

This is what "where does the impact occur" means. It sums to $f$ across all nodes.

### Hotspot

The same quantity aggregated to the **purchased product**, i.e. the second marginal of
$E$ from [00](00_core_footprint.md):

$$h_j = y_{H,j}\,[s\,L]_j$$

This is what "which purchase drives it" means. It also sums to $f$. Contribution and
hotspot are marginals of the same table and must not be added together — doing so
double counts the whole footprint. The tables are written separately for exactly this
reason.

### Intensity

Pressure per unit of expenditure on a product, independent of how much is bought:

$$m_j = [s\,L]_j \quad \text{(kt CO}_2\text{e per M€)}$$

Intensity ranks products by how damaging a euro spent on them is; hotspot ranks them by
how much damage our actual spending causes. A product can be top of one and unremarkable
on the other, and the manuscript's discussion depends on the distinction.

### Scope split

Reported here from [02](02_scopes_wood_hertwich.md), summarised in `scopes_summary.csv`
so the manuscript's scope figure is reproducible from this folder alone.

## Data requirements

As [00](00_core_footprint.md), plus the bottom-up items added outside the MRIO:
direct provider emissions (DST DRIVHUS), medical anaesthetic gases, patient and
visitor travel, employee commuting, and the domestic waste account
([05](05_waste_dst_accounts.md)).

## Deviations from the submitted manuscript, stated

These are the changes a reviewer will need to see declared.

| Submitted | Revision | Reason |
|---|---|---|
| 2019 expenditure on the 2016 model | 2022 on 2022 | reviewer R2-4; removes the deflation question entirely |
| EXIOBASE v3.7 | v3.8.2 | v3.10.2 tested and rejected, see [09](09_vintage_diagnostics.md) |
| AR4 climate factors (implicit in the DESIRE sheet) | IPCC AR6 | [15](15_gwp_vintage.md) |
| transport 37.5 % of the footprint | 18.9 % | EXIOBASE artefact, see [10](10_snac_shipping_correction.md) |
| aggregate results only | aggregate **and** full node detail | reviewer R1-11 |
| no uncertainty | Monte Carlo, 10⁵ draws | reviewer R1-1, see [04](04_uncertainty_lenzen_ieooc.md) |

## Outputs

| File | Content |
|---|---|
| `hotspot_by_producing_node.csv` (22 229 rows) | $c_i$, indexed by **producing node** |
| `contribution_by_purchased_product.csv` (30 499) | $h_j$, indexed by **purchased product** |
| `intensity_by_purchased_product.csv` (30 487) | $m_j$, indexed by purchased product |
| `*_by_sector_group.csv`, `*_by_world_region.csv`, `*_domestic_vs_imported.csv` | the aggregations the manuscript prints |
| `table_1.xlsx`, `table_s5_dk.xlsx`, `steenmeijer_table.xlsx` | manuscript tables |
| `fig_1.png` … `figure_5_total_contribution.png`, `all_figures.pdf` | manuscript figures |
| `Contribution_full_detail.xlsx`, `Hotspot_full_detail.xlsx` | SI workbooks |

## Verification

- Contribution, hotspot and the domestic/imported split each sum to the same $f$;
  asserted, not assumed.
- `analysis.audit_consistency` checks C1 (detail reconciles to aggregate) and C4
  (this folder's headline equals `00_core_footprint`'s) run against it.
- The headline is scope-guarded: only `HC_SCOPE=health_eldercare` writes here, so a
  sensitivity run cannot silently overwrite the manuscript numbers.
