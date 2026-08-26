---
name: jaw-diagram
description: "SVG diagrams, charts, and interactive visualizations for chat UI"
metadata:
  version: "1.3.0"
capabilities:
  - "SVG: structural diagrams, comparisons, timelines, mockups, art"
  - "Mermaid: flowchart, sequence, ER, state, timeline, mindmap, gantt, pie, radar, git graph, block, venn-beta"
  - "Native chart shortcut: chart-json for simple single-series bar, line, and pie charts"
  - "Charts (Chart.js): bar, line, pie, scatter, doughnut, polar"
  - "Charts (ECharts): heatmap, sankey, radar, treemap, gauge, funnel, candlestick, chord"
  - "Maps (Leaflet): interactive maps with markers, popups, dark mode"
  - "Interactive: sliders, toggles, sendPrompt, physics (Matter.js), 3D (Three.js), audio (Tone.js), creative (p5.js)"
references:
  - "svg-components.md — SVG primitives, layout templates"
  - "color-palette.md — 9-color design system"
  - "module-chart.md — Chart.js + ECharts + D3"
  - "korean-text.md — Korean/CJK text in SVG, HTML, D3, Chart.js, Mermaid, PDF embedding"
  - "structured-renderers.md — native renderer delegation notes"
  - "module-interactive.md — controls, sendPrompt, debouncing"
  - "module-widget.md — physics, 3D, audio, creative coding"
  - "module-map.md — Leaflet maps"
  - "module-mockup.md — UI mockup patterns"
  - "module-art.md — decorative SVG"
  - "module-domain-cards.md — weather, finance, sports, product card templates"
---

# Diagram Visualization Skill

## Design Principles

- **Flat**: No gradients, shadows, blur, glow, or decorative effects. Clean flat surfaces only.
- **Compact**: Show the essential inline. Explain the rest in response text.
- **Theme-aware**: Every color must work in both light and dark mode. Use CSS classes for SVG, `window.__jawTokens` for canvas/JS.
- **Text in response, visuals in tool**: All explanatory prose goes outside the diagram. Never put paragraphs of explanation inside the SVG or widget HTML.

## Complexity Budget — Hard Limits

- Box subtitles: **≤5 words**. Detail goes in `sendPrompt()` or prose — not the box.
- Colors: **≤2 ramps** per diagram. More = visual noise.
- Horizontal row: **≤4 boxes** at 680px width. 5+ boxes → shrink or wrap to 2 rows.
- Nodes: **≤6 per diagram**. 7+ → split into overview + detail diagrams.
- **Always add prose between diagrams** — never output consecutive SVG blocks or widget blocks without text between them.

## Diagram Type Selection

Route on the verb, not the noun. Same subject gets different diagrams. Prefer Mermaid when the diagram type maps cleanly to a native Mermaid syntax — it's cheaper than hand-rolling SVG.

