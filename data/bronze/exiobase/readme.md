# EXIOBASE background tables and classification workbooks

The multi-regional input-output background of the study, plus the two workbooks
that label and characterise it. **The files in this folder are not all the same
EXIOBASE release**, and the table below states the release of each, because the
mixture is deliberate and invisible from the filenames alone.

| file | release | what it is |
|:---|:---|:---|
| `IOT_2022_ixi/` | **v3.8.2** | the background model: industry-by-industry monetary tables for 2022 |
| `mr_hsut_2011_v3_3_17_extensions.xlsb` | **v3.3.17** | the hybrid supply-use extension workbook, 2011, read for the waste rows only |
| `characterisation_desire_version3_4_adapted.xlsx` | **v3.4**, adapted | DESIRE characterisation factors, modified by CML Leiden for the Steenmeijer replication |
| `classifications.xlsx` | **no release stamp; v3.3-era coding, adapted** | industry and region labels and the reporting aggregation, extended by this study |
| `regions_dk_2025.txt`, `regions_nl.txt` | v3.3-era DESIRE region list | the 49 EXIOBASE regions with their DESIRE grouping |

## Provider, licence and retrieval

| item | value |
|:---|:---|
| Provider | EXIOBASE consortium (NTNU Industrial Ecology Programme and partners); the classification and characterisation workbooks come from CML, Institute of Environmental Sciences, Leiden University |
| Dataset | EXIOBASE 3, industry-by-industry monetary tables, `IOT_<year>_ixi` |
| DOI | `10.5281/zenodo.5589597` (EXIOBASE 3.8.2) |
| URL | <https://zenodo.org/record/5589597> |
| Licence | CC BY-SA 4.0 |
| Retrieved | the v3.8.2 store predates this repository; wired in as the background on 2026-09-07 (`c7750dc`). The auxiliary workbooks arrived with the Netherlands replication (`ee3f015`, 2022-08-24) |
| Version note | `IOT_2022_ixi/metadata.json` records `name: exio382_ntnu`, `version: v3.81`, written 2021-09-08. The `v3.81` string is the writer's own label; the archive is the 3.8.2 release |

Why v3.8.2 rather than a later release is argued in
`docs/methods/exiobase_release_and_classification.md`; in short, v3.8.2's 2022
table reproduces the Danish national accounts and v3.10.2's 2022 nowcast does
not.

## The symlinks

`IOT_2022_ixi` is **a symlink, not a directory**, and it points outside the
repository:

```
data/bronze/exiobase/IOT_2022_ixi
  -> ~/Library/CloudStorage/OneDrive-Personal/Data/lca/input_output/mrio/
     exiobase/versions/v3_8_2/IOT_2022_ixi
```

That target is the author's personal EXIOBASE store and exists on one machine.
A clone gets a broken link, and every stage that builds the background fails on
it. To recreate it, download the v3.8.2 `IOT_2022_ixi` archive from the Zenodo
record above, unpack it anywhere, and link it:

```bash
ln -s /path/to/IOT_2022_ixi data/bronze/exiobase/IOT_2022_ixi
```

One year is ~1.5 GB unpacked, which is why it is linked rather than copied and
why `.gitignore` excludes `data/bronze/exiobase/IOT_2016_ixi`. The pipeline
reads the year named by `HC_BACKGROUND_YEAR`, so a run on another background
year needs that year's archive linked under the same name pattern.

Expected contents of an `IOT_<year>_ixi` archive: `A.txt` (~730 MB), `Z.txt`
(~709 MB), `Y.txt` (~23 MB), `x.txt`, `unit.txt`, `industries.txt` (163 rows),
`products.txt`, `finaldemands.txt`, `metadata.json`, `file_parameters.json`, and
the `satellite/` and `impacts/` subdirectories. `industries.txt` carrying
exactly 163 rows is the cheapest integrity check.

## Column dictionaries

### `classifications.xlsx`

Five sheets, each with a five-row banner before the header (readers pass
`skiprows=5`).

`disagg_ind` — 169 rows.

| column | meaning |
|:---|:---|
| `Position` | zero-based position in the EXIOBASE industry vector; blank for the six appended rows |
| `Description` | industry name |
| `Code` | EXIOBASE industry code, `A_` prefixed, e.g. `A_PARI` |
| `Code1` | the ISIC-derived code, e.g. `i01.a`; the column `analysis.build_dst_concordance` parses the ISIC rev.3 division from |
| `AggPos`, `AggDescription`, `AggCode` | the reporting group: position, name and short code, e.g. `Food and catering` / `Food` |
| `Scope` | `Scope 1`, `Scope 3` or `Outside protocol` |
| `Scope_hotspot` | `Direct` or `Indirect` |

`agg_ind` (19 rows), `agg_ind_fig` (21), `disagg_reg` (49), `agg_reg` (6) carry
`Position`, `Description`, `Code` and, for `disagg_reg`, the aggregate region.

**Caveat, and the reason this file has no release stamp.** The first 163 rows of
`disagg_ind` match `IOT_2022_ixi/industries.txt` exactly, in order, by name and
by both codes. The last **six rows are not EXIOBASE industries at all**: they are
this study's bottom-up items — `B_HEAL` direct healthcare impact, `B_ANAE`
anaesthetic gases, `B_PMDI` pMDI propellants, `B_COMM` employee commute, `B_VISI`
patient and visitor travel, `B_REST` undistributed travel — appended so the
reporting aggregation can carry them beside the input-output rows. The file is
therefore **adapted**, like the characterisation workbook beside it, and is not
a pristine EXIOBASE release artefact. Do not treat it as one, and do not replace
it with an upstream classification file: the six rows would be lost.

### `characterisation_desire_version3_4_adapted.xlsx`

DESIRE v3.4 characterisation factors as adapted by CML Leiden (the `info` sheet
carries the CML address). Sheets `Q_factorinputs` (4 × 25), `Q_emissions`
(121 × 427), `Q_resources` (2 × 22), `Q_materials` (18 × 640), with
`classification` (1104 rows) naming the stressors and `description` the impact
rows. Read by `pipelines.prep_background_2025.load` and
`analysis.impact_categories_full`.

**Caveat.** Its climate row is AR4-era. The study's headline GWP figures use the
AR6 factors documented in `../exiobase_characterisation/readme.md`; this
workbook supplies the non-climate categories and the AR4 comparison.

### `regions_dk_2025.txt` and `regions_nl.txt`

Tab-separated, 49 data rows plus a header, identical files but for one line.

| column | meaning |
|:---|:---|
| `ISO2`, `ISO3`, `UN code` | country identifiers |
| `Name` | country name |
| `DESIRE region`, `DESIRE region name` | the aggregate region code and name |
| `Population 2011` | population, persons, as distributed with the DESIRE region file |

The only difference is Denmark's aggregate: `regions_nl.txt` puts `DK` in `WE`
(Europe); `regions_dk_2025.txt` breaks `DK` out as its own region. **No module
reads `regions_dk_2025.txt`** — `pipelines.prep_background_2025.load` reads
`regions_nl.txt` and the Danish grouping is applied in memory. It is kept as the
written form of that grouping.

### `mr_hsut_2011_v3_3_17_extensions.xlsb`

EXIOBASE v3.3.17 hybrid supply-use extension workbook for 2011, 12 MB, binary
Excel. Read only by `pipelines.prep_background.waste` for the waste rows, which
have no counterpart in the monetary v3.8.2 tables. Its year is 2011 and its
release is v3.3.17: the waste coefficients are therefore on a different release
and a different year from the rest of the model, which is a limitation of the
waste indicator, not a mistake.
