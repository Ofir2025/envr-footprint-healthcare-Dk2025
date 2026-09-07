# Anomalies, bugs and open questions

**Purpose.** A single register of everything this revision has found: defects in
the code, defects in the data, results that look wrong or surprising, and
decisions that are still open. It is written to be read by a co-author picking
up the work — in particular for discussion with Ofir — so each entry says what
was observed, how it was established, what was done, and what remains in doubt.

**Status key.** `FIXED` — corrected and verified. `OPEN` — unresolved, needs a
decision. `ACCEPTED` — known, quantified, documented as a limitation.
**Severity.** `HIGH` changes headline numbers or conclusions; `MEDIUM` changes a
component or a diagnostic; `LOW` cosmetic or internal.

Everything below is reproducible from the repository. Where a number is quoted,
the module that regenerates it is named.

---

## A. Defects in the background data (EXIOBASE)

### A1 — v3.10.2's 2022 Danish block misallocates output `HIGH` `FIXED`

Tested against Statistics Denmark's published 117-industry input-output table
for the same year (`analysis.vintage_defect_audit`):

| DK industry, 2022 | National accounts | v3.10.2 | ratio |
|---|---|---|---|
| Health and social work | 45,321 M€ | 16,326 | **0.36** |
| Education | 22,935 | 109,673 | **4.78** |
| Financial intermediation | 18,980 | 76 | **0.004** |
| Machinery n.e.c. | 21,150 | 28 | **0.001** |
| Medical/optical instruments | 9,130 | 0 | **0.00** |
| Real estate | 46,965 | 9,915 | **0.21** |

Total Danish output is right to 3 % and `x = Z·1 + Y·1` holds to 7×10⁻¹¹, so
output was redistributed between industries rather than lost, and the table is
internally consistent. This is an allocation failure upstream of the balancing,
not corruption.

An internal check settles it without leaving our own data: Danish health and
eldercare **final** expenditure in 2022 is 40,597 M€. A health-and-social-work
industry whose **total output** is 16,326 M€ cannot deliver it.

The defect is **year-specific** — v3.10.2's own 2016 and 2019 Danish blocks pass
— and **country-specific**: Denmark, Bulgaria, Malta and Switzerland show the
same signature (education inflated, health deflated, financial intermediation
near zero) while Germany, France, Italy, the Netherlands and the United States
remain plausible.

**Action:** background moved to EXIOBASE v3.8.2 `IOT_2022_ixi`, which passes the
same test on every checkable group. See `exiobase_vintage_defects.md`.

**Still in doubt:** whether a later v3.10.x release fixes this. Not tested — only
the vintages on disk were examined. Worth re-testing before the next submission.

### A2 — v3.10.2 empties industry 33 across Europe, in every year `HIGH` `FIXED`

`Manufacture of medical, precision and optical instruments, watches and clocks
(33)` carries ~zero output in every European region of v3.10.2, in **both** the
2016 and 2022 tables. World total 186,074 M€ (v3.10.2 2022) against 1,078,613 M€
(v3.8.2 2022).

Consequence: Danish medical-appliance demand (1,094 M€) could only be met by the
few regions retaining non-zero i33, so it landed on Greece, China and the RoW
aggregates. The resulting 921 kt — 22 % of the then-headline climate footprint —
was an artefact of empty rows, not a finding about Danish procurement.

This also explains the **multiplier-outlier screening** introduced earlier in the
revision: GB medical instruments showed an intensity of 2×10⁸ kt CO₂e per M€,
which is an emission account divided by an output of zero. The screening was
treating a symptom and is withdrawn for the headline model.

**Note for Ofir:** an earlier draft of the response letter attributed the zero
intermediate purchases of medical instruments to the **capital boundary** —
equipment sitting in GFCF rather than in Z. That explanation was wrong and has
been withdrawn in `double_counting_audit.py` and
`response_to_requests_2026_09_07.md`.

### A3 — Danish sea transport is grossly misallocated `HIGH` `FIXED`

Rørmose Jensen & Iliev (2022, Statistics Denmark, pp. 11–12) report that
EXIOBASE sends **74 %** of Danish water-transport output to Danish
*intermediate* use, against **9 %** in the national accounts. The Danish-operated
fleet carries world trade, not Danish production.

Measured on our own model (`analysis.dk_shipping_correction`): **73.6 %** —
their figure to the decimal. EXIOBASE also has the Danish **health sector itself**
purchasing 394 M€ of sea transport, which is not credible.

Effect of correcting to their 9 % target:

