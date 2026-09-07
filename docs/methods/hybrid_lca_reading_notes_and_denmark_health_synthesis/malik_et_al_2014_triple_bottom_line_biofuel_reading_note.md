# Malik, Lenzen and Geschke: triple bottom line study of a lignocellulosic biofuel industry

> **Bibliographic note:** The project filename contains “2014”, reflecting the manuscript/acceptance period, but the article is published in **GCB Bioenergy (2016), 8, 96–110**, DOI 10.1111/gcbb.12240.

## Reading status and coverage ledger

| Source | Pages/sections | Status | Unreadable or missing items |
|---|---|---|---|
| Malik, Lenzen & Geschke, main article | pp. 1–15: abstract, introduction, case study, materials and methods, augmentation, process data, equations, results, Figures 1–5, Tables 1–5, discussion, acknowledgements, references, SI inventory | **COMPLETE** | None in the main text; some page images were unavailable but corresponding text/captions were readable |
| Supporting Information | Appendices S1–S5, Figures S1–S2, Tables S1–S2 | **NOT SUPPLIED / NEEDS MANUAL CHECK** | Critical step-by-step augmentation procedure is in Appendix S3; data preparation is in Appendix S4 |

The main 15-page article has been read sequentially from first page to last.

---

# 1. Core question

The paper asks what the **social, economic and environmental consequences** would be if a future lignocellulosic ethanol industry were developed in the Green Triangle region of Australia.

The authors go beyond a conventional process LCA in three ways:

1. use **IO-based hybrid LCA** to capture complete upstream supply chains;
2. calculate **triple bottom line (TBL)** indicators: employment, economic stimulus, energy use and greenhouse-gas emissions;
3. include some consequences for **competing/displaced activities**, especially pulp/paper production that loses forestry biomass and crude-oil refining displaced by biofuel.

The model is therefore partly attributional in its IO mechanics but includes selected counterfactual/displacement adjustments.

---

# 2. Case study and system scope

## 2.1 Geography

The Green Triangle spans approximately 6 million hectares across south-eastern South Australia and south-western Victoria.

It contains substantial hardwood and softwood plantations, wood processing, pulp/paper and sawmilling activities and established transport infrastructure.

## 2.2 Feedstocks

The study models 19 feedstock scenarios, differentiated by:

- hardwood versus softwood;
- pulplogs, forest/harvest residues and sawmill residues;
- transport distances between feedstock source and cellulose refinery.

Transport distances for most forestry scenarios are 50, 100, 150 or 200 km; sawmill residues are represented at 10 km.

## 2.3 Why displacement matters

The same forestry biomass is already used by pulp, paper and wood-related industries. Diverting it to ethanol therefore creates an opportunity cost.

The study explicitly estimates lost employment and economic stimulus in pulp, paper and paperboard production rather than reporting only gains from the new biofuel sector.

---

# 3. Conceptual framework: hybrid LCA and triple bottom line

The authors contrast:

- **process analysis (PA):** technologically detailed but truncated because it follows a finite set of processes;
- **input-output analysis (IOA):** complete upstream economy but sector-averaged;
- **hybrid LCA:** combines detailed bottom-up process information with top-down IO completeness.

### Author claim

Hybrid LCA provides a “best-of-both-worlds” combination of specificity and system completeness.

### Evidence in this paper

The production-layer analysis shows that truncating the cellulose-refining supply chain at layer 2 would omit more than half of several impacts; even truncating at layer 3 still omits sizeable shares.

### Critique

The IO background removes formal upstream truncation within the represented monetary economy, but it does not remove all modelling error. Aggregation, classification, proxy process data, monetary valuation and the environmental-account construction remain sources of uncertainty.

---

# 4. IO database and supply-use structure

The study uses the **Australian Industrial Ecology Virtual Laboratory (IELab)** MRIO system.

The MRIO covers:

- **19 Australian regions**;
- **344 industries per region**;
- Rest-of-World imports/exports;
- supply \(V\);
- use \(U\);
- value added \(v\);
- final demand \(y\);
- margins/taxes \(M\);
- satellite accounts \(Q\).

The authors explicitly describe the model as following a **supply-use structure**.

This is highly relevant to the Danish health-sector project because the augmentation is performed by adding both rows and columns to a supply-use MRIO rather than manipulating only a symmetric IO coefficient matrix.

---

# 5. Environmental, social and economic satellite accounts

The satellite block contains four main indicators:

1. **employment**;
2. **economic stimulus**;
3. **energy use**;
4. **greenhouse-gas / CO2 emissions**.

Data sources include:

