# The Monte Carlo analysis, explained from first principles

**Who this is for.** Anyone who has to defend this analysis to a referee, an
editor, or a co-author without having done the maths themselves. Every equation
below is stated twice: once in symbols, once in a sentence of ordinary English.
Nothing is assumed beyond multiplication and the idea of an average.

**What it corresponds to in the code.** `src/analysis/uncertainty_2025.py`.
Outputs are in `data/gold/results/04_uncertainty_lenzen_ieooc/`. Numbers quoted
here are the 2022 climate result, 100,000 draws, seed 42.

---

## 1. The question, and why a single number cannot answer it

The first-round review asked us to propagate the study's proxy assumptions across
plausible ranges and report what that does to the headline estimates, and
questioned whether a ±20-50 % band on the scaling factors was the right one.

The underlying worry is fair. Our headline is

$$F = 4{,}713 \text{ kt CO}_2\text{e}$$

and it is built from quantities that are not all measured with the same
confidence. Danish direct emissions come from a national account. Patient travel
comes from a national travel survey combined with an English visitor-to-patient
ratio. Those two do not deserve the same trust, and a single number hides that.

A Monte Carlo answers the question *"if each ingredient is allowed to wobble by
as much as we actually believe it might, how much does the answer wobble?"*

---

## 2. The idea in one paragraph, no symbols

Take the recipe that produced 4,713 kt. Instead of running it once, run it a
hundred thousand times. On each run, multiply each uncertain ingredient by a
random number close to 1 (sometimes 0.9, sometimes 1.15), drawn from a spread
that reflects how well we know that ingredient. Each run gives a slightly
different total. Collect all hundred thousand totals and look at the histogram:
the middle of it is the central estimate, and the range that contains 95 % of
them is the uncertainty interval. Then ask which ingredient's wobble did most to
widen the histogram. That last question turns out to be the important one.

---

## 3. The model being perturbed

### 3.1 Why the input-output algebra does not have to be re-run

The footprint is

$$F = \mathbf{c}\,\mathbf{L}\,\mathbf{y} + \sum_{c} B_c$$

*In words:* the footprint is the impact intensity vector $\mathbf{c}$ multiplied
by the Leontief inverse $\mathbf{L}=(\mathbf{I}-\mathbf{A})^{-1}$ multiplied by
the health-care final-demand vector $\mathbf{y}$, plus the bottom-up items $B_c$
that the input-output model cannot see (anaesthetic gases, inhaler propellants,
staff commuting, patient and visitor travel, and the providers' own direct
emissions).

This expression is **linear** in $\mathbf{y}$ and **additive** in the $B_c$. So
if we split the supply-chain part into contribution groups $g$,

$$F = \sum_{g} M_g + \sum_{c} B_c$$

*In words:* the total is the sum of the nine contribution-group amounts $M_g$
(pharmaceuticals, food, transport, …) plus the five bottom-up amounts.

For 2022, climate:

| Part | Amount (kt CO₂e) |
|---|---|
| $\sum_g M_g$, MRIO supply chain | 3,943.397 |
| $B_{\text{HEAL}}$, direct operations | 118.554 |
| $B_{\text{COMM}}$, employee commuting | 363.727 |
| $B_{\text{VISI}}$, patient and visitor travel | 263.568 |
| $B_{\text{ANAE}}$, anaesthetic gases | 12.522 |
| $B_{\text{PMDI}}$, inhaler propellants | 11.600 |
| **Total** | **4,713.368** |

Because the model is linear and additive, a draw only has to **recombine these
fourteen numbers with random multipliers**. The 7,987 × 7,987 matrix
$(\mathbf{I}-\mathbf{A})^{-1}$ is never inverted again. That is why 100,000
draws take seconds rather than weeks, and it is stated in the Methods because it
also means $\mathbf{A}$ and $\mathbf{L}$ are held fixed: uncertainty in the
*technology structure* is carried by the single MRIO factor of §4.1, not by
resampling the matrix.

---

## 4. What is allowed to wobble, and by how much

### 4.1 The shape of the wobble: a median-1 lognormal

