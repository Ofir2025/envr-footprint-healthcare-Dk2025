# What Statistics Denmark does about EXIOBASE, and what we do

Source of truth: Rørmose Jensen & Iliev (2022), *Consumption-based GHG account
for Denmark using coupled models*, Statistics Denmark / Eurostat grant
101022790, WP4; Palm et al. (2019) *J Clean Prod* 228:634-644; Tukker, Giljum &
Wood (2018) *J Ind Ecol* 22:483-498.

## 1. The defects they document, with their numbers

Their table 1 compares EXIOBASE v3.8 with the Danish national-accounts IOT for
**water transport**, 2019, million DKK:

| | EXIOBASE | Danish national accounts |
|---|---|---|
| Output | 137,637 | 246,064 |
| To Danish intermediate use | **74 %** | **9 %** |
| To exports | 14 % | 90 % |
| Imported inputs | 41 % | 93 % |
| Gross value added | **−1,880 (−1.3 %)** | **+33,339 (+14 %)** |

A negative value added is not an economy; it is a broken block. That industry is
more than half of Danish CO₂, so raw EXIOBASE routes the bulk of Danish shipping
emissions into Danish *consumption*.

Three further defects: **Danish imports in EXIOBASE are 30-40 % below the
national accounts**; the satellite vector contains extreme outliers (Mexican
secondary plastic at 372,548 t CO₂e per EUR turns a 2 M EUR import into 729 Gt);
and the nowcast years are internally out of sync, so inflation mechanically
inflates the footprint.

## 2. Their remedy is structural, ours is a patch

They adopt **simplified SNAC**: the Danish domestic block comes entirely from
the national accounts, and EXIOBASE is never used for it:
`A_d = Z x̂⁻¹`, `L_d = (I − A_d)⁻¹`, `e_d = ŝ_d L_d y_d + e_h`. EXIOBASE enters
only for imports, through `Q = Ŝ L` and `e_m = Q K m`, with `m = A_m L_d y_d +
y_m` and `K` a 7,987 × 117 concordance.

**Their model carries no shipping correction, because the wrong block is
discarded rather than repaired.**

Ours is a targeted reallocation of one row to their published 9 % benchmark. It
recovers most of the effect for a fraction of the work, and it is honest to call
it what it is: an approximation of the first step of a method we have not yet
implemented. Simplification is defensible: Moran et al. (2018) put the Danish
feedback effect at **0.4 %**, which is why simplified SNAC is used in preference
to full SNAC by both Rørmose and Palm.

Their own outlier remedy is a hard multiplier threshold of 1 kg CO₂e/DKK
(≈7.5 kg CO₂e/EUR) which they themselves call *"quite arbitrary"*; their
preferred future fix is iterative replacement of outliers by the cross-country
mean of the remaining 48 regions.

## 3. The finding that challenges our design

**Statistics Denmark does not use the nowcast years.** They freeze EXIOBASE at
**2019** (the last year backed by real emission data) for their 2019, 2020, and
2021 footprints, and deflate the demand vector back to 2019 prices.

We do the opposite: 2022 expenditure on the 2022 table, whose CO₂ accounts end
in 2019 and whose other greenhouse-gas accounts end in 2017.

Both positions are arguable. Ours has the merit that the Danish **economic**
block is validated against the 2022 national accounts and passes, and that
expenditure year and model year coincide, which is what reviewer 2 asked for.
Theirs has the merit that the **emission** side is never extrapolated.

This choice is an open decision (D8), not a settled one. A defensible middle
course is to report 2022 as the headline and a 2019-frozen, deflated variant as a
sensitivity, which would also answer reviewer 2's original concern from the
opposite direction.

## 4. Results worth citing against ours

| | Rørmose (2020) | This study (2022) |
|---|---|---|
| Danish national footprint | 65.4 Mt CO₂e | 77.5 Mt |
| Per capita | 11.0 t | 13.2 t |
| Share arising in Denmark | 38 % | n/a |
| Share arising abroad | **62 %** | n/a |
| Government consumption footprint | ~8 Mt, of which **~2/3 abroad** | n/a |

Their government-consumption finding matters directly: **Danish government
consumption, where public health care sits, is about two-thirds
imported-emissions in their coupled model**, materially more import-exposed than
households at 55 %. Our health-care footprint is **73.7 % imported** in origin,
which is consistent with, and slightly above, their government figure.

They publish **no like-for-like raw-versus-coupled comparison**, so the size of
the SNAC correction for Denmark cannot be cited from them; it would have to be
computed.

## 5. Method points that bear on our claims

- **Uncertainty priority is the reverse of the intuitive order.** Tukker et al.
  (2018): *"the environmental extensions, rather than the redistribution to
  final consumption via economic structure reflected by a specific GMRIO, forms
  the highest source of uncertainty… The next most important issue appears the
  differences in representation of the country SUT/IOT in GMRIOs, rather than
  the structure of the trade flows."* Variance mass belongs on the satellite
  first, then the domestic block, then trade.
- **Scope 2+3 is not an additive account.** Hertwich & Wood (2018) are explicit
  that scope accounting measures reduction opportunities and that the total does
  not sum to global emissions, and that **the amount of double counting depends
  on sector resolution**. Our scope partition is exact within our own boundary,
  which is a different and weaker claim, and the manuscript should say so.
- **A GHG-only footprint misses most of the variance.** Steinmann et al. (2017),
  via Tukker et al.: carbon, energy, land, water, and materials together explain
  only **~60 %** of environmental variance; adding five impact-oriented
  indicators reaches **95 %**, with toxicity the systematic omission. This result
  is the published justification for carrying IMPACT World+ alongside the five
  headline indicators.
- **Capital stays exogenous in both precedents.** Neither Rørmose nor Palm
  endogenise capital; both keep it as a GFCF final-demand column. That supports
  our baseline choice.
