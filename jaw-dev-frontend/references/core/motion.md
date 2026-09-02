# Motion Choreography — Animation Engineering Guide

This entry point owns domain gates, intensity, CSS/Framer patterns, and pointer-proximity motion. Continue with [`motion-scroll.md`](motion-scroll.md) for scroll-linked patterns, [`motion-cinematic.md`](motion-cinematic.md) for section transitions, and [`motion-media.md`](motion-media.md) for generated media, performance, reduced motion, and the final honesty audit.

Rules for meaningful, performant animation. One signature moment + a small number of supporting reveals > 10 scattered effects.

---

## Domain Gates

Motion intensity must match the product surface:

| Surface | Default |
| --- | --- |
| Finance, gov, B2B, auth, payment, security | TOOL: scroll-driven = 0 (hard); feedback/state transitions 1-4 OK |
| Dashboards, admin, ops, developer tools | TOOL: scroll-driven = 0 (hard); feedback/state transitions 1-4 OK |
| Consumer apps, education, community | APP: feedback + state-transition motion only; no scroll-motion floor |
| Landing, conversion campaign, marketing, editorial, portfolio | LANDING: scroll-driven floor 2, ceiling ~4; expressive but still performant |
| Experiential microsite, award entry, interactive story | EXPERIENCE: continuous authored choreography only under the narrative, fallback, and reachability gates below |
| Games / interactive art | domain-specific |

## FE-MOTION-BUCKET-01 - Motion Bucket Map (DEFAULT)

Classify the surface before choosing scroll choreography. The bucket map is the
primary gate; `MOTION_INTENSITY` is secondary.

- **LANDING**: landing, conversion campaign, marketing, editorial, portfolio,
  and marketing-facing pages of any product, including AI tools, education, and
  community products. Scroll-driven motion floor = 2, ceiling ~4. The floor is
  **1 signature + >= 1 supporting reveal = floor 2**.
- **EXPERIENCE**: experiential microsites, award entries, and interactive
  stories are carved out of LANDING. Continuous authored choreography is
  allowed only when every scene advances narrative or state, a reduced-motion
  fallback exists, and core information is reachable without precision
  scrolling. A conversion campaign remains LANDING. Evidence: continuous
  Awwwards/CSSDA narratives and the ambient/state utility behavior of Sky Clock
  and Nothing to Watch.
- **APP**: logged-in or in-app consumer, education, and community screens.
  Feedback + state-transition motion only; no scroll-motion floor.
- **TOOL**: dashboards, admin, finance, gov, B2B repeated-work, developer
  consoles, auth, and payment surfaces. Scroll-driven motion = 0 (hard);
  feedback/state transitions at levels 1-4 are preserved.
- **Games / interactive art**: domain-specific and exempt.

A "scroll motion" is one distinct choreographed scroll-driven moment, either a
signature moment or a supporting reveal. Identical per-section fade-up
repetition counts as one supporting moment total, not N. The floor applies to
the base experience only; `prefers-reduced-motion` and missing `@supports`
legitimately deliver zero motion.

Avoid cinematic page loads for repeated-work tools. Motion should clarify state, not slow the task.


### Award-Entry Experience Carve-Out (FE-MOTION-EXPERIENCE-01, DEFAULT)

Experiential microsites, award entries, and interactive stories may use continuous authored choreography only when every scene advances narrative or state, a reduced-motion fallback exists, and the core route remains reachable without precision scrolling. Marketing and conversion pages remain governed by the landing/campaign row above; an award reference alone does not justify cinematic motion.

Count repeated identical fade-ups as one motion idea, not many. Prefer one signature moment plus a small number of supporting reveals, and verify the static/reduced-motion reading order independently.

Avoid cinematic page loads for repeated-work tools. Motion should clarify state, not slow the task.

## MOTION_INTENSITY Levels

| Level | Rules                                                                                                           |
| :---: | --------------------------------------------------------------------------------------------------------------- |
|  1-3  | No automatic animations. CSS `:hover` and `:active` only.                                                       |
|  4-7  | Enumerate transition properties, usually `transform`, `opacity`, `background-color`, `border-color`, `box-shadow`. `animation-delay` cascades. |
| 8-10  | Complex scroll-triggered reveals. Framer Motion hooks. NEVER `window.addEventListener('scroll')`.               |

---

Never use `transition-all` as a default in Tailwind or CSS all-property transitions. Enumerate the properties so layout, width, height, and color changes do not animate accidentally.

## CSS-Only Patterns (Level 4-7)

## MOTION_INTENSITY Levels

