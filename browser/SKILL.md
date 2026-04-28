---
name: browser
description: "Chrome browser control: open pages, take ref snapshots, click, type, screenshot. Requires cli-jaw server running."
metadata:
  {
    "openclaw":
      {
        "emoji": "🌐",
        "requires": { "bins": ["cli-jaw"], "system": ["Google Chrome"] },
        "install":
          [
            {
              "id": "brew-cliclick",
              "kind": "brew",
              "formula": "cliclick",
              "bins": ["cliclick"],
              "label": "Install cliclick (optional, for coordinate-based clicks)",
            },
          ],
      },
  }
---

# Browser Control

Control Chrome through `cli-jaw browser` commands.
Use ref-based snapshots to identify page elements, then click/type by ref ID.

This skill follows the newer `30_browser` workflow shape, adapted for the
server-backed `cli-jaw browser` runtime. Commands that are not implemented in
the current `cli-jaw` runtime are separated under **Planned Runtime Delta** and
must not be used as current commands.

## Prerequisites

- `cli-jaw serve` must be running.
- Google Chrome must be installed.
- `playwright-core` must be installed in the `cli-jaw` project.

## Quick Start

```bash
cli-jaw browser start --agent                  # Automation session (headless, no visible test window)
cli-jaw browser start                          # Interactive browser (manual only)
cli-jaw browser start --headless               # Manual headless mode (server/CI/WSL)
cli-jaw browser navigate "https://example.com" # Go to URL
cli-jaw browser snapshot --interactive         # Interactive elements with ref IDs
cli-jaw browser click e3                       # Click ref e3
cli-jaw browser type e5 "hello" --submit       # Type + Enter
cli-jaw browser screenshot                     # Save screenshot path
```

## Core Workflow

Always follow this pattern:

```text
snapshot --interactive -> act by ref or key -> snapshot -> verify
```

Use a fresh snapshot after navigation, reload, tab changes, or any action that
substantially changes the page. Ref IDs belong to the latest usable snapshot and
can go stale.

## Current Commands

These commands are implemented in the current `cli-jaw browser` runtime.

### Browser Management

```bash
cli-jaw browser start [--port <auto>] [--headless] [--agent]
cli-jaw browser stop
cli-jaw browser status
cli-jaw browser reset [--force]
```

- `--agent` enables an automated headless session.
- Plain `browser start` is for user-requested interactive browsing.
- `reset` clears the browser profile and screenshots; use only when the user
  explicitly wants a reset or you have confirmed it.

### Observe

```bash
cli-jaw browser snapshot
cli-jaw browser snapshot --interactive
cli-jaw browser snapshot --interactive --max-nodes 30 --json
cli-jaw browser screenshot
cli-jaw browser screenshot --full-page
cli-jaw browser screenshot --ref e5
cli-jaw browser screenshot --json
cli-jaw browser screenshot --clip 0 0 320 180 --json
cli-jaw browser text
cli-jaw browser text --format html
cli-jaw browser get-dom --selector ".card" --max-chars 2000 --json
cli-jaw browser console --json --limit 20
cli-jaw browser network --json --limit 20
```

### Snapshot Output Example

```text
e1   link       "Gmail"
e2   link       "Images"
e3   textbox    "Search"           <- To type here: type e3 "query"
e4   button     "Google Search"    <- To click: click e4
e5   button     "I'm Feeling Lucky"
```

### Act

```bash
cli-jaw browser click e3
cli-jaw browser click e3 --double
cli-jaw browser click e3 --right
cli-jaw browser type e3 "hello"
cli-jaw browser type e3 "hello" --submit
cli-jaw browser press Enter
cli-jaw browser press Escape
cli-jaw browser press Tab
cli-jaw browser hover e5
cli-jaw browser mouse-click 400 300
cli-jaw browser mouse-click 400 300 --double
cli-jaw browser select e7 "option1"
cli-jaw browser drag e3 e5
cli-jaw browser move-mouse 400 300
cli-jaw browser mouse-down
cli-jaw browser mouse-up --right
```

### Navigate and Inspect

