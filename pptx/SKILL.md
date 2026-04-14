---
name: pptx
description: "PowerPoint PPTX create, read, edit, review. Triggers: PowerPoint, PPTX, presentation, slides, deck."
---

# PPTX Skill

Use this skill for PowerPoint `.pptx` creation, editing, review, and QA.
Triggers: `"PowerPoint"`, `"PPTX"`, `"presentation"`, `"slides"`, `"deck"`.
Primary tool: **officecli** (`~/.local/bin/officecli`).
Fallback: **pptxgenjs** for large programmatic generation (50+ data-driven slides, composable factories, heavy loop/branch logic). Even in pptxgenjs flows, officecli remains the finishing/QA tool.
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

**Execution model:** Run commands one at a time. Check exit code before proceeding. Non-zero exit = stop and fix immediately. Verify after structural operations (`get` or `validate`).

---

## 2. Subskill References

Load ONLY the one subskill matching your task. Do not load all of them.

| Task | Subskill | Path |
|------|----------|------|
| Create / edit PPTX (general) | This file + recipes | [creating.md](./creating.md) / [editing.md](./editing.md) |
| Seed / Series pitch deck | officecli-pitch-deck | [./officecli-pitch-deck/SKILL.md](./officecli-pitch-deck/SKILL.md) |
| Morph transition animations | morph-ppt | [./morph-ppt/SKILL.md](./morph-ppt/SKILL.md) |
| 3D morph effects with models | morph-ppt-3d | [./morph-ppt-3d/SKILL.md](./morph-ppt-3d/SKILL.md) |
| Detailed creation recipes | creating.md | [./creating.md](./creating.md) |
| Modification / editing guides | editing.md | [./editing.md](./editing.md) |
| JS programmatic fallback | pptxgenjs | [./pptxgenjs.md](./pptxgenjs.md) |

---

## 3. Design Dials

Before creating any deck, commit to explicit design parameters.
Present to user if direction is ambiguous. Adapt dynamically based on content type.

| Dial | Range | Default | Meaning |
|------|-------|---------|---------|
| DESIGN_VARIANCE | 1-10 | 4 | 1 = symmetric grid, 10 = asymmetric art-directed |
| VISUAL_DENSITY | 1-10 | 5 | 1 = gallery whitespace, 10 = dashboard dense |
| MOTION_INTENSITY | 1-10 | 3 | 1 = static cuts, 10 = cinematic morph throughout |

**Dial presets by deck type:**

| Deck type | VARIANCE | DENSITY | MOTION |
|-----------|----------|---------|--------|
| Investor pitch | 6 | 3 | 4 |
| Internal review | 3 | 7 | 1 |
| Conference keynote | 8 | 2 | 7 |
| Workshop / training | 4 | 6 | 2 |
| Product launch | 7 | 4 | 6 |

---

## 4. Color System

### 60-30-10 Rule

- **60%** base surfaces / backgrounds
- **30%** secondary containers / cards / dividers
- **10%** accent highlights and key metrics

### Base palette constraints

- Neutral base: Zinc, Slate, Stone tones -- NOT pure white (`#FFFFFF`)
- Off-black: `#0A0A0A` or `#111111` -- NOT pure `#000000`
- Max ONE accent color per deck
- If user provides no brand colors, pick from recommended palettes below

### Recommended palettes

Choose colors that match your topic -- don't default to generic blue.

| Theme | Base (60%) | Secondary (30%) | Accent (10%) | Text | Muted |
|-------|------------|-----------------|--------------|------|-------|
| Midnight Executive | `1E2761` | `CADCFC` | `FFFFFF` | `333333` | `8899BB` |
| Slate Professional | `2C3E50` | `ECF0F1` | `E74C3C` | `333333` | `7A8A94` |
| Forest & Moss | `2C5F2D` | `97BC62` | `F5F5F5` | `2D2D2D` | `6B8E6B` |
| Cyber Blue | `0A192F` | `64FFDA` | `CCD6F6` | `333333` | `8899BB` |
| Warm Charcoal | `1A1A2E` | `E8E4DF` | `D4A574` | `333333` | `7A8A94` |
| Clean Ink | `0F172A` | `F1F5F9` | `3B82F6` | `333333` | `8899BB` |
| Coral Energy | `F96167` | `F9E795` | `2F3C7E` | `333333` | `8B7E6A` |
| Warm Terracotta | `B85042` | `E7E8D1` | `A7BEAE` | `3D2B2B` | `8C7B75` |
| Berry & Cream | `6D2E46` | `A26769` | `ECE2D0` | `3D2233` | `8C6B7A` |
| Ocean Gradient | `065A82` | `1C7293` | `21295C` | `2B3A4E` | `6B8FAA` |

