# Danish SUT reconstruction and health-sector disaggregation

## 1. Purpose

This document describes the domestic modelling component:

\[
\text{official Danish SUT}
\rightarrow
\text{health-sector augmentation}
\rightarrow
\text{balanced augmented SUT}
\rightarrow
\text{augmented Danish IOT/EEIO}.
\]

The central principle is that sector detail should be added without changing the aggregate Danish national accounts unless a clearly documented alternative dataset is intentionally introduced.

---

# 2. Stage 0: define the accounting architecture

Before collecting detailed health data, formalise the matrices.

Let:

\[
\mathbf V\in\mathbb R^{P\times I}
\]

be the supply matrix, with products \(P\) in rows and industries \(I\) in columns.

Let:

\[
\mathbf U^d,\mathbf U^m\in\mathbb R^{P\times I}
\]

be domestic and imported intermediate-use matrices.

Let:

\[
\mathbf Y^d,\mathbf Y^m\in\mathbb R^{P\times F}
\]

be domestic and imported final-demand matrices.

Let:

\[
\mathbf W\in\mathbb R^{R\times I}
\]

contain value added and other primary inputs.

Let:

\[
\mathbf F\in\mathbb R^{E\times I}
\]

contain environmental extensions.

The model should also contain explicit concordance matrices:

\[
\mathbf C^{DB\rightarrow ISIC},
\]

\[
\mathbf C^{SHA\rightarrow DB},
\]

\[
\mathbf C^{USEEIO\rightarrow DB},
\]

\[
\mathbf C^{DK\rightarrow EXIO},
\]

and:

\[
\mathbf C^{country\rightarrow EXIOregion}.
\]

---

# 3. Create a reproducible data dictionary

Every input dataset and transformed variable should be documented.

Recommended fields:

```text
variable
description
unit
price_basis
reference_year
classification
geography
source
source_version
original_file
transformation
quality_flag
uncertainty
licence
```

This is especially important because hybrid IO models combine datasets that can differ in:

- classification;
- year;
- price basis;
- currency;
- geographical coverage;
- physical/monetary units;
- accounting boundaries.

Wiedmann et al. identify balancing, allocation, concordance, sectoral and regional aggregation, temporal mismatch, exchange rates and price conversion as important uncertainty sources in hybrid LCA.

---

# 4. Stage 1: reproduce the official Danish national-account system

Before adding health-sector detail, reproduce the public model.

## 4.1 Minimum input data

| Dataset | Required information |
|---|---|
| Supply table | products × industries |
| Use table | products × industries |
| Imports | products |
| Exports and re-exports | products |
| Final demand | household, NPISH, government, investment, exports |
| Value added | compensation, surplus, taxes/subsidies |
| Official IOT | 117 × 117 benchmark |
| Gross output | industries |
| Environmental accounts | environmental flow × industry |
| Household environmental flows | direct final household emissions |

The final detailed Danish SUT system operates at approximately 2,350 products and 117 industries.

The public symmetric input-output tables are available at 117-industry resolution and should be used as the public validation benchmark.

---

# 5. Stage 2: reproduce Statistics Denmark's SUT-to-IOT transformation

Statistics Denmark applies the fixed-product-sales-structure assumption, commonly known as **Method D**, when converting SUTs to an industry-by-industry IOT.

The conceptual assumption is:

> each product has its own sales structure regardless of which industry produced it.

A high-quality replication should reproduce the official 117 × 117 IOT before the health sector is altered.

A simplified representation of product import coefficients is:

\[
r_p^m=
\frac{
m_p-\text{reexports}_p
}{
(q_p-\text{exports}_p)+(m_p-\text{reexports}_p)
}.
\]

These coefficients can be used to divide uses into domestic and imported components.

A product-industry market-share structure based on the supply table then reallocates product flows to supplying industries.

## Replication gate

If:

\[
\mathbf Z^{replicated}_{117}
\]

does not reproduce the official:

\[
\mathbf Z^{official}_{117},
\]

within documented tolerances, stop and investigate the discrepancy.

Do not proceed to health-sector augmentation until the base system is correct.

---

# 6. Stage 3: inspect how much health detail already exists in the detailed Danish SUT

This is a mandatory diagnostic step.

Before using USEEIO, identify all health-related products in the detailed Danish SUT.

For each relevant product extract:

```text
product_code
product_description
producing_industry
domestic_output
imports
intermediate_use
household_use
government_use
NPISH_use
investment
exports
```

