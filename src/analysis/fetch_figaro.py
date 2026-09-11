# -*- coding: utf-8 -*-
"""Retrieve the Eurostat FIGARO extracts this study benchmarks against.

A bronze-layer fetcher. It is run when a year is added to the benchmark, not on
every build, and it writes nothing but files under
``data/bronze/eurostat_figaro/``.

Which dataset holds a year
--------------------------
Eurostat splits the FIGARO supply and use tables into four-year blocks, each its
own dataset code, so the dataset to query is a function of the year:

============  ===========  ===========  ===========
years         supply       use          industry IOT
============  ===========  ===========  ===========
2010-2013     ``_s1``      ``_u1``      ``_ii1``
2014-2017     ``_s2``      ``_u2``      ``_ii2``
2018-2021     ``_s3``      ``_u3``      ``_ii3``
2022-         ``_s4``      ``_u4``      ``_ii4``
============  ===========  ===========  ===========

That split is the reason a year looks unavailable when it is not: a query for
2016 against ``naio_10_fcp_u4`` returns nothing at all rather than an error, and
the four codes are easy to read as four editions of one table.
:func:`dataset_for` does the arithmetic so no caller repeats it.

The footprint datasets are not split: ``env_ac_ghgfp`` and ``env_ac_co2fp`` each
cover 2010 to 2023 in one dataset.

Why not 2025
------------
The FIGARO edition released in year $n$ ends at $n-2$, so the 2026 edition ends
at 2024 and 2025 first appears in the 2027 edition. The one FIGARO application
that already reaches 2025 is ``env_ac_rmefd``, the material footprint by final
use, which is not a supply, use or input-output table.

Output
------
One long CSV per query, columns in the order the existing extracts use, named so
the file says what was asked for: dataset family, the destination or geography
filter, and the years.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any, Iterator, Sequence

from paths import BRONZE_DIR

#: Eurostat dissemination API.
API = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data")

#: Where the extracts land.
BRONZE_FIGARO_DIR = BRONZE_DIR / "eurostat_figaro"

#: The four-year blocks the FIGARO tables are split into, newest last. The final
#: block is open-ended: Eurostat extends it rather than opening a fifth.
FIGARO_BLOCKS: tuple[tuple[int, int, str], ...] = (
    (2010, 2013, "1"),
    (2014, 2017, "2"),
    (2018, 2021, "3"),
    (2022, 9999, "4"),
)

#: Dataset stem per FIGARO table.
FIGARO_TABLES = {"supply": "naio_10_fcp_s",
                 "use": "naio_10_fcp_u",
                 "iot_industry": "naio_10_fcp_ii",
                 "iot_product": "naio_10_fcp_ip"}

#: Column order of the written CSVs, per table family. Matches the extracts
#: already in bronze, so a consumer that globs the folder sees one schema.
COLUMN_ORDER = {
    "use": ("time", "c_dest", "c_orig", "prd_ava", "ind_use", "unit", "value"),
    "supply": ("time", "geo", "nace_r2", "cpa2_1", "unit", "value"),
    "footprint": ("time", "c_dest", "c_orig", "nace_r2", "na_item", "unit",
                  "value"),
}


def dataset_for(table: str, year: int) -> str:
    """Return the Eurostat dataset code holding one year of one FIGARO table.

    Parameters
    ----------
    table : str
        A key of :data:`FIGARO_TABLES`: ``"supply"``, ``"use"``,
        ``"iot_industry"`` or ``"iot_product"``.
    year : int
        Reference year.

    Returns
    -------
    str
        The dataset code, e.g. ``"naio_10_fcp_u2"`` for the use table in 2016.

    Raises
    ------
    ValueError
        If the table is unknown or the year precedes the first block.
    """
    if table not in FIGARO_TABLES:
        raise ValueError(f"unknown FIGARO table {table!r}; "
                         f"known: {sorted(FIGARO_TABLES)}")
    for first, last, suffix in FIGARO_BLOCKS:
        if first <= year <= last:
            return f"{FIGARO_TABLES[table]}{suffix}"
    raise ValueError(f"{year} precedes the first FIGARO block "
                     f"({FIGARO_BLOCKS[0][0]})")


def fetch(dataset: str,
          **filters: str | Sequence[str]) -> dict[str, Any]:
    """Retrieve one Eurostat JSON-stat cube.

    Parameters
    ----------
    dataset : str
        Eurostat dataset code.
    **filters : str or sequence of str
        Dimension filters passed through as query parameters. A sequence
        becomes a repeated parameter, which is how the dissemination API takes
        several values for one dimension: ``time=["2016", "2019"]`` asks for two
        years and nothing between them.

    Returns
    -------
    dict
        The parsed JSON-stat cube.

    Raises
    ------
    RuntimeError
        If the request fails, the response is not JSON, or the API returns an
        error object -- which it does with HTTP 200 for a filter that selects
        nothing, so the error has to be read out of the body.
    """
    parts: list[str] = []
    for key, value in filters.items():
        values = [value] if isinstance(value, str) else list(value)
        parts.extend(f"{key}={item}" for item in values)
    url = f"{API}/{dataset}?format=JSON&" + "&".join(parts)
    out = subprocess.run(["curl", "-s", "--max-time", "300", url],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"curl failed for {dataset}: {out.stderr[:200]}")
    try:
        cube = json.loads(out.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{dataset}: non-JSON response ({exc})") from exc
    if "error" in cube:
        raise RuntimeError(f"{dataset} {filters}: {cube['error']}")
    if not cube.get("value"):
        raise RuntimeError(f"{dataset} {filters}: no observations returned; "
                           "check the year is inside this dataset's block")
    return cube


def records(cube: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Flatten a JSON-stat cube into one record per observation.

    JSON-stat stores values against a flat index into the cartesian product of
    the dimensions, row-major. This unravels it.

    Parameters
    ----------
    cube : dict
        A parsed JSON-stat cube.

    Yields
    ------
    dict
        One record per observation: a key per dimension holding that
        dimension's code, plus ``"value"``.
    """
    ids: list[str] = cube["id"]
    size: list[int] = cube["size"]
    codes = {k: list(cube["dimension"][k]["category"]["index"].keys())
             for k in ids}
    for flat, value in cube["value"].items():
        rest, position = int(flat), []
        for extent in reversed(size):
            position.append(rest % extent)
            rest //= extent
        position.reverse()
        rec = {name: codes[name][p] for name, p in zip(ids, position)}
        rec["value"] = value
        yield rec


