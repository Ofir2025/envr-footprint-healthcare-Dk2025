# Bronze: raw inputs

Place immutable source downloads and original workbooks here. Preserve the
source filename in a manifest and add the analysis year to derived names.

Country-specific files use the ISO 2 country code in their names and, for
row-oriented CSV/TSV inputs, in an `ISO2` column. For example, `nl_` identifies
Netherlands source data and `dk_` identifies Denmark source data. Bronze files
are never overwritten by modelling scripts; generated or transformed inputs
belong in `data/silver/inputs/`.

For Exiobase region labels, `exiobase_v3_7/regions_nl.txt` is the canonical
mapping inherited from the upstream Netherlands repository. The Denmark
pipeline derives its DK grouping in memory; no second region-label copy is
stored in Bronze.
