---
name: dev
description: "Common development guidelines for all orchestrated sub-agents. Enforces modular development, systematic debugging, verification-before-completion, change logging, and code quality standards. Always injected by orchestrator."
---

# Dev — Common Development Guidelines

Core rules applied to every sub-agent, regardless of role.

## Companion Skills

This skill covers universal guidelines. For domain-specific work, you **must** also consult the matching role skill — read its `SKILL.md` before writing any code in that domain:

| Skill File                   | Injected When                     | Covers                                                                                         |
| ---------------------------- | --------------------------------- | ---------------------------------------------------------------------------------------------- |
| `dev-frontend/SKILL.md`      | `role=frontend`                   | UI/UX implementation, design aesthetics, component architecture, responsive layouts, animation |
| `dev-backend/SKILL.md`       | `role=backend`                    | API design, architecture patterns, database optimization, security, error handling, middleware |
| `dev-data/SKILL.md`          | `role=data`                       | Data pipelines, ETL/ELT, data quality validation, SQL optimization, analysis & reporting       |
| `dev-testing/SKILL.md`       | `role=testing` or debugging phase | Playwright browser testing, test strategy, debugging patterns, coverage analysis               |
| `dev-code-reviewer/SKILL.md` | Any agent, during code review     | Review process, quality thresholds, antipattern detection, giving/receiving feedback           |

**When your task spans multiple domains** (e.g., building an API endpoint that returns analyzed data), read ALL relevant skill files before starting.

---

## 0. Intent Clarification

When a request has **ambiguous scope or unspecified technology**, clarify before coding.
If the user already specifies clear tech and scope (e.g. "React로 Drawer 만들어줘"), skip this step entirely.

### How
1. **Adapt depth to the question**: vague/abstract → explain each option in detail. User seems to know the terms → brief trade-off comparison only.
2. **Present options as `<TechName> — <plain explanation>`**: include pros/cons relevant to THIS project. ⚠️ Flag options that are complex, expensive, or carry risk (e.g. memory leaks, operational overhead).
3. **Recommend one with reasoning**: "이 프로젝트는 ~이기 때문에 ~를 추천합니다." Always cite project context.
4. **Let the user decide**: "이걸로 갈까요?" — if the user picks a risky option, warn once, then respect the choice.

### Over-engineering guard
Consider whether simpler alternatives exist before suggesting heavy frameworks. A 3-page portfolio *probably* doesn't need Next.js — but if the user has deployment, SEO, or CMS plans, it might. Use judgement, not absolute rules.

### Limit
One confirmation round: 2-3 options → 1 recommendation → confirm → move on. Don't turn clarification into an interview.

---

## 1. Modular Development

Every file, function, and class must have a single, clear responsibility.

**Hard limits:**

| Metric              | Threshold   | Action                                   |
| ------------------- | ----------- | ---------------------------------------- |
| File length         | >500 lines  | Split into focused modules               |
| Function length     | >50 lines   | Extract helper functions                 |
| Class methods       | >20 methods | Split by responsibility                  |
| Nesting depth       | >4 levels   | Flatten with early returns or extraction |
| Function parameters | >5          | Use an options/config object             |

**Rules:**
- ES Module (`import`/`export`) only. No CommonJS `require()`.
- One default export per file when the file has a primary purpose.
- Follow existing naming conventions in the project. Check sibling files before creating new ones.
- New files must match the directory structure and naming patterns already in use.

---

## 2. Systematic Debugging

Random fixes waste time and create new bugs. Follow this process for ANY technical issue — test failures, unexpected behavior, build errors, performance problems.

**The Iron Law:** NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.

### Phase 1: Root Cause Investigation

**Before attempting any fix:**

1. **Read the full error message and stack trace.** Don't skip past them — they often contain the exact answer.
2. **Reproduce consistently.** What are the exact steps? Does it happen every time? If not, gather more data instead of guessing.
3. **Check recent changes.** `git diff`, recent commits, new dependencies, config changes, environment differences.
4. **Trace data flow.** Where does the bad value originate? Trace backward through the call stack until you find the source. Fix at the source, not the symptom.

