---
name: continuous-agent-loop
description: Patterns for continuous autonomous agent loops with quality gates, evaluations, and recovery controls.
---

# Continuous Agent Loop

Patterns for structuring long-running agent workflows with loop selection, quality gates, and failure recovery.

## Loop Selection

```text
Start
  |
  +-- Need strict CI/PR control?           --> continuous-pr loop
  |
  +-- Need task decomposition from spec?   --> DAG-based loop
  |
  +-- Need exploratory parallel generation? --> infinite loop
  |
  +-- default                              --> sequential loop
```

## Recommended Production Stack

1. Task decomposition from spec or RFC
2. Quality gates (lint, test, type-check between iterations)
3. Evaluation harness (automated acceptance checks)
4. Session persistence (resume after interruption)

## Failure Modes

- Loop churn without measurable progress
- Repeated retries with the same root cause
- Merge queue stalls from conflicting changes
- Cost drift from unbounded model escalation

## Recovery

1. Freeze the loop
2. Audit recent iterations for root cause
3. Reduce scope to the failing unit
4. Replay with explicit acceptance criteria
