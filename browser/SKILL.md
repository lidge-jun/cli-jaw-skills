---
name: browser
description: "Chrome browser control: open pages, take ref snapshots, click, type, screenshot. Requires cli-jaw server running."
metadata:
  {
    "openclaw":
      {
        "emoji": "🌐",
        "requires": { "bins": ["cli-jaw"], "system": ["Google Chrome"] },
        "install":
          [
            {
              "id": "brew-cliclick",
              "kind": "brew",
              "formula": "cliclick",
              "bins": ["cliclick"],
              "label": "Install cliclick (optional, for coordinate-based clicks)",
            },
          ],
      },
  }
---

# Browser Control

Control Chrome through `cli-jaw browser` commands.
Use ref-based snapshots to identify page elements, then click/type by ref ID.

**Role separation**: the `search` skill discovers and routes (queries → URL
candidates); this browser skill verifies evidence when fetch/snippets are not
enough (original page, DOM, PDF, tables). Search finds, browser proves.

This skill follows the newer `30_browser` workflow shape, adapted for the
server-backed `cli-jaw browser` runtime. Commands that are not implemented in
the current `cli-jaw` runtime are separated under **Planned Runtime Delta** and
must not be used as current commands.

## Prerequisites

- `cli-jaw serve` must be running.
- Google Chrome must be installed.
- `playwright-core` must be installed in the `cli-jaw` project.

## Quick Start

```bash
cli-jaw browser start --agent                  # Automation session (headless, no visible test window)
cli-jaw browser start                          # Interactive browser (manual only)
cli-jaw browser start --headless               # Manual headless mode (server/CI/WSL)
cli-jaw browser navigate "https://example.com" # Go to URL
cli-jaw browser snapshot --interactive         # Interactive elements with ref IDs
cli-jaw browser click e3                       # Click ref e3
cli-jaw browser type e5 "hello" --submit       # Type + Enter
cli-jaw browser screenshot                     # Save screenshot path
```

## Core Workflow

Always follow this pattern:

```text
snapshot --interactive -> act by ref or key -> snapshot -> verify
```

Use a fresh snapshot after navigation, reload, tab changes, or any action that
substantially changes the page. Ref IDs belong to the latest usable snapshot and
can go stale.

## Current Commands

These commands are implemented in the current `cli-jaw browser` runtime.

## Support Labels

| Surface | Label | Notes |
| --- | --- | --- |
| local `cli-jaw browser` primitives | ready | server-backed local Chrome/CDP only |
| `doctor` and `cleanup-runtimes` | ready | dry-run by default; close requires `--force` |
| dashboard visible/headless start split | ready | visible manual and headless agent modes are separate |
| web-ai provider workflows | beta | use the `web-ai` skill and provider-specific gates |
| external hosted/cloud CDP | deferred | do not claim remote browser hosting support |

### Browser Management

```bash
cli-jaw browser start [--port <auto>] [--headless] [--agent]
cli-jaw browser stop
cli-jaw browser status
cli-jaw browser doctor [--json]
cli-jaw browser cleanup-runtimes [--json] [--close --force]
cli-jaw browser reset [--force]
```

- `--agent` enables an automated headless session.
- Plain `browser start` is for user-requested interactive browsing.
- `doctor` reports CDP/runtime ownership mismatch and orphan cleanup scope.
- `cleanup-runtimes` is dry-run by default; it only closes durable jaw-owned
  orphan runtime records when both `--close` and `--force` are supplied.
- `reset` clears the browser profile and screenshots; use only when the user
  explicitly wants a reset or you have confirmed it.

### Observe

```bash
cli-jaw browser snapshot
cli-jaw browser snapshot --interactive
cli-jaw browser snapshot --interactive --max-nodes 30 --json
cli-jaw browser screenshot
cli-jaw browser screenshot --full-page
cli-jaw browser screenshot --ref e5
cli-jaw browser screenshot --json
cli-jaw browser screenshot --clip 0 0 320 180 --json
cli-jaw browser text
cli-jaw browser text --format html
cli-jaw browser get-dom --selector ".card" --max-chars 2000 --json
cli-jaw browser console --json --limit 20
cli-jaw browser network --json --limit 20
```

### Snapshot Output Example

