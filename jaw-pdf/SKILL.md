---
name: "jaw-pdf"
description: "PDF 읽기·생성·편집·리뷰. reportlab/pdfplumber/pypdf + Korean CJK font handling, TOC generation, purpose-driven workflow, visual verification, and ELI5 patterns."
---

# PDF Skill

## Content Balance Principle (TEXT-FIRST)

Text is the main content. Visuals are opt-in supplements.

- Every page must have substantive text (3+ paragraphs of real explanation)
- Diagrams, charts, and colored boxes are SUPPLEMENTS that help explain complex structures
- Use visuals only when text alone cannot convey the relationship (architecture diagrams,
  multi-dimensional comparisons, data trends, process flows)
- A page with only a diagram and a one-liner caption is incomplete
- Ratio guideline: 80% text-driven pages, 20% pages with diagrams as primary content
- Never let visual elements replace the explanation — they illustrate it

When to include a diagram:
- Architecture or system structure (components + connections)
- Quantitative comparison (bar chart, table with numbers)
- Multi-step process that is hard to follow linearly
- Before/after or side-by-side comparison

When NOT to include a diagram:
- The concept can be explained in 2-3 sentences
- The visual is decorative rather than informative
- The page already has enough text to be understood


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

## Alternative Tools

| Tool | Best For | Korean/CJK | TOC | Quality |
|------|----------|------------|-----|---------|
| reportlab | Python programmatic control | TTFont + wordWrap CJK | multiBuild + bookmarks | Good |
| WeasyPrint | HTML/CSS reports | Pango/Fontconfig | HTML headings -> bookmarks | Excellent |
| fpdf2 | Simple Python API | HarfBuzz + fallback fonts | Manual two-pass | Good |
| Typst | Highest-quality documents | Configurable fonts | Native outlines | Excellent |
| Pandoc + engine | Source portability | Depends on backend | --toc flag | Variable |

Choose reportlab when you need programmatic control from Python. Consider WeasyPrint
when starting from HTML/CSS. Use Typst for publication-quality output.

## Real-World Workflow Patterns

Based on analysis of actual cli-jaw document production (사업계획서, 활동보고서):

### Iterative Feedback Loop

1. Draft -> Team review (Slack/email) -> Feedback collection -> Revision -> Re-review
2. Each revision creates a new DOCX with version suffix (초안 -> 수정초안 -> 피드백반영 -> 완성 -> 제출)
3. Keep all versions; never overwrite the previous draft

### Structured Section Pattern (Q1-Q4, McKinsey-style)

For consulting-style or government-submission documents:

1. Define the narrative thread FIRST: what question does each section answer?
2. Write section headings as questions, not topics
3. One key message per section; supporting evidence below
4. Ghost-deck: validate the argument flow with headings only before writing body text

Example (사업계획서):
- Q1 문제인식: "고객이 지금 어떤 손실을 겪고 있으며 기존 해결책은 왜 부족한가?"
- Q2 실현가능성: "우리가 실제로 만들 수 있다는 증거는?"
- Q3 성장전략: "고객이 왜 비용을 지불하며, 어떻게 고객 수와 매출을 늘릴 것인가?"
- Q4 향후 발전: "현재 제품을 어떤 구조로 진화시킬 것인가?"

### Korean Government Document Conventions

For 공문서 or government-submission documents:

- A4, margins: top/bottom 15mm, left/right 20mm
- Body: serif font (Pretendard GOV or 휴먼명조), 15-17pt, line spacing 150-160%
- Headings: sans-serif (고딕), Bold 700
- Left-aligned body text (no indent from title)
- Source: KRDS (krds.go.kr), 국립국어원 공문서 지침

## Embedding Images and Diagrams

### Canvas Drawing (inline diagrams)

Use reportlab Canvas for custom diagrams directly in PDF — no external images needed:

```python
from reportlab.platypus.flowables import Flowable

class CustomDiagram(Flowable):
    """Base class for inline PDF diagrams."""
    def __init__(self, width, height):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        # Rounded rectangles for boxes
        c.setFillColor(HexColor('#DBEAFE'))
        c.roundRect(0, 0, 6*cm, 2*cm, 8, fill=1, stroke=0)
        # Lines for connections
        c.setStrokeColor(HexColor('#6B7280'))
        c.setLineWidth(2)
        c.line(3*cm, 2*cm, 3*cm, 4*cm)
        # Text labels
        c.setFont('NotoSansKR', 12)
        c.drawCentredString(3*cm, 0.7*cm, '한국어 라벨')
```

