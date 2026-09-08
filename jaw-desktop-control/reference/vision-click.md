# Vision-click integration

## Decision order

1. Did `cli-jaw browser snapshot --interactive` return a ref? → CDP `click`.
2. Is Computer Use available and the target visible in its state screenshot? →
   **coordinate pointer-action directly.** Preferred for map labels, canvas
   text, and custom renders: it costs no extra model call.
3. Only if there is no ref and direct coordinate clicking is unsuitable →
   `cli-jaw browser vision-click`.

## CDP vision-click (inside Chrome)

Requires the Codex CLI: the provider path shells out to `codex exec`. If the
active CLI is not Codex, that is the precondition behind the first failure-mode
row below.

```bash
cli-jaw browser vision-click "Submit button"        # single click
cli-jaw browser vision-click "Play button" --double # double-click
```

Transcript:

```
path=cdp
action_class=pointer-action+vision
action=vision-click "Submit button"
result=ok
```

## Desktop vision-click (outside Chrome)

Vision picks the coordinates inside the Computer Use path:

1. Read state to capture a screenshot.
2. Ask the vision model for coordinates of the described target.
3. Issue a coordinate pointer-action.

```
path=computer-use
app=<app>
action_class=pointer-action+vision
action=<click at x=812, y=514>   # via vision lookup "Play button"
stale_warning=no
result=ok
```

## Guardrails

- **Always try ref-based click first.** Vision costs tokens and latency.
- **Describe the target, not the pixel.** Good: "Play button in the top-right
  corner". Bad: "the thing".
- **Prefer accessibility targets.** If the latest state read exposes an element
  index, click that instead of a coordinate.
- **Watch the coordinate frame.** The vision model answers in the frame of the
  screenshot it was given. `cli-jaw browser vision-click` converts that to the
  viewport for you; on the Computer Use path the screenshot frame *is* the
  screen frame, so no conversion applies.
- **One attempt per call.** If vision returns nothing useful, report and stop —
  do not retry ten times with rephrasings.

## Failure modes

| Symptom | Report |
|---|---|
| vision-click needs Codex but the active CLI is not Codex | dispatch to `Control` when available, otherwise report `precondition failed: vision-click requires Codex CLI (active: <cli>)` |
| vision model returns "no match" | `vision lookup failed for "<query>" — suggest a more specific description` |
| click executed but nothing happened | log both the query and the coordinates, then re-read state to confirm whether anything changed |

## Why this lives inside desktop-control

Vision-click is one tactic inside the broader "how do I reach a UI target"
problem. Routing lives here; the command encapsulates the low-level recipe
(response parsing, DPR correction, cost and latency) so you rarely need it
directly.
