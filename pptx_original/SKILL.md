---
name: pptx
description: "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\" \"slides,\" \"presentation,\" or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill."
license: Proprietary. LICENSE.txt has complete terms
---

# PPTX Skill

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Edit or create from template | Read [editing.md](editing.md) |
| Create from scratch | Read [pptxgenjs.md](pptxgenjs.md) |

---

## Reading Content

```bash
python -m markitdown presentation.pptx        # text extraction
python scripts/thumbnail.py presentation.pptx  # visual overview
python scripts/office/unpack.py presentation.pptx unpacked/  # raw XML
```

---

## Editing Workflow

Read [editing.md](editing.md) for full details.

1. Analyze template with `thumbnail.py`
2. Unpack → manipulate slides → edit content → clean → pack

---

## Creating from Scratch

Read [pptxgenjs.md](pptxgenjs.md) for full details. Use when no template or reference presentation is available.

---

## Design Principles

### Before Starting

- **Pick a bold, content-informed color palette**: if swapping your colors into a different presentation would still "work," your choices aren't specific enough
- **Dominance over equality**: one color dominates (60–70%), 1–2 supporting tones, one sharp accent
- **Dark/light contrast**: dark backgrounds for title + conclusion slides, light for content ("sandwich" structure)
- **Commit to a visual motif**: pick one distinctive element and repeat it (rounded image frames, icons in colored circles, thick single-side borders)

### Color Palettes

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| Midnight Executive | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` |
| Forest & Moss | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` |
| Coral Energy | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` |
| Warm Terracotta | `B85042` (terracotta) | `E7E8D1` (sand) | `A7BEAE` |
| Ocean Gradient | `065A82` (deep blue) | `1C7293` (teal) | `21295C` |
| Charcoal Minimal | `36454F` (charcoal) | `F2F2F2` (off-white) | `212121` |
| Teal Trust | `028090` (teal) | `00A896` (seafoam) | `02C39A` |
| Berry & Cream | `6D2E46` (berry) | `A26769` (dusty rose) | `ECE2D0` |
| Sage Calm | `84B59F` (sage) | `69A297` (eucalyptus) | `50808E` |
| Cherry Bold | `990011` (cherry) | `FCF6F5` (off-white) | `2F3C7E` |

### Per-Slide Guidelines

**Every slide needs a visual element** — image, chart, icon, or shape.

**Layout options:**
- Two-column (text left, illustration right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2×2 or 2×3 grid with content blocks
- Half-bleed image with content overlay

**Data display:**
- Large stat callouts (60–72pt numbers with small labels)
- Comparison columns (before/after, pros/cons)
- Timeline or process flow (numbered steps, arrows)

### Typography

Choose a header font with personality paired with a clean body font:

| Header | Body |
|--------|------|
| Georgia | Calibri |
| Arial Black | Arial |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Palatino | Garamond |

| Element | Size |
|---------|------|
| Slide title | 36–44pt bold |
| Section header | 20–24pt bold |
| Body text | 14–16pt |
| Captions | 10–12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3–0.5" between content blocks
- Leave breathing room

### Common Mistakes to Avoid

- Repeating the same layout across slides — vary columns, cards, and callouts
- Centering body text — left-align paragraphs and lists; center only titles
- Insufficient size contrast — titles need 36pt+ to stand out from 14–16pt body
- Defaulting to blue — pick colors reflecting the specific topic
- Inconsistent spacing — choose 0.3" or 0.5" gaps and use consistently
- Styling one slide but leaving the rest plain — commit fully or keep it simple throughout
- Text-only slides — add images, icons, charts, or visual elements
- Missing text box padding — when aligning lines/shapes with text edges, set `margin: 0` or offset to account for padding
- Low-contrast elements — icons and text both need strong contrast against background
- Accent lines under titles — these read as AI-generated; use whitespace or background color instead

---

## QA (Required)

Approach QA as a bug hunt. Your first render is almost never correct.

### Content QA

```bash
python -m markitdown output.pptx
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

Fix any leftover placeholder text before declaring success.

### Visual QA

Use subagents for visual inspection — even for 2–3 slides. Fresh eyes catch what you miss after staring at code.

Convert slides to images (see below), then have the subagent inspect with this prompt:

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Elements too close (< 0.3" gaps) or uneven spacing
- Insufficient margin from slide edges (< 0.5")
- Low-contrast text or icons
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues found.
```

### Verification Loop

1. Generate slides → convert to images → inspect
2. List issues found
3. Fix issues
4. Re-verify affected slides — one fix often creates another problem
5. Repeat until a full pass reveals no new issues

Complete at least one fix-and-verify cycle before declaring success.

---

## Converting to Images

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
# Creates slide-01.jpg, slide-02.jpg, etc.

# Re-render specific slide after fix:
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## Dependencies

- `pip install "markitdown[pptx]"` — text extraction
- `pip install Pillow` — thumbnail grids
- `npm install -g pptxgenjs` — creating from scratch
- LibreOffice (`soffice`) — PDF conversion (auto-configured via `scripts/office/soffice.py`)
- Poppler (`pdftoppm`) — PDF to images
