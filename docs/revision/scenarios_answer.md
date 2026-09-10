# Scenarios: what we now have, and how to answer the reviewer

**For Ofir.** The short version: we model scenarios properly now (fourteen
lever families across **all five impact categories**, each a full counterfactual
solve rather than a scaled term), and the result is a finding worth leading on
rather than a limitation to concede.

Method, equations, and every assumption:
[`docs/methods/replications/18_mitigation_scenarios.md`](../methods/replications/18_mitigation_scenarios.md).
Figures: `fig8_mitigation_waterfall_2022` and `fig9_burden_shifting_2022`.

---

## 1. What changed, and a correction to an earlier number

An earlier version of this note reported that "every lever at maximum ambition
reaches 31 % of the target". That figure came from summing the separate answers
of levers that had only been computed for climate, and it included the grid
pathway inside the total without saying so. Both are now fixed, and the
comparable numbers are:

| | kt CO₂e | share of the target |
|:---|:---|:---|
| All interventions, solved simultaneously (C1) | −361 | **15 %** |
| Interventions **plus** the Danish grid pathway (C3) | −461 | **20 %** |

The 20 % is the like-for-like replacement for the old 31 %. Three things
separate them: a tighter, better-sourced lever set; an old sum that double
counted where levers overlap; and the grid pathway now being restricted to the
Danish grid, which is what the Danish Energy Agency's projection covers.
Applying that trajectory to every region's grid, which an earlier version did,
would give −321 kt from the pathway instead of −145 and would put the combined
figure back at 27 %. That variant is still computed and reported as **B1G**, an
upper bound rather than an evidenced trajectory.

Three things also changed in kind, not just in value:

1. **All five impact categories** are now computed for every scenario. Three of
   the five were previously being set to zero rather than calculated, so burden
   shifting was invisible by construction.
2. **Levers act on the right object.** A lever that changes a production recipe
   now edits the technical coefficient matrix, and the system is re-solved, so
   the effect propagates through the supply chain. Previously nothing could.
3. **Combination is a simultaneous solve**, not a sum.

---

## 2. The scenario set

The scenario set is grounded in stated Danish policy and measured Danish
outcomes. Anything not sourced is labelled *illustrative* in the output and
nowhere else.

**Background pathway** (happens regardless of what the health system does):
grid and district-heat decarbonisation from 122.7 to 16.9 g CO₂e/kWh on the
Danish Energy Agency's KF22 projection, and to 32.4 on KF25. Both vintages are
reported rather than the more flattering one; they differ by a percentage point
on the same lever.

**Interventions** (the health system acts):

| | Lever | Evidence |
|:---|:---|:---|
| P1 | Hospital energy and transport | Danske Regioner's own target: −75 % by 2030 against 2018 |
| P2 | Pharmaceutical raw-material efficiency | Lundbeck: −15 % raw material 2020→2022 while production rose 18 % |
| P3 | Medical-device packaging carbon | Demant: −12 % to −23.5 % cradle-to-gate |
| P4 | Reuse of medical equipment | the regions' stated procurement focus; the level is illustrative |
| P5 | Patient, visitor, and staff travel | Danish travel survey; the level is illustrative |
| P6 | Inhaler **propellant** change | Jeswani & Azapagic: −67 % low-charge, −93 % HFA-152a |
| P7 | pMDI → dry-powder inhaler | Jeswani & Azapagic: 380× lower GWP per 100 doses |
| P8 | Nitrous oxide capture | Denmark's national inventory, 38 t N₂O/year |
| P9 | Waste diverted from incineration to recycling | Circular Industrial Plastic partnership; the level is illustrative |

**Counterfactual**: +18 % demand growth to 2035, Danske Regioner's own
business-as-usual trajectory.

---

## 3. The result to lead on

| | kt CO₂e |
|:---|:---|
| 2022 baseline | 4,712 |
| Reduction the regional target requires | −2,357 |
| Every intervention at maximum ambition, solved together | −361 |
| …with the Danish grid decarbonising too | −461 |
| …with the money saved actually being respent | −281 |
| Demand growth to 2035 | +848 |
| **2035 position, grid pathway included** | **5,100, above the 2022 baseline** |

*In words:* pull every lever we can quantify, as hard as the evidence supports,
let the Danish grid decarbonise on the government's own projection, and the
Danish health-care climate footprint in 2035 is still **higher than it is
today**, because demand grows faster than the levers bite.

That is a publishable finding, and it is the honest answer to the reviewer's
point. Identifying a hotspot is not the same as showing that acting on it
works, and when you do the work, the named clinical levers turn out to be worth
0.1-4 % each while demand growth is worth +18 %.

Two further results are worth their own sentences:

**The levers are near-additive.** Summing them separately overstates the
combined effect by 0.2 kt out of 361, under 0.1 %. That had to be computed to be
known, and it means the additive presentation common in this literature is
defensible *here*; it would not be if the levers overlapped more.

**Rebound removes a fifth of the saving.** Holding total expenditure constant
(the money not spent on devices is spent on something else) takes the combined
saving from −361 to −285 kt. Reporting a demand-reduction scenario without
rebound assumes the money is destroyed.

---

## 4. Burden shifting: the reason all five categories matter

- **Pharmaceutical raw-material efficiency is a materials lever, not a climate
  lever**: −1.6 % climate against **−3.3 % material extraction**. The
  pharmaceutical hotspot is a materials hotspot, and a climate framing would
  not have selected the intervention that addresses it.
