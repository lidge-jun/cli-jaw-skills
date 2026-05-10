---
name: dev-pabcd
description: "PABCD orchestration workflow. Structured 5-phase development with user checkpoints. Injected during orchestration mode."
---

Structured 5-phase development. Advance only with user approval.

## How It Works

PABCD is a one-way loop — forward only.

```
IDLE ──→ P ──→ A ──→ B ──→ C ──→ D ──→ IDLE
         │      │      │      │      │
        STOP   STOP   STOP   auto   auto
        wait   wait   wait
```

To restart from any phase:
```
cli-jaw orchestrate reset   → returns to IDLE
```
Then re-enter with `cli-jaw orchestrate P`.

Phases P, A, B require user approval before advancing. C and D proceed automatically once their work is done.

Transition commands:
```
cli-jaw orchestrate P       → enter Planning (from IDLE only)
cli-jaw orchestrate A       → enter Plan Audit (from P only)
cli-jaw orchestrate B       → enter Build (from A only)
cli-jaw orchestrate C       → enter Check (from B only)
cli-jaw orchestrate D       → enter Done (from C only, returns to IDLE)
cli-jaw orchestrate reset   → return to IDLE (from any state)
```

## Phases

### P — Plan

If the request has unclear scope or unspecified technology, clarify first:
- Present 2–3 options as `<TechName> — <plain explanation>`
- Recommend one with project-specific reasoning
- Confirm once, then proceed

For broad changes or unfamiliar repositories, P phase MUST include:
- Compact tree of the current repository shape
- Detected repo conventions: docs, plans, architecture notes, source-of-truth logs, naming, tests
- Whether existing `structure/`, `devlog/`, `docs/`, `plans/`, or equivalent logs were read and will be reused
- Whether `structure/` or `devlog/` is proposed

Do not create new project-level source-of-truth folders during B unless approved in P or explicitly requested by the user.

Read project docs and dev skills first. Write a plan with two parts:
- **Part 1**: Easy explanation — what will be built, in non-developer terms.
- **Part 2**: Diff-level precision — exact file paths (NEW/MODIFY/DELETE), before/after diffs for MODIFY, complete content for NEW.

If PABCD work creates or updates `devlog/` plan artifacts, the plan MUST list exact numbered Jawdev filenames:
- `00_overview.md`
- `01_phase1_<slug>.md`
- `02_phase2_<slug>.md`

Do not propose bare `PLAN.md`, `DIFF_PLAN.md`, `PHASES.md`, `RCA.md`, or `plan.md` as new devlog phase files.

Ask the user:
1. "Any business logic I shouldn't decide alone?"
2. "Does Part 1 match your intent?"

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
Implement the plan. You write all code directly. Workers are read-only verifiers.

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

When done → `cli-jaw orchestrate D`

### D — Done
Summarize the entire flow:
- What was planned (P), audited (A), built (B), checked (C)
- List of files changed
- Any follow-up items

State returns to IDLE automatically.

## Rules

1. One phase per response. Present work, then wait for user approval at P, A, B gates.
2. Sequence: P → A → B → C → D. Use `cli-jaw orchestrate reset` to restart.
3. Workers verify (read-only). You write all code directly in B.

## Repository Root Contract

Before writing a PABCD plan or dispatching an employee, determine the actual
working repository root with `pwd -P` from the target repo.

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
- B phase: **Boss writes all code**. Workers are READ-ONLY verifiers.
- ⛔ Forbidden dispatch: `"implement the feature"`, `"write the code"`, `"create the file"`.
- ✅ Allowed dispatch: `"verify src/x.ts compiles"`, `"check integration of Y"`, `"report DONE or NEEDS_FIX"`.

### Context Drift
- If a worker says *"I'll proceed based on my assumption of the plan"* → STOP. Verify the dispatch went through `/api/orchestrate/dispatch` (only that path auto-injects the plan).
- Never let workers reconstruct the plan from a short task description.

### Phase Skip
- A (audit) is never "unnecessary". Even trivial plans can hit integration issues. Audit first.
- B verification is never "skippable". Untested code is not "done".
- The orchestrator does not enforce these gates today — YOU do.
