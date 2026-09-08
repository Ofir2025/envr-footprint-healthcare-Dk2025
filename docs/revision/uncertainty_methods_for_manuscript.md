# Uncertainty analysis: methods text for the manuscript

> **If you want the method itself explained rather than the text to publish,
> read `monte_carlo_explained.md` first.** It derives every equation used here
> from first principles, names every symbol in plain English, and works one
> complete draw through by hand. This file is the prose to lift into the paper;
> that one is why the prose is true.

**For Ofir.** This text is written so it can be lifted into the Methods and
Results with light editing. Everything here is reproducible from
`analysis.uncertainty_2025`; the tables are in
`data/gold/results/04_uncertainty_lenzen_ieooc/`.

It answers the first-round review's central request (propagate the proxy
assumptions and report what that does to the headline estimates) and the second
reviewer's related request for uncertainty on the bottom-up parameters.

---

## 1. Methods text (draft)

> **Uncertainty analysis.** Parameter uncertainty was propagated by Monte Carlo
> simulation with 100,000 draws. Each uncertain quantity enters as a
> multiplicative factor drawn from a lognormal distribution with **median 1**, so
> that the simulation median reproduces the deterministic estimate and the
> analysis adds dispersion without shifting the central value. Lognormal
> multipliers are the standard choice for input-output uncertainty propagation
> (Lenzen et al., 2010) because impact estimates are products of non-negative
> quantities and are consequently right-skewed.
>
> Six parameters were treated as stochastic (Table X). Five are bottom-up items,
> assigned geometric standard deviations reflecting the quality of their
> underlying source: direct operational emissions and waste from national
> accounts (GSD 1.10), pMDI propellants (1.15), employee commuting (1.25),
> anaesthetic gases (1.30), and patient and visitor travel (1.40). The sixth
> represents uncertainty in the multi-regional input-output model itself,
> calibrated to a relative standard deviation of **8.35 %**, the value Lenzen
> et al. (2020, SI table 7.1) obtain for the Danish health-care
> greenhouse-gas footprint from a full Monte Carlo over the transaction,
> satellite, and final-demand matrices, and the only published uncertainty
> estimate for this exact quantity.
>
> Employee commuting and patient and visitor travel share a common method and
> are therefore drawn with correlation ρ = 0.8; results for ρ ∈ {0, 0.5, 0.8}
> are reported.
>
> **Structural choices are not treated as parameter uncertainty.** The
> pharmaceutical sector mapping, the price vintage, and the waste-account
> vintage are modelling decisions, not noisy measurements, and are reported as
> discrete scenarios. Representing a structural choice as a distribution would
> misrepresent a decision as measurement error.
>
> First-order Sobol indices were computed in closed form to attribute output
> variance to individual parameters, and simulation moments were verified
> against the analytic moments of the lognormal sum.

## 2. Results text (draft)

> The Monte Carlo median for the Danish health-care climate footprint is
> **4,734 kt CO₂e** with a 95 % interval of **4,064 to 5,531 kt** and a
> coefficient of variation of **7.87 %**, closely consistent with the 8.35 % that Lenzen et
> al. (2020) report for the same quantity.
>
> Variance attribution is more informative than the interval alone. **The
> multi-regional input-output model contributes 78.8 % of the output variance**;
> patient and visitor travel 6.7 %; employee commuting 5.1 %; the covariance of
> those two, which share a method, a further 9.3 %; and every remaining
> bottom-up item **less than 0.1 %**. The proxy assumptions that
> motivated the reviewers' concern are therefore not what the estimate rests on:
> the estimate rests on the input-output model. This attribution also means that
> improving the bottom-up items further would not materially narrow the
> interval, whereas a nationally consistent input-output model would.
>
> Under the alternative pharmaceutical mapping the median falls to **3,605 kt**
> with a wider coefficient of variation of 10.7 %, and the identity of the
> largest contributing group changes (§ pharmaceutical mapping).

## 3. Three properties we state explicitly

A referee may otherwise raise these, and each is now reported.

