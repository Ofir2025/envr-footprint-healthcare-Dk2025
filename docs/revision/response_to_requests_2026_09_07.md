# Response to the eight requests, in priority order

Status of the branch: `2019-update`, 22 commits. Everything below is
implemented, run, and committed unless explicitly marked as remaining work.

---

## 1. Units: EXIOBASE is in euros; why did you write $M? *(highest priority: it would contaminate everything)*

**We do not use dollars anywhere in the model.** EXIOBASE's `unit.txt` declares
`M.EUR`, and every monetary quantity in the code, the tables, and the figures is
million euro. I grepped the whole `src/` tree for `$M`, `M$`, `USD`, and `US$`:
**no hits.** The "$ millions" you saw came from quoted comparative literature,
namely Karliner et al. 2019 Appendix A (WIOD, USD), Lenzen et al. 2020 and
Pichler et al. 2019 (both USD), which are labelled as those studies' own units.

Fixed regardless: every exported table now carries an explicit `unit` column,
the data dictionary states the convention, and the DKK→EUR rate is the
Danmarks Nationalbank annual average for the analysis year (7.4396 for 2022).

## 2. Scope 1-3 without double counting, with the equations right

We read Wood & Hertwich (2018) and Cabernard et al. (2019 + SI, 2022 + SI) and
implemented their formalism rather than paraphrasing it.

**Theory, applied to our case.** With a *single* target (Danish healthcare final
demand), `f = d·L·y_H` already allocates each emission exactly once (Wood &
Hertwich p. 5): allocating production emissions to final demand sums to the
total, unlike the embodied-flow table `E_Z`. Cabernard's correction (their
eq. 9, the `q_T = rowsum(Y_T,all + A_TO L'_OO Y_O,all)` construction) bites when
scope-3 vectors of several *intertwined* targets are aggregated, the source of
their 20-30 % (2019) and ~80 % (2022) overestimates. For us it collapses to the
intra-sector self-supply term, which we quantified and handled.

**What we changed:**
- **Scope 2 now uses the energy-block inverse** `L_EE = (I_EE − A_EE)⁻¹` over
  electricity/steam/heat nodes, so generation is reached through transmission
  and distribution *without leaving the energy block*; fuel extraction,
  refining, and grid hardware correctly stay in Scope 3 (GHG Protocol
  category 3). The previous full-`L` version is kept as a reported sensitivity
  (401.5 vs 404.2 kt).
- **Self-supply loop:** because the services component is `y = A[:,h]·E_H`, the
  footprint contained `s_h(L_hh−1)E_H` = **3.2 kt CO₂e** of the health sector's
  own direct emissions, overlapping the national-accounts Scope 1. This term was
  removed. I first tried zeroing the demand element and **rejected that**: it
  also deletes the legitimate upstream chain of internally traded health services
  (a 27 kt over-correction). Only the direct term is removed.
- **Verified identity** `F_services = (m_h − s_h)·E_H` to 7.5×10⁻¹²: the
  Z-column construction yields a *pure upstream* quantity, making it the exact
  complement to a national-accounts Scope 1. (Using the true final-demand column
  instead would have double counted Scope 1 outright.)
- **Exact partition asserted in code:** `S1 + S2 + S3 + outside == total`, and
  the producing-node detail must reconcile.

**Denmark 2022: S1 142.2 | S2 401.5 | S3 4,085.7 | outside protocol 242.5 kt CO₂e.**
Scope 2 at 8.2 % of the total matches Arup/HCWH's independent WIOD estimate for
Denmark (8.3 %) almost exactly. Their Scope 1 share (11.6 % ≈ 0.51 Mt) is ~3×
what Denmark's own accounts report for the entire Q sector (0.17 Mt), evidence
for national-accounts anchoring.

`double_counting_ledger.csv` tests every overlap numerically. Cleared: the
pharma component vs provider chemical procurement (different channels: SHA
retail/marketed-government vs procurement) and all bottom-up items. **Flagged:**
provider equipment purchases are *zero* in EXIOBASE's `Z` because they sit in
gross fixed capital formation, a boundary **gap**, not an overlap, and per Wood
& Hertwich the largest single omission for a service sector like health care.

## 3. Is the Monte Carlo right, mathematically and statistically? What can we learn from IEooc?

We audited our first version against the IEooc `Methods5_Exercise4b` notebook
and the published literature, then rebuilt it. Findings and fixes:

