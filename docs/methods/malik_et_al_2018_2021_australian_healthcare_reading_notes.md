# Complete reading notes: Malik et al. (2021), Malik et al. (2018), and the 2018 supplementary appendix

## Scope and completion status

These notes cover the three supplied sources in full, page by page:

1. Malik et al. (2021), *Environmental impacts of Australia’s largest health system*, 12 pages.
2. Malik et al. (2018), *The carbon footprint of Australian health care*, 9 pages.
3. Supplementary appendix to Malik et al. (2018), *The carbon footprint of Australian healthcare*, 17 pages.

The indexed text was checked against rendered PDF pages for the important equations, figures and tables. The mathematical notation in the supplementary appendix was visually verified on the rendered pages because some equation symbols were corrupted by text extraction.

The 2021 article states that additional supplementary material exists online, but that supplementary file is not one of the three supplied sources. Therefore:

`2021 ONLINE SUPPLEMENT: NOT PROVIDED IN THE SUPPLIED CORPUS / NEEDS MANUAL CHECK FOR A FULL REPLICATION AUDIT`

This does not prevent a complete reading of the supplied 12-page 2021 article, but it limits exact replication of items that the article delegates to its supplementary Tables A1-A4 and Figures A1-A3.

---

# Coverage ledger

| Source | Pages / sections covered | Status | Unreadable or missing items |
|---|---:|---|---|
| Malik et al. (2021) | pp. 1-12, abstract, introduction, methodology, equations, limitations, findings, Figures 1-5, Table 1, discussion, conclusion, declarations, acknowledgements, references | Complete for supplied main article | Online supplementary material cited by authors was not supplied |
| Malik et al. (2018) | pp. 1-9, summary, introduction, methods, research-in-context box, Tables 1-3, main figure, discussion, declarations, references | Complete | None in supplied main article |
| 2018 supplementary appendix | pp. 1-17, IO introduction, six-step method, purchaser-price conversion, bridge matrix, uncertainty model, worked example, Tables B1-B2, C1-C2, references | Complete | None after manual visual checking of equations |

---

# Source 1: Malik et al. (2021)

## 1. Core question

The study asks how large the environmental footprint of the New South Wales health system is when both its own activities and the domestic supply chains that support it are considered.

The study measures three environmental indicators for 2017:

- greenhouse gas emissions;
- water use;
- waste generation.

It also asks where those impacts occur:

- within health sectors themselves;
- in upstream supplier layers;
- in different non-health industries;
- across Australian states.

### Author claim

A comprehensive state-level environmental footprint assessment of a health system had not previously been undertaken using this type of hybrid sub-national MRIO framework.

### Interpretation

The paper is an extension of the authors' 2018 national Australian carbon-footprint study. It increases geographical resolution, expands the environmental indicators beyond climate change, and introduces production-layer and inter-regional analyses.

---

## 2. Study design and data

### Geographic scope

The case study is New South Wales, Australia.

The authors build a sub-national MRIO system covering all eight Australian states and territories.

### Economic resolution

The Australian Industrial Ecology Virtual Laboratory, or AUS IELab, contains highly detailed Australian data. The authors use its 2,214 Statistical Area 2 regions and 1,284-sector classification as the basis for constructing a customised model.

The resulting analytical MRIO is:

\[
8 \text{ regions} \times 360 \text{ sectors per region}
\]

The 360-sector classification includes explicit healthcare detail.

### Health-system scope

The health-system sectors are based primarily on ANZSIC Division Q, Health Care and Social Assistance, supplemented by pharmaceutical and administrative categories.

The 16 analytical health sectors are:

1. Hospital services
2. Psychiatric hospital services
3. General practice medical services
4. Specialist medical services
5. Pathology and diagnostic imaging services
6. Dental services
7. Optometry and optical dispensing
8. Physiotherapy services
9. Chiropractic and osteopathic services
10. Other allied health
11. Ambulance services
12. Other health care services
13. Other residential care services
14. Research and administration
15. Medicinal goods
16. Pharmaceutical products

### Health expenditure

The authors use Australian Institute of Health and Welfare expenditure for NSW for financial year 2016-17.

A concordance links the AIHW expenditure information to the health sectors in the MRIO to form the health-system final-demand vector.

### Environmental extensions

The model uses environmental accounts in AUS IELab for:

- greenhouse gas emissions;
- water use;
- waste generation.

The exact construction of every extension is not fully reproduced in the main paper.

---

## 3. Method

### 3.1 Total output

Let:

- \(T\) = \(N \times N\) intermediate transactions matrix;
- \(y\) = \(N \times K\) final-demand matrix;
- \(\mathbf{1}_T\) and \(\mathbf{1}_y\) = summation vectors.

The total output vector is:

\[
\mathbf{x}
=
T\mathbf{1}_T
+
y\mathbf{1}_y
\]

This is the amount each industry must produce to satisfy both intermediate and final demand.

### 3.2 Direct requirements

The direct requirements matrix is:

\[
A = T\hat{x}^{-1}
\]

where \(\hat{x}\) is the diagonal matrix formed from \(\mathbf{x}\).

Element \(a_{ij}\) tells us how much input from sector \(i\) is directly required per unit of output from sector \(j\).

### 3.3 Leontief inverse

\[
L = (I-A)^{-1}
\]

and therefore:

\[
x = Ly
\]

