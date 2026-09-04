#!/usr/bin/env bash
# Create a calendar event. Writes via osascript (AppleScript).
#
# Usage:
#   cal-add.sh --calendar "Home" --title "Lunch" --start "2026-06-29 12:00" \
#     [--end "2026-06-29 13:00"] [--location "Cafe"] [--notes "..."] \
#     [--allday] [--alarm 15] [--repeat "FREQ=WEEKLY;BYDAY=MO,WE,FR"]
#
# Notes:
#   - --start / --end accept "YYYY-MM-DD" or "YYYY-MM-DD HH:MM".
#   - If --end is omitted, defaults to start + 1 hour.
#   - --alarm N adds a display alarm N minutes before start.
#   - --repeat takes an iCalendar RRULE body (without the "RRULE:" prefix).
#   - --calendar is matched case-insensitively.
#   - Prints the new event UID on success.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos
require_osascript

cal=""; title=""; start=""; end=""; loc=""; notes=""; allday=0; alarm=""; rrule=""
while [ $# -gt 0 ]; do
  case "$1" in
    --calendar) cal="$2"; shift 2;;
    --title) title="$2"; shift 2;;
    --start) start="$2"; shift 2;;
    --end) end="$2"; shift 2;;
    --location) loc="$2"; shift 2;;
    --notes) notes="$2"; shift 2;;
    --allday) allday=1; shift;;
    --alarm) alarm="$2"; shift 2;;
    --repeat) rrule="$2"; shift 2;;
    *) die "unknown arg: $1";;
  esac
done
[ -n "$cal" ]   || die "--calendar required"
[ -n "$title" ] || die "--title required"
[ -n "$start" ] || die "--start required (YYYY-MM-DD[ HH:MM])"
[ -n "$end" ]   || end="$start"
cal="$(cal_resolve "$cal")"

build_start="$(as_build_date startD "$start")"
build_end="$(as_build_date endD "$end")"

props="summary:\"$(as_escape "$title")\", start date:startD, end date:endD"
[ -n "$loc" ]   && props="$props, location:\"$(as_escape "$loc")\""
[ -n "$notes" ] && props="$props, description:\"$(as_escape "$notes")\""
[ "$allday" -eq 1 ] && props="$props, allday event:true"
[ -n "$rrule" ] && props="$props, recurrence:\"$(as_escape "$rrule")\""

extra=""
if [ -n "$alarm" ]; then
  extra="    make new display alarm at end of newEvent with properties {trigger interval:-$((10#$alarm))}"
fi

osascript <<EOF
$build_start
$build_end
if endD is less than or equal to startD then set endD to startD + (60 * 60)
tell application "Calendar"
  tell calendar "$(as_escape "$cal")"
    set newEvent to make new event with properties {$props}
$extra
    return uid of newEvent
  end tell
end tell
EOF
