---
name: video
description: "Code-based video create, edit, render, preview, and validate. Defaults to Remotion for JSON/React timelines, routes HyperFrames HTML video, TTS/STT captions, FFmpeg transforms, existing-footage editing, and docs-first provider/video-understanding workflows."
---

# Code-Based Video Skill

Route video work before rendering. Remotion is the implemented default for
JSON/React timeline videos. HyperFrames is the HTML/CSS/GSAP route for
agent-authored compositions. FFmpeg handles deterministic media transforms.

Triggers: "video", "Remotion", "HyperFrames", "animation", "mp4", "render video",
"slides to video", "HTML video", "edit this video", "subtitle video",
"video summary", "image to video", "presenter video".

Core rule: choose the route, load the matching reference, produce route-specific
artifacts, and validate the output. A successful command is not enough.

Authoring discipline: keep the main skill short, move deep engine rules into
references, and avoid copying large third-party docs into the active prompt.

---

## Route First

Read `reference/route-selector.md` when intent is not a simple Remotion render.

| User intent | Route | Status | Read |
|---|---|---|---|
| React/JSON timeline, branded explainer, TTS, captions, slide-to-video | Remotion | Active default | `reference/remotion.md` |
| HTML/CSS/GSAP composition, kinetic typography, premium tech briefing | HyperFrames | Active smoke route | `reference/hyperframes.md` |
| Authored narration, script-first subtitles, TTS-ready caption sidecars | TTS captions | Active via script JSON + Remotion draft timeline | `reference/tts-captions.md` |
| Audio/video transcription, diarized captions, subtitle generation, word-timed captions | STT captions | Active via progrok HTTP STT + FFmpeg prep | `reference/stt-captions.md` |
| Trim, concat, transcode, proxy, audio, reframe, deterministic media ops | FFmpeg utility | Active utility | `reference/validation.md` |
| Cut/polish existing footage with transcript, EDL, subtitles, overlays | Existing-footage editing | Docs-first | `reference/existing-footage-editing.md` |
| New generative video clips, image-to-video, cinematic model output | Provider video generation | Deferred docs-first | `reference/route-selector.md` |
| Presenter/avatar/talking-head video | Presenter/avatar video | Deferred docs-first | `reference/route-selector.md` |
| Search, summarize, index, or clip moments from existing video | Video understanding | Deferred docs-first | `reference/route-selector.md` |
| Browser-native media capture or MediaRecorder-style render | Browser media | Watchlist | `reference/route-selector.md` |

Default choice:

- Use **Remotion** unless the user asks for HTML-first authoring, raw media
  editing, provider generation, presenter/avatar video, or video search.
- Use **HyperFrames** for agent-editable HTML/CSS/GSAP compositions and premium
  tech briefings.
- Use **FFmpeg** for deterministic transforms.
- Treat provider, presenter, video-understanding, JSON-template, and browser
  media routes as docs-first/watchlist until a verified harness exists.

Do not promise render support for docs-first or watchlist routes. State the
missing harness or provider requirement.

---

## Visual Quality Gate

For any non-trivial original video, read:

- `reference/visual-direction.md`
- `reference/style-packs.md`
- `reference/visual-quality.md`

Workflow:

1. Perform a design read: audience, platform, palette, typography, density, and
   motion intensity.
2. Pick a style pack or define one.
3. Author the composition/edit.
4. Render or produce a preview.
5. Validate with media evidence plus sampled frames or snapshots.
6. Report a short visual QA verdict.

Hard rule: style presets are direction; validation gates are law.

---

## Remotion Quick Start

Use Remotion for the implemented JSON timeline pipeline.

```bash
node skills_ref/video/scripts/pipeline.mjs \
  --timeline timeline.json \
  --output /tmp/remotion-render
```

Common commands:

| Task | Command |
|---|---|
| Render | `node scripts/pipeline.mjs --timeline <path> [--preset Landscape-1080p]` |
| Render with TTS | `node scripts/pipeline.mjs --timeline timeline.draft.json` |
| Skip TTS | `node scripts/pipeline.mjs --timeline timeline.draft.json --skip-tts` |
| TTS only | `node scripts/tts.mjs --batch timeline.draft.json [--provider progrok]` |
| TTS single | `node scripts/tts.mjs --text "안녕하세요" --output /tmp/tts.mp3 --provider progrok --language ko` |
| TTS voices | `curl http://127.0.0.1:18645/v1/tts/voices` |
| TTS captions | `node scripts/tts-captions.mjs --script script.json --output /tmp/video-tts-captions` |
| STT captions | `node scripts/stt-captions.mjs --input input.mp4 --output /tmp/video-stt --language ko --diarize --word-timestamps` |
| Preview | `cd remotion-project && pnpm exec remotion studio` |
| Validate | `node scripts/validate-artifact.mjs /tmp/remotion-render/TimelineVideo.mp4 --preset Landscape-1080p` |

Read `reference/remotion.md` for timeline authoring, presets, TTS, components,
animation rules, and validation details.

Remotion animation rules:

