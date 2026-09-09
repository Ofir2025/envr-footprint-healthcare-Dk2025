# Denmark health-care environmental footprint replication blueprint

## Scope

This checkpoint synthesises the complete sequential reading of:

1. Eckelman & Sherman (2016), *Environmental Impacts of the U.S. Health Care System and Effects on Public Health*, 14 pages.
2. Lenzen et al. (2020), *The environmental footprint of health care: a global assessment*, 9 pages.
3. Lenzen et al. (2020) supplementary appendix, 76 pages.

It also uses the previously completed Malik et al. (2018) main paper and supplementary appendix and Malik et al. (2021) NSW study as the Australian benchmark.

The Eckelman & Sherman article lists five supporting tables/files. These supporting files are not part of the supplied project corpus, so the main article is fully read but exact reconstruction of its NHE-to-EIOLCA mapping and all numerical supporting tables requires those files.

## Coverage ledger

| Source | Coverage | Status | Missing item |
|---|---|---|---|
| Eckelman & Sherman (2016) | pp. 1-14, abstract, introduction, methods, tables, figures, results, uncertainty, discussion, conclusion, references | Complete | Supporting files S1 File and S1-S5 Tables not supplied |
| Lenzen et al. (2020) main article | pp. 1-9 | Complete | None |
| Lenzen et al. (2020) SI | pp. 1-76 | Complete | None |
| Malik et al. (2018) main + SI | Previously completed | Complete | Full 15×360 concordance not printed |
| Malik et al. (2021) | Previously completed | Complete for main article | Separate online SI not supplied |

---

# 1. Core input-output equations

Let:

- \(T\) = intermediate transaction matrix;
- \(y\) = total final demand;
- \(y_H\) = health-care final-demand vector;
- \(x\) = total output;
- \(Q\) = environmental satellite account;
- \(\hat{x}\) = diagonal matrix of total output.

Then:

\[
x=T\mathbf{1}+y
\]

\[
A=T\hat{x}^{-1}
\]

\[
L=(I-A)^{-1}
\]

\[
q=Q\hat{x}^{-1}
\]

\[
F=qLy_H
\]

where \(F\) is the vector of environmental footprints.

For a particular environmental indicator \(k\):

\[
F_k=\sum_i\sum_j q_{k i}L_{ij}y_{H,j}
\]

A detailed contribution cell is:

\[
f_{kij}=q_{ki}L_{ij}y_{H,j}
\]

This cell is the basis for sector, product, geography and supply-chain hotspot tables.

## Production-layer decomposition

Because

\[
L=I+A+A^2+A^3+\cdots
\]

the layer-\(n\) footprint is:

\[
F^{(n)}=qA^ny_H
\]

with:

- \(n=0\): on-site/direct;
- \(n=1\): immediate suppliers;
- \(n=2\): suppliers of suppliers;
- \(n\ge3\): deeper supply chain.

Cumulative share through layer \(m\):

\[
S_m=
\frac{\sum_{n=0}^{m}F^{(n)}}{F}
\]

Truncation error at layer \(m\):

\[
TE_m=1-S_m
\]

## Normalised national share

For a consistently defined national footprint denominator:

\[
Share_{H,k}=100\frac{F_{H,k}}{F_{DK,k}}
\]

The denominator should be computed using the same accounting boundary and environmental extension as the numerator.

## Per-capita footprint

\[
F_{pc,k}=\frac{F_{H,k}}{Population}
\]

## Environmental intensity of health expenditure

\[
I_{H,k}=\frac{F_{H,k}}{E_H}
\]

where \(E_H\) is total health expenditure in DKK.

## GHG by gas species

\[
GHG_g^{CO_2e}=M_g\times GWP_g
\]

and

\[
GHG_{total}=\sum_g GHG_g^{CO_2e}
\]

The GWP time horizon and assessment report used must be stored as model metadata.

## LCIA and health damage, following the logic of Eckelman & Sherman

Inventory-to-impact conversion:

