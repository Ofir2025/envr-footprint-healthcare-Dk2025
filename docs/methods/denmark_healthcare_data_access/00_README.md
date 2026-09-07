# Denmark healthcare environmental footprint data package

## Purpose

This package converts the data-access investigation into a reproducible acquisition and modelling plan for a Danish healthcare environmental-footprint study.

It is designed around five principles:

1. Use the most detailed Danish official economic data available before resorting to MRIO averages.
2. Separate the **healthcare boundary** from the **economic production structure**.
3. Use Danish official environmental accounts for domestic production and MRIO databases for foreign supply chains.
4. Benchmark results across multiple MRIO systems rather than treating one database as ground truth.
5. Record every dataset, mapping and modelling choice in auditable fact, dimension and bridge tables.

## Documents

### 01. Danish data access inventory

`01_denmark_data_access_inventory.md`

Contains the full inventory of Danish economic, health, environmental, pharmaceutical, travel and supporting datasets, their access conditions, exact table identifiers where available, and the target database package for each source.

### 02. Cross-MRIO replication strategy

`02_cross_mrio_replication_strategy.md`

Adds GLORIA to the sensitivity framework and compares EXIOBASE, GLORIA, Eora, OECD ICIO and FIGARO. It specifies the common-year strategy, harmonisation rules and cross-MRIO result packages.

### 03. Statistics Denmark SUT request guide

`03_statistics_denmark_sut_request_guide.md`

Explains exactly what is freely available, what is not, whom to contact first, what materials to prepare, what not to submit prematurely, and what to do if Statistics Denmark confirms that Research Services is required.

### 04. Ready-to-attach SUT request brief

`04_sut_request_brief.md`

A concise project/data specification that can be attached after the subject-matter contact confirms the route.

### 05. Data acquisition register

`05_data_acquisition_register.md`

A working register linking each dataset to its source, access class, years, resolution, model role, target fact/bridge table and next action.

## Main conclusion

The **full Danish working-level SUT of roughly 2,350 products × 117 industries is not publicly released**. Statistics Denmark explicitly states that detailed product-level supply-use relationships are not published because of confidentiality and that the most detailed tables can be accessed by some external users through Research Services.

However, **free Danish SUTs do exist at more aggregated resolution**:

- Eurostat national SUTs: mandatory A64 and, where voluntarily supplied, A88;
- FIGARO: 64 industries × 64 products, 2010–2024;
- Statistics Denmark: public 117-industry IOT and multiplier tables.

Therefore the correct distinction is:

> **Free SUT available? Yes, at aggregated resolution.  
> Full ~2,350-product Danish working SUT freely downloadable? No evidence found; Statistics Denmark says it is not published.**

## Suggested study years

- **Main Denmark model:** 2022, because Danish accounts and EXIOBASE 3.10.2 can be aligned well.
- **Pure cross-MRIO benchmark:** 2019, because it is pre-pandemic and avoids relying on projected/nowcast years in GLORIA and some other systems.
- **Optional recent sensitivity:** 2021 or 2022, with explicit database-vintage flags.

## Verification date

Web access and institutional routes verified: **6 September 2026**.
