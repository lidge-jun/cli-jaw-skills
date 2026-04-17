# Vision-click integration

Fallback for targets the DOM can't reach: Canvas, WebGL, iframe without cross-origin access, Shadow DOM, any pixel-only UI. This is a *vision* step sandwiched inside the Hybrid or Computer Use path — it does not replace either.

## When to use (decision order)

1. Did `cli-jaw browser snapshot --interactive` return a ref for the target?
   - Yes → use it with CDP `click`. Do NOT use vision-click.
2. Is the target **inside a visible Chrome tab**?
   - Yes → use `cli-jaw browser vision-click "<description>"` (CDP screenshot + AI coords + CDP click).
3. Is the target **outside Chrome** (desktop app) and you need to describe it rather than give coordinates?
   - Yes → take a Computer Use screenshot via `screen-capture`, feed to vision model, then `click(x, y)` via Computer Use pointer-action.

Never call vision-click as the first attempt — ref-based click is faster, cheaper, and audit-friendly.

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

`vision-click` is **one specific tactic** inside the broader "how do I reach a UI target" problem. Keeping it here (and in the `vision-click` skill for CDP implementation details) means Control can route to it without the prompt having to learn a second skill from scratch.