Every uncertain quantity enters as a **multiplier** $h$, not as an additive
error. Multipliers are the right choice because impacts are products of
non-negative quantities (a price times a quantity times an intensity), so their
errors compound rather than add, and the result is right-skewed: it can be
twice too big far more easily than it can be minus-100 % too small.

The multiplier is drawn from a lognormal distribution:

$$h = e^{\sigma z}, \qquad z \sim \mathcal{N}(0,1)$$

*In words:* draw a standard bell-curve number $z$ (mean 0, standard deviation
1), multiply it by a spread parameter $\sigma$, and raise $e$ to that power.

Two properties matter, and both are deliberate:

**(a) The median is exactly 1.** When $z=0$, $h=e^0=1$. So half the draws scale
the ingredient up and half scale it down, and the median of the simulation
reproduces the deterministic estimate. The uncertainty analysis adds dispersion;
it does not move the answer.

**(b) The mean is slightly above 1.** For a lognormal,

$$\mathbb{E}[h] = e^{\sigma^{2}/2} > 1$$

*In words:* because the distribution has a long right tail, its average sits a
little above its middle. For our MRIO factor $\sigma = 0.0834$, so the mean is
$e^{0.0834^2/2} = 1.00348$, i.e. **+0.35 %**. This upward shift is why the simulated mean
(4,751 kt) sits marginally above the deterministic value (4,713 kt). It is
arithmetic, not a modelling error, and both are reported.

### 4.2 Reading a GSD

The spread is quoted as a **geometric standard deviation**,
$\mathrm{GSD} = e^{\sigma}$, because it can be read directly:

$$\text{95 \% factor range} = \left[\mathrm{GSD}^{-1.96},\ \mathrm{GSD}^{+1.96}\right]$$

*In words:* 95 % of the draws lie between "divide by GSD to the power 1.96" and
"multiply by GSD to the power 1.96".

So a GSD of 1.25 means *"I am 95 % sure the true value is between 0.65 and 1.55
times what I have used"*, a −35 %/+55 % range. **This range is exactly the
±20-50 % band the reviewer questioned, expressed properly.** The band is not a
guess imposed on the analysis; it is what these GSDs imply.

| Parameter | GSD | $\sigma=\ln(\mathrm{GSD})$ | 95 % factor range | Which is |
|---|---|---|---|---|
| MRIO model | 1.087 | 0.0834 | 0.85 - 1.18 | −15 % / +18 % |
| Direct operations | 1.10 | 0.0953 | 0.83 - 1.21 | −17 % / +21 % |
| Inhaler propellants | 1.15 | 0.1398 | 0.76 - 1.32 | −24 % / +32 % |
| Employee commuting | 1.25 | 0.2231 | 0.65 - 1.55 | −35 % / +55 % |
| Anaesthetic gases | 1.30 | 0.2624 | 0.60 - 1.67 | −40 % / +67 % |
| Patient and visitor travel | 1.40 | 0.3365 | 0.52 - 1.93 | −48 % / +93 % |

The ordering is the argument. The two items taken from a Danish national account
are the tightest. The item with no Danish source at all (visitor travel, where
we import an English ratio) is the loosest, at roughly a factor of two either
way. **No parameter was given a range because it looked reasonable; each range
follows from what the source is.**

### 4.3 The MRIO factor, and where 8.35 % comes from

EXIOBASE publishes no standard errors for its cells, so we cannot resample them.
Instead the whole supply-chain part carries one factor calibrated to the only
published Monte Carlo estimate of *this exact quantity*: Lenzen et al. (2020),
SI table 7.1, report the Danish health-care greenhouse-gas
footprint as $2.84 \pm 0.24$ Mt CO₂e, obtained by propagating uncertainty
through Eora's transaction, satellite, and final-demand matrices. That is a
relative standard deviation of

$$\mathrm{CV} = \frac{0.24}{2.84} = 8.35\ \%$$

Converting a CV to the lognormal spread:

$$\sigma_M = \sqrt{\ln\left(1 + \mathrm{CV}^{2}\right)} = \sqrt{\ln(1+0.0835^{2})} = 0.08335$$

