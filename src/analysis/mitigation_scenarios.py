# -*- coding: utf-8 -*-
r"""Counterfactual scenarios for the Danish health-care footprint.

The second reviewer asked us to separate identifying a hotspot from showing that
acting on it works. This module answers that by modelling the levers an
attributional EE-MRIO can credibly represent, **for all five impact categories**
so that burden shifting is visible, and by stating which levers cannot be
modelled and why.

Every scenario is a full counterfactual solution of the Leontief system through
:mod:`analysis.scenario_engine`, following Aguilar-Hernandez et al. (2018) and
Donati et al. (2020): each edit carries a technical change coefficient
:math:`k_t` with a named source and a market penetration coefficient
:math:`k_p`, and the combined scenario applies every edit **simultaneously** and
re-solves, rather than summing separate answers.

Where the levers come from
--------------------------
Scenarios are grounded in stated Danish policy and in measured Danish outcomes
rather than invented ambition levels. The exceptions are labelled *illustrative*
in the ``ambition_basis`` column and nowhere else.

======  ==============================================  ==========================
ID      Lever                                            Evidence for ``k_t``
======  ==============================================  ==========================
B1      Grid and district-heat decarbonisation           Danish Energy Agency KF22 / KF25
B2      Danish demand growth to 2035                     Danske Regioner baseline
P1      Hospital energy and transport, -75 % by 2030     Danske Regioner (2020) target
P2      Pharmaceutical raw-material efficiency           Lundbeck, -15 % 2020-2022
P3      Medical-device packaging carbon                  Demant, -12 % to -23.5 %
P4      Reuse of medical equipment (lifetime extension)  Danske Regioner procurement focus
P5      Patient, visitor and staff travel                Danish national travel survey
P6      Low-charge pMDI / HFA-152a propellant            Jeswani & Azapagic (2019)
P7      pMDI to dry-powder inhaler                       Jeswani & Azapagic (2019)
P8      Nitrous oxide capture                            Denmark NID 2.G.3.a
P9      Divert health-care waste from incineration       Danish circular-plastic partnership
C1      All interventions, solved simultaneously         -
C2      C1 with expenditure held constant (rebound)      Takase et al. (2005) form
======  ==============================================  ==========================

Two structural findings shaped the design, both verified against this model
rather than assumed.

**Danish electricity emissions are not on the generation technologies.** The
Danish direct intensities are 3.208 kt CO2e per M.EUR for *Transmission of
electricity* and 18.733 for *Steam and hot water supply*, against 0.013 for coal
generation and 0.020 for wind. All eleven Danish generation-by-technology
industries together contribute 0.82 kt to the health-care footprint, while
transmission contributes 68.2 and steam 94.0. A technology-mix reallocation in
``A`` is therefore inoperative; grid decarbonisation must be applied to the
intensity matrix at the transmission, distribution and steam nodes. Two Danish
nodes (solar thermal, tide/wave) carry nowcast-artefact intensities of 13,256
and 55,322 and are excluded from any scaling.

**The health sector buys catering, not food.** 78 % of its food-related spend is
*Hotels and restaurants*, so a dietary lever is a change to that industry's
input column, not to final demand.

What is deliberately not modelled
---------------------------------
* **Price and market responses.** The model is attributional. A scenario is a
  what-if on the recipe, not a forecast of how the economy reacts.
* **"Green" versions of a product.** EXIOBASE has one *Chemicals nec* industry,
  so switching a hospital to a lower-impact supplier of the same product cannot
  be represented as a substitution; it can only appear as buying less. Green
  procurement is therefore modelled as volume reduction plus lifetime extension
  (P4), and the limitation is stated rather than papered over.
* **Capacity constraints and interaction with the rest of the economy.** The
  released Danish output is not re-employed unless the rebound scenario (C2) is
  used.

Run
---
``HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship PYTHONPATH=src
python -m analysis.mitigation_scenarios``

References
----------
Aguilar-Hernandez, G. A., Sigüenza-Sanchez, C. P., Donati, F., Rodrigues,
J. F. D., & Tukker, A. (2018). Assessing circularity interventions: A review of
EEIOA-based studies. *Journal of Economic Structures*, 7, 14.
https://doi.org/10.1186/s40008-018-0113-3

Donati, F., Aguilar-Hernandez, G. A., Sigüenza-Sánchez, C. P., de Koning, A.,
Rodrigues, J. F. D., & Tukker, A. (2020). Modeling the circular economy in
environmentally extended input-output tables: Methods, software and case study.
*Resources, Conservation and Recycling*, 152, 104508.
https://doi.org/10.1016/j.resconrec.2019.104508

Healthcare Denmark. (2024). *Transitioning towards a sustainable healthcare
sector* [White paper]. Healthcare Denmark.

Jeswani, H. K., & Azapagic, A. (2019). Life cycle environmental impacts of
inhalers. *Journal of Cleaner Production*, 237, 117733.
https://doi.org/10.1016/j.jclepro.2019.117733
"""

