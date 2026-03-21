---
name: "speech"
description: "Use when the user asks for text-to-speech narration or voiceover, accessibility reads, audio prompts, or batch speech generation via the OpenAI Audio API; run the bundled CLI (`scripts/text_to_speech.py`) with built-in voices and require `OPENAI_API_KEY` for live calls. Custom voice creation is out of scope."
---


# Speech Generation Skill

Generate spoken audio for the current project (narration, product demo voiceover, IVR prompts, accessibility reads). Defaults to `gpt-4o-mini-tts-2025-12-15` and built-in voices, and prefers the bundled CLI for deterministic, reproducible runs.

## Workflow
1. Decide intent: single clip or batch (multiple lines/prompts → batch).
2. Collect inputs: exact text (verbatim), voice, delivery style, format, constraints.
3. If batch: write a temporary JSONL under tmp/ (one job per line), run once, then delete the JSONL.
4. Augment instructions into a short labeled spec without rewriting the input text.
5. Run the bundled CLI (`scripts/text_to_speech.py`) with sensible defaults (see references/cli.md).
6. For important clips, validate: intelligibility, pacing, pronunciation, and adherence to constraints.
7. Iterate with a single targeted change (voice, speed, or instructions), then re-check.
8. Save/return final outputs and note the final text + instructions + flags used.

## Temp and output conventions
- Use `tmp/speech/` for intermediate files (for example JSONL batches); delete when done.
- Write final artifacts under `output/speech/` when working in this repo.
- Use `--out` or `--out-dir` to control output paths; keep filenames stable and descriptive.

## Dependencies (install if missing)
Prefer `uv` for dependency management.

Python packages:
```
uv pip install openai
```
If `uv` is unavailable:
```
python3 -m pip install openai
```

## Environment
- `OPENAI_API_KEY` required for live API calls.
- If missing, direct user to https://platform.openai.com/api-keys — have them set it as env var locally (never paste in chat).

## Defaults & rules
- Use `gpt-4o-mini-tts-2025-12-15` unless the user requests another model.
- Default voice: `cedar`. If the user wants a brighter tone, prefer `marin`.
- Built-in voices only. Custom voices are out of scope for this skill.
- `instructions` are supported for GPT-4o mini TTS models, but not for `tts-1` or `tts-1-hd`.
- Input length must be <= 4096 characters per request. Split longer text into chunks.
- Enforce 50 requests/minute. The CLI caps `--rpm` at 50.
- Require `OPENAI_API_KEY` before any live API call.
- Provide a clear disclosure to end users that the voice is AI-generated.
- Use the OpenAI Python SDK (`openai` package) for all API calls; do not use raw HTTP.
- Prefer the bundled CLI (`scripts/text_to_speech.py`) over writing new one-off scripts.
- Never modify `scripts/text_to_speech.py`. If something is missing, ask the user before doing anything else.

## Instruction augmentation
Reformat user direction into a short labeled spec. Make implicit details explicit; keep invented additions to zero.

Template (include relevant lines only):
```
Voice Affect: <overall character and texture of the voice>
Tone: <attitude, formality, warmth>
Pacing: <slow, steady, brisk>
Emotion: <key emotions to convey>
Pronunciation: <words to enunciate or emphasize>
Pauses: <where to add intentional pauses>
Emphasis: <key words or phrases to stress>
Delivery: <cadence or rhythm notes>
```

- Keep it short — only details the user implied. Preserve input text verbatim.
- Ask only if a missing detail would block success.

## Examples

### Single example (narration)
```
Input text: "Welcome to the demo. Today we'll show how it works."
Instructions:
Voice Affect: Warm and composed.
Tone: Friendly and confident.
Pacing: Steady and moderate.
Emphasis: Stress "demo" and "show".
```

### Batch example (IVR prompts)
```
{"input":"Thank you for calling. Please hold.","voice":"cedar","response_format":"mp3","out":"hold.mp3"}
{"input":"For sales, press 1. For support, press 2.","voice":"marin","instructions":"Tone: Clear and neutral. Pacing: Slow.","response_format":"wav"}
```

## Instruction tips
- Structure: affect → tone → pacing → emotion → pronunciation/pauses → emphasis.
- 4–8 short lines; avoid conflicting guidance.
- Add pronunciation hints for names/acronyms. Repeat invariants across iterations to reduce drift.
- More: `references/prompting.md`. Copy/paste specs: `references/sample-prompts.md`.

## Guidance by use case
Use these modules when the request is for a specific delivery style. They provide targeted defaults and templates.
- Narration / explainer: `references/narration.md`
- Product demo / voiceover: `references/voiceover.md`
- IVR / phone prompts: `references/ivr.md`
- Accessibility reads: `references/accessibility.md`

## CLI + environment notes
- CLI commands + examples: `references/cli.md`
- API parameter quick reference: `references/audio-api.md`
- Instruction patterns + examples: `references/voice-directions.md`
- If network approvals / sandbox settings are getting in the way: `references/codex-network.md`


