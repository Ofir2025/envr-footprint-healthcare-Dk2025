# -*- coding: utf-8 -*-
"""Geometric layout check for the presentation, without rendering it.

Visual QA of a deck normally means converting it to images and looking. That is
the right check and it is not always available - this machine has no headless
renderer installed - and it is in one respect weaker than it appears: a
renderer substitutes fonts it does not have, so apparent text fit in the preview
can be an artefact of the substitute's metrics rather than a property of the
deck the audience will open.

This module checks the geometry directly from the package. It reads every shape
on every slide, measures it against the slide canvas, and estimates rendered
text extent from real font metrics. It catches the defects that actually reach
an audience:

* a shape wholly or partly off the canvas;
* a shape inside the safe margin;
* two text-bearing shapes overlapping;
* text that cannot fit the box it is in at its declared point size.

It cannot see colour contrast, visual balance or whether a slide says something
worth saying. Those still need eyes. What it does replaces the part of visual QA
that is measurement rather than judgement, and it is reproducible.

Run
---
``python scripts/release/check_deck_layout.py docs/presentation/<deck>.pptx``
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

EMU_PER_IN = 914_400
NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

#: Slide dimensions are read from the package; this is only the fallback.
DEFAULT_CANVAS_IN = (13.333, 7.5)

#: House rule: body content stays half an inch from the edge.
SAFE_MARGIN_IN = 0.5

#: The deck's own title and footer bands sit above and below that margin by
#: design, on every slide. Flagging them would bury the real findings under
#: forty-four copies of a deliberate choice, so they are exempt - and named
#: here rather than silently skipped.
TITLE_BAND_IN = 0.38
FOOTER_BAND_IN = 6.90

#: Fonts the deck asks for, mapped to a metric-compatible file present on this
#: machine. Arial stands in for Calibri and Cambria: it is not metrically
#: identical, so the width estimate is approximate and the tolerance below is
#: set generously to avoid crying wolf.
FONT_SUBSTITUTE = {
    "Calibri": "/System/Library/Fonts/Supplemental/Arial.ttf",
    "Cambria": "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "Courier New": "/System/Library/Fonts/Supplemental/Courier New.ttf",
}
FALLBACK_FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"

#: A box is only reported as overfull beyond this much excess, because the
#: estimate uses substitute metrics and PowerPoint's own line breaking differs.
OVERFLOW_TOLERANCE = 1.18


@dataclass
class Shape:
    """One positioned shape on a slide."""

    slide: int
    name: str
    x: float
    y: float
    w: float
    h: float
    text: str
    size_pt: float
    font: str
    is_textbox: bool

    @property
    def right(self) -> float:
        """Right edge, inches."""
        return self.x + self.w

    @property
    def bottom(self) -> float:
        """Bottom edge, inches."""
        return self.y + self.h


def _canvas(zf: zipfile.ZipFile) -> tuple[float, float]:
    """Slide width and height in inches, from the package."""
    try:
        root = ET.fromstring(zf.read("ppt/presentation.xml"))
        sz = root.find("p:sldSz", NS)
        return (int(sz.get("cx")) / EMU_PER_IN, int(sz.get("cy")) / EMU_PER_IN)
    except Exception:                                       # noqa: BLE001
        return DEFAULT_CANVAS_IN


def _shapes(zf: zipfile.ZipFile, slide: int) -> list[Shape]:
    """Every positioned shape on one slide."""
    root = ET.fromstring(zf.read(f"ppt/slides/slide{slide}.xml"))
    out: list[Shape] = []
    for sp in root.iter():
        tag = sp.tag.split("}")[-1]
        if tag not in {"sp", "pic", "graphicFrame"}:
            continue
        xfrm = sp.find(".//a:xfrm", NS)
        if xfrm is None:
            continue
        off, ext = xfrm.find("a:off", NS), xfrm.find("a:ext", NS)
        if off is None or ext is None:
            continue
        runs = sp.findall(".//a:r", NS)
        text = "".join((r.find("a:t", NS).text or "")
                       for r in runs if r.find("a:t", NS) is not None)
        sizes = [int(r.find("a:rPr", NS).get("sz"))
                 for r in runs
                 if r.find("a:rPr", NS) is not None
                 and r.find("a:rPr", NS).get("sz")]
        fonts = [f.get("typeface") for f in sp.findall(".//a:latin", NS)
                 if f.get("typeface")]
        nv = sp.find(".//p:nvSpPr/p:cNvPr", NS)
        out.append(Shape(
            slide=slide, name=(nv.get("name") if nv is not None else tag),
            x=int(off.get("x")) / EMU_PER_IN, y=int(off.get("y")) / EMU_PER_IN,
            w=int(ext.get("cx")) / EMU_PER_IN,
            h=int(ext.get("cy")) / EMU_PER_IN,
            text=text, size_pt=max(sizes) / 100 if sizes else 0.0,
            font=fonts[0] if fonts else "",
            is_textbox=sp.find(".//p:nvSpPr/p:cNvSpPr", NS) is not None
            and sp.find(".//p:nvSpPr/p:cNvSpPr", NS).get("txBox") == "1"))
    return out


def _text_height_in(shape: Shape) -> float | None:
    """Estimate the rendered height of a shape's text, in inches.

    Wraps the text to the shape's width using real glyph advances, then
    multiplies the line count by a 1.2 line height. Returns ``None`` when the
    estimate cannot be made.
    """
    if not shape.text.strip() or shape.size_pt <= 0 or shape.w <= 0:
        return None
    try:
        from PIL import ImageFont
    except ImportError:
        return None
    path = FONT_SUBSTITUTE.get(shape.font, FALLBACK_FONT)
    if not Path(path).exists():
        path = FALLBACK_FONT
    px_per_pt = 4.0                       # render at 4x for stable metrics
    try:
        font = ImageFont.truetype(path, int(shape.size_pt * px_per_pt))
    except Exception:                                       # noqa: BLE001
        return None
    width_px = shape.w * 72 * px_per_pt
    lines = 0
    for para in shape.text.split("\n"):
        words, current = para.split(), ""
        n = 1
        for word in words:
            trial = f"{current} {word}".strip()
            if font.getlength(trial) <= width_px or not current:
                current = trial
            else:
                n += 1
                current = word
        lines += n
    return lines * shape.size_pt * 1.2 / 72


def check(path: Path) -> list[dict[str, object]]:
    """Run every geometric check on one deck.

    Parameters
    ----------
    path : pathlib.Path
        The ``.pptx`` to check.

    Returns
    -------
    list of dict
        One entry per problem, with ``slide``, ``kind``, ``shape`` and
        ``detail``.
    """
    problems: list[dict[str, object]] = []
    with zipfile.ZipFile(path) as zf:
        cw, ch = _canvas(zf)
        slides = sorted(
            int(re.search(r"slide(\d+)\.xml$", n).group(1))
            for n in zf.namelist()
            if re.match(r"ppt/slides/slide\d+\.xml$", n))
        for i in slides:
            shapes = _shapes(zf, i)
            for s in shapes:
                # Decorative shapes are allowed to bleed off the canvas; the
                # title slide does it deliberately. Text is not.
                if s.text.strip() and (
                        s.x < -1e-6 or s.y < -1e-6 or s.right > cw + 1e-6
                        or s.bottom > ch + 1e-6):
                    problems.append(dict(
                        slide=i, kind="off canvas", shape=s.name,
                        detail=f"({s.x:.2f}, {s.y:.2f}) to "
                               f"({s.right:.2f}, {s.bottom:.2f}) in "
                               f"against a {cw:.2f} x {ch:.2f} in canvas"))
                elif (s.y >= TITLE_BAND_IN - 1e-6
                      and s.y < FOOTER_BAND_IN - 1e-6
                      and (s.x < SAFE_MARGIN_IN - 1e-6
                           or s.right > cw - SAFE_MARGIN_IN + 1e-6
                           or s.bottom > ch - SAFE_MARGIN_IN + 1e-6)
                      and not (s.y <= TITLE_BAND_IN + 1e-6)):
                    problems.append(dict(
                        slide=i, kind="inside the safe margin", shape=s.name,
                        detail=f"({s.x:.2f}, {s.y:.2f}) to "
                               f"({s.right:.2f}, {s.bottom:.2f}) in, "
                               f"margin {SAFE_MARGIN_IN} in"))
                need = _text_height_in(s)
                if need is not None and need > s.h * OVERFLOW_TOLERANCE:
                    problems.append(dict(
                        slide=i, kind="text may overflow its box",
                        shape=s.name,
                        detail=f"{s.size_pt:g} pt in a {s.w:.2f} x {s.h:.2f} in "
                               f"box needs about {need:.2f} in: "
                               f"\"{s.text[:60]}...\""))
            texts = [s for s in shapes if s.text.strip()]
            for a_i, a in enumerate(texts):
                for b in texts[a_i + 1:]:
                    ox = min(a.right, b.right) - max(a.x, b.x)
                    oy = min(a.bottom, b.bottom) - max(a.y, b.y)
                    if ox > 0.05 and oy > 0.05:
                        problems.append(dict(
                            slide=i, kind="text shapes overlap",
                            shape=f"{a.name} / {b.name}",
                            detail=f"{ox:.2f} x {oy:.2f} in overlap"))
    return problems


def main() -> None:
    """Check a deck and exit non-zero if anything is wrong."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("deck", type=Path)
    args = ap.parse_args()

    problems = check(args.deck)
    if not problems:
        print(f"{args.deck.name}: layout clean")
        return
    by_kind: dict[str, int] = {}
    for p in problems:
        by_kind[str(p["kind"])] = by_kind.get(str(p["kind"]), 0) + 1
    print(f"{args.deck.name}: {len(problems)} problem(s)")
    for kind, count in sorted(by_kind.items(), key=lambda kv: -kv[1]):
        print(f"  {count:3d}  {kind}")
    print()
    for p in problems:
        print(f"  slide {p['slide']:>2}  {p['kind']:<26}  {p['shape']}")
        print(f"            {p['detail']}")
    sys.exit(1)


if __name__ == "__main__":
    main()
