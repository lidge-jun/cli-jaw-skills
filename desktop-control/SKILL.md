---
name: desktop-control
description: "Unified desktop + browser automation. Routes DOM targets to CDP (cli-jaw browser), desktop apps to Computer Use MCP, hybrid combos to both. Codex CLI + macOS required for Computer Use."
metadata:
  {
    "openclaw":
      {
        "emoji": "🖥️",
        "requires":
          {
            "bins": ["cli-jaw"],
            "system": ["macOS", "Google Chrome"],
          },
        "install":
          [
            {
              "id": "brew-cliclick",
              "kind": "brew",
              "formula": "cliclick",
              "bins": ["cliclick"],
              "label": "Install cliclick (optional — pointer-action fallback)",
            },
          ],
      },
  }
---

# Desktop Control

Unified skill for all UI automation. Chooses between CDP and Computer Use based on the target, and reports every action with a `path=` + `action_class=` transcript.

## When to use

Trigger on any request that touches a visible UI:

- "open this URL / click this button / type in this field" → read [`reference/cdp.md`](reference/cdp.md)
- "switch Chrome tab / open Finder / click System Settings" → read [`reference/computer-use.md`](reference/computer-use.md)
- "click the thing inside this Canvas / WebGL / iframe" → read [`reference/vision-click.md`](reference/vision-click.md)
- Not sure which path → read [`reference/intent-routing.md`](reference/intent-routing.md) FIRST

## Absolute rules

1. **Announce the path before acting.** First line of every task must be `path=cdp`, `path=computer-use`, or `path=cdp+cu`.
2. **Computer Use always starts with `get_app_state(app)`.** Re-call it on every stale warning and after any state change.
3. **Every action records an `action_class`.** Classes: `state-read`, `element-action`, `value-injection`, `keyboard-action`, `pointer-action`, `pointer-action+vision`.
4. **Never fall back silently.** If the required path is unavailable, stop and report which precondition failed.
5. **Never claim the cursor was visible.** Cursor overlay is best-effort in the current build.

## Preconditions (Computer Use path)

- macOS only.
- `/Applications/Jaw.app` present (TCC attribution; warn if missing, do not block).
- `/Applications/Codex Computer Use.app` present (blocks if missing — `jaw doctor --tcc --fix`).
- TCC Accessibility + AppleEvents granted to Jaw Agent.
- Active CLI must be Codex — only Codex has `mcp__computer_use__.*` access.

## Transcript format (standard)

CDP action:

```
path=cdp
url=https://example.com
action=click e3
result=ok
```

Computer Use action:

```
path=computer-use
app=Google Chrome
action_class=element-action
action=click(element_index=730)
stale_warning=no
result=ok
```

Hybrid (lookup via CDP, action via Computer Use):

```
path=cdp+cu
lookup=cli-jaw browser snapshot → bbox of "Play"
action_class=pointer-action
action=click(x=812, y=514)
result=ok
```

## Related skills

- `browser` — CDP command reference (this skill replaces its coverage).
- `vision-click` — fallback click for Canvas / iframe targets. Call site is covered here in `reference/vision-click.md`.
- `screen-capture` — generic macOS screenshot / webcam / video recording (unchanged).

## Common failures and the only correct responses

| Symptom | Correct report |
|---|---|
| "I don't see a cursor" | `cursor overlay is best-effort in the current build — action=click(...) succeeded; visible cursor not guaranteed` |
| CDP server not running | `precondition failed: cli-jaw serve not running. Start with 'jaw serve' and retry.` |
| Codex CU app missing | `precondition failed: /Applications/Codex Computer Use.app missing. Recover: jaw doctor --tcc --fix` |
| Stale warning on action | re-call `get_app_state(app)` then retry; log `stale_warning=yes` in the transcript |
| Non-GUI task routed here | `needs boss follow-up: not GUI automation` |