- Australian Bureau of Statistics for employment and IO data;
- Bureau of Resources and Energy Economics for energy;
- Department of Climate Change and Energy Efficiency for GHG factors;
- economic stimulus constructed as intermediate purchases of goods and services.

The augmented feedstock and refinery sectors receive their own direct satellite values.

---

# 6. Matrix augmentation: the central transferable method

The original MRIO does not contain separate Green Triangle feedstock operations or cellulose refining.

The authors therefore create new sectors.

## 6.1 Number of new sectors

They add:

- 19 feedstock scenario rows and columns;
- 19 cellulose-refining scenario rows and columns.

So **38 new rows and 38 new columns** are added to the South Australian part of the MRIO.

## 6.2 What is placed in the new columns?

The columns contain **production recipes**, that is, the inputs required to operate each new activity.

For forestry/feedstock operations the authors combine:

- transport-cost data;
- fixed and variable truck-cost categories;
- physical/monetary process information;
- IO forestry-sector data to fill missing process categories.

For cellulose refining they combine:

- NREL detailed capital and operating cost data for lignocellulose-to-ethanol conversion;
- IO petrol/diesel sector information for missing categories such as food, communication, trade, business services and personal services.

This is a clear example of a **hybrid recipe**:

\[
\text{new sector recipe}
=
\text{bottom-up process data}
+
\text{IO gap-filling data}.
\]

## 6.3 What is placed in the new rows?

The horizontal sections of the augmented use matrix represent the **sales structures** of the new scenarios.

The supply matrix records the monetary output of feedstocks and lignocellulose converted to ethanol.

The paper's Figure 3 explicitly labels:

- vertical region I = production recipes;
- horizontal region II = sales structures;
- supply block III = monetary output.

This is crucial for replication: **a new sector is not only a new input column. It also needs an output/sales representation.**

## 6.4 Scale

The new process recipes are scaled to the tonnes of feedstock harvested and processed under each scenario.

This provides a direct physical-to-economic scaling mechanism.

---

# 7. Data gap filling

The authors do not insist that bottom-up process data contain every IO category.

Instead, they explicitly fill missing categories from an analogous IO sector.

Examples:

- forestry IO data fill gaps in feedstock operations;
- petrol/diesel IO data fill selected service/other gaps in cellulose refining.

This is one of the strongest transferable lessons for Danish healthcare.

A health-sector child column could similarly be built as:

\[
\mathbf z_k
=
\mathbf z_k^{\text{Danish observed}}
+
\mathbf z_k^{\text{health-admin}}
+
\mathbf z_k^{\text{donor residual}},
\]

provided parent-sector totals are preserved and donor assumptions are made explicit.

---

# 8. Direct satellite data for new sectors

For each feedstock/refinery scenario the authors create direct TBL values.

Examples:

- employment from FTE-per-tonne parameters;
- energy from fuel quantities/energy-content factors and prices;
- GHG emissions from carbon-content factors;
- sequestration from wood-specific CO2 sequestration factors and biomass density.

These values are inserted as new satellite-account columns aligned with the new economic sectors.

This is analogous to splitting a Danish health-sector environmental extension using sector-specific physical drivers rather than simply copying the parent intensity.

---

# 9. IO equations

Let:

- \(A\) = direct requirements matrix;
- \(y\) = final-demand vector;
- \(L=(I-A)^{-1}\) = Leontief inverse;
- \(Q\) = satellite account;
- \(q=Q\hat{x}^{-1}\) = direct satellite intensity;
- \(m=qL\) = total multiplier.

The paper uses employment as the explanatory example, but the same structure is applied to economic stimulus, energy and CO2.

## 9.1 Direct and total impact

The Leontief inverse incorporates all upstream rounds:

\[
L=(I-A)^{-1}.
\]

Total intensity:

\[
m=qL.
\]

### Meaning

A direct intensity tells us what happens in the target activity itself per unit of output.

A total multiplier adds all upstream suppliers required directly and indirectly.

---

# 10. Production layer decomposition

The paper expands the Leontief inverse as a power series:

\[
L=I+A+A^2+A^3+\cdots.
\]

For a final-demand shock \(y^*\):

\[
Q
=
q(I+A+A^2+A^3+\cdots+A^n)y^*,
\tag{1}
\]

or:

\[
Q
=
qy^*+qAy^*+qA^2y^*+qA^3y^*+\cdots+qA^ny^*.
\tag{2}
\]

Interpretation:

- \(qy^*\): direct/on-site effect;
- \(qAy^*\): first-order suppliers;
- \(qA^2y^*\): suppliers of suppliers;
- etc.

