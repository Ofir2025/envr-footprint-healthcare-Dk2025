# FIGARO feasibility assessment and replication test plan

## 1. Verdict

\[
\boxed{\text{FIGARO should be explored empirically}}
\]

It is **not** sufficiently detailed to replace the Danish working-level SUT, but it is a stronger healthcare benchmark than previously assumed.

The current 2026 FIGARO edition provides:

- 64 industries;
- 64 products;
- 2010-2024;
- supply tables;
- use tables;
- industry-by-industry inter-country IOTs;
- product-by-product inter-country IOTs;
- direct purchases abroad;
- CSV flat and matrix files.

Official source:

https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/database

---

# 2. Why FIGARO is particularly valuable

FIGARO provides something unusual:

\[
\text{official EU national accounts}
+
\text{international trade balancing}
+
\text{Eurostat environmental accounts}
+
\text{published GHG footprint results}.
\]

This lets us test both:

1. our matrix implementation;
2. our healthcare mapping.

---

# 3. Healthcare resolution is better than “health and social work”

At the A64 classification used in FIGARO, relevant categories include separate:

- **Q86 Human health activities**;
- **Q87-Q88 Residential care and social work activities**.

This is important because healthcare can be separated from broad residential/social-care activities at the principal service-industry level.

Pharmaceutical manufacturing is also separately represented under:

- **C21 Manufacture of basic pharmaceutical products and pharmaceutical preparations**.

However, FIGARO remains coarse for other healthcare supply chains:

- medical/dental instruments fall within broader manufacturing groups;
- electromedical/electronic equipment shares broader C26 categories;
- diagnostic supplies may sit in mixed chemical/manufacturing product groups;
- individual clinical services are not resolved.

Therefore:

\[
\text{FIGARO health resolution}
>
\text{one broad health/social sector}
\]

but:

\[
\text{FIGARO health resolution}
<
\text{full Danish SUT + SHA}.
\]

---

# 4. Eurostat already publishes FIGARO GHG footprints

Eurostat publishes seven FIGARO environmental-footprint datasets:

1. `env_ac_ghgfp`
2. `env_ac_co2fp`
3. `env_ac_ch4fp`
4. `env_ac_n2ofp`
5. `env_ac_hfcfp`
6. `env_ac_pfcfp`
7. `env_ac_nf3sf6fp`

The estimates use:

- FIGARO inter-country IOTs;
- European air-emissions accounts;
- Eurostat estimates for non-European regions;
- Leontief input-output modelling.

The datasets provide origin and destination geography and final-demand attribution.

Official metadata:

https://ec.europa.eu/eurostat/cache/metadata/en/env_ac_ghgfp_esms.htm

This creates a powerful implementation benchmark.

---

# 5. The correct first test is not healthcare

Before interpreting healthcare results, reproduce a published Eurostat footprint.

## Test F0: structural accounting

For the selected FIGARO 2022 I-I table:

\[
x=Z\mathbf{1}+Y\mathbf{1}.
\]

Construct:

\[
A=Z\hat{x}^{-1}
\]

and:

\[
L=(I-A)^{-1}.
\]

Checks:

```text
dimensions
country-sector ordering
row/column orientation
currency/unit
total output reconciliation
zero-output handling
final-demand sums
```

---

# 6. Test F1: environmental extension reproduction

Obtain the relevant Eurostat air-emissions extension and calculate:

\[
q=Q\hat{x}^{-1}.
\]

Then:

\[
F=qLY.
\]

Reproduce at least one published country/final-demand GHG result.

Acceptance rule:

\[
\left|
\frac{F^{ours}-F^{Eurostat}}
{F^{Eurostat}}
\right|
< \epsilon
\]

where \(\epsilon\) is set after accounting for rounding, vintage and extension-treatment differences.

Do **not** proceed to healthcare interpretation until this test is passed or the residual is explained.

---

# 7. Test F2: Denmark native healthcare boundary

Run:

\[
y_{H1}
=
\text{native FIGARO final demand associated with Q86/health-related products}
\]

only after clarifying what is actually represented in FIGARO final demand.

Important:

> Do not simply use the output of the Q86 producing industry as healthcare final demand.

The demand vector must reflect who ultimately consumes the relevant products/services.

Store this as a deliberately coarse baseline:

`FIGARO_NATIVE_Q86`.

---

# 8. Test F3: harmonised SHA healthcare demand

Preferred FIGARO experiment:

\[
SHA
\rightarrow
CPA/A64
\rightarrow
FIGARO\ final\ demand.
\]

Construct a bridge:

`bridge_sha_figaro`

with:

```text
sha_hc
sha_hp
figaro_product
figaro_industry
weight
weight_basis
confidence
```

Then:

\[
F^{FIGARO}_{SHA}
=
qL y_{H,SHA}.
\]

This is the result that should be compared with the detailed Denmark hybrid.

---

