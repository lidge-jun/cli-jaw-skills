---
name: docx
description: "Word DOCX create, read, edit, review. Triggers: Word doc, .docx, reports, memos, letters, templates."
---

# DOCX Skill

Use this skill for any `.docx` task: create, read, edit, review, template-fill, or QA verification.
Triggers: `"Word doc"`, `".docx"`, reports, memos, letters, templates.
Primary tool: **officecli** (`officecli` (PATH)).
Fallback: **Legacy Python / OOXML scripts** only when officecli does not cover the operation.

**DOCX only.** Do NOT use this skill for PDFs, spreadsheets, HWPX, Google Docs, or any other format.

---

## 1. Quick Decision

| Task | Tool | Command pattern | Notes |
|------|------|-----------------|-------|
| Create blank DOCX | officecli | `officecli create report.docx` | Start from real Office file |
| Add paragraph | officecli | `officecli add FILE /body --type paragraph --prop text="..."` | Primary write path |
| Edit paragraph/run | officecli | `officecli set FILE /body/p[N] --prop ...` | Exact path targeting |
| Read text/outline/stats | officecli | `officecli view FILE text` | Modes: `text`, `annotated`, `outline`, `stats`, `issues`, `html` |
| Query document | officecli | `officecli query FILE "p[style=Heading1]"` | CSS-like selectors |
| Template-safe replacement | officecli | `officecli set FILE / --prop find="{{X}}" --prop replace="Y"` | Preserves template structure |
| Validation / issue scan | officecli | `officecli validate FILE` | Pair with `view FILE issues` |
| Accept tracked changes | officecli | `officecli set FILE / --prop accept-changes=all` | Also `reject-changes=all` |
| PDF conversion / visual QA | soffice | `soffice --headless --convert-to pdf FILE` | Screenshot-based QA |
| Read / analyze content | officecli | Use `view` and `get` commands | See Core Workflows |
| Edit existing document | -- | Read [editing.md](./editing.md) | Detailed editing guides |
| Create from scratch | -- | Read [creating.md](./creating.md) | Detailed creation recipes |

---

## 2. Subskill References

Additional detail lives in companion files. Load only the one you need.

| Subskill | Path | When to use |
|----------|------|-------------|
| **officecli-academic-paper** | `./officecli-academic-paper/SKILL.md` | Academic papers, citations, bibliography, TOC for papers |
| **creating.md** | `./creating.md` | Detailed creation recipes (new documents from scratch) |
| **editing.md** | `./editing.md` | Detailed editing guides (modify existing documents) |

### Decision flow

```
Is the document an academic paper (thesis, journal, conference)?
  YES --> read officecli-academic-paper/SKILL.md
  NO  --> continue with this file
Need detailed creation steps?  --> also read ./creating.md
Need detailed editing steps?   --> also read ./editing.md
```

---

## 3. Design Principles for Business Documents

### 3.1 Heading Hierarchy

- **H1**: Document title (one per document)
- **H2**: Major sections
- **H3**: Subsections under H2
- Never skip levels (H1 -> H3 is invalid). Table of Contents depends on correct heading structure.

```bash
# Verify heading hierarchy
officecli view report.docx outline
```

### 3.2 Color Palette

Use professional, muted tones only:

| Purpose | Allowed colors | Hex examples |
|---------|---------------|--------------|
| Headings, emphasis | Navy | `#003366`, `#1B2A4A` |
| Body accents, borders | Charcoal | `#333333`, `#4A4A4A` |
| Highlights, callouts | Forest green | `#2E5E3F`, `#1A4731` |

**NEVER** use rainbow colors, bright primary colors, or more than 3 accent colors in a single document.

### 3.3 Font Selection

| Script | Primary font | Fallback |
|--------|-------------|----------|
| Korean | Malgun Gothic | Pretendard |
| English / Latin | Calibri | Aptos |

The CJK fork auto-applies East Asian fonts, but verify with:

```bash
officecli raw report.docx /document | grep rFonts
```

### 3.4 Typography

Choose a readable body font (Calibri, Cambria, Georgia, Times New Roman). Keep body at 11-12pt. Headings should step up: **H1=18pt minimum (20pt preferred for long documents)**, H2=14pt bold, H3=12pt bold.

