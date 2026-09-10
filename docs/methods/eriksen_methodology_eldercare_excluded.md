# Ofir Eriksen's methodology - eldercare excluded

This is Ofir Eriksen's methodology document. Source file:
`eriksen_methodology_eldercare_excluded.docx`, created 2024-02-22, last
modified 2026-02-05. Converted from Word with `pandoc -f docx -t gfm`; the
original `.docx` is kept alongside this file.

This version explicitly **excludes eldercare (COFOG 10)** from the study
boundary. A separate, shorter methodology note by the same author -
[`eriksen_methodology_eldercare_included.md`](eriksen_methodology_eldercare_included.md)
- instead includes eldercare within EXIOBASE's "Residential care and social
work services". The two are not versions of one document: they describe two
different system-boundary choices, and both are kept.

---

## Scope and aim

This study replicates the Dutch healthcare footprint methodology by Steenmeijer et al., by conducting an Environmentally Extended Input Output Analysis (EEIOA) for the Danish healthcare system. Methodological consistency was prioritized higher than modeling choices to best ensure comparability.

Calculations of emissions were executed through a modified python script that Steenmeijer et al. had uploaded as a GitHub repository. Thank you Steenmeijer et al. for sharing your code by open sourcing it. Modifications and updates to the code can be found on the main author of this study's [Github Repository](https://github.com/Ofir2025/envr-footprint-healthcare-Dk2025).

## Conceptual framework

The approach follows the System of Health Accounts (SHA, 2011 (OECD)) and excludes Gross Fixed Capital Formation (GFCF), Non-Profit Institutions Serving Households (NPISH), and Collective Government Consumption to avoid double counting, ensure methodological consistency, and align with OECD reporting. Elderly care (COFOG 10) was excluded for multiple reasons (see background document @pageX).

## Data sources

Healthcare Expenditure: Danish Supply Use Tables (Transaction codes 3110, 3141, and 3142)

Classification: SHA 2011 (HC.1-HC.9, excluding HC.5)

Global MRIO: Exiobase v3.7 (monetary; industry by industry; 163 sectors, 49 regions; and environmental extensions)

Coding: Modified Python scripts from Steenmeijer et al.'s open-source repository

## Software

Python v3.11 (including several libraries, such as *pandas* and *numpy*)

Visual Studio Code from Microsoft

CoPilot from Microsoft (formulating code snippets, analyzing original code, and grammar checks)

## System boundary

### Included

Household Consumption (3110): co-payments and prescription pharmaceuticals

Marketed Individual Government Consumption (3141): outsourced healthcare services

Non-marketed Individual Government Consumption (3142): direct provision by government institutions

Anaesthetic gasses (N2O) and pMDi's (xDxD@@)

Private travel (commuting, patients, and visitors)

### Excluded

GFCF (infrastructure and durable equipment)

NPISH (Non-Profit Institutions Serving Households, 3130)

Collective government consumption (3200)

COFOG 10 (Elderly care)

## Expenditure vector construction

