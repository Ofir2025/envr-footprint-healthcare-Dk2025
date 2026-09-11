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

Silver is regenerable, so almost none of it is tracked. Four files are, and the
repository `.gitignore` un-ignores them one pattern at a time, because the
author's global excludes file drops every `*.csv` and that is exactly how a
required input once came to sit on one machine's disk and in no clone:

| tracked | why |
|:---|:---|
| `dst_supply_use/dk_data_2025.csv` | the expenditure and direct-emission frame every replication module reads; three numbers the manuscript's headline rests on |
| `dst_supply_use/dk_expenditure_breakdown_2019.csv` | provenance record of the 2019 expenditure boundary, column by column |
| `dst_supply_use/dk_expenditure_breakdown_2022.csv` | the same for 2022 |
| `netherlands_reference/dk_bottomup_data_2025.txt` | the four bottom-up items, which are Danish primary data and are not reproducible from bronze alone |

Untracked and rebuilt on demand: the 78 MB-per-year named register, the three
shipping-stage tables, the concordance, the background store and the handoff
workbooks. Every one of them is named in its folder's readme with the command
that produces it.

## Known defect

`dst_supply_use/dk_data_2025.csv` and
`netherlands_reference/dk_bottomup_data_2025.txt` are **one file each for every
analysis year**, overwritten on every run. A 2019 run leaves 2019 values in the
file a 2022 run then reads, and the `2025` in their names is an edition marker,
not a year of data. Their two-year neighbours — `dk_expenditure_breakdown_2019`
and `_2022`, `dk_atc_sales_2019` and `_2022`, and
`dk_health_expenditure_frame.csv`'s one block per analysis year — show what the
fix looks like. The frame file already carries both years, so the values are not
lost; the defect is that the two single-year files do not say which year they
hold.
