# Application security release checklist — ASVS-informed local policy

This local checklist supports a release decision; it is not the complete OWASP
ASVS and cannot certify conformance. Keep the existing assurance targets:
L1 for ordinary authenticated apps; L2 for admin, multi-tenant, PII, payment,
upload, and elevated internal flows. A threat model may require more. Lowering
an existing target needs a separate policy decision.

## Formal assessment baseline

Pin the official [OWASP ASVS 5.0.0 release](https://github.com/OWASP/ASVS/releases/tag/v5.0.0_release)
and assess all applicable requirements in that version. Authentication is V6;
Session Management is V7. Traceable examples include V6.3.3 (L2,
multi-factor/combined authentication), V7.2.1 (L1, trusted backend session
verification), and V7.4.1 (L1, terminated sessions cannot be reused).
These examples are not the full assessment.

For each applicable requirement record version, full ID, level, control owner,
scenario, evidence, and pass/fail/not-applicable with rationale. Keep unresolved
requirements visible. No conformance claim without full applicable coverage.

## Threat model and access

- [ ] Assets, attacker capabilities, entry points, and trust boundaries are named.
- [ ] Authentication and authorization are checked separately for each protected path.
- [ ] Tenant/object ownership is enforced on reads, writes, bulk actions, and exports.
- [ ] Jobs, uploads, webhooks, recovery paths, and admin tools follow the same policy.
- [ ] Password storage and recovery follow `../SKILL.md` §2 and current policy.
- [ ] Token lifetime, rotation, revocation, reuse detection, and termination are tested.
- [ ] Cookie-authenticated state changes have CSRF defense; SameSite alone is insufficient.
- [ ] MFA and step-up controls match the threat model and selected requirement level.

## Input, output, secrets, and data

- [ ] Untrusted input is parsed at ingress; domain invariants stay with their owner.
- [ ] Payload size, collection size, and file/path handling are bounded.
- [ ] Output encoding matches the sink; queries are parameterized.
- [ ] Secrets stay out of source, logs, client bundles, screenshots, and test output.
- [ ] PII is redacted, access-controlled, and governed by retention/deletion rules.
- [ ] TLS, CSP, cookie, CORS, and other headers fit the deployed app.

## Release evidence

- [ ] Control-level tests and threat-model evidence link to the changed flows.
- [ ] Dependency, static-analysis, and secret scans follow repository policy.
- [ ] Unresolved safety findings are assessed against the declared release gate.
- [ ] Each permitted exception has an owner, expiry, mitigation, and rationale.
- [ ] Rollback or containment steps are verified for the actual release surface.
- [ ] Unavailable checks are marked unverified; assessment coverage is explicit.

Use `owasp-top10.md` for implementation examples and `static-analysis.md` for
scan recipes. This checklist does not override stricter release requirements.
