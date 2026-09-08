# -*- coding: utf-8 -*-
"""Statistics Denmark's environmental accounts at full 117-industry resolution.

Why this exists
---------------
The SNAC coupling needs the Danish satellite :math:`S^d` on the *same*
classification as the Danish IO tables, so that a domestic direct-emission
vector can be swapped in for the EXIOBASE Danish block industry by industry.
The repository previously carried only a five-code health-sector extract
(``data/bronze/dk_direct_emissions_drivhus.csv``: ``VQ``, ``VQA``, ``V860010``,
``V870000``, ``V880000``), which is enough to set one Scope 1 number and
nothing else. This module downloads the whole account.

Statistics Denmark publishes three environmental-economic account families on
the DB07 **117-grouping** - the six-digit industry codes, of which there are
exactly 117, identical in all three tables and identical to the ``BRANCHE``
six-digit set of the waste tables already used by
:mod:`analysis.waste_domestic_dst`:

============  ==========================================  ===================
StatBank id   content                                     unit
============  ==========================================  ===================
``DRIVHUS``   Greenhouse Gas Accounts (in CO2 equiv.)     1,000 t CO2e
``MRU1``      Air Emission Accounts                       per substance
``ENE2HA``    Energy Account in GJ (detailed table)       GJ
============  ==========================================  ===================

All three follow national-accounts residence principles, which is what makes
them substitutable into an IO model at all, and all three are the **direct**
(territorial, Scope 1) account: ``DRIVHUS`` was verified against ``DRIVHUS2``
to equal that table's ``OPPRINCIP=DIR`` slice. The sibling ``FORDEL`` and
``BRUTTO`` principles redistribute emissions from electricity and district heat
onto the consuming industry; they must **not** be used here, because the IO
model derives that redistribution endogenously through the Leontief inverse and
would otherwise count it twice.

What this module does not give you
----------------------------------
``DRIVHUS`` is published rounded to whole 1,000 tonnes, so a small industry can
carry a several-per-cent rounding error and an industry below 500 t CO2e
reports as zero. ``MRU1`` publishes the non-CO2 substances in tonnes and is the
more precise source for them. Neither table is a full EXIOBASE-style satellite:
there are no water, land or material-extraction rows here, and the waste rows
live in the ``AFF*`` family instead (see :mod:`analysis.waste_domestic_dst`).

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.fetch_dst_accounts``
"""

from __future__ import annotations

import datetime as dt
import re
from typing import Any, Iterable, Sequence

import pandas as pd
import requests

from paths import BRONZE_DIR

API_ROOT = "https://api.statbank.dk/v1"
TIMEOUT_S = 240

#: Reference years of the study. Both are fetched; they are not a time series
#: (see :mod:`analysis.year_comparison`).
YEARS: tuple[str, ...] = ("2019", "2022")

OUTPUT_NAME = "dst_emission_accounts_by_industry.csv"

#: Existing health-sector extract, used only to validate the download.
VALIDATION_SOURCE = "dk_direct_emissions_drivhus.csv"

#: Six-digit DB07 industry codes are the 117-grouping. Five-digit codes are the
#: 69-grouping and bare letters the sections; both are aggregates of these and
#: are deliberately excluded so the file stays exhaustive and non-overlapping.
_SIX_DIGIT = re.compile(r"^V\d{6}$")

#: DB07 section and sub-section aggregates, reconstructed from the 117-grouping
#: for validation against the existing extract. Q = QA + QB.
SECTION_MEMBERS: dict[str, tuple[str, ...]] = {
    "VQA": ("V860010", "V860020"),
    "VQ": ("V860010", "V860020", "V870000", "V880000"),
}

#: ``DRIVHUS`` emission types. ``GHGEXBIO`` and ``GHGBIO`` are CO2-equivalent
#: totals, not separate gases: ``GHGEXBIO = CO2UBIO + N2O + CH4 + FGAS`` and
#: ``GHGBIO = GHGEXBIO + CO2BIO``. Do not sum the column blindly.
DRIVHUS_SUBSTANCES: tuple[str, ...] = (
    "GHGEXBIO", "GHGBIO", "CO2UBIO", "CO2BIO", "N2O", "CH4", "FGAS",
)
DRIVHUS_COMPONENTS: tuple[str, ...] = ("CO2UBIO", "N2O", "CH4", "FGAS")