### 3.5 Spacing & Page Setup

Use paragraph spacing (`spaceBefore`/`spaceAfter`) instead of empty paragraphs. Line spacing of 1.15x-1.5x for body text.

Always set margins explicitly. US Letter default: `pageWidth=12240`, `pageHeight=15840`, margins=1440 (1 inch).

### 3.6 Table of Contents

TOC generation depends entirely on heading styles. Before inserting TOC:

1. Confirm all headings use proper Heading1/Heading2/Heading3 styles (not manual bold+size).
2. Run `officecli view FILE outline` to verify hierarchy.
3. Generate TOC via the subskill method.

### 3.7 Table Design & Color Usage

Alternate row shading for readability. Header row with contrasting background. Consistent cell padding.
Use color sparingly -- accent color for headings or table headers, not rainbow formatting.

### 3.8 Content-to-Element Mapping

| Content Type | Recommended Element(s) | Why |
|---|---|---|
| Sequential items | Bulleted list (`listStyle=bullet`) | Scanning is faster than inline commas |
| Step-by-step process | Numbered list (`listStyle=numbered`) | Numbers communicate order |
| Comparative data | Table with header row | Columns enable side-by-side comparison |
| Trend data | Embedded chart (`chartType=line/column`) | Visual pattern recognition |
| Key definition | Hanging indent paragraph | Offset term from definition |
| Legal/contract clause | Numbered list with bookmarks | Cross-referencing via bookmarks |
| Mathematical content | Equation element (`formula=LaTeX`) | Proper OMML rendering |
| Citation/reference | Footnote or endnote | Keeps body text clean |
| Pull quote / callout | Paragraph with border + shading | Visual distinction from body |
| Multi-section layout | Section breaks with columns | Column control per section |

---

## 4. Mandatory Verification (NEVER SKIP)

After ANY DOCX creation or edit, ALWAYS execute both steps:

```bash
# Step 1: Structural validation
officecli validate output.docx

# Step 2: Visual PDF verification
soffice --headless --convert-to pdf --outdir /tmp output.docx
# Open/inspect PDF to confirm: formatting, tables, images, headers/footers
```

- Skip PDF verification = **unverified output**. Inform user if soffice is unavailable.
- If `validate` reports errors, fix them before delivering the file.

---

## 5. Prerequisite Check

```bash
which officecli || echo "MISSING: install officecli first — see https://officecli.ai"
which soffice || echo "OPTIONAL: install LibreOffice for PDF verification"
```

## 6. Tool Discovery

Always confirm syntax from help before guessing:

```bash
officecli --help
officecli docx add
officecli docx set
officecli docx query --help
```

Drill into a specific area:

```bash
officecli docx add paragraph
officecli docx add picture
officecli docx set run
officecli docx set style
```

| Binary | Path | Notes |
|--------|------|-------|
| officecli | `officecli` (PATH) | Global install includes CJK fork with CjkHelper.cs -- auto-applies fonts/lang tags |

---

## 7. Core Workflows

### 6.1 Execution Model

**Run commands one at a time. Do not write all commands into a shell script and execute it as a single block.**

OfficeCLI is incremental: every `add`, `set`, and `remove` immediately modifies the file and returns output.

1. **One command at a time, then read the output.** Check the exit code before proceeding.
2. **Non-zero exit = stop and fix immediately.** Do not continue building on a broken state.
3. **Verify after structural operations.** After adding a style, table, chart, or section, run `get` or `validate` before building on top of it.

### 6.2 Reading & Analyzing

```bash
officecli view doc.docx text                    # Full text extraction
officecli view doc.docx text --max-lines 200    # Truncated extraction
officecli view doc.docx text --start 1 --end 50 # Range extraction
officecli view doc.docx outline                 # Structure: stats, headings, headers/footers
officecli view doc.docx annotated               # Style/font/size per run, equations as LaTeX
officecli view doc.docx stats                   # Paragraph count, style/font distribution
```

### 6.3 Element Inspection

