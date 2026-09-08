# Revision ledger - bugs, method corrections and data-source upgrades

**Scope:** revision of the Danish healthcare environmental-footprint model (Eriksen et al.,
Next Sustainability NXSUST-D-26-01589) following the forensic audit of 2026-09-06 and the
first-round reviews. Every entry lists the defect, the evidence, the change, and the effect
on results. Baseline year 2019 expenditure on the EXIOBASE 2016 industry-by-industry table.

## 0. Data-vintage identification (reportable erratum)

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

## 1. E1 - Expenditure vector omitted ~90% of eldercare (critical)

**Defect:** `calculate_healthcare_totals` enumerated (transaction × purpose) columns by
hand and omitted (i) non-market government consumption of purpose 12401 (retirement
homes/day care/home help) = **DKK 68.4 bn**, and (ii) NPISH hospital services = DKK 2.3 bn -
while the manuscript stated eldercare was included.

**Fix:** complete coverage of all individual-consumption transactions (3110/3130/3141/3142)
for purposes 06112, 06130, 06200, 06300, 12401; every included column is exported to
`data/silver/inputs/dk_expenditure_breakdown_2019.csv` as a provenance record. Childcare
(12402, DKK 60.4 bn - inside Steenmeijer's wider "zorg en welzijn" scope) remains excluded
by default and is available via `include_childcare=True` for a scope sensitivity.

**Effect:** healthcare-services expenditure rises from DKK 173.0 bn to **DKK 243.7 bn**
(23.2 → 32.6 b€), +41%.

## 2. E2 - Direct (Scope-1) operational emissions (critical)

**Defect:** the "operational impacts" (B_HEAL) GWP entry was computed as
`B·(L·Ystim)` over the DK health rows = **1.39 kt CO₂e** - the MRIO-induced intra-health
emissions, which (a) are already inside the contribution totals (a double count) and
(b) are not the sector's direct emissions. An unsourced `DirectEm = 1,699 kt` sat unused
in `dk_data_2025.csv`.

**Fix:** Statistics Denmark **DRIVHUS** greenhouse-gas accounts by industry (national-
accounts-consistent, kt CO₂e excl. biogenic CO₂; `data/bronze/dk_direct_emissions_drivhus.csv`).
Scope construction mirrors the expenditure boundary:
QA Human health + 870000 Residential care + α × 880000 Social work w/o accommodation,
with α = 0.4914 derived from the supply-use tables (split of 880000's products between
purposes 12401 eldercare and 12402 childcare), minus hospital N₂O (medical gas, moved to
B_ANAE). For 2019: 106 + 23 + 0.4914×67 − 11 ≈ **151 kt CO₂e**. This restores the
Steenmeijer design (national-accounts direct figure excluding medical gases, injected via
`Hstim`).

## 3. E3 - GHG-Protocol scopes misconstructed

**Defect:** "Scope 2" summed electricity/heat-sector emissions over the **entire global
supply chain** (i.e. mostly Scope 3); "Scope 1 (MRIO)" was the 1.39 kt artifact; pMDIs
were booked to Scope 1.

**Fix:** Scope 1 = DRIVHUS direct + anaesthetic gases; Scope 2 = generation emissions of
energy purchased *directly* by the providers (energy-sector entries of the scaled
intermediate-input column × those sectors' own direct intensity); Scope 3 = remaining
supply chain + pMDI (use-phase at patients' homes) + commuting; patient/visitor travel =
outside protocol - matching Steenmeijer et al.'s Table S8 classification.

## 4. Bottom-up items - Danish primary data replace NL-scaled proxies

| Item | Old (NL × factor) | New | Source |
|---|---|---|---|
| Anaesthetic gases | 9.51 kt (NL × 0.67, births proxy) | **12.7 kt** = 38 t N₂O/yr × 298 (11.3) + population-scaled volatiles (1.4) | Denmark's National Inventory Document 2024 (DCE rep. 622), cat. 2.G.3.a; volatiles proxy pending Danish data |
| pMDI propellants | 34.61 kt (NL × 0.45) | **12.8 kt** = 7.2 t HFC (90/10 HFC-134a/227ea) × ReCiPe 2016 GWP100 | Vestbo & Press-Kristensen 2023, Eur Respir J 62:2300856; Danish EPA F-gas inventory 11.6 kt (2022, GWP100). NB: the often-quoted 31 kt is **GWP20** |
| Commuting | factor 0.544 | factor **0.5719** | employment DST NABB69 2019 (86000+87880 = 518,889) ÷ NL 1,220,750; hours 34.4/29.2; TU 2019 Table 20 distance 9.0 vs NL 7.88 km/person/day |
| Patient/visitor travel | factor 0.636 | factor **0.6300** (employment update) | no Danish primary source exists (verified); TU microdata named as future route |

The old pMDI value was ~2.7× too high (GWP20/GWP100 conflation propagated through the
Dutch scaling); the anaesthetic value was ~25% low and its N₂O part now comes from the
national inventory, coherent with the DRIVHUS netting (the accounts carry ~11 kt CO₂e of
hospital N₂O, removed from B_HEAL and re-entered via B_ANAE).

## 5. Currency and prices

DKK→EUR at the Danmarks Nationalbank 2019 annual average **7.4661** (was flat 7450 per
kDKK→M€, −0.22%). Basic-price basis verified: the loader reads sheet `Ubas` (use table at
basic prices), which is why `Conversion=1.0` is correct - now documented in code. The
2019-expenditure-on-2016-price-model mismatch (Reviewer 2) is addressed via a deflation
scenario in the uncertainty package (`src/analysis/uncertainty_2025.py`), and disappears
entirely in the planned 2022-on-2022 analysis.

## 6. Presentation/robustness fixes

- Transport disaggregation mask changed from substring (`contains('Transport')`, which
  also captured **Transport Equipment** = vehicle manufacturing) to exact group match.
- Stray no-op statement removed; `.count()[0]` → `.count().iloc[0]`, label writes made
  Copy-on-Write-safe, NumPy scalar conversions fixed (pandas 3 / NumPy 2 compatibility -
  numerically neutral).
- Loader accepts `F_Y.txt` (EXIOBASE ≥3.8) and `F_hh.txt` (3.7).
- Bottom-up file's `ISO2` provenance column no longer breaks row widths.

## 7. Result bridge (2019 expenditure, EXIOBASE 3.8.2-2016)

Filled from the corrected run; see `data/gold/results/` and
`docs/revision/results_bridge.md` for the step-by-step decomposition
(submitted → corrected), each step attributable to exactly one entry above.

## 8. Known remaining limitations (carried to the manuscript)

- Waste extension remains the 2011 hybrid-EXIOBASE waste-supply account divided by 2016
  monetary output (Steenmeijer precedent, disclosed); a rebuilt 2022-compatible waste
  extension (Eurostat env_wasgen-anchored, WIO-style) is planned for the 2022 analysis.
- Pharmaceuticals map to EXIOBASE `Chemicals nec` (aggregation bias with known sign);
  treated as a discrete scenario in the uncertainty package.
- Capital formation (GFCF) excluded, as in Steenmeijer et al.; acknowledged one-directional.
- Volatile anaesthetics remain a population-scaled proxy (no Danish inventory exists).
- The EXIOBASE-estimated input recipe of the DK "Health and social work" industry drives
  the transport-dominance result; validation against the Danish national IO health columns
  is part of the planned SUT-integration work (`docs/revision/dk_snac_feasibility.md`).
