# Motion Media, Performance, and Honesty

Final companion to [`motion.md`](motion.md), [`motion-scroll.md`](motion-scroll.md), and [`motion-cinematic.md`](motion-cinematic.md). This file owns generated video workflows, format selection, runtime budgets, reduced-motion behavior, and verification that implementation matches the declared motion dial.

## ima2 Video Pipeline for Motion Assets (FE-MOTION-VIDEO-01, DEFAULT)

When a motion surface needs real video or animated content, use ima2's video
pipeline instead of simulating motion with CSS transitions alone. Domain gates
from FE-MOTION-BUCKET-01 still apply — video assets serve the LANDING and APP
buckets; TOOL bucket surfaces use static assets with feedback-only transitions.

### Image-First Video (highest quality)

The best video output comes from generating a high-quality still first, then
animating it via image-to-video (i2v). The video model has a concrete visual
anchor, producing better composition and character consistency than text-to-video.

```bash
# Step 1: Generate keyframe with GPT Image 2 (primary provider)
# Match aspect ratio to target video: 1792x1024 for 16:9, 1024x1024 for 1:1
ima2 gen "cinematic product shot of wireless earbuds on granite, three-point lighting, 16:9" \
  --quality high --size 1792x1024 -o keyframe.png

# Step 2: Animate the keyframe via i2v
ima2 video "camera slowly orbits the product, soft ambient hum, no music, \
  hold on a centered medium shot at the end" \
  --ref keyframe.png --duration 10 --resolution 720p --aspect-ratio 16:9
```

**Keyframe provider rule:** GPT Image 2 (`--provider oauth`, `--quality high`)
produces superior keyframes. Grok (`--provider grok`) is the fallback — only
aspect ratio must match because i2v internally rescales.

### Storyboard-to-Video Chain (multi-beat sequences)

For sequences longer than 15 seconds or needing precise beat control, use the
9-panel storyboard workflow:

```bash
# Step 1: Generate opening keyframe
ima2 gen "cinematic wide shot, dramatic lighting" --quality high --size 1024x1024 -o keyframe.png

# Step 2: Generate 9-panel storyboard grid from keyframe
ima2 gen "Using this scene as reference, create a 3x3 storyboard grid (9 panels, \
  thin black borders). Panel 1: solid black (lead-in). Panel 2-9: sequential action \
  beats with timestamps. Maintain character design across panels." \
  --ref keyframe.png --quality high --size 1024x1024 -o storyboard.png

# Step 3: Animate storyboard
ima2 video "This is a 9-panel storyboard. Animate left-to-right, top-to-bottom. \
  Panel 1: black fade-in. Panel 2: ... Sound: taiko percussion builds. \
  Camera: wide establishing then push to medium. End frame: stable close-up." \
  --ref storyboard.png --duration 15 --resolution 720p --model grok-imagine-video-1.5

# Step 4: Extract last frame and chain next storyboard
ima2 video frame <generated-file>.mp4 --last -o lastframe.png
ima2 gen "Using this last frame, create next 9-panel storyboard..." \
  --ref lastframe.png --quality high --size 1024x1024
```

**9-panel rules:** Panel 1 must be solid black (auto-trimmed lead-in). Square
format (1024x1024) works best. No timestamp labels in panels — they burn into
the video. Character design must be identical across all panels.

### Video Continue and Extend

For multi-shot connected sequences:

```bash
# Extend from last frame (xAI native, combines original + extension)
ima2 video extend "camera slowly pulls back revealing the full scene" \
  --video <generated-file>.mp4 --duration 6

# Continue with lineage (new clip, carries revisedPrompt history)
ima2 video continue "she turns toward camera, rain grows louder, no music, \
  says 'gidarryeo', end on still close-up" \
  --video <generated-file>.mp4 --duration 10
```

`extend` returns original + extension as one file. `continue` creates a new
clip from the last frame with branch-local prompt lineage (up to 4 entries).

### Video Prompt Writing Rules

Video prompts must be ACTIVE — describe motion, not a static description.
Every video prompt should include:

| Element | Required | Example |
|---------|----------|---------|
| Opening frame | Yes | "tight macro on the brushed aluminum edge" |
| Camera intent | Yes | "lateral glide", "orbit", "rack focus" |
| Subject motion | Yes | "earbuds slowly rotate, light catches the stem" |
| Sound/music | Yes | "ambient hum, no music" or "lo-fi piano builds" |
| Dialogue | If needed | "speaker says 'welcome', then silence" |
| Ending frame | Yes | "settles into centered medium shot, holds steady" |
| Duration pacing | Yes | 1-4s: one action. 5-7s: setup/turn/hold. 8-15s: multi-beat arc |

**Anti-slop:** reject "cinematic", "stunning", "AAA trailer", generic "neon glow".
Write what the camera actually sees and hears.

### Model and Resolution by Motion Surface

| Motion Surface | Model | Resolution | Duration |
|---------------|-------|-----------|----------|
| Product reveal | `grok-imagine-video-1.5` | 1080p | 5-10s |
| Hero background loop | `grok-imagine-video` | 720p | 5-10s |
| Scroll-driven frame sequence | Generate video, extract frames with ffmpeg | 720p+ | 5-15s |
| Social/marketing clip | `grok-imagine-video-1.5` | 1080p | 5-15s |
| Quick draft / iteration | `grok-imagine-video` | 480p | 3-5s |

