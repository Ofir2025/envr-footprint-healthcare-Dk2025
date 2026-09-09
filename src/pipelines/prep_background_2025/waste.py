"""Reuse the canonical waste-preparation stage for the 2025 pipeline.

The 2016 and 2025 models use the same Exiobase waste workbook and algorithm;
this module is intentionally a thin compatibility entry point rather than a
second copy of that implementation.
"""

from pipelines.prep_background import waste as _canonical_waste  # noqa: F401

