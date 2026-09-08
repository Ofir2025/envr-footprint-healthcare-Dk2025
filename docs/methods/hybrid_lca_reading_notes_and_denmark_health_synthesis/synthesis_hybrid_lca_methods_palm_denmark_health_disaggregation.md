# Synthesis and replication blueprint: hybrid LCA sector augmentation, Palm simplified-SNAC, and Danish healthcare disaggregation

## Scope and purpose

This document synthesises the three completely read methodological case studies:

1. Wiedmann et al. (2011), *Application of hybrid life cycle approaches to emerging energy technologies: the case of wind power in the UK*;
2. Malik, Lenzen and Geschke, *Triple bottom line study of a lignocellulosic biofuel industry* (manuscript period 2014; published 2016);
3. Malik et al. (2015), *Hybrid life-cycle assessment of algal biofuel production*.

It then connects their transferable methods to two additional sources requested for the research design:

- Palm et al. (2019), for the **national model + MRIO simplified-SNAC coupling**;
- Hagenaars et al. (2025), for the modern taxonomy and critique of **matrix augmentation (MA)**.

The final purpose is a replicable strategy for:

1. reproducing a Danish consumption-footprint model using Denmark's 117-industry IO/SUT system and EXIOBASE;
2. disaggregating Denmark's broad health and social-work sectors into more informative, ISIC-compatible child activities;
3. assessing whether detailed US USEEIO health-sector production recipes can be used as donor information;
4. deciding when SUT-based, IOT-based, matrix-augmentation, path-exchange or integrated-hybrid approaches are most viable.

---

# 1. Coverage ledger

| Source | Main-paper coverage | Supporting material | Status |
|---|---|---|---|
| Wiedmann et al. (2011) | pp. 1-8, sequentially, all main sections, Eq. 1-2, Fig. 1-2, Table 1, discussion, associated content, acknowledgements, references | Separate Supporting Information referenced but not supplied | **MAIN PAPER COMPLETE; SI NEEDS MANUAL CHECK** |
| Malik et al. (2014/2016) TBL biofuel | pp. 1-15, sequentially, all main sections, equations, Figs. 1-5, Tables 1-5, discussion, SI inventory | Appendices S1-S5 not supplied; Appendix S3 contains stepwise insertion procedure | **MAIN PAPER COMPLETE; SI NEEDS MANUAL CHECK** |
| Malik et al. (2015) algal biofuel | pp. 1-8, sequentially, all main sections, equations, Figs. 1-4, Table 1, conclusion, Appendix-A availability notice | Table S1 and supplementary process data not supplied | **MAIN PAPER COMPLETE; SUPPLEMENT NEEDS MANUAL CHECK** |
| Palm et al. (2019) | Previously read in full in this project; used here only for the requested method synthesis | Online supplement referenced in article but not supplied | **MAIN PAPER COMPLETE; SUPPLEMENT NEEDS MANUAL CHECK** |
| Hagenaars et al. (2025) | Previously read in full in this project; used here for taxonomy/critique | No underlying study dataset | **COMPLETE** |

**Important:** none of the three primary papers can be called “supplement-complete” because their online Supporting Information was not among the supplied files. Exact reproduction of some augmentation details therefore requires obtaining those supplements.

---

# 2. The common methodological problem

All three primary papers respond to the same structural weakness in conventional IO and process LCA, but at different points in the spectrum.

A process LCA offers technological specificity but can truncate upstream requirements. An IO model captures the entire represented economy but assumes homogeneous production within each sector.

Giljum et al. (2014) describe this IO trade-off clearly: economy-wide completeness reduces process truncation, but sectoral homogeneity can mix products and processes with very different environmental intensities.

The three papers therefore try to create:

$$
\boxed{
\text{specific foreground technology}
+
\text{complete IO background}
}
$$

while maintaining accounting consistency.

---

# 3. Cross-paper comparison

| Dimension | Wiedmann et al. (2011) | Malik et al. TBL | Malik et al. (2015) algal biofuel |
|---|---|---|---|
| Main problem | Make an existing electricity sector technology-specific | Add new forestry/refinery scenario sectors | Add a hypothetical algal bio-crude sector |
| IO system | UK-ROW SUT/IO hybrid | Australian subnational MRIO/SUT | Australian subnational MRIO/SUT |
| Foreground data | Ecoinvent 2 MW offshore wind process | Forestry, transport and NREL refinery data | Engineering costs, pilot data, HTL data |
| Augmentation type | Disaggregate existing electricity sector, then replace wind recipe | Add 38 scenario rows and columns | Add one bio-crude row and column |
| Initial split | Pro rata for 11 electricity subsectors | Not a simple parent split | New activity absent from IO |
| Production column | Process-informed wind inputs | Bottom-up process recipes + IO gap filling | Bottom-up bio-crude process column |
| Sales/output row | Wind product/output linked in SUT | Explicit scenario sales structure in augmented SUT | Crude-oil sales row used as analogue |
| Balancing principle | Remove/replace overlapping IO flows; maintain hybrid table structure | Rows/columns integrated into SUT MRIO | Total new sales scaled to equal total new inputs/output |
| Upstream completion | IO residual inputs or integrated $C_u$ | Leontief MRIO | Leontief MRIO |
| Double counting | Explicit concern; overlapping IO flows zeroed | Less explicit because sectors are inserted using constructed recipes | New activity inserted rather than overlaid on an existing identical sector |
| Price issue | Major sensitivity source | Monetary process conversion, but no full price-uncertainty study | Mixed data converted to 2013 AU$; constant-price assumption stated |
| Main outputs | GHG LCI | employment, stimulus, energy, GHG | employment, stimulus, energy, GHG |
| Key analytical decomposition | PXC/SPA discussion | Production-layer and commodity breakdown | Production-layer and commodity breakdown |
| Code reported | No public code; CMLCA mentioned | No paper-specific public code; IELab platform | No paper-specific public code; IELab platform |

---

# 4. The most transferable insight: what a disaggregated/new sector actually needs

The three papers together show that a scientifically meaningful child sector is not just a new label in an IO classification.

At minimum, a new or disaggregated sector requires:

$$
\boxed{
\text{scale}
+
\text{production recipe}
+
\text{sales/output structure}
+
\text{value added}
+
\text{direct environmental extensions}
}
$$

and all these must be reconciled with the accounting system.

## 4.1 Production recipe

For sector $k$, the input column is:

$$
\mathbf z_{\cdot k}
=
\begin{bmatrix}
z_{1k}\\
z_{2k}\\
\vdots\\
z_{nk}
\end{bmatrix}.
$$

The associated technical coefficients are:

$$
a_{ik}=\frac{z_{ik}}{x_k}.
$$

A real disaggregation must make at least some child vectors different:

$$
\mathbf a_{\text{hospital}}
\neq
\mathbf a_{\text{GP}}
\neq
\mathbf a_{\text{dentist}}.
$$

If every child simply receives the parent coefficient vector, the exercise changes reporting resolution but not technology.

Hagenaars et al. (2025, §4.1.2) explicitly identify this as a weakness of many matrix-augmentation studies: scaling new/disaggregated sectors to the original sector structure limits the benefit of MA.

## 4.2 Sales/output structure

Malik et al. demonstrate that a new input column alone is insufficient. The activity must also have an output/sales row.

For a symmetric IOT:

$$
\mathbf z_{k\cdot}
=
\begin{bmatrix}
z_{k1}&z_{k2}&\cdots&z_{kn}
\end{bmatrix}.
$$

For a SUT, this is represented more naturally through the supply matrix and product use/final demand.

## 4.3 Scale

The new child must have gross output $x_k$. In a partition of an existing parent $H$:

$$
\boxed{
\sum_{k\in H}x_k=x_H.
}
$$

