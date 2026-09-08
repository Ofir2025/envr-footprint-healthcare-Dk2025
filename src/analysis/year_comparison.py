# -*- coding: utf-8 -*-
"""Bridge the 2019 and 2022 results, and say what the comparison does and does not mean.

The two reference years are the study's most easily misread pair of numbers. The
climate footprint falls by 26 % between them while every other impact category
rises by 36 % to 66 %, which looks like a contradiction and is not. Three things
change at once between the runs, and only one of them is the passage of time:

1. **the reference year**, 2019 to 2022, worth +15 % on expenditure;
2. **the background model**, EXIOBASE v3.8.2 IOT_2016 to IOT_2022;
3. **the Danish sea-transport reallocation**, absent from the 2019 run because
   no corrected 2016 background has been built, applied to the 2022 run.

A reader who takes the difference as a trend attributes the third to the first.
This module writes the bridge that prevents that: totals for both years, the
per-activity decomposition of the climate difference, and an explicit statement
of which comparisons are valid.

The decomposition is the argument. Two activity groups account for essentially
the whole climate movement in opposite directions - transport falls by
2,009 kt CO2e as the phantom Danish shipping input is removed, pharmaceuticals
and chemical products rise by 887 kt as expenditure grows and the corrected
demand vector reaches spending the submitted study did not - and everything else
together moves by less than 240 kt.

Run
---
``PYTHONPATH=src python -m analysis.year_comparison``
"""

from __future__ import annotations

import os
from typing import Any

import numpy as np
import pandas as pd

from analysis.constants import DK_POPULATION, ERIKSEN_ROOT
from paths import OUTPUT_DIR

FOLDER = "06_benchmarks_validation"
YEARS = ("2019", "2022")

#: What differs between the two runs, and whether it is a change in the world
#: or a change in the model.
RUN_DIFFERENCES: tuple[dict[str, str], ...] = (
    dict(dimension="reference year", y2019="2019", y2022="2022",
         kind="change in the world",
         effect="health-care expenditure rises 15 %, from 35,271 to "
                "40,597 M.EUR"),
    dict(dimension="background model",
         y2019="EXIOBASE v3.8.2 IOT_2016_ixi",
         y2022="EXIOBASE v3.8.2 IOT_2022_ixi",
         kind="change in the model",
         effect="different technology structure and different satellite "
                "accounts; not a like-for-like technology comparison"),
    dict(dimension="Danish sea-transport reallocation",
         y2019="not applied", y2022="applied",
         kind="change in the model",
         effect="removes the phantom domestic shipping input; the dominant "
                "single cause of the climate difference"),
    dict(dimension="demand vector",
         y2019="corrected (all individual-consumption transactions)",
         y2022="corrected (all individual-consumption transactions)",
         kind="the same in both",
         effect="both runs use this study's extraction, not the submitted "
                "manuscript's hand-enumerated list, so the demand-vector "
                "correction is NOT part of the difference between them"),
)


def _read(year: str, name: str) -> pd.DataFrame:
    """Read one table from a year's Eriksen folder."""
    return pd.read_csv(os.path.join(str(OUTPUT_DIR), ERIKSEN_ROOT, year, name))


def totals() -> pd.DataFrame:
    """Headline totals for both years, with per-capita values.

    Returns
    -------
    pandas.DataFrame
        One row per indicator, with both years, the ratio, and the per-capita
        values that make the comparison population-adjusted.
    """
    frames = []
    for year in YEARS:
        d = _read(year, "figure1_activity_contributions.csv")
        t = (d.groupby(["indicator", "unit"])["value"].sum()
             .reset_index().assign(year=year))
        t["per_capita"] = t["value"] * 1e6 / DK_POPULATION[year]
        frames.append(t)
    long = pd.concat(frames, ignore_index=True)
    wide = long.pivot_table(index=["indicator", "unit"], columns="year",
                            values=["value", "per_capita"])
    wide.columns = [f"{a}_{b}" for a, b in wide.columns]
    wide = wide.reset_index()
    wide["ratio_2022_over_2019"] = wide["value_2022"] / wide["value_2019"]
    wide["change_pct"] = 100 * (wide["ratio_2022_over_2019"] - 1)
    wide["per_capita_unit"] = wide["unit"].map({
        "kt CO2eq": "kg CO2eq per person", "kt": "kg per person",
        "Mm3": "m3 per person", "km2": "m2 per person"})
    wide["comparable_as_a_trend"] = False
    wide["why_not"] = (
        "the background model and the sea-transport correction differ between "
        "the runs, so the difference is not a time series")
    return wide


def climate_bridge() -> pd.DataFrame:
    """Decompose the climate difference by activity group.

    Returns
    -------
    pandas.DataFrame
        One row per contribution group, sorted by the size of the movement,
        with the share of the total difference each explains.
    """
    frames = {}
    for year in YEARS:
        d = _read(year, "figure1_activity_contributions.csv")
        d = d[d.indicator == "climate_change"]
        frames[year] = d.set_index("contribution_group")[["value", "share_pct"]]
    b = frames["2019"].join(frames["2022"], lsuffix="_2019", rsuffix="_2022",
                            how="outer").fillna(0.0)
    b["delta_kt"] = b["value_2022"] - b["value_2019"]
    total = float(b["delta_kt"].sum())
    b["share_of_total_change_pct"] = 100 * b["delta_kt"] / total
    b = b.sort_values("delta_kt").reset_index()
    b["driver"] = np.where(
        b["contribution_group"].eq("Transport"),
        "sea-transport reallocation, applied in 2022 only",
        np.where(b["contribution_group"].eq(
            "Pharmaceuticals and chemical products"),
            "expenditure growth and a larger chemicals block in IOT_2022",
            "background model and expenditure, no single dominant cause"))
    return b


def main() -> None:
    """Write the year bridge and print it."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)

    t = totals()
    t.to_csv(os.path.join(out_dir, "year_comparison_2019_2022.csv"),
             index=False)
    b = climate_bridge()
    b.to_csv(os.path.join(out_dir, "year_comparison_climate_bridge.csv"),
             index=False)
    pd.DataFrame(RUN_DIFFERENCES).to_csv(
        os.path.join(out_dir, "year_comparison_run_differences.csv"),
        index=False)

    pd.set_option("display.width", 220)
    print("Totals")
    print(t[["indicator", "unit", "value_2019", "value_2022",
             "change_pct"]].round(2).to_string(index=False))
    print("\nClimate bridge, kt CO2eq")
    print(b[["contribution_group", "value_2019", "value_2022", "delta_kt",
             "share_of_total_change_pct"]].round(1).to_string(index=False))
    net = float(b["delta_kt"].sum())
    two = float(b.loc[b.contribution_group.isin(
        ["Transport", "Pharmaceuticals and chemical products"]),
        "delta_kt"].abs().sum())
    rest = float(b.loc[~b.contribution_group.isin(
        ["Transport", "Pharmaceuticals and chemical products"]),
        "delta_kt"].abs().sum())
    print(f"\nnet change {net:,.1f} kt; transport and pharmaceuticals move "
          f"{two:,.1f} kt in opposite directions, every other group together "
          f"{rest:,.1f} kt")
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
