# -*- coding: utf-8 -*-
"""Malik et al. (2018, 2021) comparison layer for Denmark.

Malik et al. report the Australian health system with a specific set of
choices that differ from ours. Comparing headline numbers without matching
those choices would be misleading, so this module builds the variants that make
the comparison like-for-like, and states what cannot be matched.

Their boundary choices, and what we do about each:

  imports      2018 puts imports in the value-added block and 2021 excludes
               them, so both are DOMESTIC-ONLY models. We therefore also
               compute a domestic-only Danish variant with
                   L_dom = (I - A_DK,DK)^-1        (163 x 163)
               which is the only number comparable with their 7.2 % / 6.6 %.
  capital      2018 INCLUDES capital expenditure (a separate AIHW category,
               2,776 kt = 8 % of their total); 2021 excludes it; we exclude it
               (EXIOBASE's Z has no GFCF). Flagged, not silently ignored.
  aged care    2018 excludes it entirely; we include residential eldercare.
               The health-only scope variant (HC_SCOPE=health_only) is the
               comparable one.
  intensities  they publish kt per million dollars by health category, so this
               module emits the equivalent per-component intensities in
               kt per million EURO.

Production layers are in analysis.production_layers (their Fig. 3 method).

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.malik_replication
"""

import os
import pickle

import numpy as np
import pandas as pd

from paths import BACKGROUND_DIR, OUTPUT_DIR
from analysis.constants import (BACKGROUND_YEAR, DK_BLOCK, INDICATORS, K_DK,
                                MODEL_LABEL, N_SECTORS, DK_POPULATION)

MALIK_REFERENCE = [
    dict(study="Malik et al. 2018 (Australia, 2014-15)", indicator="climate_change",
         total_kt=35772, share_national_pct=7.2, direct_pct=13.4,
         boundary="domestic-only; capital INCLUDED; aged care excluded"),
    dict(study="Malik et al. 2021 (NSW, 2017)", indicator="climate_change",
         total_kt=7908, share_national_pct=6.6, direct_pct=11.0,
         boundary="domestic-only; capital and imports excluded"),
    dict(study="Malik et al. 2021 (NSW, 2017)", indicator="blue_water_consumption",
         total_kt=246.0, share_national_pct=4.0, direct_pct=17.0,
         boundary="water in GL (=Mm3); withdrawal, not consumption"),
    dict(study="Malik et al. 2021 (NSW, 2017)", indicator="waste_generation",
         total_kt=1624, share_national_pct=8.0, direct_pct=62.0,
         boundary="11 waste fractions, Australian accounts"),
]


