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
# HC_EXIOBASE_RELEASE / HC_BACKGROUND_TAG / HC_CAPITAL propagates to every
# downstream table.
#
# THE RELEASE IS AN INPUT, NOT A CONSTANT. It used to be neither: a single
# symlink (data/bronze/exiobase/IOT_2016_ixi) decided which release the 2019
# replication ran on, while model_label() stamped the string "EXIOBASE v3.8.2"
# from a literal. A run on v3.7 would therefore have produced gold rows
# claiming v3.8.2, and the submitted 2019 estimate - which was computed on
# v3.7 - was silently being reproduced on v3.8.2 instead. Every gold row must
# say which release actually produced it, so the release is selected by
# HC_EXIOBASE_RELEASE, carried in the background's file name, recorded in the
# background's own "source" field at build time, and read back from there.
#
# The default release is v3.8.2, not v3.10.2: v3.10.2's 2022 nowcast
# misallocates the Danish block (health output 2.8x too low, education 4.8x too
# high, machinery and medical instruments near-zero) and empties industry 33
# across Europe in every year. See docs/methods/exiobase_release_and_classification.md.
# ---------------------------------------------------------------------------

import json as _json
import os as _os

ANALYSIS_YEAR = _os.environ.get("HC_ANALYSIS_YEAR", "2022")
BACKGROUND_TAG = _os.environ.get("HC_BACKGROUND_TAG", "")

#: EXIOBASE release this process is configured for, from
#: ``HC_EXIOBASE_RELEASE``. :data:`paths.EXIOBASE_RELEASE` reads the same
#: variable, so bronze path resolution and provenance cannot disagree.
EXIOBASE_RELEASE = (_os.environ.get("HC_EXIOBASE_RELEASE", "v3_8_2").strip()
                    or "v3_8_2")

#: Capital treatment, from ``HC_CAPITAL``: ``"excluded"`` (the headline, capital
#: formation outside the boundary) or ``"endogenised"`` (consumption of fixed
#: capital inside the Leontief inverse, after Södersten et al. 2018).
CAPITAL = _os.environ.get("HC_CAPITAL", "excluded").strip() or "excluded"

#: Sector boundary, from ``HC_SCOPE``. ``"health_eldercare"`` is the submitted
#: boundary (SHA health plus residential eldercare); ``"health_only"`` drops
#: eldercare; ``"zorg_en_welzijn"`` adds child care, matching the expansive
#: Dutch boundary of Steenmeijer et al. (2022).
SCOPE = _os.environ.get("HC_SCOPE", "health_eldercare").strip() or "health_eldercare"

#: Printed release name, keyed by the release key used in paths and env vars.
RELEASE_LABEL: dict[str, str] = {
    "v3_7": "v3.7",
    "v3_8_2": "v3.8.2",
    "v3_10_2": "v3.10.2",
}

#: Suffix the release contributes to a background file stem. v3.8.2 is the
#: study's default and its pickles predate this scheme, so it contributes no
#: suffix and those files keep their names; every other release is tagged, the
#: same convention ``pipelines.prep_background_2022`` already uses for
#: ``mrio2022_v3_10_2.pkl``. Two releases can therefore coexist on disk.
RELEASE_TAG: dict[str, str] = {
    "v3_7": "_v3_7",
    "v3_8_2": "",
    "v3_10_2": "_v3_10_2",
}

#: EXIOBASE table years each release actually publishes. v3.7 (2019) stops at
#: 2016: it has no 2022 table and cannot be given one, which is why the 2022
#: series has no v3.7 variants.
#:
#: This is a property of the release, not of what happens to be downloaded here,
#: and it was verified against the Zenodo record rather than inferred from the
#: local tree: record 3583071 (v3.7) publishes ``IOT_<year>_ixi`` for 1995-2016,
#: 22 tables; record 5589597 (v3.8.2) publishes 1995-2022, 28 tables. There is
#: therefore no v3.7 2019 table to test variant a against, and none to be
#: obtained: variant a runs on ``IOT_2016_ixi`` because that is the newest table
#: its release has, which is also why the submitted manuscript analysed 2019
#: expenditure on a 2016 background.
#:
#: The tuples below list the years this study builds backgrounds for, which is a
#: subset of what each release publishes.
RELEASE_TABLE_YEARS: dict[str, tuple[str, ...]] = {
    "v3_7": ("2016",),
    "v3_8_2": ("2016", "2022"),
    "v3_10_2": ("2022",),
}

