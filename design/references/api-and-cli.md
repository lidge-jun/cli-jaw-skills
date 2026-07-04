# API Routes & CLI

## API Routes (shipped v1)

```text
GET   /api/dashboard/design/version
GET   /api/dashboard/design/pages
POST  /api/dashboard/design/pages                      [desktop]
POST  /api/dashboard/design/pages/rescan
GET   /api/dashboard/design/pages/:pageId
PATCH /api/dashboard/design/pages/:pageId              [desktop]
GET   /api/dashboard/design/pages/:pageId/files/*
PUT   /api/dashboard/design/pages/:pageId/files/*      [desktop]
GET   /api/dashboard/design/pages/:pageId/local-paths
POST  /api/dashboard/design/pages/:pageId/rescan
POST  /api/dashboard/design/pages/:pageId/export       [desktop]
POST  /api/dashboard/design/pages/:pageId/snapshots    [desktop]
GET   /api/dashboard/design/pages/:pageId/snapshots
POST  /api/dashboard/design/pages/:pageId/snapshots/:snapshotId/restore  [desktop]
GET   /api/dashboard/design/catalog
GET   /api/dashboard/design/pages/:pageId/preview
```

- prefix: `/api/dashboard/design` (기존 dashboard convention).
- `[desktop]` = mutator; requires the Electron desktop identity header.
  Agents must NOT call these — use the file-first CLI below instead.
- `/preview`는 HTML 응답 (JSON-only가 아님), CSP `script-src 'none'`.

## CLI Summary (shipped v1)

```text
jaw design list [--json]
jaw design create --title <t> [--json]
jaw design show <page-id> [--json]
jaw design path <page-id> [--json]
jaw design rescan [<page-id>] [--json]
jaw design edit <page-id> [--editor cursor|code|finder|terminal]
jaw design export <page-id> [--overwrite] [--json]
jaw design files read <page-id> <relpath>
jaw design files write <page-id> <relpath> --stdin
jaw design snapshots <page-id> list
jaw design snapshots <page-id> restore <snapshot-id>
jaw design catalog list [--json]
```

CLI 패턴: file-first (store 직접 읽기/쓰기). export/restore만 서버 상태에
의존한다.

## Run (NOT a CLI command in v1)

`jaw design run`은 v1에 존재하지 않는다. Run = Design tab toolbar button:

1. 서버가 before-snapshot을 강제로 생성 (hard gate).
2. 선택된 instance의 큐에 `Design run request` 프롬프트를 enqueue.
3. 그 instance의 agent가 pageDir 안에서 `artifact.html`을 갱신
   (allowlist: `artifact.html`, `prompt.md`, `page.json`, `assets/*`).
4. watcher/Reload가 결과를 Design tab preview에 반영.