#: ``MRU1`` exposes its substances as bare ordinals. Map them onto the same
#: mnemonics the rest of the codebase uses, and keep the published unit, which
#: differs by substance (1,000 t for CO2, t for the rest, t CO2e for the
#: fluorinated gases).
MRU1_SUBSTANCES: dict[str, str] = {
    "1": "CO2INCBIO", "3": "CO2EXCBIO", "2": "CO2BIO", "4": "SO2", "5": "NOX",
    "6": "CO", "7": "NH3", "8": "N2O", "9": "CH4", "10": "NMVOC",
    "11": "PM10", "12": "PM25", "13": "SF6", "14": "PFC", "15": "HFC",
}

#: ``ENE2HA`` carrier aggregates. ``ETOT`` is the total; the eight groups below
#: partition it exactly (verified per industry), so either the total or the
#: groups may be used, never both.
ENE2HA_TOTAL = "ETOT"
ENE2HA_GROUPS: tuple[str, ...] = (
    "EROOL", "EOIL", "ENGI", "ENGF", "EKUKO", "EAFFA", "EVE", "EKONV",
)

ACCOUNTS: dict[str, str] = {
    "DRIVHUS": "greenhouse_gas",
    "MRU1": "air_emission",
    "ENE2HA": "energy_use",
}


class StatBankError(RuntimeError):
    """A StatBank request failed, or returned something unusable.

    Raised before anything is written, so a failed download can never leave a
    half-populated or silently stale Bronze file behind.
    """


def _post(endpoint: str, body: dict[str, Any]) -> requests.Response:
    """POST to a StatBank endpoint and fail loudly.

    Parameters
    ----------
    endpoint
        Endpoint name, e.g. ``"data"`` or ``"tableinfo"``.
    body
        Request body, serialised as JSON.

    Returns
    -------
    requests.Response
        The successful response.

    Raises
    ------
    StatBankError
        On any transport error, or any status other than 200.
    """

    url = f"{API_ROOT}/{endpoint}"
    try:
        response = requests.post(url, json=body, timeout=TIMEOUT_S)
    except requests.RequestException as exc:  # network, DNS, TLS, timeout
        raise StatBankError(
            f"POST {url} table={body.get('table')!r} failed: {exc}") from exc
    if response.status_code != 200:
        raise StatBankError(
            f"POST {url} table={body.get('table')!r} returned HTTP "
            f"{response.status_code}: {response.text[:400]}")
    return response


def table_metadata(table: str) -> dict[str, Any]:
    """Return the ``tableinfo`` payload for one StatBank table.

    Parameters
    ----------
    table
        StatBank table identifier, e.g. ``"DRIVHUS"``.

    Returns
    -------
    dict
        Parsed ``tableinfo`` JSON.
    """

    response = _post("tableinfo", {"table": table, "format": "JSON",
                                   "lang": "en"})
    try:
        return response.json()
    except ValueError as exc:
        raise StatBankError(f"tableinfo {table}: response is not JSON") from exc


def industry_variable(meta: dict[str, Any]) -> dict[str, Any]:
    """Find the variable that carries the DB07 industry classification.

    The industry dimension is named inconsistently across the account families
    (``BRANCHE`` in ``DRIVHUS`` and ``MRU1``, ``ANVEND`` in ``ENE2HA``), so it
    is identified by content - the variable holding six-digit codes - rather
    than by name.

    Parameters
    ----------
    meta
        A ``tableinfo`` payload.

    Returns
    -------
    dict
        The variable definition.

    Raises
    ------
    StatBankError
        If no variable exposes six-digit industry codes.
    """

    for variable in meta["variables"]:
        codes = [v["id"] for v in variable["values"]]
        if any(_SIX_DIGIT.match(code) for code in codes):
            return variable
    raise StatBankError(
        f"table {meta.get('id')!r} exposes no six-digit industry codes; "
        "it is not published on the DB07 117-grouping")


