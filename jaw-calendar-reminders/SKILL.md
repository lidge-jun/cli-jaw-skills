---
name: jaw-calendar-reminders
description: Control macOS Calendar.app and Reminders.app from the CLI. Calendars/events (list, read, create, update, search, delete) and reminder lists/reminders (list, add, complete, delete, cleanup) with due dates, alarms, recurrence, priority, and JSON output. Zero install — built-in osascript; uses icalBuddy for fast calendar reads when present.
metadata:
  {
    "openclaw":
      {
        "emoji": "📆",
        "os": ["darwin"],
        "requires": { "bins": ["osascript"] },
        "optional_bins": ["icalBuddy"],
        "install":
          [
            {
              "id": "brew-icalbuddy",
              "kind": "brew",
              "formula": "ical-buddy",
              "bins": ["icalBuddy"],
              "label": "Optional: install icalBuddy for fast read-only calendar event queries",
            },
          ],
      },
    "triggers": ["calendar", "캘린더", "apple calendar", "애플캘린더", "ical", "event", "일정", "schedule", "meeting", "약속", "reminder", "리마인더", "미리알림", "remind me", "to-do", "todo", "할일", "할 일", "due"],
  }
---

# Apple Calendar + Reminders (macOS) Control

One skill to drive both **Calendar.app** and **Reminders.app** from the terminal.
Works on every calendar/list synced into macOS (iCloud, Google, Exchange,
CalDAV) — no API keys, no OAuth.

Verified pattern: **icalBuddy for fast calendar reads (when installed) +
osascript (AppleScript) for all writes.** Everything falls back to built-in
`osascript`, so the skill works with zero installs. Reminders are osascript-only.

## When to Use

- Calendar: user mentions "calendar"/"캘린더", an event/meeting/appointment.
- Reminders: user mentions a "reminder"/"미리알림", a personal to-do, or a task
  with a due date synced to iPhone/iCloud.

## When to Use a Heavier Tool Instead

These scripts cover the common 90%. For the following, a native EventKit tool
such as [che-ical-mcp](https://github.com/PsychQuant/che-ical-mcp) (Swift MCP,
29 tools) is a better fit — note it requires a signed binary install:

- Writing attendees/organizer (AppleScript/EventKit exposes these read-only).
- Undo/redo of calendar operations.
- Geofence (location-triggered) reminders, structured lat/long locations.
- Per-event IANA timezone, conflict detection, duplicate detection, large batch
  create/move with idempotency.

Recurring-occurrence-level edits (change one instance of a series) are also
limited here — treat the series as a whole or use the heavier tool.

## Operating Rules (follow for every write)

1. **Read → write → verify.** Before create/update/delete, do a bounded read of
   the target window/list. After the write, read back and report the final state
   (title, time, calendar/list).
2. **Confirm destructive or broad changes.** Deletes, cross-calendar moves, and
   multi-item edits need explicit user confirmation. Title/name-based bulk
   deletes require `--force`.
3. **Disambiguate duplicates.** If multiple items share a title, do not act on
   "the one" — list candidates (use UID for events) and ask which.
4. **Make recurrence & timezone explicit.** Confirm RRULE and all-day/timezone
   intent before writing recurring events; avoid silent defaults that drift
   after DST.
5. **Minimal exposure.** Query only the window/fields needed; never dump entire
   calendars for a narrow lookup. Data stays local — never send it to third
   parties.

## Setup & Permissions

- macOS only. `osascript` is built in.
- **First run triggers a TCC permission prompt** for Calendar and/or Reminders.
  Grant access under System Settings → Privacy & Security → Calendars /
  Reminders for the controlling terminal/app.
- Optional calendar read speed-up: `brew install ical-buddy` (binary `icalBuddy`).
- Calendar names are matched **case-insensitively**; an unknown name errors with
  the list of available calendars.

## Calendar Scripts

| Script | Purpose |
|--------|---------|
| `cal-list.sh` | List all calendar names |
| `cal-events.sh` | Read events (quick ranges, date range, `--json`) |
| `cal-add.sh` | Create an event (alarm, recurrence) |
| `cal-update.sh` | Edit an event by UID (selective fields) |
| `cal-search.sh` | Find events by summary substring (`--json`) |
| `cal-delete.sh` | Delete event(s) by UID or exact title (destructive) |

