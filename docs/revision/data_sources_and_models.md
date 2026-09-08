# Which external models and datasets we actually use, and why

This note was prompted by a fair challenge: an earlier memo mentioned OECD
**ICIO**.
That was a stray reference in a scoping brief. **ICIO is not used anywhere in
this study.** The models actually used are below.

## In use

| dataset | role | why this one |
|---|---|---|
| **EXIOBASE v3.10.2 IOT_2022_ixi** (Zenodo 20051562) | the model itself | 163 industries × 49 regions, the finest sectoral resolution of the harmonised global MRIOs, full GHG coverage, and the widest satellite set; the same family as the Dutch template. Native unit **M.EUR** |
| **Statistics Denmark IO tables** (117 industries, basic prices) | expenditure vector; recipe validation | public, national-accounts consistent, 2006-2022 |
| **Statistics Denmark DRIVHUS / AFFALD / AFTRYK / SHA1 / NABB69** | direct emissions, waste, national denominator, expenditure cross-check, employment | official, same DB07 classification as the IO tables, open API |
| **Eurostat FIGARO** (`env_ac_ghgfp`, supply/use 2022 & 2024) | independent benchmark and denominator | the official EU inter-country accounts; consistent, trustworthy SUT/IOT for Denmark, which is exactly why it is here |
| **EXIOBASE hybrid v3.3.18 (2011)** | legacy waste extension, now demoted | retained only as the "upstream solid residuals" tier with its composition disclosed |

## Considered and rejected, with reasons

- **OECD ICIO**: 45 industries, coarser than both EXIOBASE and the Danish
  national tables, CO₂-focused. Statistics Denmark rejected it for the same
  reason when building their own coupled model. **Not used.**
- **Eora**: used by Lenzen et al. and Pichler et al.; we use their *published
  Danish results* as benchmarks and their published SD to calibrate MRIO
  uncertainty, but not the database itself.

## FIGARO: what it can and cannot do for us

Downloaded to `data/bronze/figaro/`: the 2022 and 2024 use tables with Denmark
as destination, the DK supply table 2022-2024, and the official GHG/CO₂
footprint datasets 2021-2023.

**What it gives us now.** An independent national denominator: Denmark's
consumption-based GHG footprint 2022 = **57.40 Mt CO₂e**, against DST AFTRYK's
62.93 Mt and our model's 64.72 Mt, so the healthcare share is honestly
**7.5-8.5 %** depending on the denominator. It also puts emissions arising in
NACE Q due to Danish final demand at 176 kt (Q86 alone 97 kt), corroborating
our 142 kt Scope 1 plus the intra-health chain.

**What it can do for gap-filling.** At A64 it separates **Q86 human health**
from **Q87-Q88 residential/social work**, and carries **C21 pharmaceuticals**
separately, so it can (i) validate the EXIOBASE Danish health input recipe
against an official EU source, and (ii) supply an alternative import structure.

**What it cannot do.** 64 industries cannot substitute for the confidential
~2,350-product Danish SUT when the goal is health-sector disaggregation; it has
no medical-device or clinical-supply detail.

## US EEIO: the right tool for a specific job

It is worth adding for two purposes, neither of which the European sources cover:

1. **TRACI elementary flows.** USEEIO carries ~1,900 elementary flows mapped to
   TRACI characterisation, which is what an Eckelman & Sherman-style
   multi-pollutant and DALY analysis needs. Our EXIOBASE-based extended
   indicators give the *inventory* (PM2.5, NOx, SOx, NH₃, NMVOC, N and P to
   water) but no characterised midpoints or endpoints; USEEIO is the natural
   bridge if we want to add that layer.
2. **400+ sector resolution** as a donor prior for health-sector
   disaggregation, strictly for residual gaps where Danish data are silent,
   the discipline already stated in the research blueprint: Danish evidence
   first, USEEIO only as a transparent donor.

USEEIO is not yet implemented; it is listed as the next optional layer.
