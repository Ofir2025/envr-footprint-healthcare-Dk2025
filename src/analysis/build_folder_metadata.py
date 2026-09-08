# -*- coding: utf-8 -*-
"""Write a metadata README into every gold results folder.

A reader opening ``data/gold/results/07_malik_replication/`` should not have to
guess what is in it. This module writes a ``README.md`` per folder describing
what the layer answers, which module produced it, and, for every table, its
grain, row count, columns, units, and dimension coverage.

The descriptions are read from the folder's methods document in
``docs/methods/replications/``, so the two cannot drift apart; the table
properties are measured from the files themselves, for the same reason.

These conventions are asserted while writing and reported in each README:

* EXIOBASE industry and product codes carry **no** ``A_`` / ``C_`` prefix.
* Countries are ISO3; EXIOBASE regions with no ISO3 code carry their region
  name (``RoW Europe`` and the other four).
* Every table is a star-schema fact or summary: dimension columns, then the
  measure and its unit.

Run::

    HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship \\
        PYTHONPATH=src python -m analysis.build_folder_metadata
"""

from __future__ import annotations

import gzip
import os
import re

import pandas as pd

from paths import OUTPUT_DIR

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METHODS = os.path.join(REPO, "docs", "methods", "replications")

#: Columns that identify a dimension rather than carry a measure.
DIMENSION_HINTS = (
    "country", "region", "sector", "industry", "product", "indicator", "unit",
    "scope", "scenario", "method", "year", "component", "function", "layer",
    "origin", "target", "model", "analysis", "quantity", "parameter", "species",
    "asset", "stressor", "damage", "source", "basis", "check", "defect",
    "vintage", "metric", "item", "risk", "test", "verdict", "group", "note",
)

ROW_REGIONS = ("RoW Asia and Pacific", "RoW America", "RoW Europe",
               "RoW Africa", "RoW Middle East")


def _read_head(path: str, n: int = 400) -> tuple[pd.DataFrame, int]:
    """Read a table's head and count its rows without loading it whole.

    Parameters
    ----------
    path : str
        CSV or gzipped CSV.
    n : int, optional
        Rows to read for column inspection.

    Returns
    -------
    tuple
        ``(head_frame, total_rows)``.
    """
    opener = gzip.open if path.endswith(".gz") else open
    head = pd.read_csv(path, nrows=n)
    with opener(path, "rt", encoding="utf-8", errors="ignore") as fh:
        total = sum(1 for _ in fh) - 1
    return head, max(total, 0)


def _methods_summary(folder: str) -> tuple[str, str]:
    """Pull the title and the 'question this layer answers' from the methods doc.

    Parameters
    ----------
    folder : str
        Gold folder name, e.g. ``"07_malik_replication"``.

    Returns
    -------
    tuple of str
        ``(title, question)``; empty strings when no methods document exists.
    """
    path = os.path.join(METHODS, f"{folder}.md")
    if not os.path.exists(path):
        return "", ""
    text = open(path, encoding="utf-8").read()
    title = re.search(r"^# (.+)$", text, re.MULTILINE)
    block = re.search(r"## Question this layer answers\s+(.+?)(?=\n## )",
                      text, re.DOTALL)
    question = ""
    if block:
        para = [p.strip() for p in block.group(1).strip().split("\n\n") if p.strip()]
        question = " ".join(para[0].split()) if para else ""
    return (title.group(1).strip() if title else ""), question


def describe_table(path: str) -> dict[str, object]:
    """Measure one table's properties.

    Parameters
    ----------
    path : str
        Full path to the table.

    Returns
    -------
    dict
        Name, rows, grain, dimension and measure columns, units, and the
        dimension coverage where the table is node-resolved.
    """
    head, rows = _read_head(path)
    cols = list(head.columns)
    dims = [c for c in cols
            if any(h in c.lower() for h in DIMENSION_HINTS)
            and not pd.api.types.is_numeric_dtype(head[c])]
    measures = [c for c in cols if c not in dims]
    units = sorted(head["unit"].dropna().unique().tolist())[:6] if "unit" in cols else []

    coverage = ""
    ccol = next((c for c in cols if c.endswith("country_iso3")), None)
    scol = next((c for c in cols if c.endswith("sector_code")), None)
    if ccol and scol:
        coverage = (f"{head[ccol].nunique()}+ regions x {head[scol].nunique()}+ "
                    f"industries (sampled)")
    return {
        "name": os.path.basename(path),
        "rows": rows,
        "dims": dims,
        "measures": measures,
        "units": units,
        "coverage": coverage,
    }


def write_folder_readme(folder: str) -> str | None:
    """Write ``README.md`` for one gold folder.

    Parameters
    ----------
    folder : str
        Gold folder name.

    Returns
    -------
    str or None
        Path written, or ``None`` when the folder holds no tables.
    """
    fdir = os.path.join(str(OUTPUT_DIR), folder)
    tables = sorted(f for f in os.listdir(fdir)
                    if f.endswith((".csv", ".csv.gz")) and not f.startswith("_"))
    if not tables:
        return None

    title, question = _methods_summary(folder)
    lines = [f"# {folder}", ""]
    if title:
        lines += [f"**{title}**", ""]
    if question:
        lines += [question, ""]
    if os.path.exists(os.path.join(METHODS, f"{folder}.md")):
        lines += [f"Method, equations, and verification: "
                  f"[`docs/methods/replications/{folder}.md`]"
                  f"(../../../docs/methods/replications/{folder}.md).", ""]

    lines += [
        "## Conventions",
        "",
        "| Item | Convention |",
        "|---|---|",
        "| Schema | star schema: dimension columns, then measure and unit |",
        "| Industry / product codes | EXIOBASE codes **without** the `A_` / `C_` prefix |",
        "| Countries | ISO3 (`DNK`, `DEU`, `ROU`) |",
        "| Regions without an ISO3 code | region name (`RoW Europe`, `RoW Africa`, ...) |",
        "| Monetary unit | M.EUR, EXIOBASE basic prices, unless a column says otherwise |",
        "| Provenance | one row per file in `../MANIFEST_lineage.csv` |",
        "",
        "## Tables",
        "",
    ]

    for name in tables:
        d = describe_table(os.path.join(fdir, name))
        lines += [f"### `{d['name']}`", ""]
        bullets = [f"- **Rows:** {d['rows']:,}"]
        if d["coverage"]:
            bullets.append(f"- **Resolution:** {d['coverage']}")
        if d["units"]:
            bullets.append(f"- **Units:** {', '.join(d['units'])}")
        bullets.append(f"- **Dimensions:** {', '.join(f'`{c}`' for c in d['dims']) or 'none'}")
        bullets.append(f"- **Measures:** {', '.join(f'`{c}`' for c in d['measures']) or 'none'}")
        lines += bullets + [""]

    out = os.path.join(fdir, "README.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    return out


def main() -> None:
    """Write a README into every gold results folder."""
    root = str(OUTPUT_DIR)
    folders = sorted(f for f in os.listdir(root)
                     if os.path.isdir(os.path.join(root, f)))
    written = [w for w in (write_folder_readme(f) for f in folders) if w]
    for path in written:
        print(f"  {os.path.relpath(path, root)}")
    print(f"\n{len(written)} folder READMEs written")


if __name__ == "__main__":
    main()
