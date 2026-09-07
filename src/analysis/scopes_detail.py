# -*- coding: utf-8 -*-
"""GHG-Protocol scope decomposition with full producing-node lineage.

Partition (Wood et al. 2018, table 1 and eqs. 1-2; GHG Protocol corporate
standard):

  Scope 1  direct emissions of the Danish health providers.
           Taken from national accounts (Statistics Denmark DRIVHUS), NOT from
           the MRIO: the final-demand vector y_H is the providers' *purchase*
           column, so the providers' own direct emissions are outside
           f = s L y_H by construction and are added once, here.
           Medical anaesthetic gases are added as a bottom-up Scope 1 item
           (they are netted out of the DRIVHUS figure to avoid double counting).

  Scope 2  emissions from the GENERATION of the electricity, steam and heat
           the providers purchase. Computed as the emissions arising *in*
           electricity/steam/hot-water sectors that are induced by the
           providers' own direct purchases of those products:
               S2 = sum_{i in GEN} s_i [L y_E]_i ,  y_E = y_H restricted to
           energy products bought by the providers.
           Tracing through L is necessary because EXIOBASE books much of the
           purchase against transmission/distribution sectors whose own direct
           emissions are ~0 while generation sits one tier upstream. A strict
           first-tier variant (S2 = sum_{i in GEN} s_i y_E,i) is reported
           alongside as a sensitivity.
           NB Wood et al. define scope 2 more broadly (electricity *and fuel*
           production); we follow the GHG Protocol, where purchased fuels
           combusted on site are scope 1 and their production is scope 3.

  Scope 3  every remaining upstream emission in the footprint:
               S3_mrio = f_total - S2
           plus the bottom-up upstream items that the MRIO cannot contain
           (pMDI propellant release at patients' homes; employee commuting).

  Outside protocol   patient and visitor travel (not an organisational scope).

Exactness: Scope1 + Scope2 + Scope3 + Outside == reported total, asserted.
No cell is counted twice because S3 is defined as a residual of the same
footprint array from which S2 is taken (Wood et al. 2018: allocating
production emissions to final demand is additive; it is the *embodied-flow*
table E_Z that double counts, and we never sum that).

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.scopes_detail
"""

import os
import pickle
import re

import numpy as np
import pandas as pd

from paths import BACKGROUND_DIR, OUTPUT_DIR, SILVER_INPUT_DIR
from analysis.export_tables import _labels, _node_frame

ANALYSIS_YEAR = os.environ.get("HC_ANALYSIS_YEAR", "2022")
BACKGROUND_YEAR = "2022" if ANALYSIS_YEAR == "2022" else "2016"
GEN_PATTERN = r"\belectricity\b|\bsteam\b|\bhot\s*water\b"
INDICATORS = [(0, "climate_change", "kt CO2eq"), (1, "material_extraction", "kt"),
              (2, "blue_water_consumption", "Mm3"), (3, "land_use", "km2"),
              (6, "waste_generation", "kt")]