The Leontief inverse traces the complete upstream requirements generated by final demand.

### 3.4 Environmental intensities

Let \(Q\) contain environmental satellite accounts.

The paper defines direct environmental intensities as:

\[
q = Q\hat{x}^{-1}
\]

and total multipliers as:

\[
m=qL
\]

For greenhouse gases, a selected row gives \(q_{\mathrm{GHG}}\) and \(m_{\mathrm{GHG}}\).

The health-system footprint is obtained by applying these multipliers to the health-system expenditure vector \(\tilde{y}\).

Conceptually:

\[
F_{\mathrm{GHG}}
=
m_{\mathrm{GHG}}
\odot
\tilde{y}
\]

with \(\odot\) denoting element-wise multiplication in the authors' presentation.

### 3.5 Production-layer decomposition

A major contribution of the 2021 study is to open the Leontief inverse:

\[
L=(I-A)^{-1}
=
I+A+A^2+A^3+\cdots
\]

This gives a useful supply-chain interpretation:

\[
q_{\mathrm{GHG}}I\tilde{y}
\]

is the direct health-system layer,

\[
q_{\mathrm{GHG}}A\tilde{y}
\]

is the direct-supplier layer,

\[
q_{\mathrm{GHG}}A^2\tilde{y}
\]

is the suppliers-of-suppliers layer, and so forth.

This is more informative for policy than simply reporting a single total footprint because it tells the analyst how far away in the supply chain an impact occurs.

### 3.6 Construction and balancing of the sub-national MRIO

The paper states that AUS IELab uses a reconciliation engine, with KRAS given as an example, to construct customised MRIO tables.

The purpose of reconciliation is to combine multiple primary data sources while producing a table that:

- respects accounting constraints;
- adheres as closely as possible to the raw observations;
- fills data gaps consistently.

For missing inter-regional trade, the authors use non-survey regionalisation techniques.

This is important because complete observed trade matrices between Australian states and sectors are not available.

---

## 4. Key figures and tables

### Figure 1

Figure 1 maps the eight Australian regions in the sub-national MRIO and highlights New South Wales as the health-system case study.

### Figure 2

Figure 2 gives the health-sector contribution to the three footprints.

The largest health-sector hotspot is hospitals.

The text reports:

| Health category | GHG emissions | Water use | Waste |
|---|---:|---:|---:|
| Hospitals | about 25% | about 33% | about 47% |
| Pharmaceutical products | about 21% | about 15% | about 13% |
| Medical goods | about 18% | about 7% | lower than the two categories above |

Pathology and diagnostic services, specialist services and general practice also contribute across the indicators, generally at smaller shares.

### Figure 3

Figure 3 is the production-layer decomposition.

It shows that supply-chain structure differs by indicator.

For GHG emissions, major upstream broad groups include:

- mining;
- agriculture;
- transport and communication;
- utilities.

Mining contributes roughly one-third of the health-system GHG footprint.

For water, agriculture becomes particularly important.

For waste, direct health services are much more dominant than they are for GHG emissions or water.

### Figure 4

Figure 4 gives a commodity-level interpretation of the broad sector groups.

Examples include:

- mining: coal, crude oil and natural gas;
- agriculture: livestock and other agricultural products;
- utilities: electricity and water;
- construction;
- chemicals;
- business services;
- transport.

It demonstrates that a health-system footprint is not simply a footprint of hospitals. It is a footprint of the economic network needed to operate hospitals and other healthcare providers.

### Figure 5

Figure 5 attributes domestic supply-chain impacts to Australian states.

Most domestic impacts are associated with NSW itself, especially waste.

Important boundary caveat: the percentages in Figure 5 explicitly exclude international trade.

### Table 1

Table 1 translates hotspots into possible interventions, for example:

- inhaler substitution for direct GHG emissions;
- water-efficient hospital fixtures;
- waste segregation;
- supplier GHG requirements;
- low-carbon and plant-rich food procurement.

These are illustrative policy options, not intervention-effect estimates produced by the MRIO model.

---

## 5. Results

The estimated annual footprint of the NSW health system is:

\[
7{,}908 \text{ kt CO}_2\text{e}
\]

\[
246 \text{ GL water}
\]

\[
1{,}624 \text{ kt waste}
\]

The authors compare these with NSW totals and report:

- 6.6% of estimated NSW GHG emissions;
- 4% of NSW water use;
- 8% of NSW waste.

### Direct versus upstream impacts

First production layer only:

- GHG emissions: about 11%;
- water use: about 17%;
- waste: about 62%.

First three production layers together:

- GHG emissions: nearly 67%;
- water: about 72%;
- waste: about 90%.

This is one of the most important results.

GHG emissions and water use are predominantly supply-chain problems.

Waste is much more directly associated with healthcare operations.

---

## 6. Interpretation

### Author interpretation

The authors argue that hospital-level sustainability programmes alone are insufficient.

Because most GHG and water impacts occur outside direct healthcare activities, procurement and supplier engagement are necessary.

### My interpretation

The paper's strongest contribution is not the headline percentage. It is the structural decomposition.

It tells policymakers whether to intervene:

- inside the hospital;
- in direct procurement;
- in supplier industries;
- across state boundaries.

For GHG emissions, focusing only on direct hospital fuel use leaves most of the footprint untouched.

