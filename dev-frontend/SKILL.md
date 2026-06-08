---
name: dev-frontend
description: "Production-grade frontend with distinctive aesthetics. Detects stack and applies specialized rules. Modular: SKILL.md orchestrator + references/ for deep guidance. Injected when role=frontend."
keywords: [kanban-ui, reminder-ui, priority-matrix, dashboard-ui, notes-ui]
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
| `references/core/typography-wrapping.md`  | **Always**                           | `text-wrap: balance/pretty`, **short descriptor category** (`balance` not `pretty` for 1-3 line text), `ch` units, rag control, Korean orphan prevention, `-webkit-line-clamp` conflict |
| `references/core/logo-sections.md`        | Integration/partner logo display     | Marquee CSS, static grid, orphan cell fix, grayscale treatment, no individual hover |
| `references/core/brand-asset-sourcing.md` | Brand logos in UI                    | Simple Icons/SVGL sourcing, AI agent strategy, placeholder hierarchy, legal guide  |
| `references/core/layout-discipline.md`    | Landing/marketing pages              | Hero, eyebrow, section repetition, bento, zigzag, **per-section responsive transforms** |
| `references/core/consistency-locks.md`    | Any multi-section page               | Color, shape, theme consistency per page                                             |
| `references/core/responsive-viewport.md`  | **Always**                           | Canonical breakpoints, page containment, container queries, responsive images, safe area, split-screen |
| `references/core/mobile-ux.md`            | Consumer/landing pages with mobile traffic | Thumb zone, touch targets, sticky CTA, mobile section composition, bottom sheet, portrait media |
| See also: `dev-uiux-design` skill         | Vague requests, onboarding, UX states | Intent discovery, design isms, product personalities, onboarding/empty/error patterns |
| `references/stacks/react.md`              | React projects                       | Server Components, hooks, state, TanStack Query, shadcn/ui, performance            |
| `references/stacks/nextjs.md`             | Next.js projects                     | App Router, RSC, image optimization, data fetching, middleware                     |
| `references/stacks/vanilla.md`            | HTML+CSS+JS (no framework)           | Zero-dependency, viewport fitting, responsive CSS, progressive enhancement         |
| `references/stacks/svelte.md`             | Svelte/SvelteKit projects            | Svelte conventions, reactivity, stores, SvelteKit routing                          |

Start with `anti-slop.md`, `aesthetics.md`, `responsive-viewport.md`, and `visual-verification.md`. Add domain/locale/stack references only when relevant.

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
- For text-heavy surfaces (landing, marketing, editorial, public service), apply typography wrapping defaults — see `typography-wrapping.md`. Dashboard table cells are excluded.

---

## 1. Component Identification

When the user describes UI in vague terms (e.g. "접히는 거", "팝업 같은 거"):
1. Recommend the best-fit component with reasoning: `<Name> — <what it does, why it fits>`
2. Confirm, then proceed

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

When user intent is vague ("깔끔하게", "모던하게", "just make it look good"), read the `dev-uiux-design` skill and run the User Intent Discovery Protocol before making routing decisions.
If the user cannot answer these questions, use the `dev-uiux-design` skill's structured preference elicitation flow. Offer product references ("Notion 느낌? Linear 느낌?") and visual comparisons.

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

