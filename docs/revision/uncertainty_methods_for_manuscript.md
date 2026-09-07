# Uncertainty analysis — methods text for the manuscript

**For Ofir.** This is written so it can be lifted into the Methods and Results
with light editing. Everything here is reproducible from
`analysis.uncertainty_2025`; the tables are in
`data/gold/results/04_uncertainty_lenzen_ieooc/`.

It answers Reviewer 1's central request — *"a systematic sensitivity analysis or
Monte Carlo simulation that varies the key proxy assumptions within plausible
ranges… and reports the resulting ranges"* — and Reviewer 2's related request
for uncertainty on the bottom-up parameters.

---

## 1. Methods text (draft)

> **Uncertainty analysis.** Parameter uncertainty was propagated by Monte Carlo
> simulation with 100,000 draws. Each uncertain quantity enters as a
> multiplicative factor drawn from a lognormal distribution with **median 1**, so
> that the simulation median reproduces the deterministic estimate and the
> analysis adds dispersion without shifting the central value. Lognormal
> multipliers are the standard choice for input–output uncertainty propagation
> (Lenzen et al., 2010) because impact estimates are products of non-negative
> quantities and are consequently right-skewed.
>
> Six parameters were treated as stochastic (Table X). Five are bottom-up items,
> assigned geometric standard deviations reflecting the quality of their
> underlying source: direct operational emissions and waste from national
> accounts (GSD 1.10), pMDI propellants (1.15), employee commuting (1.25),
> anaesthetic gases (1.30) and patient and visitor travel (1.40). The sixth
> represents uncertainty in the multi-regional input–output model itself,
> calibrated to a relative standard deviation of **8.35 %** — the value Lenzen
> et al. (2020, supplementary table 7.1) obtain for the Danish health-care
> greenhouse-gas footprint from a full Monte Carlo over the transaction,
> satellite and final-demand matrices, and the only published uncertainty
> estimate for this exact quantity. It is independently corroborated by Wood et
> al. (2019), who compare five multi-regional input–output databases and report
> a relative standard deviation of 8.8 % for the Danish consumption-based
> account.
>
> Employee commuting and patient and visitor travel share a common method and
> are therefore drawn with correlation ρ = 0.8; results for ρ ∈ {0, 0.5, 0.8}
> are reported.
>
> **Structural choices are not treated as parameter uncertainty.** The
> pharmaceutical sector mapping, the price vintage and the waste-account vintage
> are modelling decisions, not noisy measurements, and are reported as discrete
> scenarios. Representing a structural choice as a distribution would
> misrepresent a decision as measurement error.
>
> First-order Sobol indices were computed in closed form to attribute output
> variance to individual parameters, and simulation moments were verified
> against the analytic moments of the lognormal sum.

## 2. Results text (draft)

> The Monte Carlo median for the Danish health-care climate footprint is
> **4,736 kt CO₂e** with a 95 % interval of **4,064–5,540 kt** and a coefficient
> of variation of **7.9 %**, closely consistent with the 8.35 % that Lenzen et
> al. (2020) report for the same quantity.
>
> Variance attribution is more informative than the interval alone. **The
> multi-regional input–output model contributes 86.8 % of the output variance**;
> patient and visitor travel 7.4 %; employee commuting 5.7 %; and every
> remaining bottom-up item **less than 0.2 %**. The proxy assumptions that
> motivated the reviewers' concern are therefore not what the estimate rests on
> — the estimate rests on the input–output model. This also means that
> improving the bottom-up items further would not materially narrow the
> interval, whereas a nationally consistent input–output model would.
>
> Under the alternative pharmaceutical mapping the median falls to **3,608 kt**
> with a wider coefficient of variation of 10.7 %, and the identity of the
> largest contributing group changes (§ pharmaceutical mapping).

## 3. Three properties we state explicitly

A referee may otherwise raise these, and each is now reported.

**(a) The input–output factor is perfectly correlated across contribution
groups.** Applying one shared multiplier is the ρ = 1 case. Rodrigues et al.
(2018) measure correlations of 0.63 ± 0.36 (median 0.76) between country
consumption-based accounts, and show that assuming *independence* understates
uncertainty by roughly half. We report all three:

