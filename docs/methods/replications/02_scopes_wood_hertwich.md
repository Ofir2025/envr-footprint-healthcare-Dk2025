# 02 — GHG-Protocol scope decomposition

**Gold folder** `data/gold/results/02_scopes_wood_hertwich/`
**Module** `analysis.scopes_detail`
**Source** Wood, Neuhoff, Moran et al. (2018), *The structure, drivers and policy
implications of the European carbon footprint*, Clim Policy 20:S39–S57, table 1 and
eqs. 1–2; GHG Protocol Corporate Standard and Scope 3 Standard

## Question this layer answers

Of the total health-care footprint, how much is emitted by the providers themselves,
how much by the generation of the energy they buy, and how much everywhere else in the
supply chain — using the partition a health system would recognise from its own
reporting.

## Method

The three scopes are computed from three different sources, because computing them all
from the MRIO would get Scope 1 wrong.

### Scope 1 — direct provider emissions

Taken from Danish national accounts (DST DRIVHUS), **not** from the MRIO.

This is a structural point, not a preference. The final-demand vector $y_H$ is the
providers' *purchase* column. The providers' own combustion is therefore outside
$f = s L y_H$ by construction: it never appears in what they buy. Adding a national
accounts figure is not double counting — it is filling a gap the model leaves open.

$$S_1 = \text{DRIVHUS}_{\text{Q}} - \text{medical N}_2\text{O} + \text{anaesthetic gases}_{\text{bottom-up}}$$

Medical nitrous oxide is netted out of the DRIVHUS figure before the bottom-up
anaesthetics estimate is added, so the gas is counted once.

### Scope 2 — generation of purchased energy

Purchased electricity, steam and heat reach the provider through transmission and
distribution, which are separate EXIOBASE industries. A first-tier calculation would
therefore capture the grid, not the power station. The energy block is inverted on its
own so the chain is followed to generation and no further:

$$L_{EE} = (I_{EE} - A_{EE})^{-1}, \qquad S_2 = d_E \cdot L_{EE}\, y_E$$

where $E$ indexes the electricity, steam and hot-water nodes in all 49 regions and
$y_E$ is the providers' own first-tier energy purchases.

Two variants are computed and reported as sensitivities, **not** added to the total:

| Variant | Value (kt) | What it does |
|---|---|---|
| first-tier only | 72.08 | stops at the retailer; misses generation behind the grid |
| **energy-block inverse** | **73.34** | protocol-conforming: reaches generation, stops there |
| full $L$ | 74.98 | also captures energy used deeper in the chain, which GHG-P assigns to Scope 3 |

### Scope 3 — everything else

$$S_3 = f_{\text{MRIO}} - S_2 - s_h (L_{hh} - 1) E_H + \text{pMDI} + \text{commuting}$$

The subtracted term is the health sector's **self-supply loop**: the pressure the
Danish health node causes in supplying itself, which the national-accounts Scope 1
figure already contains. It is 1.83 kt. Subtracting it is what makes Scope 1 and
Scope 3 additive rather than overlapping.

### Outside protocol

Patient and visitor travel (263.57 kt) is caused by the health system but is not
attributable to it under any GHG-Protocol scope, because the providers neither own,
control nor purchase it. It is reported separately rather than folded into Scope 3.

## Data requirements

| Input | Source |
|---|---|
| Direct provider emissions | DST DRIVHUS, industry Q |
| Medical anaesthetic gases | Danish pharmacy sales, bottom-up; see `docs/revision/bottom_up_anaesthetics.md` |
| Energy purchases $y_E$ | health column of the Danish use table |
| pMDI, commuting, patient travel | Danish primary registers |

## Deviations from the source, stated

- Wood et al. define the scopes for a national footprint; the application to a sector's
  final demand is ours, and the self-supply subtraction is a consequence of that
  application which their paper does not need.
- The manuscript layer ([01](01_eriksen_replication.md)) reports the **full-$L$**
  Scope 2 (74.98) rather than the protocol-conforming energy-block figure (73.34). The
  difference is 1.6 kt and does not change the total, but it does mean the reported
  Scope 2 slightly exceeds what the GHG Protocol would assign. Both are in the output.

## Outputs

| File | Rows | Content |
|---|---|---|
| `scopes_summary_detailed.csv` | — | every scope and variant, with its `basis` stated |
| `scopes_by_producing_node.csv` | 23 727 | each scope resolved to producing node |
| `double_counting_ledger.csv` | — | every overlap risk, its test, and its verdict |

## Verification

- `analysis.audit_consistency` C1: partition total 4 711.53 + self-supply loop 1.83
  = 4 713.37, which equals the manuscript grand total. **PASS.**
- The double-counting ledger tests each bottom-up item against the MRIO for overlap and
  records the numerical result, so "we checked for double counting" is a table, not a
  claim.
