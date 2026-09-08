# wp2 audit — reader-document structure

VERDICT: NEAR-PASS

Scope: uncommitted diff on codex/reader-documents, plus new dev/references/reader-documents.md (121 lines) and dev/references/static-analysis.md (20 lines), against devlog/_plan/260908_reader_documents/10_reader_documents.md.

Evidence. wc -l dev/SKILL.md = 496 (was 504). python3 scripts/validate_public_surface.py prints "validated 226 skills; known long Office skills are tracked". All five touched SKILL.md files sit under the 500 cap (496/310/264/347/144). ls */SKILL.md | wc -l = 226; README.md and docs/index.html are untouched, so the four docs greps and the 226/47/28/2 count greps still pass. Comparing git show HEAD:dev/SKILL.md section 7.2: only the "Common Rule <-> Prose Mapping" heading, its seven-row table and the "not exhaustive" sentence moved out; the toolchain gate table, thresholds and 7.3 escape hatches are byte-identical. No RULE text lost. Frontmatter untouched in all five files; cross-references use the repo's skill-name form with no ../ paths; the dev-scaffolding table row matches its api-docs and monorepo neighbors.

Ownership. Reader testing has exactly one owner: reader-documents.md:82-84 cedes co-authored reader testing to doc-coauthoring Stage 3 and keeps only the three-question floor, and doc-coauthoring/SKILL.md:65-67 points back while re-asserting Stage 3 as canonical. No cycle, no duplicated procedure. reader-documents.md:65-67 cedes evidence status to search; :114 cedes rendering to diagram. No contradiction found.

Newcomer usability. Rules are concrete and actionable: a one-line reader contract, a five-type table, the SCQA opening, anchor discipline, the three-question check. Both fenced skeletons are valid Markdown and copy-paste sized. The Korean at :39-40 is correct and natural — 두괄식 for reports, 기승전결 explicitly excluded as a narrative shape.

## BLOCKERS

1. dev/references/reader-documents.md:121 and dev/references/static-analysis.md:20 — both end with a blank line at EOF. With git add -N, git diff --check reports "new blank line at EOF" for both and exits 2. The plan's acceptance requires a clean git diff --check, and CI runs that step. Strip the trailing blank line before committing.
2. .codexclaw/ — 11 untracked files (sessions, ledger, attest JSON) are not gitignored and would be swept in by git add -A. Outside the plan; ignore or exclude them.

## NITS

1. search/references/deep-research.md is present and untracked — wp3 work, outside wp2 scope. It also raises the reference-folder count to 48 while README.md:30 and docs/index.html:137 still say 47. The validator only greps the literal "47 skills", so CI stays green, but the published number becomes wrong.
2. dev-pabcd/SKILL.md:182-184 — the new fresh-reader step is numbered 0. ahead of the existing 1-4 list and ends with no period. Renumber or make it a lead-in sentence.
3. dev-pabcd/SKILL.md:196-200 — the plan said to replace the "Summarize the entire flow:" framing; that line survives above the new paragraph, and the file gained 5 lines against the planned 3. Harmless, slightly redundant.
4. dev-scaffolding/SKILL.md:72-75 and diagram/SKILL.md:121-123 compress READER-DOC-04's substance rather than only pointing at it. Within what the plan authorized, but it is the closest thing here to canonical duplication.

Not run: python3 -m pytest tests/test_dev_frontend_refresh.py — pytest is not installed in this environment (NOT RUN). That test reads only dev-frontend/, which this diff does not touch.

## Fold (main, 2026-09-08)

Blocker 1: trailing blank lines stripped from reader-documents.md, static-analysis.md and
deep-research.md; `git add -N` + `git diff --check` now clean. Blocker 2: `.codexclaw/`
is never staged — wp2 and later commits name their files explicitly instead of `git add -A`.
Nit 1 is wp3's own change map (README/docs 47 -> 48) and lands with that phase. Nit 2: the
C step renumbered to 4 with a closing period. Nit 3: the duplicate "Summarize the entire
flow:" lead-in removed. Nit 4: dev-scaffolding and diagram stubs cut back to pointers.
pytest NOT RUN locally (not installed; the CI run is authoritative and the diff does not
touch dev-frontend/).

## Forward-use trial

A fresh Opus-5 agent was handed the raw session notes and the new reference and produced
evidence/wp2-forward/status-report.md: claim-shaped title, reader contract on line 3,
SCQA opening, claim headings, 16 notes moved to anchors A1-A16, three items labelled as
assumptions. It independently flagged the "47" count risk that the plan had already
folded. A second agent with no context ran the READER-DOC-05 check
(evidence/wp2-forward/fresh-reader.md): it answered all three questions and found one
structural stumble — the CI section states a contradiction before resolving it and its
heading over-claims. That is a defect in the trial artifact, not in the reference, and it
is exactly what the rule is meant to surface. PASS for criterion c-2's trial bullet.
