---
name: notion
description: Notion API for creating and managing pages, databases, and blocks.
homepage: https://developers.notion.com
metadata:
  {
    "openclaw":
      { "emoji": "📝", "requires": { "env": ["NOTION_API_KEY"] }, "primaryEnv": "NOTION_API_KEY" },
  }
---

# notion

Create, read, and update Notion pages, data sources (databases), and blocks via the API.

## Setup

- API key (`ntn_` prefix) stored at `~/.config/notion/api_key`
- Load: `NOTION_KEY=$(cat ~/.config/notion/api_key)`
- Target pages/databases must be shared with the integration

## API Basics

```bash
NOTION_KEY=$(cat ~/.config/notion/api_key)

# Helper — all examples below use this
notion_api() {
  local method=$1 endpoint=$2 data=$3
  curl -s -X "$method" "https://api.notion.com/v1$endpoint" \
    -H "Authorization: Bearer $NOTION_KEY" \
    -H "Notion-Version: 2025-09-03" \
    -H "Content-Type: application/json" \
    ${data:+-d "$data"}
}
```

API version `2025-09-03` (latest). Databases are called "data sources" in this version.

## Common Operations

```bash
# Search
notion_api POST /search '{"query": "page title"}'

# Get page
notion_api GET /pages/{page_id}

# Get page content (blocks)
notion_api GET /blocks/{page_id}/children

# Create page in a data source
notion_api POST /pages '{
  "parent": {"database_id": "xxx"},
  "properties": {
    "Name": {"title": [{"text": {"content": "New Item"}}]},
    "Status": {"select": {"name": "Todo"}}
  }
}'

# Query a data source
notion_api POST /data_sources/{data_source_id}/query '{
  "filter": {"property": "Status", "select": {"equals": "Active"}},
  "sorts": [{"property": "Date", "direction": "descending"}]
}'

# Create a data source
notion_api POST /data_sources '{
  "parent": {"page_id": "xxx"},
  "title": [{"text": {"content": "My Database"}}],
  "properties": {
    "Name": {"title": {}},
    "Status": {"select": {"options": [{"name": "Todo"}, {"name": "Done"}]}},
    "Date": {"date": {}}
  }
}'

# Update page properties
notion_api PATCH /pages/{page_id} \
  '{"properties": {"Status": {"select": {"name": "Done"}}}}'

# Add blocks to page
notion_api PATCH /blocks/{page_id}/children '{
  "children": [
    {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello"}}]}}
  ]
}'
```

## Property Types

- **Title:** `{"title": [{"text": {"content": "..."}}]}`
- **Rich text:** `{"rich_text": [{"text": {"content": "..."}}]}`
- **Select:** `{"select": {"name": "Option"}}`
- **Multi-select:** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **Date:** `{"date": {"start": "2024-01-15", "end": "2024-01-16"}}`
- **Checkbox:** `{"checkbox": true}`
- **Number:** `{"number": 42}`
- **URL:** `{"url": "https://..."}`
- **Email:** `{"email": "a@b.com"}`
- **Relation:** `{"relation": [{"id": "page_id"}]}`

## 2025-09-03 API Changes

- **Databases → Data Sources:** Use `/data_sources/` endpoints for queries
- **Two IDs per database:** `database_id` (for creating pages) and `data_source_id` (for querying)
- **Search results:** Databases return as `"object": "data_source"`
- **Page responses:** Include both `parent.data_source_id` and `parent.database_id`

## Environment

- Key location: `~/.config/notion/api_key` (also `~/.config/notion/access_token`)
- OAuth config: `~/.config/notion/oauth.env`
- Discover workspace page IDs via `notion_api POST /search '{"query": "page name"}'`

## Visual Design Rules (미감 가이드)

### 1. Use mention links for page references
Mention links create backlinks and show page icons automatically.

```json
// ✓ mention
{"type": "mention", "mention": {"type": "page", "page": {"id": "페이지-UUID"}}}

// ✗ plain text
{"type": "text", "text": {"content": "페이지 이름"}}
```

### 2. Skip emoji in text when using mentions
Mentions display the page icon automatically — adding emoji causes duplication.

### 3. Use callout + mention for navigation hubs

```json
{"object": "block", "type": "callout", "callout": {
    "rich_text": [
        {"type": "mention", "mention": {"type": "page", "page": {"id": "대시보드-UUID"}}},
        {"type": "text", "text": {"content": " · "}},
        {"type": "mention", "mention": {"type": "page", "page": {"id": "운영-UUID"}}}
    ],
    "icon": {"type": "emoji", "emoji": "🏠"},
    "color": "gray_background"
}}
```

### 4. Preserve child_page blocks
Deleting `child_page` blocks archives subpages permanently. Always filter them out:

```python
for block in children:
    if block["type"] != "child_page":
        delete_block(block["id"])
```

### 5. Page structure pattern

```
callout (intro/slogan) + color_background
divider
heading_2 (section)
callout (mention links) + gray_background  ← navigation
divider
heading_2 (Quick Links)
bulleted_list_item (mention → description)
```

### 6. Icons & covers
- Set a meaningful emoji icon on every page
- Add Unsplash cover images on key pages (w=1500)

### 7. Mention caveats
- Archived pages render mentions as plain text
- Integration needs access to the target page
- Rate limit: ~3 req/s — use `time.sleep(0.35)`

## Notes

- Page/database IDs are UUIDs (dashes optional)
- Database view filters are UI-only (not settable via API)
- Use `is_inline: true` to embed data sources in pages
