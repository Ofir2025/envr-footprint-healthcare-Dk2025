#!/usr/bin/env Rscript
# Manuscript figures, Denmark 2022.
#
#   fig1  Ofir's figures 1-3 combined into ONE panelled figure: activity
#         contribution, sector contribution and geographical origin, each across
#         the five impact categories. Steenmeijer aggregation kept unchanged.
#   fig2  the largest producing region x industry pairs, ranked within each
#         impact category, EXIOBASE codes on the axis
#   fig3  GHG-Protocol scopes across the five categories, stacked
#   fig4  where scope 2 arises, by producing region x industry
#   fig5  where scope 3 arises, by producing region x industry
#   fig6  the same sources as one stacked bar per pair, scope as fill
#   figS1 geographical origin on its own, for the SI
#
# Run:  Rscript R/plot_manuscript_figures.R

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.R"))

YEAR <- Sys.getenv("HC_ANALYSIS_YEAR", "2022")

IND_ORDER <- c("climate_change", "material_extraction", "blue_water_consumption",
               "land_use", "waste_generation")
IND_UNIT_EXPR <- c(climate_change = "kt~CO[2]*'-eq'", material_extraction = "kt",
                   blue_water_consumption = "Mm^3", land_use = "km^2",
                   waste_generation = "kt")
IND_UNIT_TXT <- c(climate_change = "kt CO2-eq", material_extraction = "kt",
                  blue_water_consumption = "Mm3", land_use = "km2",
                  waste_generation = "kt")
IND_NAME <- c(climate_change = "Climate change",
              material_extraction = "Material extraction",
              blue_water_consumption = "Blue water consumption",
              land_use = "Land use", waste_generation = "Waste generation")
ind_factor <- function(x) factor(x, levels = IND_ORDER)

# Strips carry the category AND its absolute total: the axis is a percentage, so
# a strip reading only "kt CO2-eq" would invite the bars to be read as absolute.
# Totals are computed from the data being plotted, never typed in.
make_labeller <- function(d) {
  tot <- d %>% group_by(indicator) %>% summarise(v = sum(value), .groups = "drop")
  as_labeller(setNames(
    sprintf("atop('%s', '%s '*%s)", IND_NAME[as.character(tot$indicator)],
            formatC(tot$v, format = "f", digits = 0, big.mark = ","),
            IND_UNIT_EXPR[as.character(tot$indicator)]),
    as.character(tot$indicator)), default = label_parsed)
}
# For grids and per-scope panels, where a total on every strip would mislead.
ind_only_labeller <- as_labeller(
  setNames(sprintf("atop('%s', (%s))", IND_NAME, IND_UNIT_EXPR), names(IND_NAME)),
  default = label_parsed)

GROUP_COLS <- c(
  "Pharmaceuticals and chemical products" = "#0072B2",
  "Pharmaceutical and chemical industry"  = "#0072B2",
  "Services" = "#009E73", "Transport" = "#E69F00",
  "Food and food services" = "#56B4E9", "Agricultural sector" = "#56B4E9",
  "Individual travel" = "#CC79A7",
  "Medical, electrical equipment and machinery" = "#D55E00",
  "Operational impacts" = "#8C564B",
  "Heat and electricity" = "#F0E442", "Electricity sector" = "#F0E442",
  "Fossil fuel industry" = "#7F7F7F", "Mining of minerals and metals" = "#B87333",
  "Denmark" = "#0072B2", "Europe" = "#009E73", "Asia and Pacific" = "#E69F00",
  "Middle East" = "#CC79A7", "America" = "#56B4E9", "Africa" = "#D55E00",
  "Unallocated" = "grey80")

gold <- function(f) read_csv(gold_path(f), show_col_types = FALSE)
strip_key <- function(x) sub("\\|\\|\\|.*$", "", x)

# Order a per-panel key by its own value, so every panel ranks independently.
order_key <- function(d) {
  o <- d %>% group_by(key) %>% summarise(v = sum(value), .groups = "drop") %>%
    arrange(v)
  d %>% mutate(key = factor(key, levels = o$key))
}

# ========= fig 1  Ofir's figures 1-3, combined into one panelled figure ======
f1 <- gold("figure1_activity_contributions.csv") %>%
  transmute(indicator, value, share_pct, group = contribution_group,
            analysis = "A  Activity contribution")
f2 <- gold("figure2_sector_contributions.csv") %>%
  transmute(indicator, value, share_pct, group = hotspot_group,
            analysis = "B  Sector contribution")
f3 <- gold("figure3_geographical_origin.csv") %>%
  transmute(indicator, value, share_pct, group = producing_world_region,
            analysis = "C  Geographical origin")

