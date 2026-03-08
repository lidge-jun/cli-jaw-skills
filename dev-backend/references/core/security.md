# Security — Backend Hardening Guide

OWASP-aligned security practices for production APIs.
Synthesized from dev-backend + senior-backend + mrgoonie backend-development.

---

## Input Validation

- Validate ALL user input at the API boundary using schema validation (Zod, Joi, Pydantic, JSON Schema)
- Reject unknown fields
- Coerce types explicitly
- Enforce length, range, and format limits
- **Never trust client-side validation** — always re-validate server-side

---

## Authentication

- Short-lived access tokens (15-60 min) + longer-lived refresh tokens
- Store secrets in environment variables, never in source code
- Verify tokens on every protected endpoint via middleware
- Hash passwords with bcrypt/argon2id (cost factor ≥ 10)
- Prefer RS256 (asymmetric) over HS256 (symmetric) for JWT
- Implement OAuth 2.1 + PKCE for third-party auth

---

## Authorization

- Define permission roles clearly: `read`, `write`, `delete`, `admin`
- Check permissions in middleware, not inside business logic
- Default to deny — explicitly grant access
- Never rely on "not forbidden"

---

## Rate Limiting

- Per-IP and per-user limits on all public endpoints
- Return `429 Too Many Requests` with `Retry-After` header
- Tighter limits on sensitive endpoints:
  - Login: 5/min per IP
  - Password reset: 3/hour per email
  - Registration: 10/hour per IP
  - API: 100/min per user

---

## Security Headers (Minimum)

```javascript
// Express + Helmet
app.use(helmet({
  contentSecurityPolicy: true,
  crossOriginEmbedderPolicy: true,
  crossOriginOpenerPolicy: true,
  hsts: { maxAge: 31536000, includeSubDomains: true },
}));
```

Enable at minimum:
- `Strict-Transport-Security` (HSTS)
- `Content-Security-Policy`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- Disable `X-Powered-By`
- Configure CORS explicitly — **never `*` in production**

---

## OWASP Top 10 (2025 Quick Reference)

| #   | Vulnerability             | Mitigation                                    |
| --- | ------------------------- | --------------------------------------------- |
| 1   | Broken Access Control     | RBAC middleware, principle of least privilege |
| 2   | Cryptographic Failures    | TLS everywhere, argon2id, no MD5/SHA1         |
| 3   | Injection                 | Parameterized queries, ORMs, validate         |
| 4   | Insecure Design           | Threat modeling, security requirements        |
| 5   | Security Misconfiguration | Helmet, no debug mode, env-specific config    |
| 6   | Vulnerable Components     | Audit deps (`npm audit`, `pip-audit`)         |
| 7   | Auth Failures             | MFA, account lockout, secure sessions         |
| 8   | Data Integrity            | Verify CI/CD pipelines, SRI for CDN           |
| 9   | Logging Failures          | Structured logging, audit trails              |
| 10  | SSRF                      | Restrict outbound URLs, no user-input URLs    |

---

## Secrets Management

```
# .env.example (committed)
DATABASE_URL=postgres://user:pass@host:5432/db
JWT_SECRET=change-me-in-production
API_KEY=your-key-here

# .env (NEVER committed — in .gitignore)
DATABASE_URL=postgres://real-user:real-pass@prod-host:5432/prod-db
```

- Never log secrets
- Never return secrets in API responses
- Rotate tokens regularly
- Use vault/KMS in production (AWS Secrets Manager, HashiCorp Vault)
