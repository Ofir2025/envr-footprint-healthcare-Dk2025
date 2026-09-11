# Shared helpers for the Danish health-care footprint figures.
#
# Carries the same house conventions as the AFRIMINE R figures: no on-figure
# title or caption, facet/panel titles are the largest text, legend at the
# bottom with no title, bars ranked descending, TIFF output only, and number
# labels that never print 0.0 or 1e-09.
#
# Reads the gold CSV facts the Python pipeline writes, so R and Python report
# the same numbers by construction rather than by coincidence.

# ---- locale guard ------------------------------------------------------------
# The scripts carry CO₂, Mm³ and km² as UTF-8 literals. Under a C locale R
# decodes the source as raw bytes and the TIFF device prints "CO..": the
# figure is written with its subscripts silently lost. Refuse to draw instead.
if (!isTRUE(l10n_info()[["UTF-8"]])) {
  stop("Not a UTF-8 locale (LC_CTYPE = ", Sys.getlocale("LC_CTYPE"), "). ",
       "Run as  LANG=en_US.UTF-8 Rscript r/<script>.r  - in a C locale ",
       "CO\u2082, Mm\u00b3 and km\u00b2 render as '..' in every figure.",
       call. = FALSE)
}

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

# Results are held per model run, so the same basename can exist under more
# than one folder. Both variant-scoped layers - the Eriksen replication
# (.../01_eriksen_replication/2019_uncorrected/, .../2019_shipping_corrected/,
# .../2022_uncorrected/, .../2022_shipping_corrected/) and the scope
# decomposition (.../02_scopes_wood_hertwich/ with the same names) - vary by
# reference year AND by whether the Danish sea-transport correction was
# applied, since the 2019-to-2022 swing this study reports is never valid to
# read as a single change unless the correction state is held fixed.
#
# Resolution is therefore by the full variant folder (year AND background tag)
# and by nothing else. A bare-year fallback used to sit here for layers named
# by year alone; layer 02 was the only such layer, and while it existed that
# fallback resolved figures 3 to 6 of the uncorrected variants to the
# shipping-corrected scope tables without saying so. With the fallback gone, a
# variant a layer does not publish is an error naming that variant rather than
# a silent substitution.
analysis_year  <- Sys.getenv("HC_ANALYSIS_YEAR", "2022")
background_tag <- Sys.getenv("HC_BACKGROUND_TAG", "")

#: Self-describing "<year>_<state>" folder name for one (year, tag) pair.
#: Mirrors ``analysis.constants.variant_name`` so the two languages resolve the
#: same folder from the same environment.
variant_name <- function(year = analysis_year, tag = background_tag) {
  suffix <- if (tag == "") "uncorrected"
            else if (tag == "_snacship") "shipping_corrected"
            else sub("^_", "", tag)
  paste0(year, "_", suffix)
}

.gold_index <- NULL
.gold_hits <- function(name) {
  if (is.null(.gold_index)) {
    .gold_index <<- list.files(gold_root, pattern = "\\.csv(\\.gz)?$",
                               recursive = TRUE, full.names = TRUE)
  }
  .gold_index[basename(.gold_index) == name]
}

gold_path <- function(name, year = analysis_year, tag = background_tag) {
  hit <- .gold_hits(name)
  if (length(hit) < 1)
    stop(sprintf("gold fact '%s' not found under %s/", name, gold_root))
  if (length(hit) > 1) {
    variant <- variant_name(year, tag)
    invariant <- hit[grepl(sprintf("/%s/", variant), hit, fixed = TRUE)]
    if (length(invariant) == 1) return(invariant[[1]])
    if (length(invariant) < 1)
      stop(sprintf(paste0("gold fact '%s' is published for %d model runs but ",
                          "not for %s. The layer has not been built for that ",
                          "year and correction state; build it, or pass ",
                          "year=/tag= for one that exists."),
                   name, length(hit), variant))
    stop(sprintf(paste0("gold fact '%s' is ambiguous within variant %s ",
                        "(%d matches). Set HC_ANALYSIS_YEAR/HC_BACKGROUND_TAG ",
                        "or pass year=/tag=."),
                 name, variant, length(invariant)))
  }
  hit[[1]]
}