For waste, direct operational actions are potentially much more powerful because most waste appears in the first production layer.

---

## 7. Limitations and critique

### 7.1 Static and linear technology

Input-output analysis assumes fixed production relationships and linear scaling.

If health expenditure doubles, the model assumes sectoral output requirements scale proportionally unless the underlying technical coefficients are changed.

It does not model behavioural adaptation, scarcity, nonlinear technological change or price responses.

### 7.2 Data vintage

The table is constructed for 2017 using source datasets as close to 2017 as possible.

Water data are available for 2017, but waste data have more limited temporal coverage.

Therefore the model is a reconciled snapshot, not a perfectly contemporaneous measurement of every input.

### 7.3 Non-survey inter-regional trade

Inter-state trade is partly estimated rather than directly observed.

This is standard regional IO practice when detailed trade data are unavailable, but it adds model dependence to the geographical attribution results.

### 7.4 International supply chains are incomplete

The authors explicitly state that the results do not consider imports.

Figure 5 also excludes international trade.

This is a major limitation for pharmaceuticals, medical equipment and other globally traded inputs.

The model therefore should not be interpreted as a complete global supply-chain footprint of NSW healthcare.

### 7.5 Investment is excluded

The authors state that investments by health sectors are not considered.

This differs from the 2018 national study, which included capital expenditure on buildings.

### 7.6 Environmental categories are limited

Only GHG emissions, water use and waste are included.

The study does not measure biodiversity, toxicity, particulate matter, land use, material extraction or other environmental pressures.

### 7.7 The 6.6%, 4% and 8% comparisons require boundary caution

The numerator is a demand-driven health-system footprint that includes indirect domestic supply-chain impacts.

The comparator is presented as an NSW economy total.

The paper does not provide a detailed reconciliation showing that the numerator and denominator use identical geographic and accounting boundaries.

This does not invalidate the estimates, but the percentage should be interpreted as a benchmarking indicator rather than a perfectly harmonised territorial share without further denominator auditing.

### 7.8 "Hybrid LCA" terminology

The study combines detailed bottom-up health expenditure data with a top-down MRIO model.

This is a valid hybridisation of data sources.

However, it is different from a hybrid LCA in which process inventories physically replace selected IO sectors. The distinction matters when comparing this study with NHS-style hybrid carbon accounting or process-IO hybrid LCA.

### 7.9 Uncertainty

Unlike the 2018 study, the main 2021 article does not present a Monte Carlo uncertainty interval around the reported NSW totals.

Uncertainty from regionalisation, concordance, environmental extensions and data reconciliation therefore remains largely implicit in the headline results.

---

## 8. Plain-language explanation

Imagine NSW Health buys a hospital service.

The hospital buys electricity, food, pharmaceuticals, equipment, cleaning and transport.

Those suppliers in turn buy fuels, chemicals, agricultural products, metals and business services.

The paper builds a map of those economic relationships and follows the spending backwards through them.

It then attaches environmental intensity data to each industry.

That lets the authors estimate not just the pollution occurring in the hospital, but the pollution generated throughout the Australian production network needed to deliver healthcare in NSW.

---

## 9. What to remember

1. 2021 is a sub-national, multi-impact extension of the Australian healthcare footprint method.
2. The model covers 8 Australian regions and 360 sectors.
3. Sixteen health sectors are resolved.
4. The footprint is 7,908 kt CO2e, 246 GL water and 1,624 kt waste.
5. Hospitals dominate all three headline indicators.
6. Pharmaceuticals and medical goods are major hotspots.
7. Only 11% of GHG emissions and 17% of water occur in the first production layer.
8. Waste is different: 62% occurs in the first layer.
9. Production-layer decomposition is one of the paper's most useful methodological contributions.
10. Imports and investment are excluded, so it is not a complete global supply-chain footprint.

---

## 10. Understanding check

| Concept | Plain-language definition | Why it matters | Question you should be able to answer | Likely misunderstanding |
|---|---|---|---|---|
| Sub-national MRIO | An IO model distinguishing several regions inside one country | Allows NSW impacts to be linked to other Australian states | Why is an Australian national IO table insufficient for Figure 5? | Assuming MRIO always means international |
| Health final demand | Spending attributed to healthcare delivery | It is the demand shock that drives the footprint | What exactly is being multiplied through the Leontief system? | Treating "health sector" only as direct hospital production |
| Leontief inverse | Matrix that captures all upstream production rounds | Converts final demand into total supply-chain requirements | Why does \(L\) capture suppliers of suppliers? | Thinking it represents only direct suppliers |
| Environmental intensity | Impact per monetary unit of sector output | Connects economics to environmental accounts | How does a dollar of demand become kg CO2e? | Treating the intensity as product-specific |
| Production layer | Distance from the final-demand sector in the supply chain | Shows how close impacts are to healthcare | What is the difference between \(A\) and \(A^2\)? | Thinking a higher layer means a larger impact |
| KRAS reconciliation | A balancing/reconciliation procedure for inconsistent IO data | Makes a coherent table from multiple data sources | Why is reconciliation necessary? | Assuming raw regional data already balance |
| Non-survey trade estimation | Model-based estimation of inter-regional flows | Needed when observed state-to-state trade is incomplete | Which result is especially sensitive to this assumption? | Treating the trade map as directly observed |
| Hotspot | Sector or supply-chain activity contributing a large share of impact | Helps prioritise interventions | Why is mining a healthcare GHG hotspot? | Thinking mining occurs inside hospitals |

