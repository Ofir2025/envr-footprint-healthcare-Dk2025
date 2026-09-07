# Denmark 2022 — primary analysis (Steenmeijer replication tier)

**Model:** EXIOBASE v3.10.2 `IOT_2022_ixi` (official txt distribution, Zenodo 20051562)
× Danish 2022 expenditure (health + eldercare) × DRIVHUS/AFFALD direct accounts ×
Danish-primary bottom-up items. Run: `HC_ANALYSIS_YEAR=2022 python -m analysis.main_2025`
after `python -m pipelines.prep_background_2022.build_background_2022`.

## 1. Inputs (all public, API-reproducible)

- **Expenditure, basic prices:** built from the published 117-industry IO workbook
  (`input_output_en_2022.xlsx` — StatBank): household consumption from the CP sheet's
  COICOP columns, NPISH + marketed/non-market individual government from the IO sheet's
  purpose columns; only industry-coded (basic-price) rows summed. COICOP-2018 codes:
  06112 pharma; 06134 appliances; 06200 out-patient; 06300/06340/06400 hospital;
  13302 eldercare (13301 childcare excluded, flag available). Totals: pharma
  DKK 14.51 bn, appliances 8.14 bn, services 279.37 bn → **DKK 302.0 bn = €40,597 M**
  at 7.4396 DKK/EUR (DNB 2022 average). Cross-check: SHA1 CHE 2022 = 271.9 bn + social
  LTC 30.0 bn. Unlike 2019, no confidential SUT extract is needed — the 2022 vector is
  fully reproducible from public tables. Provenance: `dk_expenditure_breakdown_2022.csv`.
- **Direct emissions:** DRIVHUS 2022, QA 92 + 870000 19 + α×880000 60 − hospital
  medical N₂O 11 = **118.6 kt CO₂e**. The eldercare share α = **0.3092** is now read
  from the analysis year's own IO table (industry 880000's deliveries to eldercare
  13302 vs childcare 13301: 15.54 vs 34.72 bn DKK), replacing the 0.4914 carried
  forward from the 2019 detailed SUT — a documented open item now closed.
- **Direct waste:** AFFALD01 2022 (excl. soil), same boundary and same α = **42.8 kt**.
- **Bottom-up:** anaesthetics 12.7 kt (NID 2.G.3.a 38 t N₂O ×298 + volatiles proxy);
  pMDI **11.6 kt** (Danish EPA F-gas inventory 2022 actual, GWP100); commuting factor
  0.6343 (NABB69 2022 employment 556,999; TU 2022 distance 9.3 km/p/d); visitor 0.6762.

## 2. Background build (v3.10.2 restructure)

v3.10.2 ships Z/x/Y at the archive root and satellites in eight domain folders
(733 stressors stacked; empty cells → 0). A = Z x̂⁻¹; L inverted directly. The
characterisation bridge is rebuilt: GWP (22 rows), blue water (103) and VA map 1:1 by
stressor name from the Steenmeijer/DESIRE selection; abiotic material extraction (29
rows: Metal Ores + Non-Metallic Minerals), land (all 26 land-account rows) and
employment are rebuilt from the restructured v3.10.2 names with the same concept
definitions. **Multiplier-outlier screening** (Rørmose Jensen & Iliev 2022 failure
mode: emission accounts on near-zero-output industries — observed here as GB medical
instruments at 2×10⁸ kt CO₂e/M€ injecting 2,025 kt into the appliances footprint):
air-emission entries with intensity >100× the cross-region sector median, or sitting
on outputs <1 M€, are replaced by the median intensity × actual output (96,833
entries). Screening is restricted to air emissions — extraction/land/water accounts
are legitimately concentrated and a median test would crush real mines (concentrated-
stressor caution, Jakobs 2023). Validation: the screened model's Danish national CBA
GWP is **64.7 Mt vs DST's official AFTRYK 62.9 Mt (+2.9%)**; unscreened: 69.3 Mt.
Waste extension: 2011 hybrid accounts over 2022 output (Steenmeijer precedent),
direct entry replaced by AFFALD; wide MC band; rebuild planned per the waste protocol.

## 3. Headline results, Denmark 2022

| Indicator | Healthcare footprint | Share of national CBA footprint |
|---|---|---|
| Climate change | **4,864 kt CO₂e** (~0.83 t/capita) | **7.5%** (7.7% vs DST AFTRYK, 8.5% vs Eurostat FIGARO) |
| Material extraction | 5,595 kt | 6.8% |
| Blue water | 43.0 Mm³ | 4.9% |
| Land use | 3,833 km² | 4.4% |
| Waste generation | 1,482 kt | 6.3% |

Components (GWP): services 1,983; pharmaceuticals & chemical products 1,340;
appliances 921; travel 606; direct 129.5; medical gases 24.3.

**Scopes (GHG Protocol, corrected construction — `analysis.scopes_detail`):**
**S1 142.2 / S2 401.5 / S3 4,085.7 / outside-protocol 242.5 kt CO₂e.**
Scope 2 uses the energy-block inverse `L_EE = (I_EE − A_EE)⁻¹` so that
generation is reached through transmission and distribution without leaving the
energy block; fuel extraction, refining and grid hardware stay in Scope 3, per
the GHG Protocol (the full-`L` variant, 404.2 kt, is reported as a sensitivity).
The health sector's self-supply loop, `s_h(L_hh − 1)E_H` = 3.2 kt, is removed
from the MRIO part because it overlaps the national-accounts Scope 1. The
partition is asserted exact and the producing-node detail is asserted to
reconcile. Scope 2 at 8.2 % of the total matches Arup's independent WIOD-based
8.3 % for Denmark almost exactly. Geography: Denmark 26.1% of GWP, Asia-Pacific
39.5% (DST AFTRYK: 39% domestic economy-wide; Arup: 39.1%).
Contribution groups (GWP): pharma & chemicals 33.4%, medical/electrical equipment
19.2%, individual travel 12.4%, **transport 7.0%**. Materials: pharma group 61.9%.