#: Suffix the capital treatment contributes to a background file stem.
CAPITAL_TAG: dict[str, str] = {
    "excluded": "",
    "endogenised": "_capital",
}

#: Suffix the sector boundary contributes to the PREPARED background's stem.
#:
#: The boundary does not change the EXIOBASE table, so ``mrio<stem>.pkl`` and
#: ``leontief<stem>.pkl`` never carry it; it does change the demand vector
#: ``Ystim`` that ``functions_2025.createBackground`` builds, so
#: ``gddz_background_information_<stem>.pkl`` must. Without it, a run on the
#: wider care boundary wrote its childcare-inclusive demand vector into the
#: file name the manuscript boundary owns, and every downstream module that
#: reads the background got the wrong boundary's numbers.
SCOPE_TAG: dict[str, str] = {
    "health_eldercare": "",
    "health_only": "_health_only",
    "zorg_en_welzijn": "_zorg_en_welzijn",
}

#: The care boundary the manuscript reports, and the only one the year-scoped
#: silver frames are ever written for.
MANUSCRIPT_BOUNDARY = "health_eldercare"


def require_manuscript_boundary(path: str | _os.PathLike[str],
                                reader: str) -> None:
    """Refuse to read a manuscript-boundary silver frame on another boundary.

    ``dk_data_<year>.csv`` and ``dk_expenditure_breakdown_<year>.csv`` are
    scoped on the YEAR and not on the care boundary, because
    :mod:`analysis.main_2025` writes them only for
    :data:`MANUSCRIPT_BOUNDARY` and skips the write for every other one. The
    files therefore have exactly one possible boundary by construction, and a
    boundary suffix in the name would distinguish nothing.

    What the name could not prevent is a reader on a *different* boundary
    opening them anyway and publishing the manuscript boundary's expenditure
    as that boundary's own. That is prevented here instead of in the name, and
    prevented out loud: the caller is told which boundary it is on, which file
    it tried to read, and what to run.

    Parameters
    ----------
    path : str or os.PathLike
        The silver frame about to be read. Named in the message so the caller
        does not have to find it.
    reader : str
        Module doing the read, e.g. ``"analysis.lenzen_replication"``.

    Returns
    -------
    None
        On the manuscript boundary, where the read is legitimate.

    Raises
    ------
    SystemExit
        On any other boundary.
    """
    if SCOPE == MANUSCRIPT_BOUNDARY:
        return
    raise SystemExit(
        f"{reader} reads {path}, which analysis.main_2025 writes only for "
        f"HC_SCOPE={MANUSCRIPT_BOUNDARY}; this run is on HC_SCOPE={SCOPE!r}, "
        f"so the file holds the manuscript boundary's expenditure and not this "
        f"run's. Run {reader} on the manuscript boundary, or give this module "
        f"its own boundary-scoped input before running it on another one.")


def table_year(analysis_year: str | None = None) -> str:
    """EXIOBASE table year behind one analysis year.

    Parameters
    ----------
    analysis_year : str, optional
        Four-digit analysis year. Defaults to ``HC_ANALYSIS_YEAR``.

    Returns
    -------
    str
        ``"2022"`` for the 2022 analysis year; ``"2016"`` for anything else,
        since the 2019 replication runs on the 2016 table.

        Two different reasons, both established rather than assumed. On v3.7
        there is no 2019 table at all: that release publishes 1995-2016 (Zenodo
        record 3583071). On v3.8.2 a 2019 table exists, and it is **defective
        for this study's industry**: it puts Danish health and social work at
        18,646 M.EUR against the national accounts' 39,059, a ratio of 0.48,
        and 2018 is the same. Running 2019 expenditure against the 2016 table
        is therefore not a limitation inherited from v3.7 but the only correct
        choice v3.8.2 offers. See
        ``09_exiobase_release_diagnostics/dk_health_output_by_release.csv``.

    Examples
    --------
    >>> table_year("2019")
    '2016'
    >>> table_year("2022")
    '2022'
    """
    return "2022" if (analysis_year or ANALYSIS_YEAR) == "2022" else "2016"