| defect | fix |
|---|---|
| MRIO parameter uncertainty absent → intervals ~2× too narrow | added as one shared multiplicative factor calibrated to **Lenzen et al. 2020 SI Tab. SI 7.1** (Danish health-care GHG 2.84 ± 0.24 Mt = **8.35 % relative SD**), the only published MC of this exact quantity |
| price-vintage correction (0.97) hidden inside a distribution, so the point estimate sat off-centre in its own interval | all multipliers now median 1 (MC median reproduces the deterministic model); vintage/waste/pharma are **discrete scenarios** |
| waste GSD 1.5 alone drove −53/+120 % and implied the vintage error was unbiased and log-symmetric | moved to a 0.5/1.0/2.0 **scenario band** |
| commuting and visitor travel treated as independent though both are transplants of the same Dutch study | shared method factor, ρ = 0.8 (ρ ∈ {0, 0.5, 0.8} reported) |
| ranking probabilities invalid: six of nine groups had zero variance; pharma scored P(rank 1)=1.0000 | rebuilt: group totals evaluated at the **same draw**, every group carries uncertainty, the shared MRIO factor correctly cancels |
| pharma ratio clipped at 1.0, creating a point mass | truncated lognormal |
| n = 10,000 marginal for the waste tail | n = **100,000**; verified against the **closed-form moments** of the lognormal sum |

**Result: CV 7.9 % for climate, directly comparable with Lenzen's published
8.35 % for Denmark.** Scenario A median 4,897 [4,206-5,721]; Scenario B
(pharma-specific intensity) 3,844 [3,206-4,741].

**Exact first-order variance shares** (free for an additive independent model,
better than a tornado): **MRIO 88.7 %**, visitor travel 5.9 %, commuting 5.3 %,
direct 0.12 %, anaesthetics 0.01 %, pMDI 0.004 %. The honest message for the
reviewers: the bottom-up items they questioned contribute **under 0.02 %** of
the variance; the uncertainty is essentially all MRIO.

**Ranking result worth publishing:** under Scenario A pharmaceuticals & chemicals
rank 1 in every draw; under Scenario B medical/electrical equipment takes rank 1
with P = 0.85. *The identity of the top contributor is decided by the
pharma-mapping choice, not by parameter noise.*

Adopted from IEooc: the violin/distribution plot, the CV column, explicit
statement of what is held fixed (A and L), and the `Software2` aggregation-matrix
pattern. **Not** adopted: their N = 200, their `mean ± sd` on skewed output, and
their sampling idiom. `np.log(np.random.lognormal(mean, sd))` cancels the
lognormal transform and overflows on large cells (in the shipped solution this
idiom silently zeroes 109 cells carrying 53.8 % of German final demand). Their
exercise propagates one input with survey SDs; it is a teaching example, not a
submission-grade template. We cite Lenzen SI 7 as the method precedent.

## 3b. "What do you mean by a single target?" You were right to push

My framing was sloppy. Danish healthcare spans **many** EXIOBASE nodes, and the
answer depends on which question is asked:

* the **final-demand footprint** (our headline) is additive for any number of
  target nodes: no correction needed, ever;
