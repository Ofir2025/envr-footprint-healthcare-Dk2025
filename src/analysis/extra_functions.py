"""Danish healthcare expenditure extraction from the Statistics Denmark use table.

Source file: ``data/bronze/dk_umat_2019.xlsx`` — Statistics Denmark detailed
supply-use tables 2019. Sheet ``Ubas`` holds the use table at BASIC PRICES in
1000 DKK (margins and product taxes are carried on the separate ``Umargins``
and ``Utaxes`` sheets), which is why no purchaser-to-basic price conversion is
applied downstream (Conversion = 1.0). Reading a different sheet would change
the price basis and silently break that assumption.

Scope definition (aligned with the manuscript's stated boundary — Steenmeijer
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
column for 12401 (DKK 68.4 bn — ~90 % of eldercare spending) and the NPISH
column for 06300 (DKK 2.3 bn), while the manuscript claimed eldercare was
included. See docs/revision/bug_and_method_fixes.md.

``include_childcare=True`` additionally counts purpose 12402 (kindergartens,
creches etc.), matching the full Dutch "zorg en welzijn" boundary which also
covers childcare and youth care; it is OFF by default because the manuscript
scopes the study to health plus eldercare.
"""

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


def calculate_healthcare_totals(file_path, include_childcare=False):
    """Return (hc51, hc52, healthcare_services, breakdown) in 1000 DKK, basic prices.

    ``breakdown`` is a DataFrame listing every (purpose x transaction) column
    that entered the totals — written out by the pipeline as a provenance
    record so the expenditure scope is auditable.
    """
    df = _load_use_table_basic_prices(file_path)

    hc51_total, b1 = _sum_purposes(df, _PURPOSES_PHARMA)
    hc52_total, b2 = _sum_purposes(df, _PURPOSES_APPLIANCES)

    service_purposes = _PURPOSES_SERVICES + (_PURPOSE_CHILDCARE if include_childcare else ())
    services_total, b3 = _sum_purposes(df, service_purposes)

    for row, cat in ((b1, "HC.5.1 Pharmaceuticals"), (b2, "HC.5.2 Appliances"),
                     (b3, "Healthcare services")):
        for entry in row:
            entry["category"] = cat
    breakdown = pd.DataFrame(b1 + b2 + b3)
    breakdown = breakdown[["category", "purpose_code", "purpose", "transaction", "value_kdkk"]]

    return hc51_total, hc52_total, services_total, breakdown


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
