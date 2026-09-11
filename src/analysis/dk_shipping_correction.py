# -*- coding: utf-8 -*-
"""Reallocate Danish sea transport, following Statistics Denmark's diagnosis.

Rørmose Jensen & Iliev (2022, pp. 11-12) report that EXIOBASE sends 74 % of
Danish water-transport output to Danish *intermediate* use, against 9 % in the
Danish national accounts. The Danish-operated fleet carries world trade, not
Danish production, so the misallocation loads the emissions of one of the
world's largest merchant fleets onto Danish consumption.

This module reproduces their diagnosis on the model actually in use and applies
the correction they imply. On EXIOBASE v3.8.2 IOT_2022_ixi the Danish
sea-and-coastal-water-transport row delivers 73.6 % of its output to Danish
intermediate use - Statistics Denmark's 74 %, to the decimal.

The target share, and why it is read rather than quoted
-------------------------------------------------------
Rørmose Jensen & Iliev publish the national-accounts share for 2019 only, and
give no time series. Quoting their 9 % for every background year was a stopgap.
The share they quote is a ratio inside Statistics Denmark's own domestic
input-output table, so it can be read from that table directly, for each year
the study runs on:

.. math::

   \\phi(t) = \\frac{\\sum_{j=1}^{117} d_{\\mathrm{wt},j}(t)}
                   {x_{\\mathrm{wt}}(t)}

where :math:`d_{\\mathrm{wt},j}` is the delivery of row 500000 (Water
transport) of the ``DIO`` sheet to Danish industry :math:`j` and
:math:`x_{\\mathrm{wt}}` is that row's ``Total``. This module reads
:math:`\\phi` with :func:`dst_domestic_intermediate_share`. The values are

=======  =============
year     :math:`\\phi`
=======  =============
2016     0.077
2019     0.093
2022     0.065
=======  =============

The 2019 value is the validation, not an input: it reproduces Rørmose Jensen &
Iliev's 9 % to within 0.3 percentage points, which is what licenses reading the
other two years off the same table. :func:`dst_domestic_intermediate_share`
asserts it on every call and fails loudly if it drifts.

2022's lower share is real, not a parsing accident. The row's total output rose
from 225 bn DKK in 2019 to 337 bn DKK in 2022 in the container-freight boom, and
almost all of that growth was exported, so the domestic share falls even though
domestic deliveries barely moved.

**Currency.** :math:`\\phi` is a share computed entirely inside the Danish
table - deliveries to the 117 Danish industries over the row's own total output,
both in 1000 DKK - so it is dimensionless and the DKK cancels. No Danish crowns
enter the model: the share is applied to EXIOBASE's own row total, in M.EUR.
There is no exchange rate anywhere in this correction.

``HC_SHIPPING_PHI`` overrides the lookup with any float, for pinning a value or
for reverting to the published 9 % with one variable::

    HC_SHIPPING_PHI=0.09 HC_ANALYSIS_YEAR=2022 \\
        PYTHONPATH=src .venv/bin/python -m analysis.dk_shipping_correction

Correction
----------
The row's total output is left unchanged. That is a scope decision, not a claim
that the level is right: EXIOBASE's Danish sea-transport output is 0.23x the
national-accounts figure in 2022 and 0.63x in 2016
(`09_exiobase_release_diagnostics/dk_block_vs_national_accounts.csv`), and
Rørmose Jensen & Iliev report the same defect for 2019 (p. 12). Only the
*allocation* is corrected, because the allocation is what decides whether the
emissions land in Danish consumption; the level is left to a full
national-accounts coupling.

    target_dk_intermediate = phi * x_row
    Z[row, DK] *= target_dk_intermediate / Z[row, DK].sum()
    the released amount is added to exports, distributed over foreign final
    demand in proportion to each region's existing final demand

The distribution key is this repository's own choice, not either source's:
neither Rørmose Jensen & Iliev (2022) nor Schmidt & Merciai (2023) builds a
corrected EXIOBASE, so neither proposes one. Weighting by each foreign
final-demand column's total size is a neutral numeraire, not a measured trade
pattern. Booking the release to Y rather than to foreign intermediate use makes
it terminal - it cannot re-enter a supply chain and return to Denmark through
imports - which is conservative for the quantity measured but is a departure
from the national-accounts structure, where exported freight is largely an
intermediate input abroad.

Column balance is restored by crediting the released amount to the residual net
operating surplus (the last primary-input row) of the Danish industries that
stop buying the shipping, so that `sum(Z[:, j]) + VA_j = x_j` continues to hold.
Their outputs are the part of the Danish block not in dispute, and rescaling
them would change every Danish emission intensity e_i/x_i, so the offset belongs
in the accounting item that exists to absorb the gap between output and measured
costs. Note that this does not repair the shipping industry's own value added,
which Rørmose Jensen & Iliev report as negative (p. 12) and which measures
-493 M.EUR in 2016 and +271 M.EUR in 2022 on v3.8.2.

The uncorrected model is retained; both are reported.

Run, once per background year (``HC_ANALYSIS_YEAR`` selects it -- 2022 stays
2022, anything else, 2019 today, maps to 2016 -- exactly as everywhere else in
this package; HC_BACKGROUND_TAG must be unset, since this module writes the
``_snacship`` variant itself)::

    HC_ANALYSIS_YEAR=2022 PYTHONPATH=src .venv/bin/python -m analysis.dk_shipping_correction
    HC_ANALYSIS_YEAR=2019 PYTHONPATH=src .venv/bin/python -m analysis.dk_shipping_correction

Then, for either year, with the tag now set::

    HC_BACKGROUND_TAG=_snacship HC_ANALYSIS_YEAR=2022 \\
        .venv/bin/python -m analysis.main_2025

The sensitivity band (:func:`phi_sensitivity`) reads the published replication
for the same year, so it is run last, after ``analysis.main_2025``::

    HC_ANALYSIS_YEAR=2022 PYTHONPATH=src .venv/bin/python \\
        -m analysis.dk_shipping_correction --sensitivity
"""

