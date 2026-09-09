# EXIOBASE in this study: version, vintage, and what the classification cannot say

**Audience.** Two. First, the manuscript and its supplementary information: the
version and reference year have to be stated unambiguously, and the nowcast
qualification has to be stated by us rather than found by a referee. Second, any
later project of ours that uses EXIOBASE, because most of what follows is not
specific to Denmark or to health care.

**Status.** Standing reference. The decision it supports is
[`decision_d8_nowcast_vs_frozen_year.md`](../revision/decision_d8_nowcast_vs_frozen_year.md);
the defect register behind it is
[`anomalies_bugs_and_open_questions.md`](../revision/anomalies_bugs_and_open_questions.md),
section A.

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

The two vintages on disk were tested against Statistics Denmark's own published
117-industry table for the same year (`analysis.vintage_defect_audit`):

| Danish industry, 2022 | National accounts | v3.10.2 | ratio |
|---|---|---|---|
| Health and social work | 45,321 M.EUR | 16,326 | **0.36** |
| Education | 22,935 | 109,673 | **4.78** |
| Financial intermediation | 18,980 | 76 | **0.004** |
| Machinery n.e.c. | 21,150 | 28 | **0.001** |
| Medical and optical instruments | 9,130 | 0 | **0.00** |

Danish total output is right to 3 % and the accounting identity holds to
7e-11, so output was redistributed between industries rather than lost. The
signature is year-specific (v3.10.2's own 2016 and 2019 Danish blocks pass) and
country-specific: Denmark, Bulgaria, Malta and Switzerland show it, while
Germany, France, Italy, the Netherlands and the United States look plausible.

An internal check settles it without leaving our own data. Danish health and
eldercare final expenditure in 2022 is 40,597 M.EUR. An industry whose *total
output* is 16,326 M.EUR cannot deliver it.

**The general lesson for other projects.** Never accept an MRIO release for a
country without testing that country's block against its own national accounts,
industry by industry, in the year you intend to use. The test is cheap, it needs
only a published national input-output table, and it catches the failure mode
that a balance check cannot: internally consistent tables with the output in the
wrong industries.

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
vintage audit uses:

| Year | Model over national accounts |
|---|---|
| 2016, a year EXIOBASE observed | **1.01** |
| 2022, the projection | **0.80** |

A fifth of the Danish economy is missing from the 2022 projection. Where it is
missing is the part that matters:

| Group | Model | National accounts | Ratio | Handled where |
|---|---|---|---|---|
| Sea and coastal water transport | 19,714 | 78,950 | 0.25 | corrected, section 4 |
| Chemicals and pharmaceuticals | 5,915 | 35,742 | 0.17 | reported as the study's largest limitation |
| Wholesale trade | 28,962 | 53,501 | 0.54 | 2022 prices a 2021 projection cannot see |
| Electricity | 2,540 | 10,789 | 0.24 | as above |
| **Health and social work** | **43,955** | **45,854** | **0.96** | the industry the study models |

None of the four largest gaps is new to this study and none is unaddressed. The
industry being modelled is within 4 % of Denmark's own figure, which is why the
vintage audit passes on the groups it tests.

### The part with no validation

The economic block was tested. **The emission side was not, because there is
nothing to test it against.** EXIOBASE v3.8.2's CO2 accounts end in 2019 and its
other greenhouse gases in 2017, so the 2022 satellite is an extrapolation of
three to five years on the side that carries the physics. This is the weaker
half of the vintage argument and it should be stated as such.

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
|---|---|
| [`docs/revision/shipping_reallocation_method.md`](../revision/shipping_reallocation_method.md) | the narrative version, written for a non-specialist and for the manuscript methods section |
| [`docs/methods/replications/10_sea_transport_reallocation.md`](replications/10_sea_transport_reallocation.md) | the equations, the calibration target, the effect table, and the validation against EXIOBASE's own hybrid build |
| `src/analysis/dk_shipping_correction.py` | the implementation |
| `data/gold/results/10_sea_transport_reallocation/` | the outputs |
| `docs/revision/anomalies_bugs_and_open_questions.md`, A3 | the defect as registered, with the consequence for the submitted manuscript |

The short version. Statistics Denmark report that EXIOBASE sends **74 %** of
Danish water-transport output to Danish *intermediate* use against **9 %** in the
national accounts, because Denmark operates one of the world's largest merchant
fleets and that fleet carries world trade rather than Danish production. We
measure **73.6 %** on v3.8.2 `IOT_2022_ixi`, which is their figure to the
decimal. EXIOBASE's own hybrid build gives 7.8 % natively with no correction,
which is independent confirmation that the monetary build is the thing at fault.

We reallocate to the 9 % target. Total output of the row is left alone, because
it is not in dispute; only the destination of the flows changes, and the released
11,509.8 M.EUR goes to exports. **Transport falls from 37.5 % to 18.5 % of the
supply-chain footprint**, which is 15.5 % of the 4,712 kt total.

**This must be in the manuscript and the SI**, because the submitted paper's most
quotable finding, that transport is 38 to 43 % of the Danish health-care
footprint, is withdrawn by it. The finding was an artefact of a documented
misallocation in EXIOBASE's Danish block, diagnosed by Denmark's own statistical
office rather than by us.

---

## 5. What EXIOBASE calls health care, and why that is a real limitation

### The labels, verified from the distribution

| Table | Label | Code |
|---|---|---|
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
|---|---|---|
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
|---|---|---|---|---|
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
|---|---|---|
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

---

## 6. Checklist for the next EXIOBASE project

Ordered by how much damage each catches, and every one of them caught something
here.

1. **Test the country block against national accounts, per industry, in the year
   you will use.** Not the national total, which was right to 3 % in a release
   whose health industry was out by a factor of three.
2. **Read the release's `metadata.json` for the build date before calling any
   year observed.** Compare the build date with the reference year.
3. **Find where each satellite account actually ends.** A table published for
   2022 may carry emission accounts ending in 2019, and the distribution will not
   say so on its face.
4. **Check the characterisation file separately from the tables.** The DESIRE
   workbook shipped with this vintage has four unusable rows, including an ozone
   depletion category whose factors fall entirely on NMVOC, a pollutant that does
   not deplete stratospheric ozone. See A7b.
5. **Check the GWP vintage.** The file is labelled "CML, 1999" and its factors are
   IPCC AR4. Restate deliberately, and record what cannot be restated: HFC and
   PFC arrive already aggregated to CO2 equivalent and keep whatever vintage the
   compiler used.
6. **Look for zero and near-zero rows in industries you depend on.** v3.10.2
   empties ISIC 33, medical and optical instruments, across Europe in every year,
   which sent Danish medical-appliance demand to Greece and China and produced
   22 % of a headline out of nothing.
7. **Do not use the spectral radius as a quality test.** Here rho(A) = 0.97289 is
   set almost entirely by one pathological column, paddy rice, whose column sum is
   1.14; 72 columns exceed 1. Verify the inverse and check L for negatives
   instead.
8. **Ask what the sector labels are hiding.** Section 5 is one instance of a
   general problem: an ISIC Rev.3 sector list cannot express a boundary that
   post-2008 statistics take for granted.
