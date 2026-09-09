# 03 - Target-sector scope 3 without double counting

**Gold folder** `data/gold/results/03_cabernard_target_scope3/`
**Module** `analysis.cabernard_target_scope3`
**Source** Cabernard, Pfister & Hellweg (2019), *A new method for analyzing
sustainability performance of global supply chains*, Sci Total Environ 684:164-177,
eqs. 8, 9, 12; extended in Cabernard & Pfister (2022)

## Question this layer answers

This layer answers a different question from the headline, and the distinction is the
point of the folder.

**(a) Final-demand footprint**, what the headline answers:
$$f = s\,L\,y_H$$
Each emission is allocated once, to Danish health-care final demand. This allocation
is additive over any number of target nodes and does not double count (Wood & Hertwich
2018 p. 5).

**(b) Target-sector scope 3**, what Cabernard et al. answer: *what is the scope 3 of
the health sector-regions themselves?* Here the naive form does double count.

## Method

The notation is Cabernard's, transcribed from her Table 1 and §2.2 (2019, p. 167).
Matrices are capitals, vectors lower case; $v_T$ and $v_O$ are index vectors
partitioning the 7,987 sector-regions into the **target set** $T$ and the
**non-target set** $O$, with $T \cup O = \text{all}$ and $T \cap O = \emptyset$.

$$A_{T-O} = A(v_T, v_O) \quad (1) \qquad A_{O-O} = A(v_O, v_O) \quad (2)$$
$$Y_{T-\text{all}} = Y(v_T, :) \quad (3) \qquad Y_{O-\text{all}} = Y(v_O, :) \quad (4)$$
$$x^T = x^{\text{tot}}(v_T) \quad (5) \qquad L_{\text{all}-T} = L(:, v_T) \quad (6)$$
$$L'_{O-O} = (I_{O-O} - A_{O-O})^{-1} \quad (7)$$

$d_{\text{all},i}$ is the 1 × 7,987 row vector of direct impact per unit output.

### Eq. (8): target scope 3 **with** double counting

$$e_{T,i} = d_{\text{all},i} \; L_{\text{all}-T} \; \mathrm{diag}(x^T) \qquad (8)$$

This equation is the form Cabernard attributes to previous studies, including Hertwich
& Wood (2018). Every delivery from one target node to another is counted twice: once as
the supplying target's own output, and again inside the receiving target's upstream
chain.

### Eq. (9): target scope 3 **without** double counting

The correction **replaces the gross output vector**; it does not subtract impacts. The
overbar is a row sum across final-demand columns:

