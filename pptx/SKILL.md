---
name: pptx
description: "PowerPoint PPTX create, read, edit, review. Triggers: PowerPoint, PPTX, presentation, slides, deck."
---

# PPTX Skill

Use this skill for PowerPoint `.pptx` creation, editing, review, and QA.
Triggers: `"PowerPoint"`, `"PPTX"`, `"presentation"`, `"slides"`, `"deck"`.
Primary tool: **officecli** (`~/.local/bin/officecli`).
Fallback: **pptxgenjs** for large programmatic generation and **Legacy Python scripts** for utilities officecli still lacks.
Do NOT use this skill for Keynote, Google Slides API automation, or image generation.

---

## Tool Discovery

Always inspect help before inventing properties:

```bash
officecli --help
officecli pptx add
officecli pptx set
officecli pptx query --help
```

Drill down for exact property lists:

```bash
officecli pptx add slide
officecli pptx add shape
officecli pptx set slide
officecli pptx set shape
```

---

## Quick Decision

| Task | Tool | Command | Notes |
|------|------|---------|-------|
| Create blank deck | officecli | `officecli create deck.pptx` | Start with a real PPTX |
| Add slide | officecli | `officecli add deck.pptx / --type slide --prop layout=blank` | Root parent is `/` |
| Add text/shape | officecli | `officecli add deck.pptx /slide[1] --type shape --prop text="Hello"` | Primary content path |
| Edit slide or shape | officecli | `officecli set deck.pptx /slide[1]/shape[2] --prop fill=4472C4` | Use exact spatial paths |
| Read / inspect | officecli | `officecli view deck.pptx text` | `text`, `annotated`, `outline`, `stats`, `issues`, `html`, `svg` |
| Query deck | officecli | `officecli query deck.pptx 'shape:contains("Revenue")'` | CSS-like selectors |
| Batch slide construction | officecli | `officecli batch deck.pptx --commands '[...]'` | Use for repeated layout work |
| Resident workflow | officecli | `officecli open deck.pptx` | Still pass file path after open |
| Layout / overflow scan | officecli | `officecli check deck.pptx` | Pair with `view ... issues` |
| CJK-safe authoring | officecli | `officecli` (PATH) | Global install includes CJK fork — auto-handles fonts/lang |
| Large data-driven deck generation | pptxgenjs (fallback) | `npm install pptxgenjs` | Fallback for 50+ composable slides |
| Thumbnails / orphan cleanup | Legacy Python fallback | `python scripts/thumbnail.py deck.pptx out_dir/ --individual` | Utility-only |

---

## Core Command Model

Runtime syntax is file-first:

```bash
officecli view FILE MODE
officecli add FILE PARENT --type TYPE --prop key=value
officecli set FILE PATH --prop key=value
officecli query FILE "selector"
officecli batch FILE --commands '[{"command":"add",...}]'
officecli open FILE
officecli close FILE
officecli check FILE
```

### PATH Syntax

```text
/slide[N]                   # Nth slide (1-based)
/slide[N]/shape[M]          # Mth shape on slide N
/slide[N]/placeholder[X]    # placeholder by index
/slide[N]/picture[M]        # Mth picture
/slide[N]/table[M]          # Mth table
/slide[N]/table[M]/tr[R]    # Rth row
/slide[N]/table[M]/tr[R]/cell[C]  # Cth cell
/slide[N]/chart[M]          # Mth chart
/slide[N]/video[M]          # Mth media object
/slide[N]/notes             # speaker notes
/                           # presentation root
```

---

## Common officecli Workflows

### Create a deck from scratch

```bash
officecli create deck.pptx
officecli add deck.pptx / --type slide --prop layout=blank --prop title='Quarterly Review'
officecli add deck.pptx /slide[1] --type shape   --prop text='Q2 2026 Business Update'   --prop x=2cm --prop y=3cm --prop width=22cm --prop height=3cm   --prop size=30 --prop bold=true --prop align=center

officecli add deck.pptx / --type slide --prop layout=titleContent --prop title='Key Highlights'
officecli add deck.pptx /slide[2] --type shape   --prop 'text=Revenue grew 23%
Margin expanded to 34%
New markets: APAC, LATAM'   --prop x=1.2cm --prop y=3.5cm --prop width=20cm --prop height=8cm   --prop list=bullet --prop size=18
```