Use **Text** for body copy on light backgrounds, **Muted** for captions, labels, and axis text. On dark backgrounds, use Secondary or `FFFFFF` for body text and Muted for captions.

### Dark-background contrast rule

When slide background brightness < 30% (e.g. `1E2761`, `36454F`, `000000`), ALL body text, card text, chart series colors, and icon fills MUST use white (`FFFFFF`) or near-white (brightness > 80%). NEVER use mid-gray or low-saturation tones on dark backgrounds -- contrast fails in live presentation settings.

### Banned color patterns

- Purple gradient on white background = AI slop signal
- Rainbow multi-accent = unintentional, chaotic
- `#FFFFFF` background + `#000000` text = zero personality

---

## 5. Typography

### Approved typefaces (pick one per script)

| Script | Approved typefaces |
|--------|--------------------|
| Korean | **Pretendard**, **Noto Sans KR**, **Wanted Sans** |
| English | **Geist**, **Outfit**, **Satoshi**, **Cabinet Grotesk** |

### Font pairings (safe fallbacks when approved fonts unavailable)

| Header Font | Body Font | Best For |
|-------------|-----------|----------|
| Georgia | Calibri | Formal business, finance |
| Arial Black | Arial | Bold marketing, launches |
| Trebuchet MS | Calibri | Friendly tech, startups |
| Consolas | Calibri | Developer tools, engineering |

### BANNED -- template smell

`Malgun Gothic` (sole), Inter, Roboto, Arial, Calibri (as primary), system-ui

Exception: `Malgun Gothic` acceptable ONLY as CJK fallback in `a:ea` font stack, never as primary.

### Size scale

| Element | Size | Weight |
|---------|------|--------|
| Slide title | 36-44pt | Bold |
| Section header | 20-24pt | Bold |
| Body copy | 16-20pt (min 16pt -- no exceptions) | Regular |
| Caption / source | 10-12pt | Regular, muted |
| Key metric (hero number) | 60-72pt | Bold, accent color |

**Hard Rule H4**: Body text minimum 16pt, no exceptions. If content overflows, reduce text or split slides -- never shrink font size. Exceptions allowed < 16pt: chart axis labels, legends, KPI sublabels (max 5 words), footnotes.

**Hard Rule H7**: All content slides (not cover/closing) MUST have speaker notes.

---

## 6. Layout Anti-Slop Rules

These patterns destroy presentation credibility. Avoid unconditionally.

### Banned patterns

- 3 centered cards in a row = template signal
- Every slide using identical layout = monotone deck
- Purple gradient on white = AI-generated look
- Bullet list with 6+ lines = wall of text (max 3 lines, prefer visualization)
- Title-only slide with no visual = wasted real estate
- All text center-aligned = lazy default
- Accent lines under titles = hallmark of AI-generated slides
- Text-only slides (no shapes, charts, or color blocks)

### Required patterns

- Asymmetric placement: vary element positions across slides
- Size differentiation: hero elements 3x larger than supporting
- Whitespace as design element: not every cm must be filled
- Layout variation: no two consecutive slides share the same grid
- Visual hierarchy: one clear focal point per slide
- Margin discipline: minimum 0.5 inch from all slide edges
- Left-align body text and lists; center only titles

### Slide rhythm guideline

A 10-slide deck should have at minimum 4 distinct layout types:
1. Full-bleed hero (title or key metric)
2. Split layout (text + visual, asymmetric)
3. Grid or comparison (2-3 items, varied sizes)
4. Data visualization (chart, diagram, or infographic)

### Content-to-layout quick guide

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

---

