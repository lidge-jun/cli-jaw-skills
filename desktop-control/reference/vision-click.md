# Vision-click integration (legacy)

> **Preferred approach**: If the target is visible in the `get_app_state` screenshot, use `click(x, y)` pointer-action directly from the screenshot coordinates. This is faster and works on all CLIs. The `cli-jaw browser vision-click` command below is **Codex-only and legacy** — kept for reference only.

## Decision order

1. Did `cli-jaw browser snapshot --interactive` return a ref? → CDP `click`.
2. Is the target visible in the `get_app_state` screenshot? → **`click(x, y)` pointer-action directly.** (Preferred for map labels, canvas text, custom renders.)
3. Only if the target is NOT visible and must be described by text → `cli-jaw browser vision-click` (Codex-only, legacy).

## CDP vision-click (inside Chrome)

```bash
cli-jaw browser vision-click "Submit button"        # single click
cli-jaw browser vision-click "Play button" --double # double-click
```

- Requires **Codex CLI** — only Codex has the vision model hooked in.
- Transcript:

```
path=cdp
action_class=pointer-action+vision
action=vision-click "Submit button"
result=ok
```

## Desktop vision-click (outside Chrome)

This is the `CU-05` contract — vision is used to pick coordinates inside the Computer Use path:

1. `get_app_state(app)` to snapshot state and capture a screenshot.
2. Ask the vision model for coordinates of the described target.
3. `click(x=<vx>, y=<vy>)` via Computer Use pointer-action.

Transcript:

```
path=computer-use
app=<app>
action_class=pointer-action+vision
action=click(x=812, y=514)   # via vision lookup "Play button"
stale_warning=no
result=ok
```

## Guardrails

- **Always try ref-based click first.** Vision-click consumes tokens and adds latency.
- **Describe the target, not the pixel.** Good: `"Play button in the top-right corner"`. Bad: `"the thing"`.
- **Double-check orientation.** The vision model returns coordinates in the screenshot's frame; `cli-jaw browser vision-click` handles the conversion to viewport. For Computer Use, the screenshot frame *is* the screen frame.
- **One attempt per call.** If vision returns nothing useful, report and stop — do not retry 10× with rephrasings.

## Failure modes

| Symptom | Report |
|---|---|
| vision-click needs Codex but active CLI is not Codex | `precondition failed: vision-click requires Codex CLI (active: <cli>)` |
| vision model returns "no match" | `vision lookup failed for "<query>" — suggest a more specific description` |
| click executed but nothing happened | Log both the vision query and the coordinates, then re-snapshot state to confirm whether the page/app changed |

## Why this lives inside desktop-control

`vision-click` is **one specific tactic** inside the broader "how do I reach a UI target" problem. Routing lives here; the `cli-jaw browser vision-click` command encapsulates the low-level recipe (NDJSON parsing, DPR correction, cost/latency) so you almost never need it.

If you do need the low-level recipe (e.g., you're building a new tool that emulates vision-click), the `vision-click` skill is still available as a reference skill — opt in with:

```bash
cli-jaw skill install vision-click
```