Construct health-specific submatrices:

\[
\mathbf V_H
\]

and:

\[
\mathbf U_H.
\]

The question is:

> Does Denmark already possess product-level health detail that disappears when the official SUT is converted into the 117-industry IOT?

If yes, use that information first.

---

# 7. Stage 4: define the health-sector classification

## 7.1 Economic activity backbone

For 2019 and 2022, use:

\[
\text{DB07}\leftrightarrow\text{NACE Rev.2}\leftrightarrow\text{ISIC Rev.4}.
\]

A useful starting disaggregation of Division 86 includes:

| DB07 | Analytical child sector |
|---|---|
| 861000 | Hospitals |
| 862100 | General medical practitioners |
| 862200 | Medical specialists |
| 862300 | Dentists |
| 869010 | Health visitors, home nursing, midwives etc. |
| 869020 | Physiotherapists and occupational therapists |
| 869030 | Psychological counselling |
| 869040 | Chiropractors |
| 869090 | Other health activities |

The exact final number of sectors should depend on whether robust data can support differentiated production recipes.

## 7.2 Core and extended boundaries

### Core health system

\[
\text{ISIC/NACE Division 86}.
\]

### Extended health-and-care system

Potentially add:

\[
87=\text{residential care}
\]

and:

\[
88=\text{social work without accommodation}.
\]

These should be reported separately because the industry boundary is not identical to the System of Health Accounts expenditure boundary.

---

# 8. Stage 5: construct a permanent classification crosswalk

Create:

```text
health_id
DB07
NACE_rev2
ISIC_rev4
SHA_HP
SHA_HC
USEEIO_BEA
NAICS
EXIOBASE
DB25
NACE_rev2_1
ISIC_rev5
```

This is particularly important because Denmark has moved to DB25 for many statistical domains while historical national-account systems and the proposed benchmark years are built on DB07.

---

# 9. Stage 6: estimate the size of each child health industry

Let the original health parent industry be \(H\), divided into children \(k=1,\ldots,K\).

Require:

\[
x_H=\sum_{k=1}^{K}x_k.
\]

A first set of child-output priors can be constructed from:

\[
w_k=
\frac{\widetilde{x}_k}
{\sum_k\widetilde{x}_k}
\]

and:

\[
x_k=w_kx_H.
\]

However, \(w_k\) should be reconciled using several Danish sources rather than derived from one dataset.

## 9.1 Evidence hierarchy for child output

Recommended order:

\[
\boxed{
\text{National accounts/provider accounts}
>
\text{SHA}
>
\text{administrative activity data}
>
\text{foreign donor data}
}
\]

Potential Danish sources include:

- integrated public accounts;
- regional/provider financial accounts;
- System of Health Accounts;
- DRG and patient-register information;
- public/private practitioner expenditure;
- health-insurance information;
- labour/FTE statistics;
- household budget information;
- pharmaceutical statistics.

---

# 10. Do not equate SHA expenditure with industry gross output

This is a crucial accounting point.

SHA describes healthcare expenditure by:

- function;
- provider;
- financing scheme.

The IO/SUT system describes:

- industry output;
- intermediate consumption;
- value added;
- final demand.

Therefore:

\[
\boxed{\text{SHA expenditure}\neq\text{industry gross output}}
\]

unless a specific bridge demonstrates equivalence for the component concerned.

SHA should generally be used as:

- an allocation key;
- a structural prior;
- an independent validation dataset.

National-account totals should remain the hard accounting margins.

---

# 11. Stage 7: construct differentiated health production recipes

This is the core scientific challenge.

Avoid:

\[
\mathbf a_{\text{hospital}}
=
\mathbf a_{\text{GP}}
=
\mathbf a_{\text{dentist}}.
\]

If all child sectors simply inherit the parent recipe, the disaggregation adds labels but little new technology information.

## 11.1 Recipe evidence hierarchy

### Level 1. Detailed Danish SUT

Preferred source for product inputs.

Potential categories include:

- pharmaceuticals;
- medical equipment;
- electricity;
- district heating;
- fuels;
- cleaning;
- catering;
- laboratories;
- ICT;
- transport;
- professional services;
- property services;
- waste treatment.

### Level 2. Danish provider procurement and accounts

Particularly valuable for hospital and regional health services.

### Level 3. Physical activity data

Examples:

\[
\frac{\text{kWh}}{\text{bed-day}},
\]

\[
\frac{\text{pharmaceutical expenditure}}{\text{patient}},
\]

