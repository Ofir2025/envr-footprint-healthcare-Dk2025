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

Variants b, c and d carry the study's own newer figure set, drawn by the same
code from the same tables, so a difference between them is a difference in the
data and never in the plotting - with the exceptions stated per figure below.
**Variant a carries a different set, and only that set.** There is no `2022a` or
`2022b`: EXIOBASE v3.7's series ends at 2016, so it has no 2022 table and the
release axis collapses for that year.

## Which figure set each variant carries

| Variant | Figure set | Drawn by |
|:---|:---|:---|
| `2019a` | Steenmeijer et al. (2022) figures 1-3 applied to the Danish results, and nothing else | `r/plot_steenmeijer_variant_a.r` |
| `2019b`, `2019c`, `2019d`, `2022c`, `2022d` | the study's newer set, `fig1_ofir_panels` to `figS1` | `r/plot_manuscript_figures.r`, `r/plot_absolute_and_percapita.r`, `r/plot_scenarios.r` |
| `2019_uncorrected`, `2022_uncorrected` | the newer set, as before | the same three scripts |
| `2022c` only, in addition | Steenmeijer et al. (2022) figures 1-3 with the article's labels on the 2022 headline results, in the variant-a palette; and the country-of-origin by sector heat map | `r/plot_steenmeijer_variant_a.r`, `r/plot_origin_sector_heatmap.r` |

**Why variant a differs.** Variant a is the configuration the co-author
submitted on - EXIOBASE v3.7, no Danish sea-transport correction, health-care
boundary, capital excluded - and the three figures above are the three his
submitted manuscript carried: Steenmeijer et al.'s contribution analysis, sector
hotspot analysis and geography hotspot analysis, over all five impact
categories, each stacked to 100 %. The newer set belongs to the work done after
submission. Publishing it under variant a would put figures beside a submitted
estimate that the submission never made, so variant a keeps the submitted record
exactly what it was, and the newer set is drawn for every variant that came
after.

Variant a's three figures match the originals in their groups, in their group
ORDER, in their legend wording including the scope annotations, in their
category labels with units, and in the y-axis title "Contribution (%)". Those
facts are held once, as `STEEN_*` in `r/_dk_common.r`, and read by both the
variant-a script and `r/plot_steenmeijer_replication.r`, so the two cannot drift
apart. Two things are deliberately NOT the original's:

- **The palette.** Paul Tol's `muted` qualitative scheme (SRON/EPS/TN/09-002),
  nine hues plus a pale grey, in place of the article's pastels. It is
  colourblind-safe by construction - built and tested under deuteranopia,
  protanopia and tritanopia - where two of the article's pastels converge under
  deuteranopia and are adjacent in its figure 2 stack. Its near-constant chroma
  makes it read as one designed family, it reserves its pale grey for data that
  is not a category of its own, which is exactly what the "Other" bucket is, and
  it is distinct from this repository's house Okabe-Ito set, so a variant-a panel
  cannot be mistaken for one of the newer figures. A group appearing in more than
  one of the three figures keeps one colour across them, which the article itself
  does not do.
- **Share labels.** Every stacked segment carries its own percentage at the
  segment's midpoint, in whichever of near-black and white has the higher WCAG
  contrast against that fill. **Segments below 3 % are drawn but not labelled**:
  at this canvas a 3 % segment is about 15 pt tall against a 12.5 pt label, so
  anything smaller overprints its neighbours. The x-axis title says so on the
  figure.

## Which figures exist for which variant

