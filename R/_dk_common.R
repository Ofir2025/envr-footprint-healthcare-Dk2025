# Shared helpers for the Danish health-care footprint figures.
#
# Carries the same house conventions as the AFRIMINE R figures: no on-figure
# title or caption, facet/panel titles are the largest text, legend at the
# bottom with no title, bars ranked descending, TIFF output only, and number
# labels that never print 0.0 or 1e-09.
#
# Reads the gold CSV facts the Python pipeline writes, so R and Python report
# the same numbers by construction rather than by coincidence.

suppressPackageStartupMessages({
  library(readr); library(dplyr); library(tidyr); library(ggplot2)
  library(scales); library(forcats)

  # Headless runs: open a null device so ggplot never writes Rplots.pdf into
  # the working directory (the default device opens on the first print).
  if (!interactive()) pdf(NULL)
})

# ---- roots -----------------------------------------------------------------
gold_root <- Sys.getenv("DKHC_GOLD_ROOT", "data/gold/results")
fig_dir   <- Sys.getenv("DKHC_FIG_DIR",   "figures")

# Results are held per analysis year, so the same basename exists under
# .../01_eriksen_replication/2019/ and .../2022/. Resolve to the configured year
# first and only fall back to a unique match, so a figure can never silently
# take the wrong year's data.
analysis_year <- Sys.getenv("HC_ANALYSIS_YEAR", "2022")

.gold_index <- NULL
gold_path <- function(name, year = analysis_year) {
  if (is.null(.gold_index)) {
    .gold_index <<- list.files(gold_root, pattern = "\\.csv(\\.gz)?$",
                               recursive = TRUE, full.names = TRUE)
  }
  hit <- .gold_index[basename(.gold_index) == name]
  if (length(hit) < 1)
    stop(sprintf("gold fact '%s' not found under %s/", name, gold_root))
  if (length(hit) > 1) {
    inyear <- hit[grepl(sprintf("/%s/", year), hit, fixed = TRUE)]
    if (length(inyear) == 1) return(inyear[[1]])
    stop(sprintf(paste0("gold fact '%s' is ambiguous for year %s (%d matches). ",
                        "Set HC_ANALYSIS_YEAR or pass year=."),
                 name, year, length(hit)))
  }
  hit[[1]]
}

# ---- type sizes ------------------------------------------------------------
# Size RANKING is deliberate and must always hold:
#   facet/panel title > legend text > axis title > axis tick text.
# Calibrated for the 16-18in canvases used here; the hard floor is 8pt.
FS_STRIP   <- 20
FS_LEGEND  <- 17
FS_AXTITLE <- 16
FS_AXIS    <- 15
INK        <- "#1A1A1A"   # near-black; grey15 read as faint at page scale
MM_PER_PT  <- 1 / 2.845   # geom_text(size=) is mm, not pt

# ---- palettes --------------------------------------------------------------
# GHG-Protocol scopes. Okabe-Ito hues, colourblind-safe, one hue per key.
SCOPE_ORDER <- c("Scope 1", "Scope 2", "Scope 3", "Outside protocol")
SCOPE_COLS  <- c(`Scope 1` = "#0072B2", `Scope 2` = "#009E73",
                 `Scope 3` = "#E69F00", `Outside protocol` = "#4D4D4D")

# World regions as the study aggregates them. Denmark is singled out because
# the domestic/imported split is the paper's subject; the remainder bucket is
# the house grey.
REGION_ORDER <- c("Denmark", "Europe", "Asia and Pacific", "Middle East",
                  "America", "Africa", "Unallocated")
REGION_COLS  <- c(Denmark = "#0072B2", Europe = "#009E73",
                  `Asia and Pacific` = "#E69F00", `Middle East` = "#CC79A7",
                  America = "#56B4E9", Africa = "#D55E00",
                  Unallocated = "grey70")

REMAINDER_LAB <- "Remaining regions and sector pairs"
REMAINDER_COL <- "grey78"

# One hue per impact category, so a faceted sheet is not five identical blue
# panels. Semantically ordered (warming red, materials brown, water blue, land
# green, waste purple) and drawn from the Okabe-Ito safe set where possible.
IND_COLS <- c(climate_change = "#D55E00", material_extraction = "#8C564B",
              blue_water_consumption = "#0072B2", land_use = "#009E73",
              waste_generation = "#7B3294")

# ---- label hygiene ---------------------------------------------------------
# ASCII only: the TIFF device's font has no middle dot, en dash or curly quote,
# and renders them as "..". Composite EXIOBASE names are shortened by an
# explicit whitelist rather than truncated, so the shortening is auditable.
SEP <- " - "

