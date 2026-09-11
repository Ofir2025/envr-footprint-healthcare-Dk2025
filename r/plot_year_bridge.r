#!/usr/bin/env Rscript
# fig10  the three-step bridge: 2016 before the shipping correction, 2016 after
#        it, and 2022 after it too - the same nine activity groups, three
#        times, so a reader can see how much of the 2019-to-2022 move is the
#        sea-transport reallocation and how much is the reference year.
#
# Figure-type reasoning, because the choice is the argument here.
#
# The 2019-to-2022 number this study reports moves two things at once: the
# Danish sea-transport reallocation and the reference year (background release
# IOT_2016 against IOT_2022, plus everything that changed for Danish demand in
# between). The single dumbbell this script drew before could not be honest
# about that split, because one segment was made to carry a change that is
# actually two, unrelated causes overlaid. The gold layer now carries the
# missing middle point - 2019, shipping-corrected - so the two moves can be
# drawn as two segments instead of guessed at in a caption. A single dumbbell
# no longer fits the data it would be asked to plot; it fit a two-point
# comparison and this is a three-point one.
#
# The form adopted: a connected, two-segment dot plot. One row per group,
# three markers on one shared value axis - open for 2019 uncorrected, mid grey
# for 2019 corrected, solid ink for 2022 corrected - joined by two coloured
# segments, blue for the correction step and vermillion for the year step.
# Everything stays in one panel on one shared scale, so the two segment
# lengths for a group sit directly beside each other and are compared by
# looking, not by holding one panel's scale in mind while reading another.
# Cleveland's rule still applies: a dot read against a common scale beats a
# bar length, and that does not change by adding a second segment.
#
# Rejected alternatives, and why:
#   two-panel dumbbell   one ordinary two-point dumbbell per step, side by
#                        side. Correct in principle, but it puts the
#                        comparison this figure exists to make - which step
#                        did most of the work, for this group - across a
#                        panel boundary, so the reader carries panel one's
#                        segment length in their head while reading panel
#                        two. The single-panel form gives that comparison for
#                        free, in the same row
#   paired slope graph   three x-positions (state) with one line per group.
#                        Rejected for the same reason a slope graph was
#                        rejected for the single-year version: it spends the
#                        horizontal axis on a categorical "which state"
#                        variable rather than the quantity of interest, and
#                        nine lines that change direction partway (heat and
#                        electricity falls in step 1, then rises in step 2)
#                        cross each other and are harder to rank by eye than
#                        nine rows of two dots
#   grouped bars          eighteen bars (nine groups x three states); the
#                        quantities of interest are the two step sizes, which
#                        are gaps between bars - the hardest thing to read
#                        off a chart of this kind, and now there are two gaps
#                        to read instead of one
#   waterfall             implies a sequence of steps toward a total; these
#                        nine groups do not sum to the total footprint change
#                        along one ordered path, and a waterfall was already
#                        rejected on this point for the single-year figure
#
# House rules followed. No title or caption on the image: everything a reader
# needs - which of the three markers is which, what each of the two connector
# colours means - is carried in the legend, so the figure survives with no
# note travelling alongside it at all. The axis is a LEVEL (kt CO2-eq); the
# two numbers printed against every row are CHANGES, not levels, so each
# carries a leading sign and the axis title says so explicitly, to keep the
# two readings from being confused with each other. Groups are ordered by the
# size of the total 2019-uncorrected-to-2022-corrected change, largest at the
# top, so transport and pharmaceuticals - between them nearly the whole story
# - are the first two rows a reader meets.
#
# Run:  DKHC_FIG_DIR=figures/manuscript Rscript r/plot_year_bridge.r

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.r"))

br <- read_csv(gold_path("year_comparison_two_step_bridge.csv"),
               show_col_types = FALSE)

# Four states, three steps. The chain used to start at 2019 because no 2016
# analysis existed; starting at 2016 moves the shipping correction onto the
# earliest year and leaves two clean reference-year steps on a configuration
# that does not otherwise change - same release, same correction state, same
# boundary, same capital treatment. The reader sees the correction once and
# growth twice, rather than the two confounded in one move.
STATE1 <- "2016, before shipping correction"
STATE2 <- "2016, after shipping correction"
STATE3 <- "2019, after shipping correction"
STATE4 <- "2022, after shipping correction"
STATE_ORDER <- c(STATE1, STATE2, STATE3, STATE4)
STATE_FILL  <- setNames(c("white", "grey72", "grey40", INK), STATE_ORDER)

STEP1 <- "Step 1: shipping correction, on 2016"
STEP2 <- "Step 2: reference year, 2016 to 2019"
STEP3 <- "Step 3: reference year, 2019 to 2022"
STEP_ORDER <- c(STEP1, STEP2, STEP3)
# All three hues already carry meaning elsewhere in this house palette
# (SCOPE_COLS, IND_COLS / REGION_COLS): reused here, not invented, Okabe-Ito.
STEP_COLS  <- setNames(c("#0072B2", "#009E73", "#D55E00"), STEP_ORDER)

#: A step below this moves too little to hold a label on its own segment.
LABEL_FLOOR_KT <- 20

# Largest total movers at the top: transport and pharmaceuticals are the
# whole story between them, and this puts them first.
d <- br %>%
  mutate(total_change = value_2022c - value_2016_uncorrected) %>%
  arrange(abs(total_change)) %>%
  mutate(group = factor(contribution_group, levels = contribution_group))

