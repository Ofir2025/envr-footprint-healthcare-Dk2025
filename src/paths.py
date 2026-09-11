"""Canonical repository paths used by the modelling entry points.

Keeping path resolution here makes the pipelines independent of the caller's
current working directory and portable across Windows, macOS, and Linux.

Bronze and silver are **inputs**, not deliverables: neither is in version
control, bronze is a quarter of a gigabyte of third-party data obtained under
providers' terms, and silver is ten gigabytes of prepared model objects. Two
working copies of different scope should share one physical copy of them rather
than hold two, so both layers can be pointed elsewhere with an environment
variable:

.. code-block:: console

   export HC_BRONZE_DIR=/path/to/data/bronze
   export HC_SILVER_DIR=/path/to/data/silver

Gold is the opposite case. It is the deliverable, it is in version control, and
the two copies are *entitled to different subsets of it*, so it always resolves
inside the working copy and has no override.

Silver mirrors bronze by provenance: every transformed product sits under a
folder named for the bronze folder it derives from, so a path says where a
number came from. The mirror folders are named constants here -- there is no
``SILVER_INPUT_DIR`` any more, and no module builds a silver path by joining
strings at the call site, because that is how three modules came to read
the Danish expenditure frame through ``BACKGROUND_DIR / ".." / "inputs"``.
"""

import os
from pathlib import Path


def _dir(env: str, default: Path) -> Path:
    """Resolve a data directory, allowing an environment override.

    Parameters
    ----------
    env : str
        Environment variable consulted first.
    default : Path
        Where the directory sits inside the working copy.

    Returns
    -------
    Path
        The override when set and non-empty, else the default.
    """
    value = os.environ.get(env, "").strip()
    return Path(value).expanduser().resolve() if value else default


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
BRONZE_DIR = _dir("HC_BRONZE_DIR", DATA_DIR / "bronze")
SILVER_DIR = _dir("HC_SILVER_DIR", DATA_DIR / "silver")
GOLD_DIR = DATA_DIR / "gold"
OUTPUT_DIR = GOLD_DIR / "results"

#: Model-object store: the prepared MRIO and background pickles. NOT part of
#: the bronze mirror below. A background object is not a transformed source
#: table - it is a pickled model built from many of them - and it is ten
#: gigabytes that no clone holds, so it keeps its own folder and its own
#: ``.gitignore`` entry.
BACKGROUND_DIR = SILVER_DIR / "background"
MRIO_DIR = BACKGROUND_DIR / "pickled_mrio"

#: Script-to-script handoff, also outside the bronze mirror: a workbook one
#: module writes for another module to read back is a message between two
#: scripts, not a product derived from a bronze source, so it has no bronze
#: folder to mirror and does not belong beside the tables that do.
SILVER_HANDOFF_DIR = SILVER_DIR / "handoff"

#: The handoff between :mod:`analysis.main_2025` and the three modules that read
#: its workbooks back -- :mod:`analysis.eriksen_tables`,
#: :mod:`analysis.scopes_detail` and :mod:`analysis.uncertainty_2025`. One
#: subfolder per variant, named by ``constants.eriksen_folder``.
ERIKSEN_INTERIM_DIR = SILVER_HANDOFF_DIR / "eriksen_tables"

# ---------------------------------------------------------------------------
# The bronze mirror.
#
# Silver holds transformed bronze, so it is organised the way bronze is: one
# folder per PROVIDER, named for the bronze folder the product derives from.
# A flat ``inputs/`` folder cannot say where a file came from, and that is the
# question silver exists to answer -- ``exiobase_industry_sector_group.csv``
# and ``dst_water_transport_domestic_share.csv`` sat side by side in it with
# nothing but their prefixes to distinguish an EXIOBASE product from a
# Statistics Denmark one.
#
# A product derived from more than one bronze folder sits under the one that
# dominates it, and its folder readme names the others. Only folders that hold
# something exist: there is no silver mirror of ``dk_travel_survey/``,
# ``dst_capital_stock/``, ``dst_emission_accounts/``, ``exiobase_capital/`` or
# ``exiobase_characterisation/``, because nothing is derived from them into this
# layer.
# ---------------------------------------------------------------------------

#: Conformed concordances. Mirrors ``data/bronze/classification_concordances/``.
SILVER_CLASSIFICATION_CONCORDANCES_DIR = (SILVER_DIR
                                          / "classification_concordances")

