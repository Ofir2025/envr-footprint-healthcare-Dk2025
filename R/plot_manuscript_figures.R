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
# Plain-text units for axis labels that are not parsed as plotmath. Unicode
# rather than "CO2-eq" / "Mm3": the y labels of figure 3 are a factor, not an
# expression, so the sub- and superscripts have to be carried in the string.
IND_UNIT_TXT <- c(climate_change = "kt CO\u2082-eq", material_extraction = "kt",
                  blue_water_consumption = "Mm\u00b3", land_use = "km\u00b2",
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

# "Other" is figures 1 and 2's fallback -- the remaining EXIOBASE sectors the
# nine-group `agg_ind_fig` classification does not name, following Steenmeijer
# et al.'s own usage ("the remaining sectors combined in the group labelled
# other"). "Unallocated" is a DIFFERENT bucket, kept for figure 3 / figS1's
# geographical-origin panels, where it means the bottom-up rows that genuinely
# have no producing region (ISO3 "GLO") -- see the recode to a fuller label
# just before those panels are built, below.
GROUP_COLS <- c(
  "Pharmaceuticals and chemical products" = "#0072B2",
  "Pharmaceutical and chemical industry"  = "#0072B2",
  "Services" = "#009E73", "Transport" = "#E69F00",
  "Food and food services" = "#56B4E9", "Agricultural sector" = "#56B4E9",
  "Individual travel" = "#CC79A7",
  "Medical, electrical equipment and machinery" = "#D55E00",
  "Operational impacts" = "#8C564B",
  "Heat and electricity" = "#B8860B", "Electricity sector" = "#B8860B",
  "Fossil fuel industry" = "#7F7F7F", "Mining of minerals and metals" = "#B87333",
  "Other" = "grey80",
  "Denmark" = "#0072B2", "Europe" = "#009E73", "Asia and Pacific" = "#E69F00",
  "Middle East" = "#CC79A7", "America" = "#56B4E9", "Africa" = "#D55E00",
  "Unallocated" = "grey80", "No region: bottom-up items" = "grey80")

# Figure 3 / figS1's geographical-origin bucket for the bottom-up rows that
# have no producing region (ISO3 "GLO"): "Unallocated" is correct but says
# only that the group is unmapped, not what it is. Recoded here, at display
# time only -- the published gold CSVs keep "Unallocated", since this is a
# presentation label, not a data correction.
no_region_label <- function(x) {
  dplyr::recode(x, "Unallocated" = "No region: bottom-up items")
}

gold <- function(f) read_csv(gold_path(f), show_col_types = FALSE)
strip_key <- function(x) sub("\\|\\|\\|.*$", "", x)

# Order a per-panel key by its own value, so every panel ranks independently.
# Ranking on `value` is only valid inside one indicator: summing kt CO2-eq with
# Mm3 and km2 is meaningless and produced panels that were not descending.
# `share_pct` is unit-free and is the correct ranking variable wherever a key
# spans indicators.
order_key <- function(d, by = c("share_pct", "value")) {
  by <- match.arg(by)
  o <- d %>% group_by(key) %>%
    summarise(v = sum(.data[[by]]), .groups = "drop") %>% arrange(v)
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
  transmute(indicator, value, share_pct,
            group = no_region_label(producing_world_region),
            analysis = "C  Geographical origin")

d1 <- bind_rows(f1, f2, f3) %>%
  mutate(indicator = ind_factor(indicator),
         analysis = factor(analysis, levels = c("A  Activity contribution",
                                                "B  Sector contribution",
                                                "C  Geographical origin")),
         key = paste0(group, "|||", as.integer(analysis))) %>%
  order_key(by = "share_pct")

# Absolute values with the share printed on the bar: the magnitude is what a
# reader comparing health systems needs, and the share is what ranks the groups.
# Free x per panel because the five categories have different units.
p1 <- ggplot(d1, aes(value, key, fill = group)) +
  geom_col(width = 0.74, colour = "white", linewidth = 0.15) +
  geom_text(aes(label = if_else(share_pct >= 2, sprintf("%.0f%%", share_pct),
                                NA_character_)),
            hjust = -0.18, size = 4.0, fontface = "bold", colour = INK,
            na.rm = TRUE) +
  facet_ceiling(d1 %>% group_by(indicator, analysis, key) %>%
                  summarise(value = sum(value), .groups = "drop"),
                c("indicator", "analysis"), "value", room = 1.34) +
  facet_grid(analysis ~ indicator, scales = "free", space = "free_y",
             labeller = labeller(indicator = ind_only_labeller,
                                 analysis = label_value)) +
  scale_y_discrete(labels = strip_key) +
  scale_fill_manual(values = GROUP_COLS, guide = "none") +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                     guide = guide_axis(check.overlap = TRUE),
                     expand = expansion(mult = c(0, 0.05))) +
  labs(x = "Impact (absolute; bar labels give the share of the category)",
       y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 13.5),
        strip.text.y = element_text(size = 15, angle = 0, hjust = 0,
                                    margin = margin(l = 9)),
        strip.text.x = element_text(size = 17),
        panel.spacing.x = grid::unit(1.6, "lines"),
        plot.margin = margin(14, 26, 12, 14))

