---
name: hwp
description: "HWP/HWPX create, read, edit, review, template-fill, QA. Triggers: 한글, .hwp, .hwpx, HWP, HWPX, Korean documents, 한컴오피스, OWPML."
---

# HWP/HWPX Document Skill

> **Scope**: HWP/HWPX only. Do NOT reference or load skills for other formats
> (DOCX, PPTX, XLSX, PDF). If the task involves a non-HWP format, stop and tell the user.

Primary tool: **officecli** (on PATH -- global install).
Fallback: **Legacy Python scripts** only when officecli does not cover the operation.
Triggers: `"한글"`, `".hwpx"`, `".hwp"`, `"HWP"`, `"HWPX"`, Korean documents, 한컴오피스, OWPML.

---

## Quick Decision

| Task | OK? | Command |
|------|-----|---------|
| Create new .hwpx | Yes | `officecli create file.hwpx` |
| Create from Markdown | Yes | `officecli create file.hwpx --from-markdown input.md` |
| Read / analyze .hwpx | Yes | `view text`, `annotated`, `outline`, `stats`, `html`, `markdown`, `tables`, `forms`, `objects` |
| Edit existing .hwpx | Yes | `set`, `add`, `remove`, `move`, `swap` |
| Label-based fill | Yes | `set /table/fill --prop 'fill:label=val'` |
| Form recognize | Yes | `view forms --auto` (label-value auto-detect) |
| Table map | Yes | `view tables` (2D grid + labels) |
| Markdown export | Yes | `view markdown` |
| Equation (수식) | Yes | `add --type equation --prop 'script={1 over 2}'` |
| Object finder | Yes | `view objects` (picture/field/bookmark/equation) |
| Query (expanded) | Yes | `query 'tc[text~=홍길동]'`, `:has()`, `>` combinator |
| Template merge | Yes | `merge template.hwpx out.hwpx --data '{"key":"val"}'` |
| Swap elements | Yes | `swap file.hwpx '/p[1]' '/p[2]'` |
| Column break | Yes | `add --type columnbreak --prop cols=2` |
| Image anchor / floating | Yes | `add --type picture --prop anchor=page --prop halign=center` |
| Field types | Yes | `add --type author\|title\|lastsaveby\|filename` |
| Compare documents | Yes | `compare a.hwpx b.hwpx` (LCS diff + table compare) |
| Security validation | Yes | ZIP bomb, path traversal, symlink, XXE defense |
| Broken ZIP recovery | Yes | corrupted HWPX auto-recovery via Local File Header scan |
| HTML preview | Yes | `view html --browser` |
| Watch live preview | Yes | `watch file.hwpx` |
| Validate .hwpx | Yes | `validate` (9-level check) |
| Raw XML | Yes | `raw`, `raw-set` |
| Watermark (image) | Yes | `add --type watermark --prop src=img.png` (opaque RGB preferred) |
| New form field creation | Blocked | source prototype exists; Hancom verification not closed |
| Open .hwp (binary) | No | Convert to .hwpx first (Hancom Office or `hwp_convert.py`) |

---

## Bonus Subskill References

No bonus subskills currently exist for HWP. If future subskills are added
(e.g., `./creating.md`, `./editing.md`), read them only for the specific task at hand.
Reference files live in `./reference/` (format specs, style maps, visual QA prompts).

---

## Design Principles for Korean Documents

### Korean Government Form Aesthetics (한국 공공양식 미감)

Korean official documents follow strict visual conventions. Respect them:

- **Tables are the backbone**: Korean forms are table-driven. Every label-value pair
  lives in a precisely merged cell grid. Preserve the grid structure exactly.
- **Heading hierarchy**: 제1조 (Articles) > 제1항 (Clauses) > 제1호 (Items).
  Use styleidref for outline levels. Never flatten the hierarchy.
- **Fixed margins**: Government forms use standard A4 margins (top/bottom ~15mm,
  left/right ~20mm). Do not alter margins on existing documents.
- **Alignment**: Body text is JUSTIFY (양쪽 정렬) by default in Korean documents.
  Headings may be CENTER. Never use LEFT for body text in formal documents.

### Uniform Spacing Detection (균등분할)

Korean forms often use uniform character spacing for names in cells:
`"홍 길 동"` (spaces between each character). This is a **display convention**, not data.

