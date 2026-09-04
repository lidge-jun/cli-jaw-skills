#!/usr/bin/env bash
# Create a reminder via osascript.
#
# Usage:
#   rem-add.sh --title "Buy milk"
#   rem-add.sh --title "Call mom" --list "Personal" --due "2026-06-29 18:00"
#   rem-add.sh --title "Pay rent" --due "2026-07-01" --notes "Auto-transfer"
#   rem-add.sh --title "Submit report" --due "2026-07-02 17:00" --priority high
#
# Notes:
#   - --due accepts "YYYY-MM-DD" (defaults to 09:00) or "YYYY-MM-DD HH:MM".
#   - --priority: none|high|medium|low (or raw 0|1|5|9).
#   - Omitting --list uses the default Reminders list.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos
require_osascript

title=""; list=""; due=""; notes=""; priority=""
while [ $# -gt 0 ]; do
  case "$1" in
    --title) title="$2"; shift 2;;
    --list) list="$2"; shift 2;;
    --due) due="$2"; shift 2;;
    --notes) notes="$2"; shift 2;;
    --priority) priority="$2"; shift 2;;
    *) die "unknown arg: $1";;
  esac
done
[ -n "$title" ] || die "--title required"

props="name:\"$(as_escape "$title")\""
[ -n "$notes" ] && props="$props, body:\"$(as_escape "$notes")\""
if [ -n "$priority" ]; then
  case "$priority" in
    none) priority=0;; high) priority=1;; medium) priority=5;; low) priority=9;;
    0|1|5|9) ;;
    *) die "invalid --priority: use none|high|medium|low or 0|1|5|9";;
  esac
  props="$props, priority:$priority"
fi

build_due=""
if [ -n "$due" ]; then
  # Reminders default to 09:00 when only a date is given.
  case "$due" in *" "*) ;; *) due="$due 09:00";; esac
  build_due="$(as_build_date dueD "$due")"
  props="$props, due date:dueD"
fi

if [ -n "$list" ]; then
  target="tell list \"$(as_escape "$list")\""
  target_end="end tell"
else
  target="tell default list"
  target_end="end tell"
fi

osascript <<EOF
$build_due
tell application "Reminders"
  $target
    set newR to make new reminder with properties {$props}
    return id of newR
  $target_end
end tell
EOF
