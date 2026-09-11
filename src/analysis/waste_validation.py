# -*- coding: utf-8 -*-
"""Test the inherited waste extension against Denmark's own waste accounts.

The waste indicator is inherited from Steenmeijer et al. (2022): absolute waste
supply by industry from the 2011 hybrid EXIOBASE MR-HSUT, divided by the
analysis year's monetary output. Denmark publishes SEEA waste accounts on the
same 117-industry classification as its IO tables (StatBank AFFALD01), so the
DIRECT waste of the Danish health industries can be checked against measurement
- something the original study could not do for the Netherlands.

Result (2022): the hybrid-derived direct waste of the Danish health sector is
159.99 kt against a measured 51.80 kt for the whole of NACE Q and 45.14 kt on
the study's own boundary, i.e. **3.1 times** the measured national account.
This is reported as a model limitation and motivates rebuilding the extension.

WHERE THE HYBRID FIGURE COMES FROM, AND WHY IT IS RECOMPUTED HERE.
``analysis.main_2025`` overwrites ``Hstim[6, 0]`` with the AFFALD01 figure
before it persists the background, so the row a module reads from the
background is the *replacement*, not the inherited extension. Reading it and
labelling it "hybrid" made this table compare the Danish account against
itself, and publish a ratio of 0.83 that meant nothing. The inherited value is
still recoverable exactly, because ``B`` is not overwritten: the background
construction sets ``Hstim[6, 0] = B[6, h] * x_h * scale`` with
``x_h * scale = E_H``, so the hybrid figure is ``B[6, h] * E_H``. Both are now
published, each under its own name.

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship \
         .venv/bin/python -m analysis.waste_validation
"""

import json
import os
import pickle
import subprocess

import numpy as np
import pandas as pd

from analysis.constants import BACKGROUND_YEAR, NODE_DK_HEALTH
from paths import BACKGROUND_DIR, OUTPUT_DIR, silver_dk_data_csv

API = "https://api.statbank.dk/v1/data"
ALPHA_ELDERCARE = 0.4914  # 12401 share of industry 880000's individually consumed output


def _affald(year: int) -> dict[str, float]:
    """Total waste (excl. soil) by health industry, tonnes, StatBank AFFALD01.

    Parameters
    ----------
    year : int
        Calendar year to query the AFFALD01 table for.

    Returns
    -------
    dict of str to float
        Tonnes of total waste excluding soil, keyed by the leading industry
        code token of each returned row (e.g. ``"QA"``, ``"870000"``,
        ``"880000"``, ``"Q"``).
    """
    payload = {"table": "AFFALD01", "format": "CSV", "lang": "en",
               "variables": [{"code": "ERHVERV", "values": ["VQ", "VQA", "V870000", "V880000"]},
                             {"code": "AFFFRAK", "values": ["TOTAFFALDX"]},
                             {"code": "Tid", "values": [str(year)]}]}
    out = subprocess.run(["curl", "-s", "-X", "POST", API, "-H", "Content-Type: application/json",
                          "-d", json.dumps(payload)], capture_output=True, text=True).stdout
    rows = [l.split(";") for l in out.strip().splitlines()[1:] if l.strip()]
    return {r[0].split()[0]: float(r[-1]) for r in rows}


