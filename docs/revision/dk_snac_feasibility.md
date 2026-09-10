# Danish SNAC: what Statistics Denmark does about EXIOBASE, our current patch, and the feasibility of a full build

**Question (Albert, 2026-09):** can we do for Denmark what Palm et al. (2019, J Clean Prod
228:634-644) did for Sweden (keep the national table as the authoritative domestic core and
use EXIOBASE only for imports), and thereby exploit the Danish IOT's much finer health-sector
resolution? Short answer: **yes, and Denmark is an unusually good candidate**; the medium
answer is that it is a paper-sized build, best executed for the 2022 analysis rather than
squeezed into the current revision.

This document has two halves. Sections 1-5 are the current position: what Statistics
Denmark's own coupled model found, the single reallocation this study applies as a
lightweight patch, and the open nowcast-year decision. Sections 6-11 are the feasibility
memo for the full Danish-SNAC build that would replace the patch; nothing in it has been
built yet, and two of its figures have since been superseded by the corrected model, flagged
where they occur.

---

## 1. The defects Statistics Denmark documents, with their numbers

Source of truth: Rørmose Jensen & Iliev (2022), *Consumption-based GHG account
for Denmark using coupled models*, Statistics Denmark / Eurostat grant
101022790, WP4; Palm et al. (2019) *J Clean Prod* 228:634-644; Tukker, Giljum &
Wood (2018) *J Ind Ecol* 22:483-498.

Their table 1 compares EXIOBASE v3.8 with the Danish national-accounts IOT for
**water transport**, 2019, million DKK:

| | EXIOBASE | Danish national accounts |
|:---|:---|:---|
| Output | 137,637 | 246,064 |
| To Danish intermediate use | **74 %** | **9 %** |
| To exports | 14 % | 90 % |
| Imported inputs | 41 % | 93 % |
| Gross value added | **−1,880 (−1.3 %)** | **+33,339 (+14 %)** |

A negative value added is not an economy; it is a broken block. That industry is
more than half of Danish CO₂, so raw EXIOBASE routes the bulk of Danish shipping
emissions into Danish *consumption*.

Three further defects: **Danish imports in EXIOBASE are 30-40 % below the
national accounts**; the satellite vector contains extreme outliers (Mexican
secondary plastic at 372,548 t CO₂e per EUR turns a 2 M EUR import into 729 Gt);
and the nowcast years are internally out of sync, so inflation mechanically
inflates the footprint. The version-and-vintage defects this study found on its
own model, independently of Statistics Denmark's, are documented in full in
[`../methods/exiobase_version_vintage_and_classification.md`](../methods/exiobase_version_vintage_and_classification.md).

## 2. Their remedy is structural, ours is a patch

They adopt **simplified SNAC**: the Danish domestic block comes entirely from
the national accounts, and EXIOBASE is never used for it:
$\mathbf{A}_d = \mathbf{Z}\,\hat{x}^{-1}$, $\mathbf{L}_d = (\mathbf{I} - \mathbf{A}_d)^{-1}$, $e_d = \hat{s}_d\,\mathbf{L}_d\,y_d + e_h$. EXIOBASE enters
only for imports, through $\mathbf{Q} = \hat{S}\,\mathbf{L}$ and $e_m = \mathbf{Q}\,\mathbf{K}\,m$, with $m = \mathbf{A}_m\,\mathbf{L}_d\,y_d +
y_m$ and $\mathbf{K}$ a 7,987 × 117 concordance.

**Their model carries no shipping correction, because the wrong block is
discarded rather than repaired.**

Ours is a targeted reallocation of one row to their published 9 % benchmark. It
recovers most of the effect for a fraction of the work, and it is honest to call
it what it is: an approximation of the first step of a method we have not yet
implemented. Simplification is defensible: Moran et al. (2018) put the Danish
feedback effect at **0.4 %**, which is why simplified SNAC is used in preference
to full SNAC by both Rørmose and Palm. The full mechanics and the effect on the
headline are in
[`shipping_reallocation_method.md`](shipping_reallocation_method.md).

Their own outlier remedy is a hard multiplier threshold of 1 kg CO₂e/DKK
(≈7.5 kg CO₂e/EUR) which they themselves call *"quite arbitrary"*; their
preferred future fix is iterative replacement of outliers by the cross-country
mean of the remaining 48 regions.

