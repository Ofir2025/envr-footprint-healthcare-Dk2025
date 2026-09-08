# -*- coding: utf-8 -*-
"""Shared builders for detailed, lineage-preserving result tables.

Every substantive result in this study is produced at the finest resolution the
model supports and written **twice**: once at full node detail and once
aggregated. The detailed file is the record; the aggregate is a convenience.
Storing only the aggregate destroys the ability to ask where an impact
originates, which is the question an environmentally extended MRIO exists to
answer.

The node dimension
------------------
A *node* is one (region, industry) pair — 49 x 163 = 7,987 of them. For a
consumption-based footprint the two dimensions that matter are:

*Producing node* — where the impact physically occurs. For Danish health care
this separates impacts embodied in **imports** (producing country is not
Denmark) from those arising **domestically** (producing country is Denmark),
and within each, which industry is responsible.

*Purchased product* — what the health sector actually bought, which is a
different question from where the impact arose, and is what a procurement
decision can act on.

Both are emitted where the underlying calculation supports them.

Conventions
-----------
Countries carry ISO3 codes. EXIOBASE's five rest-of-world aggregates keep their
own labels (``WA``, ``WE``, ``WF``, ``WL``, ``WM``) because they are not
countries and an ISO3 code would misrepresent them. Zero-valued rows are
dropped, since a node with no impact carries no information and 7,987 rows per
indicator per stratum is otherwise mostly zeros.
"""

from __future__ import annotations

import os
from typing import Any, Iterable

import numpy as np
import pandas as pd

from paths import BRONZE_DIR

CLASSIFICATIONS = BRONZE_DIR / "exiobase_v3_7" / "classifications.xlsx"

_CACHE: dict[str, Any] = {}


