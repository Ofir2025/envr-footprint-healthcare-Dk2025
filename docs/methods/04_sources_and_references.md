# Sources and references

## 1. Purpose

This document separates three source types:

1. **core scholarly sources provided in the project**;
2. **official statistical and methodological sources**;
3. **software/data repositories**.

The methodological blueprint should distinguish claims derived from these sources from modelling recommendations introduced for this research design.

---

# 2. Core scholarly literature

## Palm et al. (2019)

Palm, V., Wood, R., Berglund, M., Dawkins, E., Finnveden, G., Schmidt, S., & Steinbach, N. (2019). *Environmental pressures from Swedish consumption: A hybrid multi-regional input-output approach*. Journal of Cleaner Production, 228, 634-644.

DOI: https://doi.org/10.1016/j.jclepro.2019.04.181

### Role in this project

- simplified national/MRIO coupling;
- preservation of national economic/environmental statistics;
- separation of domestic and foreign supply-chain components;
- country-specific consumption footprint accounting.

---

## Hagenaars et al. (2025)

Hagenaars, R. H., Heijungs, R., Tukker, A., & Wang, R. (2025). *Hybrid LCA for sustainable transitions: principles, applications, and prospects*. Renewable and Sustainable Energy Reviews, 212, 115443.

DOI: https://doi.org/10.1016/j.rser.2025.115443

### Role

- current hybrid-LCA taxonomy;
- matrix augmentation;
- path-exchange method;
- tiered hybrid LCA;
- integrated hybrid LCA;
- methodological warnings about price dependency, double counting and poorly documented hybridisation.

---

## Agez et al. (2020)

Agez, M., Majeau-Bettez, G., Margni, M., Strømman, A. H., & Samson, R. (2020). *Lifting the veil on the correction of double counting incidents in hybrid life cycle assessment*. Journal of Industrial Ecology, 24, 517-533.

DOI: https://doi.org/10.1111/jiec.12945

### Role

- formal hybrid matrix framework;
- upstream/downstream complements;
- double-counting correction;
- distinction between explicit zeros and missing inputs.

---

## Agez et al. (2022)

Agez, M., Muller, E., Patouillard, L., Södersten, C.-J. H., Arvesen, A., Margni, M., Samson, R., & Majeau-Bettez, G. (2022). *Correcting remaining truncations in hybrid life cycle assessment database compilation*. Journal of Industrial Ecology, 26, 121-133.

DOI: https://doi.org/10.1111/jiec.13132

### Role

- capital endogenisation;
- environmental-extension gaps;
- limitations of transferring USEEIO information internationally;
- `pylcaio`;
- large-scale hybrid database construction.

---

## Wiedmann et al. (2011)

Wiedmann, T. O., Suh, S., Feng, K., Lenzen, M., Acquaye, A., Scott, K., & Barrett, J. R. (2011). *Application of hybrid life cycle approaches to emerging energy technologies: The case of wind power in the UK*. Environmental Science & Technology, 45, 5900-5907.

DOI: https://doi.org/10.1021/es2007287

### Role

- integrated and IO-based hybrid LCA;
- upstream/downstream matrices;
- price-conversion uncertainty;
- double-counting safeguards;
- structural path analysis.

---

## Bruckner et al. (2019)

Bruckner, M., Wood, R., Moran, D., Kuschnig, N., Wieland, H., Maus, V., & Börner, J. (2019). *FABIO: The construction of the food and agriculture biomass input-output model*. Environmental Science & Technology, 53, 11302-11312.

DOI: https://doi.org/10.1021/acs.est.9b03554

### Role

- supply-use thinking;
- physical SUT reconstruction;
- constrained least-squares balancing;
- handling missing values;
- transparent open-source model construction.

---

## Bruckner & Giljum (2018)

Bruckner, M., & Giljum, S. (2018). *FABIO: Food and Agriculture Biomass Input-Output model*. FINEPRINT Brief No. 3.

### Role

- physical supply-use framework;
- product/process detail;
- physical/economic hybridisation.

---

## Tukker, Giljum & Wood (2018)

Tukker, A., Giljum, S., & Wood, R. (2018). *Recent progress in assessment of resource efficiency and environmental impacts embodied in trade*. Journal of Industrial Ecology, 22.

DOI: https://doi.org/10.1111/jiec.12736

### Role

- comparison of DTA, bilateral, GMRIO, SNAC and simplified-SNAC approaches;
- national-account consistency;
- benefits and limitations of GMRIOs;
- sector/product aggregation.

---

## Wiebe et al. (2018)

Wiebe, K. S., Bjelle, E. L., Többen, J., & Wood, R. (2018). *Implementing exogenous scenarios in a global MRIO model for the estimation of future environmental footprints*. Journal of Economic Structures, 7, 20.

DOI: https://doi.org/10.1186/s40008-018-0118-y

### Role

- exogenous scenario implementation;
- distinction between footprint accounting and forecasting;
- technological-change scenarios.

---

## Gibon et al. (2015)

Gibon, T., Wood, R., Arvesen, A., Bergesen, J. D., Suh, S., & Hertwich, E. G. (2015). *A methodology for integrated, multiregional life cycle assessment scenarios under large-scale technological change*. Environmental Science & Technology, 49, 11218-11226.