| | uncorrected | corrected |
|---|---|---|
| Transport share of healthcare climate footprint | 37.5 % | **18.9 %** |
| DK sea transport as a producing node | 822 kt | **71 kt** |
| Healthcare climate footprint (MRIO part) | 5,231 kt | **3,859 kt** |
| Danish national consumption-based footprint | 85.2 Mt | **76.5 Mt** |

**Consequence for the manuscript:** the submitted finding that transport is
38–43 % of the Danish health-care footprint must be **withdrawn**. It is not a
vintage artefact — it is a documented misallocation in EXIOBASE's Danish block,
diagnosed by Denmark's own statistical office.

### A4 — Residual gap against the official Danish footprint `MEDIUM` `ACCEPTED`

After the shipping correction the modelled Danish national consumption-based GHG
footprint is **76.5 Mt** against DST's official AFTRYK **62.9 Mt** (+21 %).
Foreign shipping rows (RoW-Asia, Germany, RoW-Middle East) carry much of the
remainder, and no Danish source can correct a foreign region's allocation.

Reported as a limitation, not adjusted away. It is the strongest argument for
the full Danish SNAC tier.

### A5 — EXIOBASE understates Danish health capital `MEDIUM` `ACCEPTED`

EXIOBASE's consumption of fixed capital for the Danish health-and-social-work
industry is 1,269 M€ against 2,274 M€ in Statistics Denmark's capital accounts
(NABK69, P.51c, V86000 + V87880) — understated **1.79×**. Any capital scenario
built on EXIOBASE's own CFC row would understate the effect by nearly half.
Scenario A in `analysis.capital_gfcf` is grounded in the national accounts
instead; Scenario D still uses EXIOBASE's CFC for all regions and is therefore
conservative for Denmark.

### A6 — v3.8.2 is better, not perfect `MEDIUM` `ACCEPTED`

The chosen vintage still disagrees with Danish national accounts on some groups
(`09_vintage_diagnostics/dk_block_vs_national_accounts.csv`): electrical
machinery 3.35×, post and telecommunications 2.88×, sea transport 0.63× (2016).
The concordance test is a plausibility screen on **output levels**; it says
nothing about whether the **input structure** is right. That is what
`recipe_validation_2022.csv` measures, and there v3.8.2 also has known biases.

### A7 — EXIOBASE's spectral radius is set by a pathological column `LOW` `ACCEPTED`

`ρ(A) = 0.97289`, and the dominant eigenvector is concentrated (|v| = 0.997) on
*Cultivation of paddy rice*, an industry with a column sum of 1.14. 72 columns
have sums above 1. This is why capital endogenisation moves ρ only in the eighth
decimal — ρ is **not** an informative diagnostic here, and a "column sums < 1"
test is simply the wrong test. The meaningful checks are the inverse
verification and non-negativity of L.

### A8 — The climate characterisation is IPCC AR4, not current `LOW` `ACCEPTED`

The characterisation sheet is labelled "Problem oriented approach: baseline
(CML, 1999)", but its actual GWP100 factors are **CH₄ = 25, N₂O = 298** — that
is **IPCC AR4 (2007)**, two assessment cycles out of date for a 2022 study. (SAR
is 21/310, AR5 28/265, AR6 27.9/273.) HFC and PFC carry a factor of 1 because
those EXIOBASE stressors are already reported in CO₂-equivalent.

Quantified rather than assumed (`analysis.impact_categories_full` writes the
uncharacterised stressor totals that support this):

| GWP100 vintage | Healthcare (kt) | vs AR4 | National (kt) |
|---|---|---|---|
| IPCC SAR (1995) | 3,740 | −3.0 % | 64,767 |
| **IPCC AR4 (2007) — used** | **3,855** | — | **66,675** |
| IPCC AR5 (2013) | 3,926 | +1.8 % | 67,737 |
| IPCC AR6 (2021) | 3,931 | **+2.0 %** | 67,854 |

The effect is small, so this is a reporting obligation rather than a problem:
the manuscript must state the vintage, because a reader comparing against an
AR6-based study is entitled to know. The recomputation captures 99.9 % of the
model's characterised total (3,855 against 3,859 kt), the residue being
stressors outside the six gas families.

**Related mixing:** the bottom-up items do not share this vintage. Volatile
anaesthetics use the Sulbaek Andersen et al. (2023) recommended GWP₁₀₀ set,
N₂O uses AR4 (298) for consistency with the MRIO, and pMDI takes the Danish EPA
F-gas inventory figure as published. Steenmeijer et al. have the same problem in
a sharper form — their climate factors are AR4/DESIRE while their pMDI
propellants use genuine ReCiPe GWPs (1,549 and 3,860), so their climate total
also mixes two vintages.

