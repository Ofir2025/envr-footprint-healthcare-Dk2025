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
# "Private travel", the manuscript's term, for the gold table's "Individual travel"
d <- br %>%
  mutate(contribution_group = dplyr::recode(contribution_group,
                                            "Individual travel" = "Private travel"),
         total_change = value_2022c - value_2016_uncorrected) %>%
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
# A signed change, with a true minus sign and thousands separators, as the text
# writes numbers ("−1,727", "+657").
fmt_delta <- function(x) ifelse(abs(x) < 0.5, "0",
  paste0(ifelse(x > 0, "+", "\u2212"),
         formatC(abs(round(x)), format = "d", big.mark = ",")))

# Drawn at the size it prints, 6.69 in wide (Appendix A's text width), so the
# sizes below are points on paper. Until 2026-09-14 it was drawn 16 in wide and its
# 11 to 17 pt text printed at 4.5 to 7 pt. The two legend blocks take one row each,
# and the longest group names wrap onto a second line.
FIG_W <- 6.69; FIG_H <- 4.5
PT_LEGEND <- 7; PT_AXIS <- 7; PT_TICK <- 6.5; PT_LABEL <- 6

# The step-1 label always sits at the step's own destination (the 2019
# shipping-corrected point) nudged above the row; the step-2 label always
# sits at ITS destination (the 2022 point) nudged below. That "always the
# arrival point, always the same side" rule is what makes the labels legible
# whichever direction a given step happens to move in (heat and electricity
# falls in step 1 and rises in step 2, so a rule tied to sign would flip
# sides mid-figure).
#
# Steps 1 and 3 share the side above the row, so where both are short their
# midpoint labels met ("-171" and "-32" for Other). Labels on one side of a row
# are pushed apart until they clear each other, by their width in kt at print
# size: the panel is about 5.4 in wide, and a 6 pt bold digit about 0.045 in.
PANEL_W_IN <- 5.4
kt_per_in <- diff(range(pts$value)) * 1.16 / PANEL_W_IN
spread <- function(x, w, gap) {
  o <- order(x); x <- x[o]; w <- w[o]
  for (i in seq_along(x)[-1]) {
    need <- (w[i - 1] + w[i]) / 2 + gap - (x[i] - x[i - 1])
    if (need > 0) { x[i - 1] <- x[i - 1] - need / 2; x[i] <- x[i] + need / 2 }
  }
  x[order(o)]
}
step_labs <- segs %>%
  filter(abs(delta) >= LABEL_FLOOR_KT) %>%
  mutate(label = fmt_delta(delta), side = if_else(step == STEP2, -1, 1),
         x_lab = (x + xend) / 2, w = nchar(label) * 0.045 * kt_per_in) %>%
  group_by(group, side) %>%
  mutate(x_lab = spread(x_lab, w, gap = 0.05 * kt_per_in)) %>%
  ungroup()

p <- ggplot() +
  geom_segment(data = segs, aes(x = x, xend = xend, y = group, yend = group,
                                colour = step),
               linewidth = 0.9, lineend = "round") +
  geom_point(data = pts, aes(x = value, y = group, fill = state),
             shape = 21, colour = INK, size = 2.2, stroke = 0.45) +
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
  geom_text(data = step_labs,
            aes(x = x_lab, y = as.numeric(group) + 0.32 * side, label = label,
                colour = step),
            fontface = "bold", size = PT_LABEL / .pt, show.legend = FALSE) +
  scale_colour_manual(values = STEP_COLS, name = NULL,
                      guide = guide_legend(order = 2, nrow = 1,
                                           override.aes = list(linewidth = 1.2))) +
  scale_fill_manual(values = STATE_FILL, name = NULL,
                    guide = guide_legend(order = 1, nrow = 1,
                                         override.aes = list(size = 2.2, colour = INK),
                                         theme = theme(legend.key.width = grid::unit(8, "pt")))) +
  scale_x_continuous(labels = smart_labs, breaks = scales::breaks_extended(6),
                     expand = expansion(mult = c(0.06, 0.1))) +
  scale_y_discrete(expand = expansion(add = 0.7),
                   labels = function(x) vapply(x, function(s)
                     paste(strwrap(s, 24), collapse = "\n"), character(1))) +
  # Same unicode-subscript convention as IND_UNIT_TXT in
  # plot_manuscript_figures.r ("kt CO₂-eq"): a real subscript, typed
  # directly, since this axis title is a plain string rather than plotmath.
  # The axis title names the quantity and unit, nothing more: an explanation
  # of the labels is a note, and notes belong in the manuscript caption.
  labs(x = "Climate footprint (kt CO₂e)", y = NULL) +
  theme_minimal(base_size = PT_AXIS) +
  theme(text = element_text(colour = "black"),
        panel.grid.minor = element_blank(), panel.grid.major.y = element_blank(),
        panel.grid.major.x = element_line(colour = "#E6E6E6", linewidth = 0.25),
        axis.text.x = element_text(size = PT_TICK, colour = "black"),
        axis.text.y = element_text(size = PT_AXIS, colour = "black", lineheight = 0.9),
        axis.title.x = element_text(size = PT_AXIS, colour = "black", margin = margin(t = 4)),
        legend.position = "bottom", legend.title = element_blank(),
        legend.text = element_text(size = PT_LEGEND, colour = "black",
                                   margin = margin(l = 2, r = 4)),
        legend.key.height = grid::unit(8, "pt"), legend.key.width = grid::unit(12, "pt"),
        legend.key.spacing.x = grid::unit(4, "pt"),
        # centred on the whole sheet, not on the panel: under the panel the row
        # of four states ran off the right edge
        legend.box = "vertical", legend.location = "plot",
        legend.spacing.y = grid::unit(1, "pt"),
        legend.margin = margin(0, 0, 0, 0), legend.box.spacing = grid::unit(4, "pt"),
        plot.margin = margin(2, 4, 2, 2))

dk_save(p, "fig10_year_bridge_climate_2016_2022", w = FIG_W, h = FIG_H, dpi = 600,
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
