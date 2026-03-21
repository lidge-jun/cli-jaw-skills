---
name: dev-backend
description: "Backend engineering guide for orchestrated sub-agents. Framework-agnostic API design, clean architecture, database optimization, security hardening, systematic debugging. Modular: SKILL.md orchestrator + references/ for deep guidance. Injected when role=backend."
license: Complete terms in LICENSE.txt
---

# Dev-Backend — Production-Grade Backend Engineering

Build reliable, secure, and maintainable server-side applications.
This skill has modular references for specialized guidance — read the relevant ones before coding.

## Modular References

| File                                   | When to Read                   | What It Covers                                                         |
| -------------------------------------- | ------------------------------ | ---------------------------------------------------------------------- |
| `references/core/api-design.md`        | **Always** for API work        | REST conventions, response envelopes, HTTP status, pagination, GraphQL, gRPC, tRPC |
| `references/core/architecture.md`      | **Always** for new features    | Layered architecture, DDD, SOLID, when to split, monolith vs micro     |
| `references/core/anti-slop-backend.md` | **Always**                     | Banned patterns: god classes, raw SQL in services, magic numbers, etc. |
| `references/core/security.md`          | **Always** for production code | Redirect to `dev-security` skill (this file is a delegation pointer)             |
| `references/core/observability.md`     | Production deployments         | OpenTelemetry, structured logging, distributed tracing, alerting       |
| `references/core/caching.md`           | Performance optimization       | Redis patterns, CDN, connection pooling, cache invalidation            |
| `references/stacks/node.md`            | Node.js/TypeScript projects    | Express/Fastify, middleware, Zod validation, ESM, error handling       |
| `references/stacks/python.md`          | Python projects                | FastAPI/Django, Pydantic, async patterns, testing                      |
| `references/stacks/database.md`        | Database design/optimization   | PostgreSQL, MongoDB, indexing, N+1, migrations, ORM comparison         |

Read `api-design.md` + `anti-slop-backend.md` first, then the relevant stack file.

---

## 0. Stack Detection & Architecture Clarification

### Auto-detect (existing projects)

| File Found                          | Project Type      |
| ----------------------------------- | ----------------- |
| `tsconfig.json`                     | TypeScript (Node) |
| `package.json` (no ts)              | JavaScript (Node) |
| `pyproject.toml`/`requirements.txt` | Python            |
| `go.mod`                            | Go                |
| `Cargo.toml`                        | Rust              |

If config files exist → detect silently and proceed.

### Architecture Clarification (new or ambiguous projects)

When the request has **unspecified technology or unclear scope**, clarify before coding:

1. **Identify what's ambiguous** from this list:

| Dimension    | Options to present                                                                  |
| ------------ | ----------------------------------------------------------------------------------- |
| API style    | REST (default) · GraphQL (BFF/mobile) · gRPC (internal microservices) · tRPC (TS monorepo) |
| Database     | PostgreSQL (default, ACID) · MongoDB (flexible schema) · SQLite (embedded)          |
| Auth method  | JWT + refresh (stateless) · Session-based (simple) · OAuth 2.1 (3rd party)          |
| Realtime     | Not needed (default) · WebSocket · SSE · Polling                                    |
| Architecture | Monolith (default) · Modular monolith · Microservices                               |

2. **Recommend one with reasoning**: cite project context. e.g., "Small team → monolith + PostgreSQL + JWT is the simplest starting point."
3. **Over-engineering guard**: A CRUD API *probably* doesn't need GraphQL + microservices + event sourcing. Simple → complex, not the reverse.
4. **One round limit**: 2-3 options → recommend → confirm → proceed.

If the user already specifies clear tech (e.g. "FastAPI로 REST API 만들어줘"), **skip this entirely**.

---

## 1. Architecture Decision

Before coding, identify the right pattern:

| Team Size | Default Starting Point  |
| --------- | ----------------------- |
| 1-3 devs  | Modular monolith        |
| 4-10 devs | Modular monolith or SOA |
| 10+ devs  | Consider microservices  |

**Default to monolith.** Extract only when you have a proven need (different scaling, independent deployment, technology mismatch).

See `references/core/architecture.md` for full decision matrices.

### API Protocol Decision

