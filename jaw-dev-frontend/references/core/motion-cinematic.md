# Cinematic Motion Patterns

Companion to [`motion.md`](motion.md) and [`motion-scroll.md`](motion-scroll.md). This file owns section-to-section choreography and its mobile, accessibility, and reduced-motion gates. Continue to [`motion-media.md`](motion-media.md) for generated motion assets and final performance checks.

## Cinematic Section Transitions (Level 8+, or Level 5+ when needed to satisfy the FE-MOTION-BUCKET-01 landing floor)

Full-screen "flying" transitions where one section transforms into the next:
zoom-through, fly-through, morph, wipe, portal. Research:
the 2026-07-08 cinematic-transition research snapshot.

Domain gate: landing, campaign, editorial, and product-story surfaces only.
Never apply cinematic section transitions to tools, dashboards, admin, auth,
payment, or developer consoles — they hijack scroll, delay task work, and raise
motion-sickness and accessibility risk. Motion intensity here is Level 8+, or
Level 5+ when needed to satisfy the FE-MOTION-BUCKET-01 landing floor; do not
ship it on repeated-work surfaces.

All of these share one architecture: a **pinned full-viewport stage**, layered
sections/images, and scroll progress mapped to a timeline. Choose the driver by
job:

- **GSAP ScrollTrigger** — continuous cinematic scenes (`pin`, `scrub`, `snap`, timelines).
- **CSS scroll-driven animations** — simple fades, wipes, progress-linked transforms.
- **View Transitions API** — discrete click/state/route morphs, not scroll scrubbing.
- **Canvas/WebGL** — only when product fidelity needs image sequences or shaders.

| Pattern | CSS or JS | Best Use | Tradeoff |
| --- | --- | --- | --- |
| Zoom-through | JS (CSS for simple scale) | Enter next scene "through" an element | Giant raster layers eat memory; cap scale + asset size on mobile |
| 3D perspective fly-through | JS | Panels flying toward/away from viewer | Many composited layers; flatten finished layers, test memory |
| Crossfade / morph | CSS or JS | Soft scene change between full-viewport sections | Cheapest; watch mid-fade text contrast |
| Card-to-fullscreen expand | JS (View Transitions / FLIP) | Thumbnail or card opens into detail | Never animate layout directly; use FLIP/View Transitions |
| Wipe / reveal | CSS or JS | One section slides/wipes to reveal next | `clip-path`/mask can repaint; translated cover is fastest |
| Tunnel / portal | JS | Zoom through a shape that opens into next content | Masked shape can be unreadable on narrow screens |
| Scale + opacity depth | CSS or JS | Safe high-end depth illusion | Compositor-friendly; tune scale lower on mobile |
| View Transitions morph | JS trigger + CSS | Discrete section/state morph | Snapshot-based; not continuous scroll progress |
| GSAP pinned timeline | JS | Master timeline sequencing multiple scenes | Pin is heavy on mobile Safari; simplify via `matchMedia` |

### Zoom-through / portal

Pin a stage, scale a foreground element up (8-30x) so the next scene reveals
behind or through it. Transform and opacity only.

```js
gsap.timeline({
  scrollTrigger: { trigger: '.stage', pin: true, scrub: true, end: '+=200%' },
})
  .to('.portal', { scale: 18, ease: 'none' })
  .to('.next-scene', { opacity: 1 }, '<');
```

CSS-only portal via a growing circle mask (no next-scene replacement, simpler):

```css
.portal {
  clip-path: circle(var(--r, 8%) at 50% 50%);
  animation: open linear both;
  animation-timeline: scroll(root block);
  animation-range: 20% 70%;
}
@keyframes open { to { --r: 140%; } }
```

### 3D perspective fly-through

```css
.stage { perspective: 1200px; transform-style: preserve-3d; }
.panel { will-change: transform, opacity; }
```

