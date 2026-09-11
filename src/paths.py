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
EXIOBASE_DIR = BRONZE_DIR / "exiobase"


def ensure_runtime_directories() -> None:
    """Create generated-data directories when a pipeline needs them."""

    BACKGROUND_DIR.mkdir(parents=True, exist_ok=True)
    MRIO_DIR.mkdir(parents=True, exist_ok=True)
    SILVER_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
