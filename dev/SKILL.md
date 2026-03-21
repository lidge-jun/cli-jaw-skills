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
| `dev-backend/SKILL.md`       | `role=backend`                    | API design, architecture patterns, database optimization, error handling, middleware            |
| `dev-data/SKILL.md`          | `role=data`                       | Data pipelines, ETL/ELT, data quality validation, SQL optimization, analysis & reporting       |
| `dev-security/SKILL.md`      | Security-sensitive code, `role=security` | OWASP Top 10, auth hardening, input validation, secrets management, supply chain security |
| `dev-testing/SKILL.md`       | `role=testing` or testing phase   | Test strategy, Playwright browser testing, coverage analysis, contract testing                 |
| `dev-debugging/SKILL.md`     | Debugging phase (phase 4)         | Root cause analysis, boundary instrumentation, hypothesis testing, postmortem                  |
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
- ES Module (`import`/`export`) only in JS/TS projects. No CommonJS `require()`.
- One default export per file when the file has a primary purpose (JS/TS convention; other languages follow their idioms).
- Follow existing naming conventions in the project. Check sibling files before creating new ones.
- New files must match the directory structure and naming patterns already in use.

---

## 2. Systematic Debugging

**The Iron Law:** NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.

For full debugging methodology — boundary instrumentation, pattern analysis, hypothesis testing, and postmortem — see `dev-debugging/SKILL.md`.

This section retains only the **emergency stop triggers** that every agent must internalize:

**Red flags — stop and return to root cause investigation:**

| Rationalization                                | Reality                                                 |
| ---------------------------------------------- | ------------------------------------------------------- |
| "Quick fix for now, investigate later"         | First fix sets the pattern. Do it right from the start. |
| "Just try changing X and see"                  | Guessing guarantees rework.                             |
| "I don't fully understand but this might work" | Seeing symptoms ≠ understanding root cause.             |
| "Proposing solutions before investigating"     | You haven't done Phase 1.                               |
| "One more fix attempt" (after 2+ failures)     | 3+ failures = architectural problem.                    |

**If 3+ fix attempts fail:** STOP. Each fix revealing a new problem in a different place is a sign of **architectural issues**, not simple bugs. Question fundamentals: Is this pattern sound? Are we sticking with it through inertia? Discuss with your human partner before attempting more fixes.

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
- **Error handling is mandatory** — all async failures must be handled explicitly. No silent failures. In JS/TS backend code, the Result pattern (`neverthrow`) may replace per-call `try/catch` when failures are surfaced at a verified boundary (see `dev-backend/SKILL.md` §3). In all other cases, use `try/catch` and log with context (`console.error('[module]', error.message)`).
- **No destructive operations without confirmation** — deleting files, dropping tables, resetting state, or clearing caches require explicit user approval.

---

## 6. Code Quality Signals

Watch for these anti-patterns and fix immediately. For the full detection catalog and review-specific guidance, see `dev-code-reviewer/SKILL.md` §3.

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

## 8. Token Budget Awareness

When multiple skills are injected simultaneously (e.g., `dev` + `dev-backend` + `dev-security`), token consumption grows quickly. Follow these rules to stay efficient:

**Tiered reference loading:**
1. **Always read**: SKILL.md files for injected skills (these are the orchestrators)
2. **Read on demand**: Reference files (`references/`) — only load when the task touches that specific topic
3. **Never preload all references** — a backend task about caching doesn't need `streaming.md`

**Example:** For "Add Redis caching to user endpoint":
- Read: `dev/SKILL.md` + `dev-backend/SKILL.md` + `dev-backend/references/core/caching.md`
- Skip: `api-design.md`, `architecture.md`, `observability.md`, `database.md` (unless the task touches those areas)

**Cost awareness for sub-agents:** Each sub-agent receives its own copy of injected skills. Minimize skills injected per sub-agent — give only what's needed for that specific sub-task.

---

Write code you'd be proud to debug six months from now. Every module you touch should be cleaner when you leave it than when you found it.
