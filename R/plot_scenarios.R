#!/usr/bin/env Rscript
# Scenario figures.
#
#   fig8  waterfall: how each lever moves the climate footprint from the 2022
#         baseline to a 2035 position, against the regional target
#   fig9  burden shifting: relative change in every impact category for every
#         lever, so a trade-off is visible rather than inferred
#
# A waterfall is the right form for fig8 because the quantity being explained is
# a single number decomposed into additive steps, and because the two facts that
# matter - that the levers are small, and that demand growth is larger than all
# of them - are the two things a waterfall shows without a caption. It carries
# an explicit interaction bar: the levers are solved simultaneously, so they do
# not sum, and hiding the difference would misrepresent the model.
#
# fig9 is a matrix rather than a grouped bar chart because the comparison the
# reader needs is per cell (does this lever make THIS pressure worse?), not per
# bar length, and because five categories x fourteen scenarios is too many bars
# to read. Donati et al. (2020) report relative change per pressure for the same
# reason.
#
# Run:  HC_ANALYSIS_YEAR=2022 Rscript R/plot_scenarios.R

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.R"))

YEAR <- Sys.getenv("HC_ANALYSIS_YEAR", "2022")

ms <- read_csv(gold_path("mitigation_scenarios.csv"), show_col_types = FALSE)
tc <- read_csv(gold_path("target_consistency.csv"), show_col_types = FALSE)
stopifnot(as.character(unique(ms$analysis_year))[[1]] == YEAR)

IND_NAME <- c(climate_change = "Climate\nchange",
              material_extraction = "Material\nextraction",
              blue_water_consumption = "Blue water\nconsumption",
              land_use = "Land\nuse",
              waste_generation = "Waste\ngeneration")
IND_ORDER <- names(IND_NAME)

tcv <- function(q) tc$value[tc$quantity == q][[1]]

# ============================ fig 8  waterfall ==============================
clim <- ms %>% filter(indicator == "climate_change")

# One row per lever, at its most ambitious modelled level. Ranked by size so
# the reader meets the levers that matter first.
# P7 is excluded: it is an alternative to P6 on the same devices, so the
# combined scenario contains one or the other, never both. Showing it as a step
# would make the waterfall stop adding up.
#
# The steps are read from scenario_selection.csv, which the engine writes with
# the exact levers C1 was built from. Re-deriving them here by slice_min(change)
# picked a different ambition level for any lever that worsens climate, so the
# bars were not the set inside the combined bar and the residual was not an
# interaction.
selection <- read_csv(gold_path("scenario_selection.csv"), show_col_types = FALSE)

levers <- clim %>%
  semi_join(selection, by = c("scenario_id", "ambition")) %>%
  mutate(label = sub("^P[0-9]+ ", "", scenario)) %>%
  arrange(change) %>%
  transmute(step = label, amount = change, kind = "Health-system lever")

interaction <- tcv("interaction, i.e. what summing would overstate")
grid_amt <- tcv("interventions with the grid pathway (C3)") -
  tcv("all interventions, solved simultaneously (C1)")
demand <- tcv("demand growth offset (business as usual)")
base_val <- tcv("baseline climate footprint")
required <- abs(tcv("required reduction for the regional target"))

steps <- bind_rows(
  tibble(step = "2022 baseline", amount = base_val, kind = "Level"),
  levers,
  tibble(step = "Overlap between levers\n(they are not additive)",
         amount = -interaction, kind = "Health-system lever"),
  tibble(step = "Grid and district heat\n(happens anyway)", amount = grid_amt,
         kind = "Background pathway"),
  tibble(step = "Health demand growth\nto 2035 (+18 %)", amount = demand,
         kind = "Working against us"),
  tibble(step = "2035 position", amount = NA_real_, kind = "Level"))

# Cumulative geometry. A waterfall is a segment from the running total before
# the step to the running total after it; the two "Level" rows are columns from
# zero.
steps <- steps %>%
  mutate(idx = row_number(),
         running = cumsum(replace_na(amount, 0)),
         start = if_else(kind == "Level", 0, lag(running, default = 0)),
         end = if_else(kind == "Level",
                       if_else(is.na(amount), lag(running, default = 0)[n()],
                               amount),
                       running))
steps$end[nrow(steps)] <- steps$running[nrow(steps) - 1]
steps <- steps %>%
  mutate(step = factor(step, levels = rev(step)),
         lab = if_else(kind == "Level",
                       sprintf("%s kt", formatC(round(end), format = "d",
                                                big.mark = ",")),
                       if_else(abs(amount) < 10,
                               sprintf("%+.1f kt", amount),
                               sprintf("%+.0f kt", amount))),
         lab_x = pmax(start, end))

target_level <- base_val - required

