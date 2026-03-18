# Template Style ID Maps

Detailed charPr, paraPr, and borderFill ID definitions for each template overlay.
The base template provides IDs 0–N, and each document-type overlay adds additional IDs on top.

---

## Base Template

### charPr (Character Shape)

| ID | height | bold | Purpose |
|----|--------|------|---------|
| 0 | 1000 (10pt) | false | Default body text |
| 1 | 1000 | false | Default (hangul: 함초롬돋움) |
| 2 | 1000 | false | Default (hangul: 함초롬바탕) |
| 3 | 900 | false | Footnote (9pt) |
| 4 | 900 | false | Endnote |
| 5 | 1000 | false | Memo/comment |
| 6 | 1800 | true | Heading (18pt bold) |

### paraPr (Paragraph Shape)

| ID | align | lineSpacing | Purpose |
|----|-------|-------------|---------|
| 0 | JUSTIFY | 160% | Default justified |
| 1 | LEFT | 160% | Left-aligned |
| 2 | CENTER | 160% | Center-aligned |
| 3-19 | various | various | Numbering, TOC, list styles |

### borderFill

| ID | Description |
|----|-------------|
| 1 | No borders |
| 2 | Transparent background |

---

## Gonmun (Official Letter) — Additional Styles

### charPr

| ID | height | bold | Purpose |
|----|--------|------|---------|
| 7 | 2200 (22pt) | true | Document title |
| 8 | 1600 (16pt) | true | Signature / position title |
| 9 | 800 (8pt) | false | Contact info / department |
| 10 | 1000 (10pt) | true | Table header |

### paraPr

| ID | align | Purpose |
|----|-------|---------|
| 20 | CENTER | Title (centered) |
| 21 | JUSTIFY | Body (justified) |
| 22 | JUSTIFY | Body with indent |

### borderFill

| ID | Description |
|----|-------------|
| 3 | Solid border (black, 0.12mm) |
| 4 | Solid border + gray background |

---

## Report (Business Report) — Additional Styles

### charPr

| ID | height | bold | Purpose |
|----|--------|------|---------|
| 7 | 2000 (20pt) | true | Main title |
| 8 | 1400 (14pt) | true | Subtitle |
| 9 | 1200 (12pt) | true/underline | Section header |
| 10 | 1000 (10pt) | true | Sub-section header |
| 11 | 1000 | false | Report body text |
| 12 | 900 | false | Caption / footnote |
| 13 | 1000 | bold | Emphasis |

### paraPr

| ID | align | indent | Purpose |
|----|-------|--------|---------|
| 20 | CENTER | 0 | Title (centered) |
| 21 | JUSTIFY | 0 | Default body |
| 22 | JUSTIFY | 200 | Numbered list level 1 |
| 23 | JUSTIFY | 400 | Numbered list level 2 |
| 24-27 | JUSTIFY | various | Additional indent levels |

### borderFill

| ID | Description |
|----|-------------|
| 5 | Section header divider (thick top + thin bottom border) |

---

## Minutes (Meeting Minutes) — Additional Styles

### charPr

| ID | height | bold | Purpose |
|----|--------|------|---------|
| 7 | 1800 (18pt) | true | Title |
| 8 | 1200 (12pt) | true | Section label |
| 9 | 1000 (10pt) | true | Table header |

### paraPr

| ID | align | Purpose |
|----|-------|---------|
| 20 | CENTER | Title (centered) |
| 21 | JUSTIFY | Body (justified) |
| 22 | JUSTIFY | Body with indent |

### borderFill

| ID | Description |
|----|-------------|
| 4 | Light green background (table cells) |

---

## Proposal (Business Proposal) — Additional Styles

### charPr

| ID | height | bold | color | Purpose |
|----|--------|------|-------|---------|
| 7 | 2000 (20pt) | true | black | Main title |
| 8 | 1400 (14pt) | true | black | Subtitle |
| 9 | 1400 (14pt) | true | white | Item number badge |
| 10 | 1100 (11pt) | true | white | Sub-item number |
| 11 | 1000 (10pt) | false | black | Body text |

### paraPr

| ID | align | Purpose |
|----|-------|---------|
| 20 | CENTER | Title (centered) |
| 21 | JUSTIFY | Body (justified) |
| 22 | JUSTIFY | Body with indent |

### borderFill

| ID | Description |
|----|-------------|
| 5 | Olive green background (item number badge) |
| 6 | Light gray background (item title cell) |
| 7 | Blue background (sub-item number) |
| 8 | Bottom border only (sub-item title divider) |

---

## Unit Conversion Reference

| Conversion | Value |
|-----------|-------|
| 1pt | 100 HWPUNIT |
| 1mm | ~283.5 HWPUNIT |
| A4 width | 59528 HWPUNIT (210mm) |
| A4 height | 84186 HWPUNIT (297mm) |
| Default margin | 4252 HWPUNIT (~15mm) |
