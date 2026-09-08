# -*- coding: utf-8 -*-
"""Monte Carlo parameter uncertainty for the Danish healthcare footprint.

Answers the first-round reviews (systematic uncertainty on the bottom-up
scaling factors; sensitivity of the pharmaceuticals-to-Chemicals-nec mapping;
effect on contribution rankings) and follows the audit of the first
implementation. Design decisions, each defensible in the SI:

1. **What is perturbed.** The footprint is linear in final demand and the
   bottom-up items are additive, so draws recombine precomputed components and
   (I-A) is never re-inverted. A and L are held FIXED; this is stated in the
   Methods, as in the IEooc reference implementation.
2. **MRIO parameter uncertainty is included**, not waved away. EXIOBASE ships
   no element-level standard deviations, so it enters as one multiplicative
   factor applied jointly to all MRIO components, calibrated to the only
   published Monte Carlo estimate for this exact quantity: Lenzen et al.
   (2020) SI Tab. SI 7.1 gives the Danish health-care GHG footprint as
   2.84 +/- 0.24 Mt CO2e, i.e. a relative SD of 8.35 % obtained by propagating
   Eora's Q, T and y. Because it is shared, it cancels in group *rankings* -
   which is the statistically correct behaviour.
3. **Central estimate and interval are consistent.** All multipliers have
   median 1, so the MC median reproduces the deterministic model. Structural
   corrections (price vintage, waste-extension vintage, pharma mapping) are
   discrete SCENARIOS, never hidden inside a distribution. E[X] = exp(sigma^2/2)
   > 1 for a median-1 lognormal, so mean and median are both reported.
4. **Correlation.** Commuting and visitor travel are transplants of the same
   Dutch study through the same DK/NL ratio method, so they share a method
   factor with rho = 0.8 (rho in {0, 0.5, 0.8} reported); ignoring it would
   understate the variance of their sum.
5. **Rankings** are computed from group totals evaluated at the SAME draw, via
   an explicit aggregation of the components (the IEooc Software2 pattern), so
   every group carries uncertainty and the shared MRIO factor cancels.
6. **Verification.** For a weighted sum of independent lognormals the first two
   moments are closed-form; the MC is asserted against them, and Monte Carlo
   standard errors are reported.

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.uncertainty_2025
"""

import os

import numpy as np
import pandas as pd
from scipy.stats import truncnorm

from analysis.constants import eriksen_folder
from paths import OUTPUT_DIR, SILVER_INPUT_DIR

N_DRAWS = int(os.environ.get("HC_MC_DRAWS", 100_000))
SEED = 42
ANALYSIS_YEAR = os.environ.get("HC_ANALYSIS_YEAR", "2022")
RHO_TRAVEL = 0.8

# Correlation of the MRIO factor ACROSS contribution groups.
#
# Applying one shared factor to every group is the rho = 1 case: perfect
# correlation. That is a deliberate choice, not an oversight, and the
# literature is clear that it must be stated as such. Rodrigues et al. (2018,
# ES&T 52:7577-7586) measure country consumption-based-account correlations of
# 0.63 +/- 0.36 (median 0.76) and show that assuming INDEPENDENCE understates
# world uncertainty by about half. Perfect correlation errs in the conservative
# direction - it cannot understate - but it cannot reproduce structured
# sector-level dispersion either. Both bounds are therefore reported.
RHO_MRIO = 1.0

INDICATORS = ["Global warming (ktCO2eq)", "Material extraction (kt)",
              "Blue water consumption (Mm3)", "Land use (km2)", "Waste generation (kt)"]

# ---------------------------------------------------------------------------
# Stochastic parameters: multiplicative, median 1, lognormal (GSD).
# 95 % factor range = GSD^(+/-1.96).
# ---------------------------------------------------------------------------
PARAMS = {
    "mrio": dict(gsd=None, cv=0.0835,
                 why="Lenzen et al. 2020 SI Tab. SI 7.1: relative SD of the Danish "
                     "health-care GHG footprint from a full MRIO Monte Carlo (Eora "
                     "Q, T, y). Applied jointly to all MRIO components."),
    "direct": dict(gsd=1.10,
                   why="Statistics Denmark DRIVHUS/AFFALD accounts; residual risk is the "
                       "alpha-proration of industry 880000 and the medical-N2O netting"),
    "anaesthetic": dict(gsd=1.30,
                        why="Denmark NID 2.G.3.a activity +/-25 %, EF +/-20 % (DCE 2024); "
                            "volatile agents are a transferred proxy"),
    "pmdi": dict(gsd=1.15,
                 why="register dispensing x producer HFC content (Danish EPA F-gas "
                     "inventory / Vestbo & Press-Kristensen 2023)"),
    "commute": dict(gsd=1.25,
                    why="ratio method on NL base values with DST employment and TU distances"),
    "visitor": dict(gsd=1.40,
                    why="no Danish source; Dutch base is itself a transplanted English "
                        "per-capita figure"),
}

