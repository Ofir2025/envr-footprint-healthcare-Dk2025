# Methodological approaches implemented, and how to trace any number

This study is not a single model. It is a **core EE-MRIO footprint** plus a set
of **named methodological layers**, each implementing a specific published
method, each writing to its own folder under `data/gold/results/`, and each
traceable through `data/gold/results/MANIFEST_lineage.csv` (one row per file:
approach, script, equations, reference, inputs, checksum).

```
data/gold/results/
├── MANIFEST_lineage.csv          every gold file: approach, script, equations, inputs
├── 00_core_footprint/            the detailed footprint arrays (lineage base)
├── 01_eriksen_replication/       the Steenmeijer-style outputs (tables 1, S5)
├── 02_scopes_wood_hertwich/      GHG-Protocol scopes + the double-counting ledger
├── 03_cabernard_target_scope3/   target-perspective scope 3, corrected
├── 04_uncertainty_lenzen_ieooc/  Monte Carlo, variance shares
├── 05_waste_dst_accounts/        waste from Denmark's own SEEA accounts
├── 06_benchmarks_validation/     benchmarks, denominators, recipe validation
└── scenarios/                    scope-boundary variants
```

---

## 00 - Core EE-MRIO final-demand footprint

**Reference:** Steenmeijer et al. (2022); Miller & Blair (2009).
**Equations:** `f = C S L y_H`, decomposed cell-wise as `E[i,j] = s_i L_ij y_j`
- pressure arising in node *i* caused by Danish healthcare demand for node *j*.
Summing over *i* gives the consumption perspective, over *j* the production
perspective; both are marginals of one array, verified equal to machine
precision (`analysis.validate_io_identities`, tests T5/T6).

**Why it does not double count:** allocating production emissions to final
demand is additive and sums to the total; the embodied-flow table `E_Z` is the
construct that double counts, and we never sum it (Wood & Hertwich 2018, p. 5).

## 01 - Eriksen/Steenmeijer replication (corrected)

The original study's outputs, with the audit corrections: complete eldercare
coverage, DRIVHUS direct emissions, AFFALD direct waste, Danish bottom-up
medical gases, year-consistent currency, exact-match transport grouping.
Every correction is listed in `docs/revision/bug_and_method_fixes.md` with its
effect on the result.

## 02 - GHG-Protocol scopes (Wood & Hertwich)

**Reference:** Wood & Hertwich (2018), table 1 and eqs. 1-2; GHG Protocol.
- **Scope 1** from national accounts. The services demand vector is
  `y = A[:,h]·E_H`, and we verified the identity `F = (m_h − s_h)·E_H`, i.e.
  the construction yields a *pure upstream* quantity - the exact complement to
  a national-accounts Scope 1. (Using the true final-demand column instead
  would double count Scope 1 outright.)
- **Scope 2** = `d_E · L_EE · y_E` with `L_EE = (I_EE − A_EE)^-1` over the
  energy block, so generation is reached through transmission and distribution
  without leaving that block; fuel extraction and refining stay in Scope 3.
- **Scope 3** = the footprint residual after Scope 2, plus the bottom-up items
  the MRIO structurally cannot contain.
- **Asserted:** `S1 + S2 + S3 + outside == total`, and the producing-node
  detail reconciles.

The **double-counting ledger** (`double_counting_ledger.csv`) tests each overlap
risk numerically, including the intra-sector self-supply term (3.2 kt CO₂e,
removed) and the pharma-component-vs-procurement question (cleared: different
channels).

## 03 - Target-sector scope 3 (Cabernard)

**Reference:** Cabernard et al. (2019) eqs. 8/9/12; Cabernard et al. (2022) SI.

This answers a **different question** from 00: not "what does Danish healthcare
demand cause?" but "what is the scope 3 of the health sector-regions
themselves?" - and *that* question double counts unless corrected, because a
delivery from one target node to another is counted for the supplier and again
for the recipient. Corrected output replaces gross output with output net of
target-to-target deliveries:

```
q_T     = rowsum( Y[T,:] + A[T,O] L'_OO Y[O,:] )
e_T,wdc = d L[:,T] diag(q_T)
f_T     = (e_T − e_T,wdc) / e_T
```

**Measured for three nested target sets (Denmark 2022, climate):**

| target set | nodes | naive | corrected | double-counting factor |
|---|---|---|---|---|
| T1 Danish health and social work | 1 | 0.9 Mt | 0.9 Mt | **1.3 %** |
| T2 health and social work, all regions | 49 | 1,129 Mt | 1,100 Mt | **2.6 %** |
| T3 T2 + chemicals + medical instruments | 147 | 3,093 Mt | 2,511 Mt | **18.8 %** (23 % overestimate) |

The complement identity `d L Y·1 == e_T,wdc + d_O L'_OO Y_O·1` holds to 2×10⁻¹⁶,
confirming the implementation. **Read this correctly:** the study's headline is a
final-demand footprint (00) and is *unaffected*. But any target-perspective or
sub-sector reporting - which is exactly what the planned health-subsector
disaggregation will produce - must use eq. 9, and at T3 the error is nearly a
fifth. This is the quantitative answer to "is one target enough?": for a single
Danish health node the correction is 1.3 %, but the moment pharmaceuticals and
device manufacturing join the target set it is 19 %.

## 04 - Uncertainty (Lenzen calibration, IEooc conventions)

**References:** Lenzen et al. (2020) SI 7 for the MRIO standard deviation;
IEooc Methods5 Exercise 4b for reporting conventions.
Median-1 lognormal multipliers so the MC median reproduces the deterministic
model; structural choices as discrete scenarios; MRIO parameter uncertainty as
one shared factor at the published Danish health-care relative SD of 8.35 %;
correlated travel items; exact first-order Sobol shares (free for an additive
independent model); verified against closed-form lognormal moments.

## 05 - Waste from Denmark's own accounts

**Reference:** Statistics Denmark AFFALD01 / AFF1MU1N / AFF3MU1N.
The inherited hybrid-2011 extension was tested as absolute values, as a
coefficient, and as an allocation key, and fails all three (see
`waste_extension_validation.csv` and the revision ledger). The domestic tier now
uses Denmark's published IO waste multipliers; the imported tier is reported
separately and relabelled as upstream solid residuals.

## 06 - Benchmarks and validation

Recipe validation of EXIOBASE's Danish health input structure against the DST
117-industry health columns; three independent national denominators (own model
64.72 Mt, DST AFTRYK 62.93 Mt, Eurostat FIGARO 57.40 Mt); comparison with
Arup/HCWH, Pichler, Lenzen and the Dutch template.

---

## Lineage rule

Every gold table is exported at the **most detailed level available** and every
aggregate is a `groupby` of it - never the reverse. `MANIFEST_lineage.csv` maps
each file to its approach, script, equations, references and inputs, so any
number in the manuscript can be traced to the code that made it and the method
it implements.
