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

Every reported result must be reachable from here at the finest grain the
pipeline produces, so that aggregates are derived rather than stored. Grain of
each fact, stated because a fact table with an unstated grain cannot be audited:

==============================  ===========================================
Fact                            One row per
==============================  ===========================================
``fact_footprint_bilateral``    model x indicator x demand component x
                                producing node x purchased node
``fact_footprint_node``         model x indicator x demand component x
                                producing region x producing industry
``fact_footprint_product``      model x indicator x demand component x
                                purchased region x purchased industry
``fact_scope_node``             model x indicator x scope x producing
                                region x producing industry
``fact_scope_component``        model x indicator x scope component
                                (the GHG-Protocol ladder, per model)
``fact_national_total``         model x indicator (national and health-care
                                totals side by side, with the share)
``fact_health_function``        model x indicator x health function
``fact_health_function_node``   model x indicator x health function x
                                producing region x producing industry
``fact_health_expenditure``     model x demand component x purchased region
                                x purchased industry
``fact_scenario_node``          model x scenario x indicator x producing
                                region x producing industry
``fact_production_layer``       model x indicator x production layer x
                                producing region x producing industry
``fact_impact_node``            model x impact category x producing region x
                                producing industry
``fact_capital_node``           model x capital treatment x indicator x
                                producing region x producing industry
``fact_capital_scenario``       model x capital treatment x indicator
``fact_ghg_species``            model x substance
``fact_gwp_vintage``            model x GWP vintage x indicator
==============================  ===========================================

``fact_footprint_node`` and ``fact_footprint_product`` are the two marginals of
``fact_footprint_bilateral`` and are kept because they are what most queries
want; the bilateral fact is the primary, and the build asserts that summing it
over either margin reproduces the marginal it corresponds to.

The model dimension
-------------------
The study reports results from more than one model configuration, and until now
``dim_model`` carried a single row, which made every model-varying result
unreachable. Two designs were available: a ``dim_time`` plus a set of model
attribute dimensions, or rows in ``dim_model``.

This build uses **rows in ``dim_model``, one per model run that was actually
executed**, and gives the variations that happen *inside* a run their own
dimensions (``dim_capital_treatment``, ``dim_gwp_vintage``,
``dim_impact_category``, ``dim_scenario``). The reason is foreign-key honesty. A
model row must describe the run that produced the fact row pointing at it. The
reference year, the background vintage and the sector boundary are properties of
a run: changing any of them means re-solving the model, and the outputs land in
their own folder. The capital treatment, the GWP vintage, the characterisation
method and the mitigation lever are variations computed *within* one run and
reported side by side, so folding them into ``dim_model`` would require a model
row per crossing, most of which no run ever produced, and would let a fact point
at a configuration that was never solved. A separate ``dim_time`` was rejected
for the opposite reason: the reference year never varies independently of the
background vintage and the demand vector in this study, so a year key would
promise a degree of freedom the model does not have.

The configured run is always ``model_id`` 1, so a fact built by this process
carries 1 unless it explicitly spans configurations.

File format
-----------
Dimensions and facts of at most :data:`CSV_ROW_LIMIT` rows are written as CSV,
because they stay diffable in git, which is how a change to a dimension gets
noticed in review. Larger facts are written as Parquet with pyarrow and snappy
compression, one file per fact: columnar, typed, far smaller than gzipped CSV,
and readable by pandas, DuckDB, Power BI and Fabric. Pickle is not used - it is
Python-only, version-fragile, and executes code on load, which is not acceptable
in a published deliverable.

The five facts that predate this rule stay CSV even where they exceed the limit,
because converting them would delete a tracked deliverable rather than add one.

Scope
-----
Two gold layers are classified private in :mod:`analysis.gold_scope` and are
absent from the working copy that feeds the co-author's branch. Every source is
therefore guarded by ``gold_scope.is_present``: the fact is built when its layer
is there and simply not built when it is not, so the same module runs in both
copies and produces the model each is entitled to.

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
from analysis import gold_scope
from analysis.constants import (ANALYSIS_YEAR, BACKGROUND_YEAR, MODEL_LABEL,
                                eriksen_folder, scopes_folder)
from analysis.detail_tables import node_labels

STAR_DIR = os.path.join(str(OUTPUT_DIR), "star")

#: Row count at which a table stops being written as CSV and becomes Parquet.
#: Below it, a git diff on the file is readable and is how a dimension change
#: gets caught in review; above it the diff is noise and the storage cost is not.
CSV_ROW_LIMIT = 50_000

#: Natural key of the member that the thresholded bilateral table carries so it
#: still reproduces its own total. ``footprint_bilateral_producer_x_purchase``
#: keeps the cells covering 99.5 % of each indicator and demand component and
#: puts the remaining tail on one row whose producing and purchased node are
#: both this label. It is a first-class dimension member rather than a null,
#: because a null foreign key cannot be audited.
REMAINDER_KEY = "BELOW_THRESHOLD_REMAINDER"

#: Industry-group names that no MRIO industry carries. They exist for the
#: bottom-up items and for the truncation remainder, and are appended **after**
#: the MRIO groups rather than sorted in with them, so that adding one cannot
#: renumber a group id that a published fact already points at.
EXTRA_INDUSTRY_GROUPS: tuple[str, ...] = (
    "Private travel", "Operational impact", "Below-threshold remainder")


# --------------------------------------------------------------- dimensions
def build_dim_region() -> pd.DataFrame:
    """Conformed region dimension.

    Returns
    -------
    pandas.DataFrame
        ``region_id`` (surrogate PK), ``region_code`` (natural key: ISO3, or the
        region name where no ISO3 exists), ``region_name``, ``world_region``,
        ``region_type``, ``is_row_region``, ``is_domestic``.
    """
    regions, _ = node_labels()
    dim = pd.DataFrame({
        "region_id": range(1, len(regions) + 1),
        "region_code": regions["iso3"].values,
        "region_name": regions["country_name"].values,
        "world_region": regions["world_region"].values,
        "is_row_region": regions["is_row_region"].values,
    })
    dim["region_type"] = "MRIO region"

    # The bilateral fact needs somewhere to put the below-threshold tail. Giving
    # it a member keeps the fact's total equal to its source's; dropping it
    # would not.
    remainder = pd.DataFrame([{
        "region_id": len(dim) + 1,
        "region_code": REMAINDER_KEY,
        "region_name": "Below-threshold remainder",
        "world_region": "Below-threshold remainder",
        "is_row_region": False,
        "region_type": "truncation remainder",
    }])
    dim = pd.concat([dim, remainder], ignore_index=True)
    dim["is_domestic"] = dim["region_code"].eq("DNK")
    return dim[["region_id", "region_code", "region_name", "world_region",
                "region_type", "is_row_region", "is_domestic"]]


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
    # Appended, not sorted in: see EXTRA_INDUSTRY_GROUPS.
    groups = pd.concat([groups, pd.DataFrame({
        "industry_group_name": list(EXTRA_INDUSTRY_GROUPS),
        "industry_group_id": range(len(groups) + 1,
                                   len(groups) + 1 + len(EXTRA_INDUSTRY_GROUPS)),
    })], ignore_index=True)

    dim = pd.DataFrame({
        "industry_id": range(1, len(sectors) + 1),
        "industry_code": sectors["sector_code"].values,
        "industry_name": sectors["sector_name"].values,
        "industry_group_name": sectors["sector_group"].values,
    }).merge(groups, on="industry_group_name", how="left")
    dim["industry_type"] = "MRIO industry"

    # Bottom-up items are part of the footprint but have no MRIO node. They are
    # first-class members of the industry dimension, flagged so a query can
    # include or exclude them deliberately rather than by accident. The order is
    # fixed and append-only: ids 164 and 165 are already carried by
    # fact_scope_node, so a new item goes on the end, never in the middle.
    extra = pd.DataFrame([
        {"industry_code": "BU_COMMUTE",
         "industry_name": "Bottom-up: employee commuting",
         "industry_group_name": "Private travel",
         "industry_type": "bottom-up item"},
        {"industry_code": "BU_TRAVEL",
         "industry_name": "Bottom-up: patient and visitor travel",
         "industry_group_name": "Private travel",
         "industry_type": "bottom-up item"},
        # The scenario layer labels the same class of item with its own codes,
        # which are kept as distinct members: they are produced by a different
        # module on a different construction, and merging them here would assert
        # an equivalence nothing in the pipeline establishes.
        {"industry_code": "B_HEAL",
         "industry_name": "Bottom-up: direct impact from health-care services",
         "industry_group_name": "Operational impact",
         "industry_type": "bottom-up item"},
        {"industry_code": "B_COMM",
         "industry_name": "Bottom-up: commute (total)",
         "industry_group_name": "Operational impact",
         "industry_type": "bottom-up item"},
        {"industry_code": "B_VISI",
         "industry_name": "Bottom-up: visitor travel (total)",
         "industry_group_name": "Operational impact",
         "industry_type": "bottom-up item"},
        {"industry_code": "B_PMDI",
         "industry_name": "Bottom-up: pMDI inhaler propellant",
         "industry_group_name": "Operational impact",
         "industry_type": "bottom-up item"},
        {"industry_code": "B_ANAE",
         "industry_name": "Bottom-up: anaesthetic gases",
         "industry_group_name": "Operational impact",
         "industry_type": "bottom-up item"},
        {"industry_code": REMAINDER_KEY,
         "industry_name": "Below-threshold remainder",
         "industry_group_name": "Below-threshold remainder",
         "industry_type": "truncation remainder"},
    ]).merge(groups, on="industry_group_name", how="left")
    extra["industry_id"] = range(len(dim) + 1, len(dim) + 1 + len(extra))

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

    # The DDL declares industry_group_id NOT NULL. It was null for the two
    # bottom-up rows for as long as their group was missing from the parent
    # dimension, which is the sort of contract breach a load into a real
    # database finds and a CSV does not.
    assert dim["industry_group_id"].notna().all(), \
        "dim_industry: industry_group_id is null for " + ", ".join(
            dim.loc[dim["industry_group_id"].isna(), "industry_code"])

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


