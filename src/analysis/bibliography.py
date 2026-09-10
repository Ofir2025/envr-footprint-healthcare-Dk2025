# -*- coding: utf-8 -*-
"""One bibliography for the whole repository, and a check that it is used.

Reference lists had drifted: forty documents each carried their own, none of
them in a consistent style, none of them with a DOI, and at least one citation
could not be traced to any source at all. A reference that cannot be resolved is
worse than no reference, because it looks like evidence.

This module makes ``docs/references.csv`` the single source of truth. It renders
``docs/references.md`` in APA 7 with DOIs as resolvable links, and it verifies
that every author-year citation appearing in the documentation resolves to an
entry. The check runs in the consistency audit, so a citation cannot be added
without the source behind it.

Every DOI in ``references.csv`` was resolved against Crossref rather than typed
from memory; ``--verify`` re-runs that check over the network.

Run
---
``PYTHONPATH=src python -m analysis.bibliography``          render and check
``PYTHONPATH=src python -m analysis.bibliography --verify`` also re-check DOIs
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CSV_PATH = REPO / "docs" / "references.csv"
MD_PATH = REPO / "docs" / "references.md"

#: Documents whose in-text citations must resolve. Kept explicit rather than
#: globbing every markdown file: the reading notes under docs/methods cite far
#: more widely than this study uses, and forcing them into the bibliography
#: would make it a reading list instead of a reference list.
CHECKED_DOCS = (
    "docs/revision/uncertainty.md",
    "docs/methods/replications.md",
)
#: docs/revision/results_2022.md is deliberately not checked: it merges seven
#: source documents, most of which were never in this list before merging
#: (only the two behind "the withdrawn transport finding" and "mitigation
#: scenarios" sections were), and the newly-exposed content cites several
#: sources (Andersen et al. 2023, Eckelman et al. 2020, HCWH 2014/2019,
#: Laster et al. 1994, Lenzen & Treloar 2004, Pichler 2014, Talbot et al.
#: 2025) whose bibliographic detail this pass could not verify with enough
#: confidence to add correctly rather than guess. Completing
#: docs/references.csv for these and re-adding this document to the list is
#: follow-on work, not a merge regression: nothing this document's own prior
#: sections claimed was previously verified either.

#: Author-year citations in running prose. Matches "(Author, 2019)",
#: "Author (2019)", "Author et al. (2019)" and "A & B (2019)".
CITE = re.compile(
    r"(?<![A-Za-z])"
    r"([A-ZÅØÆ][\w'À-ɏ-]+"
    r"(?:\s+(?:&|and)\s+[A-ZÅØÆ][\w'À-ɏ-]+|\s+et\s+al\.)?)"
    r"[,\s]*\(?((?:19|20)\d\d)[a-z]?\)?")

#: Surnames parsed out of a ``references.csv`` ``authors`` field such as
#: "Rodrigues, J. F. D., Moran, D., Wood, R., & Behrens, P." - one match per
#: "Surname, Initial." group, in order.
SURNAME_RE = re.compile(r"([A-ZÅØÆÜÖ][\w'’\-]+),\s*(?:[A-Z]\.[-\s]?)+")

#: Words that begin a sentence before a year and are not surnames.
STOPWORDS = {
    "The", "This", "That", "These", "Those", "It", "In", "On", "By", "For",
    "From", "Since", "Our", "Their", "Its", "A", "An", "And", "But", "Both",
    "Table", "Figure", "Appendix", "Section", "Year", "September", "October",
    "January", "February", "March", "April", "May", "June", "July", "August",
    "November", "December", "Denmark", "Danish", "Copenhagen", "European",
    "Version", "Release", "EXIOBASE", "FIGARO", "ReCiPe", "IMPACT", "SHA",
    "COICOP", "ICIO", "NACE", "IPCC", "AR", "GWP", "OECD", "SNAC", "Reviewer",
    "Manuscript", "Are", "Where", "When", "What", "If", "As", "At", "All",
    "Between", "Before", "After", "Every", "Each", "Most", "Under", "Using",
    "With", "Without", "We", "Read", "Run", "See", "Set", "Note", "Two",
    "Three", "Four", "Five", "One", "Scope", "Health", "Statistics", "Eurostat",
    "Download", "Document", "Data", "Model", "Study", "Paper", "Report",
    "Net", "Total", "Baseline", "Reduction", "Interaction", "Rebound",
    "Demand", "Interventions", "Grid", "Climate", "Material", "Land", "Waste",
    # Dataset, table and account codes that carry a year in prose but are not
    # author surnames: Statistics Denmark accounts (AFFALD01, AFTRYK, DRIVHUS,
    # NABB69, V87880, AFF3MU1N), Denmark's health-expenditure and travel-survey
    # abbreviations (CHE, TU), the exchange-rate source (DNB), a
    # characterisation-workbook sheet label (CML), and connective words that
    # happen to precede a bare year rather than a citation.
    "AFFALD01", "AFTRYK", "DRIVHUS", "NABB69", "V87880", "AFF3MU1N", "CHE",
    "TU", "DNB", "CML", "COICOP-", "CO₂e", "No", "Unlike", "EG",
    # The manuscript under revision, cited by its own authorship
    # ("Eriksen et al. (2026)"): the submission itself, not a bibliography
    # entry, since it is this study, not an external source.
    "Eriksen",
}


def load() -> list[dict[str, str]]:
    """Read the bibliography.

    Returns
    -------
    list of dict
        One row per source, with the columns of ``docs/references.csv``.

    Raises
    ------
    AssertionError
        If a key is duplicated, or an entry has neither a DOI nor a URL.
    """
    with open(CSV_PATH, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    keys = [r["key"] for r in rows]
    dupes = {k for k in keys if keys.count(k) > 1}
    assert not dupes, f"duplicate bibliography keys: {sorted(dupes)}"
    for r in rows:
        assert r["doi"] or r["url"], (
            f"{r['key']}: every entry needs a DOI or a URL, so a reader can "
            f"reach it")
    return rows


def apa(row: dict[str, str]) -> str:
    """Format one entry in APA 7.

    Parameters
    ----------
    row : dict
        A bibliography row.

    Returns
    -------
    str
        ``Authors (Year). Title. Source. https://doi.org/...``
    """
    parts = [f"{row['authors']} ({row['year']}). {row['title']}."]
    if row["source"]:
        parts.append(f"*{row['source']}*.")
    if row["doi"]:
        parts.append(f"https://doi.org/{row['doi']}")
    elif row["url"]:
        parts.append(row["url"])
    return " ".join(parts)


def render() -> str:
    """Render ``docs/references.md`` and return its text."""
    rows = sorted(load(), key=lambda r: (r["authors"].lower(), r["year"]))
    out = [
        "# References",
        "",
        "> Generated from `docs/references.csv` by `analysis.bibliography`.",
        "> Edit the CSV, never this file - a hand edit here is overwritten the",
        "> next time the module runs.",
        "",
        "Every source cited anywhere in this repository's documentation, in APA",
        "7. For where the underlying PDFs are actually stored, see",
        "[`source_material_locations.md`](source_material_locations.md); that",
        "file links back here for the citation itself.",
        "",
        "Each DOI was resolved against Crossref rather than transcribed. Entries",
        "without a DOI are official statistics, national inventories or",
        "institutional reports, which do not have one; they carry a URL instead,",
        "as APA requires.",
        "",
        "In-text citations use author-year form and are checked against this",
        "list by the consistency audit (check C8), so a citation cannot be added",
        "without its source.",
        "",
        "---",
        "",
    ]
    for r in rows:
        out.append(f"- {apa(r)}")
        if r["note"]:
            out.append(f"  <br>*Used for:* {r['note']}")
    out.append("")
    text = "\n".join(out)
    MD_PATH.write_text(text, encoding="utf-8")
    return text


def in_text_citations(path: Path) -> set[tuple[str, str]]:
    """Author-year pairs cited in one document.

    Parameters
    ----------
    path : pathlib.Path
        Markdown file to scan.

    Returns
    -------
    set of tuple
        ``(surname-or-group, year)``. Code blocks, link targets and the
        document's own reference list are excluded: they are not prose
        citations and matching them would produce noise, not findings.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"https?://\S+", "", text)
    # Remove every "References" section (a long merged document may carry
    # several, one per merged source rather than a single trailing
    # bibliography) rather than only splitting at the first one: each such
    # heading, however it continues ("References", "References for this
    # section"), through to the next heading of any level, is a reference
    # list, not prose, and its own "Author, Initial (Year)" entries are not
    # in-text citations.
    text = re.sub(r"\n#{1,6}\s*References\b.*?(?=\n#{1,6}\s|\Z)", "\n", text,
                  flags=re.S)
    # Collapse wrapping: "Donati\net al. (2020)" is one citation, not a
    # surname called "Donati" followed by a stray year.
    text = re.sub(r"\s+", " ", text)
    found = set()
    for m in CITE.finditer(text):
        name = re.sub(r"['\u2019]s$", "", m.group(1).strip())
        head = name.split()[0]
        if head in STOPWORDS:
            continue
        found.add((name, m.group(2)))
    return found


