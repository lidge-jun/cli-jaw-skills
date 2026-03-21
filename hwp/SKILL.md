---
name: hwp
description: "HWP/HWPX create, read, edit, review. Triggers: 한글, .hwp, .hwpx, HWP, HWPX, Korean documents."
---

# HWP/HWPX Document Skill

Create, read, edit, and validate Hancom Office HWP 5.0 (binary) and HWPX (ZIP+XML) files.
HWPX uses **XML-first direct editing**; HWP uses **read + convert strategy**.

Triggers: "한글", ".hwp", ".hwpx", "HWP", "HWPX", Korean documents, 한컴오피스, OWPML.

---

## Quick Reference

| Task | Tool / Command |
|------|----------------|
| **Detect format** | `file doc.hwpx` → ZIP = HWPX, "HWP Document" = HWP 5.0 |
| **Create HWPX** | `python-hwpx` API or `build_hwpx.py` (template-based) |
| **Read HWPX** | `hwpx_cli.py text input.hwpx` or `text_extract.py` |
| **Read HWP** | `hwp5proc xml input.hwp` + pipe to python for text extraction |
| **Edit HWPX** | unpack → pretty-print → Edit → pack (auto strip+minify) |
| **Search/Replace** | `hwpx_cli.py search` / `replace` / `batch-replace` |
| **Tables** | `hwpx_cli.py tables` / `fill-table` (path-based) |
| **Content QA** | `hwpx_cli.py content-check` (keyword scan) |
| **Upgrade HWP** | `hwp_convert.py input.hwp output.hwpx` |
| **Validate** | `hwpx_cli.py validate` + `hwpx_cli.py page-guard` |
| **HWPX → PDF** | `soffice --headless --convert-to pdf` (needs H2Orestart+Java) |
| **Visual QA** | PDF → `pdftoppm -jpeg -r 150` → subagent inspection |

### Unified CLI (`hwpx_cli.py`)

```bash
python scripts/hwpx_cli.py open input.hwpx work/           # unpack + pretty-print
python scripts/hwpx_cli.py save work/ output.hwpx           # minify + strip + pack (atomic)
python scripts/hwpx_cli.py text input.hwpx                  # extract text
python scripts/hwpx_cli.py search input.hwpx "pattern"      # regex search
python scripts/hwpx_cli.py replace input.hwpx "old" "new" -o out.hwpx
python scripts/hwpx_cli.py batch-replace input.hwpx map.json -o out.hwpx
python scripts/hwpx_cli.py tables input.hwpx [--csv]        # list tables / CSV
python scripts/hwpx_cli.py fill-table input.hwpx IDX '{"label>dir":"val"}' -o out.hwpx
python scripts/hwpx_cli.py validate input.hwpx
python scripts/hwpx_cli.py page-guard -r ref.hwpx -o out.hwpx
python scripts/hwpx_cli.py toc input.hwpx [--json]
python scripts/hwpx_cli.py chunk input.hwpx [--by heading|size|pagebreak] [--json]
python scripts/hwpx_cli.py search-chunks input.hwpx "pattern" [--json]
python scripts/hwpx_cli.py repair input.hwpx                # dry-run (default)
python scripts/hwpx_cli.py repair input.hwpx --apply        # conservative auto-fix
python scripts/hwpx_cli.py content-check input.hwpx --must-not-have "[X],TODO,lorem"
python scripts/hwpx_cli.py insert-table input.hwpx --json '[["A","B"],["1","2"]]' -o out.hwpx
python scripts/hwpx_cli.py structure input.hwpx
```

### Format Overview

| Format | Ext | Structure | Read | Write | Notes |
|--------|-----|-----------|------|-------|-------|
| HWPX | `.hwpx` | ZIP + XML (OWPML) | ✅ | ✅ | Korean gov standard, cross-platform |
| HWP | `.hwp` | OLE2 compound binary | ✅ | ❌ | Legacy v5, read-only |

---