```bash
cli-jaw browser navigate "https://example.com"
cli-jaw browser open "https://example.com"
cli-jaw browser tabs
cli-jaw browser tabs --json
cli-jaw browser active-tab --json
cli-jaw browser tab-switch 2
cli-jaw browser reload
cli-jaw browser resize 1440 900
cli-jaw browser scroll --x 0 --y 1000
cli-jaw browser wait-for-selector ".toast-success" --timeout 30000
cli-jaw browser wait-for-text "Dashboard" --timeout 30000
cli-jaw browser evaluate "document.title"
```

`evaluate` is a top-level browser diagnostic command. Do not expose arbitrary
user-provided JavaScript through higher-level vendor workflows such as web-ai.

## Common Workflows

### AI Web Workflows

For ChatGPT web-ai workflows, use the `web-ai` skill. The browser skill owns
primitive page control; `web-ai` owns Oracle-style question rendering, active-tab
safety, and response baseline handling.

### Web Search

```bash
cli-jaw browser start --agent
cli-jaw browser navigate "https://www.google.com"
cli-jaw browser snapshot --interactive
cli-jaw browser type e3 "search query" --submit
cli-jaw browser snapshot --interactive
cli-jaw browser click e7
```

### Form Filling

```bash
cli-jaw browser snapshot --interactive
cli-jaw browser type e1 "John Doe"
cli-jaw browser type e2 "john@example.com"
cli-jaw browser click e3
cli-jaw browser snapshot
```

### Read Page Content

```bash
cli-jaw browser navigate "https://news.ycombinator.com"
cli-jaw browser text
cli-jaw browser text --format html
cli-jaw browser snapshot --interactive
```

## Planned Runtime Delta

The copied `30_browser` reference documents a richer command surface. These are
planned `cli-jaw browser` parity targets, not current commands unless the runtime
has been upgraded in a later PRD.

### Observe and Diagnostics

```bash
cli-jaw browser console --clear --reload --duration 3000
cli-jaw browser network --reload --duration 1000
cli-jaw browser wait 2000
```

### Actions

```bash
cli-jaw browser resize 0 0 --fullscreen
cli-jaw browser scroll down
cli-jaw browser scroll up --amount 1000
```

### Navigation and Sync

`wait-for <ref>` is deprecated in the reference design because refs are
snapshot-scoped. Prefer selector/text waits.

## Recovery Strategy

If something goes wrong, stop and inspect state before the next action.

1. `snapshot` fails -> take `screenshot` for visual inspection.
2. Ref not found -> re-run `snapshot --interactive`; refs can go stale.
3. Async UI not ready -> use `wait-for-selector` or `wait-for-text`.
4. CDP connection fails -> report the exact error, then use `status`; only
   stop/start when that is the selected recovery path.
5. Chrome/profile is truly stuck -> ask before `reset` unless the user already
   requested destructive reset.
6. DOM ref unavailable -> use the `vision-click` skill only after confirming no
   usable ref exists.

## Environment Variables

| Variable | Description |
| --- | --- |
| `CHROME_HEADLESS=1` | Enable headless mode for manual starts. |
| `CHROME_NO_SANDBOX=1` | Disable Chrome sandbox for Docker/CI only. |

The default CDP port is derived from the `cli-jaw` server port. Use
`cli-jaw browser start --port <port>` only when you need an explicit override.

## Headless Mode

```bash
cli-jaw browser start --headless
cli-jaw browser start --agent
CHROME_HEADLESS=1 cli-jaw browser start
```

Use `--agent` for automation. It avoids popping a visible browser window.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| CDP connection refused | Chrome not started or wrong port | `cli-jaw browser status`, then start with the expected port |
| Windows only opens test browser | Chrome singleton absorbed launch | Close all Chrome windows, then use `start --agent` |
| Headless CDP not opening | headless not requested in GUI-less env | Add `--headless` or use `--agent` |
| Port conflict | another process owns the CDP port | choose a different `--port` |
| Snapshot too large | page has many nodes | planned: `--max-nodes`; current: use `--interactive` |

## Notes

- Ref IDs are short-lived and should be treated as latest-snapshot scoped.
- Always re-run `snapshot --interactive` after navigation or major page changes.
- Prefer `--interactive` for token budget.
- Screenshots save to `~/.cli-jaw/screenshots/`.
- `start --agent` should be the default for agent automation.
- Non-DOM elements such as Canvas, WebGL, cross-origin iframes, and custom UI
  should use the `vision-click` skill only as an explicit fallback.
