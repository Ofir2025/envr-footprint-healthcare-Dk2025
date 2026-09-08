# Transport: a full audit of the finding being withdrawn

The submitted manuscript reports transport as the largest contributor to the Danish
health-care climate footprint, at **46 %** of sector contributions. That finding leads the
abstract, the *Research in context* panel and the cover letter. This is the audit of it.

The headline conclusion is favourable to the authors: **the 46 % is reproducible.** It is
not an analytical error. It is a faithful report of what an uncorrected EXIOBASE Danish
block says. The number has to be withdrawn because the underlying data are wrong, not
because the analysis was.

---

## 1. Is the transport group correctly defined?

**Yes, with one classification question worth stating.**

The group contains six transport *service* industries and no manufacturing:

| Code | Industry |
|---|---|
| `TRAI` | Transport via railways |
| `TLND` | Other land transport |
| `TPIP` | Transport via pipelines |
| `TWAS` | Sea and coastal water transport |
| `TWAI` | Inland water transport |
| `TAIR` | Air transport (62) |

`MOTO` and `OTRE` - motor vehicle and other transport-equipment *manufacturing* - sit in a
separate *Transport Equipment* group, correctly.

**The open question.** `TAUX`, *Supporting and auxiliary transport activities; activities of
travel agencies (63)*, sits in the **Services** group, not Transport. The manuscript states
that "transport is represented as a service sector (NACE H), capturing freight, logistics,
and service-related transport". NACE H does include warehousing and support activities for
transportation, so on the manuscript's own definition `TAUX` arguably belongs in the
transport group.

It is worth **1.07 percentage points**: transport is 15.45 % without it and 16.52 % with it.
We keep the inherited classification so the figures stay comparable with the submitted
ones, and state the alternative rather than switching silently.

## 2. Was the substring bug material?

**It was real but immaterial, and I previously overstated it.**

The submitted figure code matched transport by substring, which also caught *Transport
Equipment*. That is a genuine defect - it is wrong by construction - but on this footprint
vehicle manufacturing barely appears:

| | Transport only | + Transport Equipment | Difference |
|---|---|---|---|
| 2019, uncorrected | 47.28 % | 47.33 % | **+0.05 pp** |
| 2022, corrected | 15.45 % | 15.52 % | **+0.07 pp** |

Fixed in `analysis.manuscript_figure_tables` by matching exactly. It changes no conclusion.

## 3. Does our pipeline reproduce the 46 %?

**Yes - to 1.3 percentage points.** Running our corrected pipeline on the manuscript's own
background (EXIOBASE v3.7, 2016, no shipping correction) and its own reference year:

| | Transport share of the MRIO supply chain |
|---|---|
| Manuscript, as reported | 46 % |
| **Ours, same background and year** | **47.28 %** |

The residual 1.3 pp is the demand-vector difference (F1 in the manuscript assessment), not
a modelling disagreement. This is the strongest possible evidence that the finding was
correctly computed from the data available.

## 4. Where does 46 % go?

A four-step decomposition, each step measured rather than inferred:

| Step | Transport share | Change |
|---|---|---|
| 2019, v3.7/2016 background, uncorrected | **47.3 %** | - |
| 2022 demand and v3.8.2 background, still uncorrected | 37.5 % | −9.8 pp |
| **Danish sea-transport reallocation applied** | 18.5 % | **−19.0 pp** |
| Bottom-up items included in the denominator | **15.5 %** | −3.0 pp |

**The reallocation is the whole story.** Year, vintage and demand vector together move the
share by less than half of what the data correction does.

## 5. Is the correction itself sound?

| Test | Result |
|---|---|
| Danish national accounts benchmark | 9 % of water-transport output to domestic intermediate use |
| EXIOBASE v3.8.2 as published | **73.6 %** - Statistics Denmark's reported 74 %, to the decimal |
| EXIOBASE's own hybrid build, no correction applied | **7.8 %** - within 1.2 pp of the benchmark |
| Danish Energy Agency statutory practice | performs an equivalent reallocation for shipping and aviation |
| Row balance after correction | 1.1 × 10⁻¹¹ M€ |
| Maximum column-balance residual, Danish block | 2.4 × 10⁻⁵ M€ |
| Industry total output | unchanged - only the allocation moves |

Three independent sources agree the published monetary allocation is wrong, and none of
them is ours. The target share is set to the national-accounts benchmark exactly; there is
no fitted parameter.

## 6. What survives, and what should the paper now say?

Transport is **still the third largest** contributor at 15.5 % of the total climate
footprint, and **sea and coastal water transport alone is 10.1 %** - the single largest
transport component even after correction, reflecting genuine international shipping in
Danish health supply chains.

What changes is the ranking. **Pharmaceuticals and chemical products is the largest
contributor at 36.9 %**, not transport. The paper's central claim has to move accordingly,
in the abstract, the *Research in context* panel and the cover letter.

## 7. What a reviewer will ask, and the answer

*Why should we believe the correction rather than the published database?*
Because the correction reconstructs a figure that Danish national accounts publish, that
EXIOBASE's own hybrid construct produces natively without any correction, and that the
Danish Energy Agency already applies in statutory reporting. We are not proposing a new
method; we are reconciling one construct to three independent sources.

*Is the rest of the Danish block trustworthy?*
Only one row has a published benchmark and a first-order effect, and only that row is
corrected. Danish sectoral detail should be read as indicative; the aggregate is
benchmarked. Full national-accounts coupling (SNAC) would remove the remainder and is
scoped in `dk_snac_feasibility.md`.
