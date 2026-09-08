# Color Palette Reference

9 semantic color ramps × 3 shades × 2 themes.
Use CSS class names in SVG: `.c-{ramp}-fill`, `.c-{ramp}-stroke`, `.c-{ramp}-text`, `.c-{ramp}-bg`.

## Color Assignment Rules

Color encodes **meaning**, not sequence. Don't cycle through colors like a rainbow.

- **Group by category**: all nodes of the same type share one color
- **2 ramps per diagram** max. One neutral (slate) + one semantic is cleaner than 6 colors.
- **Prefer general-purpose ramps**: cyan, pink, purple, orange for categories
- **Reserve semantic ramps**: blue=info, green=success, amber=warning, red=error — only when meaning matches
- **slate for neutral**: start/end nodes, generic structure, disabled state

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

## Text on Colored Backgrounds

Always use the **text shade from the same ramp** as the fill. Never use plain black, generic gray, or `var(--text)` on colored fills.

```svg
<!-- Correct: blue fill + blue text -->
<rect class="c-blue-bg" x="10" y="10" width="160" height="48" />
<text class="label c-blue-text" x="90" y="34">Label</text>

<!-- Wrong: blue fill + generic text -->
<rect class="c-blue-bg" x="10" y="10" width="160" height="48" />
<text fill="#333" x="90" y="34">Label</text>
```

## Usage in SVG
```svg
<rect class="node c-blue-bg" x="10" y="10" width="160" height="48" />
<text class="label c-blue-text" x="90" y="34">Label</text>
<path class="connector" d="M 100 60 L 100 120" />
```

## Usage in diagram-html (Canvas/JS)
Canvas cannot resolve CSS classes. Use `window.__jawTokens` for computed values:
```javascript
const isDark = window.__jawTheme?.isDark ?? true;
const T = window.__jawTokens || {};
const textColor = T['--text'] || (isDark ? '#e8e6e3' : '#1a1a1a');
const accent = T['--accent'] || '#3b82f6';
const surface = T['--surface'] || (isDark ? '#1a1a1a' : '#fff');
```

For chart-specific colors, use the hex values from the tables above directly.

## CSS Variable Mapping (cli-jaw ↔ Claude.ai)

If referencing Claude.ai docs, map variable names:

| cli-jaw | Claude.ai equivalent | Use |
|---|---|---|
| `--bg` | `--color-background-tertiary` | Page background |
| `--surface` | `--color-background-secondary` | Card/surface |
| `--text` | `--color-text-primary` | Primary text |
| `--text-dim` | `--color-text-secondary` | Muted text |
| `--border` | `--color-border-tertiary` | Default border |
| `--accent` | — | Accent highlight |
| `--font-ui` | `--font-sans` | UI font |
| `--font-mono` | `--font-mono` | Code font |
| `--radius-md` | `--border-radius-md` | 8px radius |
| `--radius-lg` | `--border-radius-lg` | 12px radius |

Always use cli-jaw variable names in code. This table is for reference only.

## Contrast Notes
- All ramps meet WCAG AA 4.5:1 contrast ratio (text vs fill)
- Stroke colors serve as borders only — not relied on for legibility
- Connector lines use `var(--border)` which adapts automatically
