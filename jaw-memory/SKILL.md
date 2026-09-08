---
name: jaw-memory
description: "Persistent long-term memory across sessions. Search, read, and save durable knowledge in the current instance; use dashboard memory only for explicit read-only cross-instance lookup."
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

## Scope: L1 vs L2

- **L1 instance-local memory**: `cli-jaw memory search/read/save`; default path; current instance only; read/write.
- **L2 dashboard memory**: `cli-jaw dashboard memory search/read/instances`; cross-instance federation; read-only.
- Use L2 only when the user asks for dashboard memory, all instances, another instance/home, or cross-instance context.
- Save stable facts only through L1 `cli-jaw memory save`.
- Embedding search is optional and default OFF; do not assume it is enabled.

## Commands

### Search

```bash
cli-jaw memory search "keyword"
cli-jaw memory search "user preference"
cli-jaw memory search "auth login 401"
cli-jaw memory search "launchd plist service"
cli-jaw dashboard memory search "cross-instance topic"
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

## Chat Search (L1)

Search past conversation messages in the current instance. Use when you need prior conversation context — what was discussed, decided, or debugged.

```bash
cli-jaw chat search "<keywords>"
cli-jaw chat search "<keywords>" --days 3          # limit to recent N days
cli-jaw chat search "<keywords>" --recent 100      # limit to most recent N messages (~50 Q&A pairs)
cli-jaw chat search "<keywords>" --context 2       # show ±N surrounding messages
cli-jaw memory search "<keywords>" --chat          # search memory AND recent chat history together
```

Use `chat search` when memory search returns nothing but the fact was discussed in a prior conversation. Combine `--recent` and `--context` for focused lookups.

## Context (memory→chat jump)

Find chat messages related to a memory file by its creation time and keywords.

```bash
cli-jaw memory context structured/semantic/cli-jaw.md
cli-jaw memory context structured/episodes/live/2026-06-08.md --window 8
cli-jaw memory context feedback_no-idle-waiting.md --window 2 --limit 5
```

How it works:
- Uses `created_at` frontmatter (or file mtime) as the time center
- Extracts keywords from `name:` → `description:` → filename stem → `kind:` → body first line
- Splits compound terms into individual words for OR-based LIKE search
- Searches `messages` DB in a ±window hour range (default 4 hours)
- Cross-session — not limited to one conversation

### L2 Chat Search

Search jaw.db chat messages across all registered instances (read-only).

```bash
cli-jaw dashboard chat search "memory architecture"
cli-jaw dashboard chat search "auth" --instance 3457,3458
cli-jaw dashboard chat search "deploy" --days 7 --limit 20
cli-jaw dashboard chat search "error" --json
```

How it works:
- Opens each instance's `jaw.db` in readonly mode
- Schema probe: auto-detects `tool_log` column for extended search
- Reports warnings for native module mismatch, missing DB, schema issues
- Results sorted by `created_at` DESC across all instances

## Notes

- Prefer concise, durable entries over verbose logs
