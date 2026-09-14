# -*- coding: utf-8 -*-
# Time series across the model years, one figure per question.
#
# Why lines and points, and not an area plot. The study has three reference
# years - 2016, 2019, 2022 - and an area plot answers a question nobody asked of
# three points: it draws the region under a curve whose shape between the points
# is an artefact of the interpolation, and stacking those areas makes the
# composition legible only for the bottom band. With three observations the
# honest encodings are position and length. Cleveland's ordering of elementary
# perceptual tasks puts position along a common scale first; area is seventh.
#
# So: a connected dot plot per indicator. The dots are the observations, the
# line says only that they are the same series in time order, and every dot
# carries its value, because with three points there is no crowding argument for
# leaving them off.
#
# The variant series drawn are c and d, the two that exist in all three years on
# one release with the shipping correction applied. a and b are v3.7 and exist
# for 2019 alone, so they are not a series and are not drawn here.

suppressPackageStartupMessages({
  library(dplyr); library(ggplot2); library(readr); library(tidyr)
})
source(file.path("r", "_dk_common.r"))

IND_ORDER <- c("climate_change", "material_extraction", "blue_water_consumption",
               "land_use", "waste_generation")
IND_NAME <- c(climate_change = "Climate change",
              material_extraction = "Material extraction",
              blue_water_consumption = "Blue water consumption",
              land_use = "Land use", waste_generation = "Waste generation")
# Plain text with the sub- and superscripts typed, as in Figure 1's strips: a
# parsed atop() strip set its two lines a full line apart and ignored the bold.
IND_UNIT_TXT <- c(climate_change = "kt CO\u2082e", material_extraction = "kt",
                  blue_water_consumption = "Mm\u00b3", land_use = "km\u00b2",
                  waste_generation = "kt")
ind_labeller <- as_labeller(
  setNames(sprintf("%s\n(%s)", IND_NAME, IND_UNIT_TXT), names(IND_NAME)))

# Drawn at the size they print, 6.69 in wide (Appendix A's text width), so the
# sizes below are points on paper. Until 2026-09-14 these were drawn 16 in wide and
# their 9 to 20 pt text printed at 4 to 8 pt.
FIG_W <- 6.69
PT_STRIP <- 8; PT_LEGEND <- 7.5; PT_AXIS <- 7; PT_TICK <- 6.5; PT_LABEL <- 6
theme_print <- function() {
  theme_minimal(base_size = PT_AXIS) +
    theme(text = element_text(colour = "black"),
          panel.grid.minor = element_blank(),
          panel.grid.major = element_line(colour = "#E6E6E6", linewidth = 0.25),
          axis.text = element_text(size = PT_TICK, colour = "black"),
          axis.title.x = element_text(size = PT_AXIS, colour = "black", margin = margin(t = 4)),
          strip.text = element_text(size = PT_STRIP, face = "bold", colour = "black",
                                    lineheight = 0.95, margin = margin(b = 3)),
          strip.clip = "off",
          legend.position = "bottom", legend.title = element_blank(),
          legend.text = element_text(size = PT_LEGEND, colour = "black",
                                     margin = margin(l = 2, r = 8)),
          legend.key.size = grid::unit(9, "pt"),
          legend.margin = margin(t = 0), legend.box.spacing = grid::unit(4, "pt"),
          panel.spacing.x = grid::unit(10, "pt"),
          panel.spacing.y = grid::unit(8, "pt"),
          plot.margin = margin(2, 4, 2, 2))
}

# The two variants that form a series, and what each one is.
SERIES <- c(c = "Health-care boundary, capital excluded",
            d = "Plus child and elder care, capital endogenised")
SERIES_COLS <- c(c = "#0072B2", d = "#D55E00")

cmp <- read_csv(file.path("data", "gold", "results", "01_eriksen_replication",
                          "variant_comparison.csv"), show_col_types = FALSE) %>%
  mutate(letter = sub("^[0-9]{4}", "", variant)) %>%
  filter(letter %in% names(SERIES)) %>%
  mutate(year = as.integer(analysis_year),
         indicator = factor(indicator, levels = IND_ORDER),
         series = factor(SERIES[letter], levels = unname(SERIES)))

stopifnot(nrow(cmp) > 0)
YEARS <- sort(unique(cmp$year))

# A value label that stays readable across five indicators whose magnitudes run
# from 95 to 5,700: thousands separated, no decimals above 100, one below.
val_lab <- function(v) ifelse(
  v >= 100, formatC(v, format = "f", digits = 0, big.mark = ","),
  formatC(v, format = "f", digits = 1))

# Each value sits on the side of its dot that the line leaves free, because at
# print size a line climbing out of a dot ran through the label centred above it:
# above a dot whose neighbours are all lower, below one whose neighbours are all
# higher, above and to the left where the line rises through the dot, above and
# to the right where it falls through. The box is opaque white and drawn under
# the dots.
value_label <- function(col, fmt) {
  lab <- cmp %>%
    arrange(indicator, series, year) %>%
    group_by(indicator, series) %>%
    mutate(v = .data[[col]], d_in = v - lag(v), d_out = lead(v) - v,
           below = coalesce(d_in < 0, TRUE) & coalesce(d_out > 0, TRUE),
           hj = case_when(!is.na(d_in) & !is.na(d_out) & d_in > 0 & d_out > 0 ~ 0.9,
                          !is.na(d_in) & !is.na(d_out) & d_in < 0 & d_out < 0 ~ 0.1,
                          TRUE ~ 0.5),
           vj = if_else(below, 1.3, -0.3)) %>%
    ungroup()
  geom_label(data = lab, aes(label = fmt(v), hjust = hj, vjust = vj),
             size = PT_LABEL / .pt, fontface = "bold",
             fill = "white", border.colour = NA, label.r = grid::unit(0, "pt"),
             label.padding = grid::unit(0.8, "pt"), show.legend = FALSE)
}

