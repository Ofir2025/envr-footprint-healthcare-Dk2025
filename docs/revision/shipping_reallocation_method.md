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

An input-output model works out who ultimately pays for each industry's output.
If a Danish shipping company earns €100, the model needs to know whether that
€100 was spent by a Danish factory shipping goods for Danish customers, or by a
foreign firm moving cargo between two other countries. In the first case the
emissions belong in Denmark's consumption footprint; in the second they do not.

**EXIOBASE gets this badly wrong for Denmark.** It records **74 % of Danish
water-transport output as being bought by other Danish industries**, when the
Danish national accounts say the true figure is **9 %** - the rest is exported
services, i.e. carrying the world's cargo. Statistics Denmark documented this
(Rørmose Jensen & Iliev, 2022, table 1), and we reproduce their diagnosis on our
own model at **73.6 %**.

The consequence: emissions from ships serving global trade get charged to Danish
consumers, and - because every Danish industry appears to buy a lot of shipping
- to everything those consumers buy, including health care.

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

**Total industry output is unchanged** - it is not in dispute; it matches the
national accounts. Only its *allocation* changes. Danish industries that stop
buying phantom shipping have that amount credited to value added instead, since
their own output comes from the national accounts and is also not in dispute.

Verified: row balance to 1×10⁻¹¹, maximum column-balance residual 2×10⁻⁵ M€.

**Effect:** transport falls from 37.5 % to **18.5 %** of the health-care climate
supply-chain footprint (the 3,943 kt MRIO component; 15.4 % of the 4,713 kt total
once the domestic bottom-up items are included); the Danish sea-transport node
falls from 852 kt to **74 kt**; the Danish national footprint falls from 85.2 Mt
to **77.5 Mt**.

The basis is stated because the two denominators differ by the bottom-up
additions, which are entirely Danish and therefore dilute every supply-chain
share. Quoting a share without its basis is how the earlier drafts of this
document came to carry three figures that no longer reproduced.

## 3. How this compares with every alternative

| Approach | What it does about Danish shipping | Cost | What it buys |
|---|---|---|---|
| **Raw EXIOBASE** | Nothing. 74 % of output charged to Danish intermediate use | none | a known-wrong Danish block |
| **Ours: targeted row reallocation** | Rescales one row to the published 9 % benchmark | ~50 lines | most of the effect, at the cost of being an approximation |
| **Rørmose Jensen & Iliev (2022), Statistics Denmark** | **Discards EXIOBASE's Danish block entirely.** The domestic block comes from the Danish national accounts; EXIOBASE is used only for imports. There is no shipping correction because the wrong data is never used | a full coupled model | correctness by construction |
| **Palm et al. (2019), simplified SNAC** | Same idea for Sweden: national A, Y and air-emission satellite replace the MRIO's, the rest-of-world block is left untouched and unbalanced | a full coupled model | ditto; effect size elsewhere reported at 4-15 % |
| **Danish Energy Agency (official Danish method)** | **Also reallocates.** Danish-operated shipping and aviation are excluded from the footprint *"unless they transport goods and services consumed in Denmark"*, achieved by *"a technical reallocation of import amounts linked to the shipping and aviation industries"*. The excluded bulge is reported separately: 39 Mt in 2022 | a full coupled model | the same objective as ours, reached inside a coupled model |
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
30-40 % import understatement Rørmose also documents.

**Simplification is defensible** on published grounds: Moran et al. (2018) put
the Danish feedback effect at **0.4 %**, which is why both Rørmose and Palm use
*simplified* rather than full SNAC.

**Independent support that Denmark is a known case.** Wood et al. (2019) compare
consumption-based carbon accounts across multi-regional input-output databases
and name Denmark explicitly among the countries whose between-model variation is
driven by the handling of international transport emissions - the same defect
this note corrects, identified from outside this study and before it.

**Independent support for the direction.** Ghosh et al. (2014, Rockwool
Foundation) find Danish consumption emissions *"relatively invariant to the
inclusion of fuel bunkering"*. That near-invariance is impossible if 74 % of
Danish shipping output really were consumed domestically - so their result
predicts a correction of exactly the sign and rough size we obtain.

**It has an official precedent, which strengthens rather than weakens it.** The
Danish Energy Agency's Global Report - the statutory national consumption-based
account - performs *"a technical reallocation of import amounts linked to the
shipping and aviation industries"* so that Danish-operated transport is excluded
from the footprint unless it carries goods consumed in Denmark. Their objective
is identical to ours; they achieve it inside a coupled model, where the Danish
block comes from national accounts, whereas we achieve it by repairing one row
of EXIOBASE's Danish block.