# 9. Do not add C21 pharmaceutical output mechanically

Pharmaceutical manufacturing is an upstream industry, not automatically a separate final-demand component of healthcare.

Potential double counting arises if one adds:

\[
Q86\ final\ demand
+
C21\ industry\ output
\]

because pharmaceuticals may already enter final demand or health-service intermediate inputs.

Pharmaceutical expenditure should instead be mapped explicitly from SHA/health expenditure to relevant FIGARO products.

This same rule applies to medical equipment.

---

# 10. Test F4: compare three healthcare definitions

Run:

### H1

Native FIGARO broad healthcare definition.

### H2

SHA-mapped health services only.

### H3

Full SHA-mapped healthcare including pharmaceuticals and medical goods.

Then:

\[
BoundaryEffect
=
F_{H3}-F_{H1}.
\]

This quantifies how much of the result changes simply because the healthcare boundary is more complete.

---

# 11. Test F5: compare against Danish official IO footprint tables

For Denmark 2022 compare FIGARO results with:

- DST `EMM1MU2N`;
- DST `EMM1MU3N`;
- DST `AFTRYK1`.

Questions:

1. Is the absolute GHG footprint comparable?
2. Is the domestic/foreign share comparable?
3. Are upstream hotspot industries similar?
4. Which countries dominate foreign impacts?
5. Are discrepancies traceable to boundary or economic structure?

---

# 12. Test F6: gas-species decomposition

Use the Eurostat FIGARO gas-specific footprint datasets to construct:

\[
F_{CO_2},
F_{CH_4},
F_{N_2O},
F_{HFC},
F_{PFC},
F_{NF_3/SF_6}.
\]

Then:

\[
Share_g
=
100\frac{F_g}{F_{GHG}}.
\]

Compare with:

- Danish direct gas accounts;
- EXIOBASE;
- Lenzen/Eora species composition.

This makes FIGARO particularly useful for the gas-species KPI.

---

# 13. Test F7: geography

FIGARO footprints distinguish origin and destination geographies.

Compute:

\[
DomesticShare
=
100\frac{F_{origin=DK}}{F_{total}}.
\]

\[
EUForeignShare
=
100\frac{\sum_{r\in EU,\ r\neq DK}F_r}{F_{total}}.
\]

\[
NonEUShare
=
100-DomesticShare-EUForeignShare.
\]

Compare against AFTRYK1 and EXIOBASE.

---

# 14. FIGARO versus the Danish detailed SUT

| Capability | Detailed Danish SUT | FIGARO |
|:---|---:|---:|
| Denmark product detail | ~2,350 products | 64 |
| Industries | 117 | 64 |
| Human health separated from social care | yes | yes at Q86 vs Q87-Q88 |
| Pharmaceuticals separately visible | yes | yes C21 |
| Medical instruments detailed | potentially strong | coarse |
| Danish official balancing | strongest | harmonised/rebalanced international system |
| International supply chains | no by itself | yes |
| GHG footprint product | requires build | Eurostat publishes |
| Cross-country comparability | low/moderate | high |
| Best use | primary domestic model | official EU sensitivity/validation |

---

# 15. FIGARO uncertainty and interpretation

Eurostat notes that international tables require modelling assumptions to reconcile trade asymmetries and advises caution at detailed level.

Store:

```text
figaro_release
reference_year
economic_table_version
environmental_extension_version
observed_estimated_flag
```

Do not treat FIGARO as “official truth” merely because Eurostat publishes it.

It is an official, harmonised **modelled** inter-country system.

---

# 16. Decision criteria after the proof of concept

Retain FIGARO as a major paper benchmark if:

1. our implementation reproduces Eurostat footprints;
2. Denmark healthcare demand can be mapped without excessive unmapped expenditure;
3. Q86/C21 and associated products capture enough of the healthcare boundary for meaningful sensitivity;
4. geographic results are interpretable;
5. the healthcare result adds information beyond AFTRYK1.

## Suggested thresholds

Mapping coverage:

\[
Coverage
=
100\frac{MappedHealthExpenditure}{TotalHealthExpenditure}
\]

Target:

\[
Coverage\ge95\%.
\]

Unexplained reconciliation residual:

target below 1% where units/vintages permit.

---

# 17. Recommended FIGARO result package

`fact_figaro_healthcare`

Fields:

```text
year
figaro_release
health_boundary
final_demand_category
producer_country
producer_industry
consuming_country
impact
footprint_value
unit
domestic_foreign_flag
health_expenditure_mapped
mapping_coverage
mapping_confidence
```

---

# 18. Bottom line

FIGARO is not a substitute for the detailed Danish model.

Its scientific role is stronger:

\[
\boxed{
\text{official EU cross-border accounting benchmark}
}
\]

with an unusually valuable ability to reproduce and cross-check Eurostat's own GHG footprint calculations.

A FIGARO proof of concept should therefore occur **before** the final MRIO selection is frozen.