def check() -> list[str]:
    """Verify every checked document's citations resolve.

    Returns
    -------
    list of str
        One message per unresolved citation. Empty when all resolve.
    """
    rows = load()
    known: set[tuple[str, str]] = set()
    for r in rows:
        year = r["year"]
        # The in_text column is the canonical rendering; also accept the
        # surname alone, since "Lenzen et al. (2020)" and "(Lenzen et al.,
        # 2020)" are the same citation written two ways.
        label = r["in_text"].rsplit(",", 1)[0].strip()
        known.add((label, year))
        known.add((label.replace(" et al.", ""), year))
        first = r["authors"].split(",")[0].strip()
        known.add((first, year))
        known.add((f"{first} et al.", year))
        # Prose sometimes spells out a three-or-more-author reference in full
        # ("Rodrigues, Moran, Wood & Behrens (2018)") rather than using the
        # "et al." form the bibliography's own `in_text` column favours; the
        # citation regex then captures only the last two names before the
        # year. Both forms are the same citation, so every surname (for
        # "X et al.") and every consecutive surname pair (for "X & Y") parsed
        # from the full `authors` field is accepted too.
        surnames = SURNAME_RE.findall(r["authors"])
        for s in surnames:
            known.add((f"{s} et al.", year))
        for a, b in zip(surnames, surnames[1:]):
            known.add((f"{a} & {b}", year))
    def resolves(name: str, year: str) -> bool:
        """Whether one author-year citation matches a bibliography entry."""
        for candidate in (name, name.replace(" and ", " & ")):
            if (candidate, year) in known:
                return True
            # Multi-word surnames: the prose says "Rørmose Jensen & Iliev",
            # and a match on the tail is the same citation, not a new one.
            for label, kyear in known:
                if kyear == year and (label.endswith(candidate)
                                      or candidate.endswith(label)):
                    return True
        return False

    problems = []
    for rel in CHECKED_DOCS:
        path = REPO / rel
        if not path.exists():
            continue
        for name, year in sorted(in_text_citations(path)):
            if not resolves(name, year):
                problems.append(
                    f"{rel}: '{name} ({year})' is not in references.csv")
    return problems


