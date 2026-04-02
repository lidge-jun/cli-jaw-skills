---
name: docx
description: "Word DOCX create, read, edit, review. Triggers: Word doc, .docx, reports, memos, letters, templates."
---

# DOCX Skill

Use this skill for any `.docx` task: create, read, edit, review, template-fill, or QA verification.
Triggers: `"Word doc"`, `".docx"`, reports, memos, letters, templates.
Primary tool: **officecli** (`~/.local/bin/officecli`).
Fallback: **Legacy Python / OOXML scripts** only when officecli does not cover the operation.
Do NOT use this skill for PDFs, spreadsheets, or Google Docs.

---

## Tool Discovery

Always confirm syntax from help before guessing:

```bash
officecli --help
officecli docx add
officecli docx set
officecli docx query --help
```

Drill into a specific area when needed:

```bash
officecli docx add paragraph
officecli docx add picture
officecli docx set run
officecli docx set style
```

### Binary Locations

| Binary | Path | Notes |
|--------|------|-------|
| officecli (upstream) | `~/.local/bin/officecli` | Default binary for general DOCX work |
| officecli (fork) | `700_projects/cli-jaw/officecli/build-local/officecli` | Prefer for Korean/Japanese/Chinese authoring because CjkHelper.cs auto-applies fonts/lang tags |

---

## Quick Decision

| Task | Tool | Command | Notes |
|------|------|---------|-------|
| Create blank DOCX | officecli | `officecli create report.docx` | Start from a real Office file, not raw zip surgery |
| Add paragraph | officecli | `officecli add report.docx /body --type paragraph --prop text="Hello"` | Primary write path |
| Edit paragraph/run | officecli | `officecli set report.docx /body/p[1] --prop alignment=center` | Use exact path targeting |
| Read text/outline/stats | officecli | `officecli view report.docx text` | `text`, `annotated`, `outline`, `stats`, `issues`, `html` |
| Query document | officecli | `officecli query report.docx "p[style=Heading1]"` | CSS-like selectors |
| Batch multiple edits | officecli | `officecli batch report.docx --commands '[...]'` | Use for 3+ edits |
| Resident workflow | officecli | `officecli open report.docx` | Keep file hot in memory, but still pass file path on later commands |
| Raw OOXML fallback | officecli | `officecli raw report.docx /document` | Prefer before unpack/pack |
| Template-safe replacement | officecli | `officecli set template.docx / --prop find="{{NAME}}" --prop replace="Acme"` | In-place editing preserves template structure |
| Validation / issue scan | officecli | `officecli validate report.docx` | Pair with `officecli view report.docx issues` |
| Accept tracked changes | officecli | `officecli set report.docx / --prop accept-changes=all` | Also `--prop reject-changes=all` |
| Visual review / PDF conversion | Legacy Python / soffice fallback | `python scripts/soffice.py report.docx --to pdf` | For screenshot-based QA |

---

## Core Command Model

officecli runtime syntax is **file-first**:

```bash
officecli view FILE MODE
officecli add FILE PARENT --type TYPE --prop key=value
officecli set FILE PATH --prop key=value
officecli query FILE "selector"
officecli batch FILE --commands '[{"command":"set",...}]'
officecli open FILE
officecli close FILE
```

The `officecli docx ...` commands are for **help discovery**, not for the runtime mutation syntax.

### PATH Syntax

```text
/body/p[N]                  # Nth paragraph (1-based)
/body/p[N]/r[M]             # Mth run inside paragraph N
/body/tbl[N]                # Nth table
/body/tbl[N]/tr[R]          # Rth row in table N
/body/tbl[N]/tr[R]/tc[C]    # Cth cell in row R
/header[N]                  # Nth header
/footer[N]                  # Nth footer
/bookmark[Name]             # Bookmark by name
/footnote[N]                # Nth footnote
/endnote[N]                 # Nth endnote
/styles/{StyleId}           # Style by ID
/chart[N]                   # Nth chart
/                           # Document root
```

---

## Common officecli Workflows

### Create and populate a document

```bash
officecli create report.docx
officecli add report.docx /body --type paragraph   --prop text="Quarterly Review"   --prop style=Heading1

officecli add report.docx /body --type paragraph   --prop text="Revenue grew 15% year-over-year."   --prop font=Arial   --prop size=11

officecli add report.docx /body --type paragraph   --prop text="First item"   --prop listStyle=bullet
```

### Tables, images, links, fields