| User says / intent | Type | Output |
|---|---|---|
| "how does X work" | Illustrative SVG | Spatial metaphor, cross-section, physical layout |
| "architecture of X" (system context) | Structural SVG | Containers, regions, nesting |
| "steps of X" (generic process) | Flowchart SVG or Mermaid `flowchart` | Top-down boxes + arrows |
| "compare A vs B" | Comparison SVG | Side-by-side columns |
| "DB schema / entity relationship" | Mermaid | ` ```mermaid ` `erDiagram` |
| "class diagram / OOP structure" | Mermaid | ` ```mermaid ` `classDiagram` |
| "state machine / lifecycle" | Mermaid | ` ```mermaid ` `stateDiagram-v2` |
| "sequence / call order / API flow" | Mermaid | ` ```mermaid ` `sequenceDiagram` |
| "timeline / roadmap / history" | Mermaid | ` ```mermaid ` `timeline` |
| "mind map / brainstorm / outline" | Mermaid | ` ```mermaid ` `mindmap` |
| "git branching / release history" | Mermaid | ` ```mermaid ` `gitGraph` |
| "2×2 matrix / priority quadrant" | Mermaid | ` ```mermaid ` `quadrantChart` |
| "radar / spider / skill profile" | Mermaid v11.6+ (beta) | ` ```mermaid ` `radar-beta` |
| "gantt / project schedule" | Mermaid | ` ```mermaid ` `gantt` |
| "user journey map" | Mermaid | ` ```mermaid ` `journey` |
| "pie breakdown (simple)" | Mermaid | ` ```mermaid ` `pie` |
| "kanban board" | Mermaid v11.12+ (beta, test before use) | ` ```mermaid ` `kanban` |
| "cloud/infra architecture" | Mermaid (beta) | ` ```mermaid ` `architecture-beta` |
| "hierarchy / proportional size" | Mermaid (beta) | ` ```mermaid ` `treemap-beta` |
| "free-form block layout" | Mermaid | ` ```mermaid ` `block` |
| "packet / network frame" | Mermaid | ` ```mermaid ` `packet` |
| "ishikawa / fishbone / cause-effect" | Mermaid | ` ```mermaid ` `ishikawa` |
| "swimlane / lane-based workflow" | Mermaid | ` ```mermaid ` `swimlane-beta` |
| "requirement / traceability" | Mermaid | ` ```mermaid ` `requirementDiagram` |
| "sankey / flow quantity" | Mermaid | ` ```mermaid ` `sankey` |
| "XY chart / scatter / line" | Mermaid | ` ```mermaid ` `xychart` |
| "venn / overlap / set intersection" | Mermaid (beta) | ` ```mermaid ` `venn-beta` |
| "show sources / search results / citations" | `structured-renderers` skill | Non-diagram native card: load `structured-renderers` for `search-results` schema |
| "write / draft / compose email, message, document" | `structured-renderers` skill | Non-diagram native card: load `structured-renderers` for `compose-block` schema |
| "table / rows / sortable data / filterable data" | `structured-renderers` skill | Non-diagram native card: load `structured-renderers` for `dataframe` schema |
| "patch / diff / unified diff" | `structured-renderers` skill | Non-diagram native display: load `structured-renderers` for `diff` routing |
| "show data / chart" | `chart-json` for simple bar/line/pie; diagram-file for advanced charts | For `chart-json`, load `structured-renderers`; use file-backed Chart.js / D3 / ECharts iframe widgets when custom JS, maps, advanced chart types, or richer interactivity are required |
| "simulate / interactive" | diagram-file | File-backed Matter.js / Canvas / sliders widget |
| "large widget / iterative widget editing" | diagram-file | Default for all HTML widgets: write the full widget HTML to `~/.cli-jaw/widgets/<chatId>/<widgetId>.html`, then emit an id-only file-backed fence |
| "interactive map (with pan/zoom/markers)" | diagram-file | File-backed Leaflet iframe widget — see `reference/module-map.md` |
| "static country/state choropleth" | diagram-file | File-backed D3 + TopoJSON widget — see `reference/module-chart.md` |

Default to illustrative SVG for "how does X work?" — don't default to flowchart. Default to Mermaid when the type is in the table above — don't hand-roll an SVG when `classDiagram`/`sequenceDiagram`/`stateDiagram` already exists.

`diagram-file` is the default for all HTML widget types. Use `diagram-html` only as a fallback when the chatId cannot be determined or for very small throwaway widgets that do not warrant a file.

### Native Web UI renderer boundary

Before producing a `diagram-file` HTML widget, check whether a native renderer is a better fit:

- Load `structured-renderers` for `search-results`, `compose-block`, `dataframe`, `chart-json`, and `diff` schemas.
- Use `chart-json` for simple single-series bar/line/pie charts.
- Stay in `diagram` and use `diagram-file` for maps, multi-series charts, advanced chart types, custom JavaScript, external libraries, or richer interaction.

These renderers are lighter than HTML widgets, survive sanitizer/hydration, and avoid iframe overhead. They are final-answer-only structured fences; during streaming they remain inert code blocks. Keep JSON complete, compact, and schema-versioned. See the active `structured-renderers` skill for canonical schemas and examples.

### Mermaid gotchas (read before using beta/experimental types)

- **Do NOT use C4 diagrams** (`C4Context`, `C4Container`, etc.) — theme tokens are not applied in dark mode, text becomes unreadable ([mermaid #4906](https://github.com/mermaid-js/mermaid/issues/4906)). Substitute routing:
  - **C4 System Context** → Structural SVG (custom) OR Mermaid `flowchart` with subgraphs
  - **C4 Container** → Mermaid `architecture-beta` (cloud/infra layout)
  - **C4 Component** → Mermaid `flowchart` with `subgraph` grouping
  - **C4 Dynamic** → Mermaid `sequenceDiagram`
  - **C4 Deployment** → Mermaid `architecture-beta`
- **`sankey-beta` / `xychart-beta`** — known to break scale-down at narrow chat widths. Prefer `diagram-file` + ECharts sankey for flow diagrams, Chart.js for simple XY.
- **Now stable (no suffix needed):** `block`, `packet`, `kanban`, `sankey`, `xychart`, `ishikawa`.
- **Still beta (suffix required):** `radar-beta`, `architecture-beta`, `treemap-beta`, `venn-beta`, `wardley-beta`, `treeView-beta`, `cynefin-beta`, `swimlane-beta`. Test beta types in the cli-jaw Web UI before finalizing.
- **`sandbox` securityLevel iframe background bug** ([mermaid #5034](https://github.com/mermaid-js/mermaid/issues/5034)) — affects host rendering, not your output. No action needed from the agent.
- **Theme**: all stable Mermaid types pick up the host dark/light theme automatically via cli-jaw's `themeVariables`. Do NOT set explicit colors in `%%{init: ...}%%` unless overriding for semantic reasons.

## When to Use

### 1. Explicit request (명시적 요청)

한국어: "그려줘", "시각화", "다이어그램", "차트로", "도표로", "비교표", "플로우차트"
영어: "draw", "visualize", "diagram", "chart", "graph", "illustrate", "show me"

### 2. Proactive generation (에이전트 판단)

다음 상황에서 텍스트만으로는 전달이 부족할 때 자동 생성:
- 시스템/프로세스 아키텍처 설명 (3+ 컴포넌트)
- 데이터 3항목 이상 비교
- 프로세스 5단계 이상 설명
- 계층 구조 (트리 2+ 레벨)
- 타임라인/히스토리 (4+ 이벤트)
- 수학적 관계 시각화

### 3. Specification (명사구 스펙)

사용자가 시각물의 구조를 명사구로 기술:
- "X vs Y 비교" → comparison layout
- "X 구조" / "X 아키텍처" → architecture diagram
- "X 플로우" → flowchart
- "X 타임라인" → timeline

### 4. When NOT to use

- 단순 질의응답 (팩트 한 줄이면 충분)
- 코드 리뷰/디버깅 (코드가 더 명확)
- 이미 diagram-html 내에서 동작 중인 위젯 재생성
- 사용자가 "간단히 설명해줘"라고 한 경우

## Delivery Mechanism (read before producing anything)

All four formats — inline SVG, ` ```mermaid `, ` ```diagram-file `, ` ```diagram-html ` — are **rendered inline in the chat response**. The jaw frontend parses your reply text and mounts them automatically. `diagram-file` and `diagram-html` go into sandboxed `<iframe>` elements that the host creates; you do **not** create the iframe.

