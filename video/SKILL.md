---
name: video
description: "Remotion video create, render, preview. Triggers: video, Remotion, animation, mp4, render video, slides to video."
---

# Remotion Video Skill

JSON-driven timeline rendering with Remotion. Create, render, preview, and review videos.
Triggers: "video", "Remotion", "animation", "mp4", "render video", "slides to video".
Covers: JSON-driven timeline, theme system, resolution presets, TTS narration, render pipeline.

---

## Quick Reference

| Task           | Command                                                                              |
| -------------- | ------------------------------------------------------------------------------------ |
| **Render**     | `node scripts/pipeline.mjs --timeline <path> [--preset Landscape-1080p]`             |
| **Render+TTS** | `node scripts/pipeline.mjs --timeline timeline.draft.json` (auto-detects narration)  |
| **Skip TTS**   | `node scripts/pipeline.mjs --timeline timeline.draft.json --skip-tts`                |
| **TTS only**   | `node scripts/tts.mjs --batch timeline.draft.json [--provider supertone]`            |
| **TTS single** | `node scripts/tts.mjs --text "Hello" --output /tmp/tts-out.m4a [--provider gemini]`  |
| **TTS voices** | `node scripts/tts.mjs --list-voices [--provider supertone]`                          |
| **Async**      | `node scripts/pipeline.mjs --timeline <path> --async`                                |
| **Status**     | `node scripts/pipeline.mjs --status /tmp/remotion-render/render-result.json`         |
| **Preview**    | `cd remotion-project && pnpm exec remotion studio`                                   |
| **Validate**   | `node scripts/validate-artifact.mjs /tmp/remotion-render/TimelineVideo.mp4 --preset Landscape-1080p` |

---

## Pipeline Usage

Output goes to `/tmp/remotion-render` by default. Keep render output outside `skills_ref/video/` — that directory is source code, not workspace.

```bash
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

# Check async status
node skills_ref/video/scripts/pipeline.mjs \
  --status /tmp/remotion-render/render-result.json
```

`timeline.meta.preset` is the source of truth for resolution. CLI `--preset` overrides it with a warning.

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

### Theme System (`meta.theme`)

Each video should define a unique aesthetic. Uses `@remotion/google-fonts` for cross-platform rendering.
Default: Chakra Petch (display) + Outfit (body) + JetBrains Mono (code), dark blue + cyan accent.

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

### Content Design Rules

**Do:**
- Use concise headers without emoji
- Write bullet points as short phrases (max 8 words), 3-4 per slide
- Vary slide types: title → content → code → content
- Mix transitions: fade/slide/wipe (avoid repeating same type 3+ times)
- Show real code on code slides
- Pick a theme aesthetic and commit

**Avoid:**
- Emoji in slide titles or headers
- More than 5 bullets on a single slide
- Generic headers like "Key Features", "Getting Started", "Summary"
- Inter, Roboto, Arial as fonts in meta.theme (because they signal generic/AI-generated content)

### Content Density — Fill the Frame

The canvas is large (1920×1080 or 1080×1920). Sparse content creates dead space.
Add more content blocks — not bigger fonts or more padding.

- **Content slides**: Use `content` + `bulletPoints` together; 4-5 bullets portrait, 3-4 landscape
- **Code slides**: Minimum 6 lines portrait, 4 landscape; add comments to fill space
- **Title slides**: Always include a subtitle
- **General**: Each slide should use ≥70% of canvas area; prefer fewer dense slides over many sparse ones

### Visual Quality

Detailed anti-slop rules, per-slide-type layout guidelines, motion principles, and typography specs → `reference/visual-quality.md`

### Shorts (Portrait-1080p)

- Max 8-10 elements for 60s
- First slide = hook (max 5 words) + descriptive subtitle
- Last slide = CTA or memorable closing + tagline
- 5-6 bullets per content slide, code 6-10 lines
- Use `content` + `bulletPoints` together on every content slide

---

## TTS Integration

Three providers available. Default: Gemini.

