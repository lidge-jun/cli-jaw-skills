#!/usr/bin/env bash
# Delete reminder(s) by exact name. DESTRUCTIVE — deletion is permanent.
#
# Usage:
#   rem-delete.sh --title "Buy milk" --force
#   rem-delete.sh --title "Buy milk" --list "Personal" --force
#
# Deletes every reminder matching the exact name. Requires --force because it
# can match multiple reminders. Prints the count deleted.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos
require_osascript

title=""; list=""; force=0
while [ $# -gt 0 ]; do
  case "$1" in
    --title) title="$2"; shift 2;;
    --list) list="$2"; shift 2;;
    --force) force=1; shift;;
    *) die "unknown arg: $1";;
  esac
done
[ -n "$title" ] || die "--title required"
[ "$force" -eq 1 ] || die "delete is destructive; pass --force to confirm."

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
    set targets to (reminders of l whose name is "$(as_escape "$title")")
    repeat with r in targets
      delete r
      set n to n + 1
    end repeat
  end repeat
  return "deleted " & n & " reminder(s)"
end tell
EOF