For industry-by-industry contribution the paper writes:

\[
Q
=
q\#Ly^*
=
q\#y^*+q\#Ay^*+q\#A^2y^*+\cdots,
\tag{3}
\]

where \(\#\) denotes element-wise multiplication.

### Why it matters

This decomposition visualises where truncation occurs if a conventional process study stops after a few supplier tiers.

---

# 11. Commodity breakdown

The paper also decomposes impacts by the **immediate operating inputs** purchased by the target sector.

From Eq. (1):

\[
Q
=
q(I+A+A^2+\cdots)y^*
=
qy^*+q(I+A+A^2+\cdots)Ay^*,
\tag{4}
\]

and:

\[
Q
=
q\#y^*+qL\#Ay^*.
\tag{5}
\]

The first term is direct impact; the second attributes indirect impact to the target sector's immediate inputs.

For healthcare this is particularly useful because it can rank whether pharmaceuticals, equipment, electricity, construction, catering, ICT or transport dominate the footprint.

---

# 12. Main numerical results

## 12.1 Economic and employment effects

For the highlighted hardwood-pulplog scenario:

- around **300 jobs** are lost in the pulp/paper supply chain;
- around **2,800 jobs** are created by the biofuel supply chain;
- net gain approximately **+2,500 jobs**.

Economic stimulus:

- approximately **65 million AUD** lost in displaced economic activity;
- approximately **880 million AUD** gained;
- net approximately **+815 million AUD**.

The authors summarise the losses as only about 10% of the new employment/economic gains.

## 12.2 Energy return on investment

EROI ranges from **2.7 to 5.2** across the scenarios.

The value declines as feedstock transport distance increases.

Sawmill-residue scenarios at 10 km have the highest reported EROI values, around 4.9–5.2.

## 12.3 Carbon balance

For the highlighted scenario, the authors report:

- around **358 kt CO2 sequestered** in biomass;
- total production emissions sufficiently smaller that net sequestration is about **298 kt CO2**.

They therefore describe the cellulose-refining industry as a **net carbon sequester**.

### Critique

This conclusion is conditional on the paper's sequestration accounting and system boundary. The main article does not present a dynamic carbon-stock model, alternative forest baselines, indirect land-use change or detailed timing treatment. The “net carbon sequester” result should therefore be interpreted within the model's stated biomass/sequestration assumptions, not as a universal property of lignocellulosic ethanol.

---

# 13. Production-layer results and truncation

For the highlighted cellulose-refining scenario:

### If analysis stopped at layer 2

The paper reports omitted shares of approximately:

- **26% economic stimulus**;
- **57% employment**;
- **56% energy**;
- **57% GHG**.

### If analysis stopped at layer 3

Omitted shares are still approximately:

- **8% economic stimulus**;
- **21% employment**;
- **31% energy**;
- **27% GHG**.

More than 95% of all four impacts are accumulated by the first five production layers.

### Interpretation

This is a concrete demonstration of why supply-chain truncation can be material and why IO completion changes the result.

---

# 14. Direct versus total intensities

Table 3 shows large differences between direct intensity \(q\) and total multiplier \(m\).

For example, cellulose refining may have very low direct energy/GHG intensity relative to its total supply-chain intensity.

This means policy conclusions based only on facility emissions can be misleading.

The same is likely to apply to healthcare: hospitals may have moderate direct emissions but substantial upstream impacts through pharmaceuticals, equipment, construction, energy and services.

---

# 15. Immediate supplier hotspots

Table 4 identifies the top five immediate suppliers for the highlighted cellulose-refining scenario.

Industrial machinery/equipment is the largest contributor across all indicators:

- employment: **76.6%**;
- stimulus: **71.0%**;
- energy: **58.3%**;
- CO2: **58.5%**.

Hardwood pulplogs are second:

- employment: **13.9%**;
- stimulus: **21.9%**;
- energy: **35.1%**;
- CO2: **34.8%**.

### Why it matters

A small number of immediate inputs can dominate a hybrid footprint even though the total footprint extends through many upstream layers.

For healthcare, this supports prioritising high-impact inputs for better primary data rather than trying to improve every cell equally.

---

# 16. Treatment of displaced industries

The study applies a negative demand shock to the pulp/paper sector corresponding to forestry biomass diverted to biofuel production.

This estimates losses in:

- employment;
- economic stimulus;
- upstream activity.

The treatment is useful but partial.

The paper itself cites later literature warning that attributional LCA can mislead when used to estimate mitigation consequences. The study does not implement a full equilibrium or behavioural consequential model.

Therefore the displacement analysis should be read as a structured IO counterfactual rather than a market-equilibrium forecast.

---

# 17. Strengths

1. **Detailed augmentation rather than simple sector splitting.**
2. **Rows and columns are both created.**
3. **Process gaps are transparently filled using IO data.**
4. **New direct satellite accounts are created for the inserted sectors.**
5. **Multiple sustainability indicators share one consistent system boundary.**
6. **Production-layer decomposition demonstrates truncation quantitatively.**
7. **Competing/displaced industries are considered rather than ignored.**
8. **The regional MRIO permits subnational impacts.**

---

# 18. Limitations and methodological critique

## 18.1 Supporting Information is essential for exact replication

Appendix S3 reportedly provides the step-by-step insertion algorithm, while Appendix S4 gives process-data preparation.

Because the supplied file does not contain these appendices, an exact replication of their row/column insertion cannot yet be claimed.

`AUGMENTATION ALGORITHM DETAILS: NEEDS MANUAL CHECK IN SUPPORTING INFORMATION.`

## 18.2 Scenario sectors are hypothetical

The cellulose industry does not yet exist at the represented scale. The model combines engineering/design data and analog IO categories.

## 18.3 Data vintages are mixed

IO data, process design data, fuel prices, energy statistics and other parameters come from different years.

The article does not present a comprehensive temporal harmonisation/deflation analysis in the main text.

## 18.4 Uncertainty is not quantified comprehensively

The article reports scenario variation by feedstock and distance but does not perform a full Monte Carlo uncertainty propagation across process costs, concordance, prices and IO coefficients.

## 18.5 Carbon sequestration interpretation is model-bound

The paper's negative-carbon conclusion depends on the treatment of forest biomass and sequestration and should not be generalised outside that boundary.

## 18.6 Economic stimulus is not welfare

A larger gross-output multiplier indicates more supply-chain activity. It does not by itself demonstrate greater social welfare, productivity or cost-effectiveness.

## 18.7 IO linearity

The standard Leontief system assumes fixed technical coefficients and no supply constraints or price responses. The displacement calculations therefore do not represent market equilibrium.

---

# 19. Software, computation and code availability

The paper reports use of the **Australian Industrial Ecology Virtual Laboratory (IELab)** as the MRIO compilation and analytical environment.

It thanks Sebastian Juraszek for managing advanced computation requirements and acknowledges NeCTAR's Industrial Ecology Virtual Laboratory infrastructure.

However, the main article does **not** report:

- a standalone programming language used for the analysis;
- a public code repository for this exact paper;
- an executable script implementing the 38-sector augmentation.

Therefore:

`CODE REPOSITORY FOR PAPER: NOT REPORTED`

`PROGRAMMING LANGUAGE: NOT REPORTED`

`COMPUTATIONAL PLATFORM: IELab / NeCTAR infrastructure`

Exact insertion instructions are said to be in Supporting Information Appendix S3.

---

# 20. Transferable method for Danish healthcare

The paper suggests a direct architecture for health-sector augmentation.

Suppose an existing parent health sector \(H\) is split into children \(k\).

## Step 1: define child activities

For example:

- hospitals;
- GP practices;
- specialists;
- dentists;
- physiotherapy;
- psychological services;
- home nursing;
- other health activities.

## Step 2: construct child production recipes

Use Danish bottom-up information where possible:

- payroll/FTE;
- medicines;
- equipment;
- energy;
- cleaning;
- ICT;
- transport;
- property services.

## Step 3: use IO/donor data only to fill gaps

This mirrors Malik's use of forestry and petrol/diesel IO data for categories absent from bottom-up process data.

## Step 4: construct child sales/output rows

Use Danish SUT final-use/provider information, SHA or other output-destination evidence.

## Step 5: enforce accounting closure

For every parent input \(i\):

\[
\sum_k z_{ik}=z_{iH}.
\]

For every destination \(j\):

\[
\sum_k z_{kj}=z_{Hj}.
\]

And:

\[
\sum_kx_k=x_H.
\]

## Step 6: add child-specific environmental extensions

Use physical drivers where possible.

## Step 7: analyse production layers and commodity breakdown

This identifies the most important upstream health supply chains and where better data would yield most value.

---

# 21. Plain-language explanation

The authors take an Australian economic map that does not contain a cellulose-refining industry and **create one inside the map**.

To do that properly, they need to answer four questions:

1. What does the new industry buy?
2. Who buys its output?
3. How large is the industry?
4. What employment, energy and emissions occur directly inside it?

Detailed engineering data answer much of question 1. Existing IO sectors fill missing expenditure categories. New rows and columns answer questions 1 and 2. Physical scenario data determine scale. New satellite-account columns answer question 4.

Once inserted, the ordinary Leontief model traces all upstream consequences.

This is precisely why the paper is useful for healthcare disaggregation.

---

# 22. What I should remember

1. Matrix augmentation requires **both rows and columns**.
2. A new column is a **production recipe**.
3. A new row is a **sales/output structure**.
4. Bottom-up data can be incomplete; IO data can fill residual categories.
5. The new sector also needs its own direct environmental/social satellite values.
6. The Leontief inverse converts direct requirements into complete upstream requirements.
7. Production-layer decomposition shows quantitatively what a truncated process boundary misses.
8. Commodity breakdown identifies the immediate inputs driving the total footprint.
9. Scenario/displacement shocks are not the same as equilibrium forecasting.
10. Exact augmentation details are in the missing Supporting Information, so main-text reading alone is insufficient for exact code replication.

---

# 23. Load-bearing concepts and understanding check

| Concept | Definition | Why it matters | Question you should answer |
|---|---|---|---|
| Matrix augmentation | Adding new rows/columns to represent activities absent from the IO system. | Core method for health-sector disaggregation. | Why are both a row and a column needed? |
| Production recipe | Vector of intermediate inputs required by a new activity. | Determines its direct technology. | How did Malik construct refinery recipes? |
| Sales structure | Distribution of the new sector's output to users. | Completes the output side and preserves balance. | Where is the sales structure represented in Fig. 3? |
| IO gap filling | Using an analogous IO sector for input categories absent in process data. | Makes incomplete bottom-up inventories compatible with economy-wide models. | Which sectors were used to fill forestry/refinery gaps? |
| Satellite account | Direct social/environmental quantity aligned with sector output. | Enables footprints beyond monetary flows. | Which four satellites were analysed? |
| Leontief multiplier | Direct intensity multiplied by total upstream requirements. | Produces complete direct + indirect impact. | Why is \(m=qL\) larger than \(q\)? |
| Production layer | A tier in the upstream supplier chain. | Demonstrates truncation. | What is omitted if the system stops at layer 2? |
| Commodity breakdown | Attribution of indirect impact to immediate purchased inputs. | Identifies actionable hotspots. | Which immediate input dominated the refinery results? |
| Displacement shock | Negative IO demand representing activity crowded out by the new system. | Prevents counting gains without some losses. | What industry was displaced by forestry diversion? |
| EROI | Energy delivered relative to energy required. | Tests whether the biofuel provides net energy. | Why does EROI fall with transport distance? |

### Most likely misunderstanding

**Misunderstanding:** “The authors simply copied an existing Australian sector and renamed it cellulose refining.”

**Correction:** They construct process-informed production recipes from NREL and forestry/transport data and use existing IO sectors only to fill selected missing categories.

### Section to personally re-read

**Materials and methods, pp. 4–7**, especially “Augmentation of the MRIO table with process data”, “Process data” and the production-layer equations.

---

# 24. Evidence index

| Claim/concept | Anchor | Evidence type | Confidence |
|---|---|---|---|
| 19 regions and 344 industries per Australian region | pp. 3–4, IO database | Model scope | High |
| 38 new rows and columns inserted | p. 4, Augmentation | Method | High |
| New columns contain production recipes | pp. 4–5 | Method | High |
| IO forestry/petrol-diesel data fill missing process categories | p. 4 | Method | High |
| Satellite accounts extended for new sectors | p. 5 | Method | High |
| Fig. 3 vertical cells are production recipes; horizontal cells sales structures | p. 7 | Figure interpretation stated by authors | High |
| PLD equations use Leontief power series | p. 6 | Equations 1–3 | High |
| Layer 2 truncation omits 57% employment, 56% energy, 57% GHG | p. 11 | Result | High |
| Around 2,800 jobs created and 300 lost | p. 12 | Result | High |
| EROI 2.7–5.2 | p. 14, Table 5 | Result | High |
| Net sequestration around 298 kt CO2 in highlighted case | p. 11 | Result | High |
| Exact insertion procedure is in Appendix S3 | pp. 4, 7, 15 | Availability statement | High |
| Public code repository | Main article | **NOT REPORTED** | High |

---

# 25. Checkpoint

**Main-paper reading:** COMPLETE  
**Supporting Information:** NOT SUPPLIED / NEEDS MANUAL CHECK  
**Paper-level note:** COMPLETE  
**Ready for synthesis:** YES, subject to the SI caveat.
