---
name: web-ai
description: "Structured browser web-ai workflow for ChatGPT, Gemini, and Grok in cli-jaw."
---

# Web AI

Use this skill when the task is to ask an AI website through browser control
instead of calling a model API directly.

## Safe Defaults

- Render before sending.
- If the user explicitly says to use `agbrowse` or standalone agbrowse, run
  `agbrowse --help` first, and run `agbrowse web-ai --help` before choosing
  web-ai flags. Treat the current help output as command truth and adapt this
  skill to that surface instead of assuming cli-jaw wrapper parity.
- Use `--inline-only` only when the user explicitly wants pasted inline context.
  Source context should normally be packaged with `--context-from-files` /
  `--context-file`; upload transport creates one `.zip` archive attachment
  containing `CONTEXT_PACKAGE.md` plus the selected source files.
- Do not upload files with `--file` unless explicitly requested. For source
  context, use the context packaging flags first.
- Do not switch models.
- Do not expose arbitrary `evaluate` through web-ai.
- For live ChatGPT/Gemini observation or smoke tests, do not use headless Chrome.
  Use a headed, user-visible 30_browser/CDP session so account gates, Cloudflare,
  tool drawers, upload pickers, and model menus match the real frontend.
- Use `vision-click` only as an explicit fallback when DOM/snapshot cannot see a
  visible UI target.

## Support Labels

| Surface | Label | Notes |
| --- | --- | --- |
| prompt render/context dry-run | ready | browser-free and deterministic |
| ChatGPT/Gemini/Grok live send/poll/query | beta | depends on provider UI/account state |
| ChatGPT semantic resolver and answer artifacts | ready in cli-jaw mirror | mirrors agbrowse Phase 16/17 contracts |
| source audit flags | ready in cli-jaw mirror | `--require-source-audit` fails closed on missing inline sources |
| hosted/cloud/external-CDP operation | deferred | do not claim hosted browser support |

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
cli-jaw browser web-ai query --vendor grok --inline-only --require-source-audit --source-audit-scope "sources checked" --source-audit-date "2026-05-05" --prompt "..."
cli-jaw browser web-ai poll --vendor chatgpt --timeout 1200
cli-jaw browser web-ai capabilities --vendor chatgpt
cli-jaw browser web-ai notifications --vendor chatgpt
cli-jaw browser web-ai stop --vendor chatgpt
```

## Copy Markdown Fallback

Use only when explicitly needed:

```bash
cli-jaw browser web-ai query \
  --vendor chatgpt \
  --inline-only \
  --allow-copy-markdown-fallback \
  --prompt "Return a markdown table."
