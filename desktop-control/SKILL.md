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

> **This skill is already injected into your system prompt.** Do not run `sed`, `cat`, `head`, or `Read` to load it from disk. Guessing absolute paths like `/Users/*/.codex/skills/...` or `/Users/*/.cli-jaw-*/skills/...` wastes a turn and often targets a file that doesn't exist. If you need a specific reference file (e.g., `reference/computer-use.md`), use `cli-jaw skill read desktop-control <ref-name>`.

## When to use

Trigger on any request that touches a visible UI:

- **User message contains `$computer-use`** → **skip routing analysis**, jump straight to [`reference/computer-use.md`](reference/computer-use.md). Explicit user opt-in. If your CLI isn't codex, stop with `precondition failed: not codex`.
- "open this URL / click this button / type in this field" → read [`reference/cdp.md`](reference/cdp.md)
- "switch Chrome tab / open Finder / click System Settings" → read [`reference/computer-use.md`](reference/computer-use.md)
- "click the thing inside this Canvas / WebGL / iframe" → read [`reference/vision-click.md`](reference/vision-click.md)
- Not sure which path → read [`reference/intent-routing.md`](reference/intent-routing.md) FIRST
- Want a real end-to-end example → read [`reference/control-workflow.md`](reference/control-workflow.md)

## Absolute rules

1. **Announce the path before acting.** First line of every task must be `path=cdp`, `path=computer-use`, or `path=cdp+cu`.
2. **Computer Use always starts with `get_app_state(app)`.** Re-call it on every stale warning and after any state change.
3. **Every action records an `action_class`.** Classes: `state-read`, `element-action`, `value-injection`, `keyboard-action`, `pointer-action`, `pointer-action+vision`.
4. **Never fall back silently.** If the required path is unavailable, stop and report which precondition failed.
5. **Never claim the cursor was visible.** Cursor overlay is best-effort in the current build.
6. **🔍 When uncertain, take a screenshot FIRST.** If you ever find yourself guessing — "is that tab 342 or 357?", "did the click actually land?", "is this the right page?" — **stop** and re-ground via `get_app_state(app)` (Computer Use) or `cli-jaw browser snapshot` (CDP). Never chain actions through uncertainty. Guessing indices or URLs leads to infinite correction loops. If two consecutive actions produced ambiguous state, the **next call must be a state-read**, not another action.

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

- `browser` — CDP command reference (this skill supersedes its coverage).
- `screen-capture` — generic macOS screenshot / webcam / video recording (unchanged).
- `vision-click` — **no longer auto-active**. Absorbed as a tactic in `reference/vision-click.md`. If you need the low-level recipe (NDJSON parsing, DPR correction), run `cli-jaw skill install vision-click`.

## Common failures and the only correct responses

| Symptom | Correct report |
|---|---|
| "I don't see a cursor" | `cursor overlay is best-effort in the current build — action=click(...) succeeded; visible cursor not guaranteed` |
| CDP server not running | `precondition failed: cli-jaw serve not running. Start with 'jaw serve' and retry.` |
| Codex CU app missing | `precondition failed: /Applications/Codex Computer Use.app missing. Recover: jaw doctor --tcc --fix` |
| Stale warning on action | re-call `get_app_state(app)` then retry; log `stale_warning=yes` in the transcript |
| Non-GUI task routed here | `needs boss follow-up: not GUI automation` |
