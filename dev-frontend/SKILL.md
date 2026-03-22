---
name: dev-frontend
description: "Production-grade frontend with distinctive aesthetics. Detects stack and applies specialized rules. Modular: SKILL.md orchestrator + references/ for deep guidance. Injected when role=frontend."
license: Complete terms in LICENSE.txt
---

# Dev-Frontend — Production-Grade Frontend Engineering

Build distinctive, production-grade interfaces that avoid generic "AI slop" aesthetics.
This skill has modular references for specialized guidance — read the relevant ones before coding.

## Modular References

| File                                  | When to Read                 | What It Covers                                                                  |
| ------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------- |
| `references/core/aesthetics.md`       | **Always**                   | Design thinking, bold direction, typography, color, motion, spatial composition |
| `references/core/anti-slop.md`        | **Always**                   | Banned patterns, forbidden fonts/colors/layouts, content quality rules          |
| `references/core/motion.md`           | When motion/animation needed | CSS animations, Framer Motion, scroll-driven, View Transitions, spring physics  |
| `references/core/iterative-design.md` | Multi-round design           | LLM convergence problem, Diverge→Kill→Mutate process, upgrade techniques        |
| `references/stacks/react.md`          | React projects               | Server Components, hooks, state, TanStack Query, shadcn/ui, performance         |
| `references/stacks/nextjs.md`         | Next.js projects             | App Router, RSC, image optimization, data fetching, middleware                  |
| `references/stacks/vanilla.md`        | HTML+CSS+JS (no framework)   | Zero-dependency, viewport fitting, responsive CSS, progressive enhancement      |
| `references/stacks/svelte.md`         | Svelte/SvelteKit projects    | Svelte conventions, reactivity, stores, SvelteKit routing                       |

Read `aesthetics.md` + `anti-slop.md` first, then the relevant stack file.

---

## 0. Component Identification

When the user describes UI in vague terms (e.g. "접히는 거", "팝업 같은 거"):
1. Suggest 2-3 candidate components: `<Name> — <what it looks/works like>`
2. Recommend one with reasoning for this use case
3. Confirm, then proceed

