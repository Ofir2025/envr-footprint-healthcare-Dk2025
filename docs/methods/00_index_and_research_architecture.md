# Danish health-sector augmented EEIO research blueprint

## Document purpose

This document is the entry point to a multi-part research blueprint for constructing a detailed, national-accounts-consistent environmentally extended input-output (EEIO) model of the Danish health sector and subsequently coupling it to a global multi-regional input-output (MRIO) model.

The methodological objective is not merely to “split the health sector”. The research should preserve the accounting identities and official totals of the Danish national accounts while introducing additional health-sector detail that is scientifically justified by Danish data wherever possible.

The proposed research contains **two distinct hybridisations**:

1. **Domestic sector disaggregation / matrix augmentation** inside the Danish supply-use system.
2. **International coupling** of the national Danish model to EXIOBASE using a simplified single-country national accounts consistent (simplified-SNAC) architecture.

These two operations should be implemented and validated separately.

---

# 1. Core research architecture

The recommended sequence is:

```text
Detailed Danish SUT
        ↓
ISIC/DB-compatible health-sector augmentation
        ↓
Balanced augmented Danish SUT
        ↓
Official-style SUT-to-IOT transformation
        ↓
Nationally consistent augmented Danish EEIO model
        ↓
Simplified-SNAC coupling
        ↓
EXIOBASE foreign supply-chain multipliers
        ↓
Danish healthcare provider and consumption footprints
```

The augmented national model will contain more than the original 117 industries, but it should be designed so that it can be **exactly reaggregated to the official 117-industry national-account system**.

---

# 2. Recommended research questions

## RQ1. Health-sector disaggregation

Can heterogeneous Danish health activities be disaggregated into policy-relevant ISIC-compatible activities without disturbing the accounting totals of the official Danish supply-use and input-output system?

## RQ2. Environmental footprint

How large are the domestic and international environmental footprints of distinct Danish health services, and which domestic and foreign supply chains cause them?

## RQ3. Aggregation error

How much does the conventional aggregated representation of healthcare distort environmental footprints relative to a more detailed health-sector representation?

## RQ4. Transferability

Can the Danish method be converted into a general framework for disaggregating health sectors in EXIOBASE countries with different degrees of data availability?

---

# 3. A critical conceptual distinction: industry, provider and function

The project must distinguish three classification perspectives.

| Perspective | Example | Typical classification |
|---|---|---|
| Economic activity | hospital, GP, dentist | DB07 / NACE / ISIC |
| Healthcare provider | hospital provider, ambulatory provider | SHA-HP |
| Healthcare function | inpatient care, outpatient care, laboratory service | SHA-HC |

These should not be merged into one undifferentiated IO classification.

The recommended rule is:

\[
\boxed{\text{IO industries}=\text{DB07/NACE/ISIC economic activities}}
\]

while:

\[
\boxed{\text{health-expenditure reporting}=\text{SHA functions/providers}}
\]

This permits two different analytical outputs:

1. **Provider/industry footprints**, such as the footprint of hospitals or dentists.
2. **Functional expenditure footprints**, such as inpatient care, outpatient care, preventive care or pharmaceuticals.

---

# 4. Should the project use the detailed Danish SUTs?

## 4.1 Recommendation

**Yes. The detailed Danish supply-use tables (SUTs) should be the preferred starting point if access can be obtained.**

The Danish national accounts are compiled using approximately:

- **2,350 products**, and
- **117 industries**,

for the final detailed supply-use system.

The detailed SUT is much more informative than the published 117 × 117 symmetric IOT because the SUT preserves the product dimension before products are transformed into supplying industries.

This is particularly valuable for health-sector disaggregation.

## 4.2 Why the detailed SUT is superior to starting from the 117 × 117 IOT

### Reason 1. It reveals health-related products hidden inside broad industries

The symmetric IOT has already collapsed the product dimension into industry-to-industry transactions.

The SUT may reveal products such as specific health services, pharmaceuticals, medical services, laboratory-related outputs or other product groups that are obscured in the final IOT.

Before borrowing a US production recipe, the project should first determine how much relevant detail already exists in the Danish product accounts.

### Reason 2. Disaggregation can be performed before the symmetric transformation

A sector split is much more defensible when performed on:

