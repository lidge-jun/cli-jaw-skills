# Validation

Video completion requires artifact evidence. A command exiting 0 is not enough.

## Universal Proof Bundle

For every rendered or edited video, collect:

- output path or provider result URL
- file exists and has non-zero size when local
- duration
- dimensions
- fps when applicable
- codec/container
- audio presence when audio is expected
- sampled frame or visual snapshot evidence for non-trivial visuals
- short PASS/FAIL verdict against the route's promise

Use `ffprobe` for local media:

```bash
ffprobe -v error -show_format -show_streams -of json /path/to/output.mp4
```

## Route Gates

### Remotion

Required:

1. render output path
2. `validate-artifact.mjs` or equivalent ffprobe evidence
3. expected preset/dimensions
4. sampled frame/still check for non-trivial visuals

```bash
node scripts/validate-artifact.mjs /tmp/remotion-render/TimelineVideo.mp4 --preset Landscape-1080p
```

`validate-artifact.mjs` is Remotion-oriented. Do not present it as universal
proof for HyperFrames or FFmpeg outputs.

### HyperFrames

Required:

1. `hyperframes doctor` or environment note
2. edited composition files, not blank scaffold
3. `hyperframes lint`
4. render output
5. ffprobe media facts
6. representative frames or `inspect` output
7. visual QA verdict

If `inspect` is unavailable, sample frames:

```bash
mkdir -p /tmp/my-video/snapshots
ffmpeg -y -i /tmp/my-video/renders/out.mp4 -vf fps=1/3 /tmp/my-video/snapshots/frame_%02d.png
```

### STT Captions

Required:

1. source media or source audio path
2. raw transcript JSON
3. normalized transcript JSON
4. SRT or VTT sidecar
5. `captions.remotion.json` when Remotion overlay is used
6. monotonic timestamp proof
7. cue boundary and overlap check
8. rendered MP4 validation and sampled frame proof when captions are overlaid

### TTS Captions

Required:

1. source script JSON path
2. `narration.normalized.json`
3. `captions.remotion.json`
4. SRT or VTT sidecar
5. `timeline.draft.json`
6. TTS manifest/duration evidence when provider TTS is run, or explicit
   `--skip-tts` rationale for deterministic checks
7. post-TTS alignment proof when TTS changes element durations
8. rendered MP4 validation and sampled frame proof when captions are overlaid

### FFmpeg Utility

Required:

1. input media facts when relevant
2. output media facts
3. expected transform stated: trim, concat, transcode, proxy, normalize, reframe
4. duration/dimensions/audio checks that match the transform

For concat/cut operations, verify the final duration rather than trusting the
concat command.

### Existing-Footage Editing

Required when speech/cuts/subtitles matter:

1. media inventory
2. transcript or reason it is not needed
3. edit decision list or equivalent timeline artifact
4. subtitle output-timeline timing when captions are used
5. cut-boundary check
6. final ffprobe evidence

### Provider Generation

Docs-first until a provider route is active. When used, required evidence:

1. provider/tool used
2. model or route name
3. auth/account preflight completed
4. task/job status or result URL
5. downloaded local file and ffprobe when possible
6. provider constraints: duration, aspect ratio, audio, references

### Video Understanding

Required:

1. input media identity
2. index/transcript/search method
3. timestamped evidence
4. clip ranges when clips are produced
5. playable or local evidence links

## Visual QA Checklist

For non-trivial visuals:

- nonblank frames
- text is readable and unclipped
- CJK text has safe line breaks
- one primary focus per beat
- selected style pack is recognizable
- no banned cliches from `reference/style-packs.md`
- duration/aspect matches the request

Report one line:

```text
Visual QA: PASS - sampled frames are nonblank, readable, unclipped, and match premium-tech-briefing.
```
