# Computer Use path — `mcp__computer_use__.*`

For desktop apps and non-DOM UI. Finder, System Settings, Chrome tab bar, Spotify window, any native widget. Only reachable from the Codex CLI.

## Preconditions (check before first action)

- Platform: `macOS`.
- `/Applications/Jaw.app` present (warn-only; missing means TCC attribution falls back to node).
- `/Applications/Codex Computer Use.app` present (blocking — run `jaw doctor --tcc --fix` if missing).
- TCC Accessibility + AppleEvents granted to Jaw Agent.

If any blocker fails, stop and report: `precondition failed: <name>`. Do not switch to CDP.

## The state-first rule

Every interaction with an app begins with `get_app_state(app)`. The returned state includes element indices used by subsequent actions.

- Call `get_app_state` again after any action that changes the UI.
- When the server returns `stale_warning`, re-call `get_app_state` before retrying — it is a signal, not a failure.

### 🔍 Screenshot-before-guess (hard rule)

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
| `element-action` | `CU-01` | `click(element_index=730)` — element from last state |
| `value-injection` | `CU-02` | `type_into(element_index=12, value="password")` |
| `keyboard-action` | `CU-03` | `hotkey(["cmd", "tab"])` |
| `pointer-action` | `CU-04` | `click(x=812, y=514)` — raw pixel |
| `pointer-action+vision` | `CU-05` | vision-lookup → `click(x,y)` (see `reference/vision-click.md`) |
| `stale-recovery` | `CU-06` | re-read state after stale warning |
| `precondition-fail` | `CU-07` | report + stop |
| `confirmation-prompt` | `CU-08` | ask user before destructive action |
| `transcript-summary` | `CU-09` | summarize transcript to boss |

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
- "Press ⌘W" / global shortcut → Computer Use keyboard-action.
- Raw pixel from the user ("click 812, 514") → Computer Use pointer-action.
- Canvas / iframe with no DOM ref, visible in screenshot → Computer Use pointer-action `click(x, y)` directly from screenshot coordinates.
- Canvas / iframe not visible, need text description to find → Computer Use pointer-action+vision (legacy, see `reference/vision-click.md`).

## Never do

- Don't assume the cursor is visible. Report action success/failure, never "the cursor moved there".
- Don't silently fall back to CDP if Computer Use is unavailable — report and stop.
- Don't skip `get_app_state` because "you remember where the button is". Element indices drift with every state change.
- Don't run two Computer Use actions against the same app without re-reading state in between if the previous action changed anything.
- Don't resolve uncertainty by trying. "Let me click 342, if not, try 357" is forbidden — take a screenshot.

## Worked example

See [`reference/control-workflow.md`](control-workflow.md) for a full Chrome → web-app trace that demonstrates state-first, element_index targeting, stale recovery, and the CDP speed switch in sequence.

## After-action report (for boss)

When a task ends, summarize under `CU-09 transcript-summary`: the path chosen, the action classes used, any stale warnings encountered, and the final result.
