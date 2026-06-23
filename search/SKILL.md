---
name: search
description: "Unified search hub. Route any web/real-time/X lookup through a 4-tier escalation: built-in web search → cli-jaw browser CDP → progrok Grok OAuth → web-ai (Grok Expert / GPT Pro). Use for: search, 검색, web search, latest news, real-time info, X/Twitter, fact lookup, deep research."
metadata:
  {
    "triggers": ["search", "검색", "web search", "웹검색", "웹 검색", "find online", "look up", "google", "최신", "latest", "news", "뉴스", "real-time", "실시간", "x search", "twitter search", "트위터", "현재", "요즘", "deep research", "딥리서치"],
    "requires": { "optional_bins": ["progrok", "cli-jaw"] }
  }
---

# Search Hub

One entry point for every web / real-time / X lookup. Walk the tiers **in order**;
stop at the first that fully answers the query.

Search is discovery, not evidence. Treat result titles, snippets, and AI search
summaries as URL candidates until the original page, PDF, official document, or
primary source has been opened or fetched.

**Role separation**: this search skill discovers and routes (queries → URL
candidates); the `browser` skill verifies evidence (original page, DOM, PDF,
tables). Search finds, browser proves.

**Standalone owner**: other skills may point here for external/current evidence,
but they should not copy this tier policy. Update this skill first when search
routing, evidence status, or browser-verification rules change.

## `/search` command contract

`/search <query>` is a routing command, not a provider implementation. It must
inherit this skill's routing/evidence invariants: classify local-vs-external
search, rewrite external requests into focused queries, discover candidate URLs
before browser commands, and refuse snippet-only `sufficient` claims.

Slash-specific report fields, UX wording, and v1 command boundaries belong in
the `/search` workflow prompt, not in this skill. Update this skill only for
canonical search policy that should also apply to non-slash search intents and
dev-role evidence routing.

## Model-gated parallel research

Use single-agent search by default. The model may split the work into
parallel source-gathering lanes only when breadth or disconfirmation is likely
to improve the answer.

Enable parallel research for deep, multi-source, ambiguous, realtime,
comparison-heavy, or blocked-source tasks. Keep simple official-doc lookups,
specific URL reads, and quick version checks single-agent.

When parallel research is useful, cap it at 2-4 lanes:

- `official`: vendor docs, release notes, government/institution pages,
  primary PDFs.
- `community`: GitHub issues, Reddit, HN, Stack Overflow, forums.
- `realtime`: X/Twitter, news, current status, recent posts.
- `fetch`: browser fetch/open/text/get-dom/snapshot verification for weak or
  blocked candidate URLs.

Merge lane outputs into one evidence matrix. Parallel snippets still do not
count as sufficient evidence; the final answer still needs at least one
primary/original page fetched or opened before any claim is marked
`sufficient`.

**Snippet consensus is not verification.** Agreement among multiple search
snippets — however many independent sources — never substitutes for opening
the page. Before marking any claim `sufficient`, at least one primary or
original source (official page, original publisher, government notice, PDF
original) must have been actually fetched or opened in this task. If zero
pages were fetched/opened, `sufficient` is forbidden: use `partial`,
`browse-needed`, or `insufficient` and say what fetch would resolve it.

## Candidate-space discipline (multi-constraint identification)