### File-backed widgets (`diagram-file`)

Use ` ```diagram-file ` as the default for all HTML widget output, including charts, maps, simulations, controls, games, and custom JavaScript widgets. Write the full widget HTML first to `~/.cli-jaw/widgets/<chatId>/<widgetId>.html`, following the same HTML rules as `diagram-html`: the host renders it through the validator and sandboxed iframe, with the same CDN allowlist and theme token expectations.

The fence body is id-only: `{"id": "<widgetId>"}`. A bare widget id string is also accepted. Do not put paths in the fence; the host resolves `<current chatId>/<widgetId>.html` by convention. The file-backed cap is 2 MB, while inline `diagram-html` remains capped at 512 KB. File-backed widgets are mutable: editing the saved HTML updates every message that references the same id. Save under a new id when a frozen version is needed.

Determine the current chatId from runtime context when available. If it is not determinable, use inline `diagram-html` as the fail-safe. `diagram-html` is also acceptable for very small throwaway widgets that do not warrant a file.

| ❌ Don't | ✅ Do |
|---|---|
| Save SVG/Mermaid outputs to `.svg` / `.png` files unless explicitly asked | Paste SVG/Mermaid blocks directly into your reply |
| Wrap `diagram-html` in your own `<iframe>` / `<html>` / `<body>` / `<head>` | Start at `<div>` / `<canvas>` / `<style>` — host injects the shell |
| Send via `/api/channel/send` or Telegram/Discord — it is NOT an attachment | Let the renderer handle it; diagrams are response text |
| Reference an external image URL and call it a diagram | Output the SVG/widget code itself |

If the user says "save this diagram" or "download it", still output it inline first so they see it rendered; only write a file if they explicitly ask for a file on disk (and even then, the inline version is the canonical delivery).

## Output Formats

### 1. Inline SVG (static diagrams)
Output raw `<svg>` markup directly in the response. The chat UI renders it inline.

```
<svg viewBox="0 0 680 {height}" xmlns="http://www.w3.org/2000/svg"
  role="img" aria-labelledby="title-id desc-id">
  <title id="title-id">Diagram Title</title>
  <desc id="desc-id">Brief description for screen readers</desc>
  <!-- shapes, text, paths -->
