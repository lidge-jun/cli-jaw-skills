---
name: verification-loop
description: Multi-phase verification system for code changes — build, types, lint, tests, security, diff.
---

# Verification Loop

Systematic quality check for code changes across six phases.

## When to Use

- After completing a feature or significant code change
- Before creating a PR
- After refactoring
- When quality gates need confirmation

## Verification Phases

### Phase 1: Build
```bash
npm run build 2>&1 | tail -20
# or: pnpm build, cargo build, go build, etc.
```
Fix build failures before continuing to Phase 2.

### Phase 2: Type Check
```bash
# TypeScript
npx tsc --noEmit 2>&1 | head -30

# Python
pyright . 2>&1 | head -30
```

### Phase 3: Lint
```bash
# JS/TS
npm run lint 2>&1 | head -30

# Python
ruff check . 2>&1 | head -30
```

### Phase 4: Tests
```bash
npm run test -- --coverage 2>&1 | tail -50
```
Report: total, passed, failed, coverage %.

### Phase 5: Security Scan
```bash
grep -rn "sk-\|api_key\|SECRET" --include="*.ts" --include="*.js" . 2>/dev/null | head -10
```

### Phase 6: Diff Review
```bash
git diff --stat
git diff HEAD~1 --name-only
```
Review each changed file for unintended changes, missing error handling, edge cases.

## Report Format

```
Verification Report
===================
Build:     [PASS/FAIL]
Types:     [PASS/FAIL] (X errors)
Lint:      [PASS/FAIL] (X warnings)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (X issues)
Diff:      [X files changed]

Overall:   [READY / NOT READY] for PR

Issues:
1. ...
```

## Checkpoints

Run verification at natural boundaries:
- After completing each function or component
- Before moving to the next task
- Every ~15 minutes in long sessions

Hooks catch issues at write-time; this skill provides comprehensive review at phase boundaries.