def industries_117(meta: dict[str, Any]) -> dict[str, str]:
    """Extract the 117-grouping as ``{code: name}`` from a ``tableinfo`` payload.

    Parameters
    ----------
    meta
        A ``tableinfo`` payload.

    Returns
    -------
    dict
        Industry code (``V`` plus six digits) to industry name, with the
        redundant numeric prefix stripped from the published label.

    Raises
    ------
    StatBankError
        If the table does not carry exactly 117 six-digit codes.
    """

    variable = industry_variable(meta)
    out: dict[str, str] = {}
    for value in variable["values"]:
        code = value["id"]
        if not _SIX_DIGIT.match(code):
            continue
        out[code] = re.sub(r"^\d{6}\s+", "", value["text"]).strip()
    if len(out) != 117:
        raise StatBankError(
            f"table {meta.get('id')!r} carries {len(out)} six-digit industry "
            "codes, not 117; refusing to call it the 117-grouping")
    return out


def substance_labels(meta: dict[str, Any], variable_id: str) -> dict[str, str]:
    """Return ``{code: label}`` for one non-industry variable.

    Parameters
    ----------
    meta
        A ``tableinfo`` payload.
    variable_id
        Variable identifier, e.g. ``"EMTYPE8"``.

    Returns
    -------
    dict
        Value code to published label.
    """

    for variable in meta["variables"]:
        if variable["id"] == variable_id:
            return {v["id"]: v["text"] for v in variable["values"]}
    raise StatBankError(
        f"table {meta.get('id')!r} has no variable {variable_id!r}")


def _split_unit(label: str) -> tuple[str, str]:
    """Split a published label into name and trailing parenthesised unit.

    ``MRU1`` carries its unit inside the label, e.g.
    ``"Nitrogen oxides (NOx), (tonnes)"``. Labels without a trailing unit come
    back unchanged with an empty unit.

    Parameters
    ----------
    label
        Published value label.

    Returns
    -------
    tuple of str
        ``(name, unit)``.
    """

    match = re.search(r",\s*\(([^()]*)\)\s*$", label)
    if not match:
        return label.strip(), ""
    return label[: match.start()].strip(), match.group(1).strip()


def fetch_slice(table: str, industry_var: str, industries: Sequence[str],
                second_var: str, second_values: Sequence[str],
                years: Iterable[str]) -> pd.DataFrame:
    """Download one table slice as codes, without name mangling.

    ``valuePresentation="Code"`` is requested so the industry code arrives in
    its own column rather than glued to the label, which is what
    :mod:`analysis.waste_domestic_dst` has to unpick with ``split()``.

    Parameters
    ----------
    table
        StatBank table identifier.
    industry_var
        Name of the industry variable in this table.
    industries
        Industry codes to request.
    second_var
        Name of the substance or energy-carrier variable.
    second_values
        Codes to request from that variable.
    years
        Reference years.

    Returns
    -------
    pandas.DataFrame
        Columns ``industry_code``, ``substance``, ``year``, ``value``.

    Raises
    ------
    StatBankError
        If the request fails, or returns an unexpected shape or row count.
    """

    years = list(years)
    body = {
        "table": table, "format": "CSV", "lang": "en",
        "valuePresentation": "Code", "delimiter": ";",
        "variables": [
            {"code": industry_var, "values": list(industries)},
            {"code": second_var, "values": list(second_values)},
            {"code": "Tid", "values": years},
        ],
    }
    text = _post("data", body).content.decode("utf-8-sig")
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        raise StatBankError(f"data {table}: empty response ({text[:200]!r})")
    header = lines[0].split(";")
    if len(header) != 4:
        raise StatBankError(
            f"data {table}: expected 4 columns, got {header!r}")

    records: list[tuple[str, str, str, float]] = []
    for line in lines[1:]:
        parts = line.split(";")
        if len(parts) != 4:
            raise StatBankError(f"data {table}: malformed row {line!r}")
        industry, substance, year, raw = (p.strip() for p in parts)
        # StatBank marks a suppressed or not-available cell with dots.
        value = float("nan") if raw in {"", "..", ".", "...", "-"} else float(raw)
        records.append((industry, substance, year, value))

    expected = len(industries) * len(second_values) * len(years)
    if len(records) != expected:
        raise StatBankError(
            f"data {table}: got {len(records)} rows, expected {expected}")
    return pd.DataFrame(records,
                        columns=["industry_code", "substance", "year", "value"])


