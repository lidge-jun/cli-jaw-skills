---
name: dev-pabcd
description: |
  PABCD orchestration workflow for structured multi-step development.
  Phases: Plan → Plan Audit → Build → Check → Done.
  Triggers: "orchestrate", "지휘 모드", "pabcd", "orchestration mode"
version: 2.0.0
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

---

## Phase Details

### P — Plan

**Intent**: Force the agent to think before coding. Without this phase, agents jump straight into implementation and miss edge cases, break existing code, or misunderstand requirements.

**Job**:
1. Read structural documentation and dev skill docs first.
2. Write **Part 1**: Easy explanation (non-developer friendly).
3. Write **Part 2**: Diff-level precision — exact file paths (NEW/MODIFY/DELETE), before/after diffs for MODIFY, complete content for NEW.
4. Ask the user:
   - "Any business logic I shouldn't decide alone?"
   - "Does Part 1 match your intent?"

**How to enter P (IDLE → P)**:
- **Trigger word**: User says `orchestrate`, `pabcd`, `지휘 모드`, `오케스트레이션 모드`, or `orchestration mode`
- Inside `orchestrate()` in `pipeline.ts`:
```typescript
// shouldAutoActivatePABCD() matches trigger patterns
if (state === 'IDLE' && shouldAutoActivatePABCD(userText, meta)) {
    setState('P', { originalPrompt: userText, plan: null, workerResults: [], origin, chatId });
    state = 'P';
    prompt = `${getStatePrompt('P')}\n\nUser request:\n${userText}`;
}
```
- **CLI**: `jaw orchestrate P` → `PUT /api/orchestrate/state {state:"P"}` → `setState('P', {originalPrompt:'', plan:null, workerResults:[], origin:'api'})`
- **API**: `PUT /api/orchestrate/state {state:"P"}` directly

**How to transition → A**:
- **User approval**: User says approval keyword → `isApproveIntent()` triggers `AUTO_APPROVE_NEXT[P] → A`
- **CLI**: `jaw orchestrate A`
- **API**: `PUT /api/orchestrate/state {state:"A"}`

⛔ **STOP**. Wait for user approval. Revise if the user gives feedback.

---

### A — Plan Audit

**Intent**: Catch integration bugs BEFORE writing code. Plans often contain hallucinated imports, wrong function signatures, or files that don't exist. An independent worker agent reads the plan and verifies it against the actual codebase.

**Why not skip**: Even simple plans can reference non-existent paths. The cost of auditing is far less than the cost of implementing a broken plan and rolling back.

**Job**:
1. Output a worker JSON to spawn a **read-only** audit worker:
```json
{"subtasks":[{"agent":"Data","task":"⛔ READ-ONLY. Audit the PLAN (not code). Verify: 1) All imports resolve to real files. 2) Function signatures match actual code. 3) No integration risks. Report PASS or FAIL with itemized issues. ⛔ Do NOT touch any files.","priority":1}]}
```
2. System detects subtask JSON via `parseSubtasks(result.text)` in `orchestrate()`.
3. System finds matching employee via `findEmployee()` (3-tier: exact → case-insensitive → fuzzy).
4. System spawns worker via `runSingleAgent()` with phase=2 (`PABCD_PHASE_MAP[A]=2`).
5. Worker result is fed back to main agent via `orchestrate(wResult.text, {_workerResult: true})`.
6. Main agent receives result with prefix `[PLAN AUDIT — Worker Results]` (from `getPrefix('A', 'worker')`).
7. If FAIL → fix plan → re-audit (output worker JSON again).
8. If PASS → report to user.

**How to transition → B**:
- **User approval**: `isApproveIntent()` → `AUTO_APPROVE_NEXT[A] → B`
- **CLI**: `jaw orchestrate B`
- **API**: `PUT /api/orchestrate/state {state:"B"}`

⛔ **STOP**. Wait for user approval.

---

### B — Build

**Intent**: The Boss agent implements the code directly. Workers are **verifiers only** — they check the Boss's work but never write code themselves. This prevents conflicting edits and ensures one coherent implementation.

**Job**:
1. Read the approved, audited plan.
2. **YOU implement ALL changes** — create/modify/delete files as specified.
3. After finishing, output a worker JSON for **read-only verification**:
```json
{"subtasks":[{"agent":"Data","task":"⛔ READ-ONLY. Verify: 1) Files exist with expected content. 2) No syntax errors (tsc --noEmit if TS). 3) Imports resolve. 4) No integration conflicts. Report DONE or NEEDS_FIX. ⛔ Do NOT touch any files.","priority":1}]}
```
4. System spawns verification worker with phase=3 (`PABCD_PHASE_MAP[B]=3`).
5. Worker result fed back with prefix `[IMPLEMENTATION REVIEW — Worker Results]`.
6. If NEEDS_FIX → **you** fix the issues, then re-verify.
7. If DONE → report to user.

**How to transition → C**:
- **User approval**: `isApproveIntent()` → `AUTO_APPROVE_NEXT[B] → C`
- **CLI**: `jaw orchestrate C`
- **API**: `PUT /api/orchestrate/state {state:"C"}`

⛔ **STOP**. Wait for user approval.

---

### C — Check

**Intent**: Final sanity check after implementation.