```text
e1   link       "Gmail"
e2   link       "Images"
e3   textbox    "Search"           <- To type here: type e3 "query"
e4   button     "Google Search"    <- To click: click e4
e5   button     "I'm Feeling Lucky"
```

### Act

```bash
cli-jaw browser click e3
cli-jaw browser click e3 --double
cli-jaw browser click e3 --right
cli-jaw browser type e3 "hello"
cli-jaw browser type e3 "hello" --submit
cli-jaw browser press Enter
cli-jaw browser press Escape
cli-jaw browser press Tab
cli-jaw browser hover e5
cli-jaw browser mouse-click 400 300
cli-jaw browser mouse-click 400 300 --double
cli-jaw browser select e7 "option1"
cli-jaw browser drag e3 e5
cli-jaw browser move-mouse 400 300
cli-jaw browser mouse-down
cli-jaw browser mouse-up --right
```

### Navigate and Inspect

```bash
cli-jaw browser navigate "https://example.com"
cli-jaw browser open "https://example.com"
cli-jaw browser tabs
cli-jaw browser tabs --json
cli-jaw browser active-tab --json
cli-jaw browser tab-switch 2
cli-jaw browser reload
cli-jaw browser resize 1440 900
cli-jaw browser scroll --x 0 --y 1000
cli-jaw browser wait-for-selector ".toast-success" --timeout 30000
cli-jaw browser wait-for-text "Dashboard" --timeout 30000
cli-jaw browser evaluate "document.title"
```

`evaluate` is a top-level browser diagnostic command. Do not expose arbitrary
user-provided JavaScript through higher-level vendor workflows such as web-ai.

## Common Workflows

### AI Web Workflows

For ChatGPT web-ai workflows, use the `web-ai` skill. The browser skill owns
primitive page control; `web-ai` owns structured question rendering, active-tab
safety, and response baseline handling.

### Korean Search Result Verification

Use browser commands as downstream evidence checks after the search skill has
produced URL candidates. Search snippets and AI summaries are not final
evidence.

Recommended ladder:

```bash
cli-jaw browser fetch "<url>" --json
cli-jaw browser open "<url>"
cli-jaw browser text
cli-jaw browser snapshot --interactive
cli-jaw browser get-dom --selector "<selector>" --max-chars 4000 --json
cli-jaw browser network --json --limit 40
```

Escalate through the ladder when the candidate URL is important and the current
evidence is weak:

- fetch/open returns empty, truncated, redirected, or shell-only content;
- the page is JS-rendered, iframe-heavy, or Naver-cafe/blog/search shell content;
- the evidence lives in a PDF, attachment, table, list, ranking, or paginated
  section that plain text extraction does not expose;
- snippets conflict across providers or look like they describe a different
  program, year, region, or source.

On browser escalation, `fetch` also runs an in-page Defuddle pass that
extracts the main content as **markdown** (tables, links, and footnotes
preserved). When the JSON evidence includes `browser-defuddle`, the returned
`content` is that markdown extraction — prefer it over raw page text for
tables/lists and X/article pages. If it fails (strict CSP), fetch degrades to
plain text and records a `defuddle:*` warning.

For Korean public/current searches, preserve source-sensitive status in the
answer: `sufficient` only after original evidence is visible, `browse-needed`
when browser escalation is still required, and `insufficient` when the source
cannot be reached.

### Known URL Reader / Adaptive Fetch

`cli-jaw browser fetch <url>` is the known-URL reader lane. It can read a direct
candidate URL or a search-result URL, but it is not generic search and must not
receive a raw natural-language query.

Use this ladder for public-source reading (each step triggers only when the
previous returned blocked, empty, or low-quality content):

1. **Public endpoint resolver** (23 platform resolvers): platform-specific public
   APIs, feeds, oEmbed, registry APIs, archive indexes, or stable JSON endpoints.
   Covers: GitHub, Reddit, HN, Wikipedia, npm/PyPI, arXiv, Bluesky, Mastodon,
   StackExchange, dev.to, CrossRef, OpenLibrary, Wayback, YouTube, X/Twitter,
   V2EX, Lobsters, Naver Blog/News/Finance, Medium, Substack, LinkedIn.
   Feed readers normalize RSS, Atom, and JSON Feed with bounded items,
   namespace-tolerant author/category/content/media fields, and no network
   access beyond the known feed URL.
