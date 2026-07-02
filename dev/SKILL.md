---
name: dev
description: "MUST USE for every coding task — classifies work depth (C0-C5), task_tags overlays, modular limits, pre-write search, verification-before-completion, and safety rules. Triggers: develop, implement, refactor, feature, bug fix, test, review, code quality, scaffolding."
metadata:
  short-description: "Universal dev discipline: work classifier, overlays, verification gate, safety rules."
  keywords: "develop, implement, refactor, feature, code quality, verification"
  last-verified: "2026-07-02"
---

# Dev — Common Development Guidelines

Rules applied to every sub-agent, regardless of role.

## §0.0 Work Classifier (C0-C5)

**Classify every task before choosing process depth** (DEV-CLASS-01). The class selects planning, reading, and verification depth — never apply maximum process by default.

| Class | Name | Signals | Default Process |
|-------|------|---------|-----------------|
| C0 | Trivial Text | Typo, comment, copy, log string — zero behavior change | Direct fix + smallest proof (§0.1) |
| C1 | Single-File Local | One file, local behavior, no new abstractions | Fast path (§0.1) + targeted check |
| C2 | Ordinary Product Slice | Conventional endpoint, form, table, model, list/detail screen, integration touchpoint | Compact plan + adjacent convention search + focused tests + micro-audit (orchestration mode) |
| C3 | Cross-Domain Feature/Refactor | Multiple modules, public API, shared types, broad behavior | Compact or full PABCD depending on persistence/risk; employee audit per `dev-pabcd` Phase Skip conditions |
| C4 | High-Risk | Auth, payments, data deletion, migration, release, permission model, security boundary | Full PABCD (mandatory) + full relevant gates + durable risk/evidence record |
| C5 | Research/Ambiguous | Unclear requirements, ambiguous user value, unknown territory after one §0 clarification round | Interview/research first (`cli-jaw orchestrate I`), then reclassify |

**Tie-break (DEFAULT):** when signals match two classes, the higher class wins. A conventional route→service→storage slice still counts as C2 even though it spans files; C3's "multiple modules" means crossing a module/package boundary beyond that conventional slice.

**C4-promotion triggers override any fast path** (DEV-ESCALATE-01): security, data
deletion/migration, destructive ops, public contract change, release surface, permission
model, new dependency/framework. Any of these promotes the **affected part** of the task
to C4-level care — split it out rather than inflating the whole slice. Promotion alone
does not force a user question; stopping to ask is required only for rules individually
classed **ESCALATE** (§0.2). Classifier eval cases: `evals/classifier_cases.json` —
run when tuning trigger/classification behavior; track false promotions and demotions separately.

## §0.1 Patch Fast-Path (C0/C1)

For **C0/C1 work** (one file, no new abstractions, local behavior — a ≤5-line
edit is an example, not a limit):
- Skip: §0.5 convention discovery, §1.5 pre-write search, reference file reading
- Keep: §3 verification gate, §4 change documentation when a worklog/changelog file is provided, §5 safety rules (imports/exports), §7.2 static analysis
- Role skills: read only the SKILL.md routing table — skip references unless the table explicitly routes to one

This is scope guidance, not an exemption. Conventions visible in the touched file still apply even when proactive discovery is skipped. Promotion is **behavioral**, not territorial: a patch escalates when it can alter an auth/payment/deletion or other DEV-ESCALATE-01 path — not merely because the file lives there. A zero-behavior edit (comment, typo, log string) inside an auth file stays C0; any edit touching executed logic in such a path is not C0/C1 — reclassify and read the relevant reference.

## §0.2 Rule Classes

Every rule in the dev skill family carries one severity class. When unmarked, treat prohibitions (⛔/MUST/NEVER) as STRICT and everything else as DEFAULT.

- **STRICT** — always applies; violating it blocks completion (safety, broken builds, secrets).
- **DEFAULT** — apply unless a documented, stated reason says otherwise.
- **HEURISTIC** — judgment guide; deviation needs no justification, just awareness.
- **STYLE_SAMPLE** — illustrative example or preset only. Examples illustrate acceptable
  choices but MUST NOT become universal requirements (DEV-STYLE-SAMPLE-01).
