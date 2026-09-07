# Statistics Denmark detailed SUT request guide

## 1. What is verified

Statistics Denmark currently states that:

1. the Danish working SUT contains approximately **2,350 products × 117 industries**;
2. detailed product-level supply-use relationships are **not publicly published** because of confidentiality;
3. users wishing to work with the most detailed tables may apply through **Research Services**;
4. some external users receive the full SUT through their Research Service account;
5. the subject-matter contact for National Accounts: Input-Output and Supply-Use is **Peter Rørmose Jensen**.

Contact:

**Peter Rørmose Jensen**  
National Accounts, Climate and Environment, Economic Statistics  
`prj@dst.dk`  
+45 40 13 51 26

Official documentation:

https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/statistical-presentation

---

# 2. Is the SUT free somewhere?

## Short answer

**Yes and no.**

### Free

You can obtain:

- Danish national SUTs from Eurostat at A64 resolution and potentially A88 where Denmark has supplied the voluntary detailed table;
- FIGARO 64 × 64 inter-country SUTs;
- Statistics Denmark's 117-industry symmetric IOT.

### Not found as a free public download

The **full working-level ~2,350-product × 117-industry Danish SUT**.

Statistics Denmark explicitly says that those detailed product-level relationships are not published and directs users to Research Services.

Therefore the correct request is not:

> "Can you send me the Danish SUT because no SUT is public?"

It is:

> "I have found the public A64/A88 SUT and 117-industry IOT, but my research requires the full working-level product detail. Could you confirm the access route?"

That demonstrates that you have already done the public-data search.

---

# 3. Correct contact sequence

## Step 1: do not start with a generic Research Service application

First email the **subject-matter statistician**, Peter Rørmose Jensen.

Purpose:

- confirm that the requested full SUT exists for the target years;
- confirm which matrices can be supplied;
- confirm whether access is through Research Services, a special delivery, or another arrangement;
- confirm whether an A88/public version would meet the request;
- ask whether there are cost or output restrictions.

This is the most efficient first step because the public documentation does not describe the exact SUT-specific DDP workflow in sufficient detail.

## Step 2: wait for route confirmation

If Peter confirms that the full SUT must be accessed through Research Services:

1. identify the relevant SDU authorised research environment/data manager;
2. confirm whether your unit can create/use a project in Denmark's Data Portal;
3. prepare the project proposal and data order;
4. submit only the data actually required.

## Step 3: use Research Service guidance

Statistics Denmark's general project proposal requires a concise:

- purpose;
- project description;
- societal relevance;
- justification of data;
- population/extraction description where applicable;
- external data description;
- data-package justification.

A data order documents the exact registers/data, periods and external data included in the project.

**Important:** the normal Data Portal documentation is designed largely around register/microdata projects. The public SUT documentation does not spell out exactly how the full SUT is represented in DDP. Therefore **confirm the SUT-specific ordering route before trying to force it into a standard register-data form**.

---

# 4. Materials to prepare before emailing

You do **not** need to attach all of these to the first 90-word email.

Have them ready.

## A. One-page research/data brief

Provided as:

`04_sut_request_brief.md`

It should state:

- project title;
- institution;
- research question;
- why public A64/A88 SUT or 117-IOT is insufficient;
- requested years;
- requested matrices;
- healthcare use case;
- intended outputs;
- no request for personal data;
- intended linkage to open environmental accounts and MRIO data.

## B. Exact table specification

Request, subject to availability:

### Supply

- product × industry output;
- imports;
- basic-price totals;
- valuation columns.

### Use

- product × industry intermediate use;
- household consumption;
- government consumption;
- NPISH;
- GFCF;
- inventories;
- exports.

### Domestic/import split

Prefer:

- domestic use at basic prices;
- import use at basic prices.

### Valuation

Request:

- trade margins;
- transport margins;
- taxes on products;
- subsidies on products;
- VAT where available.

### Metadata

Request:

- product codes and labels;
- industry codes and labels;
- classifications/concordances;
- structural zero/suppression information;
- table revision/version;
- price basis;
- units;
- balancing documentation.

## C. Requested years

Recommended:

### 2022

Main Denmark reference year.

### 2019

Cross-MRIO benchmark because it is pre-pandemic and well covered in EXIOBASE, GLORIA, Eora, OECD ICIO and FIGARO.

You may initially request **2019 and 2022** rather than a long time series. This follows data-minimisation logic and makes the request easier to justify.

---

# 5. Exact email under 100 words

**Subject:** Access to detailed Danish supply-use tables for academic research

> Dear Peter,
>
> I am a researcher at SDU developing a reproducible environmental input-output assessment of the Danish health-care sector. Statistics Denmark’s documentation indicates that the full supply-use tables (about 2,350 products × 117 industries) may be available through Research Services. Could you please confirm whether the 2019 and 2022 tables, including supply, use, domestic/import use and valuation matrices, can be accessed for academic research, and advise the correct application route and required materials? I would also appreciate confirmation of the most detailed freely available alternative.
>
> Best regards,  
> Albert Osei-Owusu

