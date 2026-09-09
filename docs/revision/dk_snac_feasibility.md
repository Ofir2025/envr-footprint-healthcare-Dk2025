# Feasibility memo, a Danish-SNAC hybrid: integrating the Statistics Denmark IOT/SUT with EXIOBASE

**Question (Albert, 2026-09):** can we do for Denmark what Palm et al. (2019, J Clean Prod
228:634-644) did for Sweden (keep the national table as the authoritative domestic core and
use EXIOBASE only for imports), and thereby exploit the Danish IOT's much finer health-sector
resolution? Short answer: **yes, and Denmark is an unusually good candidate**; the medium
answer is that it is a paper-sized build, best executed for the 2022 analysis rather than
squeezed into the current revision.

## 1. What Palm et al. actually do (the "simplified SNAC" template)

Domestic part from the national SRIO with national SEEA extensions; imports from EXIOBASE
multipliers, bridged by three concordances; feedback loops (exports that return as imports)
neglected, following Moran et al. (2018) on their insignificance:

  f^(d+m) = S^d L^d y^d  +  Q^t A^m L^d y^d  +  Q^t y^m  +  f^h

with Q^t built from EXIOBASE as Q^g = S L ŷ G^p (y G^p)^-1 (product concordance G^p,
weighted by EXIOBASE final demand), then mapped to the national bilateral-trade country
dimension via a binary country concordance G^c and the trade-share matrix B, plus a
currency conversion c (their §2.2, pp. 636-637). These are the same maths our pipeline
already uses; the innovation is entirely in the data plumbing.

## 2. Why Denmark is a good candidate: the ingredients are on the shelf

| Ingredient | Status | Where |
|---|---|---|
| National IOT, **117 industries**, basic prices, current + previous-year prices, with an explicit **117-row import matrix** (imports by industry of origin × using industry) and tax/VAT rows | ✅ in repo, 2006-2022 | `data/bronze/input_output/` (DST English workbooks; also via StatBank/API) |
| Detailed SUT (2,362 products × 117 industries, basic prices, domestic/import split `Ubas_dk`/`Ubas_imp`, margins and taxes sheets) | ✅ 2019 in repo; 2022 obtainable via DST (coarser preliminary commodity system for 2021-22) | `data/bronze/dk_umat_2019.xlsx` |
| National SEEA extensions on the **same DB07/117 classification**: DRIVHUS greenhouse gases (used already for Scope 1), plus energy accounts, and air-emission accounts for other pollutants | ✅ public API, t+9 months, through 2023+ | api.statbank.dk (DRIVHUS et al.) |
| EXIOBASE 2022 multipliers for the import side | ✅ local | `IOT_2022_ixi.mat` (v3.10.2) |
| Health-sector resolution in the national table | **6 relevant industries**: 860010 hospitals, 860020 medical & dental practices, 870000 residential care, 880000 social work, **210000 Pharmaceuticals**, 320010 medical instruments | vs EXIOBASE's single `Health and social work (85)` + `Chemicals nec` proxy |
| Health expenditure by SHA function for the demand side | ✅ DST SHA1 via API (CHE 2019: 234.6 bn; 2022: 271.9 bn DKK) | cross-checks the SUT-based vector |

## 3. What the resolution buys: the three known weaknesses it removes

1. **The input-recipe problem.** Today the entire healthcare-services footprint hangs on
   EXIOBASE's *estimated* input column for DK "Health and social work", the recipe behind
   the transport-dominance headline (~41% of GWP) and behind the imploded Scope 2
   (24 kt: EXIOBASE has DK health buying almost no energy directly, where Arup's Denmark
   sheet has Scope 2 alone at 8.3% of the footprint). A Danish-SNAC model replaces that
   single recipe with four observed provider recipes (hospitals vs practices vs residential
   care vs social work) from the national SUT. **This replacement is the decisive
   scientific gain.**
2. **The pharma-mapping problem (Reviewer 1).** The national table has a real
   **Pharmaceuticals industry (210000)**: domestic pharma production no longer needs the
   Chemicals-nec proxy; only the imported share (large, but with observed country-of-origin
   totals in the import matrix) still runs through EXIOBASE, where the Piñero-style
   correction can be applied per origin.