d1 <- bind_rows(f1, f2, f3) %>%
  mutate(indicator = ind_factor(indicator),
         analysis = factor(analysis, levels = c("A  Activity contribution",
                                                "B  Sector contribution",
                                                "C  Geographical origin")),
         key = paste0(group, "|||", as.integer(analysis))) %>%
  order_key()

p1 <- ggplot(d1, aes(share_pct, key, fill = group)) +
  geom_col(width = 0.74, colour = "white", linewidth = 0.15) +
  facet_grid(analysis ~ indicator, scales = "free_y", space = "free_y",
             labeller = labeller(indicator = ind_only_labeller,
                                 analysis = label_value)) +
  scale_y_discrete(labels = strip_key) +
  scale_fill_manual(values = GROUP_COLS, guide = "none") +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                     guide = guide_axis(check.overlap = TRUE),
                     expand = expansion(mult = c(0, 0.05))) +
  labs(x = "Share of the impact category (%)", y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 12),
        strip.text.y = element_text(size = 14, angle = 0, hjust = 0,
                                    margin = margin(l = 9)),
        strip.text.x = element_text(size = 15),
        panel.spacing.x = grid::unit(1.6, "lines"),
        plot.margin = margin(14, 26, 12, 14))

dk_save(p1, sprintf("fig1_ofir_panels_%s", YEAR), w = 23, h = 14.5)

# ================= fig 2  top producing region x industry pairs =============
d2 <- gold("figure2b_top_origin_industry_pairs.csv") %>%
  mutate(indicator = ind_factor(indicator),
         pair = if_else(producing_sector_code == "OTHER", "All other pairs",
                        paste0(region_code(producing_country_iso3), SEP,
                               producing_sector_code)),
         is_rest = producing_sector_code == "OTHER",
         key = paste0(pair, "|||", as.integer(indicator))) %>%
  order_key()

p2 <- ggplot(d2, aes(share_pct, key, fill = is_rest)) +
  geom_col(width = 0.74, colour = "white", linewidth = 0.15) +
  facet_wrap(~indicator, ncol = 3, scales = "free_y",
             labeller = make_labeller(d2)) +
  scale_y_discrete(labels = strip_key) +
  scale_fill_manual(values = c(`FALSE` = "#0072B2", `TRUE` = "grey80"),
                    guide = "none") +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                     expand = expansion(mult = c(0, 0.05))) +
  labs(x = "Share of the impact category (%)", y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 13, family = "mono"),
        plot.margin = margin(14, 26, 12, 14))

dk_save(p2, sprintf("fig2_top_origin_industry_pairs_%s", YEAR), w = 17, h = 11)

# ================= fig 3  scopes, stacked ===================================
# Faceting the scopes was tried and dropped: three of five categories have no
# direct term, so a facet grid draws empty panels. Material extraction, blue
# water and land use are ZERO in scope 1 by EXIOBASE's accounting rather than by
# a data gap - extraction, abstraction and land occupation are attributed to
# extractive and agricultural industries, so a health SERVICE industry has no
# direct row. A stacked bar shows that cleanly by drawing nothing.
d3 <- gold("scope_by_continent.csv") %>%
  group_by(indicator, unit, scope) %>%
  summarise(value = sum(value), .groups = "drop") %>%
  group_by(indicator) %>%
  mutate(share_pct = 100 * value / sum(value), total = sum(value)) %>%
  ungroup() %>%
  mutate(indicator = ind_factor(indicator),
         scope = factor(scope, levels = SCOPE_ORDER),
         lab = sprintf("%s\n%s %s", IND_NAME[as.character(indicator)],
                       formatC(total, format = "f", digits = 0, big.mark = ","),
                       IND_UNIT_TXT[as.character(indicator)]))
d3 <- d3 %>% mutate(lab = factor(lab, levels = rev(unique(lab[order(indicator)]))))

p3 <- ggplot(d3, aes(share_pct, lab, fill = scope)) +
  geom_col(width = 0.68, colour = "white", linewidth = 0.2,
           position = position_stack(reverse = TRUE)) +
  geom_text(aes(label = if_else(share_pct >= 6, sprintf("%.0f%%", share_pct),
                                NA_character_)),
            position = position_stack(vjust = 0.5, reverse = TRUE),
            colour = "white", fontface = "bold", size = 4.6, na.rm = TRUE) +
  scale_fill_manual(values = SCOPE_COLS, name = NULL) +
  scale_x_continuous(labels = function(x) paste0(smart_labs(x), "%"),
                     breaks = seq(0, 100, 25),
                     expand = expansion(mult = c(0, 0.01))) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(x = "Share of the impact category", y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 14, lineheight = 1.15))

dk_save(p3, sprintf("fig3_scopes_stacked_%s", YEAR), w = 14, h = 8.5)

