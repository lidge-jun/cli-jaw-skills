---
name: dev-pabcd
description: "PABCD orchestration workflow. Structured 5-phase development with user checkpoints. Injected during orchestration mode."
---

Structured 5-phase development. Advance only with user approval.

> **C0/C1 work (e.g. small in-place patches):** See `dev` §0.0 Work Classifier and §0.1 Patch
> Fast-Path first — full PABCD is mandatory for C4 and conditional for C3, not the baseline for every task.

## Interview Trigger (MUST)

When the user asks for an interview in any form — "인터뷰하자", "인터뷰 모드", "interview",
"요구사항 정리", "스펙 정리해줘", "뭘 만들어야 하는지 정리", or any variation — you MUST
immediately run:

    cli-jaw orchestrate I

Do NOT:
- Ask clarifying questions in IDLE mode instead of entering Interview
- Use the `/interview` slash command instead of `cli-jaw orchestrate I`
- Skip Interview and go straight to P for unclear requests
- Forget to run the command — actually execute it in Bash

The `/interview` slash command is a user-facing shortcut that triggers the same transition.
As the Boss agent, always use `cli-jaw orchestrate I` directly.

## How It Works

PABCD is a forward progression with Interview return.

```
IDLE ──→ P ──→ A ──→ B ──→ C ──→ D ──→ IDLE
         │      │      │      │      │
        STOP   STOP   STOP   auto   auto
        wait   wait   wait
         └──────┴──────┴──────┴──────┘
                      ↓
                 I (Interview)
              context preserved
```

You can return to Interview (I) from any phase to clarify requirements. Context (plan, audit status) is preserved.

To restart from scratch:
```
cli-jaw orchestrate reset   → returns to IDLE (context cleared)
```
Then re-enter with `cli-jaw orchestrate P`.

Phases P, A, B require user approval before advancing. C and D proceed automatically once their work is done.

Transition commands:
```
cli-jaw orchestrate I       → enter Interview (from any state, context preserved)
cli-jaw orchestrate P       → enter Planning (from IDLE or I)
cli-jaw orchestrate A       → enter Plan Audit (from P only)
cli-jaw orchestrate B       → enter Build (from A only)
cli-jaw orchestrate C       → enter Check (from B only)
cli-jaw orchestrate D       → enter Done (from C only, returns to IDLE)
cli-jaw orchestrate reset   → return to IDLE (from any state)
```

## Phases

### P — Plan

If the request has unclear scope or unspecified technology, return to Interview (`cli-jaw orchestrate I`). Within Interview:
- Present 2–3 options as `<TechName> — <plain explanation>`
- Recommend one with project-specific reasoning
- Confirm once, then proceed

For broad changes or unfamiliar repositories, P phase MUST include:
- Compact tree of the current repository shape
- Detected repo conventions: docs, plans, architecture notes, source-of-truth logs, naming, tests
- Whether existing `structure/`, `devlog/`, `docs/`, `plans/`, or equivalent logs were read and will be reused
- Whether `structure/` or `devlog/` is proposed

Do not create new project-level source-of-truth folders during B unless approved in P or explicitly requested by the user.

Design phases before mapping them to PABCD. A phase should normally be a user-visible
or consumer-visible outcome unit: "create an item", "edit an item", "share a report",
or "compare three runnable prototypes". DB/API/UI/test work are subtasks inside that
outcome, not top-level phases by default. A simple task can finish in one PABCD with
several small phases; larger work can split into multiple PABCD passes. Layer-only
phases are allowed only when independently verifiable and explicitly justified. Do not
plan a whole database/API foundation as one PABCD before any usable outcome exists.

Read project docs and dev skills first. Write the complete plan internally, then report it simply — like a developer reporting to the CEO.

Write a plan with two parts:
- **Part 1**: Easy explanation — what will be built, in non-developer terms.
- **Part 2**: Diff-level precision — exact file paths (NEW/MODIFY/DELETE), before/after diffs for MODIFY, complete content for NEW.

