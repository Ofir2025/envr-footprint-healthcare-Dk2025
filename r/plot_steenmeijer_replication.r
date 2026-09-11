#!/usr/bin/env Rscript
# Steenmeijer et al. (2022) figures 1-3, rendered twice: once from the Dutch
# results as published, once from the Danish 2022 shipping-corrected results,
# in the same groups, the same legend order and the same palette, so the two
# countries can be laid side by side and read as one figure.
#
#   fig 1  contribution analysis: what the sector BUYS
#   fig 2  sector hotspot analysis: where the impact PHYSICALLY OCCURS
#   fig 3  geography hotspot analysis: in which world region it occurs
#
# WHAT IS COPIED FROM THE ARTICLE, AND WHY
#
#   Groups and their order      read off the printed legends (p e954, e955),
#                               not off the archived classification workbook,
#                               because the two disagree in two places and the
#                               printed figure is the thing being replicated.
#                               See docs/methods/replications.md, section 13.
#   Palette                     STEENMEIJER_COLS in r/_dk_common.r, read out of
#                               the article PDF's own drawing operators.
#   Axis title                  "Contribution (%)" on all three, as printed.
#   Category labels             their wording and their units, in their order.
#   Legend on the RIGHT         the article's placement. This is the one house
#                               convention deliberately set aside here: eight
#                               legend entries of up to 56 characters do not
#                               read at the foot of a 100 % bar chart, and the
#                               right-hand legend runs top-to-bottom in the
#                               same order as the stack, which is how the
#                               original is meant to be read.
#   No title, no caption        the house rule that is NOT set aside. The
#                               captions live in the gold folder's readme.
#
# Run:  Rscript r/plot_steenmeijer_replication.r

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.r"))

SUB <- "steenmeijer_replication"

# ---- the article's groups, order and wording -------------------------------
# Held in r/_dk_common.r (STEEN_*), not here, because r/plot_steenmeijer_variant_a.r
# draws the same three figures for variant a and the two must not be allowed to
# drift apart: a replication whose group order is a second copy of the legend is
# no longer a replication once someone edits one copy. Only the palette and the
# per-figure decoration differ between the two scripts.
IND_ORDER <- STEEN_IND_ORDER
IND_LABEL <- STEEN_IND_LABEL
FIG1_GROUP <- STEEN_FIG1_GROUP; FIG1_OTHER <- STEEN_FIG1_OTHER
FIG2_GROUP <- STEEN_FIG2_GROUP; FIG2_OTHER <- STEEN_FIG2_OTHER
fig3_group  <- steen_fig3_group
fig3_levels <- steen_fig3_levels
fig3_cols   <- function(home)
  setNames(unname(STEENMEIJER_COLS$fig3), fig3_levels(home))
UNDISTRIBUTED_CODE <- STEEN_UNDISTRIBUTED_CODE
shares_of <- steen_shares_of
to_group  <- steen_to_group

# ---- reading the gold facts ------------------------------------------------
# The Danish results live in a per-variant folder. This comparison wants the
# headline configuration for the year, which is variant c (v3.8.2, shipping
# correction applied, health-care boundary, capital excluded), so the reader
# prefers `variant_name()` for that variant, then the uncorrected companion,
# then any folder carrying the year, and says which file it took.
dk_path <- function(name, year = "2022") {
  hits <- list.files(gold_root, pattern = sprintf("^%s$", name),
                     recursive = TRUE, full.names = TRUE)
  if (length(hits) == 0)
    stop(sprintf("Danish fact '%s' not found under %s/", name, gold_root))
  headline <- variant_name(year, tag = "_snacship", release = "v3_8_2",
                           scope = "health_eldercare", capital = "excluded")
  for (pat in c(sprintf("/%s/", headline),
                sprintf("/%s_uncorrected/", year),
                sprintf("/%s/", year), year)) {
    hit <- hits[grepl(pat, hits, fixed = TRUE)]
    if (length(hit) == 1) return(hit[[1]])
    if (length(hit) > 1) hits <- hit
  }
  if (length(hits) == 1) return(hits[[1]])
  stop(sprintf("Danish fact '%s' is ambiguous for %s: %s", name, year,
               paste(hits, collapse = ", ")))
}

