# Denmark healthcare environmental-footprint data deep dive, version 2

## Purpose

This package revises and strengthens the earlier Danish data-access assessment. It focuses on four questions that materially affect the study design:

1. Can the roughly 2,350 Danish national-accounts products be obtained as a usable bilingual product list?
2. Which apparent data gaps are genuine, and which can be addressed through alternative administrative, regional or research data?
3. How should Danish healthcare waste be benchmarked without mistaking dependent datasets for independent validation?
4. Is FIGARO sufficiently suitable to justify an explicit replication and sensitivity exercise?

It also updates the cross-MRIO strategy to include **GLORIA** alongside EXIOBASE, Eora, OECD ICIO and FIGARO.

## Main conclusions

### 1. The exact 2,350-product list is not verified as a free public download

Statistics Denmark confirms that the final Danish SUT works with approximately **2,350 products and 117 industries**, but the most detailed supply-use tables are not published because of confidentiality.

Detailed product balances can, however, be supplied as customised paid national-accounts extracts, while some external users obtain the full SUT through Statistics Denmark Research Services.

Therefore the correct access strategy is:

\[
\text{subject-matter contact}
\rightarrow
\begin{cases}
\text{metadata / paid extract},\\
\text{Research Services full SUT},\\
\text{public A64/A88 fallback}
\end{cases}
\]

rather than assuming that Research Services is automatically the only route.

### 2. A bilingual health-product candidate universe can be built before the full SUT arrives

Public HS/CN and CPA classifications can be used to create Danish and English labels and flag candidate healthcare products. This will **not reproduce the exact Danish national-accounts product classification** until Statistics Denmark provides its year-specific product code/concordance.

### 3. Several earlier “data gaps” are really access and harmonisation gaps

Regional climate accounts and the common regional climate-management model show that data exist for substantial parts of:

- medical gases;
- procurement;
- patient articles;
- patient transport;
- business travel;
- energy and buildings.

However, much of the procurement climate accounting remains spend-based and partly uses EXIOBASE-type emission factors. These regional results are therefore useful operational and boundary checks, but **not automatically independent environmental benchmarks**.

### 4. Waste can be triangulated very strongly

Use four layers:

1. hospital/region operational waste;
2. Danish EPA ADS raw/statistical waste data;
3. Statistics Denmark Waste Accounts;
4. Eurostat harmonised waste statistics.

Add NHS England ERIC as an independent international hospital operational comparator.

The EPA, Statistics Denmark and Eurostat layers share underlying reporting chains and should not be portrayed as three independent measurements.

### 5. FIGARO is worth testing

FIGARO 2026 provides:

- 64 industries × 64 products;
- 2010–2024;
- supply tables;
- use tables;
- industry-by-industry IOTs;
- product-by-product IOTs;
- direct purchases abroad.

At A64, **human health activities (Q86) are separate from residential/social work (Q87–Q88)**, and pharmaceutical manufacturing (C21) is separately identifiable. This makes FIGARO more useful for healthcare than a generic “health and social work” description suggests.

Its limitation is still material: medical-device and clinical-supply detail is coarse.

### 6. Recommended model hierarchy

\[
\boxed{
\text{DK detailed SUT + SHA + Danish environmental accounts}
}
\]

is the preferred Danish backbone.

Use:

- **EXIOBASE** for broad environmental MRIO sensitivity and foreign environmental extensions;
- **GLORIA** for resource/material sensitivity;
- **FIGARO** for official EU trade and GHG benchmarking;
- **Eora** for Lenzen-method replication;
- **OECD ICIO** for economic trade/value-chain sensitivity.

## Documents

1. `01_v2_danish_product_classification_and_health_filter.md`
2. `02_v2_data_gap_resolution_matrix.md`
3. `03_v2_waste_benchmarking_protocol.md`
4. `04_v2_figaro_feasibility_and_test_plan.md`
5. `05_v2_cross_mrio_strategy_with_gloria.md`
6. `06_v2_statistics_denmark_contact_and_acquisition_plan.md`
7. `07_v2_evidence_and_source_register.md`

## Verification date

Public web sources and institutional access routes checked on **6 September 2026**.
