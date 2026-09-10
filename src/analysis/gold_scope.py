# -*- coding: utf-8 -*-
"""Which gold folders are the paper's deliverables, and which are private.

This repository is the full working copy: it carries every analysis layer,
including the ones that exist to answer a question the paper does not ask. The
branch published for the co-author carries a subset. Until now the subset was a
hand-maintained array in the publish script, which is exactly the kind of list
that drifts from what anyone believes it contains.

The classification lives here instead, once, with a reason per folder. The
publish script reads it, the audit checks that every folder on disk is
classified, and the gold README is generated from it. Adding a layer without
deciding whether it ships is therefore an error rather than an oversight.

Nothing is duplicated on disk. Both repositories hold the same
``data/gold/results`` tree; the classification says which parts of it the
published branch keeps, and the filter in
``scripts/release/publish_ofir_branch.sh`` applies it at publish time.

Run
---
``PYTHONPATH=src python -m analysis.gold_scope``            report and render
``PYTHONPATH=src python -m analysis.gold_scope --exclude``  paths to filter out
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GOLD = REPO / "data" / "gold" / "results"
# The tracked filename is lowercase; macOS is case-insensitive, so a case-only
# rename here would be a no-op on disk and a phantom rename in git.
README = GOLD / "readme.md"

#: folder -> (scope, why). ``paper`` folders back a number, figure, or table in
#: the manuscript or in the response to the reviewers, and ship. ``private``
#: folders are follow-on work: real analysis, but for the next paper.
SCOPE: dict[str, tuple[str, str]] = {
    "00_core_footprint": (
        "paper", "the footprint itself; every headline number"),
    "01_eriksen_replication": (
        "paper", "the replication the manuscript is; figures 1-3 and S1"),
    "02_scopes_wood_hertwich": (
        "paper", "the GHG-Protocol scope split; figures 3-6"),
    "03_cabernard_target_scope3": (
        "paper", "the double-counting audit the reviewers' aggregation "
                 "question turns on"),
    "04_uncertainty_lenzen_ieooc": (
        "paper", "the Monte Carlo answering the first reviewer"),
    "05_waste_dst_accounts": (
        "paper", "the Danish waste account that replaced the 2011 hybrid "
                 "extension"),
    "06_benchmarks_validation": (
        "paper", "the boundary-matched comparison with Schmidt & Merciai; "
                 "figure 7"),
    "07_malik_replication": (
        "paper", "capital-boundary comparator; Malik et al. include capital "
                 "where the other comparators exclude it"),
    "08_lenzen_replication": (
        "paper", "the comparator behind the uncertainty calibration and the "
                 "national-total family comparison"),
    "09_exiobase_release_diagnostics": (
        "paper", "the **only** evidence for rejecting EXIOBASE v3.10.2, which "
                 "the response states as fact"),
    "10_sea_transport_reallocation": (
        "paper", "the sea-transport reallocation, on which the withdrawn "
                 "transport finding depends"),
    "11_capital_gfcf": (
        "paper", "the capital treatment; the second step of figure 7"),
    "12_impact_categories_full": (
        "paper", "the full characterisation behind the five reported "
                 "categories"),
    "13_steenmeijer_replication": (
        "paper", "the Dutch study this replicates"),
    "14_eckelman_replication": (
        "paper", "comparator in the same boundary table as 07 and 08"),
    "15_gwp_revision": (
        "paper", "the AR6-versus-AR4 restatement the response leads on"),
    "16_impact_world_plus": (
        "private", "IMPACT World+ characterisation; a methods paper of its "
                   "own, cited by nothing in this revision"),
    "17_health_subsectors": (
        "private", "health sub-sector decomposition; the follow-on paper"),
    "18_mitigation_scenarios": (
        "paper", "the counterfactual scenarios; figures 8 and 9"),
    "19_tables_of_record": (
        "paper", "the verified tables of record, regenerated from the gold "
                 "facts, that supersede the values circulated during drafting"),
    "20_production_layers": (
        "paper", "how far upstream the pressure occurs; the production-layer "
                 "decomposition reported for the revision"),
    "scenarios": (
        "paper", "the sector-boundary scenarios behind the childcare step of "
                 "figure 7"),
    "star": (
        "paper", "the star schema over the reported facts"),
}

#: Source and documentation files that travel with a private folder.
PRIVATE_COMPANIONS: dict[str, tuple[str, ...]] = {
    "16_impact_world_plus": ("docs/methods/replications/16_impact_world_plus.md",
                             "src/analysis/impact_world_plus.py"),
    "17_health_subsectors": ("docs/methods/replications/17_health_subsectors.md",
                             "src/analysis/health_subsector_footprints.py",
                             "src/analysis/health_function_recipes.py",
                             # The star schema folder is a paper deliverable,
                             # but three of its files exist only where the
                             # health-function layer has been built, and
                             # table 9 is that layer's table of record. Without
                             # naming them, C10 would pass on a paper copy that
                             # had somehow acquired the private decomposition.
                             "data/gold/results/star/dim_health_function.csv",
                             "data/gold/results/star/fact_health_function.csv",
                             "data/gold/results/star/"
                             "fact_health_function_node.parquet",
                             "data/gold/results/19_tables_of_record/"
                             "table_09.csv"),
}


#: Marker naming which scope a working copy carries. ``paper`` copies hold the
#: manuscript's deliverables and nothing else; ``full`` copies hold those plus
#: the follow-on layers and the private material. The marker is explicit rather
#: than inferred from the git remote, because a clone can be re-pointed and the
#: consequence of guessing wrong is publishing private work.
PROFILE_FILE = REPO / ".repo_scope"


def profile() -> str:
    """Which scope this working copy declares.

    Returns
    -------
    str
        ``"paper"``, ``"full"``, or ``"undeclared"`` when the marker is absent.
    """
    if not PROFILE_FILE.exists():
        return "undeclared"
    return PROFILE_FILE.read_text(encoding="utf-8").strip().split()[0].lower()


def _tracked(path: str) -> bool:
    """Whether git tracks anything under a repository-relative path.

    Parameters
    ----------
    path : str
        Repository-relative file or directory.

    Returns
    -------
    bool
        True when ``git ls-files`` reports at least one entry.
    """
    out = subprocess.run(["git", "ls-files", "--", path], cwd=str(REPO),
                         capture_output=True, text=True)
    return bool(out.stdout.strip())


def out_of_profile() -> list[str]:
    """Private paths **tracked** in a copy that declares itself ``paper``.

    Tracking is the test rather than presence on disk, because tracking is what
    a push or a merge carries. An untracked copy of a reference PDF sitting in
    a working directory is untidy; a tracked one is a disclosure waiting for
    someone to run the wrong command.

    Returns
    -------
    list of str
        Repository-relative paths that should not be tracked here. Empty for a
        ``full`` or ``undeclared`` copy, where nothing is out of place by
        definition.
    """
    if profile() != "paper":
        return []
    bad: list[str] = []
    for name, (scope, _) in sorted(SCOPE.items()):
        if scope != "private":
            continue
        if _tracked(f"data/gold/results/{name}"):
            bad.append(f"data/gold/results/{name}")
        bad.extend(c for c in PRIVATE_COMPANIONS.get(name, ()) if _tracked(c))
    for extra in ("docs/presentation", "docs/references", "docs/feedback",
                  "reports/source"):
        if _tracked(extra):
            bad.append(extra)
    return bad


def is_present(folder: str) -> bool:
    """Whether a gold folder exists in this working copy.

    The two working copies hold different scopes on purpose: the copy that
    feeds the co-author's branch carries the paper's deliverables, and the
    private copy carries those plus the follow-on layers. A module that reads a
    private layer must therefore ask whether it is here rather than assume it,
    and must skip cleanly and say so when it is not. Failing instead would make
    the same pipeline pass in one copy and fail in the other for no reason but
    scope.

    Parameters
    ----------
    folder : str
        Gold folder name, for example ``"17_health_subsectors"``.

    Returns
    -------
    bool
        True when the folder exists under ``data/gold/results``.
    """
    return (GOLD / folder).is_dir()


def folders_on_disk() -> list[str]:
    """Gold folders present in the working copy."""
    if not GOLD.exists():
        return []
    return sorted(p.name for p in GOLD.iterdir() if p.is_dir())


def unclassified() -> list[str]:
    """Folders on disk with no entry in :data:`SCOPE`.

    Returns
    -------
    list of str
        Empty when every folder is classified.
    """
    return [f for f in folders_on_disk() if f not in SCOPE]


def missing_private() -> list[str]:
    """Private folders declared in :data:`SCOPE` but absent from this copy.

    Returns
    -------
    list of str
        Sorted folder names. Non-empty in the working copy that feeds the
        co-author's branch, empty in the private one.
    """
    on_disk = set(folders_on_disk())
    return sorted(name for name, (scope, _) in SCOPE.items()
                  if scope == "private" and name not in on_disk)


def exclude_paths() -> list[str]:
    """Repository paths the published branch must not carry.

    Returns
    -------
    list of str
        Gold folders classified ``private``, plus the documentation and source
        that exists only to serve them.
    """
    out = []
    for name, (scope, _) in sorted(SCOPE.items()):
        if scope != "private":
            continue
        out.append(f"data/gold/results/{name}")
        out.extend(PRIVATE_COMPANIONS.get(name, ()))
    return out


def render() -> str:
    """Write the gold README from the classification and return its text."""
    paper = [(k, v[1]) for k, v in sorted(SCOPE.items()) if v[0] == "paper"]
    private = [(k, v[1]) for k, v in sorted(SCOPE.items()) if v[0] == "private"]
    lines = [
        "# Gold results",
        "",
        "Every table here is a deliverable at the most detailed level the model",
        "supports (producing country x producing sector x purchased product x",
        "demand component), so all aggregates are derivable and no lineage is",
        "lost. Lineage for every file is in `manifest_lineage.csv`.",
        "",
        "## Two scopes, one tree",
        "",
        "This working copy holds every layer. The branch published for the",
        "co-author holds the layers below marked **paper**. Nothing is",
        "duplicated on disk: the classification lives in `analysis.gold_scope`,",
        "the publish filter reads it, and the consistency audit fails if a",
        "folder appears here without being classified. This file is generated:",
        "edit `src/analysis/gold_scope.py`, never this text.",
        "",
        f"### Paper deliverables ({len(paper)} folders)",
        "",
        "Each backs a number, figure, or table in the manuscript or in the",
        "response to the reviewers.",
        "",
        "| folder | why it ships |",
        "|:---|:---|",
    ]
    lines += [f"| `{k}` | {w} |" for k, w in paper]
    lines += [
        "",
        f"### Private extensions ({len(private)} folders)",
        "",
        "Each is real analysis, kept in this repository only: follow-on work",
        "that nothing in the current revision cites.",
        "",
        "| folder | why it stays here |",
        "|:---|:---|",
    ]
    lines += [f"| `{k}` | {w} |" for k, w in private]
    lines += [
        "",
        "## Naming",
        "",
        "Use lowercase `snake_case`, add the analysis year where a table is",
        "year-specific, and keep out editor lock files and temporary",
        "artefacts. Layers whose results differ by reference year are stored",
        "under a year subdirectory (`01_eriksen_replication/2022`), so a run for",
        "one year cannot overwrite another.",
        "",
    ]
    text = "\n".join(lines)
    README.write_text(text, encoding="utf-8")
    return text


def main() -> None:
    """Report the classification, or print the publish filter's exclude list."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exclude", action="store_true",
                    help="print the paths the published branch must not carry")
    args = ap.parse_args()

    if args.exclude:
        print("\n".join(exclude_paths()))
        return

    render()
    missing = unclassified()
    paper = sum(1 for v in SCOPE.values() if v[0] == "paper")
    private = len(SCOPE) - paper
    print(f"gold scope -> {README.relative_to(REPO)}")
    print(f"  {paper} paper deliverables, {private} private extensions")
    if missing:
        print(f"  {len(missing)} folder(s) on disk are not classified: "
              f"{', '.join(missing)}")
    else:
        print(f"  every folder on disk is classified "
              f"({len(folders_on_disk())} present)")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
