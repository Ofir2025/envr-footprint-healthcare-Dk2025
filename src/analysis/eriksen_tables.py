# -*- coding: utf-8 -*-
"""Standardise the Eriksen/Steenmeijer replication outputs as FAIR CSV tables.

The replication inherits its output routine from the Dutch code, which writes
multi-sheet Excel workbooks with the original column names (``ISO3``,
``SecTxtCode``, ``SAggDescription`` …). Those workbooks do carry full node
detail, but they are not machine-readable in the FAIR sense: a reader cannot
join them to the study's other tables, the indicator sits in the column name
rather than in a column, and a spreadsheet is not a good archival format.

This module rewrites them as long-format CSVs on the study's standard schema,
detailed and aggregated, without recomputing anything - the numbers are the
replication's own. Every conversion is checked: the standardised table must
reproduce the workbook's column totals exactly, and the assertion fails loudly
if it does not.

The three analyses
------------------
**Contribution** - ``B L diag(y)``. Where impacts occur, attributed along the
chain driven by each element of health-care demand. This is Steenmeijer's
figure 1.

**Hotspot** - ``B diag(L y)``. Where impacts occur, without attributing them
back to a purchase. This is their figures 2 and 3.

**Intensities** - impact per unit of output, by node; the multipliers behind
both.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.eriksen_tables``
"""

from __future__ import annotations

import os
from typing import Any

import numpy as np
import pandas as pd

from analysis.constants import ANALYSIS_YEAR, MODEL_LABEL, eriksen_folder
from analysis.detail_tables import domestic_import_split, node_labels
from paths import OUTPUT_DIR

FOLDER = eriksen_folder()

#: Legacy workbook column -> study schema column.
#: Workbook column -> schema column, given the node-index prefix.
def rename_map(prefix: str) -> dict[str, str]:
    """Map the legacy workbook columns onto the schema for one node index.

    Parameters
    ----------
    prefix : {"producing", "purchased"}
        Which node index the analysis is on. ``B diag(L y)`` is indexed by the
        node where the pressure physically occurs (``producing``);
        ``B L diag(y)`` is indexed by the product bought (``purchased``).
        Labelling one as the other inverts the domestic/imported split, so the
        prefix is carried explicitly rather than assumed.

    Returns
    -------
    dict of str to str
        Rename mapping for :meth:`pandas.DataFrame.rename`.
    """
    return {
        "ISO3": f"{prefix}_country_iso3",
        "RegName": f"{prefix}_country_name",
        "Region": f"{prefix}_world_region",
        "SecTxtCode": f"{prefix}_sector_code",
        "SecName": f"{prefix}_sector_name",
        "SAggDescription": f"{prefix}_sector_group",
        "Scope": "ghg_protocol_scope",
    }

#: Indicator column in the workbook -> (indicator name, unit).
INDICATORS: dict[str, tuple[str, str]] = {
    "Global warming (ktCO2eq)": ("climate_change", "kt CO2eq"),
    "Material extraction (kt)": ("material_extraction", "kt"),
    "Blue water consumption (Mm3)": ("blue_water_consumption", "Mm3"),
    "Land use (km2)": ("land_use", "km2"),
    "Waste generation (kt)": ("waste_generation", "kt"),
}

#: The intensities workbook expresses the same five indicators per million
#: euro of output, so it carries its own column names.
INTENSITY_INDICATORS: dict[str, tuple[str, str]] = {
    "Global warming (ktCO2eq)/MEUR": ("climate_change", "kt CO2eq per MEUR"),
    "Material extraction (kt)/MEUR": ("material_extraction", "kt per MEUR"),
    "Blue water consumption (Mm3)/MEUR": ("blue_water_consumption",
                                          "Mm3 per MEUR"),
    "Land use (km2)/MEUR": ("land_use", "km2 per MEUR"),
    "Waste generation (kt)/MEUR": ("waste_generation", "kt per MEUR"),
}

#: Rows that are not EXIOBASE nodes but bottom-up additions carried alongside
#: them. They are legitimate members of the detail table - they are where those
#: impacts arise - but they are not MRIO supply-chain nodes, and a reader
#: aggregating by sector must be able to tell the difference.
BOTTOM_UP_PSEUDO_NODES = frozenset({
    "Direct impact from healthcare services",
    "Emission from anesthetic gases",
    "Emission from pMDI propellants",
    "Employee commute",
    "Patient and visitor travel",
    "Not distributed travel impact",
})

#: Workbook stem -> (output stem, what the analysis answers).
ANALYSES: dict[str, tuple[str, str, str, str]] = {
    "contribution_analysis": (
        "contribution", "purchased", "product",
        "B L diag(y): impacts attributed along the chain driven by each "
        "element of health-care final demand, indexed by the PURCHASED "
        "product (Steenmeijer figure 1)"),
    "hotspot_analysis": (
        "hotspot", "producing", "node",
        "B diag(L y): where impacts physically occur, indexed by the "
        "PRODUCING node, not attributed back to a purchase "
        "(Steenmeijer figures 2 and 3)"),
    "intensities": (
        "intensity", "purchased", "product",
        "impact per unit of node output, indexed by the node whose output is "
        "bought; the multipliers behind both analyses"),
}