If anything is unclear, return to Interview (`cli-jaw orchestrate I`) — do NOT ask questions in P.

### Jawdev Document Numbering (decade ranges)

Devlog plan artifacts use decade-range numbering to separate concerns:

| Range | Purpose | Examples |
|-------|---------|----------|
| 00–09 | Research, specs, MOC | `00_plan.md`, `01_api-survey.md`, `02_competitor-analysis.md` |
| 10–19 | Phase 1 | `10_phase1-auth-module.md`, `11_phase1-db-schema.md` |
| 20–29 | Phase 2 | `20_phase2-frontend.md` |
| 30–39 | Phase 3 | ... |

Rules:
- 00-range durable research is **mandatory for C4**, and for C3 only when state must persist
  across turns/agents, public contract or architecture decisions need durable audit, or the
  user/repo already uses devlog planning for that task; optional for C0-C2 and
  low-persistence C3 (a response-level plan plus verification record is enough).
- Default: sequential within decade (`00`, `01`, `02`...).
- Overflow (>10 docs in a range): use sub-index (`00_0_name.md`, `00_1_name.md`).
- NEVER use bare filenames like `PLAN.md`, `DIFF_PLAN.md`, `PHASES.md`, `RCA.md`.

Present to the user:
1. Part 1 summary (≤5 sentences) + diagram + devlog file path
2. "혼자 결정하면 안 되는 비즈니스 로직이 있나요?" and "이 방향이 맞습니까?"

⛔ Present the plan. Revise on feedback.
When user approves → `cli-jaw orchestrate A`

### A — Plan Audit
Spawn a worker to audit the plan (not code). The worker verifies:
- All file paths and imports in the plan actually exist
- Function signatures match real code
- No integration risks
- Existing source-of-truth docs/logs were read when present
- No new `structure/`, `devlog/`, docs, or AGENTS files are introduced without user approval
- New JS/TS files follow TypeScript preference rules unless the plan states why JS is required
- New TypeScript is strict-compatible or limitations are stated
- New devlog phase documents use the numbered Jawdev filename convention.

Output worker JSON for the audit. Review results when they come back.
- If FAIL → fix the plan → output worker JSON again to re-audit
- If PASS → report results to the user

⛔ Wait for user approval. When approved → `cli-jaw orchestrate B`

### B — Build
Implement the plan. You write all code by default. Workers are read-only verifiers unless dispatched with `--mutable` (see Pitfalls).

Do not create `structure/` or `devlog/` unless approved in P or explicitly requested by the user.

After implementing, output worker JSON for verification. The worker checks your code exists and integrates cleanly.
- If NEEDS_FIX → you fix the issues → re-verify
- If DONE → report results to the user

⛔ Wait for user approval. When approved → `cli-jaw orchestrate C`

### C — Check
Final sanity check:
1. Verify all files saved and consistent
2. Run `npx tsc --noEmit` (if TypeScript project)
3. Update project structure docs if applicable
4. Report completion summary

Long external gates (CI runs, deploys) inside cli-jaw: do not block the turn —
register `cli-jaw bgtask add --cmd '[...]' --prompt "..."` and end the turn; the
server re-invokes the boss on completion and PABCD state persists across turns.
Local tsc/tests stay blocking.

When done → `cli-jaw orchestrate D`

### D — Done
Summarize the entire flow:
- What was planned (P), audited (A), built (B), checked (C)
- List of files changed
- Any follow-up items

State returns to IDLE automatically.

Project root configuration is persistent. D completion resets the PABCD state, but it
does not clear configured `projectDirs`; use `cli-jaw project clear` only when the
user explicitly asks to unset the project root.

## Rules

1. One phase per response. Present work, then wait for user approval at P, A, B gates.
2. Sequence: P → A → B → C → D. Use `cli-jaw orchestrate reset` to restart.
3. Workers verify (read-only). You write all code directly in B.
4. Goal-mode precedence: when a jaw goal is active (dev §0.4), P/A/B approval gates are
   satisfied by evidence-backed checkpoints (`cli-jaw goal update`) instead of waiting for
   user approval. Phase order, audit conditions, and verification intensity are unchanged.

