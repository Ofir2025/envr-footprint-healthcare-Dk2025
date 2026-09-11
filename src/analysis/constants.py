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
# Defined once so that no module can silently pair one release's data with
# another's provenance label, and so that a model variant selected by
# HC_BACKGROUND_TAG propagates to every downstream table.
#
# The background is EXIOBASE v3.8.2, not v3.10.2: v3.10.2's 2022 nowcast
# misallocates the Danish block (health output 2.8x too low, education 4.8x too
# high, machinery and medical instruments near-zero) and empties industry 33
# across Europe in every year. See docs/methods/exiobase_release_and_classification.md.
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
# Source: IPCC (2021) AR6 WG1 Chapter 7, Table 7.15, with SF6 from the full
# version of that table, Supplementary Table 7.SM.7. Both are in
# data/bronze/characterisation/. Carbon-cycle responses are included: the note
# to Table 7.15 states they are included in every metric it presents, so the
# whole set is on one basis. AR6 distinguishes fossil from non-fossil methane,
# which the AR4 row did not: fossil CH4 carries the extra CO2 produced by its
# oxidation.
#
# Verified against the primary source on 9 September 2026, value by value:
# Table 7.15 gives CH4-fossil 29.8, CH4-non-fossil 27.0 and N2O 273; Table
# 7.SM.7 gives SF6 25,200. The GHG Protocol's AR6 adaptation (in the
# dk_kommune_footprints reference library) agrees on the first three and prints
# 24,300 for SF6. Where the two disagree this study follows the IPCC table it
# cites, not the adaptation.
#
# WHAT CANNOT BE RESTATED: EXIOBASE reports HFC and PFC already aggregated in
# kg CO2-equivalent rather than as individual species, so their GWP revision is
# fixed by EXIOBASE and is not knowable from the satellite account. Those two
# stressors keep a factor of 1 and are excluded from the restatement; the share
# of the footprint they represent is reported by analysis.gwp_revision.
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
        stressors, whose GWP revision cannot be recovered).

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


#: Name of the manuscript-replication folder for one analysis year.
#:
#: The study now reports more than one reference year, so the Eriksen outputs
#: are held in a year subfolder rather than one flat directory. Without this a
#: 2019 run would silently overwrite the 2022 headline, which is exactly the
#: accident the scope routing already guards against.
ERIKSEN_ROOT = "01_eriksen_replication"

#: Self-describing suffix appended to the analysis year to name the Eriksen
#: variant folder, keyed by ``HC_BACKGROUND_TAG``.
#:
#: The 2019-versus-2022 transport-share swing the manuscript reports (roughly
#: 46 % to 15-18 %) is not one comparison but three confounded ones: reference
#: year, background release, AND the Danish sea-transport reallocation, since
#: the 2019 replication was never shipping-corrected while 2022 was. Folding
#: "corrected or not" into the folder name (``2019_uncorrected`` versus
#: ``2019_shipping_corrected``) rather than leaving it implicit in whether
#: ``HC_BACKGROUND_TAG`` happened to be set is what lets a reader separate the
#: two effects: a bare year number never told anyone which correction state it
#: carried.
ERIKSEN_VARIANT_SUFFIX: dict[str, str] = {
    "": "uncorrected",
    "_snacship": "shipping_corrected",
}


def eriksen_variant(year: str | None = None, tag: str | None = None) -> str:
    """Self-describing ``<year>_<state>`` name for one Eriksen run.

    Parameters
    ----------
    year : str, optional
        Four-digit analysis year. Defaults to ``HC_ANALYSIS_YEAR``.
    tag : str, optional
        Background variant tag, e.g. ``"_snacship"``. Defaults to
        ``HC_BACKGROUND_TAG``.

    Returns
    -------
    str
        E.g. ``"2019_uncorrected"``, ``"2022_shipping_corrected"``.

    Examples
    --------
    >>> eriksen_variant("2019", "")
    '2019_uncorrected'
    >>> eriksen_variant("2022", "_snacship")
    '2022_shipping_corrected'
    """
    y = year or ANALYSIS_YEAR
    t = BACKGROUND_TAG if tag is None else tag
    suffix = ERIKSEN_VARIANT_SUFFIX.get(t, t.lstrip("_") or "uncorrected")
    return f"{y}_{suffix}"


def eriksen_folder(year: str | None = None, tag: str | None = None) -> str:
    """Return the Eriksen output folder for one (analysis year, background tag).

    Parameters
    ----------
    year : str, optional
        Four-digit analysis year. Defaults to the year this process is
        configured for (``HC_ANALYSIS_YEAR``).
    tag : str, optional
        Background variant tag. Defaults to ``HC_BACKGROUND_TAG``, so every
        existing call site (which never passes ``tag``) keeps resolving to
        whatever variant the process's environment already selects.

    Returns
    -------
    str
        Path relative to the gold results root, e.g.
        ``"01_eriksen_replication/2022_shipping_corrected"``.
    """
    return f"{ERIKSEN_ROOT}/{eriksen_variant(year, tag)}"


#: Root of the GHG-Protocol scope decomposition, year-scoped for the same reason
#: as the Eriksen folder: a 2019 run must not overwrite the 2022 tables that the
#: manuscript figures are drawn from.
SCOPES_ROOT = "02_scopes_wood_hertwich"


def scopes_folder(year: str | None = None) -> str:
    """Return the scope-decomposition output folder for one analysis year.

    Parameters
    ----------
    year : str, optional
        Four-digit analysis year. Defaults to the year this process is
        configured for (``HC_ANALYSIS_YEAR``).

    Returns
    -------
    str
        Path relative to the gold results root, e.g.
        ``"02_scopes_wood_hertwich/2022"``.
    """
    return f"{SCOPES_ROOT}/{year or ANALYSIS_YEAR}"
