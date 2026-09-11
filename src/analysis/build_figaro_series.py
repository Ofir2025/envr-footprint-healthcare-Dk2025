# -*- coding: utf-8 -*-
"""Consolidate the FIGARO extracts into two time series, each one file.

Motivation
----------
Bronze holds one file per dissemination-API query, because that is what bronze
is: the retrieval, named after what was asked for. A query can only ask for the
years that sit in one dataset block, and Eurostat splits the FIGARO supply and
use tables into four-year blocks, so 2016, 2019 and 2022 arrive as three files
from three datasets. Reading a series out of that means globbing a folder and
trusting the filenames.

This module writes the series instead: one file per grain, a ``year`` column,
every year in it. Two of them, because there are two grains and a table has one.

``figaro_dk_health_inputs.csv``
    What Danish health activities buy, by year: the use table's ``Q86`` and
    ``Q87_88`` columns, intermediate inputs only. This is the FIGARO side of the
    three-way recipe validation, as a series rather than one year.

``figaro_dk_footprint_series.csv``
    Denmark's consumption-based footprint by year, origin and final-demand
    category, both indicators, at ``nace_r2 = TOTAL``.

Keys, not labels
----------------
Both files carry codes and no labels, and join to
``figaro_dimensions.csv`` on ``fact_column`` and ``code``. Denormalising the
label onto 28,000 fact rows would put Eurostat's wording in two places and let
them drift; the dimension table is where a label is allowed to live.

What is excluded, and why it has to be
-------------------------------------
The health-input series keeps only ``prd_ava`` codes typed ``product``. The use
table's rows are products *and* primary inputs -- ``D1`` compensation of
employees, ``B2A3G`` gross operating surplus, two net-tax rows -- and the two
residents adjustments; an input recipe that included value added would not be an
input recipe. The footprint series keeps every ``c_orig`` and flags the three
aggregates, rather than dropping them, because a consumer comparing against a
published EU or world total needs them and a consumer summing needs to know
which to leave out. ``WRL_REST`` is not one of them: it is the residual for the
countries FIGARO does not resolve individually and belongs in the sum.
"""

from __future__ import annotations

import pandas as pd

from analysis.build_figaro_dimensions import load_dimensions
from paths import BRONZE_DIR, SILVER_EUROSTAT_FIGARO_DIR

#: Where the bronze extracts are.
BRONZE_FIGARO_DIR = BRONZE_DIR / "eurostat_figaro"

#: The health industries of the FIGARO use table. ``Q86`` is human health
#: activities; ``Q87_88`` is residential care and social work without
#: accommodation, which the Danish expenditure boundary splits between eldercare
#: and childcare and FIGARO does not.
HEALTH_INDUSTRIES = ("Q86", "Q87_88")

#: Outputs.
HEALTH_INPUTS_CSV = "figaro_dk_health_inputs.csv"
FOOTPRINT_SERIES_CSV = "figaro_dk_footprint_series.csv"


def _codes(fact_column: str, *entry_types: str) -> set[str]:
    """Return the codes of one fact column with any of the given types.

    Parameters
    ----------
    fact_column : str
        A column of the bronze fact tables.
    *entry_types : str
        ``entry_type`` values to keep.

    Returns
    -------
    set of str
        Matching codes.
    """
    frame = load_dimensions()
    rows = frame[(frame.fact_column == fact_column)
                 & frame.entry_type.isin(entry_types)]
    return set(rows.code)


