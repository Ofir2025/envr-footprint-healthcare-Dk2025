# -*- coding: utf-8 -*-
"""Run every analysis module in dependency order, and report what happened.

The README carried a hand-written list of modules to run. It had fallen eleven
modules behind the code, which is the ordinary fate of a run order kept in
prose: nothing fails when it goes stale, so nothing corrects it. A stale run
order is a reproducibility defect, because a reader following it does not
rebuild what the repository actually contains.

This module is the run order. It is executable, so it cannot silently drift
from what the pipeline is, and it is declared in one list with the reason each
stage sits where it does. ``--check`` compares the list against the modules on
disk and fails if any module is unlisted, which is the same discipline the gold
folders are held to by ``analysis.gold_scope``.

Stages run in order and a failure stops the run, because everything downstream
of a failed stage would otherwise be written from stale inputs.

Run
---
``python scripts/run_pipeline.py``                 run every stage
``python scripts/run_pipeline.py --check``         list coverage only, run nothing
``python scripts/run_pipeline.py --from gwp_vintage``  resume from a stage
``python scripts/run_pipeline.py --only uncertainty_2025 uncertainty_figures``
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
PY = REPO / ".venv" / "bin" / "python"

#: (module, why it sits here). Order is dependency order: every module reads
#: only what an earlier one has already written.
STAGES: tuple[tuple[str, str], ...] = (
    # --- the model itself -------------------------------------------------
    ("main_2025",
     "the replication: expenditure vector, background, bottom-up items, and "
     "the contribution and hotspot tables every later layer reads"),
    ("export_tables",
     "the core footprint tables, written from the objects main_2025 leaves"),
    ("extended_indicators",
     "the four non-climate categories on the same bilateral table"),
    ("national_totals",
     "the Danish national footprint, the denominator for every share"),
    ("validate_io_identities",
     "the six input-output identities; run early so a broken table stops the "
     "run before anything is derived from it"),

    # --- accounting layers ------------------------------------------------
    ("scopes_detail", "the GHG Protocol partition"),
    ("double_counting_audit", "the ledger that scopes_detail's partition needs"),
    ("cabernard_target_scope3", "target-perspective scope 3 and its correction"),
    ("waste_validation", "the waste accounts against Eurostat and DST"),
    ("waste_domestic_dst", "the domestic waste figure from AFFALD01"),

    # --- benchmarks and validation ---------------------------------------
    ("demand_vector_consistency",
     "the expenditure vector against the national accounts"),
    ("figaro_recipe_validation", "FIGARO as an independent recipe"),
    ("recipe_validation_2022", "the three-way recipe comparison"),
    ("figaro_benchmarks", "FIGARO as an independent denominator"),
    ("danish_healthcare_benchmark",
     "the boundary-matched ladder to Schmidt and Merciai"),

    # --- replications of the comparator studies ---------------------------
    ("malik_replication", "Malik's boundary, on Danish data"),
    ("production_layers", "the layer decomposition Malik reports"),
    ("lenzen_replication", "Lenzen's KPI set"),
    ("steenmeijer_replication", "the Dutch study this replicates"),
    ("eckelman_replication", "the US comparator"),

    # --- diagnostics and sensitivities ------------------------------------
    ("vintage_defect_audit", "why v3.10.2 was rejected"),
    ("capital_gfcf", "the capital scenarios"),
    ("capital_endogenised_sodersten",
     "capital on the published matrices; reads capital_gfcf's baseline"),
    ("impact_categories_full", "all 97 characterised categories"),
    ("impact_world_plus", "IMPACT World+ characterisation"),
    ("gwp_vintage",
     "the climate vintage restatement; reads the raw stressor masses, so it "
     "must follow the modules that write them"),
    ("health_subsector_footprints", "the SHA function decomposition"),

    # --- counterfactuals ---------------------------------------------------
    ("mitigation_scenarios",
     "the scenario layer; solves a second Leontief system per scenario"),

    # --- uncertainty -------------------------------------------------------
    ("uncertainty_2025",
     "the Monte Carlo; its deterministic base is the footprint above, so it "
     "runs after every module that can move it"),
    ("uncertainty_figures", "the uncertainty figure inputs"),
    ("uncertainty_audit", "the nineteen numerical checks on the Monte Carlo"),

    # --- reporting tables --------------------------------------------------
    ("detail_tables", "the detail tables behind each aggregate"),
    ("eriksen_tables", "the replication outputs as FAIR long-format CSVs"),
    ("manuscript_figure_tables", "the tables the manuscript figures read"),
    ("scope_figure_tables", "the tables the scope figures read"),
    ("year_comparison", "the 2019 against 2022 bridge"),

    # --- the semantic layer and the registers ------------------------------
    ("build_star_schema", "the star schema over the reported facts"),
    ("build_tables_record", "the tables of record, read from the gold facts"),
    ("build_folder_metadata", "a README per gold folder"),
    ("build_manifest", "the lineage row for every gold file"),
    ("gold_scope", "the paper/private classification and the gold README"),
    ("bibliography", "the reference list and the in-text citation check"),

    # --- the gate ----------------------------------------------------------
    ("audit_consistency",
     "every consistency check; exits non-zero, so it gates a release"),
)

#: Modules that are libraries, entry points for a different job, or run by
#: another stage rather than on their own. Listing them here is what lets
#: ``--check`` insist that everything else appears in STAGES.
NOT_STAGES: frozenset[str] = frozenset({
    # a bronze-layer fetcher: it downloads register data from Statistics
    # Denmark and is run when the accounts are refreshed, not on every build
    "fetch_dst_accounts",
    "__init__", "constants", "functions", "functions_2025", "extra_functions",
    "main",                    # the RIVM original, kept for provenance
    "scenario_engine",         # library behind mitigation_scenarios
    "detail_tables",           # listed above; kept here for the set difference
    "dk_shipping_correction",  # a silver-layer step, run before this pipeline
    "audit_consistency", "build_manifest", "build_folder_metadata",
    "gold_scope", "bibliography", "build_star_schema", "build_tables_record",
    "uncertainty_audit",
})


def modules_on_disk() -> set[str]:
    """Analysis modules present in ``src/analysis``.

    Returns
    -------
    set of str
        Module names without the ``.py`` suffix.
    """
    return {p.stem for p in (SRC / "analysis").glob("*.py")}


def unlisted() -> list[str]:
    """Modules on disk that neither run as a stage nor are excused.

    Returns
    -------
    list of str
        Sorted module names with no entry in :data:`STAGES` or
        :data:`NOT_STAGES`.
    """
    listed = {name for name, _ in STAGES} | NOT_STAGES
    return sorted(modules_on_disk() - listed)


def run(module: str, env: dict[str, str]) -> tuple[bool, float, str]:
    """Run one analysis module as a subprocess.

    Parameters
    ----------
    module : str
        Module name under ``analysis``.
    env : dict of str
        Environment for the subprocess.

    Returns
    -------
    tuple of (bool, float, str)
        Whether it succeeded, how long it took in seconds, and the last lines
        of its output if it failed.
    """
    started = time.time()
    proc = subprocess.run([str(PY), "-m", f"analysis.{module}"],
                          cwd=str(REPO), env=env,
                          capture_output=True, text=True)
    elapsed = time.time() - started
    if proc.returncode == 0:
        return True, elapsed, ""
    tail = (proc.stdout + proc.stderr).strip().splitlines()[-12:]
    return False, elapsed, "\n".join("      " + line for line in tail)


def main() -> int:
    """Run the pipeline, or report its coverage.

    Returns
    -------
    int
        Zero on success. One if a stage failed or a module is unlisted.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report coverage against the modules on disk, run nothing")
    ap.add_argument("--from", dest="start", metavar="STAGE",
                    help="resume from this stage")
    ap.add_argument("--only", nargs="+", metavar="STAGE",
                    help="run only these stages, in the order given")
    args = ap.parse_args()

    missing = unlisted()
    if args.check:
        for name, why in STAGES:
            print(f"  {name:34s} {why[:74]}")
        print(f"\n{len(STAGES)} stages, {len(NOT_STAGES)} modules excused, "
              f"{len(missing)} unlisted")
        for m in missing:
            print(f"  UNLISTED  {m}")
        return 1 if missing else 0
    if missing:
        print(f"refusing to run: {len(missing)} module(s) neither staged nor "
              f"excused: {', '.join(missing)}", file=sys.stderr)
        return 1

    stages = list(STAGES)
    if args.only:
        by_name = dict(STAGES)
        stages = [(s, by_name.get(s, "requested")) for s in args.only]
    elif args.start:
        names = [n for n, _ in STAGES]
        if args.start not in names:
            print(f"no such stage: {args.start}", file=sys.stderr)
            return 1
        stages = stages[names.index(args.start):]

    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    env.setdefault("HC_ANALYSIS_YEAR", "2022")
    env.setdefault("HC_BACKGROUND_TAG", "_snacship")

    print(f"pipeline: {len(stages)} stages, year {env['HC_ANALYSIS_YEAR']}, "
          f"background tag {env['HC_BACKGROUND_TAG']!r}\n")
    total = 0.0
    for i, (name, _why) in enumerate(stages, 1):
        ok, elapsed, tail = run(name, env)
        total += elapsed
        mark = "ok  " if ok else "FAIL"
        print(f"  [{i:2d}/{len(stages)}] {mark} {name:34s} {elapsed:7.1f}s")
        if not ok:
            print(tail)
            print(f"\nstopped at {name} after {total:.0f}s; nothing downstream "
                  f"was run, because it would read stale inputs.", file=sys.stderr)
            return 1
    print(f"\n{len(stages)} stages in {total / 60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
