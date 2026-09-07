# Danish shipping in EXIOBASE: the problem, our correction, and the alternatives

**Why this document exists.** Denmark operates one of the world's largest
merchant fleets. Every consumption-based account of Denmark has to decide what
to do about it, and the available methods disagree with each other by more than
the entire health-care footprint we are trying to measure. This note states the
problem plainly, sets out exactly what we do, compares it with every other
approach we could find, and says what we do *not* claim.

Reproduce with `PYTHONPATH=src .venv/bin/python -m analysis.dk_shipping_correction`
→ `data/gold/results/10_snac_shipping_correction/`.

---

## 1. The problem, in plain terms

An input–output model works out who ultimately pays for each industry's output.
If a Danish shipping company earns €100, the model needs to know whether that
€100 was spent by a Danish factory shipping goods for Danish customers, or by a
foreign firm moving cargo between two other countries. In the first case the
emissions belong in Denmark's consumption footprint; in the second they do not.

**EXIOBASE gets this badly wrong for Denmark.** It records **74 % of Danish
water-transport output as being bought by other Danish industries**, when the
Danish national accounts say the true figure is **9 %** — the rest is exported
services, i.e. carrying the world's cargo. Statistics Denmark documented this
(Rørmose Jensen & Iliev, 2022, table 1), and we reproduce their diagnosis on our
own model at **73.6 %**.

The consequence: emissions from ships serving global trade get charged to Danish
consumers, and — because every Danish industry appears to buy a lot of shipping
— to everything those consumers buy, including health care.

Two further signs that the block is broken, from the same table: EXIOBASE gives
Danish water transport a **gross value added of −1,880 million DKK** against
+33,339 million in the national accounts (a negative value added is not an
economy), and it records the **Danish health sector itself buying 394 M€ of sea
transport**, which hospitals plainly do not.

## 2. What we do

We reallocate one row. The Danish sea-transport row's deliveries to Danish
industries are scaled down so that its domestic intermediate share equals
Statistics Denmark's published **9 %**, and the released output is moved to
exports:

```
target      = 0.09 × x_row
Z[row, DK] ← Z[row, DK] × target / Z[row, DK].sum()
Y[row, foreign] ← Y[row, foreign] + released, distributed in proportion to
                  each foreign region's existing final demand
V[last, DK]     ← V[last, DK] + removed, restoring column balance
```

**Total industry output is unchanged** — it is not in dispute; it matches the
national accounts. Only its *allocation* changes. Danish industries that stop
buying phantom shipping have that amount credited to value added instead, since
their own output comes from the national accounts and is also not in dispute.

Verified: row balance to 1×10⁻¹¹, maximum column-balance residual 2×10⁻⁵ M€.

**Effect:** transport falls from 37.5 % to **18.9 %** of the health-care climate
footprint; the Danish sea-transport node falls from 822 kt to **71 kt**; the
Danish national footprint falls from 85.2 Mt to 77.5 Mt.

## 3. How this compares with every alternative

