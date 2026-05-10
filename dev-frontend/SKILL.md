---
name: dev-frontend
description: "Production-grade frontend with distinctive aesthetics. Detects stack and applies specialized rules. Modular: SKILL.md orchestrator + references/ for deep guidance. Injected when role=frontend."
license: Complete terms in LICENSE.txt
---

# Dev-Frontend — Domain-Correct Frontend Engineering

Build distinctive, production-grade interfaces that fit the product domain, locale, interaction model, and real visual evidence.
This skill has modular references for specialized guidance — read the relevant ones before coding.

## Modular References

| File                                      | When to Read                         | What It Covers                                                                    |
| ----------------------------------------- | ------------------------------------ | --------------------------------------------------------------------------------- |
| `references/core/anti-slop.md`            | **Always**                           | 2026 AI slop patterns, Korean slop, oversized text, fake assets, default UI smells |
| `references/core/aesthetics.md`           | **Always**                           | Domain-correct visual direction, typography, color, composition                    |
| `references/core/product-density.md`      | Apps, tools, dashboards              | Density profiles for landing, consumer app, SaaS, ops, finance, devtools          |
| `references/core/asset-requirements.md`   | Any public/product/visual surface    | Required screenshots, images, diagrams, charts, generated bitmaps, or 3D assets   |
| `references/core/visual-verification.md`  | **Always before delivery**           | Screenshot, viewport, text fit, state, asset, and motion verification              |
| `references/core/korea-2026.md`           | Korean-first or Korea-facing UI      | Korean service patterns, CJK typography, formats, mobile flows                     |
| `references/core/ux-writing-ko.md`        | Korean UI copy                       | Natural Korean labels, error messages, tone, spacing, punctuation                  |
| `references/core/soft-3d-asset-gates.md`  | 3D/miniature/character-like visuals  | Toss-style soft 3D vs generic cute asset slop, domain gates                        |
| `references/core/motion.md`               | Motion/animation needed              | CSS animations, Framer Motion, scroll-driven, View Transitions, domain gates       |
| `references/core/iterative-design.md`     | Multi-round design                   | LLM convergence problem, Diverge→Kill→Mutate process, upgrade techniques           |
| `references/stacks/react.md`              | React projects                       | Server Components, hooks, state, TanStack Query, shadcn/ui, performance            |
| `references/stacks/nextjs.md`             | Next.js projects                     | App Router, RSC, image optimization, data fetching, middleware                     |
| `references/stacks/vanilla.md`            | HTML+CSS+JS (no framework)           | Zero-dependency, viewport fitting, responsive CSS, progressive enhancement         |
| `references/stacks/svelte.md`             | Svelte/SvelteKit projects            | Svelte conventions, reactivity, stores, SvelteKit routing                          |

Start with `anti-slop.md`, `aesthetics.md`, and `visual-verification.md`. Add domain/locale/stack references only when relevant.

---

## 0. Frontend Routing

Before designing or coding, classify the work:

| Decision | Options | Why It Matters |
| --- | --- | --- |
| Product surface | landing, app, dashboard, AI tool, public service, education, game, creative | Sets density, typography scale, asset requirements |
| Locale | Korean-first, global/i18n, English-only | Sets CJK typography, copy, date/number formats |
| Density | campaign, consumer app, productivity, SaaS, ops, finance, developer console | Prevents landing-page composition inside repeated-work tools |
| Asset need | none, screenshot, product photo, diagram, chart, illustration, soft 3D, game asset | Prevents asset-free gradient/card UI |
| Soft 3D/character gate | not allowed, subtle, primary | Prevents generic cute 3D/mascot slop |
| Motion intensity | static, feedback-only, expressive, cinematic | Prevents cinematic motion in utility workflows |

Default rules:
- For apps/tools/dashboards, build the actual working surface first, not a marketing hero.
- For Korean-first work, read `korea-2026.md` and `ux-writing-ko.md`.
- For any soft 3D miniature, mascot, chibi, toy-like object, or character-like asset, read `soft-3d-asset-gates.md`.
- For product/brand/object/place/person pages, use concrete visual assets in the first viewport.
- For finance, government, B2B, admin, auth, security, and developer tools, keep visual warmth restrained and subordinate to clarity.

