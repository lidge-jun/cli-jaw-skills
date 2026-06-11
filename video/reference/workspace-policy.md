# Workspace Policy

`skills_ref/video` is source code and instruction material. It is not a render
workspace.

## Output Locations

Use one of:

- `/tmp/<video-project>/`
- `/tmp/remotion-render/`
- `/tmp/video-stt-<slug>/`
- `/tmp/video-tts-<slug>/`
- a user-approved project output directory
- an ignored repo-local scratch directory only when project conventions allow it

Do not write generated videos, audio, captions, or frame dumps into
`skills_ref/video` unless the user explicitly asks for a committed fixture.

## Commit Policy

Do not commit generated media by default:

- `.mp4`
- `.webm`
- `.mov`
- `.gif`
- `.wav`
- `.mp3`
- frame dumps
- provider result downloads
- raw STT transcripts and generated subtitle sidecars unless explicitly requested
- generated TTS audio, TTS manifests, final timelines, and aligned caption
  sidecars unless explicitly requested

Commit source artifacts instead:

- `SKILL.md`
- reference docs
- timeline JSON examples when intentionally maintained
- deterministic scripts
- tiny caption JSON fixtures when needed for renderable examples
- tiny fixtures only when needed for tests

## Third-Party References

Downloaded reference repositories belong in devlog/reference material, not in
active skills.

Rules:

- remove nested `.git`
- keep source attribution
- do not copy code into active skill/runtime without license review
- use ideas, workflows, and contracts as research inputs
- keep large generated media out of committed references unless explicitly
  required

## Runtime Skill Sync

Patch source first, validate it, then sync active skill:

```bash
cli-jaw skill install video --force
cli-jaw skill read video
```

Do not edit `~/.cli-jaw-3459/skills/video` as the source of truth. It is the
installed runtime copy.
