#!/usr/bin/env Rscript
# Manuscript figures, Denmark 2022. Faceted across the five impact categories
# rather than drawn one category at a time.
#
#   fig1  activity contributions, Steenmeijer aggregation (9 groups)
#   fig2  the largest producing region x industry pairs, EXIOBASE codes
#   fig3  GHG-Protocol scopes across all five categories
#   fig3b scope 2 and 3 resolved to producing region x industry
#   figS1 geographical origin (the submitted figure 3, kept for the SI)
#
# Run:  Rscript R/plot_manuscript_figures.R

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.R"))

YEAR <- Sys.getenv("HC_ANALYSIS_YEAR", "2022")

# ---- indicator panel labels ------------------------------------------------
# Units carried in the strip, as plotmath so the subscript renders. The TIFF
# font has no subscript glyph, which is why these never go through Unicode.
IND_ORDER <- c("climate_change", "material_extraction", "blue_water_consumption",
               "land_use", "waste_generation")
# The axis is a percentage, so a strip reading only "kt CO2-eq" would invite the
# reader to take the bars as absolute. Each strip therefore carries the category
# AND its absolute total, which restores the magnitude and makes the % axis
# unambiguous. Totals are computed from the data being plotted, never typed in.
IND_UNIT_EXPR <- c(
  climate_change         = "kt~CO[2]*'-eq'",
  material_extraction    = "kt",
  blue_water_consumption = "Mm^3",
  land_use               = "km^2",
  waste_generation       = "kt")
IND_NAME <- c(
  climate_change         = "Climate change",
  material_extraction    = "Material extraction",
  blue_water_consumption = "Blue water consumption",
  land_use               = "Land use",
  waste_generation       = "Waste generation")

make_labeller <- function(d) {
  tot <- d %>% group_by(indicator) %>%
    summarise(v = sum(value), .groups = "drop")
  lab <- setNames(
    sprintf("atop('%s', '%s '*%s)",
            IND_NAME[as.character(tot$indicator)],
            formatC(tot$v, format = "f", digits = 0, big.mark = ","),
            IND_UNIT_EXPR[as.character(tot$indicator)]),
    as.character(tot$indicator))
  as_labeller(lab, default = label_parsed)
}

ind_factor <- function(x) factor(x, levels = IND_ORDER)

# Okabe-Ito, one hue per key, checked for a repeated hue within each legend.
GROUP_COLS <- c(
  "Pharmaceuticals and chemical products"       = "#0072B2",
  "Pharmaceutical and chemical industry"        = "#0072B2",
  "Services"                                    = "#009E73",
  "Transport"                                   = "#E69F00",
  "Food and food services"                      = "#56B4E9",
  "Agricultural sector"                         = "#56B4E9",
  "Individual travel"                           = "#CC79A7",
  "Medical, electrical equipment and machinery" = "#D55E00",
  "Operational impacts"                         = "#8C564B",
  "Heat and electricity"                        = "#F0E442",
  "Electricity sector"                          = "#F0E442",
  "Fossil fuel industry"                        = "#7F7F7F",
  "Mining of minerals and metals"               = "#B87333",
  "Unallocated"                                 = "grey80")

# Shared ordering across panels: rank on the headline indicator so a group sits
# in the same row in every facet and the panels can be read across.
order_by_climate <- function(d, key) {
  ord <- d %>% filter(indicator == "climate_change") %>%
    group_by(.data[[key]]) %>% summarise(v = sum(value), .groups = "drop") %>%
    arrange(v) %>% pull(.data[[key]])
  missing <- setdiff(unique(d[[key]]), ord)
  d %>% mutate(!!key := factor(.data[[key]], levels = c(missing, ord)))
}

gold <- function(f) read_csv(gold_path(f), show_col_types = FALSE)

# ===================================================== fig 1  activities =====
d1 <- gold("figure1_activity_contributions.csv") %>%
  mutate(indicator = ind_factor(indicator)) %>%
  order_by_climate("contribution_group")

p1 <- ggplot(d1, aes(share_pct, contribution_group, fill = contribution_group)) +
  geom_col(width = 0.74, colour = "white", linewidth = 0.15) +
  facet_wrap(~indicator, ncol = 3, labeller = make_labeller(d1)) +
  scale_fill_manual(values = GROUP_COLS, guide = "none") +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                     expand = expansion(mult = c(0, 0.04))) +
  labs(x = "Share of the impact category (%)", y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 15),
        plot.margin = margin(14, 26, 12, 14))

dk_save(p1, sprintf("fig1_activity_contributions_%s", YEAR), w = 17, h = 10.5)

# ============================== fig 2  top producing region x industry =======
d2 <- gold("figure2b_top_origin_industry_pairs.csv") %>%
  mutate(indicator = ind_factor(indicator),
         pair = if_else(producing_sector_code == "OTHER",
                        "All other pairs",
                        paste0(region_code(producing_country_iso3), SEP,
                               producing_sector_code)),
         is_rest = producing_sector_code == "OTHER")