---

## 1. Component Identification

When the user describes UI in vague terms (e.g. "접히는 거", "팝업 같은 거"):
1. Suggest 2-3 candidate components: `<Name> — <what it looks/works like>`
2. Recommend one with reasoning for this use case
3. Confirm, then proceed

If the user already names a specific component, skip this step.
Reference: [component.gallery/components](https://component.gallery/components/)

For new React/Vue/Svelte/Next UI source files, prefer `.tsx` or typed component files when the repo supports TypeScript. Inherit `dev` TypeScript strict-compatibility rules.
If frontend structure is unclear, read existing source-of-truth docs/logs first, then document pages, components, routes, state stores, and build commands in the repo's existing SOT before broad implementation.

---

## 2. Design Thinking

Before coding, commit to a domain-correct direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Surface**: Is this a working tool, dashboard, public service, AI workflow, game, landing page, or editorial surface?
- **Tone**: Pick a specific direction. For product tools this often means quiet, dense, trustworthy, and fast rather than loud.
- **Constraints**: Framework, performance budget, accessibility requirements.
- **Signature**: What ONE thing will make this unforgettable?

Intentionality over intensity. Bold maximalism, refined minimalism, dense utility, and friendly consumer UI can all work when they match the domain.

---

## 3. Baseline Configuration

Adjust these dials based on what's being built. Present to user if unclear.

| Dial             | Default | Range | Meaning                              |
| ---------------- | :-----: | :---: | ------------------------------------ |
| DESIGN_VARIANCE  |    5    | 1-10  | 1=symmetric utility, 10=asymmetric art |
| MOTION_INTENSITY |    4    | 1-10  | 1=static, 10=cinematic choreography    |
| VISUAL_DENSITY   |    5    | 1-10  | 1=art gallery airy, 10=cockpit dense   |

Adapt dynamically based on user requests. Dashboard → density up. Portfolio → variance up. Data tool → motion down.
Korean app/tool surfaces usually need higher density and clearer hierarchy, not oversized hero text.

---

## 4. Implementation

Read `references/core/aesthetics.md` for full guidelines. Summary:

- **Typography**: Use domain-appropriate typography. For Korean-first UIs, prioritize CJK-safe stacks before Latin display fonts.
- **Color**: Max 1 accent. Use neutral bases (Zinc/Slate) with singular high-contrast accent — avoid purple-on-white.
- **Layout**: Match the product surface. Avoid centered-card/hero patterns in repeated-use tools.
- **Motion**: See `references/core/motion.md`. One well-choreographed page load > 10 scattered effects.
- **Assets**: Use screenshots, product images, diagrams, charts, illustrations, generated bitmaps, or soft 3D only when they add product meaning.

---

## 5. Anti-Slop Enforcement

Read `references/core/anti-slop.md` for full rules. Key standards:

- Treat unexamined default typography as a slop signal. Choose a domain-appropriate stack; Korean-first UI should use CJK-safe fonts and system fallbacks deliberately.
- Use neutral or intentional color palettes — purple gradients on white are a slop signal
- Use asymmetric or purposeful layouts — centered-everything reads as template
- Vary card sizes, spans, and groupings — equal 3-card grids read as generic
- Avoid oversized bold hero text inside tools, dashboards, admin, finance flows, and public services
- Avoid asset-free UI: abstract blobs/gradients do not replace real visual evidence
- Avoid generic soft 3D icon packs; soft 3D must be semantic, brand-consistent, and restrained
- Use icons or descriptive text instead of emoji in code and UI
- Use off-black (`#0a0a0a`, `#111`) — pure `#000000` lacks depth
- Use realistic, specific names and brands in placeholder content
- Write original copy — avoid "Elevate", "Seamless", "Next-Gen" and similar clichés

---

## 6. Performance Guardrails

- Animate `transform` and `opacity` only — layout properties (`top`, `left`, `width`, `height`) cause jank
- Grain/noise filters → fixed pseudo-elements only, keep off scrolling containers
- `will-change` sparingly — remove after animation completes
- Z-index only for systemic layers (navbar, modal, overlay)
- Memoize perpetual animations in isolated components

---

## 7. Accessibility Baseline

- Semantic HTML (`<button>`, `<nav>`, `<main>`)
- Keyboard navigation for all interactive elements
- WCAG AA minimum (4.5:1 normal text, 3:1 large text)
- Visible focus indicators (`focus-visible:ring-2`)
- `prefers-reduced-motion` support
- Skip link or equivalent bypass for repeated navigation
- Focus must not be hidden by sticky headers, sticky bottom bars, sheets, or overlays
- Icon-only buttons need accessible names (`aria-label`, visible text, or labelled-by)
- Charts, status messages, loading progress, and AI streaming states need screen-reader labels or live regions where appropriate
- Do not encode meaning by color alone
- Modals, menus, comboboxes, bottom sheets, and command palettes must have a complete keyboard path
- Stress-test Korean long labels and screen-reader names; clipped Hangul is a failure
- Pointer targets follow WCAG 2.2 AA target-size rules; 44×44px is a conservative product baseline, not the only legal minimum

---

## 8. Custom Hook Patterns

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

## 9. React Performance Optimization

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

## 10. Form Handling

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

## 11. Accessibility Quick-Wins

Beyond the baseline (§7), add these interaction patterns:

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

## 12. Pre-Flight Checklist

Before delivering:
- [ ] Domain-correct direction chosen and committed
- [ ] Product surface, locale, density, asset need, soft 3D gate, and motion intensity classified
- [ ] Anti-slop patterns enforced (§5)
- [ ] Oversized hero text avoided unless this is a true hero surface
- [ ] Required assets are real, semantic, rendered, and not generic decoration
- [ ] Korean-first UI follows CJK typography and Korean UX writing rules
- [ ] Soft 3D/miniature/character assets pass domain and semantic gates
- [ ] Mobile layout collapse guaranteed (`px-4`, `max-w-7xl mx-auto`)
- [ ] Full-height sections use `min-h-[100dvh]` not `h-screen`
- [ ] Loading, empty, and error states provided
- [ ] `useEffect` animations have cleanup functions
- [ ] Custom hooks tested independently (§8)
- [ ] Memoization applied only where measured impact (§9)
- [ ] Forms validate with schema and show field-level errors (§10)
- [ ] Focus management on modals and popovers (§11)
- [ ] Desktop/mobile/narrow screenshots checked for overlap, clipping, and asset rendering
- [ ] Interactive components isolated as Client Components (if RSC)
- [ ] Stack-specific rules followed (see `references/stacks/`)

---

## 13. Backend Contract & Security Alignment

Frontend does not operate in isolation. When consuming backend APIs or implementing security-sensitive UI:

### 13.1 Contract Ownership

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

### 13.2 Security Responsibilities

| Control | Policy Owner | Implementation Owner |
|---------|-------------|---------------------|
| CSP directives | `dev-security` §5 | Frontend (no inline scripts, no `eval`, no surprise 3rd-party scripts) |
| CORS | `dev-security` §5 | Backend middleware (`dev-backend` §4) |
| XSS prevention | `dev-security` §5 | Frontend (avoid `dangerouslySetInnerHTML`; if needed, sanitize with DOMPurify + CSP defense) |
| Token storage | `dev-security` §2 | Frontend (`httpOnly` cookies preferred over `localStorage`) |
| Auth state display | `dev-security` §2 | Frontend (loading → check → redirect or render; never flash protected content) |

### 13.3 Testing Integration

- Playwright smoke tests validate rendered flows AFTER backend API + contract tests pass
- Frontend unit tests mock API responses using the **same envelope shape** defined in `dev-backend` §5
- When backend error codes change, frontend error-mapping tests must be updated