# ========= fig 4 / fig 5  where scope 2 and scope 3 arise, by pair ==========
pairs_src <- gold("scope_by_origin_and_industry.csv") %>%
  filter(producing_country_iso3 != "GLO",
         !grepl("^BU_", producing_sector_code)) %>%
  mutate(indicator = ind_factor(indicator),
         pair = paste0(region_code(producing_country_iso3), SEP,
                       producing_sector_code))

scope_source_plot <- function(which_scope, n = 12) {
  d <- pairs_src %>% filter(scope == which_scope) %>%
    group_by(indicator, pair) %>%
    summarise(value = sum(value), .groups = "drop") %>%
    group_by(indicator) %>%
    mutate(share_pct = 100 * value / sum(value)) %>%
    slice_max(value, n = n, with_ties = FALSE) %>% ungroup() %>%
    mutate(key = paste0(pair, "|||", as.integer(indicator))) %>%
    order_key()
  ggplot(d, aes(share_pct, key)) +
    geom_col(width = 0.72, colour = "white", linewidth = 0.15,
             fill = unname(SCOPE_COLS[which_scope])) +
    facet_wrap(~indicator, ncol = 3, scales = "free",
               labeller = ind_only_labeller) +
    scale_y_discrete(labels = strip_key) +
    scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(3),
                       guide = guide_axis(check.overlap = TRUE),
                       expand = expansion(mult = c(0, 0.07))) +
    labs(x = sprintf("Share of %s within the impact category (%%)",
                     tolower(which_scope)), y = NULL) +
    theme_dkhc() +
    theme(panel.grid.major.y = element_blank(),
          axis.text.y = element_text(size = 12.5, family = "mono"),
          plot.margin = margin(14, 32, 12, 14))
}

dk_save(scope_source_plot("Scope 2"), sprintf("fig4_scope2_sources_%s", YEAR),
        w = 17, h = 10.5)
dk_save(scope_source_plot("Scope 3"), sprintf("fig5_scope3_sources_%s", YEAR),
        w = 17, h = 10.5)

# ============ fig 6  the same sources, stacked by scope, per pair ===========
d6 <- pairs_src %>%
  filter(scope %in% c("Scope 1", "Scope 2", "Scope 3")) %>%
  group_by(indicator, pair, scope) %>%
  summarise(value = sum(value), .groups = "drop")
top6 <- d6 %>% group_by(indicator, pair) %>%
  summarise(v = sum(value), .groups = "drop") %>%
  group_by(indicator) %>% slice_max(v, n = 12, with_ties = FALSE) %>% ungroup()
d6 <- d6 %>% semi_join(top6, by = c("indicator", "pair")) %>%
  group_by(indicator) %>% mutate(share_pct = 100 * value / sum(value)) %>%
  ungroup() %>%
  mutate(scope = factor(scope, levels = SCOPE_ORDER),
         key = paste0(pair, "|||", as.integer(indicator))) %>%
  order_key()

p6 <- ggplot(d6, aes(share_pct, key, fill = scope)) +
  geom_col(width = 0.72, colour = "white", linewidth = 0.15,
           position = position_stack(reverse = TRUE)) +
  facet_wrap(~indicator, ncol = 3, scales = "free",
             labeller = ind_only_labeller) +
  scale_y_discrete(labels = strip_key) +
  scale_fill_manual(values = SCOPE_COLS, name = NULL, drop = TRUE) +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(3),
                     guide = guide_axis(check.overlap = TRUE),
                     expand = expansion(mult = c(0, 0.07))) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(x = "Share of the impact category (%)", y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 12.5, family = "mono"),
        plot.margin = margin(14, 32, 12, 14))

dk_save(p6, sprintf("fig6_scope_pairs_stacked_%s", YEAR), w = 17, h = 10.5)

# ===================== SI  geographical origin on its own ===================
dS <- gold("figure3_geographical_origin.csv") %>%
  mutate(indicator = ind_factor(indicator),
         key = paste0(producing_world_region, "|||", as.integer(indicator))) %>%
  order_key()

pS <- ggplot(dS, aes(share_pct, key, fill = producing_world_region)) +
  geom_col(width = 0.72, colour = "white", linewidth = 0.15) +
  facet_wrap(~indicator, ncol = 3, scales = "free_y",
             labeller = make_labeller(dS)) +
  scale_y_discrete(labels = strip_key) +
  scale_fill_manual(values = GROUP_COLS, guide = "none") +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                     expand = expansion(mult = c(0, 0.05))) +
  labs(x = "Share of the impact category (%)", y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 14))

dk_save(pS, sprintf("figS1_geographical_origin_%s", YEAR), w = 15, h = 9.5)

cat("\nmanuscript figures written to ", fig_dir, "\n", sep = "")
