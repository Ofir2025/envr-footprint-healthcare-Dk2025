# -*- coding: utf-8 -*-
"""Structured, machine-readable result tables for the Danish healthcare footprint.

Design principle: export the MOST DETAILED level and let every aggregate be
derived from it (never the reverse), so that any published figure can be traced
back to region-sector lineage.

Dimension conventions
---------------------
* Countries use ISO3 codes; the five EXIOBASE rest-of-world regions keep their
  own labels (WA/WL/WE/WF/WM = RoW Asia and Pacific / America / Europe /
  Africa / Middle East), as they are not countries.
* ``consuming_country_iso3`` is DNK throughout: Denmark is the final consumer.
* ``purchased_*`` describes the finally demanded product and the region that
  supplies it (the position in the final-demand vector y_H).
* ``producing_*`` describes where the environmental pressure physically occurs
  (the position in the direct-intensity vector), i.e. the hotspot perspective.
* All monetary values are MILLION EURO (M.EUR) - EXIOBASE's native unit
  (see unit.txt of the release); no USD anywhere in this model.

Emissions are E[i,j] = s_k(i) * L(i,j) * y(j): pressure arising in node i that
is caused by Danish final demand for node j. Summing E over i gives the
consumption ("contribution") perspective; summing over j gives the production
("hotspot") perspective. Both are exports of the SAME array, so they are
mutually consistent and non-double-counting (Wood et al. 2018: allocation of
production emissions to final demand is additive; embodied-flow tables are not).

Run:  PYTHONPATH=src .venv/bin/python -m analysis.export_tables
"""

import os
import pickle

import numpy as np
import pandas as pd

from paths import BRONZE_DIR, BACKGROUND_DIR, OUTPUT_DIR, silver_dk_data_csv

ANALYSIS_YEAR = os.environ.get("HC_ANALYSIS_YEAR", "2022")
from analysis.constants import BACKGROUND_YEAR, MODEL_LABEL, model_label  # noqa: E402
SCENARIO = os.environ.get("HC_SCENARIO", "baseline")
MODEL_VERSION = MODEL_LABEL

DEMAND_COMPONENTS = {0: "total", 1: "healthcare_services", 2: "pharmaceuticals", 3: "medical_appliances"}
# relative cutoff for the bilateral table: cells below this share of the
# indicator total are dropped; achieved coverage is reported and stored.
BILATERAL_TARGET_COVERAGE = 0.995  # keep the largest cells up to this share;
# the residual is written as an explicit remainder row so every table still
# sums EXACTLY to the reported total (no silent truncation).


