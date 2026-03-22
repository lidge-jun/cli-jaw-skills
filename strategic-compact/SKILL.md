---
name: strategic-compact
description: Manual context compaction at logical workflow boundaries to preserve context through task phases.
---

# Strategic Compact

Suggests manual compaction at strategic points rather than relying on arbitrary auto-compaction.

## When to Use

- Running long sessions approaching context limits (200K+ tokens)
- Working on multi-phase tasks (research → plan → implement → test)
- Switching between unrelated tasks within the same session
- After completing a major milestone
- When responses slow down or become less coherent (context pressure)

## Why Strategic Compaction?

Auto-compaction triggers at arbitrary points — often mid-task, losing important context with no awareness of logical boundaries.

Strategic compaction at logical boundaries:
- **After exploration, before execution** — compact research context, keep implementation plan
- **After completing a milestone** — fresh start for next phase
- **Before major context shifts** — clear exploration context before a different task

## Hook Setup

The `suggest-compact.js` script runs on PreToolUse (Edit/Write) and tracks tool calls, suggesting compaction at a configurable threshold (default: 50 calls), with reminders every 25 calls after.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{ "type": "command", "command": "node scripts/suggest-compact.js" }]
      },
      {
        "matcher": "Write",
        "hooks": [{ "type": "command", "command": "node scripts/suggest-compact.js" }]
      }
    ]
  }
}
```

Environment variable: `COMPACT_THRESHOLD` — tool calls before first suggestion (default: 50).

## Compaction Decision Guide

| Phase Transition | Compact? | Why |
|-----------------|----------|-----|
| Research → Planning | Yes | Research context is bulky; plan is the distilled output |
| Planning → Implementation | Yes | Plan is saved to a file; free up context for code |
| Implementation → Testing | Maybe | Keep if tests reference recent code; compact if switching focus |
| Debugging → Next feature | Yes | Debug traces pollute context for unrelated work |
| Mid-implementation | No | Losing variable names, file paths, and partial state is costly |
| After a failed approach | Yes | Clear the dead-end reasoning before trying a new approach |

## What Survives Compaction

| Persists | Lost |
|----------|------|
| Project config / instructions | Intermediate reasoning and analysis |
| Task lists (saved to file) | File contents previously read |
| Memory files | Multi-step conversation context |
| Git state (commits, branches) | Tool call history and counts |
| Files on disk | Nuanced preferences stated verbally |

## Best Practices

1. **Compact after planning** — once the plan is saved to a file, compact to start fresh
2. **Compact after debugging** — clear error-resolution context before continuing
3. **Preserve mid-implementation context** — keep context for related changes
4. **Write before compacting** — save important context to files or memory first
5. **Add a summary when compacting** — e.g., "Focus on implementing auth middleware next"

## Token Optimization Patterns

### Trigger-Table Lazy Loading
Instead of loading full skill content at session start, use a trigger table mapping keywords to skill paths. Skills load only when triggered, reducing baseline context by 50%+.

### Context Composition Awareness
Monitor what consumes the context window:
- Project config — always loaded, keep lean
- Loaded skills — each adds 1–5K tokens
- Conversation history — grows with each exchange
- Tool results — file reads, search results add bulk

### Duplicate Instruction Detection
Common sources of duplicate context:
- Same rules in global and project-level configs
- Skills that repeat project config instructions
- Multiple skills covering overlapping domains
