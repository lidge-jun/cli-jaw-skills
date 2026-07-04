# Direct File Write

cli-jaw의 핵심 장점: agent가 `pageDir/artifact.html`을 직접 쓴다.

## Safety Boundary

- 권한 단위: selected `pageDir` 하나
- dashboard store root 전체 노출 안 함
- projectDir은 export 때만 touch
- `realpath(root)` + `realpath(target)` confinement
- v1은 symlink reject
- artifact write allowlist: `artifact.html`, `prompt.md`, `page.json`, `assets/*`

## File States

| State | Trigger | UI |
|-------|---------|-----|
| clean | disk = cache | 표시 없음 |
| external change detected | agent/editor가 artifact 수정 | toolbar "Reload from disk" |
| preview stale | active run writing | 마지막 안정 preview 유지 |
| schema warning | page.json validation 실패 | toolbar warning badge |
| snapshot available | before-run snapshot 존재 | "Compare with last snapshot" |
| export out of sync | artifact != project export | "Re-export" |

## File Watcher

`fs.watch` + explicit `rescan` fallback (Notes watcher 패턴).
debounce 300ms로 preview refresh. 실패 시 `rescan`이 authoritative recovery.
직접 수정된 파일은 Manager 재시작 후에도 scan으로 복구 가능해야 한다.

```bash
jaw design rescan [--project <dir>] [--json]
```

## Concurrent Access

50개 managed instance (포트 3457~3506)가 같은 dashboard design store를 공유.

- `page.json`에 `revision` 필드
- API write 시 `baseRevision`이 현재 `revision`과 다르면 409 conflict
- UI: Reload / Overwrite / Keep local 선택지 제공
- agent direct-write: `rescan` 시 revision mismatch 감지
- Notes store의 `baseRevision` 409 패턴을 이식