# ---- the plot ---------------------------------------------------------------
# One 100 % stacked bar per impact category. The shares are plotted as they
# come out of gold rather than recomputed by position_fill(), so the bar is the
# number in the table and a segment that should be 5.3 % cannot become 5.4 %.
steen_plot <- function(d, levels, cols) {
  d <- d %>%
    filter(indicator %in% IND_ORDER) %>%
    mutate(indicator = factor(indicator, levels = IND_ORDER),
           figure_group = factor(figure_group, levels = levels))
  stopifnot(!any(is.na(d$figure_group)))
  ggplot(d, aes(x = indicator, y = share_pct, fill = figure_group)) +
    geom_col(width = 0.55, colour = NA) +
    scale_x_discrete(labels = IND_LABEL) +
    # No hard `limits`: the stack tops out at 100 up to floating-point dust,
    # and a limit of exactly 100 censors that last segment instead of drawing
    # it. The ticks fix the axis at 0-100 without discarding a bar.
    scale_y_continuous(breaks = seq(0, 100, 10),
                       expand = expansion(mult = c(0, 0.012))) +
    scale_fill_manual(values = cols, breaks = levels, drop = FALSE) +
    labs(x = NULL, y = "Contribution (%)") +
    guides(fill = guide_legend(ncol = 1, byrow = TRUE)) +
    theme_dkhc() +
    # The originals are a plain white panel: no gridlines, a thin dark axis
    # line on the left and bottom. theme_dkhc()'s light-grey major gridlines
    # are a house default for other figures, not a feature of these replicas,
    # so both axes' grids are dropped here and an axis line drawn in instead.
    # NOTE: theme_dkhc() sets panel.grid.major as an explicit element_line
    # (inherit.blank = FALSE), so a parent-level `panel.grid = element_blank()`
    # does not cascade down to it - panel.grid.major/.minor must be blanked
    # by name, or the major gridlines silently survive the override.
    theme(panel.grid.major = element_blank(),
          panel.grid.minor = element_blank(),
          axis.line.x = element_line(colour = INK, linewidth = 0.3),
          axis.line.y = element_line(colour = INK, linewidth = 0.3),
          legend.position = "right",
          legend.justification = "center",
          legend.text = element_text(size = 14, lineheight = 1.05,
                                     colour = INK),
          legend.key.height = grid::unit(1.35, "lines"),
          axis.text.x = element_text(size = 12.5, lineheight = 1.15,
                                     colour = INK))
}

# ---- the six figures --------------------------------------------------------
render <- function(country, home, contribution, hotspot) {
  # figure 1: the contribution (consumption) side, by purchased sector group
  f1 <- contribution %>%
    mutate(figure_group = to_group(purchased_sector_group, FIG1_GROUP,
                                   FIG1_OTHER)) %>%
    shares_of()
  dk_save(steen_plot(f1, names(STEENMEIJER_COLS$fig1), STEENMEIJER_COLS$fig1),
          sprintf("steenmeijer_fig1_contribution_%s", country),
          w = 16, h = 8.5, sub = SUB)

  # figures 2 and 3: the hotspot (production) side, with the undistributed
  # private-travel component taken out of the base, per their captions
  h <- hotspot %>% filter(producing_sector_code != UNDISTRIBUTED_CODE)

  f2 <- h %>%
    mutate(figure_group = to_group(producing_sector_group, FIG2_GROUP,
                                   FIG2_OTHER)) %>%
    shares_of()
  dk_save(steen_plot(f2, names(STEENMEIJER_COLS$fig2), STEENMEIJER_COLS$fig2),
          sprintf("steenmeijer_fig2_hotspot_sector_%s", country),
          w = 16, h = 8.5, sub = SUB)

  f3 <- h %>%
    mutate(figure_group = fig3_group(producing_world_region, home)) %>%
    shares_of()
  dk_save(steen_plot(f3, fig3_levels(home), fig3_cols(home)),
          sprintf("steenmeijer_fig3_hotspot_region_%s", country),
          w = 16, h = 8.5, sub = SUB)

  invisible(list(fig1 = f1, fig2 = f2, fig3 = f3))
}

cat("Netherlands, from the archived RIVM outputs:\n")
nl <- render(
  "nl", "Netherlands",
  read_csv(gold_path("nl_contribution_by_purchased_node.csv"),
           show_col_types = FALSE),
  read_csv(gold_path("nl_hotspot_by_producing_node.csv"),
           show_col_types = FALSE))

cat("Denmark, 2022, shipping-corrected:\n")
dk_contribution <- read_csv(dk_path("contribution_by_purchased_product.csv"),
                            show_col_types = FALSE)
dk_hotspot <- read_csv(dk_path("hotspot_by_producing_node.csv"),
                       show_col_types = FALSE)
dk <- render("dk", "Denmark", dk_contribution, dk_hotspot)

# A stacked share figure is only as honest as its totals, so every panel is
# checked to sum to 100 before the script reports success.
for (nm in names(nl)) {
  for (side in list(nl[[nm]], dk[[nm]])) {
    tot <- side %>% group_by(indicator) %>%
      summarise(t = sum(share_pct), .groups = "drop")
    stopifnot(all(abs(tot$t - 100) < 1e-6))
  }
}

cat("\nSteenmeijer replication figures written to ",
    file.path(fig_dir, SUB), "\n", sep = "")
