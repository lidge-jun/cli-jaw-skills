---
name: plankton-code-quality
description: Write-time code quality enforcement using Plankton — auto-formatting, linting, and agent-powered fixes on every file edit via hooks.
---

# Plankton Code Quality

Integration reference for Plankton (credit: @alxfazio), a write-time code quality enforcement system. Plankton runs formatters and linters on every file edit via PostToolUse hooks, then spawns agent subprocesses to fix violations.

## When to Use

- Automatic formatting and linting on every file edit (not just at commit time)
- Defense against agents modifying linter configs to pass instead of fixing code
- Tiered model routing for fixes (light model for style, standard for logic, advanced for types)
- Multi-language projects (Python, TypeScript, Shell, YAML, JSON, TOML, Markdown, Dockerfile)

## Three-Phase Architecture

Every time an agent edits or writes a file, Plankton's `multi_linter.sh` PostToolUse hook runs:

```
Phase 1: Auto-Format (Silent)
├─ Runs formatters (ruff format, biome, shfmt, taplo, markdownlint)
├─ Fixes 40–50% of issues silently
└─ No output to main agent

Phase 2: Collect Violations (JSON)
├─ Runs linters and collects unfixable violations
├─ Returns structured JSON: {line, column, code, message, linter}
└─ Still no output to main agent

Phase 3: Delegate + Verify
├─ Spawns subprocess with violations JSON
├─ Routes to model tier based on violation complexity:
│   ├─ Light: formatting, imports, style — 120s timeout
│   ├─ Standard: complexity, refactoring — 300s timeout
│   └─ Advanced: type system, deep reasoning — 600s timeout
├─ Re-runs Phase 1+2 to verify fixes
└─ Exit 0 if clean, Exit 2 if violations remain (reported to main agent)
```

### What the Main Agent Sees

| Scenario | Agent sees | Hook exit |
|----------|-----------|-----------|
| No violations | Nothing | 0 |
| All fixed by subprocess | Nothing | 0 |
| Violations remain after subprocess | `[hook] N violation(s) remain` | 2 |
| Advisory (duplicates, old tooling) | `[hook:advisory] ...` | 0 |

Most quality problems are resolved transparently.

### Config Protection

Agents may modify linter configs to disable rules rather than fix code. Plankton blocks this with:

1. **PreToolUse hook** — `protect_linter_configs.sh` blocks edits to linter configs before they happen
2. **Stop hook** — `stop_config_guardian.sh` detects config changes via `git diff` at session end
3. **Protected files** — `.ruff.toml`, `biome.json`, `.shellcheckrc`, `.yamllint`, `.hadolint.yaml`, etc.

### Package Manager Enforcement

A PreToolUse hook on Bash blocks legacy package managers:
- `pip`, `pip3`, `poetry`, `pipenv` → blocked (use `uv`)
- `npm`, `yarn`, `pnpm` → blocked (use `bun`)
- Exceptions: `npm audit`, `npm view`, `npm publish`

## Setup

```bash
# Clone Plankton (credit: @alxfazio)
git clone https://github.com/alexfazio/plankton.git
cd plankton

# Install core dependencies
brew install jaq ruff uv

# Install Python linters
uv sync --all-extras
```

Hooks in `.claude/settings.json` activate automatically.

### Per-Project Integration

1. Copy `.claude/hooks/` directory to your project
2. Copy `.claude/settings.json` hook configuration
3. Copy linter config files (`.ruff.toml`, `biome.json`, etc.)
4. Install the linters for your languages

### Language Dependencies

| Language | Required | Optional |
|----------|----------|----------|
| Python | `ruff`, `uv` | `ty` (types), `vulture` (dead code), `bandit` (security) |
| TypeScript/JS | `biome` | `oxlint`, `semgrep`, `knip` (dead exports) |
| Shell | `shellcheck`, `shfmt` | — |
| YAML | `yamllint` | — |
| Markdown | `markdownlint-cli2` | — |
| Dockerfile | `hadolint` (≥ 2.12.0) | — |
| TOML | `taplo` | — |
| JSON | `jaq` | — |

## Configuration Reference

Plankton's `.claude/hooks/config.json` controls all behavior:

```json
{
  "languages": {
    "python": true,
    "shell": true,
    "yaml": true,
    "json": true,
    "toml": true,
    "dockerfile": true,
    "markdown": true,
    "typescript": {
      "enabled": true,
      "js_runtime": "auto",
      "biome_nursery": "warn",
      "semgrep": true
    }
  },
  "phases": {
    "auto_format": true,
    "subprocess_delegation": true
  },
  "subprocess": {
    "tiers": {
      "light":    { "timeout": 120, "max_turns": 10 },
      "standard": { "timeout": 300, "max_turns": 10 },
      "advanced": { "timeout": 600, "max_turns": 15 }
    },
    "volume_threshold": 5
  }
}
```

Key settings:
- Disable unused languages to speed up hooks
- `volume_threshold` — violations above this count auto-escalate to a higher model tier
- `subprocess_delegation: false` — skip Phase 3, just report violations

## Environment Overrides

| Variable | Purpose |
|----------|---------|
| `HOOK_SKIP_SUBPROCESS=1` | Skip Phase 3, report violations directly |
| `HOOK_SUBPROCESS_TIMEOUT=N` | Override tier timeout |
| `HOOK_DEBUG_MODEL=1` | Log model selection decisions |
| `HOOK_SKIP_PM=1` | Bypass package manager enforcement |

## References

- [Plankton](https://github.com/alexfazio/plankton) (credit: @alxfazio)