## 7. Mandatory Verification (NEVER SKIP)

After ANY PPTX creation or edit, execute this loop. First render is never final.

### Step 1 -- Machine QA

```bash
officecli validate output.pptx
officecli view output.pptx issues
officecli view output.pptx text | grep -iE 'xxxx|lorem|ipsum|placeholder|TODO|click to'
officecli view output.pptx stats
officecli check output.pptx
```

Pass criteria: `validate` passes, no blocking warnings, no placeholder text, slide count matches scope, no layout overflow.

### Step 2 -- Visual QA

```bash
officecli view output.pptx html --browser    # full-fidelity multi-slide preview
officecli view output.pptx svg --start 1 --end 1 --browser  # single-slide SVG
```

Inspect every slide for: overlap/truncation, tight margins, inconsistent spacing, low contrast, broken CJK wrapping, misaligned elements. Use subagents for fresh eyes.

**Prompt for visual QA subagent:**

```
Visually inspect these slides. Assume there are issues -- find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray on cream background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.
Report ALL issues found.
```

### Step 3 -- Fix and re-verify

Fix with `officecli set`, rerun machine QA, rerender changed slides. At least ONE fix-and-verify cycle before declaring done.

---

## 8. Tool Discovery

Always inspect help before inventing properties:

```bash
officecli --help
officecli pptx add slide       # exact property list
officecli pptx add shape
officecli pptx set slide
officecli pptx set shape
officecli pptx set shape.fill  # specific property format
officecli pptx view            # all view modes
officecli pptx query           # query selector syntax
```

---

## 9. Core Workflows

### Reading & Analyzing

```bash
# Text extraction
officecli view slides.pptx text
officecli view slides.pptx text --start 1 --end 5

# Structure overview (titles, shape counts)
officecli view slides.pptx outline

# Detailed inspection (shapes, fonts, sizes, pictures, tables)
officecli view slides.pptx annotated

# Statistics
officecli view slides.pptx stats
```

### Element Inspection (PATH syntax)

Paths are 1-based XPath: `/slide[1]`, `/shape[1]`. Always quote paths in zsh.

```bash
officecli get slides.pptx '/slide[1]' --depth 1          # all shapes on slide
officecli get slides.pptx '/slide[1]/shape[1]'            # shape details
officecli get slides.pptx '/slide[1]/chart[1]'            # chart data
officecli get slides.pptx '/slide[1]/table[1]' --depth 3  # table structure
officecli get slides.pptx "/slide[1]/placeholder[title]"  # placeholder by type
```

### CSS-like Queries

```bash
officecli query slides.pptx 'shape:contains("Revenue")'   # text search
officecli query slides.pptx "picture:no-alt"               # accessibility
officecli query slides.pptx 'shape[fill=#4472C4]'          # by fill color
officecli query slides.pptx "shape[width>=10cm]"           # by dimension
officecli query slides.pptx 'slide[2] > shape[font="Arial"]'  # scoped
```

### Visual Inspection

```bash
officecli view slides.pptx html --browser    # all slides, interactive, recommended
officecli view slides.pptx svg --start 1 --end 1 --browser  # single slide
```

SVG renders one slide only. Use `html --browser` for charts, gradients, tables.

### Resident Mode (always use)

