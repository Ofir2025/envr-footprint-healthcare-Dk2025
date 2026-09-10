# Cross-MRIO replication strategy

## 1. Purpose

The study should distinguish:

\[
\text{uncertainty from the healthcare boundary}
\]

from:

\[
\text{uncertainty from the MRIO database}.
\]

A five-MRIO comparison is useful only if the healthcare demand vector and indicator definitions are harmonised as far as possible.

Recommended systems:

1. EXIOBASE
2. GLORIA
3. FIGARO
4. Eora
5. OECD ICIO

---

# 2. Preferred headline system

The primary model should remain:

\[
\boxed{
\text{DK detailed SUT}
+
\text{SHA}
+
\text{Danish environmental accounts}
+
\text{foreign MRIO extension}
+
\text{selected bottom-up replacements}
}
\]

The MRIO systems then serve different sensitivity functions.

---

# 3. GLORIA

The current UNEP GLORIA interface describes a homogeneous MR-SUT with:

- **1990-2024**;
- **164 regions**;
- **97 industries**;
- **97 commodities**;
- **6 final-demand agents**;
- **6 value-added categories**;
- **5 valuation layers**;
- current thousand USD.

GLORIA was built using IELab infrastructure for the UNEP International Resource Panel, with specific attention to **resource-flow analysis**.

Official source:

https://footprint.unep.org/gloria-mrio

## Why GLORIA matters here

GLORIA should be used particularly for:

- material extraction;
- resource footprints;
- country-of-origin resource dependencies;
- comparison of material-intensive healthcare supply chains.

## Important version rule

Older widely used GLORIA releases have different sector counts, including 120-sector configurations.

Therefore never store:

```text
mrio = GLORIA
```

alone.

Store:

```text
mrio = GLORIA
release
sector_schema_version
region_schema_version
year
projection_status
```

---

# 4. EXIOBASE

Recommended role:

\[
\boxed{\text{main environmental MRIO sensitivity}}
\]

Strengths:

- high environmental extension detail;
- harmonised sector/product structure;
- water;
- land;
- materials;
- GHGs and other emissions.

Weakness:

- healthcare service categories remain coarser than the proposed Danish health taxonomy.

Use the current fixed release selected for the paper and store the release DOI/version.

---

# 5. FIGARO

Recommended role:

\[
\boxed{\text{official EU economic/GHG benchmark}}
\]

Strengths:

- Eurostat national-account foundations;
- trade balancing;
- Q86 human health separated from Q87-Q88;
- C21 pharmaceuticals separate;
- official Eurostat FIGARO GHG footprint datasets.

Weaknesses:

- only 64 industries/products;
- medical devices and many clinical goods are aggregated.

---

# 6. Eora

Recommended role:

\[
\boxed{\text{Lenzen replication}}
\]

Strength:

The Lenzen et al. global healthcare assessment used Eora, so Eora is the appropriate database for methodological comparability.

Weakness:

Full Eora uses country-specific sector classifications, making harmonisation less straightforward.

Run:

- native Eora health boundary;
- harmonised external healthcare boundary where practical.

---

# 7. OECD ICIO

Recommended role:

\[
\boxed{\text{economic trade/value-chain sensitivity}}
\]

Strengths:

- strong international economic framework;
- long time series;
- transparent sector harmonisation.

Weakness:

- healthcare is broad;
- environmental extensions are not as rich as EXIOBASE/GLORIA for the full footprint suite.

---

# 8. Common comparison years

## Headline Danish year

\[
2022
\]

Reasons:

- final Danish SUT detail exists for final years;
- Danish environmental accounts available;
- healthcare/medicines data available;
- EXIOBASE/OECD data coverage can be aligned.

Statistics Denmark states that SUTs from 2014 onward are consistent with the latest 2022 table under the current revision, with previous-year-price consistency from 2015-2022.

## Common MRIO benchmark

\[
2019
\]

Reasons:

- pre-pandemic;
- broad overlap across databases;
- minimises extraordinary health-system/economic distortions;
- reduces dependence on projected or nowcast components.

Run 2022 as a second benchmark where each database's 2022 economic status is documented.

---

# 9. Harmonised healthcare demand

Construct one reference health vector:

\[
y_H^{common}.
\]

Map it to each database:

\[
y_{H,m}
=
B_m y_H^{common}.
\]

For each MRIO \(m\), record:

\[
Coverage_m
=
\frac{\sum y_{H,m}^{mapped}}
{\sum y_H^{common}}.
\]

No MRIO result should be interpreted without reporting mapping coverage.

---

# 10. Native versus harmonised runs

For each MRIO generate:

## Native

Uses the database's native health industry/product definition.

## Harmonised

Uses our SHA-derived healthcare boundary.

Then:

\[
BoundaryDifference_m
=
F^{harmonised}_m-F^{native}_m.
\]

This prevents health-definition differences from being mistaken for MRIO differences.

---

# 11. Common equations

For database \(m\):

\[
A_m=Z_m\hat{x}_m^{-1}
\]

\[
L_m=(I-A_m)^{-1}
\]

\[
q_{k,m}=Q_{k,m}\hat{x}_m^{-1}
\]

\[
F_{k,m}=q_{k,m}L_my_{H,m}.
\]

---

# 12. Cross-MRIO indicators

Absolute spread:

\[
Range_k
=
\max_mF_{k,m}
-
\min_mF_{k,m}.
\]

Coefficient of variation:

\[
CV_k
=
100\frac{sd(F_{k,m})}{mean(F_{k,m})}.
\]

Deviation from the Denmark-specific hybrid:

\[
RD_{k,m}
=
100\frac{F_{k,m}-F_{k,DK}}{F_{k,DK}}.
\]

