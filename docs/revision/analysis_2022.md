# Denmark 2022: primary analysis (Steenmeijer replication tier)

> **Model changed, 2026-09-07.** The background is now **EXIOBASE v3.8.2
> `IOT_2022_ixi`**, with a Danish sea-transport reallocation applied. v3.10.2 was
> withdrawn: its 2022 nowcast misallocates the Danish block (health output 2.8×
> too low, education 4.8× too high, financial intermediation and machinery
> near-zero), and it empties industry 33 across Europe in every year. See
> [`../methods/exiobase_version_vintage_and_classification.md`](../methods/exiobase_version_vintage_and_classification.md).
> Every headline number below has been regenerated; the numbers in §3 supersede
> all earlier versions.

**Model:** EXIOBASE v3.8.2 `IOT_2022_ixi` (Zenodo 5589597) with the Danish
sea-transport reallocation of Rørmose Jensen & Iliev (2022)
with climate characterised on **IPCC AR6** GWP100
× Danish 2022 expenditure (health + eldercare) × DRIVHUS/AFFALD direct accounts ×
Danish-primary bottom-up items. Run:

```
HC_BACKGROUND_YEAR=2022 python -m pipelines.prep_background_2025.load
HC_BACKGROUND_YEAR=2022 python -m pipelines.prep_background_2025.leontief
HC_BACKGROUND_YEAR=2022 python -m pipelines.prep_background_2025.process
python -m analysis.dk_shipping_correction
HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship python -m analysis.main_2025
```

## 1. Inputs (all public, API-reproducible)

- **Expenditure, basic prices:** built from the published 117-industry IO workbook
  (`input_output_en_2022.xlsx`, StatBank): household consumption from the CP sheet's
  COICOP columns, NPISH + marketed/non-market individual government from the IO sheet's
  purpose columns; only industry-coded (basic-price) rows summed. COICOP-2018 codes:
  06112 pharma; 06134 appliances; 06200 out-patient; 06300/06340/06400 hospital;
  13302 eldercare (13301 childcare excluded, flag available). Totals: pharma
  DKK 14.51 bn, appliances 8.14 bn, services 279.37 bn → **DKK 302.0 bn = €40,597 M**
  at 7.4396 DKK/EUR (DNB 2022 average). Cross-check: SHA1 CHE 2022 = 271.9 bn + social
  LTC 30.0 bn. Unlike 2019, no confidential SUT extract is needed: the 2022 vector is
  fully reproducible from public tables. Provenance: `dk_expenditure_breakdown_2022.csv`.
- **Direct emissions:** DRIVHUS 2022, QA 92 + 870000 19 + α×880000 60 − hospital
  medical N₂O 11 = **118.6 kt CO₂e**. The eldercare share α = **0.3092** is now read
  from the analysis year's own IO table (industry 880000's deliveries to eldercare
  13302 vs childcare 13301: 15.54 vs 34.72 bn DKK), replacing the 0.4914 carried
  forward from the 2019 detailed SUT, a documented open item now closed.
- **Direct waste:** AFFALD01 2022 (excl. soil), same boundary and same α = **42.8 kt**.
- **Bottom-up:** anaesthetics 11.6 kt (N₂O 11.3 from NID 2.G.3.a, volatiles 1.2
  from medstat.dk ATC N01AB sales, no longer a proxy);
  pMDI **11.6 kt** (Danish EPA F-gas inventory 2022 actual, GWP100); commuting factor
  0.6343 (NABB69 2022 employment 556,999; TU 2022 distance 9.3 km/p/d); visitor 0.6762.

## 2. Background build (v3.10.2 restructure)

v3.10.2 ships Z/x/Y at the archive root and satellites in eight domain folders
(733 stressors stacked; empty cells → 0). A = Z x̂⁻¹; L inverted directly. The
characterisation bridge is rebuilt: GWP (22 rows), blue water (103), and VA map 1:1 by
stressor name from the Steenmeijer/DESIRE selection; abiotic material extraction (29
rows: Metal Ores + Non-Metallic Minerals), land (all 26 land-account rows), and
employment are rebuilt from the restructured v3.10.2 names with the same concept
definitions. **Multiplier-outlier screening** (Rørmose Jensen & Iliev 2022 failure
mode: emission accounts on near-zero-output industries, observed here as GB medical
instruments at 2×10⁸ kt CO₂e/M€ injecting 2,025 kt into the appliances footprint):
air-emission entries with intensity >100× the cross-region sector median, or sitting
on outputs <1 M€, are replaced by the median intensity × actual output (96,833
entries). Screening is restricted to air emissions: extraction/land/water accounts
are legitimately concentrated, and a median test would crush real mines (concentrated-
stressor caution, Jakobs 2023). Validation: the screened model's Danish national CBA
GWP is **64.7 Mt vs DST's official AFTRYK 62.9 Mt (+2.9%)**; unscreened: 69.3 Mt.
Waste extension: 2011 hybrid accounts over 2022 output (Steenmeijer precedent),
direct entry replaced by AFFALD; wide MC band; rebuild planned per the waste protocol.