from __future__ import annotations

import os
import pickle
import re
import tempfile
from typing import Sequence

import numpy as np
import pandas as pd

from analysis.build_dst_concordance import DST_IO
from analysis.constants import (ANALYSIS_YEAR, BACKGROUND_TAG, BACKGROUND_YEAR,
                                K_DK, N_FINAL_DEMAND, N_SECTORS, model_label)
from paths import MRIO_DIR, OUTPUT_DIR

FOLDER = "10_sea_transport_reallocation"

# This module always writes the "_snacship" variant itself (TAG below), so it
# must be run with HC_BACKGROUND_TAG unset -- setting it would make
# BACKGROUND_YEAR point the source read at the very file this run creates.
if BACKGROUND_TAG:
    raise SystemExit(
        "analysis.dk_shipping_correction writes the _snacship background "
        f"itself; run it with HC_BACKGROUND_TAG unset, not {BACKGROUND_TAG!r}")

#: Background year this run corrects: HC_ANALYSIS_YEAR maps onto it the same
#: way every other module in this package does (2022 stays 2022; anything
#: else -- 2019 today -- runs on the 2016 background). A 2019 analysis run
#: therefore corrects mrio2016.pkl, not a nonexistent mrio2019.pkl.
BG_YEAR = BACKGROUND_YEAR
TAG = "_snacship"

SECTOR_NAME = "Sea and coastal water transport"

#: The share Rørmose Jensen & Iliev (2022), Statistics Denmark, "Coupled
#: models", pp. 11-12, report for the Danish national accounts in 2019.
#:
#: It is no longer the target the correction applies. It survives for exactly
#: two purposes: the cross-check in
#: :func:`dst_domestic_intermediate_share`, which tests that this module's
#: parse of the Danish table reproduces the published figure, and the
#: verification rows, which record it beside the share actually used.
RORMOSE_2019_SHARE = 0.09

#: Year of the DST table whose share validates the parse. It is the one year
#: Rørmose Jensen & Iliev publish, and it is NOT a background year of this
#: study - the 2019 analysis runs on the 2016 background.
RORMOSE_CROSS_CHECK_YEAR = "2019"

#: How far the DST 2019 share may sit from :data:`RORMOSE_2019_SHARE` before
#: the cross-check fails. 0.005 is half a percentage point; the observed gap is
#: 0.003, so the check has roughly a factor of two of headroom and would still
#: catch a parse that picked up the wrong row, the wrong sheet or the import
#: block instead of the domestic one.
RORMOSE_TOLERANCE = 0.005

#: Sheet of the DST workbook holding the DOMESTIC input-output table. The
#: ``IO`` sheet is the total table, domestic plus imported; only the domestic
#: one measures what share of a Danish industry's output Danish industries
#: actually buy, which is the quantity Rørmose Jensen & Iliev compare EXIOBASE
#: against.
DST_SHEET = "DIO"

#: DST DB07 code of Water transport, the Danish counterpart of EXIOBASE's
#: :data:`SECTOR_NAME`.
WATER_TRANSPORT_CODE = "500000"

#: Row label opening the Danish-production block of the ``DIO`` sheet, and the
#: one opening the Imports block that follows it. The 117 product codes repeat
#: in both, so the domestic row has to be located between them.
DST_DOMESTIC_BLOCK = "Danish production"
DST_IMPORT_BLOCK = "Imports"

#: Environment variable pinning the target share by hand, for a sensitivity run
#: or to revert to the published 9 % with one variable. Documented in the
#: module docstring.
PHI_ENV = "HC_SHIPPING_PHI"

