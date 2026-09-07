# Response to reviewers: NXSUST-D-26-01589

*The environmental impacts of the Danish health-care system: supply-chain
origins and geographical displacement of impacts*

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
the published method it implements (`data/gold/results/MANIFEST_lineage.csv`,
113 files).

**Summary of what changed**

| | Submitted | Revised |
|---|---|---|
| Analysis year | 2019 expenditure on a 2016 model | **2022 expenditure on a 2022 model** |
| Background | EXIOBASE v3.7 | **EXIOBASE v3.8.2, validated against Danish national accounts** |
| Climate metric | IPCC AR4 (implicit) | **IPCC AR6**, with a full vintage sensitivity |
| Uncertainty | none | **Monte Carlo, 100,000 draws, with Sobol variance decomposition** |
| Bottom-up items | Dutch proxies scaled to Denmark | **Danish primary data** for anaesthetics, travel, and pMDI |
| Capital | excluded, unquantified | excluded, with **two quantified sensitivities** |
| Transport finding | 38-43 % of the footprint | **withdrawn**, a documented EXIOBASE misallocation |
| Impact categories | 5 | 5 headline, **plus 135 computed across two LCIA methods** |

---

## Reviewer 1

### R1-1 · Formal uncertainty quantification

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

**Done, and the specific proxies the reviewer names have been eliminated rather
than merely bounded.**

A Monte Carlo analysis with 100,000 draws is now reported
(`analysis.uncertainty_2025`). Its construction follows three principles that we
state explicitly because they are where such analyses usually go wrong:

1. **Every multiplier has median 1**, so the Monte Carlo median reproduces the
   deterministic model. A distribution whose median is not 1 silently shifts the
   central estimate.
2. **Structural choices are discrete scenarios, never distributions.** Price
   vintage, waste vintage, and the pharmaceutical mapping are reported as
   scenarios; burying a structural choice inside a lognormal would misrepresent
   a modelling decision as parameter noise.
3. **MRIO parameter uncertainty is included**, as a shared factor calibrated to
   Lenzen et al. (2020, SI table 7.1), the only published Monte Carlo of this
   exact quantity for Denmark (2.84 ± 0.24 Mt CO₂-e, 8.35 % relative standard
   deviation). Omitting it would have made the bottom-up items look like the
   dominant uncertainty when they are not.

The results are verified against the closed-form moments of the lognormal sum.

**Three properties of the design we state rather than leave to be found.**

*The MRIO factor is perfectly correlated across contribution groups.* That
perfect correlation is a deliberate bound, not an oversight. Rodrigues et al.
(2018, ES&T 52:7577-7586)
measure correlations of 0.63 ± 0.36 (median 0.76) between country
consumption-based accounts and show that assuming **independence understates**
uncertainty by roughly half. We therefore report the bounds:

| MRIO correlation across groups | CV | 95 % interval |
|---|---|---|
| ρ = 1.00, perfect (study default) | **7.85 %** | 4,068 to 5,527 |
| ρ = 0.76, Rodrigues et al.'s measured median | 7.83 % | 4,075 to 5,532 |
| ρ = 0.00, independence | 7.72 % | 4,120 to 5,575 |

Rodrigues (2016) shows that uncorrelated components and a known aggregate
uncertainty cannot both hold. Lowering the correlation without re-solving the
spread therefore abandons the calibration, and the supply-chain coefficient of
variation collapses to 4.27 % against the 8.35 % asserted. We re-solve the
spread at each correlation so the calibrated total is preserved. The assumption
then governs how the variance is distributed, not how much of it there is: the
three totals differ by 0.13 percentage points, while the median coefficient of
variation of a single contribution group runs from 8.4 % to 16.2 %. Our default
remains the widest of the three, which is the direction a reader should prefer.
The three rows come from a sensitivity sweep run separately from the headline estimate, at 40,000 draws with an independent seed against the headline's 100,000 at seed 42, so the default row reads 7.85 % where the headline reads 7.87 %.

*Median-1 lognormal multipliers have mean exp(σ²/2) > 1*, so the simulated mean
sits marginally above the deterministic value by construction. The inflation is
**+0.35 %**, and is reported.

*First-order Sobol indices exclude interaction variance.* In this additive model
they sum to 100.0 %, so interaction mass is negligible, and the first-order
decomposition is complete. We say so rather than leaving the reader to assume it.

