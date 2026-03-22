---
name: continuous-learning-v2
description: Instinct-based learning system that observes sessions via hooks, creates atomic instincts with confidence scoring, and evolves them into skills/commands/agents. v2.1 adds project-scoped instincts to prevent cross-project contamination.
---

# Continuous Learning v2.1 — Instinct-Based Architecture

An advanced learning system that turns agent sessions into reusable knowledge through atomic "instincts" — small learned behaviors with confidence scoring.

v2.1 adds **project-scoped instincts** — React patterns stay in your React project, Python conventions stay in your Python project, and universal patterns (like "always validate input") are shared globally.

## When to Activate

- Setting up automatic learning from agent sessions
- Configuring instinct-based behavior extraction via hooks
- Tuning confidence thresholds for learned behaviors
- Reviewing, exporting, or importing instinct libraries
- Evolving instincts into full skills, commands, or agents
- Managing project-scoped vs global instincts

## What Changed in v2.1

| Feature | v2.0 | v2.1 |
|---------|------|------|
| Storage | Global only | Project-scoped (projects/<hash>/) |
| Scope | All instincts apply everywhere | Project-scoped + global |
| Detection | None | git remote URL / repo path |
| Promotion | N/A | Project → global when seen in 2+ projects |
| Commands | 4 | 6 (+promote/projects) |

## What Changed in v2 (vs v1)

| Feature | v1 | v2 |
|---------|----|----|
| Observation | Stop hook (session end) | PreToolUse/PostToolUse (100% reliable) |
| Analysis | Main context | Background agent (fast model) |
| Granularity | Full skills | Atomic "instincts" |
| Confidence | None | 0.3–0.9 weighted |
| Evolution | Direct to skill | Instincts → cluster → skill/command/agent |

## The Instinct Model

An instinct is a small learned behavior:

```yaml
---
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.7
domain: "code-style"
source: "session-observation"
scope: project
project_id: "a1b2c3d4e5f6"
project_name: "my-react-app"
---

# Prefer Functional Style

## Action
Use functional patterns over classes when appropriate.

## Evidence
- Observed 5 instances of functional pattern preference
- User corrected class-based approach to functional on 2025-01-15
```

**Properties:**
- **Atomic** — one trigger, one action
- **Confidence-weighted** — 0.3 = tentative, 0.9 = near certain
- **Domain-tagged** — code-style, testing, git, debugging, workflow, etc.
- **Evidence-backed** — tracks what observations created it
- **Scope-aware** — `project` (default) or `global`

## How It Works

```
Session Activity (in a git repo)
      |
      | Hooks capture prompts + tool use (100% reliable)
      | + detect project context (git remote / repo path)
      v
+---------------------------------------------+
|  projects/<project-hash>/observations.jsonl  |
+---------------------------------------------+
      |
      | Observer agent reads (background, fast model)
      v
+---------------------------------------------+
|          PATTERN DETECTION                   |
|   * User corrections -> instinct             |
|   * Error resolutions -> instinct            |
|   * Repeated workflows -> instinct           |
|   * Scope decision: project or global?       |
+---------------------------------------------+
      |
      | Creates/updates
      v
+---------------------------------------------+
|  projects/<hash>/instincts/personal/         |
|   * prefer-functional.yaml (0.7) [project]   |
+---------------------------------------------+
|  instincts/personal/  (GLOBAL)               |
|   * always-validate-input.yaml (0.85)        |
+---------------------------------------------+
```

## Project Detection

The system automatically detects your current project:

1. **`AGENT_PROJECT_DIR` env var** (highest priority)
2. **`git remote get-url origin`** — hashed for a portable project ID
3. **`git rev-parse --show-toplevel`** — fallback using repo path
4. **Global fallback** — if no project is detected, instincts go to global scope

Each project gets a 12-character hash ID (e.g., `a1b2c3d4e5f6`).

## Hook Setup

Add observation hooks to your agent settings. The hooks call `observe.sh` on every tool use:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "<skills-path>/continuous-learning-v2/hooks/observe.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "<skills-path>/continuous-learning-v2/hooks/observe.sh"
      }]
    }]
  }
}
```

## Commands

| Command | Description |
|---------|-------------|
| `/instinct-status` | Show all instincts (project-scoped + global) with confidence |
| `/evolve` | Cluster related instincts into skills/commands, suggest promotions |
| `/instinct-export` | Export instincts (filterable by scope/domain) |
| `/instinct-import <file>` | Import instincts with scope control |
| `/promote [id]` | Promote project instincts to global scope |
| `/projects` | List all known projects and their instinct counts |

## Configuration

Edit `config.json` to control the background observer:

```json
{
  "version": "2.1",
  "observer": {
    "enabled": false,
    "run_interval_minutes": 5,
    "min_observations_to_analyze": 20
  }
}
```

## File Structure

```
~/.config/agent/homunculus/
+-- identity.json
+-- projects.json            # Registry: hash -> name/path/remote
+-- observations.jsonl       # Global observations (fallback)
+-- instincts/
|   +-- personal/            # Global auto-learned
|   +-- inherited/           # Global imported
+-- evolved/
|   +-- agents/
|   +-- skills/
|   +-- commands/
+-- projects/
    +-- a1b2c3d4e5f6/        # Per-project directory
    |   +-- project.json
    |   +-- observations.jsonl
    |   +-- instincts/personal/
    |   +-- evolved/
    +-- f6e5d4c3b2a1/
        +-- ...
```

## Scope Decision Guide

| Pattern Type | Scope | Examples |
|-------------|-------|---------|
| Language/framework conventions | **project** | "Use React hooks", "Follow Django REST patterns" |
| File structure preferences | **project** | "Tests in `__tests__`/", "Components in src/components/" |
| Code style | **project** | "Use functional style", "Prefer dataclasses" |
| Security practices | **global** | "Validate user input", "Sanitize SQL" |
| General best practices | **global** | "Write tests first", "Handle errors explicitly" |
| Tool workflow preferences | **global** | "Grep before Edit", "Read before Write" |

## Instinct Promotion (Project → Global)

When the same instinct appears in multiple projects with high confidence, promote it to global scope.

**Auto-promotion criteria:**
- Same instinct ID in 2+ projects
- Average confidence ≥ 0.8

```bash
python3 instinct-cli.py promote prefer-explicit-errors   # specific
python3 instinct-cli.py promote                           # auto-promote all
python3 instinct-cli.py promote --dry-run                 # preview
```

## Confidence Scoring

| Score | Meaning | Behavior |
|-------|---------|----------|
| 0.3 | Tentative | Suggested, not enforced |
| 0.5 | Moderate | Applied when relevant |
| 0.7 | Strong | Auto-approved for application |
| 0.9 | Near-certain | Core behavior |

**Confidence increases** when: pattern is repeatedly observed, user accepts the behavior, similar instincts agree.

**Confidence decreases** when: user explicitly corrects, pattern goes unobserved, contradicting evidence appears.

## Privacy

- Observations stay **local** on your machine
- Project-scoped instincts are isolated per project
- Only **instincts** (patterns) can be exported — raw observations stay local
- You control what gets exported and promoted
