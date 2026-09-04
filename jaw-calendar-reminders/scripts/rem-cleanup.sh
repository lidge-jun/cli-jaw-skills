#!/usr/bin/env bash
# Clean up completed reminders. Dry-run by default — prints what WOULD be
# deleted. Pass --force to actually delete. DESTRUCTIVE with --force.
#
# Usage:
#   rem-cleanup.sh                  # dry-run: count + titles of completed
#   rem-cleanup.sh --list "Work"    # scope to one list
#   rem-cleanup.sh --force          # actually delete all completed
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos
require_osascript

list=""; force=0
while [ $# -gt 0 ]; do
  case "$1" in
    --list) list="$2"; shift 2;;
    --force) force=1; shift;;
    *) die "unknown arg: $1";;
  esac
done

if [ -n "$list" ]; then
  list_clause="set theLists to (every list whose name is \"$(as_escape "$list")\")"
else
  list_clause="set theLists to lists"
fi

if [ "$force" -eq 1 ]; then
  osascript <<EOF
tell application "Reminders"
  set n to 0
  $list_clause
  repeat with l in theLists
    set targets to (reminders of l whose completed is true)
    repeat with r in targets
      delete r
      set n to n + 1
    end repeat
  end repeat
  return "deleted " & n & " completed reminder(s)"
end tell
EOF
else
  osascript <<EOF
tell application "Reminders"
  set out to ""
  set n to 0
  $list_clause
  repeat with l in theLists
    repeat with r in (reminders of l whose completed is true)
      set out to out & "- " & (name of r) & " [" & (name of l) & "]" & linefeed
      set n to n + 1
    end repeat
  end repeat
  return "DRY-RUN: " & n & " completed reminder(s) would be deleted (pass --force):" & linefeed & out
end tell
EOF
fi
