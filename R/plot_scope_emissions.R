#!/usr/bin/env Rscript
# Danish health care 2022 - GHG-Protocol scope 1-3 emissions by origin and by
# industry. Four figures, from the figure-ready facts in
# data/gold/results/02_scopes_wood_hertwich/:
#
#   scope_emissions_by_continent_2022        scopes x world region of origin
#   scope_emissions_by_industry_group_2022   scopes x industry group
#   scope_emissions_top_origins_2022         top 20 (country, industry) pairs
#   scope_emissions_continent_by_industry_2022  the cross, faceted by region
#
# Run:  Rscript R/plot_scope_emissions.R

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.R"))

UNIT_LAB <- expression("Greenhouse gas emissions (kt CO"[2]*"-eq)")

scope_factor <- function(x) factor(x, levels = SCOPE_ORDER)

# ---------------------------------------------------------------- 1. continent
d_cont <- read_csv(gold_path("scope_by_continent.csv"), show_col_types = FALSE) %>%
  mutate(scope  = scope_factor(scope),
         region = factor(producing_world_region,
                         levels = intersect(REGION_ORDER,
                                            unique(producing_world_region))))

# Regions ranked by total emissions; first factor level is the panel bottom,
# so ascending order puts the largest at the top.
ord <- d_cont %>% group_by(region) %>% summarise(v = sum(value), .groups = "drop") %>%
  arrange(v) %>% pull(region)

p1 <- ggplot(mutate(d_cont, region = factor(region, levels = ord)),
             aes(value, region, fill = scope)) +
  geom_col(width = 0.72, colour = "white", linewidth = 0.15,
           position = position_stack(reverse = TRUE)) +
  scale_fill_manual(values = SCOPE_COLS, breaks = SCOPE_ORDER, name = NULL) +
  scale_x_continuous(labels = smart_labs, breaks = scales::extended_breaks(n = 5),
                     limits = c(0, nice_ceiling(
                       d_cont %>% group_by(region) %>%
                         summarise(v = sum(value)) %>% pull(v))),
                     expand = expansion(mult = c(0, 0.02))) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(x = UNIT_LAB, y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank())

dk_save(p1, "scope_emissions_by_continent_2022", w = 15, h = 9.5)

# ----------------------------------------------------------- 2. industry group
d_ind <- read_csv(gold_path("scope_by_industry_group.csv"), show_col_types = FALSE) %>%
  mutate(scope = scope_factor(scope)) %>%
  top_n_bucket("producing_sector_group", "value", n = 15) %>%
  group_by(producing_sector_group, scope) %>%
  summarise(value = sum(value), .groups = "drop")

ord_i <- d_ind %>% group_by(producing_sector_group) %>%
  summarise(v = sum(value), .groups = "drop") %>% arrange(v) %>%
  pull(producing_sector_group)

p2 <- ggplot(mutate(d_ind, producing_sector_group =
                      factor(producing_sector_group, levels = ord_i)),
             aes(value, producing_sector_group, fill = scope)) +
  geom_col(width = 0.72, colour = "white", linewidth = 0.15,
           position = position_stack(reverse = TRUE)) +
  scale_fill_manual(values = SCOPE_COLS, breaks = SCOPE_ORDER, name = NULL) +
  scale_x_continuous(labels = smart_labs, breaks = scales::extended_breaks(n = 5),
                     limits = c(0, nice_ceiling(
                       d_ind %>% group_by(producing_sector_group) %>%
                         summarise(v = sum(value)) %>% pull(v))),
                     expand = expansion(mult = c(0, 0.02))) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(x = UNIT_LAB, y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank())

dk_save(p2, "scope_emissions_by_industry_group_2022", w = 16, h = 10)

# ------------------------------------------------------------- 3. top origins
d_top <- read_csv(gold_path("scope_by_origin_industry_top25.csv"),
                  show_col_types = FALSE) %>%
  mutate(scope = scope_factor(scope),
         pair  = if_else(is_remainder, REMAINDER_LAB,
                         paste0(producing_country_iso3, SEP,
                                clean_sector_label(producing_sector_name))))

ord_p <- d_top %>% group_by(pair) %>% summarise(v = sum(value), .groups = "drop") %>%
  arrange(v) %>% pull(pair)

p3 <- ggplot(mutate(d_top, pair = factor(pair, levels = ord_p)),
             aes(value, pair, fill = scope)) +
  geom_col(width = 0.72, colour = "white", linewidth = 0.15,
           position = position_stack(reverse = TRUE)) +
  scale_fill_manual(values = SCOPE_COLS, breaks = SCOPE_ORDER, name = NULL) +
  scale_x_continuous(labels = smart_labs, breaks = scales::extended_breaks(n = 5),
                     limits = c(0, nice_ceiling(
                       d_top %>% group_by(pair) %>%
                         summarise(v = sum(value)) %>% pull(v))),
                     expand = expansion(mult = c(0, 0.02))) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(x = UNIT_LAB, y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 13),
        plot.margin = margin(14, 26, 12, 24))

dk_save(p3, "scope_emissions_top_origins_2022", w = 16, h = 11)

# ----------------------------------------------- 4. continent x industry group
d_cross <- read_csv(gold_path("scope_by_continent_and_industry_group.csv"),
                    show_col_types = FALSE) %>%
  mutate(scope = scope_factor(scope)) %>%
  filter(producing_world_region %in% c("Denmark", "Europe", "Asia and Pacific",
                                       "Middle East", "America", "Africa")) %>%
  group_by(producing_world_region) %>%
  group_modify(~ top_n_bucket(.x, "producing_sector_group", "value", n = 8)) %>%
  ungroup() %>%
  group_by(producing_world_region, producing_sector_group, scope) %>%
  summarise(value = sum(value), .groups = "drop") %>%
  mutate(producing_world_region =
           factor(producing_world_region,
                  levels = intersect(REGION_ORDER, unique(producing_world_region))),
         # per-facet ranking: a unique key per (group, panel), ordered by value
         key = paste0(producing_sector_group, "|||", producing_world_region))

key_ord <- d_cross %>% group_by(key) %>% summarise(v = sum(value), .groups = "drop") %>%
  arrange(v) %>% pull(key)

p4 <- ggplot(mutate(d_cross, key = factor(key, levels = key_ord)),
             aes(value, key, fill = scope)) +
  geom_col(width = 0.70, colour = "white", linewidth = 0.15,
           position = position_stack(reverse = TRUE)) +
  facet_ceiling(d_cross %>% group_by(producing_world_region, key) %>%
                  summarise(value = sum(value), .groups = "drop"),
                "producing_world_region", "value") +
  facet_wrap(~producing_world_region, scales = "free", ncol = 3, nrow = 2) +
  scale_y_discrete(labels = function(x) sub("\\|\\|\\|.*$", "", x)) +
  scale_fill_manual(values = SCOPE_COLS, breaks = SCOPE_ORDER, name = NULL) +
  scale_x_continuous(labels = smart_labs, breaks = scales::extended_breaks(n = 3),
                     guide = guide_axis(check.overlap = TRUE),
                     expand = expansion(mult = c(0, 0.02))) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(x = UNIT_LAB, y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 12))

dk_save(p4, "scope_emissions_continent_by_industry_2022", w = 20, h = 12.5)

cat("\nscope figures written to ", file.path(fig_dir), "\n", sep = "")
