# wp3 audit — deep research reference

VERDICT: NEAR-PASS

Scope: the six changed paths match the plan exactly (README.md, docs/index.html,
scripts/validate_public_surface.py, search/SKILL.md, deep-research/SKILL.md,
search/references/deep-research.md). Untracked .codexclaw/ is loop state, not a source change.

Commands: python3 scripts/validate_public_surface.py -> "validated 226 skills", exit 0.
git diff --check clean, exit 0. wc -l: search/SKILL.md 483, deep-research/SKILL.md 139,
search/references/deep-research.md 112 — all under 500. pytest NOT RUN (no pytest module
in /opt/homebrew/opt/python@3.14).

Count integrity: ls -d */references */reference | wc -l = 48, and search/references is new,
so the validator change is a real recount, not a moved goalpost. Three of four places agree.

## BLOCKERS

1. docs/index.html:115 — the hero metric still reads 47 "with references" while
   docs/index.html:137 says "48 skills". The published page contradicts itself. The validator
   greps docs only for "canonical", "og:image", "twitter:card", "226"
   (scripts/validate_public_surface.py:37), so CI stays green on a false public surface —
   exactly the failure mode the plan's README/docs section was written to prevent. Fix the
   hero metric, and ideally add "48 skills" to the docs needle list so the two cannot drift.

## NITS

1. search/references/deep-research.md:76-83 — the lane table restates the tier-to-use mapping
   that search/SKILL.md:141-144 owns. It carries no gates, order or evidence status, so it does
   not breach the standalone-owner rule at search/SKILL.md:24-26, but it is the one spot that
   will drift if tier roles change.
2. search/references/deep-research.md:12 — "An ordinary latest/current lookup stays on Tier 1/2
   however important it is" hard-codes tier numbers in a non-escalation rule.
3. search/references/deep-research.md:27, :101 and deep-research/SKILL.md:12 — the path form
   `dev` `references/reader-documents.md` is two adjacent code spans, not a resolvable path.
   The plan specified ../../dev/references/reader-documents.md; a reader agent must guess the join.

## Checks that passed

The reference does not restate tier policy, gates, the browser ladder or the evidence-status
definitions: it defers status to search (deep-research.md:50-51) and defers the parallel-research
cap to search (:85-88), matching search/SKILL.md:40-57. Its only addition there — each lane
returns provenance records, never a report draft — does not contradict the 2-4 lane cap, the
candidate-space discipline, or Rules 1-7. New Rule 5 text (search/SKILL.md:462-463) tightens
effort matching without loosening a gate. Ownership against deep-research/SKILL.md is coherent:
the marker sits under the H1, frontmatter license Apache-2.0 and author sanjay3290 are untouched,
and the "Local addition (cli-jaw-skills)" label keeps vendored provenance legible. Budgets, stop
rules (three no-lead waves or five waves, record which fired) and the six gap-matrix columns are
concrete and executable.

## Fold (main, 2026-09-08)

Blocker 1 (docs hero metric still said 47 while the same page said 48) folded: the metric
now reads 48, "48 skills" is in the docs needle list, and — going further than the audit
asked — the validator now *measures* the reference-folder count and fails when README or
docs do not report it. The literal-string grep is what let this drift in the first place.
Nits 1-2: the lane table and hard-coded tier names now defer to `search/SKILL.md` as the
owner instead of restating it. Nit 3: cross-referenced paths are single code spans.
pytest NOT RUN locally (absent from Python 3.14 here); CI is authoritative.

## Forward-use trial

A fresh Opus-5 agent followed the protocol end to end: plan.md, journal.md, ledger.md,
gap-matrix.md and report-source.md under evidence/wp3-forward/. It opened 14 sources via
curl against api.github.com and raw.githubusercontent.com, named the stop rule that fired
(open cap, 14 against a budget of 10), left the questions it could not settle marked
`insufficient` rather than guessing when web_search hit its usage limit, and flagged a
deviation instead of silently switching lanes when it found cli-jaw and progrok on PATH.
The report opens with the answer and keeps its ledger and matrix as linked artifacts.
PASS for criterion c-3's trial bullet.
