# 18 · Counterfactual scenarios

**Modules** `analysis.scenario_engine` (machinery), `analysis.mitigation_scenarios`
(the scenarios) · **Outputs** `data/gold/results/18_mitigation_scenarios/`
· **Figures** `fig8_mitigation_waterfall_2022`, `fig9_burden_shifting_2022`

This layer answers the second reviewer's request to separate identifying a
hotspot from demonstrating that acting on it works. It is written so the text
can be lifted into the manuscript's Methods and Results with light editing; every
assumption is named, every ambition level carries its evidence, and everything
the model cannot do is stated rather than left to be discovered.

---

## 1. Why the previous implementation was replaced

Scenario results were produced by scaling one term of the deterministic
footprint and reporting the difference. That is adequate for a lever acting on a
single bottom-up item and wrong for anything else:

- it could not propagate an effect through the supply chain, so no lever could
  act on a production recipe;
- it reported **climate only**, so a trade-off between impact categories was
  invisible by construction — and three of the five categories were being set to
  zero rather than computed;
- levers were combined by adding their separate answers, which double counts
  every interaction between them.

The layer now follows the counterfactual formalism the environmentally extended
input–output literature has converged on (Aguilar-Hernandez et al., 2018; Donati
et al., 2020; Wiebe et al., 2018), so that these results are comparable with
published circular-economy and future-footprint studies rather than being a
bespoke calculation.

---

## 2. The model

### 2.1 Reference and counterfactual

A scenario is a triple of edited objects and a second full solution of the
Leontief system. Writing $\mathbf{B}$ for the impact intensity matrix,
$\mathbf{A}$ for the technical coefficients, $\mathbf{y}$ for health-care final
demand, $\mathbf{d}$ for the direct (operational) vector of the Danish health
industry and $\mathbf{u}$ for the bottom-up items outside the MRIO:

$$\mathbf{r} = \mathbf{B}\,(\mathbf{I}-\mathbf{A})^{-1}\mathbf{y} + \mathbf{d} + \mathbf{u} \tag{1}$$

$$\mathbf{r}^{*} = \mathbf{B}^{*}(\mathbf{I}-\mathbf{A}^{*})^{-1}\mathbf{y}^{*} + \mathbf{d}^{*} + \mathbf{u}^{*} \tag{2}$$

$$\Delta = \mathbf{r}^{*} - \mathbf{r} \tag{3}$$

Equations (1)–(3) are Aguilar-Hernandez et al.'s (2018) equations 1–3 with the
direct and bottom-up terms this study adds. The counterfactual is **solved**,
not approximated from the baseline inverse: `numpy.linalg.solve` on
$(\mathbf{I}-\mathbf{A}^{*})$ takes about three seconds on a 7,987 × 7,987
model, and agrees with the stored Leontief inverse to 1 × 10⁻¹¹, so there is no
reason to reuse a stale one.

### 2.2 Change coefficients

Every edit is

$$M^{*}_{ij} = M_{ij}\,(1 - k_a), \qquad k_a = k_t \, k_p \tag{4}$$

after Donati et al. (2020, §2.4). $k_t$ is the **technical** change coefficient
— what the intervention achieves where it is applied — and $k_p$ the **market
penetration** coefficient — the share of the affected market that adopts it.

Splitting the two is what makes an ambition level auditable. A reader can accept
the engineering evidence for $k_t$ and still disagree about $k_p$, and can see
which is which. Both are recorded per scenario in the output table, along with
the source for each.

Where a reduction in one input is taken up by another,

$$M^{*}_{ij} = M_{ij} + \alpha\,(M^{*}_{mn} - M_{mn}) \tag{5}$$

with $\alpha$ a substitution weighting factor (Donati et al., 2020, eq. 6). The
released quantity is spread over the substitute rows **in proportion to their
existing size**, so a substitution cannot invent a supply relation that the
table does not already contain.

### 2.3 Rebound

Money not spent on one product does not vanish. Where a scenario reduces final
demand, the engine can hold total expenditure constant and redistribute the
released budget over the remaining demand in proportion to existing shares:

$$\mathbf{y}^{**} = \mathbf{y}^{*}\,\frac{\mathbf{i}'\mathbf{y}}{\mathbf{i}'\mathbf{y}^{*}} \tag{6}$$