*In words:* for a lognormal, the relative standard deviation and the log-scale
spread are related by that formula; for small CVs the two are almost equal, and
here 8.35 % maps to $\sigma_M = 0.0834$.

**Corroboration.** Wood et al. (2019) compare five global input-output databases
and give, in their Table 1, a **Denmark consumption-based relative standard
deviation of 8.8 %** (4.2 % after normalising to a common base year), against an
unweighted mean across all regions of 11.9 %. Denmark's *production*-based figure
is higher still at 19.3 %, and the paper names Denmark explicitly among the
countries whose variation is driven by how international transport emissions are
handled: independent support, from outside this study, for the sea-transport
correction.

That the between-model dispersion for Denmark (8.8 %) and the within-model
calibration used here (8.35 %) land within half a percentage point of each other
is a useful check, and it is not a coincidence of definition: the two are
measured by completely different exercises. It is not proof either. Wood et al.
caution that no real measure of uncertainty can be calculated from five
databases that share much of their source data.

*A correction to an earlier draft.* This note previously withdrew the 8.8 %
figure as untraceable. It was traceable; it is in Table 1 of the paper, which
the online abstract does not show. The figure is reinstated.

The same point is visible in this repository without leaving it. Five published
Danish national footprints span 9.77 to 13.19 t CO₂e per capita: a coefficient
of variation of **12.8 %**, and a factor of 1.35 between lowest and highest.
That spread is wider than the parametric interval, which is the argument of §8:
model choice moves the answer more than the parameters do.

### 4.4 Correlated ingredients

Commuting and patient travel are not independent errors. Both are built by the
same ratio method on the same kind of survey data; if that method is biased, it
is biased for both. Treating them as independent would understate the spread of
their sum.

They are therefore drawn from a shared random number plus one of their own:

$$\ln h_{C} = \sigma_{C}\left(\sqrt{\rho}\,z_{0} + \sqrt{1-\rho}\,z_{C}\right),
\qquad
\ln h_{V} = \sigma_{V}\left(\sqrt{\rho}\,z_{0} + \sqrt{1-\rho}\,z_{V}\right)$$

*In words:* both factors share one draw $z_0$ representing "the method is off in
this direction", weighted by $\sqrt{\rho}$, and each adds an independent draw of
its own weighted by $\sqrt{1-\rho}$.

Two things are true of this construction, and both matter:

- each factor keeps **exactly** the GSD declared in §4.2, because $\sigma_C$ and
  $\sigma_V$ multiply the whole bracket, whose variance is
  $\rho + (1-\rho) = 1$;
- the correlation between $\ln h_C$ and $\ln h_V$ is **exactly** $\rho$.

We use $\rho = 0.8$ and report $\rho \in \{0,\,0.5,\,0.8\}$.

> **A defect corrected on 8 September 2026.** The first implementation built the
> pair differently: it drew one shared factor with
> $\sigma_m = \sqrt{\rho\,\sigma_C\,\sigma_V}$ and topped each item up by
> $\sqrt{\sigma^2 - \sigma_m^2}$. At $\rho = 0.8$ that inner root is negative
> for commuting ($\sigma_m = 0.2451$ against $\sigma_C = 0.2231$); clamping it
> to zero silently raised commuting's realised GSD from the declared 1.25 to
> 1.278, and the simulation then no longer matched the closed-form moments it
> was supposed to be checked against. The construction above preserves both
> marginals exactly. The effect on the reported interval is small (the climate
> CV moves from 7.91 % to 7.87 %), but the check is now a real check.

### 4.5 The same reasoning applied across contribution groups

The MRIO factor is applied to all nine contribution groups at once:

$$f_g = \exp\!\left[\sigma_M\left(\sqrt{\rho_M}\,z_{0} + \sqrt{1-\rho_M}\,z_{g}\right)\right]$$

with $\rho_M = 1$ by default, i.e. one shared factor for every group. This setting is a
choice, and it is the conservative one: Rodrigues et al. (2018) measure
correlations of $0.63 \pm 0.36$ (median 0.76) between country consumption-based
accounts and show that assuming independence understates uncertainty by about
half. All three cases are reported:

