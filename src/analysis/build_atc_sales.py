# -*- coding: utf-8 -*-
"""Give the Danish medicines register named columns, as a silver product.

The register arrives from medstat.dk as ``<year>_atc_code_data.txt``: 1.8
million lines, semicolon separated, latin-1, **no header row**. Bronze keeps it
exactly that way, because bronze is the source as obtained and a file with
columns silently renamed is a file nobody can check against the provider. But a
positional read is also how a study gets a unit wrong by three orders of
magnitude, so the named form has to exist somewhere: it exists here, in silver.

What is and is not named
------------------------
Six of the fourteen fields have a meaning this repository can demonstrate:
positions 1 to 6, which are the register's key, and position 11, the volume,
which is verified against the values :mod:`analysis.main_2025` carries in
``DK_ANAESTHETIC_LITRES``. The rest keep positional names. Inventing a plausible
name for a column whose content has not been established is worse than leaving
the gap visible, because the invented name is what the next reader will trust.

The unit trap
-------------
Position 11 is the register's "volume in 1.000 units", and *unit* means the
product's own unit. For ATC **N01AB**, the volatile anaesthetics, every marketed
product is an inhalation liquid, so the unit is millilitres and the field is
**litres**. :data:`N01AB_LITRES_EXPECTED` pins the six values the study depends
on, and :func:`verify_anaesthetic_volumes` fails the build if a re-downloaded
register does not reproduce them.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.build_atc_sales``
"""

from __future__ import annotations

import sys

import pandas as pd

from paths import BRONZE_DIR, SILVER_DK_MEDICINES_REGISTER_DIR

#: Where the register is cached, and the name pattern it is cached under.
REGISTER_DIR = BRONZE_DIR / "dk_medicines_register"
REGISTER_NAME = "{year}_atc_code_data.txt"

#: The silver product this module writes. Silver mirrors bronze by provenance,
#: so the named-column form of the register sits under the silver folder named
#: for the bronze folder it derives from:
#: :data:`paths.SILVER_DK_MEDICINES_REGISTER_DIR`. That constant is spelled out
#: at both use sites rather than aliased to a short local name, because the
#: short name a silver writer would reach for is the one this code base reserves
#: for the gold results root, and audit check C17 reads that name to decide
#: whether a module writes gold.
OUTPUT_NAME = "dk_atc_sales_{year}.csv"

#: Years the study reads.
YEARS: tuple[str, ...] = ("2016", "2019", "2022")

#: The register is latin-1, not UTF-8: Danish product names carry ae, oe and aa.
ENCODING = "latin-1"

#: Field separator, and the number of fields on every line.
SEPARATOR = ";"
N_FIELDS = 14

#: Column names, in file order. Positions 7 to 10, 12 and 13 keep positional
#: names on purpose: their content could not be established from the file or
#: from anything in this repository, and this study reads none of them. See
#: ``data/bronze/dk_medicines_register/readme.md``. The fourteenth field is
#: always empty - an artefact of the trailing separator - and is dropped here,
#: which is the one conformance this module performs beyond naming.
COLUMNS: tuple[str, ...] = (
    "atc",
    "year",
    "sector",
    "region",
    "sex",
    "age_group",
    "field_07",
    "field_08",
    "field_09",
    "field_10",
    "volume_thousand_units",
    "field_12",
    "field_13",
    "_trailing_empty",
)

#: The slice the study reads: all sectors, whole country, both sexes, all ages.
STUDY_SLICE: dict[str, str] = {"sector": "2", "region": "0", "sex": "A",
                              "age_group": "A"}

#: Litres of liquid agent sold, per year and ATC code. These are the six numbers
#: the anaesthetic term of the footprint rests on. They are asserted rather than
#: read into the study, because a register revision that moved the volume field
#: would otherwise pass silently and change a published number.
N01AB_LITRES_EXPECTED: dict[str, dict[str, float]] = {
    "2016": {"N01AB06": 30.0, "N01AB07": 478.0, "N01AB08": 3228.0},
    "2019": {"N01AB06": 17.0, "N01AB07": 400.0, "N01AB08": 2714.0},
    "2022": {"N01AB06": 15.0, "N01AB07": 181.0, "N01AB08": 2400.0},
}

#: ATC code to agent name, for the verification message.
N01AB_AGENTS: dict[str, str] = {"N01AB06": "isoflurane",
                                "N01AB07": "desflurane",
                                "N01AB08": "sevoflurane"}


def register_path(year: str) -> str:
    """Where the raw register for one year is cached.

    Parameters
    ----------
    year : str
        Reference year, e.g. ``"2022"``.

    Returns
    -------
    str
        Absolute path to ``<year>_atc_code_data.txt`` under bronze.
    """
    return str(REGISTER_DIR / REGISTER_NAME.format(year=year))


