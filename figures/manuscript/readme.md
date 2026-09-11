# Manuscript figures

One directory per model VARIANT, because the transport-share swing the co-author
asked about (roughly 46 % in 2019 down to 15-18 % in 2022) is never one
comparison: reference year, EXIOBASE release, the Danish sea-transport
correction, the care boundary and the capital treatment can all change at once
between the submitted 2019 run and the corrected 2022 headline. A variant fixes
all four of those axes and is named `<year><letter>`
([`docs/methods/replications.md`, section 01](../../docs/methods/replications.md#r01)):

| Variant | EXIOBASE release | Danish shipping correction | Boundary | Capital |
|:---|:---|:---|:---|:---|
| a | v3.7 | no | health care (the submitted boundary) | excluded |
| b | v3.7 | yes | health care | excluded |
| c | v3.8.2 | yes | health care | excluded |
| d | v3.8.2 | yes | health care + child and elder care | endogenised |

Every variant carries the same figure set, drawn by the same code from the same
tables, so a difference between them is a difference in the data and never in
the plotting - with one stated exception, figures 3 to 6 of `2019_uncorrected`,
below. There is no `2022a` or `2022b`: EXIOBASE v3.7's series ends at 2016, so
it has no 2022 table and the release axis collapses for that year.

Every command below carries `LANG=en_US.UTF-8` so it can be copied and pasted
as it stands. `r/_dk_common.r` stops with that instruction if the locale is not
UTF-8, because a C locale drops CO₂, Mm³ and km² to `..` in every figure, and
prose above a code block is not a prefix.

```bash
# 2022c - EXIOBASE v3.8.2 IOT_2022 with the Danish sea-transport reallocation
# applied. The manuscript's headline.
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2022c Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2022c Rscript r/plot_absolute_and_percapita.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2022c Rscript r/plot_scenarios.r

# 2022d - the same year and correction, child care inside the boundary and
# consumption of fixed capital inside the Leontief inverse
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship HC_SCOPE=zorg_en_welzijn HC_CAPITAL=endogenised DKHC_FIG_DIR=figures/manuscript/2022d Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship HC_SCOPE=zorg_en_welzijn HC_CAPITAL=endogenised DKHC_FIG_DIR=figures/manuscript/2022d Rscript r/plot_absolute_and_percapita.r

# 2022_uncorrected - same background, correction NOT applied. Not a lettered
# variant: it is v3.8.2 without the correction.
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 DKHC_FIG_DIR=figures/manuscript/2022_uncorrected Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 DKHC_FIG_DIR=figures/manuscript/2022_uncorrected Rscript r/plot_absolute_and_percapita.r

# 2019a - EXIOBASE v3.7 IOT_2016, uncorrected: the release and correction state
# the manuscript was submitted on. HC_EXIOBASE_RELEASE is what selects it, and
# without it the run is v3.8.2 and is NOT variant a.
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_7 DKHC_FIG_DIR=figures/manuscript/2019a Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_7 DKHC_FIG_DIR=figures/manuscript/2019a Rscript r/plot_absolute_and_percapita.r

# 2019b - the same release, shipping-corrected
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_7 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2019b Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_7 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2019b Rscript r/plot_absolute_and_percapita.r

# 2019c - v3.8.2 IOT_2016 with the same correction applied, so it is comparable
# with 2022c on release, correction, boundary and capital alike
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2019c Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2019c Rscript r/plot_absolute_and_percapita.r

# 2019d - the widest boundary on the 2016 table
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_BACKGROUND_TAG=_snacship HC_SCOPE=zorg_en_welzijn HC_CAPITAL=endogenised DKHC_FIG_DIR=figures/manuscript/2019d Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_BACKGROUND_TAG=_snacship HC_SCOPE=zorg_en_welzijn HC_CAPITAL=endogenised DKHC_FIG_DIR=figures/manuscript/2019d Rscript r/plot_absolute_and_percapita.r

# 2019_uncorrected - v3.8.2 IOT_2016 with no correction. NOT variant a: the
# submitted estimate was computed on v3.7, which 2019a runs.
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 DKHC_FIG_DIR=figures/manuscript/2019_uncorrected Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 DKHC_FIG_DIR=figures/manuscript/2019_uncorrected Rscript r/plot_absolute_and_percapita.r

# fig10, the cross-year bridge - not tied to any one variant folder, so it
# writes straight into comparison/ rather than one of the variant folders above
LANG=en_US.UTF-8 DKHC_FIG_DIR=figures/manuscript Rscript r/plot_year_bridge.r

# the four scope-emission TIFFs, which live in figures/scopes/ rather than here
# and name their variant in the filename; the tag is not optional, because
# without it the layer resolves to the uncorrected run
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship Rscript r/plot_scope_emissions.r
```

The locale matters twice over. R also parses source files in the process
locale, and under `C` the non-ASCII characters in the labels are mangled:
"Södersten" came out as "S..dersten" with no warning.

## What the scope figures' fourth series is

Figures 3 and 6 partition by GHG-Protocol scope, and the study's own fourth
category is what the Protocol has no scope for: patient and visitor travel,
caused by the health system but neither owned, controlled nor purchased by the
providers. The gold tables call it `Outside protocol`; the legend calls it
**Patient and visitor travel**, because a figure here carries no title and no
on-image note, and the term appears in neither the manuscript nor the appendix.
The mapping is `SCOPE_LABELS` in `r/_dk_common.r`, and the category is defined
in [`docs/methods/replications.md`, section 02](../../docs/methods/replications.md#r02).

## Which variants can draw figures 3 to 6

`02_scopes_wood_hertwich` carries the same variant folders as
`01_eriksen_replication`, so `gold_path` resolves the scope tables to the
variant the environment selects and to nothing else. Figures 3 to 6 of
`2022_uncorrected` are therefore genuinely uncorrected, where before they were
byte-identical to `2022c`'s: the transport industry group carries 32.19 % of the
climate footprint in the uncorrected run against 14.87 % in the corrected one,
which is the difference the variant scheme exists to show.

| Variant | Figures 1, 2, S1 | Figures 3-6 |
|:---|:---|:---|
| `2019a` | yes | yes |
| `2019b` | yes | yes |
| `2019c` | yes | yes |
| `2019d` | yes | yes |
| `2022c` | yes | yes |
| `2022d` | yes | yes |
| `2022_uncorrected` | yes | yes |
| `2019_uncorrected` | yes | **not drawn** - layer 02 does not publish this run |

`2019_uncorrected` is the one gap, and it is a withheld figure rather than a
wrong one. The uncorrected and shipping-corrected 2016 model objects on disk
descend from two different extractions of `IOT_2016_ixi`, so a 2019 uncorrected
scope partition would miss that run's own published grand total by 58.47 kt;
publishing figures drawn from it would put a number in the paper that no
reconciliation supports. `plot_manuscript_figures.r` says so and skips those
four rather than aborting, so the rest of that variant's set still renders, and
the measurement is recorded in
[docs/revision/defects_and_fixes.md](../../docs/revision/defects_and_fixes.md).
Its transport share is readable from `01_eriksen_replication/2019_uncorrected`
(47.28 % of the climate footprint, against 21.46 % at variant c), which is
variant-scoped and unaffected.

## The variants are not interchangeable

| | 2019a | 2019b | 2019c | 2019d | 2019_uncorrected | 2022c | 2022d | 2022_uncorrected |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| Background | v3.7 IOT_2016 | v3.7 IOT_2016 | v3.8.2 IOT_2016 | v3.8.2 IOT_2016 | v3.8.2 IOT_2016 | v3.8.2 IOT_2022 | v3.8.2 IOT_2022 | v3.8.2 IOT_2022 |
| Danish sea-transport reallocation | not applied | applied | applied | applied | not applied | applied | applied | not applied |
| Boundary | health care | health care | health care | + child and elder care | health care | health care | + child and elder care | health care |
| Capital | excluded | excluded | excluded | endogenised | excluded | excluded | endogenised | excluded |
| Climate total, kt CO₂e | 8,694.66 | 6,625.53 | 4,054.77 | 5,897.84 | 6,360.39 | 4,675.47 | 6,495.66 | 6,087.33 |
| Transport share | 34.93 % | 16.56 % | 21.46 % | 20.10 % | 47.28 % | 14.87 % | 14.50 % | 32.19 % |

`2019a` runs the release and correction state the submitted manuscript used, and
it does **not** reproduce the submitted 46 % transport share: it returns 34.93 %.
`2019_uncorrected`, which is the same year and correction state on v3.8.2 rather
than v3.7, returns 47.28 % and is the run that reproduces the submitted finding.
`2022c` is the manuscript's headline. Comparing `2019_uncorrected` with `2022c`
directly - the only pair the figure set drew before the variant scheme existed -
mixes the year with the correction; see
`comparison/fig10_year_bridge_climate_2019_2022.tiff` and
`analysis.year_comparison.two_step_bridge` for the two-step decomposition that
separates them: `2019_uncorrected` -> `2019c` isolates the correction alone,
`2019c` -> `2022c` isolates the year alone. **Do not present `2019_uncorrected`
and `2022c` side by side as a time series** without that decomposition alongside
them, and do not present `2019a` or `2019b` in such a series at all: they change
the release as well.

## The set

| File | What it shows |
|:---|:---|
| `fig1_ofir_panels` | The submitted figures 1-3 as one panelled figure: activity contribution, sector contribution, geographical origin. Absolute values, bars labelled with their share. |
| `fig1b_activity_absolute` | Activity contribution, absolute, category total in the strip. |
| `fig1c_activity_per_capita` | The same per person, with the per-capita total in each strip. |
| `fig2_top_origin_industry_pairs` | The 20 largest producing region × industry pairs, ranked **within** each indicator, remainder at the foot of each panel. |
| `fig3_scopes_stacked` | GHG-Protocol scope split, all five categories. |
| `fig4_scope2_sources` | Where Scope 2 arises, by region × industry pair. |
| `fig5_scope3_sources` | The same for Scope 3. |
| `fig6_scope_pairs_stacked` | The largest pairs, stacked by scope. |
| `fig7_boundary_matched` | 2022 only. The two boundary steps from this study's headline to Schmidt & Merciai's published value. |
| `fig8_mitigation_waterfall` | 2022 only. Every quantified mitigation lever against the regional target and against demand growth. |
| `fig9_burden_shifting` | 2022 only. Every lever at its most ambitious level against every impact category, as relative change, with a cell outlined where climate improves and another pressure worsens. |
| `figS1_geographical_origin` | Geographical origin on its own, for the SI. |

`fig7`, `fig8` and `fig9` are each guarded to the year their source table was
built for, so a 2019 run cannot republish a 2022 result under a 2019 filename.
`fig8` and `fig9` come from `r/plot_scenarios.r`; the bar version that once
lived in `plot_manuscript_figures.R` was removed, so only one script writes a
figure eight.

## Conventions

Set in `r/_dk_common.r` and applied to every figure:

- TIFF, LZW, 300 dpi, white background, written through `ragg` where installed.
- No title on the image; the caption carries it.
- Legend at the bottom, one row where one row fits; omitted entirely where the
  axis labels already name every series.
- Aspect ratio between 1.4 and 1.8.
- Type sizes ranked: facet title > legend > axis title > tick label, floor 8 pt.
- Tick labels in `#1A1A1A`; `grey15` read as faint at page scale.
- Okabe-Ito palette, one hue per indicator, remainder in grey.

**Remainder bars.** Every top-N ranking shows what it leaves out. Because the
tail of a 200 × 200 MRIO is routinely several times the largest ranked bar, the
remainder is pinned to the foot of each panel, drawn to scale where it fits, and
where it does not the bar is broken and its true share printed beside it. The
axis title says so. Material extraction is the case where the remainder is
smaller than the leading pair, so that bar carries no break, which is the check
that the rule is doing what it claims.

## The cross-year comparison

`comparison/fig10_year_bridge_climate_2019_2022.tiff` decomposes the
2019-to-2022 climate footprint change into its two causes, per activity group:
the Danish sea-transport reallocation (step 1) and the reference year (step
2). Each group is drawn as three markers - 2019 uncorrected, 2019
shipping-corrected, 2022 shipping-corrected - joined by two coloured segments,
one per step, on one shared value axis. Groups are ordered by the size of the
total change, largest at the top, so transport and pharmaceuticals - between
them nearly the whole story - are the first two rows.

**Figure-type reasoning.** A single dumbbell drew this comparison until the
gold layer carried only the two end points; it could not be honest about a
change that is actually two changes overlaid (year AND correction move at
once between the submitted 2019 run and the corrected 2022 headline - see
"The four variants are not interchangeable" above). With the intermediate
point (2019, shipping-corrected) now available, the comparison is drawn as a
connected two-segment dot plot instead: one row per group, two segments per
row, on a shared scale, so a step-1 segment and a step-2 segment sit directly
beside each other and are compared by looking. A two-panel dumbbell (one panel
per step) was rejected because it puts that same comparison across a panel
boundary; a paired slope graph was rejected for spending the horizontal axis
on a categorical "which state" variable and for the line crossings a
direction-changing group (heat and electricity falls in step 1, then rises in
step 2) produces; grouped bars and a waterfall were rejected for the same
reasons the single-year version rejected them - see the script header in
`r/plot_year_bridge.r` for the full argument.

**No note on the image.** Earlier versions of this figure carried a caption on
the image itself, against the house rule, because the two-way comparison
seemed too easy to misread without one. The two-step design removes that need:
the three markers and two connector colours are decoded entirely by the
legend, and the signed delta printed beside each marker (plus an axis title
that says the axis is a level, not a change) keeps a level reading from being
mistaken for a change reading. This is the only figure in the study whose
design changed specifically to get the note off the image.