def _stamp(table: str, meta: dict[str, Any], retrieved: str) -> str:
    """Build the ``source`` string for one table.

    Parameters
    ----------
    table
        StatBank table identifier.
    meta
        Its ``tableinfo`` payload, read for the last-update timestamp.
    retrieved
        ISO date of retrieval.

    Returns
    -------
    str
        Provenance string naming the table, its vintage and the retrieval date.
    """

    updated = str(meta.get("updated", ""))[:10]
    return (f"Statistics Denmark StatBank {table} (table updated {updated}; "
            f"retrieved {retrieved} via {API_ROOT}/data)")


def fetch_all(years: Sequence[str] = YEARS,
              retrieved: str | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Download the three account families at 117-industry resolution.

    Parameters
    ----------
    years
        Reference years to fetch.
    retrieved
        ISO retrieval date to stamp. Defaults to today.

    Returns
    -------
    tuple
        The long-format frame, and a dict of per-table metadata for reporting.

    Raises
    ------
    StatBankError
        If any request fails or any table is not on the 117-grouping. Nothing
        is written by this function, so a failure leaves the Bronze file as it
        was.
    """

    retrieved = retrieved or dt.date.today().isoformat()
    requests_plan = [
        ("DRIVHUS", "EMTYPE8", list(DRIVHUS_SUBSTANCES)),
        ("MRU1", "EMTYPE8", list(MRU1_SUBSTANCES)),
        ("ENE2HA", "ENERGI1", [ENE2HA_TOTAL, *ENE2HA_GROUPS]),
    ]

    frames: list[pd.DataFrame] = []
    report: dict[str, Any] = {}
    for table, second_var, second_values in requests_plan:
        meta = table_metadata(table)
        industry_var = industry_variable(meta)
        names = industries_117(meta)
        labels = substance_labels(meta, second_var)

        frame = fetch_slice(table, industry_var["id"], sorted(names),
                            second_var, second_values, years)
        frame["account"] = ACCOUNTS[table]
        frame["industry_name"] = frame["industry_code"].map(names)

        if table == "MRU1":
            parsed = {code: _split_unit(labels[code]) for code in second_values}
            frame["substance_name"] = frame["substance"].map(
                lambda c: parsed[c][0])
            frame["unit"] = frame["substance"].map(lambda c: parsed[c][1])
            frame["substance"] = frame["substance"].map(MRU1_SUBSTANCES)
        else:
            frame["substance_name"] = frame["substance"].map(labels)
            frame["unit"] = ("1000 t CO2e" if table == "DRIVHUS" else "GJ")

        frame["source"] = _stamp(table, meta, retrieved)
        frames.append(frame)
        report[table] = {
            "title": meta.get("text"), "updated": str(meta.get("updated"))[:10],
            "industry_variable": industry_var["id"],
            "industry_variable_text": industry_var.get("text"),
            "n_industries": len(names), "n_substances": len(second_values),
            "rows": len(frame),
            "first_period": None, "years": list(years),
        }

    out = pd.concat(frames, ignore_index=True)
    out = out[["year", "industry_code", "industry_name", "account", "substance",
               "substance_name", "unit", "value", "source"]]
    out = out.sort_values(["account", "year", "industry_code", "substance"],
                          kind="mergesort").reset_index(drop=True)
    return out, report


def check_internal_consistency(frame: pd.DataFrame) -> list[str]:
    """Check the published aggregates against their own components.

    Two identities are testable inside the download: the ``DRIVHUS``
    CO2-equivalent total against its four gases, and the ``ENE2HA`` total
    against its eight carrier groups. Both are checked per industry and year.

    Parameters
    ----------
    frame
        The long-format frame from :func:`fetch_all`.

    Returns
    -------
    list of str
        One human-readable line per identity.
    """

    lines: list[str] = []

    ghg = frame[frame["account"] == "greenhouse_gas"]
    wide = ghg.pivot_table(index=["year", "industry_code"], columns="substance",
                           values="value", aggfunc="sum")
    residual = (wide[list(DRIVHUS_COMPONENTS)].sum(axis=1)
                - wide["GHGEXBIO"]).abs()
    lines.append(
        f"DRIVHUS  GHGEXBIO vs CO2UBIO+N2O+CH4+FGAS: max |diff| "
        f"{residual.max():.0f} kt over {len(residual)} industry-years "
        f"(published rounding is 1 kt per gas)")

    energy = frame[frame["account"] == "energy_use"]
    ewide = energy.pivot_table(index=["year", "industry_code"],
                               columns="substance", values="value",
                               aggfunc="sum")
    eresid = (ewide[list(ENE2HA_GROUPS)].sum(axis=1) - ewide[ENE2HA_TOTAL]).abs()
    lines.append(
        f"ENE2HA   ETOT vs the eight carrier groups: max |diff| "
        f"{eresid.max():.0f} GJ over {len(eresid)} industry-years")
    return lines


def check_against_extract(frame: pd.DataFrame,
                          path: Any | None = None) -> pd.DataFrame:
    """Reconcile the download against the existing health-sector extract.

    The extract carries three of the 117 codes directly and two DB07
    aggregates. The aggregates are rebuilt from their 117-grouping members
    (``SECTION_MEMBERS``) rather than requested again, so the check tests the
    classification hierarchy as well as the values.

    Parameters
    ----------
    frame
        The long-format frame from :func:`fetch_all`.
    path
        Location of the extract. Defaults to the Bronze copy.

    Returns
    -------
    pandas.DataFrame
        One row per compared cell, with the extract value, the value implied by
        this download, the difference and how it was derived.
    """

    path = path or (BRONZE_DIR / VALIDATION_SOURCE)
    extract = pd.read_csv(path, comment="#")
    ghg = frame[frame["account"] == "greenhouse_gas"]
    lookup = ghg.set_index(["industry_code", "substance", "year"])["value"]

    rows: list[dict[str, Any]] = []
    for record in extract.itertuples(index=False):
        year = str(record.year)
        code, substance = record.industry_code, record.emtype
        if year not in set(frame["year"]):
            rows.append(dict(industry_code=code, substance=substance, year=year,
                             extract=float(record.value_kt_co2e), fetched=None,
                             difference=None, basis="year not fetched"))
            continue
        if code in SECTION_MEMBERS:
            members = SECTION_MEMBERS[code]
            try:
                fetched = float(sum(lookup[(m, substance, year)]
                                    for m in members))
            except KeyError:
                fetched = float("nan")
            basis = "sum of " + "+".join(m.lstrip("V") for m in members)
        else:
            fetched = float(lookup.get((code, substance, year), float("nan")))
            basis = "direct 117-grouping row"
        rows.append(dict(industry_code=code, substance=substance, year=year,
                         extract=float(record.value_kt_co2e), fetched=fetched,
                         difference=fetched - float(record.value_kt_co2e),
                         basis=basis))
    return pd.DataFrame(rows)


def _data_signature(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the comparable part of a frame, ignoring the retrieval stamp.

    Parameters
    ----------
    frame
        A long-format accounts frame.

    Returns
    -------
    pandas.DataFrame
        The frame without its ``source`` column, index reset.
    """

    cols = [c for c in frame.columns if c != "source"]
    return (frame[cols].sort_values(["account", "year", "industry_code",
                                     "substance"], kind="mergesort")
            .reset_index(drop=True))


def write_accounts(frame: pd.DataFrame, report: dict[str, Any],
                   path: Any | None = None) -> tuple[Any, bool]:
    """Write the accounts file, leaving it untouched when nothing changed.

    Idempotency is on the *data*: if an existing file carries identical values,
    the file is not rewritten, so a re-run does not churn the retrieval date in
    the ``source`` column or the file's mtime.

    Parameters
    ----------
    frame
        The long-format frame to write.
    report
        Per-table metadata, rendered into the header comment block.
    path
        Destination. Defaults to the Bronze location.

    Returns
    -------
    tuple
        The path written, and whether the file changed.
    """

    path = path or (BRONZE_DIR / OUTPUT_NAME)
    if path.exists():
        try:
            existing = pd.read_csv(path, comment="#")
        except (ValueError, pd.errors.ParserError):
            existing = None
        if existing is not None and len(existing.columns) == len(frame.columns):
            new_sig = _data_signature(frame)
            old_sig = _data_signature(existing.astype(
                {c: new_sig[c].dtype for c in new_sig.columns}))
            if new_sig.equals(old_sig):
                return path, False

    header = [
        "# Statistics Denmark environmental-economic accounts by industry, DB07 117-grouping.",
        "# Long format: one row per (year, industry_code, industry_name, account, substance, unit).",
        "# Retrieved through the open StatBank REST API (https://api.statbank.dk/v1/data), no key.",
        "# Written by src/analysis/fetch_dst_accounts.py - re-run rather than edit by hand.",
        "#",
    ]
    for table, info in report.items():
        header.append(f"# {table}: {info['title']} - {info['n_industries']} "
                      f"industries via variable {info['industry_variable']} "
                      f"({info['industry_variable_text']}), "
                      f"{info['n_substances']} series, table updated "
                      f"{info['updated']}.")
    header += [
        "#",
        "# Industry codes are the six-digit DB07 codes (V + six digits), the 117-grouping used by",
        "# the Danish IO tables and by the StatBank waste tables AFF1MU1N / AFF3MU1N. Section and",
        "# 69-grouping aggregates are excluded, so the 117 rows of any (year, account, substance)",
        "# block are exhaustive and non-overlapping.",
        "#",
        "# These are DIRECT (territorial, Scope 1) accounts on national-accounts residence",
        "# principles. DRIVHUS equals DRIVHUS2 with OPPRINCIP=DIR (verified); the FORDEL and",
        "# BRUTTO principles of DRIVHUS2, which reallocate electricity and district-heat",
        "# emissions onto the consuming industry, are NOT used - the IO model derives that",
        "# reallocation itself and would otherwise count it twice.",
        "#",
        "# Aggregates inside the substance column, do not sum blindly:",
        "#   greenhouse_gas: GHGEXBIO = CO2UBIO + N2O + CH4 + FGAS; GHGBIO = GHGEXBIO + CO2BIO.",
        "#   air_emission:   CO2INCBIO = CO2EXCBIO + CO2BIO.",
        "#   energy_use:     ETOT = EROOL + EOIL + ENGI + ENGF + EKUKO + EAFFA + EVE + EKONV.",
        "#",
        "# DRIVHUS is published rounded to whole 1,000 t CO2e, so small industries carry a",
        "# rounding error of up to ~1 kt per gas and anything below 500 t reports as zero. MRU1",
        "# publishes the non-CO2 substances in tonnes and is the more precise source for them.",
    ]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write("\n".join(header) + "\n")
        frame.to_csv(handle, index=False, lineterminator="\n")
    return path, True


def main() -> None:
    """Fetch, validate and write the accounts, printing what was retrieved."""

    frame, report = fetch_all()

    print("Statistics Denmark environmental accounts, DB07 117-grouping")
    print("=" * 78)
    for table, info in report.items():
        print(f"  {table:<9} {info['title']}")
        print(f"  {'':<9} industry variable {info['industry_variable']} "
              f"({info['industry_variable_text']}), "
              f"{info['n_industries']} industries x {info['n_substances']} "
              f"series x {len(info['years'])} years = {info['rows']:,} rows; "
              f"table updated {info['updated']}")

    print(f"\nfetched {len(frame):,} rows | years "
          f"{', '.join(sorted(frame['year'].unique()))} | "
          f"{frame['industry_code'].nunique()} industries | "
          f"{frame['account'].nunique()} accounts | "
          f"{frame['substance'].nunique()} substances/carriers")
    print(f"missing (suppressed) cells: {int(frame['value'].isna().sum())}")

    print("\nper-account coverage")
    coverage = (frame.groupby("account")
                .agg(rows=("value", "size"),
                     industries=("industry_code", "nunique"),
                     series=("substance", "nunique"),
                     units=("unit", lambda s: len(set(s))))
                .sort_index())
    print(coverage.to_string())

    print("\ninternal consistency")
    for line in check_internal_consistency(frame):
        print("  " + line)

    print(f"\nvalidation against {VALIDATION_SOURCE}")
    comparison = check_against_extract(frame)
    print(comparison.to_string(index=False))
    checked = comparison.dropna(subset=["difference"])
    worst = checked["difference"].abs().max() if len(checked) else float("nan")
    exact = int((checked["difference"] == 0).sum())
    print(f"  {exact} of {len(checked)} compared cells identical; "
          f"max |difference| {worst:.0f} kt CO2e "
          f"({len(comparison) - len(checked)} cells not comparable)")

    path, changed = write_accounts(frame, report)
    print(f"\n{'written' if changed else 'unchanged (data identical)'} -> {path}")


if __name__ == "__main__":
    main()
