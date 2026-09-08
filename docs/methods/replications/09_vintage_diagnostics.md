# 09 - EXIOBASE vintage defects

**Gold folder** `data/gold/results/09_vintage_diagnostics/`
**Module** `analysis.vintage_defect_audit`
**Source** Rørmose Jensen & Iliev (2022), Statistics Denmark; Statistics Denmark's
published 117-industry input-output table

## Question this layer answers

Which EXIOBASE vintage can carry this study? Rørmose Jensen & Iliev argue EXIOBASE's
Danish block misallocates output between industries. This module turns that argument into
a reproducible test rather than accepting or dismissing it.

## Method

Every EXIOBASE vintage on disk is compared, industry group by industry group, against
Statistics Denmark's own IO table for the same year:

$$r_i = \frac{x_i^{\text{EXIOBASE}}}{x_i^{\text{national accounts}}}$$

Two defects are detected and, importantly, kept separate; they have different scopes
and different implications.

### D1: version-wide, v3.10.2

Industry 33 (*medical, precision and optical instruments*) carries approximately **zero
output in every European region, in both the 2016 and 2022 tables**. In v3.8.2 the same
industry is normal.

Danish medical-appliance expenditure is 1,094 M€. A zero domestic and zero European
supply forces that demand onto whichever regions retain a non-zero industry 33, which is
not a modelling result but an artefact of the defect.

### D2: year-specific, v3.10.2 2022 nowcast

Output is redistributed between Danish industries:

| Danish industry, 2022 | National accounts | v3.10.2 | v3.8.2 |
|---|---|---|---|
| Health and social work | 45,321 M€ | 16,326 (0.36×) | 43,955 (0.97×) |
| Education | 22,935 M€ | 109,673 (4.78×) | 20,241 (0.88×) |
| Financial intermediation | 18,980 M€ | 76 | 21,004 (1.11×) |
| Machinery n.e.c. | 21,150 M€ | 28 | 18,700 (0.88×) |
| Medical instruments | 9,130 M€ | 0 | 6,276 (0.69×) |

Total Danish output is right to 3 % and the table balances to 10⁻¹¹, so output was
**redistributed, not lost**, which is why a total-level check would miss it.

The decisive test is internal to our own data and needs no external source: Danish health
final expenditure is 40,597 M€, so a health industry with 16,326 M€ of *total output*
cannot deliver it. That mismatch is an arithmetic impossibility, not a discrepancy.

The defect also affects BG, MT, and CH, and is confined to the nowcast years, so it is
invisible to anyone validating on Germany or France.

## Data requirements

| Input | Source |
|---|---|
| EXIOBASE v3.8.2, v3.10.2, hybrid v3.3.18 | Zenodo 5589597, 20051562, 10148587 |
| Danish IO table, 117 industries | Statistics Denmark, 2016 and 2022 |
| NACE ↔ EXIOBASE industry concordance | carried in the output's `dst_nace_prefixes` column |

## Deviations from the source, stated

Rørmose Jensen & Iliev diagnose the Danish block and conclude that a national-accounts
coupling (SNAC, after Palm et al. 2019) is required. We reproduce their diagnosis but do
**not** implement full SNAC; that implementation is a larger piece of work, scoped in
`docs/revision/dk_snac_feasibility.md` and listed as an open item. What we do implement is
the single reallocation their diagnosis most directly implies
([10](10_snac_shipping_correction.md)).

## Outcome

**v3.8.2 is adopted; v3.10.2 is rejected for this study.** The rejection is evidenced by
this folder rather than asserted, which matters because v3.10.2 is the newest release and a
reviewer will reasonably ask why it was not used.

## Outputs

This layer writes `dk_block_vs_national_accounts.csv` (per industry, per vintage, with
ratios), `industry33_output_by_region.csv` (D1 across all regions), and
`vintage_defect_verdicts.csv` (one verdict row per defect per vintage).
