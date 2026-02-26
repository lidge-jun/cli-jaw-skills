---
name: api-design-reviewer
description: "REST API design review and best practices. Naming conventions, HTTP methods, pagination, error formats, versioning, breaking change detection, rate limiting, HATEOAS. Use when designing or reviewing APIs."
---

# API Design Reviewer

Comprehensive API design analysis focusing on REST conventions, consistency, and industry standards.

---

## REST Design Principles

### Resource Naming

```
✅ Good:                          ❌ Bad:
/api/v1/users                     /api/v1/getUsers
/api/v1/user-profiles             /api/v1/user_profiles
/api/v1/orders/123/line-items     /api/v1/orders/123/lineItems
```

**Rules:** Plural nouns for collections. Kebab-case for multi-word resources. CamelCase for JSON fields. No verbs in URLs (use HTTP methods).

### HTTP Methods

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Retrieve resources | Yes | Yes |
| POST | Create new resources | No | No |
| PUT | Replace entire resource | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Remove resource | Yes | No |

### URL Structure

```
Collection:   /api/v1/users
Individual:   /api/v1/users/123
Nested:       /api/v1/users/123/orders
Action:       /api/v1/users/123/activate (POST)
Filtering:    /api/v1/users?status=active&role=admin
```

---

## Pagination Patterns

### Cursor-Based (Recommended)
```json
{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6MTIzfQ==",
    "hasMore": true
  }
}
```

### Offset-Based
```json
{
  "data": [...],
  "pagination": { "offset": 20, "limit": 10, "total": 150, "hasMore": true }
}
```

---

## Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid parameters",
    "details": [
      { "field": "email", "code": "INVALID_FORMAT", "message": "Email address is not valid" }
    ],
    "requestId": "req-123456",
    "timestamp": "2024-02-16T13:00:00Z"
  }
}
```

### Status Code Usage

| Code | Meaning |
|------|---------|
| 200 | Success (GET, PUT, PATCH) |
| 201 | Created (POST) |
| 204 | No Content (DELETE) |
| 400 | Validation error |
| 401 | Authentication required |
| 403 | Permission denied |
| 404 | Resource not found |
| 409 | Conflict (duplicate, version mismatch) |
| 422 | Semantic errors (valid syntax, bad logic) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

---

## Versioning Strategies

| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| URL (recommended) | `/api/v1/users` | Clear, easy to route | URL proliferation |
| Header | `Accept: application/vnd.api+json;version=1` | Clean URLs | Less visible |
| Query parameter | `/api/users?version=1` | Simple | Not RESTful |

---

## Breaking vs Non-Breaking Changes

### Safe (Non-Breaking)
- Adding optional request fields
- Adding response fields
- Adding new endpoints
- Making required fields optional

### Breaking (Require Version Bump)
- Removing response fields
- Making optional fields required
- Changing field types
- Removing or renaming endpoints
- Changing URL structure

---

## Rate Limiting

### Response Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### 429 Response
```json
{ "error": { "code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests", "retryAfter": 3600 } }
```

---

## Authentication Patterns

| Pattern | Header | Use Case |
|---------|--------|----------|
| Bearer Token | `Authorization: Bearer <token>` | JWT, OAuth 2.0 |
| API Key | `X-API-Key: <key>` | Service-to-service |
| Basic Auth | `Authorization: Basic <base64>` | Simple auth (with HTTPS) |

---

## Idempotency

For non-idempotent operations (POST), use idempotency keys:
```
POST /api/v1/payments
Idempotency-Key: 123e4567-e89b-12d3-a456-426614174000
```

---

## Review Checklist

- [ ] Resources use plural nouns, kebab-case
- [ ] Correct HTTP methods for each operation
- [ ] Consistent error response format
- [ ] Pagination on all list endpoints
- [ ] Versioning strategy defined
- [ ] Rate limiting headers present
- [ ] Authentication documented
- [ ] Breaking changes flagged

---

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Verb-based URLs (`/getUsers`) | Use nouns + HTTP methods |
| Inconsistent response shapes | Standardize envelope format |
| Deep nesting (`/a/1/b/2/c/3/d`) | Max 2 levels, use query params |
| Ignoring status codes | Use specific codes per error type |
| Missing pagination | Always paginate lists |
| No versioning | Plan for API evolution from day one |
| Exposing internal structure | Design for external consumption |
