# Data acquisition register

## Status codes

- `READY_DOWNLOAD`
- `VERIFY_DOWNLOAD`
- `CONTACT_SENT`
- `REQUEST_REQUIRED`
- `CONTROLLED_ACCESS`
- `ACQUIRED`
- `DEFERRED`

## Register

| ID | Dataset | Provider | Access | Main years | Resolution / key variables | Model role | Target table | Next action |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| DK_ECON_001 | Full working SUT | Statistics Denmark | CONTROLLED | 2019, 2022 requested | ~2,350 products × 117 industries | domestic economic backbone | `fact_io_flow` | Email Peter Rørmose Jensen |
| DK_ECON_002 | 117-industry IOT / NAIO1-4 | Statistics Denmark | OPEN | current historical series | 117 industries | prototype domestic IO | `fact_io_flow` | Download now |
| EU_ECON_001 | National SUT T1500/T1600 | Eurostat | OPEN | 2010 onward | A64; voluntary A88 | open SUT fallback | `fact_io_flow` | Download Denmark 2019/2022 |
| EU_ECON_002 | FIGARO 2026 | Eurostat | OPEN | 2010-2024 | 64 industries × 64 products | EU MRIO sensitivity | `fact_mrio_comparison` | Download 2019/2022 |
| DK_HEALTH_001 | SHA1 | Statistics Denmark | OPEN | 2010 onward | HC × HP × HF expenditure | healthcare boundary | `fact_health_expenditure` | Download now |
| DK_GHG_001 | DRIVHUS | Statistics Denmark | OPEN | 1990-2024 | industry × GHG | domestic GHG extension | `fact_environmental_extension` | Download 2019/2022 |
| DK_GHG_002 | DRIVHUS2 | Statistics Denmark | OPEN | current series | direct + allocated energy emissions | direct/energy decomposition | `fact_ghg_species` | Download |
| DK_AIR_001 | MRU1 | Statistics Denmark | OPEN | 1990-2024 | industry × pollutant | air-pollution extension | `fact_environmental_extension` | Download 2019/2022 |
| DK_AIR_002 | EMM1MU2N | Statistics Denmark | OPEN | 1990-2024 | final demand × pollutant × multiplier | IO validation | `fact_footprint_total` | Download 2019/2022 |
| DK_AIR_003 | EMM1MU3N | Statistics Denmark | OPEN | 1990-2024 | producer industry × pollutant × final demand | supplier validation | `fact_supplier_footprint` | Download 2019/2022 |
| DK_WATER_001 | VANDRG2 | Statistics Denmark | OPEN | 2010-2024 | industry × water type | direct water extension | `fact_environmental_extension` | Download |
| DK_WATER_002 | VAN2MU2N | Statistics Denmark | OPEN | 2010-2024 | final demand × direct/indirect water | water IO validation | `fact_footprint_total` | Download |
| DK_WASTE_001 | AFFALD | Statistics Denmark | OPEN | 2011-2023 | industry × waste × treatment | waste extension | `fact_environmental_extension` | Download 2019/2022 |
| DK_WASTE_002 | AFF1MU2N | Statistics Denmark | OPEN | 2011-2023 | final demand × waste × multiplier | waste validation | `fact_footprint_total` | Download |
| DK_WASTE_003 | AFF1MU3N | Statistics Denmark | OPEN | 2011-2023 | producer industry × waste × cause | waste supplier hotspots | `fact_supplier_footprint` | Download |
| DK_MAT_001 | MRM2 | Statistics Denmark | OPEN | 1993-2024 | material categories | national material benchmark | `fact_environmental_extension` | Download |
| DK_MAT_002 | RME1 | Statistics Denmark | OPEN | 2008-2024 | raw material equivalents | resource-footprint denominator | `fact_national_share` | Download |
| DK_LAND_001 | AREALAN1 | Statistics Denmark | OPEN | limited | broad industry × land | domestic land check | `fact_environmental_extension` | Low priority |
| DK_CF_001 | AFTRYK1 | Statistics Denmark | OPEN | 1990-2024 | final use × emitting industry × country | consumption GHG/geography validation | `fact_geographic_footprint` | Download |
| DK_PHARMA_001 | Medstat | Danish Health Data Authority | OPEN | historical/current | ATC/product aggregates | exploratory pharma | `fact_bottomup_source` | Inspect/export relevant pMDIs |
| DK_PHARMA_002 | Custom aggregate medicine extract | Danish Health Data Authority | REQUEST | 2019, 2022 | ATC × product × provider × quantity/value | pharma/pMDI hybrid | `fact_bottomup_source` | Draft request |
| DK_PHARMA_003 | LSR / LMDB | Health Data Authority / Statistics Denmark | CONTROLLED | long series | detailed sales/delivery | advanced pharma | `fact_bottomup_source` | Use only if aggregate extract insufficient |
| DK_PHARMA_004 | Hospital procurement | Amgros | REQUEST | 2019, 2022 | products, quantities, values | validation/procurement | `fact_bottomup_source` | Contact after gap analysis |
| DK_TRAVEL_001 | TU | DTU | OPEN/REQUEST | 2006-2025 | mode × purpose × distance | travel model | `fact_bottomup_source` | Determine healthcare-purpose coverage |
| DK_GAS_001 | Anaesthetic gas procurement/use | Regions/hospitals | REQUEST | 2019, 2022 | gas × hospital × quantity | direct clinical GHG | `fact_bottomup_source` | Targeted investigation |
| MRIO_001 | EXIOBASE 3.10.2 | EXIOBASE consortium | MRIO | 2019, 2022 | 49 regions; 163 industries; 200 products | main environmental MRIO sensitivity | `fact_mrio_comparison` | Download/cite fixed DOI |
| MRIO_002 | GLORIA | IELab / UNEP IRP | MRIO | 2019 preferred | release-dependent 97/120 sectors; 164 regions | resource/material MRIO sensitivity | `fact_mrio_comparison` | Register and freeze exact release |
| MRIO_003 | Eora | University of Sydney | MRIO | 2019; Lenzen comparison | full country-specific classification | Lenzen replication | `fact_mrio_comparison` | Obtain academic access |
| MRIO_004 | OECD ICIO 2025 | OECD | OPEN | 1995-2022 | 80 economies + RoW; 50 industries | trade-structure sensitivity | `fact_mrio_comparison` | Download 2019/2022 |
| MRIO_005 | FIGARO 2026 | Eurostat | OPEN | 2010-2024 | 64 × 64 | EU sensitivity | `fact_mrio_comparison` | Download |

