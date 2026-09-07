# -*- coding: utf-8 -*-
"""Capital endogenisation after Södersten et al. (2018), on the ixi model.

This replaces the study's simplified capital construction with the published
method and the published capital-use matrices.

Method
------
Södersten, Wood & Hertwich (2018, *Environ Sci Technol* 52:13250-13259) endogenise
capital by adding a capital requirement matrix to the direct requirements matrix
inside the same Leontief inverse::

    K = K̄ x̂⁻¹
    L^K = (I − (A + K))⁻¹                                   (their eq. 13)

They endogenise **consumption of fixed capital**, not gross fixed capital
formation, because gross formation charges this year's investment to this year's
consumption and is hypersensitive to investment shocks (their SI §4.1.1).

The bridge this module supplies
-------------------------------
The published capital matrices (Zenodo 7073276, CC BY 4.0) are distributed as
``Kbar_exio_v3_8_2_<year>_cfc_pxi.mat``: a 9,800 × 7,987 matrix of capital
*products* used by *industries*. This study runs the industry-by-industry table,
which needs a 7,987 × 7,987 matrix, so the product rows must be mapped onto
industry rows.

Södersten do exactly this in the opposite direction — their SI §1.2 states they
convert "from our 9800-by-7987 capital transaction matrix to a symmetric
9800-by-9800 capital flow matrix K" by applying "the industry technology
construct ... to conform with the way the A matrix is constructed". The same
construct, applied to the rows rather than the columns, gives the industry-by-
industry form::

    q_p  = Σ_i V[p, i]                    total output of product p
    D    = Vᵀ q̂⁻¹                        industry × product market shares
    K̄_ixi = D K̄_pxi                       9,800 rows collapsed to 7,987

``D`` is naturally block diagonal by region, because a supply table records no
foreign industry supplying a domestic product. The supply matrix ``V`` comes from
the EXIOBASE v3.8.2 ``MRSUT_<year>`` release, which is published alongside the
input-output tables.

Because each column of ``D`` sums to one, total capital use by industry is
conserved by the mapping. That is asserted, not assumed.

Data vintages
-------------
The published capital matrices stop at 2020 and the study year is 2022. Capital
*structure* — which products form the capital stock of which industry — moves
slowly, whereas capital *level* is taken from the model's own consumption of
fixed capital for the analysis year. The 2020 structure is therefore applied to
2022 levels, and the assumption is recorded in the output.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.capital_endogenised_sodersten``
"""

from __future__ import annotations

import os
import pickle
from typing import Any

import numpy as np
import pandas as pd
import scipy.io as sio

from analysis.constants import (ANALYSIS_YEAR, BACKGROUND_YEAR, DK_POPULATION,
                                INDICATORS, MODEL_LABEL)
from analysis.detail_tables import detail_rows, domestic_import_split
from paths import BACKGROUND_DIR, OUTPUT_DIR

FOLDER = "11_capital_gfcf"
KBAR_YEAR = 2020
KBAR_PATH = f"data/bronze/capital/Kbar_exio_v3_8_2_{KBAR_YEAR}_cfc_pxi.mat"
SUPPLY_PATH = ("/Users/kwametutu/Library/CloudStorage/OneDrive-Personal/Data/"
               f"lca/input_output/mrio/exiobase/versions/v3_8_2/"
               f"MRSUT_{KBAR_YEAR}/supply.csv")

CITATION = ("Södersten, Wood & Hertwich (2018) Environ Sci Technol "
            "52:13250-13259, doi 10.1021/acs.est.8b02791; capital matrices "
            "Zenodo 10.5281/zenodo.7073276, CC BY 4.0")


def load_supply(path: str) -> np.ndarray:
    """Load the EXIOBASE supply matrix as products × industries.

    Parameters
    ----------
    path : str
        Path to ``supply.csv`` from an ``MRSUT_<year>`` release.

    Returns
    -------
    numpy.ndarray, shape (9800, 7987)
        Supply of each product by each industry, in M.EUR.

    Raises
    ------
    RuntimeError
        If the parsed shape is not the expected 9,800 × 7,987.
    """
    # Three header rows (region, sector, code) and two index columns
    # (region, product name). The dtype must not be applied to the index
    # columns, so they are skipped by position instead of parsed and dropped.
    frame = pd.read_csv(path, sep="\t", skiprows=3, header=None,
                        usecols=range(2, 2 + 7987), dtype=np.float64,
                        engine="c")
    supply = frame.to_numpy(dtype=np.float64, copy=False)
    if supply.shape != (9800, 7987):
        raise RuntimeError(
            f"supply matrix is {supply.shape}, expected (9800, 7987); the "
            "MRSUT layout may have changed")
    return supply


def market_shares(supply: np.ndarray) -> np.ndarray:
    """Industry × product market-share matrix under the industry-technology construct.

    Parameters
    ----------
    supply : numpy.ndarray, shape (n_products, n_industries)
        Supply matrix.

    Returns
    -------
    numpy.ndarray, shape (n_industries, n_products)
        ``D[i, p]`` is the share of product *p* supplied by industry *i*.
        Columns sum to one wherever the product has output, and to zero
        otherwise.
    """
    product_output = supply.sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        inverse = np.where(product_output > 0, 1.0 / product_output, 0.0)
    return (supply * inverse[:, np.newaxis]).T


