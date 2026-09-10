# 05 - Domestic waste from Danish national accounts

**Gold folder** `data/gold/results/05_waste_dst_accounts/`
**Modules** `analysis.waste_domestic_dst`, `analysis.waste_validation`
**Source** Statistics Denmark StatBank AFF1MU1N / AFF3MU1N (IO-based waste multipliers,
117 industries, 2011-2023) and AFFALD01 (SEEA waste accounts)

## Question this layer answers

How much waste does Danish health care actually generate, and is the waste indicator
inherited from Steenmeijer et al. fit to answer that?

## Method

### Why the inherited indicator was tested

The inherited waste extension applies the **2011 hybrid EXIOBASE waste-supply account** to
the analysis year's monetary output. Testing it against Denmark's own SEEA accounts shows
it is not merely out of date but a **different concept**: a total-residuals account in
which livestock manure and mining overburden dominate. 74 % of the Danish total is manure;
69 % of the health-care "waste" footprint is mining overburden plus manure.

| Quantity | Value |
|:---|:---|
| Hybrid extension, direct waste of Danish health | 240.4 kt |
| DST AFFALD01, NACE Q total waste excl. soil | 51.8 kt |
| DST, study boundary (QA + 870000 + α × 880000, α = 0.4914) | 45.1 kt |
| **Ratio, hybrid / measured** | **4.6×** |

It also fails as an allocation key: its 2011 Danish sector structure is statistically
uncorrelated with the measured 2011 structure (Pearson $r = -0.19$). A key that does not
correlate with what it is meant to distribute is not a key.

### The Danish route

Denmark uniquely publishes IO-based waste multipliers on the **same 117-industry
classification as its own IO tables**, which removes the need for a concordance:

$$W_{\text{direct}} = \sum_i d_i \, x_i, \qquad
W_{\text{total}} = \sum_i m_i \, x_i, \qquad
W_{\text{hazardous}} = \sum_i h_i \, x_i$$

with $d_i$ the direct waste intensity (t per M DKK), $m_i$ the direct-plus-indirect
multiplier, and $h_i$ the hazardous multiplier, applied to Danish health-care
expenditure $x_i$ in million DKK.

This route is a **domestic** account by construction: DST's multipliers cover the
Danish economy. It therefore complements, rather than replaces, the MRIO waste
indicator, which covers the global chain. Both are reported.

## Data requirements

| Input | Source |
|:---|:---|
| $d_i$, $m_i$, $h_i$ | DST AFF1MU1N / AFF3MU1N, 2022 |
| $x_i$ | Danish health expenditure by industry, million DKK |
| Validation target | DST AFFALD01, NACE Q |
| α = 0.4914 | share of NACE 88 in the study's eldercare boundary |

## Deviations from the source, stated

- α-proration of NACE 880000 is ours, not DST's; it is the residual risk quantified in the
  Monte Carlo `direct` parameter ([04](04_uncertainty_lenzen_ieooc.md)).
- The MRIO waste indicator is **retained** in the headline for comparability with
  Steenmeijer, with the DST account reported alongside. Replacing it silently would break
  the comparison the study exists to make.

## Outputs

| File | Content |
|:---|:---|
| `waste_footprint_domestic_dst.csv` | per industry: expenditure, three intensities, three waste quantities |
| `waste_extension_validation.csv` | the four rows of the table above, with basis |

## Verification

The hybrid-versus-measured ratio and the $r = -0.19$ correlation are both computed and
written out, so the decision to report the DST account is evidenced rather than asserted.