```

The runtime intercepts the page's `navigator.clipboard.writeText/write` during
the provider Copy button click. It does not read the OS clipboard. The flag is
the explicit policy opt-in for CLI use; do not add `--unsafe-allow`.

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

## Tab pooling and lease contention

Completed provider tabs are kept warm in a per-vendor pool so the next
`send` reuses a tab instead of creating a new one. Defaults (overridable
via env on the agbrowse side):

| Setting | Default | Env Var |
| --- | --- | --- |
| TTL per pooled tab | 15 min | `AGBROWSE_PROVIDER_POOL_TTL` |
| Warm tabs per `(owner,vendor,sessionType,origin,profile)` | 3 | `AGBROWSE_PROVIDER_POOL_MAX_PER_KEY` |
| Global cap on warm provider tabs | 8 | `AGBROWSE_PROVIDER_POOL_GLOBAL_MAX` |

If you hit `Target page... has been closed` while issuing a second
Pro / Deep Think query while another is still polling, that is lease
contention on the per-key cap. Pass `--new-tab` (or its alias
`--parallel`) on the second call to bypass pool reuse and allocate a
fresh provider tab.

## Runtime capabilities

`cli-jaw browser web-ai status --vendor <v> --json` now embeds a
`capabilities[]` array sourced from `src/browser/web-ai/capability-registry.ts`.
Each row carries `{ providerId, capabilityId, family, status, frontendStatus,
mutationAllowed, activationPath, activeStateSignals, failureStage }`.
Scope to a single capability with `--probe <capabilityId>`.

`cli-jaw browser web-ai capabilities` continues to expose the registry
directly (with `--family` / `--frontend-status` filters). agbrowse mirrors
the same hyphenated capability ID convention via its much smaller probe
runtime in `web-ai/capability.mjs`.

Completed `poll`, `query`, and `watch` results may include:

- `answerArtifact`: normalized capture metadata (`capturedBy`,
  `exactnessScore`, text/markdown lengths, warnings).
- `sourceAudit`: inline source coverage report when
  `--require-source-audit` is enabled.

Use `--require-source-audit` for research tasks where bottom-only provider
source drawers are not enough. Pair absence/no-official-response claims with
`--source-audit-scope` and `--source-audit-date`.

## Error taxonomy

Failures from `cli-jaw browser web-ai *` carry a typed JSON envelope with
`errorCode`, `stage`, `retryHint`, `vendor`, `mutationAllowed`,
`selectorsTried`, and optional `evidence`. HTTP responses
(`/api/browser/web-ai/*` 5xx bodies) and CLI `--json` output share the
same shape via `WebAiError.toJSON()`. Initial code list (full catalog in
agbrowse `devlog/03_phase2_errors.md`):

- `cdp.unreachable`, `cdp.target-mismatch`
- `provider.composer-not-visible`, `provider.model-mismatch`,
  `provider.attachment-preflight`, `provider.attachment-evidence-missing`,
  `provider.commit-not-verified`, `provider.poll-timeout`,
  `provider.runtime-disabled`
- `capability.unsupported`
- `context.over-budget`, `context.symlink-rejected`
- `grok.context-pack-not-allowed`
- `internal.unhandled`

Existing cli-jaw error classes map to typed codes via
`fromCliJawStructuredError`:

- `WrongTargetError` → `cdp.target-mismatch` (preserves
  `expectedTargetId` / `actualTargetId` in `evidence`).
- `BrowserCapabilityError` → `capability.unsupported` (preserves
  `capabilityId` / `ownerPrd`).
- `ProviderRuntimeDisabledError` → `provider.runtime-disabled` (preserves
  `vendor` / `stage`).

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
| code-mode artifact extraction | `agbrowse web-ai code-extract --vendor chatgpt --url "https://chatgpt.com/c/<conversation-id>" --output-zip ./result.zip` |

Only switch when the user explicitly asks for the standalone path. The
two runtimes share defaults (ChatGPT/Gemini 1200s, Grok 600s) and the
same `[INSTRUCTIONS]` prompt block, so behavior stays consistent. Do not
run both against the same `--port` at the same time.

When standalone `agbrowse` is explicitly requested, first inspect:

```bash
agbrowse --help
agbrowse web-ai --help
```

Then select flags from the observed help text. The standalone binary can move
faster than the cli-jaw wrapper, so do not invent wrapper-only flags or assume
older aliases when the current help output differs.

### ChatGPT Code Artifact Extraction

ChatGPT code-mode generation and later zip extraction remain standalone
`agbrowse` surfaces until cli-jaw has equivalent command routes, retrieval
runtime, tests, and installed skill docs. When an old ChatGPT conversation still
contains plain assistant text such as `/mnt/data/result.zip`, recover it with:

```bash
agbrowse web-ai code-extract \
  --vendor chatgpt \
  --url "https://chatgpt.com/c/<conversation-id>" \
  --output-zip ./result.zip
```

For multiple zips:

```bash
agbrowse web-ai code-extract \
  --vendor chatgpt \
  --url "https://chatgpt.com/c/<conversation-id>" \
  --multi-zip \
  --output-dir ./artifacts
```

Then verify locally:

```bash
unzip -t ./result.zip
unzip -l ./result.zip
```

The original conversation URL/session/current ChatGPT tab and logged-in
browser profile are still required; a copied `/mnt/data/result.zip` line alone
is not enough.

For new `agbrowse web-ai code` runs, the prompt contract asks ChatGPT to create
`PLAN.md` or `00_plan.md` in every generated code zip, and to use a visible
todo/checklist tool such as `turn_plan.update_turn_plan` only when that tool is
actually available while the response is streaming. Small tasks usually need
5-10 todo items, but complex tasks may use 20 or more. That visible todo UI
may disappear after the answer finishes; do not fail a completed run because
the UI is no longer visible. The durable validation target is the zip-root
`PLAN.md` or `00_plan.md` checklist.

## Context Packaging

Use this when the user asks for max context / current context
packaging before browser submission.

Rules:

- `--file` still means live browser upload. Do not use it for source context.
- `--context-from-files` may be repeated and accepts files, directories, and globs.
- `--context-exclude` may be repeated and accepts glob excludes.
- `--context-file` accepts a newline or JSON list of include/exclude patterns.
- default source-context transport is upload: write one `.zip` archive context
  package and attach it in the ChatGPT/Gemini composer. Do not create a
  temporary `.txt`/`.md` file yourself for source context.
- `--inline-only` or `--context-transport inline` forces the old pasted
  composer path.
- `--max-input` sets the model input-token preflight budget.
- `--max-file-size` defaults to 1 MB per file.
- `context-dry-run --json` omits `composerText` unless `--full` is passed.
- `context-render` prints the `CONTEXT_PACKAGE.md` body that will be placed
  inside the `.zip` archive by live upload transport.
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
  - 2026-06-11 headed UI note: ChatGPT may show a simplified `Intelligence`
    menu instead of the older model row plus effort submenu. The runtime maps
    `instant` and `thinking --effort light` to `Instant`,
    `thinking --effort standard` to `Medium`, `thinking --effort extended` to
    `High`, `thinking --effort heavy` to `Extra High`,
    `pro --effort standard` to `Pro Extended`, and `pro --effort extended` to
    `Pro Extended`.
- Gemini model switching: flash-lite / flash / pro
  - 2026-05-19 headed UI note: the Gemini picker currently exposes visible
    versioned labels such as `3.1 Flash-Lite`, `3 Flash`, and `3.1 Pro`, but
    workflow commands must use stable aliases (`flash-lite`, `flash`, `pro`).
    The runtime normalizes future `3.n` labels generically and keeps legacy
    `fast` as `flash-lite`, while `thinking` maps to `pro`. Deep Think remains
    a separate tool/mode request, not the plain `--model` alias.
- render/status/send/poll/query/watch/watchers/sessions/capabilities/notifications/stop
- long-running watcher startup recovery and channel delivery loop
- observed capability schemas with fail-closed unobserved tools

Future:

- Grok
- Claude
- ChatGPT web search and image generation tool runtime after headed frontend observation
- Gemini image generation runtime after headed frontend observation
- Web UI watcher dashboard
- agbrowse-owned command surfaces: ChatGPT code mode (`agbrowse web-ai code`),
  later code artifact extraction (`agbrowse web-ai code-extract`), multi-zip
  artifact retrieval, and repeatable mixed `agbrowse --file` uploads stay in
  agbrowse until cli-jaw has equivalent command surface, runtime, tests, and
  installed skill docs.
