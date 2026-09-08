# -*- coding: utf-8 -*-
"""Steenmeijer et al. (2022) replication: Denmark against the Dutch template.

This study replicates Steenmeijer et al., *The environmental impact of the
Dutch health-care sector beyond climate change* (Lancet Planet Health 2022).
FAIR replication means being able to place our Danish result beside every number
they published, in their own table structure, for every impact category - not
only climate.

This module builds that comparison. Their published values are transcribed here
as a documented constant with provenance, so the comparison is reproducible
without re-reading the paper.

Comparability warnings, stated rather than buried
-------------------------------------------------
Three differences make a naive side-by-side misleading, and each is carried
explicitly in the output tables:

**Boundary.** The Dutch study uses the broad *zorg en welzijn* definition, which
**includes childcare and youth care**. Our default Danish boundary is health
plus eldercare. The like-for-like scenario is ``HC_SCOPE=zorg_en_welzijn``, and
both are reported.

**Waste.** Their waste extension sums all 19 hybrid fractions. Ours is filtered
to the statistical waste boundary (Regulation (EC) 2150/2002 / DST AFFALD01),
which excludes manure, sewage, mining and unused mining material. The two waste
numbers are therefore **not on the same boundary**, and the unfiltered Danish
figure is reported alongside for a like-for-like reading.

**Year and vintage.** Denmark 2022 on EXIOBASE v3.8.2 against the Netherlands
2016 on EXIOBASE v3. Absolute totals are not comparable across two different
economies; per-capita values are the meaningful comparison and are computed.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.steenmeijer_replication``
"""

from __future__ import annotations

import os
from typing import Any

import numpy as np
import pandas as pd

from analysis.constants import (ANALYSIS_YEAR, DK_POPULATION, INDICATORS,
                                eriksen_folder,
                                MODEL_LABEL)
from paths import OUTPUT_DIR

FOLDER = "13_steenmeijer_replication"

#: Netherlands population, 1 January 2016 (CBS), the reference year of the
#: Dutch study.
NL_POPULATION: int = 17_030_314

#: Published Dutch values, transcribed from Steenmeijer et al. (2022).
#: Source: the Lancet article's single table, "Environmental footprints by
#: top-down and bottom-up categories" (identical to RIVM report 2022-0159
#: table 8). ``NA`` in the paper means not applicable; ``··`` means not
#: assessed, and is carried here as ``numpy.nan``.
NL_TABLE: dict[str, dict[str, float]] = {
    "Total": dict(expenditure_meur=92_515, climate_change=17_575,
                  material_extraction=33_801, blue_water_consumption=394.0,
                  land_use=23_845, waste_generation=4_803),
    "Health-care services": dict(expenditure_meur=86_096, climate_change=10_779,
                                 material_extraction=14_714,
                                 blue_water_consumption=218.0,
                                 land_use=13_748, waste_generation=2_811),
    "Pharmaceuticals and chemical products": dict(
        expenditure_meur=3_778, climate_change=4_909,
        material_extraction=18_261, blue_water_consumption=169.0,
        land_use=9_744, waste_generation=1_780),
    "Medical appliances": dict(expenditure_meur=2_641, climate_change=864,
                               material_extraction=783,
                               blue_water_consumption=7.0, land_use=351,
                               waste_generation=212),
    "Release of anaesthetic gases": dict(
        expenditure_meur=np.nan, climate_change=14, material_extraction=np.nan,
        blue_water_consumption=np.nan, land_use=np.nan,
        waste_generation=np.nan),
    "Release of pMDI propellants": dict(
        expenditure_meur=np.nan, climate_change=77, material_extraction=np.nan,
        blue_water_consumption=np.nan, land_use=np.nan,
        waste_generation=np.nan),
    "Private travel": dict(expenditure_meur=np.nan, climate_change=932,
                           material_extraction=42,
                           blue_water_consumption=0.29, land_use=3,
                           waste_generation=np.nan),
}