# EXIOBASE's five rest-of-world regions carry names, not ISO3 codes. On an axis
# of codes they need a code too, so they get the conventional RoW abbreviations.
ROW_CODE <- c(`RoW Asia and Pacific` = "RoW AP", `RoW America` = "RoW AM",
              `RoW Europe` = "RoW EU", `RoW Africa` = "RoW AF",
              `RoW Middle East` = "RoW ME")

region_code <- function(x) unname(ifelse(x %in% names(ROW_CODE), ROW_CODE[x], x))

clean_sector_label <- function(x) {
  x <- sub("^Extraction of crude petroleum and services related to crude oil extraction.*$",
           "Crude petroleum extraction", x)
  x <- sub("^Extraction of natural gas and services related to natural gas extraction.*$",
           "Natural gas extraction", x)
  x <- sub("^Retail trade, except of motor vehicles and motorcycles.*$",
           "Retail trade", x)
  x <- sub("^Wholesale trade and commission trade, except of motor vehicles.*$",
           "Wholesale trade", x)
  x <- sub("^Manufacture of gas; distribution of gaseous fuels through mains$",
           "Gas manufacture and distribution", x)
  x <- sub("^Supporting and auxiliary transport activities.*$",
           "Auxiliary transport activities", x)
  x <- gsub("\\s*\\(\\d+\\)$", "", x)   # trailing EXIOBASE index, e.g. "(52)"
  trimws(x)
}

# ---- number formatting -----------------------------------------------------
# Whole numbers print whole with comma separators; non-whole get 3 significant
# figures; zero is always exactly "0", never 0.0 or 0e+00.
smart_labs <- function(x) {
  out <- vapply(x, function(v) {
    if (is.na(v)) return(NA_character_)
    if (abs(v - round(v)) < .Machine$double.eps^0.5) {
      formatC(round(v), format = "f", digits = 0, big.mark = ",")
    } else {
      trimws(formatC(v, format = "fg", digits = 3, big.mark = ",",
                     drop0trailing = TRUE))
    }
  }, character(1))
  out[!is.na(x) & x == 0] <- "0"
  out
}

# ---- theme -----------------------------------------------------------------
theme_dkhc <- function() {
  theme_minimal(base_size = 11) +
    theme(
      plot.title = element_blank(),          # titles live in the caption, never on the sheet
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(colour = "#eeeeee", linewidth = 0.3),
      strip.text = element_text(face = "bold", hjust = 0.5, size = FS_STRIP,
                                colour = INK, margin = margin(b = 9)),
      strip.clip = "off",
      axis.title.x = element_text(size = FS_AXTITLE, colour = INK,
                                  margin = margin(t = 10)),
      axis.title.y = element_text(size = FS_AXTITLE, colour = INK),
      axis.text = element_text(size = FS_AXIS, colour = INK),
      legend.position = "bottom",
      legend.title = element_blank(),
      legend.text = element_text(size = FS_LEGEND, colour = INK),
      legend.key.width  = grid::unit(1.9, "lines"),
      legend.key.height = grid::unit(1.1, "lines"),
      legend.spacing.x  = grid::unit(0.6, "lines"),
      panel.spacing.x = grid::unit(2.4, "lines"),
      panel.spacing.y = grid::unit(1.6, "lines"),
      plot.margin = margin(14, 26, 12, 14)   # right pad so edge ticks aren't clipped
    )
}

# Axis ceiling: a pretty tick AT OR ABOVE the data max, so the longest bar sits
# under a labelled tick. 4% headroom, then round up to 2 significant figures.
nice_ceiling <- function(x) {
  x <- suppressWarnings(max(x, na.rm = TRUE))
  if (!is.finite(x) || x <= 0) return(1)
  pad <- x * 1.04
  mag <- 10 ^ (floor(log10(pad)) - 1)
  ceiling(pad / mag) * mag
}

# Per-facet axis headroom. A free-scale facet trains its range on the data, so
# the longest bar can touch the panel edge with no labelled tick above it.
# Extending the range with an invisible point is the only reliable fix: a
# breaks= function chooses which ticks are LABELLED, not where the panel ends.
facet_ceiling <- function(data, group, extent, room = 1.06) {
  ceil <- data %>%
    group_by(across(all_of(group))) %>%
    summarise(.ceiling = nice_ceiling(max(.data[[extent]], na.rm = TRUE) * room),
              .groups = "drop")
  geom_blank(data = ceil, mapping = aes(x = .ceiling), inherit.aes = FALSE)
}