dk_save(p1, sprintf("fig1_ofir_panels_%s", YEAR), w = 23, h = 14.5)

# ================= fig 2  top producing region x industry pairs =============
d2 <- gold("figure2b_top_origin_industry_pairs.csv") %>%
  mutate(indicator = ind_factor(indicator),
         pair = if_else(producing_sector_code == "OTHER", REMAINDER_LAB,
                        paste0(region_code(producing_country_iso3), SEP,
                               producing_sector_code)),
         is_rest = producing_sector_code == "OTHER",
         key = paste0(pair, "|||", as.integer(indicator))) %>%
  order_key()

d2 <- prepare_remainder(d2)

p2 <- ggplot(d2, aes(plot_x, key,
                     fill = if_else(is_rest, "remainder", as.character(indicator)))) +
  geom_col(width = 0.74, colour = "white", linewidth = 0.15) +
  remainder_breaks(d2) +
  remainder_label(d2) +
  # Strips name the category only. They used to carry a total, but this figure
  # covers the MRIO supply chain alone (~84 % of each indicator), so printing a
  # total here understated the study figure by 16 %.
  facet_ceiling(d2 %>% group_by(indicator, key) %>%
                  summarise(value = sum(plot_x), .groups = "drop"),
                "indicator", "value", room = 1.28) +
  # Free x as well as y: a shared axis is set by the one panel whose leading
  # pair reaches 42 % and flattens the other four.
  facet_wrap(~indicator, ncol = 3, scales = "free",
             labeller = ind_only_labeller) +
  scale_y_discrete(labels = strip_key) +
  scale_fill_manual(values = c(IND_COLS, remainder = REMAINDER_COL),
                    guide = "none") +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                     expand = expansion(mult = c(0, 0.05))) +
  labs(x = paste0("Share of the impact category (%). ", REMAINDER_NOTE),
       y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 14, family = "mono", colour = INK),
        plot.margin = margin(14, 26, 12, 14))

dk_save(p2, sprintf("fig2_top_origin_industry_pairs_%s", YEAR), w = 21.5, h = 12.5)

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
  # Luminance-driven label colour: white on the amber Scope 3 fill is 2.25:1,
  # below the 4.5:1 floor; black on the same fill is 9.4:1.
  # `group = scope` is load-bearing. Without it the text layer's grouping comes
  # from its own `colour` aesthetic - two levels, not four - so position_stack
  # stacks the labels in a different order from the bars and the label of the
  # outside-protocol segment was drawn at 5 % instead of 97 %.
  geom_text(aes(label = if_else(share_pct >= 4, sprintf("%.0f%%", share_pct),
                                NA_character_),
                colour = scope %in% c("Scope 3"), group = scope),
            position = position_stack(vjust = 0.5, reverse = TRUE),
            fontface = "bold", size = 4.6, na.rm = TRUE, show.legend = FALSE) +
  scale_colour_manual(values = c(`TRUE` = "#1A1A1A", `FALSE` = "white"),
                      guide = "none") +
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

