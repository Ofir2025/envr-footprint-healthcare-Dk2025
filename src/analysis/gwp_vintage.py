# -*- coding: utf-8 -*-
"""Climate characterisation vintage: what AR6 changes, and what it cannot.

This study reports climate change on **IPCC AR6** GWP100. The characterisation
workbook shipped with the background instead carries AR4 factors (CH4 = 25,
N2O = 298) under a sheet labelled "CML 1999", so the climate row is rebuilt
from the stressor names in :func:`analysis.constants.ar6_gwp_factor`.

This module documents the consequence. It restates the Danish health-care and
national footprints under four IPCC assessment vintages and reports the share
of the footprint that **cannot** be restated at all.

The limit of the restatement
----------------------------
EXIOBASE reports HFC and PFC already aggregated in kg CO2-equivalent rather
than as individual species. Whatever GWP vintage was used to aggregate them is
fixed inside the data and cannot be recovered from the satellite account, so
those two stressors are excluded from the restatement and their share is
reported. Everything else - CO2, CH4, N2O, SF6 - is an individual gas in kg and
is fully restatable.

AR6 also distinguishes **fossil from non-fossil methane** (29.8 against 27.0),
which the single AR4 factor of 25 did not. Fossil-origin methane carries the
extra CO2 produced when it oxidises.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.gwp_vintage``
"""

from __future__ import annotations

import os
import pickle
from typing import Any

import numpy as np
import pandas as pd

from analysis.constants import (ANALYSIS_YEAR, BACKGROUND_YEAR, DK_POPULATION,
                                K_DK, MODEL_LABEL, N_FINAL_DEMAND,
                                ar6_gwp_factor)
from paths import BACKGROUND_DIR, MRIO_DIR, OUTPUT_DIR

FOLDER = "15_gwp_vintage"

#: GWP100 by IPCC assessment report. Methane is split fossil/non-fossil only
#: from AR6; earlier assessments published a single value, applied to both.
#:
#: Sources: SAR (1995) table 2.9; TAR (2001) table 6.7; AR4 (2007) table 2.14;
#: AR5 (2013) table 8.7 (without climate-carbon feedback for non-CO2);
#: AR6 (2021) WG1 chapter 7 table 7.15.
VINTAGES: dict[str, dict[str, float]] = {
    "IPCC SAR (1995)": dict(CO2=1.0, CH4_fossil=21.0, CH4_biogenic=21.0,
                            N2O=310.0, SF6=23_900.0),
    "IPCC TAR (2001)": dict(CO2=1.0, CH4_fossil=23.0, CH4_biogenic=23.0,
                            N2O=296.0, SF6=22_200.0),
    "IPCC AR4 (2007)": dict(CO2=1.0, CH4_fossil=25.0, CH4_biogenic=25.0,
                            N2O=298.0, SF6=22_800.0),
    "IPCC AR5 (2013)": dict(CO2=1.0, CH4_fossil=30.0, CH4_biogenic=28.0,
                            N2O=265.0, SF6=23_500.0),
    "IPCC AR6 (2021)": dict(CO2=1.0, CH4_fossil=29.8, CH4_biogenic=27.0,
                            N2O=273.0, SF6=25_200.0),
}


def _species(stressor: str) -> str | None:
    """Classify one stressor into a gas species key, or ``None``.

    Parameters
    ----------
    stressor : str
        EXIOBASE stressor label.

    Returns
    -------
    str or None
        One of ``"CO2"``, ``"CH4_fossil"``, ``"CH4_biogenic"``, ``"N2O"`` or
        ``"SF6"``; ``None`` for stressors outside the restatement, including
        the pre-aggregated HFC and PFC.
    """
    factor = ar6_gwp_factor(stressor)
    if factor is None:
        return None
    head = str(stressor).split(" - ")[0].strip().upper()
    if head == "CH4":
        return "CH4_fossil" if factor == 29.8 else "CH4_biogenic"
    return {"CO2": "CO2", "N2O": "N2O", "SF6": "SF6"}.get(head)


