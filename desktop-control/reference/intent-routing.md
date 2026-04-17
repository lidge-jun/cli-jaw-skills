# Intent → Path Routing

Decide the path **before** acting. Announce it as the first line of your reply.

## Decision table

| Target class | Example user intent | Path | Action class |
|---|---|---|---|
| Web page DOM | "open naver.com and search foo" | `cdp` | `element-action` |
| Web page DOM (read) | "what's the headline on this page?" | `cdp` | `state-read` |
| Desktop app window | "open Finder → Downloads" | `computer-use` | `element-action` |
| Chrome chrome (non-DOM) | "switch to the tab on the right" | `computer-use` | `element-action` |
| Native dialog input | "type the password into the macOS dialog" | `computer-use` | `value-injection` |
| Global shortcut | "press ⌘⇥" | `computer-use` | `keyboard-action` |
| Arbitrary pixel | "click at (812, 514)" | `computer-use` | `pointer-action` |
| Canvas / iframe / WebGL | "click the Play button (no DOM ref)" | `cdp+cu` (vision) | `pointer-action+vision` |
| Find in DOM + pointer click | "find the Play button via DOM then click it with the cursor" | `cdp+cu` | `element-action` → `pointer-action` |

## Contract IDs

The routing table above maps to the `CU-XX` / `TX-XX` contracts defined in `devlog/_plan/computeruse/21_computer_use_capability_contracts_and_prompts.md`. Use these when you need a contract name in the transcript:

| Path | Contract |
|---|---|
| `cdp` state-read | `TX-00` |
| `cdp` element-action | `TX-01` |
| `cdp` value-injection | `TX-02` |
| `cdp` hybrid-lookup | `TX-03` |
| `cdp` vision-lookup | `TX-04` |
| `cdp` error-report | `TX-05` |
| `computer-use` state-read | `CU-00` |
| `computer-use` element-action | `CU-01` |
| `computer-use` value-injection | `CU-02` |
| `computer-use` keyboard-action | `CU-03` |
| `computer-use` pointer-action | `CU-04` |
| `computer-use` pointer-action+vision | `CU-05` |
| `computer-use` stale-recovery | `CU-06` |
| `computer-use` precondition-fail | `CU-07` |
| `computer-use` confirmation-prompt | `CU-08` |
| `computer-use` transcript-summary | `CU-09` |

## Resolution order

1. Can the target be addressed by `cli-jaw browser snapshot --interactive` ref? → **CDP**.
2. Is the target a non-DOM web widget (Canvas, WebGL, iframe, Shadow DOM)? → **CDP+CU vision** (`cli-jaw browser vision-click`).
3. Is the target outside any webpage (app window, menu bar, OS dialog)? → **Computer Use**.
4. Are you reading a pixel coordinate the user gave verbatim? → **Computer Use** pointer-action.
5. Do you need the DOM to locate the element but the user insists on a real cursor click? → **Hybrid**.

If steps 1–5 all return no match, stop and report `needs boss follow-up: ambiguous target`.

## Never do

- Do not try the wrong path once "just in case" — it burns TCC prompts and confuses logs.
- Do not silently upgrade from `state-read` to `element-action` without updating the action class.
- Do not omit the `path=` line. Boss parses it.