### Section to re-read

Re-read **Section 2.3, Hybrid life-cycle assessment**, especially the production-layer decomposition equations, and **Section 2.3.1, Limitations**.

---

# Source 2: Malik et al. (2018)

## 1. Core question

The study has two explicit aims:

1. Estimate the total carbon footprint caused by Australian healthcare in 2014-15 and express it as a share of Australia's total GHG emissions.
2. Estimate the carbon footprints of individual healthcare expenditure categories.

It is a national, carbon-only study.

---

## 2. Study design and data

### Health expenditure

The study uses AIHW Health Expenditure Australia 2014-15 data.

Total expenditure:

\[
161.637 \text{ billion AUD}
\]

The study models 15 expenditure categories after excluding the medical expenses tax rebate, which is an accounting item without a direct environmental activity.

Aged care is also excluded because it lies outside the AIHW health-expenditure domain used in the study.

### Included boundaries

The AIHW expenditure definition includes:

- public expenditure;
- private expenditure;
- private health insurance;
- patient out-of-pocket expenditure;
- investment in equipment and facilities.

Hospital expenditure includes activities taking place in hospitals, but categories such as pharmaceuticals, research, patient transport and aids/appliances are separated to avoid double counting.

### Economic data

The model begins from detailed Australian national accounts and uses a customised IELab table with 360 economic sectors.

---

## 3. Method

The main article summarises the method, while the supplied supplementary appendix gives the full six-step implementation.

The model is an economic input-output life-cycle assessment driven by healthcare expenditure.

The central relationship is:

\[
\text{Footprint}
=
\text{Expenditure}
\times
\text{CO}_2\text{e intensity}
\]

The intensity includes both direct and upstream emissions.

---

## 4. Main results

Total healthcare footprint:

\[
35{,}772 \text{ kt CO}_2\text{e}
\]

Australian total:

\[
494{,}930 \text{ kt CO}_2\text{e}
\]

Therefore:

\[
\frac{35{,}772}{494{,}930}
\approx 7.2\%
\]

### Largest categories

| Category | Total kt CO2e | Approx. share |
|---|---:|---:|
| Public hospitals | 12,295 | 34% |
| Private hospitals | 3,635 | 10% |
| Other medications | 3,347 | 9% |
| PBS pharmaceuticals | 3,257 | 9% |
| Capital expenditure | 2,776 | 8% |
| Specialist medical services | 2,169 | 6% |

When public hospitals, private hospitals and hospital-related capital expenditure are considered together, hospitals account for more than half of the footprint.

All pharmaceuticals together are about 19-20%.

### Direct versus total emissions

Table 3 gives:

\[
4{,}809 \text{ kt CO}_2\text{e}
\]

as direct emissions and:

\[
35{,}772 \text{ kt CO}_2\text{e}
\]

as total emissions.

Thus the tabulated values imply approximately:

\[
13.4\% \text{ direct}
\]

and:

\[
86.6\% \text{ indirect}
\]

The narrative rounds this to roughly 10% direct and 90% indirect.

---

## 5. Carbon intensities

Selected total intensities:

- pharmaceuticals: approximately \(0.333\) kg CO2e per AUD;
- capital expenditure: approximately \(0.290\) kg CO2e per AUD;
- hospitals: approximately \(0.256\) kg CO2e per AUD;
- aids and appliances: approximately \(0.251\) kg CO2e per AUD;
- community health: approximately \(0.227\) kg CO2e per AUD.

An important distinction is:

\[
\text{total footprint contribution}
\neq
\text{carbon intensity alone}
\]

A category can be a major contributor because:

1. it has a high carbon intensity;
2. expenditure on it is very large;
3. both.

Public hospitals are the clearest example of very large expenditure combined with a substantial total intensity.

---

## 6. Uncertainty

The study reports 68% confidence intervals, corresponding approximately to one standard deviation in the Monte Carlo framework used.

The abstract gives:

\[
35{,}772
\quad
(25{,}398\text{ to }46{,}146)
\text{ kt CO}_2\text{e}
\]

The supplementary appendix reports the same result as:

\[
35{,}772 \pm 10{,}374
\]

### Important internal inconsistency

Table 3 in the main article gives the total row as:

\[
35{,}772
\quad
(25{,}000\text{ to }45{,}748)
\]

This is different from the abstract and supplementary appendix.

The supplied sources do not explicitly explain this discrepancy.

It may reflect the way category-specific intervals were combined or reported, but that explanation is not stated by the authors and therefore should not be assumed.

For replication or citation, the safest practice is to report the central estimate and explicitly identify which uncertainty interval is being used.

---

## 7. Interpretation

### Author interpretation

Australian healthcare was responsible for about 7% of national GHG emissions.

Hospitals and pharmaceuticals are the primary hotspots.

Most emissions are indirect, showing that decarbonisation must address procurement and supply chains.

### My interpretation

The study is most useful as a top-down screening model.

It is very strong for identifying where large categories of expenditure connect to carbon-intensive supply chains.

It is not designed to tell a hospital which specific surgical product or medicine has the lowest life-cycle footprint.

That would require more detailed process or hybrid product-level modelling.

---

## 8. Limitations and critique

### 8.1 One-year snapshot

