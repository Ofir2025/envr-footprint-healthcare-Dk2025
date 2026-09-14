#!/usr/bin/env Rscript
# Absolute and per-capita variants of the activity-contribution figure, with the
# share printed on each bar. The share figures answer "what fraction", these
# answer "how much" - a reader comparing Denmark with another health system
# needs the magnitude, and per capita is the only comparable form of it.
#
# Run:  Rscript r/plot_absolute_and_percapita.r

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.r"))

YEAR <- Sys.getenv("HC_ANALYSIS_YEAR", "2022")
POP  <- c(`2019` = 5814422, `2022` = 5873420)[[YEAR]]   # analysis.constants.DK_POPULATION

IND_ORDER <- c("climate_change", "material_extraction", "blue_water_consumption",
               "land_use", "waste_generation")
IND_NAME <- c(climate_change = "Climate change",
              material_extraction = "Material extraction",
              blue_water_consumption = "Blue water consumption",
              land_use = "Land use", waste_generation = "Waste generation")
# Absolute units, and the per-capita unit each becomes. Per-capita units are
# rescaled so no panel reads 0.00: kt/5.9M people is kg per person, not kt.
# Plain text with the sub- and superscripts typed, as in Figure 1's strips: a
# parsed atop() strip set its two lines a full line apart and ignored the bold.
ABS_UNIT <- c(climate_change = "kt CO\u2082e", material_extraction = "kt",
              blue_water_consumption = "Mm\u00b3", land_use = "km\u00b2",
              waste_generation = "kt")
PC_UNIT  <- c(climate_change = "kg CO\u2082e per person",
              material_extraction = "kg per person",
              blue_water_consumption = "m\u00b3 per person",
              land_use = "m\u00b2 per person", waste_generation = "kg per person")
# multiplier from the absolute unit to the per-capita unit, before dividing by
# population: kt -> kg is 1e6; Mm3 -> m3 is 1e6; km2 -> m2 is 1e6.
PC_SCALE <- c(climate_change = 1e6, material_extraction = 1e6,
              blue_water_consumption = 1e6, land_use = 1e6,
              waste_generation = 1e6)

GROUP_COLS <- c(
  "Pharmaceuticals and chemical products" = "#0072B2", "Services" = "#009E73",
  "Transport" = "#E69F00", "Food and food services" = "#56B4E9",
  "Individual travel" = "#CC79A7", "Private travel" = "#CC79A7",
  "Medical, electrical equipment and machinery" = "#D55E00",
  "Operational impacts" = "#8C564B", "Heat and electricity" = "#F0E442",
  "Unallocated" = "grey80")

# "Private travel", the manuscript's term, for the gold tables' "Individual travel"
d <- read_csv(gold_path("figure1_activity_contributions.csv"),
              show_col_types = FALSE) %>%
  mutate(indicator = factor(indicator, levels = IND_ORDER),
         contribution_group = dplyr::recode(contribution_group,
                                            "Individual travel" = "Private travel"))

# Drawn at the size it prints, 6.69 in wide (Appendix A's text width), so the
# sizes below are points on paper. Until 2026-09-14 it was drawn 21 in wide and its
# 12 to 20 pt text printed at 4 to 6 pt. Two panels a row, not three: each panel
# ranks its own groups and so carries its own label column, and three label
# columns left the bars under an inch. Group names wrap at 24 characters, and the
# tick at a panel's right edge is dropped, because it ran towards the next label
# column.
PT_STRIP <- 8; PT_AXIS <- 7; PT_TICK <- 6.5; PT_LABEL <- 6
FIG_W <- 6.69; FIG_H <- 7.2
wrap_key <- function(x) vapply(sub("\\|\\|\\|.*$", "", x),
                               function(s) paste(strwrap(s, 24), collapse = "\n"),
                               character(1), USE.NAMES = FALSE)
inner_breaks <- function(lim) {
  b <- scales::breaks_extended(5)(lim)
  b[b >= lim[1] & b <= lim[1] + 0.8 * diff(lim)]
}