</svg>
```

Rules:
- viewBox width MUST be 680 (matches container width — do NOT change)
- Height varies by content: last element bottom + 40px padding
- Every SVG MUST have `role="img"` + `<title>` + `<desc>`
- Use classes from the design system (`.node`, `.connector`, `.label`, `.label-start`, etc.) — `.label` forces `text-anchor: middle` (centered text only); for left-aligned text use `.label-start` or just the color class
- Colors: use CSS classes, not inline fill/stroke colors
- Text: `font-family` inherited from host (do NOT set explicit fonts)

### 2. Mermaid (simple flowcharts, ERDs)
Use standard ` ```mermaid ` code blocks. The existing renderer handles these.

### 3. Interactive HTML Widget (fallback form: charts, controls, simulations)
Use ` ```diagram-file ` by default. Wrap in a ` ```diagram-html ` code block only when the chatId cannot be determined or the widget is a very small throwaway. Rendered inside a sandboxed iframe.

```
` ` `diagram-html
<div id="chart-wrapper" style="position: relative; width: 100%; height: 300px;">
  <canvas id="myChart" role="img" aria-label="Chart description">
    Fallback text
  </canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"
  onerror="document.body.innerHTML='<p>Chart library failed to load.</p>'">
</script>
<script>
  const isDark = window.__jawTheme?.isDark ?? true;
  // ... Chart.js code
</script>
` ` `
```

## SVG Design System

### Design Forbidden List
These are design quality rules (separate from security restrictions below):
- No gradients, drop shadows, blur, glow, or neon effects
- No emoji — use CSS shapes or SVG paths
- No decorative step numbers or oversized headings
- No icons or illustrations inside flowchart boxes — text only
- No rotated text
- No dark/colored backgrounds on outer containers (transparent only — host provides bg)
- Stroke width: **0.5px** for borders and edges (not 1px or 2px)
- Font weights: **400** (regular) and **500** (bold) only. Never 600 or 700.
- Font sizes in SVG: **14px** (node labels) and **12px** (subtitles/arrow labels) only
- **Sentence case** always. Never Title Case or ALL CAPS.

### `<style>` in Inline SVG

`<style>` tags inside inline SVG ARE preserved. Custom CSS classes work:

```xml
<svg viewBox="0 0 100 100">
  <style>
    .highlight { fill: #e94560; }
    .dim { fill: #94a3b8; }
  </style>
  <rect class="highlight" width="50" height="50"/>
</svg>
```

**Security filters applied automatically:**
- `@import` rules → stripped
- `@font-face` blocks → stripped
- External `url()` → replaced with `none` (internal `url(#ref)` preserved)

**Best practice:** Prefer predefined `.c-*` classes (see `reference/color-palette.md`) for theme-aware colors. Use custom `<style>` when you need colors/patterns not in the design system.

### Forbidden in Inline SVG (Security)
These are stripped by DOMPurify — NEVER use in inline `<svg>`:
- `<foreignObject>` — embeds HTML in SVG (XSS vector)
- `<animate>`, `<set>`, `<animateTransform>`, `<animateMotion>` — animation XSS vectors
- Nested `<svg>` — use `<g>` groups instead

### Forbidden Attributes in Inline SVG
- `xlink:href` — use `href="#fragment"` on `<use>` only (no external URLs)
- All `on*` event handlers (onclick, onerror, etc.) — stripped by DOMPurify

> **Note**: `diagram-file` and fallback `diagram-html` content run inside a sandboxed iframe where
> `<script>`, `on*` handlers, and CDN imports ARE allowed. The restrictions
> above apply only to inline SVG rendered in the main document.

### Color Ramps (9 semantic colors)
Each ramp has 3 shades: fill (bg), stroke (border), text (label).
Use CSS class names — see `reference/color-palette.md`:

