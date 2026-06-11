# TTS Captions

Use this route when the narration is authored by the agent/user and will be
spoken by TTS. The script is the source of truth for caption text. STT is only a
verification fallback for generated audio.

## Default Flow

```text
script JSON -> narration.normalized.json -> captions.remotion.json
-> timeline.draft.json -> existing tts.mjs batch -> timeline.final.json
-> pipeline caption alignment -> Remotion render
```

This differs from `stt-captions.md`: STT starts with existing audio/video, while
TTS captions start with a script.

## Quick Start

Run from `skills_ref/video`:

```bash
node scripts/tts-captions.mjs \
  --script examples/tts-captions/premium-briefing.script.json \
  --output /tmp/video-tts-captions
```

Render without provider credentials:

```bash
node scripts/pipeline.mjs \
  --timeline /tmp/video-tts-captions/timeline.draft.json \
  --output /tmp/video-tts-captions/render \
  --skip-tts
```

Render with TTS when the provider is configured:

```bash
node scripts/pipeline.mjs \
  --timeline /tmp/video-tts-captions/timeline.draft.json \
  --output /tmp/video-tts-captions/render
```

The default TTS provider is `progrok`, using the local OAuth proxy at
`http://127.0.0.1:18645/v1`. Start it with `progrok proxy` when it is not
already running. Use `--skip-tts` only for deterministic visual/caption checks;
it is not proof that the final video has audible narration.

## Script JSON

```json
{
  "meta": {
    "title": "Premium Briefing",
    "preset": "Landscape-720p",
    "fps": 30,
    "ttsProvider": "progrok",
    "ttsVoice": "eve",
    "ttsLanguage": "ko",
    "captions": {
      "style": "bottom-center",
      "fontSize": 34
    }
  },
  "beats": [
    {
      "id": "intro",
      "type": "title",
      "narration": "Script text is the caption source of truth.",
      "durationSec": 3.2,
      "props": {
        "title": "TTS Captions",
        "subtitle": "Script-first subtitles"
      },
      "transition": { "type": "fade", "durationSec": 0.45 },
      "voiceControl": { "tonePrompt": "calm premium tech briefing" }
    }
  ]
}
```

Rules:

- `beats[]` must be non-empty.
- each beat needs a stable `id` and `narration`.
- `type`, `props`, and `transition` map directly to Remotion timeline
  elements.
- `durationSec` can be omitted; the helper estimates it from words per minute.
- `voiceControl` stays provider-owned by `tts.mjs`.
- `meta.ttsLanguage` or `voiceControl.language` is recommended for progrok
  TTS; the helper defaults to `auto` when mixed-language detection is
  acceptable.

## Caption Timing

Generated cues carry both absolute draft times and local element binding:

```json
{
  "id": "intro-cue-01",
  "elementId": "intro",
  "localStart": 0,
  "localEnd": 2.75,
  "draftElementDurationSec": 3.2,
  "start": 0,
  "end": 2.75,
  "text": "Script text is the caption source of truth."
}
```

When TTS changes element durations, `pipeline.mjs` aligns bound cues before
embedding the caption sidecar:

```text
scale = finalElement.durationSec / draftElementDurationSec
start = elementStartSec + localStart * scale
end = elementStartSec + localEnd * scale
```

`elementStartSec` uses the same transition-overlap rule as Remotion timing.
Unbound cues without `elementId` remain absolute.

## Outputs

`tts-captions.mjs` writes:

- `narration.normalized.json`
- `captions.remotion.json`
- `captions.srt`
- `captions.vtt`
- `timeline.draft.json`
- `qa-report.md`

With `--align-timeline`, it also writes:

- `captions.aligned.remotion.json`
- `captions.aligned.srt`
- `captions.aligned.vtt`

## Validation

Minimum proof bundle:

- source script path
- normalized narration path
- `captions.remotion.json`
- `timeline.draft.json`
- TTS manifest or explicit `--skip-tts` rationale
- non-silent audio proof when the deliverable is expected to include narration
- alignment proof when TTS changes durations
- rendered MP4 validation when overlay is used
- sampled frame proof for non-trivial visuals

Do not use STT output as the final caption source for TTS videos unless the user
explicitly wants verbatim generated-audio subtitles.
