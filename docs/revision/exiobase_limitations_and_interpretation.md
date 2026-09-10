# EXIOBASE: every limitation this study is exposed to, and how to read the results

This document is written to be lifted into the manuscript's *Data*, *Methods*,
and *Limitations* sections.
Each entry follows the same three-part structure the discipline requires of a
limitation: **what it is**, **what it changes about the conclusion**, and **what
study design would reduce it**. A limitation named without its consequence is
not a limitation; it is a disclaimer.

Every weakness below was tested on this model rather than inherited from a
reading of the literature. Where a number is given, the test that produced it is
named. Where a weakness is known from the literature but not measured here, that
is stated in those words.

The honest summary is two-sided, and both halves matter. **EXIOBASE is the right
model for this study, and it has defects that change results.** A limitations
section that says only the first is promotional; one that says only the second
invites the reader to discard the work.

Uncertainty sources are treated separately and in full in
[`uncertainty_sources.md`](uncertainty_sources.md); this document covers the
properties of the database itself.

---

## 1. The Danish block is not the Danish national accounts

**What is wrong.** EXIOBASE's national blocks are estimated, not adopted from each
country's own supply-and-use tables. For Denmark this produces two measurable errors.

*Sea transport.* EXIOBASE sends **73.6 %** of Danish water-transport output to Danish
intermediate use; the Danish national accounts say **9 %**. Denmark operates one of the
world's largest merchant fleets, and that fleet carries world trade, not Danish
production. Uncorrected, this loads a global fleet's emissions onto Danish consumption:
transport appears as 37.5 % of the health-care supply-chain footprint instead of 18.5 %,
and the Danish national footprint as 85.2 Mt instead of 77.5 Mt.

*Industry allocation more generally.* Rørmose Jensen & Iliev (2022) show the Danish block
misallocates output between industries, which is why Statistics Denmark rebuild it rather
than patch it.

**What we did.** We reproduced the diagnosis on our own model (73.6 % against their 74 %, to
the decimal) and applied the single reallocation it implies, with the target set to the
national-accounts benchmark rather than fitted. EXIOBASE's own hybrid build gives 7.8 %
natively, so the correction reconstructs an allocation the data already supports by
another route.

**How to read the results.** Danish-origin transport emissions in this study are corrected
and should not be compared with uncorrected EXIOBASE studies of Denmark. Other Danish
industries are **not** individually corrected: the correction covers only the one
row with a published benchmark and a first-order effect. Treat Danish sectoral detail as
indicative and the Danish aggregate as reliable.

**Recommendation.** Full national-accounts coupling (SNAC, after Palm et al. 2019) would
remove the remaining allocation error. It is scoped in `dk_snac_feasibility.md` and is the
single most valuable methodological upgrade available to this study.

---

## 2. Vintage defects are real, version-specific, and invisible to a balance check

We tested every vintage on disk against Statistics Denmark's own table, year by year. Two
defects appeared, with different onsets:

| Defect | What breaks | Onset in v3.10.2 | v3.8.2 / v3.6 |
|---|---|---|---|
| **D1** | medical, precision and optical instruments carry ~zero output across Europe (28 of 30 regions) | **2015**, and never recovers | clean (0 of 30) |
| **D2** | Danish output redistributed; 9 of 12 concordance groups off by more than 2× | **2021-2022**, the nowcast years | clean (2 of 12) |

**Why a routine check misses them.** Danish output still totals to within 3 %, and the
table still balances to 10⁻¹¹. Output was *redistributed*, not lost. The decisive test
needed no external source: Danish health final expenditure is 40,597 M€, and a health
industry with 16,326 M€ of *total output* cannot deliver it.

**How to read the results.** This study uses **v3.8.2**, which passes both tests. Our
results are therefore not comparable, industry by industry, with studies built on v3.10.2
from 2015 onward, and the difference is a data defect, not a modelling choice.

