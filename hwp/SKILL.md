---
name: hwp
description: "HWP/HWPX create, read, edit, review. Triggers: 한글, .hwp, .hwpx, HWP, HWPX, Korean documents."
---

# HWP Skill

Use this skill for any .hwp / .hwpx task: create, read, edit, or manipulate Hangul Word Processor documents.
Triggers: "한글", ".hwp", ".hwpx", "HWP", "HWPX", Korean documents, 한컴오피스.
Covers: HWPX creation (python-hwpx), reading both HWP/HWPX, editing via XML workflow, visual QA, CJK/Korean handling.
Do NOT use for: DOCX, PDFs, spreadsheets, or Google Docs.

---

## Quick Reference

| Task        | Tool                                                 |
| ----------- | ---------------------------------------------------- |
| **Create**  | `python-hwpx` (pip) — Pure Python                    |
| **Read**    | `hwp-hwpx-parser` or `hwpparser text`                |
| **Edit**    | Unpack → XML Edit → Pack (HWPX is ZIP+XML)           |
| **Convert** | `hwpparser convert` (HWP→Text/HTML/ODT/PDF, MD→HWPX) |
| **Review**  | soffice → PDF → pdftoppm → image inspection          |

### Format Overview

| Format | Extension | Structure            | Read | Write | Notes                  |
| ------ | --------- | -------------------- | ---- | ----- | ---------------------- |
| HWPX   | `.hwpx`   | ZIP + XML (OWPML)    | ✅    | ✅     | Modern, cross-platform |
| HWP    | `.hwp`    | OLE2 compound binary | ✅    | ❌     | Legacy v5 format       |

> **HWPX = DOCX equivalent** — same ZIP+XML pattern. Unpack/pack workflows transfer directly from DOCX skill.

### Converting .hwp to .hwpx

Legacy `.hwp` files should be converted via 한컴오피스 or `hwpparser`:

```bash
hwpparser convert document.hwp output.hwpx
```

### Converting to Images

```bash
soffice --headless --convert-to pdf document.hwpx
pdftoppm -jpeg -r 150 document.pdf page
```

---

## Creating Documents: python-hwpx

