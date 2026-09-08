# Methods by replication layer

One document per gold-output folder, stating the source article, the equations as
they are implemented, the data each needs, the deviations from the source, and the
verification that runs against it.

These are written so that a reader who has the source article open can check our
implementation line by line, and so that a reader who has neither can still
reproduce the calculation. Every equation shown here is the equation in the code;
where the code departs from the published form, the departure is stated in the
*Deviations* section rather than left for the reader to discover.

| # | Layer | Source | Module |
|---|---|---|---|
| [00](00_core_footprint.md) | Core footprint | Leontief (1970); Miller & Blair (2009) | `main_2025`, `extended_indicators`, `national_totals` |
| [01](01_eriksen_replication.md) | Eriksen replication (the manuscript) | Eriksen et al., NXSUST-D-26-01589 | `main_2025`, `eriksen_tables` |
| [02](02_scopes_wood_hertwich.md) | GHG-Protocol scopes | Hertwich & Wood (2018); OECD (2025) | `scopes_detail` |
| [03](03_cabernard_target_scope3.md) | Target-sector scope 3 | Cabernard et al. (2019, 2022) | `cabernard_target_scope3` |
| [04](04_uncertainty_lenzen_ieooc.md) | Monte Carlo uncertainty | Lenzen et al. (2020); Rodrigues et al. (2018) | `uncertainty_2025` |
| [05](05_waste_dst_accounts.md) | Domestic waste from Danish accounts | Statistics Denmark AFF1MU1N / AFF3MU1N | `waste_domestic_dst` |
| [06](06_benchmarks_validation.md) | Benchmarks and consistency audit | Schmidt & Merciai (2023); Eurostat FIGARO | `danish_healthcare_benchmark`, `figaro_benchmarks` |
| [07](07_malik_replication.md) | Malik replication | Malik et al. (2018, 2021) | `malik_replication`, `production_layers` |
| [08](08_lenzen_replication.md) | Lenzen KPI set | Lenzen et al. (2020) | `lenzen_replication` |
| [09](09_vintage_diagnostics.md) | EXIOBASE vintage defects | Rørmose Jensen & Iliev (2022) | `vintage_defect_audit` |
| [10](10_snac_shipping_correction.md) | Shipping reallocation | Rørmose Jensen & Iliev (2022) | `dk_shipping_correction` |
| [11](11_capital_gfcf.md) | Capital endogenisation | Södersten et al. (2018) | `capital_endogenised_sodersten`, `capital_gfcf` |
| [12](12_impact_categories_full.md) | Full impact-category profile | DESIRE FP7 characterisation | `impact_categories_full` |
| [13](13_steenmeijer_replication.md) | Steenmeijer replication | Steenmeijer et al. (2022) | `steenmeijer_replication` |
| [14](14_eckelman_replication.md) | Eckelman replication | Eckelman & Sherman (2016) | `eckelman_replication` |
| [15](15_gwp_vintage.md) | GWP vintage sensitivity | IPCC AR4–AR6 | `gwp_vintage` |
| [16](16_impact_world_plus.md) | IMPACT World+ profile | Bulle et al. (2019); IW+ v2.2.1 | `impact_world_plus` |
| [17](17_health_subsectors.md) | Footprint by SHA function | Malik et al. (2018); OECD SHA 2011 | `health_subsector_footprints` |
| [18](18_mitigation_scenarios.md) | Mitigation scenarios | Danish Klimastatus og -fremskrivning | `mitigation_scenarios` |

## Notation used throughout

| Symbol | Meaning | Shape |
|---|---|---|
| $Z$ | inter-industry transactions, M€ basic prices | 7 987 × 7 987 |
| $x$ | industry gross output, M€ | 7 987 |
| $A = Z\hat{x}^{-1}$ | direct requirements | 7 987 × 7 987 |
| $L = (I-A)^{-1}$ | Leontief inverse (total requirements) | 7 987 × 7 987 |
| $F$ | stressor extension, physical units | 1 113 × 7 987 |
| $S = F\hat{x}^{-1}$ | direct stressor intensities | 1 113 × 7 987 |
| $C$ | characterisation matrix | $k$ × 1 113 |
| $y_H$ | Danish health-care final demand, M€ | 7 987 |
| $s = CS$ | characterised direct intensity, one indicator | 7 987 |
| $f = s L y_H$ | footprint, one indicator | scalar |

A *node* is one (region, industry) pair: 49 regions × 163 industries = 7 987.
Denmark is region index 5 (`DNK`), so the Danish block is rows/columns
$5 \times 163 \dots 6 \times 163 - 1$.
