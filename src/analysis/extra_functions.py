"""Danish healthcare expenditure extraction from the Statistics Denmark use table.

Source file: ``data/bronze/dk_umat_2019.xlsx`` - Statistics Denmark detailed
supply-use tables 2019. Sheet ``Ubas`` holds the use table at BASIC PRICES in
1000 DKK (margins and product taxes are carried on the separate ``Umargins``
and ``Utaxes`` sheets), which is why no purchaser-to-basic price conversion is
applied downstream (Conversion = 1.0). Reading a different sheet would change
the price basis and silently break that assumption.

Scope definition (aligned with the manuscript's stated boundary - Steenmeijer
et al. 2022's expansive scope minus childcare):

* HC.5.1  Pharmaceuticals and other medical products  -> purpose 06112
* HC.5.2  Therapeutic appliances and equipment        -> purpose 06130
* Healthcare services                                 -> purposes 06200
  (out-patient), 06300 (hospital) and 12401 (retirement homes, day-care
  centres etc. = residential eldercare).

For each purpose ALL individual-consumption transaction columns present in
the table are summed: 3110 households, 3130 NPISH, 3141 marketed individual
government, 3142 non-market individual government. Collective government
consumption (3200) and GFCF carry different column codes and are excluded by
construction, consistent with Steenmeijer et al. (no capital formation).

Bug fixed 2026-09 (pre-revision code): the previous version enumerated
(transaction, purpose) pairs by hand and omitted the non-market government
column for 12401 (DKK 68.4 bn - ~90 % of eldercare spending) and the NPISH
column for 06300 (DKK 2.3 bn), while the manuscript claimed eldercare was
included. See docs/revision/defects_and_fixes.md, the 2019 baseline audit's E1.

``include_childcare=True`` additionally counts purpose 12402 (kindergartens,
creches etc.), matching the full Dutch "zorg en welzijn" boundary which also
covers childcare and youth care; it is OFF by default because the manuscript
scopes the study to health plus eldercare.
"""

import os

import pandas as pd

# Individual-consumption transaction blocks that constitute final consumption
# of the selected purposes. Order and exact strings follow the DST workbook.
_INDIVIDUAL_CONSUMPTION_TRANSACTIONS = (
    "Household consumption (Transaction code 3110)",
    "NPISH (Transaction code 3130)",
    "Marketed individual government consumption (Transaction code 3141)",
    "Non-market individual government consumption (Transaction code 3142)",
)

_PURPOSES_PHARMA = ("06112",)
_PURPOSES_APPLIANCES = ("06130",)
_PURPOSES_SERVICES = ("06200", "06300", "12401")
_PURPOSE_CHILDCARE = ("12402",)


def _load_use_table_basic_prices(file_path):
    """Read the basic-price use sheet with its 3-level column header."""
    df = pd.read_excel(file_path, sheet_name="Ubas", header=[0, 1, 2], engine="openpyxl")
    df.columns = pd.MultiIndex.from_tuples(
        [tuple(str(level).strip() for level in col) for col in df.columns]
    )
    return df


def _sum_purposes(df, purposes):
    """Sum all individual-consumption columns whose purpose code matches.

    Matching is on the exact purpose code (column level 2) AND on the
    transaction block (column level 0) so that industry columns with
    similar-looking codes (e.g. industry 060000) can never be caught.
    Returns (total, breakdown) where breakdown lists every column used.
    """
    total = 0.0
    breakdown = []
    for col in df.columns:
        transaction, description, code = col
        if code in purposes and transaction in _INDIVIDUAL_CONSUMPTION_TRANSACTIONS:
            value = float(df[col].sum())
            total += value
            breakdown.append(
                {
                    "purpose_code": code,
                    "purpose": description,
                    "transaction": transaction,
                    "value_kdkk": value,
                }
            )
    return total, breakdown


