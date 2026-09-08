# Assessment of Ofir et al. (2026) against the 2022 re-analysis

We read the full submission package in `docs/ofir_et_al_2026/`: revised manuscript,
appendices A and B, reviewer responses, SI figures, and cover letter.

Findings are ordered by how much they change the paper. Each carries the test that
produced it, so none has to be taken on trust. Where the manuscript is right and our
pipeline was wrong, that is stated too.

---

## F1: The demand vector omits roughly a third of health-care services expenditure

**Severity: critical. It changes every reported number.**

Appendix A enumerates the Danish SUT cells by hand, as (transaction × purpose) pairs.
Running the same extraction over the 2019 table, our components reproduce the manuscript
almost exactly for two of three categories, which is what makes the third one decisive:

| Component | Manuscript 2019 | Our extraction, 2019 | Agreement |
|---|---|---|---|
| Pharmaceuticals | 1,735 M€ | 1,771 M€ | **2 %** |
| Medical appliances | 901 M€ | 911 M€ | **1 %** |
| **Health care services** | **23,221 M€** | **32,617 M€** | **−29 %** |

Pharmaceuticals and appliances agreeing to within 2 % rules out a price base, exchange
rate, or boundary explanation. The services gap is ~70 bn DKK, and it is concentrated in
individual-consumption cells the hand-enumerated list does not reach: above all
**non-market government consumption of residential care**, 57.9 bn DKK in 2019 alone,
plus other individual health consumption and NPISH hospital cells.

The paper defines its own scope as *"Health and social care services (including
residential & elder care)"*. On the demand vector actually used, publicly provided
eldercare, which in Denmark is nearly all eldercare, is largely absent.

**Consequence.** Table 1's services row, and therefore the headline for all five impact
categories, is understated. This omission is not a modelling choice to be defended in a
limitations paragraph; it is a missing block of the final-demand vector.

**Already fixed here.** `analysis.extra_functions` sums *all* individual-consumption
transaction columns (3110, 3130, 3141, 3142) for each purpose rather than enumerating
pairs, so a purpose cannot be silently half-covered. Recorded in
`docs/revision/bug_and_method_fixes.md`.

---

## F2: pMDI emissions are overstated about threefold

**Severity: high.** Appendix A scales the Dutch pMDI footprint by defined daily doses:
(28 / 62) × 76.9 kt = **34.6 kt CO₂e**.

Test it as a mass balance. At the ReCiPe GWP100 factor Steenmeijer use for HFC-134a
(1,549 kg CO₂e/kg), 34.6 kt implies **22.4 t of HFC propellant dispensed in Denmark**.
Vestbo & Press-Kristensen (2023), from Danish pharmacy dispensing data, measure **7.2 t**.

The implied intensities make the problem plain:

| | HFC per DDD |
|---|---|
| Netherlands, implied by Steenmeijer | 0.801 g |
| Denmark, measured | 0.257 g |

The gap is a factor of 3.1. The appendix itself notes that *"Denmark [has] a substantially
higher dry-powder inhaler (DPI) uptake than the Netherlands"* and then scales by pMDI DDD anyway,
which only works if HFC per pMDI DDD is equal in the two countries. It is not.

**The corroboration is spurious.** The appendix reports agreement with Vestbo &
Press-Kristensen's ~31 kt and calls it *"convergence… supports the robustness of the
dose-based scaling approach"*, while acknowledging in the same paragraph that the two use
different GWP time horizons. If 31 kt is a GWP20 figure, its GWP100 equivalent is
≈ 10.9 kt. That is not corroboration of 34.6 kt; it is contradiction of it. **Two
estimates on different time horizons cannot be compared, and their agreement cannot be
evidence of anything.**

Our 2022 value, 11.6 kt, is the Danish EPA F-gas inventory's actual reported MDI emission
on GWP100 (a national measurement, not a scaled proxy), and it sits almost exactly where
the GWP100 conversion of Vestbo lands.

**Recommendation.** Replace the DDD scaling with Danish primary data and delete the
convergence claim.

