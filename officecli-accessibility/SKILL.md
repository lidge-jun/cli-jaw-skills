---
name: officecli-accessibility
description: "Accessibility checks and remediation for Office documents. Alt-text validation, color contrast, reading order, heading hierarchy, and WCAG 2.1 AA compliance."
metadata:
  openclaw:
    emoji: "♿"
    requires: "officecli (>= 1.0.28)"
---

# officecli-accessibility

Overlay skill for OfficeCLI that ensures documents meet accessibility standards.
Use this skill for pre-delivery QA, compliance audits, or when creating documents for public distribution.

---

## When to Use

- Creating documents for public distribution or government compliance
- Compliance requirement: WCAG 2.1 AA, Section 508, EN 301 549, PDF/UA
- User requests "accessible" or "ADA-compliant" document
- QA review before final delivery to clients

---

## Standards Reference

| Standard | Scope | Key Requirement |
|----------|-------|-----------------|
| WCAG 2.1 AA | Web + Docs | Perceivable, Operable, Understandable, Robust |
| Section 508 | US Federal | Electronic docs must be accessible |
| EN 301 549 | EU | ICT accessibility (includes Office docs) |
| PDF/UA | PDF output | Tagged PDF structure |

---

## 1. Alt-Text Audit

Every image, chart, and non-text element needs alternative text for screen readers.

### Find Images Without Alt-Text

```bash
# PPTX: query for pictures, check alt attribute
officecli query slides.pptx 'picture' --json
# Look for entries where "alt" is empty or missing

# DOCX: find all pictures
officecli query report.docx 'picture' --json

# PPTX: filter to only pictures with alt-text present
officecli query slides.pptx 'picture[alt]' --json
# Compare count with total pictures to find gaps
```

### Set Alt-Text

```bash
# Add descriptive alt-text to a picture
officecli set slides.pptx '/slide[1]/picture[1]' \
  --prop alt="Bar chart showing Q4 revenue by region: East $2.1M, West $1.8M, Central $1.5M"

# Add alt-text to a shape used as a visual element
officecli set slides.pptx '/slide[1]/shape[2]' \
  --prop alt="Company logo - Acme Corp"

# Mark decorative images (empty alt = explicitly decorative)
officecli set slides.pptx '/slide[1]/picture[3]' --prop alt=""
```

### Alt-Text Quality Guidelines

| ✅ Good Alt-Text | ❌ Bad Alt-Text |
|------------------|----------------|
| "Bar chart showing Q4 revenue by region" | "chart" |
| "Photo of team at 2026 annual meeting" | "image1.jpg" |
| "Logo of Acme Corporation" | "logo" |
| "" (empty — decorative only) | "decorative image" |

**Rules:**
- Describe the **purpose**, not just appearance
- Include data summaries for charts/graphs
- Keep under 125 characters when possible
- Use empty string `""` only for truly decorative elements

---

## 2. Color Contrast

WCAG 2.1 AA minimum contrast ratios:

| Text Type | Min Ratio | Example |
|-----------|-----------|---------|
| Normal text (< 18pt) | **4.5:1** | Body copy, captions |
| Large text (≥ 18pt or ≥ 14pt bold) | **3:1** | Headings, titles |
| Non-text UI elements | **3:1** | Icons, borders, charts |

### Inspect Colors

```bash
# PPTX: get shape properties including colors
officecli get slides.pptx '/slide[1]' --depth 2 --json
# Check font.color and fill values for each shape

# DOCX: inspect run formatting
officecli get report.docx '/body/p[1]/r[1]' --json
# Look at font.color and background

# XLSX: inspect cell colors
officecli get data.xlsx '/Sheet1/A1' --json
# Check font.color and fill properties
```

### Common Problematic Combinations