This is the zero-cost counterfactual of Donati et al. (2020), after Takase et
al. (2005) as formalised by Aguilar-Hernandez et al. (2018, eq. 4). It is a
crude rebound — it assumes the released budget is spent on the same basket, and
ignores the price and income mechanisms that Onat et al. (2023) show can matter
more. But reporting a demand-reduction scenario *without* it silently assumes
the money is destroyed, which is a stronger and less defensible assumption.
**Both are reported** (C1 and C2), and the difference between them is the
rebound.

### 2.4 What the accounts do to an edited table

Editing $\mathbf{A}$ breaks the identity that column sums plus value added equal
total output, because the model is not told what an industry does with money it
stops spending on an input (Donati et al., 2020, §2.3). The engine measures the
imbalance,

$$\text{imbalance} = \frac{\bigl|\,\mathbf{i}'(\mathbf{A}-\mathbf{A}^{*})\,\mathbf{x}^{*}\bigr|}{\mathbf{i}'\mathbf{x}^{*}} \tag{7}$$

and reports it per scenario in `unbalanced_pct_of_output`. It is zero for every
intensity- and demand-only scenario, zero for the waste diversion (which
substitutes fully, $\alpha = 1$), and **0.7 % of total output** for the
pharmaceutical resource-efficiency lever at full market penetration. Stating it
is the point: a reader can see how far each counterfactual departs from balance
instead of being asked to assume it does not.

---

## 3. The scenarios

Grounded in stated Danish policy and measured Danish outcomes wherever
possible. Ambition levels that are **not** sourced are labelled *illustrative*
in the `ambition_basis` column of the output and nowhere else.

| ID | Lever | Object edited | $k_t$ and its evidence |
|---|---|---|---|
| **B1** | Grid and district-heat decarbonisation | $\mathbf{B}$, energy nodes | 122.7 → 16.9 g CO₂e/kWh (KF22) and → 32.4 (KF25) by 2030 (Danish Energy Agency, 2022, 2025) |
| **P1** | Hospital energy and transport | $\mathbf{y}$, Danish energy nodes | −75 % by 2030 against 2018, all public hospitals (Danske Regioner, 2024, as reported in Healthcare Denmark, 2024) |
| **P2** | Pharmaceutical raw-material efficiency | $\mathbf{A}$, Danish chemicals column | −15 % raw-material use 2020→2022 while production rose 18 % (Lundbeck, in Healthcare Denmark, 2024) |
| **P3** | Medical-device packaging carbon | $\mathbf{A}$, paper and plastics into medical instruments | −12 % to −23.5 % cradle-to-gate (Demant, in Healthcare Denmark, 2024) |
| **P4** | Reuse of medical equipment | $\mathbf{y}$, devices, with $\alpha=0.3$ into repair services | −10 % / −20 %, **illustrative**; the direction is the regions' stated procurement focus |
| **P5** | Patient, visitor and staff travel | bottom-up, **all five categories** | −10 % / −20 % / −30 %, **illustrative** |
| **P6** | Inhaler propellant change | bottom-up, pMDI | −67 % (low-charge) and −93 % (HFA-152a) of propellant GWP (Jeswani & Azapagic, 2019) |
| **P7** | pMDI → dry-powder inhaler | bottom-up, pMDI | 25 / 50 / 75 % substituted; DPI GWP is 0.06 against 23.4 kg CO₂e per 100 doses (Jeswani & Azapagic, 2019) |
| **P8** | Nitrous oxide capture | bottom-up, anaesthetic | 25 / 50 / 75 %, with $k_p = 0.6$ because N₂O is 60 % of the Danish anaesthetic term |
| **P9** | Divert health-care waste to recycling | $\mathbf{A}$, incineration → recycling, $\alpha=1$ | 20 / 40 %, **illustrative** |
| **C1** | All interventions, simultaneous | all | — |
| **C2** | C1 with expenditure held constant | all, plus eq. (6) | — |
| **C3** | C1 plus the grid pathway | all | — |
| **X** | Demand growth to 2035 | $\mathbf{y}$, scaled | +18 %, Danske Regioner business-as-usual |

Two structural findings shaped the design, both verified on this model rather
than assumed.

**Danish electricity emissions are not on the generation technologies.** Direct
intensities are 3.208 kt CO₂e per M.EUR for *Transmission of electricity* and
18.733 for *Steam and hot water supply*, against 0.013 for coal generation and
0.020 for wind. All eleven Danish generation-by-technology industries together
contribute 0.82 kt to the health-care footprint; transmission contributes 68.2
and steam 94.0. A technology-mix reallocation in $\mathbf{A}$ is therefore
inoperative, and grid decarbonisation must act on $\mathbf{B}$ at the
transmission, distribution and steam nodes. Two Danish nodes (solar thermal,
tide/wave) carry nowcast-artefact intensities of 13,256 and 55,322 and are
excluded from any scaling.

