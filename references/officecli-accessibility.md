# Accessibility Reference (officecli)

Cross-format WCAG 2.1 AA checklist for Office documents.
Format-specific accessibility commands live in each format's SKILL.md.

---

## Standards

| Standard | Scope | Key Requirement |
|----------|-------|-----------------|
| WCAG 2.1 AA | Web + Docs | Perceivable, Operable, Understandable, Robust |
| Section 508 | US Federal | Electronic docs must be accessible |
| EN 301 549 | EU | ICT accessibility (includes Office docs) |
| PDF/UA | PDF output | Tagged PDF structure |

---

## Color Contrast

WCAG 2.1 AA minimum contrast ratios:

| Text Type | Min Ratio | Example |
|-----------|-----------|---------|
| Normal text (< 18pt) | **4.5:1** | Body copy, captions |
| Large text (≥ 18pt or ≥ 14pt bold) | **3:1** | Headings, titles |
| Non-text UI elements | **3:1** | Icons, borders, charts |

### Common Problematic Combinations

| Foreground | Background | Ratio | Verdict |
|-----------|------------|-------|---------|
| `#777777` (gray) | `#FFFFFF` (white) | 4.48:1 | ❌ Fail (normal text) |
| `#767676` (gray) | `#FFFFFF` (white) | 4.54:1 | ✅ Pass (normal text) |
| `#FF0000` (red) | `#00FF00` (green) | 1.0:1 | ❌ Fail (all sizes) |
| `#1A1A2E` (navy) | `#FFFFFF` (white) | 16.8:1 | ✅ Pass |

### Contrast Calculation

```
L = 0.2126 * R + 0.7152 * G + 0.0722 * B  (relative luminance)
Ratio = (L_lighter + 0.05) / (L_darker + 0.05)
```

---

## Alt-Text Quality Rubric

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

## Font Size Minimums

| Element | Min Size | Recommended |
|---------|----------|-------------|
| Body text | 12pt | 12-14pt |
| Captions | 10pt | 11-12pt |
| Footnotes | 8pt | 9-10pt |
| Slide body (PPTX) | 18pt | 20-24pt |
| Slide titles (PPTX) | 24pt | 28-36pt |

---

## Links

Links should describe their destination, not use generic phrases.

| ✅ Good | ❌ Bad |
|---------|--------|
| "View Q4 Revenue Report" | "Click here" |
| "WCAG 2.1 Guidelines" | "Read more" |
| "Download annual report (PDF, 2MB)" | "Link" |

---

## Tables

- Every table must have a header row
- Avoid merged cells (they confuse screen readers)
- Don't use tables for layout — use them for data only
- Add a table caption/title when the data needs context

---

## Pre-Delivery Checklist

### Images & Media
- [ ] All images have meaningful alt-text
- [ ] Decorative images have empty alt-text (`alt=""`)
- [ ] Charts have data summaries in alt-text
- [ ] No essential information conveyed only through images

### Color & Contrast
- [ ] Text contrast ≥ 4.5:1 (normal) / 3:1 (large)
- [ ] Information not conveyed by color alone
- [ ] Charts use patterns/labels in addition to color

### Text & Links
- [ ] Font size ≥ 12pt for body
- [ ] No text embedded in images
- [ ] Links have descriptive text (not "click here")
- [ ] Language is set correctly for spell-check

### Batch Remediation Example

```bash
officecli batch slides.pptx --commands '[
  {"command":"set","path":"/slide[1]/picture[1]","props":{"alt":"Company revenue chart for Q4 2025"}},
  {"command":"set","path":"/slide[2]/picture[1]","props":{"alt":"Team photo at annual meeting"}},
  {"command":"set","path":"/slide[3]/picture[1]","props":{"alt":""}},
]'
officecli validate slides.pptx
```

---

## officecli Accessibility Commands

| Task | Command |
|------|---------|
| Find all pictures | `officecli query file 'picture' --json` |
| Find pictures with alt | `officecli query file 'picture[alt]' --json` |
| Set alt-text | `officecli set file '/path/picture[1]' --prop alt="description"` |
| Check heading hierarchy (DOCX) | `officecli view file.docx outline` |
| Fix heading level (DOCX) | `officecli set file.docx '/body/p[5]' --prop style=Heading2` |
| Check reading order (PPTX) | `officecli view file.pptx text` |
| Fix reading order (PPTX) | `officecli move file.pptx '/slide[1]/shape[3]' --index 1` |
| Layout check (PPTX) | `officecli check file.pptx --json` |
| Contrast fix | `officecli set file '/path' --prop font.color=1A1A2E` |
| Full validation | `officecli validate file` |
