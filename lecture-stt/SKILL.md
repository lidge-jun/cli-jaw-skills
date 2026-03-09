---
name: lecture-stt
description: >
  Transcribe audio lectures into structured markdown notes using LLM-based STT
  (Gemini Flash-Lite) with contextual prompting. Supports PDF slide guides,
  domain-aware term hints, and local Whisper fallback.
  Triggers: "강의 전사", "STT", "lecture transcription", "오디오 전사",
  "강의 녹음", "audio to text", "lecture notes", "음성 변환",
  "녹음 텍스트", "전사해줘", "transcribe", "whisper"
---

# Lecture STT Skill

## Goal

Convert lecture audio recordings into structured, high-quality markdown notes
using LLM-based Speech-to-Text. The skill leverages **contextual prompting**
(domain hints, PDF slides, format instructions) to produce notes that are
22x more compressed and 9x faster than raw transcription.

## Key Insight

LLM STT is NOT dictation — it is **speech → structured knowledge conversion**.
Providing a PDF slide deck as structural guide and domain-specific term hints
dramatically improves quality, speed, and cost.

## Instructions

### 1. Gather Inputs

Required:
- **Audio file** — `.m4a`, `.mp3`, `.wav` (up to ~8 hours for Gemini)
- **Subject title** — e.g. "거시경제학", "헌법", "Data Structures"

Optional (but strongly recommended):
- **PDF slides** — acts as structural guide → 22x output compression
- **Custom terms** — domain-specific proper nouns, acronyms

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
Use when: need filler words, exact wording (prefer Whisper for this).

### 4. Domain Auto-Inference

When the user provides only a subject title, infer domain terms automatically:

| Title pattern  | Context                                                  | Auto terms                                 |
| -------------- | -------------------------------------------------------- | ------------------------------------------ |
| 경제, 거시경제 | Macroeconomics lecture                                   | GDP, multiplier, MPC, IS-LM, fiscal policy |
| 물리           | Physics lecture                                          | Newton's laws, energy conservation, E=mc²  |
| 법학, 헌법     | Law/Constitutional law                                   | 위헌법률심판, 헌법소원, 기본권             |
| CS, 프로그래밍 | Computer Science                                         | algorithm, Big-O, data structure           |
| (no match)     | Ask Gemini to infer domain from title (1 preflight call) | —                                          |

### 5. Handle Long Audio

#### Gemini API (API key)

| Duration  | Strategy                                |
| --------- | --------------------------------------- |
| < 2 hours | Single request (safe)                   |
| 2–8 hours | Split into 2–4 chunks with 10s overlap  |
| 8+ hours  | 30-minute chunks, sequential processing |

#### Vertex AI (service account)

> [!WARNING]
> Vertex AI Flash-Lite has `max_output_tokens=8192` limit.
> Even 48-minute lectures get truncated in a single request.

| Duration  | Strategy                                     |
| --------- | -------------------------------------------- |
| < 15 min  | Single request with `max_output_tokens=8192` |
| 15-60 min | 15-min chunks with 10s overlap               |
| 1-8 hours | 15-min chunks, sequential processing         |

Use `ffmpeg` for splitting:
```bash
# Split into 15-min chunks with 10s overlap
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

# Vertex AI (service account / ADC)
# IMPORTANT: gemini-3.1-* models require location='global', NOT 'us-central1'
if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GOOGLE_CLOUD_PROJECT"):
    client = genai.Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    )
# Gemini API (API key)
else:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
```

#### Gemini — Small files (< ~50MB): inline bytes

> [!TIP]
> Inline bytes avoids the Korean filename `UnicodeEncodeError` entirely.
> Prefer this path when file size allows.

