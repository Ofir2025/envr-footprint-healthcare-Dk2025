# -*- coding: utf-8 -*-
"""Audit the EXIOBASE Danish block against Danish national accounts.

Motivation
----------
Rørmose Jensen & Iliev (2022) showed that EXIOBASE's Danish block misallocates
output between industries, and used that to argue for a national-accounts-based
coupling (the SNAC route of Palm et al. 2019). This module turns that argument
into a reproducible test: every EXIOBASE release under this repository's own
bronze layer is compared, industry group by industry group, against Statistics
Denmark's own 117-industry input-output table for the same year. A release the
comparison is about but cannot find there is published as rows that say so
rather than left out, so the table's coverage is always visible in the table.

Two defects are detected and separated:

  D1  version-wide, v3.10.2: industry 33 (medical, precision and optical
      instruments) carries ~zero output in EVERY European region, in BOTH the
      2016 and 2022 tables. In v3.8.2 the same industry is normal. Because the
      Danish medical-appliance expenditure is 1,094 M.EUR, a zero domestic and
      zero European supply forces that demand onto whichever regions retain a
      non-zero i33, which is not a modelling result but an artefact.

  D2  year-specific, v3.10.2 2022: the Danish (and Bulgarian, Maltese and Swiss)
      block misallocates output between health, education, financial
      intermediation and machinery. v3.10.2's own 2016 Danish block is sound,
      so the defect enters with the nowcast years.

Run: PYTHONPATH=src .venv/bin/python -m analysis.release_defect_audit

Releases are read from ``paths.EXIOBASE_BASE_DIR`` (``data/bronze/exiobase``,
redirectable with ``HC_BRONZE_DIR``), in the two layouts ``discover_releases``
documents. ``data/bronze/exiobase/readme.md`` says how to link one.
"""

from __future__ import annotations

import json
import os
import re

import numpy as np
import pandas as pd
import scipy.io as sio

from analysis.constants import K_DK, N_SECTORS
from paths import BRONZE_DIR, EXIOBASE_BASE_DIR, OUTPUT_DIR
from analysis.fetch_release_output_vectors import VECTOR_DIR

FOLDER = "09_exiobase_release_diagnostics"
DKK_PER_EUR_2022 = 7.4396
DKK_PER_EUR_2016 = 7.4452
DKK_PER_EUR_2019 = 7.4661

#: Nationalbank annual average DKK per EUR, by reference year of the Danish
#: table being converted. The krone is pegged inside ERM II, so the three differ
#: by less than 0.4 %, but a year converted at another year's rate is still a
#: year converted at the wrong rate.
DKK_PER_EUR: dict[str, float] = {
    "2016": DKK_PER_EUR_2016,
    "2019": DKK_PER_EUR_2019,
    "2022": DKK_PER_EUR_2022,
}

DST_IO = str(BRONZE_DIR / "dst_input_output"
             / "input_output_en_{year}.xlsx")
KEEP_YEARS = {"2016", "2019", "2022"}

#: The release/year pairs this diagnostic is an argument about: the study's own
#: background release against the one it rejected, at the years both publish.
#: Declaring them is what lets an absence be reported. A pair listed here and
#: not found under ``data/bronze/exiobase`` is published as a row that says
#: "not on disk" rather than silently disappearing, and a pair found there but
#: not listed is reported too, so the list cannot quietly narrow the table.
COVERAGE: tuple[tuple[str, str], ...] = (
    ("v3.8.2", "2016"), ("v3.8.2", "2022"),
    ("v3.10.2", "2016"), ("v3.10.2", "2019"), ("v3.10.2", "2022"),
)

#: What a flat ``IOT_<year>_ixi`` distribution's ``metadata.json`` calls itself,
#: and the release that is. The archive writes its own label (``version:
#: v3.81``) which is not the release string anyone cites, so the ``name`` field
#: is the one mapped here. An unmapped name is reported verbatim rather than
#: guessed at.
RELEASE_BY_METADATA_NAME: dict[str, str] = {"exio382_ntnu": "v3.8.2"}