#: The headline run for each reference year the study reports, keyed by year.
#: Only the entry for the year this process is **not** configured for is added,
#: because the configured one is always ``model_id`` 1. The label is stated
#: rather than composed from the environment: it must describe the run whose
#: outputs are on disk, not the run this process happens to be configured for.
YEAR_MODELS: dict[str, dict[str, str]] = {
    "2019": dict(
        background_year="2016",
        model_label="EXIOBASE v3.8.2 IOT_2016_ixi",
        # No corrected 2016 background exists, so the 2019 run carries none.
        # That is one of the three things changing between the two years, and is
        # why the pair is not a time series; see analysis.year_comparison.
        danish_block_correction="none (no corrected 2016 background exists)",
        source_folder="01_eriksen_replication/2019",
        note="pre-COVID validation baseline; not comparable with 2022 as a "
             "trend, because the reference year, the background vintage and "
             "the sea-transport reallocation all differ"),
    "2022": dict(
        background_year="2022_snacship",
        model_label="EXIOBASE v3.8.2 IOT_2022_ixi with Danish sea-transport "
                    "reallocation (Rormose Jensen & Iliev 2022)",
        danish_block_correction="sea-transport reallocation "
                                "(Rormose Jensen & Iliev 2022)",
        source_folder="01_eriksen_replication/2022",
        note="the manuscript's headline year"),
}

#: The sector-boundary runs, which exist for 2022 only: ``scenarios/`` holds one
#: run per boundary with no year subfolder, so a boundary row would be a claim
#: about a run that does not exist in any other year.
BOUNDARY_MODELS: tuple[dict[str, str], ...] = (
    dict(scope_boundary="health only (eldercare excluded)",
         source_folder="scenarios/health_only",
         note="HC_SCOPE=health_only; drops SHA residential eldercare "
              "(12401/13302) from the demand vector"),
    dict(scope_boundary="health, eldercare and childcare",
         source_folder="scenarios/zorg_en_welzijn",
         note="HC_SCOPE=zorg_en_welzijn; adds childcare (12402/13301) to match "
              "the expansive Dutch boundary of Steenmeijer et al. 2022"),
)


def build_dim_model() -> pd.DataFrame:
    """Model dimension: one row per model run the study reports.

    The configured run is ``model_id`` 1 so that a fact this process builds can
    carry a constant key; the other reported runs follow in a fixed order. See
    the module docstring for why the capital treatment, the GWP vintage, the
    characterisation method and the mitigation lever are **not** model rows.

    Returns
    -------
    pandas.DataFrame
        ``model_id`` (PK) and the attributes that make a result reproducible.
    """
    rows = [{
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
        "is_headline": True,
        "source_folder": eriksen_folder(),
        "note": "the configured run; every fact this build writes carries this "
                "model unless it explicitly spans configurations",
    }]

    def add(**kwargs: object) -> None:
        rows.append({
            "model_id": len(rows) + 1, "mrio": "EXIOBASE v3.8.2 IOT ixi",
            "gwp_vintage": "IPCC AR6", "capital": "excluded from the headline",
            "is_headline": False, **kwargs})

    for year, spec in sorted(YEAR_MODELS.items()):
        if year == ANALYSIS_YEAR:
            continue                        # already row 1
        add(analysis_year=year, scope_boundary="health and eldercare", **spec)
    if ANALYSIS_YEAR == "2022":
        for spec in BOUNDARY_MODELS:
            add(analysis_year="2022", background_year=BACKGROUND_YEAR,
                model_label=MODEL_LABEL,
                danish_block_correction="sea-transport reallocation "
                                        "(Rormose Jensen & Iliev 2022)",
                **spec)
    return pd.DataFrame(rows)[[
        "model_id", "model_label", "background_year", "analysis_year", "mrio",
        "danish_block_correction", "gwp_vintage", "scope_boundary", "capital",
        "is_headline", "source_folder", "note"]]


def build_dim_scenario(agg: pd.DataFrame,
                       selection: pd.DataFrame) -> pd.DataFrame:
    """Mitigation-scenario dimension, one row per modelled variant.

    A scenario code is not the key: ``B1`` covers two grid pathways at two
    target years, and ``P2`` three delivery shares. The variant - code, label
    and ambition together - is what a fact row identifies.

    Parameters
    ----------
    agg : pandas.DataFrame
        ``18_mitigation_scenarios/mitigation_scenarios.csv``.
    selection : pandas.DataFrame
        ``18_mitigation_scenarios/scenario_selection.csv``, which records the
        variants the combined scenario was built from.

    Returns
    -------
    pandas.DataFrame
        ``scenario_id`` (PK), the natural key, the ambition, the kind, the
        change coefficients, the rebound flag, the source and ``in_combined``.
    """
    natural = ["scenario_id", "scenario", "ambition"]
    keep = natural + ["scenario_type", "k_t", "k_p", "k_a", "edited_objects",
                      "rebound", "unbalanced_pct_of_output", "ambition_basis",
                      "source", "note"]
    dim = (agg[keep].drop_duplicates(natural).sort_values(natural)
           .reset_index(drop=True))
    dim = dim.rename(columns={"scenario_id": "scenario_code",
                              "scenario": "scenario_label",
                              "scenario_type": "scenario_kind"})

    # Which levers the combined scenario was assembled from is a property of the
    # lever, so it belongs here as a flag rather than in a fourth table.
    picked = set(map(tuple, selection[natural].astype(str).values))
    dim["in_combined"] = [
        (str(c), str(l), str(a)) in picked
        for c, l, a in zip(dim["scenario_code"], dim["scenario_label"],
                           dim["ambition"])]
    dim.insert(0, "scenario_id", range(1, len(dim) + 1))
    return dim


def build_dim_production_layer(detail_layers, agg_layers) -> pd.DataFrame:
    """Production-layer dimension for the Malik / Lenzen decomposition.

    Parameters
    ----------
    detail_layers : iterable of int
        Layer numbers the node-detail table resolves.
    agg_layers : iterable of str
        Layer labels the aggregate table carries, which includes the ``>20``
        residual that has no node detail.

    Returns
    -------
    pandas.DataFrame
        ``production_layer_id`` (PK), ``layer_code`` (natural key),
        ``layer_number``, ``layer_name``, ``is_residual``, ``has_node_detail``.
    """
    resolved = sorted(int(v) for v in set(detail_layers))
    names = {0: "direct (on-site, layer 0)", 1: "first-tier suppliers"}
    rows = [{"layer_code": str(n), "layer_number": n,
             "layer_name": names.get(n, f"layer {n}"),
             "is_residual": False, "has_node_detail": True}
            for n in resolved]
    # The aggregate closes the series with a residual tail. It is a member so
    # that the decomposition is complete on its face; it carries no node detail,
    # and is equal to the footprint total less the resolved layers.
    for label in sorted(set(map(str, agg_layers)) - {str(n) for n in resolved}):
        rows.append({"layer_code": label, "layer_number": None,
                     "layer_name": f"layers {label} (residual tail)",
                     "is_residual": True, "has_node_detail": False})
    dim = pd.DataFrame(rows)
    dim["layer_number"] = dim["layer_number"].astype("Int64")
    dim.insert(0, "production_layer_id", range(1, len(dim) + 1))
    return dim


