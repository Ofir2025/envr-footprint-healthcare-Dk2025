# -*- coding: utf-8 -*-
"""Capital (GFCF) treatment: exclusion, exogenous service flow, endogenisation.

Steenmeijer et al. (2022), like most health-sector footprint studies, exclude
gross fixed capital formation: the Leontief intermediate matrix Z contains only
current inputs, so hospital buildings, scanners and IT systems never enter the
supply chain. Wood & Hertwich (2018) and Södersten et al. (2018) both show this
is the largest single boundary omission for service sectors, whose capital
intensity is high relative to their current purchases.

Three treatments are computed and reported side by side.

  BASELINE  capital excluded. f = C S L y_H.
            What Steenmeijer, Eckelman and the NHS report; the comparable number.

  A         exogenous capital service flow. The annual consumption of fixed
            capital of the Danish health and residential-care industries is
            taken from the national accounts (DST NABK69, P.51c) and footprinted
            as an additional final demand whose commodity composition follows the
            observed Danish health capital asset mix:

                f_A = f + C S L y_cap ,   sum(y_cap) = CFC_health

            CFC, not GFCF, is the right flow for an annual account: it is the
            capital actually consumed in the year, so no asset is charged twice
            over its life. Grounding it in NABK69 rather than in EXIOBASE's own
            CFC row matters, because EXIOBASE understates Danish health CFC
            severalfold (reported in the diagnostics table).

  D         full endogenisation, following Södersten, Wood & Hertwich (2018) and
            the Lenzen-Treloar capital augmentation:

                K[:, j] = g_r(j) * cfc_j / x_j ,  A' = A + K ,
                L' = (I - A')^-1 ,  f_D = C S L' y_net

            where g_r is region r's normalised GFCF commodity vector and y_net is
            final demand with GFCF removed - capital is now intermediate, so
            leaving it in final demand would double count it. This propagates
            capital through every tier of the chain, not just the first, and is
            therefore an upper bound on the capital effect.

Two conventions, so this table can be reconciled with the others
----------------------------------------------------------------
The baseline is the MRIO supply chain plus the sector's own direct impacts. It
deliberately excludes the bottom-up additions (anaesthetic gases, pMDI
propellants, travel), because the capital boundary cannot affect them, so it is
smaller than the study headline by exactly those items.

It also does not subtract the health sector's self-supply loop, which
analysis.scopes_detail does subtract because there it would overlap the
national-accounts scope 1 figure. The two therefore differ by that loop:
3.2 kt on climate and 2.5 kt on waste. Both are correct for their own purpose;
neither is an error.

Run: PYTHONPATH=src .venv/bin/python -m analysis.capital_gfcf
"""

from __future__ import annotations

import csv
import os
import pickle

import numpy as np
import pandas as pd

from analysis.constants import (BACKGROUND_YEAR, DK_POPULATION, INDICATORS,
                                K_DK, MODEL_LABEL, N_FINAL_DEMAND, N_SECTORS)
from paths import BACKGROUND_DIR, BRONZE_DIR, MRIO_DIR, OUTPUT_DIR

FOLDER = "11_capital_gfcf"
ANALYSIS_YEAR = os.environ.get("HC_ANALYSIS_YEAR", "2022")
DKK_PER_EUR = {"2019": 7.4661, "2022": 7.4396}[ANALYSIS_YEAR]
NABK = str(BRONZE_DIR / "dst_capital_stock"
           / "nabk69_health_assets_2022.csv")

IDX_CFC = 5          # V row: 'Operating surplus: Consumption of fixed capital'
COL_GFCF = 3         # Y column within a region: gross fixed capital formation

# Asset (ESA 2010 AN.11 sub-class) -> EXIOBASE product groups. The bridge is
# deliberately coarse and stated in full: within each group the split across
# EXIOBASE products is taken from the region's own GFCF column, so only the
# group weights come from the Danish asset mix.
ASSET_BRIDGE = {
    "Buildings other than dwellings": ["Construction (45)"],
    "Other structures and land improvements": ["Construction (45)"],
    "Dwellings": ["Construction (45)"],
    "Transport equipment": [
        "Manufacture of motor vehicles, trailers and semi-trailers (34)",
        "Manufacture of other transport equipment (35)"],
    "ICT equipment, other machinery and equipment and weapon systems": [
        "Manufacture of office machinery and computers (30)",
        "Manufacture of machinery and equipment n.e.c. (29)",
        "Manufacture of electrical machinery and apparatus n.e.c. (31)",
        "Manufacture of radio, television and communication equipment and "
        "apparatus (32)",
        "Manufacture of medical, precision and optical instruments, watches "
        "and clocks (33)"],
    "Intellectual property products": [
        "Computer and related activities (72)",
        "Research and development (73)",
        "Other business activities (74)"],
    "Cultivated biological resources": ["Cultivation of crops nec"],
}


