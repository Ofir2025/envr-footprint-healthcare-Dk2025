# 19_tables_of_record

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
- **Dimensions:** `Unit`
- **Measures:** `Impact category`, `Health care`, `Per person`, `Danish total`, `Share of national (%)`

### `table_02.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Unit`
- **Measures:** `Impact category`, `2019`, `2022`, `Change (%)`

### `table_03.csv`

- **Rows:** 9
- **Format:** csv
- **Dimensions:** `Activity group`
- **Measures:** `2019 (kt CO₂-eq)`, `2022 (kt CO₂-eq)`, `Change (kt)`, `Driver`

### `table_04.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Unit`
- **Measures:** `Impact category`, `Scope 1`, `Scope 2`, `Scope 3`, `Outside protocol`, `TOTAL`

### `table_05.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Source`, `Model family`
- **Measures:** `Year`, `Mt CO₂-eq`, `t per person`, `Capital`

### `table_06.csv`

- **Rows:** 4
- **Format:** csv
- **Dimensions:** `Basis`
- **Measures:** `Mt CO₂-eq`, `t per person`, `Share of national (%)`, `Comparable`

### `table_07.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Vintage`
- **Measures:** `Health care (kt CO₂-eq)`

### `table_08.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** `Unit`
- **Measures:** `Impact category`, `Capital excluded (headline)`, `Capital as a service flow`, `Capital endogenised`, `Endogenised change (%)`

### `table_10.csv`

- **Rows:** 5
- **Format:** csv
- **Dimensions:** none
- **Measures:** `Impact category`, `Deterministic`, `Median`, `2.5th percentile`, `97.5th percentile`, `CV, Tier 2 (%)`, `CV, Tier 1 (%)`

### `table_11.csv`

- **Rows:** 7
- **Format:** csv
- **Dimensions:** none
- **Measures:** `Contributor`, `Share of variance (%)`

### `table_12.csv`

- **Rows:** 12
- **Format:** csv
- **Dimensions:** `Quantity`, `Unit`
- **Measures:** `Value`

### `table_13.csv`

- **Rows:** 33
- **Format:** csv
- **Dimensions:** `Scenario`
- **Measures:** `Climate (%)`, `Material (%)`, `Blue water (%)`, `Land (%)`, `Waste (%)`

### `table_14.csv`

- **Rows:** 13
- **Format:** csv
- **Dimensions:** `Danish industry`
- **Measures:** `National accounts (M.EUR)`, `EXIOBASE v3.8.2`, `EXIOBASE v3.10.2`

### `table_15.csv`

- **Rows:** 6
- **Format:** csv
- **Dimensions:** `Parameter`, `Basis`
- **Measures:** `GSD`, `95 % factor range`

### `tables_of_record_index.csv`

- **Rows:** 14
- **Format:** csv
- **Dimensions:** `source`
- **Measures:** `number`, `title`, `rows`, `columns`, `supersedes`