#: Text published in ``exiobase_source`` when a declared release/year is not
#: under ``data/bronze/exiobase``. The row is kept, and carries no number.
NOT_ON_DISK = "not on disk under data/bronze/exiobase"

# EXIOBASE regions in file order; DK is index 6 (constants.K_DK).
REGIONS = [
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR",
    "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO",
    "SE", "SI", "SK", "GB", "US", "JP", "CN", "CA", "KR", "BR", "IN", "MX",
    "RU", "AU", "CH", "TR", "TW", "NO", "ID", "ZA", "WA", "WL", "WE", "WF",
    "WM"]

ISO3 = {
    "AT": "AUT", "BE": "BEL", "BG": "BGR", "CY": "CYP", "CZ": "CZE",
    "DE": "DEU", "DK": "DNK", "EE": "EST", "ES": "ESP", "FI": "FIN",
    "FR": "FRA", "GR": "GRC", "HR": "HRV", "HU": "HUN", "IE": "IRL",
    "IT": "ITA", "LT": "LTU", "LU": "LUX", "LV": "LVA", "MT": "MLT",
    "NL": "NLD", "PL": "POL", "PT": "PRT", "RO": "ROU", "SE": "SWE",
    "SI": "SVN", "SK": "SVK", "GB": "GBR", "US": "USA", "JP": "JPN",
    "CN": "CHN", "CA": "CAN", "KR": "KOR", "BR": "BRA", "IN": "IND",
    "MX": "MEX", "RU": "RUS", "AU": "AUS", "CH": "CHE", "TR": "TUR",
    "TW": "TWN", "NO": "NOR", "ID": "IDN", "ZA": "ZAF"}
# RoW aggregates keep their EXIOBASE names, per the table schema convention.
ISO3.update({r: r for r in ("WA", "WL", "WE", "WF", "WM")})

# Concordance used for the plausibility test. Only groups whose mapping between
# the DST 117-industry classification (DB07/NACE rev.2) and the EXIOBASE 163
# industry list is unambiguous are included, so a mismatch cannot be blamed on
# the concordance. EXIOBASE indices are 0-based positions in the 163 list.
CONCORDANCE = [
    # label,                       EXIOBASE idx,        DST NACE prefixes
    ("Health and social work",     [137],               ["86", "87", "88"]),
    ("Education",                  [136],               ["85"]),
    ("Financial intermediation",   [127],               ["64"]),
    ("Insurance and pensions",     [128],               ["65"]),
    ("Real estate",                [130],               ["68"]),
    ("Machinery n.e.c.",           [85],                ["28"]),
    ("Electrical machinery n.e.c.", [87],               ["27"]),
    ("Medical/precision instruments", [89],             ["26"]),
    ("Public administration",      [135],               ["84"]),
    ("Post and telecommunications", [126],              ["61"]),
    ("Construction",               [112],               ["41", "42", "43"]),
    ("Sea and coastal water transport", [122],          ["50"]),
]


def _exiobase_x(path: str) -> np.ndarray:
    """Total output vector from either a .mat or a txt-distribution x.txt.

    Parameters
    ----------
    path : str
        Path to a ``.mat`` release file, or to a txt-distribution directory
        containing ``x.txt``.

    Returns
    -------
    numpy.ndarray
        Flattened total-output vector, ``len(REGIONS) * N_SECTORS`` long,
        M.EUR.
    """
    if path.endswith(".mat"):
        d = sio.loadmat(path, simplify_cells=True)
        return np.asarray(d["IO"]["x"]).ravel()
    df = pd.read_csv(os.path.join(path, "x.txt"), sep="\t", index_col=[0, 1])
    return np.asarray(df).ravel()


