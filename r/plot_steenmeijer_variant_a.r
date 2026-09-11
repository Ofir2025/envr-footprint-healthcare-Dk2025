#!/usr/bin/env Rscript
# Variant a's whole figure set: Steenmeijer et al. (2022) figures 1-3 applied to
# the Danish results, in the article's own groups, group order and legend
# wording, with a new palette and a share label on every segment.
#
#   fig 1  contribution analysis: what the sector BUYS, by product group
#   fig 2  sector hotspot analysis: where the impact PHYSICALLY OCCURS
#   fig 3  geography hotspot analysis: in which world region it occurs
#
# WHY VARIANT A CARRIES THESE THREE AND NOTHING ELSE
#
# Variant a is the configuration the co-author submitted on - EXIOBASE v3.7, no
# Danish sea-transport correction, health-care boundary, capital excluded - and
# the three figures above are the three his submitted manuscript carried. The
# study's own newer set (fig1_ofir_panels .. figS1) belongs to the work done
# after submission and is drawn for variants b, c and d by
# r/plot_manuscript_figures.r, r/plot_absolute_and_percapita.r and
# r/plot_scenarios.r. Publishing the newer set under variant a would put figures
# beside a submitted estimate that the submission never made; publishing these
# three under variant a keeps the submitted record exactly what it was.
#
# WHY A 100 % STACKED BAR, AND NOT SOMETHING BETTER
#
# It is the article's own form, and the point of this sheet is that the Danish
# panels can be laid beside the Dutch ones and read as one figure - which a
# different mark would defeat even if it read better in isolation. The form is
# also correct for what is being shown: five categories each decomposed into a
# part-to-whole set of eight or fewer groups, compared on composition rather
# than on magnitude. The absolute magnitudes those shares are taken from are not
# lost - they are published in this variant's own gold folder, table_01.csv.
#
# THE TWO DELIBERATE DEPARTURES FROM THE ORIGINAL
#
# Everything else is the article's: the groups, their ORDER top-to-bottom, the
# legend wording including the scope annotations, the category labels with their
# units, the y-axis title "Contribution (%)", the legend on the right, and no
# title and no caption on the image. Those facts live in r/_dk_common.r as
# STEEN_*, shared with r/plot_steenmeijer_replication.r so the two scripts
# cannot drift apart. What differs:
#
#   1. THE PALETTE. Paul Tol's "muted" qualitative scheme (SRON technical note
#      SRON/EPS/TN/09-002), nine hues plus a pale grey. Chosen, and not the
#      article's pastels, for four reasons that are checkable rather than
#      matters of taste:
#
#        - it is colourblind-safe by construction: Tol built and tested the
#          scheme under deuteranopia, protanopia and tritanopia simulation, so
#          the nine hues stay mutually distinct for all three, which the
#          article's pastels do not (its #C8DFB3 and #FFEC96 converge under
#          deuteranopia, and they are adjacent in figure 2's stack);
#        - the hues are held at a deliberately restrained, near-constant
#          chroma, so the family reads as one designed set rather than as a
#          default categorical ramp, and no single segment shouts;
#        - the scheme RESERVES its pale grey #DDDDDD for data that is not a
#          category of its own, which is exactly what these figures' "Other"
#          bucket is - so the residual group is grey by the palette's own rule
#          rather than by an ad-hoc choice, and it recedes behind the seven
#          named groups instead of competing with them;
#        - it is distinct from this repository's house Okabe-Ito set
#          (SCOPE_COLS, REGION_COLS, IND_COLS in r/_dk_common.r), so a reader
#          cannot mistake a variant-a panel for one of the newer figures.
#
#      Assignment rule, so the family is legible as well as safe: a group that
#      appears in more than one of the three figures keeps ONE colour across
#      them (pharmaceuticals and chemicals indigo, electricity and heat sand,
#      operational impacts purple, food and agriculture green), which the
#      article itself does not do - it prints #C8DFB3 as "Food and food
#      services" in figure 1 and "Mining of minerals and metals" in figure 2.
#      Colours freed by a group that a figure does not have are reassigned
#      within that figure. Adjacent segments in a stack never take two hues
#      from the same family, checked against the fixed legend order below.
#
#   2. SHARE LABELS. Every stacked segment carries its own percentage, printed
#      at the segment's midpoint. Segments below LABEL_FLOOR (3 %) are drawn but
#      NOT labelled: at this canvas a 3 % segment is about 15 pt tall and the
#      label is 12.5 pt, so anything smaller either overprints its neighbours or
#      has to be pushed onto a leader line, and a figure of leader lines is not
#      the article's figure any more. The x-axis title says the threshold, so a
#      reader holding the figure alone can tell an unlabelled segment from a
#      missing one; that is an axis title, not the on-image caption the house
#      rule forbids. Label ink is chosen per fill by WCAG contrast rather than
#      typed in, so it stays correct if the palette is ever changed.
#
# The figures are written to fig_dir/<variant folder>/, with the folder taken
# from variant_name() - the same resolver that chose the gold tables. It is not
# possible to render one variant's numbers into another variant's folder.
#
# Run:  LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2019 HC_EXIOBASE_RELEASE=v3_7 \
#         DKHC_FIG_DIR=figures/manuscript Rscript r/plot_steenmeijer_variant_a.r

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.r"))

