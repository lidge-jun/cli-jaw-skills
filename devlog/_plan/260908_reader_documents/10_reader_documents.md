# wp2 — Reader-document structure (diff-level)

Depends on wp1. Verifier: `python3 scripts/validate_public_surface.py` (must reach the
"validated 226 skills" line, which requires dev/SKILL.md back under 500),
`python3 -m pytest tests/test_dev_frontend_refresh.py -q`, `git diff --check`, and a forward-use trial in which a
fresh Opus-5 agent is handed a raw evidence dump and the new reference, and must produce
a document whose first paragraph is the answer and whose probes sit in an appendix.

## NEW dev/references/reader-documents.md (~120 lines)

Canonical owner of "reader-facing document structure", rules READER-DOC-01..05. Written
for this repo's voice: short rule id, one paragraph, no restatement of `search` or
`diagram` policy. Contents:

1. **Scope** — reports, explainers, devlog narrative sections, PABCD D summaries, PR
   descriptions, research reports. Excluded: evidence artifacts (command logs, receipts,
   matrices, test output) which keep their raw form and are linked, never narrated.
2. **READER-DOC-01 Reader contract** — one line before drafting: who reads this, what
   they decide next, what they already know. Then pick one document type
   (explanation / decision record / how-to / reference / research report) and hold it.
   Table of five types with the reader question and shape each answers.
3. **READER-DOC-02 Answer first** — situation, complication, question, answer in one
   short opening paragraph; the conclusion precedes any evidence. Headings state claims
   ("Cost falls 12% at the chosen tier"), not topics ("Analysis"). Korean documents use
   두괄식; 기승전결 belongs to narrative writing and never to a report.
4. **READER-DOC-03 Descending structure** — each heading summarizes what sits under it;
   siblings do not overlap and together answer the question; order follows the reader's
   questions, not the order work happened. Decision documents carry non-goals,
   alternatives considered with the reason each was rejected, and consequences.
   A table of contents once the document passes about one screen.
5. **READER-DOC-04 Evidence separated and anchored** — probes, commands, receipts and
   screenshots go to an appendix or a linked evidence file; the narrative cites them by
   anchor. Every factual claim resolves to an anchor, a source URL with its date, or a
   stated assumption. This is the rule that connects to `search`: evidence *status*
   stays owned by `search` (`sufficient`/`partial`/`browse-needed`/`insufficient`),
   this rule only says where the evidence lives in the document.
6. **READER-DOC-05 Fresh-reader check** — a context-free reader answers three questions
   in its own words: what is the answer, why believe it, what do I do next. Where it
   stumbled, fix the structure. `doc-coauthoring` Stage 3 stays canonical for co-authored
   documents: it keeps question generation, sub-agent mechanics and the exit condition.
   READER-DOC-05 sets only the three-question floor for any reader deliverable, so reader
   testing keeps a single owner.
7. **Skeletons** — report, decision record (status/context/drivers/options/decision/
   consequences), and one-figure explainer. Markdown fenced, copy-paste sized.
8. **Layer order** — structure first, sentences second; a revision changes one or two
   structural things, not the whole map.

## MODIFY dev/SKILL.md — net zero or negative lines

The validator fails at 504 lines today. Two edits, in this order:

1. **Add one ownership row** after "Project scaffolding / docs | dev-scaffolding | dev-pabcd":
   `| Reader-facing document structure | dev refs/reader-documents.md | dev-pabcd, dev-scaffolding, diagram, doc-coauthoring |` (+1 line)
2. **Add the reference pointer** in §4 Change Documentation, one line after the fenced
   entry template: "Reader deliverables (reports, summaries, devlog narrative) follow
   `references/reader-documents.md`: answer first, evidence in an appendix." (+1 line)
3. **Reclaim lines so the file lands under 500.** The audit corrected my arithmetic: the
   Redis example in section 8 is only lines 498-500, worth at most 3 lines against the 6+
   needed (504 + 2 additions = 506). Instead move the section 7.2 rule-to-prose mapping
   table (lines 460-472) into `dev/references/static-analysis.md`, a new file inside dev's
   already-counted references/ folder, leaving a one-line pointer. Net -11 lines lands at
   495. This moves illustration, not rule text: gate commands, thresholds and escape-hatch
   rules stay in SKILL.md. `dev-architecture/references/` holds only barrel, circular and
   coupling docs, so the fallback named earlier does not exist and is withdrawn.

Verification for this file: `wc -l dev/SKILL.md` ≤ 500 and the validator prints
"validated 226 skills".

## MODIFY dev-pabcd/SKILL.md — 3 lines

- **P — Plan**, after "Part 1 / Part 2" (line ~127): one line — "Part 1 follows
  `dev/references/reader-documents.md` READER-DOC-02: the answer first, in the reader's
  terms."
- **C — Check**: one line — when the work-phase delivers a document or report to a
  person, C includes the READER-DOC-05 fresh-reader check.
- **D — Done** (line ~193): replace "Summarize the entire flow:" framing with one added
  line — "Write D for someone who was not in the loop: the outcome first, then what
  changed, with evidence pointers (READER-DOC-02/04). The P/A/B/C list is the evidence
  trail, not the summary." Keep the existing bullets.

## MODIFY dev-scaffolding/SKILL.md — 1 row + 3 lines

- Add a row to the Modular References table pointing at
  `dev` `references/reader-documents.md` with "When to Read: writing a devlog narrative,
  plan summary, or generated documentation".
- In the devlog/source-of-truth section, three lines: the narrative doc carries the
  answer and what changed; probe logs, command output and receipts live beside it and are
  linked; a reviewer should learn what was decided without opening a transcript.

## MODIFY diagram/SKILL.md — 2 lines in "When to Use"

One line under §2 Proactive generation: a report or explainer that accompanies a diagram
follows `dev` `references/reader-documents.md` — answer first, figure captions state
what changes, evidence in an appendix. Rendering, security and format rules are unchanged
and stay owned here.

## MODIFY doc-coauthoring/SKILL.md — 2 lines in Stage 2

Under "Establish Structure": before proposing sections, apply the reader contract and
answer-first rule from `dev` `references/reader-documents.md`; Stage 3 reader testing
already satisfies READER-DOC-05. No change to the three-stage flow.

## Acceptance

- Validator prints "validated 226 skills"; pytest passes; `git diff --check` clean.
- No canonical text duplicated: each stub is one or two lines that point.
- Forward-use trial output has a claim-shaped title, an answer-first opening, and an
  appendix holding every probe from the input dump.

