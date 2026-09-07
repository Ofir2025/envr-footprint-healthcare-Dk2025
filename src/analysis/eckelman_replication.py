# -*- coding: utf-8 -*-
"""Eckelman & Sherman (2016) replication: Denmark on their nine-category frame.

Eckelman & Sherman, *Environmental impacts of the US health care system and
effects on public health* (PLoS ONE 2016), report nine impact categories plus
health damage in DALYs. This module places Denmark 2022 beside every one of
them.

What can and cannot be compared
-------------------------------
Their absolute values are in TRACI reference substances as implemented inside
the CMU EIO-LCA tool — PM\\ :sub:`10`-equivalents, benzene-equivalents,
toluene-equivalents. Our characterisation uses CML 1999 and the ILCD
recommended factors, whose reference substances differ. **Absolute values are
therefore not comparable and are not compared here.**

Two things are:

*Share of the national total.* This is unit-free, it is what their abstract
leads with, and it is what a reader wants: how much of a country's
environmental pressure its health system accounts for.

*Damage in DALYs.* Both studies produce them, and both express them per head of
population once normalised.

A caution on their own numbers
------------------------------
Their supplementary table S3 contradicts their table 1, figure 2 and body text
on the demand-side shares, and their S4 toxicity values disagree with table 2 by
factors of 2.9 and 13. Table 2 is the table the paper was written from and is
what is transcribed here. Their table 2 PM row also mixes reference substances
between its own columns — the health-care figure is in PM\\ :sub:`10`-equivalents
and the national total in PM\\ :sub:`2.5`-equivalents, with a factor 1.67
conversion applied silently between them — so a reader recomputing the
percentage from the printed table gets 14.7 % rather than the reported 8.9 %.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.eckelman_replication``
"""

from __future__ import annotations

import os
from typing import Any

import numpy as np
import pandas as pd

from analysis.constants import ANALYSIS_YEAR, DK_POPULATION, MODEL_LABEL
from paths import OUTPUT_DIR

FOLDER = "14_eckelman_replication"

#: US resident population, mid-2013, the reference year of their study.
US_POPULATION_2013: int = 316_128_839

#: Their table 2, "Environmental and health effects due to health care sector
#: direct and indirect emissions for 2013". ``share_pct`` is their reported
#: percentage of the national total; ``daly`` their damage estimate.
#: ``national_total`` is absent for ecotoxicity, for which they state no
#: national normalisation set exists.
ECKELMAN_TABLE2: dict[str, dict[str, Any]] = {
    "GW": dict(name="Global warming", unit="kg CO2-e",
               health_care=6.6e11, national=6.5e12, share_pct=9.8, daly=np.nan),
    "AP": dict(name="Acidification potential", unit="kg SO2-e",
               health_care=3.1e9, national=2.6e10, share_pct=11.7,
               daly=np.nan),
    "PM": dict(name="Particulate matter", unit="kg PM10-e",
               health_care=1.0e9, national=6.8e9, share_pct=8.9,
               daly=435_000),
    "EP": dict(name="Eutrophication potential", unit="kg N-e",
               health_care=9.4e7, national=6.1e9, share_pct=1.5, daly=np.nan),
    "ODP": dict(name="Ozone depletion potential", unit="kg CFC-11-e",
                health_care=7.3e5, national=4.5e7, share_pct=1.6, daly=770),
    "POP": dict(name="Photochemical oxidation (smog)", unit="kg O3-e",
                health_care=4.0e10, national=3.9e11, share_pct=10.0,
                daly=9_400),
    "ETP": dict(name="Ecotoxicity potential", unit="kg 2,4-D-e",
                health_care=6.9e7, national=np.nan, share_pct=np.nan,
                daly=np.nan),
    "HH_canc": dict(name="Human health, cancer effects", unit="kg benzene-e",
                    health_care=2.5e8, national=2.6e10, share_pct=1.0,
                    daly=84),
    "HH_noncanc": dict(name="Human health, non-cancer effects",
                       unit="kg toluene-e", health_care=6.9e11,
                       national=3.3e13, share_pct=2.2, daly=25_300),
}

#: Which of our computed categories stands in for each of theirs. The
#: reference substances differ, so this pairs *concepts*, not units. The
#: baseline variant of each method is used wherever one exists.
CATEGORY_MAP: dict[str, tuple[str, str]] = {
    "GW": ("Problem oriented approach: baseline (CML, 1999)",
           "global warming GWP100"),
    "AP": ("Problem oriented approach: baseline (CML, 1999)",
           "acidification (incl. fate, average Europe total, A&B)"),
    "PM": ("ILCD recommended CF",
           "Particulate matter/Respiratory inorganics midpoint"),
    "EP": ("Problem oriented approach: baseline (CML, 1999)",
           "eutrophication (fate not incl.)"),
    "ODP": ("Problem oriented approach: baseline (CML, 1999)",
            "ozone layer depletion ODP steady state "),
    "POP": ("Problem oriented approach: baseline (CML, 1999)",
            "photochemical oxidation (high NOx)"),
    "ETP": ("Problem oriented approach: baseline (CML, 1999)",
            "Freshwater aquatic ecotoxicity FAETP inf. "),
    "HH_canc": ("ILCD recommended CF",
                "Human toxicity midpoint, cancer effects"),
    "HH_noncanc": ("ILCD recommended CF",
                   "Human toxicity midpoint, non-cancer effects"),
}

