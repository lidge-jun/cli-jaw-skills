# Browse and QA tool ladders (`DEV-BROWSE-NATIVE-01`, `SEARCH-BROWSE-01`, `QA-TOOL-LADDER-01`)

Canonical owner: `jaw-dev`. Extracted from the router so the router stays under
its line budget; the rules are unchanged.

## Browse and QA tool routing (DEV-BROWSE-NATIVE-01, STRICT)

For ad-hoc browsing and exploratory QA — opening a page, checking a URL,
eyeballing a screen, taking a screenshot — **do not install a browser-automation
framework or driver.** Use the runtime's own browser capability first. A
deliberate end-to-end test suite is a different task and belongs to
`jaw-dev-testing`; this rule does not touch it.

Two ladders exist and their orders are deliberately **opposite**. Start at 1 and
say why when you skip a rung. What is portable here is the ordering principle, not
any specific tool name — bind each rung to whatever your runtime actually has.

| Context | Ladder | Order | Owner |
|---|---|---|---|
| Public-web proof (search, research, URL verification) | `SEARCH-BROWSE-01` | 1. `jaw browser fetch <url>` → 2. Manager embedded browser → 3. full real-profile browser → 4. screen-level control | the active `search` skill |
| QA of a surface you just built or served | `QA-TOOL-LADDER-01` | 1. Manager embedded browser (`…/snapshot`, `…/screenshot`, `…/act`) → 2. full real-profile browser → 3. screen-level control → 4. `jaw browser fetch` (public-URL shape checks only) | `jaw-dev-testing` |

The inversion is the content of the rule, not an inconsistency. Proving a public
claim wants the cheapest faithful read of what a server returns, so scripted fetch
leads. QA of your own surface needs the thing to actually render and respond to
input, so a real browser context leads and scripted fetch drops to last, where it
can only confirm shape.
