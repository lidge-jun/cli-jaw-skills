# Design Run & Preview

## Run

v1에 포함. prompt -> agent -> artifact 생성:

```bash
jaw design run <page-id> --prompt "..." --provider anthropic --model claude-opus-4.6 --reasoning medium --watch
```

### Run State

| State | Description |
|-------|-------------|
| queued | run 대기 |
| running | agent가 artifact 생성 중 |
| streaming | artifact 스트리밍 (direct-write) |
| done | 완료, after snapshot 생성 |
| error | 실패, before snapshot에서 restore 가능 |
| canceled | 사용자 취소 |

Run 중 preview: 마지막 안정 artifact를 유지하다가 run 완료 시 refresh.
agent는 `pageDir/artifact.html`을 직접 쓰고, Manager는 debounce 300ms `fs.watch`로 감지.

## Snapshot / Restore

- run 시작 전 before snapshot은 hard gate
- run 종료 후 after snapshot은 성공/실패 모두 남긴다
- restore 전 현재 상태를 recovery snapshot으로 남긴다

```bash
jaw design snapshots <page-id> list
jaw design snapshots <page-id> restore <snapshot-id>
```

## Preview

Manager가 서빙하는 sandbox URL:

```text
GET /api/dashboard/design/pages/:pageId/preview
```

- iframe `sandbox` attribute로 스크립트 범위 제한
- CSP header로 asset 범위 제한
- BrowserPanel은 `http/https`만 허용하므로 `file://` 대신 이 URL 사용
- Browser tab에서 같은 URL을 열면 Browser/CDP 도구로 검사 가능
