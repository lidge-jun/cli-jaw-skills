---
name: hwp
description: "HWP/HWPX create, read, edit, review. Triggers: 한글, .hwp, .hwpx, HWP, HWPX, Korean documents."
---

# HWP/HWPX Document Skill

Create, read, edit, and validate Hancom Office HWP 5.0 (binary) and HWPX (ZIP+XML) files.
HWPX uses **XML-first direct editing**; HWP uses **read + convert strategy**.

Triggers: "한글", ".hwp", ".hwpx", "HWP", "HWPX", Korean documents, 한컴오피스, OWPML.
Do NOT use for: DOCX, PDF, spreadsheets, or Google Docs.

---

## Quick Reference

| Task | Tool / Command |
|------|----------------|
| **Detect format** | `file doc.hwpx` → ZIP = HWPX, "HWP Document" = HWP 5.0 |
| **Create HWPX** | `python-hwpx` API or `build_hwpx.py` (template-based) |
| **Read HWPX** | `hwpx_cli.py text input.hwpx` or `text_extract.py` |
| **Read HWP** | `hwp5proc text input.hwp` (pyhwp) |
| **Edit HWPX** | unpack → pretty-print → Edit → pack (auto strip+minify) |
| **Search/Replace** | `hwpx_cli.py search` / `hwpx_cli.py replace` / `hwpx_cli.py batch-replace` |
| **Tables** | `hwpx_cli.py tables` / `hwpx_cli.py fill-table` (path-based) |
| **Upgrade HWP** | `npx hwpxjs convert:hwp` or `java -jar hwp2hwpx.jar` → then edit HWPX |
| **Validate** | `hwpx_cli.py validate` + `hwpx_cli.py page-guard` |
| **HWPX → PDF** | `soffice --headless --convert-to pdf` (needs H2Orestart+Java) |
| **Visual QA** | PDF → `pdftoppm -jpeg -r 150` → subagent inspection |

### Unified CLI (`hwpx_cli.py`)

```bash
python scripts/hwpx_cli.py open input.hwpx work/           # unpack + pretty-print
python scripts/hwpx_cli.py save work/ output.hwpx           # minify + strip + pack (atomic)
python scripts/hwpx_cli.py text input.hwpx                  # extract text
python scripts/hwpx_cli.py search input.hwpx "pattern"      # regex search in text
python scripts/hwpx_cli.py replace input.hwpx "old" "new" -o out.hwpx  # text replace
python scripts/hwpx_cli.py batch-replace input.hwpx map.json -o out.hwpx  # bulk replace
python scripts/hwpx_cli.py tables input.hwpx [--csv]        # list tables / CSV export
python scripts/hwpx_cli.py fill-table input.hwpx IDX '{"label>dir":"val"}' -o out.hwpx
python scripts/hwpx_cli.py validate input.hwpx              # structural validation
python scripts/hwpx_cli.py page-guard -r ref.hwpx -o out.hwpx  # page drift check
python scripts/hwpx_cli.py toc input.hwpx [--json]          # table of contents from headings
python scripts/hwpx_cli.py chunk input.hwpx [--by heading|size|pagebreak] [--json]
python scripts/hwpx_cli.py search-chunks input.hwpx "pattern" [--json]  # search with chunk context
python scripts/hwpx_cli.py repair input.hwpx                # dry-run diagnosis (default)
python scripts/hwpx_cli.py repair input.hwpx --apply        # conservative auto-fix
python scripts/hwpx_cli.py structure input.hwpx              # document structure tree
```

### Format Overview

| Format | Ext | Structure | Read | Write | Notes |
|--------|-----|-----------|------|-------|-------|
| HWPX | `.hwpx` | ZIP + XML (OWPML) | ✅ | ✅ | Korean gov standard, cross-platform |
| HWP | `.hwp` | OLE2 compound binary | ✅ | ❌ | Legacy v5, read-only |

---

## 1. HWPX Editing Workflow (Core)

### ⚠️ Single-Line XML Problem

Hancom saves HWPX internal XML as **minified single-line** text. grep/diff/Edit tools cannot work on it.
Always follow this pipeline:

```
unpack (pretty-print) → Edit → pack (auto strip + minify) → validate → page-guard
```

### Step 1: Unpack + Pretty-print

```bash
python scripts/office/unpack.py input.hwpx work/
# XML files are extracted with indentation for readable editing
```

