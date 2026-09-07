# Danish national-accounts products and a healthcare filtering strategy

## 1. The central question

The Danish final supply-use system is compiled using approximately:

\[
2,350\text{ products}\times117\text{ industries}.
\]

The number of products varies slightly by year as products enter and leave the balancing system.

The key question is not merely whether “a Danish product classification exists”, but whether we can obtain:

1. the **exact year-specific national-accounts product codes** used in the 2019 and 2022 SUTs;
2. their descriptions;
3. Danish and English labels;
4. the mapping from those product codes to standard classifications such as HS/CN and CPA;
5. the corresponding numerical SUT rows.

These are different access objects and should be requested separately.

---

# 2. What Statistics Denmark explicitly confirms

Statistics Denmark's SUT documentation states that:

- final SUT compilation uses about 2,350 products and 117 industries;
- product-by-product supply and use are reconciled so supply equals use;
- the most detailed SUTs are not publicly published because of confidentiality;
- some external users receive full SUTs through Research Services.

Statistics Denmark's annual national-accounts accessibility documentation also says that more detailed information from the approximately 2,350 product balances can be purchased as customised data, for example a single product balance or the product composition of a consumption group.

This means there are **at least three distinct access routes**:

| Object | Likely route |
|---|---|
| Public aggregate SUT/IOT | StatBank / Eurostat / DST download |
| Selected detailed product balances or compositions | Custom paid extract from National Accounts |
| Full working-level SUT | Research Services, subject to approval/confidentiality |

Official sources:

- https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/statistical-presentation
- https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/relevance
- https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--annual/accessibility-and-clarity

---

# 3. Is there a free public list of the exact 2,350 product codes?

## Finding

**No exact, current, year-specific public list has been verified.**

Statistics Denmark states that the final national accounts contain about 2,350 reconciled product balances, while detailed product breakdowns are not published in StatBank.

There is also a classification nuance that should be resolved directly with Statistics Denmark:

- SUT methodology describes goods in terms connected to HS/foreign-trade classifications and services to CPA;
- broader national-accounts documentation describes the national product dimension as an **adapted CPA-based classification**.

These descriptions are not necessarily contradictory. A national product code may be an internal national-accounts classification populated from HS/CN data for goods and CPA/service sources, but the **exact code architecture is not documented clearly enough publicly to reconstruct it without confirmation**.

Therefore the request should explicitly ask for:

```text
nr_product_code
label_da
label_en (if maintained)
good_service_flag
hs6_mapping
cn8_mapping
cpa21_mapping
cpa88_parent
valid_from
valid_to
revision_year
```

If Statistics Denmark does not maintain English labels internally, the HS/CPA concordance is sufficient for us to attach authoritative English labels ourselves.

---

# 4. What can be built publicly now?

A high-quality bilingual **candidate product universe** can be assembled from:

\[
\text{CN/HS goods}
+
\text{CPA products/services}.
\]

This will not be identical to the 2,350-row SUT dimension, but it lets us design and test the healthcare classifier before restricted metadata arrive.

## 4.1 Goods

The Combined Nomenclature (CN) is available annually. The first six digits correspond to HS.

Statistics Denmark provides CN search/download infrastructure and Eurostat provides classification code lists and correspondence infrastructure.

The product table should preserve the exact classification year because CN codes change over time.

Recommended fields:

```text
classification_year
cn8_code
hs6_code
label_da
label_en
valid_from
valid_to
```

## 4.2 Services and CPA products

Use CPA 2.1 for the 2019/2022 model unless Statistics Denmark specifies a different national product mapping for a particular table version.

Recommended fields:

```text
cpa_code
cpa_level
label_da
label_en
parent_cpa
```

---

# 5. Do not call all product rows “health sectors”

This distinction is essential.

## Industry

A sector or industry answers:

> Who produces?

Examples:

- NACE C21 pharmaceutical manufacturing;
- NACE Q86 human health activities.

## Product

A product answers:

> What is supplied or used?

Examples:

- pharmaceutical preparations;
- diagnostic reagents;
- medical equipment;
- hospital services.

The healthcare model needs both dimensions.

A hospital can consume products produced by dozens of non-health industries.

Therefore:

\[
\text{healthcare footprint}
\neq
\text{footprint of industries classified as healthcare}.
\]

---

# 6. Recommended healthcare product taxonomy

Use a tiered classifier.

## Tier 1: core healthcare

Strong inclusion evidence.

### Services

- Human health services, NACE/CPA 86.
- Hospital activities.
- Medical and dental practice.
- Other human health services.

### Pharmaceuticals

- CPA/NACE 21.
- HS Chapter 30, refined at subheading level.

### Medical devices

- CPA/NACE 32.50 where available.
- Electromedical and radiation equipment within CPA/NACE 26.60 where relevant.

### Diagnostics

- relevant laboratory/diagnostic reagents such as HS 3822, filtered at subheading level.

---

## Tier 2: healthcare-dependent products

Products strongly used by healthcare but not exclusively healthcare-specific.

Examples:

- respiratory equipment;
- prostheses;
- hearing aids;
- X-ray apparatus;
- specialised medical furniture;
- selected PPE;
- selected sterile consumables;
- selected laboratory goods.

