# Evidence and source register

## 1. Purpose

This register distinguishes:

- verified institutional claims;
- methodological inference;
- unresolved questions.

It should be maintained alongside the data warehouse.

---

# 2. Statistics Denmark SUT evidence

| Claim | Status | Official source |
|---|---|---|
| Final SUT works with approx. 2,350 products | Verified | https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/statistical-presentation |
| Final SUT uses 117 industries | Verified | same |
| product count varies by year | Verified | same |
| full detailed SUT not publicly published due to confidentiality | Verified | https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/relevance |
| some external users receive full SUT via Research Services | Verified | same |
| detailed product balances can be purchased as customised data | Verified | https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--annual/accessibility-and-clarity |
| exact public downloadable 2,350-code list exists | **Not verified** | request from DST |
| DST maintains English labels for every national product code | **Not verified** | request from DST |
| exact year-specific HS/CPA concordance can be released | **Not verified** | request from DST |

---

# 3. Eurostat SUT evidence

| Claim | Status | Source |
|---|---|---|
| mandatory annual national SUT uses 64 activities/products | Verified | https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/information-data |
| countries may voluntarily send A88 | Verified | same |
| Eurostat first published detailed A88 SUT/IOT in 2025 | Verified | https://ec.europa.eu/eurostat/en/web/products-eurostat-news/w/wdn-20250627-1 |
| A88 data are based on voluntary transmissions | Verified | same |
| Denmark 2022 A88 definitely exists | **Not yet verified** | check database before claiming |

---

# 4. FIGARO evidence

| Claim | Status | Source |
|---|---|---|
| 2026 FIGARO covers 2010-2024 | Verified | https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/database |
| 64 industries and 64 products | Verified | same |
| supply/use/I-I/P-P/direct purchases abroad available | Verified | same |
| Eurostat publishes FIGARO-based GHG footprint datasets | Verified | https://ec.europa.eu/eurostat/cache/metadata/en/env_ac_ghgfp_esms.htm |
| GHG footprint uses FIGARO + air-emission accounts + Leontief modelling | Verified | same |
| gas-specific datasets exist | Verified | same |
| FIGARO can replace detailed Danish SUT | Rejected | resolution too coarse for intended health disaggregation |

---

# 5. GLORIA evidence

| Claim | Status | Source |
|---|---|---|
| built for UNEP IRP resource analysis | Verified | https://footprint.unep.org/gloria-mrio |
| current interface covers 1990-2024 | Verified | same |
| 164 regions | Verified | same |
| 97 industries and 97 commodities in current interface | Verified | same |
| 5 valuation layers | Verified | same |
| older releases may use different sector counts | Verified conceptually; freeze release in analysis | technical release documentation |

---

# 6. Regional healthcare evidence

| Claim | Status | Source |
|---|---|---|
| Danish regional hospitals/institutions baseline about 3.3 Mt CO2e in 2022 | Verified | https://www.regioner.dk/regional-udvikling/groenne-hospitaler/regionernes-klimamaal/ |
| regions purchase >150,000 products | Verified | same |
| common climate-management model exists | Verified | same |
| every product has physical quantity data | **Not verified** | request underlying data |
| procurement footprint is entirely product-LCA based | **False/unsupported** | climate accounting documentation includes spend-based factors |
| some purchase emission factors use EXIOBASE | Verified in climate-accounting methodology examples | https://www.niras.dk/media/2u0nyq2c/niras-dk-climate-account-2022.pdf |
| national harmonised hospital×gas physical table is public | **Not verified** | request needed |
| Region H medical gases approx. 6,300 t CO2e/yr | Verified | https://www.regionh.dk/til-fagfolk/Klima-og-miljoe/groen-omstilling-af-hospitalerne/CO2-indsatser-i-koncerncentre/Sider/Medicinske-gasser-destruktion-og-reduktion.aspx |

---

# 7. Waste evidence

| Claim | Status | Source |
|---|---|---|
| ADS contains Danish raw waste-flow data | Verified | https://mst.dk/erhverv/groen-produktion-og-affald/affald-og-genanvendelse/affaldshaandtering/affaldsdata-og-affaldsdatasystemet/find-affaldsdata |
| 2022 EPA waste statistics include raw-data download | Verified | https://mst.dk/erhverv/groen-produktion-og-affald/affald-og-genanvendelse/affaldshaandtering/affaldsdata-og-affaldsdatasystemet/find-affaldsstatistikker-og-kortlaegning |
| DST Waste Accounts use EPA ADS as source | Verified | https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/waste-accounts/statistical-processing |
| DST allocates waste to 117 industries | Verified | https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/waste-accounts/statistical-presentation |
| about 1-2% of waste annually is proportionally distributed where activity codes are missing | Verified | DST statistical processing |
| ADS and AFFALD are independent measurements | **False** | shared lineage |
| NHS ERIC provides open trust/site CSV | Verified | https://digital.nhs.uk/data-and-information/publications/statistical/estates-returns-information-collection/summary-page-and-dataset-for-eric-2024-25 |

---

# 8. Unresolved questions to close

## Product/SUT

- exact national product code schema;
- English label availability;
- exact HS/CN/CPA mapping;
- price/cost of a metadata package;
- Research Services route and output restrictions;
- Denmark A88 availability by target year.

## Regional healthcare

- data dictionary of the common climate-management model;
- whether SKU-level data can be shared for research;
- physical quantity coverage;
- emission-factor provenance by procurement category;
- national gas-activity table availability.

## Waste

- exact healthcare granularity in Eurostat WStatR tables;
- five-region hospital waste extract for common year;
- mapping between regional waste fractions and DST/EWC-Stat.

## FIGARO

- exact healthcare product mappings at A64;
- reproducibility residual against Eurostat GHG footprints;
- compatibility between 2022 healthcare SHA expenditure and FIGARO valuation/final demand.

---

# 9. Rule for the manuscript

Every empirical source should be labelled as one of:

```text
MEASURED_ACTIVITY
ADMINISTRATIVE_ACCOUNT
OFFICIAL_STATISTICAL_MODEL
EEIO_MODEL
MRIO_MODEL
SPEND_BASED_ESTIMATE
PROCESS_LCA_FACTOR
SCENARIO_ASSUMPTION
```

This will stop measured physical data and model-derived carbon estimates from being inadvertently treated as equivalent evidence.