#: Target shares the sensitivity band reports. It brackets both DST values
#: (0.077 for 2016, 0.065 for 2022), the published 0.09, and a range wide
#: enough on either side that a reader can see the footprint's curvature
#: rather than only its slope at the applied point.
PHI_GRID: tuple[float, ...] = (0.05, 0.065, 0.077, 0.09, 0.10, 0.125, 0.15)


def _dio_domestic_intermediate_share(year: str) -> float:
    """Raw share of Water transport output bought by Danish industries.

    Reads the ``DIO`` (domestic input-output) sheet of Statistics Denmark's
    published table for one year and divides row 500000's deliveries to the
    117 Danish industries by that row's own total output. Both are in 1000
    DKK, so the quotient is dimensionless.

    The workbook is located through the same :data:`DST_IO` path constant
    :mod:`analysis.build_dst_concordance` uses, and parsed with that module's
    conventions: ``header=None``, the six-digit industry codes taken from row
    2 with ``re.fullmatch(r"\\d{6}", code)``, the row labels from column A, and
    the banner from row 0.

    Parameters
    ----------
    year : str
        Reference year of the published Danish input-output table, e.g.
        ``"2016"``.

    Returns
    -------
    float
        The domestic intermediate share, between 0 and 1.

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
    return float(np.nansum(deliveries) / total)


def dst_domestic_intermediate_share(year: str) -> float:
    """Target share phi for one background year, from the Danish table.

    This is the quantity Rørmose Jensen & Iliev (2022, pp. 11-12) quote as 9 %
    for 2019: the fraction of Danish water-transport output that Danish
    industries buy as intermediate input, in Statistics Denmark's own domestic
    input-output table. Reading it per year replaces quoting their single
    published year for every year of the study.

    Every call re-reads the 2019 table and asserts that it reproduces
    :data:`RORMOSE_2019_SHARE` to within :data:`RORMOSE_TOLERANCE`. That is the
    validation of this parse against the only published figure, and it is
    inside the function rather than in a test so that no run can apply a share
    this module has not just proved it reads correctly.

    Units
    -----
    phi is dimensionless. It is a ratio of two quantities inside the DKK table,
    so the crowns cancel; it is applied to EXIOBASE's own row total, which is
    in M.EUR. No currency conversion takes place anywhere in this correction.

    Parameters
    ----------
    year : str
        Background year of the run, ``"2016"`` or ``"2022"``. The DST table
        year IS the background year: the 2019 analysis runs on the 2016
        background (see :data:`BG_YEAR`) and therefore takes the 2016 share.

    Returns
    -------
    float
        phi for that year: 0.077 for 2016, 0.065 for 2022.

    Raises
    ------
    AssertionError
        If the 2019 table does not reproduce the published 9 %.

    Examples
    --------
    >>> round(dst_domestic_intermediate_share("2016"), 3)  # doctest: +SKIP
    0.077
    """
    check = _dio_domestic_intermediate_share(RORMOSE_CROSS_CHECK_YEAR)
    if abs(check - RORMOSE_2019_SHARE) > RORMOSE_TOLERANCE:
        raise AssertionError(
            f"cross-check failed: the DST {DST_SHEET} table for "
            f"{RORMOSE_CROSS_CHECK_YEAR} gives a domestic intermediate share "
            f"of {check:.4f}, which is more than {RORMOSE_TOLERANCE} from the "
            f"{RORMOSE_2019_SHARE} Rørmose Jensen & Iliev (2022, pp. 11-12) "
            f"report. Either the parse is wrong or the published table has "
            f"been revised; do not apply a share this has not validated.")
    if str(year) == RORMOSE_CROSS_CHECK_YEAR:
        return check
    return _dio_domestic_intermediate_share(str(year))


def applied_target_share(year: str) -> tuple[float, str]:
    """The share this run actually applies, and where it came from.

    Parameters
    ----------
    year : str
        Background year, ``"2016"`` or ``"2022"``.

    Returns
    -------
    tuple of (float, str)
        phi, and a provenance string: ``"DST DIO <year>"`` when read from the
        Danish table, ``"HC_SHIPPING_PHI override"`` when
        :data:`PHI_ENV` pins it.

    Raises
    ------
    ValueError
        If ``HC_SHIPPING_PHI`` is set to something that is not a float in
        ``(0, 1)``.
    """
    override = os.environ.get(PHI_ENV, "").strip()
    if override:
        try:
            phi = float(override)
        except ValueError as exc:
            raise ValueError(f"{PHI_ENV}={override!r} is not a float") from exc
        if not 0.0 < phi < 1.0:
            raise ValueError(f"{PHI_ENV}={phi} is not a share in (0, 1)")
        return phi, f"{PHI_ENV} override"
    return dst_domestic_intermediate_share(str(year)), f"DST {DST_SHEET} {year}"


# ---------------------------------------------------------------------------
# Sensitivity band
#
# The correction's one free parameter is phi. Reading it from the Danish table
# fixes its value but does not say how much the answer depends on it, and a
# reader who prefers Rørmose Jensen & Iliev's published 9 % for every year, or
# who doubts the 2022 freight-boom denominator, is entitled to see what that
# choice is worth in kt. This band runs the whole correction at each phi and
# reports the footprint it produces, writing no pickle and touching no
# published result.
# ---------------------------------------------------------------------------

#: Which analysis year each background year serves, the inverse of the mapping
#: :data:`analysis.constants.BACKGROUND_YEAR` applies. The expenditure vector
#: is an analysis-year quantity, so the band needs both.
ANALYSIS_YEAR_FOR_BACKGROUND: dict[str, str] = {"2016": "2019", "2022": "2022"}

#: Danmarks Nationalbank annual average DKK per euro, as
#: ``analysis.main_2025.DKK_PER_EUR_BY_YEAR``. Restated here because
#: :mod:`analysis.main_2025` is a script: importing it would run the whole
#: replication. :func:`phi_sensitivity` asserts its expenditure vector against
#: the published ``table_01.csv``, so a drift between the two copies fails the
#: run rather than passing silently.
DKK_PER_EUR_BY_YEAR: dict[str, float] = {"2019": 7.4661, "2022": 7.4396}

#: Sector group, in EXIOBASE's own ``classifications.xlsx`` aggregation, whose
#: share of the footprint the band reports. It is the group the manuscript
#: discusses and the one the correction acts on.
TRANSPORT_GROUP = "Transport"

#: Where the band is published.
SENSITIVITY_CSV = "phi_sensitivity_{background_year}.csv"


def _cbs_expenditure_frame(analysis_year: str) -> pd.DataFrame:
    """Rebuild the expenditure and direct-emission frame the background reads.

    ``functions_2025.createBackground`` consumes a three-row, three-column
    frame indexed by ``(Index, Unit)``: expenditure on health-care services,
    pharmaceuticals and appliances in M.EUR, the basic-price conversion (1.0,
    because both Danish expenditure routes are already at basic prices), and
    the sector's direct greenhouse-gas emissions in kt. This rebuilds it with
    the same :mod:`analysis.extra_functions` routines
    :mod:`analysis.main_2025` uses, rather than reading the silver copy, which
    holds whichever analysis year ran last.

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
    from paths import BRONZE_DIR

    io_2022 = BRONZE_DIR / "input_output" / "2016_2022" / "input_output_en_2022.xlsx"
    if analysis_year == "2022":
        hc51, hc52, services, _ = calculate_healthcare_totals_2022(io_2022)
        alpha = eldercare_share_of_social_work_io(io_2022)
    else:
        hc51, hc52, services, _ = calculate_healthcare_totals(
            BRONZE_DIR / "dk_umat_2019.xlsx")
        alpha = eldercare_share_of_social_work(BRONZE_DIR / "dk_umat_2019.xlsx")

    to_meur = 1.0 / (DKK_PER_EUR_BY_YEAR[analysis_year] * 1000.0)

    drivhus = pd.read_csv(BRONZE_DIR / "dk_direct_emissions_drivhus.csv",
                          comment="#")
    dh = drivhus[drivhus["year"] == int(analysis_year)].set_index(
        ["industry_code", "emtype"])["value_kt_co2e"]
    direct_kt = (dh[("VQA", "GHGEXBIO")] + dh[("V870000", "GHGEXBIO")]
                 + alpha * dh[("V880000", "GHGEXBIO")]
                 - dh[("V860010", "N2O")])

    frame = pd.DataFrame(
        [dict(Index="Expenditure", Unit="MEUR",
              **{"HC service": float(services) * to_meur,
                 "Pharm": float(hc51) * to_meur,
                 "MedAppl": float(hc52) * to_meur}),
         dict(Index="Conversion", Unit="na",
              **{"HC service": 1.0, "Pharm": 1.0, "MedAppl": 1.0}),
         dict(Index="DirectEm", Unit="kt CO2e",
              **{"HC service": float(direct_kt), "Pharm": 0.0, "MedAppl": 0.0})]
    ).set_index(["Index", "Unit"])
    return frame