```python
# Read audio
with open("lecture.m4a", "rb") as f:
    audio_bytes = f.read()

# Build contents list
contents = [
    types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp4"),
    prompt_text,  # your Level 1–5 prompt string
]

# If PDF slides available, add them too
if pdf_path:
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    contents.insert(0, types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"))

response = client.models.generate_content(
    model="gemini-3-flash-preview",  # recommended; flash-lite may copy slide text
    contents=contents,
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
import time
import shutil
import tempfile

def _safe_upload(client, filepath, ascii_name):
    """Upload file with ASCII-safe temp name to avoid httpx UnicodeEncodeError.
    
    The google-genai File API passes the filename in HTTP headers.
    httpx encodes header values as ASCII, which fails on Korean/CJK filenames.
    Workaround: copy to a temp file with an ASCII-safe name before uploading.
    """
    tmpdir = tempfile.mkdtemp(prefix="stt_")
    try:
        safe_path = os.path.join(tmpdir, ascii_name)
        shutil.copy2(filepath, safe_path)
        return client.files.upload(file=safe_path)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

# Upload audio via File API (ASCII-safe)
audio_file = _safe_upload(client, "노시론1.m4a", "lecture.m4a")

# Wait for processing (state is an enum, not a string)
from google.genai.types import FileState
while audio_file.state == FileState.PROCESSING:
    time.sleep(2)
    audio_file = client.files.get(name=audio_file.name)

# Upload PDF if available
contents = [audio_file]
if pdf_path:
    pdf_file = _safe_upload(client, pdf_path, "slides.pdf")
    contents.insert(0, pdf_file)

contents.append(prompt_text)

response = client.models.generate_content(
    model="gemini-3-flash-preview",  # recommended; flash-lite may copy slide text
    contents=contents,
)
print(response.text)

# Cleanup uploaded files
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
        model="gpt-4o-transcribe",
        file=f,
        response_format="text",
        language="ko",
    )
print(transcript)
```

### 7. Output Format

```markdown
# {Subject} — Lecture Notes

- Model: Gemini 3.1 Flash-Lite
- Time: {elapsed}s
- Tokens: {in} → {out}
- Cost: ~${cost}
- Source: {audio_file} {+ pdf_file}
- Mode: {lecture|raw}

---

{transcribed content}
```

## Anti-Patterns

> [!CAUTION]
> **Never ask the model to preserve filler words** ("Mark (uh), (um), (okay)")
> This switches the LLM into verbatim mode, destroying its structuring ability:
> - Output explodes 23x (13KB → 297KB)
> - Speed drops 8x (20s → 161s)
> - All structure, KaTeX, and slide grouping is lost
> - Repetition loops occur at the end
>
> If you need fillers, use a dedicated STT engine (Whisper) instead.

> [!WARNING]
> **Never send audio without any prompt to an LLM.**
> Without guidance, the model produces 283KB of unstructured output with
> hallucination loops. Always provide at minimum a basic transcription prompt.

## Model Comparison (Benchmarked 2026-03-04)

| Model                     | Speed (44min) | Cost/1000min | Korean quality | Notes               |
| ------------------------- | ------------- | ------------ | -------------- | ------------------- |
| **Gemini 3.1 Flash-Lite** | 3.5s/min ⭐    | ~$0.63       | ~10% CER       | Recommended         |
| mlx-whisper turbo         | 14s/min       | $0 (local)   | ~11% CER       | Offline fallback    |
| OpenAI transcribe         | —             | $6.00        | —              | Diarization support |
| Google Chirp V2           | —             | $16.00       | —              | Too expensive       |

## Cost Reference

44-minute lecture, single pass:
- Gemini 3.1 Flash-Lite: **~$0.03 (₩36)** — 86K input → 4.7K output tokens
- mlx-whisper: **$0** (local processing, ~4 min on Apple Silicon)

## Constraints

- PDF slides dramatically improve quality — always include when available
- Term hints should be ≤ 20 terms (too many causes confusion)
- Only include terms that actually appear in the audio (prevents hallucination)
- Korean + English mixing is fine — Gemini handles multilingual natively
- Speaker name hints prevent name misrecognition
- `--supplement` flag adds *[Supplementary: ...]* for unexplained PDF concepts
- **Korean/non-ASCII filenames**: File API upload fails with `UnicodeEncodeError`.
  Use `_safe_upload()` helper or inline bytes (`types.Part.from_bytes`) to avoid.
  For shell commands, prefer `find`/`glob.glob()` over `ls`/`stat` (which may hang on Korean paths).
- **Vertex AI**: File API (`client.files.upload`) is NOT available.
  Use inline bytes (< ~50MB) or compress with ffmpeg. `max_output_tokens` capped at 8192.

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

## Related Research

See `reference/` folder for detailed research documents:
- `01_traditional_stt.md` — Traditional STT architecture (Whisper, Chirp)
- `02_llm_stt.md` — LLM-based STT principles and experiments
- `03_model_comparison.md` — Full benchmark data with pricing
- `04_contextual_prompt.md` — Prompt engineering patterns and anti-patterns
- `05_implementation_plan.md` — CLI tool design (`transcribe.py`)
