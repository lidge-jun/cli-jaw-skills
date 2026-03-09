# Remotion Video Skill

Use this skill for any programmatic video task: create, render, preview, or review videos using Remotion.
Triggers: "video", "Remotion", "animation", "mp4", "render video", "slides to video".
Covers: JSON-driven timeline rendering, theme system, resolution presets, render pipeline, artifact validation.
Do NOT use for: live video editing, video download/conversion (use video-downloader), screen recording (use screen-capture), AI video generation (use sora).

---

## Quick Reference

| Task           | Command                                                                                              |
| -------------- | ---------------------------------------------------------------------------------------------------- |
| **Render**     | `node scripts/pipeline.mjs --timeline <path> [--preset Landscape-1080p]`                             |
| **Render+TTS** | `node scripts/pipeline.mjs --timeline timeline.draft.json` (auto-detects narration)                  |
| **Skip TTS**   | `node scripts/pipeline.mjs --timeline timeline.draft.json --skip-tts`                                |
| **TTS only**   | `node scripts/tts.mjs --batch timeline.draft.json [--provider supertone]`                            |
| **TTS single** | `node scripts/tts.mjs --text "Hello" --output /tmp/tts-out.m4a [--provider gemini]`                  |
| **TTS voices** | `node scripts/tts.mjs --list-voices [--provider supertone]`                                          |
| **Async**      | `node scripts/pipeline.mjs --timeline <path> --async`                                                |
| **Status**     | `node scripts/pipeline.mjs --status /tmp/remotion-render/render-result.json`                         |
| **Preview**    | `cd remotion-project && pnpm exec remotion studio` (browser UI)                                      |
| **Validate**   | `node scripts/validate-artifact.mjs /tmp/remotion-render/TimelineVideo.mp4 --preset Landscape-1080p` |

---

## Rendering Mode

### Mode 1: JSON-Driven (the only allowed mode)

Agent generates a `timeline.json` → pre-built template renders it.
No React coding required. Safe, predictable, fast.

```
Agent → timeline.json → Template components → pipeline.mjs → mp4
```

### Mode 2: Custom React (feature flag — NOT YET AVAILABLE)

Behind feature flag. Do not use.

---

## Pipeline Usage

```bash
# ⚠️  Output MUST go outside skills_ref/ — default is /tmp/remotion-render
# NEVER use --output ./out (pollutes source code)

# Sync (default) — blocks until render complete
node skills_ref/video/scripts/pipeline.mjs \
  --timeline timeline.json \
  --output /tmp/remotion-render

# With preset override (timeline.meta.preset is the source of truth)
node skills_ref/video/scripts/pipeline.mjs \
  --timeline timeline.json \
  --preset Portrait-1080p

# Async — returns immediately, renders in background
node skills_ref/video/scripts/pipeline.mjs \
  --timeline timeline.json \
  --async
# → {"status":"rendering","pid":12345,"logPath":"/tmp/remotion-render/render.log","outputPath":"/tmp/remotion-render/TimelineVideo.mp4"}

# Check async status
node skills_ref/video/scripts/pipeline.mjs \
  --status /tmp/remotion-render/render-result.json
```

### Preset SOT Rule

`timeline.meta.preset` is the **source of truth** for resolution.
CLI `--preset` is an **override** — it warns when different from timeline.

---

## Timeline Authoring

See [timeline-schema.md](../devlog/_plan/260308_remotion_video_pipeline/video/timeline-schema.md) for full TypeScript interface.

### Minimal Example

```json
{
  "meta": {
    "title": "My Video",
    "preset": "Landscape-1080p",
    "fps": 30,
    "totalDurationSec": 15
  },
  "elements": [
    {
      "type": "title",
      "startSec": 0,
      "durationSec": 5,
      "props": { "title": "Hello World", "subtitle": "A demo" },
      "transition": { "type": "fade" }
    },
    {
      "type": "content",
      "startSec": 5,
      "durationSec": 5,
      "props": { "header": "Key Points", "bulletPoints": ["Fast", "Safe", "Beautiful"] },
      "transition": { "type": "slide", "direction": "from-right" }
    },
    {
      "type": "code",
      "startSec": 10,
      "durationSec": 5,
      "props": { "code": "const x = 42;", "language": "typescript", "title": "Example" },
      "transition": { "type": "fade" }
    }
  ],
  "audio": []
}
```