| Ramp | Class prefix | Preferred use |
|---|---|---|
| cyan | `.c-cyan` | General categories (preferred for neutral info) |
| pink | `.c-pink` | General categories, highlights |
| purple | `.c-purple` | General categories, grouping |
| orange | `.c-orange` | General categories, accent |
| slate | `.c-slate` | Neutral, disabled, structural (start/end nodes) |
| blue | `.c-blue` | Informational (semantic — use only when meaning is "info") |
| green | `.c-green` | Success, positive (semantic) |
| amber | `.c-amber` | Warning, attention (semantic) |
| red | `.c-red` | Error, negative (semantic) |

**Color assignment**: color encodes **meaning**, not sequence. Don't cycle through colors like a rainbow. Group by category — all nodes of the same type share one color. Prefer cyan/pink/purple/orange for general categories. Reserve blue/green/amber/red for genuinely semantic concepts.

### Layout Patterns
- Flowchart: top-to-bottom, 680×auto
- Comparison: side-by-side columns
- Timeline: horizontal with markers
- Org chart: hierarchical tree
- See `reference/svg-components.md` for templates and detailed SVG rules.

### Style-First, Script-Last
For `diagram-file` widgets and fallback `diagram-html` widgets:
1. All `<style>` and `<link>` tags first
2. HTML structure
3. `<script>` tags last

This ensures visual content appears before scripts execute (important during streaming).

## Theme Integration

### CSS Variable Mapping (cli-jaw)
| Variable | Use |
|---|---|
| `--bg` | Page background |
| `--surface` | Card/surface background |
| `--text` | Primary text |
| `--text-dim` | Muted/secondary text |
| `--border` | Default border |
| `--accent` | Accent color |
| `--font-ui` | UI font family |
| `--font-mono` | Code font family |
| `--radius-md` | 8px border radius |
| `--radius-lg` | 12px border radius |

### By format
- **Inline SVG**: CSS classes adapt to host theme automatically
- **iframe widgets**: use `window.__jawTheme.isDark` (boolean) for JS-side theme detection
- **iframe widgets**: use `window.__jawTokens['--bg']` etc. for computed host CSS values
- Do NOT use `matchMedia('prefers-color-scheme')` — the host controls theme

## SVG Mobile Notes

- viewBox 680px 기준은 유지하되, 텍스트는 최소 14px (모바일 축소 후 ~9px)
- CJK 텍스트: 최소 16px (축소 후 ~10px)
- 터치 가능한 SVG 요소: 최소 44×44 hit area

## Animation Rules

### Inline SVG (DOMPurify sanitized)
- SMIL tags (`<animate>`, `<set>`, `<animateMotion>`) are stripped — do not use
- Inline SVG is static only — no animation

### diagram-file and diagram-html (sandboxed iframe)
All CSS/JS animation is available:

**CSS Transition** (preferred for hover/state changes):
```css
.element { transition: all 0.3s ease; }
.element:hover { transform: scale(1.05); opacity: 0.8; }
```

**CSS Animation** (keyframes):
```css
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.element { animation: fadeIn 0.5s ease-out; }
```

**JS requestAnimationFrame**: already documented in module-widget.md (Matter.js, Three.js, p5.js)

### Performance
- Animate only `transform` and `opacity` (GPU-accelerated)
- Avoid animating `width`, `height`, `top`, `left` (layout thrashing)
- Always call `cancelAnimationFrame` on cleanup

## Reference Files
For detailed patterns, see:
- `reference/svg-components.md` — SVG primitives, viewBox checklist, layout templates
- `reference/color-palette.md` — Full color values (light + dark), assignment rules
- `reference/module-chart.md` — Chart.js + D3 + ECharts 6 integration (bar/line/pie/choropleth + heatmap/sankey/radar/treemap/gauge/funnel/candlestick/chord)
- `reference/module-widget.md` — Physics (Matter.js), math graphs (Math.js), 3D (Three.js), creative coding (p5.js), audio (Tone.js), mini-games
- `reference/module-interactive.md` — Sliders, selects, segmented buttons, toggles, play/pause/reset, debouncing, sendPrompt, keyboard accessibility, control layout pattern
- `reference/module-map.md` — Leaflet interactive maps (OpenStreetMap tiles, markers, popups, dark mode)
- `reference/module-mockup.md` — UI mockup patterns
- `reference/module-art.md` — Decorative SVG patterns
- `reference/module-domain-cards.md` — Domain card templates (weather, finance, sports, product) + real-time data pipeline
- `reference/structured-renderers.md` — native renderer delegation notes
