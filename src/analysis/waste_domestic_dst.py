# -*- coding: utf-8 -*-
"""Domestic waste footprint of Danish healthcare from Statistics Denmark's own accounts.

Why this exists
---------------
The waste indicator inherited from Steenmeijer et al. (2022) applies the 2011
hybrid EXIOBASE waste-supply account to the analysis year's monetary output.
Testing it against Denmark's own SEEA waste accounts shows it is not merely
out of date but a DIFFERENT CONCEPT: it is a total-residuals account in which
livestock manure and mining overburden dominate (74 % of the Danish total is
manure; 69 % of the healthcare "waste" footprint is mining overburden plus
manure). At the Danish health sector it overstates direct waste 3.1x against the
measured NACE Q account and 3.5x against the study's own boundary
(``analysis.waste_validation``, which computes both), and it
fails as an allocation key too - its 2011 Danish sector structure is
statistically uncorrelated with the measured 2011 structure (Pearson
r = -0.19). See analysis.waste_validation and the revision notes.

Denmark, uniquely, publishes IO-based waste multipliers on the same
117-industry classification as its IO tables (StatBank AFF1MU1N / AFF3MU1N,
2011-2023): direct waste intensity and the direct+indirect multiplier in
tonnes per million DKK. This module applies them to the healthcare final
demand to produce a DOMESTIC waste footprint that is WSR/SEEA-consistent,
with a 2022 reference year, and comparable with Eurostat and with hospital
green accounts.

Boundary
--------
The DST model is domestic-closed: every tonne it allocates to final demand is
physically generated in Denmark (verified: the seven top-level final-demand
categories sum exactly to national industry waste generation). It therefore
replaces the DOMESTIC half of the indicator only. The imported half has no
equivalent source - Eurostat's env_wasgen has no NACE Q and covers 29 of the
49 EXIOBASE regions - so it is reported separately, and explicitly labelled as
upstream solid residuals rather than waste.

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.waste_domestic_dst
"""

from __future__ import annotations

import json
import os
import subprocess

import pandas as pd

from paths import OUTPUT_DIR, SILVER_INPUT_DIR

API = "https://api.statbank.dk/v1/data"

# health expenditure purpose code -> DST 117-industry code
PURPOSE_TO_INDUSTRY = {
    "06300": "V860010", "06340": "V860010", "06400": "V860010",  # hospitals
    "06200": "V860020",                                          # practices
    "13302": "V870000",                                          # residential eldercare
    "13301": "V880000",                                          # childcare (scope variant)
    "06112": "V210000",                                          # pharmaceuticals
    "06134": "V320010", "06130": "V320010",                      # medical instruments
}
INDUSTRY_NAME = {"V860010": "Hospital activities",
                 "V860020": "Medical and dental practice activities",
                 "V870000": "Residential care activities",
                 "V880000": "Social work activities without accommodation",
                 "V210000": "Pharmaceuticals",
                 "V320010": "Manufacture of medical instruments, etc."}


def _fetch(table: str, variables: list[dict[str, object]]) -> list[list[str]]:
    """Fetch one StatBank table as CSV rows, via a POST to the StatBank API.

    Parameters
    ----------
    table : str
        StatBank table id, e.g. ``"AFF1MU1N"``.
    variables : list of dict
        StatBank variable selection, each ``{"code": ..., "values": [...]}``.

    Returns
    -------
    list of list of str
        Semicolon-split data rows, header row excluded.
    """
    body = {"table": table, "format": "CSV", "lang": "en", "variables": variables}
    out = subprocess.run(["curl", "-s", "-X", "POST", API, "-H", "Content-Type: application/json",
                          "-d", json.dumps(body)], capture_output=True, text=True).stdout
    lines = [l for l in out.strip().splitlines() if l.strip()]
    rows = [l.split(";") for l in lines[1:]]
    return rows