---

## F3: Volatile anaesthetics are missing entirely

**Severity: moderate.** The bottom-up covers N₂O and pMDIs. Sevoflurane, desflurane, and
isoflurane, the agents that dominate anaesthetic climate impact in most health systems,
appear nowhere.

Denmark has a mandatory national register for these agents: Medstat ATC N01AB, all sectors.
Our 2022 figure is 1.20 kt CO₂e on the Sulbaek Andersen et al. (2023) GWP100 set with a 5 %
metabolised correction. The item is small, but it is a named omission rather than an
uncertainty.

---

## F4: N₂O is scaled from one region by birth counts when a national measurement exists

**Severity: moderate.** Appendix A eq. A4-A7 scales the Region of Southern Denmark's N₂O
purchases to the country by the ratio of births (5.267), giving 31.9 t N₂O and 9.52 kt CO₂e.

Two assumptions are load-bearing, and neither is tested: that N₂O use per birth is uniform
across regions, and that obstetric use dominates national consumption.

Denmark's National Inventory Document 2024 (DCE report 622) reports category 2.G.3.a
directly: **38 t N₂O per year**. That is a national measurement, 19 % above the scaled
estimate, and it removes both assumptions.

---

## F5: The characterisation is described inconsistently, and partly incorrectly

**Severity: moderate; a reviewer will catch it.**

The main text states ReCiPe 2016 (H) for climate, land use, and blue water, and DESIRE FP7
for material extraction and waste. Appendix A instead describes `Q` as *"characterization
matrices assembled to quantify five impact categories (GWP100, abiotic material extraction,
water use, land use, and waste flows)"*, i.e. EXIOBASE's own characterisation, which is
the DESIRE workbook. The two descriptions are not the same method.

Separately, **blue water in Mm³ and land use in km² are not ReCiPe midpoints.** ReCiPe's
water midpoint is water scarcity in m³ world-equivalent, and its land midpoint is annual
crop-equivalent area; both are weighted. Quantities reported in physical m³ and km² are
*inventory* aggregations of the satellite account. Calling them ReCiPe 2016 (H) midpoints
misdescribes them.

**Recommendation.** State plainly: climate on GWP100 with the vintage named; material
extraction, blue water, and land use as physical inventory aggregations of the EXIOBASE
satellite accounts; waste from the DESIRE extension.

---

## F6: N₂O is characterised on GWP 298 while citing AR6

**Severity: low, but trivially fixable.** Eq. A7 uses GWP100 = 298 (AR4/AR5) and cites the
IPCC AR6 synthesis report. AR6's N₂O GWP100 is **273**. Using 298 overstates the N₂O term
by 9 %. This study reports AR6 throughout.

---

## F7: Patient and visitor travel is scaled by a proxy when Denmark measures it

**Severity: moderate.** Appendix B derives the distance factor as the unweighted mean of
three ratios (commuting, 1.079; errands, 1.402; and all-purpose travel, 1.293), giving
1.258. The appendix is candid that *"none of these categories are perfectly aligned with
patient and visitor travel"*.

Denmark's National Travel Survey has a purpose code that is aligned: TU Table 15, purpose
33 *Social/sundhed* (travel to doctors and hospitals), at 0.9 km/person/day in 2019 and
0.8 in 2022. Using it removes the heuristic entirely.

**Where the manuscript is right and we were wrong.** Appendix B applies the weekly-hours
ratio to commuting (0.5057 activity scaling) but **not** to patient and visitor travel
(0.4292). That is correct (hours worked scale how often staff commute, not how far
patients travel), and our module had the hours ratio in both. We corrected it on
8 September 2026.
No reported number moves, because that item's GWP column is already taken from Danish TU
data, but the derivation now matches the appendix.

---

## F8: The Netherlands is a top-level world region in a Danish study

**Severity: low, but it distorts Figure 3.** Appendix A: *"The original codebase also keeps
the Netherlands explicit, which was deemed safest to leave un-altered."* That is
understandable as a conservative choice, but the consequence is that Figure 3's Europe bar
excludes the Netherlands, and NL appears alongside continents. Denmark is the home region
here.