# Discrete scenarios (structural choices, NOT random variables)
PRICE_VINTAGE = {"none": 1.00, "nowcast_adjusted": 0.97}
WASTE_VINTAGE = {"central": 1.0, "low": 0.5, "high": 2.0}
PHARMA_RATIO = {
    "Global warming (ktCO2eq)": dict(median=1 / 3, gsd=1.5),
    "Material extraction (kt)": dict(median=1 / 7, gsd=1.5),
    "Blue water consumption (Mm3)": dict(uniform=(1 / 7, 1.0)),
    "Land use (km2)": dict(uniform=(1 / 7, 1.0)),
    "Waste generation (kt)": dict(uniform=(1 / 7, 1.0)),
}

BU_TO_GROUP = {  # bottom-up row -> Figure-1 contribution group
    "B_HEAL": "Operational impacts", "B_ANAE": "Operational impacts",
    "B_PMDI": "Pharmaceuticals and chemical products",
    "B_COMM": "Individual travel", "B_VISI": "Individual travel",
}
PHARMA_GROUP = "Pharmaceuticals and chemical products"


def _ln(rng, gsd, n):
    """Median-1 lognormal factor."""
    return rng.lognormal(0.0, np.log(gsd), n)


def _ln_cv(rng, cv, n):
    """Median-1 lognormal with a target coefficient of variation."""
    sigma = np.sqrt(np.log(1 + cv ** 2))
    return rng.lognormal(0.0, sigma, n)


def load_groups():
    """Group x component decomposition, from the model's own outputs."""
    fig1 = pd.read_excel(os.path.join(str(OUTPUT_DIR), *eriksen_folder().split("/"), "full_results_tables.xlsx"),
                         sheet_name="Fig1_absolute", index_col=0)[INDICATORS].astype(float)
    contrib = pd.read_excel(os.path.join(str(OUTPUT_DIR), *eriksen_folder().split("/"), "contribution_analysis.xlsx"),
                            sheet_name="full")
    bu = {code: contrib[contrib["SecTxtCode"] == code][INDICATORS].astype(float).sum()
          for code in BU_TO_GROUP}
    # MRIO part of each group = group total minus the bottom-up rows mapped to it
    mrio = fig1.copy()
    parts = {c: pd.DataFrame(0.0, index=fig1.index, columns=INDICATORS) for c in bu}
    for code, grp in BU_TO_GROUP.items():
        if grp in mrio.index:
            mrio.loc[grp] -= bu[code]
            parts[code].loc[grp] = bu[code].values
    t1 = pd.read_excel(os.path.join(str(OUTPUT_DIR), *eriksen_folder().split("/"),
                                    "table_1.xlsx"), index_col=0)
    total = t1.loc["Total", INDICATORS].astype(float)
    assert np.allclose(fig1.sum().values, total.values, rtol=1e-6), \
        "group table does not reproduce the reported total - stale outputs?"
    return mrio, parts, total


