#!/usr/bin/env bash
# List all calendars known to Calendar.app (one per line).
# Usage: cal-list.sh
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos
require_osascript

osascript <<'EOF'
tell application "Calendar"
  set out to ""
  repeat with c in calendars
    set out to out & (name of c) & linefeed
  end repeat
  return out
end tell
EOF