- **Typography**: Use domain-appropriate typography. For Korean-first UIs, prioritize CJK-safe stacks before Latin display fonts. Apply `text-wrap: balance` on all headings **AND short descriptors** (hero subtitle, card description, caption — anything 1-3 lines). Use `text-wrap: pretty` only on body paragraphs (4+ lines). `pretty` has no effect on short text and will leave Korean orphans like "합니다." or "화." on a line alone. See `typography-wrapping.md` for full rules.
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
- **NEVER use emoji as UI visual elements** (feature icons, card icons, section markers, buttons) — emoji in production UI is the #1 AI slop signal. Use SVG icons (Lucide/Phosphor/Heroicons). See `anti-slop.md § Emoji Slop`
- Warm beige/cream backgrounds with brass/clay accents are banned as defaults for premium-consumer briefs — see `anti-slop.md § Premium-Consumer Palette Ban`
- Layout monotony (same family repeated, 3+ zigzag sections, overused eyebrows) — see `references/core/layout-discipline.md`
- Color, shape, and theme must be locked per-page and audited before shipping — see `references/core/consistency-locks.md`
- Use off-black (`#0a0a0a`, `#111`) — pure `#000000` lacks depth
- **Responsive enforcement**: every multi-column section must declare its mobile/tablet collapse behavior — "it'll work at mobile" is not a plan. See `responsive-viewport.md`
- **Page containment required**: `max-w-[1400px] mx-auto` or equivalent wrapper. Content stretching to viewport edges on wide monitors is a layout bug
- **Mobile is a different product**: section composition, CTA placement, and interaction model change on mobile — it is NOT just "desktop stacked vertically." See `mobile-ux.md`
- Use realistic, specific names and brands in placeholder content
- Write original copy — avoid "Elevate", "Seamless", "Next-Gen" and similar clichés
- Treat uncontrolled heading line breaks (orphaned single word, no `text-wrap`, no `max-width` in `ch`) as a slop signal — see `typography-wrapping.md`
- Treat short descriptors (hero subtitle, card description, caption) using `text-wrap: pretty` instead of `balance` as a slop signal — `pretty` does nothing on 1-3 line text, especially Korean
- Treat Korean orphan fragments ("합니다.", "화.", "입니다." alone on a line) as a slop signal — always verify Korean text breaks at target viewports
- Treat generic stroke icons as brand logo substitutes as a slop signal — use actual brand SVGs from Simple Icons, SVGL, or press kits. See `brand-asset-sourcing.md`

---

## 6. Performance Guardrails

- Animate `transform` and `opacity` only — layout properties (`top`, `left`, `width`, `height`) cause jank
- Grain/noise filters → fixed pseudo-elements only, keep off scrolling containers
- `will-change` sparingly — remove after animation completes
- Z-index only for systemic layers (navbar, modal, overlay)
- Memoize perpetual animations in isolated components

### Browser Connection Limits

| Protocol | Limit |
|---|---|
| HTTP/1.1 | 6 connections per domain (Chrome/Firefox) |
| HTTP/2 | 1 TCP connection, 100 concurrent streams |
| WebSocket | Shares the HTTP/1.1 connection pool |

Rules:
- Never open >2 SSE/WebSocket connections to the same origin from one page
- Use connection multiplexing (single WebSocket with channel/topic routing) over multiple connections
- If >6 parallel requests needed: use HTTP/2, batch API endpoints, or domain sharding (last resort)
- Preflight OPTIONS requests count against the connection limit; consolidate CORS-heavy calls

Banned:
- Opening unbounded WebSocket connections per component instance
- Polling from multiple components independently (centralize into one subscription, fan out via state)
- Creating new SSE connections on every remount without cleanup

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

## 8. Custom Hooks

Create a custom hook only when it owns reusable behavior, not just because code is a few lines long.

Good hook candidates: subscription lifecycle, reusable async state machine, form-field behavior shared across components, media/query/observer integration, keyboard/focus behavior, external store wrapper.

Avoid hooks that are merely thin aliases for `useState`, `useToggle`, `useDebounce`, or one-off component logic unless the repo already standardizes them.

Hook rules:
- The hook name describes behavior, not implementation
- Inputs are explicit and stable; return shape is small
- Side effects are justified by an external system; cleanup is correct
- Dependencies are honest; use `useEffectEvent` for non-reactive callbacks inside Effects
- Do not hide server state, router state, or form ownership inside a generic hook

---

## 9. React Performance

Default performance strategy: keep components pure, keep state local, classify state ownership correctly, use server rendering/caching boundaries, split expensive client islands, measure before memoizing.

