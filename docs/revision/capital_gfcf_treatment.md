# Capital (GFCF) in health-sector footprints: what others do, and what we do

**Question addressed:** *"Do we need to include capital/GFCF? We don't even
address endogenising capital. How do other studies address this?"*

Reproduce with `PYTHONPATH=src .venv/bin/python -m analysis.capital_gfcf`
→ `data/gold/results/11_capital_gfcf/`.

## 1. Why capital is normally missing

An input-output model's intermediate matrix $\mathbf{Z}$ records **current** inputs only.
Gross fixed capital formation sits in final demand, so in the standard Leontief
construction $f = \mathbf{C}\,\mathbf{S}\,\mathbf{L}\,y$ a hospital's building, its MRI scanner, and its
patient-record system are never in the health sector's supply chain; they are
somebody else's final demand. For manufacturing this matters little; for
services, whose capital stock is large relative to annual purchases, it is the
single largest boundary omission (Wood & Hertwich 2018; Södersten et al. 2018).

## 2. What the comparable studies do

| Study | Capital | Effect reported |
|:---|:---|:---|
| **Steenmeijer et al. 2022** (NL, the template) | **Excluded** | not quantified |
| **Eckelman & Sherman 2016; Eckelman et al. 2020** (US) | **Excluded** (US EEIO, no capital closure) | not quantified |
| **Tennison et al. 2021 / NHS England** | **Included** for the built estate via a separate capital-spend line, outside the EEIO | capital ≈ 4 % of the NHS footprint |
| **Malik et al. 2018** (Australia) | **Included**: the Australian IELab table is capital-endogenised | one reason their 7.2 % national share exceeds most others |
| **Malik et al. 2021** (NSW) | **Excluded** | stated as a limitation |
| **Lenzen et al. 2020** (global, 189 countries) | **Excluded** | stated as a limitation |
| **Pichler et al. 2019; Weisz et al. 2020** (AT, EU) | **Excluded** | n/a |
| **Arup/HCWH 2019** | **Excluded** | n/a |
| **Södersten et al. 2018** (method paper, EXIOBASE) | **Endogenised** | raises global consumption footprints ~10-15 %, and more for services |

So the field is split, and (importantly for comparability) **the studies this
one is benchmarked against mostly exclude capital**. Any headline that included
capital would not be comparable to Steenmeijer, Eckelman, Lenzen, or Pichler.

## 3. Two data problems specific to Denmark

**(a) EXIOBASE understates Danish health capital.** Its consumption of fixed
capital for the Danish health-and-social-work industry is **1,269 M€**, against
**2,274 M€** in Statistics Denmark's own capital accounts (NABK69, P.51c,
V86000 + V87880, 2022), understated **1.79×**. Any capital scenario built on
EXIOBASE's own CFC row would therefore understate the effect by nearly half.
Scenario A below is grounded in the national accounts instead.

**(b) An earlier claim in this repository was wrong and is withdrawn.** A note in
`double_counting_audit.py` and in the response letter attributed the *zero*
intermediate purchases of medical instruments by Danish providers to the capital
boundary (equipment sitting in GFCF rather than in `Z`). That was incorrect. The
zero is a data defect: EXIOBASE v3.10.2 carries ~zero output for industry 33 in
every European region in every year tested. See
[`../methods/exiobase_version_vintage_and_classification.md`](../methods/exiobase_version_vintage_and_classification.md).
Both places are corrected.

## 4. What we compute

All three treatments run on the same background, so they are strictly
comparable. Danish health capital is 36.6 % buildings, 44.7 % ICT/machinery/
equipment, 16.4 % intellectual property products, 1.7 % transport equipment
(NABK69 by asset; `capital_asset_mix.csv`).

**Baseline: capital excluded.** $f = \mathbf{C}\,\mathbf{S}\,\mathbf{L}\,y_H$. It is the Steenmeijer-comparable
number, and the study's headline.

**Scenario A: exogenous capital service flow.**

$$f_A = f + \mathbf{C}\,\mathbf{S}\,\mathbf{L}\,y_{\text{cap}}, \qquad \sum y_{\text{cap}} = \text{CFC}_{\text{health}} = 2{,}274\text{ M€}$$

CFC, not GFCF, is the correct flow for an annual account: it is the capital
actually consumed during the year, so no asset is charged more than once over
its life. Using GFCF (3,200 M€) instead would overstate by 41 % in a year of
above-trend hospital investment. $y_{\text{cap}}$ is spread over EXIOBASE products by the
Danish asset mix, and within each asset class by Denmark's own GFCF column, so
the import geography comes from the model rather than from an assumption.

