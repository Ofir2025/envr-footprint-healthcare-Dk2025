# -*- coding: utf-8 -*-
"""Figure-ready tables for the manuscript's figures 1-3, reference year 2022.

The manuscript composes three figures from the same five impact categories:

    Figure 1  activity contributions  - which purchase drives the impact
    Figure 2  sector contributions    - where the impact physically occurs
    Figure 3  geographical origin     - in which world region it occurs

Figures 1 and 2 use a coarse aggregation inherited from Steenmeijer et al., held
in the ``agg_ind_fig`` sheet of the EXIOBASE classification workbook: nine
``Contribution`` groups and eight ``Hotspot`` groups, both mapping from the 19
EXIOBASE aggregate sectors. That grouping is kept unchanged here so the revised
figures stay comparable with the submitted ones.

Two things are corrected relative to the submitted figures:

* the two analyses are read from the right side of the model - ``Contribution``
  from the purchased-product table and ``Hotspot`` from the producing-node
  table. See ``docs/methods/replications/01_eriksen_replication.md``; the file
  stems are named the opposite way round from how they read.
* the world-region aggregation singles out Denmark rather than the Netherlands.

This module writes only tabular data. The figures themselves are drawn in
``R/plot_manuscript_figures.R`` so that every figure in the study comes off one
plotting stack.

Run::

    HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship \\
        PYTHONPATH=src python -m analysis.manuscript_figure_tables
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from paths import BRONZE_DIR, OUTPUT_DIR

FOLDER = "01_eriksen_replication"
OUT = os.path.join(str(OUTPUT_DIR), FOLDER)

#: Impact categories, in the manuscript's order, with display units.
INDICATORS: dict[str, str] = {
    "climate_change": "kt CO2eq",
    "material_extraction": "kt",
    "blue_water_consumption": "Mm3",
    "land_use": "km2",
    "waste_generation": "kt",
}

#: How many origin x industry pairs the ranked figure shows before pooling.
TOP_PAIRS = 20


def figure_group_lookup() -> pd.DataFrame:
    """Map EXIOBASE aggregate sectors onto the manuscript's figure groups.

    Returns
    -------
    pandas.DataFrame
        ``sector_group`` (the EXIOBASE ``AggDescription``), ``contribution_group``
        and ``hotspot_group``. ``Other`` is renamed ``Unallocated``, as in the
        submitted figures.
    """
    path = BRONZE_DIR / "exiobase_v3_7" / "classifications.xlsx"
    fig = pd.read_excel(path, sheet_name="agg_ind_fig", skiprows=5)
    ind = pd.read_excel(path, sheet_name="disagg_ind", skiprows=5)
    ind = ind[ind["Code"].astype(str).str.startswith("A_")]
    bridge = (ind[["AggCode", "AggDescription"]].drop_duplicates()
              .rename(columns={"AggDescription": "sector_group"}))
    out = (bridge.merge(fig, left_on="AggCode", right_on="SAggCode", how="left")
           .rename(columns={"Contribution": "contribution_group",
                            "Hotspot": "hotspot_group"}))
    for col in ("contribution_group", "hotspot_group"):
        out[col] = out[col].fillna("Unallocated").replace({"Other": "Unallocated"})
    # Transport is its own group in both figures. The submitted code matched it
    # by substring, which also caught "Transport Equipment" (vehicle
    # manufacturing) and inflated the transport group - the group at the centre
    # of the finding being withdrawn. Match exactly.
    is_transport = out["sector_group"].eq("Transport")
    out.loc[is_transport, ["contribution_group", "hotspot_group"]] = "Transport"

    # The bottom-up items are not EXIOBASE sectors, so they have no row in the
    # classification workbook. The submitted figures nonetheless show them, and
    # asymmetrically: private travel is an activity a reader can act on, so it
    # is its own group in figure 1, but it has no PRODUCING sector in the model,
    # so on the producing side of figure 2 it is unallocated. Operational
    # impacts are direct emissions of the Danish providers and are named on
    # both sides. Without these rows both groups fall into "Unallocated" and
    # figure 1 loses two of its nine legend entries.
    extra = pd.DataFrame([
        {"sector_group": "Private travel",
         "contribution_group": "Individual travel",
         "hotspot_group": "Unallocated"},
        {"sector_group": "Operational impact",
         "contribution_group": "Operational impacts",
         "hotspot_group": "Operational impacts"},
    ])
    out = pd.concat([out[["sector_group", "contribution_group", "hotspot_group"]],
                     extra], ignore_index=True)
    return out


def _read(name: str) -> pd.DataFrame:
    """Read one gold table from the Eriksen folder."""
    return pd.read_csv(os.path.join(OUT, name))


def _shares(frame: pd.DataFrame, group: str) -> pd.DataFrame:
    """Add the within-indicator percentage share of a grouped table.

    Parameters
    ----------
    frame : pandas.DataFrame
        Table with ``indicator``, ``unit``, ``value`` and ``group``.
    group : str
        Grouping column name.

    Returns
    -------
    pandas.DataFrame
        Sorted, with ``share_pct`` added.
    """
    out = (frame.groupby(["indicator", "unit", group], dropna=False)["value"]
           .sum().reset_index())
    out["share_pct"] = 100 * out["value"] / out.groupby("indicator")[
        "value"].transform("sum")
    return out.sort_values(["indicator", "value"], ascending=[True, False])


def main() -> None:
    """Write the figure 1-3 tables and their ranked-detail variants."""
    lookup = figure_group_lookup()

    # ---- figure 1: activity contributions, on the PURCHASED-product side ----
    contrib = _read("contribution_by_purchased_product.csv")
    contrib = contrib[contrib["indicator"].isin(INDICATORS)]
    contrib = contrib.merge(lookup, left_on="purchased_sector_group",
                            right_on="sector_group", how="left")
    contrib["contribution_group"] = contrib["contribution_group"].fillna("Unallocated")
    fig1 = _shares(contrib, "contribution_group")
    fig1.to_csv(os.path.join(OUT, "figure1_activity_contributions.csv"), index=False)

    # ---- figure 2: sector contributions, on the PRODUCING-node side ---------
    hotspot = _read("hotspot_by_producing_node.csv")
    hotspot = hotspot[hotspot["indicator"].isin(INDICATORS)]
    hotspot = hotspot.merge(lookup, left_on="producing_sector_group",
                            right_on="sector_group", how="left")
    hotspot["hotspot_group"] = hotspot["hotspot_group"].fillna("Unallocated")
    fig2 = _shares(hotspot, "hotspot_group")
    fig2.to_csv(os.path.join(OUT, "figure2_sector_contributions.csv"), index=False)

    # ---- figure 3: geographical origin, producing side ---------------------
    fig3 = _shares(hotspot, "producing_world_region")
    fig3.to_csv(os.path.join(OUT, "figure3_geographical_origin.csv"), index=False)

    # ---- ranked origin x industry pairs, ranked WITHIN each indicator -------
    # Ranking once on climate and reusing that order across panels was tried and
    # discarded: the top climate pairs explain almost nothing of water, land or
    # material, so four of five panels became a single "all other" bar. Each
    # panel is therefore ranked on its own indicator, which is what the figure
    # is for. Bottom-up items carry no producing node (GLO / B_* codes) and are
    # excluded here - they are visible in figures 1 and 3 - so each panel states
    # the share of its indicator that the MRIO supply chain covers.
    keys = ["producing_country_iso3", "producing_world_region",
            "producing_sector_code", "producing_sector_name"]
    mrio = hotspot[(hotspot["producing_country_iso3"] != "GLO")
                   & (~hotspot["producing_sector_code"].astype(str)
                      .str.startswith("B_"))].copy()

    frames = []
    for indicator, sub in mrio.groupby("indicator"):
        rank = (sub.groupby(keys, dropna=False)["value"].sum()
                .sort_values(ascending=False))
        keep = set(rank.head(TOP_PAIRS).index)
        flag = sub.copy()
        flag["is_remainder"] = ~pd.MultiIndex.from_frame(flag[keys]).isin(keep)
        shown = (flag[~flag.is_remainder]
                 .groupby(keys + ["indicator", "unit"], dropna=False)["value"]
                 .sum().reset_index())
        order = {k: i + 1 for i, k in enumerate(rank.head(TOP_PAIRS).index)}
        shown["rank"] = [order[tuple(r)] for r in shown[keys].to_numpy().tolist()]
        rest = (flag[flag.is_remainder]
                .groupby(["indicator", "unit"], dropna=False)["value"]
                .sum().reset_index())
        if not rest.empty:
            for col, val in zip(keys, ["OTH", "Other", "OTHER",
                                       "All other pairs"]):
                rest[col] = val
            rest["rank"] = TOP_PAIRS + 1
        block = pd.concat([shown, rest], ignore_index=True)
        assert np.isclose(block["value"].sum(), sub["value"].sum(), rtol=1e-10), \
            f"{indicator}: ranked pairs lost mass"
        frames.append(block)

    pairs = pd.concat(frames, ignore_index=True)
    pairs["share_pct"] = 100 * pairs["value"] / pairs.groupby("indicator")[
        "value"].transform("sum")
    # Share of the indicator that the MRIO supply chain represents, so a reader
    # can see what the panel does not cover.
    total_all = hotspot.groupby("indicator")["value"].sum()
    pairs["mrio_coverage_pct"] = (
        100 * pairs["indicator"].map(mrio.groupby("indicator")["value"].sum())
        / pairs["indicator"].map(total_all))
    pairs.sort_values(["indicator", "rank"]).to_csv(
        os.path.join(OUT, "figure2b_top_origin_industry_pairs.csv"), index=False)

    print(f"manuscript figure tables -> {OUT}")
    for name, frame, col in (("figure1", fig1, "contribution_group"),
                             ("figure2", fig2, "hotspot_group"),
                             ("figure3", fig3, "producing_world_region")):
        print(f"  {name}: {frame[col].nunique()} groups x "
              f"{frame['indicator'].nunique()} indicators")
    print(f"  figure2b: {TOP_PAIRS} pairs + remainder x "
          f"{pairs['indicator'].nunique()} indicators")


if __name__ == "__main__":
    main()
