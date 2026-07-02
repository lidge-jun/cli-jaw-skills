---
name: dev-frontend
description: "MUST USE for any frontend, web UI, or visual implementation work — building, styling, or redesigning pages/components, responsive layouts, motion, component architecture, and production-surface polish. Triggers: frontend, UI, component, CSS, responsive, animation, React, Vue, Svelte, Tailwind, layout, styling, redesign, mockup, anti-slop, 프론트엔드, UI 작업, 반응형, 디자인 수정."
metadata:
  short-description: "Frontend implementation with responsive, accessible, anti-slop UI guidance."
  keywords: "frontend, UI, component, CSS, responsive, layout, animation, design implementation"
  last-verified: "2026-07-02"
---

# Dev-Frontend — Domain-Correct Frontend Engineering

Build distinctive, production-grade interfaces that fit the product domain, locale, interaction model, and real visual evidence.
This skill has modular references for specialized guidance — read the relevant ones before coding.
It activates by change surface whenever the work is primarily frontend, UI, styling, responsive layout, or animation.

> **C0/C1 work (small local patches):** See `dev` §0.0 Work Classifier + §0.1 Patch Fast-Path before reading references.

## Modular References

| File                                      | When to Read                         | What It Covers                                                                    |
| ----------------------------------------- | ------------------------------------ | --------------------------------------------------------------------------------- |
| `references/core/crud-ui.md`              | C2 list/detail/form product screens  | State coverage (loading/empty/error/permission), forms, objective UX gates         |
| `references/core/anti-slop.md`            | New components or UI redesign        | 2026 AI slop patterns, Korean slop, oversized text, fake assets, default UI smells |
| `references/core/aesthetics.md`           | Visual design decisions              | Domain-correct visual direction, typography, color, composition                    |
| `references/core/product-density.md`      | Apps, tools, dashboards              | Density profiles for landing, consumer app, SaaS, ops, finance, devtools          |
| `references/core/asset-requirements.md`   | Any public/product/visual surface    | Required screenshots, images, diagrams, charts, generated bitmaps, or 3D assets   |
| `references/core/visual-verification.md`  | Changes affecting rendered layout    | Screenshot, viewport, text fit, state, asset, and motion verification              |
| `references/core/korea-2026.md`           | Korean-first or Korea-facing UI      | Korean service patterns, CJK typography, formats, mobile flows                     |
| `references/core/ux-writing-ko.md`        | Korean UI copy                       | Natural Korean labels, error messages, tone, spacing, punctuation                  |
| `references/core/soft-3d-asset-gates.md`  | 3D/miniature/character-like visuals  | Toss-style soft 3D vs generic cute asset slop, domain gates                        |
| `references/core/motion.md`               | Motion/animation needed              | CSS animations, Framer Motion, scroll-driven, View Transitions, domain gates       |
| `references/core/iterative-design.md`     | Multi-round design                   | LLM convergence problem, Diverge→Kill→Mutate process, upgrade techniques           |
| `references/core/prototype-variants.md`   | Runnable design variants             | `?variant=` switchers, structurally distinct options, cleanup after winner selection |
| `references/core/typography-wrapping.md`  | Heading/descriptor text changes      | `text-wrap: balance/pretty`, **short descriptor category** (`balance` not `pretty` for 1-3 line text), `ch` units, rag control, Korean orphan prevention, `-webkit-line-clamp` conflict |
| `references/core/logo-sections.md`        | Integration/partner logo display     | Marquee CSS, static grid, orphan cell fix, grayscale treatment, no individual hover |
| `references/core/brand-asset-sourcing.md` | Brand logos in UI                    | Simple Icons/SVGL sourcing, AI agent strategy, placeholder hierarchy, legal guide  |
| `references/core/layout-discipline.md`    | Landing/marketing pages              | Hero, eyebrow, section repetition, bento, zigzag, **per-section responsive transforms** |
| `references/core/consistency-locks.md`    | Any multi-section page               | Color, shape, theme consistency per page                                             |
| `references/core/responsive-viewport.md`  | Layout or breakpoint changes         | Canonical breakpoints, page containment, container queries, responsive images, safe area, split-screen |
| `references/core/mobile-ux.md`            | Consumer/landing pages with mobile traffic | Thumb zone, touch targets, sticky CTA, mobile section composition, bottom sheet, portrait media |
| `references/core/seo-baseline.md`         | Public-facing sites, SSR/SSG           | SEO meta, JSON-LD, robots.txt, GEO strategies, OG/Twitter cards                      |
| `references/core/a11y-patterns.md`        | Interactive widgets, modals, forms     | ARIA patterns, focus management, keyboard nav, screen reader testing                  |
| `references/core/performance-budget.md`   | Launch / audit                         | CWV targets, bundle budgets, font loading, image optimization, build gates, browser connection budgets |
| `references/core/preflight-full.md`       | Launch / audit                         | Full ~40-item pre-flight checklist (router §14 keeps only blocking gates)             |
| `references/core/theme-switching.md`      | Dark mode / theme                      | CSS custom properties toggle, FOWT prevention, transition, component checklist         |
| `references/core/i18n-global.md`          | Multi-language / RTL                   | RTL layout, pluralization, Intl API, locale switching, content expansion               |
| See also: `dev-uiux-design` skill         | Vague requests, onboarding, UX states | Intent discovery, design isms, product personalities, onboarding/empty/error patterns |
| `references/stacks/react.md`              | React projects                       | Server Components, hooks, state, TanStack Query, shadcn/ui, performance            |
| `references/stacks/nextjs.md`             | Next.js projects                     | App Router, RSC, image optimization, data fetching, middleware                     |
| `references/stacks/vanilla.md`            | HTML+CSS+JS (no framework)           | Zero-dependency, viewport fitting, responsive CSS, progressive enhancement         |
| `references/stacks/svelte.md`             | Svelte/SvelteKit projects            | Svelte 5 Runes, SvelteKit 2 routing/actions, snippets, migration from Svelte 4    |
| `references/stacks/mobile-native.md`        | Native mobile app development  | RN/Expo current pairing, Flutter 3.44, KMP, Swift 6, framework selection          |
| `references/stacks/astro.md`              | Astro projects                       | Islands architecture, multi-framework shell, content collections, SSG/SSR/hybrid   |