\[
Impact_c=\sum_s CF_{c,s}E_s
\]

where \(E_s\) is the quantity of elementary flow \(s\) and \(CF_{c,s}\) is the characterisation factor for impact category \(c\).

Where a robust endpoint factor exists:

\[
DALY_c=Impact_c\times DF_c
\]

Total quantified health damage:

\[
DALY_{total}=\sum_c DALY_c
\]

Do not calculate a total DALY value for categories without defensible endpoint characterisation.

## Uncertainty

For Monte Carlo draw \(p\):

\[
F_p=Q_p\hat{x}_p^{-1}
\left(I-T_p\hat{x}_p^{-1}\right)^{-1}y_{H,p}
\]

Positive monetary and environmental inputs can be perturbed in log space:

\[
\sigma_{\log_{10}z}
\approx
\log_{10}\left(\frac{z+\sigma_z}{z}\right)
\]

Report:

\[
CV=100\frac{\sigma_F}{\bar{F}}
\]

as well as percentiles or a stated confidence/credible interval.

---

# 2. What Eckelman & Sherman add

## Method

They use U.S. National Health Expenditure categories over 2003-2013, map those categories to a 428-sector 2002 U.S. EIOLCA producer model, apply environmental extensions, use EPA TRACI midpoint characterisation, and for selected effects translate impacts to DALYs using IMPACT2002+ endpoint factors.

The model therefore has three analytical layers:

\[
\text{health expenditure}
\rightarrow
\text{supply-chain emissions}
\rightarrow
\text{environmental impacts}
\rightarrow
\text{selected health damages}
\]

This last step is absent from the Malik Australian carbon study.

## 2013 KPIs

Reported national shares include approximately:

- GHG: 9.8%;
- acidification: 11.7%;
- particulate-matter respiratory burden: 8.9%;
- smog: 10.0%;
- eutrophication: 1.5%;
- ozone depletion: 1.6%;
- carcinogenic toxicity: 1.0%;
- non-carcinogenic toxicity: 2.2%.

The paper estimates 470,000 DALYs from the selected pollutant categories, or about 405,000 DALYs after an illustrative adjustment for changes in power-generation emissions.

## High-value design lesson

Store both:

- demand-side attribution: hospital care, physician/clinical services, prescription drugs, etc.;
- supply-side attribution: electricity generation, construction, chemicals, waste management, medical-instrument manufacturing, etc.

These are different questions and should never be collapsed into one category dimension.

---

# 3. What Lenzen et al. add

## Global MRIO

Lenzen et al. use Eora v199.82 with 189 countries and 14,838 country-sector pairs.

Their environmental footprint is:

\[
F=qLy_H
\]

for 13 satellite rows representing seven reported environmental stressor families:

- seven greenhouse-gas species;
- particulate matter;
- NOx;
- SO2;
- malaria risk;
- reactive nitrogen in water;
- scarce water use.

## Key 2015 global results

Reported global health-care footprints include approximately:

- 2.4 Gt CO2e;
- 3.4 Mt PM;
- 5.5 Mt NOx;
- 6.1 Mt SO2;
- 0.8 million people malaria risk;
- 1.4 Mt reactive nitrogen;
- 7.3 TL scarce water.

Global shares include 4.4% of GHG, 2.8% of PM, 3.4% of NOx and 3.6% of SO2.

## Supply-chain convergence KPI

The supplementary appendix shows why a direct-only footprint is inadequate.

For GHG:

- direct health-care emissions were about 1 Gt CO2e;
- total footprint about 2.4 Gt CO2e;
- direct-only truncation is therefore about 60%;
- even direct + first-order suppliers leaves about 30% uncounted.

This suggests a valuable Danish KPI:

\[
TE_m=1-\frac{\sum_{n=0}^{m}F^{(n)}}{F}
\]

for \(m=0,1,2,\ldots\).

## GHG composition KPI

The SI reports the global GHG footprint in CO2e as approximately:

