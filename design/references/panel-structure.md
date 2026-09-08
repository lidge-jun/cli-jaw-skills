# Panel Structure

Design panel은 Claude Design을 따른다.

## Toolbar

```text
left: reveal pageDir / export / reload from disk
center: page selector dropdown ("ChatCLI Wireframes · 2 pages")
right: zoom / annotate / edit / share with agent
```

## Body

Full viewport preview. artifact.html을 iframe 또는 raw HTML로 렌더.
3-column 분할, Canvas/Source/History 탭, run composer 없음.

## Page Selector Dropdown

Claude Design처럼 toolbar 중앙에 배치:

- 프로젝트명 + page 수 표시 ("ChatCLI Wireframes · 2 pages")
- 클릭 시 dropdown: New blank page, page list, All project files
- 현재 선택된 page는 강조 표시
- page 전환은 이 dropdown으로만

## Right Sidebar Tab

- `Files | Diff | Browser | Design` launcher button
- CEO는 숨김
- Design은 multi-instance kind (Diff는 singleton)
- Launcher click: 첫 번째 열린 Design tab focus, 없으면 create
- `+` 메뉴: 새 Design tab create
- per-tab state: `{ pageId?: string; zoom?: number }`
- tab close/reopen 시 state 복원

## 목업 참조

우측 사이드바 기준안과 빈 상태 목업은 공개 저장소에 없다. 프로젝트의 비공개
기록에 있으니, 필요하면 그 저장소 접근 권한을 가진 사람에게 요청할 것.