make_plot <- function(per_capita) {
  dd <- d %>%
    mutate(plot_value = if (per_capita)
             value * PC_SCALE[as.character(indicator)] / POP else value,
           key = paste0(contribution_group, "|||", as.integer(indicator)))
  ord <- dd %>% group_by(key) %>% summarise(v = sum(plot_value), .groups = "drop") %>%
    arrange(v)
  dd <- dd %>% mutate(key = factor(key, levels = ord$key))

  unit_expr <- if (per_capita) PC_UNIT else ABS_UNIT

  # The category total carries the magnitude the reader needs to normalise every
  # share in the panel. It goes on the strip rather than inside the panel: an
  # in-panel annotation has to fit between the shortest bar and the axis, which
  # it does not at this label width, and it collided with the bottom row.
  tot <- dd %>% group_by(indicator) %>%
    summarise(v = sum(plot_value), .groups = "drop")
  num <- setNames(ifelse(tot$v >= 100,
                         formatC(round(tot$v), format = "d", big.mark = ","),
                         formatC(tot$v, format = "fg", digits = 3)),
                  as.character(tot$indicator))
  lab <- as_labeller(setNames(
    sprintf("%s\n%s %s", IND_NAME, num[names(IND_NAME)], unit_expr[names(IND_NAME)]),
    names(IND_NAME)))

  ggplot(dd, aes(plot_value, key, fill = contribution_group)) +
    geom_col(width = 0.72, colour = "white", linewidth = 0.1) +
    # Share printed past the bar end. Skipped below 2 % so tiny bars do not
    # collide with the axis, and the ceiling below leaves room for the text.
    geom_text(aes(label = if_else(share_pct >= 2,
                                  sprintf("%.1f%%", share_pct), NA_character_)),
              hjust = -0.15, size = PT_LABEL / .pt, fontface = "bold", colour = "black",
              na.rm = TRUE) +
    facet_ceiling(dd %>% group_by(indicator, key) %>%
                    summarise(value = sum(plot_value), .groups = "drop"),
                  "indicator", "value", room = 1.30) +
    facet_wrap(~indicator, ncol = 2, scales = "free", labeller = lab) +
    scale_y_discrete(labels = wrap_key) +
    scale_fill_manual(values = GROUP_COLS, guide = "none") +
    scale_x_continuous(labels = smart_labs, breaks = inner_breaks,
                       expand = expansion(mult = c(0, 0.02))) +
    labs(x = if (per_capita) "Impact per person" else "Impact", y = NULL) +
    theme_minimal(base_size = PT_AXIS) +
    theme(text = element_text(colour = "black"),
          panel.grid.minor = element_blank(), panel.grid.major.y = element_blank(),
          panel.grid.major.x = element_line(colour = "#E6E6E6", linewidth = 0.25),
          axis.text.y = element_text(size = PT_AXIS, colour = "black", lineheight = 0.88),
          axis.text.x = element_text(size = PT_TICK, colour = "black"),
          axis.title.x = element_text(size = PT_AXIS, colour = "black", margin = margin(t = 4)),
          strip.text = element_text(size = PT_STRIP, face = "bold", colour = "black",
                                    lineheight = 0.95, margin = margin(b = 3)),
          strip.clip = "off",
          panel.spacing.x = grid::unit(12, "pt"),
          panel.spacing.y = grid::unit(8, "pt"),
          plot.margin = margin(2, 4, 2, 2))
}

dk_save(make_plot(FALSE), sprintf("fig1b_activity_absolute_%s", YEAR),
        w = FIG_W, h = FIG_H, dpi = 600)
dk_save(make_plot(TRUE),  sprintf("fig1c_activity_per_capita_%s", YEAR),
        w = FIG_W, h = FIG_H, dpi = 600)

cat("\nabsolute and per-capita figures written to ", fig_dir, "\n", sep = "")
