# Statistics Denmark contact and acquisition plan

## 1. What should be requested

The enquiry should no longer ask only for “the SUT”.

It should ask Statistics Denmark to clarify access to **four distinct objects**:

1. full 2019 and 2022 SUT numerical tables;
2. year-specific ~2,350-product code list;
3. Danish/English descriptions and HS/CPA concordance;
4. domestic/import and valuation matrices.

This is important because product metadata may be deliverable even if numerical cells have confidentiality restrictions.

---

# 2. Why the first contact should still be Peter Rørmose Jensen

Statistics Denmark identifies:

**Peter Rørmose Jensen**  
National Accounts, Climate and Environment, Economic Statistics  
Email: `prj@dst.dk`  
Phone: +45 40 13 51 26

as the SUT/IOT subject-matter contact.

Official pages:

- https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use
- https://www.dst.dk/en/Statistik/emner/oekonomi/nationalregnskab/input-output

The public documentation shows two plausible non-public routes:

- customised paid national-accounts extracts;
- Research Services access to full SUTs.

Therefore the subject-matter statistician should confirm which route fits the project **before** a formal Research Services data order is prepared.

---

# 3. Exact first email, under 100 words

**Subject:** Detailed Danish SUT and product classification for research

> Dear Peter,
>
> I am a researcher at SDU developing a reproducible environmental input-output assessment of Danish healthcare. I have found the public Eurostat A64/A88 SUTs and Statistics Denmark’s 117-industry IOT, but need the working-level product detail. Could you confirm access to the 2019 and 2022 SUTs (about 2,350 products × 117 industries), including domestic/import use and valuation matrices, and whether the year-specific product-code list, Danish/English labels, and HS/CPA concordance can be supplied? Please advise the appropriate access route, costs, and required materials.
>
> Best regards,  
> Albert Osei-Owusu

The body is **86 words** under a conventional tokenised word count.

---

# 4. Why this email is stronger

It demonstrates that you have already identified:

- public Eurostat A64/A88;
- public 117-industry Danish IOT;
- the need for working-level product detail.

It also does not prematurely assume whether the appropriate route is:

- free metadata;
- a paid bespoke extract;
- Research Services.

---

# 5. Materials to prepare, but not attach unless requested

## A. One-page project brief

Title:

**Environmental footprint of the Danish healthcare system: a Denmark-specific hybrid EEIO/MRIO assessment**

Include:

- institution: SDU;
- objective;
- why public tables are insufficient;
- target years;
- data requested;
- model equations;
- intended outputs;
- no personal data required;
- publication/reproducibility goal.

## B. Exact data specification

### Supply

```text
product × industry domestic output
imports by product
basic-price supply
valuation bridge
```

### Use

```text
product × industry intermediate use
household consumption
government consumption
NPISH
GFCF
inventories
exports
```

### Prefer if available

```text
use of domestic output at basic prices
use of imports at basic prices
trade margins
transport margins
taxes
subsidies
VAT
```

### Metadata

```text
product code
label_da
label_en
HS/CN mapping
CPA mapping
industry code
classification version
structural/suppression flag
revision ID
price basis
unit
```

---

# 6. Why request 2019 and 2022

## 2022

Preferred main study year.

Statistics Denmark states that the fully detailed final SUT uses approximately 2,350 products and that the currently documented final 2022 SUT forms part of the consistent post-2014 series.

## 2019

Preferred cross-MRIO pre-pandemic benchmark.

Requesting only two years:

- reduces cost;
- supports data minimisation;
- makes the access case easier to justify.

---

# 7. If Peter offers a paid custom extract instead of full Research Services access

Ask for a quotation for two products:

## Product A: metadata package

```text
2019 and 2022 product code lists
labels
HS/CPA concordance
A64/A88 parent mapping
```

## Product B: health-relevant numerical extract

If the full SUT is expensive or restricted, request all rows corresponding to:

- healthcare candidate products;
- their supply;
- their intermediate/final use;
- import/domestic split;
- valuation components.

### Caution

A health-only row extract may be insufficient for constructing the full Leontief inverse.

If we need to calculate:

\[
L=(I-A)^{-1}
\]

at 2,350-product detail, we need a complete economic system, not only selected health rows.

Therefore:

> a health-only extract is useful for disaggregation/concordance, but it does **not** replace full SUT access for high-resolution IO modelling.

---

# 8. If Research Services is required

Then determine:

1. whether the relevant SDU environment is already authorised;
2. who manages Statistics Denmark research access at SDU;
3. whether SUT access uses the normal Denmark's Data Portal workflow or a special national-accounts arrangement;
4. price and expected processing time;
5. output-control rules.

Do not create a generic register-data application until DST confirms the SUT ordering path.

---

# 9. Free fallbacks to acquire regardless

## Denmark

- 117-industry IOT.

## Eurostat

- annual A64 SUT;
- inspect A88 availability for Denmark/year;
- FIGARO 64×64.

### Important A88 qualification

Eurostat first published 88-product/88-industry detailed SUTs in 2025 based on **voluntary country transmissions**.

Do not state that Denmark 2019 or 2022 A88 is available until the actual country/year cells are checked.

---

# 10. Follow-up questions if Peter replies positively

1. Are 2019 and 2022 available at the full product resolution?
2. Are they on the same revision/classification basis?
3. Can the year-specific product dimension be supplied as a separate metadata file?
4. Are English labels maintained?
5. What is the exact mapping to HS/CN and CPA?
6. Can domestic and imported use be supplied separately?
7. Are margin/tax matrices available annually or only benchmark years?
8. Are basic-price use tables available for 2019/2022?
9. Are numerical cells subject to disclosure restrictions?
10. Can the full SUT be used programmatically inside a secure research environment?
11. Can derived aggregate matrices/multipliers be exported?
12. What costs and lead times apply?

---

# 11. Decision tree

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

---

# 12. What can proceed while waiting

Do not pause the project.

Build immediately:

\[
\text{SHA1}
+
\text{117-industry IOT}
+
\text{Danish environmental accounts}.
\]

In parallel:

- build the public bilingual HS/CPA health-product candidate universe;
- test FIGARO;
- acquire EXIOBASE/GLORIA/Eora/OECD;
- develop the star schema.

The detailed SUT should drop into an architecture that already works.
