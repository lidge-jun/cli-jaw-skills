---
name: "openai-docs"
description: "Use when the user asks how to build with OpenAI products or APIs and needs up-to-date official documentation with citations (for example: Codex, Responses API, Chat Completions, Apps SDK, Agents SDK, Realtime, model capabilities or limits); prioritize OpenAI docs MCP tools and restrict any fallback browsing to official OpenAI domains."
---


# OpenAI Docs

Provide authoritative, current guidance from OpenAI developer docs using the developers.openai.com MCP server. Prioritize MCP doc tools over web search for OpenAI-related questions. Fall back to web search only when MCP returns no meaningful results.

## Quick start

- Use `mcp__openaiDeveloperDocs__search_openai_docs` to find the most relevant doc pages.
- Use `mcp__openaiDeveloperDocs__fetch_openai_doc` to pull exact sections and quote/paraphrase accurately.
- Use `mcp__openaiDeveloperDocs__list_openai_docs` only when you need to browse or discover pages without a clear query.

## OpenAI product snapshots

1. Apps SDK: Build ChatGPT apps by providing a web component UI and an MCP server that exposes your app's tools to ChatGPT.
2. Responses API: A unified endpoint designed for stateful, multimodal, tool-using interactions in agentic workflows.
3. Chat Completions API: Generate a model response from a list of messages comprising a conversation.
4. Codex: OpenAI's coding agent for software development that can write, understand, review, and debug code.
5. gpt-oss: Open-weight OpenAI reasoning models (gpt-oss-120b and gpt-oss-20b) released under the Apache 2.0 license.
6. Realtime API: Build low-latency, multimodal experiences including natural speech-to-speech conversations.
7. Agents SDK: A toolkit for building agentic apps where a model can use tools and context, hand off to other agents, stream partial results, and keep a full trace.

## If MCP server is missing

1. Run: `codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp`
2. If it fails due to permissions, retry with escalated permissions (include a 1-sentence justification).
3. Only if the escalated attempt also fails, ask the user to run the install command.
4. Ask the user to restart Codex, then re-run the doc search.

## Workflow

1. Clarify the product scope (Codex, OpenAI API, or ChatGPT Apps SDK) and the task.
2. Search docs with a precise query.
3. Fetch the best page and the specific section needed (use `anchor` when possible).
4. Answer with concise guidance and cite the doc source.
5. Provide code snippets only when the docs support them.

## Quality rules

- Treat OpenAI docs as source of truth; flag when docs are silent on a topic.
- Prefer paraphrase with citations; keep direct quotes short.
- When pages disagree, cite both and note the difference.

## Tooling notes

- Use MCP doc tools before web search for OpenAI questions.
- When falling back to web search, restrict to official OpenAI domains (developers.openai.com, platform.openai.com) and cite sources.
