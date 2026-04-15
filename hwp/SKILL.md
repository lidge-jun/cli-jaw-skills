---
name: hwp
description: "HWP/HWPX create, read, edit, review, template-fill, QA. Triggers: 한글, .hwp, .hwpx, HWP, HWPX, Korean documents, 한컴오피스, OWPML."
---

# HWP/HWPX Document Skill

> **Scope**: HWP/HWPX only. Do NOT reference or load skills for other formats
> (DOCX, PPTX, XLSX, PDF). If the task involves a non-HWP format, stop and tell the user.

Primary tool: **officecli** (on PATH — global install) for ~70% of tasks.
Fallback: **Python OOXML/OWPML scripts** (`scripts/*.py`) for what officecli cannot cover — HWP binary reading, HWP→HWPX conversion, template assembly, pattern-match editing, direct XML edits. See §3.
Triggers: `"한글"`, `".hwpx"`, `".hwp"`, `"HWP"`, `"HWPX"`, Korean documents, 한컴오피스, OWPML.

---

## 1. Quick Decision

| Task | OK? | Command |
|------|-----|---------|
| **Format like existing .hwpx** | Yes | `cp source.hwpx target.hwpx && officecli open target.hwpx` — inherit styles. See §2 |
| **Template-based create** | Yes | `python3 scripts/build_hwpx.py --template {base\|gonmun\|minutes\|proposal\|report} --output out.hwpx` — see §4 |
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
| **Pattern-match editing** | Python (L4) | `scripts/hwpx_cli.py open` → pattern edit XML → `save` — see §16 |
| **Visual QA** | Python (L3) | `scripts/contact_sheet.py` + subagent review with `reference/visual_qa_prompt.md` |
| New form field creation | Blocked | source prototype exists; Hancom verification not closed |
| Open .hwp (binary) | L3 only | `python3 scripts/hwp_reader.py` (read-only) or `scripts/hwp_convert.py IN.hwp OUT.hwpx` |

---

## 2. Reference-Based Editing (Edit > Create from Scratch)

When the user says "format like X.hwpx", "공문 양식처럼", "기존 보고서 스타일", or provides a source file — **start from the source. Don't rebuild from scratch.**

### Workflow

1. **Copy the source**: `cp source.hwpx target.hwpx` — inherits header.xml (styles), section0.xml (structure), META-INF
2. **Open** with `officecli open target.hwpx` — daemon returns immediately (do NOT run as `run_in_background`)
3. **Remove body paragraphs only** — keep `header.xml` (charPr/paraPr/borderFill), `META-INF`, settings
4. **Add new content** using existing styleidref values — they auto-apply

### Why This Matters

HWPX header.xml holds all style definitions (charPr, paraPr, borderFill, listItems). Rebuilding these from scratch:

- Breaks styleidref cross-references in section0.xml
- Loses consistent 공문/보고서 visual conventions
- Breaks validation (`officecli validate` fails)
- Takes 10× longer than modifying the copy

### Template Sources (priority order)

1. **User-provided source file** — first-class template
2. **`tests/fixtures/agentic/*.hwpx`** — realistic samples (gonmun with headings, report, minutes with tables)
3. **`templates/{base,gonmun,minutes,proposal,report}/`** — **Template Assembly system** (see §4)
4. **`officecli create`** blank — only when nothing else applies

### Example — Official Letter (공문) Reuse

```bash
# Method A: direct copy
cp SampleGonmun.hwpx MyGonmun.hwpx
officecli open MyGonmun.hwpx
# Use /table/fill to replace label-value cells
officecli set MyGonmun.hwpx /table/fill --prop '문서번호=2026-123'
officecli set MyGonmun.hwpx /table/fill --prop '수신=관계 부서장'
officecli close MyGonmun.hwpx

# Method B: template assembly (see §4)
python3 scripts/build_hwpx.py --template gonmun --output MyGonmun.hwpx
# Then edit with officecli as above
```

---

## 3. Reference Materials & Script Map

officecli covers most HWPX operations. For template assembly, direct XML editing, HWP conversion, and pattern matching, use these references + Python scripts.

### References (`reference/` — singular)