The footprint is for 2014-15.

The authors explicitly state that sector carbon intensities vary over time, so they do not claim that the 2015 intensities are valid for a historical time series.

### 8.2 Only climate change

The study models CO2e only.

Water, materials, toxicity, land use, air pollution and waste are not included.

### 8.3 Sector aggregation

IO sectors use average technologies.

This becomes increasingly problematic when moving from broad health categories to specific products or procedures.

### 8.4 Bridge-matrix assumptions

The 15 AIHW expenditure categories do not correspond directly to the 360 IO sectors.

The authors therefore construct a binary concordance and then normalise it using sector output.

This is necessary, but the allocation is a model assumption.

The uncertainty analysis does not appear to propagate uncertainty in the sector concordance itself.

### 8.5 Monetary proportionality

The method assumes the environmental footprint scales linearly with expenditure for a fixed intensity.

Higher expenditure therefore produces a larger footprint unless the intensity falls.

This is a property of the model, not empirical proof that every additional dollar of healthcare causes the same marginal emissions.

### 8.6 Imported supply chains

The supplied appendix describes imports as part of the IO accounting structure but does not provide a detailed international MRIO treatment of foreign embodied emissions.

The treatment of upstream emissions physically occurring overseas is therefore not transparent enough in the supplied material to treat the estimate as a fully global supply-chain footprint.

### 8.7 Uncertainty coverage is incomplete

The Monte Carlo simulation perturbs core IO and environmental variables.

The paper does not report probabilistic uncertainty for every modelling choice, including:

- expenditure-category mapping;
- sector classification choices;
- system-boundary choices;
- purchaser-price mapping assumptions.

The reported 68% interval should therefore not be interpreted as total epistemic uncertainty.

---

## 9. Plain-language explanation

Suppose Australia spends one million dollars on a health category.

The IO model knows which industries normally supply the industries connected to that category and how much carbon those industries emit per dollar of output.

It follows those monetary relationships upstream.

The result is a carbon intensity per dollar.

The authors then multiply that intensity by the actual healthcare expenditure.

This is why the method can estimate the footprint of the entire healthcare system without collecting physical inventories for every hospital, medicine and device.

---

## 10. What to remember

1. Australia spent AUD 161.6 billion on health in 2014-15.
2. Estimated healthcare footprint: 35.772 Mt CO2e.
3. This equals about 7.2% of national GHG emissions.
4. Public hospitals alone account for 34%.
5. Public plus private hospitals account for 44%.
6. Pharmaceuticals account for about 19-20%.
7. Capital expenditure contributes about 8%.
8. The table implies about 13% direct and 87% indirect emissions.
9. The model is expenditure-driven and linear.
10. The reported overall uncertainty interval is internally inconsistent between Table 3 and the abstract/SI.

---

## 11. Understanding check

| Concept | Plain-language definition | Why it matters | Question | Likely misunderstanding |
|---|---|---|---|---|
| EIO-LCA | LCA based on monetary IO relationships rather than product inventories | Gives system-wide coverage | Why is it appropriate for national healthcare? | Thinking it is product-specific LCA |
| Expenditure stressor | Money spent that drives the model | Determines scale of demand | What happens if expenditure rises and intensity is unchanged? | Treating expenditure as an environmental flow |
| Direct emissions | Emissions from the sector's own activities | Distinguishes operational impacts | Is purchased electricity necessarily direct in this study? | Confusing GHG Protocol scopes with IO directness |
| Indirect emissions | Emissions in upstream sectors | Explain most of the footprint | Why can a hospital have a large footprint even with efficient boilers? | Looking only at facility fuel |
| Total intensity | Direct plus upstream CO2e per AUD | Converts spending into footprint | Why is it higher than direct intensity? | Thinking "total" means national total |
| Purchaser price | Price paid by the buyer including margins and taxes | Health expenditure is observed at purchaser prices | Why not multiply basic-price intensity directly by AIHW spending? | Ignoring valuation layers |
| Concordance matrix | Mapping between health categories and IO sectors | Categories do not line up automatically | Why is a bridge required? | Assuming sector classifications are identical |
| 68% interval | Approx. one-standard-deviation uncertainty interval | Indicates model variability | Why is it narrower than a 95% interval? | Reading it as a standard 95% CI |

### Section to re-read

Re-read **Methods: Data analysis, Matrix bridge construction, and Statistical analysis**, then the corresponding supplementary Sections B3-B6.

---

# Source 3: 2018 supplementary appendix

## 1. Core role of the appendix

The supplementary appendix is the methodological backbone of the 2018 paper.

It explains how the authors move from:

\[
\text{Australian IO data}
\]

plus

\[
\text{environmental satellite data}
\]

plus

\[
\text{AIHW health expenditure}
\]

to

\[
\text{health-category CO}_2\text{e footprints}.
\]

It also contains the uncertainty model.

---

## 2. The six-step workflow

### Step 1: collect health expenditure

Obtain expenditure for the 15 AIHW categories for 2014-15.

### Step 2: construct the Australian IO system

Using ABS data and Australian IELab, construct:

- \(T\): 360-sector intermediate transactions matrix;
- \(v\): 5 value-added categories;
- \(y\): 6 final-demand categories;
- \(Q\): environmental satellite account for CO2e.

### Step 3: calculate direct and total IO intensities

Total output:

\[
x=Ly
\]

with:

\[
L=(I-A)^{-1}
\]

and:

\[
A=T\hat{x}^{-1}.
\]

Direct carbon intensity:

\[
q=Q\hat{x}^{-1}.
\]

Total carbon intensity:

\[
m=qL.
\]

### Step 4: convert basic-price intensities to purchaser-price intensities

This is a critical methodological detail.

Health expenditure is in purchaser prices, while IO intensities are initially in basic prices.

Purchaser prices are decomposed into:

- basic price;
- wholesale margin;
- retail margin;
- hotel/restaurant margin;
- road freight;
- rail freight;
- pipeline transport;
- water transport;
- air transport;
- port handling;
- marine insurance;
- gas margin;
- electricity margin;
- four tax categories;
- subsidies.

The 18 valuation sheets sum to purchaser price.

For each health-related transaction, the shares of the valuation components are calculated.

The total purchaser-price carbon intensity is then a weighted combination of:

- the basic-price intensity of the relevant product/sector;
- the carbon intensities of the margin sectors.

Taxes and subsidies are monetary valuation items and are not assigned CO2e intensities.

### Step 5: build the bridge from 15 health categories to 360 IO sectors

Construct:

\[
C \in \{0,1\}^{15\times360}
\]

where a 1 indicates that an IO sector is relevant to an AIHW health category.

The binary concordance is converted to a normalised map matrix:

\[
M
\]

with each health-category row summing to one.

The normalisation uses the total output of the linked IO sectors.

### Step 6: calculate health-category intensities and emissions

Given:

\[
q \in \mathbb{R}^{1\times360}
\]

\[
m_{pp} \in \mathbb{R}^{1\times360}
\]

and:

\[
M\in\mathbb{R}^{15\times360},
\]

the health-category direct intensity vector is:

\[
q_H=Mq^{\prime}
\]

and the health-category total purchaser-price intensity vector is:

\[
m_H=Mm_{pp}^{\prime}.
\]

Each intensity is multiplied by its corresponding AIHW expenditure.

---

## 3. Worked public-hospital example

Public-hospital expenditure:

\[
48{,}094 \text{ million AUD}
\]

The concordance links public hospitals to:

- hospital services except psychiatric hospitals;
- psychiatric hospitals;
- pathology and diagnostic imaging;
- physiotherapy.

After mapping and purchaser-price conversion:

Direct intensity:

\[
0.012846 \text{ kt CO}_2\text{e per million AUD}
\]

approximately reported as:

\[
0.013
\]

Total intensity:

\[
0.256 \text{ kt CO}_2\text{e per million AUD}
\]

Direct emissions:

\[
0.012846
\times
48{,}094
=
617.8 \text{ kt CO}_2\text{e}
\]

reported as 618 kt.

Total emissions:

\[
0.256
\times
48{,}094
\approx
12{,}295 \text{ kt CO}_2\text{e}.
\]

This example makes the expenditure-intensity logic explicit.

---

## 4. Uncertainty model

The authors explain that the footprint function contains a matrix inverse, making simple analytical propagation difficult.

They therefore use Monte Carlo simulation.

The unperturbed footprint equation is represented as:

\[
F
=
Q\hat{x}^{-1}
\left(
I-T\hat{x}^{-1}
\right)^{-1}
y.
\]

Input variables \(Q\) and \(T\) are perturbed.

The perturbation is performed in logarithmic space to prevent negative physical or monetary values.

For a generic variable \(x\), the standard deviation in log space is approximated as:

\[
\sigma_{\log_{10}x}
\approx
\log_{10}(x+\sigma_x)
-
\log_{10}(x)
=
\log_{10}
\left(
\frac{x+\sigma_x}{x}
\right).
\]

The paper uses:

\[
P=10^6
\]

Monte Carlo realisations.

A normal distribution is fitted to the resulting footprint outcomes and its standard deviation is used for the reported uncertainty.

### Important interpretation

This is parametric uncertainty propagation through the IO model.

It does not automatically quantify uncertainty from all structural modelling choices.

---

## 5. Table C1

Table C1 reproduces direct and total intensities and emissions for all 15 categories.

The appendix reports:

\[
\text{Total direct emissions}
=
4{,}809 \pm 1{,}395 \text{ kt CO}_2\text{e}
\]

and:

\[
\text{Total emissions}
=
35{,}772 \pm 10{,}374 \text{ kt CO}_2\text{e}.
\]

---

## 6. Table C2 and linearity

Table C2 deliberately holds the total CO2e intensity constant and applies it to 2013, 2014 and 2015 expenditures.

The resulting footprints rise from:

\[
33{,}796 \text{ kt}
\]

to:

\[
34{,}840 \text{ kt}
\]

to:

\[
35{,}772 \text{ kt}.
\]

The authors use this only to illustrate linearity.

They explicitly warn that real carbon intensities are not constant through time.

Therefore Table C2 is not a historical emissions time series.

---

## 7. What the appendix does not report

### Code

`NOT REPORTED`

No reproducible analysis repository or source-code archive is provided in the supplied appendix.

### Programming language

`NOT REPORTED`

The authors identify Australian IELab as the cloud-computing platform but do not specify that the analysis was executed in Python, R, MATLAB or another user-facing language.

### Exact balancing algorithm for the 2018 table

`NOT REPORTED IN THIS APPENDIX`