Useful Canvas primitives:
- `roundRect(x, y, w, h, radius)` — colored boxes, cards
- `line(x1, y1, x2, y2)` — connections, arrows
- `circle(x, y, r)` — nodes, bullets
- `drawCentredString(x, y, text)` — centered labels
- `setFillColor()` / `setStrokeColor()` — theming

### ColorBox Pattern

A reusable colored banner/callout:

```python
class ColorBox(Flowable):
    def __init__(self, text, bg_color, text_color, width, height, font_size=16):
        Flowable.__init__(self)
        self.text, self.bg, self.tc = text, bg_color, text_color
        self.width, self.height, self.fs = width, height, font_size

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.width, self.height, 10, fill=1, stroke=0)
        c.setFillColor(self.tc)
        c.setFont('NotoSansKR', self.fs)
        tw = c.stringWidth(self.text, 'NotoSansKR', self.fs)
        c.drawString((self.width - tw) / 2, self.height / 2 - self.fs / 3, self.text)
```

### Bar Chart Pattern

Horizontal bar charts for comparisons:

```python
class BarChart(Flowable):
    def __init__(self, data, width, height):
        # data: list of (label, value, max_value, color)
        Flowable.__init__(self)
        self.data, self.width, self.height = data, width, height

    def draw(self):
        c = self.canv
        bar_h, gap = 1.0*cm, 0.8*cm
        max_bar_w = self.width * 0.55
        for i, (label, value, max_val, color) in enumerate(reversed(self.data)):
            y = i * (bar_h + gap)
            c.setFont('NotoSansKR', 12)
            c.drawString(0, y + bar_h/2 - 4, label)
            bar_w = (value / max_val) * max_bar_w
            c.setFillColor(color)
            c.roundRect(self.width*0.35, y, bar_w, bar_h, 5, fill=1, stroke=0)
```

### Embedding External Images (SVG/PNG)

Convert SVG to PNG, then embed with reportlab Image:

```python
import subprocess
from reportlab.platypus import Image
from reportlab.lib.units import cm

# SVG to PNG via rsvg-convert (brew install librsvg)
subprocess.run(['rsvg-convert', 'diagram.svg', '-o', 'diagram.png'], check=True)

# Or via cairosvg (pip install cairosvg)
import cairosvg
cairosvg.svg2png(url='diagram.svg', write_to='diagram.png', dpi=200)

# Embed in story
img = Image('diagram.png', width=14*cm, height=8*cm)
story.append(img)
```

### Architecture Diagram Pattern

For MoE/pipeline/flow diagrams:

```python
class ArchDiagram(Flowable):
    def draw(self):
        c = self.canv
        # Input layer (bottom)
        c.setFillColor(HexColor('#DBEAFE'))
        c.roundRect(self.w/2 - 3*cm, 0, 6*cm, 1.5*cm, 8, fill=1, stroke=0)
        # Router (middle)
        c.setFillColor(HexColor('#FEF3C7'))
        c.roundRect(self.w/2 - 2*cm, 2.2*cm, 4*cm, 1.3*cm, 8, fill=1, stroke=0)
        # Expert boxes (top row, highlight active ones)
        for i in range(8):
            color = HexColor('#10B981') if i in active_set else HexColor('#F3F4F6')
            c.setFillColor(color)
            c.roundRect(x, y, expert_w, expert_h, 6, fill=1, stroke=0)
        # Arrows connecting layers
        c.line(src_x, src_y, dst_x, dst_y)
```

### Best Practices

- Use Canvas Flowables for reproducible, resolution-independent diagrams
- Embed external PNG/JPEG via `reportlab.platypus.Image` with explicit width/height
- Convert SVG to PNG with `rsvg-convert` (macOS: `brew install librsvg`) or `cairosvg`
- For complex diagrams, generate SVG first (better tooling), then embed as PNG
- Always set `preserveAspectRatio=True` on Image flowables
- Use colorful backgrounds (roundRect with fill) to create visual weight on each page
- Table with colored cells works as a simple grid/comparison chart