| Tool | Use when |
|------|----------|
| `memo` | child render is expensive and props are stable |
| `useMemo` | calculation is expensive or identity is required |
| `useCallback` | callback identity is required by memoized child or external API |
| `useTransition` | interaction should stay responsive while non-urgent work completes |
| `useOptimistic` | mutation UX benefits from reversible optimistic state |
| `Activity` | hidden UI should preserve state without active Effects |
| `Suspense` | dynamic/async boundary needs isolated loading behavior |

If React Compiler is enabled, remove defensive memoization unless measurement or semantics justify it. Split at route boundaries and heavy components (charts, editors, 3D).

---

## 10. Form Handling

For simple forms, use controlled components with schema validation (Zod). For complex forms (multi-step, dynamic fields), use `react-hook-form` + Zod resolver. Always show field-level errors with `role="alert"`.

---

## 11. Accessibility Quick-Wins

Beyond the baseline (§7):
- Focus management: trap focus in modals, restore on close, handle Escape
- Arrow keys navigate lists and menus; Enter/Space activate buttons and links
- Tab order follows visual flow
- `aria-expanded`, `aria-haspopup`, `aria-activedescendant` on composite widgets
- Test with screen reader and keyboard-only navigation

---

## 12. 2026 Frontend Platform Rules

Use this section when modernizing or creating React/Next/Vite frontends. Prefer project conventions first.

### React 19.2+

- **Activity**: Use `<Activity>` for state-preserving hidden UI (tabs, drawers, route shells). Do not use for security hiding or active subscriptions.
- **useEffectEvent**: For non-reactive logic inside Effects that needs latest props/state without resubscribing. Never call during render or pass to children.
- **Partial Pre-rendering**: Design pages as static shell + explicit dynamic holes + Suspense boundaries. No `Date.now()`, `Math.random()`, or request-specific data in the pre-rendered shell.
- **React Compiler**: Do not cargo-cult `memo`/`useMemo`/`useCallback`. Measure first unless referential stability is semantically required.

### Next.js 16

- Turbopack is default. Do not add custom webpack config unless proven unsupported.
- **Cache Components** (`cacheComponents: true`): dynamic rendering is default; cache only what you explicitly mark with `use cache` + `cacheLife` + `cacheTag`.
- Never cache user/session-specific data without explicit user-scoped cache key.
- Server Actions: validate input server-side, authorize against the resource, revalidate affected cache tags.

### Modern CSS

Prefer native CSS before JS layout observers or animation libraries:
- **Container queries** for component-level responsive layout (not viewport)
- **`:has()`** for parent/sibling state selection — keep selectors narrow
- **CSS nesting** for modularity — keep shallow, avoid specificity tunnels
- **Subgrid** when nested content must align to outer grid
- **View Transitions** for meaningful state continuity — respect `prefers-reduced-motion`
- **Modern units**: `dvh/svh/lvh` over `100vh`, logical properties over `left/right`
- **Tailwind v4**: CSS-first configuration, use theme variables over hardcoded values

### Build Tools

- **Vite 7**: ESM-only, Node 20.19+/22.12+, baseline-widely-available target
- **Rolldown**: experimental drop-in for Vite; pin versions, compare output before production
- Do not introduce Webpack-era config unless the existing app is already Webpack-bound

### State Classification

Before adding state, classify it:

| State type | Owner | Default tool |
|---|---|---|
| render-local UI | nearest component | `useState` / `useReducer` |
| derived | render calculation | expression / `useMemo` if expensive |
| form draft | form boundary | native form, React Hook Form, TanStack Form |
| server/cache | server/cache layer | RSC, Next cache, TanStack Query, SWR |
| URL/navigation | router | path params, search params |
| global client UI | external store | Zustand, Jotai, context |
| optimistic mutation | mutation boundary | `useOptimistic`, mutation library |
| AI stream | conversation boundary | append-only message model + stream status |

Rules: Do not store derived state just to sync with Effect. Do not put server state in Zustand. Do not put URL-shareable state only in component state. Keep optimistic state reversible.