3. **The import-allocation problem.** The current pipeline distributes pharma/appliance
   imports by EXIOBASE's final-demand sourcing proportions; the Danish SUT's `Ubas_imp`
   and the IOT import matrix provide the actual product-level import content per purpose.

## 4. Method blueprint (literature-anchored)

1. **Symmetric domestic table:** build from the rectangular DST SUT with an explicitly
   chosen construct, industry-technology/fixed-product-sales (Suh et al. 2010, eqs. 4-6)
   for an attributional footprint; or simply adopt DST's own symmetric IOT (already
   industry×industry, with the import matrix separated; half the work is done).
2. **Domestic extensions:** DRIVHUS + energy/air accounts on the same 117 industries
   (S^d directly, no concordance needed: the accounts and the IOT share DB07).
3. **Import side:** EXIOBASE-2022 multipliers Q = S L, aggregated to the Danish product/
   industry classification with a weighted concordance (Palm §2.2); country dimension via
   the DST import matrix (117 origin-industries) or, at product level, bilateral trade
   shares. Currency via the documented annual DKK/EUR rate.
4. **Double-counting discipline:** strip re-exports; CIF→FOB with the trade/transport
   counter-entry (Schoer et al. 2013, p. 14284); one master flow list with each flow
   counted once (Pauliuk 2022's rule). For any process-based add-on, subtract the
   corresponding monetary flow before adding the inventory (tiered-hybrid rule,
   Nakamura 2023 §5.1.5/5.2).
5. **Refinement shortcut (low-cost first iteration):** before the full SNAC, apply the
   **Piñero et al. (2018) correction-matrix bridge** (C = P p̂_A⁻¹; W = Cα̂; R* = W∘M) to
   inject EXIOBASE country-of-origin detail into the Danish import matrix without
   rebuilding anything. This bridge alone addresses weakness 3 and much of 2.
6. **Waste:** with the national core in place, the waste extension becomes a **WIO-style
   physical row set** (Nakamura 2023 §5.4): Danish waste statistics (Affaldsstatistik/ADS)
   by industry for the domestic side, Eurostat `env_wasgen` for EU partners, 2011-hybrid
   coefficients (or the non-public Merciai v4-2016, worth one request e-mail) for the rest
   of the world. This row set replaces the 2011-absolute-tonnes carry-forward entirely.

## 5. Error budget and validation

Schoer et al. (2013) bound the residual "national-model vs full-MRIO" gap at ~5-10% of the
import-embodied component (<5% of the total), acceptable against the recipe error it
removes. Validation set: (i) domestic direct emissions must reproduce DRIVHUS by
construction; (ii) the EXIOBASE-only model (this revision) brackets the comparison;
(iii) Scope-2 result vs Arup's 8.3% and the regions' own electricity/heat accounts
(215.8 kt CO₂e in 2018 for the regions' el+heat+transport, Danske Regioner); (iv) the
national CBA footprint vs EXIOBASE-native and Eurostat FIGARO values.

## 6. Effort and sequencing (recommendation)

- **Not for the current resubmission.** The revision stands on the corrected
  EXIOBASE-only model + uncertainty package; the response letter announces the hybrid as
  the follow-up (reviewers respond well to a concrete, cited plan).
- **Phase H1 (~days):** Piñero bridge on imports + validation of the EXIOBASE DK health
  recipe against the DST 117-industry health columns (energy, transport, pharma inputs).
  This validation yields the recipe-error quantification the transport headline needs
  *now*.
- **Phase H2 (~weeks):** full Danish-SNAC 2022 build per §4, with the WIO-style waste rows.
  This build is a methods paper in its own right (Palm et al. was exactly that for
  Sweden) and the natural vehicle for the Denmark-2022 flagship analysis.

**Price-basis discipline throughout** (Albert's standing caution): DST IOT/SUT and
DRIVHUS are basic-price/national-accounts-consistent; EXIOBASE is basic-price; health
expenditure by SHA function arrives in purchaser-type valuations. Every bridge states its
valuation, and margins/taxes move through the dedicated `Umargins`/`Utaxes` sheets, never
inside a product flow.