def build_health_inputs() -> pd.DataFrame:
    """Build the Danish health input series from the FIGARO use tables.

    Returns
    -------
    pandas.DataFrame
        Columns ``year``, ``using_industry``, ``product``, ``origin``,
        ``unit``, ``value``, sorted by year then industry then product then
        descending value.

    Raises
    ------
    FileNotFoundError
        If no use-table extract is in bronze.
    """
    files = sorted(BRONZE_FIGARO_DIR.glob("figaro2026_use_*dest_*.csv"))
    if not files:
        raise FileNotFoundError(
            f"no use-table extract in {BRONZE_FIGARO_DIR}; run\n"
            "  PYTHONPATH=src .venv/bin/python -m analysis.fetch_figaro "
            "--years 2016 2019 2022 --tables use")
    products = _codes("prd_ava", "product")
    frames = []
    for path in files:
        frame = pd.read_csv(path)
        frame = frame[frame.ind_use.isin(HEALTH_INDUSTRIES)
                      & frame.prd_ava.isin(products)]
        frames.append(frame)
    series = pd.concat(frames, ignore_index=True)
    series = series.rename(columns={"time": "year", "ind_use": "using_industry",
                                    "prd_ava": "product", "c_orig": "origin"})
    series = series[["year", "using_industry", "product", "origin", "unit",
                     "value"]]
    return series.sort_values(["year", "using_industry", "product", "value"],
                              ascending=[True, True, True, False]
                              ).reset_index(drop=True)


def build_footprint_series() -> pd.DataFrame:
    """Build the Danish footprint series from the FIGARO footprint accounts.

    Returns
    -------
    pandas.DataFrame
        Columns ``year``, ``indicator``, ``origin``, ``origin_is_aggregate``,
        ``final_demand``, ``unit``, ``value``, sorted by year then indicator
        then descending value.

    Raises
    ------
    FileNotFoundError
        If no footprint extract is in bronze.
    """
    datasets = {"env_ac_ghgfp": "greenhouse_gas",
                "env_ac_co2fp": "carbon_dioxide"}
    aggregates = _codes("c_orig", "country_aggregate")
    frames = []
    for dataset, indicator in datasets.items():
        for path in sorted(BRONZE_FIGARO_DIR.glob(f"{dataset}_DKdest_*.csv")):
            frame = pd.read_csv(path)
            frame = frame[frame.nace_r2 == "TOTAL"].copy()
            frame["indicator"] = indicator
            frames.append(frame)
    if not frames:
        raise FileNotFoundError(
            f"no footprint extract in {BRONZE_FIGARO_DIR}; run\n"
            "  PYTHONPATH=src .venv/bin/python -m analysis.fetch_figaro "
            "--years 2016 2019 2022 --tables footprints")
    series = pd.concat(frames, ignore_index=True)
    series = series.rename(columns={"time": "year", "c_orig": "origin",
                                    "na_item": "final_demand"})
    series["origin_is_aggregate"] = series.origin.isin(aggregates)
    series = series[["year", "indicator", "origin", "origin_is_aggregate",
                     "final_demand", "unit", "value"]]
    return series.sort_values(["year", "indicator", "value"],
                              ascending=[True, True, False]
                              ).reset_index(drop=True)


def main() -> None:
    """Write both series to silver and report what they cover."""
    SILVER_EUROSTAT_FIGARO_DIR.mkdir(parents=True, exist_ok=True)

    health = build_health_inputs()
    health_path = SILVER_EUROSTAT_FIGARO_DIR / HEALTH_INPUTS_CSV
    health.to_csv(health_path, index=False)

    footprint = build_footprint_series()
    footprint_path = SILVER_EUROSTAT_FIGARO_DIR / FOOTPRINT_SERIES_CSV
    footprint.to_csv(footprint_path, index=False)

    print("Danish health inputs, MIO_EUR, intermediate only")
    total = (health.groupby(["year", "using_industry"]).value.sum()
             .unstack().round(1))
    print(total.to_string())
    print(f"\n{len(health):,} rows -> {health_path}")

    print("\nDanish footprint, kt CO2-eq and kt CO2, at c_orig = WORLD, "
          "na_item = TOTAL")
    world = footprint[(footprint.origin == "WORLD")
                      & (footprint.final_demand == "TOTAL")]
    print(world.pivot(index="year", columns="indicator",
                      values="value").round(1).to_string())
    print(f"\n{len(footprint):,} rows -> {footprint_path}")


if __name__ == "__main__":
    main()