def background_stem(analysis_year: str | None = None,
                    release: str | None = None,
                    tag: str | None = None,
                    capital: str | None = None,
                    scope: str | None = None) -> str:
    """File stem identifying one background on disk.

    The stem is what ``mrio<stem>.pkl``, ``leontief<stem>.pkl`` and
    ``gddz_background_information_<stem>.pkl`` are named after, so it must
    carry every axis that changes the numbers: table year, EXIOBASE release,
    Danish sea-transport correction, and capital treatment. Two backgrounds
    that differ on any of them cannot then overwrite each other.

    Parameters
    ----------
    analysis_year : str, optional
        Four-digit analysis year. Defaults to ``HC_ANALYSIS_YEAR``.
    release : str, optional
        Release key. Defaults to ``HC_EXIOBASE_RELEASE``.
    tag : str, optional
        Sea-transport correction tag, ``""`` or ``"_snacship"``. Defaults to
        ``HC_BACKGROUND_TAG``.
    capital : str, optional
        ``"excluded"`` or ``"endogenised"``. Defaults to ``HC_CAPITAL``.
    scope : str, optional
        Sector boundary. Defaults to ``HC_SCOPE``. Contributes a suffix only
        to the PREPARED background (see :data:`SCOPE_TAG`); strip it with
        :func:`mrio_stem` to address the EXIOBASE pickles.

    Returns
    -------
    str
        E.g. ``"2016"``, ``"2016_v3_7"``, ``"2022_snacship"``,
        ``"2022_snacship_capital"``.

    Examples
    --------
    >>> background_stem("2019", "v3_7", "", "excluded")
    '2016_v3_7'
    >>> background_stem("2022", "v3_8_2", "_snacship", "endogenised")
    '2022_snacship_capital'
    >>> background_stem("2022", "v3_8_2", "_snacship", "endogenised",
    ...                 "zorg_en_welzijn")
    '2022_snacship_capital_zorg_en_welzijn'
    """
    t = BACKGROUND_TAG if tag is None else tag
    return (table_year(analysis_year)
            + RELEASE_TAG.get(release or EXIOBASE_RELEASE,
                              f"_{release or EXIOBASE_RELEASE}")
            + t
            + CAPITAL_TAG.get(capital or CAPITAL, "")
            + SCOPE_TAG.get(scope or SCOPE, ""))


def mrio_stem(stem: str | None = None) -> str:
    """Stem of the EXIOBASE pickles behind a prepared background.

    The sector boundary changes the demand vector, not the table, so it is
    carried by ``gddz_background_information_<stem>.pkl`` and not by
    ``mrio<stem>.pkl`` / ``leontief<stem>.pkl``. This drops the boundary
    suffix so one stem can address both.

    Parameters
    ----------
    stem : str, optional
        Background stem. Defaults to :data:`BACKGROUND_YEAR`.

    Returns
    -------
    str
        The same stem with any :data:`SCOPE_TAG` suffix removed.

    Examples
    --------
    >>> mrio_stem("2022_snacship_capital_zorg_en_welzijn")
    '2022_snacship_capital'
    >>> mrio_stem("2016_v3_7")
    '2016_v3_7'
    """
    s = stem or BACKGROUND_YEAR
    for suffix in SCOPE_TAG.values():
        if suffix and s.endswith(suffix):
            return s[: -len(suffix)]
    return s