This conservation identity is a major advantage of health-sector **disaggregation** compared with Malik's hypothetical new-sector insertion.

---

# 5. How the three papers handle balancing

“Balancing” refers to different operations in the three cases. These should not be conflated.

## 5.1 Wiedmann et al. (2011)

The UK study initially disaggregates electricity into eleven subsectors pro rata. The target wind sector is then made specific by replacing its original generic inputs with process-informed monetary inputs.

Where Ecoinvent already represents an input, the corresponding IO input is set to zero before the process value is inserted. Residual IO inputs not represented in the process inventory are retained.

The integrated hybrid model additionally connects the process and IO systems through:

$$
\mathbf H=
\begin{bmatrix}
-\mathbf A_{gp} & -\mathbf C_d\\
-\mathbf C_u & \mathbf I-\mathbf A_{ss}^*
\end{bmatrix}.
$$

The downstream link for wind electricity is inserted and the pre-existing wind sales coefficient is removed to prevent duplicate output representation.

**Transferable lesson:** balancing is not merely numerical row/column fitting. It also means ensuring that the same technological requirement or output is not represented twice.

## 5.2 Malik TBL study

The authors add 38 rows and 38 columns representing 19 feedstock and 19 refinery scenarios. Figure 3 explicitly distinguishes:

- vertical elements = production recipes;
- horizontal elements = sales structures;
- supply matrix = monetary output.

The exact stepwise insertion algorithm is delegated to Supporting Information Appendix S3, which is not supplied here.

**Transferable lesson:** build the new activity as a complete supply-use object, not as an isolated column.

## 5.3 Malik et al. (2015)

This paper gives the clearest balancing statement. The process recipe is inserted as a new bio-crude production column. The authors state that the inputs and outputs of an industry/commodity must be equal for the IO table to be balanced.

Because an observed bio-crude sales structure does not exist, they use **crude oil as an analogue** and scale its sales distribution to the total input/output of the new bio-crude activity.

Conceptually, if:

$$
\sum_i z_{i,b}=x_b
$$

and $s_j^{crude}$ are normalised crude-oil sales shares, then the inserted bio-crude sales vector is approximately:

$$
z_{b,j}=s_j^{crude}x_b.
$$

This equation is an explanatory reconstruction of the authors' procedure, not a printed equation in the paper.

---

# 6. Why the detailed Danish SUT is more useful than the 117 × 117 IOT

## 6.1 Current official Danish structure

Statistics Denmark documents that the final national-account supply-use system works with approximately:

$$
\boxed{2{,}350\ \text{products}\times117\ \text{industries}}
$$

whereas the published symmetric IOT is:

$$
\boxed{117\times117\ \text{industries}}.
$$

The **industry dimension is not more detailed in the final SUT**, but the **product dimension is dramatically more detailed**.

This is the important answer to “is the SUT more detailed than the IOT?”

> **Yes in product resolution and final-use information, not necessarily in the number of industries.**

Statistics Denmark balances supply and use for every one of roughly 2,350 products before constructing the symmetric IOT.

## 6.2 Why this matters for health-sector disaggregation

A broad health industry may purchase or produce multiple detailed health and non-health products. Those product relations are partially lost when the SUT is transformed to a symmetric industry-by-industry IOT.

The SUT allows us to distinguish:

$$
\mathbf V=\text{supply matrix}
$$

from:

$$
\mathbf U=\text{use matrix}.
$$

That provides stronger information for:

- which health products are actually produced;
- which products hospitals/practices consume;
- domestic versus imported product use;
- final consumption versus intermediate consumption;
- taxes, margins and valuation layers;
- product-specific balancing.

This is consistent with Wiedmann et al. (2011), who explicitly prefer a supply-use framework for hybridisation because it preserves commodity and industry detail.

## 6.3 Is the full detailed Danish SUT public through an API?

No.

Statistics Denmark states that only some SUT industry totals are currently published in StatBank. Detailed product-level supply-use relationships are not published because of confidentiality. Users can apply for access through Statistics Denmark's Research Service.

From the transmission covering 2022, Denmark also transmits SUTs to Eurostat voluntarily at **A88**, i.e. 88 products × 88 industries. This provides a useful public prototype, but it is not a substitute for the roughly 2,350-product internal SUT.

## 6.4 Public Danish IOT

The 117-industry IOT is publicly available in StatBank/downloads, including tables such as:

- `NAIO1` supply by industries and uses;
- `NAIO2` unallocated imports;
- `NAIO3` primary inputs;
- `NAIO4` totals.

---

# 7. Denmark's SUT-to-IOT transformation: Method D

Statistics Denmark produces its industry-by-industry IOT using **Method D**.

The assumption is:

> each product has a fixed sales structure, regardless of which industry produces it.

Suppose industries 1 and 2 produce 80% and 20% of a product. Method D assumes every user receives that product in the same 80/20 producing-industry proportions.

The product-to-industry transformation is based on a market-share matrix derived from the supply matrix.

This is important for the health project because a scientifically clean workflow is:

$$
\boxed{
\text{augment/disaggregate SUT}
\rightarrow
\text{rebalance SUT}
\rightarrow
\text{apply Method D}
\rightarrow
\text{calculate EEIO footprints}.
}
$$

Starting from the IOT is feasible, but it forfeits much of the product information that Method D already collapsed.

---

# 8. Palm et al. (2019): the method in plain language

Palm et al. address a different but complementary problem.

A global MRIO is internally balanced and traces international supply chains, but its Swedish block does not necessarily reproduce Statistics Sweden's official national accounts and environmental accounts exactly.

Palm therefore asks:

> Can we retain the superior official Swedish domestic data and still obtain complete foreign supply-chain impacts from EXIOBASE?

Their answer is a **linked hybrid MRIO-SRIO**, called **simplified SNAC** in the wider literature.

The core idea is:

```text
Official national IO model
        ↓
calculates domestic production requirements
        ↓
calculates how many imports those requirements induce
        ↓
map imports to EXIOBASE country-sector nodes
        ↓
apply EXIOBASE foreign environmental multipliers
        ↓
add domestic + imported + household components
```

Crucially, they **do not replace Sweden inside EXIOBASE and rebalance the full global table**.

---

# 9. Palm equations, step by step

Let:

- $A^d$ = domestic technical-coefficient matrix;
- $A^m$ = import coefficient matrix;
- $L^d=(I-A^d)^{-1}$ = domestic Leontief inverse;
- $y^d$ = domestic final demand for domestically produced goods/services;
- $y^m$ = direct imported final demand;
- $S^d$ = domestic environmental intensity;
- $Q$ = EXIOBASE total foreign environmental multiplier matrix after Leontief calculation;
- $Q^t$ = $Q$ transformed/concorded to national import categories;
- $f^h$ = direct household emissions.

## 9.1 Domestic component

$$
\boxed{
f^d=S^dL^dy^d+f^h.
}
$$

This traces Danish/Swedish domestic production chains using the official national model.

## 9.2 Imports induced by domestic production

The domestic economy needs imported intermediate inputs:

$$
\boxed{
m^d=A^mL^dy^d.
}
$$

## 9.3 Direct imported final demand

$$
\boxed{
m^m=y^m.
}
$$

## 9.4 Total imports associated with final demand

$$
\boxed{
m=m^d+m^m.
}
$$

## 9.5 EXIOBASE multipliers

For EXIOBASE:

$$
L^E=(I-A^E)^{-1},
$$

and:

$$
\boxed{Q=S^EL^E.}
$$

## 9.6 Imported environmental pressure

After currency, country and industry concordance:

$$
\boxed{
f^m=Q^tm.
}
$$

or expanded:

$$
\boxed{
f^m=Q^tA^mL^dy^d+Q^ty^m.
}
$$

