# 14 - Eckelman & Sherman replication

**Gold folder** `data/gold/results/14_eckelman_replication/`
**Module** `analysis.eckelman_replication`
**Source** Eckelman & Sherman (2016), *Environmental impacts of the US health care system
and effects on public health*, PLoS ONE 11:e0157014

## Question this layer answers

This layer places Denmark on the nine-category frame of the most-cited health-sector
footprint study, including its health-damage estimate in DALYs.

## Method

### What can and cannot be compared

Their absolute values are in **TRACI** reference substances as implemented inside the CMU
EIO-LCA tool: PM₁₀-equivalents, benzene-equivalents, toluene-equivalents. Our
characterisation uses CML 1999 and the ILCD recommended factors, whose reference substances
differ.

**Absolute values are therefore not comparable, and are not compared here.** Reporting a
Danish "benzene-equivalent" beside a TRACI one would be a unit error dressed as a result.

Two things are comparable:

1. **Share of the national total.** Unit-free, it is what their abstract leads with, and it
   is what a reader wants: how much of a country's environmental burden is its health
   system.
2. **Damage in DALYs**, where both sides have an endpoint method: theirs via TRACI/ReCiPe
   endpoints, ours via the ILCD endpoint factors in the DESIRE workbook
   ([12](12_impact_categories_full.md)). The method is named on both sides in every row.

$$\text{DALY}_c = C_c^{\text{endpoint}}\, S\, L\, y_H$$

## Data requirements

This layer needs the full impact-category table from
[12](12_impact_categories_full.md); Danish and US population; and their nine published
category values and national shares, transcribed with their `eckelman_code`.

## Deviations from the source, stated

- Their model is the CMU EIO-LCA US table for 2007-2013; ours is EXIOBASE 2022. Both the
  model family and the year differ, so the comparison is a *frame* replication, not a
  like-for-like benchmark. It is labelled as such in every output row (`us_method`,
  `dk_method`).
- Ozone depletion is **retracted** on our side: the DESIRE factor for that category failed
  the quality tests in [12](12_impact_categories_full.md). It appears in the output with
  the Danish value withheld and the reason stated, rather than being quietly omitted.

## Outputs

| File | Content |
|:---|:---|
| `nine_categories_dk_vs_us.csv` | their nine categories, US and Danish values, national shares, method named per side |
| `damage_daly_dk_vs_us.csv` | DALYs and DALYs per 1,000 population, with each side's method |

## Verification

Every row carries both methods explicitly, so no row can be read as a like-for-like
comparison when it is not.
