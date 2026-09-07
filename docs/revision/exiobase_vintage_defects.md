# EXIOBASE vintage defects and the choice of background model

**Status:** decisive for the 2022 headline. This note records why the study's
background model is **EXIOBASE v3.8.2 `IOT_2022_ixi`** and not v3.10.2, and how
that conclusion was reached. Reproduce with:

```
PYTHONPATH=src .venv/bin/python -m analysis.vintage_defect_audit
```

which writes `data/gold/results/09_vintage_diagnostics/`.

## 1. Why this test was run at all

Rørmose Jensen & Iliev (2022, Statistics Denmark) show that EXIOBASE's Danish
block misallocates output between industries — their headline case is Danish
water transport, 74 % of whose output EXIOBASE sends to Danish intermediate use
against 9 % in the national accounts. Palm et al. (2019) build the same argument
into the SNAC method: for a small, open, highly specialised economy, the
nationally estimated block should replace the MRIO's own. Both papers imply a
test that is cheap and that this project had not run: **compare the EXIOBASE
Danish block, industry by industry, against Statistics Denmark's own published
input-output table for the same year.** Denmark publishes a 117-industry IO
table annually, so the test is direct.

The prompt to run it was an anomaly, not a hunch: the medical-appliance
component of the footprint (1,094 M.EUR of expenditure, 921 kt CO₂e, 22 % of the
climate total) was landing on Greece, China and the RoW aggregates, with a
Danish contribution of exactly zero.

## 2. What the test found

Two **distinct** defects, with different scope and different consequences.

### Defect D1 — industry 33 is empty across Europe (v3.10.2, all years)

`Manufacture of medical, precision and optical instruments, watches and clocks
(33)` carries essentially zero output in every European region of v3.10.2, in
**both** the 2016 and the 2022 tables:

| Region | v3.8.2 2016 | v3.10.2 2016 | v3.10.2 2022 | v3.8.2 2022 |
|---|---|---|---|---|
| DK | 4,919 | 0 | 0 | **6,276** |
| DE | 68,118 | 4.6 | 0 | **76,025** |
| FR | 30,720 | 0 | 0 | **35,274** |
| NL | 12,455 | 0 | 0 | — |
| US | 239,045 | 298 | 2,195 | — |

*M.EUR total industry output.* The whole-world v3.10.2 2022 total for this
industry is 186,074 M.EUR, against a global medical-devices industry an order of
magnitude larger.

This is a version defect, not a modelling result. Its consequence for this study
is direct and large: with domestic and all European supply set to zero, the
Danish medical-appliance demand can only be met by whichever regions retain a
non-zero i33. The resulting geography — Greece, Russia, RoW — is an artefact of
the empty rows, not a finding about Danish procurement.

It also explains, retrospectively, the **multiplier-outlier screening** that this
project introduced for the v3.10.2 build. That screening was motivated by GB
medical instruments carrying an intensity of 2×10⁸ kt CO₂e per M.EUR. An
emission account divided by an output of zero is exactly what D1 produces. The
screening was treating a symptom.

### Defect D2 — the Danish block is misallocated (v3.10.2, 2022 only)

Against Statistics Denmark's published 2022 IO table (`Total Output` row,
117 industries, converted at 7.4396 DKK/EUR):

| DK industry, 2022 | Nat. accounts | v3.8.2 | ratio | v3.10.2 | ratio |
|---|---|---|---|---|---|
| Health and social work | 45,321 | 43,955 | **0.97** | 16,326 | **0.36** |
| Education | 22,935 | 20,241 | **0.88** | 109,673 | **4.78** |
| Financial intermediation | 18,980 | 21,004 | **1.11** | 76 | **0.004** |
| Machinery n.e.c. | 21,150 | 18,700 | **0.88** | 28 | **0.001** |
| Medical/optical instruments | 9,130 | 6,276 | 0.69 | 0 | **0.00** |
| Real estate | 46,965 | 45,673 | **0.97** | 9,915 | **0.21** |
| *Total, all industries* | *706,281* | — | — | *681,918* | *0.97* |

*M.EUR.* The **total** is right to 3 %, so output has been redistributed between
industries rather than lost. The table is also internally consistent —
`x = Z·1 + Y·1` holds to 7×10⁻¹¹ and there are no orphan rows — so this is a
classification/allocation failure upstream of the balancing, not corruption.