def split_background_stem(stem: str) -> tuple[str, str, str, str]:
    """Decompose a background stem into the four axes that built it.

    The inverse of :func:`background_stem`, so a module holding only a file
    name can recover what produced it without consulting the environment - the
    property that makes a gold row's provenance readable after the fact.

    Parameters
    ----------
    stem : str
        Background stem, e.g. ``"2016_v3_7_snacship"``.

    Returns
    -------
    tuple of str
        ``(table_year, release, tag, capital)``.

    Examples
    --------
    >>> split_background_stem("2016_v3_7_snacship")
    ('2016', 'v3_7', '_snacship', 'excluded')
    >>> split_background_stem("2022_snacship_capital")
    ('2022', 'v3_8_2', '_snacship', 'endogenised')
    """
    rest = mrio_stem(stem)
    year, rest = rest[:4], rest[4:]
    capital = "excluded"
    if rest.endswith("_capital"):
        capital, rest = "endogenised", rest[: -len("_capital")]
    tag = ""
    if rest.endswith("_snacship"):
        tag, rest = "_snacship", rest[: -len("_snacship")]
    release = "v3_8_2"
    for key, suffix in RELEASE_TAG.items():
        if suffix and rest == suffix:
            release = key
            break
    return year, release, tag, capital


BACKGROUND_YEAR = background_stem()

_VARIANT = {
    "": "",
    "_snacship": " with Danish sea-transport reallocation "
                 "(Rørmose Jensen & Iliev 2022)",
}

_CAPITAL_CLAUSE = {
    "excluded": "",
    "endogenised": " and capital endogenised (Södersten et al. 2018)",
}

#: File name of the small sidecar recording which release built a background.
#: Written beside the pickle by the build stage, read by :func:`model_label`.
RELEASE_SIDECAR = "{stem}.release.json"


def write_release_sidecar(mrio_dir: str, stem: str, release: str,
                          source: str) -> str:
    """Record, beside a background pickle, which release produced it.

    The pickle itself carries the same string in its ``"source"`` field, but a
    background is 1.1 GB and :func:`model_label` is called at import time by a
    dozen modules, so the provenance is mirrored into a few hundred bytes of
    JSON that can be read without unpickling a gigabyte.

    Parameters
    ----------
    mrio_dir : str
        Directory holding the pickles (``paths.MRIO_DIR``).
    stem : str
        Background stem the sidecar describes, from :func:`background_stem`.
    release : str
        Release key, e.g. ``"v3_7"``.
    source : str
        Full provenance string, as stored in the pickle's ``"source"`` field.

    Returns
    -------
    str
        Path written.
    """
    path = _os.path.join(mrio_dir, RELEASE_SIDECAR.format(stem=stem))
    with open(path, "w", encoding="utf-8") as fh:
        _json.dump({"stem": stem, "release": release, "source": source}, fh,
                   ensure_ascii=False, indent=1)
    return path


def release_of_background(stem: str | None = None) -> str:
    """Which EXIOBASE release produced the background with this stem.

    Read, in order, from the sidecar the build stage wrote beside the pickle
    (which mirrors the pickle's own ``"source"`` field) and then from the
    stem's own release tag. **Never from a constant**: the whole point is that
    a gold row states the release that actually produced it, and a literal in
    this module is exactly what made that impossible before.

    Parameters
    ----------
    stem : str, optional
        Background stem. Defaults to :data:`BACKGROUND_YEAR`, the background
        this process is configured for.

    Returns
    -------
    str
        Release key, e.g. ``"v3_7"`` or ``"v3_8_2"``.
    """
    s = stem or BACKGROUND_YEAR
    try:
        from paths import MRIO_DIR
        path = _os.path.join(str(MRIO_DIR), RELEASE_SIDECAR.format(stem=s))
        with open(path, encoding="utf-8") as fh:
            recorded = str(_json.load(fh)["release"])
        if recorded:
            return recorded
    except (OSError, KeyError, ValueError):
        pass
    return split_background_stem(s)[1]