**Body word count:** 90 words under a conventional word-token count.

---

# 6. Why this email is preferable

It:

- shows you have read Statistics Denmark's own documentation;
- asks about **specific years**;
- specifies the matrix components needed;
- does not presume that Research Services is definitely the only route;
- asks for the correct route;
- explicitly asks about the most detailed free alternative;
- avoids sending a large methodological explanation before the statistician confirms feasibility.

---

# 7. Ready answers if Peter asks what the data are for

## Research purpose

> The purpose is to construct a Denmark-specific environmentally extended input-output model of healthcare. Health expenditure from the System of Health Accounts will be mapped to detailed Danish products and industries, combined with Statistics Denmark environmental accounts, and linked to global MRIO databases for imported supply chains.

## Why the 117-industry IOT is insufficient

> The 117-industry IOT is sufficient for model development but aggregates product detail needed to distinguish pharmaceuticals, medical devices, clinical supplies and service inputs. The working-level SUT would allow the healthcare final-demand mapping to be based on Danish product structure rather than broad MRIO sector proxies.

## Why 2019 and 2022

> 2022 is the preferred main reference year because current Danish environmental accounts and recent MRIO systems can be aligned to it. 2019 is requested as a pre-pandemic common benchmark for cross-MRIO sensitivity analysis.

## Why domestic/import split

> The study will use Danish environmental extensions for domestic production and external MRIO extensions for foreign production. A domestic/import split is therefore required to avoid applying Danish production intensities to imported products.

---

# 8. If Research Services is required

Statistics Denmark's current general Research Service process requires an authorised institution for microdata schemes.

For this project, do not assume that you personally need to obtain a new institutional authorisation. First determine whether the relevant SDU research environment is already authorised and who the institutional authorisation/data manager is.

## Project material to have ready

### Purpose

> To quantify the direct and supply-chain environmental footprints of Danish healthcare and identify healthcare functions, products, industries and foreign supply-chain nodes responsible for greenhouse-gas emissions, air pollution, water use, waste and resource use.

### Project description

Include:

- environmentally extended input-output analysis;
- Danish SUT/IOT;
- SHA healthcare expenditure;
- domestic environmental accounts;
- MRIO imports;
- no patient-level inference;
- cross-MRIO sensitivity.

### Societal relevance

Explain that the model will provide:

- evidence for healthcare decarbonisation;
- procurement hotspot identification;
- consistent monitoring of supply-chain environmental impacts;
- reproducible national healthcare sustainability indicators.

### Data minimisation

Emphasise:

- only 2019 and 2022 initially;
- aggregated economic tables;
- no personal identifiers;
- no need for enterprise-level confidential microdata beyond the balanced SUT itself.

### External data to declare if the project environment requires it

Potential external data:

- SHA/open StatBank extracts;
- EXIOBASE;
- GLORIA;
- Eora;
- OECD ICIO;
- FIGARO;
- environmental characterisation factors.

---

# 9. Questions to resolve before submitting a formal order

Ask or confirm:

1. Is the full 2,350 × 117 SUT available for both 2019 and 2022?
2. Are 2019 and 2022 fully revised on a consistent national-accounts basis?
3. Are both current-price and previous-year-price versions available?
4. Can domestic and imported use be supplied separately?
5. Are margin and tax matrices available?
6. Can the product classification and concordance be supplied?
7. Are there suppressed cells or output restrictions?
8. Is access only on the Research Service server, or can a disclosure-controlled table be delivered?
9. Does the SUT request require a standard DDP project/data order?
10. What are the expected costs and lead time?
11. Is Denmark's A88 Eurostat transmission available for 2022, and if so is that the most detailed open substitute?
12. Are there existing environmental-account/SUT link tables that could reduce custom work?

---

# 10. Do not request more than needed initially

Avoid requesting:

- all years;
- enterprise microdata;
- confidential source datasets used to compile the SUT;
- individual healthcare records;
- product-level procurement records from Statistics Denmark unless clearly necessary.

The initial scientific need is the **balanced national SUT**, not the source microdata behind it.

---

# 11. Fallback if full access is not feasible

Use a tiered fallback:

## Tier 1

Full 2,350-product × 117-industry SUT.

## Tier 2

Eurostat A88 Denmark SUT if available for the year.

## Tier 3

Eurostat A64 national SUT.

## Tier 4

Statistics Denmark 117-industry IOT plus SHA disaggregation.

Every model run should record which tier was used.

---

# 12. Decision rule

Do not delay the entire project while access is being resolved.

Proceed immediately with:

\[
\text{117-industry IOT}
+
\text{SHA1}
+
\text{environmental accounts}
\]

and construct the code so that the detailed SUT can later replace the economic core without redesigning the star schema.
