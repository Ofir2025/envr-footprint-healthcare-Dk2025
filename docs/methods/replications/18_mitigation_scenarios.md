# 18 — Mitigation scenarios

**Gold folder** `data/gold/results/18_mitigation_scenarios/`
**Module** `analysis.mitigation_scenarios`
**Sources** Danish Energy Agency *Klimastatus og -fremskrivning* (KF22, KF25);
Danske Regioner climate targets

## Question this layer answers

Reviewer 2's R2-7: the manuscript identifies hotspots but does not model mitigation. What
would plausible Danish decarbonisation actually deliver, and what would it not?

## Method

### Grid decarbonisation

The Danish grid emission factor is projected from the official climate projections:

| Projection | 2022 | 2030 |
|---|---|---|
| KF22 | 122.7 g/kWh | 16.9 g/kWh |
| KF25 | 122.7 g/kWh | 32.4 g/kWh |

The scenario rescales the direct intensity of the Danish energy nodes and re-solves:

$$s'_i = s_i \cdot \frac{g_{2030}}{g_{2022}} \quad \text{for } i \in \text{energy nodes},
\qquad f' = s'\,L\,y_H$$

Two projections are run, not one, because the 2025 projection is materially less optimistic
than the 2022 one and a single figure would overstate confidence.

### Which nodes count as "the grid"

`ENERGY_NODE_PATTERNS` covers **transmission, distribution and steam** — deliberately
**not** generation. Generation technologies are separate EXIOBASE industries whose own
intensities the projection does not describe; rescaling them would double count the
transition. `ARTEFACT_NODE_PATTERNS` excludes solar-thermal and tide/wave nodes, which
carry EXIOBASE artefacts at Danish scale.

### Regional target consistency

Danske Regioner commit to a 50 % reduction by 2035 against a 2022 baseline.
`target_consistency.csv` places that target beside what the modelled scenarios deliver, and
records the caveat: the target is defined on the regions' **own** scope 1 and 2, while this
study's footprint is dominated by scope 3 — so the two are not the same quantity and the
target cannot be read as a footprint reduction.

## Data requirements

KF22 and KF25 grid factors; Danske Regioner target text; $s$, $L$, $y_H$; the Danish energy
node index.

## Deviations from the source, stated

- The scenarios hold **$A$, $L$ and $y_H$ fixed** and vary only intensities. They are
  therefore *ceteris paribus* sensitivities, not forecasts: they answer "what would this
  footprint be if the grid decarbonised as projected and nothing else changed". Structural
  change, demand change and foreign decarbonisation are all excluded.
- Foreign grids are **not** decarbonised, which is conservative given that 73.7 % of the
  footprint arises abroad. This is the single largest limitation and is stated in the
  output's `note` column on every row.

## Outputs

| File | Content |
|---|---|
| `mitigation_scenarios.csv` | per scenario, ambition and indicator: baseline, change, scenario value, per-capita change, source |
| `target_consistency.csv` | the Danske Regioner target beside the modelled scenarios, with the scope caveat |

## Verification

Each scenario reports its baseline in the same row as its result, so no scenario value can
be quoted without the baseline it is a change from.