**Job**:
1. Verify all files saved and consistent.
2. Run `npx tsc --noEmit` for build verification (if TypeScript).
3. Update project structure docs if applicable.
4. Report completion summary.

**How to transition → D**:
- **CLI**: `jaw orchestrate D`
- **API**: `PUT /api/orchestrate/state {state:"D"}` → `setState('D')` then `resetState()` (auto IDLE)
- Automatic after Check completes.

---

### D — Done

**Intent**: Clean closure with structured summary.

**Job**: Summarize P/A/B/C results, list files changed, note follow-ups.

**Transition**: State returns to IDLE automatically.

---

## Transition Mechanisms

### 1. Auto-Advance via Approval Intent (primary)

Inside `orchestrate()` in `pipeline.ts`:

```typescript
const AUTO_APPROVE_NEXT = { P: 'A', A: 'B', B: 'C' };

// When user message is an approval during active PABCD:
if (state !== 'IDLE' && !meta._workerResult && isApproveIntent(userText)) {
    const next = AUTO_APPROVE_NEXT[state];
    if (next) {
        setState(next);  // DB update + broadcast('orc_state')
        prompt = `${getStatePrompt(next)}\n\nUser approval:\n${userText}`;
    }
}
```

`isApproveIntent()` recognizes: `ok`, `okay`, `lgtm`, `approved`, `go`, `next`, `proceed`, `확인`, `좋아`, `진행`, `넘어가`, `다음 단계`, `ㅇㅋ`, `ㄱㄱ`

### 2. CLI Command

```bash
jaw orchestrate B    # transition to Build phase
jaw orchestrate A    # transition to Plan Audit phase
```

Internally calls:
```typescript
// bin/commands/orchestrate.ts
fetch(`http://localhost:${PORT}/api/orchestrate/state`, {
    method: 'PUT',
    body: JSON.stringify({ state: target }),  // "B"
});
```

### 3. REST API

```
PUT /api/orchestrate/state  {state: "B"}
```

Server handler (`server.ts`):
```typescript
app.put('/api/orchestrate/state', (req, res) => {
    const target = String(req.body?.state || '').toUpperCase();
    if (!canTransition(current, target)) {
        return fail(res, 409, `Cannot transition: ${current} → ${target}`);
    }
    if (target === 'D') { setState(target); resetState(); }  // D auto-resets to IDLE
    else { setState(target, target === 'P' ? { originalPrompt: '', plan: null, workerResults: [], origin: 'api' } : undefined); }
});
```

### 4. Worker Dispatch (automatic, within A and B)

When agent output contains subtask JSON during active PABCD:
```typescript
// pipeline.ts orchestrate()
const workerTasks = parseSubtasks(result.text);
if (workerTasks?.length && state !== 'IDLE') {
    const PABCD_PHASE_MAP = { A: 2, B: 3, C: 4 };
    for (const wt of workerTasks) {
        const emp = findEmployee(getEmployees.all(), wt);
        upsertEmployeeSession.run(emp.id, null, emp.cli);  // fresh session
        const wResult = await runSingleAgent(wt_profile, emp, ...);
        // Feed result BACK to main agent with _workerResult flag
        await orchestrate(wResult.text, { ...meta, _skipClear: true, _workerResult: true });
    }
}
```

### 5. Reset and Continue

```typescript
// Reset: user says "리셋", "초기화", "reset"
orchestrateReset()  // → clearAllEmployeeSessions + resetState() + worklog 'reset'
// CLI: jaw orchestrate reset  |  API: POST /api/orchestrate/reset

// Continue: user says "이어서 해줘", "계속", "continue"
orchestrateContinue()  // → resume from current state or last incomplete worklog
// API: POST /api/orchestrate/continue
```

---

## PABCD Activation

The user says one of the trigger words, matched by `shouldAutoActivatePABCD()`:
```typescript
const PABCD_ACTIVATE_PATTERNS = [
    /^\/?orchestrate$/i, /^\/?pabcd$/i, /^지휘\s*모드$/i,
    /^오케스트레이션(?:\s*모드)?$/i, /^orchestration(?:\s*mode)?$/i,
];
```

This auto-transitions IDLE → P and injects the P state prompt.

## Prefix System

`getPrefix(state, source)` in `state-machine.ts`:
- **P + user message** → `[PLANNING MODE — User Feedback]` + revision instructions
- **A + worker result** → `[PLAN AUDIT — Worker Results]` + PASS/FAIL handling
- **B + worker result** → `[IMPLEMENTATION REVIEW — Worker Results]` + DONE/NEEDS_FIX
- **B + user message** → *(no prefix — user feedback passed raw)*

## Critical Rules

1. **ONE phase per turn.** Never do P+A or A+B in the same response.
2. **⛔ STOP at phase end.** Present output, then WAIT for user.
3. **Never skip A.** Every plan must be audited.
4. **Workers are READ-ONLY.** They verify and report — never create/modify/delete files.
5. **Boss implements in B.** The main agent writes all code directly.
6. **User is the gatekeeper.** Only advance on explicit approval.

## Constraints

- ≤ 500 lines per source file
- All prompts in English
- Worker agents do NOT output subtask JSON (recursion prevention)
- State persisted in SQLite (`jaw.db` → `orc_state` table)
- Source: `src/orchestrator/{pipeline,state-machine,distribute,parser,gateway,collect}.ts`
- CLI command: `bin/commands/orchestrate.ts`
