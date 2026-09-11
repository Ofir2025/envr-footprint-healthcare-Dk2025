# Gold results

Every table here is a deliverable at the most detailed level the model
supports (producing country x producing sector x purchased product x
demand component), so all aggregates are derivable and no lineage is
lost. Lineage for every file is in `manifest_lineage.csv`.

## Two scopes, one tree

This working copy holds every layer. The branch published for the
co-author holds the layers below marked **paper**. Nothing is
duplicated on disk: the classification lives in `analysis.gold_scope`,
the publish filter reads it, and the consistency audit fails if a
folder appears here without being classified. This file is generated:
edit `src/analysis/gold_scope.py`, never this text.

### Paper deliverables (21 folders)

Each backs a number, figure, or table in the manuscript or in the
response to the reviewers.

| folder | why it ships |
|:---|:---|
| `00_core_footprint` | the footprint itself; every headline number |
| `01_eriksen_replication` | the replication the manuscript is; figures 1-3 and S1 |
| `02_scopes_wood_hertwich` | the GHG-Protocol scope split; figures 3-6 |
| `03_cabernard_target_scope3` | the double-counting audit the reviewers' aggregation question turns on |
| `04_uncertainty_lenzen_ieooc` | the Monte Carlo answering the first reviewer |
| `05_waste_dst_accounts` | the Danish waste account that replaced the 2011 hybrid extension |
| `06_benchmarks_validation` | the boundary-matched comparison with Schmidt & Merciai; figure 7 |
| `07_malik_replication` | capital-boundary comparator; Malik et al. include capital where the other comparators exclude it |
| `08_lenzen_replication` | the comparator behind the uncertainty calibration and the national-total family comparison |
| `09_exiobase_release_diagnostics` | the **only** evidence for rejecting EXIOBASE v3.10.2, which the response states as fact |
| `10_sea_transport_reallocation` | the sea-transport reallocation, on which the withdrawn transport finding depends |
| `11_capital_gfcf` | the capital treatment; the second step of figure 7 |
| `12_impact_categories_full` | the full characterisation behind the five reported categories |
| `13_steenmeijer_replication` | the Dutch study this replicates |
| `14_eckelman_replication` | comparator in the same boundary table as 07 and 08 |
| `15_gwp_revision` | the AR6-versus-AR4 restatement the response leads on |
| `18_mitigation_scenarios` | the counterfactual scenarios; figures 8 and 9 |
| `19_tables_of_record` | the verified tables of record, regenerated from the gold facts, that supersede the values circulated during drafting |
| `20_production_layers` | how far upstream the pressure occurs; the production-layer decomposition reported for the revision |
| `scenarios` | the sector-boundary scenarios behind the childcare step of figure 7 |
| `star` | the star schema over the reported facts |

### Private extensions (2 folders)

Each is real analysis, kept in this repository only: follow-on work
that nothing in the current revision cites.

| folder | why it stays here |
|:---|:---|
| `16_impact_world_plus` | IMPACT World+ characterisation; a methods paper of its own, cited by nothing in this revision |
| `17_health_subsectors` | health sub-sector decomposition; the follow-on paper |

## Naming

Use lowercase `snake_case`, add the analysis year where a table is
year-specific, and keep out editor lock files and temporary
artefacts. A layer whose results differ by model run is stored under a
variant subdirectory named `<year><letter>`, where the letter fixes
all four axes that change the numbers - EXIOBASE release, Danish
sea-transport correction, care boundary, capital treatment - and is
resolved by `analysis.constants.variant_folder` in Python and
`variant_name()` in R, never re-derived. A run for one configuration
therefore cannot overwrite another's, and no reader has to infer which
release or correction a folder carries. A bare year could not say it:
while layer 02 used one, the scope figures of one variant were drawn
from another's tables.

### Variant folders on disk (26)