### shadcn/ui and AI-Assisted UI

- Inspect existing installed components before adding new ones
- Use project's `components.json`, aliases, tokens, and registry conventions
- Do not hallucinate design-system components; verify against local source
- Remove demo-only copy and unused variants

For AI-native interfaces (chat, agent, copilot), design explicit states: empty → prompt ready → submitted → streaming → tool call → result → complete → feedback. Never fake streaming, citations, or tool calls.

---

## 13. Pre-Flight Checklist

Before delivering:
- [ ] Domain-correct direction chosen and committed
- [ ] Product surface, locale, density, asset need, soft 3D gate, and motion intensity classified
- [ ] Anti-slop patterns enforced (§5)
- [ ] Oversized hero text avoided unless this is a true hero surface
- [ ] Required assets are real, semantic, rendered, and not generic decoration
- [ ] Korean-first UI follows CJK typography and Korean UX writing rules
- [ ] Soft 3D/miniature/character assets pass domain and semantic gates
- [ ] Mobile layout collapse guaranteed with per-section-type rules (see layout-discipline.md § Responsive Transforms)
- [ ] Full-height sections use `min-h-[100dvh]` not `h-screen`
- [ ] Page containment: `max-w-[1400px] mx-auto` wrapper present (see responsive-viewport.md)
- [ ] Tested at 768px (tablet) and 1024px (split-screen) in addition to mobile/desktop
- [ ] Touch targets ≥ 44px on mobile; no hover-only interactions (see mobile-ux.md)
- [ ] Responsive images use `srcset`/`sizes` or `<picture>` for art direction (see responsive-viewport.md)
- [ ] Safe area padding for notched devices: `env(safe-area-inset-*)` on fixed elements
- [ ] Loading, empty, and error states provided
- [ ] State classified before adding store/Context/Effect/cache (§12)
- [ ] Effects sync with external systems; derived state is not Effect-synced
- [ ] Container queries considered before viewport-query or JS layout workarounds
- [ ] View transitions respect reduced motion
- [ ] shadcn components follow local registry and token conventions
- [ ] AI UI states are honest: no fake streaming, citations, or tool calls
- [ ] Forms validate with schema and show field-level errors (§10)
- [ ] Focus management on modals and popovers (§11)
- [ ] Desktop/mobile/narrow screenshots checked for overlap, clipping, and asset rendering
- [ ] Interactive components isolated as Client Components (if RSC)
- [ ] Design Read declared before code generation (see dev-uiux-design §2)
- [ ] Eyebrow count ≤ ceil(sectionCount / 3) (see layout-discipline.md)
- [ ] Section layout diversity: ≥4 different families per 8 sections
- [ ] Color/shape/theme locks consistent across all sections (see consistency-locks.md)
- [ ] Stack-specific rules followed (see `references/stacks/`)

---

## 14. Backend Contract & Security Alignment

Frontend does not operate in isolation. When consuming backend APIs or implementing security-sensitive UI:

### 14.1 Contract Ownership

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

### 14.2 Security Responsibilities

| Control | Policy Owner | Implementation Owner |
|---------|-------------|---------------------|
| CSP directives | `dev-security` §5 | Frontend (no inline scripts, no `eval`, no surprise 3rd-party scripts) |
| CORS | `dev-security` §5 | Backend middleware (`dev-backend` §4) |
| XSS prevention | `dev-security` §5 | Frontend (avoid `dangerouslySetInnerHTML`; if needed, sanitize with DOMPurify + CSP defense) |
| Token storage | `dev-security` §2 | Frontend (`httpOnly` cookies preferred over `localStorage`) |
| Auth state display | `dev-security` §2 | Frontend (loading → check → redirect or render; never flash protected content) |

### 14.3 Testing Integration

- Playwright smoke tests validate rendered flows AFTER backend API + contract tests pass
- Frontend unit tests mock API responses using the **same envelope shape** defined in `dev-backend` §5
- When backend error codes change, frontend error-mapping tests must be updated
