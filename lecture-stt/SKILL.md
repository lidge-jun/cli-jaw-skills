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

Convert lecture audio into near-verbatim structured markdown using LLM-based STT.
Leverages **contextual prompting** — PDF slides identify which slide is being discussed,
while output captures only what the professor actually said. Without proper prompting,
models tend to copy-paste slide text instead of transcribing speech.

## Instructions

### 1. Gather Inputs

Required:
- **Audio file** — `.m4a`, `.mp3`, `.wav` (up to ~8 hours)
- **Subject title** — e.g. "거시경제학", "헌법", "Data Structures"

Optional (strongly recommended):
- **PDF slides** — structural guide for page-by-page output
- **Custom terms** — domain-specific proper nouns, acronyms (≤ 20 terms to avoid confusion)
- **Language hint** — explicit lecture language prevents translation errors

### 2. Select Engine

```
GOOGLE_APPLICATION_CREDENTIALS or ADC configured?
├─ Yes → Vertex AI + Gemini 3 Flash Preview (recommended, location='global')
GEMINI_API_KEY exists?
├─ Yes → Gemini API + Gemini 3 Flash Preview (recommended)
│   └─ Fallback: Gemini 3.1 Flash-Lite (faster but may copy slide text)
├─ No, OPENAI_API_KEY exists?
│   └─ Yes → OpenAI gpt-4o-transcribe (supports diarization)
└─ No → mlx-whisper local (Apple Silicon, offline, free)
```

> Vertex AI requires `location='global'` for gemini-3.* models. Using `us-central1` returns 404.

### 3. Build Prompt

Choose prompt level based on available inputs:

#### Level 1 — Basic (no context)
```
Transcribe this audio in its original language. Output transcription only.
```

#### Level 2 — Domain Hints
```
Transcribe this audio in its original language. Output transcription only.

Context: {domain description}
Key Terms: {comma-separated terms}
```

#### Level 3 — Domain + Format
```
Transcribe this audio in its original language.

Context: {domain}
Key Terms: {terms}
Speaker: {speaker info, if known}

Output format:
- Sentence-level line breaks
- Numbers in Arabic numerals (e.g., 12,000)
- Preserve the original language throughout
- Transcription text only
```

#### Level 4 — Lecture Mode with PDF (default, best quality)
```
You are a speech-to-text transcription assistant. You are given a PDF slide
deck and an audio recording of a {subject} university lecture.

## Rule 1: Original Language Only
Never translate. If the professor speaks English, output in English.
If Korean, output in Korean. If mixed, preserve the mix exactly as spoken.

## Rule 2: Verbatim STT — Speech Only
This is STT, not summarization or note-taking.
Write down what the professor actually said, word by word,
preserving their exact phrasing and speaking style.

The PDF is only for identifying which slide is being discussed.
Output only the professor's spoken words.
If the professor reads a slide aloud, transcribe their spoken version
(which may differ from slide text).

- Include filler words, false starts, self-corrections
- Include every tangent, joke, anecdote, aside, and digression
- Keep natural speaking style (colloquial, formal, rambling — all of it)
- A 10-minute audio should produce 2000+ words
- More text is always better than less

## Page-by-Page Structure
- Structure by PDF page: `## p.{N} — {slide title or topic}`
- Go through every page in order
- Skipped pages: `*[No lecture content — slide only]*`
- Content before first slide → `## p.0 — Pre-lecture`
- Content after last slide → `## Closing`

## Beyond the PDF
Capture all off-slide content under nearest page with 💬 marker:
- Verbal explanations, intuitions, reasoning
- Real-world examples, anecdotes, case studies
- Exam tips, common mistakes, warnings
- Q&A with students
- Administrative announcements

## Output Format
- `---` dividers between page sections
- `## p.{N} — {title}` for every page
- `> ` blockquote for extended examples
- 💬 for beyond-PDF verbal content
- Math in KaTeX: $Y = C + I + G$
- One sentence per line

## Key Terms
{auto-inferred + user-supplied terms}
```

#### Level 5 — Raw Verbatim
```
Transcribe this audio verbatim. Include all speech as-is.
Sentence-level line breaks. No formatting.
```
Use when exact wording is needed without page structure (prefer Whisper for this).

### 4. Domain Auto-Inference

When the user provides only a subject title, infer domain terms:

| Title pattern  | Context                | Auto terms                                 |
| -------------- | ---------------------- | ------------------------------------------ |
| 경제, 거시경제 | Macroeconomics         | GDP, multiplier, MPC, IS-LM, fiscal policy |
| 물리           | Physics                | Newton's laws, energy conservation, E=mc²  |
| 법학, 헌법     | Constitutional law     | 위헌법률심판, 헌법소원, 기본권             |
| CS, 프로그래밍 | Computer Science       | algorithm, Big-O, data structure           |
| (no match)     | Ask model to infer     | —                                          |

### 5. Handle Long Audio

| Duration  | Strategy                                |
| --------- | --------------------------------------- |
| < 2 hours | Single request                          |
| 2–8 hours | Split into 2–4 chunks with 10s overlap  |
| 8+ hours  | 30-minute chunks, sequential processing |

Multiple audio files from the same lecture can be sent in a single request —
add multiple `types.Part.from_bytes()` parts.

Split with `ffmpeg` when needed:
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

# Vertex AI (service account / ADC) — location='global' required for gemini-3-*
if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GOOGLE_CLOUD_PROJECT"):
    client = genai.Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id"),
        location="global",
    )
# Gemini API (API key)
else:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
```

#### Gemini — Inline bytes (< ~50MB, preferred)

Inline bytes avoids the Korean filename `UnicodeEncodeError` entirely.

```python
with open("lecture.m4a", "rb") as f:
    audio_bytes = f.read()

contents = [
    types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp4"),
    prompt_text,
]

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

File API is only available with API key auth, not Vertex AI.
Korean/non-ASCII filenames cause `UnicodeEncodeError` in `httpx` — use `_safe_upload()`:

```python
import time, shutil, tempfile

def _safe_upload(client, filepath, ascii_name):
    """Upload with ASCII-safe temp name to avoid httpx UnicodeEncodeError."""
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

- **Never send audio without a prompt** — without guidance, models produce unstructured output with hallucination loops. Always provide at minimum a basic transcription prompt.
- **Flash-Lite may copy slide text** — use `gemini-3-flash-preview` for best instruction following. With Flash-Lite, add extra emphasis on speech-only transcription.

## Model Comparison (Benchmarked 2026-03-09)

| Model                      | Speed       | Verbatim Quality | Notes                                   |
| -------------------------- | ----------- | ---------------- | --------------------------------------- |
| **Gemini 3 Flash Preview** | ~50s/44min  | ⭐ Best           | Recommended. Speech-only, follows rules |
| Gemini 3.1 Flash-Lite      | ~30s/44min  | ⚠️ Copies slides  | Faster but ignores speech-only rules    |
| mlx-whisper turbo          | ~4min local | Good (raw)       | Offline fallback, no page structure     |
| OpenAI gpt-4o-transcribe   | —           | Good             | Diarization support, expensive          |

## Constraints

- PDF slides dramatically improve quality — always include when available
- Only include terms that actually appear in the audio (prevents hallucination)
- Korean + English mixing handled natively by Gemini
- Korean filenames: use `_safe_upload()` or inline bytes to avoid `UnicodeEncodeError`
- Vertex AI: File API unavailable — use inline bytes (< ~50MB) or ffmpeg compression
- Vertex AI: `location='global'` required for gemini-3-* models

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
