---
name: "develop-web-game"
description: "Use when Codex is building or iterating on a web game (HTML/JS) and needs a reliable development + testing loop: implement small changes, run a Playwright-based test script with short input bursts and intentional pauses, inspect screenshots/text, and review console errors with render_game_to_text."
---


# Develop Web Game

Build games in small steps: implement → act → pause → observe → adjust.

## Skill paths (set once)

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export WEB_GAME_CLIENT="$CODEX_HOME/skills/develop-web-game/scripts/web_game_playwright_client.js"
export WEB_GAME_ACTIONS="$CODEX_HOME/skills/develop-web-game/references/action_payloads.json"
```

## Workflow

1. **Pick one goal.** Single feature or behavior per iteration.
2. **Implement small.** Smallest change that moves the game forward.
3. **Integration points.** Provide a single canvas, `window.render_game_to_text`, and `window.advanceTime(ms)` (deterministic stepping prevents flaky tests).
4. **Initialize progress.md.** If it exists, read first — preserve `Original prompt:` at top, note prior TODOs. If missing, create with `Original prompt: <prompt>`.
5. **Verify Playwright.** Check `npx playwright` availability before first run.
6. **Run `$WEB_GAME_CLIENT`** after each meaningful change. Base actions on `$WEB_GAME_ACTIONS`.
7. **Inspect.** Capture screenshots + text state. Open and visually verify screenshots.
8. **Verify controls end-to-end.** Exercise all interactions through their full sequence (cause → intermediate → outcome). Confirm `render_game_to_text` matches screen state.
9. **Check errors.** Fix the first new console error before continuing.
10. **Reset between scenarios.** Avoid cross-test state pollution.
11. **Iterate.** Change one variable at a time, repeat steps 6–10 until stable.

Example command (actions required):
```
node "$WEB_GAME_CLIENT" --url http://localhost:5173 --actions-file "$WEB_GAME_ACTIONS" --click-selector "#start-btn" --iterations 3 --pause-ms 250
```

Example actions (inline JSON):
```json
{
  "steps": [
    { "buttons": ["left_mouse_button"], "frames": 2, "mouse_x": 120, "mouse_y": 80 },
    { "buttons": [], "frames": 6 },
    { "buttons": ["right"], "frames": 8 },
    { "buttons": ["space"], "frames": 4 }
  ]
}
```

## Test Checklist

Test new features and any areas affected by logic changes:
- Movement/interaction inputs (move, jump, shoot, confirm/select)
- Win/lose transitions, score/health/resource changes
- Boundary conditions (collisions, walls, screen edges)
- Menu/pause/start flow
- Special actions from the request (powerups, combos, puzzles, timers)

## Test Artifacts

- **Screenshots**: Open and visually inspect every screenshot — they are the source of truth. Go beyond the start screen to capture gameplay covering new features. If headless capture looks wrong, rerun in headed mode.
- **`render_game_to_text` output**: Verify it matches what screenshots show.
- **Console errors**: Fix the first new error before continuing.

Fix-and-rerun in a tight loop until screenshots, text state, and controls are all correct. Re-test all interactions after fixes to catch regressions.

## Core Game Guidelines

### Canvas + Layout
- Prefer a single canvas centered in the window.

### Visuals
- Keep on-screen text minimal; show controls on a start/menu screen rather than overlaying them during play.
- Avoid overly dark scenes unless the design calls for it. Make key elements easy to see.
- Draw the background on the canvas itself instead of relying on CSS backgrounds.

### Text State Output (render_game_to_text)
Return a concise JSON of current game state — enough to play without visuals.

```js
```js
function renderGameToText() {
  const payload = {
    mode: state.mode,
    player: { x: state.player.x, y: state.player.y, r: state.player.r },
    entities: state.entities.map((e) => ({ x: e.x, y: e.y, r: e.r })),
    score: state.score,
  };
  return JSON.stringify(payload);
}
window.render_game_to_text = renderGameToText;
```

Include: coordinate system, player state, active entities, score, mode flags. Prefer current/visible data over history.

### Time Stepping Hook
Expose `window.advanceTime(ms)` for deterministic frame stepping during Playwright tests.
```js
window.advanceTime = (ms) => {
  const steps = Math.max(1, Math.round(ms / (1000 / 60)));
  for (let i = 0; i < steps; i++) update(1 / 60);
  render();
};
```

### Fullscreen Toggle
- `f` to toggle, `Esc` to exit. Resize canvas/rendering on toggle so visuals and input mapping stay correct.

## Progress Tracking

Update `progress.md` after each meaningful chunk of work. Preserve the `Original prompt:` line at top. Leave TODOs and suggestions for the next agent.

## Playwright Prerequisites

- Prefer local `playwright` dependency if already in project.
- Fallback: `npm install -g @playwright/mcp@latest`
- Use the bundled client script (`$WEB_GAME_CLIENT`), not `@playwright/test`.

## References

- `$WEB_GAME_CLIENT` — Playwright action loop with time-stepping, screenshots, console error capture. Pass actions via `--actions-file`, `--actions-json`, or `--click`.
- `$WEB_GAME_ACTIONS` — Example action payloads (keyboard + mouse, per-frame capture).
