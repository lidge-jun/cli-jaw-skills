---
name: dev-security
description: "Authoritative security guidance for backend, frontend touchpoints, agentic AI, and production hardening. Read for auth, validation, secrets, reviews, and pre-deploy verification."
license: Complete terms in LICENSE.txt
---

# Dev-Security — Production Security Hardening

Treat security as a build constraint, not a cleanup step.
This skill is the authoritative source for authentication, authorization, input validation, secrets, headers, rate limiting, supply-chain checks, PII handling, and agentic AI safety.
`dev-backend` delegates here for policy and verification depth.
`dev-frontend` remains responsible for UI implementation, but frontend security touchpoints such as CSP compliance, CORS behavior, XSS prevention, and dependency auditing are defined here.

## When to Activate

Activate this skill when you are:
- Writing auth, session, cookie, token, password-reset, or OAuth logic.
- Accepting user input from forms, URLs, headers, cookies, webhooks, file uploads, rich text, or AI prompts.
- Handling secrets, credentials, certificates, encryption keys, or third-party API keys.
- Reviewing code for security regressions or production-readiness.
- Auditing dependencies, CI pipelines, or release integrity.
- Designing logging, PII retention, masking, audit trails, or incident response rules.
- Building AI agents, tool-using workflows, or prompt-processing systems.

Use this skill together with the domain skill, not instead of it:
- API architecture and middleware placement: See `dev-backend/SKILL.md` §4.
- Frontend rendering patterns and anti-slop UI guardrails: See `dev-frontend/SKILL.md` §§3-7.
- Test strategy and execution flow: See `dev-testing`.
- Review severity and review flow: See `dev-code-reviewer/SKILL.md` §§1-2.
- Data pipeline design: See `dev-data/SKILL.md` §§2-4.

## Threat Model First

Answer these three questions before implementation:
1. What are we protecting?
   - Accounts, sessions, payment state, internal admin actions, uploaded files, secrets, PII, audit logs.
2. From whom?
   - Anonymous users, authenticated users, malicious insiders, compromised browsers, compromised CI, poisoned dependencies, hostile prompts.
3. What is the blast radius if this fails?
   - One user, one tenant, one environment, all customers, all secrets, all build artifacts.

Security-sensitive changes must name the trust boundary before coding:
- Browser ↔ API
- Public API ↔ internal service
- App ↔ database
- Agent prompt ↔ tool execution
- CI runner ↔ production artifact

If the change touches auth, payment, file upload, logging, or PII, write the must-pass checks before coding.
This skill owns security policy.
Domain skills own architecture and implementation details.

## Modular References

| File | When to Read | What It Covers |
| --- | --- | --- |
| `references/owasp-top10.md` | Any security-sensitive code | OWASP Top 10:2025 with unsafe/safe code pairs and checklists |
| `references/language-quirks.md` | When coding in JS/TS, Python, SQL, or Go | Per-language pitfalls that scanners and reviewers commonly miss |
| `references/static-analysis.md` | Before claiming code is secure | Semgrep, CodeQL, ESLint security, npm audit, pip-audit, Bandit, gitleaks, CI, pre-commit |
| `references/asvs-checklist.md` | Before deploy or release | ASVS 5.0 Level 1 and Level 2 pre-deploy checklist for V1-V9 |
| `references/agentic-ai-security.md` | When building tool-using agents or prompt-driven flows | OWASP ASI01-ASI10 mapped to agent rules and safe operating patterns |

Read only the references relevant to the current task.
A small CSS change needs no OWASP reference.
Auth, data access, secrets, file uploads, webhooks, or incident response changes do.

## 1. Input Validation

Input validation is the first line of defense.
Validate at the first trusted boundary, reject unknown fields, enforce limits, and escape or sanitize on output for the target context.
Client-side validation improves UX only — it is never a security boundary.

**Required rules**
- Validate shape, type, format, enum membership, length, and numeric range.
- Reject unknown fields by default.
- Canonicalize before validation when encoding differences matter.
- Distinguish parsing failures from authorization failures.
- Sanitize HTML only when rich text is explicitly allowed.
- Re-validate on the server even when frontend uses the same schema.

