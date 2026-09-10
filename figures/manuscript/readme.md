# Manuscript figures

One directory per reference year. Both years carry the same figure set, drawn by
the same code from the same tables, so a difference between them is a difference
in the data and never in the plotting.

```bash
# 2022 - EXIOBASE v3.8.2 IOT_2022, Danish sea-transport reallocation applied
HC_ANALYSIS_YEAR=2022 DKHC_FIG_DIR=figures/manuscript/2022 Rscript R/plot_manuscript_figures.R
HC_ANALYSIS_YEAR=2022 DKHC_FIG_DIR=figures/manuscript/2022 Rscript R/plot_absolute_and_percapita.R
HC_ANALYSIS_YEAR=2022 DKHC_FIG_DIR=figures/manuscript/2022 Rscript R/plot_scenarios.R

# 2019 - EXIOBASE v3.8.2 IOT_2016, the manuscript's own background, UNCORRECTED
HC_ANALYSIS_YEAR=2019 DKHC_FIG_DIR=figures/manuscript/2019 Rscript R/plot_manuscript_figures.R
HC_ANALYSIS_YEAR=2019 DKHC_FIG_DIR=figures/manuscript/2019 Rscript R/plot_absolute_and_percapita.R
```

Run with a UTF-8 locale (`LANG=en_US.UTF-8`). R parses source files in the
process locale, and under `C` the non-ASCII characters in the labels are
mangled: "Södersten" came out as "S..dersten" with no warning.

## The two years are not like for like

| | 2019 | 2022 |
|:---|:---|:---|
| Background | EXIOBASE v3.8.2 IOT_2016 | EXIOBASE v3.8.2 IOT_2022 |
| Danish sea-transport reallocation | **not applied** | applied |
| Climate footprint | 6,361 kt CO₂e | 4,712 kt CO₂e |
| Transport, activity view | 41 % | 13 % |

The 2019 set runs on the background the submitted manuscript used, so it
reproduces the manuscript's transport finding rather than correcting it: in
figure 2 the single pair `DNK - TWAS` carries 27 % of the climate footprint,
which is the phantom shipping the correction removes. That reproduction is the
point of having it: it isolates the method change from the year change. **Do not
present the two sets side by side as a time series.** A corrected 2019 run would need a
`_snacship` background built for 2016, which does not exist yet.

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
`fig8` and `fig9` come from `R/plot_scenarios.R`; the bar version that once
lived in `plot_manuscript_figures.R` was removed, so only one script writes a
figure eight.

## Conventions

Set in `R/_dk_common.R` and applied to every figure:

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

`comparison/fig10_year_bridge_climate_2019_2022.tiff` is a dumbbell plot of the
nine activity groups measured in both years, largest movers first.

**Figure-type reasoning.** The question is a paired comparison over categories:
the same nine groups, measured twice, which moved and by how much. A connected
dot plot shows the pair and makes the change a property of the connector rather
than something the reader must difference by eye. Grouped bars were rejected
because the quantity of interest is the gap between two bars, which is the
hardest thing to read off a bar chart; a waterfall was rejected because it
implies a sequence of steps toward a total, which these groups are not; a slope
graph wastes the horizontal axis on an ordinal year. The house figure library
carries dumbbells as an exemplar type, and this comparison is the canonical use
for it.

**One deliberate deviation.** This figure carries a note on the image, against
the rule that captions belong in the manuscript. The single largest risk with
this figure is that it is read as a trend, and the note prevents that reading
even when the image travels without its caption. No other figure in the study does this.