### Design Rules

#### meta.theme (optional, strongly recommended)

Each video should define a unique aesthetic in `meta.theme`.
The theme system uses `@remotion/google-fonts` for consistent cross-platform rendering.

Default theme: Chakra Petch (display) + Outfit (body) + JetBrains Mono (code), dark blue palette with cyan accent.

```json
{
  "meta": {
    "theme": {
      "aesthetic": "brutalist tech",
      "font": { "display": "Chakra Petch", "body": "Outfit" },
      "color": { "accent": "#FF6B35", "bg": "#0A0A0A" },
      "gradient": { "hero": "radial-gradient(circle at 20% 30%, rgba(255,107,53,0.2) 0%, transparent 60%)" }
    }
  }
}
```

#### DO

- Use concise, punchy headers without emoji
- Write bullet points as short phrases (max 8 words)
- Limit to 3-4 bullets per slide
- Vary slide types: title → content → code → content
- Mix transitions: fade/slide/wipe, not all the same
- For code slides, show REAL code (not pseudocode)
- Pick a theme aesthetic and commit

#### DON'T

- Never use emoji in slide titles or headers
- Never put more than 5 bullets on a single slide
- Never use "Key Features", "Getting Started", "Summary" as headers
- Never repeat the same transition type 3+ times in a row
- Never use Inter, Roboto, Arial as fonts in meta.theme

#### Content Density — Fill The Frame

The rendering canvas is large (1920×1080 or 1080×1920). Sparse content creates dead space.
The fix is NOT bigger fonts or more padding — it's **more content blocks**.

**Core rule: Add blocks, don't stretch.**
If a slide has empty space, add more meaningful content to it — don't increase font size or spacing.

**Content slides — stack multiple blocks:**
- Always use `content` (paragraph) + `bulletPoints` together, not one alone
- Minimum 4-5 bullet points for portrait, 3-4 for landscape
- Bullet text should be substantive phrases (5-10 words), not single words
- Add a concluding sentence or key takeaway after bullet points
- Header should be descriptive and specific (not "Overview" or "Features")

**Code slides — fill the terminal:**
- Minimum 6 lines of code for portrait, 4 for landscape
- Add comments in the code to fill space meaningfully
- Always include a `title` prop above the code block
- If the code is short, add output/result comments below

**Title slides:**
- Always include a subtitle
- If short title, make the subtitle 2 lines (a full sentence)

**General:**
- Every slide should visually use ≥70% of the canvas area
- If a slide looks sparse, add more content blocks — not more whitespace
- Prefer fewer, denser slides over many sparse ones
- Think of each slide as a **poster**: header + body + supporting detail

#### Visual Quality — Video Anti-Slop (CRITICAL)

Video is MORE dynamic than static UI. Every frame is a first impression.
These rules adapt `dev-frontend/anti-slop.md` for Remotion motion context.

**Banned patterns — instant "AI slop" tells:**

| Banned                                               | Do Instead                                                                   |
| :--------------------------------------------------- | :--------------------------------------------------------------------------- |
| Same glow-orb → card → text structure on every slide | Each slide type has its OWN layout rhythm                                    |
| Everything centered with uniform padding             | TitleSlide = left-aligned, ContentSlide = asymmetric, QuoteSlide = offset    |
| One accent color flat everywhere                     | Accent as highlight ONLY — not header color + divider + bullets all the same |
| Font weight only 700/800                             | Use extremes: 200(thin labels) vs 900(black hero). Create tension            |
| Uniform `borderRadius: 20` on everything             | Outer card 24, inner chip/badge 8, stat card 16. Vary intentionally          |
| Static background gradient on every slide            | Shift gradient direction per slide type. Move glow orb position              |
| Bullet points are just text lines                    | Each bullet has a visual anchor: dot, number badge, icon, color bar          |
| All exits are identical fade-to-zero                 | Mix: scale-down, slide-away, blur-out. Exit is part of the rhythm            |