def build_dim_impact_category(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Impact-category dimension across every characterisation method present.

    Parameters
    ----------
    frames : dict of str to pandas.DataFrame
        Node-detail impact tables, keyed by the method name to assume when the
        table itself carries no ``method`` column.

    Returns
    -------
    pandas.DataFrame
        ``impact_category_id`` (PK), ``method`` and ``category_code`` (the
        natural key together), ``unit``, ``quality_flag``.
    """
    seen = []
    for default_method, frame in frames.items():
        cols = frame.copy()
        if "method" not in cols.columns:
            cols["method"] = default_method
        if "quality_flag" not in cols.columns:
            cols["quality_flag"] = "ok"
        seen.append(cols[["method", "indicator", "unit", "quality_flag"]]
                    .drop_duplicates())
    dim = (pd.concat(seen, ignore_index=True)
           .drop_duplicates(["method", "indicator"])
           .sort_values(["method", "indicator"]).reset_index(drop=True))
    dim = dim.rename(columns={"indicator": "category_code"})
    dim.insert(0, "impact_category_id", range(1, len(dim) + 1))
    return dim


def build_dim_substance(species: pd.DataFrame) -> pd.DataFrame:
    """Substance dimension for the greenhouse gases the restatement resolves.

    Parameters
    ----------
    species : pandas.DataFrame
        ``15_gwp_vintage/gwp_by_species.csv``.

    Returns
    -------
    pandas.DataFrame
        ``substance_id`` (PK), ``substance_code`` (natural key), ``base_unit``,
        ``gwp100``, ``gwp_vintage``, ``is_restatable``.
    """
    dim = (species[["species", "unit", "ar6_gwp100"]]
           .drop_duplicates("species").sort_values("species")
           .reset_index(drop=True)
           .rename(columns={"species": "substance_code", "unit": "base_unit",
                            "ar6_gwp100": "gwp100"}))
    dim["gwp_vintage"] = "IPCC AR6 (2021)"
    # EXIOBASE supplies HFC and PFC already aggregated in CO2-equivalent, so
    # their vintage is not knowable from the satellite account and they carry no
    # factor. The flag says so rather than leaving a bare null to be guessed at.
    dim["is_restatable"] = dim["gwp100"].notna()
    dim.insert(0, "substance_id", range(1, len(dim) + 1))
    return dim


#: Capital treatments, in the order the sensitivity reports them. The last is
#: computed by a different module from the first three, on the published capital
#: use matrices rather than the GFCF ladder, and is kept as its own member: the
#: two do not agree, and the model should show that rather than hide it.
CAPITAL_TREATMENTS: tuple[tuple[str, str, bool, str], ...] = (
    ("baseline_capital_excluded", "Capital excluded (Steenmeijer-comparable)",
     False, "analysis.capital_gfcf"),
    ("A_exogenous_capital_service_flow",
     "Capital as an exogenous service flow (CFC of DK health and residential "
     "care, DST NABK69)", True, "analysis.capital_gfcf"),
    ("D_full_endogenisation", "Capital fully endogenised, A' = A + K",
     True, "analysis.capital_gfcf"),
    ("capital endogenised (Sodersten et al. 2018)",
     "Capital endogenised on the published capital-use matrices",
     True, "analysis.capital_endogenised_sodersten"),
)


def build_dim_capital_treatment() -> pd.DataFrame:
    """Capital-boundary dimension.

    Returns
    -------
    pandas.DataFrame
        ``capital_treatment_id`` (PK), ``treatment_code`` (natural key, exactly
        as the source tables spell it), ``treatment_name``,
        ``capital_included``, ``produced_by``.
    """
    dim = pd.DataFrame(
        [{"treatment_code": code, "treatment_name": name,
          "capital_included": included, "produced_by": script}
         for code, name, included, script in CAPITAL_TREATMENTS])
    dim.insert(0, "capital_treatment_id", range(1, len(dim) + 1))
    return dim


def build_dim_gwp_vintage(sensitivity: pd.DataFrame) -> pd.DataFrame:
    """Climate-characterisation vintage dimension, SAR to AR6.

    Parameters
    ----------
    sensitivity : pandas.DataFrame
        ``15_gwp_vintage/gwp_vintage_sensitivity.csv``.

    Returns
    -------
    pandas.DataFrame
        ``gwp_vintage_id`` (PK), ``vintage_code`` (natural key),
        ``is_study_default``.
    """
    dim = (sensitivity[["gwp_vintage", "is_study_default"]]
           .drop_duplicates("gwp_vintage").reset_index(drop=True)
           .rename(columns={"gwp_vintage": "vintage_code"}))
    dim.insert(0, "gwp_vintage_id", range(1, len(dim) + 1))
    return dim


#: The GHG-Protocol ladder as ``scopes_summary.csv`` writes it, mapped to a slug
#: and a role. The role matters: the ladder carries subtotals and a grand total
#: alongside the addends, so summing every row of ``fact_scope_component``
#: double counts. Declared rather than inferred from the indentation, and
#: asserted to cover exactly the rows each file holds.
SCOPE_COMPONENTS: tuple[tuple[str, str, str, str], ...] = (
    ("Scope 1 direct (DRIVHUS, excl. medical N2O)", "scope1_direct",
     "addend", "scope1_total"),
    ("+ Anaesthetic gases (bottom-up)", "scope1_anaesthetic",
     "addend", "scope1_total"),
    ("Scope 1 (Total)", "scope1_total", "subtotal", "grand_total"),
    ("Scope 2 (generation of purchased energy)", "scope2",
     "addend", "grand_total"),
    ("Scope 3 (MRIO supply chain excl. Scope 2)", "scope3_mrio",
     "addend", "scope3_total"),
    ("+ pMDI (bottom-up, use phase)", "scope3_pmdi", "addend", "scope3_total"),
    ("+ Commute (bottom-up)", "scope3_commute", "addend", "scope3_total"),
    ("Scope 3 (Total)", "scope3_total", "subtotal", "grand_total"),
    ("Outside protocol (patient/visitor travel)", "outside_protocol",
     "addend", "grand_total"),
    ("Grand Total", "grand_total", "grand total", ""),
)


def build_dim_scope_component() -> pd.DataFrame:
    """Scope-component dimension for the GHG-Protocol ladder.

    Returns
    -------
    pandas.DataFrame
        ``scope_component_id`` (PK), ``component_code`` (natural key),
        ``component_name``, ``component_role``, ``parent_component_code``.
    """
    dim = pd.DataFrame([
        {"component_code": code, "component_name": name.strip(),
         "component_role": role, "parent_component_code": parent}
        for name, code, role, parent in SCOPE_COMPONENTS])
    dim.insert(0, "scope_component_id", range(1, len(dim) + 1))
    return dim


# ---------------------------------------------------------------- utilities
def _read(rel: str, usecols: list[str] | None = None) -> pd.DataFrame:
    """Read one denormalised gold table.

    Parameters
    ----------
    rel : str
        Path relative to ``data/gold/results``. Gzipped CSVs are decompressed
        by extension.
    usecols : list of str, optional
        Columns to read. Given for the multi-million-row detail tables, whose
        denormalised label columns are exactly what the star model replaces.

    Returns
    -------
    pandas.DataFrame
    """
    return pd.read_csv(os.path.join(str(OUTPUT_DIR), rel), usecols=usecols)


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


def _multi_key(frame: pd.DataFrame, dim: pd.DataFrame, left: list[str],
               right: list[str], id_col: str, what: str) -> pd.DataFrame:
    """Resolve a compound natural key to its surrogate id, failing on orphans.

    Parameters
    ----------
    frame : pandas.DataFrame
        Fact rows.
    dim : pandas.DataFrame
        Dimension carrying ``right`` and ``id_col``.
    left, right : list of str
        Join columns, in matching order.
    id_col : str
        Surrogate key to attach.
    what : str
        Name used in the error message.

    Returns
    -------
    pandas.DataFrame
        ``frame`` with ``id_col`` attached and the natural key dropped.

    Raises
    ------
    AssertionError
        If any fact row fails to resolve to a dimension row.
    """
    before = len(frame)
    # The fact's columns are renamed to the dimension's, never the other way
    # round: a dimension's natural key can collide with its own surrogate key
    # (``scenario_code`` and ``scenario_id`` live in the same table), and
    # renaming that way round would produce two columns of the same name.
    left_side = frame.rename(columns=dict(zip(left, right)))
    lookup = dim[right + [id_col]].copy()
    for col in right:
        left_side[col] = left_side[col].astype(str)
        lookup[col] = lookup[col].astype(str)
    out = left_side.merge(lookup, on=right, how="left")
    missing = out[out[id_col].isna()][right].drop_duplicates()
    assert missing.empty, (
        f"{what}: {len(missing)} key tuple(s) with no {id_col} row, "
        f"e.g. {missing.head(3).to_dict('records')}")
    assert len(out) == before, f"{what}: join changed the row count"
    return out.drop(columns=right)


def _grain(facts: dict[str, pd.DataFrame], name: str, keys: list[str],
           measures: list[str] | None = None) -> None:
    """Sum a fact to its declared grain in place, preserving its total.

    Sources can carry a finer grain than the model does -- the scope detail
    distinguishes DRIVHUS combustion from anaesthetic gases, both of which are
    Scope 1 at DNK/HEAL -- and two rows at one key would silently double on any
    join. Summing here is the modelling decision.

    Parameters
    ----------
    facts : dict of str to pandas.DataFrame
        Fact accumulator, modified in place.
    name : str
        Fact name.
    keys : list of str
        Columns that define the grain.
    measures : list of str, optional
        Measures to sum. Defaults to ``["value"]``.

    Raises
    ------
    AssertionError
        If aggregation moves a total, or the grain is still breached after it.
    """
    measures = measures or ["value"]
    frame = facts[name]
    before = {m: frame[m].sum() for m in measures}
    out = frame.groupby(keys, as_index=False, dropna=False)[measures].sum()
    for measure in measures:
        assert np.isclose(out[measure].sum(), before[measure], rtol=1e-12), \
            f"{name}: enforcing the grain changed {measure}"
    assert not out.duplicated(subset=keys).any(), \
        f"{name}: grain still breached after aggregation"
    facts[name] = out[keys + measures]


#: Facts kept as CSV regardless of the row rule. Only tables under the limit
#: qualify, so this is a statement about stability rather than an exemption:
#: these four are the model's oldest facts, they are small enough to diff, and
#: keeping them legible in review is worth more than the bytes.
#:
#: ``fact_footprint_node`` was here too, at 193,047 rows. It is now Parquet, on
#: the reasoning that the star tree is the semantic model rather than the
#: publication surface: a reader who wants results as text has the denormalised
#: gold tables, which stay CSV.
LEGACY_CSV_FACTS: frozenset[str] = frozenset({
    "fact_footprint_product", "fact_scope_node",
    "fact_national_total", "fact_health_function"})


def _write(name: str, frame: pd.DataFrame) -> tuple[str, int]:
    """Write one star table, choosing CSV or Parquet by row count.

    Parameters
    ----------
    name : str
        Table name, without extension.
    frame : pandas.DataFrame
        Rows to write.

    Returns
    -------
    tuple
        ``(path, size_bytes)``.
    """
    if len(frame) <= CSV_ROW_LIMIT or name in LEGACY_CSV_FACTS:
        path = os.path.join(STAR_DIR, f"{name}.csv")
        frame.to_csv(path, index=False)
    else:
        path = os.path.join(STAR_DIR, f"{name}.parquet")
        frame.to_parquet(path, engine="pyarrow", compression="snappy",
                         index=False)
    return path, os.path.getsize(path)


#: Facts carrying several measures at once, whose grain is asserted but never
#: enforced by summing: adding a share to a share is not a modelling decision,
#: it is an error.
KEY_ONLY_GRAIN: dict[str, list[str]] = {
    "fact_national_total": ["model_id", "indicator_id"],
    "fact_health_function": ["model_id", "indicator_id", "health_function_id"],
    "fact_capital_scenario": ["model_id", "capital_treatment_id",
                              "indicator_id"],
    "fact_ghg_species": ["model_id", "substance_id"],
    "fact_gwp_vintage": ["model_id", "gwp_vintage_id", "indicator_id"],
}


def _resolve_column(frame: pd.DataFrame, candidates: tuple[str, ...],
                    what: str) -> str:
    """Return the first candidate column present, or fail saying what is there.

    The two private layers are absent from the working copy that feeds the
    co-author's branch, so their column names cannot be checked here. Resolving
    by candidate and failing loudly beats assuming one spelling and writing a
    wrong fact in the copy that does hold them.

    Parameters
    ----------
    frame : pandas.DataFrame
        Source table.
    candidates : tuple of str
        Column names to try, in order of preference.
    what : str
        Name used in the error message.

    Returns
    -------
    str
        The column name found.

    Raises
    ------
    AssertionError
        If none of the candidates is present.
    """
    for col in candidates:
        if col in frame.columns:
            return col
    raise AssertionError(
        f"{what}: none of {candidates} is present; the table carries "
        f"{list(frame.columns)}")


def main() -> None:
    """Derive the star schema, assert its integrity, and write it."""
    os.makedirs(STAR_DIR, exist_ok=True)

    src = {
        "footprint_node": _read("00_core_footprint/footprint_by_producing_node.csv"),
        "footprint_product": _read("00_core_footprint/footprint_by_purchased_product.csv"),
        "extended_node": _read("00_core_footprint/extended_indicators_by_producing_node.csv"),
        "scope_node": _read(f"{scopes_folder()}/scope_by_origin_and_industry.csv"),
        "national": _read("00_core_footprint/national_totals_summary.csv"),
    }
    # The health sub-sector layer is classified private, so it is absent from
    # the working copy that feeds the co-author's branch. Its fact and its
    # dimension are then simply not built, and the model is smaller rather than
    # broken.
    has_functions = gold_scope.is_present("17_health_subsectors")
    if has_functions:
        src["health_function"] = _read(
            "17_health_subsectors/footprint_by_health_function.csv")

    dim_region = build_dim_region()
    dim_industry, dim_industry_group = build_dim_industry()
    # dim_indicator is built from these five (or six) frames and no others. The
    # ids are positional in a sorted union, so unioning in a source that
    # introduces a new indicator would renumber every published fact. The extra
    # sources below are asserted to be subsets instead.
    dim_indicator = build_dim_indicator(src)
    dim_model = build_dim_model()
    dim_scope = _simple_dim(src["scope_node"]["scope"], "scope_id", "scope_name")
    dim_component = _simple_dim(
        pd.concat([src["footprint_node"]["demand_component"],
                   src["extended_node"]["demand_component"]]),
        "demand_component_id", "demand_component_name")
    dim_function = (_simple_dim(src["health_function"]["function"],
                                "health_function_id", "health_function_name")
                    if has_functions else None)
    dim_scope_component = build_dim_scope_component()

    dims = {
        "dim_region": dim_region, "dim_industry": dim_industry,
        "dim_industry_group": dim_industry_group,
        "dim_indicator": dim_indicator, "dim_scope": dim_scope,
        "dim_demand_component": dim_component, "dim_model": dim_model,
        "dim_scope_component": dim_scope_component,
    }
    if has_functions:
        dims["dim_health_function"] = dim_function

    # ---- facts ------------------------------------------------------------
    facts: dict[str, pd.DataFrame] = {}
    grains: dict[str, list[str]] = {}

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
    grains["fact_footprint_node"] = ["model_id", "indicator_id",
                                     "demand_component_id",
                                     "producing_region_id",
                                     "producing_industry_id"]

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
    grains["fact_footprint_product"] = ["model_id", "indicator_id",
                                        "demand_component_id",
                                        "purchased_region_id",
                                        "purchased_industry_id"]

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
    grains["fact_scope_node"] = ["model_id", "indicator_id", "scope_id",
                                 "producing_region_id", "producing_industry_id"]

    # National totals travel with every result set so a health share can always
    # be formed without going back to another folder.
    n = src["national"][["indicator", "national_footprint", "national_supply_chain",
                         "national_direct_households", "healthcare_footprint_mrio",
                         "healthcare_share_pct"]].copy()
    n = _key(n, dim_indicator, "indicator", "indicator_code", "indicator_id", "national.indicator")
    n.insert(0, "model_id", 1)
    facts["fact_national_total"] = n

    if has_functions:
        h = src["health_function"][["indicator", "function", "value",
                                    "expenditure_meur", "intensity_per_meur"]].copy()
        h = _key(h, dim_indicator, "indicator", "indicator_code", "indicator_id", "health_function.indicator")
        h = _key(h, dim_function, "function", "health_function_name", "health_function_id", "health_function.function")
        h.insert(0, "model_id", 1)
        facts["fact_health_function"] = h

    # ---- bilateral: the primary the two marginals above are derived from ---
    bilateral = _read(
        "00_core_footprint/footprint_bilateral_producer_x_purchase.csv.gz",
        usecols=["indicator", "unit", "demand_component",
                 "producing_country_iso3", "producing_sector_code",
                 "purchased_country_iso3", "purchased_sector_code", "value"])
    _assert_indicator_subset(bilateral, dim_indicator, "bilateral")
    b = bilateral.drop(columns=["unit"])
    b = _key(b, dim_indicator, "indicator", "indicator_code", "indicator_id", "bilateral.indicator")
    b = _key(b, dim_component, "demand_component", "demand_component_name", "demand_component_id", "bilateral.component")
    b = _key(b, dim_region, "producing_country_iso3", "region_code", "region_id", "bilateral.producing region")
    b = b.rename(columns={"region_id": "producing_region_id"})
    b = _key(b, dim_industry, "producing_sector_code", "industry_code", "industry_id", "bilateral.producing industry")
    b = b.rename(columns={"industry_id": "producing_industry_id"})
    b = _key(b, dim_region, "purchased_country_iso3", "region_code", "region_id", "bilateral.purchased region")
    b = b.rename(columns={"region_id": "purchased_region_id"})
    b = _key(b, dim_industry, "purchased_sector_code", "industry_code", "industry_id", "bilateral.purchased industry")
    b = b.rename(columns={"industry_id": "purchased_industry_id"})
    b.insert(0, "model_id", 1)
    facts["fact_footprint_bilateral"] = b[
        ["model_id", "indicator_id", "demand_component_id",
         "producing_region_id", "producing_industry_id",
         "purchased_region_id", "purchased_industry_id", "value"]]
    grains["fact_footprint_bilateral"] = [
        "model_id", "indicator_id", "demand_component_id",
        "producing_region_id", "producing_industry_id",
        "purchased_region_id", "purchased_industry_id"]

    # ---- expenditure: the demand vector the footprint is driven by --------
    ex = _read("00_core_footprint/expenditure_vector_detail.csv",
               usecols=["demand_component", "purchased_country_iso3",
                        "purchased_sector_code", "value", "unit"])
    assert set(ex["unit"].unique()) == {"M.EUR"}, \
        "fact_health_expenditure: expected M.EUR throughout"
    ex = ex.drop(columns=["unit"]).rename(columns={"value": "expenditure_meur"})
    ex = _key(ex, dim_component, "demand_component", "demand_component_name", "demand_component_id", "expenditure.component")
    ex = _key(ex, dim_region, "purchased_country_iso3", "region_code", "region_id", "expenditure.region")
    ex = _key(ex, dim_industry, "purchased_sector_code", "industry_code", "industry_id", "expenditure.industry")
    ex = ex.rename(columns={"region_id": "purchased_region_id",
                            "industry_id": "purchased_industry_id"})
    ex.insert(0, "model_id", 1)
    facts["fact_health_expenditure"] = ex[
        ["model_id", "demand_component_id", "purchased_region_id",
         "purchased_industry_id", "expenditure_meur"]]
    grains["fact_health_expenditure"] = [
        "model_id", "demand_component_id", "purchased_region_id",
        "purchased_industry_id"]

    # ---- mitigation scenarios ---------------------------------------------
    scen_agg = _read("18_mitigation_scenarios/mitigation_scenarios.csv")
    dim_scenario = build_dim_scenario(
        scen_agg, _read("18_mitigation_scenarios/scenario_selection.csv"))
    dims["dim_scenario"] = dim_scenario

    scen = _read("18_mitigation_scenarios/scenarios_by_producing_node.csv.gz",
                 usecols=["scenario_id", "scenario", "ambition", "indicator",
                          "unit", "producing_country_iso3",
                          "producing_sector_code", "value_type", "value"])
    _assert_indicator_subset(scen, dim_indicator, "scenarios")
    # value_type restates what the industry member already says. Asserting the
    # equivalence and dropping the column keeps one statement of the fact
    # instead of two that can disagree.
    bottom_up = set(dim_industry.loc[
        dim_industry["industry_type"] == "bottom-up item", "industry_code"])
    flagged = scen["value_type"].eq("bottom-up item")
    assert (scen["producing_sector_code"].isin(bottom_up) == flagged).all(), \
        ("fact_scenario_node: value_type disagrees with "
         "dim_industry.industry_type, so it cannot be dropped as redundant")
    sc = scen.drop(columns=["unit", "value_type"])
    sc = _multi_key(sc, dim_scenario, ["scenario_id", "scenario", "ambition"],
                    ["scenario_code", "scenario_label", "ambition"],
                    "scenario_id", "scenario_node.scenario")
    sc = _key(sc, dim_indicator, "indicator", "indicator_code", "indicator_id", "scenario_node.indicator")
    sc = _key(sc, dim_region, "producing_country_iso3", "region_code", "region_id", "scenario_node.region")
    sc = _key(sc, dim_industry, "producing_sector_code", "industry_code", "industry_id", "scenario_node.industry")
    sc = sc.rename(columns={"region_id": "producing_region_id",
                            "industry_id": "producing_industry_id"})
    sc.insert(0, "model_id", 1)
    facts["fact_scenario_node"] = sc[
        ["model_id", "scenario_id", "indicator_id", "producing_region_id",
         "producing_industry_id", "value"]]
    grains["fact_scenario_node"] = [
        "model_id", "scenario_id", "indicator_id", "producing_region_id",
        "producing_industry_id"]

    # ---- production layers ------------------------------------------------
    layer_detail = _read(
        "07_malik_replication/production_layers_by_producing_node.csv.gz",
        usecols=["indicator", "unit", "layer", "producing_country_iso3",
                 "producing_sector_code", "value"])
    layer_agg = _read("07_malik_replication/production_layers.csv")
    _assert_indicator_subset(layer_detail, dim_indicator, "production layers")
    dim_production_layer = build_dim_production_layer(
        layer_detail["layer"], layer_agg["layer"])
    dims["dim_production_layer"] = dim_production_layer

    pl = layer_detail.drop(columns=["unit"])
    pl["layer"] = pl["layer"].astype(str)
    pl = _key(pl, dim_production_layer, "layer", "layer_code",
              "production_layer_id", "production_layer.layer")
    pl = _key(pl, dim_indicator, "indicator", "indicator_code", "indicator_id", "production_layer.indicator")
    pl = _key(pl, dim_region, "producing_country_iso3", "region_code", "region_id", "production_layer.region")
    pl = _key(pl, dim_industry, "producing_sector_code", "industry_code", "industry_id", "production_layer.industry")
    pl = pl.rename(columns={"region_id": "producing_region_id",
                            "industry_id": "producing_industry_id"})
    pl.insert(0, "model_id", 1)
    facts["fact_production_layer"] = pl[
        ["model_id", "indicator_id", "production_layer_id",
         "producing_region_id", "producing_industry_id", "value"]]
    grains["fact_production_layer"] = [
        "model_id", "indicator_id", "production_layer_id",
        "producing_region_id", "producing_industry_id"]

    # ---- impact categories, every characterisation method present ---------
    # IMPACT World+ is a second method over the same node dimension, not a
    # different grain, so it lands in the same fact and is told apart by
    # dim_impact_category.method. Building it as a sibling table would make
    # "the footprint by category" two queries instead of one.
    impact_cols = ["indicator", "unit", "producing_country_iso3",
                   "producing_sector_code", "value"]
    impact_sources: dict[str, pd.DataFrame] = {}
    if gold_scope.is_present("12_impact_categories_full"):
        impact_sources["DESIRE characterisation v3.4"] = _read(
            "12_impact_categories_full/impact_categories_by_producing_node.csv.gz",
            usecols=impact_cols + ["method", "quality_flag"])
    if gold_scope.is_present("16_impact_world_plus"):
        iwp = _read(
            "16_impact_world_plus/impact_world_plus_by_producing_node.csv.gz")
        keep = [_resolve_column(iwp, (c,), f"impact_world_plus.{c}")
                for c in impact_cols]
        extra = [c for c in ("method", "quality_flag") if c in iwp.columns]
        impact_sources["IMPACT World+ v2.2.1"] = iwp[keep + extra]

    if impact_sources:
        dim_impact_category = build_dim_impact_category(impact_sources)
        dims["dim_impact_category"] = dim_impact_category
        pieces = []
        for method, frame in impact_sources.items():
            part = frame.copy()
            if "method" not in part.columns:
                part["method"] = method
            pieces.append(part[["method", "indicator",
                                "producing_country_iso3",
                                "producing_sector_code", "value"]])
        ic = pd.concat(pieces, ignore_index=True)
        ic = _multi_key(ic, dim_impact_category, ["method", "indicator"],
                        ["method", "category_code"], "impact_category_id",
                        "impact_node.category")
        ic = _key(ic, dim_region, "producing_country_iso3", "region_code", "region_id", "impact_node.region")
        ic = _key(ic, dim_industry, "producing_sector_code", "industry_code", "industry_id", "impact_node.industry")
        ic = ic.rename(columns={"region_id": "producing_region_id",
                                "industry_id": "producing_industry_id"})
        ic.insert(0, "model_id", 1)
        facts["fact_impact_node"] = ic[
            ["model_id", "impact_category_id", "producing_region_id",
             "producing_industry_id", "value"]]
        grains["fact_impact_node"] = [
            "model_id", "impact_category_id", "producing_region_id",
            "producing_industry_id"]

    # ---- health functions at node detail ----------------------------------
    if has_functions:
        hf = _read("17_health_subsectors/health_function_by_producing_node.csv.gz")
        fn_col = _resolve_column(hf, ("function", "health_function",
                                      "sha_function"),
                                 "health_function_node.function")
        cols = [_resolve_column(hf, (c,), f"health_function_node.{c}")
                for c in ("indicator", "producing_country_iso3",
                          "producing_sector_code", "value")]
        hfn = hf[[fn_col] + cols].rename(columns={fn_col: "function"})
        _assert_indicator_subset(hfn, dim_indicator, "health function detail")
        unknown = set(hfn["function"].astype(str)) - set(
            dim_function["health_function_name"].astype(str))
        assert not unknown, (
            "fact_health_function_node: function(s) absent from the aggregate "
            f"the dimension is built from: {sorted(unknown)[:5]}")
        hfn = _key(hfn, dim_indicator, "indicator", "indicator_code", "indicator_id", "health_function_node.indicator")
        hfn = _key(hfn, dim_function, "function", "health_function_name", "health_function_id", "health_function_node.function")
        hfn = _key(hfn, dim_region, "producing_country_iso3", "region_code", "region_id", "health_function_node.region")
        hfn = _key(hfn, dim_industry, "producing_sector_code", "industry_code", "industry_id", "health_function_node.industry")
        hfn = hfn.rename(columns={"region_id": "producing_region_id",
                                  "industry_id": "producing_industry_id"})
        hfn.insert(0, "model_id", 1)
        facts["fact_health_function_node"] = hfn[
            ["model_id", "indicator_id", "health_function_id",
             "producing_region_id", "producing_industry_id", "value"]]
        grains["fact_health_function_node"] = [
            "model_id", "indicator_id", "health_function_id",
            "producing_region_id", "producing_industry_id"]

    # ---- capital boundary --------------------------------------------------
    dim_capital = build_dim_capital_treatment()
    dims["dim_capital_treatment"] = dim_capital

    cap = _read("11_capital_gfcf/capital_endogenised_by_producing_node.csv.gz",
                usecols=["indicator", "unit", "treatment",
                         "producing_country_iso3", "producing_sector_code",
                         "value"])
    _assert_indicator_subset(cap, dim_indicator, "capital detail")
    cn = cap.drop(columns=["unit"])
    cn = _key(cn, dim_capital, "treatment", "treatment_code", "capital_treatment_id", "capital_node.treatment")
    cn = _key(cn, dim_indicator, "indicator", "indicator_code", "indicator_id", "capital_node.indicator")
    cn = _key(cn, dim_region, "producing_country_iso3", "region_code", "region_id", "capital_node.region")
    cn = _key(cn, dim_industry, "producing_sector_code", "industry_code", "industry_id", "capital_node.industry")
    cn = cn.rename(columns={"region_id": "producing_region_id",
                            "industry_id": "producing_industry_id"})
    cn.insert(0, "model_id", 1)
    facts["fact_capital_node"] = cn[
        ["model_id", "capital_treatment_id", "indicator_id",
         "producing_region_id", "producing_industry_id", "value"]]
    grains["fact_capital_node"] = [
        "model_id", "capital_treatment_id", "indicator_id",
        "producing_region_id", "producing_industry_id"]

    # Only one treatment is resolved to node detail. The other two are reported
    # as indicator totals, which is the finest grain the pipeline produces for
    # them, so they enter at that grain rather than not at all.
    cs = _read("11_capital_gfcf/capital_scenarios_by_indicator.csv",
               usecols=["scenario", "indicator", "value", "delta_vs_baseline",
                        "pct_vs_baseline", "per_capita"])
    _assert_indicator_subset(cs, dim_indicator, "capital scenarios",
                             unit_col=None)
    cs = _key(cs, dim_capital, "scenario", "treatment_code", "capital_treatment_id", "capital_scenario.treatment")
    cs = _key(cs, dim_indicator, "indicator", "indicator_code", "indicator_id", "capital_scenario.indicator")
    cs.insert(0, "model_id", 1)
    facts["fact_capital_scenario"] = cs[
        ["model_id", "capital_treatment_id", "indicator_id", "value",
         "delta_vs_baseline", "pct_vs_baseline", "per_capita"]]

    # ---- climate characterisation: species and vintages -------------------
    species = _read("15_gwp_vintage/gwp_by_species.csv")
    dim_substance = build_dim_substance(species)
    dims["dim_substance"] = dim_substance
    gs = species[["species", "mass_kg", "ar6_gwp100", "contribution_kt_co2eq"]] \
        .rename(columns={"ar6_gwp100": "gwp100",
                         "contribution_kt_co2eq": "co2eq_kt"})
    gs = _key(gs, dim_substance, "species", "substance_code", "substance_id", "ghg_species.species")
    gs.insert(0, "model_id", 1)
    facts["fact_ghg_species"] = gs[
        ["model_id", "substance_id", "mass_kg", "gwp100", "co2eq_kt"]]

    vintage = _read("15_gwp_vintage/gwp_vintage_sensitivity.csv")
    dim_gwp_vintage = build_dim_gwp_vintage(vintage)
    dims["dim_gwp_vintage"] = dim_gwp_vintage
    gv = vintage[["gwp_vintage", "healthcare_kt_co2eq", "national_kt_co2eq",
                  "healthcare_share_pct", "healthcare_t_per_capita",
                  "not_restatable_kt_co2eq"]].copy()
    # The sensitivity restates one indicator, so it names it by convention
    # rather than in a column; the star model requires the key to be explicit.
    gv["indicator"] = "climate_change"
    gv = _key(gv, dim_gwp_vintage, "gwp_vintage", "vintage_code", "gwp_vintage_id", "gwp_vintage.vintage")
    gv = _key(gv, dim_indicator, "indicator", "indicator_code", "indicator_id", "gwp_vintage.indicator")
    gv.insert(0, "model_id", 1)
    facts["fact_gwp_vintage"] = gv[
        ["model_id", "gwp_vintage_id", "indicator_id", "healthcare_kt_co2eq",
         "national_kt_co2eq", "healthcare_share_pct",
         "healthcare_t_per_capita", "not_restatable_kt_co2eq"]]

    # ---- the Monte Carlo, one row per draw per contribution group ---------
    # The uncertainty layer published its summary and kept its detail in a
    # NumPy array, which is outside the pattern every other layer follows and
    # therefore outside the model. It is the finest thing the pipeline produces
    # anywhere: a hundred thousand draws over nine groups, and the reported
    # median, interval and coefficient of variation are all derivable from it,
    # which is asserted below rather than assumed.
    draws_path = os.path.join(str(OUTPUT_DIR), "04_uncertainty_lenzen_ieooc",
                              "uncertainty_group_draws_gwp.npy")
    cov_path = os.path.join(str(OUTPUT_DIR), "04_uncertainty_lenzen_ieooc",
                            "uncertainty_group_covariance_gwp.csv")
    if os.path.exists(draws_path) and os.path.exists(cov_path):
        draws = np.load(draws_path)
        groups = pd.read_csv(cov_path).iloc[:, 0].astype(str).tolist()
        assert draws.ndim == 2 and draws.shape[1] == len(groups), (
            f"the draw array is {draws.shape} but the covariance file names "
            f"{len(groups)} groups; the grain cannot be established")

        dim_draw_group = pd.DataFrame({
            "draw_group_id": range(1, len(groups) + 1),
            "draw_group_name": groups})
        dims["dim_draw_group"] = dim_draw_group

        n_draws, n_groups = draws.shape
        facts["fact_uncertainty_draw"] = pd.DataFrame({
            "model_id": 1,
            "indicator_id": int(dim_indicator.loc[
                dim_indicator["indicator_code"] == "climate_change",
                "indicator_id"].iloc[0]),
            "draw_id": np.repeat(np.arange(1, n_draws + 1), n_groups),
            "draw_group_id": np.tile(np.arange(1, n_groups + 1), n_draws),
            "value": draws.reshape(-1)})

        # The published summary must be recoverable from the detail, or the
        # detail is not the same object the paper reports.
        totals = draws.sum(axis=1).astype("float64")
        pub = _read("04_uncertainty_lenzen_ieooc/uncertainty_totals.csv")
        row = pub[(pub["pharma_scenario"] == "A")
                  & pub["indicator"].str.contains("Global warming")].iloc[0]
        mcse = float(row["mcse_median_pct"]) / 100.0 * float(row["median"])
        for label, got, want, tol in (
                ("median", float(np.median(totals)), float(row["median"]),
                 max(5 * mcse, 1e-6)),
                ("2.5th percentile", float(np.percentile(totals, 2.5)),
                 float(row["p2_5"]), max(5 * mcse, 1e-6)),
                ("97.5th percentile", float(np.percentile(totals, 97.5)),
                 float(row["p97_5"]), max(5 * mcse, 1e-6)),
                ("coefficient of variation",
                 100.0 * totals.std(ddof=1) / totals.mean(),
                 float(row["cv_pct"]), 0.01)):
            assert abs(got - want) <= tol, (
                f"the draws do not reproduce the published {label}: "
                f"{got:,.4f} against {want:,.4f}, tolerance {tol:,.4f}")

    # ---- the scope ladder, per model --------------------------------------
    # This is what makes the 2019 run and the two sector-boundary runs reachable
    # at all: it is the only machine-readable output they share, so it is the
    # finest grain the pipeline produces for them.
    ladder = []
    for model_id, folder in zip(dim_model["model_id"],
                                dim_model["source_folder"]):
        path = os.path.join(str(OUTPUT_DIR), *folder.split("/"),
                            "scopes_summary.csv")
        if not os.path.exists(path):
            continue
        frame = pd.read_csv(path)
        raw_to_code = {name.strip(): code
                       for name, code, _, _ in SCOPE_COMPONENTS}
        seen = {str(v).strip() for v in frame["Component"]}
        assert seen == set(raw_to_code), (
            f"fact_scope_component: {folder}/scopes_summary.csv does not carry "
            f"the declared ladder; unexpected {sorted(seen - set(raw_to_code))}, "
            f"missing {sorted(set(raw_to_code) - seen)}")
        ladder.append(pd.DataFrame({
            "model_id": model_id,
            "component_code": [raw_to_code[str(v).strip()]
                               for v in frame["Component"]],
            "indicator": "climate_change",
            "value": frame["kt_CO2eq"].values,
        }))
    if ladder:
        lad = pd.concat(ladder, ignore_index=True)
        lad = _key(lad, dim_scope_component, "component_code", "component_code",
                   "scope_component_id", "scope_component.component")
        lad = _key(lad, dim_indicator, "indicator", "indicator_code", "indicator_id", "scope_component.indicator")
        facts["fact_scope_component"] = lad[
            ["model_id", "indicator_id", "scope_component_id", "value"]]
        grains["fact_scope_component"] = ["model_id", "indicator_id",
                                          "scope_component_id"]

    # ---- grain -------------------------------------------------------------
    for name, keys in grains.items():
        measures = ["expenditure_meur"] if name == "fact_health_expenditure" \
            else ["value"]
        _grain(facts, name, keys, measures)

    # Facts whose source is already one row per key are not summed -- summing a
    # multi-measure fact would add shares and percentages, which is meaningless
    # -- but their grain is asserted, because that is the property a join needs.
    for name, keys in KEY_ONLY_GRAIN.items():
        if name in facts:
            assert not facts[name].duplicated(subset=keys).any(), \
                f"{name}: declared grain {keys} is breached"

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

    _assert_bilateral_margins(facts, dim_region, dim_industry)
    _assert_scenario_totals(facts, dim_scenario, dim_indicator, scen_agg)
    _assert_layer_totals(facts, dim_production_layer, dim_indicator, layer_agg)
    _assert_expenditure_total(facts, dim_component,
                              _read("00_core_footprint/expenditure_summary.csv"))
    if has_functions:
        _assert_function_margin(facts)

    # ---- write ------------------------------------------------------------
    written: dict[str, tuple[str, int]] = {}
    for name, frame in {**dims, **facts}.items():
        written[name] = _write(name, frame)

    print(f"star schema -> {STAR_DIR}")
    for kind, tables in (("dim", dims), ("fact", facts)):
        for name in tables:
            path, size = written[name]
            fmt = "parquet" if path.endswith(".parquet") else "csv"
            print(f"  {name:28s} {len(tables[name]):>9,} rows  {fmt:7s} "
                  f"{size / 1e6:>8.2f} MB")

    stale = sorted(
        f for f in os.listdir(STAR_DIR)
        if f.endswith((".csv", ".parquet"))
        and os.path.splitext(f)[0] not in written)
    if stale:
        # Not deleted: these are tracked deliverables, and removing one is a
        # decision for a person. Reported, so that a table left behind by a run
        # of a different scope cannot pass for part of this model.
        print(f"\n  {len(stale)} table(s) on disk that this build did not "
              f"produce: {', '.join(stale)}")


def _assert_indicator_subset(frame: pd.DataFrame, dim_indicator: pd.DataFrame,
                             what: str, unit_col: str | None = "unit") -> None:
    """Assert a source's indicators are already in the indicator dimension.

    ``dim_indicator`` numbers its rows positionally over a sorted union, so
    unioning in a source that introduces a new indicator code would renumber
    every published fact. Sources added after the dimension was fixed are
    therefore checked against it rather than merged into it.

    Parameters
    ----------
    frame : pandas.DataFrame
        Source table carrying ``indicator``.
    dim_indicator : pandas.DataFrame
        The indicator dimension.
    what : str
        Name used in the error message.
    unit_col : str or None, optional
        Column carrying the unit, checked against the dimension when present.

    Raises
    ------
    AssertionError
        If the source names an indicator or a unit the dimension does not.
    """
    known = dict(zip(dim_indicator["indicator_code"], dim_indicator["unit"]))
    unknown = sorted(set(frame["indicator"].astype(str)) - set(known))
    assert not unknown, (
        f"{what}: indicator(s) absent from dim_indicator: {unknown[:5]}. "
        "Adding them would renumber indicator_id on every published fact.")
    if unit_col and unit_col in frame.columns:
        clash = {(i, u) for i, u in
                 frame[["indicator", unit_col]].drop_duplicates().values
                 if known[str(i)] != u}
        assert not clash, f"{what}: unit disagrees with dim_indicator: {clash}"


def _assert_bilateral_margins(facts: dict[str, pd.DataFrame],
                              dim_region: pd.DataFrame,
                              dim_industry: pd.DataFrame) -> None:
    """The bilateral fact must reproduce both of its marginals.

    Three things are checked, because the bilateral table is thresholded at
    99.5 % coverage per indicator and demand component with the tail on one
    remainder row:

    1. the grand total per indicator and demand component equals both marginals
       exactly, which the remainder row is what makes true;
    2. away from the remainder member the producing (purchased) margin never
       exceeds the corresponding marginal fact, since truncation only drops
       cells;
    3. the summed shortfall equals the remainder total, so nothing is lost and
       nothing is invented.

    Parameters
    ----------
    facts : dict of str to pandas.DataFrame
        Fact accumulator, already at grain.
    dim_region, dim_industry : pandas.DataFrame
        Needed to locate the remainder member's surrogate ids.

    Raises
    ------
    AssertionError
        If any of the three fails.
    """
    bil = facts["fact_footprint_bilateral"]
    rem_region = int(dim_region.loc[dim_region["region_code"] == REMAINDER_KEY,
                                    "region_id"].iloc[0])
    rem_industry = int(dim_industry.loc[
        dim_industry["industry_code"] == REMAINDER_KEY, "industry_id"].iloc[0])
    by = ["indicator_id", "demand_component_id"]

    for margin, region_col, industry_col in (
            ("fact_footprint_node", "producing_region_id", "producing_industry_id"),
            ("fact_footprint_product", "purchased_region_id", "purchased_industry_id")):
        other = facts[margin]
        # The marginal facts also carry indicators the bilateral table does not
        # (the extended stressors are not resolved bilaterally), so compare only
        # where both are defined.
        scope = other[other["indicator_id"].isin(bil["indicator_id"].unique())]
        total_bil = bil.groupby(by)["value"].sum()
        total_other = scope.groupby(by)["value"].sum()
        joined = pd.DataFrame({"b": total_bil, "o": total_other})
        assert joined.notna().all().all(), \
            f"fact_footprint_bilateral: {margin} covers a different key set"
        assert np.allclose(joined["b"], joined["o"], rtol=1e-12), \
            (f"fact_footprint_bilateral does not reproduce {margin}: worst "
             f"relative deviation "
             f"{((joined['b'] - joined['o']).abs() / joined['o'].abs()).max():.3e}")

        kept = bil[bil[region_col] != rem_region]
        keys = by + [region_col, industry_col]
        node_margin = kept.groupby(keys)["value"].sum()
        node_other = scope.groupby(keys)["value"].sum()
        cmp = pd.DataFrame({"k": node_margin, "o": node_other}).fillna(0.0)
        assert (cmp["k"] - cmp["o"]).max() < 1e-9, \
            (f"fact_footprint_bilateral: the {margin} margin exceeds the "
             f"marginal fact at some node, which truncation cannot do")
        remainder = bil.loc[bil[region_col] == rem_region, "value"].sum()
        assert np.isclose((cmp["o"] - cmp["k"]).sum(), remainder, rtol=1e-9), \
            (f"fact_footprint_bilateral: the {margin} shortfall does not equal "
             f"the below-threshold remainder")
        assert (bil.loc[bil[region_col] == rem_region, industry_col]
                == rem_industry).all(), \
            "fact_footprint_bilateral: a remainder row carries a real industry"


def _assert_scenario_totals(facts: dict[str, pd.DataFrame],
                            dim_scenario: pd.DataFrame,
                            dim_indicator: pd.DataFrame,
                            agg: pd.DataFrame) -> None:
    """The scenario node fact must reproduce every published scenario total.

    This is what makes the aggregate table derivable rather than a second
    source: ``scenario_value`` is the node fact summed over nodes, and the
    change against the baseline is that less ``fact_footprint_node``.

    Parameters
    ----------
    facts : dict of str to pandas.DataFrame
        Fact accumulator.
    dim_scenario, dim_indicator : pandas.DataFrame
        Dimensions the fact was keyed with.
    agg : pandas.DataFrame
        ``18_mitigation_scenarios/mitigation_scenarios.csv``.

    Raises
    ------
    AssertionError
        If any scenario total fails to reproduce.
    """
    keyed = _multi_key(
        agg[["scenario_id", "scenario", "ambition", "indicator",
             "scenario_value"]].copy(),
        dim_scenario, ["scenario_id", "scenario", "ambition"],
        ["scenario_code", "scenario_label", "ambition"], "scenario_id",
        "scenario totals.scenario")
    keyed = _key(keyed, dim_indicator, "indicator", "indicator_code",
                 "indicator_id", "scenario totals.indicator")
    node = facts["fact_scenario_node"].groupby(
        ["scenario_id", "indicator_id"])["value"].sum()
    joined = keyed.set_index(["scenario_id", "indicator_id"])
    joined["node"] = node
    assert joined["node"].notna().all(), \
        "fact_scenario_node: a published scenario total has no node rows"
    assert np.allclose(joined["node"], joined["scenario_value"], rtol=1e-9), (
        "fact_scenario_node does not reproduce the published scenario totals: "
        f"worst relative deviation "
        f"{((joined['node'] - joined['scenario_value']).abs() / joined['scenario_value'].abs()).max():.3e}")


def _assert_layer_totals(facts: dict[str, pd.DataFrame],
                         dim_layer: pd.DataFrame,
                         dim_indicator: pd.DataFrame,
                         agg: pd.DataFrame) -> None:
    """The layer node fact must reproduce the published layer totals.

    Parameters
    ----------
    facts : dict of str to pandas.DataFrame
        Fact accumulator.
    dim_layer, dim_indicator : pandas.DataFrame
        Dimensions the fact was keyed with.
    agg : pandas.DataFrame
        ``07_malik_replication/production_layers.csv``.

    Raises
    ------
    AssertionError
        If a layer that has node detail fails to reproduce its total.
    """
    resolved = dim_layer[dim_layer["has_node_detail"]]
    keyed = agg[["indicator", "layer", "value"]].copy()
    keyed["layer"] = keyed["layer"].astype(str)
    keyed = keyed[keyed["layer"].isin(set(resolved["layer_code"]))]
    keyed = _key(keyed, resolved, "layer", "layer_code", "production_layer_id",
                 "layer totals.layer")
    keyed = _key(keyed, dim_indicator, "indicator", "indicator_code",
                 "indicator_id", "layer totals.indicator")
    node = facts["fact_production_layer"].groupby(
        ["indicator_id", "production_layer_id"])["value"].sum()
    joined = keyed.set_index(["indicator_id", "production_layer_id"])
    joined["node"] = node
    assert joined["node"].notna().all(), \
        "fact_production_layer: a published layer total has no node rows"
    assert np.allclose(joined["node"], joined["value"], rtol=1e-9), \
        ("fact_production_layer does not reproduce the published layer totals: "
         f"worst relative deviation "
         f"{((joined['node'] - joined['value']).abs() / joined['value'].abs()).max():.3e}")


def _assert_expenditure_total(facts: dict[str, pd.DataFrame],
                              dim_component: pd.DataFrame,
                              summary: pd.DataFrame) -> None:
    """The expenditure fact must reproduce the demand vector it details.

    Parameters
    ----------
    facts : dict of str to pandas.DataFrame
        Fact accumulator.
    dim_component : pandas.DataFrame
        The demand-component dimension.
    summary : pandas.DataFrame
        ``00_core_footprint/expenditure_summary.csv``.

    Raises
    ------
    AssertionError
        If a component's detail does not sum to its published ``y_H`` total.
    """
    keyed = _key(summary[["demand_component", "y_H_meur"]].copy(),
                 dim_component, "demand_component", "demand_component_name",
                 "demand_component_id", "expenditure totals.component")
    detail = facts["fact_health_expenditure"].groupby(
        "demand_component_id")["expenditure_meur"].sum()
    joined = keyed.set_index("demand_component_id")
    joined["detail"] = detail
    assert joined["detail"].notna().all(), \
        "fact_health_expenditure: a demand component has no detail rows"
    assert np.allclose(joined["detail"], joined["y_H_meur"], rtol=1e-12), \
        "fact_health_expenditure does not reproduce the published y_H totals"


def _assert_function_margin(facts: dict[str, pd.DataFrame]) -> None:
    """The health-function node fact must reproduce the aggregate it replaces.

    The 25-row aggregate stays because it also carries expenditure and
    intensity, which node detail cannot supply. Its footprint column, though,
    must now be derived from the node fact rather than believed.

    Parameters
    ----------
    facts : dict of str to pandas.DataFrame
        Fact accumulator.

    Raises
    ------
    AssertionError
        If the node margin does not reproduce the aggregate.
    """
    keys = ["model_id", "indicator_id", "health_function_id"]
    node = facts["fact_health_function_node"].groupby(keys)["value"].sum()
    agg = facts["fact_health_function"].set_index(keys)["value"]
    joined = pd.DataFrame({"n": node, "a": agg}).dropna()
    assert len(joined) == len(agg), \
        "fact_health_function_node does not cover every aggregate row"
    assert np.allclose(joined["n"], joined["a"], rtol=1e-9), \
        ("fact_health_function_node does not reproduce fact_health_function: "
         f"worst relative deviation "
         f"{((joined['n'] - joined['a']).abs() / joined['a'].abs()).max():.3e}")


if __name__ == "__main__":
    main()
