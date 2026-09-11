# -*- coding: utf-8 -*-
"""Target-sector scope 3 without double counting (Cabernard et al. 2019, 2022).

Two DIFFERENT questions must not be confused:

(a) FINAL-DEMAND footprint - what the headline results answer:
        f = d L y_H
    Each emission is allocated once to Danish healthcare final demand. This is
    additive and does not double count, for any number of target nodes
    (Wood & Hertwich 2018 p.5: allocating production emissions to final demand
    sums to the total; the embodied-flow table E_Z does not).

(b) TARGET-SECTOR scope 3 - "what is the scope 3 of the health sector-regions
    themselves?", the question Cabernard et al. answer. Here the naive form
        e_T = d L[:,T] diag(x_T)                                   (their eq. 8)
    DOES double count, because every delivery from one target node to another
    is counted for the supplying target and again for the receiving target.
    The corrected form replaces gross output x_T with output net of
    target-to-target deliveries:
        q_T      = rowsum( Y[T,:] + A[T,O] L'_OO Y[O,:] )
        e_T,wdc  = d L[:,T] diag(q_T)                              (their eq. 9)
        f_T      = (e_T - e_T,wdc) / e_T                           (their eq. 12)
    with L'_OO = (I_OO - A[O,O])^-1 over the non-target economy.

This module quantifies (b) for three nested target definitions, so the size of
the effect for a healthcare study is measured rather than asserted:

    T1  Danish health and social work                    (1 node)
    T2  health and social work in all 49 regions        (49 nodes)
    T3  T2 + Chemicals nec + Medical precision instruments in all regions
                                                        (147 nodes)

It also verifies Cabernard et al. (2022) SI's complement identity
    d L Y.sum(1) == e_T,wdc.sum() + d[O] L'_OO Y[O,:].sum(1)
which is an exact accounting identity, not an approximation.

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.cabernard_target_scope3
"""

import os
import pickle

import numpy as np
import pandas as pd

from analysis.constants import BACKGROUND_YEAR, MODEL_LABEL
from analysis.detail_tables import detail_rows, domestic_import_split
from paths import BACKGROUND_DIR, MRIO_DIR, OUTPUT_DIR

NS, NR, K_DK, K_HEALTH, K_CHEM, K_INSTR = 163, 49, 6, 137, 62, 89


def main() -> None:
    """Quantify Cabernard target-sector scope 3 double counting for T1/T2/T3.

    For each of the three nested target definitions (module docstring),
    computes the naive target scope 3 (eq. 8), the double-counting-corrected
    version (eq. 9), the double-counting factor ``f_T`` (eq. 12) and the SI
    complement-identity relative deviation, in kt/Mt CO2-equivalent. Writes
    the summary to
    ``data/gold/results/03_cabernard_target_scope3/cabernard_target_scope3.csv``,
    the producing-node decomposition to
    ``cabernard_target_scope3_by_producing_node.csv.gz``, and the
    domestic/imported split to ``cabernard_domestic_vs_imported.csv``, all
    under the same folder. The background actually loaded is
    ``analysis.constants.BACKGROUND_YEAR``, which carries both
    ``HC_ANALYSIS_YEAR`` and ``HC_BACKGROUND_TAG``, so a model variant
    selected on the command line reaches this layer rather than being
    silently replaced by the uncorrected background.
    """
    year = os.environ.get("HC_ANALYSIS_YEAR", "2022")
    bgy = BACKGROUND_YEAR
    with open(os.path.join(str(MRIO_DIR), f"mrio{bgy}.pkl"), "rb") as fh:
        m = pickle.load(fh)
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{bgy}.pkl"), "rb") as fh:
        bg = pickle.load(fh)
    A, Y, x, L, d = m["A"], m["Y"], m["x"][:, 0], bg["L"], bg["B"][0, :]
    n = len(x)

    targets = {
        "T1 Danish health and social work": [K_DK * NS + K_HEALTH],
        "T2 health and social work, all regions": [r * NS + K_HEALTH for r in range(NR)],
        "T3 T2 + chemicals + medical instruments, all regions":
            [r * NS + K_HEALTH for r in range(NR)]
            + [r * NS + K_CHEM for r in range(NR)]
            + [r * NS + K_INSTR for r in range(NR)],
    }

    rows, node_frames = [], []
    y_glob = Y.sum(axis=1)
    total_global = float(d @ (L @ y_glob))
    for name, T in targets.items():
        T = np.array(sorted(T))
        O = np.setdiff1d(np.arange(n), T)
        # eq. 8: naive target scope 3 (gross output)
        e_T = float(d @ (L[:, T] @ x[T]))
        # eq. 9: corrected - output net of target-to-target deliveries
        L_OO = np.linalg.inv(np.eye(len(O)) - A[np.ix_(O, O)])
        q_T = (Y[T, :] + A[np.ix_(T, O)] @ (L_OO @ Y[O, :])).sum(axis=1)
        e_wdc = float(d @ (L[:, T] @ q_T))
        # Cabernard 2022 SI complement identity
        e_O_only = float(d[O] @ (L_OO @ Y[O, :].sum(axis=1)))
        ident_dev = abs(total_global - (e_wdc + e_O_only)) / total_global
        # Where the corrected target scope 3 physically occurs. e_wdc is a
        # scalar contraction of d over the node vector L[:, T] @ q_T, so that
        # vector IS the producing-node decomposition and sums back exactly.
        by_node = d * (L[:, T] @ q_T)
        node_frames.append(detail_rows(
            by_node, country_consuming="DNK", target_set=name,
            n_target_nodes=len(T), indicator="climate_change",
            unit="kt CO2eq", model=MODEL_LABEL,
            quantity="corrected target scope 3 (Cabernard eq. 9), by producing node"))
        rows.append(dict(
            target=name, n_target_nodes=len(T),
            e_T_naive_MtCO2e=e_T / 1e3, e_T_wdc_MtCO2e=e_wdc / 1e3,
            double_counting_factor_f_T=(e_T - e_wdc) / e_T if e_T else np.nan,
            overestimate_vs_correct_pct=100 * (e_T - e_wdc) / e_wdc if e_wdc else np.nan,
            complement_identity_rel_dev=ident_dev))
        del L_OO
        print(f"{name}: |T|={len(T)}  naive {e_T/1e3:,.1f} Mt  corrected {e_wdc/1e3:,.1f} Mt "
              f" f_T={(e_T-e_wdc)/e_T:.3f}  identity dev={ident_dev:.2e}")

    df = pd.DataFrame(rows)
    df.insert(0, "analysis_year", year)
    df["note"] = ("target-perspective scope 3 (Cabernard et al. 2019 eqs. 8/9/12). "
                  "The study's HEADLINE result is a final-demand footprint and is "
                  "unaffected by this correction.")
    out = os.path.join(str(OUTPUT_DIR), "03_cabernard_target_scope3", "cabernard_target_scope3.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)
    if node_frames:
        node_detail = pd.concat(node_frames, ignore_index=True)
        node_detail.to_csv(
            os.path.join(os.path.dirname(out),
                         "cabernard_target_scope3_by_producing_node.csv.gz"),
            index=False, compression={"method": "gzip", "mtime": 0})
        domestic_import_split(
            node_detail, by=("target_set", "indicator", "unit")).to_csv(
            os.path.join(os.path.dirname(out),
                         "cabernard_domestic_vs_imported.csv"), index=False)
        print(f"  node detail: {len(node_detail):,} rows across "
              f"{node_detail.target_set.nunique()} target sets")
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
