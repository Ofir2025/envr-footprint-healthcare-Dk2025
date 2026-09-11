# Silver: the EXIOBASE-to-Denmark industry bridge

Mirrors `data/bronze/classification_concordances/`. One table: the bridge
$\mathbf{K}$ that the simplified-SNAC import estimate $e_m = \mathbf{Q}\,
\mathbf{K}\,m$ needs between the Danish DB07/NACE rev.2 classification the import
vector $m$ is written in and the EXIOBASE region-industry nodes $\mathbf{Q}$ is
written in — with the split weights that make it a weighted bridge rather than a
binary incidence matrix.

| item | value |
|:---|:---|
| Bronze sources | `data/bronze/classification_concordances/exiobase_industry_to_isic_rev3.csv` (dominant source: the ISIC side of every mapping); `data/bronze/exiobase/classifications.xlsx` for the EXIOBASE industry list and descriptions; `data/bronze/dst_input_output/input_output_en_<year>.xlsx` for the DST industry names and both split-weight vectors; `data/bronze/dst_emission_accounts/dst_emission_accounts_by_industry.csv` for the validation |
| Produced by | `analysis.build_dst_concordance` |
| Rebuild | `PYTHONPATH=src .venv/bin/python -m analysis.build_dst_concordance` |
| In version control | **no** — regenerable from the tracked bronze concordance and the DST workbooks |

It sits under `classification_concordances/` because that is where its dominant
source sits and because it is the same kind of object: a bridge between two
classifications. It used to be **written into** the bronze folder of that name,
which broke medallion rule 1 — bronze is immutable source, and nothing generated
belongs there. That defect is now fixed rather than recorded.

## Files

| file | derives from | transformation | rows × cols | size |
|:---|:---|:---|:---|:---|
| `exiobase_industry_to_dst_db07.csv` | the four bronze sources above | three sources resolved in order of authority — the EXIOBASE developers' own NACE rev.2 concordance (frozen into the module as evidence), the ISIC rev.3 division carried by EXIOBASE's `Code1`, and the industry descriptions that resolve the divisions which split or merge between revisions — then weighted by two share vectors read off the Danish table, and validated against the twelve hand-built seed groups of `analysis.release_defect_audit.CONCORDANCE` | 163 × 18 | 50 kB |

## Columns

| column | unit | meaning |
|:---|:---|:---|
| `exiobase_position` | index | zero-based position in the EXIOBASE industry vector, 0-162 |
| `exiobase_code` | — | EXIOBASE industry code, e.g. `PARI` |
| `exiobase_name` | — | industry name |
| `exiobase_code1` | — | the ISIC-derived code, e.g. `i01.a` |
| `isic_rev3_division` | code | two-digit ISIC rev.3 division parsed from `exiobase_code1`; the value this file uses |
| `isic_rev3_division_isic_concordance` | code | the same division as it appears in the bronze `exiobase_industry_to_isic_rev3.csv`, carried for cross-checking. Empty for the 25 industries that file does not cover |
| `nace_rev2_candidates_exiobase_table` | code | candidate NACE rev.2 divisions from the developers' `NACE2full_EXIOBASEp.xlsx` Sheet3, inverted and aggregated to the division. **Evidence, not the mapping**: the inversion is many-to-many, so these sets are wider than the industry's principal activity. Empty where the developers' table has no entry |
| `dst_nace_prefix` | code | two-digit NACE prefixes of the DST targets, `;`-separated |
| `dst_industry_code` | code | DST DB07 six-digit target code or codes, `;`-separated |
| `dst_industry_name` | — | their names, `;`-separated in the same order |
| `mapping_type` | — | `one-to-one`, `one-to-many`, `many-to-one` or `unmatched` |
| `confidence` | — | `high`, `medium` or `low` |
| `basis` | — | prose statement of why this mapping was made |
| `mapping_group` | index | connected-component id of the bipartite mapping graph; `-1` when unmatched |
| `dst_output_share` | share, 0-1 | share of the group's Danish **output** this row's target carries, `;`-separated for one-to-many rows, summing to 1 across the row |
| `dst_import_share` | share, 0-1 | the same on Danish **imports** |
| `mapping_group_label` | — | human-readable group label, e.g. `NACE 01 (PARI)` |
| `mapping_group_type` | — | the group's own mapping type |

## Which split weight to use

A one-to-many row divides one EXIOBASE industry between several Danish
industries, and the Danish industries inside a split can differ in emission
intensity by more than an order of magnitude — so an implementer who averages
gets a different answer from one who weights. Both published vectors are given:

`dst_import_share` is the vector a SNAC import estimate multiplies, so it is the
sharpest reading of $\mathbf{K}$ and the one the module recommends. Its caveat,
recorded in `build_dst_concordance.split_sensitivity`, is that a barely traded
group rests its shares on a small base and is better weighted on output.

`dst_output_share` is the production-share proxy of Palm et al. (2019), kept
because it is the published convention and because it is defined for every row.

A module that holds its own import vector $m$ should weight by that vector rather
than by either default written here. An implementer who keeps $m$ in Danish
classification needs no split weights at all: the Danish table publishes imports
by product at the same 117-industry resolution as the emission accounts, so
$\mathbf{Q}$ applies directly.

## Caveat

**Candidate sets are wider than principal activities.**
`nace_rev2_candidates_exiobase_table` comes from inverting a many-to-many table:
`MACH` carries 33 and 95 because NACE rev.2 moved repair out of the manufacturing
divisions, not because machinery is repair. Use the column as evidence for the
mapping, never as the mapping.
