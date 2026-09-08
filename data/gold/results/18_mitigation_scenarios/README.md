# 18_mitigation_scenarios

**18 — Mitigation scenarios**

Reviewer 2's R2-7: the manuscript identifies hotspots but does not model mitigation. What would plausible Danish decarbonisation actually deliver, and what would it not?

Method, equations and verification: [`docs/methods/replications/18_mitigation_scenarios.md`](../../../docs/methods/replications/18_mitigation_scenarios.md).

## Conventions

| Item | Convention |
|---|---|
| Schema | star schema: dimension columns, then measure and unit |
| Industry / product codes | EXIOBASE codes **without** the `A_` / `C_` prefix |
| Countries | ISO3 (`DNK`, `DEU`, `ROU`) |
| Regions without an ISO3 code | region name (`RoW Europe`, `RoW Africa`, ...) |
| Monetary unit | M.EUR, EXIOBASE basic prices, unless a column says otherwise |
| Provenance | one row per file in `../MANIFEST_lineage.csv` |

## Tables

### `mitigation_scenarios.csv`

- **Rows:** 70
- **Units:** Mm3, km2, kt, kt CO2eq
- **Dimensions:** `country_consuming`, `scenario`, `scenario_type`, `indicator`, `unit`, `note`, `source`, `model`
- **Measures:** `analysis_year`, `ambition`, `baseline`, `change`, `scenario_value`, `change_pct`, `per_capita_change`

### `target_consistency.csv`

- **Rows:** 7
- **Units:** %, kt CO2eq
- **Dimensions:** `quantity`, `unit`, `target`, `basis`
- **Measures:** `value`, `caveat`
