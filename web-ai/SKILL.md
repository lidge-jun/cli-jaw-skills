---
name: web-ai
description: "Structured browser web-ai workflow for ChatGPT, Gemini, and Grok in cli-jaw."
---

# Web AI

Use this skill when the task is to ask an AI website through browser control
instead of calling a model API directly.

## Safe Defaults

- Render before sending.
- Use `--inline-only` only when the user explicitly wants pasted inline context.
  Source context should normally be packaged as an uploaded
  markdown attachment.
- Do not upload files with `--file` unless explicitly requested. For source
  context, use the context packaging flags first.
- Do not switch models.
- Do not expose arbitrary `evaluate` through web-ai.
- For live ChatGPT/Gemini observation or smoke tests, do not use headless Chrome.
  Use a headed, user-visible 30_browser/CDP session so account gates, Cloudflare,
  tool drawers, upload pickers, and model menus match the real frontend.
- Use `vision-click` only as an explicit fallback when DOM/snapshot cannot see a
  visible UI target.

## Prompt Shape

Build a structured question envelope:

```text
[SYSTEM]
...

[USER]
## Project
...

## Goal
...

## Context
...

## Question
...

## Output
...

## Constraints
...
```

## Commands

```bash
cli-jaw browser web-ai render --vendor chatgpt --prompt "..."
cli-jaw browser web-ai context-dry-run --vendor chatgpt --prompt "..." --context-from-files "src/**/*.ts" --files-report
cli-jaw browser web-ai context-render --vendor chatgpt --prompt "..." --context-from-files "src/**/*.ts"
cli-jaw browser web-ai status --vendor chatgpt
cli-jaw browser web-ai query --vendor chatgpt --prompt "..." --context-from-files "src/foo.ts"
cli-jaw browser web-ai query --vendor chatgpt --inline-only --allow-copy-markdown-fallback --prompt "..."
cli-jaw browser web-ai poll --vendor chatgpt --timeout 1200
cli-jaw browser web-ai capabilities --vendor chatgpt
cli-jaw browser web-ai notifications --vendor chatgpt
cli-jaw browser web-ai stop --vendor chatgpt
```

## Polling Timeouts

`web-ai poll`, `web-ai query`, and `web-ai watch` accept `--timeout <seconds>`.
When omitted, the runtime uses these defaults so heavy reasoning models
(ChatGPT Pro/Heavy, Gemini Deep Think) have room to finish:

| Vendor | Default `--timeout` | Roughly |
| --- | ---: | --- |
| ChatGPT | 1200 | 20 minutes |
| Gemini | 1200 | 20 minutes |
| Grok | 600 | 10 minutes |

Pass `--timeout 1800` (30 min) or higher for unusually long Pro/Deep Think
runs. The provider tab and the cli-jaw browser Chrome process stay open
across a poll timeout — only the polling loop gives up.

## Grok context packaging is fail-closed

`cli-jaw browser web-ai send/query --vendor grok` with `--context-from-files`
/ `--context-file` / `--context-transport upload` throws with
`stage: 'grok-context-pack-not-allowed'`. Pass `--allow-grok-context-pack`
to override deliberately. When the override is used, the runtime emits a
`grok-context-pack-not-recommended` warning. Grok prefers inline prompts
plus an optional single `--file` upload; ChatGPT or Gemini handle context
packages more reliably.

## Standalone agbrowse Alternative

When the user asks to drive a **single Chrome instance** (for example to
keep their own logged-in profile open and not run two CDP sessions), the
same web-ai workflow is available through the standalone `agbrowse` CLI
(`npm install -g agbrowse`). The flags and prompt envelope shape are
identical; only the binary prefix changes.

