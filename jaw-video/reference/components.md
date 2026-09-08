# Component Library — Detailed Reference

## Surface Card System (Phase 20)

All content slides wrap their inner content in a **glassmorphism surface card**:
- `backdrop-filter: blur(N px)` — frosted glass
- Semi-transparent background (`rgba(15,23,42,0.65)` default)
- Subtle accent border + box shadow
- Customizable via `meta.theme.card` (`background`, `border`, `shadow`, `blur`, `borderRadius`)

## Animation System (Phase 21)

Each element accepts an optional `animation` config:
```json
{ "animation": { "enter": "scale-in", "exit": "fade-out" } }
```

Supported enter: `scale-in`, `fade-in`, `slide-up`, `none`
Supported exit: `scale-out`, `slide-down`, `fade-out`, `none`

Powered by `useEntranceAnimation()` hook — spring-based, auto-calculated from frame/durationInFrames.

## Transition Types (Phase 22)

| Type         | Options                                                   |
| ------------ | --------------------------------------------------------- |
| `fade`       | —                                                         |
| `slide`      | `direction`: from-left, from-right, from-top, from-bottom |
| `wipe`       | `direction`: from-left, from-right, from-top, from-bottom |
| `flip`       | `direction`: from-left, from-right                        |
| `clock-wipe` | —                                                         |

Optional `timing: "spring"` for spring-based transition timing.

## Korean Font Support (Phase 20.5)

NotoSansKR loaded as body font primary. Korean text renders natively without fallback issues.
Font stack: `NotoSansKR, Outfit, sans-serif` (body), `ChakraPetch, NotoSansKR, sans-serif` (display).

## Data Visualization (Phase 26)

`ChartSlide` supports 3 chart types — all pure SVG, no external library:
- **bar**: Staggered grow-up animation per bar
- **pie**: Sweep animation (strokeDashoffset)
- **line**: Draw-on animation with dots

```json
{
  "type": "chart",
  "props": {
    "chartType": "bar",
    "title": "Revenue by Quarter",
    "data": {
      "labels": ["Q1", "Q2", "Q3", "Q4"],
      "datasets": [{ "label": "Revenue", "data": [120, 250, 180, 320] }]
    }
  }
}
```

## Audio Features (Phase 25)

Timeline `audio[]` entries support:
- `fadeInSec` / `fadeOutSec` — volume ramp
- `loop: true` — loop audio
- `trimStartSec` — skip N seconds from start

## Project Source Structure

```
remotion-project/src/
├── index.ts                  ← registerRoot
├── Root.tsx                  ← Composition registry
├── config.ts                 ← feature flags + timing utils
├── presets.ts                ← TS presets
├── theme.ts                  ← Theme resolver + defaults
├── fonts.ts                  ← Font loading (Korean + Latin)
├── components/               ← 11 slide components + barrel
│   ├── TitleSlide.tsx
│   ├── ContentSlide.tsx
│   ├── CodeSlide.tsx
│   ├── DiagramSlide.tsx
│   ├── StatSlide.tsx          ← Phase 23: count-up KPIs
│   ├── QuoteSlide.tsx         ← Phase 23: quote display
│   ├── ComparisonSlide.tsx    ← Phase 23: side-by-side
│   ├── VideoSlide.tsx         ← Phase 24: inline video
│   ├── GifSlide.tsx           ← Phase 24: animated gifs
│   ├── LottieSlide.tsx        ← Phase 24: Lottie animation
│   ├── ChartSlide.tsx         ← Phase 26: bar/pie/line charts
│   ├── useAnimation.ts        ← Phase 21: entrance/exit hook
│   ├── Caption.tsx
│   └── index.ts              ← barrel export
└── timeline/                 ← JSON→React engine
    ├── schema.ts             ← types + validation + VoiceControl
    ├── element-router.tsx    ← type→component mapping (12 types)
    ├── renderer.tsx          ← JSON→TransitionSeries (5 transitions)
    └── loader.ts             ← JSON file loader
```
