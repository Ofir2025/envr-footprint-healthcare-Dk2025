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
SILVER_INPUT_DIR = SILVER_DIR / "inputs"
GOLD_DIR = DATA_DIR / "gold"
BACKGROUND_DIR = SILVER_DIR / "background"
MRIO_DIR = BACKGROUND_DIR / "pickled_mrio"
OUTPUT_DIR = GOLD_DIR / "results"

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
    SILVER_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