### Edit, inspect, and query

```bash
officecli view deck.pptx text
officecli view deck.pptx outline
officecli view deck.pptx stats
officecli view deck.pptx annotated
officecli view deck.pptx issues
officecli check deck.pptx

officecli set deck.pptx /slide[2]/shape[2] --prop fill=4472C4 --prop color=FFFFFF
officecli set deck.pptx /slide[2] --prop transition=fade --prop advanceTime=3000

officecli query deck.pptx 'shape:contains("Revenue")'
officecli query deck.pptx 'picture:no-alt'
```

### Add other presentation objects

```bash
officecli add deck.pptx /slide[2] --type picture --prop path=chart.png --prop x=14cm --prop y=3cm --prop width=8cm --prop height=5cm

officecli add deck.pptx /slide[3] --type table --prop rows=4 --prop cols=3 --prop x=1cm --prop y=2cm --prop width=24cm --prop height=6cm

officecli add deck.pptx /slide[4] --type chart --prop chartType=column --prop title='Revenue by Quarter' --prop 'data=Revenue:12,15,18,20' --prop categories='Q1,Q2,Q3,Q4'

officecli add deck.pptx /slide[2] --type notes --prop text='Mention the Q3 forecast and margin bridge.'
```

---

## Batch Mode

Correct batch JSON uses `command`, `parent`/`path`, `type`, and `props`.

```bash
officecli batch deck.pptx --commands '[
  {
    "command": "add",
    "parent": "/",
    "type": "slide",
    "props": {"layout": "blank", "title": "Batch Slide"}
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {"text": "Revenue Story", "x": "2cm", "y": "3cm", "width": "20cm", "height": "3cm", "size": 28, "bold": true}
  },
  {
    "command": "set",
    "path": "/slide[1]/shape[2]",
    "props": {"fill": "1E2761", "color": "FFFFFF", "align": "center"}
  }
]'
```

---

## Query Mode

```bash
officecli query deck.pptx 'shape:contains("Revenue")'
officecli query deck.pptx 'slide[2] > shape[font="Arial"]'
officecli query deck.pptx 'chart'
officecli query deck.pptx 'picture:no-alt'
```

---

## Resident Mode (open / close)

Resident mode keeps the deck cached, but commands still include the file path.

```bash
officecli open deck.pptx
officecli set deck.pptx /slide[1] --prop transition=morph
officecli add deck.pptx /slide[1] --type shape --prop text='Resident note' --prop x=2cm --prop y=15cm --prop width=10cm --prop height=2cm
officecli close deck.pptx
```

Use resident mode for interactive polishing. Use batch when the whole edit set is deterministic.

---

## Design System

### 60-30-10 color rule

- **60%** primary surfaces/backgrounds
- **30%** secondary containers/cards
- **10%** accent highlights and key numbers

```bash
officecli set deck.pptx /slide[1] --prop background=1E2761
officecli add deck.pptx /slide[1] --type shape --prop fill=CADCFC --prop x=1cm --prop y=4cm --prop width=24cm --prop height=8cm
officecli add deck.pptx /slide[1] --type shape --prop text='23%' --prop color=E74C3C --prop size=68 --prop bold=true --prop x=9cm --prop y=6cm --prop width=6cm --prop height=3cm --prop align=center
```

### Recommended palettes

| Theme | Primary | Secondary | Accent |
|------|---------|-----------|--------|
| Midnight Executive | `1E2761` | `CADCFC` | `FFFFFF` |
| Slate Professional | `2C3E50` | `ECF0F1` | `E74C3C` |
| Forest & Moss | `2C5F2D` | `97BC62` | `F5F5F5` |
| Cyber Blue | `0A192F` | `64FFDA` | `CCD6F6` |

### Typography

| Element | Guidance | officecli example |
|--------|----------|-------------------|
| Slide title | 36-44pt bold | `--prop size=40 --prop bold=true` |
| Section header | 20-24pt bold | `--prop size=22 --prop bold=true` |
| Body copy | 14-18pt | `--prop size=16` |
| Caption / source | 10-12pt muted | `--prop size=11 --prop color=999999` |
| Key metric | 60-72pt accent | `--prop size=68 --prop color=E74C3C` |

