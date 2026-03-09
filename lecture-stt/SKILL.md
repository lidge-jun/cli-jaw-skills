---
name: lecture-stt
description: >
  Transcribe audio lectures into structured markdown notes using LLM-based STT
  (Gemini 3 Flash Preview) with contextual prompting. Supports PDF slide guides,
  domain-aware term hints, and local Whisper fallback.
  Triggers: "강의 전사", "STT", "lecture transcription", "오디오 전사",
  "강의 녹음", "audio to text", "lecture notes", "음성 변환",
  "녹음 텍스트", "전사해줘", "transcribe", "whisper"
---

# Lecture STT Skill

## Goal

Convert lecture audio recordings into near-verbatim structured markdown
using LLM-based Speech-to-Text. The skill leverages **contextual prompting**
(PDF slides as structural guide, domain term hints) to produce page-by-page
transcriptions that preserve the professor's actual spoken words.

## Key Insight

LLM STT with a PDF structural guide produces **speech-only** transcription —
the PDF identifies which slide is being discussed, while the output captures
only what the professor actually said. Without proper prompting, models tend
to copy-paste slide text instead of transcribing speech.

## Instructions

### 1. Gather Inputs

Required:
- **Audio file** — `.m4a`, `.mp3`, `.wav` (up to ~8 hours)
- **Subject title** — e.g. "거시경제학", "헌법", "Data Structures"

Optional (strongly recommended):
- **PDF slides** — acts as structural guide for page-by-page output
- **Custom terms** — domain-specific proper nouns, acronyms
- **Language hint** — tell agent the lecture language (e.g. "English lecture")

### 2. Select Engine

```
GOOGLE_APPLICATION_CREDENTIALS or ADC configured?
├─ Yes → Vertex AI + Gemini 3 Flash Preview (recommended ⭐, location='global')
│   └─ Best instruction following for verbatim STT
GEMINI_API_KEY exists?
├─ Yes → Gemini API + Gemini 3 Flash Preview (recommended ⭐)
│   └─ Fallback: Gemini 3.1 Flash-Lite (faster but may copy slide text)
├─ No, OPENAI_API_KEY exists?
│   └─ Yes → OpenAI gpt-4o-transcribe (supports diarization)
└─ No → mlx-whisper local (Apple Silicon, offline, free)
```

> [!IMPORTANT]
> **Vertex AI requires `location='global'`** for gemini-3.* models.
> Using `us-central1` returns 404 NOT_FOUND.

### 3. Build Prompt

Choose the appropriate prompt level based on available inputs:

#### Level 1 — Basic (no context)
```
Transcribe this audio in its original language. Output transcription only.
```
Use when: domain unknown, quick-and-dirty transcription needed.

#### Level 2 — Domain Hints
```
Transcribe this audio in its original language. Output transcription only.

Context: {domain description}
Key Terms: {comma-separated terms}
```
Use when: you know the subject but have no PDF.

#### Level 3 — Domain + Format
```
Transcribe this audio in its original language.

Context: {domain}
Key Terms: {terms}
Speaker: {speaker info, if known}

Output format:
- Sentence-level line breaks
- Numbers in Arabic numerals (e.g., 12,000)
- Preserve the original language of the lecture throughout
- Transcription text only
```
Use when: you want consistent formatting.

#### Level 4 — Lecture Mode with PDF (best quality) ← DEFAULT
```
You are a speech-to-text transcription assistant. You are given a PDF slide
deck and an audio recording of a {subject} university lecture.

## FUNDAMENTAL RULE #1: ORIGINAL LANGUAGE ONLY
**NEVER translate.** If the professor speaks English, output MUST be in English.
If Korean, output in Korean. If mixed, preserve the mix exactly as spoken.
This is NON-NEGOTIABLE. Translating the lecture into another language is a
CRITICAL FAILURE.

## FUNDAMENTAL RULE #2: VERBATIM STT — SPEECH ONLY
This is **STT (Speech-to-Text)**, NOT summarization, NOT note-taking.
Your job is to write down what the professor ACTUALLY SAID, word by word,
preserving their exact phrasing, sentence structure, and speaking style.

**CRITICAL: Do NOT copy-paste text from the PDF slides into the output.**
The PDF is ONLY for identifying which page/slide the professor is discussing.
The OUTPUT must contain ONLY the professor's spoken words.
If the professor reads a slide out loud, transcribe their spoken version
(which may differ from the slide text).

DO NOT:
- Copy or reproduce text/bullet points from the PDF slides
- Translate ANY part of the lecture into another language
- Compress, summarize, or condense the professor's words
- Convert spoken sentences into bullet points
- Skip ANY spoken content — every sentence matters
- Paraphrase or "clean up" the professor's words
- Shorten or truncate long explanations

DO:
- Write EXACTLY what the professor said, sentence by sentence
- Keep their natural speaking style (colloquial, formal, rambling — all of it)
- Include filler words, false starts, self-corrections
- Include EVERY tangent, joke, anecdote, aside, example, and digression
- Produce VERY LONG output — more text is always better than less
- A 10-minute audio should produce at least 2000+ words of transcription

## Page-by-Page Structure (MANDATORY)
- Structure output by PDF page: `## p.{N} — {slide title or topic}`
- Go through EVERY page of the PDF in order
- If the professor skipped a page: `*[No lecture content — slide only]*`
- If the professor talked about a page extensively, write EVERYTHING
- Content spoken BEFORE first slide → `## p.0 — Pre-lecture`
- Content spoken AFTER last slide → `## Closing`

