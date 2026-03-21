---
name: codeql
description: >-
  Runs CodeQL static analysis for security vulnerability detection
  using interprocedural data flow and taint tracking. Applicable when
  finding vulnerabilities, running a security scan, performing a security
  audit, running CodeQL, building a CodeQL database, selecting query
  rulesets, creating data extension models, or processing CodeQL SARIF
  output. NOT for writing custom QL queries or CI/CD pipeline setup.
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
  - Task
  - TaskCreate
  - TaskList
  - TaskUpdate
---

# CodeQL Analysis

Supported languages: Python, JavaScript/TypeScript, Go, Java/Kotlin, C/C++, C#, Ruby, Swift.

**Skill resources:** Reference files and templates are located at `{baseDir}/references/` and `{baseDir}/workflows/`. Use `{baseDir}` to resolve paths to these files at runtime.

## Quick Start

For the common case ("scan this codebase for vulnerabilities"):

```bash
# 1. Verify CodeQL is installed
command -v codeql >/dev/null 2>&1 && codeql --version || echo "NOT INSTALLED"

# 2. Check for existing database
ls -dt codeql_*.db 2>/dev/null | head -1
```

Then execute the full pipeline: **build database → create data extensions → run analysis** using the workflows below.

## When to Use

- Scanning a codebase for security vulnerabilities with deep data flow analysis
- Building a CodeQL database from source code (with build capability for compiled languages)
- Finding complex vulnerabilities that require interprocedural taint tracking or AST/CFG analysis
- Performing comprehensive security audits with multiple query packs

## When to Use Something Else

- Custom QL queries → dedicated query development skill
- CI/CD integration → GitHub Actions docs
- Quick pattern searches or single-file analysis → Semgrep or grep
- Compiled languages without build capability → Semgrep

## Common Pitfalls

- Always check Trail of Bits + Community Packs beyond `security-extended` — they catch categories it misses.
- A successful database build does not guarantee good extraction. Verify file counts against expected source files (cached builds extract nothing).
- Even standard frameworks (Django/Spring) have custom wrappers CodeQL doesn't model — run the data extensions workflow.
- `build-mode=none` for compiled languages produces severely incomplete analysis (no interprocedural data flow). Use as last resort and flag the limitation.
- Zero findings may indicate poor database quality, missing models, or wrong packs. Investigate before reporting clean.
- Always specify the suite explicitly (e.g., `security-extended`) for reproducibility.

---

## Workflow Selection

This skill has three workflows:

| Workflow | Purpose |
|----------|---------|
| [build-database](workflows/build-database.md) | Create CodeQL database using 3 build methods in sequence |
| [create-data-extensions](workflows/create-data-extensions.md) | Detect or generate data extension models for project APIs |
| [run-analysis](workflows/run-analysis.md) | Select rulesets, execute queries, process results |


### Auto-Detection Logic

**If user explicitly specifies** what to do (e.g., "build a database", "run analysis"), execute that workflow.

**Default pipeline for "test", "scan", "analyze", or similar:** Execute all three workflows sequentially: build → extensions → analysis. The create-data-extensions step is critical for finding vulnerabilities in projects with custom frameworks or annotations that CodeQL doesn't model by default.

```bash
# Check if database exists
DB=$(ls -dt codeql_*.db 2>/dev/null | head -1)
if [ -n "$DB" ] && codeql resolve database -- "$DB" >/dev/null 2>&1; then
  echo "DATABASE EXISTS ($DB) - can run analysis"
else
  echo "NO DATABASE - need to build first"
fi
```

| Condition | Action |
|-----------|--------|
| No database exists | Execute build → extensions → analysis (full pipeline) |
| Database exists, no extensions | Execute extensions → analysis |
| Database exists, extensions exist | Ask user: run analysis on existing DB, or rebuild? |
| User says "just run analysis" or "skip extensions" | Run analysis only |


### Decision Prompt

If unclear, ask user which workflow: full scan (recommended), build database, create extensions, or run analysis.