Healthcare Expenditures was aggregated into three categories based on the System of Health Accounts (SHA, OECD:

- Healthcare services (HC.1-HC.9,excluding HC.5)
- Pharmaceutical products and other medical products (HC.51)
- Therapeutic appliances and equipment (HC.52)

Values were converted from DKK to Millions of Euro (MEUR) at an exchange rate of 7.45 DKK/EUR.

Purchaser price 🡪 basic price conversion stuff still missing

How bout dah: Conversion to basic prices was not deemed necessary, since the Danish Supply Use tables was denominated in basic prices.

The three expenditure categories were classified to corresponding EXIOBASE sectors (also used in the Dutch study):

- HC.1-HC.9 (excl.HC.5) 🡪 Health and Social Work (If transport costs are high, does that mean they spend money on driving, or also the driver? Because there would be a HUGE difference between paying someone to drive, and only paying for the expenses of the vehicles - which would result in much different emissions)
- HC.51 🡪 Chemicals n.e.c (uncertainties: Does Denmark pay the same as other countries, or are subsidies or local discounts included? This would make a huge impact since the calculations are based on monetary data)
- HC.52 🡪 Medical precision and optical instruments

Healthcare Services were scaled based on the consumption patterns from the Exiobase sector 'Health and Social Work, ensuring that the total amount of spending corresponds to the Danish Healthcare expenditures. The two other expenditure categories (HC.51 and HC.52) were distributed across countries of origin in accordance with the trade allocation patterns in Exiobase. In this way, Exiobase's structural patterns are preserved; but they are scaled to reflect actual amounts spent according to Danish SUTs.

## EEIOA calculation

The expenditure vectors determined the amounts spent, and where each EUR was spent. The following steps integrate these spendings with datasets that estimate the effects of the spending:

- Firstly, Leontief inverse captures upstream supply-chain effects, i.e. where and how products and services are produced and transported through suppliers to the Danish Healthcare System.
- Secondly, as all the results were in monetary units they needed to be coupled to Environmental Extensions and characterization factors (Recipe 2016 and DESIRE FP7) for the results to reflect quantifiable environmental effects.

Impacts results were calculated for five categories:

- Climate change (kt Co2e)
- Abiotic material extraction (kt)
- Blue water consumption (Mm3)
- Land use (km2)
- Waste generation (kt)

## Direct emissions

### Nitrous oxide

Data available: Number of births in The Region of Southern Denmark, total number of births in Denmark, and amount of N₂O purchased by the former. The difference in number of births was applied as a scalar to estimate the amount of N₂O purchased on a national level. Uncertainties depend on whether the usage of N₂O is equally distributed across Denmark AND whether number of births can function as a proxy for amount of N₂O purchased. We based the assumption on childbirth being the primary usage of N₂O.

Regional births (Region South): 11,095

National births (Denmark): 58,438

Regional N₂O purchased: 6,063.42 kg

Scalar:

```math
\text{Scalar} = \frac{\text{National births}}{\text{Regional births}} = \frac{58,438}{11,095} \approx 5.267
```

Scaled national N₂O:

```math
6,063.42 \times 5.267 \approx 31,936.38\text{ kg}
```

Converted to GWP (CO₂eq):

```math
31,936.38\text{ kg N₂O} \times \text{GWP factor (≈298)} \approx 9,517,041.29\text{ kg CO₂eq}
```

Dutch value: 14.2ktco2

Scaling factor: 9.52/14.2=0.67

(The calculations maybe fit better in a background document)

### pMDIs

Steenmeijer et al. quantified pMDI-related greenhouse gas emissions for the Netherlands in 2016 at 76.9 kt CO₂-equivalents (GWP100), based on national pharmaceutical consumption data and life-cycle emission factors for inhaler propellants. Defined daily doses (DDD) were used as the harmonised unit of comparison, as this metric reflects actual therapeutic use and avoids confounding from differences in actuation counts or inhaler formats. According to Dutch national pharmaceutical statistics underlying Steenmeijer et al., approximately 62 million pMDI DDD were dispensed in the Netherlands in 2016. Correspondingly, Danish national pharmacy dispensation data indicate that approximately 28 million pMDI DDD were dispensed in Denmark in 2019 (Vestbo & Press-Kristensen, 2023).

The difference in emissions between pMDIs and alternative inhaler devices is **substantial**, with per-device differences of approximately one order of magnitude, depending on calculation method. Consequently, total pMDI-related emissions were scaled according to the number of pMDI doses dispensed, under the assumption that emissions from alternative inhaler types are negligible in comparison.

Despite Denmark having a substantially higher dry-powder inhaler (DPI) uptake than the Netherlands, scaling emissions by pMDI DDD - rather than population size or disease prevalence - was considered the most appropriate method for cross-country adjustment. Applying a scalar based on relative pMDI use (28/62 ≈ 0.45) to the Dutch pMDI footprint yields an estimated Danish pMDI emission of approximately 35 kt CO₂-equivalents (GWP100).

This estimate aligns closely with independent Danish calculations by Vestbo & Press-Kristensen (2023), who estimated approximately 31 kt CO₂-equivalents from pMDI use using pharmacy dispensation data and propellant-specific emission factors. Minor differences are attributable to methodological choices, including the global warming potential time horizon (GWP20 vs. GWP100) and assumptions regarding propellant composition. Overall, the convergence of estimates supports the robustness of the dose-based scaling approach.

### Private travel

In order to avoid the risk of using different data sources from ecoinvent to calculate direct emissions, a scaling method has been developed to calculate direct emissions from private travel. Data was retried from 'Steenmeijer et al.'s Background document', <https://opendata.cbs.nl/#/CBS/nl/dataset/83500NED/table?ts=1765870958223>, and https://backend.orbit.dtu.dk/ws/files/245076078/TU_Denmark_2019.pdf.

The scaling relied on these categories:

- For general travel data
  - General average mileage: Avg. trip length, excl. commercial transport (CBS.nl, 2025; Table 2 In appendix @)
  - Average mileage for commuting: Mileage (PKM) by mode and purpose group (ibid, Table 20 in appendix @)
  - Average mileage on running errands: (ibid; ibid)
  - Modes of Transport: Mileage and travel time by mode (Steenmeijer et al. 20xx background, ;Table 3 in appendix @)
- Additional data for estimating commuting mileage
  - Number of employees in The Netherlands (Steenmeijer et al. 20xx background) and in Denmark (Statbank...@)
  - Actual weekly work hours (ibid)

Employees in 2019 **524000** (https://www.statista.com/statistics/461929/health-and-social-care-employment-in-denmark/?srsltid=AfmBOorvEB51hZN2lrxTPuMLIIYlZCmVrnKk2QypqRYI7oND1yWrdWto)

Faktisk ugentlig arbejdstid I 2019 34.4 (<https://www.dst.dk/da/Statistik/emner/arbejde-og-indkomst/befolkningens-arbejdsmarkedsstatus/arbejdskraftundersoegelsen-aku>)

Faktisk ugentlig arbejdstid i NL i 2019 29.2 (<https://opendata.cbs.nl/#/CBS/en/dataset/81431ENG/table> https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Actual_and_usual_hours_of_work&utm_source=chatgpt.com)

Modal of transport is very similar between DK and NL, differences are negligible.

(https://www.google.com/search?q=TU+2019+Annual+Report+(Denmark)%3A+%E2%80%9CThe+Danish+National+Travel+Survey+%E2%80%93+Annual+Statistical+Report+2019%E2%80%9D+(DTU%3B+PDF).+It+documents+survey+design+and+provides+tables%2Ffigures+of+transport+patterns+for+residents&rlz=1C1GCEU_enDK1104DK1104&oq=TU+2019+Annual+Report+(Denmark)%3A+%E2%80%9CThe+Danish+National+Travel+Survey+%E2%80%93+Annual+Statistical+Report+2019%E2%80%9D+(DTU%3B+PDF).+It+documents+survey+design+and+provides+tables%2Ffigures+of+transport+patterns+for+residents&gs_lcrp=EgZjaHJvbWUyBggAEEUYOdIBBjg4ajBqN6gCALACAA&sourceid=chrome&ie=UTF-8

https://backend.orbit.dtu.dk/ws/files/245076078/TU_Denmark_2019.pdf)

"Differences in travel distances between Denmark and the Netherlands vary by trip purpose. Commuting distances were calculated to be roughly 8% ((7.5+0.2+0.2)/(6.24+0.46+0.84+0.26+0.08)) higher in Denmark, while average travel distances across all purposes were approximately 29% (38/29.38) higher.

Distances associated with service and errand-type trips were found to be approximately 40% higher (7.6/(0.75+2.54+2.13)). This category likely includes *patient and visitor* travel, but even if it does, it does not do so exclusively. Therefore, sacrificing precision for accuracy (or similar word) a central distance scaling factor was derived as the unweighted mean of these three observed differentials (8%, 29%, and 40%), resulting in a heuristic approximation of 26%.

Calculating the emissions related to transport by using scalars avoided the risk of the contribution differences being caused by differences in ecoinvent data or other unforeseen database differences. Instead a scalar was applied to the final results of the Bottom up data Steenmeijer et al. used in their model.

Modalities were deemed sufficiently similar to exclude from further scrutiny. (Rationale: Denmark has more mileage on cars, but more electrical cars - yet less mileage on trains and 'other', which makes for a very complex redistribution to start messing around with).

Another uncertainty is that the year used in the Dutch study were 2016, while Danish values were derived from the year 2019.

Using scalars on the emission data:

Number of employees in Denmark in 2019: 524000

Number of employees in The Netherlands in 2016: 1220750

Average work hours in Denmark in 2019: 34.4

Average work hours in The Netherlands in 2016: 29.2

Mileage per day per person for commuting in Denmark in 2019: 8.5

Mileage per day per person for commuting in The Netherlands in 2016: 7.88

- Commuting
  - 524000/1220750 x 34.4/29.2 x (8.5/7.88)
    - Assuming same modal distribution, Danish commuting to and from healthcare in 2019 is assumed to be 0.545 or 54.4% of Dutch emissions in 2016

Mileage per day per person for errands in Denmark: 7.6

Mileage per day per person distributed over three types of errands in The Netherlands (Services/care, Shopping/Grocery/Shopping): 5.42

Mileage per day per person for general purposes in The Netherlands in 2016: 29.38

Mileage per day per person for general purposes in Denmark in 2019: 38

- Patient and Visitor travel:
  - 524000/1220750 x 7.6/5.42 x 38/29.38
    - Assuming the same distribution of patients and visitors per employee, emissions from Danish patients and visitors in 2019 are estimated to be 0.636 or 63.6% of Dutch emissions in 2016

## Analysis

The results are presented in three (maybe 4) ways:

- Total footprint results: The environmental impact of the Danish healthcare system and the share of the total national consumption
- Contribution analysis: Shows how much each expenditure category contributes to the total results
- Hotspot analysis: Brings an overview of where the emissions are located geographically

Problems with scope 1, 2, and 3 with direct emissions: Scope 1, anaesthetic gas used in hospital; but when it is sent back unused, it becomes scope 3.

Travel: The vehicles that the hospitals own (like ambulances and service cars) are scope 1, but commuters, patients and visitors become scope 3.
