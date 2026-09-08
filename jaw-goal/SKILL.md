---
name: jaw-goal
description: "Goal execution guidelines with PABCD integration, verification tiers, documentation workflow, and AI-driven planning"
keywords: [goal, plan, objective, verification, pabcd, orchestration]
triggers: [/goal plan, goal-driven work, goal execution]
metadata:
  openclaw:
    emoji: "🎯"
---

# Goal Execution Skill

Guidelines for AI-driven goal work within cli-jaw. Applies when a goal is active via `/goal` or `cli-jaw goal set`, and especially when using `/goal plan` for AI-driven goal formulation.

## Two Modes

### Mode 1: Direct Goal (`/goal "objective"`)

User provides the objective directly. AI executes following these guidelines. The objective is taken verbatim as the goal.

### Mode 2: AI-Planned Goal (`/goal plan "objective"`)

AI analyzes the user's intent and formulates a specific, long-term executable goal. The user's input is a direction, not the final objective.

**Planning Process (fully autonomous — no user confirmation step):**

1. **Context Scan**: Read project docs (README, CLAUDE.md, structure/, devlog/), recent git history, and relevant source code
2. **Scope Analysis**: What does the objective mean in this specific codebase? What subsystems are affected?
3. **Dependency Map**: What existing modules, APIs, data flows, or external services are involved?
4. **Risk Assessment**: What could go wrong? Integration risks? Breaking changes? Performance impact?
5. **Sub-goal Decomposition**: Break into PABCD-compatible work units, each independently verifiable
6. **Execution Plan**: Formulate a specific, measurable goal with clear completion criteria
7. **Refine & Execute**: Immediately refine the goal objective via API and enter PABCD autonomously

## Core Guidelines

### 1. PABCD Integration

Every goal should be executable through the P-A-B-C-D orchestration cycle:
- **P (Plan)**: Write a complete plan with diff-level precision
- **A (Audit)**: Dispatch an employee to audit the plan against real code
- **B (Build)**: Implement the plan; dispatch verification employees
- **C (Check)**: Final sanity check (tsc, consistency, structure docs)
- **D (Done)**: Summarize and return to IDLE

When a goal is active, it supersedes PABCD phase gates for autonomous execution. Phase transitions are mandatory shell commands (`cli-jaw orchestrate A/B/C/D`), not status text. "Supersedes gates" means no user wait — it does NOT mean skip P/A/B/C/D or merge work-phases into B. The evidence attestation (`--attest`) is still required in goal mode: it is proof-of-work, not a user-approval wait, so each forward transition must carry a real `{"from","to","did"}` (C→D also `checkOutput`/`exitCode`).

**Multi-phase / loop goals**: each sub-goal / work-phase = one FULL PABCD cycle (P→A→B→C→D). After D (state → IDLE), run `cli-jaw orchestrate P` to start the next work-phase; repeat until the objective is met. Never run B for several work-phases back-to-back. A "loop"/"루프" goal is multi-pass: pre-plan the full slice map and WRITE all per-phase decade docs to diff-level up front (DIFFLEVEL-ROADMAP-01) — scaffolding empty stubs is not pre-planning. It may open with a design-only PABCD pass (Phase 0) before the first implementation work-phase. Faithfully execute each PABCD-phase — never rubber-stamp a phase to advance.

### 2. Documentation Workflow

Documentation is required throughout the goal lifecycle:

- **Planning**: Create devlog entries at `devlog/_plan/<YYMMDD_topic>/` using decade numbering:
  - 00-09: Research, specs, analysis (mandatory)
  - 10-19: Phase 1 artifacts
  - 20-29: Phase 2 artifacts
  - 30+: Additional phases
- **Progress**: Use `cli-jaw goal update "<summary>" --evidence "<path>"` at every milestone
- **Bug tracking**: Document bugs and fixes explicitly in devlog entries
- **Phase evidence**: Every PABCD phase must produce documentation evidence (devlog path or structure update)

### 3. Commit Discipline

- Small, atomic commits after each logical change
- Never batch multiple unrelated changes into one commit
- Each commit must be self-contained and independently reversible
- Commit messages should explain WHY, not WHAT
- Do not commit generated files, secrets, or temporary state

### 4. Verification Process

Scale verification effort to change complexity (adapted from harness verification-tiers pattern):

| Tier | Criteria | Who Verifies | Evidence Required |
|------|----------|--------------|-------------------|
| **LIGHT** | <5 files, <100 lines changed | CLI sub-agent | LSP diagnostics clean |
| **STANDARD** | Default for mid-size changes | jaw employee dispatch | Diagnostics + build pass |
| **THOROUGH** | >20 files OR security/architectural changes | jaw employee (full review) | All tests pass + independent code review |

**Tier Selection Logic:**
- Security-related changes (auth, credentials, tokens, permissions) -> always THOROUGH
- Architectural changes (config, schema, types, package.json) -> always THOROUGH
- Explicit user request ("careful", "thorough", "critical") -> THOROUGH
- Small isolated fixes with full test coverage -> LIGHT
- Everything else -> STANDARD

**Override Triggers:**
- User says "quick", "simple", "trivial" -> LIGHT
- User says "thorough", "careful", "important" -> THOROUGH

### 5. Sub-agent/Employee Verification Mandates

- **Before claiming any phase completion**, dispatch independent verification
- Verification is NOT an approval gate: dispatch -> receive result -> act immediately
- Independent reviewers must challenge completion claims, not rubber-stamp
- Evidence must be authoritative: file paths, command output, test results, runtime behavior
- If verification finds issues, fix them and re-verify; do not skip

### 6. Quality Gates

Adapted from the ultragoal pattern:

- **No placeholder evidence**: Reject any evidence containing "todo", "tbd", "stub", "not implemented", or "fake pass"
- **Artifact paths required**: Every validation summary must include concrete file paths
- **Evidence triple required for completion**: Documentation evidence + Implementation evidence + Verification evidence
- **Independent review for final completion**: Dispatch a separate reviewer to challenge whether all requirements are truly met
- **Treat completion as unproven**: Default to "not done" until evidence proves otherwise

### 7. When Blocked

- Try alternative approaches before declaring blocked
- If genuinely blocked (need auth, hardware, human business decision):
  1. Record all progress with `cli-jaw goal update`
  2. Dispatch independent reviewer to confirm no viable path remains
  3. Pause with audit: `cli-jaw goal pause --agent --audit "<review summary>"`
- Never declare blocked merely because work is hard, slow, or uncertain
- Never auto-complete a goal; completion is reserved for explicit user request or verified evidence

## Steer Prompt Templates

### Direct Goal Steer
```
[System] User set a new goal: "<objective>" (ID: <id>). Acknowledge the goal and help the user achieve it.
```

### Plan Goal Steer
```
[System] User requested AI-driven goal planning: "<objective>" (ID: <id>).
Do NOT execute the objective directly. First ANALYZE, then EXECUTE AUTONOMOUSLY:
1. Context Scan -> 2. Scope Analysis -> 3. Dependency Map -> 4. Risk Assessment -> 5. Sub-goal Decomposition -> 6. Execution Plan
After analysis, immediately refine the goal objective and enter PABCD orchestration.
Do NOT wait for user confirmation. Execute the full goal autonomously.
```
