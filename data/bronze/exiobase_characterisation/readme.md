# Characterisation factors

The factors that turn stressors into impacts. Two competing IMPACT World+
matrices for the non-climate categories, and the IPCC AR6 chapter the study's
GWP-100 values are read from.

| item | value |
|:---|:---|
| Providers | CIRAIG (IMPACT World+); IPCC (AR6 WG1) |
| Licences | CC BY-SA 4.0, CC BY 4.0, and IPCC terms respectively — see each entry |
| Retrieved | 2026-09-07 |

**None of the four files below is in version control** - this readme is the
only tracked thing here. They total 26 MB of third-party material, and the two
IPCC chapters are PDFs, which the author's global excludes file drops in any
case. Every DOI and URL needed to
restore the folder is given here, and the values the study actually uses are
quoted in `analysis.constants`, so a clone can check the numbers without the
files.

## Files

| file | size | provider | shape | licence |
|:---|:---|:---|:---|:---|
| `impact_world_plus_2.2.1_expert_version_exiobase_3.8.2_and_before.xlsx` | 186 kB | CIRAIG | 57 impacts × 1113 stressors | CC BY-SA 4.0 |
| `C_exio_IW_1.28_1.46.csv` | 249 kB | CIRAIG | 36 impacts × 1113 stressors | CC BY 4.0 |
| `IPCC_AR6_WGI_Chapter07.pdf` | 22.8 MB | IPCC | — | IPCC terms |
| `IPCC_AR6_WGI_Chapter_07_Supplementary_Material.pdf` | 2.8 MB | IPCC | — | IPCC terms |

### `impact_world_plus_2.2.1_expert_version_exiobase_3.8.2_and_before.xlsx`

IMPACT World+ v2.2.1, EXIOBASE 3.8.2 expert matrix. Published 2026-03-06.

| item | value |
|:---|:---|
| DOI | `10.5281/zenodo.18892673` (concept DOI `10.5281/zenodo.1488368`) |
| URL | <https://zenodo.org/records/18892673> |

**Verified:** its column names match EXIOBASE v3.8.2 `satellite/unit.txt`
exactly, and in order — which is what licenses using it positionally.

**Caveat:** its climate rows are **AR5-like**, not AR6 (CH4 28.1, N2O 267,
SF6 23500). The study does not take its GWP row.

### `C_exio_IW_1.28_1.46.csv`

IMPACT World+ v1.28-1.46 for EXIOBASE3. Published 2021-05-05, modified
2022-12-21.

| item | value |
|:---|:---|
| DOI | `10.5281/zenodo.4739143` |
| URL | <https://zenodo.org/record/4739143> |

Its climate row is an AR4/AR5 hybrid. Kept as the licence-clean fallback and as
a sensitivity case.

### `IPCC_AR6_WGI_Chapter07.pdf`

Forster et al. (2021), AR6 WG1 Chapter 7, "The Earth's Energy Budget, Climate
Feedbacks and Climate Sensitivity", Cambridge University Press, pp. 923-1054,
doi `10.1017/9781009157896.009`.

URL: <https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_Chapter07.pdf>

**Table 7.15** (GWP-100 including carbon-cycle responses) is on report page 1017
= PDF page 95. That table is where the study's `AR6_GWP100` values come from.

Licence: IPCC terms — free use for non-commercial and educational purposes with
attribution.

### `IPCC_AR6_WGI_Chapter_07_Supplementary_Material.pdf`

AR6 WG1 Chapter 7 Supplementary Material. **Table 7.SM.7**, the full metric
table, at 7SM-24ff = PDF pages 27-38.

URL: <https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_Chapter_07_Supplementary_Material.pdf>

**Caveat:** ipcc.ch still serves the "Final Government Distribution" version of
7SM.

## Referenced but not mirrored here

| source | why not |
|:---|:---|
| AR6 WG3 Annex II Table 9, p. 11 — inventory GWP-100 including the three-way CH4 split. <https://www.ipcc.ch/report/ar6/wg3/downloads/report/IPCC_AR6_WGIII_Annex-II.pdf> | consulted, not used as an input |
| ReCiPe 2016 v1.1 characterisation factors, 6.26 MB. <https://www.rivm.nl/sites/default/files/2024-10/ReCiPe2016_CFs_v1.1_20180117.xlsx> | **not openly licensed**, so not mirrored. The two ReCiPe GWP values the pMDI item uses (1,549 and 3,860 kg CO2-eq/kg for HFC-134a and HFC-227ea) are quoted in `analysis.main_2025` |

## Which factors the study actually applies

The climate row is **AR6**, from Table 7.15 above, carried in
`analysis.constants.AR6_GWP100`. The non-climate categories come from the
DESIRE v3.4 adapted workbook in `../exiobase/`, not from this folder; the
IMPACT World+ matrices here drive
`data/gold/results/12_impact_categories_full/` and the private impact-world-plus
layer. Mixing AR4 and AR6 factors in one total is the defect that made this
folder's provenance worth writing down: the MRIO climate row moved to AR6 while
the anaesthetic N2O term did not, leaving 0.95 kt CO2-eq of disagreement inside
one number.
