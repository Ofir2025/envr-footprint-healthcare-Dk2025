# Manuscript figures

One directory per (reference year, Danish sea-transport correction state)
variant - a 2x2, not two folders - because the transport-share swing the
co-author asked about (roughly 46 % in 2019 down to 15-18 % in 2022) is never
one comparison: reference year, background release, AND the sea-transport
correction all change at once between the submitted 2019 run and the corrected
2022 headline. Splitting "corrected or not" out as its own axis lets the year
effect and the correction effect be read separately. All four variants carry
the same figure set, drawn by the same code from the same tables, so a
difference between them is a difference in the data and never in the plotting.

```bash
# 2022, shipping-corrected - EXIOBASE v3.8.2 IOT_2022 with the Danish
# sea-transport reallocation applied. The manuscript's headline.
HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2022_shipping_corrected Rscript r/plot_manuscript_figures.r
HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2022_shipping_corrected Rscript r/plot_absolute_and_percapita.r
HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2022_shipping_corrected Rscript r/plot_scenarios.r

# 2022, uncorrected - same background, correction NOT applied
HC_ANALYSIS_YEAR=2022 DKHC_FIG_DIR=figures/manuscript/2022_uncorrected Rscript r/plot_manuscript_figures.r
HC_ANALYSIS_YEAR=2022 DKHC_FIG_DIR=figures/manuscript/2022_uncorrected Rscript r/plot_absolute_and_percapita.r

# 2019, shipping-corrected - EXIOBASE v3.8.2 IOT_2016 with the same correction
# applied, so it is comparable with 2022_shipping_corrected on correction state
HC_ANALYSIS_YEAR=2019 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2019_shipping_corrected Rscript r/plot_manuscript_figures.r
HC_ANALYSIS_YEAR=2019 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript/2019_shipping_corrected Rscript r/plot_absolute_and_percapita.r

# 2019, uncorrected - EXIOBASE v3.8.2 IOT_2016, the manuscript's own
# background, exactly as submitted
HC_ANALYSIS_YEAR=2019 DKHC_FIG_DIR=figures/manuscript/2019_uncorrected Rscript r/plot_manuscript_figures.r
HC_ANALYSIS_YEAR=2019 DKHC_FIG_DIR=figures/manuscript/2019_uncorrected Rscript r/plot_absolute_and_percapita.r

# fig10, the cross-year bridge - not tied to any one variant folder, so it
# writes straight into comparison/ rather than one of the four above
DKHC_FIG_DIR=figures/manuscript Rscript r/plot_year_bridge.r
```

Run with a UTF-8 locale (`LANG=en_US.UTF-8`). R parses source files in the
process locale, and under `C` the non-ASCII characters in the labels are
mangled: "Södersten" came out as "S..dersten" with no warning.

## The four variants are not interchangeable

| | 2019_uncorrected | 2019_shipping_corrected | 2022_uncorrected | 2022_shipping_corrected |
|:---|:---|:---|:---|:---|
| Background | EXIOBASE v3.8.2 IOT_2016 | EXIOBASE v3.8.2 IOT_2016 | EXIOBASE v3.8.2 IOT_2022 | EXIOBASE v3.8.2 IOT_2022 |
| Danish sea-transport reallocation | not applied | applied | not applied | applied |
| Reproduces | the submitted manuscript | — | — | the resubmission's headline |

`2019_uncorrected` runs on the background and correction state the submitted
manuscript used, so it reproduces the manuscript's transport finding rather
than correcting it. `2022_shipping_corrected` is the manuscript's headline.
Comparing those two directly - the only pair the figure set drew before this
2x2 existed - mixes the year, the background release, AND the correction; see
`comparison/fig10_year_bridge_climate_2019_2022.tiff` and
`analysis.year_comparison.two_step_bridge` for the two-step decomposition that
separates them: `2019_uncorrected` -> `2019_shipping_corrected` isolates the
correction alone, `2019_shipping_corrected` -> `2022_shipping_corrected`
isolates the year alone. **Do not present `2019_uncorrected` and
`2022_shipping_corrected` side by side as a time series** without that
decomposition alongside them.

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