def _spectral_radius(M: np.ndarray, iters: int = 5000, tol: float = 1e-12) -> float:
    """Largest eigenvalue modulus by power iteration (M is non-negative).

    Reported to enough digits to distinguish A from A': the capital
    augmentation shifts rho only in the fourth decimal, so a loose tolerance
    would print the two as identical and hide whether the model stayed
    productive.

    Parameters
    ----------
    M : numpy.ndarray
        Non-negative square matrix, shape ``(n, n)``.
    iters : int, optional
        Maximum power-iteration steps. Defaults to 5000.
    tol : float, optional
        Convergence tolerance on the estimate's relative change. Defaults to
        ``1e-12``.

    Returns
    -------
    float
        Estimated spectral radius (dominant eigenvalue modulus), or ``0.0``
        if the iterate norm collapses to zero.
    """
    v = np.random.default_rng(0).random(M.shape[0])
    v /= np.linalg.norm(v)
    lam = 0.0
    for _ in range(iters):
        w = M @ v
        nw = np.linalg.norm(w)
        if nw == 0:
            return 0.0
        v = w / nw
        if abs(nw - lam) < tol * max(nw, 1.0):
            break
        lam = nw
    return float(nw)


def _read_nabk() -> tuple[dict[str, float], dict[str, float]]:
    """CFC and GFCF of DK health + residential care by asset, M.EUR.

    Reads ``NABK`` (DST NABK69), converting DKK to M.EUR at ``DKK_PER_EUR``.

    Returns
    -------
    cfc : dict of str to float
        Consumption of fixed capital (P.51c) by asset name, M.EUR.
    gfcf : dict of str to float
        Gross fixed capital formation (P.51g) by asset name, M.EUR.
    """
    cfc, gfcf = {}, {}
    with open(NABK, encoding="utf-8-sig") as fh:
        for row in csv.reader(fh, delimiter=";"):
            if len(row) < 6 or not row[5].strip().lstrip("-").isdigit():
                continue
            target = cfc if row[0].startswith("P.51c") else gfcf
            target[row[1]] = target.get(row[1], 0.0) + float(row[5]) / DKK_PER_EUR
    return cfc, gfcf


