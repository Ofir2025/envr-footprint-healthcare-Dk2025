# 03 — Target-sector scope 3 without double counting

**Gold folder** `data/gold/results/03_cabernard_target_scope3/`
**Module** `analysis.cabernard_target_scope3`
**Source** Cabernard, Pfister & Hellweg (2019), *A new method for analyzing
sustainability performance of global supply chains*, Sci Total Environ 684:164–177,
eqs. 8, 9, 12; extended in Cabernard & Pfister (2022)

## Question this layer answers

A different question from the headline, and the distinction is the point of the folder.

**(a) Final-demand footprint** — what the headline answers:
$$f = s\,L\,y_H$$
Each emission is allocated once, to Danish health-care final demand. This is additive
over any number of target nodes and does not double count (Wood & Hertwich 2018 p. 5).

**(b) Target-sector scope 3** — what Cabernard et al. answer: *what is the scope 3 of
the health sector-regions themselves?* Here the naive form does double count.

## Method

### The double-counting problem

The naive target-sector scope 3 is
$$e_T^{\text{naive}} = s\,L[:,T]\,\widehat{x_T} \qquad \text{(their eq. 8)}$$

Every delivery from one target node to another is counted twice: once as the supplying
target's own output, and again as an input to the receiving target. With one target node
the overlap is small; with 147 nodes it is not.

### The correction

Cabernard's corrected form removes intra-target deliveries before the upstream trace, so
each unit of pressure is attributed to exactly one target node. The overestimate is
reported as a factor:

$$f_T = \frac{e_T^{\text{naive}} - e_T^{\text{wdc}}}{e_T^{\text{naive}}}$$

and the result is checked against the complement identity — target scope 3 plus
non-target scope 3 must reconstruct the world total exactly.

### What it shows

| Target set | Nodes | Naive (Mt) | Corrected (Mt) | Overestimate |
|---|---|---|---|---|
| T1 Danish health and social work | 1 | 4.39 | 4.33 | 1.5 % |
| T2 health and social work, all regions | 49 | 2 592.1 | 2 554.5 | 1.5 % |
| T3 T2 + chemicals + medical instruments | 147 | 9 280.5 | 5 999.5 | **54.7 %** |

The T3 row is the finding. A study that defines its target broadly — health plus its
pharmaceutical and device suppliers, which is exactly how a "health-care supply chain"
is often defined — and applies the naive formula overstates by more than half.

## Data requirements

$A$, $L$, $x$ and the characterised intensity $s$ from [00](00_core_footprint.md).
No additional data.

## Deviations from the source, stated

- Cabernard et al. apply this to global sector groups; the target sets here are chosen
  to bracket plausible definitions of "the health-care supply chain", which is our
  choice and is documented in the `target` column.
- **This layer does not change the headline.** The study's headline is a final-demand
  footprint, form (a), which was never subject to this double counting. The folder
  exists to demonstrate that, not to correct anything.

## Outputs

| File | Content |
|---|---|
| `cabernard_target_scope3.csv` | the three target sets, naive vs corrected, with the identity check |
| `cabernard_target_scope3_by_producing_node.csv.gz` | corrected result at full node detail |
| `cabernard_domestic_vs_imported.csv` | domestic/imported split of the corrected result |

## Verification

`complement_identity_rel_dev` is ≤ 2.3 × 10⁻¹⁵ for all three target sets: target plus
non-target scope 3 reconstructs the world total to machine precision.