def standardise(stem: str, prefix: str, description: str) -> pd.DataFrame:
    """Convert one legacy workbook sheet to the study's long-format schema.

    Parameters
    ----------
    stem : str
        Workbook stem, for example ``"contribution_analysis"``.
    prefix : {"producing", "purchased"}
        Node index the analysis is on; see :func:`rename_map`.
    description : str
        What the analysis computes, carried into every row so the file is
        self-describing.

    Returns
    -------
    pandas.DataFrame
        Long-format table, one row per (node, indicator).

    Raises
    ------
    AssertionError
        If the reshaped table does not reproduce the workbook's column totals.
    """
    path = os.path.join(str(OUTPUT_DIR), FOLDER, f"{stem}.xlsx")
    wide = pd.read_excel(path, sheet_name="full")
    wide = wide.drop(columns=[c for c in wide.columns
                              if str(c).startswith("Unnamed")])
    mapping = INTENSITY_INDICATORS if any(
        c in wide.columns for c in INTENSITY_INDICATORS) else INDICATORS
    present = [c for c in mapping if c in wide.columns]
    long = wide.melt(id_vars=[c for c in wide.columns if c not in present],
                     value_vars=present, var_name="_indicator_col",
                     value_name="value")
    long = long.rename(columns=rename_map(prefix))

    # The legacy workbook carries EXIOBASE codes with their A_ / C_ construct
    # prefix and the Dutch original's world-region aggregation. Normalise both
    # onto the study's star-schema convention, taking the mapping from the one
    # source of truth rather than restating it here.
    regions, _ = node_labels()
    long[f"{prefix}_sector_code"] = (
        long[f"{prefix}_sector_code"].astype(str)
        .str.replace(r"^[AC]_", "", regex=True))
    # Country coding: ISO3 where one exists, the region name where none does.
    # The workbook carries EXIOBASE's bare RoW codes and the deprecated ROM.
    iso = long[f"{prefix}_country_iso3"].astype(str).replace({"ROM": "ROU"})
    row_mask = iso.isin(["WA", "WL", "WE", "WF", "WM"])
    long[f"{prefix}_country_iso3"] = iso.where(
        ~row_mask, long[f"{prefix}_country_name"])

    region_of = dict(zip(regions["iso3"], regions["world_region"]))
    long[f"{prefix}_world_region"] = (
        long[f"{prefix}_country_iso3"].map(region_of)
        .fillna(long[f"{prefix}_world_region"]))
    long["indicator"] = long["_indicator_col"].map(lambda c: mapping[c][0])
    long["unit"] = long["_indicator_col"].map(lambda c: mapping[c][1])
    long = long.drop(columns="_indicator_col")

    for column in present:
        want = float(np.nansum(wide[column].to_numpy(dtype=float)))
        got = float(long.loc[long.indicator == mapping[column][0],
                             "value"].sum())
        assert np.isclose(want, got, rtol=1e-12, atol=1e-9), (
            f"{stem}: reshaping changed the total for {column} "
            f"({want!r} -> {got!r})")

    long["component_type"] = np.where(
        long[f"{prefix}_sector_name"].isin(BOTTOM_UP_PSEUDO_NODES),
        "bottom-up item", "MRIO supply-chain node")
    long.insert(0, "analysis", description)
    long.insert(0, "sector_consuming", "health_and_eldercare")
    long.insert(0, "country_consuming", "DNK")
    long["analysis_year"] = ANALYSIS_YEAR
    long["model"] = MODEL_LABEL
    return long[long["value"].notna() & (long["value"] != 0)]


def main() -> None:
    """Write every replication analysis as a detailed and an aggregate CSV."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    for stem, (out_stem, prefix, noun, description) in ANALYSES.items():
        source = os.path.join(out_dir, f"{stem}.xlsx")
        if not os.path.exists(source):
            print(f"  skip {stem}: workbook not found - run analysis.main_2025")
            continue
        detail = standardise(stem, prefix, description)
        detail.to_csv(
            os.path.join(out_dir, f"{out_stem}_by_{prefix}_{noun}.csv"),
            index=False)
        detail.groupby(
            ["indicator", "unit", f"{prefix}_sector_group"],
            dropna=False)["value"].sum().reset_index().sort_values(
            "value", ascending=False).to_csv(
            os.path.join(out_dir, f"{out_stem}_by_sector_group.csv"),
            index=False)
        detail.groupby(
            ["indicator", "unit", f"{prefix}_world_region"],
            dropna=False)["value"].sum().reset_index().sort_values(
            "value", ascending=False).to_csv(
            os.path.join(out_dir, f"{out_stem}_by_world_region.csv"),
            index=False)
        if out_stem != "intensity":
            domestic_import_split(
                detail,
                country_column=f"{prefix}_country_iso3").to_csv(
                os.path.join(out_dir,
                             f"{out_stem}_domestic_vs_imported.csv"),
                index=False)
        print(f"  {out_stem:12} {len(detail):>7,} rows  "
              f"({detail[f'{prefix}_country_iso3'].nunique()} regions x "
              f"{detail[f'{prefix}_sector_name'].nunique()} sectors x "
              f"{detail.indicator.nunique()} indicators)")

    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
