# Native Web UI Structured Renderers

Use these fences before reaching for SVG, Mermaid, or `diagram-html` when the content matches a native card. Native renderers are final-answer-only: emit complete JSON in the final response, never partial JSON during streaming, and never include secrets or hidden internal state.

## Routing

| Intent | Fence | Use when | Avoid when |
|---|---|---|---|
| Search results, citations, source lists | `search-results` | You have public URLs and short snippets | The user asked for prose only, or URLs are private/local |
| Draft email/message/document | `compose-block` | The user needs editable copy | You only need a short plain-text sentence |
| Filter/sort/page/copy table data | `dataframe` | Rows and columns matter | The answer is a tiny 2-3 row comparison best handled in Markdown |
| Simple chart | `chart-json` | One numeric series, bar/line/pie | Multi-series, maps, advanced interaction, custom JS |
| Patch display | `diff` or raw unified diff | Showing file changes | Explaining architecture or process flow |

If the current channel cannot render Web UI widgets, fall back to plain Markdown.

## `compose-block`

Do not invent shorthand such as `{ "type": "...", "title": "...", "body": "..." }`. The renderer expects `schemaVersion`, `kind`, and at least one valid `variants[].body`.

```compose-block
{
  "schemaVersion": "compose-block-v1",
  "kind": "email",
  "title": "Client follow-up",
  "subject": "Re: Project Update",
  "variants": [
    {
      "id": "polite",
      "label": "Polite",
      "subject": "Re: Project Update",
      "body": "Hi team,\n\nFollowing up on yesterday's discussion..."
    }
  ]
}
```

Rules:

- `schemaVersion` must be `"compose-block-v1"`.
- `kind` is `email`, `message`, `document`, or `other`; `textMessage` normalizes to `message`.
- `variants` must contain 1-3 valid items.
- Each valid variant needs a non-empty `body`.
- Put body text inside `variants[].body`, not top-level `body`.

## `search-results`

```search-results
{
  "schemaVersion": "search-results-v1",
  "query": "cli-jaw structured renderer cards",
  "results": [
    {
      "title": "Result title",
      "url": "https://example.com/page",
      "snippet": "Short supporting excerpt or summary.",
      "source": "example.com"
    }
  ]
}
```

Rules:

- `schemaVersion` must be `"search-results-v1"`.
- URLs must be public `http` or `https`; localhost/private/credential URLs are dropped.
- `url` or `link` is accepted.
- `snippet` or `description` is accepted.
- Results are deduped and capped at 10.

## `dataframe`

```dataframe
{
  "schemaVersion": "dataframe-v1",
  "title": "Sales",
  "columns": ["Month", "Revenue"],
  "types": ["string", "number"],
  "rows": [
    ["Jan", 10],
    ["Feb", 30]
  ],
  "pageSize": 25
}
```

Rules:

- `schemaVersion` must be `"dataframe-v1"`.
- `columns` must contain at least one column.
- `rows` is preferred; `data` is accepted as an alias.
- Supported `types`: `string`, `number`, `boolean`, `date`, `json`.
- Keep to 20 columns, 500 rows, and short cell text.

## `chart-json`

```chart-json
{
  "schemaVersion": "chart-json-v1",
  "type": "bar",
  "title": "Revenue",
  "description": "Quarterly revenue",
  "labels": ["Q1", "Q2", "Q3"],
  "data": [10, 30, 20]
}
```

Rules:

- `schemaVersion` must be `"chart-json-v1"`.
- `type` is `bar`, `line`, or `pie`.
- `labels.length` and `data.length` must match enough to produce at least one point.
- Data is one numeric series, capped at 24 points.
- Use `diagram-html` with Chart.js/ECharts/D3 for multi-series, advanced charts, maps, sankey, heatmap, treemap, gauge, custom JS, or richer interactivity.

## `diff`

Use a `diff` fence or plain unified diff. The renderer can also auto-detect no-language unified diffs.

```diff
diff --git a/file.ts b/file.ts
--- a/file.ts
+++ b/file.ts
@@
-old
+new
```

Do not wrap diffs in SVG, Mermaid, `dataframe`, or `diagram-html` unless the user asked for a conceptual explanation rather than a patch display.
