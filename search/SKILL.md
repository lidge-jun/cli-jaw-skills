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

## Tier 2 — cli-jaw browser (CDP)

For pages that search APIs cannot reach: WAF-protected, login-gated,
JS-rendered, official portals, Naver shells/iframes, PDF/download flows, tables,
lists, or when you need to interact with a specific page.

### Gate

```bash
cli-jaw browser status   # must show "connected"
```

If not connected: `cli-jaw browser start --agent`

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

### Evidence rule

- If Tier 2 confirms the official/original source, mark the claim `sufficient`.
- If Tier 2 fails or cannot be run, mark that specific claim `browse-needed` or
  `insufficient`.
- Secondary sources may support context, but they do not upgrade a failed
  official-source claim to `sufficient`.

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
