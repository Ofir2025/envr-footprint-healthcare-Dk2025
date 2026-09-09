#!/usr/bin/env Rscript
# Danish health care - production layer decomposition, after Malik et al. (2021)
# Fig. 3, from the figure-ready facts in data/gold/results/07_malik_replication/:
#
#   production_layers_cumulative_by_group_2022  Malik Fig. 3: cumulative impact
#                                               against layer, stacked by the
#                                               same 19 upstream sector groups
#   production_layers_profile_2022              per-layer share and the
#                                               cumulative curve on one % axis
#   production_layers_by_origin_2022            each layer split Denmark against
#                                               imported, with the imported
#                                               share printed on the bar
#
# Why these three. Malik's figure answers "how far upstream does the pressure
# sit", which is the question a hospital procurement office cannot answer from a
# single footprint total: layer 0 is what the health system burns and emits
# itself, layer 1 its direct suppliers, and so on. The profile figure is the
# same decomposition read as a truncation test, which is the argument for using
# an MRIO at all rather than a first-tier supplier survey. The origin figure is
# the one that carries a policy consequence for Denmark, because leverage moves
# offshore as depth increases.
#
# Run:  Rscript R/plot_production_layers.R

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.R"))

SUB <- "production_layers"

# ---- indicator strips ------------------------------------------------------
# Units differ between indicators, so the unit belongs in the panel title. A
# single y-axis title covering five different units would be wrong.
IND_LAB <- c(
  climate_change        = "Greenhouse gases (kt CO2-eq)",
  material_extraction   = "Material extraction (kt)",
  blue_water_consumption = "Blue water consumption (Mm3)",
  land_use              = "Land use (km2)",
  waste_generation      = "Waste generation (kt)")
IND_ORDER <- names(IND_LAB)

#: The same panels without units, for the sheet whose axis is a percentage.
IND_BARE <- sub(" \\(.*$", "", IND_LAB)
names(IND_BARE) <- names(IND_LAB)

ind_factor <- function(x) factor(IND_LAB[x], levels = unname(IND_LAB))

# ---- the 19 sector groups --------------------------------------------------
# Malik's Fig. 3 shows all nineteen groups and so does this, which is a
# deliberate trade of separability for faithfulness: nineteen categories cannot
# all carry a distinct colourblind-safe hue. The mitigation is that hues are
# assigned semantically (energy carriers warm, materials earth, services and
# equipment cool) and luminance alternates between neighbours in the stack, so
# adjacent bands separate even where two hues are close.
GROUP_COLS <- c(
  `Transport`                                      = "#009E73",
  `Coal and Petroleum`                             = "#4D4D4D",
  `Food and catering`                              = "#66A61E",
  `Chemical`                                       = "#6A3D9A",
  `Electricity`                                    = "#D7301F",
  `Steam, hot water supply and water distribution` = "#FDBF6F",
  `Waste management and disposal`                  = "#E7298A",
  `Services`                                       = "#1F78B4",
  `Minerals and Metals`                            = "#8C6D31",
  `Natural gas and gaseous fuels`                  = "#FF7F00",
  `Construction`                                   = "#B15928",
  `Paper Products`                                 = "#CAB2D6",
  `Metal Products`                                 = "#A6CEE3",
  `Electrical, electronic and measuring equipment` = "#56B4E9",
  `Transport Equipment`                            = "#17BECF",
  `Non-metallic mineral products`                  = "#D9A65B",
  `Textile`                                        = "#FB9A99",
  `General and special Machinery`                  = "#BC80BD",
  `Furniture and timber`                           = "#A6D854")

# Five indicators do not fill a rectangular grid, so every sheet in this family
# has one empty cell. Malik's Fig. 3 uses that cell for the key and so does
# this: the legend is still at the foot of the sheet, still untitled, and now
# steals neither width from the panels nor a band of white space below them.
LEGEND_CELL <- c(0.845, 0.24)

ORIGIN_LAB  <- c(domestic = "Denmark", imported = "Imported")
ORIGIN_COLS <- c(Denmark = "#0072B2", Imported = "#E69F00")

# ============================================================ 1. Malik Fig. 3
d_grp <- read_csv(gold_path("production_layers_by_sector_group.csv"),
                  show_col_types = FALSE) %>%
  filter(indicator %in% IND_ORDER) %>%
  group_by(indicator, sector_group, layer) %>%
  summarise(value = sum(value), .groups = "drop") %>%
  arrange(indicator, sector_group, layer) %>%
  group_by(indicator, sector_group) %>%
  mutate(cumulative = cumsum(value)) %>%
  ungroup()