## Repository Root Contract

Before writing a PABCD plan or dispatching an employee, determine the actual
working repository root with `pwd -P` from the target repo.

If `Project root` is injected at the top of the system prompt, use that value directly.
If it is NOT set, recommend the user configure it:
- Manager UI → Project settings
- CLI: `cli-jaw project add /path/to/repo`

Setting project root prevents confusion between JAW_HOME (`~/.cli-jaw-*`) and the actual codebase.

Every A/B phase `cli-jaw dispatch` task body MUST begin with:

```text
Project root: /absolute/path/to/current/repo
```

Rules:
- `Project root` must be the current working repository, not `JAW_HOME`.
- Never let workers infer the repo root from `~/.cli-jaw*`, `process.cwd()`, or an employee temp directory.
- Resolve all relative repo paths (`src/...`, `tests/...`, `structure/...`, `skills_ref/...`) against `Project root`.
- If `Project root` is unknown, STOP and ask before dispatching.

## Shared Plan (auto-injected)

When P completes, the plan is saved to the **worklog `## Plan` section** (single source of truth) and kept in `ctx.plan`. No project-root file is created.

- In A and B, the orchestrator **auto-injects the full plan body** at the top of every `cli-jaw dispatch` task under `## Approved Plan`.
- Workers never read a plan file. Your task body should contain only the actual audit/verify instruction — the plan is prepended for you.
- Example: `cli-jaw dispatch --agent "Backend" --task "Project root: /absolute/path/to/current/repo

Audit: verify the imports in ..."` — no "read the plan" line needed.

## Pitfalls (반드시 피해야 할 행동)

### Delegation Trap
- B phase: **Boss writes all code by default**. Workers are READ-ONLY verifiers.
- 💡 To let a worker write, use `--mutable` (optionally `--scope`): `cli-jaw dispatch --agent "Name" --mutable --task "..."`.
- ⛔ Without `--mutable`: `"implement the feature"`, `"write the code"`, `"create the file"` are forbidden.
- ✅ Always allowed: `"verify src/x.ts compiles"`, `"check integration of Y"`, `"report DONE or NEEDS_FIX"`.

### Context Drift
- If a worker says *"I'll proceed based on my assumption of the plan"* → STOP. Verify the dispatch went through `/api/orchestrate/dispatch` (only that path auto-injects the plan).
- Never let workers reconstruct the plan from a short task description.

### Phase Skip
- A (audit) is **mandatory for C4**, and for C3 when public contract, architecture,
  persistence, cross-agent, or cross-session risk exists; use a micro-audit for C2 and
  optional audit for C0-C1 (see `dev` §0.0 for classes).
- B verification is never "skippable". Untested code is not "done" — but verification
  intensity scales with the work class (PABCD-AUTO-01).
- The orchestrator does not enforce these gates today — YOU do.

## PABCD Depth by Work Class

| Class | Plan (P) | Audit (A) | Build (B) | Check (C) | Record (D) |
|-------|----------|-----------|-----------|-----------|------------|
| C0-C1 | None/inline | Optional | Direct fix | Smallest proof | One-line summary |
| C2 | Compact plan | Micro-audit | Boss writes, focused tests | Targeted gate | Summary |
| C3 | Compact or full PABCD plan depending on persistence/risk | Required when public contract, architecture, persistence, cross-agent, or cross-session risk exists; otherwise focused audit | Boss writes, employees verify only when useful | Affected suite + docs consistency when docs/contracts changed | Summary + evidence; durable record only when state must persist |
| C4 | Full PABCD plan (mandatory) | Required, independent | Boss writes, employee verifies | Full relevant gates | Durable risk/approval/evidence record |
| C5 | Interview/research first | — | — | — | Reclassify, then follow the new class |