def output_path(year: str) -> str:
    """Where the named-column product for one year is written.

    Parameters
    ----------
    year : str
        Reference year, e.g. ``"2022"``.

    Returns
    -------
    str
        Absolute path to ``dk_atc_sales_<year>.csv`` under
        ``data/silver/dk_medicines_register/``.
    """
    return str(SILVER_DK_MEDICINES_REGISTER_DIR
               / OUTPUT_NAME.format(year=year))


def read_register(year: str) -> pd.DataFrame:
    """Read one year of the raw register and give its fields names.

    Every field is read as text. The register mixes numeric and non-numeric
    values in the same position - ``field_13`` carries both integers and the
    string ``">99"`` - so inferring dtypes would coerce the exceptional values
    to missing and hide them.

    Parameters
    ----------
    year : str
        Reference year, e.g. ``"2022"``.

    Returns
    -------
    pandas.DataFrame
        One row per register line, columns as in :data:`COLUMNS` with the
        trailing empty field dropped.

    Raises
    ------
    ValueError
        If a line does not carry exactly :data:`N_FIELDS` fields, or if the
        ``year`` column disagrees with the year asked for.
    """
    frame = pd.read_csv(register_path(year), sep=SEPARATOR, header=None,
                        names=list(COLUMNS), dtype=str, encoding=ENCODING,
                        keep_default_na=False, na_filter=False)
    if len(frame.columns) != N_FIELDS:
        raise ValueError(f"the {year} register parsed to "
                         f"{len(frame.columns)} fields, expected {N_FIELDS}")
    years = set(frame["year"].unique())
    if years != {year}:
        raise ValueError(f"the {year} register carries years {sorted(years)}, "
                         f"expected only {year!r}")
    return frame.drop(columns=["_trailing_empty"])


def study_slice(frame: pd.DataFrame) -> pd.DataFrame:
    """The rows the study reads: all sectors, whole country, both sexes.

    Parameters
    ----------
    frame : pandas.DataFrame
        A named register frame from :func:`read_register`.

    Returns
    -------
    pandas.DataFrame
        The subset matching :data:`STUDY_SLICE`, indexed by ``atc``.
    """
    mask = pd.Series(True, index=frame.index)
    for column, value in STUDY_SLICE.items():
        mask &= frame[column] == value
    return frame[mask].set_index("atc")


def verify_anaesthetic_volumes(frame: pd.DataFrame, year: str) -> list[str]:
    """Check the six volatile-anaesthetic volumes against the pinned values.

    Parameters
    ----------
    frame : pandas.DataFrame
        A named register frame from :func:`read_register`.
    year : str
        Reference year, e.g. ``"2022"``.

    Returns
    -------
    list of str
        One line per agent, stating the litres read and whether it matches.

    Raises
    ------
    AssertionError
        If any agent's volume differs from :data:`N01AB_LITRES_EXPECTED`. The
        anaesthetic term of the published footprint is computed from these
        numbers, so a drift is a defect, not a warning.
    """
    rows = study_slice(frame)
    lines: list[str] = []
    wrong: list[str] = []
    for code, expected in N01AB_LITRES_EXPECTED[year].items():
        if code not in rows.index:
            wrong.append(f"{code} ({N01AB_AGENTS[code]}) is absent")
            continue
        read = float(rows.loc[code, "volume_thousand_units"])
        lines.append(f"    {code} {N01AB_AGENTS[code]:<12s} "
                     f"{read:>8,.0f} L  expected {expected:>8,.0f} L")
        if read != expected:
            wrong.append(f"{code} ({N01AB_AGENTS[code]}) reads {read}, "
                         f"expected {expected}")
    if wrong:
        raise AssertionError(
            f"the {year} register does not reproduce the volatile-anaesthetic "
            f"volumes this study is built on: {'; '.join(wrong)}. Either the "
            f"register has been revised or the volume field has moved. Do not "
            f"publish a footprint from a register this has not validated.")
    return lines


def build(year: str) -> tuple[str, int]:
    """Write the named-column product for one year.

    Parameters
    ----------
    year : str
        Reference year, e.g. ``"2022"``.

    Returns
    -------
    tuple of (str, int)
        The path written, and the number of rows in it.
    """
    frame = read_register(year)
    for line in verify_anaesthetic_volumes(frame, year):
        print(line)
    SILVER_DK_MEDICINES_REGISTER_DIR.mkdir(parents=True, exist_ok=True)
    path = output_path(year)
    frame.to_csv(path, index=False, encoding="utf-8")
    return path, len(frame)


def main(years: tuple[str, ...] = YEARS) -> None:
    """Build the named-column product for every year of the study.

    Parameters
    ----------
    years : tuple of str, optional
        Reference years. Defaults to :data:`YEARS`.
    """
    for year in years:
        print(f"{year}: reading {register_path(year)}")
        path, rows = build(year)
        print(f"    written -> {path}  ({rows:,} rows)")


if __name__ == "__main__":
    main(tuple(sys.argv[1:]) or YEARS)