### A9 — Documented errors in the template study itself `MEDIUM` `ACCEPTED`

Found while transcribing Steenmeijer et al. (2022) to match their table
structures. These matter because our results are compared against theirs:

- **Table S8's scope-3 travel row is mislabelled.** Both travel rows read
  "Private travel by patients & visitors"; the scope-3 row (573 kt) is actually
  **employee commuting**. Confirmed arithmetically — the car-driver km ratio
  2280/1429 = 1.596 equals 573/359 exactly.
- **An addition error in the purchaser-to-basic-price table**, in both the
  Lancet paper and the RIVM report: `44,635 + 36,223 = 70,858`, where the true
  sum is 80,858.
- **Anaesthetic gases print as 14 kt in the Lancet and 15 kt in the RIVM
  report** (true value 14.6).
- **The pharmaceutical contribution is quoted as 38 %, 41.2 % and 27.9 %** in
  three different places.
- The Results text quotes **raw** hotspot values while Figures 2–3 plot
  **travel-redistributed** ones.

**Also worth knowing:** Steenmeijer et al. do **not** report ReCiPe 2016 impact
categories and use **no single score**. ReCiPe 2016 (H) midpoint is only a
harmonisation layer that lets the ecoinvent add-ons be summed with the
EXIOBASE/DESIRE top-down results; the RIVM report says aggregation to DALYs
"was deliberately not chosen". Their five reported categories are bespoke and
three were deliberately converted *away* from ReCiPe units. Our study's category
set is therefore correctly aligned with theirs.

---

## B. Defects in the code

### B1 — Waste extension summed non-waste fractions `HIGH` `FIXED`

`pipelines/prep_background/waste.py` summed all 19 hybrid fractions, including
**Manure, Sewage, Mining waste and Unused mining material**. None of these are
waste under Regulation (EC) 2150/2002 or in Statistics Denmark's AFFALD01 — the
account that supplies the domestic tier — so the extension was not comparable
with the Danish entry sitting beside it.

Filtering to the statistical boundary (construction/demolition and ashes
retained, as both are in scope): world industry waste **13.17 → 2.01 Gt**;
Danish national waste footprint **22.7 → 10.6 Mt**; healthcare waste
**829 → 257 kt**. `HC_WASTE_FRACTIONS=all` reproduces the old behaviour.

### B2 — Patient/visitor travel scaled with the wrong quantities `HIGH` `FIXED`

The Dutch patient-and-visitor travel item is a **whole-population** quantity
(159 km/resident/year from the English National Travel Survey × 16.98 M
residents). It was scaled to Denmark by an **employment ratio × average weekly
working hours × a distance uplift**. Employment and working hours belong to
commuting alone; applying them to a population quantity is a unit error that
inflated the item by roughly 1.5–2.0× on its own stated logic.

Replaced with Danish measurement: Transportvaneundersøgelsen (DTU), Tabel 15,
purpose code 33 "Social/sundhed" — 0.9 km/person/day (2019), 0.8 (2022), read
from the published reports and verified in the primary PDFs.

### B3 — Production-layer decomposition had a tier offset `HIGH` `FIXED`

The services demand vector is constructed as `A[:,h]·E_H`, which is **already
the first supplier tier**, whereas pharmaceuticals and appliances are true final
demands. Treating all three alike put layer 0 at 33 % instead of 19 %. Fixed by
offsetting the services layers by one.

### B4 — Monte Carlo defects `HIGH` `FIXED`

Found in audit: a bias correction hidden inside a distribution; MRIO parameter
uncertainty missing entirely; ranking probabilities invalid because six of nine
contribution groups had zero variance, giving P(rank 1) = 1.0000; the waste GSD
dominating the result; and a point mass created by clipping. Rebuilt with
median-1 lognormals, a shared MRIO factor calibrated to Lenzen et al. (2020)
SI 7.1, exact first-order Sobol shares, and verification against the closed-form
moments of the lognormal sum.

### B5 — Self-loop over-correction `MEDIUM` `FIXED`

Zeroing `Ystim[h,0]` to remove the health sector's self-supply loop removed 27 kt,
but most of that was a legitimate upstream chain. Replaced with a targeted
subtraction of the 3.2 kt that actually overlaps the national-accounts Scope 1.

### B6 — Region aggregation omitted Denmark `MEDIUM` `FIXED`

