# Wiedmann et al. (2011): application of hybrid life cycle approaches to emerging energy technologies, the case of wind power in the UK

## Reading status and coverage ledger

| Source | Pages/sections | Status | Unreadable or missing items |
|---|---|---|---|
| Wiedmann et al. (2011), main article | pp. 1–8, abstract, introduction, methods/data, equations, figures, table, results, sensitivity analysis, comparison with other studies, discussion, associated content, acknowledgements, references | **COMPLETE** | None in main article |
| Supporting Information | Referenced repeatedly by the article for the SUT framework, construction of the upstream matrix, six-GHG results, structural path analysis and additional numerical detail | **NOT SUPPLIED / NEEDS MANUAL CHECK** | Supporting Information itself was not part of the supplied file set |

The main eight-page article has been read sequentially from first page to last. Claims below refer to the main article unless explicitly marked as interpretation.

---

# 1. Core question

The paper asks whether technology-specific life-cycle information can be embedded in an economy-wide input-output framework so that indirect greenhouse-gas emissions of an emerging technology are not truncated by a conventional process LCA.

The case study is UK wind power. The authors compare:

1. **Process LCA** using Ecoinvent;
2. **IO-based hybrid LCA**, where the electricity sector is disaggregated and the wind-power production recipe is replaced with process-informed monetary inputs;
3. **Integrated hybrid LCA**, where the full Ecoinvent process system and an IO system are joined in one block matrix;
4. **Path Exchange Method (PXC)** as an additional way of selectively replacing important IO paths with better data.

### Author claim

Energy-policy models typically focus on direct emissions and can omit upstream emissions required to build and operate low-carbon infrastructure.

### Evidence/result

For the 2 MW offshore wind case, process LCA gives **13.4 g CO2/kWh**, whereas integrated hybrid and IO-based hybrid LCA give **28.7 and 29.7 g CO2/kWh**, respectively (Table 1, p. 4).

### Interpretation

The main empirical lesson is not that one of the hybrid methods is universally “correct”. It is that process truncation can materially understate upstream burdens, while hybridisation can recover omitted upstream supply-chain contributions.

### Critique

The numerical case is partly hypothetical because the authors did not have company-level UK wind-industry accounts and substituted Ecoinvent data for a representative 2 MW offshore turbine. The paper therefore evaluates methods more strongly than it measures the exact 2004 UK wind industry.

---

# 2. Study design and data

## 2.1 Economic background system

The IO framework is a **two-region supply-use system**:

- United Kingdom;
- Rest of World.

The authors explicitly prefer supply-use tables over already-symmetrised IO tables because SUTs retain both commodity and industry detail and can remain rectangular, avoiding aggregation needed to force square IO matrices (Methods, p. 2).

This is highly transferable to the Danish healthcare project: if detailed Danish SUTs are accessible, augmentation before symmetrisation is methodologically preferable.

## 2.2 Process data

The wind technology is represented using Ecoinvent inventory data for a **2 MW offshore wind power plant**.

Included life-cycle elements:

- concrete foundation;
- tower;
- transformer;
- assemblage;
- rotor blades;
- mechanical and electronic nacelle components;
- operation;
- decommissioning;
- grid connection.

Assumptions inherited from Ecoinvent include:

- **20-year lifetime**;
- **30% capacity factor**.

Excluded from the functional-system inventory:

- post-connection transmission and distribution of electricity, treated as a separate economic activity.

## 2.3 Environmental data

The integrated hybrid calculation considers the six greenhouse gases covered by the Kyoto Protocol. The main article reports detailed results primarily for CO2; detailed six-GHG results are said to be in the Supporting Information.

## 2.4 Important absence

Real financial accounts from UK wind-power firms were **not available**. The authors explicitly say that such accounts would have been preferable.

---

# 3. Method 1: IO-based hybrid LCA

## 3.1 Initial disaggregation

The electricity industry and product sectors are first divided into **eleven subsectors**, including wind power, using turnover and electricity-generation information (p. 2).

The initial split is pro rata. Therefore all child subsectors initially inherit the same:

- input structure;
- sales structure;
- technology coefficients.

This is only the starting point, not the final wind technology.

## 3.2 Replace the wind-power input column

The process inventory provides physical quantities of materials, energy and products required over the wind-turbine life cycle.

