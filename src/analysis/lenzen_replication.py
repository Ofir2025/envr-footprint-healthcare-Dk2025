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

from analysis.constants import BACKGROUND_YEAR, MODEL_LABEL
from analysis.detail_tables import detail_rows, domestic_import_split
from paths import BACKGROUND_DIR, MRIO_DIR, OUTPUT_DIR, silver_dk_data_csv
from analysis.constants import (DK_POPULATION, K_DK, N_SECTORS,
                                require_manuscript_boundary)
from analysis.production_layers import layer_decomposition

# Lenzen's published Denmark row (2015, Eora), for comparison only
# ---------------------------------------------------------------------------
# HOW THIS COMPARISON MUST BE READ.
#
# Four properties of Lenzen et al.'s Danish record limit what it can benchmark,
# and each was verified against the paper and its supplementary information.
#
# 1. The Danish expenditure base is roughly HALF of reality. Their Tab. SI 10.2
#    gives Denmark 2,975 US$ per capita against Sweden 7,800, Norway 10,210 and
#    Finland 5,560 in the same table, when all four were about 5,000-6,500
#    US$/cap. Denmark's reported intensity of 0.20 kg CO2-e per US$ is therefore
#    the highest of the Nordic group as an ARTEFACT. **Their Danish intensity
#    and share-of-GDP figures are not usable benchmarks** and are carried here
#    only to be reported as such.
#
# 2. Two different Danish totals appear for the same country-year: 3.37 Mt
#    (Tab. SI 10.1, the headline) and 2.84 +/- 0.24 Mt (Tab. SI 7.1, the
#    uncertainty table). The gap is systematic across countries and indicators,
#    so the two SI sections appear to be different model runs. This study cites
#    SI 7.1 only for the RELATIVE standard deviation used to calibrate the Monte
#    Carlo, which is legitimate, and compares levels against SI 10.1.
#
# 3. Direct + supplier does not equal their total (1.03 + 0.46 != 3.37). Their
#    "supplier" column is first-order only, so 56 % of the Danish footprint is
#    unreported higher-order. Our own decomposition reports all three tiers.
#
# 4. The boundary differs. Their Danish health sector (Tab. SI 2.1) is
#    pharmaceutical manufacturing + hospital activities + medical, dental and
#    veterinary activities: pharmaceutical MANUFACTURING and VETERINARY care are
#    inside, and there is no social or residential care sector. Ours excludes
#    veterinary and includes eldercare. Capital is never mentioned in their
#    paper or SI.
# ---------------------------------------------------------------------------

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


def main() -> None:
    """Reproduce Lenzen et al.'s health-care KPI set on the Danish model.

    For each of the five headline indicators and the four Lenzen-family
    extras (particulate matter, NOx, SO2 and reactive nitrogen to water),
    computes the total footprint, its direct, first-order-supplier and
    higher-order layers, both truncation errors, the per-capita value, the
    national total, the share of it, the expenditure intensity and the
    domestic/imported split, and carries Lenzen's own published Danish row
    beside each. Writes ``lenzen_kpi_set.csv``,
    ``lenzen_kpi_by_producing_node.csv.gz``,
    ``lenzen_kpi_domestic_vs_imported.csv`` and
    ``lenzen_expenditure_base_check.csv`` to
    ``data/gold/results/08_lenzen_replication/``.

    The background actually loaded is ``analysis.constants.BACKGROUND_YEAR``,
    which carries both ``HC_ANALYSIS_YEAR`` and ``HC_BACKGROUND_TAG``, so the
    KPI totals are computed on the same background as the headline tables
    they are meant to be comparable with.
    """
    year = os.environ.get("HC_ANALYSIS_YEAR", "2022")
    bgy = BACKGROUND_YEAR
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
    _dk_path = silver_dk_data_csv(year)
    require_manuscript_boundary(_dk_path, "analysis.lenzen_replication")
    expenditure_meur = float(pd.read_csv(_dk_path)
                             .query("Index == 'Expenditure'")
                             [["HC service", "Pharm", "MedAppl"]]
                             .sum(axis=1).iloc[0])

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

    rows, node_frames = [], []
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
        # Producing-node decomposition. f = s . (L y), so the elementwise
        # product s * (L y) is the per-node contribution and sums to f exactly.
        by_node = s * (L @ Ystim[:, 0])
        node_frames.append(detail_rows(
            by_node, country_consuming="DNK",
            sector_consuming="health_and_eldercare", indicator=ind, unit=unit,
            model=MODEL_LABEL,
            quantity="Lenzen KPI, supply-chain component by producing node"))

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
    # ---- why Lenzen's Danish intensity cannot be used as a benchmark -----
    # Their table SI 10.2 gives Denmark 2,975 US$ per capita of health
    # expenditure and 4.44 % of GDP, against Sweden 7,800 and Norway 10,210 in
    # the same table. That makes their Danish intensity the highest in the
    # Nordic group, which is an artefact of the denominator. Part of the gap is
    # boundary - their Danish health sector is pharmaceutical manufacturing,
    # hospital activities and medical/dental/veterinary practice, excluding
    # residential care and social work - and part is unexplained.
    #: Danmarks Nationalbank annual average, and Statistics Denmark NAN1 GDP
    #: at current prices, both for the analysis year.
    dkk_per_eur = {"2019": 7.4661, "2022": 7.4396}[year]
    gdp_bn_dkk = {"2019": 2333.4, "2022": 2831.3}[year]
    gdp_bn_dkk_2022 = gdp_bn_dkk
    expenditure_bn_dkk = expenditure_meur * dkk_per_eur / 1e3
    base = pd.DataFrame([
        dict(quantity="Danish health expenditure, this study",
             value=expenditure_bn_dkk, unit="bn DKK current prices",
             source="Statistics Denmark IO tables, health + eldercare"),
        dict(quantity="as share of GDP", value=100 * expenditure_bn_dkk
             / gdp_bn_dkk_2022, unit="%",
             source="GDP from Statistics Denmark NAN1, current prices"),
        dict(quantity="per capita", value=expenditure_bn_dkk * 1e9 / pop
             / dkk_per_eur, unit="EUR per capita", source="derived"),
        dict(quantity="Lenzen et al. 2020 Danish share of GDP", value=4.44,
             unit="%", source="their table SI 10.2"),
        dict(quantity="ratio, this study to Lenzen",
             value=(100 * expenditure_bn_dkk / gdp_bn_dkk_2022) / 4.44,
             unit="-",
             source="their Danish expenditure base is roughly 2.4x too small, "
                    "so their Danish INTENSITY and share-of-GDP figures are "
                    "not usable benchmarks; their absolute footprint and "
                    "per-capita values remain usable"),
    ])
    base.to_csv(os.path.join(os.path.dirname(out),
                             "lenzen_expenditure_base_check.csv"), index=False)
    print(f"\n  expenditure base: {100 * expenditure_bn_dkk / gdp_bn_dkk_2022:.2f} % "
          f"of GDP against Lenzen's 4.44 % -> their Danish intensity is an artefact")

    df.to_csv(out, index=False)
    if node_frames:
        node_detail = pd.concat(node_frames, ignore_index=True)
        node_detail.to_csv(
            os.path.join(os.path.dirname(out),
                         "lenzen_kpi_by_producing_node.csv.gz"),
            index=False, compression={"method": "gzip", "mtime": 0})
        domestic_import_split(node_detail).to_csv(
            os.path.join(os.path.dirname(out),
                         "lenzen_kpi_domestic_vs_imported.csv"), index=False)
        print(f"  node detail: {len(node_detail):,} rows across "
              f"{node_detail.indicator.nunique()} indicators")
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
