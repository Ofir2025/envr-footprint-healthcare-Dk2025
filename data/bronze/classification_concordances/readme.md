# Classification concordances

The bridges between the classifications this study has to hold together:
EXIOBASE's 163 industries and 49 regions, ISIC rev.3, NACE rev.2, Statistics
Denmark's DB07 117-grouping, and the reporting groups the figures use. They are
kept as editable CSVs rather than buried in a workbook, so correcting a mapping
is a one-file edit followed by a rebuild.

| item | value |
|:---|:---|
| Provider | this study, derived from the EXIOBASE developers' own concordance set and Statistics Denmark's published tables |
| Upstream source | `ISIC REV. 3 - EXIOBASE2.0.xlsx` and `NACE2full_EXIOBASEp.xlsx` from the EXIOBASE developer concordance set (`mrio/classifications/concordances/exiobase/developers_concordances`), byte-identical to the copies mirrored by the BONSAI project at <https://github.com/BONSAMURAIS/correspondence_tables> |
| Licence | EXIOBASE terms, CC BY-SA 4.0 |
| Retrieved | tracked from 2026-09-08 (`7bee333`); `exiobase_industry_to_dst_db07.csv` last rebuilt 2026-09-09 (`c95fa7f`) |

## Files

| file | size | shape | built by |
|:---|:---|:---|:---|
| `exiobase_industry_to_dst_db07.csv` | 50 kB | 163 × 18 | `analysis.build_dst_concordance` |
| `exiobase_industry_to_isic_rev3.csv` | 15 kB | 138 × 6 | hand-derived from the EXIOBASE developers' ISIC table |
| `exiobase_industry_to_group.csv` | 11 kB | 163 × 3 | hand-maintained |
| `exiobase_region_to_world_region.csv` | 1.4 kB | 49 × 4 | hand-maintained |

**Known defect.** `exiobase_industry_to_dst_db07.csv` is *written* by
`analysis.build_dst_concordance` into this folder. A generated file in bronze
breaks medallion rule 1 — bronze is immutable source. It is recorded here and in
`../readme.md` rather than moved in passing, because
`analysis.build_star_schema` reads this folder too.

## Column dictionaries

### `exiobase_industry_to_dst_db07.csv`

The EXIOBASE-to-Denmark industry bridge, one row per EXIOBASE industry.

| column | meaning |
|:---|:---|
| `exiobase_position` | zero-based position in the EXIOBASE industry vector, 0-162 |
| `exiobase_code` | EXIOBASE industry code, e.g. `PARI` |
| `exiobase_name` | industry name |
| `exiobase_code1` | the ISIC-derived code, e.g. `i01.a` |
| `isic_rev3_division` | two-digit ISIC rev.3 division parsed from `exiobase_code1`; the value this file uses |
| `isic_rev3_division_isic_concordance` | the same division as it appears in `exiobase_industry_to_isic_rev3.csv`, carried for cross-checking. Empty for the 25 industries that file does not cover |
| `nace_rev2_candidates_exiobase_table` | candidate NACE rev.2 divisions from the EXIOBASE developers' `NACE2full_EXIOBASEp.xlsx` Sheet3, inverted and aggregated to the division. **Evidence, not the mapping**: the inversion is many-to-many, so these sets are wider than the industry's principal activity. Empty where the developers' table has no entry |
| `dst_nace_prefix` | the two-digit NACE prefixes of the DST targets, `;`-separated |
| `dst_industry_code` | DST DB07 six-digit target code or codes, `;`-separated |
| `dst_industry_name` | their names, `;`-separated in the same order |
| `mapping_type` | `one-to-one`, `one-to-many`, `many-to-one` or `unmatched` |
| `confidence` | `high`, `medium` or `low` |
| `basis` | prose statement of why this mapping was made |
| `mapping_group` | connected-component id of the bipartite mapping graph; `-1` when unmatched |
| `dst_output_share` | share of the group's DST output this row's target carries, 0-1, `;`-separated for one-to-many rows |
| `dst_import_share` | the same on imports |
| `mapping_group_label` | human-readable group label, e.g. `NACE 01 (PARI)` |
| `mapping_group_type` | the group's own mapping type |

**Two columns were renamed in this reorganisation.**
`isic_rev3_division_bronze_csv` became `isic_rev3_division_isic_concordance`
and `nace_rev2_candidates_developer` became
`nace_rev2_candidates_exiobase_table`. The old names described where the value
sat in *this repository's* internals — "the bronze CSV", "the developer" — rather
than what the value is. A published schema has to be readable by someone who has
never seen the repository.

### `exiobase_industry_to_isic_rev3.csv`

| column | meaning |
|:---|:---|
| `exiobase_industry_code` | EXIOBASE industry code |
| `exiobase_industry_name` | industry name |
| `isic_rev3_division` | two-digit ISIC rev.3 division |
| `isic_rev3_description` | the division's name |
| `technology_group` | `Low tech`, `Mid tech` or `High tech`, for manufacturing divisions 15-37 only; empty elsewhere |
| `isic_multi_division` | the full division set, space-separated, for the five industries that span several; empty otherwise |

**Caveat.** 138 of 163 EXIOBASE industries carry a row. The 25 without one are
the activities the hybrid release renumbers (`i24.x`, `i26.w.1`, `i40.2`,
`i90.x`); they are left blank rather than guessed. Five industries span several
divisions (quarrying 14/15, private households 95/96/97, extra-territorial
93/99); for those the lowest division is taken as primary and the full set is
kept in `isic_multi_division`, so the assignment is visibly a choice. `HEAL`
maps one-to-one to division 85, *Health and social work*.

### `exiobase_industry_to_group.csv`

| column | meaning |
|:---|:---|
| `exiobase_industry_code` | EXIOBASE industry code |
| `exiobase_industry_name` | industry name |
| `industry_group_name` | one of the 19 reporting groups, e.g. `Food and catering`, `Transport` |

Source of `dim_industry_group` in the star schema.

### `exiobase_region_to_world_region.csv`

| column | meaning |
|:---|:---|
| `region_code` | EXIOBASE region code, e.g. `AUT` |
| `region_name` | region name |
| `world_region` | one of the 6 world regions, e.g. `Europe` |
| `is_row_region` | `True` for the five rest-of-world aggregates, `False` for the 44 countries |

Source of `dim_region.world_region` in the star schema.
