# Reading guide for the revision (NXSUST-D-26-01589)

Written for every author, with no input-output background assumed. It says what the revision
did, why each change is justified, and where the evidence sits. Jargon is explained the first
time it is used.

## The revision in one paragraph

The paper estimates the environmental footprint of Danish health care by feeding what Denmark
spends on health care into a model of the world economy (EXIOBASE), which traces that spending
through global supply chains to the emissions, materials, water, land and waste behind it.
The revision moved the estimate from 2019 spending on a 2016 model to 2022 spending on the
2022 model, replaced every number the submission had scaled from the Dutch study with Danish
data, corrected two defects of the model's Danish tables that Statistics Denmark's own tables
expose, quantified the uncertainty, and had every number, citation and equation checked against
its source. The climate headline moved from 4,815 to 4,267 kt CO₂e, and we can now say where
every part of it comes from.

## If you read only two things

1. The letter in the shared folder (`eriksen_et_al_2026_response_to_coauthor_review.docx`): every
   one of your comments, what changed, the corrections we found ourselves, and the decisions taken.
2. The one-page summary:
   [`revision/defects_and_fixes.md`, "E. What Ofir should know in one page"](revision/defects_and_fixes.md#e-what-ofir-should-know-in-one-page).

## The three findings that changed the paper, in plain words

1. **The big transport share was an error in the database, not a finding.** EXIOBASE records 74%
   of Danish shipping as if Danish companies used it, because Danish-flagged ships sell their
   services almost entirely abroad but the database books the sales at home. Statistics Denmark's
   own table says 6.5%, and Statistics Denmark has published on exactly this defect (Rørmose
   Jensen and Iliev 2022). We corrected it the way their publication implies, and the correction
   is why transport drops from the submission's 39% to 13.3% of the climate footprint, and the
   total by a quarter. Without this correction, every number in the paper would carry someone
   else's shipping.
2. **The model's release matters as much as its name.** We tested every EXIOBASE release on disk
   against Statistics Denmark's own tables, year by year. The newest release (v3.10.2) records
   the Danish health industry at about a third of its real size in 2022, which cannot carry
   Denmark's health spending; v3.8.2 agrees with the national accounts within 3% for 2016 and
   2022. That is why the paper uses v3.8.2, names it everywhere, and says that its 2022 table is
   a projection made in 2021. The evidence is in
   [`methods/exiobase_release_and_classification.md`](methods/exiobase_release_and_classification.md).
3. **Medicines are the least certain part, and we can now prove why.** The services part of our
   estimate uses EXIOBASE's recipe for what the Danish health industry buys, and that recipe
   contains almost no medicines (0.035% of purchases), whereas Statistics Denmark says medicines
   are 13.9% of what Danish hospitals and care buy. We computed the same recipe for seven
   countries: the Dutch one carries 11.4% medicines, the German 16.3%, the British 8.5%. So the
   gap is a defect of EXIOBASE's Danish recipe, not of the method, and the Dutch study's headline
   includes hospital medicines where ours cannot. We keep the headline on the published recipe
   because no published study alters one column inside a balanced global table, and the correction's
   size turns on the intensity of medicines: at the chemicals intensity it would put 78% of our blue
   water on pharmaceuticals (the Dutch results carry 42.9%), and at a pharmaceutical intensity it
   reverses sign, bounding the climate footprint between 3,933 and 5,635 kt. The evidence tables are
   `health_column_composition_by_country.csv` and `recipe_sensitivity_2022.csv` under
   `data/gold/results/06_benchmarks_validation/`.

## How sure can we be of the results?

- **The headline reproduces from raw data.** One command rebuilds everything from the EXIOBASE
  files and Statistics Denmark's tables and ends in an audit of 21 checks (totals, identities,
  double counting, every variant reproducing its own headline). It passes, and re-renders of the
  figures reproduce byte for byte.
- **Uncertainty is quantified, not asserted.** Every input carries a spread and 100,000 draws
  give the 95% interval (3,675 to 5,029 kt for climate). Most of the spread (69.6%) comes from
  the world-economy data, not from the Danish inputs, so better Danish data would narrow it only
  modestly. The plain-language account is in [`revision/uncertainty.md`](revision/uncertainty.md).
- **Choices are separated from noise.** Everything that is a decision rather than a measurement
  (how medicines are represented, the boundary, capital, the shipping share, the warming
  potentials) is rerun as its own case; Appendix A, Table A.7 lists all 14 with their results.
- **The scope split is verified.** Scope 1 (the sector's own emissions) plus Scope 2 (making the
  energy it buys) plus Scope 3 (everything upstream) plus patient and visitor travel add up to
  the total exactly, in every category, with the double-counting checks published; the method
  was audited against Hertwich and Wood (2018) and Cabernard and colleagues (2019), which the
  paper cites.
- **Citations were checked against the sources.** All 51 manuscript references and 36 appendix
  references were read against the claims that cite them, and every DOI was opened; the two
  links that would not open (medstat.dk and the Hagenaars thesis record) are named in
  [`eriksen_et_al_2026/readme.md`](eriksen_et_al_2026/readme.md) as to re-check before submission.

## Cite the background like this

Put this in the methods, verbatim. Each part of it has been got wrong in a draft.

> Environmental extensions and the global supply-chain structure were taken from
> **EXIOBASE version 3.8.2**, industry-by-industry monetary tables
> (`IOT_2022_ixi`, 49 regions x 163 industries), reference year **2022**, in
> basic prices, million euro. The Danish demand vector is Danish 2022
> expenditure, so demand year and model year coincide.