## Beyond the PDF
Capture ALL spoken content not on slides under nearest page with 💬 marker:
- Verbal explanations, intuitions, reasoning
- Real-world examples, case studies, anecdotes
- Tangential context, history, motivation
- Exam tips, common mistakes, warnings
- Q&A with students (both question and answer)
- Administrative announcements

## Output Format
- `---` dividers between page sections
- `## p.{N} — {title}` for EVERY page
- `> ` blockquote for professor's extended examples
- 💬 for beyond-PDF verbal content
- Math in KaTeX: $Y = C + I + G$
- One sentence per line
- Output MUST be LONG — brevity is failure

## Key Terms
{auto-inferred + user-supplied terms}
```

#### Level 5 — Raw Verbatim
```
Transcribe this audio verbatim. Include all speech as-is.
Sentence-level line breaks. No formatting.
```
Use when: need exact wording without page structure (prefer Whisper for this).

### 4. Domain Auto-Inference

When the user provides only a subject title, infer domain terms automatically:

| Title pattern  | Context                       | Auto terms                                 |
| -------------- | ----------------------------- | ------------------------------------------ |
| 경제, 거시경제 | Macroeconomics lecture        | GDP, multiplier, MPC, IS-LM, fiscal policy |
| 물리           | Physics lecture               | Newton's laws, energy conservation, E=mc²  |
| 법학, 헌법     | Law/Constitutional law        | 위헌법률심판, 헌법소원, 기본권             |
| CS, 프로그래밍 | Computer Science              | algorithm, Big-O, data structure           |
| (no match)     | Ask model to infer from title | —                                          |

### 5. Handle Long Audio

| Duration  | Strategy                                |
| --------- | --------------------------------------- |
| < 2 hours | Single request (safe)                   |
| 2–8 hours | Split into 2–4 chunks with 10s overlap  |
| 8+ hours  | 30-minute chunks, sequential processing |

> [!TIP]
> Multiple audio files from the same lecture can be sent in a single request.
> Just add multiple `types.Part.from_bytes()` parts — the model handles them
> as one continuous lecture.

Use `ffmpeg` for splitting when needed:
```bash
DUR=900  # 15 minutes
OVERLAP=10
for i in $(seq 0 $((DUR - OVERLAP)) $(ffprobe -v error -show_entries format=duration -of csv=p=0 input.m4a | cut -d. -f1)); do
  ffmpeg -i input.m4a -ss $i -t $((DUR + OVERLAP)) -y chunk_${i}.mp3
done
```

### 6. API Implementation

#### Client initialization

```python
from google import genai
from google.genai import types
import os

# Vertex AI (service account / ADC) — MUST use location='global'
if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GOOGLE_CLOUD_PROJECT"):
    client = genai.Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id"),
        location="global",  # REQUIRED for gemini-3-* models
    )
# Gemini API (API key)
else:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
```

#### Gemini — Inline bytes (< ~50MB, preferred)

> [!TIP]
> Inline bytes avoids the Korean filename `UnicodeEncodeError` entirely.
> Prefer this path when file size allows.

```python
with open("lecture.m4a", "rb") as f:
    audio_bytes = f.read()

contents = [
    types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp4"),
    prompt_text,
]