def calculate_healthcare_totals(file_path, include_childcare=False, include_eldercare=True):
    """Return (hc51, hc52, healthcare_services, breakdown) in 1000 DKK, basic prices.

    ``breakdown`` is a DataFrame listing every (purpose x transaction) column
    that entered the totals - written out by the pipeline as a provenance
    record so the expenditure scope is auditable.
    """
    df = _load_use_table_basic_prices(file_path)

    hc51_total, b1 = _sum_purposes(df, _PURPOSES_PHARMA)
    hc52_total, b2 = _sum_purposes(df, _PURPOSES_APPLIANCES)

    service_purposes = tuple(p for p in _PURPOSES_SERVICES
                             if include_eldercare or p != "12401")
    if include_childcare:
        service_purposes = service_purposes + _PURPOSE_CHILDCARE
    services_total, b3 = _sum_purposes(df, service_purposes)

    for row, cat in ((b1, "HC.5.1 Pharmaceuticals"), (b2, "HC.5.2 Appliances"),
                     (b3, "Healthcare services")):
        for entry in row:
            entry["category"] = cat
    breakdown = pd.DataFrame(b1 + b2 + b3)
    breakdown = breakdown[["category", "purpose_code", "purpose", "transaction", "value_kdkk"]]

    return hc51_total, hc52_total, services_total, breakdown


def calculate_healthcare_totals_2022(io_workbook_path, include_childcare=False,
                                     include_eldercare=True):
    """Health expenditure for 2022 from the PUBLIC Statistics Denmark IO workbook.

    The detailed purpose-coded use table (the 2019 route) is a custom extract;
    for 2022 the same three-category expenditure vector is built from the
    published 117-industry IO workbook (`input_output_en_2022.xlsx`), which is
    fully reproducible from StatBank. Basic prices: the workbook carries the
    industry-by-purpose flows at basic prices with product taxes and VAT as
    separate named rows - only rows whose first column is a numeric industry
    code (117 domestic + 117 import rows) are summed, which excludes the
    tax/VAT/value-added rows by construction.

    Classification note: the 2022 national accounts use the revised (COICOP
    2018-aligned) purpose codes - pharmaceuticals 06112 (unchanged),
    therapeutic/assistive appliances 06134 (was 06130), out-patient 06200,
    hospital services 06300 plus the new 06400 "Other hospital services",
    eldercare 13302 (was 12401), childcare 13301 (was 12402).

    Household consumption comes from the CP sheet (COICOP split of the single
    household column); NPISH and the two individual-government transactions
    from the IO sheet's purpose-labelled columns.
    """
    codes_pharma = {"06112"}
    codes_appl = {"06134", "06130"}
    # 06300 hospitals (gov/NPISH), 06340 hospital services (household-side code
    # in the CP sheet's COICOP-2018 numbering), 06400 other hospital services
    codes_services = {"06200", "06300", "06340", "06400"}
    if include_eldercare:
        codes_services = codes_services | {"13302"}
    if include_childcare:
        codes_services = codes_services | {"13301"}
    all_codes = codes_pharma | codes_appl | codes_services

    def _columns_by_code(df, wanted, transactions_only=None):
        """Map (block, description, code) columns whose code is wanted."""
        out = []
        block = None
        for j in range(df.shape[1]):
            top = str(df.iat[0, j]).strip()
            if "Transaction code" in top or top.startswith(("Collective government",
                                                           "Gross fixed capital", "Other uses")):
                block = top
            code = str(df.iat[2, j]).strip().split(".")[0]
            if code in wanted and block is not None:
                if transactions_only is None or any(t in block for t in transactions_only):
                    out.append((j, block, str(df.iat[1, j]).strip(), code))
        return out

    raw = pd.read_excel(io_workbook_path, sheet_name="IO", header=None, engine="openpyxl")
    cp = pd.read_excel(io_workbook_path, sheet_name="CP", header=None, engine="openpyxl")

    # basic-price purchase rows = rows whose first column is a numeric industry code
    def _basic_rows(df):
        col0 = df.iloc[:, 0].astype(str).str.strip()
        return col0.str.fullmatch(r"\d{5,6}")

    rows_io = _basic_rows(raw)
    rows_cp = _basic_rows(cp)

    individual_gov = ("3130", "3141", "3142")
    breakdown = []

    def _sum(df, rows, cols, source):
        total = 0.0
        for j, block, desc, code in cols:
            v = pd.to_numeric(df.loc[rows, j], errors="coerce").fillna(0).sum()
            total += float(v)
            breakdown.append({"purpose_code": code, "purpose": desc,
                              "transaction": block, "source_sheet": source,
                              "value_kdkk": float(v)})
        return total

    # household consumption: CP sheet columns (block header is on the IO sheet's
    # single household column; the CP sheet is entirely household consumption)
    cp_cols = []
    for j in range(1, cp.shape[1]):
        code = str(cp.iat[2, j]).strip().split(".")[0]
        if code in all_codes:
            cp_cols.append((j, "Household consumption (Transaction code 3110)",
                            str(cp.iat[1, j]).strip(), code))
    io_cols = _columns_by_code(raw, all_codes, transactions_only=individual_gov)

    def _cat_total(codes):
        return (
            _sum(cp, rows_cp, [c for c in cp_cols if c[3] in codes], "CP")
            + _sum(raw, rows_io, [c for c in io_cols if c[3] in codes], "IO")
        )

    hc51_total = _cat_total(codes_pharma)
    hc52_total = _cat_total(codes_appl)
    services_total = _cat_total(codes_services)

    bd = pd.DataFrame(breakdown)

    def _tag(code):
        if code in codes_pharma:
            return "HC.5.1 Pharmaceuticals"
        if code in codes_appl:
            return "HC.5.2 Appliances"
        return "Healthcare services"

    bd.insert(0, "category", bd["purpose_code"].map(_tag))
    return hc51_total, hc52_total, services_total, bd


