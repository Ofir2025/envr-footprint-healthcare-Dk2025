#!/usr/bin/env Rscript
# Appendix A, Fig. A.1: how Danish health care expenditure enters EXIOBASE, in the
# five steps the caption names. Drawn at the size it prints (6.69 in, Appendix A's
# text width), with every size a point size on paper.
#
# It replaces the co-author's diagram, a 1,340-pixel picture with no source that
# still said "Danish SUT categories", product code 06130 and "water use", and had no
# place for the distribution margins or the terms added outside the model. The
# boxes use the manuscript's own names; the three expenditure totals are read from
# the table of record, never typed.
#
# Run:  LANG=en_US.UTF-8 HC_ANALYSIS_YEAR=2022 HC_EXIOBASE_RELEASE=v3_8_2 \
#         HC_BACKGROUND_TAG=_snacship HC_SCOPE=health_eldercare HC_CAPITAL=excluded \
#         DKHC_FIG_DIR=figures/diagrams Rscript r/plot_integration_diagram.r

args <- commandArgs(FALSE)
here <- dirname(sub("--file=", "", grep("--file=", args, value = TRUE)[1]))
source(file.path(here, "_dk_common.r"))

PT_STEP <- 7.5; PT_BOX <- 6.5

t1 <- read.csv(gold_path("table_01.csv"), check.names = FALSE, row.names = 1)
meur <- function(row) formatC(round(t1[row, "Expenditure (MEUR)"]), format = "d", big.mark = ",")

# x centres: the three categories, with the distribution margins between the two
# goods in step (iii), so that no arrow crosses another or a box
X <- c(pharma = 32, marg = 51, appl = 70, serv = 89)
W <- 18
Y <- c(`1` = 11.0, `2` = 9.1, `3` = 7.0, `4` = 4.6, `5` = 2.0)

box <- function(x, y, label, w = W, h = 1.1, fill = "#EEF2F7") {
  data.frame(xmin = x - w / 2, xmax = x + w / 2, ymin = y - h / 2, ymax = y + h / 2,
             x = x, y = y, label = label, fill = fill)
}
H1 <- 1.5; H3 <- 1.5
RES <- seq(29.5, 91.5, length.out = 5)      # the five result boxes, evenly spaced
boxes <- rbind(
  box(X["pharma"], Y["1"], sprintf("Pharmaceutical and other\nmedical products (06112)\n%s million euros", meur("Pharmaceuticals and chemical products")), h = H1),
  box(X["appl"],   Y["1"], sprintf("Therapeutic appliances and\nassistive products (06134)\n%s million euros", meur("Medical appliances")), h = H1),
  box(X["serv"],   Y["1"], sprintf("Out-patient care, hospitals\nand retirement homes\n%s million euros", meur("Healthcare services")), h = H1),
  box(X["pharma"], Y["2"], "HC.51\nPharmaceuticals"),
  box(X["appl"],   Y["2"], "HC.52\nTherapeutic appliances"),
  box(X["serv"],   Y["2"], "HC.1 to HC.9, excluding\nHC.5: health care services"),
  box(X["pharma"], Y["3"], "Chemicals n.e.c.,\nby supplying region\n(the good)", h = H3),
  box(X["marg"],   Y["3"], "Danish motor-trade,\nwholesale and retail\n(distribution margins)", h = H3, fill = "#FBEFE3"),
  box(X["appl"],   Y["3"], "Medical, precision and\noptical instruments\n(the good)", h = H3),
  box(X["serv"],   Y["3"], "Health and social\nwork, its purchases\ncolumn", h = H3),
  box(45.5, Y["4"], "EXIOBASE version 3.8.2, Danish sea\ntransport reallocated: climate change,\nmaterial extraction, blue water\nconsumption, land use, waste generation",
      w = 45, h = 1.9, fill = "#E8F3E8"),
  box(83.5, Y["4"], "Added to the model result:\nthe sector's own emissions and\nwaste; anaesthetic gases, inhaler\npropellants, commuting, patient\nand visitor travel",
      w = 29, h = 1.9, fill = "#F2F2F2"),
  box(RES[1], Y["5"], "Activity\ngroup", w = 13, h = 1.2, fill = "#FFFFFF"),
  box(RES[2], Y["5"], "Producing\nsector", w = 13, h = 1.2, fill = "#FFFFFF"),
  box(RES[3], Y["5"], "Producing\nregion", w = 13, h = 1.2, fill = "#FFFFFF"),
  box(RES[4], Y["5"], "Region-by-\nindustry pair", w = 13, h = 1.2, fill = "#FFFFFF"),
  box(RES[5], Y["5"], "GHG Protocol\nscope", w = 13, h = 1.2, fill = "#FFFFFF")
)

