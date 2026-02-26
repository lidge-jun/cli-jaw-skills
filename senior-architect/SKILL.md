---
name: senior-architect
description: "System architecture design, ADRs, dependency analysis, architecture pattern selection (monolith, microservices, CQRS, event sourcing, hexagonal), database and tech stack decision matrices. Use when making architecture decisions or evaluating system design."
---

# Senior Architect

Architecture design guidance: pattern selection, decision documentation, dependency analysis, and system evolution strategies.

---

## Architecture Decision Records (ADRs)

Document every significant architecture decision:

```markdown
# ADR-001: [Decision Title]

## Status
Accepted | Proposed | Deprecated | Superseded by ADR-XXX

## Context
What problem are we facing? What constraints exist?

## Decision
What did we decide and why?

## Consequences
- Positive: [benefits]
- Negative: [trade-offs accepted]
- Risks: [what could go wrong]
```

**Store in:** `docs/adrs/` or `docs/architecture/decisions/`

---

## Architecture Pattern Selection

### Decision Matrix

| Requirement | Recommended Pattern |
|---|---|
| Rapid MVP development | Modular Monolith |
| Independent team deployment | Microservices |
| Complex domain logic | Domain-Driven Design |
| High read/write ratio difference | CQRS |
| Audit trail required | Event Sourcing |
| Third-party integrations | Hexagonal (Ports & Adapters) |

### Monolith vs Microservices

**Choose Monolith when:**
- Team < 10 engineers
- Domain boundaries unclear
- Low operational maturity
- Speed to market critical

**Choose Microservices when:**
- Independent deployment needed
- Teams own separate bounded contexts
- Different scaling requirements per service
- Polyglot technology requirements

### Pattern Overview

| Pattern | Key Idea | Trade-off |
|---------|----------|-----------|
| Modular Monolith | Single deployment, clear module boundaries | Easy start, harder to scale independently |
| Microservices | Independent services, own databases | Operational complexity, network latency |
| CQRS | Separate read/write models | Complexity increase, eventual consistency |
| Event Sourcing | Store events, not state | Full audit trail, replay capability; harder queries |
| Hexagonal | Ports & adapters separate core from infra | Testable, swappable; more indirection |

---

## Dependency Analysis

### Healthy vs Unhealthy Dependencies

| Signal | Healthy | Unhealthy |
|--------|---------|-----------|
| Direction | Unidirectional (A → B) | Circular (A → B → C → A) |
| Coupling | Interface-based | Implementation-based |
| Scope | Narrow (few imports) | Broad (importing internals) |

### Breaking Circular Dependencies

1. Extract shared interface/contract
2. Invert dependency direction (depend on abstractions)
3. Introduce an event bus or mediator
4. Split into separate modules

---

## Database Selection

| Type | Best For |
|------|----------|
| PostgreSQL | Default for most apps. ACID, complex queries, JSON support |
| MongoDB | Flexible schema, document-oriented, rapid prototyping |
| Redis | Caching, sessions, real-time features |
| DynamoDB | Serverless, auto-scaling, AWS-native |
| TimescaleDB | Time-series with SQL |

---

## Tech Stack Decision

| Question | Recommendation |
|----------|---------------|
| SEO required? | Next.js with SSR |
| Internal dashboard? | React + Vite |
| API-first backend? | FastAPI or Fastify |
| Enterprise scale? | NestJS + PostgreSQL |
| Rapid prototype? | Next.js API routes |
| Real-time needed? | WebSocket layer (Socket.io, ws) |

---

## System Design Workflow

1. **Clarify requirements:** Functional + non-functional (latency, throughput, availability)
2. **Estimate scale:** Users, requests/sec, data size, growth rate
3. **Design high-level architecture:** Components, data flow, API boundaries
4. **Choose data stores:** Based on access patterns, consistency needs
5. **Design for failure:** Retries, circuit breakers, fallbacks, graceful degradation
6. **Plan evolution:** How does this scale 10×? What do we change?

---

## Review Checklist

- [ ] Architecture Decision Record exists for key choices
- [ ] No circular dependencies between modules
- [ ] Clear separation: transport → business logic → data access
- [ ] Failure modes identified and handled
- [ ] Scaling strategy documented
- [ ] Data consistency model chosen (strong vs eventual)
