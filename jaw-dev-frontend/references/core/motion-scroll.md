# Scroll-Linked Motion Patterns

Companion to [`motion.md`](motion.md). This file owns scroll progress, horizontal stages, sticky stacks, frame/video scrub, page transitions, text/SVG/Lottie reveals, and their fallbacks.

## Scroll-Driven (Level 8+, or Level 5+ when needed to satisfy the FE-MOTION-BUCKET-01 landing floor)

### Scroll Progress
```tsx
const { scrollYProgress } = useScroll();
const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
```

### CSS Scroll-Driven Animations (preferred for reveal/progress)

The CSS scroll-driven animations module (MDN, verified 2026-07-07) animates
along scroll progress on the compositor — it replaces scroll-listener JS
(and most `useScroll` cases) for reveals, progress bars, and parallax:

```css
/* Progress bar tied to document scroll */
.progress { animation: grow linear; animation-timeline: scroll(root block); }
@keyframes grow { from { scale: 0 1; } to { scale: 1 1; } }

/* Reveal tied to the element's own viewport entry */
.reveal-item {
  animation: fadeUp linear both;
  animation-timeline: view();
  animation-range: entry 0% cover 35%;
}
```

- Key surface: `animation-timeline: scroll(<scroller> <axis>)` / `view(<axis>
  <inset>)`, `animation-range(-start/-end)`, `scroll-timeline-*`,
  `view-timeline-*`, `timeline-scope`; JS `ScrollTimeline`/`ViewTimeline`.
- Support caveat: verify current engine support before shipping
  (Firefox landed late); provide non-animated final states as fallback
  (`both` fill + content visible without the animation).
- Browser support snapshot (Can I Use, 2026-07 research): 83.66%
  global usage; Chrome/Edge 115+, Safari/iOS Safari 26+, Firefox 155
  partial/subfeature support. Treat as progressive enhancement.
- Use `@supports` around scroll timelines and keep the base state usable:

```css
.reveal { opacity: 1; transform: none; }

@supports (animation-timeline: view()) {
  .reveal {
    opacity: 0;
    transform: translateY(16px);
    animation: fadeUp linear both;
    animation-timeline: view();
    animation-range: entry 15% cover 40%;
  }
}
```

- Scroll-linked icon-chip choreography (chips drifting/parallaxing at
  different rates while scrolling) = `view()` timelines with per-chip
  `animation-range` offsets — no JS.

### View Transitions API
```tsx
document.startViewTransition(() => {
  // DOM update
});
```

### Horizontal Scroll-in-Vertical (Level 8+, or Level 5+ when needed to satisfy the FE-MOTION-BUCKET-01 landing floor)

Domain gate: landing/campaign/editorial scrolltelling only. For tools,
dashboards, admin, ops, and developer consoles, prefer a normal table/list or a
native rail; never hijack vertical scroll for repeated work.

| Technique | Best Use | Tradeoff |
| --- | --- | --- |
| Native rail + CSS Scroll Snap | Cards, galleries, product shelves | Most accessible; needs visible affordance on desktop |
| Sticky + `translateX` | One-off story sections | Must manage focus, resize, and reduced motion |
| GSAP ScrollTrigger pin | Campaign-grade timeline choreography | Dependency cost; isolate from Framer component trees |
| CSS scroll-driven | Progressive-enhanced horizontal motion | Browser support requires `@supports` fallback |

Native rail + CSS Scroll Snap:

```css
.rail {
  display: flex;
  gap: 24px;
  overflow-x: auto;
  overscroll-behavior-inline: contain;
  scroll-snap-type: x mandatory;
}

.rail-card {
  flex: 0 0 min(82vw, 420px);
  scroll-snap-align: start;
}
```

Sticky + `translateX`:

```css
.h-section { height: calc(100dvh + var(--travel)); }
.h-sticky { position: sticky; top: 0; height: 100dvh; overflow: hidden; }
.h-track { display: flex; will-change: transform; }
.h-panel { flex: 0 0 100vw; }
```

```js
const section = document.querySelector('.h-section');
const track = document.querySelector('.h-track');
let raf = 0;

function updateHorizontal() {
  raf = 0;
  const rect = section.getBoundingClientRect();
  const travel = section.offsetHeight - innerHeight;
  const max = track.scrollWidth - innerWidth;
  const progress = Math.min(1, Math.max(0, -rect.top / travel));
  track.style.transform = `translateX(${-max * progress}px)`;
}

addEventListener('scroll', () => {
  raf ||= requestAnimationFrame(updateHorizontal);
}, { passive: true });
```