| Protocol | Choose When | Avoid When |
|----------|-------------|------------|
| **REST** | Public/partner APIs, simple CRUD, caching matters | Clients need flexible data shapes |
| **GraphQL** | Mobile/BFF, multiple resources per request, bandwidth-constrained | Simple CRUD, server-to-server, file uploads |
| **gRPC** | Internal microservices, high-perf binary, bidirectional streaming | Browser clients (without gRPC-Web), public APIs |
| **tRPC** | TypeScript monorepo, internal tools, rapid prototyping | Polyglot environments, public APIs |

**Hybrid pattern (industry consensus):**
```
Public/Partner → REST (OpenAPI 3.1)
Mobile/Web BFF → GraphQL (Apollo Federation)
Internal services → gRPC (Protobuf contracts)
TS internal tools → tRPC (zero-codegen type safety)
```

See `references/core/api-design.md` for protocol-specific patterns.

---

## 2. Layered Architecture (Always Follow)

```
Routes → Controllers → Services → Repositories → Database
  │          │             │            │
  │          │             │            └── Data access only
  │          │             └── Business logic, validation
  │          └── Parse HTTP, format response
  └── URL mapping, middleware
```

**Rules:**
- Routes: URL patterns + middleware only. No logic.
- Controllers: parse input, call services, format output. No business rules.
- Services: receive/return plain data (not `req`/`res`). All logic here.
- Repositories: abstract DB access. Services access data through repositories only.

---

## 3. Error Handling (Always Follow)

| Type           | HTTP | Log Level     |
| -------------- | ---- | ------------- |
| Validation     | 400  | warn          |
| Authentication | 401  | warn          |
| Authorization  | 403  | warn          |
| Not found      | 404  | info          |
| Conflict       | 409  | warn          |
| Rate limit     | 429  | info          |
| Internal error | 500  | error + stack |

Use a centralized `AppError` class. Distinguish operational vs programmer errors.

### Error Taxonomy (AppError Hierarchy)

```typescript
abstract class AppError extends Error {
  abstract readonly statusCode: number
  abstract readonly code: string
  abstract readonly isOperational: boolean
}

class ValidationError extends AppError {
  readonly statusCode = 400
  readonly code = "VALIDATION_ERROR"
  readonly isOperational = true
}

class NotFoundError extends AppError {
  readonly statusCode = 404
  readonly code = "NOT_FOUND"
  readonly isOperational = true
}

class InternalError extends AppError {
  readonly statusCode = 500
  readonly code = "INTERNAL_ERROR"
  readonly isOperational = false // programmer error — alert + investigate
}
```

### Result Pattern (Preferred for TypeScript)

Use value-based error handling instead of thrown exceptions for business logic:

```typescript
import { ok, err, Result } from "neverthrow"

function parseUserId(input: string): Result<number, ValidationError> {
  const id = parseInt(input, 10)
  if (isNaN(id)) return err(new ValidationError("Invalid user ID"))
  return ok(id)
}

// Caller MUST handle both paths — compiler enforces it
const result = parseUserId(req.params.id)
  .andThen(id => findUser(id))
  .mapErr(e => toApiError(e))
```

| Library | When to Use |
|---------|-------------|
| **neverthrow** | Default choice — simple Rust-like `Result<T, E>` |
| **Effect** | Complex domains needing full effect system |

**Rule:** Use `Result` for business logic. Reserve `try/catch` for error boundaries (middleware, top-level handlers) only.

---

## 4. Middleware Execution Order

Apply in this sequence (order matters):

1. Request ID generation
2. Request logging
3. Security headers (CORS, CSP, HSTS)
4. Rate limiting
5. Authentication
6. Authorization
7. Body parsing
8. Input validation (schema)
9. Route handler
10. Error handler
11. Response logging

---

## 5. API Response Contract

Every endpoint must return a **stable envelope** that frontend clients can rely on:

```typescript
// Success envelope
{ "success": true, "data": { ... }, "meta": { "requestId": "req_abc123", "pagination": { "page": 1, "pageSize": 20, "total": 142 } } }

// Error envelope
{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "Email is required", "details": [{ "field": "email", "rule": "required" }] }, "meta": { "requestId": "req_abc123" } }
```