from __future__ import annotations

import os
import pickle
from typing import Any

import numpy as np
import pandas as pd

from analysis.constants import (ANALYSIS_YEAR, BACKGROUND_YEAR, DK_POPULATION,
                                INDICATORS, K_DK, MODEL_LABEL, N_SECTORS,
                                eriksen_folder)
from analysis.detail_tables import node_labels
from analysis.scenario_engine import (Edit, Scenario, apply_edits,
                                      column_imbalance, rebound_rescale, solve)
from paths import BACKGROUND_DIR, OUTPUT_DIR, SILVER_INPUT_DIR

FOLDER = "18_mitigation_scenarios"

#: Danish grid emission factor, g CO2e per kWh, from the Danish Energy Agency's
#: published projections. Two official releases give a real uncertainty band
#: rather than an invented one.
DK_GRID_FACTOR: dict[str, dict[int, float]] = {
    "KF22": {2022: 122.7, 2030: 16.9, 2035: 15.6},
    "KF25": {2030: 32.4, 2035: 28.4},
}

#: Nodes whose intensity a grid-decarbonisation scenario may scale. Generation
#: technologies are deliberately absent (see module docstring).
ENERGY_NODE_PATTERNS = ("transmission of electricity",
                        "distribution and trade of electricity",
                        "steam and hot water supply")

#: Excluded from any scaling: nowcast artefacts, not measurements.
ARTEFACT_NODE_PATTERNS = ("production of electricity by solar thermal",
                          "production of electricity by tide, wave, ocean")

#: Danske Regioner (2020) committed all Danish public hospitals to reducing
#: CO2 from energy and transport by 75 % by 2030 against 2018, and (January
#: 2024) to halving hospitals' consumption-based CO2 by 2035 against 2022.
REGIONAL_TARGET = dict(
    source="Danske Regioner, January 2024",
    reduction_pct=50.0, target_year=2035, baseline_year=2022,
    basis="consumption-based CO2 of hospitals, against a 2022 baseline")

#: Bottom-up items and the row of the bottom-up table that carries them.
BOTTOM_UP_ROWS = {"B_COMM": "Commute (total)",
                  "B_VISI": "Visitor travel (total)",
                  "B_PMDI": "pMDI",
                  "B_ANAE": "Anaesthetic"}

#: Column of the bottom-up table for each indicator.
BU_COLUMN = {"climate_change": "Global warming (ktCO2eq)",
             "material_extraction": "Material extraction (kt)",
             "blue_water_consumption": "Blue water consumption (Mm3)",
             "land_use": "Land use (km2)",
             "waste_generation": "Waste generation (kt)"}


def _node_mask(names: list[str], patterns: tuple[str, ...]) -> np.ndarray:
    """Boolean mask over nodes whose sector name matches any pattern."""
    lowered = [n.lower() for n in names]
    return np.array([any(p in n for p in patterns) for n in lowered])


def _dk_nodes(sector_positions: list[int]) -> np.ndarray:
    """Node indices of the given sector positions within the Danish block."""
    return np.array([K_DK * N_SECTORS + p for p in sector_positions])


def _sector_positions(sec: pd.DataFrame, codes: tuple[str, ...]) -> list[int]:
    """Positions of the given EXIOBASE sector codes."""
    idx = {c: i for i, c in enumerate(sec["sector_code"])}
    missing = [c for c in codes if c not in idx]
    if missing:
        raise AssertionError(f"sector codes not found: {missing}")
    return [idx[c] for c in codes]


def _all_region_nodes(sector_positions: list[int], n_regions: int) -> np.ndarray:
    """Node indices of the given sector positions in every region."""
    return np.array([r * N_SECTORS + p
                     for r in range(n_regions) for p in sector_positions])