These quantities are converted to expenditure using unit prices for domestic and imported manufactured goods.

The corresponding entries in the wind-sector use column are then replaced by these process-informed monetary values.

Conceptually:

\[
\text{physical process input}
\xrightarrow{\text{price}}
\text{monetary input}
\xrightarrow{\text{sector concordance}}
\text{IO/SUT input cell}.
\]

## 3.3 Double-counting treatment

If a product is already represented in Ecoinvent, the corresponding original IO transaction is set to zero before the process-informed value is inserted.

Inputs with no corresponding Ecoinvent product are retained from the IO table, particularly services and other items omitted from process LCA.

This produces a hybrid column containing:

- process-specific material inputs;
- residual IO inputs that complete the upstream boundary.

The paper recognises that this zeroing procedure is an approximation and identifies more sophisticated SUT-level subtraction methods as preferable.

## 3.4 Supply/output structure

The resulting SUT has:

- a wind-power **industry column** representing production requirements;
- a wind-electricity **product row** representing output.

The supply table assigns the principal product at **100%**, assuming no coproducts.

The authors stress that this is a hypothetical technology sector representing wind-power operations rather than literally the set of firms whose only activity is wind generation.

---

# 4. Method 2: integrated hybrid LCA

Integrated hybrid LCA retains the process system in physical units and links it explicitly to the IO economy.

Let:

- \(A_{gp}\) = process technology matrix for goods/processes;
- \(A^*_{ss}\) = IO/SUT compound technology matrix;
- \(C_u\) = upstream matrix linking IO sectors to process-system inputs;
- \(C_d\) = downstream matrix linking process outputs back into the IO economy.

The total hybrid requirement matrix is reported as:

\[
\mathbf H =
\begin{bmatrix}
-\mathbf A_{gp} & -\mathbf C_d\\
-\mathbf C_u & \mathbf I-\mathbf A^*_{ss}
\end{bmatrix}.
\tag{1}
\]

Inputs are represented with negative signs and outputs with positive signs.

The process block contains **3,931 processes/goods**; the IO part contains **224 sectors**. The reported total hybrid matrix dimension is 4,827 × 4,827.

## 4.1 Upstream matrix \(C_u\)

\(C_u\) adds monetary IO inputs to process activities where the process database has cut off or omitted requirements.

Its purpose is therefore **completeness**.

## 4.2 Downstream matrix \(C_d\)

\(C_d\) sends outputs from specific physical processes into the background economy.

For wind electricity, the authors assume all annual output of “electricity from wind power, at plant” is used by the “transmission of electricity” sector. They fill that downstream link and set the pre-existing wind-power sales coefficients in the use table to zero to avoid representing the output twice.

## 4.3 Environmental calculation

The total GHG result for one functional unit is obtained by multiplying the hybrid requirements by process and IO environmental extensions and by final demand for the functional unit.

The printed equation is represented conceptually as:

\[
q = [\,B\; B^*\,]\,H^{-1}\,y,
\tag{2, interpreted from the matrix formulation}
\]

where:

- \(B\) = process-level emissions;
- \(B^*\) = sectoral GHG emission intensities;
- \(y\) = demand vector containing one functional unit, here **1 kWh** of wind electricity.

**Note:** the PDF text extraction around Eq. (2) is typographically imperfect. The article's matrix figure and standard hybrid-LCA formulation indicate that the requirements system must be solved/inverted. The Supporting Information should be checked before reproducing the equation in code.

---

# 5. Path Exchange Method

The Path Exchange Method uses structural path analysis to identify individual IO supply-chain paths.

A practitioner can then replace important path information when better primary data become available.

This is presented as a way to increase specificity without constructing the entire integrated hybrid process-IO matrix.

### Why it matters

PXC offers a targeted data-improvement strategy:

1. calculate the IO-based footprint;
2. rank important paths;
3. collect better data for high-contribution paths;
4. replace those paths;
5. recalculate.

For a Danish health-sector study, this could be valuable after a first augmented EEIO model has identified dominant supply chains such as pharmaceuticals, energy, medical equipment, construction or catering.

---

# 6. Key results

## 6.1 Table 1

