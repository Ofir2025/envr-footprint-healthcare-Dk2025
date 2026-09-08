# Scenarios: what we now have, and how to answer the reviewer

**The short answer.** We *do* now model scenarios — fourteen of them for climate,
in `data/gold/results/18_mitigation_scenarios/` — and the response to Reviewer 2
must be rewritten, because the version drafted before that layer existed says we
do not. The finding is not that mitigation is easy. It is the opposite, and it
is a stronger paper for it.

---

## 1. What is in the layer

Three kinds of scenario, and the distinction matters when writing the text.

**Background pathways** — the world changes around the health system, whether or
not the health system acts. Denmark's electricity and heat carbon intensity is
projected to fall from 122.7 to 16.9 g CO₂e/kWh. Applied at the transmission,
distribution and steam nodes (generation technologies carry almost none of the
footprint, so scaling them would double-count):

| Pathway | Horizon | Effect on the climate footprint |
|---|---|---|
| KF22 | 2030 | −6.7 % |
| KF22 | 2035 | −6.8 % |
| KF25 | 2030 | −5.7 % |
| KF25 | 2035 | −6.0 % |

The two vintages disagree by a percentage point; both are reported rather than
picking the flattering one.

**Interventions** — the health system acts.

| Lever | Ambition | Effect |
|---|---|---|
| Patient, visitor and staff travel | −10 % / −20 % / −30 % | −1.3 % / −2.7 % / −4.0 % |
| pMDI → dry-powder inhaler | 25 % / 50 % / 75 % substituted | −0.06 % / −0.12 % / −0.18 % |
| Nitrous oxide capture or reduction | 25 % / 50 % / 75 % | −0.06 % / −0.12 % / −0.18 % |

**Counterfactual** — demand growth of +18 % to 2035, which *adds* 848 kt, or
+18 %.

---

## 2. The result that should be in the paper

`target_consistency.csv` sets the levers against Danske Regioner's January 2024
target for the consumption-based CO₂ of hospitals:

| | kt CO₂e |
|---|---|
| 2022 baseline | 4,713 |
| Reduction the regional target requires | −2,357 |
| **Every modelled lever, at maximum ambition, combined** | **−732** |
| Share of the target those levers reach | **31 %** |
| Demand growth to 2035, business as usual | +848 |
| **Net position after demand growth** | **+117** |

*In words:* pulling every lever we can quantify, as hard as the literature
supports, closes under a third of the gap — and is then more than cancelled by
projected demand growth. The health system does not decarbonise by substituting
inhalers and capturing nitrous oxide, however worthwhile those are.

Two caveats belong with the number and are recorded in the file:

- The levers are summed independently, ignoring interaction, so **−732 kt is an
  upper bound**, not a central estimate.
- The regional target covers hospitals; our baseline covers health **and**
  eldercare. The comparison is indicative of scale, not a compliance assessment.

---

## 3. Why this strengthens the paper rather than weakening it

Reviewer 2's point was that identifying a hotspot is not the same as
demonstrating that acting on it works. That criticism is correct and we accepted
it. The scenario layer now lets us *demonstrate* the point rather than concede
it: the named clinical levers are real but small, the background grid pathway is
larger than all of them together, and demand growth is larger than everything.

That is a defensible and publishable finding — the mitigation lever that matters
for a health system's footprint is **procurement and demand**, not the clinical
substitutions that dominate the sustainable-healthcare literature. It follows
directly from the hotspot analysis: 37 % of the climate footprint is
pharmaceuticals and chemical products, and no scenario in the literature acts on
that.

---

## 4. What must change in the submitted response

Two passages in `response_to_reviewers.md` were written before this layer
existed and now contradict the repository:

1. **R2-7** currently reads *"The paper identifies hotspots; it does not model
   mitigation"* and offers scenario modelling as "the natural next study". That
   should become: we accept the distinction, we now model it, and here is what
   it shows.
2. The **"What we have not done"** bullet *"Mitigation scenarios are not
   modelled (R2-7)"* is simply no longer true and must be removed.

Both are corrected in this revision — see the diff on that file.

What we still have not done, and should say so:

- No behavioural or economic model sits behind the intervention levers; they are
  imposed percentage reductions, not modelled responses to a policy.
- Interaction between levers is not modelled, which is why the combined figure
  is an upper bound.
- Only climate has a full scenario set. The other four categories are computed
  for the background pathway but the clinical levers do not act on them.

---

## 5. Where it is

| | |
|---|---|
| Module | `analysis.mitigation_scenarios` |
| Tables | `data/gold/results/18_mitigation_scenarios/mitigation_scenarios.csv`, `target_consistency.csv` |
| Figure | `figures/manuscript/2022/fig8_mitigation_scenarios_2022.tiff` |
| Method note | `docs/methods/replications/18_mitigation_scenarios.md` |

Reproduce with:

```bash
HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship PYTHONPATH=src python -m analysis.mitigation_scenarios
```