```ts
import { z } from 'zod';

export const RegisterInput = z.object({
  email: z.string().email().max(320),
  password: z.string().min(12).max(128),
  displayName: z.string().trim().min(1).max(80),
}).strict();
```

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RegisterInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    display_name: str = Field(min_length=1, max_length=80)
```

For injection cases, rich text, serialization pitfalls, and output encoding edge cases, read `references/owasp-top10.md` A05 and `references/language-quirks.md`.

## 2. Authentication Checklist

Use this checklist for login, session, token, password reset, magic link, OAuth, and admin access:
- [ ] Passwords hashed with `argon2id` or `bcrypt`; use MD5, SHA1, or raw SHA256 only for non-security hashing.
- [ ] Access tokens expire in 15-60 minutes.
- [ ] Refresh tokens rotate on use and support family invalidation after reuse detection.
- [ ] Browser tokens live in `httpOnly`, `secure`, `sameSite` cookies; keep session tokens out of `localStorage`.
- [ ] OAuth uses Authorization Code + PKCE; avoid implicit flow (deprecated, token-in-URL exposure).
- [ ] Sensitive actions such as email change, MFA reset, payout change, and password change require step-up auth.
- [ ] Failed logins are rate-limited and delayed progressively.
- [ ] Session invalidation runs after password reset, password change, and privilege change.
- [ ] Password reset tokens are one-time, short-lived, and stored hashed server-side.
- [ ] Auth errors are generic — avoid revealing whether a specific email exists.

See `references/owasp-top10.md` A07 for implementation patterns.
See `references/asvs-checklist.md` V2 and V3 before deploy.

## 3. Authorization and Sensitive Flows

Authentication says who the caller is.
Authorization says what the caller may do.
Security failures happen when a route checks only the first.

**Required rules**
- Default deny.
- Enforce RBAC or ABAC before business logic.
- Perform ownership checks on every resource read and write.
- Scope queries by tenant and actor, not only by route.
- Re-check authorization on bulk actions, background jobs, exports, and webhooks.
- Keep internal flags, role names, and hidden fields out of response serializers.

See `references/owasp-top10.md` A01 for code pairs.
See `dev-backend/SKILL.md` §4 for middleware execution order.

## 4. Secrets Management

Secrets are values that grant access, identity, or decryption capability.
Treat API keys, database credentials, signing keys, OAuth client secrets, webhook secrets, certificates, and recovery codes as secrets.

| Rule | Required Practice |
| --- | --- |
| Source control | Commit `.env.example`, never commit `.env`, real keys, tokens, or private certs |
| Local development | Load secrets from environment variables or a local secret store |
| Production | Use Vault, cloud secret manager, or KMS-backed delivery |
| Rotation | Document owner, rotation cadence, and emergency revocation path |
| Logging | Redact secrets before logs, traces, analytics, error reports, and screenshots |
| Testing | Use dedicated non-production keys with least privilege |

If a repository change touches secrets, run gitleaks before claiming done.
If a feature adds webhook verification or JWT signing, treat key rollover as part of the feature.
For scanning recipes, read `references/static-analysis.md`.
For agent workflows and exfiltration risk, read `references/agentic-ai-security.md`.

## 5. Security Headers

This skill owns header policy values.
`dev-backend` owns middleware ordering and integration points.

**Minimum production header baseline**
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy` with explicit `default-src`, `script-src`, `style-src`, `img-src`, `connect-src`, `frame-ancestors`, and `base-uri`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy` with unused capabilities disabled
- `X-Frame-Options: DENY` when CSP `frame-ancestors` is not sufficient for legacy support
- `Cross-Origin-Opener-Policy` and `Cross-Origin-Resource-Policy` where required by the app

```ts
import helmet from 'helmet';

app.disable('x-powered-by');
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "https://fonts.googleapis.com"],
      imgSrc: ["'self'", "data:"],
      connectSrc: ["'self'", "https://api.example.com"],
      frameAncestors: ["'none'"],
      baseUri: ["'self'"],
    },
  },
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: false },
}));
```

**Frontend touchpoints that must stay aligned**
- CSP compliance: no inline scripts, no unsafe event handlers, no surprise third-party script injection.
- CORS: explicit origin allowlist and correct credential mode for cookie-based auth.
- Avoid `dangerouslySetInnerHTML` unless sanitized with a maintained sanitizer and defended by CSP.
- Prefer cookies over browser storage for session tokens.

See `references/owasp-top10.md` A02 and A05.
See `dev-frontend/SKILL.md` §§5-7 for performance and accessibility guardrails that still apply after security changes.

## 6. Rate Limiting

Apply rate limiting per IP and, where available, per user, tenant, and credential target.
Return `429 Too Many Requests` with `Retry-After`.
Log repeated abuse without logging secrets or raw PII.

| Surface | Minimum Limit |
| --- | --- |
| Login | 5 requests per minute per IP and account identifier |
| Password reset request | 3 requests per hour per account identifier |
| Registration | 10 requests per hour per IP |
| MFA verification | 10 requests per 10 minutes per session |
| Public API | 100 requests per minute per user or API key |
| File upload start | 20 requests per hour per user |
| Webhook verification failures | Alert after burst anomalies and repeated signature failures |

Rate limiting is not only for brute force.
Use it for enumeration, abuse, accidental loops, webhook replay storms, and AI-triggered runaway automation.

## 7. Static Analysis Integration

Security claims are incomplete without automated checks.
At minimum, wire the language-appropriate scanners into local development and CI.

```bash
# JavaScript / TypeScript
npm audit --audit-level=high
npx eslint .
semgrep --config=auto .

# Python
pip-audit
bandit -q -r .
semgrep --config=auto .