## 1. HWPX Editing Workflow (Core)

### Single-Line XML Problem

Hancom saves HWPX internal XML as **minified single-line** text. grep/diff/Edit tools break on it.
Follow this pipeline:

```
unpack (pretty-print) → Edit → pack (auto strip + minify) → validate → page-guard
```

### Step 1: Unpack + Pretty-print

```bash
python scripts/office/unpack.py input.hwpx work/
```

### Step 2: Edit XML directly

Edit the pretty-printed XML. Key constraints:
- Preserve **secPr** in the first run of the first paragraph of each section (defines page geometry)
- **charPrIDRef, paraPrIDRef, borderFillIDRef** values must match header.xml definitions
- Preserve all existing namespace declarations

### Step 3: Pack (auto linesegarray strip + minify)

```bash
python scripts/office/pack.py work/ output.hwpx
# Options: --keep-linesegarray, --no-minify
```

linesegarray is a layout cache that Hancom recalculates on open. Stale cache causes text compression and missing line breaks — pack.py strips it automatically.

### Step 4: Validate + Page Guard

```bash
python scripts/validate.py output.hwpx
python scripts/page_guard.py --reference input.hwpx --output output.hwpx
```

Both validate and page-guard pass before completion. On page-guard failure: fix cause → rebuild.

---

## 2. Reference-Based Restoration

Default workflow when user provides a reference HWPX:

```bash
# 1) Analyze reference + extract XML blueprints
python scripts/analyze_template.py reference.hwpx \
  --extract-header /tmp/ref_header.xml \
  --extract-section /tmp/ref_section.xml

# 2) Clone ref_section.xml → modify only text/data as requested
#    Preserve structure: tables, paragraph count, style IDs

# 3) Build restored document
python scripts/build_hwpx.py \
  --header /tmp/ref_header.xml \
  --section /tmp/new_section0.xml \
  --output result.hwpx

# 4) Validate
python scripts/validate.py result.hwpx
python scripts/page_guard.py --reference reference.hwpx --output result.hwpx
```

### 99% Restoration Checklist

- [ ] charPrIDRef, paraPrIDRef, borderFillIDRef reference chain identical
- [ ] Table rowCnt, colCnt, colSpan, rowSpan, cellSz, cellMargin identical
- [ ] Paragraph order, count, blank-line positions identical
- [ ] Page size, margins, section properties (secPr) identical
- [ ] Changes limited to user-requested scope only
- [ ] Page count identical (page_guard PASS)

---

## 3. Creating New HWPX Documents

### python-hwpx API (simple documents)

```python
from hwpx import HwpxDocument

doc = HwpxDocument.new()
doc.add_paragraph("First paragraph.")
table = doc.add_table(rows=3, cols=4)
table.set_cell_text(0, 0, "Name")
doc.save_to_path("output.hwpx")
```

