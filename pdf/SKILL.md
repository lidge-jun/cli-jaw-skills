---
name: "pdf"
description: "Use when tasks involve reading, creating, editing, or reviewing PDF files. Visual layout checks via Poppler (pdftoppm). Python tools: reportlab (create), pdfplumber/pypdf (extract), nano-pdf (natural-language page editing). Also covers DOCX→PDF conversion via soffice."
---


# PDF Skill

## Workflow
1. Render PDF pages to PNGs for visual review (prefer `pdftoppm`; fall back to asking the user if Poppler is unavailable).
2. Use `reportlab` to generate new PDFs.
3. Use `pdfplumber` or `pypdf` for text extraction; these are unreliable for layout fidelity.
4. After each meaningful update, re-render and verify alignment, spacing, and legibility.

## Temp and output conventions
- Use `tmp/pdfs/` for intermediate files; delete when done.
- Write final artifacts under `output/pdf/` when working in this repo.
- Keep filenames stable and descriptive.

## Dependencies (install if missing)
Prefer `uv` for dependency management.

Python packages:
```
uv pip install reportlab pdfplumber pypdf
```
If `uv` is unavailable:
```
python3 -m pip install reportlab pdfplumber pypdf
```
System tools (for rendering):
```
# macOS (Homebrew)
brew install poppler

# Ubuntu/Debian
sudo apt-get install -y poppler-utils
```

If installation is blocked, tell the user which dependency is missing and how to install it.

## Rendering command
```
pdftoppm -png $INPUT_PDF $OUTPUT_PREFIX
```

## Quality expectations
- Consistent typography, spacing, margins, and section hierarchy.
- No rendering defects: clipped text, overlapping elements, broken tables, black squares, or unreadable glyphs.
- Charts, tables, and images: sharp, aligned, and clearly labeled.
- Use ASCII hyphens only — Unicode dashes (e.g. U+2011) cause rendering issues in some viewers.
- Citations and references: human-readable, no tool tokens or placeholders.

## Final checks
- Verify the latest PNG render shows zero visual defects before delivery.
- Confirm headers/footers, page numbering, and section transitions.
- Clean up or organize intermediate files after approval.