```bash
officecli open slides.pptx      # load once into memory
officecli add slides.pptx ...   # all commands run in memory
officecli set slides.pptx ...
officecli close slides.pptx     # write once to disk
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

Batch fields: `command`, `path`, `parent`, `type`, `from`, `to`, `index`, `after`, `before`, `props`, `selector`, `mode`, `depth`, `part`, `xpath`, `action`, `xml`.

`parent` = container to add into (for `add`). `path` = element to modify (for `set`, `get`, `remove`).

Batch and resident mode are independent. Each improves performance alone; they combine.

---

## 10. Common Pitfalls

| Pitfall | Correct Approach |
|---------|-----------------|
| Unquoted `[N]` in zsh | Shell glob-expands `/slide[1]`. **Always quote**: `"/slide[1]"` or `'/slide[1]'` |
| `--name "foo"` | Use `--prop name="foo"` -- all attributes go through `--prop` |
| `/shape[myname]` | Name indexing not supported. Use numeric: `/shape[3]` |
| Guessing property names | Run `officecli pptx set shape` to see exact names |
| `\n` in shell strings | Normal text: `\\n` for newline. Code slides: single `\n`. Use heredoc for complex content |
| Hex colors with `#` | Use `FF0000` not `#FF0000` -- no hash prefix |
| Theme colors | Use `accent1`..`accent6`, `dk1`, `dk2`, `lt1`, `lt2` -- not hex |
| Forgetting alt text | Always set `--prop alt="description"` on pictures |
| `--index` is 0-based | `--index 0` = first position (paths are 1-based, index is 0-based) |
| Z-order changes | Causes shape index renumbering -- re-query with `get --depth 1` after |
| `gap`/`gapwidth` on chart add | Ignored during `add` -- set after: `officecli set ... /chart[M] --prop gap=80` |
| `$` in `--prop text=` | `--prop text="$15M"` expands `$15`. Use single quotes: `'$15M'` |
| Template text wrong size | Template shapes have baked-in fonts. Always include `size`, `font`, `color` in `set` |
| `view text` misses tables | `view text` misses table content -- use `view annotated` for full text extraction, or `officecli get deck.pptx '/slide[N]/table[M]' --json` for table text |
| Chart series after creation | Cannot add series after creation. Delete and recreate with all series |
| Modifying an open file | Close the file in PowerPoint/WPS first |
| Negative coordinates | Supported -- `x=-2cm` creates bleed effects |

---

## 11. Pre-Delivery Checklist

Before declaring a presentation complete, verify ALL items:

- [ ] **(Hard Rule H7) Speaker notes**: Run `officecli view deck.pptx annotated` and confirm every content slide (not cover/closing) has speaker notes. Missing notes on content slides is a hard delivery failure.
- [ ] **Transitions**: At least one transition style applied (fade for title, push or wipe for content).
- [ ] **Alt text**: Alt text on all pictures. Check: `officecli query deck.pptx 'picture:no-alt'`
- [ ] **Layout variety >= 3 types**: At least 3 different layout types used across slides.
- [ ] **Consecutive layout check**: No two consecutive slides share the same layout pattern.
- [ ] **Overflow formula (every slide)**: For all text boxes and shapes on every slide, confirm `y + height <= 19.05cm` (standard widescreen height) and `x + width <= 33.87cm` (standard width). If overflow, reduce font size or shorten text -- never rely on truncation.
- [ ] **Card-level per-cell overflow**: For multi-card layouts (step cards, feature grids, timeline flows), verify `y + height <= 19.05cm` per card. Use `officecli get deck.pptx '/slide[N]/shape[M]'` to check each card individually -- do not estimate based on card count, measure each one.
- [ ] **Agenda consistency**: If there is an Agenda/TOC slide, confirm all listed sections match actual slide titles and order exactly, with no missing sections.
- [ ] **H4 font compliance**: All body text, card body, bullet points, multi-column content >= 16pt. Exceptions allowed < 16pt: chart axis labels, legends, KPI sublabels (max 5 words), footnotes.

> **H4 clarification**: body text >= 16pt, no exceptions. If content overflows, reduce text or split slides -- never shrink font size. Allowed < 16pt exceptions: chart axis labels, legends, KPI sublabels (max 5 words only, e.g. "Active users", "MoM growth"; full descriptive sentences do not qualify), footnotes.

- [ ] **Chart title placeholder scan**: All chart titles must not contain `()`, `[]`, `TBD`, `XXX` or other empty placeholders. If a title has dynamic content (e.g. units like `$M`), replace with actual values during QA. Check: `officecli view slides.pptx text` then search for `"()"`.

---

## 12. Quick Recipes

High-frequency visual fix patterns. Each recipe is a directly executable repair.

### Recipe 1: Section Divider z-order fix

**Root cause:** Shapes added later sit higher in z-order. If a decorative shape (circle, rectangle) is added after the text shape, it covers the text and makes the title unreadable.