| `cli-jaw browser` form | `agbrowse` form |
| --- | --- |
| `cli-jaw browser start` | `agbrowse start` |
| `cli-jaw browser status` | `agbrowse status` |
| `cli-jaw browser snapshot --interactive` | `agbrowse snapshot --interactive` |
| `cli-jaw browser web-ai render ...` | `agbrowse web-ai render ...` |
| `cli-jaw browser web-ai query --vendor chatgpt ...` | `agbrowse web-ai query --vendor chatgpt ...` |
| `cli-jaw browser web-ai poll --vendor chatgpt --timeout 1200` | `agbrowse web-ai poll --vendor chatgpt --timeout 1200` |

Only switch when the user explicitly asks for the standalone path. The
two runtimes share defaults (ChatGPT/Gemini 1200s, Grok 600s) and the
same `[INSTRUCTIONS]` prompt block, so behavior stays consistent. Do not
run both against the same `--port` at the same time.

## Context Packaging

Use this when the user asks for max context / current context
packaging before browser submission.

Rules:

- `--file` still means live browser upload. Do not use it for source context.
- `--context-from-files` may be repeated and accepts files, directories, and globs.
- `--context-exclude` may be repeated and accepts glob excludes.
- `--context-file` accepts a newline or JSON list of include/exclude patterns.
- default source-context transport is upload: write one markdown context package
  and attach it in the ChatGPT composer.
- `--inline-only` or `--context-transport inline` forces the old pasted
  composer path.
- `--max-input` sets the model input-token preflight budget.
- `--max-file-size` defaults to 1 MB per file.
- `context-dry-run --json` omits `composerText` unless `--full` is passed.
- `context-render` prints the context package attachment body by default.
- `send/query` with context packaging must fail before browser mutation if token
  budget is exceeded, or if inline transport exceeds the inline character budget.

Example:

```bash
cli-jaw browser web-ai context-dry-run \
  --vendor chatgpt \
  --model pro \
  --prompt "review current context" \
  --context-from-files "src/browser/web-ai/**/*.ts" \
  --context-exclude "**/*.test.ts" \
  --files-report \
  --json
```

## Browser Execution Policy

Live web-ai execution policy:

```text
headed Chrome required
headless forbidden
Codex Cloud out of scope
observed frontend capability -> schema row -> verified mutation
not observed -> fail closed
```

Use the 30_browser-derived loop:

```text
active-tab -> snapshot -> act -> snapshot -> verify
```

Refs are latest-snapshot scoped. Re-run snapshot after navigation, reload,
or any action that can replace the DOM before using an existing ref.

Before sending a prompt, verify the active tab is ChatGPT. If active tab is not
verified, stop and ask the operator to run:

```bash
cli-jaw browser tabs --json
cli-jaw browser tab-switch <target>
```

## Session Handling

`web-ai send` captures a baseline before insertion:

- vendor
- targetId
- URL
- promptHash
- assistantCount

Raw prompt text must not be persisted. Polling only accepts answers that appear
after the saved baseline.

## Current Scope

Current:

- ChatGPT
- Gemini / Deep Think
- inline prompt
- structured context packaging dry-run/render and inline send/query preflight
- ChatGPT file upload
- ChatGPT model switching: instant / thinking / pro
  - 2026-04-30 headed UI note: the visible opener may be the bottom composer
    `button.__composer-pill[aria-haspopup="menu"]` labeled Instant/Thinking/Pro
    or a plain `Heavy` pill, while the older top `model-switcher-dropdown-button`
    can be absent. Treat visible `Heavy` as active ChatGPT Pro/Heavy. For direct
    DOM fallback, open the model pill and select
    `[data-testid="model-switcher-gpt-5-5-pro-thinking-effort"]`; do not click
    generic "Pro" by role/name because the profile menu can also match.
- render/status/send/poll/query/watch/watchers/sessions/capabilities/notifications/stop
- long-running watcher startup recovery and channel delivery loop
- observed capability schemas with fail-closed unobserved tools

Future:

- Grok
- Claude
- ChatGPT web search and image generation tool runtime after headed frontend observation
- Gemini model picker and image generation runtime after headed frontend observation
- Web UI watcher dashboard