#: TRUE when `name` is published for this (year, tag), so a figure that a layer
#: has not been built for can be skipped out loud instead of aborting the whole
#: script. Used only by the scope figures, whose layer is variant-scoped and
#: may legitimately be missing one of the four runs.
gold_has <- function(name, year = analysis_year, tag = background_tag) {
  hit <- .gold_hits(name)
  if (length(hit) == 1) return(TRUE)
  length(hit[grepl(sprintf("/%s/", variant_name(year, tag)), hit,
                   fixed = TRUE)]) == 1
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

# Legend text for those keys. "Outside protocol" is the study's own term for a
# category the GHG Protocol has no scope for, and it appears in no published
# manuscript or appendix: a reader with the figure alone has no way to learn
# what is in it. The figures carry no title and no on-image note, by the house
# rule, so the legend is the only place the content can be said, and it says
# it. The term itself is kept, and defined, in replications.md section 02.
SCOPE_LABELS <- c(`Scope 1` = "Scope 1", `Scope 2` = "Scope 2",
                  `Scope 3` = "Scope 3",
                  `Outside protocol` = "Patient and visitor travel")

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

# Steenmeijer et al. (2022) figures 1-3 -- their own pastel palette, so the
# Danish panels can be set beside the Dutch ones without a colour shift.
#
# WHERE EACH HEX COMES FROM. The published figures are vector graphics, so the
# legend swatches are filled rectangles carrying an exact RGB fill. Each hex
# below was read out of the article PDF's drawing operators (never sampled from
# a raster, never guessed) and matched to its label by the swatch's own y
# position against the legend text baseline:
#
#   figure 1 and 2, p e954 (PDF page 6); figure 3, p e955 (PDF page 7)
#   swatch x = 463.4 (fig 1), 468.3 (fig 2), 416.8 (fig 3); each 6.9 x 4.3 pt
#
# Colour meaning is NOT shared between the three figures: #C8DFB3 is "Food and
# food services" in figure 1 and "Mining of minerals and metals" in figure 2.
# That is the article's own reuse, kept rather than harmonised, because the
# point of these panels is to sit beside the originals.
#
# The vector order IS the legend order the article prints, top to bottom, which
# is also the stacking order from the top of the bar down.
STEENMEIJER_COLS <- list(
  # p e954, swatch y = 187.1, 194.9, 210.9, 218.6, 226.4, 241.7, 249.5, 257.2
  fig1 = c(
    `Other (scope 3)`                                          = "#E1A5A0",
    `Individual travel (scope 3 and out-of-scope)`             = "#9EADD5",
    `Food and food services (scope 3)`                         = "#C8DFB3",
    `Services (scope 3)`                                       = "#9AD5E6",
    `Medical and electrical equipment and machinery (scope 3)` = "#FFEC96",
    `Operational impacts (scope 1)`                            = "#B2BBC1",
    `Heat and electricity (scope 2)`                           = "#FAB79C",
    `Pharmaceuticals and chemical products (scope 3)`          = "#D0C3E0"),
  # p e954, swatch y = 425.1, 432.9, 440.7, 448.5, 456.3, 464.1, 479.6
  fig2 = c(
    `Other`                                = "#9EADD5",
    `Mining of minerals and metals`        = "#C8DFB3",
    `Operational (direct) impacts`         = "#65449B",
    `Agricultural sector`                  = "#FFEC96",
    `Fossil fuel industry`                 = "#B2BBC1",
    `Pharmaceutical and chemical industry` = "#FAB79C",
    `Electricity sector`                   = "#D0C3E0"),
  # p e955, swatch y = 217.1, 224.9, 232.8, 240.6, 256.4, 264.3. The last two
  # entries are the study's home country and "Europe excluding it", so the
  # Danish panels keep these two colours and relabel them.
  fig3 = c(
    Africa                               = "#C8DFB3",
    Americas                             = "#9AD5E6",
    `Middle East`                        = "#FFEC96",
    `Europe (excluding the Netherlands)` = "#B2BBC1",
    `Asia-Pacific`                       = "#FAB79C",
    Netherlands                          = "#D0C3E0")
)

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
