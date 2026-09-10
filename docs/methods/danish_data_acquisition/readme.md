# Danish data acquisition

This folder is the record of the pre-modelling question: where does the data for a
Danish healthcare environmental-footprint study actually come from, what is
genuinely public, what needs a formal request, and how good is each source once
obtained.

It merges two earlier, separately dated assessments that answered overlapping
parts of this question - a first inventory and, once several of its findings
needed sharper qualification, a follow-up deep dive that revised the cross-MRIO
strategy, the Statistics Denmark contact plan and the source register, and added
three topics the first pass had not covered at all (product classification, gap
independence, and dedicated waste and FIGARO feasibility studies). Merging them
into one sequence removes the duplication between the two while keeping every
finding that either one reached alone; the keep/supersede decision for each
source document is recorded in the commit that created this folder.

## What each document answers

| # | Document | Question it answers |
|---|---|---|
| 01 | `01_denmark_data_access_inventory.md` | For every dataset a Danish replication of Malik, Eckelman or Lenzen needs (economic core, health expenditure, GHG, air pollution, water, waste, materials, pharmaceuticals, travel, clinical procurement), where is it, and is it open, controlled or request-only? |
| 02 | `02_danish_product_classification_and_health_filter.md` | The exact ~2,350-product Danish national-accounts classification is not public - so what can be built from public CN/HS/CPA classifications in the meantime, and how should "a healthcare product" be defined without conflating it with "a healthcare industry"? |
| 03 | `03_data_gap_resolution_matrix.md` | Of the items flagged as data gaps in the inventory, which are genuine absences and which are really access, harmonisation or independence problems - and what evidence quality does each source clear? |
| 04 | `04_cross_mrio_replication_strategy.md` | Which external MRIO databases (EXIOBASE, GLORIA, Eora, OECD ICIO, FIGARO) should be run for sensitivity, what role does each play, and how is a cross-MRIO comparison harmonised so that database differences are not confused with healthcare-boundary differences? |
| 05 | `05_waste_benchmarking_protocol.md` | How can Danish healthcare waste be triangulated across hospital, EPA, Statistics Denmark and Eurostat layers without mistaking three dependent reporting chains for three independent measurements? |
| 06 | `06_figaro_feasibility_and_test_plan.md` | Is FIGARO detailed enough to justify its own replication and sensitivity exercise, and if so, what is the concrete test sequence? |
| 07 | `07_statistics_denmark_contact_and_acquisition_plan.md` | Exactly what should be requested from Statistics Denmark, from whom, in what order, and what should proceed in the meantime while that request is outstanding? |
| 08 | `08_sut_request_brief.md` | The drafted one-page project brief referenced by document 07, ready to attach once the subject-matter contact confirms a route. |
| 09 | `09_data_acquisition_register.md` | Dataset-by-dataset tracking: provider, access class, years, target table and next action for every source named above. |
| 10 | `10_evidence_and_source_register.md` | Claim-by-claim verification: which specific statements about these sources are confirmed against an official citation, which are inference, and which are still open questions. |

Documents 09 and 10 answer different questions and are both kept in full: 09
tracks *datasets* toward acquisition, 10 tracks *claims* toward verification.

## What changed in the merge

- Documents 02, 03, 05, 06 and 10 came from the later deep dive and had no
  counterpart in the first pass; they carry over unchanged bar renumbering.
- Documents 01, 08 and 09 came from the first pass and had no counterpart in the
  deep dive; they also carry over unchanged bar renumbering and one corrected
  cross-reference (01 pointed at the old name of document 04).
- Document 04 is the deep dive's revised cross-MRIO strategy, with two sections
  the first pass had that the revision dropped - the quantitative MRIO
  comparison table and the `fact_mrio_comparison` result-table schema - carried
  forward as sections 16-18 rather than lost.
- Document 07 is the deep dive's revised Statistics Denmark contact plan, with
  the first pass's prepared answers to likely follow-up questions carried
  forward as section 13.
- The first pass's cross-MRIO strategy and SUT request guide, and both folders'
  own readmes, are superseded by the above and are not carried forward as
  separate files; their content is either merged above or was fully replaced by
  the deep dive's sharper version. Full text of anything not carried forward is
  in git history.