def _sector_group_by_code() -> dict[str, str]:
    """The aggregate sector group of every EXIOBASE industry code.

    Read from the same ``classifications.xlsx`` sheet
    :mod:`analysis.main_2025` merges on, so the groups the band reports are
    the groups the published contribution tables report.

    Returns
    -------
    dict of str to str
        EXIOBASE industry code, e.g. ``"i61.a"``, to its aggregate group name,
        e.g. ``"Transport"``.
    """
    from paths import EXIOBASE_DIR

    table = pd.read_excel(EXIOBASE_DIR / "classifications.xlsx",
                          sheet_name="disagg_ind", skiprows=5)
    return dict(zip(table["Code"].astype(str).str.strip(),
                    table["AggDescription"].astype(str).str.strip()))


def _published_non_mrio_additions(analysis_year: str) -> tuple[float, float]:
    """The phi-independent items the replication adds outside the MRIO.

    ``table_01.csv`` of the corresponding Eriksen variant carries the three
    bottom-up climate items - anaesthetic gases, pMDI propellants and private
    travel - that :mod:`analysis.main_2025` appends to the input-output result.
    None of them depends on phi: they are register and survey quantities. They
    are read from the published table rather than recomputed, so the band adds
    exactly what the replication adds.

    Parameters
    ----------
    analysis_year : str
        ``"2019"`` or ``"2022"``.

    Returns
    -------
    tuple of (float, float)
        The bottom-up total in kt CO2-eq, and the published grand total of the
        same table, which :func:`phi_sensitivity` uses to verify itself.
    """
    path = os.path.join(str(OUTPUT_DIR), "01_eriksen_replication",
                        f"{analysis_year}_shipping_corrected", "table_01.csv")
    table = pd.read_csv(path, index_col=0)
    column = "Global warming (ktCO2eq)"
    bottom_up = float(sum(
        table.loc[row, column]
        for row in ("Release of anaesthetic gases",
                    "Release of pMDI propellants", "Private travel")))
    return bottom_up, float(table.loc["Total", column])