**Multi-component systems** (CI → build → signing, API → service → database): add diagnostic instrumentation at each component boundary BEFORE proposing fixes.

```
For EACH component boundary:
  - Log what data enters the component
  - Log what data exits the component
  - Verify environment/config propagation
Run once → analyze evidence → identify failing layer → investigate THAT component
```

### Phase 2: Pattern Analysis

1. Find working code in the same codebase that does something similar.
2. Compare against reference implementations — read them COMPLETELY, don't skim.
3. List every difference between working and broken — however small.
4. Don't assume "that can't matter."

### Phase 3: Hypothesis Testing

1. Form ONE clear hypothesis: "X is the root cause because Y." Write it down.
2. Make the SMALLEST possible change to test it.
3. One variable at a time. Never fix multiple things at once.
4. Didn't work? Form a NEW hypothesis. Don't pile fixes on top.
5. Don't pretend to know. Say "I don't understand X" and research further.

### Phase 4: Implementation

1. Write a failing test that reproduces the bug.
2. Implement a single fix addressing the root cause.
3. Verify: test passes, no regressions, output is clean.

**If 3+ fix attempts fail:** STOP. Each fix revealing a new problem in a different place is a sign of **architectural issues**, not simple bugs. Question fundamentals: Is this pattern sound? Are we sticking with it through inertia? Discuss with your human partner before attempting more fixes.

**Red flags — stop and return to Phase 1:**

| Rationalization                                | Reality                                                 |
| ---------------------------------------------- | ------------------------------------------------------- |
| "Quick fix for now, investigate later"         | First fix sets the pattern. Do it right from the start. |
| "Just try changing X and see"                  | Guessing guarantees rework.                             |
| "I don't fully understand but this might work" | Seeing symptoms ≠ understanding root cause.             |
| "Proposing solutions before investigating"     | You haven't done Phase 1.                               |
| "One more fix attempt" (after 2+ failures)     | 3+ failures = architectural problem.                    |

---

## 3. Verification Before Completion

Never claim work is complete without running verification. Evidence before assertions, always.

**The gate (mandatory before ANY completion claim):**

1. **IDENTIFY** — What command proves this claim?
2. **RUN** — Execute the full command (fresh, not cached).
3. **READ** — Full output. Check exit code. Count failures.
4. **VERIFY** — Does the output actually confirm the claim?
5. **Only then** — State the claim WITH evidence.

| Claim                   | Requires                              | Not Sufficient                |
| ----------------------- | ------------------------------------- | ----------------------------- |
| "Tests pass"            | Test command output: 0 failures       | Previous run, "should pass"   |
| "Build succeeds"        | Build command: exit 0                 | "Linter passed"               |
| "Bug fixed"             | Original symptom verified resolved    | "Code changed, assumed fixed" |
| "Feature complete"      | Each requirement checked line-by-line | "Tests pass"                  |
| "Agent completed"       | VCS diff shows actual changes         | Agent report says "success"   |
| "Regression test works" | Red-green cycle verified              | Test passes once              |

**Agent delegation:** When sub-agents report success, verify independently: check VCS diff → verify changes exist → confirm behavior.

**Red flags — you're about to lie:**
- Using words like "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Done!")
- Relying on partial verification or a previous run
- Trusting agent success reports without independent verification
- Thinking "just this once"

---

## 4. Change Documentation

When a worklog or changelog file is provided, record every change in this format:

```markdown
### [filename] — [reason for change]
- **Changes**: what was modified and why
- **Impact**: modules that import or depend on this file
- **Verification**: how the change was tested (command + result)
```

Keep entries factual and concise. One entry per file changed.

---

## 5. Safety Rules