## 9.7 Total footprint

$$
\boxed{
f^{d+m}
=
S^dL^dy^d
+
Q^tA^mL^dy^d
+
Q^ty^m
+
f^h.
}
$$

Each term has a clear meaning:

1. domestic upstream pressures;
2. foreign pressures from intermediate imports used by Danish production;
3. foreign pressures from goods/services imported directly for final use;
4. direct household pressures.

---

# 10. How balancing works in Palm: a point that is often misunderstood

Palm's simplified-SNAC method should **not** be described as a global rebalancing method.

There are three distinct balancing layers.

## 10.1 National SUT balancing

The national statistical institute has already reconciled its SUT so that product supply equals product use.

For Denmark:

$$
\text{supply}_p=\text{use}_p
\qquad\forall p.
$$

## 10.2 Full SNAC/MRIO rebalancing

A full SNAC would replace the national block inside an MRIO and then rebalance the global table around the fixed national information.

Palm does **not** do this.

## 10.3 Simplified SNAC

The national model remains separate. EXIOBASE is used as a foreign multiplier system for the imports calculated by the national model.

Therefore:

$$
\boxed{
\text{no full MRIO rebalance is required}.
}
$$

The cost is that “feedback” flows in which the focal country's exports travel through foreign supply chains and later re-enter as imports are not fully corrected.

Tukker et al. (2018) and Palm et al. regard this as an acceptable approximation for many smaller economies.

---

# 11. Denmark has already implemented a Palm-like coupled model

This is a major practical finding for the proposed research.

Statistics Denmark's 2022 technical report, *Compilation of a consumption based greenhouse gas account for Denmark using coupled models*, explicitly adopts **simplified SNAC**.

The report states that the method uses:

- the Danish national IO table and Danish emissions as the **official foreground**;
- EXIOBASE only to calculate emissions embodied in imports;
- no replacement of the Danish block inside EXIOBASE;
- no global rebalancing.

It cites a Danish feedback effect of about **0.4% of emissions**, which Statistics Denmark judged acceptable relative to other uncertainties.

This means the research should **not start by reinventing Palm for Denmark**.

The correct strategy is:

$$
\boxed{
\text{reproduce/extend Statistics Denmark's coupled model}
}
$$

and then insert the disaggregated health block into its domestic component.

---

# 12. Statistics Denmark's coupled-model equations

The technical report gives a particularly clear implementation for the 117-industry model.

## 12.1 Domestic technical coefficients

$$
A^d=Z\hat{x}^{-1}.
$$

## 12.2 Domestic Leontief inverse

$$
L^d=(I-A^d)^{-1}.
$$

## 12.3 Domestic GHG coefficient

$$
s^d=e\hat{x}^{-1},
$$

where $e$ contains emissions for the **117 Danish industries**.

## 12.4 Domestic footprint

$$
\boxed{
e^d=\hat{s}^dL^dy^d+e^h.}
$$

## 12.5 Intermediate imports

$$
\boxed{m^d=A^mL^dy^d.}
$$

## 12.6 Direct final imports

$$
\boxed{m^m=y^m.}
$$

## 12.7 Total imports

$$
\boxed{m=m^d+m^m.}
$$

## 12.8 EXIOBASE multiplier

The report's historical EXIOBASE version used 163 industries × 49 countries/regions = 7,987 region-industry nodes:

$$
\boxed{Q=\hat{S}L.}
$$

## 12.9 Imported emissions after concordance

$$
\boxed{e_m^{EXIO}=QKm.}
$$

This is already a Danish implementation of the core Palm logic.

---

# 13. The decisive part of the Danish implementation: matrix $K$

The domestic 117-sector import vector cannot be multiplied by EXIOBASE multipliers directly because the systems differ in:

- currency;
- units;
- country classification;
- industry classification.

Statistics Denmark therefore builds a mapping/distribution matrix $K$.

In the 2022 implementation:

$$
K\in\mathbb R^{7987\times117}.
$$

Each column corresponds to one Danish national-account industry; each row corresponds to an EXIOBASE country-industry node.

The crucial accounting condition is:

$$
\boxed{
\sum_rK_{rj}=1
\qquad\forall j.
}
$$

Thus $K$ redistributes a Danish import total but does not change that total.

---

# 14. How Statistics Denmark constructs the country and sector bridge

## 14.1 Detailed import-country information

The technical report describes a matrix $C$ of approximately:

$$
2{,}350\ \text{Danish products}\times239\ \text{countries},
$$

derived from still more detailed foreign-trade information (around 10,000 trade products) and balance-of-payments service information.

The product-country distribution is normalised:

$$
M_c=C[C\hat{i}]^{-1}.
$$

## 14.2 Product-to-industry market shares

Using the Danish supply matrix $V$:

$$
\boxed{D=V\hat{x}^{-1}.}
$$

Here $D$ is the product-industry market-share matrix.

For products not produced in Denmark, Statistics Denmark assigns a “characteristic industry”, i.e. the industry in which the product would most plausibly have been produced.

## 14.3 Country aggregation

A correspondence $B$ maps the detailed Danish country list to EXIOBASE countries/regions.

Conceptually:

$$
D_c=D'M_cB.
$$

## 14.4 Danish 117 → EXIOBASE 163 industries

The report initially tested uniform splitting when one Danish industry mapped to several EXIOBASE industries.

For example, one Danish agricultural industry could be spread uniformly across 17 EXIOBASE agricultural industries.

The authors then improved this by using **EXIOBASE's empirical composition of Danish imports by country-sector** to build an annually updated split.

This is directly relevant to the proposed health disaggregation: a uniform split is a useful control, but empirical donor shares are preferable.

---

# 15. A replicable Danish Palm workflow

Assume we have the 117-industry Danish IO model or, preferably, the detailed SUT from which it is constructed.

## Step 1: choose the benchmark year and price basis

Prefer a final SUT/IOT year for which domestic environmental data and EXIOBASE are compatible.

Never mix current-price Danish imports with multipliers whose monetary denominator represents an incompatible price year without adjustment.

Statistics Denmark's technical report explicitly encountered this inflation/vintage problem and used deflation when applying a 2019 EXIOBASE model to later Danish imports.

## Step 2: assemble the Danish domestic economic matrices

Required:

- $Z^d$: domestic intermediate transactions;
- $A^m$: imported intermediate coefficients;
- $y^d$: final demand for domestic output;
- $y^m$: direct imported final demand;
- $x$: gross output;
- value-added rows for validation.

If working from the SUT, reproduce Statistics Denmark's import split and Method D transformation before comparing with the official IOT.

## Step 3: reproduce the official Danish IOT first

This is a mandatory replication gate.

Do not disaggregate healthcare until the code reproduces the public 117-sector baseline within tolerance.

## Step 4: calculate the domestic Leontief system

$$
A^d=Z^d\hat{x}^{-1},
$$

$$
L^d=(I-A^d)^{-1}.
$$

For large/sparse systems, solve linear systems rather than repeatedly forming explicit inverses.

## Step 5: attach Danish environmental extensions

For GHG:

$$
s^d=e\hat{x}^{-1}.
$$

Then:

$$
e^d=\hat{s}^dL^dy^d+e^h.
$$

## Step 6: calculate imported requirements

$$
m^d=A^mL^dy^d,
$$

$$
m^m=y^m,
$$

$$
m=m^d+m^m.
$$

## Step 7: build/read EXIOBASE

Calculate or retrieve:

$$
Q=S^EL^E.
$$

## Step 8: build the concordance $K$

Map:

```text
Danish import category
→ detailed product
→ origin country
→ Danish characteristic/producing industry
→ EXIOBASE country
→ EXIOBASE industry
→ compatible currency/unit
```

Enforce:

$$
\sum_rK_{rj}=1.
$$

## Step 9: calculate imported pressures

$$
e_m^{EXIO}=QKm.
$$

## Step 10: optionally map EXIOBASE results back to Danish industries

Use an aggregation/splitting matrix $H$ for reporting compatibility.

The 2022 Statistics Denmark implementation notes that improving $H$ changes the industry distribution but not the total footprint.

## Step 11: sum the four components

1. Danish production emissions for domestic final demand;
2. foreign emissions embodied in intermediate imports;
3. foreign emissions embodied in direct final imports;
4. direct household emissions.

## Step 12: validate

Check:

- national output totals;
- final-demand totals;
- imports;
- domestic emissions;
- $K$-column sums;
- EXIOBASE unit/currency consistency;
- aggregate result against Statistics Denmark's published climate-footprint tables where comparable.

---

# 16. Swedish data in Palm and Danish equivalents

| Palm/Swedish requirement | Purpose | Danish equivalent / preferred source |
|---|---|---|
| Swedish SNA IO tables | Domestic production structure | Statistics Denmark 117-industry IOT (`NAIO1`-`NAIO4`) or detailed SUT through Research Service |
| Swedish SUT/industry/product concordance | Product/industry structure | Danish ~2,350-product × 117-industry SUT; public A88 transmission as fallback |
| Swedish SEEA air-emission accounts | Domestic environmental extensions | Statistics Denmark Green National Accounts / energy and emissions accounts |
| Household direct emissions | Fuel combustion by households | Danish energy/emission accounts consistent with residence principle |
| Bilateral merchandise trade | Origin of imported products | Statistics Denmark foreign trade statistics |
| International services trade | Origin of imported services | Danish balance-of-payments statistics |
| Consumption/final demand | Footprint demand vector | Danish national accounts, COICOP/COFOG/investment groups |
| Exchange-rate information | DKK/EUR compatibility | Official annual exchange-rate series, applied explicitly |
| EXIOBASE | Foreign supply chains | Current EXIOBASE release, version locked and documented |
| Water/land/material satellite data | Non-GHG footprints | Statistics Denmark environmental-economic accounts where sufficiently detailed; EXIOBASE only where national data are absent/less suitable |
| Health expenditure/provider information | Not part of Palm, but needed for this project | `SHA1`, health-insurance/LUNA-derived tables, regional/provider accounts, employment and other Danish health statistics |

---

# 17. Software and code: what Palm actually reports

## 17.1 Palm et al. (2019)

In the main article:

- programming language: **NOT REPORTED**;
- software package: **NOT REPORTED**;
- MATLAB/R/Python: **NOT REPORTED**;
- public source-code repository: **NOT REPORTED**.

The article points to supplementary data, but the supplied file set does not contain executable code.

Therefore the method must be reimplemented from the equations and concordance logic rather than by running an official Palm package.

## 17.2 Statistics Denmark's coupled-model report

The technical report provides equations, dimensions and construction logic but does not, in the inspected documentation, identify a public ready-to-run software package for reproducing the full model.

## 17.3 Recommended modern implementation

This is **our recommendation**, not a claim about Palm's original software.

### Python

- `pandas` or `polars`: classifications and data preparation;
- `numpy`: matrix/vector operations;
- `scipy.sparse`: sparse IO/MRIO matrices;
- `scipy.sparse.linalg`: linear solves;
- `pymrio`: EXIOBASE parsing and MRIO operations;
- `cvxpy`: constrained health-sector reconciliation;
- `pyarrow`: efficient storage;
- `pytest`: accounting closure tests.

### R

- `useeior`: extract/build USEEIO detailed US health recipes;
- `Matrix`: sparse operations;
- `data.table`: data handling.

---

# 18. Current USEEIO: what the repository actually provides

The current US EPA platform is **`useeior`**, an open-source **R package**.

The repository documentation states that it can:

- build USEEIO models;
- expose Make and Use matrices;
- generate $A$, $L$, domestic/import matrices and environmental extensions;
- validate and export model matrices;
- apply model customisations including **sector disaggregation** and hybridisation.

This is much more useful for the Danish project than merely reading a list of US sector names.

---

# 19. USEEIO's built-in disaggregation logic

`useeior` explicitly supports a disaggregation specification with:

- `OriginalSectorCode`;
- `OriginalSectorName`;
- `DisaggregationType`;
- `SectorFile`;
- optional `MakeFile`;
- optional `UseFile`;
- optional `EnvFile`.

A user-defined Make/Use disaggregation file specifies:

- industry code;
- commodity code;
- percentage allocation.

Thus the US EPA's current software architecture itself reinforces the same lesson learned from Wiedmann and Malik:

$$
\boxed{
\text{disaggregate Make/Supply}
+
\text{disaggregate Use}
+
\text{disaggregate environmental extensions}.
}
$$

This is a valuable implementation template for Denmark, even if the Danish model is ultimately coded independently in Python.

---

# 20. USEEIO healthcare detail

The current detailed USEEIO schema contains substantially more health/social-care detail than EXIOBASE's broad health sector and more detail than Denmark's four national-account Section-Q industries.

Relevant USEEIO sectors include:

| USEEIO/BEA code | Sector |
|---|---|
| 621100 | Offices of physicians |
| 621200 | Offices of dentists |
| 621300 | Offices of other health practitioners |
| 621400 | Outpatient care centers |
| 621500 | Medical and diagnostic laboratories |
| 621600 | Home health care services |
| 621900 | Other ambulatory health care services |
| 622000 | Hospitals |
| 623A00 | Nursing and community care facilities |
| 623B00 | Residential mental health, substance abuse, and other residential care facilities |
| 624100 | Individual and family services |
| 624400 | Child day care services |
| 624A00 | Community food, housing and other relief services, including rehabilitation services |

USEEIO also contains an EXIOBASE-to-USEEIO concordance in which EXIOBASE's broad “Health and social work services” category corresponds to multiple detailed USEEIO health/social-care sectors.

This makes USEEIO a plausible **donor technology library** for a disaggregation exercise.

---

# 21. But USEEIO is not an ISIC classification

USEEIO is based on US BEA/NAICS structures.

The desired Danish/EXIOBASE target should therefore be defined first in **ISIC Rev. 4 / DB07-compatible terms**, and USEEIO should be mapped into that target.

The core ISIC Rev. 4 Section Q structure is:

| ISIC Rev. 4 | Activity |
|---|---|
| 8610 | Hospital activities |
| 8620 | Medical and dental practice activities |
| 8690 | Other human health activities |
| 8710 | Residential nursing care facilities |
| 8720 | Residential care for mental health/substance-abuse-related conditions |
| 8730 | Residential care for the elderly and disabled |
| 8790 | Other residential care activities |
| 8810 | Social work without accommodation for the elderly and disabled |
| 8890 | Other social work without accommodation |

### Critical classification point

ISIC Rev. 4 class **8620** combines:

- general practitioners;
- medical specialists;
- dentists.

Therefore, if the research wants those as separate industries, the model must create **national analytical sub-classes beneath ISIC 8620**, rather than claiming that ISIC itself distinguishes them.

Denmark's DB07 already gives us such national detail.

---

# 22. Denmark already has more detailed DB07 healthcare categories beneath the 117-sector IO model

The national-account Section Q currently contains four broad 117-level industries:

- `860010` Hospital activities;
- `860020` Medical and dental practice activities;
- `870000` Residential care activities;
- `880000` Social work activities without accommodation.

Statistics Denmark's detailed DB07 classification distinguishes, among others:

| DB07 | Activity | ISIC parent |
|---|---|---|
| 861000 | Hospitals | 8610 |
| 862100 | General medical practitioners | 8620 |
| 862200 | Medical specialists | 8620 |
| 862300 | Dentists | 8620 |
| 869010 | Health care/home nursing/midwives etc. | 8690 |
| 869020 | Physiotherapists and occupational therapists | 8690 |
| 869030 | Psychological counselling | 8690 |
| 869040 | Chiropractors | 8690 |
| 869090 | Other health activities n.e.c. | 8690 |
| 871010 | Nursing homes | 8710 |
| 871020 | Other residential nursing care | 8710 |

Statistics Denmark documentation also notes that Section Q's four national-account industries cover around **30 detailed industries** at the most detailed Danish NACE level.

This changes the research strategy substantially:

> **Before importing a US classification, first exploit Denmark's own detailed activity classification and any underlying national-account/provider information available for those activities.**

---

# 23. Recommended target classification for the Danish pilot

A sensible first model is not to create every possible social-work code. It should create only children for which differentiated evidence can be assembled.

## 23.1 Core health model

| Analytical child | ISIC anchor | Danish evidence anchor |
|---|---|---|
| Hospitals | 8610 | 860010 / DB07 861000 |
| General practice | 8620 | DB07 862100 |
| Medical specialists | 8620 | DB07 862200 |
| Dental practice | 8620 | DB07 862300 |
| Home nursing/midwifery | 8690 | DB07 869010 |
| Physiotherapy/occupational therapy | 8690 | DB07 869020 |
| Psychological services | 8690 | DB07 869030 |
| Chiropractic | 8690 | DB07 869040 |
| Other human health | 8690 | DB07 869090 |

## 23.2 Extended care/social-work model

Add only if data quality is sufficient:

- residential nursing care, ISIC 8710;
- mental-health/substance residential care, ISIC 8720;
- elderly/disabled residential care, ISIC 8730;
- other residential care, ISIC 8790;
- social work for elderly/disabled without accommodation, ISIC 8810;
- other social work without accommodation, ISIC 8890.

The extended care boundary should be reported separately because the System of Health Accounts and ISIC Section Q do not define the health boundary identically.

---

# 24. Proposed USEEIO → ISIC donor bridge

This should be treated as an analytical concordance, not an official classification equivalence.

| USEEIO sector | Likely ISIC target | Mapping quality / issue |
|---|---|---|
| 621100 Offices of physicians | 8620 | Good for physician practices, but US sector combines GP/specialist components |
| 621200 Offices of dentists | 8620 | Strong donor for dental practice |
| 621300 Other health practitioners | 8690 | Good broad donor; may need sub-allocation |
| 621400 Outpatient care centers | 8620/8690 | One-to-many; inspect service composition before allocation |
| 621500 Medical/diagnostic laboratories | 8690 | Strong conceptual match; ISIC 8690 explicitly includes medical laboratories |
| 621600 Home health care services | 8690 | Strong for professional home health; do not confuse with purely social home help under 8810 |
| 621900 Other ambulatory health care | 8690 | Broad residual donor |
| 622000 Hospitals | 8610 | Strong conceptual match |
| 623A00 Nursing/community care facilities | 8710/8730 | One-to-many; US category too broad for direct transfer |
| 623B00 Residential mental health/substance/other | 8720/8790 | One-to-many |
| 624100 Individual/family services | 8810/8890 | One-to-many social-work category |
| 624400 Child day care | 8890 or outside health scope | Include only if research boundary requires it |
| 624A00 Community food/housing/relief/rehabilitation | 8890, partly outside core health | Broad; low-quality donor for health-specific analysis |

---

# 25. How to use US “recipes” scientifically

The US recipe should **not** be copied as an absolute Danish coefficient vector.

Let $A^{US}$ be the USEEIO direct-requirements matrix.

For a US donor health sector $u$, extract:

$$
a^{US}_{iu}.
$$

Map US suppliers $i$ into a harmonised supplier classification $g$ compatible with Denmark/EXIOBASE.

Then normalise the intermediate-input composition:

$$
\boxed{
p^{US}_{g,u}
=
\frac{a^{US}_{g,u}}
{\sum_g a^{US}_{g,u}}.
}
$$

If Danish child $k$ has estimated total intermediate consumption $IC_k^{DK}$, construct a donor prior:

$$
\boxed{
\widetilde z^{USprior}_{g,k}
=
p^{US}_{g,u}IC_k^{DK}.
}
$$

The US system therefore answers:

> “How might the child sector's intermediate spending be distributed across supplier groups?”

It does **not** determine:

- Danish gross output;
- Danish value added;
- Danish prices;
- Danish direct emissions;
- Danish final-demand allocation.

Those should come from Danish evidence where possible.

---

# 26. Why direct USEEIO copying is methodologically unsafe

Agez et al. (2022) provide a directly relevant warning. When US emission factors were used to fill missing environmental extensions elsewhere, the authors noted that this implicitly assumes that other countries have US technologies and regulations.

The same problem applies to healthcare production recipes.

Denmark and the US differ in:

- healthcare financing;
- public/private provision;
- labour costs;
- pharmaceutical pricing;
- insurance administration;
- outsourcing;
- capital intensity;
- procurement;
- energy technology.

Therefore:

$$
\boxed{
\text{USEEIO should be a prior, not the Danish truth.}
}
$$

---

# 27. A data hierarchy for each Danish health child

For every input cell, use the best evidence available.

Recommended order:

$$
\boxed{
\text{detailed Danish SUT}
>
\text{Danish provider/procurement accounts}
>
\text{Danish SHA/health-insurance data}
>
\text{physical activity drivers}
>
\text{European donor}
>
\text{USEEIO donor}
>
\text{parent proportional split}
}
$$

This should be applied **cell by cell**, not necessarily sector by sector.

For example:

- payroll can come from Danish employment/payroll information;
- pharmaceuticals from Danish health/provider expenditure;
- electricity from measured energy or floor area;
- laboratory services from activity/procurement data;
- residual business-service composition from USEEIO if no Danish evidence exists.

---

# 28. Danish health information that can support the split

## 28.1 System of Health Accounts: `SHA1`

Statistics Denmark publishes health expenditure by:

- function;
- provider;
- financing scheme.

It follows SHA2011.

This is highly useful for allocation but must not automatically be equated with IO gross output.

$$
\boxed{
\text{SHA expenditure}\neq\text{industry gross output in general}.
}
$$

Use SHA as:

- a scale prior;
- a provider/function allocation key;
- validation information.

## 28.2 Health Insurance Statistics

Statistics Denmark's health-insurance data are based primarily on the regions' **LUNA** settlement system and contain:

- contacts;
- fees/expenditure;
- provider/service types.

These are particularly valuable for separating:

- general practitioners;
- specialists;
- dentists;
- physiotherapists and other primary-care providers.

## 28.3 National-account employment

Employment/FTE and compensation information can help allocate labour/value-added components.

## 28.4 Hospital and regional information

Hospital activity, regional accounts, DRG/patient information, procurement, energy and floor-area data could differentiate hospital production technology beyond the existing 860010 aggregate.

---

# 29. Matrix augmentation for healthcare: the proposed algorithm

Let $H$ be a parent Danish health industry and $k=1,\ldots,K$ its child activities.

The recommended approach follows Hagenaars' **matrix augmentation** family but incorporates the accounting discipline demonstrated by Malik and Wiedmann.

## Stage 1: define child sectors

Create the classification crosswalk first:

```text
DB07
→ NACE Rev.2
→ ISIC Rev.4 parent
→ analytical child code
→ USEEIO donor code(s)
→ EXIOBASE reporting code
→ SHA provider/function where relevant
```

## Stage 2: determine child output margins

Estimate $x_k$ using Danish evidence.

Constrain:

$$
\boxed{
\sum_kx_k=x_H.
}
$$

## Stage 3: create input priors

For product/supplier $i$:

$$
\widetilde z_{ik}
=
\text{best available evidence}.
$$

## Stage 4: create sales/supply priors

For SUT work, split the parent supply column and relevant health products.

For direct IOT work, create child rows such that their destinations are consistent with observed final/intermediate use.

## Stage 5: split value added

For primary-input category $r$:

$$
\sum_kv_{rk}=v_{rH}.
$$

Use payroll/FTE/output information to differentiate labour-intensive and capital-intensive providers.

## Stage 6: split environmental extensions

For environmental flow $e$:

$$
\boxed{
\sum_kF_{ek}=F_{eH}
}
$$

if the exercise is a pure reallocation of the official environmental account.

Use physical drivers where possible rather than output shares.

## Stage 7: reconcile all priors to hard Danish totals

Estimate the final child flows rather than accepting any single proxy directly.

---

# 30. Recommended constrained reconciliation

Let $\widetilde z_{ik}$ be the prior child flows and $z^*_{ik}$ the reconciled solution.

A weighted least-squares problem is:

$$
\boxed{
\min_{z^*_{ik}\ge0}
\sum_{i,k}
\omega_{ik}
\left(z^*_{ik}-\widetilde z_{ik}\right)^2
}
$$

subject to parent conservation.

## 30.1 Input conservation

$$
\boxed{
\sum_kz^*_{ik}=z_{iH}
\qquad\forall i.
}
$$

## 30.2 Output/sales conservation

For a symmetric IOT:

$$
\boxed{
\sum_kz^*_{kj}=z_{Hj}
\qquad\forall j.
}
$$

## 30.3 Gross output

$$
\boxed{
\sum_kx_k=x_H.
}
$$

## 30.4 Value added

$$
\boxed{
\sum_kv_{rk}=v_{rH}
\qquad\forall r.
}
$$

## 30.5 Child column balance

$$
\boxed{
x_k=\sum_i z_{ik}+v_k+t_k.}
$$

The weights should reflect data quality:

$$
\omega_{ik}=\frac{1}{\sigma_{ik}^2}.
$$

Observed Danish cells get high weights; USEEIO priors receive lower weights.

---

# 31. Why weighted optimisation is preferable to one-step proportional allocation

A pure proportional split assumes:

$$
z_{ik}=w_kz_{iH}
\qquad\forall i.
$$

This forces identical technologies.

Weighted optimisation can instead combine:

- fixed/near-fixed observed cells;
- structural zeros;
- different allocation keys for different inputs;
- donor priors;
- hard parent margins;
- non-negativity.

Alternative methods include:

- RAS;
- GRAS if negative accounting entries must be retained;
- cross-entropy;
- maximum entropy.

Bruckner et al. provide a useful precedent for constrained reconstruction in IO/SUT model building.

---

# 32. Distinguish three different balancing tasks in our final research

This distinction should appear explicitly in the methods paper.

| Balancing task | What must balance? | Recommended approach |
|---|---|---|
| Original Danish SUT | Product supply = product use | Use Statistics Denmark's already reconciled SUT; do not rebalance arbitrarily |
| Health-sector augmentation | Children must aggregate exactly to parent margins and individually balance | Weighted constrained optimisation / SUT reconciliation |
| Denmark-EXIOBASE coupling | National imports must be distributed to EXIOBASE nodes without changing totals | Column-normalised $K$ concordance; **no global MRIO rebalance in simplified SNAC** |

This resolves a common conceptual confusion.

---

# 33. What happens if the detailed Danish SUT cannot be obtained?

The research remains possible, but the inferential status changes.

## Option A: detailed SUT + provider data

**Scientific strength:** highest.

Use the 2,350-product system and Danish health information to create child technologies before Method D.

## Option B: public A88 SUT + 117 IOT + provider data

**Scientific strength:** strong and publicly reproducible.

The A88 SUT preserves a product-industry framework but with much less product detail.

## Option C: 117 IOT + Danish health data + donor recipes

**Scientific strength:** moderate/strong if provider information is rich.

Construct both child columns and rows directly under parent-margin constraints.

## Option D: 117 IOT + USEEIO only

**Scientific strength:** exploratory.

This is a synthetic Danish disaggregation, not directly observed Danish child-sector technology.

## Option E: proportional parent split

**Scientific strength:** null/control model only.

It is useful to test the software but does not solve the aggregation problem criticised by Hagenaars.

---

# 34. Alternative methodological routes

## 34.1 Matrix augmentation at SUT level

**Best fit for the current research question.**

Advantages:

- aligns with Hagenaars MA;
- exploits detailed products;
- naturally handles rows and columns;
- permits exact parent conservation;
- easier than integrated PLCA-IO hybridisation.

Costs:

- detailed data access;
- substantial concordance work;
- balancing/optimisation;
- uncertainty documentation.

## 34.2 Matrix augmentation directly in the IOT

Advantages:

- simpler data access;
- easy to prototype;
- Malik-style sector insertion is straightforward.

Disadvantages:

- product information already lost;
- row/sales allocation harder to identify;
- greater reliance on donor assumptions.

## 34.3 Integrated hybrid LCA

Following Wiedmann, use detailed process inventories for hospitals/health technologies plus IO background.

Advantages:

- maximum process specificity;
- physical units can reduce some price dependence.

Disadvantages:

- very data intensive;
- complex process-IO concordance;
- double-counting correction;
- temporal-boundary mismatch;
- not necessary if the primary goal is **sectoral health disaggregation** rather than product/process LCA.

## 34.4 Path Exchange / structural-path targeted hybrid

Start with an EEIO health sector, identify high-impact paths, and replace only the dominant paths with better data.

Advantages:

- efficient data collection;
- avoids building a full integrated hybrid database;
- useful after the first health footprint exists.

This could be an excellent **phase 2** method.

## 34.5 Global EXIOBASE health disaggregation immediately

Possible, but not recommended as the first step.

Every country would require assumptions about:

- child output shares;
- input recipes;
- environmental extensions;
- price structure;
- health-system institutions.

A Denmark proof of concept should be validated first.

---

# 35. Relative cost and methodological implications

| Approach | Data burden | Coding burden | Main uncertainty | Reproducibility | Recommendation |
|---|---:|---:|---|---|---|
| Detailed Danish SUT MA | High | Medium-high | child recipe/output evidence | Restricted-data issue | **Preferred scientific benchmark** |
| A88 SUT MA | Medium | Medium | aggregation | High/public | **Preferred open benchmark** |
| 117 IOT MA + Danish provider data | Medium | Medium | row allocation and aggregation | High | **Strong fallback** |
| 117 IOT + USEEIO donor | Low-medium | Medium | cross-country technology transfer | High | **Sensitivity/exploratory** |
| Parent proportional split | Low | Low | identical child technologies | Very high | **Null model only** |
| Integrated hybrid PLCA-IO | Very high | Very high | price, concordance, overlap, temporal boundary | Variable | Use only for selected processes |
| PXC/SPA targeted replacement | Medium | Medium-high | selection/replacement data | Good | **Good phase-2 improvement** |
| All-country EXIOBASE health split | Very high | Very high | donor assumptions in low-data countries | Good if open | Do after Danish validation |

---

# 36. Proposed research model family

A rigorous study should estimate several nested models.

## Baseline

$$
M_0=\text{official Danish 117-industry model}.
$$

## Null disaggregation

$$
M_1=\text{proportional parent-recipe health split}.
$$

## Danish-evidence model

$$
M_2=\text{Danish child output + Danish input drivers}.
$$

## Donor-completed model

$$
M_3=\text{Danish evidence + USEEIO/European residual priors}.
$$

## Detailed-SUT model, if access is obtained

$$
M_4=\text{full Danish SUT augmentation}.
$$

Key comparisons:

$$
\Delta_{technology}=M_2-M_1,
$$

$$
\Delta_{donor}=M_3-M_2,
$$

$$
\Delta_{SUT}=M_4-M_3.
$$

These comparisons quantify exactly what additional information contributes.

---

# 37. Validation requirements

## 37.1 Reaggregation closure

The augmented system must return the parent economy when the children are aggregated.

For all parent input categories:

$$
\sum_kz_{ik}=z_{iH}.
$$

For all parent output destinations:

$$
\sum_kz_{kj}=z_{Hj}.
$$

## 37.2 Environmental closure

If only reallocating official direct emissions:

$$
\sum_kF_{ek}=F_{eH}.
$$

## 37.3 Proportional-split unit test

If every child has exactly the parent technology, the aggregated footprint should reproduce the original baseline within numerical tolerance.

## 37.4 Numerical stability

Check:

$$
\rho(A)<1
$$

and inspect condition numbers, zero-output children and extreme coefficients.

## 37.5 External validation

Compare with:

- official Danish output/value-added/employment;
- `SHA1` provider totals where boundaries match;
- health-insurance expenditures;
- public Statistics Denmark climate-footprint results at an aggregated level;
- provider energy/procurement information where available.

---

# 38. Uncertainty analysis

Wiedmann et al. demonstrate that hybrid results can be highly sensitive to prices. Hagenaars similarly highlights price dependency, double counting and aggregation as recurrent hybrid-LCA problems.

The health project should separate uncertainty into:

$$
U=
\{
U_x,
U_{recipe},
U_{sales},
U_{mapping},
U_{price},
U_{environment},
U_{trade},
U_{MRIO}
\}.
$$

For Monte Carlo draw $s$:

1. draw uncertain child output shares;
2. draw uncertain donor recipe shares;
3. draw uncertain concordance allocations;
4. rebalance to hard Danish parent margins;
5. calculate $A_s$, $L_s$ and footprint;
6. calculate imported component through $K_s$/EXIOBASE if mapping uncertainty is included.

The key methodological rule is:

> **Every uncertainty draw should still satisfy the accounting constraints.**

---

# 39. Data-quality tagging

Every estimated child input should carry a provenance grade.

| Grade | Evidence |
|---|---|
| A | Direct Danish observation |
| B | Strong Danish provider/administrative estimate |
| C | Danish statistical allocation key (SHA, LUNA, employment etc.) |
| D | European donor prior |
| E | USEEIO donor prior |
| F | Parent proportional allocation |

Report, for every child sector, the share of intermediate consumption determined by A-F evidence.

This would make the model much more transparent than conventional matrix augmentation.

---

# 40. Proposed computational workflow

```text
01_download_public_dk_io.py
02_load_or_import_dk_sut.py
03_reproduce_method_D.py
04_validate_117_baseline.py
05_build_health_classification.py
06_load_sha_luna_provider_data.py
07_build_child_output_margins.py
08_build_danish_recipe_priors.py
09_extract_useeio_recipes.R
10_map_useeio_to_isic_exio.py
11_reconcile_health_sut.py
12_build_augmented_iot.py
13_split_environmental_extensions.py
14_validate_reaggregation.py
15_calculate_domestic_health_footprints.py
16_build_palm_import_vector.py
17_build_K_concordance.py
18_apply_exiobase_multipliers.py
19_uncertainty_monte_carlo.py
20_structural_path_hotspots.py
```

---

# 41. Practical USEEIO extraction workflow

The current `useeior` documentation supports building a detailed model in R.

Illustrative workflow:

```r
library(useeior)

# Inspect available EPA model specifications
seeAvailableModels()

# Build a detailed model supported by the installed release
model <- buildModel("USEEIOv2.0.1-411")

# Economic matrices of interest
U <- model$U
V <- model$V
A <- model$A
x <- model$x
q <- model$q
```

The exact supported model version should be pinned to a release at the time of analysis rather than relying on a development branch.

For the health donor recipe, select columns corresponding to the detailed USEEIO healthcare codes, map their supplier rows to the harmonised supplier classification, and normalise their intermediate-input composition.

### Important

Do not use the US direct environmental extension $B$ as the Danish child extension unless explicitly testing a US-technology scenario.

---

# 42. Proposed Danish data request

If applying for detailed SUT access, request explicitly:

1. supply matrix $V$, ~2,350 products × 117 industries;
2. use table at basic prices;
3. domestic-use table;
4. import-use table;
5. product classification and descriptions;
6. value-added rows;
7. detailed final-demand categories;
8. margins and taxes/subsidies if required for valuation conversion;
9. market-share / characteristic-industry information used for Method D if shareable;
10. metadata and confidentiality conditions for publishing derived health tables.

Preferred benchmark years should be chosen based on overlap among:

- final Danish SUT;
- Danish health data;
- environmental accounts;
- EXIOBASE.

---

# 43. What the three primary papers teach us about missing data

The papers do **not** say “stop whenever one dataset is missing”.

They demonstrate a hierarchy of transparent approximation.

### Wiedmann

When actual UK wind company data were unavailable, use a documented Ecoinvent technology surrogate and state the representativeness limitation.

### Malik TBL

When bottom-up process data omit categories, fill residual categories from analogous IO sectors.

### Malik algal biofuel

When a sales row does not exist, use a plausible analogue, crude oil, and scale it transparently to the new sector's output.

The general rule is:

$$
\boxed{
\text{use the strongest evidence available}
+
\text{make analogues explicit}
+
\text{preserve accounting totals}
+
\text{test sensitivity}.
}
$$

---

# 44. But there is a point at which disaggregation should stop

If there is no independent information distinguishing two proposed children, creating two technology vectors is not empirically identified.

For parent $H$ split into $K$ children:

$$
\sum_kz_{ik}=z_{iH}
$$

provides only one equation for $K$ unknown child flows for each supplier $i$.

Without priors or additional constraints, there are infinitely many valid allocations.

Therefore:

> **resolution should follow evidence, not merely the availability of classification codes.**

If GP and specialist technologies cannot be differentiated reliably, retain a combined medical-practice sector rather than inventing precision.

---

# 45. Recommended methodological contribution

The strongest research contribution is not:

> “We copied US health sectors into EXIOBASE.”

A stronger and more defensible contribution is:

> **A national-accounts-consistent, data-tiered matrix-augmentation framework for disaggregating healthcare and social-care activities in national and multiregional input-output systems, using national SUT/health data as primary evidence and donor technology profiles only for residual information gaps.**

This directly addresses Hagenaars' criticism of simple parent-sector scaling while retaining Palm's concern for national statistical consistency.

---

# 46. Suggested research phases

## Phase 1: reproduce Denmark's official baseline

- load 117-industry IOT;
- reconstruct Leontief model;
- reproduce domestic footprint;
- reproduce simplified-SNAC import coupling.

## Phase 2: public-data health disaggregation

- A88 SUT where available;
- DB07/ISIC classification;
- SHA and LUNA information;
- USEEIO residual priors;
- constrained reconciliation.

## Phase 3: detailed-SUT benchmark

If Research Service access is obtained:

- rebuild with ~2,350-product SUT;
- quantify information gain over A88/IOT version.

## Phase 4: targeted primary-data improvement

Use SPA/PXC-style hotspot analysis to identify the most important uncertain provider inputs.

## Phase 5: EXIOBASE international transfer

Create country tiers:

- Tier A: national SUT + health accounts;
- Tier B: national IO + health accounts + donor recipes;
- Tier C: EXIOBASE margins + regional/USEEIO donor priors with wider uncertainty.

---

# 47. Understanding questions for the synthesis

A researcher who understands the combined methods should be able to answer the following.

1. Why is a production column alone insufficient to insert a new sector?
2. Why is a proportional parent-sector split an initialisation or null model rather than a substantive disaggregation?
3. What is the difference between balancing the Danish SUT and rebalancing a global MRIO?
4. Why does simplified SNAC not require full EXIOBASE rebalancing?
5. What exactly does the matrix $K$ do in the Danish coupled model?
6. Why can USEEIO be useful as a donor without being treated as Danish technology?
7. Why should US supplier coefficients be normalised and rescaled to Danish child intermediate consumption?
8. Why does ISIC 8620 not by itself give separate GP, specialist and dentist sectors?
9. Why is the detailed Danish SUT more informative even though it still has 117 industries?
10. What is gained by performing the health split before Method D?
11. What does $C_u$ mean in integrated hybrid LCA and what problem does it solve?
12. What does a production-layer decomposition tell us that a total footprint does not?
13. How should uncertainty be propagated without violating national-account totals?
14. When should the analyst stop disaggregating and retain a broader child sector?
15. Why should Denmark be validated before attempting a global EXIOBASE healthcare split?

---

# 48. Main conclusions

## Conclusion 1

The three case studies strongly support **matrix augmentation** as a practical way to introduce technology detail, but they also show that a complete child/new sector needs a production recipe, output structure, scale and satellite information.

## Conclusion 2

For Denmark, **SUT-first augmentation is methodologically preferable** to direct manipulation of the 117 × 117 IOT whenever the detailed SUT can be accessed.

## Conclusion 3

The Danish SUT is much more detailed than the IOT in its **product dimension**: approximately 2,350 products × 117 industries versus 117 × 117 industries.

## Conclusion 4

The full detailed product-level SUT is **not publicly available through StatBank/API**. Research access is possible through Statistics Denmark; A88 Eurostat SUTs provide a public fallback.

## Conclusion 5

Palm's method is **not a global rebalancing approach**. It keeps the national model intact and uses EXIOBASE to supply foreign import multipliers.

## Conclusion 6

Statistics Denmark has already implemented a Palm-like simplified-SNAC model. This should be the starting point for the Danish replication.

## Conclusion 7

USEEIO is useful because it has detailed healthcare Make/Use structure and a current open-source `useeior` R implementation that explicitly supports disaggregation. But USEEIO recipes should be treated as **donor priors**, not copied as Danish coefficients.

## Conclusion 8

ISIC Rev. 4 should be the international backbone, while DB07 can supply Danish analytical sub-classes beneath broad ISIC classes such as 8620 and 8690.

## Conclusion 9

The recommended health model is a **constrained partition of existing Danish parent sectors**, which is more tightly identifiable than Malik's insertion of entirely new hypothetical industries because parent totals provide hard margins.

## Conclusion 10

The strongest methodological paper will quantify the difference among proportional splitting, Danish-evidence splitting, donor-completed splitting and detailed-SUT splitting, rather than presenting one synthetic model as uniquely true.

---

# 49. References

Agez, M., Majeau-Bettez, G., Margni, M., Strømman, A. H., & Samson, R. (2020). Lifting the veil on the correction of double counting incidents in hybrid life cycle assessment. *Journal of Industrial Ecology, 24*, 517-533. https://doi.org/10.1111/jiec.12945

Agez, M., Muller, E., Patouillard, L., Södersten, C.-J. H., Arvesen, A., Margni, M., Samson, R., & Majeau-Bettez, G. (2022). Correcting remaining truncations in hybrid life cycle assessment database compilation. *Journal of Industrial Ecology, 26*, 121-133. https://doi.org/10.1111/jiec.13132

Bruckner, M., Wood, R., Moran, D., Kuschnig, N., Wieland, H., Maus, V., & Börner, J. (2019). FABIO: The construction of the food and agriculture biomass input-output model. *Environmental Science & Technology, 53*, 11302-11312. https://doi.org/10.1021/acs.est.9b03554

Giljum, S., Bruckner, M., & Martinez, A. (2014). Material footprint assessment in a global input-output framework. *Journal of Industrial Ecology, 19*, 792-804.

Hagenaars, R. H., Heijungs, R., Tukker, A., & Wang, R. (2025). Hybrid LCA for sustainable transitions: Principles, applications, and prospects. *Renewable and Sustainable Energy Reviews, 212*, 115443. https://doi.org/10.1016/j.rser.2025.115443

Jensen, P. R., & Iliev, B. (2022). *Compilation of a consumption based greenhouse gas account for Denmark using coupled models*. Statistics Denmark, technical report for Eurostat.

Malik, A., Lenzen, M., & Geschke, A. (2016). Triple bottom line study of a lignocellulosic biofuel industry. *GCB Bioenergy, 8*, 96-110. https://doi.org/10.1111/gcbb.12240

Malik, A., Lenzen, M., Ralph, P. J., & Tamburic, B. (2015). Hybrid life-cycle assessment of algal biofuel production. *Bioresource Technology, 184*, 436-443. https://doi.org/10.1016/j.biortech.2014.10.132

Palm, V., Wood, R., Berglund, M., Dawkins, E., Finnveden, G., Schmidt, S., & Steinbach, N. (2019). Environmental pressures from Swedish consumption: A hybrid multi-regional input-output approach. *Journal of Cleaner Production, 228*, 634-644. https://doi.org/10.1016/j.jclepro.2019.04.181

Tukker, A., Giljum, S., & Wood, R. (2018). Recent progress in assessment of resource efficiency and environmental impacts embodied in trade. *Journal of Industrial Ecology, 22*, 489-501. https://doi.org/10.1111/jiec.12736

Wiedmann, T. (2009). A review of recent multi-region input-output models used for consumption-based emission and resource accounting. *Ecological Economics, 69*, 211-222.

Wiedmann, T. O., Suh, S., Feng, K., Lenzen, M., Acquaye, A., Scott, K., & Barrett, J. R. (2011). Application of hybrid life cycle approaches to emerging energy technologies: The case of wind power in the UK. *Environmental Science & Technology, 45*, 5900-5907. https://doi.org/10.1021/es2007287

Wiebe, K. S., Bjelle, E. L., Többen, J., & Wood, R. (2018). Implementing exogenous scenarios in a global MRIO model for the estimation of future environmental footprints. *Journal of Economic Structures, 7*, 20. https://doi.org/10.1186/s40008-018-0118-y

---

# 50. Official and software sources checked for this synthesis

## Statistics Denmark

- National Accounts: Input-Output and Supply-Use, current statistical documentation.
- Public 117-industry IO downloads and StatBank tables `NAIO1`-`NAIO4`.
- Research Service information for detailed SUT access.
- `SHA1` health expenditure.
- Health Insurance Statistics based on regional LUNA reimbursement information.
- *Compilation of a consumption based greenhouse gas account for Denmark using coupled models* (2022).

## United Nations Statistics Division

- ISIC Rev. 4 Section Q and classes 8610, 8620, 8690, 8710, 8720, 8730, 8790, 8810 and 8890.

## US EPA GitHub

- `USEPA/USEEIO`.
- `USEPA/useeior`.
- `useeior` model component specification.
- `useeior` model customisation/disaggregation specification.
- detailed healthcare sector crosswalk and metadata files.

---

# 51. Evidence-boundary note

The three primary papers were read completely in their supplied main-PDF form. Their online Supporting Information was not supplied and remains:

`UNREADABLE / NEEDS MANUAL CHECK`

for exact reproduction of some process-input and insertion details.

Palm and Hagenaars are included because they were explicitly requested for the synthesis and had already been read completely in the project workflow. Current official Statistics Denmark, UNSD and USEPA material was used to verify the Danish implementation, classification and software/data-access questions.