**Independent corroboration of the calibration.** Wood et al. (2019, *Sci. Data*
6:99) compare five multi-regional input-output databases and report, in their
Table 1, a **Danish consumption-based relative standard deviation of 8.8 %**
against our within-model 8.35 %. The two are measured by completely different
exercises and land within half a percentage point of each other. They also name
Denmark explicitly among the countries whose variation is driven by the handling
of international transport emissions, which is independent support for the
finding under "Data integrity" below. We report their own caveat with the
figure: no real measure of uncertainty can be derived from five databases that
share much of their source data. That figure is derived from a completely
different exercise (cross-database spread rather than within-model Monte Carlo)
and lands within half a percentage point of the 8.35 % we calibrate to.

**Denmark 2022, climate change: median 4,734 kt CO₂-e, 95 % interval
4,064 to 5,531 kt, coefficient of variation 7.87 %**, closely consistent with
Lenzen's published 8.35 % for the same country.

**Exact first-order Sobol variance shares**: MRIO parameters **78.8 %**, patient
and visitor travel 7.4 %, employee commuting 5.7 %, and **every other bottom-up
item below 0.2 %**. This decomposition is a more useful answer than a tornado
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
  travel survey (Transportvaneundersøgelsen, table 15, purpose code 33).

Details under R2-5.

### R1-2 · Hybrid framework, double counting, coverage gaps, and GFCF

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

**Done, and quantified in three parts.**

**(a) Double counting is now tested numerically, not asserted.**
`analysis.double_counting_audit` produces a ledger in which every overlap risk
between the top-down and bottom-up components is stated, tested against the
model, and given a verdict. The one real overlap it found has been corrected:
the health sector's own self-supply loop, `s_h(L_hh − 1)E_H` = 3.2 kt, was being
counted both in the MRIO chain and in the national-accounts scope 1 figure, and
is now subtracted. Medical nitrous oxide is netted out of the direct-emissions
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
|---|---|---|
| Excluded (baseline, as submitted) | 4,062 kt | n/a |
| Exogenous capital service flow | 4,598 kt | **+13.2 %** |
| Endogenised on the published Södersten et al. (2018) matrices | 4,849 kt | **+19.4 %** |
| Endogenised on our own simplified construction | 4,914 kt | +21.0 % |

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
|---|---|---|---|
| A, chemicals n.e.c. | 4,734 kt | 4,064 to 5,531 | 7.87 % |
| B, pharma-specific | 3,605 kt | 2,980 to 4,503 | 10.7 % |

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
model. A headline-to-headline comparison against our 4.71 Mt would be
misleading, because three boundaries differ. Removing the two that can be
removed:

| Basis | Mt CO₂e | t/capita | % of national |
|---|---|---|---|
| Schmidt & Merciai 2023 | 6.10 | 1.070 | 8.3 % |
| This study, headline (health + eldercare, capital excluded) | 4.71 | 0.802 | 6.1 % |
| + their sector boundary (NACE Q, including childcare) | 5.28 | 0.899 | 6.8 % |
| **+ their capital treatment (endogenised)** | **6.39** | **1.088** | **8.2 %** |

Boundary-matched, we agree to **1.7 % on per capita and 0.1 percentage points on
the national share**. The apparent gap was entirely the sector boundary and the
capital treatment, not the model.

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

---

## Reviewer 2

### R2-4 and R2-10 · Temporal mismatch and model vintage

> *[Referee comment withheld - the referee reports for a manuscript under
> review are confidential. The full text is in the submission system and in
> the private working copy. The heading above states the point addressed.]*

**Dissolved rather than defended.** The analysis now uses **2022 Danish
expenditure on the 2022 EXIOBASE table**. Expenditure year and model year
coincide, so no deflation step and no structural-vintage assumption is required,
and the criticism no longer applies.

This alignment was possible because Statistics Denmark publishes an annual
117-industry input-output table, so the 2022 Danish expenditure vector is fully
reproducible
from public sources, unlike 2019, which required a confidential extract. That
also answers R2-6.

We retain a vintage sensitivity for transparency, and we now report an
additional caveat the reviewers could not have known: EXIOBASE v3.8.2 was built
in 2021, so its **emission** accounts end in 2019 for CO₂ and 2017 for other
greenhouse gases. The Danish **economic** block is validated against national
accounts for 2022 and passes; the emission side is an extrapolation, and the
Limitations say so.

### R2-5 · Uncertainty or scenario analysis for the four bottom-up parameters

**Done, and three of the four are no longer proxies.**