def run_mc(mrio, parts, pharma_scenario="A", price_vintage="none",
           waste_vintage="central", rho=RHO_TRAVEL, rho_mrio=RHO_MRIO,
           n=N_DRAWS, seed=SEED):
    """Return (group_draws dict of arrays [n x groups], totals [n x indicators])."""
    rng = np.random.default_rng(seed)
    # MRIO factor, correlated across groups with correlation rho_mrio.
    # log f_g = sigma (sqrt(rho) z0 + sqrt(1-rho) z_g) keeps every marginal
    # median 1 with the same sigma, while the correlation between any two
    # groups' log-factors is exactly rho.
    sigma_mrio = np.sqrt(np.log(1.0 + PARAMS["mrio"]["cv"] ** 2))
    shared = rng.standard_normal(n)
    f = {"mrio": None,
         "B_HEAL": _ln(rng, PARAMS["direct"]["gsd"], n),
         "B_ANAE": _ln(rng, PARAMS["anaesthetic"]["gsd"], n),
         "B_PMDI": _ln(rng, PARAMS["pmdi"]["gsd"], n)}
    # correlated travel pair via a shared method factor
    s_c, s_v = np.log(PARAMS["commute"]["gsd"]), np.log(PARAMS["visitor"]["gsd"])
    s_m = np.sqrt(rho * s_c * s_v)
    m = rng.lognormal(0.0, s_m, n)
    f["B_COMM"] = m * rng.lognormal(0.0, np.sqrt(max(s_c ** 2 - s_m ** 2, 0)), n)
    f["B_VISI"] = m * rng.lognormal(0.0, np.sqrt(max(s_v ** 2 - s_m ** 2, 0)), n)

    groups = list(mrio.index)
    mrio_factor = {}
    for g in groups:
        own = rng.standard_normal(n)
        mrio_factor[g] = np.exp(sigma_mrio * (np.sqrt(rho_mrio) * shared
                                              + np.sqrt(1.0 - rho_mrio) * own))
    out, totals = {}, {}
    for ind in INDICATORS:
        G = np.empty((n, len(groups)))
        # pharma-mapping ratio (scenario B), truncated at 1.0 without a point mass
        if pharma_scenario == "B":
            spec = PHARMA_RATIO[ind]
            if "uniform" in spec:
                ratio = rng.uniform(*spec["uniform"], n)
            else:
                lo, s = np.log(spec["median"]), np.log(spec["gsd"])
                z_hi = (np.log(1.0) - lo) / s
                ratio = np.exp(lo + s * truncnorm.rvs(-np.inf, z_hi, size=n,
                                                      random_state=rng))
        else:
            ratio = np.ones(n)
        pv = PRICE_VINTAGE[price_vintage]
        wv = WASTE_VINTAGE[waste_vintage] if ind == "Waste generation (kt)" else 1.0
        for gi, g in enumerate(groups):
            v = mrio.loc[g, ind] * mrio_factor[g] * pv * wv
            if g == PHARMA_GROUP:
                v = v * ratio
            for code in BU_TO_GROUP:
                a = parts[code].loc[g, ind]
                if a != 0:
                    v = v + a * f[code]
            G[:, gi] = v
        out[ind] = G
        totals[ind] = G.sum(axis=1)
    return groups, out, totals, f


def summarize(totals, deterministic):
    rows = []
    for ind, arr in totals.items():
        q = np.percentile(arr, [2.5, 16, 50, 84, 97.5])
        n = len(arr)
        rows.append(dict(
            indicator=ind, unit=ind[ind.find("(") + 1:-1],
            deterministic=float(deterministic[ind]),
            median=q[2], mean=float(arr.mean()), sd=float(arr.std(ddof=1)),
            cv_pct=100 * float(arr.std(ddof=1) / arr.mean()),
            p2_5=q[0], p16=q[1], p84=q[3], p97_5=q[4],
            rel_low_pct=100 * (q[0] / q[2] - 1), rel_high_pct=100 * (q[4] / q[2] - 1),
            mcse_median_pct=100 * float(np.std([np.median(rng_sample) for rng_sample in
                                                np.array_split(arr, 20)], ddof=1)
                                        / np.sqrt(20) / q[2]),
        ))
    return pd.DataFrame(rows)


def sobol_first_order(mrio, parts, pharma_scenario="A"):
    """Exact first-order variance shares (additive model, independent terms)."""
    rows = []
    for ind in INDICATORS:
        contrib = {"mrio": float(mrio[ind].sum())}
        for code in BU_TO_GROUP:
            contrib[code] = float(parts[code][ind].sum())
        var = {}
        for name, a in contrib.items():
            if name == "mrio":
                sig = np.sqrt(np.log(1 + PARAMS["mrio"]["cv"] ** 2))
            else:
                key = {"B_HEAL": "direct", "B_ANAE": "anaesthetic", "B_PMDI": "pmdi",
                       "B_COMM": "commute", "B_VISI": "visitor"}[name]
                sig = np.log(PARAMS[key]["gsd"])
            var[name] = (a ** 2) * (np.exp(sig ** 2) - 1) * np.exp(sig ** 2)
        tot = sum(var.values())
        for name, v in var.items():
            rows.append(dict(indicator=ind, parameter=name,
                             variance_share_pct=100 * v / tot if tot else np.nan))
    return pd.DataFrame(rows)