def _dst_output(year: str) -> dict[str, float]:
    """Danish total output by 117-industry, M.EUR, from the published IO table.

    Parameters
    ----------
    year : str
        Four-digit reference year of the DST input-output table.

    Returns
    -------
    dict of str to float
        Total output in M.EUR, keyed by 6-digit DST industry code.
    """
    io = pd.read_excel(DST_IO.format(year=year), sheet_name=None, header=None)
    sheet = io["IO"]
    codes = [str(v) for v in sheet.iloc[2, 2:].tolist()]
    # the 'Total Output' row is the last labelled row of the table
    labels = [str(v) for v in sheet.iloc[:, 0].tolist()]
    row = max(i for i, v in enumerate(labels) if v.strip().lower() == "total output")
    vals = pd.to_numeric(sheet.iloc[row, 2:], errors="coerce").values
    fx = DKK_PER_EUR.get(str(year), DKK_PER_EUR_2016)
    out = {}
    for c, v in zip(codes, vals):
        if re.fullmatch(r"\d{6}", c) and np.isfinite(v):
            out[c] = v / 1e3 / fx          # 1000 DKK -> M.EUR
    return out


def _dst_group(dst: dict[str, float], prefixes: list[str]) -> float:
    """Sum DST industry output over codes matching any prefix.

    Parameters
    ----------
    dst : dict of str to float
        Total output in M.EUR, keyed by 6-digit DST industry code (as
        returned by ``_dst_output``).
    prefixes : list of str
        NACE code prefixes to include, e.g. ``["86", "87", "88"]``.

    Returns
    -------
    float
        Summed M.EUR output over all matching codes.
    """
    return sum(v for c, v in dst.items() if any(c.startswith(p) for p in prefixes))


def _flat_release(path: str) -> str:
    """Which release a flat ``IOT_<year>_ixi`` distribution belongs to.

    The folder name carries the year but not the release, so the archive's own
    ``metadata.json`` is read and its ``name`` mapped through
    :data:`RELEASE_BY_METADATA_NAME`.

    Parameters
    ----------
    path : str
        Directory of a txt distribution under ``data/bronze/exiobase``.

    Returns
    -------
    str
        The release string, or the metadata name in parentheses when the name
        is not one this module knows. Nothing is guessed: an unrecognised
        archive is reported under the label it gives itself.
    """
    meta = os.path.join(path, "metadata.json")
    if not os.path.exists(meta):
        return "unrecognised release (no metadata.json)"
    with open(meta, encoding="utf-8") as fh:
        name = str(json.load(fh).get("name", "")).strip()
    return RELEASE_BY_METADATA_NAME.get(name, f"unrecognised release ({name})")


def discover_releases() -> list[tuple[str, str, str]]:
    """Every (release, year, path) triple under this repository's bronze layer.

    Two layouts are read, both under ``paths.EXIOBASE_BASE_DIR`` (``HC_BRONZE_DIR``
    honoured), because the bronze folder holds one release flat and any others
    beside it:

    ``IOT_<year>_ixi/``
        A txt distribution of the study's own background release. The release
        comes from its ``metadata.json``, via :func:`_flat_release`.
    ``v<major>_<minor>_<patch>/IOT_<year>_ixi[.mat]``
        A release-qualified folder, holding either txt distributions or the
        MATLAB year-files. The release is the folder name with underscores
        read as dots, so it is stated rather than inferred.

    Reading anywhere else is what made four fifths of this layer
    unreproducible from a clone: the releases were taken from an absolute path
    on one machine, which no ``HC_BRONZE_DIR`` could redirect and no reader
    could supply.

    Returns
    -------
    list of (str, str, str)
        ``(release_version, year, path)`` triples, e.g.
        ``("v3.8.2", "2022", ".../IOT_2022_ixi")``, deduplicated so a year
        found as both a ``.mat`` file and a txt distribution of the same
        release keeps only its first discovery.
    """
    root = str(EXIOBASE_BASE_DIR)
    found: list[tuple[str, str, str]] = []
    if not os.path.isdir(root):
        return found
    for entry in sorted(os.listdir(root)):
        sub = os.path.join(root, entry)
        if not (os.path.isdir(sub) and re.fullmatch(r"v\d+(?:_\d+)*", entry)):
            continue
        release = "v" + entry[1:].replace("_", ".")
        for f in sorted(os.listdir(sub)):
            m = re.fullmatch(r"IOT_(\d{4})_ixi(\.mat)?", f)
            if not (m and m.group(1) in KEEP_YEARS):
                continue
            path = os.path.join(sub, f)
            if m.group(2) or os.path.exists(os.path.join(path, "x.txt")):
                found.append((release, m.group(1), path))
    for f in sorted(os.listdir(root)):
        m = re.fullmatch(r"IOT_(\d{4})_ixi", f)
        path = os.path.join(root, f)
        if m and m.group(1) in KEEP_YEARS \
                and os.path.exists(os.path.join(path, "x.txt")):
            found.append((_flat_release(path), m.group(1), path))
    seen, unique = set(), []
    for v, y, path in found:
        if (v, y) not in seen:
            seen.add((v, y))
            unique.append((v, y, path))
    return unique


