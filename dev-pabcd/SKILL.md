---
name: dev-pabcd
description: |
  PABCD orchestration workflow for structured multi-step development.
  Phases: Plan → Plan Audit → Build → Check → Done.
  Triggers: "orchestrate", "지휘 모드", "pabcd", "orchestration mode"
version: 1.0.0
---

# PABCD Orchestration Skill

## Goal

Drive complex development tasks through 5 mandatory phases with human checkpoints between each. Prevent the agent from rushing through work without user validation.

## What is PABCD?

PABCD = **P**lan → **A**udit (of the plan) → **B**uild → **C**heck → **D**one

Each letter is a **phase** with a specific job. The agent must complete ONE phase, then **STOP and WAIT** for user approval before advancing.

```
IDLE → P → (user OK) → A → (user OK) → B → (user OK) → C → D → IDLE
```

## Phase Details

### P — Plan

**Job**: Write a structured plan with two parts.

1. Read structural documentation and dev skill docs first.
2. Write **Part 1**: Easy explanation (non-developer friendly).
3. Write **Part 2**: Diff-level precision — exact file paths (NEW/MODIFY/DELETE), before/after diffs for MODIFY, complete content for NEW.
4. Present the plan and ask:
   - "Any business logic I shouldn't decide alone?"
   - "Does Part 1 match your intent?"

⛔ **STOP**. Wait for user approval. Revise if needed.

### A — Plan Audit

**Job**: Verify THE PLAN before any coding begins.

⚠️ This phase audits the **plan**, NOT existing code. Do NOT skip.
⚠️ Do NOT say "audit is unnecessary."

1. Output a worker JSON to spawn an audit worker:
```json
{"subtasks":[{"agent":"Data","task":"Audit the PLAN (not code). Verify: 1) All imports in the plan resolve to real files. 2) Function signatures match actual code. 3) No copy-paste integration risks. Report PASS or FAIL with itemized issues.","priority":1}]}
```
2. The system spawns the worker automatically.
3. Wait for results.
4. If FAIL → fix plan → re-audit (output worker JSON again).
5. If PASS → report to user.

⛔ **STOP**. Wait for user approval.

### B — Build

**Job**: Implement the audited plan.

Rules:
- Follow dev skill conventions strictly.
- No TODOs or placeholders — every file must be complete.
- All imports must resolve to real files.

After implementation:
1. Output a worker JSON to verify code:
```json
{"subtasks":[{"agent":"Data","task":"Verify the implemented code: 1) Integrates cleanly with existing modules. 2) No runtime issues. 3) All exports used correctly. Report DONE or NEEDS_FIX.","priority":1}]}
```
2. Wait for worker results.
3. Fix any NEEDS_FIX items.
4. Once DONE → report to user.

⛔ **STOP**. Wait for user approval.

### C — Check

**Job**: Final verification.

1. Verify all files saved and consistent.
2. Run `npx tsc --noEmit` for build verification (if TypeScript).
3. Update project structure docs if applicable.
4. Report completion summary.

Then advance to D.

### D — Done

**Job**: Summarize and close.

Report:
- What was planned (P), audited (A), implemented (B), verified (C).
- List of files changed.
- Any follow-up items.

State returns to IDLE automatically.

## How to Activate

The user says one of:
- `orchestrate`
- `지휘 모드`
- `pabcd`
- `orchestration mode`

Or the system can call `cli-jaw orchestrate` via shell.

## Critical Rules

1. **ONE phase per turn.** Never do P+A or A+B in the same response.
2. **⛔ STOP at phase end.** Present your output, then WAIT for user.
3. **Never skip A.** Even for simple projects, the plan must be audited.
4. **Workers are automatic.** Output subtask JSON → system spawns worker → results come back to you.
5. **User is the gatekeeper.** Only advance when user explicitly approves (OK, lgtm, 진행, ㅇㅋ, next).

## State Management

- State is persisted in SQLite (`jaw.db` → `orc_state` table).
- CLI and server share the same DB.
- `cli-jaw orchestrate [P|A|B|C|D]` transitions state and outputs phase prompt to stdout.
- `orchestrateReset()` or user saying "리셋해" returns to IDLE.

## Prefix System

During active PABCD, messages get automatic prefixes:
- **P state + user message** → `[PLANNING MODE — User Feedback]` prefix
- **A state + worker result** → `[PLAN AUDIT — Worker Results]` prefix
- **B state + worker result** → `[IMPLEMENTATION REVIEW — Worker Results]` prefix
- **B state + user message** → no prefix (user feedback is passed as-is)

## Transition Guards

```
IDLE → P (only)
P → A (only)
A → B (only)
B → C (only)
C → D (only)
D → IDLE (auto)
```

No skipping. P→D is invalid. IDLE→B is invalid.

## Constraints

- ≤ 500 lines per source file (dev skill hard limit)
- All prompts in English
- Worker agents are executors only — they do NOT output subtask JSON
- State machine code lives in `src/orchestrator/state-machine.ts`
- Pipeline code lives in `src/orchestrator/pipeline.ts`
