# -*- coding: utf-8 -*-
"""Figures for the uncertainty section (see analysis.uncertainty_2025).

1. distribution of each indicator total, normalised to its deterministic value
   (one panel, all five indicators, so relative spread and skew are comparable);
2. first-order variance shares per indicator (exact for this additive model);
3. tornado for climate change, with the percentile-based swings and the
   reviewers' verbatim +/-20 % and +/-50 % swings in separate blocks;
4. contribution-group ranking probabilities.

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.uncertainty_figures
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from paths import OUTPUT_DIR
from analysis.uncertainty_2025 import (INDICATORS, PARAMS, load_groups, run_mc,
                                       sobol_first_order, ranking_probabilities)

SHORT = {"Global warming (ktCO2eq)": "Climate change", "Material extraction (kt)": "Material extraction",
         "Blue water consumption (Mm3)": "Blue water", "Land use (km2)": "Land use",
         "Waste generation (kt)": "Waste generation"}

# Okabe-Ito, colour-vision-deficiency safe; unique hue per key
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442"]
# full names, never the internal row codes
PARAM_LABEL = {"mrio": "MRIO parameters", "B_HEAL": "Direct operational",
               "B_ANAE": "Anaesthetic gases", "B_PMDI": "pMDI propellants",
               "B_COMM": "Employee commuting", "B_VISI": "Patient and visitor travel"}
# font ranking: panel titles > legend > ticks/labels
plt.rcParams.update({"axes.titlesize": 13, "legend.fontsize": 10,
                     "axes.labelsize": 11, "xtick.labelsize": 10,
                     "ytick.labelsize": 10, "figure.dpi": 300})


def main():
    fig_dir = os.path.join(str(OUTPUT_DIR), "04_uncertainty_lenzen_ieooc", "figures")
    os.makedirs(fig_dir, exist_ok=True)
    mrio, parts, total = load_groups()
    groups, G, tot, _ = run_mc(mrio, parts, "A", n=50_000)
    _, G_B, tot_B, _ = run_mc(mrio, parts, "B", n=50_000)

    # 1. normalised distributions
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    data = [tot[i] / float(total[i]) for i in INDICATORS]
    vp = ax.violinplot(data, showextrema=False, widths=0.85)
    for b in vp["bodies"]:
        b.set_facecolor(OKABE_ITO[0]); b.set_alpha(0.55)
    for k, i in enumerate(INDICATORS, start=1):
        q = np.percentile(tot[i] / float(total[i]), [2.5, 50, 97.5])
        ax.plot([k, k], [q[0], q[2]], color="k", lw=1.2)
        ax.plot(k, q[1], "o", color="k", ms=4)
    ax.axhline(1.0, color=OKABE_ITO[5], lw=1.2, ls="--", label="Deterministic estimate")
    ax.set_xticks(range(1, len(INDICATORS) + 1))
    ax.set_xticklabels([SHORT[i] for i in INDICATORS], rotation=20, ha="right")
    ax.set_ylabel("Footprint relative to the deterministic estimate")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
    fig.tight_layout(); fig.savefig(os.path.join(fig_dir, "uncertainty_distributions.png"), dpi=300)
    plt.close(fig)

    # 2. variance shares
    sob = sobol_first_order(mrio, parts)
    piv = sob.pivot(index="indicator", columns="parameter", values="variance_share_pct")
    piv = piv.loc[INDICATORS]
    order = ["mrio", "B_COMM", "B_VISI", "B_HEAL", "B_ANAE", "B_PMDI"]
    piv = piv[[c for c in order if c in piv.columns]]

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
        PARAM_LABEL["_other"] = (f"Other bottom-up items (each < {VISIBLE_PCT:g} %)")
    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    labels = [SHORT[i] for i in piv.index]
    bottom = np.zeros(len(piv))
    for k, col in enumerate(piv.columns):
        vals = piv[col].values
        ax.barh(labels, vals, left=bottom, label=PARAM_LABEL[col],
                color=OKABE_ITO[k % len(OKABE_ITO)], height=0.62)
        for yi, (v, b) in enumerate(zip(vals, bottom)):
            if v >= 4:                      # skip tiny segments
                ax.text(b + v / 2, yi, f"{v:.0f}", ha="center", va="center",
                        fontsize=9, color="white" if k == 0 else "black")
        bottom += vals
    ax.set_xlabel("Share of output variance (%)")
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.invert_yaxis()
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3)
    fig.tight_layout(); fig.savefig(os.path.join(fig_dir, "uncertainty_variance_shares.png"), dpi=300)
    plt.close(fig)

    # 3. tornado for climate change
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
        rows.append((f"{PARAM_LABEL[name]} (95 %)", a * (lo - 1), a * (hi - 1)))
    for name in ("B_ANAE", "B_PMDI", "B_COMM", "B_VISI"):
        for pct in (0.2, 0.5):
            rows.append((f"{PARAM_LABEL[name]} ±{int(pct * 100)} %",
                         -comp[name] * pct, comp[name] * pct))
    # two separate blocks: percentile-based swings and the reviewers' verbatim
    # +/-20 % and +/-50 % swings are different quantities and must not interleave
    pct_rows = sorted([r for r in rows if "(95 %)" in r[0]],
                      key=lambda r: max(abs(r[1]), abs(r[2])))
    fix_rows = sorted([r for r in rows if "(95 %)" not in r[0]],
                      key=lambda r: max(abs(r[1]), abs(r[2])))
    rows = fix_rows + pct_rows
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    ypos = np.arange(len(rows))
    ax.barh(ypos, [r[2] for r in rows], color=OKABE_ITO[5], label="Upper bound")
    ax.barh(ypos, [r[1] for r in rows], color=OKABE_ITO[0], label="Lower bound")
    ax.set_yticks(ypos); ax.set_yticklabels([r[0] for r in rows])
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel(f"Change in the climate footprint (kt CO\u2082eq), "
                  f"central estimate {base:,.0f}")
    ax.axhline(len(fix_rows) - 0.5, color="0.4", lw=0.8, ls=":")
    ax.text(0.995, (len(fix_rows) + len(pct_rows) / 2) / len(rows), "parameter 95 % range",
            transform=ax.transAxes, ha="right", va="center", fontsize=9, color="0.35",
            rotation=90)
    ax.text(0.995, (len(fix_rows) / 2) / len(rows), "prescribed swings",
            transform=ax.transAxes, ha="right", va="center", fontsize=9, color="0.35",
            rotation=90)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    fig.tight_layout(); fig.savefig(os.path.join(fig_dir, "uncertainty_tornado_climate.png"), dpi=300)
    plt.close(fig)

    # 4. ranking probabilities (climate), both pharma scenarios
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 6.0), sharey=True)
    for ax, (lab, Gx) in zip(axes, [("A: pharma as Chemicals nec", G),
                                    ("B: pharma-specific intensity", G_B)]):
        rp = ranking_probabilities(groups, {ind: Gx[ind]}, top=3)
        rp = rp.set_index("group")[["P_rank_1", "P_rank_2", "P_rank_3"]]
        rp = rp.sort_values("P_rank_1", ascending=True)
        im = ax.imshow(rp.values, aspect="auto", cmap="Blues", vmin=0, vmax=1)
        ax.set_xticks(range(3)); ax.set_xticklabels(["rank 1", "rank 2", "rank 3"])
        ax.set_yticks(range(len(rp))); ax.set_yticklabels(rp.index)
        ax.set_title(lab)
        for r in range(rp.shape[0]):
            for c in range(3):
                if rp.values[r, c] > 0.01:
                    ax.text(c, r, f"{rp.values[r, c]:.2f}", ha="center", va="center",
                            fontsize=9, color="k" if rp.values[r, c] < 0.55 else "w")
    fig.tight_layout(); fig.savefig(os.path.join(fig_dir, "uncertainty_ranking_probabilities.png"), dpi=300)
    plt.close(fig)
    print("figures written to", fig_dir)
    for f in sorted(os.listdir(fig_dir)):
        print("  ", f)


if __name__ == "__main__":
    main()
