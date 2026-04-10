---
name: diagram
description: "SVG diagrams, charts, and interactive visualizations for chat UI"
version: 1.0.0
---

# Diagram Visualization Skill

## When to Use
Produce a diagram when the user's question benefits from visual explanation:
flowcharts, comparisons, timelines, org charts, data charts, maps, UI mockups.

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
- viewBox width MUST be 680 (matches container width)
- Height varies by content
- Every SVG MUST have `role="img"` + `<title>` + `<desc>`
- Use classes from the design system (`.node`, `.connector`, `.label`, etc.)
- Colors: use CSS classes, not inline fill/stroke colors
- Text: `font-family` inherited from host (do NOT set explicit fonts)

### 2. Mermaid (simple flowcharts)
Use standard ` ```mermaid ` code blocks. The existing renderer handles these.

### 3. Interactive HTML Widget (charts, controls)
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

### Forbidden in Inline SVG
These are stripped by DOMPurify — NEVER use in inline `<svg>`:
- `<foreignObject>` — embeds HTML in SVG (XSS vector)
- `<animate>`, `<set>`, `<animateTransform>`, `<animateMotion>` — animation XSS vectors
- Nested `<svg>` — use `<g>` groups instead

### Forbidden Attributes in Inline SVG
- `xlink:href` — use `href="#fragment"` on `<use>` only (no external URLs)
- All `on*` event handlers (onclick, onerror, etc.)

> **Note**: `diagram-html` content runs inside a sandboxed iframe where
> `<script>`, `on*` handlers, and CDN imports ARE allowed. The restrictions
> above apply only to inline SVG rendered in the main document.

### Color Ramps (9 semantic colors)
Each ramp has 3 shades: fill (bg), stroke (border), text (label).
Use CSS class names — see `reference/color-palette.md`:

| Ramp | Class prefix | Use |
|---|---|---|
| blue | `.c-blue` | Primary, default |
| purple | `.c-purple` | Categories, grouping |
| green | `.c-green` | Success, positive |
| amber | `.c-amber` | Warning, attention |
| red | `.c-red` | Error, negative |
| cyan | `.c-cyan` | Info, secondary |
| pink | `.c-pink` | Highlight |
| slate | `.c-slate` | Neutral, disabled |
| orange | `.c-orange` | Accent |

### Layout Patterns
- Flowchart: top-to-bottom, 680×auto
- Comparison: side-by-side columns
- Timeline: horizontal with markers
- Org chart: hierarchical tree
- See `reference/svg-components.md` for templates.

### Style-First, Script-Last
For `diagram-html` widgets:
1. All `<style>` and `<link>` tags first
2. HTML structure
3. `<script>` tags last

This ensures visual content appears before scripts execute (important during streaming).

## Theme Integration
- Inline SVG: uses CSS classes that adapt to host theme automatically
- iframe widgets: use `window.__jawTheme.isDark` (boolean) for JS-side theme detection
- iframe widgets: use `window.__jawTokens['--bg']` etc. for computed host CSS values
- Do NOT use `matchMedia('prefers-color-scheme')` — the host controls theme

## Reference Files
For detailed patterns, see:
- `reference/svg-components.md` — SVG primitives, layout templates
- `reference/color-palette.md` — Full color values (light + dark)
- `reference/module-chart.md` — Chart.js + D3 integration
- `reference/module-interactive.md` — Sliders, buttons, sendPrompt
- `reference/module-mockup.md` — UI mockup patterns
- `reference/module-art.md` — Decorative SVG patterns