| File | Read when | Contains |
|------|-----------|----------|
| `reference/hwpx-format.md` | **Before any direct XML edit** | OWPML ZIP structure, namespaces, file layout, mimetype |
| `reference/header-xml-guide.md` | Adding/modifying charPr/paraPr/borderFill/listItems styles | How to add new styles to header.xml — required reading for style customization |
| `reference/section0-xml-guide.md` | Paragraph/table/mixed-formatting direct XML | XML template for section0.xml bodies |
| `reference/style_id_maps.md` | **Style ID lookup for template overlay** | Complete style ID index for base/gonmun/minutes/proposal/report templates |
| `reference/dependencies.md` | First-time setup / environment check | Python/system packages needed (pyhwp, lxml, soffice, JAVA_HOME) |
| `reference/visual_qa_prompt.md` | Visual QA via subagent | Ready-to-use prompt for PDF-image inspection |
| `reference/table_templates/*.xml` | Inserting pre-built tables | 2x6, 3x3, 4x4, 5x4 grid XML fragments |

### Scripts (`scripts/`) — Python OWPML Toolkit

| Script | Run when | Command |
|--------|----------|---------|
| `scripts/hwpx_cli.py` | Unified Python CLI (14+ commands) — unpack, save, text, search, replace, batch-replace, tables, fill-table, validate, page-guard, toc, chunk, search-chunks, repair, content-check, insert-table, structure | `python3 scripts/hwpx_cli.py {command} ...` |
| `scripts/build_hwpx.py` | **Template-based creation** (§4) | `python3 scripts/build_hwpx.py --template {type} --output X.hwpx` |
| `scripts/analyze_template.py` | Inspect template structure before overlay | `python3 scripts/analyze_template.py work/` |
| `scripts/create_document.py` | Create empty or custom HWPX | `python3 scripts/create_document.py OUT.hwpx` |
| `scripts/table_builder.py` | Build table XML from Python objects | Used internally by `insert-table` command |
| `scripts/page_guard.py` | Detect paragraph/table/text drift vs reference doc | `python3 scripts/page_guard.py -r ref.hwpx -o out.hwpx` |
| `scripts/contact_sheet.py` | QA contact sheet (page grid image) | `python3 scripts/contact_sheet.py INPUT.pdf sheet.png` |
| `scripts/validate.py` | 9-level structural validation (Python fallback) | `python3 scripts/validate.py INPUT.hwpx` |
| `scripts/hwp_reader.py` | Read HWP 5.0 binary (OLE2, read-only) | `python3 scripts/hwp_reader.py INPUT.hwp` |
| `scripts/hwp_convert.py` | HWP → HWPX conversion (H2Orestart-based) | `python3 scripts/hwp_convert.py IN.hwp OUT.hwpx` |
| `scripts/text_extract.py` | Extract plain text from HWPX | `python3 scripts/text_extract.py INPUT.hwpx` |
| `scripts/ooxml/pack.py` / `unpack.py` | ZIP atomicity helpers | Used internally by other scripts |

### Editing Escalation Ladder

When officecli can't do the job, escalate in this order:

| Level | When | Tool |
|-------|------|------|
| **L1** officecli high-level | Typical add/set/remove, label-fill, view modes | `officecli add/set/remove/query/view/merge` |
| **L2** officecli `raw` / `raw-set` | Direct section0.xml / header.xml tweaks | `officecli raw FILE /Contents/section0.xml` or `raw-set` |
| **L3** Python script | Bulk find/replace, batch-replace, template assembly, pattern-match | `python3 scripts/hwpx_cli.py ...` or `scripts/build_hwpx.py` |
| **L4** Unpack → edit XML → repack (with lineseg strip) | KICE exams, regulations, anything requiring multi-file XML edit | `scripts/hwpx_cli.py open` → edit `work/Contents/*.xml` → strip lineseg → `save` |

**Escalation signals:**
- officecli cannot add custom style → **L2** (raw-set header.xml) + read `reference/header-xml-guide.md`
- Custom template overlay → **L3** (`scripts/build_hwpx.py`) + read `reference/style_id_maps.md`
- **HWP binary** input → **L3** (`scripts/hwp_convert.py` first, then edit HWPX)
- **Multi-file pattern match** (exam questions, regulations) → **L4** (see §16)
- **Style ID lookup** → Read `reference/style_id_maps.md` FIRST

---

## 4. Template Assembly (HWP 전용)