**Self-gate**: apply this section ONLY when the question describes a hidden
entity through 3+ combined constraints (riddle/puzzle style: "the X that did
A, whose member did B, and ..."). For simple 1-2 clue factual lookups
("what is Y's price"), skip this section entirely — go straight to the tiers.

When the gate triggers:

1. **M1 — Anchor on the rarest clue.** Rank clues by how few entities can
   satisfy them. Anchor the search on the most discriminative clue (a unique
   choreography, a specific incident, an exact number), NEVER on a broad
   category clue ("girl group", "drama", "city").
2. **M2 — Enumerate before you converge.** Before accepting any candidate,
   list 3+ candidates that satisfy the anchor clue (or state explicitly that
   fewer exist and why). Check EVERY candidate against EVERY clue in a
   candidate × constraint matrix; record each elimination reason.
3. **M3 — No implicit narrowing.** Do not restrict era, generation, region,
   or category unless the question states it. Recency bias is the known
   failure: older/less-famous entities are valid candidates. If you apply
   any narrowing, declare it explicitly in the report.
   **Era-sweep is mandatory for cultural-phenomenon clues** (a dance, a
   fashion, a meme, a catchphrase): the live search index over-represents
   recent entities, so a generic query will only surface the latest
   generation. Before fixing the candidate list, rerun the anchor clue with
   explicit era terms — at least one query with `원조`/`최초`/`시초` and one
   with an older decade qualifier (`2000년대`, `2010년대`). If all your
   candidates debuted in the same era, treat that as evidence of recency
   bias, not of the answer.
4. **M4 — Disconfirmation pass.** After converging on a final candidate, run
   at least one search that tries to find a DIFFERENT entity satisfying the
   anchor clue ("other groups famous for finger-touching choreography").
   Only finalize if the disconfirmation search fails to produce a rival.
5. **M5 — Weak-match flag.** If a clue only matches via reinterpretation or
   paraphrase (clue says "fingers touching each other", evidence says
   "piano-fingering dance"), mark that match WEAK in the matrix. Any WEAK
   match in the final candidate's row forbids `sufficient`.

**Bounded effort (the discipline must fit the time budget):**
- Cap enumeration at 3-5 candidates; one search per unverified matrix cell,
  and reuse one page's evidence across multiple cells whenever possible.
- Disconfirmation pass = 1-2 searches, no more.
- A complete shallow matrix beats deep verification of a single candidate:
  breadth first, then verify only the surviving candidate's weakest cells.

**Fallbacks (mandatory, in order):**
- Cannot enumerate 3 candidates → state it, proceed with what exists, and
  cap evidence status at `partial`.
- Disconfirmation finds a rival candidate → report the tie explicitly, run
  one more discriminating search on the strongest differing clue; if still
  tied, answer with both and mark `partial`.
- WEAK match remains on the chosen candidate → answer allowed, but
  evidence status MUST be `partial` with the weak clue named.
- Time budget runs low → report the matrix as-is (incomplete rows marked),
  never silently drop unchecked clues.

## Routing Quick-Reference

| Signal in query | Start at |
|-----------------|----------|
| General fact / docs / version | Tier 1 |
| Login-gated page, JS-rendered SPA, official page fetch failure | Tier 2 |
| X/Twitter, real-time, 실시간 | Tier 3 |
| Deep synthesis, multi-source comparison, 딥리서치 | Tier 3 (xhigh) or Tier 4 |

## Tier 1 — Built-in CLI Web Search

Your CLI's native `WebSearch` / `WebFetch` / `web_search` tool. No setup, fastest,
free. **Always try this first** unless the routing table above says otherwise.

### Good query practice

- Be specific: `"xAI grok-4.3 reasoning_effort parameter"` not `"grok api"`
- Retry with refined keywords if the first attempt is thin
- Verify freshness: check `publishedDate` in results
- Cite sources inline: `[title](url)`

### Korean source-sensitive searches

For Korean external/current/source-sensitive requests (`검색`, `찾아봐`,
`알아봐`, 공고, 정책, 가격, 후기, 순위, 목록, 표, 네이버 results), do not send
the full natural-language request as the only query.

1. Rewrite the request into 1-3 focused keyword queries.
2. Preserve anchor entities: official institution, brand/product, domain,
   current year/date, location, and document type.
3. Add source hints when useful: `공식`, `site:`, `공지사항`, `PDF`, `보도자료`,
   `후기`, `목록`, `표`, `랭킹`.
4. Run the active search/provider tool with those focused queries.
5. Treat results as URL candidates only.
6. Fetch/open the original page before final factual claims.
7. If the official/original URL is blocked, timed out, truncated, JS-rendered,
   a Naver shell/iframe, PDF binary, or a table/list that fetch cannot expose,
   run Tier 2 browser verification before relying on secondary sources.
8. Secondary sources are corroboration, not substitutes for the official source.
   If Tier 2 is not attempted after a primary-source fetch failure, mark the
   affected claims `browse-needed` or `insufficient`; do not call them
   `sufficient`.

If `agbrowse` is available, it may be used only as an optional planning helper:

```bash
agbrowse research plan --query "<request>" --json
```

Use `plan.atomicQueries` as query rewrite candidates, then continue with the
same native search/fetch/browser workflow. Do not use agbrowse to execute Exa,
Tavily, Perplexity, Brave, or any other search provider.

### When to escalate

- Results are empty, outdated, or blocked
- An official/primary URL exists but `WebFetch`/native fetch times out, returns
  403/empty/truncated content, or exposes only a JS shell
- A Naver/iframe/PDF/table/list/ranking page needs rendered source evidence
- You need to verify a specific source page before considering summaries,
  press articles, university reposts, or blogs

## Tier 2 — cli-jaw browser (CDP) + Adaptive Fetch Ladder

For pages that search APIs cannot reach: WAF-protected, login-gated,
JS-rendered, official portals, Naver shells/iframes, PDF/download flows, tables,
lists, or when you need to interact with a specific page.

`cli-jaw browser fetch <url>` runs the full adaptive-fetch escalation
internally. The agent does not need to manage the ladder manually — just call
`browser fetch` and the system tries each step automatically:
1. 23 platform-specific public endpoint resolvers (APIs, feeds, oEmbed)
2. Direct HTTP fetch
3. TLS fingerprint rotation (curl-impersonate, if installed)
4. Jina Reader r.jina.ai (default-on, opt-out with `--no-allow-third-party-reader`)
5. Browser render (Chromium CDP / Camoufox if installed)
6. DOM/table/structured extraction

The content-scorer picks the best result across all attempts. If all public
routes fail, the system reports the challenge type (CAPTCHA/login/paywall).

### Public-source reader routing map

Search may route known source classes toward `browser fetch` / adaptive-fetch
after candidate URLs exist. The browser side owns the reader ladder; this skill
only chooses when that lane is appropriate.

Candidate discovery itself should stay provider-neutral: rewrite the user
request into focused queries, use native search/provider results as candidate
URL discovery, then rank/dedupe candidates into lanes such as `official`,
`community`, `realtime`, `academic`, `package`, `archive`, and `fetch`. This
lane ranking must not execute browser fetch and must not turn `browser fetch`
into raw query search. Browser fetch reads or verifies known candidate URLs
only.

| Source class | Preferred reader lane |
| --- | --- |
| Official docs, government notices, PDFs | direct candidate URL fetch, then browser/PDF verification |
| GitHub repositories, releases, issues | official URL fetch, then `gh` or GitHub API only when needed |
| Package registries (`npm`, PyPI, crates, images) | registry JSON/API or official package page |
| Academic/library records (`arXiv`, CrossRef, OpenLibrary) | public API or canonical abstract/record URL |
| Forums and community pages (Reddit, HN, Stack Overflow, dev.to) | public JSON/RSS/API/readable page, then browser render |
| X/Twitter and fast social/current sources | search candidate discovery, public embed/syndication where available, then realtime tiers |
| Korean portals, Naver pages, blogs, rankings | candidate URL fetch, Naver/mobile/rendered DOM, table/list extraction |
| Media pages (YouTube, Vimeo, podcasts) | metadata/caption reader when available, then browser-visible page |
| Articles and commerce pages | public reader/metadata/JSON-LD, then browser main-content extraction |
| Archive-needed or removed pages | official/cache/archive candidate only when the live source is unavailable |

If a candidate requires login, payment, private membership, CAPTCHA solving, or
credentialed access, stop and report `browse-needed` or `insufficient`. Do not
frame public-source reading as bypassing authentication, paywalls, or private
content.

### Gate

```bash
cli-jaw browser status   # must show "connected"
```

If not connected: `cli-jaw browser start --agent`

**Declared need = execute.** `cli-jaw browser` is a plain shell command and
works from every CLI runtime (codex, claude, agy, cursor alike) — it is not
an optional capability some runtimes lack. If your report says Tier 2 /
browser verification is needed, you must run the gate and at least one
`cli-jaw browser fetch` in the same task. Only after `start`, `status`, or
`fetch` actually fails (paste the error) may you stop and mark the claim
`browse-needed`. Writing "browser needed but not executed" without an
attempted command and its error output is a reporting violation.

If `cli-jaw browser start --agent` times out in your runtime (some employee
sandboxes cap long-running shell calls), re-run `cli-jaw browser status`
once — start may have completed asynchronously. `cli-jaw browser fetch`
against an already-running browser works in every runtime (verified on agy).
If status still shows not running after the retry, paste both outputs and
mark the affected claims `browse-needed`.

### Verification workflow

Start Tier 2 after a candidate URL exists. Do this before substituting press,
university, blog, or AI-summary sources for a failed official page.

```bash
cli-jaw browser fetch "<url>" --json
cli-jaw browser open "<url>"
cli-jaw browser text
cli-jaw browser snapshot --interactive
cli-jaw browser get-dom --selector "<selector>" --max-chars 4000 --json
```

For search verification, prefer `cli-jaw browser fetch <url> --json` first, then
open/text/snapshot/get-dom only as needed. Do not use browser snippets as a
replacement for source evidence.

Adaptive fetch can read a known URL or a search-result URL. It does not
discover the URL candidate set by itself. If the input is only a natural
language query, return to Tier 1 query rewriting first.

### Evidence rule

- If Tier 2 confirms the official/original source, mark the claim `sufficient`.
- If Tier 2 fails or cannot be run, mark that specific claim `browse-needed` or
  `insufficient`.
- Secondary sources may support context, but they do not upgrade a failed
  official-source claim to `sufficient`.

Evidence status:

- `sufficient`: at least one original/primary URL was opened or fetched and
  supports the claim.
- `partial`: candidate evidence exists, but one or more important constraints
  remain weak or secondary.
- `browse-needed`: a candidate primary URL exists but browser/fetch
  verification was needed and could not be completed.
- `insufficient`: no credible candidate evidence was obtained.

Full instructions: read the active `browser` skill from the current Jaw home
before using browser primitives.

### When to escalate

- You have browser-confirmed raw page content but need deeper synthesis over it
- The query is about X/Twitter content or fast-moving real-time discussion
- Browser verification cannot reach the source and you need another search
  perspective

## Tier 3 — progrok (Grok OAuth Search)

AI-powered web+X search via the user's Grok OAuth token. No API key, no proxy.
Returns an AI summary with inline citations.

### Gate

```bash
progrok status   # must print "Logged in" and exit 0
```

If not logged in → skip to Tier 4. Do not block on login flow.

### Commands

```bash
# Standard search (web + X, grok-4.3, fast)
progrok search "<query>"

# Source filtering
progrok search "<query>" --web       # web only
progrok search "<query>" --x         # X/Twitter only

# Structured output for parsing
progrok search "<query>" --json

# Deep research mode (grok-4.20-multi-agent, 16 agents, slow)
progrok search "<query>" \
  --model grok-4.20-multi-agent-0309 \
  --reasoning xhigh
```

### Reasoning effort levels

| Level | Model | Behavior |
|-------|-------|----------|
| none | grok-4.3 | No reasoning, near-instant |
| low (default) | grok-4.3 | Light reasoning, fast |
| medium | grok-4.3 | Moderate depth |
| high | grok-4.3 | Deep reasoning, slower |
| xhigh | grok-4.20-multi-agent-0309 | 16 parallel agents, deep research grade |

Use `--reasoning xhigh` + `--model grok-4.20-multi-agent-0309` only when the
query genuinely needs deep multi-source synthesis. It is slow and expensive.

### Output handling

- Always include source URLs from the `citations` array in your answer
- With `--json`: parse the structured result for programmatic use
- Check `usage.server_side_tool_usage_details` for search call counts

## Tier 4 — web-ai (Grok Expert / GPT Pro)
### Long-running Tier 4 queries → bgtask

If the Tier 4 query uses a heavy model (GPT Pro, Deep Think, Deep Research)
and may run for many minutes, do not block the turn on `query`. Use
`cli-jaw browser web-ai send` to get the sessionId, then
`cli-jaw bgtask add --preset web-ai --session "$SID"` and end the turn —
the jaw server re-invokes the boss with a `[bgtask:*]` prompt on completion.
Details: active `web-ai` skill "Long-Running Queries — bgtask" section.


Drive grok.com or chatgpt.com through browser control for complex synthesis that
raw search cannot produce. Slowest tier, most capable.

### Gate

```bash
cli-jaw browser web-ai status --vendor grok    # or chatgpt
```

### Structured question format

Build queries using this envelope for best results:

```text
[SYSTEM]
You are a research analyst with expertise in <domain>.

[USER]
## Goal
<What you need answered — one clear objective>

## Context
<Background the AI needs: prior findings, constraints, domain>

## Question
<Specific question(s), numbered if multiple>

## Output
<Desired format: bullet summary, comparison table, pros/cons, etc.>

## Constraints
- Cite primary sources with URLs
- Distinguish confirmed facts from inference
- Flag information older than <date> as potentially stale
```

### Commands

```bash
# Quick inline query
cli-jaw browser web-ai query --vendor grok \
  --inline-only \
  --require-source-audit \
  --prompt "<structured question>"

# With source context from files
cli-jaw browser web-ai query --vendor chatgpt \
  --prompt "<question>" \
  --context-from-files "src/**/*.ts"

# Long-running deep think (up to 20min)
cli-jaw browser web-ai query --vendor chatgpt \
  --prompt "<complex question>" \
  --timeout 1200
```

Full instructions: read the active `web-ai` skill from the current Jaw home
before driving hosted AI providers.

## Rules

1. **Order is mandatory.** Cheaper/faster first; escalate only on failure or routing table override.
2. **Never silently chain.** If a tier errors, report what failed before escalating.
3. **Always cite sources.** Every factual claim needs a URL.
4. **Fail fast with tier-specific gates.** For Tier 2 browser, if `browser status`
   is not connected, run `cli-jaw browser start --agent` and retry
   status/fetch once. Skip Tier 2 only if browser start, status, or fetch still
   fails; report the failure and mark affected claims `browse-needed` or
   `insufficient`. For Tier 3 progrok, if `progrok status` is not logged in,
   skip that tier and report.
5. **Match effort to query.** Don't use xhigh/Tier 4 for a simple version check.
6. **No `sufficient` on snippets alone.** At least one primary/original source
   must be actually fetched/opened before any claim is marked `sufficient` —
   snippet agreement across many sources does not count.
7. **No "browser needed but not executed".** If you state Tier 2 is needed,
   run it; stop at `browse-needed` only with a pasted command failure.

## Answer Discipline

For search tasks that need comparison or audit, make the answer easy to verify:

- state the rewritten query terms or local-search rationale;
- identify candidate URLs separately from pages that were actually opened or
  fetched;
- explain whether browser verification was needed and which browser command was
  used when it was;
- label the evidence status for each important claim;
- call out unresolved uncertainty and the next source that would resolve it.

Command-specific field names, output schema, and UX wording belong in the
calling workflow such as `/search`, not in this standalone skill.
