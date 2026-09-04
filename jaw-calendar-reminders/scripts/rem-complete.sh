#!/usr/bin/env bash
# Mark reminder(s) complete by exact name.
#
# Usage:
#   rem-complete.sh --title "Buy milk"
#   rem-complete.sh --title "Buy milk" --list "Personal"
#
# Completes every incomplete reminder matching the exact name (in the given
# list, or across all lists). Prints the count completed.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos
require_osascript

title=""; list=""
while [ $# -gt 0 ]; do
  case "$1" in
    --title) title="$2"; shift 2;;
    --list) list="$2"; shift 2;;
    *) die "unknown arg: $1";;
  esac
done
[ -n "$title" ] || die "--title required"

if [ -n "$list" ]; then
  list_clause="set theLists to (every list whose name is \"$(as_escape "$list")\")"
else
  list_clause="set theLists to lists"
fi

osascript <<EOF
tell application "Reminders"
  set n to 0
  $list_clause
  repeat with l in theLists
    repeat with r in (reminders of l whose name is "$(as_escape "$title")" and completed is false)
      set completed of r to true
      set n to n + 1
    end repeat
  end repeat
  return "completed " & n & " reminder(s)"
end tell
EOF
