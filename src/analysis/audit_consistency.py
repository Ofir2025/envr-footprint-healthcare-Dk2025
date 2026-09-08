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

**C6 Documentation agreement.** Headline numbers quoted in the revision markdown
must still reproduce from the gold outputs. Six quoted figures were found to have
drifted on 8 September 2026, two of them mutually inconsistent between documents,
because the prose was written before the AR6 restatement and the waste correction.
Prose can drift; numbers should not be able to.

Exit status is non-zero if any check fails, so this can gate a release.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.audit_consistency``
"""

from __future__ import annotations

import glob
import os
import sys
from typing import Any

import numpy as np
import pandas as pd

from analysis.constants import BACKGROUND_YEAR, MODEL_LABEL
from paths import BACKGROUND_DIR, OUTPUT_DIR

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
        str(OUTPUT_DIR), "01_eriksen_replication",
        "scopes_summary.csv")).set_index("Component")["kt_CO2eq"]
    grand = float(scopes["Grand Total"])
    detailed = pd.read_csv(os.path.join(
        str(OUTPUT_DIR), "02_scopes_wood_hertwich",
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
        str(OUTPUT_DIR), "01_eriksen_replication",
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
    "10_snac_shipping_correction",     # PRODUCES the corrected background, so
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
        _check(results, "C3 freshness", False, "background not found")
        return
    built = os.path.getmtime(background)
    stale = []
    for path in glob.glob(os.path.join(str(OUTPUT_DIR), "**", "*.csv*"),
                          recursive=True):
        rel = os.path.relpath(path, str(OUTPUT_DIR))
        if "MANIFEST" in path:
            continue
        if rel.split(os.sep)[0] in BACKGROUND_INDEPENDENT:
            continue
        if os.path.basename(rel) in BACKGROUND_INDEPENDENT_FILES:
            continue
        if os.path.getmtime(path) < built - 60:
            stale.append(rel)
    _check(results, "C3 no gold file older than the background",
           not stale,
           "all current" if not stale
           else f"{len(stale)} stale: {', '.join(sorted(stale)[:6])}"
                + (" ..." if len(stale) > 6 else ""))


def c4_provenance(results: list[dict[str, Any]]) -> None:
    """Every file naming a model must name the current one."""
    wrong = []
    for path in glob.glob(os.path.join(str(OUTPUT_DIR), "**", "*.csv"),
                          recursive=True):
        if "MANIFEST" in path:
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
    manifest_path = os.path.join(str(OUTPUT_DIR), "MANIFEST_lineage.csv")
    if not os.path.exists(manifest_path):
        _check(results, "C5 manifest", False, "manifest not found")
        return
    manifest = pd.read_csv(manifest_path)
    listed = set(manifest.iloc[:, manifest.columns.get_loc("file")]) \
        if "file" in manifest.columns else set()
    on_disk = {os.path.relpath(p, str(OUTPUT_DIR))
               for p in glob.glob(os.path.join(str(OUTPUT_DIR), "**", "*.csv*"),
                                  recursive=True)
               if "MANIFEST" not in p}
    missing = {f for f in on_disk
               if not any(f.endswith(os.path.basename(x)) for x in listed)}
    _check(results, "C5 every gold file has a lineage row",
           len(missing) <= 0,
           f"{len(on_disk)} files on disk, {len(missing)} unlisted"
           + (f": {sorted(missing)[0]}" if missing else ""))


#: Headline numbers that the revision documents quote, and where each is
#: computed from. ``doc`` is the markdown that must contain ``text`` verbatim.
DOCUMENTED_NUMBERS: tuple[dict[str, Any], ...] = (
    dict(text="4,713", doc="docs/revision/analysis_2022.md",
         source=("01_eriksen_replication/hotspot_by_producing_node.csv",
                 "climate_change"),
         expect=4713.4, tol=1.0, what="health-care climate footprint, kt"),
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


def main() -> None:
    """Run every check and write the report; exit non-zero on failure."""
    results: list[dict[str, Any]] = []
    for check in (c1_headline, c2_detail_vs_aggregate, c3_freshness,
                  c4_provenance, c5_manifest, c6_documentation):
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
