# Control workflow — real Chrome trace

Below is the actual Chrome → Spotify trace that surfaced every pattern this skill enforces. **The target happens to be Spotify; the patterns are universal** — swap Chrome for Finder / Settings / Notion, same flow applies.

## Pattern 1 — State first

Every session begins with `get_app_state`. No exceptions.

```
path=computer-use
app=Google Chrome
action_class=state-read
action=get_app_state("Google Chrome")
stale_warning=no
result=ok (47 elements, focused tab: open.spotify.com)
```

The returned state gives you element indices. Without this call, you have nothing to target.

## Pattern 2 — element_index over type_text

**Wrong:**
```
action=type_text(app="Google Chrome", text="Daft Punk")
```

**Right:**
```
path=computer-use
app=Google Chrome
action_class=element-action
action=click(element_index=12)   # search input field
stale_warning=no
result=ok

path=computer-use
app=Google Chrome
action_class=value-injection
action=set_value(element_index=12, value="Daft Punk")
stale_warning=no
result=ok
```

`type_text(app)` fires keystrokes at whatever has focus — fragile. `set_value(element_index)` targets a specific element from the last state read — deterministic.

## Pattern 3 — Stale warning → re-read → retry

Spotify's search results load asynchronously. After typing, the element tree changes:

```
path=computer-use
app=Google Chrome
action_class=element-action
action=click(element_index=34)   # first search result
stale_warning=yes                # ← server signals state drift
result=error: stale element tree
```

Correct recovery:

```
path=computer-use
app=Google Chrome
action_class=stale-recovery
action=get_app_state("Google Chrome")
stale_warning=no
result=ok (52 elements — tree changed)

path=computer-use
app=Google Chrome
action_class=element-action
action=click(element_index=38)   # same result, new index
stale_warning=no
result=ok
```

Never retry with the old index. Always re-read state first. The index you memorized is gone.

## Pattern 4 — DOM target → CDP fallback (10× faster)

Midway through, you realize every target on open.spotify.com is a DOM node. Computer Use round-trips through screenshots and accessibility trees; CDP talks directly to the DOM.

Switch:

```
path=cdp
url=https://open.spotify.com
action=cli-jaw browser snapshot --interactive
result=ok (ref IDs: e1..e89)

path=cdp
url=https://open.spotify.com
action=click e42   # "Shuffle Play" button
result=ok
```

~120 ms per CDP action vs ~1200 ms per Computer Use action. When the target is web DOM, CDP wins by an order of magnitude.

## Mixing rules (recap)

| Rule | When | What |
|---|---|---|
| State first | Every app interaction start | `get_app_state(app)` before anything else |
| Screenshot-visible but not in tree | Map labels, canvas text, custom renders | `click(x, y)` pointer-action **immediately** from screenshot coords |
| element_index | Target IS in the element tree | `click(element_index=N)` / `set_value(element_index=N)` — never `type_text(app)` |
| Stale recovery | `stale_warning=yes` or element miss | Re-call `get_app_state`, get fresh indices, retry |
| CDP preference | Target has web DOM | Switch to `cli-jaw browser` for 10× speed |

### Pattern 5 — pointer-action (screenshot-visible, not in element tree)

Map labels, canvas objects, and custom-rendered UI text are visible in the `get_app_state` screenshot but absent from the element tree. Click them by coordinates directly.

```
# 1. Read state — screenshot shows "스타벅스" label on Naver map
get_app_state(app="Google Chrome")

# 2. Target is NOT in element tree → use screenshot coordinates
click(app="Google Chrome", x=719, y=388)

# 3. Verify
get_app_state(app="Google Chrome")
# → Starbucks detail panel opened ✅
```

Decision flow:
```
get_app_state(app)
  ↓
Target visible in screenshot?
  ├── YES + in element tree  → element_index click
  ├── YES + NOT in tree      → click(x, y) immediately
  └── NO                     → scroll/zoom/search, then re-read
```

## Applying this outside Chrome

Same four beats everywhere:
1. `get_app_state(app)` first.
2. Target an `element_index` with `set_value` / `click`. Never `type_text(app)`.
3. On stale warning, re-read state and retry.
4. If the target exposes web DOM (any Electron/CEF app included), swap to `cli-jaw browser` refs for speed.
