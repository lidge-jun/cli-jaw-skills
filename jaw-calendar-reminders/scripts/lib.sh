#!/usr/bin/env bash
# Shared helpers for the apple-calendar-reminders skill.
# Sourced by every cal-*.sh and rem-*.sh script. Zero external deps.
set -euo pipefail

die() { printf 'error: %s\n' "$*" >&2; exit 1; }

require_macos() {
  [ "$(uname -s)" = "Darwin" ] || die "this skill requires macOS (Calendar.app / Reminders.app + osascript)."
}

require_osascript() {
  command -v osascript >/dev/null 2>&1 || die "osascript not found in PATH."
}

# Escape a string for safe embedding inside an AppleScript double-quoted literal.
as_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

# Emit AppleScript statements that build an AppleScript date into variable $1
# from a "YYYY-MM-DD" or "YYYY-MM-DD HH:MM" string ($2).
# Missing time defaults to 00:00. Day is set to 1 first to avoid month-overflow.
as_build_date() {
  local var="$1" dt="$2"
  local datepart timepart y mo d h mi rest
  datepart="${dt%% *}"
  if [ "$dt" = "$datepart" ]; then timepart="00:00"; else timepart="${dt#* }"; fi
  y="${datepart%%-*}"; rest="${datepart#*-}"; mo="${rest%%-*}"; d="${rest#*-}"
  h="${timepart%%:*}"; mi="${timepart#*:}"
  y=$((10#$y)); mo=$((10#$mo)); d=$((10#$d)); h=$((10#$h)); mi=$((10#$mi))
  printf 'set %s to (current date)\n' "$var"
  printf 'set day of %s to 1\n' "$var"
  printf 'set year of %s to %d\n' "$var" "$y"
  printf 'set month of %s to %d\n' "$var" "$mo"
  printf 'set day of %s to %d\n' "$var" "$d"
  printf 'set hours of %s to %d\n' "$var" "$h"
  printf 'set minutes of %s to %d\n' "$var" "$mi"
  printf 'set seconds of %s to 0\n' "$var"
}

# Print every calendar name, one per line (robust to commas in names).
cal_list_names() {
  osascript <<'EOF'
tell application "Calendar"
  set out to ""
  repeat with c in calendars
    set out to out & (name of c) & linefeed
  end repeat
  return out
end tell
EOF
}

# Resolve a calendar name case-insensitively to its exact stored name.
# On no match, die with a helpful list of available calendars.
# Echoes the exact name on success.
cal_resolve() {
  local want="$1" names match
  names="$(cal_list_names)"
  match="$(printf '%s\n' "$names" | grep -ixF "$want" | head -1 || true)"
  if [ -z "$match" ]; then
    die "calendar not found: '$want'. Available: $(printf '%s' "$names" | sed '/^$/d' | paste -sd', ' -)"
  fi
  printf '%s' "$match"
}

# Print every reminder list name, one per line.
rem_list_names() {
  osascript <<'EOF'
tell application "Reminders"
  set out to ""
  repeat with l in lists
    set out to out & (name of l) & linefeed
  end repeat
  return out
end tell
EOF
}

# Emit AppleScript handlers pad2() and isoDate() for sortable "YYYY-MM-DD HH:MM"
# output. Place at the TOP of an osascript program; call as my isoDate(d) inside
# a tell block. Returns "" for a missing-value date.
as_isodate_handler() {
  cat <<'EOF'
on pad2(n)
  set s to "" & (n as integer)
  if (count of s) < 2 then set s to "0" & s
  return s
end pad2
on isoDate(d)
  if d is missing value then return ""
  return ((year of d) as integer as text) & "-" & pad2(month of d as integer) & "-" & pad2(day of d) & " " & pad2(hours of d) & ":" & pad2(minutes of d)
end isoDate
EOF
}

# Convert tab-separated stdin rows into a JSON array of objects.
# Args: column names (in order). Empty lines are skipped.
tsv_to_json() {
  local colnames; colnames="$(IFS=,; printf '%s' "$*")"
  awk -v FS='\t' -v colnames="$colnames" '
    function esc(s){ gsub(/\\/,"\\\\",s); gsub(/"/,"\\\"",s); gsub(/\r/,"",s); gsub(/\t/,"\\t",s); return s }
    BEGIN{ n=split(colnames,cn,","); printf "["; first=1 }
    {
      if ($0=="") next
      if (!first) printf ","; first=0
      printf "{"
      for (i=1;i<=n;i++){ if(i>1) printf ","; printf "\"%s\":\"%s\"", cn[i], esc($i) }
      printf "}"
    }
    END{ printf "]\n" }'
}