def _capital_demand_vector(
    Y: np.ndarray, inds: list[str], asset_cfc: dict[str, float]
) -> tuple[np.ndarray, float]:
    """Spread the health CFC over EXIOBASE products, M.EUR.

    Each asset's CFC is distributed across its ``ASSET_BRIDGE`` product
    group in proportion to Denmark's own GFCF column, so only the group
    weights come from the Danish asset mix.

    Parameters
    ----------
    Y : numpy.ndarray
        Final-demand matrix, shape ``(n_nodes, n_regions * N_FINAL_DEMAND)``.
    inds : list of str
        EXIOBASE industry names, in node order within a region.
    asset_cfc : dict of str to float
        Consumption of fixed capital by asset name, M.EUR (as returned by
        ``_read_nabk``).

    Returns
    -------
    y : numpy.ndarray
        Capital demand vector, shape ``(n_nodes,)``, M.EUR.
    unmapped : float
        CFC, in M.EUR, that could not be placed (asset missing from
        ``ASSET_BRIDGE``, non-positive amount, or a zero-weight product
        group in Denmark's GFCF column).
    """
    gfcf_dk = Y[:, K_DK * N_FINAL_DEMAND + COL_GFCF].astype(float).copy()
    gfcf_dk[gfcf_dk < 0] = 0.0            # inventory-like negatives
    y = np.zeros(Y.shape[0])
    unmapped = 0.0
    for asset, amount in asset_cfc.items():
        prods = ASSET_BRIDGE.get(asset)
        if not prods or amount <= 0:
            unmapped += max(amount, 0.0)
            continue
        idx = [i for i, n in enumerate(inds) if n in prods]
        mask = np.zeros(Y.shape[0], dtype=bool)
        for r in range(Y.shape[0] // N_SECTORS):
            for i in idx:
                mask[r * N_SECTORS + i] = True
        w = gfcf_dk * mask
        if w.sum() <= 0:
            unmapped += amount
            continue
        y += amount * w / w.sum()
    return y, unmapped


def main() -> None:
    """Compute the three capital-boundary scenarios and write them to gold.

    Builds baseline (capital excluded), scenario A (exogenous capital
    service flow from DST NABK69 CFC) and scenario D (full endogenisation,
    Södersten/Wood & Hertwich 2018, with a productivity check on the
    augmented technical matrix) for every indicator in ``INDICATORS``, plus a
    diagnostics table (NABK69 vs. EXIOBASE CFC, spectral radii, inverse
    verification) and the Danish capital asset mix. Writes
    ``capital_scenarios_by_indicator.csv``, ``capital_diagnostics.csv`` and
    ``capital_asset_mix.csv`` to ``data/gold/results/11_capital_gfcf/``, and
    prints the diagnostics and a scenario pivot table. Reads
    ``HC_ANALYSIS_YEAR`` from the environment (default ``"2022"``).

    Raises
    ------
    SystemExit
        If the endogenised technical matrix ``A'`` is not productive
        (spectral radius >= 1).
    """
    out_dir = os.path.join(OUTPUT_DIR, FOLDER)
    os.makedirs(out_dir, exist_ok=True)
    mdir = str(MRIO_DIR) + os.sep

    # the study's own prepared background: same A, L, B, Ystim and Hstim that
    # every other module uses, so the scenarios are strictly comparable
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"),
              "rb") as fh:
        bg = pickle.load(fh)
    A, L, B, Y, Ystim, Hstim = (bg["A"], bg["L"], bg["B"], bg["Y"],
                                bg["Ystim"], bg["Hstim"])
    y_H = Ystim[:, 0]

    with open(f"{mdir}mrio{BACKGROUND_YEAR}.pkl", "rb") as fh:
        m = pickle.load(fh)
    inds = list(m["label"]["industry"]["Name"])
    x, V = m["x"][:, 0], m["V"]

    cfc_assets, gfcf_assets = _read_nabk()
    cfc_total = sum(cfc_assets.values())
    y_cap, unmapped = _capital_demand_vector(Y, inds, cfc_assets)

    # EXIOBASE's own CFC for the Danish health industry, for the comparison
    exio_cfc = float(V[IDX_CFC, K_DK * N_SECTORS + 137])

    # ---- scenario D: endogenise capital in every region ------------------
    cfc_all = V[IDX_CFC, :].astype(float).copy()
    cfc_all[cfc_all < 0] = 0.0
    n_reg = A.shape[0] // N_SECTORS
    K = np.zeros_like(A)
    for r in range(n_reg):
        g = Y[:, r * N_FINAL_DEMAND + COL_GFCF].astype(float).copy()
        g[g < 0] = 0.0
        if g.sum() <= 0:
            continue
        g = g / g.sum()
        cols = slice(r * N_SECTORS, (r + 1) * N_SECTORS)
        coef = np.divide(cfc_all[cols], x[cols],
                         out=np.zeros(N_SECTORS), where=x[cols] > 0)
        K[:, cols] = np.outer(g, coef)
    A_end = A + K
    # Productivity is governed by the spectral radius, not by column sums:
    # EXIOBASE has 72 columns whose sum already exceeds 1 (tiny-output
    # industries and negative value added), yet rho(A) < 1 and L exists.
    rho_base = _spectral_radius(A)
    rho_end = _spectral_radius(A_end)
    if rho_end >= 1.0:
        raise SystemExit(f"augmented matrix is not productive: rho = {rho_end:.4f}")
    L_end = np.linalg.inv(np.eye(A.shape[0]) - A_end)
    # verify the inverse and its non-negativity on a sample of columns
    n = A.shape[0]
    probe = np.random.default_rng(0).choice(n, 12, replace=False)
    eye = np.zeros((n, probe.size))
    eye[probe, np.arange(probe.size)] = 1.0
    err = np.abs(L_end[:, probe] - A_end @ L_end[:, probe] - eye).max()
    neg = float(L_end.min())

    # y_net: capital is intermediate now, so GFCF leaves final demand
    y_H_net = y_H.copy()          # y_H is consumption only; nothing to remove

    rows = []
    for row_idx, name, unit in INDICATORS:
        c = B[row_idx, :]
        direct = float(Hstim[row_idx, 0])          # direct/operational, unchanged
        base = float(c @ (L @ y_H)) + direct
        cap_a = float(c @ (L @ y_cap))
        end = float(c @ (L_end @ y_H)) + direct
        for scen, val, note in (
                ("baseline_capital_excluded", base,
                 "Steenmeijer-comparable; capital outside the boundary"),
                ("A_exogenous_capital_service_flow", base + cap_a,
                 "baseline + CFC of DK health & residential care (DST NABK69)"),
                ("D_full_endogenisation", end,
                 "A' = A + K, Sodersten et al. 2018; upper bound")):
            rows.append(dict(
                country_consuming="DNK", sector_consuming="health_and_eldercare",
                scenario=scen, indicator=name, value=val, unit=unit,
                delta_vs_baseline=val - base,
                pct_vs_baseline=100.0 * (val - base) / base if base else np.nan,
                per_capita=val * 1e6 / DK_POPULATION[ANALYSIS_YEAR]
                if unit.startswith("kt") else np.nan,
                per_capita_unit="kg per capita" if unit.startswith("kt") else "",
                model=MODEL_LABEL, analysis_year=ANALYSIS_YEAR, note=note))
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(out_dir, "capital_scenarios_by_indicator.csv"),
               index=False)

    diag = pd.DataFrame([
        dict(quantity="DK health + residential care, consumption of fixed capital",
             value=cfc_total, unit="M.EUR",
             source="Statistics Denmark NABK69, P.51c, V86000 + V87880, 2022"),
        dict(quantity="DK health + residential care, gross fixed capital formation",
             value=sum(gfcf_assets.values()), unit="M.EUR",
             source="Statistics Denmark NABK69, P.51g"),
        dict(quantity="EXIOBASE CFC, DK health and social work industry",
             value=exio_cfc, unit="M.EUR", source=MODEL_LABEL),
        dict(quantity="ratio national accounts / EXIOBASE CFC",
             value=cfc_total / exio_cfc if exio_cfc else np.nan, unit="-",
             source="derived"),
        dict(quantity="CFC not mapped by the asset bridge", value=unmapped,
             unit="M.EUR", source="derived"),
        dict(quantity="capital demand vector total", value=float(y_cap.sum()),
             unit="M.EUR", source="derived"),
        dict(quantity="spectral radius of A (baseline)", value=float(rho_base),
             unit="-", source="productivity check; must be < 1"),
        dict(quantity="spectral radius of A' (endogenised)", value=float(rho_end),
             unit="-",
             source="productivity check; must be < 1. Note rho barely moves: "
                    "EXIOBASE's dominant eigenvector is concentrated (|v|=0.997) "
                    "on 'Cultivation of paddy rice', a near-unit-column industry "
                    "with no capital coefficient, so rho is not informative about "
                    "the augmentation. The inverse verification below is."),
        dict(quantity="max deviation of (I-A')L' from I, 12 sampled columns",
             value=float(err), unit="-", source="inverse verification"),
        dict(quantity="most negative element of L'", value=neg, unit="-",
             source="must be >= 0 for an economically meaningful inverse"),
    ])
    diag.to_csv(os.path.join(out_dir, "capital_diagnostics.csv"), index=False)

    mix = pd.DataFrame([
        dict(country_consuming="DNK", sector_consuming="health_and_eldercare",
             asset=a, consumption_of_fixed_capital_meur=v,
             share_pct=100 * v / cfc_total,
             exiobase_products="; ".join(ASSET_BRIDGE.get(a, ["UNMAPPED"])),
             unit="M.EUR", source="DST NABK69 P.51c 2022")
        for a, v in sorted(cfc_assets.items(), key=lambda kv: -kv[1])])
    mix.to_csv(os.path.join(out_dir, "capital_asset_mix.csv"), index=False)

    pd.set_option("display.width", 190)
    print(diag.to_string(index=False))
    print()
    print(res[res.indicator == "climate_change"][
        ["scenario", "value", "unit", "delta_vs_baseline",
         "pct_vs_baseline"]].to_string(index=False))
    print()
    print(res.pivot_table(index="indicator", columns="scenario",
                          values="value").round(1).to_string())
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