# Stack order: largest contributor at the foot of the stack, so the eye reads
# the dominant band against the axis rather than floating mid-panel.
grp_order <- d_grp %>%
  filter(indicator == "climate_change") %>%
  group_by(sector_group) %>%
  summarise(v = sum(value), .groups = "drop") %>%
  arrange(desc(v)) %>%
  pull(sector_group)
stopifnot(setdiff(grp_order, names(GROUP_COLS)) == character(0))

d_grp <- d_grp %>%
  mutate(panel = ind_factor(indicator),
         sector_group = factor(sector_group, levels = grp_order))

p1 <- ggplot(d_grp, aes(layer, cumulative, fill = sector_group)) +
  geom_area(position = position_stack(reverse = TRUE), colour = "white",
            linewidth = 0.12) +
  facet_wrap(~panel, scales = "free_y", ncol = 3) +
  scale_fill_manual(values = GROUP_COLS, breaks = grp_order, name = NULL) +
  scale_x_continuous(breaks = seq(0, 20, 4),
                     expand = expansion(mult = c(0, 0.01))) +
  scale_y_continuous(labels = smart_labs,
                     breaks = scales::extended_breaks(n = 5),
                     expand = expansion(mult = c(0, 0.04))) +
  guides(fill = guide_legend(ncol = 1, override.aes = list(colour = NA))) +
  labs(x = "Production layer (0 = the health system itself)",
       y = "Cumulative impact through layer n") +
  theme_dkhc() +
  theme(legend.position = "inside",
        legend.position.inside = LEGEND_CELL,
        legend.justification = c(0.5, 0.5),
        legend.text = element_text(size = 16),
        legend.key.height = grid::unit(1.05, "lines"),
        legend.key.width  = grid::unit(1.4, "lines"))

dk_save(p1, "production_layers_cumulative_by_group_2022", w = 19, h = 12,
        sub = SUB)

# ================================================== 2. layer profile, per cent
# share_pct and cumulative_share_pct are both percentages of the footprint, so
# bars and curve share one axis with no secondary scale.
d_pro <- read_csv(gold_path("production_layers.csv"), show_col_types = FALSE) %>%
  filter(indicator %in% IND_ORDER, grepl("^[0-9]+$", layer)) %>%
  # This sheet's axis is a percentage, so the unit carried in IND_LAB would be
  # wrong on its strips: the panel names go bare here.
  mutate(layer = as.integer(layer),
         panel = factor(IND_BARE[indicator], levels = unname(IND_BARE)))

p2 <- ggplot(d_pro, aes(layer)) +
  geom_col(aes(y = share_pct, fill = "Share arising in this layer"),
           width = 0.74) +
  geom_line(aes(y = cumulative_share_pct,
                colour = "Cumulative share through this layer"),
            linewidth = 0.9) +
  geom_point(aes(y = cumulative_share_pct,
                 colour = "Cumulative share through this layer"), size = 1.5) +
  facet_wrap(~panel, ncol = 3) +
  scale_fill_manual(values = c(`Share arising in this layer` = "#9EC9E2"),
                    name = NULL) +
  scale_colour_manual(
    values = c(`Cumulative share through this layer` = "#D7301F"), name = NULL) +
  scale_x_continuous(breaks = seq(0, 20, 4)) +
  scale_y_continuous(limits = c(0, 100), breaks = seq(0, 100, 25),
                     labels = function(x) paste0(x, "%"),
                     expand = expansion(mult = c(0, 0.02))) +
  guides(fill = guide_legend(order = 1, ncol = 1),
         colour = guide_legend(order = 2, ncol = 1)) +
  labs(x = "Production layer (0 = the health system itself)",
       y = "Share of the footprint") +
  theme_dkhc() +
  theme(legend.position = "inside",
        legend.position.inside = LEGEND_CELL,
        legend.justification = c(0.5, 0.5),
        legend.spacing.y = grid::unit(0.2, "lines"))

dk_save(p2, "production_layers_profile_2022", w = 18, h = 10, sub = SUB)

# ======================================================= 3. Denmark v imported
d_org <- read_csv(gold_path("production_layers_domestic_vs_imported.csv"),
                  show_col_types = FALSE) %>%
  filter(indicator %in% IND_ORDER) %>%
  mutate(panel  = ind_factor(indicator),
         origin = factor(ORIGIN_LAB[origin], levels = names(ORIGIN_COLS)))