def main() -> None:
    """Apply Malik et al.'s domestic-only boundary to the Danish model.

    For each of the five headline indicators, computes the full-MRIO footprint
    and a domestic-only variant on the Danish block's own Leontief inverse,
    each with the national denominator it is a share of, and the three
    expenditure components' total and direct intensities. Writes
    ``malik_domestic_vs_full.csv``, ``malik_component_intensities.csv`` and
    ``malik_published_reference.csv`` to
    ``data/gold/results/07_malik_replication/``.

    The background is ``analysis.constants.BACKGROUND_YEAR``, which carries
    both ``HC_ANALYSIS_YEAR`` and ``HC_BACKGROUND_TAG``.
    """
    year = os.environ.get("HC_ANALYSIS_YEAR", "2022")
    bgy = BACKGROUND_YEAR  # honours HC_BACKGROUND_TAG
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{bgy}.pkl"), "rb") as fh:
        bg = pickle.load(fh)
    A, L, B, Y, Ystim, Hstim = bg["A"], bg["L"], bg["B"], bg["Y"], bg["Ystim"], bg["Hstim"]

    # domestic-only Leontief for the Danish block (Malik's model form)
    A_dom = A[DK_BLOCK, DK_BLOCK]
    L_dom = np.linalg.inv(np.eye(N_SECTORS) - A_dom)
    y_nat = Y[:, K_DK * 7:(K_DK + 1) * 7].sum(axis=1)

    dk = pd.read_csv(os.path.join(str(BACKGROUND_DIR), "..", "inputs", "dk_data_2025.csv"))
    exp = dk.query("Index == 'Expenditure'")[["HC service", "Pharm", "MedAppl"]].iloc[0]
    comp_exp = {"healthcare_services": float(exp["HC service"]),
                "pharmaceuticals": float(exp["Pharm"]),
                "medical_appliances": float(exp["MedAppl"])}

    rows, intens = [], []
    for k, ind, unit in INDICATORS:
        s = B[k, :]
        full = float(s @ (L @ Ystim[:, 0])) + float(Hstim[k, 0])
        # domestic-only: restrict both the demand vector and the chain to Denmark
        y_dk = Ystim[DK_BLOCK, 0]
        dom = float(s[DK_BLOCK] @ (L_dom @ y_dk)) + float(Hstim[k, 0])
        nat_full = float(s @ (L @ y_nat))
        nat_dom = float(s[DK_BLOCK] @ (L_dom @ y_nat[DK_BLOCK]))
        # Both shares are published with the denominator they are taken over.
        # The domestic-only share was previously a percentage with no
        # denominator anywhere in the gold layer, so it could not be
        # reconciled from the published tables at all: nat_dom is not the
        # national footprint, it is the part of it that arises inside Denmark
        # under the domestic-only inverse, and it is a different quantity from
        # 00_core_footprint's national_supply_chain.
        rows.append(dict(indicator=ind, unit=unit,
                         full_mrio=full, domestic_only=dom,
                         domestic_share_of_full_pct=100 * dom / full,
                         national_full_mrio=nat_full,
                         national_domestic_only=nat_dom,
                         share_of_national_full_pct=100 * full / nat_full,
                         share_of_national_domestic_pct=100 * dom / nat_dom if nat_dom else np.nan,
                         denominator_note=(
                             "share_of_national_full_pct is over national_full_mrio, "
                             "which is 00_core_footprint's national_supply_chain; "
                             "share_of_national_domestic_pct is over "
                             "national_domestic_only, the pressure arising inside "
                             "Denmark from all Danish final demand under the "
                             "domestic-only inverse L_dom = (I - A_DK,DK)^-1. The "
                             "second denominator is Malik's model form and is "
                             "published nowhere else")))
        for c, col in (("healthcare_services", 1), ("pharmaceuticals", 2),
                       ("medical_appliances", 3)):
            f_c = float(s @ (L @ Ystim[:, col]))
            e_c = comp_exp[c]
            intens.append(dict(indicator=ind, unit=unit, component=c,
                               footprint=f_c, expenditure_meur=e_c,
                               total_intensity_per_meur=f_c / e_c if e_c else np.nan,
                               direct_intensity_per_meur=float(s @ Ystim[:, col]) / e_c if e_c else np.nan))
        print(f"  {ind:22s} full {full:10,.1f} | domestic-only {dom:9,.1f} "
              f"({100*dom/full:4.1f} % of full) | share of national: full "
              f"{100*full/nat_full:4.2f} %, domestic {100*dom/nat_dom if nat_dom else float('nan'):4.2f} %")

    out_dir = os.path.join(str(OUTPUT_DIR), "07_malik_replication")
    os.makedirs(out_dir, exist_ok=True)
    meta = dict(analysis_year=year, consuming_country_iso3="DNK",
                model=MODEL_LABEL)
    for name, frame in (("malik_domestic_vs_full.csv", pd.DataFrame(rows)),
                        ("malik_component_intensities.csv", pd.DataFrame(intens)),
                        ("malik_published_reference.csv", pd.DataFrame(MALIK_REFERENCE))):
        for k2, v in meta.items():
            frame.insert(0, k2, v)
        frame.to_csv(os.path.join(out_dir, name), index=False)
    print(f"written -> {out_dir}/malik_domestic_vs_full.csv (+ intensities, reference)")


if __name__ == "__main__":
    main()