## 3. The nowcast-year disagreement (decision D8, open)

**Statistics Denmark does not use the nowcast years.** They freeze EXIOBASE at
**2019** (the last year backed by real emission data) for their 2019, 2020, and
2021 footprints, and deflate the demand vector back to 2019 prices.

We do the opposite: 2022 expenditure on the 2022 table, whose CO₂ accounts end
in 2019 and whose other greenhouse-gas accounts end in 2017.

Both positions are arguable. Ours has the merit that the Danish **economic**
block is validated against the 2022 national accounts and passes, and that
expenditure year and model year coincide, which is what reviewer 2 asked for.
Theirs has the merit that the **emission** side is never extrapolated.

This choice is an open decision, tracked in full in
[`decision_d8_nowcast_vs_frozen_year.md`](decision_d8_nowcast_vs_frozen_year.md),
not a settled one. That document's recommendation is to keep 2022 as the
headline and add the 2019-frozen, deflated variant as a reported sensitivity,
which would also answer reviewer 2's original concern from the opposite
direction.

## 4. Results worth citing against ours

| | Rørmose (2020) | This study (2022) |
|:---|:---|:---|
| Danish national footprint | 65.4 Mt CO₂e | 77.5 Mt |
| Per capita | 11.0 t | 13.2 t |
| Share arising in Denmark | 38 % | n/a |
| Share arising abroad | **62 %** | n/a |
| Government consumption footprint | ~8 Mt, of which **~2/3 abroad** | n/a |

Their government-consumption finding matters directly: **Danish government
consumption, where public health care sits, is about two-thirds
imported-emissions in their coupled model**, materially more import-exposed than
households at 55 %. Our health-care footprint is **73.7 % imported** in origin,
which is consistent with, and slightly above, their government figure.

They publish **no like-for-like raw-versus-coupled comparison**, so the size of
the SNAC correction for Denmark cannot be cited from them; it would have to be
computed, which is the point of the feasibility work in sections 6-11.

## 5. Method points that bear on our claims

- **Uncertainty priority is the reverse of the intuitive order.** Tukker et al.
  (2018): *"the environmental extensions, rather than the redistribution to
  final consumption via economic structure reflected by a specific GMRIO, forms
  the highest source of uncertainty… The next most important issue appears the
  differences in representation of the country SUT/IOT in GMRIOs, rather than
  the structure of the trade flows."* Variance mass belongs on the satellite
  first, then the domestic block, then trade.
- **Scope 2+3 is not an additive account.** Hertwich & Wood (2018) are explicit
  that scope accounting measures reduction opportunities and that the total does
  not sum to global emissions, and that **the amount of double counting depends
  on sector resolution**. Our scope partition is exact within our own boundary,
  which is a different and weaker claim, and the manuscript should say so.
- **A GHG-only footprint misses most of the variance.** Steinmann et al. (2017),
  via Tukker et al.: carbon, energy, land, water, and materials together explain
  only **~60 %** of environmental variance; adding five impact-oriented
  indicators reaches **95 %**, with toxicity the systematic omission. This result
  is the published justification for carrying IMPACT World+ alongside the five
  headline indicators.
- **Capital stays exogenous in both precedents.** Neither Rørmose nor Palm
  endogenise capital; both keep it as a GFCF final-demand column. That supports
  our baseline choice.

---

## 6. What Palm et al. actually do (the "simplified SNAC" template)

Domestic part from the national SRIO with national SEEA extensions; imports from EXIOBASE
multipliers, bridged by three concordances; feedback loops (exports that return as imports)
neglected, following Moran et al. (2018) on their insignificance:

$$f^{(d+m)} = \mathbf{S}^d\,\mathbf{L}^d\,y^d + \mathbf{Q}^t\,\mathbf{A}^m\,\mathbf{L}^d\,y^d + \mathbf{Q}^t\,y^m + f^h$$

