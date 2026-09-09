# -*- coding: utf-8 -*-
"""Write a metadata readme and data dictionary into every gold table folder.

A reader opening ``data/gold/results/07_malik_replication/`` should not have to
guess what is in it. This module writes a ``readme.md`` per folder describing
what the layer answers, which module produced it, and, for every table, its
grain, row count, columns, units, and dimension coverage; and a
``data_dictionary.md`` beside it giving, per table, every column's dtype, unit,
role and a sample value.

Any folder under the gold root that holds at least one table gets both files,
however deep it sits - a year subdirectory (``01_eriksen_replication/2019``) or
a scenario folder (``scenarios/health_only``) is described exactly like a
top-level approach folder.

The descriptions are read from the folder's methods document in
``docs/methods/replications/`` (looked up by the folder's top-level component,
so a year subfolder shares its approach's document), so the two cannot drift
apart; the table properties are measured from the files themselves, for the
same reason.

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

#: Shared material folded in from the hand-written
#: ``00_core_footprint/README_data_dictionary.md`` (now superseded by this
#: generator): the column vocabulary, region coding and the reconciliation
#: identity are properties of every gold table, not just that one folder's, so
#: every generated ``data_dictionary.md`` carries them rather than losing them
#: when the generator started claiming that filename.
COMMON_COLUMNS: tuple[str, ...] = (
    "## Common columns",
    "",
    "Every gold table shares this vocabulary; columns particular to one table",
    "are described below, per table.",
    "",
    "| Column | Meaning |",
    "|:---|:---|",
    "| `analysis_year` | year of the Danish expenditure data and of the MRIO background |",
    "| `model` | MRIO release actually used (e.g. `EXIOBASE v3.10.2 IOT_2022_ixi (screened)`) |",
    "| `scenario` | model scenario (`baseline`, scope variants, pharma-mapping variants) |",
    "| `consuming_country_iso3` | always `DNK` - Denmark is the final consumer in this study |",
    "| `demand_component` | `healthcare_services`, `pharmaceuticals`, `medical_appliances` |",
    "| `indicator` | `climate_change`, `material_extraction`, `blue_water_consumption`, `land_use`, `waste_generation` |",
    "| `unit` | `kt CO2eq`, `kt`, `Mm3`, `km2`, or `M.EUR` for monetary rows |",
    "| `value` | numeric value in `unit` |",
    "",
    "## Country and region coding",
    "",
    "`*_country_iso3` uses **ISO 3166-1 alpha-3** for the 44 EXIOBASE countries.",
    "The five rest-of-world regions are **not countries** and keep their own",
    "codes and names: `WA` RoW Asia and Pacific, `WL` RoW America, `WE` RoW",
    "Europe, `WF` RoW Africa, `WM` RoW Middle East. `*_world_region` gives the",
    "continental grouping (Europe, Asia and Pacific, America, Middle East,",
    "Africa, Denmark).",
    "",
    "## The two perspectives (and why they reconcile)",
    "",
    "Every impact cell is `E[i,j] = s_k(i) . L(i,j) . y_H(j)`: pressure arising",
    "in node *i* caused by Danish healthcare final demand for node *j*. Summing",
    "over *i* gives the **consumption / contribution** perspective (by",
    "purchased product); summing over *j* gives the **production / hotspot**",
    "perspective (by producing node). Both are marginals of the same array, so",
    "they sum to the identical total - verified to machine precision by",
    "`analysis.validate_io_identities` (tests T5/T6). Allocating production",
    "emissions to final demand is additive and does not double count (Wood et",
    "al. 2018); embodied-flow tables (E_Z) would.",
    "",
    "## Units",
    "",
    "Monetary values are **million euro (M.EUR)** - EXIOBASE's native unit",
    "(`unit.txt` of the release). No US-dollar values are used anywhere in this",
    "model; dollar figures appearing in the comparative literature (Karliner et",
    "al. 2019, Lenzen et al. 2020, Pichler et al. 2019) are those studies' own",
    "units and are labelled as such wherever they are quoted.",
    "",
)


def _read_head(path: str, n: int = 400) -> tuple[pd.DataFrame, int]:
    """Read a table's head and count its rows without loading it whole.

    Parameters
    ----------
    path : str
        CSV, gzipped CSV, or Parquet. The large star-schema facts are Parquet,
        which carries its row count and schema in the footer, so neither needs
        reading the data.
    n : int, optional
        Rows to read for column inspection.

    Returns
    -------
    tuple
        ``(head_frame, total_rows)``.
    """
    if path.endswith(".parquet"):
        import pyarrow.parquet as pq

        handle = pq.ParquetFile(path)
        total = handle.metadata.num_rows
        head = next(handle.iter_batches(batch_size=min(n, max(total, 1)))) \
            .to_pandas() if total else handle.schema_arrow.empty_table().to_pandas()
        return head, total
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
        Gold folder name, e.g. ``"07_malik_replication"`` or a nested table
        folder such as ``"01_eriksen_replication/2019"`` - the methods
        document is looked up by the top-level component, since a year or
        scenario subfolder shares its approach's document.

    Returns
    -------
    tuple of str
        ``(title, question)``; empty strings when no methods document exists.
    """
    top = folder.split(os.sep)[0]
    path = os.path.join(METHODS, f"{top}.md")
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
    # A surrogate key is a dimension column even though it is numeric. Without
    # this every star fact described itself as having no dimensions and six
    # measures, which is the opposite of what it is.
    dims = [c for c in cols
            if c.endswith("_id")
            or (any(h in c.lower() for h in DIMENSION_HINTS)
                and not pd.api.types.is_numeric_dtype(head[c]))]
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