def model_label(year: str | None = None) -> str:
    """Provenance string for the background actually loaded.

    Parameters
    ----------
    year : str, optional
        Background stem, i.e. a four-digit table year possibly carrying the
        release, ``HC_BACKGROUND_TAG`` and capital suffixes (e.g.
        ``"2016_v3_7_snacship"``). Defaults to :data:`BACKGROUND_YEAR`. The
        suffixes are stripped before formatting, since each is reported
        separately in the returned string.

    Returns
    -------
    str
        E.g. ``"EXIOBASE v3.8.2 IOT_2022_ixi with Danish sea-transport
        reallocation (Rørmose Jensen & Iliev 2022)"``, or ``"EXIOBASE v3.7
        IOT_2016_ixi"``. The release comes from
        :func:`release_of_background` - the background's own record of what
        built it - not from a literal in this module.

    Examples
    --------
    >>> model_label("2016_v3_7")
    'EXIOBASE v3.7 IOT_2016_ixi'
    """
    stem = year or BACKGROUND_YEAR
    table, _release_from_stem, tag, capital = split_background_stem(stem)
    release = release_of_background(stem)
    return (f"EXIOBASE {RELEASE_LABEL.get(release, release)} IOT_{table}_ixi"
            f"{_VARIANT.get(tag, ' [' + tag + ']')}"
            f"{_CAPITAL_CLAUSE.get(capital, '')}")


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
# data/bronze/exiobase_characterisation/. Carbon-cycle responses are included: the note
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
    >>> ar6_gwp_factor("CH4 - agriculture - air")
    27.0
    >>> ar6_gwp_factor("CH4 - combustion - air")  # combustion is not fugitive
    27.0
    >>> ar6_gwp_factor("CH4 - Oil refinery - air")
    29.8
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

#: Root of the GHG-Protocol scope decomposition. Variant-scoped for the same
#: reason as the Eriksen folder, and on the same axes: the scope tables are the
#: source of manuscript figures 3-6, so a run for one year or one correction
#: state must not overwrite another's.
SCOPES_ROOT = "02_scopes_wood_hertwich"
#: The four model variants the author defines, keyed by the letter that names
#: their result folder (``01_eriksen_replication/2019a`` and so on).
#:
#: A variant is a point in a FOUR-dimensional configuration space - EXIOBASE
#: release, Danish sea-transport correction, sector boundary, capital treatment
#: - not the two-state "corrected or not" the folder names used to carry. The
#: 2019-versus-2022 transport-share swing the manuscript reports (roughly 46 %
#: to 15-18 %) is not one comparison but several confounded ones, and a folder
#: name that says only the year and the correction state cannot separate them:
#: ``2019_uncorrected`` was read as "the submitted run" when it is in fact
#: v3.8.2 without the correction, whereas the submitted estimate was computed
#: on v3.7.
#:
#: The letters are the author's choice, and they order the variants along the
#: path from the submitted estimate to the fullest boundary: ``a`` reproduces
#: what was submitted, ``b`` adds the Danish correction, ``c`` moves to the
#: current release, ``d`` widens the care boundary and brings capital inside
#: the Leontief inverse.
VARIANTS: dict[str, dict[str, str]] = {
    "a": {
        "release": "v3_7",
        "tag": "",
        "scope": "health_eldercare",
        "capital": "excluded",
        "summary": "EXIOBASE v3.7, no Danish shipping correction, health-care "
                   "boundary, capital excluded - the submitted configuration",
    },
    "b": {
        "release": "v3_7",
        "tag": "_snacship",
        "scope": "health_eldercare",
        "capital": "excluded",
        "summary": "EXIOBASE v3.7, Danish shipping correction, health-care "
                   "boundary, capital excluded",
    },
    "c": {
        "release": "v3_8_2",
        "tag": "_snacship",
        "scope": "health_eldercare",
        "capital": "excluded",
        "summary": "EXIOBASE v3.8.2, Danish shipping correction, health-care "
                   "boundary, capital excluded - the headline configuration",
    },
    "d": {
        "release": "v3_8_2",
        "tag": "_snacship",
        "scope": "zorg_en_welzijn",
        "capital": "endogenised",
        "summary": "EXIOBASE v3.8.2, Danish shipping correction, health care "
                   "plus child and elder care, capital endogenised",
    },
}

#: Reverse index of :data:`VARIANTS`, built once so no module re-derives it.
_VARIANT_LETTER: dict[tuple[str, str, str, str], str] = {
    (cfg["release"], cfg["tag"], cfg["scope"], cfg["capital"]): letter
    for letter, cfg in VARIANTS.items()
}

#: Words naming the sea-transport correction state, used ONLY to name a
#: configuration that is not one of the author's four (see
#: :func:`variant_name`). The lettered variants never reach it.
_CORRECTION_STATE: dict[str, str] = {
    "": "uncorrected",
    "_snacship": "shipping_corrected",
}


