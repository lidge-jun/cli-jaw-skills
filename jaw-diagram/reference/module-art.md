# Decorative SVG Patterns

## Simple Icons (24×24 viewBox)

### Checkmark
```svg
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="24" height="24">
  <path d="M5 13l4 4L19 7" fill="none" stroke="currentColor" stroke-width="2"
    stroke-linecap="round" stroke-linejoin="round" />
</svg>
```

### Arrow Right
```svg
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="24" height="24">
  <path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2"
    stroke-linecap="round" stroke-linejoin="round" />
</svg>
```

### Star
```svg
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="24" height="24">
  <polygon points="12,2 15,9 22,9 16.5,14 18.5,21 12,17 5.5,21 7.5,14 2,9 9,9"
    fill="currentColor" />
</svg>
```

### Gear
```svg
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="24" height="24">
  <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2" />
  <path d="M12 1v3M12 20v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M1 12h3M20 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"
    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
</svg>
```

## Badge / Pill Shape
```svg
<rect class="c-blue-bg" x="10" y="10" width="80" height="24" rx="12" />
<text class="label c-blue-text" x="50" y="22" font-size="11">Badge</text>
```

## Progress Bar (Linear)
```svg
<rect class="c-slate-fill" x="20" y="10" width="300" height="8" rx="4" />
<rect class="c-blue-fill" x="20" y="10" width="195" height="8" rx="4" />
<text class="label c-blue-text" x="340" y="16" font-size="11">65%</text>
```

## Progress Circle
```svg
<circle class="c-slate-stroke" cx="40" cy="40" r="32" stroke-width="6" fill="none" />
<circle class="c-blue-stroke" cx="40" cy="40" r="32" stroke-width="6" fill="none"
  stroke-dasharray="201" stroke-dashoffset="70"
  transform="rotate(-90 40 40)" />
<text class="label c-blue-text" x="40" y="44" font-size="14">65%</text>
```

## Decorative Divider
```svg
<line class="connector" x1="40" y1="10" x2="640" y2="10" />
```

## Rules
- Icons: 24×24 or 32×32 viewBox, single-color fill
- Use `currentColor` for fill on icons (inherits from text color)
- No photorealistic or complex illustrations
- Keep path data minimal (prefer basic shapes over complex paths)
- Max 20 elements per decorative SVG (keep simple)
- Illustration style: flat, minimal, geometric
