---
name: mcp-builder
description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
license: Complete terms in LICENSE.txt
---

# MCP Server Development Guide

Create MCP servers that enable LLMs to interact with external services. Quality is measured by how well the server enables LLMs to accomplish real-world tasks.

## Phase 1: Research and Planning

### 1.1 Design Principles

- **API coverage vs. workflow tools**: prioritize comprehensive API endpoint coverage; add workflow tools for common multi-step operations. When uncertain, prefer coverage.
- **Tool naming**: use consistent prefixes and action-oriented names (e.g., `github_create_issue`, `github_list_repos`)
- **Context management**: return focused, relevant data; support filtering and pagination
- **Error messages**: include specific suggestions and next steps to guide the agent toward solutions

### 1.2 Study MCP Protocol

Start with the sitemap: `https://modelcontextprotocol.io/sitemap.xml`
Fetch pages with `.md` suffix for markdown (e.g., `https://modelcontextprotocol.io/specification/draft.md`).

Key areas: specification overview, transport mechanisms (streamable HTTP, stdio), tool/resource/prompt definitions.

### 1.3 Framework Documentation

**Recommended stack**: TypeScript with streamable HTTP (remote) or stdio (local).

| Resource | Location |
|----------|----------|
| MCP Best Practices | [reference/mcp_best_practices.md](./reference/mcp_best_practices.md) |
| TypeScript Guide | [reference/node_mcp_server.md](./reference/node_mcp_server.md) |
| Python Guide | [reference/python_mcp_server.md](./reference/python_mcp_server.md) |
| TypeScript SDK README | `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` |
| Python SDK README | `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md` |

### 1.4 Plan Implementation

Review the service's API docs to identify key endpoints, auth requirements, and data models. Prioritize the most common operations.

## Phase 2: Implementation

### 2.1 Project Structure

See language-specific guides for setup:
- [TypeScript Guide](./reference/node_mcp_server.md) — project structure, package.json, tsconfig
- [Python Guide](./reference/python_mcp_server.md) — module organization, dependencies

### 2.2 Core Infrastructure

Create shared utilities: API client with auth, error handling helpers, response formatting (JSON/Markdown), pagination support.

### 2.3 Implement Tools

For each tool:

**Input schema**: Use Zod (TypeScript) or Pydantic (Python) with constraints, clear descriptions, and examples.

**Output schema**: Define `outputSchema` where possible; use `structuredContent` for structured responses.

**Implementation**:
- Async/await for I/O
- Actionable error messages
- Pagination support where applicable

**Annotations**: Set `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` as appropriate.

## Phase 3: Review and Test

**Code quality**: no duplicated code, consistent error handling, full type coverage, clear tool descriptions.

**Build and test**:
- TypeScript: `npm run build`, then `npx @modelcontextprotocol/inspector`
- Python: `python -m py_compile your_server.py`, then MCP Inspector

See language-specific guides for detailed testing and quality checklists.

## Phase 4: Create Evaluations

Test whether LLMs can effectively use your server to answer realistic, complex questions.

Load [reference/evaluation.md](./reference/evaluation.md) for complete guidelines.

### Process

1. **Inspect tools**: list available tools and understand capabilities
2. **Explore content**: use read-only operations to explore available data
3. **Generate questions**: create 10 complex, realistic questions
4. **Verify answers**: solve each question yourself

### Question Requirements

Each question should be: independent, read-only, complex (multiple tool calls), realistic, verifiable (single clear answer), and stable over time.

### Output Format

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames...</question>
    <answer>3</answer>
  </qa_pair>
</evaluation>
```
