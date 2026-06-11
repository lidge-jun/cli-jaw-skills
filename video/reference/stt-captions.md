# STT and Caption Generation

Use this file for audio/video transcription, diarized captions, subtitle
sidecars, word-timed captions, and Remotion caption overlays.

## Default Route

Default to local `progrok` HTTP STT:

```text
progrok /v1/stt -> transcript.raw.json -> transcript.normalized.json
-> captions.srt / captions.vtt / captions.remotion.json
```

Use FFmpeg for media prep and Remotion for designed caption overlays. Use
WhisperX, whisper-timestamped, or WebSocket STT only as docs-first/watchlist
fallbacks until a dedicated harness exists.

## Prerequisites

```bash
progrok status
curl --max-time 2 http://127.0.0.1:18645/v1/models
ffmpeg -version
ffprobe -version
```

If the proxy is not running, start `progrok proxy` before calling `/v1/stt`.

## Quick Start

```bash
node scripts/stt-captions.mjs \
  --input input.mp4 \
  --output /tmp/video-stt-demo \
  --language ko \
  --diarize \
  --word-timestamps \
  --keyterm Remotion \
  --keyterm HyperFrames
```

Deterministic fixture mode:

```bash
node scripts/stt-captions.mjs \
  --transcript fixture.raw.json \
  --source-audio fixture.wav \
  --output /tmp/video-stt-demo
```

## Audio Prep

Default mono PCM extraction:

```bash
ffmpeg -i input.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le audio.wav
```

Use multichannel only when channel separation is meaningful:

```bash
ffmpeg -i input.mp4 -vn -ar 16000 -c:a pcm_s16le audio-multichannel.wav
```

Rules:

- preserve the original media
- split long media by silence or scene boundary, not arbitrary bytes
- keep a keyterm glossary for model names, product names, people, and acronyms
- do not normalize audio unless noise/loudness materially harms STT

## Progrok HTTP STT

`progrok capabilities` currently exposes:

```text
POST /v1/stt — diarize, multichannel, keyterm, word timestamps
```

Representative request:

```bash
curl http://127.0.0.1:18645/v1/stt \
  -F "file=@audio.wav" \
  -F "language=ko" \
  -F "diarize=true" \
  -F "word_timestamps=true" \
  -F "keyterm=Remotion"
```

Always preserve the raw response. Provider field names can drift; update the
script only after a smoke test.

## Canonical Caption JSON

`stt-captions.mjs` writes canonical Remotion caption JSON:

```json
{
  "language": "ko",
  "sourceAudio": "/tmp/video-stt/audio.wav",
  "sourceMedia": "/tmp/video-stt/source.mp4",
  "entries": [
    {
      "id": "cue-001",
      "start": 0.4,
      "end": 2.2,
      "text": "progrok STT로 자막을 만듭니다.",
      "speaker": "SPEAKER_00",
      "style": "speaker",
      "words": [
        { "start": 0.4, "end": 0.9, "text": "progrok" }
      ]
    }
  ]
}
```

`pipeline.mjs` also accepts legacy arrays and `{ "segments": [...] }`, but new
artifacts should use `entries`.

## Caption Writing Rules

General:

- split by meaning, not fixed character counts
- avoid cues too short to read
- avoid overlap unless intentionally showing multiple speakers
- preserve product names and acronyms from keyterms
- separate raw transcript fidelity from polished caption wording

Korean/CJK:

- do not strand particles or endings on a new line
- keep mixed Korean/English technical terms intact
- use short, large phrases for 9:16 shorts
- use restrained lower-third captions for 16:9 briefings unless captions are the main visual device

## Remotion Overlay

Timeline config:

```json
{
  "meta": {
    "captions": {
      "src": "captions.remotion.json",
      "style": "bottom-center",
      "fontSize": 34,
      "backgroundColor": "rgba(0,0,0,0.72)"
    }
  }
}
```

`pipeline.mjs` loads `src` relative to the timeline file and embeds cue entries
before rendering. `Root.tsx` extends composition duration to include caption cue
end times, so late cues are not clipped.

## Validation

Minimum proof bundle:

- source media path
- audio extraction command
- extracted audio path
- raw transcript path
- normalized transcript path
- SRT/VTT path
- `captions.remotion.json` path
- monotonic timestamp check
- cue-boundary and overlap check
- rendered MP4 validation if overlay is used
- sampled frame/contact sheet when visual quality matters

Command success alone is not completion.

## Fallbacks and Watchlist

- WhisperX / whisper-timestamped: use when progrok timing is insufficient and a
  local dependency decision is approved.
- xAI WebSocket STT: watchlist. The local proxy does not forward WebSocket
  endpoints.
- Manual subtitle authoring: acceptable for tiny clips, but still produce the
  same sidecar artifacts and validation evidence.
