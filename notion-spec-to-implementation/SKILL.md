---
name: notion-spec-to-implementation
description: Turn Notion specs into implementation plans, tasks, and progress tracking; use when implementing PRDs/feature specs and creating Notion plans + tasks from them.
metadata:
  short-description: Turn Notion specs into implementation plans, tasks, and progress tracking
---

# Spec to Implementation

Convert a Notion spec into linked implementation plans, tasks, and ongoing status updates.

## Notion MCP setup (only if MCP calls fail)
1. `codex mcp add notion --url https://mcp.notion.com/mcp`
2. Set `[features].rmcp_client = true` in `config.toml`
3. `codex mcp login notion` — then restart Codex.

## Rules

### 1) Read the spec
- Search with `Notion:notion-search`; if multiple hits, ask the user which to use.
- Fetch with `Notion:notion-fetch`. Extract: requirements, acceptance criteria, constraints, priorities.
- Record gaps and assumptions in a clarifications block before proceeding. Why: unrecorded assumptions cause scope drift during implementation.

### 2) Create the plan
- Simple change (single component, no cross-team dependency) → single-page plan.
- Multi-phase feature or migration → phased plan with milestones.
- Create via `Notion:notion-create-pages`. Include: overview, linked spec, requirements summary, phases, dependencies/risks, and success criteria.

### 3) Create tasks
- Find the task database via `Notion:notion-search` → `Notion:notion-fetch` to confirm schema and required properties.
- **Size to 1–2 days** per task. Why: tasks larger than 2 days hide progress and make blockers invisible; smaller than 1 day creates overhead that outweighs tracking value.
- Each task must have: action-verb title, context sentence, acceptance criteria, dependencies, and relations to spec + plan.
- Set properties: status, priority, due date/story points/assignee when provided.

### 4) Link artifacts
- Plan links to spec; each task links to both plan and spec.
- Optionally add an "Implementation" section in the spec pointing to the plan via `Notion:notion-update-page`.

### 5) Track progress
- Update task status and plan checklists as work progresses. Note blockers and decisions.
- Post milestone summaries when closing a phase.
