#!/usr/bin/env Rscript
# The co-author's original three figures, redrawn on the revised 2022 results.
#
#   fig_ofir1_activity_share   what health care BUYS, by activity group
#   fig_ofir2_sector_share     where the impact physically OCCURS, by sector group
#   fig_ofir3_region_share     in which world region it occurs
#
# WHY THESE EXIST BESIDE FIGURE 1
#
# The revised manuscript draws the same three decompositions as the panels of one
# figure (fig1_ofir_panels), in absolute units with shares on the bars. Ofir
# Eriksen asked, on 2026-09-14, to have his own figures back on the new data, so
# the two forms can be compared and either can be used. They are drawn in his
# design, read off the images in his manuscript and supplementary figures file
# of September 2026: one 100 % stacked bar per impact category, his group names
# and legend order, his colour for each group (matplotlib's tab10, assigned as he
# assigned it), the legend on the right, the category names rotated under the
# bars, "Share of footprint" and "Impact category" as axis titles, and no title or
# caption on the image.
#
# WHAT DIFFERS FROM HIS IMAGES, AND WHY
#
#   - "Unallocated" is written as the revised manuscript writes it: "Other" for
#     the residual activity and sector groups, and "Travel supply chains, no
#     region" for the bottom-up rows with no producing region. The quantity is
#     the one his label named.
#   - There is no Netherlands bar. The inherited code reports the Netherlands
#     inside Europe, as Appendix A states.
#   - The category names carry the revised manuscript's names and units
#     ("Climate change (kt CO2-eq)", not "Global warming (ktCO2eq)").
#
# Each figure is written twice: a TIFF, the manuscript format, and a vector PDF,
# the format of his supplementary figures file. The shares are the gold tables'
# own, never recomputed.
#
# Run:  LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 \
#         HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded \
#         DKHC_FIG_DIR=figures/manuscript/2022c Rscript r/plot_ofir_original_figures.r

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.r"))

YEAR <- Sys.getenv("HC_ANALYSIS_YEAR", "2022")

IND_ORDER <- c("climate_change", "material_extraction", "blue_water_consumption",
               "land_use", "waste_generation")
# Plotmath, not Unicode sub- and superscripts: rotated, a Unicode subscript two
# was drawn detached from "CO".
IND_TICK <- c(climate_change = "Climate~change~(kt~CO[2]*'-eq')",
              material_extraction = "Material~extraction~(kt)",
              blue_water_consumption = "Blue~water~consumption~(Mm^3)",
              land_use = "Land~use~(km^2)",
              waste_generation = "Waste~generation~(kt)")

# matplotlib tab10, by name, so the assignments below read as his.
TAB10 <- c(blue = "#1F77B4", orange = "#FF7F0E", green = "#2CA02C", red = "#D62728",
           purple = "#9467BD", brown = "#8C564B", pink = "#E377C2", grey = "#7F7F7F",
           olive = "#BCBD22", cyan = "#17BECF")

# Legend order top to bottom, as in his legends; the stack is drawn in the same
# order from the top of the bar down.
OFIR1 <- c(`Food and food services` = TAB10[["cyan"]],
           `Heat and electricity` = TAB10[["olive"]],
           `Individual travel` = TAB10[["grey"]],
           `Medical, electrical equipment and machinery` = TAB10[["pink"]],
           `Operational impacts` = TAB10[["brown"]],
           `Pharmaceuticals and chemical products` = TAB10[["red"]],
           Services = TAB10[["green"]],
           Transport = TAB10[["orange"]],
           Other = TAB10[["blue"]])
OFIR2 <- c(`Agricultural sector` = TAB10[["cyan"]],
           `Electricity sector` = TAB10[["olive"]],
           `Fossil fuel industry` = TAB10[["grey"]],
           `Mining of minerals and metals` = TAB10[["brown"]],
           `Operational impacts` = TAB10[["purple"]],
           `Pharmaceutical and chemical industry` = TAB10[["green"]],
           Transport = TAB10[["orange"]],
           Other = TAB10[["blue"]])
OFIR3 <- c(Denmark = TAB10[["cyan"]],
           Africa = TAB10[["olive"]],
           America = TAB10[["grey"]],
           `Asia and Pacific` = TAB10[["brown"]],
           Europe = TAB10[["purple"]],
           `Middle East` = TAB10[["green"]],
           `Travel supply chains, no region` = TAB10[["blue"]])

gold <- function(f) read_csv(gold_path(f), show_col_types = FALSE)

ofir_plot <- function(d, cols) {
  d <- d %>%
    filter(indicator %in% IND_ORDER) %>%
    mutate(indicator = factor(indicator, levels = IND_ORDER),
           group = factor(group, levels = names(cols)))
  missing <- setdiff(unique(as.character(d$group)), names(cols))
  if (length(missing) || anyNA(d$group))
    stop(sprintf("groups without a colour: %s", paste(missing, collapse = ", ")))
  ggplot(d, aes(indicator, share_pct, fill = group)) +
    geom_col(width = 0.5, colour = NA) +
    scale_fill_manual(values = cols, breaks = names(cols), drop = FALSE) +
    scale_x_discrete(labels = function(x) parse(text = IND_TICK[x])) +
    scale_y_continuous(breaks = seq(0, 100, 20),
                       expand = expansion(mult = c(0, 0.04))) +
    labs(x = "Impact category", y = "Share of footprint") +
    guides(fill = guide_legend(ncol = 1)) +
    theme_classic(base_size = 13) +
    theme(axis.text = element_text(colour = "black", size = 12.5),
          axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1),
          axis.title = element_text(colour = "black", size = 13.5),
          axis.line = element_blank(),
          panel.border = element_rect(colour = "black", fill = NA, linewidth = 0.6),
          axis.ticks = element_line(colour = "black", linewidth = 0.4),
          legend.position = "right",
          legend.justification = "top",
          legend.title = element_blank(),
          legend.text = element_text(colour = "black", size = 13),
          legend.key.width = grid::unit(1.6, "lines"),
          legend.key.height = grid::unit(1.05, "lines"),
          legend.background = element_rect(colour = "grey80", linewidth = 0.4),
          plot.margin = margin(12, 16, 10, 36))
}

save_both <- function(p, name, w = 11.5, h = 6.8) {
  dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)
  dk_save(p, name, w = w, h = h)
  pdf_name <- file.path(fig_dir, paste0(sub("^fig_", "figS_", name), ".pdf"))
  ggsave(pdf_name, p, width = w, height = h, units = "in", device = cairo_pdf)
  cat(sprintf("  %-52s vector PDF\n", pdf_name))
}

a <- gold("figure1_activity_contributions.csv") %>%
  transmute(indicator, share_pct, group = contribution_group)
s <- gold("figure2_sector_contributions.csv") %>%
  transmute(indicator, share_pct, group = hotspot_group)
r <- gold("figure3_geographical_origin.csv") %>%
  transmute(indicator, share_pct,
            group = dplyr::recode(producing_world_region,
                                  "Unallocated" = "Travel supply chains, no region"))

save_both(ofir_plot(a, OFIR1), sprintf("fig_ofir1_activity_share_%s", YEAR))
save_both(ofir_plot(s, OFIR2), sprintf("fig_ofir2_sector_share_%s", YEAR))
save_both(ofir_plot(r, OFIR3), sprintf("fig_ofir3_region_share_%s", YEAR))