def phi_sensitivity(background_year: str,
                    phis: Sequence[float] = PHI_GRID,
                    write: bool = True) -> pd.DataFrame:
    """Run the sea-transport correction across a band of target shares.

    For each phi the Danish sea-transport row is reallocated exactly as
    :func:`main` reallocates it, the Leontief system is solved again on the
    corrected technical coefficients, and the Danish health-care climate
    footprint is evaluated on the study's own demand vector. Nothing is
    written to the background: no pickle is produced, and the published
    ``_snacship`` variants are neither read nor touched.

    How it reuses the replication
    -----------------------------
    The demand vector and the characterised intensity matrix come from
    ``functions_2025.createBackground`` on the UNCORRECTED background, with the
    expenditure frame rebuilt by :func:`_cbs_expenditure_frame` from the same
    :mod:`analysis.extra_functions` routines :mod:`analysis.main_2025` calls.
    The contribution is ``functions_2025.calc_contrib``. The bottom-up items
    outside the input-output model are read from the published
    ``table_01.csv`` (:func:`_published_non_mrio_additions`), because they do
    not depend on phi.

    Because the correction only rescales one row block of ``Z``, its effect on
    the coefficients is exactly a rescaling of the same row block of ``A``,

    .. math::

       a^{\\phi}_{\\mathrm{wt},j} = a_{\\mathrm{wt},j}\\,
           \\frac{\\phi\\, x_{\\mathrm{wt}}}
                {\\sum_{k \\in \\mathrm{DK}} z_{\\mathrm{wt},k}}, \\quad
       j \\in \\mathrm{DK}

    and on the demand vector exactly the same rescaling of the health
    industry's own purchase of Danish sea transport. The export leg of the
    correction lands in foreign final demand, which the health-care footprint
    never reads, so it cannot affect these numbers. The band is therefore the
    correction itself, not an approximation of it, and the run is verified
    against the published total at the applied phi before anything is written.

    Parameters
    ----------
    background_year : str
        ``"2016"`` or ``"2022"``.
    phis : sequence of float, optional
        Target shares to evaluate. Defaults to :data:`PHI_GRID`. The share the
        run actually applies is always evaluated as well, whether or not it
        falls on a grid point, because the verification below needs it.
    write : bool, optional
        Whether to publish the table. True by default.

    Returns
    -------
    pandas.DataFrame
        One row per phi, with columns ``phi``, ``phi_source``,
        ``released_meur``, ``footprint_climate_kt``, ``transport_share_pct``,
        ``background_year`` and ``model``.

    Raises
    ------
    RuntimeError
        If the run does not reproduce the published grand total at the applied
        phi to within 0.01 %, which would mean the band is not measuring the
        same model the replication publishes.
    """
    from analysis.functions_2025 import calc_contrib, createBackground

    background_year = str(background_year)
    analysis_year = ANALYSIS_YEAR_FOR_BACKGROUND[background_year]
    phi_applied, phi_applied_source = applied_target_share(background_year)

    # x_row and the uncorrected Danish intermediate total, as main() measured
    # them on the pickle itself. Reading them here rather than re-opening a
    # 1.1 GB pickle keeps the band cheap and, more to the point, makes it use
    # the same two numbers the published correction used.
    diag = pd.read_csv(os.path.join(str(OUTPUT_DIR), FOLDER,
                                    "shipping_reallocation_diagnostics.csv"))
    diag = diag[diag.background_year.astype(str) == background_year]
    if diag.empty:
        raise RuntimeError(
            f"no rows for background year {background_year} in "
            f"shipping_reallocation_diagnostics.csv; run "
            f"analysis.dk_shipping_correction for that year first")

    def _q(name: str) -> float:
        return float(diag.loc[diag.quantity == name, "value"].iloc[0])

    x_row = _q("DK sea transport total output")
    before = _q("to DK intermediate use, before")

    # The grid always carries the applied share as well, whether or not it
    # happens to fall on a round grid point, so the run can be verified
    # against the published total before it is published.
    evaluated = sorted({round(float(p), 10) for p in phis} | {round(phi_applied, 10)})

    mdir = str(MRIO_DIR) + os.sep
    with tempfile.TemporaryDirectory() as scratch:
        # createBackground persists the assembled background only when none is
        # on disk. A placeholder in a scratch directory keeps that write from
        # happening at all, so this function writes no pickle anywhere.
        placeholder = os.path.join(
            scratch, f"gddz_background_information_{background_year}.pkl")
        open(placeholder, "wb").close()
        bg = createBackground(mdir, _cbs_expenditure_frame(analysis_year),
                              scratch + os.sep, background_year)

    industries = [str(v).strip()
                  for v in bg["label"]["industry"]["Name"].tolist()]
    codes = [str(v).strip()
             for v in bg["label"]["industry"].reset_index()["CodeTxt"].tolist()]
    sea = industries.index(SECTOR_NAME)
    row = K_DK * N_SECTORS + sea
    dk = slice(K_DK * N_SECTORS, (K_DK + 1) * N_SECTORS)

    groups = _sector_group_by_code()
    transport = np.tile(
        np.array([groups.get(code) == TRANSPORT_GROUP for code in codes]), 49)
    if not transport.any():
        raise RuntimeError(f"no EXIOBASE industry maps to the "
                           f"{TRANSPORT_GROUP!r} group; the classification "
                           f"sheet and the background labels disagree")

    A = bg["A"]
    base_block = A[row, dk].copy()
    ystim = bg["Ystim"].copy()
    base_ystim_sea = ystim[row, 1:].copy()
    climate_row = bg["B"][:1, :].copy()
    bottom_up, published_total = _published_non_mrio_additions(analysis_year)
    direct_kt = float(bg["Hstim"][0, 0])
    non_mrio = bottom_up + direct_kt

    # Only A, Ystim, B and the constants above are still needed; the
    # uncorrected Leontief inverse is half a gigabyte and is about to be
    # replaced once per phi.
    for key in ("L", "H", "Y", "Q", "Vstim"):
        bg.pop(key, None)

    eye = np.arange(A.shape[0])
    records = []
    for phi in evaluated:
        scale = phi * x_row / before
        A[row, dk] = base_block * scale
        ystim[row, 1:] = base_ystim_sea * scale
        ystim[row, 0] = ystim[row, 1:].sum()

        system = -A
        system[eye, eye] += 1.0
        leontief = np.linalg.inv(system)
        del system
        contribution = calc_contrib(climate_row, leontief,
                                    ystim[:, :1])[0][:, 0]
        del leontief

        mrio_kt = float(contribution.sum())
        transport_kt = float(contribution[transport].sum())
        total_kt = mrio_kt + non_mrio
        applied = abs(phi - round(phi_applied, 10)) < 1e-12
        records.append(dict(
            phi=float(phi),
            phi_source=(f"{phi_applied_source} (applied)" if applied
                        else "sensitivity grid"),
            released_meur=before - phi * x_row,
            footprint_climate_kt=total_kt,
            transport_share_pct=100.0 * transport_kt / total_kt,
            background_year=background_year,
            model=model_label(background_year)))
        print(f"  phi {phi:.4f}  released {before - phi * x_row:10.1f} M.EUR  "
              f"footprint {total_kt:9.2f} kt  transport "
              f"{100.0 * transport_kt / total_kt:6.2f} %")

    table = pd.DataFrame(records)
    A[row, dk] = base_block

    # Self-verification. The applied phi must reproduce the grand total the
    # replication publishes; if it does not, this band is measuring a
    # different model and must not be published.
    got = float(table.loc[table.phi_source.str.endswith("(applied)"),
                          "footprint_climate_kt"].iloc[0])
    gap = abs(got - published_total) / published_total
    if gap > 1e-4:
        raise RuntimeError(
            f"the band gives {got:.2f} kt at the applied phi "
            f"{phi_applied:.5f}, against {published_total:.2f} kt in the "
            f"published table_01.csv for {analysis_year} "
            f"({100 * gap:.4f} % apart). Re-run "
            f"analysis.main_2025 for that year before publishing the band.")
    print(f"  verified against the published total: {got:.2f} vs "
          f"{published_total:.2f} kt ({100 * gap:.5f} % apart)")

    if write:
        out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(
            out_dir, SENSITIVITY_CSV.format(background_year=background_year))
        table.to_csv(path, index=False)
        print(f"written -> {path}")
    return table


