# Computer Use path

For desktop apps and non-DOM UI. Finder, System Settings, browser chrome, native
dialogs, menu bars, canvas-like regions, and any widget that cannot be addressed
through web DOM refs.

## Establish the surface before the first call

**The Computer Use tool surface belongs to the host and changes between
versions. Do not assume tool names, including the ones you remember from an
earlier build.**

Recent Codex builds expose a **CUA JavaScript session** — a `cua` object
reached through a REPL tool. Older builds exposed individual
`mcp__computer_use__*` MCP tools. A host can also have a Computer Use plugin
installed and enabled while exposing neither: an enabled plugin is not proof
that its tools are callable.

So the first step is always the same:

1. Look at what is actually exposed this session.
2. Whichever surface is present, **its own first call returns its
   documentation.** Read that result and use only the APIs it describes.
3. If no Computer Use surface is exposed, report
   `precondition failed: no Computer Use surface` and stop. Never substitute
   CDP silently.

## What stays true across surfaces

The tool names change; the discipline does not.

- **Read state before acting**, and again after anything that changes the UI or
  focus, after a staleness signal, and whenever confidence drops.
- **Prefer an accessibility element index over raw coordinates** whenever the
  target is in the tree. Indices drift with every state change, so use the ones
  from the latest read.
- **Use coordinates only when the target is visible but absent from the element
  tree** — map labels, canvas text, custom renders.
- **Prefer a targeted value-setting call over focus-only typing.** Type into
  focus only after the latest state proves the cursor is in the intended field.
- **A staleness warning is a signal to re-read, not a failure.**
- **Never claim the cursor was visible.** Cursor overlay is best-effort.

## Platform shape

macOS Computer Use is **app-scoped**: you select an app and read its state.
Windows is **window-scoped**: you enumerate windows and read one window's state.
Linux, WSL and Docker have no Computer Use host — use CDP there.

Two Windows results look like success and are not:

- **An app enumeration that answers is not a health check.** It can succeed
  while no window is readable, because it is a local enumeration rather than a
  round trip through the connection.
- **An empty window list usually means the transport is not connected**, not
  that no windows are open. Report it as a precondition failure.

Windows also requires the desktop app running in the **logged-on** session — a
locked screen is fine, logged out is not. Over SSH you land in a non-interactive
session and cannot launch a GUI directly; upload a script rather than composing
a deeply nested one-liner.

## Sandbox flag

`--dangerously-bypass-approvals-and-sandbox` disables **both** approvals and
the sandbox. On Windows it has been the known workaround for the sandbox killing
`codex exec` children, but that does not make it routine: it is an attended,
explicit user choice. cli-jaw does not add or persist it on the user's behalf.

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

