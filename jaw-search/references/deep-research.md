# Deep Research

Canonical owner of the deep-research **method** for cli-jaw. The tiers in `jaw-search/SKILL.md`
remain the execution lanes and keep their routing, gates and evidence-status policy; this
reference says how a deep-research task is scoped, tracked and reported before and after
those lanes run.

## SEARCH-DEEP-01 — Entry

Only on explicit request: **deep research**, **딥리서치**, **심층 조사**, or a question
that genuinely needs multi-source synthesis (contested claims, a comparison across
several vendors, a landscape survey). An ordinary latest/current lookup stays on the
normal ladder in `jaw-search/SKILL.md` however important it is. Nothing auto-escalates into
this protocol.

A heavier tier is not deep research. Running `--reasoning xhigh` or a Gemini agent
without a written scope and ledger produces an unauditable answer, not a research report.

## SEARCH-DEEP-02 — Scope and plan

Write this down before the first query:

- the question, the reader, and the decision the reader faces;
- time window, geography, entities, and explicit exclusions;
- the deliverable format;
- which claims are consequential enough to need a primary source.

Apply the reader contract from `jaw-dev/references/reader-documents.md` here — the scope
step and the reader contract are the same act.

## SEARCH-DEEP-03 — Query families, each with a goal

Expand the question into distinct families: entities, time windows, source classes, rival
hypotheses, and the strongest opposing view. Each family carries the goal it serves and
what a hit would unlock, so the next wave is never a reworded repeat of the last.

Families map onto the lanes `jaw-search/SKILL.md` already defines — `official`,
`community`, `realtime`, `fetch`, `academic`, `package`, `archive`. Do not invent a
parallel lane vocabulary.

Start wide with short queries, then narrow. Korean requests follow the query-rewrite
rules in `search` (focused keywords, preserved anchors, source hints).

## SEARCH-DEEP-04 — Waves and the gap matrix

Wave 1 discovers **and opens** the strongest candidates. Do not end a wave with zero
pages fetched or opened; a wave of snippets is not a wave.

After each wave, one reflection step — never mixed with a fetch — updates the matrix:

| claim | evidence (URL, date, tier) | status | contradiction | missing | next query |

`status` reuses the existing `sufficient` / `partial` / `browse-needed` /
`insufficient` vocabulary from `search`. There is no second scale.

Wave 2 fills the gaps and chases the strongest leads. Later waves only for a material
unresolved gap, a high-stakes decision, or an explicitly exhaustive request.

## SEARCH-DEEP-05 — Budgets and stop rules

State the numbers before wave 1:

| Question shape | Budget |
|----------------|--------|
| Single fact with context | 3-10 source opens, one lane |
| Comparison across N options | 2-4 lanes, 10-15 opens each |
| Landscape or exhaustive survey | only when explicitly requested |

Stop when every section has sufficient evidence and contradictions are bounded, or after
three consecutive waves with no new lead, or at five waves. Record which stop fired.
Repeated evidence is a stop signal, not a reason to keep fetching.

## SEARCH-DEEP-06 — Execution lanes

The tiers in `jaw-search/SKILL.md` do the work, unchanged — it owns which tier fits a
signal, each tier's gate, and the escalation order. Read it there rather than here; this
protocol only adds that the `deep-research` skill (the Gemini agent, when
`GEMINI_API_KEY` exists) is one more lane of the same kind, for breadth-first autonomous
coverage.

Choosing a heavier lane never replaces the ledger. Whatever a lane returns is evidence to
be recorded, not a finished report to be forwarded.

Model-gated parallel research (2-4 lanes) is already defined in `jaw-search/SKILL.md`; this
protocol adds only that each lane returns provenance records — claim, title, publisher,
date, URL, tier, contradictions — and never a report draft.

## SEARCH-DEEP-07 — Ledger and report-source.md

Keep one claim-to-source ledger for the whole task: claim, source title, publisher, date,
URL, tier reached, status, contradictions.

Write `report-source.md` once: title, reader, date, scope, assumptions, the direct
answer, analysis by sub-question, limitations and disagreements, and sources. Cite with
gapless sequential numbers and a terminal source list, so pruning a source during
synthesis never leaves a hole. Claims that reached only Tier 1 are listed separately as
open questions and never promoted silently.

## SEARCH-DEEP-08 — Deliverable

The reader-facing report follows `jaw-dev/references/reader-documents.md`: answer first,
claim-shaped headings, evidence in an appendix. Figures, charts and HTML go through the
`diagram` skill.

The ledger, gap matrix and wave journal are evidence artifacts. They are linked from the
report, not narrated inside it (READER-DOC-04).

Never invent a source, date, URL, quotation, or access result. A missing source is a
stated gap.
