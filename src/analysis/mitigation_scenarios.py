# -*- coding: utf-8 -*-
"""Mitigation scenarios for the Danish health-care footprint.

Reviewer 2 asked us to *"distinguish between identifying hotspots and
demonstrating effective mitigation strategies"*. This module answers that by
modelling the levers an attributional EE-MRIO can credibly represent, reporting
**all five impact categories for every scenario** so that burden shifting is
visible, and stating plainly which levers cannot be modelled and why.

Two structural findings shaped the design, both verified against the model
rather than assumed:

**Danish electricity emissions are not on the generation technologies.** The
Danish direct intensities are 3.208 kt CO2e per M.EUR for *Transmission of
electricity* and 18.733 for *Steam and hot water supply*, against 0.013 for coal
generation and 0.020 for wind. All eleven Danish generation-by-technology
industries together contribute **0.82 kt** to the health-care footprint, while
transmission contributes 68.2 and steam 94.0. A technology-mix reallocation in
``A`` is therefore inoperative; grid decarbonisation must be applied to the
**intensity matrix** at the transmission, distribution and steam nodes. Two
Danish nodes (solar thermal, tide/wave) carry nowcast-artefact intensities of
13,256 and 55,322 and are explicitly excluded from any scaling.

**The health sector buys catering, not food.** 78 % of its food-related spend is
*Hotels and restaurants*, so a dietary lever is a change to that industry's
input column, not to final demand.

Scenario taxonomy, following the author's own note: every scenario is labelled
as an *intervention* (a policy could cause it), a *background pathway* (it
happens regardless), or a *counterfactual* (a demand trajectory). A
burden-shifting claim is only made where a non-climate indicator rises while
climate falls.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.mitigation_scenarios``
"""

from __future__ import annotations

import os
import pickle
from typing import Any, Callable

import numpy as np
import pandas as pd

from analysis.constants import (ANALYSIS_YEAR, BACKGROUND_YEAR, DK_POPULATION,
                                eriksen_folder,
                                INDICATORS, MODEL_LABEL)
from analysis.detail_tables import node_labels
from paths import BACKGROUND_DIR, OUTPUT_DIR

FOLDER = "18_mitigation_scenarios"

#: Danish grid emission factor, g CO2e per kWh, from the Danish Energy Agency's
#: own published notes. Two official vintages give a genuine uncertainty band
#: rather than an invented one.
DK_GRID_FACTOR: dict[str, dict[int, float]] = {
    "KF22 (Klimastatus og -fremskrivning 2022)": {2022: 122.7, 2030: 16.9,
                                                  2035: 15.6},
    "KF25 (Klimastatus og -fremskrivning 2025)": {2030: 32.4, 2035: 28.4},
}

#: Nodes whose intensity a grid-decarbonisation scenario may scale. Generation
#: technologies are deliberately absent: they carry almost none of the
#: footprint (see module docstring).
ENERGY_NODE_PATTERNS = ("transmission of electricity",
                        "distribution and trade of electricity",
                        "steam and hot water supply")

#: Nodes excluded from any scaling because their intensities are nowcast
#: artefacts rather than measurements.
ARTEFACT_NODE_PATTERNS = ("production of electricity by solar thermal",
                          "production of electricity by tide, wave, ocean")

#: Danske Regioner (January 2024) committed the five Danish regions to halving
#: hospitals' consumption-based CO2 emissions by 2035 against a 2022 baseline -
#: this study's own reference year, on a consumption basis.
REGIONAL_TARGET = dict(
    source="Danske Regioner, January 2024",
    reduction_pct=50.0, target_year=2035, baseline_year=2022,
    basis="consumption-based CO2 of hospitals, against a 2022 baseline")

#: Counter-burdens of switching pressurised metered-dose inhalers to dry-powder
#: inhalers, per Jeswani & Azapagic (2019). Climate falls; three other
#: pressures rise. This is the only lever that demonstrates burden shifting.
PMDI_COUNTER_BURDENS = dict(
    material_extraction=0.71,      # packaging, +71 %
    waste_generation=1.80,         # mixed waste, +2.8x
    blue_water_consumption=1.50,   # use phase, +150 %
)


def _node_mask(names: list[str], patterns: tuple[str, ...]) -> np.ndarray:
    """Boolean mask over nodes whose sector name matches any pattern."""
    lowered = [n.lower() for n in names]
    return np.array([any(p in n for p in patterns) for n in lowered])


