# Simplified-SNAC, EXIOBASE coupling and Danish healthcare footprint accounting

## 1. Purpose

This document describes the second modelling layer:

\[
\text{augmented Danish EEIO}
\rightarrow
\text{import requirements}
\rightarrow
\text{EXIOBASE foreign multipliers}
\rightarrow
\text{total Danish healthcare footprint}.
\]

This should only be implemented after the domestic augmented model passes its accounting and validation tests.

---

# 2. Stage 15: construct a health-consumption demand matrix

The IO model and the System of Health Accounts (SHA) should be linked without confusing their accounting concepts.

Let:

\[
\mathbf Y^{NA}_{health}
\]

be the health-related national-account final demand.

Use SHA-derived allocation shares:

\[
r_{kc}
\]

where:

- \(k\) is a health product/provider/industry bridge category;
- \(c\) is a healthcare function or provider reporting category.

Then:

\[
Y^{health}_{kc}
=
r_{kc}Y^{NA}_{k}
\]

subject to:

\[
\boxed{
\sum_cY^{health}_{kc}
=
Y^{NA}_{k}
}
\]

for each relevant national-account category.

The principle is:

> SHA determines how health expenditure is subdivided, while national accounts determine the monetary totals entering the IO system.

---

# 3. Separate provider footprints from health-system expenditure footprints

Two different analytical boundaries should be reported.

## 3.1 Provider/industry footprint

Examples:

- hospitals;
- general practitioners;
- dentists;
- specialist practices;
- home nursing.

This is driven by IO industries.

## 3.2 Health-system expenditure footprint

Includes goods and services purchased to fulfil health functions, potentially including:

- pharmaceuticals;
- medical goods;
- health services;
- patient transport;
- other health-related consumption.

This boundary can be organised using SHA functions/providers.

The two totals need not be identical.

---

# 4. Pharmaceuticals and medical goods

Pharmaceutical manufacturing should not simply be reclassified as a health-service industry.

The IO model should preserve the actual economic activity classification.

Thus pharmaceuticals can appear as:

1. upstream inputs into hospitals or other providers;
2. final household/government purchases;
3. part of the health-expenditure footprint under SHA reporting.

This distinction prevents a classification error whereby an upstream manufacturing industry is treated as though it were itself a health-service provider.

---

# 5. Stage 16: capital treatment

Healthcare is capital intensive.

Important capital categories include:

- hospital buildings;
- diagnostic equipment;
- medical technology;
- ICT infrastructure;
- vehicles;
- other machinery.

Ordinary IO tables generally treat gross fixed capital formation as final demand.

The project should therefore report two variants.

## 5.1 Operational footprint

Capital remains in:

\[
\mathbf Y_{\mathrm{GFCF}}.
\]

## 5.2 Capital-inclusive health-system footprint

Health-related capital requirements are allocated to health activities through an explicit capital-use layer or capital endogenisation.

Do not simultaneously:

1. endogenise a capital flow in \(\mathbf A\), and
2. retain the same capital flow as additional health final demand.

That would double count.

Capital treatment should initially be a sensitivity analysis rather than an invisible baseline assumption.

---

# 6. Stage 17: why simplified SNAC is appropriate

There are three broad choices.

## Option A. Use EXIOBASE directly

Advantage:

- simple;
- globally balanced.

Disadvantage:

- Danish national-account blocks in EXIOBASE need not exactly reproduce Statistics Denmark.

## Option B. Full SNAC-GMRIO

Replace the Danish block in the MRIO with official Danish data and rebalance the entire global system.

Advantage:

- national consistency plus global feedback.

Disadvantage:

- technically demanding;
- produces a modified MRIO;
- requires global rebalancing.

## Option C. Simplified SNAC

Keep the official Danish domestic model intact and use the GMRIO to calculate environmental pressures embodied in imports.

Advantage:

- exact Danish domestic accounting;
- substantially easier to implement;
- no need to reconstruct the full MRIO.

This is the architecture implemented in the Palm/Statistics Denmark family of work.

