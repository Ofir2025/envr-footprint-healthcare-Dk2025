# -*- coding: utf-8 -*-
"""Canonical star schema for the Danish health-care footprint results.

The layer-by-layer gold tables are denormalised on purpose: each is readable on
its own and plots without a join. That convenience is also their weakness. The
same dimension attribute is repeated on millions of rows, which is what allowed
``producing_world_region`` to disagree between folders, and there is no key a
database or a BI tool can join on.

This module derives the canonical model from those tables: conformed dimensions
with a surrogate ``*_id`` primary key and a stable natural key, and fact tables
that carry **ids only** plus measures. It does not replace the denormalised
layer; it sits beside it in ``data/gold/star/`` as the model of record.

Grain of each fact, stated because a fact table with an unstated grain cannot be
audited:

===============================  ==========================================
Fact                             One row per
===============================  ==========================================
``fact_footprint_node``          model x indicator x demand component x
                                 producing region x producing industry
``fact_footprint_product``       model x indicator x demand component x
                                 purchased region x purchased industry
``fact_scope_node``              model x indicator x scope x producing
                                 region x producing industry
``fact_national_total``          model x indicator (national and health-care
                                 totals side by side, with the share)
``fact_health_function``         model x indicator x health function
===============================  ==========================================

Referential integrity is asserted before anything is written: every foreign key
in every fact must resolve to exactly one dimension row, and every fact must
reproduce the total of the denormalised table it was derived from. A star model
that silently drops rows on a join is worse than no star model.

Run::

    HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship \\
        PYTHONPATH=src python -m analysis.build_star_schema
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from paths import OUTPUT_DIR

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.constants import (ANALYSIS_YEAR, BACKGROUND_YEAR, MODEL_LABEL,
                                scopes_folder)
from analysis.detail_tables import node_labels

STAR_DIR = os.path.join(str(OUTPUT_DIR), "star")


# --------------------------------------------------------------- dimensions
def build_dim_region() -> pd.DataFrame:
    """Conformed region dimension.

    Returns
    -------
    pandas.DataFrame
        ``region_id`` (surrogate PK), ``region_code`` (natural key: ISO3, or the
        region name where no ISO3 exists), ``region_name``, ``world_region``,
        ``is_row_region``, ``is_domestic``.
    """
    regions, _ = node_labels()
    dim = pd.DataFrame({
        "region_id": range(1, len(regions) + 1),
        "region_code": regions["iso3"].values,
        "region_name": regions["country_name"].values,
        "world_region": regions["world_region"].values,
        "is_row_region": regions["is_row_region"].values,
    })
    dim["is_domestic"] = dim["region_code"].eq("DNK")
    return dim


def build_dim_industry() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Conformed industry dimension and its industry-group parent.

    Returns
    -------
    tuple of pandas.DataFrame
        ``(dim_industry, dim_industry_group)``. ``dim_industry`` carries
        ``industry_id`` (PK), ``industry_code`` (EXIOBASE code without the
        ``A_`` / ``C_`` prefix), ``industry_name`` and ``industry_group_id``
        (FK).
    """
    _, sectors = node_labels()
    groups = (sectors[["sector_group"]].drop_duplicates()
              .sort_values("sector_group").reset_index(drop=True))
    groups["industry_group_id"] = range(1, len(groups) + 1)
    groups = groups.rename(columns={"sector_group": "industry_group_name"})

    dim = pd.DataFrame({
        "industry_id": range(1, len(sectors) + 1),
        "industry_code": sectors["sector_code"].values,
        "industry_name": sectors["sector_name"].values,
        "industry_group_name": sectors["sector_group"].values,
    }).merge(groups, on="industry_group_name", how="left")
    dim["industry_type"] = "MRIO industry"

    # Bottom-up items are part of the footprint but have no MRIO node. They are
    # first-class members of the industry dimension, flagged so a query can
    # include or exclude them deliberately rather than by accident.
    extra = pd.DataFrame([
        {"industry_code": "BU_COMMUTE",
         "industry_name": "Bottom-up: employee commuting",
         "industry_group_name": "Private travel"},
        {"industry_code": "BU_TRAVEL",
         "industry_name": "Bottom-up: patient and visitor travel",
         "industry_group_name": "Private travel"},
    ]).merge(groups, on="industry_group_name", how="left")
    extra["industry_id"] = range(len(dim) + 1, len(dim) + 1 + len(extra))
    extra["industry_type"] = "bottom-up item"

    dim = pd.concat([dim, extra], ignore_index=True)

    # Secondary aggregations, joined from the editable concordance rather than
    # hard-coded: ISIC Rev.3 division (EXIOBASE developers' own
    # "ISIC REV. 3 - EXIOBASE2.0" table) and, for manufacturing divisions
    # 15-37 only, the technology-intensity group. Five industries have no ISIC
    # row because the hybrid release renumbers them (i24.x, i26.w.1, i40.2,
    # i90.x); they are left blank rather than guessed.
    isic_path = os.path.join(REPO, "data", "bronze", "concordances",
                             "exiobase_industry_to_isic_rev3.csv")
    if os.path.exists(isic_path):
        isic = pd.read_csv(isic_path, dtype={"isic_rev3_division": str})
        dim = dim.merge(
            isic[["exiobase_industry_code", "isic_rev3_division",
                  "isic_rev3_description", "technology_group"]],
            left_on="industry_code", right_on="exiobase_industry_code",
            how="left").drop(columns=["exiobase_industry_code"])
    else:
        for col in ("isic_rev3_division", "isic_rev3_description",
                    "technology_group"):
            dim[col] = pd.NA

    dim = dim[["industry_id", "industry_code", "industry_name",
               "industry_group_id", "industry_type", "isic_rev3_division",
               "isic_rev3_description", "technology_group"]]
    return dim, groups[["industry_group_id", "industry_group_name"]]


