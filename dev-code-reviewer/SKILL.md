---
name: dev-code-reviewer
description: "Code review guide for all orchestrated sub-agents. Review process, quality thresholds, antipattern detection, giving/receiving feedback. Available to any agent regardless of role — read this SKILL.md when performing or receiving code reviews."
---

# Dev-Code-Reviewer — Code Review Guide

Systematic code review patterns for finding real issues, not bikeshedding.

## When to Activate

- Reviewing code changes (own or others')
- Receiving code review feedback
- Assessing code quality before merge
- Evaluating pull requests or diffs
- Pre-refactoring quality baseline check

---

## 1. Code Review Process

### Pre-Review Checklist

Before reviewing any code, verify:

- [ ] Build passes (no compile/type errors)
- [ ] Tests pass (all green)
- [ ] PR/diff description explains **what** changed and **why**
- [ ] Diff is reasonable size (<500 changed lines — split larger PRs)

### Automated Pre-Scan (Run Before Manual Review)

Before reading a single line of code, run automated tools on changed files:

```bash
# JavaScript/TypeScript
npx eslint --format compact $(git diff --name-only --diff-filter=ACMR HEAD -- '*.ts' '*.tsx' '*.js' '*.jsx')
npx tsc --noEmit                    # type check only
npm audit --audit-level=high        # dependency vulnerabilities

# Python
ruff check $(git diff --name-only --diff-filter=ACMR HEAD -- '*.py')
mypy src/                           # type check
pip-audit                           # dependency vulnerabilities

# Multi-language security scan
semgrep --config=auto --severity=ERROR $(git diff --name-only --diff-filter=ACMR HEAD)
```

**Pre-Scan Rules:**
1. **Critical/error findings → block review.** Don't waste human review cycles on machine-detectable problems.
2. **Warnings → note for review, don't block.** Mention in review but don't make them blocking.
3. **Tool findings go first** in review output, before manual findings.
4. **No tool available?** Skip gracefully — pre-scan is additive, not a gate.

| Tool | Catches | Misses |
|------|---------|--------|
| ESLint/Ruff | Style, simple bugs, import issues | Architecture, business logic |
| tsc/mypy | Type errors, null safety | Runtime behavior, performance |
| Semgrep | Injection, auth bypass, SSRF | Complex multi-step vulnerabilities |
| npm audit/pip-audit | Known CVEs in deps | Zero-day, license issues |

**Separation of concerns:** Tools catch patterns; humans catch intent. Focus manual review on architecture, correctness, and business logic that tools cannot evaluate.

### Review Order (by impact, not preference)

1. **Architecture** — Does the approach make sense? Right layer? Right abstraction? Is this the right place for this code?
2. **Correctness** — Logic errors, edge cases, off-by-one, null/undefined handling, error paths
3. **Security** — Input validation, injection risks, auth checks, secrets exposure
4. **Performance** — N+1 queries, unbounded collections, missing indexes, unnecessary computation
5. **Maintainability** — Naming, structure, complexity, test coverage, documentation
6. **Style** — Last priority. Don't bikeshed formatting when there are real issues.

### Review Mindset

- **Be specific.** "This could fail" → "This throws if `user` is null on line 42"
- **Suggest, don't demand.** Unless it's a security or correctness issue.
- **Explain why.** Not just "change X to Y" but "X causes N+1 queries because..."
- **Acknowledge good work.** If a complex problem is solved elegantly, say so briefly.

---

## 2. Quality Thresholds

Flag these during review:

| Issue | Threshold | Severity |
|-------|-----------|----------|
| Long function | >50 lines | Medium |
| Large file | >500 lines | Medium |
| God class | >20 methods | High |
| Too many parameters | >5 | Medium |
| Deep nesting | >4 levels | Medium |
| High cyclomatic complexity | >10 branches | High |
| Missing error handling | any unhandled async | High |
| Hardcoded secrets | API keys, passwords in source | **Critical** |
| SQL injection | string concatenation in queries | **Critical** |
| Debug statements | console.log, debugger left in | Low |
| TODO/FIXME | unresolved in production code | Low |
| TypeScript `any` | bypassing type safety | Medium |

### Review Verdict

| Indicator | Verdict | Action |
|-----------|---------|--------|
| No high/critical issues | ✅ Approve | Merge |
| ≤2 high issues, clearly fixable | 🔧 Approve with suggestions | Fix before merge |
| Multiple high issues | ⚠️ Request changes | Author must address |
| Any critical issue | 🚫 Block | Cannot merge until resolved |

---

## 3. Common Antipatterns

### Structural

| Pattern | Symptom | Fix |
|---------|---------|-----|
| God class | One class does everything | Split by single responsibility |
| Long method | Function does 5+ distinct things | Extract named helper functions |
| Deep nesting | 4+ levels of if/for/try | Guard clauses, early returns, extraction |
| Feature envy | Method uses another object's data more than its own | Move method to the data owner |
| Shotgun surgery | One change requires edits in 10+ files | Consolidate related logic |

### Logic

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Boolean blindness | `doThing(true, false, true)` | Named options object or enum |
| Stringly typed | `status === 'actve'` (typo = silent bug) | Define enum or union type |
| Magic numbers | `if (retries > 3)` | Named constant: `MAX_RETRIES = 3` |
| Primitive obsession | Passing 5 related strings around | Create a data object/type |

### Security

| Pattern | Symptom | Fix |
|---------|---------|-----|
| SQL injection | String concatenation in queries | Parameterized queries / prepared statements |
| Hardcoded secrets | `apiKey = "sk-..."` in source | Environment variables or secret manager |
| Missing validation | Raw user input passed to logic | Schema validation at API boundary |
| Overpermission | Broad access when narrow suffices | Principle of least privilege |

### Performance

| Pattern | Symptom | Fix |
|---------|---------|-----|
| N+1 queries | Loop → query per item | Batch fetch with `WHERE IN (...)` |
| Unbounded collections | `.all()` without LIMIT | Always paginate or set max |
| Missing index | Slow repeated lookups on same column | Add database index |
| Premature optimization | Complex caching for 10 rows | Profile first, optimize second |

### Async

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Floating promise | `doAsync()` without `await` | Always `await` or handle rejection |
| Callback hell | 4+ nested callbacks | Refactor to async/await |
| Missing timeout | External call can hang forever | Set timeout on all network calls |

---

## 3.5 Security Review Quick-Check

For **every review**, scan for these OWASP-aligned red flags. Delegate to `dev-security/SKILL.md` for deep analysis.

### Must-Check (Every PR)

| Check | Red Flag | Severity |
|-------|----------|----------|
| Hardcoded secrets | `apiKey = "sk-..."`, DB URLs in source | **Critical** |
| SQL/NoSQL injection | String concatenation in queries | **Critical** |
| Missing input validation | User input passed to logic without schema check | **High** |
| Missing auth check | Endpoint accessible without authentication | **High** |
| BOLA (Broken Object Auth) | No ownership check on object access (`/users/:id` without verifying caller owns resource) | **High** |
| Secrets in logs | `console.log(req.body)` leaking tokens/passwords | **High** |

### Check When Relevant

| Check | When | Red Flag |
|-------|------|----------|
| SSRF | External URL from user input | No URL allowlist, no domain validation |
| Path traversal | File path from user input | No path sanitization, `../` not blocked |
| Mass assignment | Object spread into DB model | `Object.assign(model, req.body)` without allowlist |
| Dep vulnerabilities | New dependencies added | No `npm audit`/`pip-audit` run |
| Lockfile changes | `package-lock.json` modified | Unexpected dependency resolution changes |

> **Deep security analysis** → invoke `dev-security/SKILL.md`. This checklist catches surface-level issues during code review; `dev-security` provides OWASP Top 10 depth, ASVS checklists, and static analysis integration.

---

## 3.6 Performance Review Quick-Check

Scan every PR for these common performance pitfalls:

### Database & API

| Check | Red Flag | Fix |
|-------|----------|-----|
| N+1 queries | Loop containing DB call or API fetch | Batch with `WHERE IN (...)` or DataLoader |
| Missing pagination | `.findAll()` or `SELECT *` without LIMIT | Add cursor-based or offset pagination |
| Missing index | New WHERE/JOIN column without index | `CREATE INDEX` on filtered/joined columns |
| Unbounded query | No LIMIT on user-facing list endpoints | Always set max page size |

### Frontend-Specific

| Check | Red Flag | Fix |
|-------|----------|-----|
| Unnecessary re-renders | State updates in parent causing child re-render cascade | `React.memo`, `useMemo`, extract state down |
| Bundle size impact | New large dependency (>50KB gzipped) | Check `bundlephobia.com`, consider alternatives or lazy loading |
| Missing `key` prop | List rendering without stable keys | Use unique ID, never array index for dynamic lists |
| Unoptimized images | Large images without `next/image`, `loading="lazy"`, or srcset | Use framework image optimization |

### General

| Check | Red Flag | Fix |
|-------|----------|-----|
| Missing timeout | External HTTP call without timeout | Set timeout on all network requests |
| Sync blocking | CPU-intensive work on main thread/event loop | Offload to worker/queue |
| Memory leak | Event listeners/subscriptions without cleanup | Add cleanup in `useEffect` return / `finally` block |

---

## 4. Receiving Code Review

### The Response Pattern

When receiving review feedback:

1. **READ** — Complete feedback without reacting immediately
2. **UNDERSTAND** — Restate the technical requirement in your own words
3. **VERIFY** — Check the suggestion against codebase reality (does it apply here?)
4. **EVALUATE** — Is it technically sound for THIS codebase, not just in theory?
5. **RESPOND** — Technical acknowledgment or reasoned pushback
6. **IMPLEMENT** — One item at a time, test each change

### When to Push Back

Push back when:
- Suggestion breaks existing functionality (test it)
- Reviewer lacks full context of the current architecture
- Violates YAGNI — feature is unused (grep the codebase to verify)
- Technically incorrect for this technology stack
- Conflicts with established architectural decisions

**How:** Use technical reasoning. Reference working tests, existing code, or documented decisions. Never push back emotionally — always with evidence.

### Implementation Order (multi-item feedback)

1. **Clarify ALL unclear items FIRST** — don't implement based on partial understanding
2. Blocking issues (security, data loss, broken functionality)
3. Simple fixes (typos, missing imports, naming)
4. Complex fixes (refactoring, logic changes)
5. Test EACH fix individually. Verify no regressions after each.

### Acknowledging Feedback

```
✅ "Fixed. Changed X to use parameterized query."
✅ "Good catch — the null check was missing. Added guard on line 42."
✅ Just fix it and show the result in code.

❌ "You're absolutely right!"
❌ "Great point! Thanks for catching that!"
❌ Any performative agreement without verification
```

---

## 5. Requesting Code Review

### When to Request

| Situation | Priority |
|-----------|----------|
| Before merge to main | **Mandatory** |
| After major feature completion | **Mandatory** |
| Before large refactoring | **Mandatory** |
| After complex bug fix | Recommended |
| When stuck on approach | Recommended |
| Small config/docs changes | Skip unless impactful |

### How to Request

1. Ensure build passes and all tests are green
2. Identify the diff range (base commit → head commit)
3. Provide a summary: what was implemented, what it should do, areas to focus on
4. Keep the diff <500 lines. Split larger changes into reviewable chunks.

### Acting on Feedback

| Severity | Action |
|----------|--------|
| Critical | Fix immediately, re-request review |
| High | Fix before proceeding to next task |
| Medium | Fix before merge, can continue other work |
| Low | Note for later, apply if trivial |
| Style | Apply if trivial, otherwise defer to team conventions |

---

## 6. Sub-Agent Review Mode

For large diffs (>500 lines) or multi-domain changes, use parallel sub-agent review:

### When to Parallelize

| Condition | Strategy |
|-----------|----------|
| Diff ≤200 lines, single domain | Single-agent review (this skill) |
| Diff 200-500 lines, single domain | Single-agent, focus on hotspots |
| Diff >500 lines | **Split and parallelize** |
| Multi-domain (frontend + backend + infra) | **Parallelize by domain** |

### Orchestration Protocol

1. **Orchestrator** analyzes diff scope — identify domains, file groups, and review focus areas.

2. **Spawn parallel review agents** using `task` tool with `agent_type: "code-review"`:
   - **Security track** — auth changes, input handling, secrets, dependencies
   - **Architecture track** — layer violations, coupling, abstraction fitness
   - **Domain tracks** — frontend (apply `dev-frontend` constraints), backend (apply `dev-backend` patterns), data (apply `dev-data` patterns)

3. **Each sub-agent receives:**
   - Their file subset (use `git diff -- <paths>`)
   - The review process from §1-5 of this skill
   - Domain-specific skill reference if applicable
   - Instruction to output structured findings: `{severity, file, line, category, issue, fix}`

4. **Orchestrator collects and post-processes:**
   - **Deduplicate** — merge findings on same file:line
   - **Normalize severity** — align to Critical/High/Medium/Low
   - **Resolve conflicts** — if agents disagree, escalate with both arguments
   - **Present unified review** — sorted by severity, then by file

### Cost Awareness

| Diff Size | Agents | Justification |
|-----------|--------|---------------|
| <500 lines | 1 | Not worth parallelization overhead |
| 500-1500 lines | 2-3 | Split by domain (frontend/backend/infra) |
| >1500 lines | 3-5 | Full domain decomposition; consider if PR should be split instead |

**Rule: If you need >5 review agents, the PR is too large.** Request the author split it.

### AI Tool Integration Awareness

When external AI review tools are available, coordinate — don't duplicate:

| Tool | Strengths | Use When | Agent Focus Shifts To |
|------|-----------|----------|----------------------|
| **GitHub Copilot Code Review** | Full repo context, multi-model, auto-fix PRs | PR review on GitHub | Architecture, business logic, domain correctness |
| **CodeRabbit** | 40+ linters, learnable preferences, low false-positive | Team with `.coderabbit.yml` configured | Cross-service impact, subtle logic errors |
| **SonarQube** | Enterprise SAST, tech debt tracking, security depth | Regulated environments, existing setup | Review findings, add context tools miss |
| **Manual agent review** | Full codebase understanding, intent verification | No external tools, offline, sensitive code | Everything — full §1-5 process |

**Coordination rule:** If an external AI tool already reviewed the PR, **read its findings first**, then focus manual review on what the tool explicitly cannot do: architectural fit, business intent alignment, and cross-system impact.

---

The best code review catches the bug before the user does. Be thorough, be honest, be kind.
