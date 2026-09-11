# 19_tables_of_record

**Tables of record**

When a number from this study is quoted in the manuscript, a slide or an email, which file did it come from and is it still the current value?

Method, equations, and verification: [`docs/methods/replications.md`, section 19](../../../../docs/methods/replications.md#r19).

## Conventions

| Item | Convention |
|:---|:---|
| Schema | star schema: dimension columns, then measure and unit |
| Industry / product codes | EXIOBASE codes **without** the `A_` / `C_` prefix |
| Countries | ISO3 (`DNK`, `DEU`, `ROU`) |
| Regions without an ISO3 code | region name (`RoW Europe`, `RoW Africa`, ...) |
| Monetary unit | M.EUR, EXIOBASE basic prices, unless a column says otherwise |
| Provenance | one row per file in `../manifest_lineage.csv` |

## Tables

### `table_01.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Impact category`, `Unit`
- **Measures:** `Health care`, `Per person`, `Danish total`, `Share of national (%)`

### `table_02.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Impact category`, `Unit`
- **Measures:** `2019`, `2022`, `Change (%)`

### `table_03.csv`

- **Rows:** 9
- **Format:** csv
- **Dimensions:** `Activity group`, `Driver`
- **Measures:** `2019 (kt CO₂-eq)`, `2022 (kt CO₂-eq)`, `Change (kt)`

### `table_04.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Impact category`, `Unit`
- **Measures:** `Scope 1`, `Scope 2`, `Scope 3`, `Outside protocol`, `TOTAL`

### `table_05.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Source`, `Model family`, `Capital`
- **Measures:** `Year`, `Mt CO₂-eq`, `t per person`

### `table_06.csv`

- **Rows:** 4
- **Format:** csv
- **Dimensions:** `Basis`, `Comparable`
- **Measures:** `Mt CO₂-eq`, `t per person`, `Share of national (%)`

### `table_07.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Revision`
- **Measures:** `Health care (kt CO₂-eq)`

### `table_08.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Impact category`, `Unit`
- **Measures:** `Capital excluded (headline)`, `Capital as a service flow`, `Capital endogenised`, `Endogenised change (%)`

### `table_10.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Impact category`
- **Measures:** `Deterministic`, `Median`, `2.5th percentile`, `97.5th percentile`, `CV, Tier 2 (%)`, `CV, Tier 1 (%)`

### `table_11.csv`

- **Rows:** 7
- **Format:** csv
- **Dimensions:** `Contributor`
- **Measures:** `Share of variance (%)`

### `table_12.csv`

- **Rows:** 12
- **Format:** csv
- **Dimensions:** `Quantity`, `Unit`
- **Measures:** `Value`

### `table_13.csv`

- **Rows:** 33
- **Format:** csv
- **Dimensions:** `Scenario`, `Material (%)`, `Blue water (%)`, `Land (%)`, `Waste (%)`
- **Measures:** `Climate (%)`

### `table_14.csv`

- **Rows:** 13
- **Format:** csv
- **Dimensions:** `Danish industry`, `EXIOBASE v3.8.2`, `EXIOBASE v3.10.2`
- **Measures:** `National accounts (M.EUR)`

### `table_15.csv`

- **Rows:** 6
- **Format:** csv
- **Dimensions:** `Parameter`, `GSD`, `95 % factor range`, `Basis`
- **Measures:** none

### `tables_of_record_index.csv`

- **Rows:** 14
- **Format:** csv
- **Dimensions:** `title`, `source`, `supersedes`
- **Measures:** `number`, `rows`, `columns`
