# Hybrid LCA and coupled MRIO methods: complete reading notes and Denmark replication blueprint

**Sources fully read in the main PDFs**

1. Hagenaars, R. H., Heijungs, R., Tukker, A., & Wang, R. (2025). *Hybrid LCA for sustainable transitions: principles, applications, and prospects*. Renewable and Sustainable Energy Reviews, 212, 115443.
2. Palm, V., Wood, R., Berglund, M., Dawkins, E., Finnveden, G., Schmidt, S., & Steinbach, N. (2019). *Environmental pressures from Swedish consumption: a hybrid multi-regional input-output approach*. Journal of Cleaner Production, 228, 634–644.

**External replication sources inspected**

- Statistics Denmark, *National Accounts: Input-Output and Supply-Use* documentation.
- Jensen, P. R., & Iliev, B. (Statistics Denmark, 2022), *Compilation of a consumption based greenhouse gas account for Denmark using coupled models*.
- Statistics Denmark health expenditure statistics, SHA1.
- United States EPA USEEIO and `useeior` GitHub repositories.
- United Nations ISIC classification.
- Agez et al. (2020, 2022) papers supplied in the project, where useful for double-counting and open-source hybridisation software.

---

## 1. Coverage ledger

| Source | Pages / sections covered | Status | Unreadable or missing items |
|---|---:|---|---|
| Hagenaars et al. (2025) | pp. 1–13, abstract through references, including nomenclature, review method, equations, tables, figures, discussion, conclusion, data availability | **COMPLETE** | None material in the supplied main PDF |
| Palm et al. (2019) | pp. 1–11, abstract through references, including methods, equations, figures, tables, discussion, conclusion, appendix notice | **COMPLETE for supplied main PDF** | **UNREADABLE / NEEDS MANUAL CHECK:** the article refers to online supplementary data, but that supplementary file was not available among the supplied files and could not be retrieved reliably in this session |
| USEEIO GitHub | main USEEIO README, current `useeior` platform, health-sector classifications and crosswalk snippets | **TARGETED EXTERNAL INSPECTION COMPLETE** | Not a sequential reading of every repository file, because the task was to inspect relevant sector detail, software and possible disaggregation recipes |
| Statistics Denmark | current SUT/IOT documentation, coupled-model technical report, health expenditure documentation | **TARGETED EXTERNAL INSPECTION COMPLETE** | Some of the most detailed Danish SUT data are not openly disseminated at the same detail as the internal compilation system |

**Important scope statement:** “complete reading” above means the two supplied journal PDFs. The Palm online supplement remains outstanding and should not be treated as read.

---

# 2. Hagenaars et al. (2025): source-anchored paper note

## 2.1 Core question

The paper asks what hybrid life cycle assessment (HLCA) methods currently exist, how their computational structures differ, where they are being applied, how robust current practice is, and what methodological barriers must be resolved if HLCA is to support sustainable technological transitions and policy.

It is not an empirical LCA of one product. It is a methodological and systematic review of **114 HLCA publications from 2016–2022**.

### Author claim

HLCA attempts to combine the specificity of process-based LCA (PLCA) with the economy-wide completeness of environmentally extended input-output analysis (EEIOA).

### Evidence

The review reports that energy systems are the most common application area, while many studies still rely on poorly documented or oversimplified hybridisation procedures. Persistent concerns include price uncertainty, double counting, capital goods, linearity and mismatched environmental-flow coverage.

### Interpretation

The paper is most useful as a **method-selection map**. It tells us which hybrid architecture fits which modelling objective.

### Critique

It does not itself provide a new operational sector-disaggregation algorithm or a code package. For the proposed Danish health-sector work, its value is conceptual and methodological: **matrix augmentation is the directly relevant class**, while systematic tiered hybridisation and integrated hybrid LCA offer lessons about double counting, price data, environmental extensions and transparency.

---

## 2.2 Study design and data

The authors use a PRISMA-style literature review.

- Databases: Web of Science and Scopus.
- Time window: 2016–2022.
- Initial screening after some exclusions: 278 publications.
- Final review set: 114 publications.
- The papers were manually classified by method, application and impact-category coverage.
- Robustness-related concepts were assessed using Atlas.ti, focusing on four key issues:
  1. price uncertainty,
  2. double counting,
  3. capital goods,
  4. linearity.

**Evidence anchor:** Hagenaars, section 2, pp. 2–3.

### Limitation of review design

The authors acknowledge that relying principally on two bibliographic databases and text-search terms can omit relevant work. This is important because absence of a search term is not necessarily equivalent to absence of methodological consideration.

---

## 2.3 Foundational PLCA and IO-LCA equations

### Process LCA

A compact process-LCA representation is:

\[
\mathbf q_p
=
\mathbf B_p
\mathbf A_p^{-1}
\mathbf f_p
\]

where:

- \(\mathbf A_p\) is the PLCA technology matrix,
- \(\mathbf B_p\) is the process environmental-extension matrix,
- \(\mathbf f_p\) is the functional unit,
- \(\mathbf q_p\) is the resulting life-cycle environmental inventory or impacts, depending on the definition of \(\mathbf B_p\).

### Input-output LCA

A conventional IO-LCA representation is:

\[
\mathbf q_{io}
=
\mathbf B_{io}
(\mathbf I-\mathbf A_{io})^{-1}
\mathbf f_{io}
\]

where:

- \(\mathbf A_{io}\) contains monetary input coefficients,
- \(\mathbf L_{io}=(\mathbf I-\mathbf A_{io})^{-1}\) is the Leontief inverse,
- \(\mathbf B_{io}\) contains direct environmental intensities,
- \(\mathbf f_{io}\) is final demand.

### Plain-language explanation

PLCA says: “describe this product in very fine process detail, then follow its process network.”

IO-LCA says: “start from the complete economy, where every industry buys from other industries, and use the Leontief inverse to capture all direct and indirect requirements.”

The first is specific but can miss things outside the chosen system boundary. The second is complete at the economy level but represents an average product mix within each sector.

---

# 3. Hagenaars’ updated hybrid taxonomy

The paper’s most important conceptual contribution is to distinguish **data hybridisation** from **computational hybridisation**.

## 3.1 Data hybridisation

The calculation keeps the structure of the original PLCA or IO-LCA model, but some data are replaced or supplemented.

### Path exchange method (PXC)

PXC uses structural path analysis to identify important IO nodes or paths and replaces selected aggregate coefficients with product-specific process information.

**Purpose:** increase precision while preserving the IO system boundary.

**Strengths**
- complete IO system boundary,
- can target important nodes,
- relatively low dependence on price data compared with other approaches,
- suitable for product benchmarking.

**Weaknesses**
- time- and expertise-intensive,
- automated implementations reported in the literature are not necessarily publicly available,
- requires reliable process-to-sector matching.

### Matrix augmentation (MA)

This is the key method for the proposed health-sector project.

**Definition:** disaggregate an existing IO sector or add one or more new sectors using process or other detailed data.

Examples in the reviewed literature include splitting broad construction sectors into individual materials and adding emerging biofuel technologies.