**(a) The input-output factor is perfectly correlated across contribution
groups.** Applying one shared multiplier is the ρ = 1 case. Rodrigues et al.
(2018) measure correlations of 0.63 ± 0.36 (median 0.76) between country
consumption-based accounts, and show that assuming *independence* understates
uncertainty by roughly half. We report all three:

| Correlation across groups | CV | 95 % interval (kt) |
|---|---|---|
| ρ = 1.00, perfect (reported default) | **7.85 %** | 4,068 to 5,527 |
| ρ = 0.76, Rodrigues et al.'s measured median | 7.83 % | 4,075 to 5,532 |
| ρ = 0.00, independence | 7.72 % | 4,120 to 5,575 |

Rodrigues (2016) shows that uncorrelated components and a known aggregate
uncertainty are mutually exclusive. Holding $\sigma$ fixed while lowering
$\rho$ therefore abandons the calibration: the supply-chain coefficient of
variation collapses to 4.27 % against the 8.35 % the calibration asserts. We
instead re-solve $\sigma$ at each $\rho$ so that the calibrated total is
preserved, which is what the table reports. The correlation assumption is then
a statement about how the variance is *distributed* rather than how much of it
there is: the three totals differ by 0.13 percentage points, while the median
coefficient of variation of a single contribution group runs from 8.4 % at
$\rho = 1$ to 16.2 % at $\rho = 0$. The reported default remains the widest
total, so it cannot understate the interval. The three rows come from a
sensitivity sweep run separately from the headline estimate, at 40,000 draws
with an independent seed against the headline's 100,000 at seed 42, so the
default row reads 7.85 % where the headline reads 7.87 %.

**(b) Median-1 lognormal multipliers have mean exp(σ²/2) > 1.** The simulated
mean sits marginally above the deterministic estimate by construction. The
inflation is **+0.35 %**, immaterial here but stated.

**(c) The variance decomposition is exact, and the correlated pair is shown as
its own term.** The model is additive, so the variance splits in closed form
into each parameter's own contribution plus one covariance term for commuting
and patient travel, which share a method (ρ = 0.8). Reporting the six own-terms
alone would not be a decomposition: they would sum to 90.7 %, not 100 %. With
the covariance row the shares sum to **100.0 %** exactly and nothing is hidden.
Read as a block, travel accounts for **21.1 %** of the variance.

## 4. What this analysis does *not* establish: a limitation to state

This paragraph is written for the Limitations section. It matters: without it,
the reported interval is easy to over-read.

> **Scope of the uncertainty estimate.** The interval reported here is
> *parametric* uncertainty conditional on one input-output model. It does not
> capture structural or model-choice uncertainty: the effect of using a
> different global database, a different construct, or a nationally consistent
> table. Tukker et al. (2020) caution that *"analyses at the national level are
> much more forgiving than comparative analyses on product group level, since
> aggregation to the national level tends to iron out negative and positive
> differences at product group level"*, so published national error statistics,
> including the 8.35 % used to calibrate our input-output factor, should not be
> assumed to transfer unchanged to a single sector. Schulte et al. (2024,
> table 2) report median coefficients of variation of 4 % at country level and
> 94 % at sector level for CO₂ emission *accounts*, and 3 % and **18 %** for the
> *footprints* derived from them; a sector footprint therefore carries about six
> times the spread of a national one, even after supply-chain propagation has
> cancelled most of the account-level uncertainty. They also show that the
> *choice* of emission-account source can place a value more than three times
> outside the parametric 95 % interval. Our own vintage comparison is a direct demonstration: replacing the
> background release changed the Danish health-care climate footprint by far
> more than the parametric interval spans. The interval should therefore be read
> as the precision of this model, not as the accuracy of the estimate.

## 5. Parameter table for the supplementary information