def variant_letter(release: str | None = None, tag: str | None = None,
                   scope: str | None = None,
                   capital: str | None = None) -> str | None:
    """Letter naming one of the author's four variants, or ``None``.

    Parameters
    ----------
    release : str, optional
        EXIOBASE release key, ``"v3_7"`` or ``"v3_8_2"``. Defaults to
        ``HC_EXIOBASE_RELEASE``.
    tag : str, optional
        Sea-transport correction tag, ``""`` or ``"_snacship"``. Defaults to
        ``HC_BACKGROUND_TAG``.
    scope : str, optional
        Sector boundary, ``"health_eldercare"`` or ``"zorg_en_welzijn"``.
        Defaults to ``HC_SCOPE``.
    capital : str, optional
        ``"excluded"`` or ``"endogenised"``. Defaults to ``HC_CAPITAL``.

    Returns
    -------
    str or None
        ``"a"`` .. ``"d"`` when the four settings are one of the author's
        variants, else ``None``. ``None`` is a real answer, not a failure:
        v3.8.2 without the shipping correction is a configuration this study
        has published (``2019_uncorrected``) and it is deliberately NOT
        variant a, since variant a is on v3.7.

    Examples
    --------
    >>> variant_letter("v3_7", "", "health_eldercare", "excluded")
    'a'
    >>> variant_letter("v3_8_2", "_snacship", "zorg_en_welzijn", "endogenised")
    'd'
    >>> variant_letter("v3_8_2", "", "health_eldercare", "excluded") is None
    True
    """
    return _VARIANT_LETTER.get((
        release or EXIOBASE_RELEASE,
        BACKGROUND_TAG if tag is None else tag,
        scope or SCOPE,
        capital or CAPITAL))


def variant_config(letter: str) -> dict[str, str]:
    """The four settings that define one lettered variant.

    Parameters
    ----------
    letter : str
        Variant letter, ``"a"`` .. ``"d"``.

    Returns
    -------
    dict of str to str
        ``release``, ``tag``, ``scope``, ``capital`` and a one-line
        ``summary``, plus the derived ``release_label``, ``shipping``,
        ``boundary`` and ``capital_treatment`` used verbatim in variant
        readmes and provenance columns.

    Raises
    ------
    KeyError
        If ``letter`` is not one of the four variants.

    Examples
    --------
    >>> variant_config("a")["release_label"]
    'v3.7'
    >>> variant_config("d")["boundary"]
    'health care plus child and elder care'
    """
    cfg = dict(VARIANTS[letter])
    cfg["letter"] = letter
    cfg["release_label"] = RELEASE_LABEL[cfg["release"]]
    cfg["shipping"] = "yes" if cfg["tag"] else "no"
    cfg["boundary"] = ("health care plus child and elder care"
                       if cfg["scope"] == "zorg_en_welzijn"
                       else "health care" if cfg["scope"] == "health_eldercare"
                       else "health care excluding eldercare")
    cfg["capital_treatment"] = cfg["capital"]
    cfg["table_years"] = ", ".join(RELEASE_TABLE_YEARS[cfg["release"]])
    return cfg


#: Configurations this study publishes that are NOT one of the author's four
#: lettered variants, with the same four axes and a note on why each is kept.
#:
#: ``2019_uncorrected`` is deliberately not variant a. Variant a is on EXIOBASE
#: v3.7, the release the submitted manuscript used; these two are v3.8.2 without
#: the Danish sea-transport correction. Giving either of them the letter a would
#: assert a reproduction of the submitted estimate that it does not perform -
#: which is exactly the confusion a folder named only by year and correction
#: state allowed, since the transport bridge was measured on ``2019_uncorrected``
#: and reported as the submitted configuration.
UNLETTERED_VARIANTS: dict[str, dict[str, str]] = {
    "2019_uncorrected": {
        "release": "v3_8_2",
        "tag": "",
        "scope": "health_eldercare",
        "capital": "excluded",
        "summary": "EXIOBASE v3.8.2 IOT_2016_ixi, no Danish shipping "
                   "correction, health-care boundary, capital excluded - not "
                   "variant a, which is on v3.7",
    },
    "2022_uncorrected": {
        "release": "v3_8_2",
        "tag": "",
        "scope": "health_eldercare",
        "capital": "excluded",
        "summary": "EXIOBASE v3.8.2 IOT_2022_ixi, no Danish shipping "
                   "correction, health-care boundary, capital excluded",
    },
}