\[
\frac{\text{laboratory expenditure}}{\text{test}},
\]

\[
\frac{\text{fuel}}{\text{ambulance-km}}.
\]

### Level 4. USEEIO donor priors

Use only where Danish information is absent or too aggregated.

---

# 12. Stage 8: how USEEIO should be used

USEEIO is useful because US input-output accounts provide relatively detailed service and healthcare activity structures.

However, the safest strategy is:

\[
\boxed{\text{transfer composition rather than absolute US coefficients}}
\]

For child sector \(k\), define the US requirement vector:

\[
\mathbf a^{US}_k.
\]

Convert it to shares:

\[
p^{US}_{ik}=
\frac{
a^{US}_{ik}
}{
\sum_i a^{US}_{ik}
}.
\]

If Danish intermediate consumption for child \(k\) is:

\[
IC^{DK}_k,
\]

construct the prior:

\[
\widetilde U_{ik}
=
p^{US}_{ik}IC^{DK}_k.
\]

This preserves the Danish scale while allowing the US structure to act as a **prior**.

It should not yet be treated as the final Danish production recipe.

---

# 13. Why direct copying from USEEIO is weak

A direct monetary coefficient transfer assumes that:

- relative input prices are sufficiently comparable;
- production technology is similar;
- outsourcing structures are similar;
- institutional arrangements are similar;
- regulation is similar;
- accounting boundaries are compatible.

These assumptions are particularly strong for healthcare.

Agez et al. explicitly caution that transferring US environmental information to other countries imposes US technological and regulatory assumptions.

For Denmark, the preferred strategy is therefore:

\[
\text{Danish observation}
>
\text{Danish proxy}
>
\text{European/regional proxy}
>
\text{USEEIO donor prior}.
\]

---

# 14. Stage 9: cell-level data-quality metadata

Every estimated cell in the augmented SUT should receive a quality/status flag.

Suggested system:

| Flag | Meaning |
|---|---|
| A | direct Danish observation |
| B | derived Danish observation |
| C | Danish administrative allocation |
| D | foreign donor prior |
| E | proportional fallback |
| Z | structural zero |
| M | genuinely missing |

This distinction is important because:

\[
0\neq\text{missing}.
\]

A structural zero should not automatically be filled merely because a donor IO table contains a positive transaction.

---

# 15. Stage 10: reconcile the augmented SUT using constrained optimisation

Let:

\[
\widetilde U_{pk}
\]

be the prior intermediate-use matrix for product \(p\) and health child \(k\).

Estimate:

\[
U^*_{pk}
\]

using weighted constrained least squares:

\[
\min_{U^*_{pk}\geq0}
\sum_{p,k}
\frac{
(U^*_{pk}-\widetilde U_{pk})^2
}{
\sigma^2_{pk}
}.
\]

The variance/weight parameter \(\sigma_{pk}\) should reflect source confidence.

- Danish observation: small \(\sigma\);
- Danish proxy: medium \(\sigma\);
- USEEIO donor prior: larger \(\sigma\).

---

# 16. Hard reconciliation constraints

## 16.1 Parent intermediate-input conservation

For every product \(p\):

\[
\boxed{
\sum_k U^*_{pk}
=
U_{pH}
}
\]

unless an independently justified national-account revision is introduced.

## 16.2 Parent supply conservation

\[
\boxed{
\sum_kV^*_{pk}
=
V_{pH}
}
\]

## 16.3 Value-added conservation

For primary-input category \(r\):

\[
\boxed{
\sum_kW^*_{rk}
=
W_{rH}
}
\]

## 16.4 Gross-output conservation

\[
\boxed{
\sum_kx_k=x_H
}
\]

## 16.5 Child accounting identity

For each child:

\[
x_k=
IC_k+VA_k+\text{other primary inputs}.
\]

---

# 17. Alternative reconciliation algorithms

Weighted least squares should be the main approach because it allows source-specific uncertainty.

Sensitivity models can include:

## RAS / GRAS

Useful when only row and column margins are known.

## Cross entropy

For example:

\[
\min
\sum_{p,k}
U^*_{pk}
\ln
\left(
\frac{U^*_{pk}}{\widetilde U_{pk}}
\right)
-U^*_{pk}
+\widetilde U_{pk}.
\]

## Maximum entropy

Useful when the prior matrix is sparse or where multiple weak priors need reconciliation.

The FABIO literature provides a relevant precedent for constrained least-squares and other balancing approaches in physical supply-use reconstruction.

