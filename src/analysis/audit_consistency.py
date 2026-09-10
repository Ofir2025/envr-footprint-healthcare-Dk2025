# -*- coding: utf-8 -*-
"""Standing consistency audit across every gold result folder.

Two defects in this project were found only because two independently written
modules were made to agree by hand: the capital sensitivity was reading a
superseded direct-waste value from the background (160.0 kt where the Danish
account gives 42.8), and the boundary-scenario folder was serving results from a
withdrawn model vintage. Both had been sitting in the published outputs.

Neither should be found by hand. This module runs the checks that would have
caught them, and is intended to run after any rebuild.

Checks performed
----------------
**C1 Headline agreement.** The climate total must agree across the modules that
compute it independently, within the documented conventions.

**C2 Detail reconciles to aggregate.** Wherever a folder holds both a
node-detail file and its aggregate, they must sum to the same value.

**C3 Freshness.** No gold file may be older than the background it claims to be
derived from; a stale file is a wrong file.

**C4 Provenance.** Every file carrying a ``model`` column must name the current
model, so a table cannot silently retain a withdrawn vintage's label.

**C5 Manifest coverage.** Every gold file must have a lineage row.

**C7 Star-schema referential integrity.** Every foreign key in every fact table
must resolve to exactly one dimension row, every dimension primary key must be
unique and non-null, and the declared grain of each fact must hold (no duplicate
key tuples). A star model that drops rows on a join is worse than none. The
registries are ``STAR_KEYS`` and ``STAR_GRAIN``: a fact added to the model
without an entry in both is unaudited, which is why the build and this check are
kept in step. Facts stored as Parquet are read as such; facts whose source layer
is classified private are skipped where that layer is not in the tree.

**C6 Documentation agreement.** Headline numbers quoted in the revision markdown
must still reproduce from the gold outputs. Six quoted figures were found to have
drifted on 8 September 2026, two of them mutually inconsistent between documents,
because the prose was written before the AR6 restatement and the waste correction.
Prose can drift; numbers should not be able to.

**C6b Superseded values.** Checking that a current number reproduces catches a
document nobody updated. It does not catch the failure that actually occurs,
which is a number updated in one document and left standing in another. So the
superseded form itself is banned from every document that states a current
claim, and the registers that exist to record what a value used to be are named
explicitly rather than inferred.

**C14 Gold format.** Gold publishes tabular data only -- CSV, gzipped CSV,
Parquet, Markdown or ``.npy`` -- never a workbook, document or image, so a
consumer never has to open anything but a table.

**C15 Gold naming.** Every published file and directory name is lowercase, so
a path never has to be guessed.

**C16 Gold cleanliness.** Nothing in the published gold tree is untracked. An
untracked file is invisible to every other check in this module, so it is the
one defect that could otherwise grow without ever being reported.

**C17 Layer boundary.** No new module reads bronze and writes gold in one
step (medallion rule 4). The eleven names in ``LAYER_SKIPPERS`` are known
debt, carried until each module is re-plumbed through silver; the check
exists so that list can shrink and never grow.

Exit status is non-zero if any check fails, so this can gate a release.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.audit_consistency``
"""

from __future__ import annotations

import glob
import os
import subprocess
import sys
from typing import Any

import numpy as np
import pandas as pd

from analysis import gold_scope
from analysis.constants import (ANALYSIS_YEAR, BACKGROUND_YEAR, MODEL_LABEL,
                                eriksen_folder, scopes_folder)
from paths import BACKGROUND_DIR, GOLD_DIR, OUTPUT_DIR, PROJECT_ROOT

#: Tolerance for values that should be identical up to floating point.
EXACT = 1e-9

#: Differences that are expected and documented, with the reason. Any other
#: disagreement is a failure.
KNOWN_CONVENTIONS: dict[str, str] = {
    "capital_vs_scopes":
        "the capital baseline excludes the bottom-up additions, which the "
        "capital boundary cannot affect, and does not subtract the health "
        "sector's self-supply loop, which the scope partition does subtract "
        "to avoid overlapping national-accounts scope 1",
}


def _check(results: list[dict[str, Any]], name: str, passed: bool,
           detail: str) -> None:
    results.append(dict(check=name, status="PASS" if passed else "FAIL",
                        detail=detail))


def c1_headline(results: list[dict[str, Any]]) -> None:
    """Climate totals must agree across independently computing modules."""
    scopes = pd.read_csv(os.path.join(
        str(OUTPUT_DIR), *eriksen_folder().split("/"),
        "scopes_summary.csv")).set_index("Component")["kt_CO2eq"]
    grand = float(scopes["Grand Total"])
    detailed = pd.read_csv(os.path.join(
        str(OUTPUT_DIR), *scopes_folder().split("/"),
        "scopes_summary_detailed.csv"))
    climate = detailed[detailed.indicator == "climate_change"]
    # The table carries variant rows (alternative Scope 2 constructions and the
    # self-supply loop) alongside the partition, so summing every row double
    # counts. Compare the TOTAL row, and allow exactly the documented
    # self-supply-loop difference against the grand total.
    total_row = float(climate.loc[climate.scope == "TOTAL", "value"].iloc[0])
    loop = float(climate.loc[climate.scope == "self-supply loop removed",
                             "value"].sum())
    _check(results, "C1 scope partition vs grand total",
           abs((total_row + loop) - grand) < 0.01,
           f"partition total {total_row:,.2f} + self-supply loop {loop:,.2f} "
           f"= {total_row + loop:,.2f} vs grand total {grand:,.2f} kt")

    eriksen = pd.read_csv(os.path.join(
        str(OUTPUT_DIR), *eriksen_folder().split("/"),
        "hotspot_by_producing_node.csv"))
    hotspot = float(eriksen.loc[eriksen.indicator == "climate_change",
                                "value"].sum())
    _check(results, "C1 Eriksen hotspot detail vs grand total",
           abs(hotspot - grand) / grand < 1e-6,
           f"hotspot detail {hotspot:,.2f} vs {grand:,.2f} kt")


