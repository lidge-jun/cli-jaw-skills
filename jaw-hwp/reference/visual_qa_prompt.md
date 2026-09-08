# Visual QA Subagent Prompt Template

Use this prompt when spawning a subagent for visual inspection of rendered HWPX pages.

---

```
Visually inspect these document pages. Assume there are issues — find them.

Look for:
- Text compressed/squeezed into fewer lines than expected (linesegarray bug)
- Line breaks not occurring where they should
- Table cell content overflowing or cut off
- Empty cells that should have content
- Style inconsistency (font size, bold, alignment mismatches)
- Page margins or headers/footers misaligned
- Missing section separators or page breaks
- Korean text truncated at cell/box boundaries
- Kinsoku violations: closing punctuation (。，) at line start
- Font fallback (wrong font rendering, DroidSans instead of intended font)
- Uneven spacing between elements
- Low-contrast text (light text on light background)

Read and analyze these images:
1. /path/to/page-01.jpg (Expected: [brief description])
2. /path/to/page-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.

CJK/Korean text specific checks:
- Korean text truncated at text box or table cell right boundary?
- Unnatural syllable-level line breaks?
- Font rendering as 맑은 고딕 / intended font (no fallback glyphs)?
- Korean-Latin mixed text spacing adequate?
- Table/chart column headers wide enough for Korean content?
```
