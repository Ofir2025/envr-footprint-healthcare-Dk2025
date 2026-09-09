# Validation, uncertainty, software implementation and international scaling

## 1. Purpose

A high-resolution health-sector IO model is only scientifically useful if the added detail is accompanied by stronger validation and transparent uncertainty analysis.

This document specifies the quality-control architecture.

---

# 2. Validation family 1: accounting closure

Create product and industry aggregation matrices:

\[
\mathbf P_P
\]

and:

\[
\mathbf P_I.
\]

The augmented SUT should satisfy:

\[
\boxed{
\mathbf P_P
\mathbf U^*
\mathbf P_I^\top
=
\mathbf U^{original}
}
\]

and:

\[
\boxed{
\mathbf P_P
\mathbf V^*
\mathbf P_I^\top
=
\mathbf V^{original}
}
\]

where the original matrix is the parent-classification Danish SUT.

Gross output should satisfy:

\[
\boxed{
\mathbf P_I\mathbf x^*=\mathbf x.
}
\]

---

# 3. Validation family 2: environmental closure

For a pure disaggregation of the official Danish environmental accounts:

\[
\boxed{
\mathbf P_I\mathbf F^*=\mathbf F.
}
\]

If this is not true, the project is no longer merely disaggregating the official extension and must explicitly identify the alternative data source and reason.

---

# 4. Validation family 3: child accounting identities

For every child industry \(k\):

\[
x_k
=
IC_k
+
VA_k
+
\text{other primary inputs}.
\]

Large residuals indicate either:

- inconsistent margins;
- price-basis mismatch;
- double counting;
- missing primary-input categories.

---

# 5. Validation family 4: import bridge

For every Danish import category \(j\):

\[
\boxed{
\sum_rK_{rj}=1.
}
\]

Also test:

- no negative shares unless methodologically intended;
- currency conversion applied exactly once;
- mapped imports equal original imports after aggregation;
- country totals reproduce observed bilateral trade totals where possible.

---

# 6. Validation family 5: numerical stability

Check that:

\[
\rho(\mathbf A)<1,
\]

where \(\rho\) is the spectral radius.

Also inspect:

- zero-output sectors;
- very small denominators;
- extreme Leontief multipliers;
- condition number of \((\mathbf I-\mathbf A)\);
- negative coefficients.

Any negative entries inherited from balancing or valuation adjustments must be understood before footprint calculations are interpreted.

---

# 7. Validation family 6: external statistical benchmarks

Compare aggregated model outputs with:

- public Statistics Denmark 117-industry IOT;
- national-account output and value-added totals;
- public Danish climate-footprint statistics where comparable;
- SHA expenditure totals;
- energy accounts;
- employment accounts;
- provider statistics.

No single external benchmark is sufficient because each has a different accounting boundary.

---

# 8. A crucial validation distinction: accounting closure versus footprint equality

A correctly disaggregated model does **not** have to reproduce the parent's detailed consumption footprint exactly if the children have genuinely different technologies.

The required test is that the accounting system reaggregates correctly.

Two explicit experiments should be performed.

## Test A. Proportional/artificial split

Give all child health sectors exactly the parent technology.

Then:

\[
f^{split,proportional}
\approx
f^{parent}.
\]

This is a software unit test.

## Test B. Empirically differentiated split

Give hospitals, GPs, dentists and other children their estimated production recipes.

Then:

\[
f^{augmented}
-
f^{parent}
\]

is interpreted as an estimate of the **aggregation effect**, subject to uncertainty.

It should not automatically be interpreted as an error.

---

# 9. Model comparison framework

Estimate at least four models.

\[
M_0=\text{original 117-industry model}
\]

\[
M_1=\text{proportional health split}
\]

\[
M_2=\text{Danish-data health split}
\]

\[
M_3=\text{Danish data + USEEIO priors}
\]

Then calculate:

\[
\Delta_{\text{aggregation}}
=
M_2-M_0
\]

and:

\[
\Delta_{\text{donor}}
=
M_3-M_2.
\]

This separates the value of Danish disaggregation from the influence of foreign donor assumptions.

---

# 10. Uncertainty taxonomy

Represent total model uncertainty as:

\[
U=
\{
U_{\text{accounts}},
U_{\text{health shares}},
U_{\text{recipe}},
U_{\text{mapping}},
U_{\text{trade}},
U_{\text{price}},
U_{\text{MRIO}},
U_{\text{extensions}},
U_{\text{capital}}
\}.
\]

| Uncertainty | Example |
|---|---|
| Accounts | revised national-account cells |
| Health shares | hospital vs GP output |
| Recipe | pharmaceutical input share |
| Donor transfer | applicability of USEEIO |
| Mapping | one donor sector maps to several Danish sectors |
| Trade | service origin or re-export allocation |
| Price | DKK/EUR and vintage adjustment |
| MRIO | EXIOBASE technical coefficients |
| Extension | environmental intensity |
| Capital | operational vs capital-inclusive accounting |

---

# 11. Monte Carlo framework