- CO2: 51.87%;
- CH4: 16.05%;
- N2O: 21.94%;
- HFC: 2.75%;
- CFC: 4.75%;
- SF6: 1.50%;
- NF3: 1.15%.

A Denmark replication should retain gas species rather than storing GHG only as a single CO2e aggregate.

## Efficiency versus spending

Lenzen et al. show that environmental intensity can decline while the absolute footprint rises because expenditure grows faster than efficiency improves.

A Danish dashboard should therefore always show:

1. absolute footprint;
2. per-capita footprint;
3. footprint per DKK;
4. health expenditure;
5. activity/output if available.

---

# 4. Danish data architecture

## Highest-priority national sources

### Economic core

**Statistics Denmark national accounts SUT/IOT**

The national supply-use system is balanced at roughly 2,350 products and 117 industries. The published symmetric IOT has 117 industries, while the most detailed product-level SUT is available through Statistics Denmark Research Service because detailed relationships are confidential.

Important health-related industry codes in current national accounts include:

- 210000 Pharmaceuticals;
- 320010 Manufacture of medical instruments, etc.;
- 860010 Hospital activities;
- 860020 Medical and dental practice activities;
- 870000 Residential care activities;
- 880000 Social work activities without accommodation.

Private-consumption health categories include:

- 6111 Medical and pharmaceutical products;
- 6112 Therapeutic appliances and equipment;
- 6200 Out-patient services;
- 6300 Hospital services.

### Health expenditure

**Statistics Denmark SHA1**

Dimensions:

- 44 health functions;
- 34 providers;
- 8 financing schemes;
- current-price expenditure;
- annual observations.

Use SHA1 to define the System of Health Accounts boundary and control totals.

Do not simply add SHA1 to national-accounts health final demand. The two systems must first be reconciled to avoid double counting.

### Direct GHG and air pollutants

**DRIVHUS / DRIVHUS2**

Industry GHG accounts.

**MRU1**

Air emissions by industry for 15 emission types.

**EMM1MU1N / EMM1MU2N / EMM1MU3N**

Statistics Denmark already publishes direct/indirect air-emission multipliers and final-demand-attributed emissions. These are extremely useful as independent replication checks of a custom Leontief implementation.

### Water

**VANDRG1 / VANDRG2**

Physical water abstraction and consumption by industry and water type.

**VAN2MU2N**

Direct and indirect water consumption by final demand, including a multiplier per million DKK.

This is a domestic-water-accounting benchmark. For *scarce water* embodied in imports, a global MRIO plus region-specific scarcity characterisation is still required.

### Waste

**AFFALD**

Waste generation by industry, treatment and 48 waste categories.

**AFF1MU2N / AFF2MU2N / AFF3MU2N**

Direct/indirect waste by final demand, waste fraction, treatment or hazardousness.

**AFF1MU3N / AFF2MU3N / AFF3MU3N**

Producer-industry attribution of waste caused by final demand.

### Materials

**MRM2**

Economy-wide material flow accounts.

For detailed physical product flows, Statistics Denmark also maintains detailed material-flow physical supply-use accounts.

These accounts are useful for domestic extraction/material-use validation, but a global material footprint of Danish health care still requires an MRIO extension.

### Consumption-based climate benchmark

**AFTRYK1**

Statistics Denmark's experimental climate footprint of Danish consumption provides:

- type of use;
- emitting industry;
- emitting country;
- annual CO2e.

This can be used as a national consumption-footprint denominator and as a geographic-origin validation dataset.

### Medicines and clinical gases

**Danish Health Data Authority, Lægemiddelstatistikregisteret / Medstat**

The register covers essentially all pharmaceutical sales and deliveries in Denmark, including pharmacies and hospital supplies.

Use ATC/product/package information to estimate specific high-GWP sources such as pMDIs where reliable per-unit emission factors exist.

For anaesthetic gases, combine hospital procurement/clinical-use data with gas-specific GWP factors. Do not infer N2O use solely from monetary expenditure if physical activity data can be obtained.

