---
name: pptx
description: "PowerPoint PPTX create, read, edit, review. Triggers: PowerPoint, PPTX, presentation, slides, deck."
---

# PPTX Skill

Use this skill for PowerPoint `.pptx` creation, editing, review, and QA.
Triggers: `"PowerPoint"`, `"PPTX"`, `"presentation"`, `"slides"`, `"deck"`.

**OfficeCLI routing and consent rule:**
- First check whether `officecli` is available with `command -v officecli`.
- If installed, recommend OfficeCLI first for high-fidelity PPTX mutations, validation, query, batch/resident flows, CJK/rhwp-aware work, and Office-compatible output.
- If missing, do not auto-install. Present choices before proceeding:
  1. Install forked OfficeCLI from `https://github.com/lidge-jun/OfficeCLI` via `bash "$(npm root -g)/cli-jaw/scripts/install-officecli.sh"`.
  2. Continue with lightweight fallback tools for the current task, with limitations stated.
  3. Stop or cancel.
- Before taking a lightweight fallback path, ask the user again and state what fidelity/features may be lost.
- If the user chooses lightweight mode, save that preference to memory for future Office work.
- Use upstream/vanilla `iOfficeAI/OfficeCLI` only when the user explicitly asks for upstream behavior.

OfficeCLI is the recommended advanced backend for slide add/set/remove, validate, and query workflows.
Lightweight fallback: **pptxgenjs** for large programmatic generation (50+ data-driven slides) and **Python scripts** (`scripts/*.py`) for unpack/repair/thumbnail/cleanup when OfficeCLI is unavailable or the user chooses lightweight mode. See §3.
Do NOT use this skill for Keynote, Google Slides API automation, or image generation.

**OfficeCLI discovery rule:** use the installed CLI as the source of truth. Run `officecli --help` for workflows and `officecli help pptx ... --json` before inventing element/property names.

**Same-file execution rule:** run OfficeCLI commands against the same `.pptx` sequentially. Do not run `officecli view`, `officecli validate`, `officecli query`, or `officecli get` in parallel against one package. If a file lock occurs, stop and report the exact command and path before making a copy or retrying.

---

## 1. Quick Reference

| Task | Action |
|------|--------|
| **Format like existing deck** | `cp source.pptx target.pptx && officecli open target.pptx` — **inherit theme/layouts/masters. See §2.** |
| Read / analyze content | `view` and `get` commands (see Core Workflows) |
| Edit existing presentation | Read [editing.md](./editing.md) |
| Create from scratch | Read [creating.md](./creating.md) |
| Pitch deck (Seed / Series) | Read [officecli-pitch-deck/SKILL.md](./officecli-pitch-deck/SKILL.md) |
| Morph transition animations | Read [morph-ppt/SKILL.md](./morph-ppt/SKILL.md) |
| 3D morph effects with models | Read [morph-ppt-3d/SKILL.md](./morph-ppt-3d/SKILL.md) |
| JS programmatic fallback | Read [pptxgenjs.md](./pptxgenjs.md) |
| Color palette / typography | Read `references/design-system.md` — 20 palettes, 8 font pairings |
| Thumbnail grid / visual QA | `python3 scripts/thumbnail.py deck.pptx grid.png` |
| Unpack / repair | `python3 scripts/pptx_cli.py {open\|save\|validate\|repair}` |

**Execution model:** Run commands one at a time. Check exit code before proceeding. Non-zero = stop and fix.

---

## 2. Reference-Based Editing (Edit > Create from Scratch)

When the user says "format like X.pptx", "match existing deck style", "based on template", or provides a source file — **start from the source. Don't rebuild from scratch.**

### Workflow

1. **Copy the source**: `cp source.pptx target.pptx` — inherits theme, slide masters, layouts, fonts, colors
2. **Open** with `officecli open target.pptx` — daemon returns immediately (do NOT run as `run_in_background`)
3. **Remove slide content** but keep `/slideMaster`, `/slideLayout`, `/theme`
4. **Add new slides** using existing layouts (`--prop layout=Title+Content`) — they auto-inherit theme