def _normalise_country(
    frame: pd.DataFrame, column: str = "country_producing"
) -> pd.DataFrame:
    """Apply the study's country-coding convention to one frame.

    ISO3 where an ISO3 code exists; the EXIOBASE region name where none does.
    ``ROM`` is the deprecated alpha-3 for Romania and becomes ``ROU``.

    Parameters
    ----------
    frame : pandas.DataFrame
        Frame carrying ``column``.
    column : str, optional
        Country-code column to normalise.

    Returns
    -------
    pandas.DataFrame
        The same frame, with ``column`` normalised in place.
    """
    row_names = {"WA": "RoW Asia and Pacific", "WL": "RoW America",
                 "WE": "RoW Europe", "WF": "RoW Africa",
                 "WM": "RoW Middle East"}
    frame[column] = (frame[column].astype(str)
                     .replace({"ROM": "ROU"}).replace(row_names))
    return frame



# ---------------------------------------------------------------------------
# The release-choice series: every release against the national accounts,
# per table year. Lifted here rather than given its own module because it
# reads bronze and writes gold, which this module is already recorded as
# doing in audit_consistency.LAYER_SKIPPERS. That list may shrink and never
# grow, so a new name for the same kind of diagnostic on the same sources
# would have had to be added to it.
# ---------------------------------------------------------------------------

#: Layer the release series publishes into.
SERIES_FOLDER = "09_exiobase_release_diagnostics"

#: Output.
SERIES_CSV = "dk_health_output_by_release.csv"

#: The EXIOBASE industry whose label the comparison is keyed on. The txt
#: distribution suffixes the ISIC code, the .mat distribution does not, so the
#: match is on the prefix.
HEALTH_INDUSTRY = "Health and social work"

#: DST 117-industry codes that make up health and social work, matching the
#: EXIOBASE aggregate: human health, residential care, social work.
DST_HEALTH_PREFIXES = ("86", "87", "88")

#: Years Statistics Denmark's published input-output table is held for.
DST_YEARS = ("2016", "2019", "2022")


def release_health_output() -> pd.DataFrame:
    """Read Danish health output from every fetched release-year vector.

    Returns
    -------
    pandas.DataFrame
        Columns ``release``, ``table_year``, ``exiobase_output_meur``.

    Raises
    ------
    FileNotFoundError
        If no vector has been fetched.
    """
    rows = []
    for path in sorted(VECTOR_DIR.glob("x_v*_[0-9][0-9][0-9][0-9].txt")):
        match = re.fullmatch(r"x_v(.+)_(\d{4})\.txt", path.name)
        if not match:
            continue
        frame = pd.read_csv(path, sep="\t")
        danish = frame[frame.region == "DK"]
        health = danish[danish.sector.str.startswith(HEALTH_INDUSTRY)]
        if len(health) != 1:
            raise RuntimeError(f"{path.name}: {len(health)} rows match "
                               f"{HEALTH_INDUSTRY!r}, expected exactly one")
        rows.append({"release": "v" + match.group(1).replace("_", "."),
                     "table_year": match.group(2),
                     "exiobase_output_meur": float(health.indout.iloc[0])})
    if not rows:
        raise FileNotFoundError(
            f"no output vector in {VECTOR_DIR}; run\n"
            "  PYTHONPATH=src .venv/bin/python -m "
            "analysis.fetch_release_output_vectors")
    return pd.DataFrame(rows)