**Why it is attractive**
- low data dependency relative to more integrated methods,
- only the selected sector or sectors need to be altered,
- quick enough for case-study screening,
- does not require building a full process-LCA database.

**Critical warning from Hagenaars**

Many MA studies simply scale the new sector according to the parent sector’s existing structure. Hagenaars explicitly warns that this practice limits the benefit of augmentation.

For health-sector disaggregation, the implication is decisive:

> **Do not create “hospital”, “GP”, “dentist”, “laboratory”, etc. by copying the same parent health-sector recipe and changing only output shares.**

The children must have meaningfully differentiated input structures, preferably from Danish information, with donor data used only where Denmark-specific information is unavailable.

### Classic tiered hybrid LCA

Classic THL adds IO estimates to selected parts of a process-based LCA.

It is the most frequently used method in the review, but also the method with the weakest consistency.

A major result is that **79% of reviewed classic THL studies did not address double counting explicitly**.

The paper therefore considers classic THL poorly suited to high-stakes comparison or policy if its computational structure is not transparent.

---

## 3.2 Computational hybridisation

Instead of directly merging or replacing data in one parent architecture, the IO and PLCA systems are linked mathematically.

### Integrated hybrid LCA

A useful block-matrix representation is:

\[
\mathbf q_h
=
\mathbf B_h
\mathbf A_h^{-1}
\mathbf f_h
\]

with

\[
\mathbf B_h
=
\begin{bmatrix}
\mathbf B_p & \mathbf B_{io}
\end{bmatrix},
\]

\[
\mathbf A_h
=
\begin{bmatrix}
\mathbf A_p & -\mathbf C_d \\
-\mathbf C_u & \mathbf I-\mathbf A_{io}
\end{bmatrix},
\]

and

\[
\mathbf f_h
=
\begin{bmatrix}
\mathbf f_p\\
\mathbf 0
\end{bmatrix}.
\]

Here:

- \(\mathbf C_u\) is the **upstream cut-off matrix**, which adds IO estimates for missing PLCA inputs;
- \(\mathbf C_d\) is the **downstream cut-off matrix**, which links foreground output back into the economic background.

This structure is particularly relevant when a new technology is introduced into an economy and feedbacks or scenarios matter.

### Systematic tiered hybrid LCA

Systematic THL is similar, but sets the downstream link to zero:

\[
\mathbf q_h
=
\begin{bmatrix}
\mathbf B_p & \mathbf B_{io}
\end{bmatrix}
\begin{bmatrix}
\mathbf A_p & \mathbf 0\\
-\mathbf C_u & \mathbf I-\mathbf A_{io}
\end{bmatrix}^{-1}
\begin{bmatrix}
\mathbf f_p\\
\mathbf 0
\end{bmatrix}.
\]

This makes large-scale process-database hybridisation more tractable and is the architecture associated with the open-source `pylcaio` work in Agez et al.

---

# 4. Hagenaars’ main empirical review findings

## 4.1 Method use

Approximate shares in the 114 studies:

| Method | Share |
|---|---:|
| Path exchange | 9% |
| Matrix augmentation | 22% |
| Classic tiered HLCA | 35% |
| Systematic tiered HLCA | 18% |
| Integrated HLCA | 10% |
| Mixed/theoretical remainder | small remainder |

The exact interpretation of percentages should recognise that a small share of studies combined methods.

## 4.2 Application areas

- Energy systems: about 24%.
- Built environment: about 20%.
- Food, services, corporate footprints and several other domains were less frequently studied.

This is directly relevant to health: **health services are methodologically underdeveloped compared with energy and construction**, so a transparent health-sector augmentation could be a meaningful methodological contribution.

## 4.3 Impact-category coverage

- 53% of reviewed studies addressed only one impact category.
- 39% considered only GHG emissions.
- 73% did not convert inventory flows into characterised impact indicators.

The authors identify the mismatch between IO and PLCA elementary-flow coverage as a major obstacle.

USEEIO is highlighted as an exception because it was designed with a much richer environmental-flow inventory and compatibility with TRACI.

## 4.4 Key robustness challenges

### Double counting

When the same activity is represented by both PLCA and IO data, it must not be counted twice.

The safest accounting principle is:

\[
\text{hybrid inventory}
=
\text{specific data}
+
\text{complementary aggregate data}
-
\text{overlap}.
\]

For **pure matrix augmentation**, double counting is simpler to control if the parent sector is completely replaced by children and all children sum back exactly to the parent.

### Price uncertainty

Monetary and physical datasets often require a price bridge. Price variation can materially affect hybrid results.

For our health disaggregation, one way to reduce this problem is to keep the core Danish augmentation monetary and use physical data only as allocation drivers rather than converting an entire physical LCA into monetary coefficients.

### Capital goods

Capital formation is commonly omitted from intermediate IO recipes, even though capital can be important in health care, particularly hospital buildings, imaging equipment and medical technology.

A Danish health footprint study should therefore report clearly whether capital is:

1. left in final demand,
2. endogenised into health-sector production recipes, or
3. modelled in a separate satellite/capital layer.

Do not mix these treatments implicitly.

### Linearity

PLCA and IO models are linear:

\[
\Delta \mathbf x = \mathbf L \Delta \mathbf y.
\]

They assume fixed production recipes. A 100% increase in demand therefore gives a 100% scaling of inputs unless the model is changed.

This is appropriate for attributional footprinting and small perturbations, but not automatically for a large-scale health-system transition where prices, capacity, substitution, labour constraints and technology change.

---

# 5. What to remember from Hagenaars

| Load-bearing concept | One-sentence definition | Why it matters here |
|---|---|---|
| Aggregation error | Error caused by representing heterogeneous products with one average IO sector | Main reason to disaggregate health |
| Truncation error | Missing processes outside a PLCA system boundary | Reason hybrid LCA exists |
| Matrix augmentation | Splitting or adding IO sectors using more specific data | Best methodological family for the health task |
| Path exchange | Replacing selected important IO paths/nodes with specific process data | Alternative if only key health supply-chain nodes need refinement |
| Classic THL | Case-by-case addition of IO and PLCA results | Easy, but high double-counting risk |
| Systematic THL | Integrated upstream completion of process inventories | Useful for database hybridisation, not the first choice for splitting a national IO health sector |
| Integrated HLCA | Full block-matrix linkage of process and IO systems | Useful for scenarios/new technology feedback |
| Double counting | The same input or burden appears in both data systems | Must be prevented |
| Price bridge | Conversion between physical process units and monetary IO units | Important source of uncertainty |
| Environmental-flow mismatch | IO and PLCA databases cover different pollutants/resources | Prevents some impact categories from being truly comparable |

**Most useful section to re-read personally:** section 4.1.2 on matrix augmentation, followed by section 5.4 on limitations.

---

# 6. Palm et al. (2019): source-anchored paper note

## 6.1 Core question

Palm et al. ask how Sweden can monitor environmental pressures caused by Swedish final consumption both inside and outside Sweden while preserving official Swedish national-account and environmental-account data.