GSAP ScrollTrigger pin:

```js
gsap.to('.h-track', {
  xPercent: -100 * (panels.length - 1),
  ease: 'none',
  scrollTrigger: {
    trigger: '.h-wrap',
    pin: true,
    scrub: 1,
    snap: 1 / (panels.length - 1),
    end: () => `+=${document.querySelector('.h-track').offsetWidth}`,
  },
});
```

CSS scroll-driven enhancement:

```css
.h-track { transform: none; }

@supports (animation-timeline: scroll()) {
  .h-track {
    animation: move-x linear both;
    animation-timeline: scroll(root block);
  }

  @keyframes move-x {
    to { transform: translateX(calc(-100% + 100vw)); }
  }
}
```

Reduced motion: keep the native rail scrollable, collapse fake-horizontal
sections to a vertical stack, disable pin/scrub timelines, and make all panels
reachable in document order.

### Sticky Card Stacking (Level 7+, or Level 5+ when needed to satisfy the FE-MOTION-BUCKET-01 landing floor)

Domain gate: landing, editorial, case studies, education, onboarding. In tools,
use it only for non-blocking summaries; never stack forms, tables, or required
workflow controls.

```css
.stack {
  position: relative;
  display: grid;
  gap: 24px;
}

.stack-card {
  position: sticky;
  top: calc(24px + (var(--i) * 18px));
  transform-origin: top center;
  z-index: var(--i);
}
```

```html
<section class="stack">
  <article class="stack-card" style="--i: 1">...</article>
  <article class="stack-card" style="--i: 2">...</article>
  <article class="stack-card" style="--i: 3">...</article>
</section>
```

Reduced motion: keep sticky positioning if it only affects placement; remove
scale/rotation/fade flourishes and ensure each card remains readable when
stacked.

### Frame Sequence Scrolltelling (Level 8+, or Level 5+ when needed to satisfy the FE-MOTION-BUCKET-01 landing floor)

Domain gate: product launches, campaign pages, editorial explainers, and
portfolio moments where photoreal inspection matters. Avoid in dashboards,
admin tools, auth, payments, and repeated workflows.

AI pipeline:

```text
ima2 gen "product scene" --quality high
  -> ima2 video "motion prompt" --ref image.png --duration 10 --resolution 1080p
  -> ffmpeg -i motion.mp4 -vf "fps=24,scale=1440:-1" frames/%04d.webp
  -> Canvas scroll scrub
```

Progressive loading strategy:

1. Load poster frame 0 first.
2. Load last frame, midpoint, then quarter checkpoints.
3. Fill gaps in idle time after the section is near the viewport.
4. Draw only when the frame index changes.
5. Use separate desktop/mobile sequences when canvas dimensions differ.

Image format: WebP is the default for canvas sequences because support is broad
and decode is fast. Use AVIF + WebP in `<picture>` for static posters or art
direction. Keep JPEG as a simple fallback only.

```js
const canvas = document.querySelector('canvas.sequence');
const ctx = canvas.getContext('2d');
const section = document.querySelector('.sequence-section');
const frameCount = 180;
const frames = Array.from({ length: frameCount }, (_, i) => {
  const img = new Image();
  img.src = `/frames/${String(i + 1).padStart(4, '0')}.webp`;
  return img;
});

let current = -1;
function drawFrame(index) {
  if (index === current || !frames[index]?.complete) return;
  current = index;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(frames[index], 0, 0, canvas.width, canvas.height);
}

function scrubSequence() {
  const rect = section.getBoundingClientRect();
  const travel = section.offsetHeight - innerHeight;
  const progress = Math.min(1, Math.max(0, -rect.top / travel));
  drawFrame(Math.round(progress * (frameCount - 1)));
}

addEventListener('scroll', () => requestAnimationFrame(scrubSequence), { passive: true });
```

Reduced motion: show a poster image or a short non-scrubbed clip with controls;
do not bind dozens or hundreds of frame changes to scroll.

### Video currentTime Scrub (Level 7+, or Level 5+ when needed to satisfy the FE-MOTION-BUCKET-01 landing floor)

Domain gate: lightweight landing/editorial effects where exact frame accuracy
does not matter. Use Canvas frame sequences for Apple-style product precision.