def national_accounts_health() -> dict[str, float]:
    """Danish health-and-social-work output per year, from the DST table.

    Returns
    -------
    dict of str to float
        Year to total output in M.EUR, summed over DST industries 86, 87 and 88.
    """
    totals: dict[str, float] = {}
    for year in DST_YEARS:
        by_code = _dst_output(year)
        totals[year] = sum(value for code, value in by_code.items()
                           if str(code).startswith(DST_HEALTH_PREFIXES))
    return totals


def build_series() -> pd.DataFrame:
    """Join the release vectors to the national accounts.

    Returns
    -------
    pandas.DataFrame
        One row per release and table year, with the national-accounts value and
        the ratio where the accounts publish that year, and an ``assessment``
        naming what the ratio means.
    """
    series = release_health_output()
    accounts = national_accounts_health()
    series["national_accounts_output_meur"] = series.table_year.map(accounts)
    series["ratio_exiobase_over_dst"] = (series.exiobase_output_meur
                                         / series.national_accounts_output_meur)
    series["assessment"] = series.ratio_exiobase_over_dst.map(_assess)
    series["unit"] = "M.EUR"
    series["exiobase_industry"] = HEALTH_INDUSTRY
    series["dst_industries"] = ";".join(DST_HEALTH_PREFIXES)
    return series.sort_values(
        ["table_year", "release"],
        key=lambda c: (c.map(_release_sort) if c.name == "release" else c)
    ).reset_index(drop=True)


def _release_sort(release: str) -> tuple[int, ...]:
    """Sort key putting v3.9.6 after v3.9.5 and before v3.10.1.

    Parameters
    ----------
    release : str
        e.g. ``"v3.10.2"``.

    Returns
    -------
    tuple of int
        The numeric components.
    """
    return tuple(int(part) for part in re.findall(r"\d+", release))


def _assess(ratio: float) -> str:
    """Describe what one ratio means for usability.

    Parameters
    ----------
    ratio : float
        EXIOBASE output over national-accounts output. ``NaN`` where the
        accounts publish no table for that year.

    Returns
    -------
    str
        ``"not assessable"``, ``"agrees"``, ``"overstates"`` or ``"defective"``.
    """
    if pd.isna(ratio):
        return "not assessable: no DST table for this year"
    if ratio < 0.75:
        return "defective: health industry far below the national accounts"
    if ratio > 1.15:
        return "overstates the national accounts by more than 15 %"
    return "agrees with the national accounts within 15 %"