**An earlier draft of this note claimed our reallocation was novel in the Danish
literature. That was wrong**, and reflected a search that had not reached the
Global Report's method annexes. What is novel is applying the correction to a
*sector* study on an uncoupled EXIOBASE model; the correction itself is standard
Danish practice.

## 5. Why we corrected the transactions and not the emissions

There is an obvious alternative: leave the economic structure alone and instead
replace EXIOBASE's emission accounts with Danish national ones. **We deliberately
did not do that, and the literature is clear why.**

Melo (2019) compares top-down and bottom-up environmental extensions on the same
input-output system, so any difference is attributable to the satellite alone.
His finding for transport is emphatic: bottom-up gridded inventories
**underestimate shipping emissions roughly twelvefold** and aviation about
3.5-fold, because a gridded inventory assigns emissions to where they physically
occur, whereas an economic account must assign them to the *operator*'s country
(the residence principle). **Denmark is his worst case: 35.2 Mt of shipping
emissions under the top-down account against 1.5 Mt bottom-up - a 23-fold
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

## 5b. What the official Danish method does, in full

Recorded because it is the benchmark our approach should be judged against. The
Danish Energy Agency's Global Report uses a **coupled input-output model** with
five components: Danish input-output tables from Statistics Denmark; Statistics
Denmark emission accounts built on DCE coefficients; *"EE-MRIO database in the
form of **EXIOBASE, version 3.9.2**"*; Danish foreign-trade statistics; and DCE
land-use data. EXIOBASE 3.9.2's own country data are *"updated to 2020 with
accounting data (supply-use tables) from the **FIGARO** database"*.

Their domestic block is **residence-based** - territorial emissions plus
Danish-operated international transport - with 117 Danish industries mapped to
EXIOBASE's 163, and imports deflated to 2020 with 2020 emission factors because
EXIOBASE's later years are nowcast. They characterise on **AR5**, and exclude
land-use change.

They also state their own method's weakness: *"the global balance between
imports and exports, which the EE-MRIO database contains, is broken when data
for individual countries changes."*

Three implications for this study. Denmark's official account is **in the same
model family as ours**, which is why our national total sits with the
EXIOBASE-family results rather than with FIGARO. Their release is **newer than
ours** (3.9.2 against 3.8.2). And their practice of freezing emission factors at
the last real year rather than using the nowcast is the substance of open
decision D8.

## 5c. An independent validation: the hybrid EXIOBASE reaches the same place

The strongest check available on our correction does not come from a Danish
source at all. **EXIOBASE's own hybrid build already allocates Danish sea
transport almost exactly as Statistics Denmark says it should**, without anyone
correcting it by hand.

Measured directly on `HIOT_2011.mat` (hybrid v3.3.18), Danish
*Sea and coastal water transport*:

| Model | Output | Domestic intermediate share |
|---|---|---|
| Monetary EXIOBASE v3.8.2, 2016 | 15,432 M€ | 73.5 % |
| Monetary EXIOBASE v3.8.2, 2022 | 17,805 M€ | **73.6 %** |
| **Hybrid EXIOBASE v3.3.18, 2011** | 7,616 M€ | **7.83 %** |
| Statistics Denmark benchmark | - | **9 %** |

The monetary share is 73.5 % in 2016 and 73.6 % in 2022, so it is structural
rather than a year effect.

**Where the difference comes from, stated carefully.** It is tempting to say the
hybrid "fixes" shipping. It does not, and the documentation is explicit that it
does not even try. The hybrid takes transport services **straight from the
monetary supply-use tables** - its methodological report lists `MSUTs` as the
sole source for both supply and trade of sea transport - and states that *"only
international transportation follows a residency approach (Stadler et al.
2015)"*, i.e. the bunker allocation is inherited unchanged. Transport is one of
the sectors the hybridisation deliberately leaves in money; there is no
tonne-kilometre layer, no transport margin block, and no per-tonne shipping
requirement anywhere in the hybrid trade module.

The divergence therefore arises **not in the source data but in the
supply-use-to-input-output construct**. Merciai & Schmidt note that *"a strict
correspondence between official monetary and hybrid SUTs is lost in the EXIOBASE
v3 database, because the monetary tables follow another approach linked to the
establishment."* Both builds start from the same monetary shipping values; the
monetary industry-by-industry table resolves them onto establishment-based
units, the hybrid onto homogeneous activity units, and only the latter keeps
Danish shipping revenue out of Danish intermediate use.

That is a weaker and more accurate claim than "the hybrid fixes it". What the
comparison establishes is that **the monetary allocation is construct-dependent
rather than an observation** - two builds over the same source data disagree by
a factor of nine, and the one that agrees with the national accounts is not the
one we use.

