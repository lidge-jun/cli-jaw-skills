---
name: insecure-defaults
description: "Detects fail-open insecure defaults (hardcoded secrets, weak auth, permissive security) that allow apps to run insecurely in production. Use when auditing security, reviewing config management, or analyzing environment variable handling."
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Insecure Defaults Detection

Finds **fail-open** vulnerabilities where apps run insecurely with missing configuration. Distinguishes exploitable defaults from fail-secure patterns that crash safely.

- **Fail-open (CRITICAL):** `SECRET = env.get('KEY') or 'default'` → App runs with weak secret
- **Fail-secure (SAFE):** `SECRET = env['KEY']` → App crashes if missing

## Scope

Audit production-reachable code for auth, crypto, API security, deployment configs, secrets management, and environment variable handling.

Skip test fixtures (`test/`, `spec/`, `__tests__/`), example/template files, dev-only tools, documentation examples, build-time config replaced during deploy, and fail-secure patterns (crash-on-missing).

When in doubt: trace the code path — does the app run with the default, or crash?

## Common Rationalizations (reject these)

- "Just a dev default" → if it reaches production code, it's a finding
- "Prod config overrides it" → verify prod config exists; code-level vulnerability remains otherwise
- "Would never run without config" → prove it with code trace; many apps fail silently
- "It's behind auth" → defense in depth; compromised session still exploits weak defaults
- "We'll fix before release" → document now; "later" rarely comes

## Workflow

### 1. Search: discover and scan

Determine language, framework, and project conventions. Identify secret storage, usage patterns, third-party integrations, and crypto config.

Search `**/config/`, `**/auth/`, `**/database/`, and env files for:
- **Fallback secrets:** `getenv.*\) or ['"]`, `process\.env\.[A-Z_]+ \|\| ['"]`, `ENV\.fetch.*default:`
- **Hardcoded credentials:** `password.*=.*['"][^'"]{8,}['"]`, `api[_-]?key.*=.*['"][^'"]+['"]`
- **Weak defaults:** `DEBUG.*=.*true`, `AUTH.*=.*false`, `CORS.*=.*\*`
- **Crypto algorithms:** `MD5|SHA1|DES|RC4|ECB` in security contexts

Tailor search to discovery results. Focus on production-reachable code.

### 2. Verify: trace actual behavior

For each match, trace the code path:
- When is this executed? (startup vs. runtime)
- What happens if the config variable is missing?
- Is there validation enforcing secure config?

### 3. Confirm: production impact

- Config provided in prod → lower severity (still a code-level vulnerability)
- Config missing or uses default → critical

### 4. Report: with evidence
```
Finding: Hardcoded JWT Secret Fallback
Location: src/auth/jwt.ts:15
Pattern: const secret = process.env.JWT_SECRET || 'default';

Verification: App starts without JWT_SECRET; secret used in jwt.sign() at line 42
Production Impact: Dockerfile missing JWT_SECRET
Exploitation: Attacker forges JWTs using 'default', gains unauthorized access
```

## Quick Verification Checklist

**Fallback Secrets:** `SECRET = env.get(X) or Y`
→ Verify: App starts without env var? Secret used in crypto/auth?
→ Skip: Test fixtures, example files

**Default Credentials:** Hardcoded `username`/`password` pairs
→ Verify: Active in deployed config? No runtime override?
→ Skip: Disabled accounts, documentation examples

**Fail-Open Security:** `AUTH_REQUIRED = env.get(X, 'false')`
→ Verify: Default is insecure (false/disabled/permissive)?
→ Safe: App crashes or default is secure (true/enabled/restricted)

**Weak Crypto:** MD5/SHA1/DES/RC4/ECB in security contexts
→ Verify: Used for passwords, encryption, or tokens?
→ Skip: Checksums, non-security hashing

**Permissive Access:** CORS `*`, permissions `0777`, public-by-default
→ Verify: Default allows unauthorized access?
→ Skip: Explicitly configured permissiveness with justification

**Debug Features:** Stack traces, introspection, verbose errors
→ Verify: Enabled by default? Exposed in responses?
→ Skip: Logging-only, not user-facing

For detailed examples and counter-examples, see [examples.md](references/examples.md).