p8 <- ggplot(steps, aes(y = step)) +
  geom_segment(aes(x = start, xend = end, yend = step, colour = kind),
               linewidth = 9, lineend = "butt") +
  geom_vline(xintercept = target_level, linetype = "22", linewidth = 0.9,
             colour = "#1A1A1A") +
  annotate("text", x = target_level, y = nrow(steps) + 0.45, hjust = 1.03,
           vjust = 1, size = 4.6, fontface = "bold", colour = "#1A1A1A",
           label = sprintf("Regional target: %s kt",
                           formatC(round(target_level), format = "d",
                                   big.mark = ","))) +
  geom_text(aes(x = lab_x, label = lab), hjust = -0.15, size = 4.4,
            fontface = "bold", colour = INK) +
  scale_colour_manual(values = c(
    "Level" = "#1A1A1A",
    "Health-system lever" = "#0072B2",
    "Background pathway" = "#56B4E9",
    "Working against us" = "#D55E00"), name = NULL) +
  guides(colour = guide_legend(nrow = 1, override.aes = list(linewidth = 6))) +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(6),
                     expand = expansion(mult = c(0.01, 0.13))) +
  labs(x = expression("Climate footprint (kt CO"[2]*"-eq)"), y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 13.5, lineheight = 1.05,
                                   colour = INK))

dk_save(p8, sprintf("fig8_mitigation_waterfall_%s", YEAR), w = 16, h = 10)

# ======================== fig 9  burden shifting ============================
# Every scenario at its most ambitious level, every indicator, as relative
# change. Diverging fill so the sign is the first thing read.
# The same set as fig 8, plus the levers C1 excludes, because burden shifting is
# a property of every lever rather than only of the combined ones.
best <- clim %>%
  group_by(scenario_id) %>%
  slice_max(abs(change), n = 1, with_ties = FALSE) %>%
  ungroup() %>%
  select(scenario_id, ambition)

d9 <- ms %>%
  semi_join(best, by = c("scenario_id", "ambition")) %>%
  mutate(indicator = factor(indicator, levels = IND_ORDER,
                            labels = IND_NAME[IND_ORDER]),
         lever = sub("^[BPC][0-9]+ ", "", scenario),
         lever = paste0(scenario_id, "  ", lever),
         # Bottom-up items with no non-climate inventory: their zeros mean
         # "not resolved", not "no effect", and must not read as a clean bill.
         resolved = !(scenario_id %in% c("P6", "P7", "P8") &
                        indicator != IND_NAME[["climate_change"]]),
         shown = if_else(resolved, change_pct, NA_real_)) %>%
  group_by(scenario_id) %>%
  mutate(climate_neg = any(indicator == IND_NAME[["climate_change"]]
                           & change_pct < -1e-9)) %>%
  ungroup()

ord <- d9 %>% filter(indicator == IND_NAME[["climate_change"]]) %>%
  arrange(change_pct) %>% pull(lever)
d9 <- d9 %>% mutate(lever = factor(lever, levels = rev(ord)))

lim <- max(abs(d9$shown), na.rm = TRUE)

p9 <- ggplot(d9, aes(indicator, lever, fill = shown)) +
  geom_tile(colour = "white", linewidth = 1.1) +
  # Outline the cells where climate improves but this pressure worsens. The
  # diverging scale is set by a -13 % cell, so a +0.6 % cell is almost white:
  # the trade-off the figure exists to show would otherwise be invisible.
  geom_tile(data = ~ subset(.x, !is.na(shown) & shown > 1e-9 & climate_neg),
            fill = NA, colour = "#B2182B", linewidth = 1.4) +
  geom_text(aes(label = if_else(is.na(shown), "n.r.",
                                if_else(abs(shown) < 0.005, "\u2248 0",
                                        sprintf("%+.2f", shown))),
                colour = abs(shown) > 0.55 * lim),
            size = 4.2, fontface = "bold", na.rm = FALSE) +
  scale_fill_gradient2(low = "#1B7837", mid = "white", high = "#B2182B",
                       midpoint = 0, na.value = "grey92",
                       name = "Change in the impact category (%)",
                       limits = c(-lim, lim),
                       guide = guide_colourbar(barwidth = 16, barheight = 0.7,
                                               title.position = "top")) +
  scale_colour_manual(values = c(`TRUE` = "white", `FALSE` = "#1A1A1A"),
                      guide = "none", na.value = "#6B6B6B") +
  scale_x_discrete(position = "top", expand = expansion(0)) +
  scale_y_discrete(expand = expansion(0)) +
  labs(x = NULL, y = NULL) +
  theme_dkhc() +
  theme(panel.grid = element_blank(),
        axis.text.x.top = element_text(size = 14, lineheight = 1.05,
                                       colour = INK, face = "bold"),
        axis.text.y = element_text(size = 13, colour = INK),
        legend.position = "bottom",
        legend.title = element_text(size = 13, colour = INK))

dk_save(p9, sprintf("fig9_burden_shifting_%s", YEAR), w = 15, h = 10)

cat("\nscenario figures written to ", fig_dir, "\n", sep = "")
