# Wireframe / Mockup Generation Guide

## Artifact Structure

생성된 wireframe/mockup은 `artifact.html`로 저장.

- dark theme 기본, `color-scheme: dark` CSS 변수 사용
- 실제 앱 UI를 반영하는 도구형 디자인: 고밀도, 8px radius, Inter font
- card-in-card 금지, gradient orbs 금지
- 와이어프레임은 상태별 카드로 표현 (Claude Design의 turn/section 패턴)

## Template / Catalog

```bash
jaw design catalog list [--json]
jaw design create --template <template-id>
```

v1 template 종류:
- `wireframe`: HTML layout wireframe
- `page`: UI screen mockup
- `document`: spec/document draft

## Design System

기존 프로젝트의 디자인 토큰을 읽어서 artifact에 반영:

- CSS custom properties 기반 color/typography/spacing
- dark/light mode 대응
- `page.json`에 `designSystem` reference를 기록