**Fix rules:**
1. **Add order = z-order**: Decorative elements (circles, color blocks) must be added first; text shapes added last -- later shapes are automatically on top.
2. **Title text y position**: recommend 7-10cm (slide height 19.05cm) to avoid overlap with top/bottom decorative elements.
3. To adjust existing shapes: use `--prop zorder=back` (decorative) or `--prop zorder=front` (text).

```bash
# Correct order: decorative first, text last
officecli add slides.pptx / --type slide --prop layout=blank --prop "background=1E2761-CADCFC-180"

# Step 1: Decorative element (large semi-transparent number as background) -- added first, bottom layer
officecli add slides.pptx /slide[N] --type shape --prop text="02" \
  --prop x=2cm --prop y=4cm --prop width=29.87cm --prop height=8cm \
  --prop font=Georgia --prop size=120 --prop bold=true \
  --prop color=FFFFFF --prop align=center --prop fill=none --prop opacity=0.15

# Step 2: Left decorative bar (optional) -- decorative, bottom layer
officecli add slides.pptx /slide[N] --type shape \
  --prop preset=rect --prop fill=FFFFFF --prop opacity=0.2 \
  --prop x=0cm --prop y=7cm --prop width=6cm --prop height=0.4cm --prop line=none

# Step 3: Title text -- added last, automatically on top, y recommend 7-10cm
officecli add slides.pptx /slide[N] --type shape --prop text="Financial Performance" \
  --prop x=2cm --prop y=7.5cm --prop width=29.87cm --prop height=3cm \
  --prop font=Georgia --prop size=40 --prop bold=true \
  --prop color=FFFFFF --prop align=center --prop fill=none

# Step 4: Subtitle (optional)
officecli add slides.pptx /slide[N] --type shape --prop text="Section 2 of 4" \
  --prop x=2cm --prop y=11cm --prop width=29.87cm --prop height=1.5cm \
  --prop font=Calibri --prop size=16 --prop color=CADCFC --prop align=center --prop fill=none
```

**Post-hoc fix (if overlap already exists):**
```bash
# Push decorative element to bottom
officecli set slides.pptx "/slide[N]/shape[1]" --prop zorder=back
# Pull text to top
officecli set slides.pptx "/slide[N]/shape[3]" --prop zorder=front
# WARNING: zorder changes cause shape index renumbering -- re-query before further operations
officecli get slides.pptx '/slide[N]' --depth 1
```

### Recipe 2: KPI Box overflow

**Root cause:** KPI number font size too large, exceeding box height or width; or box dimensions not sized for the font.

**Font size safety formula:**
- `max_font_size(pt) <= box_width_cm x char_count_divisor`
  - 1-2 characters (e.g. "94%"): `box_width_cm x 10` pt upper limit, recommend 60-72pt
  - 3-4 characters (e.g. "1.2M"): `box_width_cm x 7` pt upper limit, recommend 48-56pt
  - 5+ characters: `box_width_cm x 5` pt upper limit, recommend 36-44pt
- `box height >= font_size(cm) x 1.5` (1pt ~ 0.0353cm; 64pt ~ 2.26cm, so height >= 3.4cm)

```bash
# KPI box safe template (9cm wide box, 3-character number)
# 9cm x 3 chars -> max font ~9x7=63pt -> use 60pt
# box height >= 60pt x 0.0353cm x 1.5 ~ 3.2cm -> set 4cm (with margin)

officecli add slides.pptx /slide[N] --type shape \
  --prop text="94%" \
  --prop x=2cm --prop y=5cm \
  --prop width=9cm --prop height=4cm \
  --prop font=Georgia --prop size=60 --prop bold=true \
  --prop color=CADCFC --prop align=center --prop valign=center --prop fill=none

# sublabel (KPI description, <=5 words, allowed < 16pt)
officecli add slides.pptx /slide[N] --type shape \
  --prop text="Customer Retention" \
  --prop x=2cm --prop y=9.2cm \
  --prop width=9cm --prop height=1.5cm \
  --prop font=Calibri --prop size=13 --prop color=8899BB --prop align=center --prop fill=none
```

**Overflow fix flow:**
1. Overflow found -> reduce font size (4pt at a time, re-check)
2. Font already small enough but still overflows -> increase box `height` (adjust y accordingly)
3. Never shorten the number itself ("$1.2M" must not become "$1M" just for sizing)

