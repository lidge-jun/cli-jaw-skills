# React Stack — Development Rules

Rules specific to React projects. Read `core/aesthetics.md`, `core/anti-slop.md`, and `core/visual-verification.md` first.

---

## Domain Routing

Before choosing component libraries, read the core references that match the surface:

- Korean-first UI → `korea-2026.md`, `ux-writing-ko.md`
- Tool/dashboard → `product-density.md`
- Visual/product surface → `asset-requirements.md`
- Soft 3D/mascot/miniature visuals → `soft-3d-asset-gates.md`
- Substantial UI change → `visual-verification.md`

## Behavior-First Components

Prefer proven behavior primitives for complex interactive components:

- Radix / Headless UI for dialog, popover, menu, tabs, combobox-like behavior
- shadcn/ui as source code scaffolding, not as a final visual design
- Existing repo components before adding a new dependency

Customize tokens, radius, shadows, density, and typography. Do not ship default shadcn visuals.

## Korean Mobile Patterns

React apps targeting Korean mobile flows should support:

- bottom sheets for lightweight choices
- full-screen funnels for complex steps
- sticky bottom action bars
- snackbar/toast for reversible confirmations
- safe-area insets
- `100dvh` instead of `100vh`
- long Korean label stress tests

## AI Tool States

AI features must expose state clearly:

- pending / queued
- streaming or partial result
- cancel
- retry
- undo or revert
- source/provenance when applicable
- permission boundary before sensitive actions
- rate limit or failure recovery

Do not hide AI uncertainty behind decorative gradients.

## Architecture

### Server Components When Supported By The Framework
Use Server Components only in Next App Router or another RSC-enabled framework. In Vite, SPA-only React, React Native Web, or client-only embeds, do not introduce RSC assumptions or `'use client'` boundaries.

When the framework supports RSC, default non-interactive route content to Server Components. Add `'use client'` ONLY when you need:
- Event handlers (`onClick`, `onChange`)
- State (`useState`, `useReducer`)
- Effects (`useEffect`)
- Browser APIs (`window`, `document`)

```tsx
// Server Component (default) — no 'use client'
async function ProductPage({ params }) {
  const product = await getProduct(params.id);
  return (
    <div>
      <h1>{product.name}</h1>
      <AddToCartButton productId={product.id} />
    </div>
  );
}

// Client Component — only what MUST be interactive
'use client';
function AddToCartButton({ productId }) {
  const [adding, setAdding] = useState(false);
  return <button onClick={() => addToCart(productId)}>Add</button>;
}
```

### RSC Safety Rules
- Global state ONLY in Client Components
- In Next.js, wrap providers in a `'use client'` wrapper component
- If motion/interactivity needed, extract the interactive part as an **isolated leaf** Client Component

### Interactivity Isolation
Any component using `useMotionValue`, `useTransform`, or perpetual animations MUST be extracted as a dedicated Client Component in RSC-enabled frameworks. Server Components render static layouts only.

---

## State Management

| Need                | Solution                                                |
| ------------------- | ------------------------------------------------------- |
| Local UI state      | `useState` / `useReducer`                               |
| Form state          | React Hook Form + Zod validation                        |
| Server-fetched data | TanStack Query (`@tanstack/react-query`)                |
| Global shared state | Zustand (minimal, flat store)                           |
| Deep prop drilling  | React Context (for dependency injection, NOT data flow) |

**Anti-patterns**:
- Don't use Context for frequently changing data (causes subtree re-renders)
- Don't reach for global state when local state suffices
- Don't use `useEffect` for data fetching — use TanStack Query or Server Components

---

## Component Patterns

### Compound Components
```tsx
const Tabs = ({ children }) => {
  const [active, setActive] = useState(0);
  return (
    <TabsContext.Provider value={{ active, setActive }}>
      {children}
    </TabsContext.Provider>
  );
};
Tabs.List = TabList;
Tabs.Panel = TabPanel;
```

### Custom Hooks (extract reusable logic)
```tsx
function useDebounce<T>(value: T, delay = 500): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}
```

### Generic List Component
```tsx
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}
function List<T>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map(renderItem)}</ul>;
}
```

---

## Styling

### Tailwind CSS
- Check `package.json` for Tailwind version. Do NOT mix v3/v4 syntax.
- **T4 CONFIG GUARD**: For v4, do NOT use `tailwindcss` plugin in `postcss.config.js`. Use `@tailwindcss/postcss` or Vite plugin.
- Use `cn()` utility for conditional classes:
```tsx
import { cn } from '@/lib/utils';
<button className={cn(
  'px-4 py-2 rounded',
  variant === 'primary' && 'bg-emerald-500 text-white',
  disabled && 'opacity-50 cursor-not-allowed'
)} />
```

### shadcn/ui
- MUST customize defaults — never ship generic appearance
- Override `--radius`, color palette, shadow depth
- All components should match project's aesthetic direction