# One label per layer at the top of the stack, carrying the imported share.
# Printed only where the layer is large enough to read, which is where the
# share is decision-relevant; below that the bars are slivers and a label would
# collide with its neighbour.
# Labels stop at layer 4. The message is the climb in the imported share over
# the first few layers, and by layer 5 the bars are close enough together that a
# label sits on its neighbour. A share that rounds to 100 is printed as ">99%",
# because no layer is wholly imported.
d_lab <- d_org %>%
  filter(layer <= 4) %>%
  group_by(panel, layer) %>%
  summarise(total = sum(value),
            imported = sum(value[origin == "Imported"]), .groups = "drop") %>%
  mutate(pct = 100 * imported / total,
         lab = if_else(pct >= 99.5, ">99%", sprintf("%.0f%%", pct)))

# Four equal intervals ending on a round number at or above the tallest stack,
# so every panel carries a labelled tick above its longest bar. `nice_ceiling`
# in _dk_common rounds up but says nothing about where the ticks land, and with
# a free scale the break algorithm was stopping one tick short.
nice_step <- function(x) {
  mag <- 10 ^ floor(log10(x))
  for (m in c(1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10))
    if (x <= m * mag) return(m * mag)
  10 * mag
}
# Room for the per-bar label is built into the ceiling rather than added by the
# scale's expansion, so the panel limit IS the ceiling and the four quarters of
# it are round numbers. Expanding the scale instead would put the top break at
# 1.06 times a round number, which prints as 1,272.
quarter_ceiling <- function(top) 4 * nice_step(top * 1.06 / 4)
quarter_breaks <- function(lims) seq(0, lims[2], length.out = 5)

d_ceiling <- d_org %>%
  group_by(panel, layer) %>%
  summarise(total = sum(value), .groups = "drop") %>%
  group_by(panel) %>%
  summarise(.ceiling = quarter_ceiling(max(total)), .groups = "drop")

p3 <- ggplot(d_org, aes(layer, value, fill = origin)) +
  geom_col(width = 0.76, position = position_stack(reverse = TRUE)) +
  geom_text(data = d_lab, inherit.aes = FALSE,
            aes(layer, total, label = lab), vjust = -0.55,
            size = 13 * MM_PER_PT, colour = INK, fontface = "bold") +
  # A free y scale trains itself on the data, so the tallest bar can sit above
  # the highest labelled tick. `facet_ceiling` in _dk_common lifts the extent on
  # x, which is the layer index here, so the ceiling is placed directly on y.
  geom_blank(data = d_ceiling, inherit.aes = FALSE,
             aes(x = 0, y = .ceiling)) +
  facet_wrap(~panel, scales = "free_y", ncol = 3) +
  scale_fill_manual(values = ORIGIN_COLS, name = NULL) +
  scale_x_continuous(breaks = seq(0, 20, 4)) +
  scale_y_continuous(labels = smart_labs, breaks = quarter_breaks,
                     expand = expansion(mult = c(0, 0))) +
  guides(fill = guide_legend(ncol = 1)) +
  labs(x = "Production layer (0 = the health system itself)",
       y = "Impact arising in the layer") +
  theme_dkhc() +
  theme(legend.position = "inside",
        legend.position.inside = LEGEND_CELL,
        legend.justification = c(0.5, 0.5))

dk_save(p3, "production_layers_by_origin_2022", w = 18, h = 10, sub = SUB)

# ---- what the figures say, printed so a run is self-documenting -------------
cc <- d_pro %>% filter(indicator == "climate_change")
org <- d_org %>% filter(indicator == "Greenhouse gases (kt CO2-eq)" |
                          panel == IND_LAB[["climate_change"]])
share <- org %>% group_by(layer) %>%
  summarise(imp = 100 * sum(value[origin == "Imported"]) / sum(value),
            .groups = "drop")
cat(sprintf(paste0("\nclimate change: layer 0 is %.1f%% of the footprint, ",
                   "the first three layers %.1f%%,\n  and %d layers are needed ",
                   "to pass 99%%. Imported share rises from %.0f%% in layer 0 ",
                   "to %.0f%% by layer 3.\n"),
            cc$share_pct[cc$layer == 0],
            sum(cc$share_pct[cc$layer <= 2]),
            min(cc$layer[cc$cumulative_share_pct >= 99]),
            share$imp[share$layer == 0], share$imp[share$layer == 3]))
cat("production layer figures written to ", file.path(fig_dir, SUB), "\n",
    sep = "")
