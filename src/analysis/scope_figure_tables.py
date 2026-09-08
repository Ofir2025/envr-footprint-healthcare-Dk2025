# -*- coding: utf-8 -*-
"""Figure-ready scope 1-3 tables, resolved by origin and by industry.

The scope decomposition in :mod:`analysis.scopes_detail` is complete but is not
shaped for plotting: scope 1 and the bottom-up items carry no MRIO node, the
producing-node file is 24 000 rows, and nothing aggregates it. This module
emits the tables a figure script consumes directly, at three resolutions:

    detail       scope x producing country x producing industry
    top-N        the N largest (country, industry) pairs, remainder pooled
    grouped      scope x industry group, and scope x continent, and the cross

Every table is a star-schema fact: dimension columns first, then ``value`` and
``unit``. EXIOBASE industry codes carry no ``A_`` / ``C_`` prefix and countries
are ISO3, with EXIOBASE's five rest-of-world regions carried by name, per
:func:`analysis.detail_tables.node_labels`.

Placing scope 1 and the bottom-up items
---------------------------------------
Scope 2 and the MRIO part of scope 3 are resolved to producing nodes by the
Leontief solution and are read as they stand. The remaining components have no
producing node in the model and are placed explicitly rather than dropped:

===========================  ========  ==========================================
Component                    Origin    Industry label
===========================  ========  ==========================================
Scope 1 (DRIVHUS)            DNK       Health and social work
Anaesthetic gases            DNK       Health and social work
pMDI propellants             DNK       Health and social work
Employee commuting           DNK       Bottom-up: employee commuting
Patient and visitor travel   DNK       Bottom-up: patient and visitor travel
===========================  ========  ==========================================

All five are Danish by construction: they are emissions of Danish providers,
Danish staff or Danish patients. Labelling them as such is what lets a reader
add the bars and recover the headline, and it is why the domestic share of the
total (26.3 % on the MRIO alone) rises once they are included.

Which scope 2 convention
------------------------
The manuscript reports the Hertwich & Wood convention; this folder's partition
uses the GHG Protocol strict figure so that scope 1 + 2 + 3 is internally
protocol-conforming. These tables follow the folder, and the alternative is
carried in ``scope_convention`` so a figure can be rebuilt on either.

Run::

    HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship \\
        PYTHONPATH=src python -m analysis.scope_figure_tables
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from analysis.constants import scopes_folder
from paths import OUTPUT_DIR

FOLDER = scopes_folder()

#: Components with no producing node, placed at their true Danish origin.
#: Each carries its OWN industry code: two different activities sharing one code
#: would collapse to one row on any join, and the star-schema build rejects it.
#: (scope, summary label, industry code, industry label, industry group)
#: ``scopes_detail`` writes each of these as a component row of
#: ``scopes_summary_detailed.csv``, for every indicator rather than for climate
#: alone, so the placement below is the same in all five categories.
#: (scope, component row in the summary, industry code, label, group)
BOTTOM_UP: tuple[tuple[str, str, str, str, str], ...] = (
    ("Scope 1", "Scope 1 component: direct operations",
     "HEAL", "Health and social work", "Operational impact"),
    ("Scope 1", "Scope 1 component: anaesthetic gases",
     "HEAL", "Health and social work", "Operational impact"),
    ("Scope 3", "Scope 3 component: pMDI propellant",
     "HEAL", "Health and social work", "Operational impact"),
    ("Scope 3", "Scope 3 component: employee commuting",
     "BU_COMMUTE", "Bottom-up: employee commuting", "Private travel"),
    ("Outside protocol",
     "Outside protocol component: patient and visitor travel",
     "BU_TRAVEL", "Bottom-up: patient and visitor travel", "Private travel"),
)

TOP_N = 25


def _read(name: str) -> pd.DataFrame:
    """Read one gold file from this folder.

    Parameters
    ----------
    name : str
        File name within this year's ``02_scopes_wood_hertwich`` folder.

    Returns
    -------
    pandas.DataFrame
        The file, unmodified.
    """
    return pd.read_csv(os.path.join(str(OUTPUT_DIR), *FOLDER.split("/"), name))


def build_detail() -> pd.DataFrame:
    """Assemble the full scope x origin x industry fact table.

    Returns
    -------
    pandas.DataFrame
        Columns ``scope``, ``producing_country_iso3``, ``producing_country_name``,
        ``producing_world_region``, ``producing_sector_code``,
        ``producing_sector_name``, ``producing_sector_group``, ``indicator``,
        ``unit``, ``value``, plus the study identifiers.

    Raises
    ------
    AssertionError
        If the assembled table does not reproduce the scope totals it was
        built from.
    """
    nodes = _read("scopes_by_producing_node.csv").copy()
    summary = _read("scopes_summary_detailed.csv")

    # One placement rule for all five categories. `scopes_detail` writes each
    # bottom-up term as its own component row of the summary, so a category
    # where the term happens to be zero simply contributes no row; nothing is
    # special-cased on climate any more. This is what closed the 0.2-0.6 % gap
    # between the non-climate scope tables and the study totals: the ecoinvent
    # travel inventory behind commuting and patient travel carries material,
    # water and land as well as greenhouse gases.
    idx = summary.set_index(["indicator", "scope"])
    rows = []
    for scope, component, code, industry, group in BOTTOM_UP:
        for indicator in sorted(summary["indicator"].unique()):
            if (indicator, component) not in idx.index:
                raise AssertionError(
                    f"component missing from scopes_summary_detailed: "
                    f"{indicator} / {component!r}")
            r = idx.loc[(indicator, component)]
            if float(r["value"]) == 0.0:
                continue
            rows.append({
                "consuming_country_iso3": "DNK",
                "model": nodes["model"].iloc[0],
                "analysis_year": int(nodes["analysis_year"].iloc[0]),
                "indicator": indicator,
                "unit": r["unit"],
                "scope": scope,
                "producing_country_iso3": "DNK",
                "producing_country_name": "Denmark",
                "producing_world_region": "Denmark",
                "producing_sector_code": code,
                "producing_sector_name": industry,
                "producing_sector_group": group,
                "component_type": "bottom-up item",
                "value": float(r["value"]),
            })

    nodes["component_type"] = "MRIO supply-chain node"
    detail = pd.concat([nodes, pd.DataFrame(rows)], ignore_index=True)
    detail = detail[detail["value"] != 0].reset_index(drop=True)

    # Every indicator must now reproduce ALL FOUR of its scope totals from the
    # summary - scope 1 and outside protocol included, since the bottom-up rows
    # above are written for every category.
    got = detail.groupby(["indicator", "scope"])["value"].sum()
    for indicator in sorted(detail["indicator"].unique()):
        sub = summary[summary["indicator"] == indicator]
        for scope in ("Scope 1", "Scope 2", "Scope 3", "Outside protocol"):
            rows_ = sub.loc[sub.scope == scope, "value"]
            if rows_.empty or float(rows_.iloc[0]) == 0.0:
                continue
            assert (indicator, scope) in got.index, \
                f"{indicator} {scope}: summary is non-zero but no rows assembled"
            target = float(rows_.iloc[0])
            assert np.isclose(got[(indicator, scope)], target, rtol=1e-8), (
                f"{indicator} {scope}: assembled {got[(indicator, scope)]:,.4f} "
                f"vs summary {target:,.4f}")
    return detail


def top_n_with_remainder(detail: pd.DataFrame, n: int = TOP_N) -> pd.DataFrame:
    """Collapse the detail to the ``n`` largest origin-industry pairs.

    The remainder is pooled into one explicitly labelled row per scope rather
    than dropped, so the bars still sum to the scope total and a reader can see
    how much the visible pairs actually account for.

    Parameters
    ----------
    detail : pandas.DataFrame
        Output of :func:`build_detail`.
    n : int, optional
        Number of pairs to keep, ranked on absolute value across all scopes.

    Returns
    -------
    pandas.DataFrame
        One row per (scope, pair), plus one remainder row per scope, with
        ``rank`` and ``is_remainder``.
    """
    keys = ["producing_country_iso3", "producing_country_name",
            "producing_world_region", "producing_sector_code",
            "producing_sector_name", "producing_sector_group"]
    # Rank within the headline indicator so the same pairs are shown in every
    # panel; ranking each panel separately would make the facets incomparable.
    rank_basis = detail[detail["indicator"] == "climate_change"]
    pair_total = (rank_basis.groupby(keys, dropna=False)["value"].sum()
                  .sort_values(ascending=False))
    keep = pair_total.head(n).index
    flagged = detail.set_index(keys)
    flagged["is_remainder"] = ~flagged.index.isin(keep)
    flagged = flagged.reset_index()

    shown = (flagged[~flagged.is_remainder]
             .groupby(keys + ["scope", "indicator", "unit"], dropna=False)["value"]
             .sum().reset_index())
    rank = {k: i + 1 for i, k in enumerate(keep)}
    shown["rank"] = [rank[tuple(r)] for r in shown[keys].to_numpy().tolist()]
    shown["is_remainder"] = False

    rest = (flagged[flagged.is_remainder]
            .groupby(["scope", "indicator", "unit"], dropna=False)["value"]
            .sum().reset_index())
    rest["producing_country_iso3"] = "OTH"
    rest["producing_country_name"] = f"All other origins (beyond top {n})"
    rest["producing_world_region"] = "Other"
    rest["producing_sector_code"] = "OTHER"
    rest["producing_sector_name"] = f"All other origin-industry pairs (beyond top {n})"
    rest["producing_sector_group"] = "Other"
    rest["rank"] = n + 1
    rest["is_remainder"] = True

    out = pd.concat([shown, rest], ignore_index=True).sort_values(
        ["scope", "rank"]).reset_index(drop=True)
    assert np.isclose(out["value"].sum(), detail["value"].sum(), rtol=1e-12), \
        "top-N collapse lost mass"
    return out


def main() -> None:
    """Write the detail, top-N and grouped scope tables."""
    out_dir = os.path.join(str(OUTPUT_DIR), *FOLDER.split("/"))
    os.makedirs(out_dir, exist_ok=True)
    detail = build_detail()
    detail.to_csv(os.path.join(out_dir, "scope_by_origin_and_industry.csv"),
                  index=False)

    top_n_with_remainder(detail).to_csv(
        os.path.join(out_dir, "scope_by_origin_industry_top25.csv"), index=False)

    for by, stem in (
            (["producing_sector_group"], "scope_by_industry_group"),
            (["producing_world_region"], "scope_by_continent"),
            (["producing_world_region", "producing_sector_group"],
             "scope_by_continent_and_industry_group"),
            (["producing_country_iso3", "producing_country_name",
              "producing_world_region"], "scope_by_country")):
        agg = (detail.groupby(by + ["scope", "indicator", "unit"], dropna=False)
               ["value"].sum().reset_index())
        agg["share_of_scope_pct"] = 100 * agg["value"] / agg.groupby(
            ["indicator", "scope"])["value"].transform("sum")
        agg = agg.sort_values(["indicator", "scope", "value"],
                              ascending=[True, True, False])
        agg.to_csv(os.path.join(out_dir, f"{stem}.csv"), index=False)
        assert np.isclose(agg["value"].sum(), detail["value"].sum(), rtol=1e-12), \
            f"{stem} lost mass"

    print(f"scope figure tables -> {out_dir}")
    print(f"  detail rows {len(detail):,}")
    # Never sum across indicators: the units differ.
    wide = (detail.pivot_table(index="indicator", columns="scope",
                               values="value", aggfunc="sum")
            .round(2).fillna(0.0))
    unit = detail.groupby("indicator")["unit"].first()
    wide.insert(0, "unit", unit)
    print(wide.to_string())


if __name__ == "__main__":
    main()
