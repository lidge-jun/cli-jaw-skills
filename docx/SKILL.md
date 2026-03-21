---
name: docx
description: "Word DOCX create, read, edit, review. Triggers: Word doc, .docx, reports, memos, letters, templates."
---

# DOCX Skill

Handle any .docx task: create, read, edit, or manipulate Word documents.
Covers visual review (render DOCX → PDF → PNG), tracked changes, comments, find-and-replace, and image insertion.

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

```bash
# Unpack / Pack
python scripts/docx_cli.py open input.docx work/
python scripts/docx_cli.py save work/ output.docx

# Validation & Repair
python scripts/docx_cli.py validate input.docx --json
python scripts/docx_cli.py repair input.docx --apply

# Text & Search
python scripts/docx_cli.py text input.docx
python scripts/docx_cli.py search input.docx "pattern"

# Tracked Changes & Comments
python scripts/docx_cli.py accept-changes input.docx output.docx
python scripts/docx_cli.py comment input.docx output.docx --text "Review" --anchor "target text"

# XML Cleanup
python scripts/docx_cli.py merge-runs unpacked/
```

### Conversions

```bash
# .doc → .docx
python scripts/ooxml/soffice.py --headless --convert-to docx document.doc

# .docx → images
python scripts/ooxml/soffice.py --headless --convert-to pdf document.docx
pdftoppm -jpeg -r 150 document.pdf page
```

---

## Creating Documents (docx-js)

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
        size: { width: 12240, height: 15840 },       // US Letter (DXA)
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
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

### DXA Units

| Value | DXA |
|-------|-----|
| 1 inch | 1440 |
| 0.5 inch | 720 |
| 1 cm | 567 |
| 1 pt | 20 |

Helpers: `convertInchesToTwip(1)` → 1440, `convertMillimetersToTwip(25.4)` → 1440

### Page Sizes

| Size        | width (DXA) | height (DXA) |
| ----------- | ----------- | ------------ |
| US Letter   | 12240       | 15840        |
| A4          | 11906       | 16838        |
| US Legal    | 12240       | 20160        |

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
// PageBreak inside a Paragraph
new Paragraph({ children: [new PageBreak()] })

// Or pageBreakBefore on the next paragraph
new Paragraph({ pageBreakBefore: true, children: [new TextRun("New page")] })
```

> For styles, lists, tables, ToC, headers/footers → see `references/docx-js-api.md`

---

## Reading Documents

```bash
pandoc document.docx -t markdown -o output.md
python -m markitdown document.docx
```

---

## Editing: OOXML Workflow

Unpack → XML edit → Pack (3-step workflow) for modifying existing .docx files.

### OOXML File Structure

```
unpacked/
├── [Content_Types].xml
├── _rels/.rels
├── word/
│   ├── document.xml        ← Main body
│   ├── styles.xml          ← Style definitions
│   ├── numbering.xml       ← Lists
│   ├── comments.xml        ← Comments
│   ├── header1.xml / footer1.xml
│   ├── media/              ← Images
│   └── _rels/document.xml.rels
└── docProps/
```

### Workflow

```bash
# 1. Unpack
python scripts/ooxml/unpack.py document.docx unpacked/

# 2. Check text
python -m markitdown document.docx

# 3. Edit XML with Edit tool (use string replacement, not Python scripts)

# 4. Repack
python scripts/ooxml/pack.py unpacked/ output.docx --original document.docx

# 5. Validate
python scripts/ooxml/validate.py output.docx --json

