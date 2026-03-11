---
name: pdf-expert
description: >
  PDF RAG pipeline: text extraction + Apple Vision OCR + API embedding + cosine search.
  Triggers: "pdf 읽기", "pdf rag", "문서 검색", "pdf 분석", "pdf 청크", "pdf-expert", "pdf 임베딩"
---

# PDF Expert Skill

## When to use
- Large PDF that won't fit in context (100+ pages)
- Scanned/image PDF that needs OCR
- Semantic search across one or multiple PDFs
- Building a personal document knowledge base (NotebookLM-style)

## Quick Reference

| Task | Command |
|------|---------|
| Check text vs scan pages | `python3 <skill>/scripts/pdf_check.py "file.pdf"` |
| Check with custom threshold | `python3 <skill>/scripts/pdf_check.py "file.pdf" --threshold 50 --quality-ratio 0.2` |
| Extract scan pages as PNG | `pdftoppm -png -f 3 -l 3 "file.pdf" /tmp/page_3` |
| OCR images (parallel) | `swift <skill>/scripts/ocr.swift 3 /tmp/page_*.png` |
| Embed → JSON vectors | `python3 <skill>/scripts/pdf_embed.py merged.json "doc_name"` |
| Re-embed (overwrite) | `python3 <skill>/scripts/pdf_embed.py merged.json "doc_name" --force` |
| Semantic search (1 doc) | `python3 <skill>/scripts/pdf_query.py "질문" --file doc_name` |
| Semantic search (all docs) | `python3 <skill>/scripts/pdf_query.py "질문"` |
| Keyword search (free) | `python3 <skill>/scripts/pdf_query.py "키워드" --file doc_name --grep` |
| Column-based OCR (optional) | `python3 <skill>/scripts/ocr_columns.py image.png --cols 3` |

Replace `<skill>` with the absolute path to this skill folder.

## Workflow

### Step 1: Assess PDF (`pdf_check.py`)

```bash
python3 <skill>/scripts/pdf_check.py "/path/to/doc.pdf"
```

Output:
```json
{
  "file": "/absolute/path/to/doc.pdf",
  "total_pages": 10,
  "text_pages": [{"page": 1, "text": "..."}, {"page": 3, "text": "..."}],
  "ocr_pages": [2, 4, 5]
}
```

- `text_pages`: pages with sufficient extractable text
- `ocr_pages`: page numbers that need OCR
- Optional flags: `--threshold N` (min chars, default 100), `--quality-ratio F` (min meaningful line ratio, default 0.3)

### Step 2: Extract OCR page images (`pdftoppm`)

For each page in `ocr_pages`, extract as PNG:

```bash
pdftoppm -png -f 2 -l 2 "/path/to/doc.pdf" /tmp/doc_p2
pdftoppm -png -f 4 -l 4 "/path/to/doc.pdf" /tmp/doc_p4
pdftoppm -png -f 5 -l 5 "/path/to/doc.pdf" /tmp/doc_p5
```

Output files: `/tmp/doc_p2-1.png`, `/tmp/doc_p4-1.png`, `/tmp/doc_p5-1.png`

### Step 3: OCR with Apple Vision (`ocr.swift`)

```bash
swift <skill>/scripts/ocr.swift 3 /tmp/doc_p2-1.png /tmp/doc_p4-1.png /tmp/doc_p5-1.png
```

Output:
```json
[
  {"file": "/tmp/doc_p2-1.png", "text": "OCR result...", "error": null},
  {"file": "/tmp/doc_p4-1.png", "text": "OCR result...", "error": null}
]
```

- First argument is max concurrency (3 recommended for M1 16GB)
- Results sorted by filename
- If `error` is not null, that page's OCR failed — skip or retry

### Step 4: Merge & Embed (`pdf_embed.py`)

**Merge the outputs** from Step 1 and Step 3 into a single JSON file:

```json
[
  {"page": 1, "text": "text from pdf_check", "source": "/path/to/doc.pdf"},
  {"page": 2, "text": "text from ocr.swift", "source": "/path/to/doc.pdf"},
  {"page": 3, "text": "text from pdf_check", "source": "/path/to/doc.pdf", "tables": [["h1","h2"],["v1","v2"]]}
]
```

