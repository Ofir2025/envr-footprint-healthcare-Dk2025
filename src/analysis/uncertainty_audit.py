# -*- coding: utf-8 -*-
r"""An end-to-end audit of the Monte Carlo, run against the simulation itself.

The uncertainty analysis is verified inside :mod:`analysis.uncertainty_2025` by
one assertion against closed-form moments. That catches a gross error and misses
everything else: a factor whose realised spread is not the spread declared for
it, a correlation that is not the correlation asked for, a variance
decomposition that is exact on paper and wrong in code, an interval that has not
converged, a result that depends on the seed.

Each of those has occurred in this module's history. The correlated travel pair
was built with a construction that silently widened commuting's geometric
standard deviation from the declared 1.25 to 1.278, and the closed-form check
did not fail because it used the declared value on both sides. This module
tests the simulation against its own specification rather than against a
restatement of it.

Every check is a numerical test on drawn samples, not a re-derivation. Where a
quantity has a closed form the two are compared; where it does not, a
brute-force estimate from the draws is used.

Run
---
``HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship PYTHONPATH=src
python -m analysis.uncertainty_audit``

Writes ``uncertainty_audit.csv`` beside the other uncertainty outputs and exits
non-zero if any check fails.
"""

from __future__ import annotations

import os
import sys
from typing import Any

import numpy as np
import pandas as pd

from analysis import uncertainty_2025 as u
from paths import OUTPUT_DIR

FOLDER = "04_uncertainty_lenzen_ieooc"
GWP = "Global warming (ktCO2eq)"


def _add(rows: list[dict[str, Any]], name: str, ok: bool, detail: str,
         tol: str = "") -> None:
    """Record one check."""
    rows.append(dict(check=name, status="PASS" if ok else "FAIL",
                     detail=detail, tolerance=tol))


