#!/usr/bin/env bash
# Delete event(s). DESTRUCTIVE — deletion is permanent.
#
# Usage:
#   cal-delete.sh --calendar "Home" --uid "ABCD-1234"          # delete one event by UID
#   cal-delete.sh --calendar "Home" --title "Lunch" --force    # delete ALL matching that exact title
#
# Safety:
#   - UID deletes one specific event.
#   - --title deletes every event with that exact summary and REQUIRES --force.
#   - Prints the count of deleted events.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos
require_osascript

cal=""; uid=""; title=""; force=0
while [ $# -gt 0 ]; do
  case "$1" in
    --calendar) cal="$2"; shift 2;;
    --uid) uid="$2"; shift 2;;
    --title) title="$2"; shift 2;;
    --force) force=1; shift;;
    *) die "unknown arg: $1";;
  esac
done
[ -n "$cal" ] || die "--calendar required"
cal="$(cal_resolve "$cal")"

if [ -n "$uid" ]; then
  osascript <<EOF
tell application "Calendar"
  tell calendar "$(as_escape "$cal")"
    set targets to (every event whose uid is "$(as_escape "$uid")")
    set n to count of targets
    repeat with e in targets
      delete e
    end repeat
    return "deleted " & n & " event(s)"
  end tell
end tell
EOF
elif [ -n "$title" ]; then
  [ "$force" -eq 1 ] || die "title-based delete is bulk/destructive; pass --force to confirm."
  osascript <<EOF
tell application "Calendar"
  tell calendar "$(as_escape "$cal")"
    set targets to (every event whose summary is "$(as_escape "$title")")
    set n to count of targets
    repeat with e in targets
      delete e
    end repeat
    return "deleted " & n & " event(s)"
  end tell
end tell
EOF
else
  die "provide --uid or --title"
fi
