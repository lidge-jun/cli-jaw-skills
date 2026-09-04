#!/usr/bin/env bash
# Read events in a date range. Prefers icalBuddy (fast) for plain output;
# uses osascript for ranged/calendar-filtered/JSON output.
#
# Usage:
#   cal-events.sh                       # today
#   cal-events.sh today | tomorrow | week | next7   # quick ranges
#   cal-events.sh --days 7
#   cal-events.sh --from 2026-06-29 --to 2026-07-06
#   cal-events.sh --calendar "Home" --days 3
#   cal-events.sh week --json
#
# Output (TSV): Start <TAB> End <TAB> Summary <TAB> Calendar
# With --json: array of {start,end,summary,calendar}.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos

from=""; to=""; cal=""; days=""; json=0
# Optional leading quick-range keyword.
case "${1:-}" in
  today)    from="$(date +%Y-%m-%d)"; to="$from"; shift;;
  tomorrow) from="$(date -v +1d +%Y-%m-%d)"; to="$from"; shift;;
  week|next7) from="$(date +%Y-%m-%d)"; to="$(date -v +7d +%Y-%m-%d)"; shift;;
esac
while [ $# -gt 0 ]; do
  case "$1" in
    --from) from="$2"; shift 2;;
    --to) to="$2"; shift 2;;
    --calendar) cal="$2"; shift 2;;
    --days) days="$2"; shift 2;;
    --json) json=1; shift;;
    *) die "unknown arg: $1";;
  esac
done

[ -n "$from" ] || from="$(date +%Y-%m-%d)"
if [ -z "$to" ]; then
  if [ -n "$days" ]; then to="$(date -v +"${days}"d +%Y-%m-%d)"; else to="$from"; fi
fi
[ -n "$cal" ] && cal="$(cal_resolve "$cal")"

# Fast path: icalBuddy for plain (non-JSON) output when available.
if [ "$json" -eq 0 ] && command -v icalBuddy >/dev/null 2>&1; then
  args=(-nc -npn)
  [ -n "$cal" ] && args+=(-ic "$cal")
  icalBuddy "${args[@]}" eventsFrom:"$from" to:"$to"
  exit 0
fi

require_osascript
build_from="$(as_build_date d1 "$from 00:00")"
build_to="$(as_build_date d2 "$to 23:59")"
if [ -n "$cal" ]; then
  cal_clause="set theCals to (every calendar whose name is \"$(as_escape "$cal")\")"
else
  cal_clause="set theCals to calendars"
fi

out="$(osascript <<EOF
$(as_isodate_handler)
$build_from
$build_to
tell application "Calendar"
  $cal_clause
  set out to ""
  repeat with c in theCals
    set evs to (every event of c whose start date is greater than or equal to d1 and start date is less than or equal to d2)
    repeat with e in evs
      set out to out & (my isoDate(start date of e)) & tab & (my isoDate(end date of e)) & tab & (summary of e) & tab & (name of c) & linefeed
    end repeat
  end repeat
  return out
end tell
EOF
)"

if [ "$json" -eq 1 ]; then
  printf '%s\n' "$out" | tsv_to_json start end summary calendar
else
  printf '%s\n' "$out"
fi
