---
name: vision-click
description: "Vision-based coordinate click: screenshot → AI coordinate extraction → mouse click. Codex CLI only."
metadata:
  openclaw:
    emoji: "👁️"
    requires:
      bins: ["codex", "cli-jaw"]
      system: ["Google Chrome"]
---

# Vision Click (Codex Only)

Click non-DOM elements by screenshot analysis.
Uses `codex exec -i` for vision-based coordinate extraction.

Vision click is an explicit fallback, not the default browser automation path.
Always try `cli-jaw browser snapshot --interactive` and ref-based actions first.

## Quick Start (One Command — Phase 2)

```bash
cli-jaw browser vision-click "Submit button"
# → screenshot → codex vision → DPR correction → click → verify
# 🖱️ vision-clicked "Submit button" at (400, 276) via codex
```

With options:
```bash
cli-jaw browser vision-click "Login" --double
cli-jaw browser vision-click "Menu" --provider codex
cli-jaw browser vision-click "Map pin" --clip 300 120 640 480 --verify-before-click
cli-jaw browser vision-click "Toolbar item" --region top-bar --prepare-stable
```

## Prerequisites

- Codex CLI installed + authenticated, cli-jaw server running (`cli-jaw serve`), browser started

## When to Use

Fallback only when all are true:

- `cli-jaw browser snapshot --interactive` returns no usable ref for the target
- the target is visible in a screenshot
- the user task explicitly requires a non-DOM click

Good fits: canvas, iframes, Shadow DOM, WebGL, SVG, maps, overlays.

Do not use as the normal ChatGPT/web-ai query-send-poll path.

## Manual Workflow (Phase 1)

```
1. cli-jaw browser snapshot        → Check if target has a ref ID
2. If ref exists → cli-jaw browser click <ref>  (normal path)
3. If NO ref → vision-click fallback:
   a. cli-jaw browser screenshot   → Save screenshot (check output for path)
   b. codex exec -i <screenshot_path> --json \
        --dangerously-bypass-approvals-and-sandbox \
        --skip-git-repo-check \
        'Screenshot is WxHpx. Find "<TARGET>" center pixel coordinate. \
         Return ONLY JSON: {"found":true,"x":int,"y":int,"description":"..."}'
   c. Parse JSON response for x, y coordinates
   d. cli-jaw browser mouse-click <x> <y>
   e. cli-jaw browser snapshot     → Verify click worked
```

## Commands

### Screenshot + Vision

```bash
# 1. Take screenshot
cli-jaw browser screenshot
# Output: /Users/you/.cli-jaw/screenshots/screenshot-20260224-1200.png

# 2. Extract coordinates with Codex vision
codex exec -i /path/to/screenshot.png --json \
  --dangerously-bypass-approvals-and-sandbox \
  --skip-git-repo-check \
  'Screenshot is 1280x720px. Find "Submit" button center pixel coordinate.
   Return ONLY JSON: {"found":true,"x":640,"y":400,"description":"blue submit button"}'

# 3. Click at coordinates
cli-jaw browser mouse-click 640 400

# 4. Verify
cli-jaw browser snapshot
```

### Mouse Click (pixel coordinates)

```bash
cli-jaw browser mouse-click <x> <y>          # Single click
# Double-click via API:
curl -X POST http://localhost:3457/api/browser/act \
  -H 'Content-Type: application/json' \
  -d '{"kind":"mouse-click","x":640,"y":400,"doubleClick":true}'
```

## Guardrail Options

```bash
--prepare-stable        wait briefly for layout/network calm before screenshot
--clip x y w h          analyze a CSS-pixel screenshot sub-region
--region top-bar        named clip preset: left-panel | center-map | top-bar
--verify-before-click   refuse click when the target is not plausible anymore
```

`--provider codex` is the only supported provider in this slice. Codex CLI live
smoke tests are manual only; CI uses fixtures for parsing, DPR, clip offset,
and verify-before-click behavior.

## Parsing Codex Response

Codex `--json` outputs NDJSON. Look for `item.type === "agent_message"`:

```javascript
// Parse NDJSON stream
const lines = stdout.split('\n').filter(l => l.trim());
for (const line of lines) {
    const event = JSON.parse(line);
    if (event.item?.type === 'agent_message') {
        const coords = JSON.parse(event.item.text);
        // coords = { found: true, x: 640, y: 400, description: "..." }
    }
}
```

## Limitations

- **Codex CLI only** — Gemini/Claude REST planned for Phase 3
- Latency: 2-5 seconds per vision call
- Cost: ~$0.005-0.01 per call (~18K input tokens)
- Complex UIs may need confidence check + retry
- DPR auto-correction included (Phase 2)
- Never depend on live Codex vision in CI
- Never use for CAPTCHA or anti-bot bypass
