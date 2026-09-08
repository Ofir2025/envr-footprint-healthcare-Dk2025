# 04 — Monte Carlo parameter uncertainty

**Gold folder** `data/gold/results/04_uncertainty_lenzen_ieooc/`
**Module** `analysis.uncertainty_2025`
**Sources** Lenzen et al. (2020) SI Tab. SI 7.1; Rodrigues, Moran, Wood & Behrens (2018),
*Uncertainty of consumption-based carbon accounts*, Environ Sci Technol 52:7577–7586;
Wood et al. (2019); the IEooc reference implementation

Full narrative version, written for the manuscript:
`docs/revision/uncertainty_methods_for_manuscript.md`.

## Question this layer answers

Reviewer 1's central request: how precise is the estimate, what drives its imprecision,
and are the reported rankings robust?

## Method

### What is perturbed, and what is not

The footprint is linear in final demand and the bottom-up items are additive, so a draw
recombines precomputed components. $A$ and $L$ are held **fixed** and $(I-A)$ is never
re-inverted — the same choice the IEooc reference implementation makes, and it is stated
in the Methods rather than left implicit.

Each uncertain quantity enters as a **median-1 lognormal multiplier**:

$$f^{(d)} = \sum_k \lambda_k^{(d)} \, f_k, \qquad
\lambda_k \sim \mathrm{LogNormal}(0, \sigma_k^2), \quad \mathrm{median}(\lambda_k)=1$$

Median-1 means the simulation median reproduces the deterministic result and the
distribution adds dispersion without shifting the centre. (The *mean* is inflated by
$e^{\sigma^2/2}$; this is why the median, not the mean, is reported as the central value.)

### Parameters

| Parameter | GSD / CV | Source |
|---|---|---|
| `mrio` | CV 8.35 % | Lenzen et al. (2020) SI Tab. SI 7.1: Danish health GHG footprint 2.84 ± 0.24 Mt |
| `direct` | GSD 1.1 | DST DRIVHUS/AFFALD; residual risk is the α-proration |
| `anaesthetic` | GSD 1.3 | Denmark NID 2.G.3.a activity ± 25 % |
| `pmdi` | GSD 1.15 | register dispensing × producer HFC content |
| `commute` | GSD 1.25 | ratio method on NL base with DST employment and TU distances |
| `visitor` | GSD 1.4 | no Danish source; Dutch base is itself a transplanted English figure |

The widest distribution is on the parameter with the weakest provenance, which is the
correct ordering and is visible in the table rather than asserted in prose.

### MRIO uncertainty

EXIOBASE ships no element-level standard deviations. Rather than omit the largest source
of uncertainty, it enters as **one multiplicative factor applied jointly to all MRIO
components** — i.e. correlation $\rho = 1$ between them, which is the conservative bound.
Rodrigues et al. report an empirical correlation of 0.63 ± 0.36 (median 0.76); the
$\rho = 1$ assumption is therefore an upper bound on this component's contribution, and
`uncertainty_mrio_correlation.csv` reports the interval under alternative $\rho$.

The calibration target, 8.35 %, is the only published Monte Carlo estimate of *this exact
quantity*. Wood et al. (2019) independently give 8.8 % for Denmark.

### Structural choices are scenarios, not distributions

The pharmaceuticals mapping, the price vintage and the waste vintage are **modelling
decisions**, not measurement errors. Burying a decision inside a lognormal would
misrepresent it. They are run as a factorial of scenarios
(`uncertainty_structural_scenarios.csv`) and reported separately.

### Variance decomposition

First-order Sobol indices, computed exactly rather than by resampling, since the model is
a sum of independent scaled components:

$$S_k = \frac{\mathrm{Var}(\lambda_k) \, f_k^2}{\mathrm{Var}(f)}$$

### Ranking probabilities

For each contributor group, the fraction of draws in which it takes rank 1, 2 or 3. This
answers "is the reported ranking robust?" directly, rather than by inspection of intervals.

## Results

| Quantity | Value |
|---|---|
| Deterministic climate | 4 713.4 kt |
| Median | 4 735.9 kt |
| 95 % interval | 4 063.9 – 5 540.0 kt |
| CV | 7.9 % |
| MRIO share of variance | 78.8 % |

## Deviations from the source, stated

- Lenzen et al. propagate Eora's own $Q$, $A$ and $y$ uncertainties. We cannot: EXIOBASE
  publishes none. We therefore **borrow their result as a calibration** rather than
  reproduce their propagation, and say so.
- Draws are 10⁵, not 10⁶; the Monte Carlo standard error of the median is reported
  (`mcse_median_pct`) so the reader can see that this is sufficient.

## What this does **not** establish

This is parametric uncertainty **conditional on one model**. Tukker et al. warn that
national error statistics do not transfer to sector studies; Schulte et al. find country
CV near 4 % but sector-level CV up to 94 %. Our own change of EXIOBASE vintage moved the
result by more than this interval spans. A limitations paragraph making exactly this point
is drafted in `uncertainty_methods_for_manuscript.md` and should be carried into the
manuscript — reporting the interval without it would over-claim.

## Verification

- Simulation moments are checked against the closed-form mean and variance of a sum of
  lognormals.
- Variance shares sum to 100.0 % once the covariance of the correlated travel
  pair is carried as its own row; without it the own-terms reach only 90.7 %.
- A step-by-step derivation of every equation, for a reader who does not want
  to read the code, is in `docs/revision/monte_carlo_explained.md`.
