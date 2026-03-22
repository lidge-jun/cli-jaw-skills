---
name: exa-search
description: Neural search via Exa MCP for web, code, and company research.
---

# Exa Search

Neural search for web content, code, companies, and people via the Exa MCP server.

## When to Use

- Current web information or news needed
- Searching for code examples, API docs, or technical references
- Researching companies, competitors, or market players
- Finding professional profiles or people in a domain
- Background research for development tasks

## MCP Requirement

Exa MCP server must be configured. Example MCP config:

```json
"exa-web-search": {
  "command": "npx",
  "args": ["-y", "exa-mcp-server"],
  "env": { "EXA_API_KEY": "${EXA_API_KEY}" }
}
```

Get an API key at [exa.ai](https://exa.ai).
Verify the exact tool names your Exa server exposes before depending on them.

## Core Tools

### web_search_exa
General web search for current information, news, or facts.

```
web_search_exa(query: "latest AI developments 2026", numResults: 5)
```

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `query` | string | required | Search query |
| `numResults` | number | 8 | Number of results |
| `type` | string | `auto` | Search mode |
| `livecrawl` | string | `fallback` | Prefer live crawling when needed |
| `category` | string | none | Optional: `company`, `research paper`, etc. |

### get_code_context_exa
Find code examples and documentation from GitHub, Stack Overflow, and docs sites.

```
get_code_context_exa(query: "Python asyncio patterns", tokensNum: 3000)
```

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `query` | string | required | Code or API search query |
| `tokensNum` | number | 5000 | Content tokens (1000–50000) |

## Usage Patterns

### Quick Lookup
```
web_search_exa(query: "Node.js 22 new features", numResults: 3)
```

### Code Research
```
get_code_context_exa(query: "Rust error handling patterns Result type", tokensNum: 3000)
```

### Company or People Research
```
web_search_exa(query: "Vercel funding valuation 2026", numResults: 3, category: "company")
web_search_exa(query: "site:linkedin.com/in AI safety researchers Anthropic", numResults: 5)
```

## Tips

- Use `web_search_exa` for current information, company lookups, and broad discovery
- Use search operators like `site:`, quoted phrases, and `intitle:` to narrow results
- Lower `tokensNum` (1000–2000) for focused code snippets, higher (5000+) for comprehensive context
- Use `get_code_context_exa` for API usage or code examples rather than general web pages

## Related Skills

- `deep-research` — full research workflow using firecrawl + exa together