2. **Direct fetch**: normal HTTP fetch with bounded bytes, redirects, metadata,
   and clear verdicts. HTML metadata includes canonical/feed/oEmbed links,
   OpenGraph/Twitter media fields, and JSON-LD media summaries when public in
   the page source.
3. **TLS fingerprint rotation**: on 403/429/challenge from direct fetch,
   curl-impersonate is tried with rotating browser TLS profiles
   (chrome131/safari18/firefox133) before escalating to browser. Only available
   when curl-impersonate binary is installed; falls back silently when absent.
4. **Jina Reader** (default-on): `r.jina.ai` prefix reader for clean markdown
   extraction with JS rendering. Enabled by default (`--allow-third-party-reader`);
   disable with `--no-allow-third-party-reader`. 429 triggers a 60s cooldown.
5. **Camoufox stealth browser** (optional): anti-detect Firefox with C++-level
   fingerprint spoofing via Juggler protocol. Tried before Chromium CDP when
   installed (`pip install camoufox[geoip]`). Falls back silently when absent.
6. **Browser render** (Chromium CDP): rendered text/main-content extraction for
   JS shells, WAF-thin pages, Naver/mobile pages, article pages, and surfaces.
7. **Structured extraction**: headings, tables (50-row cap), lists, code blocks,
   and JSON-LD from HTML via `structured-extractor.ts`. Available alongside
   defuddle main-content extraction.
8. **DOM/table extraction**: rendered DOM metadata, `get-dom`, selector-bound
   reads, snapshots, and screenshots when visual or interactive evidence matters.
9. **Network/metadata inspection**: inspect public network responses, OGP,
   JSON-LD, and app data only to recover the public page's own exposed content.

Optional media reader: **yt-dlp** integration for YouTube (and 1,800+ sites)
metadata and transcript extraction. Emits `ytdlp` source candidate alongside
oembed when yt-dlp binary is detected. Falls back when absent.

Adaptive-fetch keeps live public-site smoke targets as a default-off manifest.
Use it for drift checks only when explicitly running verification; ordinary unit
tests must not hit live sites. Optional media helpers such as captions or
`yt-dlp`-style extraction remain opt-in and must not auto-install dependencies.

Stop rather than bypass when the page requires login, payment, private
membership, user credentials, or CAPTCHA solving. Report `browse-needed` when a
candidate likely needs browser/human verification and `insufficient` when no
credible public route remains.

### Standalone agbrowse Alternative

When the user explicitly wants to drive a **single Chrome instance** (for
example: keep one logged-in profile open, avoid running both `cli-jaw serve`
and a second CDP session), the same browser commands are available through
the standalone `agbrowse` CLI (`npm install -g agbrowse`). The flag surface is
identical; only the binary prefix changes.

| `cli-jaw browser` form | `agbrowse` form |
| --- | --- |
| `cli-jaw browser start --agent` | `agbrowse start` |
| `cli-jaw browser status` | `agbrowse status` |
| `cli-jaw browser navigate "<url>"` | `agbrowse navigate "<url>"` |
| `cli-jaw browser snapshot --interactive` | `agbrowse snapshot --interactive` |
| `cli-jaw browser click e3` | `agbrowse click e3` |
| `cli-jaw browser type e5 "hello" --submit` | `agbrowse type e5 "hello" --submit` |
| `cli-jaw browser screenshot` | `agbrowse screenshot` |
| `cli-jaw browser tabs` | `agbrowse tabs` |
| `cli-jaw browser stop` | `agbrowse stop` |

Only switch when the user explicitly asks for the standalone path. For search
planning, `agbrowse research plan` is optional and does not replace native
cli-jaw search/browser verification. Do not run `cli-jaw browser` and `agbrowse`
against the same `--port` simultaneously —
the second start will reuse the first CDP and the persisted state files can
collide. For the web-ai layer, see the corresponding `Standalone agbrowse
Alternative` section in the `web-ai` skill.

### Web Search

```bash
cli-jaw browser start --agent
cli-jaw browser navigate "https://www.google.com"
cli-jaw browser snapshot --interactive
cli-jaw browser type e3 "search query" --submit
cli-jaw browser snapshot --interactive
cli-jaw browser click e7
```

