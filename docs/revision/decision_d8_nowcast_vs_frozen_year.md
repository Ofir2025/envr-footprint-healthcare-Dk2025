# Decision D8: 2022 nowcast, or freeze at the last real emission year?

**Status: open. This choice is the author's call.** The analysis supports either, and
the code supports both.

## The choice

| | Option A (as implemented) | Option B (Statistics Denmark's practice) |
|---|---|---|
| Model year | EXIOBASE 2022 | EXIOBASE **2019**, the last year backed by real emission data |
| Demand vector | Danish 2022 expenditure | Danish 2022 expenditure **deflated to 2019 prices** |
| Economic block | validated against Danish 2022 national accounts, passes | validated against 2019 |
| Emission accounts | **extrapolated**: CO₂ ends 2019, other GHGs end 2017 | real |
| Answers R2-4 / R2-10 | **yes**: expenditure year and model year coincide | no: reintroduces the mismatch the reviewers objected to |

## The case for A (current)

Reviewer 2 objected specifically to *"2019 expenditure applied to a 2016
structure without deflation"* and asked us to explain the vintage mismatch.
Option A dissolves that objection: no mismatch and no deflation step remain.
The Danish **economic** block of EXIOBASE v3.8.2 2022 was tested against
Statistics Denmark's published 117-industry table and passes on every checkable
industry group (health 0.97, education 0.88, financial 1.11, real estate 0.97).

### A qualification the case for A has to carry

The v3.8.2 2022 table is **itself a projection**. Its own `metadata.json`
records the file as written on 8 September 2021, so a 2022 table produced in
2021 is a nowcast, not an observation. This study rejected v3.10.2 partly
because its 2022 nowcast fails against the Danish national accounts; the
background it kept has a 2022 nowcast too, with a different and milder failure
profile rather than none.

Measured on the full 163-to-117 concordance rather than on the twelve
unambiguous groups the vintage audit uses, Danish total output in the model is
**1.01 times the national-accounts total in 2016 and 0.80 in 2022**. Twenty per
cent of the Danish economy is missing from the 2022 projection, and where it is
missing is the useful part:

| group | model | national accounts | ratio |
|---|---|---|---|
| Sea and coastal water transport | 19,714 | 78,950 | 0.25 |
| Chemicals and pharmaceuticals | 5,915 | 35,742 | 0.17 |
| Wholesale trade | 28,962 | 53,501 | 0.54 |
| Electricity | 2,540 | 10,789 | 0.24 |
| **Health and social work** | **43,955** | **45,854** | **0.96** |

None of the four largest gaps is new to this study and none is unaddressed.
The shipping row is the one this study reallocates, and the reallocation is
calibrated to the national accounts rather than to the model. The
pharmaceutical gap is the proxy problem the paper already reports as its
largest single limitation. Wholesale and electricity are a 2021 projection
failing to see 2022 prices, and neither carries much of the health-care supply
chain. **The industry the study models is at 0.96**, which is why the vintage
audit passes on the groups it tests.

The qualification stands even so, and belongs in the limitations: the choice is
between two nowcasts, not between a nowcast and an observation.

## The case for B (Statistics Denmark's)

Rørmose Jensen & Iliev freeze EXIOBASE at 2019 and deflate demand back to 2019
prices for their 2019, 2020, and 2021 footprints. Their stated reason is that the
nowcast years are internally out of sync: a flat nowcast keeps the satellite and
characterisation flat while current-price imports inflate, so **inflation
mechanically inflates the footprint**. 2022 was a high-inflation year in
Denmark, which makes this concern live rather than theoretical.

Our emission side has no validation equivalent to the economic side's. EXIOBASE
v3.8.2 was built in September 2021; its CO₂ accounts end in 2019 and its other
greenhouse gases in 2017. We are extrapolating up to five years on the side that
carries the physics.

## What the difference would be

The difference is not yet computed. It is a bounded piece of work: build the 2019
background, deflate the 2022 Danish expenditure vector to 2019 prices with the
Danish national-accounts deflators, and rerun. The environment already supports it
(`HC_BACKGROUND_YEAR=2019`), so the marginal cost is the background build plus
one analysis pass.

## Recommendation

**Keep A as the headline and add B as a reported sensitivity.** That satisfies
Reviewer 2's original objection, matches Denmark's own statistical office on the
axis they care about, and turns a methodological disagreement into a quantified
range rather than a defended position. If the two agree closely, the concern is
retired; if they diverge, that divergence is itself a finding worth reporting,
and it would bear directly on how much weight the 2022 headline can carry.

**What would change the recommendation:** if the deflation step proves
ill-conditioned (Danish 2022 inflation was concentrated in energy, so a
uniform deflator would misstate the health-care basket), then B becomes a weaker
comparator and should be reported with that caveat rather than as an equal
alternative.