```bash
officecli get doc.docx /                        # Document root (metadata, page setup)
officecli get doc.docx /body --depth 1           # List body children
officecli get doc.docx "/body/p[1]"              # Specific paragraph
officecli get doc.docx "/body/p[1]/r[1]"         # Specific run
officecli get doc.docx "/body/tbl[1]" --depth 3  # Table structure
officecli get doc.docx /styles                   # Style definitions
officecli get doc.docx "/styles/Heading1"        # Specific style
officecli get doc.docx "/header[1]"              # Header/footer
officecli get doc.docx /numbering                # Numbering definitions
officecli get doc.docx "/body/p[1]" --json       # JSON output for scripting
```

### 6.4 CSS-like Queries

```bash
officecli query doc.docx 'paragraph[style=Heading1]'            # By style
officecli query doc.docx 'p:contains("quarterly")'              # By text content
officecli query doc.docx 'p:empty'                              # Empty paragraphs
officecli query doc.docx 'image:no-alt'                         # Images without alt text
officecli query doc.docx 'p[alignment=center] > r[bold=true]'   # Compound selectors
officecli query doc.docx 'paragraph[size>=24pt]'                # By size
officecli query doc.docx 'field[fieldType!=page]'               # Fields by type
```

### 6.5 Headers & Footers

**Standard footer setup (always use this pattern for documents with a cover page):**

> **Known CLI bug:** `--prop field=page` is **silently ignored** in `add --type footer` commands. The footer is created with static text only. You **must** use `raw-set` to inject the PAGE field after creating the footer.

```bash
# Step 1. Empty footer for cover page (auto-enables differentFirstPage)
officecli add doc.docx / --type footer --prop type=first --prop text=""

# Step 2. Default footer with static "Page " text
officecli add doc.docx / --type footer --prop text="Page " --prop type=default --prop alignment=center --prop size=9pt --prop font=Calibri

# Step 3. Inject PAGE field via raw-set (footer[2] = default when first-page footer also exists)
officecli raw-set doc.docx "/footer[2]" \
  --xpath "//w:p" \
  --action append \
  --xml '<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="18"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r><w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="18"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r><w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="18"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>'
```

> **Footer index rule:** When both a first-page footer and a default footer are added, the default footer is `/footer[2]`. If there is no first-page footer, the default footer is `/footer[1]`. Always verify with `officecli get doc.docx "/footer[2]"` (or `"/footer[1]"`) to confirm the `<w:fldChar>` element is present.

> **LibreOffice rendering note:** Page number fields may display as static "Page" in LibreOffice PDF preview -- this is a LibreOffice limitation. Open in Microsoft Word to see actual page numbers. Confirm the field with `officecli get doc.docx "/footer[2]"` -- output must show `fldChar` children.

### 6.6 Resident Mode (Performance)

**Always use `open`/`close` -- it is the smart default.** Every command benefits: no repeated file I/O.

```bash
officecli open doc.docx           # Load once into memory
officecli add doc.docx ...        # All commands run in memory -- fast
officecli set doc.docx ...
officecli close doc.docx          # Write once to disk
```

### 6.7 Batch Mode (Performance)

Execute multiple operations in a single open/save cycle:

```bash
cat <<'EOF' | officecli batch doc.docx
[
  {"command":"add","parent":"/body","type":"paragraph","props":{"text":"Introduction","style":"Heading1"}},
  {"command":"add","parent":"/body","type":"paragraph","props":{"text":"This report covers Q4 results.","font":"Calibri","size":"11pt"}}
]
EOF
```

Batch supports: `add`, `set`, `get`, `query`, `remove`, `move`, `swap`, `view`, `raw`, `raw-set`, `validate`.

Batch fields: `command`, `path`, `parent`, `type`, `from`, `to`, `index`, `after`, `before`, `props` (dict), `selector`, `mode`, `depth`, `part`, `xpath`, `action`, `xml`.

`parent` = container to add into (for `add`). `path` = element to modify (for `set`, `get`, `remove`, `move`, `swap`).

---

## 8. Common Pitfalls