def write_long_csv(cube: dict[str, Any], family: str, path: Path) -> int:
    """Write one cube to bronze as long CSV, in the folder's column order.

    Parameters
    ----------
    cube : dict
        A parsed JSON-stat cube.
    family : str
        A key of :data:`COLUMN_ORDER`: ``"use"``, ``"supply"`` or
        ``"footprint"``.
    path : pathlib.Path
        File to write.

    Returns
    -------
    int
        Rows written, excluding the header.

    Raises
    ------
    ValueError
        If the cube carries a dimension the family's column order does not
        name. Writing it would silently drop a key and turn the file into an
        unlabelled aggregate.
    """
    columns = COLUMN_ORDER[family]
    extra = [d for d in cube["id"] if d not in columns and d != "freq"]
    if extra:
        raise ValueError(f"{path.name}: cube carries {extra}, which "
                         f"{family!r}'s column order does not name")
    path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        for rec in records(cube):
            writer.writerow([rec.get(c, "") for c in columns])
            written += 1
    return written


def fetch_use(years: Sequence[int], destination: str = "DK") -> list[Path]:
    """Retrieve the FIGARO use table for one destination, one file per year.

    One file per year because each year may sit in a different dataset block and
    because a single year is already 221,214 rows for one destination. The
    consolidated series with a ``year`` column is the silver product.

    Parameters
    ----------
    years : sequence of int
        Reference years.
    destination : str, optional
        ``c_dest`` filter. Default ``"DK"``.

    Returns
    -------
    list of pathlib.Path
        Files written.
    """
    written = []
    for year in years:
        dataset = dataset_for("use", year)
        cube = fetch(dataset, c_dest=destination, time=str(year))
        path = (BRONZE_FIGARO_DIR
                / f"figaro2026_use_{destination}dest_{year}.csv")
        rows = write_long_csv(cube, "use", path)
        print(f"{dataset} c_dest={destination} time={year} -> "
              f"{path.name}, {rows:,} rows")
        written.append(path)
    return written


