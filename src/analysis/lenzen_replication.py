# -*- coding: utf-8 -*-
"""Lenzen et al. (2020) KPI set, reproduced for Denmark.

Lenzen et al., 'The environmental footprint of health care: a global
assessment', Lancet Planet Health 4:e271-79, report a fixed set of per-country
indicators. This module reproduces every one of them that EXIOBASE can support,
so the Danish result is directly comparable with their published Danish row.

Equations (their eqs.; SI section 2):
    F   = q L y*                       footprint
    q   = Q xhat^-1                    direct intensities
    S_m = sum_{n<=m} q A^n y* / F      cumulative layer share (SI section 5)
    TE_m = 1 - S_m                     truncation error
    import share = 1 - tr(qhat L yhat*) / F

Indicator correspondence with their 7 families (see the notes column of the
output): climate change, PM (PM10 rows, matching their 'PM10 or less'), NOx,
SO2 (SO2 combustion + SOx non-combustion rows), reactive nitrogen to water.
NOT reproducible: malaria risk (an Eora-specific extension with no EXIOBASE
analogue) and scarce water (theirs is consumption weighted by a scarcity index;
EXIOBASE gives unweighted blue-water consumption, so it is reported as a
different concept and labelled as such).

Their published Danish values (2015, Eora) are carried in the output for
side-by-side comparison, with the caveat that Eora's Danish health expenditure
is roughly a third of the Danish national-accounts figure, so their LEVELS are
depressed and their intensity inflated; the transferable benchmarks are the
ratios (direct/supplier/higher-order split, truncation errors).

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.lenzen_replication
"""

import os
import pickle
import re

import numpy as np
import pandas as pd

from paths import BACKGROUND_DIR, MRIO_DIR, OUTPUT_DIR
from analysis.constants import DK_POPULATION, K_DK, N_SECTORS
from analysis.production_layers import layer_decomposition

# Lenzen's published Denmark row (2015, Eora), for comparison only
LENZEN_DK_2015 = {
    "climate_change": dict(total=3370.0, unit="kt CO2eq", direct=1030.0, supplier=460.0,
                           per_capita=0.59, share_national_pct=3.78, intensity=0.20,
                           note="SI Tab. 10.1/10.2/10.3/10.4; SI Tab. 7.1 gives 2.84 Mt +/- 0.24"),
    "particulate_matter": dict(total=25.01, unit="kt", note="SI Tab. 7.2, +/- 3.09"),
    "nox": dict(total=30.67, unit="kt", note="SI Tab. 7.3, +/- 3.02"),
    "so2": dict(total=27.75, unit="kt", note="SI Tab. 7.4, +/- 3.34"),
    "reactive_nitrogen_water": dict(total=1.87, unit="kt", note="SI Tab. 7.6, +/- 0.16"),
    "malaria_risk": dict(total=0.0022, unit="million people",
                         note="SI Tab. 7.5 - NOT reproducible in EXIOBASE"),
    "scarce_water": dict(total=8.67, unit="GL",
                         note="SI Tab. 7.7 - EXIOBASE gives unweighted blue water, a different concept"),
}
# extra Lenzen-family indicators built from the raw stressor blocks
EXTRA = [("particulate_matter", r"^PM10 .*- air$", "kg", 1e-6, "kt"),
         ("nox", r"^NOx .*- air$", "kg", 1e-6, "kt"),
         ("so2", r"^(SO2|SOx) .*- air$", "kg", 1e-6, "kt"),
         ("reactive_nitrogen_water", r"^N - .* - water$", "kg", 1e-6, "kt")]


