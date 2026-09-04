#!/usr/bin/env bash
# Update an existing event, identified by UID. Writes via osascript.
#
# Usage:
#   cal-update.sh --calendar "Home" --uid "ABCD-1234" [--title "..."] \
#     [--start "2026-06-29 14:00"] [--end "2026-06-29 15:00"] \
#     [--location "..."] [--notes "..."]
#
# Notes:
#   - Only the fields you pass are changed; others are left as-is.
#   - --calendar is matched case-insensitively.
#   - Prints "updated <uid>" on success, or errors if the UID is not found.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos
require_osascript

cal=""; uid=""; title=""; start=""; end=""; loc=""; notes=""
have_title=0; have_loc=0; have_notes=0
while [ $# -gt 0 ]; do
  case "$1" in
    --calendar) cal="$2"; shift 2;;
    --uid) uid="$2"; shift 2;;
    --title) title="$2"; have_title=1; shift 2;;
    --start) start="$2"; shift 2;;
    --end) end="$2"; shift 2;;
    --location) loc="$2"; have_loc=1; shift 2;;
    --notes) notes="$2"; have_notes=1; shift 2;;
    *) die "unknown arg: $1";;
  esac
done
[ -n "$cal" ] || die "--calendar required"
[ -n "$uid" ] || die "--uid required"
cal="$(cal_resolve "$cal")"

sets=""
[ "$have_title" -eq 1 ] && sets="$sets"$'\n'"    set summary of e to \"$(as_escape "$title")\""
[ "$have_loc" -eq 1 ]   && sets="$sets"$'\n'"    set location of e to \"$(as_escape "$loc")\""
[ "$have_notes" -eq 1 ] && sets="$sets"$'\n'"    set description of e to \"$(as_escape "$notes")\""

build_start=""; [ -n "$start" ] && { build_start="$(as_build_date startD "$start")"; sets="$sets"$'\n'"    set start date of e to startD"; }
build_end="";   [ -n "$end" ]   && { build_end="$(as_build_date endD "$end")"; sets="$sets"$'\n'"    set end date of e to endD"; }

[ -n "$sets" ] || die "nothing to update: pass at least one of --title/--start/--end/--location/--notes"

osascript <<EOF
$build_start
$build_end
tell application "Calendar"
  tell calendar "$(as_escape "$cal")"
    set matches to (every event whose uid is "$(as_escape "$uid")")
    if (count of matches) is 0 then error "event not found for uid: $(as_escape "$uid")"
    set e to item 1 of matches
$sets
    return "updated " & uid of e
  end tell
end tell
EOF
