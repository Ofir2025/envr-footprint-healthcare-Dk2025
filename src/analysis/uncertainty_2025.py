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
   factor applied jointly to all MRIO components, calibrated to the closest
   published Monte Carlo estimate: Lenzen et al. (2020) SI Tab. SI 7.1 gives
   the Danish health-care GHG footprint as 2.84 +/- 0.24 Mt CO2e, i.e. a
   relative SD of 8.35 % obtained by propagating Eora's Q, T and y. This is a
   TRANSFER, not a reproduction. The calibration target is an Eora footprint
   39 % smaller than this study's EXIOBASE 4.675 Mt, and Lenzen's own Fig. SI
   7.1 makes the relative SD a decreasing function of footprint size, so
   carrying 8.35 % up to a larger footprint errs wide rather than narrow.
   Lenzen also fit a normal to their draws and report sigma_F; this study
   reinterprets the same number as a lognormal CV. Because the factor is
   shared, it cancels in group *rankings* - which is the statistically correct
   behaviour.
3. **Central estimate and interval are consistent.** All multipliers have
   median 1, so the simulation adds dispersion without shifting the centre.
   The median of a SUM of lognormals is not the sum of the medians, so the MC
   median reproduces the deterministic model to within 0.5 % (0.45 % for
   climate), not exactly; only the MRIO block on its own has median exactly 1.
   Structural corrections (price base year, waste-extension reference year,
   pharma mapping) are discrete SCENARIOS, never hidden inside a distribution.
   E[X] = exp(sigma^2/2) > 1 for a median-1 lognormal, so mean and median are
   both reported.
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

from __future__ import annotations

import os
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import truncnorm

from analysis.constants import eriksen_folder
from analysis.extra_functions import write_sheets_as_csv
from paths import ERIKSEN_INTERIM_DIR, OUTPUT_DIR

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
    # Each `why` is the gold table's own provenance cell and is carried verbatim
    # into the tables of record, which allow 180 characters; keep them inside it
    # so nothing is cut mid-word. The fuller argument - in particular that the
    # mrio calibration is a transfer from Eora's 2.84 Mt to EXIOBASE's 4.675 Mt,
    # and that Lenzen's own Fig. SI 7.1 makes it err wide - is in section 04 of
    # docs/methods/replications.md and in docs/revision/uncertainty.md.
    "mrio": dict(gsd=None, cv=0.0835,
                 why="Lenzen et al. 2020 SI Tab. SI 7.1: relative SD of the Danish "
                     "health-care GHG footprint from an Eora MRIO Monte Carlo, "
                     "transferred from their 2.84 Mt to this study's 4.675 Mt"),
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
                    why="patient travel from the Danish travel survey (TU Tabel 15, "
                        "purpose 33); the VISITOR part alone has no Danish source, "
                        "carrying the NHS England ratio 0.236 (Tennison 2021)"),
}

# Discrete scenarios (structural choices, NOT random variables)
PRICE_BASE_YEAR = {"none": 1.00, "nowcast_adjusted": 0.97}
REFERENCE_YEAR = {"central": 1.0, "low": 0.5, "high": 2.0}
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


def _ln(rng: np.random.Generator, gsd: float, n: int) -> np.ndarray:
    """Draw a median-1 lognormal multiplier.

    Parameters
    ----------
    rng : numpy.random.Generator
        Generator supplying the draws; consumed in place.
    gsd : float
        Geometric standard deviation, so that :math:`\\sigma=\\ln(\\mathrm{GSD})`.
    n : int
        Number of draws.

    Returns
    -------
    numpy.ndarray
        Array of ``n`` positive multipliers with median 1.
    """
    return rng.lognormal(0.0, np.log(gsd), n)


