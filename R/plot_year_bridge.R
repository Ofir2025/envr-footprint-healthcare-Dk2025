#!/usr/bin/env Rscript
# fig10  the 2019 and 2022 climate footprints, group by group.
#
# Figure-type reasoning, because the choice is the argument here.
#
# The question the figure answers is "the same nine activity groups, measured
# twice: which moved, in which direction, and by how much?" That is a paired
# comparison over categories, and the form that shows a pair per category
# without asking the reader to difference two bar lengths by eye is the
# connected dot plot. Cleveland's rule applies (a dot on a common scale is read
# more accurately than a bar length), and the paired form makes the direction of
# each change a property of the line rather than something to be inferred.
#
# Rejected alternatives, and why:
#   grouped bars      two bars per group, eighteen bars, and the quantity of
#                     interest (the change) is the gap between them, which is
#                     the hardest thing to read off a bar chart
#   waterfall         already used for the scenario decomposition, and it shows
#                     a path to a total rather than a paired measurement; it
#                     would also imply the groups are steps in a sequence
#   slope graph       works for two points per category but wastes the
#                     horizontal axis on an ordinal year variable
#   stacked bars      composition, not comparison; the two years do not sum
#
# The house figure library carries dumbbells as an exemplar type and this is the
# canonical use for it. The Economist convention is followed: light dot for the
# earlier year, solid dot for the later one, connector coloured by direction.
#
# Run:  Rscript R/plot_year_bridge.R

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.R"))

br <- read_csv(gold_path("year_comparison_climate_bridge.csv"),
               show_col_types = FALSE)
tot <- read_csv(gold_path("year_comparison_2019_2022.csv"),
                show_col_types = FALSE)

t2019 <- tot$value_2019[tot$indicator == "climate_change"][[1]]
t2022 <- tot$value_2022[tot$indicator == "climate_change"][[1]]

# Largest movers at the top: the reader should meet transport and
# pharmaceuticals first, because between them they are the whole story.
d <- br %>%
  mutate(group = contribution_group,
         direction = if_else(delta_kt < 0, "Lower in 2022", "Higher in 2022"),
         lab = sprintf("%+.0f", delta_kt)) %>%
  arrange(abs(delta_kt)) %>%
  mutate(group = factor(group, levels = group))

DIR <- c("Lower in 2022" = "#0072B2", "Higher in 2022" = "#D55E00")

# Two point layers rather than one with a shape scale: an open marker needs a
# white FILL and a coloured BORDER, which a single layer cannot give while also
# mapping fill to direction. The first render lost the 2019 marker entirely.
p <- ggplot(d) +
  geom_segment(aes(y = group, yend = group, x = value_2019, xend = value_2022,
                   colour = direction), linewidth = 2.1, lineend = "round") +
  geom_point(aes(value_2019, group, colour = direction), shape = 21,
             fill = "white", size = 5, stroke = 1.8) +
  geom_point(aes(value_2022, group, colour = direction, fill = direction),
             shape = 21, size = 5, stroke = 1.2) +
  geom_text(aes(x = pmax(value_2019, value_2022), y = group, label = lab,
                colour = direction),
            hjust = -0.42, size = 4.4, fontface = "bold", show.legend = FALSE) +
  scale_colour_manual(values = DIR, name = NULL) +
  scale_fill_manual(values = DIR, guide = "none") +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(6),
                     expand = expansion(mult = c(0.04, 0.14))) +
  labs(x = expression("Climate footprint (kt CO"[2]*"-eq)"), y = NULL,
       caption = paste0(
         "Open marker 2019, solid marker 2022; the number is the change.\n",
         "The two runs differ in three ways at once: reference year, ",
         "background vintage (IOT_2016 against IOT_2022), and whether the\n",
         "Danish sea-transport reallocation is applied (2022 only). ",
         "The difference is a bridge between two model versions, not a time series.")) +
  theme_dkhc() +
  theme(plot.caption = element_text(size = 12, hjust = 0, colour = INK,
                                    margin = margin(t = 10))) +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 13.5, colour = INK))

dk_save(p, "fig10_year_bridge_climate_2019_2022", w = 15, h = 9)

cat(sprintf("\n2019 total %.0f kt, 2022 total %.0f kt, difference %+.0f kt\n",
            t2019, t2022, t2022 - t2019))
cat("year bridge figure written to ", fig_dir, "\n", sep = "")