- **ESCALATE** — stop and ask the user before proceeding.

## §0.3 Methodology Overlays (task_tags)

Methodologies are **conditional overlays, never universal**. They activate via dispatch
`task_tags`, explicit user request, repo convention, or a matching strict trigger — required
evidence applies only when the strict trigger applies (low-risk/local work uses the smallest
proof that validates the claim, with the reduced scope stated).

| Tag | Loads | Strict trigger |
|-----|-------|----------------|
| `tdd` / `testing` | dev-testing | User/repo enforces TDD, or regression risk |
| `bdd_acceptance` | dev-testing, dev | Ambiguous acceptance behavior |
| `ddd` / `clean_arch` / `hexagonal` / `architecture` | dev-architecture, dev-backend | Real boundary pressure at C3/C4 |
| `vertical_slice` | dev-architecture, dev-backend, dev-frontend, dev-testing | Thin end-to-end slice (C2) |
| `adr_rfc` | dev-architecture, dev-scaffolding | Significant decision, domain vocabulary, or ADR source-of-truth work |
| `review` / `code_review` | dev-code-reviewer | Review requested or C3/C4 |
| `threat_model` / `security` | dev-security | C4 security/data/tooling risk |
| `observability` / `observability_pipeline` | dev-backend (+dev-data) | Production, incident, release, long-lived runtime |
| `debugging` / `debugging_rca` | dev-debugging | Repeated failure needs root cause |
| `migration_backfill` | dev-data, dev-backend, dev-testing | Production or non-trivial data |
| `product_discovery` (+`_ui`) | dev (+dev-uiux-design) | Ambiguous behavior/user value/metric/prototype intent |
| `release_cd` | dev-testing, dev-backend, dev-scaffolding, dev-devops | Release/CI/CD surface |
| `devops` / `infra` / `deploy` | dev-devops | Container/K8s/IaC/deploy pipeline/SRE |
| `mobile_native` | dev-frontend + dev-uiux-design + dev-backend (refs) | RN/Flutter/Swift/Kotlin native app |
| `ml` / `ai` / `llm` / `rag` | dev-backend + dev-data + dev-testing (+dev-devops) | ML serving, RAG, pipeline, evaluation |
| `frontend_ui` | dev-frontend + dev-uiux-design | UI/design intent or runnable prototype variant work |
| `crud_fullstack` | dev-backend, dev-frontend, dev-testing | Boss/direct planning signal only — when delegating, prefer split roles |

Tags are normalized `task_tags`, **not** employee `role` values; the execution role stays
`frontend|backend|data|docs` (PROMPT-ROUTING-01).

The boss sets `task_tags` at dispatch. With no tags, only strict triggers (self-assessed
by the employee, reduced scope stated) activate overlays — legacy dispatches without the
field behave identically. `task_tags` must be an array; a bare string is coerced to a
single tag, and unknown tags are surfaced in the prompt, not silently dropped.

### Ordinary product reference (on-demand)

For C2 ordinary product slices, the recipe lives in
`references/product/crud-product-development.md` — read it when building a conventional
feature slice, not for every task.

## §0.4 Workflow Modes

The same rules flex by execution mode — know which one you are in:
ordinary chat (direct work, C0-C2 typical) · strict PABCD (`orchestrate P/A/B/C/D`) ·
goal mode (self-advancing gates, evidence-backed checkpoints) · isolated employee
(read-only verifier by default) · mutable employee (`--mutable`, scoped writes) ·
read-only review (no mutation, findings only) · docs-only work (no code gates, docs
consistency checks instead).

In goal mode, multi-phase / "loop"/"루프" work runs one FULL PABCD cycle per work-phase
(depth scaled by §0.0 class); after D, re-enter P for the next work-phase. Classify EACH
work-phase independently — C0-C1 fast-path applies to that work-phase's class, not the
whole goal. Do each PABCD-phase's real work; never rubber-stamp a phase to advance.

**Production surface (shared definition):** deployed for real users beyond the author;
prototypes, spikes, and internal demos are not. Skills that scope rules to
"production-surface" concerns condition on this definition.

