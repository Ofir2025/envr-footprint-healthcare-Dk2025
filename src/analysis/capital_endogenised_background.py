# -*- coding: utf-8 -*-
"""Build a capital-endogenised EE-MRIO background, after Södersten et al. (2018).

This is the background stage behind model variant ``d``. It differs from
:mod:`analysis.capital_endogenised_sodersten`, which endogenises capital
*after* the fact for one sensitivity table and leaves the pipeline untouched:
here the augmented technology is written into a background pickle, so
``analysis.main_2025`` and every layer downstream of it run on it exactly as
they run on any other background. The author chose a full pipeline run, and a
post-hoc factor applied to a finished table is not one.

Method
------
Södersten, Wood & Hertwich (2018, *Environ Sci Technol* 52:13250-13259)
endogenise **consumption of fixed capital** - not gross fixed capital
formation, which charges this year's investment to this year's consumption and
is hypersensitive to investment shocks (their SI §4.1.1) - by adding a capital
requirement matrix inside the same Leontief inverse (their eq. 13):

.. math::

   K = \\bar{K}\\hat{x}^{-1}, \\qquad L^{K} = (I - (A + K))^{-1}

Three things this module does that the post-hoc sensitivity does not
------------------------------------------------------------------
1. **The capital flows enter the transaction matrix.** :math:`\\bar{K}` is added
   to :math:`Z`, so :math:`A = (Z + \\bar{K})\\hat{x}^{-1}` is what the pipeline
   loads and what it inverts. The health sector's own capital consumption then
   reaches the demand vector too: ``functions_2025.createBackground`` builds the
   health-care services component as the health column of :math:`Z` scaled to
   Danish expenditure, so with capital outside :math:`Z` the first tier of
   capital - the hospital buildings and scanners themselves - was missing from
   the footprint even when :math:`L^{K}` propagated capital everywhere upstream.

2. **The column balance is preserved.** Endogenising consumption of fixed
   capital moves it out of value added and into intermediate consumption, so the
   same amount is subtracted from the primary-input row that reports it
   (``Operating surplus: Consumption of fixed capital``, row 5 of ``V``).
   :math:`\\sum_i Z_{ij} + \\sum_v V_{vj} = x_j` therefore still holds, exactly,
   and the value-added indicator the model reports becomes value added NET of
   capital consumption - which is what it means once capital is endogenous.

3. **The capital level is the model's own, for the analysis year.** The
   published capital matrices (Zenodo 7073276, CC BY 4.0) stop at 2020 and are
   distributed as ``Kbar_exio_v3_8_2_<year>_cfc_pxi.mat``, a 9,800 x 7,987
   product-by-industry matrix. Its **structure** - which products form which
   industry's capital stock - moves slowly and is carried over; its **level** is
   rescaled, column by column, to the consumption of fixed capital the analysis
   year's own table reports:

   .. math::

      \\bar{K}^{\\mathrm{adj}}_{\\cdot j}
        = \\bar{K}_{\\cdot j}\\,\\frac{V_{\\mathrm{cfc},j}}
                                     {\\sum_i \\bar{K}_{ij}}

   A column with no reported capital consumption, or with none in the published
   matrix, stays zero rather than being invented. The 2020-structure assumption
   is the same one ``analysis.capital_endogenised_sodersten`` records; the
   rescaling is what makes the claim true rather than nominal.

The product-to-industry bridge is :mod:`analysis.capital_endogenised_sodersten`'s
(:func:`~analysis.capital_endogenised_sodersten.load_supply` and
:func:`~analysis.capital_endogenised_sodersten.market_shares`), imported rather
than copied so the two cannot drift: the industry technology construct
:math:`D = V^{\\mathsf{T}}\\hat{q}^{-1}` collapses the 9,800 product rows onto
7,987 industry rows, which is Södersten's own construct applied to the rows
instead of the columns (their SI §1.2).

Run
---
Reads the background selected by ``HC_EXIOBASE_RELEASE`` /
``HC_ANALYSIS_YEAR`` / ``HC_BACKGROUND_TAG`` and writes that stem plus
``_capital``. ``HC_CAPITAL`` must be unset, since this module produces the
endogenised background rather than consuming it::

    HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship PYTHONPATH=src \\
        .venv/bin/python -m analysis.capital_endogenised_background

Then the pipeline runs on it with ``HC_CAPITAL=endogenised``.
"""