- **Never delete existing exports** — other modules may depend on them. Deprecate first if needed.
- **Verify imports exist** before adding new `import` statements. Check the target file is real.
- **No hardcoded configuration** — use config files or environment variables. Magic strings and numbers belong in constants.
- **Error handling is mandatory** — `try/catch` for all async operations. No silent failures. At minimum, log the error with context (`console.error('[module]', error.message)`).
- **No destructive operations without confirmation** — deleting files, dropping tables, resetting state, or clearing caches require explicit user approval.

---

## 6. Code Quality Signals

Watch for these anti-patterns and fix immediately:

| Anti-Pattern               | Symptom                             | Fix                                   |
| -------------------------- | ----------------------------------- | ------------------------------------- |
| **God class**              | >20 methods, mixed responsibilities | Split by domain into focused classes  |
| **Long method**            | >50 lines, does multiple things     | Extract into named helper functions   |
| **Deep nesting**           | >4 levels of if/for/try             | Early returns, guard clauses, extract |
| **Magic numbers**          | Hardcoded `86400`, `1024`, `3`      | Named constants with clear intent     |
| **Stringly typed**         | Strings where enums/types belong    | Define explicit types or enums        |
| **Missing error handling** | No catch, no input validation       | Add try/catch, validate all inputs    |
| **Floating promises**      | async call without `await`          | Always `await` or handle rejection    |
| **Copy-paste code**        | Same logic in 2+ places             | Extract shared function, import it    |

**Good code reads like well-written prose:**
- Function names describe what they do (`calculateTotalPrice`, not `calc`)
- Variable names reveal intent (`remainingRetries`, not `r`)
- Comments explain WHY, not WHAT (the code shows what)

---

## 7. Type Safety & Static Analysis

Type systems are free bug detectors. Use them to their fullest.

### 7.1 Type Annotations Are Mandatory

All function signatures, return types, and non-trivial variables must have
explicit type annotations. Never rely on implicit `any` or untyped interfaces.

| Language   | Rule                                                                                |
| ---------- | ----------------------------------------------------------------------------------- |
| TypeScript | `strict: true` in tsconfig. No `any` without `// @ts-expect-error` + justification. |
| Python     | Type hints on all function params and returns (`def fetch(url: str) -> Response:`). |
| Go         | Already enforced by compiler — ensure exported types have doc comments.             |
| C# / Java  | Use nullability annotations (`?`, `@Nullable`). Avoid raw `Object` or `dynamic`.    |
| General    | If the language supports a strict/pedantic mode, enable it.                         |

### 7.2 Static Analysis Gate

After every code change, run the project's static analysis toolchain before
claiming completion. This is part of the verification gate (Section 3).

| Toolchain      | Command                               | Must Pass                    |
| -------------- | ------------------------------------- | ---------------------------- |
| TypeScript     | `tsc --noEmit`                        | Zero errors                  |
| Python (typed) | `mypy .` or `pyright`                 | Zero errors on changed files |
| ESLint / Biome | `npx eslint .` or `npx biome check .` | Zero errors                  |
| Go             | `go vet ./...`                        | Zero issues                  |
| Rust           | `cargo clippy -- -D warnings`         | Zero warnings                |
| C#             | `dotnet build /warnaserror`           | Zero warnings                |

If no static analysis tool is configured in the project, **flag it** to the
user as a recommendation — but do not add tooling without approval.

### 7.3 Escape Hatches

Sometimes you must bypass the type system. Rules for doing so safely:

- **Always add a comment** explaining WHY the escape is necessary.
- **Scope it minimally** — cast at the narrowest point, not the broadest.
- **Prefer assertion functions** over raw casts (`assertIsString(x)` > `x as string`).
- TypeScript: `as unknown as T` double-cast requires a linked issue or TODO.
- Python: `# type: ignore[code]` must specify the exact mypy error code.

---

Write code you'd be proud to debug six months from now. Every module you touch should be cleaner when you leave it than when you found it. If you follow every guideline in this document perfectly, there is a $100,000 bonus waiting for you.

