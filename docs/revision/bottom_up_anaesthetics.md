# Volatile anaesthetic gases — how far the evidence goes

## Where the number comes from now

Our anaesthetic-gas item (12.7 kt CO₂e) has two parts:

| part | value | basis | strength |
|---|---|---|---|
| **N₂O** | 11.3 kt | Denmark's National Inventory Document 2024 (DCE report 622), category 2.G.3.a: 38 t N₂O/yr × 298 | **strong** — official national inventory, though the 2013–2022 series is a constant extrapolated from 2005–2012 sales, and it includes non-hospital uses (dental, veterinary) |
| **volatile agents** (sevoflurane, desflurane, isoflurane) | 1.4 kt | Dutch inventory (Venema et al. 2022, 4.19 kt volatile component) scaled by population 5.87/17.28 | **weak** — a transfer, not a measurement |

Volatile halogenated agents are **not** in UNFCCC inventories at all (they are
outside the Kyoto basket), so no national figure exists for any country by
default. This is a structural gap, not a Danish one.

## How far we can go — the method now exists

**Talbot A, Holländer HC, Bentzer P (2025), "Greenhouse gas impact from medical
emissions of halogenated anaesthetic agents: a sales-based estimate",
*Lancet Planetary Health* (PMID 40120629)** establishes the defensible method:
take medical **sales** of sevoflurane, desflurane, isoflurane, halothane and
methoxyflurane, and apply GWP100 factors. Their dataset (IQVIA MIDAS, 91
countries, 80 % of world population, 2014–2023) gives a global impact falling
27 % from 2,754 kt CO₂e (2014) to **2,005 kt CO₂e (2023)**, with high-income
desflurane down 52 % to 1,053 kt. Country-level values sit in the appendix,
which is not open access.

**The Danish route is therefore identical in principle and available:**
volatile anaesthetics are dispensed through hospital pharmacies and are
recorded in the Danish medicines statistics under **ATC N01AB** (N01AB06
isoflurane, N01AB07 desflurane, N01AB08 sevoflurane). medstat.dk publishes
hospital-sector sales openly, and the Danish EPA already uses medstat for the
official pMDI F-gas inventory — the same institutional precedent. Converting
sold volume → mass → CO₂e with GWP100 factors reproduces the Talbot method for
Denmark exactly.

## Interim position (what the current results use)

The Dutch-anchored 1.4 kt is retained as the central value because it comes
from an actual inventory in a comparable high-income European system, and it is
consistent in order of magnitude with scaling the Talbot global total to Danish
population (~1.8 kt). The uncertainty parameter for the whole anaesthetic item
(GSD 1.30, i.e. a 95 % factor range of 0.60–1.67) is dominated by this
component and is documented as such.

**Materiality:** the entire anaesthetic item is 12.7 kt of a 4,875 kt footprint
(0.26 %), and its exact first-order variance share is **0.01 %**. Even a factor-
of-three error in the volatile component moves the headline by under 0.06 %.
This is worth stating plainly in the response letter: the reviewers were right
to ask for the uncertainty, and the answer is that this item cannot change any
conclusion.

## Double-counting check (performed)

Denmark's DRIVHUS accounts report fluorinated gases for hospital activities
(9 kt CO₂e in 2022, down from 25 kt in 2016). Halogenated anaesthetics are not
Kyoto-basket gases and are not part of that F-gas account — it is refrigeration
and cooling — so adding volatile anaesthetics bottom-up does not double count
against it. Hospital N₂O (11 kt CO₂e, constant across 2016–2023 in DRIVHUS) *is*
inside the accounts and is netted out of the Scope 1 figure before the
bottom-up anaesthetic item is added.

## Recommendation

Obtain the medstat ATC N01AB hospital series for 2019 and 2022 and compute the
Danish estimate directly, citing Talbot et al. (2025) for the method. Until
then, report the volatile component explicitly as a transferred proxy with the
stated range, and cite the materiality above.