scope_source_plot <- function(which_scope, n = 10) {
  full <- pairs_src %>% filter(scope == which_scope) %>%
    group_by(indicator, pair) %>%
    summarise(value = sum(value), .groups = "drop") %>%
    group_by(indicator) %>%
    mutate(share_pct = 100 * value / sum(value)) %>% ungroup()
  keep <- full %>% group_by(indicator) %>%
    slice_max(value, n = n, with_ties = FALSE) %>% ungroup()
  # Pool the tail into one labelled bar, so the reader can see what the top n
  # actually covers rather than having to assume it is most of the category.
  rest <- full %>% anti_join(keep, by = c("indicator", "pair")) %>%
    group_by(indicator) %>%
    summarise(value = sum(value), share_pct = sum(share_pct),
              pair = REMAINDER_LAB, .groups = "drop")
  d <- bind_rows(keep, rest) %>%
    mutate(is_rest = pair == REMAINDER_LAB,
           key = paste0(pair, "|||", as.integer(indicator))) %>%
    order_key() %>%
    prepare_remainder()
  # Coloured by indicator, as in figure 2: the scope is fixed within the whole
  # figure and named in the axis title, so a fill legend saying so twice was
  # redundant, and one flat colour across five panels invited the reader to
  # compare bar lengths that are shares of five different denominators.
  ggplot(d, aes(plot_x, key,
                fill = if_else(is_rest, "remainder", as.character(indicator)))) +
    geom_col(width = 0.72, colour = "white", linewidth = 0.15) +
    remainder_breaks(d) +
    remainder_label(d, size = 4.4) +
    scale_fill_manual(values = c(IND_COLS, remainder = REMAINDER_COL),
                      guide = "none") +
    facet_ceiling(d %>% group_by(indicator, key) %>%
                    summarise(value = sum(plot_x), .groups = "drop"),
                  "indicator", "value", room = 1.26) +
    facet_wrap(~indicator, ncol = 3, scales = "free",
               labeller = ind_only_labeller) +
    scale_y_discrete(labels = strip_key) +
    scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                       guide = guide_axis(check.overlap = TRUE),
                       expand = expansion(mult = c(0, 0.05))) +
    # "Share of Scope 3 within the impact category" reads as the share Scope 3
    # is OF the category. The denominator here is the category's Scope 3 total.
    labs(x = sprintf("Share of the category's %s impact (%%). %s",
                     which_scope, REMAINDER_NOTE), y = NULL) +
    theme_dkhc() +
    theme(panel.grid.major.y = element_blank(),
          axis.text.y = element_text(size = 14, family = "mono", colour = INK),
          plot.margin = margin(14, 32, 12, 14))
}

dk_save(scope_source_plot("Scope 2"), sprintf("fig4_scope2_sources_%s", YEAR),
        w = 21.5, h = 12)
dk_save(scope_source_plot("Scope 3"), sprintf("fig5_scope3_sources_%s", YEAR),
        w = 21.5, h = 12)

# ============ fig 6  the same sources, stacked by scope, per pair ===========
d6 <- pairs_src %>%
  filter(scope %in% c("Scope 1", "Scope 2", "Scope 3")) %>%
  group_by(indicator, pair, scope) %>%
  summarise(value = sum(value), .groups = "drop")
top6 <- d6 %>% group_by(indicator, pair) %>%
  summarise(v = sum(value), .groups = "drop") %>%
  group_by(indicator) %>% slice_max(v, n = 10, with_ties = FALSE) %>% ungroup()