def fetch_supply(years: Sequence[int], geography: str = "DK") -> list[Path]:
    """Retrieve the FIGARO supply table, one file per four-year block.

    The supply table is three orders of magnitude smaller than the use table --
    a whole block for one country is under a megabyte -- so a block is fetched
    whole and the file is named for the years it holds.

    Parameters
    ----------
    years : sequence of int
        Reference years. Years inside one block produce one file.
    geography : str, optional
        ``geo`` filter. Default ``"DK"``.

    Returns
    -------
    list of pathlib.Path
        Files written, one per distinct block the years fall in.
    """
    blocks = {dataset_for("supply", year) for year in years}
    written = []
    for dataset in sorted(blocks):
        cube = fetch(dataset, geo=geography)
        held = sorted(cube["dimension"]["time"]["category"]["index"])
        span = f"{held[0]}-{held[-1]}" if len(held) > 1 else held[0]
        path = (BRONZE_FIGARO_DIR
                / f"figaro2026_supply_{geography}_{span}.csv")
        rows = write_long_csv(cube, "supply", path)
        print(f"{dataset} geo={geography} -> {path.name}, {rows:,} rows")
        written.append(path)
    return written


def fetch_footprints(years: Sequence[int], destination: str = "DK",
                     datasets: Sequence[str] = ("env_ac_ghgfp",
                                                "env_ac_co2fp")
                     ) -> list[Path]:
    """Retrieve the FIGARO-based footprint accounts for a span of years.

    These datasets are not split into blocks, so one query covers the whole span
    and the file is named for it.

    Parameters
    ----------
    years : sequence of int
        Reference years; the query asks for each explicitly.
    destination : str, optional
        ``c_dest`` filter. Default ``"DK"``.
    datasets : sequence of str, optional
        Dataset codes. Default the greenhouse-gas and carbon-dioxide footprints.

    Returns
    -------
    list of pathlib.Path
        Files written, one per dataset.
    """
    span = f"{min(years)}-{max(years)}" if len(set(years)) > 1 else str(
        years[0])
    written = []
    for dataset in datasets:
        cube = fetch(dataset, c_dest=destination,
                     time=[str(year) for year in sorted(set(years))])
        path = (BRONZE_FIGARO_DIR
                / f"{dataset}_{destination}dest_{span}.csv")
        rows = write_long_csv(cube, "footprint", path)
        print(f"{dataset} c_dest={destination} {span} -> "
              f"{path.name}, {rows:,} rows")
        written.append(path)
    return written


def main() -> None:
    """Fetch the extracts named on the command line."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--years", type=int, nargs="+", required=True,
                        help="reference years to retrieve")
    parser.add_argument("--tables", nargs="+",
                        choices=("use", "supply", "footprints"),
                        default=("use", "supply", "footprints"),
                        help="which extracts to retrieve")
    arguments = parser.parse_args()

    if "use" in arguments.tables:
        fetch_use(arguments.years)
    if "supply" in arguments.tables:
        fetch_supply(arguments.years)
    if "footprints" in arguments.tables:
        fetch_footprints(arguments.years)


if __name__ == "__main__":
    main()