- Use `useCurrentFrame`, `interpolate`, `spring`, and `<Sequence>`.
- Do not use CSS transitions, CSS animations, or Tailwind animation classes.
- Keep generated render outputs outside `skills_ref/video`.

---

## HyperFrames Quick Start

Use HyperFrames when the deliverable should be authored as HTML/CSS/GSAP.

```bash
npx --yes hyperframes doctor
npx --yes hyperframes init /tmp/my-video --example blank --non-interactive --skip-skills --resolution landscape
npx --yes hyperframes lint /tmp/my-video
npx --yes hyperframes render /tmp/my-video --output /tmp/my-video/renders/out.mp4 --format mp4 --quality standard --fps 30
ffprobe -v error -show_format -show_streams -of json /tmp/my-video/renders/out.mp4
```

Before rendering, author the composition. Rendering an untouched blank scaffold
is not valid proof.

Read `reference/hyperframes.md` for production loop, premium tech briefing
style, GeekNews smoke recipe, and verification gates.

---

## FFmpeg Utility Route

FFmpeg is the active deterministic media utility route.

Examples:

```bash
# Extract segment
ffmpeg -i raw.mp4 -ss 00:12:30 -to 00:15:45 -c copy segment_01.mp4

# Concatenate listed files
ffmpeg -f concat -safe 0 -i concat.txt -c copy assembled.mp4

# Proxy for faster editing
ffmpeg -i raw.mp4 -vf "scale=960:-2" -c:v libx264 -preset ultrafast -crf 28 proxy.mp4

# Extract audio for transcription
ffmpeg -i raw.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav

# Normalize audio
ffmpeg -i segment.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v copy normalized.mp4
```

For cut-heavy editing, subtitles, transcript-aware decisions, or output
timeline EDLs, read `reference/existing-footage-editing.md` instead of treating
the task as raw FFmpeg snippets.

---

## Validation

Read `reference/validation.md` before declaring a video task complete.

Minimum route evidence:

| Route | Evidence |
|---|---|
| Remotion | output path, non-zero MP4, `validate-artifact.mjs` or ffprobe, sampled/still frame for non-trivial visuals |
| HyperFrames | doctor/lint/render, ffprobe, sampled frames or inspect output, visual QA verdict |
| TTS captions | script JSON, normalized narration, `captions.remotion.json`, draft/final timeline, TTS manifest or skip-TTS rationale, non-silent audio proof when TTS is expected, alignment proof when TTS changes duration, rendered frame proof if overlaid |
| STT captions | raw transcript, normalized transcript, SRT/VTT, `captions.remotion.json`, timestamp checks, rendered frame proof if overlaid |
| FFmpeg | input/output ffprobe, expected duration/dimensions/codec, output inspection |
| Existing footage | EDL/timeline artifact, transcript cache when speech matters, subtitle-last proof, cut-boundary checks |

Command succeeded != done. Completion requires route-specific evidence.

---

## Workspace Policy

Read `reference/workspace-policy.md` for source/output boundaries.

- `skills_ref/video` is source, not workspace.
- Generated video/audio/caption outputs go to `/tmp` or a project output folder.
- Do not commit generated MP4/WebM/GIF/audio unless explicitly requested.
- Third-party reference repositories are idea/reference material, not active
  runtime code.

---

## Reference Map

| File | When to read |
|---|---|
| `reference/route-selector.md` | ambiguous intent, docs-first routes, provider/understanding/presenter requests |
| `reference/remotion.md` | Remotion timeline, TTS, components, animation, render pipeline |
| `reference/hyperframes.md` | HTML/CSS/GSAP compositions and premium tech briefings |
| `reference/tts-captions.md` | authored narration, script-first subtitles, TTS-ready caption sidecars |
| `reference/stt-captions.md` | audio transcription, diarization, subtitles, word-level timing, Remotion caption JSON |
| `reference/existing-footage-editing.md` | transcript/EDL/subtitle/cut-boundary editing |
| `reference/visual-direction.md` | design read before non-trivial original video |
| `reference/style-packs.md` | first-pass video aesthetics and banned cliches |
| `reference/visual-quality.md` | anti-slop frame, typography, layout, and motion rules |
| `reference/validation.md` | proof bundles and completion gates |
| `reference/workspace-policy.md` | generated media, reference repos, and commit policy |
| `reference/tts-integration.md` | provider auth, voiceControl, speed, caching |
| `reference/components.md` | Remotion component library details |

---

## Dependencies

- Node.js 20+, pnpm, ffmpeg, ffprobe
- Remotion dependencies under `~/.jaw-shared/remotion/node_modules/`
- Bootstrap Remotion with `node scripts/ensure-remotion.mjs`
- HyperFrames via `npx --yes hyperframes ...`
- TTS via local progrok proxy `/v1/tts` by default; run `progrok proxy`
  or use `PROGROK_BASE_URL` when the proxy is on another port.
- TTS captions via script JSON, existing TTS batch, Remotion caption sidecars
- STT captions via local `progrok` proxy `/v1/stt`, plus ffmpeg/ffprobe
- TTS: `GEMINI_API_KEY` for Gemini, `SUPERTONE_API_KEY` for Supertone,
  none for Supertonic
