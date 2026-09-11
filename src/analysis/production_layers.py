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

Denmark 2022 against Malik et al. (2021) NSW, cumulative share of the first
three production layers: climate 63.0 % against their 67 %, waste 88.0 %
against 90 %, blue water 57.0 % against 72 %. The water gap is expected -
their water is an unqualified physical volume, ours is blue water
consumption. Regenerate with this module; the comparison is written to
production_layers_vs_malik.csv.

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.production_layers
"""

import os
import pickle

import numpy as np
import pandas as pd

from paths import BACKGROUND_DIR, OUTPUT_DIR
from analysis.constants import (BACKGROUND_YEAR, INDICATORS, MODEL_LABEL,
                                NODE_DK_HEALTH)
from analysis.detail_tables import detail_rows, domestic_import_split

# ---------------------------------------------------------------------------
# Malik et al. (2021), NSW health system, for comparison.
#
# Their layer definition, verbatim: "we consider the first layer to be direct
# q_GHG I y, the second layer (q_GHG A y) as the suppliers of the health
# sectors, third layer (q_GHG A^2 y) suppliers' of suppliers". Their "first
# three production layers" are therefore L0 + L1 + L2 in the zero-indexed
# notation used here, and their figure 3 x-axis 1...8 is L0...L7.
#
# Verbatim result: "accounting for not just the direct activities but also the
# activities of direct suppliers, and the suppliers of those direct suppliers
# (first three production layers, Fig. 3) explains the vast majority of impacts
# (nearly 67% of GHG emissions, 72% water emissions, and 90% of waste)."
#
# Boundary caution: Malik et al. 2021 exclude capital AND imports entirely
# ("the results do not consider imports and investments by the health
# sectors"), and their water is a physical volume never stated to be withdrawal
# or consumptive use. Their waste share uses a 2011 denominator against a 2017
# numerator. The layer SHARES are the comparable quantity; the levels are not.
# ---------------------------------------------------------------------------
MALIK_LAYER_REFERENCE = {
    "climate_change": dict(first_three_layers_pct=67.0, first_layer_pct=11.0,
                           unit="kt CO2e", total=7908.0),
    "blue_water_consumption": dict(first_three_layers_pct=72.0,
                                   first_layer_pct=17.0, unit="GL",
                                   total=246.0),
    "waste_generation": dict(first_three_layers_pct=90.0,
                             first_layer_pct=62.0, unit="kt", total=1624.0),
}
from analysis.export_tables import _labels

MAX_LAYER = int(os.environ.get("HC_MAX_LAYER", 20))


def layer_decomposition(
    A: np.ndarray,
    s: np.ndarray,
    y: np.ndarray,
    max_layer: int = MAX_LAYER,
    L: np.ndarray | None = None,
) -> tuple[np.ndarray, float]:
    """Decompose a footprint into production layers ``diag(s) A^n y``.

    Iterates ``v <- A v`` rather than forming powers of ``A``, so each layer's
    node-level pressure is exact and no dense matrix power is ever computed.

    Parameters
    ----------
    A : numpy.ndarray
        Technical coefficient matrix, shape ``(n, n)``.
    s : numpy.ndarray
        Per-node stressor intensity row for one indicator, shape ``(n,)``, in
        the indicator's native unit per M.EUR of output.
    y : numpy.ndarray
        Final-demand vector, shape ``(n,)``, in M.EUR.
    max_layer : int, optional
        Highest layer index to compute explicitly (layers ``0..max_layer``).
        Defaults to ``MAX_LAYER`` (``HC_MAX_LAYER``, default 20).
    L : numpy.ndarray or None, optional
        Leontief inverse, shape ``(n, n)``. When given, the residual beyond
        ``max_layer`` is closed exactly as ``s @ (L @ v)``; when ``None`` the
        residual is only ``s @ v`` for the final iterate.

    Returns
    -------
    layers : numpy.ndarray
        Array of shape ``(max_layer + 1, n)``, layer ``m`` by producing node,
        in the indicator's native unit.
    residual : float
        Pressure beyond ``max_layer``, in the same unit, so that
        ``layers.sum() + residual`` equals the full footprint.
    """
    n = len(y)
    out = np.zeros((max_layer + 1, n))
    v = y.astype(float).copy()
    for m in range(max_layer + 1):
        out[m] = s * v
        v = A @ v
    residual = float(s @ (L @ v)) if L is not None else float(s @ v)
    return out, residual


def main() -> None:
    """Decompose the footprint by production layer and compare against Malik.

    For each of the five ``INDICATORS``, splits the healthcare footprint into
    layers 0..``MAX_LAYER`` plus an exact residual (accounting for the
    services-vs-goods layer offset described in the module docstring, and the
    health sector's own direct impact from ``Hstim``), by producing node and
    by sector group. Writes ``production_layers.csv``,
    ``production_layers_by_producing_node.csv.gz``,
    ``production_layers_domestic_vs_imported.csv`` and
    ``production_layers_by_sector_group.csv`` to
    ``data/gold/results/20_production_layers/``, and
    ``production_layers_vs_malik.csv`` (cumulative first-three/first-layer
    shares against ``MALIK_LAYER_REFERENCE``) to
    ``data/gold/results/07_malik_replication/``. Reads ``HC_ANALYSIS_YEAR``
    from the environment (default ``"2022"``) and ``HC_BACKGROUND_TAG`` via
    ``BACKGROUND_YEAR`` to select the background pickle.
    """
    year = os.environ.get("HC_ANALYSIS_YEAR", "2022")
    bgy = BACKGROUND_YEAR  # honours HC_BACKGROUND_TAG
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{bgy}.pkl"), "rb") as fh:
        bg = pickle.load(fh)
    A, L, B, Ystim, Hstim = bg["A"], bg["L"], bg["B"], bg["Ystim"], bg["Hstim"]
    reg, sec = _labels()
    groups = np.tile(sec["sector_group"].values, len(reg))

    rows, bysec, node_frames = [], [], []
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
        # layer x producing node. The health sector's own direct impact has a
        # producing node - the Danish health industry itself - so it is placed
        # there rather than dropped, which lets the node detail reconcile with
        # the layer totals exactly.
        layers_detail = layers.copy()
        layers_detail[0, NODE_DK_HEALTH] += float(Hstim[k, 0])
        for m in range(len(totals)):
            if not np.any(layers_detail[m]):
                continue
            node_frames.append(detail_rows(
                layers_detail[m], country_consuming="DNK",
                sector_consuming="health_and_eldercare",
                analysis_year=year, indicator=ind, unit=unit, layer=m,
                model=MODEL_LABEL))

        # layer x sector group (Malik Fig. 3)
        for m in range(len(totals)):
            g = pd.DataFrame({"sector_group": groups, "value": layers[m]})
            gg = g.groupby("sector_group", as_index=False)["value"].sum()
            gg["indicator"] = ind; gg["unit"] = unit; gg["layer"] = m
            bysec.append(gg)
        print(f"  {ind:22s} L0 {100*totals[0]/grand:5.1f} %  L0-L2 "
              f"{100*cum[2]:5.1f} %  L0-L8 {100*cum[8]:5.1f} %  "
              f"TE0 {100*(1-cum[0]):5.1f} %  TE1 {100*(1-cum[1]):5.1f} %")

    out_dir = os.path.join(str(OUTPUT_DIR), "20_production_layers")
    os.makedirs(out_dir, exist_ok=True)
    malik_dir = os.path.join(str(OUTPUT_DIR), "07_malik_replication")
    os.makedirs(malik_dir, exist_ok=True)
    meta = dict(analysis_year=year, consuming_country_iso3="DNK",
                model=MODEL_LABEL,
                method="production layer decomposition, Malik et al. 2021 / Lenzen et al. 2020 SI 5")
    df = pd.DataFrame(rows); dfs = pd.concat(bysec, ignore_index=True)
    for k2, v in meta.items():
        df.insert(0, k2, v); dfs.insert(0, k2, v)
    df.to_csv(os.path.join(out_dir, "production_layers.csv"), index=False)
    if node_frames:
        node_detail = pd.concat(node_frames, ignore_index=True)
        node_detail.to_csv(
            os.path.join(out_dir,
                         "production_layers_by_producing_node.csv.gz"),
            index=False, compression={"method": "gzip", "mtime": 0})
        domestic_import_split(
            node_detail, by=("indicator", "unit", "layer")).to_csv(
            os.path.join(out_dir,
                         "production_layers_domestic_vs_imported.csv"),
            index=False)
        print(f"  node detail: {len(node_detail):,} rows "
              f"({node_detail.layer.nunique()} layers x "
              f"{node_detail.indicator.nunique()} indicators)")

    # explicit comparison against Malik et al. (2021), shares only
    comparison = []
    for indicator, published in MALIK_LAYER_REFERENCE.items():
        subset = df[df.indicator == indicator]
        if subset.empty:
            continue
        ours_three = float(subset[subset.layer == 2]["cumulative_share_pct"]
                           .iloc[0])
        ours_first = float(subset[subset.layer == 0]["cumulative_share_pct"]
                           .iloc[0])
        comparison.append(dict(
            indicator=indicator,
            denmark_first_three_layers_pct=ours_three,
            malik_nsw_first_three_layers_pct=published["first_three_layers_pct"],
            denmark_first_layer_pct=ours_first,
            malik_nsw_first_layer_pct=published["first_layer_pct"],
            malik_total=published["total"], malik_unit=published["unit"],
            layer_definition="Malik's 'first three production layers' are "
                             "L0 + L1 + L2 here; their figure 3 axis 1..8 is "
                             "L0..L7",
            comparability="shares are comparable; levels are not - Malik et "
                          "al. 2021 exclude capital and imports entirely, and "
                          "their water is an unqualified physical volume",
            source_malik="Malik et al. 2021, Lancet Planet Health 5:e e-pub, "
                         "section 3 and figure 3",
            source_denmark=MODEL_LABEL))
    pd.DataFrame(comparison).to_csv(
        os.path.join(malik_dir, "production_layers_vs_malik.csv"), index=False)
    dfs.to_csv(os.path.join(out_dir, "production_layers_by_sector_group.csv"), index=False)
    print(f"written -> {out_dir}/production_layers.csv (+ by sector group)")


if __name__ == "__main__":
    main()
