# Route Selector

Use this file when a video request is not a straightforward Remotion timeline
render.

## Classification Order

Classify by user intent before selecting an engine.

1. Existing source video supplied?
   - Search/summarize/index moments -> video understanding (docs-first)
   - Cut/polish/subtitle/reframe -> existing-footage editing (docs-first) or
     FFmpeg utility for simple transforms
2. New code-rendered video?
   - JSON/React/data/timeline/slide video -> Remotion (active default)
   - HTML/CSS/GSAP/agent-editable composition -> HyperFrames (active smoke route)
3. New generated video clip?
   - Cinematic text-to-video or image-to-video -> provider generation
     (deferred docs-first)
4. Human presenter or avatar?
   - Route to presenter/avatar video (deferred docs-first)
5. Pure media transform?
   - Route to FFmpeg utility (active)

## Route Status

| Route | Status | Promise level |
|---|---|---|
| Remotion | Active default | local render supported through existing scripts |
| HyperFrames | Active smoke route | local HTML composition render supported when CLI works |
| FFmpeg utility | Active | deterministic transforms supported |
| Existing-footage editing | Docs-first | use contracts; do not overpromise full agent editor |
| Provider video generation | Deferred docs-first | verify current provider docs/auth/model before use |
| Presenter/avatar video | Deferred docs-first | verify provider, avatar, voice, and language readiness |
| Video understanding | Deferred docs-first | verify VideoDB or equivalent ingest/index tool |
| JSON template rendering | Deferred docs-first | requires runtime/license decision |
| Motion Canvas / Manim / MoviePy | Watchlist | add harness before promising output |

## Conservative Defaults

- Remotion is the default for new code-rendered timeline videos.
- HyperFrames is preferred for HTML-native motion graphics and tech briefings.
- FFmpeg is preferred for simple deterministic media transforms.
- Existing source video defaults to editing or understanding, not generation.
- Provider routes require current docs or CLI/MCP discovery before execution.
- Docs-first routes may produce plans, contracts, or manual instructions, but
  should not claim local render support until a harness exists.

## Adjacent Skill Chaining

Video work often depends on adjacent capabilities:

- image generation for first frames, textures, thumbnails, or title cards
- TTS for narration
- search for current provider docs
- browser/desktop capture for UI demos
- diagram for source charts or explanatory graphics

Chain deliberately. Do not call adjacent skills just because they exist.

## Provider Route Guardrail

For provider video generation, never rely on memorized endpoints. The minimum
preflight is:

1. current official docs or CLI/MCP help checked
2. auth/API key/account state known
3. model supports the requested duration/aspect/audio/reference mode
4. cost/latency risk surfaced
5. output validation path known

If any of these are missing, keep the provider route docs-first and propose a
Remotion/HyperFrames/local alternative.