```bash
# Verification
officecli view slides.pptx annotated
# Check each KPI shape: y+height <= 19.05cm
officecli get slides.pptx '/slide[N]/shape[M]'
```

### Recipe 3: Timeline spacing

**Root cause:** Setting the last node x directly to `slide_width - right_margin` creates floating-point gaps, making the last node visually "stranded" from its neighbors.

**Uniform distance formula:**
```
left_margin   = 2cm (or per design)
right_margin  = 2cm (or per design)
circle_width  = node circle width (e.g. 3cm)

# CRITICAL: usable_width must subtract circle_width, otherwise last node right edge overflows slide
usable_width = slide_width - left_margin - right_margin - circle_width
             = 33.87 - 2 - 2 - 3 = 26.87cm (standard 16:9, circle_width=3cm)

node_spacing = usable_width / (N - 1)   # N = total node count

node_x[i]   = left_margin + node_spacing x i   # i = 0, 1, ..., N-1
```

> **Why subtract circle_width?** `node_x[i]` is the circle's left x. Last node right edge = `node_x[N-1] + circle_width`. Without subtracting, right edge exceeds slide width (33.87cm), causing a P1 truncation error.

**Example (4 nodes, circle width 3cm):**
```
usable_width = 33.87 - 2 - 2 - 3 = 26.87cm
node_spacing = 26.87 / 3 ~ 8.957cm

node_x[0] = 2cm             -> right edge 5cm      OK
node_x[1] = 2 + 8.957     = 10.957cm -> right edge 13.96cm  OK
node_x[2] = 2 + 8.957x2   = 19.914cm -> right edge 22.91cm  OK
node_x[3] = 2 + 8.957x3   = 28.87cm  -> right edge 31.87cm  OK (< 33.87)
```

```bash
# 4-node uniform timeline (node_spacing ~ 8.957cm, circle width 3cm, usable_width=26.87cm)
# Horizontal baseline (from first node center to last node center)
officecli add slides.pptx /slide[N] --type connector \
  --prop x=3.5cm --prop y=10cm --prop width=27.87cm --prop height=0 \
  --prop line=CADCFC --prop lineWidth=2pt

# Node 1 (i=0) x=2cm
officecli add slides.pptx /slide[N] --type shape \
  --prop preset=ellipse --prop fill=1E2761 \
  --prop x=2cm --prop y=8.5cm --prop width=3cm --prop height=3cm --prop line=none
officecli add slides.pptx /slide[N] --type shape --prop text="Q1" \
  --prop x=2cm --prop y=8.5cm --prop width=3cm --prop height=3cm \
  --prop fill=none --prop color=FFFFFF --prop size=16 --prop bold=true \
  --prop align=center --prop valign=center

# Node 2 (i=1) x=10.96cm
officecli add slides.pptx /slide[N] --type shape \
  --prop preset=ellipse --prop fill=CADCFC \
  --prop x=10.96cm --prop y=8.5cm --prop width=3cm --prop height=3cm --prop line=none
officecli add slides.pptx /slide[N] --type shape --prop text="Q2" \
  --prop x=10.96cm --prop y=8.5cm --prop width=3cm --prop height=3cm \
  --prop fill=none --prop color=1E2761 --prop size=16 --prop bold=true \
  --prop align=center --prop valign=center

# Node 3 (i=2) x=19.91cm
officecli add slides.pptx /slide[N] --type shape \
  --prop preset=ellipse --prop fill=1E2761 \
  --prop x=19.91cm --prop y=8.5cm --prop width=3cm --prop height=3cm --prop line=none
officecli add slides.pptx /slide[N] --type shape --prop text="Q3" \
  --prop x=19.91cm --prop y=8.5cm --prop width=3cm --prop height=3cm \
  --prop fill=none --prop color=FFFFFF --prop size=16 --prop bold=true \
  --prop align=center --prop valign=center

# Node 4 (i=3) x=28.87cm
officecli add slides.pptx /slide[N] --type shape \
  --prop preset=ellipse --prop fill=CADCFC \
  --prop x=28.87cm --prop y=8.5cm --prop width=3cm --prop height=3cm --prop line=none
officecli add slides.pptx /slide[N] --type shape --prop text="Q4" \
  --prop x=28.87cm --prop y=8.5cm --prop width=3cm --prop height=3cm \
  --prop fill=none --prop color=1E2761 --prop size=16 --prop bold=true \
  --prop align=center --prop valign=center
```

