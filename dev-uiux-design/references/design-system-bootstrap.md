## 13. Design System Bootstrap

When starting a new project or establishing a design system, use this token architecture template.

### Token Template
```css
:root {
  /* Spacing (4px base) */
  --space-0: 0; --space-1: 4px; --space-2: 8px; --space-3: 12px;
  --space-4: 16px; --space-6: 24px; --space-8: 32px; --space-12: 48px; --space-16: 64px;

  /* Radius */
  --radius-none: 0; --radius-sm: 4px; --radius-md: 8px;
  --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;

  /* Elevation */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 2px 4px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-lg: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);

  /* Timing */
  --duration-fast: 100ms; --duration-normal: 200ms; --duration-slow: 400ms;
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

  /* Typography */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'Geist Mono', 'SF Mono', monospace;
  --text-xs: 0.75rem; --text-sm: 0.875rem; --text-base: 1rem;
  --text-lg: 1.125rem; --text-xl: 1.25rem; --text-2xl: 1.5rem; --text-3xl: 2rem;
}
```

### Component Hierarchy
- **Atoms:** Button, Input, Badge, Avatar, Icon, Toggle, Checkbox, Radio
- **Molecules:** Form Field (label + input + error), Card, Menu Item, Search Bar, Stat Card
- **Organisms:** Navigation Bar, Sidebar, Data Table, Form Section, Modal/Dialog, Command Palette

### Extending Existing Systems (shadcn/ui)
- Inspect existing installed components before adding new ones.
- Use the project's `components.json`, aliases, tokens, and registry conventions.
- Do not hallucinate components — verify against local source.
- New components must use the same token variables as existing ones.

