# Capital (GFCF) in health-sector footprints: what others do, and what we do

**Question addressed:** *"Do we need to include capital/GFCF? We don't even
address endogenising capital. How do other studies address this?"*

Reproduce with `PYTHONPATH=src .venv/bin/python -m analysis.capital_gfcf`
→ `data/gold/results/11_capital_gfcf/`.

## 1. Why capital is normally missing

An input-output model's intermediate matrix `Z` records **current** inputs only.
Gross fixed capital formation sits in final demand, so in the standard Leontief
construction `f = C S L y` a hospital's building, its MRI scanner and its
patient-record system are never in the health sector's supply chain — they are
somebody else's final demand. For manufacturing this matters little; for
services, whose capital stock is large relative to annual purchases, it is the
single largest boundary omission (Wood & Hertwich 2018; Södersten et al. 2018).

## 2. What the comparable studies do

| Study | Capital | Effect reported |
|---|---|---|
| **Steenmeijer et al. 2022** (NL, the template) | **Excluded** | not quantified |
| **Eckelman & Sherman 2016; Eckelman et al. 2020** (US) | **Excluded** (US EEIO, no capital closure) | not quantified |
| **Tennison et al. 2021 / NHS England** | **Included** for the built estate via a separate capital-spend line, outside the EEIO | capital ≈ 4 % of the NHS footprint |
| **Malik et al. 2018** (Australia) | **Included** — the Australian IELab table is capital-endogenised | one reason their 7.2 % national share exceeds most others |
| **Malik et al. 2021** (NSW) | **Excluded** | stated as a limitation |
| **Lenzen et al. 2020** (global, 189 countries) | **Excluded** | stated as a limitation |
| **Pichler et al. 2019; Weisz et al. 2020** (AT, EU) | **Excluded** | — |
| **Arup/HCWH 2019** | **Excluded** | — |
| **Södersten et al. 2018** (method paper, EXIOBASE) | **Endogenised** | raises global consumption footprints ~10–15 %, and more for services |

So the field is split, and — importantly for comparability — **the studies this
one is benchmarked against mostly exclude capital**. Any headline that included
capital would not be comparable to Steenmeijer, Eckelman, Lenzen or Pichler.

## 3. Two data problems specific to Denmark

**(a) EXIOBASE understates Danish health capital.** Its consumption of fixed
capital for the Danish health-and-social-work industry is **1,269 M€**, against
**2,274 M€** in Statistics Denmark's own capital accounts (NABK69, P.51c,
V86000 + V87880, 2022) — understated **1.79×**. Any capital scenario built on
EXIOBASE's own CFC row would therefore understate the effect by nearly half.
Scenario A below is grounded in the national accounts instead.

**(b) An earlier claim in this repository was wrong and is withdrawn.** A note in
`double_counting_audit.py` and in the response letter attributed the *zero*
intermediate purchases of medical instruments by Danish providers to the capital
boundary — equipment sitting in GFCF rather than in `Z`. That was incorrect. The
zero is a data defect: EXIOBASE v3.10.2 carries ~zero output for industry 33 in
every European region in every year tested. See
[`exiobase_vintage_defects.md`](exiobase_vintage_defects.md). Both places are
corrected.

## 4. What we compute

All three treatments run on the same background, so they are strictly
comparable. Danish health capital is 36.6 % buildings, 44.7 % ICT/machinery/
equipment, 16.4 % intellectual property products, 1.7 % transport equipment
(NABK69 by asset; `capital_asset_mix.csv`).

**Baseline — capital excluded.** `f = C S L y_H`. The Steenmeijer-comparable
number, and the study's headline.

**Scenario A — exogenous capital service flow.**

```
f_A = f + C S L y_cap ,   sum(y_cap) = CFC_health = 2,274 M€
```