def main() -> None:
    """Compare the inherited hybrid waste extension against measured AFFALD01.

    Reads the direct-waste row of the health sector from the pickled
    background (kt, 2011 hybrid EXIOBASE MR-HSUT scaled to analysis-year
    output) and Statistics Denmark's SEEA waste accounts (AFFALD01, tonnes
    converted to kt) for the same year, and reports both alongside the
    study-boundary measured total (``QA + 870000 + ALPHA_ELDERCARE *
    880000``) and their ratio. Writes
    ``data/gold/results/05_waste_dst_accounts/waste_extension_validation.csv``
    and prints the comparison. Reads ``HC_ANALYSIS_YEAR`` from the
    environment (default ``"2022"``) for the AFFALD01 query, and the
    background from ``analysis.constants.BACKGROUND_YEAR``, which carries
    both that variable and ``HC_BACKGROUND_TAG``. The hybrid direct-waste row
    happens to be identical in the corrected and uncorrected backgrounds, so
    no published value depends on this today; it is read through the shared
    constant anyway, because a future background revision could make the
    difference real without warning.
    """
    year = int(os.environ.get("HC_ANALYSIS_YEAR", "2022"))
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"),
              "rb") as fh:
        bg = pickle.load(fh)
    # The row the model carries, after main_2025's AFFALD01 replacement.
    modelled_direct_kt = float(bg["Hstim"][6, 0])
    # The inherited hybrid value, recomputed from the intensity matrix, which
    # the replacement does not touch. See the module docstring.
    expenditure = pd.read_csv(silver_dk_data_csv(str(year)))
    e_h = float(expenditure[expenditure["Index"] == "Expenditure"]
                .iloc[0]["HC service"])
    hybrid_direct_kt = float(bg["B"][6, NODE_DK_HEALTH]) * e_h

    a = _affald(year)
    qa = a.get("QA", np.nan) / 1e3            # tonnes -> kt
    res = a.get("870000", np.nan) / 1e3
    soc = a.get("880000", np.nan) / 1e3
    q_tot = a.get("Q", np.nan) / 1e3
    measured_scope = qa + res + ALPHA_ELDERCARE * soc

    rows = [
        dict(source="EXIOBASE hybrid 2011 waste extension (as inherited)",
             quantity="direct waste of the Danish health sector", value_kt=hybrid_direct_kt,
             basis="absolute 2011 tonnes / analysis-year monetary output; "
                   "recomputed as B[6, DK health] x healthcare-services "
                   "expenditure, because main_2025 overwrites the background's "
                   "own Hstim row with the Danish account"),
        dict(source="This study's model, after the AFFALD01 replacement",
             quantity="direct waste of the Danish health sector, as modelled",
             value_kt=modelled_direct_kt,
             basis="Hstim[6, 0] of the persisted background, set by "
                   "analysis.main_2025 from AFFALD01"),
        dict(source="Statistics Denmark AFFALD01 (SEEA waste accounts)",
             quantity="Q human health and social work, total waste excl. soil",
             value_kt=q_tot, basis=f"measured, {year}"),
        dict(source="Statistics Denmark AFFALD01 (SEEA waste accounts)",
             quantity="study boundary: QA + 870000 + alpha x 880000",
             value_kt=measured_scope, basis=f"measured, {year}, alpha={ALPHA_ELDERCARE}"),
        dict(source="ratio", quantity="hybrid / measured (Q total)",
             value_kt=hybrid_direct_kt / q_tot if q_tot else np.nan,
             basis="dimensionless; the size of the defect the replacement removes"),
        dict(source="ratio", quantity="hybrid / measured (study boundary)",
             value_kt=hybrid_direct_kt / measured_scope if measured_scope else np.nan,
             basis="dimensionless"),
        dict(source="ratio", quantity="modelled / measured (study boundary)",
             value_kt=modelled_direct_kt / measured_scope if measured_scope else np.nan,
             basis="dimensionless; a conformance check on the replacement, not "
                   "on the extension. It is not 1.000 because the model takes "
                   "AFFALD01 at the release main_2025 records, while this row "
                   "queries StatBank live"),
    ]
    df = pd.DataFrame(rows)
    df["analysis_year"] = year
    out = os.path.join(str(OUTPUT_DIR), "05_waste_dst_accounts", "waste_extension_validation.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)
    print(df.to_string(index=False))
    print(f"\nwritten -> {out}")
    print(f"\nInterpretation: the inherited hybrid-2011 extension overstates the "
          f"DIRECT waste of Danish health care by a factor of "
          f"{hybrid_direct_kt / q_tot:.1f} against Denmark's own measured SEEA "
          f"waste accounts for NACE Q, and "
          f"{hybrid_direct_kt / measured_scope:.1f} against the study's own "
          f"boundary. The direct row is therefore replaced by AFFALD01 in the "
          f"model, and the supply-chain waste result is reported with a "
          f"scenario band rather than a confidence interval.")


if __name__ == "__main__":
    main()
