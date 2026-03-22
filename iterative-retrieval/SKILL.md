---
name: iterative-retrieval
description: Pattern for progressively refining context retrieval in multi-agent workflows.
---

# Iterative Retrieval Pattern

Solves the "context problem" in multi-agent workflows where sub-agents cannot predict what context they need until they start working.

## When to Use

- Spawning sub-agents that need codebase context they cannot predict upfront
- Building multi-agent workflows where context is progressively refined
- Encountering "context too large" or "missing context" failures in agent tasks
- Optimizing token usage in agent orchestration

## The Problem

Sub-agents are spawned with limited context. They lack knowledge of which files are relevant, what patterns exist, or what terminology the project uses.

Standard approaches fail:
- **Send everything**: exceeds context limits
- **Send nothing**: agent lacks critical information
- **Guess what's needed**: often wrong

## The Solution: Iterative Retrieval

A 4-phase loop that progressively refines context (max 3 cycles):

```
┌───────────────────────────────────────┐
│  DISPATCH → EVALUATE → REFINE → LOOP │
│       ▲                    │          │
│       └────────────────────┘          │
│       Max 3 cycles, then proceed      │
└───────────────────────────────────────┘
```

### Phase 1: DISPATCH
Broad initial query to gather candidate files:
- Start with high-level intent patterns (`src/**/*.ts`)
- Use domain keywords (`authentication`, `user`, `session`)
- Exclude test files

### Phase 2: EVALUATE
Score each retrieved file for relevance (0–1):
- **High (0.7–1.0)**: directly implements target functionality
- **Medium (0.5–0.7)**: contains related patterns or types
- **Low (< 0.5)**: tangentially related or irrelevant
- Identify what context is still missing

### Phase 3: REFINE
Update search criteria based on evaluation:
- Add new patterns discovered in high-relevance files
- Add terminology found in the codebase
- Exclude confirmed irrelevant paths
- Target specific gaps

### Phase 4: LOOP
Repeat with refined criteria. Stop when:
- 3+ files score ≥ 0.7 with no critical gaps, or
- Max cycles (3) reached

## Practical Examples

### Bug Fix Context
```
Task: "Fix the authentication token expiry bug"

Cycle 1:
  DISPATCH: Search for "token", "auth", "expiry" in src/**
  EVALUATE: Found auth.ts (0.9), tokens.ts (0.8), user.ts (0.3)
  REFINE: Add "refresh", "jwt" keywords; exclude user.ts

Cycle 2:
  DISPATCH: Search refined terms
  EVALUATE: Found session-manager.ts (0.95), jwt-utils.ts (0.85)
  → Sufficient context (4 high-relevance files)
```

### Feature Implementation
```
Task: "Add rate limiting to API endpoints"

Cycle 1:
  DISPATCH: Search "rate", "limit", "api" in routes/**
  EVALUATE: No matches — codebase uses "throttle" terminology
  REFINE: Add "throttle", "middleware" keywords

Cycle 2:
  DISPATCH: Search refined terms
  EVALUATE: Found throttle.ts (0.9), middleware/index.ts (0.7)
  REFINE: Need router patterns

Cycle 3:
  DISPATCH: Search "router", "express" patterns
  EVALUATE: Found router-setup.ts (0.8)
  → Sufficient context
```

## Agent Prompt Template

```markdown
When retrieving context for this task:
1. Start with broad keyword search
2. Evaluate each file's relevance (0–1 scale)
3. Identify what context is still missing
4. Refine search criteria and repeat (max 3 cycles)
5. Return files with relevance ≥ 0.7
```

## Best Practices

1. **Start broad, narrow progressively** — initial queries should be exploratory
2. **Learn codebase terminology** — first cycle often reveals naming conventions
3. **Track what's missing** — explicit gap identification drives refinement
4. **Stop at "good enough"** — 3 high-relevance files beat 10 mediocre ones
5. **Exclude confidently** — low-relevance files rarely become relevant

## Related Skills

- `continuous-learning` — for patterns that improve over time