| Provider         | ID           | Default Voice | Strengths                              | Env Key             |
| ---------------- | ------------ | ------------- | -------------------------------------- | ------------------- |
| **Gemini**       | `gemini`     | `Kore`        | 30 voices, tone via prompt             | `GEMINI_API_KEY`    |
| **Supertone**    | `supertone`  | Andrew        | 6 emotion styles, Korean-best          | `SUPERTONE_API_KEY` |
| **Supertonic**   | `supertonic` | `M1`          | 0.22s gen, free, offline               | none                |

### Workflow: Draft → TTS → Final → Render

1. Write `timeline.draft.json` with `narration` + optional `voiceControl` per element
2. Pipeline auto-detects narration → generates per-cut audio
3. Produces `timeline.final.json` with `audio[]` entries + corrected `durationSec`
4. Final timeline rendered with synced audio

### Draft Timeline with Narration

```json
{
  "elements": [
    {
      "id": "intro",
      "type": "title",
      "durationSec": 11,
      "narration": "Welcome to the analysis report.",
      "voiceControl": { "tonePrompt": "Calm, professional news anchor tone" },
      "props": { "title": "Tech Trends", "subtitle": "2026 Edition" }
    }
  ]
}
```

### Duration Estimation

- Korean: ~6.5 chars/sec → `Math.ceil(narration.length / 6.5) + 0.5`
- Final `durationSec` auto-corrected by ffprobe measurement

Full TTS details (auth paths, priority chain, voiceControl fields, caching, audio path contract) → `reference/tts-integration.md`

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

### Features

- **Surface Card**: Glassmorphism wrapper on content slides. Customize via `meta.theme.card`
- **Animation**: Optional `animation: { enter: "scale-in", exit: "fade-out" }` per element. Enter: scale-in, fade-in, slide-up, none. Exit: scale-out, slide-down, fade-out, none
- **Transitions**: fade, slide, wipe, flip, clock-wipe. Optional `timing: "spring"`. Slide/wipe accept `direction`
- **Korean fonts**: NotoSansKR loaded as body primary. Stack: `NotoSansKR, Outfit, sans-serif`
- **Charts**: bar (staggered grow), pie (sweep), line (draw-on). Pure SVG, no external library
- **Audio**: `fadeInSec`/`fadeOutSec`, `loop`, `trimStartSec`

Full component details → `reference/components.md`

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

All 3 gates pass for a render to be considered successful.

| Gate         | Checks                                  | Role            |
| :----------- | :-------------------------------------- | :-------------- |
| 1. Policy    | No forbidden engine in logs             | Supplementary   |
| 2. Execution | `remotion render` exit 0                | Primary         |
| 3. Artifact  | ffprobe duration/codec/resolution valid | **Final truth** |

```bash
node scripts/validate-artifact.mjs /tmp/remotion-render/TimelineVideo.mp4 --preset Landscape-1080p
```

---

## Dependencies

- **Runtime**: Node.js 20+, pnpm, ffmpeg, ffprobe
- **Packages**: Installed at `~/.remotion/node_modules/`. Run `setup-remotion.sh` once
- **Chromium**: Auto-installed by `remotion browser ensure` (via `ensure-remotion.mjs`)
- **TTS env**: `GEMINI_API_KEY` for Gemini; `SUPERTONE_API_KEY` for Supertone; none for Supertonic
- **Bootstrap**: `node scripts/ensure-remotion.mjs` before first render
- **Vertex AI auth**: `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS`

---

## Project Structure

```
skills_ref/video/
├── SKILL.md
├── reference/                    ← visual-quality.md, tts-integration.md, components.md
├── scripts/
│   ├── pipeline.mjs              ← CLI entrypoint (sync/async/TTS)
│   ├── tts.mjs                   ← TTS orchestrator (multi-provider)
│   ├── tts-providers/            ← gemini.mjs, supertone.mjs, supertonic.mjs
│   ├── ensure-remotion.mjs       ← runtime bootstrap
│   ├── validate-artifact.mjs     ← Gate 3: ffprobe validation
│   └── presets.mjs               ← resolution presets (ESM)
└── remotion-project/
    ├── public/example-timeline.json
    └── src/
        ├── components/           ← 11 slide components + barrel
        └── timeline/             ← JSON→React engine
```