The methodological problem is that a global MRIO is balanced globally but does not reproduce every individual country’s official national accounts exactly.

Their solution is a **linked national SRIO + MRIO model**, later commonly referred to as a **simplified SNAC / coupled model**.

---

## 6.2 The key methodological decision: do not rebalance the global MRIO

Palm explicitly considers approaches that replace the national block inside an MRIO and rebalance the whole global system.

They **do not do that**.

Instead:

1. keep the Swedish national IO structure for the Swedish economy;
2. keep official Swedish environmental data where available;
3. use EXIOBASE only to provide foreign embodied-impact multipliers for Swedish imports;
4. use Swedish bilateral trade information to allocate imports by origin.

This is justified by previous evidence that feedback from Swedish exports returning through global supply chains is small enough that it can be neglected for the national footprint purpose.

### Plain-language explanation

Imagine two models:

- a high-quality official model of Sweden;
- a globally complete model that is less accurate for Sweden but knows the rest of the world.

Palm does **not** throw away the Swedish model and force everything into the global model.

Instead, Sweden is calculated with Swedish data. The global model is asked only:

> “For each krona of this imported product from this foreign origin, how much environmental pressure is generated throughout the foreign supply chain?”

That foreign multiplier is attached to the imports used by Swedish production and final demand.

This is the central idea.

---

# 7. Palm’s equations, step by step

## 7.1 Domestic part

Let:

- \(\mathbf A^d\): domestic technical-coefficient matrix;
- \(\mathbf y^d\): Swedish final demand for domestically produced products;
- \(\mathbf S^d\): Swedish direct environmental intensities;
- \(\mathbf f^h\): direct household environmental pressures.

Then:

\[
\mathbf L^d
=
(\mathbf I-\mathbf A^d)^{-1}.
\]

Domestic production pressure caused by domestic final demand is:

\[
\mathbf f^d
=
\mathbf S^d
\mathbf L^d
\mathbf y^d
+
\mathbf f^h.
\]

### What goes in?

Official Swedish domestic IO coefficients, official domestic final demand and direct Swedish environmental intensities.

### What happens?

The domestic Leontief inverse follows every direct and indirect Swedish production requirement.

### What comes out?

Environmental pressure occurring in Sweden because of Swedish final demand, plus direct household emissions.

### What does it not prove?

It does not estimate environmental pressure occurring abroad. That requires the import module.

---

## 7.2 Imported requirements

Imports used to satisfy Swedish final demand have two components:

\[
\mathbf m
=
\mathbf A^m\mathbf x+\mathbf y^m,
\]

where:

- \(\mathbf A^m\) is the import-input coefficient matrix;
- \(\mathbf y^m\) is direct final demand for imported products;
- \(\mathbf x=\mathbf L^d\mathbf y^d\).

Hence:

\[
\mathbf m
=
\mathbf A^m
\mathbf L^d
\mathbf y^d
+
\mathbf y^m.
\]

This equation is one of the most important in the whole paper.

It means foreign production is required in two ways:

1. imported inputs are used by Danish/Swedish domestic industries;
2. imported products are bought directly for final use.

---

## 7.3 EXIOBASE multipliers

From EXIOBASE:

\[
\mathbf Q
=
\mathbf S
\mathbf L,
\]

where \(\mathbf S\) is the environmental intensity matrix and \(\mathbf L\) the global MRIO Leontief inverse.

\(\mathbf Q\) therefore gives the full supply-chain environmental pressure per monetary unit of output/final demand for each foreign region-sector combination.

---

## 7.4 Why \(\mathbf Q\) cannot be multiplied directly by Swedish imports

The dimensions do not match because of:

1. currency,
2. product classification,
3. country classification.

Palm therefore constructs transformations.

### Product concordance

A product concordance \(\mathbf G_p\) maps EXIOBASE product detail to the published Swedish product classification.

### Country concordance

A country concordance \(\mathbf G_c\) maps EXIOBASE regions to the much more detailed Swedish bilateral trade geography.

### Bilateral import shares

A matrix \(\mathbf B\) gives the share of each imported product by country of origin.

The mapped multiplier is then weighted by the actual bilateral import structure.

---

## 7.5 Imported footprint

Once the multiplier matrix \(\mathbf Q^t\) is compatible with Swedish imports:

\[
\mathbf f^m
=
\mathbf Q^t
\left(
\mathbf A^m
\mathbf L^d
\mathbf y^d
+
\mathbf y^m
\right).
\]

---

## 7.6 Total footprint

\[
\boxed{
\mathbf f^{d+m}
=
\mathbf S^d\mathbf L^d\mathbf y^d
+
\mathbf Q^t\mathbf A^m\mathbf L^d\mathbf y^d
+
\mathbf Q^t\mathbf y^m
+
\mathbf f^h
}
\]

This equation can be read as four blocks:

\[
\text{total footprint}
=
\underbrace{\text{domestic supply chain}}_1
+
\underbrace{\text{foreign inputs to domestic production}}_2
+
\underbrace{\text{direct final imports}}_3
+
\underbrace{\text{direct households}}_4.
\]

This four-part decomposition is also the cleanest implementation structure for Denmark.

---

# 8. Palm’s data

The Swedish application used:

- national IO tables;
- Swedish national accounts final demand;
- Swedish trade statistics;
- Swedish SEEA air emissions for domestic industry;
- EXIOBASE for foreign air emissions;
- EXIOBASE for water, land and material extraction for both domestic and foreign components where Swedish-specific SEEA data were unavailable;
- household direct emissions.

The period is 2008–2014. EXIOBASE was extrapolated beyond its original 2011 data for later years.

The model used product-by-product tables.

---

# 9. Palm’s price treatment

The model was run in current prices.

For physical environmental indicators, changes in physical tonnes, hectares, cubic metres, etc. can still be interpreted physically.

Value added is different because monetary changes mix price and volume effects.

Since a consistent constant-price hybrid model was unavailable, Palm deflated the final calculated value-added component using Swedish final-demand deflators.

### Replication lesson

For Denmark, always decide explicitly whether EXIOBASE multipliers and Danish import values are in a common price year.

Do not multiply a 2019 EXIOBASE intensity by a 2025 current-price import vector without either:

- updating the MRIO,
- deflating the Danish monetary vector to the MRIO price year, or
- conducting a sensitivity analysis.

---

# 10. Palm’s main findings

For Sweden in 2014:

- most investigated environmental pressures were generated predominantly abroad;
- more than 90% of sulphur emissions associated with consumption occurred abroad;
- more than 80% of blue-water use occurred abroad;
- land use was the main exception;
- most pressures declined over 2008–2014 while consumption-based value added rose;
- material consumption did not show the same decline.

The authors interpret this as evidence of absolute decoupling during the observed period, but explicitly warn that the period is too short to determine whether it is a durable structural trend.

### Critique

The linked architecture is highly attractive for official national footprint accounting, but it inherits several assumptions:

1. foreign multipliers depend on the quality of EXIOBASE;
2. countries grouped in the same EXIOBASE region can inherit the same base multiplier;
3. bilateral trade origin is not necessarily the country in which all upstream impacts occur;
4. temporal extrapolation of MRIO structures can become inaccurate;
5. the small-feedback assumption should be tested for the focal country and year;
6. current-price coupling requires careful deflation;
7. product concordance and origin allocation can dominate results for heterogeneous imports.

---

# 11. What to remember from Palm

| Concept | Plain-language definition | Why it matters |
|---|---|---|
| Coupled model | National IO for domestic economy plus MRIO multipliers for imports | Preserves trusted national data |
| Simplified SNAC | National block is not inserted into and rebalanced within the global MRIO | Avoids huge rebalancing exercise |
| Domestic Leontief inverse | Total domestic production needed for domestic final demand | Calculates domestic supply-chain effects |
| Import coefficient matrix | Imported inputs per unit of domestic output | Links domestic production to foreign demand |
| MRIO multiplier | Full global impact per monetary unit of foreign output | Supplies imported footprint intensities |
| Product concordance | Mapping between domestic and MRIO classifications | Required before multiplying matrices |
| Bilateral trade shares | Origin distribution of imports | Gives country/region specificity |
| Feedback effect | Domestic exports that return embodied in imports | Simplified SNAC neglects this |
| Price-year alignment | Ensuring money in \(\mathbf Q\) and \(\mathbf m\) represents compatible purchasing power | Prevents time-series bias |

**Most useful section to re-read personally:** Palm section 2.2, particularly the derivation from the domestic model through the construction of \(\mathbf Q^t\).

---

# 12. Does Palm rebalance the MRIO?

## Short answer

**No.**

Palm deliberately chooses a simplified linked approach **instead of** replacing Sweden inside EXIOBASE and rebalancing the full global MRIO.

This distinction is essential.

There are three different balancing questions that should not be mixed together:

### 12.1 National SUT balancing

Statistics Denmark already reconciles the national SUT so that, for every product:

\[
\text{supply}
=
\text{use}.
\]

This is the official national-accounts balancing problem.

### 12.2 Palm / simplified-SNAC coupling

The national table remains intact and EXIOBASE provides import multipliers.

There is **no full global RAS/GRAS rebalance** merely because the national table and EXIOBASE differ.

### 12.3 Sector-disaggregation balancing

If we split Danish health into children, the augmented table must be constrained so that recombining the children reproduces the original parent sector.

This is a **local matrix-reconciliation problem**, not the same as rebalancing EXIOBASE.

---

# 13. The most important external finding: Statistics Denmark has already implemented the Danish Palm-type method

Statistics Denmark published a 2022 Eurostat technical report titled:

> *Compilation of a consumption based greenhouse gas account for Denmark using coupled models.*

This is effectively the Danish implementation blueprint for the Palm / simplified-SNAC approach.

That report is more directly useful for your planned Danish replication than trying to translate Palm’s Swedish 59-product matrices literally.

## 13.1 Why this changes the replication strategy

You do **not** need to force the Danish 117-industry table into Palm’s original 59 Swedish product groups.

Statistics Denmark already demonstrates the coupled model using the **117 Danish industries**.

Their implementation uses:

- 117 Danish industries;
- EXIOBASE 163 industries;
- 49 EXIOBASE countries/regions;
- bilateral Danish trade;
- a mapping matrix \(\mathbf K\) from 117 Danish industries to 7,987 EXIOBASE region-industry combinations;
- a return aggregation matrix \(\mathbf H\).

---

# 14. Exact Denmark coupled-model equations

## 14.1 Domestic coefficients

\[
\mathbf A^d
=
\mathbf Z
\widehat{\mathbf x}^{-1}.
\]

\[
\mathbf L^d
=
(\mathbf I-\mathbf A^d)^{-1}.
\]

Domestic direct GHG intensity:

\[
\mathbf s^d
=
\mathbf e
\widehat{\mathbf x}^{-1}.
\]

Domestic component of the footprint:

\[
\boxed{
\mathbf e^d
=
\widehat{\mathbf s}^d
\mathbf L^d
\mathbf y^d
+
\mathbf e^h
}
\]

where \(\mathbf e^h\) is direct household fuel combustion.

## 14.2 Imported requirements

\[
\mathbf m^d
=
\mathbf A^m
\mathbf L^d
\mathbf y^d
\]

and

\[
\mathbf m^m
=
\mathbf y^m.
\]

Therefore:

\[
\boxed{
\mathbf m
=
\mathbf m^d+\mathbf m^m
}
\]

## 14.3 EXIOBASE multipliers

For EXIOBASE:

\[
\mathbf Q
=
\widehat{\mathbf S}
\mathbf L.
\]

The 2022 Statistics Denmark model used:

- \(163\) EXIOBASE industries,
- \(49\) countries/regions,
- \(163\times49=7{,}987\) region-industry nodes.

## 14.4 Concordance matrix

Let:

\[
\mathbf K
\in
\mathbb R^{7987\times117}
\]

map the Danish import vector into EXIOBASE region-industries.

Each column of \(\mathbf K\) should sum to one if it is purely a distribution key:

\[
\sum_r K_{rj}=1.
\]

Then:

\[
\boxed{
\mathbf e_m^{exio}
=
\mathbf Q\mathbf K\mathbf m
}
\]

## 14.5 Mapping results back to Danish sectors

If results need to be reported in the Danish 117-industry classification:

\[
\boxed{
\mathbf e^m
=
\mathbf H\mathbf e_m^{exio}
}
\]

with \(\mathbf H\) aggregating EXIOBASE region-industry results back to the Danish classification.

---

# 15. How Statistics Denmark constructed the import key

This is one of the most useful pieces of the Danish technical report.

## 15.1 Country distribution of products

Danish imports are available in much greater product and partner-country detail than the IOT.

The technical report describes approximately:

- 2,350 national-account products,
- 239 partner countries,
- underlying foreign-trade information from roughly 10,000 product lines plus services from the balance of payments.

A normalised country-share matrix is formed:

\[
\mathbf M_c
=
\mathbf C
\left[
\widehat{\mathbf C\mathbf i}
\right]^{-1}.
\]

## 15.2 Product-to-industry market shares

Using the Danish supply matrix:

\[
\mathbf D
=
\mathbf V
\widehat{\mathbf x}^{-1},
\]

where \(\mathbf V\) has approximately 2,350 products by 117 industries.

This identifies which Danish industries produce each product.

For products not produced domestically, Statistics Denmark assigns a likely producing industry.

## 15.3 Country aggregation to EXIOBASE geography

The detailed partner-country system is aggregated to EXIOBASE regions using a mapping matrix \(\mathbf B\):

\[
\mathbf D_c
=
\mathbf D'
\mathbf M_c
\mathbf B.
\]

## 15.4 Danish 117 to EXIOBASE 163

The report first experimented with equal shares when one Danish industry mapped to several EXIOBASE industries.

It then moved to an **empirical key based on EXIOBASE’s observed composition of Danish imports**.

This is an important lesson:

> Never keep an equal split as the final method if observable data can supply empirical shares.

---

