---
name: semgrep
description: Run Semgrep static analysis scan on a codebase using parallel subagents. Automatically
  detects and uses Semgrep Pro for cross-file analysis when available. Use when asked to scan
  code for vulnerabilities, run a security audit with Semgrep, find bugs, or perform
  static analysis. Spawns parallel workers for multi-language codebases and triage.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Write
  - Task
  - AskUserQuestion
  - TaskCreate
  - TaskList
  - TaskUpdate
  - WebFetch
---

# Semgrep Security Scan

Run a complete Semgrep scan with automatic language detection, parallel execution via Task subagents, and parallel triage. Uses Semgrep Pro for cross-file taint analysis when available.

## Prerequisites

Semgrep CLI required:
```bash
semgrep --version
```

Optional — Semgrep Pro enables cross-file taint tracking, inter-procedural analysis, and additional languages (Apex, C#, Elixir):
```bash
semgrep --pro --validate --config p/default 2>/dev/null && echo "Pro available" || echo "OSS only"
```

## Scope

**Use for**: security audits, vulnerability scanning, bug pattern detection, first-pass static analysis.

**Use instead**: binary analysis tools (for binaries), existing CI pipelines (if Semgrep CI configured), CodeQL (cross-file without Pro), `semgrep-rule-creator` skill (custom rules), `semgrep-rule-variant-creator` skill (porting rules).

---

## Architecture

Main agent orchestrates parallel Task subagents:

1. Detect languages + check Pro availability
2. Select rulesets (ref: [rulesets.md]({baseDir}/references/rulesets.md))
3. Present plan + rulesets → **await user approval** (hard gate)
4. Spawn parallel scan Tasks (one per language category)
5. Spawn parallel triage Tasks
6. Collect and report results

| Agent | Tools | Purpose |
|-------|-------|---------|
| `static-analysis:semgrep-scanner` | Bash | Execute parallel semgrep scans per language |
| `static-analysis:semgrep-triager` | Read, Grep, Glob, Write | Classify findings by reading source context |

## Task Tracking

Create all 6 tasks with dependencies on invocation:

| Task | Gate | Proceeds when |
|------|------|---------------|
| Step 1: Detect languages/Pro | — | — |
| Step 2: Select rulesets | — | Step 1 done |
| Step 3: Get approval | **Hard gate** | User explicitly approves |
| Step 4: Execute scans | Soft gate | Step 3 done |
| Step 5: Triage findings | Soft gate | All scan JSONs exist |
| Step 6: Report results | — | Step 5 done |

Step 3 hard gate: mark completed only after explicit user confirmation ("yes", "proceed", "approved", or equivalent). The original scan request does not count as approval.

---

## Workflow

### Step 1: Detect Languages and Pro Availability

```bash
# Check Pro
SEMGREP_PRO=false
if semgrep --pro --validate --config p/default 2>/dev/null; then
  SEMGREP_PRO=true
fi

# Find languages by extension
fd -t f -e py -e js -e ts -e jsx -e tsx -e go -e rb -e java -e php -e c -e cpp -e rs | \
  sed 's/.*\.//' | sort | uniq -c | sort -rn

# Detect frameworks
ls -la package.json pyproject.toml Gemfile go.mod Cargo.toml pom.xml 2>/dev/null
fd -t f "Dockerfile" "docker-compose" ".tf" "*.yaml" "*.yml" | head -20
```

Map extensions → categories: Python, JavaScript/TypeScript, Go, Ruby, Java, PHP, C/C++, Rust, Docker, Terraform, Kubernetes.

### Step 2: Select Rulesets

Follow the **Ruleset Selection Algorithm** in [rulesets.md]({baseDir}/references/rulesets.md). Output structured JSON for Step 3 review:

```json
{
  "baseline": ["p/security-audit", "p/secrets"],
  "python": ["p/python", "p/django"],
  "javascript": ["p/javascript", "p/react", "p/nodejs"],
  "third_party": ["https://github.com/trailofbits/semgrep-rules"]
}
```

Third-party rulesets (Trail of Bits, 0xdea, Decurity) are included by default when languages match — they catch vulnerabilities absent from the official registry.

### Step 3: Present Plan and Get Approval

Present a plan covering:
- Target directory and output directory (`./semgrep-results-NNN/`)
- Engine type (Pro/OSS)
- Detected languages with file counts
- All rulesets grouped by category with checkboxes
- Available-but-not-selected rulesets
- Execution strategy (parallel task count, agent types)

**Approval flow:**
1. Allow the user to add/remove rulesets before approving
2. Use AskUserQuestion if no response received
3. Mark Step 3 complete only after explicit approval
4. Re-present updated plan if user modifies rulesets

**Not valid approval:** silence, questions about the plan, the original scan request.

### Step 4: Spawn Parallel Scan Tasks

Create numbered output directory, then spawn all scan Tasks in a single message:

```bash
LAST=$(ls -d semgrep-results-[0-9][0-9][0-9] 2>/dev/null | sort | tail -1 | grep -o '[0-9]*$' || true)
NEXT_NUM=$(printf "%03d" $(( ${LAST:-0} + 1 )))
OUTPUT_DIR="semgrep-results-${NEXT_NUM}"
mkdir -p "$OUTPUT_DIR"
```

Use `subagent_type: static-analysis:semgrep-scanner` with approved rulesets from Step 3. See [scanner-task-prompt.md]({baseDir}/references/scanner-task-prompt.md) for prompt template.

Each task scans one language category, outputting to `$OUTPUT_DIR/{lang}-*.json` and `*.sarif`.

### Step 5: Spawn Parallel Triage Tasks

After scans complete, spawn triage Tasks using `subagent_type: static-analysis:semgrep-triager`. See [triage-task-prompt.md]({baseDir}/references/triage-task-prompt.md) for prompt template.

Triage reads source context around each finding to classify as true/false positive.

### Step 6: Collect Results

Generate merged SARIF with triaged true positives:

```bash
uv run {baseDir}/scripts/merge_triaged_sarif.py [OUTPUT_DIR]
```

The script reads `*-triage.json` files, filters to true positives, and writes `findings-triaged.sarif`. Uses [SARIF Multitool](https://www.npmjs.com/package/@microsoft/sarif-multitool) if available, falls back to pure Python.

Report summary to user:
- Files scanned, rulesets used
- Raw vs triaged finding counts
- Breakdown by severity (ERROR/WARNING/INFO) and category
- Output file locations (`findings-triaged.sarif`, `*-triage.json`, raw `*.json`/`*.sarif`)

---

## Common Pitfalls

| Pitfall | Correct approach |
|---------|-----------------|
| Missing `--metrics=off` | Always disable telemetry |
| Sequential rulesets | Run in parallel with `&` and `wait` |
| Unscoped rulesets | Use `--include="*.py"` for language-specific rules |
| Reporting raw findings | Always triage to filter false positives |
| Sequential Tasks | Spawn all Tasks in a single message for parallelism |
| Using `--config auto` | Sends metrics, less ruleset control — use explicit rulesets |
| Skipping Pro check | Pro catches ~2.5× more true positives via cross-file analysis |
| Treating scan request as plan approval | Present plan with parameters, await explicit "yes" |
| Adding/removing rulesets without asking | Only scan with the user-approved ruleset list |

## Limitations

1. **OSS mode** cannot track data flow across files — enable Pro via `semgrep login` + `semgrep install-semgrep-pro`
2. **Pro cross-file** uses `-j 1` (slower per ruleset; compensated by parallel rulesets)
3. Some false positive patterns require human judgment