### Patient and staff travel

**DTU Danish National Travel Survey (Transportvaneundersøgelsen, TU)**

Use mode, distance and trip-frequency distributions as national mobility priors. For health-specific travel, supplement with regional/hospital survey or administrative data.

### Territorial national GHG denominator

**DCE/Aarhus University National Inventory Document**

Use the UNFCCC/Paris inventory when the question is territorial emissions.

Do not divide a consumption-based MRIO numerator by a territorial UNFCCC denominator without explicitly labelling the mixed boundary.

---

# 5. Recommended Denmark model

The preferred design is a nested hybrid:

\[
\boxed{
\text{Danish detailed SUT}
+
\text{SHA health boundary}
+
\text{Danish environmental accounts}
+
\text{global MRIO for imports}
+
\text{bottom-up clinical sources}
}
\]

This is stronger than mapping only three Danish expenditure groups into three broad EXIOBASE sectors because it preserves Denmark-specific purchasing structure before linking imports to global production systems.

## Domestic block

Build the Danish product-by-industry SUT block first.

Use the SUT rather than the 117-sector symmetric IOT whenever detailed Research Service access is available.

The SUT is the best place to distinguish pharmaceutical products, medical equipment, hospital services, outpatient services and other health-related products before aggregation destroys detail.

## Foreign block

Link imported products to an MRIO such as EXIOBASE, OECD ICIO or Eora through a product/industry concordance.

Domestic impacts can use Danish official environmental accounts.

Imported impacts use region-specific MRIO extensions.

This prevents Denmark's relatively clean domestic electricity mix from being incorrectly applied to foreign production.

## Bottom-up replacement/addition

Use physical data for sources that monetary IO models represent poorly:

- anaesthetic gases;
- pMDI propellants;
- staff commuting;
- patient and visitor travel;
- selected high-value pharmaceuticals/devices when process data are available.

For every bottom-up item, store an explicit overlap flag indicating which MRIO expenditure/flow was removed or adjusted to prevent double counting.

---

# 6. Result packages and star-schema design

## Shared dimensions

| Dimension | Primary key | Essential attributes |
|---|---|---|
| dim_time | time_key | year, price_year, calendar/financial year |
| dim_geography | geography_key | country, region, municipality, origin/destination flag |
| dim_industry | industry_key | DB07/NACE/ISIC code, name, hierarchy |
| dim_product | product_key | SUT product code, CPA/COICOP mapping, description |
| dim_health_function | health_function_key | SHA HC code and name |
| dim_provider | provider_key | SHA HP code and name |
| dim_financing | financing_key | SHA HF code and name |
| dim_impact | impact_key | indicator, midpoint/endpoint, unit, method/version |
| dim_gas_flow | flow_key | elementary flow/gas, CAS where applicable, GWP/CF version |
| dim_supply_layer | layer_key | direct, first order, second order, higher order |
| dim_price_basis | price_key | current/constant, basic/purchaser, currency |
| dim_scenario | scenario_key | baseline, sensitivity, hybrid variant, MRIO version |
| dim_source | source_key | institution, table ID, dataset version, extraction date |
| dim_scope | scope_key | territorial/consumption, capital included, travel included, etc. |

## P01: health expenditure

**fact_health_expenditure**

Grain:
one observation per year × health function × provider × financing scheme × product/industry mapping × price basis.

Fields:

- expenditure_id PK
- time_key FK
- health_function_key FK
- provider_key FK
- financing_key FK
- product_key FK nullable
- industry_key FK nullable
- price_key FK
- source_key FK
- amount_dkk
- mapping_weight
- is_health_boundary
- quality_flag

## P02: IO monetary system

**fact_io_flow**

Grain:
one supplying node × using node × year × valuation.

Fields:

- io_flow_id
- time_key
- supplier_industry_key / supplier_product_key
- user_industry_key
- geography_key
- price_key
- source_key
- value_dkk
- domestic_import_flag
- valuation_component

## P03: environmental extensions

**fact_environmental_extension**

