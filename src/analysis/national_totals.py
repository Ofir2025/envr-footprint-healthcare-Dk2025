# -*- coding: utf-8 -*-
"""Danish national consumption footprint at full detail, and healthcare's share.

The healthcare footprint is only interpretable against a national total built
on the SAME model and boundary. This module computes the Danish
consumption-based footprint for ALL final demand (every one of the 163 product
groups across 49 supplying regions, plus direct household emissions) and
expresses the healthcare result as a share of it.

Two decompositions, both exported at full detail:
  * by PURCHASED product   c_j = m_j y_j          with m = d L  (the multiplier)
  * by PRODUCING node      c_i = d_i (L y)_i
Both sum to the same national total (asserted).

Healthcare's share is then reported per indicator and per product group, so the
question "what share of the impacts of all goods and services consumed in
Denmark is health-related?" is answered at the level of the 163 sectors rather
than only in aggregate.

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.national_totals
"""

import os
import pickle

import numpy as np
import pandas as pd

from paths import BACKGROUND_DIR, OUTPUT_DIR
from analysis.export_tables import _labels, _node_frame

ANALYSIS_YEAR = os.environ.get("HC_ANALYSIS_YEAR", "2022")
BACKGROUND_YEAR = "2022" if ANALYSIS_YEAR == "2022" else "2016"
K_DK, NS, NY = 6, 163, 7
INDICATORS = [(0, "climate_change", "kt CO2eq"), (1, "material_extraction", "kt"),
              (2, "blue_water_consumption", "Mm3"), (3, "land_use", "km2"),
              (6, "waste_generation", "kt")]


def main():
    out_dir = os.path.join(str(OUTPUT_DIR), "00_core_footprint")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        bg = pickle.load(fh)
    B, L, Y, H, Ystim = bg["B"], bg["L"], bg["Y"], bg["H"], bg["Ystim"]
    reg, sec = _labels()
    purch = _node_frame(reg, sec, "purchased")
    prod = _node_frame(reg, sec, "producing")

    # Danish final demand: the 7 final-demand categories of the DK block
    y_nat = Y[:, K_DK * NY:(K_DK + 1) * NY].sum(axis=1)
    y_h = Ystim[:, 0]

    rows_purch, rows_prod, summary, byprod = [], [], [], []
    for k, ind, unit in INDICATORS:
        d = B[k, :]
        m = d @ L                                   # cradle-to-gate multipliers
        c_purch = m * y_nat                         # by purchased product
        c_prod = d * (L @ y_nat)                    # by producing node
        direct_hh = float(H[k, K_DK * NY:(K_DK + 1) * NY].sum())
        nat_total = float(c_purch.sum()) + direct_hh
        assert abs(c_purch.sum() - c_prod.sum()) / max(abs(c_purch.sum()), 1e-9) < 1e-9

        hc_total = float((m * y_h).sum())            # healthcare, same model

        for frame, vec, store in ((purch, c_purch, rows_purch), (prod, c_prod, rows_prod)):
            nz = np.flatnonzero(np.abs(vec) > 0)
            df = frame.iloc[nz].copy()
            df.insert(0, "unit", unit)
            df.insert(0, "indicator", ind)
            df["value"] = vec[nz]
            store.append(df)

        # per product group (163 sectors, summed over supplying regions)
        g = pd.DataFrame({"sector_code": np.tile(sec["sector_code"].values, len(reg)),
                          "sector_name": np.tile(sec["sector_name"].values, len(reg)),
                          "sector_group": np.tile(sec["sector_group"].values, len(reg)),
                          "national": c_purch, "healthcare": m * y_h})
        gg = g.groupby(["sector_code", "sector_name", "sector_group"], as_index=False).sum()
        gg.insert(0, "unit", unit)
        gg.insert(0, "indicator", ind)
        # NB this ratio can exceed 100 %: y_H is superimposed on the model
        # rather than carved out of EXIOBASE's Danish final demand (see
        # analysis.demand_vector_consistency). It is a diagnostic, not a share.
        gg["healthcare_vs_sector_ratio_pct"] = np.where(
            gg["national"] > 0, 100 * gg["healthcare"] / gg["national"], np.nan)
        gg["sector_share_of_national_pct"] = 100 * gg["national"] / gg["national"].sum()
        byprod.append(gg)

        summary.append(dict(
            indicator=ind, unit=unit,
            national_footprint=nat_total,
            national_supply_chain=float(c_purch.sum()),
            national_direct_households=direct_hh,
            healthcare_footprint_mrio=hc_total,
            healthcare_share_pct=100 * hc_total / nat_total))
        print(f"  {ind:22s} national {nat_total:12,.1f} {unit:9s} "
              f"(households direct {direct_hh:9,.1f}) | healthcare MRIO {hc_total:10,.1f} "
              f"= {100 * hc_total / nat_total:5.2f} %")

    meta = dict(analysis_year=ANALYSIS_YEAR,
                model=f"EXIOBASE v3.10.2 IOT_{BACKGROUND_YEAR}_ixi (screened)",
                consuming_country_iso3="DNK",
                scope="ALL Danish final demand (163 products x 49 regions, 7 FD categories)")
    for name, frames in (("national_footprint_by_purchased_product.csv", rows_purch),
                         ("national_footprint_by_producing_node.csv", rows_prod),
                         ("national_vs_healthcare_by_product_group.csv", byprod)):
        df = pd.concat(frames, ignore_index=True)
        for k2, v in meta.items():
            df.insert(0, k2, v)
        df.to_csv(os.path.join(out_dir, name), index=False)
        print(f"{name}: {len(df):,} rows")
    s = pd.DataFrame(summary)
    for k2, v in meta.items():
        s.insert(0, k2, v)
    s.to_csv(os.path.join(out_dir, "national_totals_summary.csv"), index=False)


if __name__ == "__main__":
    main()