For simulation \(s\):

1. draw child-output shares;
2. draw uncertain production-recipe coefficients;
3. draw uncertain concordance weights;
4. reconcile the SUT;
5. reconstruct the IOT;
6. calculate \(\mathbf A_s\);
7. solve for domestic requirements;
8. draw import-origin uncertainty;
9. apply foreign multipliers;
10. calculate footprint.

Report:

\[
\tilde f,
\]

\[
P_5,
\]

and:

\[
P_{95}
\]

instead of only a single point estimate.

---

# 12. Data-quality-weighted uncertainty

The cell-quality flag introduced in the domestic model should control uncertainty distributions.

Example:

| Flag | Suggested uncertainty treatment |
|---|---|
| A | narrow distribution |
| B | low-to-medium |
| C | medium |
| D | relatively wide |
| E | wide |
| Z | fixed zero unless evidence changes |
| M | unresolved / scenario distribution |

The exact distributions should be empirically calibrated wherever possible rather than assigned arbitrary coefficients of variation.

---

# 13. Double-counting safeguards

For the first paper, design the disaggregation primarily as a **partition of existing national-account totals**.

If:

\[
\sum_kU_{pk}=U_{pH},
\]

the donor information redistributes an existing total rather than adding a second copy of the same expenditure.

This is a much safer starting point than adding a complete process-LCA inventory on top of an IO sector.

If PLCA processes are later introduced, explicitly use a hybrid double-counting correction framework.

Agez et al. show that an uncorrected IO complement can duplicate flows already represented in process inventories, and compare correction methods for this problem.

---

# 14. Structural-path analysis as a data-quality tool

Structural path analysis should not be used only for visualisation.

It can guide further data collection.

For each health child sector:

1. rank paths by contribution;
2. identify coefficients with weak data-quality flags;
3. calculate their contribution to total uncertainty;
4. prioritise Danish data collection for high-contribution, low-quality paths.

This creates a formal **value-of-information** strategy.

---

# 15. International scaling after Denmark is validated

Do not begin by disaggregating every EXIOBASE country.

Use Denmark as the high-data benchmark.

Then classify countries into data tiers.

| Tier | Available information | Suggested method |
|---|---|---|
| A | national detailed SUT + SHA + admin/provider data | national augmentation |
| B | national SUT/IOT + SHA + limited admin data | constrained donor augmentation |
| C | EXIOBASE + international SHA/WHO/OECD data | regional/donor priors with wide uncertainty |

For each country and parent health sector:

\[
\boxed{
\sum_k Z^{child}_{ik}
=
Z^{parent}_{iH}
}
\]

and, if environmental extensions are only being allocated:

\[
\boxed{
\sum_k F^{child}_{ek}
=
F^{parent}_{eH}.
}
\]

---

# 16. Hierarchical donor model

Do not use one US recipe for every country.

A general prior can be:

\[
\mathbf p_{ck}
=
\alpha_c
\mathbf p^{national}_{ck}
+
\beta_c
\mathbf p^{regional}_{k}
+
\gamma_c
\mathbf p^{USEEIO}_{k},
\]

with:

\[
\alpha_c+\beta_c+\gamma_c=1.
\]

For a high-data country:

\[
\alpha_c\rightarrow1.
\]

For a low-data country:

\[
\gamma_c
\]

may be larger, but the corresponding uncertainty should also increase.

---

# 17. Scenario analysis should be a later phase

The baseline model is attributional.

It assumes fixed coefficients unless explicitly modified.

If the future research question becomes:

> What happens if hospital care is structurally shifted toward home care?

then:

\[
\mathbf A
\rightarrow
\mathbf A_s
\]

and:

\[
\mathbf y
\rightarrow
\mathbf y_s.
\]

The model should then be explicitly presented as a scenario model rather than using the baseline Leontief system as a forecast.

Large structural transitions may additionally require:

- capacity constraints;
- technology change;
- price response;
- labour substitution;
- rebound effects;
- dynamic capital.

---

# 18. Recommended software stack

## Python

```text
pandas or polars
numpy
scipy
scipy.sparse
pymrio
cvxpy
pyarrow
pandera
pytest
SALib
```

### Purpose

- `pandas/polars`: data transformations;
- `numpy/scipy`: matrix algebra;
- `scipy.sparse`: large sparse SUT/MRIO matrices;
- `pymrio`: MRIO handling;
- `cvxpy`: constrained reconciliation;
- `pandera`: schema/data validation;
- `pytest`: automated accounting tests;
- `SALib`: sensitivity analysis.

## R

```text
useeior
Matrix
data.table
```

Use R primarily to extract/build USEEIO donor structures where necessary.

---

# 19. Recommended repository

