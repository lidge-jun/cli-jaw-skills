---
name: pptx
description: "PowerPoint PPTX create, read, edit, review. Triggers: PowerPoint, PPTX, presentation, slides, deck."
---

# PPTX Skill

Use this skill for PowerPoint `.pptx` creation, editing, review, and QA.
Triggers: `"PowerPoint"`, `"PPTX"`, `"presentation"`, `"slides"`, `"deck"`.
Primary tool: **officecli** (PATH).
Fallback: **pptxgenjs** for large programmatic generation (50+ data-driven slides). Even in pptxgenjs flows, officecli remains the finishing/QA tool.
Do NOT use this skill for Keynote, Google Slides API automation, or image generation.

---

## 1. Quick Reference

| Task | Action |
|------|--------|
| Read / analyze content | `view` and `get` commands (see Core Workflows) |
| Edit existing presentation | Read [editing.md](./editing.md) |
| Create from scratch | Read [creating.md](./creating.md) |
| Pitch deck (Seed / Series) | Read [officecli-pitch-deck/SKILL.md](./officecli-pitch-deck/SKILL.md) |
| Morph transition animations | Read [morph-ppt/SKILL.md](./morph-ppt/SKILL.md) |
| 3D morph effects with models | Read [morph-ppt-3d/SKILL.md](./morph-ppt-3d/SKILL.md) |
| JS programmatic fallback | Read [pptxgenjs.md](./pptxgenjs.md) |

**Execution model:** Run commands one at a time. Check exit code before proceeding. Non-zero = stop and fix.

---

## 2. Subskill References

Load ONLY the one subskill matching your task. Do not load all of them.

| Task | Subskill | Path |
|------|----------|------|
| General PPTX | This file + recipes | [creating.md](./creating.md) / [editing.md](./editing.md) |
| Pitch deck | officecli-pitch-deck | [./officecli-pitch-deck/SKILL.md](./officecli-pitch-deck/SKILL.md) |
| Morph animations | morph-ppt | [./morph-ppt/SKILL.md](./morph-ppt/SKILL.md) |
| 3D morph | morph-ppt-3d | [./morph-ppt-3d/SKILL.md](./morph-ppt-3d/SKILL.md) |
| JS fallback | pptxgenjs | [./pptxgenjs.md](./pptxgenjs.md) |

---

## 3. Design Ideas

Don't create boring slides. Plain bullets on a white background won't impress anyone.

### Before starting

- **Pick a bold, content-informed color palette.** It should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **One color dominates** (60-70% visual weight), with 1-2 supporting tones and one sharp accent.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — colored cards, thick side borders, icon circles. Carry it across every slide.

### Design dials

Before creating, decide these three parameters. Present to user if ambiguous.

| Dial | Range | Default | Meaning |
|------|-------|---------|---------|
| DESIGN_VARIANCE | 1-10 | 4 | 1 = symmetric grid, 10 = asymmetric art-directed |
| VISUAL_DENSITY | 1-10 | 5 | 1 = gallery whitespace, 10 = dashboard dense |
| MOTION_INTENSITY | 1-10 | 3 | 1 = static cuts, 10 = cinematic morph |

Presets by deck type:

| Deck type | VARIANCE | DENSITY | MOTION |
|-----------|----------|---------|--------|
| Investor pitch | 6 | 3 | 4 |
| Internal review | 3 | 7 | 1 |
| Conference keynote | 8 | 2 | 7 |
| Workshop / training | 4 | 6 | 2 |
| Product launch | 7 | 4 | 6 |

### Recommended palettes

Choose colors that match your topic — don't default to generic blue.

| Theme | Primary | Secondary | Accent | Text | Muted |
|-------|---------|-----------|--------|------|-------|
| Midnight Executive | `1E2761` | `CADCFC` | `FFFFFF` | `333333` | `8899BB` |
| Slate Professional | `2C3E50` | `ECF0F1` | `E74C3C` | `333333` | `7A8A94` |
| Forest & Moss | `2C5F2D` | `97BC62` | `F5F5F5` | `2D2D2D` | `6B8E6B` |
| Coral Energy | `F96167` | `F9E795` | `2F3C7E` | `333333` | `8B7E6A` |
| Warm Terracotta | `B85042` | `E7E8D1` | `A7BEAE` | `3D2B2B` | `8C7B75` |
| Ocean Gradient | `065A82` | `1C7293` | `21295C` | `2B3A4E` | `6B8FAA` |
| Charcoal Minimal | `36454F` | `F2F2F2` | `212121` | `333333` | `7A8A94` |
| Berry & Cream | `6D2E46` | `A26769` | `ECE2D0` | `3D2233` | `8C6B7A` |