| Foreground | Background | Ratio | Verdict |
|-----------|------------|-------|---------|
| `#777777` (gray) | `#FFFFFF` (white) | 4.48:1 | ❌ Fail (normal text) |
| `#767676` (gray) | `#FFFFFF` (white) | 4.54:1 | ✅ Pass (normal text) |
| `#FF0000` (red) | `#00FF00` (green) | 1.0:1 | ❌ Fail (all sizes) |
| `#1A1A2E` (navy) | `#FFFFFF` (white) | 16.8:1 | ✅ Pass |
| `#FFFFFF` (white) | `#2C3E50` (dark) | 11.4:1 | ✅ Pass |

### Fix Contrast Issues

```bash
# Change low-contrast text to a darker color
officecli set slides.pptx '/slide[1]/shape[1]' --prop font.color=1A1A2E

# Change background to improve contrast
officecli set slides.pptx '/slide[1]/shape[1]' --prop fill=FFFFFF

# DOCX: fix light gray text
officecli set report.docx '/body/p[3]/r[1]' --prop font.color=333333
```

### Contrast Calculation Formula

```
L = 0.2126 * R + 0.7152 * G + 0.0722 * B  (relative luminance)
Ratio = (L_lighter + 0.05) / (L_darker + 0.05)
```

Use an external contrast checker tool (e.g., WebAIM) for precise calculations.
officecli `check` command flags some contrast issues for PPTX documents:

```bash
officecli check slides.pptx --json
```

---

## 3. Reading Order

For screen readers, the reading order in PowerPoint = the shape order (z-order) on each slide.

### Check Current Reading Order

```bash
# View shapes in reading order (output order = tab/read order)
officecli get slides.pptx '/slide[1]' --depth 1 --json
# Shapes are listed in their current reading order

# Quick text-order view
officecli view slides.pptx text
# Text appears in the order a screen reader would read it
```

### Fix Reading Order

```bash
# Move a shape to a specific reading-order position (1-based index)
officecli move slides.pptx '/slide[1]/shape[3]' --index 1
# Shape 3 is now read first

# Example: ensure title is read before body content
officecli move slides.pptx '/slide[1]/shape[2]' --index 1
```

### Reading Order Checklist per Slide

1. Title/heading shapes should be first in order
2. Body content follows in logical sequence (top→bottom, left→right)
3. Decorative elements should be last (or marked as decorative)
4. Navigation elements should be in consistent position across slides

---

## 4. Document Structure (DOCX)

### Heading Hierarchy

Headings must follow a logical hierarchy. Never skip levels.

| ✅ Correct | ❌ Incorrect |
|-----------|-------------|
| H1 → H2 → H3 | H1 → H3 (skipped H2) |
| H1 → H2 → H2 → H3 | H2 → H1 (inverted) |
| H1 → H2 → H3 → H2 | H1 → H4 (skipped 2 levels) |

### Check Heading Structure

```bash
# Find all heading paragraphs
officecli query report.docx 'paragraph[style~=Heading]' --json

# View document outline (shows heading hierarchy)
officecli view report.docx outline

# Quick check: heading levels should increment by 1
officecli view report.docx outline | grep -E 'H[1-6]'
```

### Fix Heading Levels

```bash
# Change a paragraph's heading style
officecli set report.docx '/body/p[5]' --prop style=Heading2

# Demote Heading1 to Heading2
officecli set report.docx '/body/p[3]' --prop style=Heading2
```

---

## 5. Tables

### Table Headers

Tables must have a designated header row for screen readers.

```bash
# DOCX: check table structure
officecli get report.docx '/body/tbl[1]' --depth 2 --json
# Verify first row is marked as header

# XLSX: check if header row exists
officecli get data.xlsx '/Sheet1' --depth 1 --json

# PPTX: check table structure
officecli get slides.pptx '/slide[1]/table[1]' --depth 2 --json
```

### Table Accessibility Rules

- Every table must have a header row
- Avoid merged cells (they confuse screen readers)
- Don't use tables for layout — use them for data only
- Add a table caption/title when the data needs context

---

## 6. Links

### Check Link Text