**Recommendation for the field.** Anyone using v3.10.2 for a European study from 2015
should check industry 33 before trusting sectoral results, and anyone using a nowcast year
should check the national block against national accounts. Neither check is standard
practice; both should be. `analysis.vintage_defect_audit` is a reusable implementation.

---

## 3. One health industry, so no genuine sub-sector detail

EXIOBASE's `ixi` layout has a **single** health and social work industry. Malik et al.
(2021) and Lenzen et al. (2020) report sub-sector detail because their MRIOs inherit it
from national tables; neither method is reproducible here.

**What we did.** We implemented the one route that is reproducible, namely Malik et al.'s
(2018) output-prorated concordance, and then published its decomposition rather than its
ranking alone. Five SHA functions carry only **three distinct intensities**, and
**99.99 %** of the variation across functions is explained by expenditure alone.

**How to read the results.** The services / pharmaceuticals / appliances split is a genuine
intensity finding. The ordering *within* the three service functions is an expenditure
ranking and carries no supply-chain information. Do not quote hospital-versus-outpatient
intensity differences from this study; there are none to quote.

**Recommendation.** The Danish 117-industry table resolves hospitals separately. Genuine
per-function recipes need it.

---

## 4. Monetary homogeneity, and what it does to pharmaceuticals

Every EXIOBASE industry is assumed to sell a homogeneous product at a uniform price, so a
euro of "Chemicals nec" carries the same intensity whether it buys a generic paracetamol or
a patented biologic. Pharmaceutical prices are far from cost-reflective.

**How to read the results.** The pharmaceutical footprint (4.8 % of spend, 36.6 % of the
function total) is the number in this study most exposed to price heterogeneity, and it is
**probably an overestimate** if Danish pharmaceutical prices carry above-average margins.
The Monte Carlo treats the mapping as a structural scenario, not a distribution, precisely
because it is a modelling choice rather than measurement error.

---

## 5. The satellite account constrains what can be characterised

HFC and PFC arrive **already aggregated in kg CO₂-equivalent**, on an unrecoverable GWP
vintage, so they cannot be restated on AR6; their share is reported rather than hidden.
The DESIRE characterisation workbook is 2014-vintage: three of its rows failed our tests
(an endpoint identical to its own midpoint, a photochemical endpoint two orders of
magnitude from its published damage factor, an SF₆ factor matching no IPCC assessment) and
**ozone depletion was retracted** on that basis.

**Recommendation.** IMPACT World+ v2.2.1 is current, openly licensed, and aligned to the
EXIOBASE v3.8.2 stressor list; it is computed alongside DESIRE and should displace it for
water scarcity, land biodiversity, and mineral resources.

---

## 6. No published parameter uncertainty

EXIOBASE ships no element-level standard deviations. Our Monte Carlo therefore calibrates
MRIO uncertainty to Lenzen et al.'s published 8.35 % for this exact quantity and applies it
as a single joint factor: correlation ρ = 1, the conservative bound.

**How to read the interval.** The reported 95 % interval, 4,064 to 5,531 kt, is **parametric
uncertainty conditional on one model**. The interval is not a confidence interval on "the"
Danish health footprint. Our own change of EXIOBASE vintage moved the result by more than
this interval spans, and Tukker et al. warn that national error statistics do not transfer to
sector studies. Report the interval and this sentence together, or not at all.

---

## 7. Boundary conventions that are choices, not facts

| Convention | This study | Effect if changed |
|---|---|---|
| Capital | excluded from the headline | +19.4 % (Södersten endogenisation) |
| Sector boundary | health + eldercare | +12 % on NACE Q incl. childcare |
| Scope 2 | Hertwich & Wood full-multiplier | −2.2 % on the GHG-Protocol strict form |
| Waste | MRIO extension retained for comparability | the Danish account is 4.6× lower |

None of these is wrong; each is a convention that must be stated with the number. The
boundary-matched benchmark in `06_benchmarks_validation` shows what happens when they are
matched to a comparator: agreement with Schmidt & Merciai improves from 25 % apart to
**1.7 %**.

