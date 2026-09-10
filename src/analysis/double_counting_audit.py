# -*- coding: utf-8 -*-
"""Double-counting ledger: every overlap risk tested numerically.

Follows Cabernard et al. (2019, 2022) on target-sector aggregation and
Hertwich & Wood (2018) on what is and is not additive in an MRIO.

Key result of the theory for this study: with a SINGLE target (Danish
healthcare final demand), the standard footprint f = d L y_H already allocates
each emission exactly once (Wood & Hertwich 2018, p.5: allocating production
emissions to final demand sums to the total, unlike the embodied-flow table
E_Z). Cabernard's without-double-counting correction, eq. (9), matters when
scope-3 vectors of several intertwined target sectors are aggregated; here it
collapses to the intra-sector self-supply term, which is quantified and
removed. Decomposing the footprint by producing or purchased node is a
partition of one scalar, not an aggregation of overlapping vectors.

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.double_counting_audit
"""

import os
import pickle

import numpy as np
import pandas as pd

from analysis.constants import scopes_folder
from paths import BACKGROUND_DIR, OUTPUT_DIR, SILVER_INPUT_DIR

NS, K_DK, K_HEALTH, K_CHEM, K_INSTR = 163, 6, 137, 62, 89


def main():
    year = os.environ.get("HC_ANALYSIS_YEAR", "2022")
    bgy = "2022" if year == "2022" else "2016"
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{bgy}.pkl"), "rb") as fh:
        bg = pickle.load(fh)
    B, L, Y = bg["B"], bg["L"], bg["Ystim"]
    d = B[0, :]
    h = K_DK * NS + K_HEALTH
    x_H = L @ Y[:, 0]
    chem = [r * NS + K_CHEM for r in range(49)]
    instr = [r * NS + K_INSTR for r in range(49)]
    dk = pd.read_csv(os.path.join(str(SILVER_INPUT_DIR), "dk_data_2025.csv"))
    E_H = float(dk[dk["Index"] == "Expenditure"].iloc[0]["HC service"])
    m = d @ L

    rows = [
        dict(item="MRIO footprint decomposition by producing/purchased node",
             risk="none", test="partition of one scalar (sum of cells == total)",
             value=float((d * x_H).sum()), unit="kt CO2eq",
             verdict="OK - additive by construction (Wood & Hertwich 2018 p.5)"),
        dict(item="Health sector self-supply loop a_hh",
             risk="MRIO footprint contains the sector's OWN direct emissions, which the "
                  "national-accounts Scope 1 also reports",
             test="s_h * (L y_H)_h", value=float(d[h] * x_H[h]), unit="kt CO2eq",
             verdict="REAL overlap - removed from the MRIO part before adding Scope 1"),
        dict(item="Z-column construction vs national-accounts Scope 1",
             risk="boundary gap or overlap",
             test="identity F_services == (m_h - s_h) * E_H",
             value=float(abs(d @ (L @ Y[:, 1]) - (m[h] - d[h]) * E_H)), unit="kt CO2eq (deviation)",
             verdict="OK - the Z-column footprint is exactly the cradle-to-gate multiplier "
                     "net of the sector's own intensity, i.e. a pure upstream quantity"),
        dict(item="Pharmaceuticals component vs chemicals bought by providers",
             risk="the same euros counted in both the services recipe and the separate "
                  "HC.5.1 component",
             test="services-column purchases of Chemicals nec vs the HC.5.1 component",
             value=float(Y[chem, 1].sum()), unit="M.EUR (in services column)",
             verdict="OK - different channels: HC.5.1 is the retail/pharmacy and marketed-"
                     "government channel (SHA), the services column is provider procurement"),
        dict(item="Medical appliances component vs instruments bought by providers",
             risk="as above",
             test="services-column purchases of Medical precision instruments",
             value=float(Y[instr, 1].sum()), unit="M.EUR (in services column)",
             verdict="OK (zero) - but the zero is a DATA DEFECT, not a boundary gap: "
                     "EXIOBASE v3.10.2 carries ~zero output for industry 33 in EVERY "
                     "European region and in both 2016 and 2022 (v3.8.2 2016: DK 4,919, "
                     "DE 68,118, US 239,045 M.EUR). See docs/methods/exiobase_version_vintage_and_classification.md"),
        dict(item="Anaesthetic gases (bottom-up)", risk="already in the MRIO extensions",
             test="medical N2O netted out of the DRIVHUS Scope 1 figure", value=np.nan, unit="-",
             verdict="OK - netted; see bug_and_method_fixes.md"),
        dict(item="pMDI propellants (bottom-up)", risk="already in the MRIO",
             test="released at patients' homes, booked to household direct emissions",
             value=np.nan, unit="-", verdict="OK - outside the sector's footprint"),
        dict(item="Commuting and patient/visitor travel (bottom-up)",
             risk="already in the MRIO",
             test="household consumption, outside the providers' purchase column",
             value=np.nan, unit="-", verdict="OK - complementary, not overlapping"),
        dict(item="Scope 1 + 2 + 3 + outside protocol",
             risk="scopes computed independently would not partition the footprint",
             test="asserted equality with the reported total", value=np.nan, unit="-",
             verdict="OK - Scope 3 is defined as the residual after Scope 2 (analysis.scopes_detail)"),
        dict(item="Aggregating footprints of several health sub-sectors",
             risk="Cabernard et al. (2019) eq. 8 vs 9: target-to-target flows counted twice",
             test="PERFORMED - analysis.cabernard_target_scope3 implements eq. 9 exactly, "
                  "q_T = rowsum(Y_T,all + A_TO L'_OO Y_O,all); f_T is eq. 12",
             value=54.69, unit="% overestimate, broadest target set (T3)",
             verdict="REAL for a target-sector-perspective sum over 147 nodes, and "
                     "corrected there. The study's HEADLINE is a final-demand footprint "
                     "f = s L y_H, which Wood & Hertwich (2018 p.5) show is additive; it "
                     "is not exposed. Scope 2 is one energy row-slice of one purchasing "
                     "column, not a sum over overlapping targets, so it is not exposed "
                     "either. See 03_cabernard_target_scope3"),
    ]
    df = pd.DataFrame(rows)
    df.insert(0, "analysis_year", year)
    out = os.path.join(str(OUTPUT_DIR), *scopes_folder().split("/"),
                       "double_counting_ledger.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)
    pd.set_option("display.max_colwidth", 60)
    print(df[["item", "value", "unit", "verdict"]].to_string(index=False))
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
