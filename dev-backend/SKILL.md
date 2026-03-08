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
| `references/core/api-design.md`        | **Always** for API work        | REST conventions, response envelopes, HTTP status, pagination, GraphQL |
| `references/core/architecture.md`      | **Always** for new features    | Layered architecture, DDD, SOLID, when to split, monolith vs micro     |
| `references/core/anti-slop-backend.md` | **Always**                     | Banned patterns: god classes, raw SQL in services, magic numbers, etc. |
| `references/core/security.md`          | **Always** for production code | OWASP, auth, input validation, rate limiting, security headers         |
| `references/stacks/node.md`            | Node.js/TypeScript projects    | Express/Fastify, middleware, Zod validation, ESM, error handling       |
| `references/stacks/python.md`          | Python projects                | FastAPI/Django, Pydantic, async patterns, testing                      |
| `references/stacks/database.md`        | Database design/optimization   | PostgreSQL, MongoDB, indexing, N+1, migrations, transactions           |

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

If config files exist → detect silently. No questions needed.

### Architecture Clarification (new or ambiguous projects)

When the request has **unspecified technology or unclear scope**, clarify before coding:

1. **Identify what's ambiguous** from this list:

| Dimension    | Options to present                                                         |
| ------------ | -------------------------------------------------------------------------- |
| API style    | REST (default) · GraphQL (flexible clients) · gRPC (internal, high-perf)   |
| Database     | PostgreSQL (default, ACID) · MongoDB (flexible schema) · SQLite (embedded) |
| Auth method  | JWT + refresh (stateless) · Session-based (simple) · OAuth 2.1 (3rd party) |
| Realtime     | Not needed (default) · WebSocket · SSE · Polling                           |
| Architecture | Monolith (default) · Modular monolith · Microservices                      |

2. **Recommend one with reasoning**: cite project context. "3명 프로젝트라 모노리스 + PostgreSQL + JWT 조합을 추천합니다."
3. **Over-engineering guard**: A CRUD API *probably* doesn't need GraphQL + microservices + event sourcing. Simple → complex, not the reverse.
4. **One round limit**: 2-3 options → recommend → confirm → proceed. Don't interview.

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
- Repositories: abstract DB access. Services never write raw SQL.

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

## 5. Pre-Flight Checklist

Before delivering:
- [ ] Consistent response envelope on every endpoint
- [ ] Input validation with schema (Zod, Pydantic, etc.)
- [ ] Authentication middleware on protected routes
- [ ] Rate limiting on public endpoints
- [ ] Structured JSON logging with `requestId`
- [ ] Error handler returns proper HTTP codes
- [ ] No raw SQL in service layer
- [ ] No hardcoded secrets
- [ ] Migrations have rollback
- [ ] Stack-specific rules followed (see `references/stacks/`)
