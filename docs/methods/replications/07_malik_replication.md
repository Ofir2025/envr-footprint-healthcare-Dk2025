# 07 - Malik replication and production layers

**Gold folder** `data/gold/results/07_malik_replication/`
**Modules** `analysis.malik_replication`, `analysis.production_layers`
**Sources** Malik, Lenzen, McAlister & McGain (2018), *The carbon footprint of Australian
health care*, Lancet Planet Health 2:e27-35; Malik et al. (2021); Lenzen et al. (2020) SI §5

## Question this layer answers

How does Denmark compare with the Australian health system, on Australia's own
methodological choices rather than ours; and how far upstream does the pressure occur?

## Method

### Making the comparison like-for-like

Malik et al.'s boundary choices differ from ours in ways that make a naive comparison
wrong. Each is matched or declared:

| Choice | Malik 2018 | Malik 2021 | This study | What we do |
|---|---|---|---|---|
| imports | in the value-added block | excluded | full MRIO | compute a domestic-only variant |
| capital | included (2,776 kt, 8 % of their total) | excluded | excluded | report the capital sensitivity separately |

Because both Malik papers are **domestic-only models**, the only Danish number comparable
with their 7.2 % / 6.6 % national shares is a domestic-only variant:

$$L_{\text{dom}} = (I - A_{\text{DK,DK}})^{-1} \qquad (163 \times 163)$$

$$f_{\text{dom}} = s_{\text{DK}} \, L_{\text{dom}} \, y_{H,\text{DK}}$$

This variant is reported in `malik_domestic_vs_full.csv` beside the full-MRIO result,
so the reader can see both the comparable number and the complete one.

### Production-layer decomposition

The Leontief inverse is a convergent series, so the footprint splits by how far upstream
the pressure occurs:

$$L = (I-A)^{-1} = I + A + A^2 + \dots$$
$$f^{(n)} = \mathrm{diag}(s)\, A^n y \qquad \text{(pressure in layer } n \text{, by node)}$$
$$S_m = \frac{\sum_{n \le m} f^{(n)}}{f}, \qquad TE_m = 1 - S_m$$

The **diagonalised** form is what allows each layer to be broken down by the sector in
which the pressure occurs (Malik's Fig. 3); the scalar form $q A^n y$ cannot do that.

Powers of $A$ are never formed; the layer vector is iterated $v \leftarrow A v$, which
is $O(n^2)$ per layer instead of $O(n^3)$.

The residual beyond the last computed layer is closed **exactly**:

$$\text{residual} = s \cdot A^{M+1} L y$$

so the reported layers plus residual sum to the footprint with no truncation error left
unaccounted.

### What the layers show

| Layer | Imported share |
|---|---|
| 0 | 49.7 % |
| 1 | 70.8 % |
| 2 | 78.0 % |
| 3 | 89.7 % |

Geographical displacement deepens with every tier. This deepening is the evidence
behind the manuscript's displacement claim, and it is stronger than the aggregate split
because it shows a gradient rather than a single ratio.

## Data requirements

This layer needs $A$, $L$, $s$, and $y_H$ from [00](00_core_footprint.md); Malik's
published values are transcribed into `malik_published_reference.csv` with their
boundary recorded per row.

## Deviations from the source, stated

- Malik's Australian model (IELab) has native health sub-sector detail that EXIOBASE's
  `ixi` layout does not; sub-sector comparison is therefore made through the concordance
  route of [17](17_health_subsectors.md), with its limits stated there.
- Their capital inclusion is not matched in the headline; it is quantified in
  [11](11_capital_gfcf.md).

## Outputs

This layer writes `malik_domestic_vs_full.csv`, `malik_component_intensities.csv`,
`malik_published_reference.csv`, `production_layers.csv`,
`production_layers_by_sector_group.csv`, `production_layers_domestic_vs_imported.csv`,
`production_layers_by_producing_node.csv.gz`, `production_layers_vs_malik.csv`.

## Verification

Layers plus residual reconcile to the footprint exactly, by construction of the residual
term; the reconciliation is asserted at write time.