### Step 2: Edit XML directly with Read/Edit tools

Edit the pretty-printed XML. Key constraints:
- **secPr** (Section Properties): MUST be preserved in the first run of the first paragraph of each section
- **charPrIDRef, paraPrIDRef, borderFillIDRef**: must match header.xml definitions
- **Namespace declarations**: preserve all existing ns declarations during edits

### Step 3: Pack (auto linesegarray strip + minify)

```bash
python scripts/office/pack.py work/ output.hwpx
# Options: --keep-linesegarray (skip strip), --no-minify (keep pretty-print)
# XML is minified back + mimetype placed as first ZIP entry (STORED)
```

linesegarray is a **layout cache** (line positions, widths) that Hancom recalculates on open. If not stripped after text changes, Hancom trusts the stale cache and forces modified text into the old layout — causing text compression and missing line breaks. pack.py strips it automatically.

### Step 4: Validate + Page Guard

```bash
python scripts/validate.py output.hwpx
python scripts/page_guard.py --reference input.hwpx --output output.hwpx
```

Do NOT mark as complete with validate alone. page_guard MUST also pass.
On page_guard failure: fix cause (excess length / structural change) → rebuild.

---

## 2. Reference-Based Restoration (when user attaches .hwpx)

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
- [ ] Changes limited to user-requested scope (body text, values only)
- [ ] Page count identical (page_guard PASS)

---

## 3. Creating New HWPX Documents

### 3.1 python-hwpx API (simple documents)

```python
from hwpx import HwpxDocument

doc = HwpxDocument.new()
doc.add_paragraph("First paragraph.")

table = doc.add_table(rows=3, cols=4)
table.set_cell_text(0, 0, "Name")
table.set_cell_text(0, 1, "Department")

doc.save_to_path("output.hwpx")
```