def main():
    year = os.environ.get("HC_ANALYSIS_YEAR", "2022")
    bgy = "2022" if year == "2022" else "2016"
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{bgy}.pkl"), "rb") as fh:
        bg = pickle.load(fh)
    with open(os.path.join(str(MRIO_DIR), f"mrio{bgy}.pkl"), "rb") as fh:
        m = pickle.load(fh)
    A, L, B, Y, Ystim, Hstim = bg["A"], bg["L"], bg["B"], bg["Y"], bg["Ystim"], bg["Hstim"]
    names = [str(x) for x in m["label"]["extension"]["Name"]]
    R, x = m["R"], m["x"][:, 0]
    xinv = np.where(x > 0, 1.0 / np.where(x > 0, x, 1.0), 0.0)
    pop = DK_POPULATION[year]
    y_nat = Y[:, K_DK * 7:(K_DK + 1) * 7].sum(axis=1)
    expenditure_meur = float(pd.read_csv(
        os.path.join(str(BACKGROUND_DIR), "..", "inputs", "dk_data_2025.csv")
    ).query("Index == 'Expenditure'")[["HC service", "Pharm", "MedAppl"]].sum(axis=1).iloc[0])

    # intensity vectors: the five characterised rows plus the Lenzen-family extras
    series = [(B[0, :], "climate_change", "kt CO2eq", float(Hstim[0, 0])),
              (B[1, :], "material_extraction", "kt", float(Hstim[1, 0])),
              (B[2, :], "blue_water_consumption", "Mm3", float(Hstim[2, 0])),
              (B[3, :], "land_use", "km2", float(Hstim[3, 0])),
              (B[6, :], "waste_generation", "kt", float(Hstim[6, 0]))]
    for ind, pat, native, scale, unit in EXTRA:
        rx = re.compile(pat)
        idx = [i for i, n in enumerate(names) if rx.match(n)]
        series.append(((R[idx, :].sum(axis=0) * xinv) * scale, ind, unit, 0.0))

    rows = []
    for s, ind, unit, direct_extra in series:
        y_serv, y_goods = Ystim[:, 1], Ystim[:, 2] + Ystim[:, 3]
        lay_s, res_s = layer_decomposition(A, s, y_serv, max_layer=2, L=L)
        lay_g, res_g = layer_decomposition(A, s, y_goods, max_layer=2, L=L)
        f_total = float(s @ (L @ Ystim[:, 0])) + direct_extra
        direct = float(lay_g[0].sum()) + direct_extra
        supplier = float(lay_s[0].sum() + lay_g[1].sum())
        higher = f_total - direct - supplier
        nat = float(s @ (L @ y_nat))
        dom = float(s[K_DK * N_SECTORS:(K_DK + 1) * N_SECTORS]
                    @ (L @ Ystim[:, 0])[K_DK * N_SECTORS:(K_DK + 1) * N_SECTORS])
        ref = LENZEN_DK_2015.get(ind, {})
        rows.append(dict(
            indicator=ind, unit=unit, total=f_total,
            direct=direct, supplier_first_order=supplier, higher_order=higher,
            direct_pct=100 * direct / f_total, supplier_pct=100 * supplier / f_total,
            higher_order_pct=100 * higher / f_total,
            truncation_error_TE0_pct=100 * (1 - direct / f_total),
            truncation_error_TE1_pct=100 * (1 - (direct + supplier) / f_total),
            per_capita=f_total / pop * 1e6,          # kt per million people -> t/cap etc.
            national_total=nat, share_of_national_pct=100 * f_total / nat if nat else np.nan,
            intensity_per_meur=f_total / expenditure_meur,
            domestic_pct=100 * dom / f_total, import_pct=100 * (1 - dom / f_total),
            lenzen_dk_2015=ref.get("total"), lenzen_unit=ref.get("unit"),
            lenzen_note=ref.get("note")))
        print(f"  {ind:24s} {f_total:10,.1f} {unit:9s} | direct {100*direct/f_total:5.1f}% "
              f"supplier {100*supplier/f_total:5.1f}% higher {100*higher/f_total:5.1f}% | "
              f"imports {100*(1-dom/f_total):5.1f}%")

    # indicators Lenzen report that EXIOBASE cannot supply
    for ind in ("malaria_risk", "scarce_water"):
        ref = LENZEN_DK_2015[ind]
        rows.append(dict(indicator=ind, unit=ref["unit"], total=np.nan,
                         lenzen_dk_2015=ref["total"], lenzen_unit=ref["unit"],
                         lenzen_note=ref["note"]))

    df = pd.DataFrame(rows)
    df.insert(0, "analysis_year", year)
    df.insert(0, "consuming_country_iso3", "DNK")
    df["population"] = pop
    df["health_expenditure_meur"] = expenditure_meur
    out_dir = os.path.join(str(OUTPUT_DIR), "08_lenzen_replication")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "lenzen_kpi_set.csv")
    df.to_csv(out, index=False)
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
