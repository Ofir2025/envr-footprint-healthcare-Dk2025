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
IND_UNIT_EXPR <- c(climate_change = "kt~CO[2]*'-eq'", material_extraction = "kt",
                   blue_water_consumption = "Mm^3", land_use = "km^2",
                   waste_generation = "kt")
ind_labeller <- as_labeller(
  setNames(sprintf("atop('%s', (%s))", IND_NAME, IND_UNIT_EXPR), names(IND_NAME)),
  default = label_parsed)

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

# ---------------------------------------------- 1. the footprint, by year -----
p1 <- ggplot(cmp, aes(year, healthcare_footprint,
                      colour = series, group = series)) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 3.1) +
  geom_text(aes(label = val_lab(healthcare_footprint)),
            vjust = -1.15, size = 3.5, show.legend = FALSE,
            fontface = "bold") +
  scale_colour_manual(values = unname(SERIES_COLS), name = NULL) +
  scale_x_continuous(breaks = YEARS, expand = expansion(mult = 0.14)) +
  scale_y_continuous(labels = smart_labs,
                     expand = expansion(mult = c(0.10, 0.20))) +
  facet_wrap(~indicator, ncol = 3, scales = "free_y",
             labeller = ind_labeller) +
  guides(colour = guide_legend(nrow = 1)) +
  labs(x = NULL, y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.x = element_blank())

dk_save(p1, "fig11_footprint_by_year", w = 16, h = 10, sub = "comparison")

# ------------------------------------- 2. the share of the national total -----
p2 <- ggplot(cmp, aes(year, healthcare_share_pct,
                      colour = series, group = series)) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 3.1) +
  geom_text(aes(label = sprintf("%.1f%%", healthcare_share_pct)),
            vjust = -1.15, size = 3.5, show.legend = FALSE, fontface = "bold") +
  scale_colour_manual(values = unname(SERIES_COLS), name = NULL) +
  scale_x_continuous(breaks = YEARS, expand = expansion(mult = 0.14)) +
  scale_y_continuous(labels = function(x) paste0(smart_labs(x), "%"),
                     expand = expansion(mult = c(0.12, 0.22))) +
  facet_wrap(~indicator, ncol = 3, scales = "free_y",
             labeller = ind_labeller) +
  guides(colour = guide_legend(nrow = 1)) +
  labs(x = NULL, y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.x = element_blank())

dk_save(p2, "fig12_share_of_national_by_year", w = 16, h = 10, sub = "comparison")

# --------------------------- 3. what each activity group contributes, by year --
# A grouped bar rather than a stacked one: the question is how each group moved
# between the years, which stacking answers only for the band at the base.
# Ranked by the LATEST year, descending from the top, and every bar labelled.
act <- lapply(YEARS, function(y) {
  f <- file.path("data", "gold", "results", "01_eriksen_replication",
                 paste0(y, "c"), "figure1_activity_contributions.csv")
  if (!file.exists(f)) return(NULL)
  read_csv(f, show_col_types = FALSE) %>%
    filter(indicator == "climate_change") %>%
    transmute(year = y, group = contribution_group, value, share_pct)
}) %>% bind_rows()

if (nrow(act) > 0) {
  ord <- act %>% filter(year == max(YEARS)) %>% arrange(value) %>% pull(group)
  act <- act %>% mutate(group = factor(group, levels = ord),
                        year_f = factor(year, levels = rev(YEARS)))
  p3 <- ggplot(act, aes(value, group, fill = year_f)) +
    geom_col(position = position_dodge(width = 0.78), width = 0.72) +
    geom_text(aes(label = val_lab(value)),
              position = position_dodge(width = 0.78),
              hjust = -0.16, size = 3.2, colour = INK) +
    scale_fill_manual(values = setNames(
      c("#D55E00", "#0072B2", "#009E73")[seq_along(YEARS)], rev(YEARS)),
      name = NULL, breaks = as.character(YEARS)) +
    scale_x_continuous(labels = smart_labs,
                       expand = expansion(mult = c(0, 0.16))) +
    guides(fill = guide_legend(nrow = 1, reverse = TRUE)) +
    labs(x = "Climate footprint (kt CO₂-eq)", y = NULL) +
    theme_dkhc() +
    theme(panel.grid.major.y = element_blank())

  dk_save(p3, "fig13_activity_groups_by_year", w = 16, h = 10, sub = "comparison")
}

cat("year-comparison figures written to", file.path(fig_dir, "comparison"), "\n")