---

## 8. Import proportionality: who buys the imports is assumed, not observed

**What it is.** EXIOBASE does not know which Danish industry buys which imported
product. It distributes each imported commodity across purchasing industries in
proportion to their use of the domestic equivalent. Nothing in the source data
supports that proportionality; it is a modelling necessity.

**What it changes about the conclusion.** Schulte et al. (2021) randomised this
assumption on EXIOBASE at exactly this study's resolution and found national
footprints insensitive to it, with coefficients of variation generally below 4 per
cent, but industry-level footprints far less so: a quarter of industries exceeded 10
per cent for carbon and 30 per cent for land, material, and water, with extreme
cases above 300 per cent. Read across to this study, the **health-care total is
safe from this assumption, and the contribution-group split is softer than its
point estimates suggest.** Import proportionality is a second reason, alongside
the single health industry, not to quote group-level differences finely.

**What would reduce it.** Firm-level or customs-linked import data by purchasing
industry would reduce it. None exists for Denmark at this resolution.

---

## 9. Within-sector homogeneity: one intensity for every firm in an industry

**What it is.** Every firm in an EXIOBASE industry is assumed to produce the same
product with the same technology and the same impact intensity. A Danish
manufacturer of generic paracetamol and a manufacturer of a patented biologic
are one row.

**What it changes about the conclusion.** Rodrigues et al. (2018) report a
within-sector coefficient of variation of carbon per unit output above one for
17 of 23 Japanese manufacturing sectors. Schulte et al. (2024) state the
consequence exactly: their uncertainty estimates are on the *mean* emissions of
a sector, and within-sector variability may be substantially larger. Since
pharmaceuticals are 37 per cent of this study's climate footprint and 51 per
cent of its material footprint, and since hospitals buy a narrow and atypical
slice of the chemicals sector, **the pharmaceutical figure carries more
uncertainty than any interval reported here shows, and the direction of the bias
is unknown.**

**What would reduce it.** Product-level or firm-level intensity data for the
specific pharmaceuticals purchased would reduce it, as would a hybrid model in
which the pharmaceutical column is replaced by process data.

---

## 10. The reference year is a nowcast, not a benchmark table

**What it is.** EXIOBASE's 2022 table is projected forward from the most recent
benchmark year rather than compiled from a 2022 supply-and-use table, because
no country has published one.

**What it changes about the conclusion.** Nowcast years carry the errors this
study documents in section 2, and Lenzen et al. (2010) observe that uncertainty
grows with distance from the benchmark year, although they did not prove it.
This growth in uncertainty is why the vintage tests in section 2 were run at all,
and why v3.10.2 was rejected: its nowcast years fail against the Danish national accounts.
**Sectoral detail for 2022 should be read as less firm than the same detail for
a benchmark year would be.**

**What would reduce it.** Statistics Denmark's own 2022 supply-and-use table,
coupled to the global model, would reduce it. That coupling is the SNAC route.

---

## 11. Correlation between elements is not published, and cannot be assumed away

**What it is.** EXIOBASE publishes no covariance information for its cells. A
user who wants to propagate uncertainty must therefore assume a correlation
structure, and Rodrigues (2016) proves the two convenient assumptions
(uncorrelated elements, and a known aggregate uncertainty) are mutually
exclusive.

**What it changes about the conclusion.** The missing covariance information
means that no reported interval for an EXIOBASE result can be simultaneously
calibrated and independence-based, and a study that reports one without saying
which it chose is reporting an artefact.
This study holds the calibration and varies the correlation, and reports what
that does; see `uncertainty_sources.md` section 3.3.

**What would reduce it.** Schulte et al. (2024) published greenhouse-gas
accounts at exactly this resolution with element-level uncertainties **and**
correlations attached. Adopting them is the single most valuable methodological
upgrade available to this study after SNAC coupling.

---

## 12. Waste, water, and land extensions are weaker than the greenhouse-gas one

