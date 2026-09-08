# Control workflow — a real trace

The trace below surfaced every pattern this skill enforces. The target happens
to be a music web app in Chrome; **the patterns are universal** — swap Chrome
for Finder, Settings, or any native app and the same flow applies.

Tool names are deliberately absent. The surface is host-provided and version
dependent (see [`computer-use.md`](computer-use.md)); what follows is the
shape of the work, not an API listing.

## Pattern 1 — State first

Every session begins with a state read. No exceptions.

```
path=computer-use
app=Google Chrome
action_class=state-read
action=<state read for the focused app>
stale_warning=no
result=ok (47 elements, focused tab: open.spotify.com)
```

The returned state gives you element indices. Without it you have nothing to
target.

## Pattern 2 — Element index over focus-only typing

**Fragile:** fire keystrokes at whatever currently has focus.

**Deterministic:**

```
path=computer-use
app=Google Chrome
action_class=element-action
action=<click element_index=12>   # search input field
stale_warning=no
result=ok

path=computer-use
app=Google Chrome
action_class=value-injection
action=<set value on element_index=12 to "Daft Punk">
stale_warning=no
result=ok
```

Typing into focus is a guess about where the cursor is. Setting a value on an
element from the last state read is not.

## Pattern 3 — Stale warning, re-read, retry

Search results load asynchronously, so the element tree changes underneath you:

```
action=<click element_index=34>   # first search result
stale_warning=yes                 # server signals state drift
result=error: stale element tree
```

Correct recovery:

```
action_class=stale-recovery
action=<state read>
result=ok (52 elements — tree changed)

action_class=element-action
action=<click element_index=38>   # same result, new index
result=ok
```

Never retry with the old index. The index you memorized is gone.

## Pattern 4 — DOM target, CDP is faster

Midway through you realize every target on the page is a DOM node. Computer Use
round-trips through screenshots and accessibility trees; CDP talks to the DOM.

```
path=cdp
url=https://open.spotify.com
action=cli-jaw browser snapshot --interactive
result=ok (ref IDs: e1..e89)

path=cdp
action=click e42   # "Shuffle Play"
result=ok
```

Roughly an order of magnitude faster per action. When the target has web DOM,
CDP wins.

## Pattern 5 — Pointer action for screenshot-visible, tree-absent targets

Map labels, canvas objects, and custom-rendered text appear in the state
screenshot but not in the element tree. Click them by coordinate:

```
1. <state read>          # screenshot shows the label on the map
2. <click at x=719, y=388>
3. <state read>          # detail panel opened
```

Decision flow:

```
state read
  ↓
Target visible in screenshot?
  ├── YES + in element tree  → element index click
  ├── YES + NOT in tree      → coordinate click
  └── NO                     → scroll/zoom/search, then re-read
```

## Mixing rules

| Rule | When | What |
|---|---|---|
| State first | First Computer Use interaction each turn | Read state before anything else |
| Screenshot-visible but not in tree | Map labels, canvas text, custom renders | Coordinate click immediately |
| Element index | Target is in the tree | Prefer index over coordinate; type into focus only after verifying it |
| Stale recovery | Staleness signal or element miss | Re-read, get fresh indices, retry |
| CDP preference | Target has web DOM | Switch to `cli-jaw browser` refs for speed |

## Applying this outside a browser

Same four beats everywhere: read state, target an element index, re-read on
staleness, and switch to CDP refs if the app exposes web DOM (any Electron or
CEF app included).

