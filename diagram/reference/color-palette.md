# Color Palette Reference

9 semantic color ramps × 3 shades × 2 themes.
Use CSS class names in SVG: `.c-{ramp}-fill`, `.c-{ramp}-stroke`, `.c-{ramp}-text`, `.c-{ramp}-bg`.

## Dark Mode (default — `:root`)

| Ramp   | Fill (bg)  | Stroke (border) | Text (label) |
|--------|-----------|-----------------|-------------|
| blue   | `#1e3a5f` | `#3b82f6`       | `#93c5fd`   |
| purple | `#3b1f5e` | `#8b5cf6`       | `#c4b5fd`   |
| green  | `#14532d` | `#22c55e`       | `#86efac`   |
| amber  | `#451a03` | `#f59e0b`       | `#fcd34d`   |
| red    | `#450a0a` | `#ef4444`       | `#fca5a5`   |
| cyan   | `#083344` | `#06b6d4`       | `#67e8f9`   |
| pink   | `#500724` | `#ec4899`       | `#f9a8d4`   |
| slate  | `#1e293b` | `#64748b`       | `#94a3b8`   |
| orange | `#431407` | `#f97316`       | `#fdba74`   |

## Light Mode (`[data-theme="light"]`)

| Ramp   | Fill (bg)  | Stroke (border) | Text (label) |
|--------|-----------|-----------------|-------------|
| blue   | `#dbeafe` | `#2563eb`       | `#1e40af`   |
| purple | `#ede9fe` | `#7c3aed`       | `#5b21b6`   |
| green  | `#dcfce7` | `#16a34a`       | `#15803d`   |
| amber  | `#fef3c7` | `#d97706`       | `#92400e`   |
| red    | `#fee2e2` | `#dc2626`       | `#991b1b`   |
| cyan   | `#cffafe` | `#0891b2`       | `#155e75`   |
| pink   | `#fce7f3` | `#db2777`       | `#9d174d`   |
| slate  | `#f1f5f9` | `#475569`       | `#334155`   |
| orange | `#ffedd5` | `#ea580c`       | `#9a3412`   |

## Usage in SVG
```svg
<!-- Rectangle with blue fill + stroke -->
<rect class="node c-blue-bg" x="10" y="10" width="160" height="48" />

<!-- Text label in blue -->
<text class="label c-blue-text" x="90" y="34">Label</text>

<!-- Connector line -->
<path class="connector" d="M 100 60 L 100 120" />
```

## Usage in diagram-html (Canvas/JS)
Canvas cannot resolve CSS classes. Use `window.__jawTokens` for computed values:
```javascript
const isDark = window.__jawTheme?.isDark ?? true;
const T = window.__jawTokens || {};
const textColor = T['--text'] || (isDark ? '#e8e6e3' : '#1a1a1a');
```

For chart-specific colors, use the hex values from the tables above directly.

## Contrast Notes
- All ramps meet WCAG AA 4.5:1 contrast ratio (text vs fill)
- Stroke colors serve as borders only — not relied on for legibility
- Connector lines use `var(--border)` which adapts automatically
