# Self-check — status-report.md against references/reader-documents.md

## Reader contract line

Line 3 of `status-report.md`, immediately under the title, labelled **Reader contract:**. It names the reader (a maintainer who was not in the session), the decision (whether to approve the reader-documents PR), the prior knowledge (repo layout and the per-file size cap, no session context), and the chosen type (report). One type is held throughout — no decision-record or how-to sections are mixed in.

## Rules applied and where

**READER-DOC-01 — Reader contract.** The contract line above. Type held as *Report / explainer*, so the shape is answer → why → evidence → next steps. The two "decision taken" notes (A13, A14) are reported as facts inside the report rather than expanded into a decision record, which would have mixed types.

**READER-DOC-02 — Answer first.** The opening paragraph runs SCQA in one block: situation (500-line cap enforced by the validator), complication (`dev/SKILL.md` at 504 fails; the protocol cannot be inlined at 472), question (implicit — what changed and what must a reviewer check), answer (two extractions clear the cap; the stale "47" count is the one thing to check first). The governing conclusion appears before any evidence. Every heading states a claim: "dev/SKILL.md breaches the cap on main, and the §7.2 extraction lands it at 496", "Green CI on main does not cover the validator failure" — none are topic labels like "Analysis" or "CI".

**READER-DOC-03 — Descending structure.** Each heading summarizes what sits under it. Siblings do not overlap: cap breach and its fix, protocol placement, the count contradiction, verification coverage, exclusions, next steps. Order follows the reader's questions (what is broken → how it is fixed → what is newly wrong → how well is it proven), not the order the probes ran in. A table of contents is present because the document exceeds one screen. Non-goals appear as "What this does not cover"; alternatives and consequences are omitted because the reference says to match length to the decision and this is a report, not a decision record — the one rejected alternative that matters to the reader (inlining the protocol into `search/SKILL.md`) is stated with its reason inside the relevant claim.

**READER-DOC-04 — Evidence separated and anchored.** No command transcript sits in the narrative. All sixteen raw notes are in "Appendix: evidence" as A1–A16, each tagged by kind (command, file read, grep, probe, decision, risk). Every factual claim in the narrative resolves to an anchor or is labelled an assumption. Three assumptions are labelled inline as *Assumption (not in the notes)*: whether the PR already updates the "47" references, why CI was green while the validator fails, and — in "What this does not cover" — that the notes record decisions rather than verified file states. No source URLs exist in the input, and the appendix says so. Evidence *status* language (sufficient/partial/insufficient) is deliberately not used, since the reference assigns that vocabulary to `search`.

**READER-DOC-05 — Fresh-reader check.** Self-administered; no external reader was available in this bounded task, so this is a floor check rather than a recorded read. (1) *What is the answer?* — two extractions bring both files under the cap, and the one open blocker is the 47-vs-48 count. (2) *Why should I believe it?* — 504 > 500 from the validator, 472 + 140 > 500 arithmetic, and three grepped locations stating 47. (3) *What do I do next?* — the four numbered items in "Next steps", each with an owner. No structural change was needed on this pass; per the reference's layer order, structure was fixed before prose and no wholesale rearrangement was made.

## Claim-to-anchor map

| Narrative claim | Resolves to |
|-----------------|-------------|
| Repo enforces a 500-line cap per `SKILL.md` via `validate_public_surface.py` | A3 |
| `dev/SKILL.md` is 504 lines and the validator exits 1 on main | A1 |
| The only failing condition is line count (skill count matches expectation) | A2, A3 |
| Extraction to `dev/references/static-analysis.md` yields −11 lines → 496 | A13 |
| Four lines of headroom remain after the fix | A13 + A3 (496 vs 500) |
| Splitting material into a `references/` folder has repo precedent | A11 |
| `search/SKILL.md` is 472 lines | A4 |
| Inlining ~140 protocol lines would breach the cap | A14 |
| Skills must not duplicate canonical content | A8 |
| `search` already owns tier policy standalone | A9 |
| Three published surfaces state 47 reference folders | A6, A7 |
| The new folder makes the true count 48 | A15 |
| Whether the PR updates those counts is unknown | labelled assumption |
| Last CI on main `25e30780` succeeded 2026-09-05 | A5 |
| Green CI coexists with a failing validator | A5 + A1 |
| Explanation for that coexistence | labelled assumption |
| `pytest tests/` needs `officecli`; CI runs only one test file | A16 |
| Registry drift 230 vs 226 is pre-existing and out of scope | A12 |
| `deep-research` is vendored Apache-2.0 by sanjay3290, wrapping Gemini | A10 |
| The 496 figure is a projection, not a measurement | A13 (recorded as a decision, no post-change measurement in the notes) |

Nothing in the narrative is unsourced. Facts absent from the notes — PR number, branch name, author, review state, current file contents after the edits — are not asserted anywhere in the report.

