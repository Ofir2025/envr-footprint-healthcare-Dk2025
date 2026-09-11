# -*- coding: utf-8 -*-
"""Reallocate Danish sea transport, following Statistics Denmark's diagnosis.

Rørmose Jensen & Iliev (2022, pp. 11-12) report that EXIOBASE sends 74 % of
Danish water-transport output to Danish *intermediate* use, against 9 % in the
Danish national accounts. The Danish-operated fleet carries world trade, not
Danish production, so the misallocation loads the emissions of one of the
world's largest merchant fleets onto Danish consumption.

This module reproduces their diagnosis on the model actually in use and applies
the correction they imply. On EXIOBASE v3.8.2 IOT_2022_ixi the Danish
sea-and-coastal-water-transport row delivers 73.6 % of its output to Danish
intermediate use - Statistics Denmark's 74 %, to the decimal.

The benchmark is published for one year only. Rørmose Jensen & Iliev report the
9 % national-accounts share for 2019 and give no time series; it is applied here
to 2022 (and to 2016 if run on that background) on the evidence that the
EXIOBASE side of the discrepancy is year-invariant - 73.51 % in 2016, 73.65 % in
2022, against their 74 % for 2019.

Correction
----------
The row's total output is left unchanged. That is a scope decision, not a claim
that the level is right: EXIOBASE's Danish sea-transport output is 0.23x the
national-accounts figure in 2022 and 0.63x in 2016
(`09_exiobase_release_diagnostics/dk_block_vs_national_accounts.csv`), and
Rørmose Jensen & Iliev report the same defect for 2019 (p. 12). Only the
*allocation* is corrected, because the allocation is what decides whether the
emissions land in Danish consumption; the level is left to a full
national-accounts coupling.

    target_dk_intermediate = SHARE_TARGET * x_row
    Z[row, DK] *= target_dk_intermediate / Z[row, DK].sum()
    the released amount is added to exports, distributed over foreign final
    demand in proportion to each region's existing final demand

The distribution key is this repository's own choice, not either source's:
neither Rørmose Jensen & Iliev (2022) nor Schmidt & Merciai (2023) builds a
corrected EXIOBASE, so neither proposes one. Weighting by each foreign
final-demand column's total size is a neutral numeraire, not a measured trade
pattern. Booking the release to Y rather than to foreign intermediate use makes
it terminal - it cannot re-enter a supply chain and return to Denmark through
imports - which is conservative for the quantity measured but is a departure
from the national-accounts structure, where exported freight is largely an
intermediate input abroad.

Column balance is restored by crediting the released amount to the residual net
operating surplus (the last primary-input row) of the Danish industries that
stop buying the shipping, so that `sum(Z[:, j]) + VA_j = x_j` continues to hold.
Their outputs are the part of the Danish block not in dispute, and rescaling
them would change every Danish emission intensity e_i/x_i, so the offset belongs
in the accounting item that exists to absorb the gap between output and measured
costs. Note that this does not repair the shipping industry's own value added,
which Rørmose Jensen & Iliev report as negative (p. 12) and which measures
-493 M.EUR in 2016 and +271 M.EUR in 2022 on v3.8.2.

The uncorrected model is retained; both are reported.

Run, once per background year (``HC_ANALYSIS_YEAR`` selects it -- 2022 stays
2022, anything else, 2019 today, maps to 2016 -- exactly as everywhere else in
this package; HC_BACKGROUND_TAG must be unset, since this module writes the
``_snacship`` variant itself)::

    HC_ANALYSIS_YEAR=2022 PYTHONPATH=src .venv/bin/python -m analysis.dk_shipping_correction
    HC_ANALYSIS_YEAR=2019 PYTHONPATH=src .venv/bin/python -m analysis.dk_shipping_correction

Then, for either year, with the tag now set::

    HC_BACKGROUND_TAG=_snacship HC_ANALYSIS_YEAR=2022 \\
        .venv/bin/python -m analysis.main_2025
"""

import os
import pickle

import numpy as np
import pandas as pd

from analysis.constants import (ANALYSIS_YEAR, BACKGROUND_TAG, BACKGROUND_YEAR,
                                K_DK, N_FINAL_DEMAND, N_SECTORS, model_label)
from paths import MRIO_DIR, OUTPUT_DIR

FOLDER = "10_sea_transport_reallocation"