# ---------------------------------------------- 1. the footprint, by year -----
p1 <- ggplot(cmp, aes(year, healthcare_footprint,
                      colour = series, group = series)) +
  geom_line(linewidth = 0.5) +
  value_label("healthcare_footprint", val_lab) +
  geom_point(size = 1.3) +
  scale_colour_manual(values = unname(SERIES_COLS), name = NULL) +
  scale_x_continuous(breaks = YEARS, expand = expansion(mult = 0.14)) +
  scale_y_continuous(labels = smart_labs,
                     expand = expansion(mult = c(0.18, 0.20))) +
  facet_wrap(~indicator, ncol = 3, scales = "free_y",
             labeller = ind_labeller) +
  guides(colour = guide_legend(nrow = 1)) +
  labs(x = NULL, y = NULL) +
  theme_print() +
  theme(panel.grid.major.x = element_blank())

dk_save(p1, "fig11_footprint_by_year", w = FIG_W, h = 4.6, dpi = 600, sub = "comparison")

# ------------------------------------- 2. the share of the national total -----
p2 <- ggplot(cmp, aes(year, healthcare_share_pct,
                      colour = series, group = series)) +
  geom_line(linewidth = 0.5) +
  value_label("healthcare_share_pct", function(v) sprintf("%.1f%%", v)) +
  geom_point(size = 1.3) +
  scale_colour_manual(values = unname(SERIES_COLS), name = NULL) +
  scale_x_continuous(breaks = YEARS, expand = expansion(mult = 0.14)) +
  scale_y_continuous(labels = function(x) paste0(smart_labs(x), "%"),
                     expand = expansion(mult = c(0.18, 0.22))) +
  facet_wrap(~indicator, ncol = 3, scales = "free_y",
             labeller = ind_labeller) +
  guides(colour = guide_legend(nrow = 1)) +
  labs(x = NULL, y = NULL) +
  theme_print() +
  theme(panel.grid.major.x = element_blank())

dk_save(p2, "fig12_share_of_national_by_year", w = FIG_W, h = 4.6, dpi = 600, sub = "comparison")

# --------------------------- 3. what each activity group contributes, by year --
# A grouped bar rather than a stacked one: the question is how each group moved
# between the years, which stacking answers only for the band at the base.
# Ranked by the LATEST year, descending from the top, and every bar labelled.
# "Private travel", the manuscript's term, for the gold tables' "Individual
# travel" (relabelled at display time, as in plot_absolute_and_percapita.r).
act <- lapply(YEARS, function(y) {
  f <- file.path("data", "gold", "results", "01_eriksen_replication",
                 paste0(y, "c"), "figure1_activity_contributions.csv")
  if (!file.exists(f)) return(NULL)
  read_csv(f, show_col_types = FALSE) %>%
    filter(indicator == "climate_change") %>%
    transmute(year = y, value, share_pct,
              group = dplyr::recode(contribution_group,
                                    "Individual travel" = "Private travel"))
}) %>% bind_rows()

if (nrow(act) > 0) {
  ord <- act %>% filter(year == max(YEARS)) %>% arrange(value) %>% pull(group)
  act <- act %>% mutate(group = factor(group, levels = ord),
                        year_f = factor(year, levels = rev(YEARS)))
  p3 <- ggplot(act, aes(value, group, fill = year_f)) +
    geom_col(position = position_dodge(width = 0.78), width = 0.72) +
    geom_text(aes(label = val_lab(value)),
              position = position_dodge(width = 0.78),
              hjust = -0.16, size = PT_LABEL / .pt, colour = "black") +
    scale_fill_manual(values = setNames(
      c("#D55E00", "#0072B2", "#009E73")[seq_along(YEARS)], rev(YEARS)),
      name = NULL, breaks = as.character(YEARS)) +
    scale_x_continuous(labels = smart_labs,
                       expand = expansion(mult = c(0, 0.16))) +
    # group names longer than 24 characters take a second line
    scale_y_discrete(labels = function(x) vapply(x, function(s)
      paste(strwrap(s, 24), collapse = "\n"), character(1))) +
    # keys run 2016, 2019, 2022, the order the bars run top to bottom in each group
    guides(fill = guide_legend(nrow = 1)) +
    labs(x = "Climate footprint (kt CO₂e)", y = NULL) +
    theme_print() +
    theme(panel.grid.major.y = element_blank(),
          axis.text.y = element_text(size = PT_AXIS, colour = "black", lineheight = 0.9))

  dk_save(p3, "fig13_activity_groups_by_year", w = FIG_W, h = 4.6, dpi = 600, sub = "comparison")
}

cat("year-comparison figures written to", file.path(fig_dir, "comparison"), "\n")