| Figure | 2019a | 2019b | 2019c | 2019d | 2019_uncorrected | 2022c | 2022d | 2022_uncorrected |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| `fig1_contribution_product_group` | yes | - | - | - | - | - | - | - |
| `fig2_hotspot_sector` | yes | - | - | - | - | - | - | - |
| `fig3_hotspot_geography` | yes | - | - | - | - | - | - | - |
| `fig1_contribution_product_group`, `fig2_hotspot_sector`, `fig3_hotspot_geography` on the 2022 results | - | - | - | - | - | yes | - | - |
| `figS2_origin_sector_heatmap` | - | - | - | - | - | yes | - | - |
| `fig1_ofir_panels` | - | yes | yes | yes | yes | yes | yes | yes |
| `fig1b_activity_absolute` | - | yes | yes | yes | yes | yes | yes | yes |
| `fig1c_activity_per_capita` | - | yes | yes | yes | yes | yes | yes | yes |
| `fig2_top_origin_industry_pairs` | - | yes | yes | yes | yes | yes | yes | yes |
| `fig3_scopes_stacked` | - | yes | yes | yes | **no** | yes | yes | yes |
| `fig4_scope2_sources` | - | yes | yes | yes | **no** | yes | yes | yes |
| `fig5_scope3_sources` | - | yes | yes | yes | **no** | yes | yes | yes |
| `fig6_scope_pairs_stacked` | - | yes | yes | yes | **no** | yes | yes | yes |
| `fig7_boundary_matched` | - | **no** | **no** | **no** | **no** | yes | yes | **no** |
| `fig8_mitigation_waterfall` | - | **no** | **no** | **no** | **no** | yes | **no** | **no** |
| `fig9_burden_shifting` | - | **no** | **no** | **no** | **no** | yes | **no** | **no** |
| `figS1_geographical_origin` | - | yes | yes | yes | yes | yes | yes | yes |

A `-` is a figure that is not part of that variant's set at all; a **no** is a
figure of that variant's set that the data cannot support, and every one of them
is a withheld figure rather than a missing one:

- **Figures 3 to 6 of `2019_uncorrected`.** `02_scopes_wood_hertwich` publishes
  no tables for that run, so `plot_manuscript_figures.r` says so and skips those
  four rather than aborting. The reason is in "Which variants can draw figures 3
  to 6" below.
- **Figure 7, `2019*` and the uncorrected runs.** The benchmark table it draws
  is built on the 2022 shipping-corrected background, and the script is guarded
  to that year and correction state so a 2019 run cannot republish a 2022 result
  under a 2019 filename. Note that figure 7 is a boundary LADDER whose first bar
  is variant c and whose last bar is variant d, so it is not a per-variant
  result: the file in `2022c/` and the file in `2022d/` are byte-identical by
  construction, and the bars name their own boundary and capital treatment.
- **Figures 8 and 9, everything but `2022c`.** `18_mitigation_scenarios`
  publishes ONE scenario layer, whose baseline climate footprint is 4,266.88 kt
  - variant 2022c exactly. `plot_scenarios.r` stops unless the run is 2022, and
  running it under `2022d` would put variant c's baseline and levers in variant
  d's folder. It is therefore run for `2022c` and for nothing else.

## Which file replaces which figure in the submitted manuscript

The submitted manuscript carries three separate figures and Appendix A carries one.
The post-submission set does not map onto them one for one, because
`fig1_ofir_panels` deliberately draws all three of the submitted figures as panels
of a single figure. Dropping the current images in is therefore a decision about
the revision's figure plan, not a substitution, and the table below is what that
decision is between.

The decision, taken on 2026-09-12, was to collapse the submitted three into one
panelled figure and spend the two freed slots on cuts the submission did not have.
The journal's guide asks for three to five figures in a Research Article, so the
revision carries three.

| Revised manuscript | File, variant `2022c` | Was |
|:---|:---|:---|
| Figure 1, panels A, B, C | `fig1_ofir_panels_2022.tiff` | the submitted Figures 1, 2 and 3 |
| Figure 2 | `fig2_top_origin_industry_pairs_2022.tiff` | new: producing region by industry |
| Figure 3 | `fig3_scopes_stacked_2022.tiff` | new: the GHG Protocol scope partition, and the producing industry groups behind Scope 3 |

Everything else moved into Appendix A, which carries sixteen figures, A1 to A16,
each cited from the manuscript: the integration diagram (A1), the largest pairs by
scope and the scope sources (A2 to A4), per-person contributions (A5), the origin by
sector heat map (A6), the three reference years and the climate bridge between them
(A7 to A10), the boundary-matched benchmark ladder (A11) and five uncertainty
figures (A12 to A16). `figures/uncertainty/*.png` and
`figures/manuscript/comparison/*.tiff` are the sources for those.

Three figures left Appendix A on 14 September 2026. The absolute contributions
figure repeated Fig. 1A in units Table A.1 already gives, and the geography panel
on its own (`figS1_geographical_origin`) repeated Figure 1C, so the heat map took its
place. The two mitigation scenario figures (`fig8_mitigation_waterfall`,
`fig9_burden_shifting`) are held back for the follow-up paper, which evaluates
mitigation: the revision identifies where impacts arise and does not estimate
mitigation potential. Both figures, `plot_scenarios.r` and the scenario layer stay
in the working copy for that paper and are withheld from the published branch.

