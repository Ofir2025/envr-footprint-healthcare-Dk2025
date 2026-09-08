# EXIOBASE weaknesses, and how to read this study's results in light of them

Written to be lifted into the manuscript's *Data*, *Methods* and *Limitations*. Every
weakness below is one we tested on our own model rather than one we inherited from a
reading of the literature; where a number is given, the test that produced it is named.

The honest summary: **EXIOBASE is the right model for this study and it has defects that
change results.** Both halves matter. A limitations section that says only the first is
promotional; one that says only the second invites the reader to discard the work.

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

**What we did.** Reproduced the diagnosis on our own model (73.6 % against their 74 %, to
the decimal) and applied the single reallocation it implies, with the target set to the
national-accounts benchmark rather than fitted. EXIOBASE's own hybrid build gives 7.8 %
natively, so the correction reconstructs an allocation the data already supports by
another route.

**How to read the results.** Danish-origin transport emissions in this study are corrected
and should not be compared with uncorrected EXIOBASE studies of Denmark. Other Danish
industries are **not** individually corrected - only the one row with a published
benchmark and a first-order effect. Treat Danish sectoral detail as indicative and the
Danish aggregate as reliable.

**Recommendation.** Full national-accounts coupling (SNAC, after Palm et al. 2019) would
remove the remaining allocation error. It is scoped in `dk_snac_feasibility.md` and is the
single most valuable methodological upgrade available to this study.

---

## 2. Vintage defects are real, version-specific, and invisible to a balance check

We tested every vintage on disk against Statistics Denmark's own table, year by year. Two
defects, with different onsets:

| Defect | What breaks | Onset in v3.10.2 | v3.8.2 / v3.6 |
|---|---|---|---|
| **D1** | medical, precision and optical instruments carry ~zero output across Europe (28 of 30 regions) | **2015**, and never recovers | clean (0 of 30) |
| **D2** | Danish output redistributed; 9 of 12 concordance groups off by more than 2× | **2021-2022**, the nowcast years | clean (2 of 12) |

**Why a routine check misses them.** Danish output still totals to within 3 % and the
table still balances to 10⁻¹¹. Output was *redistributed*, not lost. The decisive test
needed no external source: Danish health final expenditure is 40,597 M€, and a health
industry with 16,326 M€ of *total output* cannot deliver it.

**How to read the results.** This study uses **v3.8.2**, which passes both tests. Our
results are therefore not comparable, industry by industry, with studies built on v3.10.2
from 2015 onward - and the difference is a data defect, not a modelling choice.

**Recommendation for the field.** Anyone using v3.10.2 for a European study from 2015
should check industry 33 before trusting sectoral results, and anyone using a nowcast year
should check the national block against national accounts. Neither check is standard
practice; both should be. `analysis.vintage_defect_audit` is a reusable implementation.

---

## 3. One health industry, so no genuine sub-sector detail

EXIOBASE's `ixi` layout has a **single** health and social work industry. Malik et al.
(2021) and Lenzen et al. (2020) report sub-sector detail because their MRIOs inherit it
from national tables; neither method is reproducible here.

**What we did.** Implemented the one route that is reproducible - Malik et al.'s (2018)
output-prorated concordance - and then published its decomposition rather than its ranking
alone. Five SHA functions carry only **three distinct intensities**, and **99.99 %** of the
variation across functions is explained by expenditure alone.

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

**How to read the results.** The pharmaceutical footprint - 4.8 % of spend, 36.6 % of the
function total - is the number in this study most exposed to price heterogeneity, and it is
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

**Recommendation.** IMPACT World+ v2.2.1 is current, openly licensed and aligned to the
EXIOBASE v3.8.2 stressor list; it is computed alongside DESIRE and should displace it for
water scarcity, land biodiversity and mineral resources.

---

## 6. No published parameter uncertainty

EXIOBASE ships no element-level standard deviations. Our Monte Carlo therefore calibrates
MRIO uncertainty to Lenzen et al.'s published 8.35 % for this exact quantity and applies it
as a single joint factor - correlation ρ = 1, the conservative bound.

**How to read the interval.** The reported 95 % interval, 4,064-5,540 kt, is **parametric
uncertainty conditional on one model**. It is not a confidence interval on "the" Danish
health footprint. Our own change of EXIOBASE vintage moved the result by more than this
interval spans, and Tukker et al. warn that national error statistics do not transfer to
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

## What this means for a reader of the paper

1. **Trust the aggregate, qualify the sectoral detail.** The Danish health footprint and
   its domestic/imported split rest on corrected, benchmarked quantities. Industry-level
   Danish detail rests on an estimated national block.
2. **Read every share with its basis.** Transport is 18.5 % of the supply chain and 15.4 %
   of the total; both are correct and they are not interchangeable.
3. **Treat the uncertainty interval as conditional.** Model choice moves the answer more
   than the parameters do.
4. **Do not compare across EXIOBASE vintages** without checking the defects in §2.