def analytic_moments(mrio, parts):
    """Closed-form mean and SD of the additive lognormal sum (verification)."""
    res = {}
    for ind in INDICATORS:
        terms = [(float(mrio[ind].sum()), np.sqrt(np.log(1 + PARAMS["mrio"]["cv"] ** 2)))]
        for code in BU_TO_GROUP:
            key = {"B_HEAL": "direct", "B_ANAE": "anaesthetic", "B_PMDI": "pmdi",
                   "B_COMM": "commute", "B_VISI": "visitor"}[code]
            terms.append((float(parts[code][ind].sum()), np.log(PARAMS[key]["gsd"])))
        mean = sum(a * np.exp(s ** 2 / 2) for a, s in terms)
        var = sum(a ** 2 * (np.exp(s ** 2) - 1) * np.exp(s ** 2) for a, s in terms)
        res[ind] = (mean, np.sqrt(var))
    return res


def ranking_probabilities(groups, group_draws, top=3):
    rows = []
    for ind, G in group_draws.items():
        ranks = (-G).argsort(axis=1).argsort(axis=1)
        for gi, g in enumerate(groups):
            rec = dict(indicator=ind, group=g)
            for r in range(min(top, len(groups))):
                rec[f"P_rank_{r + 1}"] = float((ranks[:, gi] == r).mean())
            rows.append(rec)
    return pd.DataFrame(rows)