with $\mathbf{Q}^t$ built from EXIOBASE as
$$\mathbf{Q}^g = \mathbf{S}\,\mathbf{L}\,\hat{y}\,\mathbf{G}^p\,(y\,\mathbf{G}^p)^{-1}$$
(product concordance $\mathbf{G}^p$, weighted by EXIOBASE final demand), then mapped to the national bilateral-trade country
dimension via a binary country concordance $\mathbf{G}^c$ and the trade-share matrix $\mathbf{B}$, plus a
currency conversion $c$ (their §2.2, pp. 636-637). These are the same maths our pipeline
already uses; the innovation is entirely in the data plumbing.

## 7. Why Denmark is a good candidate: the ingredients are on the shelf

| Ingredient | Status | Where |
|:---|:---|:---|
| National IOT, **117 industries**, basic prices, current + previous-year prices, with an explicit **117-row import matrix** (imports by industry of origin × using industry) and tax/VAT rows | ✅ in repo, 2006-2022 | `data/bronze/input_output/` (DST English workbooks; also via StatBank/API) |
| Detailed SUT (2,362 products × 117 industries, basic prices, domestic/import split `Ubas_dk`/`Ubas_imp`, margins and taxes sheets) | ✅ 2019 in repo; 2022 obtainable via DST (coarser preliminary commodity system for 2021-22) | `data/bronze/dk_umat_2019.xlsx` |
| National SEEA extensions on the **same DB07/117 classification**: DRIVHUS greenhouse gases (used already for Scope 1), plus energy accounts, and air-emission accounts for other pollutants | ✅ public API, t+9 months, through 2023+ | api.statbank.dk (DRIVHUS et al.) |
| EXIOBASE multipliers for the import side | ✅ local | see note below |
| Health-sector resolution in the national table | **6 relevant industries**: 860010 hospitals, 860020 medical & dental practices, 870000 residential care, 880000 social work, **210000 Pharmaceuticals**, 320010 medical instruments | vs EXIOBASE's single `Health and social work (85)` + `Chemicals nec` proxy |
| Health expenditure by SHA function for the demand side | ✅ DST SHA1 via API (CHE 2019: 234.6 bn; 2022: 271.9 bn DKK) | cross-checks the SUT-based vector |

**A correction to this memo's original wording.** When this feasibility question
was first scoped, the EXIOBASE copy on disk for the import-side multipliers was
`IOT_2022_ixi.mat` **v3.10.2**. That vintage has since been rejected as the
study's background model: it misallocates the Danish block and empties the
medical-instruments industry across Europe, as set out in full in
[`../methods/exiobase_version_vintage_and_classification.md`](../methods/exiobase_version_vintage_and_classification.md).
**Any Danish-SNAC build must use v3.8.2, the current background model, for the
import-side multipliers**, not the v3.10.2 copy this memo originally pointed at.
The rest of the feasibility argument is unaffected: the ingredients on the
Danish side do not depend on which EXIOBASE vintage supplies the import side.

## 8. What the resolution buys: the three known weaknesses it removes

1. **The input-recipe problem.** Today the entire healthcare-services footprint hangs on
   EXIOBASE's *estimated* input column for DK "Health and social work" — the recipe that,
   at the time this memo was first drafted, sat behind a transport-dominance headline of
   ~41 % of GWP. **That transport figure is now superseded and withdrawn**: the sea-transport
   reallocation corrected it to 18.5 % of the supply-chain footprint (15.5 % of the total),
   documented in full in
   [`shipping_reallocation_method.md`](shipping_reallocation_method.md). The recipe problem
   itself is unaffected by that correction and remains real: EXIOBASE's single estimated
   health-industry column is also behind the imploded Scope 2 (24 kt: EXIOBASE has DK
   health buying almost no energy directly, where Arup's Denmark sheet has Scope 2 alone at
   8.3 % of the footprint). A Danish-SNAC model replaces that single recipe with four
   observed provider recipes (hospitals vs practices vs residential care vs social work)
   from the national SUT. **This replacement is the decisive scientific gain**, independent
   of the transport correction above.
2. **The pharma-mapping problem (Reviewer 1).** The national table has a real
   **Pharmaceuticals industry (210000)**: domestic pharma production no longer needs the
   Chemicals-nec proxy; only the imported share (large, but with observed country-of-origin
   totals in the import matrix) still runs through EXIOBASE, where the Piñero-style
   correction can be applied per origin.
