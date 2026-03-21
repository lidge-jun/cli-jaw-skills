# TTS Integration — Detailed Reference

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
Default (narration only)          → gemini
meta.ttsProvider specified        → that provider
element.voiceControl.style set    → supertone (needs emotion)
Bulk/offline generation           → supertonic (local)
```

## Priority Chain

```
CLI --provider    >  meta.ttsProvider    >  "gemini"
CLI --voice       >  meta.ttsVoice       >  provider.DEFAULT_VOICE
vc.speed          >  meta.ttsSpeed       >  1.2
vc.style          >  "neutral"           (supertone only)
vc.tonePrompt     >  (none)              (gemini only)
```

## Speed Strategy (default 1.2x)

| Provider       | Method                     | Notes                    |
| -------------- | -------------------------- | ------------------------ |
| **Gemini**     | ffmpeg `atempo` post-proc  | No native speed API      |
| **Supertone**  | API `voice_settings.speed` | Native — sounds natural  |
| **Supertonic** | ffmpeg `atempo` post-proc  | PyPI speed needs testing |

Set `speed: 1.0` to disable acceleration.

## VoiceControl Fields

| Field           | Provider    | Description                                          |
| --------------- | ----------- | ---------------------------------------------------- |
| `voice`         | All         | Override voice (provider-specific ID)                |
| `tonePrompt`    | Gemini only | Natural language tone instruction                    |
| `style`         | Supertone   | "neutral"\|"happy"\|"sad"\|"curious"\|"shy"\|"angry" |
| `pitch`         | Supertone   | Pitch shift -3 ~ +3                                  |
| `pitchVariance` | Supertone   | Pitch variance 0.5 ~ 2.0                             |
| `speed`         | All         | Playback speed 0.5 ~ 2.0                             |

## TTS Caching

- Cache key: `sha256(provider|voice|narration|style|pitch|pitchVariance|speed|tonePrompt)` → first 16 hex chars
- Files: `remotion-project/public/tts/{id}.{m4a|mp3|wav}`
- Cache hit: skips API call, reuses existing file
- Manifest: `remotion-project/public/tts/manifest.json`

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