| Parameter | Distribution | GSD / CV | 95 % factor range | Source and residual risk |
|---|---|---|---|---|
| Input-output model | lognormal, median 1 | CV 8.35 % | 0.85-1.18 | Lenzen et al. (2020) SI table 7.1, Danish health-care GHG footprint; applied jointly to all MRIO components |
| Direct operational | lognormal, median 1 | GSD 1.10 | 0.83-1.21 | Statistics Denmark DRIVHUS and AFFALD01; residual risk is the eldercare proration and the medical-N₂O netting |
| pMDI propellants | lognormal, median 1 | GSD 1.15 | 0.76-1.32 | Danish EPA F-gas inventory; register dispensing × producer HFC content |
| Employee commuting | lognormal, median 1 | GSD 1.25 | 0.65-1.55 | Ratio method on Danish employment (DST) and travel-survey distances |
| Anaesthetic gases | lognormal, median 1 | GSD 1.30 | 0.60-1.67 | Danish NID 2.G.3.a activity ±25 %, emission factor ±20 % |
| Patient and visitor travel | lognormal, median 1 | GSD 1.40 | 0.52-1.93 | Danish national travel survey; the visitor component has no Danish source |

## References

- Lenzen M, Wood R, Wiedmann T (2010) Uncertainty analysis for multi-region
  input-output models. *Economic Systems Research* 22(1):43-63.
- Lenzen M, Malik A, Li M, et al. (2020) The environmental footprint of health
  care. *Lancet Planetary Health* 4:e271-e279 (SI table 7.1).
- Rodrigues JFD, Moran D, Wood R, Behrens P (2018) Uncertainty of consumption-
  based carbon accounts. *Environmental Science & Technology* 52:7577-7586.
- Schulte S, Jakobs A, Pauliuk S (2024) Uncertainty in greenhouse gas emission
  accounts. *Earth System Science Data* 16:2669-2700.
- Tukker A, Wood R, Schmidt S (2020) Towards accepted procedures for calculating
  international consumption-based carbon accounts. *Climate Policy*
  20(sup1):S90-S106.

---

## 6. Supplementary Information: section S*n*, ready to paste

The section is self-contained: it repeats the few sentences it needs from the
Methods so it can be read on its own, as an SI section should be. Equations are
numbered S1-S7; the plain-English derivation of each is in
`monte_carlo_explained.md`.