# 16. Danish SUT versus Danish IOT: which is more detailed?

## Answer

**The SUT is much more detailed in the product dimension.**

The current Statistics Denmark documentation states that the final Danish SUT compilation works with approximately:

\[
2{,}350\ \text{products}
\times
117\ \text{industries}.
\]

The published symmetric IO system is:

\[
117
\times
117\ \text{industries}.
\]

Thus:

- the **industry dimension is broadly the same**;
- the SUT preserves far more **product heterogeneity**;
- conversion from SUT to symmetric IOT necessarily collapses product detail and imposes a technology assumption.

### Consequence for health disaggregation

If access to the detailed Danish SUT can be obtained, start from the SUT, not the 117 × 117 IOT.

The SUT can show which detailed products are used by the current health industries even when the symmetric IOT has aggregated them.

It is therefore the best Danish base for constructing distinct “recipes” for health subsectors.

---

# 17. Danish-equivalent data map for replicating Palm

| Palm requirement | Danish equivalent | Role |
|---|---|---|
| Domestic IOT | Statistics Denmark 117-industry IO tables, NAIO1 and downloadable CSV/ZIP | \(\mathbf Z^d,\mathbf A^d,\mathbf L^d\) |
| Domestic/import separation | Danish IO tables / underlying use tables distinguishing domestic and imported use | \(\mathbf A^d,\mathbf A^m\) |
| Detailed SUT | Statistics Denmark final SUT, about 2,350 products × 117 industries | Better mapping and health disaggregation |
| Final demand | National accounts, COICOP/COFOG/investment detail | \(\mathbf y^d,\mathbf y^m,\mathbf y^e\) |
| Bilateral goods trade | Statistics Denmark foreign trade by detailed commodity and partner country | \(\mathbf C,\mathbf M_c\) |
| Services trade | Balance of Payments services trade | Country/service origin |
| Domestic air/GHG emissions | Statistics Denmark Energy and Air Emission Accounts / Green National Accounts | \(\mathbf e,\mathbf S^d\) |
| Direct household emissions | Residence-principle energy/emission accounts | \(\mathbf e^h\) |
| Water | Green National Accounts water accounts | environmental extension |
| Materials | Economy-Wide Material Flow Accounts / raw-material equivalents where relevant | environmental extension |
| Land | Land accounts, where compatible | environmental extension |
| Foreign supply chains | EXIOBASE | \(\mathbf Q\) |
| Health output/provider detail | SHA1 health expenditure by provider/function/financing | health split shares |
| Detailed health classifications | DB07 detailed industry classification, ISIC/NACE concordance | target sector definitions |
| Detailed health activity | public health insurance, hospital accounts, staffing/activity records, Danish Health Data Authority where available | recipe and allocation drivers |

---

# 18. Software and code: what the authors report

## 18.1 Palm et al. (2019)

In the supplied main paper:

- programming language: **NOT REPORTED**
- package: **NOT REPORTED**
- code repository: **NOT REPORTED**

The paper points to online supplementary data, but the supplement could not be retrieved here.

Therefore it would be incorrect to claim that Palm provides reusable code.

## 18.2 Statistics Denmark coupled model

The 2022 technical report explains the matrices in substantial detail but does not identify a Python/R/MATLAB package in the report text inspected.

**Software: NOT REPORTED in the technical report.**

## 18.3 Hagenaars et al. (2025)

Hagenaars is a review paper, not a software release.

It discusses automation in prior studies.

Most importantly, systematic tiered hybrid LCA has been automated in work associated with Agez et al. using the open-source **`pylcaio`** framework.

`pylcaio` should not be mislabelled as “the Hagenaars package” and it is **not a ready-made matrix-augmentation package for the Danish health problem**.

## 18.4 USEEIO

The current USEPA modelling architecture uses:

- **`useeior`**, an R package, as the current platform for USEEIO v2+;
- **`stateior`**, R, for state IO construction;
- **`flowsa`**, Python, for environmental/employment flows by NAICS;
- **`LCIAformatter`**, Python, for impact-assessment methods;
- Federal Elementary Flow List tools for environmental-flow harmonisation.

The older USEEIO Python platform is no longer the current model-generation framework.

---

# 19. Recommended implementation stack for this project

This section is **my implementation recommendation**, not software reported by Palm or Hagenaars.

## Python

- `pandas` / `polars`: data preparation.
- `numpy`: dense matrix operations.
- `scipy.sparse`: EXIOBASE-scale matrices.
- `scipy.sparse.linalg`: sparse solves.
- `pymrio`: importing and manipulating EXIOBASE.
- `cvxpy`: constrained health-sector disaggregation.
- `scipy.optimize`: non-negative least squares where a lighter solver is sufficient.
- `pyarrow` / Parquet: reproducible storage of large harmonised tables.
- `pydantic` or explicit validation functions: schema and balance validation.
- `pytest`: reproducibility and matrix-closure tests.

### Important computational recommendation

Do not compute a full matrix inverse unless needed.

Solve:

\[
(\mathbf I-\mathbf A)\mathbf x=\mathbf y
\]

using a sparse linear solver.

This is numerically and computationally preferable to explicitly forming \(\mathbf L\) for large MRIO systems.

---

# 20. Health-sector disaggregation: the Hagenaars-consistent route

## 20.1 Method choice

The closest method in Hagenaars is:

\[
\boxed{\text{Matrix augmentation}}
\]

because the objective is explicitly to split one or more broad IO sectors into more specific sectors.

This is not primarily a tiered-LCA problem.

### Proposed architecture

1. Start with Denmark.
2. Define an ISIC-compatible target health-sector classification.
3. Obtain Danish child-sector output totals.
4. Construct differentiated child input recipes.
5. Reconcile children exactly to the parent IO/SUT margins.
6. Split final demand and direct environmental extensions.
7. validate by exact aggregation back to the original system.
8. only after the Danish method is validated, develop a transferable EXIOBASE-country algorithm.

---

# 21. How detailed is Danish health already?

The 117-industry Danish IO classification already distinguishes approximately:

- hospital activities,
- medical and dental practice activities,
- residential care activities,
- social work activities without accommodation.

This means the Danish starting point is already more specific than a single undifferentiated “health and social work” sector.

However, the detailed Danish DB07 classification contains much more health detail, including separate categories for, for example:

- general medical practice,
- medical specialists,
- dental practice,
- home/visiting nursing and midwifery,
- physiotherapy/occupational therapy,
- psychologists,
- chiropractors,
- other health activities.

This detailed classification provides a logical national target structure, provided every detailed category is mapped transparently back to ISIC Rev.4.

---

# 22. Recommended ISIC Rev.4 backbone

For international comparability, retain a crosswalk to the following ISIC Rev.4 classes:

| ISIC Rev.4 | Sector |
|---|---|
| 8610 | Hospital activities |
| 8620 | Medical and dental practice activities |
| 8690 | Other human health activities |
| 8710 | Residential nursing care facilities |
| 8720 | Residential care activities for mental health / substance-dependence-related care |
| 8730 | Residential care activities for older persons and persons with disabilities |
| 8790 | Other residential care activities |
| 8810 | Social work without accommodation for older persons and persons with disabilities |
| 8890 | Other social work activities without accommodation |

