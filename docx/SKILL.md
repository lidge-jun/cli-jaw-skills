---
name: docx
description: "Word DOCX create, read, edit, review. Triggers: Word doc, .docx, reports, memos, letters, templates."
---

# DOCX Skill

Use this skill for any .docx task: create, read, edit, or manipulate Word documents.
Triggers: "Word doc", ".docx", reports, memos, letters, templates.
Also covers visual review (render DOCX → PDF → PNG via soffice + pdftoppm), tracked changes, comments, find-and-replace, and image insertion.
Do NOT use for PDFs, spreadsheets, or Google Docs.

---

## Quick Reference

| Task        | Tool                                        |
| ----------- | ------------------------------------------- |
| **Create**  | `docx` npm package (docx-js) — JavaScript   |
| **Read**    | `pandoc` or `python -m markitdown`          |
| **Edit**    | Unpack → XML Edit → Pack (OOXML workflow)   |
| **Review**  | soffice → PDF → pdftoppm → image inspection |
| **Convert** | `.doc` → `.docx` via soffice                |

### Unified CLI (`docx_cli.py`)

All operations are available through a single entrypoint:

```bash
# Unpack / Pack
python scripts/docx_cli.py open input.docx work/
python scripts/docx_cli.py save work/ output.docx

# Validation & Repair
python scripts/docx_cli.py validate input.docx --json
python scripts/docx_cli.py repair input.docx              # dry-run (default)
python scripts/docx_cli.py repair input.docx --apply       # actually fix

# Text & Search
python scripts/docx_cli.py text input.docx
python scripts/docx_cli.py search input.docx "pattern"

# Tracked Changes & Comments
python scripts/docx_cli.py accept-changes input.docx output.docx
python scripts/docx_cli.py comment input.docx output.docx --text "Review" --anchor "target text"
python scripts/docx_cli.py comment input.docx output.docx --json comments.json

# XML Cleanup
python scripts/docx_cli.py merge-runs unpacked/
```

### Converting .doc to .docx

Legacy `.doc` files must be converted before editing:

```bash
python scripts/ooxml/soffice.py --headless --convert-to docx document.doc
```

### Converting to Images

```bash
python scripts/ooxml/soffice.py --headless --convert-to pdf document.docx
pdftoppm -jpeg -r 150 document.pdf page
```

---

## Creating Documents: docx-js (npm `docx`)

