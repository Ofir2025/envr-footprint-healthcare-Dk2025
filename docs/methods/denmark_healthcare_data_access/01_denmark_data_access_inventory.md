# Danish data access inventory

## 1. Scope

This inventory identifies where the data required to replicate and extend Malik et al., Eckelman & Sherman, and Lenzen et al. can be obtained for Denmark.

Access codes used below:

- **OPEN**: publicly downloadable or API-accessible without a research application.
- **CONTROLLED**: access requires an institutional/research application.
- **REQUEST**: no standard public extract identified; direct contact or custom statistics request is appropriate.
- **MRIO**: external multi-regional input-output database.

---

# 2. Economic core

## 2.1 Full Danish working-level SUT

**Source:** Statistics Denmark, National Accounts: Input-Output and Supply-Use.

**Resolution:** approximately 2,350 products × 117 industries.

**Status:** `CONTROLLED`.

Statistics Denmark states that:

- the Danish SUT system balances approximately 2,350 products and 117 industries;
- only some industry-level totals are published in StatBank;
- detailed product-level supply-use relationships are not published because of confidentiality;
- users wishing to work with the most detailed tables can apply for access through Research Services;
- some external users receive the full SUT through their Research Service account.

### Why this is the preferred domestic backbone

The detailed SUT retains the product × industry structure needed to distinguish:

- pharmaceuticals;
- medical devices;
- hospital services;
- outpatient services;
- diagnostic goods/services;
- food;
- electricity;
- construction;
- transport;
- ICT;
- cleaning;
- other intermediate products.

### Target database objects

- `fact_io_flow`
- `dim_product`
- `dim_industry`
- `dim_price_basis`
- `bridge_health_to_economic_node`

### Official source

https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/statistical-presentation

---

## 2.2 Public Danish 117-industry IOT

**Source:** Statistics Denmark.

**Status:** `OPEN`.

The current input-output page provides a 117-industry IOT as a downloadable ZIP and current StatBank tables including:

- `NAIO1` - input-output table, supply by industries, use and price unit;
- `NAIO2` - unallocated imports;
- `NAIO3` - primary inputs;
- `NAIO4` - totals;
- `NAIO5` - employment.

### Use

Use this immediately to:

1. build and test the IO engine;
2. validate row/column orientation;
3. reproduce official multipliers;
4. build the star-schema pipeline before restricted SUT access is resolved.

### Official source

https://www.dst.dk/en/Statistik/emner/oekonomi/nationalregnskab/input-output

---

## 2.3 Free national SUTs from Eurostat

**Source:** Eurostat ESA supply, use and input-output tables.

**Status:** `OPEN`.

This is the key correction to the earlier wording: **Danish SUT data are available free at aggregated European reporting resolution.**

Mandatory national SUT transmission distinguishes:

- 64 activities;
- 64 products.

Countries may voluntarily transmit:

- 88 activities;
- 88 products.

Annual tables include:

- `T1500` - supply table at basic prices including transformation to purchasers' prices;
- `T1600` - use table at purchasers' prices.

For benchmark years ending in 0 or 5, the system also includes:

- `T1610` - use at basic prices;
- `T1611` - use of domestic output;
- `T1612` - use of imports;
- `T1620` - trade and transport margins;
- `T1630` - taxes less subsidies;
- symmetric IOTs.

Common Eurostat dataset families include:

- `naio_10_cp15` - supply table;
- `naio_10_cp16` - use table.

### Limitation

These tables are **not the same as the full ~2,350-product Danish working SUT**. They are useful open substitutes and harmonised validation datasets.

### Official sources

https://ec.europa.eu/eurostat/en/web/esa-supply-use-input-tables/information-data

https://ec.europa.eu/eurostat/en/web/esa-supply-use-input-tables/database

---

## 2.4 FIGARO

**Source:** Eurostat FIGARO 2026 edition.

**Status:** `OPEN`.

Coverage:

- 64 industries;
- 64 products;
- 2010-2024;
- EU inter-country supply, use and IOT tables;
- CSV data for supply, use and IOT;
- 27 EU states plus candidate countries, major trading partners and rest of world.

### Role

FIGARO is useful for:

- open EU-level sensitivity;
- bilateral EU supply-chain structure;
- an independent bridge between the domestic Danish model and global MRIO calculations.

### Official source

https://ec.europa.eu/eurostat/en/web/esa-supply-use-input-tables/database

---

# 3. Healthcare expenditure and boundary

## 3.1 SHA1

**Source:** Statistics Denmark StatBank.

**Table:** `SHA1`.

**Status:** `OPEN`.

Approximate dimensions currently include:

- 44 healthcare functions;
- 34 provider categories;
- 8 financing schemes;
- annual current-price expenditure.