def load_groups() -> tuple[pd.DataFrame, dict[str, pd.DataFrame], pd.Series]:
    """Read the deterministic group x component decomposition the draws perturb.

    Returns
    -------
    mrio : pandas.DataFrame
        MRIO amount per contribution group (rows) and indicator (columns),
        i.e. each Figure-1 group total less the bottom-up rows mapped to it.
    parts : dict of str to pandas.DataFrame
        One frame per bottom-up component, same shape as ``mrio``, zero
        everywhere except in the group that component belongs to.
    total : pandas.Series
        Deterministic total per indicator, from ``table_01.csv``.

    Raises
    ------
    AssertionError
        When the group table does not reproduce the reported total, which
        means one of the two inputs is stale.
    """
    fig1 = pd.read_csv(os.path.join(str(OUTPUT_DIR), *eriksen_folder().split("/"),
                                    "full_results_tables_fig1_absolute.csv"),
                       index_col=0)[INDICATORS].astype(float)
    # Intermediate workbook, not a deliverable: it lives in silver's handoff
    # tree (see main_2025's interim_dir), not in gold.
    contrib = pd.read_excel(os.path.join(str(ERIKSEN_INTERIM_DIR),
                                         *eriksen_folder().split("/"),
                                         "contribution_analysis.xlsx"),
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
    t1 = pd.read_csv(os.path.join(str(OUTPUT_DIR), *eriksen_folder().split("/"),
                                  "table_01.csv"), index_col=0)
    total = t1.loc["Total", INDICATORS].astype(float)
    assert np.allclose(fig1.sum().values, total.values, rtol=1e-6), \
        "group table does not reproduce the reported total - stale outputs?"
    return mrio, parts, total


def run_mc(mrio: pd.DataFrame, parts: dict[str, pd.DataFrame],
           pharma_scenario: str = "A", price_base_year: str = "none",
           reference_year: str = "central", rho: float = RHO_TRAVEL,
           rho_mrio: float = RHO_MRIO, n: int = N_DRAWS, seed: int = SEED,
           cv_target: float | None = None,
           ) -> tuple[list[str], dict[str, np.ndarray], dict[str, np.ndarray],
                      dict[str, np.ndarray]]:
    """Simulate the footprint by recombining the deterministic amounts.

    Parameters
    ----------
    mrio : pandas.DataFrame
        MRIO amount per contribution group and indicator, from
        :func:`load_groups`.
    parts : dict of str to pandas.DataFrame
        Bottom-up amount per component, group and indicator.
    pharma_scenario : {'A', 'B'}, optional
        ``'A'`` keeps the *Chemicals nec* mapping; ``'B'`` applies the
        pharmaceutical-specific ratio, a structural scenario rather than a
        parameter.
    price_base_year : {'none', 'nowcast_adjusted'}, optional
        Structural scenario on the price base year.
    reference_year : {'central', 'low', 'high'}, optional
        Structural scenario on the waste-extension reference year; applies to
        the waste indicator only.
    rho : float, optional
        Correlation imposed between the log-factors of commuting and visitor
        travel.
    rho_mrio : float, optional
        Correlation of the MRIO factor across contribution groups. At the
        default 1.0 every group carries numerically the same draw.
    n : int, optional
        Number of draws.
    seed : int, optional
        Seed of the generator, so a run is reproducible.
    cv_target : float, optional
        Relative standard deviation the MRIO block must reproduce. Defaults to
        the calibrated ``PARAMS["mrio"]["cv"]``.

    Returns
    -------
    groups : list of str
        Contribution-group names, in the column order of every array below.
    group_draws : dict of str to numpy.ndarray
        Per indicator, an ``(n, len(groups))`` array of group totals.
    totals : dict of str to numpy.ndarray
        Per indicator, the ``(n,)`` array of footprint totals.
    factors : dict of str to numpy.ndarray
        The realised multipliers, one ``(n,)`` array per stochastic parameter.
        ``factors["mrio"]`` is the multiplier realised on the whole MRIO block
        of ``INDICATORS[0]``, i.e. the drawn block amount over its
        deterministic amount; at ``rho_mrio = 1`` that is exactly the shared
        factor :math:`e^{\\sigma_M z_0}` every group carries. It is returned
        so the audit can test the parameter that carries most of the variance
        rather than skipping it.

    Notes
    -----
    The draw order of ``rng`` is part of the published result: every reported
    median and interval is reproducible only from this sequence at the seed
    and draw count the output tables now record. Adding or removing a draw
    here moves every number in the layer.
    """
    rng = np.random.default_rng(seed)
    cv_target = PARAMS["mrio"]["cv"] if cv_target is None else float(cv_target)
    # MRIO factor, correlated across groups with correlation rho_mrio.
    # log f_g = sigma (sqrt(rho) z0 + sqrt(1-rho) z_g) keeps every marginal
    # median 1 with the same sigma, while the correlation between any two
    # groups' log-factors is exactly rho.
    shared = rng.standard_normal(n)
    # "mrio" is filled in below, from the block actually realised on the first
    # indicator. It used to be left at None, which made the audit's median-1
    # and realised-spread checks silently skip the one parameter carrying
    # 78 % of the variance.
    f: dict[str, np.ndarray] = {
         "B_HEAL": _ln(rng, PARAMS["direct"]["gsd"], n),
         "B_ANAE": _ln(rng, PARAMS["anaesthetic"]["gsd"], n),
         "B_PMDI": _ln(rng, PARAMS["pmdi"]["gsd"], n)}
    # Correlated travel pair. Both factors are built from ONE shared standard
    # normal and one of their own, each scaled by its own sigma:
    #
    #     log h_C = sigma_C (sqrt(rho) z0 + sqrt(1 - rho) z_C)
    #     log h_V = sigma_V (sqrt(rho) z0 + sqrt(1 - rho) z_V)
    #
    # so each marginal keeps exactly the GSD declared in PARAMS while the
    # correlation of the log-factors is exactly rho. The previous construction
    # drew one shared factor of sigma_m = sqrt(rho sigma_C sigma_V) and topped
    # each up by sqrt(sigma^2 - sigma_m^2); at rho = 0.8 that root is negative
    # for commuting (sigma_m = 0.2451 against sigma_C = 0.2231), the clamp to
    # zero silently raised commuting's realised GSD from the declared 1.25 to
    # 1.278, and the simulation then no longer matched the analytic moments or
    # the variance decomposition, both of which use the declared sigmas.
    s_c, s_v = np.log(PARAMS["commute"]["gsd"]), np.log(PARAMS["visitor"]["gsd"])
    z_shared = rng.standard_normal(n)
    a_rho, b_rho = np.sqrt(rho), np.sqrt(1.0 - rho)
    f["B_COMM"] = np.exp(s_c * (a_rho * z_shared + b_rho * rng.standard_normal(n)))
    f["B_VISI"] = np.exp(s_v * (a_rho * z_shared + b_rho * rng.standard_normal(n)))

    groups = list(mrio.index)
    out, totals = {}, {}
    for ind in INDICATORS:
        # The MRIO spread is re-solved for THIS indicator at THIS correlation,
        # so the calibrated block CV is held whatever rho is. At rho = 1 the
        # solution is the plain sqrt(ln(1 + CV^2)) and the default result is
        # unchanged; below 1 the spread must widen to compensate for the lost
        # covariance. Without this the independence case silently abandoned the
        # calibration and reported an interval half as wide as the evidence
        # supports. See sigma_for_rho.
        sigma_mrio = (np.sqrt(np.log(1.0 + cv_target * cv_target))
                      if rho_mrio >= 1.0
                      else sigma_for_rho(mrio[ind].values, rho_mrio, cv_target))
        mrio_factor = {}
        for g in groups:
            own = rng.standard_normal(n)
            mrio_factor[g] = np.exp(sigma_mrio * (np.sqrt(rho_mrio) * shared
                                                  + np.sqrt(1.0 - rho_mrio) * own))
        if ind == INDICATORS[0]:
            # The block multiplier actually realised, amount-weighted over the
            # groups. Nothing is drawn here, so the generator's sequence - and
            # therefore every published median and interval - is untouched.
            amt = mrio[ind].values.astype(float)
            f["mrio"] = (sum(amt[gi] * mrio_factor[g]
                             for gi, g in enumerate(groups)) / amt.sum())
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
        pv = PRICE_BASE_YEAR[price_base_year]
        wv = REFERENCE_YEAR[reference_year] if ind == "Waste generation (kt)" else 1.0
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


def summarize(totals: dict[str, np.ndarray],
              deterministic: pd.Series) -> pd.DataFrame:
    """Percentiles, moments and Monte Carlo standard error per indicator.

    Parameters
    ----------
    totals : dict of str to numpy.ndarray
        Simulated footprint totals, as returned by :func:`run_mc`.
    deterministic : pandas.Series
        Deterministic total per indicator, for the ``deterministic`` column.

    Returns
    -------
    pandas.DataFrame
        One row per indicator. ``median`` is the reported central value, not
        ``mean``: median-1 multipliers leave the median at the deterministic
        estimate to within 0.5 %, while the mean is inflated (see
        :func:`analytic_moments`). ``mcse_median_pct`` is the standard error
        of the median itself, from twenty equal batches of the draws.
    """
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


def summarize_groups(groups: list[str], group_draws: dict[str, np.ndarray],
                     deterministic_groups: dict[str, pd.Series]
                     ) -> pd.DataFrame:
    """Moments, percentiles and a share interval for every reported group.

    The headline totals have carried a full distribution since the Monte Carlo
    was built. The numbers the manuscript actually *reports* mostly are not the
    headline: they are the contribution groups of figure 1 and table 1, and none
    of them carried an interval. Reviewer 1 asked for "the resulting ranges for
    the main impact estimates", and a range on the total alone does not answer
    that, because a reader cannot infer a group's range from it -- the groups do
    not vary independently. They share the MRIO multiplier, so their ranges are
    strongly correlated and much narrower *relative to each other* than the
    total's range would suggest.

    That correlation is why the share interval is reported alongside the level
    interval. Under the study's default of perfect MRIO correlation, a group that
    is entirely MRIO-driven keeps an almost fixed share while its level moves by
    +/- 16 %: the shared factor cancels in the ratio. The two intervals answer
    two different questions, and reporting only the first would overstate the
    uncertainty on every statement of the form "pharmaceuticals are 37 % of the
    footprint".

    Parameters
    ----------
    groups : list of str
        Contribution-group names, in the column order of ``group_draws``.
    group_draws : dict of str to numpy.ndarray
        Per indicator, an ``(n, len(groups))`` array of group totals, from
        :func:`run_mc`.
    deterministic_groups : dict of str to pandas.Series
        Per indicator, the deterministic group totals, indexed by group.

    Returns
    -------
    pandas.DataFrame
        One row per indicator and group: ``deterministic``, ``median``,
        ``mean``, ``sd``, ``cv_pct``, the 2.5/16/84/97.5 percentiles of the
        level, and ``share_pct`` with its own 2.5/97.5 percentiles.
    """
    rows = []
    for ind, matrix in group_draws.items():
        totals = matrix.sum(axis=1)
        det = deterministic_groups[ind]
        for j, group in enumerate(groups):
            arr = matrix[:, j]
            q = np.percentile(arr, [2.5, 16, 50, 84, 97.5])
            with np.errstate(invalid="ignore", divide="ignore"):
                shares = 100.0 * arr / totals
            sq = np.percentile(shares[np.isfinite(shares)], [2.5, 50, 97.5])
            mean = float(arr.mean())
            rows.append(dict(
                indicator=ind, unit=ind[ind.find("(") + 1:-1], group=group,
                deterministic=float(det.get(group, np.nan)),
                median=q[2], mean=mean, sd=float(arr.std(ddof=1)),
                cv_pct=(100 * float(arr.std(ddof=1)) / mean if mean else np.nan),
                p2_5=q[0], p16=q[1], p84=q[3], p97_5=q[4],
                share_pct=sq[1], share_p2_5=sq[0], share_p97_5=sq[2]))
    return pd.DataFrame(rows)


#: Which PARAMS entry drives each bottom-up component.
_PARAM_OF = {"B_HEAL": "direct", "B_ANAE": "anaesthetic", "B_PMDI": "pmdi",
             "B_COMM": "commute", "B_VISI": "visitor"}


def _sigma(name: str) -> float:
    """Log-scale standard deviation of one parameter's median-1 multiplier."""
    if name == "mrio":
        return float(np.sqrt(np.log(1 + PARAMS["mrio"]["cv"] ** 2)))
    return float(np.log(PARAMS[_PARAM_OF[name]]["gsd"]))


def sigma_for_rho(amounts: np.ndarray, rho: float,
                  target_cv: float | None = None) -> float:
    r"""Log-scale spread that holds the calibrated total CV at a given correlation.

    Parameters
    ----------
    amounts : array_like
        Deterministic amount carried by each contribution group.
    rho : float
        Correlation imposed between the groups' log-factors.
    target_cv : float, optional
        Relative standard deviation the MRIO block must reproduce. Defaults to
        the calibrated value in ``PARAMS["mrio"]["cv"]``.

    Returns
    -------
    float
        :math:`\sigma` such that the block's coefficient of variation equals
        ``target_cv`` under correlation ``rho``.

    Notes
    -----
    This closes an inconsistency that made the correlation sensitivity
    unusable. Applying the same :math:`\sigma` at every :math:`\rho` fixes each
    group's marginal spread and lets the TOTAL's spread fall as the correlation
    falls, so the independence case silently abandoned the calibration target
    and reported an interval roughly half as wide as the evidence supports
    (block CV 4.29 % against the calibrated 8.35 %, the
    ``mrio_block_cv_if_not_recalibrated_pct`` column of
    ``uncertainty_mrio_correlation.csv``). Rodrigues (2016) shows the
    two assumptions - uncorrelated disaggregates and a known aggregate
    uncertainty - are mutually exclusive, and Rodrigues et al. (2018) measure
    the penalty: assuming independence between country accounts understates the
    world account's uncertainty by half.

    Holding the total fixed instead turns :math:`\rho` into what a reader wants
    it to be: a sensitivity on how the variance is DISTRIBUTED across groups,
    not on how much of it there is. The variance of the block is

    .. math::
        \operatorname{Var} = \sum_i \sum_j a_i a_j
        \left(e^{\rho_{ij}\sigma^2} - 1\right) e^{\sigma^2},
        \qquad \rho_{ii} = 1,

    which is monotone in :math:`\sigma`, so a bisection is exact enough.
    """
    a = np.asarray(amounts, dtype=float)
    target = PARAMS["mrio"]["cv"] if target_cv is None else float(target_cv)
    total = a.sum()
    outer = np.outer(a, a)
    eye = np.eye(len(a), dtype=bool)

    def cv(sigma):
        rho_ij = np.full(outer.shape, rho)
        rho_ij[eye] = 1.0
        var = float((outer * (np.exp(rho_ij * sigma ** 2) - 1.0)
                     * np.exp(sigma ** 2)).sum())
        return np.sqrt(var) / total

    lo, hi = 1e-6, 5.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if cv(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def tier1_error_propagation(mrio: pd.DataFrame,
                            parts: dict[str, pd.DataFrame],
                            rho: float = RHO_TRAVEL) -> pd.DataFrame:
    r"""IPCC Tier 1 uncertainty, reported alongside the Tier 2 simulation.

    Parameters
    ----------
    mrio : pandas.DataFrame
        Deterministic MRIO amount per contribution group and indicator.
    parts : dict of str to pandas.DataFrame
        Deterministic bottom-up amount per component, group and indicator.
    rho : float, optional
        Correlation of the travel pair's log-factors.

    Returns
    -------
    pandas.DataFrame
        One row per indicator with the Tier 1 combined uncertainty, in percent
        of the deterministic total.

    Notes
    -----
    IPCC (2000) section 6.3.1 and 6.4.2 both require a Tier 1 result to be
    reported alongside a Tier 2 one, noting it costs "hardly any additional
    effort". Tier 1 combines source-category uncertainties by the
    error-propagation rule for a sum (IPCC eq. 6.3),

    .. math::
        U_{\text{total}} =
        \frac{\sqrt{\sum_i (U_i x_i)^2}}{\sum_i x_i},

    which assumes the terms are uncorrelated and each has a spread below about
    30 % of its mean. Both conditions hold for the bottom-up items; the MRIO
    block is a single term here, so its internal correlation does not enter.
    The covariance of the correlated travel pair is added, since ignoring it
    would make the Tier 1 figure inconsistent with the Tier 2 one for a reason
    that has nothing to do with the tier.

    The per-term variance is the same expression :func:`sobol_first_order` and
    :func:`analytic_moments` use,

    .. math::
        \operatorname{Var}(a_i h_i) =
        a_i^2\left(e^{\sigma_i^2}-1\right)e^{\sigma_i^2},

    because :math:`a_i` is the *median* of the term, not its mean. This module
    used to compute :math:`a_i^2(e^{\sigma_i^2}-1)` here, the variance of a
    lognormal whose mean is :math:`a_i`, so the three closed forms in this
    module disagreed with one another; the climate figure moved from 7.84 % to
    7.90 % when they were reconciled. The residual gap against the Tier 2
    coefficient of variation is now a matter of what each divides by: Tier 1
    normalises on the deterministic total, the reported Tier 2 CV on the
    simulated mean, which sits about 0.84 % above it.
    """
    rows = []
    for ind in INDICATORS:
        terms = [(float(mrio[ind].sum()), _sigma("mrio"))]
        for code in BU_TO_GROUP:
            terms.append((float(parts[code][ind].sum()), _sigma(code)))
        total = sum(a for a, _ in terms)
        var = sum(a ** 2 * (np.exp(s ** 2) - 1) * np.exp(s ** 2)
                  for a, s in terms)
        a_c = float(parts["B_COMM"][ind].sum())
        a_v = float(parts["B_VISI"][ind].sum())
        s_c, s_v = _sigma("B_COMM"), _sigma("B_VISI")
        var += 2.0 * a_c * a_v * np.exp((s_c ** 2 + s_v ** 2) / 2.0) * (
            np.exp(rho * s_c * s_v) - 1.0)
        rows.append(dict(indicator=ind, deterministic=total,
                         tier1_uncertainty_pct=100 * np.sqrt(var) / total
                         if total else np.nan))
    return pd.DataFrame(rows)


def sobol_first_order(mrio: pd.DataFrame, parts: dict[str, pd.DataFrame],
                      pharma_scenario: str = "A",
                      rho: float = RHO_TRAVEL) -> pd.DataFrame:
    r"""Exact variance decomposition of the additive lognormal model.

    Parameters
    ----------
    mrio : pandas.DataFrame
        Deterministic MRIO amount per contribution group and indicator.
    parts : dict of pandas.DataFrame
        Deterministic bottom-up amount per component, group and indicator.
    pharma_scenario : str, optional
        Kept for signature compatibility; the decomposition is taken on the
        central mapping.
    rho : float, optional
        Correlation of the log-factors of commuting and visitor travel.

    Returns
    -------
    pandas.DataFrame
        ``indicator``, ``parameter``, ``variance_share_pct``. Shares sum to
        100 % exactly: the own-variance of each parameter plus one row for the
        covariance the correlated travel pair contributes. Without that row the
        shares would not be a decomposition at all when rho > 0.

    Notes
    -----
    For :math:`F=\sum_j a_j h_j` with :math:`h_j` lognormal of median 1 and
    log-scale SD :math:`\sigma_j`,

    .. math::
        \operatorname{Var}(F)=\sum_j a_j^2 (e^{\sigma_j^2}-1)e^{\sigma_j^2}
        + 2 a_C a_V e^{(\sigma_C^2+\sigma_V^2)/2}(e^{\rho\sigma_C\sigma_V}-1)

    That the shares sum to 100 % is arithmetic - every share is its own term
    over the sum of the same terms - and so is not evidence that the
    decomposition is right. The evidence is the frozen-input comparison in
    :mod:`analysis.uncertainty_audit`, which rebuilds two of these shares from
    the draws and finds the closed form.
    """
    rows = []
    for ind in INDICATORS:
        contrib = {"mrio": float(mrio[ind].sum())}
        for code in BU_TO_GROUP:
            contrib[code] = float(parts[code][ind].sum())
        var = {}
        for name, a in contrib.items():
            sig = _sigma(name)
            var[name] = (a ** 2) * (np.exp(sig ** 2) - 1) * np.exp(sig ** 2)
        a_c, a_v = contrib.get("B_COMM", 0.0), contrib.get("B_VISI", 0.0)
        s_c, s_v = _sigma("B_COMM"), _sigma("B_VISI")
        cov = 2.0 * a_c * a_v * np.exp((s_c ** 2 + s_v ** 2) / 2.0) * (
            np.exp(rho * s_c * s_v) - 1.0)
        var["covariance_commute_visitor"] = float(cov)
        tot = sum(var.values())
        for name, v in var.items():
            rows.append(dict(indicator=ind, parameter=name,
                             variance_share_pct=100 * v / tot if tot else np.nan))
    return pd.DataFrame(rows)


def analytic_moments(mrio: pd.DataFrame, parts: dict[str, pd.DataFrame],
                     rho: float = RHO_TRAVEL) -> dict[str, tuple[float, float]]:
    r"""Closed-form mean and SD of the additive lognormal sum (verification).

    Parameters
    ----------
    mrio : pandas.DataFrame
        Deterministic MRIO amount per contribution group and indicator.
    parts : dict of str to pandas.DataFrame
        Deterministic bottom-up amount per component, group and indicator.
    rho : float, optional
        Correlation of the travel pair's log-factors.

    Returns
    -------
    dict of str to tuple of float
        ``indicator -> (mean, standard deviation)``.

    Notes
    -----
    The mean is :math:`\sum_j a_j e^{\sigma_j^2/2}`, which sits above the
    deterministic total :math:`\sum_j a_j` by the amount every median-1
    lognormal contributes. That inflation is a property of all six
    parameters, not of the MRIO factor alone: for climate it is +0.84 %,
    of which the MRIO factor supplies +0.35 pp and visitor travel, on a much
    smaller amount but a much wider spread, a further +0.32 pp.

    The covariance of the correlated travel pair is included; without it the
    closed form understates the SD and the assertion against the simulation had
    to be loosened rather than being a real check.
    """
    res = {}
    for ind in INDICATORS:
        terms = [(float(mrio[ind].sum()), _sigma("mrio"))]
        for code in BU_TO_GROUP:
            terms.append((float(parts[code][ind].sum()), _sigma(code)))
        mean = sum(a * np.exp(s ** 2 / 2) for a, s in terms)
        var = sum(a ** 2 * (np.exp(s ** 2) - 1) * np.exp(s ** 2) for a, s in terms)
        a_c = float(parts["B_COMM"][ind].sum())
        a_v = float(parts["B_VISI"][ind].sum())
        s_c, s_v = _sigma("B_COMM"), _sigma("B_VISI")
        var += 2.0 * a_c * a_v * np.exp((s_c ** 2 + s_v ** 2) / 2.0) * (
            np.exp(rho * s_c * s_v) - 1.0)
        res[ind] = (mean, np.sqrt(var))
    return res


def ranking_probabilities(groups: list[str],
                          group_draws: dict[str, np.ndarray],
                          top: int = 3) -> pd.DataFrame:
    """Probability that each contribution group takes each of the top ranks.

    Parameters
    ----------
    groups : list of str
        Contribution-group names, in the column order of ``group_draws``.
    group_draws : dict of str to numpy.ndarray
        Per indicator, an ``(n, len(groups))`` array of group totals, ranked
        within each draw so that the shared MRIO factor cancels.
    top : int, optional
        How many ranks to report.

    Returns
    -------
    pandas.DataFrame
        ``indicator``, ``group`` and one ``P_rank_r`` column per rank.
    """
    rows = []
    for ind, G in group_draws.items():
        ranks = (-G).argsort(axis=1).argsort(axis=1)
        for gi, g in enumerate(groups):
            rec = dict(indicator=ind, group=g)
            for r in range(min(top, len(groups))):
                rec[f"P_rank_{r + 1}"] = float((ranks[:, gi] == r).mean())
            rows.append(rec)
    return pd.DataFrame(rows)


def main() -> None:
    """Run every configuration and write the layer's thirteen tables.

    Notes
    -----
    Every table that reports a median or an interval carries its own ``draws``
    and ``seed``, because the layer publishes the same central case from five
    different runs: the headline at 100,000 draws and the sensitivity sweeps
    at 20,000 or 40,000 with their own seeds. Their medians span about 3 kt,
    twice the Monte Carlo standard error of the median, which is the expected
    size; without the two columns a reader comparing two files in this folder
    could only read that as a contradiction.
    """
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

    # The deterministic group totals the draws perturb: the MRIO amount plus
    # every bottom-up component mapped into that group. Built here rather than
    # re-read, so the `deterministic` column of the group table is by
    # construction the same decomposition the simulation starts from.
    det_groups = {ind: (mrio[ind] + sum(part[ind] for part in parts.values()))
                  for ind in mrio.columns}

    summaries, ranks, scen_rows, group_summaries = [], [], [], []
    for scen in ("A", "B"):
        _, G, tot, _ = run_mc(mrio, parts, scen)
        s = summarize(tot, total)
        s.insert(0, "pharma_scenario", scen)
        s["draws"], s["seed"] = N_DRAWS, SEED
        summaries.append(s)
        g = summarize_groups(groups, G, det_groups)
        g.insert(0, "pharma_scenario", scen)
        g["draws"], g["seed"] = N_DRAWS, SEED
        group_summaries.append(g)
        r = ranking_probabilities(groups, G)
        r.insert(0, "pharma_scenario", scen)
        ranks.append(r)
    # structural scenarios on the deterministic model
    for pv in PRICE_BASE_YEAR:
        for wv in REFERENCE_YEAR:
            _, _, tot, _ = run_mc(mrio, parts, "A", price_base_year=pv, reference_year=wv,
                                  n=20_000)
            for ind, arr in tot.items():
                scen_rows.append(dict(price_base_year=pv, reference_year=wv, indicator=ind,
                                      median=float(np.median(arr)),
                                      draws=20_000, seed=SEED))
    # Travel-correlation sensitivity. The rho = 0.8 row IS the study default,
    # so it and the headline describe the same configuration at different draw
    # counts; the draws and seed columns are what lets a reader see that the
    # 3 kt between them is Monte Carlo noise rather than a second answer.
    rho_rows = []
    for rho in (0.0, 0.5, 0.8):
        _, _, tot, _ = run_mc(mrio, parts, "A", rho=rho, n=20_000)
        a = tot["Global warming (ktCO2eq)"]
        q = np.percentile(a, [2.5, 50, 97.5])
        rho_rows.append(dict(rho=rho, median=q[1], p2_5=q[0], p97_5=q[2],
                             cv_pct=100 * a.std(ddof=1) / a.mean(),
                             draws=20_000, seed=SEED))

    # MRIO correlation across contribution groups: the rho = 1 default is a
    # perfect-correlation bound; rho = 0 is the independence bound that
    # Rodrigues et al. (2018) show understates uncertainty; rho = 0.76 is their
    # measured median for country consumption-based accounts.
    # Now that the spread is re-solved at each correlation, the TOTAL interval
    # is held at the calibration and rho is a sensitivity on how the variance is
    # DISTRIBUTED across groups. The group-level CVs are therefore the
    # informative column, not the total. The uncalibrated total is reported
    # alongside so the size of the defect this corrects is visible.
    mrio_rho_rows = []
    for rm, label in ((1.0, "perfect correlation (study default). Rodrigues "
                            "(2016): the only value consistent with holding a "
                            "known aggregate uncertainty"),
                      (0.76, "Rodrigues et al. (2018) measured median "
                             "correlation between country consumption-based "
                             "accounts"),
                      (0.0, "independence. Rodrigues et al. (2018) show this "
                            "understates aggregate uncertainty by about half "
                            "unless the spread is re-solved, as it is here")):
        _, G, tot, _ = run_mc(mrio, parts, "A", rho_mrio=rm, n=40_000, seed=13)
        a = tot["Global warming (ktCO2eq)"]
        q = np.percentile(a, [2.5, 50, 97.5])
        gwp_groups = G["Global warming (ktCO2eq)"]
        group_cv = 100 * gwp_groups.std(axis=0, ddof=1) / gwp_groups.mean(axis=0)
        sig_cal = (np.sqrt(np.log(1 + PARAMS["mrio"]["cv"] ** 2)) if rm >= 1.0
                   else sigma_for_rho(mrio["Global warming (ktCO2eq)"].values, rm))
        sig_flat = np.sqrt(np.log(1 + PARAMS["mrio"]["cv"] ** 2))
        amounts = mrio["Global warming (ktCO2eq)"].values
        outer = np.outer(amounts, amounts)
        rr = np.full(outer.shape, rm); np.fill_diagonal(rr, 1.0)
        cv_uncal = 100 * np.sqrt((outer * (np.exp(rr * sig_flat ** 2) - 1)
                                  * np.exp(sig_flat ** 2)).sum()) / amounts.sum()
        mrio_rho_rows.append(dict(
            rho_mrio=rm, interpretation=label, median=q[1], p2_5=q[0],
            p97_5=q[2], cv_pct=100 * a.std(ddof=1) / a.mean(),
            sigma_used=sig_cal,
            mrio_block_cv_if_not_recalibrated_pct=cv_uncal,
            median_group_cv_pct=float(np.median(group_cv)),
            max_group_cv_pct=float(group_cv.max()),
            draws=40_000, seed=13))
    mrio_rho = pd.DataFrame(mrio_rho_rows)

    # Median-1 lognormal multipliers have mean exp(sigma^2/2) > 1, so the MC
    # mean sits above the deterministic value by construction. This is the
    # inflation of the WHOLE sum, sum_j a_j exp(sigma_j^2/2) over sum_j a_j,
    # not of the MRIO factor alone. The two are different quantities and the
    # difference is not small: the MRIO factor contributes +0.35 %, the sum
    # inflates by +0.84 %, because visitor travel carries a spread wide enough
    # that its own inflation adds a further +0.32 pp on a much smaller amount.
    # Quoting the MRIO factor's figure as the gap between the simulated mean
    # and the deterministic estimate accounted for under half of it.
    _gwp = INDICATORS[0]
    _terms = [(float(mrio[_gwp].sum()), _sigma("mrio"))]
    _terms += [(float(parts[c][_gwp].sum()), _sigma(c)) for c in BU_TO_GROUP]
    mean_inflation = float(sum(a * np.exp(s ** 2 / 2) for a, s in _terms)
                           / sum(a for a, _ in _terms))

    summ = pd.concat(summaries, ignore_index=True)
    rk = pd.concat(ranks, ignore_index=True)
    sob = sobol_first_order(mrio, parts)
    tier1 = tier1_error_propagation(mrio, parts)

    # Variance shares at every correlation, because at rho = 1 the MRIO share is
    # near its maximum by construction and reporting it alone would present an
    # assumption as a finding.
    share_rows = []
    for rm in (1.0, 0.76, 0.0):
        _, G, tot, f = run_mc(mrio, parts, "A", rho_mrio=rm, n=40_000, seed=17)
        arr = tot["Global warming (ktCO2eq)"]
        bu = np.zeros(len(arr))
        for code in BU_TO_GROUP:
            amt = float(parts[code]["Global warming (ktCO2eq)"].sum())
            if amt:
                bu = bu + amt * f[code]
        share_rows.append(dict(
            rho_mrio=rm,
            mrio_variance_share_pct=100 * (1 - float(bu.var(ddof=1))
                                           / float(arr.var(ddof=1))),
            note="frozen-input estimate: the share of output variance that "
                 "disappears when the bottom-up terms alone are varied",
            draws=40_000, seed=17))
    rho_shares = pd.DataFrame(share_rows)

    # The calibration is a CARBON statistic applied to five categories. Schulte
    # et al. (2021), on this database and this resolution, find industry-level
    # footprint CVs above 10 % for carbon but above 30 % for land, material and
    # water. A single carbon-calibrated factor therefore understates the four
    # non-carbon categories, and the size of that understatement is not known.
    # It is reported as a bounding scenario at three times the carbon spread,
    # labelled as a bound rather than an estimate, because no per-category
    # calibration for a national footprint exists to be used instead.
    noncarbon_rows = []
    for mult, label in ((1.0, "carbon calibration applied unchanged (default)"),
                        (3.0, "bound: three times the carbon spread, after the "
                              "carbon-to-other ratio in Schulte et al. (2021) "
                              "industry footprints. NOT an estimate")):
        _, _, tot_nc, _ = run_mc(mrio, parts, "A", n=40_000, seed=23,
                                 cv_target=PARAMS["mrio"]["cv"] * mult)
        for ind, arr in tot_nc.items():
            if ind == "Global warming (ktCO2eq)" and mult != 1.0:
                continue
            q = np.percentile(arr, [2.5, 50, 97.5])
            noncarbon_rows.append(dict(
                indicator=ind, mrio_spread_multiplier=mult, basis=label,
                median=q[1], p2_5=q[0], p97_5=q[2],
                cv_pct=100 * arr.std(ddof=1) / arr.mean(),
                draws=40_000, seed=23))
    noncarbon = pd.DataFrame(noncarbon_rows)

    # IPCC (2000) section 6.4, step 5: a Tier 2 result is converged when the
    # 95 % range is determined to within 1 %. Measured rather than assumed, and
    # measured on every indicator in both pharmaceutical-mapping scenarios. The
    # table used to hold one row - climate, scenario A - while the documents
    # said "the criterion is met at 100,000 draws" without qualification. Ten
    # rows cost one extra run and make that sentence simply true; the four
    # non-carbon indicators and scenario B carry wider spreads, so the one
    # combination that was measured was not the demanding one.
    conv_rows = []
    for scen in ("A", "B"):
        _, _, tot_conv, _ = run_mc(mrio, parts, scen)
        for ind, arr in tot_conv.items():
            halves = [np.percentile(h, [2.5, 97.5])
                      for h in np.array_split(arr, 2)]
            conv = float(np.max(np.abs(halves[0] - halves[1])
                                / np.percentile(arr, [2.5, 97.5])))
            conv_rows.append(dict(
                criterion="IPCC (2000) 6.4 step 5: 95 % range determined to "
                          "within 1 %",
                indicator=ind, pharma_scenario=scen,
                draws=N_DRAWS, seed=SEED,
                max_relative_difference_between_halves_pct=100 * conv,
                passes=bool(conv < 0.01)))
    convergence = pd.DataFrame(conv_rows)

    # Schulte et al. (2026) section 4: where results are correlated, share the
    # full sample, or failing that the covariance matrix. Publishing group
    # medians and spreads alone is the option that paper ranks worst.
    _, G_full, _, _ = run_mc(mrio, parts, "A")
    gwp = G_full["Global warming (ktCO2eq)"]
    # The published sample is (N_DRAWS x 9) float32, kt CO2eq, pharma scenario
    # A, rho = 0.8, rho_mrio = 1.0, seed 42, columns in the order of `groups`.
    # That order is the covariance table's row order, and its key column is
    # named `group` rather than shipped as a blank header, so the .npy's column
    # order is readable from a file rather than inferred. The full
    # specification is in docs/methods/replications.md section 04.
    pd.concat(group_summaries, ignore_index=True).to_csv(
        os.path.join(out_dir, "uncertainty_by_group.csv"), index=False)

    cov = pd.DataFrame(np.cov(gwp, rowvar=False), index=groups, columns=groups)
    cov.to_csv(os.path.join(out_dir, "uncertainty_group_covariance_gwp.csv"),
               index_label="group")
    np.save(os.path.join(out_dir, "uncertainty_group_draws_gwp.npy"),
            gwp.astype(np.float32))
    # z = 1.959964, not 1.96: the columns are named for the 2.5th and 97.5th
    # percentiles and now hold them, rather than the 2.503rd and 97.497th.
    z95 = 1.959963984540054
    par = pd.DataFrame([dict(parameter=k, distribution="lognormal, median 1",
                             gsd=v.get("gsd"), cv=v.get("cv"),
                             factor_2_5pct=(v["gsd"] ** -z95 if v.get("gsd") else
                                            np.exp(-z95 * np.sqrt(np.log(1 + v["cv"] ** 2)))),
                             factor_97_5pct=(v["gsd"] ** z95 if v.get("gsd") else
                                             np.exp(z95 * np.sqrt(np.log(1 + v["cv"] ** 2)))),
                             source=v["why"]) for k, v in PARAMS.items()])
    # Single source of truth for the seven uncertainty_summary sheets: the richer
    # mrio_correlation frame (with its extra mean_over_deterministic_closed_form
    # column) is folded in here rather than written a second time afterwards, so
    # each CSV has exactly one writer and the result no longer depends on
    # statement order.
    write_sheets_as_csv({
        "totals": summ, "variance_shares": sob,
        "ranking_probabilities": rk, "structural_scenarios": pd.DataFrame(scen_rows),
        "travel_correlation": pd.DataFrame(rho_rows),
        "mrio_correlation": mrio_rho.assign(
            mean_over_deterministic_closed_form=mean_inflation),
        "parameters": par,
    }, out_dir, "uncertainty", index=False)
    for name, df in (("uncertainty_tier1_error_propagation", tier1),
                     ("uncertainty_variance_shares_by_correlation", rho_shares),
                     ("uncertainty_convergence", convergence),
                     ("uncertainty_noncarbon_bound", noncarbon)):
        df.to_csv(os.path.join(out_dir, name + ".csv"), index=False)

    print(summ[["pharma_scenario", "indicator", "deterministic", "median", "mean",
                "cv_pct", "p2_5", "p97_5"]].round(2).to_string(index=False))
    print("\nFirst-order variance shares (GWP):")
    print(sob[sob.indicator == INDICATORS[0]].round(2).to_string(index=False))
    print(f"\nMRIO-correlation sensitivity (GWP). Closed-form mean over "
          f"deterministic, all six parameters, "
          f"sum a_j exp(sigma_j^2/2) / sum a_j = {mean_inflation:.5f} "
          f"(+{100 * (mean_inflation - 1):.2f} %):")
    print(mrio_rho[["rho_mrio", "median", "p2_5", "p97_5", "cv_pct"]]
          .round(2).to_string(index=False))
    print("\nTravel-correlation sensitivity (GWP):")
    print(pd.DataFrame(rho_rows).round(2).to_string(index=False))
    print("\nTier 1 (IPCC error propagation), reported alongside Tier 2:")
    print(tier1.round(2).to_string(index=False))
    print("\nMRIO variance share at each correlation:")
    print(rho_shares[["rho_mrio", "mrio_variance_share_pct"]].round(1)
          .to_string(index=False))
    print("\nConvergence:")
    print(convergence.to_string(index=False))
    print("\nNon-carbon categories: default against the three-times bound:")
    print(noncarbon.pivot_table(index="indicator",
                                columns="mrio_spread_multiplier",
                                values="cv_pct").round(2).to_string())


if __name__ == "__main__":
    main()