def _labels() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Region and sector label frames, from the single source of truth.

    This used to be a second, independent reader of ``classifications.xlsx``.
    Two readers meant two places to apply a convention, and the star-schema
    rules (no ``A_`` / ``C_`` prefix on industry codes; Denmark rather than the
    Netherlands as the singled-out home region) were applied to only one of
    them, so half the gold tables silently disagreed with the other half.
    It now delegates.

    Returns
    -------
    tuple of pandas.DataFrame
        ``(regions, sectors)`` as returned by
        :func:`analysis.detail_tables.node_labels`.
    """
    from analysis.detail_tables import node_labels
    return node_labels()


def _node_frame(reg: pd.DataFrame, sec: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """Expand region and sector labels into a full 49x163-node label frame.

    Parameters
    ----------
    reg : pandas.DataFrame
        Region labels (``iso3``, ``country_name``, ``world_region``), one row
        per region, in node order.
    sec : pandas.DataFrame
        Sector labels (``sector_code``, ``sector_name``, ``sector_group``),
        one row per sector, in node order.
    prefix : str
        Column-name prefix, e.g. ``"producing"`` or ``"purchased"``.

    Returns
    -------
    pandas.DataFrame
        One row per (region, sector) node, in EXIOBASE node order, with six
        ``f"{prefix}_*"`` label columns.
    """
    nr, ns = len(reg), len(sec)
    return pd.DataFrame({
        f"{prefix}_country_iso3": np.repeat(reg["iso3"].values, ns),
        f"{prefix}_country_name": np.repeat(reg["country_name"].values, ns),
        f"{prefix}_world_region": np.repeat(reg["world_region"].values, ns),
        f"{prefix}_sector_code": np.tile(sec["sector_code"].values, nr),
        f"{prefix}_sector_name": np.tile(sec["sector_name"].values, nr),
        f"{prefix}_sector_group": np.tile(sec["sector_group"].values, nr),
    })


def main() -> None:
    """Write the full-detail expenditure and footprint tables to gold.

    Builds the expenditure vector (``y_H``) at full region-sector detail and
    its basic-price summary, then for each of the five core indicators and
    each non-total demand component computes the bilateral array
    ``E[i,j] = s_k(i) L(i,j) y(j)`` and exports it by producing node, by
    purchased product, and as a coverage-thresholded bilateral table (largest
    cells covering ``BILATERAL_TARGET_COVERAGE``, with an explicit remainder
    row so totals reconcile exactly). Writes
    ``expenditure_vector_detail.csv``, ``expenditure_summary.csv``,
    ``footprint_by_producing_node.csv``, ``footprint_by_purchased_product.csv``,
    ``footprint_bilateral_producer_x_purchase.csv.gz`` and
    ``_bilateral_coverage.csv`` to
    ``data/gold/results/00_core_footprint/``. Reads ``HC_ANALYSIS_YEAR`` and
    ``HC_SCENARIO`` from the environment (defaults ``"2022"``/``"baseline"``).
    """
    out_dir = os.path.join(str(OUTPUT_DIR), "00_core_footprint")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        bg = pickle.load(fh)

    B, L, Ystim = bg["B"], bg["L"], bg["Ystim"]
    char = bg["label"]["characterization"]
    indicators = [(0, "climate_change", "kt CO2eq"), (1, "material_extraction", "kt"),
                  (2, "blue_water_consumption", "Mm3"), (3, "land_use", "km2"),
                  (6, "waste_generation", "kt")]
    reg, sec = _labels()
    prod = _node_frame(reg, sec, "producing")
    purch = _node_frame(reg, sec, "purchased")
    meta = dict(analysis_year=ANALYSIS_YEAR, scenario=SCENARIO, model=MODEL_VERSION,
                consuming_country_iso3="DNK")

    # ---------- 1. expenditure vector (final demand y_H), full detail -------
    rows = []
    for c, cname in DEMAND_COMPONENTS.items():
        if c == 0:
            continue
        y = Ystim[:, c]
        nz = np.flatnonzero(y)
        df = purch.iloc[nz].copy()
        df.insert(0, "demand_component", cname)
        df["value"] = y[nz]
        df["unit"] = "M.EUR"
        rows.append(df)
    exp = pd.concat(rows, ignore_index=True)
    for k, v in meta.items():
        exp.insert(0, k, v)
    exp["note"] = ("healthcare_services enters as the scaled intermediate-input "
                   "column of DK Health and social work (Steenmeijer construction): "
                   "value added carries no environmental pressure and is therefore "
                   "not part of y_H; pharmaceuticals/appliances enter at full "
                   "basic-price value distributed over supplying regions")
    exp.to_csv(os.path.join(out_dir, "expenditure_vector_detail.csv"), index=False)
    print(f"expenditure_vector_detail.csv: {len(exp):,} rows, "
          f"y_H total {exp['value'].sum():,.1f} M.EUR")
    dk = pd.read_csv(silver_dk_data_csv(ANALYSIS_YEAR))
    bp = dk[dk["Index"] == "Expenditure"].iloc[0]
    conv = dk[dk["Index"] == "Conversion"].iloc[0]
    esum = pd.DataFrame([
        {"demand_component": "healthcare_services",
         "basic_price_expenditure_meur": float(bp["HC service"]) * float(conv["HC service"]),
         "y_H_meur": float(Ystim[:, 1].sum())},
        {"demand_component": "pharmaceuticals",
         "basic_price_expenditure_meur": float(bp["Pharm"]) * float(conv["Pharm"]),
         "y_H_meur": float(Ystim[:, 2].sum())},
        {"demand_component": "medical_appliances",
         "basic_price_expenditure_meur": float(bp["MedAppl"]) * float(conv["MedAppl"]),
         "y_H_meur": float(Ystim[:, 3].sum())},
    ])
    esum["unit"] = "M.EUR"
    for k, v in meta.items():
        esum.insert(0, k, v)
    esum.to_csv(os.path.join(out_dir, "expenditure_summary.csv"), index=False)

    # ---------- 2/3/4. footprint arrays ------------------------------------
    prod_rows, purch_rows, bil_rows, cover = [], [], [], []
    for k_row, ind_name, unit in indicators:
        s_k = B[k_row, :]
        for c, cname in DEMAND_COMPONENTS.items():
            if c == 0:
                continue
            y = Ystim[:, c]
            nz = np.flatnonzero(y)
            # E[:, nz] = s_k[:,None] * L[:, nz] * y[nz][None,:]
            E = (L[:, nz] * y[nz][np.newaxis, :]) * s_k[:, np.newaxis]
            tot = float(E.sum())
            if tot == 0:
                continue
            # producing perspective (sum over purchased nodes)
            pv = E.sum(axis=1)
            pnz = np.flatnonzero(np.abs(pv) > 0)
            d = prod.iloc[pnz].copy()
            d.insert(0, "demand_component", cname)
            d.insert(0, "unit", unit); d.insert(0, "indicator", ind_name)
            d["value"] = pv[pnz]
            prod_rows.append(d)
            # purchased-product perspective (sum over producing nodes)
            qv = E.sum(axis=0)
            d2 = purch.iloc[nz].copy()
            d2.insert(0, "demand_component", cname)
            d2.insert(0, "unit", unit); d2.insert(0, "indicator", ind_name)
            d2["value"] = qv
            purch_rows.append(d2)
            # bilateral: keep largest cells covering BILATERAL_TARGET_COVERAGE
            flat = E.ravel()
            order = np.argsort(np.abs(flat))[::-1]
            csum = np.cumsum(np.abs(flat[order]))
            need = int(np.searchsorted(csum, BILATERAL_TARGET_COVERAGE * csum[-1]) + 1)
            keep = order[:need]
            ii, jj = np.unravel_index(keep, E.shape)
            vals = flat[keep]
            b = pd.concat([prod.iloc[ii].reset_index(drop=True),
                           purch.iloc[nz[jj]].reset_index(drop=True)], axis=1)
            b.insert(0, "demand_component", cname)
            b.insert(0, "unit", unit); b.insert(0, "indicator", ind_name)
            b["value"] = vals
            rem = tot - float(vals.sum())
            if abs(rem) > 0:
                r = {c: "BELOW_THRESHOLD_REMAINDER" for c in b.columns if c.endswith(
                    ("_iso3", "_name", "_code", "_group", "_region"))}
                r.update({"indicator": ind_name, "unit": unit,
                          "demand_component": cname, "value": rem})
                b = pd.concat([b, pd.DataFrame([r])], ignore_index=True)
            bil_rows.append(b)
            cover.append({"indicator": ind_name, "demand_component": cname,
                          "total": tot, "cells_kept": len(vals),
                          "coverage_pct": 100 * float(vals.sum()) / tot})
            del E

    def _write(frames: list[pd.DataFrame], name: str) -> pd.DataFrame:
        """Concatenate frames, prepend run metadata, and write one gold CSV.

        Parameters
        ----------
        frames : list of pandas.DataFrame
            Row blocks to concatenate, one per indicator/demand-component
            pair.
        name : str
            Output filename, written under the closed-over ``out_dir``.

        Returns
        -------
        pandas.DataFrame
            The concatenated, metadata-prefixed frame that was written.
        """
        df = pd.concat(frames, ignore_index=True)
        for k, v in meta.items():
            df.insert(0, k, v)
        df.to_csv(os.path.join(out_dir, name), index=False)
        print(f"{name}: {len(df):,} rows")
        return df

    _write(prod_rows, "footprint_by_producing_node.csv")
    _write(purch_rows, "footprint_by_purchased_product.csv")
    bil = pd.concat(bil_rows, ignore_index=True)
    for k, v in meta.items():
        bil.insert(0, k, v)
    bil_path = os.path.join(out_dir, "footprint_bilateral_producer_x_purchase.csv.gz")
    bil.to_csv(bil_path, index=False, compression={"method": "gzip", "mtime": 0})
    print(f"footprint_bilateral_producer_x_purchase.csv.gz: {len(bil):,} rows "
          f"(gzip; includes explicit remainder rows so totals reconcile exactly)")
    cov = pd.DataFrame(cover)
    cov.to_csv(os.path.join(out_dir, "_bilateral_coverage.csv"), index=False)
    print("bilateral coverage: min %.3f%%, max %.3f%%" %
          (cov["coverage_pct"].min(), cov["coverage_pct"].max()))


if __name__ == "__main__":
    main()
