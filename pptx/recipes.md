# PPTX Quick Recipes

High-frequency visual fix patterns. Each recipe is a directly executable repair.

## Recipe 1: Section Divider z-order fix

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

## Recipe 2: KPI Box overflow

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

## Recipe 3: Timeline spacing

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
