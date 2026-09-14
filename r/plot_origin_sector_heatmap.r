#!/usr/bin/env Rscript
# Where the Danish health care footprint arises: producing country or region by
# producing sector group, for all five impact categories on one sheet.
#
#   columns  the 49 EXIOBASE countries and rest-of-world regions, plus "No region"
#            for the indirect parts of the travel terms, which the Dutch inventory
#            quantifies without a place; grouped by world region, Denmark first
#   rows     the twelve largest of the scope layer's 21 producing sector groups (the
#            groups of Appendix A's scope figures), by their mean share across the
#            five categories, and the other nine pooled into one row that is ranked
#            by its own value; 21 rows in five panels overprinted their labels
#   panels   one per impact category, sharing the row order and the columns
#   fill     the cell's share of that category's footprint, in eight bins on a
#            sequential YlOrRd scale, so a 0.1 % cell and a 40 % cell sit on one
#            key; a cell with no footprint at all is left white
#
# Shares, not absolute values, because the five categories have different units
# and one colour key must serve all of them. Cells of 10 % or more carry their
# share, in whichever of near-black and white reads better on the fill.
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

YEAR <- Sys.getenv("HC_ANALYSIS_YEAR", "2022")

IND_ORDER <- c("climate_change", "material_extraction", "blue_water_consumption",
               "land_use", "waste_generation")
IND_STRIP <- c(climate_change = "Climate~change~(kt~CO[2]*'-eq')",
               material_extraction = "Material~extraction~(kt)",
               blue_water_consumption = "Blue~water~consumption~(Mm^3)",
               land_use = "Land~use~(km^2)",
               waste_generation = "Waste~generation~(kt)")
REGION_GROUPS <- c("Denmark", "Europe", "Asia and Pacific", "America", "Africa",
                   "Middle East", "No region")
# Two-line strips for the narrow groups, whose single-line names ran into each other.
REGION_STRIP <- c(Denmark = "Denmark", Europe = "Europe",
                  `Asia and Pacific` = "Asia and Pacific", America = "America",
                  Africa = "Africa", `Middle East` = "Middle\nEast",
                  `No region` = "No\nregion")
N_SECTORS <- 12
OTHER_SECTORS <- "Other sector groups"

# Sentence case for the scope layer's group names; the published table keeps its own.
SECTOR_LABEL <- c(
  "Minerals and Metals" = "Minerals and metals",
  "Coal and Petroleum" = "Coal and petroleum",
  "Metal Products" = "Metal products",
  "Paper Products" = "Paper products",
  "General and special Machinery" = "General and special machinery",
  "Transport Equipment" = "Transport equipment",
  "Operational impact" = "Operational impacts",
  "Private travel" = "Commuting and patient and visitor travel",
  "Steam, hot water supply and water distribution" = "Steam, hot water and water distribution")

BIN_BREAKS <- c(0, 0.01, 0.1, 0.5, 1, 5, 10, 25, Inf)
BIN_LABELS <- c("up to 0.01", "0.01 to 0.1", "0.1 to 0.5", "0.5 to 1",
                "1 to 5", "5 to 10", "10 to 25", "25 or more")
# ColorBrewer YlOrRd, eight classes from its nine (the palest step is left out so
# the lowest bin still separates from the white of an empty cell).
BIN_COLS <- setNames(c("#FFEDA0", "#FED976", "#FEB24C", "#FD8D3C",
                       "#FC4E2A", "#E31A1C", "#BD0026", "#800026"), BIN_LABELS)

rel_luminance <- function(hex) {
  v <- grDevices::col2rgb(hex) / 255
  lin <- ifelse(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ^ 2.4)
  as.numeric(c(0.2126, 0.7152, 0.0722) %*% lin)
}
ink_for <- function(fill) ifelse(vapply(fill, rel_luminance, numeric(1)) < 0.3,
                                 "#FFFFFF", INK)

d <- read_csv(gold_path("hotspot_by_producing_country_and_sector_group.csv"),
              show_col_types = FALSE) %>%
  filter(indicator %in% IND_ORDER) %>%
  mutate(region = if_else(producing_country_iso3 == "GLO", "No region",
                          producing_world_region),
         column = case_when(producing_country_iso3 == "GLO" ~ "No region",
                            TRUE ~ region_code(producing_country_iso3)),
         sector = dplyr::recode(producing_sector_group, !!!SECTOR_LABEL)) %>%
  group_by(indicator, region, column, sector) %>%
  summarise(value = sum(value), .groups = "drop")