def main() -> None:
    """Compute the vintage sensitivity and write it to the gold folder."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(str(MRIO_DIR),
                           f"mrio{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        mrio = pickle.load(fh)
    with open(os.path.join(str(MRIO_DIR),
                           f"leontief{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        leontief = pickle.load(fh)
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"),
              "rb") as fh:
        background = pickle.load(fh)

    raw = mrio["R"]
    output = mrio["x"][:, 0]
    labels = list(mrio["label"]["extension"].iloc[:, 0])
    gwp_row = mrio["Q"][0, :]

    inverse = np.divide(1.0, output, out=np.zeros_like(output),
                        where=output > 0)
    intensities = raw * inverse[np.newaxis, :]

    health = intensities @ (leontief @ background["Ystim"][:, 0])
    nation = intensities @ (leontief @ mrio["Y"][
        :, K_DK * N_FINAL_DEMAND:(K_DK + 1) * N_FINAL_DEMAND].sum(axis=1))

    # mass by species, and the CO2-equivalent already fixed inside EXIOBASE
    mass_health: dict[str, float] = {}
    mass_nation: dict[str, float] = {}
    fixed_health = fixed_nation = 0.0
    for index, label in enumerate(labels):
        key = _species(label)
        if key is not None:
            mass_health[key] = mass_health.get(key, 0.0) + health[index]
            mass_nation[key] = mass_nation.get(key, 0.0) + nation[index]
        elif gwp_row[index] != 0:
            fixed_health += gwp_row[index] * health[index]
            fixed_nation += gwp_row[index] * nation[index]

    rows: list[dict[str, Any]] = []
    population = DK_POPULATION[ANALYSIS_YEAR]
    for name, factors in VINTAGES.items():
        h = sum(mass_health.get(k, 0.0) * f for k, f in factors.items()) \
            + fixed_health
        n = sum(mass_nation.get(k, 0.0) * f for k, f in factors.items()) \
            + fixed_nation
        rows.append(dict(
            country_consuming="DNK", analysis_year=ANALYSIS_YEAR,
            gwp_vintage=name, is_study_default=name.startswith("IPCC AR6"),
            healthcare_kt_co2eq=h / 1e6, national_kt_co2eq=n / 1e6,
            healthcare_share_pct=100.0 * h / n if n else np.nan,
            healthcare_t_per_capita=h / 1e3 / population,
            not_restatable_kt_co2eq=fixed_health / 1e6,
            not_restatable_share_pct=100.0 * fixed_health / h if h else np.nan,
            model=MODEL_LABEL,
            note="HFC and PFC are supplied by EXIOBASE already in CO2eq and "
                 "keep whatever vintage EXIOBASE used; they are excluded from "
                 "the restatement and reported in not_restatable_*"))
    table = pd.DataFrame(rows)
    table.to_csv(os.path.join(out_dir, "gwp_vintage_sensitivity.csv"),
                 index=False)

    species = pd.DataFrame([
        dict(country_consuming="DNK", sector_consuming="health_and_eldercare",
             species=k, mass_kg=v, unit="kg",
             ar6_gwp100=VINTAGES["IPCC AR6 (2021)"][k],
             contribution_kt_co2eq=v * VINTAGES["IPCC AR6 (2021)"][k] / 1e6)
        for k, v in sorted(mass_health.items(), key=lambda kv: -kv[1])])
    species.loc[len(species)] = dict(
        country_consuming="DNK", sector_consuming="health_and_eldercare",
        species="HFC + PFC (pre-aggregated by EXIOBASE)",
        mass_kg=np.nan, unit="kg CO2eq", ar6_gwp100=np.nan,
        contribution_kt_co2eq=fixed_health / 1e6)
    species.to_csv(os.path.join(out_dir, "gwp_by_species.csv"), index=False)

    pd.set_option("display.width", 200)
    print(table[["gwp_vintage", "healthcare_kt_co2eq", "national_kt_co2eq",
                 "healthcare_t_per_capita", "is_study_default"]]
          .to_string(index=False))
    print(f"\nNot restatable (HFC + PFC, already CO2eq in EXIOBASE): "
          f"{fixed_health / 1e6:,.1f} kt = "
          f"{100 * fixed_health / (sum(mass_health.get(k, 0.0) * f for k, f in VINTAGES['IPCC AR6 (2021)'].items()) + fixed_health):.1f} %"
          " of the AR6 health-care footprint")
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