def build_scenarios(bg: dict[str, Any], sec: pd.DataFrame, n_regions: int,
                    names: list[str]) -> list[Scenario]:
    """Assemble every scenario, with its evidence.

    Parameters
    ----------
    bg : dict
        The prepared background.
    sec : pandas.DataFrame
        Sector labels, from :func:`analysis.detail_tables.node_labels`.
    n_regions : int
        Number of regions in the model.
    names : list of str
        Sector name of every node, region-major.

    Returns
    -------
    list of Scenario
        Ordered so that the combined scenarios come last.
    """
    energy = _node_mask(names, ENERGY_NODE_PATTERNS) & ~_node_mask(
        names, ARTEFACT_NODE_PATTERNS)
    dk_energy = energy.copy()
    dk_energy[:K_DK * N_SECTORS] = False
    dk_energy[(K_DK + 1) * N_SECTORS:] = False

    chem = _sector_positions(sec, ("CHEM",))
    mein = _sector_positions(sec, ("MEIN",))
    heal = _sector_positions(sec, ("HEAL",))
    # P4 moves device spending into the industry that repairs and refurbishes
    # them. EXIOBASE has no repair industry, so this is *Other business
    # services*, which is where maintenance and refurbishment contracts sit.
    # The name is stated in the lever's note because the substitute is not what
    # the lever is called. Falling back to the health industry itself, as an
    # earlier version did, would have substituted the sector into its own
    # column without saying so.
    assert "OBUS" in set(sec["sector_code"]), (
        "P4 substitutes into Other business services (OBUS); this background "
        "does not carry that industry, so the lever cannot be built")
    repair = _sector_positions(sec, ("OBUS",))
    incin = _sector_positions(
        sec, tuple(c for c in ("INCF", "INCP", "INCL", "INCM", "INCT", "INCW",
                               "INCO") if c in set(sec["sector_code"])))
    recyc = _sector_positions(
        sec, tuple(c for c in ("RYMS", "PLAW", "BOTW")
                   if c in set(sec["sector_code"])))

    scenarios: list[Scenario] = []

    # ---- B1 background: grid and district-heat decarbonisation ----------
    #
    # Reported twice, because the evidence and the modelled scope differ. The
    # Danish Energy Agency projects the DANISH grid; applying that trajectory
    # to every region's energy nodes assumes the rest of the world decarbonises
    # at Denmark's projected rate, which no source here supports. So B1 is the
    # evidence-matched Denmark-only case and B1G is the global upper bound, and
    # the difference between them is reported rather than buried in a note.
    base_factor = DK_GRID_FACTOR["KF22"][2022]
    for release, factors in DK_GRID_FACTOR.items():
        for year in (2030, 2035):
            if year not in factors:
                continue
            k_t = 1.0 - factors[year] / base_factor
            src = (f"Danish Energy Agency {release}: {base_factor} -> "
                   f"{factors[year]} g CO2e/kWh")
            for sid, cols, scope, basis in (
                    ("B1", dk_energy, "Danish",
                     "the Danish grid, which is what the projection covers"),
                    ("B1G", energy, "every region",
                     "every region's grid, at Denmark's projected rate; an "
                     "upper bound, not an evidenced trajectory")):
                scenarios.append(Scenario(
                    sid=sid, name=f"grid and district heat, {scope}, {year}",
                    kind="background pathway",
                    ambition=f"{release} to {year}",
                    edits=(Edit(target="B", cols=np.flatnonzero(cols),
                                k_t=k_t, k_p=1.0, source=src,
                                penetration_basis=basis),),
                    note=("scales the intensity matrix at transmission, "
                          "distribution and steam nodes in " + scope +
                          "; generation technologies carry almost none of "
                          "the footprint and are not scaled")))

    # ---- P1 hospital energy and transport, Danske Regioner 2020 ---------
    for k_p in (0.5, 1.0):
        scenarios.append(Scenario(
            sid="P1", name="hospital energy and transport",
            kind="intervention",
            ambition=f"-75 % by 2030, {k_p:.0%} of the target met",
            edits=(Edit(target="y", rows=np.flatnonzero(dk_energy),
                        k_t=0.75, k_p=k_p,
                        source=("Danske Regioner (2020): all public hospitals "
                                "to cut CO2 from energy and transport by 75 % "
                                "by 2030 against 2018"),
                        penetration_basis=(
                            "share of the stated target actually met; both "
                            "half and full delivery are reported")),),
            note=("acts on the health sector's purchases of Danish "
                  "electricity, distribution and steam. The regions' own "
                  "measures - climate-friendly buildings, heating conversion, "
                  "hybrid ambulances - are inputs to this reduction, not "
                  "separate levers, and cannot be resolved individually in a "
                  "model with one health industry")))

    # ---- P2 pharmaceutical raw-material efficiency ----------------------
    for k_p in (0.25, 0.50, 1.00):
        scenarios.append(Scenario(
            sid="P2", name="pharmaceutical raw-material efficiency",
            kind="intervention",
            ambition=f"-15 % inputs, {k_p:.0%} of Danish production",
            edits=(Edit(target="A", cols=_dk_nodes(chem),
                        k_t=0.15, k_p=k_p,
                        source=("Lundbeck, reported in Healthcare Denmark "
                                "(2024): raw-material use down 15 % from 2020 "
                                "to 2022 while chemical production rose 18 %"),
                        penetration_basis=(
                            "share of Danish pharmaceutical output achieving "
                            "what one firm achieved; reported as a range "
                            "because that share is unknown")),),
            note=("a resource-efficiency edit on the input column of the "
                  "Danish chemicals industry - Aguilar-Hernandez et al. "
                  "(2018) section 4.4, lower input coefficients at the same "
                  "output. Only the Danish column is edited: a plant-level "
                  "Danish result is not evidence about chemical production "
                  "elsewhere")))

    # ---- P3 medical-device packaging ------------------------------------
    for k_t, lab in ((0.12, "-12 %"), (0.235, "-23.5 %")):
        scenarios.append(Scenario(
            sid="P3", name="medical-device packaging carbon",
            kind="intervention", ambition=f"{lab} cradle-to-gate",
            edits=(Edit(target="A", cols=_all_region_nodes(mein, n_regions),
                        rows=_all_region_nodes(
                            _sector_positions(sec, ("PAPE", "PLAS"))
                            if {"PAPE", "PLAS"} <= set(sec["sector_code"])
                            else chem, n_regions),
                        k_t=k_t, k_p=1.0,
                        source=("Demant, reported in Healthcare Denmark "
                                "(2024): 12 % to 23.5 % lower cradle-to-gate "
                                "packaging carbon across the hearing-aid "
                                "portfolio, using recycled PET"),
                        penetration_basis=(
                            "applied to the paper and plastics inputs of "
                            "medical-instrument manufacturing in every region")),),
            note=("packaging is not a separate EXIOBASE product, so the edit "
                  "acts on the paper and plastics inputs of the "
                  "medical-instruments column. That is broader than packaging "
                  "alone and therefore an upper bound on this lever")))

    # ---- P4 reuse of medical equipment, lifetime extension --------------
    for k_t in (0.10, 0.20):
        scenarios.append(Scenario(
            sid="P4", name="reuse of medical equipment",
            kind="intervention", ambition=f"-{k_t:.0%} device purchases",
            edits=(Edit(target="y", rows=_all_region_nodes(mein, n_regions),
                        k_t=k_t, k_p=1.0, alpha=0.30,
                        substitute_rows=_dk_nodes(repair),
                        source=("Danske Regioner procurement focus on reuse "
                                "of medical equipment, reported in Healthcare "
                                "Denmark (2024). The reduction level is "
                                "ILLUSTRATIVE - no Danish reuse rate is "
                                "published"),
                        penetration_basis="illustrative ambition"),),
            note=("product lifetime extension, Aguilar-Hernandez et al. "
                  "(2018) section 4.3: lower final demand for the device, "
                  "with 30 % of the saving reappearing as maintenance and "
                  "repair services rather than disappearing")))

    # ---- P5 travel, all five categories ---------------------------------
    for k_t in (0.10, 0.20, 0.30):
        scenarios.append(Scenario(
            sid="P5", name="patient, visitor and staff travel",
            kind="intervention", ambition=f"-{k_t:.0%}",
            edits=(Edit(target="bottom_up", key="B_COMM", k_t=k_t, k_p=1.0,
                        source="Danish national travel survey (TU) purpose 33",
                        penetration_basis="illustrative ambition"),
                   Edit(target="bottom_up", key="B_VISI", k_t=k_t, k_p=1.0,
                        source="Danish national travel survey (TU) purpose 33",
                        penetration_basis="illustrative ambition")),
            note=("acts on the bottom-up travel items in ALL FIVE categories - "
                  "the ecoinvent inventory behind them carries material, "
                  "water and land as well as greenhouse gases, and treating "
                  "the non-climate columns as zero understated this lever")))

    # ---- P6 propellant change, the better-evidenced inhaler lever -------
    for k_t, lab in ((0.67, "low-charge pMDI"), (0.93, "HFA-152a propellant")):
        scenarios.append(Scenario(
            sid="P6", name=f"inhaler propellant: {lab}",
            kind="intervention", ambition=f"-{k_t:.0%} propellant GWP",
            edits=(Edit(target="bottom_up", key="B_PMDI", k_t=k_t, k_p=1.0,
                        source=("Jeswani & Azapagic (2019): reducing propellant "
                                "by 67 % cuts the carbon footprint of use and "
                                "end-of-life by 67 %; replacing HFA-134a with "
                                "HFA-152a cuts it by 93 %"),
                        penetration_basis=(
                            "full substitution of the Danish pMDI stock; a "
                            "device change, not a change of therapy")),),
            note=("this lever is better evidenced than switching device class "
                  "and carries no therapeutic trade-off, because the "
                  "medicine and the delivery route are unchanged")))

    # ---- P7 device switch, with the burden shift named ------------------
    for k_t in (0.25, 0.50, 0.75):
        scenarios.append(Scenario(
            sid="P7", name="pMDI to dry-powder inhaler",
            kind="intervention", ambition=f"{k_t:.0%} substituted",
            edits=(Edit(target="bottom_up", key="B_PMDI", k_t=k_t, k_p=1.0,
                        source=("Jeswani & Azapagic (2019): dry-powder inhaler "
                                "GWP is 0.06 kg CO2e per 100 doses against "
                                "23.4 for the HFA inhaler, a factor of 380"),
                        penetration_basis="share of the pMDI stock switched"),),
            note=("BURDEN SHIFT, sourced and directional. Jeswani & Azapagic "
                  "report the dry-powder inhaler as WORSE than the HFA "
                  "inhaler for abiotic depletion of elements, eutrophication "
                  "and freshwater and terrestrial ecotoxicity. Those act on "
                  "the device life cycle, which this MRIO does not resolve, "
                  "so the direction is reported and the magnitude is not "
                  "invented. Dry-powder inhalers are also not clinically "
                  "suitable for every patient")))

    # ---- P8 nitrous oxide -----------------------------------------------
    for k_t in (0.25, 0.50, 0.75):
        scenarios.append(Scenario(
            sid="P8", name="nitrous oxide capture or reduction",
            kind="intervention", ambition=f"{k_t:.0%}",
            edits=(Edit(target="bottom_up", key="B_ANAE", k_t=k_t, k_p=0.60,
                        source=("Denmark National Inventory Document category "
                                "2.G.3.a: 38 t N2O per year"),
                        penetration_basis=(
                            "N2O is 60 % of the Danish anaesthetic-gas term; "
                            "the volatile agents are a separate item that "
                            "capture does not touch")),),
            note=("acts on the N2O share of the anaesthetic term only. The "
                  "volatile agents already reflect the Danish desflurane "
                  "phase-out and are not reduced again here")))

    # ---- P9 waste diversion ----------------------------------------------
    if incin and recyc:
        for k_t in (0.20, 0.40):
            scenarios.append(Scenario(
                sid="P9", name="divert health-care waste to recycling",
                kind="intervention", ambition=f"{k_t:.0%} of incineration",
                edits=(Edit(target="A", rows=_all_region_nodes(incin, n_regions),
                            cols=_dk_nodes(heal), k_t=k_t, k_p=1.0, alpha=1.0,
                            substitute_rows=_all_region_nodes(recyc, n_regions),
                            substitute_cols=_dk_nodes(heal),
                            source=("Circular Industrial Plastic partnership "
                                    "and the regions' stated focus on avoiding "
                                    "waste, Healthcare Denmark (2024). The "
                                    "diverted share is ILLUSTRATIVE"),
                            penetration_basis="illustrative ambition"),),
                note=("residual waste management, Aguilar-Hernandez et al. "
                      "(2018) section 4.1: the health industry's purchases of "
                      "incineration are moved to recycling services. EXIOBASE "
                      "resolves both explicitly, so this is a real "
                      "substitution rather than an intensity fudge")))

    return scenarios