| Input category | Process LCA | Integrated hybrid LCA | IO-based hybrid LCA | Unit |
|---|---:|---:|---:|---|
| Cement | 2.15 | 2.46 | 8.49 | g CO2/kWh |
| Iron | 0.34 | 1.70 | 1.04 | g CO2/kWh |
| Steel | 5.19 | 16.8 | 14.4 | g CO2/kWh |
| Metals | 0.24 | 0.32 | 0.52 | g CO2/kWh |
| Metal forming | 0.83 | 1.80 | 2.45 | g CO2/kWh |
| Plastics | 3.11 | 3.55 | 1.52 | g CO2/kWh |
| Electricity | 0.38 | 0.39 | 0.39 | g CO2/kWh |
| Transport | 0.25 | 0.33 | 0.27 | g CO2/kWh |
| Disposal | 0.43 | 0.45 | 0.01 | g CO2/kWh |
| Other | 0.50 | 0.94 | 0.64 | g CO2/kWh |
| **Total** | **13.4** | **28.7** | **29.7** | **g CO2/kWh** |

### Interpretation

The two hybrid totals are close, but their internal contributions differ substantially.

Steel is dominant in both hybrid methods, contributing roughly 50–60% of the total.

Cement is much larger in IO-based hybrid LCA because that model fully reflects UK-specific 2004 cement production and emissions, whereas the process data combine Danish, Swiss and broader European technologies.

### What the table does not prove

It does not establish that IO-based hybrid LCA is always more accurate than integrated hybrid LCA. Differences arise from:

- technology geography;
- sector-average versus process-specific representation;
- prices;
- disaggregation assumptions;
- process data quality.

---

# 7. Sensitivity analysis

The authors identify uncertainty from:

- source data;
- imputation and balancing;
- allocation;
- proportionality/homogeneity assumptions;
- concordance;
- sector aggregation;
- regional aggregation;
- temporal mismatch;
- representativeness;
- exchange rates;
- price conversion.

They regard physical-to-monetary conversion as a major uncertainty source in the hybrid models.

Prices are varied by ±20%.

Reported CO2 response ranges:

- Integrated hybrid LCA: approximately **±10.8%**;
- IO-based hybrid LCA: approximately **±19.6%**.

The integrated method is less price-sensitive because only the upstream IO complement is monetised, whereas more of the IO-based hybrid adjustment depends on monetary conversion.

The authors explicitly state that this simple sensitivity test is not a comprehensive uncertainty analysis and recommend Monte Carlo analysis with real industry data.

---

# 8. Comparison with other wind studies

The paper reviews a wide range of previous process and hybrid estimates, including approximately:

- Vestas: 5–8 g CO2/kWh;
- Martínez et al.: about 6.6 g CO2e/kWh for a 2 MW turbine;
- floating turbine study: 11.5–12.2 g CO2e/kWh;
- broader literature: roughly 2–123.7 g/kWh depending on design and assumptions;
- Lenzen and Munksgaard regression estimate: about **31 g CO2/kWh** for a 2 MW turbine.

The latter is close to the two hybrid estimates in this paper.

This comparison supports plausibility but is not a validation against direct observation of the exact UK wind sector.

---

# 9. Discussion and limitations

## 9.1 Surrogate technology rather than observed UK industry

The analysis uses Ecoinvent's 2 MW offshore technology because company data were unavailable.

Therefore it models a representative technology rather than the exact composition of UK wind activity in 2004.

## 9.2 Simplified double-counting correction

IO inputs are set to zero where a process input exists.

The authors acknowledge that a more sophisticated subtraction at SUT level would better eliminate overlap.

## 9.3 Sector-definition choice

The wind-power sector is constructed to include all activities related to wind generation, including turbine manufacturing, rather than modelling a separate turbine-manufacturing industry feeding a pure electricity-generation industry.

This is a modelling choice that affects interpretation.

## 9.4 Temporal mismatch

Process LCA spreads construction, operation and decommissioning across a 20-year lifetime, whereas an IO table represents one accounting year.

Embedding life-cycle-average process inputs into a single annual IO sector assumes that those life-cycle proportions characterise the annual sector.

This can be particularly problematic for rapidly growing technologies.

## 9.5 Capital treatment

Capital investment is **not endogenised** as an intermediate input. It remains in final demand because detailed investment breakdowns for wind were unavailable.

The authors identify better capital treatment as future work.

## 9.6 Transmission and distribution

Grid connection is included, but downstream transmission/distribution is outside the wind LCI and treated separately.

