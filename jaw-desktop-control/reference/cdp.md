# CDP path — `cli-jaw browser`

For anything addressable by Chrome DOM: page text, form fields, buttons inside the page.

## Preconditions

```
cli-jaw browser status
```

- Must report a running session (or `start --agent` first).
- If server is down → report `precondition failed: cli-jaw serve not running` and stop.

## Session commands

```bash
cli-jaw browser status                         # is a session active?
cli-jaw browser start --agent                  # headless automation session (default for agents)
cli-jaw browser start --headless               # manual headless (WSL/CI/Docker)
cli-jaw browser start                          # visible window — only when user explicitly asks
cli-jaw browser navigate "https://example.com" # go to URL
cli-jaw browser open "https://example.com"     # open in new tab
cli-jaw browser tabs                           # list tabs
```

Prefer `--agent`. Plain `start` opens a visible window the user may not want.

## Snapshot + act

```bash
cli-jaw browser snapshot --interactive   # list clickable elements with ref IDs (e1, e2, ...)
cli-jaw browser click e3                 # click by ref
cli-jaw browser type e5 "query" --submit # type + Enter
cli-jaw browser press Enter              # fallback key press
cli-jaw browser screenshot               # save a PNG
cli-jaw browser text                     # dump visible text
```

Ref IDs **reset after every navigate**. Always re-snapshot after navigating.

## Action class mapping (CDP)

| Command | Action class |
|---|---|
| `snapshot`, `text`, `screenshot` | `state-read` |
| `click`, `type ... --submit` | `element-action` |
| `type <ref> "value"` (no submit) | `value-injection` |
| `press Enter` / `press Escape` | `keyboard-action` |

## Transcript format (CDP)

```
path=cdp
url=<current url>
action=<command>
result=ok
```

On error:

```
path=cdp
url=<current url>
action=<command>
result=error: <one-line reason>
```

## Failure modes

- **No ref found** for target → if visible in `get_app_state` screenshot, use Computer Use `click(x, y)` pointer-action. Otherwise report the gap.
- **Navigation drift** between snapshot and click → re-snapshot and retry once; if still off, report.
- **CDP session died mid-task** → report `precondition failed: cdp session terminated` and stop.

## What NOT to do here

- Don't use `curl`/`wget` to "read a page" — always CDP.
- Don't open a visible window just to inspect logs — use the Web UI debug console.
- Don't try coordinate-based click when a ref exists — use the ref.
