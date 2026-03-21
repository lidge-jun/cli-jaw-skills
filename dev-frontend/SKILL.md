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

Before coding, commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick a strong direction — don't default to "clean and modern." Choose from: brutally minimal, maximalist, retro-futuristic, luxury/refined, editorial/magazine, brutalist/raw, art deco, cyberpunk, organic/biomorphic, etc.
- **Constraints**: Framework, performance budget, accessibility requirements.
- **Signature**: What ONE thing will make this unforgettable?

**CRITICAL**: Intentionality over intensity. Bold maximalism and refined minimalism both work — the key is committing fully.

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

- **Typography**: Never Inter/Roboto/Arial. Use Geist, Outfit, Satoshi, Cabinet Grotesk, or characterful alternatives.
- **Color**: Max 1 accent. No purple-on-white. Use neutral bases (Zinc/Slate) with singular high-contrast accent.
- **Layout**: Break centered-card patterns. Use asymmetry, overlap, diagonal flow, generous negative space.
- **Motion**: See `references/core/motion.md`. One well-choreographed page load > 10 scattered effects.
- **Backgrounds**: Create atmosphere — gradient meshes, noise textures, geometric patterns, layered transparencies.

---

## 4. Anti-Slop Enforcement

Read `references/core/anti-slop.md` for full rules. Critical bans:

- NO Inter/Roboto/Arial/system-ui fonts
- NO purple gradients on white backgrounds
- NO centered-everything layouts
- NO generic card grids (3 equal cards in a row)
- NO emoji in code or UI
- NO pure black (#000000) — use off-black
- NO generic placeholder names (John Doe, Acme Corp)
- NO AI copywriting clichés ("Elevate", "Seamless", "Next-Gen")

---

## 5. Performance Guardrails

- Animate ONLY `transform` and `opacity` — never `top`, `left`, `width`, `height`
- Grain/noise filters → fixed pseudo-elements only, never on scrolling containers
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

## 7. Pre-Flight Checklist

Before delivering:
- [ ] Bold aesthetic direction chosen and committed
- [ ] No banned anti-slop patterns
- [ ] Mobile layout collapse guaranteed (`px-4`, `max-w-7xl mx-auto`)
- [ ] Full-height sections use `min-h-[100dvh]` not `h-screen`
- [ ] Loading, empty, and error states provided
- [ ] `useEffect` animations have cleanup functions
- [ ] Interactive components isolated as Client Components (if RSC)
- [ ] Stack-specific rules followed (see `references/stacks/`)

---

## 8. Backend Contract & Security Alignment

Frontend does not operate in isolation. When consuming backend APIs or implementing security-sensitive UI:

### 8.1 Contract Ownership

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

### 8.2 Security Responsibilities

| Control | Policy Owner | Implementation Owner |
|---------|-------------|---------------------|
| CSP directives | `dev-security` §5 | Frontend (no inline scripts, no `eval`, no surprise 3rd-party scripts) |
| CORS | `dev-security` §5 | Backend middleware (`dev-backend` §4) |
| XSS prevention | `dev-security` §5 | Frontend (avoid `dangerouslySetInnerHTML`; if needed, sanitize with DOMPurify + CSP defense) |
| Token storage | `dev-security` §2 | Frontend (`httpOnly` cookies preferred over `localStorage`) |
| Auth state display | `dev-security` §2 | Frontend (loading → check → redirect or render; never flash protected content) |

### 8.3 Testing Integration

- Playwright smoke tests validate rendered flows AFTER backend API + contract tests pass
- Frontend unit tests mock API responses using the **same envelope shape** defined in `dev-backend` §5
- When backend error codes change, frontend error-mapping tests must be updated
