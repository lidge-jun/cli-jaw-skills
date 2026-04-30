---
name: web-ai
description: "Oracle-style browser web-ai workflow for ChatGPT first slice in cli-jaw."
---

# Web AI

Use this skill when the task is to ask an AI website through browser control
instead of calling a model API directly.

## Safe Defaults

- Render before sending.
- Use `--inline-only` for every `send` or `query`.
- Do not upload files.
- Do not switch models.
- Do not expose arbitrary `evaluate` through web-ai.
- For live ChatGPT/Gemini observation or smoke tests, do not use headless Chrome.
  Use a headed, user-visible 30_browser/CDP session so account gates, Cloudflare,
  tool drawers, upload pickers, and model menus match the real frontend.
- Use `vision-click` only as an explicit fallback when DOM/snapshot cannot see a
  visible UI target.

## Prompt Shape

Build an Oracle-style question envelope:

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
cli-jaw browser web-ai status --vendor chatgpt
cli-jaw browser web-ai query --vendor chatgpt --inline-only --prompt "..."
cli-jaw browser web-ai poll --vendor chatgpt --timeout 600
cli-jaw browser web-ai capabilities --vendor chatgpt
cli-jaw browser web-ai notifications --vendor chatgpt
cli-jaw browser web-ai stop --vendor chatgpt
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
- ChatGPT file upload
- ChatGPT model switching: instant / thinking / pro
  - 2026-04-30 headed UI note: the visible opener may be the bottom composer
    `button.__composer-pill[aria-haspopup="menu"]` labeled Instant/Thinking/Pro,
    while the older top `model-switcher-dropdown-button` can be absent. Do not
    click generic "Pro" by role/name because the profile menu can also match.
- render/status/send/poll/query/watch/watchers/sessions/capabilities/notifications/stop
- long-running watcher startup recovery and channel delivery loop
- observed capability schemas with fail-closed unobserved tools

Future:

- Grok
- Claude
- ChatGPT web search and image generation tool runtime after headed frontend observation
- Gemini model picker and image generation runtime after headed frontend observation
- Web UI watcher dashboard