## 9.7 Aggregation and allocation remain

Even hybrid IO methods retain sector-average technologies in the background system. Hybridisation reduces but does not eliminate aggregation error.

---

# 10. Which method do the authors prefer?

The authors conclude that **IO-based hybrid LCA is easier and less expensive to implement** than full integrated hybrid LCA because it requires fewer matrices and less processing.

Advantages of IO-based hybrid:

- easier model construction;
- easier updating;
- national IO tables provide country-specific structures;
- national data are often more current.

Advantages of integrated hybrid:

- physical process flows do not all need monetisation;
- thousands of specific processes can be linked to primary data;
- potentially more technologically specific.

PXC is proposed as a practical way to improve an IO-based model selectively.

---

# 11. Software, code and reproducibility

## Reported software/tool information

The main article acknowledges Reinout Heijungs for advice on:

- Ecoinvent data;
- the **CMLCA tool**;
- hybrid-LCA methods.

However, the main article does **not** provide:

- a programming language;
- a public source-code repository;
- executable model code;
- a package implementing the complete method.

Therefore:

`CODE REPOSITORY: NOT REPORTED`

`PROGRAMMING LANGUAGE: NOT REPORTED`

`CMLCA INVOLVEMENT: mentioned in acknowledgements, but exact computational role is not fully documented in the main article.`

The Supporting Information reportedly contains step-by-step construction details for the SUT and upstream matrix, so it is important for exact replication.

---

# 12. Transferable lessons for Danish healthcare disaggregation

This paper is directly relevant to the proposed Danish health study in five ways.

## 12.1 Start from SUT where possible

The paper explicitly prefers SUTs because they preserve commodity and industry detail.

For Denmark, this strengthens the case for using the detailed Danish SUT before converting to a symmetric IOT.

## 12.2 A proportional split is only an initialisation

The wind subsectors initially receive identical parent technology and sales structure, but the target wind sector is then replaced with more specific data.

That supports the following Danish workflow:

\[
\text{parent health sector}
\rightarrow
\text{pro-rata initial children}
\rightarrow
\text{replace child columns with differentiated evidence}
\rightarrow
\text{reconcile/balance}.
\]

## 12.3 Need both production and sales structure

A disaggregated sector requires not only a new input column but also a consistent output/product row.

For hospitals, GPs, dentists and other providers, both sides must be addressed.

## 12.4 Use donor/process information carefully

Ecoinvent acts as a technology donor because UK company data are missing. The authors are transparent that this weakens representativeness.

USEEIO could play an analogous role for Danish healthcare, but only as donor information rather than as direct evidence of Danish technology.

## 12.5 Quantify price and disaggregation uncertainty

The ±20% price experiment shows that monetisation uncertainty can materially change results. A Danish healthcare augmentation should therefore propagate uncertainty in:

- price conversion;
- donor recipe transfer;
- output shares;
- balancing;
- sector concordances.

---

# 13. Plain-language explanation

Imagine the economy as a map of who buys from whom.

A normal IO table has a broad electricity sector. A process LCA has a detailed list of steel, concrete, plastics and other components of one wind turbine but may stop tracing some upstream services and indirect requirements.

The paper tests two ways to combine them.

### IO-based hybrid

Create a wind-power sector inside the IO table, then overwrite its generic input recipe with a more realistic wind-turbine recipe. The rest of the economy automatically supplies the upstream chain.

### Integrated hybrid

Keep the detailed wind-turbine process system intact and mathematically connect it to the IO economy wherever process data stop.

The first is simpler. The second is more structurally detailed. Both recover substantially more upstream CO2 than the pure process LCA in this case.

---

# 14. What I should remember

1. **SUTs are preferred to symmetric IOTs for augmentation** because they retain product and industry detail.
2. **Pro-rata sector splitting alone does not create new technology.** It is an initial condition.
3. **The target child sector needs a differentiated production column.**
4. **The output/sales side must also be handled.**
5. **Double counting occurs if detailed process inputs are added without removing their aggregate IO counterparts.**
6. **Hybridisation can more than double the process-only result when important upstream requirements are truncated.**
7. **Monetisation is a major uncertainty source.**
8. **Integrated hybrid is more data- and computation-intensive; IO-based hybrid is easier to update.**
9. **PXC can target the most important supply-chain paths for better data collection.**
10. **Life-cycle process data and annual IO tables have different temporal boundaries.**

