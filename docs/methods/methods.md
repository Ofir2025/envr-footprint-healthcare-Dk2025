# Methods

The methodology behind this study: the named methodological layers that
implement each published method (and how to trace any number back through
them), which external models and datasets are actually used and why not the
others, the EXIOBASE coupling this revision's pipeline runs (simplified SNAC,
the import bridge, and full footprint accounting), and the feasibility
assessment for the fuller Danish national-accounts coupling that would
replace this revision's one-row patch. The per-replication-layer write-ups
(one document per gold-output folder) and the Danish data-acquisition record
are kept as their own documents:
[docs/methods/replications.md](replications.md) and
[docs/methods/danish_data_acquisition.md](danish_data_acquisition.md).

## Contents

1. [Methodological approaches implemented, and how to trace any number](#methodological-approaches-implemented-and-how-to-trace-any-number)
2. [Which external models and datasets we actually use, and why](#which-external-models-and-datasets-we-actually-use-and-why)
3. [Simplified SNAC, EXIOBASE coupling and Danish healthcare footprint accounting](#simplified-snac-exiobase-coupling-and-danish-healthcare-footprint-accounting)
4. [Danish SNAC: what Statistics Denmark does, what we patch, and the feasibility of a full build](#danish-snac-what-statistics-denmark-does-what-we-patch-and-the-feasibility-of-a-full-build)

---

## Methodological approaches implemented, and how to trace any number

This study is not a single model. It is a **core EE-MRIO footprint** plus a set
of **named methodological layers**, each implementing a specific published
method, each writing to its own folder under `data/gold/results/`, and each
traceable through `data/gold/results/manifest_lineage.csv` (one row per file:
approach, script, equations, reference, inputs, checksum).

```
data/gold/results/
├── manifest_lineage.csv          every gold file: approach, script, equations, inputs
├── 00_core_footprint/            the detailed footprint arrays (lineage base)
├── 01_eriksen_replication/       the Steenmeijer-style outputs (tables 1, S5)
├── 02_scopes_wood_hertwich/      GHG-Protocol scopes + the double-counting ledger
├── 03_cabernard_target_scope3/   target-perspective scope 3, corrected
├── 04_uncertainty_lenzen_ieooc/  Monte Carlo, variance shares
├── 05_waste_dst_accounts/        waste from Denmark's own SEEA accounts
├── 06_benchmarks_validation/     benchmarks, denominators, recipe validation
└── scenarios/                    scope-boundary variants
```

The full method write-up for every layer above — the source equations, data
requirements, deviations from the source, and verification — is in
[docs/methods/replications.md](replications.md), one section per layer. What
follows here is the short version: what each layer is for, in one or two
paragraphs, with the reference and the equation that defines it.

### 00 - Core EE-MRIO final-demand footprint

**Reference:** Steenmeijer et al. (2022); Miller & Blair (2009).
**Equations:** $f = \mathbf{C}\,\mathbf{S}\,\mathbf{L}\,y_H$, decomposed cell-wise as $E_{ij} = s_i\,L_{ij}\,y_j$
- pressure arising in node *i* caused by Danish healthcare demand for node *j*.
Summing over *i* gives the consumption perspective, over *j* the production
perspective; both are marginals of one array, verified equal to machine
precision (`analysis.validate_io_identities`, tests T5/T6).

**Why it does not double count:** allocating production emissions to final
demand is additive and sums to the total; the embodied-flow table $\mathbf{E}_Z$ is the
construct that double counts, and we never sum it (Wood & Hertwich 2018, p. 5).

### 01 - Eriksen/Steenmeijer replication (corrected)

The original study's outputs, with the audit corrections: complete eldercare
coverage, DRIVHUS direct emissions, AFFALD direct waste, Danish bottom-up
medical gases, year-consistent currency, exact-match transport grouping.
Every correction is listed in
[docs/revision/defects_and_fixes.md](../revision/defects_and_fixes.md) with
its effect on the result.

### 02 - GHG-Protocol scopes (Wood & Hertwich)

**Reference:** Wood & Hertwich (2018), table 1 and eqs. 1-2; GHG Protocol.
- **Scope 1** from national accounts. The services demand vector is
  $y = \mathbf{A}(:,h)\,E_H$, and we verified the identity $F_{\text{services}} = (m_h - s_h)\,E_H$, i.e.
  the construction yields a *pure upstream* quantity - the exact complement to
  a national-accounts Scope 1. (Using the true final-demand column instead
  would double count Scope 1 outright.)
- **Scope 2** = $d_E \cdot \mathbf{L}_{EE} \cdot y_E$ with $\mathbf{L}_{EE} = (\mathbf{I}_{EE} - \mathbf{A}_{EE})^{-1}$ over the
  energy block, so generation is reached through transmission and distribution
  without leaving that block; fuel extraction and refining stay in Scope 3.
- **Scope 3** = the footprint residual after Scope 2, plus the bottom-up items
  the MRIO structurally cannot contain.
- **Asserted:** $S_1 + S_2 + S_3 + \text{outside} = \text{total}$, and the
  producing-node detail reconciles.

The **double-counting ledger** (`double_counting_ledger.csv`) tests each overlap
risk numerically, including the intra-sector self-supply term (1.83 kt CO₂e,
removed) and the pharma-component-vs-procurement question (cleared: different
channels).

### 03 - Target-sector scope 3 (Cabernard)

**Reference:** Cabernard et al. (2019) eqs. 8/9/12; Cabernard et al. (2022) SI.

This answers a **different question** from 00: not "what does Danish healthcare
demand cause?" but "what is the scope 3 of the health sector-regions
themselves?" - and *that* question double counts unless corrected, because a
delivery from one target node to another is counted for the supplier and again
for the recipient. Corrected output replaces gross output with output net of
target-to-target deliveries:

$$q_T = \text{rowsum}\big(\mathbf{Y}_{T,\text{all}} + \mathbf{A}_{T-O}\,\mathbf{L}'_{O-O}\,\mathbf{Y}_{O,\text{all}}\big)$$
$$e_{T,\text{wdc}} = d\,\mathbf{L}(:,T)\,\mathrm{diag}(q_T)$$
$$f_T = (e_T - e_{T,\text{wdc}}) / e_T$$

**Measured for three nested target sets (Denmark 2022, climate):**

| target set | nodes | naive | corrected | double-counting factor |
|:---|:---|:---|:---|:---|
| T1 Danish health and social work | 1 | 0.9 Mt | 0.9 Mt | **1.3 %** |
| T2 health and social work, all regions | 49 | 1,129 Mt | 1,100 Mt | **2.6 %** |
| T3 T2 + chemicals + medical instruments | 147 | 3,093 Mt | 2,511 Mt | **18.8 %** (23 % overestimate) |

The complement identity $d\,\mathbf{L}\,\mathbf{Y}\,\mathbf{1} = e_{T,\text{wdc}} + d_O\,\mathbf{L}'_{O-O}\,\mathbf{Y}_O\,\mathbf{1}$ holds to $2\times10^{-16}$,
confirming the implementation. **Read this correctly:** the study's headline is a
final-demand footprint (00) and is *unaffected*. But any target-perspective or
sub-sector reporting - which is exactly what the planned health-subsector
disaggregation will produce - must use eq. 9, and at T3 the error is nearly a
fifth. This is the quantitative answer to "is one target enough?": for a single
Danish health node the correction is 1.3 %, but the moment pharmaceuticals and
device manufacturing join the target set it is 19 %.

### 04 - Uncertainty (Lenzen calibration, IEooc conventions)

**References:** Lenzen et al. (2020) SI 7 for the MRIO standard deviation;
IEooc Methods5 Exercise 4b for reporting conventions.
Median-1 lognormal multipliers so the MC median reproduces the deterministic
model; structural choices as discrete scenarios; MRIO parameter uncertainty as
one shared factor at the published Danish health-care relative SD of 8.35 %;
correlated travel items; exact first-order Sobol shares (free for an additive
independent model); verified against closed-form lognormal moments. Full
derivation, worked example, and every reported number:
[docs/revision/uncertainty.md](../revision/uncertainty.md).

### 05 - Waste from Denmark's own accounts

**Reference:** Statistics Denmark AFFALD01 / AFF1MU1N / AFF3MU1N.
The inherited hybrid-2011 extension was tested as absolute values, as a
coefficient, and as an allocation key, and fails all three (see
`waste_extension_validation.csv` and
[docs/revision/defects_and_fixes.md](../revision/defects_and_fixes.md)). The
domestic tier now uses Denmark's published IO waste multipliers; the imported
tier is reported separately and relabelled as upstream solid residuals.

### 06 - Benchmarks and validation

Recipe validation of EXIOBASE's Danish health input structure against the DST
117-industry health columns; three independent national denominators (own model
64.72 Mt, DST AFTRYK 62.93 Mt, Eurostat FIGARO 57.40 Mt); comparison with
Arup/HCWH, Pichler, Lenzen and the Dutch template.

### Lineage rule

Every gold table is exported at the **most detailed level available** and every
aggregate is a `groupby` of it - never the reverse. `manifest_lineage.csv` maps
each file to its approach, script, equations, references and inputs, so any
number in the manuscript can be traced to the code that made it and the method
it implements.

---

## Which external models and datasets we actually use, and why

This note was prompted by a fair challenge: an earlier memo mentioned OECD
**ICIO**. That was a stray reference in a scoping brief. **ICIO is not used
anywhere in this study.** The models actually used are below.

### In use

| dataset | role | why this one |
|:---|:---|:---|
| **EXIOBASE v3.10.2 IOT_2022_ixi** (Zenodo 20051562) | the model itself | 163 industries × 49 regions, the finest sectoral resolution of the harmonised global MRIOs, full GHG coverage, and the widest satellite set; the same family as the Dutch template. Native unit **M.EUR** |
| **Statistics Denmark IO tables** (117 industries, basic prices) | expenditure vector; recipe validation | public, national-accounts consistent, 2006-2022 |
| **Statistics Denmark DRIVHUS / AFFALD / AFTRYK / SHA1 / NABB69** | direct emissions, waste, national denominator, expenditure cross-check, employment | official, same DB07 classification as the IO tables, open API |
| **Eurostat FIGARO** (`env_ac_ghgfp`, supply/use 2022 & 2024) | independent benchmark and denominator | the official EU inter-country accounts; consistent, trustworthy SUT/IOT for Denmark, which is exactly why it is here |
| **EXIOBASE hybrid v3.3.18 (2011)** | legacy waste extension, now demoted | retained only as the "upstream solid residuals" tier with its composition disclosed |

**A note on the table above.** The Zenodo record named for the model itself is
the one the *classification* work drew on; the study's actual background
model, adopted after the release audit, is **EXIOBASE v3.8.2**, not v3.10.2.
That decision, and the evidence for it, is in
[docs/methods/replications.md, section 09](replications.md#r09) and
[docs/revision/defects_and_fixes.md, anomalies A1-A2](../revision/defects_and_fixes.md#a-defects-in-the-background-data-exiobase).

### Considered and rejected, with reasons

- **OECD ICIO**: 45 industries, coarser than both EXIOBASE and the Danish
  national tables, CO₂-focused. Statistics Denmark rejected it for the same
  reason when building their own coupled model. **Not used.**
- **Eora**: used by Lenzen et al. and Pichler et al.; we use their *published
  Danish results* as benchmarks and their published SD to calibrate MRIO
  uncertainty, but not the database itself.

### FIGARO: what it can and cannot do for us

Downloaded to `data/bronze/eurostat_figaro/`: the 2022 and 2024 use tables with Denmark
as destination, the DK supply table 2022-2024, and the official GHG/CO₂
footprint datasets 2021-2023.

**What it gives us now.** An independent national denominator: Denmark's
consumption-based GHG footprint 2022 = **57.40 Mt CO₂e**, against DST AFTRYK's
62.93 Mt and our model's 64.72 Mt, so the healthcare share is honestly
**7.5-8.5 %** depending on the denominator. It also puts emissions arising in
NACE Q due to Danish final demand at 176 kt (Q86 alone 97 kt), corroborating
our 142 kt Scope 1 plus the intra-health chain.

**What it can do for gap-filling.** At A64 it separates **Q86 human health**
from **Q87-Q88 residential/social work**, and carries **C21 pharmaceuticals**
separately, so it can (i) validate the EXIOBASE Danish health input recipe
against an official EU source, and (ii) supply an alternative import structure.
The full feasibility test plan for FIGARO is in
[docs/methods/danish_data_acquisition.md, section 6](danish_data_acquisition.md#6-figaro-feasibility-and-test-plan).

**What it cannot do.** 64 industries cannot substitute for the confidential
~2,350-product Danish SUT when the goal is health-sector disaggregation; it has
no medical-device or clinical-supply detail.

### US EEIO: the right tool for a specific job

It is worth adding for two purposes, neither of which the European sources cover:

1. **TRACI elementary flows.** USEEIO carries ~1,900 elementary flows mapped to
   TRACI characterisation, which is what an Eckelman & Sherman-style
   multi-pollutant and DALY analysis needs. Our EXIOBASE-based extended
   indicators give the *inventory* (PM2.5, NOx, SOx, NH₃, NMVOC, N and P to
   water) but no characterised midpoints or endpoints; USEEIO is the natural
   bridge if we want to add that layer.
2. **400+ sector resolution** as a donor prior for health-sector
   disaggregation, strictly for residual gaps where Danish data are silent,
   the discipline already stated in the research blueprint: Danish evidence
   first, USEEIO only as a transparent donor.

USEEIO is not yet implemented; it is listed as the next optional layer.

---

## Simplified SNAC, EXIOBASE coupling and Danish healthcare footprint accounting

### 1. Purpose

This section describes the second modelling layer:

$$
\text{augmented Danish EEIO}
\rightarrow
\text{import requirements}
\rightarrow
\text{EXIOBASE foreign multipliers}
\rightarrow
\text{total Danish healthcare footprint}.
$$

This should only be implemented after the domestic augmented model passes its
accounting and validation tests. `analysis.build_dst_concordance`, which runs
in the published pipeline, is specified against this section's import-bridge
part, and
[docs/methods/replications.md, section 10](replications.md#r10) (the Danish
sea-transport reallocation) points here for the full coupling that
reallocation approximates with a single-row patch.

### 2. Stage 15: construct a health-consumption demand matrix

The IO model and the System of Health Accounts (SHA) should be linked without
confusing their accounting concepts.

Let $y^{NA}_{\text{health}}$ be the health-related national-account final
demand. Use SHA-derived allocation shares $r_{kc}$, where $k$ is a health
product/provider/industry bridge category and $c$ is a healthcare function or
provider reporting category. Then

$$y^{\text{health}}_{kc} = r_{kc}\,y^{NA}_{k}$$

subject to

$$\boxed{\sum_c y^{\text{health}}_{kc} = y^{NA}_{k}}$$

for each relevant national-account category. The principle is: SHA determines
how health expenditure is subdivided, while national accounts determine the
monetary totals entering the IO system.

### 3. Separate provider footprints from health-system expenditure footprints

Two different analytical boundaries should be reported.

**3.1 Provider/industry footprint.** Examples: hospitals; general
practitioners; dentists; specialist practices; home nursing. This is driven by
IO industries.

**3.2 Health-system expenditure footprint.** Includes goods and services
purchased to fulfil health functions, potentially including pharmaceuticals,
medical goods, health services, patient transport, and other health-related
consumption. This boundary can be organised using SHA functions/providers.

The two totals need not be identical.

### 4. Pharmaceuticals and medical goods

Pharmaceutical manufacturing should not simply be reclassified as a
health-service industry. The IO model should preserve the actual economic
activity classification. Thus pharmaceuticals can appear as: (1) upstream
inputs into hospitals or other providers; (2) final household/government
purchases; (3) part of the health-expenditure footprint under SHA reporting.
This distinction prevents a classification error whereby an upstream
manufacturing industry is treated as though it were itself a health-service
provider.

### 5. Stage 16: capital treatment

Healthcare is capital intensive. Important capital categories include hospital
buildings, diagnostic equipment, medical technology, ICT infrastructure,
vehicles, and other machinery. Ordinary IO tables generally treat gross fixed
capital formation as final demand. The project should therefore report two
variants.

**5.1 Operational footprint.** Capital remains in $y_{\text{GFCF}}$.

**5.2 Capital-inclusive health-system footprint.** Health-related capital
requirements are allocated to health activities through an explicit
capital-use layer or capital endogenisation. Do not simultaneously (1)
endogenise a capital flow in $\mathbf{A}$, and (2) retain the same capital
flow as additional health final demand — that would double count. Capital
treatment should initially be a sensitivity analysis rather than an invisible
baseline assumption. (The revision's own capital sensitivity, run against
this discipline, is in
[docs/revision/results_2022.md, "Capital (GFCF) treatment"](../revision/results_2022.md#capital-gfcf-treatment).)

### 6. Stage 17: why simplified SNAC is appropriate

There are three broad choices.

**Option A. Use EXIOBASE directly.** Advantage: simple, globally balanced.
Disadvantage: Danish national-account blocks in EXIOBASE need not exactly
reproduce Statistics Denmark.

**Option B. Full SNAC-GMRIO.** Replace the Danish block in the MRIO with
official Danish data and rebalance the entire global system. Advantage:
national consistency plus global feedback. Disadvantage: technically
demanding; produces a modified MRIO; requires global rebalancing.

**Option C. Simplified SNAC.** Keep the official Danish domestic model intact
and use the GMRIO to calculate environmental pressures embodied in imports.
Advantage: exact Danish domestic accounting; substantially easier to
implement; no need to reconstruct the full MRIO. This is the architecture
implemented in the Palm/Statistics Denmark family of work (see
[section 4](#danish-snac-what-statistics-denmark-does-what-we-patch-and-the-feasibility-of-a-full-build)
below for their published equations and results). For a small open economy
such as Denmark, simplified SNAC is an attractive research design when the
primary question concerns Denmark.

### 7. Domestic coefficients

Split the Danish use structure into $\mathbf{A}^d$ for domestic intermediate
inputs and $\mathbf{A}^m$ for imported intermediate inputs. Then
$\mathbf{L}^d = (\mathbf{I}-\mathbf{A}^d)^{-1}$. For domestic final demand
$y^d$, the imported intermediate requirements induced by domestic production
are

$$\boxed{m^I = \mathbf{A}^m\,\mathbf{L}^d\,y^d}$$

Direct imported final demand is $\boxed{m^F = y^m}$. Hence total import demand
induced by Danish final demand is

$$\boxed{m = \mathbf{A}^m\,\mathbf{L}^d\,y^d + y^m}$$

### 8. EXIOBASE foreign multipliers

For EXIOBASE define $\mathbf{A}^E = \mathbf{Z}^E\,\widehat{x^E}^{-1}$. Then
$\mathbf{L}^E = (\mathbf{I}-\mathbf{A}^E)^{-1}$. Let $\mathbf{F}^E$ be
environmental extensions and $\mathbf{S}^E = \mathbf{F}^E\,\widehat{x^E}^{-1}$.
The global foreign supply-chain multiplier is

$$\boxed{\mathbf{Q}^E = \mathbf{S}^E\,\mathbf{L}^E}$$

This matrix gives environmental pressure per monetary unit of EXIOBASE final
demand by region-sector node.

### 9. Stage 18: Danish import-to-EXIOBASE bridge

A concordance is needed between detailed Danish imports and EXIOBASE
region-sector nodes. The bridge should combine (1) product mapping; (2)
country-of-origin mapping; (3) currency conversion; (4) reference-year price
harmonisation where needed. Conceptually,

$$\mathbf{K} = \mathbf{K}_{\text{sector}}\,\mathbf{K}_{\text{country}}$$

The matrix should be sparse. For every Danish import category $j$,

$$\boxed{\sum_r K_{rj} = 1}$$

unless a documented amount is intentionally left unallocated.

### 10. Detailed goods trade

For imported goods, use detailed Danish bilateral trade information wherever
possible. For product $p$ and origin country $c$,

$$b_{pc} = \frac{M_{pc}}{\sum_c M_{pc}}$$

These bilateral shares are used to assign imported products to EXIOBASE
producing regions. This is preferable to the domestic technology assumption
because foreign production structures and emission intensities differ from
Denmark.

### 11. Imported services

Goods customs data are not sufficient for services. Use service-trade /
balance-of-payments information to estimate country-of-origin shares for
imported services. Services should be mapped carefully because healthcare
supply chains contain substantial inputs from ICT, professional services,
finance, real estate, transport, and other business services. If bilateral
detail is incomplete, use documented hierarchical allocation rules and
propagate uncertainty.

### 12. Currency conversion

Keep currency conversion explicit. For example,

$$m^{EUR} = c_{DKK\rightarrow EUR}\,\mathbf{K}\,m^{DKK}$$

Avoid hiding currency factors inside a concordance matrix unless that design is
very clearly documented. If Danish and EXIOBASE data refer to different price
years, introduce a separate deflation/reflation layer rather than treating
nominal values as directly comparable.

### 13. Stage 19: current EXIOBASE quality control

Do not simply reproduce historical outlier thresholds used in older
implementations. The current EXIOBASE release should be evaluated afresh. For
environmental intensity $S_{ejr}$, where $e$ is the environmental extension,
$j$ the sector, and $r$ the region, a robust regional outlier diagnostic can be

$$z^{MAD}_{ejr} = \frac{S_{ejr} - \operatorname{median}_r(S_{ejr})}{1.4826\,MAD_r(S_{ejr})}$$

Flagged intensities should trigger: (1) inspection of direct extensions; (2)
inspection of sector output denominators; (3) review of EXIOBASE
documentation/known issues; (4) comparison with neighbouring or structurally
similar countries; (5) sensitivity analysis. Do not automatically winsorise or
delete extreme values — some extreme environmental intensities are genuine.

### 14. Stage 20: total coupled footprint

The final Danish footprint can be expressed as

$$\boxed{f^{DK} = \mathbf{S}^d\,\mathbf{L}^d\,y^d + \mathbf{Q}^t\,\mathbf{A}^m\,\mathbf{L}^d\,y^d + \mathbf{Q}^t\,y^m + f^h}$$

where $\mathbf{Q}^t$ is the EXIOBASE multiplier transformed into the Danish
import classification. The four terms represent: (1) domestic Danish supply
chains; (2) foreign inputs embodied in Danish domestic production; (3) direct
imported final-use products; (4) direct household environmental pressures.

### 15. Decomposition by health sector

For each health child $k$, calculate $f_k$. Examples: hospitals; GPs;
specialists; dentists; physiotherapists; home nursing; other health
activities. Results should be decomposable into domestic + foreign. Foreign
results should further be decomposable by producing region, producing
industry, imported product, and upstream supply-chain layer.

### 16. Decomposition by healthcare function

Using the SHA-final-demand bridge, calculate functional footprints for
categories such as inpatient care, outpatient care, preventive care,
ancillary services, medical goods, and long-term health care where within
scope. This is distinct from the provider footprint.

### 17. Structural-path analysis

Once the model is validated, structural path analysis can identify high-impact
chains, for example: Hospital → pharmaceuticals → chemical manufacturing →
electricity generation → GHG emissions; or Dentist → medical equipment →
fabricated metals → primary metals → mining. This can identify high-value
data-collection targets. If a major footprint is driven by a donor-estimated
coefficient, that coefficient becomes a priority for Danish primary data
collection.

### 18. Avoid double counting in the international coupling

The simplified-SNAC architecture must separate domestic production, imported
intermediate inputs, and imported final use. Do not apply the full EXIOBASE
multiplier to Danish domestic production and then add domestic Danish
emissions again. Likewise, if capital is endogenised into the technical
matrix, do not also add the same capital final demand as an additional
health-system burden. A transparent accounting map should specify exactly
which layer accounts for each flow.

### 19. Baseline result set

The first publication-grade footprint model should report, under
**Economic**: gross output, intermediate consumption, value added, and import
dependence. Under **Environmental**, initially GHG emissions, then where
robust: energy, water, materials, land, and selected air pollutants. Under
**Spatial**: Denmark, EU, other Europe, China, other Asia, North America, and
other world regions. Under **Supply-chain**: direct health-provider impacts,
domestic upstream, imported direct, and imported upstream.

### 20. Why this architecture is preferable

This approach preserves the strongest information at each analytical scale:

$$\boxed{\text{Statistics Denmark} \rightarrow \text{domestic technology and national margins}}$$
$$\boxed{\text{SHA/admin data} \rightarrow \text{health-specific allocation}}$$
$$\boxed{\text{USEEIO} \rightarrow \text{residual technological priors}}$$
$$\boxed{\text{EXIOBASE} \rightarrow \text{foreign supply-chain completion}}$$

It avoids the two weakest alternatives: (1) treating EXIOBASE's Danish block as
more authoritative than Statistics Denmark; (2) treating US healthcare
production structures as though they were Danish observations.

---

## Danish SNAC: what Statistics Denmark does, what we patch, and the feasibility of a full build

**Question (Albert, 2026-09):** can we do for Denmark what Palm et al. (2019, J
Clean Prod 228:634-644) did for Sweden (keep the national table as the
authoritative domestic core and use EXIOBASE only for imports), and thereby
exploit the Danish IOT's much finer health-sector resolution? Short answer:
**yes, and Denmark is an unusually good candidate**; the medium answer is that
it is a paper-sized build, best executed for the 2022 analysis rather than
squeezed into the current revision.

This section has two halves. Subsections 1-5 are the current position: what
Statistics Denmark's own coupled model found, the single reallocation this
study applies as a lightweight patch, and the open nowcast-year decision.
Subsections 6-11 are the feasibility memo for the full Danish-SNAC build that
would replace the patch; nothing in it has been built yet, and two of its
figures have since been superseded by the corrected model, flagged where they
occur.

### 1. The defects Statistics Denmark documents, with their numbers

Source of truth: Rørmose Jensen & Iliev (2022), *Consumption-based GHG account
for Denmark using coupled models*, Statistics Denmark / Eurostat grant
101022790, WP4; Palm et al. (2019) *J Clean Prod* 228:634-644; Tukker, Giljum &
Wood (2018) *J Ind Ecol* 22:483-498.

Their table 1 compares EXIOBASE v3.8 with the Danish national-accounts IOT for
**water transport**, 2019, million DKK:

| | EXIOBASE | Danish national accounts |
|:---|:---|:---|
| Output | 137,637 | 246,064 |
| To Danish intermediate use | **74 %** | **9 %** |
| To exports | 14 % | 90 % |
| Imported inputs | 41 % | 93 % |
| Gross value added | **−1,880 (−1.3 %)** | **+33,339 (+14 %)** |

A negative value added is not an economy; it is a broken block. That industry is
more than half of Danish CO₂, so raw EXIOBASE routes the bulk of Danish shipping
emissions into Danish *consumption*.

Three further defects: **Danish imports in EXIOBASE are 30-40 % below the
national accounts**; the satellite vector contains extreme outliers (Mexican
secondary plastic at 372,548 t CO₂e per EUR turns a 2 M EUR import into 729 Gt);
and the nowcast years are internally out of sync, so inflation mechanically
inflates the footprint. The version-and-release defects this study found on its
own model, independently of Statistics Denmark's, are documented in full in
[`exiobase_release_and_classification.md`](exiobase_release_and_classification.md).

### 2. Their remedy is structural, ours is a patch

They adopt **simplified SNAC**: the Danish domestic block comes entirely from
the national accounts, and EXIOBASE is never used for it:
$\mathbf{A}_d = \mathbf{Z}\,\hat{x}^{-1}$, $\mathbf{L}_d = (\mathbf{I} - \mathbf{A}_d)^{-1}$,
$e_d = \hat{s}_d\,\mathbf{L}_d\,y_d + e_h$. EXIOBASE enters only for imports,
through $\mathbf{Q} = \hat{s}\,\mathbf{L}$ and $e_m = \mathbf{Q}\,\mathbf{K}\,m$,
with $m = \mathbf{A}_m\,\mathbf{L}_d\,y_d + y_m$ and $\mathbf{K}$ a
7,987 × 117 concordance. This is the same simplified-SNAC formalism as
[section 3, stage 17](#simplified-snac-exiobase-coupling-and-danish-healthcare-footprint-accounting)
above; Palm's own version of the equations, in her notation, is given in
subsection 6 below.

**Their model carries no shipping correction, because the wrong block is
discarded rather than repaired.**

Ours is a targeted reallocation of one row to their published 9 % benchmark. It
recovers most of the effect for a fraction of the work, and it is honest to call
it what it is: an approximation of the first step of a method we have not yet
implemented. Simplification is defensible: Moran et al. (2018) put the Danish
feedback effect at **0.4 %**, which is why simplified SNAC is used in preference
to full SNAC by both Rørmose and Palm. The full mechanics and the effect on the
headline are in
[docs/revision/results_2022.md, "The withdrawn transport finding"](../revision/results_2022.md#the-withdrawn-transport-finding).

Their own outlier remedy is a hard multiplier threshold of 1 kg CO₂e/DKK
(≈7.5 kg CO₂e/EUR) which they themselves call *"quite arbitrary"*; their
preferred future fix is iterative replacement of outliers by the cross-country
mean of the remaining 48 regions.

### 3. The nowcast-year disagreement (Decision D8, open)

**Statistics Denmark does not use the nowcast years.** They freeze EXIOBASE at
**2019** (the last year backed by real emission data) for their 2019, 2020, and
2021 footprints, and deflate the demand vector back to 2019 prices.

We do the opposite: 2022 expenditure on the 2022 table, whose CO₂ accounts end
in 2019 and whose other greenhouse-gas accounts end in 2017.

Both positions are arguable. Ours has the merit that the Danish **economic**
block is validated against the 2022 national accounts and passes, and that
expenditure year and model year coincide, which is what reviewer 2 asked for.
Theirs has the merit that the **emission** side is never extrapolated.

This choice is an open decision, tracked in full as
[Decision D8 in docs/revision/results_2022.md](../revision/results_2022.md#decision-d8-2022-nowcast-or-the-last-observed-year),
not a settled one. That document's recommendation is to keep 2022 as the
headline and add the 2019-frozen, deflated variant as a reported sensitivity,
which would also answer reviewer 2's original concern from the opposite
direction.

### 4. Results worth citing against ours

| | Rørmose (2020) | This study (2022) |
|:---|:---|:---|
| Danish national footprint | 65.4 Mt CO₂e | 77.2 Mt |
| Per capita | 11.0 t | 13.2 t |
| Share arising in Denmark | 38 % | n/a |
| Share arising abroad | **62 %** | n/a |
| Government consumption footprint | ~8 Mt, of which **~2/3 abroad** | n/a |

Their government-consumption finding matters directly: **Danish government
consumption, where public health care sits, is about two-thirds
imported-emissions in their coupled model**, materially more import-exposed than
households at 55 %. Our health-care footprint is **73.7 % imported** in origin,
which is consistent with, and slightly above, their government figure.

They publish **no like-for-like raw-versus-coupled comparison**, so the size of
the SNAC correction for Denmark cannot be cited from them; it would have to be
computed, which is the point of the feasibility work in subsections 6-11.

### 5. Method points that bear on our claims

- **Uncertainty priority is the reverse of the intuitive order.** Tukker et al.
  (2018): *"the environmental extensions, rather than the redistribution to
  final consumption via economic structure reflected by a specific GMRIO, forms
  the highest source of uncertainty… The next most important issue appears the
  differences in representation of the country SUT/IOT in GMRIOs, rather than
  the structure of the trade flows."* Variance mass belongs on the satellite
  first, then the domestic block, then trade.
- **Scope 2+3 is not an additive account.** Hertwich & Wood (2018) are explicit
  that scope accounting measures reduction opportunities and that the total does
  not sum to global emissions, and that **the amount of double counting depends
  on sector resolution**. Our scope partition is exact within our own boundary,
  which is a different and weaker claim, and the manuscript should say so.
- **A GHG-only footprint misses most of the variance.** Steinmann et al. (2017),
  via Tukker et al.: carbon, energy, land, water, and materials together explain
  only **~60 %** of environmental variance; adding five impact-oriented
  indicators reaches **95 %**, with toxicity the systematic omission. This result
  is the published justification for carrying IMPACT World+ alongside the five
  headline indicators.
- **Capital stays exogenous in both precedents.** Neither Rørmose nor Palm
  endogenise capital; both keep it as a GFCF final-demand column. That supports
  our baseline choice (see
  [docs/revision/results_2022.md, "Capital (GFCF) treatment"](../revision/results_2022.md#capital-gfcf-treatment)).

### 6. What Palm et al. actually do (the "simplified SNAC" template)

Domestic part from the national SRIO with national SEEA extensions; imports
from EXIOBASE multipliers, bridged by three concordances; feedback loops
(exports that return as imports) neglected, following Moran et al. (2018) on
their insignificance:

$$f^{(d+m)} = \mathbf{S}^d\,\mathbf{L}^d\,y^d + \mathbf{Q}^t\,\mathbf{A}^m\,\mathbf{L}^d\,y^d + \mathbf{Q}^t\,y^m + f^h$$

with $\mathbf{Q}^t$ built from EXIOBASE as

$$\mathbf{Q}^g = \mathbf{S}\,\mathbf{L}\,\hat{y}\,\mathbf{G}^p\,(y\,\mathbf{G}^p)^{-1}$$

(product concordance $\mathbf{G}^p$, weighted by EXIOBASE final demand), then
mapped to the national bilateral-trade country dimension via a binary country
concordance $\mathbf{G}^c$ and the trade-share matrix $\mathbf{B}$, plus a
currency conversion $c$ (their §2.2, pp. 636-637). These are the same maths our
pipeline already uses (compare
[section 3, stage 20](#simplified-snac-exiobase-coupling-and-danish-healthcare-footprint-accounting)
above); the innovation is entirely in the data plumbing.

### 7. Why Denmark is a good candidate: the ingredients are on the shelf

| Ingredient | Status | Where |
|:---|:---|:---|
| National IOT, **117 industries**, basic prices, current + previous-year prices, with an explicit **117-row import matrix** (imports by industry of origin × using industry) and tax/VAT rows | ✅ in repo, 2006-2022 | `data/bronze/dst_input_output/` (DST English workbooks; also via StatBank/API) |
| Detailed SUT (2,362 products × 117 industries, basic prices, domestic/import split `Ubas_dk`/`Ubas_imp`, margins and taxes sheets) | ✅ 2019 in repo; 2022 obtainable via DST (coarser preliminary commodity system for 2021-22) | `data/bronze/dk_umat_2019.xlsx` |
| National SEEA extensions on the **same DB07/117 classification**: DRIVHUS greenhouse gases (used already for Scope 1), plus energy accounts, and air-emission accounts for other pollutants | ✅ public API, t+9 months, through 2023+ | api.statbank.dk (DRIVHUS et al.) |
| EXIOBASE multipliers for the import side | ✅ local | see note below |
| Health-sector resolution in the national table | **6 relevant industries**: 860010 hospitals, 860020 medical & dental practices, 870000 residential care, 880000 social work, **210000 Pharmaceuticals**, 320010 medical instruments | vs EXIOBASE's single `Health and social work (85)` + `Chemicals nec` proxy |
| Health expenditure by SHA function for the demand side | ✅ DST SHA1 via API (CHE 2019: 234.6 bn; 2022: 271.9 bn DKK) | cross-checks the SUT-based vector |

**A correction to this section's original wording.** When this feasibility
question was first scoped, the EXIOBASE copy on disk for the import-side
multipliers was `IOT_2022_ixi.mat` **v3.10.2**. That release has since been
rejected as the study's background model: it misallocates the Danish block and
empties the medical-instruments industry across Europe, as set out in full in
[`exiobase_release_and_classification.md`](exiobase_release_and_classification.md).
**Any Danish-SNAC build must use v3.8.2, the current background model, for the
import-side multipliers**, not the v3.10.2 copy this memo originally pointed at.
The rest of the feasibility argument is unaffected: the ingredients on the
Danish side do not depend on which EXIOBASE release supplies the import side.

### 8. What the resolution buys: the three known weaknesses it removes

1. **The input-recipe problem.** Today the entire healthcare-services footprint
   hangs on EXIOBASE's *estimated* input column for DK "Health and social work"
   — the recipe that, at the time this section was first drafted, sat behind a
   transport-dominance headline of ~41 % of GWP. **That transport figure is now
   superseded and withdrawn**: the sea-transport reallocation corrected it to
   17.8 % of the supply-chain footprint (14.9 % of the total), documented in full
   in
   [docs/revision/results_2022.md, "The withdrawn transport finding"](../revision/results_2022.md#the-withdrawn-transport-finding).
   The recipe problem itself is unaffected by that correction and remains real:
   EXIOBASE's single estimated health-industry column is also behind the
   imploded Scope 2 (24 kt: EXIOBASE has DK health buying almost no energy
   directly, where Arup's Denmark sheet has Scope 2 alone at 8.3 % of the
   footprint). A Danish-SNAC model replaces that single recipe with four
   observed provider recipes (hospitals vs practices vs residential care vs
   social work) from the national SUT. **This replacement is the decisive
   scientific gain**, independent of the transport correction above.
2. **The pharma-mapping problem (Reviewer 1).** The national table has a real
   **Pharmaceuticals industry (210000)**: domestic pharma production no longer
   needs the Chemicals-nec proxy; only the imported share (large, but with
   observed country-of-origin totals in the import matrix) still runs through
   EXIOBASE, where the Piñero-style correction can be applied per origin.
3. **The import-allocation problem.** The current pipeline distributes
   pharma/appliance imports by EXIOBASE's final-demand sourcing proportions; the
   Danish SUT's `Ubas_imp` and the IOT import matrix provide the actual
   product-level import content per purpose.

### 9. Method blueprint (literature-anchored)

1. **Symmetric domestic table:** build from the rectangular DST SUT with an
   explicitly chosen construct, industry-technology/fixed-product-sales (Suh et
   al. 2010, eqs. 4-6) for an attributional footprint; or simply adopt DST's own
   symmetric IOT (already industry×industry, with the import matrix separated;
   half the work is done).
2. **Domestic extensions:** DRIVHUS + energy/air accounts on the same 117
   industries ($\mathbf{S}^d$ directly, no concordance needed: the accounts and
   the IOT share DB07).
3. **Import side:** EXIOBASE v3.8.2 multipliers $\mathbf{Q} = \mathbf{S}\,\mathbf{L}$,
   aggregated to the Danish product/industry classification with a weighted
   concordance (Palm §2.2); country dimension via the DST import matrix
   (117 origin-industries) or, at product level, bilateral trade shares.
   Currency via the documented annual DKK/EUR rate.
4. **Double-counting discipline:** strip re-exports; CIF→FOB with the
   trade/transport counter-entry (Schoer et al. 2013, p. 14284); one master flow
   list with each flow counted once (Pauliuk 2022's rule). For any process-based
   add-on, subtract the corresponding monetary flow before adding the inventory
   (tiered-hybrid rule, Nakamura 2023 §5.1.5/5.2).
5. **Refinement shortcut (low-cost first iteration):** before the full SNAC,
   apply the **Piñero et al. (2018) correction-matrix bridge**
   ($\mathbf{C} = \mathbf{P}\,\hat{p}_A^{-1}$; $\mathbf{W} = \mathbf{C}\,\hat{\alpha}$;
   $\mathbf{R}^* = \mathbf{W} \circ \mathbf{M}$) to inject EXIOBASE
   country-of-origin detail into the Danish import matrix without rebuilding
   anything. This bridge alone addresses weakness 3 and much of 2.
6. **Waste:** with the national core in place, the waste extension becomes a
   **WIO-style physical row set** (Nakamura 2023 §5.4): Danish waste statistics
   (Affaldsstatistik/ADS) by industry for the domestic side, Eurostat
   `env_wasgen` for EU partners, 2011-hybrid coefficients (or the non-public
   Merciai v4-2016, worth one request e-mail) for the rest of the world. This
   row set replaces the 2011-absolute-tonnes carry-forward entirely.

### 10. Error budget and validation

Schoer et al. (2013) bound the residual "national-model vs full-MRIO" gap at
~5-10% of the import-embodied component (<5% of the total), acceptable against
the recipe error it removes. Validation set: (i) domestic direct emissions must
reproduce DRIVHUS by construction; (ii) the EXIOBASE-only model (this revision)
brackets the comparison; (iii) Scope-2 result vs Arup's 8.3% and the regions'
own electricity/heat accounts (215.8 kt CO₂e in 2018 for the regions' el+heat+
transport, Danske Regioner); (iv) the national CBA footprint vs EXIOBASE-native
and Eurostat FIGARO values.

### 11. Effort and sequencing (recommendation)

- **Not for the current resubmission.** The revision stands on the corrected
  EXIOBASE-only model + uncertainty package; the response letter announces the
  hybrid as the follow-up (reviewers respond well to a concrete, cited plan).
- **Phase H1 (~days):** Piñero bridge on imports + validation of the EXIOBASE DK
  health recipe against the DST 117-industry health columns (energy, transport,
  pharma inputs). This validation yields the recipe-error quantification the
  transport headline needs *now*.
- **Phase H2 (~weeks):** full Danish-SNAC 2022 build per section 9, with the
  WIO-style waste rows. This build is a methods paper in its own right (Palm et
  al. was exactly that for Sweden) and the natural vehicle for the Denmark-2022
  flagship analysis.

**Price-basis discipline throughout** (Albert's standing caution): DST IOT/SUT
and DRIVHUS are basic-price/national-accounts consistent; EXIOBASE is
basic-price; health expenditure by SHA function arrives in purchaser-type
valuations. Every bridge states its valuation, and margins/taxes move through
the dedicated `Umargins`/`Utaxes` sheets, never inside a product flow.