### Classification warning

ISIC has since been revised. Do not mix newer ISIC revisions with the DB07/NACE Rev.2 structure without an explicit concordance.

For this project, if the target is compatibility with Denmark’s 117-industry DB07 and EXIOBASE’s older classifications, **ISIC Rev.4 should remain the backbone**.

---

# 23. What USEEIO adds

USEEIO’s detailed US model contains a much richer health service split than a typical MRIO.

Relevant detailed commodities/industries include:

| USEEIO/BEA code | Description | Indicative ISIC Rev.4 destination |
|---|---|---|
| 621100 | Offices of physicians | 8620 |
| 621200 | Offices of dentists | 8620 |
| 621300 | Offices of other health practitioners | mostly 8690 |
| 621400 | Outpatient care centres | 8620/8690, requires weighting |
| 621500 | Medical and diagnostic laboratories | 8690 |
| 621600 | Home health care services | mostly 8690 |
| 621900 | Other ambulatory health care services | mostly 8690 |
| 622000 | Hospitals | 8610 |
| 623A00 | Nursing and community care facilities | 8710/8730 mixture |
| 623B00 | Residential mental-health, substance-abuse and other residential care facilities | 8720/8790 mixture |
| 624100 | Individual and family services | 8810/8890 mixture |
| 624400 | Child day care services | 8890 or outside the strict health-only boundary |
| 624A00 | Community food, housing and other relief services, including rehabilitation services | mixed 8890/other |

### Crucial interpretation

USEEIO should be treated as a **donor of recipe shape**, not as a source of Danish monetary coefficients.

US prices, insurance arrangements, labour intensity, health-financing structures and service organisation differ fundamentally from Denmark.

The US recipe can answer:

> “What types of supplier sectors tend to differentiate a laboratory from a hospital or dentist?”

It should not answer directly:

> “What exact DKK input coefficient should a Danish laboratory use?”

---

# 24. Denmark-first recipe hierarchy

Use the following evidence hierarchy for each child health sector.

## Tier 1: Danish SUT microstructure

Best source.

Use detailed product rows to estimate health subsectors’ purchases of:

- pharmaceuticals,
- medical devices,
- laboratory supplies,
- energy,
- ICT,
- cleaning,
- catering,
- transport,
- professional services,
- buildings/rent,
- outsourced diagnostics,
- waste management,
- etc.

## Tier 2: Danish System of Health Accounts, SHA1

SHA1 is particularly valuable for **output and expenditure shares**.

It distinguishes providers and functions such as hospitals, ambulatory providers and long-term care and follows the international SHA 2011 framework.

It can supply:

\[
w_k
=
\frac{\text{expenditure/output of health child }k}
{\text{total expenditure/output of parent health sector}}.
\]

## Tier 3: administrative and operational health data

Examples:

- hospital accounts,
- regional accounts,
- staffing/FTE,
- bed-days,
- procedures,
- diagnostic tests,
- floor area,
- energy,
- ambulance kilometres,
- prescriptions,
- public health insurance payments.

These are useful for differentiating specific inputs and direct environmental extensions.

## Tier 4: USEEIO donor profiles

Use only where Danish supply-structure information is missing.

## Tier 5: modelled priors

For countries with weak data, use pooled donor recipes with explicit uncertainty.

---

# 25. Mathematical health-sector disaggregation

Suppose the parent health sector is \(H\) and we want \(K\) child sectors.

## 25.1 Split gross output

Let:

\[
x_H
=
\text{gross output of parent}.
\]

Define shares \(w_k\) such that:

\[
w_k\ge0,
\qquad
\sum_{k=1}^K w_k=1.
\]

Then:

\[
x_k
=
w_kx_H.
\]

Shares should come from Danish data where possible, not USEEIO.

---

## 25.2 Construct prior child recipes

Let:

\[
\widetilde a_{ik}
\]

be the prior amount of input \(i\) per monetary unit of child \(k\).

Possible sources:

- Danish detailed SUT,
- health accounts,
- provider accounts,
- USEEIO donor coefficients.

The unconstrained prior monetary flow is:

\[
\widetilde z_{ik}
=
\widetilde a_{ik}x_k.
\]

---

## 25.3 Reconcile child inputs to the parent

The disaggregation must conserve the original parent’s purchases.

For every supplier \(i\):

\[
\boxed{
\sum_{k=1}^K z_{ik}
=
z_{iH}
}
\]

where \(z_{iH}\) is the original flow from supplier \(i\) to the parent health sector.

This is the most important accounting constraint.

### Value added

If \(v_H\) is parent value added:

\[
\boxed{
\sum_{k=1}^K v_k
=
v_H
}
\]

and each child must satisfy its own column balance:

\[
x_k
=
\sum_i z_{ik}
+
v_k
+
\text{net taxes/other primary inputs}.
\]

---

# 26. Do not forget the health-sector row

Splitting only the **column** gives differentiated production recipes but does not fully disaggregate the symmetric IOT.

You also have to decide how the parent health-sector output is sold to:

- other industries,
- households,
- government,
- NPISH,
- investment if relevant,
- exports.

For each destination \(j\):

\[
\boxed{
\sum_{k=1}^K z_{kj}
=
z_{Hj}
}
\]

and for final demand:

\[
\boxed{
\sum_{k=1}^K y_k
=
y_H.
}
\]

For Denmark, SHA1, COICOP, COFOG and government accounts can help allocate these final-use flows.

---

# 27. Recommended optimisation formulation

A robust approach is a constrained reconciliation rather than simple proportional copying.

## 27.1 Weighted least squares

\[
\min_{\mathbf z\ge0}
\sum_{i,k}
\omega_{ik}
\left(
z_{ik}-\widetilde z_{ik}
\right)^2
\]

subject to:

\[
\sum_k z_{ik}=z_{iH}
\quad\forall i,
\]

\[
\sum_i z_{ik}+v_k=x_k
\quad\forall k,
\]

plus known hard constraints from Danish data.

Higher \(\omega_{ik}\) means the prior is considered more reliable.

## 27.2 Cross-entropy alternative

For strictly positive priors:

\[
\min_{\mathbf z\ge0}
\sum_{i,k}
z_{ik}
\ln
\left(
\frac{z_{ik}}
{\widetilde z_{ik}}
\right)
-z_{ik}
+\widetilde z_{ik}
\]

subject to the same constraints.

This keeps the solution as close as possible to the donor structure while satisfying Danish accounting margins.

## 27.3 GRAS/RAS

RAS/GRAS can be useful when row and column margins are known.

However, because the health-sector task has:

- zero restrictions,
- multiple donor priors,
- potentially negative primary-input items,
- varying reliability across cells,

a general constrained optimisation framework is likely easier to audit than a single blind RAS pass.

---

# 28. Environmental extensions for the child health sectors

Suppose the parent has direct environmental flow \(F_{rH}\) for stressor \(r\).

For children:

\[
F_{rk}
=
s_{rk}x_k.
\]

If no genuinely new direct-emission information is introduced, conservation requires:

\[
\boxed{
\sum_k F_{rk}
=
F_{rH}
}
\]

for every stressor \(r\).

## Preferred allocation drivers

Use physical Danish drivers where available.

| Flow | Potential health allocation driver |
|---|---|
| Electricity | measured kWh, floor area, equipment intensity |
| Heating | floor area, heat consumption |
| Vehicle fuel | ambulance/service vehicle kilometres |
| Waste | kg waste by provider type |
| Anaesthetic gases | hospital procedure/activity data |
| Refrigerants | facility/equipment stock |
| Water | metered use, beds, visits |
| Labour | FTE/payroll |
| Pharmaceuticals | expenditure, prescriptions, hospital pharmacy data |
| Laboratory materials | tests / laboratory expenditure |

This is much stronger than using US direct emissions as Danish intensities.

---

# 29. Double counting in the health matrix augmentation

## Pure partition of a parent sector

If the parent sector is deleted and fully replaced by children:

\[
H
\longrightarrow
\{h_1,\dots,h_K\},
\]

and all parent flows are allocated exactly once, double counting is relatively straightforward to prevent.

Do not keep both:

- the original parent “health” sector, and
- a complete set of children representing all of that parent.

## If PLCA data are inserted

If a detailed process-LCA input is added to a child while the corresponding monetary IO input already remains in the child, the overlap must be removed.

Conceptually:

\[
\text{hybrid child}
=
\text{IO child}
+
\text{specific process data}
-
\text{overlap}.
\]

Agez et al. further warn that a zero can mean:

- true zero,
- unknown/missing.

Treating all zeros as true zeros can create truncation; treating all zeros as missing can create double counting.

---

# 30. Validation tests after health disaggregation

The augmented table should pass all of the following.

## 30.1 Exact recombination test

Aggregate the children back to \(H\).

Require:

\[
\left\|
\mathbf Z_{\text{recombined}}
-
\mathbf Z_{\text{original}}
\right\|
<\epsilon.
\]

Similarly:

\[
\left\|
\mathbf y_{\text{recombined}}
-
\mathbf y_{\text{original}}
\right\|
<\epsilon,
\]

and:

\[
\left\|
\mathbf F_{\text{recombined}}
-
\mathbf F_{\text{original}}
\right\|
<\epsilon.
\]

## 30.2 National totals

Check unchanged:

- total output,
- imports,
- exports,
- value added,
- GDP,
- final demand,
- direct environmental totals, unless intentionally replaced with new data.

## 30.3 Non-negativity

Cells that should be non-negative must remain so.

## 30.4 Productivity

Check:

\[
\rho(\mathbf A)<1
\]

or, practically, confirm that:

\[
(\mathbf I-\mathbf A)
\]

is non-singular and gives economically plausible Leontief outputs.

## 30.5 Footprint closure

If all children are aggregated in final results, the total national footprint should recover the baseline to numerical precision for a pure disaggregation.

If the total changes materially before introducing genuinely new data, the disaggregation algorithm has altered the economic system rather than merely resolving it.

## 30.6 Sensitivity

Vary:

- child output shares,
- donor recipe weights,
- hospital/ambulatory allocation,
- domestic versus US priors,
- price assumptions,
- environmental-allocation drivers.

Report distributions, not just one deterministic result.

---

# 31. Suggested USEEIO donor-recipe procedure

For a given US health donor \(u\):

1. Extract the full intermediate-input vector:
   \[
   \mathbf a^{US}_u.
   \]

2. Aggregate the US supplier sectors to a harmonised ISIC/NACE/EXIOBASE bridge.

3. Remove components that are structural artefacts of the US health financing system if they should not transfer to Denmark.

4. Convert the vector to shares of intermediate consumption:
   \[
   p_{iu}^{US}
   =
   \frac{a_{iu}^{US}}
   {\sum_i a_{iu}^{US}}.
   \]

5. Estimate Danish intermediate-input total for child \(k\):
   \[
   IC_k.
   \]

6. Build a prior:
   \[
   \widetilde z_{ik}
   =
   p_{iu}^{US}
   IC_k.
   \]

7. Replace any available cells with higher-quality Danish observations.

8. Reconcile the complete matrix to Danish parent margins using constrained optimisation.

This transfers **composition**, not US dollar coefficients.

---

# 32. How to extend the health disaggregation from Denmark to EXIOBASE countries

Do not immediately copy one Danish or US recipe into all 49 EXIOBASE regions.

Use a tiered international method.

## Tier A countries

Countries with detailed national SUTs and health accounts:

- country-specific output shares,
- country-specific health input recipes,
- country-specific environmental extensions.

## Tier B countries

Countries with health expenditure/provider data but no accessible detailed SUT:

- national output shares,
- pooled donor recipe shape,
- country-specific labour/energy/price adjustments.

## Tier C countries / rest-of-world regions

- regional output shares,
- hierarchical donor model,
- explicitly larger uncertainty.

Each augmented country must still conserve its original EXIOBASE parent margins.

---

# 33. A practical research design for the Denmark pilot

## Phase 1: reproduce the unmodified Danish IO model

Deliverables:

- load 117-industry IOT,
- reproduce output from final demand,
- reproduce published multipliers,
- establish tests.

## Phase 2: reproduce Statistics Denmark’s coupled footprint

Start with one year for which Denmark and EXIOBASE align well.

Deliverables:

- \(\mathbf A^d,\mathbf A^m,\mathbf L^d\),
- \(\mathbf m\),
- \(\mathbf K\),
- \(\mathbf Q\),
- \(\mathbf H\),
- domestic/imported footprint decomposition.

## Phase 3: reproduce the existing four Danish health sectors

Before disaggregation, create a baseline health footprint for:

- hospitals,
- medical/dental practice,
- residential care,
- social work without accommodation.

## Phase 4: detailed health target classification

Create:

- `dk117_to_isic4.csv`,
- `useeio_to_isic4.csv`,
- `exiobase_to_isic4.csv`,
- `health_target_sectors.csv`.

## Phase 5: output-share model

Estimate \(x_k\) from Danish SHA1 and national accounts.

## Phase 6: child recipe priors

Construct from:

1. detailed Danish SUT/product information,
2. Danish provider/administrative accounts,
3. USEEIO only as a donor prior.

## Phase 7: constrained matrix augmentation

Solve for balanced child columns and rows.

## Phase 8: environmental extensions

Split or replace direct environmental data with physical Danish drivers.

## Phase 9: validation

Run the recombination and footprint-closure suite.

## Phase 10: uncertainty

Monte Carlo or scenario-based perturbation of uncertain shares and recipe priors.

## Phase 11: EXIOBASE transfer

Only after Denmark is validated, develop the multi-country donor hierarchy.

---

# 34. Suggested reproducible project structure