| folder | configuration |
|:---|:---|
| `01_eriksen_replication/2016_uncorrected` | EXIOBASE v3.8.2 IOT_2016_ixi, no Danish shipping correction, health-care boundary, capital excluded - the 2016 counterpart of 2019_uncorrected and 2022_uncorrected |
| `01_eriksen_replication/2016a` | EXIOBASE v3.7, no Danish shipping correction, health-care boundary, capital excluded - the submitted configuration |
| `01_eriksen_replication/2016b` | EXIOBASE v3.7, Danish shipping correction, health-care boundary, capital excluded |
| `01_eriksen_replication/2016c` | EXIOBASE v3.8.2, Danish shipping correction, health-care boundary, capital excluded - the headline configuration |
| `01_eriksen_replication/2016d` | EXIOBASE v3.8.2, Danish shipping correction, health care plus child and elder care, capital endogenised |
| `01_eriksen_replication/2019_uncorrected` | EXIOBASE v3.8.2 IOT_2016_ixi, no Danish shipping correction, health-care boundary, capital excluded - not variant a, which is on v3.7 |
| `01_eriksen_replication/2019a` | EXIOBASE v3.7, no Danish shipping correction, health-care boundary, capital excluded - the submitted configuration |
| `01_eriksen_replication/2019b` | EXIOBASE v3.7, Danish shipping correction, health-care boundary, capital excluded |
| `01_eriksen_replication/2019c` | EXIOBASE v3.8.2, Danish shipping correction, health-care boundary, capital excluded - the headline configuration |
| `01_eriksen_replication/2019d` | EXIOBASE v3.8.2, Danish shipping correction, health care plus child and elder care, capital endogenised |
| `01_eriksen_replication/2022_uncorrected` | EXIOBASE v3.8.2 IOT_2022_ixi, no Danish shipping correction, health-care boundary, capital excluded |
| `01_eriksen_replication/2022c` | EXIOBASE v3.8.2, Danish shipping correction, health-care boundary, capital excluded - the headline configuration |
| `01_eriksen_replication/2022d` | EXIOBASE v3.8.2, Danish shipping correction, health care plus child and elder care, capital endogenised |
| `02_scopes_wood_hertwich/2016_uncorrected` | EXIOBASE v3.8.2 IOT_2016_ixi, no Danish shipping correction, health-care boundary, capital excluded - the 2016 counterpart of 2019_uncorrected and 2022_uncorrected |
| `02_scopes_wood_hertwich/2016a` | EXIOBASE v3.7, no Danish shipping correction, health-care boundary, capital excluded - the submitted configuration |
| `02_scopes_wood_hertwich/2016b` | EXIOBASE v3.7, Danish shipping correction, health-care boundary, capital excluded |
| `02_scopes_wood_hertwich/2016c` | EXIOBASE v3.8.2, Danish shipping correction, health-care boundary, capital excluded - the headline configuration |
| `02_scopes_wood_hertwich/2016d` | EXIOBASE v3.8.2, Danish shipping correction, health care plus child and elder care, capital endogenised |
| `02_scopes_wood_hertwich/2019_uncorrected` | EXIOBASE v3.8.2 IOT_2016_ixi, no Danish shipping correction, health-care boundary, capital excluded - not variant a, which is on v3.7 |
| `02_scopes_wood_hertwich/2019a` | EXIOBASE v3.7, no Danish shipping correction, health-care boundary, capital excluded - the submitted configuration |
| `02_scopes_wood_hertwich/2019b` | EXIOBASE v3.7, Danish shipping correction, health-care boundary, capital excluded |
| `02_scopes_wood_hertwich/2019c` | EXIOBASE v3.8.2, Danish shipping correction, health-care boundary, capital excluded - the headline configuration |
| `02_scopes_wood_hertwich/2019d` | EXIOBASE v3.8.2, Danish shipping correction, health care plus child and elder care, capital endogenised |
| `02_scopes_wood_hertwich/2022_uncorrected` | EXIOBASE v3.8.2 IOT_2022_ixi, no Danish shipping correction, health-care boundary, capital excluded |
| `02_scopes_wood_hertwich/2022c` | EXIOBASE v3.8.2, Danish shipping correction, health-care boundary, capital excluded - the headline configuration |
| `02_scopes_wood_hertwich/2022d` | EXIOBASE v3.8.2, Danish shipping correction, health care plus child and elder care, capital endogenised |

Two configurations carry a self-describing name instead of a letter
rather than being given one they were not assigned; both are v3.8.2
without the shipping correction, and neither is variant a, which is on
v3.7.
