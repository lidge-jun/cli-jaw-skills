---
name: web-ai
description: "Oracle-style browser web-ai workflow for ChatGPT first slice in cli-jaw."
---

# Web AI

Use this skill when the task is to ask an AI website through `cli-jaw browser`
instead of calling a model API directly. PRD32 first slice supports ChatGPT only.

## Safe Defaults

- Render before sending.
- Use `--inline-only` for every `send` or `query`.
- Do not upload files.
- Do not switch models.
- Do not expose arbitrary `evaluate` through web-ai.
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
cli-jaw browser web-ai stop --vendor chatgpt
```

## Browser Execution Policy

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
- inline prompt
- render/status/send/poll/query/stop

Future:

- Grok
- Gemini / Deep Think
- Claude
- file upload
- model switching
- thinking-time selection