```text
health_io_hybrid/
├── README.md
├── environment.yml
├── pyproject.toml
├── data/
│   ├── raw/
│   │   ├── dst_io/
│   │   ├── dst_sut/
│   │   ├── dst_trade/
│   │   ├── dst_sha/
│   │   ├── exiobase/
│   │   └── useeio/
│   ├── mappings/
│   │   ├── dk117_to_isic4.csv
│   │   ├── useeio_to_isic4.csv
│   │   ├── exiobase_to_isic4.csv
│   │   └── country_to_exiobase.csv
│   └── processed/
├── src/
│   ├── io/
│   │   ├── build_dk.py
│   │   ├── solve_io.py
│   │   └── validate_io.py
│   ├── palm/
│   │   ├── build_import_vector.py
│   │   ├── build_K.py
│   │   ├── build_Q.py
│   │   └── footprint.py
│   ├── health/
│   │   ├── target_classification.py
│   │   ├── output_shares.py
│   │   ├── donor_recipes.py
│   │   ├── reconcile.py
│   │   └── extensions.py
│   └── uncertainty/
│       └── monte_carlo.py
├── tests/
│   ├── test_balance.py
│   ├── test_recombination.py
│   ├── test_concordances.py
│   └── test_footprint_closure.py
└── results/
```

---

# 35. Recommended methodological contribution of the health paper

A publishable contribution should not be:

> “We copied the USEEIO health sectors into Denmark.”

A stronger contribution is:

> **A classification-consistent, margin-preserving matrix-augmentation framework for disaggregating health and social-care sectors in national and multi-regional IO systems using national health accounts, detailed SUT information and donor technology profiles, with explicit uncertainty and exact aggregation closure.**

This would directly respond to Hagenaars’ criticism that simple scaling of parent sectors reduces the benefit of matrix augmentation.

---

# 36. Evidence index

| Claim / concept | Source anchor | Evidence type | Confidence |
|---|---|---|---|
| Hagenaars reviewed 114 studies from 2016–2022 | Hagenaars abstract and section 2 | author methods | High |
| Energy is largest application at 24% | Hagenaars abstract / section 5 | review result | High |
| MA disaggregates or adds IO sectors | Hagenaars section 4.1.2, p. 6 | method definition | High |
| MA used by 22% of reviewed studies | Hagenaars section 4.1.2 / Table 1 | review result | High |
| Parent-sector scaling limits MA benefit | Hagenaars section 4.1.2, p. 6 | author critique | High |
| USEEIO has unusually rich elementary-flow coverage | Hagenaars section 5.3 | review observation | High |
| Palm does not rebalance the full MRIO | Palm section 2.1 | method choice | High |
| Palm uses product-by-product Sweden and EXIOBASE tables | Palm section 2.2 | method specification | High |
| Palm runs 2008–2014 in current prices | Palm section 2.2 | method specification | High |
| Statistics Denmark uses simplified SNAC | Statistics Denmark 2022 report, section 2.3 | official method | High |
| Danish feedback effect accepted as about 0.4% | Statistics Denmark 2022 report, section 2.3 | reported literature-based estimate | High |
| Danish final SUT uses about 2,350 products ×117 industries | Statistics Denmark current SUT/IOT documentation | official metadata | High |
| Published Danish symmetric IOT is 117×117 | Statistics Denmark current IO documentation | official metadata | High |
| USEEIO current platform is `useeior` in R | USEPA GitHub README | software documentation | High |
| USEEIO contains detailed health sectors | USEPA `useeior` classification/crosswalk files | code/data documentation | High |
| Denmark should use USEEIO as donor prior, not direct coefficients | present methodological recommendation | interpretation | Medium-high |
| Constrained reconciliation should conserve parent margins | present methodological recommendation | IO accounting requirement | High |

---

# 37. Understanding questions

## Hagenaars

You should be able to answer:

1. Why does an IO table have lower truncation error but higher aggregation error than a process LCA?
2. Why is matrix augmentation the natural method for splitting a health sector?
3. Why is copying the parent-sector recipe into every child an unsatisfactory disaggregation?
4. What is the difference between classic and systematic tiered hybrid LCA?
5. What do \(\mathbf C_u\) and \(\mathbf C_d\) do?
6. Why can price data dominate hybrid uncertainty?
7. Why is double counting easier to avoid in a pure parent-to-children matrix augmentation than in classic THL?
8. Why does environmental-flow harmonisation matter even after the economic matrices have been hybridised?

### Likely misunderstanding

**Misunderstanding:** “Hybrid LCA automatically produces more accurate results than both PLCA and IO-LCA.”

**Correction:** Hybridisation can reduce particular truncation and aggregation problems, but it introduces mapping, price, double-counting and data-consistency uncertainties. The architecture and data quality determine whether it improves the result.

---

## Palm

You should be able to answer:

1. Why is the domestic footprint calculated with a domestic Leontief inverse?
2. What two terms make up total imported requirements?
3. What does \(\mathbf Q=\mathbf SL\) represent?
4. Why can \(\mathbf Q\) not simply be multiplied by the Danish import vector?
5. What information belongs in the concordance matrix \(\mathbf K\)?
6. Why does simplified SNAC avoid full MRIO rebalancing?
7. What is the feedback effect that the method neglects?
8. How should current-price Danish imports be combined with MRIO multipliers from a different year?

### Likely misunderstanding

**Misunderstanding:** “Palm replaces Sweden in EXIOBASE with the official Swedish IO table.”

**Correction:** That would be the full SNAC route. Palm’s simplified linked model retains the national model separately and uses MRIO multipliers for the import component.

---

# 38. Final methodological recommendation

For the work described here, treat the two tasks as linked but distinct:

## Task A: national footprint coupling

Use the **Palm / Statistics Denmark simplified-SNAC architecture**.

This gives a nationally consistent Danish consumption footprint while preserving global upstream import coverage.

## Task B: health-sector detail

Use **Hagenaars-style matrix augmentation** inside the Danish national model.

The health children should be constructed using:

\[
\text{Danish margins}
+
\text{Danish health/SUT information}
+
\text{USEEIO donor structure where necessary}
+
\text{constrained reconciliation}.
\]

The combined architecture is:

\[
\boxed{
\text{detailed Danish health-augmented IO}
\quad+\quad
\text{EXIOBASE import multipliers}
}
\]

not:

\[
\text{copy US coefficients directly into Denmark}
\]

and not:

\[
\text{replace Denmark in EXIOBASE and rebalance the entire world model}
\]

unless a later research question specifically requires full global feedback consistency.

---

## 39. Checkpoint status

This file is the persistent checkpoint for the two-paper review and the first replication design.

Before a final empirical implementation, the remaining data-access tasks are:

1. obtain the most detailed Danish SUT available for the chosen year;
2. download the exact 117-industry Danish domestic/import IO tables for that year;
3. obtain SHA1 provider/function data at maximum available detail;
4. select the matching EXIOBASE year/version and price basis;
5. construct the exact DB07–ISIC Rev.4–USEEIO–EXIOBASE concordances;
6. retrieve Palm’s online supplement manually if its content is needed for exact historical reproduction;
7. test whether the current Danish climate-footprint publication already provides downloadable mapping artefacts beyond the 2022 technical report.