DOI: https://doi.org/10.1021/acs.est.5b01558

### Role

- scenario-dependent hybrid LCA/MRIO;
- long-term technological change;
- integration of process and macro systems.

---

## Malik et al. (2015)

Malik, A., Lenzen, M., Ralph, P. J., & Tamburic, B. (2015). *Hybrid life-cycle assessment of algal biofuel production*. Bioresource Technology, 184, 436-443.

DOI: https://doi.org/10.1016/j.biortech.2014.10.132

### Role

- matrix augmentation;
- bottom-up engineering data plus MRIO;
- balancing an inserted industry;
- upstream supply-chain decomposition.

---

## Malik, Lenzen & Geschke (2016)

Malik, A., Lenzen, M., & Geschke, A. (2016). *Triple bottom line study of a lignocellulosic biofuel industry*. GCB Bioenergy, 8, 96-110.

DOI: https://doi.org/10.1111/gcbb.12240

### Role

- IO-based hybrid LCA;
- regional economic, social and environmental indicators;
- production-layer decomposition.

---

# 3. Official Statistics Denmark sources

## National Accounts: Input-Output and Supply-Use - statistical presentation

https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/statistical-presentation

Key points used:

- approximately 2,350 products and 117 industries in the detailed final SUT system;
- supply-use accounting identities;
- detailed product relationships are not publicly published because of confidentiality;
- researchers can apply for detailed access via Research Service;
- 117 × 117 industry IOTs are publicly published;
- DB07/NACE Rev.2/ISIC Rev.4 classification;
- Method D / fixed product sales structure for IOT construction.

---

## National Accounts: Input-Output and Supply-Use - statistical processing

https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/statistical-processing

Key points:

- final SUT compilation: 117 industries and approximately 2,350 products;
- preliminary SUT can be more aggregated;
- consumption and investment detail used in compilation.

---

## National Accounts: Input-Output and Supply-Use - comparability

https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/national-accounts--input-output-and-supply-use/comparability

Key point:

- Statistics Denmark documents revision consistency across recent detailed SUT vintages.

---

## Input-output tables in StatBank

https://www.dst.dk/en/Statistik/udgivelser/nyt/relateret?pid=1153

Relevant public tables include:

- `NAIO1`
- `NAIO2`
- `NAIO3`
- `NAIO4`
- multiplier tables.

---

## StatBank API

https://www.dst.dk/en/Statistik/hjaelp-til-statistikbanken/api

Important interpretation:

The API exposes **published StatBank data**.

It does not override confidentiality restrictions on detailed unpublished SUT cells.

---

## Input-output topic page

https://www.dst.dk/en/Statistik/emner/oekonomi/nationalregnskab/input-output

Includes public 117-industry input-output downloads and links to StatBank.

---

# 4. Eurostat SUT/IOT sources

## ESA supply, use and input-output tables - information on data

https://ec.europa.eu/eurostat/en/web/esa-supply-use-input-tables/information-data

Key points:

- harmonised public national SUTs;
- mandatory approximately 64 activities/products;
- voluntary more detailed 88-activity/product transmission;
- annual supply/use tables;
- five-yearly basic-price and symmetric IO tables.

---

## Eurostat SUT/IOT methodology

https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/methodology

Key points:

- SUT identities;
- product/industry classification;
- use of SUTs for balancing;
- relationship to symmetric IOT construction.

---

## Eurostat REST API

https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started/api

Useful for programmatic access to public Eurostat SUT/IOT datasets.

---

# 5. USEEIO sources

## USEEIO model repository

https://github.com/USEPA/USEEIO

## `useeior`

https://github.com/USEPA/useeior

### Role in this project

- inspect US healthcare sector structure;
- construct donor production-recipe priors;
- inspect disaggregation specifications;
- do not transfer US absolute environmental intensities to Denmark without justification.

---

# 6. EXIOBASE sources

## EXIOBASE

https://www.exiobase.eu/

Recent data releases are also distributed through Zenodo.

### Role

- global foreign supply-chain multipliers;
- environmental extensions;
- country/region-sector attribution of imported impacts.

Use the release version explicitly in every model run and preserve checksums/version metadata.

---

# 7. System of Health Accounts

## OECD System of Health Accounts

https://www.oecd.org/en/publications/a-system-of-health-accounts_9789264116016-en.html

### Role

- health functions;
- healthcare providers;
- financing schemes;
- health-expenditure accounting.

SHA should be used as a bridge and allocation source, not automatically equated with IO industry gross output.

---

# 8. Source hierarchy recommended for this project

For Danish health-sector disaggregation:

\[
\boxed{
\text{official Danish national-account observation}
>
\text{Danish provider/admin information}
>
\text{Danish SHA}
>
\text{European/regional proxy}
>
\text{USEEIO prior}
}
\]

For domestic environmental extensions:

\[
\boxed{
\text{official Danish environmental accounts}
>
\text{Danish physical provider data for allocation}
>
\text{other proxy}
}
\]

For imported upstream pressures:

\[
\boxed{
\text{Danish bilateral import structure}
+
\text{EXIOBASE foreign multipliers}
}
\]

This hierarchy is the central data-quality principle of the proposed research.
