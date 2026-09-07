# -*- coding: utf-8 -*-
"""Extended impact categories for the Danish healthcare footprint.

The core model reports the five Steenmeijer et al. (2022) categories (climate,
abiotic material extraction, blue water, land, waste). EXIOBASE v3.10.2 carries
further stressor families that the comparative literature uses and that cost
nothing extra to compute from the same Leontief system:

* air pollutants  PM2.5, PM10, NOx, SOx, NH3, NMVOC  -> the stressor families
  reported by Lenzen et al. (2020) and the inventory side of the Eckelman &
  Sherman (2016) public-health-damage analysis;
* energy use (final and gross, TJ);
* reactive nitrogen and phosphorus to water (eutrophication pressure).

These are pressure (inventory) accounts, not characterised midpoints; no
endpoint/DALY conversion is applied here because that needs an LCIA model with
defensible characterisation factors (Eckelman & Sherman use TRACI + IMPACT2002+
and explicitly refuse endpoints for categories lacking robust factors).

Detail is exported in the same schema as analysis.export_tables so the two sets
of indicators aggregate identically.

Run: PYTHONPATH=src .venv/bin/python -m analysis.extended_indicators
"""

import os
import pickle
import re

import numpy as np
import pandas as pd

from paths import BACKGROUND_DIR, MRIO_DIR, OUTPUT_DIR
from analysis.export_tables import _labels, _node_frame, DEMAND_COMPONENTS

ANALYSIS_YEAR = os.environ.get("HC_ANALYSIS_YEAR", "2022")
BACKGROUND_YEAR = "2022" if ANALYSIS_YEAR == "2022" else "2016"

# name pattern -> (indicator, native unit, scale to reporting unit, reporting unit)
FAMILIES = [
    (r"^PM2\.5 .*- air$",  "pm2_5",            "kg", 1e-6, "kt"),
    (r"^PM10 .*- air$",    "pm10",             "kg", 1e-6, "kt"),
    (r"^NOx .*- air$",     "nox",              "kg", 1e-6, "kt"),
    (r"^(SOx|SO2) .*- air$", "sox",            "kg", 1e-6, "kt"),
    (r"^NH3 .*- air$",     "nh3",              "kg", 1e-6, "kt"),
    (r"^NMVOC .*- air$",   "nmvoc",            "kg", 1e-6, "kt"),
    (r"^Energy use - Final$", "energy_use_final", "TJ", 1.0, "TJ"),
    (r"^Energy use - Gross$", "energy_use_gross", "TJ", 1.0, "TJ"),
    (r"^N - .* - water$",  "nitrogen_to_water", "kg", 1e-6, "kt"),
    (r"^P - .* - water$",  "phosphorus_to_water", "kg", 1e-6, "kt"),
]


def main():
    out_dir = os.path.join(str(OUTPUT_DIR), "tables")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(str(MRIO_DIR), f"mrio{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        m = pickle.load(fh)
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        bg = pickle.load(fh)

    names = [str(x) for x in m["label"]["extension"]["Name"]]
    units = [str(x) for x in m["label"]["extension"]["unit"]]
    R, x = m["R"], m["x"][:, 0]
    xinv = np.where(x > 0, 1.0 / np.where(x > 0, x, 1.0), 0.0)
    L, Ystim = bg["L"], bg["Ystim"]
    reg, sec = _labels()
    prod = _node_frame(reg, sec, "producing")
    meta = dict(analysis_year=ANALYSIS_YEAR, scenario=os.environ.get("HC_SCENARIO", "baseline"),
                model=f"EXIOBASE v3.10.2 IOT_{BACKGROUND_YEAR}_ixi (screened)",
                consuming_country_iso3="DNK")

    detail_rows, summary_rows = [], []
    for pat, ind_name, native_unit, scale, rep_unit in FAMILIES:
        rx = re.compile(pat)
        idx = [i for i, n in enumerate(names) if rx.match(n)]
        if not idx:
            print(f"  ! no stressors matched for {ind_name}")
            continue
        bad = {units[i] for i in idx} - {native_unit}
        assert not bad, f"{ind_name}: unexpected units {bad}"
        s = (R[idx, :].sum(axis=0) * xinv) * scale     # intensity per M.EUR output
        for c, cname in DEMAND_COMPONENTS.items():
            if c == 0:
                continue
            y = Ystim[:, c]
            v = s * (L @ y)
            nz = np.flatnonzero(np.abs(v) > 0)
            d = prod.iloc[nz].copy()
            d.insert(0, "demand_component", cname)
            d.insert(0, "unit", rep_unit)
            d.insert(0, "indicator", ind_name)
            d["value"] = v[nz]
            detail_rows.append(d)
            summary_rows.append({"indicator": ind_name, "unit": rep_unit,
                                 "demand_component": cname, "n_stressor_rows": len(idx),
                                 "value": float(v.sum())})
        print(f"  {ind_name:20s} {len(idx):3d} stressor rows -> "
              f"{sum(r['value'] for r in summary_rows if r['indicator']==ind_name):12,.2f} {rep_unit}")

    det = pd.concat(detail_rows, ignore_index=True)
    summ = pd.DataFrame(summary_rows)
    for k, v in meta.items():
        det.insert(0, k, v)
        summ.insert(0, k, v)
    det.to_csv(os.path.join(out_dir, "extended_indicators_by_producing_node.csv"), index=False)
    summ.to_csv(os.path.join(out_dir, "extended_indicators_summary.csv"), index=False)
    print(f"\nextended_indicators_by_producing_node.csv: {len(det):,} rows")
    tot = summ.groupby(["indicator", "unit"])["value"].sum().reset_index()
    print(tot.to_string(index=False))


if __name__ == "__main__":
    main()