Imported impact:

\[
IS_{k,m}
=
100\frac{F_{foreign,k,m}}{F_{k,m}}.
\]

---

# 13. Do not average MRIO results blindly

An arithmetic mean of five databases does not automatically produce a better footprint.

Differences can be structural:

- trade balancing;
- product aggregation;
- economic year;
- environmental extension;
- rest-of-world construction;
- import proportionality;
- healthcare mapping.

The preferred outcome is:

\[
\text{central Denmark-specific estimate}
+
\text{structured sensitivity envelope}.
\]

---

# 14. Suggested results table

| Indicator | DK hybrid | EXIOBASE | GLORIA | FIGARO | Eora | OECD | spread | interpretation |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| GHG | | | | | | | | |
| Water | | | | n/a/limited | | | | |
| Scarce water | | | | n/a | | | | |
| Materials | | | | n/a/limited | | | | |
| Land | | | | n/a/limited | | | | |
| PM | | | | limited | | | | |
| NOx | | | | FIGARO extension if available | | | | |
| SO2 | | | | | | | | |

Only populate cells where the underlying extension is scientifically comparable.

---

# 15. Final role allocation

| System | Primary use |
|---|---|
| DK detailed SUT | high-resolution Danish economic core |
| DK environmental accounts | domestic physical extensions |
| EXIOBASE | broad global environmental sensitivity |
| GLORIA | resource/material sensitivity |
| FIGARO | official EU GHG/trade sensitivity |
| Eora | Lenzen replication |
| OECD ICIO | trade/value-chain sensitivity |

This is a more defensible design than choosing one MRIO and treating it as ground truth.

---

# 16. Quantitative MRIO comparison

Carried forward from the earlier assessment this document supersedes, because the
narrative sections above do not otherwise put the five candidate databases side by
side with their concrete resolution and access figures.

| Database | Main current/relevant structure | Health-sector detail | Environmental strength | Access | Main use here |
|---|---|---|---|---|---|
| EXIOBASE 3.10.2 | 49 regions, 163 industries, 200 products; core economic update through 2022 | broad health/social-work service plus separate goods sectors | very strong GHG, energy, water, land, materials | academic/non-commercial release on Zenodo | preferred environmental MRIO sensitivity |
| GLORIA | release-dependent; current UNEP interface describes 164 regions and 97 industry/commodity sectors; widely used v59 has 120 sectors | broad human health/social work; separate pharmaceutical manufacturing in the 97-sector technical classification | especially strong materials/resources, plus emissions, water, land and social indicators | IELab registration/download; commercial licensing separately | high-country-resolution resource/material sensitivity |
| Eora | full Eora has country-specific sector detail; Eora26 is harmonised 26-sector model | Denmark in Lenzen-era Eora had pharmaceuticals, hospital activities, medical/dental/veterinary activities; detail varies by country | broad global satellite accounts | academic registration/licensing | methodological replication of Lenzen et al. |
| OECD ICIO 2025 | 80 economies + RoW; 50 unique industries; 1995-2022 | one `Q Human health and social work activities` industry | primarily economic/value-chain framework; environmental extensions need external pairing | open downloadable CSV | trade/economic structural sensitivity |
| FIGARO 2026 | 64 industries × 64 products; 2010-2024 | broad NACE/CPA health categories | strong official EU economic/trade consistency; environmental footprint products available separately | open Eurostat CSV/Excel | official EU sensitivity and bridge |

---

# 17. Harmonisation protocol

Also carried forward, because it is the explicit step sequence that sections 9-10
assume rather than spell out.

## Step 1: freeze healthcare scope

Create one common taxonomy, for example:

```text
HC_SERVICES
HC_PHARMACEUTICALS
HC_MEDICAL_DEVICES
HC_ADMIN_RESEARCH
HC_CAPITAL
```

Then construct a database-specific concordance for each MRIO.

## Step 2: harmonise valuation

Record:

- basic prices;
- purchasers' prices;
- trade margins;
- transport margins;
- taxes/subsidies.

Do not compare spend multipliers with mismatched valuations.

## Step 3: harmonise currency and price year

For intensity comparisons:

\[
I_{k,m}=\frac{F_{k,m}}{E_{H,m}}
\]

all models must use comparable price-year assumptions.

## Step 4: harmonise GWP

Store:

```text
gwp_assessment_report
gwp_time_horizon
gas_species
```

Do not compare AR4-based CO2e directly with AR6-based CO2e without recalculation or clear labelling.

## Step 5: separate boundary effects from database effects

Run two comparisons:

### Native-model result

Uses each MRIO's native health structure.

### Harmonised-demand result

Uses the same externally constructed healthcare demand concept as far as mappings allow.

The second is the proper **MRIO sensitivity test**.

---

# 18. Cross-MRIO result table schema

The formal schema behind the results table in section 14, also carried forward.

Create:

`fact_mrio_comparison`

Recommended schema:

| Field | Meaning |
|---|---|
| `time_key` | reference year |
| `mrio_key` | database + release |
| `impact_key` | GHG, water, materials, etc. |
| `health_scope_key` | common health boundary |
| `price_basis_key` | price/valuation |
| `footprint_value` | absolute footprint |
| `per_capita_value` | population-normalised |
| `intensity_per_currency` | environmental intensity |
| `domestic_share_pct` | Denmark-produced share |
| `foreign_share_pct` | foreign-produced share |
| `top10_supplier_share_pct` | concentration |
| `mapping_coverage_pct` | share of healthcare expenditure mapped |
| `mapping_uncertainty_grade` | quality of concordance |
| `economic_data_status` | observed/estimated/projected |
| `notes` | caveats |
