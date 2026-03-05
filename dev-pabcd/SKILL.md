---
name: dev-pabcd
description: "PABCD orchestration workflow. Structured 5-phase development with user checkpoints. Injected during orchestration mode."
---

This skill guides structured, multi-step development through 5 mandatory phases.
The user controls the pace — you never advance without their approval.

## Purpose

PABCD exists to prevent two common AI mistakes:
1. **Rushing to code** without thinking through the design (missed edge cases, broken imports, wrong architecture decisions)
2. **Delivering unverified work** — code that compiles but hasn't been sanity-checked against the existing codebase

By splitting work into Plan → Audit → Build → Check → Done, each phase gets focused attention and the user stays in control.

## How It Works

PABCD is a strictly sequential pipeline. Each phase must complete before the next begins. The user decides when to advance.

```
IDLE ──→ P ──→ A ──→ B ──→ C ──→ D ──→ IDLE
         │      │      │      │      │
        STOP   STOP   STOP   auto   auto
        wait   wait   wait
```

Phases P, A, B require user approval before advancing. C and D proceed automatically once their work is done.

To advance between phases, run:
```
cli-jaw orchestrate P   → enter Planning
cli-jaw orchestrate A   → enter Plan Audit
cli-jaw orchestrate B   → enter Build
cli-jaw orchestrate C   → enter Check
cli-jaw orchestrate D   → enter Done (returns to IDLE)
```

This is the ONLY way to transition. No other method.

## Phases

### P — Plan
Read project docs and dev skills first. Write a plan with two parts:
- **Part 1**: Easy explanation — what will be built, in non-developer terms.
- **Part 2**: Diff-level precision — exact file paths (NEW/MODIFY/DELETE), before/after diffs for MODIFY, complete content for NEW.

Ask the user:
1. "Any business logic I shouldn't decide alone?"
2. "Does Part 1 match your intent?"

⛔ STOP. Present the plan. Revise if the user gives feedback.
When user approves → `cli-jaw orchestrate A`

### A — Plan Audit
Spawn a worker to audit YOUR PLAN (not the code). The worker verifies:
- All file paths and imports in the plan actually exist
- Function signatures match real code
- No integration risks

Output worker JSON for the audit. Review results when they come back.
- If FAIL → fix the plan → output worker JSON again to re-audit
- If PASS → report results to the user

⛔ STOP. When user approves → `cli-jaw orchestrate B`

### B — Build
Now implement. YOU write all the code directly. Workers are READ-ONLY verifiers — they never create, modify, or delete files.

After implementing, output worker JSON for verification. The worker checks your code exists and integrates cleanly.
- If NEEDS_FIX → you fix the issues → re-verify
- If DONE → report results to the user

⛔ STOP. When user approves → `cli-jaw orchestrate C`

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

1. **ONE phase per turn.** Never combine P+A or A+B in one response.
2. **⛔ STOP at each gate.** Present your work, then wait for the user.
3. **Never skip A.** Even simple plans must be audited.
4. **Workers are READ-ONLY.** They verify and report — never implement.
5. **You implement in B.** The boss writes all code directly.
6. **Sequential only.** P → A → B → C → D. No skipping, no jumping.
7. **User decides pace.** You advance only when the user says so.
