# Silver: the Danish bottom-up inventory

Mirrors `data/bronze/netherlands_reference/`. One table: the impact items that sit
**outside** the input-output model — anaesthetic gases, metered-dose inhaler
propellants, staff commuting and visitor travel — expressed for Denmark.

| item | value |
|:---|:---|
| Bronze sources | `data/bronze/netherlands_reference/nl_bottomup_data.txt` (Steenmeijer et al., the baseline that is scaled — dominant source); `data/bronze/dk_travel_survey/commuting_private_travel_calculations_2026.xlsx` for the commute and visitor factors; `data/bronze/dk_medicines_register/<year>_atc_code_data.txt`, via `dk_atc_sales_<year>.csv`, for the volatile anaesthetics |
| Produced by | `analysis.main_2025` |
| Read by | `analysis.scopes_detail`, `analysis.mitigation_scenarios` |
| Rebuild | `HC_ANALYSIS_YEAR=<year> HC_BACKGROUND_TAG=_snacship PYTHONPATH=src .venv/bin/python -m analysis.main_2025` |
| In version control | **yes** — the Danish primary values are not reproducible from bronze alone |

It sits under `netherlands_reference/` because the Dutch file is the object that
is transformed: every row and column of this table is a row and column of
`nl_bottomup_data.txt`, rescaled. The Danish register and travel survey supply
factors and replacement values, not structure.

## Files

| file | derives from | transformation | rows × cols | size |
|:---|:---|:---|:---|:---|
| `dk_bottomup_data_2025.txt` | `nl_bottomup_data.txt` | every impact column of the four sources multiplied by its Danish/Dutch factor; the `(total)` rows recomputed from their scaled `(direct)` and `(indirect)` rows rather than scaled directly; the two medical-gas climate values then **replaced** by Danish primary values; `ISO2` set to `DK` | 8 × 7 | 480 B |

Tab-separated, as the Dutch baseline is.

## Columns

| column | unit | meaning |
|:---|:---|:---|
| `Source` | — | row name: `Anaesthetic`, `pMDI`, `Commute (total/direct/indirect)`, `Visitor travel (total/direct/indirect)` |
| `Global warming (ktCO2eq)` | kt CO2-eq | climate impact |
| `Material extraction (kt)` | kt | raw material extraction |
| `Blue water consumption (Mm3)` | Mm³ | blue water consumption |
| `Land use (km2)` | km² | land use |
| `Waste generation (kt)` | kt | waste generation; zero for every bottom-up item |
| `ISO2` | — | country of the row; `DK` throughout |

## The transformation, per row

**Commute and visitor travel** are scaled from the Dutch values on Danish
employment, hours and travel distance. The factors are analysis-year specific:

| factor | 2019 | 2022 |
|:---|:---|:---|
| `Commute` | 0.5719 | 0.6343 |
| `Visitor travel` | 0.5348 | 0.5740 |

**Anaesthetic and pMDI** keep their Dutch factors (0.67 and 0.45) only for the
non-climate columns, which are all zero. Their climate values are Danish
measurements that replace the scaled Dutch ones outright:

| item | value | source |
|:---|:---|:---|
| anaesthetic, N2O term | 38 t N2O/yr × 273 kg CO2-eq/kg | Denmark's National Inventory Document 2024 (DCE report 622) category 2.G.3.a, characterised on AR6 GWP-100, the same factor the MRIO climate row uses |
| anaesthetic, volatile agents | sevoflurane, desflurane and isoflurane litres sold | the Danish Medicines Agency register (ATC N01AB), via `../dk_medicines_register/dk_atc_sales_<year>.csv`; densities from Laster, Fang & Eger (1994), GWP-100 from Sulbaek Andersen, Nielsen & Sherman (2023); sevoflurane reduced 5 % for the metabolised fraction |
| `pMDI` | 12.8 kt (2019), 11.6 kt (2022) | Vestbo & Press-Kristensen (2023) HFC dispensed × ReCiPe 2016 GWP-100 for 2019; the Danish EPA F-gas inventory's own MDI figure for 2022 |

The two anaesthetic terms sum to the 11.572 kt this file carries. The hospital
N2O inside Statistics Denmark's direct-emissions figure is subtracted where that
figure is built (`../dst_supply_use/dk_data_2025.csv`), so there is no double
counting.

## Caveats

**The `(total)` rows are not independent.** Each is the sum of its `(direct)` and
`(indirect)` rows. A consumer that sums the `Source` column triple-counts
commuting and visitor travel.

**Known defect: one file for every analysis year.** This table is overwritten on
every run and the `2025` in its name is an edition marker, not a year of data, so
a 2019 run leaves 2019 values in the file a 2022 run then reads. Every value in it
is analysis-year specific — both scaling factors and both medical-gas values
differ between 2019 and 2022 — which makes it the file in this layer where the
defect matters most. It is recorded in `../readme.md` as well.
