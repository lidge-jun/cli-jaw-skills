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
GEMINI_API_KEY exists?
├─ Yes → Gemini 3.1 Flash-Lite (recommended ⭐)
│   └─ Fallback → older Flash-Lite versions
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
You are a lecture note assistant. You are given a PDF slide deck and an audio
recording of a {subject} university lecture.

## Task
1. Transcribe ALL lecture content as detailed as possible — capture every
   explanation, example, and nuance the professor gives.
2. Follow the PDF slide structure (one section per slide) when applicable.
3. Be THOROUGH — include all details, side stories, real-world examples.
4. Include ALL speech: administrative announcements, attendance policies,
   grading info, course logistics, off-topic remarks, jokes, and anecdotes.
   Do NOT skip or summarize any spoken content.

## Supplementary Notes
- If the professor did NOT explain a PDF concept, add *[Supplementary: ...]*

## Language
- Output in the ORIGINAL language of the lecture. Do NOT translate.
- If the lecture mixes languages (e.g., English lecture with Korean asides),
  preserve the mixed-language output as spoken.

## Output Format
- `---` dividers + topic/slide title per section
- Professor's examples in `> ` blockquote — be detailed, capture full reasoning
- Math in KaTeX: $Y = C + I + G$
- Sentence-level line breaks
- Administrative/logistical content under a clear heading (e.g., ## Course Logistics)
- FOCUS boxes, case studies, warnings: include ALL

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

| Duration  | Strategy                                |
| --------- | --------------------------------------- |
| < 2 hours | Single request (safe)                   |
| 2–8 hours | Split into 2–4 chunks with 10s overlap  |
| 8+ hours  | 30-minute chunks, sequential processing |

Use `ffmpeg` for splitting: `ffmpeg -i input.m4a -ss {start} -t {duration} chunk.mp3`

### 6. API Implementation

#### Gemini — Small files (< ~20MB): inline bytes

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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
    model="gemini-3.1-flash-lite-preview",
    contents=contents,
)
print(response.text)
```

#### Gemini — Large files (> 20MB): File API upload

```python
import time

# Upload audio via File API
audio_file = client.files.upload(file="lecture.m4a")
while audio_file.state == "PROCESSING":
    time.sleep(2)
    audio_file = client.files.get(name=audio_file.name)

# Upload PDF if available
contents = [audio_file]
if pdf_path:
    pdf_file = client.files.upload(file=pdf_path)
    contents.insert(0, pdf_file)

contents.append(prompt_text)

response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
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

## Dependencies

```bash
# Required
pip install google-genai    # Gemini API

# Optional
pip install mlx-whisper     # Local Whisper (Apple Silicon)
pip install openai          # OpenAI diarization
brew install ffmpeg         # Audio splitting for long files
```

## Related Research

See `reference/` folder for detailed research documents:
- `01_traditional_stt.md` — Traditional STT architecture (Whisper, Chirp)
- `02_llm_stt.md` — LLM-based STT principles and experiments
- `03_model_comparison.md` — Full benchmark data with pricing
- `04_contextual_prompt.md` — Prompt engineering patterns and anti-patterns
- `05_implementation_plan.md` — CLI tool design (`transcribe.py`)
