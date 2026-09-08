# 13 - Steenmeijer replication

**Gold folder** `data/gold/results/13_steenmeijer_replication/`
**Module** `analysis.steenmeijer_replication`
**Source** Steenmeijer, Rodrigues, Zijp & Waaijers-van der Loop (2022), *The environmental
impact of the Dutch health-care sector beyond climate change*, Lancet Planet Health
6:e949-57

## Question this layer answers

This layer places Denmark beside every number the Dutch study published, in their own
table structure, for every impact category, not only climate. That completeness is what
FAIR replication means here.

Their published values are transcribed into the module as a documented constant with
provenance, so the comparison is reproducible without re-reading the paper.

## Method

### Their core construction, implemented exactly

The health services component is not footprinted from an expenditure vector but from the
health industry's own **input column**:

$$f_{\text{services}} = Z[:,h] \times \frac{E_H}{x_h}$$

where $x_h$ is the health industry's **total input**, intermediate use *plus* value
added, not intermediate use alone. On our model this holds exactly:

$$\textstyle\sum Z[:,h] + \sum V[:,h] = x_h \qquad (11{,}730.9 + 32{,}224.5 = 43{,}955.5\ \text{M€})$$

and since $A[:,h] = Z[:,h]/x_h$ by construction, our $A[:,h]\cdot E_H$ **is** their formula.

A consequence worth stating, because it looks wrong at first sight: the demand vector
entering the MRIO is much smaller than health expenditure: 13,067 M€ against
40,597 M€ (32.2 %). Steenmeijer's equivalent is 26,283 against 92,515 M€ (28.4 %). The
difference is value added, which has no upstream footprint.

### Whose final demand?

**All financing regimes, not households only.** Steenmeijer cover the whole health-care
sector's final demand. The one thing they exclude is the *household extension* (direct
household emissions), which we also exclude. This boundary was verified against the paper
rather than inferred, because the distinction changes the boundary substantially.

### Comparability warnings, carried in the output

Three differences make a naive side-by-side misleading. Each is a column in the output
tables, not a footnote:

| Difference | Netherlands | Denmark |
|---|---|---|
| **Boundary** | *zorg en welzijn*, includes childcare | health + eldercare, excludes childcare |
| **Year** | 2016 | 2022 |
| **Background** | EXIOBASE v3.3 | v3.8.2 with sea-transport reallocation |

The Danish run with the Dutch boundary (`HC_SCOPE=zorg_en_welzijn`) is available for the
matched comparison and is used in [06](06_benchmarks_validation.md).

### The comparison that matters

The decisive comparison is both countries' **health share of the national total**, which
is unit-free and is what their abstract leads with. Their headline finding, that material
extraction is a *larger* share of the national total than climate change (13 % against
7.3 %), reproduces in Denmark (7.9 % against 6.1 %). That reproduction is an independent
argument for the multi-indicator framing.

## Data requirements

This layer needs $Z$, $V$, $x$, $A$, $L$, $S$, and $C$; Danish health expenditure; and
the Dutch published values, transcribed with provenance.

## Deviations from the source, stated

- Their background is EXIOBASE v3.3 and ours v3.8.2; we do not rebuild on v3.3, so
  absolute levels carry a vintage component.
- Our climate figures are AR6, theirs are the workbook's AR4. Absolute climate values are
  therefore not directly comparable; shares are.

## Outputs

This layer writes `template_table_dk_vs_nl.csv` (their table structure, both countries,
per capita and absolute) and `national_shares_dk_vs_nl.csv` (health share of national by
indicator, with the comparability note per row).