### Layout rules

- Minimum slide-edge margin: **0.5 inches**
- Avoid text-only slides when a chart, image, icon, or shape can clarify the point
- Keep repeated spacing consistent; use officecli coordinates deliberately
- Prefer left-aligned body text and centered titles

---

## CJK / Korean Text Handling

> CJK 상세 규칙 → see `../references/officecli-cjk.md`

### Primary: fork binary auto-handles CJK

The cli-jaw fork includes `CjkHelper.cs` for PPTX. It auto-detects Korean/Japanese/Chinese text and applies language tags plus sane default fonts.

```bash
officecli add deck.pptx /slide[1] --type shape \
  --prop text='분기별 실적 보고서' \
  --prop x=2cm --prop y=3cm --prop width=20cm --prop height=3cm \
  --prop size=30 --prop bold=true
```

### PPTX-Specific CJK: DrawingML East Asian Fonts

PPTX uses DrawingML (`a:ea`) instead of WordprocessingML (`w:rFonts`):

```bash
# Set East Asian font on a shape
officecli set deck.pptx /slide[1]/shape[2] --prop font='Malgun Gothic'

# Japanese slide
officecli add deck.pptx /slide[2] --type shape \
  --prop text="日本語のプレゼンテーション" \
  --prop x=1cm --prop y=1cm --prop w=8cm --prop h=1.5cm
officecli set deck.pptx '/slide[2]/shape[1]' --prop font="Yu Gothic"

# Override with Noto Sans for cross-platform safety
officecli set deck.pptx /slide[1]/shape[2] --prop font='Noto Sans KR'
```

### CJK Text Overflow Check

```bash
# PPTX-specific: check for text overflow in CJK slides
officecli check deck.pptx
# CJK text often overflows due to wider character widths
```

### Additional CJK Guidance

If a deck needs stricter locale/font policy than the built-in defaults, consult `../references/officecli-cjk.md`.

---

## QA Verification Loop (MANDATORY)

**Never treat first render as final. QA is bug hunting.**

### Step 1 — machine QA

```bash
officecli validate deck.pptx
officecli view deck.pptx issues
officecli view deck.pptx text | grep -iE 'xxxx|lorem|ipsum|placeholder|TODO|click to'
officecli view deck.pptx stats
officecli check deck.pptx
```

Checklist:

- [ ] `validate` passes
- [ ] `view ... issues` has no blocking warnings
- [ ] placeholder text is gone
- [ ] slide count matches the requested scope
- [ ] `check` finds no serious layout overflow

### Step 2 — human QA

```bash
soffice --headless --convert-to pdf deck.pptx
pdftoppm -jpeg -r 150 deck.pdf slide
```

Inspect for:

- [ ] overlap / truncation
- [ ] too-tight margins
- [ ] inconsistent spacing
- [ ] low contrast
- [ ] broken CJK wrapping or fallback fonts
- [ ] misaligned charts/tables/images

### Step 3 — fix and re-verify

- [ ] fix with `officecli set`
- [ ] rerun machine QA
- [ ] rerender only the changed slide when possible
- [ ] do at least one fix-and-verify cycle before declaring done

---

## Accessibility (WCAG 2.1 AA)

> 접근성 기준 → see `../references/officecli-accessibility.md`

Presentations are where accessibility matters most — they're projected, shared, and read aloud.

```bash
officecli add deck.pptx / --type slide --prop layout=titleContent --prop title='Section Name'
officecli query deck.pptx 'picture:no-alt'
```

### Reading Order

For screen readers, the reading order = shape order (z-order) on each slide.

```bash
# View shapes in reading order
officecli get deck.pptx '/slide[1]' --depth 1 --json

# Text appears in the order a screen reader would read it
officecli view deck.pptx text

# Fix reading order: move shape to a specific position (1-based)
officecli move deck.pptx '/slide[1]/shape[3]' --index 1
# Shape 3 is now read first

# Ensure title is read before body content
officecli move deck.pptx '/slide[1]/shape[2]' --index 1
```

**Reading order rules per slide:**
1. Title/heading shapes should be first in order
2. Body content follows in logical sequence (top→bottom, left→right)
3. Decorative elements should be last (or marked as decorative)
4. Navigation elements in consistent position across slides