#: The Danish medicines register with named columns. Mirrors
#: ``data/bronze/dk_medicines_register/``.
SILVER_DK_MEDICINES_REGISTER_DIR = SILVER_DIR / "dk_medicines_register"

#: Products read off Statistics Denmark's published input-output workbooks.
#: Mirrors ``data/bronze/dst_input_output/``.
SILVER_DST_INPUT_OUTPUT_DIR = SILVER_DIR / "dst_input_output"

#: Products read off the detailed Danish supply-use tables. Mirrors
#: ``data/bronze/dst_supply_use/``.
SILVER_DST_SUPPLY_USE_DIR = SILVER_DIR / "dst_supply_use"

#: The dimension tables the Eurostat FIGARO fact tables ship without. Mirrors
#: ``data/bronze/eurostat_figaro/``.
SILVER_EUROSTAT_FIGARO_DIR = SILVER_DIR / "eurostat_figaro"

#: Products read off the EXIOBASE auxiliary workbooks. Mirrors
#: ``data/bronze/exiobase/``.
SILVER_EXIOBASE_DIR = SILVER_DIR / "exiobase"

#: Products derived from the Dutch replication's own inputs. Mirrors
#: ``data/bronze/netherlands_reference/``.
SILVER_NETHERLANDS_REFERENCE_DIR = SILVER_DIR / "netherlands_reference"

#: Every folder of the bronze mirror, declared once so
#: :func:`ensure_runtime_directories` and the folder readmes cannot disagree
#: with the constants above about what the layer contains.
SILVER_MIRROR_DIRS: tuple[Path, ...] = (
    SILVER_CLASSIFICATION_CONCORDANCES_DIR,
    SILVER_DK_MEDICINES_REGISTER_DIR,
    SILVER_DST_INPUT_OUTPUT_DIR,
    SILVER_DST_SUPPLY_USE_DIR,
    SILVER_EUROSTAT_FIGARO_DIR,
    SILVER_EXIOBASE_DIR,
    SILVER_NETHERLANDS_REFERENCE_DIR,
)

# ---------------------------------------------------------------------------
# Silver products read across module boundaries.
#
# A product with one writer and one reader can name itself inside the module
# pair that owns it. These three cannot: each is written by one module and read
# by several others, and every reader that spelled the name out was a place the
# name could go stale. Three of them spelled it as
# ``BACKGROUND_DIR / ".." / "inputs"``, which survived the move of the file it
# pointed at only because the move had not happened yet.
#
# All three are YEAR-SCOPED, and they are functions rather than constants for
# that reason. Two of them used to be one tracked file each for every analysis
# year, overwritten on every run, under the names ``dk_data_2025.csv`` and
# ``dk_bottomup_data_2025.txt`` - where ``2025`` was an edition marker and not a
# year of data. A 2019 run left 2019 values in the file a 2022 run then read,
# and every reader of them read whichever year happened to have run last. A
# path that cannot be built without naming a year cannot be read for the wrong
# one.
# ---------------------------------------------------------------------------


def silver_dk_data_csv(year: str) -> Path:
    """Path of the expenditure and direct-emission frame for one year.

    Parameters
    ----------
    year : str
        Four-digit analysis year, e.g. ``"2022"``.

    Returns
    -------
    Path
        ``data/silver/dst_supply_use/dk_data_<year>.csv``, the three-row frame
        ``functions_2025.createBackground`` consumes. Written by
        :mod:`analysis.main_2025`; read by :mod:`analysis.export_tables`,
        :mod:`analysis.lenzen_replication`, :mod:`analysis.malik_replication`
        and :mod:`analysis.waste_validation`.
    """
    return SILVER_DST_SUPPLY_USE_DIR / f"dk_data_{year}.csv"


def silver_dk_bottomup_txt(year: str) -> Path:
    """Path of the Danish bottom-up inventory for one year.

    Parameters
    ----------
    year : str
        Four-digit analysis year, e.g. ``"2022"``.

    Returns
    -------
    Path
        ``data/silver/netherlands_reference/dk_bottomup_data_<year>.txt``: the
        four non-MRIO items, scaled from the Dutch baseline and then overwritten
        with Danish primary values. Written by :mod:`analysis.main_2025`; read
        by :mod:`analysis.scopes_detail` and
        :mod:`analysis.mitigation_scenarios`. Every value in it is analysis-year
        specific - both scaling factors and both medical-gas values differ
        between 2019 and 2022 - which is why it is the file the missing year
        scope mattered most in.
    """
    return SILVER_NETHERLANDS_REFERENCE_DIR / f"dk_bottomup_data_{year}.txt"


