# 11 - Capital endogenisation

**Gold folder** `data/gold/results/11_capital_gfcf/`
**Modules** `analysis.capital_endogenised_sodersten`, `analysis.capital_gfcf`
**Source** Södersten, Wood & Hertwich (2018), *Environmental impacts of capital formation*,
Environ Sci Technol 52:13250-13259, eq. 13 and SI §4.1.1; capital matrices from
Zenodo 7073276 (CC BY 4.0)

## Question this layer answers

Steenmeijer, Eckelman, and the NHS reports all **exclude** capital: the Leontief
matrix carries current inputs only, so hospital buildings, scanners, and IT systems
never enter the supply chain. Wood & Hertwich and Södersten et al. both show this is
the largest single boundary omission for service sectors. How large is it here?

## Method

### The published method

Södersten et al. add a capital requirement matrix inside the same Leontief inverse:

$$K = \bar{K}\,\hat{x}^{-1}, \qquad L^K = \bigl(I - (A + K)\bigr)^{-1} \qquad \text{(their eq. 13)}$$

They endogenise **consumption of fixed capital (CFC)**, not gross fixed capital formation,
because gross formation charges this year's investment to this year's consumption and is
hypersensitive to investment shocks (their SI §4.1.1).

### The bridge this study had to supply

The published capital matrices are distributed as
`Kbar_exio_v3_8_2_<year>_cfc_pxi.mat`, a **9,800 × 7,987** matrix of capital *products*
used by *industries*. This study runs the **industry-by-industry** table, which needs
7,987 × 7,987, so the product rows must be mapped to industries.

Södersten's SI (line 166) states they apply "the industry technology construct … to conform
with the way the A matrix is constructed". That construct needs the **market-share matrix**,
which is built from the MRSUT supply table published alongside the IOTs in the same Zenodo
record:

$$D_{ip} = \frac{V_{pi}}{q_p}, \qquad \bar{K}^{\text{ixi}} = D\,\bar{K}^{\text{pxi}}$$

with $V$ the supply table (9,800 products × 7,987 industries) and $q$ total product
output.

> An earlier draft of `docs/revision/capital_gfcf_treatment.md` claimed these matrices
> could not be used with an ixi model. That assertion was wrong (MRSUT files exist for
> every year in Zenodo record 5589597), and the claim has been retracted in that
> document.

### Three treatments, reported side by side

| Treatment | Definition |
|:---|:---|
| **Baseline** | capital excluded, $f = C S L y_H$, what Steenmeijer, Eckelman, and the NHS report, and the comparable number |
| **A: exogenous service flow** | CFC of the Danish health and residential-care industries (DST NABK69, P.51c) footprinted as an additional final demand, with the commodity composition of the observed Danish health capital asset mix |
| **B: endogenised (Södersten)** | $L^K$ as above |

### Effect of endogenisation

| Indicator | Change |
|:---|:---|
| Climate change | 4,062 → 4,849 kt, **+19.4 %** |
| Material extraction | +33.2 % |
| Blue water | +10.2 % |
| Land use | +20.0 % |
| Waste generation | +17.3 % |

The simplified construction used earlier gave +21.0 %, so the published method validates it
to within 1.6 percentage points.

## Data requirements

| Input | Source |
|:---|:---|
| $\bar{K}^{\text{pxi}}$ | `Kbar_exio_v3_8_2_2020_cfc_pxi.mat`, Zenodo 7073276 |
| Supply table $V$ | `MRSUT_2020/supply.csv`, Zenodo 5589597 (223 MB) |
| CFC by asset | DST NABK69, P.51c |
| Asset ↔ EXIOBASE product mapping | `capital_asset_mix.csv` |

Two implementation traps, both recorded because both silently corrupt the result:

- `supply.csv` must be read with `usecols=range(2, 2+7987)`; applying `dtype=np.float64`
  to the index columns raises on the ISO2 codes.
- The asset name is `"ICT equipment, other machinery and equipment and weapon systems"`.
  Truncating it before `and weapon systems` silently drops 45 % of CFC.

## Deviations from the source, stated

- Södersten use the 2020 capital matrix; our analysis year is 2022. The capital stock
  structure is treated as stable over two years, which is stated rather than assumed
  silently. No 2022 $\bar{K}$ has been published.
- **The headline keeps capital excluded.** Endogenising it would break comparability with
  every study the paper benchmarks against. The magnitude is reported here so the omission
  is quantified rather than merely declared.

## Outputs

This layer writes `capital_endogenised_sodersten.csv`,
`capital_scenarios_by_indicator.csv`, `capital_asset_mix.csv`,
`capital_diagnostics.csv`, `capital_endogenised_by_producing_node.csv.gz`, and
`capital_endogenised_domestic_vs_imported.csv`.

## Verification

Product-to-industry conservation holds to 1.17 × 10⁻¹⁴; the inverse is verified by
$L^K[:,j] - (A+K)L^K[:,j] - I[:,j]$ at 1.64 × 10⁻¹⁴. Productivity is tested by power
iteration on $A+K$, not by column sums: EXIOBASE has 72 columns summing above 1 while
remaining productive, so a column-sum test gives a false failure.