**Layout diversity per slide type:**

| Slide           | Layout Pattern                                                        | NOT This             |
| :-------------- | :-------------------------------------------------------------------- | :------------------- |
| TitleSlide      | Left-aligned, full-bleed background, accent line                      | Centered text blob   |
| ContentSlide    | Header left + bullets right (split), or header top + dense grid       | Centered stack       |
| CodeSlide       | Terminal-style frame, mono bg, glow on syntax                         | Card with code text  |
| StatSlide       | Asymmetric cards, stagger scale-in, big number / small label contrast | Equal centered cards |
| QuoteSlide      | Large `"` glyph 200px, quote offset right, author small bottom-left   | Centered italic text |
| ComparisonSlide | True split — left vs right with different accent hues                 | Two identical cards  |
| ChartSlide      | Chart fills 70%, labels crisp (min 20px), axis lines visible          | Tiny chart in card   |

**Motion principles for video (beyond static UI):**

- **One hero animation per slide** — don't animate everything equally. Pick ONE element that moves big, rest enters quietly
- **Stagger creates rhythm** — bullets, stat cards, chart bars. `delay = BASE + i * STEP` (6-10 frames between items)
- **Background is alive** — glow orbs drift slowly, gradient shifts over time. Static bg = dead frame
- **Exit is choreography** — don't just fade. The exit move of slide N should visually connect to the entrance of slide N+1
- **Weight extremes create depth** — 200 weight label + 900 weight number = instant premium. 700+800 = mud
- **Negative space is a feature** — don't fill every pixel. Strategic emptiness makes the content breathe

**Typography for video (different from web):**

- Minimum readable size: **24px** (1080p) / **28px** (portrait). Smaller = unwatchable
- Heading: **900 weight, tight letter-spacing (-0.03em), line-height 1.1**
- Body: **400 weight, generous line-height (1.6-1.7)**
- Labels/captions: **200-300 weight, wide letter-spacing (0.08em), uppercase**
- Numbers (stat): **`font-variant-numeric: tabular-nums`** for alignment during count-up

#### Shorts (Portrait-1080p)

Portrait has 1920px of vertical space — you MUST fill it.

- Max 8-10 elements for 60s
- First slide = hook (max 5 words) + descriptive subtitle
- Last slide = CTA or memorable closing + tagline
- 5-6 bullets per content slide (portrait can hold more)
- Code 6-10 lines (add comments to fill)
- Use `content` + `bulletPoints` together on every content slide

---

## TTS Integration (Multi-Provider Narration)

### Provider Overview

| Provider             | ID           | Default Voice | Strengths                                  | Env Key             |
| -------------------- | ------------ | ------------- | ------------------------------------------ | ------------------- |
| **Gemini** (default) | `gemini`     | `Kore`        | 30 voices, unlimited text, tone via prompt | `GEMINI_API_KEY`    |
| **Supertone Cloud**  | `supertone`  | Andrew        | 6 emotion styles, pitch/speed, Korean-best | `SUPERTONE_API_KEY` |
| **Supertonic Local** | `supertonic` | `M1`          | 0.22s gen, free, offline (Phase 11B)       | none                |

#### Gemini Auth Paths

```
GOOGLE_APPLICATION_CREDENTIALS or ADC configured?
├─ Yes → Vertex AI (same model: gemini-2.5-flash-preview-tts)
│   └─ new GoogleGenAI({ vertexai: true, project, location })
GEMINI_API_KEY exists?
├─ Yes → Gemini API (default path)
│   └─ new GoogleGenAI({ apiKey })
```