### Slide Titles

Every slide MUST have a title for screen reader navigation. Slides without titles are invisible landmarks.

```bash
# Create slide with explicit title
officecli add deck.pptx / --type slide --prop layout=titleContent --prop title='Key Metrics'

# Check for missing titles
officecli view deck.pptx outline
```

### Alt-Text for Shapes and Images

```bash
# Find pictures without alt-text
officecli query deck.pptx 'picture:no-alt'

# Set alt-text on images
officecli set deck.pptx '/slide[1]/picture[1]' \
  --prop alt="Bar chart showing Q4 revenue by region: East $2.1M, West $1.8M"

# Mark decorative shapes (empty alt)
officecli set deck.pptx '/slide[1]/picture[3]' --prop alt=""

# Batch alt-text remediation
officecli batch deck.pptx --commands '[
  {"command":"set","path":"/slide[1]/picture[1]","props":{"alt":"Company revenue chart for Q4 2025"}},
  {"command":"set","path":"/slide[2]/picture[1]","props":{"alt":"Team photo at annual meeting"}},
  {"command":"set","path":"/slide[3]/picture[1]","props":{"alt":""}}
]'
```

### Contrast Checking

```bash
# Inspect shape colors for contrast issues
officecli get deck.pptx '/slide[1]' --depth 2 --json
# Check font.color against fill values

# officecli check flags some contrast issues
officecli check deck.pptx --json

# Fix low-contrast text
officecli set deck.pptx '/slide[1]/shape[1]' --prop font.color=1A1A2E
officecli set deck.pptx '/slide[1]/shape[1]' --prop fill=FFFFFF
```

### Accessibility checklist

- [ ] Every slide has a real title: `officecli view deck.pptx outline`
- [ ] Picture alt text exists where required: `officecli query deck.pptx 'picture:no-alt'`
- [ ] Tab/reading order matches visual order: `officecli view deck.pptx text`
- [ ] Title is read first on each slide
- [ ] Contrast stays readable (≥ 4.5:1 normal, ≥ 3:1 large): `officecli check deck.pptx`
- [ ] Captions do not drop below 10pt
- [ ] Language metadata is correct for CJK slides
- [ ] Information not conveyed by color alone
- [ ] Charts use patterns/labels in addition to color
- [ ] Decorative images have empty alt-text (`alt=""`)

---

## Complex Programmatic Creation (pptxgenjs — Fallback)

Use `pptxgenjs` only when the deck is highly data-driven or generated at large scale.

```bash
npm install pptxgenjs
```

Good fallback cases:

- 50+ slides from structured datasets
- reusable composable slide factories
- heavy looping/branching logic before final render

Even in `pptxgenjs` flows, officecli remains the preferred finishing/QA tool for spot edits, queries, and validation.

---

## Legacy Python CLI (Fallback)

| Command | Role | Status |
|---------|------|--------|
| `python3 scripts/thumbnail.py deck.pptx out_dir/ --individual` | Slide thumbnails | Fallback |
| `python3 scripts/clean.py work/` | Orphan media scan | Fallback |
| `python3 scripts/pptx_cli.py validate deck.pptx --json` | Validation helper | Fallback |
| `python3 scripts/pptx_cli.py repair deck.pptx --json` | Structural repair dry-run | Fallback |
| `python3 scripts/pptx_cli.py open deck.pptx unpacked/` | Unpack OOXML for deep inspection | Legacy |
| `python3 scripts/pptx_cli.py save unpacked/ output_fixed.pptx` | Repack inspected OOXML | Legacy |
| `python3 scripts/pptx_cli.py search deck.pptx 'pattern' --json` | Text search helper | Fallback |

---

## Dependencies

| Tool | Why it exists | Status |
|------|---------------|--------|
| `officecli` (PATH) | Primary PPTX CLI — global install includes CJK fork | Required |
| `dotnet` | Runtime/build for officecli | Required for fork builds |
| `pptxgenjs` | Large programmatic generation | Optional fallback |
| `python3` | Utility scripts | Optional fallback |
| `soffice` | PPTX → PDF for visual QA | Optional fallback |
| `pdftoppm` | PDF → images for slide review | Optional fallback |