```js
gsap.to('.panel', {
  z: 600, rotationX: -12, autoAlpha: 0, stagger: 0.15,
  scrollTrigger: { trigger: '.stage', pin: true, scrub: true },
});
```

Cap travel distance and rotation on small screens; perspective reads stronger
on mobile and can trigger motion sickness.

### Crossfade / scale-depth morph

The safest high-end look: previous section scales down and fades, next scales
from slightly larger to rest. Compositor-friendly.

```css
.scene { position: sticky; top: 0; height: 100dvh; }
.scene--out { animation: sink linear both; animation-timeline: view(); animation-range: exit 0% exit 100%; }
@keyframes sink { to { opacity: 0; transform: scale(0.92); } }
```

On mobile, tune the incoming scale toward `1.04 -> 1` (not `1.08`) to reduce
motion sickness.

### Wipe / reveal

```css
.next { clip-path: inset(0 0 100% 0); animation: wipe linear both; animation-timeline: view(); }
@keyframes wipe { to { clip-path: inset(0 0 0 0); } }
```

A translated cover panel (transform only) is cheaper than `clip-path` on
low-power devices; prefer it when the wipe is a straight edge.

### Card-to-fullscreen (View Transitions)

Discrete, click-driven morph — not scroll. Match old/new with a shared name.

```js
card.style.viewTransitionName = 'hero-media';
document.startViewTransition(() => openDetailView());
```

```css
::view-transition-old(hero-media),
::view-transition-new(hero-media) { animation-duration: 0.4s; }
```

Provide a fallback for unsupported browsers, preserve focus, and land the
expansion into a scrollable detail view on mobile with working back gesture.

### GSAP pinned master timeline

Build the timeline first, then attach one ScrollTrigger. One pinned master
timeline beats many competing triggers.

```js
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '.story', start: 'top top', end: '+=400%',
    pin: true, scrub: 1, snap: 1 / (scenes - 1),
  },
});
tl.addLabel('s1').to('.s1', { autoAlpha: 0 })
  .addLabel('s2').fromTo('.s2', { scale: 1.08, autoAlpha: 0 }, { scale: 1, autoAlpha: 1 }, '<');
```

### Mobile + reduced motion (mandatory)

- Gate pinned/zoom scenes with `ScrollTrigger.matchMedia()` or a CSS media
  query; on small screens replace with stacked sections or a native swipe rail.
- Serve smaller media variants and fewer/lower-res frames on mobile; giant
  raster zoom layers crash memory.
- Under `prefers-reduced-motion: reduce`, disable zoom/fly/portal entirely:
  render a static poster or a plain crossfade, and never pin scroll.

```js
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!reduce) { /* build cinematic timeline */ }
```

Animate `transform` and `opacity` as the default vocabulary; layout/paint
properties are hard to keep smooth under a pinned, scrubbed timeline.

---

## Soft-Focus Organic Background + Capsule Label (Level 5+)

The OpenAI-announcement-card grammar: an expressive soft-focus organic field
with an opaque capsule label floating above (see aesthetics.md § Expressive vs
Functional Layers). Prefer a REAL soft-focus photographic or generated image
for the background; the pure-CSS fallback:

```css
.card {
  position: relative; overflow: hidden; border-radius: 28px;
  background:
    radial-gradient(circle at 25% 20%, #d8efd5 0, transparent 34%),
    radial-gradient(circle at 75% 35%, #c8dfd8 0, transparent 38%),
    radial-gradient(circle at 45% 80%, #f2d9c8 0, transparent 42%);
}
.card::before { content:""; position:absolute; inset:-40px; background:inherit;
  filter: blur(32px) saturate(1.05); transform: scale(1.08); }
.card::after  { content:""; position:absolute; inset:0; pointer-events:none;
  opacity:.18; mix-blend-mode:multiply;
  /* grain: noise image or SVG feTurbulence filter */ }
.pill { display:inline-flex; align-items:center; border-radius:999px;
  background:#fff; color:#000; padding:.35em .85em; font-weight:800; }
```

