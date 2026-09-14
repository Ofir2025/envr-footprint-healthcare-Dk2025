# -*- coding: utf-8 -*-
"""Figures for the uncertainty section (see analysis.uncertainty_2025).

1. distribution of each indicator total, normalised to its deterministic value
   (one panel, all five indicators, so relative spread and skew are comparable);
2. first-order variance shares per indicator (exact for this additive model);
3. 95 % interval of each contribution group of the climate footprint;
4. tornado for climate change, with the percentile-based swings and the
   reviewers' verbatim +/-20 % and +/-50 % swings in separate blocks;
5. contribution-group ranking probabilities.

Every figure is drawn at the width it prints in Appendix A, 6.69 in (an A4 page
with 2 cm margins), so each point size in this module is the size on paper.
Appendix A is published exactly as received; drawn 8.4 to 10.5 in wide with 9 to
13 pt text, these figures printed their text at 6 to 8 pt and their annotations
lower (fixed 2026-09-14).

Run: HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship PYTHONPATH=src \
     .venv/bin/python -m analysis.uncertainty_figures
"""

from __future__ import annotations

import os
from collections.abc import Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.text
import numpy as np
import pandas as pd

from paths import PROJECT_ROOT
from analysis.uncertainty_2025 import (INDICATORS, PARAMS, load_groups, run_mc,
                                       sobol_first_order, ranking_probabilities)

#: Display names: the manuscript's "Private travel" for the model's "Individual travel".
DISPLAY = {"Individual travel": "Private travel"}
#: Line breaks for the two longest group names, which otherwise set the width
#: every heat-map column and interval bar loses. The words are unchanged.
WRAP = {"Medical, electrical equipment and machinery":
            "Medical, electrical equipment\nand machinery",
        "Pharmaceuticals and chemical products":
            "Pharmaceuticals and\nchemical products"}
SHORT = {"Global warming (ktCO2eq)": "Climate change", "Material extraction (kt)": "Material extraction",
         "Blue water consumption (Mm3)": "Blue water consumption", "Land use (km2)": "Land use",
         "Waste generation (kt)": "Waste generation"}

# Okabe-Ito, colour-vision-deficiency safe; unique hue per key
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442"]
# full names, never the internal row codes
PARAM_LABEL = {"mrio": "Input-output parameters", "B_HEAL": "Operational term",
               "B_ANAE": "Anaesthetic gases", "B_PMDI": "Inhaler propellants",
               "B_COMM": "Employee commuting", "B_VISI": "Patient and visitor travel",
               "covariance_commute_visitor":
                   "Covariance of the two travel terms"}

#: Printed width of every figure in Appendix A (A4, 2 cm margins), inches.
PRINT_W = 6.69
#: Tallest figure the page leaves room for, with its caption, inches.
MAX_H = 8.3
#: Raster resolution at the printed size (Elsevier: >= 500 dpi for text art).
DPI = 600
# Point sizes on paper, strictly ranked: panel titles > legend > axis labels
# and tick labels > in-plot annotations.
TITLE_PT, LEGEND_PT, LABEL_PT, TICK_PT, ANNOT_PT = 8.5, 7.5, 7.0, 7.0, 6.0

plt.rcParams.update({
    "font.size": LABEL_PT, "axes.titlesize": TITLE_PT, "legend.fontsize": LEGEND_PT,
    "axes.labelsize": LABEL_PT, "xtick.labelsize": TICK_PT, "ytick.labelsize": TICK_PT,
    # text is black, never grey
    "text.color": "black", "axes.labelcolor": "black", "axes.edgecolor": "black",
    "xtick.color": "black", "ytick.color": "black", "axes.titlecolor": "black",
    # rules and ticks in proportion to 7 pt text
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "xtick.major.pad": 2.0, "ytick.major.pad": 2.0,
    "axes.titlepad": 4.0, "axes.labelpad": 3.0,
    "legend.frameon": False, "legend.handlelength": 1.6, "legend.handletextpad": 0.5,
    "legend.columnspacing": 1.4, "legend.borderaxespad": 0.2,
    # CO$_2$ set in the text face rather than in a separate math italic
    "mathtext.default": "regular",
    "figure.dpi": 100, "savefig.dpi": DPI,
})