| Level | Rules                                                                                                           |
| :---: | --------------------------------------------------------------------------------------------------------------- |
|  1-3  | No automatic animations. CSS `:hover` and `:active` only.                                                       |
|  4-7  | Enumerate transition properties, usually `transform`, `opacity`, `background-color`, `border-color`, `box-shadow`. `animation-delay` cascades. |
| 8-10  | Complex scroll-triggered reveals. Framer Motion hooks. NEVER `window.addEventListener('scroll')`.               |

---

Never use `transition-all` as a default in Tailwind or CSS all-property transitions. Enumerate the properties so layout, width, height, and color changes do not animate accidentally.

## CSS-Only Patterns (Level 4-7)

### Staggered Reveal
```css
.reveal-item {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeUp 0.6s ease forwards;
  animation-delay: calc(var(--index) * 100ms);
}

@keyframes fadeUp {
  to { opacity: 1; transform: translateY(0); }
}
```

### Hover Lift
```css
.card {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.3s ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px -15px rgba(0,0,0,0.1);
}
```

### Active Press
```css
.button:active {
  transform: translateY(1px) scale(0.98);
}
```

---

## Framer Motion Patterns (Level 6+)

### Spring Physics (mandatory for interactive elements)
```tsx
// Premium, weighty feel — no linear easing
const spring = { type: "spring", stiffness: 100, damping: 20 };
```

### Stagger Children
```tsx
// Parent + Children MUST be in the same Client Component tree
const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
};
const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
};
```

### Layout Animations
```tsx
// Smooth re-ordering / resizing
<motion.div layout layoutId="unique-id" />
```

### Magnetic Hover (Level 8+)
**CRITICAL**: NEVER use `useState` for magnetic hover. Use EXCLUSIVELY:
```tsx
const x = useMotionValue(0);
const y = useMotionValue(0);
// No re-renders. Pure motion outside React cycle.
```

---

## Pointer-Proximity Motion — Icon Chips, Magnetic, Dock (Level 6+)

2026-trend surface: floating icon-chip clusters that respond to the cursor —
magnetic pull, dock-style magnification, proximity glow. Chip-as-content
composition is Tier-2 observed (aside.com, 2026-07-07); the motion patterns
below are Tier-1 pattern-survey synthesis — see
the 2026-07-07 practitioner research snapshot. Use for
landing/expressive surfaces only (Domain Gates above); never inside
repeated-work tools.

Rules (FE-PROXIMITY-01, DEFAULT):

- **One listener, shared state.** Track `pointermove` once per cluster (or
  once on the section), write normalized cursor position into CSS variables
  inside a single rAF; chips consume the variables. Never N per-chip
  listeners.
- **Gate the capability**: wrap in `@media (hover: hover) and (pointer:
  fine)`; touch devices get the static layout (or a scroll-driven
  equivalent), not a broken hover sim.
- **Reduced motion**: proximity displacement counts as non-essential motion;
  under `prefers-reduced-motion: reduce`, chips stay static (opacity/color
  feedback only).
- Transform/opacity only, as everywhere else. Displacement caps keep text
  legible: magnetic pull <= 8-12px for buttons, dock scale <= 1.3-1.5.

```js
// Shared cluster loop: one pointermove -> CSS vars -> chips derive their own motion
const cluster = document.querySelector('.chip-cluster');
let px = 0, py = 0, raf = 0;
cluster.addEventListener('pointermove', (e) => {
  px = e.clientX; py = e.clientY;
  raf ||= requestAnimationFrame(() => {
    raf = 0;
    const r = cluster.getBoundingClientRect();
    cluster.style.setProperty('--mx', `${px - r.left}px`);
    cluster.style.setProperty('--my', `${py - r.top}px`);
  });
});
cluster.addEventListener('pointerleave', () => {
  cluster.style.setProperty('--mx', '-9999px'); // chips ease back to rest
});
```

- **Magnetic chip**: displacement = (cursor - chip center) x strength
  (0.2-0.5), eased back on leave via a `transform` transition or spring.
- **Dock magnification**: per-chip `scale = 1 + k * max(0, 1 -
  distance/influenceRadius)` with `transform-origin: bottom`; a
  linear/gaussian falloff over ~2-3 neighbor chips reads as macOS Dock.
  Reserve real dock behavior for playful/creative surfaces.
- With Framer Motion, keep this in `useMotionValue` + `useTransform` (no
  re-renders), same as Magnetic Hover above.

---

Continue: [`motion-scroll.md`](motion-scroll.md).