# Add PDF if available
if pdf_path:
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    contents.insert(0, types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"))

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=contents,
    config=types.GenerateContentConfig(max_output_tokens=65536),
)
print(response.text)
```

#### Gemini API — Large files (> 50MB): File API upload

> [!WARNING]
> **File API is only available with API key auth, NOT Vertex AI.**
> For Vertex AI with large files, compress with ffmpeg first or use GCS URIs.
>
> **Korean/non-ASCII filenames cause `UnicodeEncodeError`** in `httpx`.
> Always use `_safe_upload()` below to copy to ASCII-safe temp paths first.

```python
import time, shutil, tempfile

def _safe_upload(client, filepath, ascii_name):
    """Upload file with ASCII-safe temp name to avoid httpx UnicodeEncodeError."""
    tmpdir = tempfile.mkdtemp(prefix="stt_")
    try:
        safe_path = os.path.join(tmpdir, ascii_name)
        shutil.copy2(filepath, safe_path)
        return client.files.upload(file=safe_path)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

audio_file = _safe_upload(client, "노시론1.m4a", "lecture.m4a")

from google.genai.types import FileState
while audio_file.state == FileState.PROCESSING:
    time.sleep(2)
    audio_file = client.files.get(name=audio_file.name)

contents = [audio_file]
if pdf_path:
    pdf_file = _safe_upload(client, pdf_path, "slides.pdf")
    contents.insert(0, pdf_file)
contents.append(prompt_text)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=contents,
    config=types.GenerateContentConfig(max_output_tokens=65536),
)
print(response.text)

client.files.delete(name=audio_file.name)
if pdf_path:
    client.files.delete(name=pdf_file.name)
```

#### mlx-whisper — Local fallback (Apple Silicon)

```python
import mlx_whisper

result = mlx_whisper.transcribe(
    "lecture.m4a",
    path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
    language="ko",
)
print(result["text"])
```

#### OpenAI — Diarization support

```python
from openai import OpenAI
client = OpenAI()
with open("lecture.m4a", "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-transcribe", file=f,
        response_format="text", language="ko",
    )
print(transcript)
```

### 7. Output Format

```markdown
# {Subject} — Lecture Notes

- Model: gemini-3-flash-preview (Vertex AI, global)
- Time: {elapsed}s
- Tokens: {in} → {out}
- Source: {audio_file} {+ pdf_file}
- Mode: STT (Level 4, verbatim, original language)

---

{transcribed content}
```

## Anti-Patterns

> [!CAUTION]
> **Never send audio without any prompt to an LLM.**
> Without guidance, the model produces unstructured output with
> hallucination loops. Always provide at minimum a basic transcription prompt.

> [!WARNING]
> **Flash-Lite may copy PDF slide text instead of transcribing speech.**
> Use `gemini-3-flash-preview` for best instruction following.
> If using Flash-Lite, add extra emphasis on "DO NOT copy slide text".

## Model Comparison (Benchmarked 2026-03-09)

| Model                      | Speed       | Verbatim Quality    | Notes                                        |
| -------------------------- | ----------- | ------------------- | -------------------------------------------- |
| **Gemini 3 Flash Preview** | ~50s/44min  | ⭐ Best              | Recommended. Speech-only, follows rules well |
| Gemini 3.1 Flash-Lite      | ~30s/44min  | ⚠️ Copies slide text | Faster but ignores "no-copy" instructions    |
| mlx-whisper turbo          | ~4min local | Good (raw)          | Offline fallback, no page structure          |
| OpenAI gpt-4o-transcribe   | —           | Good                | Diarization support, expensive               |

## Constraints

- PDF slides dramatically improve quality — always include when available
- Term hints should be ≤ 20 terms (too many causes confusion)
- Only include terms that actually appear in the audio (prevents hallucination)
- Korean + English mixing is fine — Gemini handles multilingual natively
- **Language hint**: tell the agent the lecture language explicitly to prevent translation
- **Korean filenames**: Use `_safe_upload()` or inline bytes to avoid `UnicodeEncodeError`
- **Vertex AI**: File API is NOT available. Use inline bytes (< ~50MB) or ffmpeg compress
- **Vertex AI**: Must use `location='global'` for gemini-3-* models

## Dependencies

```bash
# Required
pip install google-genai    # Gemini API + Vertex AI (unified SDK)

# Optional
pip install mlx-whisper     # Local Whisper (Apple Silicon)
pip install openai          # OpenAI diarization
brew install ffmpeg         # Audio splitting for long files

# Vertex AI auth
gcloud auth application-default login  # or set GOOGLE_APPLICATION_CREDENTIALS
```