### Why This Matters

Slide master and theme definitions (fonts, colors, placeholder geometry) are document-specific. Recreating them from scratch:

- Loses consistent branding across slides
- Breaks existing placeholder positions
- Takes 5-10× longer than modifying the copy

### Template Sources (priority order)

1. **User-provided source file** — first-class template
2. **`tests/fixtures/*.pptx`** — pre-built examples shipped with this skill
3. **`officecli-pitch-deck/` templates** — if pitch/investor context
4. **`morph-ppt/reference/styles/*`** — 51 curated style definitions (`bw--brutalist`, `dark--aurora-softedge`, `light--minimal-product`, etc.)
5. **`officecli create`** blank — only when nothing else applies

### Example — Inherit Existing Brand

```bash
# CORRECT: inherit theme and layouts
cp CompanyBrand.pptx Q4Report.pptx
officecli open Q4Report.pptx
officecli remove Q4Report.pptx "/slide[1]"          # remove sample slides
officecli add Q4Report.pptx / --type slide --prop layout=Title
officecli add Q4Report.pptx '/slide[1]' --type textbox --prop text="Q4 Report" --prop placeholder=title
officecli close Q4Report.pptx

# WRONG: recreate theme (loses brand)
officecli create Q4Report.pptx
# ... add all fonts, colors, masters from scratch ...
```

---

## 3. Reference Materials & Script Map

officecli covers most PPTX tasks. For design, QA, and repair, use these references + scripts.

### References (`references/`)

| File | Read when | Contains |
|------|-----------|----------|
| `references/design-system.md` | **Before picking colors/fonts** — palette + typography decision | 20 palettes (business/nature/energy/tech/warm), 8 font pairings, 4 Korean fonts |

### Deep-Dive Files (inside subskills)

These are specific reference files nested inside subskill folders. Load only the one you need. §4 lists the top-level subskill SKILL.md entry points.

| Path | Read when | Contains |
|------|-----------|----------|
| `morph-ppt/reference/decision-rules.md` | Planning framework for content-heavy decks | Pyramid Principle, SCQA, page types |
| `morph-ppt/reference/pptx-design.md` | Canvas spec, ghost position math | Canvas, fonts, spacing tokens (x=36cm ghost) |
| `morph-ppt/reference/styles/INDEX.md` | Picking a distinct visual style | 51 style definitions with spec + example |
| `morph-ppt/reference/quality-gates.md` | Phase 4–5 QA gates for morph decks | QA checklist |
| `morph-ppt/reference/officecli-pptx-min.md` | Morph-specific officecli commands | Minimal command reference |
| `pptxgenjs.md` | Programmatic generation (50+ data-driven slides) | PptxGenJS API reference |
| `recipes.md` | 3 copy-paste repair patterns | Section divider z-order, KPI overflow, timeline spacing |

### Scripts (`scripts/`) — Python OOXML Toolkit

| Script | Run when | Command |
|--------|----------|---------|
| `scripts/pptx_cli.py` | Unified Python CLI — unpack, save, validate, repair, thumbnail, search, TOC, add-slide, clean, export-pdf | `python3 scripts/pptx_cli.py {open\|save\|validate\|repair\|text\|search\|toc\|thumbnail\|export-pdf\|add-slide\|clean}` |
| `scripts/thumbnail.py` | Slide thumbnail grid or individual PNGs (visual QA) | `python3 scripts/thumbnail.py IN.pptx grid.png` or `IN.pptx out_dir/ --individual` |
| `scripts/clean.py` | Find/remove orphaned media/files from unpacked PPTX | `python3 scripts/clean.py work/ [--delete]` |
| `scripts/add_slide.py` | Add or duplicate slides on unpacked dir (legacy OOXML) | `python3 scripts/add_slide.py work/ --blank` or `--duplicate 3 --position 1` |
| `scripts/run_tests.py` | Run skill regression tests (fixtures + expected outputs) | `python3 scripts/run_tests.py` |