Rules: the capsule is opaque (not glass); one organic field per viewport
(gradient budget applies); grain at low opacity (.1-.2); animate only
transform/opacity on the field (slow drift), never the blur radius.
Counts toward the ambient-gradient budget — a real image is exempt.

## Product-Led Hero Motion (Level 6+)

Motion combos for product-as-stage heroes (see layout-discipline.md § Hero
Composition Grammar):

- **Parallax layered product scene**: product/device foreground moves slower
  or opposite to the background field; 2-3 layers max, transform-only.
- **Scroll-driven product rotation**: 3D or frame-sequence rotation of the
  product mapped to scroll progress (see Frame Sequence Scrolltelling above);
  keep the interactive scene full-bleed, not boxed in a card.
- **Video-in-mockup**: an autoplaying muted product-UI loop inside a device
  frame; lazy-load, `playsinline muted loop`, poster fallback, pause offscreen
  via IntersectionObserver.
- All three: static first-frame fallback under `prefers-reduced-motion`.

## Scroll Pattern Decision Tree

```text
Need a scroll effect?
  |
  +-- Product tool, dashboard, admin, auth, payment?
  |     -> scroll-driven = 0 (hard, FE-MOTION-BUCKET-01); feedback-only motion allowed.
  |
  +-- Cards/gallery need horizontal browsing?
  |     -> Native rail + CSS Scroll Snap.
  |
  +-- Full-page slide deck or presentation?
  |     -> CSS scroll-snap y mandatory; reduce to proximity when needed.
  |
  +-- Simple reveal, progress, or parallax?
  |     -> CSS scroll-driven animation + @supports fallback.
  |
  +-- Pinned horizontal campaign story?
  |     -> GSAP ScrollTrigger pin + scrub, isolated from UI component motion.
  |
  +-- Cinematic full-screen transition (zoom-through, fly, portal, morph)?
  |     -> Pinned stage + timeline: GSAP ScrollTrigger for continuous scenes,
  |        CSS scroll-driven for simple fade/wipe. Landing/campaign only.
  |
  +-- Discrete section/card-to-detail morph on click?
  |     -> View Transitions API (view-transition-name), not scroll scrubbing.
  |
  +-- Product-grade frame-by-frame object motion?
  |     -> Canvas + Image sequence + progressive loading.
  |
  +-- Layered narrative cards?
  |     -> Sticky Card Stacking.
  |
  +-- Text-as-window, mask, or kinetic type?
  |     -> Text Mask & Reveal, with semantic text preserved.
  |
  +-- Route/timeline drawing?
  |     -> SVG Path Drawing with precomputed path length.
  |
  +-- Vector animation scrub?
  |     -> Lottie + ScrollTrigger goToAndStop.
  |
  +-- Simple video scrub?
        -> video.currentTime only when frame precision is not required.
```

Default fallback: content visible, controls reachable, no scroll hijack. Under
`prefers-reduced-motion`, every branch resolves to static content, native
scroll, proximity snap, or user-controlled playback.

---

## Frame Sequence Format Guide

| Format | Use For | Avoid When |
| --- | --- | --- |
| WebP | Default canvas frame sequences; broad support and fast decode | You need the absolute smallest possible bytes |
| AVIF | Static posters, `<picture>` primary source, bandwidth-sensitive art direction | Decode cost or tooling slows scroll responsiveness |
| JPEG | Legacy/simple fallback and easy production pipelines | Alpha, modern compression, or large frame counts matter |

Rules:

- Canvas sequences: prefer WebP frames, sized separately for desktop/mobile.
- Static posters: use `<picture>` with AVIF first and WebP fallback.
- Long sequences: prioritize frame count, dimensions, and preload order before
  chasing marginal compression gains.
- Do not ship hundreds of full-resolution frames without an IntersectionObserver
  preload gate and checkpoint-first loading.
- Reduced motion: poster image beats loading an entire sequence the user will
  not see.

---