> [python-hwpx GitHub](https://github.com/airmang/python-hwpx) — MIT License
> Only dependency: `lxml`

```bash
pip install python-hwpx
```

### Basic Structure

```python
from hwpx import HwpxDocument

# Create new blank document
doc = HwpxDocument.new()

# Add paragraphs
doc.add_paragraph("python-hwpx로 생성한 문단입니다.")

# Save
doc.save_to_path("output.hwpx")
```

### Opening Existing Documents

```python
# File path
doc = HwpxDocument.open("보고서.hwpx")

# Context manager (recommended)
with HwpxDocument.open("보고서.hwpx") as doc:
    doc.add_paragraph("새 내용 추가")
    doc.save_to_path("수정본.hwpx")

# From bytes
import io
doc = HwpxDocument.open(io.BytesIO(hwpx_bytes))
```

### Tables

```python
# Create N×M table
table = doc.add_table(rows=3, cols=4)

# Set cell text
table.set_cell_text(0, 0, "이름")
table.set_cell_text(0, 1, "부서")
table.set_cell_text(0, 2, "직급")
table.set_cell_text(0, 3, "연락처")

# Fill data rows
table.set_cell_text(1, 0, "김철수")
table.set_cell_text(1, 1, "개발팀")

# Merge cells: (row1, col1) to (row2, col2)
table.merge_cells(0, 0, 1, 1)
table.set_cell_text(0, 0, "병합된 셀", logical=True, split_merged=True)

# Get table dimensions
print(f"Rows: {table.row_count}, Cols: {table.col_count}")
```

### Text Runs (Formatted Text)

```python
# Add bold, underline run
paragraph = doc.paragraphs[0]
paragraph.add_run("굵은 텍스트", bold=True)
paragraph.add_run("밑줄 텍스트", underline=True)

# Italic existing run
run = paragraph.runs[0]
run.set_italic(True)

# Text color
run.set_color("#FF0000")
```

### Memos (Comments)

```python
# Add memo anchored to paragraph
paragraph = doc.paragraphs[0]
doc.add_memo_with_anchor("검토 필요", paragraph=paragraph)

# Find and delete memos
memos = list(doc.memos)
for memo in memos:
    if "삭제대상" in memo.text:
        doc.remove_memo(memo)
```

### Sections

```python
# Add section at end
new_section = doc.add_section()
new_section.add_paragraph("두 번째 섹션 내용")

# Insert section at specific position
doc.add_section(after=0)  # After first section

# Delete section
doc.remove_section(1)
```

### Headers & Footers

```python
# Set header/footer text
doc.set_header_text("기밀 문서", page_type="BOTH")
doc.set_footer_text("— 1 —", page_type="BOTH")

# Odd/even pages
doc.set_header_text("홀수 페이지", page_type="ODD")
doc.set_footer_text("짝수 페이지", page_type="EVEN")

# Remove header
doc.remove_header(page_type="BOTH")
```

### Footnotes & Bookmarks

```python
# Add footnote
doc.add_footnote(paragraph, "각주 텍스트")

# Add bookmark
doc.add_bookmark("bookmark_name", paragraph)

# Add hyperlink
doc.add_hyperlink("https://example.com", paragraph, "링크 텍스트")
```

### Page Layout

```python
# Check page size
section = doc.sections[0]
print(f"Width: {section.page_width}, Height: {section.page_height}")

# Switch to landscape
section.set_landscape()

# Adjust margins
section.set_margins(top=2000, bottom=2000, left=1500, right=1500)

# Multi-column layout
section.set_columns(count=2, gap=1000)
```

### Text Search & Replace

```python
# Simple text replacement
doc.replace_text("임시", "확정")

# Style-based replacement (replace only red text)
doc.replace_text_in_runs(
    "임시", "확정",
    text_color="#FF0000",
)

# Find runs by style
underlined = doc.find_runs_by_style(underline_type="SINGLE")
```

### Export

```python
# Export to different formats
text = doc.export_text()
html = doc.export_html()
md   = doc.export_markdown()
```

### Schema Validation

```bash
# CLI validation
hwpx-validate document.hwpx
```

```python
# Programmatic validation
from hwpx.tools.validator import validate
result = validate("document.hwpx")
```

### Low-Level XML Access

```python
# Header references
doc.border_fills    # Border/fill styles
doc.bullets         # Bullet definitions
doc.styles          # Style definitions
doc.track_changes   # Change tracking

# Master pages, history, version
doc.master_pages
doc.histories
doc.version
```

---

## Reading Documents

### python-hwpx (HWPX only)

```python
from hwpx import TextExtractor, ObjectFinder

# Text extraction
for section in TextExtractor("문서.hwpx"):
    for para in section.paragraphs:
        print(para.text)

# Object search
for obj in ObjectFinder("문서.hwpx").find("tbl"):
    print(obj.tag, obj.attributes)
```

### hwp-hwpx-parser (HWP + HWPX)

```bash
pip install hwp-hwpx-parser
```

```python
from hwp_hwpx_parser import Reader

# Unified reader for both formats
with Reader("document.hwp") as r:
    print(r.text)                    # Plain text
    print(r.tables)                  # Table list
    print(r.get_memos())             # Memo list

# Tables as Markdown
with Reader("document.hwpx") as r:
    print(r.get_tables_as_markdown())

# Full extraction with notes
with Reader("document.hwp") as r:
    result = r.extract_text_with_notes()
    print(result.text)       # Body (footnotes as [^1], endnotes as [^e1])
    print(result.footnotes)  # List[NoteData]
    print(result.endnotes)   # List[NoteData]
    print(result.memos)      # List[MemoData]

# Image extraction
with Reader("document.hwp") as r:
    for img in r.get_images():
        with open(img.filename, "wb") as f:
            f.write(img.data)
```

### hwpparser (CLI + Python API)

```bash
pip install hwpparser
```

```bash
# Text extraction
hwpparser text document.hwp

# Format conversion
hwpparser convert document.hwp output.txt
hwpparser convert document.hwp output.html
hwpparser convert document.hwp output.pdf

# Markdown → HWPX
hwpparser convert document.md output.hwpx

# Batch conversion
hwpparser batch ./hwp_files/ -f text -o ./output/
```

```python
import hwpparser

# Read HWP
doc = hwpparser.read_hwp("document.hwp")
print(doc.text)   # Plain text
print(doc.html)   # HTML

# Convert
hwpparser.convert("input.hwp", "output.pdf")
hwpparser.markdown_to_hwpx("# 제목\n내용", "output.hwpx")

# RAG chunking
chunks = hwpparser.hwp_to_chunks("document.hwp", chunk_size=1000)

# LangChain loader
from hwpparser import HWPLoader
loader = HWPLoader("document.hwp")
docs = loader.load()
```

> ⚠️ `hwpparser` depends on `pyhwp` (AGPL v3). Be aware of copyleft license implications for production services.

---

## Editing: OWPML Direct Edit Workflow

For modifying existing .hwpx files: Unpack → XML edit → Pack (same 3-step pattern as DOCX).

### HWPX File Structure (OWPML)

```
unpacked/
├── META-INF/
│   └── container.xml         ← OPC container manifest
├── Contents/
│   ├── header.xml            ← Document-level settings (fonts, styles, numbering)
│   ├── content.hpf           ← Content manifest (section list)
│   ├── section0.xml          ← First section (paragraphs, runs, text)
│   ├── section1.xml          ← Additional sections
│   └── BinData/              ← Embedded images and binary resources
├── Preview/
│   ├── PrvText.txt           ← Text preview
│   └── PrvImage.png          ← Thumbnail preview
└── version.xml               ← Version metadata
```

### XML Hierarchy

```
본문 → 구역 <sec> → 문단 <hp:p> → 런 <hp:run> → 텍스트 <hp:t>
```

| Element        | Namespace                | Purpose                                 |
| -------------- | ------------------------ | --------------------------------------- |
| `<sec>`        | `owpml/2024/section`     | Section (page layout unit)              |
| `<hp:p>`       | `owpml/2024/paragraph`   | Paragraph                               |
| `<hp:run>`     | `owpml/2024/paragraph`   | Run (text + formatting)                 |
| `<hp:t>`       | `owpml/2024/paragraph`   | Text node                               |
| `<secPr>`      | `owpml/2024/section`     | Section properties (page size, margins) |
| `<head>`       | `owpml/2024/head`        | Header (fonts, styles, numbering)       |
| `<masterPage>` | `owpml/2024/master-page` | Master page (headers/footers)           |

### Workflow

```bash
# 1. Unpack (HWPX is just a ZIP)
python -c "
import zipfile, os, sys
with zipfile.ZipFile('document.hwpx', 'r') as z:
    z.extractall('unpacked/')
"

# 2. Check text content
pip install hwp-hwpx-parser
python -c "
from hwp_hwpx_parser import Reader
with Reader('document.hwpx') as r:
    print(r.text)
"

# 3. Edit XML (Contents/section0.xml etc. using Edit tool)
#    Use the Edit tool directly for string replacement. Do not write Python scripts.

# 4. Repack
python -c "
import zipfile, os
with zipfile.ZipFile('output.hwpx', 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk('unpacked/'):
        for f in files:
            filepath = os.path.join(root, f)
            arcname = os.path.relpath(filepath, 'unpacked/')
            z.write(filepath, arcname)
"
```

### XML Editing Rules

- **Use python-hwpx API first** — direct XML editing only when API doesn't cover your use case
- **Preserve namespace prefixes** — OWPML uses `hp:`, `hc:`, `ha:` etc.
- **Maintain manifest** — `content.hpf` must list all sections; update when adding/removing sections
- **Section ordering** — sections are numbered `section0.xml`, `section1.xml`, etc.
- **Binary resources** — images go in `Contents/BinData/`, referenced by `<hp:binItem>` in header.xml

### Template Preservation

```python
# Best approach: use python-hwpx API for placeholder replacement
with HwpxDocument.open("template.hwpx") as doc:
    doc.replace_text("{{제목}}", "실제 제목")
    doc.replace_text("{{날짜}}", "2026-03-08")
    doc.replace_text("{{내용}}", "본문 텍스트")
    doc.save_to_path("filled.hwpx")
```

Rules:
- Never alter styles, formatting, or structure beyond what was requested
- Never modify `<charPr>` (character properties) — preserves fonts, colors, sizes
- Never delete existing numbering definitions or style references
- When extending tables, verify existing cell merge patterns first

---

## Anti-Patterns

| ❌ Don't                         | ✅ Do Instead                                 | Why                                |
| ------------------------------- | -------------------------------------------- | ---------------------------------- |
| Edit .hwp binary directly       | Convert to .hwpx first, or use read-only API | HWP is OLE2 compound, not editable |
| Manual ZIP with wrong structure | Use `python-hwpx` save methods               | Missing manifest breaks file       |
| Ignore namespace prefixes       | Preserve `hp:`, `hc:`, `ha:` prefixes        | Parser fails on wrong namespaces   |
| Use pyhwpx (COM automation)     | Use python-hwpx (Pure Python)                | pyhwpx requires Windows + 한/글    |
| Hardcode section filenames      | Read from `content.hpf` manifest             | Section naming may vary            |
| Skip validation after editing   | Run `hwpx-validate` or open in 한/글         | Silent corruption is common        |
| Forget to update content.hpf    | Always sync manifest when adding sections    | Missing sections won't render      |

---

## CJK / Korean Text Handling

HWPX is natively Korean — CJK handling is built into the format specification.

### Native Korean Attributes

OWPML includes Korean text handling attributes by default:

```xml
<!-- In section XML: paragraph properties -->
<hp:paraPr>
  <hc:autoSpaceEAsianEng>true</hc:autoSpaceEAsianEng>
  <hc:autoSpaceEAsianNum>true</hc:autoSpaceEAsianNum>
</hp:paraPr>
```

| Attribute            | Default | Effect                                           |
| -------------------- | ------- | ------------------------------------------------ |
| `autoSpaceEAsianEng` | true    | Automatic spacing between Korean and Latin       |
| `autoSpaceEAsianNum` | true    | Automatic spacing between Korean and digits      |
| `wordWrap`           | Korean  | Korean syllable-level line breaking enabled      |
| `kinsoku`            | true    | Prevents forbidden characters at line boundaries |

### Korean Fonts

```python
# python-hwpx: fonts defined in header.xml style references
# Default Korean fonts in HWPX:
# - 함초롬바탕 (HCR Batang) — default serif
# - 함초롬돋움 (HCR Dotum) — default sans
# - 맑은 고딕 (Malgun Gothic) — Windows
# - Noto Sans KR — cross-platform
```

Recommended fonts:

| Font          | License   | Cross-platform | Best for          |
| ------------- | --------- | -------------- | ----------------- |
| Noto Sans KR  | OFL       | Win/Mac/Linux  | Safest choice     |
| Pretendard    | OFL       | Win/Mac/Linux  | Modern UI         |
| 함초롬바탕    | Hancom    | Hancom only    | Default HWP serif |
| 함초롬돋움    | Hancom    | Hancom only    | Default HWP sans  |
| Malgun Gothic | MS bundle | Windows only   | Windows-only docs |
| NanumGothic   | OFL       | Win/Mac/Linux  | General Korean    |

### CJK QA Checklist

After rendering, check these CJK-specific items:
- [ ] Korean text not truncated at boundaries
- [ ] Line breaks at natural positions (syllable boundaries, not mid-character)
- [ ] No kinsoku violations (closing punctuation at line start)
- [ ] Korean-Latin mixed text has proper spacing
- [ ] Font renders as intended (no fallback glyphs)
- [ ] Table columns wide enough for Korean content

---

## QA Verification Loop (MANDATORY)

**First render almost always has issues. QA is bug hunting, not confirmation.**

### Step 1: Content QA

```bash
# Check text content via hwp-hwpx-parser
pip install hwp-hwpx-parser
python -c "
from hwp_hwpx_parser import Reader
with Reader('output.hwpx') as r:
    print(r.text)
"

# Or via python-hwpx
python -c "
from hwpx import HwpxDocument
doc = HwpxDocument.open('output.hwpx')
print(doc.export_text())
"

# Check for placeholder remnants
python -c "
from hwp_hwpx_parser import Reader
with Reader('output.hwpx') as r:
    text = r.text
    import re
    remnants = re.findall(r'{{.*?}}|xxxx|lorem|ipsum|placeholder|TODO', text, re.I)
    if remnants: print('REMNANTS FOUND:', remnants)
    else: print('Clean — no placeholders found')
"
```

### Step 2: Structural Validation

```bash
# Schema validation
hwpx-validate output.hwpx

# ZIP integrity
python -c "
import zipfile
with zipfile.ZipFile('output.hwpx') as z:
    result = z.testzip()
    print('ZIP OK' if result is None else f'CORRUPT: {result}')
"
```

### Step 3: Visual QA

```bash
soffice --headless --convert-to pdf output.hwpx
pdftoppm -jpeg -r 150 output.pdf page
```

**⚠️ USE SUBAGENTS** — even for 2-3 pages. Fresh eyes catch what you'll miss.

**Subagent prompt template for visual inspection:**

```
Visually inspect these HWP document pages. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words)
- Text overflow or cut off at edges
- Table cell content truncated
- Uneven gaps or inconsistent spacing
- Insufficient margin from page edges
- Low-contrast text
- Leftover placeholder content ({{...}})
- Korean text rendering issues (fallback fonts, broken syllables)

CJK/Korean specific checks:
- Korean text truncated at text box right boundary?
- Unnatural syllable-level line breaks (kinsoku violations)?
- Font rendering as intended (no DroidSans fallback)?
- Korean-Latin mixed text spacing adequate?
- Table/chart column headers wide enough for Korean content?

For each page, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/page-01.jpg (Expected: [brief description])
2. /path/to/page-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### Step 4: Fix & Re-verify

1. Find issue → fix
2. Re-render only the fixed page: `pdftoppm -jpeg -r 150 -f N -l N output.pdf page-fixed`
3. Re-inspect — one fix often creates another problem
4. **Never declare completion before at least 1 fix-and-verify cycle**

---

## Accessibility

| Requirement       | Standard          | Implementation                          |
| ----------------- | ----------------- | --------------------------------------- |
| Color contrast    | >= 4.5:1          | Check text vs background colors         |
| Image alt text    | Required on all   | Add `<hp:altText>` on picture objects   |
| Minimum font size | >= 10pt           | No captions below 10pt                  |
| Language metadata | `lang="ko-KR"`    | Built-in for HWPX                       |
| Heading hierarchy | Sequential levels | Use numbered outline level styles       |
| Reading order     | Logical flow      | Section/paragraph order = reading order |

---

## Dependencies

```bash
# HWPX create/edit (Pure Python, MIT)
pip install python-hwpx

# HWP/HWPX reading (Pure Python, Apache 2.0)
pip install hwp-hwpx-parser

# HWP conversion + CLI (MIT, but AGPL dependency)
pip install hwpparser

# PDF conversion & visual QA
# LibreOffice (soffice)
# Poppler (pdftoppm)
```

---

## Library Tier Guide

### Tier 1 — Primary Tools

| Library         | Use For                       | License        | Lang   |
| --------------- | ----------------------------- | -------------- | ------ |
| python-hwpx     | HWPX create/edit/read         | MIT            | Python |
| hwp-hwpx-parser | HWP+HWPX text extraction      | Apache 2.0     | Python |
| hwpparser       | CLI conversion + HWPX from MD | MIT (AGPL dep) | Python |

### Tier 2 — Specialized

| Library | Use For                                   | License    | Lang              |
| ------- | ----------------------------------------- | ---------- | ----------------- |
| unhwp   | HWP/HWPX → Markdown (fast)                | MIT        | Rust + Python FFI |
| hwpers  | HWP reading + SVG rendering + HWP writing | MIT/Apache | Rust              |
| pyhwp   | Legacy HWP v5 parsing                     | AGPL v3    | Python            |

### Tier 3 — Niche

| Library        | Use For                            | License    | Lang   |
| -------------- | ---------------------------------- | ---------- | ------ |
| hwp-extract    | Password-protected HWP extraction  | MIT        | Python |
| openhwp        | Rust HWP/HWPX + IR conversion      | MIT        | Rust   |
| hwp-rs         | Low-level Rust HWP parser          | Apache 2.0 | Rust   |
| pyhwpx         | Lightweight HWPX parser            | MIT        | Python |
| python_hwp     | ML data extraction from HWP        | MIT        | Python |
| bob-hwp-parser | HWP JS macro extraction (security) | MIT        | Python |