Start with `anti-slop.md`, `aesthetics.md`, `responsive-viewport.md`, and `visual-verification.md`. Add domain/locale/stack references only when relevant.
For C2 ordinary app screens (form/table/list/detail), `crud-ui.md` alone suffices; add the style references above for marketing/visual surfaces or C3+ work.

When frontend choices depend on current framework, design-system, browser API,
library behavior, browser-rendered source evidence, or package/source freshness,
read the active `search` skill and follow its source-fetch and evidence-status
rules before treating external material as proof.

### Verification grounding

**STRICT:** For render/executable artifacts (HTML, SVG, games, UI, charts),
run the real renderer: headless browser, screenshot, canvas check, or equivalent.
Observe the actual output yourself, fix what observation reveals, then re-run.
Static parsing confirms well-formed files; it does not prove the artifact is
visually or interactively correct. One clean observation is enough for unchanged
state; do not re-render unchanged output just to repeat evidence.

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
- Every user-facing decision point must justify its existence — defaults first, one primary action per screen, choices demoted to progressive disclosure; surface-conditional per density profile (`dev-uiux-design` UX-LAZY-01 owns the gate).
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

## 1.5 Objective Gates vs Style Samples

Two different kinds of rules live in this skill (see `dev` §0.2):
- **Objective UX gates (STRICT/DEFAULT)** — accessibility baseline (§7, §11), state coverage
  (loading/empty/error/permission), keyboard operability, visible focus, contrast. Missing
  these are review findings.
- **Style direction (STYLE_SAMPLE)** — design thinking (§2), aesthetics, density profiles,
  product personalities, preset tokens, and the concrete values in §4-§5 (palettes, font
  choices, pixel max-widths). These illustrate acceptable choices; they are NOT
  requirements, must not override an existing design system (Design System Detection stays
  MANDATORY), and must never be enforced as universal taste (UX-STYLE-01).

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

After Design Read, set dials per `dev-uiux-design` §2 Dial Setting.

Product density profile (D1-D8 in `references/core/product-density.md`) sets component class; VISUAL_DENSITY (1-10) sets spacing within that class. These are orthogonal axes.

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

Rule classes (dev §0.2): items below are DEFAULT — deviate with a stated reason; concrete
values and palettes are STYLE_SAMPLE (§1.5); the emoji-as-UI-icon ban is the only STRICT item.

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