Grain:
one environmental flow × producing industry × geography × year.

Fields:

- extension_id
- time_key
- geography_key
- industry_key
- flow_key
- impact_key
- source_key
- physical_quantity
- output_dkk
- direct_intensity_per_dkk
- uncertainty_sd

## P04: headline footprint

**fact_footprint_total**

Grain:
one year × impact × scenario × scope.

Fields:

- footprint_id
- time_key
- impact_key
- scenario_key
- scope_key
- value
- unit
- sd
- p025
- p975
- national_total_same_boundary
- national_share_pct
- population
- per_capita_value
- health_expenditure_dkk
- intensity_per_dkk

## P05: demand-side health-category contribution

**fact_health_category_footprint**

Grain:
one health function/provider/product × impact × year.

Measures:

- footprint_value
- share_of_health_footprint_pct
- expenditure_dkk
- footprint_per_dkk

## P06: supply-side sector hotspot

**fact_supplier_footprint**

Grain:
one producing industry × origin geography × impact × year.

Measures:

- footprint_value
- share_pct
- direct_or_indirect_flag

This answers a different question from P05.

## P07: production layers and truncation

**fact_production_layer**

Fields:

- time_key
- impact_key
- layer_key
- geography_key
- scenario_key
- footprint_value
- cumulative_footprint
- cumulative_share_pct
- truncation_error_pct

## P08: geographic displacement

**fact_geographic_footprint**

Fields:

- consuming_geography_key
- producing_geography_key
- impact_key
- time_key
- footprint_value
- domestic_share_pct
- foreign_share_pct
- eu_share_pct
- non_eu_share_pct

## P09: GHG species

**fact_ghg_species**

Fields:

- time_key
- flow_key
- scope_key
- mass
- mass_unit
- gwp_value
- gwp_version
- co2e_value
- share_of_total_ghg_pct

## P10: time trends and efficiency

**fact_footprint_trend**

Fields:

- time_key
- impact_key
- total_footprint
- per_capita_footprint
- health_expenditure_dkk
- footprint_intensity_per_dkk
- population
- index_base100
- yoy_change_pct

## P11: national-normalised indicators

**fact_national_share**

Fields:

- time_key
- impact_key
- health_footprint
- national_footprint
- denominator_boundary
- health_share_pct

Never leave `denominator_boundary` implicit.

## P12: uncertainty

**fact_uncertainty_run**

Grain:
one Monte Carlo draw × scenario × impact × year.

Fields:

- run_id
- time_key
- impact_key
- scenario_key
- footprint_value
- seed
- perturbation_model
- q_uncertainty_version
- t_uncertainty_version
- y_uncertainty_version

A summary table can contain mean, SD, CV and percentiles.

## P13: environmental health damages

**fact_health_damage**

Fields:

- time_key
- impact_key
- elementary_flow
- footprint_inventory_value
- characterization_method
- midpoint_value
- endpoint_method
- daly_value
- daly_per_billion_dkk
- uncertainty_lower
- uncertainty_upper
- endpoint_validity_flag

Only populate DALY when a defensible endpoint model exists.

## P14: bottom-up clinical sources

**fact_bottomup_source**

Fields:

- time_key
- provider_key
- activity_type
- activity_quantity
- activity_unit
- emission_factor
- factor_unit
- footprint_value
- impact_key
- source_key
- overlap_io_sector_key
- io_amount_removed_or_adjusted
- double_counting_rule
- uncertainty_sd

---

# 7. Minimum KPI set for a Denmark publication

## Core accounting KPIs

1. Total environmental footprint by impact.
2. Share of the Danish national footprint using a matched denominator.
3. Footprint per capita.
4. Footprint per DKK of health expenditure.
5. Direct versus supply-chain share.
6. Health-demand-category contributions.
7. Supplying-industry contributions.
8. Geographic origin, Denmark/EU/non-EU.
9. Production-layer convergence and truncation.
10. GHG composition by gas species.
11. Imported-share / displaced-impact share.
12. Monte Carlo uncertainty and model sensitivity.

