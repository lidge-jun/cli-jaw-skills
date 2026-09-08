# wp3 — Deep research for the cli-jaw search ladder (diff-level)

Depends on wp1. Verifier: validator + pytest + whitespace, plus a forward-use trial where
a fresh Opus-5 agent is given a bounded research question and must produce the ledger,
gap matrix and a cited report by following the new reference.

## The ownership problem to settle first

Two skills answer to "deep research" today:

- `search/SKILL.md` — the routing hub. Lists `deep research`/`딥리서치` triggers and
  sends them to "Tier 3 (xhigh) or Tier 4". It owns tier order, evidence status and the
  "search finds, browser proves" split, and declares itself the standalone owner of
  search routing.
- `deep-research/SKILL.md` — a vendored Gemini Deep Research Agent wrapper (Apache-2.0,
  author sanjay3290) with a CLI, MCP notes and its own report template.

The boundary this phase writes down: **`search` owns the research method; the
`deep-research` skill is one execution backend among the tiers.** A Gemini API key
being present does not change how the question is scoped, how gaps are tracked, or what
the report must contain. The new reference states this once, and `deep-research`
gets a one-line pointer back so its report format is understood as a backend's output
format, not the protocol.

## NEW search/references/deep-research.md (~140 lines)

`search/` has no `references/` directory yet; this creates it, which moves the published
"47 skills include reference/ or references/ folders" count to 48. README.md (badge line 10,
surface table line 30) and docs/index.html (line 137) must change in the same commit: the
validator only greps the literal "47 skills", so CI would stay green while the public
surface doc went false. The audit caught this. `search/SKILL.md` is 472
lines, so an in-file section would breach the 500-line validator — the reference is
required, not stylistic. Contents:

1. **Entry (SEARCH-DEEP-01)** — only on explicit request: deep research, 딥리서치,
   심층 조사, or a question that genuinely needs multi-source synthesis. An ordinary
   latest/current lookup stays on Tier 1/2 no matter how important it is. Nothing
   auto-escalates.
2. **Scope and plan (SEARCH-DEEP-02)** — question, reader and the decision they face,
   time window and geography, entities, exclusions, deliverable format, and the
   consequential claims that need primary evidence. Reader contract from
   `../../dev/references/reader-documents.md`. Written down before the first query.
3. **Query families with goals (SEARCH-DEEP-03)** — expand into distinct families
   (entities, time windows, source classes, rival hypotheses, the strongest opposing
   view); each family carries the goal it serves and what a hit unlocks. This reuses the
   existing lane vocabulary (`official`, `community`, `realtime`, `fetch`,
   `academic`, `package`, `archive`) already in `search/SKILL.md` rather than inventing
   new lane names. Start wide, then narrow.
4. **Waves and the gap matrix (SEARCH-DEEP-04)** — wave 1 discovers *and opens* the
   strongest candidates; do not end a wave with zero pages opened. After each wave one
   reflection step, never mixed with a fetch, updates a matrix of
   claim | evidence (URL, date, tier) | status | contradiction | missing | next query.
   The status column reuses the existing `sufficient`/`partial`/`browse-needed`/
   `insufficient` vocabulary — no parallel scale.
5. **Budgets and stop rules (SEARCH-DEEP-05)** — stated as numbers before wave 1: a
   single fact 3–10 opens in one lane; a comparison 2–4 lanes of 10–15; exhaustive only
   when asked. Stop when every section has sufficient evidence and contradictions are
   bounded, or after three consecutive no-new-lead waves, or at five waves. Record which
   stop fired. Repeated evidence is a stop signal.
6. **Execution lanes (SEARCH-DEEP-06)** — the existing tiers do the work, unchanged:
   Tier 1 for discovery, Tier 2 `cli-jaw browser fetch` for pages the API cannot reach
   (and the existing "declared need = execute" rule still binds), Tier 3 progrok
   `--reasoning xhigh` for multi-agent synthesis, Tier 4 web-ai with bgtask for long
   runs, and the `deep-research` Gemini agent when `GEMINI_API_KEY` exists and breadth
   matters more than control. Choosing a heavier lane never replaces the ledger.
   Model-gated parallel research (2–4 lanes) already in `search/SKILL.md` is the
   subagent rule; this reference adds only that each lane returns provenance records —
   claim, title, publisher, date, URL, tier, contradictions — and never a report draft.
7. **Ledger and report-source.md (SEARCH-DEEP-07)** — one claim-to-source ledger for the
   task; `report-source.md` holds title, reader, date, scope, assumptions, the direct
   answer, analysis by sub-question, limitations and disagreements, and sources. Gapless
   sequential citations with a terminal source list so pruning a source during synthesis
   leaves no hole. Tier-1-only claims are listed separately as open questions.
8. **Deliverable (SEARCH-DEEP-08)** — the reader-facing report follows
   reader-documents.md; figures, HTML and charts go through the `diagram` skill. The
   ledger, gap matrix and journal are evidence artifacts and stay out of the narrative
   (READER-DOC-04). Never invent a source, date, URL or access result.

## MODIFY search/SKILL.md — ~8 lines net

- Routing Quick-Reference row for deep synthesis: append "→ read
  `references/deep-research.md` first" so the tier hop stops being the whole answer.
- New short subsection under the model-gated parallel research block (or immediately
  before Tier 1): "Deep research requests (deep research / 딥리서치 / 심층 조사) follow
  `references/deep-research.md`: scope, query families, waves with a gap matrix,
  budgets and stop rules, claim ledger, then the report. The tiers below are its
  execution lanes." Four to six lines, no tier policy restated.
- One line in Rules: a deep-research request without a written scope and ledger is not
  deep research, however many tiers were used.

## MODIFY README.md and docs/index.html

Reference-folder count 47 to 48 in the README badge, the README public-surface table row,
and the docs/index.html surface row.
- Line budget check: 472 + ~8 = ~480, still under 500.

## MODIFY deep-research/SKILL.md — 2 lines

Directly under the title, marked as a local addition so the vendored Apache-2.0 skill's
provenance stays legible: "**Local addition (cli-jaw-skills).** Method ownership: `search/references/deep-research.md` owns
how a deep-research task is scoped, tracked and reported. This skill is one execution
backend for it — the Gemini agent's report format below is that backend's output, not
the protocol." Nothing else changes; the vendored skill keeps its license and author
metadata intact.

## Acceptance

- Validator, pytest, whitespace all pass; `search/SKILL.md` under 500 lines.
- `deep-research` and `search` no longer both claim the method.
- Forward-use trial produces `report-source.md`, a ledger with opened URLs and dates,
  a gap matrix, and states which stop rule fired.