# This module always writes the "_snacship" variant itself (TAG below), so it
# must be run with HC_BACKGROUND_TAG unset -- setting it would make
# BACKGROUND_YEAR point the source read at the very file this run creates.
if BACKGROUND_TAG:
    raise SystemExit(
        "analysis.dk_shipping_correction writes the _snacship background "
        f"itself; run it with HC_BACKGROUND_TAG unset, not {BACKGROUND_TAG!r}")

#: Background year this run corrects: HC_ANALYSIS_YEAR maps onto it the same
#: way every other module in this package does (2022 stays 2022; anything
#: else -- 2019 today -- runs on the 2016 background). A 2019 analysis run
#: therefore corrects mrio2016.pkl, not a nonexistent mrio2019.pkl.
BG_YEAR = BACKGROUND_YEAR
TAG = "_snacship"

# Rørmose Jensen & Iliev (2022), Statistics Denmark, "Coupled models", pp. 11-12
SHARE_TARGET = 0.09
SECTOR_NAME = "Sea and coastal water transport"


def _upsert_by_background_year(new: pd.DataFrame, path: str) -> pd.DataFrame:
    """Replace this run's rows in an existing table, keeping other years' rows.

    Parameters
    ----------
    new : pandas.DataFrame
        Rows for the background year this run just computed. Must carry a
        ``background_year`` column.
    path : str
        Where the table is, or will be, written.

    Returns
    -------
    pandas.DataFrame
        ``new`` merged with whatever the file on disk holds for OTHER
        background years, so running this module for 2019 does not erase the
        2022 rows an earlier run wrote, and running it again for 2022 does
        not erase 2019's.
    """
    if not os.path.exists(path):
        return new
    old = pd.read_csv(path)
    if "background_year" not in old.columns:
        # A pre-upsert file from a single-year run holds only that run's own
        # background year, so it is superseded rather than merged.
        return new
    this_year = str(new["background_year"].iloc[0])
    old = old[old["background_year"].astype(str) != this_year]
    return pd.concat([old, new], ignore_index=True)