def variant_axes(name: str) -> dict[str, str] | None:
    """The four axes behind a variant folder name, or ``None``.

    The inverse of :func:`variant_name`, so a module holding only a path can
    recover which release, correction, boundary and capital treatment produced
    the tables under it - which is what lets a provenance check verify a gold
    row against its own folder instead of against one hardcoded release.

    Parameters
    ----------
    name : str
        Variant folder name or a path ending in one, e.g. ``"2019a"`` or
        ``"01_eriksen_replication/2019_uncorrected/table_01.csv"``. Every
        component is tried, so a full file path resolves.

    Returns
    -------
    dict of str to str or None
        ``release``, ``tag``, ``scope``, ``capital`` and ``summary``, or
        ``None`` when no component of ``name`` is a variant folder.

    Examples
    --------
    >>> variant_axes("2019a")["release"]
    'v3_7'
    >>> variant_axes("01_eriksen_replication/2022_uncorrected")["tag"]
    ''
    >>> variant_axes("00_core_footprint") is None
    True
    """
    for part in str(name).replace("\\\\", "/").split("/"):
        letter = part[4:]
        if part[:4].isdigit() and letter in VARIANTS:
            return dict(VARIANTS[letter])
        if part in UNLETTERED_VARIANTS:
            return dict(UNLETTERED_VARIANTS[part])
    return None


def variant_description(name: str) -> str:
    """One-line configuration of a variant folder, from its name alone.

    Parameters
    ----------
    name : str
        Variant folder name, e.g. ``"2019a"`` or ``"2019_uncorrected"``. A
        path is accepted too, in which case its last component is used.

    Returns
    -------
    str
        The variant's ``summary``, or an empty string when the name is not a
        variant folder at all.

    Examples
    --------
    >>> variant_description("2022d")
    'EXIOBASE v3.8.2, Danish shipping correction, health care plus child and elder care, capital endogenised'
    >>> variant_description("01_eriksen_replication/2019a").startswith('EXIOBASE v3.7')
    True
    >>> variant_description("00_core_footprint")
    ''
    """
    axes = variant_axes(str(name).rstrip("/").split("/")[-1])
    return axes["summary"] if axes else ""


def variant_name(year: str | None = None, release: str | None = None,
                 tag: str | None = None, scope: str | None = None,
                 capital: str | None = None) -> str:
    """Folder name for one model run: ``<year><letter>``.

    Parameters
    ----------
    year : str, optional
        Four-digit analysis year. Defaults to ``HC_ANALYSIS_YEAR``.
    release : str, optional
        Release key. Defaults to ``HC_EXIOBASE_RELEASE``.
    tag : str, optional
        Sea-transport correction tag. Defaults to ``HC_BACKGROUND_TAG``.
    scope : str, optional
        Sector boundary. Defaults to ``HC_SCOPE``.
    capital : str, optional
        Capital treatment. Defaults to ``HC_CAPITAL``.

    Returns
    -------
    str
        ``"2019a"`` .. ``"2022d"`` for the author's four variants. A
        configuration outside them keeps a self-describing name instead of
        being given a letter it has not been assigned - ``"2019_uncorrected"``
        for v3.8.2 with no correction, and the release appended when it is not
        the default release.

    Examples
    --------
    >>> variant_name("2019", "v3_7", "", "health_eldercare", "excluded")
    '2019a'
    >>> variant_name("2022", "v3_8_2", "_snacship", "zorg_en_welzijn", "endogenised")
    '2022d'
    >>> variant_name("2019", "v3_8_2", "", "health_eldercare", "excluded")
    '2019_uncorrected'
    """
    y = year or ANALYSIS_YEAR
    letter = variant_letter(release, tag, scope, capital)
    if letter is not None:
        return f"{y}{letter}"
    rel = release or EXIOBASE_RELEASE
    t = BACKGROUND_TAG if tag is None else tag
    parts = [y]
    if RELEASE_TAG.get(rel, f"_{rel}"):
        parts.append(rel)
    parts.append(_CORRECTION_STATE.get(t, t.lstrip("_") or "uncorrected"))
    sc = scope or SCOPE
    if sc != "health_eldercare":
        parts.append(sc)
    if (capital or CAPITAL) != "excluded":
        parts.append("capital")
    return "_".join(parts)