If the user already names a specific component, skip this step.
Reference: [component.gallery/components](https://component.gallery/components/)

---

## 1. Design Thinking

Before coding, commit to a bold aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick a strong direction — don't default to "clean and modern." Choose from: brutally minimal, maximalist, retro-futuristic, luxury/refined, editorial/magazine, brutalist/raw, art deco, cyberpunk, organic/biomorphic, etc.
- **Constraints**: Framework, performance budget, accessibility requirements.
- **Signature**: What ONE thing will make this unforgettable?

Intentionality over intensity. Bold maximalism and refined minimalism both work — commit fully to the chosen direction.

---

## 2. Baseline Configuration

Adjust these dials based on what's being built. Present to user if unclear.

| Dial             | Default | Range | Meaning                              |
| ---------------- | :-----: | :---: | ------------------------------------ |
| DESIGN_VARIANCE  |    8    | 1-10  | 1=symmetric grids, 10=asymmetric art |
| MOTION_INTENSITY |    6    | 1-10  | 1=static, 10=cinematic choreography  |
| VISUAL_DENSITY   |    4    | 1-10  | 1=art gallery airy, 10=cockpit dense |

Adapt dynamically based on user requests. Dashboard → density up. Portfolio → variance up. Data tool → motion down.

---

## 3. Implementation

Read `references/core/aesthetics.md` for full guidelines. Summary:

- **Typography**: Use Geist, Outfit, Satoshi, Cabinet Grotesk, or other characterful typefaces — avoid Inter/Roboto/Arial.
- **Color**: Max 1 accent. Use neutral bases (Zinc/Slate) with singular high-contrast accent — avoid purple-on-white.
- **Layout**: Break centered-card patterns. Use asymmetry, overlap, diagonal flow, generous negative space.
- **Motion**: See `references/core/motion.md`. One well-choreographed page load > 10 scattered effects.
- **Backgrounds**: Create atmosphere — gradient meshes, noise textures, geometric patterns, layered transparencies.

---

## 4. Anti-Slop Enforcement

Read `references/core/anti-slop.md` for full rules. Key standards:

- Use characterful fonts (Geist, Outfit, Satoshi, Cabinet Grotesk) — Inter/Roboto/Arial/system-ui are banned
- Use neutral or intentional color palettes — purple gradients on white are a slop signal
- Use asymmetric or purposeful layouts — centered-everything reads as template
- Vary card sizes, spans, and groupings — equal 3-card grids read as generic
- Use icons or descriptive text instead of emoji in code and UI
- Use off-black (`#0a0a0a`, `#111`) — pure `#000000` lacks depth
- Use realistic, specific names and brands in placeholder content
- Write original copy — avoid "Elevate", "Seamless", "Next-Gen" and similar clichés

---

## 5. Performance Guardrails

- Animate `transform` and `opacity` only — layout properties (`top`, `left`, `width`, `height`) cause jank
- Grain/noise filters → fixed pseudo-elements only, keep off scrolling containers
- `will-change` sparingly — remove after animation completes
- Z-index only for systemic layers (navbar, modal, overlay)
- Memoize perpetual animations in isolated components

---

## 6. Accessibility Baseline

- Semantic HTML (`<button>`, `<nav>`, `<main>`)
- Keyboard navigation for all interactive elements
- WCAG AA minimum (4.5:1 normal text, 3:1 large text)
- Visible focus indicators (`focus-visible:ring-2`)
- `prefers-reduced-motion` support
- Touch targets ≥ 44×44px

---

## 7. Custom Hook Patterns

Extract reusable logic into custom hooks:

### useDebounce — Delay value updates

```typescript
function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}

// Usage: const debouncedQuery = useDebounce(searchQuery, 300)
```

### useToggle — Boolean state with flip

```typescript
function useToggle(initial = false): [boolean, () => void] {
  const [value, setValue] = useState(initial)
  const toggle = useCallback(() => setValue(v => !v), [])
  return [value, toggle]
}
```

### Hook Design Rules
- Name with `use` prefix — React enforces this
- Return `[value, actions]` tuple or `{ data, loading, error }` object
- Handle cleanup in `useEffect` return — prevent memory leaks
- Keep hooks focused — one concern per hook

---

## 8. React Performance Optimization

### Memoization Decision Tree

| Situation | Tool | Example |
|-----------|------|---------|
| Expensive computation from props/state | `useMemo` | Sorting/filtering large arrays |
| Callback passed to memoized child | `useCallback` | Event handlers for `React.memo` children |
| Pure component with stable props | `React.memo` | List items, cards |
| Frequent re-renders from context | Split contexts | Separate read-only from write contexts |

Skip memoization for cheap computations or components that render fast already — premature optimization adds complexity.

### Code Splitting

```typescript
const HeavyChart = lazy(() => import('./HeavyChart'))

// Wrap with Suspense + meaningful fallback
<Suspense fallback={<ChartSkeleton />}>
  <HeavyChart data={data} />
</Suspense>
```

Split at route boundaries and heavy components (charts, editors, 3D). Keep above-the-fold content in the main bundle.

---

## 9. Form Handling

### Controlled Form with Validation (Zod + Schema)

```typescript
const schema = z.object({
  name: z.string().min(1, "Required").max(200),
  email: z.string().email("Invalid email"),
})

function CreateForm() {
  const [data, setData] = useState({ name: '', email: '' })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const result = schema.safeParse(data)
    if (!result.success) {
      setErrors(Object.fromEntries(
        result.error.issues.map(i => [i.path[0], i.message])
      ))
      return
    }
    setErrors({})
    submitToApi(result.data)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input value={data.name}
        onChange={e => setData(p => ({ ...p, name: e.target.value }))} />
      {errors.name && <span role="alert">{errors.name}</span>}
      {/* ... */}
    </form>
  )
}
```

For complex forms (multi-step, dynamic fields), use `react-hook-form` + Zod resolver.

---

## 10. Accessibility Quick-Wins

Beyond the baseline (§6), add these interaction patterns:

### Focus Management (Modal)

```typescript
function Modal({ isOpen, onClose, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null)
  const previousFocus = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (isOpen) {
      previousFocus.current = document.activeElement as HTMLElement
      modalRef.current?.focus()
    } else {
      previousFocus.current?.focus()
    }
  }, [isOpen])

  if (!isOpen) return null
  return (
    <div ref={modalRef} role="dialog" aria-modal="true" tabIndex={-1}
      onKeyDown={e => e.key === 'Escape' && onClose()}>
      {children}
    </div>
  )
}
```

### Keyboard Navigation Checklist
- Arrow keys navigate lists and menus
- Enter/Space activate buttons and links
- Escape closes modals, dropdowns, popovers
- Tab order follows visual flow
- `aria-expanded`, `aria-haspopup`, `aria-activedescendant` on composite widgets

---

## 11. Pre-Flight Checklist

Before delivering:
- [ ] Bold aesthetic direction chosen and committed
- [ ] Anti-slop patterns enforced (§4)
- [ ] Mobile layout collapse guaranteed (`px-4`, `max-w-7xl mx-auto`)
- [ ] Full-height sections use `min-h-[100dvh]` not `h-screen`
- [ ] Loading, empty, and error states provided
- [ ] `useEffect` animations have cleanup functions
- [ ] Custom hooks tested independently (§7)
- [ ] Memoization applied only where measured impact (§8)
- [ ] Forms validate with schema and show field-level errors (§9)
- [ ] Focus management on modals and popovers (§10)
- [ ] Interactive components isolated as Client Components (if RSC)
- [ ] Stack-specific rules followed (see `references/stacks/`)

---

## 12. Backend Contract & Security Alignment

Frontend does not operate in isolation. When consuming backend APIs or implementing security-sensitive UI:

### 12.1 Contract Ownership

| Responsibility | Owner |
|---------------|-------|
| Response envelope shape (`success`, `data`, `error`, `meta`) | `dev-backend` defines, `dev-testing` verifies |
| Consumer-side fixture alignment | **Frontend** — keep mocks in sync with `fixtures/contracts/` |
| Contract test triggers | Frontend payload changes → update contract tests BEFORE merging (see `dev-testing` §3) |
| Error display mapping | Frontend maps `error.code` to user-facing messages; never parse `error.message` for logic |

**When a frontend change touches API consumption:**
1. Check if the response shape assumption still holds
2. If changed, update or add a contract test first (see `dev-testing` §3.5)
3. Align frontend mocks/fixtures with backend golden examples

### 12.2 Security Responsibilities

| Control | Policy Owner | Implementation Owner |
|---------|-------------|---------------------|
| CSP directives | `dev-security` §5 | Frontend (no inline scripts, no `eval`, no surprise 3rd-party scripts) |
| CORS | `dev-security` §5 | Backend middleware (`dev-backend` §4) |
| XSS prevention | `dev-security` §5 | Frontend (avoid `dangerouslySetInnerHTML`; if needed, sanitize with DOMPurify + CSP defense) |
| Token storage | `dev-security` §2 | Frontend (`httpOnly` cookies preferred over `localStorage`) |
| Auth state display | `dev-security` §2 | Frontend (loading → check → redirect or render; never flash protected content) |

### 12.3 Testing Integration

- Playwright smoke tests validate rendered flows AFTER backend API + contract tests pass
- Frontend unit tests mock API responses using the **same envelope shape** defined in `dev-backend` §5
- When backend error codes change, frontend error-mapping tests must be updated