### Editing Escalation Ladder

When officecli can't do the job, escalate in this order:

| Level | When | Tool |
|-------|------|------|
| **L1** officecli high-level | Typical slide/shape add/set/remove | `officecli add/set/remove/query/view` |
| **L2** officecli `raw-set` | XML injection — custom animations, chart XML, theme tweaks | `officecli raw-set FILE PATH --xpath X --action A --xml ...` |
| **L3** Python script | Thumbnail generation, orphan cleanup, unified CLI ops | `python3 scripts/*.py` |
| **L4** Unpack → edit XML → repack | Morph transitions beyond officecli, custom `p:transition` XML, macro handling | `scripts/pptx_cli.py open` → edit `work/ppt/slides/*.xml` → `save` |
| **L5** pptxgenjs | 50+ slides from datasets, composable factories, heavy loop logic | `npm install pptxgenjs` + JS pipeline |

**Escalation signals:**
- officecli shows **"silently ignored"** or unsupported prop → **L2**
- Need **morph/custom transitions** beyond high-level → **L4**
- **Bulk generation** from data (50+ slides) → **L5** (pptxgenjs)
- **Unpacked workflow** for cleanup/reorg → **L3** (`pptx_cli.py clean`)
- **Design pick** (color, font, style) → Read `references/design-system.md` + `morph-ppt/reference/styles/INDEX.md` FIRST

---

## 4. Subskill References

Load ONLY the one subskill matching your task. Do not load all of them.

| Task | Subskill | Path |
|------|----------|------|
| General PPTX | This file + recipes | [creating.md](./creating.md) / [editing.md](./editing.md) |
| Pitch deck | officecli-pitch-deck | [./officecli-pitch-deck/SKILL.md](./officecli-pitch-deck/SKILL.md) |
| Morph animations | morph-ppt | [./morph-ppt/SKILL.md](./morph-ppt/SKILL.md) |
| 3D morph | morph-ppt-3d | [./morph-ppt-3d/SKILL.md](./morph-ppt-3d/SKILL.md) |
| JS fallback | pptxgenjs | [./pptxgenjs.md](./pptxgenjs.md) |

---

## 5. Slide Design Guidance

Design is a deliverable, not optional polish. A slide deck is not a document: if the largest element plus one glance does not communicate the slide's point, the hierarchy has failed.

> **The 3-second test.** Every slide must pass it — a viewer grasps the one point in 3 seconds. Wrong chart type, bullet walls, and weak hierarchy all fail it.

Canonical owners (read for depth; this skill carries the slide-adapted essentials inline):
> - Design-direction / intent discovery, hierarchy levers → `dev-uiux-design` skill.
> - Anti-slop philosophy + render verification → `dev-frontend` skill.

### 5.1 Slide Design Read

Before styling, state: deck type, audience, the decision the audience must make, existing brand/template, and the dominant visual reference. If a `DESIGN.md` or template exists, it overrides.

### 5.2 Before starting

- **Pick a bold, content-informed color palette.** It should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **One color dominates** (60-70% visual weight), with 1-2 supporting tones and one sharp accent.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.

Reference files:
> - Full palettes + Text/Muted columns + personality map: `references/design-system.md`.
> - Slide-adapted hierarchy levers + per-slide checklist: `references/visual-hierarchy.md`.
> - Copy-paste visual-effect recipes (gradient/shadow/glow/etc.): `references/visual-effects.md`.
> - Distinct design styles: `morph-ppt/reference/styles/INDEX.md` (51 curated styles).

### 5.3 Intent Discovery for Decks

When deck direction is vague ("멋지게 만들어줘", "깔끔하게"), ask up to 4 binary/ternary questions before building. If the user names a reference product, skip to mapping via `references/design-system.md`. (Adapted from `dev-uiux-design` §1; "viewport" step dropped — slides are fixed 16:9.)

