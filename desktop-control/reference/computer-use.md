# Computer Use path

For desktop apps and non-DOM UI. Finder, System Settings, Chrome tab bar, native dialogs, menu bars, canvas-like regions, and any widget that cannot be addressed through web DOM refs.

## Current tool surface

Use the Computer Use tools exposed by the active runtime. The current contract is:

| Tool | Use |
|---|---|
| `list_apps()` | Discover available/recent apps when the app name is unknown. |
| `get_app_state(app)` | Start or refresh an app session; returns screenshot plus accessibility tree. Required before interaction each assistant turn. `app` may be a display name, bundle identifier, or full app path. |
| `click(app, element_index, click_count?, mouse_button?)` | Click an accessibility element from the latest state. |
| `click(app, x, y, click_count?, mouse_button?)` | Click raw screenshot/screen coordinates. |
| `drag(app, from_x, from_y, to_x, to_y)` | Drag by coordinates. |
| `press_key(app, key)` | Send a key or key combination such as `Return`, `Tab`, or `super+c`. |
| `scroll(app, element_index, direction, pages)` | Scroll a scrollable accessibility element. |
| `select_text(app, element_index, text, selection?, prefix?, suffix?)` | Select exact text inside a text element, or place the cursor before/after it. Use prefix/suffix when the target text is not unique. |
| `set_value(app, element_index, value)` | Set a specific editable accessibility element. |
| `type_text(app, text)` | Type literal text into current focus. Use only after verifying focus. |
| `perform_secondary_action(app, element_index, action)` | Invoke a secondary accessibility action exposed by an element. |

## Preconditions (check before first action)

- Platform: `macOS`.
- The active agent runtime exposes the Computer Use tools listed above.
- If the app is not obvious, call `list_apps()` before `get_app_state(app)`.
- TCC Accessibility and AppleEvents are granted to the controlling app.
- In cli-jaw packaged installs, `/Applications/Jaw.app` and `/Applications/Codex Computer Use.app` may be required for TCC attribution. Treat missing bundles as setup failures when this path was explicitly requested.

If any blocker fails, stop and report: `precondition failed: <name>`. Do not switch to CDP.

## The state-first rule

Every assistant turn that interacts with an app begins with `get_app_state(app)`. The returned state includes a screenshot and element indices used by subsequent actions.

- Call `get_app_state` again after any action that changes the UI or focus.
- When the server returns `stale_warning`, re-call `get_app_state` before retrying — it is a signal, not a failure.
- If an action does not change state and the next action uses the same fresh tree intentionally, you may continue; do not continue through uncertainty.

### Screenshot-before-guess (hard rule)

If at any point you are **not 100% certain** of the current state — which tab is focused, whether a previous click landed, whether the page changed, which element index corresponds to the target — **stop and take a screenshot** via `get_app_state(app)` before the next action. Symptoms that demand an immediate state-read:

- You catch yourself writing "maybe 342, or 357" — guessing indices.
- A click was issued but you can't confirm its effect.
- You navigated/switched apps and don't know what's foreground.
- Two consecutive actions produced no visible progress.
- You're about to type a long value without checking the cursor is in the right field.

Rule: **never issue a second action into uncertainty**. The only correct next call is `get_app_state(app)`. This is cheap; infinite correction loops are not.

### Recovery pattern (concrete)

When you notice ambiguity mid-task, follow this exact sequence:

1. `get_app_state(app)` — re-ground; note the real element_index of your target.
2. Log `action_class=state-read` with a one-line note (`reason=disambiguation`).
3. Re-issue the intended action using the *fresh* element_index.
4. After that action, `get_app_state(app)` once more to confirm the effect.

Never skip step 1 to "save a call." One extra state-read always beats one wrong click.

## Action classes (contract IDs from doc 21)

| Class | Contract | Example |
|---|---|---|
| `state-read` | `CU-00` | `get_app_state("Finder")` |
| `element-action` | `CU-01` | `click(element_index=730)`; `select_text(element_index=12, text="target")` — element from last state |
| `value-injection` | `CU-02` | `set_value(element_index=12, value="search text")`; `type_text(text)` only after focus verification |
| `keyboard-action` | `CU-03` | `press_key(key="super+Tab")` |
| `pointer-action` | `CU-04` | `click(x=812, y=514)` — raw pixel |
| `pointer-action+vision` | `CU-05` | vision-lookup → `click(x,y)` (see `reference/vision-click.md`) |
| `stale-recovery` | `CU-06` | re-read state after stale warning |
| `precondition-fail` | `CU-07` | report + stop |
| `confirmation-prompt` | `CU-08` | ask user before destructive action |
| `transcript-summary` | `CU-09` | summarize transcript to boss |
| `secondary-action` | `CU-10` | `perform_secondary_action(element_index=44, action="AXShowMenu")` |
| `scroll-action` | `CU-11` | `scroll(element_index=9, direction="down", pages=0.5)` |
| `drag-action` | `CU-12` | `drag(from_x=100, from_y=100, to_x=400, to_y=100)` |

## Transcript format (Computer Use)

```
path=computer-use
app=<app display name>
action_class=<class>
action=<tool call + key args>
stale_warning=<yes|no>
result=ok
```

On failure:

```
path=computer-use
app=<app display name>
action_class=<class>
action=<tool call + key args>
stale_warning=<yes|no>
result=error: <one-line reason>
```

## Decision aids

- Non-DOM target inside Chrome (tab bar, window controls) → Computer Use.
- Dialog or menu the page can't reach → Computer Use.
- "Press Command-W" / global shortcut → Computer Use keyboard-action.
- Select or place the cursor within known text → Computer Use `select_text(...)` element-action, then re-read or inject text intentionally.
- Raw pixel from the user ("click 812, 514") → Computer Use pointer-action.
- Canvas / iframe with no DOM ref, visible in screenshot → Computer Use pointer-action `click(x, y)` directly from screenshot coordinates.
- Canvas / iframe not visible, need text description to find → Computer Use pointer-action+vision (legacy, see `reference/vision-click.md`).

## Never do

- Don't assume the cursor is visible. Report action success/failure, never "the cursor moved there".
- Don't silently fall back to CDP if Computer Use is unavailable — report and stop.
- Don't skip `get_app_state` because "you remember where the button is". Element indices drift with every state change.
- Don't run two Computer Use actions against the same app without re-reading state in between if the previous action changed anything.
- Don't resolve uncertainty by trying. "Let me click 342, if not, try 357" is forbidden — take a screenshot.
- Don't use keyboard shortcuts to select text when `select_text` can target the exact text in the latest accessibility tree.
- Don't use `type_text(app, text)` as a shortcut for targeted form entry unless focus was verified in the latest state.

## Worked example

See [`reference/control-workflow.md`](control-workflow.md) for a full Chrome → web-app trace that demonstrates state-first, element_index targeting, stale recovery, and the CDP speed switch in sequence.

## After-action report (for boss)

When a task ends, summarize under `CU-09 transcript-summary`: the path chosen, the action classes used, any stale warnings encountered, and the final result.