See [python-hwpx GitHub](https://github.com/airmang/python-hwpx) for full API.

Known bug: `set_header_text()` / `set_footer_text()` silently fail. Workaround: unpack → manually edit header/footer XML in section0.xml `<hp:headerFooter>` → pack.

### Template-based creation

```bash
python scripts/build_hwpx.py \
  --template gonmun \
  --section my_section.xml \
  --title "Document Title" \
  --output gonmun.hwpx
```

Available templates: `base`, `gonmun` (official letter), `report`, `minutes`, `proposal`

### Table Builder (H2Orestart-compatible)

Use `table_builder.py` instead of raw XML tables, which crash H2Orestart due to missing undocumented attributes:

```bash
python scripts/table_builder.py --json '[["연도","규모"],["2024","4200"]]' -o table.xml
python scripts/table_builder.py --csv data.csv -o table.xml
```

Golden table templates: `reference/table_templates/`

### Markdown/JSON → HWPX

```bash
python scripts/create_document.py --input content.md --output doc.hwpx
```

---

## 4. Text Extraction

### HWPX

```bash
python scripts/text_extract.py input.hwpx                    # plain text
python scripts/text_extract.py input.hwpx --format markdown   # markdown
python scripts/text_extract.py input.hwpx --include-tables    # include tables
```

### HWP 5.0 (upgrade-first strategy)

HWPX is the canonical format. Upgrade HWP files to HWPX for editing:

```bash
# Read / inspect
hwp5proc xml input.hwp           # XML representation
hwp5proc ls input.hwp            # list OLE streams

# Quick text extraction:
hwp5proc xml input.hwp | python3 -c "
import sys, xml.etree.ElementTree as ET
tree = ET.parse(sys.stdin)
for elem in tree.getroot().iter():
    if elem.text and elem.text.strip():
        print(elem.text.strip())
"

# Upgrade to HWPX
python scripts/hwp_convert.py input.hwp output.hwpx
# Then edit the resulting HWPX using Section 1 workflow
```

> `@ssabrojs/hwpxjs convert:hwp` may produce dummy HWPX with placeholder text for some files (2026-03-18). Verify section0.xml content after conversion.

> 출처: [HWP→HWPX API license](https://forum.developer.hancom.com/t/hwp-hwpx-api/2980)
> 출처: [HWPX→HWP API not available](https://forum.developer.hancom.com/t/hwpx-hwp-api/2606)

---

## 5. XML Writing Guides

Detailed XML reference for section0.xml and header.xml editing:

- **Section0.xml**: paragraphs, blank lines, mixed formatting, tables → `reference/section0-xml-guide.md`
- **Header.xml**: charPr, paraPr, borderFill definitions → `reference/header-xml-guide.md`
- **Style ID maps**: template-specific ID ranges → `reference/style_id_maps.md`

---

## 6. QA Verification Loop

First render almost always has issues. Treat QA as bug hunting, not confirmation.

### Step 1: Structural validation

```bash
python scripts/validate.py output.hwpx
```

Checks: ZIP validity, required files, mimetype position/compression, XML well-formedness.

### Step 2: Page guard (when reference exists)

```bash
python scripts/page_guard.py --reference input.hwpx --output output.hwpx
```

Thresholds: text >15%, paragraph >25% → FAIL.

### Step 3: Content QA

```bash
python scripts/text_extract.py output.hwpx | grep -iE "xxxx|lorem|placeholder|TODO|견본"

python scripts/hwpx_cli.py content-check output.hwpx \
  --must-not-have "[X],TODO,lorem,placeholder,견본"
```

### Step 4: Visual QA

Use subagents for visual inspection — fresh eyes catch issues you miss after editing XML.

```bash
export JAVA_HOME="$(brew --prefix openjdk)/libexec/openjdk.jdk/Contents/Home"
soffice --headless --norestore --convert-to pdf output.hwpx
pdftoppm -jpeg -r 150 output.pdf page
```

Subagent prompt template: `reference/visual_qa_prompt.md`

### Step 5: Fix & Re-verify

1. Find issue → fix XML → re-pack
2. Re-render only changed pages: `pdftoppm -jpeg -r 150 -f N -l N output.pdf page-fixed`
3. Re-inspect — one fix often creates another problem
4. Complete at least 1 fix-and-verify cycle before declaring done

### QA Checklist

- [ ] validate.py PASS
- [ ] page_guard.py PASS (if reference exists)
- [ ] No placeholder remnants in text
- [ ] Visual render matches expected layout
- [ ] Table content complete, text not compressed (linesegarray stripped)
- [ ] Style consistency, page count matches reference
- [ ] Korean text wrapping correctly, fonts rendering as intended
- [ ] Color contrast ≥ 4.5:1, font size ≥ 9pt

---

## 7. CJK/Korean Text Handling

- Korean fonts: verify `맑은 고딕`, `함초롬돋움`, `함초롬바탕` in header.xml `<hh:fontRef>`
- CJK display width: fullwidth chars = 2 units (`scripts/ooxml/cjk_utils.py` → `get_display_width()`)
- Color contrast: WCAG 2.1 AA ratio 4.5:1 (`check_contrast()`)
- `inject_korean_lang()` and `auto_fit_columns()` in cjk_utils.py are **OOXML-specific** (DOCX/PPTX). For HWPX, set Korean attributes directly in header.xml charPr `<hh:fontRef hangul="..."/>`.

---

## 8. HWPX → PDF Conversion

Requires LibreOffice + H2Orestart extension + Java Runtime.

```bash
soffice --headless --norestore --convert-to pdf input.hwpx --outdir ./
pdftoppm -jpeg -r 150 input.pdf page   # for visual QA
```

If conversion fails ("source file could not be loaded"):
1. Verify Java is installed: `java -version`
2. Verify H2Orestart extension is installed in LibreOffice
3. Terminate stale soffice processes then retry
4. Use absolute paths for input file

---

## 9. Essential Rules

1. **HWPX is the canonical format** — all edits target HWPX; HWP is an upgrade-source only
2. **Preserve secPr** in first paragraph's first run (defines page geometry)
3. **mimetype first** — first ZIP entry, ZIP_STORED, `application/hwp+zip`
4. **Preserve namespaces** — keep all existing ns declarations during XML edits
5. **Strip linesegarray** after any text change — Hancom trusts stale cache, causing layout corruption
6. **Pretty-print ↔ minify** — pretty-print on unpack, minify on pack
7. **validate + page-guard** before completion — both required
8. **Style ID sync** — section XML IDRefs must match header.xml definitions
9. **Rebuild on page-guard failure** — fix cause, rebuild, re-verify
10. **Change only what user requested** — preserve existing structure (tables, paragraphs, secPr)
11. **Whitespace in `<hp:t>` is significant** — preserve carefully
12. **Verify XML well-formedness** before build — fix unclosed tags immediately
13. **Preserve table structure** — rowCnt/colCnt/colSpan/rowSpan changes only when requested
14. **Templates are read-only** — copy before modifying
15. **Match reference page count** — adjust text to fit existing layout
16. **Atomic save** — pack.py writes temp file → validates → atomic rename
17. **Fill-table by label path** — `hwpx_cli.py fill-table` for gov forms: `"이름 > 오른쪽": "value"`
18. **repair is dry-run by default** — use `--apply` or `-o` for fixes (safe: XML decl, linesegarray, IDRef→0)
19. **Agentic reading for long docs** — use `toc` → `chunk` → `search-chunks` for 50+ page documents
20. **Use pack.py or hwpx_cli.py save** for repacking — raw zipfile skips linesegarray strip, mimetype STORED, XML minify
21. **Use table_builder.py or python-hwpx API** for tables — raw XML causes H2Orestart crashes
22. **Verify hwpxjs conversion output** — some HWP files produce dummy HWPX content

---

## 10. Dependencies & Platform

See `reference/dependencies.md` for full installation guide, cross-platform matrix, and library tiers.

### Core Python packages

```bash
pip install hwpx lxml pyhwp olefile defusedxml openpyxl Pillow
```

### System dependencies

```bash
# macOS
brew install libreoffice openjdk poppler
# H2Orestart: https://github.com/ebandal/H2Orestart/releases
```

---

## File Structure

```
hwp_hwpx/
├── SKILL.md
├── reference/          ← hwpx-format.md, style_id_maps.md, visual_qa_prompt.md,
│                         section0-xml-guide.md, header-xml-guide.md, dependencies.md
├── scripts/
│   ├── office/         ← unpack.py (pretty-print), pack.py (strip+minify)
│   ├── hwpx_cli.py     ← unified CLI
│   ├── validate.py, page_guard.py, build_hwpx.py, analyze_template.py
│   ├── text_extract.py, create_document.py, hwp_reader.py
│   └── ooxml/          ← cjk_utils.py, soffice.py
└── templates/          ← base, gonmun, report, minutes, proposal
```