- When reading: strip uniform spaces to get the actual value (`"홍길동"`).
- When writing: if the template cell uses uniform spacing, insert spaces to match
  (e.g., 2-char name `"이 준"`, 3-char `"홍 길 동"`, 4-char `"남궁민수"`).
- Detection regex: `^(\S)\s(\S)\s(\S)$` etc. (single-char groups separated by 1 space).

### Document Type Classification

| Type | Key Signals | Example |
|------|------------|---------|
| `exam` | equation 10+, rect objects | KICE 수능/모의고사 시험지 |
| `form` | table 3+, checkboxes (□/■) | 대학 신청서, 정부 양식 |
| `regulation` | ○ bullets 10+, 별첨/조항 refs, table 10+ | 운영지침, 내규, 시행세칙 |
| `report` | long text, few tables | 보고서, 논문 |
| `mixed` | none of above | 사업계획서 |

---

## Mandatory Verification (NEVER SKIP)

After ANY HWPX edit operation, ALWAYS execute these in order:

```bash
# 1. Structural validation (MUST pass)
officecli validate output.hwpx

# 2. PDF visual verification (MUST check)
soffice --headless --convert-to pdf --outdir /tmp output.hwpx
# Verify: table positions, guide text removed, checkboxes correct,
#         merged cell text in correct row, numbers not corrupted

# 3. If Hancom Office available, also open .hwpx directly
```

**Skip PDF verification = unverified output. Always inform user if soffice is unavailable.**

---

## Tool Discovery

Always confirm syntax from help before guessing:

```bash
officecli --help
officecli hwpx add
officecli hwpx set
officecli hwpx view --help
```

---

## Core Workflows

### Create & Import & Merge

```bash
officecli create doc.hwpx                                    # empty doc
officecli create doc.hwpx --from-markdown input.md           # MD->HWPX (JUSTIFY default)
officecli create doc.hwpx --from-markdown input.md --align left  # left-aligned
officecli merge template.hwpx out.hwpx --data '{"이름":"홍길동"}'  # template {{key}} replace
officecli merge template.hwpx out.hwpx --data data.json           # JSON file data
```

### View Modes

```bash
officecli view doc.hwpx text                    # line-numbered text
officecli view doc.hwpx annotated               # path + style detail
officecli view doc.hwpx outline                 # headings only
officecli view doc.hwpx stats                   # document statistics
officecli view doc.hwpx html --browser          # A4 HTML preview
officecli view doc.hwpx markdown                # GFM markdown export
officecli view doc.hwpx tables                  # table 2D grid + label map
officecli view doc.hwpx forms --auto            # CLICK_HERE + label-value auto-detect
officecli view doc.hwpx forms --auto --json     # JSON for AI pipeline
officecli view doc.hwpx objects                 # picture/field/bookmark/equation list
officecli view doc.hwpx objects --object-type field  # filter by type
officecli view doc.hwpx styles                  # charPr/paraPr styles
officecli view doc.hwpx issues                  # 9-level validation issues
```

### Edit

```bash
officecli add doc.hwpx /section[1] --type paragraph --prop text="content" --prop fontsize=11
officecli add doc.hwpx /section[1] --type table --prop rows=3 --prop cols=4
officecli set doc.hwpx '/section[1]/p[1]' --prop bold=true --prop align=CENTER
officecli set doc.hwpx / --prop find="old" --prop replace="new"
officecli remove doc.hwpx /section[1]/p[3]
officecli swap doc.hwpx '/p[1]' '/p[2]'
```

### Label Fill (table auto-fill)

```bash
officecli set doc.hwpx / --prop 'fill:대표자=홍길동' --prop 'fill:연락처=010-1234'
officecli set doc.hwpx / --prop 'fill:주소>down=서울시'   # direction: right(default), down, left, up
officecli set doc.hwpx /table/fill --prop '이름=김서준'    # fill: prefix optional
```

### Query (extended syntax)

```bash
officecli query doc.hwpx 'p'                          # all paragraphs
officecli query doc.hwpx 'tc[text~=홍길동]'           # cell text search
officecli query doc.hwpx 'run[bold=true]'              # bold runs
officecli query doc.hwpx 'p:has(tbl)'                  # paragraphs containing tables
officecli query doc.hwpx 'tbl > tr > tc[colSpan!=1]'   # merged cells
officecli query doc.hwpx 'run[fontsize>=20]'           # 20pt+ font
officecli query doc.hwpx 'p[heading=1]'                # heading 1
```

