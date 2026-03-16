---
name: html2pptx
description: "Convert HTML slides into native PowerPoint elements. Triggers: HTML to PPTX, convert HTML slides, html2pptx."
---

# HTML to PPTX Skill

Convert HTML slides into native PowerPoint elements with accurate positioning.
Triggers: "HTML to PPTX", "convert HTML slides", "HTML presentation", "html2pptx".
Covers: HTML→native PPTX conversion (text, images, shapes, lists), screenshot fallback.
Do NOT use for: programmatic PPTX creation (use pptx skill), Keynote, Google Slides.

For programmatic slide creation without HTML, see [pptx skill](../pptx/SKILL.md).

---

## Quick Reference

| Task                     | Tool                                                                      |
| ------------------------ | ------------------------------------------------------------------------- |
| **Convert (native)**     | `require("./scripts/html2pptx.cjs")` — library, not CLI                   |
| **Convert (screenshot)** | `node scripts/convert.mjs slide.html [output.pptx] [--layout 16x9\|4x3]`  |
| **Batch convert**        | `node scripts/batch.mjs slide-01.html slide-02.html [--output deck.pptx] [--layout 16x9\|4x3]` |

---

## How It Works

```
HTML file → Playwright render → page.evaluate():
  ├── body background extraction (image/color)
  ├── DOM element traversal
  │   ├── <div> + background/border → shape element
  │   ├── <img> → image element
  │   ├── <p>, <h1>-<h6> → text element + inline formatting
  │   ├── <ul>, <ol> → bullet list element
  │   └── .placeholder → { x, y, w, h } for addChart() etc.
  └── validation (overflow, dimension mismatch)
→ PptxGenJS addText/addImage/addShape()
→ { slide, placeholders }
```

---

## Usage

### Single Slide

```javascript
const pptxgen = require("pptxgenjs");
const html2pptx = require("./scripts/html2pptx.cjs");

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // or "LAYOUT_4x3" — must match HTML body dimensions

  const { slide, placeholders } = await html2pptx("slide.html", pres);

  // Use placeholders for charts (if HTML had class="placeholder" elements)
  if (placeholders.length > 0) {
    slide.addChart(pres.charts.LINE, chartData, placeholders[0]);
  }

  await pres.writeFile({ fileName: "output.pptx" });
})();
```

### Batch (Multiple Slides)

```javascript
const path = require("path");
const pptxgen = require("pptxgenjs");
const html2pptx = require("./scripts/html2pptx.cjs");

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";

  const slides = ["slide-01.html", "slide-02.html", "slide-03.html"];
  for (const file of slides) {
    await html2pptx(path.join(__dirname, file), pres);
  }
  await pres.writeFile({ fileName: "deck.pptx" });
})();
```

### Screenshot Fallback

When CSS is too complex for native conversion:

```bash
node scripts/convert.mjs slide.html output.pptx
```

This renders the HTML as a full-page screenshot and embeds it as a single image.
**Tradeoff**: pixel-perfect visuals, but text is not selectable/editable.

---

## HTML Authoring Rules

### Required

- `<body>` must have explicit `width` and `height` matching the presentation layout
  - LAYOUT_16x9: `width: 960px; height: 540px` (10" × 5.625" at 96 DPI)
  - LAYOUT_4x3: `width: 960px; height: 720px` (10" × 7.5" at 96 DPI)
  - Use `--layout 4x3` flag in CLI wrappers for 4:3 mode
- All text must be in `<p>`, `<h1>`-`<h6>`, `<ul>`, or `<ol>` — not bare text in `<div>`

### Supported CSS

| CSS Property          | PPTX Mapping      | Notes                                     |
| --------------------- | ----------------- | ----------------------------------------- |
| `background-color`    | shape fill        | On `<div>` only, not text elements        |
| `border` (uniform)    | shape line        | Must be same width on all 4 sides         |
| `border` (partial)    | line shapes       | Individual lines for each side            |
| `border-radius`       | `rectRadius`      | px, pt, or % supported                    |
| `box-shadow`          | shadow prop       | Outer only, inset shadows ignored         |
| `transform: rotate()` | `rotate` prop     | Degrees, matrix also parsed               |
| `writing-mode`        | 90°/270°          | `vertical-rl` = 90°, `vertical-lr` = 270° |
| `text-transform`      | applied directly  | uppercase, lowercase, capitalize          |
| `<b>`, `<strong>`     | `bold: true`      |                                           |
| `<i>`, `<em>`         | `italic: true`    |                                           |
| `<u>`                 | `underline: true` |                                           |