def c2_detail_vs_aggregate(results: list[dict[str, Any]]) -> None:
    """Node-detail files must sum to their aggregate companions."""
    pairs = [
        ("12_impact_categories_full",
         "impact_categories_by_producing_node.csv.gz",
         "impact_categories_all_methods.csv",
         ["method", "indicator"], "healthcare_supply_chain"),
        ("16_impact_world_plus",
         "impact_world_plus_by_producing_node.csv.gz",
         "impact_world_plus_all_categories.csv",
         ["indicator"], "healthcare_supply_chain"),
    ]
    for folder, detail_name, agg_name, keys, agg_col in pairs:
        if not gold_scope.is_present(folder):
            _check(results, f"C2 {folder} detail reconciles", True,
                   "skipped: this layer is classified private and is not in "
                   "this working copy")
            continue
        detail_path = os.path.join(str(OUTPUT_DIR), folder, detail_name)
        agg_path = os.path.join(str(OUTPUT_DIR), folder, agg_name)
        if not os.path.isdir(os.path.join(str(OUTPUT_DIR), folder)):
            # An optional layer that was not built is not an inconsistency.
            # Distributions of this repository may legitimately omit a folder;
            # only a folder that exists but is incomplete is a failure.
            _check(results, f"C2 {folder}", True, "layer not built in this tree")
            continue
        if not (os.path.exists(detail_path) and os.path.exists(agg_path)):
            _check(results, f"C2 {folder}", False,
                   "folder present but detail/aggregate file missing")
            continue
        detail = pd.read_csv(detail_path)
        agg = pd.read_csv(agg_path)
        summed = detail.groupby(keys)["value"].sum()
        target = agg.set_index(keys)[agg_col]
        joined = pd.DataFrame({"a": target, "d": summed}).dropna()
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = (joined["d"] - joined["a"]).abs() / joined["a"].abs()
        worst = float(np.nanmax(rel)) if len(joined) else 0.0
        _check(results, f"C2 {folder} detail reconciles", worst < 1e-8,
               f"{len(joined)} categories, max relative deviation {worst:.2e}")


#: Folders whose outputs do NOT derive from the prepared background, so the
#: freshness rule does not apply to them. Both read raw EXIOBASE distributions
#: and Danish national-accounts tables directly, and are therefore unaffected by
#: a background rebuild.
BACKGROUND_INDEPENDENT: frozenset[str] = frozenset({
    "09_vintage_diagnostics",          # compares raw EXIOBASE vintages to DST
    "10_sea_transport_reallocation",     # PRODUCES the corrected background, so
                                       # its outputs necessarily predate it
    "scenarios",                       # alternative boundaries, which
                                       # deliberately do not persist a
                                       # background of their own
})

#: Individual files that are likewise independent of the background.
BACKGROUND_INDEPENDENT_FILES: frozenset[str] = frozenset({
    "recipe_validation_2022.csv",      # EXIOBASE vs the Danish IOT recipe
})


def c3_freshness(results: list[dict[str, Any]]) -> None:
    """No background-derived gold file may predate the background."""
    background = os.path.join(
        str(BACKGROUND_DIR),
        f"gddz_background_information_{BACKGROUND_YEAR}.pkl")
    if not os.path.exists(background):
        # The silver background is ten gigabytes and is not in version control,
        # so it is absent from every clone. Absence is not staleness: the check
        # has no input, which is a different thing from the gold tree being out
        # of date, and failing on it would make the audit unusable anywhere the
        # pipeline has not been run.
        _check(results, "C3 no gold file older than the background", True,
               "skipped: the background is not in this checkout, so freshness "
               "cannot be tested here; run the pipeline to test it")
        return
    built = os.path.getmtime(background)
    stale = []
    for path in glob.glob(os.path.join(str(OUTPUT_DIR), "**", "*.csv*"),
                          recursive=True):
        rel = os.path.relpath(path, str(OUTPUT_DIR))
        if "manifest_lineage" in path:
            continue
        if rel.split(os.sep)[0] in BACKGROUND_INDEPENDENT:
            continue
        if os.path.basename(rel) in BACKGROUND_INDEPENDENT_FILES:
            continue
        # Year-scoped folders belong to their own background. A 2019 table is
        # not stale because the 2022 background was rebuilt after it; it is
        # derived from IOT_2016 and is checked when the audit runs for 2019.
        parts = rel.split(os.sep)
        other_year = {p for p in parts
                      if len(p) == 4 and p.isdigit() and p.startswith(("19", "20"))}
        if other_year and ANALYSIS_YEAR not in other_year:
            continue
        if os.path.getmtime(path) < built - 60:
            stale.append(rel)
    _check(results, "C3 no gold file older than the background",
           not stale,
           "all current" if not stale
           else f"{len(stale)} stale: {', '.join(sorted(stale)[:6])}"
                + (" ..." if len(stale) > 6 else ""))


