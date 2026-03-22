---
name: eval-harness
description: Evaluation framework for agent sessions implementing eval-driven development (EDD) principles.
---

# Eval Harness

Evaluation framework for agent-assisted workflows. Define expected behavior before implementation, run evals continuously, and track regressions with pass@k metrics.

## When to Use

- Defining pass/fail criteria for agent task completion
- Measuring agent reliability with pass@k metrics
- Creating regression test suites for prompt or agent changes
- Benchmarking agent performance across model versions

## Eval Types

### Capability Evals
Test whether an agent can accomplish something new:
```markdown
[CAPABILITY EVAL: feature-name]
Task: Description of what the agent should accomplish
Success Criteria:
  - [ ] Criterion 1
  - [ ] Criterion 2
Expected Output: Description of expected result
```

### Regression Evals
Verify existing functionality remains intact:
```markdown
[REGRESSION EVAL: feature-name]
Baseline: SHA or checkpoint name
Tests:
  - existing-test-1: PASS/FAIL
  - existing-test-2: PASS/FAIL
Result: X/Y passed (previously Y/Y)
```

## Grader Types

| Type | Use when | Example |
|------|----------|---------|
| Code grader | Deterministic assertions | `grep -q "export function handleAuth" src/auth.ts` |
| Rule grader | Regex/schema constraints | JSON schema validation, pattern matching |
| Model grader | Open-ended output quality | LLM-as-judge with 1–5 rubric |
| Human grader | Ambiguous or security-sensitive | Manual review with risk level flag |

Prefer code graders where possible — deterministic results are more reliable than probabilistic ones.

## Metrics

### pass@k
"At least one success in k attempts"
- pass@1: First attempt success rate
- pass@3: Success within 3 attempts
- Typical target: pass@3 ≥ 90%

### pass^k
"All k trials succeed"
- pass^3: 3 consecutive successes
- Use for release-critical paths (target: 1.00)

## Eval Workflow

### 1. Define (before coding)
```markdown
## EVAL DEFINITION: feature-xyz

### Capability Evals
1. Can create new user account
2. Can validate email format

### Regression Evals
1. Existing login still works
2. Session management unchanged

### Success Metrics
- pass@3 ≥ 90% for capability evals
- pass^3 = 100% for regression evals
```

### 2. Implement
Write code to pass the defined evals.

### 3. Evaluate
Run each eval, record PASS/FAIL per item.

### 4. Report
```
EVAL REPORT: feature-xyz
========================
Capability:  2/2 passed (pass@3: 100%)
Regression:  2/2 passed (pass^3: 100%)
Overall:     READY FOR REVIEW
```

## Eval Storage

```
evals/
  feature-xyz.md      # Eval definition
  feature-xyz.log     # Run history
  baseline.json       # Regression baselines
```

## Best Practices

1. **Define evals before coding** — forces clear thinking about success criteria
2. **Run evals frequently** — catch regressions early
3. **Track pass@k over time** — monitor reliability trends
4. **Prefer code graders** — deterministic beats probabilistic
5. **Keep human review for security** — security checks benefit from manual judgment
6. **Keep evals fast** — slow evals get skipped
7. **Version evals with code** — evals are first-class artifacts

## Pitfalls

- Overfitting prompts to known eval examples
- Measuring only happy-path outputs
- Ignoring cost and latency drift while chasing pass rates
- Allowing flaky graders in release gates
