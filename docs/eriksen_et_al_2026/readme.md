# Eriksen et al. (2026) submission package

Everything that goes to *Next Sustainability* for NXSUST-D-26-01589, and nothing
else. These are the working files as well as the deliverables: the manuscript and
appendix A carry the revision as tracked changes, so there is no separate working
copy to keep in step. The latest layer of tracked changes in both is by Albert
Kwame Osei-Owusu, dated 14 September 2026. In both documents the EndNote field
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
| `eriksen_et_al_2026_manuscript.docx` | The manuscript, revision tracked. Three figures, one table, 49 references. | yes, tracked and clean |
| `eriksen_et_al_2026_supplementary_appendix_a.docx` | Supplementary appendix A: derivations, validation, five tables, nineteen figures, 34 references. | yes, tracked and clean |
| `eriksen_et_al_2026_supplementary_appendix_b_travel_calculations.xlsx` | Supplementary appendix B: the travel calculations workbook, with README, commuting (Eqs. A.11 and A.12), patient and visitor travel (Eq. A.13), modal split and the superseded ratio scaling for comparison. Formulas carry cached values and reproduce the model output. | yes |
| `eriksen_et_al_2026_reviewer_responses.docx` | The formal point-by-point response to the editor and reviewers. | yes |
| `eriksen_et_al_2026_cover_letter.docx` | The cover letter to *Next Sustainability*. | yes |
| `eriksen_et_al_2026_declaration_interests.docx` | The declaration of competing interests. | yes |
| `eriksen_et_al_2026_ethics_declaration.docx` | The ethics declaration. | yes |
| `eriksen_et_al_2026_supplementary_figures_si.pdf` | Supplementary figures of the July 2026 submission, superseded by appendix A and cited nowhere. | **no** |
| `guide_for_authors_next_sustainability.pdf` | The journal's guide for authors, for reference (Elsevier copyright). | no |

The figure files for upload are `figures/manuscript/2022c/fig1_ofir_panels_2022.tiff`,
`fig2_top_origin_industry_pairs_2022.tiff` and `fig3_scopes_stacked_2022.tiff`.
Still outstanding before submission: the new Zenodo version DOI (appendix A, Data,
code and software; manuscript, Data availability) and the title page with
affiliations and the corresponding author's email.

## What is and is not versioned

- The response letter quotes both referee reports in full. It is committed on the
  working branch but excluded by name from the public branch in
  `scripts/release/publish_ofir_branch.sh`, and its builder lives under
  `scripts/release/`, which is never published.
- Appendix B is force-added despite the user's global `*.xlsx` ignore, because it is
  a deliverable of the paper. The two PDFs stay unversioned: one is superseded, the
  other is the publisher's.

## The response letter is generated

Never edit the letter in Word. Change the content blocks in
`scripts/release/response_letter/build_response_letter.py`, rebuild and check it:

```bash
python scripts/release/response_letter/build_response_letter.py
python scripts/release/response_letter/validate_letter.py
```

The validator counts words and headings and fails on em or en dashes, arrows,
banned words, bare reference numbers and repository paths in the authors' text.
Keep [`../revision/response_to_reviewers.md`](../revision/response_to_reviewers.md)
consistent with it; the consistency audit checks that file's numbers.