The version matters (releases disagree by a factor of 2.7 on the Danish health industry), the
table type matters (`ixi` and `pxp` have 163 and 200 sectors and are not interchangeable), and
the 2022 table is a projection compiled in September 2021, which the limitations say.

## Where to find anything

| You want | Go to |
|:---|:---|
| The point-by-point reviewer response | `docs/revision/response_to_reviewers.md` |
| The letter answering your review, point by point | `docs/eriksen_et_al_2026/r02_submission/v2/` |
| How to cite the background, and its limitations | `docs/methods/exiobase_release_and_classification.md` |
| What changed since submission, and why | `docs/revision/results_2022.md` |
| Method and equations, per analysis layer | `docs/methods/replications.md` |
| What each results folder contains | a `readme.md` and `data_dictionary.md` in every `data/gold/results/**/` folder |
| Findings against our own submitted results | `docs/revision/defects_and_fixes.md` |
| Where any published number comes from | `data/gold/results/manifest_lineage.csv`, one row per file with its script, inputs and method |

## What data we replaced, and why

The submitted paper and the revision use the same model (Steenmeijer and colleagues' code,
adapted to Denmark). What changed is the data fed into it. Each row says what the submitted
version used, what the revision uses, why the new data are better, and what we have to assume
for it to hold. The submitted climate footprint was 4,815 kt CO₂e; the revised one is 4,267 kt.

| What | Submitted | Revised | Why the new data are better | What we assume |
|:---|:---|:---|:---|:---|
| Year and background model | 2019 spending on the 2016 EXIOBASE table, not deflated (cited as version 3.7, run on 3.8.2) | 2022 spending on the 2022 table of EXIOBASE 3.8.2 | Spending and model refer to the same year, so no price adjustment is needed; the 2019 table puts the Danish health industry at 48 % of its national-accounts size | The 2022 table, a projection made in September 2021, describes 2022 supply chains well enough; its Danish health block agrees with the national accounts within 3 % |
| Health care spending | Government spending on elder care (DKK 68.4 bn) and NPISH hospital spending (DKK 2.3 bn) left out | Every household, NPISH and government column for the health and elder care purposes in Statistics Denmark's 2022 input-output table | Covers the sector the paper defines; about 90 % of elder care was missing | Health care is the System of Health Accounts boundary widened to social care; childcare stays out (tested in Table A.6) |
| Price basis of medicines and appliances | The whole purchase charged at the manufacturing intensity | The wholesale and retail margins in the purchase (40.5 % and 54.4 % of it) charged to the Danish trade industries | Statistics Denmark records the margins as trade services; charging them as manufacturing added 11.4 % | The margins carry the emissions of Danish trade, not of making the product |
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
| Uncertainty | Not quantified | Monte Carlo analysis (100,000 draws) and 14 sensitivity cases (Appendix A, Table A.7) | Shows how far each input and each modelling choice moves the result | The spreads of the bottom-up terms are judgements; the input-output spread is the 8.35 % that Lenzen and colleagues report for the Danish carbon footprint, applied to all five categories |
| Capital | Left out and not estimated | Still left out of the headline, but its size is estimated (12.5 % to 19.0 % of the climate footprint) | Readers can compare with studies that include investment | The 2020 capital matrices apply to 2022 output |

## Scope 1, 2 and 3, in plain words

Scope 1 is what the health sector burns and releases itself; Scope 2 is the making of the
electricity and heat it buys; Scope 3 is everything else upstream; and patient and visitor
travel is reported beside them because the reporting standard leaves it out. The four parts add
up to the total exactly, in every category, and the tables behind every cut (by scope, by
producing country, by industry, and their combinations) are in
`data/gold/results/02_scopes_wood_hertwich/<year>_<correction state>/`, scoped by year and by
correction state so a figure cannot pick up the wrong run's bars. One finding worth a sentence:
the 25 largest origin-industry pairs carry only 44% of the footprint, so no single supplier
dominates Danish health care's impacts.

## Conventions in the data

Tables put naming columns first, then the measure and its unit. Countries are ISO3 codes
(`ROU`, not the deprecated `ROM`); EXIOBASE regions with no country code carry their region
name (`RoW Europe` and so on). The world-region grouping singles out Denmark, as the Dutch
original singled out the Netherlands.

## Reproducing

```bash
export PYTHONPATH=src HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship
python -m analysis.main_2025
python -m analysis.audit_consistency   # 21 checks, non-zero exit on failure
LANG=en_US.UTF-8 Rscript r/plot_scope_emissions.r
```

## What is deliberately not on this branch

* **`data/bronze/`**: raw third-party inputs (EXIOBASE, the capital matrices, the medicine
  register extracts, StatBank downloads), obtained under each provider's terms and not ours to
  redistribute. Every source, its licence and how to fetch it is in
  [`methods/methods.md`](methods/methods.md).
* **`docs/references/`**: PDFs of published articles; `docs/source_material_locations.md` maps
  where they live.
* **Referee reports**: confidential for a manuscript under review. Our response reproduces the
  replies in full and the headings state each point; the reviewers' text stays in the
  submission system.
* **Two analysis layers** (IMPACT World+ characterisation and the SHA sub-sector decomposition)
  that go beyond what the reviewers asked and belong to follow-on work; the audit skips them by
  design rather than reporting them missing.