Operators: `=`, `!=`, `~=` (contains), `>=`, `<=`
Pseudo: `:empty`, `:contains(text)`, `:has(child)`, `:first`, `:last`
Virtual attrs: `text`, `bold`, `italic`, `fontsize`, `colSpan`, `rowSpan`, `heading`

### Compare

```bash
officecli compare a.hwpx b.hwpx                    # text diff (default)
officecli compare a.hwpx b.hwpx --mode outline      # heading diff
officecli compare a.hwpx b.hwpx --mode table --json  # table diff JSON
```

LCS DP alignment (fallback greedy for >10M cells).
Table similarity: dimension weight 0.3 + content weight 0.7.
Page range filtering: `--pages "1-3,5"`.

### Validate

```bash
officecli validate doc.hwpx
```

9-level: ZIP integrity, package (mimetype/rootfile/version), XML, IDRef, table structure,
namespace, BinData orphan, field pairs, section count.

### Image & Watermark

```bash
# Inline image
officecli add doc.hwpx /section[1] --type picture --prop path=/path/to/image.png

# Page-centered floating image
officecli add doc.hwpx /section[1] --type picture \
  --prop path=/path/to/image.png \
  --prop anchor=page --prop halign=center --prop valign=middle

# Watermark (opaque RGB PNG recommended; avoid transparent PNGs)
officecli add doc.hwpx /section[1] --type watermark \
  --prop src=/path/to/watermark.png --prop bright=0 --prop contrast=0

# Adjust position after creation
officecli set doc.hwpx '/section[1]/p[2]/run[1]/pic[1]' \
  --prop x=1111 --prop y=2222 --prop lock=1 --prop wrap=topbottom
```

### Watch & HTML Preview

```bash
officecli watch doc.hwpx           # auto-refresh HTML on file change
officecli unwatch doc.hwpx         # stop
officecli view doc.hwpx html --browser  # one-shot A4 preview
```

---

## Common Pitfalls

| Pitfall | Correct Approach |
|---------|-----------------|
| `--props text=Hello` | `--prop text=Hello` -- singular `--prop` always |
| `/body/p[1]` path | HWPX uses `/section[1]/p[1]` -- section-based, not body |
| `.hwp` (binary) open | Convert to `.hwpx` first (Hancom Office or `hwp_convert.py`) |
| Unquoted `[N]` in shell | `"/section[1]/p[1]"` -- always quote paths |
| fontsize omitted | `--prop fontsize=11` always -- prevents charPr 0 pollution |
| `officecli view file.hwpx` (no mode) | Error. Must specify: `text`, `markdown`, `tables`, etc. |
| Manual table mapping | `view tables` replaces manual inspection |
| HWP->HWPX text replace | Whole-paragraph `<t>` -- use raw string replace; p[0] may contain page-number fragments |

### Essential Rules (from subskill)

- **Auto-normalization**: PUA removal and uniform spacing collapse are applied automatically.
- **Transport parity**: CLI, Resident, and MCP all support the same view modes (tables, markdown, objects, forms).

---

## Form Recognition & Fill

### 4-Strategy Recognition

1. **Adjacent cell label-value** -- table label->value detection (default)
2. **Header+data rows** -- column-header recognition
3. **In-cell patterns** -- `□` checkbox, `keyword(  )` paren-blank, `(label:  )` annotation
4. **KV table detection** -- 16 Korean keywords trigger auto-detection

### 3-Phase Fill Pipeline

1. **In-cell patterns** -- checkbox `□`->`☑`, paren-blank fill, annotation fill
2. **Table label-value** -- exact + prefix 60% matching, 4-directional (`right`/`down`/`left`/`up`)
3. **Inline paragraph** -- regex lookbehind for `"label: value"` outside tables

### AI Form Fill Workflow

```bash
officecli view form.hwpx forms --auto --json > fields.json  # Step 1: recognize
# Step 2: AI maps label->value
officecli set form.hwpx /table/fill --prop '성 명=홍길동'   # Step 3: fill
```

