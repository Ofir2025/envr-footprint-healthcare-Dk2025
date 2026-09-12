# Eriksen et al. (2026) submission package

Everything that goes to *Next Sustainability* for NXSUST-D-26-01589, and nothing
else. These are the working files as well as the deliverables: the manuscript and
appendix A carry the revision as tracked changes authored by Albert, so there is
no separate working copy to keep in step. There was one until 2026-09-12, in a
`revision/` subfolder, and it produced exactly the failure duplication invites:
the response letter here sat four days out of date while the real answer lived in
`docs/revision/response_to_reviewers.md`.

For this repository's own assessment of the manuscript against the 2022
re-analysis, see
[`../revision/results_2022.md`, "Assessment of the Eriksen et al. (2026) manuscript"](../revision/results_2022.md#assessment-of-the-eriksen-et-al-2026-manuscript).
The record of what each round of revision changed is in
[`../revision/request_checklist.md`](../revision/request_checklist.md).

| File | Purpose |
|:---|:---|
| `eriksen_et_al_2026_manuscript.docx` | The manuscript, revision tracked. Three figures, 46 references. |
| `eriksen_et_al_2026_supplementary_appendix_a.docx` | Supplementary appendix A: derivations, validation, nineteen figures. |
| `eriksen_et_al_2026_supplementary_appendix_b_private_travel_scaling.xlsx` | Supplementary appendix B: the private-travel scaling workbook. |
| `eriksen_et_al_2026_supplementary_figures_si.pdf` | Supplementary figures as submitted. |
| `eriksen_et_al_2026_reviewer_responses.docx` | Point-by-point response to the reviewers. Built from `../revision/response_to_reviewers.md`, which is the source of truth. |
| `eriksen_et_al_2026_cover_letter.docx` | The cover letter to *Next Sustainability*. |
| `eriksen_et_al_2026_declaration_interests.docx` | The declaration of competing interests. |
| `eriksen_et_al_2026_ethics_declaration.docx` | The ethics declaration. |
| `guide_for_authors_next_sustainability.pdf` | The journal's guide for authors, for reference. |

Two files here never reach the public branch. The response letter reproduces both
referee reports in full and is excluded by name in
`scripts/release/publish_ofir_branch.sh`; the appendix B workbook and the two PDFs
are covered by a global gitignore for `*.xlsx` and `*.pdf`, so they live in the
working tree only.

The response letter is generated, not edited here. Change
`../revision/response_to_reviewers.md` and rebuild:

```
pandoc docs/revision/response_to_reviewers.md --from=markdown+pipe_tables \
  -o docs/eriksen_et_al_2026/eriksen_et_al_2026_reviewer_responses.docx
```
