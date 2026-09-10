# 02 - GHG-Protocol scope decomposition

**Gold folder** `data/gold/results/02_scopes_wood_hertwich/`
**Module** `analysis.scopes_detail`
**Sources** Hertwich & Wood (2018), *The growing importance of scope 3 greenhouse gas
emissions from industry*, Environ Res Lett 13:104013, table 1 and eqs. 1-3; GHG Protocol
Corporate Standard and Scope 3 Standard; Doucet et al. / OECD (2025), *Measuring
greenhouse gas emissions in the health sector*, §3.2

> An earlier version of this document and of `scopes_detail.py` attributed the scope
> partition to *Wood, Neuhoff, Moran et al., Clim Policy 20:S39-S57*. That reference is
> a real paper but not the source of this method. The table and equation numbers the module
> follows are Hertwich & Wood (2018) ERL, which is the paper held in the library.

## Question this layer answers

Of the total health-care footprint, this layer asks how much is emitted by the
providers themselves, how much by the generation of the energy they buy, and how much
everywhere else in the supply chain, using the partition a health system would
recognise from its own reporting.

## Method

The three scopes are computed from three different sources, because computing them all
from the MRIO would get Scope 1 wrong.

### Scope 1: direct provider emissions

Scope 1 is taken from Danish national accounts (DST DRIVHUS), **not** from the MRIO.

This boundary is a structural point, not a preference. The final-demand vector $y_H$
is the providers' *purchase* column. The providers' own combustion is therefore outside
$f = s L y_H$ by construction: it never appears in what they buy. Adding a national
accounts figure is not double counting; it is filling a gap the model leaves open.

$$S_1 = \text{DRIVHUS}_{\text{Q}} - \text{medical N}_2\text{O} + \text{anaesthetic gases}_{\text{bottom-up}}$$

Medical nitrous oxide is netted out of the DRIVHUS figure before the bottom-up
anaesthetics estimate is added, so the gas is counted once.

### Scope 2: generation of purchased energy

Purchased electricity, steam, and heat reach the provider through transmission and
distribution, which are separate EXIOBASE industries. A first-tier calculation would
therefore capture the grid, not the power station. The energy block is inverted on its
own so the chain is followed to generation and no further:

$$L_{EE} = (I_{EE} - A_{EE})^{-1}, \qquad S_2 = d_E \cdot L_{EE}\, y_E$$

where $E$ indexes the electricity, steam, and hot-water nodes in all 49 regions and
$y_E$ is the providers' own first-tier energy purchases.

### Three published conventions, all computed

Scope 2 is not one number in the EE-MRIO literature. Three conventions differ by how much
of the purchased-energy chain they count, and the study computes all three:

| Convention | Formula | Value (kt) | What it counts |
|:---|:---|:---|:---|
| OECD (Doucet et al. 2025 §3.2) | $F A Y$, energy sectors | 72.08 | direct emissions of the *first-tier* energy supplier only |
| GHG Protocol strict | $d_E L_{EE} y_E$ | **73.34** | traces through T&D to **generation**, stops inside the energy block |
| **Hertwich & Wood (2018)** | $E_Z = \hat{m}Z$, $m = s(I-A)^{-1}$, energy rows | **74.98** | cradle-to-gate: generation **plus** the upstream fuel supply behind it |

**The manuscript reports 74.98**, the Hertwich & Wood convention, because that is the
method this pipeline inherits and the paper it follows. It is broader than the corporate
standard, which assigns upstream fuel supply to Scope 3 category 3.

**This folder's own partition uses 73.34**, the strict-protocol figure, so that its
Scope 1 + 2 + 3 decomposition is internally protocol-conforming.

The OECD form **under-counts on EXIOBASE `ixi`**: electricity reaches the buyer through
*Transmission* and *Distribution and trade of electricity*, whose own combustion intensity
is near zero, so generation sits one tier further back than $F A Y$ reaches. This
shortfall is a model-layout artefact, not a flaw in their method: their ICIO tables
have a single sector D.

The spread is 72.1-75.0 kt: 3.9 % of Scope 2 and **0.06 % of the total footprint**. The
choice changes no conclusion. It is reported because the manuscript claims GHG-Protocol
scopes, and a reader is entitled to know which operationalisation produced the number.

### Scope 3: everything else