def build_dim_indicator(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Conformed indicator dimension, unioned over every source table.

    Parameters
    ----------
    frames : dict of str to pandas.DataFrame
        Source tables that carry ``indicator`` and ``unit``.

    Returns
    -------
    pandas.DataFrame
        ``indicator_id`` (PK), ``indicator_code`` (natural key), ``unit``.
    """
    seen = []
    for frame in frames.values():
        if {"indicator", "unit"} <= set(frame.columns):
            seen.append(frame[["indicator", "unit"]].drop_duplicates())
    dim = (pd.concat(seen, ignore_index=True).drop_duplicates("indicator")
           .sort_values("indicator").reset_index(drop=True))
    dim.insert(0, "indicator_id", range(1, len(dim) + 1))
    return dim.rename(columns={"indicator": "indicator_code"})


def _simple_dim(values, id_col: str, name_col: str) -> pd.DataFrame:
    """Build a one-attribute dimension from a set of labels.

    Parameters
    ----------
    values : iterable of str
        Distinct labels.
    id_col, name_col : str
        Column names for the surrogate key and the label.

    Returns
    -------
    pandas.DataFrame
        Two columns, sorted by label, ids from 1.
    """
    vals = sorted({str(v) for v in values if pd.notna(v)})
    return pd.DataFrame({id_col: range(1, len(vals) + 1), name_col: vals})


def build_dim_model() -> pd.DataFrame:
    """Model / scenario dimension: one row per background and boundary.

    Returns
    -------
    pandas.DataFrame
        ``model_id`` (PK) and the attributes that make a result reproducible.
    """
    return pd.DataFrame([{
        "model_id": 1,
        "model_label": MODEL_LABEL,
        "background_year": BACKGROUND_YEAR,
        "analysis_year": ANALYSIS_YEAR,
        "mrio": "EXIOBASE v3.8.2 IOT ixi",
        "danish_block_correction": "sea-transport reallocation "
                                   "(Rormose Jensen & Iliev 2022)",
        "gwp_vintage": "IPCC AR6",
        "scope_boundary": "health and eldercare",
        "capital": "excluded from the headline",
    }])


# ---------------------------------------------------------------- utilities
def _read(rel: str) -> pd.DataFrame:
    """Read one denormalised gold table.

    Parameters
    ----------
    rel : str
        Path relative to ``data/gold/results``.

    Returns
    -------
    pandas.DataFrame
    """
    return pd.read_csv(os.path.join(str(OUTPUT_DIR), rel))


def _key(frame: pd.DataFrame, dim: pd.DataFrame, on_left: str, on_right: str,
         id_col: str, what: str) -> pd.DataFrame:
    """Replace a natural key with its surrogate id, failing on any orphan.

    Parameters
    ----------
    frame : pandas.DataFrame
        Fact rows.
    dim : pandas.DataFrame
        Dimension carrying ``on_right`` and ``id_col``.
    on_left, on_right : str
        Join columns.
    id_col : str
        Surrogate key to attach.
    what : str
        Name used in the error message.

    Returns
    -------
    pandas.DataFrame
        ``frame`` with ``id_col`` attached and ``on_left`` dropped.

    Raises
    ------
    AssertionError
        If any fact row fails to resolve to a dimension row.
    """
    before = len(frame)
    out = frame.merge(dim[[on_right, id_col]], left_on=on_left,
                      right_on=on_right, how="left")
    orphans = out[out[id_col].isna()][on_left].dropna().unique()
    assert len(orphans) == 0, (
        f"{what}: {len(orphans)} value(s) with no {id_col} row, "
        f"e.g. {sorted(map(str, orphans))[:5]}")
    assert len(out) == before, f"{what}: join changed the row count"
    if on_right != on_left:
        out = out.drop(columns=[on_right])
    return out.drop(columns=[on_left])


def main() -> None:
    """Derive the star schema, assert its integrity, and write it."""
    os.makedirs(STAR_DIR, exist_ok=True)

    src = {
        "footprint_node": _read("00_core_footprint/footprint_by_producing_node.csv"),
        "footprint_product": _read("00_core_footprint/footprint_by_purchased_product.csv"),
        "extended_node": _read("00_core_footprint/extended_indicators_by_producing_node.csv"),
        "scope_node": _read(f"{scopes_folder()}/scope_by_origin_and_industry.csv"),
        "national": _read("00_core_footprint/national_totals_summary.csv"),
        "health_function": _read("17_health_subsectors/footprint_by_health_function.csv"),
    }

    dim_region = build_dim_region()
    dim_industry, dim_industry_group = build_dim_industry()
    dim_indicator = build_dim_indicator(src)
    dim_model = build_dim_model()
    dim_scope = _simple_dim(src["scope_node"]["scope"], "scope_id", "scope_name")
    dim_component = _simple_dim(
        pd.concat([src["footprint_node"]["demand_component"],
                   src["extended_node"]["demand_component"]]),
        "demand_component_id", "demand_component_name")
    dim_function = _simple_dim(src["health_function"]["function"],
                               "health_function_id", "health_function_name")

    # ---- facts ------------------------------------------------------------
    facts: dict[str, pd.DataFrame] = {}

    node = pd.concat([src["footprint_node"], src["extended_node"]],
                     ignore_index=True)
    f = node[["indicator", "demand_component", "producing_country_iso3",
              "producing_sector_code", "value"]].copy()
    f = _key(f, dim_indicator, "indicator", "indicator_code", "indicator_id", "footprint_node.indicator")
    f = _key(f, dim_component, "demand_component", "demand_component_name", "demand_component_id", "footprint_node.component")
    f = _key(f, dim_region, "producing_country_iso3", "region_code", "region_id", "footprint_node.region")
    f = _key(f, dim_industry, "producing_sector_code", "industry_code", "industry_id", "footprint_node.industry")
    f = f.rename(columns={"region_id": "producing_region_id",
                          "industry_id": "producing_industry_id"})
    f.insert(0, "model_id", 1)
    facts["fact_footprint_node"] = f[
        ["model_id", "indicator_id", "demand_component_id",
         "producing_region_id", "producing_industry_id", "value"]]

    p = src["footprint_product"][["indicator", "demand_component",
                                  "purchased_country_iso3",
                                  "purchased_sector_code", "value"]].copy()
    p = _key(p, dim_indicator, "indicator", "indicator_code", "indicator_id", "footprint_product.indicator")
    p = _key(p, dim_component, "demand_component", "demand_component_name", "demand_component_id", "footprint_product.component")
    p = _key(p, dim_region, "purchased_country_iso3", "region_code", "region_id", "footprint_product.region")
    p = _key(p, dim_industry, "purchased_sector_code", "industry_code", "industry_id", "footprint_product.industry")
    p = p.rename(columns={"region_id": "purchased_region_id",
                          "industry_id": "purchased_industry_id"})
    p.insert(0, "model_id", 1)
    facts["fact_footprint_product"] = p[
        ["model_id", "indicator_id", "demand_component_id",
         "purchased_region_id", "purchased_industry_id", "value"]]

    s = src["scope_node"][["indicator", "scope", "producing_country_iso3",
                           "producing_sector_code", "value"]].copy()
    s = _key(s, dim_indicator, "indicator", "indicator_code", "indicator_id", "scope_node.indicator")
    s = _key(s, dim_scope, "scope", "scope_name", "scope_id", "scope_node.scope")
    s = _key(s, dim_region, "producing_country_iso3", "region_code", "region_id", "scope_node.region")
    s = _key(s, dim_industry, "producing_sector_code", "industry_code", "industry_id", "scope_node.industry")
    s = s.rename(columns={"region_id": "producing_region_id",
                          "industry_id": "producing_industry_id"})
    s.insert(0, "model_id", 1)
    facts["fact_scope_node"] = s[
        ["model_id", "indicator_id", "scope_id",
         "producing_region_id", "producing_industry_id", "value"]]

    # National totals travel with every result set so a health share can always
    # be formed without going back to another folder.
    n = src["national"][["indicator", "national_footprint", "national_supply_chain",
                         "national_direct_households", "healthcare_footprint_mrio",
                         "healthcare_share_pct"]].copy()
    n = _key(n, dim_indicator, "indicator", "indicator_code", "indicator_id", "national.indicator")
    n.insert(0, "model_id", 1)
    facts["fact_national_total"] = n

    h = src["health_function"][["indicator", "function", "value",
                                "expenditure_meur", "intensity_per_meur"]].copy()
    h = _key(h, dim_indicator, "indicator", "indicator_code", "indicator_id", "health_function.indicator")
    h = _key(h, dim_function, "function", "health_function_name", "health_function_id", "health_function.function")
    h.insert(0, "model_id", 1)
    facts["fact_health_function"] = h

    # Enforce each fact's declared grain. Sources can carry a finer grain than
    # the model does -- the scope detail distinguishes DRIVHUS combustion from
    # anaesthetic gases, both of which are Scope 1 at DNK/HEAL -- and two rows
    # at one key would silently double on any join. Summing here is the
    # modelling decision: the component split lives in the denormalised layer.
    grain = {
        "fact_footprint_node": ["model_id", "indicator_id", "demand_component_id",
                                "producing_region_id", "producing_industry_id"],
        "fact_footprint_product": ["model_id", "indicator_id", "demand_component_id",
                                   "purchased_region_id", "purchased_industry_id"],
        "fact_scope_node": ["model_id", "indicator_id", "scope_id",
                            "producing_region_id", "producing_industry_id"],
    }
    for name, keys in grain.items():
        before = facts[name]["value"].sum()
        facts[name] = (facts[name].groupby(keys, as_index=False)["value"].sum())
        assert np.isclose(facts[name]["value"].sum(), before, rtol=1e-12), \
            f"{name}: enforcing the grain changed the total"
        assert not facts[name].duplicated(subset=keys).any(), \
            f"{name}: grain still breached after aggregation"

    dims = {
        "dim_region": dim_region, "dim_industry": dim_industry,
        "dim_industry_group": dim_industry_group,
        "dim_indicator": dim_indicator, "dim_scope": dim_scope,
        "dim_demand_component": dim_component, "dim_model": dim_model,
        "dim_health_function": dim_function,
    }

    # ---- integrity --------------------------------------------------------
    for name, dim in dims.items():
        pk = dim.columns[0]
        assert dim[pk].is_unique, f"{name}: {pk} is not unique"
        assert dim[pk].notna().all(), f"{name}: {pk} has nulls"

    assert np.isclose(facts["fact_footprint_node"]["value"].sum(),
                      node["value"].sum(), rtol=1e-12), \
        "fact_footprint_node does not reproduce its source total"
    assert np.isclose(facts["fact_scope_node"]["value"].sum(),
                      src["scope_node"]["value"].sum(), rtol=1e-12), \
        "fact_scope_node does not reproduce its source total"

    for name, frame in {**dims, **facts}.items():
        frame.to_csv(os.path.join(STAR_DIR, f"{name}.csv"), index=False)

    print(f"star schema -> {STAR_DIR}")
    for name, frame in dims.items():
        print(f"  {name:24s} {len(frame):>8,} rows   PK {frame.columns[0]}")
    for name, frame in facts.items():
        print(f"  {name:24s} {len(frame):>8,} rows")


if __name__ == "__main__":
    main()
