# 05_waste_dst_accounts

**05 - Domestic waste from Danish national accounts**

How much waste does Danish health care actually generate, and is the waste indicator inherited from Steenmeijer et al. fit to answer that?

Method, equations, and verification: [`docs/methods/replications/05_waste_dst_accounts.md`](../../../docs/methods/replications/05_waste_dst_accounts.md).

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

### `waste_extension_validation.csv`

- **Rows:** 4
- **Format:** csv
- **Dimensions:** `source`, `quantity`, `basis`
- **Measures:** `value_kt`, `analysis_year`

### `waste_footprint_domestic_dst.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `industry`, `source`
- **Measures:** `analysis_year`, `industry_code`, `expenditure_m_dkk`, `direct_intensity_t_per_mdkk`, `multiplier_t_per_mdkk`, `hazardous_multiplier_t_per_mdkk`, `direct_waste_t`, `total_waste_t`, `hazardous_waste_t`, `boundary`
