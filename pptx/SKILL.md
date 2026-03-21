---
name: pptx
description: "PowerPoint PPTX create, read, edit, review. Triggers: PowerPoint, PPTX, presentation, slides, deck."
---

# PPTX Skill

Create, read, edit, or review PPTX presentations.
Scope: programmatic slide creation (PptxGenJS), editing existing PPTX (OOXML workflow), design system, visual QA loop.
Out of scope: Keynote, Google Slides API, PDFs, image generation.

---

## Quick Reference

| Task       | Tool                                        |
| ---------- | ------------------------------------------- |
| **Create** | `pptxgenjs` (npm) — JavaScript              |
| **Read**   | `markitdown[pptx]` or `thumbnail.py`        |
| **Edit**   | Unpack → XML Edit → Pack. See [editing.md](editing.md) |
| **Review** | soffice → PDF → pdftoppm → image inspection |
| **Search** | `pptx_cli.py search input.pptx "pattern" [--json]` |
| **TOC**    | `pptx_cli.py toc input.pptx [--json]` |

For PptxGenJS API reference, see [pptxgenjs.md](pptxgenjs.md).

### Unified CLI (`pptx_cli.py`)

```bash
# Unpack / Pack
python scripts/pptx_cli.py open input.pptx work/
python scripts/pptx_cli.py save work/ output.pptx

# Validation & Repair
python scripts/pptx_cli.py validate input.pptx --json
python scripts/pptx_cli.py repair input.pptx              # dry-run (default)
python scripts/pptx_cli.py repair input.pptx --apply       # actually fix

# Text & Thumbnails
python scripts/pptx_cli.py text input.pptx
python scripts/pptx_cli.py thumbnail input.pptx grid.png
python scripts/pptx_cli.py thumbnail input.pptx out_dir/ --individual

# Slide Operations (unpacked dir)
python scripts/pptx_cli.py add-slide work/ --blank
python scripts/pptx_cli.py add-slide work/ --duplicate 3 --position 1
python scripts/pptx_cli.py clean work/
python scripts/pptx_cli.py clean work/ --delete

# Export
python scripts/pptx_cli.py export-pdf input.pptx output.pdf

# Search & Navigation (presentation order)
python scripts/pptx_cli.py search input.pptx "pattern" --json
python scripts/pptx_cli.py toc input.pptx --json
```

---

## Reading Content

```bash
python scripts/pptx_cli.py text presentation.pptx          # Text extraction
python -m markitdown presentation.pptx                      # Alternative
python scripts/pptx_cli.py thumbnail presentation.pptx t.png  # Visual overview
python scripts/pptx_cli.py open presentation.pptx unpacked/ # Raw XML access
python scripts/pptx_cli.py validate presentation.pptx --json # Structure check
python scripts/pptx_cli.py repair presentation.pptx          # Auto-repair
```

---

## Converting to Images

```bash
python scripts/ooxml/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
# Creates slide-01.jpg, slide-02.jpg, etc.

# Re-render specific slide after fixes:
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## Design System

### 60-30-10 Color Rule

Apply this ratio to every presentation:
- **60%** — Primary (background, large surfaces)
- **30%** — Secondary (content areas, cards)
- **10%** — Accent (CTA, key metrics, icons)

**20 color palettes and font pairings** → [references/design-system.md](references/design-system.md)

### Typography Sizes

| Element            | Size    | Style        |
| ------------------ | ------- | ------------ |
| Slide title        | 36-44pt | bold         |
| Section header     | 20-24pt | bold         |
| Body text          | 14-16pt | regular      |
| Caption/source     | 10-12pt | muted color  |
| Key metric callout | 60-72pt | bold, accent |

### Spacing

- Slide edge margin: minimum **0.5 inches**
- Content block spacing: **0.3–0.5 inches** (keep consistent)
- White space is premium — leave breathing room

### Visual Hierarchy

1. **Size** — important things are larger
2. **Color** — accent only for CTA and key metrics
3. **Weight** — bold for titles and key points only; body stays regular

### Slide Layout Ideas

Every slide needs a visual element — image, chart, icon, or shape.

**Layout options:** two-column (text + illustration), icon + text rows, 2×2 / 2×3 grid, half-bleed image with overlay, full-bleed background, section dividers.

**Building blocks:** See [pptxgenjs.md → Composable Patterns](pptxgenjs.md#composable-patterns) for reusable code primitives. Combine these to create layouts — design each deck fresh.

**Data display:** large stat callouts (60-72pt), comparison columns, timeline/process flows.

**Visual polish:**
- Icons in colored circles next to section headers
- Commit to one visual motif and repeat across every slide
- Dark backgrounds for title + conclusion, light for content ("sandwich" structure)

---

## Common Mistakes

| Mistake                         | Better Approach                            | Why                                   |
| ------------------------------- | ------------------------------------------ | ------------------------------------- |
| Repeat same layout              | Mix: 2-column, cards, callout, chart       | Monotony kills audience focus         |
| Center-align body text          | Left-align body, center titles only        | Readability principle                 |
| Insufficient size contrast      | Title 36pt+, body 14-16pt                 | Visual hierarchy is essential         |
| Default blue palette            | Choose theme-appropriate palette           | Design intent shows                   |
| Inconsistent spacing            | Standardize at 0.3" or 0.5"               | Creates polished feel                 |
| Text-only slides                | Add images, charts, icons, shapes          | Slides without visuals are forgotten  |
| Ignore text box padding         | Set `margin: 0` or offset compensation     | Lines/shapes misalign with text       |
| Decorative line under title     | Use whitespace or background color         | Hallmark of AI-generated slides       |
| Low contrast elements           | Light bg → dark text (min 4.5:1 ratio)     | Accessibility and readability         |
| All content on one slide        | 1 slide = 1 message principle              | Prevent information overload          |
| `#` in color values             | `'4472C4'` (no #)                          | PptxGenJS throws error                |
| 8-digit hex colors              | `'4472C4'` (6-digit only)                  | Alpha channel unsupported             |
| Reuse options objects           | New object literal each time               | Shared reference causes side effects  |
| CJK text with default width     | Use `estimateTextWidthInches()`            | Korean overflows Latin-sized boxes    |
| Copy layout patterns verbatim   | Use composable primitives, design fresh    | Prevents cookie-cutter decks          |