def multipliers(
    year: str, industries: list[str]
) -> dict[str, dict[str, float]]:
    """(direct intensity, direct+indirect multiplier, hazardous multiplier), t per m DKK.

    Parameters
    ----------
    year : str
        Four-digit calendar year to query.
    industries : list of str
        DST ``BRANCHE`` industry codes (e.g. ``"V860010"``) to fetch.

    Returns
    -------
    dict of str to dict
        Keyed by industry code; each value has keys ``"direct"``,
        ``"multiplier"`` and, where available, ``"hazardous"``, all in tonnes
        per million DKK.
    """
    res = {}
    tot = _fetch("AFF1MU1N", [{"code": "BRANCHE", "values": industries},
                              {"code": "AFFFRAK", "values": ["TOTAFFALDX"]},
                              {"code": "MULT", "values": ["AFF1INT", "AFF1MUL"]},
                              {"code": "PRISENHED", "values": ["V"]},
                              {"code": "Tid", "values": [str(year)]}])
    for r in tot:
        code = "V" + r[0].split()[0]
        kind = "direct" if "intensity" in r[2] else "multiplier"
        res.setdefault(code, {})[kind] = float(r[-1])
    haz = _fetch("AFF3MU1N", [{"code": "BRANCHE", "values": industries},
                              {"code": "FARLIG", "values": ["FARLIG"]},
                              {"code": "MULT", "values": ["AFF3MUL"]},
                              {"code": "PRISENHED", "values": ["V"]},
                              {"code": "Tid", "values": [str(year)]}])
    for r in haz:
        res.setdefault("V" + r[0].split()[0], {})["hazardous"] = float(r[-1])
    return res


def main() -> None:
    """Build the domestic waste footprint from Danish IO-based multipliers.

    Maps healthcare expenditure purpose codes to DST industries, fetches
    each industry's direct and direct+indirect waste multiplier (and
    hazardous-waste multiplier where available) from AFF1MU1N/AFF3MU1N, and
    applies them to expenditure to get direct, total and hazardous domestic
    waste in tonnes. Writes
    ``data/gold/results/05_waste_dst_accounts/waste_footprint_domestic_dst.csv``
    and prints the by-industry table and an implied-multiplier cross-check.
    Reads ``HC_ANALYSIS_YEAR`` from the environment (default ``"2022"``).

    Raises
    ------
    AssertionError
        If any expenditure row's purpose code is not in
        ``PURPOSE_TO_INDUSTRY``.
    """
    year = os.environ.get("HC_ANALYSIS_YEAR", "2022")
    exp = pd.read_csv(os.path.join(str(SILVER_INPUT_DIR),
                                   f"dk_expenditure_breakdown_{year}.csv"))
    exp["purpose_code"] = exp["purpose_code"].astype(str).str.zfill(5)
    exp["industry"] = exp["purpose_code"].map(PURPOSE_TO_INDUSTRY)
    missing = exp[exp["industry"].isna()]["purpose_code"].unique()
    assert len(missing) == 0, f"unmapped purpose codes: {missing}"
    # source values are 1000 DKK -> million DKK
    y = exp.groupby("industry")["value_kdkk"].sum() / 1e3

    mult = multipliers(year, list(y.index))
    rows = []
    for ind, spend in y.items():
        m = mult[ind]
        rows.append(dict(
            industry_code=ind.lstrip("V"), industry=INDUSTRY_NAME[ind],
            expenditure_m_dkk=spend,
            direct_intensity_t_per_mdkk=m["direct"],
            multiplier_t_per_mdkk=m["multiplier"],
            hazardous_multiplier_t_per_mdkk=m.get("hazardous"),
            direct_waste_t=spend * m["direct"],
            total_waste_t=spend * m["multiplier"],
            hazardous_waste_t=spend * m.get("hazardous", float("nan")),
        ))
    df = pd.DataFrame(rows).sort_values("total_waste_t", ascending=False)
    df.insert(0, "analysis_year", year)
    df["source"] = "Statistics Denmark AFF1MU1N / AFF3MU1N (SEEA waste accounts, IO-based)"
    df["boundary"] = "domestic (Danish waste generation); imports not covered"

    out = os.path.join(str(OUTPUT_DIR), "05_waste_dst_accounts", "waste_footprint_domestic_dst.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)

    tot_spend, tot_w = df.expenditure_m_dkk.sum(), df.total_waste_t.sum()
    print(df[["industry", "expenditure_m_dkk", "multiplier_t_per_mdkk",
              "direct_waste_t", "total_waste_t", "hazardous_waste_t"]].round(1).to_string(index=False))
    print(f"\nDomestic waste footprint of Danish healthcare, {year}:")
    print(f"  total          {tot_w / 1e3:10,.1f} kt   (direct {df.direct_waste_t.sum() / 1e3:,.1f} kt)")
    print(f"  hazardous      {df.hazardous_waste_t.sum() / 1e3:10,.1f} kt")
    print(f"  expenditure    {tot_spend / 1e3:10,.1f} bn DKK")
    print(f"  implied multiplier {tot_w / tot_spend:.3f} t per m DKK "
          f"(DST individual government consumption: 0.786 - independent check)")
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
