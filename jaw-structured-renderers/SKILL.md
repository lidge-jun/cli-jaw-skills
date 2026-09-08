---
name: jaw-structured-renderers
description: "Native Web UI structured renderer schemas for compose-block drafts, search-results cards, dataframe tables, chart-json charts, and diff output"
metadata:
  version: "1.0.0"
capabilities:
  - "compose-block: editable email, message, and document draft cards"
  - "search-results: source/result cards with public URLs"
  - "dataframe: filterable, sortable, pageable row/column data"
  - "chart-json: simple single-series bar, line, and pie charts"
  - "diff: native patch display for unified diffs"
references:
  - "schemas.md — canonical JSON schemas and examples"
---

# Structured Renderers Skill

Use this skill before emitting native Web UI structured fences:

- `compose-block`
- `search-results`
- `dataframe`
- `chart-json`
- `diff`

These are final-answer-only renderer contracts. Emit complete JSON only in the final assistant response, never partial JSON during streaming, and never include secrets, hidden chain-of-thought, credentials, local-only URLs, or internal state.

## When To Use

Use the smallest native renderer that matches the answer:

| Intent | Fence |
|---|---|
| Search results, source cards, citations with URLs | `search-results` |
| Editable email, message, or document drafts | `compose-block` |
| Filterable/sortable/pageable row data | `dataframe` |
| Simple single-series bar, line, or pie chart | `chart-json` |
| File patch or unified diff display | `diff` or raw unified diff |

If the current channel cannot render Web UI widgets, fall back to clear Markdown.

## Required Schema Check

Before emitting a structured fence, read `references/schemas.md` and match the exact schema for the fence.

Important drift guards:

- `compose-block` requires `schemaVersion: "compose-block-v1"`, `kind`, and `variants[]`.
- Never emit shorthand `compose-block` objects such as `{ "type": "...", "title": "...", "body": "..." }`.
- Put draft text in `variants[].body`, `variants[].paragraphs`, or `variants[].bodyLines`; top-level `body` is not the editable draft body.
- Renderer fences must contain strict JSON, not JavaScript-like object literals.
- Never put raw literal line breaks inside quoted JSON string values. For multiline draft text, use escaped newlines like `\\n` or `\\n\\n` inside `variants[].body`.
- For multiline drafts, prefer `variants[].paragraphs: string[]` (joined with blank lines) or `variants[].bodyLines: string[]` (joined with single line breaks) so no newline escape is needed inside JSON strings.
- For long single-string drafts, prefer JSON produced by `JSON.stringify` or compact JSON so every newline inside string content is escaped.
- `search-results`, `dataframe`, and `chart-json` also require their `*-v1` `schemaVersion`.
- Use `diagram-html` instead of `chart-json` for multi-series charts, maps, advanced chart types, external libraries, or custom JavaScript.

## Relationship To Diagram

`diagram` owns SVG, Mermaid, maps, advanced chart widgets, interactive visualizations, and `diagram-html`.

This skill owns native non-diagram Web UI renderer schemas. For simple charts, prefer `chart-json`; for advanced charts or custom interaction, load `diagram` and use `diagram-html`.