`coderagg` listed `['NL','WE','WA','WL','WM','WF']`, silently dropping the
domestic region from aggregated geography reporting.

### B7 — Wrong EXIOBASE vintage assumed `MEDIUM` `FIXED`

The submitted results could not be reproduced on v3.7. Fingerprinting the
satellite file naming (`F_Y.txt` vs `F_hh.txt`) identified **v3.8.2** as the
vintage actually used. The loader now accepts both layouts.

### B8 — Duplicated constants and stale paths `MEDIUM` `FIXED`

Model indices were duplicated across eight modules under two naming conventions;
`BACKGROUND_YEAR` was redefined independently in five modules; the model
provenance string `"EXIOBASE v3.10.2 ... (screened)"` was hardcoded in seven
places and survived the vintage change, so tables would have carried a false
label. All now come from `analysis.constants`. A stale duplicate source tree
(`src/envr_footprint_healthcare/`) was removed, and root-level output paths left
behind by the gold reorganisation were fixed.

### B9 — pandas 3 incompatibilities `LOW` `FIXED`

`count()[0]`, chained assignment, and implicit NumPy scalar conversion.

### B10 — Defects introduced during this revision, and corrected `MEDIUM` `FIXED`

Recorded for honesty, because they were mine, not Ofir's:

- The **outlier screening** was first applied to all satellite accounts, which
  crushed material extraction fourfold; restricted to air emissions. It is now
  withdrawn entirely, its cause being A2.
- The capital module's productivity test used **column sums** instead of the
  spectral radius (see A7), and its inverse verification computed
  `(I−A')[:,probe].T @ L'`, which is not `(I−A')L'` and reported a spurious
  0.40 error. Both corrected; the inverse now verifies at 2×10⁻¹⁴.
- The capital asset bridge used a **truncated asset name**, silently dropping
  45 % of the consumption of fixed capital. Fixed; unmapped CFC is now 0 and is
  asserted in the diagnostics table.
- The vintage audit **discovered 2022 twice** (txt and .mat of the same release),
  double-counting it in the verdict table.
- The variance-share figure gave **legend keys to three series never drawn**.

---

## C. Results that need explaining

### C1 — Scope 2 is far below the independent benchmark `MEDIUM` `OPEN`

Scope 2 is **72.7 kt, 1.6 %** of the climate footprint. Arup's independent
WIOD-based estimate for Denmark (2014) is **8.3 %**. Two effects push the same
way and neither is separately identified: the Danish grid fell from roughly 300
to 120 g CO₂/kWh between 2014 and 2022, and 2022 was an energy-price spike year,
so a given euro of electricity spend buys far less power and a monetary model
understates physical consumption.

**Needs a decision:** whether to report Scope 2 in physical terms using Danish
energy statistics (Energistyrelsen) rather than inferring it from spend. This is
the cleanest fix and is not yet implemented.

### C2 — The demand vector does not nest inside EXIOBASE's final demand `MEDIUM` `ACCEPTED`

`06_benchmarks_validation/demand_vector_consistency.csv`: Danish pharmaceutical
health expenditure is 1,950 M€ against EXIOBASE's Danish final demand for that
product of 865 M€ (2.3×); medical appliances 1,094 M€ against **0.9 M€**
(1,206×). The Danish expenditure vector is built from national COICOP data and
does not have to nest inside EXIOBASE's own final demand, but a ratio of 1,206
is a warning about how EXIOBASE allocates that product to Denmark.

### C3 — Direct healthcare waste is far below Australian figures `MEDIUM` `OPEN`

DST AFFALD01 gives Danish health-sector direct waste of 42.8 kt = **7.3 kg per
capita**. Malik et al. 2021 report NSW direct health waste at roughly **126 kg
per capita** — a 17× difference. This is very likely definitional (the
Australian account attributes construction and demolition waste to the health
sector), but it has not been reconciled and should be before any cross-country
waste comparison is published.

### C4 — Healthcare share of national waste is implausibly low `MEDIUM` `OPEN`

2.05 % of the national waste footprint, against 5–8 % for the other indicators
and 8 % in Malik et al. Related to C3 and to the 2011 vintage of the waste
extension.

### C5 — The imported waste tier cannot be grounded `MEDIUM` `ACCEPTED`

No consumption-based waste account exists anywhere — not in Eurostat, FIGARO,
OECD, GLORIA or UNEP. Eurostat `env_wasgen` collapses all of NACE G–U into a
single services code, so health (Q86) is not separable; the EXIOBASE hybrid
(2011) is the only per-region, per-sector waste account in existence. Roughly
36 % of the imported tier can be anchored in measurement; about 32 % sits in the
RoW aggregates where no national statistic can ever apply.