```bash
scripts/cal-list.sh

# Quick ranges + JSON
scripts/cal-events.sh today
scripts/cal-events.sh week --json
scripts/cal-events.sh --from 2026-06-29 --to 2026-07-06 --calendar "Home"

# Create with alarm (15 min before) and weekly recurrence
scripts/cal-add.sh --calendar "Home" --title "Standup" \
  --start "2026-06-29 09:00" --end "2026-06-29 09:15" \
  --alarm 15 --repeat "FREQ=WEEKLY;BYDAY=MO,WE,FR"
scripts/cal-add.sh --calendar "Home" --title "Holiday" --start "2026-07-04" --allday

# Edit by UID (only passed fields change)
scripts/cal-update.sh --calendar "Home" --uid "ABCD-1234" \
  --start "2026-06-29 14:00" --end "2026-06-29 15:00" --location "Room 2"

scripts/cal-search.sh "standup" --calendar "Work" --json
scripts/cal-delete.sh --calendar "Home" --uid "ABCD-1234"
scripts/cal-delete.sh --calendar "Home" --title "Lunch" --force
```

Event dates accept `YYYY-MM-DD` or `YYYY-MM-DD HH:MM`. Omitting `--end` defaults
to start + 1 hour. `cal-add.sh` prints the new event UID; use it with
`cal-update.sh`/`cal-delete.sh`. JSON/osascript output uses sortable ISO dates.

## Reminder Scripts

| Script | Purpose |
|--------|---------|
| `rem-lists.sh` | List all reminder lists |
| `rem-list.sh` | List reminders (filters, sort, `--json`) |
| `rem-add.sh` | Create a reminder (list, due, notes, priority) |
| `rem-complete.sh` | Mark reminder(s) complete by exact name |
| `rem-delete.sh` | Delete reminder(s) by exact name (destructive) |
| `rem-cleanup.sh` | Delete completed reminders (dry-run by default) |

```bash
scripts/rem-lists.sh
scripts/rem-list.sh --list "Work"
scripts/rem-list.sh --overdue
scripts/rem-list.sh --completed
scripts/rem-list.sh --sort due --json
scripts/rem-add.sh --title "Buy milk"
scripts/rem-add.sh --title "Call mom" --list "Personal" --due "2026-06-29 18:00"
scripts/rem-add.sh --title "Submit report" --due "2026-07-02 17:00" --priority high
scripts/rem-complete.sh --title "Buy milk" --list "Personal"
scripts/rem-delete.sh --title "Buy milk" --force
scripts/rem-cleanup.sh                 # preview completed
scripts/rem-cleanup.sh --force         # actually delete completed
```

Reminder `--due` accepts `YYYY-MM-DD` (defaults to 09:00) or `YYYY-MM-DD HH:MM`.
`--priority`: `none|high|medium|low` (or raw `0|1|5|9`). `rem-list.sh` filters:
default incomplete, `--all`, `--completed`, `--overdue`; sort with
`--sort due|title`. `rem-add.sh` prints the new reminder id.

## Destructive Operations

- `cal-delete.sh --uid` removes one event; `--title` removes **all** matching and
  requires `--force`.
- `rem-delete.sh` matches by exact name, can remove multiple, requires `--force`.
- `rem-cleanup.sh` is **dry-run by default**; `--force` deletes all completed.
- Deletion is permanent — confirm intent with the user before running.

## Date Handling

Dates are built component-by-component in AppleScript (year/month/day/hour/
minute), avoiding locale-dependent string parsing; `day` is set to 1 first to
prevent month overflow. Read output (osascript/JSON path) is normalized to
sortable `YYYY-MM-DD HH:MM`. See `references/applescript-patterns.md` for the
raw AppleScript and extension points.

## Output Formats

- Default: tab-separated (TSV) rows for easy `cut`/`awk` piping.
- `--json` (on `cal-events.sh`, `cal-search.sh`, `rem-list.sh`): a JSON array of
  objects with escaped values, for scripting/agent consumption.

## Limitations

- The osascript calendar-read fallback iterates calendars and can be slow over
  wide ranges — install `icalBuddy` for fast reads (note: `--json` always uses
  the osascript path for stable columns).
- Attendee/organizer writes, undo/redo, geofence reminders, per-event timezone,
  and occurrence-level recurring edits are out of scope (see "When to Use a
  Heavier Tool").
- Reminder match (complete/delete) is by **exact** name; read first, then act.
