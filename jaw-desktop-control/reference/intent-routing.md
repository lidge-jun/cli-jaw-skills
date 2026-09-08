# Intent → Path Routing

Decide the path **before** acting. Announce it as the first line of your reply.

## Decision table

| Target class | Example user intent | Path | Action class |
|---|---|---|---|
| Web page DOM | "open naver.com and search foo" | `cdp` | `element-action` |
| Web page DOM (read) | "what's the headline on this page?" | `cdp` | `state-read` |
| Desktop app window | "open Finder → Downloads" | `computer-use` | `element-action` |
| Chrome chrome (non-DOM) | "switch to the tab on the right" | `computer-use` | `element-action` |
| Native dialog input | "type into the macOS dialog" | `computer-use` | `value-injection` |
| Global shortcut | "press Command-Tab" | `computer-use` | `keyboard-action` |
| Arbitrary pixel | "click at (812, 514)" | `computer-use` | `pointer-action` |
| Canvas / iframe / WebGL | "click the Play button (no DOM ref)" | `cdp+cu` (vision) | `pointer-action+vision` |
| Find in DOM + pointer click | "find the Play button via DOM then click it with the cursor" | `cdp+cu` | `element-action` → `pointer-action` |

## Resolution order

0. **Does the user's message contain `$computer-use` or `/computer-use`?** → **Computer Use**, no further analysis. Explicit user opt-in overrides the heuristics below. If Computer Use tools are unavailable, stop with `precondition failed: computer-use unavailable` instead of trying CDP.
1. Can the target be addressed by `cli-jaw browser snapshot --interactive` ref? → **CDP**.
2. Is the target a non-DOM web widget (Canvas, WebGL, iframe, Shadow DOM) visible in the Computer Use state screenshot? → **Computer Use** pointer-action from those screenshot coordinates. (Fallback: `cli-jaw browser vision-click` for no-ref browser cases.)
3. Is the target outside any webpage (app window, menu bar, OS dialog)? → **Computer Use**.
4. Are you reading a pixel coordinate the user gave verbatim? → **Computer Use** pointer-action.
5. Do you need the DOM to locate the element but the user insists on a real cursor click? → **Hybrid**.
6. Is the app name unclear? → **Computer Use** discovery first, then continue routing inside the selected target. Use whatever discovery and state-read calls your host's surface documents; on Windows an enumeration that answers proves nothing about the connection.

If steps 0–6 all return no match, stop and report `needs boss follow-up: ambiguous target`.

## Never do

- Do not try the wrong path once "just in case" — it burns TCC prompts and confuses logs.
- Do not silently upgrade from `state-read` to `element-action` without updating the action class.
- Do not omit the `path=` line. Boss parses it.
