# Export & Sidebar Handoff

## Export

```bash
jaw design export <page-id> [--target design/<slug>.html] [--overwrite] [--json]
```

- export target: selected `projectDir` 내부 relative path만 허용
- 기본값: no-overwrite. 충돌 시 409 + existing revision/mtime/size 반환
- export 후 Diff tab을 자동 focus하고 변경분 표시
- Browser tab은 preview URL을 열되, 같은 URL tab이 있으면 focus

## Sidebar Handoff

- Export 후 Diff tab 자동 focus
- "Open in Browser" 클릭 시 preview URL을 Browser tab으로 열기
- 같은 preview URL tab이 있으면 focus
- Files에서 exported file 더블클릭 시 Design page로 역추적

## 목업 참조

- `devlog/_plan/260705.../183_design_export_handoff_tabs_mockup.html`