def combine(scenarios: list[Scenario]) -> tuple[list[Scenario], list[Scenario]]:
    """Build the two combined scenarios from the most ambitious of each lever.

    Parameters
    ----------
    scenarios : list of Scenario
        The individual scenarios.

    Returns
    -------
    combined : list of Scenario
        ``C1`` (all interventions applied simultaneously), ``C2`` (the same
        with total final expenditure held constant) and ``C3`` (C1 plus the
        grid pathway).
    selected : list of Scenario
        The individual levers C1 was built from, one per lever. The naive sum
        and the waterfall figure must use exactly this set: selecting by the
        largest change instead, as they did, picks a different ambition level
        for any lever that worsens the indicator, and the difference between
        the sum and the combined solution then contains that mismatch rather
        than an interaction.

    Notes
    -----
    Summing the separate answers, which the previous implementation did, double
    counts every interaction: a lever that cuts electricity purchases and a
    lever that decarbonises electricity both claim the same avoided emission.
    Applying the edits together and re-solving prices that overlap correctly.
    P7 is excluded because it is an alternative to P6 on the same devices, not
    an addition to it.
    """
    best: dict[str, Scenario] = {}
    for s in scenarios:
        if s.kind != "intervention" or s.sid == "P7":
            continue
        prev = best.get(s.sid)
        if prev is None or sum(e.k_a for e in s.edits) > sum(
                e.k_a for e in prev.edits):
            best[s.sid] = s
    edits = tuple(e for s in best.values() for e in s.edits)
    note = ("every intervention at its most ambitious modelled level, applied "
            "simultaneously and re-solved. P7 is excluded as an alternative to "
            "P6 on the same devices. This is NOT the sum of the individual "
            "rows: overlapping levers are netted by the solution")
    # The background pathway is not a health-system lever, but the regions
    # meet their target in a decarbonising grid, so the policy-relevant
    # combination includes it. All three are reported.
    # The Denmark-only pathway, because it is the one the projection evidences.
    grid = max((s for s in scenarios if s.sid == "B1"),
               key=lambda s: sum(e.k_a for e in s.edits))
    selected = list(best.values())
    return [
        Scenario(sid="C1", name="all interventions combined",
                 kind="combined", ambition="maximum modelled", edits=edits,
                 note=note),
        Scenario(sid="C2", name="all interventions, expenditure held constant",
                 kind="combined", ambition="maximum modelled, with rebound",
                 edits=edits, rebound=True,
                 note=(note + ". Total final expenditure is held at the "
                       "baseline, so money not spent on one product is spent "
                       "on the rest of the basket")),
        Scenario(sid="C3", name="interventions and the grid pathway",
                 kind="combined",
                 ambition="maximum modelled, " + grid.ambition,
                 edits=edits + tuple(grid.edits),
                 note=(note + ". The grid pathway is added because the regions "
                       "meet their target in a decarbonising economy; it is "
                       "not something the health system causes")),
    ], selected


