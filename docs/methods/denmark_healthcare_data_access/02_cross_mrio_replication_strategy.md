# Cross-MRIO replication strategy

## 1. Objective

The Danish healthcare footprint should be estimated with a preferred Denmark-specific hybrid model and then tested against several MRIO systems.

The purpose of cross-MRIO comparison is **model uncertainty and structural sensitivity**, not to average the databases indiscriminately.

Recommended systems:

1. EXIOBASE
2. GLORIA
3. Eora
4. OECD ICIO
5. FIGARO

---

# 2. Common mathematical kernel

For every MRIO:

\[
A = Z\hat{x}^{-1}
\]

\[
L=(I-A)^{-1}
\]

\[
q=Q\hat{x}^{-1}
\]

\[
F=qLy_H
\]

where:

- \(Z\) is intermediate demand;
- \(x\) is total output;
- \(Q\) is the environmental extension;
- \(y_H\) is the harmonised healthcare final-demand vector.

A cross-MRIO comparison is valid only if the **demand boundary, reference year, price basis, GWP method and indicator definition** are harmonised as far as possible.

---

# 3. Recommended comparison framework

## Model DK-HYBRID

Preferred headline model:

\[
\text{Danish detailed SUT}
+
\text{SHA}
+
\text{Danish environmental accounts}
+
\text{foreign MRIO extension}
+
\text{bottom-up healthcare data}.
\]

This is the primary Denmark estimate.

## MRIO sensitivity models

Run the same harmonised healthcare demand concept through:

- EXIOBASE;
- GLORIA;
- Eora;
- OECD ICIO;
- FIGARO.

Do **not** substitute their native health-sector final demand directly and then call differences "MRIO uncertainty". Native health boundaries differ materially.

---

# 4. MRIO comparison

| Database | Main current/relevant structure | Health-sector detail | Environmental strength | Access | Main use here |
|---|---|---|---|---|---|
| EXIOBASE 3.10.2 | 49 regions, 163 industries, 200 products; core economic update through 2022 | broad health/social-work service plus separate goods sectors | very strong GHG, energy, water, land, materials | academic/non-commercial release on Zenodo | preferred environmental MRIO sensitivity |
| GLORIA | release-dependent; current UNEP interface describes 164 regions and 97 industry/commodity sectors; widely used v59 has 120 sectors | broad human health/social work; separate pharmaceutical manufacturing in the 97-sector technical classification | especially strong materials/resources, plus emissions, water, land and social indicators | IELab registration/download; commercial licensing separately | high-country-resolution resource/material sensitivity |
| Eora | full Eora has country-specific sector detail; Eora26 is harmonised 26-sector model | Denmark in Lenzen-era Eora had pharmaceuticals, hospital activities, medical/dental/veterinary activities; detail varies by country | broad global satellite accounts | academic registration/licensing | methodological replication of Lenzen et al. |
| OECD ICIO 2025 | 80 economies + RoW; 50 unique industries; 1995–2022 | one `Q Human health and social work activities` industry | primarily economic/value-chain framework; environmental extensions need external pairing | open downloadable CSV | trade/economic structural sensitivity |
| FIGARO 2026 | 64 industries × 64 products; 2010–2024 | broad NACE/CPA health categories | strong official EU economic/trade consistency; environmental footprint products available separately | open Eurostat CSV/Excel | official EU sensitivity and bridge |

---

# 5. GLORIA: why it should be added

## 5.1 Strengths

GLORIA was built using IELab infrastructure for the UN International Resource Panel and is explicitly resource-footprint oriented.

The current UNEP GLORIA interface describes:

- 164 regions;
- 97 industries;
- 97 commodities;
- six final-demand agents;
- five valuation layers;
- 1990–2024 time coverage.

The older/widely used GLORIA v59 family used in many academic workflows has a 120-sector classification. Because the sector count is **release-dependent**, never store "GLORIA" as though it were one immutable database.

Store:

```text
mrio_name = GLORIA
mrio_release = ...
sector_schema_version = ...
economic_data_status = observed / estimated / projected
```

## 5.2 Health representation

The 97-sector technical classification includes:

- manufacture of pharmaceuticals, medicinal chemical and botanical products;
- human health and social work activities.

That is useful because pharmaceutical manufacturing is separate even though healthcare services remain aggregated.

## 5.3 Environmental role

GLORIA is particularly valuable for:

- material extraction;
- specific mineral-resource pathways;
- global resource footprints;
- country-of-origin analysis;
- land/water/emissions sensitivity.

## 5.4 Access

Current access is routed through IELab registration/download. IELab states that data are available for download and that commercial licences are available separately through FootprintLab.

## 5.5 Implementation

For older releases, `pymrio` supports parsing and calculation. Newer GLORIA access/format should be tested before freezing the production pipeline. MARIO also supports GLORIA parsing.