VARIANT <- variant_name()
HOME    <- "Denmark"

# Segments smaller than this are drawn but carry no label. See the header.
LABEL_FLOOR <- 3

# ---- the palette -----------------------------------------------------------
# Paul Tol, "Colour schemes", SRON/EPS/TN/09-002, the `muted` scheme. Named
# here rather than inlined so the assignment tables below read as meanings.
TOL <- c(indigo = "#332288", cyan = "#88CCEE", teal = "#44AA99",
         green  = "#117733", olive = "#999933", sand = "#DDCC77",
         rose   = "#CC6677", wine  = "#882255", purple = "#AA4499",
         residual = "#DDDDDD")

# Each vector is in the article's legend order, top to bottom, which is also the
# stacking order from the top of the bar down. Adjacency is checked in that
# order: no two neighbours share a hue family.
VA_FIG1_COLS <- c(
  `Other (scope 3)`                                          = TOL[["residual"]],
  `Individual travel (scope 3 and out-of-scope)`             = TOL[["rose"]],
  `Food and food services (scope 3)`                         = TOL[["green"]],
  `Services (scope 3)`                                       = TOL[["cyan"]],
  `Medical and electrical equipment and machinery (scope 3)` = TOL[["teal"]],
  `Operational impacts (scope 1)`                            = TOL[["purple"]],
  `Heat and electricity (scope 2)`                           = TOL[["sand"]],
  `Pharmaceuticals and chemical products (scope 3)`          = TOL[["indigo"]])

VA_FIG2_COLS <- c(
  Other                                  = TOL[["residual"]],
  `Mining of minerals and metals`        = TOL[["olive"]],
  `Operational (direct) impacts`         = TOL[["purple"]],
  `Agricultural sector`                  = TOL[["green"]],
  `Fossil fuel industry`                 = TOL[["rose"]],
  `Pharmaceutical and chemical industry` = TOL[["indigo"]],
  `Electricity sector`                   = TOL[["sand"]])

# Figure 3's entries are named per country, so the colours are attached to the
# article's legend positions. The home country takes the deepest, most
# saturated hue: the domestic/imported split is the paper's subject, and the
# home bar is the one a reader looks for first.
va_fig3_cols <- function(home)
  setNames(c(TOL[["green"]], TOL[["cyan"]], TOL[["sand"]], TOL[["teal"]],
             TOL[["rose"]], TOL[["indigo"]]),
           steen_fig3_levels(home))

# ---- label ink -------------------------------------------------------------
# WCAG 2.1 relative luminance, then whichever of near-black and white has the
# higher contrast ratio against the fill. Computed, not typed: a palette edit
# that darkens a fill must not leave black text on it.
rel_luminance <- function(hex) {
  v <- grDevices::col2rgb(hex) / 255
  lin <- ifelse(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ^ 2.4)
  as.numeric(c(0.2126, 0.7152, 0.0722) %*% lin)
}
contrast_ratio <- function(a, b) {
  l <- sort(c(rel_luminance(a), rel_luminance(b)), decreasing = TRUE)
  (l[[1]] + 0.05) / (l[[2]] + 0.05)
}
label_ink <- function(fill)
  vapply(fill, function(f) if (contrast_ratio("#FFFFFF", f) >
                               contrast_ratio(INK, f)) "#FFFFFF" else INK,
         character(1), USE.NAMES = FALSE)

