---
name: oracle-consult
description: Use Oracle CLI for second-model consultation with selected repo files. Trigger when Codex should ask an external model to review architecture, debug hard failures, audit PRDs/plans, compare approaches, or cross-check risky code with file context. Prefer dry-run and manual approval before any API/browser execution.
---

# Oracle Consult

Use Oracle as an external second-opinion tool, not as a replacement for local
verification. Oracle bundles a prompt plus selected files, then sends them to a
browser or API model. Treat the answer as advisory and verify it against the
codebase and tests.

## Local Policy

Prefer the globally installed `oracle` CLI for normal use. Do not require MCP for
this skill. MCP is an optional convenience bridge only, and it should not be the
first path for broad or sensitive file context because it does not provide a
dry-run preview.

Use `gpt-5-pro` as the default Oracle browser model for this local workflow.
Oracle `0.9.0` was observed resolving Pro browser requests to `gpt-5-pro`, so do
not use ChatGPT UI labels such as `GPT-5.5 Pro` as command defaults.

## Default Rule

Do not start a real Oracle run first. Show help once per session if the CLI has
not been used yet, then preview the file bundle.

```bash
oracle --help
```

```bash
oracle --dry-run summary --files-report \
  -p "<task>" \
  --file "<paths>"
```

If `oracle` is not installed, use the pinned package:

```bash
npx -y @steipete/oracle@0.9.0 --dry-run summary --files-report \
  -p "<task>" \
  --file "<paths>"
```

For sensitive or broad file sets, inspect the actual prompt bundle:

```bash
oracle --dry-run full \
  -p "<task>" \
  --file "<paths>"
```

Use `--dry-run json` when the exact expanded file list or token distribution
needs machine-readable inspection.

## File Selection

Attach only the files needed to answer the question.

Good examples:

```bash
--file src/agent/events.ts
--file tests/events.test.ts
--file "devlog/_plan/parse/*.md"
--file "src/**/*.ts" --file "!src/**/*.test.ts"
```

Avoid by default:

- `.env`, secrets, private keys, tokens, cookies, auth dumps
- whole home directories
- unrelated vendored dependencies
- large generated output
- user data outside the task scope

Use absolute file paths when calling Oracle through MCP or from an uncertain
working directory.

Important Oracle file behavior:

- Default ignored directories include `node_modules`, `dist`, `coverage`, `.git`,
  `.turbo`, `.next`, `build`, and `tmp` unless explicitly selected.
- Globs honor `.gitignore`.
- Symlinks are not followed during glob expansion.
- Dotfiles are filtered unless the pattern explicitly includes a dot segment,
  such as `--file ".github/**"`.
- Files over the default size cap are rejected unless the cap is raised in
  `ORACLE_MAX_FILE_SIZE_BYTES` or `~/.oracle/config.json`.

## Prompt Shape

Oracle starts with no project memory. Include enough context in the prompt.

Use this structure:

```text
Project: <repo/app name and stack>
Goal: <what needs to be reviewed or solved>
Context: <what changed, what failed, what you already tried>
Question: <specific request>
Output: <wanted answer format, risks, tests, smallest patch, etc.>
Constraints: <do not change X, preserve Y, no API cost unless approved, etc.>
```

For plan audits, ask for:

```text
Check whether this plan is sound. Identify blocking risks, stale assumptions,
missing tests, and the smallest safe first PR.
```

## Safe Execution Choices

### Manual paste path

Use this when API/browser automation is risky, the context is sensitive, or the
user wants manual control.

```bash
oracle --render --copy \
  -p "<task>" \
  --file "<paths>"
```

### Browser path

Use this only after the user approves browser automation. It controls a signed-in
browser profile and can take several minutes.

First-time login:

```bash
oracle --engine browser \
  --browser-manual-login \
  --browser-keep-browser \
  --browser-input-timeout 120000 \
  -p "HI"
```

Normal browser run:

```bash
oracle --engine browser \
  --browser-manual-login \
  --browser-auto-reattach-delay 5s \
  --browser-auto-reattach-interval 3s \
  --browser-auto-reattach-timeout 60s \
  --model gpt-5-pro \
  --slug "<short-slug>" \
  -p "<task>" \
  --file "<paths>"
```

Notes:

- Use `gpt-5-pro` as the default browser model unless the user asks for a
  different model.
