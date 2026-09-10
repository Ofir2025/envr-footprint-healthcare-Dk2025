# -*- coding: utf-8 -*-
"""Render every Mermaid diagram in the documentation to a PNG.

The diagrams live inside the Markdown they explain, as fenced ``mermaid``
blocks, so GitHub and most editors render them in place and they cannot drift
away from the text that refers to them. A reader working from a PDF, a Word
export or an editor without Mermaid support has no such luxury, so each block
is also rendered to ``figures/diagrams/``.

Those PNGs were previously produced by hand, which left the repository holding
figures with no producer. This module is that producer: every PNG under
``figures/diagrams/`` is regenerated from the Markdown, and the mapping from
block to filename is declared rather than inferred, so renaming a file is a
visible change rather than a silent one.

The renderer is ``@mermaid-js/mermaid-cli``. It pulls a headless browser, so it
is deliberately not a dependency of the analysis environment. Install it once,
anywhere, and point this module at it:

.. code-block:: console

   npm install @mermaid-js/mermaid-cli
   MMDC=./node_modules/.bin/mmdc python scripts/render_diagrams.py

With no ``MMDC`` set the module looks for ``mmdc`` on the path. The PNGs are
committed, so this only needs running when a diagram changes.

Run
---
``python scripts/render_diagrams.py``          render every declared diagram
``python scripts/render_diagrams.py --check``  report drift without rendering
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "figures" / "diagrams"

#: source document -> the diagrams it carries, in the order they appear.
#: One entry per fenced ``mermaid`` block. A document with more blocks than
#: names, or fewer, is an error rather than a silent partial render.
DIAGRAMS: dict[str, tuple[str, ...]] = {
    "docs/revision/uncertainty.md": ("uncertainty_taxonomy",),
    "docs/methods/replications.md": ("footprint_marginals", "scenario_workflow"),
    "docs/revision/results_2022.md": ("shipping_reallocation",),
}

BLOCK = re.compile(r"^```mermaid\n(.*?)^```", re.MULTILINE | re.DOTALL)

#: Passed to the headless browser mermaid-cli drives. Without the sandbox flags
#: it refuses to start under most CI users.
PUPPETEER = '{"args":["--no-sandbox","--disable-setuid-sandbox"]}'


def blocks(document: Path) -> list[str]:
    """Mermaid sources found in a Markdown document, in order.

    Parameters
    ----------
    document : Path
        The Markdown file to scan.

    Returns
    -------
    list of str
        The body of each fenced ``mermaid`` block, fence lines excluded.
    """
    if not document.exists():
        return []
    return [m.group(1) for m in BLOCK.finditer(document.read_text(encoding="utf-8"))]


def renderer() -> str:
    """Path to the mermaid-cli executable.

    Returns
    -------
    str
        The command to invoke.

    Raises
    ------
    SystemExit
        If no renderer can be found, with the install line to run.
    """
    mmdc = os.environ.get("MMDC") or shutil.which("mmdc")
    if not mmdc:
        sys.exit(
            "no mermaid renderer found.\n"
            "  npm install @mermaid-js/mermaid-cli\n"
            "  MMDC=./node_modules/.bin/mmdc python scripts/render_diagrams.py"
        )
    return mmdc


def render(source: str, target: Path, mmdc: str, scale: int = 2) -> None:
    """Render one Mermaid source to a PNG.

    Parameters
    ----------
    source : str
        The Mermaid diagram definition.
    target : Path
        Where to write the PNG.
    mmdc : str
        The mermaid-cli executable.
    scale : int, default 2
        Device pixel ratio. Two gives a figure that stays legible when placed
        at half width in a document.
    """
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "diagram.mmd"
        conf = Path(tmp) / "puppeteer.json"
        src.write_text(source, encoding="utf-8")
        conf.write_text(PUPPETEER, encoding="utf-8")
        subprocess.run(
            [mmdc, "-i", str(src), "-o", str(target), "-b", "white",
             "-s", str(scale), "-p", str(conf)],
            check=True, capture_output=True, text=True,
        )


def main() -> int:
    """Render, or check, every declared diagram.

    Returns
    -------
    int
        Zero when every declared diagram was found and, unless checking only,
        rendered. One when a document carries a different number of blocks
        than the registry declares.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report drift between the registry and the documents")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    mmdc = None if args.check else renderer()
    failures = 0

    for document, names in DIAGRAMS.items():
        found = blocks(REPO / document)
        if len(found) != len(names):
            print(f"  MISMATCH {document}: {len(found)} blocks, "
                  f"{len(names)} declared")
            failures += 1
            continue
        for source, name in zip(found, names):
            target = OUT / f"{name}.png"
            if args.check:
                print(f"  {'ok' if target.exists() else 'MISSING'}  {name}")
                failures += 0 if target.exists() else 1
                continue
            render(source, target, mmdc)
            print(f"  {name}.png  <- {document}")

    total = sum(len(v) for v in DIAGRAMS.values())
    print(f"\n{total} diagrams across {len(DIAGRAMS)} documents, "
          f"{failures} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
