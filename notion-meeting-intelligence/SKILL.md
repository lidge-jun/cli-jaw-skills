---
name: notion-meeting-intelligence
description: Prepare meeting materials with Notion context and Codex research; use when gathering context, drafting agendas/pre-reads, and tailoring materials to attendees.
metadata:
  short-description: Prep meetings with Notion context and tailored agendas
---

# Meeting Intelligence

Prep meetings by pulling Notion context, tailoring agendas/pre-reads, and enriching with Codex research.

## Notion MCP setup (only if MCP calls fail)
1. `codex mcp add notion --url https://mcp.notion.com/mcp`
2. Set `[features].rmcp_client = true` in `config.toml`
3. `codex mcp login notion` — then restart Codex.

## Rules

1. **Confirm inputs first**: get objective, desired outcomes/decisions, attendees, duration, and date/time before searching.
2. **Pull context**: search with `Notion:notion-search`, fetch with `Notion:notion-fetch` — look for prior notes, specs, OKRs, action items.
3. **Choose format by meeting type**:
   - Status/update → status format
   - Decision/approval → decision format
   - Planning (sprint/project) → planning format
   - Retro/feedback → retrospective format
   - 1:1 → one-on-one format
   - Ideation → brainstorming format
4. **Draft in Notion** via `Notion:notion-create-pages`. Every agenda must include: context block, goals, per-item owner + timebox, decisions needed, risks, and prep asks. Link source Notion pages.
5. **Enrich with research**: add Codex-sourced facts, benchmarks, or risks where relevant. Cite every claim with a source link; separate fact from opinion.
6. **Finalize**: add next steps with owners. Create follow-up tasks in the relevant Notion database if needed. Use `Notion:notion-update-page` for subsequent changes.
