# Remotion Route

Remotion is the active default for JSON/React timeline videos, TTS narration,
branded templates, captions, slide-to-video, data-driven explainers, UI demos,
and React-style motion graphics.

## Commands

Run commands from `skills_ref/video` unless using absolute paths.

| Task | Command |
|---|---|
| Render | `node scripts/pipeline.mjs --timeline <path> [--preset Landscape-1080p]` |
| Render + TTS | `node scripts/pipeline.mjs --timeline timeline.draft.json` |
| Skip TTS | `node scripts/pipeline.mjs --timeline timeline.draft.json --skip-tts` |
| TTS only | `node scripts/tts.mjs --batch timeline.draft.json [--provider supertone]` |
| TTS single | `node scripts/tts.mjs --text "Hello" --output /tmp/tts-out.m4a [--provider gemini]` |
| TTS voices | `node scripts/tts.mjs --list-voices [--provider supertone]` |
| Async | `node scripts/pipeline.mjs --timeline <path> --async` |
| Status | `node scripts/pipeline.mjs --status /tmp/remotion-render/render-result.json` |
| Preview | `cd remotion-project && pnpm exec remotion studio` |
| Validate | `node scripts/validate-artifact.mjs /tmp/remotion-render/TimelineVideo.mp4 --preset Landscape-1080p` |

## Pipeline Usage

Output goes to `/tmp/remotion-render` by default.

```bash
node skills_ref/video/scripts/pipeline.mjs \
  --timeline timeline.json \
  --output /tmp/remotion-render
```

With preset override:

```bash
node skills_ref/video/scripts/pipeline.mjs \
  --timeline timeline.json \
  --preset Portrait-1080p
```

`timeline.meta.preset` is the source of truth for resolution. CLI `--preset`
overrides it with a warning.

## Animation Rules

Use Remotion frame-based primitives:

- `useCurrentFrame()`
- `interpolate()`
- `spring()`
- `<Sequence>`

Forbidden:

- CSS transitions
- CSS animations
- Tailwind animation classes
- wall-clock animation assumptions

These do not render reliably in Remotion output. Animation must derive from
frames.

## Timeline Authoring

Minimal timeline:

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
      "props": {
        "header": "Key Points",
        "bulletPoints": ["Fast", "Safe", "Beautiful"]
      },
      "transition": { "type": "slide", "direction": "from-right" }
    }
  ],
  "audio": []
}
```

## Theme System

Each video should define a deliberate aesthetic.

```json
{
  "meta": {
    "theme": {
      "aesthetic": "premium tech briefing",
      "font": { "display": "Chakra Petch", "body": "Outfit" },
      "color": { "accent": "#67E8F9", "bg": "#0A0A0A" }
    }
  }
}
```

Avoid default-feeling combinations such as Inter/Roboto/Arial with generic blue
gradients unless the user's brand specifically requires them.

## Content Design Rules

Do:

- use concise headers without emoji
- write bullet points as short phrases
- vary slide types
- mix transitions intentionally
- show real code on code slides
- pick a style pack and commit to it

Avoid:

- generic headers like "Key Features" or "Summary"
- more than 5 bullets on ordinary slides
- sparse frames with tiny content
- repeating the same centered card layout

Portrait Shorts exception:

- 5-6 bullets can be acceptable when density is the explicit style and the frame
  remains readable.
- Use this as an exception, not the default.

## Components

Read `reference/components.md` for detailed component behavior.

Common element types:

- `title`
- `content`
- `code`
- `diagram`
- `stat`
- `quote`
- `comparison`
- `video`
- `gif`
- `lottie`
- `chart`
- captions

## TTS

Read `reference/tts-integration.md` for auth, priority, voice control, speed,
and caching.

Draft timeline flow:

1. write `timeline.draft.json` with `narration`
2. pipeline generates per-cut audio
3. pipeline writes `timeline.final.json`
4. final timeline renders with synced audio

## Resolution Presets

| Preset | Width | Height | Use |
|---|---:|---:|---|
| `Landscape-720p` | 1280 | 720 | draft/preview |
| `Landscape-1080p` | 1920 | 1080 | standard delivery |
| `Portrait-1080p` | 1080 | 1920 | TikTok/Reels/Shorts |
| `Square-1080p` | 1080 | 1080 | Instagram/LinkedIn |

Default: `Landscape-1080p`.

## Validation

Use Remotion's 3-tier gate:

| Gate | Checks |
|---|---|
| Policy | no forbidden engine in logs, supplementary |
| Execution | `remotion render` exits 0 |
| Artifact | ffprobe duration/codec/resolution valid |

Final truth is the artifact:

```bash
node scripts/validate-artifact.mjs /tmp/remotion-render/TimelineVideo.mp4 --preset Landscape-1080p
```

For non-trivial visuals, also sample or inspect frames and report a visual QA
verdict.