Two qualifications, both material:

**The allocation of *emissions* is unchanged.** The hybrid inherits monetary
EXIOBASE's residence-principle bunker allocation verbatim; the correlation
between the two allocations across countries is **0.95**. Measured on the
hybrid, the Danish sea-transport activity buys about 6.0 Mt of refined petroleum
and carries **18.4 Mt CO₂ - 34.5 % of Denmark's entire activity-side fossil
CO₂** (Greece 46.2 %, Norway 38.6 %). Our correction addresses the same half of
the problem the hybrid's construct does: who is recorded as buying the service,
not whose account the emissions land in.

A detail worth knowing: **Malta carries only 16 kt** in the hybrid despite being
a major flag state, so whatever the underlying allocation tracks, it is not flag
registry.

**Years do not match.** The hybrid is 2011 and our model is 2022, and the output
levels differ roughly twofold. The comparison establishes that the monetary
build's allocation is the outlier, not that 7.83 % is the right 2022 number.

**What this means for the correction.** It moves from "a defensible
approximation with no precedent" to "a manual reconstruction of an allocation
that an alternative construct over the same source data produces natively, and
that Denmark's statistical office publishes." Three independent routes - the
national accounts, the hybrid construct, and the Danish Energy Agency's own
reallocation in the statutory Global Report - agree that the monetary Danish
figure is wrong in the direction and roughly the magnitude we correct.

**No publication claims the hybrid corrects shipping.** Searching the whole
hybrid corpus - the 90-page methodological report, the version guide, the v4
report and the journal article - the word "bunker" appears exactly once, in a
sentence explaining why EXIOBASE differs from EDGAR. The inference that the
construct produces a better Danish allocation is ours, drawn from the data, and
is presented as such.

**Where a genuine structural fix is being built.** The BONSAI successor adds an
explicit trade-and-transport margin block and a route-based freight account
computing port-to-port distances and per-tonne-kilometre fuel intensities by
mode. That would replace the monetary-service treatment altogether. Its own
documentation warns the methods apply *"only partly to EXIOBASE v4"*, so it is a
direction of travel rather than an available alternative.

## 6. Limitations

- **One row, not a model.** The other Danish industries retain EXIOBASE's
  structure, including its documented 30-40 % understatement of Danish imports.
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

Full entries, with DOIs, are in [`docs/REFERENCES.md`](../REFERENCES.md), which
is generated from `docs/references.csv`. Cited here:

- Ghosh, B., Jensen, J. V., & Munch-Petersen, N. (2014). *Measuring Denmark's
  CO₂ emissions 1996-2009*. Rockwool Foundation Research Unit.
- Melo, D. (2019). *Bottom-up and top-down environmental extensions for the
  EUREGIO MRIO* [Master's thesis]. Leiden University and TNO.
- Moran, D., Wood, R., & Rodrigues, J. F. D. (2018). A note on the magnitude of
  the feedback effect in environmentally extended multi-region input-output
  tables. *Journal of Industrial Ecology, 22*(3), 532-539.
  https://doi.org/10.1111/jiec.12658
- Palm, V., Wood, R., Berglund, M., Dawkins, E., Finnveden, G., Schmidt, S., &
  Steinbach, N. (2019). Environmental pressures from Swedish consumption - A
  hybrid multi-regional input-output approach. *Journal of Cleaner Production,
  228*, 634-644. https://doi.org/10.1016/j.jclepro.2019.04.181
- Rørmose Jensen, P., & Iliev, V. (2022). *Consumption-based greenhouse gas
  account for Denmark using coupled models*. Statistics Denmark, Eurostat grant
  101022790, work package 4. https://www.dst.dk
- Stadler, K., Wood, R., Simas, M., Bulavskaya, T., de Koning, A., Kuenen, J.,
  Acosta-Fernández, J., Usubiaga, A., Merciai, S., Schmidt, J., Theurl, M.,
  Kastner, T., Eisenmenger, N., Giljum, S., Lutter, S., Bruckner, M., & Tukker,
  A. (2015). *Integrated report on EXIOBASE 3* (DESIRE deliverable 5.3).
  European Commission FP7. https://cordis.europa.eu/project/id/308552
- Usubiaga, A., & Acosta-Fernández, J. (2015). Carbon emission accounting in
  MRIO models: The territory vs. the residence principle. *Economic Systems
  Research, 27*(4), 458-477. https://doi.org/10.1080/09535314.2015.1049126
- Wood, R., Moran, D. D., Rodrigues, J. F. D., & Stadler, K. (2019). Variation
  in trends of consumption based carbon accounts. *Scientific Data, 6*, 99.
  https://doi.org/10.1038/s41597-019-0102-x
