---
name: memory
description: "Persistent long-term memory across sessions. Search, read, and save durable knowledge."
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "requires": null,
        "install": null,
      },
  }
---

# Long-term Memory

## Rules

1. **Search before answering** about past work, decisions, or preferences — run `cli-jaw memory search <keywords>` first.
2. **Save durable facts immediately** — user preferences, key decisions, stable project facts.
3. **Use structured destinations** — prefer `structured/profile.md`, `structured/semantic/...`, or `structured/episodes/...`.
4. **Admit gaps** — if search returns nothing, say "I don't have a record of that."
5. **Save stable facts only** — not transient TODOs, phase logs, or temporary checklists.
6. **Search broadly** — consider Korean/English variants, error codes, symbols, and filenames.
7. **Use injected context** — a task snapshot may be in the prompt; still search when precision matters.

## Commands

### Search

```bash
cli-jaw memory search "keyword"
cli-jaw memory search "user preference"
cli-jaw memory search "auth login 401"
cli-jaw memory search "launchd plist service"
```

### Read

```bash
cli-jaw memory read structured/profile.md
cli-jaw memory read structured/semantic/cli-jaw.md
cli-jaw memory read structured/episodes/live/2026-03-07.md
cli-jaw memory read structured/profile.md --lines 1-30
```

### Save

```bash
cli-jaw memory save structured/profile.md "- User prefers Korean UI and English code"
cli-jaw memory save structured/semantic/cli-jaw.md "- Memory runtime uses task snapshots before response generation"
cli-jaw memory save structured/episodes/live/2026-03-07.md "## 16:30\n- Decided to remove query-provider setup from memory UX"
```

### List & Init

```bash
cli-jaw memory list
cli-jaw memory init
```

## Storage Layout

| Path | Purpose |
| --- | --- |
| `{{JAW_HOME}}/memory/structured/profile.md` | Stable profile, preferences, long-lived project context |
| `{{JAW_HOME}}/memory/structured/episodes/` | Time-ordered episodic memory |
| `{{JAW_HOME}}/memory/structured/semantic/` | Durable facts and extracted knowledge |
| `{{JAW_HOME}}/memory/structured/procedures/` | Reusable workflows and rules |
| `{{JAW_HOME}}/memory/structured/sessions/` | Optional session-derived memory |
| `{{JAW_HOME}}/memory/structured/index.sqlite` | Search index |

## Workflows

### New Conversation

1. Use injected memory context if present
2. Search memory if the task depends on prior decisions or preferences
3. Read the relevant file when exact wording or details matter

### User Mentions a Preference

1. Acknowledge briefly
2. Save to `structured/profile.md`
3. If it is project-specific, also save to an appropriate semantic file

### User Asks "Do you remember...?"

1. Run `cli-jaw memory search "<keywords>"`
2. If found, answer with the remembered fact and cite the source file
3. If not found, say there is no saved record and offer to save it

### End of Important Session

1. Save the durable decision or fact
2. Use episodic files for time-bound outcomes
3. Use semantic/profile files for long-lived knowledge

## Notes

- Prefer concise, durable entries over verbose logs