### CSS Variables for Design Tokens
```css
:root {
  --color-primary: oklch(0.7 0.15 160);
  --color-surface: oklch(0.98 0 0);
  --radius-default: 0.75rem;
  --shadow-card: 0 20px 40px -15px rgba(0,0,0,0.05);
}
```

---

## Dependency Verification [MANDATORY]

Before importing ANY 3rd party library:
1. Check `package.json`
2. If missing, output `npm install <package>` BEFORE providing code
3. **Never assume** a library exists

---

## Icons

Use EXACTLY `@phosphor-icons/react` or `@radix-ui/react-icons` as import paths.
Standardize `strokeWidth` globally (e.g., exclusively `1.5` or `2.0`).
**NEVER** use emoji — see `anti-slop.md`.

---

## Performance

### Bundle Optimization
| Heavy Package | Size  | Alternative                    |
| ------------- | ----- | ------------------------------ |
| moment        | 290KB | date-fns (12KB) or dayjs (2KB) |
| lodash        | 71KB  | lodash-es with tree-shaking    |
| axios         | 14KB  | Native fetch or ky (3KB)       |
| @mui/material | Large | shadcn/ui or Radix UI          |

### Rendering
- Parallel fetch: `Promise.all([getUser(), getStats()])`
- Streaming: `<Suspense fallback={<Skeleton />}>`
- Avoid waterfall: never fetch sequentially in nested components
- `React.memo` for expensive pure components
- `useMemo` / `useCallback` only when measured, not preemptively

### Image Optimization
```tsx
// Above fold — load immediately
<Image src="/hero.jpg" alt="Hero" width={1200} height={600} priority />

// Responsive fill
<div className="relative aspect-video">
  <Image src="/product.jpg" alt="Product" fill
    sizes="(max-width: 768px) 100vw, 50vw"
    className="object-cover" />
</div>
```

---

## Testing

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('button triggers action', async () => {
  const onClick = vi.fn();
  render(<Button onClick={onClick}>Click</Button>);
  await userEvent.click(screen.getByRole('button'));
  expect(onClick).toHaveBeenCalledTimes(1);
});

test('dialog is accessible', () => {
  render(<Dialog open title="Confirm" />);
  expect(screen.getByRole('dialog')).toHaveAttribute('aria-labelledby');
});
```

---

## Responsiveness

- Standardize breakpoints: `sm`, `md`, `lg`, `xl`
- Contain layouts: `max-w-[1400px] mx-auto` or `max-w-7xl`
- **NEVER** `h-screen` for full-height. ALWAYS `min-h-[100dvh]`
- **NEVER** `w-[calc(33%-1rem)]`. ALWAYS CSS Grid
- DESIGN_VARIANCE levels 4-10: aggressive single-column fallback on `< 768px`

## Behavior Rules (moved from SKILL.md §8-§10, 2026-07-02)

### Custom Hooks
Create a custom hook only when it owns reusable behavior. Good candidates: subscription
lifecycle, reusable async state machine, shared form-field behavior, media/query/observer
integration, keyboard/focus behavior, external store wrapper. Avoid thin aliases for
`useState`/`useToggle`/`useDebounce` unless the repo standardizes them.
Rules: name describes behavior, not implementation; explicit stable inputs, small return
shape; side effects justified by an external system with correct cleanup; honest
dependencies (`useEffectEvent` for non-reactive callbacks); never hide server/router/form
ownership inside a generic hook.

### React Performance
Keep components pure, state local, classify state ownership, use server rendering/caching
boundaries, split expensive client islands, measure before memoizing.

| Tool | Use when |
|------|----------|
| `memo` | child render is expensive and props are stable |
| `useMemo` | calculation is expensive or identity is required |
| `useCallback` | callback identity required by memoized child or external API |
| `useTransition` | interaction should stay responsive during non-urgent work |
| `useOptimistic` | mutation UX benefits from reversible optimistic state |
| `Activity` | hidden UI should preserve state without active Effects |
| `Suspense` | dynamic/async boundary needs isolated loading behavior |

With React Compiler enabled, remove defensive memoization unless measurement or semantics
justify it. Split at route boundaries and heavy components (charts, editors, 3D).
Inspect React Performance Tracks (Chrome DevTools) before adding memoization.

### Form Handling
Simple forms: controlled components + schema validation (Zod). Complex (multi-step,
dynamic fields): react-hook-form + Zod resolver. Always show field-level errors with
`role="alert"`.

## Sources

| Claim | Source | Checked |
|---|---|---|
| React 19.2 line: Activity, useEffectEvent, PPR, Performance Tracks | https://react.dev/blog/2025/10/01/react-19-2 | 2026-07-02 |
| React Compiler stable/optional | https://react.dev/learn/react-compiler/introduction | 2026-07-02 |