\[
\mathbf V=\text{supply matrix}
\]

and:

\[
\mathbf U=\text{use matrix}
\]

than when performed directly on a symmetric \(\mathbf Z\) matrix.

The SUT explicitly distinguishes:

- which products industries produce;
- which products industries consume;
- final uses of products;
- imports;
- value-added components.

This allows both the **rows and columns** associated with newly created health activities to be treated coherently.

### Reason 3. Product-level accounting constraints can be preserved

For each product \(p\):

\[
q_p + m_p
=
\sum_j U_{pj}
+
\sum_f Y_{pf}.
\]

That means:

\[
\boxed{\text{supply}_p=\text{use}_p}
\]

can be maintained during the disaggregation.

This gives much stronger validation than splitting an IOT column and checking only total industry output.

### Reason 4. It reduces dependence on USEEIO donor information

If Danish product and provider data already distinguish some health inputs, those data should dominate.

USEEIO should be used only for **residual information gaps** rather than becoming the technological foundation of the Danish health model.

### Reason 5. It supports a cleaner domestic/import separation

The coupled Palm/Statistics Denmark model needs imported intermediate and final-use requirements.

The SUT framework is the natural place to separate:

\[
\mathbf U=\mathbf U^d+\mathbf U^m
\]

and:

\[
\mathbf Y=\mathbf Y^d+\mathbf Y^m.
\]

### Reason 6. It preserves official national-account consistency

The augmented health system can be constrained so that reaggregation yields the original national-account totals.

For example:

\[
\sum_{k\in H}U^*_{pk}=U_{pH},
\]

where \(H\) is the original health parent sector and \(k\) denotes its newly created child sectors.

### Reason 7. It allows the official SUT-to-IOT method to be replicated

Statistics Denmark constructs its industry-by-industry IOT from the SUT using the fixed-product-sales-structure assumption, often referred to as **Model/Method D**.

Therefore the scientifically clean order is:

\[
\text{augment SUT}\rightarrow\text{rebalance SUT}\rightarrow\text{apply Method D}\rightarrow\text{EEIO analysis}.
\]

---

# 5. Are the approximately 2,350-product Danish SUTs publicly accessible through an API?

## 5.1 Short answer

**No, not in their full detailed product-by-industry form.**

Statistics Denmark's StatBank API provides programmatic access to **all data that are published in StatBank**, but Statistics Denmark explicitly states that the detailed product-level relationships in the approximately 2,350-product SUT are **not publicly published because of confidentiality**.

Therefore:

\[
\boxed{
\text{StatBank API access}
\neq
\text{access to the full 2,350-product SUT}
}
\]

## 5.2 What is publicly available from Statistics Denmark?

The following are publicly available:

- the 117-industry input-output tables;
- associated input-output tables for supply, imports, primary inputs and totals;
- multiplier tables;
- national-account industry totals;
- other published national-account statistics.

These can be accessed through the **StatBank interface or StatBank API**.

For example, the public input-output system includes the NAIO family of tables.

## 5.3 What is not publicly available?

Statistics Denmark states that only some totals from the Danish SUT are published at industry level and that:

> the detailed relationships between supply and use at product level are not published due to confidentiality.

Researchers requiring the most detailed SUT can apply for access through **Statistics Denmark's Research Service**.

This should therefore be treated as an explicit institutional-access task at the start of the project.

## 5.4 What can be obtained publicly from Eurostat?

Eurostat publishes harmonised national SUTs and IOTs through its dissemination system and API.

However, these are much more aggregated than the Danish compilation system:

- standard mandatory SUT transmission: approximately **64 products × 64 industries**;
- voluntary more detailed transmission: up to approximately **88 products × 88 industries**.

These public Eurostat tables are extremely useful for:

- method development;
- testing scripts;
- international comparability;
- prototyping the SUT-to-IOT workflow.

They are **not a substitute for the approximately 2,350-product Danish working SUT** if the objective is high-resolution health-sector disaggregation.

---

# 6. Recommended access strategy

Use a three-level data strategy.

## Level A. Preferred research dataset

Request through Statistics Denmark Research Service:

- detailed final SUT for 2019;
- detailed final SUT for 2022;
- associated product classifications;
- domestic/import information where available;
- metadata needed to reproduce Method D;
- any permissible concordance files.

