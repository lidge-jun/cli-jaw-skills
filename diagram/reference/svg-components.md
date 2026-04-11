# SVG Components Reference

## ViewBox Safety Checklist

Before finalizing any SVG, verify:

1. **Width**: viewBox width = 680 (mandatory, never change)
2. **Content bounds**: all elements within x=20..660. Safe area: x=40..640.
3. **Height**: find lowest element (max `y + height`), set viewBox height = that + 40px.
4. **Horizontal fit**: for each row, verify `sum(box widths + gaps) ≤ 640`. Four 160px boxes + three 20px gaps = 700px → **doesn't fit**. Shrink boxes or subtitles.
5. **text-anchor**: `text-anchor="end"` at x<60 is risky — text extends left past x=0. Use `text-anchor="start"` or verify: `label_chars × 8 < anchor_x`.
6. **No negative coords**: viewBox starts at 0,0. No negative x or y.

## Font Calibration (Geist Sans)

SVG `<text>` never auto-wraps. Each character ≈ 8px wide at 14px, ≈ 6.5px at 12px.

| Text example | Chars | Weight | Size | Approx width |
|---|---|---|---|---|
| Authentication Service | 22 | 500 | 14px | ~176px |
| Background Processor | 20 | 500 | 14px | ~160px |
| Detects incoming tokens | 22 | 400 | 12px | ~143px |
| forwards request | 16 | 400 | 12px | ~104px |

Before placing text in a box: does `text_width + 2×padding` fit the container?
If subtitle needs wrapping (`<tspan>`), it's too long — shorten it.

## Style Rules

- **Stroke width**: 0.5px for borders and connector edges
- **Connector paths**: MUST have `fill="none"` — SVG defaults to `fill: black`
- **Rect rounding**: `rx="4"` subtle, `rx="8"` emphasized, `rx="12"` max
- **Text vertical alignment**: every `<text>` inside a box needs `dominant-baseline="central"`
- **Font sizes**: 14px (node labels, `.label`) and 12px (subtitles) only
- **No rotated text**

## Primitives

### Arrow Marker (include in every SVG)
```svg
<defs>
  <marker id="arrowhead" markerWidth="10" markerHeight="7"
    refX="10" refY="3.5" orient="auto">
    <polygon class="c-slate-fill" points="0 0, 10 3.5, 0 7" />
  </marker>
</defs>
```

### Single-Line Node (48px tall)
```svg
<rect class="node c-blue-bg" x="260" y="20" width="160" height="48" rx="8" />
<text class="label c-blue-text" x="340" y="44"
  dominant-baseline="central">Step 1</text>
```

### Two-Line Node (64px tall)
```svg
<rect class="node c-blue-bg" x="240" y="20" width="200" height="64" rx="8" />
<text class="label c-blue-text" x="340" y="40"
  dominant-baseline="central" font-weight="500">Title</text>
<text class="label c-blue-text" x="340" y="60"
  dominant-baseline="central" font-size="12">Subtitle (≤5 words)</text>
```

### Connector Arrow
```svg
<path class="connector" d="M 340 68 L 340 100"
  fill="none" marker-end="url(#arrowhead)" />
```

### Diagram Title
```svg
<text class="diagram-title" x="340" y="24">Diagram title</text>
```

## Layout Templates

### Flowchart (Top-to-Bottom)
```svg
<svg viewBox="0 0 680 320" xmlns="http://www.w3.org/2000/svg"
  role="img" aria-labelledby="fc-title fc-desc">
  <title id="fc-title">Process Flow</title>
  <desc id="fc-desc">Three step process flow</desc>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7"
      refX="10" refY="3.5" orient="auto">
      <polygon class="c-slate-fill" points="0 0, 10 3.5, 0 7" />
    </marker>
  </defs>

  <rect class="node c-blue-bg" x="260" y="20" width="160" height="48" rx="8" />
  <text class="label c-blue-text" x="340" y="44"
    dominant-baseline="central">Step 1</text>

  <path class="connector" d="M 340 68 L 340 100"
    fill="none" marker-end="url(#arrowhead)" />

  <rect class="node c-green-bg" x="260" y="100" width="160" height="48" rx="8" />
  <text class="label c-green-text" x="340" y="124"
    dominant-baseline="central">Step 2</text>

  <path class="connector" d="M 340 148 L 340 180"
    fill="none" marker-end="url(#arrowhead)" />

  <rect class="node c-purple-bg" x="260" y="180" width="160" height="48" rx="8" />
  <text class="label c-purple-text" x="340" y="204"
    dominant-baseline="central">Step 3</text>
</svg>
```

Spacing: 60px between nodes (48px node + 12px gap + arrow). Max 4-5 nodes per flowchart.

### Comparison (Side-by-Side)
```svg
<svg viewBox="0 0 680 200" xmlns="http://www.w3.org/2000/svg"
  role="img" aria-labelledby="cmp-title cmp-desc">
  <title id="cmp-title">Option Comparison</title>
  <desc id="cmp-desc">Side-by-side comparison of two options</desc>

  <rect class="node c-cyan-bg" x="20" y="40" width="300" height="140" rx="8" />
  <text class="diagram-title c-cyan-text" x="170" y="70">Option A</text>
  <text class="label c-cyan-text" x="170" y="100" font-size="12">Feature details</text>

  <line class="connector" x1="340" y1="20" x2="340" y2="200" />

  <rect class="node c-pink-bg" x="360" y="40" width="300" height="140" rx="8" />
  <text class="diagram-title c-pink-text" x="510" y="70">Option B</text>
  <text class="label c-pink-text" x="510" y="100" font-size="12">Feature details</text>
</svg>
```

### Timeline (Horizontal)
```svg
<svg viewBox="0 0 680 120" xmlns="http://www.w3.org/2000/svg"
  role="img" aria-labelledby="tl-title tl-desc">
  <title id="tl-title">Project Timeline</title>
  <desc id="tl-desc">Key milestones on a horizontal timeline</desc>

  <line class="connector" x1="40" y1="60" x2="640" y2="60" />

  <circle class="c-cyan-bg" cx="120" cy="60" r="8" />
  <text class="label c-cyan-text" x="120" y="90">Q1</text>

  <circle class="c-pink-bg" cx="300" cy="60" r="8" />
  <text class="label c-pink-text" x="300" y="90">Q2</text>

  <circle class="c-purple-bg" cx="480" cy="60" r="8" />
  <text class="label c-purple-text" x="480" y="90">Q3</text>
</svg>
```

## Guidelines Summary
- Always use `viewBox="0 0 680 {height}"` — width 680 is mandatory
- Use `<g>` for grouping related elements (not nested `<svg>`)
- Keep text concise — truncate long labels
- Use `dominant-baseline="central"` for vertical text centering
- Include arrow marker `<defs>` in every flowchart SVG
- All connectors need `fill="none"`