Use **Text** for body copy on light backgrounds, **Muted** for captions, labels, and axis text.
On dark backgrounds (brightness < 30%), all body text must be white (`FFFFFF`) or near-white — mid-gray fails in projection.
Off-black: `0A0A0A` not `000000`.

Avoid: purple gradient on white (AI slop), rainbow multi-accent, `FFFFFF` bg + `000000` text (zero personality).

### For each slide

Every slide needs a visual element — shape, chart, table, or picture. Text-only slides are forgettable.

**Layout options** (vary these — don't repeat the same one):
- Two-column: text left, visual right (or reversed)
- Icon + text rows: icon in colored shape, bold header, description
- 2x2 or 2x3 grid: content blocks with size differentiation
- Half-bleed shape: full-width colored block with content overlay
- Large stat callouts: big numbers (60-72pt) with small labels
- Comparison columns: before/after, pros/cons
- Timeline or process flow: numbered steps with arrows or connecting shapes
- Full-width quote with attribution

**Assets to use actively:**

```bash
# Shapes as content containers (cards, banners, blocks)
officecli add deck.pptx '/slide[1]' --type shape --prop shape=roundRect \
  --prop fill=1E2761 --prop x=1cm --prop y=4cm --prop w=15cm --prop h=12cm

# Tables for structured data
officecli add deck.pptx '/slide[2]' --type table \
  --prop rows=4 --prop cols=3 --prop x=1cm --prop y=3cm --prop width=24cm --prop height=6cm

# Charts for data visualization
officecli add deck.pptx '/slide[3]' --type chart \
  --prop chartType=column --prop title='Revenue' --prop 'data=Q1:12,Q2:15,Q3:18,Q4:20'

# Pictures with alt text
officecli add deck.pptx '/slide[1]' --type picture \
  --prop path=photo.png --prop x=14cm --prop y=3cm --prop width=8cm --prop height=5cm \
  --prop alt='Team photo'

# Hyperlinks on shapes
officecli set deck.pptx '/slide[1]/shape[2]' --prop link='https://example.com'

# Video / audio embedding
officecli add deck.pptx '/slide[4]' --type video --prop path=demo.mp4 \
  --prop x=2cm --prop y=3cm --prop width=20cm --prop height=12cm --prop autoplay=true

# OLE embed (Excel, Word, PDF inside a slide)
officecli add deck.pptx '/slide[5]' --type ole --prop path=data.xlsx \
  --prop x=2cm --prop y=3cm --prop width=20cm --prop height=12cm

# Connectors / arrows between shapes
officecli add deck.pptx '/slide[2]' --type connector \
  --prop startShape=1 --prop endShape=2 --prop lineColor=4472C4 --prop tailEnd=arrow

# Speaker notes on every content slide
officecli add deck.pptx '/slide[1]' --type notes --prop 'text=Key talking point here.'

# Theme colors (use instead of hex for theme-aware decks)
officecli set deck.pptx '/slide[1]/shape[1]' --prop fill=accent1
# Available: accent1..accent6, dk1, dk2, lt1, lt2, tx1, tx2, bg1, bg2

# Flip / rotate shapes
officecli set deck.pptx '/slide[1]/shape[2]' --prop flipH=true
officecli set deck.pptx '/slide[1]/shape[2]' --prop rotation=45

# Slide master / layout editing (theme customization)
officecli set deck.pptx '/slideMaster[1]/shape[2]' --prop text='Company Name'
officecli set deck.pptx '/slideLayout[2]/shape[1]' --prop fill=1E2761

# Animations (entrance, exit, emphasis)
officecli set deck.pptx '/slide[1]/shape[2]' --prop animation=fadeIn --prop delay=500

# Superscript / subscript (scientific text)
officecli add deck.pptx '/slide[1]/shape[1]' --type run \
  --prop text='H' --prop size=18
officecli add deck.pptx '/slide[1]/shape[1]' --type run \
  --prop text='2' --prop size=12 --prop subscript=true

# Template merge with data
officecli merge template.pptx output.pptx --data '{"title":"Q4 Report","revenue":"$5.1M"}'

# Watch mode (live preview with auto-refresh)
officecli watch deck.pptx --port 3000

# Slideshow settings
officecli set deck.pptx / --prop show.loop=true --prop show.narration=false
```

### Typography

Choose a font pairing with personality — don't default to Arial.

| Header Font | Body Font | Best For |
|-------------|-----------|----------|
| Georgia | Calibri | Formal business, finance |
| Arial Black | Arial | Bold marketing, launches |
| Trebuchet MS | Calibri | Friendly tech, startups |
| Consolas | Calibri | Developer tools, engineering |

Korean: **Pretendard**, **Noto Sans KR**, **Wanted Sans**.

Avoid as primary: `Malgun Gothic` (sole), Inter, Roboto, Arial, Calibri — these read as default/template.
Exception: `Malgun Gothic` acceptable as CJK fallback in `a:ea` font stack, never as primary.

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 16-20pt (min 16pt) |
| Caption / source | 10-12pt muted |
| Key metric | 60-72pt bold, accent color |

Body text minimum 16pt. Overflow → reduce text or split slides, never shrink font.
All content slides (not cover/closing) should have speaker notes.

### Slide rhythm

A 10-slide deck should have at minimum 4 distinct layout types:
1. Full-bleed hero (title or key metric)
2. Split layout (text + visual)
3. Grid or comparison (2-3 items)
4. Data visualization (chart, diagram, or infographic)

### Content-to-layout guide

| Content Type | Recommended Layout |
|---|---|
| Pricing / plan tiers | 2-3 column cards (comparison) |
| Team / people | Icon grid or 2x3 cards |
| Timeline / roadmap | Process flow with arrows / numbered steps |
| Key metrics / KPIs | Large stat callouts (3-4 big numbers) |
| Testimonials / quotes | Full-width quote with attribution |
| Feature comparison | Two-column before/after or table |
| Architecture / system | Shapes + connectors diagram |
| Financial data | Chart + summary table side-by-side |

### Avoid (common design mistakes)

- Same layout on every slide — vary columns, cards, callouts
- Center-aligned body text — left-align paragraphs; center only titles
- Insufficient size contrast — titles 36pt+ vs body 16pt
- Default blue for everything — pick colors that match the topic
- Inconsistent spacing — choose 0.3" or 0.5" gaps and stick to it
- Styling one slide and leaving the rest plain — commit fully
- Text-only slides — add shapes, charts, color blocks, pictures
- Low-contrast text or icons — both need strong contrast against background
- Accent lines under titles — hallmark of AI-generated slides; use whitespace instead
- Decorative web-UI elements (thin 1cm sidebar lines, small ornamental circles) — PPT는 프로젝터 매체, 웹앱이 아님

---

## 4. Creation Workflow

```bash
# 1. ASCII 파일명으로 /tmp/ 에서 작업 (한국어 파일명은 resident 깨짐)
officecli create /tmp/deck_work.pptx --type pptx

# 2. add slide → set background → add shapes/textboxes/charts
officecli add /tmp/deck_work.pptx /slide --type slide
officecli set /tmp/deck_work.pptx '/slide[1]' --prop background=1E2761
officecli add /tmp/deck_work.pptx '/slide[1]' --type textbox \
  --prop 'text=Title Here' --prop x=2cm --prop y=3cm --prop w=30cm --prop h=4cm \
  --prop fontsize=44 --prop bold=true --prop color=FFFFFF --prop fontFamily=Pretendard

# 3. 완료 후 resident 명시 종료
officecli close /tmp/deck_work.pptx

# 4. 최종 파일명으로 안전 복사 (한국어 OK)
python3 -c "import shutil; shutil.copy2('/tmp/deck_work.pptx', 'final.pptx')"
```

---

## 5. QA (Required)

**Assume there are problems. Your job is to find them.**

Your first render is almost never correct. Approach QA as a bug hunt, not a confirmation step. If you found zero issues on first inspection, you weren't looking hard enough.

### Step 1 — Machine QA

```bash
officecli validate output.pptx
officecli view output.pptx issues
officecli view output.pptx text | grep -iE 'xxxx|lorem|ipsum|placeholder|TODO|click to'
officecli view output.pptx stats
officecli check output.pptx
```

### Step 2 — Visual QA

```bash
officecli view output.pptx html --browser
```

**USE SUBAGENTS** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there. Subagents have fresh eyes.

**Prompt for visual QA subagent:**

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, stacked elements)
- Text overflow or cut off at box boundaries
- Elements too close (< 0.3" gaps) or nearly touching
- Uneven gaps (large empty area vs cramped)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned
- Low-contrast text or icons
- Leftover placeholder content
- Text boxes too narrow causing excessive wrapping

For each slide, list issues or areas of concern, even if minor.
Report ALL issues found.
```

### Step 3 — Fix and re-verify

Fix with `officecli set`, rerun QA. **Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## 6. Prerequisite Check

```bash
which officecli || echo "MISSING: install officecli first — see https://officecli.ai"
which soffice || echo "OPTIONAL: install LibreOffice for PDF verification"
```

## 7. Tool Discovery

Always inspect help before inventing properties:

```bash
officecli --help
officecli pptx add slide       # exact property list
officecli pptx add shape
officecli pptx set slide
officecli pptx set shape
officecli pptx view            # all view modes
officecli pptx query           # query selector syntax
```

---

## 8. Core Workflows

### Reading & Analyzing

```bash
officecli view slides.pptx text
officecli view slides.pptx text --start 1 --end 5
officecli view slides.pptx outline
officecli view slides.pptx annotated
officecli view slides.pptx stats
```

### Element Inspection (PATH syntax)

Paths are 1-based: `/slide[1]`, `/shape[1]`. Always quote paths in zsh.

```bash
officecli get slides.pptx '/slide[1]' --depth 1
officecli get slides.pptx '/slide[1]/shape[1]'
officecli get slides.pptx '/slide[1]/chart[1]'
officecli get slides.pptx '/slide[1]/table[1]' --depth 3
```

### CSS-like Queries

```bash
officecli query slides.pptx 'shape:contains("Revenue")'
officecli query slides.pptx "picture:no-alt"
officecli query slides.pptx 'shape[fill=#4472C4]'
officecli query slides.pptx "shape[width>=10cm]"
```

### Visual Inspection

```bash
officecli view slides.pptx html --browser    # recommended
officecli view slides.pptx svg --start 1 --end 1 --browser
```

### Resident Mode

```bash
officecli open slides.pptx
officecli add slides.pptx ...
officecli set slides.pptx ...
officecli close slides.pptx     # always close explicitly
```

### Batch Mode

```bash
cat <<'EOF' | officecli batch slides.pptx
[
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"text":"Title","x":"2cm","y":"2cm","width":"20cm","height":"3cm","size":"36","bold":"true"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"text":"Body","x":"2cm","y":"6cm","width":"20cm","height":"10cm","size":"16"}}
]
EOF
```

Batch supports: `add`, `set`, `get`, `query`, `remove`, `move`, `swap`, `view`, `raw`, `raw-set`, `validate`.

---

## 9. Common Pitfalls

| Pitfall | Correct Approach |
|---------|-----------------|
| Unquoted `[N]` in zsh | Always quote: `"/slide[1]"` or `'/slide[1]'` |
| `--name "foo"` | Use `--prop name="foo"` — all attributes through `--prop` |
| Guessing property names | Run `officecli pptx set shape` for exact names |
| Hex colors with `#` | Use `FF0000` not `#FF0000` |
| `$` in `--prop text=` | Use single quotes: `'$15M'` |
| `view text` misses tables | Use `view annotated` for full text |
| Chart series after creation | Cannot add — delete and recreate |
| Korean filename + resident | CJK causes resident UTF-8 corruption. Use ASCII, then copy. If stuck: `pkill -9 -f "resident-serve"` |
| Resident zombie | `pkill -9 -f "resident-serve"`, wait 1s, retry |

