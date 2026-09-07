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
    "00_core_footprint": dict(
        approach="Core EE-MRIO final-demand footprint",
        reference="Steenmeijer et al. 2022; Miller & Blair 2009",
        script="analysis.export_tables / analysis.extended_indicators",
        equations="f = C S L y_H ; E[i,j] = s_i L_ij y_j",
        inputs="EXIOBASE v3.10.2 IOT_2022_ixi (screened); DK expenditure vector"),
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