### Model role

SHA should define **what counts as healthcare** and how final demand is disaggregated.

It should not simply be added to national-accounts health expenditure. Instead, construct a concordance:

\[
\text{SHA function/provider/financing}
\rightarrow
\text{SUT products/industries}
\]

with weights that reconcile to the agreed healthcare control total.

### Target objects

- `fact_health_expenditure`
- `dim_health_function`
- `dim_provider`
- `dim_financing`
- `bridge_health_to_economic_node`

### Source

https://www.statbank.dk/SHA1

---

# 4. Greenhouse gases and air pollution

## 4.1 DRIVHUS / DRIVHUS2

**Status:** `OPEN`.

Use for direct Danish industry greenhouse-gas extensions.

Useful healthcare-relevant industries include pharmaceuticals, medical instruments and health-service industries.

### Target objects

- `fact_environmental_extension`
- `fact_ghg_species`

### Source

https://www.statbank.dk/DRIVHUS

---

## 4.2 MRU1

**Status:** `OPEN`.

Industry air-emission account containing pollutants including:

- CO2;
- SO2;
- NOx;
- CO;
- NH3;
- N2O;
- CH4;
- NMVOC;
- PM10;
- PM2.5;
- F-gases.

### Role

Core domestic extension for the Eckelman-style multi-pollutant model.

### Source

https://m.statbank.dk/TableInfo/MRU1

---

## 4.3 EMM1MU2N

**Status:** `OPEN`.

Statistics Denmark's direct and indirect air-emission multiplier table by final-demand category.

It can be used as an **independent unit test** of a custom calculation:

\[
F=qLy_H.
\]

### Target role

Validation of:

- `fact_footprint_total`;
- final-demand multipliers;
- pollutant intensities.

### Source

https://m.statbank.dk/TableInfo/EMM1MU2N

---

## 4.4 EMM1MU3N

**Status:** `OPEN`.

Provides emissions caused by final demand by the industries in which the emissions arise.

### Target role

Validation of:

- `fact_supplier_footprint`.

### Source

https://m.statbank.dk/TableInfo/EMM1MU3N

---

# 5. Water

## 5.1 VANDRG2

**Status:** `OPEN`.

Physical water account by industry and water type.

### Target

- `fact_environmental_extension`

### Source

https://m.statbank.dk/TableInfo/VANDRG2

---

## 5.2 VAN2MU2N

**Status:** `OPEN`.

Contains direct and indirect water use caused by final demand and multipliers per monetary demand.

### Use

Independent validation of the domestic water footprint.

### Important distinction

This is physical water consumption, not automatically scarcity-weighted water.

For Lenzen-style scarce-water footprints:

\[
F_{\text{scarce water}}
=
\sum_r Water_r \times ScarcityFactor_r.
\]

Foreign regional water must therefore be supplied by an MRIO/resource dataset and regional scarcity factors.

### Source

https://m.statbank.dk/TableInfo/VAN2MU2N

---

# 6. Waste

## 6.1 AFFALD

**Status:** `OPEN`.

Physical waste generation by:

- industry;
- waste fraction;
- treatment.

### Source

https://m.statbank.dk/TableInfo/AFFALD

---

## 6.2 AFF1MU2N and related multiplier tables

**Status:** `OPEN`.

Provides direct and direct-plus-indirect waste by final demand, including multiplier units.

### Target

- `fact_footprint_total`
- `fact_health_category_footprint`

### Source

https://m.statbank.dk/TableInfo/AFF1MU2N

---

## 6.3 AFF1MU3N and related producer tables

**Status:** `OPEN`.

Provides producing-industry attribution for waste caused by final demand.

### Target

- `fact_supplier_footprint`

### Source

https://m.statbank.dk/TableInfo/AFF1MU3N

---

# 7. Materials and land

## 7.1 MRM2

**Status:** `OPEN`.

Economy-wide material flows covering biomass, ores, non-metallic minerals and fossil materials.

### Use

National material-flow benchmark and extension-development input.

### Source

https://m.statbank.dk/TableInfo/MRM2

---

## 7.2 RME1

**Status:** `OPEN`.

Raw-material-equivalent / resource-footprint account.

### Use

National material-footprint denominator and validation benchmark.

### Limitation

A ready-made public `health final demand × raw material` multiplier table comparable to EMM1MU2N was not identified. Healthcare-specific material footprints therefore still require custom IO/MRIO calculation.

### Source

https://m.statbank.dk/TableInfo/RME1

---

## 7.3 AREALAN1

**Status:** `OPEN`, but low priority.

Contains broad domestic land-use information and is too aggregated to represent the full global healthcare land footprint.

### Use

Domestic land benchmark only.

### Source

https://m.statbank.dk/TableInfo/AREALAN1