Collapsing the three costs the shared legend nothing, because `fig1_ofir_panels`
was drawn as one figure from the start; what it costs is vertical space, so the
panel figure needs a full page in the typeset article.

`r/plot_steenmeijer_variant_a.r` draws Steenmeijer et al.'s three-figure form for
variant `a`, the configuration the manuscript was submitted on, and, since
2026-09-14 and at the authors' request, for the 2022c headline as well. The
post-submission set is still never drawn under variant `a`, because that would
put figures beside an estimate the submission never made.

## Captions the figures do not carry

No figure in this study carries a title, a note or a caption. Two sentences that
a reader of figures 2, 5 and 6 needs are therefore recorded here, to be used as
caption text in the manuscript and the SI:

**The remainder bar.** *A top-N ranking must show what it leaves out. The
remainder sits at the foot of each panel; where it exceeds the ranked bars its
own bar is broken and its true share printed, so the ranking is not flattened
into slivers by a tail that is several times the largest ranked bar.* Until
2026-09-11 this sentence was concatenated into the x-axis title of those three
figures, which put 150 characters under the panels and left the axis title
itself unreadable.

**The heat map's caption**, as placed in Appendix A (Fig. A.6). *Environmental
impacts associated with Danish health care in 2022 by country or region of
production (columns) and producing sector group (rows), for the five impact
categories. Each cell is a share of the category's total footprint, given in the
panel title; white cells have no footprint. Region codes are as in Fig. 2 of the
main text. Private travel (direct) is the vehicle emissions of commuting and
patient and visitor travel; its supply chains have no country of production and
are not shown (6.7% of climate change, under 1% of each other category).* The
longer draft, with every share and the region codes spelled out, took the
caption past the foot of the page.

**The axis labels are codes.** *Region and EXIOBASE industry codes are used on
the y axis of figures 2, 4, 5 and 6. Full EXIOBASE industry names run to 90
characters and reduce the plotting panel to a sliver; the names are one join
away, in `data/gold/results/star/dim_industry.csv` and in each layer's data
dictionary.*

## Value labels

Every ranked bar carries its value, and every point of the comparison series
carries its value. Labels sit outside the bar end in the ink colour, never
inside: a 0.8 % share in a panel whose largest bar is 2.6 % has no room inside
it, and a rule that labels only the bars wide enough to hold a label is the rule
that left the tallest bars of figures 2, 4 and 5 carrying no number at all until
2026-09-11. `ranked_labels()` in `r/_dk_common.r` is the single implementation;
`facet_ceiling(room = )` reserves the headroom it needs.

Since 2026-09-14 every ranked bar and the remainder bar carry the same label:
one decimal and a percent sign ("4.7%", "43.3%", "67.4%"), in the same size and
weight. Until then small bars printed "4.7", large ones "43" and the remainder a
bold "67%", which read as three different quantities. The pair codes on the y
axis of figures 2, 4, 5 and 6 are set in black in the regular sans face; the
monospaced face they used rendered thin enough to read as faint.

## The comparison series

`comparison/` holds the figures that run across the three reference years rather
than within one. They are drawn from
`data/gold/results/01_eriksen_replication/variant_comparison.csv` by
`r/plot_year_comparison.r`, which needs only `DKHC_FIG_DIR=figures/manuscript`:

| figure | content |
|:---|:---|
| `fig11_footprint_by_year.tiff` | the health-care footprint in 2016, 2019 and 2022, one panel per indicator, one line per boundary |
| `fig12_share_of_national_by_year.tiff` | the same three years as a share of the Danish national footprint |
| `fig13_activity_groups_by_year.tiff` | what each activity group contributed to the climate footprint in each year, grouped bars ranked by the latest year |
| `fig10_year_bridge_climate_2016_2022.tiff` | the three-step bridge across all three reference years: the shipping correction on 2016, then 2016 to 2019, then 2019 to 2022 |

**The bridge spans all three years.** `fig10` used to run 2019 to 2022 in two
steps, because no 2016 analysis existed. It now chains four states - 2016 before
the shipping correction, 2016 after it, 2019, 2022 - so the correction is
isolated on the earliest year and the two reference-year steps run on a
configuration that does not otherwise change. The correction is a one-off
−2,196 kt, of which transport is −1,727; the year steps are +186 kt
(2016→2019) and +271 kt (2019→2022), the latter dominated by pharmaceuticals at
+657 kt. A step is labelled only when it moves at least 20 kt: below that the
segment is too short to hold a number, and the value is in
`06_benchmarks_validation/year_comparison_two_step_bridge.csv`.