| Approach | What it does about Danish shipping | Cost | What it buys |
|---|---|---|---|
| **Raw EXIOBASE** | Nothing. 74 % of output charged to Danish intermediate use | none | a known-wrong Danish block |
| **Ours: targeted row reallocation** | Rescales one row to the published 9 % benchmark | ~50 lines | most of the effect, at the cost of being an approximation |
| **Rørmose Jensen & Iliev (2022), Statistics Denmark** | **Discards EXIOBASE's Danish block entirely.** The domestic block comes from the Danish national accounts; EXIOBASE is used only for imports. There is no shipping correction because the wrong data is never used | a full coupled model | correctness by construction |
| **Palm et al. (2019), simplified SNAC** | Same idea for Sweden: national A, Y and air-emission satellite replace the MRIO's, the rest-of-world block is left untouched and unbalanced | a full coupled model | ditto; effect size elsewhere reported at 4–15 % |
| **Danish Energy Agency** | **Excludes international shipping entirely**, following IPCC territorial convention, and reports it in a separate module: 39 Mt from Danish-operated bunkering abroad in 2022 | n/a | avoids the question rather than answering it |
| **Territorial bunker sales** (DEA *Energy Statistics*; Klimarådet's proposed 2050 target) | Counts fuel *sold* in Denmark to ships of any flag | n/a | a third, different number again |

**Four incompatible Danish shipping boundaries coexist**, two of them inside the
Danish Energy Agency itself. This is not a settled area, and any single figure
for "Denmark's shipping emissions" is meaningless without its boundary.

The published size of what is at stake: Usubiaga & Acosta-Fernández (2015),
bridging territorial to residence-based emissions on EXIOBASE 3, put
**Denmark at +30 %**, naming it in the large-fleet group alongside Greece
(+70 %) and Norway (+60 %).

## 4. What our correction is, and is not

**It is** a defensible approximation of the first and largest step of the method
Statistics Denmark uses, applied to the one industry they document as broken,
using their own published benchmark.

**It is not** a coupled model. We do not replace the Danish block; we repair one
row of it. Every other Danish industry keeps EXIOBASE's structure, including the
30–40 % import understatement Rørmose also documents.

**Simplification is defensible** on published grounds: Moran et al. (2018) put
the Danish feedback effect at **0.4 %**, which is why both Rørmose and Palm use
*simplified* rather than full SNAC.

**Independent support for the direction.** Ghosh et al. (2014, Rockwool
Foundation) find Danish consumption emissions *"relatively invariant to the
inclusion of fuel bunkering"*. That near-invariance is impossible if 74 % of
Danish shipping output really were consumed domestically — so their result
predicts a correction of exactly the sign and rough size we obtain.

**It appears to be novel.** No Danish study we have found applies a
sea-transport reallocation. That is a contribution, but it also means there is
no precedent to lean on, and we say so.

## 5. Why we corrected the transactions and not the emissions

There is an obvious alternative: leave the economic structure alone and instead
replace EXIOBASE's emission accounts with Danish national ones. **We deliberately
did not do that, and the literature is clear why.**

Melo (2019) compares top-down and bottom-up environmental extensions on the same
input–output system, so any difference is attributable to the satellite alone.
His finding for transport is emphatic: bottom-up gridded inventories
**underestimate shipping emissions roughly twelvefold** and aviation about
3.5-fold, because a gridded inventory assigns emissions to where they physically
occur, whereas an economic account must assign them to the *operator*'s country
(the residence principle). **Denmark is his worst case: 35.2 Mt of shipping
emissions under the top-down account against 1.5 Mt bottom-up — a 23-fold
spread.**

In plain terms: a Danish ship burning fuel in the Pacific belongs in Denmark's
economic account because a Danish company operates it, but a map-based inventory
puts those emissions in the Pacific, where no economy claims them. Substituting
such an inventory would silently delete most of Danish shipping.

So the fault is in **who is recorded as buying the shipping**, not in **how much
the ships emit**. We fixed the transaction side. Melo's caution applies to the
satellite side and is the reason we left it alone.

One implication we carry: Melo shows satellite errors propagate linearly and
undamped through the model, so any future substitution of Danish emission
accounts must be done per-stressor and with the residence principle preserved,
not wholesale.

## 6. Limitations

- **One row, not a model.** The other Danish industries retain EXIOBASE's
  structure, including its documented 30–40 % understatement of Danish imports.
- **Foreign shipping is untouched.** Rest-of-world Asia, Germany and rest-of-world
  Middle East sea transport still contribute to the Danish footprint, and no
  Danish source can correct another country's allocation. This is a large part
  of why our national total remains above the official one.
- **The 9 % benchmark is a single published year.** Rørmose report it for 2019;
  we apply it to 2022.
- **The released output is distributed across foreign final demand in proportion
  to existing demand.** That is a neutral assumption, not a measured trade
  pattern.

## References

- Ghosh B, Jensen JV, et al. (2014) *Measuring Denmark's CO₂ emissions 1996–2009*. Rockwool Foundation.
- Melo D (2019) *Bottom-up and top-down environmental extensions for the EUREGIO MRIO*. MSc thesis, Leiden University / TNO.
- Moran D, Wood R, Rodrigues JFD (2018) A note on the magnitude of the feedback effect in MRIO. *Journal of Industrial Ecology*.
- Palm V, Wood R, Berglund M, et al. (2019) *Journal of Cleaner Production* 228:634–644.
- Rørmose Jensen P, Iliev V (2022) *Consumption-based GHG account for Denmark using coupled models*. Statistics Denmark, Eurostat grant 101022790, WP4.
- Usubiaga A, Acosta-Fernández J (2015) Carbon emission accounting in MRIO models: the territory vs. the residence principle. *Economic Systems Research* 27(4):458–477.
