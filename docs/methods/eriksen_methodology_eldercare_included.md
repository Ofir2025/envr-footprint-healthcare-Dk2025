# Ofir Eriksen's methodology - eldercare included

This is Ofir Eriksen's methodology document. Source file:
`eriksen_methodology_eldercare_included.docx`, created 2024-02-22, last
modified 2026-02-04. Converted from Word with `pandoc -f docx -t gfm`; the
original `.docx` is kept alongside this file.

This version explicitly **includes eldercare** as part of EXIOBASE's
"Residential care and social work services". A separate, longer methodology
note by the same author -
[`eriksen_methodology_eldercare_excluded.md`](eriksen_methodology_eldercare_excluded.md)
- instead excludes eldercare (COFOG 10) from the study boundary. The two are
not versions of one document: they describe two different system-boundary
choices, and both are kept.

---

## Study aim and scope

The consumption‑based environmental footprint of the Danish healthcare system was quantified, by replicating the analytical structure of Steenmeijer et al. and adapting it to Denmark. The analysis covers upstream supply‑chain impacts of healthcare consumption and selected healthcare‑specific emission sources that are poorly represented in monetary input-output tables (anaesthetic gases, pMDIs, staff commuting, and patient/visitor travel)

## Analytical framework

Environmentally extended multi‑regional input-output (EE‑MRIO) modelling was based on EXIOBASE v3.7 (49 regions, 163 industries) with environmental extensions and characterization factors. After loading EXIOBASE data and classifications, the Leontief inverse $`L = (I - A)^{- 1}`$ was computed, interindustry transactions $`Z = A \cdot diag(x)`$ was reconstructed.

## Definition of healthcare consumption

Healthcare final demand was built from Danish national accounts (SUT) categories mapped to EXIOBASE, following the structure in Steenmeijer et al.:

1.  Healthcare & social care services (incl. human health, residential, and social work services);

2.  Pharmaceutical products and other medical products;

3.  Therapeutic appliances and equipment.  
    Danish SUT detail (2019) was used to classify and aggregate expenditures consistently with EXIOBASE’s product‑by‑industry system; values remained in EXIOBASE’s monetary system to preserve MRIO balance. [\[DK Umat 2019.xlsx \| Excel\]](https://syddanskuni-my.sharepoint.com/personal/ofe_igt_sdu_dk/_layouts/15/Doc.aspx?sourcedoc=%7B8A27B6B6-DA82-4DB6-B1D0-4C5687667135%7D&file=DK%20Umat%202019.xlsx&action=default&mobileredirect=true), [\[syddanskun...epoint.com\]](https://syddanskuni-my.sharepoint.com/personal/ofe_igt_sdu_dk/Documents/Microsoft%20Copilot%20Chat%20Files/exiobase_3_7-waste2025.py)

Eldercare is included throughout as part of EXIOBASE’s “Residential care and social work services”, aligning with the sectoral boundary used in the code
