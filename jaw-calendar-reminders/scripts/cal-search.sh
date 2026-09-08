#!/usr/bin/env bash
# Search events by summary substring (case-insensitive) within a date window.
#
# Usage:
#   cal-search.sh "standup" [--calendar "Work"] [--from 2026-06-01] [--to 2026-12-31] [--json]
#
# Output (TSV): UID <TAB> Start <TAB> Summary <TAB> Calendar
# With --json: array of {uid,start,summary,calendar}.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos
require_osascript

query="${1:-}"; shift || true
[ -n "$query" ] || die "search query required: cal-search.sh \"text\" [--calendar N] [--from D] [--to D] [--json]"

cal=""; from=""; to=""; json=0
while [ $# -gt 0 ]; do
  case "$1" in
    --calendar) cal="$2"; shift 2;;
    --from) from="$2"; shift 2;;
    --to) to="$2"; shift 2;;
    --json) json=1; shift;;
    *) die "unknown arg: $1";;
  esac
done
[ -n "$from" ] || from="$(date -v -30d +%Y-%m-%d)"
[ -n "$to" ]   || to="$(date -v +90d +%Y-%m-%d)"
[ -n "$cal" ] && cal="$(cal_resolve "$cal")"

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
set q to "$(as_escape "$query")"
tell application "Calendar"
  set out to ""
  $cal_clause
  repeat with c in theCals
    set evs to (every event of c whose start date is greater than or equal to d1 and start date is less than or equal to d2 and summary contains q)
    repeat with e in evs
      set out to out & (uid of e) & tab & (my isoDate(start date of e)) & tab & (summary of e) & tab & (name of c) & linefeed
    end repeat
  end repeat
  return out
end tell
EOF
)"

if [ "$json" -eq 1 ]; then
  printf '%s\n' "$out" | tsv_to_json uid start summary calendar
else
  printf '%s\n' "$out"
fi
