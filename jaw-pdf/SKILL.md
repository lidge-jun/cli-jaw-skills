---
name: "jaw-pdf"
description: "PDF 읽기·생성·편집·리뷰. reportlab/pdfplumber/pypdf + Korean CJK font handling, TOC generation, purpose-driven workflow, visual verification, and ELI5 patterns."
---

# PDF Skill

## Purpose-Driven Workflow (do this FIRST)

Before generating any PDF, define:

1. **Purpose** — what is this document for? (report, proposal, manual, presentation handout, certificate, invoice, ELI5 explainer)
2. **Audience** — who reads it? (executive, engineer, student, general public, 한국어 사용자)
3. **Structure** — what sections does it need? (TOC, executive summary, chapters, appendix, references)
4. **Language** — Korean, English, or mixed? (determines font registration)

Without this, do not start PDF generation. Ask the user if unclear.

### Document Templates

| Template | Sections | Notes |
|----------|----------|-------|
| Report | Cover, TOC, Executive Summary, Body chapters, Conclusion, References | Formal, numbered headings |
| Proposal | Cover, Problem, Solution, Timeline, Budget, Team | Persuasive, visual hierarchy |
| Manual | Cover, TOC, Chapters with step-by-step, Troubleshooting, Index | Instructional, many subheadings |
| ELI5 Explainer | Title, Key Concept (large text + diagram), Step-by-step, Summary | Simple, visual-heavy, large fonts |
| Presentation Handout | Slide-per-page layout, speaker notes section | Matches slide structure |

## Korean / CJK Font Handling

### Font Detection

Detect available Korean fonts on the system before PDF generation:

```python
import os
from pathlib import Path

def find_korean_fonts():
    """Detect available Korean TrueType fonts on the system."""
    candidates = [
        # macOS
        ("NotoSansKR", [
            Path.home() / "Library/Fonts/NotoSansKR-Regular.ttf",
            Path("/Library/Fonts/NotoSansKR-Regular.ttf"),
            Path("/System/Library/Fonts/NotoSansKR-Regular.ttf"),
        ]),
        ("AppleGothic", [
            Path("/System/Library/Fonts/Supplemental/AppleGothic.ttf"),
        ]),
        ("NanumGothic", [
            Path.home() / "Library/Fonts/NanumGothic.ttf",
            Path("/Library/Fonts/NanumGothic.ttf"),
            Path("/opt/homebrew/share/fonts/NanumGothic.ttf"),
        ]),
        # Linux
        ("NotoSansCJKkr", [
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/noto-cjk/NotoSansCJKkr-Regular.otf"),
        ]),
        # Windows
        ("MalgunGothic", [
            Path("C:/Windows/Fonts/malgun.ttf"),
        ]),
    ]
    found = []
    for name, paths in candidates:
        for p in paths:
            if p.exists():
                found.append((name, str(p)))
                break
    return found
```

### Font Registration with reportlab

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def register_korean_font():
    """Register the first available Korean font. Returns the font name."""
    fonts = find_korean_fonts()
    if not fonts:
        raise RuntimeError(
            "No Korean font found. Install one:\n"
            "  macOS: brew install font-noto-sans-cjk-kr\n"
            "  Linux: sudo apt install fonts-noto-cjk\n"
            "  Windows: Malgun Gothic is pre-installed"
        )
    name, path = fonts[0]
    pdfmetrics.registerFont(TTFont(name, path))
    return name

