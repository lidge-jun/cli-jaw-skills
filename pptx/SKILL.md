---
name: pptx
description: "PowerPoint PPTX create, read, edit, review. Triggers: PowerPoint, PPTX, presentation, slides, deck."
---

# PPTX Skill

Use this skill for any PowerPoint task: create, read, edit, or review PPTX presentations.
Triggers: "PowerPoint", "PPTX", "presentation", "slides", "deck".
Covers: programmatic slide creation (PptxGenJS), editing existing PPTX (OOXML workflow), design system, visual QA loop.
Do NOT use for: Keynote, Google Slides API, PDFs, or image generation.

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

All operations are available through a single entrypoint:

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
# Text extraction (unified CLI)
python scripts/pptx_cli.py text presentation.pptx

# Text extraction (alternative)
python -m markitdown presentation.pptx

# Visual overview (thumbnail grid)
python scripts/pptx_cli.py thumbnail presentation.pptx thumbnails.png

# Raw XML access
python scripts/pptx_cli.py open presentation.pptx unpacked/

# Validate structure
python scripts/pptx_cli.py validate presentation.pptx --json
# Returns: {"passed": bool, "errors": [...], "warnings": [...], "stats": {...}}

# Auto-repair (if validation fails)
python scripts/pptx_cli.py repair presentation.pptx
```

---

## Converting to Images

```bash
python scripts/ooxml/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

Creates `slide-01.jpg`, `slide-02.jpg`, etc.

