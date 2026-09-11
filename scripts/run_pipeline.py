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
``python scripts/run_pipeline.py --from gwp_revision``  resume from a stage
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
#: The interpreter to run stages with. A working copy without its own virtual
#: environment falls back to the interpreter running this script, and
#: ``check_interpreter`` then tests that the fallback can actually carry the
#: pipeline. It could not in this copy: the system interpreter has no
#: ``pyarrow``, so every parquet fact the star schema writes would have failed
#: at the last stage, after forty minutes of work. A silent fallback to an
#: interpreter missing a dependency is worse than no fallback.
_LOCAL_VENV = REPO / ".venv" / "bin" / "python"
PY = _LOCAL_VENV if _LOCAL_VENV.exists() else Path(sys.executable)

#: Third-party modules a stage may import, and what depends on each. Checked
#: once before the first stage runs rather than discovered stage by stage.
REQUIRED: dict[str, str] = {
    "numpy": "every module",
    "pandas": "every module",
    "scipy": "the Monte Carlo and the .mat readers",
    "pyarrow": "the parquet facts of the star schema",
    "openpyxl": "the Danish input-output workbooks",
    "matplotlib": "the Python figures",
}


def check_interpreter() -> list[str]:
    """Which required third-party modules the chosen interpreter cannot import.

    Returns
    -------
    list of str
        Module names, empty when the interpreter can carry every stage. The
        test is an import in a subprocess of ``PY`` itself, not of this
        process, because the two are different interpreters whenever a local
        virtual environment exists.
    """
    probe = ("import importlib, sys; "
             "print(' '.join(m for m in sys.argv[1:] "
             "if importlib.util.find_spec(m) is None))")
    out = subprocess.run([str(PY), "-c", probe, *REQUIRED],
                         capture_output=True, text=True, check=False)
    return out.stdout.split()

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
    ("cabernard_target_scope3", "target-perspective scope 3 and its correction"),
    ("double_counting_audit",
     "the ledger that scopes_detail's partition needs; it runs after the "
     "target-set correction because its last row quotes that layer's "
     "published overestimate rather than a literal"),
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
    ("build_dst_concordance",
     "the EXIOBASE-to-Denmark industry bridge and its output validation; the "
     "national table it validates against is read here, so it follows the "
     "modules that establish the model's own totals"),

    # --- replications of the comparator studies ---------------------------
    ("malik_replication", "Malik's boundary, on Danish data"),
    ("production_layers", "the layer decomposition Malik reports"),
    ("lenzen_replication", "Lenzen's KPI set"),
    ("steenmeijer_replication", "the Dutch study this replicates"),
    ("eckelman_replication", "the US comparator"),

    # --- diagnostics and sensitivities ------------------------------------
    ("release_defect_audit", "why v3.10.2 was rejected"),
    ("capital_gfcf", "the capital scenarios"),
    ("capital_endogenised_sodersten",
     "capital on the published matrices; reads capital_gfcf's baseline"),
    ("impact_categories_full", "all 97 characterised categories"),
    ("impact_world_plus", "IMPACT World+ characterisation"),
    ("gwp_revision",
     "the climate revision restatement; reads the raw stressor masses, so it "
     "must follow the modules that write them"),
    ("health_subsector_footprints", "the SHA function decomposition"),
    ("health_function_recipes",
     "reads that decomposition, so it runs after it: gives each service "
     "function its own input recipe from the Danish table"),

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
    # a bronze-to-silver conformance step: it gives the medstat register named
    # columns and is run when the register is refreshed, not on every build
    "build_atc_sales",
    # the other bronze-to-silver conformance step: it labels the FIGARO code
    # columns from Eurostat's own codelists. Its product is tracked, so every
    # clone has it before figaro_benchmarks imports it; it is re-run when a
    # FIGARO extract is added or the codelists are refreshed, not on every build
    "build_figaro_dimensions",
    "__init__", "constants", "functions", "functions_2025", "extra_functions",
    "main",                    # the RIVM original, kept for provenance
    "scenario_engine",         # library behind mitigation_scenarios
    "detail_tables",           # listed above; kept here for the set difference
    # the silver stage that reads the Danish IO workbook, the supply-use
    # workbook and the EXIOBASE classification on dk_shipping_correction's
    # behalf; run before it, and rebuilt when a bronze source changes
    "build_shipping_inputs",
    "dk_shipping_correction",  # a silver-layer step, run before this pipeline
    # the other silver-layer background stage: it endogenises consumption of
    # fixed capital into a background pickle (variant d), writes no gold, and
    # like dk_shipping_correction must run before the pipeline that reads it
    "capital_endogenised_background",
    "audit_consistency", "build_manifest", "build_folder_metadata",
    "gold_scope", "bibliography", "build_star_schema", "build_tables_record",
    "uncertainty_audit",
})


