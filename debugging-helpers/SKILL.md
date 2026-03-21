---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# Systematic Debugging

Find root cause before attempting fixes. Symptom fixes mask underlying issues and waste time.

## The Four Phases

Complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

Before attempting any fix:

1. **Read error messages carefully**
   - Read stack traces completely — they often contain the exact solution
   - Note line numbers, file paths, error codes

2. **Reproduce consistently**
   - Identify exact steps to trigger reliably
   - If not reproducible, gather more data before forming hypotheses

3. **Check recent changes**
   - Git diff, recent commits, new dependencies, config changes
   - Environmental differences

4. **Gather evidence in multi-component systems**

   When a system has multiple components (CI → build → signing, API → service → database), add diagnostic instrumentation before proposing fixes:

   ```
   For each component boundary:
     - Log what data enters and exits the component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   Then investigate that specific component
   ```

   Example (multi-layer system):
   ```bash
   # Layer 1: Workflow
   echo "=== Secrets available: ==="
   echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"

   # Layer 2: Build script
   env | grep IDENTITY || echo "IDENTITY not in environment"

   # Layer 3: Signing
   security find-identity -v

   # Layer 4: Actual signing
   codesign --sign "$IDENTITY" --verbose=4 "$APP"
   ```

5. **Trace data flow**

   See `root-cause-tracing.md` for the complete backward tracing technique.

   Quick version:
   - Where does the bad value originate?
   - What called this with the bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom

### Phase 2: Pattern Analysis

1. **Find working examples** — locate similar working code in the same codebase
2. **Compare against references** — read reference implementations completely before applying
3. **Identify differences** — list every difference between working and broken, however small
4. **Understand dependencies** — what components, settings, config, or assumptions are involved?

### Phase 3: Hypothesis and Testing

1. **Form a single hypothesis** — state clearly: "I think X is the root cause because Y"
2. **Test minimally** — make the smallest possible change to test the hypothesis; one variable at a time
3. **Verify before continuing** — if it worked, proceed to Phase 4; if not, form a new hypothesis (avoid stacking fixes)

### Phase 4: Implementation

1. **Create a failing test case** — simplest possible reproduction, automated if feasible
2. **Implement a single fix** — address root cause only; no "while I'm here" improvements
3. **Verify the fix** — test passes, no other tests broken, issue actually resolved

4. **If the fix fails** — count attempts:
   - < 3 attempts: return to Phase 1, re-analyze with new information
   - ≥ 3 attempts: stop and question the architecture (see below)

5. **If 3+ fixes failed: question architecture**

   Pattern indicating architectural problems:
   - Each fix reveals new shared state / coupling / problem in a different place
   - Fixes require massive refactoring to implement
   - Each fix creates new symptoms elsewhere

   Stop and question fundamentals:
   - Is this pattern fundamentally sound?
   - Should we refactor architecture vs. continue fixing symptoms?

   Discuss with the human before attempting more fixes.

## Signs You Should Return to Phase 1

If any of these apply, pause and re-investigate before continuing:

- Attempting a fix without understanding the root cause
- Skipping reproduction or test verification
- Stacking multiple speculative changes
- On the 3rd+ fix attempt without new evidence
- Proposing solutions before tracing data flow

## Supporting Techniques

Available in this directory:

- **`root-cause-tracing.md`** — trace bugs backward through call stack to find original trigger
- **`defense-in-depth.md`** — add validation at multiple layers after finding root cause
- **`condition-based-waiting.md`** — replace arbitrary timeouts with condition polling

Related skills:
- **tdd** — for creating failing test cases (Phase 4)
- **dev-testing** — verify fix worked before claiming success

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| 1. Root Cause | Read errors, reproduce, check changes, gather evidence | Understand what and why |
| 2. Pattern | Find working examples, compare | Identify differences |
| 3. Hypothesis | Form theory, test minimally | Confirmed or new hypothesis |
| 4. Implementation | Create test, fix, verify | Bug resolved, tests pass |