def variant_folder(root: str, year: str | None = None,
                   release: str | None = None, tag: str | None = None,
                   scope: str | None = None,
                   capital: str | None = None) -> str:
    """Return one layer's output folder for one variant.

    The single resolver behind :func:`eriksen_folder` and
    :func:`scopes_folder`. Both layers vary on the same four axes and are read
    by the same figure scripts, so they name their folders from one rule; a
    layer that resolved a variant of its own would put figures drawn from two
    layers on two different backgrounds without saying so, which is exactly
    what a bare year number did to figures 3-6.

    Parameters
    ----------
    root : str
        Layer folder under the gold results root, e.g. :data:`ERIKSEN_ROOT` or
        :data:`SCOPES_ROOT`.
    year : str, optional
        Four-digit analysis year. Defaults to ``HC_ANALYSIS_YEAR``.
    release : str, optional
        Release key. Defaults to ``HC_EXIOBASE_RELEASE``.
    tag : str, optional
        Sea-transport correction tag. Defaults to ``HC_BACKGROUND_TAG``.
    scope : str, optional
        Sector boundary. Defaults to ``HC_SCOPE``.
    capital : str, optional
        Capital treatment. Defaults to ``HC_CAPITAL``.

    Returns
    -------
    str
        Path relative to the gold results root, e.g.
        ``"02_scopes_wood_hertwich/2022c"``.

    Examples
    --------
    >>> variant_folder(SCOPES_ROOT, "2019", "v3_7", "", "health_eldercare", "excluded")
    '02_scopes_wood_hertwich/2019a'
    """
    return f"{root}/{variant_name(year, release, tag, scope, capital)}"


def eriksen_folder(year: str | None = None, release: str | None = None,
                   tag: str | None = None, scope: str | None = None,
                   capital: str | None = None) -> str:
    """Return the Eriksen output folder for one variant.

    Parameters
    ----------
    year : str, optional
        Four-digit analysis year. Defaults to ``HC_ANALYSIS_YEAR``.
    release : str, optional
        Release key. Defaults to ``HC_EXIOBASE_RELEASE``.
    tag : str, optional
        Sea-transport correction tag. Defaults to ``HC_BACKGROUND_TAG``.
    scope : str, optional
        Sector boundary. Defaults to ``HC_SCOPE``.
    capital : str, optional
        Capital treatment. Defaults to ``HC_CAPITAL``.

    Returns
    -------
    str
        Path relative to the gold results root, e.g.
        ``"01_eriksen_replication/2022c"``.
    """
    return variant_folder(ERIKSEN_ROOT, year, release, tag, scope, capital)


def scopes_folder(year: str | None = None, release: str | None = None,
                  tag: str | None = None, scope: str | None = None,
                  capital: str | None = None) -> str:
    """Return the scope-decomposition folder for one variant.

    Parameters
    ----------
    year : str, optional
        Four-digit analysis year. Defaults to ``HC_ANALYSIS_YEAR``.
    release : str, optional
        Release key. Defaults to ``HC_EXIOBASE_RELEASE``.
    tag : str, optional
        Sea-transport correction tag. Defaults to ``HC_BACKGROUND_TAG``.
    scope : str, optional
        Sector boundary. Defaults to ``HC_SCOPE``.
    capital : str, optional
        Capital treatment. Defaults to ``HC_CAPITAL``.

    Returns
    -------
    str
        Path relative to the gold results root, e.g.
        ``"02_scopes_wood_hertwich/2022c"``.
    """
    return variant_folder(SCOPES_ROOT, year, release, tag, scope, capital)
