#!/usr/bin/env Rscript
# Where the Danish health care footprint arises: country or region of production
# by producing sector group, for all five impact categories on one sheet.
#
#   columns  the 49 EXIOBASE countries and rest-of-world regions, and nothing else,
#            grouped by world region, countries ranked within their group; the
#            groups run Denmark, Europe, Africa, Asia and Pacific, Middle East,
#            America, an order chosen so that the two- and three-column groups
#            each sit beside a wide one: ranked by share, "Middle East" and
#            "Africa" fell side by side and their names read as "East Africa"
#   rows     the ten producing sector groups with the largest share of any one
#            category, and the other eleven pooled into "Other sector groups"; the
#            rows are ranked by their mean share, the pooled row included
#   panels   one per impact category, stacked, sharing the columns and the rows;
#            each panel title carries the category's total footprint, which is
#            what 100 % means in that panel
#   fill     the cell's share of its category's total footprint, in eight bins on
#            ColorBrewer YlOrRd, so a 0.01 % cell and a 45 % cell sit on one key;
#            a cell with no footprint is white and has its own key
#
# The travel supply chains are not drawn. The per-kilometre travel inventory
# splits each trip into the vehicle's direct emissions, which occur in Denmark
# and are drawn in the Denmark column, and the indirect part (fuel supply and
# vehicle manufacture), which it quantifies without any country. Placing that
# part in a pseudo-region would break the rule that every column is a place, so
# it is left out, as Steenmeijer et al. (2022) leave it out of their geography
# figure. The shares keep the whole footprint as their base, so every cell and
# every row or column total agrees with figure 1; each panel therefore sums to
# 100 % less the undrawn part, which the script prints for the caption.
#
# Drawn at the size it is printed. Appendix A prints figures across its full
# text width, 6.69 in (A4 with 2 cm side margins), so the canvas IS that width
# and every size below is the point size on paper. Until 2026-09-14 this sheet
# was drawn 22 in wide with 10.5 to 13 pt labels, which Word shrank to 3 to 4 pt.
# 49 columns in 6.69 in leave about 7 pt per column, which is the ceiling on the
# country codes; the row count is what buys the row labels their size.
#
# Source: 01_eriksen_replication/<variant>/hotspot_by_producing_country_and_sector_group.csv,
# whose five category totals are the study's headline footprints.
#
# Run:  LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 \
#         HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded \
#         DKHC_FIG_DIR=figures/manuscript/2022c Rscript r/plot_origin_sector_heatmap.r

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.r"))
suppressPackageStartupMessages({library(patchwork); library(ggh4x)})

YEAR <- Sys.getenv("HC_ANALYSIS_YEAR", "2022")

# ---- print geometry: points on paper -------------------------------------------
PRINT_W <- 6.69          # Appendix A text width, in
PRINT_H <- as.numeric(Sys.getenv("HEATMAP_H", "8.6"))  # room for a caption on the page
PT_TITLE  <- 9           # panel titles, the largest text on the sheet
PT_STRIP  <- 7.5         # world-region groups
PT_LEGEND <- 7.5         # legend keys and the axis title
PT_ROW    <- 7.5         # sector groups
PT_COL    <- 6.5         # country codes: 49 columns cap them near 7 pt
PT_CELL   <- 5.5         # the few shares printed inside cells

IND_ORDER <- c("climate_change", "material_extraction", "blue_water_consumption",
               "land_use", "waste_generation")
N_SECTORS <- as.integer(Sys.getenv("HEATMAP_ROWS", "10"))
OTHER_SECTORS <- "Other sector groups"

# Short, sentence-case names for the scope layer's groups; the published table
# keeps its own. The travel row holds only the direct part, and says so.
SECTOR_LABEL <- c(
  "Food and catering" = "Food and catering",
  "Minerals and Metals" = "Minerals and metals",
  "Chemical" = "Chemical industry",
  "Operational impact" = "Operational impacts",
  "Transport" = "Transport",
  "Waste management and disposal" = "Waste management",
  "Coal and Petroleum" = "Coal and petroleum",
  "Private travel" = "Private travel (direct)",
  "Electricity" = "Electricity",
  "Services" = "Services",
  "Steam, hot water supply and water distribution" = "Steam, hot water and water supply",
  "Paper Products" = "Paper products",
  "Metal Products" = "Metal products",
  "General and special Machinery" = "General and special machinery",
  "Transport Equipment" = "Transport equipment")

BIN_BREAKS <- c(0, 0.01, 0.1, 0.5, 1, 5, 10, 25, Inf)
BIN_LABELS <- c("up to 0.01", "0.01 to 0.1", "0.1 to 0.5", "0.5 to 1",
                "1 to 5", "5 to 10", "10 to 25", "25 or more")
