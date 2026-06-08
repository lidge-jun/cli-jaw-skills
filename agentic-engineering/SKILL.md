---
name: agentic-engineering
description: Operate as an agentic engineer using eval-first execution, decomposition, and cost-aware model routing.
---

# Agentic Engineering

Use this skill for engineering workflows where AI agents perform most implementation work and humans enforce quality and risk controls.

## Operating Principles

1. Define completion criteria before execution.
2. Decompose work into agent-sized units.
3. Route model tiers by task complexity.
4. Measure with evals and regression checks.

## Eval-First Loop

1. Define capability eval and regression eval.
2. Run baseline and capture failure signatures.
3. Execute implementation.
4. Re-run evals and compare deltas.

## Task Decomposition

Apply the 15-minute unit rule:
- each unit should be independently verifiable
- each unit should have a single dominant risk
- each unit should expose a clear done condition

## Model Routing

| Tier | Model | Use For |
|------|-------|---------|
| Fast/Cheap | Haiku 4.5 (`claude-haiku-4-5`) | Classification, boilerplate, narrow edits |
| Balanced | Sonnet 4.6 (`claude-sonnet-4-6`) | Implementation, refactors, most coding |
| Deep | Opus 4.8 (`claude-opus-4-8`) | Architecture, root-cause analysis, multi-file invariants |

Escalate model tier only when lower tier fails with a clear reasoning gap.

## Session Strategy

- Continue session for closely-coupled units.
- Start fresh session after major phase transitions.
- Compact after milestone completion, not during active debugging.

## Review Focus for AI-Generated Code

Prioritize:
- invariants and edge cases
- error boundaries
- security and auth assumptions
- hidden coupling and rollout risk

Focus review cycles on behavior and logic; rely on automated tooling for style enforcement.

## Cost Discipline

Track per task:
- model
- token estimate
- retries
- wall-clock time
- success/failure

Escalate model tier only when lower tier fails with a clear reasoning gap.

## Agent Development Lifecycle (ADLC)

Structured approach for building agent-powered features:

1. **Define** — Write eval criteria and acceptance tests before implementation
2. **Build** — Implement agent workflow with tool definitions (MCP preferred)
3. **Test** — Run capability evals + regression evals, measure quality metrics
4. **Deploy** — Canary rollout with observability; use feature flags for gradual enablement
5. **Monitor** — Track success rate, cost, drift, and user feedback in production

## Tool Integration

- Use **MCP (Model Context Protocol)** as the standard for agent tool access
- Define tools with precise schemas — vague descriptions produce vague tool calls
- Prefer server-side tool execution over client-side when security matters

## Agent Security & Governance

- Agents are **non-human identities**: apply zero-trust principles (least-privilege, time-bounded credentials)
- Audit every tool call and decision in structured logs
- Define a governance policy: which actions require human approval?
- Review agent outputs for compliance before external delivery

## Team Structure

- Optimal: **2–4 person pods** with AI agent support
- Each pod member reviews agent output, not just code
- Measure team by **business outcomes**, not vanity metrics (lines of code, commits)
