# Reader Documents

Canonical owner of reader-facing document structure (READER-DOC-01..05). Other skills
point here; they do not restate these rules.

## Scope

Anything a person reads to understand or decide: reports, explainers, devlog narrative
sections, PABCD D summaries, PR descriptions, research reports, generated documentation.

Not in scope: evidence artifacts — command logs, receipts, gap matrices, test output,
search ledgers. Those keep their raw form, live beside the document, and are linked.

The failure this prevents: an agent that ran twelve probes writes a document listing the
twelve probes. The reader wanted the answer, the reason to believe it, and what to do
next. The probes belong in an appendix.

## READER-DOC-01 — Reader contract

Before drafting, write one line: **who reads this, what they decide or do next, what they
already know.** Then choose one document type and hold it:

| Type | Reader question | Shape |
|------|-----------------|-------|
| Report / explainer | What is true, and why? | Answer → why → evidence → next steps |
| Decision record | What did we choose, and what does it cost? | Context → drivers → options → decision → consequences |
| How-to | How do I do X? | Goal → prerequisites → numbered steps → verification |
| Reference | What are the exact facts? | Tables and definitions, no narrative |
| Research report | What does the evidence say about Q? | Direct answer → analysis by sub-question → limits → sources |

Mixing types in one document degrades all of them. Split instead.

## READER-DOC-02 — Answer first

Open with situation, complication, question, and answer in one short paragraph. The
governing conclusion appears before any evidence. Every heading states a claim, not a
topic: "Cost falls 12% at the chosen tier", not "Analysis".

Korean documents use **두괄식** — 결론·전망·요약을 맨 앞에. **기승전결** is a narrative
build-up for stories and essays; it is never the shape of a report.

## READER-DOC-03 — Descending structure

Each heading summarizes what sits under it. Siblings do not overlap and together answer
the reader's question. Their order follows the reader's questions, not the order the work
happened in. Add a table of contents once the document passes about one screen.

Decision documents carry three sections writers habitually skip:

- **Non-goals** — what this deliberately does not do.
- **Alternatives considered** — each with the reason it was rejected.
- **Consequences** — what the choice costs, including the bad parts.

Match length to the decision. A one-paragraph choice does not need a full record.

## READER-DOC-04 — Evidence separated and anchored

Probes, commands, receipts, screenshots, and logs go to an appendix or a linked evidence
file. The narrative cites them by anchor (`A1`, `A2`, …).

Every factual claim in the narrative resolves to one of: an evidence anchor, a source URL
with its date, or a stated assumption. A claim with none of the three is removed or
labelled unverified.

Evidence *status* is not owned here — `search` owns `sufficient` / `partial` /
`browse-needed` / `insufficient`. This rule only says where the evidence sits in the
document, and that the narrative may not quietly outrun it.

Do not paste a command transcript where the reader expects a conclusion. Do not summarize
the evidence away either. Both belong in the document, in their own places.

## READER-DOC-05 — Fresh-reader check

A reader with no task context answers three questions in its own words:

1. What is the answer?
2. Why should I believe it?
3. What do I do next?

Where the reader stumbled, fix the structure. Record who read it and what changed.

`doc-coauthoring` Stage 3 stays canonical for co-authored documents — it owns question
generation, the sub-agent mechanics, and the exit condition. This rule sets the
three-question floor for every other reader deliverable.

## Skeletons

Report or explainer:

```markdown
# <Claim-shaped title>
<SCQA paragraph ending in the answer>
## Contents            (once past one screen)
## <Claim 1>           reasoning, figure whose caption states what changes
## <Claim 2>
## What this does not cover
## Next steps          who does what
## Appendix: evidence  A1..An — commands, receipts, sources with dates
```

Decision record:

```markdown
# <Decision as a sentence>
Status · Date · Deciders
## Context and problem
## Decision drivers
## Options considered   each with pros, cons, why rejected
## Decision
## Consequences         good, bad, follow-ups
```

Explainer with a figure: question → one figure whose caption states what changes and why
→ detail on demand → sources. Rendering, formats and security stay owned by `diagram`.

## Layer order

Structure first, sentences second. Fix the map before polishing prose, and limit a
revision to one or two structural changes — a document rearranged wholesale on every pass
loses the reader.