def c9_gold_scope(results: list[dict[str, Any]]) -> None:
    """C9: every gold folder is declared as a paper deliverable or private.

    The published branch is a filtered view of this tree. The filter reads
    `analysis.gold_scope`, so a folder added without a classification would be
    published or withheld by accident rather than by decision.
    """
    try:
        from analysis import gold_scope
    except Exception as exc:                            # noqa: BLE001
        _check(results, "C9 gold scope declared", False, f"unavailable: {exc}")
        return
    missing = gold_scope.unclassified()
    paper = sum(1 for v in gold_scope.SCOPE.values() if v[0] == "paper")
    private = len(gold_scope.SCOPE) - paper
    _check(results, "C9 every gold folder is classified", not missing,
           f"{paper} paper deliverables, {private} private extensions"
           if not missing else f"unclassified: {', '.join(missing)}")


GOLD_ALLOWED_SUFFIXES = (".csv", ".csv.gz", ".parquet", ".md", ".npy")


def c14_gold_format(results: list[dict[str, Any]]) -> None:
    """C14: gold publishes tabular data, not workbooks, documents or images.

    Walks :data:`GOLD_DIR` (``data/gold``), not just :data:`OUTPUT_DIR`
    (``data/gold/results``), so ``data/gold/readme.md`` is covered on the
    same footing as everything under ``results/`` - C16 already walks the
    same root to check tracked-ness, so C14 and C15 match it rather than
    checking a narrower tree.
    """
    root = str(GOLD_DIR)
    if not os.path.isdir(root):
        _check(results, "C14 gold holds tabular data only", False,
               f"unavailable: GOLD_DIR does not exist: {root}")
        return
    offenders = [
        os.path.relpath(os.path.join(dirpath, name), root)
        for dirpath, _, names in os.walk(root)
        for name in names
        if not name.endswith(GOLD_ALLOWED_SUFFIXES)
    ]
    _check(results, "C14 gold holds tabular data only", not offenders,
           "; ".join(sorted(offenders)[:8]) or "clean")


def c15_gold_lowercase(results: list[dict[str, Any]]) -> None:
    """C15: every published file AND directory name is lowercase.

    Walks :data:`GOLD_DIR` for the same reason as :func:`c14_gold_format`.

    Directory names are checked as well as file names: ``os.walk`` yields
    them as its second element on every call, and a version that only
    inspects ``names`` (the files) discards that element - a capitalised
    *folder* would then pass silently, even though the spec's target state
    ("every name under ``data/gold/`` is lowercase") and the global lowercase
    constraint both cover folder names too. Both are collected as `(path,
    kind)` pairs so the failure detail says which is which.
    """
    root = str(GOLD_DIR)
    if not os.path.isdir(root):
        _check(results, "C15 every gold name is lowercase", False,
               f"unavailable: GOLD_DIR does not exist: {root}")
        return
    offenders = []
    for dirpath, dirnames, names in os.walk(root):
        for d in dirnames:
            if d != d.lower():
                offenders.append(os.path.relpath(os.path.join(dirpath, d), root) + "/")
        for name in names:
            if name != name.lower():
                offenders.append(os.path.relpath(os.path.join(dirpath, name), root))
    _check(results, "C15 every gold name is lowercase", not offenders,
           "; ".join(sorted(offenders)[:8]) or "clean")