**Rules:**
- `success` boolean at top level — never infer from HTTP status alone
- `error.code` is machine-readable (UPPER_SNAKE), `error.message` is human-readable
- `meta.requestId` on every response — enables cross-service tracing
- Pagination uses cursor-based (`after`/`before`) for large datasets, offset-based (`page`/`pageSize`) for admin UIs
- Nullability: explicitly return `null` for absent optional fields, never omit the key
- Timestamps: ISO 8601 UTC (`2024-01-15T09:30:00Z`), never Unix epoch in JSON
- Money: integer cents + currency code, never floating point

See `references/core/api-design.md` for protocol-specific patterns (REST, GraphQL, gRPC, tRPC).

---

## 6. Caching Strategy

**The cardinal rule:** cache only after correctness is proven. Never cache before you have tested the uncached path.

### Cache Key Design

```
{service}:{resource}:{identifier}:{version}
user-service:profile:u_12345:v2
```

- Include version in keys to avoid stale data after schema changes
- Use consistent hashing for cache keys — no random components
- Namespace by service to prevent key collisions in shared Redis

### TTL Selection

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| User session | 15-60 min | Security boundary |
| User profile | 5-15 min | Balance freshness vs load |
| Public config/feature flags | 1-5 min | Low write frequency |
| Computed aggregations | 10-60 min | Expensive to recompute |
| Static assets (CDN) | 1 year + cache-busting hash | Immutable content |

### Invalidation Triggers

| Event | Action |
|-------|--------|
| Data mutation (write/update/delete) | Invalidate related cache keys immediately |
| Schema/version change | Bump version in cache key prefix |
| Deployment | Warm critical caches during rollout |
| User logout/password change | Purge all session and profile caches for that user |

### Patterns

| Pattern | When |
|---------|------|
| **Cache-aside** (default) | App reads cache → miss → read DB → write cache |
| **Write-through** | App writes DB + cache atomically — strong consistency |
| **Write-behind** | App writes cache → async DB write — high throughput, risk of loss |
| **Read-through** | Cache library handles DB fetch on miss — simpler app code |

**Cache safety rules:**
- Set a TTL on every cache entry — prevents stale data
- Add jitter or locking on expiry — prevents cache stampede
- Encrypt cached PII with access controls
- Exclude error responses from cache — prevents failure propagation

See `references/core/caching.md` for Redis patterns, CDN configuration, and connection pooling.

---

## 7. Observability (OpenTelemetry)

Use OpenTelemetry for the three pillars of observability:

| Signal | Purpose | Backends |
|--------|---------|----------|
| **Traces** | Request flow across services | Jaeger, Tempo, Zipkin |
| **Metrics** | Quantitative measurements | Prometheus, Grafana |
| **Logs** | Event records with context | Loki, ELK, Uptrace |

**Structured Logging Rules:**
1. JSON format only in production — never free-text
2. Every log includes `traceId`, `spanId`, `requestId`
3. Log levels: `error` (needs action) · `warn` (degraded) · `info` (business events) · `debug` (dev only)
4. **Never log PII, secrets, or full request bodies**
5. Use OTel semantic conventions for field names

```typescript
import { trace, context } from '@opentelemetry/api';

// Extract trace context from the active span (auto-injected by OTel middleware)
const span = trace.getSpan(context.active());
const traceId = span?.spanContext().traceId ?? 'no-trace';
const spanId = span?.spanContext().spanId ?? 'no-span';

logger.error("Payment failed", {
  "error.type": "card_declined",
  "payment.id": paymentId,
  "user.id": userId,
  "trace.id": traceId,
  "span.id": spanId,
})
```

See `references/core/observability.md` for auto-instrumentation setup, custom spans, and alerting.

---

## 8. Pre-Flight Checklist

Before delivering:
- [ ] Consistent response envelope on every endpoint
- [ ] Input validation with schema (Zod, Pydantic, etc.)
- [ ] Authentication middleware on protected routes
- [ ] Rate limiting on public endpoints
- [ ] Structured JSON logging with `requestId` and `traceId`
- [ ] Error handler returns proper HTTP codes via `AppError` hierarchy
- [ ] No raw SQL in service layer
- [ ] No hardcoded secrets
- [ ] Migrations have rollback
- [ ] Observability: traces and structured logs wired (see `references/core/observability.md`)
- [ ] Security review: delegate to `dev-security/SKILL.md` for production readiness
- [ ] Stack-specific rules followed (see `references/stacks/`)