| $\rho_M$ | $\sigma$ required | Total CV | Median group CV |
|---|---|---|---|
| 1.00, the study default | 0.083 | 7.85 % | 8.4 % |
| 0.76, Rodrigues et al.'s measured median | 0.092 | 7.83 % | 9.2 % |
| 0.00, independence | 0.161 | 7.72 % | 16.2 % |

The three rows come from a sensitivity sweep run separately from the headline
estimate, at 40,000 draws with an independent seed against the headline's
100,000 at seed 42. The default row therefore reads 7.85 % where the headline
reads 7.87 %; the gap is Monte Carlo noise of the expected size, not a
disagreement between the two.

**The spread is re-solved at every correlation so that the calibrated total is
held.** This re-solving corrects a defect found on 8 September 2026. Holding $\sigma$ fixed
while varying $\rho_M$ left each group's own spread unchanged, so the total's
spread fell as the correlation fell and the independence case reported a
supply-chain coefficient of variation of 4.27 % against the calibrated 8.35 %.
The sensitivity was silently abandoning the calibration it was meant to test,
and understating the interval by roughly half, the same error Rodrigues et al.
(2018) measure between dependent and independent sampling of country accounts.
Rodrigues (2016) proves the two assumptions cannot both hold: uncorrelated
disaggregates and a known aggregate uncertainty are mutually exclusive.

With the total held, $\rho_M$ becomes a sensitivity on how the variance is
**distributed**, which is what a reader wants it to be. The informative column
is the last one: at independence each contribution group carries twice the
uncertainty it does under perfect correlation, while the total is unchanged.

### 4.6 What is deliberately **not** given a distribution

Three things are modelling **choices**, not noisy measurements, and are run as
discrete scenarios instead:

| Structural choice | Why it is a scenario, not a distribution |
|---|---|
| Mapping pharmaceuticals to *Chemicals nec* | No "true value with measurement error" exists here. Either you accept the proxy or you apply Hagenaars' correction. Both are run; the answer differs by a third. |
| Price vintage | A convention about which year's prices to use. |
| Waste-account vintage | The 2011 hybrid extension against Denmark's own SEEA account: a change of *concept*, 4.6× at the health sector. |

Dressing a decision up as measurement error would tell the reader that the truth
lies somewhere in between. It does not; it lies at one of them.

---

## 5. One complete draw, worked through

This walkthrough is the whole algorithm on a single draw. Suppose the random
number generator produces $z_0 = +0.50$ for the shared MRIO factor and, for the
bottom-up items, $z_{\text{HEAL}} = -0.30$, $z_0^{\text{travel}} = +0.80$,
$z_C = -0.20$, $z_V = +0.10$, $z_{\text{ANAE}} = +1.10$,
$z_{\text{PMDI}} = -0.60$.

**Step 1: the supply chain.**
$f = e^{0.08335 \times 0.50} = e^{0.04168} = 1.04256$
$3{,}943.397 \times 1.04256 = 4{,}111.22$ kt

**Step 2: direct operations.** $\sigma = 0.09531$.
$h = e^{0.09531 \times (-0.30)} = 0.9718$
$118.554 \times 0.9718 = 115.21$ kt

**Step 3: commuting.** $\sigma_C = 0.22314$, $\rho = 0.8$, so
$\sqrt{\rho} = 0.8944$ and $\sqrt{1-\rho} = 0.4472$.
$\ln h_C = 0.22314\,(0.8944 \times 0.80 + 0.4472 \times (-0.20)) = 0.1397$
$h_C = 1.1499$, and $363.727 \times 1.1499 = 418.26$ kt

**Step 4: patient and visitor travel.** $\sigma_V = 0.33647$, **same**
$z_0^{\text{travel}} = 0.80$, which is where the correlation acts.
$\ln h_V = 0.33647\,(0.8944 \times 0.80 + 0.4472 \times 0.10) = 0.2558$
$h_V = 1.2915$, and $263.568 \times 1.2915 = 340.40$ kt

**Step 5: anaesthetics and inhalers.**
$12.522 \times e^{0.26236 \times 1.10} = 12.522 \times 1.3346 = 16.71$ kt
$11.600 \times e^{0.13976 \times (-0.60)} = 11.600 \times 0.9196 = 10.67$ kt

