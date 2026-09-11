# -*- coding: utf-8 -*-
"""Bridge the 2019 and 2022 results, and say what the comparison does and does not mean.

The two reference years are the study's most easily misread pair of numbers. The
climate footprint falls by 26 % between them while every other impact category
rises by 36 % to 66 %, which looks like a contradiction and is not. Three things
change at once between the runs, and only one of them is the passage of time:

1. **the reference year**, 2019 to 2022, worth +15 % on expenditure;
2. **the background model**, EXIOBASE v3.8.2 IOT_2016 to IOT_2022;
3. **the Danish sea-transport reallocation**, absent from the 2019 run because
   no corrected 2016 background had been built, applied to the 2022 run.

A reader who takes the difference as a trend attributes the third to the first.
Since ``analysis.dk_shipping_correction`` now also runs on the 2016 background,
point 3 no longer has to be confounded with the other two: :func:`two_step_bridge`
below isolates it as its own step, using the variant folders
``2019_uncorrected`` / ``2019c`` / ``2022_uncorrected`` / ``2022c``
Eriksen folders. :func:`totals` and :func:`climate_bridge` are kept as they were
for continuity with the submitted (2019, uncorrected) versus headline
(2022, shipping-corrected) comparison the manuscript figures still draw on; they
still confound all three points and remain explicitly labelled as not a trend.

The two-step decomposition is the argument. Two activity groups account for
essentially the whole climate movement in opposite directions - transport falls
as the phantom Danish shipping input is removed (the correction step, present
in both years once both are corrected), pharmaceuticals and chemical products
rise as expenditure grows between 2019 and 2022 (the year step) - and every
other group together moves by much less.

Run
---
``PYTHONPATH=src python -m analysis.year_comparison``
"""

from __future__ import annotations

import os
from typing import Any

import numpy as np
import pandas as pd

from analysis.constants import DK_POPULATION, eriksen_folder
from paths import OUTPUT_DIR

FOLDER = "06_benchmarks_validation"
YEARS = ("2019", "2022")
#: Which background-correction variant :func:`totals` and :func:`climate_bridge`
#: read for each year - preserved exactly as the historical (submitted vs.
#: headline) comparison, i.e. 2019 uncorrected against 2022 shipping-corrected,
#: so those two functions keep confounding what the manuscript figures already
#: confound, rather than silently changing meaning under an unchanged docstring.
_LEGACY_TAG: dict[str, str] = {"2019": "", "2022": "_snacship"}

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
    """Read one table from a year's (legacy-tagged) Eriksen variant folder."""
    # By keyword: eriksen_folder resolves four axes, and a positional
    # second argument is the RELEASE, not the tag.
    folder = eriksen_folder(year, tag=_LEGACY_TAG[year])
    return pd.read_csv(os.path.join(str(OUTPUT_DIR), folder, name))


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


#: The three nodes of the honest, two-step bridge, named by the variant folder
#: each one reads: the manuscript's own uncorrected 2019 run, the same 2019
#: expenditure corrected for the phantom Danish shipping input (variant c on the
#: 2016 table), and the 2022 headline (variant c on the 2022 table). The step
#: 2019_uncorrected -> 2019c isolates the correction alone (same year, same
#: background release); the step 2019c -> 2022c isolates the year alone (same
#: correction state, release, boundary and capital treatment on both ends).
#:
#: All three are on EXIOBASE v3.8.2, which is what makes the first step the
#: correction ALONE. None of them is variant a or b: those are on v3.7, so a
#: bridge through them would move the release at the same time and measure two
#: things at once - which is precisely what this decomposition exists to avoid.
#: The bridge chain, in order. Each consecutive pair is one step, and each step
#: changes exactly ONE thing, which is the whole point of drawing it as a chain
#: rather than as a single before-and-after.
#:
#: It used to start at 2019 and run three nodes, because no 2016 analysis
#: existed. It now starts at 2016, which moves the sea-transport correction onto
#: the EARLIEST year and leaves two clean year steps on a configuration that does
#: not otherwise change: same release, same correction state, same boundary,
#: same capital treatment. A reader can therefore see the correction once and the
#: reference-year growth twice, instead of seeing them confounded in one move.
BRIDGE_NODES: tuple[str, ...] = ("2016_uncorrected", "2016c", "2019c", "2022c")
_BRIDGE_YEAR_TAG: dict[str, tuple[str, str]] = {
    "2016_uncorrected": ("2016", ""),
    "2016c": ("2016", "_snacship"),
    "2019c": ("2019", "_snacship"),
    "2022c": ("2022", "_snacship"),
}