HWP has a unique **base + overlay template system**. Most HWPX creation for 공문/보고서/회의록/제안서 should use this instead of `officecli create` blank.

### Available Templates

| Template | Purpose |
|----------|---------|
| `templates/base/` | Empty HWPX skeleton (mimetype, META-INF, empty header/section) |
| `templates/gonmun/` | Official letter (공문) styles — 문서번호, 수신, 참조, 제목, 본문 |
| `templates/minutes/` | Meeting minutes (회의록) styles — 일시, 장소, 참석자, 안건, 결정사항 |
| `templates/proposal/` | Proposal (제안서) styles — 제안개요, 배경, 내용, 기대효과 |
| `templates/report/` | Report (보고서) styles — 요약, 현황, 분석, 제언 |

### Method 1: build_hwpx.py (recommended)

```bash
python3 scripts/build_hwpx.py --template report --output Q4Report.hwpx
# Then edit content with officecli
officecli open Q4Report.hwpx
officecli set Q4Report.hwpx /table/fill --prop '제목=2026 Q4 보고'
# ... continue editing ...
```

### Method 2: Manual Overlay (for customization)

```bash
# 1. Copy base skeleton
cp -r templates/base/ work/

# 2. Overlay domain-specific styles
cp -r templates/gonmun/* work/Contents/

# 3. Edit header.xml and section0.xml as needed
#    Reference: reference/header-xml-guide.md, reference/section0-xml-guide.md
#    Style IDs: reference/style_id_maps.md

# 4. Repack as HWPX (ZIP with strip + minify)
python3 scripts/ooxml/pack.py work/ out.hwpx

# 5. Validate
officecli validate out.hwpx
```

### Style ID Reference

Every template defines charPr/paraPr/borderFill style IDs. To customize without breaking cross-references:

1. Read `reference/style_id_maps.md` for the template's complete ID index
2. Use `scripts/analyze_template.py work/` to inspect current structure
3. Add new styles via `reference/header-xml-guide.md` patterns — preserve existing IDs

---

## 5. Subskill & Resource Map

HWP does not have bonus subskill folders (unlike docx's `officecli-academic-paper/` or pptx's `morph-ppt/`). All auxiliary resources live directly inside this skill:

| Resource | Location | Purpose |
|----------|----------|---------|
| **Reference docs** | `./reference/*.md` | XML guides, style ID maps, QA prompts — see §3 |
| **Python scripts** | `./scripts/*.py` | OOXML toolkit, HWP conversion, template assembly — see §3 |
| **Templates (base+overlay)** | `./templates/{base,gonmun,minutes,proposal,report}/` | Template assembly system — see §4 |
| **Test fixtures** | `./tests/fixtures/` | Pre-built `.hwpx` samples usable as `cp` sources — see §2 |

If future bonus subskills are added (e.g., `./creating.md`, `./editing.md`, `./officecli-kice-exam/`), read them only for the specific task at hand.

---

## 6. Design Principles for Korean Documents

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

## 7. Mandatory Verification (NEVER SKIP)

After ANY HWPX edit operation, ALWAYS execute these in order:

```bash
# 1. Structural validation (MUST pass)
officecli validate output.hwpx

# 2. PDF visual verification (MUST check)
soffice --headless --convert-to pdf --outdir /tmp output.hwpx
# Verify: table positions, guide text removed, checkboxes correct,
#         merged cell text in correct row, numbers not corrupted

# 3. Visual QA via subagent (use reference/visual_qa_prompt.md)
#    python3 scripts/contact_sheet.py /tmp/output.pdf sheet.png
#    Then: dispatch subagent with reference/visual_qa_prompt.md

# 4. If Hancom Office available, also open .hwpx directly
```

**Skip PDF verification = unverified output. Always inform user if soffice is unavailable.**

---

## 8. Prerequisite Check

```bash
which officecli || echo "MISSING: install officecli first — see https://officecli.ai"
which soffice || echo "OPTIONAL: install LibreOffice for PDF verification"
python3 -c "import lxml; import pyhwp" 2>/dev/null || echo "OPTIONAL: pip install lxml pyhwp (for Python fallbacks)"
echo "JAVA_HOME=$JAVA_HOME (required for H2Orestart HWP→HWPX conversion)"
```

## 9. Tool Discovery

Always confirm syntax from help before guessing:

