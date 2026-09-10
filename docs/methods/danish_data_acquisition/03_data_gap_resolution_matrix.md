# Data-gap resolution matrix for the Danish healthcare footprint model

## 1. Why the earlier “gap” language was too simple

A data item can exist but still be unusable for replication because:

- it is not public;
- it is not national;
- it is not harmonised across regions;
- it lacks physical quantities;
- it is spend-based rather than activity-based;
- it reuses EXIOBASE factors and therefore is not independent of the model being benchmarked;
- its healthcare boundary differs from SHA;
- it is only available in reports rather than machine-readable tables.

The revised inventory therefore scores each gap on:

1. **existence**;
2. **accessibility**;
3. **resolution**;
4. **methodological independence**;
5. **preferred solution**;
6. **fallback solution**.

---

# 2. Revised gap matrix

| Data need | Evidence data exist? | Public usable data? | Independence from EEIO/MRIO | Preferred route | Residual gap |
|:---|---:|---:|---:|:---|:---|
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

---

# 3. Regional climate data: useful, but not a complete independent benchmark

The Danish Regions report a common 2022 hospital/institution climate baseline of about **3.3 Mt CO2e** and state that the regions buy more than **150,000 products**.

This confirms that a large procurement data infrastructure exists.

However, regional climate-accounting documentation also shows an important limitation: purchasing emissions can be calculated using **spend-based EXIOBASE emission factors**, inflation-adjusted to the relevant year.

Therefore:

\[
\text{regional procurement climate account}
\not\equiv
\text{independent physical LCA benchmark}.
\]

Use it for:

- organisational boundary checks;
- expenditure/category totals;
- identifying major procurement groups;
- testing whether national models reproduce the same hotspot ranking;
- obtaining physical data where the regional model uses quantities.

Do not use its spend-based CO2e output as independent confirmation of an EXIOBASE-based national calculation.

Official sources:

- https://www.regioner.dk/regional-udvikling/groenne-hospitaler/regionernes-klimamaal/
- https://www.niras.dk/media/2u0nyq2c/niras-dk-climate-account-2022.pdf

---

# 4. Medical gases

## What is verified

Region Hovedstaden reports approximately **6,300 t CO2e annually** from medical gases and distinguishes:

- direct release during patient care;
- indirect emissions from production/procurement.

This demonstrates that gas-specific accounting exists operationally.

## What is not yet verified

A national public table of:

```text
year
region
hospital
gas
kg or litres consumed
kg destroyed/recovered
direct CO2e
upstream CO2e
```

has not been found.

## Preferred solution

Request the underlying common-regional gas activity table.

If only purchase data are available:

\[
F_g
=
Q_g\times GWP_g
\]

adjusted for:

- wastage;
- destruction;
- capture;
- stock changes.

## Fallback

Use public regional CO2e totals as bounding values, but do not mix them into the final national physical calculation without harmonising GWPs and boundaries.

Source:

https://www.regionh.dk/til-fagfolk/Klima-og-miljoe/groen-omstilling-af-hospitalerne/CO2-indsatser-i-koncerncentre/Sider/Medicinske-gasser-destruktion-og-reduktion.aspx

---

# 5. Procurement and medical consumables

## What exists

The regions state that their hospitals/institutions buy more than 150,000 products. Regional climate accounts expose categories such as:

- medicines;
- medical articles/equipment;
- assistive devices;
- implants;
- test materials;
- chemicals;
- hygiene items;
- disposable products;
- general goods/services.

## Preferred data request

Request a disclosure-safe annual extract at the finest harmonised category or SKU level available:

```text
year
region
hospital_or_entity
sku_or_item_id
product_description
supplier
procurement_category
quantity
unit
spend_dkk
emission_factor
factor_unit
factor_source
calculation_method
reported_co2e
```

### Why all factor fields matter

If:

\[
reported\_co2e
=
spend\times EXIOBASE\ factor,
\]

that field cannot be used as independent validation of an EXIOBASE footprint.

But:

- quantity;
- product category;
- spend;
- supplier;
- organisation;

remain highly useful independent activity data.

---

# 6. Pharmaceuticals

Use a hierarchy.

## Level 1: open aggregate data

Medstat.

Purpose:

- ATC trends;
- candidate pMDIs;
- quantity-based sensitivity.

## Level 2: custom aggregate extract

Preferred first request to the Danish Health Data Authority.

Possible grain:

```text
year
ATC
product_or_package_number
hospital_vs_primary_care
region
department_if_disclosable
```

Measures:

```text
packages
DDD
units
quantity
value_dkk
```

## Level 3: LSR/LMDB

Use only if the aggregate extract cannot answer the environmental question.

This follows proportionality and avoids unnecessary person-level data.

---

# 7. Patient and staff travel

## Region-paid patient transport

Strong operational data appear to exist in regional climate/transport systems.

Preferred extract:

```text
year
region
transport_type
journeys
passenger_km
vehicle_km
fuel_or_energy
```

## Self-arranged patient travel

A defensible model is possible from:

\[
\text{patient residence}
\rightarrow
\text{hospital/contact location}
\]

combined with travel mode assumptions.

Model:

\[
PKM_{o,h,m}
=
Contacts_{o,h}
\times
Distance_{o,h}
\times
ModeShare_{o,h,m}.
\]

Use the National Patient Register for contact geography and DTU TU for travel behaviour.

## Staff commuting

Potential design:

\[
EmployeeTrips_{o,w,m}
=
Employees_{o,w}
\times
WorkingDays
\times
ModeShare_{o,w,m}.
\]

Use residence-workplace registers plus TU mode modelling.

## Visitor travel

This remains a genuine gap.

Recommended treatment:

- facility surveys where available;
- visitor-per-admission assumptions;
- low/base/high scenarios;
- keep it as a separate component.

---

# 8. Energy and buildings

These are comparatively well covered.

Use:

- region/facility meter data where accessible;
- Statistics Denmark energy/environmental accounts for national consistency;
- construction/GFCF for capital.

Avoid double counting when bottom-up facility energy is added to an IO final-demand model.

Define:

```text
bottomup_replacement_flag
io_flow_removed
replacement_quantity
replacement_factor
```

---

# 9. Materials and resources

Denmark's material accounts are strong for national totals but do not directly answer:

> Which raw materials are attributable to healthcare final demand?

Use:

\[
\text{Danish SUT demand}
+
\text{MRIO material extensions}.
\]

Cross-model:

- EXIOBASE;
- GLORIA.

GLORIA is particularly valuable here because it was explicitly constructed for global resource-flow/material-footprint analysis.

---

# 10. What remains genuinely unresolved

After deeper searching, the strongest unresolved issues are:

1. the exact full Danish SUT and its year-specific product metadata;
2. machine-readable common regional procurement/activity data;
3. national physical gas consumption by hospital and gas species;
4. visitor travel;
5. product-level environmental factors for large numbers of medical devices/consumables;
6. healthcare-specific global material/land/water-scarcity attribution;
7. uncertainty in mapping SHA expenditure to SUT/MRIO products.

Therefore the problem has **not disappeared**. It has shifted from “data do not exist” to:

\[
\boxed{
\text{access}
+
\text{classification}
+
\text{independence}
+
\text{boundary harmonisation}
}
\]

for several high-value datasets.

---

# 11. Data-quality grading

Every source should receive four independent grades:

```text
access_grade
resolution_grade
boundary_grade
independence_grade
```

Example:

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

This prevents “available” from being confused with “good enough”.
