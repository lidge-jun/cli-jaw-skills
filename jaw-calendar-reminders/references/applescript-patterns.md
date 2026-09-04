# Apple Calendar + Reminders — AppleScript Reference

Raw AppleScript primitives behind the `cal-*.sh` and `rem-*.sh` scripts, plus
extension points not yet wired into the scripts.

## Component-by-component dates (both apps)

AppleScript's `date "..."` string coercion depends on the Mac's locale/region
format, so it is unreliable across machines. Build the date by setting
components, and set `day` to 1 first so reassigning the month never overflows
(e.g. moving from a 31-day month into February):

```applescript
set d to (current date)
set day of d to 1
set year of d to 2026
set month of d to 6
set day of d to 29
set hours of d to 12
set minutes of d to 0
set seconds of d to 0
```

## ASCII operators

osascript accepts ASCII comparison operators, so scripts avoid non-ASCII glyphs:
`is greater than or equal to` (≥), `is less than or equal to` (≤), plus `<=`/`>=`.

---

## Calendar

### Create an event

```applescript
tell application "Calendar"
  tell calendar "Home"
    make new event with properties {¬
      summary:"Lunch", start date:startD, end date:endD, ¬
      location:"Cafe", description:"notes", allday event:false}
  end tell
end tell
```

`uid of newEvent` returns a stable identifier for later lookup/delete.

### Read events in a range

```applescript
tell application "Calendar"
  set evs to (every event of calendar "Home" whose ¬
    start date is greater than or equal to d1 and ¬
    start date is less than or equal to d2)
end tell
```

### Extension points

Alarm (15 min before):

```applescript
tell e to make new sound alarm at end with properties {trigger interval:-15}
```

Attendee:

```applescript
tell e to make new attendee at end with properties {display name:"Sam", email:"sam@example.com"}
```

Recurrence (iCalendar RRULE):

```applescript
set recurrence of e to "FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,WE,FR"
```

### icalBuddy quick reference (read-only)

```bash
icalBuddy eventsToday
icalBuddy eventsToday+7
icalBuddy eventsFrom:2026-06-29 to:2026-07-06
icalBuddy -ic "Work" eventsToday
icalBuddy calendars
icalBuddy -nc -npn eventsToday   # clean output (no calendar names / prop names)
```

---

## Reminders

### Core operations

```applescript
tell application "Reminders" to get name of every list

tell application "Reminders"
  get name of (reminders of list "Work" whose completed is false)
end tell

tell application "Reminders"
  tell list "Personal"
    make new reminder with properties {name:"Call mom", body:"…", due date:dueD}
  end tell
end tell

tell application "Reminders"
  set completed of (first reminder of list "Personal" whose name is "Call mom") to true
end tell

tell application "Reminders"
  delete (reminders of list "Personal" whose name is "Call mom")
end tell
```

Use `tell default list` to target the user's default list.

### Extension points

Priority (0 none, 1 high, 5 medium, 9 low):

```applescript
set priority of r to 1
```

Flagged filter:

```applescript
get name of (reminders of list "Work" whose flagged is true)
```

---

## Sortable ISO dates (used by `--json` / osascript read path)

AppleScript's default date coercion (`date as string`) is locale-formatted and
not sortable. `lib.sh` injects `pad2()` + `isoDate()` handlers; scripts call
`my isoDate(d)` inside the `tell` block to emit `YYYY-MM-DD HH:MM` (or `""` for
a missing-value date). This makes `sort -k` and JSON output stable.

## Competitor feature landscape (gap reference)

Where this skill stands relative to surveyed Apple Calendar/Reminders CLI/MCP tools:

| Capability | This skill | Heavier tools |
| --- | --- | --- |
| List/read/create/search/delete events | yes | yes |
| Event update (selective fields) | yes (`cal-update.sh`) | yes |
| Alarms, RRULE recurrence on create | yes | yes |
| Quick ranges (today/tomorrow/week), JSON | yes | yes |
| Case-insensitive calendar match | yes (`cal_resolve`) | yes |
| Reminders: filters/sort/priority/cleanup | yes | yes |
| Attendee/organizer write | no (EventKit read-only) | read-only too |
| Undo/redo | no | che-ical-mcp |
| Conflict / duplicate detection | no | che-ical-mcp |
| Batch create/move, idempotent writes | no | che-ical-mcp |
| Per-event IANA timezone | no | che-ical-mcp |
| Geofence (location-trigger) reminders | no | che-ical-mcp |
| Occurrence-level recurring edits | no | che-ical-mcp |
| Install footprint | zero (osascript) | signed Swift binary / brew |

Representative tools surveyed:
- `calctl` — icalBuddy reads + AppleScript writes (calendars/show/add/search).
- `che-ical-mcp` — native Swift EventKit MCP, 29 tools, undo/redo, batch,
  timezone, attendees (read), `--cli` mode, signed/notarized binary.
- `ivangdavila/apple-calendar-macos` — operating-rules skill: command-path
  probing, read-then-write-then-verify, confirm-destructive, duplicate
  disambiguation (the basis for this skill's "Operating Rules" section).

Content was rephrased for compliance with licensing restrictions.

## TCC permission notes (both apps)
- The first Calendar/Reminders access from a given parent process raises a
  system prompt.
- An empty result with no prompt usually means the controlling app was denied
  earlier — re-grant under System Settings → Privacy & Security →
  Calendars / Reminders, then retry.
- Automated/headless contexts may not show a clickable prompt — grant the
  controlling terminal access once, interactively, beforehand.
