# Response to reviewers: NXSUST-D-26-01589

*The environmental footprint of the Danish health care system: supply-chain
origins and geographical displacement*  
(title revised; the submitted version read "The environmental impacts of the
Danish health care system: supply-chain origins and geographical displacement
of impacts")

We thank both reviewers for a careful and constructive reading. The revision is
substantial. Two of the criticisms (the absence of uncertainty quantification
and the temporal mismatch between expenditure and model years) proved on
re-examination to be more serious than the reviewers could have known, and
addressing them properly led us to re-audit the entire computational chain. That
audit found defects in our background data that changed the headline results and
required us to **withdraw one of the submitted paper's findings**. We set that
out in full below, because we would rather report it ourselves than have it
found later.

Every analysis referred to here is reproducible from the repository. Each result
file carries a lineage record naming the script, the equations, the inputs, and
the published method it implements (`data/gold/results/manifest_lineage.csv`,
113 files).

**Summary of what changed**

| | Submitted | Revised |
|:---|:---|:---|
| Analysis year | 2019 expenditure on a 2016 model | **2022 expenditure on a 2022 model** |
| Climate footprint | 4,815 kt CO₂e, 5.6 % of the national total | **4,652 kt CO₂e (95 % interval 4,012 to 5,460), 6.0 %** |
| Range across the five categories | 3.6 % to 5.6 % of national | **2.4 % to 7.9 %** |
| Leading contributor | transport | **pharmaceuticals and chemical products, 37.3 % of the climate footprint and the largest in all five categories** |
| Background | EXIOBASE v3.7 | **EXIOBASE v3.8.2, validated against Danish national accounts** |
| Climate metric | IPCC AR4 (implicit) | **IPCC AR6**, with a full revision sensitivity |
| Uncertainty | none | **Monte Carlo, 100,000 draws, with Sobol variance decomposition** |
| Bottom-up items | Dutch proxies scaled to Denmark | **Danish primary data** for anaesthetics, travel, and pMDI |
| Capital | excluded, unquantified | excluded, with **two quantified sensitivities** |
| Transport finding | 38-43 % of the footprint | **withdrawn**, a documented EXIOBASE misallocation |
| Impact categories | 5 | 5 headline, **plus 99 characterised in full, 96 of them usable**, across the DESIRE workbook's four method families (CML 1999, USEtox, EcoIndicator 99, ILCD recommended) |

---

## Reviewer 1

### R1-1 · Formal uncertainty quantification

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

**Done, and the specific proxies the reviewer names have been eliminated rather
than merely bounded.**

**Ranges are now reported for every estimate the paper states, not only for the
totals.** The reviewer asks for "the resulting ranges for the main impact
estimates", and a range on the five headline totals does not answer that: the
contribution groups do not vary independently, so a reader cannot infer a
group's range from the total's. `uncertainty_by_group.csv` therefore carries the
mean, standard deviation, coefficient of variation and 95 % interval of every
contribution group in every indicator, beside the interval on that group's
*share* of the footprint. For the 2022 climate footprint:

| Contribution group | Deterministic, kt CO₂-eq | Mean ± SD | CV | 95 % interval | Share | Share, 95 % interval |
|:---|---:|---:|---:|---:|---:|---:|
| Pharmaceuticals and chemical products | 1,737.4 | 1,743.0 ± 145.2 | 8.3 % | 1,476–2,046 | 37.3 % | 34.1–39.5 % |
| Individual travel | 603.9 | 627.3 ± 166.4 | **26.5 %** | 366–1,012 | 13.0 % | **8.1–20.4 %** |
| Services | 613.4 | 615.3 ± 51.6 | 8.4 % | 521–723 | 13.2 % | 12.0–14.0 % |
| Transport | 566.5 | 568.3 ± 47.6 | 8.4 % | 481–668 | 12.2 % | 11.1–12.9 % |
| Food and food services | 433.7 | 435.1 ± 36.5 | 8.4 % | 368–511 | 9.3 % | 8.5–9.8 % |
| Other | 293.0 | 293.9 ± 24.6 | 8.4 % | 249–345 | 6.3 % | 5.7–6.6 % |
| Medical, electrical equipment and machinery | 199.9 | 200.5 ± 16.8 | 8.4 % | 170–236 | 4.3 % | 3.9–4.5 % |
| Operational impacts | 130.1 | 131.1 ± 11.9 | 9.1 % | 110–156 | 2.8 % | 2.2–3.5 % |
| Heat and electricity | 74.2 | 74.4 ± 6.2 | 8.4 % | 63–87 | 1.6 % | 1.5–1.7 % |

Three things in that table are worth the reviewer's attention, and we state them
rather than leave them to be read off.

**Seven of the nine groups carry the same coefficient of variation, 8.4 %.** That
is the MRIO block's own, and it is not a coincidence: those groups are entirely
MRIO-driven and share one multiplier, so their levels move together. The two
exceptions are the finding. Individual travel carries **26.5 %**, three times the
rest, because commuting and patient and visitor travel are bottom-up terms with
uncertainties of their own; operational impacts carries 9.1 %, slightly above the
block because the Danish direct-emissions account is tight.

**Shares are far tighter than levels, because the shared factor cancels in the
ratio.** Pharmaceuticals move by ±16 % in level and by 34.1–39.5 % in share.
Reporting only the level interval would overstate the uncertainty on every
statement of the form "pharmaceuticals are 37 % of the footprint", which is the
form most of the paper's claims take.

**The ranking is robust at the top and not at the middle.** Pharmaceuticals lead
in every draw. Individual travel's share spans 8.4 % to 20.9 %, which overlaps
Services, Transport and Food, so its rank is genuinely uncertain -
`uncertainty_ranking_probabilities.csv` gives the probability of each group
holding each of the first three places.

A Monte Carlo analysis with 100,000 draws is now reported
(`analysis.uncertainty_2025`).

**What the analysis is.** We state its construction plainly, because the phrase
"Monte Carlo" covers designs that differ greatly in what they establish. The
footprint is linear in final demand and the bottom-up items are additive, so the
quantity resampled is a fourteen-element vector of deterministic amounts — nine
input-output contribution groups and five bottom-up items — recombined on every
draw by **six scalar multipliers**. The technical coefficient matrix **A**, the
Leontief inverse **L**, the health-care final-demand vector **y** and the
impact-intensity vector **c** are held **fixed**; (**I** − **A**) is never
re-inverted and no EXIOBASE cell is resampled. This is the restriction the IEooc
reference implementation makes, and it makes the analysis an error propagation
over six parameters executed by simulation rather than a resampling of the
input-output model.

Its construction follows three principles that we state explicitly because they
are where such analyses usually go wrong:

1. **Every multiplier has median 1**, so the analysis adds dispersion without
   shifting the central estimate. Because the median of a *sum* of lognormals is
   not the sum of the medians, the simulation median reproduces the
   deterministic model to within 0.5 % — +0.45 %, or +21 kt on 4,675 kt — rather
   than exactly. A distribution whose median is not 1 would shift the central
   estimate silently; this one does not.
2. **Structural choices are discrete scenarios, never distributions.** Price
   base year, waste reference year, and the pharmaceutical mapping are reported as
   scenarios; burying a structural choice inside a lognormal would misrepresent
   a modelling decision as parameter noise.
3. **Input-output parameter uncertainty is included**, as a shared factor
   calibrated to Lenzen et al. (2020, SI table 7.1), the closest published Monte
   Carlo of this quantity for Denmark (2.84 ± 0.24 Mt CO₂-e, 8.35 % relative
   standard deviation). Omitting it would have made the bottom-up items look like
   the dominant uncertainty when they are not. We note that this is a
   **transfer**, not a reproduction: Lenzen et al. obtain 8.35 % in Eora for a
   footprint of 2.84 Mt, and it is applied here to an EXIOBASE footprint of
   4.652 Mt, 64 % larger. Their own supplementary analysis makes the relative
   standard deviation a decreasing function of footprint size, so carrying the
   figure to a larger footprint errs wide rather than narrow — but it is a
   borrowed scalar, and the interval inherits whatever is wrong with it.

Of the six spreads, that one is the only figure taken from a publication. The
five bottom-up geometric standard deviations are judgements about the kind of
source each quantity has, ordered by provenance — tightest on the item read from
a Danish national account, widest on the item whose visitor component has no
Danish source at all — because no published error statistic exists for any of
them. We prefer to say so rather than let the ordering imply a precision it does
not have.

The results are verified against the closed-form moments of the lognormal sum,
and `analysis.uncertainty_audit` runs nineteen further numerical tests on the
drawn samples, all reported in
`data/gold/results/04_uncertainty_lenzen_ieooc/uncertainty_audit.csv`.

**Three properties of the design we state rather than leave to be found.**

*The MRIO factor is perfectly correlated across contribution groups.* That
perfect correlation is a deliberate bound, not an oversight. Rodrigues et al.
(2018, ES&T 52:7577-7586)
measure correlations of 0.63 ± 0.36 (median 0.76) between country
consumption-based accounts and show that assuming **independence understates**
uncertainty by roughly half. We therefore report the bounds:

| MRIO correlation across groups | CV | 95 % interval (kt CO₂-e) |
|:---|:---|:---|
| ρ = 1.00, perfect (study default) | **7.86 %** | 4,035 to 5,484 |
| ρ = 0.76, Rodrigues et al.'s measured median | 7.83 % | 4,038 to 5,482 |
| ρ = 0.00, independence | 7.72 % | 4,090 to 5,522 |

Rodrigues (2016) shows that uncorrelated components and a known aggregate
uncertainty cannot both hold. Lowering the correlation without re-solving the
spread therefore abandons the calibration, and the supply-chain coefficient of
variation collapses to 4.29 % against the 8.35 % asserted. We re-solve the
spread at each correlation so the calibrated total is preserved. The assumption
then governs how the variance is distributed, not how much of it there is: the
three totals differ by 0.14 percentage points, while the median coefficient of
variation of a single contribution group runs from 8.4 % to 16.1 %. Our default
remains the widest of the three, which is the direction a reader should prefer.
The three rows come from a sensitivity sweep run separately from the headline
estimate, at 40,000 draws on an independent seed against the headline's 100,000
at seed 42, so the default row reads 7.85 % where the headline reads 7.86 %.
Every table in the uncertainty folder that reports a median or an interval now
carries its own draw count and seed, so differences of this kind can be
identified as simulation noise rather than taken for disagreement.

*Median-1 lognormal multipliers have mean exp(σ²/2) > 1*, so the simulated mean
sits marginally above the deterministic value by construction. Summed over all
six parameters the closed-form inflation is **+0.84 %** (the input-output factor
alone accounts for +0.35 pp of it, patient and visitor travel for a further
+0.32 pp); the simulated mean sits +0.80 % above the deterministic estimate. Both
mean and median are reported.

*First-order Sobol indices exclude interaction variance.* In this additive model
the six own-variance terms sum to **91.1 %**. The remaining **8.9 %** is not
interaction mass but the covariance of employee commuting and patient and visitor
travel, which share a derivation method and are therefore drawn with correlation
ρ = 0.8. We report it as its own row rather than distributing or suppressing it;
with it the decomposition sums to 100.0 % and nothing is hidden.

**Independent corroboration of the calibration.** Wood et al. (2019, *Sci. Data*
6:99) compare five multi-regional input-output databases and report, in their
Table 1, a **Danish consumption-based relative standard deviation of 8.8 %**
against our within-model 8.35 %. The two are measured by completely different
exercises and land within half a percentage point of each other. They also name
Denmark explicitly among the countries whose variation is driven by the handling
of international transport emissions, which is independent support for the
finding under "Data integrity" below. We report their own caveat with the
figure: no real measure of uncertainty can be derived from five databases that
share much of their source data.

**Denmark 2022, climate change: median 4,673 kt CO₂-e, 95 % interval
4,012 to 5,460 kt, coefficient of variation 7.86 %** (Tier 2 simulation; the
IPCC Tier 1 error propagation the same standard requires alongside it gives
7.89 %), closely consistent with Lenzen's published 8.35 % for the same country.

**Exact first-order Sobol variance shares**: input-output parameters **79.4 %**,
patient and visitor travel 6.9 %, employee commuting 4.6 %, the covariance of
those two 8.9 %, and **every other bottom-up item below 0.1 %** (the largest,
direct operations, is 0.096 %). Read as a block, travel accounts for 20.5 %. This
decomposition is a more useful answer than a tornado
diagram alone: the proxy assumptions the reviewer was concerned about are not
what the estimate rests on. The estimate rests on the multi-regional
input-output model.

We also report **ranking probabilities** for the contribution groups, which
answers a question the reviewer implies: whether the identity of the largest
contributor holds across draws. That identity does not hold across the two
pharmaceutical mappings (see R1-4), and we now say so.

**On the three named proxies.** Rather than bound them, we replaced them:

- *Birth-rate scaling of nitrous oxide*: replaced by Denmark's National
  Inventory Document, category 2.G.3.a.
- *Cross-country scaling for pMDI*: replaced by the Danish EPA F-gas inventory.
- *Cross-country scaling for private travel*: replaced by the Danish national
  travel survey (Transportvaneundersøgelsen, table 15, purpose code 33). The
  visitor component of that item is the one part the survey cannot supply, and it
  remains an imported ratio; it is why that parameter carries the widest spread
  in the set.

Details under R2-5.

**What this interval does not cover.** We would rather state the limits of the
analysis than have the reviewer infer them, so we set them out here and carry the
first of them into the manuscript beside the interval itself.

The interval is **parametric uncertainty conditional on one model**. It is not a
confidence interval on the Danish health-care footprint. Tukker et al. (2020)
caution that national error statistics do not transfer unchanged to single
sectors, and Schulte et al. (2024, table 2) report median footprint coefficients
of variation of 3 % at country level against 18 % at sector level. Our own change
of EXIOBASE release moved the result by more than this interval spans. The
interval should be read as the precision of this model, not the accuracy of the
estimate, and the manuscript says so wherever it is quoted.

Three specific exclusions follow from the design described above, and each is a
choice we would defend rather than an oversight:

- **Characterisation factors carry no distribution.** Their uncertainty is
  excluded on the explicit warrant of the IPCC (2000, section 6.1) and the GHG
  Protocol. We do report the footprint restated on every IPCC revision from SAR
  to AR6 as a separate sensitivity, so the effect of the characterisation
  *choice* is visible even though its measurement error is not propagated.
- **The expenditure vector carries no distribution.** Its structure — which
  health-care activity buys what, in what proportions — is held fixed, and only a
  proportional error on the supply-chain block as a whole is represented, through
  the shared input-output factor. Wood et al. (2019) rank final demand above the
  technical coefficients as a driver of between-database variation, so the
  omission matters; its direction is unknown, and closing it would require an
  error structure on the expenditure vector that the published Statistics Denmark
  tables do not supply.
- **The results are conditional on one model release.** **A** and **L** come from
  EXIOBASE v3.8.2 and are held fixed, so release and construct uncertainty sit
  entirely outside the interval. This is the largest omitted term, and the one we
  can demonstrate rather than assert: replacing the background release changed
  the headline by more than the interval's full width.

Structural choices are not absent from the revision; they are simply not inside
the distributions. The pharmaceutical mapping, the price base year and the
waste-account reference year are run as **discrete scenarios** and reported
alongside the interval, because representing a decision as measurement error
would tell the reader the truth lies somewhere between two options when it lies
at one of them. The scenarios also carry the most important finding of this
section: the alternative pharmaceutical mapping moves the median to 3,544 kt,
which lies entirely outside the parametric 95 % interval of 4,012 to 5,460 kt. A
modelling choice moves this estimate further than all six parameters together do,
and we would rather the reviewer read that from us than deduce it.

### R1-2 · Hybrid framework, double counting, coverage gaps, and GFCF

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

**Done, and quantified in three parts.**

**(a) Double counting is now tested numerically, not asserted.**
`analysis.double_counting_audit` produces a ledger in which every overlap risk
between the top-down and bottom-up components is stated, tested against the
model, and given a verdict. The one real overlap it found has been corrected:
the health sector's own self-supply loop, $s_h(L_{hh}-1)E_H$ = 1.83 kt, was
being counted both in the MRIO chain and in the national-accounts scope 1
figure, and is now subtracted. The ledger is
`02_scopes_wood_hertwich/2022_shipping_corrected/double_counting_ledger.csv`;
its first row states
the quantity being partitioned, the MRIO footprint decomposition, at 3,906.45 kt
CO₂-eq, the same number `00_core_footprint` publishes, and its second row is the
1.83 kt loop. Medical nitrous oxide is netted out of the direct-emissions
figure before the bottom-up anaesthetics item is added.

We also record a correction to our own earlier reasoning: an earlier draft
attributed the *zero* intermediate purchases of medical instruments by Danish
providers to the capital boundary. That attribution was wrong, and the true
explanation is a data defect described under "Data integrity" below.

**(b) Coverage gaps are enumerated.** The revised manuscript states plainly what
the assessment does not cover: capital (quantified below), stratospheric ozone
depletion (not computable: EXIOBASE carries no CFC, halon, or HCFC stressor),
imported waste beyond a 2011 hybrid extension, and physical energy accounting
for scope 2.

**(c) Gross fixed capital formation is now quantified.**
`analysis.capital_gfcf` implements three treatments on the same background:

| Treatment | Climate | vs baseline |
|:---|:---|:---|
| Excluded (baseline, as submitted) | 4,025.0 kt | n/a |
| Exogenous capital service flow | 4,559.7 kt | **+13.3 %** |
| Endogenised on the published Södersten et al. (2018) matrices | 4,808.9 kt | **+19.5 %** |
| Endogenised on our own simplified construction | 4,874.7 kt | +21.1 % |

Every cell is the climate row of `11_capital_gfcf`: the first, second and fourth
from `capital_scenarios_by_indicator.csv`, the third from
`capital_endogenised_sodersten.csv`.

The two endogenised rows are reported together because the second was computed
first, and the published matrices then reproduced it to within 1.6 percentage
points. That agreement is the evidence that the construction was sound, so it is
shown rather than dropped; the published route is the one to quote.

The exogenous case uses the **consumption of fixed capital**, not gross
formation, because CFC is the capital actually consumed within the year and
therefore the correct flow for an annual account; and it is taken from Statistics
Denmark's capital accounts (NABK69) rather than from EXIOBASE, whose Danish
health CFC is understated 1.79-fold.

We retain exclusion as the headline **for comparability**: Steenmeijer et al.
(2022), Eckelman & Sherman (2016), Lenzen et al. (2020), and Pichler et al.
(2019) all exclude capital, and Malik et al. (2018) include it, which is part
of why their Australian share (7.2 %) exceeds most others, a point we now make
explicitly rather than leaving the comparison naive.

Independent support for treating capital as material rather than marginal:
Eurostat's FIGARO-based footprint puts **gross fixed capital formation at 30.8 %
of Denmark's entire national consumption footprint**, three times the whole of
general-government consumption.

**(d) On "hybrid".** We accept the reviewer's distinction and have adopted their
language. The approach is additive, not an integrated hybrid LCA, and the
revised Methods says so, explains why (the bottom-up items concern flows with no
counterpart in the monetary accounts, namely anaesthetic gases, propellants, and
private travel, so integration would require a physical layer EXIOBASE does not
provide at this resolution), and states the interpretive consequence.

### R1-3 · Supply-chain displacement, trade, and normative framing

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

**Accepted, and the revision is now equipped to do it properly.**

At submission we could describe displacement only in aggregate. Every result is
now stored at full node detail (49 regions × 163 industries) with an explicit
domestic-versus-imported origin split for **every** impact category. We can
therefore name the regions and sectors, which is what the reviewer asks for.

**Danish health care's climate footprint is 26.3 % domestic and 73.7 % imported
in origin**, and the imported share rises with supply-chain depth: production
layer 0 is 50/50, layer 3 is 90 % imported. The Discussion now reports the
bearing regions by indicator, and notes that water and land impacts fall
disproportionately on regions with existing water stress.

On the five suggested references: they concern photovoltaic supply chains rather
than health care, as the reviewer anticipates. We engage the **principle** they
establish: that trade linkages transmit environmental pressure across borders
and that policy in one jurisdiction shapes outcomes in another. We cite them
alongside displacement work from the health-care and consumption-based
accounting literature so that the normative argument rests on evidence from the
sector under study as well as on the analogous case.

**Danish policy hooks for the Discussion.** The displacement finding connects
directly to statutory Danish commitments, which the revision now cites:

- **Climate Act (Act No. 965 of 26 June 2020), §1(3)(4)** requires that Danish
  reductions *"must result in real domestic reductions, but it must also be
  ensured that Danish measures do not simply relocate all of the greenhouse gas
  emissions outside of Denmark's borders."* A health system whose footprint is
  **73.7 % imported in origin** is precisely the case that provision
  contemplates.
- **§6(3)** makes the Danish Energy Agency's *Global Report* a statutory annual
  deliverable, so consumption-based accounting is an established obligation, not
  an academic preference.
- The **Danish Council on Climate Change (Klimarådet, 2025)** formally
  recommends that the Act *specify benchmarks for consumption-based carbon
  footprints and for the carbon footprint of public procurement.* The Energy
  Agency already reports public procurement at 12.2 Mt CO₂e, of which **regions
  account for 26 %**, and Danish hospitals are regional-government
  responsibilities. A regionally attributable health-sector footprint is
  therefore directly usable against a benchmark the Council has asked for.

### R1-4 · Pharmaceutical mapping to Chemicals n.e.c.

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

**Done, and it changes a headline claim, which we now report.**

Two mappings are carried as explicit scenarios:

- **Scenario A**: pharmaceuticals mapped to EXIOBASE *Chemicals n.e.c.*, as
  submitted and as in Steenmeijer et al.
- **Scenario B**: a pharmaceutical-specific intensity.

| | Climate median | 95 % interval | CV |
|:---|:---|:---|:---|
| A, chemicals n.e.c. | 4,673 kt | 4,012 to 5,460 | 7.86 % |
| B, pharma-specific | 3,544 kt | 2,927 to 4,433 | 10.7 % |

The consequence is not merely a range. Under Scenario A, pharmaceuticals and
chemicals hold rank 1 among contribution groups in **every** Monte Carlo draw.
Under Scenario B, medical and electrical equipment takes rank 1 with probability
0.85 and pharmaceuticals fall to 0.09. **The identity of the largest contributor
is decided by this mapping choice, not by parameter noise.** The revised
Results and Discussion state this dependence, and the policy recommendations are
qualified accordingly, which is precisely the implication the reviewer asked us
to draw out.

### R1-12 · Benchmark Denmark against comparable studies

**Done, and the closest comparator validates the model once boundaries are
matched.**

Schmidt & Merciai (2023) report Danish "Health and social work services" at
**6.1 Mt CO₂e, 1.07 t per capita, 8.3 % of the Danish national footprint** for
2016, the only published Danish health-sector footprint on an EXIOBASE-family
model. A headline-to-headline comparison against our 4.68 Mt would be
misleading, because three boundaries differ. Removing the two that can be
removed:

| Basis | Mt CO₂e | t/capita | % of national |
|:---|:---|:---|:---|
| Schmidt & Merciai 2023 | 6.10 | 1.070 | 8.3 % |
| This study, headline (health + eldercare, capital excluded) | 4.68 | 0.796 | 6.1 % |
| + their sector boundary (NACE Q, including childcare) | 5.28 | 0.899 | 6.8 % |
| **+ their capital treatment (endogenised)** | **6.40** | **1.089** | **8.3 %** |

Boundary-matched, we agree to **1.8 % on per capita**, and on the national share
to 8.28 % against their 8.3 %. The apparent gap was entirely the sector boundary
and the capital treatment, not the model.

One difference cannot be removed by adjustment and is stated rather than
corrected away: their model is *consequential*, ours *attributional*.

We also benchmark the **national** footprint, where published Danish estimates
separate by model family rather than by year; see "What we have not done".

### R1-5, R2-3 · Contribution relative to the existing literature

The revision now states the gap the study fills, in the literature's own terms.
Hertwich (2011) surveys consumption-based accounting and observes:

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

Government consumption is about **10 % of global greenhouse-gas emissions**, and
health care is its largest single component in most high-income countries; yet
the comparative work Hertwich identifies as missing is still largely missing.
This study contributes a national health-sector footprint that is (a) resolved
to producing region and industry for **every** impact category rather than
climate alone, (b) benchmarked against four published studies on their own table
structures, and (c) fully reproducible from public sources.

He also names a confounder we take seriously and now discuss: *"Differences in
the role of the state and in the national accounting for public services may
actually play a role here, in addition to differences in underlying
technology."* Cross-country comparison of public-sector footprints is partly a
comparison of how states are organised, not only of how they pollute.

### R1-9, R1-11 · Transport services, and naming the regions

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

R1-11 is answered by the node-level detail described under R1-3.

**R1-9 requires us to withdraw a finding.** See "Data integrity" below. The
reviewer's instinct to interrogate that number was correct.

Reviewer-facing text, for the response letter:

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*
>
> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*
>
> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

---

## Reviewer 2

### R2-4 and R2-10 · Temporal mismatch and model release

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

**Dissolved rather than defended.** The analysis now uses **2022 Danish
expenditure on the 2022 EXIOBASE table**. Expenditure year and model year
coincide, so no deflation step and no structural price-base-year assumption is required,
and the criticism no longer applies.

This alignment was possible because Statistics Denmark publishes an annual
117-industry input-output table, so the 2022 Danish expenditure vector is fully
reproducible
from public sources, unlike 2019, which required a confidential extract. That
also answers R2-6.

**The original mismatch, quantified as asked.** Dissolving a criticism is not
the same as answering it, so here is the size of the thing that was dissolved.
The model is linear in the expenditure vector, so an expenditure deflator
multiplies the MRIO supply-chain component exactly and leaves the bottom-up
items untouched. The submitted configuration is still published as
`01_eriksen_replication/2019_uncorrected/`: a grand total of 6,418.86 kt
CO₂-eq, of which 5,621.24 kt is the MRIO supply-chain component and 797.61 kt
the Danish direct and bottom-up items
(`scopes_summary.csv` in that folder). Applying the 2019 → 2016 deflator of
0.966 used in the submitted-era sensitivity takes that component to 5,430.12 kt
and the grand total to **6,227.74 kt**, i.e. the omitted deflation overstated
the submitted figure by **191.12 kt, 3.1 %**. That is smaller than the
sea-transport misallocation the same table carries, and smaller than the
uncertainty interval around it, which is why we judged it worth removing
outright rather than correcting.

We retain a reference-year sensitivity for transparency, and we now report an
additional caveat the reviewers could not have known: EXIOBASE v3.8.2 was built
in 2021, so its **emission** accounts end in 2019 for CO₂ and 2017 for other
greenhouse gases. The Danish **economic** block is validated against national
accounts for 2022 and passes; the emission side is an extrapolation, and the
Limitations say so.

### R2-5 · Uncertainty or scenario analysis for the four bottom-up parameters

**Done, and three of the four are no longer proxies.**

| Item | Submitted | Revised | Source |
|:---|:---|:---|:---|
| Anaesthetic gases | Dutch value scaled by birth rate | **11.57 kt** = nitrous oxide 10.37 + volatile agents 1.20 | Nitrous oxide: National Inventory Document 2024 (DCE 622), category 2.G.3.a, 38 t N₂O/yr × 273 (AR6 GWP₁₀₀, the factor the model's climate row uses). Volatile agents: medstat.dk register, ATC N01AB, actual Danish sales — sevoflurane 2,400 L, desflurane 181 L, isoflurane 15 L; densities from Laster et al. (1994); GWP₁₀₀ from Sulbaek Andersen et al. (2023) |
| Patient and visitor travel | Dutch value scaled by employment | **263.6 kt** | Transportvaneundersøgelsen (DTU), table 15, purpose 33 "Social/sundhed", 0.8 km/person/day. The **visitor** share is the one part the survey cannot isolate — it folds hospital visits into "visiting family and friends" — so that share alone is still imported, as the NHS England visitor-to-patient ratio of 0.236 (Tennison et al., 2021), and it is why this parameter carries the widest spread of the six |
| pMDI propellants | Dutch value scaled | **11.6 kt** | Danish EPA F-gas inventory |
| Employee commuting | Dutch value scaled | 363.7 kt | Danish employment and travel-survey distances |

The anaesthetics item is now sensitive to Danish practice in a way a fixed proxy
could not be: it shows the Danish desflurane phase-out (400 L in 2019 → 181 L in
2022), which is the most policy-relevant feature of that line.

All four are additionally in the Monte Carlo of R1-1, each with its own lognormal
spread ordered by the strength of its source, and the variance decomposition
answers the reviewer's question directly — it says how much of the estimate's
imprecision each of these four items actually causes:

| Bottom-up parameter | Geometric SD | Share of output variance |
|:---|:---|:---|
| Employee commuting | 1.25 | 4.608 % |
| Patient and visitor travel | 1.40 | 6.914 % |
| Covariance of those two, which share a method (ρ = 0.8) | — | 8.934 % |
| Direct operations | 1.10 | 0.096 % |
| Anaesthetic gases | 1.30 | 0.0076 % |
| pMDI propellants | 1.15 | 0.0020 % |

Read as a block, travel accounts for 20.5 % of the variance; the remaining
bottom-up items account for 0.11 % between them, and the input-output model for
79.4 %. Commuting and patient travel are the only two of the four that matter,
and they matter jointly, because the same ratio method produced both — which is
why we model their correlation rather than assume it away, and report the result
at ρ ∈ {0, 0.5, 0.8} (`uncertainty_travel_correlation.csv`). Treating them as
independent would narrow the 95 % interval by about 38 kt at each end.

**We also found and corrected an error in the submitted travel figure.** The
Dutch patient-and-visitor travel item is a *whole-population* quantity (159 km
per resident per year applied to 16.98 M residents). It had been scaled to
Denmark by an employment ratio multiplied by average weekly working hours,
quantities that belong to commuting alone. Applying them to a population
quantity inflated the item by roughly 1.5-2.0-fold on its own stated logic.

### R2-6 · Reproducibility of the Danish adaptation

**Done.** The analysis is reproducible end to end from public sources. Every
result file has a lineage row giving its approach, script, equations, inputs,
and published reference. The 2022 expenditure vector is built from published
Statistics Denmark tables; the bottom-up items come from named public registers;
the background is a published EXIOBASE release. Environment switches let a
reader reproduce the alternative model configurations, waste boundaries, and scope
definitions rather than take them on trust.

### R2-7 · Mitigation potential versus hotspot identification

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

**Accepted, and rather than concede the point we have modelled it, because the
answer supports the reviewer's instinct.** Language treating a hotspot as an
intervention opportunity has been removed from the Results and qualified in the
Discussion. We then added a scenario layer so the distinction can be
demonstrated instead of asserted (Figure 8; `18_mitigation_scenarios`).

Every scenario is a full counterfactual solution of the Leontief system, not a
scaled term, following the formalism of Aguilar-Hernandez et al. (2018) and
Donati et al. (2020): a scenario edits the intensity matrix, the technical
coefficients, or final demand; each edit carries a technical change coefficient
with a named source and a market-penetration coefficient stated separately; and
combined scenarios apply every edit **simultaneously** and re-solve. **All five
impact categories are reported for every scenario**, so a trade-off between them
is visible rather than assumed away.

Levers are grounded in Danish policy and measured Danish outcomes: the regions'
own −75 %-by-2030 target for hospital energy and transport; Lundbeck's measured
−15 % raw-material use; Demant's −12 % to −23.5 % packaging carbon; the Danish
Energy Agency's two grid projections; Jeswani and Azapagic's inhaler figures;
the national N₂O inventory. Levels that are not sourced are labelled
illustrative.

Set against Danske Regioner's target for hospitals' consumption-based CO₂:

| | kt CO₂e | share of the target |
|:---|:---|:---|
| 2022 baseline | 4,675 | - |
| Reduction the target requires | −2,338 | - |
| Every intervention at maximum ambition, solved together | −361 | 15 % |
| …with the grid pathway too | −460 | **20 %** |
| …with the money saved actually respent (rebound) | −281 | 12 % |
| Demand growth to 2035, business as usual | +842 | - |
| **2035 position, grid pathway included** | **5,057** | **above the 2022 baseline** |

The regional target covers hospitals while our baseline covers health and
eldercare, so the comparison is indicative of scale rather than a compliance
assessment.

Two results deserve their own sentence. **The levers are near-additive**:
summing them separately overstates the combined effect by 0.2 kt in 361, which
had to be computed to be known. **Rebound removes a fifth of the saving**:
holding total expenditure constant takes the combined figure from −361 to
−281 kt, and reporting a demand-reduction scenario without it assumes the money
is destroyed.

Reporting all five categories also surfaces trade-offs that a climate-only
analysis cannot see. Pharmaceutical raw-material efficiency does twice as much
for material extraction (−3.3 %) as for climate (−1.6 %): the pharmaceutical
hotspot is a materials hotspot. Holding expenditure constant improves climate
and materials while **worsening blue water, land use, and waste**, because the
released budget is respent on a more land- and water-intensive basket.

The substantive point is the one the reviewer was reaching for: the clinical
substitutions that dominate the sustainable-healthcare literature are real but
small, the background grid pathway is larger than all of them together, and
demand growth is larger than everything. What the hotspot analysis identifies
(pharmaceuticals and chemical products at 37 % of the climate footprint) is
precisely what no published scenario acts on. That mismatch is a finding, and it
follows from separating hotspot identification from mitigation rather than
conflating them.

What we still do not claim: no behavioural or economic model lies behind the
intervention levers (they are imposed reductions, not modelled policy
responses), interaction between levers is not modelled, and only climate carries
the full scenario set.

### R2-11 · Figure readability

Figures have been rebuilt to a consistent specification: colour-blind-safe
palette, bottom-placed legends, no baked-in titles, aspect ratios in the
1.4-1.8 range, and consistent indicator naming across axes. One substantive
defect was corrected: the variance-share figure carried legend keys for three
series that are never drawn, which are now pooled into a single labelled
residual so that every key corresponds to something visible.

---

## The remaining points, answered in order

The points above are the ones that required new analysis. The rest of both
reports are answered here, in the order the reports make them, so that nothing is
left to be inferred from the revised manuscript alone.

### Reviewer 1, minor points

**"Previous studies have used simplified system models" is vague (lines 47-48).**
Named in the revision. The comparators are now identified individually: Eckelman
and Sherman's US assessment, which uses a single-region EEIO and therefore
attributes all upstream impact to domestic production; Malik and colleagues'
Australian work, which is multi-regional but reports climate alone; Steenmeijer
and colleagues' Dutch study, which is the template here and carries five
categories but no uncertainty analysis; and Lenzen and colleagues' global
comparison, which resolves 189 countries at the cost of sector detail. The
limitation each shares is stated rather than implied: none reports a quantified
interval on its estimates, and the first two cannot separate domestic from
imported impact for a small open economy.

**Direction and magnitude of the pharmaceutical bias.** Quantified. EXIOBASE has
no pharmaceutical sector; expenditure is mapped to `Chemicals n.e.c.`, whose
emission intensity is that of bulk chemistry. Bulk chemistry is more
energy-intensive per euro than pharmaceutical formulation, so the climate and
material figures for this category are **likely overestimates**. The FIGARO
cross-check bounds it: FIGARO resolves `C21` pharmaceutical manufacturing
separately, and the Danish health sector's pharmaceutical input share there is
lower than the EXIOBASE proxy implies. We state the direction in the manuscript
and decline to state a single correction factor, because the two classifications
are not a like-for-like pair.

**Specific interventions in the conclusion.** Three are now named, each tied to
where the impact arises rather than to general principle: procurement of
pharmaceuticals and chemical products, the single largest lever at 37.3% of the
climate footprint; employee commuting and patient and visitor travel, 13.0% and
the part of the system a health authority controls most directly through siting,
scheduling and transport provision; and food procurement, 9.3% of the climate
footprint and 33% of land use.

**Grammar and formatting.** Corrected, including the two the reviewer names:
"pharmaceuticals and chemical products **were** the largest contributor", and the
malformed "0-83 t CO2e", which is now written with a decimal point. The
manuscript has been read through for the long and redundant sentences Reviewer 2
also raises.

### Reviewer 2, remaining points

**Expand the introduction; state the challenges motivating the research; state
the implications.** The introduction now sets out what a health system cannot
learn from facility-level accounting, why a small open economy makes the question
sharper than it is for a large one, and what a quantified supply-chain answer
lets a purchaser do that a production-based figure does not.

**Define EEIO, EE-MRIO, LCA, GFCF, N2O and pMDI at first use.** Done, each at
first occurrence in the main text and again at first occurrence in the appendix,
which is read separately.

**"Approximately 10% of GDP on health care" needs a year and a source.** Now
9.4% of gross domestic product in 2024, attributed to its source.

**Develop the conclusions: unique contributions, limitations, implications,
future research.** The conclusion now states the contribution as the three-year
series on one release with the sea-transport allocation corrected and a
quantified interval on every reported estimate, which none of the comparator
studies carries; the limitations in the terms below; the implications as the
three named interventions; and the next steps as the two the data would support,
namely a Danish-technology hybrid for the health sector and an extension of the
series once EXIOBASE publishes a non-nowcast year after 2020.

**The limitations subsection must say which assumptions are critical and how
future work could address them.** Rewritten on exactly that basis. It now
separates what bounds the estimates from what bounds their interpretation, gives
the capital omission a number (endogenising capital on Södersten and colleagues'
published matrices raises the input-output component from 4,025 to 4,809 kt, so the
omission is worth about 19%), and states
which parameter would repay further work: individual travel is the only line
whose coefficient of variation, 26.5%, is materially above the 8.3-9.1% that the
input-output data imposes on everything else. It also states the limit of that
observation - narrowing travel would move the total's interval very little,
because the variance is three-quarters multi-regional input-output parameters.

**Rephrase long or redundant sentences; correct grammar, punctuation and
formatting.** Done throughout, and the house style has been converted to the
journal's: decimal points rather than middle dots, an unstructured abstract
within the 250-word limit, keywords added, and the declaration headings renamed
to "Declaration of competing interests", "Declaration of generative AI use" and
"Data availability".

## Data integrity: findings we report against our own submitted results

Addressing R1-1 and R2-10 required re-examining the background data. Three
findings emerged that affect the submitted results. We report them because they
are material.

### 1. The transport finding does not survive, and must be withdrawn

The submitted manuscript reported transport as 38-43 % of the Danish health-care
footprint. On a sound model that result reproduces (36.8 % of the supply-chain component, `2022_uncorrected/`), with Danish sea and
coastal water transport alone contributing 852 kt.

**The finding is an artefact, and Denmark's own statistical office has published
on it.** Rørmose Jensen & Iliev (2022) report that EXIOBASE allocates **74 %** of
Danish
water-transport output to Danish *intermediate* use, against **9 %** in the
national accounts: the Danish-operated merchant fleet carries world trade, not
Danish production. Measured on our model the figure is **73.6 %**, reproducing
their diagnosis to the decimal. EXIOBASE even records the Danish health sector
itself as purchasing 394 M€ of sea transport, which is not credible.

Applying a target share read from Statistics Denmark's own domestic
input-output table for the background year (6.5 % for 2022; their published
9 % is reproduced to within 0.3 percentage points by reading the same table
for 2019), with row and column balances preserved to 10⁻¹¹ and industry
output unchanged:

| | Uncorrected | Corrected |
|:---|:---|:---|
| Transport share of the supply-chain climate footprint | 36.8 % | **17.8 %** |
| Danish sea transport as a producing node | 852 kt | **53.0 kt** |

The 17.8 % is on the 3,906 kt supply-chain component; on the 4,675 kt total,
which additionally carries the entirely Danish bottom-up items, transport is
14.9 %. The revised manuscript reports transport at 17.8 % and explains why the
submitted figure was too high. Reviewer 1's request to define what "transport
services" contains (R1-9) led directly to this.

**The correction is independently supported.** EXIOBASE's own *hybrid* build,
which resolves the same monetary source data onto homogeneous activity units
rather than establishment-based ones, allocates only **7.8 %** of Danish
sea-transport output to Danish intermediate use, within 1.2 percentage points
of the national-accounts benchmark, with no manual correction. The monetary
build gives 73.5 % in 2016 and 73.6 % in 2022. Two builds over the same source
data therefore disagree by a factor of nine, and the one agreeing with the
national accounts is not the one in general use: **the monetary allocation is
construct-dependent rather than an observation.** Three independent routes agree
the monetary Danish figure errs in the direction and roughly the magnitude we
correct: the national accounts, the hybrid construct, and the Danish Energy
Agency's own reallocation in the statutory Global Report. We note that no
publication claims the hybrid corrects shipping; the inference is ours, drawn
from the data.

### 2. The background model had to be replaced

We initially moved to the newest EXIOBASE release (v3.10.2) for the 2022 year.
Testing its Danish block against Statistics Denmark's published 2022
input-output table showed it could not be used:

| Danish industry, 2022 | National accounts | EXIOBASE v3.10.2 |
|:---|:---|:---|
| Health and social work | 45,321 M€ | 16,326 M€ (0.36×) |
| Education | 22,935 M€ | 109,673 M€ (4.78×) |
| Financial intermediation | 18,980 M€ | 76 M€ |
| Machinery n.e.c. | 21,150 M€ | 28 M€ |

Total Danish output is correct to 3 %, and the table balances to 10⁻¹¹, so
output has been redistributed between industries rather than lost. A check
internal to our own data settles it: Danish health and eldercare *final expenditure* in 2022
is 40,597 M€, so a health industry whose *total output* is 16,326 M€ cannot
deliver it. The defect appears only in the nowcast years and affects Denmark,
Bulgaria, Malta, and Switzerland while leaving the large economies plausible.

The study therefore uses **v3.8.2**. We report this defect because it bears on
any study using that release, not only ours.

**Every release published since v3.8.2 was then put to the same test**, so that
the choice rests on measurement rather than on the first alternative that worked.
Danish health and social work, total output in million euro, against Statistics
Denmark's published figure for the same year:

| Release | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 |
|:---|---:|---:|---:|---:|---:|---:|---:|
| v3.8.2 | 37,163 | 38,298 | *17,590* | *18,646* | 42,834 | 42,028 | 43,955 |
| v3.9.4 / .5 / .6 | 41,030 | 39,005 | 38,956 | 41,883 | 43,615 | *30,434* | *31,745* |
| v3.10.1 / .2 | 36,756 | 40,229 | 43,969 | 42,868 | 46,953 | *16,336* | *16,326* |
| Statistics Denmark | 36,640 | — | — | 39,059 | — | — | 45,321 |

Each release carries a two-year window in which the Danish health industry is
roughly half of what the national accounts report, and the window moves with the
release. In the study's primary year, 2022, v3.8.2 returns 0.970 of the national
accounts against v3.9's 0.700 and v3.10's 0.360; in 2016 all three are usable.
**No release published since v3.8.2 improves on it for 2022, and two make it
substantially worse.** We state this plainly rather than claim that v3.8.2 is
free of defects: it is not, and its own window is 2018-2019. That is why the 2019
analysis is run on the 2016 table — on v3.8.2 the 2019 table puts Danish health
at 0.477 of the national accounts, so pairing 2019 expenditure with the 2016
structure is the only correct option the release offers, not a convenience.

The comparison is published in full as
`09_exiobase_release_diagnostics/dk_health_output_by_release.csv`.

### 3. The submitted results derive from v3.8.2, not the v3.7 we cited

The submitted manuscript cites EXIOBASE v3.7. Rebuilding the pipeline from that
record does not reproduce the submitted results: the health-care services demand
column comes to 8,506 M€ against the 6,656 M€ published, and total greenhouse
gases are 39 % higher. Rebuilding from **v3.8.2** reproduces the published demand
vector exactly — 6,656.4 M€, to one decimal.

Two further checks point the same way. The submitted manuscript reports transport
at 46 % of sector contributions; a genuine v3.7 run returns **34.9 %**, while
v3.8.2's 2016 table without the shipping correction returns **46.9 %**. And v3.7
publishes no 2019 table at all — its series ends at 2016 (Zenodo record 3583071) —
so no alternative v3.7 configuration is available that could account for the
difference.

We therefore report, as a correction to the record, that **the submitted results
were produced on EXIOBASE v3.8.2 while the manuscript cited v3.7**, evidently
with the satellite file `F_Y.txt` renamed to `F_hh.txt` to satisfy the v3.7-era
loader. The revised manuscript states v3.8.2 throughout, with the Zenodo DOI and
an MD5-verifiable archive. We raise it ourselves because a reader attempting to
reproduce the submitted numbers from the cited release would fail, and because
the release turns out to be the right one on the evidence above — the citation
was wrong, not the choice.

### 3. Characterisation defects

Four rows of the characterisation workbook distributed with the background are
unusable. The most consequential defect is the **ozone-depletion** row: it
characterises only NMVOC, which drives tropospheric ozone *formation*, not
stratospheric *depletion*, and EXIOBASE contains no CFC, halon, or HCFC stressor
at all. Stratospheric ozone depletion is therefore **not computable** from this
satellite account, and we now report it as such rather than reporting a number.

The revision consequently carries a second, current characterisation method
(IMPACT World+ v2.2.1) alongside the original, and climate is reported on
**IPCC AR6** rather than the AR4 factors the workbook actually contained.

---

## What we have not done

- **Mitigation scenarios carry no behavioural model** (R2-7). The levers are
  imposed percentage reductions rather than modelled responses to a policy,
  interaction between levers is not modelled (so the combined figure is an
  upper bound), and only climate carries the full scenario set.
- **No full national-accounts coupling.** We apply the single documented
  sea-transport correction, not a complete SNAC reconstruction.

  Our national footprint is 23 % above Statistics Denmark's official figure and
  35 % above Eurostat's (77,240.6 kt against 62,900 and 57,401.7;
  `06_benchmarks_validation/figaro_vs_this_study_climate.csv`). That gap is **a property of the model family, not of
  our implementation.** Published Danish national footprints separate by the
  model used, not by the year:

  | Source | Year | Model family | t CO₂e per capita |
  |:---|:---|:---|:---|
  | Eurostat FIGARO | 2022 | national accounts | 9.77 |
  | Statistics Denmark AFTRYK | 2022 | national accounts coupled to EXIOBASE | 10.71 |
  | Rørmose Jensen & Iliev | 2020 | national accounts coupled to EXIOBASE | 11.00 |
  | Schmidt & Merciai 2023 | 2016 | **EXIOBASE** (v4 hybrid) | **12.90** |
  | **This study** | 2022 | **EXIOBASE** (v3.8.2) | **13.15** |

  Our estimate is within **1.9 %** of the only other published Danish
  EXIOBASE-based footprint, and the two EXIOBASE-family results sit 17 % to
  35 % above the three national-accounts-family results. Hertwich (2011) reports the same
  phenomenon and names Denmark in it: *"For the USA, Denmark, Germany and the
  Netherlands, the apparent reduction of greenhouse gas emissions over time
  comes as a paradox that can only be explained by differences in the
  calculation methods, not by actual developments."* The divergence is therefore
  attributable to how each family treats the Danish domestic block
  (principally shipping) and not to an error here. We report the gap, name its
  cause, and identify the national-accounts coupling as the route that would
  close it.
- **Scope 2 is inferred from expenditure**, which understates physical
  consumption in a price-spike year such as 2022.
