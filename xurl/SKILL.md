---
name: xurl
description: A CLI tool for making authenticated requests to the X (Twitter) API. Use this skill when you need to post tweets, reply, quote, search, read posts, manage followers, send DMs, upload media, or interact with any X API v2 endpoint.
metadata:
  {
    "openclaw":
      {
        "emoji": "𝕏",
        "requires": { "bins": ["xurl"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "xdevplatform/tap/xurl",
              "bins": ["xurl"],
              "label": "Install xurl (brew)",
            },
            {
              "id": "npm",
              "kind": "npm",
              "package": "@xdevplatform/xurl",
              "bins": ["xurl"],
              "label": "Install xurl (npm)",
            },
          ],
      },
  }
---

# xurl — Agent Skill Reference

`xurl` is a CLI for the X API. Supports **shortcut commands** (one-liners) and **raw curl-style** access to any v2 endpoint. All output is JSON to stdout.

## Installation

```bash
# Homebrew (macOS)
brew install --cask xdevplatform/tap/xurl

# npm
npm install -g @xdevplatform/xurl

# Shell script (installs to ~/.local/bin)
curl -fsSL https://raw.githubusercontent.com/xdevplatform/xurl/main/install.sh | bash

# Go
go install github.com/xdevplatform/xurl@latest
```

## Authentication

Run `xurl auth status` to check current auth state.

### Secret Safety

- Never read, print, or send `~/.xurl` to LLM context (contains tokens).
- Never pass credentials via agent commands — user fills `~/.xurl` manually.
- Never use `--verbose` / `-v` in agent sessions (exposes auth headers).
- Forbidden flags in agent commands: `--bearer-token`, `--consumer-key`, `--consumer-secret`, `--access-token`, `--token-secret`, `--client-id`, `--client-secret`.

### Setup

App credential registration must be done by the user outside the agent session. After registration:

```bash
xurl auth oauth2                        # authenticate
xurl auth default prod-app              # set default app
xurl auth default prod-app alice        # set default app + user
xurl --app dev-app /2/users/me          # one-off override
```

Tokens persist to `~/.xurl` in YAML (per-app isolated). OAuth 2.0 tokens auto-refresh.

## Quick Reference

| Action | Command |
|--------|---------|
| Post | `xurl post "Hello world!"` |
| Reply | `xurl reply POST_ID "Nice post!"` |
| Quote | `xurl quote POST_ID "My take"` |
| Delete | `xurl delete POST_ID` |
| Read | `xurl read POST_ID` |
| Search | `xurl search "QUERY" -n 10` |
| Who am I | `xurl whoami` |
| User lookup | `xurl user @handle` |
| Timeline | `xurl timeline -n 20` |
| Mentions | `xurl mentions -n 10` |
| Like / Unlike | `xurl like POST_ID` / `xurl unlike POST_ID` |
| Repost / Undo | `xurl repost POST_ID` / `xurl unrepost POST_ID` |
| Bookmark / Remove | `xurl bookmark POST_ID` / `xurl unbookmark POST_ID` |
| List bookmarks | `xurl bookmarks -n 10` |
| List likes | `xurl likes -n 10` |
| Follow / Unfollow | `xurl follow @handle` / `xurl unfollow @handle` |
| Following / Followers | `xurl following -n 20` / `xurl followers -n 20` |
| Block / Unblock | `xurl block @handle` / `xurl unblock @handle` |
| Mute / Unmute | `xurl mute @handle` / `xurl unmute @handle` |
| Send DM | `xurl dm @handle "message"` |
| List DMs | `xurl dms -n 10` |
| Upload media | `xurl media upload path/to/file.mp4` |
| Media status | `xurl media status MEDIA_ID` |
| **App Management** | |
| List apps | `xurl auth apps list` |
| Remove app | `xurl auth apps remove NAME` |
| Set default | `xurl auth default APP_NAME [USERNAME]` |
| Per-request app | `xurl --app NAME /2/users/me` |
| Auth status | `xurl auth status` |

> `POST_ID` accepts full URLs too (e.g. `https://x.com/user/status/123`) — xurl extracts the ID.

> Leading `@` is optional for usernames.

## Media Workflow

Upload first, then attach to post:

```bash
xurl media upload photo.jpg              # note the media_id
xurl post "Check this out" --media-id MEDIA_ID

# Multiple media
xurl post "Thread pics" --media-id 111 --media-id 222

# Video: poll until processing completes
xurl media upload video.mp4
xurl media status --wait MEDIA_ID
xurl post "Watch this" --media-id MEDIA_ID
```

## Social Graph Extras

```bash
# Another user's following/followers
xurl following --of elonmusk -n 20
xurl followers --of elonmusk -n 20
```

## Global Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--app` | | Use a specific registered app (overrides default) |
| `--auth` | | Force auth type: `oauth1`, `oauth2`, or `app` |
| `--username` | `-u` | Which OAuth2 account to use |
| `--verbose` | `-v` | Forbidden in agent sessions (leaks auth headers) |
| `--trace` | `-t` | Add `X-B3-Flags: 1` trace header |

## Raw API Access

For endpoints not covered by shortcuts:

```bash
xurl /2/users/me                                      # GET (default)
xurl -X POST /2/tweets -d '{"text":"Hello!"}'         # POST with JSON
xurl -X DELETE /2/tweets/1234567890                    # DELETE
xurl -H "Content-Type: application/json" /2/endpoint  # custom headers
xurl -s /2/tweets/search/stream                       # force streaming
xurl https://api.x.com/2/users/me                     # full URLs work
```

## Streaming

Auto-detected for known endpoints (`/2/tweets/search/stream`, `/2/tweets/sample/stream`, `/2/tweets/sample10/stream`). Force with `-s`.

## Error Handling

- Non-zero exit code on errors; API errors returned as JSON to stdout.
- Auth errors suggest re-running `xurl auth oauth2`.
- Commands needing your user ID (like, repost, bookmark, follow) auto-fetch via `/2/users/me`.

## Notes

- **Rate limits**: 429 → wait and retry. Write endpoints have stricter limits than reads.
- **Scopes**: 403 on an action may mean the token lacks a required scope — re-run `xurl auth oauth2`.
- **Multiple accounts**: Authenticate multiple OAuth2 accounts per app; switch with `-u` or `xurl auth default APP USER`.