```bash
officecli add report.docx /body --type table --prop rows=3 --prop cols=3
officecli set report.docx /body/tbl[1]/tr[1]/tc[1] --prop text="Header A"
officecli set report.docx /body/tbl[1]/tr[1]/tc[2] --prop text="Header B"

officecli add report.docx /body --type picture   --prop path=logo.png   --prop width=2in   --prop height=1in   --prop alt="Company logo"

officecli add report.docx /body/p[1] --type hyperlink   --prop url=https://example.com   --prop text="Visit site"

officecli add report.docx / --type header --prop text="Confidential"
officecli add report.docx /body/p[1] --type pagenum
```

### Read, inspect, and query

```bash
officecli view report.docx text
officecli view report.docx annotated
officecli view report.docx outline
officecli view report.docx stats
officecli view report.docx issues
officecli view report.docx html --browser
officecli get report.docx /
officecli query report.docx "p[style=Heading1]"
officecli query report.docx "p[alignment=center] > r[bold=true]"
```

### Edit existing content safely

```bash
officecli set report.docx /body/p[3] --prop text="Updated content here."
officecli set report.docx /body/p[1] --prop alignment=center
officecli set report.docx /body/p[1]/r[1] --prop bold=true --prop color=FF0000 --prop size=14
officecli set report.docx /styles/Heading1 --prop font=Arial --prop size=28 --prop bold=true
```

---

## Batch Mode

Use batch for 3+ edits so officecli opens/saves once.

```bash
officecli batch report.docx --commands '[
  {
    "command": "add",
    "parent": "/body",
    "type": "paragraph",
    "props": {"text": "Batch Title", "style": "Heading1"}
  },
  {
    "command": "add",
    "parent": "/body",
    "type": "paragraph",
    "props": {"text": "Batch body copy.", "font": "Arial", "size": 11}
  },
  {
    "command": "set",
    "path": "/body/p[1]",
    "props": {"alignment": "center"}
  }
]'
```

For larger batches, prefer `--input ops.json` instead of a giant inline string.

---

## Resident Mode (open / close)

Resident mode keeps the file warm in memory, but runtime commands still use the file path.

```bash
officecli open report.docx
officecli set report.docx /body/p[1] --prop text="Updated title"
officecli add report.docx /body --type paragraph --prop text="New paragraph"
officecli close report.docx
```

Use resident mode for long interactive edit sessions.
Use batch mode when the whole change set is already known up front.

---

## Query Mode

```bash
officecli query report.docx "p[style=Heading1]"
officecli query report.docx "bookmark"
officecli query report.docx "image:no-alt"
officecli query report.docx 'field:contains("DATE")'
```

---

## Template Preservation

When editing branded or client templates:

1. Inspect first: `officecli view template.docx outline`
2. Identify exact targets: `officecli view template.docx text`
3. Edit in place with `officecli set`
4. Validate after every pass: `officecli validate template.docx`

```bash
officecli view template.docx outline
officecli view template.docx text
officecli set template.docx /body/p[3] --prop text="New Q4 figures"
officecli set template.docx / --prop find="{{COMPANY}}" --prop replace="Acme Corp"
officecli validate template.docx
```

### Placeholder replacement pattern

```bash
officecli query template.docx 'r:contains("{{")'
officecli set template.docx /body/p[2]/r[1] --prop text="Actual Company Name"
officecli set template.docx /body/p[5]/r[1] --prop text="2026-03-27"
```

---

## Accessibility (WCAG 2.1 AA)

> 접근성 기준 → see `references/officecli-accessibility.md`

officecli covers the machine-checkable parts of DOCX accessibility well enough for first-pass QA.

```bash
officecli view report.docx issues
officecli query report.docx "image:no-alt"
officecli query report.docx "p[style=Heading1]"
```

### Heading Structure

Headings must follow a logical hierarchy — never skip levels (H1 → H3 is invalid).

```bash
# Check heading hierarchy
officecli view report.docx outline
officecli view report.docx outline | grep -E 'H[1-6]'

# Fix heading levels
officecli set report.docx '/body/p[5]' --prop style=Heading2
```

### Alt-Text for Images

Every image, chart, and non-text element needs alternative text for screen readers.

```bash
# Find images without alt-text
officecli query report.docx 'picture' --json
officecli query report.docx "image:no-alt"

# Add alt-text to a picture
officecli add report.docx /body --type picture \
  --prop path=chart.png --prop width=4in --prop height=3in \
  --prop alt="Bar chart showing Q4 revenue by region"
```

### Table Headers

Tables must have a designated header row for screen readers.

```bash
officecli get report.docx '/body/tbl[1]' --depth 2 --json
```

- Every table must have a header row
- Avoid merged cells (they confuse screen readers)
- Don't use tables for layout — use them for data only

### Reading Order

```bash
# Check for generic link text
officecli view report.docx text | grep -iE 'click here|read more|learn more|here'
```

### Accessibility checklist

