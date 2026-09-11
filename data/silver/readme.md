# Silver: transformed bronze, ready to load

Silver is the middle of the medallion. It holds the **validated, conformed,
model-ready products of bronze** — one file per transformation, each with a
named producing module and a command that rebuilds it from the immutable
sources in `data/bronze/`.

## The contract

**1. What belongs here.** A file whose values are bronze values, transformed:
named, unit-converted, joined, conformed to the classification the model reads,
or reduced to the frame a downstream function consumes. The Danish medicines
register with its fourteen positional fields given names. Statistics Denmark's
water-transport share, read out of a 117-industry workbook. The EXIOBASE
industry-to-DB07 bridge. The three-row expenditure frame `createBackground`
takes.

**2. What does not.** Raw sources do not: they stay in `data/bronze/`, which no
modelling script writes to, and a generated file there is a defect regardless of
its content. Published results do not: they go to `data/gold/results/`, which is
in version control, is tabular-only, and is what the manuscript quotes. A file
here that no module reads is also not a silver product — it is debris.

**3. Silver is regenerable.** Every file in this layer can be deleted and
rebuilt, and every folder readme names the command that rebuilds each of its
files. That is why most of the layer is git-ignored without loss: a clone
restores it by running the pipeline, not by downloading it. It is also why
nothing may read silver as a source of record. If a number can only be obtained
by reading a silver file that no command reproduces, that number has no
provenance.

**4. Silver mirrors bronze, by provenance.** Each transformed product sits in a
folder named for the **bronze folder it derives from**, so the path says where
the numbers came from:

```
data/bronze/dst_input_output/input_output_en_2022.xlsx   ← source
data/silver/dst_input_output/dst_water_transport_domestic_share.csv   ← product
```

A product built from several bronze folders sits under the one that dominates
it, with the others named in its folder's readme. Only folders that hold
something exist — there is no silver `dk_travel_survey/`, `dst_capital_stock/`,
`dst_emission_accounts/`, `eurostat_figaro/`, `exiobase_capital/` or
`exiobase_characterisation/`, because nothing in this layer is derived from them.

The layer used to be one flat `inputs/` folder. It could not answer the one
question silver exists to answer: `exiobase_industry_sector_group.csv` and
`dst_water_transport_domestic_share.csv` sat side by side in it with nothing but
a filename prefix to say that one is an EXIOBASE product and the other a
Statistics Denmark one, and two of its four tracked files were not mentioned in
its readme at all. Check C20 of `analysis.audit_consistency` now fails if a
tracked file here sits in a folder whose readme does not name it.

**5. Two things here are not part of the mirror**, and both are kept apart
deliberately.

`background/` is the **model-object store**: the pickled MRIO tables and the
prepared background objects. A background object is not a transformed source
table — it is a model built from many of them, and it is roughly ten gigabytes
that no clone holds. It is git-ignored, `paths.BACKGROUND_DIR` points at it, and
a working copy may hold it as a symlink to another checkout's copy rather than as
a directory of its own.

`handoff/` is the **script-to-script handoff**: workbooks one module writes for
another module to read back. An interim workbook is not a transformed source
table. It has no bronze folder to be named for, it is one module's private
message to another rather than an input any consumer may read, and mixing it in
with the derived data is what put six Excel files into the published gold tree in
the first place. See `handoff/readme.md`.

## Index

| folder | derives from | holds |
|:---|:---|:---|
| `classification_concordances/` | `data/bronze/classification_concordances/` | the EXIOBASE-to-DB07 industry bridge with its split weights |
| `dk_medicines_register/` | `data/bronze/dk_medicines_register/` | the Danish ATC sales register with named columns |
| `dst_input_output/` | `data/bronze/dst_input_output/` | the Danish water-transport domestic share phi per table year |
| `dst_supply_use/` | `data/bronze/dst_supply_use/` | the Danish healthcare expenditure frame, its per-column provenance record, and the two-year expenditure and direct-emission table |
| `exiobase/` | `data/bronze/exiobase/` | EXIOBASE industry code to aggregate reporting group |
| `netherlands_reference/` | `data/bronze/netherlands_reference/` | the Danish bottom-up inventory, scaled from the Dutch baseline |
| `background/` | — | the model-object store; git-ignored, not a bronze mirror |
| `handoff/` | — | script-to-script interim workbooks; git-ignored, not a bronze mirror |

## Rebuilding the layer

In dependency order, from a working copy with `data/bronze/` populated:

```console
PYTHONPATH=src .venv/bin/python -m analysis.build_atc_sales
PYTHONPATH=src .venv/bin/python -m analysis.build_dst_concordance
PYTHONPATH=src .venv/bin/python -m analysis.build_shipping_inputs
PYTHONPATH=src HC_ANALYSIS_YEAR=2019 HC_BACKGROUND_TAG=_snacship \
    .venv/bin/python -m analysis.main_2025
PYTHONPATH=src HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship \
    .venv/bin/python -m analysis.main_2025
```

The first three read bronze only. `analysis.main_2025` also builds the
background objects under `background/` and the handoff workbooks under
`handoff/`, and it writes the published Eriksen tables to gold, so it is the
step that has to run per analysis year.

Both layers can be pointed outside the working copy, so two checkouts of
different scope share one physical copy:

```console
export HC_BRONZE_DIR=/path/to/data/bronze
export HC_SILVER_DIR=/path/to/data/silver
```

## What is and is not in version control