$$e^{\text{wdc}}_{T,i} = d_{\text{all},i} \; L_{\text{all}-T} \;
\mathrm{diag}\!\left( \overline{Y_{T-\text{all}} + A_{T-O} \, L'_{O-O} \, Y_{O-\text{all}}} \right) \qquad (9)$$

Gross output $x^T$ is replaced by (i) final demand met directly by target outputs, plus
(ii) final demand for target products embodied in **non-target** outputs, deliberately
omitting target-into-target inputs. Because $A_{T-O}$ selects only the $T \to O$ block and
$L'_{O-O}$ propagates through non-target sectors only, this substitution removes
**both** direct $T \to T$ deliveries **and** indirect $T \to \dots \to T$ loops.

$L_{\text{all}-T}$ is untouched: the complete upstream chain, including inputs from other
target sectors, is still fully counted for whichever target's corrected output it attaches
to.

### Eq. (12): the overestimation factor

$$f_{T,i} = \frac{e_{T,i} - e^{\text{wdc}}_{T,i}}{e_{T,i}} \qquad (12)$$

### As implemented

`analysis.cabernard_target_scope3`, line for line against the equations above:

```python
L_OO  = np.linalg.inv(np.eye(len(O)) - A[np.ix_(O, O)])          # eq. 7
e_T   = float(d @ (L[:, T] @ x[T]))                              # eq. 8
q_T   = (Y[T, :] + A[np.ix_(T, O)] @ (L_OO @ Y[O, :])).sum(axis=1)  # eq. 9 bracket, overbar
e_wdc = float(d @ (L[:, T] @ q_T))                               # eq. 9
f_T   = (e_T - e_wdc) / e_T                                      # eq. 12
```

### What it shows

| Target set | Nodes | Eq. (8) naive (Mt) | Eq. (9) corrected (Mt) | $f_T$, eq. (12) | Overestimate against the corrected value |
|---|---|---|---|---|---|
| T1 Danish health and social work | 1 | 4.39 | 4.33 | 1.5 % | 1.5 % |
| T2 health and social work, all regions | 49 | 2,592.1 | 2,554.5 | 1.4 % | 1.5 % |
| T3 T2 + chemicals + medical instruments | 147 | 9,280.5 | 5,999.5 | **35.4 %** | **54.7 %** |

Two statistics are reported because they answer different questions and only one of
them is equation (12). $f_T$ takes the naive figure as its denominator and therefore
says what share of the naive total is double counted. The overestimate takes the
corrected figure as its denominator and says by how much the naive total exceeds the
right answer. They coincide while double counting is small and diverge once it is not,
which is why the T3 row reads 35.4 % against 54.7 %. Both are written to
`cabernard_target_scope3.csv`, as `double_counting_factor_f_T` and
`overestimate_vs_correct_pct`.

The T3 row is the finding, and it is the same mechanism Cabernard reports: a broadly
defined target set whose members sit in each other's supply chains. Her own G20 paper
reports overestimation above 40 % for biomass and fossil resources and above 100 % for
metals and non-metallic minerals. Those are overestimates against the corrected value,
so the comparable figure here is **54.7 %**, which is of that order.

## Data requirements

This layer needs $A$, $L$, $x$, and the characterised intensity $s$ from
[00](00_core_footprint.md). No additional data is required.

## Does our headline inherit the Hertwich & Wood double counting?

**No, and the reason is structural rather than a correction we apply.**

Cabernard's objection is to Eq. (8) applied to a *set* of target sectors. The double
counting arises from summing $E_Z$-type flows over targets that sit in each other's supply
chains. Three of our numbers could in principle be exposed to it; each is checked:

| Our quantity | Form | Exposed? |
|---|---|---|
| Headline footprint | $f = s L y_H$, a **final-demand** footprint | **No.** Hertwich & Wood state it themselves: $E_y$ sums to the total while $E_Z$ does not. Each emission is allocated once, to Danish health final demand. |
| Scope 2 ([02](02_scopes_wood_hertwich.md)) | energy **rows** of $E_Z$ for the single health **column** | **No.** One row-slice of one purchasing column is not a sum over overlapping targets. No second target exists to double count against. |
| Scope 1 + 2 + 3 | $S_3$ is the footprint **residual** after $S_1$ and $S_2$ | **No.** The partition is constructed to sum to $f$ exactly, so it cannot exceed it. Audit check C1 asserts this identity. |
| Target-sector scope 3 (this folder) | Eq. (8) | **Yes**, which is precisely why Eq. (9) is implemented here. |

So the exposure is confined to the one quantity this folder exists to compute, and there it
is corrected with Cabernard's own equation rather than an approximation of it. The
manuscript's reported numbers are all final-demand footprints and are unaffected.

## Deviations from the source, stated

- Cabernard et al. apply this to global sector groups; the target sets here are chosen
  to bracket plausible definitions of "the health-care supply chain", which is our
  choice and is documented in the `target` column.
- **Cabernard excludes extraction sectors** from her target set when quantifying double
  counting, "because this step is already included in the upstream supply chain of
  material processing" (2019, §2.7). Our target sets are health, chemicals, and medical
  instruments, none of which is an extraction sector, so the analogous exclusion does not
  arise. The point is stated because a reader checking our T3 against her method will
  look for it.
- Cabernard formalises **scope 3 only**. The strings "scope 1" and "scope 2" do not appear
  in either the 2019 or the 2022 paper. Our scope 1 and 2 come from
  [02](02_scopes_wood_hertwich.md) (Hertwich & Wood and the GHG Protocol), not from her,
  and this folder makes no scope 1 or scope 2 claim.
- **This layer does not change the headline.** The study's headline is a final-demand
  footprint, form (a), which was never subject to this double counting. The folder
  exists to demonstrate that, not to correct anything.

## Outputs

| File | Content |
|---|---|
| `cabernard_target_scope3.csv` | the three target sets, naive vs corrected, with the identity check |
| `cabernard_target_scope3_by_producing_node.csv.gz` | corrected result at full node detail |
| `cabernard_domestic_vs_imported.csv` | domestic/imported split of the corrected result |

## Verification

`complement_identity_rel_dev` is ≤ 2.3 × 10⁻¹⁵ for all three target sets: target plus
non-target scope 3 reconstructs the world total to machine precision.