**Connected dots, not an area plot.** With three observations an area plot draws
the region under a curve whose shape between the points is an artefact of the
interpolation, and stacking those areas makes the composition legible only for
the band at the base. Cleveland's ordering of elementary perceptual tasks puts
position along a common scale first and area seventh, so with three points the
honest encodings are position and length: a connected dot plot for the levels, a
grouped bar for the composition. The line carries no claim about the years
between the points; it says only that the dots are one series in time order.

Only variants `c` and `d` form a series: they exist in all three years on one
release with the shipping correction applied. `a` and `b` are EXIOBASE v3.7,
which publishes no table after 2016, so they exist for 2019 alone and are not
drawn as a trend.

## Rendering

Every command below carries `LANG=en_US.UTF-8` so it can be copied and pasted as
it stands. `r/_dk_common.r` stops with that instruction if the locale is not
UTF-8, because a C locale drops CO₂, Mm³ and km² to `..` in every figure, and
prose above a code block is not a prefix.

All five model-selecting variables are set on every line, even where the value is
the default, so a line is self-contained and an exported `HC_*` left over from an
earlier run cannot silently change which variant is drawn.

```bash
# DKHC_FIG_DIR means two different things below, which is a trap worth naming.
# For `plot_steenmeijer_variant_a.r` it is the PARENT and the script appends the
# folder variant_name() resolved. For `plot_manuscript_figures.r`,
# `plot_absolute_and_percapita.r` and `plot_year_comparison.r` it is the folder
# written to directly. Passing the parent to the second kind writes every TIFF
# to `figures/manuscript/` instead of the variant folder, silently.

# ---- variant a: Steenmeijer figures 1-3, and only those --------------------
# EXIOBASE v3.7 IOT_2016, uncorrected: the release and correction state the
# manuscript was submitted on. HC_EXIOBASE_RELEASE is what selects it; without
# it the run is v3.8.2 and is NOT variant a.
#
# DKHC_FIG_DIR is the PARENT here, not the variant folder: this script appends
# the folder that variant_name() resolved, the same resolver that chose the gold
# tables, so one variant's numbers cannot be written into another's folder.
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_7 HC_BACKGROUND_TAG= HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript Rscript r/plot_steenmeijer_variant_a.r

# ---- 2016c and 2016d: the earliest year of the series -----------------------
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2016 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2016c Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2016 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=zorg_en_welzijn HC_CAPITAL=endogenised DKHC_FIG_DIR=figures/manuscript/2016d Rscript r/plot_manuscript_figures.r

# ---- the comparison series across 2016, 2019 and 2022 -----------------------
LANG=en_US.UTF-8 DKHC_FIG_DIR=figures/manuscript Rscript r/plot_year_comparison.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship DKHC_FIG_DIR=figures/manuscript Rscript r/plot_year_bridge.r

# ---- variant b: v3.7, shipping-corrected ------------------------------------
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_7 HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2019b Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_7 HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2019b Rscript r/plot_absolute_and_percapita.r

# ---- 2019c: v3.8.2 IOT_2016, corrected, so it is comparable with 2022c on
# release, correction, boundary and capital alike ----------------------------
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2019c Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2019c Rscript r/plot_absolute_and_percapita.r

# ---- 2019d: the widest boundary on the 2016 table ---------------------------
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=zorg_en_welzijn HC_CAPITAL=endogenised DKHC_FIG_DIR=figures/manuscript/2019d Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=zorg_en_welzijn HC_CAPITAL=endogenised DKHC_FIG_DIR=figures/manuscript/2019d Rscript r/plot_absolute_and_percapita.r

# ---- 2022c: the manuscript's headline. The only variant that draws figures
# 8 and 9, because the scenario layer's baseline IS this variant -------------
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2022c Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2022c Rscript r/plot_absolute_and_percapita.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2022c Rscript r/plot_scenarios.r
# Steenmeijer et al.'s three figures on the 2022 results (DKHC_FIG_DIR is the parent)
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript Rscript r/plot_steenmeijer_variant_a.r
# the country-of-origin by sector heat map (Fig. A.6) and the demand integration diagram (Fig. A.1)
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2022c Rscript r/plot_origin_sector_heatmap.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/diagrams Rscript r/plot_integration_diagram.r

# ---- 2022d: the same year and correction, child care inside the boundary and
# consumption of fixed capital inside the Leontief inverse. plot_scenarios.r is
# deliberately NOT run here - see "Figures 8 and 9" above -------------------
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=zorg_en_welzijn HC_CAPITAL=endogenised DKHC_FIG_DIR=figures/manuscript/2022d Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG=_snacship HC_SCOPE=zorg_en_welzijn HC_CAPITAL=endogenised DKHC_FIG_DIR=figures/manuscript/2022d Rscript r/plot_absolute_and_percapita.r

# ---- 2019_uncorrected: v3.8.2 IOT_2016 with no correction. NOT variant a: the
# submitted estimate was computed on v3.7, which 2019a runs -----------------
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG= HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2019_uncorrected Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG= HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2019_uncorrected Rscript r/plot_absolute_and_percapita.r

# ---- 2022_uncorrected: same background as 2022c, correction NOT applied -----
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG= HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2022_uncorrected Rscript r/plot_manuscript_figures.r
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 HC_BACKGROUND_TAG= HC_SCOPE=health_eldercare HC_CAPITAL=excluded DKHC_FIG_DIR=figures/manuscript/2022_uncorrected Rscript r/plot_absolute_and_percapita.r

# ---- fig10, the cross-year bridge - not tied to any one variant folder, so it
# writes straight into comparison/ rather than one of the variant folders -----
LANG=en_US.UTF-8 DKHC_FIG_DIR=figures/manuscript Rscript r/plot_year_bridge.r

# ---- the four scope-emission TIFFs, which live in figures/scopes/ rather than
# here and name their variant in the filename; the tag is not optional, because
# without it the layer resolves to the uncorrected run ------------------------
LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship Rscript r/plot_scope_emissions.r
```

