---
name: jaw-desktop-control
description: "Unified desktop + browser automation. Routes DOM targets to CDP (cli-jaw browser), desktop apps to jaw-computer-use MCP or Codex native Computer Use, and hybrid work to both. macOS is app-scoped and Windows is window-scoped."
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

> **This skill is already injected into your system prompt.** Do not run `sed`, `cat`, `head`, or `Read` to load it from disk. Guessing absolute paths like `/Users/*/.codex/skills/...` or `/Users/*/.cli-jaw-*/skills/...` wastes a turn and often targets a file that doesn't exist. If you need a specific reference file (e.g., `reference/computer-use.md`), use `cli-jaw skill read jaw-desktop-control <ref-name>`.

## When to use

Trigger on any request that touches a visible UI:

- **User message contains `$computer-use` or `/computer-use`** → **skip routing analysis**, jump straight to [`reference/computer-use.md`](reference/computer-use.md). Explicit user opt-in. If no Computer Use surface is exposed, stop with `precondition failed: no Computer Use surface`.
- "open this URL / click this button / type in this field" → read [`reference/cdp.md`](reference/cdp.md)
- "switch Chrome tab / open Finder / click System Settings" → read [`reference/computer-use.md`](reference/computer-use.md)
- "click the thing inside this Canvas / WebGL / iframe" → read [`reference/vision-click.md`](reference/vision-click.md)
- Not sure which path → read [`reference/intent-routing.md`](reference/intent-routing.md) FIRST
- Want a real end-to-end example → read [`reference/workflow-example.md`](reference/workflow-example.md)

## Absolute rules

1. **Announce the path before acting.** First line of every task must be `path=cdp`, `path=computer-use`, or `path=cdp+cu`.
2. **Computer Use always starts each assistant turn with a state read before interacting.** Re-read on stale warnings, after actions that change UI state, and whenever confidence drops.
3. **Every meaningful action records an `action_class`.** Classes: `state-read`, `element-action`, `value-injection`, `keyboard-action`, `pointer-action`, `pointer-action+vision`, `scroll-action`, `drag-action`, `secondary-action`.
4. **Never fall back silently.** If the required path is unavailable, stop and report which precondition failed.
5. **Never claim the cursor was visible.** Cursor overlay is best-effort in the current build.
6. **When uncertain, take a screenshot FIRST.** If you ever find yourself guessing — "is that tab 342 or 357?", "did the click actually land?", "is this the right page?" — **stop** and re-ground via the platform's state read (Computer Use) or `cli-jaw browser snapshot` (CDP). Never chain actions through uncertainty. Guessing indices or URLs leads to infinite correction loops. If two consecutive actions produced ambiguous state, the **next call must be a state-read**, not another action.

## Preconditions (Computer Use path)

- macOS or Windows with the ChatGPT desktop app and Computer Use. jaw resolves the newest bundled `cua_repl` under `~/.codex/plugins/cache/openai-bundled/unified-computer-use/`. Linux, WSL, and Docker have no Computer Use host — CDP is available only for DOM work, never as a substitute for an explicit `$computer-use` request.
- **Computer Use is an MCP tool, not an employee.** For every MCP-aware jaw CLI except Codex, use the managed `jaw-computer-use` server's `js` tool (Claude: `mcp__jaw-computer-use__js`). Codex bosses and employees use Codex's native Computer Use plugin. Read [`reference/computer-use.md`](reference/computer-use.md) before the first call; the first tool call returns its own `cua` API documentation. Use only the documented API. An enabled plugin is not proof its tool is callable.
- macOS Computer Use is app-scoped: select an app, then read its state. Windows is window-scoped: enumerate windows, then read one window's state.
- On Windows an enumeration that answers proves nothing about the connection, and an empty window list usually means the transport is not connected rather than that no windows are open.
- jaw answers Computer Use app-approval prompts from the run's permission policy: `auto` approves, `safe` declines. Report a declined prompt as `not approved`.
- On macOS, the responsible jaw service process/binary may need permission to access data from other apps. If the first app call blocks, report `precondition failed: computer-use app access blocked` and explain the App Data permission in Privacy & Security; the pane name varies by macOS version.
- Windows: the ChatGPT desktop app must be running in the logged-on session and its transport connected. A locked screen is fine; logged out is not.

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
| No Computer Use surface exposed | `precondition failed: no Computer Use surface` — install/open the ChatGPT desktop app with Computer Use, then restart jaw so it registers `jaw-computer-use` |
| First Computer Use app call blocks on macOS | `precondition failed: computer-use app access blocked` — check the jaw service process/binary's App Data permission in Privacy & Security |
| Computer Use app approval declined under `safe` | `not approved` |
| Stale warning on action | re-read state then retry; log `stale_warning=yes` in the transcript |
| Non-GUI task routed here | `needs boss follow-up: not GUI automation` |