def korean_styles(font_name):
    """Create paragraph styles with Korean font support."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='KoreanBody',
        fontName=font_name,
        fontSize=11,
        leading=16,
        wordWrap='CJK',
    ))
    styles.add(ParagraphStyle(
        name='KoreanHeading1',
        fontName=font_name,
        fontSize=22,
        leading=28,
        spaceAfter=12,
        wordWrap='CJK',
    ))
    styles.add(ParagraphStyle(
        name='KoreanHeading2',
        fontName=font_name,
        fontSize=16,
        leading=22,
        spaceAfter=8,
        wordWrap='CJK',
    ))
    return styles
```

### Critical: wordWrap='CJK'

reportlab's default word-wrap algorithm only breaks at spaces. Korean text has no spaces
between words in many contexts, so without `wordWrap='CJK'` the text overflows the page
margin or gets clipped. **Always set `wordWrap='CJK'` on every style used for Korean text.**

## Table of Contents (TOC)

### Clickable TOC with reportlab

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.units import cm

class TOCDocTemplate(SimpleDocTemplate):
    """Document template that collects TOC entries from headings."""

    def afterFlowable(self, flowable):
        """Register TOC entries when a heading flowable is rendered."""
        if not isinstance(flowable, Paragraph):
            return
        import hashlib
        style_name = flowable.style.name
        text = flowable.getPlainText()
        if style_name == 'KoreanHeading1':
            # Use text-based stable key — counters break multiBuild
            key = 'toc-' + hashlib.md5(text.encode()).hexdigest()[:8]
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=0)
            self.notify('TOCEntry', (0, text, self.page, key))
        elif style_name == 'KoreanHeading2':
            key = 'toc-' + hashlib.md5(text.encode()).hexdigest()[:8]
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=1)
            self.notify('TOCEntry', (1, text, self.page, key))

def build_pdf_with_toc(output_path, title, sections, font_name):
    """
    Build a PDF with Korean TOC.
    sections: list of (level, heading_text, body_paragraphs)
    """
    doc = TOCDocTemplate(output_path, topMargin=2*cm, bottomMargin=2*cm)
    styles = korean_styles(font_name)
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name='TOCLevel0', fontName=font_name, fontSize=14,
                       leftIndent=0, leading=20),
        ParagraphStyle(name='TOCLevel1', fontName=font_name, fontSize=12,
                       leftIndent=1*cm, leading=16),
    ]

    story = []
    story.append(Paragraph(title, styles['KoreanHeading1']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph('목차', styles['KoreanHeading1']))
    story.append(toc)
    story.append(PageBreak())
    for level, heading, paragraphs in sections:
        style = 'KoreanHeading1' if level == 0 else 'KoreanHeading2'
        story.append(Paragraph(heading, styles[style]))
        for para in paragraphs:
            story.append(Paragraph(para, styles['KoreanBody']))
            story.append(Spacer(1, 0.3*cm))

    doc.multiBuild(story)
```

### Pitfalls

- **Import path**: `TableOfContents` lives in `reportlab.platypus.tableofcontents`,
  NOT in `reportlab.platypus` directly.
- **Stable bookmark keys**: use text-based keys (e.g. `hashlib.md5(text)`), not counters.
  Counters increment across `multiBuild` passes and cause infinite "Index entries not resolved" errors.
- **TOC title style**: the "목차" heading above the TOC object must use a NON-TRACKED style.
  If it uses the same style as content headings, it becomes a TOC entry pointing to itself,
  causing infinite recursion in `multiBuild`.

### Key points

- Use `multiBuild()` instead of `build()` — TOC needs two passes to resolve page numbers.
- `bookmarkPage()` + `addOutlineEntry()` create the PDF viewer sidebar outline.
- `notify('TOCEntry', ...)` populates the in-document clickable TOC.

## ELI5 Pattern (Explain Like I'm 5)

For simple explanatory PDFs aimed at non-technical audiences:

### Design Principles

- **Large fonts**: body 14pt+, headings 24pt+
- **Visual hierarchy**: one concept per page, clear section breaks
- **Diagrams over text**: embed SVG/PNG diagrams for every key concept
- **Simple language**: short sentences, no jargon, analogies
- **Color coding**: consistent colors for recurring concepts
- **Progressive disclosure**: build complexity gradually across pages

### Structure

1. **Title page**: big title, one-line subtitle, optional illustration
2. **Key Concept page**: one diagram + 2-3 sentences explaining the core idea
3. **Step-by-step pages**: numbered steps with illustrations
4. **Summary page**: bullet recap of key points

### Implementation

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor

ELI5_STYLES = {
    'title_size': 32,
    'heading_size': 24,
    'body_size': 16,
    'leading_ratio': 1.5,
    'margin': 3 * cm,
    'accent_color': HexColor('#2563EB'),
    'bg_light': HexColor('#F0F7FF'),
}
```

## Visual Verification Contract

**Every PDF generation MUST include visual verification before delivery.**

### Verification Loop

```
Generate PDF -> Render to PNG -> View image -> Check -> Fix -> Re-render -> Re-check
```

### Steps

1. **Render** each page to PNG:
   ```bash
   pdftoppm -png -r 200 output.pdf /tmp/pdf_verify
   ```

2. **View** each page image (use view_image tool or equivalent).

3. **Check** against this checklist:
   - Korean text renders correctly (no boxes, no `?`, no blank glyphs)
   - TOC page numbers are correct (not all showing "0" or blank)
   - TOC links are clickable (open in PDF viewer to verify)
   - Margins are consistent (no text touching edges)
   - Headings have clear hierarchy (size, weight, spacing)
   - Images/diagrams are sharp and aligned
   - Page numbers appear in header/footer
   - No orphaned headings (heading at bottom of page with body on next)
   - Line spacing is readable (not cramped)
   - Mixed Korean/English text aligns properly

4. **Fix** any issues found and repeat from step 1.

5. **Do not deliver** until all checklist items pass on the latest render.

### Korean-Specific Verification

| Symptom | Cause | Fix |
|---------|-------|-----|
| Square boxes | Font not registered | Register TTFont with Korean font |
| Text overflows margin | Missing wordWrap CJK | Add wordWrap='CJK' to style |
| Garbled characters | Wrong encoding | Ensure UTF-8 source, TTFont (not Type1) |
| Cramped spacing | Leading too small | Set leading to 1.4-1.6x font size |
| Mixed-language misalignment | Different font metrics | Use same font for both, or adjust baseline |

## Standard Workflow

1. **Define purpose/audience/structure** (see Purpose-Driven Workflow above).
2. **Detect and register Korean fonts** if the document contains Korean text.
3. **Build the document** with TOC if it has 3+ sections.
4. **Render to PNG** and visually verify every page.
5. Use reportlab to generate new PDFs.
6. Use pdfplumber or pypdf for text extraction; these are unreliable for layout fidelity.
7. After each meaningful update, re-render and verify alignment, spacing, and legibility.

## Temp and output conventions

- Use `tmp/pdfs/` for intermediate files; delete when done.
- Write final artifacts under `output/pdf/` when working in this repo.
- Keep filenames stable and descriptive.

## Dependencies (install if missing)

Prefer uv for dependency management.

Python packages:
```
uv pip install reportlab pdfplumber pypdf
```
If uv is unavailable:
```
python3 -m pip install reportlab pdfplumber pypdf
```
System tools (for rendering):
```
# macOS (Homebrew)
brew install poppler

# Ubuntu/Debian
sudo apt-get install -y poppler-utils
```

## Rendering command

```
pdftoppm -png -r 200 $INPUT_PDF $OUTPUT_PREFIX
```

## Quality expectations

- Consistent typography, spacing, margins, and section hierarchy.
- No rendering defects: clipped text, overlapping elements, broken tables, black squares, or unreadable glyphs.
- Charts, tables, and images: sharp, aligned, and clearly labeled.
- Use ASCII hyphens only. Unicode dashes cause rendering issues in some viewers.
- Citations and references: human-readable, no tool tokens or placeholders.
- Korean text: properly wrapped, correct glyphs, readable spacing.

## Final checks

- Verify the latest PNG render shows zero visual defects before delivery.
- Confirm headers/footers, page numbering, and section transitions.
- Clean up or organize intermediate files after approval.
- For Korean documents: verify glyph rendering on at least 3 representative pages.

## Cross-references

- **Diagrams in PDF**: see jaw-diagram skill for SVG/Mermaid/Chart.js generation,
  then embed as PNG via reportlab.platypus.Image.
- **DOCX to PDF**: `soffice --headless --convert-to pdf input.docx` (requires LibreOffice).
- **Visual verification**: see jaw-pdf-vision for OCR-based PDF reading.