**How to merge:**
- `text_pages` from Step 1 → use `page` and `text` directly
- `ocr.swift` results from Step 3 → extract page number from filename (e.g., `doc_p2-1.png` → page 2)
- Skip entries where `error` is not null
- `tables` field is optional — if you want table-aware search, extract tables with `pdfplumber`'s `page.extract_tables()` and include them. `pdf_embed.py` will create separate chunks for each table.
- `source` should be the original PDF path

Save as `/tmp/merged.json`, then embed:

```bash
python3 <skill>/scripts/pdf_embed.py /tmp/merged.json "my_document"
```

Output: `~/.cli-jaw/vectors/my_document.vectors.json`

If the file already exists, it skips (PDF is static → no incremental update needed). Use `--force` to re-embed.

### Step 5: Query (`pdf_query.py`)

**Semantic search** (requires 1 API call for query embedding):
```bash
python3 <skill>/scripts/pdf_query.py "5G 요금제 가격이 얼마야?" --file my_document
```

**Keyword search** (no API call, free):
```bash
python3 <skill>/scripts/pdf_query.py "NPV" --file my_document --grep
```

**Search all documents** (omit `--file`):
```bash
python3 <skill>/scripts/pdf_query.py "계약 해지 조건"
```

**Adjust result count** with `--n`:
```bash
python3 <skill>/scripts/pdf_query.py "질문" --file my_document --n 10
```

## Storage

```
~/.cli-jaw/vectors/
├── air_프로모션.vectors.json
├── 계약서_2026.vectors.json
└── 기출문제_수학.vectors.json
```

Each `.vectors.json` contains embedded chunks with vectors, text, page numbers, and metadata. Embedding is done once; all subsequent searches are free (local cosine similarity). Only query embedding costs 1 API call.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMBEDDING_PROVIDER` | No | `gemini` | `gemini`, `openai`, or `vertex` |
| `GEMINI_API_KEY` | When provider=gemini | — | Google AI API key |
| `OPENAI_API_KEY` | When provider=openai | — | OpenAI API key |
| `EMBEDDING_MODEL` | No | Provider-dependent* | Embedding model name |
| `EMBEDDING_BATCH_SIZE` | No | `50` | Texts per API call |
| `VERTEX_PROJECT` | When provider=vertex | ADC auto-detect | GCP project ID |
| `VERTEX_LOCATION` | When provider=vertex | `us-central1` | GCP region |
| `EMBEDDING_DIM` | When provider=vertex | `0` (full) | Output dimensionality |

*`EMBEDDING_MODEL` defaults:
- gemini → `gemini-embedding-001`
- openai → `text-embedding-3-small`
- vertex → `gemini-embedding-001`

## Dependencies

| Package | Required by | Install |
|---------|-------------|---------|
| `pdfplumber` | pdf_check.py | `pip install pdfplumber` |
| `google-auth` | _embedding.py (Vertex only) | `pip install google-auth` |
| `Pillow` | ocr_columns.py only | `pip install Pillow` |
| Xcode CLT (Swift) | ocr.swift | Usually pre-installed on macOS |
| `poppler` (pdftoppm) | Step 2 image extraction | `brew install poppler` |

Gemini and OpenAI providers use stdlib `urllib` only — no extra packages needed.

## Optional: Column-based OCR (`ocr_columns.py`)

For images with column layouts (tables, multi-column documents):

```bash
python3 <skill>/scripts/ocr_columns.py image.png --cols 3 --header-px 100
```

Splits image into columns (and optional header), OCRs each part separately, returns combined result. Requires `Pillow`.

| Flag | Default | Description |
|------|---------|-------------|
| `--cols N` | 5 | Number of columns |
| `--header-px N` | 0 | Header height in pixels to extract separately |
| `--output` | json | `json` or `text` |

## Constraints

- **M1 concurrency**: Do not exceed 4 for `ocr.swift` concurrency on M1 16GB. Recommended: 3.
- **OCR languages**: `ocr.swift` is hardcoded to Korean (`ko-KR`) and English (`en-US`). Other languages may produce inaccurate results.
- **Cleanup**: Delete temporary PNG files and merged JSON from `/tmp/` after embedding.