### NOT Supported

| CSS Property                 | Workaround                                                 |
| ---------------------------- | ---------------------------------------------------------- |
| CSS gradients                | Rasterize to PNG with Sharp, use `background-image: url()` |
| Background images on `<div>` | Use `<img>` element or slide-level `background`            |
| `box-shadow: inset`          | Not supported in PowerPoint                                |
| Margins on inline `<span>`   | Use padding on parent or position differently              |
| Bare text in `<div>`         | Wrap in `<p>` or heading tags                              |

---

## Placeholders

Add `class="placeholder"` to any `<div>` to extract its position:

```html
<div class="placeholder" id="chart-area"
     style="position: absolute; left: 100px; top: 200px; width: 400px; height: 300px;">
</div>
```

The converter skips rendering this element and returns:
```javascript
{ id: "chart-area", x: 1.04, y: 2.08, w: 4.17, h: 3.12 }
```

Use these coordinates to place charts, external images, or other programmatic content.

---

## Validation

The converter validates and throws errors for:

| Check                     | Error Message Pattern                                |
| ------------------------- | ---------------------------------------------------- |
| Content overflow          | "HTML content overflows body by Xpt horizontally..." |
| Dimension mismatch        | "HTML dimensions don't match presentation layout..." |
| Text too close to bottom  | "Text box ends too close to bottom edge..."          |
| CSS gradients             | "CSS gradients are not supported..."                 |
| Background images on div  | "Background images on DIV elements..."               |
| Bare text in div          | "DIV element contains unwrapped text..."             |
| Styling on text elements  | "Text element has background/border/shadow..."       |
| Manual bullet symbols     | "Text element starts with bullet symbol..."          |
| Margins on inline spans   | "Inline element has margin-left..."                  |

All validation errors are collected and thrown together in a single error.

---

## Anti-Patterns

| ❌ Don't                               | ✅ Do Instead                               | Why                                    |
| -------------------------------------- | ------------------------------------------ | -------------------------------------- |
| Bare text in `<div>`                   | Wrap in `<p>`, `<h1>`-`<h6>`, `<ul>`      | Bare text is silently dropped          |
| Background/border on `<p>`, `<h>` tags | Move styling to parent `<div>`             | Only `<div>` maps to PPTX shapes      |
| CSS gradients                          | Rasterize to PNG first                     | No PPTX gradient equivalent            |
| Manual bullet chars (`• Item`)         | Use `<ul><li>Item</li></ul>`               | Proper PPTX bullets with indentation   |
| Margins on `<span>`                    | Use padding on parent element              | Inline margins ignored in PowerPoint   |
| Omit body width/height                 | Always set explicit dimensions             | Converter can't infer slide size       |
| `<div>` background-image               | Use `<img>` or slide-level background      | Div bg images not extracted            |

---

## Dependencies

```bash
npm install pptxgenjs playwright sharp
npx playwright install chromium   # Download browser binary
```

> **macOS**: `convert.mjs`/`html2pptx.cjs`는 `channel: "chrome"`로 시스템 Chrome을 사용합니다.
> Chrome이 없으면 `launchOptions.channel` 제거 후 Playwright 번들 Chromium을 사용하세요.

---

## QA Workflow

```bash
# 1. Convert
node scripts/batch.mjs slide-*.html --output deck.pptx

# 2. Visual check
soffice --headless --convert-to pdf deck.pptx
pdftoppm -jpeg -r 150 deck.pdf slide

# 3. Compare HTML source vs PPTX output
# Open both side-by-side and check:
# - Text positioning matches
# - Colors/fills match
# - Images present and sized correctly
# - No elements missing or duplicated
```

Checklist:
- [ ] All text elements converted (no bare text dropped)
- [ ] Shape fills match HTML background colors
- [ ] Border rendering correct (uniform or partial)
- [ ] Image positions match HTML layout
- [ ] Placeholder coordinates returned correctly
- [ ] No validation errors thrown
- [ ] Text selectable in PowerPoint (not rasterized)
