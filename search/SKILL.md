---
name: search
description: "Unified search hub. Route any web/real-time/X lookup through a 4-tier escalation: built-in web search → progrok Grok OAuth → cli-jaw browser CDP → web-ai (Grok Expert / GPT Pro). Use for: search, 검색, web search, latest news, real-time info, X/Twitter, fact lookup, deep research."
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
| X/Twitter, real-time, 실시간 | Tier 2 |
| Login-gated page, JS-rendered SPA | Tier 3 |
| Deep synthesis, multi-source comparison, 딥리서치 | Tier 2 (xhigh) or Tier 4 |

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
7. If the original is blocked, truncated, JS-rendered, a Naver shell/iframe,
   PDF binary, or a table/list that fetch cannot expose, mark the answer
   `browse-needed` or `insufficient` and escalate to Tier 3.

If `agbrowse` is available, it may be used only as an optional planning helper:

```bash
agbrowse research plan --query "<request>" --json
```

Use `plan.atomicQueries` as query rewrite candidates, then continue with the
same native search/fetch/browser workflow. Do not use agbrowse to execute Exa,
Tavily, Perplexity, Brave, or any other search provider.

### When to escalate

- Results are empty, outdated, or blocked
- You need an AI-synthesized summary with citations
- The query is about X/Twitter content
- You need deeper reasoning over multiple sources

## Tier 2 — progrok (Grok OAuth Search)

AI-powered web+X search via the user's Grok OAuth token. No API key, no proxy.
Returns an AI summary with inline citations.

### Gate

```bash
progrok status   # must print "Logged in" and exit 0
```

If not logged in → skip to Tier 3. Do not block on login flow.

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

## Tier 3 — cli-jaw browser (CDP)

For pages that search APIs cannot reach: WAF-protected, login-gated, JS-rendered,
or when you need to interact with a specific page.

### Gate

```bash
cli-jaw browser status   # must show "connected"
```

If not connected: `cli-jaw browser start --agent`

### Workflow

```bash
cli-jaw browser navigate "<url>"
cli-jaw browser snapshot --interactive   # get ref IDs (reset on navigation)
cli-jaw browser click <ref>
cli-jaw browser type <ref> "<text>" --submit
```

Full instructions: read `/Users/jun/.cli-jaw-3463/skills/browser/SKILL.md`

For search verification, Tier 3 starts after a candidate URL exists. Prefer
`cli-jaw browser fetch <url> --json` or browser open/text/snapshot commands to
inspect the original source. Do not use browser snippets as a replacement for
source evidence.

### When to escalate

- You have raw page content but need deep reasoning/synthesis over it
- Multiple pages need cross-referencing with expert-level analysis

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

Full instructions: read `/Users/jun/.cli-jaw-3463/skills/web-ai/SKILL.md`

## Rules

1. **Order is mandatory.** Cheaper/faster first; escalate only on failure or routing table override.
2. **Never silently chain.** If a tier errors, report what failed before escalating.
3. **Always cite sources.** Every factual claim needs a URL.
4. **Fail fast.** If a gate check fails (progrok not logged in, browser not connected), skip that tier and report.
5. **Match effort to query.** Don't use xhigh/Tier 4 for a simple version check.