### Frame Extraction for Scroll Sequences

To create scroll-driven frame sequences from ima2 video:

```bash
# Generate the motion asset
ima2 video "product slowly rotates 360 degrees on clean backdrop" \
  --ref product.png --duration 10 --resolution 1080p -o motion.mp4

# Extract WebP frames for canvas scroll scrub
ffmpeg -i motion.mp4 -vf "fps=24,scale=1440:-1" frames/%04d.webp

# Or extract specific keyframes
ima2 video frame motion.mp4 --last -o lastframe.png
```

Then use the Frame Sequence Scrolltelling pattern from this document with
the extracted frames.

### Parallel Video Generation

Video generation is slow (30-120s per clip). For multi-shot sequences, launch
clips in parallel when they do not depend on each other:

```bash
# Independent shots can run concurrently
ima2 video "wide establishing shot" --ref scene.png --duration 5 &
ima2 video "close-up detail shot" --ref detail.png --duration 5 &

# Monitor progress
ima2 ps --json

# Sequential shots (each needs the previous last frame) must be serial
```

### `$imagegen` Fallback — Motion Without Video

When ima2 is unavailable, `$imagegen` cannot generate video. Degrade to:

1. **Static keyframe + CSS animation:** Generate a high-quality still with
   `$imagegen`, then apply CSS transforms (parallax, scale, fade) for motion.
2. **Multi-still frame sequence:** Generate 3-5 stills at different angles or
   states with `$imagegen`, use CSS scroll-driven animations to crossfade.
3. **CSS-only motion:** Use the CSS patterns in this document (scroll-driven
   animations, sticky card stacking, text reveals) without bitmap frames.

The quality gap is significant — video > multi-still > CSS-only. Document the
gap in the deliverable when using fallback motion.

---

## Performance Rules

1. Animate ONLY `transform` and `opacity`. Never `top`, `left`, `width`, `height`.
2. `will-change: transform` sparingly. Remove after animation completes.
3. Grain/noise filters → fixed `pointer-events-none` pseudo-elements only.
4. Perpetual/infinite animations MUST be `React.memo`'d and isolated in microscopic Client Components.
5. Wrap dynamic lists in `<AnimatePresence>`.
6. 60fps target. Profile on mobile before shipping.

---

## Creative Arsenal (Inspiration)

Pick from these for signature moments — don't use all of them:

| Category       | Concepts                                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------ |
| **Navigation** | Mac OS Dock magnification, Magnetic buttons, Gooey menu, Dynamic Island                          |
| **Cards**      | Parallax tilt (3D on mouse), Spotlight border, Holographic foil hover                            |
| **Scroll**     | Sticky scroll stack, Horizontal scroll hijack, Zoom parallax, SVG path drawing                   |
| **Text**       | Kinetic marquee, Text mask reveal (type as window to video), Text scramble (Matrix decode)       |
| **Micro**      | Particle explosion button, Directional hover fill, Ripple click effect, Mesh gradient background |

---

## `prefers-reduced-motion` (Mandatory)

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Always include. No exceptions.

CSS overrides alone are NOT enough for JS-driven scroll effects. When
`prefers-reduced-motion: reduce` is set, the script must SHORT-CIRCUIT setup:
skip building frame arrays, skip binding scroll/resize listeners, skip the
update loop, and render a static, readable end state instead (all reveal text
lit, a representative canvas frame drawn, the first caption shown). A CSS
`animation-duration: 0.01ms` override still lets the JS build hundreds of
offscreen frames and run a scroll handler every frame — wasteful and still
motion under user control.

```js
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
if (reduce) {
  drawStaticFrame();          // one representative frame, not the whole sequence
  revealAll();                // reveal copy, show first caption
  return;                     // bind no listeners, run no update loop
}
buildFrames();
addEventListener('scroll', onScroll, { passive: true });
```

Provenance: scroll-effect and cinematic-transition research reviewed on
2026-07-08; refresh browser support and product examples before current claims.

---

## Motion Honesty (FE-MOTION-HONESTY-01, DEFAULT)

Source: taste-skill v2 (62k stars), adapted for this skill family.

The declared MOTION_INTENSITY dial must match the shipped page's actual motion.
A dial value above 4 that ships a static page is a lie — the motion was claimed
but never delivered.

| Dial | Required motion evidence |
|------|------------------------|
| 1-3 | Hover and active state transitions only. No scroll-driven motion required. |
| 4-5 | At least one entrance animation or staggered load-in visible on first scroll. |
| 6-7 | Scroll-driven reveals on multiple sections + at least one signature moment. |
| 8-10 | Choreographed scroll timeline or parallax + signature moment + supporting reveals. |

Verification: scroll the built page top-to-bottom and count distinct motion events.
If the count does not match the dial band, either lower the dial or add the motion.

Honesty has a second dimension: motion must carry a semantic verb, not merely
raise the event count. A repeated verb is communicative when the same action
explains brand or product state across loader, navigation, and content—for
example Cobloc assembling identity, SSTR translating telemetry into loader
grammar, or Interfere demonstrating issue resolution. Generic decorative
entrances remain disallowed as a governing system. This does not remove the
level 4-5 requirement for at least one entrance animation or staggered load-in;
that required entrance must be restrained, while the repeated system earns its
place by communicating state.

Any MOTION_INTENSITY > 3 MUST honor `prefers-reduced-motion`: reduce to hover/active
only. This is not optional at any dial level.
