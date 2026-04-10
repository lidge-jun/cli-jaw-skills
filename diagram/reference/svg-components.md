# SVG Components Reference

## Primitives

### Rounded Rectangle Node
```svg
<rect class="node c-blue-bg" x="10" y="10" width="160" height="48" rx="8" ry="8" />
<text class="label c-blue-text" x="90" y="34">Node Label</text>
```

### Connector Arrow
```svg
<defs>
  <marker id="arrowhead" markerWidth="10" markerHeight="7"
    refX="10" refY="3.5" orient="auto">
    <polygon class="c-slate-fill" points="0 0, 10 3.5, 0 7" />
  </marker>
</defs>
<path class="connector" d="M 90 58 L 90 90" marker-end="url(#arrowhead)" />
```

### Label Text
```svg
<text class="label c-blue-text" x="100" y="30">Label Text</text>
```

### Diagram Title
```svg
<text class="diagram-title" x="340" y="24">Diagram Title</text>
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

  <!-- Node 1 -->
  <rect class="node c-blue-bg" x="260" y="20" width="160" height="48" />
  <text class="label c-blue-text" x="340" y="44">Step 1</text>

  <!-- Arrow 1→2 -->
  <path class="connector" d="M 340 68 L 340 100" marker-end="url(#arrowhead)" />

  <!-- Node 2 -->
  <rect class="node c-green-bg" x="260" y="100" width="160" height="48" />
  <text class="label c-green-text" x="340" y="124">Step 2</text>

  <!-- Arrow 2→3 -->
  <path class="connector" d="M 340 148 L 340 180" marker-end="url(#arrowhead)" />

  <!-- Node 3 -->
  <rect class="node c-purple-bg" x="260" y="180" width="160" height="48" />
  <text class="label c-purple-text" x="340" y="204">Step 3</text>
</svg>
```

Spacing: 60px between nodes (48px node + 12px gap + arrow).

### Comparison (Side-by-Side)
```svg
<svg viewBox="0 0 680 200" xmlns="http://www.w3.org/2000/svg"
  role="img" aria-labelledby="cmp-title cmp-desc">
  <title id="cmp-title">Option Comparison</title>
  <desc id="cmp-desc">Side-by-side comparison of two options</desc>

  <!-- Left column -->
  <rect class="node c-blue-bg" x="20" y="40" width="300" height="140" />
  <text class="diagram-title c-blue-text" x="170" y="70">Option A</text>
  <text class="label c-blue-text" x="170" y="100">Feature details</text>

  <!-- Divider -->
  <line class="connector" x1="340" y1="20" x2="340" y2="200" />

  <!-- Right column -->
  <rect class="node c-green-bg" x="360" y="40" width="300" height="140" />
  <text class="diagram-title c-green-text" x="510" y="70">Option B</text>
  <text class="label c-green-text" x="510" y="100">Feature details</text>
</svg>
```

### Timeline (Horizontal)
```svg
<svg viewBox="0 0 680 120" xmlns="http://www.w3.org/2000/svg"
  role="img" aria-labelledby="tl-title tl-desc">
  <title id="tl-title">Project Timeline</title>
  <desc id="tl-desc">Key milestones on a horizontal timeline</desc>

  <!-- Axis -->
  <line class="connector" x1="40" y1="60" x2="640" y2="60" />

  <!-- Markers -->
  <circle class="c-blue-bg" cx="120" cy="60" r="8" />
  <text class="label c-blue-text" x="120" y="90">Q1</text>

  <circle class="c-green-bg" cx="300" cy="60" r="8" />
  <text class="label c-green-text" x="300" y="90">Q2</text>

  <circle class="c-purple-bg" cx="480" cy="60" r="8" />
  <text class="label c-purple-text" x="480" y="90">Q3</text>
</svg>
```

## Guidelines
- Always use `viewBox="0 0 680 {height}"` — width 680 is mandatory
- Use `<g>` for grouping related elements (not nested `<svg>`)
- Keep text concise — truncate long labels
- Minimum touch target: 44×44px for interactive elements
- Use `dominant-baseline="central"` for vertical text centering