For a small open economy such as Denmark, simplified SNAC is an attractive research design when the primary question concerns Denmark.

---

# 7. Domestic coefficients

Split the Danish use structure into:

\[
\mathbf A^d
\]

for domestic intermediate inputs and:

\[
\mathbf A^m
\]

for imported intermediate inputs.

Then:

\[
\mathbf L^d=
(\mathbf I-\mathbf A^d)^{-1}.
\]

For domestic final demand:

\[
\mathbf y^d,
\]

the imported intermediate requirements induced by domestic production are:

\[
\boxed{
\mathbf m^I
=
\mathbf A^m
\mathbf L^d
\mathbf y^d
}
\]

Direct imported final demand is:

\[
\boxed{
\mathbf m^F=\mathbf y^m
}
\]

Hence total import demand induced by Danish final demand is:

\[
\boxed{
\mathbf m=
\mathbf A^m
\mathbf L^d
\mathbf y^d
+
\mathbf y^m
}
\]

---

# 8. EXIOBASE foreign multipliers

For EXIOBASE define:

\[
\mathbf A^E
=
\mathbf Z^E
\widehat{\mathbf x^E}^{-1}.
\]

Then:

\[
\mathbf L^E
=
(\mathbf I-\mathbf A^E)^{-1}.
\]

Let:

\[
\mathbf F^E
\]

be environmental extensions and:

\[
\mathbf S^E=
\mathbf F^E
\widehat{\mathbf x^E}^{-1}.
\]

The global foreign supply-chain multiplier is:

\[
\boxed{
\mathbf Q^E
=
\mathbf S^E
\mathbf L^E
}
\]

This matrix gives environmental pressure per monetary unit of EXIOBASE final demand by region-sector node.

---

# 9. Stage 18: Danish import-to-EXIOBASE bridge

A concordance is needed between detailed Danish imports and EXIOBASE region-sector nodes.

The bridge should combine:

1. product mapping;
2. country-of-origin mapping;
3. currency conversion;
4. reference-year price harmonisation where needed.

Conceptually:

\[
\mathbf K
=
\mathbf K_{\text{sector}}
\mathbf K_{\text{country}}.
\]

The matrix should be sparse.

For every Danish import category \(j\):

\[
\boxed{
\sum_rK_{rj}=1
}
\]

unless a documented amount is intentionally left unallocated.

---

# 10. Detailed goods trade

For imported goods, use detailed Danish bilateral trade information wherever possible.

For product \(p\) and origin country \(c\):

\[
b_{pc}
=
\frac{
M_{pc}
}{
\sum_cM_{pc}
}.
\]

These bilateral shares are used to assign imported products to EXIOBASE producing regions.

This is preferable to the domestic technology assumption because foreign production structures and emission intensities differ from Denmark.

---

# 11. Imported services

Goods customs data are not sufficient for services.

Use service-trade / balance-of-payments information to estimate country-of-origin shares for imported services.

Services should be mapped carefully because healthcare supply chains contain substantial inputs from:

- ICT;
- professional services;
- finance;
- real estate;
- transport;
- other business services.

If bilateral detail is incomplete, use documented hierarchical allocation rules and propagate uncertainty.

---

# 12. Currency conversion

Keep currency conversion explicit.

For example:

\[
\mathbf m^{EUR}
=
c_{DKK\rightarrow EUR}
\mathbf K
\mathbf m^{DKK}.
\]

Avoid hiding currency factors inside a concordance matrix unless that design is very clearly documented.

If Danish and EXIOBASE data refer to different price years, introduce a separate deflation/reflation layer rather than treating nominal values as directly comparable.

---

# 13. Stage 19: current EXIOBASE quality control

Do not simply reproduce historical outlier thresholds used in older implementations.

The current EXIOBASE release should be evaluated afresh.

For environmental intensity \(S_{ejr}\), where:

- \(e\) = environmental extension;
- \(j\) = sector;
- \(r\) = region,

a robust regional outlier diagnostic can be:

\[
z^{MAD}_{ejr}
=
\frac{
S_{ejr}
-
\operatorname{median}_r(S_{ejr})
}{
1.4826\,MAD_r(S_{ejr})
}.
\]