## Level B. Public national benchmark

Use the public 117-industry Danish IOT and national-account tables from StatBank/API for:

- replication;
- closure tests;
- benchmarking;
- public reproducibility.

## Level C. Public SUT prototype

Use Eurostat 64/88-product SUTs to:

- develop and test the software architecture before restricted data access is granted;
- verify SUT balancing code;
- test Method D transformation;
- build reusable pipelines.

This means the project does **not have to wait** for Research Service approval before methodological development begins.

---

# 7. Recommended study years

A two-benchmark-year strategy is preferable to immediately constructing a long time series.

## 7.1 Primary benchmark: 2022

Reasons:

- it can be aligned relatively closely with recent EXIOBASE economic data;
- it captures a modern Danish health system;
- current Statistics Denmark documentation identifies the final detailed SUT system through 2022 as consistent with the latest national-account framework.

## 7.2 Validation benchmark: 2019

Reasons:

- pre-COVID benchmark;
- avoids interpreting pandemic-specific healthcare expenditure as normal structural behaviour;
- enables a useful temporal robustness test.

The first methodological paper should prioritise two high-quality balanced models rather than a long but assumption-heavy time series.

---

# 8. Two-stage hybridisation

## Stage A. Danish matrix augmentation

The first hybridisation should answer:

> How can the existing health parent industry be divided into more specific Danish health industries while preserving the national accounts?

This is a **matrix augmentation / sector disaggregation** problem.

## Stage B. Danish-MRIO coupling

The second hybridisation should answer:

> How can official Danish domestic technology be combined with foreign supply-chain environmental intensities?

This follows the **simplified-SNAC** architecture used in Palm et al. and subsequently by Statistics Denmark.

The two steps should be independently tested.

---

# 9. Research gates

The complete project should proceed through explicit gates.

```text
G0  Select benchmark years
G1  Obtain / identify Danish SUT access
G2  Reproduce the official 117-industry IOT
G3  Inventory health products in the detailed SUT
G4  Construct DB07/ISIC/SHA/USEEIO concordances
G5  Estimate child-industry output and value-added margins
G6  Estimate differentiated Danish health production recipes
G7  Introduce USEEIO priors only for residual gaps
G8  Reconcile and balance the augmented SUT
G9  Disaggregate environmental extensions
G10 Reconstruct the augmented IOT
G11 Validate the domestic health footprint
G12 Couple Denmark to EXIOBASE
G13 Perform uncertainty and structural-path analysis
G14 Produce publication-ready Danish model
G15 Extend methodology internationally
```

A gate should not be passed until its balance, classification and validation tests are satisfactory.

---

# 10. Files in this research blueprint

1. `00_index_and_research_architecture.md`  
   Research architecture, research questions, detailed Danish SUT decision and data-access strategy.

2. `01_danish_sut_and_health_disaggregation.md`  
   Detailed national-account reconstruction, health classification, data hierarchy, USEEIO priors and constrained balancing.

3. `02_snac_exiobase_and_footprint_accounting.md`  
   Domestic EEIO calculation, health final-demand accounting, capital, simplified-SNAC, EXIOBASE coupling and footprint equations.

4. `03_validation_uncertainty_software_and_scaling.md`  
   Validation, aggregation tests, uncertainty, double counting, structural paths, international scaling, software and publication programme.

5. `04_sources_and_references.md`  
   Annotated scholarly literature and official statistical/API sources.

---

# 11. Overall methodological position

The recommended methodology can be summarised as:

\[
\boxed{
\text{Danish evidence first}
\rightarrow
\text{constrained augmentation}
\rightarrow
\text{official-account consistency}
\rightarrow
\text{foreign MRIO completion}
}
\]

The project should not begin by imposing US healthcare production recipes on Denmark.

Instead:

1. exploit the much richer Danish SUT and health-account information;
2. preserve all Danish accounting margins;
3. use USEEIO only as a transparent donor prior where Danish information is missing;
4. couple the resulting Danish model to EXIOBASE for foreign supply chains.

This approach combines the strengths of national accounting, EEIO, hybrid LCA and health accounting while keeping the most consequential assumptions visible and testable.
