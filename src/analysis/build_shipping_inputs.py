# -*- coding: utf-8 -*-
r"""Silver-stage inputs for the Danish sea-transport reallocation.

Why this module exists
----------------------
:mod:`analysis.dk_shipping_correction` writes published tables into gold. It
also used to open three bronze files on its way there: Statistics Denmark's
domestic input-output workbook for the target share :math:`\phi`, the detailed
supply-use workbook and the DRIVHUS extract for the expenditure frame, and
EXIOBASE's ``classifications.xlsx`` for the sector groups. That made it a
bronze-to-gold module with no reproducible middle - medallion rule 4 - and it
was carried on ``audit_consistency.LAYER_SKIPPERS`` as debt.

This module is the middle. It reads bronze, conforms what it finds, and writes
three small CSVs into silver. ``dk_shipping_correction`` reads those and no
longer opens bronze at all, which is how the skipper list shrinks by one rather
than by being argued with.

What it writes
--------------
``dst_input_output/dst_water_transport_domestic_share.csv``
    The target share :math:`\phi` per year, with the two quantities it is the
    quotient of, so a reader can check the division rather than trust it.

``dst_supply_use/dk_health_expenditure_frame.csv``
    The three-row expenditure and direct-emission frame
    ``functions_2025.createBackground`` consumes, one block per analysis year.

``exiobase/exiobase_industry_sector_group.csv``
    EXIOBASE industry code to its aggregate reporting group.

The three folders are not an accident: silver mirrors bronze by provenance, so
each product sits under the silver folder named for the bronze folder it was
read from.

The share
---------
Rørmose Jensen & Iliev (2022, pp. 11-12) publish the national-accounts share for
2019 only. It is a ratio inside Statistics Denmark's own domestic input-output
table, so it can be read from that table for every year the study runs on:

.. math::

   \phi(t) = \frac{\sum_{j=1}^{117} d_{\mathrm{wt},j}(t)}{x_{\mathrm{wt}}(t)}

where :math:`d_{\mathrm{wt},j}` is the delivery of row 500000 (Water transport)
of the ``DIO`` sheet to Danish industry :math:`j` and :math:`x_{\mathrm{wt}}` is
that row's ``Total``. Both are in 1000 DKK, so :math:`\phi` is dimensionless and
the crowns cancel.

The 2019 row is the **validation**, not an input: it reproduces Rørmose Jensen &
Iliev's 9 % to within 0.3 percentage points, and that is what licenses reading
the other two years off the same table. It is written to the silver table so the
consumer can re-assert it on every run without reopening bronze.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.build_shipping_inputs``
"""

from __future__ import annotations

import datetime as dt
import re

import numpy as np
import pandas as pd

from paths import (BRONZE_DIR, EXIOBASE_BASE_DIR,
                   SILVER_DST_INPUT_OUTPUT_DIR, SILVER_DST_SUPPLY_USE_DIR,
                   SILVER_EXIOBASE_DIR)

#: Statistics Denmark's published input-output workbook, one per year.
DST_IO = BRONZE_DIR / "dst_input_output" / "input_output_en_{year}.xlsx"

#: The detailed supply-use workbook and the DRIVHUS extract the expenditure
#: frame is built from.
DK_UMAT = BRONZE_DIR / "dst_supply_use" / "dk_umat_2019.xlsx"
DRIVHUS = (BRONZE_DIR / "dst_emission_accounts"
           / "dk_direct_emissions_drivhus.csv")

#: EXIOBASE's classification workbook, whose ``disagg_ind`` sheet carries the
#: aggregate reporting group of every industry.
CLASSIFICATIONS = EXIOBASE_BASE_DIR / "classifications.xlsx"

#: Sheet of the DST workbook holding the DOMESTIC input-output table. The
#: ``IO`` sheet is the total table, domestic plus imported; only the domestic
#: one measures what share of a Danish industry's output Danish industries
#: actually buy.
DST_SHEET = "DIO"

#: DST DB07 code of Water transport.
WATER_TRANSPORT_CODE = "500000"

#: Row label opening the Danish-production block of the ``DIO`` sheet, and the
#: one opening the Imports block that follows it. The 117 product codes repeat
#: in both, so the domestic row has to be located between them.
DST_DOMESTIC_BLOCK = "Danish production"
DST_IMPORT_BLOCK = "Imports"

#: The share Rørmose Jensen & Iliev (2022, pp. 11-12) report for 2019.
RORMOSE_2019_SHARE = 0.09