---

# 18. Stage 11: consider product augmentation as well as industry augmentation

Adding industries alone may not eliminate aggregation error.

Suppose one broad hospital-service product is produced by several newly created hospital industries.

If all users continue purchasing the same broad product, subsequent SUT-to-IOT transformation may continue to impose a common product sales structure.

Where independent evidence exists, the project may need:

\[
\text{hospital service}
\rightarrow
\begin{cases}
\text{somatic hospital service}\\
\text{psychiatric hospital service}\\
\text{specialised hospital service}
\end{cases}.
\]

The result would be:

\[
(P+\Delta P)\times(I+\Delta I).
\]

Product disaggregation should only be introduced when data support it.

---

# 19. Stage 12: preserve both rows and columns

A common error in IO sector disaggregation is to split the input recipe while ignoring the output structure.

Working at SUT level avoids much of this problem because both:

\[
\mathbf U
\]

and:

\[
\mathbf V
\]

are explicitly augmented.

The parent sector should be **replaced by its children**, not retained in addition to them.

Thus:

\[
\boxed{
\text{parent flow}
=
\sum \text{child flows}
}
\]

rather than:

\[
\text{parent flow}+\sum\text{child flows}.
\]

This is the same general anti-double-counting principle used in hybrid LCA when a detailed representation replaces an aggregated one.

---

# 20. Stage 13: reconstruct the augmented Danish IOT

After the augmented SUT is exactly balanced, apply the replicated Danish Method D transformation.

The augmented transaction matrix is:

\[
\mathbf Z^*.
\]

Let gross output be:

\[
\mathbf x^*.
\]

Then:

\[
\mathbf A^*
=
\mathbf Z^*
\widehat{\mathbf x^*}^{-1}.
\]

The Leontief inverse is:

\[
\mathbf L^*
=
(\mathbf I-\mathbf A^*)^{-1}.
\]

For repeated simulations, solve the corresponding linear systems rather than explicitly calculating a dense inverse whenever possible.

---

# 21. Stage 14: disaggregate environmental extensions

Let the parent direct environmental flow be:

\[
F_{eH}.
\]

For a pure allocation exercise require:

\[
\boxed{
F_{eH}
=
\sum_kF_{ek}.
}
\]

## Recommended drivers

| Flow | Preferred driver |
|---|---|
| Electricity | measured electricity consumption |
| District heat | measured heat consumption |
| Fuels | fuel accounts |
| Vehicle fuels | fleet / ambulance kilometres |
| Water | metered water |
| Waste | measured waste |
| Refrigerants | facility/equipment information |
| Anaesthetic gases | procurement/activity data where compatible |
| Employment | FTE or hours |
| Compensation | payroll |
| Pharmaceutical input | purchasing expenditure or physical quantity |

If external bottom-up data imply a different direct-emission total than the official environmental accounts, the project should distinguish:

1. **official-account-consistent extension**, and
2. **alternative bottom-up extension**.

These should not be silently merged.

---

# 22. Recommended first environmental indicator

The first methodological application should prioritise greenhouse gases:

\[
\mathrm{CO_2e}.
\]

Once the model is stable, add:

- energy;
- water;
- materials;
- land;
- selected air pollutants.

Only later add broader LCIA categories where the underlying extension coverage and characterisation factors are sufficiently harmonised.

This staged strategy is preferable because hybrid LCA literature shows that environmental-flow coverage can differ substantially between PLCA and EEIO databases.

---

# 23. Domestic EEIO model

Define direct environmental intensity:

\[
\mathbf S^d=
\mathbf F^d
\widehat{\mathbf x}^{-1}.
\]

The domestic production-chain footprint of final demand is:

\[
\mathbf f^d=
\mathbf S^d
\mathbf L^d
\mathbf y^d.
\]

If direct household emissions are relevant:

\[
\mathbf f^{dom,total}
=
\mathbf S^d
\mathbf L^d
\mathbf y^d
+
\mathbf f^h.
\]

This domestic model must be validated before foreign MRIO multipliers are introduced.

---

# 24. Main domestic deliverables

At the end of this stage, the project should be able to report:

- hospital production recipes;
- GP production recipes;
- specialist production recipes;
- dental production recipes;
- other health-practitioner recipes;
- direct environmental intensities;
- domestic upstream multipliers;
- aggregation differences versus the original 117-sector model;
- uncertainty caused by donor data;
- data-quality flags for every estimated cell.

This forms the foundation for international coupling described in the next document.