---

# 6. EXIOBASE

## Why retain it

EXIOBASE remains the strongest environmental all-rounder for this project because its harmonised industry/product resolution and environmental extensions are unusually rich.

The current DOI-stamped release is 3.10.2.

The 3.10 series updates:

- economic data to 2022;
- FIGARO aggregate SUT data to 2022;
- bilateral trade to 2022;
- energy balances to 2022;
- land and water extensions;
- GHG extensions.

## Health limitation

EXIOBASE's health service itself remains broad. Therefore the preferred strategy is:

\[
\text{detailed Danish health vector}
\rightarrow
\text{Danish SUT}
\rightarrow
\text{EXIOBASE only for foreign supply chains}
\]

rather than forcing the whole Danish system into the native broad EXIOBASE health sector.

---

# 7. Eora

Eora remains essential because Lenzen et al. used Eora v199.82.

For exact methodological comparison with Lenzen:

\[
F=qLy_H
\]

should be reproduced in Eora for a common year.

## Strength

Full Eora retains country-specific classifications rather than forcing every country into one global sector list.

## Weakness

That same property makes cross-country sector harmonisation harder.

Eora26 is easier to compare but sacrifices health detail.

## Denmark-specific value

The Lenzen supplementary information showed Denmark with several health-related sectors rather than only one global health sector. This makes full Eora useful as a historical benchmark.

---

# 8. OECD ICIO

The current regular 2025 ICIO edition contains:

- 80 economies plus a rest-of-world aggregate;
- 50 unique industries;
- 1995–2022.

Healthcare is represented as:

`Q Human health and social work activities (ISIC 86–88)`.

## Use

Use OECD ICIO mainly to test:

- bilateral import structure;
- upstream economic composition;
- foreign value-chain dependence;
- sensitivity of imported footprint allocation.

It is not the preferred source for detailed environmental extensions.

---

# 9. FIGARO

FIGARO provides an official EU inter-country SUT/IOT framework:

- 64 industries;
- 64 products;
- 2010–2024;
- supply, use, product-by-product and industry-by-industry tables.

## Use

FIGARO is valuable for:

- EU trade consistency;
- Denmark-EU bilateral supply chains;
- an open sensitivity model;
- checking how much results depend on the EXIOBASE trade structure.

---

# 10. Common-year strategy

A cross-MRIO comparison should distinguish the **main Danish reference year** from the **common MRIO benchmark year**.

## Main Denmark model: 2022

Advantages:

- Danish national data are strong;
- EXIOBASE economic data are updated through 2022;
- OECD ICIO reaches 2022;
- pharmaceutical and environmental data are available.

## Cross-MRIO benchmark: 2019

Recommended for the cleanest structural comparison because:

- it is pre-pandemic;
- it is widely covered across all MRIO systems;
- it avoids relying on projected/nowcast observations in GLORIA and other databases.

## Optional second benchmark: 2021 or 2022

Use only with an explicit flag distinguishing:

- observed;
- estimated;
- projected;
- nowcast data.

---

# 11. Harmonisation protocol

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

# 12. Cross-MRIO result package

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

---

# 13. Key sensitivity KPIs

For MRIO \(m\):

\[
F_{k,m}
\]

Absolute footprint.

Cross-MRIO coefficient of variation:

\[
CV_k
=
100
\frac{\sigma(F_{k,m})}
{\overline{F}_{k}}
\]

Range:

\[
Range_k
=
\max_m(F_{k,m})-\min_m(F_{k,m})
\]

Relative deviation from the preferred Danish hybrid:

\[
RD_{k,m}
=
100
\frac{F_{k,m}-F_{k,DK}}{F_{k,DK}}
\]

Imported share:

\[
IS_{k,m}
=
100\frac{F_{foreign,k,m}}{F_{k,m}}
\]

Top-supplier overlap can also be measured using rank correlation or Jaccard overlap.

---

# 14. Interpretation rule

If EXIOBASE, GLORIA, Eora, OECD/paired-extension and FIGARO give different results, do not immediately conclude that one is "wrong".

Differences can arise from:

- sector aggregation;
- national-account revisions;
- trade balancing;
- import proportionality;
- environmental extensions;
- health-sector mapping;
- price valuation;
- reference-year construction;
- treatment of capital;
- projections/nowcasts.

The comparison should decompose these sources before interpreting the spread as uncertainty.

---

# 15. Recommended hierarchy

## Headline estimate

`DK-HYBRID`

## Main environmental MRIO sensitivity

`EXIOBASE 3.10.2`

## Resource/material sensitivity

`GLORIA`

## Lenzen replication

`Eora`

## Economic trade sensitivity

`OECD ICIO`

## Official EU sensitivity

`FIGARO`

This hierarchy gives every MRIO a clear methodological purpose rather than producing five redundant footprint estimates.
