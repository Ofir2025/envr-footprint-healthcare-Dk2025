# -*- coding: utf-8 -*-
"""Audit the EXIOBASE Danish block against Danish national accounts.

Motivation
----------
Rørmose Jensen & Iliev (2022) showed that EXIOBASE's Danish block misallocates
output between industries, and used that to argue for a national-accounts-based
coupling (the SNAC route of Palm et al. 2019). This module turns that argument
into a reproducible test: every EXIOBASE release on disk is compared, industry
group by industry group, against Statistics Denmark's own 117-industry
input-output table for the same year.

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
"""

import os
import re

import numpy as np
import pandas as pd
import scipy.io as sio

from analysis.constants import K_DK, N_SECTORS
from paths import BRONZE_DIR, OUTPUT_DIR

FOLDER = "09_exiobase_release_diagnostics"
DKK_PER_EUR_2022 = 7.4396
DKK_PER_EUR_2016 = 7.4452

EXIO_ROOT = os.path.expanduser(
    "~/Library/CloudStorage/OneDrive-Personal/Data/lca/input_output/mrio/"
    "exiobase/versions")
DST_IO = str(BRONZE_DIR / "input_output" / "2016_2022"
             / "input_output_en_{year}.xlsx")
KEEP_YEARS = {"2016", "2019", "2022"}

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


def _exiobase_x(path):
    """Total output vector from either a .mat or a txt-distribution x.txt."""
    if path.endswith(".mat"):
        d = sio.loadmat(path, simplify_cells=True)
        return np.asarray(d["IO"]["x"]).ravel()
    df = pd.read_csv(os.path.join(path, "x.txt"), sep="\t", index_col=[0, 1])
    return np.asarray(df).ravel()


def _dst_output(year):
    """Danish total output by 117-industry, M.EUR, from the published IO table."""
    io = pd.read_excel(DST_IO.format(year=year), sheet_name=None, header=None)
    sheet = io["IO"]
    codes = [str(v) for v in sheet.iloc[2, 2:].tolist()]
    # the 'Total Output' row is the last labelled row of the table
    labels = [str(v) for v in sheet.iloc[:, 0].tolist()]
    row = max(i for i, v in enumerate(labels) if v.strip().lower() == "total output")
    vals = pd.to_numeric(sheet.iloc[row, 2:], errors="coerce").values
    fx = DKK_PER_EUR_2022 if str(year) == "2022" else DKK_PER_EUR_2016
    out = {}
    for c, v in zip(codes, vals):
        if re.fullmatch(r"\d{6}", c) and np.isfinite(v):
            out[c] = v / 1e3 / fx          # 1000 DKK -> M.EUR
    return out


def _dst_group(dst, prefixes):
    return sum(v for c, v in dst.items() if any(c.startswith(p) for p in prefixes))


def discover_releases():
    """Every (release, year, path) triple present on this machine."""
    found = []
    txt = os.path.join(EXIO_ROOT, "v3_10_2", "txt")
    if os.path.exists(os.path.join(txt, "x.txt")):
        found.append(("v3.10.2", "2022", txt))
    # v3.6 is superseded and its 20 year-files are large; the comparison that
    # matters is between the releases this study could actually use.
    for v, sub in (("v3.10.2", "v3_10_2/industry"), ("v3.8.2", "v3_8_2"),
                   ("v3.7", "v3_7")):
        d = os.path.join(EXIO_ROOT, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            m = re.fullmatch(r"IOT_(\d{4})_ixi\.mat", f)
            if m and m.group(1) in KEEP_YEARS:
                found.append((v, m.group(1), os.path.join(d, f)))
        for f in sorted(os.listdir(d)):
            m = re.fullmatch(r"IOT_(\d{4})_ixi", f)
            if m and m.group(1) in KEEP_YEARS \
                    and os.path.exists(os.path.join(d, f, "x.txt")):
                found.append((v, m.group(1), os.path.join(d, f)))
    # a year can be discovered twice (txt distribution and .mat of the same
    # release); keep the first occurrence only
    seen, unique = set(), []
    for v, y, path in found:
        if (v, y) not in seen:
            seen.add((v, y))
            unique.append((v, y, path))
    return unique


def _normalise_country(frame, column="country_producing"):
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


def main():
    out_dir = os.path.join(OUTPUT_DIR, FOLDER)
    os.makedirs(out_dir, exist_ok=True)
    releases = discover_releases()
    print(f"releases found: {[(v, y) for v, y, _ in releases]}")

    dst_cache, rows, i33 = {}, [], []
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
                    unit="M.EUR",
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
                unit="M.EUR",
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
            bad = s[(s.ratio_exiobase_over_dst < 0.5)
                    | (s.ratio_exiobase_over_dst > 2.0)]
            verdicts.append(dict(
                defect="D2 Danish block misallocation", mrio_release=v,
                mrio_year=y,
                metric="concordance groups off by more than 2x vs DST",
                value=int(len(bad)), of=int(len(s)),
                world_total_meur=np.nan,
                verdict="DEFECT" if len(bad) >= 4 else "ok"))
    ver = pd.DataFrame(verdicts)
    ver.to_csv(os.path.join(out_dir, "release_defect_verdicts.csv"), index=False)

    pd.set_option("display.width", 200)
    print("\n", ver.to_string(index=False))
    if not blk.empty:
        print("\nDanish block vs national accounts (ratio EXIOBASE / DST):")
        piv = blk.pivot_table(index="sector_producing",
                              columns=["mrio_release", "mrio_year"],
                              values="ratio_exiobase_over_dst")
        print(piv.round(2).to_string())
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
