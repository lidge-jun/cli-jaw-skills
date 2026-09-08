# TTS Integration — Detailed Reference

## Progrok Auth Path

Progrok is the default TTS provider for local cli-jaw video work.

```text
progrok login done?
├─ Yes → progrok proxy at http://127.0.0.1:18645/v1
│   └─ POST /v1/tts returns audio bytes using the user's xAI OAuth session
No proxy?
└─ Start `progrok proxy` or set PROGROK_BASE_URL to another local proxy URL
```

`progrok.mjs` calls the local proxy, not xAI directly. It does not need
`XAI_API_KEY`, `GEMINI_API_KEY`, or `SUPERTONE_API_KEY`.

Request shape:

```json
{
  "text": "안녕하세요",
  "voice_id": "eve",
  "language": "ko",
  "output_format": { "codec": "mp3" },
  "speed": 1.0,
  "text_normalization": true
}
```

Built-in voices: `eve`, `ara`, `leo`, `rex`, `sal`. Custom voice ids from
progrok/xAI can also be passed as `voiceControl.voice`.

## Gemini Auth Paths

```
GOOGLE_APPLICATION_CREDENTIALS or ADC configured?
├─ Yes → Vertex AI (same model: gemini-2.5-flash-preview-tts)
│   └─ new GoogleGenAI({ vertexai: true, project, location })
GEMINI_API_KEY exists?
├─ Yes → Gemini API (default path)
│   └─ new GoogleGenAI({ apiKey })
```

Client initialization (`gemini.mjs`):
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

Note: Model name is identical for both paths: `gemini-2.5-flash-preview-tts`.
Vertex AI does not use File API — only direct generation calls.

## Provider Selection

```
Default (narration only)          → progrok
meta.ttsProvider specified        → that provider
element.voiceControl.style set    → supertone (needs emotion)
Bulk/offline generation           → supertonic (local)
```

## Priority Chain

```
CLI --provider    >  meta.ttsProvider    >  "progrok"
CLI --voice       >  meta.ttsVoice       >  provider.DEFAULT_VOICE
CLI --language    >  meta.ttsLanguage    >  PROGROK_TTS_LANGUAGE > "auto"
vc.speed          >  meta.ttsSpeed       >  1.2
vc.style          >  "neutral"           (supertone only)
vc.tonePrompt     >  (none)              (gemini only)
```

## Speed Strategy (default 1.2x)

| Provider       | Method                     | Notes                    |
| -------------- | -------------------------- | ------------------------ |
| **Progrok**    | API `speed`                | Native; OAuth proxy      |
| **Gemini**     | ffmpeg `atempo` post-proc  | No native speed API      |
| **Supertone**  | API `voice_settings.speed` | Native — sounds natural  |
| **Supertonic** | ffmpeg `atempo` post-proc  | PyPI speed needs testing |

Set `speed: 1.0` to disable acceleration.

## VoiceControl Fields

| Field           | Provider    | Description                                          |
| --------------- | ----------- | ---------------------------------------------------- |
| `voice`         | All         | Override voice (provider-specific ID)                |
| `tonePrompt`    | Gemini only | Natural language tone instruction                    |
| `language`      | Progrok     | BCP-47 language such as `ko`, `en`, or `auto`        |
| `style`         | Supertone   | "neutral"\|"happy"\|"sad"\|"curious"\|"shy"\|"angry" |
| `pitch`         | Supertone   | Pitch shift -3 ~ +3                                  |
| `pitchVariance` | Supertone   | Pitch variance 0.5 ~ 2.0                             |
| `speed`         | All         | Playback speed 0.5 ~ 2.0                             |

## TTS Caching

- Cache key: `sha256(provider|voice|narration|style|pitch|pitchVariance|speed|tonePrompt|language)` → first 16 hex chars
- Files: `remotion-project/public/tts/{id}.{m4a|mp3|wav}`
- Cache hit: skips API call, reuses existing file
- Manifest: `remotion-project/public/tts/manifest.json`

## Script-First Captions

For narrated videos that need subtitles, use `reference/tts-captions.md` before
running provider TTS.

Ownership:

- `tts-captions.mjs` owns script normalization, caption sidecars, and
  `timeline.draft.json`.
- `tts.mjs` owns provider selection, voice control, cache keys, audio files, and
  `timeline.final.json`.
- `pipeline.mjs` owns post-TTS caption realignment before Remotion render.

When the caption sidecar contains `elementId`, `localStart`, and `localEnd`,
`pipeline.mjs` aligns captions against the effective final timeline so TTS
duration drift does not desync subtitles.

## Audio Path Contract

| Context  | Path format        | Example                    |
| -------- | ------------------ | -------------------------- |
| Disk     | Full absolute path | `/abs/path/tts/id.m4a`     |
| Timeline | Relative in public | `tts/id.m4a`               |
| Renderer | `staticFile(src)`  | `staticFile("tts/id.m4a")` |

In timeline, use `tts/id.m4a` (not `public/tts/...`) — `staticFile()` already resolves from `public/`.

## Pipeline Status Model

| Status           | Meaning                       |
| ---------------- | ----------------------------- |
| `tts_generating` | TTS batch in progress         |
| `rendering`      | Remotion render in progress   |
| `succeeded`      | Render + validation passed    |
| `failed`         | Error (see `phase` + details) |
