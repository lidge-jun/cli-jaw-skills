# Visual Reports and Explainer Documents

Use this reference when the deliverable is a visual report or explainer document. `../../jaw-dev/references/reader-documents.md` owns the reader contract, answer-first structure and evidence anchors; this file adds visual composition. `visual-story.md` owns the figure's claim and fresh-reader check. For PDF creation and mandatory final-page checks, load `jaw-pdf`. These are authoring rules, not a report exporter or a promise of automated QA.

## Storyline and summary

**REPORT-STORY-01 — Build the story before layout.** For a decision report, write a dot-dash outline: each dot is a section claim and each dash names its supporting figure, table or dated evidence. Move from the reader's situation through the complication and answer to reasoning, plan and ask. An explainer can move from question through mechanism and evidence to implication, without a decision ask. Check that sibling sections are comparable and the headings alone convey the argument. Research, history and reference documents use the genre and ending in the reader-document owner; they do not acquire a manufactured ask.

**REPORT-STORY-02 — Headings carry content.** A decision section or exhibit title states a finding the reader could contest. Research may state a question or finding; history may state an event or dispute; reference material may name the item being defined. A generic heading such as “Analysis” gives the reader no map. Keep scope, period and number in a heading when its claim depends on them, and check that its evidence supports it.

**REPORT-SUMMARY-01 — A long decision report stands on its summary.** Give a delivered multi-page decision report a summary page that works alone: the situation, answer, three to five supported claims with their periods, and the decision requested. It is not a universal page-count rule for short explainers or a demand for a closing ask in research reports. Use connected prose or numbered claims, not fragments copied from section titles.

## Exhibits and visual language

**REPORT-EXHIBIT-01 — Make every exhibit traceable.** Number figures and tables separately, refer to them by number, and title each with its takeaway. Put its source, date or period, units, denominator and any estimate or assumption nearby. Mark truncated axes. A figure should reveal structure, flow or comparison that prose or a nearby table does not already show. Keep exact plotted values available in text or an accessible table.

**REPORT-VIZ-01 — Let the comparison choose the chart.** Use position or length for precise comparison, direct labels for the series that carries the claim, and a common scale when comparing panels. Distinguish missing from zero and forecast from observation; disclose filters, aggregation, logarithmic scales and justified axis truncation. Bars encoding magnitude need a zero baseline. Calculate totals from unrounded values. For print, check the scaled figure on the actual page: labels need at least 8.5pt and readable contrast. The chat SVG's 680px canvas does not establish print legibility.

**REPORT-DESIGN-01 — Compose a publication for its reader.** Set the document's hierarchy with typography, spacing and alignment before adding containers. A restrained face pair, fine rules and one meaningful accent often suit a report; cards suit independently actionable items, while aligned rows suit repeated comparisons. Avoid reflexive stat cards, tinted callouts, decorative badges and box-and-arrow figures that have no claim. These are design choices, not a ban on a supplied brand or a format that benefits from cards. Vary page rhythm: some sections are prose, others give an exhibit room to carry the point.

**REPORT-BRAND-01 — Name the issuer as the reader knows it.** A report cover names the issuing organization and, when relevant, the recipient, author/team, date, version and confidentiality. Use supplied brand assets and a consistent identity across cover, headers and exhibits. Do not invent a logo, palette or fictional organization to make a page feel finished.

## Paged composition and print

**REPORT-ANATOMY-01 — Give longer reports navigable furniture.** For a report over about four pages, consider cover, contents with page numbers, stand-alone summary, body, limits or next steps, appendix and any required notice. A decision report's title and sections can carry claims; research and reference material retain their genre. Use a running header and page number in the body, with no page furniture on the cover. Adapt the anatomy to the reader and any supplied template or required notice.

**REPORT-PRINT-01 — Declare and inspect the page.** Choose A4 or Letter according to the recipient, then set margins, running headers, page numbers, contents and break behavior in the chosen PDF tool. Keep headings with their first paragraph, repeat table headers and allow long tables to continue. Avoid stranded headings, isolated lines, half-empty pages and tiny printed figure labels. Check the actual output, including contents page numbers and the last page. `jaw-pdf` owns tool-specific export and verification mechanics.

## Assurance and reader review

**REPORT-ASSURANCE-01 — State the review scope before export.** Label the artifact `draft`, `standard` or `publication`. A draft may have source and spot checks; standard review covers text integrity and pagination; publication review covers every final page, fonts and glyphs, claims and exhibits, and editorial comprehension. Report omitted checks explicitly. These labels describe review depth; they are not automated pass receipts and do not waive `jaw-pdf`'s mandatory checks for a delivered PDF.

**REPORT-QA-01 — Review the final artifact, not a previous build.** Confirm page count and size, text extraction where available, last records and totals, font coverage, glyphs, contents links and numbers, table continuations, headings and figure scale. Visually inspect the pages required by the chosen scope; a delivered PDF follows `jaw-pdf`'s every-page check. Record each finding and the corrected page or state. A successful export, filename or stale screenshot is not a PASS.

**REPORT-FRESH-01 — Ask a reader to reconstruct the story.** From final rendered pages, a reader without task context states the answer, why the evidence supports it, the action when this genre calls for one, and where comprehension stopped. Note empty headings and any page where visual emphasis obscures the claim. Fix structure before polishing sentences. If no independent reader is available, perform the same check yourself and disclose that limit; keep `visual-story.md`'s figure-level fresh-reader check.
