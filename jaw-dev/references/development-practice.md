# Development practice

## 0.5 Repository Convention Discovery

Before broad changes, inspect existing conventions: source layout (`src/`, `app/`,
`packages/`), source-of-truth docs (`structure/`, `docs/`, `adr/`, `devlog/`, `plans/`),
agent context files (`AGENTS.md`, `CLAUDE.md`, tool instruction files), JS/TS setup
(`package.json`, `tsconfig*`, linter config, sibling extensions), and naming/test/
phase-document patterns (see `jaw-dev-pabcd`).

MUST follow existing conventions when they are clear.
MUST read existing `structure/`, `devlog/`, or other source-of-truth logs before broad implementation.
MUST NOT create `structure/`, `devlog/`, `AGENTS.md`, docs folders, or new tooling silently in an existing repo.
If the repo is immature/undocumented, propose a lightweight source-of-truth structure and ask before creating it.

### Broad Change Preview

**Broad change** = creates/reorganizes directories, touches 5+ files, spans multiple
top-level packages, adds a feature/module/service, or adds source-of-truth structure.
Before one, show: detected signals · compact tree (≤40 lines, omit `node_modules`/`dist`/
`build`/`.git`) · planned edits (files to create/modify) · convention decision (reuse vs ask).

---

## 1. Modular Development

Give every file, function, and class a single, clear responsibility.

**Review signals (DEFAULT — exceed with a stated responsibility or risk rationale):**

| Metric              | Threshold   | Action                                   |
| ------------------- | ----------- | ---------------------------------------- |
| File length         | >400 lines  | Split into focused modules (canonical owner: jaw-dev-architecture §1) |
| Function length     | >50 lines   | Extract helper functions                 |
| Class methods       | >20 methods | Split by responsibility                  |
| Nesting depth       | >4 levels   | Flatten with early returns or extraction |
| Function parameters | >5          | Use an options/config object             |
| PR changeset        | >500 lines  | Split into focused PRs                   |

### Blast Radius Limits

One logical change per PR/changeset — unrelated cleanup and drive-by refactors go separately.

| Change Scope | Max Blast Radius | Exceeds → |
|---|---|---|
| Single bug fix | 1–3 files | Split fix from cleanup |
| Feature addition | 1 module/package | Separate infra from feature |
| Refactoring | Pre-approved scope only | Get scope approval first |
| Dependency upgrade | Isolated PR | Never bundle with features |

**Rules:**
- Prefer ESM for new JS/TS code where the repository and runtime support it. Preserve required CommonJS interfaces; migration and bundler optimization are separate changes.
- One default export per file when it has a primary purpose (JS/TS convention; other languages follow their idioms).
- Follow existing naming/directory conventions; check sibling files before creating new ones.
- Where a project uses devlog phase documents, the default is
  `devlog/_plan/YYMMDD_slug/` with decade-range numbering (LEXICO-SPLIT-01;
  see `jaw-dev-pabcd`). A repository that forbids in-tree records uses its
  approved external location. Do not introduce records just for C0/C1.

---

## 1.5 Necessity Gate & Pre-Write Search Obligation

**DEV-NECESSITY-01 (DEFAULT — ponytail discipline, verified 2026-07-02):** before writing
ANY code, check the no-code options in order — do nothing / delete / configure / reuse —
and state which you rejected and why. Frame tasks exclusions-first (what NOT to add)
before the goal. Never lazy about STRICT domains: trust boundaries, data loss, security,
accessibility.

**Rule:** Before creating a new function, helper, type, component, constant, route, fixture, or module, search the codebase for an existing owner or equivalent implementation. No new abstraction may be introduced without search evidence. This section does not apply on the §0.1 fast path (C0/C1 — no new abstractions are being created).

**Structure map first (DEFAULT — DEV-MAP-FIRST-01):** for C2+ work in unfamiliar territory, run `jaw map <dir>` (ranked structure map) before deep Grep dives; then use `rg` and file reads to confirm the narrowed targets. Works on subtrees for large monorepos. Guidance, not enforced.

**Read before editing (DEV-READ-FIRST-01).** Any C2+ edit to existing code reads the target file and its direct caller/consumer when the change crosses a boundary before writing. C0/C1 fast path still applies.

| Artifact being created | Required searches | Preferred outcome |
|---|---|---|
| Function/helper | Exact name, verb phrase, domain noun | Extend existing helper or add next to owner |
| Type/interface/schema | Exact type name and shape fields | Reuse or extend existing contract |
| Component | UI label, route, component name, feature folder | Modify owning component |
| Constant/magic string | Literal value and semantic name | Move to existing constants/contract module |
| Test fixture/factory | Fixture factory and existing test data | Extend shared fixture factory |
| Route/API client | Endpoint path, handler name, client wrapper | Update both server and client owner |
| Config/env flag | Env var prefix and config module | Add to central config owner |

**Banned patterns:**
- Creating `utils.ts`, `helpers.ts`, or `common.ts` without owner search
- Duplicating a type because import path was not obvious
- Creating parallel API clients for the same endpoint
- "I could not find it" without showing search terms

**Search evidence required:** When code is changed, include terms searched, files inspected, reuse decision, and new-code justification in the final response.

---

## 2. Systematic Debugging

Investigate the root cause before applying any fix — guessing compounds rework.
Full methodology (boundary instrumentation, competing hypotheses, postmortem):
`../../jaw-dev-debugging/SKILL.md` (canonical owner).

**Emergency stop triggers** — any of these means return to root-cause investigation:
"quick fix now, investigate later" · "just try changing X" · "don't fully understand
but might work" · proposing solutions before investigating · "one more attempt" after
2+ failures. After 3 failed fixes, pause and question the approach before another attempt.
**Repeated-friction rule (DEV-FRICTION-01, DEFAULT).** When the same command class
fails twice with the same normalized error, do not retry a third time unchanged:
switch approach — a different tool, different flags, or root-cause the
environment. Repeated identical failures are friction evidence, not bad luck.

**Repeated-edit-shape rule (DEV-EDIT-SHAPE-01, DEFAULT).** Three same-shaped edits
in a row (the same structural transform applied at different sites) mean you are
hand-running a codemod: stop and switch to an AST-based rewrite tool or a scripted
transform, so the remaining sites are transformed deterministically. The third
identical edit is the signal — by then the transform is known, and continuing by
hand is where the divergent site gets missed.


---