def _group_label(name: str) -> str:
    """Return the printed name of a contribution group.

    Parameters
    ----------
    name : str
        Contribution-group name as the model writes it.

    Returns
    -------
    str
        The manuscript's name for the group, broken over two lines when it is
        one of the two longest.
    """
    shown = DISPLAY.get(name, name)
    return WRAP.get(shown, shown)


def _figure(height: float, **subplot_kw) -> tuple[plt.Figure, np.ndarray | plt.Axes]:
    """Open a figure at the printed width with constrained layout.

    Parameters
    ----------
    height : float
        Figure height, inches; at most :data:`MAX_H`.
    **subplot_kw
        Passed to :func:`matplotlib.pyplot.subplots` (``ncols``, ``sharey``).

    Returns
    -------
    tuple of matplotlib.figure.Figure and Axes or numpy.ndarray of Axes
        The figure and its axes.

    Raises
    ------
    ValueError
        If ``height`` exceeds :data:`MAX_H`.
    """
    if height > MAX_H:
        raise ValueError(f"figure height {height} in exceeds the {MAX_H} in the page allows")
    fig, ax = plt.subplots(figsize=(PRINT_W, height), layout="constrained", **subplot_kw)
    fig.get_layout_engine().set(w_pad=2 / 72, h_pad=2 / 72, wspace=0.02, hspace=0.02)
    return fig, ax


