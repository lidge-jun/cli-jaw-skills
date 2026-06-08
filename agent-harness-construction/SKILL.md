---
name: agent-harness-construction
description: Design and optimize AI agent action spaces, tool definitions, and observation formatting for higher completion rates.
---

# Agent Harness Construction

Use this skill when you are improving how an agent plans, calls tools, recovers from errors, and converges on completion.

## Core Model

Agent output quality is constrained by:
1. Action space quality
2. Observation quality
3. Recovery quality
4. Context budget quality

## Action Space Design

1. Use stable, explicit tool names.
2. Keep inputs schema-first and narrow.
3. Return deterministic output shapes.
4. Prefer focused tools with clear scope.

## Granularity Rules

- Use micro-tools for high-risk operations (deploy, migration, permissions).
- Use medium tools for common edit/read/search loops.
- Use macro-tools only when round-trip overhead is the dominant cost.

## Observation Design

Every tool response should include:
- `status`: success|warning|error
- `summary`: one-line result
- `next_actions`: actionable follow-ups
- `artifacts`: file paths / IDs

## Error Recovery Contract

For every error path, include:
- root cause hint
- safe retry instruction
- explicit stop condition

## Context Budgeting

1. Keep system prompt minimal and invariant.
2. Move large guidance into skills loaded on demand.
3. Prefer references to files over inlining long documents.
4. Compact at phase boundaries, not arbitrary token thresholds.

## Architecture Pattern Guidance

- ReAct: best for exploratory tasks with uncertain path.
- Function-calling: best for structured deterministic flows.
- Hybrid (recommended): ReAct planning + typed tool execution.

## Benchmarking

Track:
- completion rate
- retries per task
- pass@1 and pass@3
- cost per successful task

## Patterns to Watch For

- Consolidate tools with overlapping semantics into distinct, well-scoped actions.
- Include recovery hints in every tool response.
- Pair error output with suggested next steps.
- Keep context references focused and relevant to the current task.

## Tool Integration Standards (2026)

- **MCP (Model Context Protocol)**: Preferred standard for defining and exposing agent tools. Provides schema-based tool discovery, typed inputs/outputs, and cross-platform compatibility.
- **AGENTS.md / Harness Templates**: Codify harness configuration in a discoverable file at the project root. Document available tools, preferred patterns, and constraints.

## Observability

Instrument every tool call with:
- Tool name and invocation timestamp
- Input hash (for deduplication detection)
- Latency and token cost
- Success/failure and error class

Use **LangSmith**, **Logfire**, or **OpenTelemetry** for trace visualization. Without observability, harness optimization is guesswork.

## Multi-Agent Topologies

| Topology | Structure | Best For |
|----------|-----------|----------|
| Pipeline | A → B → C | Sequential processing stages |
| Fan-out/Fan-in | Hub dispatches N workers, merges results | Parallel independent tasks |
| Supervisor | Supervisor delegates and reviews | Quality-gated workflows |
| DAG | Dependency-ordered execution graph | Complex workflows with partial dependencies |

## Evals-in-CI

Run harness evaluation as part of your CI pipeline. Track completion rate, cost, and latency per commit. Regressions in harness quality should block merges.

