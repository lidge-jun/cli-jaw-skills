# Computer Use workflow — worked example

The example below is reconstructed from a real Chrome session and carries every
pattern this skill enforces. The target happens to be a music web app;
**the patterns are universal** — swap Chrome for Finder, Settings, or any
native app and the same flow applies.

Use the `jaw-computer-use` MCP `js` tool, or Codex's native Computer Use plugin.
The first call returns its own `cua` API documentation; read it before using
only the methods it describes (see [`computer-use.md`](computer-use.md)). The
example below illustrates decisions rather than prescribing unverified calls.

## Pattern 1 — State first

Every session begins with a state read. No exceptions.

```
path=computer-use
app=Google Chrome
action_class=state-read
action=<state read for the focused app>
stale_warning=no
result=ok (47 elements, focused tab: the music app)
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
action=<type "Daft Punk" after verifying focus on element_index=12>
stale_warning=no
result=ok
```

Typing into focus is a guess unless the latest state confirms the intended
field is focused. Use the documented `app.typeText` only after that check.

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

For a task that did not explicitly require `$computer-use`, you may find that
every target on the page is a DOM node. CDP talks directly to the DOM:

```
path=cdp
url=<the music app>
action=cli-jaw browser snapshot --interactive
result=ok (ref IDs: e1..e89)

path=cdp
action=click e42   # "Shuffle Play"
result=ok
```

Use DOM refs when they fit the user's request. Never switch to CDP for an
explicit `$computer-use` request.

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
| CDP preference | Target has web DOM and Computer Use was not explicitly requested | Switch to `cli-jaw browser` refs |

## Applying this outside a browser

Same four beats everywhere: read state, target an element index, re-read on
staleness, and use CDP refs for eligible DOM work when the user did not
explicitly request Computer Use.
