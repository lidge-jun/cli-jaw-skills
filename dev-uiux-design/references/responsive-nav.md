## 14. Responsive Strategy

### Canonical Breakpoint Tiers

Aligned with Tailwind defaults. Use these consistently across all skill references.

| Tier | Breakpoint | Tailwind | Name | Typical Devices |
|------|-----------|----------|------|-----------------|
| T1 | < 640px | default | **Mobile** | Phone portrait (320-480), phone landscape (480-640) |
| T2 | ≥ 640px | `sm:` | **Large Mobile** | Landscape phones, small tablets |
| T3 | ≥ 768px | `md:` | **Tablet** | iPad portrait, desktop split-screen (half of 1440px) |
| T4 | ≥ 1024px | `lg:` | **Small Desktop** | iPad landscape, laptop, desktop split-screen (half of 1920px) |
| T5 | ≥ 1280px | `xl:` | **Desktop** | Standard desktop monitors |
| T5+ | ≥ 1536px | `2xl:` | **Large Desktop** | Ultra-wide, large monitors |

**Verification sub-tiers** (test at these, but don't use as CSS breakpoints): 320px (narrow stress), 390px (standard mobile), 1440px (standard desktop).

### Mobile-First vs Desktop-First

| Choose Mobile-First When | Choose Desktop-First When |
|--------------------------|--------------------------|
| Consumer / public-facing product | Internal tool / admin panel |
| Content consumption primary use | Data-dense productivity tool |
| New project (progressive enhancement) | Existing desktop app adding mobile |

### Container Query Adoption (2026 baseline, 93%+ support)

`@container` is the DEFAULT for reusable components. `@media` is reserved for page-level layout shifts only.

Components should adapt to their container's width, not the viewport. This is what makes a card component work correctly in a sidebar, modal, full-width layout, AND split-screen window — all without viewport media queries.

```css
.card-container { container-type: inline-size; }

@container (max-width: 399px) {
  .card { display: flex; flex-direction: column; }
}
@container (min-width: 400px) {
  .card { display: grid; grid-template-columns: 1fr 1fr; }
}
@container (min-width: 700px) {
  .card { grid-template-columns: 1fr 1fr 1fr; }
}
```

When to use `@media` (page-level):
- Sidebar show/hide (`@media (min-width: 1024px)`)
- Nav mode switch (hamburger ↔ horizontal)
- Page grid column count
- Print styles

When to use `@container` (component-level):
- Card layouts (single-col ↔ multi-col)
- Feature grids
- Embedded widgets, modals, sidebars
- Any component that might live in different-width parents

### Split-Screen / Half-Window (the neglected viewport)

macOS split-view on a 1440px display: each app ~640-720px.
Windows snap on 1440px: each half ~720px. On 1920px: ~960px.

This 640-1024px range falls between "mobile collapse" and "full desktop." Most pages break here.

Rules:
- At T2 (640-767px): 2-col grids → 1-col. Side-by-side hero stacks. Padding tightens.
- At T3 (768-1023px): 3-col grids → 2-col. Hero can stay side-by-side if text-heavy. Bento → 2-col.
- Always test at 768px AND 1024px — these are the split-screen breakpoints.

### Responsive Navigation by Density Profile

| Density | Desktop Navigation | Mobile Navigation |
|---------|-------------------|-------------------|
| D1–D3 (campaign/consumer) | Horizontal top nav | Hamburger menu |
| D4–D6 (SaaS/productivity) | Collapsible sidebar (256px→64px) | Bottom tab bar (4–5 items) |
| D7–D8 (ops/developer) | Fixed sidebar + top breadcrumb | Sidebar stays, no collapse |

---

## 15. Navigation & Information Architecture

### Sidebar
- Expanded: 256px fixed width. Collapsed: 64px (icons only).
- Item height: 36px. Horizontal padding: 12px.
- Active state: 8% primary color background + 3px left accent border.
- Transition: 200ms ease-in-out.
- Group sections with subtle separators and 10px uppercase section labels.

### Tab Bar (Bottom Navigation — Mobile)
- Maximum 5 items. Active item has filled icon + label. Inactive: outline icon only.
- Safe area padding for notch/home-indicator devices.
- Center the primary action if it has elevated importance (FAB pattern).

### Command Palette (Cmd+K)
- Centered modal at 20% from top, max-width 600px.
- Instant search with fuzzy matching.
- Category grouping (Actions, Pages, Settings).
- Recent items shown on empty query.
- Keyboard navigation: arrow keys + Enter.

### Breadcrumbs
- Use for hierarchical navigation deeper than 2 levels.
- Show abbreviated path on mobile (... > Parent > Current).
- Clickable segments except the current page.
- Separator: `/` or `>` — pick one and be consistent.

### By Product Surface

| Surface | Primary Nav | Secondary Nav | Search |
|---------|-------------|---------------|--------|
| Landing/marketing | Horizontal top nav | Footer links | Not needed |
| Consumer app | Bottom tab bar (mobile), sidebar (desktop) | In-context navigation | Optional |
| SaaS/productivity | Collapsible sidebar | Breadcrumbs + tabs | Command palette |
| Dashboard/ops | Fixed sidebar | Tab groups per section | Always visible search bar |
| Developer tool | Sidebar + command palette | Breadcrumbs | Prominent Cmd+K |
