---
name: apple-reminders
description: Manage Apple Reminders via remindctl CLI (list, add, edit, complete, delete). Supports lists, date filters, and JSON/plain output.
homepage: https://github.com/steipete/remindctl
metadata:
  {
    "openclaw":
      {
        "emoji": "⏰",
        "os": ["darwin"],
        "requires": { "bins": ["remindctl"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "steipete/tap/remindctl",
              "bins": ["remindctl"],
              "label": "Install remindctl via Homebrew",
            },
          ],
      },
  }
---

# Apple Reminders CLI (remindctl)

Use `remindctl` to manage Apple Reminders directly from the terminal.

## When to Use

- User mentions "reminder" or "Reminders app", personal to-dos with due dates, or wants tasks synced to iOS.

## Use Something Else For

- Clawdbot tasks/alerts → `cron` tool with systemEvent
- Calendar events → Apple Calendar
- Project task management → Notion, GitHub Issues
- "Remind me" that means a bot alert → clarify intent first

## Setup

- Install: `brew install steipete/tap/remindctl`
- macOS-only; grant Reminders permission when prompted
- Check status: `remindctl status`
- Request access: `remindctl authorize`

## Common Commands

### View Reminders

```bash
remindctl                    # Today's reminders
remindctl today              # Today
remindctl tomorrow           # Tomorrow
remindctl week               # This week
remindctl overdue            # Past due
remindctl all                # Everything
remindctl 2026-01-04         # Specific date
```

### Manage Lists

```bash
remindctl list               # List all lists
remindctl list Work          # Show specific list
remindctl list Projects --create    # Create list
remindctl list Work --delete        # Delete list
```

### Create Reminders

```bash
remindctl add "Buy milk"
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl add --title "Meeting prep" --due "2026-02-15 09:00"
```

### Complete/Delete

```bash
remindctl complete 1 2 3     # Complete by ID
remindctl delete 4A83 --force  # Delete by ID
```

### Output Formats

```bash
remindctl today --json       # JSON for scripting
remindctl today --plain      # TSV format
remindctl today --quiet      # Counts only
```

## Date Formats

Accepted by `--due` and date filters:

- `today`, `tomorrow`, `yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601 (`2026-01-04T12:34:56Z`)


