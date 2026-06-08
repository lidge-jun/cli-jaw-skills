---
name: ui-design-system
description: "Design token generation, color palettes, typography scales, component architecture, WCAG accessibility, and developer handoff. Use when creating design systems, maintaining visual consistency, or bridging design-development collaboration."
---

# UI Design System

---

## 1. Design Token Generation

### Token Format: W3C DTCG (2025.10)

Use the **W3C Design Token Community Group** format as the canonical interchange format for tokens:

```json
{
  "color": {
    "brand": {
      "primary": {
        "$type": "color",
        "$value": "oklch(0.65 0.25 265)",
        "$description": "Primary brand color"
      }
    }
  }
}
```

Key conventions:
- `$type` declares the token type (color, dimension, fontFamily, fontWeight, etc.)
- `$value` holds the resolved value
- Group nesting replaces flat naming (e.g., `color.brand.primary` not `color-brand-primary`)
- Use **Style Dictionary** (v4+) to transform DTCG tokens into platform outputs (CSS, iOS, Android, Figma)

### Semantic Token Naming (Four-Part Hierarchy)

Structure token names as: **category.concept.property.modifier**

| Part | Examples |
|------|----------|
| Category | `color`, `space`, `font`, `border`, `shadow` |
| Concept | `brand`, `neutral`, `feedback`, `surface` |
| Property | `base`, `foreground`, `background`, `border` |
| Modifier | `default`, `hover`, `active`, `disabled`, `subtle` |

Examples: `color.brand.background.default`, `color.feedback.error.foreground`, `space.layout.gap.lg`

### Color System

From a single brand color, generate a full palette:

| Step | Brightness | Use Case |
|------|------------|----------|
| 50 | 95% | Subtle backgrounds |
| 100–200 | 90–85% | Light backgrounds, hover states |
| 300–400 | 75–65% | Borders, disabled states |
| 500 | Original | Base/default color |
| 600–700 | 80–60% of original | Hover (dark), active states |
| 800–900 | 40–20% of original | Text, headings |

### Wide-Gamut Color Spaces

**Oklch** is the preferred perceptually uniform color space for design tokens. It provides consistent lightness across hues, making palette generation predictable:

```css
/* Oklch: lightness, chroma, hue */
--color-brand-500: oklch(0.65 0.25 265);
--color-brand-600: oklch(0.55 0.25 265);  /* Darken by reducing L */

/* Display P3 fallback for broader gamut */
--color-accent: color(display-p3 0.2 0.5 1.0);
```

- Use `oklch()` for new projects; it's supported in all modern browsers (2024+)
- Use `color(display-p3 ...)` for vivid colors beyond sRGB gamut
- Always provide an sRGB fallback with `@supports` or CSS `color()` fallback syntax

### Typography Scale (1.25x Ratio)

| Token | Size | Calculation |
|-------|------|-------------|
| xs | 10px | base ÷ 1.25² |
| sm | 13px | base ÷ 1.25¹ |
| base | 16px | Base |
| lg | 20px | base × 1.25¹ |
| xl | 25px | base × 1.25² |
| 2xl | 31px | base × 1.25³ |
| 3xl | 39px | base × 1.25⁴ |

### Spacing (8pt Grid)

Base unit: 8px. Scale: 0, 4, 8, 12, 16, 24, 32, 48, 64.

### Export Formats

```bash
# CSS custom properties
python scripts/design_token_generator.py "#0066CC" modern css > design-tokens.css

# SCSS variables
python scripts/design_token_generator.py "#0066CC" modern scss > _design-tokens.scss

# JSON (for Figma/tooling)
python scripts/design_token_generator.py "#0066CC" modern json > design-tokens.json
```

---

## 2. Component Architecture (Atomic Design)

| Level | Examples | Tokens Used |
|-------|----------|-------------|
| Atoms | Button, Input, Icon, Badge | colors, sizing, borders, typography |
| Molecules | FormField, SearchBar, Card | atoms + spacing, shadows |
| Organisms | Header, DataTable, Modal | molecules + layout, z-index |
| Templates | DashboardLayout, AuthLayout | organisms + grid, breakpoints |

### Variant Patterns

**Size:**
```
sm: height 32px, paddingX 12px, fontSize 14px
md: height 40px, paddingX 16px, fontSize 16px
lg: height 48px, paddingX 20px, fontSize 18px
```

**Color:**
```
primary:   background primary-500, text white
secondary: background neutral-100, text neutral-900
ghost:     background transparent, text neutral-700
```

---

## 3. Responsive Design

### Breakpoints

| Name | Width | Target |
|------|-------|--------|
| xs | 0 | Small phones |
| sm | 480px | Large phones |
| md | 640px | Tablets |
| lg | 768px | Small laptops |
| xl | 1024px | Desktops |
| 2xl | 1280px | Large screens |

### Fluid Typography

```css
--fluid-h1: clamp(2rem, 1rem + 3.6vw, 4rem);
--fluid-h2: clamp(1.75rem, 1rem + 2.3vw, 3rem);
--fluid-body: clamp(1rem, 0.95rem + 0.2vw, 1.125rem);
```

---

## 4. WCAG Accessibility

### Contrast Requirements

| Level | Normal Text | Large Text (≥18pt / ≥14pt bold) |
|-------|-------------|---------|
| AA | 4.5:1 | 3:1 |
| AAA | 7:1 | 4.5:1 |

### Checklist
- [ ] Color contrast meets WCAG AA
- [ ] Focus indicators visible on all interactive elements
- [ ] Touch targets ≥ 44×44px
- [ ] Semantic HTML elements used
- [ ] All images have alt text

---

## 5. Developer Handoff

### Framework Integration

**React + CSS Variables:**
```tsx
import './design-tokens.css';
<button className="btn btn-primary">Click</button>
```

**Tailwind Config:**
```javascript
const tokens = require('./design-tokens.json');
module.exports = { theme: { colors: tokens.colors, fontFamily: tokens.typography.fontFamily } };
```

### Handoff Checklist
- [ ] Token files added to project
- [ ] Theme imported in app entry point
- [ ] Component library uses tokens only (no hardcoded values)
- [ ] Documentation generated

---

## Style Presets

| Aspect | Modern | Classic | Playful |
|--------|--------|---------|---------|
| Font Sans | Inter | Helvetica | Poppins |
| Font Mono | Fira Code | Courier | Source Code Pro |
| Border Radius | 8px | 4px | 16px |
| Shadows | Layered, subtle | Single layer | Soft, pronounced |

---

## Tooling Reference

| Tool | Purpose |
|------|---------|
| [Style Dictionary](https://styledictionary.com/) (v4+) | Transform DTCG tokens to CSS, iOS, Android, Compose |
| [Figma Variables](https://help.figma.com/hc/en-us/articles/15339657135383) | Design-side token management and theming |
| [Cobalt UI](https://cobalt-ui.pages.dev/) | DTCG-native token pipeline alternative |
| [Tokens Studio](https://tokens.studio/) | Figma plugin for syncing tokens to/from code |