The appendix explains data feeds into IELab but does not explicitly say that this particular 2018 custom table was balanced with KRAS.

KRAS is explicitly mentioned in the 2021 paper.

### Full concordance matrix

`NOT PROVIDED IN THE SUPPLIED 2018 APPENDIX`

The principles and a public-hospital example are given, but the full 15 x 360 matrix is not printed.

---

## 8. Plain-language explanation

The appendix solves three classification problems.

First, it converts industries into environmental intensities.

Second, it converts those intensities from factory-gate prices to the prices actually paid by healthcare purchasers.

Third, it converts economic-sector classifications into healthcare-expenditure classifications.

Only after all three conversions does it multiply expenditure by intensity.

That is why simply taking a single "health" sector from an IO table would not replicate Malik et al. (2018).

---

## 9. What to remember

1. The appendix is essential for replication.
2. \(A=T\hat{x}^{-1}\).
3. \(L=(I-A)^{-1}\).
4. \(q=Q\hat{x}^{-1}\).
5. \(m=qL\).
6. Purchaser-price conversion uses 12 margin categories plus taxes/subsidies.
7. The health bridge is 15 x 360.
8. Mapping is output-weighted, not a simple unweighted average.
9. Healthcare emissions equal mapped intensity times healthcare expenditure.
10. Uncertainty uses \(10^6\) Monte Carlo realisations with logarithmic perturbations.

---

## 10. Understanding check

| Concept | Definition | Why it matters | Question | Likely misunderstanding |
|---|---|---|---|---|
| Basic price | Producer/factory-gate valuation | IO intensities start here | Why can it differ from health expenditure valuation? | Equating basic and purchaser prices |
| Margin | Distribution service embedded in purchaser price | Margins themselves cause emissions | Why does road freight appear in purchaser-price conversion? | Treating margins as taxes |
| Map matrix | Normalised bridge from health categories to IO sectors | Produces one health intensity from several IO sectors | Why must rows sum to one? | Thinking binary concordance is the final weighting |
| Output weighting | Sector output used to allocate shares | Determines mapped intensity | What happens if one linked sector is much larger than another? | Assuming equal weights |
| Monte Carlo perturbation | Repeated random variation of input data | Propagates parametric uncertainty | Why use many simulations? | Thinking it proves the true value is normally distributed |
| Log perturbation | Randomisation in log space | Prevents negative values | Why not add unrestricted normal error directly? | Ignoring non-negativity |
| Linearity | Fixed intensity times expenditure | Fundamental IO assumption | What must change for expenditure to rise while emissions fall? | Treating intensity as immutable |

### Section to re-read

Re-read **B3 through B6** and the **worked public-hospital example in Section C**.

---

# Cross-paper synthesis

## 1. Methodological evolution

| Dimension | Malik et al. (2018) | 2018 supplementary appendix | Malik et al. (2021) |
|---|---|---|---|
| Geography | Australia | Australia | NSW within 8-region Australia |
| Reference year | 2014-15 | 2014-15 | 2017 |
| Health resolution | 15 AIHW expenditure categories | Same | 16 health sectors |
| Economic resolution | 360 sectors | 360 sectors | 360 sectors x 8 regions |
| Main method | National EIO-LCA | Detailed implementation | Sub-national MRIO hybrid |
| Environmental indicators | GHG only | GHG only | GHG, water, waste |
| Capital expenditure | Included | Included | Investments excluded |
| Production layers | Not central | Not central | Explicit \(I+A+A^2+\cdots\) decomposition |
| Regional trade | No sub-national attribution | No | Yes, modelled |
| International supply-chain coverage | Not fully transparent | Not fully transparent | Imports explicitly excluded |
| Uncertainty | Monte Carlo 68% intervals | Full method, \(10^6\) runs | No headline probabilistic interval reported |
| Main policy insight | Hospitals and pharmaceuticals dominate | How to reproduce the calculation | Most GHG and water impacts lie upstream |

---

# Why the studies differ

The 2021 NSW number should not be interpreted as simply a smaller version of the 2018 national number.

The studies differ in:

- year;
- geography;
- health-sector classification;
- environmental extensions;
- treatment of investment;
- regional structure;
- supply-chain attribution.

The 2021 result is about 7.9 Mt CO2e and the 2018 national result about 35.8 Mt CO2e, but a direct ratio is not a rigorous estimate of NSW's "share" of the national footprint because the system boundaries and reference years differ.

---

# Central methodological lessons for replication

## Lesson 1: sector definition is as important as the Leontief equation

The mathematics of:

\[
L=(I-A)^{-1}
\]

is standard.

The difficult part is defining healthcare demand correctly and mapping expenditure without double counting.

## Lesson 2: valuation matters

If health expenditure is in purchaser prices but IO intensities are in basic prices, multiplying them directly creates a valuation mismatch.

The 2018 purchaser-price conversion is therefore not a cosmetic detail.

## Lesson 3: disaggregation creates information but also assumptions

Moving from one aggregated "health and social work" sector to 15 or 16 health categories improves policy relevance.

However, every disaggregation requires mapping rules and weights.

These rules need their own sensitivity analysis.

## Lesson 4: national IO is not necessarily a global footprint

A national IO model can capture domestic supply-chain rounds but may not trace the technologies and environmental intensities of overseas producers unless it is linked to an MRIO or imports are explicitly modelled.