**Client initialization** (`gemini.mjs`):
```js
import { GoogleGenAI } from "@google/genai";

// Vertex AI (service account / ADC)
if (process.env.GOOGLE_APPLICATION_CREDENTIALS || process.env.GOOGLE_CLOUD_PROJECT) {
  const ai = new GoogleGenAI({
    vertexai: true,
    project: process.env.GOOGLE_CLOUD_PROJECT || "your-project-id",
    location: process.env.GOOGLE_CLOUD_LOCATION || "us-central1",
  });
}
// Gemini API (API key) — current default
else {
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
}
```

> [!WARNING]
> Model name is identical for both paths: `gemini-2.5-flash-preview-tts`.
> Vertex AI does NOT use File API — only direct generation calls.

### Provider Selection

```
Default (narration only)          → gemini
meta.ttsProvider specified        → that provider
element.voiceControl.style set    → supertone (needs emotion)
Bulk/offline generation           → supertonic (local)
```

### Priority Chain

```
CLI --provider    >  meta.ttsProvider    >  "gemini"
CLI --voice       >  meta.ttsVoice       >  provider.DEFAULT_VOICE
vc.speed          >  meta.ttsSpeed       >  1.2
vc.style          >  "neutral"           (supertone only)
vc.tonePrompt     >  (none)              (gemini only)
```

### Speed Strategy (default 1.2x)

| Provider       | Method                     | Notes                    |
| -------------- | -------------------------- | ------------------------ |
| **Gemini**     | ffmpeg `atempo` post-proc  | No native speed API      |
| **Supertone**  | API `voice_settings.speed` | Native — sounds natural  |
| **Supertonic** | ffmpeg `atempo` post-proc  | PyPI speed needs testing |

Set `speed: 1.0` to disable acceleration.

### Workflow: Draft → TTS → Final → Render

1. **Draft timeline**: Write `timeline.draft.json` with `narration` + optional `voiceControl`
2. **TTS generation**: Pipeline auto-detects narration → generates per-cut audio via selected provider
3. **Final timeline**: `timeline.final.json` with `audio[]` entries + corrected `durationSec`
4. **Render**: Final timeline rendered with synced audio

### Draft Timeline with Narration + VoiceControl

```json
{
  "meta": {
    "title": "Demo",
    "preset": "Landscape-1080p",
    "fps": 30,
    "ttsProvider": "gemini",
    "ttsSpeed": 1.2
  },
  "elements": [
    {
      "id": "intro",
      "type": "title",
      "durationSec": 11,
      "narration": "Welcome to the analysis report.",
      "voiceControl": { "tonePrompt": "Calm, professional news anchor tone" },
      "props": { "title": "Tech Trends", "subtitle": "2026 Edition" }
    },
    {
      "id": "concern",
      "type": "content",
      "durationSec": 16,
      "narration": "The financial outlook is concerning...",
      "voiceControl": { "tonePrompt": "Serious and empathetic tone" },
      "props": {
        "header": "Financial Analysis",
        "content": "Key metrics show decline.",
        "bulletPoints": ["Revenue down 15%", "Margin compression", "Cash burn rate"]
      }
    }
  ]
}
```

### VoiceControl Fields

| Field           | Provider    | Description                                          |
| --------------- | ----------- | ---------------------------------------------------- |
| `voice`         | All         | Override voice (provider-specific ID)                |
| `tonePrompt`    | Gemini only | Natural language tone instruction                    |
| `style`         | Supertone   | "neutral"\|"happy"\|"sad"\|"curious"\|"shy"\|"angry" |
| `pitch`         | Supertone   | Pitch shift -3 ~ +3                                  |
| `pitchVariance` | Supertone   | Pitch variance 0.5 ~ 2.0                             |
| `speed`         | All         | Playback speed 0.5 ~ 2.0                             |

### Duration Estimation

- Korean: ~6.5 chars/sec (range 6.0–7.3)
- Use `Math.ceil(narration.length / 6.5) + 0.5` for draft `durationSec`
- Final `durationSec` is auto-corrected by ffprobe measurement

