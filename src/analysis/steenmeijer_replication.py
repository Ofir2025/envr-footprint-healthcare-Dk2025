# -*- coding: utf-8 -*-
"""Steenmeijer et al. (2022) replication: Denmark against the Dutch template.

This study replicates Steenmeijer et al., *The environmental impact of the
Dutch health-care sector beyond climate change* (Lancet Planet Health 2022).
FAIR replication means being able to place our Danish result beside every number
they published, in their own table structure, for every impact category - not
only climate.

This module builds that comparison. Their published values are transcribed here
as a documented constant with provenance, so the comparison is reproducible
without re-reading the paper.

Comparability warnings, stated rather than buried
-------------------------------------------------
Three differences make a naive side-by-side misleading, and each is carried
explicitly in the output tables:

**Boundary.** The Dutch study uses the broad *zorg en welzijn* definition, which
**includes childcare and youth care**. Our default Danish boundary is health
plus eldercare. The like-for-like scenario is ``HC_SCOPE=zorg_en_welzijn``, and
both are reported.

**Waste.** Their waste extension sums all 19 hybrid fractions. Ours is filtered
to the statistical waste boundary (Regulation (EC) 2150/2002 / DST AFFALD01),
which excludes manure, sewage, mining and unused mining material. The two waste
numbers are therefore **not on the same boundary**, and the unfiltered Danish
figure is reported alongside for a like-for-like reading.

**Year and release.** Denmark 2022 on EXIOBASE v3.8.2 against the Netherlands
2016 on EXIOBASE v3. Absolute totals are not comparable across two different
economies; per-capita values are the meaningful comparison and are computed.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.steenmeijer_replication``
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from analysis.constants import (ANALYSIS_YEAR, DK_POPULATION, INDICATORS,
                                eriksen_folder,
                                MODEL_LABEL)
from paths import OUTPUT_DIR, PROJECT_ROOT

FOLDER = "13_steenmeijer_replication"

#: Netherlands population, 1 January 2016 (CBS), the reference year of the
#: Dutch study.
NL_POPULATION: int = 17_030_314

#: Published Dutch values, transcribed from Steenmeijer et al. (2022).
#: Source: the Lancet article's single table, "Environmental footprints by
#: top-down and bottom-up categories" (identical to RIVM report 2022-0159
#: table 8). ``NA`` in the paper means not applicable; ``··`` means not
#: assessed, and is carried here as ``numpy.nan``.
NL_TABLE: dict[str, dict[str, float]] = {
    "Total": dict(expenditure_meur=92_515, climate_change=17_575,
                  material_extraction=33_801, blue_water_consumption=394.0,
                  land_use=23_845, waste_generation=4_803),
    "Health-care services": dict(expenditure_meur=86_096, climate_change=10_779,
                                 material_extraction=14_714,
                                 blue_water_consumption=218.0,
                                 land_use=13_748, waste_generation=2_811),
    "Pharmaceuticals and chemical products": dict(
        expenditure_meur=3_778, climate_change=4_909,
        material_extraction=18_261, blue_water_consumption=169.0,
        land_use=9_744, waste_generation=1_780),
    "Medical appliances": dict(expenditure_meur=2_641, climate_change=864,
                               material_extraction=783,
                               blue_water_consumption=7.0, land_use=351,
                               waste_generation=212),
    "Release of anaesthetic gases": dict(
        expenditure_meur=np.nan, climate_change=14, material_extraction=np.nan,
        blue_water_consumption=np.nan, land_use=np.nan,
        waste_generation=np.nan),
    "Release of pMDI propellants": dict(
        expenditure_meur=np.nan, climate_change=77, material_extraction=np.nan,
        blue_water_consumption=np.nan, land_use=np.nan,
        waste_generation=np.nan),
    "Private travel": dict(expenditure_meur=np.nan, climate_change=932,
                           material_extraction=42,
                           blue_water_consumption=0.29, land_use=3,
                           waste_generation=np.nan),
}

#: Dutch national consumption footprints and the health-care share of each.
#: Source: supplementary table S7 (= RIVM table 9). Computed by the authors on
#: the unaltered Dutch final demand of the same EE-MRIO.
NL_NATIONAL: dict[str, dict[str, float]] = {
    "climate_change": dict(national=241_358, share_pct=7.3, unit="kt CO2eq"),
    "material_extraction": dict(national=259_060, share_pct=13.0, unit="kt"),
    "blue_water_consumption": dict(national=5_226, share_pct=7.5, unit="Mm3"),
    "land_use": dict(national=329_537, share_pct=7.2, unit="km2"),
    "waste_generation": dict(national=113_826, share_pct=4.2, unit="kt"),
}

#: Danish waste on the Dutch (unfiltered, all 19 fractions) boundary, for a
#: like-for-like reading. Regenerate with ``HC_WASTE_FRACTIONS=all``.
DK_WASTE_ALL_FRACTIONS_KT: float = 829.2

INDICATOR_UNIT: dict[str, str] = {name: unit for _, name, unit in INDICATORS}


# ---------------------------------------------------------------------------
# The published Dutch results as FAIR data.
#
# The RIVM repository ships its results as six Excel workbooks. A workbook is
# not a fact table: the sheets are wide, the index columns are blank-filled the
# way Excel writes a MultiIndex, the impact columns carry their unit inside the
# column name, and nothing in the file says where it came from. The functions
# below convert every sheet of every workbook into the same long format the
# Danish gold layer uses, so the two countries can be read with one vocabulary,
# and assert every column total back against the workbook it came from.
#
# Nothing here recomputes a Dutch number. The archive is transcribed, not
# re-run: their EXIOBASE v3.7 background is not in this repository, and a
# re-run would no longer be their published result.
# ---------------------------------------------------------------------------

#: Upstream repository of the archived Dutch model and results.
RIVM_UPSTREAM: str = "https://github.com/rivm-syso/envr-footprint-healthcare"

#: Where the verbatim archive of that repository sits, relative to a working
#: copy that carries it. This working copy is the manuscript subset and does
#: not, so the location is overridable; see :func:`rivm_archive_dir`.
RIVM_ARCHIVE_REL: str = os.path.join("archive", "rivm_steenmeijer_2022")

#: Environment variable naming the archive when it lives in a companion
#: working copy rather than in this one.
RIVM_ARCHIVE_ENV: str = "HC_RIVM_ARCHIVE_DIR"

#: Reference year of every Dutch figure in the archive. Their waste extension
#: is 2011 (paper p e951); every other pressure is 2016.
NL_REFERENCE_YEAR: int = 2016

#: Workbook impact column -> (indicator, unit), in the Danish gold vocabulary.
IMPACT_COLUMNS: dict[str, tuple[str, str]] = {
    "Global warming (ktCO2eq)": ("climate_change", "kt CO2eq"),
    "Material extraction (kt)": ("material_extraction", "kt"),
    "Blue water consumption (Mm3)": ("blue_water_consumption", "Mm3"),
    "Land use (km2)": ("land_use", "km2"),
    "Waste generation (kt)": ("waste_generation", "kt"),
}

#: Workbook expenditure column -> demand component, in the Danish gold
#: vocabulary. The Dutch column names are their own ("Medical durables goods");
#: the values they hold are the same three components.
EXPENDITURE_COLUMNS: dict[str, str] = {
    "Total (MEUR)": "total",
    "Healthcare services": "healthcare_services",
    "Pharmaceuticals and consumables": "pharmaceuticals",
    "Medical durables goods": "medical_appliances",
}

#: Workbook column -> gold column, applied before anything else so that the
#: rest of the conversion speaks one vocabulary. ``Scope`` carries the GHG
#: Protocol scope in the contribution workbook and Direct/Indirect in the
#: hotspot workbook; both are scope statements and share the column.
COLUMN_RENAME: dict[str, str] = {
    "ISO3": "country_iso3",
    "RegName": "country_name",
    "Region": "world_region",
    "SecTxtCode": "sector_code",
    "SecName": "sector_name",
    "SAggDescription": "sector_group",
    "Scope": "ghg_protocol_scope",
}

#: EXIOBASE v3.7 codes the archive writes that are not ISO 3166-1 alpha-3.
#: The gold convention is alpha-3 for the 44 countries, and the five
#: rest-of-world regions keep their own codes (WA/WL/WE/WF/WM).
ISO3_FIXES: dict[str, str] = {"ROM": "ROU"}

#: Rows of the archive that are not EXIOBASE nodes but the study's own
#: bottom-up items, keyed by the pseudo-sector code the archive gives them.
BOTTOM_UP_CODES: frozenset[str] = frozenset(
    {"B_HEAL", "B_ANAE", "B_PMDI", "B_COMM", "B_VISI", "B_REST"})

#: The code the archive gives the part of the private-travel life-cycle result
#: that was never bridged to an EXIOBASE node: "Not distributed travel impact".
#: The captions of their figures 2 and 3 say this component was distributed
#: proportionally, which is what :func:`_figure_shares` does with it.
UNDISTRIBUTED_CODE: str = "B_REST"


def rivm_archive_dir(archive_dir: str | os.PathLike[str] | None = None) -> Path:
    """Locate the verbatim archive of the RIVM repository.

    Parameters
    ----------
    archive_dir : str or os.PathLike, optional
        Explicit location. When omitted, ``HC_RIVM_ARCHIVE_DIR`` is consulted,
        then ``archive/rivm_steenmeijer_2022`` inside this working copy, then
        the same path inside a sibling working copy of the companion
        repository.

    Returns
    -------
    pathlib.Path
        Directory holding the archive's ``output/`` and ``scripts/`` folders.

    Raises
    ------
    FileNotFoundError
        When no candidate holds ``output/Table1.xlsx``, rather than writing
        gold tables from a directory that is not the archive.
    """
    candidates: list[Path] = []
    if archive_dir is not None:
        candidates.append(Path(archive_dir).expanduser())
    env = os.environ.get(RIVM_ARCHIVE_ENV, "").strip()
    if env:
        candidates.append(Path(env).expanduser())
    candidates.append(PROJECT_ROOT / RIVM_ARCHIVE_REL)
    candidates.append(PROJECT_ROOT.parent / "envhealth_footprint"
                      / RIVM_ARCHIVE_REL)
    for candidate in candidates:
        if (candidate / "output" / "Table1.xlsx").exists():
            return candidate.resolve()
    raise FileNotFoundError(
        "the RIVM archive was not found; set "
        f"{RIVM_ARCHIVE_ENV} to the directory holding "
        f"output/Table1.xlsx (upstream {RIVM_UPSTREAM})"
        f". Looked in: {', '.join(str(c) for c in candidates)}")


def _source(workbook: str, sheet: str) -> str:
    """Provenance string for one archived sheet.

    Parameters
    ----------
    workbook : str
        Workbook file name, e.g. ``"ContributionAnalysis.xlsx"``.
    sheet : str
        Sheet name within it.

    Returns
    -------
    str
        The archive path, the sheet, and the upstream repository, in one field
        that travels with every row.
    """
    return (f"{RIVM_ARCHIVE_REL}/output/{workbook}#{sheet}"
            f" (upstream {RIVM_UPSTREAM})")


def _read_sheet(archive: Path, workbook: str, sheet: str) -> pd.DataFrame:
    """Read one archived sheet and normalise its index columns.

    Excel writes a pandas MultiIndex with the outer level blank on every row
    but the first of each group, so the outer level has to be carried down
    before the sheet can be used as a fact table. The unnamed row-number column
    pandas wrote on export is dropped.

    Parameters
    ----------
    archive : pathlib.Path
        Archive directory from :func:`rivm_archive_dir`.
    workbook : str
        Workbook file name.
    sheet : str
        Sheet name.

    Returns
    -------
    pandas.DataFrame
        The sheet, with gold column names and no blank-filled index cells.
    """
    frame = pd.read_excel(archive / "output" / workbook, sheet_name=sheet)
    frame = frame.loc[:, [c for c in frame.columns
                          if not str(c).startswith("Unnamed:")]]
    frame = frame.rename(columns=COLUMN_RENAME)
    value_cols = set(IMPACT_COLUMNS) | set(EXPENDITURE_COLUMNS) | {
        f"{c}/MEUR" for c in IMPACT_COLUMNS}
    index_cols = [c for c in frame.columns if c not in value_cols]
    if index_cols:
        frame[index_cols] = frame[index_cols].ffill()
    if "country_iso3" in frame.columns:
        frame["country_iso3"] = frame["country_iso3"].replace(ISO3_FIXES)
    return frame


def _melt(frame: pd.DataFrame, columns: dict[str, tuple[str, str]],
          source: str, *, per_meur: bool = False) -> pd.DataFrame:
    """Turn a sheet's wide impact columns into ``indicator``/``unit``/``value``.

    Parameters
    ----------
    frame : pandas.DataFrame
        Sheet as returned by :func:`_read_sheet`.
    columns : dict
        Wide column name -> ``(indicator, unit)``.
    source : str
        Provenance string from :func:`_source`, copied onto every row.
    per_meur : bool, optional
        When true the wide columns carry a ``/MEUR`` suffix and the unit
        becomes an intensity.

    Returns
    -------
    pandas.DataFrame
        Long format: the sheet's dimensions, then ``indicator``, ``unit``,
        ``value``, ``source``.
    """
    wide = {f"{name}/MEUR" if per_meur else name: meta
            for name, meta in columns.items()}
    present = [c for c in wide if c in frame.columns]
    dims = [c for c in frame.columns if c not in present]
    out = frame.melt(id_vars=dims, value_vars=present,
                     var_name="_column", value_name="value")
    out["indicator"] = out["_column"].map(lambda c: wide[c][0])
    out["unit"] = out["_column"].map(
        lambda c: f"{wide[c][1]} per M.EUR" if per_meur else wide[c][1])
    out = out.drop(columns="_column")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out["source"] = source
    return out[dims + ["indicator", "unit", "value", "source"]]


def _decorate(frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """Prefix the node columns and add the study-level dimensions.

    Parameters
    ----------
    frame : pandas.DataFrame
        Long table from :func:`_melt`.
    prefix : str
        ``"producing"`` for the hotspot (production) perspective,
        ``"purchased"`` for the contribution (consumption) perspective.

    Returns
    -------
    pandas.DataFrame
        With ``study``, ``consuming_country_iso3`` and ``reference_year``
        leading, and the node columns named as in the Danish gold tables.
    """
    out = frame.rename(columns={
        c: f"{prefix}_{c}" for c in
        ("country_iso3", "country_name", "world_region",
         "sector_code", "sector_name", "sector_group")
        if c in frame.columns})
    code_col = f"{prefix}_sector_code"
    if code_col in out.columns:
        codes = out[code_col].astype(str)
        # after the last node column, so the node reads as one block and the
        # flag that says whether the node is an EXIOBASE one follows it
        anchor = f"{prefix}_sector_group"
        after = out.columns.get_loc(anchor) if anchor in out.columns \
            else out.columns.get_loc(code_col)
        out.insert(after + 1, "component_type",
                   np.where(codes.isin(BOTTOM_UP_CODES),
                            "bottom-up item", "MRIO supply-chain node"))
        # gold convention: EXIOBASE codes without the A_ / C_ prefix. The
        # study's own bottom-up rows are not EXIOBASE sectors and keep the
        # B_ code that identifies them, which `component_type` also flags.
        out[code_col] = codes.str.replace(r"^[AC]_", "", regex=True)
    out.insert(0, "study", "steenmeijer_2022")
    out.insert(1, "consuming_country_iso3", "NLD")
    out.insert(2, "reference_year", NL_REFERENCE_YEAR)
    return out


def _assert_totals(long: pd.DataFrame, wide: pd.DataFrame,
                   columns: dict[str, tuple[str, str]], label: str,
                   *, per_meur: bool = False) -> int:
    """Assert the converted table reproduces the workbook's column totals.

    Parameters
    ----------
    long : pandas.DataFrame
        Converted long table, carrying ``indicator`` and ``value``.
    wide : pandas.DataFrame
        The sheet it was converted from.
    columns : dict
        The same wide-column mapping the conversion used.
    label : str
        Table name, used in the failure message.
    per_meur : bool, optional
        Whether the wide columns carry the ``/MEUR`` suffix.

    Returns
    -------
    int
        Number of columns checked.

    Raises
    ------
    AssertionError
        If any column total moved by more than 1e-9 relative.
    """
    checked = 0
    for name, (indicator, _unit) in columns.items():
        column = f"{name}/MEUR" if per_meur else name
        if column not in wide.columns:
            continue
        expected = float(pd.to_numeric(wide[column], errors="coerce").sum())
        got = float(long.loc[long["indicator"] == indicator, "value"].sum())
        tolerance = 1e-9 * max(abs(expected), 1.0)
        if not abs(got - expected) <= tolerance:
            raise AssertionError(
                f"{label}: column '{column}' totals {got!r} after conversion "
                f"but {expected!r} in the workbook "
                f"(difference {got - expected!r})")
        checked += 1
    return checked


#: One row per table the conversion writes: output file, workbook, sheet, the
#: perspective its node columns describe, and the wide-column family. Keeping
#: it declarative means a sheet cannot be converted without being named, and
#: the manifest and the readme list exactly what the loop wrote.
CONVERSIONS: tuple[dict[str, str], ...] = (
    dict(file="nl_contribution_by_purchased_node.csv",
         workbook="ContributionAnalysis.xlsx", sheet="full",
         prefix="purchased", family="impact"),
    dict(file="nl_contribution_by_purchased_product.csv",
         workbook="ContributionAnalysis.xlsx", sheet="allsec",
         prefix="purchased", family="impact"),
    dict(file="nl_contribution_by_sector_group.csv",
         workbook="ContributionAnalysis.xlsx", sheet="aggsec",
         prefix="purchased", family="impact"),
    dict(file="nl_hotspot_by_producing_node.csv",
         workbook="HotspotAnalysis.xlsx", sheet="full",
         prefix="producing", family="impact"),
    dict(file="nl_hotspot_by_producing_sector.csv",
         workbook="HotspotAnalysis.xlsx", sheet="allsec",
         prefix="producing", family="impact"),
    dict(file="nl_hotspot_by_sector_group.csv",
         workbook="HotspotAnalysis.xlsx", sheet="aggsec",
         prefix="producing", family="impact"),
    dict(file="nl_hotspot_by_sector_group_and_country.csv",
         workbook="HotspotAnalysis.xlsx", sheet="aggsec_aggreg",
         prefix="producing", family="impact"),
    dict(file="nl_hotspot_by_producing_country.csv",
         workbook="HotspotAnalysis.xlsx", sheet="allreg",
         prefix="producing", family="impact"),
    dict(file="nl_hotspot_by_world_region.csv",
         workbook="HotspotAnalysis.xlsx", sheet="aggreg",
         prefix="producing", family="impact"),
    dict(file="nl_expenditure_by_purchased_node.csv",
         workbook="ExpenditureVector.xlsx", sheet="full",
         prefix="purchased", family="expenditure"),
    dict(file="nl_expenditure_by_purchased_product.csv",
         workbook="ExpenditureVector.xlsx", sheet="allsec",
         prefix="purchased", family="expenditure"),
    dict(file="nl_expenditure_by_sector_group.csv",
         workbook="ExpenditureVector.xlsx", sheet="aggsec",
         prefix="purchased", family="expenditure"),
    dict(file="nl_expenditure_by_sector_group_and_country.csv",
         workbook="ExpenditureVector.xlsx", sheet="aggsec_aggreg",
         prefix="purchased", family="expenditure"),
    dict(file="nl_intensity_by_purchased_node.csv",
         workbook="Intensities.xlsx", sheet="full",
         prefix="purchased", family="intensity"),
    dict(file="nl_intensity_by_purchased_product.csv",
         workbook="Intensities.xlsx", sheet="allsec",
         prefix="purchased", family="intensity"),
    dict(file="nl_intensity_by_sector_group.csv",
         workbook="Intensities.xlsx", sheet="aggsec",
         prefix="purchased", family="intensity"),
    dict(file="nl_intensity_by_sector_group_and_country.csv",
         workbook="Intensities.xlsx", sheet="aggsec_aggreg",
         prefix="purchased", family="intensity"),
)


def _convert_sheet(archive: Path, spec: dict[str, str]) -> tuple[pd.DataFrame,
                                                                 int]:
    """Convert one archived sheet and assert its totals.

    Parameters
    ----------
    archive : pathlib.Path
        Archive directory.
    spec : dict
        One entry of :data:`CONVERSIONS`.

    Returns
    -------
    tuple
        ``(long_table, columns_checked)``.
    """
    wide = _read_sheet(archive, spec["workbook"], spec["sheet"])
    source = _source(spec["workbook"], spec["sheet"])
    if spec["family"] == "expenditure":
        columns = {name: (component, "M.EUR")
                   for name, component in EXPENDITURE_COLUMNS.items()}
        long = _melt(wide, columns, source)
        checked = _assert_totals(long, wide, columns, spec["file"])
        long = long.rename(columns={"indicator": "demand_component"})
        long["indicator"] = "expenditure"
    else:
        per_meur = spec["family"] == "intensity"
        long = _melt(wide, IMPACT_COLUMNS, source, per_meur=per_meur)
        checked = _assert_totals(long, wide, IMPACT_COLUMNS, spec["file"],
                                 per_meur=per_meur)
    long = _decorate(long, spec["prefix"])
    ordered = [c for c in long.columns
               if c not in ("indicator", "unit", "value", "source")]
    if "demand_component" in ordered:
        ordered.remove("demand_component")
        ordered.append("demand_component")
    return long[ordered + ["indicator", "unit", "value", "source"]], checked


# ---------------------------------------------------------------------------
# The three published figures, as data.
#
# The grouping rules below are the paper's, read off its own legends (p e954
# for figures 1 and 2, p e955 for figure 3) and checked segment by segment
# against the vector geometry of those figures. Two of them differ from the
# `agg_ind_fig` sheet of the archived classification workbook, and the
# difference is visible rather than arguable - see
# `docs/methods/replications.md`, section 13.
# ---------------------------------------------------------------------------

#: EXIOBASE aggregate sector -> figure 1 group. Everything unlisted is "Other".
FIG1_GROUPS: dict[str, str] = {
    "Chemical": "Pharmaceuticals and chemical products (scope 3)",
    "Electricity": "Heat and electricity (scope 2)",
    "Natural gas and gaseous fuels": "Heat and electricity (scope 2)",
    "Steam, hot water supply and water distribution":
        "Heat and electricity (scope 2)",
    "Operational impact": "Operational impacts (scope 1)",
    "Electrical, electronic and measuring equipment":
        "Medical and electrical equipment and machinery (scope 3)",
    "Services": "Services (scope 3)",
    "Food and catering": "Food and food services (scope 3)",
    "Private travel": "Individual travel (scope 3 and out-of-scope)",
}

#: Figure 1's legend, top to bottom, as printed on p e954.
FIG1_ORDER: tuple[str, ...] = (
    "Other (scope 3)",
    "Individual travel (scope 3 and out-of-scope)",
    "Food and food services (scope 3)",
    "Services (scope 3)",
    "Medical and electrical equipment and machinery (scope 3)",
    "Operational impacts (scope 1)",
    "Heat and electricity (scope 2)",
    "Pharmaceuticals and chemical products (scope 3)",
)

#: EXIOBASE aggregate sector -> figure 2 group. Everything unlisted is "Other".
FIG2_GROUPS: dict[str, str] = {
    "Electricity": "Electricity sector",
    "Chemical": "Pharmaceutical and chemical industry",
    "Coal and Petroleum": "Fossil fuel industry",
    "Natural gas and gaseous fuels": "Fossil fuel industry",
    "Food and catering": "Agricultural sector",
    "Minerals and Metals": "Mining of minerals and metals",
    "Operational impact": "Operational (direct) impacts",
}

#: Figure 2's legend, top to bottom, as printed on p e954.
FIG2_ORDER: tuple[str, ...] = (
    "Other",
    "Mining of minerals and metals",
    "Operational (direct) impacts",
    "Agricultural sector",
    "Fossil fuel industry",
    "Pharmaceutical and chemical industry",
    "Electricity sector",
)

#: EXIOBASE world region -> figure 3 group, in the paper's own wording.
FIG3_GROUPS: dict[str, str] = {
    "Netherlands": "Netherlands",
    "Asia and Pacific": "Asia-Pacific",
    "Europe": "Europe (excluding the Netherlands)",
    "Middle East": "Middle East",
    "America": "Americas",
    "Africa": "Africa",
}

#: Figure 3's legend, top to bottom, as printed on p e955.
FIG3_ORDER: tuple[str, ...] = (
    "Africa", "Americas", "Middle East",
    "Europe (excluding the Netherlands)", "Asia-Pacific", "Netherlands",
)

#: The published figures' own bar composition, read off the article rather than
#: recomputed.
#:
#: Figures 1-3 are vector graphics in the published PDF (pp e954-e955), so every
#: stacked segment is a filled rectangle with an exact height and an exact fill
#: colour. Dividing a segment's height by its bar's height gives the percentage
#: the figure actually draws, and the fill colour says which legend entry it
#: belongs to. This is the only machine-readable form of the published figures
#: that exists: the archived ``main.py`` records that the manuscript figures
#: were composed in a spreadsheet, and the archive ships no figure data file.
#:
#: Two caveats are visible in the numbers. A segment drawn at 0.091 % sits at
#: the composing spreadsheet's hairline minimum (0.12 pt on a 132 pt bar) and is
#: a drawing floor, not a value. And a segment whose value rounded to zero was
#: not drawn at all, so a legend entry can be missing from a bar.
#:
#: Source: Steenmeijer et al. (2022), figures 1 and 2 (p e954), figure 3
#: (p e955).
PUBLISHED_FIGURE_SHARES: dict[int, dict[str, dict[str, float]]] = {
    1: {
        "climate_change": {
            "Other (scope 3)": 12.213,
            "Individual travel (scope 3 and out-of-scope)": 5.267,
            "Food and food services (scope 3)": 5.832,
            "Services (scope 3)": 6.678,
            "Medical and electrical equipment and machinery (scope 3)": 7.619,
            "Operational impacts (scope 1)": 9.029,
            "Heat and electricity (scope 2)": 11.757,
            "Pharmaceuticals and chemical products (scope 3)": 41.606,
        },
        "material_extraction": {
            "Other (scope 3)": 9.955,
            "Individual travel (scope 3 and out-of-scope)": 0.093,
            "Food and food services (scope 3)": 1.505,
            "Services (scope 3)": 4.139,
            "Medical and electrical equipment and machinery (scope 3)": 4.139,
            "Heat and electricity (scope 2)": 0.470,
            "Pharmaceuticals and chemical products (scope 3)": 79.699,
        },
        "blue_water_consumption": {
            "Other (scope 3)": 3.841,
            "Individual travel (scope 3 and out-of-scope)": 0.094,
            "Food and food services (scope 3)": 23.891,
            "Services (scope 3)": 4.609,
            "Medical and electrical equipment and machinery (scope 3)": 3.010,
            "Heat and electricity (scope 2)": 1.411,
            "Pharmaceuticals and chemical products (scope 3)": 63.144,
        },
        "land_use": {
            "Other (scope 3)": 7.698,
            "Individual travel (scope 3 and out-of-scope)": 0.094,
            "Food and food services (scope 3)": 23.703,
            "Services (scope 3)": 5.455,
            "Medical and electrical equipment and machinery (scope 3)": 2.634,
            "Heat and electricity (scope 2)": 0.471,
            "Pharmaceuticals and chemical products (scope 3)": 60.040,
        },
        "waste_generation": {
            "Other (scope 3)": 13.153,
            "Food and food services (scope 3)": 13.357,
            "Services (scope 3)": 5.832,
            "Medical and electrical equipment and machinery (scope 3)": 7.807,
            "Operational impacts (scope 1)": 3.951,
            "Heat and electricity (scope 2)": 1.599,
            "Pharmaceuticals and chemical products (scope 3)": 54.302,
        },
    },
    2: {
        "climate_change": {
            "Other": 30.778,
            "Mining of minerals and metals": 2.453,
            "Operational (direct) impacts": 10.174,
            "Agricultural sector": 11.265,
            "Fossil fuel industry": 11.718,
            "Pharmaceutical and chemical industry": 12.082,
            "Electricity sector": 21.529,
        },
        "material_extraction": {
            "Other": 1.164,
            "Mining of minerals and metals": 97.837,
            "Agricultural sector": 0.273,
            "Fossil fuel industry": 0.091,
            "Pharmaceutical and chemical industry": 0.636,
            "Electricity sector": 0.091,
        },
        "blue_water_consumption": {
            "Other": 5.161,
            "Mining of minerals and metals": 0.545,
            "Agricultural sector": 88.753,
            "Fossil fuel industry": 0.091,
            "Pharmaceutical and chemical industry": 3.724,
            "Electricity sector": 1.817,
        },
        "land_use": {
            "Other": 1.710,
            "Mining of minerals and metals": 0.092,
            "Agricultural sector": 98.200,
            "Fossil fuel industry": 0.091,
            "Pharmaceutical and chemical industry": 0.091,
            "Electricity sector": 0.091,
        },
        "waste_generation": {
            "Other": 8.250,
            "Mining of minerals and metals": 50.871,
            "Operational (direct) impacts": 3.997,
            "Agricultural sector": 29.796,
            "Fossil fuel industry": 0.818,
            "Pharmaceutical and chemical industry": 4.270,
            "Electricity sector": 1.999,
        },
    },
    3: {
        "climate_change": {
            "Africa": 4.406,
            "Americas": 9.326,
            "Middle East": 10.754,
            "Europe (excluding the Netherlands)": 13.323,
            "Asia-Pacific": 25.028,
            "Netherlands": 37.164,
        },
        "material_extraction": {
            "Africa": 1.360,
            "Americas": 5.139,
            "Middle East": 10.087,
            "Europe (excluding the Netherlands)": 6.186,
            "Asia-Pacific": 74.799,
            "Netherlands": 2.429,
        },
        "blue_water_consumption": {
            "Africa": 7.261,
            "Americas": 14.179,
            "Middle East": 28.929,
            "Europe (excluding the Netherlands)": 6.661,
            "Asia-Pacific": 40.444,
            "Netherlands": 2.524,
        },
        "land_use": {
            "Africa": 16.396,
            "Americas": 28.835,
            "Middle East": 2.855,
            "Europe (excluding the Netherlands)": 22.649,
            "Asia-Pacific": 28.264,
            "Netherlands": 1.002,
        },
        "waste_generation": {
            "Africa": 5.928,
            "Americas": 37.209,
            "Middle East": 5.234,
            "Europe (excluding the Netherlands)": 12.181,
            "Asia-Pacific": 25.504,
            "Netherlands": 13.944,
        },
    },
}

#: Height a segment is drawn at when its value is below what the composing
#: spreadsheet could render, as a percentage of the bar.
FIGURE_HAIRLINE_PCT: float = 0.091

#: Which article page each figure is printed on.
FIGURE_PAGE: dict[int, str] = {1: "e954", 2: "e954", 3: "e955"}


def _published_vs_archive(figures: dict[int, pd.DataFrame]) -> pd.DataFrame:
    """Compare what the article draws with what the archived workbooks hold.

    Parameters
    ----------
    figures : dict
        Figure number -> the share table :func:`_figure_shares` produced from
        the archive.

    Returns
    -------
    pandas.DataFrame
        One row per figure, indicator and legend entry, carrying both shares
        and their difference in percentage points.

    Raises
    ------
    ValueError
        If a published bar's segments do not sum to 100 %.
    """
    rows: list[dict[str, Any]] = []
    for figure, panels in PUBLISHED_FIGURE_SHARES.items():
        archive = figures[figure].set_index(["indicator", "figure_group"])
        for indicator, segments in panels.items():
            total = sum(segments.values())
            # A bar's segments sum to 100 % up to the rounding of the measured
            # heights, plus whatever each hairline segment was inflated by:
            # a hairline can overstate its share by at most its own height.
            hairlines = sum(np.isclose(v, FIGURE_HAIRLINE_PCT, atol=0.002)
                            for v in segments.values())
            slack = 0.2 + hairlines * FIGURE_HAIRLINE_PCT
            if not np.isclose(total, 100.0, atol=slack):
                raise ValueError(f"figure {figure} {indicator}: published "
                                 f"segments sum to {total}, not 100 "
                                 f"(tolerance {slack:.3f})")
            for group, published in segments.items():
                key = (indicator, group)
                held = float(archive.loc[key, "share_pct"]) \
                    if key in archive.index else 0.0
                rows.append(dict(
                    figure=figure, article_page=FIGURE_PAGE[figure],
                    indicator=indicator, figure_group=group,
                    published_share_pct=published,
                    archive_share_pct=held,
                    difference_pp=held - published,
                    note="drawn at the composing spreadsheet's hairline "
                         "minimum, so the published value is a floor rather "
                         "than a measurement"
                         if np.isclose(published, FIGURE_HAIRLINE_PCT,
                                       atol=0.002) else "",
                    source=f"Steenmeijer et al. (2022) figure {figure}, "
                           f"p {FIGURE_PAGE[figure]}, segment geometry of the "
                           f"published vector figure; archive share from "
                           f"{RIVM_UPSTREAM}"))
    return pd.DataFrame(rows)


def _figure_shares(long: pd.DataFrame, key: str, groups: dict[str, str],
                   order: tuple[str, ...], *, other: str | None,
                   distribute_undistributed: bool) -> pd.DataFrame:
    """Group one long table into a figure's stacked-bar shares.

    Parameters
    ----------
    long : pandas.DataFrame
        Node-level long table carrying ``indicator``, ``unit``, ``value``, the
        grouping column ``key``, and ``*_sector_code``.
    key : str
        Column the groups are read from.
    groups : dict
        Value of ``key`` -> figure group.
    order : tuple of str
        The legend, top to bottom.
    other : str or None
        Group name unmapped values fall into; ``None`` means every value must
        map, and an unmapped one is an error.
    distribute_undistributed : bool
        Whether to drop the study's undistributed private-travel rows from the
        base, which is what "proportionally distributed among all groups"
        (figure 2) and "among all regions" (figure 3) amounts to.

    Returns
    -------
    pandas.DataFrame
        ``indicator``, ``unit``, ``figure_group``, ``legend_position``,
        ``value``, ``share_pct``.

    Raises
    ------
    ValueError
        If a value of ``key`` has no group and ``other`` is ``None``, or if any
        indicator's shares do not sum to 100.
    """
    frame = long.copy()
    code_col = next(c for c in frame.columns if c.endswith("sector_code"))
    if distribute_undistributed:
        frame = frame[frame[code_col] != UNDISTRIBUTED_CODE]
    frame["figure_group"] = frame[key].map(groups)
    if other is None:
        missing = sorted(frame.loc[frame["figure_group"].isna(), key].unique())
        if missing:
            raise ValueError(f"no figure group for {key}: {missing}")
    else:
        frame["figure_group"] = frame["figure_group"].fillna(other)
    out = (frame.groupby(["indicator", "unit", "figure_group"],
                         as_index=False)["value"].sum())
    out["share_pct"] = 100 * out["value"] / out.groupby(
        "indicator")["value"].transform("sum")
    out["legend_position"] = out["figure_group"].map(
        {name: i + 1 for i, name in enumerate(order)})
    if out["legend_position"].isna().any():
        raise ValueError(f"groups outside the legend: "
                         f"{sorted(set(out.figure_group) - set(order))}")
    totals = out.groupby("indicator")["share_pct"].sum()
    if not np.allclose(totals.to_numpy(), 100.0, atol=1e-9):
        raise ValueError(f"figure shares do not sum to 100: {totals.to_dict()}")
    return out.sort_values(["indicator", "legend_position"])[
        ["indicator", "unit", "figure_group", "legend_position", "value",
         "share_pct"]]


def convert_rivm_outputs(archive_dir: str | os.PathLike[str] | None = None,
                         out_dir: str | os.PathLike[str] | None = None,
                         ) -> pd.DataFrame:
    """Convert every sheet of every RIVM output workbook into gold CSVs.

    Every impact column of every sheet is melted into ``indicator`` / ``unit``
    / ``value``, given the Danish gold layer's dimension names, and written
    with a ``source`` column naming the archived workbook, the sheet and the
    upstream repository. Each written table's column totals are asserted back
    against the workbook before it is written, so a conversion cannot publish a
    number the archive does not hold.

    Parameters
    ----------
    archive_dir : str or os.PathLike, optional
        Archive location; see :func:`rivm_archive_dir`.
    out_dir : str or os.PathLike, optional
        Where to write. Defaults to the Steenmeijer gold folder.

    Returns
    -------
    pandas.DataFrame
        One row per written file: ``file``, ``rows``, ``columns_checked``,
        ``source``.

    Raises
    ------
    AssertionError
        If any converted column total differs from the workbook's.
    """
    archive = rivm_archive_dir(archive_dir)
    target = Path(out_dir) if out_dir is not None \
        else Path(str(OUTPUT_DIR)) / FOLDER
    target.mkdir(parents=True, exist_ok=True)

    written: list[dict[str, Any]] = []
    tables: dict[str, pd.DataFrame] = {}
    for spec in CONVERSIONS:
        long, checked = _convert_sheet(archive, spec)
        long.to_csv(target / spec["file"], index=False)
        tables[spec["file"]] = long
        written.append(dict(file=spec["file"], rows=len(long),
                            columns_checked=checked,
                            source=_source(spec["workbook"], spec["sheet"])))

    # ---- the two summary tables, transposed into long format --------------
    for name, workbook, dimension in (
            ("nl_table_01.csv", "Table1.xlsx", "table_row"),
            ("nl_table_s05.csv", "TableS5.xlsx", "indicator")):
        wide = pd.read_excel(archive / "output" / workbook)
        wide = wide.rename(columns={wide.columns[0]: dimension})
        source = _source(workbook, "Sheet1")
        if workbook == "Table1.xlsx":
            columns = dict(IMPACT_COLUMNS)
            columns["Expenditure (MEUR)"] = ("expenditure", "M.EUR")
            long = _melt(wide, columns, source)
            checked = _assert_totals(long, wide, columns, name)
        else:
            # TableS5 is transposed relative to the other sheets: its rows are
            # the impact categories and its columns are the three quantities,
            # so the impact-column vocabulary is applied to the row labels.
            long = wide.melt(id_vars=[dimension],
                             value_vars=[c for c in wide.columns
                                         if c != dimension],
                             var_name="quantity", value_name="value")
            label = long.pop(dimension)
            long["unit"] = [
                "%" if "share" in str(q).lower()
                else IMPACT_COLUMNS.get(str(row), ("", ""))[1]
                for q, row in zip(long["quantity"], label)]
            long["indicator"] = [IMPACT_COLUMNS.get(str(row), ("", ""))[0]
                                 for row in label]
            long["source"] = source
            checked = 0
            for column in [c for c in wide.columns if c != dimension]:
                expected = float(wide[column].sum())
                got = float(long.loc[long["quantity"] == column,
                                     "value"].sum())
                if not abs(got - expected) <= 1e-9 * max(abs(expected), 1.0):
                    raise AssertionError(
                        f"{name}: column '{column}' totals {got!r} after "
                        f"conversion but {expected!r} in the workbook")
                checked += 1
            long = long[["indicator", "quantity", "unit", "value", "source"]]
        long.insert(0, "study", "steenmeijer_2022")
        long.insert(1, "consuming_country_iso3", "NLD")
        long.insert(2, "reference_year", NL_REFERENCE_YEAR)
        long.to_csv(target / name, index=False)
        written.append(dict(file=name, rows=len(long),
                            columns_checked=checked, source=source))

    # ---- the three figures ------------------------------------------------
    contribution = tables["nl_contribution_by_purchased_node.csv"]
    hotspot = tables["nl_hotspot_by_producing_node.csv"]
    figures = (
        ("nl_figure1_contribution_groups.csv", contribution,
         "purchased_sector_group", FIG1_GROUPS, FIG1_ORDER,
         "Other (scope 3)", False),
        ("nl_figure2_hotspot_sector_groups.csv", hotspot,
         "producing_sector_group", FIG2_GROUPS, FIG2_ORDER, "Other", True),
        ("nl_figure3_hotspot_world_regions.csv", hotspot,
         "producing_world_region", FIG3_GROUPS, FIG3_ORDER, None, True),
    )
    built: dict[int, pd.DataFrame] = {}
    for number, (name, long, key, groups, order, other, distribute) in \
            enumerate(figures, start=1):
        shares = _figure_shares(long, key, groups, order, other=other,
                                distribute_undistributed=distribute)
        built[number] = shares
        shares = shares.copy()
        shares.insert(0, "study", "steenmeijer_2022")
        shares.insert(1, "consuming_country_iso3", "NLD")
        shares.insert(2, "reference_year", NL_REFERENCE_YEAR)
        shares.insert(3, "figure", number)
        shares["source"] = long["source"].iloc[0]
        shares.to_csv(target / name, index=False)
        written.append(dict(file=name, rows=len(shares),
                            columns_checked=len(IMPACT_COLUMNS),
                            source=shares["source"].iloc[0]))

    comparison = _published_vs_archive(built)
    comparison.insert(0, "study", "steenmeijer_2022")
    comparison.insert(1, "consuming_country_iso3", "NLD")
    comparison.insert(2, "reference_year", NL_REFERENCE_YEAR)
    comparison.to_csv(target / "nl_published_figure_shares.csv", index=False)
    written.append(dict(file="nl_published_figure_shares.csv",
                        rows=len(comparison),
                        columns_checked=len(PUBLISHED_FIGURE_SHARES) * 5,
                        source="Steenmeijer et al. (2022) figures 1-3, "
                               "pp e954-e955"))

    return pd.DataFrame(written)


def _load_components() -> pd.DataFrame:
    """Read the Danish footprint by demand component and indicator.

    Returns
    -------
    pandas.DataFrame
        Indexed by ``demand_component`` with one column per indicator, in the
        indicator's own unit.
    """
    path = os.path.join(str(OUTPUT_DIR), "00_core_footprint",
                        "footprint_by_purchased_product.csv")
    frame = pd.read_csv(path)
    return frame.pivot_table(index="demand_component", columns="indicator",
                             values="value", aggfunc="sum")


def _load_bottom_up() -> dict[str, float]:
    """Read the Danish bottom-up climate components, in kt CO2-equivalent.

    The three bottom-up rows of the template table have no counterpart in the
    MRIO component file, and the operational (scope 1) component belongs inside
    the health-care services row, as it does in the Dutch table.

    Returns
    -------
    dict
        Keys ``"operational"``, ``"anaesthetic"``, ``"pmdi"`` and ``"travel"``;
        travel is commuting plus patient and visitor travel, matching the Dutch
        "Private travel" row.

    Raises
    ------
    RuntimeError
        If an expected component is absent, rather than silently returning zero.
    """
    path = os.path.join(str(OUTPUT_DIR), *eriksen_folder().split("/"),
                        "scopes_summary.csv")
    frame = pd.read_csv(path).set_index("Component")["kt_CO2eq"]
    wanted = {
        "operational": "Scope 1 direct (DRIVHUS, excl. medical N2O)",
        "anaesthetic": "  + Anaesthetic gases (bottom-up)",
        "pmdi": "  + pMDI (bottom-up, use phase)",
        "commute": "  + Commute (bottom-up)",
        "patient_visitor": "Outside protocol (patient/visitor travel)",
    }
    missing = [label for label in wanted.values() if label not in frame.index]
    if missing:
        raise RuntimeError(f"scopes_summary.csv is missing: {missing}")
    values = {key: float(frame[label]) for key, label in wanted.items()}
    values["travel"] = values.pop("commute") + values.pop("patient_visitor")
    return values


def _load_national() -> pd.DataFrame:
    """Read the Danish national totals and the health-care share of each."""
    path = os.path.join(str(OUTPUT_DIR), "00_core_footprint",
                        "national_totals_summary.csv")
    return pd.read_csv(path).set_index("indicator")


def main() -> None:
    """Build and write the Denmark-versus-Netherlands comparison tables."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)

    try:
        converted = convert_rivm_outputs(out_dir=out_dir)
    except FileNotFoundError as exc:
        print(f"Dutch archive not converted: {exc}")
    else:
        print(f"Converted {len(converted)} Dutch tables from the RIVM "
              f"archive, {int(converted['columns_checked'].sum())} column "
              f"totals asserted against the workbooks.")

    components = _load_components()
    national = _load_national()
    bottom_up = _load_bottom_up()
    dk_population = DK_POPULATION[ANALYSIS_YEAR]

    component_map = {
        "Health-care services": "healthcare_services",
        "Pharmaceuticals and chemical products": "pharmaceuticals",
        "Medical appliances": "medical_appliances",
    }

    rows: list[dict[str, Any]] = []
    for row_name, published in NL_TABLE.items():
        for indicator, unit in INDICATOR_UNIT.items():
            nl_value = published.get(indicator, np.nan)
            key = component_map.get(row_name)
            if key is not None and key in components.index \
                    and indicator in components.columns:
                dk_value = float(components.loc[key, indicator])
                # the Dutch "Health-care services" row carries the sector's own
                # operational emissions; ours are added from national accounts
                if key == "healthcare_services" \
                        and indicator == "climate_change":
                    dk_value += bottom_up["operational"]
            elif row_name == "Release of anaesthetic gases":
                dk_value = bottom_up["anaesthetic"] \
                    if indicator == "climate_change" else np.nan
            elif row_name == "Release of pMDI propellants":
                dk_value = bottom_up["pmdi"] \
                    if indicator == "climate_change" else np.nan
            elif row_name == "Private travel":
                dk_value = bottom_up["travel"] \
                    if indicator == "climate_change" else np.nan
            elif row_name == "Total":
                dk_value = float(components[indicator].sum())
                if indicator == "climate_change":
                    dk_value += (bottom_up["operational"]
                                 + bottom_up["anaesthetic"]
                                 + bottom_up["pmdi"] + bottom_up["travel"])
            else:
                dk_value = np.nan
            rows.append(dict(
                table_row=row_name, indicator=indicator, unit=unit,
                netherlands_2016=nl_value, denmark_2022=dk_value,
                netherlands_per_capita=nl_value / NL_POPULATION * 1e6
                if np.isfinite(nl_value) else np.nan,
                denmark_per_capita=dk_value / dk_population * 1e6
                if np.isfinite(dk_value) else np.nan,
                per_capita_unit=f"{unit} per million population",
                dk_as_pct_of_nl_per_capita=(
                    100.0 * (dk_value / dk_population)
                    / (nl_value / NL_POPULATION)
                    if np.isfinite(dk_value) and np.isfinite(nl_value)
                    and nl_value != 0 else np.nan),
                source_netherlands="Steenmeijer et al. 2022, Lancet Planet "
                                   "Health, main table (= RIVM 2022-0159 "
                                   "table 8)",
                source_denmark=MODEL_LABEL))
    table = pd.DataFrame(rows)
    table.insert(0, "analysis_year_denmark", ANALYSIS_YEAR)
    table.insert(1, "reference_year_netherlands", 2016)
    table.to_csv(os.path.join(out_dir, "template_table_dk_vs_nl.csv"),
                 index=False)

    share_rows: list[dict[str, Any]] = []
    for indicator, published in NL_NATIONAL.items():
        dk = national.loc[indicator] if indicator in national.index else None
        dk_share = float(dk["healthcare_share_pct"]) if dk is not None \
            else np.nan
        dk_national = float(dk["national_footprint"]) if dk is not None \
            else np.nan
        note = ""
        if indicator == "waste_generation":
            note = ("NOT on the same boundary: the Dutch figure sums all 19 "
                    "hybrid waste fractions, ours is filtered to the "
                    "statistical waste boundary. On the Dutch boundary the "
                    f"Danish health-care figure is "
                    f"{DK_WASTE_ALL_FRACTIONS_KT:,.0f} kt.")
        share_rows.append(dict(
            indicator=indicator, unit=published["unit"],
            netherlands_national=published["national"],
            netherlands_health_share_pct=published["share_pct"],
            denmark_national=dk_national,
            denmark_health_share_pct=dk_share,
            share_difference_pp=dk_share - published["share_pct"],
            comparability_note=note,
            source_netherlands="Steenmeijer et al. 2022 table S7 "
                               "(= RIVM 2022-0159 table 9)",
            source_denmark=MODEL_LABEL))
    shares = pd.DataFrame(share_rows)
    shares.to_csv(os.path.join(out_dir, "national_shares_dk_vs_nl.csv"),
                  index=False)

    pd.set_option("display.width", 200)
    climate = table[table.indicator == "climate_change"]
    print("Template table, climate change (kt CO2eq):")
    print(climate[["table_row", "netherlands_2016", "denmark_2022",
                   "dk_as_pct_of_nl_per_capita"]]
          .to_string(index=False, max_colwidth=40))
    print("\nHealth-care share of the national footprint:")
    print(shares[["indicator", "netherlands_health_share_pct",
                  "denmark_health_share_pct", "share_difference_pp"]]
          .to_string(index=False))
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