## 3. Headline results, Denmark 2022

| Indicator | Health-care footprint | Danish national footprint | Share, full footprint | Share, supply-chain component |
|:---|:---|:---|:---|:---|
| Climate change | **4,712.4 kt CO₂e** (802 kg per person) | 77,477.5 kt | 6.1 % | 5.1 % |
| Material extraction | 4,259.4 kt | 53,939.3 kt | 7.9 % | 7.8 % |
| Blue water | 95.5 Mm³ | 1,276.4 Mm³ | 7.5 % | 7.5 % |
| Land use | 4,855.5 km² | 99,466.2 km² | 4.9 % | 4.9 % |
| Waste generation | 259.4 kt | 10,587.3 kt | 2.5 % | 2.0 % |

*Two bases are given because they answer different questions and the study's own
rule is that a share is meaningless without one. The full footprint adds the
Danish bottom-up items to the supply-chain component; those items are almost
entirely climate, which is why the two shares differ materially for climate and
waste and barely at all for the other three. Source:
`00_core_footprint/national_totals_summary.csv` and the tables of record.*

**Scopes (GHG Protocol, `analysis.scopes_detail`):**
**S1 130.1 / S2 75.0 / S3 4,243.5 / outside-protocol 263.6 kt CO₂e.**
Partition asserted exact; producing-node detail reconciles. All six IO
identities pass at ≤10⁻¹⁰ (`analysis.validate_io_identities`).

**By producing sector group (climate, share of the 4,712 kt total):**
transport 15.4 %, coal and petroleum 13.4 %, private travel 13.3 %, food and
catering 12.9 %, chemicals 9.4 %, electricity 9.0 %, steam and hot water 6.4 %,
waste management 4.7 %, services 3.3 %.

These figures are producing-node shares, taken from `hotspot_by_sector_group.csv`
(`B diag(L y)`). The purchased-product view of the same footprint is a different
table (`contribution_by_purchased_product.csv`, `B L diag(y)`) and gives a
different ranking; the two must not be quoted interchangeably.

**Monte Carlo** (100,000 draws, `analysis.uncertainty_2025`): median
**4,734 kt**, 95 % interval **4,064 to 5,531 kt**, CV **7.87 %**, alongside
Lenzen et al.'s published 8.35 % for Denmark. First-order variance shares: MRIO
parameters 78.8 %, the covariance between commuting and visitor travel 9.3 %,
visitor travel 6.7 %, commuting 5.1 %; every other bottom-up item below 0.1 %.

**Capital boundary.** Capital is excluded in the headline, for comparability with
Steenmeijer, Eckelman, Lenzen, and Pichler. Including it adds **13.2 %**
(exogenous CFC from Danish national accounts) or **19.4 %** (endogenised on the
published Södersten et al. 2018 capital matrices; our own simplified
endogenisation gave 21.0 %, which the published route reproduces to within 1.6
percentage points). See [`capital_gfcf_treatment.md`](capital_gfcf_treatment.md).

Scope 2 is 1.6 % of the total, against Arup's 8.3 % for Denmark in 2014. The
direction is right (the Danish grid fell from roughly 300 to 120 g CO₂/kWh over
that period), but 2022 was also an energy-price spike year, so a given euro of
electricity spend buys far less power, and a monetary model understates physical
consumption. Both effects push the same way, and neither is separately identified
here; the gap is flagged as an open item, not claimed as a finding.

**Climate characterisation: IPCC AR6.** The workbook shipped with the
background carries AR4 factors (CH₄ = 25, N₂O = 298) under a "CML 1999" label.
The climate row is rebuilt on AR6 (`analysis.constants.ar6_gwp_factor`), which
also distinguishes fossil from non-fossil methane (29.8 against 27.0) as AR4 did
not. Vintage sensitivity, healthcare supply chain: SAR 3,740 · TAR 3,791 ·
AR4 3,855 · AR5 3,956 · **AR6 3,945 kt**. **3.9 % (155 kt) cannot be restated at
all**: EXIOBASE supplies HFC and PFC already aggregated in CO₂-equivalent, so
their vintage is fixed inside the data. See `15_gwp_vintage/`.

### Bottom-up items now on Danish primary data

| Item | Value | Source |
|:---|:---|:---|
| Anaesthetic gases | **11.6 kt** (N₂O 11.3 + volatiles 1.2) | medstat.dk ATC N01AB sales (sevoflurane 2,400 L, desflurane 181 L, isoflurane 15 L), densities from Laster et al. 1994, GWP₁₀₀ from Sulbaek Andersen et al. 2023; N₂O from NID 2.G.3.a |
| Patient + visitor travel | **263.6 kt** (patient 213.2 + visitor 50.3) | TU (DTU) Tabel 15, purpose 33 "Social/sundhed", 0.8 km/person/day; visitor uplift 0.236 from NHS England |
| pMDI propellants | 11.6 kt | Danish EPA F-gas inventory 2022 |
| Direct operational | 118.6 kt CO₂e, 42.8 kt waste | DRIVHUS, AFFALD01 |