# Share must be computed against the WHOLE indicator, before the top-12 filter.
# Computing it after made every bar a share of the top 12 while the axis claimed
# a share of the category - DNK-HEAL climate was drawn at 14.3 % against a true
# 3.5 %.
d6_all <- d6 %>% group_by(indicator) %>%
  mutate(share_pct = 100 * value / sum(value)) %>% ungroup()
d6 <- d6_all %>% semi_join(top6, by = c("indicator", "pair")) %>%
  mutate(scope = factor(scope, levels = SCOPE_ORDER))
# Pool the tail so the reader can see what the shown pairs actually cover.
rest6 <- d6_all %>% anti_join(top6, by = c("indicator", "pair")) %>%
  group_by(indicator, scope) %>%
  summarise(value = sum(value), share_pct = sum(share_pct),
            pair = REMAINDER_LAB, .groups = "drop") %>%
  mutate(scope = factor(scope, levels = SCOPE_ORDER))
d6 <- bind_rows(d6, rest6) %>%
  mutate(is_rest = pair == REMAINDER_LAB,
         key = paste0(pair, "|||", as.integer(indicator))) %>%
  order_key() %>%
  prepare_remainder()

p6 <- ggplot(d6, aes(plot_x, key, fill = scope)) +
  geom_col(width = 0.72, colour = "white", linewidth = 0.15,
           position = position_stack(reverse = TRUE)) +
  remainder_breaks(d6) +
  remainder_label(d6, size = 4.4) +
  facet_ceiling(d6 %>% group_by(indicator, key) %>%
                  summarise(value = sum(plot_x), .groups = "drop"),
                "indicator", "value", room = 1.26) +
  facet_wrap(~indicator, ncol = 3, scales = "free",
             labeller = ind_only_labeller) +
  scale_y_discrete(labels = strip_key) +
  scale_fill_manual(values = SCOPE_COLS, name = NULL, drop = TRUE) +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(4),
                     guide = guide_axis(check.overlap = TRUE),
                     expand = expansion(mult = c(0, 0.05))) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(x = paste0("Share of the impact category (%). ", REMAINDER_NOTE),
       y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 14, family = "mono", colour = INK),
        plot.margin = margin(14, 32, 12, 14))

dk_save(p6, sprintf("fig6_scope_pairs_stacked_%s", YEAR), w = 21.5, h = 12)

# ===================== SI  geographical origin on its own ===================
dS <- gold("figure3_geographical_origin.csv") %>%
  mutate(indicator = ind_factor(indicator),
         producing_world_region = no_region_label(producing_world_region),
         key = paste0(producing_world_region, "|||", as.integer(indicator))) %>%
  order_key()