**Scenario D: full endogenisation** (Södersten, Wood & Hertwich 2018;
Lenzen-Treloar augmentation):

$$K(:,j) = g_r(j) \cdot \frac{\text{cfc}_j}{x_j}, \qquad \mathbf{A}' = \mathbf{A} + K, \qquad \mathbf{L}' = (\mathbf{I} - \mathbf{A}')^{-1}$$

for every industry in every region, $g_r$ being region *r*'s normalised GFCF
commodity vector. This construction propagates capital through **every** tier of
the chain, not just the first, and is an upper bound.

## 5. Results (Denmark 2022, shipping-corrected model)

| Indicator | Baseline (excluded) | A (exogenous CFC) | D (endogenised, simplified construction) |
|:---|:---|:---|:---|
| Climate change (kt CO₂e) | **4,062** | 4,598 (**+13.2 %**) | 4,914 (**+21.0 %**) |
| Material extraction (kt) | **4,234** | 5,028 (**+18.8 %**) | 5,547 (**+31.0 %**) |
| Blue water (Mm³) | **95.3** | 102.4 (**+7.4 %**) | 105.4 (**+10.6 %**) |
| Land use (km²) | **4,854** | 5,362 (**+10.5 %**) | 5,767 (**+18.8 %**) |
| Waste generation (kt) | **259.4** | 283.2 (**+9.2 %**) | 301.0 (**+16.0 %**) |

*MRIO components; the bottom-up items are unaffected by the capital boundary.
Source: `11_capital_gfcf/capital_scenarios_by_indicator.csv`. The waste row
previously read 377, 400 and 418 kt, from the accounts before the hybrid-waste
boundary was corrected; column D here is this study's own construction, and the
published Södersten matrices are in the table further down.*

Capital adds **13-21 %** to the climate footprint and more to materials, which
is what one expects: buildings and equipment are material-intensive. The spread
between A and D is the honest measure of how much the answer depends on the
method rather than on the data.

## 5b. Independent evidence that capital is not negligible

Eurostat's own FIGARO-based footprint for Denmark 2022 (`env_ac_ghgfp`,
reproduced in `06_benchmarks_validation/figaro_dk_footprint_by_final_demand.csv`)
splits the national consumption-based total by final-demand category:

| Final demand category | kt CO₂e | share |
|:---|:---|:---|
| Household final consumption | 30,172 | 52.6 % |
| **Gross fixed capital formation** | **17,676** | **30.8 %** |
| General government final consumption | 6,374 | 11.1 % |
| Changes in inventories and valuables | 2,845 | 5.0 % |
| NPISH final consumption | 335 | 0.6 % |
| **Total** | **57,402** | 100 % |

Capital formation carries **31 % of Denmark's entire consumption-based
footprint**, three times the whole of general-government consumption. A
health-sector study that excludes capital is therefore excluding a category that
is large in the national accounts, not a rounding term. This share is an argument
for reporting the capital sensitivity prominently, not for changing the headline:
the exclusion remains the comparable choice, but it must be stated as a boundary
decision with a quantified consequence rather than as a technical detail.

## 5c. The published framing of the choice

Hertwich (2011, *Economic Systems Research* 23(1):27-47, §3.4) treats
endogenisation explicitly as a modelling **choice** rather than a correctness
question, and sizes what is at stake:

> *"Some input-output studies endogenize gross fixed capital expenditure: they
> treat investment as a prerequisite for production and hence assign the
> emissions connected to the building of factories and machines to the products
> that are produced in these factories and machines… **When investments are kept
> separate, they turn out to be more important than government consumption. On a
> global level, they account for 18 % of greenhouse gas emissions**, with the
> highest shares observed in emerging economies."*

He also gives the argument for the opposite choice:

> *"Other authors, however, prefer to keep capital expenditure as a separate
> final demand category. This can be very sensible in the case of rapidly
> developing countries where the current rate of capital expenditure is much
> larger than required to sustain a steady level of output (Peters et al.,
> 2007)."*

Composition: construction about 10 %, with most of the remainder machinery, and
transport also material.

**Why this matters here specifically.** Hospital estate, imaging equipment, and
vehicle fleets sit in gross fixed capital formation. With capital exogenous
(which is what both Rørmose Jensen & Iliev and Palm et al. do), a health-care
footprint defined over government and household health consumption **excludes
them**, and the excluded pool is globally about 18 % of greenhouse-gas
emissions, larger than all government consumption at about 10 %. That is the
strongest available argument for reporting the capital sensitivity prominently
rather than as a footnote.