**Step 6: add up.**

$$4{,}111.22 + 115.21 + 418.26 + 340.40 + 16.71 + 10.67 = 5{,}012.5 \text{ kt}$$

That total is **one** draw: 5,012 kt against a deterministic 4,713 kt. Repeat
100,000 times with fresh random numbers and sort the results. Notice in step 4
that because commuting drew high, travel drew high too; that is the correlation
doing its work, and it is why the pair together widens the interval more than
either would alone.

---

## 6. Reading the output

### 6.1 The interval

| Quantity | Symbol | 2022 climate |
|---|---|---|
| Deterministic estimate | $F$ | 4,713.4 kt |
| Simulation median | $\tilde{F}$ | 4,734.7 kt |
| Simulation mean | $\bar{F}$ | 4,750.9 kt |
| Standard deviation | $s$ | 373.8 kt |
| Coefficient of variation | $s/\bar{F}$ | 7.87 % |
| 95 % interval | 2.5th to 97.5th percentile | **4,065 to 5,532 kt** |

The median reproduces the deterministic estimate to 0.5 %, as designed. The CV
of 7.87 % is close to the 8.35 % Lenzen et al. report for the same quantity by a
completely different route: a useful external check, not a coincidence, since
the MRIO factor dominates.

### 6.2 The variance decomposition: the part that actually answers the reviewer

The interval alone does not say *which* assumption to worry about. For an
additive model the variance splits exactly:

$$\operatorname{Var}(F) \;=\; \underbrace{\sum_{j} a_j^{2}\left(e^{\sigma_j^{2}}-1\right)e^{\sigma_j^{2}}}_{\text{each ingredient on its own}} \;+\; \underbrace{2\,a_C a_V\,e^{(\sigma_C^{2}+\sigma_V^{2})/2}\left(e^{\rho\sigma_C\sigma_V}-1\right)}_{\text{the correlated travel pair}}$$

*In words:* every ingredient contributes its own amount squared times a spread
term, and the two correlated travel items contribute an extra amount because
they move together. The share each contributes is its term divided by the total.

Because this decomposition is closed-form, it is computed exactly rather than
estimated from the draws, and the shares sum to 100 % by construction:

| Contributor | Share of variance |
|---|---|
| **MRIO model** | **78.8 %** |
| Patient and visitor travel | 6.7 % |
| Employee commuting | 5.1 % |
| Covariance of the travel pair | 9.3 % |
| Direct operations | 0.09 % |
| Anaesthetic gases | 0.009 % |
| Inhaler propellants | 0.002 % |

**This decomposition is the answer to the reviewers.** The proxy assumptions
that worried them (anaesthetics, inhalers, the scaled bottom-up items) together
account for less than 0.11 % of the variance. Travel, taken as a block including
its covariance, accounts for 21.1 %. Everything else is the input-output model.

Two consequences follow, and both should be stated in the paper:

1. Tightening the bottom-up proxies further would not narrow the interval. The
   effort would be wasted.
2. The one change that would narrow it is a nationally consistent input-output
   model, which is precisely what SNAC coupling would deliver.

### 6.3 Verification

Two independent checks run on every execution:

- **Closed-form moments.** For the additive lognormal sum, the mean is
  $\sum_j a_j e^{\sigma_j^{2}/2}$ and the variance is the expression in §6.2.
  The simulation is asserted against both; the run reports
  *"MC means match closed-form moments within 5 MCSE (n = 100,000)"*.
- **Monte Carlo standard error.** The uncertainty of the *simulation itself*
  (i.e. from having drawn 100,000 rather than infinitely many samples) is
  reported per indicator; for the climate median it is **0.035 %**, so the
  reported digits are stable.

---

## 7. Answers to the five questions a referee will ask

**"Why 100,000 draws?"** Because the Monte Carlo standard error at that size is
0.035 % of the median, two orders of magnitude smaller than the quantity being
reported. More draws would change no reported digit.