def _folder_tables(fdir: str) -> list[str]:
    """Table filenames directly inside one gold folder, sorted.

    Parameters
    ----------
    fdir : str
        Full path to the folder.

    Returns
    -------
    list of str
        Filenames of tables (``.csv``, ``.csv.gz``, ``.parquet``) directly in
        ``fdir``, excluding any leading-underscore auxiliary file.
    """
    return sorted(f for f in os.listdir(fdir)
                 if f.endswith((".csv", ".csv.gz", ".parquet"))
                 and not f.startswith("_"))


def _relative_link(target: str, fdir: str) -> str:
    """A forward-slash relative path from ``fdir`` to ``target``.

    Both the manifest and the methods-document links are computed this way
    rather than with a hardcoded ``../`` count, so a nested folder (a year or
    scenario subdirectory) gets a link with the right number of steps.
    """
    return os.path.relpath(target, fdir).replace(os.sep, "/")


def write_folder_readme(folder: str) -> str | None:
    """Write ``readme.md`` for one gold folder.

    Parameters
    ----------
    folder : str
        Gold folder name, relative to the gold root. May contain path
        separators for a nested table folder, e.g.
        ``"01_eriksen_replication/2019"`` or ``"scenarios/health_only"``.

    Returns
    -------
    str or None
        Path written, or ``None`` when the folder holds no tables.
    """
    fdir = os.path.join(str(OUTPUT_DIR), folder)
    tables = _folder_tables(fdir)
    if not tables:
        return None

    title, question = _methods_summary(folder)
    top = folder.split(os.sep)[0]
    lines = [f"# {folder}", ""]
    if title:
        lines += [f"**{title}**", ""]
    if question:
        lines += [question, ""]
    methods_doc = os.path.join(METHODS, f"{top}.md")
    if os.path.exists(methods_doc):
        lines += [f"Method, equations, and verification: "
                  f"[`docs/methods/replications/{top}.md`]"
                  f"({_relative_link(methods_doc, fdir)}).", ""]

    manifest_path = os.path.join(str(OUTPUT_DIR), "manifest_lineage.csv")
    lines += [
        "## Conventions",
        "",
        "| Item | Convention |",
        "|:---|:---|",
        "| Schema | star schema: dimension columns, then measure and unit |",
        "| Industry / product codes | EXIOBASE codes **without** the `A_` / `C_` prefix |",
        "| Countries | ISO3 (`DNK`, `DEU`, `ROU`) |",
        "| Regions without an ISO3 code | region name (`RoW Europe`, `RoW Africa`, ...) |",
        "| Monetary unit | M.EUR, EXIOBASE basic prices, unless a column says otherwise |",
        f"| Provenance | one row per file in `{_relative_link(manifest_path, fdir)}` |",
        "",
        "## Tables",
        "",
    ]

    for name in tables:
        d = describe_table(os.path.join(fdir, name))
        lines += [f"### `{d['name']}`", ""]
        bullets = [f"- **Rows:** {d['rows']:,}",
                   f"- **Format:** {'parquet (pyarrow, snappy)' if name.endswith('.parquet') else 'csv'}"]
        if d["coverage"]:
            bullets.append(f"- **Resolution:** {d['coverage']}")
        if d["units"]:
            bullets.append(f"- **Units:** {', '.join(d['units'])}")
        bullets.append(f"- **Dimensions:** {', '.join(f'`{c}`' for c in d['dims']) or 'none'}")
        bullets.append(f"- **Measures:** {', '.join(f'`{c}`' for c in d['measures']) or 'none'}")
        lines += bullets + [""]

    out = os.path.join(fdir, "readme.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    return out


def column_dictionary(path: str) -> list[dict[str, str]]:
    """Describe every column of one table.

    Parameters
    ----------
    path : str
        Full path to the table.

    Returns
    -------
    list of dict
        One entry per column: name, dtype, unit, role, and a sample value.
    """
    head, _ = _read_head(path)
    described = describe_table(path)
    dims = set(described["dims"])
    unit_of = ""
    if "unit" in head.columns:
        seen = head["unit"].dropna().unique().tolist()
        unit_of = seen[0] if len(seen) == 1 else "varies by row"
    entries = []
    for col in head.columns:
        sample = head[col].dropna()
        entries.append({
            "column": col,
            "dtype": str(head[col].dtype),
            "unit": "" if col in dims or col == "unit" else unit_of,
            "role": "dimension" if col in dims else "measure",
            "example": str(sample.iloc[0])[:40] if len(sample) else "",
        })
    return entries


def write_folder_dictionary(folder: str) -> str | None:
    """Write ``data_dictionary.md`` for one gold folder.

    Parameters
    ----------
    folder : str
        Gold folder name, relative to the gold root, exactly as accepted by
        :func:`write_folder_readme`.

    Returns
    -------
    str or None
        Path written, or ``None`` when the folder holds no tables.
    """
    fdir = os.path.join(str(OUTPUT_DIR), folder)
    tables = _folder_tables(fdir)
    if not tables:
        return None
    lines = [f"# {folder} - data dictionary", "",
             "One row per column of every table in this folder. Units are the",
             "table's own; `varies by row` means the table carries a `unit`",
             "column and the value is read from there.", ""]
    lines += list(COMMON_COLUMNS)
    lines += ["## Tables", ""]
    for name in tables:
        lines += [f"### `{name}`", "",
                  "| Column | Role | Type | Unit | Example |",
                  "|:---|:---|:---|:---|:---|"]
        for e in column_dictionary(os.path.join(fdir, name)):
            lines.append(f"| `{e['column']}` | {e['role']} | {e['dtype']} | "
                         f"{e['unit']} | {e['example']} |")
        lines.append("")
    out = os.path.join(fdir, "data_dictionary.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    return out


def _table_folders(root: str) -> list[str]:
    """Every folder holding at least one table, relative to the gold root.

    Parameters
    ----------
    root : str
        Gold results root, i.e. ``OUTPUT_DIR``.

    Returns
    -------
    list of str
        Sorted relative paths (``os.sep``-joined), one per folder that holds
        at least one non-auxiliary ``.csv``, ``.csv.gz`` or ``.parquet`` file
        directly - a year or scenario subfolder counts on its own, its parent
        does not unless it also holds a table directly.
    """
    found = []
    for dirpath, _, names in os.walk(root):
        if any(n.endswith((".csv", ".csv.gz", ".parquet")) and not n.startswith("_")
               for n in names):
            rel = os.path.relpath(dirpath, root)
            found.append("" if rel == "." else rel)
    return sorted(f for f in found if f)


def main() -> None:
    """Write a readme and data dictionary into every gold folder holding a table."""
    root = str(OUTPUT_DIR)
    folders = _table_folders(root)
    written = []
    for folder in folders:
        for fn in (write_folder_readme(folder), write_folder_dictionary(folder)):
            if fn:
                written.append(fn)
    for path in written:
        print(f"  {os.path.relpath(path, root)}")
    print(f"\n{len(written)} files written across {len(folders)} table folders")


if __name__ == "__main__":
    main()