| Correlation across groups | CV | 95 % interval (kt) |
|---|---|---|
| ρ = 1.00 — perfect (reported default) | **7.9 %** | 4,057–5,546 |
| ρ = 0.76 — Rodrigues et al.'s measured median | 7.3 % | 4,114–5,477 |
| ρ = 0.00 — independence | 5.2 % | 4,315–5,274 |

The default is the widest and therefore cannot understate the interval.

**(b) Median-1 lognormal multipliers have mean exp(σ²/2) > 1.** The simulated
mean sits marginally above the deterministic estimate by construction. The
inflation is **+0.35 %**, immaterial here but stated.

**(c) First-order Sobol indices exclude interaction variance.** In this additive
model they sum to **100.0 %**, so the first-order decomposition is complete and
no interaction mass is hidden.

## 4. What this analysis does *not* establish — a limitation to state

This paragraph is written for the Limitations section. It matters: without it,
the reported interval is easy to over-read.

> **Scope of the uncertainty estimate.** The interval reported here is
> *parametric* uncertainty conditional on one input–output model. It does not
> capture structural or model-choice uncertainty: the effect of using a
> different global database, a different construct, or a nationally consistent
> table. Tukker et al. (2020) caution that *"analyses at the national level are
> much more forgiving than comparative analyses on product group level, since
> aggregation to the national level tends to iron out negative and positive
> differences at product group level"* — so published national error statistics,
> including the 8.35 % used to calibrate our input–output factor, should not be
> assumed to transfer unchanged to a single sector. Schulte et al. (2024) find
> median coefficients of variation of about 4 % for country-level CO₂ accounts
> but **94 % at sector level**, and show that the *choice* of emission-account
> source can place a value more than three times outside the parametric 95 %
> interval. Our own vintage comparison is a direct demonstration: replacing the
> background release changed the Danish health-care climate footprint by far
> more than the parametric interval spans. The interval should therefore be read
> as the precision of this model, not as the accuracy of the estimate.

## 5. Parameter table for the supplementary information

| Parameter | Distribution | GSD / CV | 95 % factor range | Source and residual risk |
|---|---|---|---|---|
| Input–output model | lognormal, median 1 | CV 8.35 % | 0.85–1.18 | Lenzen et al. (2020) SI table 7.1, Danish health-care GHG footprint; applied jointly to all MRIO components |
| Direct operational | lognormal, median 1 | GSD 1.10 | 0.83–1.21 | Statistics Denmark DRIVHUS and AFFALD01; residual risk is the eldercare proration and the medical-N₂O netting |
| pMDI propellants | lognormal, median 1 | GSD 1.15 | 0.76–1.32 | Danish EPA F-gas inventory; register dispensing × producer HFC content |
| Employee commuting | lognormal, median 1 | GSD 1.25 | 0.65–1.55 | Ratio method on Danish employment (DST) and travel-survey distances |
| Anaesthetic gases | lognormal, median 1 | GSD 1.30 | 0.60–1.67 | Danish NID 2.G.3.a activity ±25 %, emission factor ±20 % |
| Patient and visitor travel | lognormal, median 1 | GSD 1.40 | 0.52–1.93 | Danish national travel survey; the visitor component has no Danish source |

## References

- Lenzen M, Wood R, Wiedmann T (2010) Uncertainty analysis for multi-region
  input–output models. *Economic Systems Research* 22(1):43–63.
- Lenzen M, Malik A, Li M, et al. (2020) The environmental footprint of health
  care. *Lancet Planetary Health* 4:e271–e279 (SI table 7.1).
- Rodrigues JFD, Moran D, Wood R, Behrens P (2018) Uncertainty of consumption-
  based carbon accounts. *Environmental Science & Technology* 52:7577–7586.
- Schulte S, Jakobs A, Pauliuk S (2024) Uncertainty in greenhouse gas emission
  accounts. *Earth System Science Data* 16:2669–2700.
- Tukker A, Wood R, Schmidt S (2020) Towards accepted procedures for calculating
  international consumption-based carbon accounts. *Climate Policy*
  20(sup1):S90–S106.
- Wood R, Neuhoff K, Moran D, et al. (2019) The structure, drivers and policy
  implications of the European carbon footprint. *Scientific Data* 6:99.