**"Why lognormal rather than normal?"** A normal distribution puts positive
probability on negative emissions. A lognormal cannot go below zero and is
right-skewed, which is how multiplicative errors actually behave. This
distribution is the standard choice in input-output uncertainty analysis (Lenzen
et al., 2010).

**"Where do the ±20-50 % ranges come from?"** They are not assumed; they are
what the GSDs in §4.2 imply, and each GSD follows from the type of source. Two
of the six ranges are *narrower* than 20-50 % precisely because those quantities
come from a national account, and one is *wider* because it has no Danish source
at all.

**"Isn't one shared MRIO factor too crude?"** Yes, and it is the conservative
crudeness. §4.5 reports the alternative correlations; the default gives the
widest interval, so it cannot be accused of understating uncertainty.

**"Does the interval mean the true value is 95 % likely to be in it?"** No, and
the paper says so. See §8.

---

## 8. The limitation that must be stated with the interval

> **Scope of the uncertainty estimate.** The interval reported here is
> *parametric* uncertainty conditional on one input-output model. It does not
> capture structural or model-choice uncertainty: the effect of using a
> different global database, a different construct, or a nationally consistent
> table. Tukker et al. (2020) caution that national error statistics do not
> transfer unchanged to a single sector. Schulte et al. (2024, table 2) report
> median coefficients of variation of 4 % at country level and **94 % at sector
> level** for CO₂ emission *accounts*, and 3 % and **18 %** for the *footprints*
> derived from them. The footprint pair is the comparison that applies to this
> study, because propagation through supply chains cancels much of the
> account-level uncertainty; even so, a sector footprint carries roughly six
> times the spread of a national one. They also show that the choice of
> emission-account source can place a value more than three times outside the
> parametric 95 % interval.
> Our own vintage comparison demonstrates it directly: replacing the background
> release changed the Danish health-care climate footprint by more than this
> interval spans. The interval is the **precision of this model**, not the
> **accuracy of the estimate**.

Report the interval and this paragraph together, or not at all.

---

## 9. Where each equation lives in the code

| Equation | Function in `analysis/uncertainty_2025.py` |
|---|---|
| $h = e^{\sigma z}$, GSD form | `_ln` |
| $\sigma = \sqrt{\ln(1+\mathrm{CV}^2)}$ | `_ln_cv`, and inline in `run_mc` |
| Correlated pair (§4.4) | `run_mc`, the `f["B_COMM"] / f["B_VISI"]` block |
| Group MRIO factor (§4.5) | `run_mc`, `mrio_factor[g]` |
| Recombination (§5) | `run_mc`, the loop over `INDICATORS` and `groups` |
| Percentiles and CV (§6.1) | `summarize` |
| Variance decomposition (§6.2) | `sobol_first_order` |
| Closed-form moments (§6.3) | `analytic_moments` |
| Structural scenarios (§4.6) | `PHARMA_RATIO`, `PRICE_VINTAGE`, `WASTE_VINTAGE` |

Reproduce with:

```bash
HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship PYTHONPATH=src python -m analysis.uncertainty_2025
```

---

## References

- Lenzen M, Wood R, Wiedmann T (2010) Uncertainty analysis for multi-region
  input-output models. *Economic Systems Research* 22(1):43-63.
- Lenzen M, Malik A, Li M, et al. (2020) The environmental footprint of health
  care. *Lancet Planetary Health* 4:e271-e279 (SI table 7.1).
- Rodrigues JFD, Moran D, Wood R, Behrens P (2018) Uncertainty of
  consumption-based carbon accounts. *Environmental Science & Technology*
  52:7577-7586.
- Schulte S, Jakobs A, Pauliuk S (2024) Uncertainty in greenhouse gas emission
  accounts. *Earth System Science Data* 16:2669-2700.
- Tukker A, Wood R, Schmidt S (2020) Towards accepted procedures for calculating
  international consumption-based carbon accounts. *Climate Policy*
  20(sup1):S90-S106.
- Wood R, Moran DD, Rodrigues JFD, Stadler K (2019) Variation in trends of
  consumption based carbon accounts. *Scientific Data* 6:99.
  doi:10.1038/s41597-019-0102-x