See [python-hwpx GitHub](https://github.com/airmang/python-hwpx) for full API docs.

**Known bugs**: `set_header_text()` and `set_footer_text()` silently fail (text not saved). Workaround: unpack → manually edit the header/footer XML in section0.xml `<hp:headerFooter>` → pack.

### 3.2 Template-based creation (formatted documents)

```bash
python scripts/build_hwpx.py \
  --template gonmun \
  --section my_section.xml \
  --title "Document Title" \
  --output gonmun.hwpx
```

Available templates: `base`, `gonmun` (official letter), `report`, `minutes`, `proposal`

### 3.3 Markdown/JSON → HWPX

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

HWP binary cannot be written. The canonical format is HWPX.
HWP files should be **upgraded to HWPX**, edited there, and saved as HWPX.
Hancom's official stance: HWP→HWPX conversion may be available depending on license; HWPX→HWP API is not provided.

```bash
# 1. Read / inspect
hwp5proc text input.hwp          # extract text
hwp5proc xml input.hwp           # XML representation
hwp5proc ls input.hwp            # list OLE streams

# 2. Upgrade to HWPX (pick one)
npx hwpxjs convert:hwp input.hwp                    # Node.js
java -jar hwp2hwpx.jar input.hwp output.hwpx        # Java (neolord0/hwp2hwpx)

# 3. Edit the resulting HWPX using Section 1 workflow
# 4. Save as HWPX (canonical). HWP compat output is a separate optional path.
```

> 출처: [HWP→HWPX API license](https://forum.developer.hancom.com/t/hwp-hwpx-api/2980)
> 출처: [HWPX→HWP API not available](https://forum.developer.hancom.com/t/hwpx-hwp-api/2606)

---

## 5. Section0.xml Writing Guide

### Basic paragraph

```xml
<hp:p paraPrIDRef="0" styleIDRef="0">
  <hp:run charPrIDRef="0">
    <hp:secPr><!-- ONLY in first paragraph, first run --></hp:secPr>
    <hp:t>Body text content.</hp:t>
  </hp:run>
</hp:p>
```

- `secPr`: MUST be in the first run of the first paragraph. Defines page size, margins, columns.
- `paraPrIDRef`: references paraPr ID defined in header.xml
- `charPrIDRef`: references charPr ID defined in header.xml

### Blank line

```xml
<hp:p paraPrIDRef="0" styleIDRef="0">
  <hp:run charPrIDRef="0"><hp:t></hp:t></hp:run>
</hp:p>
```

### Mixed formatting in one paragraph

```xml
<hp:p paraPrIDRef="0" styleIDRef="0">
  <hp:run charPrIDRef="0"><hp:t>Normal </hp:t></hp:run>
  <hp:run charPrIDRef="7"><hp:t>Bold Title</hp:t></hp:run>
  <hp:run charPrIDRef="0"><hp:t> followed by normal text</hp:t></hp:run>
</hp:p>
```

### Table

```xml
<hp:tbl colCnt="2" rowCnt="2" cellSpacing="0" borderFillIDRef="1">
  <hp:tr>
    <hp:tc colAddr="0" rowAddr="0" colSpan="1" rowSpan="1">
      <hp:cellSz width="29764" height="1000"/>
      <hp:cellMargin left="510" right="510" top="141" bottom="141"/>
      <hp:p paraPrIDRef="0" styleIDRef="0">
        <hp:run charPrIDRef="0"><hp:t>Cell content</hp:t></hp:run>
      </hp:p>
    </hp:tc>
    <hp:tc colAddr="1" rowAddr="0" colSpan="1" rowSpan="1">
      <!-- ... -->
    </hp:tc>
  </hp:tr>
</hp:tbl>
```

---

## 6. Header.xml Modification Guide

Add new styles by appending definitions to header.xml.

### Adding charPr (character shape)

```xml
<hh:charPr id="7" height="2200" bold="true">
  <hh:fontRef hangul="맑은 고딕" latin="맑은 고딕"/>
</hh:charPr>
```
- `id`: next available number (existing max + 1)
- `height`: point size × 100 (22pt = 2200)

### Adding paraPr (paragraph shape)

```xml
<hh:paraPr id="20" align="CENTER">
  <hh:spacing line="160" lineType="PERCENT"/>
  <hh:margin left="0" right="0" indent="0"/>
</hh:paraPr>
```

### Adding borderFill

```xml
<hh:borderFill id="3">
  <hh:border>
    <hh:left type="SOLID" width="0.12mm" color="#000000"/>
    <hh:right type="SOLID" width="0.12mm" color="#000000"/>
    <hh:top type="SOLID" width="0.12mm" color="#000000"/>
    <hh:bottom type="SOLID" width="0.12mm" color="#000000"/>
  </hh:border>
</hh:borderFill>
```

### Template Style ID Summary

| Template | charPr | paraPr | borderFill |
|----------|--------|--------|------------|
| base | 0-6 | 0-19 | 1-2 |
| gonmun | +7-10 (title 22pt, signature 16pt, contact 8pt, table header 10pt) | +20-22 | +3-4 |
| report | +7-13 (title 20pt, subtitle 14pt, etc.) | +20-27 | +5 |
| minutes | +7-9 (title 18pt, section 12pt, table header 10pt) | +20-22 | +4 |
| proposal | +7-11 (title 20pt, subtitle 14pt, etc.) | +20-22 | +5-8 |

Full style ID maps: reference/style_id_maps.md

---

## 7. QA Verification Loop (MANDATORY)

**First render almost always has issues. QA is bug hunting, not confirmation.**

### Step 1: Structural validation

```bash
python scripts/validate.py output.hwpx
```
Checks: ZIP validity, required files, mimetype position/compression, XML well-formedness.

### Step 2: Page guard (when reference exists)

```bash
python scripts/page_guard.py --reference input.hwpx --output output.hwpx
```
Checks: paragraph count, page/column breaks, table count/shape, text length.
Thresholds: text >15%, paragraph >25% → FAIL.

### Step 3: Content QA

```bash
python scripts/text_extract.py output.hwpx --format markdown
# Check for placeholder remnants
python scripts/text_extract.py output.hwpx | grep -iE "xxxx|lorem|placeholder|TODO|견본"
```

### Step 4: Visual QA

**⚠️ USE SUBAGENTS** — you've been staring at the XML and will see what you expect, not what's there. Subagents have fresh eyes.

```bash
# Requires: LibreOffice + H2Orestart + Java (see Section 11)
export JAVA_HOME="$(brew --prefix openjdk)/libexec/openjdk.jdk/Contents/Home"
soffice --headless --norestore --convert-to pdf output.hwpx
pdftoppm -jpeg -r 150 output.pdf page
```

Subagent prompt template: see reference/visual_qa_prompt.md

### Step 5: Fix & Re-verify

1. Find issue → fix XML → re-pack
2. Re-render only changed pages: `pdftoppm -jpeg -r 150 -f N -l N output.pdf page-fixed`
3. Re-inspect — one fix often creates another problem
4. **Never declare completion before at least 1 fix-and-verify cycle**

### QA Checklist

- [ ] validate.py PASS
- [ ] page_guard.py PASS (if reference exists)
- [ ] No placeholder remnants in text
- [ ] Visual render matches expected layout
- [ ] Table content complete (no empty cells that should have data)
- [ ] Text not compressed/squeezed (linesegarray stripped)
- [ ] Style consistency (headings, body, table headers)
- [ ] Page count matches reference
- [ ] Korean text wrapping correctly
- [ ] Korean font rendering as intended (no fallback glyphs)
- [ ] Color contrast >= 4.5:1
- [ ] Font size >= 9pt

---

## 8. CJK/Korean Text Handling

- Korean fonts in HWPX: verify `맑은 고딕`, `함초롬돋움`, `함초롬바탕` in header.xml `<hh:fontRef>`
- CJK display width: fullwidth chars = 2 units (`scripts/ooxml/cjk_utils.py` → `get_display_width()`)
- Color contrast: WCAG 2.1 AA ratio 4.5:1 (`check_contrast()`)
- Note: `inject_korean_lang()` and `auto_fit_columns()` in cjk_utils.py are **OOXML-specific** (DOCX/PPTX `<a:rPr>` elements). They do not apply to HWPX XML. For HWPX, set Korean attributes directly in header.xml charPr `<hh:fontRef hangul="..."/>`.

---

## 9. Critical Rules

1. **HWPX is the canonical format** — all edits and saves target HWPX. HWP is an upgrade-source, not a save target
2. **Preserve secPr** — never delete from first paragraph's first run
3. **mimetype first** — first ZIP entry, ZIP_STORED, "application/hwp+zip"
4. **Preserve namespaces** — keep all existing ns declarations during XML edits
5. **Strip linesegarray** — MUST remove after any text change (Hancom recalculates on open)
6. **Pretty-print ↔ minify** — pretty-print on unpack, minify on pack
7. **validate + page-guard mandatory** — both must pass before completion
8. **Style ID sync** — section XML IDRefs must match header.xml definitions
9. **Rebuild on page-guard failure** — never submit failed output
10. **Change only what user requested** — no unauthorized structure changes (tables/paragraphs/secPr)
11. **HWP upgrade-first** — upgrade HWP→HWPX, edit HWPX, save as HWPX. HWP compat output is optional, separate path
12. **Watch mixed content** — whitespace inside `<hp:t>` is significant
13. **Verify XML well-formedness before build** — fix unclosed tags immediately
14. **Preserve table structure** — no unauthorized rowCnt/colCnt/colSpan/rowSpan changes
15. **Templates are read-only** — copy before modifying
16. **Match reference page count** — adjust text to fit existing layout
17. **Atomic save** — pack.py writes to temp file → validates ZIP → atomic rename. Original file is never corrupted on failure
18. **Fill-table by label path** — use `hwpx_cli.py fill-table` for gov forms: `"이름 > 오른쪽": "value"` finds label cell, navigates relatively
19. **repair is dry-run by default** — `repair` reports issues without changing files. Use `--apply` or `-o` for actual fixes. Only 3 safe fixes: XML decl, linesegarray, IDRef→0
20. **Agentic Reading for long docs** — use `toc` → `chunk` → `search-chunks` pipeline to navigate 50+ page documents without loading everything into context

---

## 10. HWPX → PDF Conversion

Requires LibreOffice + H2Orestart extension + Java Runtime.

```bash
# Requires LibreOffice + H2Orestart + Java (see Section 11 for setup)

# Convert HWPX to PDF
soffice --headless --norestore --convert-to pdf input.hwpx --outdir ./

# Convert to images for visual QA
pdftoppm -jpeg -r 150 input.pdf page
```

If conversion fails with "source file could not be loaded":
1. Check Java: `java -version` — must be installed
2. Check H2Orestart: extension must be installed in LibreOffice
3. Kill stale soffice: `pkill -f soffice` then retry
4. Use absolute paths for input file

---

## 11. Dependencies & Installation

### Core Python packages

```bash
pip install hwpx lxml pyhwp olefile defusedxml openpyxl
```

| Package | Purpose |
|---------|---------|
| `hwpx` (python-hwpx) | HWPX read/modify/create |
| `lxml` | XML parsing (unpack/pack pretty-print) |
| `pyhwp` | HWP 5.0 read/extract (hwp5proc CLI) |
| `olefile` | HWP 5.0 OLE container access |
| `defusedxml` | Safe XML parsing (XXE prevention) |
| `openpyxl` | CJK column width utilities |

### System dependencies

```bash
# macOS (Homebrew)
brew install libreoffice openjdk poppler   # soffice, java, pdftoppm

# Environment variables (add to ~/.zshrc)
export JAVA_HOME="$(brew --prefix openjdk)/libexec/openjdk.jdk/Contents/Home"
export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"

# H2Orestart extension (HWPX support for LibreOffice PDF conversion)
# Download: https://github.com/ebandal/H2Orestart/releases
# Install: unopkg add H2Orestart.oxt

# Linux (apt)
sudo apt install libreoffice default-jre poppler-utils
# H2Orestart: apt install libreoffice-h2orestart (Debian sid+) or .oxt manual install
```

### HWP→HWPX upgrade tools (pick one)

```bash
# Option A: Node.js
npm install -g @ssabrojs/hwpxjs    # then: npx hwpxjs convert:hwp input.hwp

# Option B: Java (neolord0/hwp2hwpx) — most accurate conversion
# Download jar from: https://github.com/neolord0/hwp2hwpx/releases
# then: java -jar hwp2hwpx.jar input.hwp output.hwpx
# Requires: Java 11+ (already installed for H2Orestart)
```

---

## 12. Cross-Platform Compatibility

| Feature | macOS | Linux | Windows |
|---------|-------|-------|---------|
| **HWPX read/edit** | ✅ python-hwpx | ✅ python-hwpx | ✅ python-hwpx |
| **HWPX → PDF** | ✅ soffice+H2Orestart+Java | ✅ same | ✅ same |
| **HWP read** | ✅ pyhwp | ✅ pyhwp | ✅ pyhwp |
| **HWP → HWPX upgrade** | ✅ hwpxjs / hwp2hwpx | ✅ same | ✅ same |
| **HWP write (binary)** | ❌ | ❌ | ⚠️ COM only (pyhwpx) |
| **unpack/pack/validate** | ✅ pure Python | ✅ pure Python | ✅ pure Python |
| **linesegarray strip** | ✅ pack.py auto | ✅ pack.py auto | ✅ pack.py auto |

### Key platform notes

- **Core editing pipeline** (unpack→edit→pack) is **pure Python, fully cross-platform**. Zero system deps.
- **PDF conversion** needs LibreOffice + H2Orestart + Java on all platforms (only system-level dep).
- **HWP→HWPX upgrade** needs Node.js (hwpxjs) or Java (hwp2hwpx). Java is already required for PDF.
- **HWP binary write** is Windows-only via COM (pyhwpx). Use upgrade-first strategy instead.
- **macOS LibreOffice**: may need `pkill -f soffice` before each headless call to avoid stale locks.

---

## 13. Library Tiers

| Tier | Library | Format | Capabilities |
|------|---------|--------|-------------|
| **1** | python-hwpx | HWPX | R/W/Create — primary tool |
| **1** | pyhwp | HWP 5.0 | Read-only — most mature binary parser |
| **2** | hwp-hwpx-parser | HWP+HWPX | Read-only parser |
| **2** | olefile | HWP 5.0 | Low-level OLE access |
| **3** | @ssabrojs/hwpxjs | HWPX+HWP conv | Node.js — HWP→HWPX conversion |
| **3** | hwplib (Java) | HWP 5.0 | Only HWP binary R/W library |

## File Structure

```
hwp_hwpx/
├── SKILL.md
├── reference/          ← hwpx-format.md, style_id_maps.md, visual_qa_prompt.md
├── scripts/
│   ├── office/         ← unpack.py (pretty-print), pack.py (strip+minify)
│   ├── hwpx_cli.py           ← unified CLI (open/save/text/search/replace/tables/fill-table/validate)
│   ├── validate.py, page_guard.py, build_hwpx.py, analyze_template.py
│   ├── text_extract.py, create_document.py, hwp_reader.py
│   └── ooxml/          ← cjk_utils.py, soffice.py
└── templates/          ← base, gonmun, report, minutes, proposal
```