Representative HS families for **candidate screening only** include:

| HS heading/family | Candidate health use |
|---|---|
| 3001–3006 | medicinal and pharmaceutical goods |
| 3822 | diagnostic/laboratory reagents |
| 9018 | medical, surgical, dental and veterinary instruments |
| 9019 | mechanotherapy/respiratory-related apparatus |
| 9020 | breathing appliances |
| 9021 | orthopaedic appliances, prostheses, hearing aids etc. |
| 9022 | X-ray and radiation apparatus |
| 9402 | medical, surgical and dental furniture |

These headings must **not** be included wholesale without lower-level review because some include veterinary or non-health uses.

---

## Tier 3: enabling inputs

These are not “health products” in a narrow classification sense but may be major healthcare footprint drivers:

- electricity;
- heating;
- construction;
- food;
- laundry;
- cleaning;
- ICT;
- transport;
- chemicals;
- packaging;
- office services.

Tier 3 should be discovered from the hospital/SHA demand structure, not by relabelling the underlying products as medical.

---

# 7. Social care boundary

Do not automatically include all of:

\[
NACE/CPA\ 87\text{ and }88.
\]

Instead use SHA to determine the health boundary.

Create separate flags:

```text
health_core_flag
long_term_healthcare_flag
social_care_flag
sha_in_scope_flag
```

This makes it possible to publish:

- healthcare only;
- healthcare plus health-related long-term care;
- broader health and social care;

without rewriting the base data.

---

# 8. Proposed bilingual product dimension

Create:

`dim_dk_na_product`

with:

| Field | Meaning |
|---|---|
| `product_key` | warehouse key |
| `reference_year` | SUT year |
| `dst_na_product_code` | exact DST code once obtained |
| `label_da` | Danish label |
| `label_en` | English label |
| `classification_origin` | DST / CN / HS / CPA |
| `cn8_code` | CN link |
| `hs6_code` | HS link |
| `cpa21_code` | CPA link |
| `cpa88_parent` | Eurostat 88-product parent |
| `cpa64_parent` | Eurostat A64 parent |
| `good_service_flag` | goods/services |
| `health_tier` | 0, 1, 2, 3 |
| `health_group` | pharma/device/service/etc. |
| `sha_hc_code` | SHA mapping if relevant |
| `capital_flag` | capital good |
| `clinical_consumable_flag` | yes/no |
| `mapping_confidence` | high/medium/low |
| `mapping_method` | code/manual/procurement/SHA |
| `review_status` | pending/verified/rejected |
| `source_version` | provenance |

---

# 9. Healthcare candidate bridge

Keep healthcare classification as a bridge rather than hard-coding a permanent health flag into the product master:

`bridge_product_health_scope`

Fields:

```text
product_key
health_scope_key
sha_hc_code
inclusion_weight
inclusion_reason
evidence_source
confidence_grade
reviewer
review_date
```

This allows one product to be:

- 100% healthcare;
- partly healthcare;
- in-scope only for a particular SHA function.

---

# 10. Filtering workflow

## Pass 1: exact-code screening

Use known CPA/HS/CN code families.

## Pass 2: bilingual keyword screening

English examples:

```text
medical
hospital
pharmaceutical
medicinal
diagnostic
surgical
dental
prosthetic
orthopaedic
laboratory
ambulance
rehabilitation
```

Danish examples:

```text
medicinsk
hospital
lægemiddel
farmaceutisk
diagnostisk
kirurgisk
tandlæge
protese
ortopædisk
laboratorie
ambulance
rehabilitering
```

Keyword screening is for candidate discovery, not final inclusion.

## Pass 3: SHA concordance

Check whether the product is purchased within a SHA healthcare function/provider.

## Pass 4: procurement validation

Use regional procurement categories/SKUs to establish which candidate products are actually consumed by healthcare.

## Pass 5: manual review

Review:

- multi-use products;
- veterinary-containing headings;
- mixed social/health services;
- capital goods;
- chemicals/reagents;
- PPE.

---

# 11. What we should request from Statistics Denmark

The first contact should ask for both **data** and **classification metadata**.

Priority metadata request:

1. year-specific product code list for 2019 and 2022;
2. Danish product descriptions;
3. English labels if maintained;
4. HS/CN mapping for goods;
5. CPA mapping for services/products;
6. A88/A64 parent mapping;
7. code validity/version information.

Priority numeric request:

1. supply matrix;
2. use matrix;
3. domestic/import use if available;
4. valuation matrices;
5. final demand;
6. capital formation.

This separates the classification problem from the confidentiality problem.

---

# 12. Practical conclusion

We can begin health-product filtering **before full SUT access**, but we should not claim that a public HS/CPA-derived list is the exact Danish 2,350-product SUT dimension.

The correct workflow is:

\[
\boxed{
\text{public CN/HS + CPA bilingual universe}
}
\]

\[
\downarrow
\]

\[
\boxed{
\text{candidate healthcare classifier}
}
\]

\[
\downarrow
\]

\[
\boxed{
\text{DST year-specific product list + concordance}
}
\]

\[
\downarrow
\]

\[
\boxed{
\text{verified health-to-SUT bridge}
}
\]

This is both reproducible and scientifically defensible.