**Monte Carlo (100,000 draws, `analysis.uncertainty_2025`, rebuilt after audit).**
All multipliers have median 1 so the MC median reproduces the deterministic model;
structural choices (price vintage, waste vintage, pharma mapping) are discrete
scenarios, never hidden inside a distribution. MRIO parameter uncertainty is
included as a shared factor calibrated to Lenzen et al. (2020) SI Tab. SI 7.1
(Danish health-care GHG 2.84 ± 0.24 Mt = 8.35 % relative SD) — the only published
Monte Carlo of this exact quantity. Commuting and visitor travel share a method
factor (ρ = 0.8; ρ ∈ {0, 0.5, 0.8} reported). Verified against the closed-form
moments of the lognormal sum.

| Scenario | GWP median | 95 % interval | CV |
|---|---|---|---|
| A — pharma as Chemicals nec | 4,897 | 4,206–5,721 | 7.9 % |
| B — pharma-specific intensity | 3,844 | 3,206–4,741 | 10.1 % |

The CV of 7.9 % sits directly alongside Lenzen's published 8.35 % for Denmark.
**Exact first-order variance shares:** MRIO parameters 88.7 %, visitor travel
5.9 %, commuting 5.3 %, direct operational 0.12 %, anaesthetics 0.01 %, pMDI
0.004 %. The bottom-up items the reviewers questioned contribute under 0.02 % of
the variance; the uncertainty is essentially all MRIO — a more useful answer to
the review than the tornado alone.

**Ranking probabilities** (contribution groups, climate): under Scenario A
pharmaceuticals & chemicals hold rank 1 in every draw; under Scenario B medical
and electrical equipment takes rank 1 with P = 0.85 and pharma falls to P = 0.09.
The identity of the top contributor is therefore decided by the pharma-mapping
choice, not by parameter noise — exactly the sensitivity Reviewer 1 requested.

## 4. The transport headline does not survive the vintage update

On EXIOBASE 3.8.2-2016 (the submitted model's actual vintage), transport was 38.5–43%
of the healthcare GWP footprint. On v3.10.2-2022, **all transport industries carry
11.7% of the MRIO footprint** (Danish water transport 3.2%). The recipe-validation
diagnostic (`recipe_validation_2022.csv`; EXIOBASE DK health column vs the actual DST
117-industry health columns) shows why: EXIOBASE still overstates water transport
(1.9% vs 0.4% of inputs), post/telecom (5.2 vs 1.3) and business services (39.1 vs
23.2), and **understates pharmaceutical/chemical inputs two-fold (8.0 vs 14.9%)** —
but the gross v3.8.2 misallocation of Danish shipping (Rørmose Jensen & Iliev 2022,
pp. 11–12: 74% of water-transport output to Danish intermediate use vs 9% actual) is
largely gone. Consequence for the manuscript: the "transport ≈ 40%" finding must be
withdrawn/reframed as vintage-dependent; pharma & equipment dominance (52% combined)
is the robust story, consistent with Steenmeijer's NL result and Arup's Denmark sheet
(transport 16.6% there). The 2019-corrected (6.29 Mt on v3.8.2) and 2022 (4.88 Mt on
v3.10.2) results **must not be read as a time trend** — the vintage change dominates.

## 4b. Scope-boundary sensitivity (all five indicators)

| boundary | expenditure (M€) | GWP (kt) | share | t/capita | materials | water | land | waste |
|---|---|---|---|---|---|---|---|---|
| health only (no eldercare) | 31,079 | 4,405 | 6.81 % | 0.750 | 5,123 | 38.9 | 3,414 | 1,354 |
| **health + eldercare (default)** | **40,597** | **4,875** | **7.53 %** | **0.830** | **5,595** | **43.0** | **3,833** | **1,482** |
| + childcare ("zorg en welzijn", Steenmeijer-comparable) | 49,709 | 5,325 | 8.23 % | 0.907 | 6,047 | 47.0 | 4,234 | 1,604 |

SHA-based studies (Pichler, Arup/Karliner, OECD) include long-term health care
but not childcare; Steenmeijer's Dutch boundary does include childcare and youth
care, which is why the third row is the like-for-like comparison with the
template. Malik et al. exclude aged care entirely; Lenzen's Danish boundary
excludes residential care but includes veterinary. Our default sits with the SHA
mainstream, and the spread across the three boundaries is only ±10 %.

## 5. Benchmarks

DST AFTRYK 2022: national 62.9 Mt; household "G Medical products, health services"
686 kt (out-of-pocket slice only); government consumption (all functions) 6.82 Mt.
Arup/HCWH 2014: 4.4 Mt, 6.3%, 0.78 t/cap, S2 8.3%, 39.1% domestic. Pichler 2014:
4.0 Mt CO₂ (CO₂-only), 6.4%. Our 4.88 Mt / 7.5% / 0.82 t per capita sits coherently
against all three; the per-capita stability 2014→2022 despite expenditure growth
mirrors the intensity-decline mechanism in Lenzen et al. (2020).

## 6. Remaining gaps (carried into the response letter)

Volatile anaesthetics proxy; no Danish patient/visitor-travel source (verified —
TU microdata named as route); waste extension vintage (rebuild per
`03_v2_waste_benchmarking_protocol`); α eldercare share from 2019 SUT; capital
excluded (Steenmeijer-consistent); pharma mapping as Scenario B; EXIOBASE recipe
biases quantified in `recipe_validation_2022.csv` → motivate the Danish-SNAC phase.
