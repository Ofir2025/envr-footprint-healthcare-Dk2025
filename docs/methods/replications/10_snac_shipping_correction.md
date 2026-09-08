# 10 - Danish sea-transport reallocation

**Gold folder** `data/gold/results/10_snac_shipping_correction/`
**Module** `analysis.dk_shipping_correction`
**Source** Rørmose Jensen & Iliev (2022), pp. 11-12, Statistics Denmark

Narrative version, written for the layman and for the manuscript methods:
`docs/revision/shipping_reallocation_method.md`.

## Question this layer answers

The submitted manuscript's most quotable finding was that transport accounts for roughly
40 % of the Danish health-care footprint. Is that a finding or an artefact?

## Method

### The diagnosis, reproduced

Statistics Denmark report that EXIOBASE sends **74 %** of Danish water-transport output to
Danish *intermediate* use, against **9 %** in the Danish national accounts. Denmark
operates one of the world's largest merchant fleets; that fleet carries world trade, not
Danish production, so the misallocation loads a global fleet's emissions onto Danish
consumption.

On EXIOBASE v3.8.2 `IOT_2022_ixi` we measure **73.6 %**: Statistics Denmark's 74 %, to the
decimal. EXIOBASE's own hybrid build, which resolves the same source data onto activity
rather than establishment units, gives **7.8 %** natively, within 1.2 points of the
benchmark and with no correction applied.

### The correction

The row's **total output is left unchanged**: it is not in dispute and matches the
national accounts. Only its *allocation* is corrected:

$$t = \phi \, x_{\text{row}}, \qquad \phi = 0.09$$
$$Z[\text{row}, \text{DK}] \leftarrow Z[\text{row}, \text{DK}] \cdot \frac{t}{\sum Z[\text{row}, \text{DK}]}$$

The released amount, 11,509.8 M€, is added to exports, distributed over foreign final
demand in proportion to existing shares. Value added is credited so the column balance
holds.

### Effect

| Quantity | Before | After |
|---|---|---|
| Share to DK intermediate use | 73.6 % | 9.0 % |
| Transport share of the supply-chain footprint | 37.5 % | **18.5 %** |
| DK sea transport as a producing node | 852 kt | **74 kt** |
| Danish national footprint | 85.2 Mt | **77.5 Mt** |

The 18.5 % is on the 3,943 kt MRIO supply-chain basis; on the 4,712 kt total, which
includes the entirely-Danish bottom-up items, transport is 15.5 %. **Quote the basis with
the share**: six figures in the revision documents drifted precisely because it was
omitted.

## Why this is not a novel method

Three independent sources already do or imply this, and none of them is ours:

1. **Danish national accounts** publish the 9 % benchmark and rebuild the Danish block
   entirely rather than patch it.
2. **EXIOBASE's own hybrid build** produces 7.8 % natively.
3. **The Danish Energy Agency** performs "a technical reallocation of import amounts linked
   to the shipping and aviation industries" in the statutory Global Report.

An earlier draft of our methods described the correction as novel. It is not, and the
retraction matters: reconstructing an allocation that official Danish practice already
applies is a far easier argument at review than proposing a new one.

## Data requirements

| Input | Source |
|---|---|
| $Z$, $x$, $Y$ | EXIOBASE v3.8.2 `IOT_2022_ixi` |
| $\phi = 0.09$ | Statistics Denmark national accounts, water transport |
| Cross-check 7.8 % | EXIOBASE hybrid v3.3.18 |

## Deviations from the source, stated

- Statistics Denmark rebuild the whole Danish block (SNAC). We correct **one row**. This
  one-row correction is a narrower intervention that fixes the defect with the largest
  effect on our result while leaving the rest of the block as EXIOBASE published it. The
  trade-off is set out in `docs/revision/snac_and_mrio_remedies.md`.
- $\phi$ is set to the benchmark exactly rather than fitted; the correction carries no
  free parameter.

## Outputs

`shipping_reallocation_diagnostics.csv` (every quantity above, with its source),
`phantom_shipping_input_removed_by_industry.csv` (which Danish industries were recorded as
buying the phantom shipping, including 394 M€ by the health sector, which does not charter
container ships).

## Verification

Row balance residual 1.1 × 10⁻¹¹ M€; maximum column-balance residual in the Danish block
2.4 × 10⁻⁵ M€; industry output unchanged.