---

## QA Verification Loop

First render almost always has issues. QA is bug hunting, not confirmation.

### Step 1: Machine QA (run before visual review)

```bash
# 1. Structural validation — must pass
python scripts/pptx_cli.py validate output.pptx --json

# 2. Placeholder remnant check — zero matches expected
python scripts/pptx_cli.py text output.pptx | grep -iE "xxxx|lorem|ipsum|placeholder|TODO|click to"

# 3. Slide count check
python scripts/pptx_cli.py text output.pptx | grep -c "^--- Slide"

# 4. Orphan media detection
python scripts/pptx_cli.py clean work/ 2>&1
```

### Step 2: Visual QA (use subagents for fresh eyes)

Delegate visual inspection to subagents — you've been staring at code and will see what you expect.

```bash
python scripts/pptx_cli.py export-pdf output.pptx output.pdf
pdftoppm -jpeg -r 150 output.pdf slide
# Or: python scripts/pptx_cli.py thumbnail output.pptx contact_sheet.png
```

**Subagent prompt template:**

```
Inspect these slides. Assume there are issues — find them.

Check for:
- Overlapping elements (text through shapes, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Source citations or footers colliding with content
- Elements too close (< 0.3" gaps) or cramped areas
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text or icons
- Text boxes too narrow causing excessive wrapping
- Korean text truncated, unnatural line breaks, or font fallback issues

For each slide, list issues found. Read and analyze:
1. /path/to/slide-01.jpg (Expected: [brief description])
```

### Step 3: Fix & Re-verify

1. Fix issue → re-run machine QA (catches regressions)
2. Re-render only the fixed slide: `pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed`
3. Re-inspect visually — one fix often creates another problem
4. Complete at least 1 fix-and-verify cycle before declaring done

---

## CJK / Korean Text Handling

### Text Box Width

CJK characters are full-width (~2× Latin). Default PptxGenJS sizing assumes Latin metrics, causing overflow.

```javascript
function estimateTextWidthInches(text, fontSize) {
  let charUnits = 0;
  for (const char of text) {
    const code = char.codePointAt(0);
    if (
      (code >= 0x1100 && code <= 0x11FF) ||   // Hangul Jamo
      (code >= 0x3000 && code <= 0x9FFF) ||   // CJK + symbols
      (code >= 0xAC00 && code <= 0xD7AF) ||   // Hangul Syllables
      (code >= 0xF900 && code <= 0xFAFF) ||   // CJK Compat
      (code >= 0xFF00 && code <= 0xFFEF)      // Fullwidth Forms
    ) {
      charUnits += 2;
    } else {
      charUnits += 1;
    }
  }
  return charUnits * fontSize * 0.0104 * 0.9;
}
```

### Korean Language Attributes

Set `lang="ko-KR"` to enable kinsoku (line-break rules) and spell-checking:

```javascript
slide.addText('한글 텍스트', {
  fontFace: 'Noto Sans KR', fontSize: 16, lang: 'ko-KR'
});
```

If `lang` is unavailable, post-process:

```bash
python scripts/ooxml/unpack.py output.pptx unpacked/
python -c "from scripts.ooxml.cjk_utils import inject_korean_lang; inject_korean_lang('unpacked/ppt/slides/')"
python scripts/ooxml/pack.py unpacked/ output_ko.pptx --original output.pptx
```

### East Asian Font Theme

Set Korean font in theme XML for consistent rendering:

```xml
<!-- ppt/theme/theme1.xml -->
<a:fontScheme name="Korean">
  <a:majorFont>
    <a:latin typeface="Calibri"/>
    <a:ea typeface=""/>
    <a:font script="Hang" typeface="Noto Sans KR"/>
  </a:majorFont>
  <a:minorFont>
    <a:latin typeface="Calibri"/>
    <a:ea typeface=""/>
    <a:font script="Hang" typeface="Noto Sans KR"/>
  </a:minorFont>
</a:fontScheme>
```

Korean font options → [references/design-system.md](references/design-system.md#korean-fonts)

---

## Accessibility (WCAG 2.1 AA)

| Requirement        | Standard          | Implementation                          |
| ------------------ | ----------------- | --------------------------------------- |
| Color contrast     | >= 4.5:1          | Use `cjk_utils.check_contrast()`       |
| Image alt text     | Required on all   | `altText` property on `addImage()`      |
| Minimum font size  | >= 10pt           | No captions below 10pt                  |
| Language metadata  | `lang="ko-KR"`   | Screen reader pronunciation support     |
| Reading order      | Logical flow      | `addText/addImage` call order = reader order |
| Slide titles       | Every slide       | Navigation for screen readers            |

---

## Dependencies

```bash
npm install pptxgenjs          # Presentation creation
pip install "markitdown[pptx]"  # Text extraction
pip install Pillow              # Thumbnail generation
pip install defusedxml          # Safe XML parsing (validate.py, repair.py)
# LibreOffice (soffice)         # PDF conversion
# Poppler (pdftoppm)            # PDF → image
# scripts/ooxml/cjk_utils.py   # Korean: width calc, lang injection, contrast check
```
