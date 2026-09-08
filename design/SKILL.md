---
name: design
description: "cli-jaw Design workspace: create, preview, run, and export design pages from the right sidebar. Covers panel UX, direct-write workflow, artifact lifecycle, wireframe generation, design system, and Open Design adapter."
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "requires": { "bins": ["cli-jaw"] },
      },
  }
---

# Design Workspace

cli-jaw Design workspace skill. Design tab은 오른쪽 sidebar에서 Files, Diff,
Browser와 동급인 launcher/tab이다.

## Prerequisites

- `cli-jaw serve` running (UI preview, API routes).
- `jaw design` CLI commands (file-first, server fallback).

## Modular References

| File | When to Read | What It Covers |
|------|-------------|----------------|
| `references/panel-structure.md` | Design tab UI 구현 | Claude Design style toolbar + viewport, page selector dropdown |
| `references/page-lifecycle.md` | page CRUD, storage | create/list/show/path/edit, dashboard store layout, project-key |
| `references/direct-write.md` | agent artifact 수정 | safety boundary, file states, watcher, rescan, concurrent access |
| `references/run-and-preview.md` | design run, preview | run state machine, preview sandbox URL, snapshot/restore |
| `references/export-handoff.md` | export, sidebar handoff | export to project, Diff/Browser tab handoff, conflict policy |
| `references/wireframe-guide.md` | 와이어프레임 생성 | artifact 구조, template/catalog, design system reference |
| `references/api-and-cli.md` | API route, CLI command | full route list, jaw design CLI summary, file-first pattern |
| `references/open-design-adapter.md` | Open Design 연동 (v2+) | adapter status/list/import, vendor 안함, optional |

## Core Rules

### Panel Structure (Claude Design style)

```text
toolbar:
  left: reveal pageDir / export / reload from disk
  center: page selector dropdown ("ChatCLI Wireframes · 2 pages")
  right: zoom / annotate / edit / share with agent

body:
  full viewport preview (iframe or raw HTML)
```

3-column 분할, Canvas/Source/History 탭, run composer 없음.
상세: `references/panel-structure.md`.

### Safety Boundary

- 권한 단위: selected `pageDir` 하나.
- dashboard store root 전체 노출 안 함.
- projectDir은 export 때만 touch.
- `realpath` confinement, symlink reject (v1).
- artifact write allowlist: `artifact.html`, `prompt.md`, `page.json`, `assets/*`.
- 상세: `references/direct-write.md`.

### Concurrent Access

50개 managed instance (포트 3457~3506)가 같은 dashboard design store를 공유한다.
Notes식 `baseRevision` 409 conflict 패턴. 상세: `references/direct-write.md`.

### Right Sidebar Integration

- Design은 multi-instance kind (Files/Browser처럼 여러 tab 가능).
- Launcher click: 첫 번째 열린 Design tab focus. 없으면 create.
- per-tab state: `{ pageId?: string; zoom?: number }`.
- 상세: `references/panel-structure.md`.

### v1 Scope

page CRUD + preview + direct-write 감지 + run (Design tab Run button -> selected
instance agent -> artifact 생성) + export 전부 v1에 포함.

## Shipped v1 Surface (2026-07-04)

### CLI (file-first; the store on disk is the source of truth)

```text
jaw design list [--json]                     # pages across projects
jaw design create --title <t> [--json]       # new page (project key snapshot at create)
jaw design show <page-id> [--json]           # page.json summary
jaw design path <page-id> [--json]           # pageDir / artifact / prompt local paths
jaw design rescan [<page-id>] [--json]       # re-read disk state into page.json
jaw design edit <page-id> [--editor ...]     # open pageDir in an editor
jaw design export <page-id> [--overwrite]    # copy artifact into the project dir
jaw design files read <page-id> <relpath>
jaw design files write <page-id> <relpath> --stdin
jaw design snapshots <page-id> list|restore <snapshot-id>
jaw design catalog list [--json]
```

There is NO `jaw design run` in v1. Run is the Design tab toolbar button: it
takes a server-side before-snapshot (hard gate), then enqueues a generation
prompt into the CURRENTLY SELECTED instance's queue.

### Agent contract for a "Design run request" message

When you receive a chat message titled `Design run request`:

1. Read the Brief first (`prompt.md` path given in the message) — it holds the
   page requirements.
2. Your ONLY write target is the given pageDir. Write `artifact.html` in place
   (direct file write or `jaw design files write <page-id> artifact.html --stdin`).
   Allowlist: `artifact.html`, `prompt.md`, `page.json`, `assets/*`.
3. Preview is CSP-locked (`script-src 'none'`): produce STATIC, self-contained
   HTML/CSS. No `<script>`, no external CDN references — inline styles/SVG only.
4. Do not write anywhere else; do not export unless asked. The user reviews the
   result live in the Manager Design tab (watcher/Reload picks it up).
5. A before-snapshot was already taken server-side; restore points live under
   the page `snapshots/` directory (keep-last-20).

### Invariants

- `page.json` is the source of truth; concurrent writers use `baseRevision`
  and get 409 on conflict — rescan, merge, retry.
- HTTP mutator routes (`POST/PATCH/PUT` under `/api/dashboard/design`) require
  the Electron desktop identity header. Agents do NOT call mutator routes —
  use the file-first CLI/direct writes above.
- `realpath` confinement + symlink reject inside pageDir.
