# 15 - Climate characterisation vintage

**Gold folder** `data/gold/results/15_gwp_vintage/`
**Module** `analysis.gwp_vintage`
**Source** IPCC AR6 WG1 Table 7.15 and WG3 Annex II; AR4, AR5 for the sensitivity

## Question this layer answers

This study reports climate change on **IPCC AR6**. The characterisation workbook shipped
with the background instead carries **AR4** factors (CH₄ = 25, N₂O = 298) under a sheet
labelled "CML 1999". What does the restatement change, and what can it not reach?

## Method

The climate row is rebuilt from the stressor names rather than read from the workbook, in
`analysis.constants.ar6_gwp_factor`:

| Species | AR6 GWP100 |
|---|---|
| CO₂ | 1 |
| CH₄, fossil | 29.8 |
| CH₄, non-fossil | 27.0 |
| N₂O | 273 |
| SF₆ | 25 200 |

AR6 distinguishes fossil from non-fossil methane. The fossil marker list
(`CH4_FOSSIL_MARKERS`) covers gas and oil extraction, coal and lignite mining, and oil
refining. **Combustion methane is deliberately excluded** from that list: AR6 WG3 Annex II
assigns 27.0 to fossil-*combustion* methane, so treating it as fossil-extraction methane
would over-characterise it.

$$f_{\text{climate}} = \sum_g \mathrm{GWP}_g^{(v)} \cdot m_g \quad \text{for vintage } v$$

The footprint is restated under four assessment vintages, and the results reported side by
side.

### The limit of the restatement, reported not hidden

EXIOBASE reports **HFC and PFC already aggregated in kg CO₂-equivalent**, not as individual
species. Whatever GWP vintage was used to aggregate them is fixed inside the data and
cannot be recovered from the satellite account. Those two stressors are therefore excluded
from the restatement, and the share of the footprint that **cannot** be restated is
reported (`not_restatable` column).

Everything else - CO₂, CH₄, N₂O, SF₆ - is an individual gas in kg and is fully restatable.

## Data requirements

The EXIOBASE stressor list with species names and units; $S$, $L$, $y_H$; the four IPCC
assessment factor sets.

## Deviations from the source, stated

- The DESIRE workbook's climate row is **not used**. This is a deliberate departure from
  the inherited pipeline and is the reason the study's climate figures differ from the
  submitted manuscript's beyond the vintage and shipping changes.
- The fossil/non-fossil methane split relies on EXIOBASE's industry naming, which is a
  proxy for the physical distinction. The marker list is explicit in `constants.py` so the
  assignment can be audited and changed.

## Outputs

| File | Content |
|---|---|
| `gwp_vintage_sensitivity.csv` | health-care and national footprints under four vintages, with the non-restatable share |
| `gwp_by_species.csv` | mass, AR6 factor and CO₂e contribution per species |

## Verification

`gwp_by_species.csv` sums to the reported climate footprint, so the restatement is
auditable species by species rather than only in aggregate.