ZERO_LABEL <- "0"
# White for no footprint, then ColorBrewer YlOrRd, eight classes from its nine
# (the palest step is left out so the lowest bin still separates from white).
BIN_COLS <- setNames(c("#FFFFFF", "#FFEDA0", "#FED976", "#FEB24C", "#FD8D3C",
                       "#FC4E2A", "#E31A1C", "#BD0026", "#800026"),
                     c(ZERO_LABEL, BIN_LABELS))

rel_luminance <- function(hex) {
  v <- grDevices::col2rgb(hex) / 255
  lin <- ifelse(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ^ 2.4)
  as.numeric(c(0.2126, 0.7152, 0.0722) %*% lin)
}
ink_for <- function(fill) ifelse(vapply(fill, rel_luminance, numeric(1)) < 0.3,
                                 "#FFFFFF", "#000000")

raw <- read_csv(gold_path("hotspot_by_producing_country_and_sector_group.csv"),
                show_col_types = FALSE) %>%
  filter(indicator %in% IND_ORDER)
totals <- raw %>% group_by(indicator) %>% summarise(total = sum(value), .groups = "drop")

# the undrawn travel supply chains, as a share of each category, for the caption
undrawn <- raw %>% filter(producing_country_iso3 == "GLO") %>%
  group_by(indicator) %>% summarise(v = sum(value), .groups = "drop") %>%
  right_join(totals, by = "indicator") %>%
  mutate(pct = 100 * coalesce(v, 0) / total)
cat("  travel supply chains with no country, not drawn (% of category):\n")
for (i in IND_ORDER) cat(sprintf("    %-24s %6.2f\n", i, undrawn$pct[undrawn$indicator == i]))

d <- raw %>%
  filter(producing_country_iso3 != "GLO") %>%
  mutate(region = producing_world_region,
         column = region_code(producing_country_iso3),
         sector = producing_sector_group) %>%
  left_join(totals, by = "indicator") %>%
  group_by(indicator, region, column, sector) %>%
  summarise(share_pct = 100 * sum(value / total), .groups = "drop")
stopifnot(n_distinct(d$column) == 49, !anyNA(d$region))

# the rows: the largest share of any one category decides which groups are named
keep <- d %>% group_by(indicator, sector) %>%
  summarise(s = sum(share_pct), .groups = "drop") %>%
  group_by(sector) %>% summarise(v = max(s), .groups = "drop") %>%
  arrange(desc(v)) %>% head(N_SECTORS) %>% pull(sector)
unlabelled <- setdiff(keep, names(SECTOR_LABEL))
if (length(unlabelled)) stop("no short label for: ", paste(unlabelled, collapse = ", "))
d <- d %>%
  mutate(sector = if_else(sector %in% keep, unname(SECTOR_LABEL[sector]), OTHER_SECTORS)) %>%
  group_by(indicator, region, column, sector) %>%
  summarise(share_pct = sum(share_pct), .groups = "drop")

drawn <- d %>% group_by(indicator) %>% summarise(t = sum(share_pct), .groups = "drop") %>%
  left_join(undrawn, by = "indicator")
stopifnot(all(abs(drawn$t + drawn$pct - 100) < 1e-6))

region_order <- c("Denmark", "Europe", "Africa", "Asia and Pacific", "Middle East",
                  "America")
stopifnot(setequal(region_order, unique(d$region)))
col_order <- d %>% group_by(region, column) %>%
  summarise(v = sum(share_pct), .groups = "drop") %>%
  mutate(region = factor(region, levels = region_order)) %>%
  arrange(region, desc(v)) %>% pull(column)
row_order <- d %>% group_by(indicator, sector) %>%
  summarise(v = sum(share_pct), .groups = "drop") %>%
  group_by(sector) %>% summarise(v = mean(v), .groups = "drop") %>%
  arrange(v) %>% pull(sector)

# every country-sector-category combination, so an empty cell is drawn white
grid <- tidyr::expand_grid(indicator = IND_ORDER,
                           distinct(d, region, column),
                           sector = unique(d$sector)) %>%
  left_join(d, by = c("indicator", "region", "column", "sector")) %>%
  mutate(share_pct = coalesce(share_pct, 0),
         region = factor(region, levels = region_order),
         column = factor(column, levels = col_order),
         sector = factor(sector, levels = row_order),
         bin = if_else(share_pct > 0,
                       as.character(cut(share_pct, BIN_BREAKS, labels = BIN_LABELS,
                                        right = TRUE, include.lowest = FALSE)),
                       ZERO_LABEL),
         bin = factor(bin, levels = c(ZERO_LABEL, BIN_LABELS)),
         label = if_else(share_pct >= 10, sprintf("%.0f", share_pct), NA_character_),
         ink = ink_for(BIN_COLS[as.character(bin)]))

