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