# keep the largest sector groups by their mean share across the categories
keep <- d %>% group_by(indicator) %>% mutate(s = value / sum(value)) %>%
  group_by(sector) %>% summarise(v = mean(s), .groups = "drop") %>%
  arrange(desc(v)) %>% head(N_SECTORS) %>% pull(sector)
d <- d %>%
  mutate(sector = if_else(sector %in% keep, sector, OTHER_SECTORS)) %>%
  group_by(indicator, region, column, sector) %>%
  summarise(value = sum(value), .groups = "drop") %>%
  group_by(indicator) %>%
  mutate(share_pct = 100 * value / sum(value)) %>%
  ungroup()

stopifnot(all(abs(d %>% group_by(indicator) %>%
                    summarise(t = sum(share_pct)) %>% pull(t) - 100) < 1e-6))

# every country-sector-indicator combination, so an empty cell is drawn white
grid <- tidyr::expand_grid(indicator = IND_ORDER,
                           distinct(d, region, column),
                           sector = unique(d$sector)) %>%
  left_join(d, by = c("indicator", "region", "column", "sector")) %>%
  mutate(share_pct = coalesce(share_pct, 0))

col_order <- d %>% group_by(region, column) %>%
  summarise(v = sum(share_pct), .groups = "drop") %>%
  mutate(region = factor(region, levels = REGION_GROUPS)) %>%
  arrange(region, desc(v)) %>% pull(column)
row_order <- d %>% group_by(sector) %>%
  summarise(v = sum(share_pct) / length(IND_ORDER), .groups = "drop") %>%
  arrange(v) %>% pull(sector)

grid <- grid %>%
  mutate(indicator = factor(indicator, levels = IND_ORDER),
         region = factor(region, levels = REGION_GROUPS),
         column = factor(column, levels = col_order),
         sector = factor(sector, levels = row_order),
         bin = if_else(share_pct > 0,
                       as.character(cut(share_pct, BIN_BREAKS, labels = BIN_LABELS,
                                        right = TRUE, include.lowest = FALSE)),
                       NA_character_),
         bin = factor(bin, levels = BIN_LABELS),
         label = if_else(share_pct >= 10, sprintf("%.0f", share_pct), NA_character_),
         ink = if_else(is.na(bin), INK, ink_for(BIN_COLS[as.character(bin)])))

p <- ggplot(grid, aes(column, sector)) +
  geom_tile(aes(fill = bin), colour = "grey88", linewidth = 0.25) +
  geom_text(aes(label = label, colour = ink), size = 3.1, fontface = "bold",
            na.rm = TRUE) +
  scale_colour_identity() +
  scale_fill_manual(values = BIN_COLS, breaks = BIN_LABELS, drop = FALSE,
                    na.value = "white",
                    name = "Share of the impact category (%)") +
  facet_grid(indicator ~ region, scales = "free_x", space = "free_x",
             labeller = labeller(indicator = as_labeller(IND_STRIP, label_parsed),
                                 region = as_labeller(REGION_STRIP))) +
  scale_x_discrete(expand = c(0, 0)) +
  scale_y_discrete(expand = c(0, 0)) +
  labs(x = "Country or region of production", y = NULL) +
  guides(fill = guide_legend(nrow = 1, title.position = "left",
                             override.aes = list(colour = "grey70"))) +
  theme_dkhc() +
  theme(panel.grid.major = element_blank(),
        panel.spacing.x = grid::unit(0.35, "lines"),
        panel.spacing.y = grid::unit(0.9, "lines"),
        axis.text.x = element_text(size = 10.5, angle = 90, hjust = 1, vjust = 0.5,
                                   colour = "black"),
        axis.text.y = element_text(size = 12, colour = "black"),
        strip.text.x = element_text(size = 12.5, face = "bold", lineheight = 0.95),
        strip.text.y = element_text(size = 13, angle = 0, hjust = 0, face = "bold"),
        legend.title = element_text(size = 13, colour = INK),
        legend.text = element_text(size = 12.5, colour = INK),
        plot.margin = margin(10, 14, 10, 10))

dk_save(p, sprintf("figS2_origin_sector_heatmap_%s", YEAR), w = 22, h = 15)
