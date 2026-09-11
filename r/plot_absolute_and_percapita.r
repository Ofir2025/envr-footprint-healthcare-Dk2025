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
ABS_UNIT <- c(climate_change = "kt~CO[2]*'-eq'", material_extraction = "kt",
              blue_water_consumption = "Mm^3", land_use = "km^2",
              waste_generation = "kt")
PC_UNIT  <- c(climate_change = "kg~CO[2]*'-eq'~per~person",
              material_extraction = "kg~per~person",
              blue_water_consumption = "m^3~per~person",
              land_use = "m^2~per~person", waste_generation = "kg~per~person")
# multiplier from the absolute unit to the per-capita unit, before dividing by
# population: kt -> kg is 1e6; Mm3 -> m3 is 1e6; km2 -> m2 is 1e6.
PC_SCALE <- c(climate_change = 1e6, material_extraction = 1e6,
              blue_water_consumption = 1e6, land_use = 1e6,
              waste_generation = 1e6)

GROUP_COLS <- c(
  "Pharmaceuticals and chemical products" = "#0072B2", "Services" = "#009E73",
  "Transport" = "#E69F00", "Food and food services" = "#56B4E9",
  "Individual travel" = "#CC79A7",
  "Medical, electrical equipment and machinery" = "#D55E00",
  "Operational impacts" = "#8C564B", "Heat and electricity" = "#F0E442",
  "Unallocated" = "grey80")

d <- read_csv(gold_path("figure1_activity_contributions.csv"),
              show_col_types = FALSE) %>%
  mutate(indicator = factor(indicator, levels = IND_ORDER))

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
    sprintf("atop('%s', '%s'~%s)", IND_NAME, num[names(IND_NAME)], unit_expr),
    names(IND_NAME)), default = label_parsed)

  ggplot(dd, aes(plot_value, key, fill = contribution_group)) +
    geom_col(width = 0.72, colour = "white", linewidth = 0.15) +
    # Share printed past the bar end. Skipped below 2 % so tiny bars do not
    # collide with the axis, and the ceiling below leaves room for the text.
    geom_text(aes(label = if_else(share_pct >= 2,
                                  sprintf("%.1f%%", share_pct), NA_character_)),
              hjust = -0.15, size = 4.1, fontface = "bold", colour = "#2C3E50",
              na.rm = TRUE) +
    facet_ceiling(dd %>% group_by(indicator, key) %>%
                    summarise(value = sum(plot_value), .groups = "drop"),
                  "indicator", "value", room = 1.30) +
    facet_wrap(~indicator, ncol = 3, scales = "free", labeller = lab) +
    scale_y_discrete(labels = function(x) sub("\\|\\|\\|.*$", "", x)) +
    scale_fill_manual(values = GROUP_COLS, guide = "none") +
    scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                       guide = guide_axis(check.overlap = TRUE),
                       expand = expansion(mult = c(0, 0.02))) +
    labs(x = if (per_capita) "Impact per person" else "Impact", y = NULL) +
    theme_dkhc() +
    theme(panel.grid.major.y = element_blank(),
          axis.text.y = element_text(size = 13.5, colour = INK),
          plot.margin = margin(14, 30, 12, 14))
}

dk_save(make_plot(FALSE), sprintf("fig1b_activity_absolute_%s", YEAR),
        w = 21, h = 12)
dk_save(make_plot(TRUE),  sprintf("fig1c_activity_per_capita_%s", YEAR),
        w = 21, h = 12)

cat("\nabsolute and per-capita figures written to ", fig_dir, "\n", sep = "")
