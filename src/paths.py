"""Canonical repository paths used by the modelling entry points.

Keeping path resolution here makes the pipelines independent of the caller's
current working directory and portable across Windows, macOS, and Linux.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
SILVER_INPUT_DIR = SILVER_DIR / "inputs"
GOLD_DIR = DATA_DIR / "gold"
BACKGROUND_DIR = SILVER_DIR / "background"
MRIO_DIR = BACKGROUND_DIR / "pickled_mrio"
OUTPUT_DIR = GOLD_DIR / "results"
EXIOBASE_DIR = BRONZE_DIR / "exiobase_v3_7"


def ensure_runtime_directories() -> None:
    """Create generated-data directories when a pipeline needs them."""

    BACKGROUND_DIR.mkdir(parents=True, exist_ok=True)
    MRIO_DIR.mkdir(parents=True, exist_ok=True)
    SILVER_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
