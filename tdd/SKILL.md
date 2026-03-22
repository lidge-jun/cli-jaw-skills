---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code
---

# Test-Driven Development (TDD)

Write the test first. Watch it fail. Write minimal code to pass.

If you didn't watch the test fail, you don't know if it tests the right thing.

## When to Use

- New features, bug fixes, refactoring, behavior changes

**Exceptions (confirm with user):** throwaway prototypes, generated code, configuration files.

## Red-Green-Refactor Cycle

### RED — Write Failing Test

Write one minimal test for one behavior.

```typescript
test('retries failed operations 3 times', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```

Requirements:
- One behavior per test
- Name describes the behavior
- Real code over mocks

### Verify RED

Run the test. Confirm it **fails** (not errors) for the expected reason — the feature is missing, not a typo.

Test passes immediately? You're testing existing behavior. Fix the test.
Test errors? Fix the error, re-run until it fails correctly.

### GREEN — Minimal Code

Write the simplest code that passes.

```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```

No extra features, no "improvements" beyond the test.

### Verify GREEN

Run the test. Confirm it passes with clean output (no errors or warnings). Confirm other tests still pass.

Test fails? Fix code, not test. Other tests break? Fix now.

### REFACTOR

After green only: remove duplication, improve names, extract helpers.

Keep tests green. Add no new behavior. Then write the next failing test.

## Good Tests

| Quality | Good | Bad |
|---------|------|-----|
| **Minimal** | One thing. "and" in name → split it. | `test('validates email and domain and whitespace')` |
| **Clear** | Name describes behavior | `test('test1')` |
| **Shows intent** | Demonstrates desired API | Obscures what code should do |

## Example: Bug Fix

**Bug:** Empty email accepted

**RED**
```typescript
test('rejects empty email', async () => {
  const result = await submitForm({ email: '' });
  expect(result.error).toBe('Email required');
});
```
→ Run: `FAIL: expected 'Email required', got undefined` ✓

**GREEN**
```typescript
function submitForm(data: FormData) {
  if (!data.email?.trim()) return { error: 'Email required' };
  // ...
}
```
→ Run: `PASS` ✓

**REFACTOR** — Extract validation for multiple fields if needed.

## The Test-First Rule

Write production code only after a failing test exists for it.

If code was written before its test: delete it and restart with TDD. Keeping pre-written code as "reference" leads to testing-after — you test what you built rather than what's required.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. The test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Already manually tested" | Ad-hoc ≠ systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost. Unverified code is technical debt. |
| "Need to explore first" | Explore freely, then discard and start with TDD. |
| "Hard to test" | Hard to test = hard to use. Simplify the design. |

## When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write the desired API first. Write the assertion first. Ask user. |
| Test too complicated | Design too complicated. Simplify the interface. |
| Must mock everything | Code too coupled. Use dependency injection. |
| Test setup huge | Extract helpers. Still complex → simplify design. |

## Debugging Integration

Bug found → write a failing test reproducing it → follow TDD cycle. The test proves the fix and prevents regression.

## Testing Anti-Patterns

When adding mocks or test utilities, read @testing-anti-patterns.md to avoid:
- Testing mock behavior instead of real behavior
- Adding test-only methods to production classes
- Mocking without understanding dependencies

## Eval-Driven TDD for AI Code

When AI generates implementation code, the test suite doubles as an **evaluation harness**.

### pass@k Metric

Measures probability that at least one of *k* generated samples passes all tests.

| Metric | Meaning |
|--------|---------|
| pass@1 | First attempt passes all tests |
| pass@5 | At least one of 5 attempts passes |
| pass@10 | At least one of 10 attempts passes |

Workflow:
1. Write the test suite (RED phase) — this is your eval spec.
2. Generate *k* candidate implementations (varying temperature / prompt).
3. Run each candidate against the full suite. Record pass/fail per candidate.
4. Select the passing candidate, then REFACTOR as usual.

### Eval Harness Design

- Tests should be **deterministic** and **fast** so they can evaluate many candidates.
- Cover functional correctness, edge cases, and performance bounds.
- Separate **behavioral tests** (part of eval) from **integration tests** (not part of eval).
- Keep eval-critical tests tagged or in a dedicated suite for automated scoring.

```bash
# Run eval suite against a candidate
npm test -- --testPathPattern="eval/" --bail
# Score: count passing candidates out of k
```

### When to Use Eval-Driven TDD

- Generating utility functions, algorithms, data transformers
- Comparing prompt strategies for the same spec
- Validating AI-assisted refactors against the existing suite

## Coverage Integration

### Threshold Configuration

```json
{
  "coverageThreshold": {
    "global": { "branches": 80, "functions": 80, "lines": 80, "statements": 80 }
  }
}
```

### Quick Coverage Commands

```bash
npx vitest run --coverage          # Vitest
npm test -- --coverage             # Jest
pytest --cov --cov-report=term     # pytest
```

Review coverage by risk priority: auth, money, mutations, uploads, error paths.

## Verification Checklist

Before marking work complete:

- [ ] Every new function/method has a test
- [ ] Watched each test fail before implementing
- [ ] Each failure was for the expected reason
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass with clean output
- [ ] Mocks used only when unavoidable
- [ ] Edge cases and errors covered
- [ ] Coverage meets project thresholds