The canonical method reference Hertwich points to, Lenzen & Treloar (2004)
*Journal of Applied Input-Output Analysis* 10:1-11, is not held locally and
would need fetching if the endogenisation algebra is to be cited at source
rather than through Södersten et al. (2018).

## 5d. Södersten et al. (2018): the method, and how ours differs

The paper is now held locally (`docs/references/sodersten_et_al_2018_endogenizing_capital_mrio.pdf`
and its SI), obtained from the author's NTNU doctoral thesis, which reprints it
under an ACS AuthorChoice licence permitting non-commercial redistribution.

**Their method.** $\mathbf{A} = \mathbf{Z}\,\hat{x}^{-1}$, $K = \bar{K}\,\hat{x}^{-1}$, and capital enters the *same*
inverse rather than being bordered on:

$$\mathbf{L}^K = (\mathbf{I} - (\mathbf{A} + K))^{-1}$$

The double-counting fix is that **gross fixed capital formation is removed from
final demand**. A residual $y_r^K = \text{GFCF} - \text{CFC}$ is added back only to keep
same-year global totals comparable, and they describe it themselves as *"only a
workaround"*; it can go negative.

**They endogenise consumption of fixed capital, not gross formation**, breaking
with Lenzen & Treloar. Their reasons: GFCF charges this year's investment to
this year's consumption, is hypersensitive to shocks (investment fell from 26 %
to 22 % of global final demand after 2008), and inverts the life-cycle logic.
**This study makes the same choice**, and Statistics Denmark's NABK69 publishes
both flows so the choice is ours to make rather than imposed by data.

**Their effect sizes.** Final-consumption footprints rise **7 % (Poland) to 48 %
(Brazil)**, up to 57 %; global traded emissions rise 11 %; 45 of 49 regions
widen their consumption-minus-production gap. The result that matters here:
**service multipliers rise most in relative terms**, post and telecommunications
by more than 200 %, real estate by about 200 %, other services 23-110 %. Health
care is a service sector, which is why our +21 % endogenised figure is at the
lower end rather than an outlier. The paper reports no Danish or Nordic values
and does not mention health care.

**How our implementation differs, precisely.** We construct $K(:,j) = g_r(j) \cdot
\text{cfc}_j / x_j$, using each region's own normalised GFCF vector as the commodity
mix. Södersten build $\bar{K}$ from a KLEMS 8-asset × 32-industry base with
proxy-weighted concordances, a generic NACE-average matrix for uncovered
countries, and regionalisation by GFCF import origin. Ours is a coarser
commodity mix applied to the same CFC level; it captures the magnitude but not
the asset composition.

**The published capital matrices are now used.** Zenodo record 7073276,
*Capital use matrices*, CC BY 4.0, ships
`Kbar_exio_v3_8_2_{1995..2020}_cfc_{pxp,pxi}.mat`. The `pxi` file is
(9800, 7987): its columns match our industry dimension, its rows are products.

An earlier draft of this note said adopting it would require running the whole
analysis in product space because the `ixi` distribution ships no supply table.
**That was wrong on both counts.** EXIOBASE v3.8.2 publishes `MRSUT_<year>`
supply-use tables alongside the input-output tables, and Södersten's own SI
describes the required operation: they convert their 9800 × 7987 capital
transaction matrix using *"the industry technology construct … to conform with
the way the A matrix is constructed"*. Applying that construct to the rows
rather than the columns gives the industry-by-industry form directly:

$$q_p = \sum_i V_{p,i} \qquad \text{total output of product } p$$
$$D = V^{\mathsf{T}}\,\hat{q}^{-1} \qquad \text{industry × product market shares}$$
$$\bar{K}_{\text{ixi}} = D\,\bar{K}_{\text{pxi}} \qquad \text{9,800 product rows} \rightarrow \text{7,987 industry rows}$$
$$K = \bar{K}_{\text{ixi}}\,\hat{x}^{-1}$$
$$\mathbf{L}^K = (\mathbf{I} - (\mathbf{A} + K))^{-1} \qquad \text{their eq. 13}$$

$D$ is block diagonal by region by construction, and each of its columns sums to
one, so total capital use by industry is conserved by the mapping, asserted in
code at 1.2×10⁻¹⁴. The augmented inverse verifies at 1.6×10⁻¹⁴.

**Result on the published matrices** (`analysis.capital_endogenised_sodersten`):

| Indicator | Baseline | Endogenised | Change |
|:---|:---|:---|:---|
| Climate change (kt CO₂e) | 4,062 | **4,849** | **+19.4 %** |
| Material extraction (kt) | 4,234 | 5,639 | +33.2 % |
| Blue water (Mm³) | 95.3 | 105.1 | +10.2 % |
| Land use (km²) | 4,854 | 5,823 | +20.0 % |
| Waste generation (kt) | 259.4 | 304.3 | +17.3 % |