# Secrets
gitleaks detect --source=. --no-git
```

For CI templates, pre-commit hooks, and tool-specific guidance, read `references/static-analysis.md`.
For review gating, combine this with `dev-code-reviewer/SKILL.md` §§1-2.

## 8. Agent Configuration Security

Agent-authored configuration files create a trust surface distinct from application code.

### Configuration Audit Checklist

| File | Check For |
| --- | --- |
| `CLAUDE.md` / `AGENTS.md` | Hardcoded secrets, auto-run instructions, prompt injection patterns |
| `settings.json` | Overly permissive allow lists (`Bash(*)`), missing deny lists, dangerous bypass flags |
| `mcp.json` | Risky MCP servers, hardcoded env secrets, `npx -y` supply chain risks |
| `hooks/` | Command injection via `${file}` interpolation, data exfiltration, silent error suppression |
| Agent definitions | Unrestricted tool access, prompt injection surface, missing model constraints |

### MCP Server Vetting

Before enabling any MCP server:
- Verify the package source and maintainer on npm/PyPI.
- Prefer pinned versions over `npx -y` auto-install.
- Restrict server capabilities to the minimum required scope.
- Use `${ENV_VAR}` references for all credentials.

### Sandboxing and Blast Radius Containment

Reduce the impact of any single compromise:
- Run agent tools with least-privilege filesystem access.
- Scope database credentials to the minimum required tables and operations.
- Isolate CI runners from production secrets using environment separation.
- Use network egress filtering for build and agent environments.
- Prefer ephemeral credentials that expire after the task completes.
- When an agent can execute shell commands, maintain an explicit deny list for destructive operations.

## 9. Pre-Flight Security Checklist

A security-sensitive change is complete only when every applicable item passes.

- [ ] Threat model names assets, attacker, trust boundary, and blast radius.
- [ ] All user input is validated at the first trusted boundary with unknown fields rejected.
- [ ] Authentication covers token TTL, cookie flags, reset flow, and revocation rules.
- [ ] Authorization is enforced per resource, not only per route.
- [ ] Queries, commands, templates, and serializers are protected from injection.
- [ ] Secrets are not committed, logged, embedded in screenshots, or exposed in client bundles.
- [ ] Security headers and CORS are explicit for the deployed environment.
- [ ] File upload, payment, logging, and PII changes pass their must-pass checks from the relevant reference.
- [ ] Rate limiting covers auth, public endpoints, and abuse-prone flows.
- [ ] Static analysis runs clean enough for the repository policy: Semgrep, CodeQL or equivalent, dependency audit, and secret scan.
- [ ] Error handling returns safe client messages and preserves structured server-side diagnostics.
- [ ] ASVS Level 1 passes for all security-sensitive changes; Level 2 passes for auth, payments, PII, admin, or multi-tenant flows.
- [ ] Agentic workflows resist prompt injection, tool misuse, exfiltration, and excessive agency.

### Must-Pass Addenda for High-Risk Changes

**Logging and PII**
- [ ] Raw email, phone number, access token, session cookie, recovery code, and payment data are redacted before logs and traces.
- [ ] Retention and deletion behavior are defined for the new data.

**File Uploads**
- [ ] Enforce file type, file size, storage path isolation, malware scanning policy, and download authorization.
- [ ] Validate server-side — the client-provided filename and MIME type are untrusted input.

**Payments**
- [ ] Idempotency, webhook signature verification, reconciliation, and failure-state handling are tested.
- [ ] Payment provider secrets stay out of logs, analytics, and client bundles.

If any item remains unknown, stop, investigate, and resolve the gap before proceeding.

## 10. Security Ownership Matrix

This matrix clarifies who defines, implements, and verifies each security control across the skill bundle:

| Control | Policy Owner | Implementation Owner | Verification Owner |
|---------|-------------|---------------------|--------------------|
| Input validation schema | `dev-security` §1 | Domain skill (backend/frontend/data) | `dev-testing` §2 |
| Auth flow (login, session, token) | `dev-security` §2 | `dev-backend` §4 middleware | `dev-testing` §1.3 risk priorities |
| Authorization (RBAC/ABAC) | `dev-security` §3 | `dev-backend` service layer | `dev-testing` §2 + `dev-code-reviewer` |
| Security headers (CSP, CORS, HSTS) | `dev-security` §5 | `dev-backend` middleware + `dev-frontend` compliance | `dev-testing` + static analysis |
| Rate limiting | `dev-security` §6 | `dev-backend` §4 middleware | Load testing + monitoring |
| PII/data classification | `dev-security` + `dev-data` §7 | `dev-data` pipeline + `dev-backend` API | `dev-testing` + audit logs |
| Secrets management | `dev-security` §4 | All skills (runtime env) | gitleaks + `dev-code-reviewer` |
| Dependency security | `dev-security` §7 | CI pipeline owner | `npm audit` / `pip-audit` in CI |
| Agentic AI safety | `dev-security` refs/agentic-ai | Agent builder | Scenario testing (`dev-testing`) |

Reference this matrix from `dev-backend` and `dev-frontend` when ownership is unclear.