#: Year of the DST table whose share validates the parse. It is the one year
#: they publish, and it is NOT a background year of this study - the 2019
#: analysis runs on the 2016 background.
RORMOSE_CROSS_CHECK_YEAR = "2019"

#: How far the DST 2019 share may sit from :data:`RORMOSE_2019_SHARE` before
#: the cross-check fails. 0.005 is half a percentage point; the observed gap is
#: 0.003, so the check has roughly a factor of two of headroom and would still
#: catch a parse that picked up the wrong row, the wrong sheet or the import
#: block instead of the domestic one.
RORMOSE_TOLERANCE = 0.005

#: DST table years read. 2016 and 2022 are the study's background years; 2019 is
#: the cross-check year and serves no background.
TABLE_YEARS: tuple[str, ...] = ("2016", "2019", "2022")

#: Which background year consumes each table year. The cross-check year is
#: consumed by none, and its ``background_year`` cell is left empty.
BACKGROUND_FOR_TABLE_YEAR: dict[str, str] = {"2016": "2016", "2022": "2022"}

#: Which analysis year each background year serves. The expenditure vector is an
#: analysis-year quantity.
ANALYSIS_YEAR_FOR_BACKGROUND: dict[str, str] = {"2016": "2019", "2022": "2022"}

#: Danmarks Nationalbank annual average DKK per euro, as
#: ``analysis.main_2025.DKK_PER_EUR_BY_YEAR``.
DKK_PER_EUR_BY_YEAR: dict[str, float] = {"2019": 7.4661, "2022": 7.4396}

#: The three silver products, by name. Kept as bare names because they are
#: quoted back in this module's and ``dk_shipping_correction``'s error
#: messages, where the folder is noise.
SHARE_CSV = "dst_water_transport_domestic_share.csv"
EXPENDITURE_CSV = "dk_health_expenditure_frame.csv"
SECTOR_GROUP_CSV = "exiobase_industry_sector_group.csv"

#: The same three as paths. They do NOT share a folder: silver mirrors bronze
#: by provenance, and these three products come from three different providers'
#: folders -- the share from Statistics Denmark's input-output workbooks, the
#: expenditure frame from the detailed supply-use table, the sector groups from
#: EXIOBASE's classification workbook. One module writing into three folders is
#: the mirror working, not a defect: what groups a silver file is where its
#: numbers came from, not which script happened to write it.
SHARE_PATH = SILVER_DST_INPUT_OUTPUT_DIR / SHARE_CSV
EXPENDITURE_PATH = SILVER_DST_SUPPLY_USE_DIR / EXPENDITURE_CSV
SECTOR_GROUP_PATH = SILVER_EXIOBASE_DIR / SECTOR_GROUP_CSV


def _today() -> str:
    """Today's date, ISO-8601.

    Returns
    -------
    str
        ``YYYY-MM-DD``. Recorded in the ``retrieved`` column so a reader can
        tell when a silver row was last read off the bronze workbook.
    """
    return dt.date.today().isoformat()


def water_transport_deliveries(year: str) -> tuple[float, float]:
    """Danish intermediate deliveries and total output of Water transport.

    Reads the ``DIO`` sheet of Statistics Denmark's published table for one
    year. The sheet is not header-first: the banner occupies row 0, the
    six-digit industry codes row 2, and the row labels column A, so the blocks
    are located by label rather than by position.

    Parameters
    ----------
    year : str
        Reference year of the published Danish input-output table, e.g.
        ``"2016"``.

    Returns
    -------
    tuple of (float, float)
        Deliveries to the 117 Danish industries, and the row's own total
        output. Both in 1000 DKK.

    Raises
    ------
    ValueError
        If the sheet does not yield 117 industry columns, if the Water
        transport row cannot be located inside the Danish-production block, or
        if the row's total output is not positive.
    """
    sheet = pd.read_excel(str(DST_IO).format(year=year),
                          sheet_name=DST_SHEET, header=None)
    header = [str(v).strip() for v in sheet.iloc[2, :].tolist()]
    banner = [str(v).strip() for v in sheet.iloc[0, :].tolist()]
    labels = [str(v).strip() for v in sheet.iloc[:, 0].tolist()]

    industry_columns = [j for j, code in enumerate(header)
                        if re.fullmatch(r"\d{6}", code)]
    if len(industry_columns) != 117:
        raise ValueError(f"read {len(industry_columns)} industry columns from "
                         f"the {year} {DST_SHEET} sheet, expected 117")

    first = labels.index(DST_DOMESTIC_BLOCK)
    last = labels.index(DST_IMPORT_BLOCK)
    rows = [i for i, label in enumerate(labels)
            if label == WATER_TRANSPORT_CODE and first < i < last]
    if len(rows) != 1:
        raise ValueError(f"found {len(rows)} rows coded "
                         f"{WATER_TRANSPORT_CODE} in the Danish-production "
                         f"block of the {year} {DST_SHEET} sheet, expected 1")
    row = rows[0]

    total_column = banner.index("Total")
    deliveries = pd.to_numeric(sheet.iloc[row, industry_columns],
                               errors="coerce").to_numpy(dtype=float)
    total = float(pd.to_numeric(sheet.iat[row, total_column]))
    if not np.isfinite(total) or total <= 0:
        raise ValueError(f"the {year} {DST_SHEET} Water transport row has "
                         f"total output {total}, which cannot be a divisor")
    return float(np.nansum(deliveries)), total