| Pitfall | Correct Approach |
|---------|-----------------|
| `--name "foo"` | Use `--prop name="foo"` -- all attributes go through `--prop` |
| Guessing property names | Run `officecli docx set paragraph` to see exact names |
| `\n` in shell strings | Use `\\n` for newlines in `--prop text="line1\\nline2"` |
| Modifying an open file | Close the file in Word first |
| Hex colors with `#` | Use `FF0000` not `#FF0000` -- no hash prefix |
| Paths are 1-based | `/body/p[1]`, `/body/tbl[1]` -- XPath convention |
| `--index` is 0-based | `--index 0` = first position -- array convention |
| Unquoted `[N]` in zsh/bash | Shell glob-expands `/body/p[1]` -- always quote paths: `"/body/p[1]"` |
| Spacing in raw numbers | Use unit-qualified values: `'12pt'`, `'0.5cm'`, `'1.5x'` not raw twips |
| Empty paragraphs for spacing | Use `spaceBefore`/`spaceAfter` properties on paragraphs |
| `$` in `--prop text=` (shell) | Use single quotes: `--prop text='$50M'` |
| `$` and `'` in batch JSON | Use heredoc: `cat <<'EOF' \| officecli batch` |
| Wrong border format | Use `style;size;color;space` format: `single;4;FF0000;1` |
| listStyle on run | `listStyle` is a paragraph property, not a run property |
| Row-level bold/color/shd | Row `set` only supports `height`, `header`, and `c1/c2/c3` text shortcuts. Use cell-level `set` for formatting |
| Section vs root property names | Section uses `pagewidth`/`pageheight` (lowercase). Document root uses `pageWidth`/`pageHeight` (camelCase) |
| `--prop field=page` in footer | **SILENTLY IGNORED** in `add --type footer`. Must use `raw-set` to inject `<w:fldChar>`. See Headers & Footers section. |
| Page number on cover | Adding `--type footer --prop type=first` auto-enables differentFirstPage. Do NOT use `set / --prop differentFirstPage=true` -- unsupported and silently fails |
| TOC skipped for multi-heading docs | Any document with 3+ headings requires a TOC. Add with `--type toc --index 0` after cover page break |
| Code block indentation via spaces | Use `ind.left` paragraph property (e.g. `--prop ind.left=720`) -- consecutive spaces produce warnings |

---

## 9. Known Issues

| Issue | Workaround |
|---|---|
| **No visual preview** | Unlike pptx (SVG/HTML), docx has no built-in rendering. Use `view text`/`outline`/`annotated`/`issues` for verification. Users must open in Word for visual check. |
| **Track changes creation requires raw XML** | OfficeCLI can accept/reject tracked changes but cannot create them via high-level commands. Use `raw-set` with XML. |
| **Tab stops may require raw XML** | Tab stop creation is not exposed in high-level commands. Use `raw-set` to add tab stop definitions. |
| **Chart series cannot be added after creation** | `set --prop data=` can only update existing series, not add new ones. Delete and recreate the chart. |
| **Complex numbering definitions** | `listStyle=bullet/numbered` covers simple cases. For multi-level lists, use `numId`/`numLevel` properties. |
| **Shell quoting in batch with echo** | Use heredoc: `cat <<'EOF' \| officecli batch doc.docx`. |
| **Batch intermittent failure** | ~1-in-15 batch operations may fail with "Failed to send to resident". Retry or close/reopen file. Split large batches into 10-15 operation chunks. |
| **Table-level `padding` produces invalid XML** | Do not use `set tbl[N] --prop padding=N`. Use cell-level `padding.top`/`padding.bottom`. If already applied, remove with `raw-set --xpath "//w:tbl[N]/w:tblPr/w:tblCellMar" --action remove`. |
| **Internal hyperlinks not supported** | `hyperlink` only accepts absolute URIs. For `#bookmark` links, use `raw-set` with `<w:hyperlink w:anchor="bookmarkName">`. |
| **Table `--index` positioning unreliable** | `--index N` on `add /body --type table` may be ignored. Add content in desired order, or remove/re-add elements. |
| **`\mathcal` in equations causes validation errors** | Use `\mathit` or plain letters instead. |
| **`view text` shows "1." for all numbered items** | Display-only limitation. Rendered output in Word/LibreOffice shows correct auto-incrementing numbers. |
| **`chartType=pie`/`doughnut` in LibreOffice PDF** | Do NOT use these chart types when LibreOffice PDF delivery is required. Slices are invisible. Use `chartType=column` or `bar` instead. |

---

## 10. QA Checklist

**Assume there are problems. Your job is to find them.**