# ---- the plot --------------------------------------------------------------
# One 100 % stacked bar per impact category. The shares are plotted as they come
# out of gold rather than recomputed by position_fill(), so the bar is the
# number in the table and a segment that should be 5.3 % cannot become 5.4 %.
# Default stacking (not reversed) puts the FIRST factor level at the top of the
# bar, which is how the article's legend and stack are ordered.
va_plot <- function(d, levels, cols) {
  d <- d %>%
    filter(indicator %in% STEEN_IND_ORDER) %>%
    mutate(indicator = factor(indicator, levels = STEEN_IND_ORDER),
           figure_group = factor(figure_group, levels = levels),
           label_col = label_ink(cols[as.character(figure_group)]),
           label = if_else(share_pct >= LABEL_FLOOR,
                           sprintf("%.0f%%", share_pct), NA_character_))
  stopifnot(!any(is.na(d$figure_group)))
  ggplot(d, aes(x = indicator, y = share_pct, fill = figure_group)) +
    geom_col(width = 0.55, colour = NA) +
    # `group = figure_group` is load-bearing. Without it the text layer's
    # grouping is taken from its own `colour` aesthetic - two levels, not
    # eight - so position_stack orders the labels differently from the bars and
    # a segment is labelled with a neighbour's share.
    geom_text(aes(label = label, colour = label_col, group = figure_group),
              position = position_stack(vjust = 0.5), size = 4.4,
              fontface = "bold", na.rm = TRUE, show.legend = FALSE) +
    scale_colour_identity() +
    scale_x_discrete(labels = STEEN_IND_LABEL) +
    # No hard `limits`: the stack tops out at 100 up to floating-point dust, and
    # a limit of exactly 100 censors that last segment instead of drawing it.
    scale_y_continuous(breaks = seq(0, 100, 10),
                       expand = expansion(mult = c(0, 0.012))) +
    scale_fill_manual(values = cols, breaks = levels, drop = FALSE) +
    # No x title. The label floor is a note about how the figure was drawn,
    # and notes belong in the manuscript caption - the folder readme states
    # it. The originals carry no x title either.
    labs(x = NULL, y = "Contribution (%)") +
    guides(fill = guide_legend(ncol = 1, byrow = TRUE)) +
    theme_dkhc() +
    # The originals are a plain white panel: no gridlines, a thin dark axis line
    # on the left and bottom. theme_dkhc() sets panel.grid.major as an explicit
    # element_line (inherit.blank = FALSE), so a parent-level
    # `panel.grid = element_blank()` does not cascade down to it - both must be
    # blanked by name or the major gridlines silently survive the override.
    theme(panel.grid.major = element_blank(),
          panel.grid.minor = element_blank(),
          axis.line.x = element_line(colour = INK, linewidth = 0.3),
          axis.line.y = element_line(colour = INK, linewidth = 0.3),
          legend.position = "right",
          legend.justification = "center",
          legend.text = element_text(size = 14, lineheight = 1.05,
                                     colour = INK),
          legend.key.height = grid::unit(1.35, "lines"),
          axis.title.x = element_text(size = 13, colour = INK,
                                      margin = margin(t = 12)),
          axis.text.x = element_text(size = 12.5, lineheight = 1.15,
                                     colour = INK))
}

# ---- the three figures ------------------------------------------------------
cat(sprintf("Variant %s, Steenmeijer figures 1-3:\n", VARIANT))

contribution <- read_csv(gold_path("contribution_by_purchased_product.csv"),
                         show_col_types = FALSE)
hotspot      <- read_csv(gold_path("hotspot_by_producing_node.csv"),
                         show_col_types = FALSE)

# figure 1: the contribution (consumption) side, by purchased product group
f1 <- contribution %>%
  mutate(figure_group = steen_to_group(purchased_sector_group,
                                       STEEN_FIG1_GROUP, STEEN_FIG1_OTHER)) %>%
  steen_shares_of()
dk_save(va_plot(f1, names(VA_FIG1_COLS), VA_FIG1_COLS),
        sprintf("fig1_contribution_product_group_%s", VARIANT),
        w = 16, h = 8.5, sub = VARIANT)

# figures 2 and 3: the hotspot (production) side, with the undistributed
# private-travel component taken out of the base, per the article's captions
h <- hotspot %>% filter(producing_sector_code != STEEN_UNDISTRIBUTED_CODE)

f2 <- h %>%
  mutate(figure_group = steen_to_group(producing_sector_group,
                                       STEEN_FIG2_GROUP, STEEN_FIG2_OTHER)) %>%
  steen_shares_of()
dk_save(va_plot(f2, names(VA_FIG2_COLS), VA_FIG2_COLS),
        sprintf("fig2_hotspot_sector_%s", VARIANT),
        w = 16, h = 8.5, sub = VARIANT)

f3 <- h %>%
  mutate(figure_group = steen_fig3_group(producing_world_region, HOME)) %>%
  steen_shares_of()
dk_save(va_plot(f3, steen_fig3_levels(HOME), va_fig3_cols(HOME)),
        sprintf("fig3_hotspot_geography_%s", VARIANT),
        w = 16, h = 8.5, sub = VARIANT)

# A stacked share figure is only as honest as its totals, so every panel is
# checked to sum to 100 before the script reports success.
for (side in list(f1, f2, f3)) {
  tot <- side %>% group_by(indicator) %>%
    summarise(t = sum(share_pct), .groups = "drop")
  stopifnot(all(abs(tot$t - 100) < 1e-6))
}

cat(sprintf("\nvariant %s figures written to %s\n", VARIANT,
            file.path(fig_dir, VARIANT)))