def silver_dk_expenditure_breakdown_csv(year: str) -> Path:
    """Path of the per-column expenditure provenance record for one year.

    Parameters
    ----------
    year : str
        Four-digit analysis year, e.g. ``"2022"``.

    Returns
    -------
    Path
        ``data/silver/dst_supply_use/dk_expenditure_breakdown_<year>.csv``.
        Written by :mod:`analysis.main_2025`, read by
        :mod:`analysis.waste_domestic_dst`.
    """
    return SILVER_DST_SUPPLY_USE_DIR / f"dk_expenditure_breakdown_{year}.csv"


#: Shared, release-independent EXIOBASE inputs: the DESIRE characterisation
#: workbook, ``classifications.xlsx``, the region files and the hybrid waste
#: workbook. These are one copy for every release, so they are NOT under a
#: release subfolder and must be read from here rather than from
#: :data:`EXIOBASE_DIR`.
EXIOBASE_BASE_DIR = BRONZE_DIR / "exiobase"

#: EXIOBASE release the process is configured for, from ``HC_EXIOBASE_RELEASE``.
#:
#: Defined here rather than imported from :mod:`analysis.constants` because
#: this module must not depend on the analysis package; the two agree by
#: reading the same variable, and ``analysis.constants.EXIOBASE_RELEASE`` is
#: the name the rest of the code base uses.
EXIOBASE_RELEASE = os.environ.get("HC_EXIOBASE_RELEASE", "v3_8_2").strip() \
    or "v3_8_2"


def exiobase_release_dir(release: str | None = None) -> Path:
    """Directory holding one release's ``IOT_<year>_ixi`` trees.

    Parameters
    ----------
    release : str, optional
        Release key, ``"v3_7"`` or ``"v3_8_2"``. Defaults to
        :data:`EXIOBASE_RELEASE`.

    Returns
    -------
    Path
        ``data/bronze/exiobase/<release>`` when that directory exists, else
        ``data/bronze/exiobase`` itself. The fallback keeps the pre-existing
        top-level symlinks (``data/bronze/exiobase/IOT_2016_ixi``) working in a
        working copy that has not yet grown the per-release trees.
    """
    per_release = EXIOBASE_BASE_DIR / (release or EXIOBASE_RELEASE)
    return per_release if per_release.is_dir() else EXIOBASE_BASE_DIR


def exiobase_iot_dir(year: str, release: str | None = None) -> Path:
    """Path of one release-year EXIOBASE industry-by-industry table.

    Parameters
    ----------
    year : str
        Four-digit table year, e.g. ``"2016"``.
    release : str, optional
        Release key. Defaults to :data:`EXIOBASE_RELEASE`.

    Returns
    -------
    Path
        ``<release dir>/IOT_<year>_ixi``, falling back to the top-level
        ``data/bronze/exiobase/IOT_<year>_ixi`` symlink when the release tree
        does not carry that year.

    Raises
    ------
    FileNotFoundError
        If neither location exists, naming both so the caller can see which
        symlink is missing.
    """
    candidates = [exiobase_release_dir(release) / f"IOT_{year}_ixi",
                  EXIOBASE_BASE_DIR / f"IOT_{year}_ixi"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"no EXIOBASE IOT_{year}_ixi for release "
        f"{release or EXIOBASE_RELEASE!r}; looked in "
        + ", ".join(str(c) for c in candidates))


#: Release-resolved EXIOBASE directory: the tree holding the ``IOT_<year>_ixi``
#: tables of the release this process is configured for. The release-independent
#: auxiliary workbooks live in :data:`EXIOBASE_BASE_DIR`, one level up.
EXIOBASE_DIR = exiobase_release_dir()


def ensure_runtime_directories() -> None:
    """Create generated-data directories when a pipeline needs them."""

    BACKGROUND_DIR.mkdir(parents=True, exist_ok=True)
    MRIO_DIR.mkdir(parents=True, exist_ok=True)
    SILVER_HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    for directory in SILVER_MIRROR_DIRS:
        directory.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