def c16_gold_clean(results: list[dict[str, Any]]) -> None:
    """C16: nothing in the published tree is untracked.

    An untracked file is invisible to every other check in this module, so it
    is the one defect that can grow without ever being reported.

    This compares what is on disk against what git tracks, rather than asking
    git for untracked files directly. ``git ls-files --others
    --exclude-standard`` honours the caller's PERSONAL ``core.excludesFile``,
    which is a machine-local setting outside this repository: if that file
    ignores e.g. ``*.pdf``, ``*.png``, ``*.xlsx`` or ``*.csv``, exactly the
    debris this check exists to catch becomes invisible to it, on that
    machine only. Walking the tree and diffing against ``git ls-files``
    (tracked files, with no ignore semantics at all) cannot be defeated by any
    ignore file, personal or otherwise.
    """
    root = str(OUTPUT_DIR)
    gold_root = os.path.join(str(PROJECT_ROOT), "data", "gold")
    if not os.path.isdir(root):
        _check(results, "C16 no untracked file in gold", False,
               f"unavailable: OUTPUT_DIR does not exist: {root}")
        return
    out = subprocess.run(
        ["git", "ls-files", "--", "data/gold"],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    if out.returncode != 0:
        _check(results, "C16 no untracked file in gold", False,
               f"unavailable: git exited {out.returncode}: {out.stderr.strip()}")
        return
    tracked = {os.path.normpath(line) for line in out.stdout.splitlines()
              if line.strip()}
    # followlinks=True: this repo already uses a directory symlink under gold's
    # sibling data/silver/background, so the pattern is live. Plain os.walk
    # neither descends into a symlinked directory nor lists the link itself in
    # `names` (only in the discarded `dirs` slot), so without this a symlinked
    # directory under data/gold - and everything beneath it - is invisible to
    # this check.
    on_disk = {
        os.path.normpath(os.path.relpath(os.path.join(dirpath, name),
                                         str(PROJECT_ROOT)))
        for dirpath, _, names in os.walk(gold_root, followlinks=True)
        for name in names
    }
    offenders = sorted(on_disk - tracked)
    _check(results, "C16 no untracked file in gold", not offenders,
           f"{len(offenders)} untracked: {', '.join(offenders[:8])}"
           + (" ..." if len(offenders) > 8 else "") if offenders else "clean")


LAYER_SKIPPERS = {
    "build_dst_concordance", "capital_endogenised_sodersten", "capital_gfcf",
    "export_tables", "figaro_recipe_validation", "impact_categories_full",
    "main", "main_2025", "manuscript_figure_tables", "recipe_validation_2022",
    "vintage_defect_audit",
}


def c17_layer_boundary(results: list[dict[str, Any]]) -> None:
    """C17: no NEW module reads bronze and writes gold in one step.

    Medallion rule 4. The eleven in ``LAYER_SKIPPERS`` are the known debt,
    carried into the bronze phase where their read paths change anyway. The
    check exists so the list can shrink and never grow: remove a name when the
    module is re-plumbed, and C17 fails the moment a twelfth appears.
    """
    src = os.path.join(str(PROJECT_ROOT), "src", "analysis")
    own_file = os.path.basename(__file__)
    found = set()
    for name in os.listdir(src):
        if not name.endswith(".py") or name == own_file:
            # This module is the auditor, not an audited pipeline stage: it
            # never reads bronze, and the exclusion is necessary rather than
            # cosmetic, because this very check's condition below spells out
            # "BRONZE_DIR" and "EXIOBASE_DIR" as string literals next to
            # "OUTPUT_DIR", so the file that defines the heuristic always
            # contains the substrings the heuristic searches for.
            continue
        text = open(os.path.join(src, name), encoding="utf-8").read()
        if ("BRONZE_DIR" in text or "EXIOBASE_DIR" in text) and "OUTPUT_DIR" in text:
            found.add(name[:-3])
    new = sorted(found - LAYER_SKIPPERS)
    _check(results, "C17 no new bronze-to-gold module", not new,
           f"new: {', '.join(new)}" if new else f"{len(found)} known, none new")


def c8_citations(results: list[dict[str, Any]]) -> None:
    """C8: every in-text citation resolves to the bibliography.

    A citation that cannot be traced is worse than none, because it reads as
    evidence. One document carried a corroborating figure attributed to a paper
    that is not in the reference library and could not be checked; the claim was
    withdrawn and this check exists so the next one is caught.
    """
    try:
        from analysis import bibliography
    except Exception as exc:                            # noqa: BLE001
        _check(results, "C8 citations resolve", False, f"unavailable: {exc}")
        return
    try:
        problems = bibliography.check()
        n_sources = len(bibliography.load())
    except AssertionError as exc:
        _check(results, "C8 citations resolve", False, str(exc))
        return
    _check(results, "C8 every citation resolves", not problems,
           f"{n_sources} sources, {len(bibliography.CHECKED_DOCS)} documents "
           f"checked" if not problems
           else f"{len(problems)} unresolved: {problems[0]}")


def c4_provenance(results: list[dict[str, Any]]) -> None:
    """Every file naming a model must name the current one."""
    wrong = []
    for path in glob.glob(os.path.join(str(OUTPUT_DIR), "**", "*.csv"),
                          recursive=True):
        if "manifest_lineage" in path:
            continue
        try:
            head = pd.read_csv(path, nrows=200)
        except Exception:                                  # noqa: BLE001
            continue
        if "model" not in head.columns:
            continue
        labels = {str(v) for v in head["model"].dropna().unique()}
        foreign = {v for v in labels
                   if v != MODEL_LABEL and "EXIOBASE" in v
                   and "v3.8.2" not in v}
        if foreign:
            wrong.append((os.path.relpath(path, str(OUTPUT_DIR)),
                          sorted(foreign)[0][:60]))
    _check(results, "C4 no gold file carries a superseded model label",
           not wrong,
           "all current" if not wrong
           else f"{len(wrong)} files, e.g. {wrong[0][0]} -> {wrong[0][1]}")


def c5_manifest(results: list[dict[str, Any]]) -> None:
    """Every gold file must have a lineage row."""
    manifest_path = os.path.join(str(OUTPUT_DIR), "manifest_lineage.csv")
    if not os.path.exists(manifest_path):
        _check(results, "C5 manifest", False, "manifest not found")
        return
    manifest = pd.read_csv(manifest_path)
    listed = set(manifest.iloc[:, manifest.columns.get_loc("file")]) \
        if "file" in manifest.columns else set()
    on_disk = {os.path.relpath(p, str(OUTPUT_DIR))
               for p in glob.glob(os.path.join(str(OUTPUT_DIR), "**", "*.csv*"),
                                  recursive=True)
               if "manifest_lineage" not in p}
    missing = {f for f in on_disk
               if not any(f.endswith(os.path.basename(x)) for x in listed)}
    _check(results, "C5 every gold file has a lineage row",
           len(missing) <= 0,
           f"{len(on_disk)} files on disk, {len(missing)} unlisted"
           + (f": {sorted(missing)[0]}" if missing else ""))


#: Headline numbers that the revision documents quote, and where each is
#: computed from. ``doc`` is the markdown that must contain ``text`` verbatim.
DOCUMENTED_NUMBERS: tuple[dict[str, Any], ...] = (
    dict(text="4,712", doc="docs/revision/analysis_2022.md",
         source=(f"{eriksen_folder()}/hotspot_by_producing_node.csv",
                 "climate_change"),
         expect=4712.4, tol=0.2, what="health-care climate footprint, kt"),
    dict(text="3,943", doc="docs/revision/shipping_reallocation_method.md",
         source=("17_health_subsectors/footprint_by_health_function.csv",
                 "climate_change"),
         expect=3943.4, tol=1.0,
         what="MRIO supply-chain component (SHA functions), kt"),
    dict(text="77.5 Mt", doc="docs/revision/analysis_2022.md",
         source=("00_core_footprint/national_totals_summary.csv",
                 "climate_change"),
         expect=77477.5, tol=50.0, what="Danish national footprint, kt",
         column="national_footprint"),
)

#: Values that were quoted in the documentation and have since been superseded.
#: Checking that a current number reproduces catches a document that was never
#: updated; it does not catch a document that was updated in one place and not
#: another, which is how every drift found on 8 September 2026 actually
#: happened. So the superseded form is banned outright from the documents that
#: state current claims, and any future legitimate use has to be argued for
#: here rather than appearing silently.
SUPERSEDED_TEXT: tuple[tuple[str, str], ...] = (
    ("4,064-5,540", "pre-correction 95 % interval; the current one is 4,065 to 5,532"),
    ("4,059-5,531", "pre-correction 95 % interval from the correlation sweep"),
    ("4,057-5,546", "pre-correction 95 % interval"),
    ("4 063.9", "pre-correction interval, also with a thin-space separator"),
    ("86.8 %", "input-output share of variance before the covariance term was "
               "reported separately; it is 78.8 %"),
    ("18.9 %", "transport share after the reallocation; it is 18.5 % of the "
               "supply-chain component and 15.4 % of the total"),
    ("67.9 %", "first three production layers; the value is 63.0 %"),
    ("872.8", "domestic-only Malik total; the value is 839.5 kt"),
    ("822 kt", "Danish sea-transport node before the reallocation; it is 852 kt"),
    ("12.7 kt", "anaesthetic-gas item before the medstat register replaced the "
                "proxy; it is 12.5 kt"),
    ("4,715 kt", "health-care climate footprint; it is 4,713 kt"),
    ("4,736 kt", "Monte Carlo median; it is 4,735 kt"),
    ("4,875 kt", "health-care climate footprint from a superseded run"),
    ("4,713 kt", "health-care climate footprint before the bottom-up nitrous "
                 "oxide moved to AR6; it is 4,712 kt"),
    ("4,713.4", "the same, to one decimal"),
    ("4,713.37", "the same, to two decimals"),
    ("4,711.53", "scope partition total before the same change; it is 4,710.58"),
    ("4,065 to 5,532", "95 % interval before the same change; it is 4,064 to 5,531"),
    ("4,735 kt", "Monte Carlo median before the same change; it is 4,734 kt"),
)

#: Documents that record what a number used to be, and therefore must be
#: allowed to contain a superseded form. Everything else under the revision,
#: replication and figure trees states current claims.
HISTORICAL_DOCS: frozenset[str] = frozenset({
    # the register of what was asked for and what each answer used to say
    "docs/revision/request_checklist.md",
    # a before-and-after table of every fix, so the "before" is the point
    "docs/revision/bug_and_method_fixes.md",
    # carries its own corrections table, listing the value each figure replaced
    "docs/revision/anomalies_bugs_and_open_questions.md",
    # a dated reply, quoting the branch state on the day it was written;
    # rewriting its numbers would falsify a record rather than correct it
    "docs/revision/response_to_requests_2026_09_07.md",
})

#: Trees whose markdown states current claims.
CLAIM_TREES: tuple[str, ...] = ("docs/revision", "docs/methods/replications",
                                "figures/manuscript")


def c6b_superseded(results: list[dict[str, Any]]) -> None:
    """No current-claim document may quote a value that has been superseded.

    Parameters
    ----------
    results : list of dict
        Accumulator the check appends its verdict to.
    """
    repo = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    hits: list[str] = []
    scanned = 0
    for tree in CLAIM_TREES:
        for path in sorted(glob.glob(os.path.join(repo, tree, "**", "*.md"),
                                     recursive=True)):
            rel = os.path.relpath(path, repo)
            if rel in HISTORICAL_DOCS:
                continue
            scanned += 1
            body = open(path, encoding="utf-8").read()
            for text, why in SUPERSEDED_TEXT:
                if text in body:
                    hits.append(f"{rel} quotes {text!r} ({why})")
    detail = ("; ".join(hits[:3]) + (f"; and {len(hits) - 3} more"
                                     if len(hits) > 3 else "")) if hits else (
        f"{scanned} documents carry none of the {len(SUPERSEDED_TEXT)} "
        f"superseded values")
    _check(results, "C6 no document quotes a superseded value",
           not hits, detail)


def c6_documentation(results: list[dict[str, Any]]) -> None:
    """Headline numbers quoted in the revision docs must still reproduce.

    Parameters
    ----------
    results : list of dict
        Accumulator the check appends its verdict to.
    """
    repo = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    stale: list[str] = []
    skipped: list[str] = []
    for entry in DOCUMENTED_NUMBERS:
        rel, indicator = entry["source"]
        path = os.path.join(str(OUTPUT_DIR), rel)
        if not os.path.exists(path):
            # The layer this number comes from is not in this distribution.
            # Skipping is correct: the check has no input, which is not the
            # same as the documentation being wrong.
            skipped.append(entry["what"])
            continue
        frame = pd.read_csv(path)
        rows = frame[frame["indicator"].astype(str).str.contains(indicator)]
        if "column" in entry:
            got = float(rows[entry["column"]].iloc[0])
        else:
            keep = rows
            for group in entry.get("subtract_groups", ()):
                col = next((c for c in rows.columns
                            if c.endswith("sector_group")), None)
                if col is not None:
                    keep = keep[keep[col] != group]
            got = float(keep["value"].sum())
        if abs(got - entry["expect"]) > entry["tol"]:
            stale.append(f"{entry['what']}: gold {got:,.1f} vs registry "
                         f"{entry['expect']:,.1f}")
            continue
        doc = os.path.join(repo, entry["doc"])
        if not os.path.exists(doc):
            stale.append(f"{entry['doc']} missing")
        elif entry["text"] not in open(doc, encoding="utf-8").read():
            stale.append(f"{entry['doc']} no longer quotes "
                         f"{entry['text']!r} ({entry['what']})")
    checked = len(DOCUMENTED_NUMBERS) - len(skipped)
    detail = "; ".join(stale) if stale else f"{checked} documented numbers reproduce"
    if skipped and not stale:
        detail += f" ({len(skipped)} skipped, layer not in this tree)"
    _check(results, "C6 revision docs quote the current numbers", not stale, detail)


#: fact -> (foreign key column, dimension file, dimension primary key).
#: ``model_id`` is checked on every fact, so it is listed once per fact rather
#: than repeated here.
STAR_KEYS: tuple[tuple[str, str, str, str], ...] = (
    ("fact_footprint_node", "indicator_id", "dim_indicator", "indicator_id"),
    ("fact_footprint_node", "demand_component_id", "dim_demand_component", "demand_component_id"),
    ("fact_footprint_node", "producing_region_id", "dim_region", "region_id"),
    ("fact_footprint_node", "producing_industry_id", "dim_industry", "industry_id"),
    ("fact_footprint_product", "purchased_region_id", "dim_region", "region_id"),
    ("fact_footprint_product", "purchased_industry_id", "dim_industry", "industry_id"),
    ("fact_footprint_bilateral", "indicator_id", "dim_indicator", "indicator_id"),
    ("fact_footprint_bilateral", "demand_component_id", "dim_demand_component", "demand_component_id"),
    ("fact_footprint_bilateral", "producing_region_id", "dim_region", "region_id"),
    ("fact_footprint_bilateral", "producing_industry_id", "dim_industry", "industry_id"),
    ("fact_footprint_bilateral", "purchased_region_id", "dim_region", "region_id"),
    ("fact_footprint_bilateral", "purchased_industry_id", "dim_industry", "industry_id"),
    ("fact_scope_node", "scope_id", "dim_scope", "scope_id"),
    ("fact_scope_node", "producing_region_id", "dim_region", "region_id"),
    ("fact_scope_node", "producing_industry_id", "dim_industry", "industry_id"),
    ("fact_scope_component", "indicator_id", "dim_indicator", "indicator_id"),
    ("fact_scope_component", "scope_component_id", "dim_scope_component", "scope_component_id"),
    ("fact_national_total", "indicator_id", "dim_indicator", "indicator_id"),
    ("fact_health_function", "health_function_id", "dim_health_function", "health_function_id"),
    ("fact_health_function_node", "indicator_id", "dim_indicator", "indicator_id"),
    ("fact_health_function_node", "health_function_id", "dim_health_function", "health_function_id"),
    ("fact_health_function_node", "producing_region_id", "dim_region", "region_id"),
    ("fact_health_function_node", "producing_industry_id", "dim_industry", "industry_id"),
    ("fact_health_expenditure", "demand_component_id", "dim_demand_component", "demand_component_id"),
    ("fact_health_expenditure", "purchased_region_id", "dim_region", "region_id"),
    ("fact_health_expenditure", "purchased_industry_id", "dim_industry", "industry_id"),
    ("fact_scenario_node", "scenario_id", "dim_scenario", "scenario_id"),
    ("fact_scenario_node", "indicator_id", "dim_indicator", "indicator_id"),
    ("fact_scenario_node", "producing_region_id", "dim_region", "region_id"),
    ("fact_scenario_node", "producing_industry_id", "dim_industry", "industry_id"),
    ("fact_production_layer", "indicator_id", "dim_indicator", "indicator_id"),
    ("fact_production_layer", "production_layer_id", "dim_production_layer", "production_layer_id"),
    ("fact_production_layer", "producing_region_id", "dim_region", "region_id"),
    ("fact_production_layer", "producing_industry_id", "dim_industry", "industry_id"),
    ("fact_impact_node", "impact_category_id", "dim_impact_category", "impact_category_id"),
    ("fact_impact_node", "producing_region_id", "dim_region", "region_id"),
    ("fact_impact_node", "producing_industry_id", "dim_industry", "industry_id"),
    ("fact_capital_node", "capital_treatment_id", "dim_capital_treatment", "capital_treatment_id"),
    ("fact_capital_node", "indicator_id", "dim_indicator", "indicator_id"),
    ("fact_capital_node", "producing_region_id", "dim_region", "region_id"),
    ("fact_capital_node", "producing_industry_id", "dim_industry", "industry_id"),
    ("fact_capital_scenario", "capital_treatment_id", "dim_capital_treatment", "capital_treatment_id"),
    ("fact_capital_scenario", "indicator_id", "dim_indicator", "indicator_id"),
    ("fact_ghg_species", "substance_id", "dim_substance", "substance_id"),
    ("fact_gwp_vintage", "gwp_vintage_id", "dim_gwp_vintage", "gwp_vintage_id"),
    ("fact_gwp_vintage", "indicator_id", "dim_indicator", "indicator_id"),
    ("fact_uncertainty_draw", "indicator_id", "dim_indicator", "indicator_id"),
    ("fact_uncertainty_draw", "draw_group_id", "dim_draw_group", "draw_group_id"),
)

#: fact -> the columns that define its declared grain.
STAR_GRAIN: dict[str, list[str]] = {
    "fact_footprint_node": ["model_id", "indicator_id", "demand_component_id",
                            "producing_region_id", "producing_industry_id"],
    "fact_footprint_product": ["model_id", "indicator_id", "demand_component_id",
                               "purchased_region_id", "purchased_industry_id"],
    "fact_footprint_bilateral": ["model_id", "indicator_id",
                                 "demand_component_id", "producing_region_id",
                                 "producing_industry_id", "purchased_region_id",
                                 "purchased_industry_id"],
    "fact_scope_node": ["model_id", "indicator_id", "scope_id",
                        "producing_region_id", "producing_industry_id"],
    "fact_scope_component": ["model_id", "indicator_id", "scope_component_id"],
    "fact_national_total": ["model_id", "indicator_id"],
    "fact_health_function": ["model_id", "indicator_id", "health_function_id"],
    "fact_health_function_node": ["model_id", "indicator_id",
                                  "health_function_id", "producing_region_id",
                                  "producing_industry_id"],
    "fact_health_expenditure": ["model_id", "demand_component_id",
                                "purchased_region_id", "purchased_industry_id"],
    "fact_scenario_node": ["model_id", "scenario_id", "indicator_id",
                           "producing_region_id", "producing_industry_id"],
    "fact_production_layer": ["model_id", "indicator_id",
                              "production_layer_id", "producing_region_id",
                              "producing_industry_id"],
    "fact_impact_node": ["model_id", "impact_category_id",
                         "producing_region_id", "producing_industry_id"],
    "fact_capital_node": ["model_id", "capital_treatment_id", "indicator_id",
                          "producing_region_id", "producing_industry_id"],
    "fact_capital_scenario": ["model_id", "capital_treatment_id",
                              "indicator_id"],
    "fact_ghg_species": ["model_id", "substance_id"],
    "fact_gwp_vintage": ["model_id", "gwp_vintage_id", "indicator_id"],
    "fact_uncertainty_draw": ["model_id", "indicator_id", "draw_id",
                              "draw_group_id"],
}


def c7_star_integrity(results: list[dict[str, Any]]) -> None:
    """Foreign keys resolve, primary keys are unique, and each grain holds.

    A fact whose source layer is classified private is absent from the working
    copy that feeds the co-author's branch, and is skipped rather than counted as
    a broken key: the check has no input, which is not the same as the model
    being wrong. A fact that IS present with a missing dimension still fails.

    Parameters
    ----------
    results : list of dict
        Accumulator the check appends its verdicts to.
    """
    star = os.path.join(str(OUTPUT_DIR), "star")
    if not os.path.isdir(star):
        _check(results, "C7 star schema", True, "star schema not built in this tree")
        return

    cache: dict[str, pd.DataFrame] = {}

    def load(name: str) -> pd.DataFrame:
        """Read one star table, whichever of the two formats holds it."""
        if name not in cache:
            csv = os.path.join(star, f"{name}.csv")
            parquet = os.path.join(star, f"{name}.parquet")
            if os.path.exists(csv):
                cache[name] = pd.read_csv(csv)
            elif os.path.exists(parquet):
                cache[name] = pd.read_parquet(parquet)
            else:
                raise FileNotFoundError(name)
        return cache[name]

    def present(name: str) -> bool:
        return any(os.path.exists(os.path.join(star, f"{name}{ext}"))
                   for ext in (".csv", ".parquet"))

    orphans: list[str] = []
    skipped: set[str] = set()
    checked = 0
    facts = {fact for fact, _, _, _ in STAR_KEYS} | set(STAR_GRAIN)
    # Every fact carries model_id, so check it once per fact rather than listing
    # it 16 times in the registry.
    keys = tuple(STAR_KEYS) + tuple(
        (fact, "model_id", "dim_model", "model_id") for fact in sorted(facts))
    for fact, fk, dim, pk in keys:
        if not present(fact):
            skipped.add(fact)
            continue
        try:
            f, d = load(fact), load(dim)
        except FileNotFoundError:
            orphans.append(f"{fact}.{fk} -> {dim}: dimension not in this tree")
            continue
        checked += 1
        missing = set(f[fk].dropna().unique()) - set(d[pk].unique())
        if missing:
            orphans.append(f"{fact}.{fk} -> {dim}: {len(missing)} unmatched, "
                           f"e.g. {sorted(missing)[:3]}")
    # A duplicated or null dimension primary key is the other way a join goes
    # wrong -- it fans rows out instead of dropping them -- so it is graded here
    # rather than as a separate check. The build asserts it before writing; this
    # asserts it of what is on disk, which is what a consumer actually loads.
    dims = sorted({dim for _, _, dim, _ in STAR_KEYS}
                  | {"dim_model", "dim_industry_group"})
    n_dims = 0
    for name in dims:
        if not present(name):
            continue
        frame = load(name)
        pk = f"{name[4:]}_id"
        pk = pk if pk in frame.columns else frame.columns[0]
        n_dims += 1
        if not frame[pk].is_unique:
            orphans.append(f"{name}.{pk} is not unique")
        elif frame[pk].isna().any():
            orphans.append(f"{name}.{pk} has nulls")

    detail = (f"{checked} foreign keys, 0 orphans; {n_dims} dimension keys "
              f"unique and complete")
    if skipped:
        detail += (f" ({len(skipped)} fact(s) not in this tree: "
                   f"{', '.join(sorted(skipped))})")
    _check(results, "C7 star schema foreign keys resolve", not orphans,
           "; ".join(orphans) if orphans else detail)

    dupes: list[str] = []
    graded = 0
    for fact, grain in STAR_GRAIN.items():
        if not present(fact):
            continue
        f = load(fact)
        graded += 1
        n = int(f.duplicated(subset=grain).sum())
        if n:
            dupes.append(f"{fact}: {n:,} rows breach the declared grain")
    _check(results, "C7 star schema grain holds", not dupes,
           "; ".join(dupes) if dupes
           else f"{graded} facts, no duplicate key tuples")


def c10_repo_profile(results: list[dict[str, Any]]) -> None:
    """A paper-scope working copy may not hold private material.

    The two working copies exist to carry different scopes. The copy that feeds
    the co-author's branch holds the manuscript's deliverables; the private copy
    holds those plus the follow-on layers, the reference PDFs, the deck and the
    feedback. Until now the separation happened only at publish time, inside a
    filter that rewrites history on the way out, which means the private
    material sat in the copy that pushes and a mistake there is a disclosure.
    This check makes the separation a property of the working copy instead.

    Parameters
    ----------
    results : list of dict
        Accumulator the check appends its verdict to.
    """
    prof = gold_scope.profile()
    stray = gold_scope.out_of_profile()
    if prof == "undeclared":
        _check(results, "C10 working copy carries only its declared scope", True,
               "skipped: this copy declares no scope in .repo_scope")
        return
    _check(results, "C10 working copy carries only its declared scope",
           not stray,
           f"profile {prof!r}, nothing out of place" if not stray else
           f"profile {prof!r}, {len(stray)} private path(s) present: "
           + ", ".join(stray[:3]))


def main() -> None:
    """Run every check and write the report; exit non-zero on failure."""
    results: list[dict[str, Any]] = []
    for check in (c1_headline, c2_detail_vs_aggregate, c3_freshness,
                  c4_provenance, c5_manifest, c6_documentation, c6b_superseded,
                  c7_star_integrity,
                  c8_citations, c9_gold_scope,
                  c14_gold_format, c15_gold_lowercase, c16_gold_clean,
                  c17_layer_boundary,
                  c10_repo_profile):
        try:
            check(results)
        except Exception as exc:                            # noqa: BLE001
            _check(results, check.__name__, False, f"raised {exc!r}")

    table = pd.DataFrame(results)
    table["known_conventions"] = "; ".join(KNOWN_CONVENTIONS.values())
    out_dir = os.path.join(str(OUTPUT_DIR), "06_benchmarks_validation")
    os.makedirs(out_dir, exist_ok=True)
    table.to_csv(os.path.join(out_dir, "consistency_audit.csv"), index=False)

    pd.set_option("display.width", 200)
    print(table[["check", "status", "detail"]]
          .to_string(index=False, max_colwidth=96))
    failed = int((table.status == "FAIL").sum())
    print(f"\n{len(table) - failed} passed, {failed} failed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
