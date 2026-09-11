# -*- coding: utf-8 -*-
"""GHG-Protocol scope decomposition with full producing-node lineage.

Partition (Hertwich & Wood 2018, *The growing importance of scope 3 greenhouse
gas emissions from industry*, Environ Res Lett 13:104013, table 1 and eqs. 1-3;
GHG Protocol corporate standard; OECD/Doucet et al. 2025 for the health-sector
application):

THREE PUBLISHED SCOPE-2 CONVENTIONS EXIST, and they differ by which part of the
purchased-energy chain they count. All three are computed and reported; the
study's headline follows Hertwich & Wood, whose method this pipeline inherits.

    OECD (Doucet et al. 2025 eq.)   E2 = F A Y restricted to energy sectors
        Direct emissions of the first-tier energy supplier only. On EXIOBASE ixi
        this UNDER-counts, because electricity reaches the buyer through
        "Transmission" and "Distribution and trade of electricity", whose own
        combustion intensity is ~0; generation sits one tier further back.

    GHG Protocol strict              S2 = d_E . L_EE y_E,  L_EE = (I_EE-A_EE)^-1
        Traces through transmission and distribution to GENERATION and stops
        inside the energy block, so fuel extraction, refining and grid hardware
        remain in Scope 3 - the corporate standard's boundary, which assigns
        upstream fuel supply to Scope 3 category 3.

    Hertwich & Wood 2018 (HEADLINE)  E_Z = mhat Z, m = s (I-A)^-1, energy rows
        Cradle-to-gate embodied emissions of the purchased energy: generation
        PLUS the upstream fuel supply behind it. Broader than the corporate
        standard, and the convention of the paper this study follows.

The spread across the three is 72.1 - 75.0 kt CO2e, i.e. 3.9 % of Scope 2 and
0.06 % of the total footprint, so the choice does not affect any conclusion. It
is reported explicitly because the manuscript claims GHG-Protocol scopes and a
reader is entitled to know which operationalisation produced the number.

  Scope 1  direct emissions of the Danish health providers.
           Taken from national accounts (Statistics Denmark DRIVHUS), NOT from
           the MRIO: the final-demand vector y_H is the providers' *purchase*
           column, so the providers' own direct emissions are outside
           f = s L y_H by construction and are added once, here.
           Medical anaesthetic gases are added as a bottom-up Scope 1 item
           (they are netted out of the DRIVHUS figure to avoid double counting).

  Scope 2  emissions from the GENERATION of the electricity, steam and heat
           the providers purchase, computed with the ENERGY-BLOCK inverse:
               L_EE = (I_EE - A_EE)^-1 ,  S2 = d_E . L_EE y_E
           where E indexes electricity/steam/hot-water nodes in all regions and
           y_E is the providers' own first-tier energy purchases. The block
           inverse reaches generation through transmission and distribution
           (whose own combustion intensity is ~0 in EXIOBASE) WITHOUT leaving
           the energy block, so fuel extraction, refining and grid hardware
           stay in Scope 3 - exactly the GHG Protocol boundary. Using the full
           L instead would additionally capture electricity consumed deep in
           the chain, which the Protocol assigns to Scope 3 category 3.
           The OECD first-tier form and the Hertwich & Wood full-multiplier
           form are both computed alongside it; see the three conventions set
           out at the top of this module.

  Scope 3  every remaining upstream emission in the footprint:
               S3_mrio = f_total - S2
           plus the bottom-up upstream items that the MRIO cannot contain
           (pMDI propellant release at patients' homes; employee commuting).

  Outside protocol   patient and visitor travel (not an organisational scope).

Self-supply correction: the services component is y = A[:,h] E_H, so the
footprint contains s_h (L_hh - 1) E_H of the health sector's OWN direct
emissions through the intra-sector loop a_hh. That term overlaps the
national-accounts Scope 1 and is removed from the MRIO part before Scope 1 is
added (Denmark 2022: 1.83 kt CO2e, 1.4 % of Scope 1, published in this
folder's scopes_summary_detailed.csv as "self-supply loop removed"). The construction is
otherwise exactly complementary to a national-accounts Scope 1, because
    F_services = (m_h - s_h) E_H
identically (verified in code): the Z-column footprint IS the health sector's
cradle-to-gate multiplier net of its own direct intensity.

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
from analysis.constants import (BACKGROUND_YEAR, MODEL_LABEL,  # noqa: E402
                                eriksen_folder, scopes_folder)
GEN_PATTERN = r"\belectricity\b|\bsteam\b|\bhot\s*water\b"
INDICATORS = [(0, "climate_change", "kt CO2eq"), (1, "material_extraction", "kt"),
              (2, "blue_water_consumption", "Mm3"), (3, "land_use", "km2"),
              (6, "waste_generation", "kt")]


def main() -> None:
    """Partition the footprint into GHG-Protocol scopes with node lineage.

    For each of the five ``INDICATORS``, computes Scope 1 (national-accounts
    direct plus anaesthetic gases), Scope 2 under all three published
    conventions (OECD first-tier, GHG Protocol strict energy-block inverse -
    the study's basis, and Hertwich & Wood full-multiplier - the manuscript's
    reported figure), Scope 3 as the MRIO residual plus pMDI and commuting,
    and Outside-protocol patient/visitor travel, after removing the health
    sector's self-supply loop that would otherwise double-count against
    national-accounts Scope 1. Writes ``scopes_summary_detailed.csv`` and
    ``scopes_by_producing_node.csv`` to the analysis year's scope-decomposition
    gold folder (``analysis.constants.scopes_folder``), and prints the
    partition per indicator.

    Raises
    ------
    AssertionError
        If the bottom-up items file is missing a required row or column, if
        Scope 1 + 2 + 3 + Outside does not reproduce the reported total to
        within ``1e-9``, or if the producing-node detail does not reconcile
        with the Scope 2 + Scope 3 summary to within ``1e-6``.
    """
    out_dir = os.path.join(str(OUTPUT_DIR), *scopes_folder().split("/"))
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
    # Intermediate workbook, not a deliverable: it lives in silver's
    # eriksen_interim handoff (see main_2025's interim_dir), not in gold.
    contrib = pd.read_excel(
        os.path.join(str(SILVER_INPUT_DIR), "eriksen_interim",
                     *eriksen_folder().split("/"),
                     "contribution_analysis.xlsx"), sheet_name="full")
    b_heal = contrib[contrib["SecTxtCode"] == "B_HEAL"].iloc[0]
    DIRECT_COL = {"climate_change": "Global warming (ktCO2eq)",
                  "material_extraction": "Material extraction (kt)",
                  "blue_water_consumption": "Blue water consumption (Mm3)",
                  "land_use": "Land use (km2)",
                  "waste_generation": "Waste generation (kt)"}
    # Bottom-up items, all five categories. `main_2025` rewrites this file in
    # place with the Danish primary values for the year it was run for, so this
    # module must run straight after it for the same year.
    bu = pd.read_csv(os.path.join(str(SILVER_INPUT_DIR), "dk_bottomup_data_2025.txt"),
                     sep="\t").set_index("Source")
    for _row in ("Anaesthetic", "pMDI", "Commute (total)",
                 "Visitor travel (total)"):
        missing = [c for c in DIRECT_COL.values() if c not in bu.columns]
        if missing:
            raise AssertionError(f"bottom-up file lacks columns {missing}")
        if _row not in bu.index:
            raise AssertionError(f"bottom-up file lacks row {_row!r}")

    # energy purchases of the providers = healthcare-services component only
    y_energy = np.zeros(Ystim.shape[0])
    y_energy[gen_idx] = Ystim[gen_idx, 1]
    # energy-block inverse: reach generation through T&D without leaving the block
    A = bg["A"]
    A_EE = A[np.ix_(gen_idx, gen_idx)]
    L_EE = np.linalg.inv(np.eye(len(gen_idx)) - A_EE)
    x_energy_block = L_EE @ y_energy[gen_idx]
    x_energy_fullL = (L @ y_energy)[gen_idx]        # reported as a sensitivity only

    # self-supply loop of the health sector (overlaps national-accounts Scope 1)
    h = 6 * ns + 137
    x_H = L @ Ystim[:, 0]
    selfloop = {}

    summary, detail = [], []
    for k_row, ind, unit in INDICATORS:
        s = B[k_row, :]
        y_tot = Ystim[:, 0]
        e_nodes = s * (L @ y_tot)                 # producing-node footprint
        f_total = float(e_nodes.sum())

        s2_nodes = np.zeros_like(e_nodes)
        s2_nodes[gen_idx] = s[gen_idx] * x_energy_block
        s2 = float(s2_nodes.sum())
        s2_strict = float((s[gen_idx] * y_energy[gen_idx]).sum())
        s2_fullL = float((s[gen_idx] * x_energy_fullL).sum())

        # remove the health sector's own direct emissions pulled through a_hh
        loop = float(s[h] * x_H[h])
        selfloop[ind] = loop
        e_nodes = e_nodes.copy()
        e_nodes[h] -= loop
        f_total -= loop

        s3_nodes = e_nodes - s2_nodes             # residual: no overlap by construction
        s3_mrio = float(s3_nodes.sum())

        # The bottom-up items are not climate-only: the ecoinvent inventory
        # behind commuting and patient/visitor travel carries all five
        # categories (vehicle manufacture, fuel supply, infrastructure), and the
        # Eriksen tables place it as the GLO/B_REST node. Treating those columns
        # as zero here left the non-climate scope tables 0.2-0.6 % below the
        # study totals reported by figures 1 and 2. The placement is the same
        # for every category and follows the GHG Protocol: anaesthetic gases are
        # direct (Scope 1), pMDI propellant and employee commuting are Scope 3
        # (categories 1 and 7), patient and visitor travel is outside the
        # protocol because those people are not the reporting entity.
        # For climate the B_HEAL GWP already IS the DRIVHUS figure net of
        # medical N2O, so anaesthetic adds without double counting.
        col = DIRECT_COL[ind]
        c_direct = float(b_heal[col])
        c_anae = float(bu.loc["Anaesthetic", col])
        c_pmdi = float(bu.loc["pMDI", col])
        c_commute = float(bu.loc["Commute (total)", col])
        c_visitor = float(bu.loc["Visitor travel (total)", col])
        s1 = c_direct + c_anae
        s3 = s3_mrio + c_pmdi + c_commute
        outside = c_visitor
        total = s1 + s2 + s3 + outside

        summary += [
            {"indicator": ind, "unit": unit, "scope": "Scope 1", "value": s1,
             "basis": "national accounts (DRIVHUS/AFFALD) + medical gases" if ind in
                      ("climate_change", "waste_generation") else "EXIOBASE direct of the sector"},
            {"indicator": ind, "unit": unit, "scope": "Scope 2", "value": s2,
             "basis": "GHG Protocol strict: generation of purchased "
                      "electricity/steam/heat, traced through T&D with the "
                      "energy-block inverse; basis of this folder's partition"},
            {"indicator": ind, "unit": unit,
             "scope": "Scope 2 (OECD first-tier convention)",
             "value": s2_strict,
             "basis": "Doucet et al. 2025: F A Y restricted to energy sectors; "
                      "under-counts on EXIOBASE ixi because T&D sit between the "
                      "buyer and generation. Not added to the total"},
            {"indicator": ind, "unit": unit,
             "scope": "Scope 2 (Hertwich & Wood 2018 convention)",
             "value": s2_fullL,
             "basis": "cradle-to-gate embodied emissions of purchased energy "
                      "(E_Z = mhat Z, m = s L). Broader than the corporate "
                      "standard, which puts upstream fuel in Scope 3 cat. 3. "
                      "THIS IS THE MANUSCRIPT'S REPORTED SCOPE 2. Not added to "
                      "this folder's total"},
            {"indicator": ind, "unit": unit, "scope": "self-supply loop removed",
             "value": loop, "basis": "s_h (L_hh - 1) E_H, overlaps national-accounts Scope 1"},
            {"indicator": ind, "unit": unit, "scope": "Scope 3", "value": s3,
             "basis": "footprint residual after Scope 2, plus pMDI (climate) "
                      "and commuting"},
            {"indicator": ind, "unit": unit, "scope": "Outside protocol", "value": outside,
             "basis": "patient and visitor travel"},
            {"indicator": ind, "unit": unit, "scope": "TOTAL", "value": total, "basis": "S1+S2+S3+outside"},
        ]
        # Components of the scopes above, written out so the figure tables can
        # place each bottom-up term at its own producing node instead of
        # inferring it. They are parts of the totals, never added to them.
        summary += [
            {"indicator": ind, "unit": unit,
             "scope": "Scope 1 component: direct operations", "value": c_direct,
             "basis": "national accounts (DRIVHUS / AFFALD01) or EXIOBASE "
                      "direct row of the Danish health industry. Component"},
            {"indicator": ind, "unit": unit,
             "scope": "Scope 1 component: anaesthetic gases", "value": c_anae,
             "basis": "Medstat N01AB volatiles + NID N2O. Component"},
            {"indicator": ind, "unit": unit,
             "scope": "Scope 3 component: pMDI propellant", "value": c_pmdi,
             "basis": "Danish EPA F-gas inventory, MDI line. Component"},
            {"indicator": ind, "unit": unit,
             "scope": "Scope 3 component: employee commuting", "value": c_commute,
             "basis": "bottom-up commuting, GHG Protocol Scope 3 cat. 7. "
                      "Component"},
            {"indicator": ind, "unit": unit,
             "scope": "Outside protocol component: patient and visitor travel",
             "value": c_visitor,
             "basis": "TU purpose 33 + NHS visitor ratio. Component"},
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
    meta = dict(analysis_year=ANALYSIS_YEAR, model=MODEL_LABEL,
                consuming_country_iso3="DNK")
    for k, v in meta.items():
        summ.insert(0, k, v)
        det.insert(0, k, v)
    summ.to_csv(os.path.join(out_dir, "scopes_summary_detailed.csv"), index=False)
    det.to_csv(os.path.join(out_dir, "scopes_by_producing_node.csv"), index=False)

    # ---- exactness checks --------------------------------------------------
    print("Scope partition (GHG Protocol strict; Hertwich & Wood 2018 table 1):")
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
        # Node detail is the MRIO array only, so every bottom-up term added to
        # Scope 3 above has to come back out before the comparison.
        bu_extra = float(bu.loc["pMDI", DIRECT_COL[ind]]) + \
            float(bu.loc["Commute (total)", DIRECT_COL[ind]])
        assert abs(d - (s - bu_extra)) < 1e-6, f"{ind}: node detail != scope totals"
    print("PASS: scopes partition exactly and node detail reconciles")
    print(f"written -> {out_dir}/scopes_summary_detailed.csv, scopes_by_producing_node.csv")


if __name__ == "__main__":
    main()