**The health sector buys catering, not food.** 78 % of its food-related spend is
*Hotels and restaurants*, so a dietary lever is a change to that industry's
input column, not to final demand.

---

## 4. Results

### 4.1 Climate

| | kt CO₂e | of the 2022 baseline |
|---|---|---|
| 2022 baseline | 4,713 | — |
| Reduction the regional target requires | −2,357 | −50 % |
| All interventions, solved simultaneously (**C1**) | **−361** | −7.7 % |
| The same levers summed separately | −362 | — |
| Interaction | −0.2 | — |
| Interventions with the grid pathway (**C3**) | **−634** | −13.5 % |
| Interventions with expenditure held constant (**C2**) | −285 | −6.0 % |
| Rebound, i.e. what respending removes | +77 | 21 % of the saving |
| Demand growth to 2035, business as usual | +848 | +18 % |
| **Net 2035 position, grid pathway included** | **+215** | **+4.6 %** |

Three things are worth saying in the paper.

**The levers are close to additive.** Summing them separately overstates the
combined effect by 0.2 kt out of 361 — under 0.1 %. That is a *result*, not an
assumption: it had to be computed to be known, and it means the naive additive
presentation common in this literature happens to be defensible here. It would
not be if the levers overlapped more.

**Respending removes a fifth of the saving.** C2 is 77 kt weaker than C1. A
scenario reported without rebound is reporting the case where the money is
destroyed.

**Demand growth is larger than everything.** Every quantified lever at maximum
ambition, plus a decarbonising grid, reaches 27 % of the regional target and is
then more than cancelled by projected demand growth, leaving the 2035 footprint
**above** the 2022 baseline. This is the substantive finding, and it follows
directly from the hotspot analysis: the levers that dominate the sustainable
healthcare literature act on 2 % of the footprint, while pharmaceuticals and
chemical products — 37 % of climate and 51 % of material extraction — are acted
on by no published scenario we could find.

### 4.2 Burden shifting

Reporting all five categories was the point of the rebuild, and it changes what
can be said.

- **P2, pharmaceutical raw-material efficiency, is a materials lever more than a
  climate lever**: −1.6 % climate against **−3.3 % material extraction**. The
  pharmaceutical hotspot is a materials hotspot, and the intervention that
  addresses it is not the one the climate framing would select.
- **C2 shifts burden.** Holding expenditure constant improves climate (−6.0 %)
  and materials (−2.6 %) but **worsens blue water (+0.63 %), land use (+0.58 %)
  and waste (+0.27 %)**, because the released budget is respent on a basket that
  is more land- and water-intensive than the health basket it left. This is the
  clearest trade-off in the study and it only appears once rebound and all five
  categories are modelled together.
- **P9, waste diversion, backfires slightly on climate** (+0.002 %) while
  cutting waste (−0.04 %). Recycling services have their own supply chain. The
  magnitudes are trivial because the health sector's direct purchases of
  incineration are small, but the sign is real and is reported.
- **P6, P7 and P8 are climate-only by data, not by finding.** The bottom-up
  inventory behind propellants and anaesthetic gases carries no non-climate
  columns, so those cells are marked `n.r.` in figure 9 rather than plotted as
  zero. Jeswani and Azapagic (2019) report the dry-powder inhaler as **worse**
  than the pressurised inhaler for abiotic depletion of elements,
  eutrophication, and freshwater and terrestrial ecotoxicity; that trade-off is
  real, acts on the device life cycle which this MRIO does not resolve, and is
  therefore reported directionally rather than given an invented number.

---

## 5. Stress tests

| Test | Result |
|---|---|
| Baseline reproduces the study headline | asserted in code; scenario baseline within 1 % of 4,713.368 kt, and equal to it |
| Counterfactual solve against the stored inverse | agrees to 1 × 10⁻¹¹ |
| Levers summed vs solved simultaneously | 0.2 kt apart on climate; reported, not assumed |
| Accounting imbalance from editing **A** | 0 for B- and y-only scenarios; 0.7 % of output at the largest A edit; reported per scenario |
| Two official grid-projection vintages | KF22 and KF25 differ by 1.0 pp on the same lever; both reported rather than the more flattering one |
| Market penetration | P2 reported at 25 / 50 / 100 % of Danish production, because the share achieving Lundbeck's result is unknown |
| Rebound on/off | C1 vs C2; 21 % of the saving |
| Substitution keeps balance | P9 with $\alpha = 1$ has zero imbalance, as it must |