def eldercare_share_of_social_work(file_path):
    """Share of industry 880000's individually consumed output serving eldercare.

    Industry 880000 (Social work activities without accommodation) produces both
    eldercare-type services (purpose 12401: home help, day centres for the
    elderly/disabled) and childcare (purpose 12402: kindergartens, creches).
    The expenditure scope includes 12401 but not 12402, so its DRIVHUS direct
    emissions are prorated by this share. The share is derived from the same
    supply-use tables as the expenditure vector: products supplied by 880000
    (sheet ``Vbas``) are traced to the 12401 vs 12402 individual-consumption
    columns of the basic-price use table (sheet ``Ubas``).
    """
    supply = pd.read_excel(file_path, sheet_name="Vbas", header=[0, 1, 2], engine="openpyxl")
    supply.columns = pd.MultiIndex.from_tuples(
        [tuple(str(level).strip() for level in col) for col in supply.columns]
    )
    use = _load_use_table_basic_prices(file_path)

    col_880000 = [c for c in supply.columns if c[2] == "880000"]
    if not col_880000:
        raise KeyError("Industry 880000 not found in the Vbas sheet")
    supplied = supply[col_880000[0]].fillna(0) > 0
    products = set(supply.iloc[:, 0].astype(str)[supplied])

    rows = use.iloc[:, 0].astype(str).isin(products)
    totals = {"12401": 0.0, "12402": 0.0}
    for col in use.columns:
        transaction, _description, code = col
        if code in totals and transaction in _INDIVIDUAL_CONSUMPTION_TRANSACTIONS:
            totals[code] += float(use.loc[rows, col].sum())
    return totals["12401"] / (totals["12401"] + totals["12402"])


def eldercare_share_of_social_work_io(io_workbook_path):
    """Eldercare share of industry 880000's individually consumed output, from
    the published IO table of the analysis year itself.

    Superior to deriving it from an earlier detailed SUT: the IO workbook is
    industry-by-purpose, so row 880000 gives that industry's OWN deliveries to
    eldercare (13302) and childcare (13301) directly, in the analysis year.
    Denmark 2022: 15.54 vs 34.72 bn DKK -> alpha = 0.3092 (the 2019 SUT-derived
    value was 0.4914, so carrying it forward would have overstated the share).
    """
    import numpy as np
    io = pd.read_excel(io_workbook_path, sheet_name="IO", header=None, engine="openpyxl")
    codes = io.iloc[:, 0].astype(str).str.strip()
    rows = np.flatnonzero((codes == "880000").values)
    if len(rows) == 0:
        raise KeyError("industry 880000 not found in the IO sheet")
    cols = {}
    for j in range(io.shape[1]):
        c = str(io.iat[2, j]).strip()
        if c in ("13301", "13302"):
            cols.setdefault(c, []).append(j)
    r = int(rows[0])
    val = {k: sum(float(pd.to_numeric(io.iat[r, j], errors="coerce") or 0.0) for j in v)
           for k, v in cols.items()}
    total = val.get("13301", 0.0) + val.get("13302", 0.0)
    if total <= 0:
        raise ValueError("no eldercare/childcare deliveries found for industry 880000")
    return val.get("13302", 0.0) / total