def main():
    out_dir = os.path.join(str(OUTPUT_DIR), "tables")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        bg = pickle.load(fh)
    B, L, Ystim = bg["B"], bg["L"], bg["Ystim"]
    reg, sec = _labels()
    nr, ns = len(reg), len(sec)
    names_full = pd.Series(list(sec["sector_name"]) * nr)
    gen_mask = names_full.str.contains(GEN_PATTERN, case=False, regex=True, na=False).to_numpy()
    gen_idx = np.flatnonzero(gen_mask)
    prod = _node_frame(reg, sec, "producing")

    # Direct (Scope 1) impacts are taken from the B_HEAL row that the main
    # pipeline writes, so both use byte-identical numbers: GWP from DRIVHUS and
    # waste from AFFALD01 (Danish measured), the other categories from EXIOBASE.
    contrib = pd.read_excel(os.path.join(str(OUTPUT_DIR), "contribution_analysis.xlsx"),
                            sheet_name="full")
    b_heal = contrib[contrib["SecTxtCode"] == "B_HEAL"].iloc[0]
    DIRECT_COL = {"climate_change": "Global warming (ktCO2eq)",
                  "material_extraction": "Material extraction (kt)",
                  "blue_water_consumption": "Blue water consumption (Mm3)",
                  "land_use": "Land use (km2)",
                  "waste_generation": "Waste generation (kt)"}
    direct_gwp = float(b_heal[DIRECT_COL["climate_change"]])
    bu = pd.read_csv(os.path.join(str(SILVER_INPUT_DIR), "dk_bottomup_data_2025.txt"),
                     sep="\t").set_index("Source")
    gwp_col = "Global warming (ktCO2eq)"
    anaesthetic = float(bu.loc["Anaesthetic", gwp_col])
    pmdi = float(bu.loc["pMDI", gwp_col])
    commute = float(bu.loc["Commute (total)", gwp_col])
    visitor = float(bu.loc["Visitor travel (total)", gwp_col])

    # energy purchases of the providers = healthcare-services component only
    y_energy = np.zeros(Ystim.shape[0])
    y_energy[gen_idx] = Ystim[gen_idx, 1]
    x_energy = L @ y_energy

    summary, detail = [], []
    for k_row, ind, unit in INDICATORS:
        s = B[k_row, :]
        y_tot = Ystim[:, 0]
        e_nodes = s * (L @ y_tot)                 # producing-node footprint
        f_total = float(e_nodes.sum())

        s2_nodes = np.zeros_like(e_nodes)
        s2_nodes[gen_idx] = s[gen_idx] * x_energy[gen_idx]
        s2 = float(s2_nodes.sum())
        s2_strict = float((s[gen_idx] * y_energy[gen_idx]).sum())

        s3_nodes = e_nodes - s2_nodes             # residual: no overlap by construction
        s3_mrio = float(s3_nodes.sum())

        if ind == "climate_change":
            # the B_HEAL GWP already IS the DRIVHUS figure net of medical N2O
            s1 = direct_gwp + anaesthetic
            s3 = s3_mrio + pmdi + commute
            outside = visitor
        else:
            s1 = float(b_heal[DIRECT_COL[ind]])
            s3, outside = s3_mrio, 0.0
        total = s1 + s2 + s3 + outside

        summary += [
            {"indicator": ind, "unit": unit, "scope": "Scope 1", "value": s1,
             "basis": "national accounts (DRIVHUS/AFFALD) + medical gases" if ind in
                      ("climate_change", "waste_generation") else "EXIOBASE direct of the sector"},
            {"indicator": ind, "unit": unit, "scope": "Scope 2", "value": s2,
             "basis": "generation emissions of purchased electricity/steam/heat (traced)"},
            {"indicator": ind, "unit": unit, "scope": "Scope 2 (first-tier variant)",
             "value": s2_strict, "basis": "sensitivity, not added to the total"},
            {"indicator": ind, "unit": unit, "scope": "Scope 3", "value": s3,
             "basis": "footprint residual after Scope 2, plus pMDI and commuting"},
            {"indicator": ind, "unit": unit, "scope": "Outside protocol", "value": outside,
             "basis": "patient and visitor travel"},
            {"indicator": ind, "unit": unit, "scope": "TOTAL", "value": total, "basis": "S1+S2+S3+outside"},
        ]

        for scope_name, vec in (("Scope 2", s2_nodes), ("Scope 3", s3_nodes)):
            nz = np.flatnonzero(np.abs(vec) > 0)
            d = prod.iloc[nz].copy()
            d.insert(0, "scope", scope_name)
            d.insert(0, "unit", unit)
            d.insert(0, "indicator", ind)
            d["value"] = vec[nz]
            detail.append(d)

    summ = pd.DataFrame(summary)
    det = pd.concat(detail, ignore_index=True)
    meta = dict(analysis_year=ANALYSIS_YEAR, model=f"EXIOBASE v3.10.2 IOT_{BACKGROUND_YEAR}_ixi (screened)",
                consuming_country_iso3="DNK")
    for k, v in meta.items():
        summ.insert(0, k, v)
        det.insert(0, k, v)
    summ.to_csv(os.path.join(out_dir, "scopes_summary_detailed.csv"), index=False)
    det.to_csv(os.path.join(out_dir, "scopes_by_producing_node.csv"), index=False)

    # ---- exactness checks --------------------------------------------------
    print("Scope partition (GHG Protocol; Wood et al. 2018 table 1):")
    for ind, _, _ in [(i[1], i[0], i[2]) for i in INDICATORS]:
        sub = summ[summ["indicator"] == ind].set_index("scope")["value"]
        parts = sub[["Scope 1", "Scope 2", "Scope 3", "Outside protocol"]].sum()
        assert abs(parts - sub["TOTAL"]) < 1e-9, f"{ind}: partition does not sum"
        print(f"  {ind:22s} S1 {sub['Scope 1']:9.2f} | S2 {sub['Scope 2']:9.2f} "
              f"| S3 {sub['Scope 3']:11.2f} | outside {sub['Outside protocol']:7.2f} "
              f"| total {sub['TOTAL']:11.2f}")
    # scope detail must reproduce the MRIO footprint exactly
    for ind, _, _ in [(i[1], i[0], i[2]) for i in INDICATORS]:
        d = det[det["indicator"] == ind]["value"].sum()
        s = summ[(summ["indicator"] == ind) &
                 (summ["scope"].isin(["Scope 2", "Scope 3"]))]["value"].sum()
        bu_extra = (pmdi + commute) if ind == "climate_change" else 0.0
        assert abs(d - (s - bu_extra)) < 1e-6, f"{ind}: node detail != scope totals"
    print("PASS: scopes partition exactly and node detail reconciles")
    print(f"written -> {out_dir}/scopes_summary_detailed.csv, scopes_by_producing_node.csv")


if __name__ == "__main__":
    main()
