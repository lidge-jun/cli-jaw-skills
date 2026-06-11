# Existing-Footage Editing

This route is docs-first. Use it for editing source footage with cuts,
subtitles, transcript-aware decisions, overlays, pacing, or post-production
polish. Use FFmpeg utility directly for simple deterministic transforms.

## When To Use

- user provides one or more existing videos
- cut down a long recording
- remove dead air or filler
- create clips/highlights
- add or burn subtitles
- reframe to portrait/square
- add overlays or title cards to existing footage
- polish audio or color after edits

## Core Artifacts

Create explicit intermediate artifacts:

- media inventory
- transcript cache when speech matters
- timeline view or packed takes
- EDL, edit decision list, or equivalent timeline JSON
- subtitle file when captions are used
- preview output
- final output
- validation report

## Editing Rules

Borrowed from actual video editing skill references:

- do not cut inside a spoken word
- snap speech cuts to word boundaries
- add short padding/fades at hard cut boundaries
- apply subtitles last
- subtitle timing must use the output timeline, not source offsets
- cache transcripts
- verify cut boundaries in the rendered output
- keep preview and final outputs separate

## Suggested Folder Shape

Use a project output folder, not `skills_ref/video`:

```text
/tmp/video-edit/
  project.md
  media-inventory.json
  transcripts/
  timeline-view.md
  edl.json
  subtitles/
  preview/
  final/
  validation.md
```

## Minimal Workflow

1. Inventory media with ffprobe.
2. Extract audio when transcription is needed.
3. Generate or reuse transcript/word timing.
4. Build a compact timeline view.
5. Draft EDL.
6. Render preview.
7. Inspect cut boundaries, captions, audio, and frames.
8. Render final.
9. Validate final output with ffprobe and visual checks.

## FFmpeg Examples

Extract audio:

```bash
ffmpeg -i raw.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav
```

Cut a segment:

```bash
ffmpeg -i raw.mp4 -ss 00:12:30 -to 00:15:45 -c copy segment_01.mp4
```

Concatenate segments:

```bash
ffmpeg -f concat -safe 0 -i concat.txt -c copy assembled.mp4
```

Burn subtitles:

```bash
ffmpeg -i assembled.mp4 -vf "subtitles=master.srt" -c:a copy final.mp4
```

## Validation

Required:

- final output path
- ffprobe duration, codec, dimensions
- EDL/timeline exists
- transcript exists or reason it is unnecessary
- subtitles are output-timeline aligned when used
- cut-boundary check completed
- sampled frames are readable and nonblank

This route should not be marked active-full until a local EDL/transcript/render
harness exists.
