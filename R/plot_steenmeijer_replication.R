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
#   Palette                     STEENMEIJER_COLS in R/_dk_common.R, read out of
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
# Run:  Rscript R/plot_steenmeijer_replication.R

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.R"))

SUB <- "steenmeijer_replication"

# ---- the five impact categories, in the article's order --------------------
# Axis wording and units are theirs, sub/superscripts included: the axis text
# is a factor level rather than a plotmath expression, so the sub/superscripts
# are carried as Unicode escapes in the string itself, not as plotmath's
# CO[2] / km^2 syntax - expressions would also refuse to wrap onto multiple
# lines, which these labels need. ragg's TIFF device (see dk_save()) renders
# the glyphs cleanly.
IND_ORDER <- c("climate_change", "material_extraction", "blue_water_consumption",
               "land_use", "waste_generation")
IND_LABEL <- c(
  climate_change         = "Climate change\n(kilotonnes of\nCO\u2082 equivalent)",
  material_extraction    = "Material extraction\n(kilotonnes)",
  blue_water_consumption = "Blue water\nconsumption\n(Mm\u00b3)",
  land_use               = "Land use\n(km\u00b2)",
  waste_generation       = "Waste generation\n(kilotonnes)")

# ---- the article's grouping rules ------------------------------------------
# Read off the legends and checked segment by segment against the published
# vector geometry. Anything not listed falls into the figure's "Other".
FIG1_GROUP <- c(
  "Chemical" = "Pharmaceuticals and chemical products (scope 3)",
  "Electricity" = "Heat and electricity (scope 2)",
  "Natural gas and gaseous fuels" = "Heat and electricity (scope 2)",
  "Steam, hot water supply and water distribution" =
    "Heat and electricity (scope 2)",
  "Operational impact" = "Operational impacts (scope 1)",
  "Electrical, electronic and measuring equipment" =
    "Medical and electrical equipment and machinery (scope 3)",
  "Services" = "Services (scope 3)",
  "Food and catering" = "Food and food services (scope 3)",
  "Private travel" = "Individual travel (scope 3 and out-of-scope)")
FIG1_OTHER <- "Other (scope 3)"

FIG2_GROUP <- c(
  "Electricity" = "Electricity sector",
  "Chemical" = "Pharmaceutical and chemical industry",
  "Coal and Petroleum" = "Fossil fuel industry",
  "Natural gas and gaseous fuels" = "Fossil fuel industry",
  "Food and catering" = "Agricultural sector",
  "Minerals and Metals" = "Mining of minerals and metals",
  "Operational impact" = "Operational (direct) impacts")
FIG2_OTHER <- "Other"

# The world regions, keyed by the EXIOBASE aggregate the gold tables carry.
# The home country and "Europe excluding it" are named per country, and keep
# the article's two colours in both.
#
# `home` is always the bare country name ("Netherlands", "Denmark"): that is
# how the article's own legend prints the standalone entry. English needs the
# definite article only inside the "Europe (excluding ...)" phrase - "the
# Netherlands" there, but "Denmark" unchanged - so that phrasing is applied
# locally rather than folded into `home` itself.
with_article <- function(home) if (home == "Netherlands") paste("the", home) else home
fig3_group <- function(region, home) {
  out <- unname(c("Asia and Pacific" = "Asia-Pacific",
                  "Middle East" = "Middle East", "America" = "Americas",
                  "Africa" = "Africa")[region])
  out[region == "Europe"] <- sprintf("Europe (excluding %s)", with_article(home))
  out[region %in% c("Netherlands", "Denmark")] <- home
  if (any(is.na(out)))
    stop(sprintf("no figure-3 region for: %s",
                 paste(unique(region[is.na(out)]), collapse = ", ")))
  out
}
fig3_levels <- function(home)
  c("Africa", "Americas", "Middle East",
    sprintf("Europe (excluding %s)", with_article(home)), "Asia-Pacific", home)
fig3_cols <- function(home)
  setNames(unname(STEENMEIJER_COLS$fig3), fig3_levels(home))

# The part of the private-travel life-cycle result that was never bridged to an
# EXIOBASE node. The captions of figures 2 and 3 say this component was
# distributed proportionally among all groups and all regions, which for a
# 100 % stacked bar is the same as computing the shares without it.
UNDISTRIBUTED_CODE <- "B_REST"

# ---- reading the gold facts ------------------------------------------------
# The Danish results live in a per-variant folder whose name another stream is
# changing (2022 -> 2022_shipping_corrected). gold_path() resolves a bare year
# only, so the Danish reader prefers the shipping-corrected folder, then any
# 2022 folder, and says which file it took.
dk_path <- function(name, year = "2022") {
  hits <- list.files(gold_root, pattern = sprintf("^%s$", name),
                     recursive = TRUE, full.names = TRUE)
  if (length(hits) == 0)
    stop(sprintf("Danish fact '%s' not found under %s/", name, gold_root))
  for (pat in c(sprintf("/%s_shipping_corrected/", year),
                sprintf("/%s/", year), year)) {
    hit <- hits[grepl(pat, hits, fixed = TRUE)]
    if (length(hit) == 1) return(hit[[1]])
    if (length(hit) > 1) hits <- hit
  }
  if (length(hits) == 1) return(hits[[1]])
  stop(sprintf("Danish fact '%s' is ambiguous for %s: %s", name, year,
               paste(hits, collapse = ", ")))
}

# Shares within each impact category, from a table already carrying
# `figure_group`.
shares_of <- function(d) {
  d %>%
    group_by(indicator, figure_group) %>%
    summarise(value = sum(value), .groups = "drop_last") %>%
    mutate(share_pct = 100 * value / sum(value)) %>%
    ungroup()
}

# Map a grouping column onto a figure's legend entries, with everything
# unlisted falling into that figure's own "Other".
to_group <- function(x, map, other) unname(ifelse(x %in% names(map),
                                                  map[x], other))

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
