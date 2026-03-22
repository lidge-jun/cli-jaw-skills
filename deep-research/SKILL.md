---
name: deep-research
description: Run autonomous multi-step research via Google Gemini Deep Research Agent. Produces cited reports from web sources.
license: Apache-2.0
metadata:
  author: sanjay3290
  version: "1.0"
---

# Gemini Deep Research

Autonomous research agent that plans searches, reads sources, and synthesizes cited reports.

## When to Use

- Questions requiring synthesis across many sources (market analysis, literature reviews, competitive landscape)
- Due diligence or technical research where breadth matters more than speed
- NOT for quick factual lookups (use `search` skill instead)

Trade-off: higher cost and latency in exchange for comprehensive, cited coverage.

## Requirements

- Python 3.8+, httpx (`pip install -r requirements.txt`)
- `GEMINI_API_KEY` environment variable

## CLI Reference

```bash
python3 scripts/research.py --query "..." [options]
```

| Flag | Effect |
|------|--------|
| `--query "..."` | Research question (required for new tasks) |
| `--format "..."` | Output structure template |
| `--stream` | Stream progress in real-time |
| `--no-wait` | Start task and return immediately |
| `--status <id>` | Check status of a running task |
| `--wait <id>` | Block until task completes |
| `--continue <id>` | Follow-up on previous research |
| `--list` | List recent research tasks |
| `--json` | Output as structured JSON |
| `--raw` | Output raw API response |

## Cost and Latency

Costs and times vary by query complexity and source count. Expect minutes, not seconds. Check actual token usage in the output metadata for accurate billing.

## Exit Codes

- **0**: Success
- **1**: Error (API, config, or timeout)
- **130**: Cancelled (Ctrl+C)

---

## MCP-Based Web Research

When firecrawl or exa MCP servers are available, use them as complementary search sources alongside the Gemini agent.

### Available MCP Tools

| Server | Tools | Best For |
|--------|-------|----------|
| firecrawl | `firecrawl_search`, `firecrawl_scrape`, `firecrawl_crawl` | Broad web search, full-page scraping |
| exa | `web_search_exa`, `web_search_advanced_exa`, `crawling_exa` | Semantic search, date-filtered results |

### Multi-Source Search Strategy

For each research sub-question:
1. Use 2–3 keyword variations per sub-question.
2. Search with each available tool (firecrawl + exa for best coverage).
3. Deep-read 3–5 key sources with `firecrawl_scrape` or `crawling_exa` — search snippets alone are insufficient.
4. Aim for 15–30 unique sources across all sub-questions.

Source priority: academic papers, official docs > reputable news > blogs > forums.

### Date-Filtered Search (exa)

```
web_search_advanced_exa(query: "...", numResults: 5, startPublishedDate: "2025-01-01")
```

Use date filters for fast-moving topics (AI, policy, markets).

## Report Format

```markdown
# [Topic]: Research Report
*Generated: [date] | Sources: [N] | Confidence: [High/Medium/Low]*

## Executive Summary
[3–5 sentence overview of key findings]

## 1. [Theme]
[Findings with inline citations]
- Key point ([Source](url))
- Supporting data ([Source](url))

## 2. [Theme]
...

## Key Takeaways
- [Actionable insight 1]
- [Actionable insight 2]

## Sources
1. [Title](url) — [one-line summary]
2. ...

## Methodology
Searched [N] queries across [tools used]. Analyzed [M] sources.
Sub-questions: [list]
```

Short topics: deliver full report inline. Long reports: executive summary + key takeaways inline, full report saved to file.

## Multi-Source Triangulation

1. **Every claim needs a source.** No unsourced assertions.
2. **Cross-reference**: if only one source says it, flag as unverified.
3. **Recency**: prefer sources from the last 12 months for fast-moving topics.
4. **Acknowledge gaps**: if a sub-question has poor coverage, say so explicitly.
5. **Separate fact from inference**: label estimates, projections, and opinions clearly.

## Parallel Research with Subagents

For broad topics, launch parallel explore/research agents per sub-question cluster:
- Agent 1: sub-questions 1–2
- Agent 2: sub-questions 3–4
- Agent 3: cross-cutting themes + synthesis prep

Each agent searches, reads sources, and returns structured findings. The main session synthesizes into the final report.
