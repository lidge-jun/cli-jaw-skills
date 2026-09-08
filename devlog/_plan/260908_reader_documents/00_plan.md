# Reader documents and deep research for cli-jaw skills — roadmap

Loop-spec: satisfy-spec; trigger: the user's 2026-09-08 request to reflect the CodexClaw
0.2.24 guidance in the cli-jaw skill library. Goal: a cli-jaw agent asked for a report,
devlog entry or phase summary writes the answer first with evidence in an appendix, and a
딥리서치 request follows a defined loop instead of an undefined tier hop. Non-goals: the
cli-jaw runtime repo, codexclaw (already shipped), new skill folders, unrelated skills,
and the pre-existing uncommitted edits in the main checkout. Verifier: repo's own
`scripts/validate_public_surface.py`, `pytest tests/`, whitespace check, plus independent
audits and forward-use trials. Stop: all four goalplan criteria met and the PR merges.
Memory artifact: this unit under `devlog/_plan/260908_reader_documents/`. Outcomes:
DONE with observed proof; capability gaps reported as limitations. Escalation: main
reclaims a slice after two distinct leaf failures. Resource bounds: no user cap;
Opus-5 subagents unlimited; PR and merge authorized by the user in this session.

## The problem in this repo

cli-jaw skills already carry the discipline for *finding* things — the search hub's
four tiers, evidence statuses, and the "search finds, browser proves" split are strong.
What is missing is the shape of what the agent writes afterward. `dev-pabcd` D says
"summarize the entire flow: what was planned, audited, built, checked, list of files
changed", which produces a chronology of the agent's own process. `dev-scaffolding`
defines devlog numbering but not what goes in the narrative versus the evidence.
`diagram` covers rendering and security thoroughly but says nothing about report
structure. `doc-coauthoring` has a reader-testing stage (Stage 3) but no answer-first
rule, and it is a conversational co-writing flow rather than a structure owner.

On research: `search/SKILL.md` lists `deep research`/`딥리서치` as triggers and routes
them to "Tier 3 (xhigh) or Tier 4", but there is no loop — no scope step, no query
families, no gap matrix, no claim ledger, no report template, no stop rule. Separately,
`deep-research/` is a vendored Gemini Deep Research Agent skill (Apache-2.0,
author sanjay3290) with its own report format and MCP notes. Two skills claim the same
words with no ownership boundary.

## Hard constraints discovered (2026-09-08)

These bound every later phase and were verified by running the repo's own checks:

- `scripts/validate_public_surface.py` requires **exactly 226** `*/SKILL.md` files.
  No new skill folder may be created. New material must live under an existing skill's
  `references/` directory.
- The same script fails any `SKILL.md` over **500 lines** outside the four Office
  skills. `dev/SKILL.md` is **504 lines on main today**, so the validator already
  exits 1 before any change of mine. wp2 must not grow it, and should trim it back
  under the limit if that can be done without losing content.
- `search/SKILL.md` is 472 lines: a large in-file section would breach 500, so the
  deep-research protocol belongs in `search/references/`.
- CI also runs `pytest tests/test_dev_frontend_refresh.py`, four `docs/index.html`
  marker greps, and `git diff --check` (whitespace).
- The main checkout `/Users/jun/Developer/new/700_projects/cli-jaw-skills` has 24
  uncommitted files (dev-frontend, dev-uiux-design, dev, dev-pabcd). All work happens in
  the linked worktree `cli-jaw-skills-readerdocs` on `codex/reader-documents` so those
  stay untouched.

## Conventions to follow

- Frontmatter is `name` + `description` with triggers inline; `search` adds a
  `metadata` JSON block with `triggers` and `requires`. Keep each skill's existing shape.
- `dev/SKILL.md` owns the Skill Ownership Map: one canonical owner per rule area, stubs
  elsewhere, "MUST NOT duplicate canonical content".
- `search` declares itself a **standalone owner**: other skills point at it and must not
  copy its tier policy. The deep-research reference must sit under `search`, not be
  restated in callers.
- Reference tables use the "| File | When to Read | What It Covers |" shape
  (`dev-scaffolding`) or a modular list (`dev-backend`).

## Work-phase map

| wp | Delivers | Verifiable close |
|---|---|---|
| wp1 | this roadmap + 010/020/030 diff-level docs | independent audit PASS |
| wp2 | `dev/references/reader-documents.md` + ownership row + stubs in dev-pabcd, dev-scaffolding, diagram, doc-coauthoring | validator, forward-use trial |
| wp3 | `search/references/deep-research.md` + search routing + ownership boundary against the Gemini skill | validator, forward-use trial |
| wp4 | full repo checks, PR to main, merge | CI green, merged |

Detailed change maps: [10_reader_documents.md](10_reader_documents.md),
[20_deep_research.md](20_deep_research.md), [30_delivery.md](30_delivery.md).