#: Modules allowed to name a data path relative to the repository root. Only
#: ``gold_scope`` qualifies: it reports repository-relative paths as *text*, for
#: a human and for git, and never opens them.
RELATIVE_PATH_EXEMPT: frozenset[str] = frozenset({"gold_scope"})


def relative_data_paths() -> list[str]:
    """Modules that build a data path relative to the working directory.

    Every data path must resolve through :mod:`paths`, because bronze and
    silver can be pointed elsewhere so two working copies share one physical
    copy of them, and because a relative literal breaks as soon as the caller
    is not standing in the repository root. Two such literals survived until a
    run from the second working copy found them, one at a time; this makes the
    class visible instead.

    Returns
    -------
    list of str
        ``module:line`` for each offending literal.
    """
    hits: list[str] = []
    for path in sorted((SRC / "analysis").glob("*.py")):
        if path.stem in RELATIVE_PATH_EXEMPT:
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            for quote in ('"data/', "'data/", '"./data/', 'f"data/'):
                if quote in line:
                    hits.append(f"{path.stem}:{n}")
                    break
    return hits


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


def available(module: str) -> bool:
    """Whether a stage's module is in this working copy.

    Two stages read layers classified private in :mod:`analysis.gold_scope`,
    and their modules travel with those layers, so a paper-scope copy does not
    have them. The pipeline skips them rather than failing: one run order has
    to serve both copies, and a missing private module is a scope difference
    rather than a broken build.

    Parameters
    ----------
    module : str
        Module name under ``analysis``.

    Returns
    -------
    bool
        True when the module file exists.
    """
    return (SRC / "analysis" / f"{module}.py").exists()


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
        loose = relative_data_paths()
        print(f"\n{len(STAGES)} stages, {len(NOT_STAGES)} modules excused, "
              f"{len(missing)} unlisted, {len(loose)} relative data path(s)")
        for m in missing:
            print(f"  UNLISTED  {m}")
        for m in loose:
            print(f"  RELATIVE PATH  {m}  (resolve it through paths.py)")
        absent = check_interpreter()
        print(f"  interpreter {PY}")
        for m in absent:
            print(f"  MISSING DEPENDENCY  {m}  ({REQUIRED[m]})")
        return 1 if (missing or loose or absent) else 0
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

    absent = check_interpreter()
    if absent:
        print(f"refusing to run: {PY} cannot import "
              f"{', '.join(absent)}.\n"
              f"  needed by: "
              f"{'; '.join(f'{m} for {REQUIRED[m]}' for m in absent)}\n"
              f"  fix: python3 -m venv {REPO / '.venv'} && "
              f"{REPO / '.venv' / 'bin' / 'python'} -m pip install -r "
              f"{REPO / 'requirements.txt'}", file=sys.stderr)
        return 1

    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    env.setdefault("HC_ANALYSIS_YEAR", "2022")
    env.setdefault("HC_BACKGROUND_TAG", "_snacship")

    print(f"pipeline: {len(stages)} stages, year {env['HC_ANALYSIS_YEAR']}, "
          f"background tag {env['HC_BACKGROUND_TAG']!r}\n")
    total = 0.0
    for i, (name, _why) in enumerate(stages, 1):
        if not available(name):
            print(f"  [{i:2d}/{len(stages)}] skip {name:34s} "
                  f"not in this working copy")
            continue
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