1. **Mood** — "청중에게 남길 느낌: `executive/trustworthy` · `premium/editorial` · `energetic/product-launch` · `technical/precise` · `training/clear` 중?"
2. **Density** — "한 장당 정보 밀도: `keynote sparse`(한 메시지) · `business normal`(제목+시각+짧은 근거) · `review dense`(차트/표 중심) 중?"
3. **Shape language** — "도형 언어: `sharp grid`(정밀/컨설팅) · `soft cards`(친근/제품) · `editorial bleed`(이미지/큰 타이포) · `diagrammatic`(프로세스/시스템) 중?"
4. **Reference / template** — "따라야 할 기준: `existing template/brand deck` · `product ref (Linear/Apple/Stripe)` · `industry convention` · `no reference — propose one` 중?"

Answers feed the dials below with reasoned values instead of defaults.

### 5.4 Deck Dials

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

> **"복잡" = higher DENSITY, not higher VARIANCE.** A complex brief means more data/features, not more visual tricks. "Simple" = decrease all three dials proportionally. (from `dev-uiux-design` §2)

### 5.5 16:9 Canvas, Grid & Negative Space

Standard widescreen is **33.87 × 19.05cm**. Treat it as a 12-column grid internally.

- **Edge margin ≥ 1.27cm** (0.5") on all sides.
- **Inter-block gap ≥ 0.76cm** (0.3") between cards/columns/rows — pick ONE value (0.76 or 1.27cm) and use it everywhere; mixed gaps look unfinished.
- **≥ 20% negative space per slide.** Filling every pixel reads as amateur.
- **Compose, don't web-center.** Intentional asymmetry (content left, breathing room right) reads more designed than centering everything.
- Card grids: `usable = 33.87 − 2·margin − (N−1)·gap`, then `col_width = usable / N`. Don't hand-pick x.

### 5.6 Slide Visual Hierarchy

Exactly **one** primary focal point per slide. Build the eye-path from 6 levers (full detail: `references/visual-hierarchy.md`):

1. **Size** — title ≥36pt and ≥2× body; adjacent levels differ ≥1.25×; max 4 levels/slide.
2. **Weight** — title 700-800 / labels 600 / body 400-500; never weight alone.
3. **Color** — accent on **≤2 elements per slide** (the focal object); "everything accent = nothing accent".
4. **Spacing** — whitespace = hierarchy; section gap > group gap > element gap; margins ≥1.27cm, gaps ≥0.76cm.
5. **Position** — primary message upper-left / optical center; citations/notes/page-no in stable periphery.
6. **Density** — alternate dense/sparse slides; never two dense slides back-to-back (except appendix).

### 5.7 Palette, Contrast & Projection

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

- **Accent discipline:** one accent only; apply it to **≤2 elements per slide**. If every card/icon is accent-colored, the focal point is lost.
- Full 20-palette set with Text/Muted + a product-personality → palette map: `references/design-system.md`.

### 5.8 Layout Patterns by Slide Job

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
officecli add deck.pptx '/slide[1]' --type shape --prop geometry=roundRect \
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

# Connectors / arrows between shapes.
# Endpoints use from=/to= (shape index or /slide[N]/shape[M]). startShape/endShape are READ-ONLY.
# Every flow connector needs an arrowhead. shape=elbow is the canonical right-angle form.
officecli add deck.pptx '/slide[2]' --type connector \
  --prop from=1 --prop to=2 --prop shape=elbow --prop color=#4472C4 --prop tailEnd=arrow

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

### 5.9 Typography for Slides

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

| Element | Size | Min shape height |
|---------|------|------------------|
| Slide title | 36-44pt bold (≥2× body) | ≥ 2cm |
| Section header | 20-24pt bold | ≥ 1.2cm |
| Body text | **18-22pt (min 18pt)** | ≥ 1cm |
| Caption / source | 10-12pt muted | ≥ 0.6cm |
| Key metric | 60-72pt bold, accent color | — |

**Body floor is 18pt** for audience-facing prose. Four exceptions may go below 18pt: chart axis labels, legends, footer/page number, and ≤5-word KPI sublabels (e.g. "Active users"). Descriptive sentences must be ≥18pt. Rule of thumb: min shape height ≈ font_pt × 0.05cm. Overflow → cut text or split slides, **never shrink font**; if cards won't fit, drop cards.

**Line breaks (manual `text-wrap: balance`).** Break titles/subtitles between thought-units so no line ends with a 1-word (EN) orphan; keep line lengths balanced. **Korean: last line ≥4 chars (2 syllable blocks)** — never leave "다." / "화." alone. Body line length ~45-65 chars. (from `dev-uiux-design` typography-line-breaks)

All content slides (not cover/closing) should have speaker notes.

### 5.10 Chart-Choice Decision Table

Wrong chart type kills the 3-second test:

| Data shape | Use | Avoid |
|---|---|---|
| Category comparison (A vs B vs C) | `column` (vertical) / `bar` (≥6 cats, horizontal) | pie (slices merge), line (no time axis) |
| Time series, 1-3 series | `line` | area (occlusion), bar (implies discrete) |
| Part-of-whole, 2-5 slices | `pie` / `doughnut` | pie with 8+ slices (unreadable) |
| Correlation / distribution | `scatter` | line (implies ordering) |
| Many categories × metrics, dense | stacked `column` or heatmap | one chart per metric — consolidate |
| KPI snapshot (single big number) | **Large-text shape** (60-72pt + ≤5-word sublabel), NOT a chart | gauge chart, tiny bar |

Rule of thumb: if >3 series and >8 categories, split into two charts or switch to a table.

### 5.11 Content-to-Layout Guide

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

A 10-slide deck needs ≥4 distinct layout types (hero / split / grid / data-viz) — never repeat one layout.

### 5.12 Image / Screenshot / Logo Treatment

Read the image first; choose treatment from what you see, not from the filename.
- **Full-bleed photo** → size to COVER the region (crop edges), no border.
- **Screenshot / diagram / logo** → size to FIT (never crop content); place on a contrasting fill rectangle, don't let it float on white.
- **Text over a photo** → never raw; put it on a card or lay a dark scrim (~50-60% opacity) between.
- Never stretch (distort aspect ratio). Prefer user/brand assets; no emoji or self-drawn art unless asked.

### 5.13 Visual Motif Commitment

Pick ONE distinctive element (rounded image frames, section numbers in filled circles, single-side border band, diagonal accent strips) and carry it to every slide. **Declare it in your build plan first** (`## Motif: numbered circles in brand color`). A secondary motif is fine only if it doesn't compete. Styling one slide richly and leaving the rest plain reads as abandoned.

### 5.14 Copy Reads Human

Titles orient on content, not punchline. No "It's not X. It's Y.", no manufactured tension, no faux-insight ("The magic moment"), no one-word drama ("Momentum."). Cut hype adjectives (seamless, robust, game-changing, Elevate, Next-Gen) — let the number carry it. Pick ONE title grammar (all noun-phrases OR all action statements, never mixed) and hold it throughout.

### 5.15 Slide-Specific Anti-Slop

Each = pattern → one-line fix. (Slide-adapted from `dev-frontend` §5 + built-in AI-tells.)

1. **Three Icon Columns** — centered title + 3 equal icon/text cols → one dominant block + 2 unequal supports.
2. **Bullet Wall** — title + 5-9 bullets → split to one idea/slide or convert to process/KPI/comparison.
3. **Gradient Everywhere** — gradients on everything → one gradient surface max, else solid + whitespace.
4. **Accent Underline Title** — thin colored rule under every title → hierarchy via whitespace/band/scale.
5. **Left-Border Card Stripe** — rounded card + colored vertical bar → solid fill / top accent band / spacing.
6. **Template Blue Corporate** — default blue + Calibri + white → topic palette + explicit font pair.
7. **Everything Centered** — all text/cards centered → center only cover titles + hero numerals; left-align reading text.
8. **Data Confetti** — decorative/fake KPIs to fill space → whitespace + hierarchy; never invent evidence.
9. **Tiny Table Cram** — spreadsheet at 8pt → big-type decision + 3-5 key rows; full table to appendix.
10. **Directionless Flow** — boxes + plain lines → named shapes, `shape=elbow` connectors, arrowheads on every flow.
11. **Image Float** — logo/screenshot floating on white / raw text on photo → fit on backing shape; scrim/card for text-over-photo.
12. **Motif Abandonment** — one designed cover, plain rest → declare one motif, apply across cover/divider/content/close.

**STRICT bans:** emoji as iconography (feature/card/section icons) — use a shape or real icon asset; purple gradient on white; `FFFFFF` bg + `000000` text (use off-black `0A0A0A`).

---

## 5A. Delivery Standards ("not done" if violated)

### 5A.1 All-decks requirements

- **One idea per slide.** If a slide needs a second title to explain its scope, split it.
- **Explicit type hierarchy** — set sizes on every text shape; don't rely on theme defaults.
- **Two fonts max, one palette** — one heading + one body; a third *display* face only for cover title / big numerals. One dominant color (60-70%) + one support + one accent; never 4+ in body.
- **Every slide carries an informing visual** — shape, chart, icon, or meaningful gradient band, not decoration. Exceptions: literal quote slides, code blocks, one summary-table slide.
- **Less is more** — don't pad with decorative stats/icons/filler ("data slop"). Fix an empty slide with layout + whitespace, not invented content.
- **Speaker notes on every content slide.**
- **Preserve existing templates** — when a file has a theme/masters, match them.

### 5A.2 Visual delivery floor (every deck, checked at QA)

- **No placeholder tokens rendered** — `{{name}}`, `$fy$24`, `<TODO>`, `lorem`, `xxxx`, empty `()`/`[]`.
- **No off-edge overflow / clipped text** — grow the box or shorten the value, never trim content to fit.
- **Cover carries orienting elements** — title + subtitle + presenter/client + date + brand band.
- **Contrast** — on any fill brightness <30% (`1E2761`, `36454F`, deep forest/berry), every body run, card body, chart series, and icon must be `FFFFFF` or brightness >80%. Mid-gray (`6B7B8D` ≈44%) vanishes on projection. Spot-check via `view html` after any dark-fill pass.

If any fails, STOP and fix before declaring done.

---

## 6. Creation Workflow

**Step 0 — Title sequence first (plan, don't build yet).** Before creating any slide, write the full ordered list of slide titles. If someone reading ONLY the titles can't follow the argument, fix the arc now — cheaper in a list than after 14 slides. Pick ONE title grammar and hold it (see §5.14). Also declare the motif (§5.13) and dials (§5.4) here.

```bash
# 1. ASCII 파일명으로 /tmp/ 에서 작업 (한국어 파일명은 resident 깨짐)
officecli create /tmp/deck_work.pptx --type pptx

# 2. add slide (parent is '/', the presentation root) → set background → add shapes/textboxes/charts
officecli add /tmp/deck_work.pptx / --type slide
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

## 7. QA — Delivery Gate (Required)

**Assume there are problems.** First render is almost never correct. Zero issues found = you weren't looking hard enough. **Any gate failure = REJECT, do not deliver.** Done = every gate PASS **and** Gate 3 loop converged.

### Gate 1 — schema
`officecli validate "<file>"`. Any schema error → REJECT and fix. (Modern MS chart-extension XML can fail schema yet render in LibreOffice — report as "schema failed, LibreOffice render succeeded".)

### Gate 2 — overflow / format / structure
`officecli view "<file>" issues`. Any issue (`[O1]`, `[C1]`, `[S1]`, …) → REJECT, fix, re-run until clean.

### Gate 2b — leftover placeholders
`officecli view "<file>" text`, then scan for `xxxx`, `lorem`/`ipsum`, `<TODO>`, `placeholder`, "click to", empty `()`/`[]`. Any hit → REJECT.

```bash
officecli validate output.pptx
officecli view output.pptx issues
officecli view output.pptx text | grep -iE 'xxxx|lorem|ipsum|placeholder|TODO|click to'
officecli view output.pptx stats
```

### Gate 3 — Visual audit (MANDATORY)

```bash
officecli view output.pptx html --browser

# Thumbnail grid for quick scan: wrapper uses LibreOffice -> pdftoppm -> Pillow
python3 scripts/thumbnail.py output.pptx grid.png
```

LibreOffice render is visual evidence, not a guarantee that PowerPoint for Mac renders identically.

**USE A FRESH SUBAGENT** — even for 2-3 slides. The builder is biased toward "looks fine"; a separate pair of eyes is more critical. Hand it the screenshots + this checklist with adversarial framing.

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
- Low-contrast / dark-on-dark text or icons (fill <30% with text <80%)
- Image treatment: stretched photo, raw text on photo, cropped logo, image floating on white
- Missing arrowheads on flow connectors
- Leftover placeholder content
- Text boxes too narrow causing excessive wrapping
- Title line-break: last line is a single word (EN) or ≤3 chars (KO)

For each slide, list issues or areas of concern, even if minor.
Report ALL issues found.
```

### Fix-verify loop (mandatory, max 3 cycles)

Fix with `officecli set` → re-run Gate 3 → repeat until zero new issues; one fix often surfaces another. After 3 rounds without convergence, STOP and report `slide N: <issue> — attempted: <fixes> — likely root: <template|design-conflict|ambiguous>` for the user to decide. **Do not declare success until a fix-verify cycle finds zero new issues.**

---

## 8. Prerequisite Check

```bash
# Required
python3 -c "import pptx" || echo "MISSING: pip install python-pptx"

# LibreOffice: check only; ask before installing when PDF/thumbnail output is needed.
which soffice >/dev/null 2>&1 || echo "ASK USER: LibreOffice is not installed; install it for PDF conversion/thumbnails or skip that output."

# OfficeCLI: check only; do not auto-install from a skill.
if ! command -v officecli >/dev/null 2>&1; then
  echo "ASK USER: install forked OfficeCLI from https://github.com/lidge-jun/OfficeCLI, continue lightweight, or stop."
  echo "Install command after approval: bash \"\$(npm root -g)/cli-jaw/scripts/install-officecli.sh\""
fi
```

## 9. Tool Discovery

Always inspect help before inventing properties:

```bash
officecli --help
officecli help pptx
officecli help pptx add slide --json       # exact property list
officecli help pptx add shape --json
officecli help pptx set slide --json
officecli help pptx set shape --json
officecli view --help                      # all view modes
officecli help pptx query
```

---

## 10. Core Workflows

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
officecli open slides.pptx      # returns IMMEDIATELY; daemon in bg
officecli add slides.pptx ...
officecli set slides.pptx ...
officecli close slides.pptx     # always close explicitly
```

> **Do NOT run `officecli open` as a background shell job.** It returns immediately and the daemon lives in the background automatically. Running it as a monitored shell creates zombies and file locks.

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

> **Error decoding:** `'X' is an invalid start of a value` = shell syntax leaked into JSON. Use heredoc `cat <<'EOF' | officecli batch FILE` with single-quoted delimiter.

---

## 11. Common Pitfalls

| Pitfall | Correct Approach |
|---------|-----------------|
| Unquoted `[N]` in zsh | Always quote: `"/slide[1]"` or `'/slide[1]'` |
| `--name "foo"` | Use `--prop name="foo"` — all attributes through `--prop` |
| Guessing property names | Run `officecli help pptx set shape --json` for exact names |
| Hex colors with `#` | Use `FF0000` not `#FF0000` |
| `$` in `--prop text=` | Use single quotes: `'$15M'` |
| `view text` misses tables | Use `view annotated` for full text |
| Chart series after creation | Cannot add — delete and recreate |
| Korean filename + resident | CJK causes resident UTF-8 corruption. Use ASCII, then copy. If stuck: `pkill -9 -f "resident-serve"` |
| Resident zombie | `pkill -9 -f "resident-serve"`, wait 1s, retry |
| **Recreating theme/masters that exist** | `cp source.pptx target.pptx` first. Keep `/slideMaster`, `/slideLayout`, `/theme`. See §2 |
| **`officecli open` as background shell** | Run foreground — returns immediately, daemon runs in bg automatically. Background shell spawn creates zombies |
| **Batch JSON `'X' is an invalid start of a value`** | Shell syntax leaked. Use heredoc: `cat <<'EOF' \| officecli batch FILE.pptx` |
| **Picking colors/fonts blindly** | Read `references/design-system.md` (20 palettes, 8 font pairings) BEFORE picking. See §3 |
| **Using old `officecli pptx set shape` syntax** | Use `officecli help pptx set shape --json`; schema help now lives under `officecli help <format> ...` |

---

## 12. Pre-Delivery Checklist

- [ ] Speaker notes on all content slides
- [ ] At least one transition style applied
- [ ] Alt text on all pictures: `officecli query deck.pptx 'picture:no-alt'`
- [ ] Layout variety >= 3 types across slides
- [ ] No overflow: `y + height <= 19.05cm`, `x + width <= 33.87cm`
- [ ] No placeholder text remaining
- [ ] Body text >= 16pt everywhere
- [ ] Chart titles contain actual values (no `TBD`, `()`)

---

## 13. Quick Recipes

See [recipes.md](./recipes.md) for 3 copy-paste repair patterns:
1. Section Divider z-order fix
2. KPI Box overflow (font size formula)
3. Timeline spacing (uniform distance formula)

---

## 14. Anti-Patterns

- Never use example data from subskill files (FitPulse, LearnFlow, etc.)
- Never leave placeholder text: `lorem`, `ipsum`, `XXXX`, `TODO`
- Every slide must have a title (accessibility)
- Speaker notes on all content slides
- Max 2 font families per deck
- `Malgun Gothic` as sole font = rejected
- `view issues` "(untitled)" for blank-layout is expected, not a defect
- **Recreating theme/masters instead of copying source**: When user provides a reference deck, `cp` first. See §2
- **Ignoring reference materials**: If design-pick fails, READ `references/design-system.md` + `morph-ppt/reference/styles/INDEX.md` (§3) BEFORE defaulting to generic blue + Arial

---

## 15. CJK / Korean

cli-jaw fork auto-detects Korean and applies language tags + default fonts.

```bash
officecli validate deck.pptx
officecli view deck.pptx issues
officecli view deck.pptx stats
```

---

## 16. Accessibility (WCAG 2.1 AA)

- Every slide has a title: `officecli view deck.pptx outline`
- Alt text on images: `officecli query deck.pptx 'picture:no-alt'`
- Reading order = shape order (title first)
- Contrast >= 4.5:1 normal, >= 3:1 large
- Information not conveyed by color alone

---

## 17. Dependencies

| Tool | Purpose | Status |
|------|---------|--------|
| `officecli` (PATH) | Recommended advanced PPTX backend; fork source is `https://github.com/lidge-jun/OfficeCLI` | Optional; ask before install |
| `pptxgenjs` | Large programmatic generation (L5) | Optional |
| `python3` | Scripts (`scripts/*.py`) for L3 | Required for L3/L4 |
| `soffice` | PDF conversion for QA | Optional |