**What it is.** The greenhouse-gas extension is built from energy balances and
national inventories and is the most scrutinised part of the satellite account.
The material, water, land, and waste extensions rest on thinner source data and
have received far less validation in the literature.

**What it changes about the conclusion.** Every uncertainty statement in this
study is calibrated on a **carbon** figure. Schulte et al. (2021) find
industry-level footprint dispersion roughly three times higher for land, material,
and water than for carbon on this same database. The four non-carbon categories
are therefore reported with intervals that are **too narrow, by an unknown
factor**, and a bounding run at three times the carbon spread is reported
alongside them for that reason.

**What would reduce it.** A per-category uncertainty assessment of the EXIOBASE
extensions would reduce it. None exists. This absence is a gap in the field, not
only in this study.

---

## What this means for a reader of the paper

1. **Trust the aggregate, qualify the sectoral detail.** The Danish health-care
   footprint and its domestic and imported split rest on corrected, benchmarked
   quantities. Industry-level Danish detail rests on an estimated national
   block, an assumed import allocation, and a homogeneous-sector assumption, and
   three separate limitations above converge on the same advice.
2. **Read every share with its basis.** Transport is 18.5 per cent of the supply
   chain and 15.4 per cent of the total; both are correct, and they are not
   interchangeable.
3. **Treat the uncertainty interval as conditional.** Model choice moves the
   answer more than the parameters do. This study's own structural scenario on
   the pharmaceutical mapping lands entirely outside its parametric 95 per cent
   interval, which is the clearest possible demonstration.
4. **Do not compare across EXIOBASE vintages** without checking the defects in
   section 2.
5. **Do not read the non-carbon categories with the carbon interval.** Section
   12 explains why, and the bounding run is reported for that purpose.

---

## References

Full entries with DOIs are in [`docs/references.md`](../references.md).

- Lenzen, M., Wood, R., & Wiedmann, T. (2010). Uncertainty analysis for
  multi-region input-output models. *Economic Systems Research, 22*(1), 43-63.
  https://doi.org/10.1080/09535311003661226
- Rodrigues, J. F. D. (2016). Maximum-entropy prior uncertainty and correlation
  of statistical economic data. *Journal of Business & Economic Statistics,
  34*(3), 357-367. https://doi.org/10.1080/07350015.2015.1038545
- Rodrigues, J. F. D., Moran, D., Wood, R., & Behrens, P. (2018). Uncertainty of
  consumption-based carbon accounts. *Environmental Science & Technology,
  52*(13), 7577-7586. https://doi.org/10.1021/acs.est.8b00632
- Schulte, S., Jakobs, A., & Pauliuk, S. (2021). Relaxing the import
  proportionality assumption in multi-regional input-output modelling. *Journal
  of Economic Structures, 10*, 20. https://doi.org/10.1186/s40008-021-00250-8
- Schulte, S., Jakobs, A., & Pauliuk, S. (2024). Estimating the uncertainty of
  the greenhouse gas emission accounts in global multi-regional input-output
  analysis. *Earth System Science Data, 16*(6), 2669-2700.
  https://doi.org/10.5194/essd-16-2669-2024
- Stadler, K., Wood, R., Bulavskaya, T., Södersten, C.-J., Simas, M., Schmidt,
  S., Usubiaga, A., Acosta-Fernández, J., Kuenen, J., Bruckner, M., Giljum, S.,
  Lutter, S., Merciai, S., Schmidt, J. H., Theurl, M. C., Plutzar, C., Kastner,
  T., Eisenmenger, N., Erb, K.-H., de Koning, A., & Tukker, A. (2018).
  EXIOBASE 3. *Journal of Industrial Ecology, 22*(3), 502-515.
  https://doi.org/10.1111/jiec.12715
- Tukker, A., Wood, R., & Schmidt, S. (2020). Towards accepted procedures for
  calculating international consumption-based carbon accounts. *Climate Policy,
  20*(sup1), S90-S106. https://doi.org/10.1080/14693062.2020.1722605