- **Rebound shifts burden.** Holding expenditure constant improves climate and
  materials but **worsens blue water (+0.63 %), land use (+0.58 %), and waste
  (+0.27 %)**. The money is respent inside health care, not on a thirstier
  basket: the purchases the levers cut, energy and devices, are less water-
  and land-intensive than the health-care average, so holding expenditure
  constant tilts the basket towards what remains. This burden shift is the
  clearest trade-off in the study and only appears when rebound and all five
  categories are modelled together.
- **Waste diversion backfires slightly on climate** while cutting waste.
  Recycling services have their own supply chain.
- **Dry-powder inhalers trade climate for other pressures.** Jeswani and
  Azapagic report them as worse than pressurised inhalers for abiotic
  depletion, eutrophication, and ecotoxicity. Those act on the device life
  cycle, which this model does not resolve, so figure 9 marks those cells
  `n.r.` rather than plotting a zero, and the direction is stated in the text.
  This device-level trade-off is also why P6 (changing the propellant, not the
  device) is the better lever: it carries no therapeutic trade-off, since
  medicine and delivery route are unchanged.

---

## 5. What must change in the submitted response

Two passages in `response_to_reviewers.md` were written before this layer
existed. Both are corrected in this revision:

1. **R2-7** said "the paper identifies hotspots; it does not model mitigation".
   It now reports what the scenarios show.
2. The **"What we have not done"** bullet said mitigation scenarios are not
   modelled. It now states the real limitations: no behavioural or economic
   model behind the intervention levels, no price response, and interaction
   between levers computed but not driven by any market mechanism.

**We do not rebalance the table.** When a scenario changes a production recipe,
the edited table no longer satisfies the identity that column sums plus value
added equal total output, because the model is not told what the industry does
with the money it stops spending. We leave that imbalance in place, measure it,
and report it per scenario rather than forcing the table back onto its totals.
Rebalancing would partly undo the intervention and return a smaller effect than
it implies, and would require an assumption we do not have; Lenzen et al. (2010)
decline to rebalance for the same reason. The largest departure across the whole
scenario set is 0.7 % of total output, on the pharmaceutical lever at full
market penetration. Every intensity-only and demand-only scenario is exactly
balanced, and so is the waste diversion, because it substitutes fully.

What we still do not claim, and should say plainly:

- The model is **attributional**. A scenario is a what-if on the recipe, not a
  forecast of how the economy reacts. Schmidt and Merciai's Danish work is
  consequential and answers a different question.
- **"Green" versions of a product cannot be represented.** EXIOBASE has one
  *Chemicals nec* industry, so a hospital switching to a lower-impact supplier
  of the same product appears only as buying less. This aggregation is the
  single biggest limitation on a procurement lever, and it is why green
  procurement, which the regions say is where most of their emissions sit,
  cannot be given the weight their own strategy gives it. A hybrid or
  physically extended table is the fix, and the natural next study.
- Ambition levels for P4, P5, and P9 are **illustrative**, not policy targets.

---

## 6. Where it is

| | |
|:---|:---|
| Engine | `analysis.scenario_engine` |
| Scenarios | `analysis.mitigation_scenarios` |
| Tables | `18_mitigation_scenarios/mitigation_scenarios.csv`, `target_consistency.csv`, `burden_shifting.csv` |
| Figures | `figures/manuscript/2022/fig8_mitigation_waterfall_2022.tiff`, `fig9_burden_shifting_2022.tiff` |
| Method note | `docs/methods/replications/18_mitigation_scenarios.md` |

```bash
HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship PYTHONPATH=src python -m analysis.mitigation_scenarios
HC_ANALYSIS_YEAR=2022 Rscript R/plot_scenarios.R
```

---

## References

Full entries with DOIs in [`docs/references.md`](../references.md).

- Aguilar-Hernandez, G. A., Sigüenza-Sanchez, C. P., Donati, F., Rodrigues,
  J. F. D., & Tukker, A. (2018). Assessing circularity interventions: A review
  of EEIOA-based studies. *Journal of Economic Structures, 7*, 14.
  https://doi.org/10.1186/s40008-018-0113-3
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
- Lenzen, M., Wood, R., & Wiedmann, T. (2010). Uncertainty analysis for
  multi-region input-output models: A case study of the UK's carbon footprint.
  *Economic Systems Research, 22*(1), 43-63.
  https://doi.org/10.1080/09535311003661226
- Onat, N. C., Mandouri, J., Kucukvar, M., Sen, B., Abbasi, S. A., Alhajyaseen,
  W., Kutty, A. A., Jabbar, R., Contreras, M. T., & Jraisat, L. (2023). Rebound
  effects undermine carbon footprint reduction potential of autonomous electric
  vehicles. *Nature Communications, 14*, 6258.
  https://doi.org/10.1038/s41467-023-41992-2
- Takase, K., Kondo, Y., & Washizu, A. (2005). An analysis of sustainable
  consumption by the waste input-output model. *Journal of Industrial Ecology,
  9*(1-2), 201-219. https://doi.org/10.1162/1088198054084653
- Wiebe, K. S., Bjelle, E. L., Többen, J., & Wood, R. (2018). Implementing
  exogenous scenarios in a global MRIO model for the estimation of future
  environmental footprints. *Journal of Economic Structures, 7*, 20.
  https://doi.org/10.1186/s40008-018-0118-y
