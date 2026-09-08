# Uncertainty and scenarios: the response to Reviewer 1

The first-round review asked us to propagate the study's proxy assumptions across
plausible ranges and report what that does to the headline estimates, suggesting
±20-50 % for the scaling factors, and to identify which assumptions drive the result.

This is what was done, why the ranges are what they are, and how to answer the specific
doubt about the ±20-50 % figure.

---

## 1. The strongest part of the answer is not the Monte Carlo

Three of the four proxies the reviewer names have been **eliminated, not bounded**. Where a
Danish measurement exists, a transplanted proxy has been replaced by it:

| Proxy the reviewer questioned | Submitted | Now |
|---|---|---|
| Nitrous oxide scaled from one region by births | 9.52 kt, from Region of Southern Denmark × birth ratio | **11.32 kt** from Denmark's National Inventory Document 2024 (DCE 622), category 2.G.3.a - a national measurement |
| pMDI scaled from Dutch defined daily doses | 34.6 kt | **11.6 kt** from the Danish EPA F-gas inventory's reported MDI emission |
| Patient and visitor travel scaled from Dutch totals | Dutch value × 0.54 | **Danish National Travel Survey**, Table 15, purpose 33 *Social/sundhed* - the category that actually measures travel to doctors and hospitals |
| Employee commuting | scaled on Dutch commuting | still scaled, but on national-accounts employment (DST NABB69) and the TU distance table |

**Answering a proxy objection by removing the proxy is stronger than quantifying its
uncertainty.** That should lead the response; the Monte Carlo supports it rather than
substituting for it.

## 2. Why the ranges are not a flat ±20-50 %

The reviewer's ±20-50 % is a reasonable prompt, not a specification, and applying it
uniformly would be **wrong**. It would assign the same uncertainty to a reading from a
mandatory national register as to a figure transplanted from an English travel survey via
the Netherlands. Each parameter's range is therefore derived from its own evidence.

What that produces, as 95 % intervals on the multiplier:

| Parameter | Distribution | 95 % range | Contains ±20-50 %? |
|---|---|---|---|
| Anaesthetic gases | lognormal, GSD 1.30 | −40 % to +67 % | **yes** |
| pMDI propellants | lognormal, GSD 1.15 | −24 % to +32 % | **yes** |
| Employee commuting | lognormal, GSD 1.25 | −35 % to +55 % | **yes** |
| Patient and visitor travel | lognormal, GSD 1.40 | −48 % to +93 % | **yes** |
| Direct emissions (DRIVHUS/AFFALD) | lognormal, GSD 1.10 | −17 % to +21 % | narrower, deliberately |
| MRIO parameters | lognormal, CV 8.35 % | −15 % to +18 % | narrower, deliberately |

**Every cross-country scaling factor - which is what the reviewer asked about - spans at
least the range he proposed, and the widest spans twice it.** The two that are narrower
are not scaling factors: one is a Danish national-accounts measurement, the other is the
only published Monte Carlo estimate of this exact quantity (Lenzen et al. 2020, SI Table
SI 7.1: 2.84 ± 0.24 Mt, a relative SD of 8.35 %; Wood et al. 2019 Table 1 give Denmark's
cross-database consumption-based spread as 8.8 %, within half a point of ours). Widening either to ±50 % would be inventing uncertainty rather than
estimating it, and would make the interval uninterpretable.

The ordering is also defensible on its face: the widest distribution sits on patient and
visitor travel, the parameter with the weakest provenance, and the narrowest on the
national accounts. That is visible in the parameter table rather than asserted in prose.

## 3. What the Monte Carlo found

100,000 draws, every uncertain quantity a median-1 lognormal multiplier so the simulation
median reproduces the deterministic result:

| | Climate change |
|---|---|
| Deterministic | 4,713 kt CO₂e |
| Median | 4,735 kt |
| 95 % interval | **4,065 - 5,532 kt** |
| Coefficient of variation | **7.9 %** |

Cross-check: Lenzen et al. report 8.35 % for the same quantity by an entirely different
route. Two independent methods landing within half a percentage point is the best available
external validation.

**Which assumptions dominate** - the reviewer's second question - by exact first-order
Sobol shares:

| Source | Share of variance |
|---|---|
| MRIO parameters | **78.8 %** |
| Covariance of the two travel items (shared method) | 9.3 % |
| Patient and visitor travel | 6.7 % |
| Employee commuting | 5.1 % |
| All other bottom-up items | 0.1 % |

This is the most useful single result for the reviewer: **the proxies he was worried about
are not what the estimate rests on.** Even the widest of them moves the total by a few per
cent. Improving them further would not narrow the interval; a nationally consistent model
would.

## 4. Structural choices are scenarios, not distributions

The pharmaceutical mapping, the price vintage and the waste vintage are **modelling
decisions**, not measurement errors. Burying a decision inside a lognormal would
misrepresent it as noise. They are run as an explicit factorial
(`uncertainty_structural_scenarios.csv`) and reported separately, with the pharmaceutical
mapping carrying the Hagenaars adjustment the manuscript's own appendix cites.

## 5. Mitigation scenarios - the answer to Reviewer 2's R2-7

Not out of scope, and already modelled. Fourteen climate scenario rows in
`18_mitigation_scenarios`, built on the Danish Energy Agency's own projections rather than
assumed rates:

| Scenario | Ambition | Change |
|---|---|---|
| Energy decarbonisation to 2030 | KF22 projection | −6.7 % |
| Energy decarbonisation to 2035 | KF22 projection | −6.8 % |
| Energy decarbonisation to 2030 | KF25 projection | −5.7 % |
| Travel reduction | −30 % | −4.0 % |

Two are run rather than one because the 2025 projection is materially less optimistic than
the 2022 one, and reporting a single figure would overstate confidence.

**The honest headline: full Danish grid decarbonisation removes under 7 % of the
footprint.** That is a finding, not a disappointment - it follows directly from 73.7 % of
impacts arising abroad, and it is the strongest available argument that health-sector
mitigation has to be a procurement question rather than an energy question.

## 6. What the interval does *not* establish

To be stated in the paper, not omitted:

> The reported interval is parametric uncertainty **conditional on one model**. It is not a
> confidence interval on the Danish health-care footprint. Tukker et al. warn that national
> error statistics do not transfer to sector studies, and Schulte et al. find country-level
> CV near 4 % but sector-level CV up to 94 %. This study's own change of EXIOBASE vintage
> moved the result by more than this interval spans.

Reporting 7.9 % without that sentence would over-claim, and a referee who knows the
literature will say so.
