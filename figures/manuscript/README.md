# Manuscript figures

One directory per reference year. Both years carry the same figure set, drawn by
the same code from the same tables, so a difference between them is a difference
in the data and never in the plotting.

```bash
# 2022 — EXIOBASE v3.8.2 IOT_2022, Danish sea-transport reallocation applied
HC_ANALYSIS_YEAR=2022 DKHC_FIG_DIR=figures/manuscript/2022 Rscript R/plot_manuscript_figures.R
HC_ANALYSIS_YEAR=2022 DKHC_FIG_DIR=figures/manuscript/2022 Rscript R/plot_absolute_and_percapita.R

# 2019 — EXIOBASE v3.8.2 IOT_2016, the manuscript's own background, UNCORRECTED
HC_ANALYSIS_YEAR=2019 DKHC_FIG_DIR=figures/manuscript/2019 Rscript R/plot_manuscript_figures.R
HC_ANALYSIS_YEAR=2019 DKHC_FIG_DIR=figures/manuscript/2019 Rscript R/plot_absolute_and_percapita.R
```

Run with a UTF-8 locale (`LANG=en_US.UTF-8`). R parses source files in the
process locale, and under `C` the non-ASCII characters in the labels are
mangled — "Södersten" came out as "S..dersten" with no warning.

## The two years are not like for like

| | 2019 | 2022 |
|---|---|---|
| Background | EXIOBASE v3.8.2 IOT_2016 | EXIOBASE v3.8.2 IOT_2022 |
| Danish sea-transport reallocation | **not applied** | applied |
| Climate footprint | 6,361 kt CO₂e | 4,713 kt CO₂e |
| Transport, activity view | 41 % | 13 % |

The 2019 set runs on the background the submitted manuscript used, so it
reproduces the manuscript's transport finding rather than correcting it — in
figure 2 the single pair `DNK – TWAS` carries 27 % of the climate footprint,
which is the phantom shipping the correction removes. That is the point of
having it: it isolates the method change from the year change. **Do not present
the two sets side by side as a time series.** A corrected 2019 run would need a
`_snacship` background built for 2016, which does not exist yet.

## The set

| File | What it shows |
|---|---|
| `fig1_ofir_panels` | The submitted figures 1–3 as one panelled figure: activity contribution, sector contribution, geographical origin. Absolute values, bars labelled with their share. |
| `fig1b_activity_absolute` | Activity contribution, absolute, category total in the strip. |
| `fig1c_activity_per_capita` | The same per person, with the per-capita total in each strip. |
| `fig2_top_origin_industry_pairs` | The 20 largest producing region × industry pairs, ranked **within** each indicator, remainder at the foot of each panel. |
| `fig3_scopes_stacked` | GHG-Protocol scope split, all five categories. |
| `fig4_scope2_sources` | Where Scope 2 arises, by region × industry pair. |
| `fig5_scope3_sources` | The same for Scope 3. |
| `fig6_scope_pairs_stacked` | The largest pairs, stacked by scope. |
| `fig7_boundary_matched` | 2022 only. The two boundary steps from this study's headline to Schmidt & Merciai's published value. |
| `fig8_mitigation_scenarios` | 2022 only. Every quantified mitigation lever against the regional target and against demand growth. |
| `figS1_geographical_origin` | Geographical origin on its own, for the SI. |

`fig7` and `fig8` are guarded to the year their source table was built for, so a
2019 run cannot republish the 2022 comparison under a 2019 filename.

## Conventions

Set in `R/_dk_common.R` and applied to every figure:

- TIFF, LZW, 300 dpi, white background, written through `ragg` where installed.
- No title on the image — the caption carries it.
- Legend at the bottom, one row where one row fits; omitted entirely where the
  axis labels already name every series.
- Aspect ratio between 1.4 and 1.8.
- Type sizes ranked: facet title > legend > axis title > tick label, floor 8 pt.
- Tick labels in `#1A1A1A`; `grey15` read as faint at page scale.
- Okabe–Ito palette, one hue per indicator, remainder in grey.

**Remainder bars.** Every top-N ranking shows what it leaves out. Because the
tail of a 200 × 200 MRIO is routinely several times the largest ranked bar, the
remainder is pinned to the foot of each panel, drawn to scale where it fits, and
where it does not the bar is broken and its true share printed beside it. The
axis title says so. Material extraction is the case where the remainder is
smaller than the leading pair, so that bar carries no break — which is the check
that the rule is doing what it claims.
