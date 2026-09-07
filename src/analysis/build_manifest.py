# -*- coding: utf-8 -*-
"""Build the lineage manifest for every gold result file.

One row per file: which approach it belongs to, the script that produced it,
the equations and published reference that approach implements, the inputs it
consumed, plus size and a content hash. This is the entry point for tracing any
published number back to both its data and its method.

Run: PYTHONPATH=src .venv/bin/python -m analysis.build_manifest
"""

import hashlib
import os
from datetime import datetime, timezone

import pandas as pd

from paths import OUTPUT_DIR

APPROACHES = {
    "09_vintage_diagnostics": dict(
        approach="EXIOBASE vintage audit against Danish national accounts",
        reference="Rørmose Jensen & Iliev 2022 (Statistics Denmark); Palm et al. 2019; "
                  "Stadler et al. 2018 (J Ind Ecol 22:502)",
        script="analysis.vintage_defect_audit",
        equations="ratio = x_EXIOBASE(group) / x_nationalaccounts(group)",
        inputs="EXIOBASE v3.7/v3.8.2/v3.10.2 x vectors; DST 117-industry IO tables"),
    "10_snac_shipping_correction": dict(
        approach="Danish sea-transport reallocation (simplified SNAC step)",
        reference="Rørmose Jensen & Iliev 2022, pp. 11-12; Palm et al. 2019",
        script="analysis.dk_shipping_correction",
        equations="Z[row,DK] *= 0.09*x_row / Z[row,DK].sum(); residual to exports; "
                  "value added credited to restore column balance",
        inputs="EXIOBASE v3.8.2 IOT_2022_ixi; DST water-transport allocation"),
    "11_capital_gfcf": dict(
        approach="Capital boundary: excluded, exogenous service flow, endogenised",
        reference="Södersten, Wood & Hertwich 2018 (ES&T 52:13250); Wood & Hertwich 2018; "
                  "Malik et al. 2018",
        script="analysis.capital_gfcf",
        equations="f_A = f + C S L y_cap ; K[:,j] = g_r cfc_j / x_j ; A' = A + K",
        inputs="prepared background; DST NABK69 P.51c/P.51g by asset, 2022"),
    "12_impact_categories_full": dict(
        approach="All DESIRE impact categories (CML, USEtox, EcoIndicator 99, ILCD)",
        reference="DESIRE/EXIOBASE characterisation v3.4; ILCD recommended CFs; "
                  "Eckelman & Sherman 2016 for the category set and DALY comparison",
        script="analysis.impact_categories_full",
        equations="e = R xhat^-1 L y ; impact = Q_full e",
        inputs="raw 1113-row stressor matrix; characterisation_desire_version3_4_adapted.xlsx"),
    "13_steenmeijer_replication": dict(
        approach="Denmark against the Dutch template, table by table",
        reference="Steenmeijer et al. 2022 (Lancet Planet Health 6:e949) main table "
                  "and table S7; RIVM report 2022-0159 tables 8 and 9",
        script="analysis.steenmeijer_replication",
        equations="f_services = Z[:,h] (E_H / x_h); per-capita normalisation",
        inputs="Danish footprint by demand component; scopes summary; "
               "published Dutch values transcribed with provenance"),
    "14_eckelman_replication": dict(
        approach="Denmark on Eckelman & Sherman's nine-category frame, plus DALYs",
        reference="Eckelman & Sherman 2016 (PLoS ONE 11:e0157014) table 2",
        script="analysis.eckelman_replication",
        equations="share = f_health / f_national per category; DALY from ILCD endpoints",
        inputs="12_impact_categories_full; published US values transcribed with provenance"),
    "15_gwp_vintage": dict(
        approach="Climate characterisation vintage sensitivity, SAR to AR6",
        reference="IPCC AR6 WG1 ch.7 table 7.15; AR5 table 8.7; AR4 table 2.14",
        script="analysis.gwp_vintage",
        equations="f = sum_g m_g GWP100_g(vintage) + fixed CO2eq stressors",
        inputs="raw stressor masses by species; IPCC GWP100 by assessment report"),
    "16_impact_world_plus": dict(
        approach="IMPACT World+ v2.2.1, 38 live categories with DALY endpoints",
        reference="Bulle et al. 2019 (Int J LCA 24:1653); CIRAIG matrix for EXIOBASE "
                  "3.8.2, DOI 10.5281/zenodo.18892673, CC-BY-SA-4.0",
        script="analysis.impact_world_plus",
        equations="impact = C_IW+ (R xhat^-1 L y); column alignment asserted at load",
        inputs="raw stressor matrix; IMPACT World+ 57 x 1113 expert matrix"),
    "01_eriksen_replication_tables": dict(
        approach="Replication outputs restated as FAIR long-format CSVs",
        reference="Steenmeijer et al. 2022 figures 1-3",
        script="analysis.eriksen_tables",
        equations="contribution B L diag(y); hotspot B diag(L y); intensities B",
        inputs="the replication's own workbooks; totals asserted unchanged"),
    "06_benchmarks_danish_healthcare": dict(
        approach="Boundary-matched benchmark against the published Danish comparator",
        reference="Schmidt & Merciai 2023, GHG emissions from Danish consumption 2016 "
                  "(2.-0 LCA for CONCITO), EXIOBASE v4 hybrid",
        script="analysis.danish_healthcare_benchmark",
        equations="match sector boundary (NACE Q) and capital treatment, then compare",
        inputs="boundary scenarios; capital scenarios; national totals"),
    "17_health_subsectors": dict(
        approach="Footprint by SHA health function, after Malik et al. 2018",
        reference="Malik et al. 2018 (Lancet Planet Health 2:e27) concordance method; "
                  "Malik et al. 2021 and Lenzen et al. 2020 for why native detail is needed",
        script="analysis.health_subsector_footprints",
        equations="total_k = m . y*_k with y*_k = E_k M_k; ranking decomposed into "
                  "expenditure and intensity effects",
        inputs="Danish expenditure by purpose code; prepared background"),
    "18_mitigation_scenarios": dict(
        approach="Mitigation levers an attributional EE-MRIO can credibly model",
        reference="Danske Regioner 2024 regional target; Danish Energy Agency KF22/KF25 "
                  "grid factors; Jeswani & Azapagic 2019; Wilkinson et al. 2019",
        script="analysis.mitigation_scenarios",
        equations="intensity scaling on energy nodes; bottom-up arithmetic; demand scaling",
        inputs="prepared background; scopes summary; DEA published emission factors"),
    "11_capital_endogenised": dict(
        approach="Capital endogenised with the published capital-use matrices",
        reference="Sodersten, Wood & Hertwich 2018 (ES&T 52:13250) eq. 13; capital "
                  "matrices Zenodo 10.5281/zenodo.7073276 CC BY 4.0; EXIOBASE MRSUT supply",
        script="analysis.capital_endogenised_sodersten",
        equations="D = V' qhat^-1 ; Kbar_ixi = D Kbar_pxi ; K = Kbar_ixi xhat^-1 ; "
                  "L^K = (I-(A+K))^-1",
        inputs="Kbar_exio_v3_8_2_2020_cfc_pxi.mat; MRSUT_2020 supply.csv; background"),
    "00_core_footprint": dict(
        approach="Core EE-MRIO final-demand footprint",
        reference="Steenmeijer et al. 2022; Miller & Blair 2009",
        script="analysis.export_tables / analysis.extended_indicators",
        equations="f = C S L y_H ; E[i,j] = s_i L_ij y_j",
        inputs="EXIOBASE v3.8.2 IOT_2022_ixi; DK expenditure vector"),
    "01_eriksen_replication": dict(
        approach="Eriksen/Steenmeijer replication outputs (corrected)",
        reference="Steenmeijer et al. 2022; Eriksen et al. NXSUST-D-26-01589",
        script="analysis.main_2025",
        equations="contribution B L diag(y); hotspot B diag(L y)",
        inputs="background pickle; DRIVHUS; AFFALD01; Danish bottom-up items"),
    "02_scopes_wood_hertwich": dict(
        approach="GHG Protocol scopes and the double-counting ledger",
        reference="Wood & Hertwich 2018 (ERL 13:104013) table 1, eqs. 1-2; GHG Protocol",
        script="analysis.scopes_detail / analysis.double_counting_audit",
        equations="S2 = d_E L_EE y_E ; S3 = f - S2 ; S1 from national accounts",
        inputs="background pickle; DRIVHUS; AFFALD01; bottom-up file"),
    "03_cabernard_target_scope3": dict(
        approach="Target-sector scope 3 without double counting",
        reference="Cabernard et al. 2019 (STOTEN 684:164-177) eqs. 8/9/12; 2022 SI",
        script="analysis.cabernard_target_scope3",
        equations="q_T = rowsum(Y_T + A_TO L'_OO Y_O); e_wdc = d L[:,T] diag(q_T); f_T",
        inputs="EXIOBASE A, Y, x; nested target sets T1/T2/T3"),
    "04_uncertainty_lenzen_ieooc": dict(
        approach="Monte Carlo parameter uncertainty and scenarios",
        reference="Lenzen et al. 2020 SI 7 (MRIO SD); IEooc Methods5 Exercise 4b",
        script="analysis.uncertainty_2025 / analysis.uncertainty_figures",
        equations="median-1 lognormal multipliers; exact first-order Sobol shares",
        inputs="01_eriksen_replication tables; published Danish health-care SD"),
    "05_waste_dst_accounts": dict(
        approach="Waste from Denmark's own SEEA accounts (domestic tier)",
        reference="Statistics Denmark AFFALD01 / AFF1MU1N / AFF3MU1N",
        script="analysis.waste_domestic_dst / analysis.waste_validation",
        equations="W = sum_i y_i m_i, m_i = DST direct+indirect waste multiplier",
        inputs="StatBank API; DK expenditure breakdown"),
    "06_benchmarks_validation": dict(
        approach="Benchmarks, national denominators and recipe validation",
        reference="Arup/HCWH 2019; Pichler 2019; Lenzen 2020; Eurostat FIGARO; DST AFTRYK",
        script="analysis.recipe_validation_2022 and assembled comparisons",
        equations="n/a (comparisons)",
        inputs="published values; env_ac_ghgfp; AFTRYK1; DST IO 2022"),
    "07_malik_replication": dict(
        approach="Malik-comparable variants and production layer decomposition",
        reference="Malik et al. 2018 (Lancet Planet Health 2:e27-35); Malik et al. 2021 (RCR 169:105556)",
        script="analysis.malik_replication / analysis.production_layers",
        equations="L = I + A + A^2 + ...; f^(n) = diag(s) A^n y; L_dom = (I - A_DK,DK)^-1",
        inputs="background pickle; Danish expenditure components"),
    "08_lenzen_replication": dict(
        approach="Lenzen KPI set reproduced for Denmark",
        reference="Lenzen et al. 2020 (Lancet Planet Health 4:e271-79) and SI",
        script="analysis.lenzen_replication",
        equations="F = q L y*; S_m and TE_m; import share; per-capita and intensity KPIs",
        inputs="background pickle; raw stressor blocks for PM10/NOx/SO2/reactive N"),
    "scenarios": dict(
        approach="Scope-boundary scenario runs",
        reference="SHA 2011 boundary; Steenmeijer expansive boundary",
        script="analysis.main_2025 with HC_SCOPE",
        equations="as 01_eriksen_replication", inputs="as 01_eriksen_replication"),
}


def main():
    root = str(OUTPUT_DIR)
    rows = []
    for sub, meta in APPROACHES.items():
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            continue
        for dirpath, _, files in os.walk(d):
            for fn in sorted(files):
                if fn.startswith("."):
                    continue
                fp = os.path.join(dirpath, fn)
                with open(fp, "rb") as fh:
                    h = hashlib.sha256(fh.read()).hexdigest()[:16]
                rows.append(dict(approach_folder=sub, file=os.path.relpath(fp, root),
                                 size_bytes=os.path.getsize(fp), sha256_16=h, **meta))
    df = pd.DataFrame(rows)
    df["generated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    df["monetary_unit"] = "M.EUR (EXIOBASE native); Danish sources in 1000 DKK / m DKK"
    df["country_coding"] = "ISO3 for countries; WA/WL/WE/WF/WM keep RoW region labels"
    out = os.path.join(root, "MANIFEST_lineage.csv")
    df.to_csv(out, index=False)
    print(df.groupby("approach_folder").size().to_string())
    print(f"\n{len(df)} gold files -> {out}")


if __name__ == "__main__":
    main()