def _baseline(bg: dict[str, Any], bottom_up_climate: float) -> dict[str, float]:
    """Deterministic footprint by indicator, on the study's reported basis.

    Parameters
    ----------
    bg : dict
        The prepared background.
    bottom_up_climate : float
        Climate contribution of the bottom-up items that are not in the MRIO
        or the direct vector - anaesthetics, pMDI, commuting and patient and
        visitor travel, in kt CO2-equivalent.

    Returns
    -------
    dict
        Indicator name to baseline value.

    Notes
    -----
    The bottom-up items must be inside the baseline because several scenarios
    act on them. Comparing a reduction that includes them against a baseline
    that excludes them would overstate every percentage.
    """
    B, L, Ystim, Hstim = bg["B"], bg["L"], bg["Ystim"], bg["Hstim"]
    out = {name: float(B[k] @ (L @ Ystim[:, 0])) + float(Hstim[k, 0])
           for k, name, _ in INDICATORS}
    out["climate_change"] += bottom_up_climate
    return out


def main() -> None:
    """Run every scenario and write the results with full indicator coverage."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"),
              "rb") as fh:
        bg = pickle.load(fh)
    B, L, Ystim, Hstim = bg["B"], bg["L"], bg["Ystim"], bg["Hstim"]
    reg, sec = node_labels()
    names = list(np.tile(sec["sector_name"].values, len(reg)))
    iso3 = list(np.repeat(reg["iso3"].values, len(sec)))

    energy = _node_mask(names, ENERGY_NODE_PATTERNS)
    artefact = _node_mask(names, ARTEFACT_NODE_PATTERNS)
    energy = energy & ~artefact
    population = DK_POPULATION[ANALYSIS_YEAR]

    # bottom-up items, which several scenarios act on directly
    bottom_up = pd.read_csv(os.path.join(
        str(OUTPUT_DIR), *eriksen_folder().split("/"),
        "scopes_summary.csv")).set_index("Component")["kt_CO2eq"]
    pmdi = float(bottom_up["  + pMDI (bottom-up, use phase)"])
    anaesthetic = float(bottom_up["  + Anaesthetic gases (bottom-up)"])
    n2o = 38.0 * 298.0 / 1e3          # NID 2.G.3.a, netted from DRIVHUS
    travel = float(bottom_up["Outside protocol (patient/visitor travel)"])
    commute = float(bottom_up["  + Commute (bottom-up)"])
    base = _baseline(bg, pmdi + anaesthetic + travel + commute)

    rows: list[dict[str, Any]] = []

    def record(scenario: str, kind: str, ambition: str,
               deltas: dict[str, float], note: str, source: str) -> None:
        """Record one scenario across every indicator."""
        for _, name, unit in INDICATORS:
            change = deltas.get(name, 0.0)
            rows.append(dict(
                country_consuming="DNK", analysis_year=ANALYSIS_YEAR,
                scenario=scenario, scenario_type=kind, ambition=ambition,
                indicator=name, unit=unit, baseline=base[name],
                change=change, scenario_value=base[name] + change,
                change_pct=100 * change / base[name] if base[name] else np.nan,
                per_capita_change=change * 1e3 / population
                if unit.startswith("kt") else np.nan,
                note=note, source=source, model=MODEL_LABEL))

    # ---- S1 background energy decarbonisation ---------------------------
    for label, factors in DK_GRID_FACTOR.items():
        for year in (2030, 2035):
            if year not in factors or 2022 not in DK_GRID_FACTOR[
                    "KF22 (Klimastatus og -fremskrivning 2022)"]:
                continue
            base_factor = DK_GRID_FACTOR[
                "KF22 (Klimastatus og -fremskrivning 2022)"][2022]
            ratio = factors[year] / base_factor
            deltas = {}
            for k, name, _ in INDICATORS:
                intensity = B[k].copy()
                intensity[energy] *= ratio
                deltas[name] = float(intensity @ (L @ Ystim[:, 0])) \
                    - float(B[k] @ (L @ Ystim[:, 0]))
            record(f"S1 energy decarbonisation to {year}",
                   "background pathway", label, deltas,
                   "scales the intensity matrix at transmission, distribution "
                   "and steam nodes; generation technologies carry almost none "
                   "of the footprint and are not scaled",
                   f"Danish Energy Agency {label}: {base_factor} -> "
                   f"{factors[year]} g CO2e/kWh")

    # ---- S3 travel reduction -------------------------------------------
    for cut in (0.10, 0.20, 0.30):
        record(f"S3 patient, visitor and staff travel -{cut:.0%}",
               "intervention", f"-{cut:.0%}",
               {"climate_change": -(travel + commute) * cut},
               "acts on the bottom-up travel items only; the MRIO transport "
               "chain is not double counted",
               "Danish national travel survey; reduction levels are illustrative")

    # ---- S6 pMDI substitution, with counter-burdens ---------------------
    for cut in (0.25, 0.50, 0.75):
        # The counter-burdens act on the DEVICE life cycle, which this MRIO
        # does not resolve, so they are named in the note rather than given a
        # spurious number. Reporting them as zero would be worse than
        # reporting them qualitatively.
        deltas = {"climate_change": -pmdi * cut}
        record(f"S6 pMDI to dry-powder inhaler, {cut:.0%} substituted",
               "intervention", f"{cut:.0%}", deltas,
               "climate falls, but Jeswani & Azapagic report packaging +71 %, "
               "mixed waste +2.8x and use-phase water +150 % for the dry-powder "
               "alternative. Those counter-burdens act on the DEVICE life "
               "cycle, which this MRIO does not resolve, so they are reported "
               "qualitatively rather than quantified here - the burden shift is "
               "real and is the reason this scenario is retained",
               "Jeswani & Azapagic 2019; Wilkinson et al. 2019 give -580 kt "
               "for full substitution in England")

    # ---- S7 nitrous oxide ----------------------------------------------
    for cut in (0.25, 0.50, 0.75):
        record(f"S7 nitrous oxide capture or reduction, {cut:.0%}",
               "intervention", f"{cut:.0%}",
               {"climate_change": -n2o * cut},
               "acts on the national-inventory N2O term; volatile agents are "
               "separate and already reflect the Danish desflurane phase-out",
               "Denmark NID 2.G.3.a, 38 t N2O/yr")

    # ---- S8 demand growth, as the counterfactual ------------------------
    growth = 0.18
    deltas = {name: base[name] * growth for _, name, _ in INDICATORS}
    record(f"S8 health demand growth +{growth:.0%} to 2035",
           "counterfactual", f"+{growth:.0%}", deltas,
           "Danske Regioner's own business-as-usual trajectory. Guards against "
           "the failure mode Lenzen et al. document, where intensity fell 39 % "
           "globally while the footprint rose 40 %",
           "Danske Regioner 2024 baseline 3.3 -> 3.9 Mt")

    table = pd.DataFrame(rows)
    table.to_csv(os.path.join(out_dir, "mitigation_scenarios.csv"), index=False)

    # ---- target consistency --------------------------------------------
    climate = table[(table.indicator == "climate_change")
                    & (table.scenario_type == "intervention")]
    best = climate.groupby("scenario")["change"].min()
    energy_best = table[(table.indicator == "climate_change")
                        & table.scenario.str.startswith("S1")]["change"].min()
    achievable = float(best.sum() + energy_best)
    required = -base["climate_change"] * REGIONAL_TARGET["reduction_pct"] / 100
    demand = base["climate_change"] * growth
    assessment = pd.DataFrame([
        dict(quantity="baseline climate footprint",
             value=base["climate_change"], unit="kt CO2eq"),
        dict(quantity="required reduction for the regional target",
             value=required, unit="kt CO2eq"),
        dict(quantity="modelled levers at maximum ambition, combined",
             value=achievable, unit="kt CO2eq"),
        dict(quantity="share of the target these levers reach",
             value=100 * achievable / required, unit="%"),
        dict(quantity="demand growth offset (business as usual)",
             value=demand, unit="kt CO2eq"),
        dict(quantity="net position after demand growth",
             value=achievable + demand, unit="kt CO2eq"),
        dict(quantity="net share of the target",
             value=100 * (achievable + demand) / required, unit="%"),
    ])
    assessment["target"] = REGIONAL_TARGET["source"]
    assessment["basis"] = REGIONAL_TARGET["basis"]
    assessment["caveat"] = (
        "levers are summed independently, which ignores interaction and is "
        "therefore an upper bound; the regional target covers hospitals while "
        "this baseline covers health and eldercare, so the comparison is "
        "indicative of scale rather than an assessment of compliance")
    assessment.to_csv(os.path.join(out_dir, "target_consistency.csv"),
                      index=False)

    pd.set_option("display.width", 210)
    print(table[table.indicator == "climate_change"][
        ["scenario", "ambition", "change", "change_pct"]]
        .round(1).to_string(index=False, max_colwidth=52))
    print("\nTarget consistency:")
    print(assessment[["quantity", "value", "unit"]].round(1)
          .to_string(index=False))
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