* the **target-sector scope 3** (Cabernard's question) double counts
  target-to-target deliveries and *does* need eq. 9.

So I implemented eqs. 8/9/12 and measured it for three nested target sets
(`03_cabernard_target_scope3/`):

| target set | nodes | naive | corrected | double counting |
|---|---|---|---|---|
| Danish health and social work | 1 | 0.9 Mt | 0.9 Mt | 1.3 % |
| health and social work, all 49 regions | 49 | 1,129 Mt | 1,100 Mt | 2.6 % |
| + chemicals and medical instruments, all regions | 147 | 3,093 Mt | 2,511 Mt | **18.8 %** |

The complement identity `d L Y·1 == e_T,wdc + d_O L'_OO Y_O·1` holds to
2×10⁻¹⁶, confirming the implementation. **The practical lesson:** for one Danish
health node the correction is 1.3 %, but the moment pharmaceuticals and device
manufacturing enter the target set (which is exactly what the planned
sub-sector disaggregation does), it is nearly a fifth. That correction is now
implemented rather than promised.

## 4. Proper CSV tables with correct schemas, most detailed first

**Now organised by approach**, as you asked, each folder holding the outputs of
one named method, with `MANIFEST_lineage.csv` at the root mapping every file to
its approach, script, equations, published reference, inputs, and content hash:

```
00_core_footprint/           01_eriksen_replication/    02_scopes_wood_hertwich/
03_cabernard_target_scope3/  04_uncertainty_lenzen_ieooc/
05_waste_dst_accounts/       06_benchmarks_validation/     scenarios/
```

`docs/methods_approaches.md` documents each approach with its equations and
references. The detailed tables are all long-format with explicit units:

| file | grain |
|---|---|
| `footprint_by_producing_node.csv` | indicator × demand component × **producing** country ISO3 × sector (complete, unthresholded) |
| `footprint_by_purchased_product.csv` | same for the **purchased** product and its supplying region |
| `footprint_bilateral_producer_x_purchase.csv.gz` | the full 4-D array `E[i,j] = s_i L_ij y_j`: largest cells covering ≥99.5 % **plus an explicit remainder row so totals reconcile exactly** |
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

## 5. Waste: all sources explored and tested before settling

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

The reason is conceptual, not vintage: the hybrid account is a **total-residuals**
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
is Eurostat-consistent rather than an alternative to it.

## 6. Childcare and the scope boundary: should we include it, what do others do?

We implemented it as a switch (`HC_SCOPE`) and ran it for all five indicators:

| boundary | expenditure | GWP | share | t/cap |
|---|---|---|---|---|
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

## 7. FIGARO for Denmark 2022

We downloaded and used it. Eurostat's official FIGARO-based GHG footprint
(`env_ac_ghgfp`) gives Denmark **57.40 Mt CO₂e (2022)**, against DST AFTRYK's
62.93 Mt and our model's 64.72 Mt, so the healthcare **share is 7.5-8.5 %
depending on the denominator**, now reported as a range with all three named.
FIGARO also puts emissions arising in NACE Q due to Danish final demand at
176 kt (Q86 alone 97 kt), corroborating our 142 kt Scope 1 plus the intra-health
chain. FIGARO supply/use tables for DK 2022 and 2024 are in
`data/bronze/figaro/`. **Assessment:** at A64 resolution FIGARO separates Q86
from Q87-Q88 and has C21 pharmaceuticals separately, so it is a genuine
cross-model benchmark and a plausible import-structure source, but its 64
industries cannot substitute for the confidential ~2,350-product DST SUT for
health disaggregation.

## 8. Volatile anaesthetics: how far can we go?

The N₂O half is solid (national inventory, 38 t/yr → 11.3 kt CO₂e). The volatile
half (1.4 kt) is a population-scaled Dutch figure, because **halogenated agents
are outside the Kyoto basket and appear in no national inventory**.

The method now exists in the literature: **Talbot, Holländer & Bentzer (2025),
*Lancet Planetary Health*** (PMID 40120629), a sales-based estimate from IQVIA
data, 91 countries, GWP100, global impact falling 27 % to 2,005 kt CO₂e in 2023.
Denmark can be done identically and openly: volatile anaesthetics are recorded
under **ATC N01AB** in the Danish medicines statistics (medstat.dk, hospital
sector), the same source the Danish EPA already uses for the official pMDI
inventory. That is the recommended next data step.

**Materiality, stated plainly:** the whole anaesthetic item is 12.7 kt of
4,875 kt (0.26 %), and its exact variance share is **0.01 %**. A factor-of-three
error moves the headline by under 0.06 %. Double counting checked: DRIVHUS
F-gases for hospitals (9 kt, refrigeration) do not include anaesthetics, and
hospital N₂O is netted out before the bottom-up item is added.

---

## Remaining work

1. medstat ATC N01AB extraction for the Danish volatile-anaesthetics estimate.
2. Imported waste: no source exists; currently reported separately as residuals.
3. Capital (GFCF) is excluded, as in Steenmeijer (per Wood & Hertwich the
   largest single boundary omission for health care). Now quantified in
   `capital_gfcf_treatment.md` with an exogenous and a fully endogenised
   scenario. **Correction:** an earlier draft of this note attributed the zero
   intermediate purchases of medical instruments to the capital boundary. That
   was wrong. The zero is a defect in EXIOBASE v3.10.2, which carries ~zero
   output for industry 33 across all European regions in both 2016 and 2022
   (`exiobase_vintage_defects.md`).
4. Patient/visitor travel still has no Danish source (verified absent), the
   only remaining component with no national anchor.
5. **Closed since:** the eldercare share α is no longer carried from 2019. It is
   now read from the analysis year's own IO table (industry 880000's deliveries
   to eldercare vs childcare): **α = 0.3092 for 2022**, not 0.4914. Direct
   emissions fall to 118.6 kt and direct waste to 42.8 kt, and the two accounts
   now use the same α by construction.
5. Danish-SNAC hybrid and the Lenzen/Malik-style sub-sector disaggregation, for
   which Cabernard eq. (9) *will* be required and is already documented.