### TTS Caching

- Cache key: `sha256(provider|voice|narration|style|pitch|pitchVariance|speed|tonePrompt)` → first 16 hex chars
- Files: `remotion-project/public/tts/{id}.{m4a|mp3|wav}`
- Cache hit: skips API call, reuses existing file
- Manifest: `remotion-project/public/tts/manifest.json`

### Audio Path Contract

| Context  | Path format        | Example                    |
| -------- | ------------------ | -------------------------- |
| Disk     | Full absolute path | `/abs/path/tts/id.m4a`     |
| Timeline | Relative in public | `tts/id.m4a`               |
| Renderer | `staticFile(src)`  | `staticFile("tts/id.m4a")` |

**NEVER** use `public/tts/...` in timeline — `staticFile()` already resolves from `public/`.

### Pipeline Status Model

| Status           | Meaning                       |
| ---------------- | ----------------------------- |
| `tts_generating` | TTS batch in progress         |
| `rendering`      | Remotion render in progress   |
| `succeeded`      | Render + validation passed    |
| `failed`         | Error (see `phase` + details) |

---

## Component Library

### Slides

| Component         | Props                                                   | Use For              |
| ----------------- | ------------------------------------------------------- | -------------------- |
| `TitleSlide`      | `title`, `subtitle`, `animation?`                       | Opening/closing      |
| `ContentSlide`    | `header`, `content`, `bulletPoints`, `animation?`       | Body content         |
| `CodeSlide`       | `code`, `language`, `title`, `animation?`               | Code demos           |
| `DiagramSlide`    | `src`, `title`, `caption`, `fit`, `animation?`          | Images/diagrams      |
| `StatSlide`       | `title`, `stats[]` (value/suffix/label/trend/decimals)  | KPI / count-up       |
| `QuoteSlide`      | `quote`, `author?`, `source?`                           | Quotes               |
| `ComparisonSlide` | `title`, `left{label,items,accent}`, `right{…}`         | Side-by-side compare |
| `VideoSlide`      | `src`, `title?`, `startFrom?`, `playbackRate?`, `loop?` | Inline video         |
| `GifSlide`        | `src`, `title?`, `fit?`                                 | Animated GIF         |
| `LottieSlide`     | `src`, `title?`                                         | Lottie animation     |
| `ChartSlide`      | `chartType`, `title`, `data{labels,datasets}`           | Bar/pie/line chart   |
| `Caption`         | `text`, `position`, `designTheme?`                      | Timed subtitles      |

All slide components consume `designTheme: Theme` from the theme system.
Theme is resolved once in `TimelineRenderer` and passed through `ElementRouter`.

### Surface Card System (Phase 20)

All content slides wrap their inner content in a **glassmorphism surface card**:
- `backdrop-filter: blur(N px)` — frosted glass
- Semi-transparent background (`rgba(15,23,42,0.65)` default)
- Subtle accent border + box shadow
- Customizable via `meta.theme.card` (`background`, `border`, `shadow`, `blur`, `borderRadius`)

### Animation System (Phase 21)

Each element accepts an optional `animation` config:
```json
{ "animation": { "enter": "scale-in", "exit": "fade-out" } }
```
Supported enter: `scale-in`, `fade-in`, `slide-up`, `none`
Supported exit: `scale-out`, `slide-down`, `fade-out`, `none`

Powered by `useEntranceAnimation()` hook — spring-based, auto-calculated from frame/durationInFrames.

### Transition Types (Phase 22)

| Type         | Options                                                   |
| ------------ | --------------------------------------------------------- |
| `fade`       | —                                                         |
| `slide`      | `direction`: from-left, from-right, from-top, from-bottom |
| `wipe`       | `direction`: from-left, from-right, from-top, from-bottom |
| `flip`       | `direction`: from-left, from-right                        |
| `clock-wipe` | —                                                         |

