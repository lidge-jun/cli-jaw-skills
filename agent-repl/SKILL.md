---
name: agent-repl
description: Persistent REPL sessions with model switching, branching, and export. Manage multi-turn agent conversations as session files.
---

# Agent REPL

Manage persistent REPL sessions for multi-turn agent conversations.

## Capabilities

- Persistent markdown-backed sessions
- Model switching between conversations
- Dynamic skill loading per session
- Session branching for exploratory paths
- Cross-session search
- History compaction after milestones
- Export to md/json/txt

## Operating Guidance

1. Keep sessions task-focused.
2. Branch before high-risk changes.
3. Compact after major milestones.
4. Export before sharing or archival.

## Extension Rules

- Keep zero external runtime dependencies.
- Preserve markdown-as-database compatibility.
- Keep command handlers deterministic and local.
