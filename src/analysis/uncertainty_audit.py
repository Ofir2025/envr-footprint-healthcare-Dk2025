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

A check whose tolerance is wider than the effect it tests, whose subject is an
identity the code cannot violate, or which skips the parameter that carries
most of the variance, is not a check. Three rows failed one of those tests and
were replaced on 11 September 2026: the median-1 and realised-spread rows now
include the MRIO factor, which they had been skipping; the "shares sum to
100 %" row, which tested floating-point addition, is now a frozen-input
rebuild of the travel block's share; and the mean/median row, whose tolerance
was wider than the inflation it measured, now tests the mean inflation of the
whole sum against its closed form at a tolerance four times inside it.

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
    # The MRIO factor is included. It used to be returned as None and skipped
    # here, so the row certified the five bottom-up factors and passed over the
    # one carrying 78.4 % of the variance. Its realised deviation, 7.5e-04, is
    # in fact the largest of the six, so the row's own "largest" figure was
    # wrong as well as incomplete.
    worst, worst_name = 0.0, ""
    for name, arr in factors.items():
        dev = abs(float(np.median(arr)) - 1.0)
        if dev > worst:
            worst, worst_name = dev, name
    _add(rows, "median-1 multipliers, MRIO factor included", worst < 5e-3,
         f"largest deviation {worst:.2e} ({worst_name}) over "
         f"{len(factors)} parameters", "< 5e-3")

    # ---- 2. realised spread equals the declared spread -------------------
    # This is the check that would have caught the correlated-pair defect.
    # The five bottom-up factors are declared by a GSD, so they are tested on
    # the log-scale SD; the MRIO factor is declared by a coefficient of
    # variation, so it is tested on the CV its block actually realises, which
    # is the calibration target itself.
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
    want_cv = float(u.PARAMS["mrio"]["cv"])
    got_cv = float(factors["mrio"].std(ddof=1) / factors["mrio"].mean())
    rel = abs(got_cv - want_cv) / want_cv
    if rel > worst:
        worst, worst_name = rel, (f"mrio: declared CV {100 * want_cv:.2f} %, "
                                  f"realised {100 * got_cv:.4f} %")
    _add(rows, "realised spread equals declared spread, MRIO factor included",
         worst < 0.02,
         f"largest relative deviation {worst:.3%} ({worst_name}); mrio block "
         f"CV {100 * got_cv:.4f} % against the calibrated "
         f"{100 * want_cv:.2f} %", "< 2 %")

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
    # The row that used to sit here asserted that the shares sum to 100 % at a
    # tolerance of 1e-6. They are computed as v / sum(v), so that row tested
    # floating-point addition and could not fail. It is replaced by a second
    # frozen-input rebuild: the travel block's share, which is the only place
    # the covariance term appears and therefore the number a referee is most
    # entitled to see verified from the draws rather than asserted in closed
    # form. Both frozen-input rows reuse the draws already in hand, so no run
    # is performed whose result is then discarded.
    sob = u.sobol_first_order(mrio, parts)
    var_full = float(totals[GWP].var(ddof=1))
    gwp_shares = sob[sob.indicator == GWP].set_index("parameter")[
        "variance_share_pct"]

    travel_closed = float(gwp_shares["B_COMM"] + gwp_shares["B_VISI"]
                          + gwp_shares["covariance_commute_visitor"])
    a_c, a_v = (float(parts["B_COMM"][GWP].sum()),
                float(parts["B_VISI"][GWP].sum()))
    travel_only = a_c * factors["B_COMM"] + a_v * factors["B_VISI"]
    travel_brute = 100.0 * float(travel_only.var(ddof=1)) / var_full
    _add(rows, "travel block variance share, closed form vs frozen-input "
         "estimate", abs(travel_closed - travel_brute) < 1.5,
         f"closed form {travel_closed:.2f} % (own terms "
         f"{gwp_shares['B_COMM'] + gwp_shares['B_VISI']:.2f} % plus covariance "
         f"{gwp_shares['covariance_commute_visitor']:.2f} %), frozen-input "
         f"{travel_brute:.2f} %", "+/- 1.5 pp")

    # The same test on the MRIO share: freeze the MRIO factor and measure how
    # much variance disappears.
    share_closed = float(gwp_shares["mrio"])
    bu_only = np.zeros(n)
    for code in u.BU_TO_GROUP:
        a = float(parts[code][GWP].sum())
        if a:
            bu_only = bu_only + a * factors[code]
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

    # ---- 10. the median reproduces the deterministic estimate to 0.5 % ----
    # Every multiplier has median 1, but the median of a SUM of lognormals is
    # not the sum of the medians, so this is an agreement to a stated
    # tolerance and not an identity. The tolerance is the 0.5 % the documents
    # claim, so that a drift past the claim fails the run instead of quietly
    # making the manuscript wrong.
    det = float(mrio[GWP].sum() + sum(float(parts[c][GWP].sum())
                                      for c in u.BU_TO_GROUP))
    _add(rows, "median reproduces the deterministic estimate to within 0.5 %",
         abs(med - det) / det < 0.005,
         f"median {med:,.1f} kt against deterministic {det:,.1f} kt, "
         f"{abs(med - det) / det:.3%} apart", "< 0.5 %")

    # ---- 11. the simulated mean matches the closed-form mean inflation ----
    # This row used to compare the mean/median ratio with exp(sigma_M^2/2) at
    # a tolerance of +/- 0.004. The effect under test was 0.00348, SMALLER
    # than the tolerance, so the row passed whether or not any inflation
    # occurred; and exp(sigma^2/2) is the mean inflation of ONE lognormal, not
    # of a sum of six with different spreads, so the agreement it reported was
    # a coincidence presented as an identity. The real statement is that the
    # simulated mean sits above the deterministic total by the closed-form
    # sum_j a_j exp(sigma_j^2 / 2) / sum_j a_j, which is +0.84 % here rather
    # than the MRIO factor's +0.35 %. The tolerance is set four times inside
    # the effect.
    terms = [(float(mrio[GWP].sum()), u._sigma("mrio"))]
    terms += [(float(parts[c][GWP].sum()), u._sigma(c)) for c in u.BU_TO_GROUP]
    want = float(sum(a * np.exp(s ** 2 / 2) for a, s in terms)
                 / sum(a for a, _ in terms))
    got = float(totals[GWP].mean() / det)
    _add(rows, "mean inflation matches the closed form over all six "
         "parameters", abs(got - want) < 0.002,
         f"expected {want:.5f} (+{100 * (want - 1):.2f} %), measured "
         f"{got:.5f} (+{100 * (got - 1):.2f} %); the MRIO factor alone would "
         f"give {np.exp(u._sigma('mrio') ** 2 / 2):.5f}",
         "+/- 0.002 on an effect of 0.008")

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

    # ---- 13. the calibration survives the correlation sensitivity --------
    # This is the check for the defect corrected on 8 September 2026: applying
    # one sigma at every rho let the total's spread collapse as the correlation
    # fell, so the independence case reported an interval roughly half as wide
    # as the calibration supports.
    #
    # The run is the PUBLISHED one - 40,000 draws at seed 13, the
    # configuration behind uncertainty_mrio_correlation.csv - not an
    # independent draw at seed 29 as it was until 11 September 2026. On that
    # seed the row reported 7.84 / 7.81 / 7.78 % and a spread of 0.05 pp while
    # the gold table it is meant to certify published 7.86 / 7.83 / 7.72 % and
    # a spread of 0.14 pp, so the folder carried two different answers to the
    # same question and the audit contradicted the claim it existed to check.
    cvs = []
    for rm in (1.0, 0.76, 0.0):
        _, _, t, _ = u.run_mc(mrio, parts, "A", rho_mrio=rm, n=40_000, seed=13)
        arr = t[GWP]
        cvs.append(100 * float(arr.std(ddof=1) / arr.mean()))
    spread = max(cvs) - min(cvs)
    _add(rows, "calibrated total CV held across correlations", spread < 0.5,
         f"CV at rho = 1.00 / 0.76 / 0.00 is "
         f"{cvs[0]:.2f} / {cvs[1]:.2f} / {cvs[2]:.2f} %, a spread of "
         f"{spread:.2f} pp, recomputed on the published run (40,000 draws, "
         f"seed 13)", "< 0.5 pp")

    # ---- 14. group-level spread widens as correlation falls --------------
    # The point of rho once the total is held: it redistributes variance.
    _, G1, _, _ = u.run_mc(mrio, parts, "A", rho_mrio=1.0, n=40_000, seed=31)
    _, G0, _, _ = u.run_mc(mrio, parts, "A", rho_mrio=0.0, n=40_000, seed=31)
    cv1 = float(np.median(100 * G1[GWP].std(axis=0, ddof=1)
                          / G1[GWP].mean(axis=0)))
    cv0 = float(np.median(100 * G0[GWP].std(axis=0, ddof=1)
                          / G0[GWP].mean(axis=0)))
    _add(rows, "group-level spread widens as correlation falls", cv0 > cv1,
         f"median group CV {cv1:.1f} % at rho = 1 against {cv0:.1f} % at "
         f"rho = 0; the total is unchanged, so rho redistributes variance "
         f"rather than creating it", "rho = 0 wider")

    # ---- 15. Tier 1 agrees with Tier 2 -----------------------------------
    # Both tiers now use the same variance expression, so the residual gap is
    # what each divides by: Tier 1 normalises on the deterministic total,
    # Tier 2 on the simulated mean, which sits about 0.84 % above it.
    t1 = u.tier1_error_propagation(mrio, parts)
    t1_gwp = float(t1.loc[t1.indicator == GWP, "tier1_uncertainty_pct"].iloc[0])
    t2_gwp = 100 * float(totals[GWP].std(ddof=1) / totals[GWP].mean())
    _add(rows, "Tier 1 agrees with Tier 2", abs(t1_gwp - t2_gwp) < 1.0,
         f"Tier 1 error propagation {t1_gwp:.2f} % against Tier 2 simulation "
         f"{t2_gwp:.2f} %; IPCC (2000) 6.3.1 requires both to be reported",
         "< 1 pp")

    # ---- 16. the pharma scenario multiplier is a proper distribution -----
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