## Companion Skills

This skill covers universal guidelines. **STRICT (DEV-ROUTE-01):** for domain-specific work, also read the matching role skill's `SKILL.md` before writing code in that domain:

| Skill File                   | Injected When                     | Covers |
| ---------------------------- | --------------------------------- | ------ |
| `dev-frontend/SKILL.md`      | `role=frontend`                   | UI implementation, responsive, anti-slop |
| `dev-backend/SKILL.md`       | `role=backend`                    | API/architecture, data access, ops |
| `dev-data/SKILL.md`          | `role=data`                       | Pipelines, data quality, analytics SQL |
| `dev-security/SKILL.md`      | Security-sensitive code, or `security`/`threat_model` task_tags | OWASP, auth, secrets, supply chain |
| `dev-testing/SKILL.md`       | `testing`/`tdd` task_tags, or testing phase | Test strategy, Playwright, contracts, CI |
| `dev-debugging/SKILL.md`     | Debugging phase (phase 4)         | Root-cause method, instrumentation |
| `dev-code-reviewer/SKILL.md` | Any agent, during code review     | Review process, severity, antipatterns |
| `dev-architecture/SKILL.md`  | Module boundary work, dependency analysis | Cycles, coupling, barrels, validation placement |
| `dev-uiux-design/SKILL.md`   | Vague design direction, UX state patterns | Intent discovery, design vocabulary, UX states |
| `dev-scaffolding/SKILL.md`   | New project/feature setup, structural audit, docs generation | Lidge Standard, colocation, devlog |
| `dev-pabcd/SKILL.md`         | Orchestrated multi-phase development | PABCD phases, gates, attestation |

### Skill Ownership Map

Each rule area has exactly one canonical owner. Other skills may contain stubs but MUST NOT duplicate canonical content.

| Rule Area | Canonical Owner | Stub Locations |
|-----------|----------------|----------------|
| Circular dependencies | dev-architecture | dev, dev-code-reviewer |
| Module boundaries / layers | dev-architecture | dev-backend, dev-frontend |
| Coupling taxonomy | dev-architecture | dev-code-reviewer |
| Barrel / re-export | dev-architecture | dev-scaffolding |
| Pre-write search | dev §1.5 | dev-code-reviewer |
| Edge-first testing | dev-testing §6 | — |
| Test-induced defense | dev-testing §6.7 | dev-code-reviewer |
| Boundary-only defense | dev-architecture §4 | dev-backend, dev-security |
| Process isolation | dev-backend refs/ | dev-code-reviewer |
| Code quality signals / antipatterns | dev-code-reviewer §3 | dev §6 |
| Long-lived connections (server lifecycle) | dev-backend §1 | dev-frontend |
| Browser connection budgets | dev-frontend refs/performance-budget | — |
| Async task queue | dev-backend §2 | — |
| Debugging methodology | dev-debugging | dev-code-reviewer |
| Data pipeline patterns | dev-data | dev-backend |
| Design intent discovery | dev-uiux-design | dev-frontend |
| Project scaffolding / docs | dev-scaffolding | dev-pabcd |
| Orchestration workflow | dev-pabcd | — |

When updating a rule, update the canonical owner first, then verify stubs still point correctly.

**When your task spans multiple domains**, read each relevant skill file before starting.

---

## Family Invariants (apply to every `dev-*` skill)

**FAMILY-SLOP-01 / FAMILY-CITE-01 / FAMILY-PROOF-01:** no filler, placeholders, fake fallbacks, speculative wrappers, or broad defensive clutter without a named boundary reason; code findings, plans, reviews, contradictions, and verification claims cite exact files/lines or command/artifact evidence; no completion claim without fresh proof from the §3 verification gate.

**FAMILY-FRESH-01 (DEFAULT):** version-pinned or time-sensitive claims live in
`references/` with a Sources row (URL + checked date); routers carry only a
frontmatter `last-verified` stamp. Treat claims older than the stamp as re-verify-first.

## Documentation Verification (Context7)