### Form Filling

```bash
cli-jaw browser snapshot --interactive
cli-jaw browser type e1 "John Doe"
cli-jaw browser type e2 "john@example.com"
cli-jaw browser click e3
cli-jaw browser snapshot
```

### Read Page Content

```bash
cli-jaw browser navigate "https://news.ycombinator.com"
cli-jaw browser text
cli-jaw browser text --format html
cli-jaw browser snapshot --interactive
```

## Planned Runtime Delta

The copied `30_browser` reference documents a richer command surface. These are
planned `cli-jaw browser` parity targets, not current commands unless the runtime
has been upgraded in a later PRD.

### Observe and Diagnostics

```bash
cli-jaw browser console --clear --reload --duration 3000
cli-jaw browser network --reload --duration 1000
cli-jaw browser wait 2000
```

### Actions

```bash
cli-jaw browser resize 0 0 --fullscreen
cli-jaw browser scroll down
cli-jaw browser scroll up --amount 1000
```

### Navigation and Sync

`wait-for <ref>` is deprecated in the reference design because refs are
snapshot-scoped. Prefer selector/text waits.

## Recovery Strategy

If something goes wrong, stop and inspect state before the next action.

1. `snapshot` fails -> take `screenshot` for visual inspection.
2. Ref not found -> re-run `snapshot --interactive`; refs can go stale.
3. Async UI not ready -> use `wait-for-selector` or `wait-for-text`.
4. CDP connection fails -> report the exact error, then use `status`; only
   stop/start when that is the selected recovery path.
5. Chrome/profile is truly stuck -> ask before `reset` unless the user already
   requested destructive reset.
6. DOM ref unavailable -> use the `vision-click` skill only after confirming no
   usable ref exists.

## Environment Variables

| Variable | Description |
| --- | --- |
| `CHROME_HEADLESS=1` | Enable headless mode for manual starts. |
| `CHROME_NO_SANDBOX=1` | Disable Chrome sandbox for Docker/CI only. |

The default CDP port is derived from the `cli-jaw` server port. Use
`cli-jaw browser start --port <port>` only when you need an explicit override.

## Headless Mode

```bash
cli-jaw browser start --headless
cli-jaw browser start --agent
CHROME_HEADLESS=1 cli-jaw browser start
```

Use `--agent` for automation. It avoids popping a visible browser window.

## Runtime Cleanup

```bash
cli-jaw browser doctor --json
cli-jaw browser cleanup-runtimes
cli-jaw browser cleanup-runtimes --close --force
```

`cleanup-runtimes` is intentionally conservative. It only acts on a durable
`browser-runtime-owner.json` record written by jaw-owned Chrome launches, and
the process command line must still match the recorded pid, CDP port, and
profile. Chrome helper processes containing `--type=` are rejected. Never use
general `ps` output as proof that a Chrome process is safe to close.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| CDP connection refused | Chrome not started or wrong port | `cli-jaw browser status`, then start with the expected port |
| `running:false` with `owner:jaw-owned` | stale runtime metadata or dead CDP | `cli-jaw browser doctor`, then retry `browser start` |
| old headless jaw Chrome remains | durable jaw-owned orphan candidate | `cli-jaw browser cleanup-runtimes` dry-run before `--close --force` |
| Windows only opens test browser | Chrome singleton absorbed launch | Close all Chrome windows, then use `start --agent` |
| Headless CDP not opening | headless not requested in GUI-less env | Add `--headless` or use `--agent` |
| Port conflict | another process owns the CDP port | choose a different `--port` |
| Snapshot too large | page has many nodes | planned: `--max-nodes`; current: use `--interactive` |

## Notes

- Ref IDs are short-lived and should be treated as latest-snapshot scoped.
- Always re-run `snapshot --interactive` after navigation or major page changes.
- Prefer `--interactive` for token budget.
- Screenshots save to `~/.cli-jaw/screenshots/`.
- `start --agent` should be the default for agent automation.
- Non-DOM elements such as Canvas, WebGL, cross-origin iframes, and custom UI
  should use the `vision-click` skill only as an explicit fallback.