Optional `timing: "spring"` for spring-based transition timing.

### Korean Font Support (Phase 20.5)

NotoSansKR loaded as body font primary. Korean text renders natively without fallback issues.
Font stack: `NotoSansKR, Outfit, sans-serif` (body), `ChakraPetch, NotoSansKR, sans-serif` (display).

### Data Visualization (Phase 26)

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

### Audio Features (Phase 25)

Timeline `audio[]` entries support:
- `fadeInSec` / `fadeOutSec` — volume ramp
- `loop: true` — loop audio
- `trimStartSec` — skip N seconds from start

---

## Resolution Presets

| Preset            | Width | Height | Aspect | Use For             |
| ----------------- | ----- | ------ | ------ | ------------------- |
| `Landscape-720p`  | 1280  | 720    | 16:9   | Draft/preview       |
| `Landscape-1080p` | 1920  | 1080   | 16:9   | Standard delivery   |
| `Portrait-1080p`  | 1080  | 1920   | 9:16   | TikTok/Reels/Shorts |
| `Square-1080p`    | 1080  | 1080   | 1:1    | Instagram/LinkedIn  |

Default: `Landscape-1080p`. Agent picks based on user keywords (reels/shorts → Portrait).

---

## Render Validation — 3-Tier Gate

All 3 gates must pass for a render to be considered successful.

| Gate         | Checks                                  | Role            |
| :----------- | :-------------------------------------- | :-------------- |
| 1. Policy    | No forbidden engine in logs             | Supplementary   |
| 2. Execution | `remotion render` exit 0                | Primary         |
| 3. Artifact  | ffprobe duration/codec/resolution valid | **Final truth** |

```bash
# Gate 3 standalone validation
node scripts/validate-artifact.mjs /tmp/remotion-render/TimelineVideo.mp4 --preset Landscape-1080p
# → { "valid": true, "duration": 15.0, "codec": "h264", "width": 1920, "height": 1080 }
```

---

## Project Structure

```
skills_ref/video/
├── SKILL.md                          ← this file
├── scripts/
│   ├── pipeline.mjs                  ← CLI entrypoint (sync/async/TTS)
│   ├── tts.mjs                       ← TTS orchestrator (multi-provider)
│   ├── tts-providers/
│   │   ├── gemini.mjs                ← Gemini Cloud TTS (default)
│   │   ├── supertone.mjs             ← Supertone Cloud TTS (emotion)
│   │   └── supertonic.mjs            ← Supertonic Local TTS (Phase 11B)
│   ├── ensure-remotion.mjs           ← runtime bootstrap
│   ├── validate-artifact.mjs         ← Gate 3: ffprobe validation
│   └── presets.mjs                   ← resolution presets (ESM)
└── remotion-project/
    ├── package.json
    ├── tsconfig.json
    ├── public/example-timeline.json  ← example timeline
    └── src/
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

---

## Dependencies

- **Runtime**: Node.js 20+, pnpm, ffmpeg, ffprobe
- **Packages**: Installed globally at `~/.remotion/node_modules/`. Run `setup-remotion.sh` once.
- **Chromium**: Auto-installed by `remotion browser ensure` (called by `ensure-remotion.mjs`)
- **Env**: `GEMINI_API_KEY` for Gemini TTS (API key path); or `GOOGLE_APPLICATION_CREDENTIALS` / ADC for Vertex AI path; `SUPERTONE_API_KEY` for Supertone; none for Supertonic
- **Bootstrap**: `node scripts/ensure-remotion.mjs` before first render — checks `~/.remotion`
- **Vertex AI auth**: `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS`

### ⚠️ Output Path Rule

**NEVER write render output into `skills_ref/video/`.** This is source code, not a workspace.

- Default output: `/tmp/remotion-render/`
- Use `--output /tmp/my-project/` for custom paths
- Timeline draft/final files → `/tmp/` or project-specific dir
- `skills_ref/video/out/`, `skills_ref/video/timeline.draft.json` = **WRONG**