# ---- the remainder bar -------------------------------------------------------
# House rule: a top-N ranking must always show what it leaves out. The awkward
# part is that in a 200 x 200 MRIO the tail is routinely several times the
# largest ranked bar, so a to-scale remainder flattens the ranking it is meant
# to qualify into slivers.
#
# The convention adopted across this study: pin the remainder to the FOOT of
# every panel, draw it to scale wherever it fits, and where it does not, break
# the bar and print its true share beside it. Nothing is hidden - the remainder
# is present, labelled, and the one bar carrying break marks - and the axis
# title says so. `REMAINDER_NOTE` is that sentence.
#
# The three functions below expect `d` to carry `indicator`, `key` (a factor
# built by the caller's ranking), `share_pct` and `is_rest`. Stacked figures are
# handled too: every segment of a truncated remainder is scaled by the same
# factor, so the composition of the bar survives the break.
REMAINDER_NOTE <- paste(
  "The remainder sits at the foot of each panel; where it exceeds the ranked",
  "bars its own bar is broken and its true share printed.")

prepare_remainder <- function(d, room = 1.04) {
  lv <- levels(d$key)
  rest <- unique(as.character(d$key[d$is_rest]))
  d <- d %>% mutate(key = factor(key, levels = c(lv[lv %in% rest],
                                                 lv[!lv %in% rest])))
  cap <- d %>% filter(!is_rest) %>%
    group_by(indicator, key) %>%
    summarise(.t = sum(share_pct), .groups = "drop_last") %>%
    summarise(cap = max(.t), .groups = "drop")
  tot <- d %>% filter(is_rest) %>%
    group_by(indicator) %>%
    summarise(rest_total = sum(share_pct), .groups = "drop")
  d %>% left_join(cap, by = "indicator") %>%
    left_join(tot, by = "indicator") %>%
    mutate(trunc = is_rest & rest_total > cap,
           plot_x = if_else(trunc, share_pct * cap * room / rest_total,
                            share_pct))
}

# One label per remainder bar, at its drawn end, carrying the TRUE share.
remainder_label <- function(d, size = 4.6, hjust = -0.22) {
  lab <- d %>% filter(is_rest) %>%
    group_by(indicator, key) %>%
    summarise(x = sum(plot_x), lab = sprintf("%.0f%%", sum(share_pct)),
              .groups = "drop")
  geom_text(data = lab, inherit.aes = FALSE,
            aes(x = x, y = key, label = lab), hjust = hjust, size = size,
            fontface = "bold", colour = INK)
}

# Break marks. The remainder is level 1 of every panel after prepare_remainder,
# so the row index is constant and needs no per-panel lookup.
remainder_breaks <- function(d, linewidth = 0.9) {
  b <- d %>% filter(trunc) %>% distinct(indicator, cap) %>%
    tidyr::crossing(off = c(0.90, 0.96))
  if (nrow(b) == 0) return(NULL)
  geom_segment(data = b, inherit.aes = FALSE,
               aes(x = cap * off, xend = cap * (off + 0.035),
                   y = 1 - 0.34, yend = 1 + 0.34),
               colour = "white", linewidth = linewidth)
}

# ---- top-N with a re-sorted remainder --------------------------------------
# House rule: bucket the long tail into ONE bar, and re-sort that bucket into
# the ranking by its own value -- never append it last.
top_n_bucket <- function(d, key, value, n = 20, label = REMAINDER_LAB) {
  ranked <- d %>%
    group_by(.data[[key]]) %>%
    summarise(.v = sum(.data[[value]]), .groups = "drop") %>%
    arrange(desc(.v))
  keep <- head(ranked[[key]], n)
  d %>%
    mutate(!!key := if_else(.data[[key]] %in% keep, .data[[key]], label))
}

# ---- saver -----------------------------------------------------------------
# TIFF only, LZW, white background. Notes belong in the manuscript caption,
# never on the image.
dk_save <- function(p, name, w = 16, h = 10, dpi = 300, sub = ".") {
  d <- file.path(fig_dir, sub)
  dir.create(d, recursive = TRUE, showWarnings = FALSE)
  f <- file.path(d, paste0(name, ".tiff"))
  # ragg's TIFF device where it is installed: the base grDevices tiff device on
  # macOS drops non-ASCII glyphs silently - "Sodersten" came out as "S..dersten"
  # - and there is no warning to catch it. ragg shapes UTF-8 correctly.
  if (requireNamespace("ragg", quietly = TRUE)) {
    ggsave(f, p, width = w, height = h, units = "in", dpi = dpi,
           device = ragg::agg_tiff, compression = "lzw", bg = "white")
  } else {
    ggsave(f, p, width = w, height = h, units = "in", dpi = dpi,
           compression = "lzw", bg = "white")
  }
  cat(sprintf("  %-52s %.1f x %.1f in (aspect %.2f)\n", f, w, h, w / h))
  invisible(f)
}