def main():
    out_dir = os.path.join(str(OUTPUT_DIR), "04_uncertainty_lenzen_ieooc")
    os.makedirs(out_dir, exist_ok=True)
    mrio, parts, total = load_groups()

    # verification against closed-form moments
    groups, G_A, tot_A, _ = run_mc(mrio, parts, "A")
    am = analytic_moments(mrio, parts)
    for ind, arr in tot_A.items():
        mu, sd = am[ind]
        mcse = sd / np.sqrt(len(arr))
        assert abs(arr.mean() - mu) < 5 * mcse, f"{ind}: MC mean off analytic value"
    print(f"PASS: MC means match closed-form moments within 5 MCSE (n={N_DRAWS:,})")

    summaries, ranks, scen_rows = [], [], []
    for scen in ("A", "B"):
        _, G, tot, _ = run_mc(mrio, parts, scen)
        s = summarize(tot, total)
        s.insert(0, "pharma_scenario", scen)
        summaries.append(s)
        r = ranking_probabilities(groups, G)
        r.insert(0, "pharma_scenario", scen)
        ranks.append(r)
    # structural scenarios on the deterministic model
    for pv in PRICE_VINTAGE:
        for wv in WASTE_VINTAGE:
            _, _, tot, _ = run_mc(mrio, parts, "A", price_vintage=pv, waste_vintage=wv,
                                  n=20_000)
            for ind, arr in tot.items():
                scen_rows.append(dict(price_vintage=pv, waste_vintage=wv, indicator=ind,
                                      median=float(np.median(arr))))
    # travel-correlation sensitivity
    rho_rows = []
    for rho in (0.0, 0.5, 0.8):
        _, _, tot, _ = run_mc(mrio, parts, "A", rho=rho, n=20_000)
        a = tot["Global warming (ktCO2eq)"]
        q = np.percentile(a, [2.5, 50, 97.5])
        rho_rows.append(dict(rho=rho, median=q[1], p2_5=q[0], p97_5=q[2],
                             cv_pct=100 * a.std(ddof=1) / a.mean()))

    # MRIO correlation across contribution groups: the rho = 1 default is a
    # perfect-correlation bound; rho = 0 is the independence bound that
    # Rodrigues et al. (2018) show understates uncertainty; rho = 0.76 is their
    # measured median for country consumption-based accounts.
    mrio_rho_rows = []
    for rm, label in ((1.0, "perfect correlation (study default, upper bound)"),
                      (0.76, "Rodrigues et al. 2018 measured median for "
                             "country consumption-based accounts"),
                      (0.0, "independence (lower bound; Rodrigues et al. show "
                            "this understates uncertainty)")):
        _, _, tot, _ = run_mc(mrio, parts, "A", rho_mrio=rm, n=20_000)
        a = tot["Global warming (ktCO2eq)"]
        q = np.percentile(a, [2.5, 50, 97.5])
        mrio_rho_rows.append(dict(
            rho_mrio=rm, interpretation=label, median=q[1], p2_5=q[0],
            p97_5=q[2], cv_pct=100 * a.std(ddof=1) / a.mean()))
    mrio_rho = pd.DataFrame(mrio_rho_rows)

    # Median-1 lognormal multipliers have mean exp(sigma^2/2) > 1, so the MC
    # mean sits slightly above the deterministic value by construction. Small
    # here, but reported rather than left for a referee to find.
    sigma_mrio = np.sqrt(np.log(1.0 + PARAMS["mrio"]["cv"] ** 2))
    mean_inflation = float(np.exp(sigma_mrio ** 2 / 2.0))

    summ = pd.concat(summaries, ignore_index=True)
    rk = pd.concat(ranks, ignore_index=True)
    sob = sobol_first_order(mrio, parts)
    par = pd.DataFrame([dict(parameter=k, distribution="lognormal, median 1",
                             gsd=v.get("gsd"), cv=v.get("cv"),
                             factor_2_5pct=(v["gsd"] ** -1.96 if v.get("gsd") else
                                            np.exp(-1.96 * np.sqrt(np.log(1 + v["cv"] ** 2)))),
                             factor_97_5pct=(v["gsd"] ** 1.96 if v.get("gsd") else
                                             np.exp(1.96 * np.sqrt(np.log(1 + v["cv"] ** 2)))),
                             source=v["why"]) for k, v in PARAMS.items()])
    with pd.ExcelWriter(os.path.join(str(OUTPUT_DIR), "04_uncertainty_lenzen_ieooc", "uncertainty_summary.xlsx"),
                        engine="xlsxwriter") as xw:
        summ.to_excel(xw, sheet_name="totals", index=False)
        sob.to_excel(xw, sheet_name="variance_shares", index=False)
        rk.to_excel(xw, sheet_name="ranking_probabilities", index=False)
        pd.DataFrame(scen_rows).to_excel(xw, sheet_name="structural_scenarios", index=False)
        pd.DataFrame(rho_rows).to_excel(xw, sheet_name="travel_correlation", index=False)
        mrio_rho.to_excel(xw, sheet_name="mrio_correlation", index=False)
        par.to_excel(xw, sheet_name="parameters", index=False)
    for name, df in (("uncertainty_totals", summ), ("uncertainty_variance_shares", sob),
                     ("uncertainty_ranking_probabilities", rk),
                     ("uncertainty_structural_scenarios", pd.DataFrame(scen_rows)),
                     ("uncertainty_parameters", par)):
        df.to_csv(os.path.join(out_dir, name + ".csv"), index=False)

    print(summ[["pharma_scenario", "indicator", "deterministic", "median", "mean",
                "cv_pct", "p2_5", "p97_5"]].round(2).to_string(index=False))
    print("\nFirst-order variance shares (GWP):")
    print(sob[sob.indicator == INDICATORS[0]].round(2).to_string(index=False))
    mrio_rho.assign(
        median_1_lognormal_mean_inflation=mean_inflation).to_csv(
        os.path.join(str(OUTPUT_DIR), "04_uncertainty_lenzen_ieooc",
                     "uncertainty_mrio_correlation.csv"), index=False)
    print(f"\nMRIO-correlation sensitivity (GWP). Median-1 lognormal mean "
          f"inflation exp(sigma^2/2) = {mean_inflation:.5f} "
          f"(+{100 * (mean_inflation - 1):.2f} %):")
    print(mrio_rho[["rho_mrio", "median", "p2_5", "p97_5", "cv_pct"]]
          .round(2).to_string(index=False))
    print("\nTravel-correlation sensitivity (GWP):")
    print(pd.DataFrame(rho_rows).round(2).to_string(index=False))


if __name__ == "__main__":
    main()
