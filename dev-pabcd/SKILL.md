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

Read project docs and dev skills first. Write a plan with two parts:
- **Part 1**: Easy explanation — what will be built, in non-developer terms.
- **Part 2**: Diff-level precision — exact file paths (NEW/MODIFY/DELETE), before/after diffs for MODIFY, complete content for NEW.

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

Output worker JSON for the audit. Review results when they come back.
- If FAIL → fix the plan → output worker JSON again to re-audit
- If PASS → report results to the user

⛔ Wait for user approval. When approved → `cli-jaw orchestrate B`

### B — Build
Implement the plan. You write all code directly. Workers are read-only verifiers.

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