```bash
# DOCX: find all hyperlinks
officecli query report.docx 'paragraph > run[link]' --json
# Verify link text is descriptive

# Check for generic link text
officecli view report.docx text | grep -iE 'click here|read more|learn more|here'
```

### Fix Link Text

Links should describe their destination, not use generic phrases.

| ✅ Good | ❌ Bad |
|---------|--------|
| "View Q4 Revenue Report" | "Click here" |
| "WCAG 2.1 Guidelines" | "Read more" |
| "Download annual report (PDF, 2MB)" | "Link" |

---

## 7. Font Size and Readability

### Minimum Sizes

| Element | Min Size | Recommended |
|---------|----------|-------------|
| Body text | 12pt | 12-14pt |
| Captions | 10pt | 11-12pt |
| Footnotes | 8pt | 9-10pt |
| Slide body | 18pt | 20-24pt |
| Slide titles | 24pt | 28-36pt |

### Check Font Sizes

```bash
# DOCX: find small text
officecli query report.docx 'paragraph > run[size<=10pt]' --json

# PPTX: check shape text sizes
officecli get slides.pptx '/slide[1]' --depth 2 --json
```

---

## Pre-Delivery Accessibility Checklist

Run this checklist before delivering any document:

### Images & Media
- [ ] All images have meaningful alt-text: `officecli query file 'picture' --json`
- [ ] Decorative images have empty alt-text (`alt=""`)
- [ ] Charts have data summaries in alt-text
- [ ] No essential information conveyed only through images

### Color & Contrast
- [ ] Text contrast ≥ 4.5:1 (normal) / 3:1 (large): `officecli check file.pptx`
- [ ] Information not conveyed by color alone
- [ ] Charts use patterns/labels in addition to color

### Structure (DOCX)
- [ ] Heading hierarchy is correct (no skips): `officecli view file.docx outline`
- [ ] Lists use proper list styles (not manual bullets)
- [ ] Tables have header rows
- [ ] No empty paragraphs used for spacing

### Reading Order (PPTX)
- [ ] Tab order matches visual reading order: `officecli view file.pptx text`
- [ ] Title is read first on each slide
- [ ] Content follows logical flow

### Text & Links
- [ ] Font size ≥ 12pt for body: `officecli query file.docx 'paragraph > run[size<=10pt]'`
- [ ] No text embedded in images
- [ ] Links have descriptive text (not "click here")
- [ ] Language is set correctly for spell-check

### Validation
- [ ] `officecli validate file` passes with no errors
- [ ] `officecli check file.pptx` reports no critical issues

---

## Batch Accessibility Fixes

For bulk remediation across an entire presentation:

```bash
# Example: set alt-text for multiple pictures in one batch
officecli batch slides.pptx --commands '[
  {"command":"set","path":"/slide[1]/picture[1]","props":{"alt":"Company revenue chart for Q4 2025"}},
  {"command":"set","path":"/slide[2]/picture[1]","props":{"alt":"Team photo at annual meeting"}},
  {"command":"set","path":"/slide[3]/picture[1]","props":{"alt":"Product roadmap timeline diagram"}},
  {"command":"set","path":"/slide[4]/picture[1]","props":{"alt":""}}
]'

# Validate after fixes
officecli validate slides.pptx
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Find all pictures | `officecli query file 'picture' --json` |
| Find pictures with alt | `officecli query file 'picture[alt]' --json` |
| Set alt-text | `officecli set file '/slide[1]/picture[1]' --prop alt="description"` |
| Check reading order | `officecli view file.pptx text` |
| Fix reading order | `officecli move file.pptx '/slide[1]/shape[3]' --index 1` |
| Check heading hierarchy | `officecli view file.docx outline` |
| Fix heading level | `officecli set file.docx '/body/p[5]' --prop style=Heading2` |
| Layout issues (PPTX) | `officecli check file.pptx --json` |
| Full validation | `officecli validate file` |