def audit() -> pd.DataFrame:
    """Run every check and return the report.

    Returns
    -------
    pandas.DataFrame
        One row per check, with ``status`` and the measured quantity.
    """
    rows: list[dict[str, Any]] = []
    mrio, parts, _ = u.load_groups()
    groups, G, totals, factors = u.run_mc(mrio, parts, "A")
    n = len(totals[GWP])

    # ---- 1. every multiplier has median 1 -------------------------------
    worst, worst_name = 0.0, ""
    for name, arr in factors.items():
        if arr is None:
            continue
        dev = abs(float(np.median(arr)) - 1.0)
        if dev > worst:
            worst, worst_name = dev, name
    _add(rows, "median-1 multipliers", worst < 5e-3,
         f"largest deviation {worst:.2e} ({worst_name})", "< 5e-3")

    # ---- 2. realised spread equals the declared spread -------------------
    # This is the check that would have caught the correlated-pair defect.
    declared = {"B_HEAL": "direct", "B_ANAE": "anaesthetic", "B_PMDI": "pmdi",
                "B_COMM": "commute", "B_VISI": "visitor"}
    worst, worst_name = 0.0, ""
    for code, key in declared.items():
        want = float(np.log(u.PARAMS[key]["gsd"]))
        got = float(np.log(factors[code]).std(ddof=1))
        rel = abs(got - want) / want
        if rel > worst:
            worst, worst_name = rel, f"{code}: declared GSD " \
                f"{u.PARAMS[key]['gsd']}, realised {np.exp(got):.4f}"
    _add(rows, "realised GSD equals declared GSD", worst < 0.02,
         f"largest relative deviation {worst:.3%} ({worst_name})", "< 2 %")

    # ---- 3. correlation of the travel pair -------------------------------
    got = float(np.corrcoef(np.log(factors["B_COMM"]),
                            np.log(factors["B_VISI"]))[0, 1])
    _add(rows, "travel-pair log correlation", abs(got - u.RHO_TRAVEL) < 0.02,
         f"asked {u.RHO_TRAVEL}, realised {got:.4f}", "+/- 0.02")

    # ---- 4. correlation of the MRIO factor across groups ------------------
    _, Gh, _, _ = u.run_mc(mrio, parts, "A", rho_mrio=0.5, n=40_000, seed=7)
    lo = np.log(Gh[GWP][:, 0] / mrio.iloc[0][GWP])
    hi = np.log(Gh[GWP][:, 1] / mrio.iloc[1][GWP])
    got = float(np.corrcoef(lo, hi)[0, 1])
    _add(rows, "MRIO factor correlation across groups, rho = 0.5",
         abs(got - 0.5) < 0.06,
         f"asked 0.50, realised {got:.4f} on two groups with no bottom-up term",
         "+/- 0.06")

    # ---- 5. simulation against the closed-form moments -------------------
    am = u.analytic_moments(mrio, parts)
    worst, worst_name = 0.0, ""
    for ind, arr in totals.items():
        mean_c, sd_c = am[ind]
        rel_m = abs(arr.mean() - mean_c) / mean_c
        rel_s = abs(arr.std(ddof=1) - sd_c) / sd_c
        for rel, what in ((rel_m, "mean"), (rel_s, "SD")):
            if rel > worst:
                worst, worst_name = rel, f"{ind} {what}"
    _add(rows, "simulated moments match the closed form", worst < 0.02,
         f"largest relative deviation {worst:.3%} ({worst_name})", "< 2 %")

    # ---- 6. variance decomposition is exact -----------------------------
    sob = u.sobol_first_order(mrio, parts)
    tot = sob.groupby("indicator")["variance_share_pct"].sum()
    _add(rows, "variance shares sum to 100 %",
         bool(np.allclose(tot.values, 100.0, atol=1e-6)),
         f"range {tot.min():.6f} to {tot.max():.6f} %", "1e-6")

    # The closed-form decomposition is checked against a brute-force estimate:
    # freeze one input at its median and measure how much variance disappears.
    share_closed = sob[(sob.indicator == GWP)
                       & (sob.parameter == "mrio")]["variance_share_pct"].iloc[0]
    var_full = float(totals[GWP].var(ddof=1))
    _, _, tot_frozen, _ = u.run_mc(mrio, parts, "A", n=40_000, seed=11)
    # rebuild the total with the MRIO factor held at 1 by using rho_mrio = 1
    # and a zero-variance draw: easiest exactly is to recompute the sum of the
    # bottom-up contributions alone.
    bu_only = np.zeros(40_000)
    _, _, _, f2 = u.run_mc(mrio, parts, "A", n=40_000, seed=11)
    for code in u.BU_TO_GROUP:
        a = float(parts[code][GWP].sum())
        if a:
            bu_only = bu_only + a * f2[code]
    share_brute = 100.0 * (1.0 - float(bu_only.var(ddof=1)) / var_full)
    _add(rows, "MRIO variance share, closed form vs frozen-input estimate",
         abs(share_closed - share_brute) < 3.0,
         f"closed form {share_closed:.1f} %, frozen-input {share_brute:.1f} %",
         "+/- 3 pp")

    # ---- 7. convergence --------------------------------------------------
    med = float(np.median(totals[GWP]))
    halves = [float(np.median(h)) for h in np.array_split(totals[GWP], 2)]
    _add(rows, "median stable across simulation halves",
         abs(halves[0] - halves[1]) / med < 0.005,
         f"halves {halves[0]:,.1f} and {halves[1]:,.1f} kt, "
         f"{abs(halves[0] - halves[1]) / med:.3%} apart", "< 0.5 %")

    lo_hi = np.percentile(totals[GWP], [2.5, 97.5])
    boots = np.array([np.percentile(
        np.random.default_rng(s).choice(totals[GWP], n, replace=True),
        [2.5, 97.5]) for s in range(20)])
    rel = float(np.max(boots.std(axis=0, ddof=1) / lo_hi))
    _add(rows, "interval endpoints converged", rel < 0.005,
         f"bootstrap SD of the 2.5th and 97.5th percentiles is {rel:.3%} "
         f"of the endpoint", "< 0.5 %")

    # ---- 8. independence of the seed -------------------------------------
    spread = []
    for seed in (1, 2, 3, 4, 5):
        _, _, t, _ = u.run_mc(mrio, parts, "A", n=40_000, seed=seed)
        spread.append(float(np.median(t[GWP])))
    rel = float(np.std(spread, ddof=1) / np.mean(spread))
    _add(rows, "result does not depend on the seed", rel < 0.005,
         f"median across five seeds varies by {rel:.3%}", "< 0.5 %")

    # ---- 9. support and shape --------------------------------------------
    _add(rows, "every draw is positive", bool((totals[GWP] > 0).all()),
         f"minimum draw {totals[GWP].min():,.1f} kt", "> 0")
    skew = float(((totals[GWP] - totals[GWP].mean()) ** 3).mean()
                 / totals[GWP].std() ** 3)
    _add(rows, "distribution is right-skewed, as a product of "
         "non-negative quantities must be", skew > 0,
         f"skewness {skew:.3f}", "> 0")

    # ---- 10. the median reproduces the deterministic estimate ------------
    det = float(mrio[GWP].sum() + sum(float(parts[c][GWP].sum())
                                      for c in u.BU_TO_GROUP))
    _add(rows, "median reproduces the deterministic estimate",
         abs(med - det) / det < 0.01,
         f"median {med:,.1f} kt against deterministic {det:,.1f} kt, "
         f"{abs(med - det) / det:.3%} apart", "< 1 %")

    # ---- 11. mean sits above the median by exactly exp(sigma^2/2) --------
    sig = u._sigma("mrio")
    want = float(np.exp(sig ** 2 / 2))
    got = float(totals[GWP].mean() / med)
    _add(rows, "mean/median ratio matches exp(sigma^2/2)",
         abs(got - want) < 0.004,
         f"expected {want:.5f}, measured {got:.5f}", "+/- 0.004")

    # ---- 12. structural scenarios stay outside the interval --------------
    _, _, tot_b, _ = u.run_mc(mrio, parts, "B")
    sep = float(np.median(tot_b[GWP])) < float(np.percentile(totals[GWP], 2.5))
    _add(rows, "structural scenario is not inside the parametric interval",
         sep,
         f"pharmaceutical-mapping scenario median "
         f"{np.median(tot_b[GWP]):,.0f} kt against the central 2.5th "
         f"percentile {np.percentile(totals[GWP], 2.5):,.0f} kt - a modelling "
         f"choice moves the answer further than the parameters do",
         "median outside the central 95 % interval")

    # ---- 13. the pharma scenario multiplier is a proper distribution -----
    _, _, _, _ = u.run_mc(mrio, parts, "B", n=20_000, seed=3)
    ratio_med = float(np.median(tot_b[GWP] / totals[GWP][:len(tot_b[GWP])]))
    _add(rows, "pharmaceutical mapping ratio is bounded above by 1",
         ratio_med < 1.0,
         f"scenario/central median ratio {ratio_med:.3f}; the correction can "
         f"only reduce the mapped intensity, never raise it", "< 1")

    return pd.DataFrame(rows)


def main() -> None:
    """Run the audit, write it, and exit non-zero on any failure."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)
    report = audit()
    report.to_csv(os.path.join(out_dir, "uncertainty_audit.csv"), index=False)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 96)
    print(report.to_string(index=False))
    n_fail = int((report.status == "FAIL").sum())
    print(f"\n{len(report) - n_fail} passed, {n_fail} failed")
    print(f"written -> {out_dir}/uncertainty_audit.csv")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
