---
name: notion-research-documentation
description: Research across Notion and synthesize into structured documentation; use when gathering info from multiple Notion sources to produce briefs, comparisons, or reports with citations.
metadata:
  short-description: Research Notion content and produce briefs/reports
---

# Research & Documentation

Pull Notion pages, synthesize findings, and publish cited briefs or reports.

Why this skill? Notion knowledge is scattered across pages. Without systematic search + citation, research outputs miss context or make unsourced claims.

## Notion MCP setup (only if MCP calls fail)
1. `codex mcp add notion --url https://mcp.notion.com/mcp`
2. Set `[features].rmcp_client = true` in `config.toml`
3. `codex mcp login notion` — then restart Codex.

## Rules

1. **Search broadly, then narrow**: use `Notion:notion-search` with multiple query variations. Ask the user to confirm scope when results are ambiguous.
2. **Track every source**: record each fetched page's URL/ID. Use direct quotes for critical facts. Why: unsourced claims in research docs erode trust.
3. **Choose format by purpose**:
   - Quick readout → brief (1 page, key points only)
   - Single-topic dive → summary (findings + evidence)
   - Option tradeoffs → comparison (structured pros/cons/criteria table)
   - Deep dive / exec-ready → comprehensive report (full sections + recommendations)
4. **Outline before writing**: group findings by themes or questions. Flag gaps and contradictions explicitly.
5. **Create in Notion** via `Notion:notion-create-pages`. Every doc must include: title, summary, key findings, supporting evidence, inline citations, and a references section linking source pages.
6. **Finalize**: add highlights, risks, open questions. Create follow-up tasks if needed. Use `Notion:notion-update-page` for updates.