**Verification:** After creating the timeline, check node x coordinates are uniformly distributed:
```bash
officecli view slides.pptx annotated
# Or check per-node
officecli get slides.pptx '/slide[N]' --depth 1
# Manually verify adjacent node x differences are consistent (tolerance +/- 0.05cm)
```

If the last node appears stranded: calculate actual spacing (`x[N-1] - x[N-2]` vs `x[1] - x[0]`), then reset last node x using the uniform spacing formula:
```bash
officecli set slides.pptx "/slide[N]/shape[M]" --prop x=28.87cm
```

---

## 13. Anti-Patterns

### Content leakage

- NEVER use example data from subskill files (FitPulse, LearnFlow, etc.)
- NEVER leave placeholder text: `lorem`, `ipsum`, `XXXX`, `TODO`, `click to add`
- All content must be real or clearly marked as `[PLACEHOLDER: description]`

### Structural

- Every slide MUST have a title (accessibility + screen reader)
- No empty slides, no duplicate slide titles
- Speaker notes on all content slides (Hard Rule H7)

### Font

- `Malgun Gothic` as sole font = rejected
- System default fonts without explicit override = rejected
- Mixed font families beyond 2 per deck = visual noise

### Known pitfalls

- `view outline` / `view issues` report "(untitled)" for blank-layout slides -- this is expected, not a defect. `view issues` reports "untitled" for blank-layout slides because custom designs use `layout=blank`; these warnings are not real issues.
- SVG/screenshot may show fewer chart series than exist -- verify with `get /slide[N]/chart[M]`
- Batch intermittent "Failed to send to resident" -- retry or close/reopen file

---

## 14. Legacy Python + pptxgenjs

### Legacy Python CLI (fallback)

| Script | Command | Purpose |
|--------|---------|---------|
| `thumbnail.py` | `python3 scripts/thumbnail.py deck.pptx out_dir/ --individual` | Slide thumbnails |
| `clean.py` | `python3 scripts/clean.py work/` | Orphan media scan |
| `pptx_cli.py validate` | `python3 scripts/pptx_cli.py validate deck.pptx --json` | Validation helper |
| `pptx_cli.py repair` | `python3 scripts/pptx_cli.py repair deck.pptx --json` | Structural repair dry-run |

### pptxgenjs (npm)

Use `pptxgenjs` (`npm install pptxgenjs`) only when:
- 50+ slides from structured datasets
- Reusable composable slide factories
- Heavy looping/branching logic before final render

Even in pptxgenjs flows, officecli remains the preferred finishing/QA tool.

---

## 15. CJK / Korean Text Handling

The cli-jaw fork includes `CjkHelper.cs` for PPTX -- auto-detects Korean/Japanese/Chinese and applies language tags plus default fonts.

```bash
officecli check deck.pptx    # catches CJK text overflow
```

For stricter locale/font policy: see `../references/officecli-cjk.md`.

---

## 16. Accessibility (WCAG 2.1 AA)

- Every slide has a real title: `officecli view deck.pptx outline`
- Alt text on all non-decorative images: `officecli query deck.pptx 'picture:no-alt'`
- Reading order matches visual order: title first, then content top-to-bottom
- Contrast >= 4.5:1 (normal text), >= 3:1 (large text)
- Information not conveyed by color alone

---

## 17. Dependencies

| Tool | Purpose | Status |
|------|---------|--------|
| `officecli` (PATH) | Primary PPTX CLI -- global install includes CJK fork | Required |
| `dotnet` | Runtime/build for officecli | Required for fork builds |
| `pptxgenjs` | Large programmatic generation | Optional fallback |
| `python3` | Utility scripts | Optional fallback |
| `soffice` | PPTX to PDF for visual QA | Optional fallback |
| `pdftoppm` | PDF to images for slide review | Optional fallback |
