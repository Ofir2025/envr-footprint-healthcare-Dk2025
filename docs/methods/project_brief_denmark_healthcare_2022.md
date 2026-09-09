# Project brief: Denmark healthcare environmental footprint, 2022

## Goal
Replicate, validate, and extend Steenmeijer et al. (2022) for **Denmark in 2022**. The final analysis must be scientifically defensible, reproducible, and suitable for a strong peer-reviewed journal in industrial ecology, sustainability, or planetary health.

## Your role
Act as a senior industrial ecologist, EE-MRIO researcher, input-output economist, LCA practitioner, and research software reviewer.

## Primary repositories
Original Dutch study implementation:  
`/Users/kwametutu/workzone/projects/codebase/github/envhealth_footprint`

Danish replication by Ofir and co-authors:  
`/Users/kwametutu/workzone/projects/codebase/github/envrfootprint_healthcare`

Main Dutch paper:  
`/Users/kwametutu/workzone/projects/codebase/github/envrfootprint_healthcare/docs/references/steenmeijer_et_al_2022_environmental_impact_dutch_health_care.pdf`

Local EXIOBASE data:  
`/Users/kwametutu/Library/CloudStorage/OneDrive-Personal/Data/lca/input_output/mrio/exiobase/`

Important external EXIOBASE resources:
- https://zenodo.org/records/10148587
- https://zenodo.org/records/20051562

## Target year and key constraint
The target analysis year is **2022**.

I have already parsed the 2022 EXIOBASE **IXI** data to `.mat`. Inspect the local EXIOBASE directory thoroughly before downloading anything else.

The unresolved issue is **waste**. Hybrid EXIOBASE is locally available for 2011 and 2016, but not natively for 2022. Do not silently transfer 2011/2016 waste coefficients into 2022. First determine how waste is represented in the hybrid system, whether a defensible 2022-compatible source can be constructed or obtained, and what double-counting risks arise when combining it with the 2022 monetary IXI model.

Relevant local hybrid data include:

`/Users/kwametutu/Library/CloudStorage/OneDrive-Personal/Data/lca/input_output/mrio/exiobase/versions/hybrid_v3_3_18/HIOT_2011.mat`

`/Users/kwametutu/Library/CloudStorage/OneDrive-Personal/Data/lca/input_output/mrio/exiobase/versions/hybrid_v3_8_beta2/HIOT_2016.mat`

## First task: forensic audit before changing anything
Before editing methodology or code:

1. Reconstruct the Dutch workflow end-to-end from raw inputs to final results.
2. Compare the Dutch repository with the Danish replication and identify every substantive change in data, equations, classifications, years, assumptions, and outputs.
3. Inventory all locally available EXIOBASE datasets, years, table types, extensions, labels, units, waste data, SUT/IOT files, and parsed `.mat` files.
4. Determine which Danish 2022 data already exist and which data are missing.
5. Identify hard-coded 2016, 2019, Dutch, currency, price-basis, or classification assumptions that remain in the Danish implementation.
6. Do not assume code is scientifically correct because it runs.

## Danish SUT requirement
Determine whether suitable Danish 2022 supply-use data are already available locally. If not, identify exactly what must be downloaded and from which authoritative source.

Audit:
- year consistency;
- basic vs purchaser prices;
- current vs constant prices;
- product vs industry classifications;
- imports and margins;
- healthcare services;
- pharmaceuticals;
- medical appliances;
- concordance with EXIOBASE.

Do not mix years or price concepts without explicitly documenting and testing the implications.

## Mandatory methodological reading
Read the main Dutch paper completely and study the relevant methods before altering equations.

MRIO methods and accounting:  
`/Users/kwametutu/workzone/projects/codebase/github/envrfootprint_healthcare/docs/references/wood_et_al_2018_the_growing_importance_of_scope_3_greenhouse_gas_emissions_from_industry.pdf`

Read the relevant papers in:  
`/Users/kwametutu/Library/CloudStorage/OneDrive-Personal/_Projects/2026_project/AFRIMAT/docs/references/articles/methods/input_output_models/`

Double-counting and footprint methodology:  
`/Users/kwametutu/Library/CloudStorage/OneDrive-Personal/_Projects/2026_project/AFRIMAT/docs/references/articles/methods/footprint_methodologies/`

Healthcare footprint literature and supporting evidence:  
`/Users/kwametutu/workzone/projects/codebase/github/envrfootprint_healthcare/docs/references/`

Pay particular attention to Steenmeijer et al. (2022), Lenzen et al. (2020), Karliner et al. (2019), Malik et al. (2018, 2021), Pichler et al. (2019), Tennison et al. (2021), Eckelman & Sherman (2016), and the 2025 Denmark health-sector emissions fact sheet.

Read methods, equations, supplementary information, system boundaries, and limitations, not only abstracts or keyword matches.

## Accounting checks
Reconstruct and verify the exact equations implemented, including at minimum:

`A = Z x̂⁻¹`  
`L = (I - A)⁻¹`  
`S = F x̂⁻¹`

and the exact footprint formulation used for the Danish healthcare final-demand vector.

Do not change equations merely to reproduce an expected result. Check dimensions, units, ordering, labels, and matrix identities independently.

Keep distinct:
- territorial emissions;
- production-based impacts;
- consumption-based impacts;
- healthcare footprint;
- direct healthcare impacts.

## Double-counting guardrail
Maintain an explicit double-counting ledger for every bottom-up addition, especially:
- anaesthetic gases;
- pMDIs;
- pharmaceuticals;
- medical devices;
- employee commuting;
- patient and visitor travel;
- energy;
- waste;
- wastewater;
- food;
- construction/capital.

Before adding any bottom-up burden, establish whether it is already represented in the MRIO footprint and document the resolution.

## Evidence and provenance
For every major input, record:
- source;
- target year;
- actual year;
- unit;
- price basis;
- classification;
- transformation;
- proxy status;
- uncertainty.

Distinguish clearly between:
1. source data;
2. code implementation;
3. assumptions/proxies;
4. new recommendations.

## Guardrails
IMPORTANT:
- Do not overwrite raw data.
- Do not silently repair discrepancies.
- Do not mix years, currencies, units, price bases, or classifications without documentation.
- Do not fabricate missing data.
- Do not use 2011/2016 waste as 2022 truth without a justified method and sensitivity analysis.
- Do not add direct/bottom-up impacts before checking for double counting.
- Do not rewrite the manuscript before the computational audit and numerical validation are complete.
- Ask me when a missing scientific decision cannot be resolved from the data, code, documentation, or literature.

## First deliverable
Produce a concise forensic audit covering:
- Dutch method and code flow;
- Danish implementation and departures;
- available local data;
- 2022 IXI readiness;
- Danish SUT status;
- waste-extension options;
- missing inputs;
- likely methodological risks;
- double-counting risks;
- recommended sequence for the 2022 analysis;
- unresolved decisions requiring my input.

Only after I approve the audit should you implement substantive methodological changes.