The travel item previously scaled a **whole-population** Dutch quantity by an
employment ratio and by weekly working hours, a unit error, since those belong
to commuting alone. It is now built from Danish measurement instead of the
England → Netherlands → Denmark double transplant. The anaesthetics item is no
longer a population-scaled Dutch proxy and now shows the Danish desflurane
phase-out (400 L in 2019 → 181 L in 2022), which a fixed proxy could not.

## 4. The transport headline was a Danish shipping artefact

The submitted manuscript reported transport at 38-43 % of the Danish healthcare
footprint. On the uncorrected v3.8.2 2022 model that finding reproduces exactly:
**transport 37.5 %** of the supply-chain footprint, with Danish sea and coastal
water transport alone contributing 852 kt.

The finding is an artefact, and the source is documented by Statistics Denmark.
Rørmose Jensen & Iliev (2022, pp. 11-12) report that EXIOBASE sends **74 %** of
Danish water-transport output to Danish *intermediate* use, against **9 %** in the
national accounts: the Danish-operated fleet carries world trade, not Danish
production. Measured on our own model the figure is **73.6 %**, reproducing their
diagnosis to the decimal. EXIOBASE even has the Danish health sector itself
buying 394 M€ of sea transport.

Applying their 9 % target (`analysis.dk_shipping_correction`; row and column
balances preserved to 10⁻¹¹, output unchanged, released value credited to value
added) gives:

| | uncorrected | corrected |
|:---|:---|:---|
| Transport share of the supply-chain footprint | 37.5 % | **18.5 %** |
| DK sea transport as a producing node | 852 kt | **74 kt** |
| Healthcare climate footprint (MRIO supply chain) | 5,231 kt | **3,943 kt** |
| Danish national CBA footprint | 85.2 Mt | **77.5 Mt** |

**Consequence for the manuscript: the "transport ≈ 40 %" finding must be
withdrawn**, not as vintage-dependent, but as a known and published
misallocation in EXIOBASE's Danish block. Pharmaceuticals, chemicals, and
equipment remain the story that survives the correction, consistent with
Steenmeijer's Dutch result.

The corrected national footprint of 77.5 Mt still exceeds DST's official AFTRYK
of 62.9 Mt by 23 %. That gap separates by **model family**, not by year: the two
published EXIOBASE-based Danish footprints are 12.90 t/capita (Schmidt & Merciai
2023) and 13.19 (this study), against 9.77 (Eurostat FIGARO), 10.71 (DST AFTRYK),
and 11.00 (Rørmose Jensen & Iliev) for the national-accounts family. Our result
is within 2.3 % of its own family. Foreign shipping rows (RoW-Asia, Germany, RoW-Middle East)
carry much of the remainder and cannot be corrected from Danish sources. This
residual gap is the strongest available argument for the full Danish SNAC tier,
and it is reported as a limitation rather than adjusted away.

## 4b. Scope-boundary sensitivity (all five indicators)

| boundary | expenditure (M€) | GWP (kt) | share | t/capita | materials | water | land | waste |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
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

## 5b. Waste boundary: what the filter does and does not establish

The hybrid extension's 19 fractions were previously summed in full. Manure,
sewage, mining waste, and unused mining material are not waste under Regulation
(EC) 2150/2002 or in Statistics Denmark's AFFALD01 (the account that supplies
the domestic tier), so the unfiltered sum was not comparable with the Danish
entry it sits beside. Construction and demolition waste and ashes are in scope
and are retained.

Effect: world industry waste 13.17 → 2.01 Gt; the Danish national
consumption-based waste footprint 22.7 → 10.6 Mt; the healthcare footprint
829 → 257 kt.

**This filter is a boundary correction, not a validation.** DST's AFFALD01 total
for all Danish industries in 2022 is 18.9 Mt, but that is production-based and
includes soil, so it cannot be compared directly with a 10.6 Mt
consumption-based figure. What can be said is that the unfiltered model exceeded
the national production total, and the filtered one no longer does. The
underlying extension is still the 2011 hybrid extrapolated over 2022 output,
which remains the largest single uncertainty in the waste indicator, and no
consumption-based waste account exists anywhere against which to test it:
not in Eurostat, FIGARO, OECD, GLORIA, or UNEP.

## 6. Remaining gaps (carried into the response letter)

Volatile anaesthetics proxy; no Danish patient/visitor-travel source (verified:
TU microdata named as route); waste extension vintage (rebuild per
`03_v2_waste_benchmarking_protocol`); α eldercare share from 2019 SUT; capital
excluded (Steenmeijer-consistent); pharma mapping as Scenario B; EXIOBASE recipe
biases quantified in `recipe_validation_2022.csv` → motivate the Danish-SNAC phase.