---

# 15. Load-bearing concepts and understanding check

| Concept | One-sentence definition | Why it matters | Question you should be able to answer |
|---|---|---|---|
| SUT | A system showing products supplied by industries and products used by industries/final demand. | Retains more structure for disaggregation than a symmetric IOT. | Why did the authors prefer a SUT for hybridisation? |
| Pro-rata disaggregation | Splitting a parent sector into children using shares while initially retaining the same technology. | It creates labels/scales, not true technological differentiation. | Why is it only the first step? |
| IO-based hybrid LCA | An IO model whose target sector is modified using process-specific input information. | Easier route to economy-wide completeness. | Which parts of the wind-sector column were replaced and which retained? |
| Integrated hybrid LCA | One matrix system that directly links process activities and the IO economy. | Preserves physical process detail while completing upstream boundaries. | What roles do \(C_u\) and \(C_d\) play? |
| Upstream matrix \(C_u\) | Links missing IO inputs into process activities. | Completes process-system truncation. | Why is \(C_u\) needed if Ecoinvent is already detailed? |
| Downstream matrix \(C_d\) | Links process outputs into the economic background system. | Prevents a process system from being isolated from downstream use. | What did the authors assume about wind electricity output? |
| Double counting | Representing the same economic/process input in both the process and IO layers. | Can systematically overstate footprints. | How did the paper approximately prevent it? |
| Price conversion | Converting physical process inputs into monetary IO-compatible expenditures. | One of the largest sources of uncertainty in IO-based hybridisation. | What happened when prices were varied ±20%? |
| PXC | A method that replaces selected IO supply-chain paths with better data. | Offers a lower-cost alternative to full process-IO integration. | How could PXC guide Danish hospital data collection? |
| Temporal mismatch | Combining multi-year life-cycle process data with one-year IO accounts. | Can distort rapidly changing technologies. | Why is this especially important for growing wind sectors? |

### Most likely misunderstanding

**Misunderstanding:** “The authors split electricity into eleven subsectors, so the wind sector automatically became technology-specific.”

**Correction:** No. The initial split retained identical input and sales structures. Technology specificity was introduced only when the wind input bundle was replaced with process-informed data.

### Section to personally re-read

**Methods and data, pp. 2–3**, especially the sequence from pro-rata disaggregation to process-informed replacement, double-counting treatment and construction of \(C_u\)/\(C_d\).

---

# 16. Evidence index

| Claim/concept | Anchor | Evidence type | Confidence |
|---|---|---|---|
| SUT preferred to IOT because it retains product/industry detail and can remain rectangular | p. 2, Methods and data | Author methodological statement | High |
| Electricity divided into eleven subsectors | p. 2 | Method | High |
| Initial child subsectors retain identical input and sales structures | p. 2 | Method | High |
| 2 MW offshore Ecoinvent process used as surrogate | p. 2 | Data/assumption | High |
| 20-year lifetime and 30% capacity factor | p. 2 | Process-data assumption | High |
| IO transactions corresponding to process-covered products set to zero | p. 2 | Double-counting method | High |
| Integrated matrix uses \(C_u\) and \(C_d\) | p. 3, Eq. 1 and Fig. 1 | Equation/figure | High |
| Process LCA 13.4 vs hybrid 28.7/29.7 g CO2/kWh | p. 4, Table 1 | Result | High |
| ±20% price sensitivity gives ±10.8% integrated and ±19.6% IO-based range | p. 5, §3.2 | Sensitivity result | High |
| Capital investments left in final demand | p. 6, Discussion | Limitation | High |
| IO-based hybrid described as easier/less expensive | p. 6 | Author comparison | High |
| Supporting Information contains additional method/data/SPA detail | p. 6, Associated content | Availability statement | High |
| CMLCA tool mentioned in acknowledgements | p. 6 | Acknowledgement | High |
| Public code repository | Main article | **NOT REPORTED** | High |

---

# 17. Checkpoint

**Main-paper reading:** COMPLETE  
**Supporting Information:** NOT SUPPLIED / NEEDS MANUAL CHECK  
**Paper-level note:** COMPLETE  
**Ready for cross-paper synthesis:** YES, subject to the Supporting Information caveat.