#: Dutch national consumption footprints and the health-care share of each.
#: Source: supplementary table S7 (= RIVM table 9). Computed by the authors on
#: the unaltered Dutch final demand of the same EE-MRIO.
NL_NATIONAL: dict[str, dict[str, float]] = {
    "climate_change": dict(national=241_358, share_pct=7.3, unit="kt CO2eq"),
    "material_extraction": dict(national=259_060, share_pct=13.0, unit="kt"),
    "blue_water_consumption": dict(national=5_226, share_pct=7.5, unit="Mm3"),
    "land_use": dict(national=329_537, share_pct=7.2, unit="km2"),
    "waste_generation": dict(national=113_826, share_pct=4.2, unit="kt"),
}

#: Danish waste on the Dutch (unfiltered, all 19 fractions) boundary, for a
#: like-for-like reading. Regenerate with ``HC_WASTE_FRACTIONS=all``.
DK_WASTE_ALL_FRACTIONS_KT: float = 829.2

INDICATOR_UNIT: dict[str, str] = {name: unit for _, name, unit in INDICATORS}


def _load_components() -> pd.DataFrame:
    """Read the Danish footprint by demand component and indicator.

    Returns
    -------
    pandas.DataFrame
        Indexed by ``demand_component`` with one column per indicator, in the
        indicator's own unit.
    """
    path = os.path.join(str(OUTPUT_DIR), "00_core_footprint",
                        "footprint_by_purchased_product.csv")
    frame = pd.read_csv(path)
    return frame.pivot_table(index="demand_component", columns="indicator",
                             values="value", aggfunc="sum")


def _load_bottom_up() -> dict[str, float]:
    """Read the Danish bottom-up climate components, in kt CO2-equivalent.

    The three bottom-up rows of the template table have no counterpart in the
    MRIO component file, and the operational (scope 1) component belongs inside
    the health-care services row, as it does in the Dutch table.

    Returns
    -------
    dict
        Keys ``"operational"``, ``"anaesthetic"``, ``"pmdi"`` and ``"travel"``;
        travel is commuting plus patient and visitor travel, matching the Dutch
        "Private travel" row.

    Raises
    ------
    RuntimeError
        If an expected component is absent, rather than silently returning zero.
    """
    path = os.path.join(str(OUTPUT_DIR), *eriksen_folder().split("/"),
                        "scopes_summary.csv")
    frame = pd.read_csv(path).set_index("Component")["kt_CO2eq"]
    wanted = {
        "operational": "Scope 1 direct (DRIVHUS, excl. medical N2O)",
        "anaesthetic": "  + Anaesthetic gases (bottom-up)",
        "pmdi": "  + pMDI (bottom-up, use phase)",
        "commute": "  + Commute (bottom-up)",
        "patient_visitor": "Outside protocol (patient/visitor travel)",
    }
    missing = [label for label in wanted.values() if label not in frame.index]
    if missing:
        raise RuntimeError(f"scopes_summary.csv is missing: {missing}")
    values = {key: float(frame[label]) for key, label in wanted.items()}
    values["travel"] = values.pop("commute") + values.pop("patient_visitor")
    return values


def _load_national() -> pd.DataFrame:
    """Read the Danish national totals and the health-care share of each."""
    path = os.path.join(str(OUTPUT_DIR), "00_core_footprint",
                        "national_totals_summary.csv")
    return pd.read_csv(path).set_index("indicator")