```bash
officecli --help
officecli hwpx add
officecli hwpx set
officecli hwpx view --help
python3 scripts/hwpx_cli.py --help
python3 scripts/build_hwpx.py --help
```

---

## 10. Core Workflows

### Create & Import & Merge

```bash
officecli create doc.hwpx                                    # empty doc
officecli create doc.hwpx --from-markdown input.md           # MD->HWPX (JUSTIFY default)
officecli create doc.hwpx --from-markdown input.md --align left  # left-aligned
officecli merge template.hwpx out.hwpx --data '{"이름":"홍길동"}'  # template {{key}} replace
officecli merge template.hwpx out.hwpx --data data.json           # JSON file data

# Template assembly (see §4)
python3 scripts/build_hwpx.py --template gonmun --output gonmun.hwpx
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

### Resident Mode (live connection)

```bash
officecli open doc.hwpx          # returns IMMEDIATELY; daemon in bg
officecli view text               # view without re-opening
officecli set '/p[1]' --prop bold=true
officecli close                   # close session
```

> **Do NOT run `officecli open` as a background shell job.** It returns immediately and the daemon lives in the background automatically. Running it as a monitored shell creates zombies and file locks.

### Batch Mode (multiple commands)

```bash
officecli batch doc.hwpx <<'EOF'
view text
view stats
view forms --auto
EOF
```

> **Error decoding:** `'X' is an invalid start of a value` = shell syntax leaked into JSON-style batch. Use heredoc with single-quoted delimiter `<<'EOF'`.

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

### Pre-Delivery Checklist

- [ ] `officecli validate` passes (0 errors)
- [ ] `soffice --headless --convert-to pdf` → visual check
- [ ] Table cells in correct positions (cellAddr mapping)
- [ ] Guide text (※, 예시) fully removed
- [ ] Checkboxes □/■ in intended cells only
- [ ] Merged cell text in correct row
- [ ] If Hancom available, open .hwpx directly

---

## 11. Common Pitfalls

| Pitfall | Correct Approach |
|---------|-----------------|
| `--props text=Hello` | `--prop text=Hello` -- singular `--prop` always |
| `/body/p[1]` path | HWPX uses `/section[1]/p[1]` -- section-based, not body |
| `.hwp` (binary) open | Convert to `.hwpx` first (Hancom Office or `scripts/hwp_convert.py`) |
| Unquoted `[N]` in shell | `"/section[1]/p[1]"` -- always quote paths |
| fontsize omitted | `--prop fontsize=11` always -- prevents charPr 0 pollution |
| `officecli view file.hwpx` (no mode) | Error. Must specify: `text`, `markdown`, `tables`, etc. |
| Manual table mapping | `view tables` replaces manual inspection |
| HWP->HWPX text replace | Whole-paragraph `<t>` -- use raw string replace; p[0] may contain page-number fragments |
| **Recreating header.xml styles that exist in template** | `cp source.hwpx target.hwpx` first. Read `reference/style_id_maps.md` before custom styling. See §2 |
| **`officecli open` as background shell** | Run foreground — returns immediately, daemon runs in bg automatically. Background shell spawn creates zombies |
| **Direct XML edit without lineseg strip** | Stale `<hp:linesegarray>` cache causes text overlap. Use `scripts/hwpx_cli.py` (strips automatically) or apply lineseg strip manually (see §16) |
| **Custom style work without reading reference/** | `reference/header-xml-guide.md` + `reference/style_id_maps.md` are mandatory reading. See §3 |

### Essential Rules (from subskill)

- **Auto-normalization**: PUA removal and uniform spacing collapse are applied automatically.
- **Transport parity**: CLI, Resident, and MCP all support the same view modes (tables, markdown, objects, forms).

---

## 12. Form Recognition & Fill

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

## 13. Security

| Check | Limits |
|-------|--------|
| ZIP bomb | 1000 entries, 200 MB, 100:1 ratio |
| Path traversal | null byte, `..`, absolute path, drive letter, symlink |
| XXE | `DtdProcessing.Prohibit` |
| Table size | 200 cols x 10000 rows |

---

## 14. HWP->HWPX Conversion

### Format Detection

```bash
file doc.hwpx   # "Zip archive" -> HWPX (ZIP + OWPML XML)
file doc.hwp    # "HWP Document" -> HWP 5.0 (OLE2 binary, read-only)
```

### Conversion

```bash
# Python fallback (H2Orestart-based)
python3 scripts/hwp_convert.py input.hwp output.hwpx