This is especially important for pharmaceuticals and medical equipment.

## Lesson 5: direct operational emissions are not the same as the total healthcare footprint

Both studies show that supply chains dominate GHG emissions.

A decarbonisation strategy focused only on hospital buildings misses much of the problem.

---

# Replication blueprint

## A. Replicating the 2018 national method

### Inputs

You need:

1. national symmetric IO table or SUT converted to an IO framework;
2. environmental extension \(Q\);
3. healthcare expenditure categories;
4. valuation/margin data;
5. concordance from healthcare categories to IO sectors.

### Workflow

\[
x=T\mathbf{1}+y\mathbf{1}
\]

\[
A=T\hat{x}^{-1}
\]

\[
L=(I-A)^{-1}
\]

\[
q=Q\hat{x}^{-1}
\]

\[
m=qL
\]

Convert \(m\) from basic to purchaser prices.

Construct:

\[
C_{H\times N}
\rightarrow
M_{H\times N}
\]

Then:

\[
m_H=Mm_{pp}^{\prime}
\]

and:

\[
F_H=m_H\odot e_H
\]

where \(e_H\) is the vector of healthcare expenditure.

### Replication-critical items missing from the supplied study

- complete 15 x 360 concordance;
- executable code;
- exact IELab build configuration;
- complete uncertainty input standard deviations.

A conceptual replication is possible from the paper and SI.

A byte-for-byte numerical replication is not possible from the supplied documents alone.

---

## B. Replicating the 2021 NSW method

In addition to the national workflow:

1. regionalise the IO system;
2. estimate inter-regional trade;
3. reconcile the regional tables;
4. retain health-sector detail;
5. attach regional environmental extensions;
6. construct the NSW health final-demand vector;
7. compute PLD:

\[
F
=
q
\left(
I+A+A^2+\cdots
\right)
y_H;
\]

8. aggregate the 360 sectors to interpretable hotspot groups;
9. attribute impacts by origin region.

### Replication-critical missing items

The article references supplementary:

- Table A1;
- Table A2;
- Table A3;
- Table A4;
- Figures A1-A3.

Those materials are not in the supplied corpus.

Therefore exact replication of the sector concordance, detailed sector results and some supporting model configuration remains incomplete until the 2021 supplementary material is obtained.

---

# Evidence index

| Claim or concept | Source anchor | Evidence type | Confidence |
|---|---|---|---|
| 2021 NSW totals: 7,908 kt CO2e, 246 GL water, 1,624 kt waste | Malik 2021, Results 3.1, p. 4 and Conclusion pp. 10-11 | Quantitative result | High |
| 6.6%, 4%, 8% shares | Malik 2021, abstract and Discussion 4.1 | Quantitative comparison | High, with denominator-boundary caveat |
| 8 states, 360 sectors | Malik 2021, Methods 2.1 | Model design | High |
| 16 health sectors | Malik 2021, Methods 2.2 | Scope/classification | High |
| KRAS reconciliation | Malik 2021, Limitations 2.3.1 | Method | High |
| Imports and investments excluded | Malik 2021, Limitations 2.3.1 | Boundary limitation | High |
| First-layer GHG 11%, water 17%, waste 62% | Malik 2021, Discussion 4.2.2 | Decomposition result | High |
| First three layers GHG 67%, water 72%, waste 90% | Malik 2021, Discussion 4.2.2 | Decomposition result | High |
| 2018 national footprint 35,772 kt CO2e | Malik 2018, Summary/Results | Quantitative result | High |
| 2018 share 7.2% | Malik 2018, Results | Quantitative result | High |
| Hospitals + pharmaceuticals dominate | Malik 2018, Results/Discussion | Hotspot result | High |
| Direct emissions 4,809 kt | Malik 2018, Table 3 | Quantitative result | High |
| \(m=qL\) | 2018 SI, B3 | Equation | High |
| 15 x 360 bridge matrix | 2018 SI, B4 | Mapping method | High |
| Purchaser-price conversion | 2018 SI, B3 | Valuation method | High |
| \(10^6\) Monte Carlo simulations | 2018 SI, B6 | Uncertainty method | High |
| Abstract/SI uncertainty differs from main Table 3 total row | Malik 2018 main + SI | Internal consistency check | High |
| Full executable code is provided | All three supplied sources | NOT REPORTED | High confidence that it is absent from supplied documents |

---

# Final synthesis

The three sources form a clear methodological progression.

The 2018 study establishes the national Australian healthcare carbon footprint using expenditure-linked environmentally extended IO analysis.

The 2018 supplementary appendix shows how that result is actually constructed, including the Leontief system, purchaser-price conversion, 15 x 360 bridge matrix and Monte Carlo uncertainty.

The 2021 study takes the same research programme to a sub-national level, adds water and waste, resolves 16 health sectors, distinguishes eight Australian regions and opens the Leontief inverse into production layers.

The shared scientific message is robust:

> The environmental footprint of healthcare is not mainly confined to hospitals. A large part, especially for climate change and water use, arises in the economic supply chains required to deliver healthcare.

The strongest methodological warning is equally important:

> A footprint estimate is only as defensible as its healthcare boundary, sector concordance, valuation convention, regionalisation and environmental extensions. The Leontief inverse is not the difficult part. Building the demand vector and the bridge to the economic system is.

