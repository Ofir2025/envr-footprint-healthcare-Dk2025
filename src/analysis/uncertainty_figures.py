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

SHORT = {"Global warming (ktCO2eq)": "climate", "Material extraction (kt)": "materials",
         "Blue water consumption (Mm3)": "blue water", "Land use (km2)": "land",
         "Waste generation (kt)": "waste"}


def main():
    fig_dir = os.path.join(str(OUTPUT_DIR), "figures")
    os.makedirs(fig_dir, exist_ok=True)
    mrio, parts, total = load_groups()
    groups, G, tot, _ = run_mc(mrio, parts, "A", n=50_000)
    _, G_B, tot_B, _ = run_mc(mrio, parts, "B", n=50_000)

    # 1. normalised distributions
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    data = [tot[i] / float(total[i]) for i in INDICATORS]
    vp = ax.violinplot(data, showextrema=False, widths=0.85)
    for b in vp["bodies"]:
        b.set_facecolor("#4878a8"); b.set_alpha(0.65)
    for k, i in enumerate(INDICATORS, start=1):
        q = np.percentile(tot[i] / float(total[i]), [2.5, 50, 97.5])
        ax.plot([k, k], [q[0], q[2]], color="k", lw=1.2)
        ax.plot(k, q[1], "o", color="k", ms=4)
    ax.axhline(1.0, color="firebrick", lw=1, ls="--", label="deterministic estimate")
    ax.set_xticks(range(1, len(INDICATORS) + 1))
    ax.set_xticklabels([SHORT[i] for i in INDICATORS])
    ax.set_ylabel("footprint relative to the deterministic estimate")
    ax.set_title("Parameter uncertainty by indicator (median, 95 % interval), Denmark 2022")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(fig_dir, "uncertainty_distributions.png"), dpi=300)
    plt.close(fig)

    # 2. variance shares
    sob = sobol_first_order(mrio, parts)
    piv = sob.pivot(index="indicator", columns="parameter", values="variance_share_pct")
    piv = piv.loc[INDICATORS]
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    bottom = np.zeros(len(piv))
    for col in piv.columns:
        ax.barh([SHORT[i] for i in piv.index], piv[col].values, left=bottom, label=col)
        bottom += piv[col].values
    ax.set_xlabel("share of output variance (%)")
    ax.set_title("First-order variance contributions (exact for this additive model)")
    ax.legend(frameon=False, fontsize=8, ncol=3)
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
        rows.append((f"{name} (95 %)", a * (lo - 1), a * (hi - 1)))
    for name in ("B_ANAE", "B_PMDI", "B_COMM", "B_VISI"):
        for pct in (0.2, 0.5):
            rows.append((f"{name} +/-{int(pct * 100)} %", -comp[name] * pct, comp[name] * pct))
    rows.sort(key=lambda r: max(abs(r[1]), abs(r[2])))
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ypos = np.arange(len(rows))
    ax.barh(ypos, [r[2] for r in rows], color="#c0504d", label="high")
    ax.barh(ypos, [r[1] for r in rows], color="#4878a8", label="low")
    ax.set_yticks(ypos); ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel(f"change in the climate footprint (kt CO2eq); central estimate {base:,.0f}")
    ax.set_title("One-at-a-time sensitivity, climate change")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(fig_dir, "uncertainty_tornado_climate.png"), dpi=300)
    plt.close(fig)

    # 4. ranking probabilities (climate), both pharma scenarios
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    for ax, (lab, Gx) in zip(axes, [("A: pharma as Chemicals nec", G),
                                    ("B: pharma-specific intensity", G_B)]):
        rp = ranking_probabilities(groups, {ind: Gx[ind]}, top=3)
        rp = rp.set_index("group")[["P_rank_1", "P_rank_2", "P_rank_3"]]
        rp = rp.sort_values("P_rank_1", ascending=True)
        im = ax.imshow(rp.values, aspect="auto", cmap="Blues", vmin=0, vmax=1)
        ax.set_xticks(range(3)); ax.set_xticklabels(["rank 1", "rank 2", "rank 3"])
        ax.set_yticks(range(len(rp))); ax.set_yticklabels(rp.index, fontsize=8)
        ax.set_title(lab, fontsize=9)
        for r in range(rp.shape[0]):
            for c in range(3):
                if rp.values[r, c] > 0.01:
                    ax.text(c, r, f"{rp.values[r, c]:.2f}", ha="center", va="center",
                            fontsize=7, color="k" if rp.values[r, c] < 0.6 else "w")
    fig.suptitle("Probability that a contribution group holds each rank (climate change)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(fig_dir, "uncertainty_ranking_probabilities.png"), dpi=300)
    plt.close(fig)
    print("figures written to", fig_dir)
    for f in sorted(os.listdir(fig_dir)):
        print("  ", f)


if __name__ == "__main__":
    main()