# Two-line names where a group is narrower than its name.
REGION_STRIP <- c(Denmark = "Denmark", Europe = "Europe",
                  `Asia and Pacific` = "Asia and\nPacific", America = "America",
                  Africa = "Africa", `Middle East` = "Middle\nEast")

fmt_total <- function(x) if (x >= 100) formatC(round(x), format = "d", big.mark = ",") else
  formatC(x, format = "f", digits = 1)
panel_title <- function(ind) {
  t <- fmt_total(totals$total[totals$indicator == ind])
  switch(ind,
    climate_change         = bquote(bold("Climate change, " * .(t) * " kt CO"[2] * "e")),
    material_extraction    = bquote(bold("Material extraction, " * .(t) * " kt")),
    blue_water_consumption = bquote(bold("Blue water consumption, " * .(t) * " Mm"^3)),
    land_use               = bquote(bold("Land use, " * .(t) * " km"^2)),
    waste_generation       = bquote(bold("Waste generation, " * .(t) * " kt")))
}

panel <- function(ind, first, last) {
  ggplot(filter(grid, indicator == ind), aes(column, sector)) +
    # show.legend = TRUE keeps a coloured key for a bin this panel does not use;
    # without it the collected legend drew "10 to 25" and "25 or more" empty
    geom_tile(aes(fill = bin), colour = "grey80", linewidth = 0.15, show.legend = TRUE) +
    geom_text(aes(label = label, colour = ink), size = PT_CELL / .pt,
              fontface = "bold", na.rm = TRUE) +
    scale_colour_identity() +
    scale_fill_manual(values = BIN_COLS, breaks = c(ZERO_LABEL, BIN_LABELS),
                      drop = FALSE, name = "Share of the category's total footprint (%)") +
    # a rule under each group's name spans exactly its columns, so a name wider
    # than its group still reads as belonging to it
    facet_grid(. ~ region, scales = "free_x", space = "free_x",
               labeller = labeller(region = as_labeller(REGION_STRIP))) +
    scale_x_discrete(expand = c(0, 0)) +
    scale_y_discrete(expand = c(0, 0)) +
    labs(title = panel_title(ind), y = NULL,
         x = if (last) "Country or region of production" else NULL) +
    guides(fill = guide_legend(nrow = 1, title.position = "top",
                               override.aes = list(colour = "grey60"))) +
    theme_minimal(base_size = PT_ROW) +
    theme(text = element_text(colour = "black"),
          plot.title = element_text(size = PT_TITLE, hjust = 0,
                                    margin = margin(t = if (first) 0 else 5, b = 3)),
          plot.title.position = "plot",
          panel.grid = element_blank(),
          panel.spacing.x = grid::unit(5, "pt"),
          strip.text.x = if (first) element_text(size = PT_STRIP, face = "bold",
                                                 lineheight = 0.9, vjust = 0,
                                                 margin = margin(b = 2.5))
                         else element_blank(),
          strip.background.x = if (first) element_part_rect(side = "b", colour = "black",
                                                            fill = NA, linewidth = 0.4)
                               else element_blank(),
          strip.clip = "off",
          axis.text.y = element_text(size = PT_ROW, colour = "black",
                                     margin = margin(r = 2)),
          axis.text.x = if (last) element_text(size = PT_COL, colour = "black", angle = 90,
                                               hjust = 1, vjust = 0.5,
                                               margin = margin(t = 2))
                        else element_blank(),
          axis.title.x = element_text(size = PT_LEGEND, colour = "black",
                                      margin = margin(t = 4)),
          axis.ticks = element_blank(),
          legend.position = "bottom",
          legend.title = element_text(size = PT_LEGEND, colour = "black"),
          legend.text = element_text(size = PT_LEGEND, colour = "black",
                                     margin = margin(l = 2, r = 1)),
          legend.key.spacing.x = grid::unit(4, "pt"),
          legend.key.width = grid::unit(9, "pt"),
          legend.key.height = grid::unit(7, "pt"),
          legend.margin = margin(t = 0),
          plot.margin = margin(1, 4, 1, 1))
}

p <- wrap_plots(lapply(seq_along(IND_ORDER), function(k)
       panel(IND_ORDER[k], first = k == 1, last = k == length(IND_ORDER))),
     ncol = 1) +
  plot_layout(guides = "collect") &
  theme(legend.position = "bottom", legend.justification = "left",
        legend.location = "plot")

dk_save(p, sprintf("figS2_origin_sector_heatmap_%s", YEAR), w = PRINT_W, h = PRINT_H,
        dpi = 600)