---

## D. Open decisions

These change results and are the author's call, not the analyst's.

| # | Decision | Options | Current choice | Why it matters |
|---|---|---|---|---|
| D1 | **Pharmaceutical mapping** | EXIOBASE `Chemicals nec` vs a pharma-specific intensity | Chemicals nec (Scenario A) | Decides the **identity of the top contributor**: under A pharmaceuticals hold rank 1 in every Monte Carlo draw; under B medical and electrical equipment takes rank 1 with P = 0.85. This is a mapping choice, not a finding |
| D2 | **Capital boundary** | excluded / exogenous CFC / endogenised | excluded in headline | +13.3 % to +21.0 % on climate. Excluded keeps comparability with Steenmeijer, Eckelman, Lenzen, Pichler; Malik 2018 includes it, which partly explains their higher 7.2 % |
| D3 | **Scope boundary** | health only / + eldercare / + childcare | health + eldercare | ±10 % spread. Steenmeijer's Dutch boundary includes childcare, so the third row is the like-for-like comparison with the template |
| D4 | **Eldercare share α** | 2019 detailed SUT (0.4914) vs analysis-year IO table (0.3092) | analysis-year IO | Changes direct emissions and waste. Ofir's original used the 2019 value carried forward |
| D5 | **Visitor travel** | drop it / import the NHS ratio | NHS ratio 0.236, labelled | No Danish source exists for visitor travel. This is the only remaining fully imported parameter |
| D7 | **GWP vintage** | AR4 (as characterised) / restate on AR6 | AR4 | Only ±2 % on climate, but the manuscript must state it, and the bottom-up items already use other vintages |
| D6 | **Vintage** | v3.8.2 now / wait for a corrected v3.10.x | v3.8.2 | See A1, A6 |

---

## E. What Ofir should know in one page

1. The **transport ≈ 40 % finding does not survive** and must come out of the
   manuscript. It is an EXIOBASE Danish shipping misallocation that Statistics
   Denmark has published on, and we reproduce their diagnostic figure exactly.
2. The **background model changed** from v3.10.2 to v3.8.2 because v3.10.2's
   2022 Danish block fails against national accounts. This is not a preference;
   the health industry's output there is smaller than health final demand.
3. **Headline numbers all moved.** Denmark 2022: climate 4,627 kt, materials
   4,234 kt, water 95.3 Mm³, land 4,854 km², waste 257 kt.
4. Three bottom-up items are now **Danish primary data** rather than scaled Dutch
   proxies: anaesthetics (medstat register), patient travel (national travel
   survey), pMDI (Danish EPA). One of them was carrying a unit error.
5. The **uncertainty is essentially all MRIO** — 86 % of variance. The bottom-up
   items the reviewers questioned contribute under 0.5 % each. That is a more
   useful answer to the review than the tornado alone.
6. Six decisions in section D are still open and are yours.

---

## F. Verifications that passed

Recorded so that a reader knows what *was* checked, not only what failed.

- **The Steenmeijer Z-column construction is implemented exactly.** Their
  formula is `f_services = Z[:,h] × (E_H / x_h)` where `x_h` is the health
  industry's **total input**, intermediate use *plus* value added. On our model
  `sum(Z[:,h]) + sum(V[:,h]) = x_h` holds exactly (11,730.9 + 32,224.5 =
  43,955.5 M€), and `A[:,h] = Z[:,h]/x_h` by construction, so our
  `A[:,h]·E_H` is their formula.
- **The demand vector entering the MRIO is correspondingly smaller than health
  expenditure**, as it must be: 13,067 M€ against 40,597 M€ of Danish health and
  eldercare expenditure (32.2 %). Steenmeijer's equivalent is 26,283 against
  92,515 M€ (28.4 %). The difference is value added, which has no upstream
  footprint.
- **An independently rebuilt characterisation reproduces the pipeline.** Building
  the CML GWP100 row from the workbook without reference to the production code
  gives the Danish health-care supply-chain footprint as 3.859×10⁹ kg CO₂e,
  identical to the pipeline's figure.
- **The national total reconciles**: supply chain 66,745 kt plus household direct
  9,709 kt equals the 76,454 kt reported by `analysis.national_totals`.
- **All six IO accounting identities pass** at ≤10⁻¹⁰
  (`analysis.validate_io_identities`).