#: Our ILCD endpoint categories that yield DALYs, and the Eckelman damage
#: category each corresponds to. Their study assigns no DALYs to climate
#: change, stating that robust endpoint factors do not exist; ours does, so it
#: is reported separately and excluded from the like-for-like total.
DALY_MAP: dict[str, str] = {
    "PM": "Particulate matter/Respiratory inorganics endpoint",
    "HH_canc": "Human toxicity endpoint, cancer effects",
    "HH_noncanc": "Human toxicity endpoint, non-cancer effects",
}
DALY_CLIMATE = "Climate change endpoint, human health"


def _load_full() -> pd.DataFrame:
    """Read the full impact-category table, keeping only trustworthy rows."""
    path = os.path.join(str(OUTPUT_DIR), "12_impact_categories_full",
                        "impact_categories_all_methods.csv")
    frame = pd.read_csv(path)
    return frame[frame.quality_flag == "ok"]


def _lookup(frame: pd.DataFrame, method: str, indicator: str) -> pd.Series:
    """Find one category, failing loudly if the label does not match.

    Raises
    ------
    KeyError
        If the (method, indicator) pair matches no row, so a silent NaN can
        never be mistaken for a genuine zero.
    """
    hit = frame[(frame.method == method) & (frame.indicator == indicator)]
    if hit.empty:
        hit = frame[(frame.method == method)
                    & (frame.indicator.str.strip() == indicator.strip())]
    if hit.empty:
        raise KeyError(f"no category matches {method!r} / {indicator!r}")
    return hit.iloc[0]


def main() -> None:
    """Build and write the Denmark-versus-United-States comparison."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)
    frame = _load_full()
    dk_population = DK_POPULATION[ANALYSIS_YEAR]

    rows: list[dict[str, Any]] = []
    for code, published in ECKELMAN_TABLE2.items():
        method, indicator = CATEGORY_MAP[code]
        ours = _lookup(frame, method, indicator)
        rows.append(dict(
            eckelman_code=code, effect_category=published["name"],
            us_unit=published["unit"], us_health_care=published["health_care"],
            us_national=published["national"],
            us_share_of_national_pct=published["share_pct"],
            dk_method=method, dk_indicator=indicator,
            dk_unit=ours["unit"],
            dk_health_care=ours["healthcare_supply_chain"],
            dk_national=ours["national_supply_chain"],
            dk_share_of_national_pct=ours["healthcare_share_of_national_pct"],
            share_difference_pp=(ours["healthcare_share_of_national_pct"]
                                 - published["share_pct"])
            if np.isfinite(published["share_pct"]) else np.nan,
            comparability="shares only; reference substances differ between "
                          "TRACI-in-EIOLCA and CML/ILCD, so absolute values "
                          "are not comparable",
            source_us="Eckelman & Sherman 2016, PLoS ONE 11(6):e0157014, "
                      "table 2",
            source_dk=MODEL_LABEL))
    comparison = pd.DataFrame(rows)
    comparison.insert(0, "analysis_year_denmark", ANALYSIS_YEAR)
    comparison.insert(1, "reference_year_us", 2013)
    comparison.to_csv(
        os.path.join(out_dir, "nine_categories_dk_vs_us.csv"), index=False)

    daly_rows: list[dict[str, Any]] = []
    for code, indicator in DALY_MAP.items():
        ours = _lookup(frame, "ILCD recommended CF", indicator)
        us_daly = ECKELMAN_TABLE2[code]["daly"]
        daly_rows.append(dict(
            damage_category=ECKELMAN_TABLE2[code]["name"],
            us_daly=us_daly,
            us_daly_per_1000=1e3 * us_daly / US_POPULATION_2013
            if np.isfinite(us_daly) else np.nan,
            dk_daly=ours["healthcare_supply_chain"],
            dk_daly_per_1000=1e3 * ours["healthcare_supply_chain"]
            / dk_population,
            us_method="IMPACT 2002+ endpoint factors",
            dk_method="ILCD recommended endpoint factors"))
    climate = _lookup(frame, "ILCD recommended CF", DALY_CLIMATE)
    daly_rows.append(dict(
        damage_category="Climate change (Denmark only)",
        us_daly=np.nan, us_daly_per_1000=np.nan,
        dk_daly=climate["healthcare_supply_chain"],
        dk_daly_per_1000=1e3 * climate["healthcare_supply_chain"]
        / dk_population,
        us_method="not assessed: they state robust endpoint factors do not "
                  "exist for climate change",
        dk_method="ILCD recommended endpoint factors"))
    damage = pd.DataFrame(daly_rows)
    damage.to_csv(os.path.join(out_dir, "damage_daly_dk_vs_us.csv"),
                  index=False)

    pd.set_option("display.width", 200)
    print("Health care's share of the national total, Denmark vs United States")
    print(comparison[["eckelman_code", "effect_category",
                      "us_share_of_national_pct", "dk_share_of_national_pct",
                      "share_difference_pp"]]
          .to_string(index=False, max_colwidth=34))
    print("\nHealth damage (DALY):")
    print(damage[["damage_category", "us_daly_per_1000", "dk_daly_per_1000"]]
          .to_string(index=False, max_colwidth=34))
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