def main() -> None:
    """Run every scenario across all five categories and write the tables."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"),
              "rb") as fh:
        bg = pickle.load(fh)
    A, B, Ystim, Hstim = bg["A"], bg["B"], bg["Ystim"], bg["Hstim"]
    y0 = Ystim[:, 0]
    reg, sec = node_labels()
    n_regions = len(reg)
    names = list(np.tile(sec["sector_name"].values, n_regions))
    population = DK_POPULATION[ANALYSIS_YEAR]

    bu = pd.read_csv(os.path.join(str(SILVER_INPUT_DIR),
                                  "dk_bottomup_data_2025.txt"),
                     sep="\t").set_index("Source")

    def bottom_up_items(indicator: str, scale: dict[str, float] | None = None
                        ) -> dict[str, float]:
        """Bottom-up value per item for one indicator, after any scaling.

        Parameters
        ----------
        indicator : str
            One of the five impact categories.
        scale : dict of str to float, optional
            Reduction applied to an item, keyed by its bottom-up code.

        Returns
        -------
        dict of str to float
            One entry per bottom-up item, in the indicator's own unit.
        """
        col = BU_COLUMN[indicator]
        return {key: float(bu.loc[row, col]) * (1.0 - (scale or {}).get(key, 0.0))
                for key, row in BOTTOM_UP_ROWS.items()}

    def bottom_up(indicator: str, scale: dict[str, float] | None = None
                  ) -> float:
        """Bottom-up total for one indicator, with optional per-item scaling."""
        return sum(bottom_up_items(indicator, scale).values())

    # ---- baseline --------------------------------------------------------
    x0 = solve(A, y0)
    base: dict[str, float] = {}
    for k, name, _ in INDICATORS:
        base[name] = float(B[k] @ x0) + float(Hstim[k, 0]) + bottom_up(name)

    headline = pd.read_csv(os.path.join(
        str(OUTPUT_DIR), *eriksen_folder().split("/"),
        "scopes_summary.csv")).set_index("Component")["kt_CO2eq"]
    grand = float(headline["Grand Total"])
    assert abs(base["climate_change"] - grand) / grand < 0.01, (
        f"scenario baseline {base['climate_change']:,.1f} kt departs from the "
        f"study headline {grand:,.1f} kt by more than 1 %")

    scenarios = build_scenarios(bg, sec, n_regions, names)
    combined, selected = combine(scenarios)
    scenarios += combined
    #: (scenario_id, ambition) of the levers C1 was actually built from.
    in_c1 = {(s.sid, s.ambition) for s in selected}

    # The node vector B_alt[k] * x is what the dot product below collapses to a
    # scalar. Discarding it would leave the scenario layer as the one part of
    # the study with no detail behind its aggregates, so it is kept: every
    # scenario total is reproducible from this table by summation, which is the
    # property the rest of the gold layer is held to.
    node_rows: list[pd.DataFrame] = []
    reg_iso = np.repeat(reg["iso3"].to_numpy(), len(sec))
    reg_name = np.repeat(reg["country_name"].to_numpy(), len(sec))
    sec_code = np.tile(sec["sector_code"].to_numpy(), n_regions)
    sec_name = np.tile(sec["sector_name"].to_numpy(), n_regions)
    sec_group = np.tile(sec["sector_group"].to_numpy(), n_regions)

    rows: list[dict[str, Any]] = []
    for s in scenarios:
        scale = {e.key: e.k_a for e in s.edits
                 if e.target == "bottom_up" and e.key}
        A_alt, B_alt, y_alt, _ = apply_edits(A, B, y0, s.edits)
        if s.rebound:
            y_alt = rebound_rescale(y_alt, y0,
                                    edited=np.flatnonzero(y_alt < y0))
        x = x0 if A_alt is A and y_alt is y0 else solve(A_alt, y_alt)
        imbalance = column_imbalance(A_alt, A, x)
        for k, name, unit in INDICATORS:
            contrib = np.asarray(B_alt[k]).reshape(-1) * np.asarray(x).reshape(-1)
            items = bottom_up_items(name, scale)
            value = float(contrib.sum()) + float(Hstim[k, 0]) + sum(items.values())
            change = value - base[name]

            keep = np.flatnonzero(np.abs(contrib) > 0)
            frame = pd.DataFrame({
                "scenario_id": s.sid, "scenario": s.label,
                "ambition": s.ambition, "indicator": name,
                "unit": unit,
                "producing_country_iso3": reg_iso[keep],
                "producing_country_name": reg_name[keep],
                "producing_sector_code": sec_code[keep],
                "producing_sector_name": sec_name[keep],
                "producing_sector_group": sec_group[keep],
                "value_type": "supply chain",
                "value": contrib[keep]})
            extra = pd.DataFrame({
                "scenario_id": s.sid, "scenario": s.label,
                "ambition": s.ambition, "indicator": name,
                "unit": unit, "producing_country_iso3": "DNK",
                "producing_country_name": "Denmark",
                "producing_sector_code": ["B_HEAL", *items],
                "producing_sector_name": ["Direct impact from healthcare services",
                                          *(BOTTOM_UP_ROWS[key] for key in items)],
                "producing_sector_group": "Operational impact",
                "value_type": "bottom-up item",
                "value": [float(Hstim[k, 0]), *items.values()]})
            node_rows.append(pd.concat([frame, extra], ignore_index=True))
            rows.append(dict(
                country_consuming="DNK", analysis_year=ANALYSIS_YEAR,
                scenario_id=s.sid, scenario=s.label, scenario_type=s.kind,
                ambition=s.ambition, indicator=name, unit=unit,
                baseline=base[name], scenario_value=value, change=change,
                change_pct=100 * change / base[name] if base[name] else np.nan,
                # kt to kg, Mm3 to m3 and km2 to m2 are all a factor of a
                # million, so one conversion serves every indicator. The
                # previous factor of a thousand gave tonnes per person under a
                # column with no unit, which is how it went unnoticed.
                per_capita_change=change * 1e6 / population,
                per_capita_unit={"kt CO2eq": "kg CO2eq per capita",
                                 "kt": "kg per capita",
                                 "Mm3": "m3 per capita",
                                 "km2": "m2 per capita"}[unit],
                k_t=";".join(f"{e.k_t:g}" for e in s.edits),
                k_p=";".join(f"{e.k_p:g}" for e in s.edits),
                k_a=";".join(f"{e.k_a:g}" for e in s.edits),
                edited_objects=";".join(sorted({e.target for e in s.edits})),
                rebound=s.rebound,
                unbalanced_pct_of_output=imbalance,
                ambition_basis=" | ".join(
                    dict.fromkeys(e.penetration_basis for e in s.edits)),
                source=" | ".join(dict.fromkeys(e.source for e in s.edits)),
                note=s.note, model=MODEL_LABEL))
        del A_alt, B_alt, y_alt
    table = pd.DataFrame(rows)
    table.to_csv(os.path.join(out_dir, "mitigation_scenarios.csv"), index=False)

    # ---- the detail behind every aggregate above -------------------------
    detail = pd.concat(node_rows, ignore_index=True)
    detail.insert(0, "analysis_year", ANALYSIS_YEAR)
    detail.insert(0, "country_consuming", "DNK")
    detail["model"] = MODEL_LABEL
    key = ["scenario_id", "ambition", "indicator"]
    assert not table.duplicated(key).any(), (
        "the scenario table is not unique on " + ", ".join(key))
    check = (detail.groupby(key)["value"].sum().rename("detail").reset_index()
             .merge(table[key + ["scenario_value"]], on=key, validate="1:1"))
    worst = float((check["detail"] - check["scenario_value"]).abs().max())
    assert worst < 1e-6, (
        f"the scenario detail does not reproduce its own aggregate; worst "
        f"discrepancy {worst:.3e}")
    detail.to_csv(os.path.join(out_dir, "scenarios_by_producing_node.csv.gz"),
                  index=False, compression={"method": "gzip", "mtime": 0})
    pd.DataFrame([dict(scenario_id=s.sid, scenario=s.label, ambition=s.ambition,
                       in_combined="C1")
                  for s in selected]).to_csv(
        os.path.join(out_dir, "scenario_selection.csv"), index=False)
    print(f"  node detail {len(detail):,} rows, reproduces every scenario "
          f"total to {worst:.1e}")

    # ---- target consistency ---------------------------------------------
    climate = table[table.indicator == "climate_change"]
    combined = float(climate.loc[climate.scenario_id == "C1", "change"].iloc[0])
    with_grid = float(climate.loc[climate.scenario_id == "C3", "change"].iloc[0])
    rebounded = float(climate.loc[climate.scenario_id == "C2", "change"].iloc[0])
    # The naive sum must be taken over the SAME levers C1 contains, or the
    # difference is not an interaction term. P7 is an alternative to P6 on the
    # same devices and is excluded from both.
    picked = climate[[(r.scenario_id, r.ambition) in in_c1
                      for r in climate.itertuples()]]
    assert len(picked) == len(in_c1), (
        f"the naive sum covers {len(picked)} levers, C1 was built from "
        f"{len(in_c1)}")
    naive = float(picked["change"].sum())
    growth = 0.18
    demand = base["climate_change"] * growth
    required = -base["climate_change"] * REGIONAL_TARGET["reduction_pct"] / 100
    assessment = pd.DataFrame([
        dict(quantity="baseline climate footprint",
             value=base["climate_change"], unit="kt CO2eq"),
        dict(quantity="required reduction for the regional target",
             value=required, unit="kt CO2eq"),
        dict(quantity="all interventions, solved simultaneously (C1)",
             value=combined, unit="kt CO2eq"),
        dict(quantity="the same levers summed separately",
             value=naive, unit="kt CO2eq"),
        dict(quantity="interaction, i.e. what summing would overstate",
             value=naive - combined, unit="kt CO2eq"),
        dict(quantity="share of the target the interventions alone reach",
             value=100 * combined / required, unit="%"),
        dict(quantity="interventions with the grid pathway (C3)",
             value=with_grid, unit="kt CO2eq"),
        dict(quantity="share of the target with the grid pathway",
             value=100 * with_grid / required, unit="%"),
        dict(quantity="interventions with expenditure held constant (C2)",
             value=rebounded, unit="kt CO2eq"),
        dict(quantity="rebound, i.e. the saving respending removes",
             value=rebounded - combined, unit="kt CO2eq"),
        dict(quantity="demand growth offset (business as usual)",
             value=demand, unit="kt CO2eq"),
        dict(quantity="net position, grid pathway included",
             value=with_grid + demand, unit="kt CO2eq"),
    ])
    assessment["target"] = REGIONAL_TARGET["source"]
    assessment["basis"] = REGIONAL_TARGET["basis"]
    assessment["caveat"] = (
        "the regional target covers hospitals while this baseline covers "
        "health and eldercare, so the comparison is indicative of scale rather "
        "than an assessment of compliance; levers are applied simultaneously "
        "and re-solved, so the combined figure is not an upper bound in the "
        "way a naive sum would be")
    assessment.to_csv(os.path.join(out_dir, "target_consistency.csv"),
                      index=False)

    # ---- burden shifting -------------------------------------------------
    shift = (table.pivot_table(index=["scenario_id", "scenario", "ambition"],
                               columns="indicator", values="change_pct")
             .reset_index())
    ind_cols = [c for c in shift.columns if c in BU_COLUMN]
    others = [c for c in ind_cols if c != "climate_change"]
    # Burden shifting: climate improves while some other pressure worsens.
    shift["shifts_burden"] = ((shift["climate_change"] < -1e-9)
                              & (shift[others] > 1e-9).any(axis=1))
    # Backfire: the lever makes climate worse. A different failure, and one a
    # reader must not have to infer from a sign.
    shift["backfires_on_climate"] = shift["climate_change"] > 1e-9
    # Several bottom-up levers act on items for which no non-climate inventory
    # exists, so their zeros mean "not resolved", not "no effect".
    shift["non_climate_resolved"] = ~shift["scenario_id"].isin(
        {"P6", "P7", "P8"})
    shift.to_csv(os.path.join(out_dir, "burden_shifting.csv"), index=False)

    pd.set_option("display.width", 220)
    print(climate[["scenario", "ambition", "change", "change_pct"]]
          .round(2).to_string(index=False, max_colwidth=46))
    print("\nTarget consistency:")
    print(assessment[["quantity", "value", "unit"]].round(1)
          .to_string(index=False))
    print(f"\nBurden shifting: {int(shift['shifts_burden'].sum())} of "
          f"{len(shift)} scenarios improve climate while worsening another "
          f"pressure; {int(shift['backfires_on_climate'].sum())} worsen "
          f"climate itself")
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