- Oracle `0.9.0` was observed resolving Pro browser runs to `gpt-5-pro`.
- Do not hard-code ChatGPT UI labels such as `GPT-5.5 Pro` unless verified in a
  fresh run.
- Browser runs can take 10 minutes or longer. This is normal for Pro models.
- Keep the browser window open until Oracle finishes.
- If the run disconnects, reattach instead of starting a duplicate.
- Use `--browser-attachments auto|never|always` when attachment delivery needs
  to be forced. `auto` pastes inline up to Oracle's threshold, then uploads.

### API path

Use this only after explicit user approval because it can spend API tokens.

```bash
oracle --engine api \
  --model gpt-5-pro \
  --slug "<short-slug>" \
  -p "<task>" \
  --file "<paths>"
```

Do not rely on engine auto-selection. If `OPENAI_API_KEY` exists, Oracle may
choose API mode unless `--engine browser` is explicit.

Use API mode for Claude, Grok, Codex, or multi-model runs. Browser mode is the
main path for ChatGPT/GPT and Gemini web flows.

## Session Handling

Use memorable slugs.

```bash
oracle status --hours 72 --limit 50
oracle session <session-id-or-slug> --render
```

If a browser/API run is already active:

1. Check `oracle status`.
2. Attach to the existing session.
3. Do not rerun the same prompt unless the user explicitly wants a fresh run.
4. Use `--force` only when a new browser/API session is intentional.

Oracle stores sessions under `~/.oracle/sessions` unless `ORACLE_HOME_DIR` is
set.

## MCP Notes

Do not install or require Oracle MCP for this skill by default. The global CLI is
enough for the normal workflow and supports the safety features this skill
depends on: `--dry-run`, `--files-report`, `--render`, `--copy`, and direct
session reattach.

Oracle MCP is useful only when an agent runtime explicitly needs structured
`consult` or `sessions` tools. It mirrors the CLI session store, but it does not
provide a dry-run/preflight tool. Therefore, do not use MCP `consult` as the
first safe path for broad or sensitive file context.

If MCP is intentionally needed later, prefer a pinned reproducible template:

```json
{
  "servers": {
    "oracle": {
      "command": "npx",
      "args": ["-y", "@steipete/oracle@0.9.0", "oracle-mcp"]
    }
  }
}
```

Global MCP is acceptable only after local smoke testing:

```bash
npm install -g @steipete/oracle@0.9.0
oracle --version
```

Then:

```json
{
  "servers": {
    "oracle": {
      "command": "oracle-mcp",
      "args": []
    }
  }
}
```

Before relying on global `oracle-mcp`, verify it in the local environment:

```bash
timeout 8s bash -lc 'tail -f /dev/null | oracle-mcp'
```

The expected result is a timeout with no immediate crash.

## Quality Bar

After receiving Oracle output:

1. Separate Oracle's claims from verified facts.
2. Check cited files/paths against the repo.
3. Run local tests or typechecks before accepting recommendations.
4. Record useful findings in the relevant devlog/plan, not in production code.
5. Do not merge or ship solely because Oracle recommended it.

## Common Patterns

Plan audit:

```bash
oracle --dry-run summary --files-report \
  -p "Audit this plan. Find blocking risks, missing tests, stale assumptions, and the smallest safe first PR." \
  --file devlog/_plan/<topic>/*.md
```

Bug investigation:

```bash
oracle --dry-run summary --files-report \
  -p "Investigate this bug from the attached code and tests. Return root cause candidates and the smallest verification plan." \
  --file src/<area>/*.ts \
  --file tests/<area>*.test.ts
```

Architecture cross-check:

```bash
oracle --dry-run summary --files-report \
  -p "Compare these integration options and recommend the lowest-risk first implementation." \
  --file devlog/_plan/<topic>/*.md \
  --file src/<relevant-entrypoint>.ts
```

Long browser review after dry-run approval:

```bash
oracle --engine browser \
  --browser-manual-login \
  --browser-auto-reattach-delay 5s \
  --browser-auto-reattach-interval 3s \
  --browser-auto-reattach-timeout 60s \
  --model gpt-5-pro \
  --slug "<3-5-word-slug>" \
  -p "<standalone project briefing and exact question>" \
  --file "<paths>"
```