$$S_3 = f_{\text{MRIO}} - S_2 - s_h (L_{hh} - 1) E_H + \text{pMDI} + \text{commuting}$$

The subtracted term is the health sector's **self-supply loop**: the pressure the
Danish health node causes in supplying itself, which the national-accounts Scope 1
figure already contains. It is 1.83 kt. Subtracting it is what makes Scope 1 and
Scope 3 additive rather than overlapping.

### Outside protocol

Patient and visitor travel (263.57 kt) is caused by the health system but is not
attributable to it under any GHG-Protocol scope, because the providers neither own,
control, nor purchase it. It is reported separately rather than folded into Scope 3.

## Data requirements

| Input | Source |
|:---|:---|
| Direct provider emissions | DST DRIVHUS, industry Q |
| Medical anaesthetic gases | Danish pharmacy sales, bottom-up; see `docs/revision/bottom_up_anaesthetics.md` |
| Energy purchases $y_E$ | health column of the Danish use table |
| pMDI, commuting, patient travel | Danish primary registers |

## Deviations from the source, stated

- Hertwich & Wood define the scopes for *gross production* of whole sectors; the
  application to one sector's **final demand** is ours, and the self-supply subtraction is
  a consequence of that application which their paper does not need.
- The manuscript layer ([01](01_eriksen_replication.md)) totals 4,712.42 kt using the
  Hertwich & Wood Scope 2; this folder totals 4,710.58 kt using the strict-protocol
  Scope 2 and removing the self-supply loop. Both are correct on their stated basis, and
  audit check C1 reconciles them: 4,710.58 + 1.83 = 4,712.42. The two terms are
  rounded independently, so adding the printed figures gives 4,712.41; the check
  runs on the unrounded values and closes to 1e-9.

## Outputs

| File | Rows | Content |
|:---|:---|:---|
| `scopes_summary_detailed.csv` | n/a | every scope and variant, with its `basis` stated |
| `scopes_by_producing_node.csv` | 23,727 | each scope resolved to producing node |
| `double_counting_ledger.csv` | n/a | every overlap risk, its test, and its verdict |

## Verification

- `analysis.audit_consistency` C1: partition total 4,710.58 + self-supply loop 1.83
  = 4,712.42, which equals the manuscript grand total. **PASS.**
- The double-counting ledger tests each bottom-up item against the MRIO for overlap and
  records the numerical result, so "we checked for double counting" is a table, not a
  claim.

## Figure-ready tables and figures

`analysis.scope_figure_tables` reshapes the partition for plotting. Scope 2 and the MRIO
part of scope 3 already carry producing nodes; scope 1 and the bottom-up items do not, and
are placed at their true Danish origin rather than dropped:

| Component | Origin | Industry label |
|:---|:---|:---|
| Scope 1 (DRIVHUS) + anaesthetic gases | DNK | Health and social work |
| pMDI propellants | DNK | Health and social work |
| Employee commuting | DNK | Bottom-up: employee commuting |
| Patient and visitor travel | DNK | Bottom-up: patient and visitor travel |

All are Danish by construction (emissions of Danish providers, staff, or patients),
so labelling them as such is what lets the bars be added back to the headline.

| Table | Grain |
|:---|:---|
| `scope_by_origin_and_industry.csv` | scope × producing country × producing industry (7,346 rows) |
| `scope_by_origin_industry_top25.csv` | the 25 largest (country, industry) pairs, remainder pooled and labelled |
| `scope_by_industry_group.csv` | scope × industry group |
| `scope_by_continent.csv` | scope × world region of origin |
| `scope_by_continent_and_industry_group.csv` | the cross |
| `scope_by_country.csv` | scope × country |

Each aggregation asserts that it preserves the total, so no view can silently lose mass.

`R/plot_scope_emissions.R` renders four TIFFs from these tables, in the study's figure
conventions (`R/_dk_common.R`): no on-figure title, facet titles the largest text, legend
at the bottom without a title, bars ranked descending with the remainder re-sorted into the
ranking by its own value, per-facet axis ceilings so no bar touches the panel edge, and
ASCII-only labels because the TIFF font renders a middle dot as `..`.

**A finding visible in the top-origins figure:** the 25 largest origin-industry pairs
account for 45 % of the footprint; the pooled remainder is the single largest bar. The
Danish health footprint is diffuse (no supplier dominates it), which is itself worth
stating, and is why the remainder bar is kept rather than cropped.
