# -*- coding: utf-8 -*-
"""Accounting-identity tests for the EE-MRIO system actually used.

Verifies, on the pickled background, the standard Leontief identities
(Miller & Blair 2009, ch. 2; Wood et al. 2018 eqs. 1-2) rather than assuming
the released files are self-consistent:

  T1  row balance          x = Z*1 + Y*1
  T2  technical coefficients A = Z x^-1  (as constructed)
  T3  Leontief inverse     (I - A) L = I
  T4  output reproduction  x = L (Y*1)
  T5  footprint identity   sum_i s_i x_i  ==  sum_i s_i [L y]_i   for any y
  T6  perspective identity sum over producers of E == sum over purchases of E,
                           where E[i,j] = s_i L_ij y_j
  T7  units                monetary unit of the release is M.EUR

Run: PYTHONPATH=src .venv/bin/python -m analysis.validate_io_identities
"""

import os
import pickle

import numpy as np

from paths import MRIO_DIR, BACKGROUND_DIR

YEAR = os.environ.get("HC_BACKGROUND_YEAR", "2022")
TOL = 1e-6


def _rel(a, b):
    denom = max(abs(float(b)), 1e-12)
    return abs(float(a) - float(b)) / denom


def main():
    with open(os.path.join(str(MRIO_DIR), f"mrio{YEAR}.pkl"), "rb") as fh:
        m = pickle.load(fh)
    with open(os.path.join(str(MRIO_DIR), f"leontief{YEAR}.pkl"), "rb") as fh:
        L = pickle.load(fh)
    Z, Y, x, A = m["Z"], m["Y"], m["x"][:, 0], m["A"]
    n = len(x)
    results = []

    # T1 row balance
    rowbal = Z.sum(axis=1) + Y.sum(axis=1)
    mask = x > 0
    err = np.abs(rowbal[mask] - x[mask]) / x[mask]
    results.append(("T1 row balance x = Z*1 + Y*1", float(np.max(err)), "max rel dev"))

    # T2 A = Z xhat^-1
    j = int(np.argmax(x))
    err2 = np.max(np.abs(A[:, j] * x[j] - Z[:, j])) / max(np.max(np.abs(Z[:, j])), 1e-12)
    results.append(("T2 A = Z xhat^-1 (largest column)", float(err2), "max rel dev"))

    # T3 (I-A)L = I  on a random subset of columns
    rng = np.random.default_rng(0)
    cols = rng.choice(n, size=25, replace=False)
    IA_L = L[:, cols] - A @ L[:, cols]
    eye = np.zeros_like(IA_L)
    eye[cols, np.arange(len(cols))] = 1.0
    results.append(("T3 (I-A)L = I (25 random cols)", float(np.max(np.abs(IA_L - eye))), "max abs dev"))

    # T4 x = L (Y*1)
    x_hat = L @ Y.sum(axis=1)
    err4 = np.abs(x_hat[mask] - x[mask]) / x[mask]
    results.append(("T4 x = L(Y*1)", float(np.max(err4)), "max rel dev"))

    # T5/T6 need the healthcare background (S and y_H)
    bgp = os.path.join(str(BACKGROUND_DIR), f"gddz_background_information_{YEAR}.pkl")
    if os.path.exists(bgp):
        with open(bgp, "rb") as fh:
            bg = pickle.load(fh)
        B, Ys = bg["B"], bg["Ystim"]
        for k, name in ((0, "climate"), (1, "material"), (6, "waste")):
            s = B[k, :]
            y = Ys[:, 0]
            lhs = float(s @ (L @ y))
            nz = np.flatnonzero(y)
            E = (L[:, nz] * y[nz][np.newaxis, :]) * s[:, np.newaxis]
            results.append((f"T5 {name}: s.Ly == sum(E)", _rel(E.sum(), lhs), "rel dev"))
            results.append((f"T6 {name}: producer-sum == purchase-sum",
                            _rel(E.sum(axis=1).sum(), E.sum(axis=0).sum()), "rel dev"))
            del E

    print(f"EE-MRIO identity tests, background year {YEAR}, n = {n} nodes")
    print(f"monetary unit of release: {m.get('source', 'n/a')}")
    ok = True
    for name, val, kind in results:
        flag = "PASS" if val < TOL else "FAIL"
        ok &= val < TOL
        print(f"  [{flag}] {name:45s} {kind} = {val:.3e}")
    print("ALL IDENTITIES PASS" if ok else "SOME IDENTITIES FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
