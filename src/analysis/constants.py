# -*- coding: utf-8 -*-
"""Shared model constants.

These indices were previously duplicated across eight modules under two naming
conventions. They are defined once here so a classification change cannot leave
part of the pipeline pointing at the wrong sector.

Verified against EXIOBASE v3.10.2 (identical ordering in v3.7/v3.8.2):
  region 6  = DNK
  industry 137 = A_HEAL  Health and social work (85)
  industry  62 = A_CHEM  Chemicals nec              (pharmaceutical proxy)
  industry  89 = A_MEIN  Medical, precision and optical instruments (33)
"""

N_REGIONS = 49
N_SECTORS = 163
N_FINAL_DEMAND = 7
N_NODES = N_REGIONS * N_SECTORS

K_DK = 6
K_HEALTH = 137
K_PHARM = 62
K_APPL = 89

NODE_DK_HEALTH = K_DK * N_SECTORS + K_HEALTH
DK_BLOCK = slice(K_DK * N_SECTORS, (K_DK + 1) * N_SECTORS)

# characterisation rows of B / Hstim
ROW_GWP, ROW_MATERIAL, ROW_WATER, ROW_LAND, ROW_VA, ROW_EMPL, ROW_WASTE = range(7)

INDICATORS = [
    (ROW_GWP, "climate_change", "kt CO2eq"),
    (ROW_MATERIAL, "material_extraction", "kt"),
    (ROW_WATER, "blue_water_consumption", "Mm3"),
    (ROW_LAND, "land_use", "km2"),
    (ROW_WASTE, "waste_generation", "kt"),
]

DK_POPULATION = {"2019": 5_814_422, "2022": 5_873_420}


# ---------------------------------------------------------------------------
# Background model selection and provenance.
#
# Defined once so that no module can silently pair one vintage's data with
# another's provenance label, and so that a model variant selected by
# HC_BACKGROUND_TAG propagates to every downstream table.
#
# The background is EXIOBASE v3.8.2, not v3.10.2: v3.10.2's 2022 nowcast
# misallocates the Danish block (health output 2.8x too low, education 4.8x too
# high, machinery and medical instruments near-zero) and empties industry 33
# across Europe in every year. See docs/revision/exiobase_vintage_defects.md.
# ---------------------------------------------------------------------------

import os as _os

ANALYSIS_YEAR = _os.environ.get("HC_ANALYSIS_YEAR", "2022")
BACKGROUND_TAG = _os.environ.get("HC_BACKGROUND_TAG", "")
BACKGROUND_YEAR = ("2022" if ANALYSIS_YEAR == "2022" else "2016") + BACKGROUND_TAG

_VARIANT = {
    "": "",
    "_snacship": " with Danish sea-transport reallocation "
                 "(Rørmose Jensen & Iliev 2022)",
}


def model_label(year=None):
    """Provenance string for the background actually loaded."""
    y = (year or BACKGROUND_YEAR).replace(BACKGROUND_TAG, "") if BACKGROUND_TAG \
        else (year or BACKGROUND_YEAR)
    return (f"EXIOBASE v3.8.2 IOT_{y}_ixi"
            f"{_VARIANT.get(BACKGROUND_TAG, ' [' + BACKGROUND_TAG + ']')}")


MODEL_LABEL = model_label()


# ---------------------------------------------------------------------------
# Climate characterisation: IPCC AR6 GWP100.
#
# The characterisation workbook shipped with the background carries IPCC AR4
# factors (CH4 = 25, N2O = 298) under a sheet labelled "CML 1999". This study
# restates climate on AR6, the current assessment.
#
# Source: IPCC (2021) AR6 WG1 Chapter 7, Table 7.15 (GWP100, including
# carbon-cycle responses for non-CO2 gases, which is the set used for emission
# metrics). AR6 distinguishes fossil from non-fossil methane, which the AR4 row
# did not: fossil CH4 carries the extra CO2 produced by its oxidation.
#
# WHAT CANNOT BE RESTATED: EXIOBASE reports HFC and PFC already aggregated in
# kg CO2-equivalent rather than as individual species, so their GWP vintage is
# fixed by EXIOBASE and is not knowable from the satellite account. Those two
# stressors keep a factor of 1 and are excluded from the restatement; the share
# of the footprint they represent is reported by analysis.gwp_vintage.
# ---------------------------------------------------------------------------

#: IPCC AR6 GWP100 factors, kg CO2-equivalent per kg of gas.
AR6_GWP100 = {
    "CO2": 1.0,
    "CH4_fossil": 29.8,
    "CH4_biogenic": 27.0,
    "N2O": 273.0,
    "SF6": 25_200.0,
}

#: EXIOBASE stressor-name fragments that take the AR6 **fossil** methane factor
#: of 29.8. These are all FUGITIVE emissions: methane that escapes unburned from
#: gas and oil extraction, coal mining and refining.
#:
#: Combustion methane is deliberately NOT here. AR6's fossil factor is higher
#: than the non-fossil one because fossil methane oxidises to fossil CO2
#: (chapter 7: "methane from fossil fuel sources has slightly higher emissions
#: metric values than that from non-fossil sources"). For fuel combustion that
#: CO2 is already in the inventory, since combustion CO2 is derived from the
#: carbon content of the fuel, so applying 29.8 there would count the same
#: carbon twice. AR6 WG3 Annex II accordingly assigns 27.0 to fossil-combustion
#: methane. The distinction is worth only 1.55 kt on the Danish health-care
#: footprint (0.04 %), because EXIOBASE's combustion methane is small next to
#: its fugitive methane - it is applied for correctness, not for magnitude.
CH4_FOSSIL_MARKERS = (
    "Extraction/production of (natural) gas",
    "Extraction/production of crude oil",
    "Mining of antracite",
    "Mining of bituminous coal",
    "Mining of coking coal",
    "Mining of lignite",
    "Mining of sub-bituminous coal",
    "Oil refinery",
)


def ar6_gwp_factor(stressor: str) -> float | None:
    """Return the AR6 GWP100 factor for one EXIOBASE stressor name.

    Parameters
    ----------
    stressor : str
        The stressor label as it appears in the EXIOBASE satellite account,
        for example ``"CH4 - agriculture - air"``.

    Returns
    -------
    float or None
        The AR6 GWP100 factor, or ``None`` if the stressor is not one this
        restatement covers (which includes the pre-aggregated HFC and PFC
        stressors, whose vintage cannot be recovered).

    Examples
    --------
    >>> ar6_gwp_factor("CH4 - combustion - air")
    29.8
    >>> ar6_gwp_factor("CH4 - agriculture - air")
    27.0
    >>> ar6_gwp_factor("HFC - air") is None
    True
    """
    name = str(stressor)
    head = name.split(" - ")[0].strip().upper()
    if head == "CO2":
        return AR6_GWP100["CO2"]
    if head == "N2O":
        return AR6_GWP100["N2O"]
    if head == "SF6":
        return AR6_GWP100["SF6"]
    if head == "CH4":
        fossil = any(marker.lower() in name.lower()
                     for marker in CH4_FOSSIL_MARKERS)
        return AR6_GWP100["CH4_fossil" if fossil else "CH4_biogenic"]
    return None
