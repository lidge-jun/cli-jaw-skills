---
name: desktop-control
description: "Unified desktop + browser automation. Routes DOM targets to CDP (cli-jaw browser), desktop apps to Computer Use, hybrid combos to both. Codex desktop/CLI required for Computer Use; macOS is app-scoped and Windows is window-scoped."
metadata:
  {
    "openclaw":
      {
        "emoji": "🖥️",
        "requires":
          { "bins": ["cli-jaw"], "system": ["Google Chrome"] },
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

Unified skill for all UI automation. Chooses between CDP and Computer Use based on the target, and reports meaningful actions with a `path=` + `action_class=` transcript.

> **This skill is already injected into your system prompt.** Do not run `sed`, `cat`, `head`, or `Read` to load it from disk. Guessing absolute paths like `/Users/*/.codex/skills/...` or `/Users/*/.cli-jaw-*/skills/...` wastes a turn and often targets a file that doesn't exist. If you need a specific reference file (e.g., `reference/computer-use.md`), use `cli-jaw skill read desktop-control <ref-name>`.

## When to use

Trigger on any request that touches a visible UI:

- **User message contains `$computer-use` or `/computer-use`** → **skip routing analysis**, jump straight to [`reference/computer-use.md`](reference/computer-use.md). Explicit user opt-in. If Computer Use tools are not available, stop with `precondition failed: computer-use unavailable`.
- "open this URL / click this button / type in this field" → read [`reference/cdp.md`](reference/cdp.md)
- "switch Chrome tab / open Finder / click System Settings" → read [`reference/computer-use.md`](reference/computer-use.md)
- "click the thing inside this Canvas / WebGL / iframe" → read [`reference/vision-click.md`](reference/vision-click.md)
- Not sure which path → read [`reference/intent-routing.md`](reference/intent-routing.md) FIRST
- Want a real end-to-end example → read [`reference/control-workflow.md`](reference/control-workflow.md)

## Absolute rules

1. **Announce the path before acting.** First line of every task must be `path=cdp`, `path=computer-use`, or `path=cdp+cu`.
2. **Computer Use always starts each assistant turn with a state read before interacting.** macOS: `get_app_state(app)`. Windows: `get_window_state({app, id})`. Re-call it on stale warnings, after actions that change UI state, and whenever confidence drops.
3. **Every meaningful action records an `action_class`.** Classes: `state-read`, `element-action`, `value-injection`, `keyboard-action`, `pointer-action`, `pointer-action+vision`, `scroll-action`, `drag-action`, `secondary-action`.
4. **Never fall back silently.** If the required path is unavailable, stop and report which precondition failed.
5. **Never claim the cursor was visible.** Cursor overlay is best-effort in the current build.
6. **When uncertain, take a screenshot FIRST.** If you ever find yourself guessing — "is that tab 342 or 357?", "did the click actually land?", "is this the right page?" — **stop** and re-ground via the platform's state read (Computer Use) or `cli-jaw browser snapshot` (CDP). Never chain actions through uncertainty. Guessing indices or URLs leads to infinite correction loops. If two consecutive actions produced ambiguous state, the **next call must be a state-read**, not another action.

## Preconditions (Computer Use path)

- macOS or Windows. Linux, WSL, and Docker have no Computer Use host — use CDP there.
- **The two platforms expose different APIs.** macOS is app-scoped, Windows is window-scoped. Read [`reference/computer-use.md`](reference/computer-use.md) before the first call.
  - macOS tools: `list_apps`, `get_app_state`, `click`, `drag`, `press_key`, `scroll`, `select_text`, `set_value`, `type_text`, `perform_secondary_action`.
  - Windows tools: `list_windows`, `get_window_state`, `activate_window`, `get_window`, `click`, `drag`, `press_key`, `scroll`, `set_value`, `type_text`, `launch_app`, `list_apps`, `perform_secondary_action`. There is **no** `get_app_state` and **no** `select_text`.
- macOS: start a session by selecting the app display name, bundle identifier, or full app path. Use `list_apps` if the app is unknown.
- Windows: start from `list_windows()`, then `get_window_state({app, id})`. Calls must run inside `node_repl` — a bare `node.exe` silently falls back to a helper that sees zero windows.
- If packaged through cli-jaw, `/Applications/Jaw.app` and `/Applications/Codex Computer Use.app` may be required for TCC attribution. Missing app bundles are a setup issue, not a reason to silently switch paths.
- macOS: TCC Accessibility and AppleEvents must be granted to the controlling app.
- Windows: the Codex desktop app must be running in the logged-on session — it creates the named pipe. A locked screen is fine; logged out is not.

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
| Computer Use tools missing | `precondition failed: computer-use unavailable` |
| cli-jaw CU app missing in packaged install | `precondition failed: /Applications/Codex Computer Use.app missing. Recover: jaw doctor --tcc --fix` |
| Stale warning on action | re-call `get_app_state(app)` then retry; log `stale_warning=yes` in the transcript |
| Non-GUI task routed here | `needs boss follow-up: not GUI automation` |