def main() -> None:
    """Build and write the Denmark-versus-Netherlands comparison tables."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)

    components = _load_components()
    national = _load_national()
    bottom_up = _load_bottom_up()
    dk_population = DK_POPULATION[ANALYSIS_YEAR]

    component_map = {
        "Health-care services": "healthcare_services",
        "Pharmaceuticals and chemical products": "pharmaceuticals",
        "Medical appliances": "medical_appliances",
    }

    rows: list[dict[str, Any]] = []
    for row_name, published in NL_TABLE.items():
        for indicator, unit in INDICATOR_UNIT.items():
            nl_value = published.get(indicator, np.nan)
            key = component_map.get(row_name)
            if key is not None and key in components.index \
                    and indicator in components.columns:
                dk_value = float(components.loc[key, indicator])
                # the Dutch "Health-care services" row carries the sector's own
                # operational emissions; ours are added from national accounts
                if key == "healthcare_services" \
                        and indicator == "climate_change":
                    dk_value += bottom_up["operational"]
            elif row_name == "Release of anaesthetic gases":
                dk_value = bottom_up["anaesthetic"] \
                    if indicator == "climate_change" else np.nan
            elif row_name == "Release of pMDI propellants":
                dk_value = bottom_up["pmdi"] \
                    if indicator == "climate_change" else np.nan
            elif row_name == "Private travel":
                dk_value = bottom_up["travel"] \
                    if indicator == "climate_change" else np.nan
            elif row_name == "Total":
                dk_value = float(components[indicator].sum())
                if indicator == "climate_change":
                    dk_value += (bottom_up["operational"]
                                 + bottom_up["anaesthetic"]
                                 + bottom_up["pmdi"] + bottom_up["travel"])
            else:
                dk_value = np.nan
            rows.append(dict(
                table_row=row_name, indicator=indicator, unit=unit,
                netherlands_2016=nl_value, denmark_2022=dk_value,
                netherlands_per_capita=nl_value / NL_POPULATION * 1e6
                if np.isfinite(nl_value) else np.nan,
                denmark_per_capita=dk_value / dk_population * 1e6
                if np.isfinite(dk_value) else np.nan,
                per_capita_unit=f"{unit} per million population",
                dk_as_pct_of_nl_per_capita=(
                    100.0 * (dk_value / dk_population)
                    / (nl_value / NL_POPULATION)
                    if np.isfinite(dk_value) and np.isfinite(nl_value)
                    and nl_value != 0 else np.nan),
                source_netherlands="Steenmeijer et al. 2022, Lancet Planet "
                                   "Health, main table (= RIVM 2022-0159 "
                                   "table 8)",
                source_denmark=MODEL_LABEL))
    table = pd.DataFrame(rows)
    table.insert(0, "analysis_year_denmark", ANALYSIS_YEAR)
    table.insert(1, "reference_year_netherlands", 2016)
    table.to_csv(os.path.join(out_dir, "template_table_dk_vs_nl.csv"),
                 index=False)

    share_rows: list[dict[str, Any]] = []
    for indicator, published in NL_NATIONAL.items():
        dk = national.loc[indicator] if indicator in national.index else None
        dk_share = float(dk["healthcare_share_pct"]) if dk is not None \
            else np.nan
        dk_national = float(dk["national_footprint"]) if dk is not None \
            else np.nan
        note = ""
        if indicator == "waste_generation":
            note = ("NOT on the same boundary: the Dutch figure sums all 19 "
                    "hybrid waste fractions, ours is filtered to the "
                    "statistical waste boundary. On the Dutch boundary the "
                    f"Danish health-care figure is "
                    f"{DK_WASTE_ALL_FRACTIONS_KT:,.0f} kt.")
        share_rows.append(dict(
            indicator=indicator, unit=published["unit"],
            netherlands_national=published["national"],
            netherlands_health_share_pct=published["share_pct"],
            denmark_national=dk_national,
            denmark_health_share_pct=dk_share,
            share_difference_pp=dk_share - published["share_pct"],
            comparability_note=note,
            source_netherlands="Steenmeijer et al. 2022 table S7 "
                               "(= RIVM 2022-0159 table 9)",
            source_denmark=MODEL_LABEL))
    shares = pd.DataFrame(share_rows)
    shares.to_csv(os.path.join(out_dir, "national_shares_dk_vs_nl.csv"),
                  index=False)

    pd.set_option("display.width", 200)
    climate = table[table.indicator == "climate_change"]
    print("Template table, climate change (kt CO2eq):")
    print(climate[["table_row", "netherlands_2016", "denmark_2022",
                   "dk_as_pct_of_nl_per_capita"]]
          .to_string(index=False, max_colwidth=40))
    print("\nHealth-care share of the national footprint:")
    print(shares[["indicator", "netherlands_health_share_pct",
                  "denmark_health_share_pct", "share_difference_pp"]]
          .to_string(index=False))
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
