---
name: notion-knowledge-capture
description: Capture conversations and decisions into structured Notion pages; use when turning chats/notes into wiki entries, how-tos, decisions, or FAQs with proper linking.
metadata:
  short-description: Capture conversations into structured Notion pages
---

# Knowledge Capture

Convert conversations and notes into structured, linkable Notion pages for easy reuse.

## Notion MCP setup (only if MCP calls fail)
1. `codex mcp add notion --url https://mcp.notion.com/mcp`
2. Set `[features].rmcp_client = true` in `config.toml`
3. `codex mcp login notion` — then restart Codex.

## Rules

### 1) Classify the capture
- Ask: purpose, audience, freshness, and new-or-update.
- Content types: **decision**, **how-to**, **FAQ**, **wiki entry**, **learning note**, **documentation page**.

### 2) Find the target database
- Search with `Notion:notion-search`, then fetch with `Notion:notion-fetch` to confirm the database schema.
- Required properties to verify before creating pages:
  - **All types**: title, tags, owner, status, created date
  - **Decisions**: additionally need: alternatives (rich text), outcome (select), rationale (rich text)
  - **How-tos**: additionally need: prerequisites (rich text), steps (rich text)
  - **FAQs**: additionally need: question (title), answer (rich text)
- If multiple candidate databases exist, ask the user. Otherwise use the primary wiki/docs DB.

### 3) Extract and structure
- **Decisions**: record alternatives considered, rationale, and outcome.
- **How-tos**: capture steps, prerequisites, links to assets/code, and edge cases.
- **FAQs**: phrase as Q&A with concise answers; link to deeper docs.
- **Wiki/docs**: summarize the concept, add context, and link related pages.

### 4) Create in Notion
- Use `Notion:notion-create-pages` with the database's `data_source_id`. Set all verified properties.
- If updating an existing page, fetch first, then edit via `Notion:notion-update-page`.

### 5) Link and surface
- Add relations/backlinks to hub pages and related records.
- Include a summary for future readers. Create follow-up tasks if needed.