The locale matters twice over. R also parses source files in the process locale,
and under `C` the non-ASCII characters in the labels are mangled: "Södersten"
came out as "S..dersten" with no warning.

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
byte-identical to `2022c`'s: the transport industry group carries 34.07 % of the
climate footprint in the uncorrected run against 15.59 % in the corrected one,
which is the difference the variant scheme exists to show.

| Variant | Figures 1, 2, S1 | Figures 3-6 |
|:---|:---|:---|
| `2019b` | yes | yes |
| `2019c` | yes | yes |
| `2019d` | yes | yes |
| `2022c` | yes | yes |
| `2022d` | yes | yes |
| `2022_uncorrected` | yes | yes |
| `2019_uncorrected` | yes | yes |

`2019a` is not in this table: it carries the Steenmeijer set instead, which has
no scope partition in it. Its scope tables exist in
`02_scopes_wood_hertwich/2019a/` all the same, and the scope figures could be
drawn from them if the set for that variant ever changed.

`2019_uncorrected` used to be the one gap: figures 3 to 6 were withheld for it
on the grounds that the uncorrected and shipping-corrected 2016 model objects
descended from two different extractions of `IOT_2016_ixi`. That diagnosis was
wrong - the two objects' $A$, $Y$, $R$, $H$ and $x$ are byte-identical, and what
differed was the climate row of the characterisation matrix, IPCC AR4 in one and
IPCC AR6 in the other. With both 2016 backgrounds on AR6 the partition closes on
that run's own grand total to the last digit, `02_scopes_wood_hertwich/2019_uncorrected`
is published, and all four figures draw. The measurement is recorded in
[docs/revision/defects_and_fixes.md](../../docs/revision/defects_and_fixes.md).
Its transport share is readable from `01_eriksen_replication/2019_uncorrected`
(47.43 % of the climate footprint, against 21.30 % at variant c).

## The variants are not interchangeable

| | 2019a | 2019b | 2019c | 2019d | 2019_uncorrected | 2022c | 2022d | 2022_uncorrected |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| Background | v3.7 IOT_2016 | v3.7 IOT_2016 | v3.8.2 IOT_2016 | v3.8.2 IOT_2016 | v3.8.2 IOT_2016 | v3.8.2 IOT_2022 | v3.8.2 IOT_2022 | v3.8.2 IOT_2022 |
| Danish sea-transport reallocation | not applied | applied | applied | applied | not applied | applied | applied | not applied |
| Boundary | health care | health care | health care | + child and elder care | health care | health care | + child and elder care | health care |
| Capital | excluded | excluded | excluded | endogenised | excluded | excluded | endogenised | excluded |
| Climate total, kt CO₂e | 8,152.69 | 6,088.38 | 3,995.59 | 6,018.05 | 6,309.86 | 4,266.88 | 6,220.59 | 5,688.08 |
| Transport share | 36.78 % | 17.45 % | 21.30 % | 19.36 % | 47.43 % | 15.58 % | 14.63 % | 34.06 % |