### Confidence & Feedback

- Fill returns **unmatched labels** (labels without matching cells reported)
- Font-size heading detection: H1 >= 1.5x, H2 >= 1.3x, H3 >= 1.15x base
- Multi-`<hp:t>` in-cell replacement handles fragmented text nodes
- Form confidence score included in recognition output

### Regulation-Specific Patterns

- **Checkbox hierarchy**: `□` (section) -> `○` (item) -> `-` (detail) -> `*` (footnote)
- **Appendix references**: `[별첨 제N호]`, `[별지 N]` -- linked to form templates
- **Digit-concatenated headings**: `"3지원금 집행기준"` (no space between number and title)
- **Uniform footer**: repeated identical footers -> org extraction

### Exam XML Structure Patterns (condensed)

| Pattern | Description | Detection |
|---------|-------------|-----------|
| Page/Column breaks | `pageBreak="1"` / `columnBreak="1"` on `<hp:p>` | Page boundary = question group boundary |
| p[0] Monster | secPr + colPr + title tbl + question 1 text merged | Everything in first paragraph |
| Equation interleaving | `<t>` ↔ `<equation>` alternating pattern | Skip equations during text extraction |
| Answer choices | `①` + 5 `<equation>` (5-choice) | Auto-detect answer paragraphs |
| Text fragmentation | 1-2 char `<t>` splits (HWP conversion) | Concatenate all text then match |
| 2-column layout | `<hp:colPr type="NEWSPAPER" colCount="2">` | Exam-specific layout |

---

## Security

| Check | Limits |
|-------|--------|
| ZIP bomb | 1000 entries, 200 MB, 100:1 ratio |
| Path traversal | null byte, `..`, absolute path, drive letter, symlink |
| XXE | `DtdProcessing.Prohibit` |
| Table size | 200 cols x 10000 rows |

---

## HWP->HWPX Conversion

### Format Detection

```bash
file doc.hwpx   # "Zip archive" -> HWPX (ZIP + OWPML XML)
file doc.hwp    # "HWP Document" -> HWP 5.0 (OLE2 binary, read-only)
```

### Structural Differences

| Aspect | Native HWPX | HWP->HWPX Converted |
|--------|-------------|---------------------|
| Text unit | Short `<t>` per run | Entire paragraph in one `<t>` |
| Title p[0] | secPr + tbl + content | Page number fragments `<t>20</t>` + `<t>1</t>` mixed in |
| Editing | Run-level precise replacement | Raw string replace or whole-paragraph swap needed |

### Editing Strategies for Converted Files

1. **Title**: run-aware replacement -- `set_run_text(p0, 'old', 'new')` (skip page-number runs)
2. **Body**: raw string replace on serialized XML -- `sec0.replace(old, new)`
3. **Multi-`<t>` cells**: use `ReplaceTextInCell()` -- concatenate all `<t>` -> match -> redistribute

---

## Equation Handling (수식)

HWPX equations use Hancom's **proprietary script language**. NOT MathML, NOT LaTeX, NOT OMML.

| Script | Result |
|--------|--------|
| `{1 over 2}` | 1/2 (fraction) |
| `sqrt{x}` | square root of x |
| `x^2`, `x_i` | superscript, subscript |
| `int _0 ^1 f(x)dx` | definite integral |
| `sum _{i=1} ^n` | sigma summation |
| `lim _{x->0}` | limit |
| `matrix{a&b # c&d}` | 2x2 matrix |

```bash
# Create equation
officecli add doc.hwpx /section --type equation --prop 'script=x^2 + y^2 = r^2'
# View all equations
officecli view doc.hwpx objects --object-type equation
# Edit: modify <hp:script> text nodes via Python XML editing
```

Equation scripts are opaque -- edit only `<hp:script>` text, not the binary payload.
Math exam docs (KICE) require `<hp:equation>` for every expression. Never use plain text.

**Verified**: KICE 수능 수학 template (`/private/tmp/kice-full-edit-v2.hwpx`, 836 equations) -- text/equation edit + lineseg strip -> Hancom OK.

---

## Pattern-Match Editing (Python Fallback)

For complex form editing beyond officecli `set`/`find-replace` (KICE exams, regulations):

