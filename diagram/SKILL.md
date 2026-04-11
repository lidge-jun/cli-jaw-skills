---
name: diagram
description: "SVG diagrams, charts, and interactive visualizations for chat UI"
version: 1.1.0
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

Route on the verb, not the noun. Same subject gets different diagrams:

| User says | Type | Output |
|---|---|---|
| "how does X work" | Illustrative SVG | Spatial metaphor, cross-section, physical layout |
| "architecture of X" | Structural SVG | Containers, regions, nesting |
| "steps of X" | Flowchart SVG | Top-down boxes + arrows |
| "compare A vs B" | Comparison SVG | Side-by-side columns |
| "DB schema" | Mermaid | ` ```mermaid ` erDiagram |
| "show data / chart" | diagram-html | Chart.js / D3 iframe widget |
| "simulate / interactive" | diagram-html | Matter.js / Canvas / controls |

Default to illustrative for "how does X work?" — don't default to flowchart.

## When to Use
Produce a diagram when the user's question benefits from visual explanation:
flowcharts, comparisons, timelines, org charts, data charts, maps, UI mockups,
physics simulations, interactive demos.

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
- Use classes from the design system (`.node`, `.connector`, `.label`, etc.)
- Colors: use CSS classes, not inline fill/stroke colors
- Text: `font-family` inherited from host (do NOT set explicit fonts)

### 2. Mermaid (simple flowcharts, ERDs)
Use standard ` ```mermaid ` code blocks. The existing renderer handles these.

### 3. Interactive HTML Widget (charts, controls, simulations)
Wrap in ` ```diagram-html ` code block. Rendered inside a sandboxed iframe.

```
` ` `diagram-html
<div id="chart-wrapper" style="position: relative; width: 100%; height: 300px;">
  <canvas id="myChart" role="img" aria-label="Chart description">
    Fallback text
  </canvas>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"
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

### Forbidden in Inline SVG (Security)
These are stripped by DOMPurify — NEVER use in inline `<svg>`:
- `<foreignObject>` — embeds HTML in SVG (XSS vector)
- `<animate>`, `<set>`, `<animateTransform>`, `<animateMotion>` — animation XSS vectors
- Nested `<svg>` — use `<g>` groups instead

### Forbidden Attributes in Inline SVG
- `xlink:href` — use `href="#fragment"` on `<use>` only (no external URLs)
- All `on*` event handlers (onclick, onerror, etc.) — stripped by DOMPurify

> **Note**: `diagram-html` content runs inside a sandboxed iframe where
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
For `diagram-html` widgets:
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

## Reference Files
For detailed patterns, see:
- `reference/svg-components.md` — SVG primitives, viewBox checklist, layout templates
- `reference/color-palette.md` — Full color values (light + dark), assignment rules
- `reference/module-chart.md` — Chart.js + D3 integration
- `reference/module-widget.md` — Physics (Matter.js), math graphs (Math.js), 3D (Three.js), creative coding (p5.js), audio (Tone.js), mini-games
- `reference/module-interactive.md` — Sliders, buttons, sendPrompt
- `reference/module-mockup.md` — UI mockup patterns
- `reference/module-art.md` — Decorative SVG patterns
