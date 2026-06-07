## 14. Responsive Strategy

### Breakpoint Scale
```
320px  — Small mobile (iPhone SE)
480px  — Large mobile
640px  — Small tablet / landscape mobile
768px  — Tablet portrait
1024px — Tablet landscape / small desktop
1280px — Desktop
1536px — Large desktop
```

### Mobile-First vs Desktop-First

| Choose Mobile-First When | Choose Desktop-First When |
|--------------------------|--------------------------|
| Consumer / public-facing product | Internal tool / admin panel |
| Content consumption primary use | Data-dense productivity tool |
| New project (progressive enhancement) | Existing desktop app adding mobile |

### Container Query Adoption
Prefer `@container` over `@media` for reusable components. Container queries let components adapt to their parent's size, not the viewport — enabling the same component in a sidebar, modal, or full-width layout.

```css
.card-container { container-type: inline-size; }
@container (min-width: 400px) { .card { grid-template-columns: 1fr 1fr; } }
```

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