3. **The import-allocation problem.** The current pipeline distributes pharma/appliance
   imports by EXIOBASE's final-demand sourcing proportions; the Danish SUT's `Ubas_imp`
   and the IOT import matrix provide the actual product-level import content per purpose.

## 9. Method blueprint (literature-anchored)

1. **Symmetric domestic table:** build from the rectangular DST SUT with an explicitly
   chosen construct, industry-technology/fixed-product-sales (Suh et al. 2010, eqs. 4-6)
   for an attributional footprint; or simply adopt DST's own symmetric IOT (already
   industry×industry, with the import matrix separated; half the work is done).
2. **Domestic extensions:** DRIVHUS + energy/air accounts on the same 117 industries
   (S^d directly, no concordance needed: the accounts and the IOT share DB07).
3. **Import side:** EXIOBASE v3.8.2 multipliers Q = S L, aggregated to the Danish product/
   industry classification with a weighted concordance (Palm §2.2); country dimension via
   the DST import matrix (117 origin-industries) or, at product level, bilateral trade
   shares. Currency via the documented annual DKK/EUR rate.
4. **Double-counting discipline:** strip re-exports; CIF→FOB with the trade/transport
   counter-entry (Schoer et al. 2013, p. 14284); one master flow list with each flow
   counted once (Pauliuk 2022's rule). For any process-based add-on, subtract the
   corresponding monetary flow before adding the inventory (tiered-hybrid rule,
   Nakamura 2023 §5.1.5/5.2).
5. **Refinement shortcut (low-cost first iteration):** before the full SNAC, apply the
   **Piñero et al. (2018) correction-matrix bridge** ($\mathbf{C} = \mathbf{P}\,\hat{p}_A^{-1}$; $\mathbf{W} = \mathbf{C}\,\hat{\alpha}$; $\mathbf{R}^* = \mathbf{W} \circ \mathbf{M}$) to
   inject EXIOBASE country-of-origin detail into the Danish import matrix without
   rebuilding anything. This bridge alone addresses weakness 3 and much of 2.
6. **Waste:** with the national core in place, the waste extension becomes a **WIO-style
   physical row set** (Nakamura 2023 §5.4): Danish waste statistics (Affaldsstatistik/ADS)
   by industry for the domestic side, Eurostat `env_wasgen` for EU partners, 2011-hybrid
   coefficients (or the non-public Merciai v4-2016, worth one request e-mail) for the rest
   of the world. This row set replaces the 2011-absolute-tonnes carry-forward entirely.

## 10. Error budget and validation

Schoer et al. (2013) bound the residual "national-model vs full-MRIO" gap at ~5-10% of the
import-embodied component (<5% of the total), acceptable against the recipe error it
removes. Validation set: (i) domestic direct emissions must reproduce DRIVHUS by
construction; (ii) the EXIOBASE-only model (this revision) brackets the comparison;
(iii) Scope-2 result vs Arup's 8.3% and the regions' own electricity/heat accounts
(215.8 kt CO₂e in 2018 for the regions' el+heat+transport, Danske Regioner); (iv) the
national CBA footprint vs EXIOBASE-native and Eurostat FIGARO values.

## 11. Effort and sequencing (recommendation)

- **Not for the current resubmission.** The revision stands on the corrected
  EXIOBASE-only model + uncertainty package; the response letter announces the hybrid as
  the follow-up (reviewers respond well to a concrete, cited plan).
- **Phase H1 (~days):** Piñero bridge on imports + validation of the EXIOBASE DK health
  recipe against the DST 117-industry health columns (energy, transport, pharma inputs).
  This validation yields the recipe-error quantification the transport headline needs
  *now*.
- **Phase H2 (~weeks):** full Danish-SNAC 2022 build per §9, with the WIO-style waste rows.
  This build is a methods paper in its own right (Palm et al. was exactly that for
  Sweden) and the natural vehicle for the Denmark-2022 flagship analysis.

**Price-basis discipline throughout** (Albert's standing caution): DST IOT/SUT and
DRIVHUS are basic-price/national-accounts-consistent; EXIOBASE is basic-price; health
expenditure by SHA function arrives in purchaser-type valuations. Every bridge states its
valuation, and margins/taxes move through the dedicated `Umargins`/`Utaxes` sheets, never
inside a product flow.
