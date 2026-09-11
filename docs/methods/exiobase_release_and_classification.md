# EXIOBASE in this study: release, and what the classification cannot say

**Audience.** Two. First, the manuscript and its supplementary information: the
version and reference year have to be stated unambiguously, and the nowcast
qualification has to be stated by us rather than found by a referee. Second, any
later project of ours that uses EXIOBASE, because most of what follows is not
specific to Denmark or to health care.

**Status.** Standing reference. This is the full methods statement on release
and classification, decisive for the 2022 headline. The decision it
supports is
[`../revision/results_2022.md`, "Decision D8"](../revision/results_2022.md#decision-d8-2022-nowcast-or-the-last-observed-year);
the defect register behind it is
[`../revision/defects_and_fixes.md`, section A](../revision/defects_and_fixes.md#a-defects-in-the-background-data-exiobase),
section A. For the manuscript-facing limitations statement built on this
decision, see
[`../revision/uncertainty.md`, section 7](../revision/uncertainty.md#7-how-to-read-the-results-given-every-exiobase-limitation).

---

## 1. The sentence the manuscript must contain

> Environmental extensions and the global supply-chain structure were taken from
> **EXIOBASE version 3.8.2**, industry-by-industry monetary tables
> (`IOT_2022_ixi`, 49 regions x 163 industries), reference year **2022**, in
> basic prices, million euro. The Danish demand vector is Danish 2022
> expenditure, so demand year and model year coincide.

Three things in that sentence do work, and all three have been got wrong in
drafts before.

**The version.** `3.8.2`, not "EXIOBASE 3" and not "the latest version". The
release matters more than the family: v3.10.2 and v3.8.2 disagree by a factor of
three on the size of the Danish health industry, and the study rejects v3.10.2
for that reason. A reader cannot reproduce anything from "EXIOBASE 3".

**The table type.** `ixi`, industry by industry. EXIOBASE also publishes `pxp`,
product by product, with a different number of sectors (200 rather than 163) and
different labels. Results are not interchangeable between them.

**The reference year.** 2022, and see section 3 before writing the word
"observed" anywhere near it.

---

## 2. Why the version is not a detail

Reproduce this section's diagnostics with:

```
PYTHONPATH=src .venv/bin/python -m analysis.release_defect_audit
```

which writes `data/gold/results/09_exiobase_release_diagnostics/`.

### 2.1 Why this test was run at all

Rørmose Jensen & Iliev (2022, Statistics Denmark) show that EXIOBASE's Danish
block misallocates output between industries; their headline case is Danish
water transport, 74 % of whose output EXIOBASE sends to Danish intermediate use
against 9 % in the national accounts. Palm et al. (2019) build the same argument
into the SNAC method: for a small, open, highly specialised economy, the
nationally estimated block should replace the MRIO's own. Both papers imply a
test that is cheap and that this project had not run: **compare the EXIOBASE
Danish block, industry by industry, against Statistics Denmark's own published
input-output table for the same year.** Denmark publishes a 117-industry IO
table annually, so the test is direct.

The prompt to run it was an anomaly, not a hunch: the medical-appliance
component of the footprint (1,094 M.EUR of expenditure, 921 kt CO₂e, 22 % of the
climate total) was landing on Greece, China, and the RoW aggregates, with a
Danish contribution of exactly zero.

### 2.2 What the test found: two distinct defects

The test found two **distinct** defects, with different scope and different
consequences.

#### Defect D1: industry 33 is empty across Europe (v3.10.2, all years)

`Manufacture of medical, precision and optical instruments, watches and clocks
(33)` carries essentially zero output in every European region of v3.10.2, in
**both** the 2016 and the 2022 tables:

| Region | v3.8.2 2016 | v3.10.2 2016 | v3.10.2 2022 | v3.8.2 2022 |
|:---|:---|:---|:---|:---|
| DK | 4,919 | 0 | 0 | **6,276** |
| DE | 68,118 | 4.6 | 0 | **76,025** |
| FR | 30,720 | 0 | 0 | **35,274** |
| NL | 12,455 | 0 | 0 | n/a |
| US | 239,045 | 298 | 2,195 | n/a |

*M.EUR total industry output.* The whole-world v3.10.2 2022 total for this
industry is 186,074 M.EUR, against a global medical-devices industry an order of
magnitude larger. The emptiness is not confined to the two years tested here:
across the full v3.10.2 time series the industry never recovers from 2015
onward (see the onset table in
[`../revision/uncertainty.md`, section 7](../revision/uncertainty.md#7-how-to-read-the-results-given-every-exiobase-limitation)
section 2, which frames the same defect by onset year for the manuscript).

This emptiness is a version defect, not a modelling result. Its consequence for
this study is direct and large: with domestic and all European supply set to
zero, the Danish medical-appliance demand can only be met by whichever regions
retain a non-zero i33. The resulting geography (Greece, Russia, RoW) is an
artefact of the empty rows, not a finding about Danish procurement.

It also explains, retrospectively, the **multiplier-outlier screening** that this
project introduced for the v3.10.2 build. That screening was motivated by GB
medical instruments carrying an intensity of 2×10⁸ kt CO₂e per M.EUR. An
emission account divided by an output of zero is exactly what D1 produces. The
screening was treating a symptom.

#### Defect D2: the Danish block is misallocated (v3.10.2, 2022 only)

Against Statistics Denmark's published 2022 IO table (`Total Output` row,
117 industries, converted at 7.4396 DKK/EUR):

| DK industry, 2022 | Nat. accounts | v3.8.2 | ratio | v3.10.2 | ratio |
|:---|:---|:---|:---|:---|:---|
| Health and social work | 45,321 | 43,955 | **0.97** | 16,326 | **0.36** |
| Education | 22,935 | 20,241 | **0.88** | 109,673 | **4.78** |
| Financial intermediation | 18,980 | 21,004 | **1.11** | 76 | **0.004** |
| Machinery n.e.c. | 21,150 | 18,700 | **0.88** | 28 | **0.001** |
| Medical/optical instruments | 9,130 | 6,276 | 0.69 | 0 | **0.00** |
| Real estate | 46,965 | 45,673 | **0.97** | 9,915 | **0.21** |
| *Total, all industries* | *706,281* | n/a | n/a | *681,918* | *0.97* |

*M.EUR.* The **total** is right to 3 %, so output has been redistributed between
industries rather than lost. The table is also internally consistent
($x = \mathbf{Z}\,\mathbf{1} + \mathbf{Y}\,\mathbf{1}$ holds to 7×10⁻¹¹, and no orphan rows appear), so the
discrepancy is a classification/allocation failure upstream of the balancing, not
corruption.

D2 is **year-specific**: v3.10.2's own 2016 Danish block is sound (health
36,756; education 20,369; machinery 33,165 M.EUR). It appears with the nowcast
years. It is also **country-specific**: Germany (health 4.05 % of national
output), France (4.70 %), Italy (4.68 %), the Netherlands (4.22 %), and the
United States (3.43 %) are all plausible in v3.10.2 2022. The affected group is
**Denmark, Bulgaria, Malta, and Switzerland**, which share one signature:
education inflated, health deflated, financial intermediation collapsed to
near-zero.

An independent internal check confirms D2 without leaving the study's own data:
Danish health and eldercare **final** expenditure in 2022 is 40,597 M.EUR. A
health-and-social-work industry whose **total output** is 16,326 M.EUR cannot
deliver it. The v3.10.2 2022 Danish health column is arithmetically impossible.

### 2.3 Consequence and decision

v3.10.2 `IOT_2022_ixi` cannot support this study. The defects fall precisely on
the model elements the method depends on: the health industry column, which is
the source of the services recipe through the Steenmeijer Z-column construction;
the medical-instruments industry, which carries the appliance component; and the
financial and machinery industries, which are part of the services supply chain.

**Decision: the background model is EXIOBASE v3.8.2 `IOT_2022_ixi`.** This
release is the best available combination on all three criteria that matter:

1. *Correct analysis year.* 2022 is the study's agreed year and v3.8.2 publishes
   a 2022 table (Zenodo 5589597).
2. *Sound Danish block.* Every checkable industry group falls within ±12 % of
   Danish national accounts, and the two the study most depends on (health and
   social work, and real estate) within 3 %.
3. *Continuity with the submitted manuscript.* v3.8.2 is the release the
   original submission was built on, established earlier by fingerprinting. The
   revision therefore changes the year and the corrected method, not the model
   family, and reviewers can attribute differences to the corrections rather
   than to a release change.

The v3.10.2 artefacts are retained as `mrio2022_v3_10_2.pkl` and
`leontief2022_v3_10_2.pkl` so that every number in this section can be
regenerated, and so that a v3.10.2 sensitivity remains available.

**What this changes downstream:**

- **Outlier screening is withdrawn for the headline model.** It was introduced to
  contain D1 and is unnecessary once industry 33 has real output. It is retained
  as a diagnostic and reported as a sensitivity.
- **The medical-appliance component must be re-estimated.** Its previous value
  (921 kt, 22 % of the climate footprint, sourced from Greece/China/RoW) was
  built on empty European rows.
- **The transport finding must be re-examined on the corrected model.** The
  earlier conclusion that "transport ≈ 40 %" is release-dependent was itself
  derived partly from the v3.10.2 comparison and has to be re-derived. See
  section 4 below.
- **The case for the Danish SNAC phase is strengthened, not weakened.** v3.8.2's
  Danish block agrees with national accounts on *totals*; that is a necessary but
  not sufficient condition. Rørmose Jensen & Iliev's finding concerns the
  *allocation of intermediate use*, which the recipe-validation diagnostic
  measures separately and which remains the motivation for the SNAC tier (see
  [`methods.md`, "Danish SNAC"](methods.md#danish-snac-what-statistics-denmark-does-what-we-patch-and-the-feasibility-of-a-full-build)).

**The general lesson for other projects.** Never accept an MRIO release for a
country without testing that country's block against its own national accounts,
industry by industry, in the year you intend to use. The test is cheap, it needs
only a published national input-output table, and it catches the failure mode
that a balance check cannot: internally consistent tables with the output in the
wrong industries. Section 6 turns this into a checklist.

### 2.4 What the withdrawn v3.10.2 build actually did

Kept for the record, in the past tense: this is the build this study ran
before D1 and D2 above forced the change to v3.8.2, and it is the origin of
the multiplier-outlier screening referred to throughout this section. None of
it describes the study's method today; the current build is
[`../revision/results_2022.md`](../revision/results_2022.md) §2.

v3.10.2's archive layout differs from v3.8.2's: it shipped $\mathbf{Z}$, $x$
and $\mathbf{Y}$ at the archive root, with satellite extensions stacked across
eight domain folders (733 stressor rows; empty cells set to zero) rather than
the single `satellite/F.txt` v3.8.2 uses. The withdrawn pipeline built
$\mathbf{A} = \mathbf{Z}\,\hat{x}^{-1}$ from that layout and inverted
$\mathbf{L}$ directly. The characterisation bridge had to be rebuilt for the
new stressor names: GWP100 (22 rows), blue water (103 rows), and value added
mapped 1:1 by stressor name from the Steenmeijer/DESIRE selection; abiotic
material extraction (29 rows: metal ores plus non-metallic minerals), land use
(all 26 land-account rows), and employment were rebuilt from the restructured
names under the same concept definitions used for v3.8.2.

**The multiplier-outlier screen existed only for this build, and only because
of D1.** With industry 33 emptied across Europe, an emission account divided
by a near-zero output produced pathological intensities (the GB medical-
instruments case already noted above). The withdrawn pipeline screened for
it: air-emission entries at more than 100× the cross-region sector median, or
sitting on outputs under 1 M.EUR, were replaced by the median intensity times
actual output (96,833 entries). Screening was restricted to air emissions
because extraction, land, and water accounts are legitimately concentrated and
a median test would have crushed real mines (the concentrated-stressor
caution in Jakobs 2023). On the screened v3.10.2 build, the Danish national
consumption-based climate footprint came to **64.7 Mt against DST's official
AFTRYK 62.9 Mt (+2.9 %)**; unscreened, it was **69.3 Mt**. Both numbers
describe the withdrawn build, not the adopted model, whose own Danish
national footprint is **77.2 Mt** on the corrected v3.8.2 background, with
the sea-transport target read from Statistics Denmark's own table for the
background year (see section 4 below and `../revision/results_2022.md` §3;
`data/gold/results/00_core_footprint/national_totals_summary.csv`,
77,240.6 kt).

Outlier screening is retained on v3.8.2 only as a diagnostic and reported as a
sensitivity (section 2.3 above); the headline model needs none of it, because
v3.8.2 has no near-zero-output row in the industries this study depends on.

### 2.5 Honest limits of this test

The concordance in `analysis.release_defect_audit` covers twelve industry groups
whose mapping between the Danish DB07/NACE classification and the EXIOBASE 163
list is unambiguous. It is a plausibility screen, not a full concordance: a group
passing at ±12 % is evidence that the block is not grossly misallocated, not
proof that its input structure is correct. The input-structure question is what
`recipe_validation_2022.csv` addresses, and there v3.8.2 also has known biases
(see
[`../revision/uncertainty.md`, section 7](../revision/uncertainty.md#7-how-to-read-the-results-given-every-exiobase-limitation)
section 1). Neither test was run against a release other than those on disk, so
this section makes no claim about v3.9, v3.10.0 or v3.10.1.

---

## 3. The 2022 table is itself a nowcast

### In plain terms

A global trade database is assembled from national statistics, and national
statistics arrive late. Denmark's 2022 accounts did not exist in 2022. So when
the compilers wanted a 2022 table they could not observe one; they projected the
last year they had forward.

The v3.8.2 distribution's own `metadata.json` records the file as written on
**8 September 2021**. Its "2022" is a forecast made before 2022 happened.

This study rejected v3.10.2 partly because its 2022 nowcast fails against the
Danish national accounts. The honest statement is not that our version is
observed and theirs is projected. **Both are projections. Ours is a shorter one
with a milder and differently shaped error.**

### How far off, measured

Danish total output in the model against the national-accounts total, on the
full 163-to-117 concordance rather than on the twelve unambiguous groups the
release audit uses:

| Year | Model over national accounts |
|:---|:---|
| 2016, a year EXIOBASE observed | **1.01** |
| 2022, the projection | **0.80** |

A fifth of the Danish economy is missing from the 2022 projection. Where it is
missing is the part that matters:

| Group | Model | National accounts | Ratio | Handled where |
|:---|:---|:---|:---|:---|
| Sea and coastal water transport | 19,714 | 78,950 | 0.25 | corrected, section 4 |
| Chemicals and pharmaceuticals | 5,915 | 35,742 | 0.17 | reported as the study's largest limitation |
| Wholesale trade | 28,962 | 53,501 | 0.54 | 2022 prices a 2021 projection cannot see |
| Electricity | 2,540 | 10,789 | 0.24 | as above |
| **Health and social work** | **43,955** | **45,854** | **0.96** | the industry the study models |

None of the four largest gaps is new to this study and none is unaddressed. The
industry being modelled is within 4 % of Denmark's own figure, which is why the
release audit passes on the groups it tests.

### The part with no validation

The economic block was tested. **The emission side was not, because there is
nothing to test it against.** EXIOBASE v3.8.2's CO2 accounts end in 2019 and its
other greenhouse gases in 2017, so the 2022 satellite is an extrapolation of
three to five years on the side that carries the physics. This is the weaker
half of the release argument and it should be stated as such.

### What to write in the paper

Not "EXIOBASE 2022 data" without qualification. Something closer to:

> The 2022 tables of EXIOBASE v3.8.2 are themselves nowcast: the release was
> compiled in September 2021, its CO2 accounts end in 2019 and its remaining
> greenhouse gas accounts in 2017. The Danish economic block was validated
> against Statistics Denmark's published 2022 input-output table and reproduces
> health and social work to within 4 %; the emission side has no equivalent
> validation. Results for 2022 therefore rest on a projected economic structure
> and an extrapolated emission account, and the alternative of freezing the
> background at 2019 with deflated demand is reported as a sensitivity.

Statistics Denmark themselves freeze EXIOBASE at 2019 and deflate demand back to
2019 prices, for a stated reason worth repeating: a flat nowcast holds the
satellite and the characterisation constant while current-price imports inflate,
so **inflation mechanically inflates the footprint**. 2022 was a high-inflation
year in Denmark, which makes the concern live rather than theoretical.

---

## 4. Where the shipping row is explained

This comes up first in every discussion of the Danish block, so the pointers, in
increasing order of technicality:

| Document | What it gives |
|:---|:---|
| [`docs/revision/results_2022.md`, "The withdrawn transport finding"](../revision/results_2022.md#the-withdrawn-transport-finding) | the narrative version, written for a non-specialist and for the manuscript methods section, including the withdrawal of the submitted "transport ≈ 40 %" finding |
| [`docs/methods/replications.md`, section 10](replications.md#r10) | the equations, the calibration target, the effect table, and the validation against EXIOBASE's own hybrid build |
| `src/analysis/dk_shipping_correction.py` | the implementation |
| `data/gold/results/10_sea_transport_reallocation/` | the outputs |
| [`docs/revision/defects_and_fixes.md`, anomaly A3](../revision/defects_and_fixes.md#a3-danish-sea-transport-is-grossly-misallocated-high-fixed) | the defect as registered, with the consequence for the submitted manuscript |

The short version. Statistics Denmark report that EXIOBASE sends **74 %** of
Danish water-transport output to Danish *intermediate* use against **9 %** in the
national accounts, because Denmark operates one of the world's largest merchant
fleets and that fleet carries world trade rather than Danish production. We
measure **73.6 %** on v3.8.2 `IOT_2022_ixi`, which is their figure to the
decimal. EXIOBASE's own hybrid build gives 7.8 % natively with no correction,
which is independent confirmation that the monetary build is the thing at fault.

We reallocate to a target read from Statistics Denmark's own domestic
input-output table for the background year — **6.5 %** for 2022, not the 9 %
figure Rørmose Jensen & Iliev (2022) publish for 2019 alone; reading their
2019 table the same way returns 9.3 %, reproducing their published figure to
0.3 percentage points, which is the check that licenses reading the other
years off the same table (see
[`docs/methods/replications.md`, "Where $\phi$ comes from"](replications.md#r10-phi)
for the per-year values). Total output of the row is left alone, because
it is not in dispute; only the destination of the flows changes, and the released
11,953.9 M.EUR goes to exports. **Transport falls from 37.5 % to 17.8 % of the
supply-chain footprint**, which is 14.9 % of the 4,675 kt total.

**This must be in the manuscript and the SI**, because the submitted paper's most
quotable finding, that transport is 38 to 43 % of the Danish health-care
footprint, is withdrawn by it. The finding was an artefact of a documented
misallocation in EXIOBASE's Danish block, diagnosed by Denmark's own statistical
office rather than by us.

---

## 5. What EXIOBASE calls health care, and why that is a real limitation

### The labels, verified from the distribution

| Table | Label | Code |
|:---|:---|:---|
| `ixi`, industry | **Health and social work (85)** | `A_HEAL`, `i85`, index 137 of the developers' own 0 to 162 numbering |
| `pxp` and the supply-use tables, product | **Health and social work services (85)** | same 85 grouping |

Both read from files on disk: the industry from `classifications.xlsx`
(`disagg_ind`), the product from the v3.8.2 `MRSUT_2020` supply table. The `(85)`
is **ISIC Revision 3, division 85**.

### What sits inside it

EXIOBASE's own developer concordance maps that single industry onto **four**
NACE Revision 2 divisions, and Statistics Denmark's 117-industry grouping
resolves them into five industries:

| NACE rev.2 | DST industry | |
|:---|:---|:---|
| 75 | 750000 | Veterinary activities |
| 86 | 860010 | Hospital activities |
| 86 | 860020 | Medical and dental practice activities |
| 87 | 870000 | Residential care activities |
| 88 | 880000 | Social work activities without accommodation |

So EXIOBASE's health industry contains hospitals, medical and dental practice,
residential care, social work **and veterinary medicine**, in one row, with one
emission intensity.

### Does social work count as health?

Under the classification EXIOBASE uses, yes, because ISIC Rev.3 put them in one
division. Under every classification currently in force, no:

| System | Human health | Residential care | Social work | Veterinary |
|:---|:---|:---|:---|:---|
| **ISIC Rev.3** (what EXIOBASE uses) | 85 | 85 | 85 | 85 |
| **ISIC Rev.4** | 86 | 87 | 88 | 75 |
| **NACE Rev.2** | 86 | 87 | 88 | 75 |
| **NAICS** | 621, 622 | 623 | 624 | 54194 |

ISIC Rev.4 (2008) and NACE Rev.2 (2008) split division 85 three ways and moved
veterinary out of it entirely, into the professional and technical services
section. NAICS reached the same separation from a different direction: sector 62
is "Health Care and Social Assistance", with health care in 621 to 623 and social
assistance standing alone in 624.

The answer to the theoretical question is therefore: **the aggregation is a
statement about the age of the classification, not a claim that social work is a
kind of health care.** All three modern systems treat them as adjacent but
distinct. EXIOBASE is the outlier because it is built on a classification frozen
before the 2008 revisions.

### Why this is not merely academic

It is the reason this study has a boundary problem at all, and it drives a
number the manuscript reports.

Because the model cannot separate them, the **demand vector** must do the work
instead. The study defines its boundary on the expenditure side, using the System
of Health Accounts, and runs three scopes:

| Scope | Boundary | Where |
|:---|:---|:---|
| health only | SHA health, eldercare excluded | `scenarios/health_only` |
| **health and eldercare** | the headline | the configured run |
| health, eldercare and childcare | the expansive Dutch boundary of Steenmeijer et al. | `scenarios/zorg_en_welzijn` |

Residential eldercare is roughly a third of Danish health services expenditure,
so the choice is not marginal, and it cannot be made inside EXIOBASE. It is made
in the demand vector and reported as a sensitivity. **A future disaggregation of
ISIC 85 in EXIOBASE would let the boundary be set on the supply side too**, and
would let hospital intensity be distinguished from social-care intensity, which
at present it cannot be. That, and not the aggregate total, is what a
disaggregated health row would buy.

The same limitation is why `17_health_subsectors` decomposes by SHA function
rather than by industry: the function detail exists in the expenditure data and
has no counterpart in the model's sector list.

### How much the merge actually costs

The size of the loss is quantified in the follow-on layer rather than here,
because it is work for the next paper rather than for this manuscript. What the
manuscript needs is the limitation itself, and it is stated where it belongs: the
published decomposition is pro-rata, three of its five functions therefore share
one intensity exactly, and `17_health_subsectors` reports a ranking
decomposition so that no reader can mistake an expenditure ordering for a
supply-chain finding.

---

## 6. Checklist for the next EXIOBASE project

Ordered by how much damage each catches, and every one of them caught something
here.

1. **Test the country block against national accounts, per industry, in the year
   you will use.** Not the national total, which was right to 3 % in a release
   whose health industry was out by a factor of 2.7.
2. **Read the release's `metadata.json` for the build date before calling any
   year observed.** Compare the build date with the reference year.
3. **Find where each satellite account actually ends.** A table published for
   2022 may carry emission accounts ending in 2019, and the distribution will not
   say so on its face.
4. **Check the characterisation file separately from the tables.** The DESIRE
   workbook shipped with this release has four unusable rows, including an ozone
   depletion category whose factors fall entirely on NMVOC, a pollutant that does
   not deplete stratospheric ozone. See A7b.
5. **Check the GWP revision.** The file is labelled "CML, 1999" and its factors are
   IPCC AR4. Restate deliberately, and record what cannot be restated: HFC and
   PFC arrive already aggregated to CO2 equivalent and keep whatever revision the
   compiler used.
6. **Look for zero and near-zero rows in industries you depend on.** v3.10.2
   empties ISIC 33, medical and optical instruments, across Europe in every year,
   which sent Danish medical-appliance demand to Greece and China and produced
   22 % of a headline out of nothing.
7. **Do not use the spectral radius as a quality test.** Here $\rho(\mathbf{A}) = 0.97289$ is
   set almost entirely by one pathological column, paddy rice, whose column sum is
   1.14; 72 columns exceed 1. Verify the inverse and check $\mathbf{L}$ for negatives
   instead.
8. **Ask what the sector labels are hiding.** Section 5 is one instance of a
   general problem: an ISIC Rev.3 sector list cannot express a boundary that
   post-2008 statistics take for granted.

---

## References

Full entries with DOIs are in [`docs/references.md`](../references.md).

- Palm, V., Wood, R., Berglund, M., Dawkins, E., Finnveden, G., Schmidt, S., &
  Steinbach, N. (2019). Environmental pressures from Swedish consumption - a
  hybrid multi-regional input-output approach. *Journal of Cleaner Production,
  228*, 634-644. https://doi.org/10.1016/j.jclepro.2019.04.181
- Rørmose Jensen, P., & Iliev, V. (2022). Consumption-based greenhouse gas
  account for Denmark using coupled models. *Statistics Denmark, Eurostat grant
  101022790, work package 4*. https://www.dst.dk
- Stadler, K., Wood, R., Bulavskaya, T., Södersten, C.-J., Simas, M., Schmidt,
  S., Usubiaga, A., Acosta-Fernández, J., Kuenen, J., Bruckner, M., Giljum, S.,
  Lutter, S., Merciai, S., Schmidt, J. H., Theurl, M. C., Plutzar, C., Kastner,
  T., Eisenmenger, N., Erb, K.-H., de Koning, A., & Tukker, A. (2018).
  EXIOBASE 3: developing a time series of detailed environmentally extended
  multi-regional input-output tables. *Journal of Industrial Ecology, 22*(3),
  502-515. https://doi.org/10.1111/jiec.12715
- Statistics Denmark, published input-output tables, `input_output_en_2022.xlsx`.