---

## 10. Pre-Delivery Checklist

- [ ] Speaker notes on all content slides
- [ ] At least one transition style applied
- [ ] Alt text on all pictures: `officecli query deck.pptx 'picture:no-alt'`
- [ ] Layout variety >= 3 types across slides
- [ ] No overflow: `y + height <= 19.05cm`, `x + width <= 33.87cm`
- [ ] No placeholder text remaining
- [ ] Body text >= 16pt everywhere
- [ ] Chart titles contain actual values (no `TBD`, `()`)

---

## 11. Quick Recipes

See [recipes.md](./recipes.md) for 3 copy-paste repair patterns:
1. Section Divider z-order fix
2. KPI Box overflow (font size formula)
3. Timeline spacing (uniform distance formula)

---

## 12. Anti-Patterns

- Never use example data from subskill files (FitPulse, LearnFlow, etc.)
- Never leave placeholder text: `lorem`, `ipsum`, `XXXX`, `TODO`
- Every slide must have a title (accessibility)
- Speaker notes on all content slides
- Max 2 font families per deck
- `Malgun Gothic` as sole font = rejected
- `view issues` "(untitled)" for blank-layout is expected, not a defect

---

## 13. Legacy Python + pptxgenjs

| Script | Purpose |
|--------|---------|
| `thumbnail.py` | Slide thumbnails |
| `clean.py` | Orphan media scan |
| `pptx_cli.py validate` | Validation helper |
| `pptx_cli.py repair` | Structural repair |

**pptxgenjs** (`npm install pptxgenjs`): 50+ slides from datasets, composable factories, heavy loop logic. officecli remains the finishing tool.

---

## 14. CJK / Korean

cli-jaw fork auto-detects Korean and applies language tags + default fonts.

```bash
officecli check deck.pptx    # catches CJK text overflow
```

---

## 15. Accessibility (WCAG 2.1 AA)

- Every slide has a title: `officecli view deck.pptx outline`
- Alt text on images: `officecli query deck.pptx 'picture:no-alt'`
- Reading order = shape order (title first)
- Contrast >= 4.5:1 normal, >= 3:1 large
- Information not conveyed by color alone

---

## 16. Dependencies

| Tool | Purpose | Status |
|------|---------|--------|
| `officecli` (PATH) | Primary PPTX CLI | Required |
| `pptxgenjs` | Large programmatic generation | Optional |
| `python3` | Utility scripts | Optional |
| `soffice` | PDF conversion for QA | Optional |
