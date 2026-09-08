#!/usr/bin/env bash
# Build and push the curated public branch for Ofir's repository.
#
# The local `2019-update` branch is the FULL working branch: it carries the raw
# third-party inputs, the follow-on analysis layers, the presentation and the
# unredacted reviewer response. The public branch is a filtered view of it.
#
# The filter must live here, not in someone's shell history. Pushing
# `2019-update` directly would publish:
#   * data/bronze  - third-party data obtained under providers' own terms
#   * docs/references, reports/source - PDFs of published articles
#   * docs/feedback - internal notes
#   * docs/revision/response_to_reviewers.md - verbatim referee comments,
#     which are confidential while the manuscript is under review
#   * layers 16 and 17 - follow-on work for the next paper
#
# Usage:  scripts/release/publish_ofir_branch.sh [--dry-run]
set -euo pipefail

SRC_BRANCH="2019-update"
PUB_BRANCH="ofir-revision"
REMOTE_BRANCH="2019-update"
REMOTE="origin"
REDACTED="${REDACTED_RESPONSE:-/tmp/redact/rtr_public.md}"
DRY_RUN="${1:-}"

# Which gold layers ship.
#
# Only 16 and 17 are withheld: IMPACT World+ and the health sub-sector
# decomposition are follow-on work for the next paper, and neither is cited by
# anything in the revision.
#
# Layers 07, 08, 09, 14 and 15 were considered for exclusion and are KEPT,
# because the reviewer response asserts things that only they evidence. Ship the
# response without them and a co-author is left defending claims with no table
# behind them on the branch he has:
#
#   07 malik      capital treatment: Malik et al. include capital where the
#                 other comparators exclude it (R2-3 boundary discussion)
#   08 lenzen     the comparator behind the uncertainty calibration and the
#                 national-total family comparison
#   09 vintage    the ONLY evidence for rejecting EXIOBASE v3.10.2, which the
#                 response states as fact
#   14 eckelman   comparator in the same boundary table as 07 and 08
#   15 gwp        the AR6-versus-AR4 restatement the response leads on
#
# Each is also referenced by 6-12 files in docs/ and src/, so removing them
# would leave dangling paths throughout the shipped documentation.
EXCLUDE=(
  data/bronze/exiobase_v3_7 data/bronze/medstat data/bronze/capital data/bronze/figaro
  docs/references reports/source docs/presentation docs/feedback
  data/gold/results/16_impact_world_plus data/gold/results/17_health_subsectors
  docs/methods/replications/16_impact_world_plus.md
  docs/methods/replications/17_health_subsectors.md
  src/analysis/impact_world_plus.py src/analysis/health_subsector_footprints.py
)

if [ -n "$(git status --porcelain)" ]; then
  echo "==> refusing to publish: the working tree is not clean." >&2
  echo "    git filter-branch cannot rewrite a branch with uncommitted changes." >&2
  git status --short | head -10 >&2
  exit 1
fi

echo "==> redacting the reviewer response"
mkdir -p "$(dirname "$REDACTED")"
python3 - "$REDACTED" <<'PY'
import re, sys
src = "docs/revision/response_to_reviewers.md"
text = open(src, encoding="utf-8").read()
placeholder = ("> *[Referee comment withheld - the referee reports for a manuscript under\n"
               "> review are confidential. The full text is in the submission system and in\n"
               "> the private working copy. The heading above states the point addressed.]*\n")
out, n = re.subn(r"(?:^> .*(?:\n|$))+", lambda m: placeholder, text, flags=re.MULTILINE)
open(sys.argv[1], "w", encoding="utf-8").write(out)
print(f"    {n} referee blockquote(s) withheld")
PY

echo "==> rebuilding $PUB_BRANCH from $SRC_BRANCH"
git branch -f "$PUB_BRANCH" "$SRC_BRANCH"
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --prune-empty --index-filter "
  git rm -r -q --cached --ignore-unmatch ${EXCLUDE[*]}
  if git ls-files --cached --error-unmatch docs/revision/response_to_reviewers.md >/dev/null 2>&1; then
    H=\$(git hash-object -w '$REDACTED')
    git update-index --cacheinfo 100644 \"\$H\" docs/revision/response_to_reviewers.md
  fi
" "$REMOTE/main..$PUB_BRANCH" >/dev/null 2>&1

echo "==> verifying"
fail=0
check () { # name  expected  actual
  if [ "$2" = "$3" ]; then printf "    ok   %-42s %s\n" "$1" "$3"
  else printf "    FAIL %-42s expected %s, got %s\n" "$1" "$2" "$3"; fail=1; fi
}
tree () { git ls-tree -r "$PUB_BRANCH" --name-only; }
check "excluded paths present"      0 "$(tree | grep -cE '^(data/bronze/(exiobase_v3_7|medstat|capital|figaro)|docs/references|reports/source|docs/presentation|docs/feedback)' || true)"
check "follow-on layers present"    0 "$(tree | grep -cE '16_impact_world_plus|17_health_subsectors' || true)"
check "verbatim referee text"       0 "$(git show "$PUB_BRANCH:docs/revision/response_to_reviewers.md" | grep -c 'absence of formal uncertainty' || true)"
# The check above guards one file. Referee wording has reached other documents
# before - a methods note quoting the review in its opening paragraph - so scan
# the WHOLE published tree for the reports' distinctive phrases. Add a phrase
# here whenever a new one is quoted anywhere in the working branch.
REFEREE_PHRASES='absence of formal uncertainty|systematic sensitivity analysis or Monte Carlo|which assumptions contribute most to the uncertainty|distinguish between identifying hotspots|plausible ranges \(e\.g\.'
leaked=0
for f in $(tree | grep -E '\.(md|txt|tex)$' | grep -v '^docs/revision/response_to_reviewers\.md$'); do
  n=$(git show "$PUB_BRANCH:$f" 2>/dev/null | grep -cE "$REFEREE_PHRASES" || true)
  if [ "$n" -gt 0 ]; then echo "         referee wording in $f"; leaked=$((leaked + n)); fi
done
check "referee wording, whole tree" 0 "$leaked"
check "Claude attribution trailers" 0 "$(git log "$REMOTE/main..$PUB_BRANCH" --grep='Co-Authored-By' -i --format=%H | wc -l | tr -d ' ')"
[ "$fail" -eq 0 ] || { echo "==> verification FAILED - nothing pushed"; exit 1; }

echo "==> $(tree | wc -l | tr -d ' ') files, $(git rev-list --count "$REMOTE/main..$PUB_BRANCH") commits"
if [ "$DRY_RUN" = "--dry-run" ]; then
  echo "==> dry run, not pushing"; exit 0
fi
git push --force-with-lease "$REMOTE" "$PUB_BRANCH:$REMOTE_BRANCH"
echo "==> pushed $PUB_BRANCH -> $REMOTE/$REMOTE_BRANCH"