def _upsert_by_background_year(new: pd.DataFrame, path: str) -> pd.DataFrame:
    """Replace this run's rows in an existing table, keeping other years' rows.

    Parameters
    ----------
    new : pandas.DataFrame
        Rows for the background year this run just computed. Must carry a
        ``background_year`` column.
    path : str
        Where the table is, or will be, written.

    Returns
    -------
    pandas.DataFrame
        ``new`` merged with whatever the file on disk holds for OTHER
        background years, so running this module for 2019 does not erase the
        2022 rows an earlier run wrote, and running it again for 2022 does
        not erase 2019's.
    """
    if not os.path.exists(path):
        return new
    old = pd.read_csv(path)
    if "background_year" not in old.columns:
        # A pre-upsert file from a single-year run holds only that run's own
        # background year, so it is superseded rather than merged.
        return new
    this_year = str(new["background_year"].iloc[0])
    old = old[old["background_year"].astype(str) != this_year]
    return pd.concat([old, new], ignore_index=True)


def main() -> None:
    """Reallocate Danish sea transport on the configured background year.

    Reads ``mrio<BG_YEAR>.pkl`` and writes ``mrio<BG_YEAR>_snacship.pkl`` /
    ``leontief<BG_YEAR>_snacship.pkl`` beside it, plus this layer's two gold
    diagnostics tables. Both tables are upserted by ``background_year`` (see
    :func:`_upsert_by_background_year`), so a run on one background year does
    not erase another's rows -- 2016 and 2022 sit side by side, and a reader
    can see directly whether the 74 % misallocation Rørmose Jensen & Iliev
    (2022) report for 2019 also holds on the 2016 background this study's
    2019 replication actually runs on.

    The target share is :func:`applied_target_share` for the background year:
    read from Statistics Denmark's domestic input-output table, or pinned by
    ``HC_SHIPPING_PHI``. Both the share and its provenance are written to every
    row of the diagnostics table, beside the 2019 cross-check against the one
    share Rørmose Jensen & Iliev publish.
    """
    out_dir = os.path.join(OUTPUT_DIR, FOLDER)
    os.makedirs(out_dir, exist_ok=True)
    mdir = str(MRIO_DIR) + os.sep

    with open(f"{mdir}mrio{BG_YEAR}.pkl", "rb") as fh:
        m = pickle.load(fh)
    inds = list(m["label"]["industry"]["Name"])
    sea = inds.index(SECTOR_NAME)
    row = K_DK * N_SECTORS + sea

    Z, Y, x, V = m["Z"].copy(), m["Y"].copy(), m["x"].copy(), m["V"].copy()
    dk = slice(K_DK * N_SECTORS, (K_DK + 1) * N_SECTORS)
    dk_fd = slice(K_DK * N_FINAL_DEMAND, (K_DK + 1) * N_FINAL_DEMAND)

    phi, phi_source = applied_target_share(BG_YEAR)
    rormose_check = dst_domestic_intermediate_share(RORMOSE_CROSS_CHECK_YEAR)
    print(f"phi = {phi:.5f} ({phi_source}); DST {DST_SHEET} "
          f"{RORMOSE_CROSS_CHECK_YEAR} cross-check {rormose_check:.5f} against "
          f"Rørmose Jensen & Iliev {RORMOSE_2019_SHARE}")

    x_row = float(x[row, 0])
    before = float(Z[row, dk].sum())
    target = phi * x_row
    if before <= target:
        raise SystemExit(f"no correction needed: DK intermediate share is "
                         f"{100 * before / x_row:.1f} %")

    released = before - target
    scale = target / before
    removed_by_industry = Z[row, dk] * (1.0 - scale)
    Z[row, dk] *= scale

    # exports: distribute over foreign final demand in proportion to each
    # region's existing total final demand, so no region is singled out
    fd_tot = Y.sum(axis=0)
    mask = np.ones(Y.shape[1], dtype=bool)
    mask[dk_fd] = False
    w = np.where(mask, fd_tot, 0.0)
    w = w / w.sum()
    Y[row, :] += released * w

    # column balance: credit the released amount to the value added of the
    # Danish industries that stop buying the shipping
    V[-1, dk] += removed_by_industry

    # rebuild A and L on the corrected Z
    xs = x[:, 0].copy()
    inv = np.divide(1.0, xs, out=np.zeros_like(xs), where=xs > 0)
    A = Z * inv[np.newaxis, :]
    L = np.linalg.inv(np.eye(A.shape[0]) - A)

    m["Z"], m["Y"], m["A"], m["V"] = Z, Y, A, V
    with open(f"{mdir}mrio{BG_YEAR}{TAG}.pkl", "wb") as fh:
        pickle.dump(m, fh)
    with open(f"{mdir}leontief{BG_YEAR}{TAG}.pkl", "wb") as fh:
        pickle.dump(L, fh)

    # verification
    resid_row = float(abs(Z[row, :].sum() + Y[row, :].sum() - x_row))
    col = Z[:, dk].sum(axis=0) + V[:, dk].sum(axis=0)
    resid_col = float(np.max(np.abs(col - xs[dk])))
    after = float(Z[row, dk].sum())

    # Year-aware, so a 2019 (2016-background) run does not print "IOT_2022_ixi"
    # against numbers it never touched. model_label() strips BACKGROUND_TAG,
    # which is guaranteed empty here (asserted above), so this is exactly
    # "EXIOBASE v3.8.2 IOT_<BG_YEAR>_ixi" with no variant suffix -- the
    # UNCORRECTED background this run reads, before its own correction.
    source_label = model_label(BG_YEAR)
    rows = [
        dict(quantity="DK sea transport total output", value=x_row, unit="M.EUR",
             source=source_label),
        dict(quantity="to DK intermediate use, before", value=before,
             unit="M.EUR", source=source_label),
        dict(quantity="share to DK intermediate use, before",
             value=100 * before / x_row, unit="%",
             source="reproduces Rørmose Jensen & Iliev 2022 (74 % for 2019)"),
        dict(quantity="share to DK intermediate use, after",
             value=100 * after / x_row, unit="%",
             source=f"target read from {phi_source}"),
        dict(quantity="phi applied (target DK intermediate share)",
             value=phi, unit="share (dimensionless)", source=phi_source),
        dict(quantity=f"DST {DST_SHEET} {RORMOSE_CROSS_CHECK_YEAR} domestic "
                      f"intermediate share (cross-check)",
             value=rormose_check, unit="share (dimensionless)",
             source=f"Statistics Denmark, input_output_en_"
                    f"{RORMOSE_CROSS_CHECK_YEAR}.xlsx, sheet {DST_SHEET}"),
        dict(quantity="Rørmose Jensen & Iliev 2022 published share (2019)",
             value=RORMOSE_2019_SHARE, unit="share (dimensionless)",
             source="Rørmose Jensen & Iliev 2022, Statistics Denmark, "
                    "'Coupled models', pp. 11-12"),
        dict(quantity="cross-check gap, DST minus published",
             value=rormose_check - RORMOSE_2019_SHARE,
             unit="share (dimensionless)",
             source=f"passes while within {RORMOSE_TOLERANCE}"),
        dict(quantity="output reallocated to exports", value=released,
             unit="M.EUR", source="this correction"),
        dict(quantity="row balance residual after correction", value=resid_row,
             unit="M.EUR", source="verification"),
        dict(quantity="max column balance residual, DK block",
             value=resid_col, unit="M.EUR", source="verification"),
    ]
    df = pd.DataFrame(rows)
    df.insert(0, "country_producing", "DNK")
    df.insert(1, "sector_producing", SECTOR_NAME)
    # Every row carries the share the run applied and where it came from, so a
    # reader picking one row out of the file still knows which phi produced it.
    df["phi_applied"] = phi
    df["phi_source"] = phi_source
    df["rormose_2019_cross_check"] = rormose_check
    # Which background year (and which analysis year selected it) every row
    # below describes -- required so a reader comparing this file across runs
    # can tell the 2016 rows from the 2022 rows without cross-referencing
    # anything else.
    df.insert(2, "background_year", BG_YEAR)
    df.insert(3, "analysis_year", ANALYSIS_YEAR)
    diag_path = os.path.join(out_dir, "shipping_reallocation_diagnostics.csv")
    df = _upsert_by_background_year(df, diag_path)
    df.to_csv(diag_path, index=False)

    # which Danish industries lose the phantom shipping input
    top = pd.DataFrame(dict(
        country_producing="DNK", sector_producing=SECTOR_NAME,
        background_year=BG_YEAR, analysis_year=ANALYSIS_YEAR,
        country_consuming="DNK", sector_consuming=inds,
        value=removed_by_industry, unit="M.EUR"))
    top = top[top.value > 0].sort_values("value", ascending=False)
    top_path = os.path.join(out_dir,
                            "phantom_shipping_input_removed_by_industry.csv")
    top = _upsert_by_background_year(top, top_path)
    top.to_csv(top_path, index=False)

    this_run = df[df.background_year.astype(str) == str(BG_YEAR)]
    print(f"background year {BG_YEAR} (analysis year {ANALYSIS_YEAR})")
    print(this_run.to_string(index=False))
    print(f"\nrow balance residual {resid_row:.3e} | column residual "
          f"{resid_col:.3e} M.EUR")
    print("\nDanish industries losing the largest phantom shipping input:")
    print(top[top.background_year.astype(str) == str(BG_YEAR)]
          .head(10)[["sector_consuming", "value"]].to_string(index=False))
    print(f"\nwritten -> {out_dir}")
    print(f"background -> mrio{BG_YEAR}{TAG}.pkl, leontief{BG_YEAR}{TAG}.pkl")


if __name__ == "__main__":
    import sys

    if "--sensitivity" in sys.argv[1:]:
        print(f"phi sensitivity band, background year {BG_YEAR}")
        phi_sensitivity(BG_YEAR)
    else:
        main()