We fold NL into Europe and single out Denmark. **This change is a deliberate deviation
from the submitted figure and must be declared** if Figure 3 is regenerated.

---

## F9: The transport finding does not survive

**Severity: critical for framing.** The abstract, the Research-in-context panel, and the
cover letter all lead on transport (46 % of GHG in the sector view).

EXIOBASE routes 73.6 % of Danish sea-transport output to Danish intermediate use against
9 % in the national accounts, a defect Statistics Denmark published (Rørmose Jensen &
Iliev 2022) and which EXIOBASE's own hybrid build does not reproduce (7.8 % natively).
Correcting it takes transport from 37.5 % to 18.5 % of the supply-chain footprint.

**The cover letter states this transport share as the key finding.** It will need rewriting
alongside the abstract.

---

## F10: Known pharmaceutical bias is acknowledged but neither bounded nor carried

**Severity: moderate.** Appendix A cites Hagenaars: mapping pharmaceuticals to Chemicals
n.e.c. overstates material extraction by **61 %** and greenhouse gases by **11 %**. The
appendix concludes that no correction factor was applied and results are *"indicative of
chemically intensive supply chains"*.

That is honest, but it leaves the single largest known bias in the study unquantified while
Table 1 attributes 43.5 % of material extraction to that category. At minimum the
Hagenaars adjustment should be carried as a sensitivity so the reader can see the range.
We run it as a structural scenario in the Monte Carlo rather than as a distribution,
because it is a modelling choice and not measurement error.

---

## F11: Venue and format are inconsistent

**Severity: editorial, but it will be noticed on submission.**

The cover letter submits to **Cell Reports Sustainability**, noting the paper was
*"encouraged by the editors"* to move there after The Lancet Planetary Health. But the
manuscript is still in Lancet format: a Background / Methods / Findings / Interpretation
abstract, a *Research in context* panel, and Lancet numbered referencing. Cell Reports
Sustainability uses a different structure.

The titles also differ: the manuscript and cover letter use *"The environmental impacts of
the Danish health care system: supply-chain origins and geographical displacement of
impacts"*; Appendix A is headed *"The Geographical Displacement of Healthcare's
Environmental impacts: A Danish Input-Output Study"*.

---

## What this means for the 2022 re-analysis

The 2022 results are **not** a like-for-like update of Table 1. Three things changed at
once: the reference year (2019 → 2022), the background model (v3.7/2016 → v3.8.2/2022 with
the Danish sea-transport correction), and the demand vector (F1). The last is the largest.

| | Manuscript 2019 | This study 2022 |
|---|---|---|
| Expenditure | 25,857 M€ | 40,597 M€ |
| Climate change | 4,815 kt (5.6 %) | 4,713 kt (6.1 %) |
| Material extraction | 2,601 kt (5.5 %) | 4,261 kt (7.9 %) |
| Blue water | 47 Mm³ (4.3 %) | 95.5 Mm³ (7.5 %) |
| Land use | 2,753 km² (3.6 %) | 4,856 km² (4.9 %) |
| Waste generation | 840 kt (3.6 %) | 259 kt (2.5 %) |

Climate is nearly flat because two large changes offset: a 57 % larger demand vector
against the withdrawal of the phantom shipping emissions. The other four rise roughly with
the demand vector. Waste falls because the 2011 hybrid waste extension was replaced with
Denmark's own SEEA waste accounts, which are 4.6× lower at the health sector, a change of
concept, not a correction of arithmetic.

**The decisive outstanding test** is to run our corrected pipeline on **2019** and compare
with Table 1 directly. That isolates the method change from the year change and would let
the paper state exactly how much of the revision is each. It needs year-aware output
routing first, so that a 2019 run cannot overwrite the 2022 headline, the same guard the
scope scenarios already have. The test is recorded in
`docs/revision/anomalies_bugs_and_open_questions.md` as the next task.