```text
dk_health_eeio/
│
├── README.md
├── environment.yml
├── pyproject.toml
│
├── data/
│   ├── raw/
│   │   ├── dst_sut/
│   │   ├── dst_iot/
│   │   ├── dst_environment/
│   │   ├── dst_health_sha/
│   │   ├── health_admin/
│   │   ├── exiobase/
│   │   └── useeio/
│   │
│   ├── mappings/
│   │   ├── db07_isic4.csv
│   │   ├── db07_db25.csv
│   │   ├── sha_db07.csv
│   │   ├── useeio_db07.csv
│   │   ├── dk_exio.csv
│   │   └── country_exio.csv
│   │
│   └── processed/
│
├── src/
│   ├── sut/
│   │   ├── load_sut.py
│   │   ├── split_imports.py
│   │   ├── method_d.py
│   │   └── validate_sut.py
│   │
│   ├── health/
│   │   ├── classification.py
│   │   ├── output_margins.py
│   │   ├── recipe_priors.py
│   │   ├── useeio_priors.py
│   │   ├── reconcile.py
│   │   └── extensions.py
│   │
│   ├── io/
│   │   ├── coefficients.py
│   │   ├── leontief.py
│   │   └── footprint.py
│   │
│   ├── snac/
│   │   ├── trade_origin.py
│   │   ├── exio_bridge.py
│   │   ├── multipliers.py
│   │   └── coupled_footprint.py
│   │
│   └── uncertainty/
│       ├── distributions.py
│       └── monte_carlo.py
│
├── tests/
│   ├── test_supply_use_balance.py
│   ├── test_parent_closure.py
│   ├── test_method_d.py
│   ├── test_import_bridge.py
│   ├── test_proportional_split.py
│   └── test_environmental_closure.py
│
└── results/
```

---

# 20. Complete input-data inventory

| Data | Purpose | Priority |
|---|---|---:|
| Danish detailed supply matrix | health products/output | Essential |
| Danish detailed use matrix | health production recipes | Essential |
| Danish 117 IOT | public benchmark | Essential |
| Final demand | consumption footprint | Essential |
| Detailed imports/re-exports | domestic/import split | Essential |
| Bilateral goods trade | origin of imports | Essential |
| Services BOP | origin of service imports | Essential |
| Value-added accounts | balance children | Essential |
| Danish GHG accounts | environmental extensions | Essential |
| Household direct emissions | total footprint | Essential |
| SHA provider/function/financing | health allocation | Essential |
| Public/provider accounts | child-sector output and costs | Very high |
| DRG/patient-register data | hospital activity split | Very high |
| Pharmaceutical data | medical goods allocation | Very high |
| Household-budget information | private practitioners | High |
| Labour/FTE | health recipe and validation | High |
| Energy accounts | direct energy allocation | High |
| Provider procurement | differentiated recipes | Very high |
| USEEIO | donor recipe priors | Secondary |
| EXIOBASE | foreign supply-chain multipliers | Essential |
| EUR/DKK rate | currency harmonisation | Essential |
| Price indices | temporal harmonisation | Conditional |
| Capital-use data | capital-inclusive model | Phase II |
| Water/material/land accounts | multi-impact model | Phase II |

---

# 21. Data-acquisition order

Request or obtain in this order:

1. detailed Danish final SUTs for benchmark years;
2. product and industry classifications;
3. domestic/import split information;
4. official 117 × 117 IOTs;
5. SHA tables by provider/function/financing;
6. provider/public-account detail;
7. environmental accounts;
8. detailed bilateral trade;
9. Statistics Denmark's available Danish-to-EXIOBASE concordances, if shareable;
10. USEEIO donor data;
11. EXIOBASE.

This order prevents the research from investing heavily in foreign proxies before discovering that Danish source data already contain the required information.

---

# 22. Recommended publication programme

## Paper 1. Method

**A national-accounts-consistent framework for health-sector disaggregation in environmentally extended input-output models: the Danish case**

Focus:

- SUT augmentation;
- health classification;
- constrained reconciliation;
- donor priors;
- aggregation error;
- uncertainty.

## Paper 2. Application

**The environmental footprint of Danish healthcare: domestic and global supply-chain pressures**

Focus:

- GHG;
- energy;
- additional pressures where robust;
- domestic versus foreign footprint;
- providers and functions;
- capital sensitivity.

## Paper 3. International method

**Disaggregating healthcare in global MRIO systems: a hierarchical national-data and donor-technology framework**

Focus:

- EXIOBASE countries;
- SHA/OECD/WHO data;
- data tiers;
- hierarchical donor priors;
- uncertainty.

---

# 23. Recommended scientific positioning

Avoid describing the paper merely as:

> We disaggregated Danish healthcare using USEEIO.

A stronger methodological contribution is:

> A national-accounts-consistent method for disaggregating healthcare industries in supply-use and environmentally extended input-output systems using national health accounts, administrative health data and constrained reconciliation, with donor technology profiles used only for residual information gaps.

The methodological contribution then rests on four pillars:

\[
\boxed{\text{classification consistency}}
\]

\[
\boxed{\text{SUT accounting consistency}}
\]

\[
\boxed{\text{environmental-account consistency}}
\]

\[
\boxed{\text{international supply-chain completeness}}
\]

This is a more general and defensible industrial-ecology contribution.