> [docx GitHub](https://github.com/dolanmiu/docx) — MIT License

```bash
npm install docx
```

### Basic Structure

```typescript
import { Document, Packer, Paragraph, TextRun } from "docx";
import * as fs from "fs";

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },  // US Letter (DXA)
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }  // 1 inch
      }
    },
    children: [
      new Paragraph({ children: [new TextRun("Hello World")] })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("document.docx", buffer);
});
```

### DXA Unit Conversion

- **1 inch = 1440 DXA** (twips)
- US Letter: 12240 × 15840 DXA (8.5 × 11 inch)
- A4: 11906 × 16838 DXA
- Content width = page width − left margin − right margin

```
1 inch    = 1440 DXA
0.5 inch  = 720 DXA
0.25 inch = 360 DXA
1 cm      = 567 DXA
1 pt      = 20 DXA
```

Helpers:
```typescript
import { convertInchesToTwip, convertMillimetersToTwip } from "docx";
convertInchesToTwip(1)         // 1440
convertMillimetersToTwip(25.4) // 1440
```

### Page Sizes

| Size                | width (DXA) | height (DXA) | inches       |
| ------------------- | ----------- | ------------ | ------------ |
| US Letter           | 12240       | 15840        | 8.5 × 11     |
| A4                  | 11906       | 16838        | 8.27 × 11.69 |
| US Legal            | 12240       | 20160        | 8.5 × 14     |
| US Letter Landscape | 15840       | 12240        | 11 × 8.5     |

### Margin Guide

| Purpose        | Top/Bottom | Left/Right   | DXA              |
| -------------- | ---------- | ------------ | ---------------- |
| Standard       | 1"         | 1"           | 1440 all         |
| Narrow         | 0.5"       | 0.5"         | 720 all          |
| Binding margin | 1"         | 1.25" (left) | left: 1800       |
| Wide margin    | 1"         | 1.5"         | left/right: 2160 |

### Styles

```typescript
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Arial", size: 24 } }  // 12pt (size = half-points)
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1",
        basedOn: "Normal", next: "Normal",
        quickFormat: true,
        run: { size: 56, bold: true, color: "000000" },  // 28pt
        paragraph: { spacing: { after: 120 } }
      }
    ]
  },
  sections: [{ children: [
    new Paragraph({ style: "Heading1", children: [new TextRun("Title")] })
  ]}]
});
```

> `size` uses **half-point** units — 12pt = `size: 24`

### Bullet & Numbered Lists

```typescript
import { LevelFormat, AlignmentType, convertInchesToTwip } from "docx";

const doc = new Document({
  numbering: {
    config: [{
      reference: "my-bullets",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "\u2022",
        alignment: AlignmentType.LEFT,
        style: {
          paragraph: {
            indent: { left: convertInchesToTwip(0.5), hanging: convertInchesToTwip(0.25) }
          }
        }
      }]
    }]
  },
  sections: [{
    children: [
      new Paragraph({
        numbering: { reference: "my-bullets", level: 0 },
        children: [new TextRun("First item")]
      }),
      new Paragraph({
        numbering: { reference: "my-bullets", level: 0 },
        children: [new TextRun("Second item")]
      })
    ]
  }]
});
```

> ❌ NEVER insert bullets manually as `"• Item"` — always use numbering config

### Tables

```typescript
import { Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType } from "docx";

const table = new Table({
  columnWidths: [3505, 5505],  // DXA
  rows: [
    new TableRow({
      children: [
        new TableCell({
          width: { size: 3505, type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, color: "auto", fill: "4472C4" },
          children: [new Paragraph("Header")]
        }),
        new TableCell({
          width: { size: 5505, type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, color: "auto", fill: "4472C4" },
          children: [new Paragraph("Value")]
        })
      ]
    })
  ]
});
```

> - Use `ShadingType.CLEAR` (SOLID causes black background)
> - Use `WidthType.DXA` (percentage breaks in Google Docs)

### Images

```typescript
import { ImageRun } from "docx";

new Paragraph({
  children: [new ImageRun({
    type: "png",  // required: png, jpg, jpeg, gif, bmp, svg
    data: fs.readFileSync("image.png"),
    transformation: { width: 200, height: 150 }  // pixels
  })]
});
```

### Page Breaks

```typescript
import { PageBreak } from "docx";

// CRITICAL: PageBreak must be inside a Paragraph
new Paragraph({ children: [new PageBreak()] })

// Or use pageBreakBefore on the next paragraph
new Paragraph({ pageBreakBefore: true, children: [new TextRun("New page")] })
```

### Table of Contents

```typescript
import { TableOfContents, HeadingLevel } from "docx";

// CRITICAL: Headings must use HeadingLevel ONLY — no custom styles
new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" })

// Heading paragraphs must include outlineLevel in style definition:
paragraphStyles: [{
  id: "Heading1", name: "Heading 1",
  paragraph: { outlineLevel: 0 },  // required for TOC
  // ...
}]
```

### Header & Footer

```typescript
import { Header, Footer, PageNumber } from "docx";

const doc = new Document({
  sections: [{
    properties: { titlePage: true },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [
            new TextRun("Title "),
            new TextRun({ children: ["Page ", PageNumber.CURRENT] })
          ]
        })]
      }),
      first: new Header({
        children: [new Paragraph({ children: [new TextRun("First Page Header")] })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({
            children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES]
          })]
        })]
      })
    },
    children: [new Paragraph("Content")]
  }]
});
```

---

## Reading Documents

```bash
# Pandoc (markdown conversion)
pandoc document.docx -t markdown -o output.md

# markitdown (text extraction)
python -m markitdown document.docx
```

---

## Editing: OOXML Direct Edit Workflow

For modifying existing .docx files: Unpack → XML edit → Pack (3-step workflow).

### OOXML File Structure

```
unpacked/
├── [Content_Types].xml
├── _rels/.rels
├── word/
│   ├── document.xml        ← Main body content
│   ├── styles.xml          ← Style definitions
│   ├── numbering.xml       ← Bullet/numbered lists
│   ├── comments.xml        ← Comments
│   ├── header1.xml         ← Header
│   ├── footer1.xml         ← Footer
│   ├── media/              ← Images
│   └── _rels/document.xml.rels  ← Resource relationships
└── docProps/
```

### Workflow

```bash
# 1. Unpack
python scripts/ooxml/unpack.py document.docx unpacked/

# 2. Check text content
python -m markitdown document.docx

# 3. Edit XML (word/document.xml etc. using Edit tool)
#    Use the Edit tool directly for string replacement. Do not write Python scripts.

# 4. Repack
python scripts/ooxml/pack.py unpacked/ output.docx --original document.docx

# 5. Validate
python scripts/ooxml/validate.py output.docx --json
# Returns: {"passed": bool, "errors": [...], "warnings": [...], "stats": {...}}

# 6. Auto-repair (if validation fails)
python scripts/ooxml/repair.py output.docx
# Returns: {"repaired": int, "details": [...]}
```

After creating new documents with docx-js, always validate:
```bash
python scripts/ooxml/validate.py doc.docx --json
```

### Adding Comments

```bash
# Add a comment (auto-creates comment XML files if needed)
python scripts/comment.py unpacked/ 0 "Comment text"

# Add a reply to comment 0
python scripts/comment.py unpacked/ 1 "Reply text" --parent 0
```

After running, add markers to document.xml:
```xml
<w:commentRangeStart w:id="0"/>
  ... commented content ...
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>
```

### Accepting Tracked Changes

```bash
python scripts/accept_changes.py input.docx output.docx
```

### Post-processing Tracked Changes

```bash
# Merge adjacent runs with identical formatting (reduces XML bloat)
python scripts/ooxml/merge_runs.py unpacked/
# Returns: {"merged_count": int, "files_modified": int, "proof_errors_removed": int}

# Simplify adjacent tracked changes from same author
python scripts/ooxml/simplify_tracked.py unpacked/
# Returns: {"merged_count": int, "authors": [...]}

# Verify tracked changes correctness against original
python scripts/ooxml/redline_diff.py unpacked/ original.docx --author Agent
# Returns: {"passed": bool, "diff": str | None, "stats": {...}}
```

### XML Editing Rules

- **Use defusedxml.minidom** — `xml.etree.ElementTree` corrupts namespaces
- **Smart quotes** → XML entities: `&#x201C;` (`"`), `&#x201D;` (`"`), `&#x2018;` (`'`), `&#x2019;` (`'`)
- **Preserve whitespace**: `xml:space="preserve"` on `<w:t>` (for leading/trailing spaces)
- **RSID**: 8-digit hex (e.g., `00AB1234`)
- **Element order in `<w:pPr>`**: `<w:pStyle>`, `<w:numPr>`, `<w:spacing>`, `<w:ind>`, `<w:jc>`, `<w:rPr>` last
- **`<w:delInstrText>`**: Inside `<w:del>`, use `<w:delInstrText>` instead of `<w:instrText>`
- **Replace entire `<w:r>` elements**: When adding tracked changes, replace the whole `<w:r>...</w:r>` block with `<w:del>...<w:ins>...` as siblings. Don't inject tracked change tags inside a run
- **Preserve `<w:rPr>` formatting**: Copy the original run's `<w:rPr>` block into your tracked change runs to maintain bold, font size, etc.

### Tracked Changes

#### Insertion

```xml
<w:ins w:id="1" w:author="Agent" w:date="2026-03-08T00:00:00Z">
  <w:r><w:t>inserted text</w:t></w:r>
</w:ins>
```

#### Deletion

```xml
<w:del w:id="2" w:author="Agent" w:date="2026-03-08T00:00:00Z">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
```

> Inside `<w:del>`, always use `<w:delText>` instead of `<w:t>`, and `<w:delInstrText>` instead of `<w:instrText>`.

#### Minimal Edits — only mark what changes

```xml
<!-- Change "30 days" to "60 days" -->
<w:r><w:t>The term is </w:t></w:r>
<w:del w:id="1" w:author="Agent" w:date="2026-03-08T00:00:00Z">
  <w:r><w:delText>30</w:delText></w:r>
</w:del>
<w:ins w:id="2" w:author="Agent" w:date="2026-03-08T00:00:00Z">
  <w:r><w:t>60</w:t></w:r>
</w:ins>
<w:r><w:t> days.</w:t></w:r>
```

#### Paragraph Deletion (prevent orphan empty paragraphs)

```xml
<w:p>
  <w:pPr><w:rPr>
    <w:del w:id="3" w:author="Agent" w:date="2026-03-08T00:00:00Z"/>
  </w:rPr></w:pPr>
  <w:del w:id="4" w:author="Agent" w:date="2026-03-08T00:00:00Z">
    <w:r><w:delText>paragraph content</w:delText></w:r>
  </w:del>
</w:p>
```

> Without `<w:del/>` inside `<w:pPr><w:rPr>`, an empty paragraph remains after accepting

#### Rejecting Another Author's Insertion

Nest deletion inside their insertion:
```xml
<w:ins w:author="Jane" w:id="5">
  <w:del w:author="Agent" w:id="10">
    <w:r><w:delText>their inserted text</w:delText></w:r>
  </w:del>
</w:ins>
```

#### Restoring Another Author's Deletion

Add insertion after — don't modify their deletion:
```xml
<w:del w:author="Jane" w:id="5">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
<w:ins w:author="Agent" w:id="10">
  <w:r><w:t>deleted text</w:t></w:r>
</w:ins>
```

### Images via XML

1. Add image file to `word/media/`
2. Add relationship to `word/_rels/document.xml.rels`:
```xml
<Relationship Id="rId5" Type=".../image" Target="media/image1.png"/>
```
3. Add content type to `[Content_Types].xml`:
```xml
<Default Extension="png" ContentType="image/png"/>
```
4. Reference in document.xml (EMU units: 914400 = 1 inch):
```xml
<w:drawing>
  <wp:inline>
    <wp:extent cx="914400" cy="914400"/>  <!-- 1 inch × 1 inch -->
    <a:graphic>
      <a:graphicData uri=".../picture">
        <pic:pic>
          <pic:blipFill><a:blip r:embed="rId5"/></pic:blipFill>
        </pic:pic>
      </a:graphicData>
    </a:graphic>
  </wp:inline>
</w:drawing>
```

### Relationships Editing Guide

- Manage `rId` mappings in `_rels/document.xml.rels`
- When replacing images: update both `media/` file AND `_rels` simultaneously
- For new rId: use existing max number + 1

---

## Google Docs Compatibility

| Feature           | Word | Google Docs          | Notes                 |
| ----------------- | ---- | -------------------- | --------------------- |
| Table width %     | ✅    | ❌ breaks             | Use DXA               |
| Custom fonts      | ✅    | ⚠️ Google Fonts only  | Use standard fonts    |
| Tracked Changes   | ✅    | ✅                    | Compatible            |
| Headers/Footers   | ✅    | ✅                    | Compatible            |
| Complex numbering | ✅    | ⚠️ partial            | Use simple bullets    |
| Image wrapping    | ✅    | ⚠️ limited            | Use inline            |
| Korean fonts      | ✅    | ⚠️ no Noto/Pretendard | Use Google Fonts only |

---

## Anti-Patterns

| ❌ Don't                         | ✅ Do Instead                                     | Why                                |
| ------------------------------- | ------------------------------------------------ | ---------------------------------- |
| Use `\n` for line breaks        | Separate `Paragraph` objects                     | `\n` is ignored or breaks          |
| Manual bullets `"• Item"`       | `numbering.config` + `LevelFormat.BULLET`        | Word bullet feature won't work     |
| `ShadingType.SOLID`             | `ShadingType.CLEAR` + `fill` color               | SOLID causes black background      |
| `WidthType.PERCENTAGE`          | `WidthType.DXA`                                  | Breaks in Google Docs              |
| Landscape: long side as `width` | Short side as `width` + `orientation: LANDSCAPE` | docx-js swaps internally           |
| Omit `type` on `ImageRun`       | Always specify `type: "png"` etc.                | Omission causes error              |
| All content in one paragraph    | Separate `Paragraph` per item                    | Structured documents required      |
| `font.size: 12` (as points)     | `font.size: 24` (half-points)                    | docx-js uses half-point units      |
| Long Korean in single `TextRun` | Split into separate `Paragraph`s                 | Korean wraps poorly without spaces |

---

## CJK / Korean Text Handling

When creating documents with Korean, Chinese, or Japanese text, apply these rules.

### Word Wrapping

Korean uses syllable-level wrapping, not word-level. Set OOXML attributes on paragraphs:

```xml
<w:pPr>
  <w:wordWrap w:val="0"/>        <!-- Allow character-level wrapping -->
  <w:overflowPunct w:val="1"/>   <!-- Kinsoku: prevent punctuation at line start -->
  <w:autoSpaceDE w:val="1"/>     <!-- Auto 1/4em gap between Latin and Korean -->
  <w:autoSpaceDN w:val="1"/>     <!-- Auto gap between Korean and digits -->
</w:pPr>
```

| Attribute                 | Default | Effect                                                       |
| ------------------------- | ------- | ------------------------------------------------------------ |
| `w:wordWrap val="0"`      | 1       | Allow syllable-level wrapping (essential for narrow columns) |
| `w:overflowPunct val="1"` | 1       | Kinsoku shori — keeps closing punctuation off line starts    |
| `w:autoSpaceDE val="1"`   | 1       | Automatic spacing between Korean and Latin text              |
| `w:autoSpaceDN val="1"`   | 1       | Automatic spacing between Korean and digits                  |

> docx-js does not expose these attributes directly. Generate the document, then use the unpack → XML edit → pack workflow to inject them.

### East Asian Fonts

```typescript
// docx-js: specify EA font in TextRun
new TextRun({
  text: "한글 문서",
  font: { eastAsia: "Malgun Gothic" }  // EA font
});

// Document-level default
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Noto Sans KR", size: 24 }  // 12pt
      }
    }
  },
  // ...
});
```

Recommended Korean fonts:

| Font          | License   | Cross-platform | Best for          |
| ------------- | --------- | -------------- | ----------------- |
| Noto Sans KR  | OFL       | Win/Mac/Linux  | Safest choice     |
| Pretendard    | OFL       | Win/Mac/Linux  | Modern UI         |
| Malgun Gothic | MS bundle | Windows only   | Windows-only docs |
| NanumGothic   | OFL       | Win/Mac/Linux  | General Korean    |
| Noto Serif KR | OFL       | Win/Mac/Linux  | Print/academic    |

### DXA Width for CJK

CJK characters occupy roughly twice the width of Latin characters. Use `scripts/ooxml/cjk_utils.py` for table column width estimation:

```python
from scripts.ooxml.cjk_utils import get_display_width, pixel_to_emu, emu_to_pixel

# Full-width aware width
get_display_width("Hello")     # 5
get_display_width("한글 테스트")  # 10

# EMU conversion for images
pixel_to_emu(400)              # 3810000
emu_to_pixel(3810000)          # 400
```

For table column widths with CJK text:

```typescript
// DXA column width estimation with CJK awareness
const columnWidths = headers.map(h => {
  const displayWidth = [...h].reduce((sum, ch) => {
    const code = ch.codePointAt(0) ?? 0;
    return sum + ((code >= 0xAC00 && code <= 0xD7AF) ||
                  (code >= 0x3000 && code <= 0x9FFF) ? 2 : 1);
  }, 0);
  return Math.max(displayWidth * 180, 1440);  // 180 DXA per char unit, min 1 inch
});
```

### Korean Language Injection (Post-processing)

After generating a docx with docx-js, inject `lang="ko-KR"` for proper kinsoku and spell-check:

```bash
python scripts/ooxml/unpack.py output.docx unpacked/
python -c "from scripts.ooxml.cjk_utils import inject_korean_lang; inject_korean_lang('unpacked/')"
python scripts/ooxml/pack.py unpacked/ output_ko.docx --original output.docx
```

---

## Template Preservation

When modifying existing documents, **never alter styles, formatting, or structure beyond what was requested.**

```bash
# OOXML editing preserves all styles
python scripts/ooxml/unpack.py template.docx unpacked/
# Edit only the text content in word/document.xml
# <w:t>{{TITLE}}</w:t> → <w:t>Actual Title</w:t>
# NEVER modify <w:rPr> (run properties) — preserves fonts, colors, sizes
python scripts/ooxml/pack.py unpacked/ filled.docx --original template.docx
```

Rules:
- Never delete existing conditional formatting or data validations
- Never overwrite cell/paragraph styles unless explicitly requested
- Never remove named ranges or bookmarks
- When extending a data range, verify existing chart references first

---

## Accessibility (WCAG 2.1 AA)

| Requirement       | Standard          | Implementation                                  |
| ----------------- | ----------------- | ----------------------------------------------- |
| Color contrast    | >= 4.5:1          | Use `cjk_utils.check_contrast()` to verify      |
| Image alt text    | Required on all   | `ImageRun({ altText: { title, description } })` |
| Minimum font size | >= 10pt           | No captions below 10pt                          |
| Language metadata | `lang="ko-KR"`    | Enables screen reader pronunciation             |
| Heading hierarchy | Sequential levels | H1 → H2 → H3, no skipping                       |
| Reading order     | Logical flow      | Document structure matches visual order         |

> **Reading order matters**: `children[]` array order in each Section = screen reader reading order. Always arrange: Heading → Body → Image → Caption.

```typescript
// Alt text on images
new ImageRun({
  type: "png", data: imageData,
  transformation: { width: 400, height: 300 },
  altText: {
    title: "Sales Chart",
    description: "Bar chart showing Q1-Q4 2025 revenue growth"
  }
});
```

```python
# Contrast check
from scripts.ooxml.cjk_utils import check_contrast
ratio = check_contrast("FFFFFF", "4472C4")
assert ratio >= 4.5, f"Contrast insufficient: {ratio:.1f}:1 (need >= 4.5:1)"
```

---

## QA Verification

```bash
# Check text content
python -m markitdown output.docx

# Check for placeholder remnants
python -m markitdown output.docx | grep -iE "xxxx|lorem|ipsum|placeholder|TODO"

# Visual verification
soffice --headless --convert-to pdf output.docx
pdftoppm -jpeg -r 150 output.pdf page
```

Checklist:
- [ ] Text content accurate
- [ ] Style consistency (heading vs body distinction)
- [ ] Page margins appropriate
- [ ] Images inserted and positioned
- [ ] Header/Footer displayed
- [ ] Page numbers correct
- [ ] Tracked changes markup valid (when editing)
- [ ] No placeholder remnants
- [ ] Images have alt text
- [ ] Font size >= 10pt
- [ ] Color contrast >= 4.5:1
- [ ] Korean text not truncated / wrapping correctly (if CJK content)
- [ ] Korean font rendering as intended, no fallback glyphs
- [ ] Kinsoku: no closing punctuation (。，) at line start
- [ ] Korean-Latin mixed spacing natural (autoSpaceDE applied)

---

## Dependencies

```bash
npm install docx               # DOCX creation
pip install markitdown          # Text extraction
pip install defusedxml          # Safe XML parsing (validate.py, repair.py)
# pandoc                        # Markdown conversion
# LibreOffice (soffice)         # PDF conversion, accept tracked changes
# Poppler (pdftoppm)            # PDF → image
# scripts/ooxml/cjk_utils.py   # Korean: width calc, lang injection, contrast check
# scripts/ooxml/repair.py      # Auto-repair: whitespace, durableId, orphan rels
# scripts/ooxml/merge_runs.py  # Merge adjacent <w:r> with same formatting
# scripts/ooxml/simplify_tracked.py  # Merge adjacent tracked changes (same author)
# scripts/ooxml/redline_diff.py      # Validate tracked changes via difflib
```