| Item | Submitted | Revised | Source |
|---|---|---|---|
| Volatile anaesthetics | Dutch value scaled by birth rate | **11.6 kt** | medstat.dk register, ATC N01AB, actual Danish sales: sevoflurane 2,400 L, desflurane 181 L, isoflurane 15 L; densities from Laster et al. (1994); GWP₁₀₀ from Sulbaek Andersen et al. (2023) |
| Patient and visitor travel | Dutch value scaled by employment | **263.6 kt** | Transportvaneundersøgelsen (DTU), table 15, purpose 33 "Social/sundhed", 0.8 km/person/day |
| pMDI propellants | Dutch value scaled | **11.6 kt** | Danish EPA F-gas inventory |
| Employee commuting | Dutch value scaled | 363.7 kt | Danish employment and travel-survey distances |

The anaesthetics item is now sensitive to Danish practice in a way a fixed proxy
could not be: it shows the Danish desflurane phase-out (400 L in 2019 → 181 L in
2022), which is the most policy-relevant feature of that line.

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
reader reproduce the alternative vintages, waste boundaries, and scope
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
|---|---|---|
| 2022 baseline | 4,712 | - |
| Reduction the target requires | −2,357 | - |
| Every intervention at maximum ambition, solved together | −361 | 15 % |
| …with the grid pathway too | −634 | **27 %** |
| …with the money saved actually respent (rebound) | −285 | 12 % |
| Demand growth to 2035, business as usual | +848 | - |
| **2035 position, grid pathway included** | **4,928** | **above the 2022 baseline** |

The regional target covers hospitals while our baseline covers health and
eldercare, so the comparison is indicative of scale rather than a compliance
assessment.

Two results deserve their own sentence. **The levers are near-additive**:
summing them separately overstates the combined effect by 0.2 kt in 361, which
had to be computed to be known. **Rebound removes a fifth of the saving**:
holding total expenditure constant takes the combined figure from −361 to
−285 kt, and reporting a demand-reduction scenario without it assumes the money
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

## Data integrity: findings we report against our own submitted results

Addressing R1-1 and R2-10 required re-examining the background data. Three
findings emerged that affect the submitted results. We report them because they
are material.

### 1. The transport finding does not survive, and must be withdrawn

The submitted manuscript reported transport as 38-43 % of the Danish health-care
footprint. On a sound model that result reproduces (37.5 %), with Danish sea and
coastal water transport alone contributing 852 kt.

**The finding is an artefact, and Denmark's own statistical office has published
on it.** Rørmose Jensen & Iliev (2022) report that EXIOBASE allocates **74 %** of
Danish
water-transport output to Danish *intermediate* use, against **9 %** in the
national accounts: the Danish-operated merchant fleet carries world trade, not
Danish production. Measured on our model the figure is **73.6 %**, reproducing
their diagnosis to the decimal. EXIOBASE even records the Danish health sector
itself as purchasing 394 M€ of sea transport, which is not credible.

Applying their 9 % benchmark, with row and column balances preserved to 10⁻¹¹
and industry output unchanged:

| | Uncorrected | Corrected |
|---|---|---|
| Transport share of the supply-chain climate footprint | 37.5 % | **18.5 %** |
| Danish sea transport as a producing node | 852 kt | **74 kt** |

The 18.5 % is on the 3,943 kt supply-chain component; on the 4,712 kt total,
which additionally carries the entirely Danish bottom-up items, transport is
15.4 %. The revised manuscript reports transport at 18.5 % and explains why the
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
|---|---|---|
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

The study therefore uses **v3.8.2**, which passes the same test on every
checkable industry group. We report this defect because it bears on any study
using that release, not only ours.

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

  Our national footprint is 22 % above Statistics Denmark's official figure and
  33 % above Eurostat's. That gap is **a property of the model family, not of
  our implementation.** Published Danish national footprints separate by the
  model used, not by the year:

  | Source | Year | Model family | t CO₂e per capita |
  |---|---|---|---|
  | Eurostat FIGARO | 2022 | national accounts | 9.77 |
  | Statistics Denmark AFTRYK | 2022 | national accounts coupled to EXIOBASE | 10.71 |
  | Rørmose Jensen & Iliev | 2020 | national accounts coupled to EXIOBASE | 11.00 |
  | Schmidt & Merciai 2023 | 2016 | **EXIOBASE** (v4 hybrid) | **12.90** |
  | **This study** | 2022 | **EXIOBASE** (v3.8.2) | **13.19** |

  Our estimate is within **2.3 %** of the only other published Danish
  EXIOBASE-based footprint, and both EXIOBASE-family results sit about 20 %
  above both national-accounts-family results. Hertwich (2011) reports the same
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
