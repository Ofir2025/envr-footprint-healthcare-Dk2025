#!/usr/bin/env bash
# Take the full copy's CODE into the paper copy. Code only: gold is rebuilt.
#
# docs/SYNC.md used to give this as `git checkout dk/main -- .`, and that was
# wrong three times over. The paper copy has no `dk` remote, so it could not
# run. `-- .` takes every path the full copy has, so it stages the follow-on
# gold layers, the reference library and the reviewer material, and leaves
# check C10 to fail afterwards and catch the disclosure it had just made. And
# taking `data/gold` at all is wrong in principle: the two copies are entitled
# to different gold, each builds its own from its own scope, and copying one
# copy's results into the other silently replaces a paper-scope build with a
# full-scope one. The first real run of the earlier command pulled in the
# health-function facts, the IMPACT World+ facts, table 9 and the manuscript
# and reviewer documents; none of those belong in the copy that pushes to the
# co-author's public repository.
#
# So this script syncs source and method documentation, and nothing else. Gold
# and figures are regenerated here afterwards, which is also the only way the
# paper copy's numbers stay its own rather than inherited.
#
# Run from the paper copy:  scripts/release/sync_paper_copy.sh [path-to-full-copy]

set -euo pipefail

FULL=${1:-../envhealth_footprint}
REPO=$(git rev-parse --show-toplevel)
cd "$REPO"

#: What a sync moves: code, the run order, the figure scripts, the method
#: documentation, and the dependency declarations. Anything not named here is
#: either generated (data, figures), specific to one copy (.repo_scope,
#: BRANCH_NOTES.md) or private to the full copy (docs/references,
#: docs/ofir_et_al_2026, docs/incidents, docs/feedback, docs/presentation).
#
#: docs/revision and BRANCH_NOTES.md are here because they are PUBLISHED. They
#: ship to the co-author's branch, so leaving them out of the sync let the
#: published revision documents drift from the ones being edited: a comparator
#: corrected here stayed wrong there. The rule is that anything the publish
#: filter carries and a person authors has to be synced, and only generated
#: things are rebuilt instead.
INCLUDE=(src scripts R .githooks docs/methods docs/revision
         BRANCH_NOTES.md README.md requirements.txt pyproject.toml)

[ -f .repo_scope ] || { echo "no .repo_scope here; is this a working copy?" >&2; exit 1; }
SCOPE=$(awk 'NF{print tolower($1); exit}' .repo_scope)
[ "$SCOPE" = "paper" ] || {
  echo "refusing to run: this copy declares scope '$SCOPE'." >&2
  echo "Work flows from the full copy to the paper copy and never back." >&2
  exit 1; }

[ -d "$FULL/.git" ] || { echo "not a git repository: $FULL" >&2; exit 1; }
FULL_SCOPE=$(awk 'NF{print tolower($1); exit}' "$FULL/.repo_scope" 2>/dev/null || echo "?")
[ "$FULL_SCOPE" = "full" ] || {
  echo "refusing to run: $FULL declares scope '$FULL_SCOPE', expected 'full'." >&2
  exit 1; }

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "refusing to run: the working tree has uncommitted changes." >&2
  echo "A sync overwrites files; commit or stash first." >&2
  exit 1
fi

echo "==> fetching main from $FULL"
git fetch --quiet "$FULL" main

# Take the incoming gold_scope BEFORE computing the exclusion list from it.
#
# The list used to be computed from this copy's own gold_scope, which is one
# sync behind. A file newly declared private in the full copy is therefore not
# yet on this copy's list, so the very sync that introduces it also stages it.
# That is exactly what happened when health_function_recipes.py was added: the
# post-sync check caught it, but a check that fires after the mistake is a worse
# design than an order that cannot make it.
git checkout FETCH_HEAD -- src/analysis/gold_scope.py

# The source and method files that travel with a private gold folder.
GOLD_EXCLUDE=$(PYTHONPATH=src python3 -m analysis.gold_scope --exclude)
[ -n "$GOLD_EXCLUDE" ] || { echo "gold_scope listed no private paths" >&2; exit 1; }

#: Held back pending the author's decision rather than withheld on principle.
#: The assessment of the co-author's own submission is a candid critique of his
#: manuscript, and publishing it to his repository is his co-author's call to
#: make deliberately, not something a sync should do as a side effect of
#: widening its include list. Its sibling assessment IS published, so this is a
#: pause, not a policy. Remove the line to publish it.
HELD=(docs/revision/manuscript_assessment_ofir_et_al_2026.md)

EXCLUDE_SPECS=()
for path in $GOLD_EXCLUDE "${HELD[@]}"; do EXCLUDE_SPECS+=(":(exclude)$path"); done

echo "==> taking ${INCLUDE[*]}"
git checkout FETCH_HEAD -- "${INCLUDE[@]}" "${EXCLUDE_SPECS[@]}"

echo "==> checking the result carries only this copy's scope"
PYTHONPATH=src python3 - <<'CHECK'
import sys
from analysis import gold_scope
stray = gold_scope.out_of_profile()
if stray:
    print("SYNC STAGED PRIVATE PATHS, do not commit:", file=sys.stderr)
    for path in stray:
        print(f"  {path}", file=sys.stderr)
    sys.exit(1)
print(f"  profile {gold_scope.profile()!r}, nothing out of place")
CHECK

cat <<'NOTE'

Code taken. Gold and figures were NOT copied: rebuild them here so this copy's
results are its own.

    python scripts/run_pipeline.py
    Rscript R/plot_manuscript_figures.R      # and the other figure scripts

Then review `git status` and commit. Nothing was committed by this script.
NOTE