```js
const video = document.querySelector('.scrub-video');
const section = document.querySelector('.video-section');

function scrubVideo() {
  if (!video.duration) return;
  const rect = section.getBoundingClientRect();
  const progress = Math.min(1, Math.max(0, -rect.top / (section.offsetHeight - innerHeight)));
  video.currentTime = progress * video.duration;
}

addEventListener('scroll', () => requestAnimationFrame(scrubVideo), { passive: true });
```

Known limitations: `currentTime` seeks are not frame-perfect, mobile media
policies can delay readiness, decode can stutter, and long GOP videos scrub
poorly. Consider all-I-frame encoding only when the larger file size is
acceptable.

Reduced motion: let the user play/pause normally, show poster-first content,
and avoid automatic scroll-bound seeking.

### Slide/Page Transitions (Level 6+)

Domain gate: presentation-like landing pages, education modules, galleries, and
interactive stories. Avoid hard scroll snap in forms, docs, dashboards, and
long-reading content.

```css
.slides {
  height: 100dvh;
  overflow-y: auto;
  scroll-snap-type: y mandatory;
}

.slide {
  min-height: 100svh;
  scroll-snap-align: start;
  scroll-snap-stop: always;
}
```

Use View Transitions for discrete morphs between selected slides or route/state
changes, not continuous scroll progress. Use Sticky Card Stacking when the page
should keep natural document flow instead of full-page snapping.

Reduced motion: change `scroll-snap-type` to `y proximity` or remove snap, and
disable View Transition animations.

### Text Mask & Reveal (Level 8+, or Level 5+ when needed to satisfy the FE-MOTION-BUCKET-01 landing floor)

Domain gate: editorial, campaign, portfolio, and hero storytelling. In product
tools, use plain readable text and reserve reveal for small onboarding moments.

```css
.masked-copy {
  clip-path: inset(0 100% 0 0);
  animation: text-wipe linear both;
  animation-timeline: view();
  animation-range: entry 20% cover 45%;
}

@keyframes text-wipe {
  to { clip-path: inset(0 0 0 0); }
}
```

SVG mask over video:

```svg
<svg viewBox="0 0 1200 400" aria-hidden="true">
  <defs>
    <mask id="headline-mask">
      <text x="50%" y="55%" text-anchor="middle">LAUNCH</text>
    </mask>
  </defs>
  <foreignObject width="1200" height="400" mask="url(#headline-mask)">
    <video autoplay muted loop playsinline src="/motion.webm"></video>
  </foreignObject>
</svg>
```

Kinetic typography: split decorative layers only; keep one semantic text node
available to assistive tech and search. Animate transforms/opacity, not layout
properties.

Reduced motion: render final text immediately, keep video masks static or use a
poster, and do not scramble/split characters over time.

### SVG Path Drawing (Level 7+, or Level 5+ when needed to satisfy the FE-MOTION-BUCKET-01 landing floor)

Domain gate: routes, timelines, process maps, editorial diagrams, and playful
landing moments. Avoid it for dense operational diagrams where the path itself
is critical information.

```css
.route-path {
  stroke-dasharray: var(--path-length);
  stroke-dashoffset: var(--path-length);
  animation: draw-path linear both;
  animation-timeline: view();
  animation-range: entry 10% cover 60%;
}

@keyframes draw-path {
  to { stroke-dashoffset: 0; }
}
```

Set `--path-length` from `path.getTotalLength()` once at init, not on every
scroll frame.

Reduced motion: show the completed path immediately and use labels or markers
for meaning; never make comprehension depend on the drawing animation.

### Lottie Scroll Scrub (Level 7+, or Level 5+ when needed to satisfy the FE-MOTION-BUCKET-01 landing floor)

Domain gate: vector explainers, icons, onboarding, and editorial diagrams. Do
not use Lottie for photoreal product scrolltelling; use frame sequences instead.

```js
const anim = lottie.loadAnimation({
  container: document.querySelector('.lottie'),
  renderer: 'svg',
  loop: false,
  autoplay: false,
  path: '/motion.json',
});

ScrollTrigger.create({
  trigger: '.lottie-section',
  start: 'top bottom',
  end: 'bottom top',
  scrub: true,
  onUpdate: ({ progress }) => {
    anim.goToAndStop(progress * (anim.totalFrames - 1), true);
  },
});
```

Reduced motion: pause at the most informative frame, provide static SVG/PNG
fallback, and do not scrub vector motion in response to scroll.

**NEVER mix GSAP/Three.js with Framer Motion in the same component tree.**
Use Framer for UI. Use GSAP/Three.js ONLY for isolated full-page scrolltelling or canvas backgrounds, wrapped in strict `useEffect` cleanup blocks.

---