> ### S*n*. Uncertainty propagation
>
> #### S*n*.1 Model
>
> The health-care footprint is
>
> $$F=\mathbf{c}\,(\mathbf{I}-\mathbf{A})^{-1}\mathbf{y}+\sum_{c}B_{c}\tag{S1}$$
>
> where $\mathbf{c}$ is the impact-intensity vector, $\mathbf{A}$ the technical
> coefficient matrix, $\mathbf{y}$ the health-care final-demand vector, and
> $B_c$ the five bottom-up items. Equation (S1) is linear in $\mathbf{y}$ and
> additive in $B_c$, so writing the supply-chain term as a sum over the nine
> contribution groups $g$,
>
> $$F=\sum_{g}M_{g}+\sum_{c}B_{c}\tag{S2}$$
>
> uncertainty can be propagated by resampling the fourteen deterministic
> amounts $\{M_g, B_c\}$ without re-inverting $(\mathbf{I}-\mathbf{A})$.
> $\mathbf{A}$ and $\mathbf{L}$ are consequently held fixed; uncertainty in the
> technical structure is carried by the single multiplier of (S5).
>
> #### S*n*.2 Distributions
>
> Each uncertain quantity enters as a multiplicative factor
>
> $$h=e^{\sigma z},\qquad z\sim\mathcal{N}(0,1)\tag{S3}$$
>
> lognormal with median 1, so that the simulation median reproduces the
> deterministic estimate. Lognormal multipliers are standard for input-output
> uncertainty propagation (Lenzen et al., 2010) because impacts are products of
> non-negative quantities. The spread is reported as a geometric standard
> deviation $\mathrm{GSD}=e^{\sigma}$, whose 95 % factor range is
> $[\mathrm{GSD}^{-1.96},\mathrm{GSD}^{1.96}]$. For a factor specified by a
> coefficient of variation instead,
>
> $$\sigma=\sqrt{\ln\!\left(1+\mathrm{CV}^{2}\right)}\tag{S4}$$
>
> Note that a median-1 lognormal has mean $e^{\sigma^{2}/2}>1$; for the
> input-output factor this is +0.35 %, and both the simulation mean and median
> are reported.
>
> #### S*n*.3 The input-output factor
>
> EXIOBASE publishes no element-level standard deviations. The supply-chain
> term therefore carries one factor per contribution group,
>
> $$f_{g}=\exp\!\left[\sigma_{M}\left(\sqrt{\rho_{M}}\,z_{0}+\sqrt{1-\rho_{M}}\,z_{g}\right)\right]\tag{S5}$$
>
> with $\sigma_M$ from (S4) on $\mathrm{CV}=8.35\ \%$, the relative standard
> deviation Lenzen et al. (2020, SI table 7.1) obtain for the Danish
> health-care greenhouse-gas footprint by propagating Eora's transaction,
> satellite, and final-demand matrices, the only published Monte Carlo of this
> quantity. The default $\rho_M=1$ applies one
> shared factor to every group. Because uncorrelated components and a known
> aggregate uncertainty are mutually exclusive (Rodrigues, 2016), $\sigma_M$ is
> re-solved at each $\rho_M$ so that (S4) continues to hold;
> $\rho_M\in\{0,0.76,1\}$ are reported. The default gives the widest total
> interval, and the sensitivity varies how the variance is distributed across
> contribution groups rather than how much of it there is.
>
> #### S*n*.4 Correlated bottom-up items
>
> Employee commuting and patient and visitor travel share a derivation method,
> so their factors share a random component:
>
> $$\ln h_{C}=\sigma_{C}\!\left(\sqrt{\rho}\,z_{0}+\sqrt{1-\rho}\,z_{C}\right),\qquad
> \ln h_{V}=\sigma_{V}\!\left(\sqrt{\rho}\,z_{0}+\sqrt{1-\rho}\,z_{V}\right)\tag{S6}$$
>
> This construction preserves each marginal GSD exactly while giving the
> log-factors correlation $\rho$; $\rho=0.8$ is used, and $\rho\in\{0,0.5,0.8\}$
> reported.
>
> #### S*n*.5 Variance decomposition
>
> Because (S2) is additive the output variance is available in closed form:
>
> $$\operatorname{Var}(F)=\sum_{j}a_{j}^{2}\!\left(e^{\sigma_{j}^{2}}-1\right)e^{\sigma_{j}^{2}}
> +2a_{C}a_{V}e^{(\sigma_{C}^{2}+\sigma_{V}^{2})/2}\!\left(e^{\rho\sigma_{C}\sigma_{V}}-1\right)\tag{S7}$$
>
> where $a_j$ is the deterministic amount carried by parameter $j$. Variance
> shares are computed from (S7) rather than estimated from the draws, and sum to
> 100 % exactly once the covariance term is reported as its own contribution.
> The simulation was verified against the closed-form mean
> $\sum_j a_j e^{\sigma_j^{2}/2}$ and against (S7); agreement is within five
> Monte Carlo standard errors at $N=10^{5}$ draws, and the Monte Carlo standard
> error of the reported median is 0.035 %.
>
> #### S*n*.6 Structural choices
>
> The pharmaceutical sector mapping, the price vintage, and the waste-account
> vintage are modelling decisions rather than noisy measurements and are
> reported as discrete scenarios (Table S*m*), not as distributions.
>
> #### S*n*.7 Results
>
> | | Climate change |
> |---|---|
> | Deterministic estimate | 4,712 kt CO₂e |
> | Simulation median | 4,734 kt CO₂e |
> | Simulation mean | 4,751 kt CO₂e |
> | Coefficient of variation | 7.9 % |
> | 95 % interval | 4,064 to 5,531 kt CO₂e |
>
> | Variance contributor | Share |
> |---|---|
> | Input-output model | 78.8 % |
> | Covariance, commuting × patient travel | 9.3 % |
> | Patient and visitor travel | 6.7 % |
> | Employee commuting | 5.1 % |
> | Direct operations | 0.09 % |
> | Anaesthetic gases | 0.007 % |
> | Inhaler propellants | 0.002 % |
>
> Travel as a block, covariance included, accounts for 21.1 % of the variance;
> every other bottom-up item accounts for less than 0.1 %.
