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
| `dk_bottomup_data_2019.txt` | `nl_bottomup_data.txt` | every impact column of the four sources multiplied by its 2019 Danish/Dutch factor; the `(total)` rows recomputed from their scaled `(direct)` and `(indirect)` rows rather than scaled directly; the two medical-gas climate values then **replaced** by Danish primary values; `ISO2` set to `DK` | 8 × 7 | 481 B |
| `dk_bottomup_data_2022.txt` | the same | the same, on the 2022 factors and the 2022 Danish values | 8 × 7 | 480 B |

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
figure is built (`../dst_supply_use/dk_data_<year>.csv`), so there is no double
counting.

## Caveats

**The `(total)` rows are not independent.** Each is the sum of its `(direct)` and
`(indirect)` rows. A consumer that sums the `Source` column triple-counts
commuting and visitor travel.

**Fixed defect: one file for every analysis year.** There used to be a single
`dk_bottomup_data_2025.txt`, overwritten on every run, with `2025` an edition
marker and not a year of data — so a 2019 run left 2019 values in the file a 2022
run then read. This was the file in the layer where that mattered most, because
**every** value in it is analysis-year specific: both scaling factors and both
medical-gas values differ between the two years, so there was no row a wrong-year
read could be harmless in. The two years now sit in two files, resolved by
`paths.silver_dk_bottomup_txt(year)`. Verified by a 2022 → 2019 → 2022 round
trip, which left the 2022 file untouched by the 2019 run and the 2022 gold tables
byte-identical.

## `dk_bottomup_data_2016.txt`

The 2016 row of the bottom-up inventory, built by the same scaling as 2019 and
2022 and from Denmark's own sources throughout. Every parameter was retrieved
rather than assumed, and each reproduces the published value for 2019 and 2022
before being applied to 2016:

| parameter | 2016 | source |
|:---|:---|:---|
| Health and social care employment | 501,258 | Statistics Denmark NABB69, `Employment (number)`, industries 86000 + 87880 |
| Employment ratio against the Dutch base | 0.41061 | ÷ 1,220,750, the CBS figure Steenmeijer et al. use |
| Actual weekly hours | 34.4 / 29.2 | the study's constant, as for 2019 and 2022 |
| Commuting distance | 9.7 km/person/day | TU årsrapport Danmark 2016, Tabel 20, `Arbejdspl.` column |
| **Commute factor** | **0.5955** | the product of the three |
| **Patient and visitor factor** | **0.5166** | employment ratio × the 1.258097 distance uplift |
| Travel, purpose `Social/sundhed` | 0.7 km/person/day | TU årsrapport Danmark 2016, Tabel 15 |
| Population aged 6 and over | 5,346,887 | Statistics Denmark FOLK1A, total less ages 0-5 |
| Sevoflurane / desflurane / isoflurane | 3,228 / 478 / 30 L | medstat.dk `2016_atc_code_data.txt`, ATC N01AB08 / 07 / 06 |
| Nitrous oxide | 38 t | Denmark's National Inventory Document 2024, constant 2013-2022, so 2016 is covered directly |
| pMDI propellant | 5.5 t HFC-134a | Miljøstyrelsen, *Danish consumption and emission of F-gases*, Environmental Project 1979 (2018) |

Three of these deserve a reader's attention.

**The TU 2016 annual report is not linked from DTU's publication page**, which
lists 2017 onwards. It exists at the same URL pattern as its successors
(`tu_danmark_2016_n.pdf`) and is cached here as `tu_danmark_2016.pdf`.

**The commuting distance for 2019 was 9.0 km/person/day in this study until
2026-09-11 and is now 9.1**, the figure the TU 2019 report's Table 20 and Table
15 both carry; 9.0 appears in neither. The commute factor moves 0.5719 to 0.5783
and commuting rises 1.1 %. 2022's 9.3 reproduces exactly.

**The pMDI figure is the weakest of the 2016 parameters.** The Danish EPA reports
5.5 t of HFC-134a and separates no HFC-227ea for MDI that year, so the 227ea
share is imputed at 2019's 90/10 split, giving 6.11 t and 10.88 kt CO₂-eq on the
same ReCiPe 2016 factors. The EPA's own 5.5 t is itself an estimate carried
forward from 2015 by a 10 % reduction, because the Danish Medicines Agency
changed its database format that year. The same method applied to 2019's 7.2 t
returns 12.82 kt against the 12.8 kt published, which is the check on it.