#: What each step changes, in the order of :data:`BRIDGE_NODES`.
BRIDGE_STEPS: tuple[tuple[str, str, str], ...] = (
    ("delta_correction_kt", "2016_uncorrected", "2016c"),
    ("delta_2016_2019_kt", "2016c", "2019c"),
    ("delta_2019_2022_kt", "2019c", "2022c"),
)


def two_step_bridge() -> pd.DataFrame:
    """Decompose the climate difference into a correction step and a year step.

    Returns
    -------
    pandas.DataFrame
        One row per activity (``contribution_group``), with the climate-change
        value at each of the three :data:`BRIDGE_NODES`, the two deltas
        (``delta_correction_kt``, ``delta_year_kt``), each delta's share of its
        own step's net movement, and which single step each group's movement is
        attributed to.
    """
    frames: dict[str, pd.Series] = {}
    for node in BRIDGE_NODES:
        year, tag = _BRIDGE_YEAR_TAG[node]
        d = pd.read_csv(os.path.join(
            str(OUTPUT_DIR), eriksen_folder(year, tag=tag),
            "figure1_activity_contributions.csv"))
        d = d[d.indicator == "climate_change"]
        frames[node] = d.set_index("contribution_group")["value"]
    wide = pd.DataFrame(frames).fillna(0.0)
    wide.columns = [f"value_{c}" for c in wide.columns]
    for name, a, b in BRIDGE_STEPS:
        wide[name] = wide[f"value_{b}"] - wide[f"value_{a}"]
    # Kept under its old name as well: the two-step figure and the revision
    # documents refer to `delta_year_kt`, and the quantity they mean is the
    # 2019-to-2022 step.
    wide["delta_year_kt"] = wide["delta_2019_2022_kt"]
    wide = wide.reset_index()

    for name, _a, _b in BRIDGE_STEPS:
        total = float(wide[name].sum())
        wide[f"share_of_{name[6:-3]}_change_pct"] = (
            100 * wide[name] / total if total else np.nan)
    wide["share_of_year_change_pct"] = wide["share_of_2019_2022_change_pct"]
    wide["driver"] = np.where(
        wide["contribution_group"].eq("Transport"),
        "correction step: sea-transport reallocation; "
        "year step: expenditure and background growth, transport unaffected "
        "once both ends are corrected",
        np.where(wide["contribution_group"].eq(
            "Pharmaceuticals and chemical products"),
            "year step: expenditure growth and a larger chemicals block in "
            "IOT_2022; little affected by the correction",
            "background model and expenditure growth, no single dominant "
            "cause in either step"))
    return wide.sort_values("delta_2019_2022_kt").reset_index(drop=True)


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
    tb = two_step_bridge()
    tb.to_csv(os.path.join(out_dir, "year_comparison_two_step_bridge.csv"),
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

    print("\nThree-step bridge, kt CO2eq "
          "(shipping correction on 2016, then 2016-2019, then 2019-2022)")
    print(tb[["contribution_group", *[f"value_{n}" for n in BRIDGE_NODES],
              *[name for name, _a, _b in BRIDGE_STEPS]]]
          .round(1).to_string(index=False))
    for name, a, b in BRIDGE_STEPS:
        print(f"  {a} -> {b}: net {float(tb[name].sum()):+,.1f} kt")
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