To re-render specific slides after fixes:
```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## Design System

### 60-30-10 Color Rule

Apply this ratio to every presentation:
- **60%** — Primary (background, large surfaces)
- **30%** — Secondary (content areas, cards)
- **10%** — Accent (CTA, key metrics, icons)

### Color Palettes (20 options)

Select a palette that matches the content theme. Never settle for default blue.

#### Business & Professional

| Theme              | Primary (60%) | Secondary (30%) | Accent (10%) |
| ------------------ | ------------- | --------------- | ------------ |
| Midnight Executive | `1E2761`      | `CADCFC`        | `FFFFFF`     |
| Charcoal Minimal   | `36454F`      | `F2F2F2`        | `212121`     |
| Navy Corporate     | `0D1B2A`      | `1B3A5C`        | `E0E1DD`     |
| Slate Professional | `2C3E50`      | `ECF0F1`        | `E74C3C`     |

#### Nature & Wellness

| Theme          | Primary (60%) | Secondary (30%) | Accent (10%) |
| -------------- | ------------- | --------------- | ------------ |
| Forest & Moss  | `2C5F2D`      | `97BC62`        | `F5F5F5`     |
| Sage Calm      | `84B59F`      | `69A297`        | `50808E`     |
| Ocean Gradient | `065A82`      | `1C7293`        | `21295C`     |
| Earth Warm     | `5D4037`      | `D7CCC8`        | `FF8F00`     |

#### Energy & Creative

| Theme           | Primary (60%) | Secondary (30%) | Accent (10%) |
| --------------- | ------------- | --------------- | ------------ |
| Coral Energy    | `F96167`      | `F9E795`        | `2F3C7E`     |
| Cherry Bold     | `990011`      | `FCF6F5`        | `2F3C7E`     |
| Berry & Cream   | `6D2E46`      | `A26769`        | `ECE2D0`     |
| Electric Purple | `5B2C6F`      | `D2B4DE`        | `F39C12`     |

#### Tech & Modern

| Theme       | Primary (60%) | Secondary (30%) | Accent (10%) |
| ----------- | ------------- | --------------- | ------------ |
| Teal Trust  | `028090`      | `00A896`        | `02C39A`     |
| Neon Dark   | `121212`      | `1DB954`        | `FFFFFF`     |
| Cyber Blue  | `0A192F`      | `64FFDA`        | `CCD6F6`     |
| Glass Light | `F8F9FA`      | `E9ECEF`        | `495057`     |

#### Warmth & Friendly

| Theme           | Primary (60%) | Secondary (30%) | Accent (10%) |
| --------------- | ------------- | --------------- | ------------ |
| Warm Terracotta | `B85042`      | `E7E8D1`        | `A7BEAE`     |
| Golden Hour     | `F4A261`      | `264653`        | `E76F51`     |
| Rose Soft       | `FADBD8`      | `F5B7B1`        | `922B21`     |
| Sand Dune       | `C4A35A`      | `F5F0E1`        | `3E2723`     |

### Font Pairings

| Header       | Body           | Mood                  |
| ------------ | -------------- | --------------------- |
| Georgia      | Calibri        | Classic, trustworthy   |
| Arial Black  | Arial          | Bold, intuitive        |
| Trebuchet MS | Calibri        | Modern, clean          |
| Cambria      | Calibri Light  | Academic, polished     |
| Impact       | Arial          | Impactful              |
| Palatino     | Garamond       | Elegant, formal        |
| Consolas     | Calibri        | Tech, code             |
| Segoe UI     | Segoe UI Light | MS native, contemporary|

### Typography Sizes

| Element            | Size    | Style        |
| ------------------ | ------- | ------------ |
| Slide title        | 36-44pt | bold         |
| Section header     | 20-24pt | bold         |
| Body text          | 14-16pt | regular      |
| Caption/source     | 10-12pt | muted color  |
| Key metric callout | 60-72pt | bold, accent |

### Spacing Principles

- Slide edge margin: minimum **0.5 inches**
- Content block spacing: **0.3–0.5 inches** (keep consistent)
- White space is "premium" — don't fill every inch

### Visual Hierarchy

1. **Size** — important things are larger
2. **Color** — accent only for CTA and key metrics
3. **Weight** — bold for titles and key points only; body stays regular

### Slide Layout Ideas

**Every slide needs a visual element** — image, chart, icon, or shape. Text-only slides are forgettable.

**Layout options for each slide:**
- Two-column (text left, illustration right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2×2 or 2×3 grid (image on one side, grid of content blocks on other)
- Half-bleed image (full left/right side) with content overlay
- Full-bleed background with overlaid text box
- Section dividers with bold centered text

**Building blocks**: See [pptxgenjs.md → Composable Patterns](pptxgenjs.md#composable-patterns) for reusable code primitives (accent bars, badges, data-driven loops, etc.). Combine these to create your own layouts — never copy a layout recipe wholesale.

**Data display ideas:**
- Large stat callouts (big numbers 60-72pt with small labels below)
- Comparison columns (before/after, pros/cons, side-by-side)
- Timeline or process flow (numbered steps, arrows)

**Visual polish:**
- Icons in small colored circles next to section headers
- Italic accent text for key stats or taglines
- Commit to a visual motif — pick ONE distinctive element and repeat across every slide (rounded frames, thick side borders, etc.)
- **Dark/light contrast**: Dark backgrounds for title + conclusion, light for content ("sandwich" structure)

---

## Anti-Patterns

| ❌ Don't                        | ✅ Do Instead                            | Why                                   |
| ------------------------------- | --------------------------------------- | ------------------------------------- |
| Repeat same layout              | Mix: 2-column, cards, callout, chart    | Monotony kills audience focus         |
| Center-align body text          | Left-align body, center titles only     | Readability principle                 |
| Insufficient size contrast      | Title 36pt+, body 14-16pt              | Visual hierarchy is essential         |
| Stick with default blue         | Choose theme-appropriate palette        | Design intent must show               |
| Inconsistent spacing            | Standardize at 0.3" or 0.5"            | Creates polished feel                 |
| Text-only slides                | Add images, charts, icons, shapes       | Slides without visuals are forgotten  |
| Ignore text box padding         | Set `margin: 0` or offset compensation  | Lines/shapes misalign with text       |
| Decorative line under title     | Use whitespace or background color      | Hallmark of AI-generated slides       |
| Low contrast elements           | Light bg → dark text (min 4.5:1 ratio)  | Accessibility and readability         |
| All content on one slide        | 1 slide = 1 message principle           | Prevent information overload          |
| Use `#` in color values         | `'4472C4'` (no #)                       | PptxGenJS throws error                |
| Use 8-digit hex                 | `'4472C4'` (6-digit only)              | Alpha channel not supported           |
| Reuse options objects           | New object literal each time            | Shared reference causes unintended changes |
| CJK text box with default width | Use `estimateTextWidthInches()`         | Korean overflows default Latin sizing |
| Copy layout patterns verbatim   | Use composable primitives, design each deck fresh | Every presentation looks identical     |

---

## QA Verification Loop (MANDATORY)

**First render almost always has issues. QA is bug hunting, not confirmation.**

### Step 1: Machine QA (Automated — run before human review)

These checks can be run by CLI/script without visual inspection:

```bash
# 1. Structural validation
python scripts/pptx_cli.py validate output.pptx --json
# Must pass: no broken rels, valid XML, content-types consistent

# 2. Content extraction — check for placeholder remnants
python scripts/pptx_cli.py text output.pptx | grep -iE "xxxx|lorem|ipsum|placeholder|TODO|click to"
# Zero matches expected

# 3. Slide count sanity check
python scripts/pptx_cli.py text output.pptx | grep -c "^--- Slide"
# Must match expected slide count

# 4. Orphan media detection
python scripts/pptx_cli.py clean work/ 2>&1
# "No orphaned files" expected

# 5. (Optional) markitdown for richer content diff
pip install "markitdown[pptx]"
python -m markitdown output.pptx
```

**Machine QA checklist:**
- [ ] `validate --json` passes (no errors)
- [ ] No placeholder text in `text` output
- [ ] Slide count matches specification
- [ ] No orphaned media files
- [ ] No broken relationship targets

### Step 2: Human QA (Visual — always use subagents)

**⚠️ USE SUBAGENTS** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there. Subagents have fresh eyes.