`2019a` runs the release and correction state the submitted manuscript used, and
it does **not** reproduce the submitted 46 % transport share: it returns 36.78 %,
or 35.01 % on the submission's own valuation, which mapped distribution margins to
the goods. `2019_uncorrected`, which is the same year and correction state on v3.8.2
rather than v3.7, returns 47.43 %, or 46.99 % on the submission's valuation, and is
the run that reproduces the submitted finding. The two submission-valuation shares
are from the runs of 12 September 2026 and have not been re-run since commuting was
estimated directly on 14 September.
`2022c` is the manuscript's headline. Comparing `2019_uncorrected` with `2022c`
directly - the only pair the figure set drew before the variant scheme existed -
mixes the year with the correction; see
`comparison/fig10_year_bridge_climate_2016_2022.tiff` and
`analysis.year_comparison.two_step_bridge` for the two-step decomposition that
separates them: `2019_uncorrected` -> `2019c` isolates the correction alone,
`2019c` -> `2022c` isolates the year alone. **Do not present `2019_uncorrected`
and `2022c` side by side as a time series** without that decomposition alongside
them, and do not present `2019a` or `2019b` in such a series at all: they change
the release as well.

## The set

**Variant a's set** (`r/plot_steenmeijer_variant_a.r`). The filenames carry the
variant letter, which the newer set's do not: these three are the only figures
that will be laid beside the submitted manuscript, and a TIFF pulled out of its
folder must still say which model run it came from.

| File | What it shows |
|:---|:---|
| `fig1_contribution_product_group_2019a` | Contribution analysis: what health care BUYS, by product group, all five categories, stacked to 100 %. Steenmeijer figure 1. |
| `fig2_hotspot_sector_2019a` | Sector hotspot analysis: where the impact PHYSICALLY OCCURS, by industry group. Steenmeijer figure 2. |
| `fig3_hotspot_geography_2019a` | Geography hotspot analysis: in which world region it occurs. Steenmeijer figure 3. |

**The newer set** (variants b, c, d and the two uncorrected runs).

| File | What it shows |
|:---|:---|
| `fig1_ofir_panels` | The submitted figures 1-3 as one panelled figure: activity contribution, sector contribution, geographical origin. Absolute values, bars labelled with their share. |
| `fig1b_activity_absolute` | Activity contribution, absolute, category total in the strip. |
| `fig1c_activity_per_capita` | The same per person, with the per-capita total in each strip. |
| `fig2_top_origin_industry_pairs` | The 20 largest producing region × industry pairs, ranked **within** each indicator, remainder at the foot of each panel. |
| `fig3_scopes_stacked` | GHG-Protocol scope split, all five categories, beside Scope 3 broken down by producing industry group. Drawn at 6.69 by 4.6 in. |
| `fig4_scope2_sources` | Where Scope 2 arises, by region × industry pair. |
| `fig5_scope3_sources` | The same for Scope 3. |
| `fig6_scope_pairs_stacked` | The largest pairs, stacked by scope. |
| `fig7_boundary_matched` | 2022 corrected runs only. The two boundary steps from this study's headline to Schmidt & Merciai's published value. |
| `fig8_mitigation_waterfall` | Withheld for the follow-up paper. |
| `fig9_burden_shifting` | Withheld for the follow-up paper. |
| `figS1_geographical_origin` | Geographical origin on its own. No longer in Appendix A, where it repeated Figure 1C. |

`fig7`, `fig8` and `fig9` are each guarded to the year their source table was
built for, so a 2019 run cannot republish a 2022 result under a 2019 filename.
`fig8` and `fig9` come from `r/plot_scenarios.r`, which is run for `2022c`
alone because the scenario layer's baseline is that variant; the bar version
that once lived in `plot_manuscript_figures.R` was removed, so only one script
writes a figure eight.

## Conventions

Set in `r/_dk_common.r` and applied to every figure:

- TIFF, LZW, 300 dpi, white background, written through `ragg` where installed.
- No title on the image; the caption carries it.
- Legend at the bottom, one row where one row fits; omitted entirely where the
  axis labels already name every series.
- Aspect ratio between 1.4 and 1.8, except figures drawn at the full printed page
  width, where the page sets it (figures 1 and 2 are about 1.05, the heat map 0.81).
- Type sizes ranked: facet title > legend > axis title > tick label, floor 8 pt,
  a floor that only means something at the printed size (see "Print size" below).
- Tick labels in `#1A1A1A`; `grey15` read as faint at page scale.
- Climate change is labelled "kt CO₂e", as the manuscript writes it, in every figure;
  until 14 September 2026 the R figures read "kt CO₂-eq".
- Okabe-Ito palette, one hue per indicator, remainder in grey.
- In figure 1 (and figS1) the world regions of panel C take hues of their own,
  none repeated from panels A and B: Denmark `#872010`, Europe `#536389`, Asia
  and Pacific `#C46D3A`, Middle East `#E4C0A4`, America `#31D9F1`, Africa
  `#96D77E`. Panel C holds places only: since 14 September 2026 the travel
  supply chains, which have no country of production (6.75 % of climate change),
  are left out of it, as they are of the heat map and Table A.3, and the caption
  gives the share; until then they were a grey "Travel supply chains, no region"
  bar. They were chosen from an
  HCL grid to maximise the smallest CIE Lab distance to the other eleven
  colours and to each other under normal vision and deuteranopia, protanopia and
  tritanopia simulation; the closest pair is 13.5 Delta E.

### Print size

A size set in points is a size on paper only if the canvas is as wide as the
printed figure. The manuscript and Appendix A place every figure across their
text width, 6.69 in, and the typeset article prints a full-width figure at 7.48 in
(190 mm), so the size that reaches the reader is

$$
s_{\text{print}} = s_{\text{canvas}} \times \frac{w_{\text{print}}}{w_{\text{canvas}}}
$$

Measured on 14 September 2026 at the 6.69 in the Word files use:

| Figure | Canvas width, in | Smallest labels on the canvas, pt | Same labels on paper, pt |
|:---|---:|:---|:---|
| Figure 1, `fig1_ofir_panels` | 6.69 | bar shares 6, group names 7, tick labels 6.5, strips 8 | the same |
| Figure 2, `fig2_top_origin_industry_pairs` | 6.69 | bar shares 5.5, pair codes and ticks 6.5, strips 8 | the same |
| Figure 3, `fig3_scopes_stacked` | 6.69 | segment shares 6, category names 7, legend 7.5, panel titles 8.5 | the same |
| Steenmeijer figures 1 to 3, 2022c | 16.0 | segment shares and category labels 12.5, legend 14 | 5.2, 5.9 |
| Appendix A figures drawn in R (Figs. A.1 to A.5, A.7 to A.11) | 6.69 | value labels 6, ticks 6.5, labels 7, titles 8 | the same |
| Appendix A uncertainty figures, matplotlib (Figs. A.12 to A.16) | 6.69 | annotations 6, ticks and labels 7, titles 8.5 | the same |
| Heat map, `figS2_origin_sector_heatmap` | 6.69 | country codes 6.5, in-cell shares 5.5, row labels 7.2, all else 7.5 to 9 | the same |

Figures 1, 2 and 3 and the heat map are drawn at their printed size since 14
September 2026; until then figures 1 and 2 printed their labels at 3 to 4 pt.
Figure 1 now takes 6.69 by 6.3 in and figure 2 6.69 by 6.4 in, close to a page each:
figure 1 wraps its group names at 24 characters and its category names at 16, and
drops the tick at each panel's right edge, which ran into the next panel's zero;
figure 2's remainder bar is "All other pairs", because "Remaining regions and sector
pairs" was the widest label and cost each panel a fifth of its width. The Appendix A
figures followed on the same day, so every figure in the manuscript and Appendix A is
drawn at its printed width. Fig. A.1 is no longer the co-author's diagram, a 1,340-pixel
picture with no source that still said "Danish SUT categories" and product code
06130; `r/plot_integration_diagram.r` draws it from the table of record into
`figures/diagrams/demand_integration.tiff`.

