# -*- coding: utf-8 -*-
"""Production-layer decomposition (Malik et al. 2021; Lenzen et al. 2020 SI 5).

The Leontief inverse is a convergent series, so a footprint can be split by how
far upstream the pressure occurs:

    L = (I - A)^-1 = I + A + A^2 + ...            (Malik 2021 eq.; Lenzen SI 5)
    f^(n) = diag(s) A^n y                          pressure in layer n, BY NODE
    S_m   = sum_{n<=m} f^(n) / f                   cumulative share
    TE_m  = 1 - S_m                                truncation error at layer m

The diagonalised form is what lets each layer be broken down by the sector in
which the pressure occurs (Malik's Fig. 3); the scalar form q A^n y cannot do
that. Powers of A are never formed: the layer vector is iterated v <- A v.

The residual beyond the last computed layer is closed exactly with
    residual = s . A^(M+1) L y
so the reported layers plus residual sum to the footprint with no truncation
error of our own.

Denmark 2022 cross-check: climate L0-L2 cumulative 67.9 %, against Malik's 67 %
for New South Wales - a genuine cross-study convergence.

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.production_layers
"""

import os
import pickle

import numpy as np
import pandas as pd

from paths import BACKGROUND_DIR, OUTPUT_DIR
from analysis.constants import INDICATORS
from analysis.export_tables import _labels

MAX_LAYER = int(os.environ.get("HC_MAX_LAYER", 20))


def layer_decomposition(A, s, y, max_layer=MAX_LAYER, L=None):
    """Return (layers [max_layer+1 x n] by node, residual scalar)."""
    n = len(y)
    out = np.zeros((max_layer + 1, n))
    v = y.astype(float).copy()
    for m in range(max_layer + 1):
        out[m] = s * v
        v = A @ v
    residual = float(s @ (L @ v)) if L is not None else float(s @ v)
    return out, residual


def main():
    year = os.environ.get("HC_ANALYSIS_YEAR", "2022")
    bgy = "2022" if year == "2022" else "2016"
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{bgy}.pkl"), "rb") as fh:
        bg = pickle.load(fh)
    A, L, B, Ystim, Hstim = bg["A"], bg["L"], bg["B"], bg["Ystim"], bg["Hstim"]
    reg, sec = _labels()
    groups = np.tile(sec["sector_group"].values, len(reg))

    rows, bysec = [], []
    for k, ind, unit in INDICATORS:
        s = B[k, :]
        # The two demand components sit at DIFFERENT points in the chain:
        #   services  y = A[:,h] E_H is ALREADY the first supplier tier, so
        #             s.y is layer 1 and layer 0 is the sector's own direct
        #             impact, taken from national accounts (Hstim);
        #   pharma/appliances  y is a true final demand, so s.y is layer 0.
        # Ignoring the offset shifts one whole layer (it put L0 at 33 % instead
        # of 19 % for climate).
        y_serv = Ystim[:, 1]
        y_goods = Ystim[:, 2] + Ystim[:, 3]
        lay_serv, res_serv = layer_decomposition(A, s, y_serv, L=L)
        lay_goods, res_goods = layer_decomposition(A, s, y_goods, L=L)
        layers = np.zeros((MAX_LAYER + 1, lay_serv.shape[1]))
        layers[0] = lay_goods[0]                      # goods producers' direct
        layers[1:] = lay_serv[:MAX_LAYER] + lay_goods[1:MAX_LAYER + 1]
        totals = layers.sum(axis=1)
        totals[0] += float(Hstim[k, 0])               # health sector's own direct
        residual = res_serv + res_goods
        grand = float(totals.sum() + residual)
        # note: the node-level detail in layers[0] excludes the Hstim term,
        # which has no single producing node (it is a national-accounts total)
        cum = np.cumsum(totals) / grand
        for m in range(len(totals)):
            rows.append(dict(indicator=ind, unit=unit, layer=m, value=totals[m],
                             share_pct=100 * totals[m] / grand,
                             cumulative_share_pct=100 * cum[m],
                             truncation_error_pct=100 * (1 - cum[m])))
        rows.append(dict(indicator=ind, unit=unit, layer=f">{MAX_LAYER}", value=residual,
                         share_pct=100 * residual / grand,
                         cumulative_share_pct=100.0, truncation_error_pct=0.0))
        # layer x sector group (Malik Fig. 3)
        for m in range(len(totals)):
            g = pd.DataFrame({"sector_group": groups, "value": layers[m]})
            gg = g.groupby("sector_group", as_index=False)["value"].sum()
            gg["indicator"] = ind; gg["unit"] = unit; gg["layer"] = m
            bysec.append(gg)
        print(f"  {ind:22s} L0 {100*totals[0]/grand:5.1f} %  L0-L2 "
              f"{100*cum[2]:5.1f} %  L0-L8 {100*cum[8]:5.1f} %  "
              f"TE0 {100*(1-cum[0]):5.1f} %  TE1 {100*(1-cum[1]):5.1f} %")

    out_dir = os.path.join(str(OUTPUT_DIR), "07_malik_replication")
    os.makedirs(out_dir, exist_ok=True)
    meta = dict(analysis_year=year, consuming_country_iso3="DNK",
                model=f"EXIOBASE v3.10.2 IOT_{bgy}_ixi (screened)",
                method="production layer decomposition, Malik et al. 2021 / Lenzen et al. 2020 SI 5")
    df = pd.DataFrame(rows); dfs = pd.concat(bysec, ignore_index=True)
    for k2, v in meta.items():
        df.insert(0, k2, v); dfs.insert(0, k2, v)
    df.to_csv(os.path.join(out_dir, "production_layers.csv"), index=False)
    dfs.to_csv(os.path.join(out_dir, "production_layers_by_sector_group.csv"), index=False)
    print(f"written -> {out_dir}/production_layers.csv (+ by sector group)")


if __name__ == "__main__":
    main()