Flagged intensities should trigger:

1. inspection of direct extensions;
2. inspection of sector output denominators;
3. review of EXIOBASE documentation/known issues;
4. comparison with neighbouring or structurally similar countries;
5. sensitivity analysis.

Do not automatically winsorise or delete extreme values.

Some extreme environmental intensities are genuine.

---

# 14. Stage 20: total coupled footprint

The final Danish footprint can be expressed as:

\[
\boxed{
\mathbf f^{DK}
=
\mathbf S^d
\mathbf L^d
\mathbf y^d
+
\mathbf Q^t
\mathbf A^m
\mathbf L^d
\mathbf y^d
+
\mathbf Q^t
\mathbf y^m
+
\mathbf f^h
}
\]

where:

\[
\mathbf Q^t
\]

is the EXIOBASE multiplier transformed into the Danish import classification.

The four terms represent:

1. domestic Danish supply chains;
2. foreign inputs embodied in Danish domestic production;
3. direct imported final-use products;
4. direct household environmental pressures.

---

# 15. Decomposition by health sector

For each health child \(k\), calculate:

\[
\mathbf f_k.
\]

Examples:

- hospitals;
- GPs;
- specialists;
- dentists;
- physiotherapists;
- home nursing;
- other health activities.

Results should be decomposable into:

\[
\text{domestic}
+
\text{foreign}.
\]

Foreign results should further be decomposable by:

- producing region;
- producing industry;
- imported product;
- upstream supply-chain layer.

---

# 16. Decomposition by healthcare function

Using the SHA-final-demand bridge, calculate functional footprints for categories such as:

- inpatient care;
- outpatient care;
- preventive care;
- ancillary services;
- medical goods;
- long-term health care where within scope.

This is distinct from the provider footprint.

---

# 17. Structural-path analysis

Once the model is validated, structural path analysis can identify high-impact chains.

Example:

```text
Hospital
→ pharmaceuticals
→ chemical manufacturing
→ electricity generation
→ GHG emissions
```

or:

```text
Dentist
→ medical equipment
→ fabricated metals
→ primary metals
→ mining
```

This can identify high-value data-collection targets.

If a major footprint is driven by a donor-estimated coefficient, that coefficient becomes a priority for Danish primary data collection.

---

# 18. Avoid double counting in the international coupling

The simplified-SNAC architecture must separate:

- domestic production;
- imported intermediate inputs;
- imported final use.

Do not apply the full EXIOBASE multiplier to Danish domestic production and then add domestic Danish emissions again.

Likewise, if capital is endogenised into the technical matrix, do not also add the same capital final demand as an additional health-system burden.

A transparent accounting map should specify exactly which layer accounts for each flow.

---

# 19. Baseline result set

The first publication-grade footprint model should report:

## Economic

- gross output;
- intermediate consumption;
- value added;
- import dependence.

## Environmental

Initially:

- GHG emissions.

Then, where robust:

- energy;
- water;
- materials;
- land;
- selected air pollutants.

## Spatial

- Denmark;
- EU;
- other Europe;
- China;
- other Asia;
- North America;
- other world regions.

## Supply-chain

- direct health-provider impacts;
- domestic upstream;
- imported direct;
- imported upstream.

---

# 20. Why this architecture is preferable

This approach preserves the strongest information at each analytical scale:

\[
\boxed{
\text{Statistics Denmark}
\rightarrow
\text{domestic technology and national margins}
}
\]

\[
\boxed{
\text{SHA/admin data}
\rightarrow
\text{health-specific allocation}
}
\]

\[
\boxed{
\text{USEEIO}
\rightarrow
\text{residual technological priors}
}
\]

\[
\boxed{
\text{EXIOBASE}
\rightarrow
\text{foreign supply-chain completion}
}
\]

It avoids the two weakest alternatives:

1. treating EXIOBASE's Danish block as more authoritative than Statistics Denmark;
2. treating US healthcare production structures as though they were Danish observations.
