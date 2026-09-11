# Branch notes - revision materials for NXSUST-D-26-01589

Everything needed to answer both reviewers. Start with
[`docs/revision/response_to_reviewers.md`](revision/response_to_reviewers.md).

## Cite the background like this

Put this in the methods, verbatim. Each part of it has been got wrong in a draft.

> Environmental extensions and the global supply-chain structure were taken from
> **EXIOBASE version 3.8.2**, industry-by-industry monetary tables
> (`IOT_2022_ixi`, 49 regions x 163 industries), reference year **2022**, in
> basic prices, million euro. The Danish demand vector is Danish 2022
> expenditure, so demand year and model year coincide.

`3.8.2` and not "EXIOBASE 3": v3.10.2 and v3.8.2 disagree by a factor of 2.7 on
the size of the Danish health industry -- 16,326 against 43,955 M.EUR of output
in 2022, where the national accounts give 45,321
(`09_exiobase_release_diagnostics/dk_block_vs_national_accounts.csv`) -- and this
study rejects v3.10.2 for that reason, so the release is not a detail a reader
can fill in. `ixi` and not `pxp`:
those have 163 and 200 sectors and their results are not interchangeable. And the
2022 tables are themselves a nowcast, compiled in September 2021, which the
limitations must say. The full argument, the measured size of the projection
error, and draft wording for the limitations paragraph are in
[`docs/methods/exiobase_release_and_classification.md`](methods/exiobase_release_and_classification.md).

| You want | Go to |
|:---|:---|
| The point-by-point reviewer response | `docs/revision/response_to_reviewers.md` |
| How to cite the background, and its limitations | `docs/methods/exiobase_release_and_classification.md` |
| What changed since submission, and why | `docs/revision/results_2022.md` |
| Method and equations, per analysis layer | `docs/methods/replications.md` |
| What each results folder contains | a `readme.md` (and generated `data_dictionary.md`) in every `data/gold/results/**/` that holds a table |
| Findings against our own submitted results | `docs/revision/defects_and_fixes.md` |
| Provenance of every file | `data/gold/results/manifest_lineage.csv` |

## The three things that change the paper

1. **The transport finding must be withdrawn.** EXIOBASE routes 73.6 % of Danish
   sea-transport output to Danish intermediate use; the national accounts say 9 %.
   Statistics Denmark published this defect (Rørmose Jensen & Iliev 2022) and EXIOBASE's
   own hybrid build gives 7.8 % natively, so the correction reconstructs an allocation
   official Danish practice already applies rather than proposing a new method.
   Transport falls from 37.5 % to **17.8 %** of the supply-chain footprint.
   See [`docs/methods/replications.md`, section 10](methods/replications.md#r10)
   and [`docs/revision/results_2022.md`, "The withdrawn transport finding"](revision/results_2022.md#the-withdrawn-transport-finding).

2. **The background model changed, and the v3.10.2 defects are datable.** Every release on
   disk was tested against Statistics Denmark's own table, year by year. Two distinct
   defects, with different onsets:

   | Defect | What breaks | Onset | v3.8.2 / v3.6 |
   |---|---|---|---|
   | **D1** | medical, precision and optical instruments carry ~zero output across Europe (28 of 30 regions) | **2015**, and never recovers | clean (0 of 30) |
   | **D2** | Danish output redistributed; 9 of 12 concordance groups off by more than 2x | **2021-2022**, the nowcast years | clean (2 of 12) |

   D2 in 2022 gives the Danish health industry 16,326 M€ of total output against
   45,321 M€ in the national accounts - which cannot deliver 40,597 M€ of health final
   demand. That is an arithmetic impossibility, not a tolerance question. Danish output
   still totals to within 3 % and the table still balances to 10⁻¹¹, so a total-level
   check misses both. The consequence is not only ours: anyone running a European study on
   v3.10.2 from 2015 onward inherits D1 with no warning.
   See [`docs/methods/replications.md`, section 09](methods/replications.md#r09).

3. **Climate is on IPCC AR6**, not the workbook's AR4 factors, with a four-revision
   sensitivity and the non-restatable share (HFC/PFC, pre-aggregated by EXIOBASE) reported.
   See [`docs/methods/replications.md`, section 15](methods/replications.md#r15).

## Scope 1-3 emissions, by origin and by industry

Six figure-ready tables per model run in
`data/gold/results/02_scopes_wood_hertwich/<year>_<correction state>/`
(`scope_by_*`) at three resolutions - full detail (scope × producing country ×
producing industry), the top 25 origin-industry pairs with the remainder pooled,
and aggregations by industry group, by continent and the cross. The layer is
scoped by reference year AND by whether the Danish sea-transport reallocation
was applied, exactly as `01_eriksen_replication` is, so a figure cannot take the
wrong correction state's bars. `r/plot_scope_emissions.r` renders four TIFFs
from them, each naming the run it was drawn from.

Scope 1 and the bottom-up items have no producing node in the model; they are placed at
their true Danish origin rather than dropped, so the bars add back to the headline.

A finding worth a sentence in the paper: the 25 largest origin-industry pairs account for
**44 %** of the footprint, and the pooled remainder is the single largest bar. The Danish
health footprint is diffuse - no supplier dominates it.

## Conventions in the data

Star schema throughout: dimension columns, then measure and unit. EXIOBASE industry and
product codes carry **no** `A_` / `C_` prefix. Countries are ISO3 (`ROU`, not the
deprecated `ROM`); EXIOBASE regions with no ISO3 code carry their region name
(`RoW Europe`, …). The world-region aggregation singles out **Denmark** - the Dutch
original singled out the Netherlands, which in a Danish study split NL out of Europe in
every regional chart.

## Reproducing

```bash
export PYTHONPATH=src HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship
python -m analysis.main_2025
python -m analysis.audit_consistency   # every check the module defines (C1-C10, C14-C18), non-zero exit on failure
LANG=en_US.UTF-8 Rscript r/plot_scope_emissions.r
```

## What is deliberately not on this branch

* **`data/bronze/`** - raw third-party inputs (EXIOBASE, the Södersten capital matrices,
  Danish Medstat ATC files, StatBank extracts), obtained under each provider's own terms
  and not ours to redistribute from a public repository. Every source, its licence and its
  access route is in
  [`docs/methods/methods.md`, "Which external models and datasets we actually use, and why"](methods/methods.md#which-external-models-and-datasets-we-actually-use-and-why).
* **`docs/references/`** - PDFs of published articles. See
  `docs/source_material_locations.md` for what lives there.
* **Referee comments.** The response document reproduces our replies in full but withholds
  the referee text: reports for a manuscript under review are confidential. The headings
  state each point addressed; the full text is in the submission system.
* **Two analysis layers** (IMPACT World+ characterisation, SHA health sub-sector
  decomposition) that go beyond what the reviewers asked and belong to follow-on work. The
  audit skips them cleanly rather than reporting them missing.