**Core flow**: unpack HWPX -> strip lineseg -> pattern-match edit XML -> repack ZIP.
Hancom recalculates layout on open. Tools: `hwpx_form_edit.py` (12 CLI commands), `pack.py`.

**Pattern catalog**: 98+ patterns (Plan 99.8), 58 implementation tasks (Plan 99.9).

Key patterns: lineseg strip (R1), checkbox (R6), label detect (R7-R8),
uniform space normalization (R10), checkbox hierarchy (R21), appendix ref (R22).

---

## Legacy Python Fallback

Scripts path: `~/.cli-jaw/skills_ref/hwp/scripts/`

| Task | Tool | Command |
|------|------|---------|
| HWP binary read | `hwp_reader.py` | `python scripts/hwp_reader.py input.hwp` |
| HWP->HWPX convert | `hwp_convert.py` | `python scripts/hwp_convert.py input.hwp output.hwpx` |
| HWPX create (template) | `build_hwpx.py` | `python scripts/build_hwpx.py --template report --output out.hwpx` |
| Text extract | `text_extract.py` | `python scripts/text_extract.py input.hwpx` |
| Unpack/edit/repack | `hwpx_cli.py` | `python scripts/hwpx_cli.py open input.hwpx work/` -> edit -> `save work/ out.hwpx` |
| Search/replace | `hwpx_cli.py` | `python scripts/hwpx_cli.py replace input.hwpx "old" "new" -o out.hwpx` |
| Batch replace | `hwpx_cli.py` | `python scripts/hwpx_cli.py batch-replace input.hwpx map.json -o out.hwpx` |
| Table manipulation | `hwpx_cli.py` | `python scripts/hwpx_cli.py fill-table input.hwpx IDX '{"label>dir":"val"}' -o out.hwpx` |
| HWPX->PDF | `soffice` | `soffice --headless --convert-to pdf --outdir /tmp input.hwpx` |
| Visual QA | PDF->image | `pdftoppm -jpeg -r 150 out.pdf preview` -> sub-agent review |
| Validate | `validate.py` | `python scripts/validate.py input.hwpx` |
| Page count guard | `page_guard.py` | `python scripts/page_guard.py -r ref.hwpx -o out.hwpx` |
| Doc structure | `hwpx_cli.py` | `python scripts/hwpx_cli.py structure input.hwpx` |
| Repair | `hwpx_cli.py` | `python scripts/hwpx_cli.py repair input.hwpx --apply` |

> **Priority**: use officecli first. Python is for operations officecli cannot do
> (HWP binary read, HWP->HWPX conversion, PDF output, template generation, pattern-match editing).

### Lineseg Strip (critical for direct XML editing)

When editing HWPX XML directly (not via officecli), you MUST strip ALL `<hp:linesegarray>`
elements. Stale layout cache causes characters to overlap into a single line.

```python
re.sub(r'<(?:hp:)?linesegarray[^>]*>.*?</(?:hp:)?linesegarray>', '', xml, flags=re.DOTALL)
re.sub(r'<(?:hp:)?linesegarray[^/]*/>', '', result)  # self-closing
```

officecli handles this automatically. This rule applies only to direct Python XML editing.

### Python Environment

```bash
pip install pyhwp lxml   # HWP reading + XML processing
# soffice: LibreOffice (macOS: brew install --cask libreoffice)
# H2Orestart: Java-based HWP conversion engine (for PDF conversion)
```

---

## Anti-Patterns (MUST AVOID)

1. **No equations in math exams = broken output** -- KICE docs require `<hp:equation>` elements
2. **No direct HWP binary editing** -- HWP 5.0 (`.hwp`) is read-only; convert to HWPX first
3. **No XML editing without lineseg strip** -- stale cache causes overlapping text
4. **No cross-format skill loading** -- this skill is `.hwp`/`.hwpx` only

---

## Dependencies

| Tool | Purpose | Required? |
|------|---------|-----------|
| `officecli` (global) | Primary HWPX CLI | **Required** |
| `python3` | Legacy fallback scripts | Optional |
| `soffice` (LibreOffice) | PDF conversion + visual verification | Recommended |
| `Java` (JAVA_HOME) | H2Orestart HWP conversion engine | For HWP->HWPX only |
| `dotnet` | Build officecli from source | For builds only |