---

# Source registry fields to store

Every acquired dataset should create one row in `dim_source` containing:

```text
source_key
provider
dataset_code
dataset_name
access_class
access_route
source_url
license_or_terms
reference_year
release_version
download_date
raw_redistributable
application_required
application_status
data_controller
target_fact_or_bridge
quality_notes
```

For MRIO data additionally store:

```text
mrio_release
sector_schema_version
region_schema_version
economic_data_status
environmental_extension_version
gwp_version
```

For controlled data additionally store:

```text
project_number
allowed_users
output_control_rules
expiry_date
raw_export_allowed
```

---

# Immediate acquisition sprint

## Sprint 1: open Danish backbone

Acquire:

- NAIO1-4;
- SHA1;
- DRIVHUS;
- MRU1;
- EMM1MU2N;
- EMM1MU3N;
- VANDRG2;
- VAN2MU2N;
- AFFALD;
- AFF1MU2N;
- AFF1MU3N;
- MRM2;
- RME1;
- AFTRYK1.

## Sprint 2: open international benchmarks

Acquire:

- Eurostat national SUT;
- FIGARO;
- EXIOBASE 3.10.2;
- OECD ICIO.

## Sprint 3: access requests

Send:

1. detailed SUT enquiry;
2. pharmaceutical aggregate-data enquiry;
3. TU detailed-extract enquiry.

## Sprint 4: MRIO sensitivity

Acquire/activate:

- GLORIA;
- Eora.

Freeze all version metadata before calculation.
