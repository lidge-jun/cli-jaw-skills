---
name: prompt-engineering
description: >
  Analyze and optimize prompts for AI coding agents. Decompose tasks into
  components (skills/commands/agents), detect missing context, and produce
  ready-to-paste improved prompts. Advisory only — outputs prompts, not code.
  Triggers: "optimize prompt", "improve my prompt", "rewrite this prompt",
  "how to write a prompt for", "help me prompt"
---

# Prompt Engineering

Analyze a draft prompt, identify gaps, map it to available agent components,
and output an optimized prompt the user can paste and run.

## When to Use

- User asks to optimize, improve, or rewrite a prompt
- User asks "what's the best way to ask the agent to..."
- User pastes a draft prompt and asks for feedback

## When to Skip

- User wants the task executed directly ("just do it")
- User asks to optimize code or performance (that's a refactoring task)

## How It Works

Advisory only — output analysis and an optimized prompt. Do not execute the task.

### Phase 1: Project Detection

Before analyzing the prompt, detect context from the working directory:

1. Read `CLAUDE.md` / `AGENTS.md` for project conventions
2. Detect tech stack from config files:
   - `package.json` → Node / TypeScript / React / Next.js
   - `go.mod` → Go
   - `pyproject.toml` / `requirements.txt` → Python
   - `Cargo.toml` → Rust
   - `build.gradle` / `pom.xml` → Java / Kotlin
3. Note the detected stack for component matching and missing-context analysis

If no project files found, flag "tech stack unknown" and proceed.

### Phase 2: Intent Classification

Classify the user's task:

| Category | Signal Words | Example |
|----------|-------------|---------|
| New Feature | build, create, add, implement | "Build a login page" |
| Bug Fix | fix, broken, not working, error | "Fix the auth flow" |
| Refactor | refactor, clean up, restructure | "Refactor the API layer" |
| Research | how to, what is, explore | "How to add SSO" |
| Testing | test, coverage, verify | "Add tests for the cart" |
| Review | review, audit, check | "Review my PR" |
| Documentation | document, update docs | "Update the API docs" |
| Infrastructure | deploy, CI, docker, database | "Set up CI/CD pipeline" |

### Phase 3: Scope Assessment

| Scope | Heuristic | Approach |
|-------|-----------|----------|
| Trivial | Single file, < 50 lines | Direct execution |
| Low | Single component or module | Single skill or tool |
| Medium | Multiple components, same domain | Chained steps + verification |
| High | Cross-domain, 5+ files | Plan first, then phased execution |
| Epic | Multi-session, architectural shift | Multi-session plan with checkpoints |

### Phase 4: Component Mapping

Map intent + scope to available agent components:

| Intent | Skills | Agents |
|--------|--------|--------|
| New Feature | dev, dev-frontend/backend, dev-scaffolding | planner, code-reviewer |
| Bug Fix | dev-testing, dev-debugging | tdd-guide |
| Refactor | dev-code-reviewer | code-reviewer |
| Research | search, rag | explore agent |
| Testing | dev-testing | test runner |
| Review | dev-code-reviewer | code-reviewer |
| Documentation | documentation | doc writer |
| Infrastructure | dev-backend | architect |

For project-specific skills, check `.agents/skills/` to find applicable ones.

### Phase 5: Missing Context Detection

Scan the prompt for missing information:

- [ ] **Tech stack** — detected or needs user input?
- [ ] **Target scope** — files, directories, or modules specified?
- [ ] **Acceptance criteria** — how to know the task is done?
- [ ] **Error handling** — edge cases and failure modes addressed?
- [ ] **Security requirements** — auth, validation, secrets?
- [ ] **Testing expectations** — unit, integration, E2E?
- [ ] **Existing patterns** — reference files or conventions to follow?
- [ ] **Scope boundaries** — what to exclude?

If 3+ items are missing, ask the user up to 3 clarification questions before
generating the optimized prompt.

### Phase 6: Generate Optimized Prompt

Produce two versions:

**Full version** (inside a fenced code block):
- Clear task description with context
- Tech stack (detected or specified)
- Acceptance criteria
- Verification steps
- Scope boundaries (what to exclude)
- Relevant skills/agents to invoke

**Quick version** (one-liner patterns):

| Intent | Pattern |
|--------|---------|
| New Feature | `Plan [feature]. Implement with tests. Review. Verify.` |
| Bug Fix | `Write failing test for [bug]. Fix to green. Verify.` |
| Refactor | `Refactor [scope]. Review. Verify no regressions.` |
| Research | `Search for [topic]. Summarize findings with citations.` |
| Testing | `Add tests for [module]. Target [coverage]% coverage.` |

## Prompt Quality Principles

1. **Specificity over vagueness**: name files, modules, endpoints
2. **Acceptance criteria**: define "done" before starting
3. **Scope boundaries**: state what to exclude to prevent drift
4. **Existing patterns**: reference existing code the agent should follow
5. **Verification step**: end with a concrete check (test, build, curl)
6. **Component awareness**: invoke skills/agents by name when applicable

## Output Format

```
### Prompt Diagnosis
**Strengths**: (what the original does well)
**Issues**: (table: issue | impact | fix)
**Needs Clarification**: (numbered questions)

### Recommended Components
(table: type | component | purpose)

### Optimized Prompt — Full
(fenced code block, ready to paste)

### Optimized Prompt — Quick
(one-liner)

### Enhancement Rationale
(table: what was added | why)
```

## Constraints

- Advisory only — produce prompts, not implementations
- Respond in the same language as the user's input
- When referencing skills, verify they exist in `.agents/skills/` first
- Keep optimized prompts self-contained and copy-pasteable
