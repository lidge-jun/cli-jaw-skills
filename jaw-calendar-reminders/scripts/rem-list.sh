#!/usr/bin/env bash
# List reminders. Defaults to incomplete reminders across all lists.
#
# Usage:
#   rem-list.sh                       # incomplete, all lists
#   rem-list.sh --list "Work"         # incomplete in one list
#   rem-list.sh --all                 # include completed
#   rem-list.sh --completed           # only completed
#   rem-list.sh --overdue             # incomplete with a due date in the past
#   rem-list.sh --sort due|title      # sort output
#   rem-list.sh --json                # JSON array
#
# Output (TSV): Done(0/1) <TAB> Name <TAB> Due(ISO) <TAB> List
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos
require_osascript

list=""; mode="incomplete"; sort_by=""; json=0
while [ $# -gt 0 ]; do
  case "$1" in
    --list) list="$2"; shift 2;;
    --all) mode="all"; shift;;
    --completed) mode="completed"; shift;;
    --overdue) mode="overdue"; shift;;
    --sort) sort_by="$2"; shift 2;;
    --json) json=1; shift;;
    *) die "unknown arg: $1";;
  esac
done

if [ -n "$list" ]; then
  list_clause="set theLists to (every list whose name is \"$(as_escape "$list")\")"
else
  list_clause="set theLists to lists"
fi

case "$mode" in
  all)        filter="(reminders of l)";;
  completed)  filter="(reminders of l whose completed is true)";;
  *)          filter="(reminders of l whose completed is false)";;  # incomplete + overdue
esac

out="$(osascript <<EOF
$(as_isodate_handler)
tell application "Reminders"
  set out to ""
  set nowD to (current date)
  $list_clause
  repeat with l in theLists
    repeat with r in $filter
      set dd to missing value
      try
        set dd to due date of r
      end try
      set dueStr to my isoDate(dd)
      set doneFlag to "0"
      if completed of r then set doneFlag to "1"
      set keep to true
      if "$mode" is "overdue" then
        if dd is missing value then
          set keep to false
        else if dd is greater than or equal to nowD then
          set keep to false
        end if
      end if
      if keep then set out to out & doneFlag & tab & (name of r) & tab & dueStr & tab & (name of l) & linefeed
    end repeat
  end repeat
  return out
end tell
EOF
)"

# Optional sort (post-process). Columns: 1=done 2=name 3=due 4=list
case "$sort_by" in
  due)   out="$(printf '%s' "$out" | sed '/^$/d' | sort -t "$(printf '\t')" -k3)";;
  title) out="$(printf '%s' "$out" | sed '/^$/d' | sort -t "$(printf '\t')" -k2)";;
  "")    : ;;
  *) die "invalid --sort: use 'due' or 'title'";;
esac

if [ "$json" -eq 1 ]; then
  printf '%s\n' "$out" | tsv_to_json done name due list
else
  printf '%s\n' "$out"
fi
