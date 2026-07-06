---
name: repo-map
description: "Ranked repository structure map via `cli-jaw map`. Use for codebase overview, structure map, symbol overview, unfamiliar codebase exploration, architecture orientation. Triggers: repo map, structure map, codebase overview, 와꾸, project structure, unfamiliar code."
---

# repo-map

`cli-jaw map` prints a compact, ranked symbol overview of a repository or subtree.
It scans TS/JS-family sources, extracts definitions (functions, classes,
interfaces, types, enums, exported consts, class methods), counts cross-file
identifier references, and lists files ordered by reference gravity with their
definitions and line numbers, cut to a token budget.

Reach for it before deep Grep dives when entering unfamiliar code: the map shows
the project shape — which files own which symbols and where the likely
architectural center is — so subsequent Grep/Read calls are targeted instead of
exploratory.

## Grep and map boundaries

Use Grep for text: literal strings, comments, config values, exact symbol
lookups, and regex searches.

Use this skill for an overview map, not exact search. The map is a guide for
where to inspect next, not proof that a symbol is absent. After the map narrows
the territory, confirm targets with Grep/Read.

## When to use this skill

- "Give me a structure map of this package."
- "I am in unfamiliar code; show me the shape first."
- "What files define the main symbols in this subtree?"
- "와꾸 먼저 보자."

## CLI usage

```bash
cli-jaw map .                  # map the current repo
cli-jaw map src/ --budget 2048 # subtree map with a tighter budget
```

- `<path>` defaults to `.`; both files and directories are accepted.
- `--budget N` sets the approximate token budget (default 4096; tokens are
  estimated as chars/4).
- Common non-source dirs (`.git`, `node_modules`, `dist`, `build`, `target`,
  `out`, `coverage`, hidden dirs) are skipped during the walk.

## Subtree maps for large monorepos

`cli-jaw map <subdir>` scopes BOTH the walk and the ranking to that subtree: the
reference counts are computed only from files under `<subdir>`, so
feature-partitioned monorepos get per-feature maps whose central files are not
drowned out by global hubs. Prefer a subtree map plus a tight budget over one
giant whole-repo map.

## Ranking and coverage (v1)

- Ranking is reference-count gravity (how often a file's definitions are named
  across the scanned set), not PageRank. It is deterministic and dependency-free.
- Language tier: TS/JS family (`.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`, `.cjs`) is
  the supported set. Other languages are not scanned in v1.
- Extraction is a line-based definition scan, honest about its limits: exotic
  syntax may be missed. Treat the map as orientation, then inspect the surfaced
  files.

## Degradation

- `cli-jaw map --help` prints usage and exits 0 with no engine work.
- An unreadable or missing path prints one hint line and exits 1 — never a stack
  trace.

## Doctrine

On-demand only: the map body is never preloaded into the system prompt or cached
by a daemon. Generate it fresh when needed; a stale map is worse than no map.