steps <- data.frame(
  y = unname(Y),
  label = c("(i) Danish health\ncare expenditure,\n2022", "(ii) System of\nHealth Accounts\ncategories",
            "(iii) EXIOBASE\nsectors", "(iv) Environmental\nextensions and\nadded terms",
            "(v) Results\nreported by"))

seg <- function(x, y, xend, yend) data.frame(x = x, y = y, xend = xend, yend = yend)
top <- function(k, h = 1.1) Y[k] + h / 2
bot <- function(k, h = 1.1) Y[k] - h / 2
arrows <- rbind(
  seg(X["pharma"], bot("1", H1), X["pharma"], top("2")),
  seg(X["appl"],   bot("1", H1), X["appl"],   top("2")),
  seg(X["serv"],   bot("1", H1), X["serv"],   top("2")),
  seg(X["pharma"], bot("2"), X["pharma"], top("3", H3)),
  seg(X["pharma"] + 6, bot("2"), X["marg"] - 4, top("3", H3)),
  seg(X["appl"] - 6, bot("2"), X["marg"] + 4, top("3", H3)),
  seg(X["appl"],   bot("2"), X["appl"],   top("3", H3)),
  seg(X["serv"],   bot("2"), X["serv"],   top("3", H3)),
  seg(X["pharma"], bot("3", H3), X["pharma"], Y["4"] + 0.95),
  seg(X["marg"],   bot("3", H3), X["marg"],   Y["4"] + 0.95),
  seg(X["appl"],   bot("3", H3), 58, Y["4"] + 0.95),
  seg(X["serv"],   bot("3", H3), 65, Y["4"] + 0.95),
  data.frame(x = RES, y = Y["5"] + 1.05, xend = RES, yend = top("5", 1.2))
)
# both boxes of step (iv) feed one rule, and the rule feeds every result
rules <- rbind(seg(45.5, Y["4"] - 0.95, 45.5, Y["5"] + 1.05),
               seg(83.5, Y["4"] - 0.95, 83.5, Y["5"] + 1.05),
               seg(RES[1], Y["5"] + 1.05, RES[5], Y["5"] + 1.05))

p <- ggplot() +
  geom_segment(data = rules, aes(x = x, xend = xend, y = y, yend = yend),
               colour = "grey45", linewidth = 0.3) +
  geom_segment(data = arrows, aes(x = x, xend = xend, y = y, yend = yend),
               colour = "grey45", linewidth = 0.3,
               arrow = grid::arrow(length = grid::unit(3, "pt"), type = "closed")) +
  geom_rect(data = boxes, aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax, fill = fill),
            colour = "grey35", linewidth = 0.25) +
  geom_text(data = boxes, aes(x = x, y = y, label = label), size = PT_BOX / .pt,
            lineheight = 0.92, colour = "black") +
  geom_text(data = steps, aes(x = 0, y = y, label = label), hjust = 0, fontface = "bold",
            size = PT_STEP / .pt, lineheight = 0.92, colour = "black") +
  scale_fill_identity() +
  coord_cartesian(xlim = c(0, 98), ylim = c(1.25, 11.85), expand = FALSE, clip = "off") +
  theme_void() +
  theme(plot.margin = margin(3, 3, 3, 3))

dk_save(p, "demand_integration", w = 6.69, h = 4.0, dpi = 600)