This result **validates the simplified construction** reported above, which gave
+21.0 % on climate against the published method's +19.4 %. The two agree to
1.6 percentage points, so the simplified version was adequate for the magnitude
while the published matrices give the asset composition.

One vintage assumption is recorded in the output: the published matrices stop at
2020 and the study year is 2022, so the 2020 capital *structure* is applied to
2022 *levels*. Capital composition moves slowly; the level comes from the model's
own consumption of fixed capital.

A newer record (20762989, 1995-2022 on EXIOBASE v3.10.2) exists but is access-
restricted.

## 5e. A Danish capital anomaly worth reporting

Danish national accounts show that **water transport is the one major Danish
industry where depreciation exceeds investment**: consumption of fixed capital
16,444 m DKK against gross fixed capital formation 11,894 m DKK in 2022. Health
is the reverse (13,125 against 18,888). One would therefore expect capital
endogenisation to load heavily onto Danish shipping, amplifying the
misallocation documented in `shipping_reallocation_method.md`.

**In our model it does the opposite.** EXIOBASE records **zero consumption of
fixed capital for Danish sea and coastal water transport**, against 1,269 M€ for
Danish health. Ships plainly depreciate, so this zero is another symptom of the
broken Danish water-transport block, the same block that carries a negative
value added in EXIOBASE. The practical consequence is that our capital
scenarios **under**-capitalise Danish shipping rather than over-capitalising it,
which is the conservative direction but should be stated.

## 5f. Why the Schmidt & Merciai route was not taken

Their capital treatment is the mirror image of Södersten's: they fix the *level*
at gross fixed capital formation and use consumption of fixed capital as the
distribution *key*, then rebalance iteratively. It is cheaper (no KLEMS) and
conserves yearly global totals exactly, but models no asset composition. Their
Danish 2016 effect is **−1.1 Mt CO₂-eq, −1.6 %** of a 69.2 Mt baseline: a
between-country reallocation, because Denmark exports more capital-intensive
goods than it imports, not a contradiction of Södersten's +7-48 %.

It is not reproducible: the EXIOBASE-hybrid v4 database is not public, the code
repository their documentation cites has been deleted, and the base year is
2016. The capital method itself is a single documented paragraph.

## 6. Recommendation

**Keep the baseline (capital excluded) as the headline**, because that is what
makes the result comparable with Steenmeijer, Eckelman, Lenzen, Pichler, and
Arup, the studies the paper is positioned against. **Report Scenario A as the
headline sensitivity** (it is grounded in Danish national accounts and uses the
correct annual flow) and **Scenario D as the bound**. State explicitly that
Malik et al. 2018's higher Australian share (7.2 %) is partly a capital-boundary
difference, not only a real difference, which materially changes how that
comparison should be read.

## 7. Verification and honest limits

- $(\mathbf{I} - \mathbf{A}')\mathbf{L}' = \mathbf{I}$ verified to $2\times10^{-14}$ on sampled columns; $\mathbf{L}' \ge 0$.
- The spectral radius moves only from 0.97289056 to 0.97289057. This stability is
  **not** evidence that capital is negligible: EXIOBASE's dominant eigenvector is
  concentrated (|v| = 0.997) on *Cultivation of paddy rice*, a near-unit-column
  industry with no capital coefficient. ρ is uninformative here; the inverse
  verification is the meaningful check. Recorded in `capital_diagnostics.csv`.
- The asset→product bridge is coarse and fully stated in `capital_asset_mix.csv`.
  Only the *group* weights come from the Danish asset mix; the split within a
  group comes from the region's GFCF column.
- Scenario D uses EXIOBASE's own CFC for all regions, which for Denmark is
  understated 1.79×; the Danish correction is applied in Scenario A only. D is
  therefore conservative for Denmark.
- Neither scenario endogenises capital in the *bottom-up* items.

## References

- Södersten C-J, Wood R, Hertwich EG (2018) Endogenizing capital in MRIO models:
  the implications for consumption-based accounting. *Environ Sci Technol*
  52(22):13250-13259.
- Wood R, Hertwich EG (2018) *Environ Res Lett* 13:104013.
- Malik A, Lenzen M, McAlister S, McGain F (2018) The carbon footprint of
  Australian health care. *Lancet Planet Health* 2:e27-e35.
- Lenzen M, Malik A, Li M, et al. (2020) The environmental footprint of health
  care. *Lancet Planet Health* 4:e271-e279.
- Statistics Denmark, NABK69, accumulation account and balance sheets.