def domestic_share_table(years: tuple[str, ...] = TABLE_YEARS) -> pd.DataFrame:
    """The target share phi for every DST table year.

    Parameters
    ----------
    years : tuple of str, optional
        DST table years to read. Defaults to :data:`TABLE_YEARS`.

    Returns
    -------
    pandas.DataFrame
        Columns ``background_year``, ``dst_table_year``,
        ``domestic_intermediate_dkk``, ``row_total_dkk``, ``phi``,
        ``source_workbook`` and ``retrieved``. One row per table year.

    Raises
    ------
    AssertionError
        If the 2019 table does not reproduce
        :data:`RORMOSE_2019_SHARE` to within :data:`RORMOSE_TOLERANCE`. The
        parse is validated against the only published figure here, at build
        time, and the validating row is written out so the consumer can assert
        it again without reopening bronze.
    """
    rows: list[dict[str, object]] = []
    for year in years:
        domestic, total = water_transport_deliveries(year)
        rows.append(dict(
            background_year=BACKGROUND_FOR_TABLE_YEAR.get(year, ""),
            dst_table_year=year,
            domestic_intermediate_dkk=domestic,
            row_total_dkk=total,
            phi=domestic / total,
            source_workbook=DST_IO.name.format(year=year),
            retrieved=_today()))
    table = pd.DataFrame(rows)

    check = float(table.loc[table.dst_table_year == RORMOSE_CROSS_CHECK_YEAR,
                            "phi"].iloc[0])
    if abs(check - RORMOSE_2019_SHARE) > RORMOSE_TOLERANCE:
        raise AssertionError(
            f"cross-check failed: the DST {DST_SHEET} table for "
            f"{RORMOSE_CROSS_CHECK_YEAR} gives a domestic intermediate share "
            f"of {check:.4f}, which is more than {RORMOSE_TOLERANCE} from the "
            f"{RORMOSE_2019_SHARE} Rørmose Jensen & Iliev (2022, pp. 11-12) "
            f"report. Either the parse is wrong or the published table has "
            f"been revised; do not publish a share this has not validated.")
    return table