# 6. Auto-repair (if needed)
python scripts/ooxml/repair.py output.docx
```

Always validate after creating documents with docx-js:
```bash
python scripts/ooxml/validate.py doc.docx --json
```

### XML Editing Rules

- Use **defusedxml.minidom** — `xml.etree.ElementTree` corrupts namespaces
- Smart quotes → XML entities: `&#x201C;` `&#x201D;` `&#x2018;` `&#x2019;`
- Preserve whitespace: `xml:space="preserve"` on `<w:t>` for leading/trailing spaces
- RSID: 8-digit hex (e.g., `00AB1234`)
- `<w:pPr>` element order: `<w:pStyle>`, `<w:numPr>`, `<w:spacing>`, `<w:ind>`, `<w:jc>`, `<w:rPr>` last
- Inside `<w:del>`, use `<w:delInstrText>` instead of `<w:instrText>`
- Replace entire `<w:r>` elements for tracked changes — inject `<w:del>...<w:ins>...` as siblings
- Copy original `<w:rPr>` formatting into tracked change runs

> For tracked changes XML patterns, comments, post-processing → see `references/tracked-changes.md`

---

## Google Docs Compatibility

| Feature           | Word | Google Docs | Fix                   |
| ----------------- | ---- | ----------- | --------------------- |
| Table width %     | ✅    | ❌           | Use DXA               |
| Custom fonts      | ✅    | ⚠️           | Use Google Fonts      |
| Complex numbering | ✅    | ⚠️           | Use simple bullets    |
| Image wrapping    | ✅    | ⚠️           | Use inline            |

---

## Anti-Patterns

| Avoid                            | Use instead                                      | Why                                |
| -------------------------------- | ------------------------------------------------ | ---------------------------------- |
| `\n` for line breaks             | Separate `Paragraph` objects                     | `\n` is ignored in OOXML           |
| Manual bullets `"• Item"`        | `numbering.config` + `LevelFormat.BULLET`        | Breaks Word bullet features        |
| `ShadingType.SOLID`              | `ShadingType.CLEAR` + `fill` color               | SOLID causes black background      |
| `WidthType.PERCENTAGE`           | `WidthType.DXA`                                  | Breaks in Google Docs              |
| Landscape: long side as `width`  | Short side + `orientation: LANDSCAPE`             | docx-js swaps internally           |
| Omit `type` on `ImageRun`        | Always specify `type: "png"` etc.                | Omission causes runtime error      |
| `font.size: 12` (as points)      | `font.size: 24` (half-points)                    | docx-js uses half-point units      |

---

## Template Preservation

When modifying existing documents, only alter what was requested:

```bash
python scripts/ooxml/unpack.py template.docx unpacked/
# Edit text in word/document.xml: <w:t>{{TITLE}}</w:t> → <w:t>Actual Title</w:t>
# Preserve <w:rPr> (run properties) — keeps fonts, colors, sizes
python scripts/ooxml/pack.py unpacked/ filled.docx --original template.docx
```

Rules:
- Preserve existing conditional formatting and data validations
- Preserve cell/paragraph styles unless explicitly requested to change
- Preserve named ranges and bookmarks
- When extending data ranges, verify existing chart references first

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
- Text content accurate
- Style consistency (heading vs body distinction)
- Page margins appropriate
- Images inserted and positioned
- Header/Footer and page numbers correct
- Tracked changes markup valid (when editing)
- No placeholder remnants
- Korean text wrapping correctly (if CJK content)

> For CJK/Korean text handling, fonts, accessibility → see `references/cjk-handling.md`

---

## Dependencies

```bash
npm install docx               # DOCX creation
pip install markitdown          # Text extraction
pip install defusedxml          # Safe XML parsing
# pandoc                        # Markdown conversion
# LibreOffice (soffice)         # PDF conversion
# Poppler (pdftoppm)            # PDF → image
# scripts/ooxml/cjk_utils.py   # Korean: width calc, lang injection, contrast check
# scripts/ooxml/repair.py      # Auto-repair
# scripts/ooxml/merge_runs.py  # Merge adjacent <w:r> with same formatting
```

## References

- `references/docx-js-api.md` — styles, lists, tables, ToC, headers/footers, images via XML
- `references/tracked-changes.md` — tracked changes XML, comments, post-processing
- `references/cjk-handling.md` — CJK/Korean text, fonts, width calculation, accessibility