- Animate `transform` and `opacity` only — layout properties cause jank
- Grain/noise filters → fixed pseudo-elements only, off scrolling containers
- `will-change` sparingly (remove after animation); z-index only for systemic layers
- Memoize perpetual animations in isolated components
- **Browser connection budgets** (≤2 SSE/WS per origin per page, multiplex over
  multiplying, no per-component polling): detail + limits table in
  `references/core/performance-budget.md` (this skill owns browser-side budgets;
  server connection lifecycle is owned by `dev-backend` §1)

---

## 7. Accessibility Baseline

- Semantic HTML (`<button>`, `<nav>`, `<main>`); keyboard navigation for all interactive elements
- WCAG AA minimum (4.5:1 normal text, 3:1 large text); visible focus indicators; `prefers-reduced-motion`
- Skip link; focus never hidden by sticky headers/bars/sheets/overlays
- Icon-only buttons need accessible names; charts/status/loading/AI-streaming states need labels or live regions
- Do not encode meaning by color alone
- Modals, menus, comboboxes, bottom sheets, command palettes: complete keyboard path —
  trap focus, restore on close, Escape; arrow-key navigation; honest `aria-expanded`/
  `aria-haspopup`/`aria-activedescendant`; tab order follows visual flow
- Stress-test Korean long labels and screen-reader names; clipped Hangul is a failure
- Pointer targets follow WCAG 2.2 AA target-size (24×24 CSS px minimum with exceptions);
  44×44px is a conservative product baseline, not the legal minimum
- Test with screen reader and keyboard-only navigation; deep patterns → `a11y-patterns.md`

---

## 8. React Behavior Rules (hooks · performance · forms)

Full guidance moved to `references/stacks/react.md` § Behavior Rules. Router decisions:

| Decision | Rule |
|----------|------|
| New custom hook | Only when it owns reusable behavior (subscription lifecycle, async state machine, shared form-field behavior) — never a thin `useState` alias |
| Memoization | Measure first; with React Compiler enabled, remove defensive `memo`/`useMemo`/`useCallback` unless semantics require identity |
| Perf strategy | Pure components, local state, correct state ownership (§12 table), split expensive client islands |
| Forms | Simple → controlled + schema (Zod); complex/multi-step → react-hook-form + resolver; field errors with `role="alert"` |

---

## 12. 2026 Frontend Platform Rules (verified 2026-07-02)

Use this section when modernizing or creating React/Next/Vite frontends. Prefer project
conventions first. Version-detail depth lives in `references/stacks/react.md` / `nextjs.md`.

### React (19.2.x line)

- **`<Activity>`** (stable): state-preserving hidden UI (tabs, drawers, route shells) — not for security hiding or active subscriptions.
- **useEffectEvent**: non-reactive Effect logic needing latest props/state; never call during render or pass to children.
- **Partial Pre-rendering**: static shell + explicit dynamic holes + Suspense; nothing request-specific in the shell.
- **React Compiler** (stable, optional): measure before memoizing (§8).
- **Performance gate**: inspect React Performance Tracks in Chrome DevTools before adding memoization or blaming rendering.

### Next.js (16.x)

- Turbopack is the default bundler (webpack is opt-in `--webpack`).
- **Cache Components** (`cacheComponents: true`): dynamic by default; cache only explicit `use cache` + `cacheLife` + `cacheTag`; PPR is expressed through Cache Components (the old `experimental.ppr` flag is gone).
- Never cache user/session data without a user-scoped cache key.
- Server Actions: validate server-side, authorize against the resource, revalidate affected tags.

### Modern CSS (Baseline check before shipping)

Prefer native CSS before JS layout observers/animation libraries: container queries,
`:has()`, subgrid (all Baseline widely-available), View Transitions (same-document,
Baseline 2025 newly-available — provide fallback for cautious audiences),
`text-wrap: balance/pretty`, `dvh/svh/lvh` units, logical properties, shallow CSS
nesting. **Tailwind v4** (CSS-first config, theme variables). Record Baseline status
(widely/newly/caution) for each modern feature used and decide fallback per audience.

### Build Tools

- **Vite 8**: Rolldown/Oxc is the integrated default bundler (`rolldown-vite` is only a
  Vite 7 migration bridge). Node 20.19+/22.12+; Baseline target Chrome/Edge 111,
  Firefox 114, Safari 16.4.
- Detect Vite 7 vs 8 before editing config — don't assume Rollup/esbuild-era plugins.
- Do not introduce Webpack-era config unless the app is already Webpack-bound.

### Agent-visible runtime diagnostics (DEFAULT)

