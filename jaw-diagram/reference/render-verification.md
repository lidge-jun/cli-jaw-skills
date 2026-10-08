# Render Verification

Verification matches the failure it could catch. The figure's claim and fresh-reader check remain in `visual-story.md`; this file covers the produced artifact. `jaw-pdf` owns PDF creation and its final-page checks.

## VIZ-VERIFY-SCALE-01 — Choose the tier by what can fail unseen

| Deliverable | Before delivery |
|---|---|
| Inline SVG or Mermaid rendered in chat | Reread the final source, labels and evidence. The reader sees the host render. |
| Small static HTML/SVG in ordinary flow, without runtime data, libraries or export | Reread the saved source and return the artifact. |
| Computed marks, connectors based on rendered boxes, webfonts, libraries, responsive layout or controls | Apply DIAGRAM-RENDER-VERIFY-01 to the final rendered output. |
| PDF, print or paged report | Inspect the actual output pages under the chosen assurance scope; PDF mechanics and mandatory checks belong to `jaw-pdf`. |

Do not report an unrun check as passed. State the source-only scope when that is all you checked. A reported defect or a defect seen on the first render promotes every subsequent fix to render verification.

## DIAGRAM-RENDER-VERIFY-01 — Inspect the computed result

Render the final artifact, then read its screenshot or exported page. Check clipping, collisions, empty charts, runtime errors, legibility, contrast and CJK glyphs. Inspect the longest labels at narrow and wide widths appropriate to the artifact; for responsive HTML, include roughly 320px, 736px and the intended desktop width. A valid SVG viewBox or successful parser run cannot establish visible layout.

For a `diagram-file`, inspect the actual widget in the cli-jaw Web UI after saving it. A file write or fence alone does not prove its appearance. Change the primary input and observe the resulting values or marks; exercise keyboard access, focus and reset when provided. A screenshot alone does not prove interaction.

For print, read the exported pages with final content and scenario state, including table continuations, page breaks, glyphs and figure text. Follow `visual-reports.md` for report-specific inspection and `jaw-pdf` for PDF output. After a fix, render and inspect the affected result again. Report which surfaces and states you actually checked.
