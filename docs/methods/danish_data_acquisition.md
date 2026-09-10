# Danish data acquisition

This document is the record of the pre-modelling question: where does the data
for a Danish healthcare environmental-footprint study actually come from, what
is genuinely public, what needs a formal request, and how good is each source
once obtained. It merges eleven documents that were built in two passes — a
first inventory (sections 1, 8 and 9 below) and a later deep dive (sections 2,
3, 5, 6 and 10) that revised the cross-MRIO strategy, the Statistics Denmark
contact plan and the source register, and added three topics the first pass
had not covered at all: product classification, gap independence, and
dedicated waste and FIGARO feasibility studies. Section 4 (cross-MRIO
replication strategy) and section 7 (the Statistics Denmark contact plan) are
themselves each a merge of a first-pass document and the deep dive's revision
of it, done at the time the two passes were folded into one `danish_data_acquisition/`
folder; nothing either pass found alone was dropped in that earlier merge, and
nothing is dropped in this one. Sections 9 and 10 answer different questions
and are both kept in full: 9 tracks *datasets* toward acquisition, 10 tracks
*claims* toward verification.

## Contents

1. [Denmark data access inventory](#1-denmark-data-access-inventory)
2. [Danish product classification and health filter](#2-danish-product-classification-and-health-filter)
3. [Data gap resolution matrix](#3-data-gap-resolution-matrix)
4. [Cross-MRIO replication strategy](#4-cross-mrio-replication-strategy)
5. [Waste benchmarking protocol](#5-waste-benchmarking-protocol)
6. [FIGARO feasibility and test plan](#6-figaro-feasibility-and-test-plan)
7. [Statistics Denmark contact and acquisition plan](#7-statistics-denmark-contact-and-acquisition-plan)
8. [SUT request brief](#8-sut-request-brief)
9. [Data acquisition register](#9-data-acquisition-register)
10. [Evidence and source register](#10-evidence-and-source-register)

Access codes used throughout: **OPEN** (publicly downloadable or API-accessible
without a research application), **CONTROLLED** (requires an
institutional/research application), **REQUEST** (no standard public extract
identified; direct contact or a custom statistics request is appropriate),
**MRIO** (external multi-regional input-output database).

---

## 1. Denmark data access inventory

For every dataset a Danish replication of Malik, Eckelman or Lenzen needs
(economic core, health expenditure, GHG, air pollution, water, waste,
materials, pharmaceuticals, travel, clinical procurement), where is it, and is
it open, controlled or request-only? The "target" table names below name
tables in the published star schema, `docs/methods/star_schema.sql`, and the
30 tables actually shipped under `data/gold/results/star/`.

### 1.1 Economic core

**Full Danish working-level SUT.** Source: Statistics Denmark, National
Accounts: Input-Output and Supply-Use. Resolution: approximately 2,350
products × 117 industries. Status: **CONTROLLED**. Statistics Denmark states
that the Danish SUT system balances approximately 2,350 products and 117
industries; only some industry-level totals are published in StatBank;
detailed product-level supply-use relationships are not published because of
confidentiality; users wishing to work with the most detailed tables can apply
for access through Research Services; some external users receive the full
SUT through their Research Service account. The detailed SUT is the preferred
domestic backbone because it retains the product × industry structure needed
to distinguish pharmaceuticals, medical devices, hospital services, outpatient
services, diagnostic goods/services, food, electricity, construction,
transport, ICT, cleaning and other intermediate products. Target database
objects: `dim_industry`, `dim_industry_group`, `fact_health_expenditure`.
Source: https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/statistical-presentation

**Public Danish 117-industry IOT.** Source: Statistics Denmark. Status:
**OPEN**. The current input-output page provides a 117-industry IOT as a
downloadable ZIP and current StatBank tables including `NAIO1` (input-output
table, supply by industries, use and price unit), `NAIO2` (unallocated
imports), `NAIO3` (primary inputs), `NAIO4` (totals) and `NAIO5` (employment).
Use this immediately to build and test the IO engine, validate row/column
orientation, reproduce official multipliers, and build the star-schema
pipeline before restricted SUT access is resolved. Source:
https://www.dst.dk/en/Statistik/emner/oekonomi/nationalregnskab/input-output

**Free national SUTs from Eurostat.** Source: Eurostat ESA supply, use and
input-output tables. Status: **OPEN**. This is the key correction to an
earlier, looser wording: **Danish SUT data are available free at aggregated
European reporting resolution.** Mandatory national SUT transmission
distinguishes 64 activities and 64 products; countries may voluntarily
transmit 88 activities and 88 products. Annual tables include `T1500`
(supply table at basic prices including transformation to purchasers' prices)
and `T1600` (use table at purchasers' prices). For benchmark years ending in
0 or 5, the system also includes `T1610` (use at basic prices), `T1611` (use
of domestic output), `T1612` (use of imports), `T1620` (trade and transport
margins), `T1630` (taxes less subsidies), and symmetric IOTs. Common Eurostat
dataset families include `naio_10_cp15` (supply table) and `naio_10_cp16`
(use table). Limitation: these tables are **not the same as the full
~2,350-product Danish working SUT**; they are useful open substitutes and
harmonised validation datasets. Sources:
https://ec.europa.eu/eurostat/en/web/esa-supply-use-input-tables/information-data
and https://ec.europa.eu/eurostat/en/web/esa-supply-use-input-tables/database

**FIGARO.** Source: Eurostat FIGARO 2026 edition. Status: **OPEN**. Coverage:
64 industries, 64 products, 2010-2024, EU inter-country supply, use and IOT
tables, CSV data for supply, use and IOT, 27 EU states plus candidate
countries, major trading partners and rest of world. Role: open EU-level
sensitivity, bilateral EU supply-chain structure, and an independent bridge
between the domestic Danish model and global MRIO calculations. Source:
https://ec.europa.eu/eurostat/en/web/esa-supply-use-input-tables/database

### 1.2 Healthcare expenditure and boundary

**SHA1.** Source: Statistics Denmark StatBank. Table: `SHA1`. Status:
**OPEN**. Approximate dimensions currently include 44 healthcare functions,
34 provider categories, 8 financing schemes, and annual current-price
expenditure. SHA should define **what counts as healthcare** and how final
demand is disaggregated. It should not simply be added to national-accounts
health expenditure; instead, construct a concordance from SHA
function/provider/financing to SUT products/industries, with weights that
reconcile to the agreed healthcare control total. Target objects:
`fact_health_expenditure`, `dim_health_function`. Source:
https://www.statbank.dk/SHA1

### 1.3 Greenhouse gases and air pollution

**DRIVHUS / DRIVHUS2.** Status: **OPEN**. Use for direct Danish industry
greenhouse-gas extensions. Useful healthcare-relevant industries include
pharmaceuticals, medical instruments and health-service industries. Target
objects: `fact_ghg_species`, `fact_scope_component`. Source:
https://www.statbank.dk/DRIVHUS

**MRU1.** Status: **OPEN**. Industry air-emission account containing
pollutants including CO2, SO2, NOx, CO, NH3, N2O, CH4, NMVOC, PM10, PM2.5 and
F-gases — the core domestic extension for the Eckelman-style multi-pollutant
model. Source: https://m.statbank.dk/TableInfo/MRU1

**EMM1MU2N.** Status: **OPEN**. Statistics Denmark's direct and indirect
air-emission multiplier table by final-demand category. It can be used as an
**independent unit test** of a custom calculation $F = q\,\mathbf{L}\,y_H$.
Target role: validation of `fact_national_total`, final-demand multipliers,
and pollutant intensities. Source:
https://m.statbank.dk/TableInfo/EMM1MU2N

**EMM1MU3N.** Status: **OPEN**. Provides emissions caused by final demand by
the industries in which the emissions arise. Target role: validation of
`fact_footprint_node`. Source: https://m.statbank.dk/TableInfo/EMM1MU3N

### 1.4 Water

**VANDRG2.** Status: **OPEN**. Physical water account by industry and water
type. Target: `fact_footprint_node`. Source:
https://m.statbank.dk/TableInfo/VANDRG2

**VAN2MU2N.** Status: **OPEN**. Contains direct and indirect water use
caused by final demand and multipliers per monetary demand, for independent
validation of the domestic water footprint. Important distinction: this is
physical water consumption, not automatically scarcity-weighted water. For
Lenzen-style scarce-water footprints, $F_{\text{scarce water}} = \sum_r
\text{Water}_r \times \text{ScarcityFactor}_r$, so foreign regional water
must be supplied by an MRIO/resource dataset and regional scarcity factors.
Source: https://m.statbank.dk/TableInfo/VAN2MU2N

### 1.5 Waste

**AFFALD.** Status: **OPEN**. Physical waste generation by industry, waste
fraction and treatment. Source: https://m.statbank.dk/TableInfo/AFFALD

**AFF1MU2N and related multiplier tables.** Status: **OPEN**. Direct and
direct-plus-indirect waste by final demand, including multiplier units.
Target: `fact_national_total`, `fact_health_function`. Source:
https://m.statbank.dk/TableInfo/AFF1MU2N

**AFF1MU3N and related producer tables.** Status: **OPEN**. Producing-industry
attribution for waste caused by final demand. Target: `fact_footprint_node`.
Source: https://m.statbank.dk/TableInfo/AFF1MU3N

### 1.6 Materials and land

**MRM2.** Status: **OPEN**. Economy-wide material flows covering biomass,
ores, non-metallic minerals and fossil materials — a national material-flow
benchmark and extension-development input. Source:
https://m.statbank.dk/TableInfo/MRM2

**RME1.** Status: **OPEN**. Raw-material-equivalent / resource-footprint
account — a national material-footprint denominator and validation
benchmark. Limitation: a ready-made public *health final demand × raw
material* multiplier table comparable to EMM1MU2N was not identified;
healthcare-specific material footprints therefore still require custom
IO/MRIO calculation. Source: https://m.statbank.dk/TableInfo/RME1

**AREALAN1.** Status: **OPEN**, but low priority. Contains broad domestic
land-use information and is too aggregated to represent the full global
healthcare land footprint; domestic land benchmark only. Source:
https://m.statbank.dk/TableInfo/AREALAN1

### 1.7 Official Danish consumption-footprint benchmark

**AFTRYK1.** Status: **OPEN**. Danish consumption climate footprints by
final use, emitting industry, emitting country and year — particularly
valuable for validating $F_{\text{domestic}}$ versus $F_{\text{foreign}}$.
Target: `fact_footprint_node`, `fact_national_total`. Source:
https://m.statbank.dk/TableInfo/AFTRYK1

### 1.8 Pharmaceuticals

**Medstat.** Status: **OPEN**. Exploratory pharmaceutical statistics and
preliminary product/ATC activity.

**Custom aggregated statistical extract.** Institution: Danish Health Data
Authority / Forskerservice. Status: **REQUEST**. This should be the **first
pharmaceutical data request** before applying for person-level registers.
Suggested grain: year/month × ATC × product/package × sector × region ×
hospital/department where possible. Suggested measures: packages, DDD,
physical quantity, sales/purchase value, number of units. Why this route: the
footprint model does not require personal identifiers, so a
disclosure-controlled aggregate extract is likely to be simpler and more
proportionate. Source:
https://sundhedsdatastyrelsen.dk/data-og-registre/forskerservice/ansoeg-om-data/statistikudtraek

**Lægemiddelstatistikregisteret / LMDB.** Status: **CONTROLLED**. Use if the
aggregate extract cannot provide sufficient product/provider detail.
Potential role: pMDIs, pharmaceutical quantities, provider/hospital
disaggregation, product-level validation.

**Amgros.** Status: **REQUEST**. No open row-level national hospital
pharmaceutical-procurement dataset suitable for this model was identified.
Approach Amgros only after defining the exact fields missing from LSR/LMDB or
an aggregate Health Data Authority extract.

### 1.9 Travel

**DTU Transportvaneundersøgelsen.** Status: mixed — public summaries
**OPEN**; custom/detailed extracts **REQUEST**. Useful variables include
mode, trip purpose, distance, geography, and demographic/household variables
where permitted. Limitation: no single public national table was identified
that simultaneously gives provider × staff/patient/visitor × mode ×
distance; a healthcare-specific travel model will therefore require TU plus
provider/activity or survey data. Contact route: `turequests@transport.dtu.dk`.
Source:
https://www.man.dtu.dk/english/Scientific-advice/The-Danish-National-Travel-Survey/Documentation

### 1.10 Clinical gases and non-pharmaceutical procurement

**Anaesthetic gases.** Status: **REQUEST**. No open national hospital-level
annual dataset for N2O, desflurane, sevoflurane and related clinical gases
was identified. Potential sources to investigate: Danish Regions, regional
procurement, hospital pharmacies, technical/facility gas purchasing systems.

**Medical consumables and devices.** Status: **REQUEST**. No open national
SKU-level procurement dataset was identified for all disposables, implants,
diagnostics, PPE, instruments and equipment. Potential sources: regional
procurement units, Danish Regions, hospital procurement systems, SKI where
categories overlap, supplier/contract records.

### 1.11 External MRIO sources

Detailed comparison is in [section 4](#4-cross-mrio-replication-strategy).
Recommended MRIO set: EXIOBASE, GLORIA, Eora, OECD ICIO, FIGARO — treated as
**alternative model systems**, not interchangeable raw datasets.

### 1.12 Access priority

Immediate downloads, in order: Statistics Denmark 117-industry IOT; SHA1;
DRIVHUS/DRIVHUS2; MRU1; EMM1MU2N/EMM1MU3N; VANDRG2/VAN2MU2N;
AFFALD/AFF*MU*; MRM2/RME1; AFTRYK1; Eurostat national A64/A88 SUTs; FIGARO;
EXIOBASE. Parallel requests: full Danish detailed SUT; pharmaceutical
aggregate extract; TU healthcare-relevant extract; clinical gases/procurement.

### 1.13 Bottom line on SUT availability

> **A Danish SUT is available free at aggregated resolution. The full
> approximately 2,350-product × 117-industry working SUT is not publicly
> downloadable according to Statistics Denmark's current documentation.**

The free alternatives do not remove the value of requesting the full SUT,
because product-level health-system disaggregation is precisely where the
extra detail matters most.

---

## 2. Danish product classification and health filter

The exact ~2,350-product Danish national-accounts classification is not
public — so what can be built from public CN/HS/CPA classifications in the
meantime, and how should "a healthcare product" be defined without conflating
it with "a healthcare industry"?

### 2.1 The central question

The Danish final supply-use system is compiled using approximately $2{,}350$
products $\times$ $117$ industries; the number of products varies slightly by
year as products enter and leave the balancing system. The key question is
not merely whether "a Danish product classification exists", but whether we
can obtain: (1) the exact year-specific national-accounts product codes used
in the 2019 and 2022 SUTs; (2) their descriptions; (3) Danish and English
labels; (4) the mapping from those product codes to standard classifications
such as HS/CN and CPA; (5) the corresponding numerical SUT rows. These are
different access objects and should be requested separately.

### 2.2 What Statistics Denmark explicitly confirms

Statistics Denmark's SUT documentation states that final SUT compilation uses
about 2,350 products and 117 industries; product-by-product supply and use
are reconciled so supply equals use; the most detailed SUTs are not publicly
published because of confidentiality; some external users receive full SUTs
through Research Services. Statistics Denmark's annual national-accounts
accessibility documentation also says that more detailed information from the
approximately 2,350 product balances can be purchased as customised data, for
example a single product balance or the product composition of a consumption
group. This means there are at least three distinct access routes:

| Object | Likely route |
|:---|:---|
| Public aggregate SUT/IOT | StatBank / Eurostat / DST download |
| Selected detailed product balances or compositions | Custom paid extract from National Accounts |
| Full working-level SUT | Research Services, subject to approval/confidentiality |

Official sources:
https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/statistical-presentation,
https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/relevance,
https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--annual/accessibility-and-clarity

### 2.3 Is there a free public list of the exact 2,350 product codes?

**No exact, current, year-specific public list has been verified.** Statistics
Denmark states that the final national accounts contain about 2,350
reconciled product balances, while detailed product breakdowns are not
published in StatBank. There is also a classification nuance to resolve
directly with Statistics Denmark: SUT methodology describes goods in terms
connected to HS/foreign-trade classifications and services to CPA, while
broader national-accounts documentation describes the national product
dimension as an **adapted CPA-based classification**. These descriptions are
not necessarily contradictory — a national product code may be an internal
national-accounts classification populated from HS/CN data for goods and
CPA/service sources — but the exact code architecture is not documented
clearly enough publicly to reconstruct it without confirmation. The request
should therefore explicitly ask for: `nr_product_code`, `label_da`,
`label_en` (if maintained), `good_service_flag`, `hs6_mapping`,
`cn8_mapping`, `cpa21_mapping`, `cpa88_parent`, `valid_from`, `valid_to`,
`revision_year`. If Statistics Denmark does not maintain English labels
internally, the HS/CPA concordance is sufficient for us to attach
authoritative English labels ourselves.

### 2.4 What can be built publicly now?

A high-quality bilingual **candidate product universe** can be assembled from
CN/HS goods plus CPA products/services. This will not be identical to the
2,350-row SUT dimension, but it lets us design and test the healthcare
classifier before restricted metadata arrive.

**Goods.** The Combined Nomenclature (CN) is available annually; its first
six digits correspond to HS. Statistics Denmark provides CN search/download
infrastructure and Eurostat provides classification code lists and
correspondence infrastructure. The product table should preserve the exact
classification year because CN codes change over time. Recommended fields:
`classification_year`, `cn8_code`, `hs6_code`, `label_da`, `label_en`,
`valid_from`, `valid_to`.

**Services and CPA products.** Use CPA 2.1 for the 2019/2022 model unless
Statistics Denmark specifies a different national product mapping for a
particular table version. Recommended fields: `cpa_code`, `cpa_level`,
`label_da`, `label_en`, `parent_cpa`.

### 2.5 Do not call all product rows "health sectors"

This distinction is essential. An **industry** answers "who produces?" (for
example NACE C21 pharmaceutical manufacturing, or NACE Q86 human health
activities). A **product** answers "what is supplied or used?" (for example
pharmaceutical preparations, diagnostic reagents, medical equipment, hospital
services). The healthcare model needs both dimensions: a hospital can consume
products produced by dozens of non-health industries, so healthcare footprint
$\neq$ footprint of industries classified as healthcare.

### 2.6 Recommended healthcare product taxonomy

Use a tiered classifier.

**Tier 1 — core healthcare**, with strong inclusion evidence: human health
services (NACE/CPA 86, hospital activities, medical and dental practice,
other human health services); pharmaceuticals (CPA/NACE 21; HS chapter 30,
refined at subheading level); medical devices (CPA/NACE 32.50 where
available; electromedical and radiation equipment within CPA/NACE 26.60 where
relevant); diagnostics (relevant laboratory/diagnostic reagents such as HS
3822, filtered at subheading level).

**Tier 2 — healthcare-dependent products**, strongly used by healthcare but
not exclusively healthcare-specific: respiratory equipment, prostheses,
hearing aids, X-ray apparatus, specialised medical furniture, selected PPE,
selected sterile consumables, selected laboratory goods. Representative HS
families for **candidate screening only**:

| HS heading/family | Candidate health use |
|:---|:---|
| 3001-3006 | medicinal and pharmaceutical goods |
| 3822 | diagnostic/laboratory reagents |
| 9018 | medical, surgical, dental and veterinary instruments |
| 9019 | mechanotherapy/respiratory-related apparatus |
| 9020 | breathing appliances |
| 9021 | orthopaedic appliances, prostheses, hearing aids etc. |
| 9022 | X-ray and radiation apparatus |
| 9402 | medical, surgical and dental furniture |

These headings must **not** be included wholesale without lower-level review,
because some include veterinary or non-health uses.

**Tier 3 — enabling inputs**: not "health products" in a narrow
classification sense but potentially major healthcare footprint drivers —
electricity, heating, construction, food, laundry, cleaning, ICT, transport,
chemicals, packaging, office services. Tier 3 should be discovered from the
hospital/SHA demand structure, not by relabelling the underlying products as
medical.

### 2.7 Social care boundary

Do not automatically include all of NACE/CPA 87 and 88. Instead use SHA to
determine the health boundary, with separate flags: `health_core_flag`,
`long_term_healthcare_flag`, `social_care_flag`, `sha_in_scope_flag`. This
makes it possible to publish healthcare only, healthcare plus health-related
long-term care, or broader health and social care, without rewriting the base
data.

### 2.8 Proposed bilingual product dimension

Create `dim_dk_na_product` with fields: `product_key`, `reference_year`,
`dst_na_product_code` (exact DST code once obtained), `label_da`, `label_en`,
`classification_origin` (DST/CN/HS/CPA), `cn8_code`, `hs6_code`,
`cpa21_code`, `cpa88_parent`, `cpa64_parent`, `good_service_flag`,
`health_tier` (0, 1, 2, 3), `health_group` (pharma/device/service/etc.),
`sha_hc_code`, `capital_flag`, `clinical_consumable_flag`,
`mapping_confidence` (high/medium/low), `mapping_method`
(code/manual/procurement/SHA), `review_status` (pending/verified/rejected),
`source_version`.

### 2.9 Healthcare candidate bridge

Keep healthcare classification as a bridge rather than hard-coding a
permanent health flag into the product master: `bridge_product_health_scope`
with fields `product_key`, `health_scope_key`, `sha_hc_code`,
`inclusion_weight`, `inclusion_reason`, `evidence_source`,
`confidence_grade`, `reviewer`, `review_date`. This allows one product to be
100% healthcare, partly healthcare, or in-scope only for a particular SHA
function.

### 2.10 Filtering workflow

Five passes: (1) **exact-code screening** using known CPA/HS/CN code
families; (2) **bilingual keyword screening** — English examples: medical,
hospital, pharmaceutical, medicinal, diagnostic, surgical, dental, prosthetic,
orthopaedic, laboratory, ambulance, rehabilitation; Danish examples: medicinsk,
hospital, lægemiddel, farmaceutisk, diagnostisk, kirurgisk, tandlæge, protese,
ortopædisk, laboratorie, ambulance, rehabilitering (for candidate discovery,
not final inclusion); (3) **SHA concordance** — check whether the product is
purchased within a SHA healthcare function/provider; (4) **procurement
validation** — use regional procurement categories/SKUs to establish which
candidate products are actually consumed by healthcare; (5) **manual review**
of multi-use products, veterinary-containing headings, mixed social/health
services, capital goods, chemicals/reagents, and PPE.

### 2.11 What we should request from Statistics Denmark

The first contact should ask for both **data** and **classification
metadata**. Priority metadata request: (1) year-specific product code list
for 2019 and 2022; (2) Danish product descriptions; (3) English labels if
maintained; (4) HS/CN mapping for goods; (5) CPA mapping for
services/products; (6) A88/A64 parent mapping; (7) code validity/version
information. Priority numeric request: (1) supply matrix; (2) use matrix; (3)
domestic/import use if available; (4) valuation matrices; (5) final demand;
(6) capital formation. This separates the classification problem from the
confidentiality problem.

### 2.12 Practical conclusion

We can begin health-product filtering **before** full SUT access, but we
should not claim that a public HS/CPA-derived list is the exact Danish
2,350-product SUT dimension. The correct workflow is public CN/HS + CPA
bilingual universe $\rightarrow$ candidate healthcare classifier
$\rightarrow$ DST year-specific product list + concordance $\rightarrow$
verified health-to-SUT bridge. This is both reproducible and scientifically
defensible.

---

## 3. Data gap resolution matrix

Of the items flagged as data gaps in [section 1](#1-denmark-data-access-inventory),
which are genuine absences and which are really access, harmonisation or
independence problems — and what evidence quality does each source clear?

### 3.1 Why the earlier "gap" language was too simple

A data item can exist but still be unusable for replication because it is not
public; not national; not harmonised across regions; lacks physical
quantities; is spend-based rather than activity-based; reuses EXIOBASE
factors and therefore is not independent of the model being benchmarked; has
a healthcare boundary that differs from SHA; or is only available in reports
rather than machine-readable tables. The revised inventory therefore scores
each gap on: existence, accessibility, resolution, methodological
independence, preferred solution, and fallback solution.

### 3.2 Revised gap matrix

| Data need | Evidence data exist? | Public usable data? | Independence from EEIO/MRIO | Preferred route | Residual gap |
|:---|:---|:---|:---|:---|:---|
| Detailed Danish SUT | Yes | No at full ~2,350 level | High | DST Research Services/custom extract | access/cost/confidentiality |
| Product classification | Yes | Exact 2,350 list not verified public | High | request code list + HS/CPA concordance | exact metadata |
| Health expenditure | Yes | Yes, SHA1 | High | DST SHA | concordance to SUT |
| Pharmaceuticals | Yes | partially | High for physical sales | Medstat / aggregate SDS extract / LSR-LMDB | provider-product detail |
| Hospital procurement | Yes, >150k products | reports only at useful aggregates | mixed | common regional climate/procurement extract | machine-readable harmonised SKU data |
| Medical gases | Yes | public aggregates | high for physical use if obtained | regional/common climate model | harmonised hospital×gas quantities |
| Patient transport paid by regions | Yes | regional reports | high | regional transport systems | national harmonised extract |
| Self-arranged patient travel | indirect | no national ready-made table | modelled | LPR origin-destination + TU mode model | mode choice/visitor separation |
| Staff business travel | Yes | regional reports | high | regional climate accounts | harmonised national extract |
| Staff commuting | indirect | no healthcare-specific public table | modelled | residence-workplace registers + TU | controlled access |
| Visitor travel | weak | no | modelled | facility surveys/scenarios | genuine evidence gap |
| Hospital waste | Yes | regional reports | high | regional operational waste | harmonised five-region table |
| National waste | Yes | EPA + DST | same lineage | ADS + AFFALD | boundary/classification |
| Cross-country waste | Yes | Eurostat | national reporting lineage | Eurostat WStatR | coarse activity groups |
| Energy | Yes | strong | high | regional meters + Danish energy accounts | organisational boundary |
| Buildings/capital | Yes | partial | mixed | DST GFCF + regional construction data | asset allocation |
| Food | Yes | procurement/spend | mixed | regional procurement + SUT/MRIO | physical composition |
| Devices/consumables | Yes | procurement reports/ERP likely | mixed | regional SKU/category extract | factors and product mapping |
| Water | Yes | strong national account | high domestically | VANDRG/VAN2MU + MRIO imports | scarcity weighting abroad |
| Materials | national aggregate yes | yes | high | DST material accounts + GLORIA/EXIOBASE | health-specific attribution |
| Land | weak domestic sector detail | limited | high | MRIO extensions | healthcare-specific domestic detail |
| Public-health damage | emissions yes; endpoint factors external | yes for many factors | model-based | air emissions + LCIA/health impact models | epidemiological/CF uncertainty |

### 3.3 Regional climate data: useful, but not a complete independent benchmark

The Danish Regions report a common 2022 hospital/institution climate baseline
of about **3.3 Mt CO2e** and state that the regions buy more than **150,000
products** — confirming that a large procurement data infrastructure exists.
However, regional climate-accounting documentation also shows an important
limitation: purchasing emissions can be calculated using **spend-based
EXIOBASE emission factors**, inflation-adjusted to the relevant year.
Therefore a regional procurement climate account is not equivalent to an
independent physical LCA benchmark. Use it for organisational boundary
checks; expenditure/category totals; identifying major procurement groups;
testing whether national models reproduce the same hotspot ranking; and
obtaining physical data where the regional model uses quantities. Do not use
its spend-based CO2e output as independent confirmation of an EXIOBASE-based
national calculation. Sources:
https://www.regioner.dk/regional-udvikling/groenne-hospitaler/regionernes-klimamaal/
and https://www.niras.dk/media/2u0nyq2c/niras-dk-climate-account-2022.pdf

### 3.4 Medical gases

**Verified.** Region Hovedstaden reports approximately **6,300 t CO2e
annually** from medical gases and distinguishes direct release during
patient care from indirect emissions from production/procurement — gas-specific
accounting exists operationally. **Not yet verified.** A national public
table of year × region × hospital × gas × kg or litres consumed × kg
destroyed/recovered × direct CO2e × upstream CO2e has not been found.
**Preferred solution.** Request the underlying common-regional gas activity
table; if only purchase data are available, $F_g = Q_g \times GWP_g$,
adjusted for wastage, destruction, capture and stock changes. **Fallback.**
Use public regional CO2e totals as bounding values, but do not mix them into
the final national physical calculation without harmonising GWPs and
boundaries. Source:
https://www.regionh.dk/til-fagfolk/Klima-og-miljoe/groen-omstilling-af-hospitalerne/CO2-indsatser-i-koncerncentre/Sider/Medicinske-gasser-destruktion-og-reduktion.aspx

### 3.5 Procurement and medical consumables

The regions state that their hospitals/institutions buy more than 150,000
products; regional climate accounts expose categories such as medicines,
medical articles/equipment, assistive devices, implants, test materials,
chemicals, hygiene items, disposable products, and general goods/services.
Preferred data request: a disclosure-safe annual extract at the finest
harmonised category or SKU level available — year, region,
hospital_or_entity, sku_or_item_id, product_description, supplier,
procurement_category, quantity, unit, spend_dkk, emission_factor,
factor_unit, factor_source, calculation_method, reported_co2e. Why all factor
fields matter: if $\text{reported\_co2e} = \text{spend} \times
\text{EXIOBASE factor}$, that field cannot be used as independent validation
of an EXIOBASE footprint — but quantity, product category, spend, supplier
and organisation remain highly useful independent activity data.

### 3.6 Pharmaceuticals

Use a hierarchy. **Level 1 — open aggregate data:** Medstat, for ATC trends,
candidate pMDIs, and quantity-based sensitivity. **Level 2 — custom aggregate
extract:** the preferred first request to the Danish Health Data Authority,
at grain year × ATC × product_or_package_number ×
hospital_vs_primary_care × region × department_if_disclosable, with measures
packages, DDD, units, quantity, value_dkk. **Level 3 — LSR/LMDB:** use only
if the aggregate extract cannot answer the environmental question. This
follows proportionality and avoids unnecessary person-level data.

### 3.7 Patient and staff travel

**Region-paid patient transport.** Strong operational data appear to exist in
regional climate/transport systems. Preferred extract: year, region,
transport_type, journeys, passenger_km, vehicle_km, fuel_or_energy.
**Self-arranged patient travel.** A defensible model is possible from patient
residence $\rightarrow$ hospital/contact location combined with travel mode
assumptions: $PKM_{o,h,m} = \text{Contacts}_{o,h} \times
\text{Distance}_{o,h} \times \text{ModeShare}_{o,h,m}$, using the National
Patient Register for contact geography and DTU TU for travel behaviour.
**Staff commuting.** Potential design: $\text{EmployeeTrips}_{o,w,m} =
\text{Employees}_{o,w} \times \text{WorkingDays} \times
\text{ModeShare}_{o,w,m}$, using residence-workplace registers plus TU mode
modelling. **Visitor travel.** This remains a genuine gap; recommended
treatment is facility surveys where available, visitor-per-admission
assumptions, low/base/high scenarios, kept as a separate component.

### 3.8 Energy and buildings

Comparatively well covered. Use region/facility meter data where accessible;
Statistics Denmark energy/environmental accounts for national consistency;
construction/GFCF for capital. Avoid double counting when bottom-up facility
energy is added to an IO final-demand model — define
`bottomup_replacement_flag`, `io_flow_removed`, `replacement_quantity`,
`replacement_factor`.

### 3.9 Materials and resources

Denmark's material accounts are strong for national totals but do not
directly answer which raw materials are attributable to healthcare final
demand. Use Danish SUT demand plus MRIO material extensions, cross-modelled
against EXIOBASE and GLORIA. GLORIA is particularly valuable here because it
was explicitly constructed for global resource-flow/material-footprint
analysis.

### 3.10 What remains genuinely unresolved

After deeper searching, the strongest unresolved issues are: (1) the exact
full Danish SUT and its year-specific product metadata; (2) machine-readable
common regional procurement/activity data; (3) national physical gas
consumption by hospital and gas species; (4) visitor travel; (5)
product-level environmental factors for large numbers of medical
devices/consumables; (6) healthcare-specific global material/land/water-
scarcity attribution; (7) uncertainty in mapping SHA expenditure to SUT/MRIO
products. The problem has therefore **not disappeared** — it has shifted from
"data do not exist" to access + classification + independence + boundary
harmonisation, for several high-value datasets.

### 3.11 Data-quality grading

Every source should receive four independent grades: `access_grade`,
`resolution_grade`, `boundary_grade`, `independence_grade`. Example:

| Source | Access | Resolution | Boundary | Independence |
|:---|:---|:---|:---|:---|
| DST SHA1 | A | A | A | A |
| DST full SUT | C until access | A | A | A |
| regional procurement spend CO2e | B | A/B | B | C if EXIOBASE factor |
| regional physical gas quantity | B | A | A | A |
| Eurostat FIGARO footprint | A | B | B | A relative to custom EXIOBASE |
| DST AFFALD | A | A | A | B relative to EPA ADS |
| Eurostat waste | A | C for healthcare detail | B | B relative to Danish reporting |
| visitor travel scenario | A | D | C | C |

This prevents "available" from being confused with "good enough".

---

## 4. Cross-MRIO replication strategy

Which external MRIO databases (EXIOBASE, GLORIA, Eora, OECD ICIO, FIGARO)
should be run for sensitivity, what role does each play, and how is a
cross-MRIO comparison harmonised so that database differences are not
confused with healthcare-boundary differences?

### 4.1 Purpose

The study should distinguish uncertainty from the healthcare boundary from
uncertainty from the MRIO database. A five-MRIO comparison is useful only if
the healthcare demand vector and indicator definitions are harmonised as far
as possible. Recommended systems: EXIOBASE, GLORIA, FIGARO, Eora, OECD ICIO.

### 4.2 Preferred headline system

The primary model should remain: DK detailed SUT + SHA + Danish environmental
accounts + foreign MRIO extension + selected bottom-up replacements. The
MRIO systems then serve different sensitivity functions.

### 4.3 GLORIA

The current UNEP GLORIA interface describes a homogeneous MR-SUT with
1990-2024, 164 regions, 97 industries, 97 commodities, 6 final-demand agents,
6 value-added categories, 5 valuation layers, current thousand USD. GLORIA
was built using IELab infrastructure for the UNEP International Resource
Panel, with specific attention to **resource-flow analysis**. Source:
https://footprint.unep.org/gloria-mrio. GLORIA should be used particularly
for material extraction, resource footprints, country-of-origin resource
dependencies, and comparison of material-intensive healthcare supply chains.
Important version rule: older widely used GLORIA releases have different
sector counts, including 120-sector configurations. Never store `mrio =
GLORIA` alone — store `mrio = GLORIA`, `release`, `sector_schema_version`,
`region_schema_version`, `year`, `projection_status`.

### 4.4 EXIOBASE

Recommended role: **main environmental MRIO sensitivity**. Strengths: high
environmental extension detail; harmonised sector/product structure; water,
land, materials, GHGs and other emissions. Weakness: healthcare service
categories remain coarser than the proposed Danish health taxonomy. Use the
current fixed release selected for the paper and store the release DOI/version.

### 4.5 FIGARO

Recommended role: **official EU economic/GHG benchmark**. Strengths:
Eurostat national-account foundations; trade balancing; Q86 human health
separated from Q87-Q88; C21 pharmaceuticals separate; official Eurostat
FIGARO GHG footprint datasets. Weaknesses: only 64 industries/products;
medical devices and many clinical goods are aggregated.

### 4.6 Eora

Recommended role: **Lenzen replication**. Strength: the Lenzen et al. global
healthcare assessment used Eora, so Eora is the appropriate database for
methodological comparability. Weakness: full Eora uses country-specific
sector classifications, making harmonisation less straightforward. Run both
the native Eora health boundary and a harmonised external healthcare boundary
where practical.

### 4.7 OECD ICIO

Recommended role: **economic trade/value-chain sensitivity**. Strengths:
strong international economic framework; long time series; transparent
sector harmonisation. Weakness: healthcare is broad; environmental
extensions are not as rich as EXIOBASE/GLORIA for the full footprint suite.

### 4.8 Common comparison years

**Headline Danish year: 2022** — final Danish SUT detail exists for final
years; Danish environmental accounts are available; healthcare/medicines data
are available; EXIOBASE/OECD data coverage can be aligned. Statistics Denmark
states that SUTs from 2014 onward are consistent with the latest 2022 table
under the current revision, with previous-year-price consistency from
2015-2022. **Common MRIO benchmark: 2019** — pre-pandemic; broad overlap
across databases; minimises extraordinary health-system/economic
distortions; reduces dependence on projected or nowcast components. Run 2022
as a second benchmark where each database's 2022 economic status is
documented.

### 4.9 Harmonised healthcare demand

Construct one reference health vector $y_H^{\text{common}}$. Map it to each
database as $y_{H,m} = \mathbf{B}_m\,y_H^{\text{common}}$. For each MRIO $m$,
record coverage $= \sum y_{H,m}^{\text{mapped}} / \sum y_H^{\text{common}}$.
No MRIO result should be interpreted without reporting mapping coverage.

### 4.10 Native versus harmonised runs

For each MRIO generate a **native** result (using the database's native
health industry/product definition) and a **harmonised** result (using our
SHA-derived healthcare boundary), then $\text{BoundaryDifference}_m =
F^{\text{harmonised}}_m - F^{\text{native}}_m$. This prevents health-definition
differences from being mistaken for MRIO differences.

### 4.11 Common equations

For database $m$: $\mathbf{A}_m = \mathbf{Z}_m\,\hat{x}_m^{-1}$;
$\mathbf{L}_m = (\mathbf{I} - \mathbf{A}_m)^{-1}$; $q_{k,m} =
\mathbf{Q}_{k,m}\,\hat{x}_m^{-1}$; $F_{k,m} = q_{k,m}\,\mathbf{L}_m\,y_{H,m}$.

### 4.12 Cross-MRIO indicators

Absolute spread: $\text{Range}_k = \max_m F_{k,m} - \min_m F_{k,m}$.
Coefficient of variation: $CV_k = 100\,sd(F_{k,m})/\text{mean}(F_{k,m})$.
Deviation from the Denmark-specific hybrid: $RD_{k,m} = 100\,(F_{k,m} -
F_{k,DK})/F_{k,DK}$. Imported impact: $IS_{k,m} =
100\,F_{\text{foreign},k,m}/F_{k,m}$.

### 4.13 Do not average MRIO results blindly

An arithmetic mean of five databases does not automatically produce a better
footprint. Differences can be structural: trade balancing, product
aggregation, economic year, environmental extension, rest-of-world
construction, import proportionality, healthcare mapping. The preferred
outcome is a central Denmark-specific estimate plus a structured sensitivity
envelope.

### 4.14 Suggested results table

| Indicator | DK hybrid | EXIOBASE | GLORIA | FIGARO | Eora | OECD | spread | interpretation |
|:---|---:|---:|---:|---:|---:|---:|---:|:---|
| GHG | | | | | | | | |
| Water | | | | n/a/limited | | | | |
| Scarce water | | | | n/a | | | | |
| Materials | | | | n/a/limited | | | | |
| Land | | | | n/a/limited | | | | |
| PM | | | | limited | | | | |
| NOx | | | | FIGARO extension if available | | | | |
| SO2 | | | | | | | | |

Only populate cells where the underlying extension is scientifically
comparable.

### 4.15 Final role allocation

| System | Primary use |
|:---|:---|
| DK detailed SUT | high-resolution Danish economic core |
| DK environmental accounts | domestic physical extensions |
| EXIOBASE | broad global environmental sensitivity |
| GLORIA | resource/material sensitivity |
| FIGARO | official EU GHG/trade sensitivity |
| Eora | Lenzen replication |
| OECD ICIO | trade/value-chain sensitivity |

This is a more defensible design than choosing one MRIO and treating it as
ground truth.

### 4.16 Quantitative MRIO comparison

| Database | Main current/relevant structure | Health-sector detail | Environmental strength | Access | Main use here |
|:---|:---|:---|:---|:---|:---|
| EXIOBASE 3.10.2 | 49 regions, 163 industries, 200 products; core economic update through 2022 | broad health/social-work service plus separate goods sectors | very strong GHG, energy, water, land, materials | academic/non-commercial release on Zenodo | preferred environmental MRIO sensitivity |
| GLORIA | release-dependent; current UNEP interface describes 164 regions and 97 industry/commodity sectors; widely used v59 has 120 sectors | broad human health/social work; separate pharmaceutical manufacturing in the 97-sector technical classification | especially strong materials/resources, plus emissions, water, land and social indicators | IELab registration/download; commercial licensing separately | high-country-resolution resource/material sensitivity |
| Eora | full Eora has country-specific sector detail; Eora26 is harmonised 26-sector model | Denmark in Lenzen-era Eora had pharmaceuticals, hospital activities, medical/dental/veterinary activities; detail varies by country | broad global satellite accounts | academic registration/licensing | methodological replication of Lenzen et al. |
| OECD ICIO 2025 | 80 economies + RoW; 50 unique industries; 1995-2022 | one `Q Human health and social work activities` industry | primarily economic/value-chain framework; environmental extensions need external pairing | open downloadable CSV | trade/economic structural sensitivity |
| FIGARO 2026 | 64 industries × 64 products; 2010-2024 | broad NACE/CPA health categories | strong official EU economic/trade consistency; environmental footprint products available separately | open Eurostat CSV/Excel | official EU sensitivity and bridge |

(Carried forward unchanged from the first-pass assessment, because the
narrative sections above do not otherwise put the five candidate databases
side by side with their concrete resolution and access figures.)

### 4.17 Harmonisation protocol

Also carried forward from the first pass, as the explicit step sequence that
sections 4.9-4.10 assume rather than spell out.

**Step 1 — freeze healthcare scope.** Create one common taxonomy, for
example `HC_SERVICES`, `HC_PHARMACEUTICALS`, `HC_MEDICAL_DEVICES`,
`HC_ADMIN_RESEARCH`, `HC_CAPITAL`. Then construct a database-specific
concordance for each MRIO.

**Step 2 — harmonise valuation.** Record basic prices, purchasers' prices,
trade margins, transport margins, taxes/subsidies. Do not compare spend
multipliers with mismatched valuations.

**Step 3 — harmonise currency and price year.** For intensity comparisons
$I_{k,m} = F_{k,m}/E_{H,m}$, all models must use comparable price-year
assumptions.

**Step 4 — harmonise GWP.** Store `gwp_assessment_report`,
`gwp_time_horizon`, `gas_species`. Do not compare AR4-based CO2e directly
with AR6-based CO2e without recalculation or clear labelling.

**Step 5 — separate boundary effects from database effects.** Run two
comparisons: a **native-model result** using each MRIO's native health
structure, and a **harmonised-demand result** using the same externally
constructed healthcare demand concept as far as mappings allow. The second is
the proper **MRIO sensitivity test**.

### 4.18 Cross-MRIO result table schema

The formal schema behind the results table in section 4.14, also carried
forward. Create `fact_mrio_comparison` with fields: `time_key` (reference
year), `mrio_key` (database + release), `impact_key` (GHG, water, materials,
etc.), `health_scope_key` (common health boundary), `price_basis_key`
(price/valuation), `footprint_value` (absolute footprint), `per_capita_value`
(population-normalised), `intensity_per_currency` (environmental intensity),
`domestic_share_pct` (Denmark-produced share), `foreign_share_pct`
(foreign-produced share), `top10_supplier_share_pct` (concentration),
`mapping_coverage_pct` (share of healthcare expenditure mapped),
`mapping_uncertainty_grade` (quality of concordance), `economic_data_status`
(observed/estimated/projected), `notes` (caveats).

---

## 5. Waste benchmarking protocol

How can Danish healthcare waste be triangulated across hospital, EPA,
Statistics Denmark and Eurostat layers without mistaking three dependent
reporting chains for three independent measurements?

### 5.1 Research objective

The waste component should answer at least four distinct questions: (1) how
much waste is generated by Danish healthcare; (2) what kinds of waste are
generated; (3) how is that waste treated; (4) how much upstream waste
throughout the supply chain is caused by healthcare final demand. These
require different datasets. Do not collapse hospital operational waste and
supply-chain waste footprint into one measure.

### 5.2 Recommended four-layer Danish evidence system

**Layer A — hospital and regional operational waste.** Purpose: measure
waste physically generated by healthcare organisations. Examples of publicly
reported regional data include Region Midtjylland 2024: **7,068 t** total
waste, including **413 t clinical risk waste**, with recycling, incineration,
special treatment and landfill breakdowns; other regional
climate/sustainability accounts report waste quantities and treatment
indicators. This is the strongest bottom-up healthcare validation layer.
Preferred extract grain: year, region, hospital, facility_type,
waste_fraction, hazardous_flag, treatment, tonnes, source_system.

**Layer B — Danish EPA Affaldsdatasystemet (ADS).** Purpose: administrative
national waste-flow source. The Danish EPA states that ADS contains raw data
on quantities, waste types, sources, treatment, imports and exports. Public
annual waste statistics include downloadable raw-data files, including for
2022 — a highly valuable open source. Sources:
https://mst.dk/erhverv/groen-produktion-og-affald/affald-og-genanvendelse/affaldshaandtering/affaldsdata-og-affaldsdatasystemet/find-affaldsdata
and
https://mst.dk/erhverv/groen-produktion-og-affald/affald-og-genanvendelse/affaldshaandtering/affaldsdata-og-affaldsdatasystemet/find-affaldsstatistikker-og-kortlaegning

**Layer C — Statistics Denmark Waste Accounts.** Purpose: SEEA-consistent
industry attribution and IO compatibility. Statistics Denmark's waste
accounts allocate waste to the same **117 industries** as the
national/green accounts, publish **32 waste categories**, distinguish
treatment, and include imports/exports. Relevant direct tables: `AFFALD01`
(waste generation by industry and waste category), `AFFALD02` (by industry
and treatment), `AFFALD03` (by industry and hazardousness), `AFFALD04`
(imports/exports). Relevant IO tables include `AFF1MU1N`, `AFF1MU2N`,
`AFF1MU3N`, `AFF2MU1N`, `AFF2MU2N`, `AFF2MU3N`. These allow both direct
healthcare waste and direct-plus-indirect waste caused by final demand.

### 5.3 Critical dependence: EPA ADS and Statistics Denmark are not independent

Statistics Denmark explicitly states that the Waste Accounts are based on
EPA ADS. The processing sequence is approximately: ADS $\rightarrow$ EPA
validation $\rightarrow$ DST industry allocation $\rightarrow$ AFFALD.
Statistics Denmark then allocates residual records without industry activity
codes; approximately **1-2% of total waste annually** is proportionally
distributed in this way, with variation by waste type. **ADS versus AFFALD is
therefore a lineage/reconciliation comparison, not an independent validation
test.** This is scientifically important and should be stated explicitly in
the paper.

### 5.4 Why ADS is still valuable

ADS lets us investigate what happens before Statistics Denmark: source
categories, treatment, reporting patterns, potentially more detailed waste
origins, raw-data structure. AFFALD tells us what happens after the waste is
transformed into 117-industry SEEA-compatible accounts. The difference
between them is itself methodologically informative.

### 5.5 Eurostat waste data

Eurostat waste statistics provide harmonised country reporting by waste
category, hazardousness, economic activity aggregates, and treatment. Use the
Waste Statistics Regulation datasets, including `env_wasgen`. Important
limitation: the European waste reporting activity aggregation is **coarser
than Denmark's 117-industry Waste Accounts**; do not assume Eurostat exposes
a healthcare industry at the same granularity as DST's Q86-type
national-account industries for every waste table. Eurostat is best used for
national/cross-country benchmarking, hazardous/non-hazardous composition,
waste intensity by broad service sectors where available, and total waste and
treatment consistency — not as a replacement for AFFALD for detailed Danish
healthcare attribution.

### 5.6 Eurostat is not fully independent of Denmark either

Denmark's national administrative waste reporting feeds Danish EPA
$\rightarrow$ national statistics $\rightarrow$ EU reporting. Thus EPA,
Statistics Denmark and Eurostat form a **statistical chain**. The correct
framing:

| Comparison | Meaning |
|:---|:---|
| ADS vs AFFALD | national processing/reconciliation |
| AFFALD vs Eurostat | harmonisation/aggregation |
| regional hospitals vs AFFALD | operational-to-national validation |
| Danish hospitals vs NHS ERIC | independent international operational comparison |

### 5.7 Independent international hospital benchmark: NHS ERIC

NHS England's Estates Returns Information Collection (ERIC) is an official
annual collection for NHS organisations providing secondary care. The
2024/25 release provides open trust-level CSV, site-level CSV, data
definitions and reports — a genuinely useful independent operational
comparator. Source:
https://digital.nhs.uk/data-and-information/publications/statistical/estates-returns-information-collection/summary-page-and-dataset-for-eric-2024-25.
Do not compare raw tonnes without normalisation: preferred indicators are kg
waste per occupied bed day, kg clinical waste per admission, kg waste per
1,000 outpatient contacts, kg waste per m², and kg waste per million DKK
healthcare activity, depending on denominator availability.

### 5.8 Proposed waste fact tables

`fact_operational_waste`, at grain year × facility × waste fraction ×
treatment, with fields `time_key`, `geography_key`, `provider_key`,
`facility_key`, `waste_key`, `treatment_key`, `tonnes`, `hazardous_flag`,
`source_key`, `measurement_method`, `quality_flag`.

`fact_waste_footprint`, at grain year × healthcare demand × producer
industry × waste fraction, with fields `time_key`, `health_function_key`,
`industry_key`, `waste_key`, `scenario_key`, `direct_tonnes`,
`indirect_tonnes`, `total_tonnes`, `share_pct`. Do not merge the two.

### 5.9 Waste and treatment dimensions

`dim_waste`: `waste_key`, `dst_fraction_code`, `dst_fraction_label_da`,
`dst_fraction_label_en`, `ewc_stat_code`, `ewc_code`, `hazardous_flag`,
`clinical_risk_flag`, `pharmaceutical_waste_flag`, `infectious_flag`,
`material_group`.

`dim_treatment`: `treatment_key`, `treatment_code`, `treatment_name`,
`recycling_flag`, `energy_recovery_flag`, `incineration_flag`,
`landfill_flag`, `special_treatment_flag`, `temporary_storage_flag`.

### 5.10 Boundary reconciliation

For each dataset store: `hospital_only`, `regional_administration`,
`primary_care`, `psychiatry`, `social_care`, `construction_waste`, `soil`,
`wastewater_sludge`, `outsourced_services`, `pharmaceutical_returns`,
`household_like_waste`. Comparison then becomes $W^A_{\text{comparable}} =
W^A - W^A_{\text{excluded}} + W^A_{\text{missing adjustment}}$, rather than
comparing headline numbers blindly.

### 5.11 Recommended 2022 benchmark exercise

2022 is attractive because EPA publishes revised 2022 waste statistics and
raw-data files; Statistics Denmark has 2022 Waste Accounts; it aligns with
the main proposed healthcare footprint year; and FIGARO/EXIOBASE and other
systems can be tested near the same year. Steps: (1) download EPA 2022 waste
raw data; (2) download AFFALD01, AFFALD02, AFFALD03, relevant AFF*MU* tables;
(3) identify the Danish health industries and final-demand health category;
(4) reconcile EPA source classifications to DST 117 industries where
possible; (5) collect 2022 or nearest-year hospital/region physical waste;
(6) extract Eurostat Denmark waste statistics; (7) construct comparable
indicators.

### 5.12 Validation statistics

For source $s$: $\text{Difference}_s = W_s - W_{\text{reference}}$;
$\text{RelativeDifference}_s = 100\,(W_s - W_{\text{reference}})/W_{\text{reference}}$.
For category $c$: $\text{Share}_c = 100\,W_c/W_{\text{total}}$. Treatment
rate: $\text{RecyclingRate} = 100\,W_{\text{recycling}}/W_{\text{total}}$.
Clinical-risk intensity: $CRI = W_{\text{clinical risk}}/\text{hospital
activity}$.

### 5.13 Recommended evidence hierarchy for waste

**Healthcare operations:** (1) facility/region measured waste; (2) EPA
administrative reports/raw data; (3) DST Waste Accounts. **Economy-wide
supply-chain waste:** (1) DST IO waste multipliers; (2) custom Danish
$q\,\mathbf{L}\,y_H$ waste model; (3) MRIO waste extension where available.
**International operational comparison:** (1) NHS ERIC; (2) comparable
hospital networks with published methods. **Cross-country national
comparison:** (1) Eurostat.

### 5.14 Main methodological caution

Do not write "the Danish result was validated independently against EPA,
Statistics Denmark and Eurostat" — that would overstate independence. Write
instead: "the estimate was triangulated across facility-level operational
data and the Danish administrative/statistical waste-accounting chain, with
Eurostat used to test international harmonisation and NHS ERIC as an
external operational benchmark." That is the scientifically defensible
formulation.

---

## 6. FIGARO feasibility and test plan

Is FIGARO detailed enough to justify its own replication and sensitivity
exercise, and if so, what is the concrete test sequence?

### 6.1 Verdict

**FIGARO should be explored empirically.** It is **not** sufficiently
detailed to replace the Danish working-level SUT, but it is a stronger
healthcare benchmark than previously assumed. The current 2026 FIGARO
edition provides 64 industries, 64 products, 2010-2024, supply tables, use
tables, industry-by-industry inter-country IOTs, product-by-product
inter-country IOTs, direct purchases abroad, and CSV flat and matrix files.
Official source: https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/database

### 6.2 Why FIGARO is particularly valuable

FIGARO provides something unusual: official EU national accounts, plus
international trade balancing, plus Eurostat environmental accounts, plus
published GHG footprint results. This lets us test both our matrix
implementation and our healthcare mapping.

### 6.3 Healthcare resolution is better than "health and social work"

At the A64 classification used in FIGARO, relevant categories include
separate **Q86 Human health activities** and **Q87-Q88 Residential care and
social work activities** — healthcare can be separated from broad
residential/social-care activities at the principal service-industry level.
Pharmaceutical manufacturing is also separately represented under **C21
Manufacture of basic pharmaceutical products and pharmaceutical
preparations**. However, FIGARO remains coarse for other healthcare supply
chains: medical/dental instruments fall within broader manufacturing groups;
electromedical/electronic equipment shares broader C26 categories; diagnostic
supplies may sit in mixed chemical/manufacturing product groups; individual
clinical services are not resolved. So FIGARO health resolution is better
than one broad health/social sector, but coarser than the full Danish SUT +
SHA.

### 6.4 Eurostat already publishes FIGARO GHG footprints

Eurostat publishes seven FIGARO environmental-footprint datasets:
`env_ac_ghgfp`, `env_ac_co2fp`, `env_ac_ch4fp`, `env_ac_n2ofp`,
`env_ac_hfcfp`, `env_ac_pfcfp`, `env_ac_nf3sf6fp`. The estimates use FIGARO
inter-country IOTs, European air-emissions accounts, Eurostat estimates for
non-European regions, and Leontief input-output modelling; the datasets
provide origin and destination geography and final-demand attribution.
Official metadata: https://ec.europa.eu/eurostat/cache/metadata/en/env_ac_ghgfp_esms.htm.
This creates a powerful implementation benchmark.

### 6.5 The correct first test is not healthcare

Before interpreting healthcare results, reproduce a published Eurostat
footprint.

**Test F0 — structural accounting.** For the selected FIGARO 2022 I-I table,
$x = \mathbf{Z}\mathbf{1} + \mathbf{Y}\mathbf{1}$. Construct $\mathbf{A} =
\mathbf{Z}\,\hat{x}^{-1}$ and $\mathbf{L} = (\mathbf{I} - \mathbf{A})^{-1}$.
Checks: dimensions; country-sector ordering; row/column orientation;
currency/unit; total output reconciliation; zero-output handling;
final-demand sums.

**Test F1 — environmental extension reproduction.** Obtain the relevant
Eurostat air-emissions extension and calculate $q = \mathbf{Q}\,\hat{x}^{-1}$,
then $F = q\,\mathbf{L}\,\mathbf{Y}$. Reproduce at least one published
country/final-demand GHG result. Acceptance rule: $\left|(F^{\text{ours}} -
F^{\text{Eurostat}})/F^{\text{Eurostat}}\right| < \epsilon$, where $\epsilon$
is set after accounting for rounding, reference-year and extension-treatment
differences. Do **not** proceed to healthcare interpretation until this test
is passed or the residual is explained.

**Test F2 — Denmark native healthcare boundary.** Run $y_{H1} = $ native
FIGARO final demand associated with Q86/health-related products, only after
clarifying what is actually represented in FIGARO final demand. Important: do
not simply use the output of the Q86 producing industry as healthcare final
demand — the demand vector must reflect who ultimately consumes the relevant
products/services. Store this as a deliberately coarse baseline,
`FIGARO_NATIVE_Q86`.

**Test F3 — harmonised SHA healthcare demand.** Preferred FIGARO experiment:
SHA $\rightarrow$ CPA/A64 $\rightarrow$ FIGARO final demand. Construct a
bridge `bridge_sha_figaro` with fields `sha_hc`, `sha_hp`, `figaro_product`,
`figaro_industry`, `weight`, `weight_basis`, `confidence`. Then
$F^{\text{FIGARO}}_{\text{SHA}} = q\,\mathbf{L}\,y_{H,\text{SHA}}$. This is
the result that should be compared with the detailed Denmark hybrid.

### 6.6 Do not add C21 pharmaceutical output mechanically

Pharmaceutical manufacturing is an upstream industry, not automatically a
separate final-demand component of healthcare. Potential double counting
arises if one adds Q86 final demand plus C21 industry output, because
pharmaceuticals may already enter final demand or health-service
intermediate inputs. Pharmaceutical expenditure should instead be mapped
explicitly from SHA/health expenditure to relevant FIGARO products. This same
rule applies to medical equipment.

### 6.7 Test F4: compare three healthcare definitions

Run **H1** (native FIGARO broad healthcare definition), **H2** (SHA-mapped
health services only), and **H3** (full SHA-mapped healthcare including
pharmaceuticals and medical goods). Then $\text{BoundaryEffect} = F_{H3} -
F_{H1}$, quantifying how much of the result changes simply because the
healthcare boundary is more complete.

### 6.8 Test F5: compare against Danish official IO footprint tables

For Denmark 2022, compare FIGARO results with DST `EMM1MU2N`, `EMM1MU3N` and
`AFTRYK1`. Questions: (1) is the absolute GHG footprint comparable; (2) is
the domestic/foreign share comparable; (3) are upstream hotspot industries
similar; (4) which countries dominate foreign impacts; (5) are discrepancies
traceable to boundary or economic structure?

### 6.9 Test F6: gas-species decomposition

Use the Eurostat FIGARO gas-specific footprint datasets to construct
$F_{CO_2}$, $F_{CH_4}$, $F_{N_2O}$, $F_{HFC}$, $F_{PFC}$, $F_{NF_3/SF_6}$,
then $\text{Share}_g = 100\,F_g/F_{GHG}$. Compare with Danish direct gas
accounts, EXIOBASE, and Lenzen/Eora species composition. This makes FIGARO
particularly useful for the gas-species KPI.

### 6.10 Test F7: geography

FIGARO footprints distinguish origin and destination geographies. Compute
$\text{DomesticShare} = 100\,F_{\text{origin}=DK}/F_{\text{total}}$;
$\text{EUForeignShare} = 100\,\sum_{r \in EU, r \neq DK} F_r / F_{\text{total}}$;
$\text{NonEUShare} = 100 - \text{DomesticShare} - \text{EUForeignShare}$.
Compare against AFTRYK1 and EXIOBASE.

### 6.11 FIGARO versus the Danish detailed SUT

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

### 6.12 FIGARO uncertainty and interpretation

Eurostat notes that international tables require modelling assumptions to
reconcile trade asymmetries and advises caution at detailed level. Store
`figaro_release`, `reference_year`, `economic_table_version`,
`environmental_extension_version`, `observed_estimated_flag`. Do not treat
FIGARO as "official truth" merely because Eurostat publishes it — it is an
official, harmonised **modelled** inter-country system.

### 6.13 Decision criteria after the proof of concept

Retain FIGARO as a major paper benchmark if: (1) our implementation
reproduces Eurostat footprints; (2) Denmark healthcare demand can be mapped
without excessive unmapped expenditure; (3) Q86/C21 and associated products
capture enough of the healthcare boundary for meaningful sensitivity; (4)
geographic results are interpretable; (5) the healthcare result adds
information beyond AFTRYK1. Suggested thresholds: mapping coverage $=
100\,\text{MappedHealthExpenditure}/\text{TotalHealthExpenditure} \ge 95\%$;
unexplained reconciliation residual below 1% where units/reference years permit.

### 6.14 Recommended FIGARO result package

`fact_figaro_healthcare`, with fields `year`, `figaro_release`,
`health_boundary`, `final_demand_category`, `producer_country`,
`producer_industry`, `consuming_country`, `impact`, `footprint_value`,
`unit`, `domestic_foreign_flag`, `health_expenditure_mapped`,
`mapping_coverage`, `mapping_confidence`.

### 6.15 Bottom line

FIGARO is not a substitute for the detailed Danish model. Its scientific role
is stronger: an **official EU cross-border accounting benchmark**, with an
unusually valuable ability to reproduce and cross-check Eurostat's own GHG
footprint calculations. A FIGARO proof of concept should therefore occur
**before** the final MRIO selection is frozen.

---

## 7. Statistics Denmark contact and acquisition plan

Exactly what should be requested from Statistics Denmark, from whom, in what
order, and what should proceed in the meantime while that request is
outstanding?

### 7.1 What should be requested

The enquiry should no longer ask only for "the SUT". It should ask Statistics
Denmark to clarify access to **four distinct objects**: (1) full 2019 and
2022 SUT numerical tables; (2) year-specific ~2,350-product code list; (3)
Danish/English descriptions and HS/CPA concordance; (4) domestic/import and
valuation matrices. This is important because product metadata may be
deliverable even if numerical cells have confidentiality restrictions.

### 7.2 Why the first contact should still be Peter Rørmose Jensen

Statistics Denmark identifies **Peter Rørmose Jensen** (National Accounts,
Climate and Environment, Economic Statistics; email `prj@dst.dk`; phone +45
40 13 51 26) as the SUT/IOT subject-matter contact. Official pages:
https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use
and https://www.dst.dk/en/Statistik/emner/oekonomi/nationalregnskab/input-output.
The public documentation shows two plausible non-public routes: customised
paid national-accounts extracts, or Research Services access to full SUTs.
The subject-matter statistician should confirm which route fits the project
**before** a formal Research Services data order is prepared.

### 7.3 Exact first email, under 100 words

**Subject:** Detailed Danish SUT and product classification for research

> Dear Peter,
>
> I am a researcher at SDU developing a reproducible environmental
> input-output assessment of Danish healthcare. I have found the public
> Eurostat A64/A88 SUTs and Statistics Denmark's 117-industry IOT, but need
> the working-level product detail. Could you confirm access to the 2019 and
> 2022 SUTs (about 2,350 products × 117 industries), including domestic/import
> use and valuation matrices, and whether the year-specific product-code
> list, Danish/English labels, and HS/CPA concordance can be supplied? Please
> advise the appropriate access route, costs, and required materials.
>
> Best regards,
> Albert Osei-Owusu

The body is **86 words** under a conventional tokenised word count.

### 7.4 Why this email is stronger

It demonstrates that the public Eurostat A64/A88 tables, the public
117-industry Danish IOT, and the need for working-level product detail have
all already been identified. It also does not prematurely assume whether the
appropriate route is free metadata, a paid bespoke extract, or Research
Services.

### 7.5 Materials to prepare, but not attach unless requested

**A. One-page project brief.** Title: *Environmental footprint of the Danish
healthcare system: a Denmark-specific hybrid EEIO/MRIO assessment*. The
drafted brief is [section 8](#8-sut-request-brief) below. It covers
institution (SDU), objective, why public tables are insufficient, target
years, data requested, model equations, intended outputs, the absence of any
personal-data need, and the publication/reproducibility goal.

**B. Exact data specification.** Supply: product × industry domestic output;
imports by product; basic-price supply; valuation bridge. Use: product ×
industry intermediate use; household consumption; government consumption;
NPISH; GFCF; inventories; exports. Prefer if available: use of domestic
output at basic prices; use of imports at basic prices; trade margins;
transport margins; taxes; subsidies; VAT. Metadata: product code; label_da;
label_en; HS/CN mapping; CPA mapping; industry code; classification version;
structural/suppression flag; revision ID; price basis; unit.

### 7.6 Why request 2019 and 2022

**2022** is the preferred main study year: Statistics Denmark states that
the fully detailed final SUT uses approximately 2,350 products and that the
currently documented final 2022 SUT forms part of the consistent post-2014
series. **2019** is the preferred cross-MRIO pre-pandemic benchmark.
Requesting only two years reduces cost, supports data minimisation, and makes
the access case easier to justify.

### 7.7 If Peter offers a paid custom extract instead of full Research Services access

Ask for a quotation for two products. **Product A — metadata package:** 2019
and 2022 product code lists, labels, HS/CPA concordance, A64/A88 parent
mapping. **Product B — health-relevant numerical extract:** if the full SUT
is expensive or restricted, request all rows corresponding to healthcare
candidate products, their supply, their intermediate/final use, import/
domestic split, and valuation components. **Caution:** a health-only row
extract may be insufficient for constructing the full Leontief inverse — if
we need to calculate $\mathbf{L} = (\mathbf{I} - \mathbf{A})^{-1}$ at
2,350-product detail, we need a complete economic system, not only selected
health rows. A health-only extract is useful for disaggregation/concordance,
but it does **not** replace full SUT access for high-resolution IO modelling.

### 7.8 If Research Services is required

Then determine: (1) whether the relevant SDU environment is already
authorised; (2) who manages Statistics Denmark research access at SDU; (3)
whether SUT access uses the normal Denmark's Data Portal workflow or a
special national-accounts arrangement; (4) price and expected processing
time; (5) output-control rules. Do not create a generic register-data
application until DST confirms the SUT ordering path.

### 7.9 Free fallbacks to acquire regardless

**Denmark:** 117-industry IOT. **Eurostat:** annual A64 SUT; inspect A88
availability for Denmark/year; FIGARO 64×64. Important A88 qualification:
Eurostat first published 88-product/88-industry detailed SUTs in 2025 based
on **voluntary country transmissions** — do not state that Denmark 2019 or
2022 A88 is available until the actual country/year cells are checked.

### 7.10 Follow-up questions if Peter replies positively

(1) Are 2019 and 2022 available at the full product resolution? (2) Are they
on the same revision/classification basis? (3) Can the year-specific product
dimension be supplied as a separate metadata file? (4) Are English labels
maintained? (5) What is the exact mapping to HS/CN and CPA? (6) Can domestic
and imported use be supplied separately? (7) Are margin/tax matrices
available annually or only benchmark years? (8) Are basic-price use tables
available for 2019/2022? (9) Are numerical cells subject to disclosure
restrictions? (10) Can the full SUT be used programmatically inside a secure
research environment? (11) Can derived aggregate matrices/multipliers be
exported? (12) What costs and lead times apply?

### 7.11 Decision tree

```text
Email Peter
   |
   +-- exact product metadata can be supplied openly/cheaply
   |      -> acquire immediately
   |
   +-- selected detailed balances available as paid extract
   |      -> assess usefulness/cost
   |
   +-- full SUT requires Research Services
   |      -> initiate SDU institutional route
   |
   +-- full SUT unavailable
          -> Eurostat A88/A64 + 117-IOT + SHA + procurement hybrid
```

### 7.12 What can proceed while waiting

Do not pause the project. Build immediately: SHA1 + 117-industry IOT +
Danish environmental accounts. In parallel: build the public bilingual
HS/CPA health-product candidate universe; test FIGARO; acquire
EXIOBASE/GLORIA/Eora/OECD; develop the star schema. The detailed SUT should
drop into an architecture that already works.

### 7.13 Ready answers if Peter asks what the data are for

Carried forward from the first-pass assessment: prepared wording for the
questions a subject-matter contact is likely to ask before confirming a
route.

**Research purpose.** "The purpose is to construct a Denmark-specific
environmentally extended input-output model of healthcare. Health
expenditure from the System of Health Accounts will be mapped to detailed
Danish products and industries, combined with Statistics Denmark
environmental accounts, and linked to global MRIO databases for imported
supply chains."

**Why the 117-industry IOT is insufficient.** "The 117-industry IOT is
sufficient for model development but aggregates product detail needed to
distinguish pharmaceuticals, medical devices, clinical supplies and service
inputs. The working-level SUT would allow the healthcare final-demand
mapping to be based on Danish product structure rather than broad MRIO
sector proxies."

**Why 2019 and 2022.** "2022 is the preferred main reference year because
current Danish environmental accounts and recent MRIO systems can be aligned
to it. 2019 is requested as a pre-pandemic common benchmark for cross-MRIO
sensitivity analysis."

**Why domestic/import split.** "The study will use Danish environmental
extensions for domestic production and external MRIO extensions for foreign
production. A domestic/import split is therefore required to avoid applying
Danish production intensities to imported products."

---

## 8. SUT request brief

The drafted one-page project brief referenced by [section 7](#7-statistics-denmark-contact-and-acquisition-plan),
ready to attach once the subject-matter contact confirms a route.

**Project title.** *Environmental footprint of the Danish healthcare system: a
Denmark-specific hybrid EEIO/MRIO assessment.*

**Institution.** University of Southern Denmark (SDU).

**Purpose.** The project will quantify the direct and supply-chain
environmental footprints of Danish healthcare using Danish national accounts,
health expenditure and environmental-economic accounts. The aim is to
identify the healthcare functions, products, industries and domestic/foreign
supply-chain nodes responsible for greenhouse-gas emissions, air pollution,
water use, waste and resource use.

**Why the detailed SUT is required.** The public 117-industry Danish IOT and
Eurostat A64/A88 SUTs are suitable for aggregate IO analysis but do not
retain enough Danish product detail for a robust healthcare concordance. The
working-level Danish SUT of approximately 2,350 products × 117 industries
would allow health expenditure from the System of Health Accounts to be
allocated to Danish products and industries before aggregation, reducing
dependence on broad MRIO sector proxies for pharmaceuticals, medical
devices, clinical supplies and health services.

**Requested reference years.** (1) **2022** — preferred main Denmark
reference year. (2) **2019** — common pre-pandemic benchmark for sensitivity
across multiple MRIO databases. If both years are not available on a
comparable revision basis, advice on the closest consistent pair would be
appreciated.

**Requested tables**, subject to availability and disclosure rules. Supply
table: domestic output by product × industry; imports by product;
basic-price supply; transformation to purchasers' prices. Use table:
intermediate use by product × industry; household final consumption;
government final consumption; NPISH; gross fixed capital formation; changes
in inventories; exports. Separate valuation/use components where available:
use of domestic output at basic prices; use of imports at basic prices; trade
margins; transport margins; taxes on products; subsidies on products; VAT.

**Requested metadata.** Complete product code list and labels; complete
industry code list and labels; classification/concordance documentation;
monetary unit and price basis; revision/version identifier; balancing
methodology; confidentiality/suppression flags; guidance on linking the
tables to Statistics Denmark environmental accounts.

**Planned analysis.** The tables will be used to construct $\mathbf{A} =
\mathbf{Z}\,\hat{x}^{-1}$, $\mathbf{L} = (\mathbf{I} - \mathbf{A})^{-1}$, and
healthcare footprints $F = q\,\mathbf{L}\,y_H$. Domestic production will be
combined with Statistics Denmark environmental accounts. Imported demand
will be linked to global MRIO systems including EXIOBASE, GLORIA, Eora, OECD
ICIO and FIGARO.

**Data protection and minimisation.** The request concerns aggregated
national economic tables. No person-level records, CPR numbers or patient
microdata are required. The initial request is limited to two reference
years to minimise the data volume while supporting the main national
estimate and cross-MRIO sensitivity analysis.

**Intended outputs.** Peer-reviewed methodological and empirical research;
reproducible healthcare environmental-footprint indicators; documented
sector/product concordances; aggregate results only; no attempt to identify
confidential enterprises.

**Preferred access outcome.** Access to the most detailed balanced SUT
available to external academic researchers. If full working-level access is
not feasible, advice is requested on the most detailed disclosure-safe
alternative, including whether Denmark's A88 Eurostat tables are available
for 2019 and/or 2022.

---

## 9. Data acquisition register

Dataset-by-dataset tracking: provider, access class, years, target table and
next action for every source named in the sections above. Status codes:
`READY_DOWNLOAD`, `VERIFY_DOWNLOAD`, `CONTACT_SENT`, `REQUEST_REQUIRED`,
`CONTROLLED_ACCESS`, `ACQUIRED`, `DEFERRED`.

| ID | Dataset | Provider | Access | Main years | Resolution / key variables | Model role | Target table | Next action |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| DK_ECON_001 | Full working SUT | Statistics Denmark | CONTROLLED | 2019, 2022 requested | ~2,350 products × 117 industries | domestic economic backbone | `fact_io_flow` | Email Peter Rørmose Jensen |
| DK_ECON_002 | 117-industry IOT / NAIO1-4 | Statistics Denmark | OPEN | current historical series | 117 industries | prototype domestic IO | `fact_io_flow` | Download now |
| EU_ECON_001 | National SUT T1500/T1600 | Eurostat | OPEN | 2010 onward | A64; voluntary A88 | open SUT fallback | `fact_io_flow` | Download Denmark 2019/2022 |
| EU_ECON_002 | FIGARO 2026 | Eurostat | OPEN | 2010-2024 | 64 industries × 64 products | EU MRIO sensitivity | `fact_mrio_comparison` | Download 2019/2022 |
| DK_HEALTH_001 | SHA1 | Statistics Denmark | OPEN | 2010 onward | HC × HP × HF expenditure | healthcare boundary | `fact_health_expenditure` | Download now |
| DK_GHG_001 | DRIVHUS | Statistics Denmark | OPEN | 1990-2024 | industry × GHG | domestic GHG extension | `fact_environmental_extension` | Download 2019/2022 |
| DK_GHG_002 | DRIVHUS2 | Statistics Denmark | OPEN | current series | direct + allocated energy emissions | direct/energy decomposition | `fact_ghg_species` | Download |
| DK_AIR_001 | MRU1 | Statistics Denmark | OPEN | 1990-2024 | industry × pollutant | air-pollution extension | `fact_environmental_extension` | Download 2019/2022 |
| DK_AIR_002 | EMM1MU2N | Statistics Denmark | OPEN | 1990-2024 | final demand × pollutant × multiplier | IO validation | `fact_footprint_total` | Download 2019/2022 |
| DK_AIR_003 | EMM1MU3N | Statistics Denmark | OPEN | 1990-2024 | producer industry × pollutant × final demand | supplier validation | `fact_supplier_footprint` | Download 2019/2022 |
| DK_WATER_001 | VANDRG2 | Statistics Denmark | OPEN | 2010-2024 | industry × water type | direct water extension | `fact_environmental_extension` | Download |
| DK_WATER_002 | VAN2MU2N | Statistics Denmark | OPEN | 2010-2024 | final demand × direct/indirect water | water IO validation | `fact_footprint_total` | Download |
| DK_WASTE_001 | AFFALD | Statistics Denmark | OPEN | 2011-2023 | industry × waste × treatment | waste extension | `fact_environmental_extension` | Download 2019/2022 |
| DK_WASTE_002 | AFF1MU2N | Statistics Denmark | OPEN | 2011-2023 | final demand × waste × multiplier | waste validation | `fact_footprint_total` | Download |
| DK_WASTE_003 | AFF1MU3N | Statistics Denmark | OPEN | 2011-2023 | producer industry × waste × cause | waste supplier hotspots | `fact_supplier_footprint` | Download |
| DK_MAT_001 | MRM2 | Statistics Denmark | OPEN | 1993-2024 | material categories | national material benchmark | `fact_environmental_extension` | Download |
| DK_MAT_002 | RME1 | Statistics Denmark | OPEN | 2008-2024 | raw material equivalents | resource-footprint denominator | `fact_national_share` | Download |
| DK_LAND_001 | AREALAN1 | Statistics Denmark | OPEN | limited | broad industry × land | domestic land check | `fact_environmental_extension` | Low priority |
| DK_CF_001 | AFTRYK1 | Statistics Denmark | OPEN | 1990-2024 | final use × emitting industry × country | consumption GHG/geography validation | `fact_geographic_footprint` | Download |
| DK_PHARMA_001 | Medstat | Danish Health Data Authority | OPEN | historical/current | ATC/product aggregates | exploratory pharma | `fact_bottomup_source` | Inspect/export relevant pMDIs |
| DK_PHARMA_002 | Custom aggregate medicine extract | Danish Health Data Authority | REQUEST | 2019, 2022 | ATC × product × provider × quantity/value | pharma/pMDI hybrid | `fact_bottomup_source` | Draft request |
| DK_PHARMA_003 | LSR / LMDB | Health Data Authority / Statistics Denmark | CONTROLLED | long series | detailed sales/delivery | advanced pharma | `fact_bottomup_source` | Use only if aggregate extract insufficient |
| DK_PHARMA_004 | Hospital procurement | Amgros | REQUEST | 2019, 2022 | products, quantities, values | validation/procurement | `fact_bottomup_source` | Contact after gap analysis |
| DK_TRAVEL_001 | TU | DTU | OPEN/REQUEST | 2006-2025 | mode × purpose × distance | travel model | `fact_bottomup_source` | Determine healthcare-purpose coverage |
| DK_GAS_001 | Anaesthetic gas procurement/use | Regions/hospitals | REQUEST | 2019, 2022 | gas × hospital × quantity | direct clinical GHG | `fact_bottomup_source` | Targeted investigation |
| MRIO_001 | EXIOBASE 3.10.2 | EXIOBASE consortium | MRIO | 2019, 2022 | 49 regions; 163 industries; 200 products | main environmental MRIO sensitivity | `fact_mrio_comparison` | Download/cite fixed DOI |
| MRIO_002 | GLORIA | IELab / UNEP IRP | MRIO | 2019 preferred | release-dependent 97/120 sectors; 164 regions | resource/material MRIO sensitivity | `fact_mrio_comparison` | Register and freeze exact release |
| MRIO_003 | Eora | University of Sydney | MRIO | 2019; Lenzen comparison | full country-specific classification | Lenzen replication | `fact_mrio_comparison` | Obtain academic access |
| MRIO_004 | OECD ICIO 2025 | OECD | OPEN | 1995-2022 | 80 economies + RoW; 50 industries | trade-structure sensitivity | `fact_mrio_comparison` | Download 2019/2022 |
| MRIO_005 | FIGARO 2026 | Eurostat | OPEN | 2010-2024 | 64 × 64 | EU sensitivity | `fact_mrio_comparison` | Download |

### 9.1 Source registry fields to store

Every acquired dataset should create one row in `dim_source` containing:
`source_key`, `provider`, `dataset_code`, `dataset_name`, `access_class`,
`access_route`, `source_url`, `license_or_terms`, `reference_year`,
`release_version`, `download_date`, `raw_redistributable`,
`application_required`, `application_status`, `data_controller`,
`target_fact_or_bridge`, `quality_notes`. For MRIO data additionally store
`mrio_release`, `sector_schema_version`, `region_schema_version`,
`economic_data_status`, `environmental_extension_version`, `gwp_version`.
For controlled data additionally store `project_number`, `allowed_users`,
`output_control_rules`, `expiry_date`, `raw_export_allowed`.

### 9.2 Immediate acquisition sprint

**Sprint 1 — open Danish backbone.** Acquire NAIO1-4; SHA1; DRIVHUS; MRU1;
EMM1MU2N; EMM1MU3N; VANDRG2; VAN2MU2N; AFFALD; AFF1MU2N; AFF1MU3N; MRM2; RME1;
AFTRYK1.

**Sprint 2 — open international benchmarks.** Acquire Eurostat national SUT;
FIGARO; EXIOBASE 3.10.2; OECD ICIO.

**Sprint 3 — access requests.** Send the detailed SUT enquiry, the
pharmaceutical aggregate-data enquiry, and the TU detailed-extract enquiry.

**Sprint 4 — MRIO sensitivity.** Acquire/activate GLORIA and Eora. Freeze
all version metadata before calculation.

---

## 10. Evidence and source register

Claim-by-claim verification: which specific statements about the sources
above are confirmed against an official citation, which are inference, and
which are still open questions. This register distinguishes verified
institutional claims, methodological inference, and unresolved questions,
and should be maintained alongside the data warehouse.

### 10.1 Statistics Denmark SUT evidence

| Claim | Status | Official source |
|:---|:---|:---|
| Final SUT works with approx. 2,350 products | Verified | https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/statistical-presentation |
| Final SUT uses 117 industries | Verified | same |
| product count varies by year | Verified | same |
| full detailed SUT not publicly published due to confidentiality | Verified | https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/relevance |
| some external users receive full SUT via Research Services | Verified | same |
| detailed product balances can be purchased as customised data | Verified | https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--annual/accessibility-and-clarity |
| exact public downloadable 2,350-code list exists | **Not verified** | request from DST |
| DST maintains English labels for every national product code | **Not verified** | request from DST |
| exact year-specific HS/CPA concordance can be released | **Not verified** | request from DST |

### 10.2 Eurostat SUT evidence

| Claim | Status | Source |
|:---|:---|:---|
| mandatory annual national SUT uses 64 activities/products | Verified | https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/information-data |
| countries may voluntarily send A88 | Verified | same |
| Eurostat first published detailed A88 SUT/IOT in 2025 | Verified | https://ec.europa.eu/eurostat/en/web/products-eurostat-news/w/wdn-20250627-1 |
| A88 data are based on voluntary transmissions | Verified | same |
| Denmark 2022 A88 definitely exists | **Not yet verified** | check database before claiming |

### 10.3 FIGARO evidence

| Claim | Status | Source |
|:---|:---|:---|
| 2026 FIGARO covers 2010-2024 | Verified | https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/database |
| 64 industries and 64 products | Verified | same |
| supply/use/I-I/P-P/direct purchases abroad available | Verified | same |
| Eurostat publishes FIGARO-based GHG footprint datasets | Verified | https://ec.europa.eu/eurostat/cache/metadata/en/env_ac_ghgfp_esms.htm |
| GHG footprint uses FIGARO + air-emission accounts + Leontief modelling | Verified | same |
| gas-specific datasets exist | Verified | same |
| FIGARO can replace detailed Danish SUT | Rejected | resolution too coarse for intended health disaggregation |

### 10.4 GLORIA evidence

| Claim | Status | Source |
|:---|:---|:---|
| built for UNEP IRP resource analysis | Verified | https://footprint.unep.org/gloria-mrio |
| current interface covers 1990-2024 | Verified | same |
| 164 regions | Verified | same |
| 97 industries and 97 commodities in current interface | Verified | same |
| 5 valuation layers | Verified | same |
| older releases may use different sector counts | Verified conceptually; freeze release in analysis | technical release documentation |

### 10.5 Regional healthcare evidence

| Claim | Status | Source |
|:---|:---|:---|
| Danish regional hospitals/institutions baseline about 3.3 Mt CO2e in 2022 | Verified | https://www.regioner.dk/regional-udvikling/groenne-hospitaler/regionernes-klimamaal/ |
| regions purchase >150,000 products | Verified | same |
| common climate-management model exists | Verified | same |
| every product has physical quantity data | **Not verified** | request underlying data |
| procurement footprint is entirely product-LCA based | **False/unsupported** | climate accounting documentation includes spend-based factors |
| some purchase emission factors use EXIOBASE | Verified in climate-accounting methodology examples | https://www.niras.dk/media/2u0nyq2c/niras-dk-climate-account-2022.pdf |
| national harmonised hospital×gas physical table is public | **Not verified** | request needed |
| Region H medical gases approx. 6,300 t CO2e/yr | Verified | https://www.regionh.dk/til-fagfolk/Klima-og-miljoe/groen-omstilling-af-hospitalerne/CO2-indsatser-i-koncerncentre/Sider/Medicinske-gasser-destruktion-og-reduktion.aspx |

### 10.6 Waste evidence

| Claim | Status | Source |
|:---|:---|:---|
| ADS contains Danish raw waste-flow data | Verified | https://mst.dk/erhverv/groen-produktion-og-affald/affald-og-genanvendelse/affaldshaandtering/affaldsdata-og-affaldsdatasystemet/find-affaldsdata |
| 2022 EPA waste statistics include raw-data download | Verified | https://mst.dk/erhverv/groen-produktion-og-affald/affald-og-genanvendelse/affaldshaandtering/affaldsdata-og-affaldsdatasystemet/find-affaldsstatistikker-og-kortlaegning |
| DST Waste Accounts use EPA ADS as source | Verified | https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/waste-accounts/statistical-processing |
| DST allocates waste to 117 industries | Verified | https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/waste-accounts/statistical-presentation |
| about 1-2% of waste annually is proportionally distributed where activity codes are missing | Verified | DST statistical processing |
| ADS and AFFALD are independent measurements | **False** | shared lineage |
| NHS ERIC provides open trust/site CSV | Verified | https://digital.nhs.uk/data-and-information/publications/statistical/estates-returns-information-collection/summary-page-and-dataset-for-eric-2024-25 |

### 10.7 Unresolved questions to close

**Product/SUT:** exact national product code schema; English label
availability; exact HS/CN/CPA mapping; price/cost of a metadata package;
Research Services route and output restrictions; Denmark A88 availability by
target year.

**Regional healthcare:** data dictionary of the common climate-management
model; whether SKU-level data can be shared for research; physical quantity
coverage; emission-factor provenance by procurement category; national
gas-activity table availability.

**Waste:** exact healthcare granularity in Eurostat WStatR tables; five-region
hospital waste extract for common year; mapping between regional waste
fractions and DST/EWC-Stat.

**FIGARO:** exact healthcare product mappings at A64; reproducibility
residual against Eurostat GHG footprints; compatibility between 2022
healthcare SHA expenditure and FIGARO valuation/final demand.

### 10.8 Rule for the manuscript

Every empirical source should be labelled as one of: `MEASURED_ACTIVITY`,
`ADMINISTRATIVE_ACCOUNT`, `OFFICIAL_STATISTICAL_MODEL`, `EEIO_MODEL`,
`MRIO_MODEL`, `SPEND_BASED_ESTIMATE`, `PROCESS_LCA_FACTOR`,
`SCENARIO_ASSUMPTION`. This will stop measured physical data and
model-derived carbon estimates from being inadvertently treated as
equivalent evidence.