```bash
# Render slides to images for inspection
python scripts/pptx_cli.py export-pdf output.pptx output.pdf
pdftoppm -jpeg -r 150 output.pdf slide
# Or use thumbnail grid:
python scripts/pptx_cli.py thumbnail output.pptx contact_sheet.png
```

**Subagent prompt template for visual inspection:**

```
Visually inspect these slides. Assume there are issues — find them.

Layout & spacing issues:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently

Visual quality issues:
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping

CJK/Korean text specific checks:
- Korean text truncated at text box right boundary?
- Unnatural syllable-level line breaks (kinsoku violations)?
- Font rendering as Noto Sans KR / intended font (no DroidSans fallback)?
- Korean-Latin mixed text spacing adequate?
- Table/chart column headers wide enough for Korean content?

For each slide, list issues or areas of concern, even if minor.
Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
Report ALL issues found, including minor ones.
```

**Human QA checklist:**
- [ ] Element overlap (text penetrating shapes)
- [ ] Text overflow/truncation
- [ ] Element spacing < 0.3" (too tight)
- [ ] Slide edge margin < 0.5"
- [ ] Alignment inconsistency among similar elements
- [ ] Insufficient contrast (light text on light background)
- [ ] Text boxes too narrow causing excessive wrapping
- [ ] Visual coherence across slides (consistent motif, color, spacing)

### Step 3: Fix & Re-verify

1. Find issue → fix
2. **Re-run machine QA** first (fast, catches regressions)
3. **Re-render only the fixed slide**: `pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed`
4. Re-inspect visually — one fix often creates another problem
5. **Never declare completion before at least 1 fix-and-verify cycle**

---

## CJK / Korean Text Handling

### Text Box Width for CJK

CJK characters are full-width (~2× Latin width). Default PptxGenJS text-box sizing assumes Latin metrics, causing:
- Text overflow outside box boundaries
- Excessive wrapping on short strings

**Always calculate width with CJK awareness:**

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

// Usage
const title = '한글 프레젠테이션 제목';
const w = Math.min(estimateTextWidthInches(title, 36) + 0.3, 11);
slide.addText(title, {
  x: (13.33 - w) / 2, y: 2.5, w, h: 1.5,
  fontSize: 36, fontFace: 'Noto Sans KR', bold: true
});
```

### Korean Language Attributes

Set `lang="ko-KR"` to enable kinsoku (line-break rules) and proper spell-checking:

```javascript
// PptxGenJS v3.12+
slide.addText('한글 텍스트', {
  fontFace: 'Noto Sans KR', fontSize: 16, lang: 'ko-KR'
});
```

If `lang` is not available, post-process the generated file:

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

Recommended fonts:

| Font               | License   | Cross-platform | Best for           |
| ------------------ | --------- | -------------- | ------------------ |
| Noto Sans KR       | OFL       | Win/Mac/Linux  | Safest choice      |
| Pretendard         | OFL       | Win/Mac/Linux  | Modern UI          |
| Malgun Gothic      | MS bundle | Windows only   | Windows-only decks |
| NanumGothic        | OFL       | Win/Mac/Linux  | General Korean     |

### CJK QA Checklist

**Machine-verifiable** (run via CLI/script):
- [ ] `cjk_utils.check_contrast()` passes for all text elements
- [ ] No CJK font names in document XML that aren't in embedded fonts list
- [ ] `text` output contains expected Korean content (no encoding corruption)

**Human-verifiable** (visual inspection required):
- [ ] Korean text not truncated at text box boundaries
- [ ] Line breaks occur at natural positions (not mid-word)
- [ ] No kinsoku violations (closing punctuation at line start)
- [ ] Korean-Latin mixed text has proper spacing
- [ ] Font renders as intended (no fallback to DroidSans or system default)
- [ ] Table columns wide enough for Korean content
- [ ] Slide title with Korean fits on one line (or wraps gracefully)

---

## Accessibility (WCAG 2.1 AA)

| Requirement        | Standard          | Implementation                          |
| ------------------ | ----------------- | --------------------------------------- |
| Color contrast     | >= 4.5:1          | Use `cjk_utils.check_contrast()` to verify |
| Image alt text     | Required on all   | `altText` property on `addImage()`      |
| Minimum font size  | >= 10pt           | No captions below 10pt                  |
| Language metadata  | `lang="ko-KR"`   | Screen reader pronunciation support     |
| Reading order      | Logical flow      | `addText/addImage` call order = screen reader order |
| Slide titles       | Every slide       | Helps navigation for screen readers     |

```javascript
// Alt text on images (required)
slide.addImage({
  path: 'chart.png', x: 1, y: 1, w: 5, h: 3,
  altText: 'Bar chart showing Q1-Q4 2025 revenue growth by region'
});

// Reading order: call order determines screen reader sequence
// Title → Body → Chart → Caption
slide.addText('Title', { ... });
slide.addText('Body content', { ... });
slide.addImage({ altText: 'Chart description', ... });
slide.addText('Source: Company Report', { ... });
```

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
