---
name: continuous-learning
description: Automatically extract reusable patterns from agent sessions and save them as learned skills for future use.
---

# Continuous Learning

Evaluate agent sessions on completion to extract reusable patterns saved as learned skills.

## When to Activate

- Setting up automatic pattern extraction from agent sessions
- Configuring a Stop hook for session evaluation
- Reviewing or curating learned skills
- Adjusting extraction thresholds or pattern categories

## How It Works

This skill runs as a **Stop hook** at the end of each session:

1. **Session Evaluation**: Checks if session has enough messages (default: 10+)
2. **Pattern Detection**: Identifies extractable patterns from the session
3. **Skill Extraction**: Saves useful patterns to a learned skills directory

## Configuration

Edit `config.json` to customize:

```json
{
  "min_session_length": 10,
  "extraction_threshold": "medium",
  "auto_approve": false,
  "learned_skills_path": "~/.config/agent/skills/learned/",
  "patterns_to_detect": [
    "error_resolution",
    "user_corrections",
    "workarounds",
    "debugging_techniques",
    "project_specific"
  ],
  "ignore_patterns": [
    "simple_typos",
    "one_time_fixes",
    "external_api_issues"
  ]
}
```

## Pattern Types

| Pattern | Description |
|---------|-------------|
| `error_resolution` | How specific errors were resolved |
| `user_corrections` | Patterns from user corrections |
| `workarounds` | Solutions to framework/library quirks |
| `debugging_techniques` | Effective debugging approaches |
| `project_specific` | Project-specific conventions |

## Hook Setup

Add a Stop hook to your agent settings:

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "<skills-path>/continuous-learning/evaluate-session.sh"
      }]
    }]
  }
}
```

## Why Stop Hook?

- **Lightweight**: Runs once at session end
- **Non-blocking**: Adds no latency to individual messages
- **Complete context**: Has access to the full session transcript

## v2 Comparison

The v2 instinct-based approach (see `continuous-learning-v2`) offers finer granularity:

| Feature | v1 (this) | v2 (instinct-based) |
|---------|-----------|---------------------|
| Observation | Stop hook (session end) | PreToolUse/PostToolUse hooks |
| Granularity | Full skills | Atomic "instincts" |
| Confidence | None | 0.3–0.9 weighted |
| Evolution | Direct to skill | Instincts → cluster → skill/command/agent |
