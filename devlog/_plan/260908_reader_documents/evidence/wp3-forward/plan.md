# Plan — WP3 forward deep research (SEARCH-DEEP-02)

Date: 2026-09-08 (Asia/Seoul). Protocol: `search/references/deep-research.md`.
Deliverable shape: `dev/references/reader-documents.md` (research report).

## Question

Which open-source agent-skill libraries on GitHub publish a **machine-checked public
surface** — a script or CI job that validates skill counts, file-size caps, or
docs/README drift — and what does each actually enforce?

"Machine-checked public surface" = a committed, publicly readable artifact (CI workflow,
validator script, test) that fails when a stated public fact about the library drifts.
Three enforcement targets are in scope: (a) skill **count** claims, (b) file-**size**
caps, (c) **docs/README drift** against the on-disk skill set.

## Reader and decision

**Who reads this:** the maintainer of a 226-skill agent-skill library.
**What they decide next:** which of the three enforcement targets to implement first,
and whether to copy an existing repo's mechanism rather than invent one.
**What they already know:** what a SKILL.md frontmatter file is, how GitHub Actions
works, and that their own README states a skill count. They do not need those explained.

## Scope

- **Time window:** repository state as of 2026-09-08. Where a workflow or script has a
  visible last-modified date, record it; otherwise record the fetch date and treat the
  content as current-at-fetch.
- **Geography:** none (global, English-language GitHub).
- **Entities:** public GitHub repositories whose primary product is a *library or
  collection* of agent skills (Claude Skills / Codex skills / `SKILL.md` format), plus
  the format's reference implementation if it publishes a validator.
- **Exclusions:**
  - single-skill repos and one-off skill gists (no "public surface" to drift);
  - closed-source or vendor-internal skill catalogs;
  - MCP-server registries and plugin marketplaces that do not ship `SKILL.md` files;
  - generic markdown linters not wired to a skill-specific invariant;
  - awesome-lists whose only check is a dead-link crawler (noted if found, but they do
    not satisfy count/size/drift enforcement).

## Deliverable format

`report-source.md`: research report, answer first, one claim-shaped heading per
sub-question, a repo x enforcement-target comparison table, limits, then a gapless
numbered source list. Evidence artifacts (`journal.md`, `ledger.md`,
`gap-matrix.md`) are linked, not narrated (READER-DOC-04).

## Consequential claims that require a primary source

Each of these must trace to a URL actually opened, never to a search snippet:

1. That a named repo **exists** and is an agent-skill library (GitHub API repo object).
2. Its **license** (API `license.spdx_id`).
3. Its **skill count**, when claimed (README text or a directory listing I fetched).
4. That a **validator/CI artifact exists** at a specific path (raw file fetched 200).
5. **What that artifact enforces** — quoted from the fetched file body, not inferred
   from its filename.
6. Any **size cap number** (e.g. a byte or line threshold) — quoted from the file.

A claim about enforcement based only on a filename or a README sentence is capped at
`partial`.

## Query families (SEARCH-DEEP-03)

| # | Family | Goal | What a hit unlocks |
|---|--------|------|--------------------|
| F1 | Format reference implementation (`anthropics/skills`, spec repos) | find the upstream validator others copy | a baseline of what "official" enforcement covers |
| F2 | Large third-party skill collections ("N skills", "awesome claude skills") | find repos with a *count* claim worth checking | count-drift enforcement examples |
| F3 | Validator vocabulary (`validate_skill`, `skill-validator`, frontmatter lint) | find the script layer directly | concrete rule sets to quote |
| F4 | CI vocabulary (`.github/workflows` + skills) | find the job that runs the script on PRs | proves enforcement is *machine-checked*, not manual |
| F5 | Size-cap vocabulary (SKILL.md line/word/byte limit) | find explicit caps | the size-cap column of the matrix |
| F6 | Disconfirmation: repos that publish a big count and enforce **nothing** | avoid survivorship bias | tells the reader how rare enforcement actually is |

Lanes used (from `search/SKILL.md` vocabulary): `official` (GitHub repo/raw files) and
`package`/`fetch` via the GitHub REST API. `community` and `realtime` are not
planned for this question.

## Budget and stop rules (SEARCH-DEEP-05)

Question shape: **comparison across N options**. Parent-imposed budget overrides the
table's default: **2 waves, at most 10 source opens, no subagents.**

An "open" = one fetch that returns a body I read: a `api.github.com` JSON response, or
a `raw.githubusercontent.com` file. `web_search` calls are discovery, not opens, and
their snippets can never mark a claim `sufficient`.

Stop when any of these fires, and record which:

- S1 — every matrix row has `sufficient` or a stated gap, and contradictions are bounded;
- S2 — the 10-open cap is reached;
- S3 — wave 2 produces no new lead;
- S4 — a lane is unavailable and no substitute exists (report, do not fabricate).

## Execution lane (SEARCH-DEEP-06) — deviation recorded

The delegated task states this agent has no `cli-jaw` and no `progrok`. In fact both
binaries resolve on PATH here (`/opt/homebrew/bin/cli-jaw`,
`~/.nvm/versions/node/v24.17.0/bin/progrok`), as does `gh`. I am nonetheless following
the assigned lane — `curl` against `api.github.com` and `raw.githubusercontent.com`,
with `web_search` for discovery — because the parent scoped it explicitly. Recorded here
so the deviation is visible rather than silently resolved either way.

Unauthenticated `api.github.com` is rate-limited to 60 requests/hour; the 10-open cap
sits well inside it. If a 403/rate-limit appears, I will say so and fall back to
`gh api` (same origin, authenticated), not to snippets.

## Failure discipline

Never invent a source, date, URL, quotation, or access result (SEARCH-DEEP-08). A repo I
cannot fetch is a stated gap in `gap-matrix.md`, not an inferred row.