---

## 6. What is deliberately not modelled

- **Price and market responses.** The model is attributional. A scenario is a
  what-if on the recipe, not a forecast of how the economy reacts. Schmidt and
  Merciai's (2023) Danish work is consequential and answers a different
  question; the comparison in layer 06 is boundary-matched precisely because the
  two cannot be compared directly.
- **"Green" versions of a product.** EXIOBASE has one *Chemicals nec* industry,
  so a hospital switching to a lower-impact supplier of the same product cannot
  be represented as a substitution — only as buying less. Green procurement is
  therefore modelled as volume reduction plus lifetime extension (P4), and this
  limitation is why a procurement lever cannot be given the weight the regions'
  own strategy gives it. Resolving it needs a hybrid or physically extended
  table, which is the natural next study.
- **Capacity constraints and re-employment of released output.** Only C2 does
  anything with the released expenditure, and it does the simplest possible
  thing.
- **Behavioural response.** The intervention levels are imposed, not modelled.
  P4, P5 and P9 are illustrative ambitions and say so.
- **Dynamics.** These are comparative-static counterfactuals on a 2022 table,
  not a pathway. Wiebe et al. (2018) show how exogenous scenario trajectories
  can be implemented in a global MRIO; doing so here would require projecting
  $\mathbf{A}$, which this study does not attempt.

---

## References

Full entries with DOIs are in [`docs/REFERENCES.md`](../../REFERENCES.md).

- Aguilar-Hernandez, G. A., Sigüenza-Sanchez, C. P., Donati, F., Rodrigues,
  J. F. D., & Tukker, A. (2018). Assessing circularity interventions: A review
  of EEIOA-based studies. *Journal of Economic Structures, 7*, 14.
  https://doi.org/10.1186/s40008-018-0113-3
- Danish Energy Agency. (2022). *Klimastatus og -fremskrivning 2022 (KF22)*.
  https://ens.dk
- Danish Energy Agency. (2025). *Klimastatus og -fremskrivning 2025 (KF25)*.
  https://ens.dk
- Danske Regioner. (2024). *Klimahandling i regionerne*. https://www.regioner.dk
- Donati, F., Aguilar-Hernandez, G. A., Sigüenza-Sánchez, C. P., de Koning, A.,
  Rodrigues, J. F. D., & Tukker, A. (2020). Modeling the circular economy in
  environmentally extended input-output tables: Methods, software and case
  study. *Resources, Conservation and Recycling, 152*, 104508.
  https://doi.org/10.1016/j.resconrec.2019.104508
- Healthcare Denmark. (2024). *Transitioning towards a sustainable healthcare
  sector* [White paper]. https://www.healthcaredenmark.dk
- Jeswani, H. K., & Azapagic, A. (2019). Life cycle environmental impacts of
  inhalers. *Journal of Cleaner Production, 237*, 117733.
  https://doi.org/10.1016/j.jclepro.2019.117733
- Kagawa, S., Nansai, K., & Kudoh, Y. (2009). Does product lifetime extension
  increase our income at the expense of energy consumption? *Energy Economics,
  31*(4), 597-606. https://doi.org/10.1016/j.eneco.2008.08.011
- Onat, N. C., Mandouri, J., Kucukvar, M., Sen, B., Abbasi, S. A., Alhajyaseen,
  W., Kutty, A. A., Jabbar, R., Contreras, M. T., & Jraisat, L. (2023). Rebound
  effects undermine carbon footprint reduction potential of autonomous electric
  vehicles. *Nature Communications, 14*, 6258.
  https://doi.org/10.1038/s41467-023-41992-2
- Schmidt, J. H., & Merciai, S. (2023). *Danish consumption-based environmental
  footprints using a hybrid consequential input-output model*. 2.-0 LCA
  consultants. https://lca-net.com
- Takase, K., Kondo, Y., & Washizu, A. (2005). An analysis of sustainable
  consumption by the waste input-output model. *Journal of Industrial Ecology,
  9*(1-2), 201-219. https://doi.org/10.1162/1088198054084653
- Wiebe, K. S., Bjelle, E. L., Többen, J., & Wood, R. (2018). Implementing
  exogenous scenarios in a global MRIO model for the estimation of future
  environmental footprints. *Journal of Economic Structures, 7*, 20.
  https://doi.org/10.1186/s40008-018-0118-y