Before using any external library API, verify current syntax via Context7 MCP
(`resolve-library-id` → `query-docs`). **Verify when:** API not verified this session,
pinned version, uncertain behavior, or a major release in the past 6 months.
**Skip for:** language built-ins, standard library, syntax verified this session.
If Context7 is unavailable, fall back to web search for official docs — never rely
on training data alone for library-specific APIs.

### External/current evidence

For current versions, release notes, CVEs, package/source checks, or provider behavior,
read the active `search` skill and follow its query-rewrite, source-fetch, and
evidence-status rules. Sub-agents are bound by this policy too — include it in dispatch prompts.

---

## 0. Intent Clarification

When a request has **ambiguous scope or unspecified technology**, clarify before coding;
skip entirely when tech and scope are already clear.

- Present 2-3 options as `<TechName> — <plain explanation>` with project-relevant
  pros/cons; ⚠️ flag complex/expensive/risky options.
- Recommend one, citing project context; let the user decide (warn once on a risky pick).
- **Over-engineering guard**: prefer the simplest option that meets stated needs.
- **Limit — one confirmation round**: options → recommendation → confirm → move on.

---

## 0.5 Repository Convention Discovery

Before broad changes, inspect existing conventions: source layout (`src/`, `app/`,
`packages/`), source-of-truth docs (`structure/`, `docs/`, `adr/`, `devlog/`, `plans/`),
agent context files (`AGENTS.md`, `CLAUDE.md`, tool instruction files), JS/TS setup
(`package.json`, `tsconfig*`, linter config, sibling extensions), and naming/test/
phase-document patterns (Jawdev decade numbering — see `dev-pabcd`).

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

**Hard limits (DEFAULT — exceed only with a stated reason):**

| Metric              | Threshold   | Action                                   |
| ------------------- | ----------- | ---------------------------------------- |
| File length         | >400 lines  | Split into focused modules (canonical owner: dev-architecture §1) |
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
- Use ES Modules in JS/TS projects — CommonJS `require()` breaks tree-shaking and static analysis.
- One default export per file when it has a primary purpose (JS/TS convention; other languages follow their idioms).
- Follow existing naming/directory conventions; check sibling files before creating new ones.
- Jawdev/devlog phase documents use decade-range numbering (00-09 research, 10-19 phase 1, …); never bare `PLAN.md`/`PHASES.md`/`RCA.md`. Full convention: `dev-pabcd`.

---

## 1.5 Pre-Write Codebase Search Obligation

**Rule:** Before creating a new function, helper, type, component, constant, route, fixture, or module, search the codebase for an existing owner or equivalent implementation. No new abstraction may be introduced without search evidence. This section does not apply on the §0.1 fast path (C0/C1 — no new abstractions are being created).

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
`dev-debugging/SKILL.md` (canonical owner).

**Emergency stop triggers** — any of these means return to root-cause investigation:
"quick fix now, investigate later" · "just try changing X" · "don't fully understand
but might work" · proposing solutions before investigating · "one more attempt" after
2+ failures. **3+ failed fixes = architectural problem**: pause, question the pattern
itself, and discuss with the user before further fixes.

---

## 3. Verification Before Completion (STRICT)

Verify every completion claim with evidence. Run the relevant command fresh, read full output, and confirm the claim matches.

**Verification gate (before any completion claim):**

1. **Identify** — What command proves this claim?
2. **Run** — Execute fresh (not cached).
3. **Read** — Full output. Check exit code. Count failures.
4. **Confirm** — Does the output actually support the claim?
5. **Report** — State the claim with evidence attached.

**Per-class verification floor (DEV-VERIFY-FLOOR-01):** C0/C1 use the smallest proof; C2 adds focused integration/contract checks for the touched slice; C3 runs affected suites and contract/docs checks; C4 runs full relevant gates plus negative cases and durable evidence.

| Claim                   | Requires                              | Not Sufficient                |
| ----------------------- | ------------------------------------- | ----------------------------- |
| "Tests pass"            | Test command output: 0 failures       | Previous run, "should pass"   |
| "Build succeeds"        | Build command: exit 0                 | "Linter passed"               |
| "Bug fixed"             | Original symptom verified resolved    | "Code changed, assumed fixed" |
| "Feature complete"      | Each requirement checked line-by-line | "Tests pass"                  |
| "Agent completed"       | VCS diff shows actual changes         | Agent report says "success"   |
| "Regression test works" | Red-green cycle verified              | Test passes once              |