Silver is regenerable, so almost none of it is tracked. Seven files are, and the
repository `.gitignore` un-ignores them one pattern at a time, because the
author's global excludes file drops every `*.csv` and that is exactly how a
required input once came to sit on one machine's disk and in no clone:

| tracked | why |
|:---|:---|
| `dst_supply_use/dk_data_2019.csv` | the 2019 expenditure and direct-emission frame every replication module reads |
| `dst_supply_use/dk_data_2022.csv` | the same for 2022; three numbers the manuscript's headline rests on |
| `dst_supply_use/dk_expenditure_breakdown_2019.csv` | provenance record of the 2019 expenditure boundary, column by column |
| `dst_supply_use/dk_expenditure_breakdown_2022.csv` | the same for 2022 |
| `netherlands_reference/dk_bottomup_data_2019.txt` | the four bottom-up items for 2019, Danish primary data not reproducible from bronze alone |
| `netherlands_reference/dk_bottomup_data_2022.txt` | the same for 2022 |
| `dst_input_output/dst_water_transport_domestic_share.csv` | $\phi$, the sea-transport reallocation's target share. Tracked on 11 September 2026, at 401 bytes: it is a published number the methods text quotes and every row of layer 10's diagnostics carries, and it multiplies a row block of $\mathbf{A}$ before a Leontief inversion, so it is read to the last bit |

Untracked and rebuilt on demand, and each one tested against the same question -
*does anything published quote a number from this file?*

| untracked | why not, on that test |
|:---|:---|
| `dk_medicines_register/dk_atc_sales_<year>.csv` | 78 MB per year; the numbers it feeds are published as the anaesthetic-gas item, not as register rows |
| `exiobase/exiobase_industry_sector_group.csv` | no document quotes a number from it. The group labels it assigns travel into gold in the published tables' own `sector_group` columns, and `data/bronze/exiobase/classifications.xlsx` is tracked, so one command rebuilds it in any clone |
| `classification_concordances/exiobase_industry_to_dst_db07.csv` | the same: it is a mapping, not a quoted value, and its bronze concordances are tracked |
| `dst_supply_use/dk_health_expenditure_frame.csv` | every value in it is already in the two tracked `dk_data_<year>.csv` files - it is the same frame reshaped to carry both years at once |
| `background/`, `handoff/` | the model-object store and the interim workbooks; ten gigabytes and six workbooks, neither a source of record |

Every one of them is named in its folder's readme with the command that produces
it.

## Fixed defect: the year scope

`dk_data_2025.csv` and `dk_bottomup_data_2025.txt` used to be **one file each for
every analysis year**, overwritten on every run, with `2025` an edition marker
rather than a year of data. A 2019 run left 2019 values in the file a 2022 run
then read, and every reader of them read whichever year had run last.

They are now `dk_data_<year>.csv` and `dk_bottomup_data_<year>.txt`, which is the
pattern their neighbours already used — `dk_expenditure_breakdown_<year>.csv`,
`dk_atc_sales_<year>.csv` — and `paths.silver_dk_data_csv` and
`paths.silver_dk_bottomup_txt` are functions of the year rather than constants,
so a path cannot be built without naming a year and cannot be read for the wrong
one. Verified by a 2022 → 2019 → 2022 round trip: the 2019 run left
`dk_data_2022.csv` and `dk_bottomup_data_2022.txt` untouched, and the 2022 gold
tables came back byte-identical.

## Why the year is in the name and the care boundary is not

The year is in the name because a file can hold either year's values: a 2019 run
and a 2022 run both write, so a shared name is overwritten and read for the
wrong year. That happened, and it is the fixed defect above.

The care boundary is **not** in the name, and this is a decision rather than an
omission. `analysis.main_2025` writes `dk_data_<year>.csv` and
`dk_expenditure_breakdown_<year>.csv` **only** for `HC_SCOPE=health_eldercare`
and skips the write on every other boundary, so these files have exactly one
possible boundary. A suffix would distinguish nothing: there is no second file
for it to be distinguished from, and a `_health_eldercare` on every name would
state a constant.

What a suffix could not have prevented either is the one thing that could go
wrong here — a module running on another boundary opening the file anyway and
publishing the manuscript boundary's expenditure as that boundary's own. A
suffix does not stop a reader from typing it. So that is enforced at the read
instead, by `analysis.constants.require_manuscript_boundary`, which every
reader of these two files calls first: `analysis.export_tables`,
`analysis.lenzen_replication`, `analysis.malik_replication`,
`analysis.waste_validation` and `analysis.waste_domestic_dst`. On any boundary
but the manuscript's they stop, and say which boundary they are on and which
file they refused to read.

`dk_bottomup_data_<year>.txt` is a third case and needs neither the suffix nor
the guard: it is written on every boundary, and it is boundary-INVARIANT.
Anaesthetic gases, pMDI propellants, commuting and patient travel are Danish
primary totals scaled from the Dutch baseline, and none of the four scaling
inputs is a function of the care boundary. Measured rather than assumed: a
`zorg_en_welzijn` run on 11 September 2026 rewrote the file and left it
byte-identical, and the three bottom-up rows of `table_01.csv` are equal to the
last digit in `01_eriksen_replication/2019c` and `01_eriksen_replication/2019d`.

`analysis.double_counting_audit` records the same asymmetry from the reader's
side, and `data/silver/dst_supply_use/readme.md` repeats this section beside the
files it is about.