Prefer dev servers that surface browser/runtime errors to the CLI/agent before relying
on static review: Vite 8 forwards browser console to the dev server (auto-activates for
coding agents); Next 16 ships DevTools MCP. Wire these before debugging rendered behavior.

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

### Design System Detection (MANDATORY — before creating tokens)

Before inventing design tokens, check:
1. Does the project have an installed design system? (`grep -r "material-ui\|@mui\|carbon-components\|@carbon\|@fluentui\|govuk-frontend\|uswds" package.json`)
2. Does the project have existing tokens? (`find . -name "tokens.*" -o -name "theme.*" -o -name "design-system*"`)
3. Does the brief name a specific design system?

If YES to any: use the official package. Do not recreate CSS by hand.

| System | Package | Import |
|--------|---------|--------|
| Material | @mui/material | `import { Button } from '@mui/material'` |
| Carbon | @carbon/react | `import { Button } from '@carbon/react'` |
| Fluent | @fluentui/react | `import { Button } from '@fluentui/react-components'` |
| GOV.UK | govuk-frontend | `import 'govuk-frontend/dist/govuk/all.scss'` |
| USWDS | @uswds/uswds | `import '@uswds/uswds/css/uswds.css'` |

If NO: proceed with `dev-uiux-design/references/design-system-bootstrap.md`.

### shadcn/ui and AI-Assisted UI

- Inspect existing installed components before adding new ones
- Use project's `components.json`, aliases, tokens, and registry conventions
- Do not hallucinate design-system components; verify against local source
- Remove demo-only copy and unused variants

For AI-native interfaces (chat, agent, copilot), design explicit states: empty → prompt ready → submitted → streaming → tool call → result → complete → feedback. Never fake streaming, citations, or tool calls.

---

## 13. Error Boundaries

Wrap each major section (not the whole app); boundary renders friendly message + retry +
report link; log to monitoring in `componentDidCatch`; never show stack traces to users.
Error hierarchy: field-inline → form-summary → section Error Boundary → page `error.tsx`
→ root boundary (offline/crash page).

---

## 14. Pre-Flight Gates

Gates apply to production surfaces (`dev` §0.4 shared definition); prototypes and
internal demos are exempt unless production polish is requested.
**Full ~40-item checklist: `references/core/preflight-full.md`** — run it for launches
and audits. The blocking gates below are the minimum for every production delivery:

- [ ] Design Read declared before code (dev-uiux-design §2); surface/locale/density/asset/motion classified (§0)
- [ ] Anti-slop enforced (§5) — incl. emoji-as-icon ban (STRICT)
- [ ] Loading, empty, and error states provided
- [ ] Accessibility baseline (§7): keyboard path, focus management, contrast, reduced motion
- [ ] Mobile collapse per section type + touch targets ≥44px + `min-h-[100dvh]` + page containment
- [ ] State classified before adding store/Context/Effect/cache (§12 table)
- [ ] Forms: schema validation + field-level errors (§8)
- [ ] Korean-first UI: CJK typography + `word-break: keep-all` + orphan screenshot check
- [ ] AI UI states honest: no fake streaming, citations, or tool calls
- [ ] Core Web Vitals are the performance gate (INP ≤200ms field data); Lighthouse
      Performance score is an advisory smoke signal, not the blocker — budgets in `performance-budget.md`
- [ ] Rendered verification run (§ Verification grounding): screenshots at mobile/tablet/desktop
- [ ] Error Boundaries wrap major sections (§13); stack-specific rules followed (`references/stacks/`)

---

## 15. Backend Contract & Security Alignment

| Responsibility | Owner |
|---------------|-------|
| Response envelope shape (`success`, `data`, `error`, `meta`) | `dev-backend` defines, `dev-testing` verifies |
| Consumer-side fixture alignment | **Frontend** — keep mocks in sync with `fixtures/contracts/`; payload changes update contract tests BEFORE merging (`dev-testing` §3.5) |
| Error display mapping | Frontend maps `error.code` to messages; never parse `error.message` for logic |
| CSP/XSS/token storage | Policy: `dev-security` §5/§2. Frontend implements: no inline scripts/`eval`; sanitize `dangerouslySetInnerHTML` (DOMPurify) or avoid; `httpOnly` cookies over `localStorage`; never flash protected content |

Playwright smoke validates rendered flows AFTER API + contract tests pass; frontend unit
tests mock the same envelope shape as `dev-backend` §5; error-code changes update
frontend error-mapping tests.
