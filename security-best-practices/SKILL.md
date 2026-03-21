---
name: "security-best-practices"
description: "Perform language and framework specific security best-practice reviews and suggest improvements. Trigger only when the user explicitly requests security best practices guidance, a security review/report, or secure-by-default coding help. Trigger only for supported languages (python, javascript/typescript, go). Do not trigger for general code review, debugging, or non-security tasks."
---

# Security Best Practices

## Workflow

1. **Identify languages and frameworks** in scope — inspect the repo if unclear. Cover both frontend and backend for web apps.
2. **Load matching references** from `references/`. Filename format: `<language>-<framework>-<stack>-security.md`. Also check `<language>-general-<stack>-security.md`. For unspecified web frontends, check `javascript-general-web-frontend-security.md`.
3. **If no references match**, apply well-known security practices for the detected stack. When generating a report, note that concrete guidance is unavailable.

## Modes

1. **Secure-by-default coding** — apply guidance to all new code going forward
2. **Passive detection** — flag critical vulnerabilities encountered while working; focus on highest-impact issues
3. **Security report** — produce a prioritized report (see Report Format below), then offer to fix findings

## Overrides

Project docs or prompt files may override specific practices. Respect these overrides — suggest documenting the rationale so future work stays consistent.

## Report Format

Write to `security_best_practices_report.md` (or user-specified path).

- Executive summary at top
- Sections grouped by severity (critical → low)
- Each finding has a numeric ID, file path with line numbers, and (for critical) a one-sentence impact statement
- After writing, summarize findings to the user and note the file location

## Fixes

- Fix one finding at a time with clear comments explaining the security rationale
- Consider regression risk — insecure code is often depended on elsewhere. A careful, project-aware fix is better than a quick one
- Follow the project's commit and testing workflows; use clear commit messages referencing the finding
- Ask the user before applying fixes from a report; notify and ask for critical passive findings

## General Security Advice

- **Public resource IDs**: use UUID4 or random hex instead of auto-incrementing integers — prevents enumeration and ID guessing
- **TLS/HSTS**: avoid flagging missing TLS in dev environments. Set `Secure` cookies only when the app runs over TLS (provide an env flag to toggle). Avoid recommending HSTS — misconfiguration causes lasting outages and user lockout