def expenditure_frame(analysis_year: str) -> pd.DataFrame:
    """The expenditure and direct-emission frame for one analysis year.

    ``functions_2025.createBackground`` consumes a three-row, three-column
    frame indexed by ``(Index, Unit)``: expenditure on health-care services,
    pharmaceuticals and appliances in M.EUR, the basic-price conversion (1.0,
    because both Danish expenditure routes are already at basic prices), and
    the sector's direct greenhouse-gas emissions in kt. It is rebuilt here with
    the same :mod:`analysis.extra_functions` routines
    :mod:`analysis.main_2025` uses, rather than copied from the silver frame
    :mod:`analysis.main_2025` leaves behind, which holds whichever analysis
    year ran last.

    Parameters
    ----------
    analysis_year : str
        ``"2019"`` or ``"2022"``.

    Returns
    -------
    pandas.DataFrame
        Indexed by ``(Index, Unit)``, columns ``HC service``, ``Pharm``,
        ``MedAppl``, in the positional order ``createBackground`` reads.
    """
    from analysis.extra_functions import (calculate_healthcare_totals,
                                          calculate_healthcare_totals_2022,
                                          eldercare_share_of_social_work,
                                          eldercare_share_of_social_work_io)

    io_2022 = str(DST_IO).format(year="2022")
    if analysis_year == "2022":
        hc51, hc52, services, _ = calculate_healthcare_totals_2022(io_2022)
        alpha = eldercare_share_of_social_work_io(io_2022)
    else:
        hc51, hc52, services, _ = calculate_healthcare_totals(DK_UMAT)
        alpha = eldercare_share_of_social_work(DK_UMAT)

    to_meur = 1.0 / (DKK_PER_EUR_BY_YEAR[analysis_year] * 1000.0)

    drivhus = pd.read_csv(DRIVHUS, comment="#")
    dh = drivhus[drivhus["year"] == int(analysis_year)].set_index(
        ["industry_code", "emtype"])["value_kt_co2e"]
    direct_kt = (dh[("VQA", "GHGEXBIO")] + dh[("V870000", "GHGEXBIO")]
                 + alpha * dh[("V880000", "GHGEXBIO")]
                 - dh[("V860010", "N2O")])

    return pd.DataFrame(
        [dict(Index="Expenditure", Unit="MEUR",
              **{"HC service": float(services) * to_meur,
                 "Pharm": float(hc51) * to_meur,
                 "MedAppl": float(hc52) * to_meur}),
         dict(Index="Conversion", Unit="na",
              **{"HC service": 1.0, "Pharm": 1.0, "MedAppl": 1.0}),
         dict(Index="DirectEm", Unit="kt CO2e",
              **{"HC service": float(direct_kt), "Pharm": 0.0,
                 "MedAppl": 0.0})]
    ).set_index(["Index", "Unit"])


def expenditure_frame_table(
        analysis_years: tuple[str, ...] = ("2019", "2022")) -> pd.DataFrame:
    """Every analysis year's expenditure frame, in one long table.

    Parameters
    ----------
    analysis_years : tuple of str, optional
        Analysis years to build. Defaults to ``("2019", "2022")``.

    Returns
    -------
    pandas.DataFrame
        Columns ``analysis_year``, ``Index``, ``Unit``, ``HC service``,
        ``Pharm``, ``MedAppl``. Three rows per analysis year, in the
        positional order ``createBackground`` reads.
    """
    blocks = []
    for year in analysis_years:
        block = expenditure_frame(year).reset_index()
        block.insert(0, "analysis_year", year)
        blocks.append(block)
    return pd.concat(blocks, ignore_index=True)


def sector_group_table() -> pd.DataFrame:
    """The aggregate reporting group of every EXIOBASE industry.

    Read from the same ``classifications.xlsx`` sheet
    :mod:`analysis.main_2025` merges on, so the groups the sensitivity band
    reports are the groups the published contribution tables report.

    Returns
    -------
    pandas.DataFrame
        Columns ``exiobase_industry_code`` (the ``A_``-prefixed code the
        background labels carry, e.g. ``A_PARI``), ``exiobase_industry_name``
        and ``sector_group``.
    """
    table = pd.read_excel(CLASSIFICATIONS, sheet_name="disagg_ind", skiprows=5)
    frame = pd.DataFrame({
        "exiobase_industry_code": table["Code"].astype(str).str.strip(),
        "exiobase_industry_name": table["Description"].astype(str).str.strip(),
        "sector_group": table["AggDescription"].astype(str).str.strip()})
    return frame[frame.exiobase_industry_code != "nan"].reset_index(drop=True)


def main() -> None:
    """Build and write all three silver products."""
    for target in (SHARE_PATH, EXPENDITURE_PATH, SECTOR_GROUP_PATH):
        target.parent.mkdir(parents=True, exist_ok=True)

    share = domestic_share_table()
    share.to_csv(SHARE_PATH, index=False)
    for record in share.itertuples(index=False):
        role = ("cross-check" if record.dst_table_year
                == RORMOSE_CROSS_CHECK_YEAR
                else f"background {record.background_year}")
        print(f"  DST {record.dst_table_year}  phi {record.phi:.4f}  ({role})")
    print(f"written -> {SHARE_PATH}")

    frame = expenditure_frame_table()
    frame.to_csv(EXPENDITURE_PATH, index=False)
    print(f"written -> {EXPENDITURE_PATH}  ({len(frame)} rows)")

    groups = sector_group_table()
    groups.to_csv(SECTOR_GROUP_PATH, index=False)
    print(f"written -> {SECTOR_GROUP_PATH}  ({len(groups)} rows)")


if __name__ == "__main__":
    main()