from __future__ import annotations

import os
import pickle

import numpy as np
import scipy.io as sio

from analysis.capital_endogenised_sodersten import (CITATION, KBAR_PATH,
                                                    KBAR_YEAR, SUPPLY_PATH,
                                                    load_supply, market_shares)
from analysis.constants import (CAPITAL, EXIOBASE_RELEASE, background_stem,
                                model_label, write_release_sidecar)
from paths import MRIO_DIR

#: Row of ``V`` reporting consumption of fixed capital. Verified against the
#: background's own primary-input labels at run time rather than trusted.
ROW_CFC = 5
CFC_LABEL = "Operating surplus: Consumption of fixed capital"

#: Stem of the background read, and of the one written.
SOURCE_STEM = background_stem(capital="excluded", scope="health_eldercare")
OUTPUT_STEM = f"{SOURCE_STEM}_capital"


def endogenise(kbar_ixi: np.ndarray, cfc: np.ndarray) -> tuple[np.ndarray, float]:
    """Rescale a capital-use matrix to one year's consumption of fixed capital.

    Parameters
    ----------
    kbar_ixi : numpy.ndarray, shape (n, n)
        Capital use by industry, industry by industry, in the published
        reference year's levels.
    cfc : numpy.ndarray, shape (n,)
        Consumption of fixed capital reported by the analysis year's own table,
        one value per industry, in M.EUR.

    Returns
    -------
    tuple of (numpy.ndarray, float)
        The rescaled matrix, and the total capital consumption it carries in
        M.EUR. Columns whose published capital use is zero, or whose reported
        capital consumption is not positive, are returned as zero rather than
        scaled by an undefined factor.
    """
    published = kbar_ixi.sum(axis=0)
    live = (published > 0) & (cfc > 0)
    factor = np.zeros_like(published)
    factor[live] = cfc[live] / published[live]
    scaled = kbar_ixi * factor[np.newaxis, :]
    scaled[:, ~live] = 0.0
    return scaled, float(scaled.sum())