**Agent delegation:** When sub-agents report success, verify independently: check VCS diff → verify changes exist → confirm behavior.

**Long external waits (cli-jaw runtime):** don't block the turn polling CI/deploys/
web-ai sessions — register `cli-jaw bgtask add --cmd '[...]' --prompt "..."` and end
the turn; the server re-invokes the boss on completion. Local tests/tsc/builds stay blocking.

**Red flags — unverified claims creeping in:** "should"/"probably"/"seems to" ·
satisfaction before verification · partial/previous-run evidence · trusting agent
success reports · "just this once".

---

## 4. Change Documentation

When a worklog/changelog file is provided, record one factual entry per changed file:
`### [filename] — [reason]` with **Changes** (what/why), **Impact** (dependent modules),
and **Verification** (command + result).

---

## 5. Safety Rules

- **Preserve existing exports** — other modules may depend on them. Deprecate first if removal is needed.
- **Verify imports exist** before adding `import` statements. Confirm the target file and export are real.
- **Externalize configuration** — use config files or environment variables. Place magic strings and numbers in named constants.
- **Handle all async errors explicitly** — surface failures at a clear boundary. In JS/TS backend code, the Result pattern (`neverthrow`) may replace per-call `try/catch` when failures are surfaced at a verified boundary (see `dev-backend/SKILL.md` §3). In other cases, use `try/catch` and log with context (`console.error('[module]', error.message)`).
- **Confirm before destructive operations (ESCALATE)** — deleting files, dropping tables, resetting state, or clearing caches require explicit user approval.

---

## 6. Code Quality Signals (stub)

Anti-pattern detection (god class, long method, deep nesting, magic numbers, stringly
typed, missing boundary error handling, floating promises, copy-paste) is canonically
owned by `dev-code-reviewer/SKILL.md` §3 — read it when writing or reviewing code.
Thresholds mirror §1 hard limits; boundary-error placement follows dev-architecture §4.

---

## 7. Type Safety & Static Analysis

### 7.0 JS/TS Source File Default

New JS/TS source files prefer TypeScript (`.ts`/`.tsx`) when the repo supports it or
is greenfield; use `.js` only for clearly JS-only repos, build constraints, or explicit
user request. Never introduce TS tooling, convert existing JS, or change `tsconfig`
without approval. New TypeScript MUST be strict-compatible from the first patch:
no implicit `any` (explicit `any` needs justification), prefer `unknown` + narrowing,
type exported params/returns, handle null/undefined deliberately. Verify with the
project's typecheck (or `tsc --noEmit`); if strict compatibility can't be verified, say so.

### 7.1 Type Annotations

Add explicit types to all function signatures, return types, and non-trivial variables.
TypeScript: `strict: true`, no implicit `any` (explicit `any` needs a justification
comment). Python: hints on all params/returns. Enable the language's strict/pedantic
mode when one exists. Per-language rules table: `references/static-analysis-gate.md`.

### 7.2 Static Analysis Gate

After every code change, run the project's static analysis toolchain as part of the
verification gate (§3) — zero errors on changed files is the floor. Per-toolchain
commands and the anti-pattern ↔ lint-rule mapping live in
`references/static-analysis-gate.md`; check project config for the canonical rule set.
If no tool is configured, recommend one — but do not add tooling without approval.

### 7.3 Escape Hatches

When bypassing the type system is unavoidable: comment why, scope minimally (narrowest
cast point), prefer assertion functions over raw casts. TS `as unknown as T` needs a
linked issue/TODO; Python `# type: ignore[code]` must name the exact error code.

---

## 8. Token Budget Awareness

**Tiered reference loading:** (1) always read injected skills' SKILL.md routers;
(2) read `references/` files only when the task touches that topic; (3) do not
preload all references (HEURISTIC) — e.g. a caching task reads `caching.md` only.
**Sub-agents:** each receives its own copy of injected skills — inject only what
that sub-task needs.

---