### Issue Detection

```bash
officecli view doc.docx issues
officecli view doc.docx issues --type format
officecli view doc.docx issues --type content
officecli view doc.docx issues --type structure
```

### Content QA

```bash
officecli view doc.docx text
officecli view doc.docx outline
officecli query doc.docx 'p:empty'
officecli query doc.docx 'image:no-alt'

# Check for leftover placeholders
officecli query doc.docx 'p:contains("lorem")'
officecli query doc.docx 'p:contains("xxxx")'
officecli query doc.docx 'p:contains("placeholder")'
```

### Pre-Delivery Checklist

- [ ] Metadata set (title, author)
- [ ] PAGE field injected in footer -- verify with `officecli get doc.docx "/footer[2]" --depth 3` (must show `fldChar` elements). **Required: raw-set PAGE field injection** -- `--prop field=page` in add command is silently ignored. If no first-page footer, use `"/footer[1]"`.
- [ ] First-page footer added (`--prop type=first --prop text=""`) if document has a cover page
- [ ] Cover page content fills >= 60% of the page (accent bars, subtitle, author, date, contact info)
- [ ] TOC present when document has 3+ headings (`--type toc --prop levels="1-3" --prop title="Table of Contents" --prop hyperlinks=true --prop pagenumbers=true --index 0`)
- [ ] Last page content fills >= 40% of the page
- [ ] Heading hierarchy correct (no skipped levels)
- [ ] No empty paragraphs used as spacing
- [ ] All images have alt text
- [ ] Tables have header rows
- [ ] Document validates with `officecli validate`
- [ ] No placeholder text remaining

### Verification Loop

1. Generate document
2. Run `view issues` + `view outline` + `view text` + `validate`
3. List issues found (if none, look again more critically)
4. Fix issues
5. Re-verify -- one fix often creates another problem
6. Repeat until a full pass reveals no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

**QA display notes:**
- `view text` shows "1." for ALL numbered list items regardless of actual rendered number. This is a display limitation -- not a defect.
- `view issues` flags "body paragraph missing first-line indent" on cover page paragraphs, centered headings, list items, callout boxes, etc. These warnings are expected. First-line indent is only required in APA/academic body text.

---

## 11. Legacy Python CLI (Fallback)

Use these ONLY when officecli does not cover the requirement.

| Script | Role | Status |
|--------|------|--------|
| `python3 scripts/accept_changes.py FILE` | Accept tracked changes | Fallback |
| `python3 scripts/ooxml/merge_runs.py FILE` | Merge adjacent identical runs | Fallback |
| `python3 scripts/ooxml/redline_diff.py FILE` | Tracked-change validation | Fallback |
| `python3 scripts/docx_cli.py repair FILE --json` | Structural repair dry-run | Fallback |
| `soffice --headless --convert-to pdf FILE` | PDF conversion / visual QA | Fallback |

---

## 12. Anti-Patterns (MUST AVOID)

- **Placeholder data**: NEVER leave "Acme Corp", "Alice Chen", "Lorem ipsum" in output. If the user has not provided data, **ask**.
- **Footer PAGE fields**: When setting page numbers via `raw-set`, the XML structure must be exact. See the Headers & Footers section for the correct `fldChar`/`instrText`/`fldChar` sequence.
- **Empty paragraphs for spacing**: Use `spacing-after` properties.
- **Manual bullet characters** (-, *): Use `listStyle=bullet` or `listStyle=number`.
- **Manual font XML injection**: Use `--prop font=...` when it suffices.
- **Chinese comments in output**: Some subskill reference files contain Chinese-language code comments (operational notes). NEVER copy these into user-facing document output. Treat them as internal annotations only.

---

## 13. Dependencies

| Tool | Purpose | Status |
|------|---------|--------|
| `officecli` (PATH) | Primary DOCX CLI -- global install includes CJK fork | Required |
| `dotnet` | Runtime/build for officecli | Required for fork builds |
| `python3` | Fallback scripts | Optional fallback |
| `soffice` | PDF conversion / `.doc` migration / macro workflows | Optional fallback |
| `pdftoppm` | Image-based QA after PDF render | Optional fallback |

### Fork build (development only)

```bash
dotnet publish -c Release -o build-local
```
