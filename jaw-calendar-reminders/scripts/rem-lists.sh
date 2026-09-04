#!/usr/bin/env bash
# List all reminder lists (one per line).
# Usage: rem-lists.sh
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib.sh"
require_macos
require_osascript

osascript <<'EOF'
tell application "Reminders"
  set out to ""
  repeat with l in lists
    set out to out & (name of l) & linefeed
  end repeat
  return out
end tell
EOF
