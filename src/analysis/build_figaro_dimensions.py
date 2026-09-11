# -*- coding: utf-8 -*-
"""Give the Eurostat FIGARO fact tables the dimension tables they ship without.

Motivation
----------
Every file in ``data/bronze/eurostat_figaro/`` is a long fact table: one row per
cell, keys in code columns, one ``value``. The dissemination API serves the keys
and nothing else, so a reader holding ``figaro2026_use_DKdest_2022.csv`` sees

.. code-block:: text

   2022,DK,DOM,CPA_C21,Q86,MIO_EUR,1234.5

and cannot tell without leaving the repository that ``CPA_C21`` is
pharmaceutical products and ``Q86`` is human health activities. That is the
star-schema defect the folder had: fact tables with no dimension tables. This
module supplies them, from Eurostat's own SDMX codelists, so no label in this
study is a guess about what a code means.

Three of the distinctions it carries are not cosmetic:

**``ind_use`` is not one classification.** The FIGARO use table's columns are
industries *and* final-demand categories in the same code column: 64 NACE rev.2
activities followed by ``P3_S13``, ``P3_S14``, ``P3_S15``, ``P51G`` and
``P5M``. Summing the column without separating them adds final demand to
intermediate use. The ``entry_type`` column separates them.

**``prd_ava`` is not one classification either.** Its rows are 64 CPA products
followed by the primary-input rows of the use table -- ``D1`` compensation of
employees, ``B2A3G`` gross operating surplus, the two net-tax rows -- and the
two residents/non-residents adjustments. Summing products and value added
double counts output.

**Not every non-country code in ``c_orig`` is an aggregate.** The column carries
49 single countries and five codes that are not one of them, and they behave in
three different ways, which was checked against the tables rather than read off
the labels. ``WORLD``, ``EU27_2020`` and ``EXT_EU27_2020`` are true aggregates
that overlap their members: summing ``value`` over every origin of a footprint
extract counts some emissions three times. ``WRL_REST`` is the residual for the
countries FIGARO does not resolve individually, so it must be *kept* in a sum,
not dropped with the aggregates. ``DOM``, whose Eurostat label is "Domestic
country", is not a duplicate of ``DK``: in the use table it appears on 414 rows,
every one of them a primary input or an adjustment -- ``D1``, ``B2A3G``,
``D21X31``, ``D29X39``, ``OP_RES``, ``OP_NRES`` -- and on no product row at all.
It is the origin code for rows that have no country of origin. Typing the three
apart is what lets a consumer sum the column correctly; a reader who dropped
everything that was not an ISO code would lose the rest of the world, and one
who dropped nothing would treble-count the EU.

**And ``nace_r2`` mixes NACE levels.** The footprint extracts carry 21 section
letters, 55 divisions, households' direct emissions, a ``G-U_X_H`` aggregate
spanning sections, and two different totals, all in one column -- ``Q`` beside
``Q86`` and ``Q87_Q88``. The supply table's ``nace_r2`` is flat by contrast: 64
divisions and nothing else. ``nace_level`` carries the level, taken from the
shape of the code, which for NACE is definitional rather than inferred: a
section is a single letter, a division is a letter with digits. Which of those
levels adds up to what is arithmetic, not classification, so it is measured
rather than asserted -- see ``data/silver/eurostat_figaro/readme.md``, where the
section sum is shown to reproduce the ``TOTAL`` row exactly and the divisions are
shown *not* to, because nine of the 21 sections are published with no division
detail at all. A reader who summed the division rows as though they partitioned
the economy would be 37 % low.

Why the labels are fetched per column, not per classification
-------------------------------------------------------------
Eurostat publishes one codelist per *dimension*, not per classification, and the
spellings differ between dimensions of the same classification. The footprint
extracts write food manufacturing as ``C10-C12`` in ``nace_r2``; the use table
writes the same activity as ``C10-12`` in ``ind_use``. Sixteen of the 69
``ind_use`` codes are absent from ``NACE_R2`` for this reason, and three of them
(``P3_S14``, ``P3_S15``, ``P5M``) are absent from every other codelist as well.
Resolving each fact column against the codelist of the same name resolves all of
them exactly, with no spelling repair and no inference from ESA 2010 semantics.
:data:`FACT_COLUMN_CODELIST` is that pairing, and :func:`build_dimensions`
fails rather than emit a row whose label it had to invent.

Provenance
----------
Codelists are cached in bronze as retrieved, one TSV per codelist, so a rebuild
is offline and a reader can diff the label this table carries against the file
it was read from. ``--refresh`` re-fetches them.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import urllib.request
from pathlib import Path

import pandas as pd

from paths import BRONZE_DIR, SILVER_EUROSTAT_FIGARO_DIR

#: Eurostat SDMX 2.1 codelist endpoint. ``{codelist}`` is the codelist id.
CODELIST_URL = ("https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1"
                "/codelist/ESTAT/{codelist}?format=TSV&compressed=false")

#: Where the retrieved codelists are cached, and where the fact tables are.
BRONZE_FIGARO_DIR = BRONZE_DIR / "eurostat_figaro"

#: Output.
DIMENSIONS_CSV = "figaro_dimensions.csv"

#: Every code column of the bronze fact tables, paired with the Eurostat
#: codelist of the same name. The pairing is the point: see the module
#: docstring on why ``ind_use`` must not be resolved against ``NACE_R2``.
FACT_COLUMN_CODELIST: dict[str, str] = {
    "c_dest": "C_DEST",
    "c_orig": "C_ORIG",
    "geo": "GEO",
    "prd_ava": "PRD_AVA",
    "cpa2_1": "CPA2_1",
    "ind_use": "IND_USE",
    "nace_r2": "NACE_R2",
    "na_item": "NA_ITEM",
    "unit": "UNIT",
}

#: The ``ind_use`` codes that are final-demand columns of the use table rather
#: than industries. ``P85`` is *not* among them: it is NACE P85, education.
FINAL_DEMAND_IND_USE = frozenset({"P3_S13", "P3_S14", "P3_S15", "P51G", "P5M"})

#: The ``prd_ava`` codes that are primary-input rows of the use table.
VALUE_ADDED_PRD_AVA = frozenset({"B2A3G", "D1", "D21X31", "D29X39"})

#: The ``prd_ava`` codes that are the residents/non-residents adjustments.
ADJUSTMENT_PRD_AVA = frozenset({"OP_RES", "OP_NRES"})

#: Country codes that aggregate other country codes of the same column, so that
#: summing the column with them in it double counts.
COUNTRY_AGGREGATES = frozenset({"EU27_2020", "EXT_EU27_2020", "WORLD"})

#: The residual for countries FIGARO does not resolve individually. It overlaps
#: nothing and belongs in a sum over origins.
COUNTRY_RESIDUAL = frozenset({"WRL_REST"})

#: The origin code carried by rows that have no country of origin: in the use
#: table ``DOM`` appears only on the primary-input and adjustment rows.
COUNTRY_NO_ORIGIN = frozenset({"DOM"})

#: Codes that are a total over the rest of their own column.
TOTAL_CODES = frozenset({"TOTAL", "TOT"})


def codelist_cache(codelist: str) -> Path:
    """Return the bronze cache path for one codelist.

    Parameters
    ----------
    codelist : str
        Eurostat codelist id, e.g. ``"IND_USE"``.

    Returns
    -------
    pathlib.Path
        Path the codelist is cached at, lowercase, inside the bronze FIGARO
        folder so the labels sit beside the fact tables they decode.
    """
    return BRONZE_FIGARO_DIR / f"codelist_{codelist.lower()}.tsv"


def fetch_codelist(codelist: str, refresh: bool = False) -> dict[str, str]:
    """Read one Eurostat codelist, downloading it if it is not cached.

    Parameters
    ----------
    codelist : str
        Eurostat codelist id.
    refresh : bool, optional
        Re-download even when the cache exists. Default ``False``, so a rebuild
        is offline and reproduces the labels the cache holds.

    Returns
    -------
    dict of str to str
        Code to label. Codes are unique within a codelist.

    Raises
    ------
    ValueError
        If the response is empty, which the API returns for an unknown
        codelist id rather than an HTTP error.
    """
    cache = codelist_cache(codelist)
    if refresh or not cache.exists():
        url = CODELIST_URL.format(codelist=codelist)
        with urllib.request.urlopen(url, timeout=120) as response:
            payload = response.read().decode("utf-8")
        if not payload.strip():
            raise ValueError(f"{codelist}: empty codelist from {url}")
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(payload, encoding="utf-8")
    labels: dict[str, str] = {}
    for line in cache.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0]:
            labels[parts[0]] = parts[1].strip()
    if not labels:
        raise ValueError(f"{codelist}: no code-label pairs in {cache}")
    return labels


def scan_fact_tables() -> dict[str, dict[str, list[str]]]:
    """Collect every code used in every code column of the bronze fact tables.

    Returns
    -------
    dict of str to dict of str to list of str
        Fact column to code to the sorted file names the code appears in. Only
        columns named in :data:`FACT_COLUMN_CODELIST` are scanned; ``time`` and
        ``value`` are not code columns.

    Raises
    ------
    FileNotFoundError
        If the bronze FIGARO folder holds no CSV fact table.
    """
    tables = sorted(BRONZE_FIGARO_DIR.glob("*.csv"))
    if not tables:
        raise FileNotFoundError(f"no fact table in {BRONZE_FIGARO_DIR}")
    seen: dict[str, dict[str, set[str]]] = {}
    for table in tables:
        frame = pd.read_csv(table, dtype=str)
        for column in frame.columns:
            if column not in FACT_COLUMN_CODELIST:
                continue
            codes = frame[column].dropna().unique()
            for code in codes:
                seen.setdefault(column, {}).setdefault(code, set()).add(
                    table.name)
    return {column: {code: sorted(files) for code, files in codes.items()}
            for column, codes in seen.items()}


def nace_level(code: str) -> str:
    """Return which level of NACE rev.2 one ``nace_r2`` code sits at.

    Taken from the shape of the code, which for NACE is definitional: a section
    is a single letter A to U, a division is a letter followed by digits, and a
    range of divisions is written by FIGARO with a hyphen or an underscore
    inside one section. The three codes that are not NACE at all -- households'
    direct emissions and the two totals -- are enumerated.

    Nothing about additivity is claimed here. Which levels sum to which total is
    measured in the folder readme, because the extracts publish division detail
    for only 12 of the 21 sections and no rule about code shape could know that.

    Parameters
    ----------
    code : str
        A code from the ``nace_r2`` column.

    Returns
    -------
    str
        ``"section"``, ``"division"``, ``"cross_section"``, ``"household"``,
        ``"all_activities"`` or ``"all_activities_and_households"``.
    """
    if code == "TOTAL":
        return "all_activities"
    if code == "TOTAL_HH":
        return "all_activities_and_households"
    if code == "HH":
        return "household"
    if re.fullmatch(r"[A-U]", code):
        return "section"
    if re.fullmatch(r"[A-U]\d\d?([-_][A-U]?\d\d?)?", code):
        return "division"
    return "cross_section"


def entry_type(column: str, code: str) -> str:
    """Classify one code by what kind of thing it names.

    The classification is by enumerated set, never by code prefix: ``P85`` in
    ``ind_use`` starts with ``P`` and is an industry, while ``P51G`` in the same
    column is final demand, so a prefix rule gets education wrong.

    Parameters
    ----------
    column : str
        Fact-table column the code appears in.
    code : str
        The code.

    Returns
    -------
    str
        One of ``"total"``, ``"country"``, ``"country_aggregate"``,
        ``"country_residual"``, ``"no_origin"``, ``"unit"``, ``"final_demand"``,
        ``"value_added"``, ``"adjustment"``, ``"product"``, ``"household"`` or
        ``"industry"``. Only ``country_aggregate`` and ``total`` overlap other
        rows of the same column and have to come out of a sum;
        ``country_residual`` has to stay in. Among industries the overlap is in
        ``nace_level`` instead, because there it is a matter of level rather
        than of kind.
    """
    if code in TOTAL_CODES:
        return "total"
    if column in ("c_orig", "c_dest", "geo"):
        if code in COUNTRY_AGGREGATES:
            return "country_aggregate"
        if code in COUNTRY_RESIDUAL:
            return "country_residual"
        if code in COUNTRY_NO_ORIGIN:
            return "no_origin"
        return "country"
    if column == "unit":
        return "unit"
    if column == "na_item":
        return "final_demand"
    if column == "ind_use" and code in FINAL_DEMAND_IND_USE:
        return "final_demand"
    if column == "prd_ava":
        if code in VALUE_ADDED_PRD_AVA:
            return "value_added"
        if code in ADJUSTMENT_PRD_AVA:
            return "adjustment"
    if column in ("prd_ava", "cpa2_1"):
        return "product"
    if column == "nace_r2":
        level = nace_level(code)
        if level.startswith("all_activities"):
            return "total"
        if level == "household":
            return "household"
    return "industry"


def build_dimensions(refresh: bool = False) -> pd.DataFrame:
    """Build the dimension table for the FIGARO fact tables held in bronze.

    One row per (fact column, code) pair actually used by a bronze fact table,
    so the table is a dimension of *these* extracts rather than a copy of
    Eurostat's 5,580-code CPA register.

    Parameters
    ----------
    refresh : bool, optional
        Re-download the codelists. Default ``False``.

    Returns
    -------
    pandas.DataFrame
        Columns ``fact_column``, ``code``, ``label``, ``entry_type``,
        ``nace_level``, ``codelist``, ``bronze_files``.

    Raises
    ------
    ValueError
        If any code used by a fact table has no label in the codelist paired
        with its column. The table is a dimension table or it is nothing: a
        missing label must stop the build, not ship as an empty string.
    """
    used = scan_fact_tables()
    unknown = sorted(set(used) - set(FACT_COLUMN_CODELIST))
    if unknown:
        raise ValueError(f"code columns with no codelist paired: {unknown}")
    rows: list[dict[str, object]] = []
    unresolved: list[str] = []
    for column in sorted(used):
        codelist = FACT_COLUMN_CODELIST[column]
        labels = fetch_codelist(codelist, refresh=refresh)
        for code, files in sorted(used[column].items()):
            label = labels.get(code)
            if label is None:
                unresolved.append(f"{column}={code} (not in {codelist})")
                continue
            rows.append({"fact_column": column,
                         "code": code,
                         "label": label,
                         "entry_type": entry_type(column, code),
                         "nace_level": (nace_level(code)
                                        if column == "nace_r2" else ""),
                         "codelist": codelist,
                         "bronze_files": ";".join(files)})
    if unresolved:
        raise ValueError("codes with no Eurostat label:\n  "
                         + "\n  ".join(unresolved))
    return pd.DataFrame(rows)


def load_dimensions() -> pd.DataFrame:
    """Read the dimension table a previous build wrote.

    Returns
    -------
    pandas.DataFrame
        The table, as written by :func:`main`.

    Raises
    ------
    FileNotFoundError
        If it has not been built. The message names the command that builds it,
        because a consumer that failed here has a missing silver product rather
        than a bug.
    """
    path = SILVER_EUROSTAT_FIGARO_DIR / DIMENSIONS_CSV
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not built; run\n"
            "  PYTHONPATH=src .venv/bin/python -m "
            "analysis.build_figaro_dimensions")
    return pd.read_csv(path, dtype=str)


def code_labels(fact_column: str) -> dict[str, str]:
    """Return code to label for one fact column.

    Parameters
    ----------
    fact_column : str
        A column of the bronze fact tables, e.g. ``"c_orig"``.

    Returns
    -------
    dict of str to str
        Code to Eurostat label. Empty if the column carries no code in any
        bronze fact table.
    """
    frame = load_dimensions()
    rows = frame[frame.fact_column == fact_column]
    return dict(zip(rows.code, rows.label))


def aggregate_codes(fact_column: str) -> set[str]:
    """Return the codes of one fact column that overlap other codes in it.

    A consumer that sums a code column must exclude these or double count. For
    ``nace_r2`` the overlap is by level, so the section letters are *not*
    returned -- they are the additive set there, and the divisions under them
    are the incomplete one; see the folder readme.

    Parameters
    ----------
    fact_column : str
        A column of the bronze fact tables.

    Returns
    -------
    set of str
        Codes typed ``country_aggregate`` or ``total`` in that column.
    """
    frame = load_dimensions()
    rows = frame[(frame.fact_column == fact_column)
                 & frame.entry_type.isin(["country_aggregate", "total"])]
    return set(rows.code)


def main() -> None:
    """Write the dimension table to silver and report what it covers."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true",
                        help="re-download the Eurostat codelists")
    arguments = parser.parse_args()

    dimensions = build_dimensions(refresh=arguments.refresh)
    SILVER_EUROSTAT_FIGARO_DIR.mkdir(parents=True, exist_ok=True)
    out = SILVER_EUROSTAT_FIGARO_DIR / DIMENSIONS_CSV
    dimensions.to_csv(out, index=False)

    print(f"FIGARO dimension table, built {dt.date.today().isoformat()}")
    print(f"{len(dimensions)} rows, {dimensions.fact_column.nunique()} "
          f"fact columns\n")
    summary = (dimensions.groupby(["fact_column", "codelist", "entry_type"])
               .size().rename("codes").reset_index())
    print(summary.to_string(index=False))
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