---

# 8. Official Danish consumption-footprint benchmark

## AFTRYK1

**Status:** `OPEN`.

Provides Danish consumption climate footprints by:

- final use;
- emitting industry;
- emitting country;
- year.

### Importance

This is particularly valuable for validating:

\[
F_{\text{domestic}}
\quad\text{versus}\quad
F_{\text{foreign}}.
\]

### Target

- `fact_geographic_footprint`
- `fact_national_share`

### Source

https://m.statbank.dk/TableInfo/AFTRYK1

---

# 9. Pharmaceuticals

## 9.1 Medstat

**Status:** `OPEN`.

Use for exploratory pharmaceutical statistics and preliminary product/ATC activity.

---

## 9.2 Custom aggregated statistical extract

**Institution:** Danish Health Data Authority / Forskerservice.

**Status:** `REQUEST`.

This should be the **first pharmaceutical data request** before applying for person-level registers.

Suggested grain:

\[
year/month
\times ATC
\times product/package
\times sector
\times region
\times hospital/department\text{ where possible}.
\]

Suggested measures:

- packages;
- DDD;
- physical quantity;
- sales/purchase value;
- number of units.

### Why this route

The footprint model does not require personal identifiers. A disclosure-controlled aggregate extract is therefore likely to be simpler and more proportionate.

### Source

https://sundhedsdatastyrelsen.dk/data-og-registre/forskerservice/ansoeg-om-data/statistikudtraek

---

## 9.3 Lægemiddelstatistikregisteret / LMDB

**Status:** `CONTROLLED`.

Use if the aggregate extract cannot provide sufficient product/provider detail.

Potential role:

- pMDIs;
- pharmaceutical quantities;
- provider/hospital disaggregation;
- product-level validation.

---

## 9.4 Amgros

**Status:** `REQUEST`.

No open row-level national hospital pharmaceutical-procurement dataset suitable for this model was identified.

Approach Amgros only after defining the exact fields missing from LSR/LMDB or an aggregate Health Data Authority extract.

---

# 10. Travel

## DTU Transportvaneundersøgelsen

**Status:** mixed.

- public summaries: `OPEN`;
- custom/detailed extracts: `REQUEST`.

Useful variables include:

- mode;
- trip purpose;
- distance;
- geography;
- demographic and household variables where permitted.

### Limitation

No single public national table was identified that simultaneously gives:

\[
provider
\times staff/patient/visitor
\times mode
\times distance.
\]

A healthcare-specific travel model will therefore require TU plus provider/activity or survey data.

### Contact route

`turequests@transport.dtu.dk`

### Source

https://www.man.dtu.dk/english/Scientific-advice/The-Danish-National-Travel-Survey/Documentation

---

# 11. Clinical gases and non-pharmaceutical procurement

## Anaesthetic gases

**Status:** `REQUEST`.

No open national hospital-level annual dataset for N2O, desflurane, sevoflurane and related clinical gases was identified.

Potential sources to investigate:

- Danish Regions;
- regional procurement;
- hospital pharmacies;
- technical/facility gas purchasing systems.

## Medical consumables and devices

**Status:** `REQUEST`.

No open national SKU-level procurement dataset was identified for all disposables, implants, diagnostics, PPE, instruments and equipment.

Potential sources:

- regional procurement units;
- Danish Regions;
- hospital procurement systems;
- SKI where categories overlap;
- supplier/contract records.

---

# 12. External MRIO sources

Detailed comparison is provided in `02_cross_mrio_replication_strategy.md`.

Recommended MRIO set:

1. EXIOBASE
2. GLORIA
3. Eora
4. OECD ICIO
5. FIGARO

These should be treated as **alternative model systems**, not interchangeable raw datasets.

---

# 13. Access priority

## Immediate downloads

1. Statistics Denmark 117-industry IOT
2. SHA1
3. DRIVHUS / DRIVHUS2
4. MRU1
5. EMM1MU2N / EMM1MU3N
6. VANDRG2 / VAN2MU2N
7. AFFALD / AFF*MU*
8. MRM2 / RME1
9. AFTRYK1
10. Eurostat national A64/A88 SUTs
11. FIGARO
12. EXIOBASE

## Parallel requests

1. full Danish detailed SUT;
2. pharmaceutical aggregate extract;
3. TU healthcare-relevant extract;
4. clinical gases/procurement.

---

# 14. Bottom line on SUT availability

The correct statement is:

> **A Danish SUT is available free at aggregated resolution. The full approximately 2,350-product × 117-industry working SUT is not publicly downloadable according to Statistics Denmark's current documentation.**

The free alternatives do not remove the value of requesting the full SUT because product-level health-system disaggregation is precisely where the extra detail matters most.
