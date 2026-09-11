# Defects and fixes

This document is the revision's defect ledger: the 2019-baseline audit that
started the revision, the current (2022) register of anomalies, bugs, code
defects, results that need explaining, and open decisions, and the technical
response to the eight review requests of 7 September 2026. It is the
technical backbone behind [`request_checklist.md`](request_checklist.md),
which is the up-to-date status ledger; this document carries the evidence and
the numbers behind each line of it. Later sections carry later, more current
figures; where a number in an earlier section has been superseded, that is
stated at the point where it recurs rather than silently corrected in place,
because the earlier section is itself a dated snapshot of the audit as it
stood on the day it was written.

## Contents

1. [The 2019 baseline audit](#the-2019-baseline-audit)
2. [Anomalies, bugs and open questions (current register)](#anomalies-bugs-and-open-questions-current-register)
3. [Methods and data soundness: response to the eight review requests](#methods-and-data-soundness-response-to-the-eight-review-requests)

---

## The 2019 baseline audit

**Scope:** revision of the Danish healthcare environmental-footprint model (Eriksen et al.,
Next Sustainability NXSUST-D-26-01589) following the forensic audit of 2026-09-06 and the
first-round reviews. Every entry lists the defect, the evidence, the change, and the effect
on results. Baseline year 2019 expenditure on the EXIOBASE 2016 industry-by-industry table.
**These are 2019 figures.** The 2022 re-analysis carries its own, current versions
of most of these fixes; see the [anomalies register](#anomalies-bugs-and-open-questions-current-register)
below and [docs/revision/results_2022.md](results_2022.md) for the figures that
supersede this section where the two differ.

### Release identification (reportable erratum)

The manuscript and repo README cite EXIOBASE **v3.7** (Zenodo 3583071). Rebuilding the
pipeline from that record does **not** reproduce the submitted results (healthcare-services
demand column 8,506 M€ vs the published 6,656 M€; total GHG +39%). Rebuilding from
**EXIOBASE v3.8.2** (Zenodo 5589597, `IOT_2016_ixi.zip`) reproduces the published
demand vector **exactly** (scaled intermediate-input sum 6,656.4 M€ = committed value to
one decimal). The submitted results therefore derive from **v3.8.2**, with the satellite
file `F_Y.txt` evidently renamed to `F_hh.txt` to satisfy the v3.7-era loader.

*Action:* the revision pins EXIOBASE 3.8.2 (MD5-verifiable Zenodo artifact), the loader
now accepts both `F_Y.txt`/`F_hh.txt` names, and the manuscript's data statement must be
corrected from v3.7 to v3.8.2.

### E1: Expenditure vector omitted ~90% of eldercare (critical)

**Defect:** `calculate_healthcare_totals` enumerated (transaction × purpose) columns by
hand and omitted (i) non-market government consumption of purpose 12401 (retirement
homes/day care/home help) = **DKK 68.4 bn**, and (ii) NPISH hospital services = DKK 2.3 bn,
while the manuscript stated eldercare was included.

**Fix:** complete coverage of all individual-consumption transactions (3110/3130/3141/3142)
for purposes 06112, 06130, 06200, 06300, 12401; every included column is exported to
`data/silver/inputs/dk_expenditure_breakdown_2019.csv` as a provenance record. Childcare
(12402, DKK 60.4 bn, inside Steenmeijer's wider "zorg en welzijn" scope) remains excluded
by default and is available via `include_childcare=True` for a scope sensitivity.

**Effect:** healthcare-services expenditure rises from DKK 173.0 bn to **DKK 243.7 bn**
(23.2 → 32.6 b€), +41%.

### E2: Direct (Scope-1) operational emissions (critical)

**Defect:** the "operational impacts" (B_HEAL) GWP entry was computed as
$\mathbf{B}\,(\mathbf{L}\,y_{\text{stim}})$ over the DK health rows = **1.39 kt CO₂e**, the MRIO-induced intra-health
emissions, which (a) are already inside the contribution totals (a double count) and
(b) are not the sector's direct emissions. An unsourced `DirectEm = 1,699 kt` sat unused
in `dk_data_2025.csv`.

**Fix:** Statistics Denmark **DRIVHUS** greenhouse-gas accounts by industry (national-
accounts-consistent, kt CO₂e excl. biogenic CO₂; `data/bronze/dk_direct_emissions_drivhus.csv`).
Scope construction mirrors the expenditure boundary:
QA Human health + 870000 Residential care + α × 880000 Social work w/o accommodation,
with α = 0.4914 derived from the supply-use tables (split of 880000's products between
purposes 12401 eldercare and 12402 childcare), minus hospital N₂O (medical gas, moved to
B_ANAE). For 2019: 106 + 23 + 0.4914×67 − 11 ≈ **151 kt CO₂e**. This construction restores
the Steenmeijer design (national-accounts direct figure excluding medical gases, injected
via `Hstim`).

### E3: GHG-Protocol scopes misconstructed

**Defect:** "Scope 2" summed electricity/heat-sector emissions over the **entire global
supply chain** (i.e. mostly Scope 3); "Scope 1 (MRIO)" was the 1.39 kt artifact; pMDIs
were booked to Scope 1.

**Fix:** Scope 1 = DRIVHUS direct + anaesthetic gases; Scope 2 = generation emissions of
energy purchased *directly* by the providers (energy-sector entries of the scaled
intermediate-input column × those sectors' own direct intensity); Scope 3 = remaining
supply chain + pMDI (use-phase at patients' homes) + commuting; patient/visitor travel =
outside protocol, matching Steenmeijer et al.'s Table S8 classification.

### Bottom-up items: Danish primary data replace NL-scaled proxies (2019 figures)

| Item | Old (NL × factor) | New (2019) | Source |
|:---|:---|:---|:---|
| Anaesthetic gases | 9.51 kt (NL × 0.67, births proxy) | **12.7 kt** = 38 t N₂O/yr × 298 (11.3) + population-scaled volatiles (1.4) | Denmark's National Inventory Document 2024 (DCE rep. 622), cat. 2.G.3.a; volatiles proxy pending Danish data |
| pMDI propellants | 34.61 kt (NL × 0.45) | **12.8 kt** = 7.2 t HFC (90/10 HFC-134a/227ea) × ReCiPe 2016 GWP100 | Vestbo & Press-Kristensen 2023, Eur Respir J 62:2300856; Danish EPA F-gas inventory 11.6 kt (2022, GWP100). NB: the often-quoted 31 kt is **GWP20** |
| Commuting | factor 0.544 | factor **0.5719** | employment DST NABB69 2019 (86000+87880 = 518,889) ÷ NL 1,220,750; hours 34.4/29.2; TU 2019 Table 20 distance 9.0 vs NL 7.88 km/person/day |
| Patient/visitor travel | factor 0.636 | factor **0.6300** (employment update) | no Danish primary source exists (verified); TU microdata named as future route |

The old pMDI value was ~2.7× too high (GWP20/GWP100 conflation propagated through the
Dutch scaling); the anaesthetic value was ~25% low, and its N₂O part now comes from the
national inventory, coherent with the DRIVHUS netting (the accounts carry ~11 kt CO₂e of
hospital N₂O, removed from B_HEAL and re-entered via B_ANAE). **These figures are for
2019**; the 2022 re-analysis carries its own current values, given in
[docs/revision/results_2022.md](results_2022.md#bottom-up-items-now-on-danish-primary-data)
and, for the anaesthetics item specifically, in
[docs/revision/results_2022.md, "Bottom-up anaesthetic gases"](results_2022.md#bottom-up-anaesthetic-gases).

### Currency and prices

DKK→EUR at the Danmarks Nationalbank 2019 annual average **7.4661** (was flat 7450 per
kDKK→M€, −0.22%). Basic-price basis verified: the loader reads sheet `Ubas` (use table at
basic prices), which is why `Conversion=1.0` is correct, now documented in code. The
2019-expenditure-on-2016-price-model mismatch (Reviewer 2) is addressed via a deflation
scenario in the uncertainty package (`src/analysis/uncertainty_2025.py`), and disappears
entirely in the 2022-on-2022 analysis (see
[docs/revision/results_2022.md](results_2022.md) and
[Decision D8](results_2022.md#decision-d8-2022-nowcast-or-the-last-observed-year)).

### Presentation/robustness fixes

- Transport disaggregation mask changed from substring (`contains('Transport')`, which
  also captured **Transport Equipment** = vehicle manufacturing) to exact group match.
- Stray no-op statement removed; `.count()[0]` → `.count().iloc[0]`, label writes made
  Copy-on-Write-safe, NumPy scalar conversions fixed (pandas 3 / NumPy 2 compatibility;
  numerically neutral).
- Loader accepts `F_Y.txt` (EXIOBASE ≥3.8) and `F_hh.txt` (3.7).
- Bottom-up file's `ISO2` provenance column no longer breaks row widths.

### Result bridge (2019 expenditure, EXIOBASE 3.8.2-2016)

The bridge is filled from the corrected run; see `data/gold/results/` and
[docs/revision/results_2022.md, "Results bridge: submitted vs corrected"](results_2022.md#results-bridge-submitted-vs-corrected)
for the step-by-step decomposition (submitted → corrected), each step attributable to
exactly one entry above.

### Known remaining limitations (carried to the manuscript, as of the 2019 baseline)

- Waste extension remains the 2011 hybrid-EXIOBASE waste-supply account divided by 2016
  monetary output (Steenmeijer precedent, disclosed); a rebuilt 2022-compatible waste
  extension (Eurostat env_wasgen-anchored, WIO-style) is planned for the 2022 analysis.
- Pharmaceuticals map to EXIOBASE `Chemicals nec` (aggregation bias with known sign);
  treated as a discrete scenario in the uncertainty package.
- Capital formation (GFCF) excluded, as in Steenmeijer et al.; acknowledged one-directional.
- Volatile anaesthetics remain a population-scaled proxy (no Danish inventory exists).
  **Since closed for 2022**; see
  [docs/revision/results_2022.md, "Bottom-up anaesthetic gases"](results_2022.md#bottom-up-anaesthetic-gases).
- The EXIOBASE-estimated input recipe of the DK "Health and social work" industry drives
  the transport-dominance result; validation against the Danish national IO health columns
  is part of the planned SUT-integration work
  ([docs/methods/methods.md, "Danish SNAC"](../methods/methods.md#danish-snac-what-statistics-denmark-does-what-we-patch-and-the-feasibility-of-a-full-build)).

---

## Anomalies, bugs and open questions (current register)

**Purpose.** A single register of everything this revision has found: defects in
the code, defects in the data, results that look wrong or surprising, and
decisions that are still open. It is written to be read by a co-author picking
up the work (in particular for discussion with Ofir), so each entry says what
was observed, how it was established, what was done, and what remains in doubt.

**Status key.** `FIXED`: corrected and verified. `OPEN`: unresolved, needs a
decision. `ACCEPTED`: known, quantified, documented as a limitation.
**Severity.** `HIGH` changes headline numbers or conclusions; `MEDIUM` changes a
component or a diagnostic; `LOW` cosmetic or internal.

Everything below is reproducible from the repository. Where a number is quoted,
the module that regenerates it is named.

### A. Defects in the background data (EXIOBASE)

#### A1: v3.10.2's 2022 Danish block misallocates output `HIGH` `FIXED`

Tested against Statistics Denmark's published 117-industry input-output table
for the same year (`analysis.release_defect_audit`):

| DK industry, 2022 | National accounts | v3.10.2 | ratio |
|:---|:---|:---|:---|
| Health and social work (NACE 75, 86, 87, 88) | 45,854 M€ | 16,326 | **0.36** |
| Education | 22,935 | 109,673 | **4.78** |
| Financial intermediation | 18,980 | 76 | **0.004** |
| Machinery n.e.c. | 21,150 | 28 | **0.001** |
| Medical/optical instruments | 9,130 | 0 | **0.00** |
| Real estate | 46,965 | 9,915 | **0.21** |

Total Danish output is right to 3 %, and $x = \mathbf{Z}\,\mathbf{1} + \mathbf{Y}\,\mathbf{1}$ holds to 7×10⁻¹¹, so
output was redistributed between industries rather than lost, and the table is
internally consistent. This redistribution is an allocation failure upstream of
the balancing, not corruption.

The comparator is the whole of ISIC rev.3 division 85, veterinary medicine
included, because that is what EXIOBASE's single health industry covers; the
narrower NACE 86, 87 and 88 group is 45,321 M€, and using it would compare the
model's full-group output against a partial national-accounts group.

An internal check settles it without leaving our own data: Danish health and
eldercare **final** expenditure in 2022 is 40,597 M€. A health-and-social-work
industry whose **total output** is 16,326 M€ cannot deliver it.

The defect is **year-specific** (v3.10.2's own 2016 and 2019 Danish blocks pass)
and **country-specific**: Denmark, Bulgaria, Malta, and Switzerland show the
same signature (education inflated, health deflated, financial intermediation
near zero), while Germany, France, Italy, the Netherlands, and the United States
remain plausible.

**Action:** background moved to EXIOBASE v3.8.2 `IOT_2022_ixi`, which passes the
same test on every checkable group. See
[`../methods/exiobase_release_and_classification.md`](../methods/exiobase_release_and_classification.md).

**Still in doubt:** whether a later v3.10.x release fixes this. We did not test
it: only the releases on disk were examined. Re-testing before the next
submission is worthwhile.

#### A2: v3.10.2 empties industry 33 across Europe, in every year `HIGH` `FIXED`

`Manufacture of medical, precision and optical instruments, watches and clocks
(33)` carries ~zero output in every European region of v3.10.2, in **both** the
2016 and 2022 tables. World total 186,074 M€ (v3.10.2 2022) against 1,078,613 M€
(v3.8.2 2022).

Consequence: Danish medical-appliance demand (1,094 M€) could only be met by the
few regions retaining non-zero i33, so it landed on Greece, China, and the RoW
aggregates. The resulting 921 kt, 22 % of the then-headline climate footprint,
was an artefact of empty rows, not a finding about Danish procurement.

This emptying also explains the **multiplier-outlier screening** introduced
earlier in the revision: GB medical instruments showed an intensity of 2×10⁸ kt
CO₂e per M€, which is an emission account divided by an output of zero. The
screening was treating a symptom and is withdrawn for the headline model.

**Note for Ofir:** an earlier draft of the response letter attributed the zero
intermediate purchases of medical instruments to the **capital boundary**
(equipment sitting in GFCF rather than in Z). That explanation was wrong and has
been withdrawn in `double_counting_audit.py` and
[the methods-soundness response, section 2](#2-scope-1-3-without-double-counting-with-the-equations-right).

#### A3: Danish sea transport is grossly misallocated `HIGH` `FIXED`

Rørmose Jensen & Iliev (2022, Statistics Denmark, pp. 11-12) report that
EXIOBASE sends **74 %** of Danish water-transport output to Danish
*intermediate* use, against **9 %** in the national accounts. The Danish-operated
fleet carries world trade, not Danish production.

Measured on our own model (`analysis.dk_shipping_correction`): **73.6 %**,
their figure to the decimal. EXIOBASE also has the Danish **health sector itself**
purchasing 394 M€ of sea transport, which is not credible.

Effect of correcting to their 9 % target, **as first implemented, with the
target held fixed at 9 % for every background year**:

| | uncorrected | corrected |
|:---|:---|:---|
| Transport share of the supply-chain climate footprint | 37.5 % | **18.5 %** |
| DK sea transport as a producing node | 852 kt | **74 kt** |
| Healthcare climate footprint (MRIO part) | 5,231 kt | **3,943 kt** |
| Danish national consumption-based footprint | 85.2 Mt | **77.5 Mt** |

The corrected transport share is on the 3,943 kt supply-chain basis; on the
4,712 kt total it is 15.4 %. The full method, the comparison with every
alternative, and the audit of the withdrawn submitted finding are in
[docs/revision/results_2022.md, "The withdrawn transport finding"](results_2022.md#the-withdrawn-transport-finding).
Finding F2 below (["Numbers quoted in the revision docs had drifted"](#f2-numbers-quoted-in-the-revision-docs-had-drifted-from-the-gold-outputs))
records the values this table carried before it was reconciled against the
gold outputs.

**Superseded again, since 11 September 2026.** The fixed 9 % target above was
itself replaced by a target read from Statistics Denmark's own domestic
input-output table for the background year (6.5 % for 2022, 7.7 % for 2016;
9.3 % reading their 2019 table is the cross-check that reproduces their
published 9 %). This table's "corrected" column is therefore a superseded
intermediate state, kept for the record; the current numbers are 17.8 % of
the supply-chain footprint (14.9 % of the 4,675 kt total), 53.0 kt for the
Danish sea-transport node, and 77.2 Mt for the Danish national footprint. See
["Correction target read from the DST table per year"](#correction-target-read-from-the-dst-table-per-year)
below.

**Consequence for the manuscript:** the submitted finding that transport is
38-43 % of the Danish health-care footprint must be **withdrawn**. It is not a
release artefact; it is a documented misallocation in EXIOBASE's Danish block,
diagnosed by Denmark's own statistical office.

#### A4: Residual gap against the official Danish footprint `MEDIUM` `ACCEPTED`

After the shipping correction the modelled Danish national consumption-based GHG
footprint is **77.2 Mt** against DST's official AFTRYK **62.9 Mt** (+23 %).
Foreign shipping rows (RoW-Asia, Germany, RoW-Middle East) carry much of the
remainder, and no Danish source can correct a foreign region's allocation.

The gap is reported as a limitation, not adjusted away. It is the strongest
argument for the full Danish SNAC tier.

#### A5: EXIOBASE understates Danish health capital `MEDIUM` `ACCEPTED`

EXIOBASE's consumption of fixed capital for the Danish health-and-social-work
industry is 1,269 M€ against 2,274 M€ in Statistics Denmark's capital accounts
(NABK69, P.51c, V86000 + V87880), understated **1.79×**. Any capital scenario
built on EXIOBASE's own CFC row would understate the effect by nearly half.
Scenario A in `analysis.capital_gfcf` is grounded in the national accounts
instead; Scenario D still uses EXIOBASE's CFC for all regions and is therefore
conservative for Denmark. Full detail in
[docs/revision/results_2022.md, "Capital (GFCF) treatment"](results_2022.md#capital-gfcf-treatment).

#### A6: v3.8.2 is better, not perfect `MEDIUM` `ACCEPTED`

The chosen release still disagrees with Danish national accounts on some groups
(`09_exiobase_release_diagnostics/dk_block_vs_national_accounts.csv`): electrical
machinery 3.35×, post and telecommunications 2.88×, sea transport 0.63× (2016).
The concordance test is a plausibility screen on **output levels**; it says
nothing about whether the **input structure** is right. That is what
`recipe_validation_2022.csv` measures, and there v3.8.2 also has known biases.

#### A7: EXIOBASE's spectral radius is set by a pathological column `LOW` `ACCEPTED`

$\rho(\mathbf{A}) = 0.97289$, and the dominant eigenvector is concentrated (|v| = 0.997) on
*Cultivation of paddy rice*, an industry with a column sum of 1.14. 72 columns
have sums above 1. This concentration is why capital endogenisation moves ρ only
in the eighth decimal; ρ is **not** an informative diagnostic here, and a
"column sums < 1" test is simply the wrong test. The meaningful checks are the
inverse verification and non-negativity of $\mathbf{L}$.

#### A7b: Four defective rows in the DESIRE characterisation workbook `HIGH` `FIXED`

The workbook shipped with the background (`characterisation_desire_version3_4_
adapted.xlsx`, a 2014 FP7 file) has four rows that cannot be used. All
four are now detected in `analysis.impact_categories_full` and flagged in the
gold table rather than left for a reader to discover.

1. **Ozone layer depletion characterises the wrong pollutant class.** Its
   factors fall entirely on **NMVOC** (48 stressors, CF ≈ 2.3×10⁻⁵ kg
   CFC-11-eq per kg). NMVOC drives *tropospheric ozone formation*; stratospheric
   ozone *depletion* is caused by CFCs, halons, and HCFCs, **none of which
   exists as a stressor anywhere in EXIOBASE**. IMPACT World+ v2.2.1 correctly
   returns zero for this category. Ozone depletion is therefore **not computable** from this
   satellite account, and the Eckelman comparison now reports it as such.
   *This retracts a previously reported Danish ODP share of 12.9 %.*
2. **Freshwater ecotoxicity endpoint is bit-identical to its own midpoint**
   while carrying a different unit, so its factors are a copy and it conveys no
   damage information.
3. **Photochemical ozone formation endpoint** yields a DALY-per-midpoint ratio
   about 55× below the published IMPACT 2002+ damage factor.
4. **SF₆ carries 26,087**, which matches no IPCC assessment (SAR 23,900,
   TAR 22,200, AR4 22,800, AR5 23,500, AR6 25,200). EXIOBASE's own shipped
   impact files use 22,800 for the same row, so this is a corruption local to
   the adapted copy. Superseded by the AR6 restatement, which sets 25,200.

**Consequence:** the study now carries a second, current characterisation
method, **IMPACT World+ v2.2.1** (CIRAIG, DOI 10.5281/zenodo.18892673,
CC-BY-SA-4.0), whose 1113 columns match the EXIOBASE v3.8.2 stressor list
exactly and in order (asserted at load, fatal on mismatch). It supplies 38 live
categories including water scarcity, mineral resource use, land biodiversity,
and DALY endpoints (none of which DESIRE could provide); only 11 of its 57
categories have no matching stressor, against 42 of DESIRE's 121.

#### A8b: The 2022 background is itself a nowcast `MEDIUM` `ACCEPTED`

EXIOBASE v3.8.2 was built in September 2021. Its emission accounts end in 2019
for CO₂ and 2017 for the other greenhouse gases, so the 2022 table extrapolates
both the economy and the emissions. The Danish *economic* block was validated
against Statistics Denmark's 2022 national accounts and passes; the *emission*
side has no equivalent validation and is an extrapolation of up to five years.
This qualification, and the choice between the 2022 nowcast and Statistics
Denmark's own practice of freezing at the last observed year, is
[Decision D8](results_2022.md#decision-d8-2022-nowcast-or-the-last-observed-year).

A later release, v3.9.6 (DOI 10.5281/zenodo.15689391), nowcasts 2022 from a 2020
base and revises non-combustion methane. Migrating would also mean switching to
the IMPACT World+ matrix built for EXIOBASE 3.9 and later, because the stressor
layout changed. The migration is not done here; it is recorded as the strongest
candidate for the next revision.

#### A8: The climate characterisation is IPCC AR4, not current `LOW` `ACCEPTED`

The characterisation sheet is labelled "Problem oriented approach: baseline
(CML, 1999)", but its actual GWP100 factors are **CH₄ = 25, N₂O = 298**, that
is, **IPCC AR4 (2007)**, two assessment cycles out of date for a 2022 study. (SAR
is 21/310, AR5 28/265, AR6 27.9/273.) HFC and PFC carry a factor of 1 because
those EXIOBASE stressors are already reported in CO₂-equivalent.

Quantified rather than assumed (`analysis.impact_categories_full` writes the
uncharacterised stressor totals that support this):

| GWP100 revision | Healthcare (kt) | vs AR4 | National (kt) |
|:---|:---|:---|:---|
| IPCC SAR (1995) | 3,703 | −3.0 % | 64,531 |
| IPCC TAR (2001) | 3,754 | −1.7 % | 65,327 |
| IPCC AR4 (2007), as EXIOBASE ships | 3,818 | n/a | 66,439 |
| IPCC AR5 (2013) | 3,918 | +2.6 % | 67,773 |
| **IPCC AR6 (2021), used** | **3,906** | **+2.3 %** | **67,519** |

The study restates to AR6; the row marked as EXIOBASE's own is what the database
ships, and is shown because a reader comparing against a study that did not
restate is entitled to know the gap. The effect is small, so the revision is a
reporting obligation rather than a problem. The restatement covers 96.0 % of the
characterised total: the remaining 155.3 kt is HFC and PFC, which EXIOBASE
supplies already aggregated to CO₂-equivalent and which therefore keep whatever
revision EXIOBASE used. That residue is reported rather than silently restated
(`gwp_revision_sensitivity.csv`, columns `not_restatable_*`).

**Related mixing, since resolved.** The bottom-up items do not all share the
MRIO row's GWP revision. Volatile anaesthetics use the Sulbaek Andersen et al. (2023)
recommended GWP₁₀₀ set and pMDI takes the Danish EPA F-gas inventory figure as
published, both of which are deliberate: they are the published values for those
specific gases. The nitrous oxide term was the one genuine mismatch. It carried
**AR4's 298**, chosen when the MRIO climate row still ran on EXIOBASE's own
DESIRE factors, which are AR4, so the two agreed; rebuilding the MRIO row on AR6
left it stranded at a different revision from the model around it.

An earlier draft of this register argued for leaving it, on the grounds that
38 t × (298 − 273) = 0.95 kt CO₂e is 0.02 % of the headline against a 95 %
interval spanning 1,467 kt. That reasoning was wrong in kind rather than in
arithmetic: a study that states it reports on AR6 should report on AR6
everywhere, and the cost of restating is a pipeline run. The term now uses
`AR6_GWP100["N2O"]` from `analysis.constants`, so it cannot drift from the model
again, and the headline moved 4,713.368 to **4,712.418 kt**.

Steenmeijer et al. have the same problem and it is not resolved there: their
climate factors are AR4/DESIRE while their pMDI propellants use genuine ReCiPe
GWPs (1,549 and 3,860), so their climate total mixes two revisions.

#### A9: Documented errors in the template study itself `MEDIUM` `ACCEPTED`

These errors were found while transcribing Steenmeijer et al. (2022) to match
their table structures. They matter because our results are compared against
theirs:

- **Table S8's scope-3 travel row is mislabelled.** Both travel rows read
  "Private travel by patients & visitors"; the scope-3 row (573 kt) is actually
  **employee commuting**. The arithmetic confirms it: the car-driver km ratio
  2280/1429 = 1.596 equals 573/359 exactly.
- **An addition error in the purchaser-to-basic-price table**, in both the
  Lancet paper and the RIVM report: `44,635 + 36,223 = 70,858`, where the true
  sum is 80,858.
- **Anaesthetic gases print as 14 kt in the Lancet and 15 kt in the RIVM
  report** (true value 14.6).
- **The pharmaceutical contribution is quoted as 38 %, 41.2 % and 27.9 %** in
  three different places.
- The Results text quotes **raw** hotspot values while Figures 2-3 plot
  **travel-redistributed** ones.

**Also worth knowing:** Steenmeijer et al. do **not** report ReCiPe 2016 impact
categories and use **no single score**. ReCiPe 2016 (H) midpoint is only a
harmonisation layer that lets the ecoinvent add-ons be summed with the
EXIOBASE/DESIRE top-down results; the RIVM report says aggregation to DALYs
"was deliberately not chosen". Their five reported categories are bespoke, and
three were deliberately converted *away* from ReCiPe units. Our study's category
set is therefore correctly aligned with theirs.

### B. Defects in the code

#### B1: Waste extension summed non-waste fractions `HIGH` `FIXED`

`pipelines/prep_background/waste.py` summed all 19 hybrid fractions, including
**Manure, Sewage, Mining waste, and Unused mining material**. None of these are
waste under Regulation (EC) 2150/2002 or in Statistics Denmark's AFFALD01 (the
account that supplies the domestic tier), so the extension was not comparable
with the Danish entry sitting beside it.

Filtering to the statistical boundary (construction/demolition and ashes
retained, as both are in scope): world industry waste **13.17 → 2.01 Gt**;
Danish national waste footprint **22.7 → 10.6 Mt**; healthcare waste
**829 → 257 kt**. `HC_WASTE_FRACTIONS=all` reproduces the old behaviour.

#### B2: Patient/visitor travel scaled with the wrong quantities `HIGH` `FIXED`

The Dutch patient-and-visitor travel item is a **whole-population** quantity
(159 km/resident/year from the English National Travel Survey × 16.98 M
residents). It was scaled to Denmark by an **employment ratio × average weekly
working hours × a distance uplift**. Employment and working hours belong to
commuting alone; applying them to a population quantity is a unit error that
inflated the item by roughly 1.5-2.0× on its own stated logic.

It was replaced with Danish measurement: Transportvaneundersøgelsen (DTU),
Tabel 15, purpose code 33 "Social/sundhed", at 0.9 km/person/day (2019), 0.8
(2022), read from the published reports and verified in the primary PDFs.

#### B3: Production-layer decomposition had a tier offset `HIGH` `FIXED`

The services demand vector is constructed as $\mathbf{A}(:,h)\,E_H$, which is **already
the first supplier tier**, whereas pharmaceuticals and appliances are true final
demands. Treating all three alike put layer 0 at 33 % instead of 19 %. The fix
offsets the services layers by one.

#### B4: Monte Carlo defects `HIGH` `FIXED`

The audit found: a bias correction hidden inside a distribution; MRIO parameter
uncertainty missing entirely; ranking probabilities invalid because six of nine
contribution groups had zero variance, giving P(rank 1) = 1.0000; the waste GSD
dominating the result; and a point mass created by clipping. The module was
rebuilt with median-1 lognormals, a shared MRIO factor calibrated to Lenzen et
al. (2020) SI 7.1, exact first-order Sobol shares, and verification against the
closed-form moments of the lognormal sum. Full derivation in
[docs/revision/uncertainty.md](uncertainty.md).

#### B5: Self-loop over-correction `MEDIUM` `FIXED`

Zeroing `Ystim[h,0]` to remove the health sector's self-supply loop removed 27 kt,
but most of that was a legitimate upstream chain. Replaced with a targeted
subtraction of the 3.2 kt that actually overlaps the national-accounts Scope 1.

#### B6: Region aggregation omitted Denmark `MEDIUM` `FIXED`

`coderagg` listed `['NL','WE','WA','WL','WM','WF']`, silently dropping the
domestic region from aggregated geography reporting.

#### B7: Wrong EXIOBASE release assumed `MEDIUM` `FIXED`

The submitted results could not be reproduced on v3.7. Fingerprinting the
satellite file naming (`F_Y.txt` vs `F_hh.txt`) identified **v3.8.2** as the
release actually used. The loader now accepts both layouts.

#### B8: Duplicated constants and stale paths `MEDIUM` `FIXED`

Model indices were duplicated across eight modules under two naming conventions;
`BACKGROUND_YEAR` was redefined independently in five modules; the model
provenance string `"EXIOBASE v3.10.2 ... (screened)"` was hardcoded in seven
places and survived the release change, so tables would have carried a false
label. All now come from `analysis.constants`. A stale duplicate source tree
(`src/envr_footprint_healthcare/`) was removed, and root-level output paths left
behind by the gold reorganisation were fixed.

#### B9: pandas 3 incompatibilities `LOW` `FIXED`

`count()[0]`, chained assignment, and implicit NumPy scalar conversion.

#### B10: Defects introduced during this revision, and corrected `MEDIUM` `FIXED`

These are recorded for honesty, because they were mine, not Ofir's:

- The **outlier screening** was first applied to all satellite accounts, which
  crushed material extraction fourfold; restricted to air emissions. It is now
  withdrawn entirely, its cause being A2.
- The capital module's productivity test used **column sums** instead of the
  spectral radius (see A7), and its inverse verification computed
  `(I−A')[:,probe].T @ L'`, which is not `(I−A')L'` and reported a spurious
  0.40 error. Both are corrected; the inverse now verifies at 2×10⁻¹⁴.
- The capital asset bridge used a **truncated asset name**, silently dropping
  45 % of the consumption of fixed capital. The bridge is fixed; unmapped CFC is
  now 0 and is asserted in the diagnostics table.
- The release audit **discovered 2022 twice** (txt and .mat of the same release),
  double-counting it in the verdict table.
- The variance-share figure gave **legend keys to three series never drawn**.

### C. Results that need explaining

#### C1: Scope 2 is far below the independent benchmark `MEDIUM` `OPEN`

Scope 2 is **72.7 kt, 1.6 %** of the climate footprint. Arup's independent
WIOD-based estimate for Denmark (2014) is **8.3 %**. Two effects push the same
way, and neither is separately identified: the Danish grid fell from roughly 300
to 120 g CO₂/kWh between 2014 and 2022, and 2022 was an energy-price spike year,
so a given euro of electricity spend buys far less power, and a monetary model
understates physical consumption.

**Needs a decision:** whether to report Scope 2 in physical terms using Danish
energy statistics (Energistyrelsen) rather than inferring it from spend. This
change is the cleanest fix and is not yet implemented.

#### C2: The demand vector does not nest inside EXIOBASE's final demand `MEDIUM` `ACCEPTED`

`06_benchmarks_validation/demand_vector_consistency.csv`: Danish pharmaceutical
health expenditure is 1,950 M€ against EXIOBASE's Danish final demand for that
product of 865 M€ (2.3×); medical appliances 1,094 M€ against **0.9 M€**
(1,206×). The Danish expenditure vector is built from national COICOP data and
does not have to nest inside EXIOBASE's own final demand, but a ratio of 1,206
is a warning about how EXIOBASE allocates that product to Denmark.

#### C3: Direct healthcare waste is far below Australian figures `MEDIUM` `OPEN`

DST AFFALD01 gives Danish health-sector direct waste of 42.8 kt = **7.3 kg per
capita**. Malik et al. 2021 report NSW direct health waste at roughly **126 kg
per capita**, a 17× difference. This difference is very likely definitional (the
Australian account attributes construction and demolition waste to the health
sector), but it has not been reconciled and should be before any cross-country
waste comparison is published.

#### C4: Healthcare share of national waste is implausibly low `MEDIUM` `OPEN`

Healthcare accounts for 2.05 % of the national waste footprint, against 5-8 %
for the other indicators and 8 % in Malik et al. The anomaly is related to C3
and to the 2011 reference year of the waste extension.

#### C5: The imported waste tier cannot be grounded `MEDIUM` `ACCEPTED`

No consumption-based waste account exists anywhere: not in Eurostat, FIGARO,
OECD, GLORIA, or UNEP. Eurostat `env_wasgen` collapses all of NACE G-U into a
single services code, so health (Q86) is not separable; the EXIOBASE hybrid
(2011) is the only per-region, per-sector waste account in existence. Roughly
36 % of the imported tier can be anchored in measurement; about 32 % sits in the
RoW aggregates where no national statistic can ever apply.

#### C6: Lenzen et al.'s Danish record has a halved expenditure base `MEDIUM` `ACCEPTED`

The record was verified against their supplementary information. Their Tab. SI
10.2 gives Denmark **2,975 US$ per capita** of health expenditure against Sweden
7,800, Norway 10,210, and Finland 5,560 **in the same table**, when all four
countries were around 5,000-6,500 US$ per capita in reality. Denmark's reported
intensity of 0.20 kg CO₂-e per US$ is consequently the highest in the Nordic
group, which is an artefact of the denominator rather than a finding.

**Consequence:** their Danish *intensity* and *share-of-GDP* figures cannot be
used as benchmarks. Their absolute footprint and per-capita values remain usable
with the caveats below.

Three further problems appear in the same source, all verified:

- **Two different Danish totals for the same country-year**: 3.37 Mt (Tab. SI
  10.1, the headline) and 2.84 ± 0.24 Mt (Tab. SI 7.1, the uncertainty table).
  The gap is systematic across countries and indicators, so the two sections
  appear to be different model runs. This study cites SI 7.1 **only** for the
  relative standard deviation that calibrates the Monte Carlo (which is
  legitimate, since a relative SD is unaffected by a level shift), and compares
  levels against SI 10.1. Both are named in `08_lenzen_replication/`.
- **Direct plus supplier does not equal their total** (1.03 + 0.46 ≠ 3.37).
  Their supplier column is first-order only, leaving 56 % of the Danish
  footprint as unreported higher-order. Our decomposition reports all three
  tiers.
- **Their global direct share is irreconcilable**: figure 4 gives 63.1 Mt as
  "3 %", Tab. SI 9.1 gives 0.85 Gt as 35 %.

**Boundary difference to state in any comparison:** their Danish health sector
is pharmaceutical *manufacturing* + hospital activities + medical, dental, and
veterinary activities. Pharmaceutical manufacturing and veterinary care are
inside; no social or residential care sector is included. Ours excludes
veterinary and includes eldercare. Capital is never mentioned in their paper or SI.

### D. Open decisions

These change results and are the author's call, not the analyst's.

| # | Decision | Options | Current choice | Why it matters |
|:---|:---|:---|:---|:---|
| D1 | **Pharmaceutical mapping** | EXIOBASE `Chemicals nec` vs a pharma-specific intensity | Chemicals nec (Scenario A) | Decides the **identity of the top contributor**: under A pharmaceuticals hold rank 1 in every Monte Carlo draw; under B medical and electrical equipment takes rank 1 with P = 0.85. This reversal is a mapping choice, not a finding |
| D2 | **Capital boundary** | excluded / exogenous CFC / endogenised | excluded in headline | +13.2 % to +21.0 % on climate. Excluded keeps comparability with Steenmeijer, Eckelman, Lenzen, Pichler; Malik 2018 includes it, which partly explains their higher 7.2 % |
| D3 | **Scope boundary** | health only / + eldercare / + childcare | health + eldercare | ±10 % spread. Steenmeijer's Dutch boundary includes childcare, so the third row is the like-for-like comparison with the template |
| D4 | **Eldercare share α** | 2019 detailed SUT (0.4914) vs analysis-year IO table (0.3092) | analysis-year IO | Changes direct emissions and waste. Ofir's original used the 2019 value carried forward |
| D5 | **Visitor travel** | drop it / import the NHS ratio | NHS ratio 0.236, labelled | No Danish source exists for visitor travel. This ratio is the only remaining fully imported parameter |
| D8 | **Nowcast year versus frozen emission year** | 2022 table (ours) / freeze at EXIOBASE 2019 and deflate demand, as Statistics Denmark do | 2022 | Our Danish *economic* block is validated for 2022 and passes; the *emission* accounts end in 2019 (CO₂) and 2017 (other GHGs). Rørmose Jensen & Iliev freeze at 2019 for exactly this reason. Full treatment in [Decision D8](results_2022.md#decision-d8-2022-nowcast-or-the-last-observed-year) |
| D7 | **GWP revision** | AR6 (current) / AR5 (UNFCCC-mandated) | **AR6** | Only ±2 % on climate. Note UNFCCC mandates **AR5** (decision 7/CP.27), so an AR6 footprint is not directly comparable with Denmark's national inventory; an AR5 sensitivity is available and EXIOBASE ships an AR5 row |
| D6 | **Release** | v3.8.2 now / wait for a corrected v3.10.x | v3.8.2 | See A1, A6 |

### E. What Ofir should know in one page

1. The **transport ≈ 40 % finding does not survive** and must come out of the
   manuscript. It is an EXIOBASE Danish shipping misallocation that Statistics
   Denmark has published on, and we reproduce their diagnostic figure exactly.
2. The **background model changed** from v3.10.2 to v3.8.2 because v3.10.2's
   2022 Danish block fails against national accounts. This change is not a
   preference; the health industry's output there is smaller than health final
   demand.
3. **Headline numbers all moved.** Denmark 2022, full footprint: climate
   4,675.5 kt, materials 4,257.2 kt, water 95.4 Mm³, land 4,851.8 km², waste
   259.3 kt. The supply-chain component alone is 3,906.4 kt of climate; the
   difference is the Danish bottom-up items, which are almost entirely climate.
   (Since 11 September 2026 the sea-transport target share $\phi$ is read from
   Statistics Denmark's own table for the background year rather than a fixed
   0.09; see ["Correction target read from the DST table per year"](#correction-target-read-from-the-dst-table-per-year)
   below.)
4. Three bottom-up items are now **Danish primary data** rather than scaled Dutch
   proxies: anaesthetics (medstat register), patient travel (national travel
   survey), pMDI (Danish EPA). One of them was carrying a unit error.
5. The **uncertainty is essentially all MRIO** (78.4 % of variance, current
   figure; see [docs/revision/uncertainty.md](uncertainty.md)). The bottom-up
   items the reviewers questioned contribute under 0.5 % each. That is a more
   useful answer to the review than the tornado alone.
6. Six decisions in section D are still open and are yours.

### F. Verifications that passed

These are recorded so that a reader knows what *was* checked, not only what
failed.

- **The Steenmeijer Z-column construction is implemented exactly.** Their
  formula is $f_{\text{services}} = \mathbf{Z}(:,h) \times (E_H / x_h)$ where $x_h$ is the health
  industry's **total input**, intermediate use *plus* value added. On our model
  $\sum_i Z_{i,h} + \sum_i V_{i,h} = x_h$ holds exactly (11,730.9 + 32,224.5 =
  43,955.5 M€), and $\mathbf{A}(:,h) = \mathbf{Z}(:,h)/x_h$ by construction, so our
  $\mathbf{A}(:,h)\,E_H$ is their formula.
- **The demand vector entering the MRIO is correspondingly smaller than health
  expenditure**, as it must be: 13,067 M€ against 40,597 M€ of Danish health and
  eldercare expenditure (32.2 %). Steenmeijer's equivalent is 26,283 against
  92,515 M€ (28.4 %). The difference is value added, which has no upstream
  footprint.
- **An independently rebuilt characterisation reproduces the pipeline.** Building
  the climate row from the workbook without reference to the production code
  reproduces the pipeline's Danish health-care supply-chain footprint, now
  3,906.4 kt CO₂e on IPCC AR6 with the shipping correction applied, $\phi$ read
  per year.
- **The national total reconciles**: supply chain 67,518.6 kt plus household
  direct 9,722.0 kt equals the 77,240.6 kt reported by
  `analysis.national_totals`.
- **All six IO accounting identities pass** at ≤10⁻¹⁰
  (`analysis.validate_io_identities`).

### Findings of 8 September 2026

#### F1: `contribution` and `hotspot` were labelled with the wrong node index

**Severity: high (misleading), zero effect on values.**

The two analyses inherited from the original code are named the opposite way round
from how a reader will guess, and the long-format outputs compounded the
confusion by giving *both* the `producing_*` column prefix:

| Analysis | Formula | Indexed by | Was labelled | Now labelled |
|:---|:---|:---|:---|:---|
| `hotspot` | $\mathbf{B}\,\mathrm{diag}(\mathbf{L}y)$ | producing node | `producing_*` ✓ | `producing_*` |
| `contribution` | $\mathbf{B}\,\mathbf{L}\,\mathrm{diag}(y)$ | purchased product | `producing_*` ✗ | `purchased_*` |
| `intensity` | $[\mathbf{B}\mathbf{L}]_j$ | purchased product | `producing_*` ✗ | `purchased_*` |

Consequence if read naively: the domestic share of the climate footprint is
**26.3 %** on the producing-node basis and **61.7 %** on the purchased-product
basis. A reader taking `contribution_by_producing_node.csv` at face value would have
reported that 62 % of the footprint *arises* in Denmark, when the correct figure for
that claim is 26 %. For a manuscript whose title is *geographical displacement of
impacts*, that is the central number.

**Fixed** in `analysis.eriksen_tables` (`rename_map()`, and `ANALYSES` now carries
the node prefix explicitly) and in `analysis.detail_tables.domestic_import_split`
(new `country_column` argument). Files regenerated; values unchanged; all seven
consistency checks still pass. File *stems* keep the legacy words for continuity
with the submitted manuscript, but the schema now disambiguates them.

#### F2: Numbers quoted in the revision docs had drifted from the gold outputs

**Severity: medium.** Six figures quoted in
[docs/revision/results_2022.md](results_2022.md) and in this file no longer
reproduced, having been written before the AR6 restatement and the waste
correction:

| Quantity | Quoted | Actual |
|:---|:---|:---|
| Transport share after correction | 18.9 % | 18.5 % |
| DK sea transport node, before | 822 kt | 852 kt |
| DK sea transport node, after | 71 kt | 74 kt |
| Health-care MRIO supply chain | 3,859 kt | 3,943 kt |
| Danish national footprint, corrected | 76.5 Mt | 77.5 Mt |
| National supply chain / household direct | 66,745 / 9,709 kt | 67,755.5 / 9,722.0 kt |

Two of these were also mutually inconsistent between documents (76.5 Mt against
77.5 Mt for the same quantity), which is how the drift was found.

**Fixed**, and guarded: `analysis.audit_consistency` check **C6** now re-reads a
registry of headline numbers out of the markdown and fails if any of them stops
matching the gold outputs. Prose can still drift; the numbers can no longer drift
silently.

### Findings of 11 September 2026

#### Correction target read from the DST table per year

**Severity: medium.** The sea-transport correction's target share $\phi$
stopped being the hardcoded 0.09 - Rørmose Jensen & Iliev's (2022) single
published figure for 2019 - and is now read from Statistics Denmark's own
domestic input-output table for the background year the run uses: **0.0774**
for 2016 and **0.0651** for 2022. Their 2019 table is kept as the cross-check
that this reading reproduces their published figure: it returns **0.0931**,
within 0.3 percentage points of 0.09. Every gold table under
`data/gold/results/` was republished; this is the full before-and-after,
old against new, of every headline number the change touched. The old column
is the model with $\phi = 0.09$ applied to both background years; the new
column is $\phi$ read per year as above. Both uncorrected variants were
re-run and are byte-identical, as they must be.

| Quantity | Old | New | Change | Change, % |
|:---|---:|---:|---:|---:|
| $\phi$, 2016 background | 0.0900 | 0.0774 | −0.0126 | −14.1 |
| $\phi$, 2022 background | 0.0900 | 0.0651 | −0.0249 | −27.7 |
| Output released, 2016 background, M€ | 9,955.9 | 10,151.0 | +195.1 | +2.0 |
| Output released, 2022 background, M€ | 11,509.8 | 11,953.9 | +444.2 | +3.9 |
| **2022 climate footprint, kt CO₂-eq** | **4,712.4** | **4,675.5** | **−37.0** | **−0.78** |
| 2022 MRIO supply-chain component, kt | 3,943.4 | 3,906.4 | −37.0 | −0.94 |
| 2022 transport, purchased product, kt | 595.8 | 566.5 | −29.3 | −4.9 |
| 2022 transport, producing node, kt | 728.2 | 695.1 | −33.1 | −4.5 |
| 2022 Danish sea transport as a producing node, kt | 74 | 53.0 | −21 | −28 |
| 2022 Danish national footprint, kt | 77,477.5 | 77,240.6 | −236.9 | −0.31 |
| 2022 health-care share of the national footprint, % | 5.09 | 5.06 | −0.03 | −0.63 |
| Monte Carlo median, 2022, kt | 4,734 | 4,697 | −37 | −0.78 |
| Monte Carlo 95 % interval, kt | 4,064–5,531 | 4,032–5,488 | −32 / −43 | −0.79 / −0.78 |
| **2019 climate footprint, corrected, kt** | **4,085.4** | **4,054.8** | **−30.6** | **−0.75** |
| 2019 transport, purchased product, kt | 813.0 | 788.9 | −24.1 | −3.0 |
| Bridge: correction step, net kt | −2,275.0 | −2,305.6 | −30.6 | +1.3 |
| Bridge: year step, net kt | +627.0 | +620.7 | −6.3 | −1.0 |
| 2019 uncorrected variant, all 28 files | — | — | **byte-identical** | 0 |
| 2022 uncorrected variant, all 28 files | — | — | **byte-identical** | 0 |

Old values are the gold tables as committed before the change (commit `c536fe4`),
taken before anything was rebuilt, except the two producing-node rows, which
are the published figures the documents already carried; the Danish
sea-transport node was reported to the unit, so its change is given to the
unit too.

The direction is the same everywhere and the magnitude is small: reading the
share per year lowers the 2022 footprint by 0.8 % and the 2019 one by 0.7 %,
and moves no ranking. What it removes is an assumption - that a share
published for one year holds for every year - at the price of one extra
bronze read. The full band of $\phi$ values, and what each is worth, is in
[docs/methods/replications.md, section 10](../methods/replications.md#r10-sensitivity)
and in `10_sea_transport_reallocation/phi_sensitivity_2016.csv` and
`phi_sensitivity_2022.csv`: tripling $\phi$ from 0.05 to 0.15 moves the 2022
total by 3.2 %.

**Fixed and current.** `docs/revision/results_2022.md`, "The withdrawn
transport finding", carries a one-line pointer to this table rather than a
second copy of it, so a claim-tree document never quotes an old value: **C6**
would fail on it and the ban on superseded strings (**C6b**, below) would
have to be skipped for that document. `analysis.audit_consistency`'s
`SUPERSEDED_TEXT` registry should gain the old-column values above as banned
strings, with this document (and any "as submitted" or "as first implemented"
historical sentence) as the allowed exception; see the phi-correction task's
own report for the exact entries.

---

## Methods and data soundness: response to the eight review requests

**A dated snapshot, kept for the record.** This is the response to the eight
requests raised on 7 September 2026, quoting the branch state on the day it was
written (`2019-update`, 22 commits). Everything below is implemented, run, and
committed unless explicitly marked as remaining work. **Numbers here are NOT
updated when later work supersedes them; where a later document disagrees, the
later document carries the current position.** [`request_checklist.md`](request_checklist.md)
is the up-to-date status ledger; this section is the technical narrative behind
one specific round of it.

> **Editorial note added during the docs-consolidation pass.** Two figures below
> are now superseded and are flagged at the point they occur rather than
> silently corrected: the Scope 2 value in item 2 (401.5 kt, 8.2 % of the total)
> is superseded by the current pipeline's **72.7-75.0 kt, 1.6 %** (see
> [anomaly C1](#c1-scope-2-is-far-below-the-independent-benchmark-medium-open)
> and [docs/revision/results_2022.md](results_2022.md)); and the MRIO variance
> share in item 3 (88.7 %) is superseded by the current **78.4 %** (see
> [docs/revision/uncertainty.md](uncertainty.md)). Both are dated snapshots from
> an earlier pipeline state, exactly as this section's own preamble warns.

### 1. Units: EXIOBASE is in euros; why did you write $M? *(highest priority: it would contaminate everything)*

**We do not use dollars anywhere in the model.** EXIOBASE's `unit.txt` declares
`M.EUR`, and every monetary quantity in the code, the tables, and the figures is
million euro. I grepped the whole `src/` tree for `$M`, `M$`, `USD`, and `US$`:
**no hits.** The "$ millions" you saw came from quoted comparative literature,
namely Karliner et al. 2019 Appendix A (WIOD, USD), Lenzen et al. 2020 and
Pichler et al. 2019 (both USD), which are labelled as those studies' own units.

Fixed regardless: every exported table now carries an explicit `unit` column,
the data dictionary states the convention, and the DKK→EUR rate is the
Danmarks Nationalbank annual average for the analysis year (7.4396 for 2022).

### 2. Scope 1-3 without double counting, with the equations right

We read Wood & Hertwich (2018) and Cabernard et al. (2019 + SI, 2022 + SI) and
implemented their formalism rather than paraphrasing it.

**Theory, applied to our case.** With a *single* target (Danish healthcare final
demand), $f = d\cdot\mathbf{L}\cdot y_H$ already allocates each emission exactly once (Wood &
Hertwich p. 5): allocating production emissions to final demand sums to the
total, unlike the embodied-flow table $\mathbf{E}_Z$. Cabernard's correction (their
eq. 9, the $q_T = \text{rowsum}(\mathbf{Y}_{T,\text{all}} + \mathbf{A}_{TO}\,\mathbf{L}'_{OO}\,\mathbf{Y}_{O,\text{all}})$ construction) bites when
scope-3 vectors of several *intertwined* targets are aggregated, the source of
their 20-30 % (2019) and ~80 % (2022) overestimates. For us it collapses to the
intra-sector self-supply term, which we quantified and handled. The full
implementation is in [docs/methods/replications.md, section 03](../methods/replications.md#r03).

**What we changed:**
- **Scope 2 now uses the energy-block inverse** $\mathbf{L}_{EE} = (\mathbf{I}_{EE} - \mathbf{A}_{EE})^{-1}$ over
  electricity/steam/heat nodes, so generation is reached through transmission
  and distribution *without leaving the energy block*; fuel extraction,
  refining, and grid hardware correctly stay in Scope 3 (GHG Protocol
  category 3). The previous full-$\mathbf{L}$ version is kept as a reported sensitivity
  (401.5 vs 404.2 kt, **both dated snapshots**; see the editorial note above).
- **Self-supply loop:** because the services component is $y = \mathbf{A}(:,h)\,E_H$, the
  footprint contained $s_h(L_{hh}-1)E_H$ = **3.2 kt CO₂e** of the health sector's
  own direct emissions, overlapping the national-accounts Scope 1. This term was
  removed. I first tried zeroing the demand element and **rejected that**: it
  also deletes the legitimate upstream chain of internally traded health services
  (a 27 kt over-correction). Only the direct term is removed.
- **Verified identity** $F_{\text{services}} = (m_h - s_h)\,E_H$ to $7.5\times10^{-12}$: the
  Z-column construction yields a *pure upstream* quantity, making it the exact
  complement to a national-accounts Scope 1. (Using the true final-demand column
  instead would have double counted Scope 1 outright.)
- **Exact partition asserted in code:** $S_1 + S_2 + S_3 + \text{outside} = \text{total}$, and
  the producing-node detail must reconcile.

**Denmark 2022 (as of this snapshot): S1 142.2 | S2 401.5 | S3 4,085.7 | outside protocol 242.5 kt CO₂e.**
Scope 2 at 8.2 % of the total matched Arup/HCWH's independent WIOD estimate for
Denmark (8.3 %) almost exactly at the time this was written. Their Scope 1 share (11.6 % ≈ 0.51 Mt) is ~3×
what Denmark's own accounts report for the entire Q sector (0.17 Mt), evidence
for national-accounts anchoring. **These scope figures are superseded**; see
the editorial note above and
[docs/revision/results_2022.md, "Headline results"](results_2022.md#headline-results-denmark-2022)
for the current S1/S2/S3/outside-protocol partition.

`double_counting_ledger.csv` tests every overlap numerically. Cleared: the
pharma component vs provider chemical procurement (different channels: SHA
retail/marketed-government vs procurement) and all bottom-up items. **Flagged:**
provider equipment purchases are *zero* in EXIOBASE's `Z` because they sit in
gross fixed capital formation, a boundary **gap**, not an overlap, and per Wood
& Hertwich the largest single omission for a service sector like health care.

### 3. Is the Monte Carlo right, mathematically and statistically? What can we learn from IEooc?

We audited our first version against the IEooc `Methods5_Exercise4b` notebook
and the published literature, then rebuilt it. Findings and fixes:

| defect | fix |
|:---|:---|
| MRIO parameter uncertainty absent → intervals ~2× too narrow | added as one shared multiplicative factor calibrated to **Lenzen et al. 2020 SI Tab. SI 7.1** (Danish health-care GHG 2.84 ± 0.24 Mt = **8.35 % relative SD**), the only published MC of this exact quantity |
| price-base-year correction (0.97) hidden inside a distribution, so the point estimate sat off-centre in its own interval | all multipliers now median 1 (MC median reproduces the deterministic model); price/waste/pharma are **discrete scenarios** |
| waste GSD 1.5 alone drove −53/+120 % and implied the reference-year error was unbiased and log-symmetric | moved to a 0.5/1.0/2.0 **scenario band** |
| commuting and visitor travel treated as independent though both are transplants of the same Dutch study | shared method factor, ρ = 0.8 (ρ ∈ {0, 0.5, 0.8} reported) |
| ranking probabilities invalid: six of nine groups had zero variance; pharma scored P(rank 1)=1.0000 | rebuilt: group totals evaluated at the **same draw**, every group carries uncertainty, the shared MRIO factor correctly cancels |
| pharma ratio clipped at 1.0, creating a point mass | truncated lognormal |
| n = 10,000 marginal for the waste tail | n = **100,000**; verified against the **closed-form moments** of the lognormal sum |

**Result (as of this snapshot): CV 7.9 % for climate, directly comparable with Lenzen's published
8.35 % for Denmark.** Scenario A median 4,897 [4,206-5,721]; Scenario B
(pharma-specific intensity) 3,844 [3,206-4,741]. **These figures are superseded**
by the current Monte Carlo run; see
[docs/revision/uncertainty.md](uncertainty.md) for the current median (4,697 kt),
interval (4,032-5,488 kt), and CV (7.87 %).

**Exact first-order variance shares (as of this snapshot)** (free for an additive independent model,
better than a tornado): **MRIO 88.7 %**, visitor travel 5.9 %, commuting 5.3 %,
direct 0.12 %, anaesthetics 0.01 %, pMDI 0.004 %. **Superseded**; the current
shares (MRIO 78.4 %, the correlated travel pair 9.4 %, visitor travel 6.8 %,
commuting 5.2 %) are in
[docs/revision/uncertainty.md](uncertainty.md#2-the-monte-carlo-explained-from-first-principles).
The honest message for the reviewers was, and remains: the bottom-up items they questioned contribute
**under 0.02-0.1 %** of the variance; the uncertainty is essentially all MRIO.

**Ranking result worth publishing:** under Scenario A pharmaceuticals & chemicals
rank 1 in every draw; under Scenario B medical/electrical equipment takes rank 1
with P = 0.85. *The identity of the top contributor is decided by the
pharma-mapping choice, not by parameter noise.* This ranking finding is not
superseded; only the interval and variance-share numbers above are.

Adopted from IEooc: the violin/distribution plot, the CV column, explicit
statement of what is held fixed (A and L), and the `Software2` aggregation-matrix
pattern. **Not** adopted: their N = 200, their `mean ± sd` on skewed output, and
their sampling idiom. `np.log(np.random.lognormal(mean, sd))` cancels the
lognormal transform and overflows on large cells (in the shipped solution this
idiom silently zeroes 109 cells carrying 53.8 % of German final demand). Their
exercise propagates one input with survey SDs; it is a teaching example, not a
submission-grade template. We cite Lenzen SI 7 as the method precedent.

### 3b. "What do you mean by a single target?" You were right to push

My framing was sloppy. Danish healthcare spans **many** EXIOBASE nodes, and the
answer depends on which question is asked:

* the **final-demand footprint** (our headline) is additive for any number of
  target nodes: no correction needed, ever;
* the **target-sector scope 3** (Cabernard's question) double counts
  target-to-target deliveries and *does* need eq. 9.

So I implemented eqs. 8/9/12 and measured it for three nested target sets
(`03_cabernard_target_scope3/`):

| target set | nodes | naive | corrected | double counting |
|:---|:---|:---|:---|:---|
| Danish health and social work | 1 | 0.9 Mt | 0.9 Mt | 1.3 % |
| health and social work, all 49 regions | 49 | 1,129 Mt | 1,100 Mt | 2.6 % |
| + chemicals and medical instruments, all regions | 147 | 3,093 Mt | 2,511 Mt | **18.8 %** |

The complement identity $d\,\mathbf{L}\,\mathbf{Y}\,\mathbf{1} = e_{T,\text{wdc}} + d_O\,\mathbf{L}'_{OO}\,\mathbf{Y}_O\,\mathbf{1}$ holds to
$2\times10^{-16}$, confirming the implementation. **The practical lesson:** for one Danish
health node the correction is 1.3 %, but the moment pharmaceuticals and device
manufacturing enter the target set (which is exactly what the planned
sub-sector disaggregation does), it is nearly a fifth. That correction is now
implemented rather than promised. (The current, more detailed measurement of
this three-tier table, with a third target set going further, is in
[docs/methods/replications.md, section 03](../methods/replications.md#r03).)

### 4. Proper CSV tables with correct schemas, most detailed first

**Now organised by approach**, as you asked, each folder holding the outputs of
one named method, with `manifest_lineage.csv` at the root mapping every file to
its approach, script, equations, published reference, inputs, and content hash:

```
00_core_footprint/           01_eriksen_replication/    02_scopes_wood_hertwich/
03_cabernard_target_scope3/  04_uncertainty_lenzen_ieooc/
05_waste_dst_accounts/       06_benchmarks_validation/     scenarios/
```

[docs/methods/methods.md](../methods/methods.md) documents each approach with its equations and
references. The detailed tables are all long-format with explicit units:

| file | grain |
|:---|:---|
| `footprint_by_producing_node.csv` | indicator × demand component × **producing** country ISO3 × sector (complete, unthresholded) |
| `footprint_by_purchased_product.csv` | same for the **purchased** product and its supplying region |
| `footprint_bilateral_producer_x_purchase.csv.gz` | the full 4-D array $E_{ij} = s_i\,L_{ij}\,y_j$: largest cells covering ≥99.5 % **plus an explicit remainder row so totals reconcile exactly** |
| `scopes_by_producing_node.csv` | scope × indicator × producing country × sector |
| `extended_indicators_by_producing_node.csv` | the ten additional pressures, same schema |
| `expenditure_vector_detail.csv` / `expenditure_summary.csv` | y_H and its relation to basic-price expenditure |
| plus | uncertainty totals/variance shares/rankings/parameters, scope-boundary scenarios, waste validation, double-counting ledger, benchmark and denominator comparisons |

Your schema is honoured exactly: `consuming_country_iso3` (always DNK),
`producing_country_iso3`, `producing_sector_code/name`, `purchased_country_iso3`,
`purchased_sector_code/name`, `value`, `unit`, plus `world_region` and
`sector_group` so any aggregation is a `groupby`. **ISO3 for countries; the five
rest-of-world regions keep their own labels** (WA/WL/WE/WF/WM), taken from the
existing `classifications.xlsx` correspondence. Verified: producing-side,
purchased-side, and bilateral totals agree to machine precision, and the
difference from `table_1` is exactly the direct operational row.

### 5. Waste: all sources explored and tested before settling

We tested every option with real data rather than reasoning in the abstract.

**The inherited hybrid-2011 extension fails three independent tests:**
1. *Absolute:* it implies 647 kt of direct waste for Danish health care in 2022;
   Denmark measures **51.8 kt** (AFFALD01, Q), **12.5× too high**. For the same
   year 2011 it is 4.7× the measured value.
2. *As a coefficient:* 2.32 t per m DKK vs DST's measured direct intensity of
   0.154, **15× too high**, and 3.2× DST's entire direct+indirect multiplier.
3. *As an allocation key* (your suggestion, tested properly): its 2011 Danish
   sector structure is **statistically uncorrelated** with the measured 2011
   structure (Pearson r = −0.19, p = 0.56). It puts 74.8 % of Danish waste on
   agriculture where DST has 1.3 %, and 0.5 % on construction where DST has 43 %.

The reason is conceptual, not a matter of reference year: the hybrid account is a **total-residuals**
account. Livestock manure is 74 % of the Danish total, and **69 % of our
"waste" footprint is mining overburden plus manure**. It is not waste as any
statistical office defines it.

**Eurostat cannot rescue it:** `env_wasgen` has **no NACE Q at all** (health is
inside a G-U services aggregate) and covers 29 of 49 EXIOBASE regions,
**21.6 %** of our footprint by tonnage.

**What we adopted.** Denmark uniquely publishes IO-based waste multipliers on the
same 117-industry classification as its IO tables (`AFF1MU1N`/`AFF3MU1N`).
Applying them to the healthcare final demand gives a **domestic** waste footprint
of **216.0 kt (52.1 kt direct), of which 17.0 kt hazardous**, implied multiplier
0.715 t per m DKK against DST's own individual-government-consumption multiplier
of 0.786, an independent check agreeing within 9 %. The DST model is
domestic-closed, so the imported half is reported **separately and relabelled**
as upstream solid residuals, not waste. DST's own accounts are Denmark's Eurostat
submission (95.7 % agreement with `env_wasgen` for services), so this treatment
is Eurostat-consistent rather than an alternative to it. (Current 2022 waste
figures are in
[docs/revision/results_2022.md, "Waste boundary"](results_2022.md#waste-boundary-what-the-filter-does-and-does-not-establish).)

### 6. Childcare and the scope boundary: should we include it, what do others do?

We implemented it as a switch (`HC_SCOPE`) and ran it for all five indicators:

| boundary | expenditure | GWP | share | t/cap |
|:---|:---|:---|:---|:---|
| health only | €31,079 M | 4,405 kt | 6.81 % | 0.750 |
| **health + eldercare (default)** | **€40,597 M** | **4,875 kt** | **7.53 %** | **0.830** |
| + childcare ("zorg en welzijn") | €49,709 M | 5,325 kt | 8.23 % | 0.907 |

Data exist for all three (purpose 13301 in the public 2022 IO workbook).
**What others do:** SHA-based studies (Pichler, Karliner/Arup, OECD-Doucet)
include long-term health care but **not** childcare; Steenmeijer's Dutch boundary
*does* include childcare and youth care because CBS bundles "zorg en welzijn";
Malik et al. exclude aged care entirely; Lenzen's Danish boundary excludes
residential care but includes veterinary. **Recommendation:** keep health +
eldercare as the headline (SHA mainstream, comparable with the Danish policy
audience) and report the third row as the like-for-like comparison with the
Dutch template. The spread is only ±10 %.

**All impact categories:** we now carry **15**: the five Steenmeijer categories
plus PM2.5, PM10, NOx, SOx, NH₃, NMVOC, final and gross energy, and reactive N
and P to water. This set matches Lenzen's stressor families and gives the
inventory side of an Eckelman-style health-damage analysis (no DALY conversion
applied; that needs an LCIA model with defensible endpoint factors).

### 7. FIGARO for Denmark 2022

We downloaded and used it. Eurostat's official FIGARO-based GHG footprint
(`env_ac_ghgfp`) gives Denmark **57.40 Mt CO₂e (2022)**, against DST AFTRYK's
62.93 Mt and our model's 64.72 Mt, so the healthcare **share is 7.5-8.5 %
depending on the denominator**, now reported as a range with all three named.
FIGARO also puts emissions arising in NACE Q due to Danish final demand at
176 kt (Q86 alone 97 kt), corroborating our 142 kt Scope 1 plus the intra-health
chain. FIGARO supply/use tables for DK 2022 and 2024 are in
`data/bronze/eurostat_figaro/`. **Assessment:** at A64 resolution FIGARO separates Q86
from Q87-Q88 and has C21 pharmaceuticals separately, so it is a genuine
cross-model benchmark and a plausible import-structure source, but its 64
industries cannot substitute for the confidential ~2,350-product DST SUT for
health disaggregation. (See also
[docs/methods/methods.md, "Which external models and datasets we actually use"](../methods/methods.md#which-external-models-and-datasets-we-actually-use-and-why),
which explains why FIGARO is kept and OECD ICIO is not.)

### 8. Volatile anaesthetics: how far can we go?

The N₂O half is solid (national inventory, 38 t/yr → 11.3 kt CO₂e). The volatile
half (1.4 kt) is a population-scaled Dutch figure, because **halogenated agents
are outside the Kyoto basket and appear in no national inventory**.

The method now exists in the literature: **Talbot, Holländer & Bentzer (2025),
*Lancet Planetary Health*** (PMID 40120629), a sales-based estimate from IQVIA
data, 91 countries, GWP100, global impact falling 27 % to 2,005 kt CO₂e in 2023.
Denmark can be done identically and openly: volatile anaesthetics are recorded
under **ATC N01AB** in the Danish medicines statistics (medstat.dk, hospital
sector), the same source the Danish EPA already uses for the official pMDI
inventory. That is the recommended next data step, and it is what the 2022
re-analysis does; see
[docs/revision/results_2022.md, "Bottom-up anaesthetic gases"](results_2022.md#bottom-up-anaesthetic-gases).

**Materiality, stated plainly:** the whole anaesthetic item is 12.7 kt of
4,875 kt (0.26 %), and its exact variance share is **0.01 %**. A factor-of-three
error moves the headline by under 0.06 %. Double counting checked: DRIVHUS
F-gases for hospitals (9 kt, refrigeration) do not include anaesthetics, and
hospital N₂O is netted out before the bottom-up item is added.

### Remaining work (as of this snapshot)

1. medstat ATC N01AB extraction for the Danish volatile-anaesthetics estimate.
   **Done for 2022**; see
   [docs/revision/results_2022.md, "Bottom-up anaesthetic gases"](results_2022.md#bottom-up-anaesthetic-gases).
2. Imported waste: no source exists; currently reported separately as residuals.
3. Capital (GFCF) is excluded, as in Steenmeijer (per Wood & Hertwich the
   largest single boundary omission for health care). Now quantified in
   [docs/revision/results_2022.md, "Capital (GFCF) treatment"](results_2022.md#capital-gfcf-treatment)
   with an exogenous and a fully endogenised
   scenario. **Correction:** an earlier draft of this note attributed the zero
   intermediate purchases of medical instruments to the capital boundary. That
   was wrong. The zero is a defect in EXIOBASE v3.10.2, which carries ~zero
   output for industry 33 across all European regions in both 2016 and 2022
   ([`../methods/exiobase_release_and_classification.md`](../methods/exiobase_release_and_classification.md)).
4. Patient/visitor travel still has no Danish source (verified absent), the
   only remaining component with no national anchor.
5. **Closed since:** the eldercare share α is no longer carried from 2019. It is
   now read from the analysis year's own IO table (industry 880000's deliveries
   to eldercare vs childcare): **α = 0.3092 for 2022**, not 0.4914. Direct
   emissions fall to 118.6 kt and direct waste to 42.8 kt, and the two accounts
   now use the same α by construction.
6. Danish-SNAC hybrid and the Lenzen/Malik-style sub-sector disaggregation, for
   which Cabernard eq. (9) *will* be required and is already documented in
   [docs/methods/methods.md](../methods/methods.md).