def _save(fig: plt.Figure, path: str) -> None:
    """Write a figure at its printed size and close it.

    No tight bounding box: it would crop the canvas and change the printed
    width, so the layout engine fits the content inside the canvas instead,
    and the check below fails if any text was drawn outside it.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure drawn at :data:`PRINT_W` inches wide.
    path : str
        Output PNG path.

    Raises
    ------
    AssertionError
        If any text falls outside the canvas.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    canvas = fig.bbox
    for text in fig.findobj(matplotlib.text.Text):
        if not text.get_visible() or not text.get_text().strip():
            continue
        ext = text.get_window_extent(renderer)
        assert (ext.x0 >= canvas.x0 - 0.5 and ext.x1 <= canvas.x1 + 0.5
                and ext.y0 >= canvas.y0 - 0.5 and ext.y1 <= canvas.y1 + 0.5), (
            f"text {text.get_text()!r} is clipped by the canvas in {os.path.basename(path)}")
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def plot_distributions(tot: dict[str, np.ndarray], total: pd.Series, path: str) -> None:
    """Draw the normalised distribution of each indicator total (Fig. A.12).

    Parameters
    ----------
    tot : dict of str to numpy.ndarray
        Monte Carlo draws of each indicator total, in the indicator's unit.
    total : pandas.Series
        Deterministic total per indicator, same unit.
    path : str
        Output PNG path.
    """
    fig, ax = _figure(3.3)
    data = [tot[i] / float(total[i]) for i in INDICATORS]
    vp = ax.violinplot(data, showextrema=False, widths=0.85)
    for b in vp["bodies"]:
        b.set_facecolor(OKABE_ITO[0]); b.set_edgecolor("none"); b.set_alpha(0.55)
    # The five violins are ALMOST THE SAME SHAPE, and that is the finding rather
    # than a fault in the drawing: material extraction, blue water and land use
    # are 100 % MRIO-driven, so normalising each on its own deterministic total
    # leaves one lognormal multiplier drawn three times. Climate change (78 %
    # MRIO) and waste generation (95 %) differ only slightly. Without the CV
    # printed on each violin a reader sees five identical shapes and cannot tell
    # whether the figure is informative or broken; with it, the 7.2 % to 8.4 %
    # spread is legible and the reason for the sameness is on the page.
    #
    # The outermost labelled ticks bracket the thinnest tails, and the CVs sit in
    # one row along the top of the axes, above every tail: written over the neck
    # of its violin, as it was, each label crossed the distribution it describes.
    step = 0.2
    y_lo = np.floor(min(a.min() for a in data) / step) * step
    y_hi = np.ceil(max(a.max() for a in data) / step) * step
    for k, arr in enumerate(data, start=1):
        q = np.percentile(arr, [2.5, 50, 97.5])
        ax.plot([k, k], [q[0], q[2]], color="k", lw=0.9)
        ax.plot(k, q[1], "o", color="k", ms=2.8)
        ax.annotate(f"CV {100 * arr.std(ddof=1) / arr.mean():.1f}%", xy=(k, y_hi),
                    xytext=(0, -2.5), textcoords="offset points",
                    ha="center", va="top", fontsize=ANNOT_PT)
    ax.axhline(1.0, color=OKABE_ITO[5], lw=0.9, ls="--", label="Deterministic estimate")
    ax.set_ylim(y_lo, y_hi)
    ax.set_yticks(np.round(np.arange(y_lo, y_hi + step / 2, step), 1))
    ax.set_xlim(0.45, len(INDICATORS) + 0.55)
    ax.set_xticks(range(1, len(INDICATORS) + 1))
    ax.set_xticklabels([SHORT[i] for i in INDICATORS])
    ax.set_ylabel("Footprint relative to the deterministic estimate")
    fig.legend(*ax.get_legend_handles_labels(), loc="outside lower center", ncol=1)
    _save(fig, path)


def plot_variance_shares(sob: pd.DataFrame, path: str) -> None:
    """Draw the first-order variance share of each parameter (Fig. A.13).

    Parameters
    ----------
    sob : pandas.DataFrame
        Output of :func:`analysis.uncertainty_2025.sobol_first_order`:
        ``indicator``, ``parameter`` and ``variance_share_pct`` (per cent).
    path : str
        Output PNG path.

    Raises
    ------
    AssertionError
        If an indicator's shares do not sum to 100 %.
    """
    piv = sob.pivot(index="indicator", columns="parameter", values="variance_share_pct")
    piv = piv.loc[INDICATORS]
    # The covariance term BELONGS on this chart. Commuting and patient-and-
    # visitor travel are drawn correlated at rho = 0.8, so the variance of their
    # sum carries a 2 rho sigma_1 sigma_2 term that is neither parameter's alone.
    # Omitting it left the climate bar summing to 90.6 % on a chart whose axis
    # is "share of output variance" and whose limit is 100 %: a reader could see
    # a tenth of the variance was unaccounted for and had nothing to attribute
    # it to. First-order Sobol indices sum to one only for INDEPENDENT inputs
    # (Saltelli et al. 2008); under correlation the covariance is a component of
    # the decomposition, not a rounding error.
    order = ["mrio", "B_COMM", "B_VISI", "covariance_commute_visitor",
             "B_HEAL", "B_ANAE", "B_PMDI"]
    piv = piv[[c for c in order if c in piv.columns]]
    # Guard rather than trust: a bar that does not sum to 100 % is the defect
    # this block exists to prevent, and it should fail here rather than be
    # noticed on the rendered figure.
    sums = piv.sum(axis=1)
    assert np.allclose(sums, 100.0, atol=0.05), (
        f"variance shares do not sum to 100 %: {sums.to_dict()}")

    # A legend entry for a series that is never visible is a false key: the
    # reader is given a colour to look for that does not appear anywhere on the
    # plot. Parameters whose largest share across all indicators falls below the
    # visibility threshold are therefore pooled into one labelled residual, so
    # the bars still sum to 100 % and every key corresponds to something drawn.
    VISIBLE_PCT = 0.5
    faint = [c for c in piv.columns if piv[c].max() < VISIBLE_PCT]
    if faint:
        pooled = piv[faint].sum(axis=1)
        piv = piv.drop(columns=faint)
        if pooled.max() > 0:
            piv[f"_other"] = pooled
        PARAM_LABEL["_other"] = (f"Other bottom-up terms (each below {VISIBLE_PCT:g}%)")
    fig, ax = _figure(2.75)
    labels = [SHORT[i] for i in piv.index]
    bottom = np.zeros(len(piv))
    for k, col in enumerate(piv.columns):
        vals = piv[col].values
        ax.barh(labels, vals, left=bottom, label=PARAM_LABEL[col],
                color=OKABE_ITO[k % len(OKABE_ITO)], height=0.72)
        for yi, (v, b) in enumerate(zip(vals, bottom)):
            if v >= 4:                      # skip tiny segments
                ax.text(b + v / 2, yi, f"{v:.0f}", ha="center", va="center",
                        fontsize=ANNOT_PT, color="white" if k == 0 else "black")
        bottom += vals
    ax.set_xlabel("Share of output variance (%)")
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_ylim(len(piv) - 0.5, -0.5)       # first indicator on top, no dead band
    fig.legend(*ax.get_legend_handles_labels(), loc="outside lower center", ncol=3)
    _save(fig, path)


def plot_group_intervals(groups: Sequence[str], draws: np.ndarray, det: pd.Series,
                         path: str) -> None:
    """Draw each contribution group's 95 % interval, climate change (Fig. A.14).

    Parameters
    ----------
    groups : sequence of str
        Contribution-group names, in the column order of ``draws``.
    draws : numpy.ndarray
        ``(n, len(groups))`` Monte Carlo draws of the group totals, kt CO2e.
    det : pandas.Series
        Deterministic amount per group, kt CO2e.
    path : str
        Output PNG path.
    """
    # Where the uncertainty actually varies: across contribution groups.
    #
    # The five indicators barely differ from one another (see the violins), so a
    # reader could leave this analysis believing the uncertainty is one number.
    # It is not: across the nine contribution groups of the climate footprint the
    # coefficient of variation runs from 8.3 % to 26.3 %, a factor of three, and
    # that spread is what a reader deciding which estimate to trust needs.
    #
    # The design follows Schulte et al. (2024, Earth Syst. Sci. Data 16:2669),
    # figures 5 and 6: a 95 % interval drawn as a bar of RELATIVE deviation from
    # the central value, with the entries sorted by their share of the total, so
    # magnitude and precision are read together. Sorting by share rather than by
    # uncertainty is deliberate - it puts the groups that matter at the top and
    # lets the reader see that the largest are also the tightest.
    rows = []
    for j, g in enumerate(groups):
        arr = draws[:, j]
        med = float(np.median(arr))
        q = np.percentile(arr, [2.5, 97.5])
        rows.append((g, float(det.get(g, np.nan)), med,
                     100 * (q[0] / med - 1), 100 * (q[1] / med - 1),
                     100 * float(arr.std(ddof=1)) / float(arr.mean())))
    rows.sort(key=lambda r: r[1])                     # ascending: largest on top
    names = [r[0] for r in rows]
    share = np.array([r[1] for r in rows]) / float(det.sum()) * 100
    lo = np.array([r[3] for r in rows]); hi = np.array([r[4] for r in rows])
    cv = np.array([r[5] for r in rows])

    fig, ax = _figure(3.35)
    y = np.arange(len(names))
    ax.barh(y, hi - lo, left=lo, height=0.62, color=OKABE_ITO[0], alpha=0.55,
            zorder=2)
    ax.plot(np.zeros(len(names)), y, "o", color="k", ms=3.2, zorder=3)
    ax.axvline(0, color="k", lw=0.7, zorder=1)
    notes = []
    for k in range(len(names)):
        # opaque background, so the grid lines behind a note do not cross it
        notes.append(ax.annotate(
            f"CV {cv[k]:.1f}%   {share[k]:.0f}% of total", xy=(hi[k], y[k]),
            xytext=(3, 0), textcoords="offset points", va="center",
            fontsize=ANNOT_PT, zorder=4,
            bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="none")))
    ax.set_yticks(y); ax.set_yticklabels([_group_label(n) for n in names])
    ax.set_ylim(-0.6, len(names) - 0.4)
    ax.set_xlabel("95% uncertainty interval, relative to the group's own median (%)")
    step = 20
    x_lo = np.floor(lo.min() / step) * step
    ax.set_xlim(x_lo, np.ceil(hi.max() / step) * step)
    # Widen the right limit until the longest note ends inside the axes with
    # 4 pt to spare; the layout moves the axes as it goes, so measure after
    # each draw.
    for _ in range(8):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        inv = ax.transData.inverted()
        right_px = max(n.get_window_extent(renderer).x1 for n in notes) + 4 * fig.dpi / 72
        right = inv.transform((right_px, 0))[0]
        if abs(right - ax.get_xlim()[1]) <= 0.2:
            break
        ax.set_xlim(x_lo, right)
    ax.set_xticks(np.arange(x_lo, ax.get_xlim()[1] + 1e-9, step))
    ax.grid(axis="x", color="0.88", lw=0.5, zorder=0)
    ax.set_axisbelow(True)
    _save(fig, path)


def plot_tornado(mrio: pd.DataFrame, parts: dict[str, pd.DataFrame], total: pd.Series,
                 path: str) -> None:
    """Draw the tornado of the climate footprint (Fig. A.15).

    Parameters
    ----------
    mrio : pandas.DataFrame
        MRIO amount per contribution group and indicator.
    parts : dict of str to pandas.DataFrame
        Bottom-up amount per component, contribution group and indicator.
    total : pandas.Series
        Deterministic total per indicator.
    path : str
        Output PNG path.
    """
    ind = INDICATORS[0]
    base = float(total[ind])
    comp = {"mrio": float(mrio[ind].sum())}
    for code in ("B_HEAL", "B_ANAE", "B_PMDI", "B_COMM", "B_VISI"):
        comp[code] = float(parts[code][ind].sum())
    key = {"mrio": "mrio", "B_HEAL": "direct", "B_ANAE": "anaesthetic",
           "B_PMDI": "pmdi", "B_COMM": "commute", "B_VISI": "visitor"}
    rows = []
    for name, a in comp.items():
        p = PARAMS[key[name]]
        sig = (np.log(p["gsd"]) if p.get("gsd") else np.sqrt(np.log(1 + p["cv"] ** 2)))
        lo, hi = np.exp(-1.96 * sig), np.exp(1.96 * sig)
        rows.append((f"{PARAM_LABEL[name]} (95%)", a * (lo - 1), a * (hi - 1)))
    for name in ("B_ANAE", "B_PMDI", "B_COMM", "B_VISI"):
        for pct in (0.2, 0.5):
            rows.append((f"{PARAM_LABEL[name]} ±{int(pct * 100)}%",
                         -comp[name] * pct, comp[name] * pct))
    # two separate blocks: percentile-based swings and the reviewers' verbatim
    # +/-20 % and +/-50 % swings are different quantities and must not interleave
    pct_rows = sorted([r for r in rows if "(95%)" in r[0]],
                      key=lambda r: max(abs(r[1]), abs(r[2])))
    fix_rows = sorted([r for r in rows if "(95%)" not in r[0]],
                      key=lambda r: max(abs(r[1]), abs(r[2])))
    rows = fix_rows + pct_rows
    fig, ax = _figure(3.7)
    ypos = np.arange(len(rows))
    up = ax.barh(ypos, [r[2] for r in rows], color=OKABE_ITO[5], height=0.72,
                 label="Upper bound")
    down = ax.barh(ypos, [r[1] for r in rows], color=OKABE_ITO[0], height=0.72,
                   label="Lower bound")
    ax.set_yticks(ypos); ax.set_yticklabels([r[0] for r in rows])
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.axvline(0, color="k", lw=0.6)
    ax.set_xlabel(f"Change in the climate footprint (kt CO$_2$e), "
                  f"central estimate {base:,.0f}")
    # the outermost labelled ticks bracket both bar ends
    step = 200
    x_lo = np.floor(min(r[1] for r in rows) / step) * step
    x_hi = np.ceil(max(r[2] for r in rows) / step) * step
    ax.set_xlim(x_lo, x_hi)
    ax.set_xticks(np.arange(x_lo, x_hi + 1e-9, step))
    # The block names sit either side of the divider, at the right, where the
    # rows next to it are short; rotated along the right spine, as they were,
    # the upper name runs into the MRIO bar at print size.
    divider = len(fix_rows) - 0.5
    ax.axhline(divider, color="0.4", lw=0.6, ls=":")
    ax.annotate("parameter 95% range", xy=(x_hi, divider), xytext=(-2, 1.5),
                textcoords="offset points", ha="right", va="bottom", fontsize=ANNOT_PT)
    ax.annotate("prescribed swings", xy=(x_hi, divider), xytext=(-2, -1.5),
                textcoords="offset points", ha="right", va="top", fontsize=ANNOT_PT)
    # lower bound first, as the bars read left to right
    fig.legend([down, up], ["Lower bound", "Upper bound"], loc="outside lower center", ncol=2)
    _save(fig, path)


def plot_ranking(groups: Sequence[str], draws_a: np.ndarray, draws_b: np.ndarray,
                 path: str) -> None:
    """Draw the ranking probabilities of the climate groups, both cases (Fig. A.16).

    Parameters
    ----------
    groups : sequence of str
        Contribution-group names, in the column order of the draws.
    draws_a, draws_b : numpy.ndarray
        ``(n, len(groups))`` climate draws of the group totals under Case A
        (Chemicals n.e.c.) and Case B (pharmaceutical-specific), kt CO2e.
    path : str
        Output PNG path.
    """
    ind = INDICATORS[0]
    # ONE row order for both panels. The panels share their y axis, so the tick
    # labels set on the second panel are the labels of both: sorting each panel
    # separately printed panel B's group names against panel A's rows, which put
    # pharmaceuticals' 0.97 against "Services" until 2026-09-14. The order is
    # panel A's, by probability of rank one, then two, then three.
    tables = {lab: ranking_probabilities(list(groups), {ind: Gx}, top=3)
                   .set_index("group")[["P_rank_1", "P_rank_2", "P_rank_3"]]
              for lab, Gx in [("Case A: Chemicals n.e.c.", draws_a),
                              ("Case B: pharmaceutical-specific", draws_b)]}
    order = (tables["Case A: Chemicals n.e.c."]
             .sort_values(["P_rank_1", "P_rank_2", "P_rank_3"], ascending=True).index)
    fig, axes = _figure(3.55, ncols=2, sharey=True)
    fig.get_layout_engine().set(wspace=0.06)
    for ax, lab in zip(axes, tables):
        rp = tables[lab].loc[order]
        ax.imshow(rp.values, aspect="auto", cmap="Blues", vmin=0, vmax=1)
        ax.set_xticks(range(3)); ax.set_xticklabels(["rank 1", "rank 2", "rank 3"])
        ax.set_yticks(range(len(rp))); ax.set_yticklabels([_group_label(n) for n in rp.index])
        ax.set_title(lab)
        for r in range(rp.shape[0]):
            for c in range(3):
                if rp.values[r, c] > 0.01:
                    ax.text(c, r, f"{rp.values[r, c]:.2f}", ha="center", va="center",
                            fontsize=ANNOT_PT, color="k" if rp.values[r, c] < 0.55 else "w")
    _save(fig, path)


def main() -> None:
    """Run the simulation at the published draw count and seed; write the figures."""
    # Figures live in figures/, never in the gold results tree; that rule has
    # no exception for one layer.
    fig_dir = os.path.join(str(PROJECT_ROOT), "figures", "uncertainty")
    os.makedirs(fig_dir, exist_ok=True)
    mrio, parts, total = load_groups()
    # The published draw count and seed, so every number printed on a figure is
    # the number in the tables; at 50,000 draws the figure printed private
    # travel's CV as 25.6 % against the published 25.8 % (fixed 2026-09-14).
    groups, G, tot, _ = run_mc(mrio, parts, "A")
    _, G_B, tot_B, _ = run_mc(mrio, parts, "B")
    ind0 = INDICATORS[0]
    det_groups = {ind: (mrio[ind] + sum(pt[ind] for pt in parts.values()))
                  for ind in mrio.columns}

    plot_distributions(tot, total, os.path.join(fig_dir, "uncertainty_distributions.png"))
    plot_variance_shares(sobol_first_order(mrio, parts),
                         os.path.join(fig_dir, "uncertainty_variance_shares.png"))
    plot_group_intervals(groups, G[ind0], det_groups[ind0],
                         os.path.join(fig_dir, "uncertainty_by_group_climate.png"))
    plot_tornado(mrio, parts, total, os.path.join(fig_dir, "uncertainty_tornado_climate.png"))
    plot_ranking(groups, G[ind0], G_B[ind0],
                 os.path.join(fig_dir, "uncertainty_ranking_probabilities.png"))
    print("figures written to", fig_dir)
    for f in sorted(os.listdir(fig_dir)):
        print("  ", f)


if __name__ == "__main__":
    main()