# Per-facet ranking: a unique key per (pair, panel) ordered by that panel's own
# value, then the panel suffix is stripped from the labels. Free y scales, so
# each category shows its own largest contributors.
d2 <- d2 %>%
  mutate(key = paste0(pair, "|||", as.integer(indicator)))
ord2 <- d2 %>% group_by(key) %>% summarise(v = sum(value), .groups = "drop") %>%
  arrange(v) %>% pull(key)
d2 <- d2 %>% mutate(key = factor(key, levels = ord2))

p2 <- ggplot(d2, aes(share_pct, key, fill = is_rest)) +
  geom_col(width = 0.74, colour = "white", linewidth = 0.15) +
  scale_y_discrete(labels = function(x) sub("\\|\\|\\|.*$", "", x)) +
  facet_wrap(~indicator, ncol = 3, scales = "free_y",
             labeller = make_labeller(d2)) +
  scale_fill_manual(values = c(`FALSE` = "#0072B2", `TRUE` = "grey80"),
                    guide = "none") +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                     expand = expansion(mult = c(0, 0.04))) +
  labs(x = "Share of the impact category (%)", y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 13, family = "mono"),
        plot.margin = margin(14, 26, 12, 14))

dk_save(p2, sprintf("fig2_top_origin_industry_pairs_%s", YEAR), w = 17, h = 11)

# ===================================================== fig 3  scopes =========
d3 <- gold("scope_by_continent.csv") %>%
  group_by(indicator, unit, scope) %>%
  summarise(value = sum(value), .groups = "drop") %>%
  group_by(indicator) %>% mutate(share_pct = 100 * value / sum(value)) %>%
  ungroup() %>%
  mutate(indicator = ind_factor(indicator),
         scope = factor(scope, levels = rev(SCOPE_ORDER)))

p3 <- ggplot(d3, aes(share_pct, scope, fill = scope)) +
  geom_col(width = 0.7, colour = "white", linewidth = 0.15) +
  facet_wrap(~indicator, ncol = 3, labeller = make_labeller(d3)) +
  scale_fill_manual(values = SCOPE_COLS, guide = "none") +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                     expand = expansion(mult = c(0, 0.04))) +
  labs(x = "Share of the impact category (%)", y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 15))

dk_save(p3, sprintf("fig3_scopes_by_impact_%s", YEAR), w = 15, h = 9.5)

# ------------- fig 3b  scopes 2 and 3 by producing region x industry --------
d3b <- gold("scope_by_continent_and_industry_group.csv") %>%
  filter(scope %in% c("Scope 2", "Scope 3")) %>%
  mutate(indicator = ind_factor(indicator)) %>%
  top_n_bucket("producing_sector_group", "value", n = 10,
               label = "Remaining industry groups") %>%
  group_by(indicator, unit, scope, producing_sector_group) %>%
  summarise(value = sum(value), .groups = "drop") %>%
  group_by(indicator, scope) %>% mutate(share_pct = 100*value/sum(value)) %>%
  ungroup() %>%
  order_by_climate("producing_sector_group")

p3b <- ggplot(d3b, aes(share_pct, producing_sector_group, fill = scope)) +
  geom_col(width = 0.72, colour = "white", linewidth = 0.15,
           position = position_dodge(width = 0.78)) +
  facet_wrap(~indicator, ncol = 3, labeller = make_labeller(d3b)) +
  scale_fill_manual(values = SCOPE_COLS[c("Scope 2", "Scope 3")], name = NULL) +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                     expand = expansion(mult = c(0, 0.04))) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(x = "Share of the scope within the impact category (%)", y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 13))

dk_save(p3b, sprintf("fig3b_scope_by_industry_group_%s", YEAR), w = 17, h = 11)

# ============================ SI  geographical origin (submitted figure 3) ==
dS <- gold("figure3_geographical_origin.csv") %>%
  mutate(indicator = ind_factor(indicator)) %>%
  order_by_climate("producing_world_region")

pS <- ggplot(dS, aes(share_pct, producing_world_region,
                     fill = producing_world_region)) +
  geom_col(width = 0.72, colour = "white", linewidth = 0.15) +
  facet_wrap(~indicator, ncol = 3, labeller = make_labeller(dS)) +
  scale_fill_manual(values = REGION_COLS, guide = "none") +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                     expand = expansion(mult = c(0, 0.04))) +
  labs(x = "Share of the impact category (%)", y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 15))

dk_save(pS, sprintf("figS1_geographical_origin_%s", YEAR), w = 15, h = 9.5)

cat("\nmanuscript figures written to ", fig_dir, "\n", sep = "")