# Read-only HWP inspection (no conversion)
python3 scripts/hwp_reader.py input.hwp
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

## 15. Equation Handling (수식)

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

## 16. Pattern-Match Editing (Python L4 Fallback)

For complex form editing beyond officecli `set`/`find-replace` (KICE exams, multi-section regulations, fragmented text nodes):

**Core flow**: unpack HWPX → strip lineseg → pattern-match edit XML → repack ZIP. Hancom recalculates layout on open.

Tools: `scripts/hwpx_cli.py` (unpack/search/replace/batch-replace/fill-table — strips lineseg automatically), `scripts/ooxml/pack.py`.

### Key Patterns (non-exhaustive)

| Pattern | Description | Where |
|---------|-------------|-------|
| **Lineseg strip** | Remove stale `<hp:linesegarray>` cache | Apply on every direct XML write (see below) |
| **Checkbox substitution** | `□` → `☑`, with multi-`<t>` node handling | `hwpx_cli.py replace` or regex |
| **Label→value detection** | Label cell adjacent to value cell (right/down/left/up) | `officecli set /table/fill` handles most cases |
| **Uniform-space normalization** | `"홍 길 동"` ↔ `"홍길동"` conversion | Automatic in officecli; manual in direct XML |
| **Checkbox hierarchy** | `□` (section) → `○` (item) → `-` (detail) → `*` (footnote) | Regulation-specific |
| **Appendix references** | `[별첨 제N호]`, `[별지 N]` linked to form templates | Regulation-specific |
| **p[0] Monster** | secPr + tbl + question 1 text merged in first paragraph (HWP-converted files) | `scripts/hwp_convert.py` output requires paragraph-level replace |
| **Equation interleaving** | `<t>` ↔ `<equation>` alternating | Skip equations during text extraction |

For repository-internal pattern catalog references (Plan 99.8 / 99.9) see the devlog; the scripts above implement the concrete operations.

### Lineseg Strip (critical for direct XML editing)

When editing HWPX XML directly (NOT via officecli or scripts/hwpx_cli.py), you MUST strip ALL `<hp:linesegarray>` elements. Stale layout cache causes characters to overlap into a single line.

```python
import re
xml = re.sub(r'<(?:hp:)?linesegarray[^>]*>.*?</(?:hp:)?linesegarray>', '', xml, flags=re.DOTALL)
xml = re.sub(r'<(?:hp:)?linesegarray[^/]*/>', '', xml)  # self-closing
```

officecli and `scripts/hwpx_cli.py` handle this automatically. This rule applies only to raw Python XML editing.

---

## 17. Anti-Patterns (MUST AVOID)

1. **No equations in math exams = broken output** -- KICE docs require `<hp:equation>` elements
2. **No direct HWP binary editing** -- HWP 5.0 (`.hwp`) is read-only; convert to HWPX first via `scripts/hwp_convert.py`
3. **No XML editing without lineseg strip** -- stale cache causes overlapping text. Use `scripts/hwpx_cli.py` (auto-strips) or apply the regex in §16
4. **No cross-format skill loading** -- this skill is `.hwp`/`.hwpx` only
5. **Rebuilding styles that exist in template** — when user provides a source .hwpx, `cp` first and read `reference/style_id_maps.md`. See §2
6. **Ignoring reference materials** — `reference/header-xml-guide.md`, `reference/section0-xml-guide.md`, and `reference/style_id_maps.md` are mandatory reading for custom XML work. See §3

---

## 18. Dependencies

| Tool | Purpose | Required? |
|------|---------|-----------|
| `officecli` (global) | Primary HWPX CLI | **Required** |
| `python3` | Fallback scripts (`scripts/*.py`) | **Required for L3/L4** |
| `lxml` | XML processing for scripts/* | Required for L3/L4 (`pip install lxml`) |
| `pyhwp` | HWP 5.0 binary reading | Required for HWP→HWPX |
| `soffice` (LibreOffice) | PDF conversion + visual verification | Recommended |
| `Java` (JAVA_HOME) | H2Orestart HWP conversion engine | For HWP→HWPX only |
| `dotnet` | Build officecli from source | For builds only |