Variant a's three figures set two of these aside on purpose, and only these
two: the legend is on the RIGHT, because eight legend entries of up to 56
characters do not read at the foot of a 100 % bar chart and the right-hand
legend runs top-to-bottom in the same order as the stack, which is how the
original is meant to be read; and the palette is Paul Tol's `muted` rather than
Okabe-Ito, for the reasons given under "Which figure set each variant carries".
No title and no caption on the image is the rule that is NOT set aside
anywhere.

**Steenmeijer's figures on 2022c.** The three variant-a figures are also drawn on
the headline run, with the article's groups, group order, legend wording and
category labels, in the variant-a palette (Paul Tol's muted scheme, never the
article's own colours), so the Danish 2022 result can be read in the article's
form beside the manuscript's panelled figure 1. The category labels are set as
plotmath with the article's line breaks, so the subscript of CO2 is drawn by
the math engine. The geography figure follows the article in taking the
undistributed travel component out of the base, which is why Denmark's share
there (34 %) differs from figure 1's 31 %.

**The origin by sector heat map** (`figS2_origin_sector_heatmap`) is drawn at
the size it prints, 6.69 by 8.3 in at 600 dpi, because Appendix A prints figures
across its full text width (A4 with 2 cm side margins). Every size in the script
is therefore a point size on paper: panel titles 9 pt; region groups, legend and axis title 7.5 pt; row labels
7.2 pt; country codes 6.5 pt; in-cell shares 5.5 pt. At 8.6 in the figure and its
caption did not fit one A4 page, so the caption was stranded on the next. Until
14 September 2026 it was drawn 22 in wide with 10.5 to 13 pt labels, which Word
shrank to 3 to 4 pt. Its columns are the 49 EXIOBASE countries and regions of
production and nothing else, grouped by world region under a rule that spans each
group's columns, in the order Denmark, Europe, Africa, Asia and Pacific, Middle
East, America: that order keeps each two- or three-column group beside a wide one,
where ranking the groups by share put "Middle East" beside "Africa" and the two
names read as "East Africa". The rows are the ten producing sector groups with
the largest share of any one category and one pooled "Other sector groups" row,
ranked by mean share; thirteen rows per panel would have needed 6 pt labels. Each
panel title carries the category's total footprint, which is what 100 % means in
that panel. The fill is the cell's share of that total in eight ColorBrewer YlOrRd
bins, white for no footprint with its own key, and cells of 10 % or more print
their share.

**What the heat map leaves out, and why.** The per-kilometre travel inventory
splits commuting and patient and visitor travel into the vehicles' direct
emissions, which occur in Denmark and are drawn there as "Private travel
(direct)", and an indirect part, fuel supply and vehicle manufacture, which it
quantifies without any country of production. That part is not drawn, because a
"No region" column would be a column that is not a place: it is 6.75 % of
climate change, 0.91 % of material extraction, 0.30 % of blue water consumption,
0.05 % of land use and none of waste generation, and the script prints these
shares on every run. The shares keep the whole footprint as their base, so every
cell agrees with figure 1 and each panel sums to 100 % less that part.
Steenmeijer et al. (2022) leave the same component out of their geography figure.

**Figure 3's Scope 3 column.** Scope 3 is 89 % of the climate footprint and all
but a fraction of the other four categories, so a bar that only says so hides the
result. The right-hand panel breaks Scope 3 down by the producing industry group it
arises in, using Figure 1B's group names wherever the grouping is the same
(agricultural sector, mining of minerals and metals, fossil fuel industry,
pharmaceutical and chemical industry, electricity sector, transport) plus three
groups that are "Other" in Figure 1B but matter inside Scope 3: services, waste
management and employee commuting. Its colours are not Figure 1B's, because Figure
1B's blue, green and orange are the scope colours in the left panel; they were
chosen to stay at least 10 CIE Lab units from every other colour in the figure
under deuteranopia, protanopia and tritanopia simulation. The left-hand totals are
those the scope partition covers, which exclude the health sector's own
self-supply loop, so climate change reads 4,265 kt and waste generation 219 kt
against headlines of 4,267 and 221 kt; the caption says so.

**Remainder bars.** Every top-N ranking shows what it leaves out. The
remainder is ranked by its own value like every other bar and drawn to scale,
with no break and no note; in figure 2's material extraction panel, for
instance, it sits second, below the Danish sand and clay node. It keeps its grey so
it reads as a residual rather than as a category.

## The cross-year comparison

`comparison/fig10_year_bridge_climate_2016_2022.tiff` decomposes the
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