CFC, not GFCF, is the correct flow for an annual account: it is the capital
actually consumed during the year, so no asset is charged more than once over
its life. Using GFCF (3,200 M€) instead would overstate by 41 % in a year of
above-trend hospital investment. `y_cap` is spread over EXIOBASE products by the
Danish asset mix, and within each asset class by Denmark's own GFCF column, so
the import geography comes from the model rather than from an assumption.

**Scenario D — full endogenisation** (Södersten, Wood & Hertwich 2018;
Lenzen–Treloar augmentation):

```
K[:, j] = g_r(j) · cfc_j / x_j ,   A' = A + K ,   L' = (I − A')⁻¹
```

for every industry in every region, `g_r` being region *r*'s normalised GFCF
commodity vector. This propagates capital through **every** tier of the chain,
not just the first, and is an upper bound.

## 5. Results (Denmark 2022, shipping-corrected model)

| Indicator | Baseline (excluded) | A — exogenous CFC | D — endogenised |
|---|---|---|---|
| Climate change (kt CO₂e) | **3,978** | 4,506 (**+13.3 %**) | 4,815 (**+21.0 %**) |
| Material extraction (kt) | 4,234 | 5,028 (+18.8 %) | 5,547 (+31.0 %) |
| Blue water (Mm³) | 95.3 | 102.4 (+7.4 %) | 105.4 (+10.6 %) |
| Land use (km²) | 4,854 | 5,362 (+10.5 %) | 5,767 (+18.8 %) |
| Waste generation (kt) | 1,031 | 1,203 (+16.7 %) | 1,263 (+22.5 %) |

*MRIO components; the bottom-up items are unaffected by the capital boundary.*

Capital adds **13–21 %** to the climate footprint and more to materials, which
is what one expects: buildings and equipment are material-intensive. The spread
between A and D is the honest measure of how much the answer depends on the
method rather than on the data.

## 6. Recommendation

**Keep the baseline (capital excluded) as the headline**, because that is what
makes the result comparable with Steenmeijer, Eckelman, Lenzen, Pichler and
Arup — the studies the paper is positioned against. **Report Scenario A as the
headline sensitivity** (it is grounded in Danish national accounts and uses the
correct annual flow) and **Scenario D as the bound**. State explicitly that
Malik et al. 2018's higher Australian share (7.2 %) is partly a capital-boundary
difference, not only a real difference — which materially changes how that
comparison should be read.

## 7. Verification and honest limits

- `(I − A')L' = I` verified to 2×10⁻¹⁴ on sampled columns; `L' ≥ 0`.
- The spectral radius moves only from 0.97289056 to 0.97289057. This is **not**
  evidence that capital is negligible: EXIOBASE's dominant eigenvector is
  concentrated (|v| = 0.997) on *Cultivation of paddy rice*, a near-unit-column
  industry with no capital coefficient. ρ is uninformative here; the inverse
  verification is the meaningful check. Recorded in `capital_diagnostics.csv`.
- The asset→product bridge is coarse and fully stated in `capital_asset_mix.csv`.
  Only the *group* weights come from the Danish asset mix; the split within a
  group comes from the region's GFCF column.
- Scenario D uses EXIOBASE's own CFC for all regions, which for Denmark is
  understated 1.79×; the Danish correction is applied in Scenario A only. D is
  therefore conservative for Denmark.
- Neither scenario endogenises capital in the *bottom-up* items.

## References

- Södersten C-J, Wood R, Hertwich EG (2018) Endogenizing capital in MRIO models:
  the implications for consumption-based accounting. *Environ Sci Technol*
  52(22):13250–13259.
- Wood R, Hertwich EG (2018) *Environ Res Lett* 13:104013.
- Malik A, Lenzen M, McAlister S, McGain F (2018) The carbon footprint of
  Australian health care. *Lancet Planet Health* 2:e27–e35.
- Lenzen M, Malik A, Li M, et al. (2020) The environmental footprint of health
  care. *Lancet Planet Health* 4:e271–e279.
- Statistics Denmark, NABK69, accumulation account and balance sheets.
