# -*- coding: utf-8 -*-
"""Test the inherited waste extension against Denmark's own waste accounts.

The waste indicator is inherited from Steenmeijer et al. (2022): absolute waste
supply by industry from the 2011 hybrid EXIOBASE MR-HSUT, divided by the
analysis year's monetary output. Denmark publishes SEEA waste accounts on the
same 117-industry classification as its IO tables (StatBank AFFALD01), so the
DIRECT waste of the Danish health industries can be checked against measurement
- something the original study could not do for the Netherlands.

Result (2022): the hybrid-derived direct waste of the Danish health sector is
an order of magnitude above the measured national account. This is reported as
a model limitation and motivates rebuilding the extension.

Run: PYTHONPATH=src .venv/bin/python -m analysis.waste_validation
"""

import json
import os
import pickle
import subprocess

import numpy as np
import pandas as pd

from paths import BACKGROUND_DIR, OUTPUT_DIR

API = "https://api.statbank.dk/v1/data"
ALPHA_ELDERCARE = 0.4914  # 12401 share of industry 880000's individually consumed output


def _affald(year):
    """Total waste (excl. soil) by health industry, tonnes, StatBank AFFALD01."""
    payload = {"table": "AFFALD01", "format": "CSV", "lang": "en",
               "variables": [{"code": "ERHVERV", "values": ["VQ", "VQA", "V870000", "V880000"]},
                             {"code": "AFFFRAK", "values": ["TOTAFFALDX"]},
                             {"code": "Tid", "values": [str(year)]}]}
    out = subprocess.run(["curl", "-s", "-X", "POST", API, "-H", "Content-Type: application/json",
                          "-d", json.dumps(payload)], capture_output=True, text=True).stdout
    rows = [l.split(";") for l in out.strip().splitlines()[1:] if l.strip()]
    return {r[0].split()[0]: float(r[-1]) for r in rows}


def main():
    year = int(os.environ.get("HC_ANALYSIS_YEAR", "2022"))
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{'2022' if year == 2022 else '2016'}.pkl"),
              "rb") as fh:
        bg = pickle.load(fh)
    hybrid_direct_kt = float(bg["Hstim"][6, 0])

    a = _affald(year)
    qa = a.get("QA", np.nan) / 1e3            # tonnes -> kt
    res = a.get("870000", np.nan) / 1e3
    soc = a.get("880000", np.nan) / 1e3
    q_tot = a.get("Q", np.nan) / 1e3
    measured_scope = qa + res + ALPHA_ELDERCARE * soc

    rows = [
        dict(source="EXIOBASE hybrid 2011 waste extension (as inherited)",
             quantity="direct waste of the Danish health sector", value_kt=hybrid_direct_kt,
             basis="absolute 2011 tonnes / analysis-year monetary output"),
        dict(source="Statistics Denmark AFFALD01 (SEEA waste accounts)",
             quantity="Q human health and social work, total waste excl. soil",
             value_kt=q_tot, basis=f"measured, {year}"),
        dict(source="Statistics Denmark AFFALD01 (SEEA waste accounts)",
             quantity="study boundary: QA + 870000 + alpha x 880000",
             value_kt=measured_scope, basis=f"measured, {year}, alpha={ALPHA_ELDERCARE}"),
        dict(source="ratio", quantity="hybrid / measured (Q total)",
             value_kt=hybrid_direct_kt / q_tot if q_tot else np.nan, basis="dimensionless"),
    ]
    df = pd.DataFrame(rows)
    df["analysis_year"] = year
    out = os.path.join(str(OUTPUT_DIR), "tables", "waste_extension_validation.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)
    print(df.to_string(index=False))
    print(f"\nwritten -> {out}")
    print("\nInterpretation: the inherited hybrid-2011 extension overstates the DIRECT "
          "waste of Danish health care by roughly an order of magnitude against "
          "Denmark's own measured SEEA waste accounts. The direct row is therefore "
          "replaced by AFFALD01 in the model, and the supply-chain waste result is "
          "reported with a scenario band rather than a confidence interval.")


if __name__ == "__main__":
    main()
