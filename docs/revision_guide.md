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

1. **The transport finding must be corrected.** EXIOBASE routes 73.6 % of Danish
   sea-transport output to Danish intermediate use; the national accounts say 9 %.
   Statistics Denmark published this defect (Rørmose Jensen & Iliev 2022) and EXIOBASE's
   own hybrid build gives 7.8 % natively, so the correction reconstructs an allocation
   official Danish practice already applies rather than proposing a new method.
   In 2022 transport decreases from 34.1 % to **15.6 %** of the climate footprint by producing
   sector, and transport services from 29.7 % to **13.3 %** by purchase, so pharmaceuticals and
   chemical products (27.1 %) become the largest contributor.
   See [`docs/methods/replications.md`, section 10](methods/replications.md#r10)
   and [`docs/revision/results_2022.md`, "The corrected transport share"](revision/results_2022.md#the-corrected-transport-share).

2. **The background model changed, and the v3.10.2 defects are datable.** Every release on
   disk was tested against Statistics Denmark's own table, year by year. Two distinct
   defects, with different onsets:

   | Defect | What breaks | Onset | v3.8.2 / v3.6 |
   |:---|:---|:---|:---|
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

## What data we replaced, and why

The submitted paper and the revision use the same model (Steenmeijer and colleagues' code,
adapted to Denmark). What changed is the data fed into it. Each row says what the submitted
version used, what the revision uses, why the new data are better, and what we have to assume
for it to hold. The submitted climate footprint was 4,815 kt CO₂e; the revised one is 4,267 kt.

| What | Submitted | Revised | Why the new data are better | What we assume |
|:---|:---|:---|:---|:---|
| Year and background model | 2019 spending on the 2016 EXIOBASE table, not deflated (cited as version 3.7, run on 3.8.2) | 2022 spending on the 2022 table of EXIOBASE 3.8.2 | Spending and model refer to the same year, so no price adjustment is needed; the 2019 table puts the Danish health industry at 48 % of its national-accounts size | The 2022 table, a projection made in September 2021, describes 2022 supply chains well enough; its Danish health block agrees with the national accounts within 3 % |
| Health care spending | Government spending on elder care (DKK 68.4 bn) and NPISH hospital spending (DKK 2.3 bn) left out | Every household, NPISH and government column for the health and elder care purposes in Statistics Denmark's 2022 input-output table | Covers the sector the paper defines; about 90 % of elder care was missing | Health care is the System of Health Accounts boundary widened to social care; childcare stays out (tested in Table A.6) |
| Price basis of medicines and appliances | The whole purchase charged at the manufacturing intensity | The wholesale and retail margins in the purchase (40.5 % and 54.4 % of it) charged to the Danish trade industries | Statistics Denmark records the margins as trade services; charging them as manufacturing added 11.5 % | The margins carry the emissions of Danish trade, not of making the product |
| Exchange rate | A flat 7.45 DKK per euro | The annual average for the year, 7.4396 for 2022 | The rate of the year the spending refers to | None (the change is 0.2 %) |
| Danish sea transport | EXIOBASE's allocation: 74 % of Danish shipping output used by Danish industries | 6.5 %, the share in Statistics Denmark's own table | Danish ships sell mostly abroad; the old share put international shipping emissions on Danish purchases, and correcting it decreased the climate footprint by 25 % | The national table's share applies to the EXIOBASE row; every industry's total output is kept unchanged |
| The sector's own emissions | 1.4 kt CO₂e, read from inside the model (an artefact) | 119.5 kt from Statistics Denmark's emission accounts (DRIVHUS), with medical nitrous oxide taken out | The model cannot see the fuel and gases the sector itself burns and releases; the national accounts measure them | The elder care share of social work (0.31) applies to emissions as it does to spending |
| The sector's own waste | Taken from the model | 42.8 kt from Statistics Denmark's waste accounts (AFFALD01) | Measured rather than modelled | Same boundary and share as the emissions |
| What counts as waste | All 19 fractions of the EXIOBASE waste account, including manure, sewage and mining residues | Only the fractions that EU and Danish statistics count as waste | Comparable with Danish waste statistics; most of the old 829 kt was not waste | None |
| Anaesthetic gases | 9.51 kt: the Dutch value scaled by births | 11.75 kt: nitrous oxide from Denmark's emission inventory (38 t a year) and volatile agents from national sales | Danish data in place of a Dutch proxy | All medical nitrous oxide is health care (an upper bound, since dental and veterinary use cannot be separated); all agent sold is released except 5 % of sevoflurane |
| Inhaler propellants | 34.61 kt: the Dutch value scaled, mixing 20-year and 100-year warming potentials | 12.55 kt from the Danish EPA's F-gas inventory, on AR6 values | Danish data on one consistent time horizon | The inventory's emission estimate holds (half released in the year of sale, half in the next) |
| Employee commuting | The Dutch value scaled by employment and hours | 444 kt: Danish travel-survey distances, allocated by health care's share of hours worked | Danish distances; it also removes a Dutch base that counted one trip a day | Health staff travel as far per hour worked as the average worker, and the Dutch emissions per kilometre hold in Denmark |
| Patient and visitor travel | The Dutch value scaled by employment ratios | 264 kt: the travel survey's trips for health and social purposes, with visitors added at the English ratio | Danish distances | Those trips are patient travel (an upper bound), and visitors relate to patients as in England |
| Climate weights | AR4 values for the input-output part | AR6 for the input-output part and the gases | The current IPCC values | The sector's own emissions keep the AR5 values of the national accounts, and travel keeps the Dutch inventory's values |
| Uncertainty | Not quantified | Monte Carlo analysis (100,000 draws) and 14 sensitivity cases (Appendix A, Table A.6) | Shows how far each input and each modelling choice moves the result | The spreads of the bottom-up terms are judgements; the input-output spread is the 8.35 % that Lenzen and colleagues report for the Danish carbon footprint, applied to all five categories |
| Capital | Left out and not estimated | Still left out of the headline, but its size is estimated (12.5 % to 19.0 % of the climate footprint) | Readers can compare with studies that include investment | The 2020 capital matrices apply to 2022 output |

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
python -m analysis.audit_consistency   # every check the module defines (C1, C2, C4-C10, C14-C21), non-zero exit on failure
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