pts <- bind_rows(
  d %>% transmute(group, state = STATE1, value = value_2016_uncorrected),
  d %>% transmute(group, state = STATE2, value = value_2016c),
  d %>% transmute(group, state = STATE3, value = value_2019c),
  d %>% transmute(group, state = STATE4, value = value_2022c)
) %>% mutate(state = factor(state, levels = STATE_ORDER))

segs <- bind_rows(
  d %>% transmute(group, x = value_2016_uncorrected, xend = value_2016c,
                  step = STEP1, delta = delta_correction_kt),
  d %>% transmute(group, x = value_2016c, xend = value_2019c,
                  step = STEP2, delta = delta_2016_2019_kt),
  d %>% transmute(group, x = value_2019c, xend = value_2022c,
                  step = STEP3, delta = delta_2019_2022_kt)
) %>% mutate(step = factor(step, levels = STEP_ORDER))

# A signed whole number in the colour of its step is a change; a level would
# carry no sign. Zero prints as "0", never "+0" (house rule: no 0.0, no +0).
fmt_delta <- function(x) ifelse(abs(x) < 0.5, "0", sprintf("%+.0f", x))

# The step-1 label always sits at the step's own destination (the 2019
# shipping-corrected point) nudged above the row; the step-2 label always
# sits at ITS destination (the 2022 point) nudged below. That "always the
# arrival point, always the same side" rule is what makes the labels legible
# whichever direction a given step happens to move in (heat and electricity
# falls in step 1 and rises in step 2, so a rule tied to sign would flip
# sides mid-figure).
p <- ggplot() +
  geom_segment(data = segs, aes(x = x, xend = xend, y = group, yend = group,
                                colour = step),
               linewidth = 2.0, lineend = "round") +
  geom_point(data = pts, aes(x = value, y = group, fill = state),
             shape = 21, colour = INK, size = 5, stroke = 1.1) +
  # Step labels, at the midpoint of each segment. Two rules keep them legible,
  # and the first was learned by drawing it without them: consecutive midpoints
  # are NOT far enough apart when two steps are both short, and "+50" and "+9"
  # overprinted as "+5709".
  #
  # Steps 1 and 3 go above the row and step 2 below, so a short step 2 can never
  # sit on top of either. And a step is labelled only when it moves at least
  # LABEL_FLOOR_KT; below that the segment is too short to hold a number at any
  # offset, and the value is published in
  # 06_benchmarks_validation/year_comparison_two_step_bridge.csv, which the
  # folder readme points at.
  geom_text(data = segs %>% filter(step != STEP2, abs(delta) >= LABEL_FLOOR_KT),
            aes(x = (x + xend) / 2, y = group, label = fmt_delta(delta),
                colour = step),
            fontface = "bold", size = 3.8, nudge_y = 0.30,
            show.legend = FALSE) +
  geom_text(data = segs %>% filter(step == STEP2, abs(delta) >= LABEL_FLOOR_KT),
            aes(x = (x + xend) / 2, y = group, label = fmt_delta(delta),
                colour = step),
            fontface = "bold", size = 3.8, nudge_y = -0.30,
            show.legend = FALSE) +
  scale_colour_manual(values = STEP_COLS, name = NULL,
                      guide = guide_legend(order = 2, ncol = 1,
                                           override.aes = list(linewidth = 3))) +
  scale_fill_manual(values = STATE_FILL, name = NULL,
                    guide = guide_legend(order = 1, ncol = 1,
                                         override.aes = list(size = 5, colour = INK))) +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(6),
                     expand = expansion(mult = c(0.06, 0.1))) +
  scale_y_discrete(expand = expansion(add = 0.7)) +
  # Same unicode-subscript convention as IND_UNIT_TXT in
  # plot_manuscript_figures.r ("kt CO₂-eq"): a real subscript, typed
  # directly, since this axis title is a plain string rather than plotmath.
  # The axis title names the quantity and unit, nothing more: an explanation
  # of the labels is a note, and notes belong in the manuscript caption.
  labs(x = "Climate footprint (kt CO₂-eq)", y = NULL) +
  theme_dkhc() +
  theme(panel.grid.major.y = element_blank(),
        axis.text.y = element_text(size = 13.5, colour = INK),
        legend.box = "vertical",
        legend.spacing.y = grid::unit(0.15, "lines"))

dk_save(p, "fig10_year_bridge_climate_2016_2022", w = 16, h = 9.5,
        sub = "comparison")

cat(sprintf(
  paste0("\n2016 uncorrected %.0f kt -> 2016 corrected %.0f kt -> ",
         "2019 corrected %.0f kt -> 2022 corrected %.0f kt\n"),
  sum(d$value_2016_uncorrected), sum(d$value_2016c),
  sum(d$value_2019c), sum(d$value_2022c)))
cat(sprintf(
  "shipping correction %+.0f kt, 2016-2019 %+.0f kt, 2019-2022 %+.0f kt\n",
  sum(d$delta_correction_kt), sum(d$delta_2016_2019_kt),
  sum(d$delta_2019_2022_kt)))
cat("three-step year bridge figure written to ", fig_dir, "\n", sep = "")
