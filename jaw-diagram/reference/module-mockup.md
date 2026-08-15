# UI Mockup Patterns

## Browser Window Chrome
```svg
<svg viewBox="0 0 680 400" xmlns="http://www.w3.org/2000/svg"
  role="img" aria-labelledby="bw-title bw-desc">
  <title id="bw-title">Browser Wireframe</title>
  <desc id="bw-desc">Browser window mockup showing page layout</desc>

  <!-- Window chrome -->
  <rect class="c-slate-bg" x="20" y="20" width="640" height="360" rx="8" />

  <!-- Title bar -->
  <rect class="c-slate-fill" x="20" y="20" width="640" height="36" rx="8" />
  <!-- Traffic lights -->
  <circle class="c-red-stroke" cx="44" cy="38" r="6" fill="none" stroke-width="1.5" />
  <circle class="c-amber-stroke" cx="64" cy="38" r="6" fill="none" stroke-width="1.5" />
  <circle class="c-green-stroke" cx="84" cy="38" r="6" fill="none" stroke-width="1.5" />

  <!-- URL bar -->
  <rect class="c-slate-bg" x="110" y="28" width="440" height="20" rx="4" />
  <text class="label c-slate-text" x="330" y="38" font-size="10">https://example.com</text>

  <!-- Content area -->
  <rect x="40" y="76" width="600" height="284" fill="var(--surface)" rx="0" />

  <!-- Placeholder content lines -->
  <rect class="c-slate-fill" x="60" y="96" width="200" height="12" rx="2" />
  <rect class="c-slate-fill" x="60" y="120" width="560" height="8" rx="2" />
  <rect class="c-slate-fill" x="60" y="136" width="480" height="8" rx="2" />
  <rect class="c-slate-fill" x="60" y="152" width="520" height="8" rx="2" />
</svg>
```

## Mobile Phone Frame
```svg
<svg viewBox="0 0 680 500" xmlns="http://www.w3.org/2000/svg"
  role="img" aria-labelledby="mp-title mp-desc">
  <title id="mp-title">Mobile Wireframe</title>
  <desc id="mp-desc">Mobile phone mockup</desc>

  <!-- Phone body -->
  <rect class="c-slate-bg" x="220" y="20" width="240" height="460" rx="24" />

  <!-- Screen -->
  <rect x="230" y="56" width="220" height="400" fill="var(--surface)" rx="4" />

  <!-- Status bar -->
  <text class="label c-slate-text" x="340" y="74" font-size="10">9:41</text>

  <!-- Home indicator -->
  <rect class="c-slate-fill" x="300" y="448" width="80" height="4" rx="2" />
</svg>
```

## Card Component
```svg
<rect class="c-slate-bg" x="20" y="20" width="300" height="180" rx="8" />
<!-- Header -->
<rect class="c-blue-fill" x="20" y="20" width="300" height="40" rx="8" />
<text class="label c-blue-text" x="170" y="44">Card Title</text>
<!-- Body -->
<text class="label c-slate-text" x="170" y="90">Card content goes here</text>
<!-- Footer -->
<line class="connector" x1="40" y1="160" x2="300" y2="160" />
<text class="label c-slate-text" x="170" y="180" font-size="11">Footer action</text>
```

## Rules
- Use thin 0.5px strokes for wireframe lines
- Fill with `var(--surface)` for backgrounds
- Text uses actual content (not Lorem ipsum)
- Interactive elements use `c-blue` for actionable items
- Disabled elements use `c-slate`
- Keep mockups schematic — not pixel-perfect
