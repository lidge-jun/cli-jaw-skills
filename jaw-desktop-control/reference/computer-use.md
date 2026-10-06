# Computer Use path

For desktop apps and non-DOM UI. Finder, System Settings, browser chrome, native
dialogs, menu bars, canvas-like regions, and any widget that cannot be addressed
through web DOM refs.

## Establish the surface before the first call

**Computer Use is an MCP tool, not an employee.**
jaw registers the managed `jaw-computer-use` MCP server for every MCP-aware CLI
except Codex. Call its `js` tool (`mcp__jaw-computer-use__js` in Claude). Codex
bosses and employees use Codex's native Computer Use plugin. Both routes use a
CUA JavaScript session; the first call returns its own documentation and initial
UI state. Read that documentation before further calls and use only the API it
describes, such as `cua.getApp(name)`, `app.getAXState()`, `app.click(index|[x,y])`,
`app.typeText`, and `app.pressKey`. Do not assume tool names beyond the exposed
`js` surface or invent other `cua` methods. An enabled plugin is not proof that
its tools are callable.

If no Computer Use surface is exposed, report
`precondition failed: no Computer Use surface`. Install or open the ChatGPT
desktop app with Computer Use, then restart jaw so it registers
`jaw-computer-use`. On Linux, WSL, or Docker there is no Computer Use host;
CDP can serve DOM work only. Never substitute CDP for an explicit
`$computer-use` request.

jaw resolves the newest bundled `cua_repl` under
`~/.codex/plugins/cache/openai-bundled/unified-computer-use/`. It answers
Computer Use app-approval prompts from the run's permission policy: `auto`
approves, `safe` declines. Report a declined prompt as `not approved`.

## What stays true across surfaces

The tool names change; the discipline does not.

- **Read state before acting**, and again after anything that changes the UI or
  focus, after a staleness signal, and whenever confidence drops.
- **Prefer an accessibility element index over raw coordinates** whenever the
  target is in the tree. Indices drift with every state change, so use the ones
  from the latest read.
- **Use coordinates only when the target is visible but absent from the element
  tree** — map labels, canvas text, custom renders.
- **Type only after checking focus.** Use the documented `app.typeText` after
  the latest state proves the cursor is in the intended field.
- **A staleness warning is a signal to re-read, not a failure.** If an action
  provably did not change state and the next one intentionally reuses the same
  fresh tree, you may continue — but never continue through uncertainty.
- **Never claim the cursor was visible.** Cursor overlay is best-effort.

## Platform shape

macOS Computer Use is **app-scoped**: you select an app and read its state.
Windows is **window-scoped**: you enumerate windows and read one window's state.
Linux, WSL and Docker have no Computer Use host; CDP serves separate DOM work.

### macOS preconditions

- The responsible process/binary of the jaw service may lack macOS permission
  to access data from other apps (TCC App Data for the ChatGPT Computer Use
  container). A Terminal-launched jaw without that grant can block on the first
  app call. Report `precondition failed: computer-use app access blocked` and
  point to Privacy & Security for the responsible process/binary; the exact
  pane name varies by macOS version.
- Grant any additional Accessibility or AppleEvents permission requested by
  macOS for the controlling app.

### Windows preconditions

Two Windows results look like success and are not:

- **An app enumeration that answers is not a health check.** It can succeed
  while no window is readable, because it is a local enumeration rather than a
  round trip through the connection.
- **An empty window list usually means the transport is not connected**, not
  that no windows are open. Report it as a precondition failure.

Windows also requires the ChatGPT desktop app with Computer Use running in the
**logged-on** session — a locked screen is fine, logged out is not — and the
Codex desktop plugin cache on that host. The mechanism is the same
`jaw-computer-use` MCP `js` route for non-Codex CLIs and native plugin for Codex.
The app creates the transport endpoint when it starts;
`codex-computer-use.exe` is the **notify client**, not the
server, so confirming that process proves nothing. The app also rewrites
`config.toml` with the current endpoint at launch, so read that file **after**
launching rather than trusting a stored value.

Over SSH you land in a non-interactive session and cannot launch a GUI directly
— use the task scheduler to start it in the logged-on session. Quoting nests
several layers deep (ssh → PowerShell → shell → codex), so upload a script file
rather than composing a one-liner.

## Sandbox flag

`--dangerously-bypass-approvals-and-sandbox` disables **both** approvals and
the sandbox. On Windows it has been the known workaround for the sandbox killing
`codex exec` children — the signature is exit `-1073741502` with an empty
stderr, which reads like a hang rather than a kill.

That does not make the flag routine. It is an attended, explicit user choice,
and cli-jaw does not add or persist it on the user's behalf. **`permissions=auto`
is not an equivalent substitute** — do not reach for it as a quieter way to get
the same effect.

## The state-first rule

Every assistant turn that interacts with an app begins with a state read.

### Screenshot-before-guess (hard rule)

If you are not certain of the current state — which tab is focused, whether a
previous click landed, which element index is the target — **stop and re-read
state before the next action.** Symptoms that demand it immediately:

- You catch yourself writing "maybe 342, or 357".
- A click was issued but you cannot confirm its effect.
- You switched apps and do not know what is foreground.
- Two consecutive actions produced no visible progress.
- You are about to type a long value without checking the cursor location.

Never issue a second action into uncertainty. One extra state read always beats
one wrong click.

### Recovery pattern

1. Re-read state; note the real index of your target.
2. Log `action_class=state-read` with `reason=disambiguation`.
3. Re-issue the intended action using the *fresh* index.
4. Read state once more to confirm the effect.

## Action classes

`state-read`, `element-action`, `value-injection`, `keyboard-action`,
`pointer-action`, `pointer-action+vision`, `stale-recovery`,
`precondition-fail`, `confirmation-prompt`, `transcript-summary`,
`secondary-action`, `scroll-action`, `drag-action`.

## Transcript format

```
path=computer-use
app=<app display name>
action_class=<class>
action=<call + key args>
stale_warning=<yes|no>
result=<ok|error: one-line reason>
```

## Decision aids

- Non-DOM target inside a browser (tab bar, window controls) → Computer Use.
- Dialog or menu the page cannot reach → Computer Use.
- Global shortcut → Computer Use keyboard-action.
- Raw pixel from the user → Computer Use pointer-action.
- Canvas or iframe with no DOM ref, visible in the state screenshot → Computer
  Use pointer-action from those coordinates.

## Never do

- Do not assume a tool name. Establish the surface first.
- Do not treat an enabled plugin as proof its tools are callable.
- Do not assume the cursor is visible.
- Do not silently fall back to CDP when Computer Use is unavailable.
- Do not skip the state read because you remember where the button is.
- Do not resolve uncertainty by trying. Re-read instead.

## After-action report

When a task ends, summarize under `transcript-summary`: the path chosen, the
action classes used, any staleness warnings encountered, and the final result.

## Worked example

See [`workflow-example.md`](workflow-example.md) for an end-to-end trace
covering state-first, element-index targeting, stale recovery, and the CDP
speed switch in sequence.
