# Eriksen et al. (2026) submission package

Everything that goes to *Next Sustainability* for NXSUST-D-26-01589, and nothing
else. These are the working files as well as the deliverables: the manuscript and
appendix A carry the revision as tracked changes, so there is no separate working
copy to keep in step. The latest layer of tracked changes in both is dated 21 October
2026: Albert Kwame Osei-Owusu's answer to Ofir Eriksen's review, with the five edits of
Ofir's that were kept tracked under his own name. In both documents the EndNote field
codes have been removed and the reference list replaced by a static list, verified
entry by entry and numbered in order of first citation, with every DOI or URL
linked.

A duplicate `revision/` subfolder existed until 2026-09-12 and produced the failure
duplication invites: the response letter sat four days out of date. There is one
copy of each file, here.

## Where to start (co-authors)

| If you want to… | Open |
|:---|:---|
| Read or edit the revised paper | `eriksen_et_al_2026_manuscript.docx` (tracked changes); accept all changes in Word for a clean copy |
| See what changed on 14 September 2026 and why | [`../revision/defects_and_fixes.md`, "Findings of 14 September 2026"](../revision/defects_and_fixes.md#findings-of-14-september-2026) |
| Check a number in the paper | [`../../data/gold/results/19_tables_of_record/`](../../data/gold/results/19_tables_of_record/) and `../../data/gold/results/manifest_lineage.csv` |
| Read the reply to the reviewers | `eriksen_et_al_2026_reviewer_responses.docx` (formal letter); [`../revision/response_to_reviewers.md`](../revision/response_to_reviewers.md) (technical companion) |
| Rerun everything | `python scripts/run_pipeline.py` from the repository root; see [`../../readme.md`](../../readme.md), "Running it" |

## Files

| File | Purpose | Submit |
|:---|:---|:---|
| `eriksen_et_al_2026_manuscript.docx` | The manuscript, revision tracked. Three figures, two tables (Table 1, data sources and main assumptions, added 21 October 2026), 49 references. | yes, tracked and clean |
| `eriksen_et_al_2026_supplementary_appendix_a.docx` | Supplementary appendix A: derivations, validation, five tables, sixteen figures (each cited from the manuscript), 34 references. | yes, tracked and clean |
| `eriksen_et_al_2026_supplementary_appendix_b_travel_calculations.xlsx` | Supplementary appendix B: the travel calculations workbook, with README, commuting (Eqs. A.11 and A.12), patient and visitor travel (Eq. A.13), modal split and the superseded ratio scaling for comparison. Formulas carry cached values and reproduce the model output. | yes |
| `eriksen_et_al_2026_reviewer_responses.docx` | The full point-by-point response to the editor and reviewers, quoting every comment (24 pages). | keep as the full record |
| `eriksen_et_al_2026_reviewer_responses_concise.docx` | The concise response: every comment answered in one to four sentences, with the change and its location (about 5 pages). | yes |
| `eriksen_et_al_2026_cover_letter.docx` | The one-page cover letter to *Next Sustainability*, from Ofir Eriksen as lead author. | yes |
| `eriksen_et_al_2026_declaration_interests.docx` | The declaration of competing interests. | yes |
| `eriksen_et_al_2026_ethics_declaration.docx` | The ethics declaration. | yes |
| `guide_for_authors_next_sustainability.pdf` | The journal's guide for authors, for reference (Elsevier copyright). | no |

Figures, all in `figures/manuscript/2022c/`:

| Set | Files | Use |
|:---|:---|:---|
| Manuscript figures 1 to 3 | `fig1_ofir_panels_2022.tiff`, `fig2_top_origin_industry_pairs_2022.tiff`, `fig3_scopes_stacked_2022.tiff` | upload with the manuscript |
| Steenmeijer et al. (2022) figures 1 to 3, with the article's labels, on the 2022 results | `fig1_contribution_product_group_2022c.tiff`, `fig2_hotspot_sector_2022c.tiff`, `fig3_hotspot_geography_2022c.tiff` | for comparison with the Dutch study, or in place of the panelled figure 1 |
| Heat map: the 49 countries and regions of production by sector group, five impact categories, drawn at its printed width of 6.69 in | `figS2_origin_sector_heatmap_2022.tiff` | Appendix A, Fig. A.6 |

The July 2026 supplementary figures file was removed: its three charts duplicated
the submitted manuscript's figures.
Still outstanding before submission, and who holds each:

- **The new Zenodo version DOI** (appendix A, Data, code and software; manuscript,
  Data availability). Only Ofir's GitHub account can create the release.
- **The title page.** Ofir prepared one for the first submission, in Teams, which
  this repository cannot see. It must carry the revised title, which differs from
  the submitted one, the affiliations, the corresponding author's email and the
  author order proposed on 14 September 2026: Ofir Eriksen, Albert Kwame
  Osei-Owusu, Styrmir Gislason, Morten Birkved, Ciprian Cimpan. The guide for
  authors asks for given names in full, so the submitted title page's initials
  ("Osei-Owusu A", which also dropped Kwame) become full names.
- **The Authorship Change Request form** (Ofir, as corresponding author). The
  submitted order was Eriksen, Gislason, Osei-Owusu, Birkved, Cimpan; the proposal
  moves Albert Kwame Osei-Owusu from third to second. The guide for authors allows a
  rearrangement before acceptance only if the editor approves a request made on the
  journal's Authorship Change Request form, with the reason and written agreement
  from all five authors. The review may pause while it is considered, and a change
  made without the form can lead to rejection. The CRediT statement, the appendix A
  author line and both response letters already use the proposed order; if the
  change is not approved, restore the submitted order in all four.
- **The CRediT statement.** Drafted on 12 September 2026 from what the repository
  shows, not from notes by any author. It assigns roles to Ofir Eriksen and Albert
  Kwame Osei-Owusu only; Styrmir Gislason, Morten Birkved and Ciprian Cimpan read
  "[roles to be confirmed]" until they state theirs, and all five authors confirm
  the whole statement.
- **The Hagenaars thesis** (manuscript reference [47], appendix A reference [2]). Its title is
  given as "An investigation into the carbon and material footprint of the Dutch consumption of
  pharmaceuticals" (Delft and Leiden), whereas Steenmeijer et al. (2022) cite "The carbon and
  material footprint of the Dutch consumption of pharmaceuticals" (Leiden). Appendix A's figures
  from it (indirect footprint about 60 % lower for material extraction and 10 % lower for
  greenhouse gases on SNAC-EXIOBASE, Dutch health care, 2014) have not been checked against the
  thesis, because the TU Delft repository could not be reached on 21 and 22 October 2026. Read
  the thesis before submission.
- **Two links to re-check before submission**: medstat.dk (TLS error on 21 October 2026) and the
  TU Delft resolver above. Every other DOI and URL in both reference lists was opened and leads
  to the work cited.
- **Length.** The main text is about 7,100 words against the journal's guide of 3,000 to 6,000
  (counted on 22 October 2026, abstract 249 of 250 words).

The penicillin sentence (appendix A, System boundary) was verified on 21 October 2026 against
Olsen et al. (2026), Fig. 2, where the normalised results are dominated by human toxicity
(carcinogenic), freshwater ecotoxicity and marine ecotoxicity.

## Co-author review rounds

`r02_submission/` holds the versions the authors exchange within the revision round (r02), as in
the authors' other papers. `v1/` is Ofir Eriksen's review of 21 October 2026, his two annotated
files exactly as received; `v2/` is the answer, his copies with every reply and every change
tracked (`…_review_replies.docx`) and a letter answering him point by point. Each version's
`readme.md` lists every file in the folder shared with the co-authors, with its role and SHA-256.
Nothing in a version folder is edited by hand:

```bash
.venv/bin/python scripts/release/review_round/build_coauthor_letter.py
.venv/bin/python scripts/release/review_round/build_review_round.py --version v2 --shared <shared folder>
.venv/bin/python scripts/release/review_round/build_review_round.py --version v2 --check <shared folder>
```

The second command makes the clean copies with Word itself (every revision accepted), writes the
version's readme and refreshes the shared folder, moving any file it replaces to the Trash. The
folder is kept off the public branch by `scripts/release/publish_ofir_branch.sh`.

## What is and is not versioned

- The package shared with Ofir in Teams is kept in
  `docs/deliverables/nxsust_d_26_01589_revision/`, inside the working copy and
  ignored by git. It holds copies of the files above under the names the package uses: the
  manuscript and appendix A as `_tracked_changes.docx` and as `_clean.docx` (all
  revisions accepted in Word, citation highlights removed), both response letters as
  `_response_to_reviewers` and `_response_to_reviewers_concise`, the cover letter,
  declarations and appendix B, and the figures from `figures/manuscript/2022c/`
  (`figures/1_manuscript_figures/figure_1.tiff` to `figure_3.tiff`, Steenmeijer et
  al.'s three in `2_steenmeijer_figures_2022_data/`, the heat map in
  `3_origin_sector_heat_map/`). Refresh it from these sources after every change,
  never edit it, and upload the whole folder to Teams. Both documents carry Word's
  "do not compress images in file" setting (`w:doNotAutoCompressPictures` in
  `word/settings.xml`); without it Word downsamples the figures when it saves the
  clean copies.
- The response letters quote or paraphrase both referee reports. They are committed on the
  working branch but excluded by name from the public branch in
  `scripts/release/publish_ofir_branch.sh`, and its builder lives under
  `scripts/release/`, which is never published.
- The mitigation scenarios are held back for a follow-up paper. Their layer, modules,
  script and figures stay committed on the working branch, and
  `analysis.gold_scope` classifies them as withheld, so the published branch
  carries none of them in any commit, and the documents that described them are
  published with those passages removed.
- Appendix B is force-added despite the user's global `*.xlsx` ignore, because it
  is a deliverable. The journal's guide for authors stays unversioned: it is the
  publisher's.

## The letters are generated

Never edit the letters in Word. Change the content blocks in
`scripts/release/response_letter/build_response_letter.py` (full response),
`scripts/release/response_letter/build_response_letter_concise.py` (concise response) or
`scripts/release/cover_letter/build_cover_letter.py`, rebuild and check:

```bash
python scripts/release/response_letter/build_response_letter.py
python scripts/release/response_letter/build_response_letter_concise.py
python scripts/release/cover_letter/build_cover_letter.py
python scripts/release/response_letter/validate_letter.py
python scripts/release/response_letter/validate_letter.py docs/eriksen_et_al_2026/eriksen_et_al_2026_reviewer_responses_concise.docx
```

The validator counts words and headings and fails on em or en dashes, arrows,
banned words, bare reference numbers and repository paths in the authors' text.
Keep [`../revision/response_to_reviewers.md`](../revision/response_to_reviewers.md)
consistent with it; the consistency audit checks that file's numbers.