def eldercare_share_diagnostics(io_workbook_2019, io_workbook_2022, sut_2019):
    """Separate the method effect from the year effect in the eldercare share.

    Two constructions of alpha (the eldercare share of industry 880000's
    individually consumed output) were available:

      * detailed-SUT method (2019): products SUPPLIED BY 880000 traced through
        the use table to purposes 12401/12402. This attributes to 880000 the
        whole flow of every product it supplies, including the part supplied by
        other industries - it answers a product question, not an industry one.
      * IO-table method: industry 880000's OWN row read against the eldercare
        and childcare purpose columns. This is the correct object for
        allocating industry 880000's emissions.

    Applying the IO method to both years gives 0.3060 (2019) and 0.3092 (2022):
    stable to about 1 %. The gap to the SUT-derived 0.4914 is therefore a
    METHOD artefact, not a change between years - which is what justifies the
    switch. Alpha remains an allocation assumption (it presumes equal emission
    intensity per unit output across the two service types), and it is a small
    lever: 0.31 vs 0.49 moves the Danish healthcare climate footprint by
    10.9 kt CO2e, about 0.2 %.
    """
    return {
        "io_method_2019": eldercare_share_of_social_work_io(io_workbook_2019),
        "io_method_2022": eldercare_share_of_social_work_io(io_workbook_2022),
        "sut_method_2019": eldercare_share_of_social_work(sut_2019),
    }


def write_sheets_as_csv(frames: dict[str, "pd.DataFrame"], out_dir: str,
                        stem: str, index: bool = True) -> list[str]:
    """Write one CSV per sheet, lowercase, in place of a workbook.

    Gold publishes tabular data only, so a frame that used to become one sheet
    of a multi-sheet ``.xlsx`` becomes its own CSV instead. The sheet name is
    folded into the filename rather than kept as workbook structure, which is
    why it is lowercased and stripped of spaces and ``%`` here rather than left
    for a consumer to normalise.

    Parameters
    ----------
    frames : dict of str to pandas.DataFrame
        Sheet name to frame, in the order the sheets should be written.
    out_dir : str
        Destination folder.
    stem : str
        Filename stem; each sheet becomes ``<stem>_<sheet>.csv``.
    index : bool, default True
        Passed through to ``DataFrame.to_csv``. Some frames were built with a
        meaningful row index (written to the workbook with ``index=True``);
        others are already flat and were written with ``index=False``, and
        keeping the default here would add a spurious leading column of row
        numbers to those.

    Returns
    -------
    list of str
        Paths written, in order.

    Raises
    ------
    ValueError
        If two sheet names slug to the same filename (e.g. "A B" and "A-B"
        both become "a_b") - writing both would silently drop the first.
    """
    os.makedirs(out_dir, exist_ok=True)
    slugs: dict[str, str] = {}
    written = []
    for sheet, frame in frames.items():
        slug = (sheet.lower().replace(" ", "_").replace("%", "pct")
                .replace("-", "_").strip("_"))
        if slug in slugs:
            raise ValueError(
                f"write_sheets_as_csv: sheet names {slugs[slug]!r} and "
                f"{sheet!r} both slug to {slug!r} - would overwrite "
                f"{stem}_{slug}.csv"
            )
        slugs[slug] = sheet
        path = os.path.join(out_dir, f"{stem}_{slug}.csv")
        frame.to_csv(path, index=index)
        written.append(path)
    return written