- [ ] All images have alt text
- [ ] Heading hierarchy is sequential (no skips)
- [ ] Lists use proper list styles (not manual bullets)
- [ ] Links use descriptive text (not "click here")
- [ ] Document metadata includes title/author when required
- [ ] Body text remains readable at target size (≥ 12pt)
- [ ] Tables keep header semantics where needed
- [ ] No empty paragraphs used for spacing
- [ ] Language metadata is set correctly

---

## QA Verification

```bash
officecli validate report.docx
officecli view report.docx stats
officecli view report.docx text
officecli view report.docx issues
python scripts/soffice.py report.docx --to pdf
```

### QA loop

- [ ] `validate` passes
- [ ] `view ... text` matches expected copy
- [ ] `view ... issues` has no blocking warnings
- [ ] PDF visual review matches the requested layout
- [ ] Fonts/styles stay consistent with the template

---

## CJK Handling (Korean / Japanese / Chinese)

> CJK 상세 규칙 → see `references/officecli-cjk.md`

### Primary: fork binary auto-handles CJK

The cli-jaw fork includes `CjkHelper.cs`, which auto-detects CJK text and applies appropriate fonts and `w:lang` tags.

```bash
OFFICECLI=700_projects/cli-jaw/officecli/build-local/officecli
$OFFICECLI add report.docx /body --type paragraph --prop text="분기별 보고서" --prop style=Heading1
$OFFICECLI add report.docx /body --type paragraph --prop text="매출이 전년 대비 15% 증가했다."
```

### DOCX-Specific CJK Commands

Use `w:rFonts` and `w:lang` for East Asian font and language tag injection:

```bash
# Set East Asian font via raw XML on specific runs
officecli raw-set report.docx /document \
  --xpath '//w:r[w:t[contains(.,"분기")]]/w:rPr' \
  --action append \
  --xml '<w:rFonts w:eastAsia="Malgun Gothic" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'

# Set language tag for Korean spell-checking
officecli raw-set report.docx /document \
  --xpath '//w:r/w:rPr' \
  --action append \
  --xml '<w:lang w:eastAsia="ko-KR" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'

# Set CJK font on a specific run (high-level)
officecli set report.docx '/body/p[1]/r[1]' --prop font.name="Malgun Gothic"

# Batch font application across all runs
officecli batch report.docx --commands '[
  {"command":"set","path":"/body/p[1]/r[1]","props":{"font.name":"Malgun Gothic"}},
  {"command":"set","path":"/body/p[2]/r[1]","props":{"font.name":"Malgun Gothic"}}
]'
```

### Verify CJK Tags

```bash
officecli raw report.docx /document | grep -E 'rFonts|w:lang'
officecli raw report.docx /document | grep kinsoku
```

### CJK Styles

Pre-built CJK document styles are available in `references/cjk-styles/`. See `references/cjk-styles/INDEX.md` for the catalog.

### Legacy fallback

If the fork binary is unavailable, post-process with the legacy script:

```bash
python scripts/ooxml/cjk_utils.py report.docx
```

### Phase 05 note

> `scripts/ooxml/cjk_utils.py` and unpack/pack workflows overlap with officecli raw/set behavior. Phase 05 should consolidate the remaining DOCX OOXML duplication behind officecli-native commands.

---

## Legacy Python CLI (Fallback)

Use these only when officecli does not yet cover the requirement.

| Script | Role | Status |
|--------|------|--------|
| `python scripts/accept_changes.py report.docx` | Accept tracked changes via LibreOffice macro | Fallback |
| `python scripts/soffice.py report.docx --to pdf` | PDF conversion / visual QA | Fallback |
| `python scripts/ooxml/repair.py report.docx` | Repair malformed OOXML | Fallback |
| `python scripts/ooxml/merge_runs.py report.docx` | Merge adjacent identical runs | Fallback |
| `python scripts/ooxml/redline_diff.py report.docx` | Tracked-change validation | Fallback |
| `python scripts/ooxml/unpack.py report.docx unpacked/` | Raw zip surgery | Legacy |
| `python scripts/ooxml/pack.py unpacked/ report_fixed.docx` | Repack OOXML | Legacy |

---

## Dependencies

| Tool | Why it exists | Status |
|------|---------------|--------|
| `~/.local/bin/officecli` | Primary DOCX CLI | Required |
| `700_projects/cli-jaw/officecli/build-local/officecli` | Fork with CJK auto-handling | Recommended for CJK |
| `dotnet` | Runtime/build for officecli | Required for fork builds |
| `python3` | Fallback scripts | Optional fallback |
| `soffice` | PDF conversion / `.doc` migration / macro workflows | Optional fallback |
| `pdftoppm` | Image-based QA after PDF render | Optional fallback |

### Fork build

```bash
cd 700_projects/cli-jaw/officecli
dotnet publish -c Release -o build-local
```