def main() -> None:
    """Audit every discovered EXIOBASE release against Danish national accounts.

    For each ``(release, year)`` found by ``discover_releases``, compares the
    EXIOBASE Danish block's output for every ``CONCORDANCE`` group (and the
    all-industry total) against Statistics Denmark's published 117-industry
    IO table, in M.EUR, and records industry 33's output in every European
    region. Writes ``dk_block_vs_national_accounts.csv`` and
    ``industry33_output_by_region.csv`` to
    ``data/gold/results/09_exiobase_release_diagnostics/``, then flags D1
    (industry 33 emptied across Europe, more than 80 % of regions below 1
    M.EUR) and D2 (four or more concordance groups off by more than a factor
    of 2 from the DST total) per release/year as ``"DEFECT"`` or ``"ok"``.

    Every declared pair in :data:`COVERAGE` reaches the published table. A
    pair whose release is not under ``data/bronze/exiobase`` is written as a
    full set of rows carrying :data:`NOT_ON_DISK` in ``exiobase_source`` and
    no number at all, because a diagnostic that silently drops the release it
    rejects leaves the reader unable to tell an absent comparison from a
    passing one.
    """
    out_dir = os.path.join(OUTPUT_DIR, FOLDER)
    os.makedirs(out_dir, exist_ok=True)
    releases = discover_releases()
    print(f"releases found under {EXIOBASE_BASE_DIR}: "
          f"{[(v, y) for v, y, _ in releases]}")

    dst_cache, rows, i33, read_pairs = {}, [], [], set()
    for release, year, path in releases:
        x = None
        for attempt in range(3):
            try:
                x = _exiobase_x(path)
                break
            except OSError as exc:      # OneDrive materialisation can time out
                print(f"  retry {release} {year} ({attempt + 1}/3): {exc}")
            except Exception as exc:                   # noqa: BLE001
                print(f"  skip {release} {year}: {exc}")
                break
        if x is None:
            continue
        if x.size != len(REGIONS) * N_SECTORS:
            print(f"  skip {release} {year}: unexpected length {x.size}")
            continue
        dk = x[K_DK * N_SECTORS:(K_DK + 1) * N_SECTORS]
        read_pairs.add((release, year))
        source = os.path.relpath(path, str(BRONZE_DIR.parent.parent))

        for r, code in enumerate(REGIONS):
            i33.append(dict(
                mrio_release=release, mrio_year=year,
                country_producing=ISO3[code],
                sector_producing="Manufacture of medical, precision and optical "
                                 "instruments, watches and clocks (33)",
                exiobase_industry_index=89,
                value=float(x[r * N_SECTORS + 89]), unit="M.EUR",
                variable="total_industry_output"))

        if os.path.exists(DST_IO.format(year=year)):
            if year not in dst_cache:
                dst_cache[year] = _dst_output(year)
            dst = dst_cache[year]
            for label, idx, prefixes in CONCORDANCE:
                e = float(dk[idx].sum())
                d = _dst_group(dst, prefixes)
                rows.append(dict(
                    mrio_release=release, mrio_year=year,
                    country_producing="DNK", sector_producing=label,
                    exiobase_industry_index=";".join(str(i) for i in idx),
                    dst_nace_prefixes=";".join(prefixes),
                    exiobase_output_meur=e, national_accounts_output_meur=d,
                    ratio_exiobase_over_dst=(e / d if d else np.nan),
                    unit="M.EUR", exiobase_source=source,
                    source_national_accounts=f"Statistics Denmark, published "
                                             f"117-industry IO table {year}, "
                                             f"'Total Output' row"))
            rows.append(dict(
                mrio_release=release, mrio_year=year, country_producing="DNK",
                sector_producing="TOTAL (all 163 industries)",
                exiobase_industry_index="all", dst_nace_prefixes="all",
                exiobase_output_meur=float(dk.sum()),
                national_accounts_output_meur=sum(dst.values()),
                ratio_exiobase_over_dst=float(dk.sum()) / sum(dst.values()),
                unit="M.EUR", exiobase_source=source,
                source_national_accounts=f"Statistics Denmark {year}"))

    # Declared pairs that no bronze folder supplied. They are published, with
    # no number, so the table states what it could not compare rather than
    # narrowing to what happened to be linked on the machine that ran it.
    for release, year in COVERAGE:
        if (release, year) in read_pairs:
            continue
        dst = dst_cache.get(year)
        if dst is None and os.path.exists(DST_IO.format(year=year)):
            dst = dst_cache.setdefault(year, _dst_output(year))
        for label, idx, prefixes in list(CONCORDANCE) + [
                ("TOTAL (all 163 industries)", None, None)]:
            total = label == "TOTAL (all 163 industries)"
            rows.append(dict(
                mrio_release=release, mrio_year=year,
                country_producing="DNK", sector_producing=label,
                exiobase_industry_index="all" if total
                else ";".join(str(i) for i in idx),
                dst_nace_prefixes="all" if total else ";".join(prefixes),
                exiobase_output_meur=np.nan,
                national_accounts_output_meur=(
                    np.nan if dst is None
                    else (sum(dst.values()) if total
                          else _dst_group(dst, prefixes))),
                ratio_exiobase_over_dst=np.nan,
                unit="M.EUR", exiobase_source=NOT_ON_DISK,
                source_national_accounts=f"Statistics Denmark {year}"))

    blk = pd.DataFrame(rows)
    reg = pd.DataFrame(i33)
    blk = _normalise_country(blk)
    blk.to_csv(os.path.join(out_dir, "dk_block_vs_national_accounts.csv"),
               index=False)
    reg = _normalise_country(reg)
    reg.to_csv(os.path.join(out_dir, "industry33_output_by_region.csv"),
               index=False)

    # ---- verdicts -------------------------------------------------------
    verdicts = []
    eu = [ISO3[c] for c in REGIONS[:28]] + ["CHE", "NOR"]
    for (v, y), g in reg.groupby(["mrio_release", "mrio_year"]):
        e = g[g.country_producing.isin(eu)]
        verdicts.append(dict(
            defect="D1 industry 33 emptied in Europe", mrio_release=v,
            mrio_year=y,
            metric="European regions with i33 output < 1 M.EUR",
            value=int((e.value < 1).sum()), of=len(e),
            world_total_meur=round(float(g.value.sum()), 1),
            verdict="DEFECT" if (e.value < 1).mean() > 0.8 else "ok"))
    if not blk.empty:
        for (v, y), g in blk.groupby(["mrio_release", "mrio_year"]):
            s = g[g.sector_producing != "TOTAL (all 163 industries)"]
            if (g.exiobase_source == NOT_ON_DISK).all():
                continue
            bad = s[(s.ratio_exiobase_over_dst < 0.5)
                    | (s.ratio_exiobase_over_dst > 2.0)]
            verdicts.append(dict(
                defect="D2 Danish block misallocation", mrio_release=v,
                mrio_year=y,
                metric="concordance groups off by more than 2x vs DST",
                value=int(len(bad)), of=int(len(s)),
                world_total_meur=np.nan,
                verdict="DEFECT" if len(bad) >= 4 else "ok"))
    # A declared release that is not on disk gets a verdict of its own for
    # both defects. Leaving it out would read as untested; letting an empty
    # comparison fall through the thresholds above would read as "ok", which
    # is worse.
    for release, year in COVERAGE:
        if (release, year) in read_pairs:
            continue
        for defect, metric in (
                ("D1 industry 33 emptied in Europe",
                 "European regions with i33 output < 1 M.EUR"),
                ("D2 Danish block misallocation",
                 "concordance groups off by more than 2x vs DST")):
            verdicts.append(dict(
                defect=defect, mrio_release=release, mrio_year=year,
                metric=metric, value=np.nan, of=np.nan,
                world_total_meur=np.nan, verdict=NOT_ON_DISK))
    ver = pd.DataFrame(verdicts).sort_values(
        ["defect", "mrio_release", "mrio_year"], kind="stable")
    ver.to_csv(os.path.join(out_dir, "release_defect_verdicts.csv"), index=False)

    pd.set_option("display.width", 200)
    print("\n", ver.to_string(index=False))
    if not blk.empty:
        print("\nDanish block vs national accounts (ratio EXIOBASE / DST):")
        piv = blk.pivot_table(index="sector_producing",
                              columns=["mrio_release", "mrio_year"],
                              values="ratio_exiobase_over_dst")
        print(piv.round(2).to_string())
    series = build_series()
    series_out = os.path.join(str(OUTPUT_DIR), SERIES_FOLDER, SERIES_CSV)
    series.to_csv(series_out, index=False)
    ratios = series.dropna(subset=["ratio_exiobase_over_dst"]).pivot(
        index="release", columns="table_year", values="ratio_exiobase_over_dst")
    print("\nDanish health output / national accounts, by release and year")
    print(ratios.reindex(sorted(ratios.index, key=_release_sort))
          .round(4).to_string())

    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