def main() -> None:
    """Reallocate Danish sea transport on the configured background year.

    Reads ``mrio<BG_YEAR>.pkl`` and writes ``mrio<BG_YEAR>_snacship.pkl`` /
    ``leontief<BG_YEAR>_snacship.pkl`` beside it, plus this layer's two gold
    diagnostics tables. Both tables are upserted by ``background_year`` (see
    :func:`_upsert_by_background_year`), so a run on one background year does
    not erase another's rows -- 2016 and 2022 sit side by side, and a reader
    can see directly whether the 74 % misallocation Rørmose Jensen & Iliev
    (2022) report for 2019 also holds on the 2016 background this study's
    2019 replication actually runs on.
    """
    out_dir = os.path.join(OUTPUT_DIR, FOLDER)
    os.makedirs(out_dir, exist_ok=True)
    mdir = str(MRIO_DIR) + os.sep

    with open(f"{mdir}mrio{BG_YEAR}.pkl", "rb") as fh:
        m = pickle.load(fh)
    inds = list(m["label"]["industry"]["Name"])
    sea = inds.index(SECTOR_NAME)
    row = K_DK * N_SECTORS + sea

    Z, Y, x, V = m["Z"].copy(), m["Y"].copy(), m["x"].copy(), m["V"].copy()
    dk = slice(K_DK * N_SECTORS, (K_DK + 1) * N_SECTORS)
    dk_fd = slice(K_DK * N_FINAL_DEMAND, (K_DK + 1) * N_FINAL_DEMAND)

    x_row = float(x[row, 0])
    before = float(Z[row, dk].sum())
    target = SHARE_TARGET * x_row
    if before <= target:
        raise SystemExit(f"no correction needed: DK intermediate share is "
                         f"{100 * before / x_row:.1f} %")

    released = before - target
    scale = target / before
    removed_by_industry = Z[row, dk] * (1.0 - scale)
    Z[row, dk] *= scale

    # exports: distribute over foreign final demand in proportion to each
    # region's existing total final demand, so no region is singled out
    fd_tot = Y.sum(axis=0)
    mask = np.ones(Y.shape[1], dtype=bool)
    mask[dk_fd] = False
    w = np.where(mask, fd_tot, 0.0)
    w = w / w.sum()
    Y[row, :] += released * w

    # column balance: credit the released amount to the value added of the
    # Danish industries that stop buying the shipping
    V[-1, dk] += removed_by_industry

    # rebuild A and L on the corrected Z
    xs = x[:, 0].copy()
    inv = np.divide(1.0, xs, out=np.zeros_like(xs), where=xs > 0)
    A = Z * inv[np.newaxis, :]
    L = np.linalg.inv(np.eye(A.shape[0]) - A)

    m["Z"], m["Y"], m["A"], m["V"] = Z, Y, A, V
    with open(f"{mdir}mrio{BG_YEAR}{TAG}.pkl", "wb") as fh:
        pickle.dump(m, fh)
    with open(f"{mdir}leontief{BG_YEAR}{TAG}.pkl", "wb") as fh:
        pickle.dump(L, fh)

    # verification
    resid_row = float(abs(Z[row, :].sum() + Y[row, :].sum() - x_row))
    col = Z[:, dk].sum(axis=0) + V[:, dk].sum(axis=0)
    resid_col = float(np.max(np.abs(col - xs[dk])))
    after = float(Z[row, dk].sum())

    # Year-aware, so a 2019 (2016-background) run does not print "IOT_2022_ixi"
    # against numbers it never touched. model_label() strips BACKGROUND_TAG,
    # which is guaranteed empty here (asserted above), so this is exactly
    # "EXIOBASE v3.8.2 IOT_<BG_YEAR>_ixi" with no variant suffix -- the
    # UNCORRECTED background this run reads, before its own correction.
    source_label = model_label(BG_YEAR)
    rows = [
        dict(quantity="DK sea transport total output", value=x_row, unit="M.EUR",
             source=source_label),
        dict(quantity="to DK intermediate use, before", value=before,
             unit="M.EUR", source=source_label),
        dict(quantity="share to DK intermediate use, before",
             value=100 * before / x_row, unit="%",
             source="reproduces Rørmose Jensen & Iliev 2022 (74 % for 2019)"),
        dict(quantity="share to DK intermediate use, after",
             value=100 * after / x_row, unit="%",
             source="Rørmose Jensen & Iliev 2022 target (9 %)"),
        dict(quantity="output reallocated to exports", value=released,
             unit="M.EUR", source="this correction"),
        dict(quantity="row balance residual after correction", value=resid_row,
             unit="M.EUR", source="verification"),
        dict(quantity="max column balance residual, DK block",
             value=resid_col, unit="M.EUR", source="verification"),
    ]
    df = pd.DataFrame(rows)
    df.insert(0, "country_producing", "DNK")
    df.insert(1, "sector_producing", SECTOR_NAME)
    # Which background year (and which analysis year selected it) every row
    # below describes -- required so a reader comparing this file across runs
    # can tell the 2016 rows from the 2022 rows without cross-referencing
    # anything else.
    df.insert(2, "background_year", BG_YEAR)
    df.insert(3, "analysis_year", ANALYSIS_YEAR)
    diag_path = os.path.join(out_dir, "shipping_reallocation_diagnostics.csv")
    df = _upsert_by_background_year(df, diag_path)
    df.to_csv(diag_path, index=False)

    # which Danish industries lose the phantom shipping input
    top = pd.DataFrame(dict(
        country_producing="DNK", sector_producing=SECTOR_NAME,
        background_year=BG_YEAR, analysis_year=ANALYSIS_YEAR,
        country_consuming="DNK", sector_consuming=inds,
        value=removed_by_industry, unit="M.EUR"))
    top = top[top.value > 0].sort_values("value", ascending=False)
    top_path = os.path.join(out_dir,
                            "phantom_shipping_input_removed_by_industry.csv")
    top = _upsert_by_background_year(top, top_path)
    top.to_csv(top_path, index=False)

    this_run = df[df.background_year.astype(str) == str(BG_YEAR)]
    print(f"background year {BG_YEAR} (analysis year {ANALYSIS_YEAR})")
    print(this_run.to_string(index=False))
    print(f"\nrow balance residual {resid_row:.3e} | column residual "
          f"{resid_col:.3e} M.EUR")
    print("\nDanish industries losing the largest phantom shipping input:")
    print(top[top.background_year.astype(str) == str(BG_YEAR)]
          .head(10)[["sector_consuming", "value"]].to_string(index=False))
    print(f"\nwritten -> {out_dir}")
    print(f"background -> mrio{BG_YEAR}{TAG}.pkl, leontief{BG_YEAR}{TAG}.pkl")


if __name__ == "__main__":
    main()