def node_labels() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the EXIOBASE region and industry classifications.

    Returns
    -------
    regions : pandas.DataFrame
        Columns ``pos``, ``iso3``, ``country_name``, ``world_region``,
        ``is_row_region``, ordered by model position.
    sectors : pandas.DataFrame
        Columns ``pos``, ``sector_code``, ``sector_name``, ``sector_group``,
        ordered by model position.

    Notes
    -----
    Cached after first call; the workbook is read once per process.
    """
    if "labels" not in _CACHE:
        cls = pd.read_excel(CLASSIFICATIONS, sheet_name="disagg_reg", skiprows=5)
        regions = pd.DataFrame({
            "pos": cls["Position"],
            "iso3": cls["Code1"].astype(str),
            "country_name": cls["Description"].astype(str),
            "world_region": cls["AggDescription"].astype(str),
            "is_row_region": cls["Code2"].astype(int).eq(-1),
        }).sort_values("pos").reset_index(drop=True)
        ind = pd.read_excel(CLASSIFICATIONS, sheet_name="disagg_ind", skiprows=5)
        ind = ind[ind["Code"].astype(str).str.startswith("A_")]
        sectors = pd.DataFrame({
            "pos": range(len(ind)),
            # Star-schema convention: EXIOBASE industry and product codes are
            # carried WITHOUT the A_ / C_ activity/commodity prefix, which
            # encodes the table construct rather than the industry itself and
            # would not join to a shared dim_industry across ixi and pxp runs.
            "sector_code": ind["Code"].astype(str)
                              .str.replace(r"^[AC]_", "", regex=True).values,
            "sector_name": ind["Description"].astype(str).values,
            "sector_group": ind["AggDescription"].astype(str).values,
        })
        # Country coding, per the study's star-schema convention: ISO3 where an
        # ISO3 code exists, and the REGION NAME where one does not. EXIOBASE's
        # five rest-of-world regions have no ISO3 code, so their bare model
        # codes (WA/WL/WE/WF/WM) are replaced by the names already carried in
        # ``country_name``. ROM is the deprecated alpha-3 for Romania; the
        # current code is ROU, and one file in the tree already used ROU, so
        # the two spellings coexisted until this was applied centrally.
        regions["iso3"] = regions["iso3"].replace({"ROM": "ROU"})
        regions.loc[regions["is_row_region"], "iso3"] = \
            regions.loc[regions["is_row_region"], "country_name"]

        # The world-region aggregation is inherited from the Dutch original,
        # which singled out the Netherlands as its home region. In a Danish
        # study that leaves NL as a spurious top-level "world region" while
        # Denmark is the actual home. Fold NL back into Europe; Denmark is
        # given its own label so the domestic/imported split stays legible.
        regions["world_region"] = np.where(
            regions["iso3"].eq("DNK"), "Denmark",
            regions["world_region"].replace({"Netherlands": "Europe"}))
        _CACHE["labels"] = (regions, sectors)
    return _CACHE["labels"]


def node_frame(prefix: str = "producing") -> pd.DataFrame:
    """Build the 7,987-row node label frame.

    Parameters
    ----------
    prefix : str, optional
        Column-name prefix, normally ``"producing"`` or ``"purchased"``.

    Returns
    -------
    pandas.DataFrame
        One row per node, in model order, with ``<prefix>_country_iso3``,
        ``<prefix>_country_name``, ``<prefix>_world_region``,
        ``<prefix>_sector_code``, ``<prefix>_sector_name`` and
        ``<prefix>_sector_group``.
    """
    regions, sectors = node_labels()
    n_sectors = len(sectors)
    return pd.DataFrame({
        f"{prefix}_country_iso3": np.repeat(regions["iso3"].values, n_sectors),
        f"{prefix}_country_name": np.repeat(regions["country_name"].values,
                                            n_sectors),
        f"{prefix}_world_region": np.repeat(regions["world_region"].values,
                                            n_sectors),
        f"{prefix}_sector_code": np.tile(sectors["sector_code"].values,
                                         len(regions)),
        f"{prefix}_sector_name": np.tile(sectors["sector_name"].values,
                                         len(regions)),
        f"{prefix}_sector_group": np.tile(sectors["sector_group"].values,
                                          len(regions)),
    })


def detail_rows(values: np.ndarray, *, prefix: str = "producing",
                drop_zero: bool = True, **columns: Any) -> pd.DataFrame:
    """Attach node labels to a 7,987-length value vector.

    Parameters
    ----------
    values : numpy.ndarray
        One value per node, in model order.
    prefix : str, optional
        Node-dimension prefix passed to :func:`node_frame`.
    drop_zero : bool, optional
        Drop rows whose value is exactly zero. Default ``True``.
    **columns
        Scalar columns to attach to every row, for example
        ``indicator="climate_change"``, ``unit="kt CO2eq"``, ``scope="Scope 3"``.
        They are placed before the node columns so the file reads
        left-to-right from context to detail.

    Returns
    -------
    pandas.DataFrame
        The labelled detail table, sorted by descending value.

    Raises
    ------
    ValueError
        If ``values`` does not have one entry per node.
    """
    frame = node_frame(prefix)
    values = np.asarray(values).ravel()
    if values.size != len(frame):
        raise ValueError(f"expected {len(frame)} node values, got {values.size}")
    out = frame.copy()
    out["value"] = values
    for name, value in reversed(list(columns.items())):
        out.insert(0, name, value)
    if drop_zero:
        out = out[out["value"] != 0]
    return out.sort_values("value", ascending=False).reset_index(drop=True)


def write_pair(detail: pd.DataFrame, out_dir: str, stem: str,
               group_by: Iterable[str], value_col: str = "value") -> tuple[str, str]:
    """Write a detailed table and its aggregate as two files.

    Parameters
    ----------
    detail : pandas.DataFrame
        The full-detail table, as returned by :func:`detail_rows`.
    out_dir : str
        Destination directory.
    stem : str
        File stem; the outputs are ``<stem>_by_producing_node.csv`` and
        ``<stem>_summary.csv``.
    group_by : iterable of str
        Columns to group the aggregate by.
    value_col : str, optional
        Name of the numeric column.

    Returns
    -------
    tuple of str
        Paths of the detailed and aggregate files.
    """
    os.makedirs(out_dir, exist_ok=True)
    detail_path = os.path.join(out_dir, f"{stem}_by_producing_node.csv")
    summary_path = os.path.join(out_dir, f"{stem}_summary.csv")
    detail.to_csv(detail_path, index=False)
    keys = [c for c in group_by if c in detail.columns]
    detail.groupby(keys, dropna=False)[value_col].sum().reset_index() \
        .sort_values(value_col, ascending=False) \
        .to_csv(summary_path, index=False)
    return detail_path, summary_path


def domestic_import_split(detail: pd.DataFrame, home: str = "DNK",
                          by: Iterable[str] = ("indicator", "unit"),
                          country_column: str = "producing_country_iso3",
                          ) -> pd.DataFrame:
    """Split a detailed table into domestic and imported origin.

    Parameters
    ----------
    detail : pandas.DataFrame
        A table carrying ``country_column`` and ``value``.
    home : str, optional
        ISO3 code of the consuming country. Default ``"DNK"``.
    by : iterable of str, optional
        Additional grouping columns.
    country_column : str, optional
        Node-country column to split on. Use ``"purchased_country_iso3"`` for a
        table indexed by the purchased product rather than the producing node;
        the two answer different questions and must not be conflated.

    Returns
    -------
    pandas.DataFrame
        One row per group per origin, with ``origin`` in
        ``{"domestic", "imported"}``, the value, and its share of the group.
    """
    frame = detail.copy()
    frame["origin"] = np.where(
        frame[country_column] == home, "domestic", "imported")
    keys = [c for c in by if c in frame.columns] + ["origin"]
    out = frame.groupby(keys, dropna=False)["value"].sum().reset_index()
    totals = out.groupby([k for k in keys if k != "origin"],
                         dropna=False)["value"].transform("sum")
    out["share_of_total_pct"] = 100.0 * out["value"] / totals
    return out