def main() -> None:
    """Write the capital-endogenised background beside the one it augments.

    Reads ``mrio<SOURCE_STEM>.pkl``, adds the rescaled capital-use matrix to
    ``Z``, removes the same amount from the consumption-of-fixed-capital row of
    ``V``, rebuilds ``A`` and its Leontief inverse, and writes
    ``mrio<OUTPUT_STEM>.pkl`` / ``leontief<OUTPUT_STEM>.pkl`` plus the release
    sidecar that records what produced them.

    Raises
    ------
    SystemExit
        If ``HC_CAPITAL`` is set: this module writes the endogenised
        background, so it must be run on the capital-excluded one.
    RuntimeError
        If the primary-input row 5 of the background is not the
        consumption-of-fixed-capital row, if the product-to-industry mapping
        does not conserve capital use, or if the rebuilt inverse does not
        satisfy :math:`L(I - A) = I`.
    """
    if CAPITAL != "excluded":
        raise SystemExit(
            "analysis.capital_endogenised_background writes the _capital "
            f"background itself; run it with HC_CAPITAL unset, not {CAPITAL!r}")

    mdir = str(MRIO_DIR) + os.sep
    print(f"release {EXIOBASE_RELEASE} | {SOURCE_STEM} -> {OUTPUT_STEM}")
    with open(f"{mdir}mrio{SOURCE_STEM}.pkl", "rb") as fh:
        m = pickle.load(fh)

    labels = [str(x) for x in m["label"]["primary"]["Name"]]
    if labels[ROW_CFC] != CFC_LABEL:
        raise RuntimeError(
            f"primary-input row {ROW_CFC} is {labels[ROW_CFC]!r}, expected "
            f"{CFC_LABEL!r}; the capital transfer would hit the wrong account")

    Z, V, x = m["Z"].copy(), m["V"].copy(), m["x"]
    output = np.asarray(x).ravel()
    n = Z.shape[0]

    kbar_pxi = np.asarray(
        sio.loadmat(KBAR_PATH, simplify_cells=True)["Kbar"], dtype=np.float64)
    print(f"Kbar (published, {KBAR_YEAR}, cfc, product x industry): "
          f"{kbar_pxi.shape}, total {kbar_pxi.sum():,.0f} M.EUR")
    shares = market_shares(load_supply(SUPPLY_PATH))
    kbar_ixi = shares @ kbar_pxi
    del shares

    before, after = kbar_pxi.sum(axis=0), kbar_ixi.sum(axis=0)
    live = before > 0
    deviation = float(np.max(np.abs(after[live] - before[live]) / before[live]))
    print(f"column-total conservation, max relative deviation: {deviation:.3e}")
    if deviation > 1e-9:
        raise RuntimeError(
            f"industry-technology mapping did not conserve capital use "
            f"(max relative deviation {deviation:.3e})")
    del kbar_pxi

    cfc = np.asarray(V[ROW_CFC, :], dtype=np.float64).copy()
    capital, total = endogenise(kbar_ixi, cfc)
    del kbar_ixi
    print(f"capital rescaled to the table's own consumption of fixed capital: "
          f"{total:,.0f} M.EUR over {int((capital.sum(axis=0) > 0).sum())} "
          f"industries (reported CFC {float(cfc[cfc > 0].sum()):,.0f} M.EUR)")

    Z += capital
    V[ROW_CFC, :] = cfc - capital.sum(axis=0)
    del capital

    with np.errstate(divide="ignore", invalid="ignore"):
        inverse_output = np.where(output > 0, 1.0 / output, 0.0)
    A = Z * inverse_output[np.newaxis, :]
    residual_col = float(np.max(np.abs(Z.sum(axis=0) + V.sum(axis=0) - output)))
    print(f"max column balance residual after the transfer: {residual_col:.3e} M.EUR")

    L = np.linalg.inv(np.eye(n) - A)
    probe = np.random.default_rng(0).choice(n, 8, replace=False)
    identity = np.zeros((n, probe.size))
    identity[probe, np.arange(probe.size)] = 1.0
    residual = float(np.abs(L[:, probe] - A @ L[:, probe] - identity).max())
    print(f"inverse verification, max deviation from identity: {residual:.3e}")
    if residual > 1e-6:
        raise RuntimeError(f"(I - A)^-1 failed verification at {residual:.3e}")

    m["Z"], m["V"], m["A"] = Z, V, A
    m["release"] = EXIOBASE_RELEASE
    m["source"] = (f"{m.get('source', model_label(SOURCE_STEM))}; capital "
                   f"endogenised by analysis.capital_endogenised_background "
                   f"({CITATION}), {KBAR_YEAR} capital structure rescaled to "
                   f"this table's own consumption of fixed capital")
    with open(f"{mdir}mrio{OUTPUT_STEM}.pkl", "wb") as fh:
        pickle.dump(m, fh)
    with open(f"{mdir}leontief{OUTPUT_STEM}.pkl", "wb") as fh:
        pickle.dump(L, fh)
    write_release_sidecar(mdir, OUTPUT_STEM, EXIOBASE_RELEASE, str(m["source"]))
    print(f"background -> mrio{OUTPUT_STEM}.pkl, leontief{OUTPUT_STEM}.pkl")


if __name__ == "__main__":
    main()