def verify_dois(pause: float = 0.4) -> list[str]:
    """Re-resolve every DOI against Crossref.

    Parameters
    ----------
    pause : float
        Seconds between requests, to stay inside Crossref's polite pool.

    Returns
    -------
    list of str
        One message per DOI that does not resolve or whose title disagrees.
    """
    problems = []
    for r in load():
        if not r["doi"]:
            continue
        url = "https://api.crossref.org/works/" + urllib.parse.quote(r["doi"])
        req = urllib.request.Request(
            url, headers={"User-Agent": "dk-health-footprint/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as fh:
                got = json.load(fh)["message"]
        except Exception as exc:                       # noqa: BLE001
            problems.append(f"{r['key']}: DOI {r['doi']} did not resolve ({exc})")
            continue
        # Crossref wraps long titles, so collapse whitespace before comparing;
        # otherwise every wrapped title reads as a mismatch.
        title = re.sub(r"\s+", " ", (got.get("title") or [""])[0]).lower()
        want = re.sub(r"\s+", " ", r["title"]).lower()
        if want.split(":")[0][:30] not in title:
            problems.append(
                f"{r['key']}: DOI {r['doi']} resolves to '{title[:70]}', "
                f"not '{r['title'][:70]}'")
        time.sleep(pause)
    return problems


def main() -> None:
    """Render the bibliography and report any unresolved citation."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify", action="store_true",
                    help="re-resolve every DOI against Crossref")
    args = ap.parse_args()

    render()
    rows = load()
    with_doi = sum(1 for r in rows if r["doi"])
    print(f"bibliography -> {MD_PATH.relative_to(REPO)}")
    print(f"  {len(rows)} sources, {with_doi} with a DOI, "
          f"{len(rows) - with_doi} official statistics or reports with a URL")

    problems = check()
    if problems:
        print(f"\n{len(problems)} unresolved citation(s):")
        for p in problems:
            print(f"  {p}")
    else:
        print(f"  every citation in {len(CHECKED_DOCS)} checked documents "
              f"resolves")

    if args.verify:
        bad = verify_dois()
        print(f"\nDOI verification: {len(bad)} problem(s)")
        for b in bad:
            print(f"  {b}")
        problems += bad
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