def main() -> None:
    """Endogenise capital and write the comparison to the gold folder."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"),
              "rb") as fh:
        bg = pickle.load(fh)
    A, L, B, Ystim, Hstim = bg["A"], bg["L"], bg["B"], bg["Ystim"], bg["Hstim"]

    kbar_pxi = np.asarray(
        sio.loadmat(KBAR_PATH, simplify_cells=True)["Kbar"], dtype=np.float64)
    print(f"Kbar (published, {KBAR_YEAR}, cfc, product x industry): "
          f"{kbar_pxi.shape}, total {kbar_pxi.sum():,.0f} M.EUR")

    supply = load_supply(SUPPLY_PATH)
    shares = market_shares(supply)
    print(f"supply matrix {supply.shape}; market shares {shares.shape}")

    kbar_ixi = shares @ kbar_pxi
    del supply, shares

    # Conservation: each column of D sums to one, so total capital used by an
    # industry must survive the mapping. Assert rather than assume.
    before = kbar_pxi.sum(axis=0)
    after = kbar_ixi.sum(axis=0)
    live = before > 0
    deviation = float(np.max(np.abs(after[live] - before[live]) / before[live]))
    print(f"column-total conservation, max relative deviation: {deviation:.3e}")
    if deviation > 1e-9:
        raise RuntimeError(
            f"industry-technology mapping did not conserve capital use "
            f"(max relative deviation {deviation:.3e})")
    del kbar_pxi

    # K = Kbar xhat^-1, then L^K = (I - (A + K))^-1
    output = bg.get("x")
    if output is None:
        from paths import MRIO_DIR
        with open(os.path.join(str(MRIO_DIR),
                               f"mrio{BACKGROUND_YEAR}.pkl"), "rb") as fh:
            output = pickle.load(fh)["x"][:, 0]
    output = np.asarray(output).ravel()
    with np.errstate(divide="ignore", invalid="ignore"):
        inverse_output = np.where(output > 0, 1.0 / output, 0.0)
    capital = kbar_ixi * inverse_output[np.newaxis, :]
    del kbar_ixi

    augmented = A + capital
    leontief_k = np.linalg.inv(np.eye(A.shape[0]) - augmented)

    probe = np.random.default_rng(0).choice(A.shape[0], 8, replace=False)
    identity = np.zeros((A.shape[0], probe.size))
    identity[probe, np.arange(probe.size)] = 1.0
    residual = float(np.abs(leontief_k[:, probe]
                            - augmented @ leontief_k[:, probe]
                            - identity).max())
    print(f"inverse verification, max deviation from identity: {residual:.3e}")

    population = DK_POPULATION[ANALYSIS_YEAR]
    rows: list[dict[str, Any]] = []
    node_frames: list[pd.DataFrame] = []
    for k, indicator, unit in INDICATORS:
        direct = float(Hstim[k, 0])
        baseline = float(B[k] @ (L @ Ystim[:, 0])) + direct
        endogenised = float(B[k] @ (leontief_k @ Ystim[:, 0])) + direct
        rows.append(dict(
            country_consuming="DNK", sector_consuming="health_and_eldercare",
            analysis_year=ANALYSIS_YEAR, indicator=indicator, unit=unit,
            baseline_capital_excluded=baseline,
            endogenised_sodersten=endogenised,
            change=endogenised - baseline,
            change_pct=100 * (endogenised - baseline) / baseline,
            per_capita_endogenised=endogenised * 1e3 / population
            if unit.startswith("kt") else np.nan,
            method=CITATION, kbar_year=KBAR_YEAR,
            structure_assumption=f"{KBAR_YEAR} capital structure applied to "
                                 f"{ANALYSIS_YEAR} levels; capital composition "
                                 "moves slowly, capital level comes from the "
                                 "model's own consumption of fixed capital",
            model=MODEL_LABEL))
        if indicator == "climate_change":
            node_frames.append(detail_rows(
                B[k] * (leontief_k @ Ystim[:, 0]),
                country_consuming="DNK", indicator=indicator, unit=unit,
                treatment="capital endogenised (Sodersten et al. 2018)",
                model=MODEL_LABEL))

    table = pd.DataFrame(rows)
    table.to_csv(os.path.join(out_dir, "capital_endogenised_sodersten.csv"),
                 index=False)
    detail = pd.concat(node_frames, ignore_index=True)
    detail.to_csv(os.path.join(
        out_dir, "capital_endogenised_by_producing_node.csv.gz"),
        index=False, compression="gzip")
    domestic_import_split(detail).to_csv(
        os.path.join(out_dir, "capital_endogenised_domestic_vs_imported.csv"),
        index=False)

    pd.set_option("display.width", 190)
    print()
    print(table[["indicator", "unit", "baseline_capital_excluded",
                 "endogenised_sodersten", "change_pct"]]
          .round(2).to_string(index=False))
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