## Public-health extension from Eckelman

13. PM2.5-related DALYs attributable to the health-care supply chain.
14. Smog/ozone-related DALYs where the selected LCIA model supports them.
15. Human-toxicity damage only with high caution and explicit uncertainty.
16. DALYs per billion DKK of healthcare expenditure.

## Health-system performance extension suggested by Lenzen

17. Environmental footprint per inpatient episode.
18. Environmental footprint per outpatient contact.
19. Environmental footprint per quality-adjusted health output if a defensible health-output denominator is selected.
20. Footprint intensity versus health outcomes/quality indicators.
21. Avoidable/low-value-care footprint as a future scenario, not as a direct IO observation.

---

# 8. Key comparison

| Feature | Malik 2018 | Malik 2021 NSW | Eckelman & Sherman 2016 | Lenzen et al. 2020 |
|---|---|---|---|---|
| Geography | Australia | NSW + 8 Australian regions | USA | 189-country MRIO |
| Time | 2014-15 | 2017 | 2003-13 | 2000-15 |
| Health demand | 15 AIHW categories | 16 health sectors + NSW expenditure | NHE categories | health sectors embedded in Eora |
| Main impacts | GHG | GHG, water, waste | 9 LCIA categories | 7 environmental stressor families |
| Global supply chains | Limited/unclear | imports excluded | no full MRIO geography | yes |
| DALY endpoint | no | no | yes, selected categories | no direct DALY attribution |
| Production layers | no | yes | no | yes, extensively |
| GHG species | aggregated | aggregated | aggregated GHG | explicit gas species |
| Time drivers | no | no | static intensity + spending trend | expenditure/efficiency + regression |
| Uncertainty | Monte Carlo | limited in main paper | qualitative/sensitivity | Monte Carlo using Eora SDs |
| Main unique contribution | purchaser-price bridge | regional multi-impact PLD | pollution → public health damage | global trade, convergence, intensity, elasticity |

---

# 9. Important source inconsistencies to retain

## Lenzen Denmark 2015

The supplementary appendix contains two Denmark carbon values that should not be silently combined:

- uncertainty Table SI 7.1: 2.84 ± 0.24 Mt CO2e;
- detailed 2015 Table SI 10.1: 3.37 Mt CO2e.

The supplied SI text does not provide an obvious explanation for the difference. Treat it as an internal reporting/version issue requiring author/data verification before using the uncertainty from SI 7.1 with the SI 10.1 central value.

Table SI 10.1 also reports Denmark:

- population 5.69 million;
- health expenditure US$16.93 billion;
- total GHG 3.37 Mt CO2e.

Table SI 10.2 reports 0.59 t CO2e per capita.

Table SI 10.3 reports health care at 3.78% of Denmark's national GHG footprint.

Table SI 10.4 reports a total GHG multiplier of approximately 0.20 kg CO2e per US$.

These values are model results from Eora and are not equivalent to a Denmark-specific SUT/SHA model.

---

# 10. Main recommendation

A Denmark replication should not copy one paper mechanically.

Use:

- Malik 2018 for the health-expenditure bridge and purchaser-price discipline;
- Malik 2021 for health-sector disaggregation and production-layer decomposition;
- Eckelman & Sherman for multi-pollutant LCIA, demand/supply dual attribution and selected DALY endpoints;
- Lenzen 2020 for global imports, geographical displacement, GHG-species decomposition, convergence/truncation, time-series efficiency analysis and uncertainty.

The most defensible architecture is therefore:

\[
\boxed{
\text{Statistics Denmark SUT/SHA}
\rightarrow
\text{Danish domestic EEIO}
\rightarrow
\text{MRIO import extension}
\rightarrow
\text{clinical bottom-up corrections}
\rightarrow
\text{multi-impact + health-damage analytics}
}
\]

This gives a Denmark-specific model without losing the global supply-chain completeness that is the main strength of Lenzen et al.