pS <- ggplot(dS, aes(share_pct, key, fill = producing_world_region)) +
  geom_col(width = 0.72, colour = "white", linewidth = 0.15) +
  facet_ceiling(dS %>% group_by(indicator, key) %>%
                  summarise(value = sum(share_pct), .groups = "drop"),
                "indicator", "value", room = 1.02) +
  facet_wrap(~indicator, ncol = 3, scales = "free",
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


# ============ fig 7  boundary-matched comparison with Schmidt & Merciai ======
# Reviewers and co-authors both asked the same question: why is this study's
# headline 4.7 Mt when Schmidt & Merciai (2023) report 6.1 Mt for the same
# country? The answer is not a discrepancy, it is two conventions, and the two
# steps that separate them are measurable. This figure carries them:
#
#   headline               health + eldercare, capital excluded
#   + childcare            NACE Q as they define it (HC_SCOPE=zorg_en_welzijn)
#   + capital endogenised  A' = A + K, Sodersten, Wood & Hertwich (2018)
#
# Only the last bar is comparable with the published value, and even then their
# model is consequential and ours attributional - stated on the figure so the
# agreement is not read as more than it is. Written only for the year the
# benchmark table exists for.
bm_path <- tryCatch(gold_path("danish_healthcare_benchmark_boundary_matched.csv"),
                    error = function(e) NA_character_)
bm <- if (is.na(bm_path)) NULL else read_csv(bm_path, show_col_types = FALSE)
# The benchmark table is not year-scoped, so `gold_path` resolves it for every
# variant. Draw the figure only for the (year, correction state) it was
# actually built for: the year alone is not enough since the 2x2 split
# introduced two folders per year (uncorrected and shipping-corrected) and the
# benchmark's own `model` column shows it is built on the shipping-corrected
# background - drawing it under `..._uncorrected` would mislabel corrected
# data as uncorrected, and a 2019 run would still silently republish the 2022
# comparison under a 2019 filename without the year check.
bm_is_corrected <- !is.null(bm) &&
  any(grepl("sea-transport reallocation", bm$model, fixed = TRUE))
this_run_is_corrected <- background_tag == "_snacship"
if (!is.null(bm) &&
    as.character(unique(bm$year[bm$basis != "Schmidt & Merciai 2023 (published comparator)"])) == YEAR &&
    bm_is_corrected == this_run_is_corrected) {
  d7 <- bm %>%
    filter(basis != "Schmidt & Merciai 2023 (published comparator)") %>%
    mutate(step = factor(basis,
                         levels = c("this study, headline",
                                    "this study, sector boundary matched",
                                    "this study, sector boundary AND capital matched"),
                         labels = c("Headline\nhealth + eldercare,\ncapital excluded",
                                    "+ childcare\nNACE Q sector boundary",
                                    "+ capital endogenised\nS\u00f6dersten et al. (2018)")),
           comparable = basis == "this study, sector boundary AND capital matched")
  published <- bm %>%
    filter(basis == "Schmidt & Merciai 2023 (published comparator)")
  ref <- published$value_kt[[1]]

  p7 <- ggplot(d7, aes(step, value_kt, fill = comparable)) +
    geom_col(width = 0.62, colour = "white", linewidth = 0.2) +
    geom_hline(yintercept = ref, linetype = "22", linewidth = 0.8,
               colour = "#1A1A1A") +
    annotate("text", x = 0.55, y = ref, hjust = 0, vjust = -0.7, size = 5,
             fontface = "bold", colour = "#1A1A1A",
             label = sprintf("Schmidt & Merciai (2023): %s kt",
                             formatC(ref, format = "d", big.mark = ","))) +
    geom_text(aes(label = sprintf("%s kt\n%.2f t per person",
                                  formatC(round(value_kt), format = "d",
                                          big.mark = ","), t_per_capita)),
              vjust = -0.35, size = 5, fontface = "bold", colour = INK,
              lineheight = 1.05) +
    scale_fill_manual(values = c(`FALSE` = "#9EC9E2", `TRUE` = "#0072B2"),
                      labels = c(`FALSE` = "Not comparable with the published value",
                                 `TRUE` = "Boundary and capital matched"),
                      name = NULL) +
    scale_y_continuous(labels = smart_labs, expand = expansion(mult = c(0, 0.20)),
                       breaks = scales::breaks_extended(5)) +
    guides(fill = guide_legend(nrow = 1)) +
    labs(x = NULL,
         y = expression("Climate change (kt CO"[2]*"-eq)")) +
    theme_dkhc() +
    theme(panel.grid.major.x = element_blank(),
          axis.text.x = element_text(size = 15, lineheight = 1.1, colour = INK))

  dk_save(p7, sprintf("fig7_boundary_matched_%s", YEAR), w = 13, h = 8.5)
}


# fig 8 is produced by R/plot_scenarios.R, not here.
#
# An earlier bar version of the mitigation figure lived at this point and
# wrote fig8_mitigation_scenarios_<year>. It was replaced by the waterfall in
# plot_scenarios.R, which shows the path from the baseline to the 2035 outcome
# rather than a set of independent bars, and the reasoning for that choice is
# in that script's header. Two producers writing two differently named figure
# eights is how a superseded figure returns, so the old block is removed rather
# than left guarded.

cat("\nmanuscript figures written to ", fig_dir, "\n", sep = "")