D2 is **year-specific**: v3.10.2's own 2016 Danish block is sound (health
36,756; education 20,369; machinery 33,165 M.EUR). It appears with the nowcast
years. It is also **country-specific**: Germany (health 4.05 % of national
output), France (4.70 %), Italy (4.68 %), the Netherlands (4.22 %) and the
United States (3.43 %) are all plausible in v3.10.2 2022. The affected group is
**Denmark, Bulgaria, Malta and Switzerland**, which share one signature —
education inflated, health deflated, financial intermediation collapsed to
near-zero.

An independent internal check confirms D2 without leaving the study's own data:
Danish health and eldercare **final** expenditure in 2022 is 40,597 M.EUR. A
health-and-social-work industry whose **total output** is 16,326 M.EUR cannot
deliver it. The v3.10.2 2022 Danish health column is arithmetically impossible.

## 3. Consequence and decision

v3.10.2 `IOT_2022_ixi` cannot support this study. The defects fall precisely on
the model elements the method depends on: the health industry column, which is
the source of the services recipe through the Steenmeijer Z-column construction;
the medical-instruments industry, which carries the appliance component; and the
financial and machinery industries, which are part of the services supply chain.

**Decision: the background model is EXIOBASE v3.8.2 `IOT_2022_ixi`.** This is
the best available combination on all three criteria that matter:

1. *Correct analysis year.* 2022 is the study's agreed year and v3.8.2 publishes
   a 2022 table (Zenodo 5589597).
2. *Sound Danish block.* Every checkable industry group falls within ±12 % of
   Danish national accounts, and the two the study most depends on — health and
   social work, and real estate — within 3 %.
3. *Continuity with the submitted manuscript.* v3.8.2 is the vintage the
   original submission was built on, established earlier by fingerprinting. The
   revision therefore changes the year and the corrected method, not the model
   family, and reviewers can attribute differences to the corrections rather
   than to a vintage change.

The v3.10.2 artefacts are retained as `mrio2022_v3_10_2.pkl` and
`leontief2022_v3_10_2.pkl` so that every number in this note can be regenerated,
and so that a v3.10.2 sensitivity remains available.

### What this changes downstream

- **Outlier screening is withdrawn for the headline model.** It was introduced to
  contain D1 and is unnecessary once industry 33 has real output. It is retained
  as a diagnostic and reported as a sensitivity.
- **The medical-appliance component must be re-estimated.** Its previous value
  (921 kt, 22 % of the climate footprint, sourced from Greece/China/RoW) was
  built on empty European rows.
- **The transport finding must be re-examined on the corrected model.** The
  earlier conclusion that "transport ≈ 40 %" is vintage-dependent was itself
  derived partly from the v3.10.2 comparison and has to be re-derived.
- **The case for the Danish SNAC phase is strengthened, not weakened.** v3.8.2's
  Danish block agrees with national accounts on *totals*; that is a necessary but
  not sufficient condition. Rørmose Jensen & Iliev's finding concerns the
  *allocation of intermediate use*, which the recipe-validation diagnostic
  measures separately and which remains the motivation for the SNAC tier.

## 4. Honest limits of this test

The concordance in `analysis.vintage_defect_audit` covers twelve industry groups
whose mapping between the Danish DB07/NACE classification and the EXIOBASE 163
list is unambiguous. It is a plausibility screen, not a full concordance: a group
passing at ±12 % is evidence that the block is not grossly misallocated, not
proof that its input structure is correct. The input-structure question is what
`recipe_validation_2022.csv` addresses, and there v3.8.2 also has known biases.
Neither test was run against a vintage other than those on disk, so this note
makes no claim about v3.9, v3.10.0 or v3.10.1.

## References

- Palm V, Wood R, Berglund M, et al. (2019) Environmental pressures from Swedish
  consumption — a hybrid multi-regional input-output approach. *J Clean Prod*.
- Rørmose Jensen P, Iliev V (2022) *Coupled models — combining national accounts
  with EXIOBASE*. Statistics Denmark.
- Stadler K, Wood R, Bulavskaya T, et al. (2018) EXIOBASE 3: developing a time
  series of detailed environmentally extended multi-regional input-output tables.
  *J Ind Ecol* 22(3):502–515.
- Statistics Denmark, published input-output tables, `input_output_en_2022.xlsx`.
